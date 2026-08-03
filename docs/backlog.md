# Delivery Backlog

Backlog items are evidence tasks, not deadline commitments. Only one primary phase and one small supporting task should be active at a time.

## Active - verified data foundation / Gate G3

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| G3-01 | Acquire the official UKBDS 2026 package without overwriting raw evidence | Four versioned files are present and ODS archives pass integrity checks | Project owner | Complete |
| G3-02 | Register provenance and checksums | Source and dataset registers contain URLs, dates, sizes, licences, and SHA-256 values | Project owner | Complete |
| G3-03 | Verify questionnaire routing, size definitions, weighting, confidence limits, and suppression | Technical checks recorded in the source profile | Project owner | In progress |
| G3-04 | Profile workbook structure and candidate tables | Source profile records sheets, dimensions, types, target tables, and denominators | Project owner | In progress |
| G3-05 | Approve the first extraction target and public denominator label | D-005 accepted, revised, or rejected | Research director | Complete |

## Active supporting work - reproducible transformation / Gate G4

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| G4-01 | Extract Table 42 employer-size rows with confidence limits and bases | Versioned interim CSV, metadata, and passing tests | Project owner | Complete - accepted by D-007 |
| G4-02 | Reconcile Table 41 to the published report | Automated rounded-value checks and recorded tolerance | Project owner | Complete - accepted by D-007 |
| G4-03 | Design and approve the long analytical schema | Data dictionary and schema decision | Research director | Complete - accepted by D-008 |
| G4-04 | Transform accepted Table 42 evidence and load SQLite | Versioned processed CSV, database, metadata, tests, and SQL reconciliation | Project owner | Complete - accepted and promoted by D-009 |

## Next supporting work - analysis and review / Gate G5

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| G5-01 | Write and validate the first descriptive SQL query from the approved snapshot | Saved query, machine-readable result, denominator label, confidence intervals, reconciliation, and review note | Project owner | Complete - accepted by D-010 |
| G5-02 | Review the first descriptive result and its limitations | Research-director accept, rework, or reject decision | Research director | Complete - accepted by D-010 |
| G5-03 | Assess whether formal business-size significance tests are supported | Published-method review, available/missing evidence list, and bounded technical recommendation | Project owner | Complete - accepted by D-011 |
| G5-04 | Create an accessible confidence-interval chart and text equivalent | Draft visual, source note, alt text, contrast/readability checks, and reconciliation to F-001 | Project owner | Complete - accepted by D-012 |
| G5-05 | Draft the first evidence-brief section around F-001 and the accepted chart | Bounded headline, evidence table, chart, source note, denominator, uncertainty, limitations, and internal-review status | Project owner | Complete - accepted by D-013 |
| G5-06 | Review the first evidence-brief section | Research-director accept, rework, or reject decision | Research director | Complete - accepted by D-013 |
| G5-07 | Extract and validate Table 48 AI-system integration by business size | Four conditional rows, supplied confidence intervals and bases, registered denominator, checksums, metadata, tests, and review note | Project owner | Complete - accepted by D-014 |
| G5-08 | Review the second question, indicator and conditional denominator | Research-director accept, rework, or reject decision before processed transformation | Research director | Complete - accepted by D-014 |
| G5-09 | Transform the D-014-approved Table 48 input into the governed long model and SQLite candidate | Registered AI-user denominator, four reconciled observations, provenance, integrity checks, metadata, and tests | Project owner | Complete - accepted and promoted by D-015 |
| G5-10 | Review the Table 48 processed candidate before analysis | Research-director accept, rework, or reject decision | Research director | Complete - accepted by D-015 |
| G5-11 | Write and validate the F-002 descriptive SQL query from the D-015 snapshot | Table 48-only query, four rows, denominator label, confidence intervals, reconciliation, metadata, and review note | Project owner | Complete - accepted by D-016 |
| G5-12 | Review the F-002 descriptive result and limitations | Research-director accept, rework, or reject decision | Research director | Complete - accepted by D-016 |
| G5-13 | Create an accessible F-002 confidence-interval chart | Draft visual, explicit AI-user denominator, source note, text equivalent, readability checks, and reconciliation to D-016 | Project owner | Complete - accepted by D-017 |
| G5-14 | Review the F-002 chart before using it in the second report | Research-director accept, rework, or reject decision | Research director | Complete - accepted by D-017 |
| G5-15 | Draft the second evidence brief by building F-002 onto the F-001 baseline | Combined narrative structure, both approved charts, separate denominator labels, evidence tables, limitations, source notes, and internal-review status | Project owner | Complete - accepted by D-018 |
| G5-16 | Review the second evidence brief before saving Report 02 | Research-director accept, rework, or reject decision | Research director | Complete - accepted by D-018 |
| G5-17 | Generate and visually validate private Report 02 from the D-018-approved brief | Reproducible PDF, both accepted charts, visible denominator separation, source notes, metadata, page renders, visual QA and report register entry | Project owner | Complete - technical and visual QA passed |
| G5-18 | Review Report 02 before treating it as the saved second report | Research-director accept, rework or reject decision | Research director | Bundled into the D-019 consolidated review |
| G5-19 | Extract Table 50 and generate a governed Report 03 on AI policy/guidance among AI users | Checksum-verified workbooks, reconciled central/lower/upper values, supplied bases, reproducible three-page PDF, metadata and page-by-page visual QA | Project owner | Complete - technical and visual QA passed |
| G5-20 | Review Report 02, F-003, Report 03 and final website wording together | One research-director accept, rework or reject decision covering the exact public claims | Research director | Superseded by the complete G5-24 five-report review |
| G5-21 | Define and feasibility-check Reports 04 and 05 | Registered source tables, candidate questions, denominators, limitations, later reuse and information-architecture note | Project owner | Complete - source structure checked under D-020 |
| G5-22 | Produce Report 04 on AI use cases by business size | Validated Table 42 purpose extraction, confidence intervals, bases, multi-response warning, chart, PDF and visual QA | Project owner | Complete - technical, text and visual QA passed |
| G5-23 | Produce Report 05 on operational AI adoption pathways | Validated Table 43/47/48/50 panels, separated denominators, charts, PDF and visual QA; no composite score | Project owner | Complete - technical, text and visual QA passed |
| G5-24 | Review the complete five-report foundation | One consolidated research-director decision covering Reports 01-05 and exact public wording | Research director | Ready - five-report private review package complete |
| G5-25 | Redesign and expand Reports 01-05 as final publications | Five consistent, evidence-rich PDFs; exact values, business-use insights, limitations, metadata, automated checks and page-by-page visual QA | Project owner | Complete - final suite approved by D-022 |
| G5-26 | Produce a denominator-safe cross-report synthesis | Standalone PDF connecting F-001 through F-005 without cross-population arithmetic, causal claims or a maturity score | Project owner | Complete - final synthesis approved by D-022 |

