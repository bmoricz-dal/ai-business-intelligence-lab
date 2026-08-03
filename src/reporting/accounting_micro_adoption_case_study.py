"""Generate the secondary-evidence micro accounting AI adoption worked case."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from src.reporting.accounting_ai_readiness_report import (
    BLUE, INK, LEFT, LINE, MUTED, NAVY, PALE, RIGHT, SKY, TEAL, WHITE,
    P, bullet, callout, metric_cards, report_table,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/pdf"
PUBLIC_DATA = ROOT / "data/public/accounting_micro_ai_adoption_playbook_2026.csv"
PDF_NAME = "UK_Micro_Accounting_Practice_AI_Adoption_Worked_Case_2026.pdf"
REPORT_DATE = "3 August 2026"
AUTHOR = "Benedek Moricz"
BRAND = "DAL Data & AI Lab"
PAGE_W, PAGE_H = A4
TOP = 20 * mm
BOTTOM = 17 * mm

SOURCES = [
    ("Choi and Xie — Human + AI in Accounting", "https://onlinelibrary.wiley.com/doi/10.1111/1475-679x.70052"),
    ("Journal of Accounting and Public Policy — AI adoption in accounting and non-accounting firms", "https://doi.org/10.1016/j.jaccpubpol.2026.107433"),
    ("Journal of Global Information Management — AI Adoption in Accounting", "https://doi.org/10.4018/JGIM.404639"),
    ("DSIT — AI Adoption Research", "https://www.gov.uk/government/publications/ai-adoption-research/ai-adoption-research"),
    ("DBT — Business population estimates 2025", "https://www.gov.uk/government/statistics/business-population-estimates-2025/business-population-estimates-for-the-uk-and-regions-2025-statistical-release"),
    ("FRC — Generative and Agentic AI Guidance", "https://www.frc.org.uk/library/standards-codes-policy/audit-assurance-and-ethics/guidance/ai-in-audit/"),
    ("ICO — AI and data protection risk toolkit", "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/ai-and-data-protection-risk-toolkit/"),
    ("NCSC — Guidelines for secure AI system development", "https://www.ncsc.gov.uk/collection/guidelines-secure-ai-system-development/"),
    ("NIST — AI RMF Playbook", "https://airc.nist.gov/airmf-resources/playbook/"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_link(number: int, label: str, url: str) -> Paragraph:
    return P(f'<b>{number}. {label}</b><br/><link href="{url}" color="#2D83C5">{url}</link>', "SourceR")


def page_frame(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 9 * mm, PAGE_W, 9 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(LEFT, PAGE_H - 6 * mm, BRAND)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 6 * mm, "MICRO ACCOUNTING AI ADOPTION WORKED CASE")
    canvas.setStrokeColor(LINE)
    canvas.line(LEFT, 12 * mm, PAGE_W - RIGHT, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(LEFT, 8 * mm, "Owner-approved publication | Fictional composite | Secondary evidence only")
    canvas.drawRightString(PAGE_W - RIGHT, 8 * mm, f"{doc.page}")
    canvas.restoreState()


def cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#204F70"))
    for x in range(0, int(PAGE_W), 32):
        canvas.line(x, 0, x, PAGE_H)
    for y in range(0, int(PAGE_H), 32):
        canvas.line(0, y, PAGE_W, y)
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(LEFT, PAGE_H - 24 * mm, BRAND.upper())
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 25)
    y = PAGE_H - 54 * mm
    for line in ["UK Micro Accounting", "Practice AI Adoption", "Worked Case, 2026"]:
        canvas.drawString(LEFT, y, line)
        y -= 12 * mm
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica", 11)
    canvas.drawString(LEFT, y - 3 * mm, "A step-by-step method for a seven-person practice")
    canvas.setFillColor(BLUE)
    canvas.rect(LEFT, 55 * mm, 48 * mm, 3 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(LEFT, 41 * mm, REPORT_DATE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(LEFT, 34 * mm, f"Prepared by {AUTHOR}")
    canvas.setFillColor(SKY)
    canvas.drawRightString(PAGE_W - RIGHT, 21 * mm, "USE  |  INTEGRATE  |  AUTOMATE  |  CONFIGURE  |  GOVERN")
    canvas.restoreState()


def step_table(rows: list[list[str]]) -> list:
    return [report_table(["Step", "Action", "Evidence / gate"], rows, [18 * mm, 91 * mm, 65 * mm])]


def build_story() -> list:
    story: list = [PageBreak()]
    story += [P("EXECUTIVE BRIEF", "Kicker"), P("Turn adoption evidence into a controlled business decision", "H1R")]
    story.append(callout(
        "Cedar Ledger Ltd is a fictional seven-person accounting practice. The case demonstrates a reusable implementation method; it does not report a real firm's results and does not promise savings, ROI or a successful adoption outcome."
    ))
    story += [Spacer(1, 8)]
    story.append(metric_cards([
        ("7", "payroll employees", "Illustrative firm inside the micro-employer band"),
        ("4", "adoption methods", "Use, integrate, automate and configure"),
        ("6", "decision gates", "Scope, data, test, shadow, pilot and scale"),
    ]))
    story += [Spacer(1, 9), P("Case verdict", "H2R")]
    story.append(P("A micro practice should begin with one measured workflow and the least complex method that can solve it. The strongest current accounting evidence favours controlled transaction-processing, reconciliation and close support with exception handling and professional review."))
    story.append(bullet("Governance starts before tool selection and remains active across every pathway."))
    story.append(bullet("Known-case testing and shadow mode precede reliance on output."))
    story.append(bullet("Review, correction, training, assurance and incident costs stay inside the benefit boundary."))
    story.append(bullet("Scale, limited use, delay and no adoption are all valid outcomes."))
    story += [P("Evidence boundary", "H2R")]
    story.append(P("Official DSIT micro-business results cover firms with 5–9 employees. The fictional practice therefore has seven employees. Its client count, workload, pilot size, timetable and thresholds are scenario assumptions, not UK accounting-sector estimates."))

    story += [PageBreak(), P("01  THE FICTIONAL PRACTICE", "Kicker"), P("Cedar Ledger Ltd", "H1R")]
    story.append(report_table(
        ["Case item", "Illustrative assumption", "Status"],
        [
            ["People", "Seven payroll employees: owner-director, senior accountant, three accountants/bookkeepers, payroll specialist and administrator", "Fits official micro band; role mix is invented"],
            ["Clients", "180 small-business and sole-trader clients", "Scenario input; not a sector average"],
            ["Systems", "Cloud ledger, payroll, document portal and email", "Illustrative operating environment"],
            ["Problem", "Manual exceptions and close review consume scarce senior time", "Hypothesis to measure, not an observed fact"],
            ["Initial workflow", "Transaction categorisation, reconciliation and close support", "Chosen from strongest accounting evidence"],
            ["Excluded", "Autonomous tax/audit conclusions, material postings and unreviewed advice", "Control boundary"],
        ], [32 * mm, 94 * mm, 48 * mm]
    ))
    story += [Spacer(1, 8), P("Why this case is useful", "H2R")]
    story.append(P("The case makes implementation choices visible without pretending that a fictional outcome is evidence. A real firm can copy the sequence, replace the assumptions with its own systems and baseline, and retain the same decision gates."))
    story.append(callout("Do not copy Cedar Ledger's client count, pilot size or timetable into a business case. Copy the measurement and decision method.", colour=PALE, edge=TEAL))

    story += [PageBreak(), P("02  CHOOSE THE METHOD", "Kicker"), P("Four routes and one valid no-go decision", "H1R")]
    story.append(report_table(
        ["Method", "Choose when", "Accounting examples", "Complexity"],
        [
            ["Use", "The task needs assistive language or research but no live system connection", "Internal research, summaries, draft procedures", "Lowest"],
            ["Integrate", "The task repeats inside an existing ledger or workflow", "Coding, matching, reconciliation, close exceptions", "Moderate"],
            ["Automate", "Triggers, actions, permissions and failure states can be bounded", "Exception routing, tasks, draft reminders", "Higher"],
            ["Configure", "Value depends on approved firm knowledge", "Procedure and template retrieval with citations", "Moderate-higher"],
            ["Do not adopt", "The task is hard to verify, high-consequence or poorly measured", "Professional conclusions and material decisions", "Valid outcome"],
        ], [25 * mm, 57 * mm, 60 * mm, 32 * mm]
    ))
    story += [Spacer(1, 8), P("Micro-practice design principle", "H2R")]
    story.append(P("Buy or configure a controlled service before custom development. DSIT found in-house development uncommon, and accounting adoption studies identify compatibility, infrastructure, skills, financial readiness, trust and vendor support as relevant adoption conditions. These studies explain conditions; they do not prove business benefit."))
    story.append(callout("The pathways are operating choices, not maturity levels. A firm can use one without progressing to the next."))

    story += [PageBreak(), P("03  COMMON FOUNDATION", "Kicker"), P("Six steps before any pilot", "H1R")]
    story += step_table([
        ["1", "Name accountable owner, qualified reviewer and operational lead", "Signed responsibility and rollback record"],
        ["2", "Map one workflow from trigger to final sign-off", "Inputs, systems, exceptions and judgement points visible"],
        ["3", "Collect four weeks of baseline data", "Volume, time, review, corrections, exceptions and incidents"],
        ["4", "Classify data and professional consequence", "Permitted data, environment and use approved"],
        ["5", "Choose Use, Integrate, Automate, Configure or no adoption", "Task-system fit and consequence justify the choice"],
        ["6", "Pre-register measures, total cost and stop rules", "Decision rules fixed before results are seen"],
    ])
    story += [Spacer(1, 8), P("Govern, map, measure, manage", "H2R")]
    story.append(P("The sequence tailors NIST's voluntary AI RMF functions to a resource-constrained accounting practice. It also incorporates ICO data-protection questions, NCSC lifecycle security and FRC professional-review controls. None of those sources is evidence of productivity benefit."))
    story.append(P("If the workflow cannot be measured or the firm cannot name a qualified reviewer, Cedar Ledger stops before purchasing a tool."))

    story += [PageBreak(), P("04  PATHWAY A — USE", "Kicker"), P("Approved standalone assistance", "H1R")]
    story.append(P("Best fit: internal research, summaries and first drafts. Client-identifiable data are excluded until the data route and purpose are explicitly approved."))
    story += step_table([
        ["1–2", "Approve one controlled tool; document prohibited data and permitted tasks", "Terms, retention, access and training use accepted"],
        ["3", "Create bounded prompts requiring sources, caveats and output format", "Prompt set approved by qualified reviewer"],
        ["4–5", "Prepare 20 known tasks and run them with two intended users", "Illustrative test size; no client-identifiable data"],
        ["6", "Score factual support, omissions, confidentiality and correction time", "Failures are investigated, not averaged away"],
        ["7", "Permit limited live use for approved internal tasks", "Source checking and named approval enforced"],
        ["8", "Review usage, corrections and incidents after four weeks", "Continue, revise or stop"],
    ])
    story += [Spacer(1, 8)]
    story.append(callout("The 20 tasks, two users and four weeks are illustrative case choices. A real firm sets its own test size based on task variation and consequence."))

    story += [PageBreak(), P("05  PATHWAY B — INTEGRATE", "Kicker"), P("Transaction and close support", "H1R")]
    story.append(P("This is the case's central pathway because it connects to the strongest accounting-specific field evidence. The evidence concerns an integrated platform with workflow management and human review—not an isolated chatbot."))
    story += step_table([
        ["1", "Select one measured bottleneck in coding, reconciliation or close", "Workflow outcome, not generic AI objective"],
        ["2", "Review supplier data flows, access, retention, logs, export and exit", "Assurance questions resolved"],
        ["3–4", "Test historical known cases, unusual items and failure-prone work", "Suggestions, confidence, exceptions and review time compared"],
        ["5", "Run two close cycles in shadow mode", "Current process remains authoritative; disagreements logged"],
        ["6", "Pilot with 10 illustrative low-complexity clients", "Scenario size only; segment and reviewer approved"],
        ["7–8", "Route exceptions and prohibit automatic material postings", "Original, suggestion, review and override retained"],
        ["9", "Compare full effort, quality and cost after two live cycles", "Scale by segment, revise or stop"],
    ])
    story += [Spacer(1, 8), P("Human-AI gate", "H2R")]
    story.append(P("The accounting field study found average classification improvement in a framed task but also greater error risk when accountants followed inaccurate or non-consensus suggestions. Cedar Ledger therefore tests exception behaviour and retains professional override."))

    story += [PageBreak(), P("06  PATHWAY C — AUTOMATE", "Kicker"), P("Bound actions before granting autonomy", "H1R")]
    story.append(P("Best fit: internal exception routing, task creation, evidence requests and draft reminders. External messages and ledger postings remain approval-gated."))
    story += step_table([
        ["1", "Draw trigger → data → decision → action → review → log", "Every action and reviewer visible"],
        ["2", "Use deterministic rules where ordinary rules are sufficient", "AI limited to genuinely uncertain steps"],
        ["3", "Make the first release read-only or draft-only", "Permissions enforce the boundary"],
        ["4", "Test missing, wrong-client, conflict, duplicate, unusual and outage cases", "Failures route safely to named staff"],
        ["5", "Shadow proposed actions against staff decisions", "False and missed actions reviewed"],
        ["6", "Require approval for client communication and ledger action", "Approval log retained"],
        ["7–8", "Monitor, pause and re-authorise after material change", "Rollback works; logging and fallback remain available"],
    ])
    story += [Spacer(1, 8)]
    story.append(callout("Automation is not justified by labour saving alone. A task must have bounded permissions, observable failure, a named exception owner and a tested manual fallback.", colour=PALE, edge=TEAL))

    story += [PageBreak(), P("07  PATHWAY D — CONFIGURE", "Kicker"), P("Retrieve approved knowledge; do not manufacture authority", "H1R")]
    story.append(P("Best fit: retrieving current firm procedures, checklist clauses and approved templates. The assistant cites the underlying document and does not own the professional conclusion."))
    story += step_table([
        ["1", "Define the knowledge question and authorised users", "Scope is retrieval, not 'upload everything'"],
        ["2–3", "Inventory, deduplicate and approve documents", "Owner, version, access and expiry recorded"],
        ["4", "Require document and section citations", "Every supported answer is verifiable"],
        ["5–6", "Test 30 direct, ambiguous, conflicting, outdated and no-answer questions", "Support, citation, completeness and refusal scored"],
        ["7", "Pilot on internal procedures without client files", "Access and source checking operate"],
        ["8", "Add refresh, deletion, access review and incident handling", "Corpus remains current"],
        ["9", "Reject custom model training unless a separate case passes", "Build/no-build decision documented"],
    ])
    story += [Spacer(1, 8)]
    story.append(P("For Cedar Ledger, custom foundation-model development is a no-go. The firm has no dedicated model-development capability, and the assurance burden is disproportionate to the defined retrieval need. This is a case decision, not a universal prohibition."))

    story += [PageBreak(), P("08  12-WEEK WORKED SEQUENCE", "Kicker"), P("Combine methods without assuming a funnel", "H1R")]
    story.append(report_table(
        ["Week", "Cedar Ledger activity", "Decision output"],
        [
            ["1", "Appoint owner; map reconciliation and close", "Scope and accountability"],
            ["2–5", "Collect four-week baseline; classify data; review supplier", "Baseline and data decision"],
            ["3–4", "Test standalone assistant on known internal tasks", "Use / revise / stop"],
            ["5–6", "Test embedded AI on historical known cases", "Test report and exceptions"],
            ["7–8", "Run two shadow close cycles", "Shadow comparison"],
            ["9–10", "Controlled integration pilot; automation draft-only", "Live pilot log"],
            ["11", "Recalculate total cost and quality; test rollback", "Scale recommendation"],
            ["12", "Owner review", "Scale, revise, hold or stop"],
        ], [23 * mm, 101 * mm, 50 * mm]
    ))
    story += [Spacer(1, 8)]
    story.append(callout("This timetable demonstrates the method. It is not evidence that 12 weeks is sufficient for every firm or system."))

    story += [PageBreak(), P("09  MEASURE THE WHOLE OUTCOME", "Kicker"), P("Time saved is not the benefit boundary", "H1R")]
    story.append(report_table(
        ["Dimension", "Measures", "Reason"],
        [
            ["Quality", "First-pass acceptance, overrides, corrections, material errors and near misses", "Detect false efficiency"],
            ["Time", "Median days to report, preparation, review and correction minutes per 100 transactions", "Separate preparation from assurance"],
            ["Capacity", "Senior-review hours and time reallocated to explanation or analysis", "Test augmentation mechanism"],
            ["Risk", "Unsupported outputs, access/confidentiality incidents and exceptions per 100 transactions", "Keep denominators and consequences visible"],
            ["Cost", "Licences, supplier/setup, internal setup, training, review, correction, assurance and incidents", "Avoid partial ROI"],
        ], [27 * mm, 98 * mm, 49 * mm]
    ))
    story += [Spacer(1, 8), P("Firm-specific formulas", "H2R")]
    story.append(P("<b>Total pilot cost</b> = licences + supplier/setup + internal setup + training + review + correction + assurance/security + incident cost"))
    story.append(P("<b>Net measured capacity value</b> = (baseline total hours − pilot total hours) × documented loaded hourly cost − total pilot cost"))
    story.append(P("These produce a management estimate for one firm and period. They are not a sector ROI statistic and should not be compared with self-reported productivity percentages."))

    story += [PageBreak(), P("10  SIX DECISION GATES", "Kicker"), P("Proceed, revise or stop", "H1R")]
    story.append(report_table(
        ["Gate", "Proceed only when", "Stop or revise when"],
        [
            ["G0 Scope", "Workflow, owner, users and prohibited actions are named", "Objective is generic or responsibility unclear"],
            ["G1 Data", "Purpose, minimisation, supplier route and access documented", "Sensitive data enter an unapproved environment"],
            ["G2 Known cases", "Quality and failure behaviour pass the pre-registered rule", "Material error, unsupported answer or missing log"],
            ["G3 Shadow", "Quality maintained; exceptions reach reviewer", "Staff cannot explain or override output"],
            ["G4 Pilot", "Full cost, correction and incidents remain acceptable", "Benefit disappears or controls fail"],
            ["G5 Scale", "Segment, support, monitoring, rollback and review approved", "Material lock-in, drift or unresolved risk"],
        ], [24 * mm, 76 * mm, 74 * mm]
    ))
    story += [Spacer(1, 8), P("Illustrative thresholds", "H2R")]
    story.append(P("The case does not prescribe a universal accuracy or time-saving percentage. Cedar Ledger must set thresholds before testing, based on materiality, client risk, reviewer capacity and baseline variation. Zero tolerance applies to unauthorised disclosure and unapproved material postings; other thresholds require an explicit owner decision."))

    story += [PageBreak(), P("11  EVIDENCE-TO-ACTION MAP", "Kicker"), P("What each source can—and cannot—support", "H1R")]
    story.append(report_table(
        ["Evidence", "Used for", "Not used for"],
        [
            ["Accounting field and experiment", "Transaction/close mechanism, known-case and human-review design", "UK effect size or guaranteed saving"],
            ["Accounting adoption studies", "Compatibility, skills, infrastructure, trust, vendor support and cost questions", "Realised benefit or micro-UK prevalence"],
            ["DSIT UK research", "Micro trial context, barriers, oversight and reported impact", "Accounting-specific causal outcome"],
            ["FRC guidance", "System design, testing, education, governance and human oversight", "Benefit magnitude outside audit"],
            ["ICO and NCSC", "Data-protection and lifecycle-security controls", "Professional or commercial recommendation"],
            ["NIST", "Tailored govern-map-measure-manage structure", "Mandatory checklist or certification"],
        ], [48 * mm, 65 * mm, 61 * mm]
    ))
    story += [Spacer(1, 8)]
    story.append(P("DSIT reports that micro and small firms often use informal or inexpensive tests, while limited skills, unclear need, integration difficulty, cost, regulation and data concerns remain barriers. The worked case turns the useful small-test instinct into a documented pilot rather than treating ad-hoc use as sufficient governance."))

    story += [PageBreak(), P("12  REUSABLE DECISION RECORD", "Kicker"), P("What a real firm should retain", "H1R")]
    for item in [
        "Workflow, intended benefit and excluded actions.",
        "Accountable owner, users, reviewer and rollback owner.",
        "Data classes, supplier, system diagram and access route.",
        "Evidence used and its population, task and transfer limits.",
        "Baseline period, measures, denominators and pre-registered thresholds.",
        "Known-case, failure-test and shadow results.",
        "Pilot population, dates, full cost and correction effort.",
        "Incidents, near misses, exceptions, overrides and unresolved risks.",
        "Signed scale, revise, hold or stop decision.",
        "Rollback test, next review date and change triggers.",
    ]:
        story.append(bullet(item))
    story += [Spacer(1, 8), P("Final research conclusion", "H2R")]
    story.append(callout("The evidence supports a controlled adoption process, not a predetermined adoption outcome. For a micro accounting practice, the strongest starting hypothesis is integrated transaction and close support with professional review. The correct decision may still be limited use, delay or no adoption."))

    story += [PageBreak(), P("13  METHODS AND SOURCES", "Kicker"), P("Secondary evidence and transparent assumptions", "H1R")]
    story.append(P("The case combines accounting outcome evidence, accounting and SME adoption research, official UK business evidence and authoritative controls. Research findings, scenario assumptions and owner-set thresholds remain separate. No vendor claim or vendor price is used."))
    story.append(report_table(
        ["Control", "Application"],
        [
            ["Case status", "Fictional composite; no observed firm outcome"],
            ["Size", "Seven employees fits 1–9 official micro band and DSIT 5–9 survey frame"],
            ["Transfer", "US and non-UK evidence supports mechanisms only"],
            ["Measurement", "Four-week baseline and firm-specific pilot replace imported effect sizes"],
            ["Costs", "Review, correction, training, assurance and incidents included"],
            ["Publication", "Owner-approved on 3 August 2026"],
        ], [48 * mm, 126 * mm]
    ))
    story += [Spacer(1, 7), P("Core sources", "H2R")]
    for number, (label, url) in enumerate(SOURCES, 1):
        story.append(source_link(number, label, url))
    story += [Spacer(1, 6), P("Citation", "H2R")]
    story.append(P("Moricz, B. (2026). <i>UK Micro Accounting Practice AI Adoption Worked Case, 2026.</i> DAL Data &amp; AI Lab."))
    story.append(P("This worked case is not accounting, legal, tax, audit, data-protection, investment or procurement advice.", "SmallR"))
    return story


def validate_public_data() -> None:
    with PUBLIC_DATA.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) < 40:
        raise ValueError("Adoption playbook must contain at least 40 steps")
    required = {"step_id", "pathway", "action", "proceed_condition", "stop_or_revise_condition", "scenario_status"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Adoption playbook is missing required fields")
    if any(not row["stop_or_revise_condition"] for row in rows):
        raise ValueError("Every step must retain a stop or revise condition")


def generate() -> Path:
    validate_public_data()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / PDF_NAME
    doc = SimpleDocTemplate(
        str(path), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM,
        title="UK Micro Accounting Practice AI Adoption Worked Case, 2026",
        author=AUTHOR,
        subject="Secondary-evidence fictional composite case for controlled AI adoption",
    )
    doc.build(build_story(), onFirstPage=cover, onLaterPages=page_frame)
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = ["fictional", "secondary evidence", "seven", "shadow mode", "no adoption", "not a sector roi", "professional review"]
    missing = [item for item in required if item.lower() not in text.lower()]
    if missing:
        raise ValueError(f"Required report text missing: {missing}")
    metadata = {
        "title": "UK Micro Accounting Practice AI Adoption Worked Case, 2026",
        "publication_date": "2026-08-03",
        "author": AUTHOR,
        "research_mode": "secondary_data_only",
        "case_status": "fictional_composite",
        "approval_status": "owner_authorised_final_publication",
        "publication_status": "approved_for_distribution",
        "evidence_boundary": "Scenario assumptions are illustrative and no outcome is an observed firm or sector effect.",
        "output": {"file": PDF_NAME, "sha256": sha256(path), "page_count": len(reader.pages)},
        "public_data": {"file": str(PUBLIC_DATA.relative_to(ROOT)), "sha256": sha256(PUBLIC_DATA)},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    print(generate())
