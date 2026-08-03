# Cedar Ledger Ltd: reusable AI adoption method

This document is a worked implementation design for a fictional seven-person UK accounting practice. It is not evidence that a particular firm achieved the scenario results. Replace every illustrative operating input and threshold with the adopting firm's own measured baseline and risk tolerance.

## 1. Illustrative firm

| Item | Scenario assumption | Evidence status |
|---|---|---|
| Firm | Cedar Ledger Ltd | Fictional composite |
| People | Seven payroll employees | Chosen to fit the official 1–9 micro band and DSIT 5–9 frame |
| Roles | Owner-director, senior accountant, three accountants/bookkeepers, payroll specialist, administrator | Illustrative |
| Clients | 180 small-business and sole-trader clients | Illustrative; not a sector average |
| Systems | Cloud ledger, payroll, document portal and email | Illustrative common operating pattern |
| Initial problem | Manual transaction exceptions and close review consume scarce senior time | Illustrative problem statement |
| Prohibited scope | Autonomous tax/audit conclusions, material postings, financial decisions and unreviewed client advice | Research control |

## 2. Common foundation: complete before choosing a pathway

### Step 1 — Appoint accountability

Name one owner-director as accountable owner, one qualified reviewer and one operational lead. Record who can approve tools, data, pilots, live use and rollback. A micro firm may assign several roles to the same person, but the responsibilities must remain explicit.

### Step 2 — Map one workflow

Write the current workflow from trigger to final sign-off. Record inputs, systems, hand-offs, exceptions, outputs, client exposure and the point where professional judgement enters. Do not begin from a product demonstration.

### Step 3 — Measure four weeks of baseline

For a repeated workflow capture volume, elapsed time, hands-on time, review time, exception count, correction count, first-pass acceptance and incidents. Use medians as well as totals where a few difficult cases distort averages.

### Step 4 — Classify data and consequence

Identify personal data, special-category data, tax information, payroll data, bank details, client-confidential records and materiality. Decide what may enter a tool, in which environment, and for what purpose. If personal data are involved, assess data-protection obligations and whether a DPIA is required.

### Step 5 — Select the pathway

- Choose **Use** when the work is mainly research, summarisation or a first draft and does not require a live system connection.
- Choose **Integrate** when the task repeats inside the ledger or practice workflow and exceptions can be reviewed.
- Choose **Automate** only when rules, permissions, failure states and approvals can be defined in advance.
- Choose **Configure** when value depends on retrieving approved firm procedures or templates.
- Choose **do not adopt** when the task is difficult to verify, high-consequence, poorly measured or unsupported by accountable staff.

### Step 6 — Pre-register the decision

Before testing, record the baseline, selected measures, minimum acceptable quality, expected operational benefit, maximum tolerated risk, pilot population, reviewer, cost boundary and stop conditions. Thresholds are owner-set controls, not research findings.

## 3. Pathway A — Approved standalone use

**Best fit:** internal research, meeting-note summaries, first-draft internal procedures and non-client-specific explanations.

1. Approve one enterprise-grade tool and disable or prohibit unapproved consumer accounts.
2. Document data that must never be entered and whether submitted data are retained or used for model training.
3. Create three bounded prompt templates containing purpose, permitted sources, required caveats and output format.
4. Prepare 20 known tasks with accepted reference answers and planted edge cases.
5. Have two users run the tasks without client-identifiable data.
6. A qualified reviewer scores factual support, missing caveats, confidentiality, usefulness and correction time.
7. Revise prompts and training; retest failures rather than averaging them away.
8. Permit limited live use only for the approved task and user group.
9. Require source checking and named approval before any content leaves the firm.
10. Review usage, corrections and incidents after four weeks; continue, revise or stop.

**Do not use it for:** final tax positions, audit conclusions, client-specific advice without qualified review, or copying uncontrolled client records into a general tool.

## 4. Pathway B — Vendor-embedded integration

**Best fit:** transaction categorisation, matching, reconciliations, close checklists and exception queues.

1. Select one measured bottleneck, such as reconciliation review time—not “implement AI”.
2. Confirm the accounting platform's AI feature, data flows, access controls, retention, sub-processors, support, logs, export and exit route.
3. Obtain contract/data-protection review and record unresolved supplier questions.
4. Construct a known-case set from historical, properly controlled transactions, including unusual and error-prone items.
5. Test suggestions against accepted treatments; record accuracy, confidence, exceptions, false acceptance and review time.
6. Run two close cycles in **shadow mode**: staff complete the current process while the AI result is captured but not relied upon.
7. Compare on the same measures and investigate every material disagreement.
8. Pilot with an illustrative 10 low-complexity clients only after the shadow gate passes. The number 10 is a scenario choice, not evidence.
9. Route low-confidence, unusual, high-value and policy-exception items to the named reviewer.
10. Prohibit automatic material postings; retain the original record, suggestion, reviewer action and reason for override.
11. Compare total effort, quality and cost after two live close cycles.
12. Scale by client segment only if quality is maintained, controls work and the measured benefit exceeds the full adoption cost.

## 5. Pathway C — Bounded automation

**Best fit:** internal exception routing, task creation, evidence requests and draft reminders. External messages and accounting entries require approval.

