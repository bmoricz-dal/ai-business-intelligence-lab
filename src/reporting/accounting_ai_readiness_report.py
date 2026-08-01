"""Generate the final UK Accounting SMEs AI readiness report.

The report uses secondary evidence only and keeps non-comparable adoption
definitions, populations and denominators separate.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/pdf"
PUBLIC_DATA = ROOT / "data/public/accounting_ai_readiness_2026.csv"
PDF_NAME = "UK_Accounting_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf"
REPORT_DATE = "1 August 2026"
AUTHOR = "Benedek Moricz"
BRAND = "DAL Data & AI Lab"

ONS_URL = "https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation/datasets/ukbusinessactivitysizeandlocation"
UKBDS_URL = "https://www.gov.uk/government/statistics/uk-business-data-survey-2026"
DSIT_URL = "https://www.gov.uk/government/publications/ai-adoption-research"
SAGE_URL = "https://www.sage.com/en-gb/-/media/files/sagedotcom/uk/documents/pdf/press-release-attachments/going-for-growth-report-2024.pdf"
AWEB_URL = "https://www.accountingweb.co.uk/resources/state-of-the-nation-ai-in-accountancy-and-bookkeeping"
FRC_URL = "https://www.frc.org.uk/library/standards-codes-policy/audit-assurance-and-ethics/guidance/ai-in-audit/"
ICAEW_URL = "https://www.icaew.com/technical/practice-resources/practice-news/ai-and-accountants"

PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 20 * mm
BOTTOM = 17 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

NAVY = colors.HexColor("#173E5B")
BLUE = colors.HexColor("#2D83C5")
SKY = colors.HexColor("#DDF2FF")
PALE = colors.HexColor("#EFF8FD")
ICE = colors.HexColor("#F8FCFE")
INK = colors.HexColor("#233E52")
MUTED = colors.HexColor("#60798B")
LINE = colors.HexColor("#C5DFEE")
TEAL = colors.HexColor("#138A8A")
CORAL = colors.HexColor("#C95D4D")
WHITE = colors.white


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Kicker", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.2, leading=10.5, tracking=1.0, textColor=BLUE, spaceAfter=8))
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=NAVY, alignment=TA_LEFT, spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=11.2, leading=17, textColor=INK, spaceAfter=8))
styles.add(ParagraphStyle(name="H1R", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=NAVY, spaceAfter=7))
styles.add(ParagraphStyle(name="H2R", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=BLUE, spaceBefore=5, spaceAfter=5))
styles.add(ParagraphStyle(name="H3R", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=9.3, leading=12, textColor=NAVY, spaceBefore=4, spaceAfter=3))
styles.add(ParagraphStyle(name="BodyR", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12.7, textColor=INK, spaceAfter=5.5))
styles.add(ParagraphStyle(name="BodyBoldR", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.8, leading=12.7, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallR", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9.7, textColor=MUTED, spaceAfter=3.5))
styles.add(ParagraphStyle(name="BulletR", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.6, leading=12.2, textColor=INK, leftIndent=11, firstLineIndent=-8, spaceAfter=3.2))
styles.add(ParagraphStyle(name="TableHeadR", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=6.8, leading=8.7, textColor=WHITE))
styles.add(ParagraphStyle(name="TableBodyR", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.7, leading=8.9, textColor=INK))
styles.add(ParagraphStyle(name="TableBodyBoldR", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=6.7, leading=8.9, textColor=NAVY))
styles.add(ParagraphStyle(name="MetricR", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=20, leading=22, textColor=BLUE, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="MetricLabelR", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=NAVY, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CalloutR", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10.1, leading=14.5, textColor=NAVY))
styles.add(ParagraphStyle(name="SourceR", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.5, leading=8.5, textColor=MUTED, spaceAfter=3))


def P(text: str, style: str = "BodyR") -> Paragraph:
    return Paragraph(text, styles[style])


def bullet(text: str) -> Paragraph:
    return P(f"- {text}", "BulletR")


def callout(text: str, colour=SKY, edge=BLUE) -> Table:
    table = Table([[P(text, "CalloutR")]], colWidths=[CONTENT_W])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colour),
        ("LINEBEFORE", (0, 0), (0, -1), 4, edge),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def report_table(headers: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    data = [[P(value, "TableHeadR") for value in headers]]
    for row in rows:
        data.append([P(value, "TableBodyBoldR" if i == 0 else "TableBodyR") for i, value in enumerate(row)])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for row_index in range(1, len(data)):
        if row_index % 2 == 0:
            style.append(("BACKGROUND", (0, row_index), (-1, row_index), PALE))
    table.setStyle(TableStyle(style))
    return table


def metric_cards(items: list[tuple[str, str, str]]) -> Table:
    cells = []
    for value, label, note in items:
        cells.append([P(value, "MetricR"), P(label, "MetricLabelR"), P(note, "SmallR")])
    table = Table([cells], colWidths=[CONTENT_W / len(items)] * len(items))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


class BarChart(Flowable):
    def __init__(self, rows: list[tuple[str, float, str]], height: float = 180):
        super().__init__()
        self.rows = rows
        self.width = CONTENT_W
        self.height = height

    def draw(self) -> None:
        drawing = Drawing(self.width, self.height)
        label_w = 155
        value_w = 36
        plot_w = self.width - label_w - value_w
        gap = (self.height - 30) / len(self.rows)
        for tick in (0, 25, 50, 75, 100):
            x = label_w + plot_w * tick / 100
            drawing.add(Line(x, 12, x, self.height - 8, strokeColor=LINE, strokeWidth=0.5))
            drawing.add(String(x, self.height - 2, f"{tick}%", fontName="Helvetica", fontSize=6.5, fillColor=MUTED, textAnchor="middle"))
        for index, (label, estimate, role) in enumerate(self.rows):
            y = self.height - 25 - index * gap
            colour = BLUE if role == "direct" else TEAL
            drawing.add(String(0, y + 1, label, fontName="Helvetica", fontSize=7.5, fillColor=INK))
            drawing.add(Rect(label_w, y - 2, plot_w * estimate / 100, 8, fillColor=colour, strokeColor=None))
            drawing.add(Circle(label_w + plot_w * estimate / 100, y + 2, 3.3, fillColor=colour, strokeColor=WHITE, strokeWidth=0.5))
            drawing.add(String(self.width, y, f"{estimate:.2f}%" if estimate % 1 else f"{estimate:.0f}%", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colour, textAnchor="end"))
        drawing.drawOn(self.canv, 0, 0)


def page_frame(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 9 * mm, PAGE_W, 9 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(LEFT, PAGE_H - 6 * mm, BRAND)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 6 * mm, "ACCOUNTING SECTOR AI READINESS 2026")
    canvas.setStrokeColor(LINE)
    canvas.line(LEFT, 12 * mm, PAGE_W - RIGHT, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(LEFT, 8 * mm, "Secondary-data research | Evidence definitions remain separate")
    canvas.drawRightString(PAGE_W - RIGHT, 8 * mm, f"{doc.page}")
    canvas.restoreState()


def cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#204F70"))
    for x in range(0, int(PAGE_W), 32):
        canvas.line(x, 0, x, PAGE_H)
    for y in range(0, int(PAGE_H), 32):
        canvas.line(0, y, PAGE_W, y)
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(LEFT, PAGE_H - 24 * mm, BRAND.upper())
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 28)
    title = ["UK Accounting SMEs:", "AI Adoption and", "Operational Readiness, 2026"]
    y = PAGE_H - 58 * mm
    for line in title:
        canvas.drawString(LEFT, y, line)
        y -= 12 * mm
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica", 11)
    canvas.drawString(LEFT, y - 3 * mm, "A five-dimension current-state report using secondary evidence only")
    canvas.setFillColor(BLUE)
    canvas.rect(LEFT, 55 * mm, 48 * mm, 3 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(LEFT, 41 * mm, REPORT_DATE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(LEFT, 34 * mm, f"Prepared by {AUTHOR}")
    canvas.setFillColor(SKY)
    canvas.drawRightString(PAGE_W - RIGHT, 21 * mm, "ADOPTION  |  INTEGRATION  |  GOVERNANCE  |  USE CASES  |  PATHWAYS")
    canvas.restoreState()


def source_link(number: int, label: str, url: str) -> Paragraph:
    return P(f'<b>{number}. {label}</b><br/><link href="{url}" color="#2D83C5">{url}</link>', "SourceR")


def build_story() -> list:
    story: list = [PageBreak()]
    story += [P("EXECUTIVE BRIEF", "Kicker"), P("What the evidence says now", "H1R")]
    story.append(callout("AI has moved beyond niche experimentation in UK accounting, but the measured level of adoption changes sharply with the survey definition. Current evidence points mainly to task-level, text and information work; secure integration, governance and measurement remain less developed."))
    story.append(Spacer(1, 7))
    story.append(metric_cards([
        ("39,860", "registered accounting SMEs", "VAT/PAYE enterprises in SIC 69.20, March 2025"),
        ("26%", "adopted AI", "Direct accounting-practice survey, April 2024"),
        ("54%", "piloting or adopted", "Same 2024 survey; do not compare as a trend"),
    ]))
    story += [Spacer(1, 9), P("The short answer", "H2R")]
    story.append(P("The strongest direct accounting-practice benchmark located reports 26% of practices as having adopted AI and 54% as piloting or having adopted it in April 2024. A later, self-selected AccountingWEB study reports 71.38% using external, non-embedded tools in 2026. These figures answer different questions and come from different samples; they are not a time series and must not be averaged."))
    story.append(P("The direct sources nevertheless agree on the form of current use. AI is used most visibly for tax or information research, drafting, summarisation, chatbots, document processing, repetitive-task automation, reporting and forecasting. The pattern is broader at the task level than at the operating-model level."))
    story += [P("What cannot be claimed", "H2R"), bullet("There is no identified official open estimate for the share of UK SIC 69.20 SMEs currently using AI."), bullet("The report does not claim that adoption improves productivity, accuracy, revenue or client outcomes."), bullet("Readiness is an organising framework, not a score or league table."), bullet("Broad SIC M official figures are contextual proxies, not accounting-SME estimates.")]
    story.append(Spacer(1, 6))
    story.append(P("Research boundary", "H2R"))
    story.append(P("This report is the current-state baseline. A later research series will assess benefits, effectiveness and which AI systems improve user businesses most. No surveys, interviews or other primary data collection are used here."))

    story += [PageBreak(), P("01  SECTOR AND EVIDENCE FRAME", "Kicker"), P("A large SME sector, but a fragmented evidence base", "H1R")]
    story.append(P("The target population is UK enterprises whose principal activity is SIC 2007 class 69.20: accounting, bookkeeping and auditing activities; tax consultancy. SMEs are defined here as enterprises with 0-249 employees. In-house finance teams in other industries are outside scope."))
    sector_rows = [
        ["0-4", "31,295", "Direct sector frame"], ["5-9", "4,995", "Direct sector frame"],
        ["10-19", "2,190", "Direct sector frame"], ["20-49", "945", "Direct sector frame"],
        ["50-99", "295", "Direct sector frame"], ["100-249", "140", "Direct sector frame"],
        ["SME total", "39,860", "Derived sum of published bands"], ["250+", "115", "Separate benchmark"],
    ]
    story.append(report_table(["Employment size", "Registered enterprises", "Evidence role"], sector_rows, [45*mm, 45*mm, 84*mm]))
    story.append(P("Source: ONS UK business: activity, size and location 2025, Table 4. Counts are control-rounded to base 5 and cover VAT and/or PAYE-registered enterprises. Unregistered sole practitioners are not captured." , "SmallR"))
    story += [Spacer(1, 6), P("Three evidence layers", "H2R")]
    story.append(report_table(["Layer", "What it contributes", "How it is used"], [
        ["Direct accounting surveys", "Practice adoption, tools, tasks, barriers and preparedness", "Directional sector evidence; sample limits remain visible"],
        ["Official SIC M survey", "Adoption, integration, policy and pathways with confidence intervals", "Context only; wider professional/scientific/technical sector and not SME-only"],
        ["Official economy-wide research", "Technology mix, oversight and barriers", "Context only; excludes the smallest firms or groups accounting into broad sectors"],
    ], [40*mm, 65*mm, 69*mm]))
    story.append(callout("Evidence decision: publish a triangulated current-state assessment. Do not manufacture a single accounting-SME prevalence estimate from incompatible sources.", colour=PALE, edge=TEAL))

    story += [PageBreak(), P("02  AI USE", "Kicker"), P("Adoption is visible - and definition-sensitive", "H1R")]
    story.append(P("Each percentage below retains its own population and meaning. Visual proximity does not imply comparability."))
    story.append(BarChart([
        ("Adopted AI - practices, 2024", 26, "direct"),
        ("Piloting or adopted - practices, 2024", 54, "direct"),
        ("External tool use - AWEB sample, 2026", 71.38, "direct"),
        ("Any listed AI use - broad SIC M, 2026", 50.586, "context"),
    ]))
    story.append(P("Blue bars are direct accounting evidence; the 2026 AccountingWEB bar is still directional because participation was self-selected and included members in practice and business. Teal is an official broad-sector contextual proxy. None is an official accounting-SME prevalence estimate.", "SmallR"))
    story += [P("Interpretation", "H2R"), bullet("The 2024 accounting-practice survey shows that AI adoption had passed the earliest experimental stage, while nearly half of practices were neither piloting nor adopted."), bullet("The 2026 AccountingWEB result shows widespread use of external tools among its respondents, but cannot be generalised to all UK accounting SMEs."), bullet("The official SIC M estimate, 50.6% reporting any listed use, confirms that AI is material across the surrounding professional-services environment. It does not isolate accounting or SMEs.")]
    story.append(callout("Conclusion for dimension 1: AI use is no longer niche, but a precise sector-wide adoption rate cannot be recovered from secondary evidence currently available."))

    story += [PageBreak(), P("03  INTEGRATION AND OPERATIONAL DEPTH", "Kicker"), P("Tool access is broader than verified workflow integration", "H1R")]
    story.append(metric_cards([
        ("71.38%", "external non-embedded tools", "AccountingWEB respondent sample, 2026"),
        ("66.18%", "believe AI is embedded", "Perception of core software, same sample"),
        ("19.9%", "system integration", "AI users in broad SIC M, official context"),
    ]))
    story += [Spacer(1, 8), P("What these measures mean", "H2R")]
    story.append(P("External tool use captures stand-alone access. Belief that core software contains AI captures perceived vendor embedding, not necessarily active or informed use. The UKBDS integration measure describes AI-using businesses in the much broader SIC M sector. These measures overlap conceptually but do not share a denominator."))
    story.append(report_table(["Signal", "Reading", "Limit"], [
        ["Stand-alone access", "General-purpose external tools are prominent", "Self-selected sample; does not establish organisational approval"],
        ["Vendor embedding", "AI may arrive through existing software", "Respondent belief is not verified feature use"],
        ["System integration", "Only one in five broad SIC M AI users report integration", "Contextual proxy; conditional denominator"],
        ["Integration preference", "37.56% prioritise natural integration", "Preference, not current implementation"],
    ], [40*mm, 66*mm, 68*mm]))
    story.append(callout("Conclusion for dimension 2: accounting AI is more established as a tool layer than as demonstrably integrated, recurring infrastructure."))

    story += [PageBreak(), P("04  GOVERNANCE AND HUMAN OVERSIGHT", "Kicker"), P("Security and skills are the clearest readiness constraints", "H1R")]
    story.append(metric_cards([
        ("16%", "well prepared for AI skills", "UK accounting practices, 2024"),
        ("63%", "skills concern", "Concern that skills restrict effective use, 2024"),
        ("61.95%", "data-security obstacle", "AccountingWEB respondent sample, 2026"),
    ]))
    story += [Spacer(1, 8), P("Governance prevalence", "H2R")]
    story.append(P("In the official UKBDS contextual proxy, 19.9% of AI-using SIC M businesses reported a formal or informal AI policy or guidance (95% confidence interval 12.6%-27.2%; rounded unweighted base 280). Policy presence does not demonstrate policy quality, client-data protection or compliance."))
    story.append(report_table(["Operational control", "Why it matters", "Evidence status"], [
        ["Approved tools and data rules", "Protect client confidentiality and limit uncontrolled uploads", "Guidance-supported; no representative accounting-SME prevalence"],
        ["Human review", "Maintains professional judgement and accountability", "Guidance-supported; no representative prevalence"],
        ["Staff capability", "Enables effective and critical use", "Direct survey signals a material gap"],
        ["Policy or guidance", "Sets expected use and escalation routes", "Official broad-sector proxy only"],
        ["Audit trail and monitoring", "Supports assurance and incident review", "Normative requirement; not measured sector-wide"],
    ], [42*mm, 74*mm, 58*mm]))
    story.append(P("FRC and ICAEW materials are used as normative context only. They explain responsible practice but do not show how common controls are." , "SmallR"))
    story.append(callout("Conclusion for dimension 3: governance cannot be inferred from adoption. Skills, security and proportionate oversight are separate operational capabilities."))

    story += [PageBreak(), P("05  USE CASES AND AI TYPES", "Kicker"), P("Text, information and document work lead current use", "H1R")]
    story.append(P("The two accounting surveys use different task lists. Percentages within each list may overlap because respondents could report more than one use."))
    story.append(BarChart([
        ("Tax legislation research - AWEB 2026", 59.45, "direct"),
        ("Drafting emails - AWEB 2026", 58.77, "direct"),
        ("Summarising financial data - AWEB 2026", 53.76, "direct"),
        ("Client communication chatbots - 2024", 51, "direct"),
        ("Repetitive-task automation - 2024", 34, "direct"),
        ("AI insights and reporting - 2024", 32, "direct"),
        ("Document processing - 2024", 30, "direct"),
        ("Forecasting and scenarios - 2024", 29, "direct"),
    ], height=245))
    story.append(P("Direct accounting evidence, shown in two separate source-defined groups. Do not rank across the 2024 and 2026 surveys as though they share a sample or questionnaire.", "SmallR"))
    story += [P("Technology pattern", "H2R"), P("The reported use cases are most consistent with generative language tools, natural-language processing, document intelligence and rules or automation embedded in applications. Official economy-wide DSIT research also finds text and language tools dominant among AI users, while agentic AI remains much less common. That official result is context, not an accounting estimate.")]
    story.append(callout("Conclusion for dimension 4: current use is predominantly assistive and task-level - research, drafting, summarisation, client communication and document handling - with automation, reporting and forecasting also visible."))

    story += [PageBreak(), P("06  ADOPTION PATHWAYS", "Kicker"), P("Buying and using tools dominate over building autonomous systems", "H1R")]
    story.append(P("The evidence indicates three main routes: staff using external general-purpose tools, vendors adding AI inside core accounting software, and practices adopting task-specific automation. In-house model development and automated decision-making remain uncommon in the closest official broad-sector context."))
    story.append(report_table(["Pathway", "Current evidence", "Assessment"], [
        ["External general-purpose tools", "71.38% in the self-selected AccountingWEB sample", "Prominent access route; organisational approval is unknown"],
        ["Vendor-embedded AI", "66.18% believe core software contains AI", "Important diffusion route; perceived presence is not verified use"],
        ["Task-specific applications", "Chatbots, document processing, automation, reporting and forecasting", "Visible in direct accounting survey evidence"],
        ["System integration", "19.9% among AI users in broad SIC M", "Limited official contextual signal"],
        ["Automated decision-making", "4.1% among AI users in broad SIC M", "Specialised; 95% CI 0.5%-7.7%"],
        ["Developing or training AI", "1.0% of all businesses in broad SIC M", "Rare contextual pathway; 95% CI 0%-2.3%"],
    ], [46*mm, 72*mm, 56*mm]))
    story += [Spacer(1, 7), P("Operational reading", "H2R"), bullet("Most visible adoption begins with accessible tools and existing software rather than bespoke AI development."), bullet("Embedded functionality may spread without users always recognising the boundary between conventional automation and AI."), bullet("Automated decisions are not representative of mainstream current use and require stronger assurance than assistive drafting or research."), bullet("No pathway is assumed to be superior; later research will test benefits and suitability by workflow.")]
    story.append(callout("Conclusion for dimension 5: accounting SMEs appear to adopt AI mainly by using external tools and vendor features, not by training models or delegating decisions autonomously."))

    story += [PageBreak(), P("07  CONCLUDING SYNTHESIS", "Kicker"), P("How ready is the sector?", "H1R")]
    story.append(callout("The sector is use-ready before it is fully operations-ready: access and task-level experimentation are widespread in the available surveys, while verified integration, governance and workforce capability are less mature and less consistently measured."))
    story += [Spacer(1, 8), P("1. How much AI use has started?", "H2R")]
    story.append(P("Enough to conclude that AI is no longer niche among accounting practices. The best direct benchmark reports 26% adopted and 54% piloting or adopted in April 2024. A 2026 self-selected profession sample reports 71.38% external-tool use. Because the definitions and samples differ, the report does not convert these into one sector rate or trend."))
    story += [P("2. What type of use dominates?", "H2R")]
    story.append(P("Assistive, language-heavy and document-oriented tasks: tax and information research, drafting, summarisation, client chatbots, document processing and reporting. Repetitive-task automation and forecasting are also visible. Bespoke development and automated decision-making are uncommon in official broad-sector context."))
    story += [P("3. What is the main readiness gap?", "H2R")]
    story.append(P("The move from individual tool use to governed, secure and integrated workflows. Direct surveys flag data security, skills and natural integration as leading issues. Official contextual evidence also shows that system integration and policy are much less common than broad AI use."))
    story += [P("4. What comes next?", "H2R")]
    story.append(P("A separate benefits and effectiveness programme should test where AI improves accounting practices and their client businesses, which workflows benefit, what controls are needed, and which systems offer the strongest fit. This report makes no impact claim in advance of that evidence."))
    story.append(P("Overall evidence confidence: moderate for the direction and type of current accounting use; low for a precise population prevalence estimate; insufficient for causal claims about business benefit.", "BodyBoldR"))

    story += [PageBreak(), P("08  METHODS AND COMPARABILITY", "Kicker"), P("Secondary data only, with denominator controls", "H1R")]
    story.append(P("Sources were selected for direct sector relevance, official status, openness, recency and methodological transparency. The study uses public or free-to-read secondary sources only. No survey, interview, web scraping of personal data or primary fieldwork was conducted."))
    story.append(report_table(["Grade", "Meaning", "Examples in this report"], [
        ["A - direct frame", "Matches the sector/population concept", "ONS SIC 69.20 enterprise counts"],
        ["B - direct directional", "Accounting-specific but not a representative SME estimate", "Sage/Demos/ACCA 2024; AccountingWEB/Sage 2026"],
        ["C - contextual proxy", "Official but broader sector or different size coverage", "UKBDS SIC M; DSIT AI Adoption Research"],
        ["D - prohibited", "Would mix definitions or imply unsupported causality", "Averaging adoption figures; ROI claims; readiness score"],
    ], [35*mm, 70*mm, 69*mm]))
    story += [Spacer(1, 7), P("Key controls", "H2R"), bullet("Fieldwork date and publication date are kept separate."), bullet("All-business and AI-user denominators are never combined."), bullet("Multiple-response percentages are never added."), bullet("Pilot, external-tool use, embedded AI, integration and transformation remain distinct concepts."), bullet("Confidence intervals and rounded bases are retained where supplied."), bullet("Guidance is used as normative context, never as adoption prevalence evidence.")]
    story += [P("Limitations", "H2R"), P("No official dataset isolates both SIC 69.20 and SME size for AI use. The 2024 direct survey includes large practices and does not publish raw microdata or the full questionnaire. The 2026 AccountingWEB sample is self-selected, mixes practice and business respondents and does not support population inference. ONS sector counts exclude unregistered enterprises. Official comparator surveys use broader sector groups and varying minimum business sizes.")]

    story += [PageBreak(), P("09  SOURCES", "Kicker"), P("Open and free-to-read evidence used", "H1R")]
    story.append(source_link(1, "ONS - UK business: activity, size and location 2025", ONS_URL))
    story.append(source_link(2, "DSIT - UK Business Data Survey 2026", UKBDS_URL))
    story.append(source_link(3, "DSIT - AI Adoption Research 2026", DSIT_URL))
    story.append(source_link(4, "Sage, Demos and ACCA - Going for Growth, 2024", SAGE_URL))
    story.append(source_link(5, "AccountingWEB and Sage - State of the nation: AI in accountancy and bookkeeping, 2026", AWEB_URL))
    story.append(source_link(6, "Financial Reporting Council - AI in Audit guidance", FRC_URL))
    story.append(source_link(7, "ICAEW - AI and accountants: rules and guidance", ICAEW_URL))
    story += [Spacer(1, 8), P("Reproducibility", "H2R"), P("The public research package includes the observation-level CSV, source register, dataset register, data dictionary, findings matrix, comparability matrix and the report-generation code. Local raw-source files are preserved with checksums but are not republished when copyright or distribution terms do not permit it.")]
    story.append(P("Citation", "H2R"))
    story.append(P(f"Moricz, B. ({REPORT_DATE[-4:]}). <i>UK Accounting SMEs: AI Adoption and Operational Readiness, 2026.</i> DAL Data & AI Lab."))
    story.append(callout("Publication note: this report describes the current state of adoption. It is not investment, legal, accounting or procurement advice.", colour=PALE, edge=TEAL))
    return story


def validate_public_data() -> None:
    if not PUBLIC_DATA.exists():
        raise FileNotFoundError(PUBLIC_DATA)
    with PUBLIC_DATA.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    if len(rows) < 20:
        raise ValueError("Public accounting evidence must contain at least 20 observations")
    if {row["evidence_role"] for row in rows} - {"direct_frame", "direct_directional", "contextual_proxy"}:
        raise ValueError("Unexpected evidence role")
    for row in rows:
        if not row["source_id"] or not row["indicator_id"] or not row["denominator_label"]:
            raise ValueError("Missing required evidence field")


def generate() -> Path:
    validate_public_data()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / PDF_NAME
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM, title="UK Accounting SMEs: AI Adoption and Operational Readiness, 2026", author=AUTHOR, subject="Secondary-data current-state research on AI adoption in UK accounting SMEs")
    doc.build(build_story(), onFirstPage=cover, onLaterPages=page_frame)
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = ["secondary evidence only", "26%", "71.38%", "39,860", "series", "no impact claim", "SIC 69.20"]
    missing = [item for item in required if item.lower() not in text.lower()]
    if missing:
        raise ValueError(f"Required report text missing: {missing}")
    metadata = {
        "title": "UK Accounting SMEs: AI Adoption and Operational Readiness, 2026",
        "publication_date": "2026-08-01",
        "author": AUTHOR,
        "research_mode": "secondary_data_only",
        "approval_status": "owner_authorised_final_publication",
        "publication_status": "approved_for_distribution",
        "evidence_boundary": "No official open estimate isolates AI adoption among UK SIC 69.20 SMEs; non-comparable sources remain separate.",
        "output": {"file": PDF_NAME, "sha256": sha256(path), "page_count": len(reader.pages)},
        "public_data": {"file": str(PUBLIC_DATA.relative_to(ROOT)), "sha256": sha256(PUBLIC_DATA)},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    print(generate())
