# DAL News workflow

Implementation prepared on 10 September 2026. This document describes the news integration, not an already activated daily service.

## What is built

Weekday runner → public feeds/APIs → deterministic collector → D1 evidence history → editorial draft → exact-revision human approval → published edition.

The collector does not call an AI model or write news stories. Editorial work still uses the source charter and `news-workflow/EDITORIAL_HANDOFF.md`; the editor interface accepts a separately researched, reviewed JSON draft. A future AI drafting integration must use separate permissions and must not receive the publication credential.

| Surface | Behaviour |
| --- | --- |
| `/news` | Latest published edition and up to 59 previous editions; honest preparation state while empty |
| `/news/YYYY-MM-DD` | A published edition; drafts are not returned |
| `/briefing/evidence/latest.json` | Latest collection pack, including failures and research gaps |
| `/briefing/evidence/YYYY-MM-DD.json` | Latest saved revision of that day's evidence pack |
| `/api/news/collector/state` | Authenticated, paginated hydration of recent collector state |
| `/api/news/collector/runs` | Authenticated, atomic ingestion of a run and its changed records |
| `/api/news/editor/editions/YYYY-MM-DD` | Authenticated review of a draft and its revision/approval state |
| `/api/news/editor/editions/YYYY-MM-DD/draft` | Save a new draft or revise the expected existing revision |
| `/api/news/editor/editions/YYYY-MM-DD/approve` | Record a named review of an exact revision |
| `/api/news/editor/editions/YYYY-MM-DD/publish` | Publish only if the current revision is approved |

## Database and release destination

- Maintained repository: `bmoricz-dal/ai-business-intelligence-lab`.
- Production Worker: `dal-data-ai-lab`.
- Intended public origin: `https://dal-data-ai-lab.moricz-labs.workers.dev`.
- D1 database: `dal-news`.
- D1 ID created for this integration: `d994f92f-4e51-42de-b946-1936481cf1b0`.
- D1 binding: `DB`.
- Generated schema migration: `website/drizzle/0000_gray_thena.sql`.
- Release configuration: `DAL_NEWS_DATABASE_ID` must contain the verified database ID. The guard rejects an absent ID or the local placeholder, and confirms that the generated binding matches it.

The existing `.openai/hosting.json` project ID points to the separate `sme-intelligence-lab-uk.benedict-moricz.chatgpt.site` publication. It has been preserved as existing metadata; publishing through that Sites record would not update the requested `workers.dev` destination. Use DAL's maintained guarded release process for the requested site. Do not create a duplicate Sites project or silently switch publication destinations.

## Collection state and recovery

The remote runner starts with a fresh temporary SQLite database. It hydrates source success markers and eight days of relevant identity/version/pack state from D1 in pages of 100 rows. The collector still uses its 30-hour normal window, 72-hour Monday window and up to seven days of recovery.

Only changed rows are uploaded. The database stores item identities, all accepted versions, observations, daily pack membership and collection-run snapshots. A unique generation number makes competing uploads fail atomically; a changed generation requires starting collection again. Repeating an already stored run with the same payload returns success without a second write. Reusing its ID with different evidence fails.

Each upload is bounded to 5 MB, each state-table JSON parameter to 1.5 MB and each daily pack to 500 items. These are application limits, not an assertion that every source/day will fit. If a limit is reached, preserve the local recovery payload and investigate before increasing it. The eight-day hydration window bounds routine history reads; database history is not automatically deleted. A retention/pruning policy still needs agreement before long-term unattended operation.

`output/pending-upload.json` contains the exact public-data upload for recovery, without credentials. If a response is lost, retry that exact file; if its generation conflicts, recollect from current D1 state. Artifacts expire after seven days; durable evidence remains in D1.

## Permissions and publication control

