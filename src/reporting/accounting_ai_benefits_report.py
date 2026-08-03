"""Generate the accounting AI benefits and system-fit evidence review.

The report uses secondary evidence only. International field results are
presented as transfer evidence and are not converted into UK SME effect sizes.
"""

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
    BLUE,
    CONTENT_W,
    INK,
    LEFT,
    LINE,
    MUTED,
    NAVY,
    PALE,
    RIGHT,
    SKY,
    TEAL,
    WHITE,
    P,
    bullet,
    callout,
    metric_cards,
    report_table,
)
from src.reporting.publication_design import draw_page_frame, draw_signature_cover


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/pdf"
PUBLIC_DATA = ROOT / "data/public/accounting_ai_benefits_system_fit_2026.csv"
PDF_NAME = "UK_Accounting_SMEs_AI_Benefits_and_System_Fit_2026.pdf"
REPORT_DATE = "3 August 2026"
AUTHOR = "Benedek Moricz"
BRAND = "DAL Data & AI Lab"

JAR_URL = "https://onlinelibrary.wiley.com/doi/10.1111/1475-679x.70052"
DSIT_URL = "https://www.gov.uk/government/publications/ai-adoption-research/ai-adoption-research"
OECD_URL = "https://www.oecd.org/en/publications/the-effects-of-generative-ai-on-productivity-innovation-and-entrepreneurship_b21df222-en.html"
FRC_URL = "https://www.frc.org.uk/library/standards-codes-policy/audit-assurance-and-ethics/guidance/ai-in-audit/"
ICAEW_URL = "https://www.icaew.com/insights/viewpoints-on-the-news/2025/nov-2025/how-genai-can-save-you-time-during-the-accounting-cycle"
DUPS_URL = "https://www.gov.uk/government/publications/business-data-use-and-productivity-study-wave-2"
ONS_URL = "https://www.ons.gov.uk/businessindustryandtrade/business/businessservices/articles/artificialintelligenceinukbusinesses/2023to2026"

PAGE_W, PAGE_H = A4
TOP = 20 * mm
BOTTOM = 17 * mm


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_link(number: int, label: str, url: str) -> Paragraph:
    return P(
        f'<b>{number}. {label}</b><br/><link href="{url}" color="#2D83C5">{url}</link>',
        "SourceR",
    )


def page_frame(canvas, doc) -> None:
    draw_page_frame(canvas, doc, page_w=PAGE_W, page_h=PAGE_H, left=LEFT, right=RIGHT, brand=BRAND, short_title="Accounting AI benefits and system fit 2026", footer_note="Secondary evidence | UK transfer limits remain visible")


def cover(canvas, doc) -> None:
    draw_signature_cover(canvas, page_w=PAGE_W, page_h=PAGE_H, left=LEFT, right=RIGHT, brand=BRAND, series="Accounting sector / Benefits", formal_title="UK Accounting SMEs / Benefits and system fit / 2026", headline="Value is clearest when AI augments a controlled accounting workflow.", subtitle="What the secondary evidence can support - and where transfer stops.", report_date=REPORT_DATE, author=AUTHOR, taxonomy="Workflow / Outcome / System / Control / Transfer")


