"""Generate the publication-quality five-report suite and cross-report synthesis."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from pypdf import PdfReader

from src.reporting.publication_design import draw_page_frame


ROOT = Path("/Users/henribergson/Desktop/SME-Intelligence-Lab")
OUTPUT = ROOT / "output/pdf"
ARCHIVE = OUTPUT / "archive/pre_final_20260729"
DATA = ROOT / "data/processed/uk_business_data_survey/2026-06-18/analysis"

SOURCE_URL = "https://www.gov.uk/government/statistics/uk-business-data-survey-2026"
TECHNICAL_URL = (
    "https://www.gov.uk/government/statistics/uk-business-data-survey-2026/"
    "uk-business-data-survey-2026-technical-report"
)
REPORT_DATE = "29 July 2026"
AUTHOR = "Benedek Moricz"
BRAND = "DAL Data & AI Lab"

PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 20 * mm
BOTTOM = 17 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

NAVY = colors.HexColor("#173E5B")
BLUE = colors.HexColor("#2D83C5")
SKY = colors.HexColor("#DDF2FF")
SKY_STRONG = colors.HexColor("#B9E3FA")
PALE = colors.HexColor("#EFF8FD")
ICE = colors.HexColor("#F8FCFE")
INK = colors.HexColor("#233E52")
MUTED = colors.HexColor("#60798B")
LINE_COLOUR = colors.HexColor("#C5DFEE")
TEAL = colors.HexColor("#138A8A")
GOLD = colors.HexColor("#F2C35B")
CORAL = colors.HexColor("#C95D4D")
WHITE = colors.white

SIZE_ORDER = ("micro", "small", "medium", "large")
SIZE_LABELS = {
    "micro": "Micro (1-9)",
    "small": "Small (10-49)",
    "medium": "Medium (50-249)",
    "large": "Large (250+) benchmark",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


AI_USE_PATH = DATA / "g5_01_ai_use_by_size/result.csv"
INTEGRATION_PATH = DATA / "g5_11_ai_integration_by_size/result.csv"
GOVERNANCE_PATH = DATA / "g5_19_ai_policy_by_size/result.csv"
USE_CASES_PATH = DATA / "g5_22_ai_use_cases_by_size/result.csv"
PATHWAYS_PATH = DATA / "g5_23_operational_ai_pathways/result.csv"

AI_USE = read_csv(AI_USE_PATH)
INTEGRATION = read_csv(INTEGRATION_PATH)
GOVERNANCE = read_csv(GOVERNANCE_PATH)
USE_CASES = read_csv(USE_CASES_PATH)
PATHWAYS = read_csv(PATHWAYS_PATH)


def value(row: dict[str, str], key: str = "estimate") -> float:
    return float(row[key])


def pct(row_or_value: dict[str, str] | float, decimals: int = 1) -> str:
    raw = value(row_or_value) if isinstance(row_or_value, dict) else row_or_value
    return f"{raw * 100:.{decimals}f}%"


def interval(row: dict[str, str]) -> str:
    return f"{float(row['lower_limit']) * 100:.1f}-{float(row['upper_limit']) * 100:.1f}%"


def by_size(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["business_size"]: row for row in rows}


def by_indicator(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["indicator_id"], {})[row["business_size"]] = row
    return grouped


AI = by_size(AI_USE)
INTEGRATION_BY_SIZE = by_size(INTEGRATION)
GOVERNANCE_BY_SIZE = by_size(GOVERNANCE)
USE_CASES_BY_INDICATOR = by_indicator(USE_CASES)
PATHWAYS_BY_INDICATOR = by_indicator(PATHWAYS)


def validate_inputs() -> None:
    for label, rows in (
        ("AI use", AI_USE),
        ("integration", INTEGRATION),
        ("governance", GOVERNANCE),
    ):
        if len(rows) != 4 or tuple(row["business_size"] for row in rows) != SIZE_ORDER:
            raise ValueError(f"{label} rows changed")
    if len(USE_CASES) != 28 or len(USE_CASES_BY_INDICATOR) != 7:
        raise ValueError("Use-case evidence must contain 28 rows across seven indicators")
    if len(PATHWAYS) != 16 or len(PATHWAYS_BY_INDICATOR) != 4:
        raise ValueError("Pathway evidence must contain 16 rows across four indicators")
    for rows in (AI_USE, INTEGRATION, GOVERNANCE, USE_CASES, PATHWAYS):
        for row in rows:
            estimate = float(row["estimate"])
            lower = float(row["lower_limit"])
            upper = float(row["upper_limit"])
            if not 0 <= lower <= estimate <= upper <= 1:
                raise ValueError("Invalid estimate or confidence interval")
            if int(float(row["sample_base"])) <= 0:
                raise ValueError("Invalid respondent base")
    if {row["denominator_id"] for row in AI_USE} != {"all_uk_businesses"}:
        raise ValueError("Report 01 denominator changed")
    if {row["denominator_id"] for row in INTEGRATION} != {
        "uk_businesses_using_ai_technologies"
    }:
        raise ValueError("Report 02 denominator changed")
    if {row["denominator_id"] for row in GOVERNANCE} != {
        "uk_businesses_using_ai_technologies"
    }:
        raise ValueError("Report 03 denominator changed")
    if {row["denominator_id"] for row in USE_CASES} != {"all_uk_businesses"}:
        raise ValueError("Report 04 denominator changed")
    pathway_denominators = {
        indicator: {row["denominator_id"] for row in sizes.values()}
        for indicator, sizes in PATHWAYS_BY_INDICATOR.items()
    }
    expected = {
        "system_integration": {"uk_businesses_using_ai_technologies"},
        "automated_decision_making": {"uk_businesses_using_ai_technologies"},
        "ai_policy_guidance": {"uk_businesses_using_ai_technologies"},
        "ai_development_training": {"all_uk_businesses"},
    }
    if pathway_denominators != expected:
        raise ValueError("Report 05 denominator mapping changed")


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverKicker",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        tracking=1.1,
        textColor=colors.HexColor("#71DCFF"),
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#A9C0CE"),
        alignment=TA_LEFT,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=SKY,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverHeadline",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=29,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=11,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        tracking=1,
        textColor=colors.HexColor("#6EE7C2"),
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.2,
        textColor=colors.HexColor("#DDF2FF"),
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.8,
        leading=9,
        textColor=colors.HexColor("#A9C0CE"),
    )
)
styles.add(
    ParagraphStyle(
        name="H1R",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=NAVY,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="H2R",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=BLUE,
        spaceBefore=5,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyR",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=INK,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyBoldR",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=INK,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallR",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.4,
        leading=10.4,
        textColor=MUTED,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletR",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.5,
        textColor=INK,
        leftIndent=11,
        firstLineIndent=-8,
        spaceAfter=3.5,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeadR",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.3,
        textColor=WHITE,
    )
)
styles.add(
    ParagraphStyle(
        name="TableBodyR",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.1,
        leading=9.4,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        name="TableBodyBoldR",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.1,
        leading=9.4,
        textColor=NAVY,
    )
)
styles.add(
    ParagraphStyle(
        name="MetricR",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=21,
        textColor=BLUE,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="MetricLabelR",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=NAVY,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="CalloutR",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=15,
        textColor=NAVY,
        spaceAfter=0,
    )
)


def P(text: str, style: str = "BodyR") -> Paragraph:
    return Paragraph(text, styles[style])


def bullet(text: str) -> Paragraph:
    return P(f"- {text}", "BulletR")


def report_table(
    headers: list[str],
    rows: list[list[str]],
    widths: list[float] | None = None,
    *,
    font_size: float = 7.1,
) -> Table:
    header_style = styles["TableHeadR"]
    body_style = styles["TableBodyR"]
    bold_style = styles["TableBodyBoldR"]
    body_style.fontSize = font_size
    body_style.leading = font_size + 2.2
    data = [[P(item, "TableHeadR") for item in headers]]
    for row in rows:
        data.append(
            [
                P(item, "TableBodyBoldR" if index == 0 else "TableBodyR")
                for index, item in enumerate(row)
            ]
        )
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    styling = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE_COLOUR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]
    for index in range(1, len(data)):
        if index % 2 == 0:
            styling.append(("BACKGROUND", (0, index), (-1, index), PALE))
    table.setStyle(TableStyle(styling))
    return table


def callout(text: str, *, colour: colors.Color = SKY, edge: colors.Color = BLUE) -> Table:
    table = Table([[P(text, "CalloutR")]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colour),
                ("LINEBEFORE", (0, 0), (0, -1), 4, edge),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def metric_cards(items: list[tuple[str, str, str]]) -> Table:
    width = CONTENT_W / len(items)
    cells = []
    for value_text, label, note in items:
        cells.append(
            [
                P(value_text, "MetricR"),
                P(label, "MetricLabelR"),
                P(note, "SmallR"),
            ]
        )
    table = Table([cells], colWidths=[width] * len(items))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE_COLOUR),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_COLOUR),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def insight_cards(items: list[tuple[str, str]], columns: int = 2) -> Table:
    rows = []
    for index in range(0, len(items), columns):
        cells = []
        for title, body in items[index : index + columns]:
            cells.append(
                P(
                    f'<font color="#2D83C5"><b>{title}</b></font><br/>{body}',
                    "BodyR",
                )
            )
        while len(cells) < columns:
            cells.append("")
        rows.append(cells)
    width = CONTENT_W / columns
    table = Table(rows, colWidths=[width] * columns)
    styling = [
        ("BACKGROUND", (0, 0), (-1, -1), ICE),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE_COLOUR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]
    table.setStyle(TableStyle(styling))
    return table


class CIChart(Flowable):
    def __init__(
        self,
        rows: list[dict[str, str]],
        *,
        width: float = CONTENT_W,
        height: float = 250,
        max_value: float = 1.0,
    ):
        super().__init__()
        self.rows = rows
        self.width = width
        self.height = height
        self.max_value = max_value

    def draw(self) -> None:
        chart = Drawing(self.width, self.height)
        label_width = 122
        right_pad = 45
        plot_x = label_width
        plot_w = self.width - label_width - right_pad
        top = self.height - 34
        row_gap = (self.height - 68) / len(self.rows)
        for tick in range(0, 101, 25):
            x = plot_x + plot_w * (tick / 100) / self.max_value
            chart.add(Line(x, 18, x, self.height - 20, strokeColor=LINE_COLOUR, strokeWidth=0.6))
            chart.add(String(x, self.height - 12, f"{tick}%", fontName="Helvetica", fontSize=7, fillColor=MUTED, textAnchor="middle"))
        for index, row in enumerate(self.rows):
            y = top - index * row_gap
            size = row["business_size"]
            benchmark = size == "large"
            colour = TEAL if benchmark else BLUE
            chart.add(String(0, y - 3, SIZE_LABELS[size], fontName="Helvetica-Bold" if benchmark else "Helvetica", fontSize=8, fillColor=INK))
            lower = float(row["lower_limit"]) / self.max_value
            estimate = float(row["estimate"]) / self.max_value
            upper = float(row["upper_limit"]) / self.max_value
            chart.add(Line(plot_x + plot_w * lower, y, plot_x + plot_w * upper, y, strokeColor=colour, strokeWidth=2.2))
            chart.add(Line(plot_x + plot_w * lower, y - 4, plot_x + plot_w * lower, y + 4, strokeColor=colour, strokeWidth=1.2))
            chart.add(Line(plot_x + plot_w * upper, y - 4, plot_x + plot_w * upper, y + 4, strokeColor=colour, strokeWidth=1.2))
            chart.add(Circle(plot_x + plot_w * estimate, y, 4, fillColor=colour, strokeColor=WHITE, strokeWidth=0.7))
            chart.add(String(self.width - 2, y - 3, pct(row), fontName="Helvetica-Bold", fontSize=8, fillColor=colour, textAnchor="end"))
        chart.drawOn(self.canv, 0, 0)


class GroupedBarChart(Flowable):
    def __init__(
        self,
        groups: list[tuple[str, list[tuple[str, float, bool]]]],
        *,
        max_percent: float,
        colour_map: dict[str, colors.Color],
        legend: list[tuple[str, str]],
        show_values: bool,
        width: float = CONTENT_W,
        height: float = 330,
    ):
        super().__init__()
        self.groups = groups
        self.max_percent = max_percent
        self.colour_map = colour_map
        self.legend = legend
        self.show_values = show_values
        self.width = width
        self.height = height

    def draw(self) -> None:
        chart = Drawing(self.width, self.height)
        label_width = 112
        plot_x = label_width
        right_pad = 34 if self.show_values else 8
        plot_w = self.width - label_width - right_pad
        legend_y = self.height - 15
        legend_x = plot_x
        for key, label in self.legend:
            colour = self.colour_map[key]
            chart.add(Rect(legend_x, legend_y - 4, 8, 8, fillColor=colour, strokeColor=None))
            chart.add(String(legend_x + 12, legend_y - 2, label, fontName="Helvetica", fontSize=6.5, fillColor=INK))
            legend_x += max(78, len(label) * 4.7 + 26)
        top = self.height - 54
        group_gap = (self.height - 82) / len(self.groups)
        for tick in range(0, int(self.max_percent) + 1, 10):
            x = plot_x + plot_w * tick / self.max_percent
            chart.add(Line(x, 18, x, self.height - 40, strokeColor=LINE_COLOUR, strokeWidth=0.5))
            chart.add(String(x, self.height - 34, f"{tick}%", fontName="Helvetica", fontSize=6.7, fillColor=MUTED, textAnchor="middle"))
        for group_index, (label, bars) in enumerate(self.groups):
            centre_y = top - group_index * group_gap
            chart.add(String(0, centre_y - 2, label, fontName="Helvetica-Bold", fontSize=7.5, fillColor=INK))
            bar_h = min(7.5, group_gap / max(len(bars), 1) - 2)
            start_y = centre_y + ((len(bars) - 1) * (bar_h + 2)) / 2
            for bar_index, (bar_label, percent, benchmark) in enumerate(bars):
                y = start_y - bar_index * (bar_h + 2)
                colour = self.colour_map[bar_label]
                chart.add(Rect(plot_x, y - bar_h / 2, plot_w * percent / self.max_percent, bar_h, fillColor=colour, strokeColor=None))
                if self.show_values:
                    chart.add(String(self.width - 1, y - 2.6, f"{percent:.1f}%", fontName="Helvetica-Bold", fontSize=6.4, fillColor=colour, textAnchor="end"))
        chart.drawOn(self.canv, 0, 0)


def page_decor(report_number: str, short_title: str):
    def draw(canvas, doc) -> None:
        canvas.saveState()
        page = canvas.getPageNumber()
        if page == 1:
            canvas.setFillColor(colors.HexColor("#06131D"))
            canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#081C29"))
            canvas.rect(0, 0, PAGE_W * .72, PAGE_H, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#0B2637"))
            canvas.circle(PAGE_W - 22 * mm, 51 * mm, 53 * mm, fill=1, stroke=0)
            for radius, colour in ((44, "#174152"), (34, "#22616B"), (23, "#2D7B78"), (13, "#6EE7C2")):
                canvas.setStrokeColor(colors.HexColor(colour))
                canvas.setLineWidth(.7)
                canvas.circle(PAGE_W - 22 * mm, 51 * mm, radius * mm, fill=0, stroke=1)
            canvas.setFillColor(colors.HexColor("#6EE7C2"))
            canvas.circle(PAGE_W - 33 * mm, 61 * mm, 2 * mm, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#71DCFF"))
            canvas.circle(PAGE_W - 67 * mm, 35 * mm, 1.4 * mm, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#6EE7C2"))
            canvas.rect(0, 0, 3 * mm, PAGE_H, fill=1, stroke=0)
            canvas.setStrokeColor(colors.HexColor("#174052"))
            canvas.line(LEFT, PAGE_H - 28 * mm, PAGE_W - RIGHT, PAGE_H - 28 * mm)
        else:
            draw_page_frame(canvas, doc, page_w=PAGE_W, page_h=PAGE_H, left=LEFT, right=RIGHT, brand=BRAND, short_title=f"Report {report_number} / {short_title}", footer_note="DSIT UK Business Data Survey 2026 | Owner-reviewed research")
        canvas.restoreState()
    return draw


def cover(
    report_number: str,
    title: str,
    subtitle: str,
    evidence_scope: str,
    takeaway: str,
) -> list:
    return [
        Spacer(1, 29 * mm),
        P(f"REPORT {report_number} / UK SME AI ADOPTION INTELLIGENCE", "CoverKicker"),
        P(title, "CoverTitle"),
        P(takeaway, "CoverHeadline"),
        P(subtitle, "CoverSub"),
        Spacer(1, 5 * mm),
        P("EVIDENCE SCOPE", "CoverLabel"),
        P(evidence_scope, "CoverBody"),
        Spacer(1, 7 * mm),
        metric_cards(
            [
                ("UKBDS", "Official source", "DSIT 2026"),
                ("95%", "Uncertainty", "Intervals retained"),
                ("SMEs", "Primary scope", "Large shown separately"),
            ]
        ),
        Spacer(1, 8 * mm),
        P(f"{BRAND} | {AUTHOR} | {REPORT_DATE}", "CoverMeta"),
        PageBreak(),
    ]


def section(title: str, intro: str | None = None) -> list:
    items = [
        P(title, "H1R"),
        HRFlowable(width="100%", thickness=1.2, color=BLUE),
        Spacer(1, 5),
    ]
    if intro:
        items.append(P(intro, "BodyR"))
    return items


def methods_page(
    *,
    table_ids: str,
    denominator_text: str,
    special_limits: list[str] | None = None,
) -> list:
    items = section(
        "Method, interpretation and source trail",
        "These reports retain the survey definitions rather than treating every percentage as directly comparable.",
    )
    items.extend(
        [
            P("Source and fieldwork", "H2R"),
            P(
                "Department for Science, Innovation and Technology, UK Business Data Survey 2026. "
                "Fieldwork ran from 10 October 2025 to 28 January 2026. "
                f"Source tables used: {table_ids}.",
                "BodyR",
            ),
            P("Denominator", "H2R"),
            P(denominator_text, "BodyR"),
            P("Uncertainty and bases", "H2R"),
            P(
                "The official central estimates and supplied 95% confidence intervals are shown. "
                "Unweighted sample bases are rounded respondent counts, not counts of UK businesses. "
                "The medium and large groups generally have wider intervals because their bases are smaller.",
                "BodyR",
            ),
            P("Interpretation limits", "H2R"),
        ]
    )
    limits = [
        "The findings are descriptive. They do not establish causation or business impact.",
        "The published package does not provide the covariance, replicate weights, raw microdata or official pairwise method needed for a fully defensible size-group significance test.",
        "Large businesses are a separate benchmark and are not part of the primary SME result.",
    ]
    if special_limits:
        limits.extend(special_limits)
    items.extend(bullet(item) for item in limits)
    items.extend(
        [
            P("Official material", "H2R"),
            P(
                f'<link href="{SOURCE_URL}" color="#2D83C5">UK Business Data Survey 2026 publication</link><br/>'
                f'<link href="{TECHNICAL_URL}" color="#2D83C5">UK Business Data Survey 2026 technical report</link>',
                "BodyR",
            ),
            callout(
                "Use this evidence as a disciplined starting point for questions and prioritisation - not as a substitute for organisation-specific assessment.",
                colour=PALE,
                edge=TEAL,
            ),
        ]
    )
    return items


def exact_rows(rows: list[dict[str, str]]) -> list[list[str]]:
    return [
        [
            SIZE_LABELS[row["business_size"]],
            pct(row),
            interval(row),
            f"{int(float(row['sample_base'])):,}",
        ]
        for row in rows
    ]


def build_report(
    path: Path,
    report_number: str,
    title: str,
    story: list,
    *,
    metadata: dict,
) -> None:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title=title,
        author=AUTHOR,
        subject="UK SME AI adoption intelligence",
    )
    doc.build(
        story,
        onFirstPage=page_decor(report_number, title),
        onLaterPages=page_decor(report_number, title),
    )
    reader = PdfReader(str(path))
    payload = {
        "report_id": metadata["report_id"],
        "title": title,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "author": AUTHOR,
        "decision_id": "D-022",
        "approval_status": "owner_authorised_final_publication",
        "publication_status": "approved_for_distribution",
        "source_release": "UK Business Data Survey 2026 / 2026-06-18",
        "source_url": SOURCE_URL,
        "technical_report_url": TECHNICAL_URL,
        "finding_ids": metadata.get("finding_ids", []),
        "input_files": [
            {"path": str(source), "sha256": sha256_file(source)}
            for source in metadata.get("input_files", [])
        ],
        "output": {
            "path": str(path),
            "sha256": sha256_file(path),
            "page_count": len(reader.pages),
        },
        "evidence_rules": {
            "confidence_intervals_retained": True,
            "large_businesses_separate_benchmark": True,
            "causal_claim_present": False,
            "formal_significance_claim_present": False,
            "cross_denominator_arithmetic_present": False,
        },
        "visual_qa": {"status": "pending", "rendered_pages": []},
    }
    path.with_suffix(".metadata.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def report_01() -> tuple[Path, dict]:
    path = OUTPUT / "SME_Report_01_AI_Use_by_Business_Size.pdf"
    story = cover(
        "01",
        "Reported AI use by business size",
        "A clear baseline for how widely UK businesses report using AI-based technologies.",
        "Table 42 describes all UK businesses within each published size group. "
        "Micro, small and medium businesses are the primary scope; large businesses are a reference benchmark.",
        "Reported AI-use point estimates rise from 37.4% for micro businesses to 50.8% for small and 57.1% for medium businesses.",
    )
    story.extend(section("Executive summary"))
    story.extend(
        [
            metric_cards(
                [
                    (pct(AI["micro"]), "Micro", interval(AI["micro"])),
                    (pct(AI["small"]), "Small", interval(AI["small"])),
                    (pct(AI["medium"]), "Medium", interval(AI["medium"])),
                    (pct(AI["large"]), "Large*", interval(AI["large"])),
                ]
            ),
            Spacer(1, 9),
            P(
                "The point estimates show a consistent size gradient across the published categories. "
                "This is useful for market segmentation and service design because a single 'SME adoption rate' would conceal material differences between micro, small and medium businesses.",
                "BodyBoldR",
            ),
            P("What the evidence supports", "H2R"),
            insight_cards(
                [
                    ("Size matters for the baseline", "Micro businesses have the lowest point estimate among the three SME groups; medium businesses have the highest."),
                    ("The benchmark is distinct", "The 78.2% large-business estimate provides context, but large businesses are not included in the core SME finding."),
                    ("Uncertainty remains visible", "Intervals widen for medium and large groups, reflecting smaller rounded respondent bases."),
                    ("The result is about reported use", "It does not show frequency, effectiveness, depth of integration or return on investment."),
                ]
            ),
            Spacer(1, 9),
            callout(
                "Business implication: compare organisations with the most relevant size group before discussing sector, use case or implementation depth.",
                colour=SKY,
                edge=TEAL,
            ),
            PageBreak(),
        ]
    )
    story.extend(section("Evidence by business size", "Point estimates with supplied 95% confidence intervals."))
    story.extend(
        [
            CIChart(AI_USE, height=245),
            Spacer(1, 6),
            report_table(
                ["Business size", "Estimate", "95% interval", "Rounded base"],
                exact_rows(AI_USE),
                [62 * mm, 30 * mm, 42 * mm, 38 * mm],
            ),
            Spacer(1, 7),
            P(
                "* Large businesses are shown as a separately labelled reference benchmark. "
                "Rounded bases are respondents, not counts of UK businesses.",
                "SmallR",
            ),
            PageBreak(),
        ]
    )
    story.extend(section("Decision use: a baseline, not a diagnosis"))
    story.extend(
        [
            P(
                "The survey result is most useful as a starting point for better questions. "
                "It does not diagnose an individual firm or prescribe a technology purchase.",
                "BodyR",
            ),
            insight_cards(
                [
                    ("For micro businesses", "Which low-complexity, repeatable tasks could justify experimentation without creating unnecessary data or governance risk?"),
                    ("For small businesses", "Which successful experiments are ready to move into recurring workflows, with clear ownership and human review?"),
                    ("For medium businesses", "Where should integration, governance and workforce capability be strengthened as use becomes more widespread?"),
                    ("For advisers and policymakers", "Do support offers distinguish between basic use, system integration and organisational governance rather than treating adoption as binary?"),
                ]
            ),
            Spacer(1, 10),
            P("Recommended next cuts", "H2R"),
            bullet("Repeat the baseline by the source's published sector categories where sample bases and suppression permit."),
            bullet("Separate experimentation, recurring workflow use and system integration."),
            bullet("Pair the adoption baseline with use-case, governance and operational pathway evidence."),
            bullet("Avoid converting the percentage into an estimate of business counts without an appropriate population denominator and survey design treatment."),
            Spacer(1, 8),
            callout(
                "Useful insight: the size gradient is a segmentation signal. It is not proof that size causes adoption or that every difference is statistically significant.",
                colour=PALE,
                edge=BLUE,
            ),
            PageBreak(),
        ]
    )
    story.extend(
        methods_page(
            table_ids="Table 42",
            denominator_text="All UK businesses within each published business-size category.",
            special_limits=[
                "The measure records use of any listed AI-based technology; it does not distinguish occasional experimentation from embedded operational use."
            ],
        )
    )
    metadata = {"report_id": "report_01_ai_use_by_size", "finding_ids": ["F-001"], "input_files": [AI_USE_PATH]}
    return path, {"story": story, "metadata": metadata}


def report_02() -> tuple[Path, dict]:
    path = OUTPUT / "SME_Report_02_AI_Adoption_and_System_Integration_by_Size.pdf"
    story = cover(
        "02",
        "AI adoption and system integration",
        "Two related but distinct views: how widely AI is used, and how deeply it is connected to business systems.",
        "Table 42 describes all businesses. Table 48 describes only businesses that already report using AI. "
        "The two percentages are never subtracted, divided or converted into a funnel.",
        "AI use is broader than system integration: among AI-using SMEs, only 26.9%-31.5% report at least one AI tool integrated with business systems.",
    )
    story.extend(section("Executive summary"))
    story.extend(
        [
            metric_cards(
                [
                    ("37.4%-57.1%", "Reported AI use", "All SME size groups"),
                    ("26.9%-31.5%", "System integration", "Among AI-using SMEs"),
                    ("2 populations", "Comparison rule", "Never combine"),
                ]
            ),
            Spacer(1, 9),
            P(
                "The evidence separates reach from operational embedding. "
                "Reported AI use rises across SME size groups, while the integration estimates for micro, small and medium AI users are clustered around three in ten.",
                "BodyBoldR",
            ),
            insight_cards(
                [
                    ("Reach is uneven", "The all-business adoption baseline ranges from 37.4% for micro to 57.1% for medium businesses."),
                    ("Integration is not universal", "Among businesses already using AI, the SME integration point estimates range from 26.9% to 31.5%."),
                    ("The denominator changes", "Integration percentages cannot be read as shares of all businesses or compared arithmetically with adoption percentages."),
                    ("Large is a benchmark", "The large-business integration point estimate is higher, but this report makes no formal significance claim."),
                ]
            ),
            Spacer(1, 10),
            callout("A business can report AI use without having AI integrated into its systems. The survey therefore supports a reach-versus-depth distinction.", colour=SKY, edge=TEAL),
            PageBreak(),
        ]
    )
    story.extend(section("Reach: reported AI use among all businesses"))
    story.extend(
        [
            P("<b>Denominator:</b> all UK businesses within each published size group.", "BodyR"),
            CIChart(AI_USE, height=245),
            report_table(["Business size", "Estimate", "95% interval", "Rounded base"], exact_rows(AI_USE), [62*mm, 30*mm, 42*mm, 38*mm]),
            Spacer(1, 7),
            P("The point estimates rise across the three SME groups. This measure does not show whether use is occasional, recurring or integrated.", "SmallR"),
            PageBreak(),
        ]
    )
    story.extend(section("Depth: system integration among AI users"))
    story.extend(
        [
            P("<b>Denominator:</b> UK businesses that report using AI technologies.", "BodyR"),
            CIChart(INTEGRATION, height=245),
            report_table(["Business size", "Estimate", "95% interval", "Rounded base"], exact_rows(INTEGRATION), [62*mm, 30*mm, 42*mm, 38*mm]),
            Spacer(1, 7),
            P("These figures are conditional on already using AI. They are not percentages of all UK businesses.", "SmallR"),
            PageBreak(),
        ]
    )
    story.extend(section("Business interpretation: move from access to operating model"))
    story.extend(
        [
            P(
                "The report does not estimate a conversion rate from use to integration. "
                "It does, however, show why adoption conversations should distinguish tool access from recurring, connected workflows.",
                "BodyR",
            ),
            insight_cards(
                [
                    ("Use", "Which tasks are being supported, by whom, and how frequently?"),
                    ("Integration", "Which systems, data flows and controls connect the AI tool to normal operations?"),
                    ("Ownership", "Who is accountable for outputs, exceptions, data handling and human review?"),
                    ("Value evidence", "What outcome is monitored, and what would count as evidence that integration is useful?"),
                ]
            ),
            Spacer(1, 10),
            P("Cross-measure insight", "H2R"),
            bullet("The adoption baseline is size-sensitive, but integration among SME AI users is comparatively clustered in the published point estimates."),
            bullet("This pattern is consistent with a distinction between access to AI tools and deeper operational embedding."),
            bullet("The survey does not explain the causes of integration or identify the specific systems involved."),
            bullet("Sector, workflow and organisational capability should be tested before assuming the same pathway applies to every SME."),
            Spacer(1, 9),
            callout("Practical hypothesis for later research: barriers to initial use may differ from barriers to system integration.", colour=PALE, edge=BLUE),
            PageBreak(),
        ]
    )
    story.extend(
        methods_page(
            table_ids="Tables 42 and 48",
            denominator_text="Table 42 covers all UK businesses. Table 48 covers only UK businesses that report using AI technologies. The two populations remain separate.",
            special_limits=[
                "The report does not calculate an adoption-to-integration conversion rate.",
                "The source does not identify the systems, frequency, quality or effectiveness of integration.",
            ],
        )
    )
    metadata = {"report_id": "report_02_ai_adoption_integration", "finding_ids": ["F-001", "F-002"], "input_files": [AI_USE_PATH, INTEGRATION_PATH]}
    return path, {"story": story, "metadata": metadata}


def report_03() -> tuple[Path, dict]:
    path = OUTPUT / "SME_Report_03_AI_Governance_by_Business_Size.pdf"
    story = cover(
        "03",
        "AI governance among AI-using businesses",
        "How commonly businesses report formal or informal AI policy or guidance.",
        "Table 50 describes businesses that already report using AI technologies. "
        "The measure is a net for formal or informal policy or guidance; it does not assess quality or effectiveness.",
        "Policy or guidance point estimates rise from 20.1% for micro AI users to 29.0% for small and 36.8% for medium AI users.",
    )
    story.extend(section("Executive summary"))
    story.extend(
        [
            metric_cards(
                [
                    (pct(GOVERNANCE_BY_SIZE["micro"]), "Micro AI users", interval(GOVERNANCE_BY_SIZE["micro"])),
                    (pct(GOVERNANCE_BY_SIZE["small"]), "Small AI users", interval(GOVERNANCE_BY_SIZE["small"])),
                    (pct(GOVERNANCE_BY_SIZE["medium"]), "Medium AI users", interval(GOVERNANCE_BY_SIZE["medium"])),
                    (pct(GOVERNANCE_BY_SIZE["large"]), "Large benchmark", interval(GOVERNANCE_BY_SIZE["large"])),
                ]
            ),
            Spacer(1, 9),
            P(
                "The published point estimates increase with business size. "
                "Even so, the survey measure only shows whether any formal or informal policy or guidance is reported - not whether it is complete, used or effective.",
                "BodyBoldR",
            ),
            insight_cards(
                [
                    ("Formalisation differs by size", "The micro-business point estimate is the lowest and the medium-business point estimate the highest among SMEs."),
                    ("Many AI users report no policy/guidance", "The reported net remains below 40% for each of the three SME groups."),
                    ("Presence is not quality", "The source does not evaluate coverage, enforcement, staff awareness or outcomes."),
                    ("Governance should fit the business", "A proportionate approach can start with clear responsibilities and decision rules rather than a large policy manual."),
                ]
            ),
            Spacer(1, 10),
            callout("Governance is an operating discipline, not a document count. The survey supplies a baseline for asking better questions.", colour=SKY, edge=TEAL),
            PageBreak(),
        ]
    )
    story.extend(section("Evidence by business size", "Point estimates among businesses already using AI, with supplied 95% confidence intervals."))
    story.extend(
        [
            CIChart(GOVERNANCE, height=245),
            report_table(["Business size", "Estimate", "95% interval", "Rounded base"], exact_rows(GOVERNANCE), [62*mm, 30*mm, 42*mm, 38*mm]),
            Spacer(1, 7),
            P("These are conditional estimates for AI-using businesses, not percentages of all UK businesses.", "SmallR"),
            PageBreak(),
        ]
    )
    story.extend(section("Decision use: six proportionate governance questions"))
    story.extend(
        [
            P("The following are practical discussion prompts, not additional survey findings.", "BodyR"),
            insight_cards(
                [
                    ("1. Ownership", "Who is accountable for permitted uses, exceptions and unresolved risks?"),
                    ("2. Data", "What information may or may not be entered into AI tools, and why?"),
                    ("3. Human review", "Which outputs require checking before they influence customers, staff or financial decisions?"),
                    ("4. Transparency", "When should colleagues or customers be told that AI supported a process or output?"),
                    ("5. Incidents", "How should errors, unsafe outputs, data leakage or vendor changes be reported and handled?"),
                    ("6. Monitoring", "Which uses, outcomes and complaints should be reviewed periodically?"),
                ]
            ),
            Spacer(1, 10),
            P("Useful interpretation", "H2R"),
            bullet("The increasing size pattern is a reason to segment governance support, not evidence that larger firms have better governance."),
            bullet("Policy presence and system integration should be reviewed together, because connected workflows can increase operational consequences."),
            bullet("A short, role-specific set of rules may be more usable for a small business than a generic enterprise policy."),
            bullet("Later research should test sector regulation, data sensitivity, customer impact and workforce practices."),
            PageBreak(),
        ]
    )
    story.extend(
        methods_page(
            table_ids="Table 50",
            denominator_text="UK businesses within each published business-size category that report using AI technologies.",
            special_limits=[
                "The net combines formal and informal policy or guidance.",
                "The measure does not assess governance quality, completeness, enforcement or effectiveness.",
            ],
        )
    )
    metadata = {"report_id": "report_03_ai_governance", "finding_ids": ["F-003"], "input_files": [GOVERNANCE_PATH]}
    return path, {"story": story, "metadata": metadata}


USE_CASE_LABELS = {
    "research_information": "Research",
    "summarise_or_draft": "Summarise/draft",
    "generate_images_or_videos": "Images/videos",
    "analyse_data_or_models": "Data analysis/models",
    "draft_computer_code": "Computer code",
    "cybersecurity_protection": "Cybersecurity",
    "customer_service_chatbots": "Customer chatbots",
}
USE_CASE_ORDER = (
    "research_information",
    "summarise_or_draft",
    "generate_images_or_videos",
    "analyse_data_or_models",
    "draft_computer_code",
    "cybersecurity_protection",
    "customer_service_chatbots",
)


def report_04() -> tuple[Path, dict]:
    path = OUTPUT / "SME_Report_04_How_UK_Businesses_Use_AI.pdf"
    story = cover(
        "04",
        "How UK businesses use AI",
        "Seven published use cases reveal where reported activity is concentrated.",
        "Table 42 describes all UK businesses. Businesses could select more than one use case, so categories overlap and must not be added together.",
        "Research is the highest listed use-case point estimate in every size group. Summarising or drafting is also prominent, especially for medium and large businesses.",
    )
    story.extend(section("Executive summary"))
    story.extend(
        [
            metric_cards(
                [
                    ("#1", "Research", "Highest listed use case"),
                    ("#2", "Summarise/draft", "Close second"),
                    ("7", "Published categories", "Multiple response"),
                ]
            ),
            Spacer(1, 9),
            P(
                "The leading reported purposes are information-oriented: researching information and summarising or drafting. "
                "Specialised uses such as coding, cybersecurity and customer chatbots have lower point estimates, particularly among micro and small businesses.",
                "BodyBoldR",
            ),
            insight_cards(
                [
                    ("Information work leads", "Research is highest across all four size groups; summarising/drafting is also consistently prominent."),
                    ("Technical use is narrower", "Data analysis, coding and cybersecurity have lower point estimates than the two leading information tasks."),
                    ("Size differences recur", "The large-business benchmark is higher across all seven listed categories."),
                    ("The categories overlap", "A business may report several purposes, so the percentages describe incidence, not a portfolio that sums to 100%."),
                ]
            ),
            Spacer(1, 10),
            callout("Useful insight: current reported use appears weighted toward information and content tasks rather than highly embedded technical applications.", colour=SKY, edge=TEAL),
            PageBreak(),
        ]
    )
    groups = []
    for indicator in USE_CASE_ORDER:
        sizes = USE_CASES_BY_INDICATOR[indicator]
        bars = [(size, float(sizes[size]["estimate"]) * 100, size == "large") for size in SIZE_ORDER]
        groups.append((USE_CASE_LABELS[indicator], bars))
    story.extend(section("Use-case profile by business size", "Point estimates across seven multiple-response categories."))
    story.extend(
        [
            GroupedBarChart(
                groups,
                max_percent=60,
                colour_map={"micro": BLUE, "small": TEAL, "medium": NAVY, "large": CORAL},
                legend=[
                    ("micro", "Micro"),
                    ("small", "Small"),
                    ("medium", "Medium"),
                    ("large", "Large benchmark"),
                ],
                show_values=False,
                height=360,
            ),
            Spacer(1, 6),
            P("Blue bars show SME groups; teal marks the large-business benchmark. Confidence intervals are retained in the exact-value tables on the following pages.", "SmallR"),
            callout("Do not add the category percentages: businesses could report more than one purpose.", colour=PALE, edge=CORAL),
            PageBreak(),
        ]
    )
    story.extend(section("Exact SME estimates and confidence intervals"))
    rows = []
    for indicator in USE_CASE_ORDER:
        sizes = USE_CASES_BY_INDICATOR[indicator]
        rows.append(
            [
                USE_CASE_LABELS[indicator],
                f"{pct(sizes['micro'])}<br/><font size='6'>{interval(sizes['micro'])}</font>",
                f"{pct(sizes['small'])}<br/><font size='6'>{interval(sizes['small'])}</font>",
                f"{pct(sizes['medium'])}<br/><font size='6'>{interval(sizes['medium'])}</font>",
                f"{pct(sizes['large'])}<br/><font size='6'>{interval(sizes['large'])}</font>",
            ]
        )
    story.extend(
        [
            report_table(["Use case", "Micro", "Small", "Medium", "Large*"], rows, [54*mm, 30*mm, 30*mm, 30*mm, 30*mm], font_size=6.7),
            Spacer(1, 8),
            P("Each cell shows the central estimate and, beneath it, the supplied 95% confidence interval.", "SmallR"),
            P("Rounded respondent bases", "H2R"),
            metric_cards(
                [
                    ("2,500", "Micro", "Respondents"),
                    ("680", "Small", "Respondents"),
                    ("220", "Medium", "Respondents"),
                    ("130", "Large*", "Respondents"),
                ]
            ),
            PageBreak(),
        ]
    )
    story.extend(section("Business interpretation: start with the task"))
    story.extend(
        [
            P(
                "The use-case profile supports a task-first conversation. It does not show whether the reported tools are effective, frequent or integrated.",
                "BodyR",
            ),
            insight_cards(
                [
                    ("Task value", "Which recurring information or content task consumes time and has a clearly defined quality standard?"),
                    ("Risk and review", "What data, legal, customer or reputational risk would require stronger human checking?"),
                    ("Workflow fit", "Is the tool used occasionally, or can it be connected safely to an existing process?"),
                    ("Evidence of benefit", "What before-and-after measure could test usefulness without assuming productivity gains?"),
                ]
            ),
            Spacer(1, 10),
            P("Cross-use-case insight", "H2R"),
            bullet("Research and summarising/drafting form a broad information-work cluster across sizes."),
            bullet("Data analysis/models rises with size in the point estimates and is particularly higher for the large benchmark."),
            bullet("Coding, cybersecurity and customer chatbots remain more specialised among SMEs in the published point estimates."),
            bullet("Later sector analysis should test whether this pattern changes in technology, accounting and financial services."),
            Spacer(1, 9),
            callout("The most useful next question is not simply 'Do you use AI?' but 'For which task, with what controls, and with what evidence of benefit?'", colour=SKY, edge=BLUE),
            PageBreak(),
        ]
    )
    story.extend(
        methods_page(
            table_ids="Table 42",
            denominator_text="All UK businesses within each published business-size category.",
            special_limits=[
                "This is a multiple-response question. Categories overlap and must not be summed.",
                "The survey does not measure frequency, quality, productivity or return on investment for each use case.",
            ],
        )
    )
    metadata = {"report_id": "report_04_ai_use_cases", "finding_ids": ["F-004"], "input_files": [USE_CASES_PATH]}
    return path, {"story": story, "metadata": metadata}


PATHWAY_LABELS = {
    "system_integration": "System integration",
    "automated_decision_making": "Automated decisions",
    "ai_policy_guidance": "Policy/guidance",
    "ai_development_training": "In-house development/training",
}


def report_05() -> tuple[Path, dict]:
    path = OUTPUT / "SME_Report_05_Operational_AI_Adoption_Pathways.pdf"
    story = cover(
        "05",
        "Operational AI adoption pathways",
        "Integration, governance, automated decisions and in-house development are distinct operational choices.",
        "Tables 43, 48 and 50 describe AI-using businesses. Table 47 describes all businesses. "
        "The indicators are shown in separate denominator panels and are not combined into a maturity score.",
        "Among AI-using SMEs, integration and policy/guidance point estimates are higher than automated decision-making. In-house AI development/training remains uncommon across all SMEs.",
    )
    story.extend(section("Executive summary"))
    story.extend(
        [
            metric_cards(
                [
                    ("26.9%-31.5%", "Integration", "Among AI-using SMEs"),
                    ("20.1%-36.8%", "Policy/guidance", "Among AI-using SMEs"),
                    ("3.4%-5.3%", "Automated decisions", "Among AI-using SMEs"),
                    ("3.3%-6.5%", "In-house build/train", "Across all SMEs"),
                ]
            ),
            Spacer(1, 9),
            P(
                "Operational adoption is not one linear ladder. Businesses may integrate, govern, automate, develop or train AI in different combinations. "
                "The source supports separate measures, not a single readiness score.",
                "BodyBoldR",
            ),
            insight_cards(
                [
                    ("Integration is the most common listed operational measure", "Among AI-using micro and small businesses, its point estimate is above policy/guidance and automated decisions."),
                    ("Governance increases with size", "The policy/guidance point estimate rises across micro, small and medium AI users."),
                    ("Automated decisions remain limited", "Point estimates are below 6% for each SME group among AI users."),
                    ("In-house build/training is uncommon", "Across all businesses, the SME point estimates range from 3.3% to 6.5%."),
                ]
            ),
            Spacer(1, 9),
            callout("Operationalisation is better understood as a set of choices and controls than as a single maturity score.", colour=SKY, edge=TEAL),
            PageBreak(),
        ]
    )
    ai_user_indicators = ("system_integration", "ai_policy_guidance", "automated_decision_making")
    groups = []
    for size in SIZE_ORDER:
        bars = []
        for indicator in ai_user_indicators:
            row = PATHWAYS_BY_INDICATOR[indicator][size]
            bars.append((PATHWAY_LABELS[indicator], float(row["estimate"]) * 100, size == "large"))
        groups.append((SIZE_LABELS[size], bars))
    story.extend(section("Conditional pathways among businesses already using AI"))
    story.extend(
        [
            GroupedBarChart(
                groups,
                max_percent=70,
                colour_map={
                    "System integration": BLUE,
                    "Policy/guidance": TEAL,
                    "Automated decisions": CORAL,
                },
                legend=[
                    ("System integration", "Integration"),
                    ("Policy/guidance", "Policy/guidance"),
                    ("Automated decisions", "Automated decisions"),
                ],
                show_values=True,
                height=275,
            ),
            Spacer(1, 7),
            report_table(
                ["Business size", "Integration", "Policy/guidance", "Automated decisions"],
                [
                    [
                        SIZE_LABELS[size],
                        pct(PATHWAYS_BY_INDICATOR["system_integration"][size]),
                        pct(PATHWAYS_BY_INDICATOR["ai_policy_guidance"][size]),
                        pct(PATHWAYS_BY_INDICATOR["automated_decision_making"][size]),
                    ]
                    for size in SIZE_ORDER
                ],
                [55*mm, 39*mm, 39*mm, 39*mm],
            ),
            Spacer(1, 7),
            P("All three measures on this page describe businesses already using AI. They are distinct indicators and are not required stages.", "SmallR"),
            PageBreak(),
        ]
    )
    development_rows = [PATHWAYS_BY_INDICATOR["ai_development_training"][size] for size in SIZE_ORDER]
    story.extend(section("In-house AI development or training across all businesses"))
    story.extend(
        [
            P("<b>Denominator:</b> all UK businesses within each published size group.", "BodyR"),
            CIChart(development_rows, height=245, max_value=0.25),
            report_table(["Business size", "Estimate", "95% interval", "Rounded base"], exact_rows(development_rows), [62*mm, 30*mm, 42*mm, 38*mm]),
            Spacer(1, 8),
            callout(
                "This indicator is uncommon across SMEs. It does not reveal whether businesses buy external tools, configure existing products or use third-party support.",
                colour=PALE,
                edge=CORAL,
            ),
            PageBreak(),
        ]
    )
    story.extend(section("Decision use: four separate operating questions"))
    story.extend(
        [
            insight_cards(
                [
                    ("Integrate", "Which systems, data flows and process owners are involved, and how are exceptions handled?"),
                    ("Govern", "What proportionate rules, responsibilities and human-review requirements apply?"),
                    ("Automate", "Which decisions are suitable for automation, and where must accountability stay explicitly human?"),
                    ("Build or train", "Is in-house development genuinely necessary, or can the problem be solved through existing tools and process redesign?"),
                ]
            ),
            Spacer(1, 10),
            P("Cross-pathway insight", "H2R"),
            bullet("For AI-using SMEs, integration and governance are more common in the point estimates than automated decision-making."),
            bullet("In-house development or training is a separate all-business measure and remains uncommon among SMEs."),
            bullet("The evidence does not support a fixed sequence in which every business must use, integrate, automate and build."),
            bullet("A practical adoption plan should select only the pathways justified by the task, risk, data and available capability."),
            Spacer(1, 9),
            callout("Useful insight: operational AI support should distinguish workflow integration, governance, automation and technical build capability rather than packaging them as one service.", colour=SKY, edge=BLUE),
            PageBreak(),
        ]
    )
    story.extend(
        methods_page(
            table_ids="Tables 43, 47, 48 and 50",
            denominator_text="Tables 43, 48 and 50 cover businesses that report using AI technologies. Table 47 covers all UK businesses. The two populations are displayed separately.",
            special_limits=[
                "The indicators are not a required sequence and are not combined into a readiness or maturity score.",
                "The source does not identify vendors, implementation quality, spend, outcomes or the reasons businesses choose each pathway.",
            ],
        )
    )
    metadata = {"report_id": "report_05_operational_ai_pathways", "finding_ids": ["F-005"], "input_files": [PATHWAYS_PATH]}
    return path, {"story": story, "metadata": metadata}


def synthesis_report() -> tuple[Path, dict]:
    path = OUTPUT / "SME_Cross_Report_Synthesis_AI_Adoption_and_Operationalisation.pdf"
    story = cover(
        "SYNTHESIS",
        "From AI use to operationalisation",
        "Cross-report insights from five UK SME AI adoption studies.",
        "The synthesis compares patterns only where definitions allow. All-business and AI-user measures remain separate; multiple-response categories are not summed.",
        "The five reports point to a recurring distinction between access to AI, the tasks it supports, and the organisational work needed to integrate and govern it.",
    )
    story.extend(section("Five reports, one evidence story"))
    story.extend(
        [
            insight_cards(
                [
                    ("01 - Adoption", "Reported AI-use point estimates rise from 37.4% for micro to 57.1% for medium businesses."),
                    ("02 - Integration", "Among AI users, SME system-integration point estimates cluster between 26.9% and 31.5%."),
                    ("03 - Governance", "Policy/guidance point estimates rise from 20.1% for micro to 36.8% for medium AI users."),
                    ("04 - Use cases", "Research is the highest listed use-case point estimate in every size group."),
                    ("05 - Pathways", "Integration and policy/guidance are more common than automated decisions among AI-using SMEs."),
                    ("Common boundary", "Every finding is descriptive; none establishes causation, effectiveness or formal pairwise significance."),
                ],
                columns=2,
            ),
            Spacer(1, 10),
            callout(
                "Cross-report conclusion: 'adoption' is not one event. The evidence distinguishes reported use, task choice, system integration, governance, automation and in-house development.",
                colour=SKY,
                edge=TEAL,
            ),
            PageBreak(),
        ]
    )
    story.extend(section("Reach, integration and governance by size"))
    rows = []
    for size in SIZE_ORDER:
        rows.append(
            [
                SIZE_LABELS[size],
                pct(AI[size]),
                pct(INTEGRATION_BY_SIZE[size]),
                pct(GOVERNANCE_BY_SIZE[size]),
            ]
        )
    story.extend(
        [
            report_table(
                ["Business size", "AI use - all businesses", "Integration - AI users", "Policy/guidance - AI users"],
                rows,
                [50*mm, 41*mm, 41*mm, 41*mm],
            ),
            Spacer(1, 10),
            P(
                "The columns describe different populations. They are presented side by side to show distinct dimensions, not to calculate conversion rates.",
                "SmallR",
            ),
            insight_cards(
                [
                    ("Size gradient in reach", "The all-business adoption point estimates rise across the three SME groups."),
                    ("Integration plateau among SMEs", "The small and medium integration point estimates are similar, while micro is modestly lower; intervals overlap."),
                    ("Governance gradient among AI users", "The policy/guidance point estimate rises across micro, small and medium AI users."),
                    ("Large benchmark separates", "Large businesses have higher point estimates on all three measures, but the source does not explain why."),
                ]
            ),
            Spacer(1, 9),
            callout("Inference: access to AI, integration and governance may face different constraints and should be researched as separate workstreams.", colour=PALE, edge=BLUE),
            PageBreak(),
        ]
    )
    story.extend(section("Information tasks lead the reported use-case profile"))
    use_case_rows = []
    for indicator in USE_CASE_ORDER:
        sizes = USE_CASES_BY_INDICATOR[indicator]
        use_case_rows.append(
            [
                USE_CASE_LABELS[indicator],
                pct(sizes["micro"]),
                pct(sizes["small"]),
                pct(sizes["medium"]),
                pct(sizes["large"]),
            ]
        )
    story.extend(
        [
            report_table(["Use case", "Micro", "Small", "Medium", "Large*"], use_case_rows, [54*mm, 30*mm, 30*mm, 30*mm, 30*mm]),
            Spacer(1, 8),
            insight_cards(
                [
                    ("Broad information cluster", "Research and summarising/drafting are the two leading listed purposes across size groups."),
                    ("Narrower technical applications", "Coding, cybersecurity and chatbots have lower point estimates among SMEs."),
                    ("Operational depth is separate", "A reported use case does not show whether a tool is integrated, governed or effective."),
                    ("Sector question", "Technology, accounting and financial services may show different task profiles and should be tested separately."),
                ]
            ),
            Spacer(1, 9),
            callout("Cross-report insight: task selection appears to be the entry point; integration and governance determine whether use becomes part of a dependable operating process.", colour=SKY, edge=TEAL),
            PageBreak(),
        ]
    )
    story.extend(section("Operationalisation: what is common and what is not"))
    story.extend(
        [
            metric_cards(
                [
                    ("26.9%-31.5%", "Integration", "AI-using SMEs"),
                    ("20.1%-36.8%", "Policy/guidance", "AI-using SMEs"),
                    ("3.4%-5.3%", "Automated decisions", "AI-using SMEs"),
                    ("3.3%-6.5%", "In-house build/train", "All SMEs"),
                ]
            ),
            Spacer(1, 10),
            P(
                "The operational indicators do not form a maturity ladder. They show that different capabilities and controls are unevenly present.",
                "BodyBoldR",
            ),
            insight_cards(
                [
                    ("Integration and governance are central", "Their point estimates are well above automated decision-making among AI-using SMEs."),
                    ("Automation is limited", "Automated-decision point estimates remain below 6% for each SME group."),
                    ("In-house build is specialised", "Development/training point estimates remain below 7% across all SME groups."),
                    ("Buy-versus-build is unresolved", "The source does not identify procurement, vendor choice or external implementation support."),
                ]
            ),
            Spacer(1, 10),
            P("Practical inference - labelled, not measured", "H2R"),
            bullet("Many SMEs may need help turning selected tasks into controlled workflows before considering complex automation."),
            bullet("Governance can be developed alongside integration rather than postponed until after scale."),
            bullet("Most organisations should test whether existing tools and process redesign are sufficient before assuming in-house model development is necessary."),
            bullet("Sector-specific evidence is needed before turning these general patterns into a market offer."),
            PageBreak(),
        ]
    )
    story.extend(section("A decision framework for SMEs and advisers"))
    story.extend(
        [
            insight_cards(
                [
                    ("1. Define the task", "Identify the recurring decision or workflow, its users and the quality standard."),
                    ("2. Assess the evidence", "Use the relevant size and sector baseline without treating it as an individual diagnosis."),
                    ("3. Choose the pathway", "Decide whether the need is simple use, integration, governance, automation or development."),
                    ("4. Set controls", "Define data rules, human review, ownership, incident handling and monitoring."),
                    ("5. Test usefulness", "Measure a bounded operational outcome without assuming causation or ROI."),
                    ("6. Review and scale", "Expand only when evidence, controls and capability support the next step."),
                ],
                columns=2,
            ),
            Spacer(1, 10),
            P("Research priorities created by the synthesis", "H2R"),
            bullet("Sector profiles for technology, accounting and financial services, subject to bases and suppression."),
            bullet("Barriers to initial use versus barriers to system integration."),
            bullet("Governance practices beyond policy presence, including staff awareness and incident response."),
            bullet("Task-level evidence on frequency, quality, productivity and business outcomes."),
            bullet("Buy, configure, integrate or build choices and the role of external providers."),
            Spacer(1, 8),
            callout("The synthesis is most useful as a map of questions and evidence gaps. It does not create a readiness score or claim a universal adoption journey.", colour=PALE, edge=CORAL),
            PageBreak(),
        ]
    )
    story.extend(
        methods_page(
            table_ids="Tables 42, 43, 47, 48 and 50",
            denominator_text="Reports 01 and 04 use all-business measures. Reports 02 and 03 use AI-user measures. Report 05 contains both and keeps them in separate panels.",
            special_limits=[
                "Cross-report statements compare qualitative patterns only; they do not multiply or subtract estimates with different denominators.",
                "Report 04 categories allow multiple responses and are not summed.",
                "Practical recommendations are labelled as decision prompts or hypotheses rather than survey findings.",
            ],
        )
    )
    metadata = {
        "report_id": "cross_report_synthesis",
        "finding_ids": ["F-001", "F-002", "F-003", "F-004", "F-005"],
        "input_files": [AI_USE_PATH, INTEGRATION_PATH, GOVERNANCE_PATH, USE_CASES_PATH, PATHWAYS_PATH],
    }
    return path, {"story": story, "metadata": metadata}


def archive_previous() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.glob("SME_*.pdf"):
        destination = ARCHIVE / path.name
        if not destination.exists():
            shutil.copy2(path, destination)
        metadata = path.with_suffix(".metadata.json")
        if metadata.exists():
            metadata_destination = ARCHIVE / metadata.name
            if not metadata_destination.exists():
                shutil.copy2(metadata, metadata_destination)


def remove_legacy_report_01() -> None:
    for name in (
        "SME_Preliminary_Report_01_AI_Use_by_Business_Size.pdf",
        "SME_Preliminary_Report_01_AI_Use_by_Business_Size.metadata.json",
    ):
        path = OUTPUT / name
        if path.exists():
            path.unlink()


def main() -> None:
    validate_inputs()
    archive_previous()
    reports = [
        report_01(),
        report_02(),
        report_03(),
        report_04(),
        report_05(),
        synthesis_report(),
    ]
    labels = [
        ("01", "Reported AI use by business size"),
        ("02", "AI adoption and system integration"),
        ("03", "AI governance among AI-using businesses"),
        ("04", "How UK businesses use AI"),
        ("05", "Operational AI adoption pathways"),
        ("SYNTHESIS", "From AI use to operationalisation"),
    ]
    for (path, bundle), (report_number, title) in zip(reports, labels):
        build_report(
            path,
            report_number,
            title,
            bundle["story"],
            metadata=bundle["metadata"],
        )
    remove_legacy_report_01()
    manifest = {
        "suite_id": "uk_sme_ai_adoption_final_report_suite",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "decision_id": "D-022",
        "publication_status": "approved_for_distribution",
        "reports": [
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "page_count": len(PdfReader(str(path)).pages),
            }
            for path, _bundle in reports
        ],
        "input_files": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in (AI_USE_PATH, INTEGRATION_PATH, GOVERNANCE_PATH, USE_CASES_PATH, PATHWAYS_PATH)
        ],
    }
    (OUTPUT / "SME_Final_Report_Suite.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
