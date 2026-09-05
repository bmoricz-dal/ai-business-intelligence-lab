# DAL Data & AI Lab website

The public site is https://dal-data-ai-lab.moricz-labs.workers.dev/.
This repository's `website/` directory is the maintained website source. Start
new work from current GitHub `main`; use a feature branch for changes.

## Develop and verify

Use the Node version in `../.nvmrc` and npm 12.0.2. npm is the only package
manager for this project; commit `package-lock.json` with package changes.

```sh
npm ci
npm run dev
```

Before review:

```sh
npm run verify
```

This runs lint, the production build, generated Cloudflare types, separate
browser/Worker type checks, and regression tests. The tests discover every
page, protect the 15 released routes, verify internal links, anchor targets,
public PDFs and built assets, check metadata and 404 behaviour, exercise input
validation, and check release guard decisions. They do not replace real-browser
interaction, responsive layout or accessibility testing.

## Structure

| Location | Purpose |
| --- | --- |
| `app/` | Pages, components, interaction logic and shared styles |
| `app/site-shell.tsx`, `app/mobile-site-nav.tsx` | Shared navigation |
| `app/research-data.ts` | Shared publication metadata |
| `app/sectors/accounting/`, `app/sectors/construction/` | Sector programmes |
| `app/adoption-pathways/` | Evidence pages and synthetic workflow labs |
| `app/ai-business-adoption-map/` | Decision Map |
| `public/` | Published images, PDFs and CSV copies |
| `worker/`, `vite.config.ts` | Cloudflare runtime and build configuration |
| `db/`, `examples/d1/` | Inactive optional D1 starter code; no database configured |
| `tests/` | Automated regressions and route integrity checks |
| `scripts/release.mjs` | Checked release entry point |
| `dist/`, `.wrangler/`, generated types | Disposable build output; never edit |

Publication source files live in repository-level `publications/` and
`data/public/`. Public copies are tracked under `public/`; do not change research
values during a website-only maintenance release.

## Release

See [the maintenance guide](../docs/WEBSITE_MAINTENANCE.md). After review, merge
and fetch the exact current `main` into the maintained checkout. Release from a
clean tree only:

```sh
npm run release:check
```

This checks current GitHub main and the live release marker, repeats validation,
and runs a Cloudflare dry run. It publishes nothing. After explicit publication
approval, `npm run deploy` repeats these checks before publishing.

The first guarded release requires `--bootstrap-live-marker`, only after the
existing live version has been verified manually. Later releases reject a
newer or divergent live commit. Guard failures must be resolved, not bypassed
with direct Wrangler commands. A deliberate rollback is a separate reviewed
operation. The guard cannot prevent manual dashboard releases or unguarded
commands in other copies of the project.