## Active product work - private website / Gate G6

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| G6-01 | Build and privately deploy the evidence website | Responsive evidence page, exact-value tables, verified PDF downloads, automated content tests, successful production build, source commit, saved Sites version and owner-only production deployment | Project owner | Complete - final report-suite Sites version 4 deployed owner-only |
| G6-02 | Review the private production website and all public-facing claims | Research-director acceptance or requested rework in the consolidated D-019 review | Research director | Ready for consolidated review |
| G6-03 | Make the accepted website publicly accessible | Public access change only after G5-20/G6-02 acceptance; verify final production URL and record release | Project owner | Blocked by consolidated content approval |
| G6-04 | Expand the private website for future sector and pathway research and apply the light-blue theme | Accessible dropdown navigation, three-branch structure, five-report library, responsive styles, updated preview image, tests and owner-only deployment | Project owner | Complete - final report-suite Sites version 4 deployed owner-only |
| G6-05 | Replace website report downloads and add the cross-report insight section | Six verified PDF downloads, synthesis section, responsive styling, content tests, fixed source commit and owner-only Sites deployment | Project owner | Complete - source commit `6db1b33`, Sites version 4 deployed owner-only |

## Accounting sector programme - benefits and system fit

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| ACC-B01 | Freeze the benefits question, evidence hierarchy and inclusion criteria | Benefits research plan and accepted decision log | Research director | Complete |
| ACC-B02 | Register and grade open accounting-benefit evidence | Seven-source register with A-D evidence roles and explicit transfer limits | Project owner | Complete |
| ACC-B03 | Build the observation-level benefits evidence matrix | Public CSV with outcomes, populations, causal status and limitations | Project owner | Complete |
| ACC-B04 | Produce the accounting benefits and system-fit evidence review | Reproducible ten-page PDF, metadata, automated tests and page-by-page visual QA | Project owner | Complete |
| ACC-B05 | Publish a dedicated accounting-benefits webpage | Responsive route, dropdown link, report and data downloads, route and content tests | Project owner | Complete |
| ACC-B06 | Reassess quantified UK impact | Triggered by an independent UK accounting-SME causal or strong longitudinal outcome study | Research director | Monitoring - evidence trigger not yet met |
| ACC-B07 | Extend to client-business outcomes | Separate secondary-evidence protocol for effects on accounting-practice clients | Research director | Later scope |

