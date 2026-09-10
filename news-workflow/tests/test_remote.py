from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from dal_news.remote import Client, NoRedirect, collect_remote
from test_collector import NOW, SOURCE, fake, rss
from datetime import timedelta


class FakeAPI:
    def __init__(self):
        self.payload = None
        self.rows = {name: {} for name in ['source_state', 'identities', 'versions', 'observations', 'pack_items']}
        self.generation = 0
    def request(self, path, payload=None):
        if payload is not None:
            self.payload = payload
            for table, rows in payload['state'].items():
                key_width = {'observations': 3, 'pack_items': 2}.get(table, 1)
                for row in rows:
                    self.rows[table][tuple(row[:key_width])] = row
            self.generation += 1
            return {'status': 'stored'}
        from urllib.parse import parse_qs, urlsplit
        table = parse_qs(urlsplit(path).query)['table'][0]
        return {'table': table, 'rows': list(self.rows[table].values()), 'generation': self.generation, 'next_cursor': None}


class RemoteTests(unittest.TestCase):
    def test_credentials_cannot_be_redirected_to_another_origin(self):
        with self.assertRaises(ValueError):
            Client('https://example.org', 'x' * 40)
        with self.assertRaises(ValueError):
            NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.org')

    def test_remote_roundtrip_emits_delta_and_retains_recovery_payload(self):
        client = FakeAPI()
        with TemporaryDirectory() as folder:
            pack, result = collect_remote(client, {'sources': [SOURCE], 'search_only': []}, Path(folder), fake(rss()), NOW)
            self.assertEqual(result['status'], 'stored')
            self.assertEqual(pack['run_summary']['mode'], 'remote_collection')
            self.assertEqual(len(client.payload['state']['versions']), 1)
            self.assertEqual(json.loads(client.payload['pack_json']), pack)
            self.assertTrue((Path(folder) / 'pending-upload.json').exists())

    def test_fresh_runner_restores_prior_evidence_and_suppresses_cross_day_repeat(self):
        client = FakeAPI()
        registry = {'sources': [SOURCE], 'search_only': []}
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            collect_remote(client, registry, Path(first), fake(rss()), NOW)
            pack, _ = collect_remote(client, registry, Path(second), fake(rss()), NOW + timedelta(days=1))
            self.assertEqual(pack['evidence_items'], [])
            self.assertEqual(pack['integrity_checks']['exact_duplicates_this_run'], 1)
            self.assertEqual(client.payload['state']['versions'], [])


if __name__ == '__main__':
    unittest.main()
