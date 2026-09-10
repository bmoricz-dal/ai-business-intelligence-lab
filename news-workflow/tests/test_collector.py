from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from http.client import RemoteDisconnected
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from dal_news.collector import (MAX_BYTES, canonical_url, collect_source, date_value,
    digest, duplicate_groups, fetch, load_registry, normalise, parse_feed, review_html,
    run, write_outputs)

NOW = datetime(2026, 9, 9, 12, tzinfo=timezone.utc)
SOURCE = {"id": "test", "name": "Test source", "publisher": "Test publisher",
          "url": "https://example.org/feed", "kind": "feed", "desk": "Frontier technology",
          "tier": 1, "primary": True, "vendor_origin": True, "active": True,
          "item_type": "announcement", "geography": "Global"}


def rss(title="A new inference deployment capability", guid="one", url="https://example.org/story", date="Wed, 09 Sep 2026 10:00:00 GMT", extra=""):
    return f'<rss><channel><item><guid>{guid}</guid><title>{title}</title><link>{url}</link><pubDate>{date}</pubDate><description>Source claim pending review.</description>{extra}</item></channel></rss>'.encode()


def fake(body):
    return lambda source: (body, {"http_status": 200, "content_type": "application/rss+xml", "response_sha256": sha256(body).hexdigest()})


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "test.sqlite3"
        self.registry = {"schema_version": 1, "sources": [deepcopy(SOURCE)], "search_only": ["Independent corroboration pending"]}

    def collect(self, body=None, now=NOW, fetcher=None):
        return run(self.registry, self.db, now, fetcher or fake(body or rss()))

    def test_tracking_removed_but_meaningful_parameters_preserved(self):
        self.assertEqual(canonical_url("https://Example.org/a?id=5&utm_source=email#x"), "https://example.org/a?id=5")
        for url in ["javascript:alert(1)", "https://name:password@example.org/a"]:
            with self.assertRaises(ValueError):
                canonical_url(url)

    def test_naive_and_invalid_dates_rejected(self):
        self.assertIsNone(date_value("2026-09-09T10:00:00"))
        self.assertIsNone(date_value("not a date"))
        self.assertEqual(date_value("2026-09-09T11:00:00+01:00").hour, 10)

    def test_atom_namespace_updated_fallback_and_relative_link(self):
        body = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>one</id><title>Title</title><updated>2026-09-09T10:00:00Z</updated><link rel="self" href="/api/item"/><link href="/story"/><summary>Abstract</summary></entry></feed>'
        item = normalise(parse_feed(body, SOURCE)[0], SOURCE, NOW)
        self.assertEqual(item["canonical_url"], "https://example.org/story")
        self.assertIsNone(item["published_at"])
        self.assertEqual(item["updated_at"], "2026-09-09T10:00:00Z")

    def test_html_instead_of_feed_and_entities_fail(self):
        for body in [b'<html>Access denied</html>', b'<!DOCTYPE rss [<!ENTITY x "a">]><rss/>']:
            items, health = collect_source(SOURCE, NOW, NOW - timedelta(days=1), fake(body))
            self.assertEqual(items, [])
            self.assertEqual(health["status"], "failed")

    def test_malformed_item_does_not_discard_good_sibling(self):
        body = rss().replace(b'</channel>', b'<item><title>Missing fields</title></item></channel>')
        pack = self.collect(body)
        self.assertEqual(len(pack["evidence_items"]), 1)
        self.assertEqual(pack["run_summary"]["status"], "incomplete")
        self.assertEqual(pack["integrity_checks"]["rejected_items"], 1)

    def test_future_items_rejected(self):
        pack = self.collect(rss(date="Thu, 10 Sep 2026 12:00:00 GMT"))
        self.assertEqual(pack["evidence_items"], [])
        self.assertEqual(pack["integrity_checks"]["rejected_items"], 1)

    def test_rerun_keeps_same_day_pack_and_suppresses_cross_day_repeats(self):
        first = self.collect()
        second = self.collect(now=NOW + timedelta(hours=1))
        self.assertEqual(first["evidence_items"], second["evidence_items"])
        self.assertEqual(second["run_summary"]["new_versions_this_run"], 0)
        third = self.collect(now=NOW + timedelta(days=1))
        self.assertEqual(third["evidence_items"], [])
        self.assertEqual(third["run_summary"]["status"], "needs_review")

    def test_material_update_creates_linked_version(self):
        first = self.collect()
        second = self.collect(rss(title="Changed capability with a material correction"))
        self.assertEqual(len(second["evidence_items"]), 1)
        self.assertEqual(second["evidence_items"][0]["previous_version_id"], first["evidence_items"][0]["version_id"])
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM versions").fetchone()[0], 2)

    def test_canonical_alias_deduplicates_changed_guid(self):
        self.collect()
        second = self.collect(rss(guid="another", url="https://example.org/story?utm_source=feed"))
        self.assertEqual(second["run_summary"]["item_total"], 1)

    def test_one_source_failure_is_visible_and_does_not_stop_others(self):
        other = {**SOURCE, "id": "broken"}
        self.registry["sources"].append(other)
        def partial(source):
            if source["id"] == "broken":
                raise TimeoutError("Timed out")
            return fake(rss())(source)
        pack = self.collect(fetcher=partial)
        self.assertEqual(pack["run_summary"]["status"], "incomplete")
        self.assertEqual(pack["run_summary"]["source_failed"], 1)
        self.assertEqual(len(pack["evidence_items"]), 1)

    def test_all_failures_keep_prior_pack_items_and_report_failure(self):
        self.collect()
        def fail(source):
            raise TimeoutError("Timed out")
        pack = self.collect(fetcher=fail)
        self.assertEqual(pack["run_summary"]["status"], "failed")
        self.assertEqual(len(pack["evidence_items"]), 1)

    def test_monday_includes_weekend(self):
        monday = datetime(2026, 9, 14, 6, tzinfo=timezone.utc)
        pack = self.collect(rss(date="Fri, 11 Sep 2026 07:00:00 GMT"), now=monday)
        self.assertEqual(len(pack["evidence_items"]), 1)

    def test_recovery_overlap_after_failed_day(self):
        self.collect()
        later = NOW + timedelta(days=3)
        pack = self.collect(rss(guid="missed", url="https://example.org/missed", date="Thu, 10 Sep 2026 15:00:00 GMT"), now=later)
        self.assertEqual(len(pack["evidence_items"]), 1)

    def test_empty_feed_and_stale_feed_are_not_complete(self):
        for body in [b'<rss><channel/></rss>', rss(date="Mon, 01 Jun 2026 10:00:00 GMT")]:
            pack = self.collect(body)
            self.assertEqual(pack["run_summary"]["status"], "incomplete")

    def test_keyword_filter_and_full_article_body_excluded(self):
        self.registry["sources"][0]["keywords"] = ["AI"]
        pack = self.collect(rss(title="Rail transport news", extra="<content>AI full article</content>"))
        self.assertEqual(pack["evidence_items"], [])
        self.assertEqual(pack["coverage_and_gaps"]["sources"][0]["filtered"], 1)

    def test_short_excerpt_and_safe_review_html(self):
        body = rss(title="&lt;script&gt;alert(1)&lt;/script&gt; Useful AI announcement")
        body = body.replace(b"Source claim pending review.", ("word " * 1000).encode())
        pack = self.collect(body)
        self.assertEqual(len(pack["evidence_items"][0]["source_excerpt"].split()), 60)
        self.assertTrue(pack["evidence_items"][0]["excerpt_truncated"])
        html = review_html(pack)
        self.assertNotIn("<script>", html)
        self.assertFalse(pack["publication_approved"])

    def test_checksum_and_output_roundtrip(self):
        pack = self.collect()
        claimed = pack["integrity_checks"].pop("pack_sha256")
        self.assertEqual(digest(pack), claimed)
        pack["integrity_checks"]["pack_sha256"] = claimed
        folder = Path(self.tmp.name) / "review"
        write_outputs(pack, folder)
        self.assertEqual(json.loads((folder / "latest.json").read_text()), pack)
        self.assertTrue((folder / "review.html").exists())

    def test_github_draft_exclusion_and_prerelease_label(self):
        source = {**SOURCE, "kind": "github"}
        body = json.dumps([{"id": 1, "tag_name": "v1.0-rc1", "html_url": "https://github.com/a/b/releases/1", "published_at": "2026-09-09T10:00:00Z", "prerelease": True}, {"draft": True}]).encode()
        records = parse_feed(body, source)
        self.assertEqual(len(records), 1)
        self.assertTrue(normalise(records[0], source, NOW)["evidence_cautions"]["prerelease"])

    def test_similar_cross_source_headlines_are_grouped_not_merged(self):
        a = normalise(parse_feed(rss(), SOURCE)[0], SOURCE, NOW)
        b = {**a, "item_id": "two", "publisher": "Another publisher", "source_id": "other"}
        a["item_id"] = "one"
        self.assertEqual(len(duplicate_groups([a, b])), 1)

    def test_pack_cap_visible_and_checkpoint_not_advanced(self):
        with patch("dal_news.collector.MAX_ITEMS", 0):
            pack = self.collect()
        self.assertEqual(pack["run_summary"]["status"], "incomplete")
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM source_state").fetchone()[0], 0)

    def test_registry_rejects_duplicate_identifiers(self):
        self.registry["sources"].append(SOURCE)
        path = Path(self.tmp.name) / "sources.json"
        path.write_text(json.dumps(self.registry))
        with self.assertRaises(ValueError):
            load_registry(path)

    def test_oversized_response_rejected(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, count): return b"x" * (MAX_BYTES + 1)
        with patch("dal_news.collector.urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "2 MB"):
                fetch(SOURCE)

    def test_remote_disconnect_retries_once_then_records_failure(self):
        with patch("dal_news.collector.urlopen", side_effect=RemoteDisconnected("Connection closed")) as request, patch("dal_news.collector.time.sleep"):
            items, health = collect_source(SOURCE, NOW, NOW - timedelta(days=1))
        self.assertEqual(request.call_count, 2)
        self.assertEqual(items, [])
        self.assertEqual(health["status"], "failed")


if __name__ == "__main__":
    unittest.main()
