"""Run the collector with D1-backed state through the authenticated DAL Worker."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from .collector import SCHEMA, digest, load_registry, run, write_outputs

ORIGIN = 'https://dal-data-ai-lab.moricz-labs.workers.dev'
TABLES = {'source_state': 2, 'identities': 2, 'versions': 4, 'observations': 4, 'pack_items': 3}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('API redirects are refused; credentials stay on the configured origin')

class Client:
    def __init__(self, origin: str, token: str, allow_local=False):
        self.origin = origin.rstrip('/')
        parsed = urlsplit(self.origin)
        local = allow_local and parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1'} and parsed.path == '' and not parsed.username and not parsed.password
        if self.origin != ORIGIN and not local:
            raise ValueError('Use the maintained DAL origin, or explicitly allow localhost for tests')
        if len(token) < 32:
            raise ValueError('A NEWS_INGEST_TOKEN of at least 32 characters is required')
        self.token = token
        self.opener = build_opener(NoRedirect())

    def request(self, path: str, payload=None):
        data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
        if data and len(data) > 5_000_000:
            raise ValueError('Upload exceeds 5 MB; state and pack need a smaller batch')
        request = Request(self.origin + path, data=data, headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json', 'User-Agent': 'DAL-News-Collector/0.2'})
        try:
            with self.opener.open(request, timeout=45) as response:
                result = response.read(5_000_001)
                if len(result) > 5_000_000:
                    raise ValueError('API response exceeds size limit')
                return json.loads(result)
        except HTTPError as exc:
            # Never print request headers or credentials. The saved payload can be retried.
            raise RuntimeError(f'DAL API returned HTTP {exc.code}; remote success is not confirmed') from None


def hydrate(client, db_path: Path):
    baseline = {}
    generation = None
    with sqlite3.connect(db_path) as db:
        db.executescript(SCHEMA)
        for table, width in TABLES.items():
            cursor = 0
            baseline[table] = set()
            for _ in range(1000):
                query = {'table': table, 'cursor': cursor}
                if generation is not None:
                    query['generation'] = generation
                response = client.request('/api/news/collector/state?' + urlencode(query))
                if generation is not None and response['generation'] != generation:
                    raise ValueError('Remote state changed during hydration')
                generation = response['generation']
                rows = response['rows']
                if response['table'] != table or len(rows) > 100 or any(len(row) != width for row in rows):
                    raise ValueError('Invalid state page')
                db.executemany(f'INSERT INTO {table} VALUES ({",".join("?" for _ in range(width))})', rows)
                baseline[table].update(tuple(row) for row in rows)
                next_cursor = response['next_cursor']
                if next_cursor is None:
                    break
                if not isinstance(next_cursor, int) or next_cursor <= cursor:
                    raise ValueError('Invalid state cursor')
                cursor = next_cursor
            else:
                raise ValueError('Remote state page limit reached')
    return generation, baseline


def upload_payload(pack, db_path, generation, baseline):
    # Validate the collector checksum before creating an exact-byte transport checksum.
    checked = json.loads(json.dumps(pack))
    checksum = checked['integrity_checks'].pop('pack_sha256')
    if digest(checked) != checksum:
        raise ValueError('Evidence pack checksum mismatch')
    payload = json.dumps(pack, ensure_ascii=False)
    state = {}
    with sqlite3.connect(db_path) as db:
        for table in TABLES:
            state[table] = [list(row) for row in db.execute(f'SELECT * FROM {table}') if tuple(row) not in baseline[table]]
    return {'generation': generation, 'pack_json': payload, 'transport_sha256': sha256(payload.encode()).hexdigest(), 'state': state}


def collect_remote(client, registry, output: Path, fetcher=None, now=None):
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dal-news-') as temporary:
        db_path = Path(temporary) / 'working.sqlite3'
        generation, baseline = hydrate(client, db_path)
        kwargs = {'fetcher': fetcher} if fetcher else {}
        pack = run(registry, db_path, now=now, **kwargs)
        pack['run_summary']['mode'] = 'remote_collection'
        pack['integrity_checks'].pop('pack_sha256')
        pack['integrity_checks']['pack_sha256'] = digest(pack)
        write_outputs(pack, output)
        payload = upload_payload(pack, db_path, generation, baseline)
        pending = output / 'pending-upload.json'
        pending.write_text(json.dumps(payload, ensure_ascii=False))
        result = client.request('/api/news/collector/runs', payload)
        (output / 'upload-result.json').write_text(json.dumps(result, indent=2))
        # Keep the exact payload for safe idempotent recovery after uncertain responses.
        return pack, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', default=ORIGIN)
    parser.add_argument('--allow-local', action='store_true')
    parser.add_argument('--registry', type=Path, default=Path('sources.json'))
    parser.add_argument('--output', type=Path, default=Path('output'))
    parser.add_argument('--retry-upload', type=Path)
    args = parser.parse_args()
    client = Client(args.origin, os.environ.get('NEWS_INGEST_TOKEN', ''), args.allow_local)
    if args.retry_upload:
        result = client.request('/api/news/collector/runs', json.loads(args.retry_upload.read_text()))
        print(json.dumps(result))
        return
    pack, result = collect_remote(client, load_registry(args.registry), args.output)
    print(json.dumps({'collection': pack['run_summary'], 'upload': result}, indent=2))
    raise SystemExit(0 if pack['run_summary']['status'] == 'complete' else 2)


if __name__ == '__main__':
    main()