- `NEWS_INGEST_TOKEN` is a Worker secret used only by the collector. Store the matching value in the GitHub secret `DAL_NEWS_INGEST_TOKEN`.
- `NEWS_EDITOR_TOKEN` is a different Worker secret for the owner-operated editorial interface. Do not put it in the collection workflow.
- Both must be independently generated random secrets of at least 32 characters. The routes fail closed while secrets are absent.
- The collector cannot create, approve or publish editions. Public routes read only the published snapshot.
- Saving a correction clears that draft's approval, while the previous published snapshot stays visible. The new revision needs a new approval before publication.
- Approval records are an operational record supplied by the authorised editor; this phase does not provide individual editor sign-in, a tamper-proof review ledger or an editing UI.
- Never use example or test credentials in production. Do not commit secret values, `.dev.vars`, runtime environment files, SQLite databases or generated evidence.

## Rollout sequence

1. Review and merge the feature branch after the website and collector checks pass.
2. From the maintained canonical checkout, refresh `main` and follow the existing release guard. Supply the verified `DAL_NEWS_DATABASE_ID`. The guarded release applies pending additive D1 migrations before the Worker upload; a failed upload may leave the migration applied. Do not rewrite applied migration files.
3. Prepare a private JSON file containing separate `NEWS_INGEST_TOKEN` and `NEWS_EDITOR_TOKEN` values and set `DAL_NEWS_SECRETS_FILE` to its absolute path. The guard validates the file and passes it to Wrangler's supported `--secrets-file` option, so code and secrets can be uploaded together. Keep the file ignored and readable only by the owner. Separate secret-update commands can publish Worker versions; do not perform them casually before the release decision.
4. Deploy the reviewed website change through `npm run deploy` after the owner's release approval. Confirm the live release marker and the new routes. Nothing should be presented as published news until an edition has been approved and published.
5. Add the collector-only GitHub secret and set the repository variable `DAL_NEWS_ENABLED=true` when ready for the manual production trial. The checked-in workflow has **manual dispatch only**; its proposed weekday cron is commented out.
6. Run one manual production collection. Confirm the stored pack, source warnings, duplicate handling and a fresh-runner rerun. Do not promote source claims to verified facts.
7. Research and review a real draft. Store it as a draft, inspect the exact revision, record the owner's approval and publish that revision. Test fixtures must never be used as a real edition.
8. Confirm publication timing, source coverage, retention and account cost controls, then enable the proposed `30 5 * * 1-5` schedule in the workflow through review. This is 05:30 UTC, with a different UK local time in summer and winter. Leave time for delayed jobs before drafting.

The repository was verified as public. GitHub/Cloudflare spending controls and ongoing plan allowances have not been confirmed; do not describe the running service as guaranteed zero-cost before that check. No paid AI service is enabled by this change.

## Operator commands

From `news-workflow`, with the appropriate secret available in the environment:

```sh
python3 -m dal_news.remote
python3 -m dal_news.remote --retry-upload output/pending-upload.json
python3 -m dal_news.editor show YYYY-MM-DD
python3 -m dal_news.editor draft YYYY-MM-DD --revision 0 --file reviewed-edition.json
python3 -m dal_news.editor approve YYYY-MM-DD --revision 1 --reviewer 'Reviewer name'
python3 -m dal_news.editor publish YYYY-MM-DD --revision 1
```

Dates, filenames, reviewer names and revision numbers above are syntax examples. Use the actual reviewed edition and current server-reported revision. The last two commands represent explicit human approval and publication actions; do not run them from the collector or an unattended drafting agent.

## Verification and limits

Website verification covers lint, production build, generated bindings, application/Worker type checks and 39 tests, including real local Cloudflare D1 migration/ingestion, permission separation, exact-revision approval, correction handling and rendered published-only routes. Collector verification covers 26 tests, including state recovery on a fresh runner and cross-day deduplication.

The local `/news` route returned HTTP 200 and a preview was opened. This is not a visual, mobile or keyboard audit. No browser-interaction QA was requested or claimed. The existing dependency tree reported 10 audit findings (six high, four moderate) during installation; dependency upgrades are outside this change.

Production collection, secret configuration, public release, weekday scheduling and the AI drafting stage remain pending until the rollout steps are completed and recorded.
