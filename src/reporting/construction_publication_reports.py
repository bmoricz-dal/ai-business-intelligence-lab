"""Generate the owner-approved construction sector publication set.

The four reports use secondary evidence only. They preserve denominators,
evidence types and transfer limits, and the worked case is explicitly fictional.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/pdf"
REPORT_DATE = "12 August 2026"
AUTHOR = "Benedek Moricz"
BRAND = "DAL Data & AI Lab"

PAGE_W, PAGE_H = A4
LEFT = RIGHT = 18 * mm
TOP = 20 * mm
BOTTOM = 17 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

FOREST = colors.HexColor("#17372C")
DEEP = colors.HexColor("#0F211A")
GOLD = colors.HexColor("#D7A845")
PALE = colors.HexColor("#F3E7C8")
MINT = colors.HexColor("#E8F2EC")
PAPER = colors.HexColor("#FBFAF5")
INK = colors.HexColor("#23362E")
MUTED = colors.HexColor("#607068")
LINE = colors.HexColor("#CAD5CE")
WHITE = colors.white

ONS = "https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation/datasets/ukbusinessactivitysizeandlocation"
UKBDS = "https://www.gov.uk/government/statistics/uk-business-data-survey-2026"
DSIT_SKILLS = "https://www.gov.uk/government/publications/skills-for-ai-what-works-for-ai-upskilling-in-the-uk/research-evidence-analysis-and-methodology-what-works-for-ai-upskilling-in-the-uk"
RICS_AI = "https://www.rics.org/news-insights/artificial-intelligence-in-construction-report"
RICS_STANDARD = "https://www.rics.org/profession-standards/rics-standards-and-guidance/conduct-competence/responsible-use-of-ai"
DBT_SME = "https://www.gov.uk/government/publications/understanding-technology-adoption-among-uk-smes"
CAST = "https://assets.publishing.service.gov.uk/media/6a26e9cc2cdcfdb7436ac0e6/supporting_case_studies.pdf"
CONSTRUCTIONCO = "https://www.cipd.org/uk/knowledge/case-studies/construction-company-ai/"
BID_MODEL = "https://www.tandfonline.com/doi/abs/10.1080/15623599.2026.2629023"
NCSC = "https://www.ncsc.gov.uk/news/joint-ventures-construction-guidance"
BSR = "https://www.gov.uk/guidance/building-control-approval-for-higher-risk-buildings"


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CKicker", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10, tracking=1, textColor=GOLD, spaceAfter=8))
styles.add(ParagraphStyle(name="CH1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=FOREST, spaceAfter=8))
styles.add(ParagraphStyle(name="CH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=FOREST, spaceBefore=7, spaceAfter=5))
styles.add(ParagraphStyle(name="CBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12.8, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="CBullet", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.6, leading=12.2, textColor=INK, leftIndent=11, firstLineIndent=-8, spaceAfter=4))
styles.add(ParagraphStyle(name="CSmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.8, leading=9.2, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="CTHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=6.8, leading=8.6, textColor=WHITE))
styles.add(ParagraphStyle(name="CTBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.8, leading=9, textColor=INK))
styles.add(ParagraphStyle(name="CTBodyBold", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=6.8, leading=9, textColor=FOREST))
styles.add(ParagraphStyle(name="CMetric", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=19, leading=22, textColor=FOREST, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CMetricLabel", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=6.8, leading=8.5, textColor=INK, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CCallout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=FOREST))
styles.add(ParagraphStyle(name="CSource", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.3, leading=8.2, textColor=MUTED, spaceAfter=4))


def p(text: str, style: str = "CBody") -> Paragraph:
    return Paragraph(text, styles[style])


def bullet(text: str) -> Paragraph:
    return p(f"- {text}", "CBullet")


def callout(text: str) -> Table:
    table = Table([[p(text, "CCallout")]], colWidths=[CONTENT_W])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("LINEBEFORE", (0, 0), (0, -1), 4, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def table(headers: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    data = [[p(cell, "CTHead") for cell in headers]]
    data.extend([[p(cell, "CTBodyBold" if index == 0 else "CTBody") for index, cell in enumerate(row)] for row in rows])
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    rules = [
        ("BACKGROUND", (0, 0), (-1, 0), FOREST), ("GRID", (0, 0), (-1, -1), .4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for row_index in range(2, len(data), 2):
        rules.append(("BACKGROUND", (0, row_index), (-1, row_index), MINT))
    result.setStyle(TableStyle(rules))
    return result


def metrics(items: list[tuple[str, str, str]]) -> Table:
    cells = [[p(value, "CMetric"), p(label, "CMetricLabel"), p(note, "CSmall")] for value, label, note in items]
    result = Table([cells], colWidths=[CONTENT_W / len(items)] * len(items))
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MINT), ("BOX", (0, 0), (-1, -1), .5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), .5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return result


def source(number: int, label: str, url: str) -> Paragraph:
    return p(f'<b>{number}. {label}</b><br/><link href="{url}" color="#7A5410">{url}</link>', "CSource")


def page_frame(canvas, doc, short_title: str) -> None:
    canvas.saveState()
    canvas.setFillColor(FOREST)
    canvas.rect(0, PAGE_H - 9 * mm, PAGE_W, 9 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(LEFT, PAGE_H - 6 * mm, BRAND)
    canvas.setFont("Helvetica", 6.4)
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 6 * mm, short_title)
    canvas.setStrokeColor(LINE)
    canvas.line(LEFT, 12 * mm, PAGE_W - RIGHT, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.4)
    canvas.drawString(LEFT, 8 * mm, "Owner-approved publication | Secondary evidence and explicit limits")
    canvas.drawRightString(PAGE_W - RIGHT, 8 * mm, str(doc.page))
    canvas.restoreState()


def cover(canvas, doc, title_lines: list[str], strapline: str, footer: str) -> None:
    canvas.saveState()
    canvas.setFillColor(DEEP)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#284B3E"))
    for x in range(0, int(PAGE_W), 32):
        canvas.line(x, 0, x, PAGE_H)
    for y in range(0, int(PAGE_H), 32):
        canvas.line(0, y, PAGE_W, y)
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(LEFT, PAGE_H - 24 * mm, BRAND.upper())
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 26)
    y = PAGE_H - 55 * mm
    for line in title_lines:
        canvas.drawString(LEFT, y, line)
        y -= 12 * mm
    canvas.setFillColor(PALE)
    canvas.setFont("Helvetica", 10.5)
    canvas.drawString(LEFT, y - 3 * mm, strapline)
    canvas.setFillColor(GOLD)
    canvas.rect(LEFT, 55 * mm, 48 * mm, 3 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(LEFT, 41 * mm, REPORT_DATE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(LEFT, 34 * mm, f"Prepared by {AUTHOR}")
    canvas.setFillColor(PALE)
    canvas.drawRightString(PAGE_W - RIGHT, 21 * mm, footer)
    canvas.restoreState()


def readiness_story() -> list:
    story = [PageBreak(), p("EXECUTIVE BRIEF", "CKicker"), p("Large SME reach; uneven operational readiness", "CH1")]
    story += [callout("Construction is the recommended next sector because it combines the largest registered-SME frame in the shortlist with below-benchmark AI use, thin integration and a very limited policy signal. The official sector estimates are not SME-only."), Spacer(1, 8)]
    story.append(metrics([("384,525", "registered SMEs", "SIC F, VAT/PAYE, March 2025"), ("21.5%", "any listed AI use", "95% CI 14.2%-28.8%; base about 330"), ("3.1%", "AI guidance", "AI users; 95% CI 0%-9.2%; base about 100")]))
    story += [Spacer(1, 9), p("What can be said", "CH2"), bullet("AI experimentation is visible in construction, but there is no defensible SME-only adoption rate."), bullet("Integration and policy estimates are conditional on AI use and are imprecise."), bullet("The evidence supports bounded workflow experiments, not autonomous construction decisions."), p("What cannot be said", "CH2"), bullet("The UKBDS percentages cannot be multiplied by the ONS SME count."), bullet("No source establishes sector-wide productivity, profit, safety or compliance effects."), bullet("The readiness dimensions are an organising framework, not a maturity score.")]

    story += [PageBreak(), p("01  SECTOR AND PRIORITY", "CKicker"), p("Why construction follows accounting", "CH1")]
    story.append(table(["Candidate", "Registered SMEs", "AI use", "Weighted score"], [["Construction", "384,525", "21.5%", "4.80 / 5"], ["Manufacturing", "128,950", "31.9%", "4.30 / 5"], ["Retail", "212,455", "29.6% broad proxy", "4.25 / 5"], ["Technology", "122,310", "58.2% broad proxy", "3.40 / 5"], ["Finance", "56,035", "43.0%", "3.20 / 5"], ["Legal", "33,360", "50.6% broad proxy", "3.05 / 5"]], [48*mm, 40*mm, 42*mm, 44*mm]))
    story += [Spacer(1, 7), p("The score is a transparent judgement aid", "CH2"), p("Weights cover registered-SME reach, adoption/readiness gap, authoritative evidence, simulator fit and portfolio distinctiveness. The score is not a statistical model, market-demand measure or willingness-to-pay estimate. A sensitivity that doubles evidence coverage still leaves construction narrowly ahead of manufacturing."), p("Population boundary", "CH2"), p("The ONS frame covers VAT and/or PAYE-registered enterprises in SIC divisions 41, 42 and 43 with 0-249 employees. Counts are control-rounded and exclude unregistered businesses.")]

    story += [PageBreak(), p("02  FIVE READINESS DIMENSIONS", "CKicker"), p("Task use has moved ahead of operating controls", "CH1")]
    story.append(table(["Dimension", "Evidence signal", "Decision implication"], [["AI use", "21.5% any listed AI use; all construction business sizes", "Treat the estimate as sector context, not SME prevalence"], ["Integration", "14.0% among construction AI users; CI 1.9%-26.2%", "Test one workflow and keep manual fallback"], ["Governance", "3.1% policy/guidance among AI users; CI includes zero", "Name approved use, data rules, review and incidents"], ["Use cases", "Tender preparation, documents, scheduling and coordination", "Begin with bounded, reviewable information work"], ["Pathway", "Use and pilots are more visible than organisation-wide deployment", "Scale only after quality and total effort are measured"]], [32*mm, 72*mm, 70*mm]))
    story += [Spacer(1, 8), callout("The widest gap is not access to a chatbot. It is the ability to connect an approved tool to a defined workflow with traceability, human review and a stop rule."), p("Direct industry context", "CH2"), p("In the global RICS survey, 45% reported no AI implementation, 34% an early pilot, just under 12% regular use in specific processes and less than 1% organisation-wide use. The sample is global, 48% UK and not SME-only.")]

    story += [PageBreak(), p("03  PRACTICAL IMPLICATION", "CKicker"), p("Start with controlled document work", "CH1"), p("Tender requirement extraction and evidence matching offer a testable entry point because inputs, source clauses, omissions, citations and review decisions can remain visible. The experiment should exclude final pricing, programme commitments, method statements, safety judgements and regulatory conclusions."), p("Minimum pilot measures", "CH2"), table(["Measure", "Baseline and pilot question"], [["Preparation", "How many person-hours are used before review?"], ["Review", "How much qualified review and correction are required?"], ["Coverage", "How many mandatory requirements are identified and evidenced?"], ["Traceability", "Can each material statement be linked to an approved source?"], ["Quality", "What omissions, unsupported claims and rework occur?"], ["Control", "Are incidents, overrides, owners and rollback recorded?"]], [45*mm, 129*mm]), Spacer(1, 8), callout("A positive time signal is not ROI. Licences, setup, training, correction, assurance, incidents and opportunity cost remain inside the decision boundary.")]

    story += [PageBreak(), p("04  SOURCES AND LIMITS", "CKicker"), p("Traceable evidence; bounded conclusion", "CH1"), source(1, "ONS - UK business: activity, size and location 2025", ONS), source(2, "DSIT - UK Business Data Survey 2026", UKBDS), source(3, "DSIT - What works for AI upskilling in UK construction", DSIT_SKILLS), source(4, "RICS - Artificial intelligence in construction report 2025", RICS_AI), source(5, "DBT - Understanding technology adoption among UK SMEs", DBT_SME), p("Conclusion", "CH2"), p("Construction is a defensible next-sector research priority. The current evidence supports a controlled workflow test and a visible governance layer. It does not support an exact construction-SME adoption rate or a promise of business benefit."), callout("Descriptive secondary research only. Not construction, safety, legal, regulatory, procurement or investment advice.")]
    return story


def benefits_story() -> list:
    story = [PageBreak(), p("EXECUTIVE BRIEF", "CKicker"), p("Controlled document work is the strongest near-term fit", "CH1"), callout("The evidence supports a plausible workflow case for requirement extraction, evidence retrieval and first-draft control. It does not establish UK construction-SME ROI or autonomous construction."), Spacer(1, 8)]
    story.append(metrics([("30%", "document management", "Perceived high significance; global RICS survey"), ("96.25%", "prototype F1", "Requirement extraction; two-case research setting"), ("60 to 15", "reported minutes", "Large-company legal review; self-reported")]))
    story += [Spacer(1, 9), p("Keep evidence types separate", "CH2"), bullet("Industry perception identifies where professionals expect significance."), bullet("Prototype performance measures a narrow technical task."), bullet("A company case can illustrate implementation but does not create a sector benchmark."), bullet("None of these measures tender quality, win rate, margin, safety or compliance.")]

    story += [PageBreak(), p("01  EVIDENCE LADDER", "CKicker"), p("Claim strength moves with evidence strength", "CH1"), table(["Evidence", "Observed signal", "Permitted interpretation"], [["RICS professional survey", "36% scheduling/progress, 30% document management, 29% risk", "Perceived opportunity in a global, non-SME-only sample"], ["Bid research prototype", "96.25% average F1 reported for extraction", "Narrow technical performance in the reported test"], ["ConstructionCo case", "Legal review reportedly reduced from about 60 to 15 minutes", "Self-reported departmental transfer case in a large employer"], ["Cast Consultancy", "Qualitative confidence and capability improvements", "Named SME implementation journey, not performance evaluation"], ["DSIT skills synthesis", "Tender preparation and programme coordination priorities", "Official implementation and training context"]], [38*mm, 64*mm, 72*mm]), Spacer(1, 8), callout("The signals are not pooled, averaged or converted into a construction-SME effect size.")]

    story += [PageBreak(), p("02  SYSTEM FIT", "CKicker"), p("Set autonomy by consequence and verifiability", "CH1"), table(["Position", "Candidate workflow", "Minimum control"], [["Controlled deployment", "Tender extraction, document classification, source-backed response skeletons", "Approved sources, citations, version control and named reviewer"], ["Conditional deployment", "Scheduling support, risk prompts, contract review and coordination", "Specialist review, tested integration, escalation and audit trail"], ["Do not delegate autonomously", "Safety decisions, regulatory conclusions, final pricing, programmes and commitments", "Professional accountability and final judgement remain human"]], [43*mm, 67*mm, 64*mm]), Spacer(1, 8), p("Why tender support", "CH2"), p("The workflow is document-heavy, reversible and testable. A requirement can be compared with its source clause, candidate evidence can be accepted or rejected, and unsupported content can remain visibly incomplete."), p("Where the system stops", "CH2"), p("The workflow cannot determine buildability, price the job, approve a programme, produce a final method statement or make safety and regulatory decisions.")]

    story += [PageBreak(), p("03  MEASURE TOTAL WORKFLOW PERFORMANCE", "CKicker"), p("Draft speed alone is not a benefit", "CH1"), table(["Outcome family", "Measures"], [["Time", "Preparation, review, correction, rework and approval hours"], ["Coverage", "Mandatory requirements found, missed and wrongly classified"], ["Evidence", "Relevant approved sources found, unsupported statements and citation defects"], ["Quality", "Material omissions, contradictions, false confidence and final corrections"], ["Control", "Incidents, escalations, overrides, rollback and retained audit trail"], ["Economics", "Licences, setup, integration, training, assurance and opportunity cost"]], [45*mm, 129*mm]), Spacer(1, 8), callout("Proceed only if quality and control remain acceptable after review and correction effort is included."), p("A valid stop decision", "CH2"), p("If documents are inconsistent, evidence ownership is weak, reviewers cannot explain the output or the benefit disappears after assurance, holding or stopping is a successful control outcome.")]

    story += [PageBreak(), p("04  SOURCES AND VERDICT", "CKicker"), p("A bounded benefits conclusion", "CH1"), source(1, "RICS - Artificial intelligence in construction report 2025", RICS_AI), source(2, "DSIT - Construction AI upskilling evidence", DSIT_SKILLS), source(3, "Generative AI model for construction bid preparation", BID_MODEL), source(4, "CIPD/IFOW - ConstructionCo AI journey", CONSTRUCTIONCO), source(5, "DSIT - Cast Consultancy supporting case", CAST), source(6, "RICS - Responsible use of AI standard", RICS_STANDARD), p("Verdict", "CH2"), p("A controlled tender-document workflow is a credible pilot candidate. Published evidence does not establish causal UK construction-SME productivity, profit, safety or compliance improvement."), callout("Not construction, legal, safety, regulatory, procurement or investment advice.")]
    return story


def journeys_story() -> list:
    story = [PageBreak(), p("EXECUTIVE BRIEF", "CKicker"), p("Follow workflow change, not product announcements", "CH1"), callout("Three evidence bundles show different parts of implementation. They are kept separate by organisation, research method and outcome type; missing stages are not reconstructed."), Spacer(1, 8), metrics([("90", "approx. employees", "Cast Consultancy SME case"), ("3", "case bundles", "SME, large-company and prototype"), ("0", "pooled ROI claims", "Transfer the design, not another result")]), Spacer(1, 9), p("Comparison frame", "CH2"), table(["Stage", "Question"], [["Problem", "Which workflow or capability gap triggered the work?"], ["Selection", "How were requirements, users and boundaries defined?"], ["Pilot", "What was tested, by whom and with what controls?"], ["Adaptation", "What changed after feedback or failure?"], ["Outcome", "What was measured, reported or left unknown?"]], [42*mm, 132*mm])]

    story += [PageBreak(), p("01  CAST CONSULTANCY", "CKicker"), p("A live workflow anchored tool-based upskilling", "CH1"), table(["Journey point", "Published evidence"], [["Starting point", "A roughly 90-person consultancy needed to understand the Gateway 2 workflow."], ["Implementation", "A group of about 10-15 project managers used a tool-based learning approach."], ["Feedback", "Users raised practical issues and fed them back to the provider."], ["Reported outcome", "Qualitative confidence, capability, collaboration and critical-review gains."], ["Boundary", "No audited time, cost, quality, safety or compliance result."]], [44*mm, 130*mm]), Spacer(1, 8), p("Transfer lesson", "CH2"), p("Tie upskilling to a live, bounded workflow. Keep users, reviewers and the provider close enough for problems to change the implementation."), callout("The case supports an implementation design, not a productivity claim."), source(1, "DSIT supporting case studies - Cast Consultancy", CAST), source(2, "Building Safety Regulator - higher-risk building control approval", BSR)]

    story += [PageBreak(), p("02  CONSTRUCTIONCO", "CKicker"), p("Consultation and governance followed an earlier setback", "CH1"), table(["Journey point", "Published evidence"], [["Starting point", "A previous system struggled after limited consultation; AI activity was fragmented."], ["Selection", "A cross-functional group used MoSCoW requirements and identified bounded use cases."], ["Controls", "Confidence levels, data leakage, legal requirements and strategy were made visible."], ["Reported outcome", "Legal document review reportedly fell from about 60 to 15 minutes."], ["Boundary", "Several-thousand-employee housebuilder; estimate was self-reported and not independently evaluated."]], [44*mm, 130*mm]), Spacer(1, 8), p("Transfer lesson", "CH2"), p("Start with users and requirements before tool choice. A failed digital implementation can be relevant evidence about consultation and change management without becoming an AI outcome."), callout("Do not transfer the reported time saving to an SME business case."), source(1, "CIPD/IFOW - ConstructionCo AI journey", CONSTRUCTIONCO)]

    story += [PageBreak(), p("03  BID-PREPARATION PROTOTYPE", "CKicker"), p("Technical performance is one part of a tender system", "CH1"), table(["Journey point", "Published evidence"], [["Problem", "Repeated extraction, retrieval and drafting work in construction bid preparation."], ["System", "Requirement extraction, semantic retrieval, a structured repository and draft generation."], ["Reported result", "96.25% average F1 in the reported quantitative test."], ["What remains", "Evidence approval, commercial challenge, delivery validation and submission assurance."], ["Boundary", "Two-case research prototype; not a UK SME field outcome, tender win rate or ROI."]], [44*mm, 130*mm]), Spacer(1, 8), p("Transfer lesson", "CH2"), p("Evaluate extraction separately from evidence matching, drafting, specialist review and the final submission decision."), callout("A high extraction score cannot validate an unsupported statement or make a commercial commitment."), source(1, "Generative AI model for construction bid preparation", BID_MODEL)]

    story += [PageBreak(), p("04  CROSS-CASE SYNTHESIS", "CKicker"), p("Five lessons survive the evidence boundaries", "CH1"), bullet("Begin with one defined workflow and a named operational owner."), bullet("Include the people who do and review the work before selecting the tool."), bullet("Keep source traceability, exception handling and human override visible."), bullet("Measure correction and review effort alongside preparation time."), bullet("Transfer implementation design, not another organisation's outcome."), p("Sources", "CH2"), source(1, "DSIT supporting construction cases", CAST), source(2, "CIPD/IFOW ConstructionCo case", CONSTRUCTIONCO), source(3, "Construction bid-preparation research prototype", BID_MODEL), source(4, "DBT - Understanding technology adoption among UK SMEs", DBT_SME), callout("Secondary evidence only. No pooled ROI, vendor ranking or reconstructed success story.")]
    return story


def tender_story() -> list:
    story = [PageBreak(), p("EXECUTIVE BRIEF", "CKicker"), p("A synthetic tender workflow for controlled adoption", "CH1"), callout("Northstar Build Ltd is a fictional 18-person contractor. The community-centre refurbishment, tender clauses, evidence and calculations are synthetic. The case demonstrates a method; it does not produce a real bid."), Spacer(1, 8), metrics([("18", "fictional employees", "Scenario input, not a sector average"), ("6", "workstations", "Gate, extract, evidence, draft, challenge, assure"), ("0", "real uploads", "Browser-only deterministic experience")]), Spacer(1, 9), p("Case verdict", "CH2"), bullet("AI may assist bounded requirement extraction, retrieval and first-draft structure."), bullet("Human owners retain commercial, delivery, safety, regulatory and submission decisions."), bullet("A pilot compares total effort and quality against the same baseline."), bullet("Hold, revise and stop are valid outcomes.")]

    story += [PageBreak(), p("01  THE FICTIONAL CASE", "CKicker"), p("Northstar Build Ltd", "CH1"), table(["Case item", "Synthetic assumption", "Status"], [["People", "18-person regional contractor", "Invented scenario"], ["Opportunity", "Community-centre refurbishment", "Invented tender"], ["Problem", "Repeated clause extraction and evidence assembly", "Hypothesis to test"], ["Inputs", "Four fixed clauses and controlled evidence records", "Synthetic browser data"], ["Excluded", "Real client data, prices, programmes, method statements and safety decisions", "Hard control boundary"], ["Decision", "Human submission sign-off", "Cannot be delegated"]], [36*mm, 88*mm, 50*mm]), Spacer(1, 8), p("Why this workflow", "CH2"), p("Tender documents make requirements, evidence gaps and unsupported claims observable. The design can demonstrate safe stops without pretending to evaluate construction engineering or commercial judgement."), callout("No upload, live model, client system or construction software connection is used.")]

    story += [PageBreak(), p("02  SIX WORKSTATIONS", "CKicker"), p("From opportunity gate to assurance", "CH1"), table(["Stage", "Action", "Proceed signal"], [["1 Opportunity gate", "Check fit, capacity, deadline and prohibited assumptions", "Named owner and conditional bid decision"], ["2 Requirements", "Extract and compare every clause with source wording", "Mandatory requirements reviewed"], ["3 Evidence", "Match current, relevant and owned evidence", "Gaps remain visible; evidence approved"], ["4 Draft control", "Prepare a source-linked response skeleton", "Every material statement has a source and reviewer"], ["5 Challenge", "Test delivery, commercial and commitment assumptions", "Issues resolved, assigned or held"], ["6 Assurance", "Run final human compliance and quality review", "Accountable person authorises any real submission"]], [39*mm, 79*mm, 56*mm]), Spacer(1, 8), callout("The simulation shows READY FOR HUMAN SIGN-OFF only after all synthetic review, evidence and challenge controls are complete. It never submits anything.")]

    story += [PageBreak(), p("03  PILOT GATES", "CKicker"), p("Proceed, revise, hold or stop", "CH1"), table(["Gate", "Proceed only when", "Stop or revise when"], [["G0 Scope", "Bid decision, owner and prohibited actions named", "Generic objective or unclear accountability"], ["G1 Data", "Approved documents, access and retention defined", "Sensitive data enters an unapproved tool"], ["G2 Known cases", "Extraction and retrieval pass fixed tests", "Material omission, invention or broken citation"], ["G3 Shadow", "Current process remains authoritative", "Users cannot explain or override output"], ["G4 Pilot", "Quality, review and total cost stay acceptable", "Draft speed disappears after correction"], ["G5 Scale", "Monitoring, support and rollback are approved", "Unresolved delivery, safety, commercial or lock-in risk"]], [28*mm, 73*mm, 73*mm]), Spacer(1, 8), p("Zero-tolerance boundaries", "CH2"), p("Unauthorised disclosure, invented mandatory requirements, unapproved commitments and autonomous safety or regulatory decisions trigger a stop or escalation.")]

    story += [PageBreak(), p("04  MEASUREMENT AND REUSE", "CKicker"), p("Replace every assumption with a local baseline", "CH1"), table(["Measure", "Record"], [["Baseline", "Preparation, review, correction, quality and incident measures for the current workflow"], ["Pilot", "The same measures after assistive tooling and controls"], ["Full cost", "Licences, setup, training, review, correction, assurance and incidents"], ["Capacity signal", "Baseline hours minus pilot preparation and added review/correction"], ["Decision", "Scale, limit, revise, hold or stop with reasons"]], [42*mm, 132*mm]), Spacer(1, 8), callout("A positive hour balance is not ROI. Quality, control, full cost and opportunity cost remain part of the decision."), p("Sources", "CH2"), source(1, "DSIT construction AI upskilling evidence", DSIT_SKILLS), source(2, "RICS responsible use of AI standard", RICS_STANDARD), source(3, "NCSC construction information-security guidance", NCSC), source(4, "Construction bid-preparation research prototype", BID_MODEL), p("Boundary", "CH2"), p("Evidence-informed fictional composite. Not construction, legal, safety, regulatory, procurement or investment advice.")]
    return story


REPORTS = [
    ("UK_Construction_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf", ["UK Construction SMEs:", "AI Adoption and", "Operational Readiness, 2026"], "A five-dimension current-state report", "USE | INTEGRATION | GOVERNANCE | WORKFLOW | PATHWAY", "CONSTRUCTION AI READINESS 2026", readiness_story),
    ("UK_Construction_SMEs_AI_Benefits_and_System_Fit_2026.pdf", ["UK Construction SMEs:", "AI Benefits and", "System Fit, 2026"], "A workflow-level secondary-evidence review", "WORKFLOW | OUTCOME | CONTROL | TRANSFER", "CONSTRUCTION AI BENEFITS 2026", benefits_story),
    ("UK_Construction_SMEs_AI_Adoption_Journeys_2026.pdf", ["UK Construction SMEs:", "AI Adoption", "Journeys, 2026"], "Three evidence-bounded implementation journeys", "PROBLEM | PILOT | ADAPTATION | OUTCOME", "CONSTRUCTION AI JOURNEYS 2026", journeys_story),
    ("UK_Construction_SME_AI_Tender_Worked_Case_2026.pdf", ["UK Construction SME:", "AI Tender", "Worked Case, 2026"], "A synthetic, controlled adoption method", "GATE | EXTRACT | EVIDENCE | CHALLENGE | ASSURE", "CONSTRUCTION TENDER WORKED CASE", tender_story),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(spec: tuple) -> Path:
    filename, title_lines, strapline, footer, short_title, story_builder = spec
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / filename
    doc = SimpleDocTemplate(str(destination), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM, title=" ".join(title_lines), author=AUTHOR, subject=strapline)
    doc.build(story_builder(), onFirstPage=lambda canvas, current_doc: cover(canvas, current_doc, title_lines, strapline, footer), onLaterPages=lambda canvas, current_doc: page_frame(canvas, current_doc, short_title))
    reader = PdfReader(str(destination))
    metadata = {"title": " ".join(title_lines), "author": AUTHOR, "report_date": REPORT_DATE, "page_count": len(reader.pages), "sha256": sha256(destination), "generated_at": datetime.now(timezone.utc).isoformat(), "status": "owner-approved publication", "evidence_mode": "secondary evidence only"}
    (OUTPUT / filename.replace(".pdf", ".metadata.json")).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    for report in REPORTS:
        path = build_report(report)
        print(f"built {path.name} ({len(PdfReader(str(path)).pages)} pages)")


if __name__ == "__main__":
    main()
