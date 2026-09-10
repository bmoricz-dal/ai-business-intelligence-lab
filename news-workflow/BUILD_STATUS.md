# DAL News — historical prototype status

This records the local prototype before website integration. For the current build, database and rollout status, see [DAL News workflow](../docs/DAL_NEWS_WORKFLOW.md). Trial output directories referenced below remain in the original local workspace and are not committed to this repository.

Updated: 10 September 2026. Milestone: local collection and editorial handoff prototype.

## Confirmed working

- Registry-driven intake from 15 public RSS, Atom and GitHub release endpoints.
- Source links, original dates, collection timestamps, short excerpts and evidence cautions.
- Local SQLite history with exact identity matching, linked record versions, cumulative daily packs and duplicate suppression across days.
- Bounded requests, retry handling, keyword filters, visible parse failures and freshness warnings.
- JSON evidence pack, HTML review page and Markdown review queue.
- A reusable editorial handoff with the charter's scoring rule and human review record.
- 23 automated checks passed on 10 September. They cover parsing, date ambiguity, future dates, partial failures, reruns, cross-day repeats, updates, recovery, HTML escaping, response limits and dropped-connection retries.

## Live collection evidence

| Trial | Outcome |
| --- | --- |
| 9 September, first implementation | 20 items; 9 sources without warnings, 4 partial and 2 failed. Oversized archives and release responses identified. Saved separately in `output-first-trial/`. |
| 9 September, revised intake | 21 items; 12 sources without warnings, 2 stale-source warnings and 1 dropped connection. Release request-size problems resolved. |
| 10 September, 07:06 UTC | 7 new or updated items; all 15 endpoints returned successfully, 13 sources without warnings and 2 stale-source warnings. Seven unchanged records were suppressed. |

Latest run ID: `6cc5043b-f143-473c-85f0-69ceb11d7b4c`.

Latest collection status: **Incomplete**. Cloudflare AI's newest dated feed item was 14 August; NIST's was 24 August. Both exceeded the prototype's 14-day freshness threshold. These are warnings to investigate, not confirmed feed outages or proof that no newer material exists elsewhere.

The seven latest records are candidates for research. Their source claims have not been independently verified, scored, drafted or approved for publication. The queue is strongly weighted towards vendor announcements and implementation material; the missing editorial desks remain explicit research tasks.

## Validation limits

The Browser tool rejected opening the local HTML review page under its URL security policy. Visual, responsive and keyboard checks remain unverified; no alternate browser route was used. A Markdown review queue is provided for direct reading. Automated checks cover generated content and escaping but do not replace visual inspection.

No scheduled job, Cloudflare database, public evidence endpoint, AI API integration or published edition has been created. The maintained website and the three reference documents were not changed. Source configuration is a local trial proposal.

## Next stage

1. Inspect the current candidate queue and apply the editorial handoff to a small sample. Confirm that the collected fields are sufficient to verify and write useful stories.
2. Investigate the Cloudflare/NIST freshness warnings; refine broad-source filtering and select independent/adoption-evidence sources or a repeatable manual research step.
3. Port accepted collector files into a feature branch in the maintained DAL repository after refreshing `main`. Keep generated evidence out of Git.
4. Build the D1 storage adapter, retention design and authenticated ingestion path, then the read-only evidence endpoint. Validate each against local fixtures before provisioning production resources.
5. Confirm metadata visibility, publication timing and account cost controls, then activate the scheduled collection. The plan's 05:30 UTC weekday time is still only proposed.

The next immediate working artifact is a manually reviewed and scored story shortlist. Public deployment and scheduling can follow once the collection and editorial handoff are satisfactory.