def build_story() -> list:
    story: list = [PageBreak()]
    story += [P("EXECUTIVE BRIEF", "Kicker"), P("The strongest signal is controlled workflow augmentation", "H1R")]
    story.append(callout(
        "AI can create measurable value in accounting work, but the present evidence supports a narrow conclusion: integrated systems can improve transaction-processing and close workflows when they combine accounting data, workflow rules, confidence or exception handling and professional review. The evidence does not support autonomous accounting or a UK SME ROI benchmark."
    ))
    story += [Spacer(1, 8)]
    story.append(metric_cards([
        ("79", "SME client firms", "Peer-reviewed US operational field setting"),
        ("7.5-7.9", "days", "Improvement in a reporting-timeliness proxy"),
        ("700", "UK AI users", "Official self-reported impact context"),
    ]))
    story += [Spacer(1, 9), P("What can be concluded", "H2R")]
    story.append(bullet("Bookkeeping, transaction categorisation, reconciliations and month-end close have the clearest measurable accounting-specific evidence."))
    story.append(bullet("In one peer-reviewed US field setting, integrated GenAI use was associated with faster reporting timeliness and less attention to routine data-entry work."))
    story.append(bullet("A narrow framed experiment found that AI assistance improved classification accuracy on average, while non-consensus AI recommendations could increase error risk."))
    story.append(bullet("UK AI-using businesses often report productivity and process benefits, but those reports are broad-sector, self-reported and not causal accounting-SME estimates."))
    story += [P("What cannot be concluded", "H2R")]
    story.append(P("There is no defensible UK accounting-SME productivity uplift, ROI, revenue effect or vendor ranking in the open evidence reviewed. The 7.5 to 7.9 day result is international transfer evidence, not a UK benchmark."))

    story += [PageBreak(), P("01  QUESTION AND EVIDENCE GATE", "Kicker"), P("A benefits study needs a different standard from an adoption study", "H1R")]
    story.append(P("The current-state accounting report established how much AI use has started and which tasks are visible. This second study asks a harder question: whether a defined AI system changes a measurable accounting outcome, compared with an appropriate baseline, and under what controls."))
    story.append(report_table(
        ["Grade", "Evidence type", "Permitted interpretation"],
        [
            ["A", "Experimental or credible quasi-experimental effect for a defined task", "Improved or caused, but only within the tested task and design"],
            ["B", "Peer-reviewed operational field evidence with longitudinal controls", "Associated with; may support a transfer hypothesis"],
            ["C", "Official or representative self-reported evidence", "Businesses reported; not a measured causal effect"],
            ["D", "Professional guidance or workflow illustration", "Supports mechanism and control design only"],
        ],
        [24 * mm, 76 * mm, 74 * mm],
    ))
    story += [Spacer(1, 8), P("Evidence-gate result", "H2R")]
    story.append(P("The gate passes for a bounded evidence review. The evidence base contains one strong accounting-specific operational study, official UK impact context, an experimental evidence synthesis and authoritative UK audit controls. It does not contain an open UK accounting-SME causal evaluation."))
    story.append(callout("Publication boundary: report workflow-level evidence and uncertainty. Do not average sources, extrapolate international effect sizes to the UK or convert self-reported impacts into ROI.", colour=PALE, edge=TEAL))

    story += [PageBreak(), P("02  STRONGEST WORKFLOW EVIDENCE", "Kicker"), P("Transaction processing and close support", "H1R")]
    story.append(P("Choi and Xie study an AI-enabled accounting platform serving 79 US private SME clients from January 2023 to March 2025, with more than 200,000 transaction records. The system combines a knowledge graph, retrieval-augmented generation and language models with workflow management and a human-in-the-loop review module."))
    story.append(report_table(
        ["Outcome", "Finding", "Evidence-safe reading"],
        [
            ["Reporting timeliness", "Alternative longitudinal designs estimate about 7.5 to 7.9 days faster", "Most robust operational signal; still not a UK causal benchmark"],
            ["Ledger granularity", "About 12% higher in the main specification", "Quality proxy; smaller and not always significant in alternative designs"],
            ["Task allocation", "Approximately 9% of time shifted from routine data entry", "Consistent with augmentation; platform-specific measurement"],
            ["Client capacity", "Positive association; magnitude varies by specification", "Learning and selection prevent a standalone causal claim"],
        ],
        [45 * mm, 62 * mm, 67 * mm],
    ))
    story += [Spacer(1, 7), P("Why the system matters", "H2R")]
    story.append(P("The evidence is not about an isolated chatbot. The AI layer is connected to accounting records and workflow rules, produces confidence signals and routes exceptions to accountants who can review or override suggestions. This combination is the relevant system-fit hypothesis for accounting SMEs."))
    story += [P("Transfer limits", "H2R")]
    story.append(P("The firms are US private clients of one technology partner, the sample is non-random, the operational data are proprietary and the environment may differ from UK practice regulation, tax work and client mix. Longitudinal and staggered-adoption analyses reduce but do not eliminate selection concerns."))

    story += [PageBreak(), P("03  HUMAN-AI PERFORMANCE", "Kicker"), P("Benefits and errors coexist", "H1R")]
    story.append(callout("The relevant question is not whether AI is accurate in general. It is whether the workflow detects uncertainty, routes exceptions and preserves professional judgement where errors matter."))
    story += [Spacer(1, 8)]
    story.append(report_table(
        ["Evidence", "Result", "Operational implication"],
        [
            ["Framed classification experiment", "AI assistance improved classification accuracy on average", "A narrow task can benefit from decision support"],
            ["Non-consensus recommendations", "Reliance on inaccurate or non-consensus suggestions increased error risk", "Users must not treat fluent output as authority"],
            ["Confidence scores", "Experienced accountants intervened more when AI confidence was low", "Confidence can support triage, not replace review"],
            ["Professional expertise", "The study finds complementarity between expertise and AI", "Benefits depend on judgement and escalation capability"],
        ],
        [48 * mm, 60 * mm, 66 * mm],
    ))
    story += [Spacer(1, 8), P("System-fit reading", "H2R")]
    story.append(P("Structured, repetitive and reviewable tasks are the strongest fit: transaction coding, matching, reconciliations, close checklists and first-draft explanations. Fit weakens when a task is ambiguous, high-stakes or difficult to verify, including tax conclusions, audit conclusions and material postings."))
    story.append(P("The OECD review of experimental studies reaches the same general mechanism: productivity effects depend on task fit, user experience and the ability to evaluate outputs; applying GenAI beyond its capabilities can lower quality."))

    story += [PageBreak(), P("04  UK BENEFIT CONTEXT", "Kicker"), P("Reported productivity is common; measured revenue change is not", "H1R")]
    story.append(P("DSIT surveyed 3,500 UK private businesses with at least five employees in 2025. The impact questions were asked of 700 businesses using AI. These figures are useful context but are self-reported, broad-sector and not accounting-specific."))
    story.append(metric_cards([
        ("75%", "reported productivity impact", "Improved workforce productivity"),
        ("57%", "reported process impact", "New or improved processes"),
        ("77%", "reported no revenue change", "12% reported an increase"),
    ]))
    story += [Spacer(1, 9)]
    story.append(report_table(
        ["Measure", "Estimate", "Interpretation"],
        [
            ["Any workforce-productivity impact", "75%", "Multiple-response impact question; businesses reported an impact"],
            ["Estimated employee-productivity increase", "56%", "Respondent estimate; 35% reported no change and 1% a decrease"],
            ["New or improved processes", "57%", "Supports a process-improvement hypothesis, not an effect size"],
            ["No impact so far", "10%", "Benefit is not universal even among adopters"],
            ["No revenue change", "77%", "Productivity or process benefits do not automatically become revenue"],
        ],
        [63 * mm, 28 * mm, 83 * mm],
    ))
    story.append(callout("UK conclusion: businesses frequently report operational benefits, but the available official evidence does not isolate accounting SMEs or measure a causal productivity uplift."))

    story += [PageBreak(), P("05  SYSTEM-FIT PATHWAY", "Kicker"), P("Where accounting SMEs should expect the strongest fit", "H1R")]
    story.append(report_table(
        ["Position", "Workflow examples", "Minimum control boundary"],
        [
            ["Controlled deployment", "Transaction coding, reconciliations, close checklists, draft explanations, internal research", "Approved data; workflow rules; confidence or exception handling; documented human review"],
            ["Conditional deployment", "Client communications, advisory preparation, forecasting, contract and document review", "Qualified reviewer; source checking; known-case testing; escalation route"],
            ["Do not delegate autonomously", "Tax conclusions, audit conclusions, material postings, financial or regulatory decisions", "Professional judgement and accountability remain with a qualified person"],
        ],
        [43 * mm, 67 * mm, 64 * mm],
    ))
    story += [Spacer(1, 9), P("Five conditions for beneficial adoption", "H2R")]
    story.append(bullet("Task fit: the task is sufficiently repeatable, bounded and verifiable."))
    story.append(bullet("Data fit: client data are accurate, authorised and handled within confidentiality rules."))
    story.append(bullet("Workflow fit: the AI is connected to the right records, rules and exception path."))
    story.append(bullet("Human fit: users understand limitations and can review, override and escalate."))
    story.append(bullet("Measurement fit: time, corrections, review effort and service outcomes are tracked against a baseline."))
    story += [P("What to measure", "H2R")]
    story.append(P("For bookkeeping and close, the most credible secondary-evidence-aligned measures are days to close, transaction-recording lag, exceptions per 1,000 transactions, correction or override rate, review minutes, reconciliations completed, clients supported and time reallocated to interpretation or advisory work. Revenue and margin should be treated as downstream outcomes, not assumed benefits."))

    story += [PageBreak(), P("06  CONTROLS AND ACCOUNTABILITY", "Kicker"), P("Controls are part of the benefit mechanism", "H1R")]
    story.append(P("The FRC's 2026 Generative and Agentic AI Guidance is audit-specific and does not measure benefits. It is nevertheless the strongest UK authority for the controls needed when AI output may inform high-stakes professional work."))
    story.append(report_table(
        ["Control category", "Purpose", "Accounting-SME application"],
        [
            ["System design and development", "Make the system responsive to intended use", "Bound prompts, sources, rules and permitted actions to a defined workflow"],
            ["Certification and testing", "Establish confidence before reliance", "Test against known transactions, edge cases and material-error scenarios"],
            ["Staff education and governance", "Reduce misuse and misunderstanding", "Approved tools, data rules, training and escalation responsibilities"],
            ["Human review and oversight", "Detect deficient output and preserve accountability", "Review thresholds, exception queues, sign-off and retained evidence"],
        ],
        [48 * mm, 55 * mm, 71 * mm],
    ))
    story += [Spacer(1, 8)]
    story.append(P("FRC guidance also makes a critical boundary explicit: technology does not change the accountability of firms and responsible individuals for audit quality. The same principle should guide tax, reporting and advisory workflows even where the precise regulatory duties differ."))
    story.append(callout("Benefit without control is not a complete outcome. Time saved must be assessed alongside correction, review, confidentiality and professional-accountability costs.", colour=PALE, edge=TEAL))

    story += [PageBreak(), P("07  CONCLUSION", "Kicker"), P("What the evidence supports now", "H1R")]
    story.append(P("The secondary evidence supports a clear but bounded conclusion: accounting AI is most likely to create measurable value when it augments structured workflows rather than replaces professional judgement."))
    story += [P("Strongest present use case", "H2R")]
    story.append(P("Bookkeeping, transaction processing, reconciliation and month-end close. One peer-reviewed operational field study associates an integrated AI workflow with faster reporting timeliness and less routine data-entry attention. The architecture includes accounting data, workflow management, confidence signals and human review."))
    story += [P("What remains promising rather than proven", "H2R")]
    story.append(P("Higher client capacity, more granular reporting, drafting, research, client communication and advisory preparation. These uses have plausible mechanisms and supporting contextual evidence, but they do not yet have a comparable UK accounting-SME outcome base."))
    story += [P("What is not supported", "H2R")]
    story.append(P("A UK accounting-SME productivity percentage, sector ROI, revenue uplift, vendor league table or autonomous-accounting recommendation. The evidence also does not show that every adopter benefits: 10% of UK AI users in the official survey reported no impact, while most reported no revenue change."))
    story += [P("Research verdict", "H2R")]
    story.append(callout("Proceed from current-state adoption research to workflow-specific benefit tracking. The next secondary-data update should add independent accounting field studies when they appear and reassess whether UK-specific evidence is strong enough for a quantified benchmark."))
    story.append(P("Overall confidence: moderate for the transaction-processing and close-support mechanism; moderate-to-low for transferring the magnitude to UK accounting SMEs; insufficient for ROI or vendor comparison.", "BodyBoldR"))

    story += [PageBreak(), P("08  METHODS AND SOURCES", "Kicker"), P("Transparent inclusion, transfer and claim controls", "H1R")]
    story.append(P("Sources were selected for accounting relevance, openness, methodological transparency and outcome measurability. International evidence was retained only when it observed real accounting workflows or tested a clearly defined accounting task. Professional guidance was separated from impact evidence."))
    story.append(report_table(
        ["Control", "Application"],
        [
            ["Population", "US accounting field evidence is labelled as transfer evidence; UK surveys remain broad-sector context"],
            ["Outcome", "Time, throughput, quality proxies and self-reported impacts remain separate"],
            ["Causality", "Operational associations are not rewritten as causal effects"],
            ["System", "Results are tied to the observed integrated platform, not to AI in general"],
            ["Cost", "Review, correction, training and governance are part of the benefit boundary"],
            ["Prohibited synthesis", "No averaging, composite score, ROI model or vendor ranking"],
        ],
        [48 * mm, 126 * mm],
    ))
    story += [Spacer(1, 7), P("Core sources", "H2R")]
    story.append(source_link(1, "Choi and Xie - Human + AI in Accounting, Journal of Accounting Research", JAR_URL))
    story.append(source_link(2, "DSIT - AI Adoption Research", DSIT_URL))
    story.append(source_link(3, "OECD - The effects of generative AI on productivity, innovation and entrepreneurship", OECD_URL))
    story.append(source_link(4, "Financial Reporting Council - AI in Audit guidance", FRC_URL))
    story.append(source_link(5, "ICAEW - How GenAI can save time during the accounting cycle", ICAEW_URL))
    story.append(source_link(6, "DSIT - Business data use and productivity study, wave 2", DUPS_URL))
    story.append(source_link(7, "ONS - Artificial intelligence in UK businesses: 2023 to 2026", ONS_URL))
    story += [Spacer(1, 6), P("Citation", "H2R")]
    story.append(P("Moricz, B. (2026). <i>UK Accounting SMEs: AI Benefits and System Fit, 2026.</i> DAL Data &amp; AI Lab."))
    story.append(P("This report is not accounting, legal, tax, audit, investment or procurement advice.", "SmallR"))
    return story