## Accounting sector programme - micro-practice adoption lab

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| ACC-C01 | Freeze the composite-case boundary | Secondary-only research plan, seven-person scope and explicit fictional status | Research director | Complete - approved 2026-08-03 |
| ACC-C02 | Register implementation and control evidence | Open peer-reviewed and authoritative source register with transfer limits | Project owner | Complete |
| ACC-C03 | Build the reusable pathway tracker | Step-level CSV covering Use, Integrate, Automate, Configure and cross-cutting governance | Project owner | Complete |
| ACC-C04 | Produce the supporting theoretical and methods PDF | Reproducible 15-page publication, metadata, automated tests and page-by-page visual QA | Project owner | Complete |
| ACC-C05 | Build the interactive adoption workspace | Pathway selector, checklist, browser-only measurement calculator, six gates and JSON export | Project owner | Complete; 11 website tests pass |
| ACC-C06 | Approve the public scenario and example values | Research-director decision on assumptions, initial calculator values and wording | Research director | Complete - approved 2026-08-03 |
| ACC-C07 | Publish and deploy the approved workspace | GitHub commit, Cloudflare deployment and live interaction verification | Project owner | Complete - commit 59b50f4; Worker version 5d6c15d2-5dd7-4c0d-9ee2-f8e33cb06abb |
| ACC-C08 | Build the Accounting AI Experience Lab | Four hands-on synthetic method demos, manual-versus-adopted comparisons, shared control room, evidence boundaries and production tests | Project owner | Complete - commit 12baead4; Worker version 588b57ca-6ab3-43ab-a5b2-f663f780670c |
| ACC-C09 | Rebuild the Lab around the accounting cycle | Move general method explanations to the background page; connect bookkeeping, ledger, close, accounts, insight and quality-control workstations; retain evidence boundaries and tests | Project owner | Complete - commit e4df810f; Worker version c3e5f313-7c4f-48c7-9d04-777f7edf3f11 |

## Accounting sector programme - adoption journeys

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| ACC-D01 | Freeze the journey question, case boundary and evidence hierarchy | Secondary-only protocol, six-grade hierarchy and eleven-stage lifecycle | Research director | Complete and approved 2026-08-03 |
| ACC-D02 | Register and grade implementation evidence | Fourteen open sources with primary, contextual, comparator and transfer roles | Project owner | Complete and published |
| ACC-D03 | Build the claim-level journey matrix | Twenty-three lifecycle observations retaining outcome status, grade and transfer boundary | Project owner | Complete and published |
| ACC-D04 | Publish the public case index | Six transparent rows separating core cases, synthesis, comparators and transfer cases | Project owner | Complete and published |
| ACC-D05 | Build the Accounting AI Adoption Journeys page | Dedicated route, nested Accounting navigation, source links, limitations and Lab hand-off | Project owner | Complete; lint, production build and 12 website tests pass |
| ACC-D06 | Approve public claims and release | Research-director review, GitHub commit, Cloudflare deployment and live verification | Research director | Complete - GitHub `fa40765`; Sites version 7; public Worker `602e8e8e-301b-40ab-848c-b6ead9958485`; live checks passed |
| ACC-D07 | Extend to independently measured UK micro-practice outcomes | Triggered by a named longitudinal case with baseline, quality, cost and control measures | Research director | Monitoring - evidence gap |

## Completed by handover baseline - Gate G1

| ID | Task | Evidence of completion | Owner | Status |
|---|---|---|---|---|
| G1-01 | Confirm one primary and one secondary MVP audience | Approved entries in the charter and research brief | Research director | Settled in handover; files need alignment |
| G1-02 | Define no more than six answerable research questions | Each question has a decision use, plausible source, population, period, and intended output | Research director | Settled in handover; files need alignment |
| G1-03 | Define core concepts and denominators | Glossary records working and source-specific definitions, inclusions, exclusions, and decision IDs | Research director | Settled in handover; source-specific detail in progress |
| G1-04 | Screen the top two candidate sources | Access, licence, format, variables, periods, populations, and limitations recorded | Project owner | UKBDS active; second source deferred until first profile |
| G1-05 | Complete initial risks and evidence gaps | Risks have owner, mitigation, contingency, and status | Project owner | Initial baseline complete |
| G1-06 | Freeze MVP and park extensions | MVP and non-goals approved; deferred ideas recorded without entering active scope | Research director | Settled in handover; files need alignment |
| G1-07 | Hold Gate G1 review | Proceed, rework, or stop/re-scope decision recorded in the decision log | Research director | Proceed recorded by D-003 and D-004 |

## Next - Gate G2

| ID | Task | Evidence of completion | Status |
|---|---|---|---|
| G2-01 | Confirm clean setup instructions | Fresh environment can run the documented checks | Not started |
| G2-02 | Pin dependencies when the first pipeline requires them | Dependency versions and update method are documented | Waiting for source format |
| G2-03 | Add configuration and secret checks | Tests prove local secrets and generated data are excluded | Partly complete |
| G2-04 | Create the first repository baseline | Intentional initial commit after scope and file review | Owner approval required |

## Later / parking lot

- Controlled AI insights after the evidence layer is stable.
- Tableau Public after the static evidence MVP reconciles.
- Power BI when a suitable environment exists.
- Companies House firm-level extensions after aggregate analysis is stable.
- A pilot service only after structured discovery evidence supports it.
