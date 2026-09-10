# DAL News workflow — collection and publication integration

This is the first working stage of the DAL AI Daily Brief: **collect → inspect coverage → verify sources → select stories → draft → human approval → publish**.

Collection, the D1 adapter, evidence endpoints and reviewed-edition publishing are implemented. Production database tables have been prepared; website deployment, credentials, a production trial and weekday activation remain separate rollout steps. See `../docs/DAL_NEWS_WORKFLOW.md` for the current integration and release instructions.

## Start here

1. Open `output/review.md` or `output/review.html` for the current evidence queue and source warnings.
2. Inspect the failures and research gaps before choosing any stories.
3. Open candidate source links and verify claims; the collector has read feed metadata, not the linked articles.
4. Use `EDITORIAL_HANDOFF.md` to research, score and draft the brief.
5. Approve the final copy separately before publishing it.

The original planning documents remain reference material. Their historical “No implementation authorised” label describes their earlier status; the user's 9 September request starts this local build. Proposed times, platform changes and access settings have not been activated.

## Run collection

Python 3.12 or newer is required. This prototype uses the Python standard library; there are no additional dependencies or paid AI calls.

From this `news-workflow` folder:

```sh
python3 -m dal_news.collector
python3 -m unittest discover -s tests -v
```

This Mac's bundled Python, if the usual command is unavailable:

```sh
/Users/henribergson/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m dal_news.collector
```

The collector needs outbound HTTPS access to the endpoints in `sources.json`. All output defaults to the local `output/` folder. It makes no database, GitHub or website changes outside that folder and reads no credentials.

| File | Purpose |
| --- | --- |
| `sources.json` | Proposed local-trial feed register and explicit research gaps |
| `dal_news/collector.py` | Parsing, date checks, filtering, deduplication, storage and review-page generation |
| `output/review.html` | Human-readable evidence queue |
| `output/review.md` | Text version of the coverage report and linked candidate queue |
| `output/latest.json` | Current machine-readable evidence pack |
| `output/YYYY-MM-DD.json` | Latest revision of a dated pack |
| `output/evidence.sqlite3` | Local history, identities, versions, source checkpoints and run snapshots |
| `EDITORIAL_HANDOFF.md` | Manual research, selection and drafting instructions |
| `BUILD_STATUS.md` | Verified results, remaining limitations and next build stage |

Exit code `0` means collection completed without warnings. Exit code `2` means the run produced a pack requiring attention; inspect its coverage. A programming, configuration or storage exception fails separately. **A complete collection is not a fact-checked or publication-approved brief.**

## Behaviour and evidence boundaries

- Fifteen initial endpoints cover selected official announcements, engineering posts, policy releases and three repository release feeds. The wider charter is represented as explicit research gaps.
- Requests use three workers, a 20-second request timeout, one retry for temporary server/network errors, a 2 MB response limit, 2,000 parsed records per source and a 500-item daily pack limit. Rate-limit or forbidden responses remain visible failures. No authentication or access-control bypass is attempted.
- The window is 30 hours, extended to 72 hours on Mondays. A prior successful checkpoint allows recovery with six hours of overlap, capped at seven days with a warning. First collection cannot recover material older than its initial window. Truncated feeds and missed windows may require manual research.
- Source IDs and tracking-cleaned canonical URLs identify exact repeats. Changed records retain linked versions. Probable duplicate headlines within the same pack and 72 hours are flagged for review and retained separately. This is not semantic deduplication or a claim that two stories describe the same event.
- Reruns keep the cumulative daily evidence pack and suppress unchanged items on later days. Historical run snapshots remain in SQLite. Changed filters do not erase items already admitted to that day's pack; review or start a separately named trial database when testing a different configuration.
- Date-less, timezone-ambiguous and future-dated entries are rejected visibly. Atom entries with only an update time retain an explicitly missing publication time. A newest source item older than 14 days raises a freshness warning; this is a diagnostic, not proof that the source is broken.
- Each item contains a source excerpt of at most 60 words, dates, links, source-level classifications and retrieval metadata. Article bodies and GitHub release bodies are not stored. Sources may supply long descriptions; only a bounded excerpt is retained. Review licensing before exposing excerpts publicly.
- Primary-source and vendor-origin labels describe the configured publisher, not independent verification of every post. In particular, platform-hosted community posts require authorship checks. Research announcements are not automatically classified as peer-reviewed papers.
- Keyword filtering of broad feeds uses titles and the stored excerpt and can miss relevant articles. Full feed bodies are not searched for editorial relevance.
- This phase fetches the configured feed/API response each run. Conditional HTTP requests, release pagination, per-provider rate budgets and retention pruning are not implemented. Pagination and item-limit concerns are exposed where detected. Remote D1 storage is available through the integrated runner described below.
- The checksum is SHA-256 of the JSON object serialised with sorted keys and `ensure_ascii=False`, excluding `integrity_checks.pack_sha256`. It identifies the pack contents; it does not authenticate a publisher or prove claims true.
- HTML escapes all source fields and includes no scripts or remote assets. Source material is untrusted input, including for any later AI-assisted editorial step.

## Connection to the maintained website

This collector is now part of the DAL repository on the `codex/dal-news-workflow` feature branch, created from freshly fetched `origin/main`. The original local prototype and synced project files are preserved. No public website release has been performed.

When this collection model is accepted, port the intended source files into a feature branch based on freshly fetched `main` in `/Users/henribergson/Desktop/DAL-Website`. Keep generated packs and SQLite history out of Git. Follow the website handoff's existing verification and guarded-release process for any actual site changes.

The integrated architecture uses GitHub Actions for collection, Cloudflare D1 for operational history and the maintained Worker for evidence access and reviewed editions. Each remote run restores recent D1 history into a temporary SQLite working database, performs deterministic collection, then uploads changed records in one transactional batch. D1 holds the durable state; runner files and GitHub artifacts are not the operational source of truth.

Before enabling that next stage, resolve the source gaps, confirm storage retention and metadata visibility, inspect current account quotas/billing controls, then build and test the D1 adapter and endpoint. The planning documents' 05:30 UTC weekday schedule remains a proposal; no schedule is installed.
