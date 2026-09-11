# DAL News: private source review and story selection

Prepared from the existing production release `450c3344624cf3db910322536426853f3cdf5c11`. This review stage is not deployed. The live collector, original nine D1 tables, public evidence endpoint, `/news` and exact-revision publication safeguards remain unchanged.

## Owner journey

Open `/editorial/review` and enter the separate review access key. Choose a collection, inspect source health, read the priority shortlist and expand remaining candidates. Each card contains the collected title, source, date and link, the source excerpt, a provisional DAL relevance explanation, provenance/corroboration labels and the full score breakdown. Related candidates expand below a representative item; decisions remain individual.

Choose **Selected for analysis**, **Rejected**, or **Needs review**. Optional notes save with the decision. Saved decisions, revisions and recent history appear on each card. Search and decision filters include the lower-ranked candidates. Older collections can be loaded in batches of 30.

Selection does not run AI, draft an edition, approve anything or publish anything. No publication control is present in this interface. The existing raw public evidence endpoint retains its existing behaviour; review decisions and notes never appear there or on `/news`.

## Reading-priority ranking

Version: `dal-reading-priority-1`. Ranking is deterministic, runs on stored evidence when review is requested, and needs no AI API. Every candidate remains available. Up to eight representative story groups scoring at least 35/100 enter the shortlist; this is a reading threshold, not editorial eligibility.

| Factor | Maximum | What receives weight |
| --- | ---: | --- |
| AI capabilities / governance | 18 | Capability/evaluation signals; explicit governance, privacy or policy |
| Implementation | 18 | Deployment methods, workflow details, walkthroughs and operational prototypes |
| Economics / outcomes | 20 | Cost, productivity, performance or time-saving mechanisms; uncorroborated vendor numerical claims are capped at 14 |
| Enterprise / adoption | 14 | Business use cases and described adoption; built-in product features are not treated as customer adoption |
| UK / SME relevance | 18 | Explicit UK or small-business context; small-team transferability alone receives 8 and is not labelled UK evidence |
| Evidence available to review | 12 | Usable excerpt and source-level provenance; vendor primary excerpts receive only 6, and no source is labelled independently verified |

Deductions: thin/missing excerpt −10; routine version release −20; consumer feature −25; recap −12; promotional headline −8; preprint/prerelease −6. Scores are clamped to 0–100. Publisher identity or company size never earns a bonus. Recency is shown as context and an old collection warning, rather than used to inflate scores. Missing excerpt detail can underrank a significant development; editors can select any candidate.

These are lexical signals in titles/excerpts, not semantic research, verified outcomes or an assessment of actual commercial materiality. The short description is labelled **What the source says**. The explanation describes why a signal merits investigation. Source-owned claims are not rewritten as facts. The later charter score (including its verified-primary-source requirement) is separate.

Exact canonical URLs and identical non-generic headlines group automatically. Near-headline groups require at least three meaningful shared words and 60% token-set overlap. Conflicting numbers and generic release headlines are kept apart. Group membership compares with the representative to avoid transitive topic clusters. Grouping neither deletes records, changes their IDs, transfers decisions nor adds score/corroboration weight.

## Example: latest real production collection

Read back from production before changes: 10 September 2026, 21:57 UTC; run `c59b7f8c-8bd5-4b52-8907-da27ce198529`. It contains 25 items from 15 responding sources. Fourteen sources are healthy; Cloudflare AI has an old-feed warning (latest dated item 14 August). Collection is incomplete, despite successful storage. Coverage gaps remain visible.

| Candidate | Score | Main reasons |
| --- | ---: | --- |
| Heurist Finance investment workbench | 58 | Auditable workflow context 18; per-query cost mechanism 12; customer adoption 14; small-team transferability 8; vendor excerpt 6 |
| NVIDIA NIM: claimed 2.5× user capacity | 54 | Capability 12; production serving 12; capped vendor performance claim 14; enterprise context 10; vendor excerpt 6 |
| SageMaker model caching / cold starts | 50 | Capability 12; concrete implementation 18; capped time-saving claim 14; vendor excerpt 6 |
| OpenAI government access / cyber defence | 48 | Governance 18; capped pricing claim 14; public-sector use 10; vendor excerpt 6; no UK/SME points |
| RFI questionnaire workflow | 48 | Implementation 18; capped time-saving claim 14; business workflow 10; vendor excerpt 6 |
| AvioBook operational prototype | 44 | Implementation 12; operational-delay mechanism 12; adoption 14; vendor excerpt 6 |

PII detection and multimodal model-serving disaggregation complete the eight-item shortlist. Qwen deployment ties at 36 but falls just outside the eight-group cap; equal scores use stable item IDs as a reproducible tie-break, not an editorial preference. Seventeen candidates remain available below it. Bare Transformers/Ollama release numbers and consumer sports Search features score 0 on available evidence. The conservative grouping rules found no sufficiently close duplicates in this real pack; synthetic overlap/duplicate cases are covered by tests. Many items share a platform but concern distinct developments.

