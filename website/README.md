# DAL Data & AI Lab website

This is the source for the public UK SME AI adoption intelligence website:

<https://dal-data-ai-lab.moricz-labs.workers.dev/>

## Page structure

- `/` — Overview of the project, its purpose, research model and future goals
- `/about` — research background, purpose, values and contact details
- `/ai-in-business` — the five general reports and cross-report synthesis
- `/sectors` — the sector research programme
- `/sectors/accounting` — the completed accounting-sector study
- `/adoption-pathways` — use, integration, automation, build and governance pathways
- `/methods` — source roles, denominator controls, limitations and reproducibility

The shared navigation is defined in `app/site-shell.tsx`. Publication metadata
and download links used across pages are defined in `app/research-data.ts`.

## Local validation

Node.js 22.13 or later is recommended.

```bash
npm ci
npm test
npm run lint
```

`npm test` builds the Cloudflare Worker and checks all seven routes, direct
navigation, page-level evidence, methods transparency and the Accounting page.

## Publication assets

The deployed `public/reports/` files are release copies of the PDFs held in the
repository-level `publications/` directory. The deployed accounting CSV is the
release copy held in `data/public/accounting/`. They are not duplicated inside
this source folder in GitHub.

## Deployment

The production deployment command is:

```bash
npm run deploy
```

It targets the Cloudflare Worker named `dal-data-ai-lab`. Deployment should only
follow a clean `npm test` run against the same source version.
