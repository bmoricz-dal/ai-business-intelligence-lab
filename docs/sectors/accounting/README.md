# UK Accounting SMEs: AI Adoption and Operational Readiness, 2026

This folder contains the complete secondary-data research package for the accounting current-state report, the Phase 2A benefits and system-fit evidence review and the locally completed adoption-journeys study.

## Publication outputs

- Final report: `output/pdf/UK_Accounting_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf`
- Public evidence: `data/public/accounting_ai_readiness_2026.csv`
- Report generator: `src/reporting/accounting_ai_readiness_report.py`
- Public webpage: `site/app/sectors/accounting/page.tsx`

## Phase 2B — micro-practice adoption lab

The next module translates the current-state and benefits evidence into a fictional seven-person accounting-practice case. Its primary output is the Accounting AI Experience Lab: one connected browser-only monthly cycle taking a fictional client through bookkeeping capture, ledger categorisation, reconciliation and close, management accounts, source-linked business insight and final quality control. General adoption-method explanations sit on the AI in Practice background page; small method labels identify the mechanism behind each accounting workstation. The earlier pathway planner remains as a secondary implementation workspace. A 15-page PDF provides supporting theory and method.

- Interactive route: `site/app/adoption-pathways/accounting-micro-case-study/page.tsx`
- Step-level tracker: `data/public/accounting_micro_ai_adoption_playbook_2026.csv`
- Supporting PDF: `output/pdf/UK_Micro_Accounting_Practice_AI_Adoption_Worked_Case_2026.pdf`
- Research plan: `micro_case_study_research_plan.md`
- Detailed method: `micro_case_study_method.md`
- Source register: `micro_case_study_source_register.csv`
- Decision log: `micro_case_study_decision_log.md`

Status: complete and owner-approved for publication on 2026-08-03, including the Experience Lab extension.

## Phase 2C — Accounting AI Adoption Journeys

The third accounting-sector study examines published implementation journeys from starting problem and selection through pilot, setback, adaptation, outcome and work change. It uses secondary evidence only. Three core accounting-practice evidence bundles are kept separate from historical non-AI comparators and provider-authored finance-function transfer cases.

- Webpage: `site/app/sectors/accounting/adoption-journeys/page.tsx`
- Public case index: `data/public/accounting_ai_adoption_journeys_2026.csv`
- Research protocol: `adoption_journeys_research_plan.md`
- Graded source register: `adoption_journeys_source_register.csv`
- Claim-level matrix: `adoption_journeys_evidence_matrix.csv`
- Findings matrix: `adoption_journeys_findings_matrix.md`
- Data dictionary: `adoption_journeys_data_dictionary.md`
- Decision log: `adoption_journeys_decision_log.md`

Status: approved and published on 2026-08-03. Research package release: GitHub commit `fa40765`. Website release: Sites version 7 and public Worker version `602e8e8e-301b-40ab-848c-b6ead9958485`. Live page, navigation, cross-link, report and dataset checks passed on the Worker domain.

### Phase 2A - benefits and system fit

- Final report: `output/pdf/UK_Accounting_SMEs_AI_Benefits_and_System_Fit_2026.pdf`
- Public evidence: `data/public/accounting_ai_benefits_system_fit_2026.csv`
- Report generator: `src/reporting/accounting_ai_benefits_report.py`
- Public webpage: `site/app/sectors/accounting/benefits/page.tsx`
- Research protocol: `benefits_research_plan.md`
- Findings matrix: `benefits_findings_matrix.md`
- Source register: `benefits_source_register.csv`
- Decision log: `benefits_decision_log.md`

## Research controls

- `research_plan.md` - scope, boundary, conclusions and completion status.
- `source_register.csv` - registered sources and evidence roles.
- `dataset_register.csv` - source files, retrieval dates and checksums.
- `source_profiles.md` - methods and limitations of the core sources.
- `comparability_matrix.md` - permitted and prohibited cross-source comparisons.
- `findings_matrix.md` - publication-approved claims and limitations.
- `data_dictionary.md` - observation model and denominator controls.
- `decision_log.md` - accounting-specific owner and method decisions.

## Central conclusion

AI is no longer niche among UK accounting practices, but no official open source supports one exact adoption rate for UK accounting SMEs. The strongest direct evidence reports 26% adopted and 54% piloting or adopted in April 2024; a later self-selected AccountingWEB sample reports 71.38% external-tool use. These measures are not averaged or treated as a trend.

Current use is mainly task-level and assistive: research, drafting, summarisation, client communication, document processing, automation and reporting. External tools and vendor-embedded features dominate over bespoke development or automated decisions. Security, skills, integration and human oversight remain separate readiness capabilities.

The current-state report makes no benefit claim. The separate Phase 2A review finds that transaction processing, bookkeeping and close support have the strongest measurable signal when AI is integrated with workflow controls and professional review. International field results are transfer evidence, not UK accounting-SME benchmarks; no ROI or vendor ranking is published.