This ranking is not a recommended publication order. For example, NVIDIA's performance claim still needs its hardware/workload conditions and independent validation; the US government offer has no demonstrated UK applicability.

## Privacy and persistence

- New `NEWS_REVIEW_TOKEN` credential is separate from collection and publication credentials. The private service fails closed if it is absent. The release secret-file validator accepts an optional distinct review key while preserving existing two-key release files.
- Access-key exchange issues a random, eight-hour session. Only its SHA-256 digest, salted by the review key, is stored in D1. Production cookies are `Secure`, `HttpOnly`, `SameSite=Strict`, host-only and path `/`. Logout revokes the session; key rotation invalidates old sessions. The shared owner key is not a multi-user identity/audit system.
- All review APIs validate the session server-side. State-changing requests require a matching Origin. Spoofed user headers and collector/editor bearer tokens do not grant review access. Session cookies do not authorise existing collector/editor APIs.
- Private responses are no-store and noindex, with framing prohibited. The page has a restrictive CSP. Source values use text nodes, never HTML insertion. Source links are restricted to HTTP(S), opened with no opener or referrer. The key is never stored in localStorage/sessionStorage or placed in a URL.
- Additive migration `0001_luxuriant_chronomancer.sql` adds sessions, decisions and decision-history tables. SQL triggers append history atomically with a successful decision save. Applied migration `0000` is untouched.
- Decisions are keyed to a stable item ID but record the exact reviewed version/run, score snapshot, note, revision and timestamp. A new version appears as Needs review without erasing the prior decision. Any future analysis consumer must require the selected version to match the intended evidence version.
- Compare-and-swap revisions prevent stale tabs from overwriting another saved decision. Error responses do not claim success; refresh after an uncertain response. History retains the snapshot used at the time, even if a later ranking version changes the displayed score.
- Local preview uses local Cloudflare D1 storage under this worktree's ignored `.wrangler/state`. It contains a copy of real source evidence. It does not bind remotely to production. Local decisions persist across sessions/restarts while this directory is retained; they are not automatically transferred to production. Preserve/export them deliberately before removing the preview.

## Verification

Full website verification: lint, build, binding generation, application/Worker type checks and 51 tests passed. Collector: 26 tests passed. Review tests cover ranking discrimination, conservative grouping, privacy, forged headers, separate permissions, secure/expired/revoked sessions, CSRF, malformed inputs, stale writes, exact-version decisions, history, pagination, unchanged public publication behaviour, and actual local Cloudflare D1 migration/trigger execution.

HTTP integration checks against the local server verified sign-in, authenticated access to the real 25-item board, served CSS/JavaScript, no key in returned HTML, sign-out and post-logout rejection. Existing preview decisions were preserved. Browser visual/mobile/keyboard interaction QA has not been performed; do not describe HTTP or unit checks as that audit.

## Guarded rollout — only after explicit owner approval

1. Review and merge this change after CI passes. Refresh the clean canonical `main` checkout.
2. Keep the existing production D1 ID and both existing credentials. Generate a new, separate high-entropy review key; do not copy the local demo key. Add `NEWS_REVIEW_TOKEN` to the private release secrets file. Never put it in GitHub collection credentials or source control.
3. Run the maintained release checks and `npm run deploy` only after the owner's explicit approval. The existing guard applies the additive migration before uploading the Worker. No migration or secret update has been applied remotely for this stage.
4. Verify unauthenticated requests show only the sign-in page; authenticate, inspect the latest real board and verify a deliberate review decision persists. Recheck public `/news`, source collection and exact-revision publication safeguards. Do not manufacture a published edition for testing.
5. Decide explicitly whether to transfer the owner's local preview selections into the deployed review store. Keep them tied to exact evidence versions.

The weekday collection schedule remains inactive, as before. This stage does not modify the collection workflow, pricing settings, AI integrations or automated publication.

## Recommended next stage: selected-story research dossiers

Build an owner-triggered analysis job for selected, unchanged evidence versions only. Snapshot the selected IDs/versions, decision revision, run checksum, ranking version and research questions. A separate analysis credential should read selected inputs and write research drafts, with no ability to select, approve or publish.

For each story: open and verify the primary source; distinguish publication/event dates; check material numbers, scope and denominators; seek independent corroboration; research UK/SME transferability and implementation constraints; separate confirmed facts, vendor claims, DAL interpretation and unresolved questions. Treat all retrieved content as untrusted reference material. Return a cited dossier and the charter score, with a cost/time cap and explicit access failures. Require a human review before converting any dossier into an edition draft. Retain the existing exact-revision approval gate for publication.
