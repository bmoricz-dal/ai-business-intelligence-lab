# Website maintenance and release controls

## Source of truth

Use GitHub `bmoricz-dal/ai-business-intelligence-lab`, branch `main`, and its
`website/` folder. Build output and old checkouts are not source. Keep one
maintained editor workspace; preserve unfinished older work separately and
port individual changes through reviewed diffs. Never copy an old folder over
the maintained checkout or use `git reset --hard` to reconcile unfinished work.

1. Fetch current GitHub main before starting a change.
2. Create a feature branch from that main.
3. Make a bounded change, inspect the diff, and run `npm run verify` in `website/`.
4. Review both functional behaviour and the intended content change.
5. Merge only after checks pass. Keep dependencies and their npm lockfile together.
6. Publish through the guarded release script after owner approval.

The proposed GitHub Actions workflow checks pull requests and main; it does not
deploy. Configure the `Website checks / verify` check as a required branch rule
and prohibit force pushes to main in GitHub after adopting this workflow.
Those repository settings are not changed by adding the workflow file.

## Release provenance

The release guard requires the canonical `website/` folder, the expected origin,
a clean tree, branch main, and HEAD equal to freshly queried GitHub main. It
checks those again after validation. The first guarded deployment publishes
`/release.json`, containing only the source commit and build time. Subsequent
releases require that live commit to be an ancestor of the candidate. Failed
network checks stop publication.

For the first guarded release only, after manually comparing the candidate to
the actual live site, run:

```sh
npm run release:check -- --bootstrap-live-marker
```

After approval use `npm run deploy -- --bootstrap-live-marker`. The bootstrap
flag only permits a 404 for the missing marker; it does not bypass a valid
newer marker or other failures. Omit the flag after the first guarded release.
Never publish an old `dist/` directory. The release command always rebuilds and
validates the current source. Confirm `/release.json`, all 15 pages and key
interactions after deployment. These controls reduce accidental rollback risk;
they do not replace review or govern direct dashboard/CLI changes.

## Validation and known limits — 5 September 2026

The baseline was GitHub main `e14e1acc68809feef894b0aee002386bd57c1088`.
The baseline build and 21 tests passed, while TypeScript failed because Worker
runtime types were missing. Maintenance adds separate browser/Worker checks,
route/download regressions, input validation, trusted-origin share metadata,
and an image endpoint that uses the configured asset binding.

Local final verification: clean `npm ci`, lint, production build, generated
Cloudflare types, both TypeScript projects, 32 tests and Wrangler dry run passed.
All 15 pages preserved the baseline main-content text; 350 internal links and
referenced build/CSS assets passed integrity checks. GitHub-hosted CI has not
run because this candidate has not been pushed.

Compatible package updates reduce the npm audit from 23 flagged dependency
entries (17 high) to 6 (2 high, 4 moderate). These are dependency findings, not
proof of exploitation or of live-site reachability:

- `image-size@2.0.2` and its parent `vinext` account for the two high entries.
  The advisory affects ICNS, JXL and HEIF parsing. npm reports a migration to
  `vinext@1.0.0-beta.9` as the fix, not a compatible image-size update. Keep that
  migration separate with browser regressions and source/build compatibility
  review. The current site accepts no image uploads; that does not remove the
  dependency finding.
- Four moderate entries come from the inactive Drizzle development tool chain
  through an old esbuild loader. Do not run its development server with
  untrusted traffic. Upgrade or remove this scaffold only as a deliberate
  database-tooling change; npm's suggested forced downgrade is not applied.

Current advisory evidence:
[ICNS parser](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr),
[JXL/HEIF parsers](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq),
[esbuild development server](https://github.com/advisories/GHSA-67mh-4wv8-2f99).
Runtime typing follows [Cloudflare type generation](https://developers.cloudflare.com/workers/languages/typescript/#generate-types).

Real-browser QA was blocked by an administrative security-policy check during
this audit. Responsive layout, browser console, keyboard/pointer behaviour and
end-to-end lab interactions remain unverified. Research claims, PDF contents,
external source-link validity, Cloudflare account settings and live release
parity were not re-audited. Do not label this a full security or accessibility
certification. Publication remains pending.