1. Draw the proposed automation as trigger → data → rule/AI step → decision → action → reviewer → log.
2. Separate deterministic rules from AI judgement. Use ordinary rules where rules are enough.
3. List every action the automation is technically permitted to take.
4. Make the first release read-only or draft-only.
5. Create failure tests: missing document, wrong client, conflicting instruction, duplicate item, unusual amount and unavailable system.
6. Define an exception queue, named owner, response time and manual fallback.
7. Run in shadow mode and compare generated actions with staff decisions.
8. Allow a limited pilot only after false actions and missed exceptions are reviewed.
9. Require approval before sending client communication or posting to a ledger.
10. Monitor action counts, rejected actions, corrections, incidents and time displaced into review.
11. Pause automatically when logging fails, data scope changes or a material incident occurs.
12. Re-authorise after material system, model, supplier or workflow changes.

## 6. Pathway D — Configured knowledge retrieval

**Best fit:** finding approved firm procedures, checklist clauses, template wording and internal technical references.

1. Define the knowledge question and users; do not start by uploading the shared drive.
2. Inventory documents, owners, versions, confidentiality and expiry dates.
3. Remove duplicates and obsolete material; mark the authoritative version.
4. Restrict the corpus to approved internal content and permitted external sources.
5. Configure access so users retrieve only material they are already authorised to see.
6. Require answers to cite the underlying document and section.
7. Build at least 30 test questions: direct, ambiguous, conflicting, outdated and no-answer cases.
8. Score retrieval support, citation correctness, completeness, refusal and answer-review time.
9. Pilot with internal procedures only; exclude client files initially.
10. Add version refresh, deletion, access-review and incident processes before live expansion.
11. Keep professional conclusions outside the assistant; it retrieves evidence but does not own judgement.
12. Reject custom model training unless a separate capability, security, cost and assurance case passes.

## 7. One 12-week worked sequence

This sequence demonstrates how Cedar Ledger could combine the pathways. It is not a mandatory timetable.

| Week | Activity | Gate output |
|---|---|---|
| 1 | Appoint owner; map reconciliation and close workflow | Scope and accountability approved |
| 2–5 | Collect four-week baseline; classify data; review supplier | Baseline and data decision |
| 3–4 | Test standalone assistant on known internal tasks | Use / revise / stop |
| 5–6 | Test embedded AI on historical known cases | Test report and exceptions |
| 7–8 | Run two shadow close cycles | Shadow comparison |
| 9–10 | Controlled integration pilot; automation remains draft-only | Live pilot log |
| 11 | Recalculate total cost and quality; test rollback | Scale recommendation |
| 12 | Owner review: scale, revise, hold or stop | Signed decision and next review date |

## 8. Measurement specification

### Quality and risk

- First-pass acceptance = accepted AI-supported items / reviewed AI-supported items.
- Override rate = overridden suggestions / reviewed suggestions.
- Material-error count and near-miss count, reported separately.
- Unsupported-output rate for drafting or retrieval tasks.
- Client-data, access or confidentiality incidents.
- Exceptions per 100 transactions, with the denominator visible.

### Time and capacity

- Median calendar days from complete records to issued report.
- Hands-on preparation minutes per 100 transactions.
- Review and correction minutes per 100 transactions.
- Senior-review hours per close cycle.
- Hours reallocated to client explanation, analysis or advisory preparation.

### Cost boundary

`total pilot cost = licences + supplier/setup + internal setup + training + review + correction + assurance/security + incident cost`

`net measured capacity value = (baseline total hours − pilot total hours) × chosen loaded hourly cost − total pilot cost`

The firm must document its loaded-cost method. The result is a firm-specific management estimate, not a sector ROI statistic.

## 9. Decision gates

| Gate | Proceed only when | Stop or revise when |
|---|---|---|
| G0 Scope | One workflow, owner, users and prohibited actions are named | Objective is “use AI” or responsibility is unclear |
| G1 Data | Lawful purpose, minimisation, supplier route and access are documented | Sensitive data would enter an unapproved environment |
| G2 Known cases | Required quality and failure behaviour pass the pre-registered rule | Material errors, unsupported answers or missing logs occur |
| G3 Shadow | Quality is maintained and exceptions reach the reviewer | Staff cannot explain or override the output |
| G4 Pilot | Full cost, correction effort and incidents remain acceptable | Benefit disappears after review/correction or controls fail |
| G5 Scale | Segment, support, monitoring, rollback and review date are approved | Vendor lock-in, drift, workflow change or unresolved risk is material |

## 10. Reusable decision record

For each pathway, retain:

1. workflow and intended benefit;
2. accountable owner, users and reviewer;
3. data classes, supplier and system diagram;
4. evidence used and its transfer limit;
5. baseline period and measures;
6. known-case and shadow results;
7. pilot population and dates;
8. full cost and correction effort;
9. incidents, overrides and unresolved risks;
10. signed scale, revise, hold or stop decision;
11. rollback owner and last tested date;
12. next review trigger.

## 11. Evidence-safe conclusion

The case demonstrates a defensible process, not a guaranteed business outcome. The strongest current accounting evidence supports testing controlled transaction-processing and close support. Broader UK evidence shows that micro firms often start with small, inexpensive trials and commonly retain human checking, while skills, unclear need, integration, cost, regulation, accuracy and data concerns remain relevant. The correct end state may be scale, limited use, delayed adoption or no adoption.