def validate_public_data() -> None:
    if not PUBLIC_DATA.exists():
        raise FileNotFoundError(PUBLIC_DATA)
    with PUBLIC_DATA.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) < 15:
        raise ValueError("Benefits evidence matrix must contain at least 15 observations")
    required = {"finding_id", "workflow", "outcome", "evidence_grade", "source_id", "causal_status"}
    if not required.issubset(rows[0]):
        raise ValueError("Benefits evidence matrix is missing required fields")
    if any(not row["main_limitation"] for row in rows):
        raise ValueError("Every benefits observation must retain a limitation")


def generate() -> Path:
    validate_public_data()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / PDF_NAME
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title="UK Accounting SMEs: AI Benefits and System Fit, 2026",
        author=AUTHOR,
        subject="Secondary-evidence review of accounting AI workflow benefits and system fit",
    )
    doc.build(build_story(), onFirstPage=cover, onLaterPages=page_frame)
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = [
        "secondary evidence",
        "7.5-7.9",
        "79",
        "700",
        "not a UK benchmark",
        "human review",
        "vendor ranking",
    ]
    missing = [item for item in required if item.lower() not in text.lower()]
    if missing:
        raise ValueError(f"Required report text missing: {missing}")
    metadata = {
        "title": "UK Accounting SMEs: AI Benefits and System Fit, 2026",
        "publication_date": "2026-08-03",
        "author": AUTHOR,
        "research_mode": "secondary_data_only",
        "approval_status": "owner_authorised_final_publication",
        "publication_status": "approved_for_distribution",
        "evidence_boundary": "No open UK accounting-SME causal evaluation was identified; international field results are transfer evidence only.",
        "output": {"file": PDF_NAME, "sha256": sha256(path), "page_count": len(reader.pages)},
        "public_data": {"file": str(PUBLIC_DATA.relative_to(ROOT)), "sha256": sha256(PUBLIC_DATA)},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    print(generate())
