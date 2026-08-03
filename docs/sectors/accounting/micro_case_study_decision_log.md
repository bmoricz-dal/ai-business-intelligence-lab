# Micro accounting AI adoption case: decision log

## ACC-C01 — Composite rather than observed case

Decision: Use a clearly labelled fictional composite because the project is restricted to secondary data and has not observed a real practice implementation.  
Status: owner-approved on 2026-08-03.  
Implication: no scenario input may be presented as a sector statistic or empirical outcome.

## ACC-C02 — Seven-person practice

Decision: Use seven payroll employees so the case sits inside both the official 1–9 micro-employer definition and DSIT's narrower 5–9 micro survey frame.  
Status: owner-approved on 2026-08-03.  
Implication: evidence that excludes firms with 1–4 employees is not generalised to that group.

## ACC-C03 — Pathways are choices, not stages

Decision: Preserve Use, Integrate, Automate, Configure/Build and Govern as distinct operating choices.  
Status: owner-approved on 2026-08-03.  
Implication: the case contains a decision tree and optional branches, not a maturity score or compulsory sequence.

## ACC-C04 — Start from the strongest workflow evidence

Decision: Use transaction categorisation, reconciliation and close support for the worked integration pilot.  
Status: owner-approved on 2026-08-03.  
Implication: drafting and client communication remain lower-risk or conditional examples rather than the central benefit claim.

## ACC-C05 — Buy/configure before build

Decision: The composite micro practice assesses existing approved services before custom development and does not train a foundation model.  
Status: owner-approved on 2026-08-03.  
Implication: “build” can end in a documented no-go decision; no pathway is assumed beneficial.

## ACC-C06 — Firm-specific measurement

Decision: Require a four-week baseline, known-case test, shadow run and controlled pilot before scale.  
Status: owner-approved on 2026-08-03.  
Implication: published productivity estimates do not become expected savings or ROI inputs.

## ACC-C07 — Human accountability

Decision: Keep approval with named qualified staff for client-facing content, ledger postings and professional conclusions.  
Status: owner-approved on 2026-08-03.  
Implication: autonomous tax, audit, material posting and regulated decisions are outside the case scope.

## ACC-C08 — Publication gate

Decision: Publish the tested package only after the research director approves the case assumptions, thresholds and wording.  
Status: complete; publication approved by the research director on 2026-08-03 through the instruction to update GitHub and Cloudflare.

## ACC-C09 — Interactive workspace is the main product

Decision: Make the website adoption lab the primary output. Retain the PDF as theoretical and methods support.  
Status: accepted from owner direction on 2026-08-03.  
Implication: the website must demonstrate pathway choice, step completion, measurement, decision gates and export rather than merely summarise the PDF.

## ACC-C10 — Browser-only planning data

Decision: The demo accepts only illustrative or aggregated numbers, keeps state in the current browser session and provides a JSON export without sending data to DAL.  
Status: owner-approved on 2026-08-03.  
Implication: the interface visibly prohibits names, tax identifiers, payroll data, bank details and confidential documents.

## ACC-C11 — Verified release

Decision: Publish the owner-approved interactive workspace, supporting report, public pathway tracker and reproducibility records to the existing public repository and Worker.  
Status: complete on 2026-08-03.  
Release record: GitHub commit `59b50f471e3f45f9d1b289a0ec653ea86b6bca48`; Cloudflare Worker version `5d6c15d2-5dd7-4c0d-9ee2-f8e33cb06abb`. The live route returned HTTP 200, the interactive client bundle loaded, and the live PDF and CSV SHA-256 fingerprints matched the approved files.  
Implication: future substantive changes to case assumptions, thresholds, evidence claims or privacy behaviour require a new reviewed release.

## ACC-C12 — Test-drive experience becomes the primary product

Decision: Reframe the website from a planner-first adoption lab into an Accounting AI Experience Lab that lets viewers experience how controlled AI changes synthetic accounting work. Preserve the pathway planner as a secondary next step.  
Status: owner-approved for publication on 2026-08-03 through the explicit instruction “publish them”.  
Experience boundary: Use, Integrate, Automate and Configure demonstrations are deterministic and browser-only. Their time, manual-touch, quality-check and control-coverage figures are illustrative mechanics, not observed firm outcomes, product performance tests, UK accounting-SME benchmarks or promised benefits.  
Implication: the visitor should understand why adoption may improve efficiency, quality control and operational visibility, while the interface continues to show the human review, exception handling, citations and safe stops needed to make those improvements credible.

## ACC-C13 — Verified Accounting AI Experience Lab release

Decision: Record the tested Experience Lab extension as the current public Phase 2B release.  
Status: complete on 2026-08-03.  
Release record: GitHub commit `12baead4dfdb801c2b9ac622688a59b32e4b4743`; Cloudflare Worker version `588b57ca-6ab3-43ab-a5b2-f663f780670c`. The production build and lint checks passed, all 11 website tests passed, all nine public routes returned HTTP 200, and the live Experience Lab client bundle contained the four scenario workspaces, shared control room and control/failure-test interactions.  
Implication: the public Experience Lab is the primary practical demonstration and the planner is its secondary implementation workspace. Future substantive changes to scenarios, illustrative values, evidence claims, privacy behaviour or controls require a new reviewed release.

## ACC-C14 — Organise the Lab around accounting work

Decision: Move the general Use, Integrate, Automate, Configure and Govern explanations to the AI in Practice background page. Rebuild the Accounting AI Experience Lab around one connected fictional monthly cycle: bookkeeping capture, ledger categorisation, reconciliation and close, management accounts, business insights, and final quality and audit-trail review. Keep adoption methods only as secondary mechanism labels.  
Status: owner-approved for implementation and deployment on 2026-08-03 through the instruction “Do them and then deploy!”.  
Evidence boundary: every record, amount, comparison, check and narrative remains deterministic and fictional. The Lab does not produce prepared accounts, accounting advice, observed performance, a UK SME benchmark, an AI product test or promised benefit.  
Implication: the general page explains how AI can enter operations; the sector Lab demonstrates what controlled AI-enabled accounting work can look like.
