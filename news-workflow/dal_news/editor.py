"""Explicit editorial operations. The collection job never imports this module."""
import argparse
import json
import os
from pathlib import Path
from .remote import Client, ORIGIN


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['show', 'draft', 'approve', 'publish'])
    parser.add_argument('date')
    parser.add_argument('--revision', type=int)
    parser.add_argument('--file', type=Path)
    parser.add_argument('--reviewer')
    parser.add_argument('--origin', default=ORIGIN)
    parser.add_argument('--allow-local', action='store_true')
    args = parser.parse_args()
    from datetime import date
    if date.fromisoformat(args.date).isoformat() != args.date:
        parser.error('Use an ISO edition date: YYYY-MM-DD')
    client = Client(args.origin, os.environ.get('NEWS_EDITOR_TOKEN', ''), args.allow_local)
    path = '/api/news/editor/editions/' + args.date
    if args.action == 'show':
        print(json.dumps(client.request(path), indent=2, ensure_ascii=False))
        return
    if args.revision is None or args.revision < 0:
        parser.error('Supply the exact revision; a new draft starts at revision 0')
    payload = {'expected_revision': args.revision}
    if args.action == 'draft':
        if not args.file:
            parser.error('A draft JSON file is required')
        payload['edition'] = json.loads(args.file.read_text())
    if args.action == 'approve':
        if not args.reviewer:
            parser.error('Name the person who reviewed this exact draft')
        payload['reviewer'] = args.reviewer
    print(json.dumps(client.request(path + '/' + args.action, payload), indent=2))


if __name__ == '__main__':
    main()
