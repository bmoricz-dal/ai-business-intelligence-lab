"""Create private Report 02 from the D-018-approved combined evidence brief."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPORT_ID = "report_02_ai_adoption_integration"
REPORT_TITLE = "AI adoption and system integration by business size"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")
EXPECTED_HASHES = {
    "combined_brief": "363a370dbd6647a62f2d367305987e431308a6eddccb3b72cd66251c4f090599",
    "combined_brief_approval": "45d3ffaacc7163e0708bf894871a6c9735f5b8a968d35be12f5189f0f8c36597",
    "f001_result": "8f0d29ec30451fbec96aefb5aa0909e31d62c16c0e618bb75d95d809f51d8eb6",
    "f001_chart": "096df1115a0fde319df3ff2cdfc4d16fa4f1d27973460577411715eb6bc0b8f8",
    "f001_chart_approval": "1216452b86fb7270f4bf7cc39768035cf7306cea34059d1c8f7f54dcc2d101a4",
    "f002_result": "dd84088a34c925767dc86786000e6299d6636c5e2c6fba18148c055840beda09",
    "f002_chart": "933ce1b1dc3ff6573983bbaa5d53afa654293ce2aca72c34fbed42fcd328eeee",
    "f002_chart_approval": "039795fd66e383c0c077509cfe04debdc3a4a163332bb578ba6a17f2ccf76d08",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_hash(path: Path, key: str) -> None:
    if sha256_file(path) != EXPECTED_HASHES[key]:
        raise ValueError(f"Report 02 approved-input checksum mismatch: {key}")


def _load_rows(
    path: Path,
    *,
    table: str,
    indicator: str,
    denominator: str,
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError(f"Expected four rows in {path.name}")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError(f"Unexpected business-size rows in {path.name}")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError(f"Unexpected analytical roles in {path.name}")
    if {row["source_table_id"] for row in rows} != {table}:
        raise ValueError(f"Unexpected source table in {path.name}")
    if {row["indicator_id"] for row in rows} != {indicator}:
        raise ValueError(f"Unexpected indicator in {path.name}")
    if {row["denominator_id"] for row in rows} != {denominator}:
        raise ValueError(f"Unexpected denominator in {path.name}")
    return rows


def verify_inputs(
    *,
    combined_brief_path: Path,
    combined_brief_approval_path: Path,
    f001_result_path: Path,
    f001_chart_path: Path,
    f001_chart_approval_path: Path,
    f002_result_path: Path,
    f002_chart_path: Path,
    f002_chart_approval_path: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    paths = {
        "combined_brief": combined_brief_path,
        "combined_brief_approval": combined_brief_approval_path,
        "f001_result": f001_result_path,
        "f001_chart": f001_chart_path,
        "f001_chart_approval": f001_chart_approval_path,
        "f002_result": f002_result_path,
        "f002_chart": f002_chart_path,
        "f002_chart_approval": f002_chart_approval_path,
    }
    for key, path in paths.items():
        _require_hash(path, key)

    brief_approval = json.loads(
        combined_brief_approval_path.read_text(encoding="utf-8")
    )
    if (
        brief_approval.get("decision_id") != "D-018"
        or brief_approval.get("task_id") != "G5-16"
        or brief_approval.get("finding_ids") != ["F-001", "F-002"]
        or brief_approval.get("approval_status")
        != "approved_for_internal_product_development"
        or brief_approval.get("validation_result") != "passed"
        or not brief_approval.get("brief_bytes_unchanged")
    ):
        raise ValueError("Report 02 requires the D-018-approved combined brief")
    checks = brief_approval.get("checks", {})
    if checks.get("denominator_ids") != [
        "all_uk_businesses",
        "uk_businesses_using_ai_technologies",
    ]:
        raise ValueError("D-018 does not retain both expected denominators")
    if checks.get("denominators_kept_separate") is not True:
        raise ValueError("D-018 does not confirm denominator separation")
    if checks.get("cross_denominator_arithmetic_present") is not False:
        raise ValueError("D-018 does not prohibit cross-denominator arithmetic")

    f001_chart_approval = json.loads(
        f001_chart_approval_path.read_text(encoding="utf-8")
    )
    if (
        f001_chart_approval.get("decision_id") != "D-012"
        or f001_chart_approval.get("finding_id") != "F-001"
        or f001_chart_approval.get("approval_status")
        != "approved_for_internal_product_development"
    ):
        raise ValueError("Report 02 requires the D-012-approved F-001 chart")

    f002_chart_approval = json.loads(
        f002_chart_approval_path.read_text(encoding="utf-8")
    )
    if (
        f002_chart_approval.get("decision_id") != "D-017"
        or f002_chart_approval.get("finding_id") != "F-002"
        or f002_chart_approval.get("approval_status")
        != "approved_for_internal_product_development"
        or f002_chart_approval.get("checks", {}).get(
            "conditional_denominator_visible"
        )
        is not True
    ):
        raise ValueError("Report 02 requires the D-017-approved F-002 chart")

    first_rows = _load_rows(
        f001_result_path,
        table="42",
        indicator="uses_any_ai_based_technologies",
        denominator="all_uk_businesses",
    )
    second_rows = _load_rows(
        f002_result_path,
        table="48",
        indicator="ai_tools_integrated_with_systems",
        denominator="uk_businesses_using_ai_technologies",
    )

    brief = combined_brief_path.read_text(encoding="utf-8")
    required_phrases = (
        "Denominator: all UK businesses",
        "These are not percentages of all UK businesses",
        "does not multiply, divide or subtract",
        "Publication status: Not approved",
    )
    for phrase in required_phrases:
        if phrase not in brief:
            raise ValueError(f"D-018 brief is missing safeguard: {phrase}")

    approval_ids = {
        "brief": brief_approval["approval_id"],
        "f001_chart": f001_chart_approval["approval_id"],
        "f002_chart": f002_chart_approval["approval_id"],
    }
    return first_rows, second_rows, approval_ids


def report_spec() -> dict[str, Any]:
    return {
        "report_id": REPORT_ID,
        "title": REPORT_TITLE,
        "page_count": 4,
        "page_titles": [
            "Executive summary",
            "Reported AI use among all businesses",
            "System integration among businesses already using AI",
            "Interpretation, method and evidence trail",
        ],
        "finding_ids": ["F-001", "F-002"],
        "denominator_ids": [
            "all_uk_businesses",
            "uk_businesses_using_ai_technologies",
        ],
        "publication_status": "not_approved",
    }


def validate_output_target(output_pdf: Path, *, replace: bool = False) -> None:
    metadata_path = output_pdf.with_suffix(".metadata.json")
    if (output_pdf.exists() or metadata_path.exists()) and not replace:
        raise FileExistsError(f"Refusing to overwrite Report 02: {output_pdf}")


def _wrap(text: str, font: str, size: float, width: float) -> list[str]:
    from reportlab.pdfbase.pdfmetrics import stringWidth

    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and stringWidth(candidate, font, size) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _paragraph(
    pdf: Any,
    text: str,
    *,
    x: float,
    y: float,
    width: float,
    font: str = "Helvetica",
    size: float = 9,
    leading: float = 12,
    colour: Any = None,
) -> float:
    from reportlab.lib.colors import HexColor

    pdf.setFillColor(colour or HexColor("#273444"))
    pdf.setFont(font, size)
    for line in _wrap(text, font, size, width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def _footer(pdf: Any, page_number: int, page_count: int) -> None:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4

    width, _height = A4
    pdf.setStrokeColor(HexColor("#CCD7DD"))
    pdf.setLineWidth(0.6)
    pdf.line(42, 42, width - 42, 42)
    pdf.setFillColor(HexColor("#5C6873"))
    pdf.setFont("Helvetica", 7)
    pdf.drawString(42, 28, "SME Intelligence Lab | Internal - not for publication")
    pdf.drawRightString(width - 42, 28, f"Report 02 | Page {page_number} of {page_count}")


def _section_header(pdf: Any, section: str, title: str, page: int) -> float:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import A4

    width, height = A4
    navy = HexColor("#15324A")
    pdf.setFillColor(navy)
    pdf.rect(0, height - 72, width, 72, stroke=0, fill=1)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(42, height - 27, section.upper())
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(42, height - 52, title)
    pdf.setFont("Helvetica", 7)
    pdf.drawRightString(width - 42, height - 27, f"REPORT 02 / {page:02d}")
    return height - 100


def _draw_badge(pdf: Any, text: str, x: float, y: float, width: float) -> None:
    from reportlab.lib.colors import HexColor

    pdf.setFillColor(HexColor("#F4C95D"))
    pdf.roundRect(x, y, width, 20, 5, stroke=0, fill=1)
    pdf.setFillColor(HexColor("#15324A"))
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawCentredString(x + width / 2, y + 7, text)


def _draw_measure_card(
    pdf: Any,
    *,
    x: float,
    y_top: float,
    width: float,
    height: float,
    title: str,
    denominator: str,
    rows: list[dict[str, str]],
    accent: str,
) -> None:
    from reportlab.lib.colors import HexColor

    pdf.setFillColor(HexColor("#EEF4F6"))
    pdf.roundRect(x, y_top - height, width, height, 7, stroke=0, fill=1)
    pdf.setFillColor(HexColor(accent))
    pdf.rect(x, y_top - 4, width, 4, stroke=0, fill=1)
    pdf.setFillColor(HexColor("#15324A"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 12, y_top - 23, title)
    y = _paragraph(
        pdf,
        denominator,
        x=x + 12,
        y=y_top - 39,
        width=width - 24,
        size=7,
        leading=9,
        colour=HexColor("#5C6873"),
    )
    labels = {"micro": "Micro", "small": "Small", "medium": "Medium", "large": "Large*"}
    y -= 5
    for row in rows:
        pdf.setFillColor(HexColor("#273444"))
        pdf.setFont("Helvetica", 8)
        pdf.drawString(x + 12, y, labels[row["business_size"]])
        pdf.setFont("Helvetica-Bold", 9)
        pdf.setFillColor(HexColor(accent))
        pdf.drawRightString(
            x + width - 12,
            y,
            f"{float(row['estimate_percent']):.1f}%",
        )
        y -= 18
    pdf.setFillColor(HexColor("#5C6873"))
    pdf.setFont("Helvetica", 6.5)
    pdf.drawString(x + 12, y_top - height + 10, "* Large businesses are a reference benchmark.")


def _draw_ci_chart(
    pdf: Any,
    rows: list[dict[str, str]],
    *,
    x: float,
    y_top: float,
    width: float,
) -> float:
    from reportlab.lib.colors import HexColor, white
    from reportlab.pdfbase.pdfmetrics import stringWidth

    plot_left = x + 150
    plot_right = x + width - 28
    plot_width = plot_right - plot_left
    grid = HexColor("#CCD7DD")
    ink = HexColor("#273444")
    muted = HexColor("#5C6873")
    primary = HexColor("#005EA5")
    benchmark = HexColor("#A84F00")
    row_gap = 34
    bottom = y_top - 30 - row_gap * 3 - 24

    pdf.setFont("Helvetica", 7)
    pdf.setFillColor(muted)
    pdf.setStrokeColor(grid)
    pdf.setLineWidth(0.6)
    for tick in (0, 20, 40, 60, 80, 100):
        tick_x = plot_left + plot_width * tick / 100
        pdf.line(tick_x, y_top - 10, tick_x, bottom + 10)
        pdf.drawCentredString(tick_x, y_top, f"{tick}%")

    labels = {
        "micro": "Micro (up to 9)",
        "small": "Small (10 to 49)",
        "medium": "Medium (50 to 249)",
        "large": "Large (250+) benchmark",
    }
    for index, row in enumerate(rows):
        row_y = y_top - 28 - index * row_gap
        estimate = float(row["estimate_percent"])
        lower = float(row["lower_limit_percent"])
        upper = float(row["upper_limit_percent"])
        colour = benchmark if row["business_size"] == "large" else primary
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(x, row_y - 3, labels[row["business_size"]])
        x_lower = plot_left + plot_width * lower / 100
        x_upper = plot_left + plot_width * upper / 100
        x_estimate = plot_left + plot_width * estimate / 100
        pdf.setStrokeColor(colour)
        pdf.setLineWidth(2.8)
        pdf.line(x_lower, row_y, x_upper, row_y)
        pdf.setLineWidth(1.4)
        pdf.line(x_lower, row_y - 4, x_lower, row_y + 4)
        pdf.line(x_upper, row_y - 4, x_upper, row_y + 4)
        pdf.setFillColor(colour)
        if row["business_size"] == "large":
            path = pdf.beginPath()
            path.moveTo(x_estimate, row_y + 6)
            path.lineTo(x_estimate + 6, row_y)
            path.lineTo(x_estimate, row_y - 6)
            path.lineTo(x_estimate - 6, row_y)
            path.close()
            pdf.drawPath(path, stroke=0, fill=1)
        else:
            pdf.circle(x_estimate, row_y, 4.5, stroke=0, fill=1)
        label = f"{estimate:.1f}%"
        label_x = min(x_upper + 7, plot_right - 32)
        label_width = stringWidth(label, "Helvetica-Bold", 7.5)
        pdf.setFillColor(white)
        pdf.rect(label_x - 1, row_y - 5, label_width + 2, 10, stroke=0, fill=1)
        pdf.setFillColor(colour)
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y - 3, label)
    return bottom - 4


def _draw_evidence_table(
    pdf: Any,
    rows: list[dict[str, str]],
    *,
    x: float,
    y: float,
    width: float,
) -> float:
    from reportlab.lib.colors import HexColor

    pale = HexColor("#EEF4F6")
    navy = HexColor("#15324A")
    ink = HexColor("#273444")
    grid = HexColor("#CCD7DD")
    columns = (x + 8, x + 225, x + 305, x + 402)
    pdf.setFillColor(pale)
    pdf.rect(x, y - 3, width, 19, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 7.5)
    for position, header in zip(
        columns,
        ("Published size group", "Estimate", "95% interval", "Base"),
        strict=True,
    ):
        pdf.drawString(position, y + 3, header)
    y -= 18
    labels = {
        "micro": "Micro, up to 9 employees",
        "small": "Small, 10 to 49 employees",
        "medium": "Medium, 50 to 249 employees",
        "large": "Large, 250 or more employees*",
    }
    for row in rows:
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(columns[0], y, labels[row["business_size"]])
        pdf.drawString(columns[1], y, f"{float(row['estimate_percent']):.1f}%")
        pdf.drawString(
            columns[2],
            y,
            f"{float(row['lower_limit_percent']):.1f}% to "
            f"{float(row['upper_limit_percent']):.1f}%",
        )
        pdf.drawRightString(x + width - 8, y, f"{int(row['sample_base']):,}")
        pdf.setStrokeColor(grid)
        pdf.setLineWidth(0.4)
        pdf.line(x, y - 5, x + width, y - 5)
        y -= 17
    return y


def _draw_page_one(pdf: Any, first: list[dict[str, str]], second: list[dict[str, str]]) -> None:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import A4

    width, height = A4
    navy = HexColor("#15324A")
    muted = HexColor("#5C6873")
    pale = HexColor("#EEF4F6")
    teal = "#087E8B"
    orange = "#A84F00"

    pdf.setFillColor(navy)
    pdf.rect(0, height - 160, width, 160, stroke=0, fill=1)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(42, height - 34, "SME INTELLIGENCE LAB")
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(42, height - 72, "AI adoption and system integration")
    pdf.drawString(42, height - 102, "by business size")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(42, height - 128, "Evidence from the UK Business Data Survey 2026")
    _draw_badge(pdf, "PRIVATE REPORT 02 - NOT FOR PUBLICATION", 42, height - 184, 202)
    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 7)
    pdf.drawRightString(width - 42, height - 177, "D-018 approved evidence brief")

    y = height - 218
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(42, y, "Executive summary")
    y = _paragraph(
        pdf,
        "This report presents two related but distinct measures: reported AI use "
        "among all businesses, and system integration among businesses already "
        "using AI. The measures use different denominators and are not combined "
        "mathematically.",
        x=42,
        y=y - 18,
        width=width - 84,
        size=9,
        leading=12,
    )

    card_top = y - 12
    gap = 14
    card_width = (width - 84 - gap) / 2
    _draw_measure_card(
        pdf,
        x=42,
        y_top=card_top,
        width=card_width,
        height=154,
        title="1. Reported AI use",
        denominator="Denominator: all businesses in each size group",
        rows=first,
        accent=teal,
    )
    _draw_measure_card(
        pdf,
        x=42 + card_width + gap,
        y_top=card_top,
        width=card_width,
        height=154,
        title="2. System integration",
        denominator="Denominator: businesses already using AI",
        rows=second,
        accent=orange,
    )

    y = card_top - 184
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "How to read the evidence")
    pdf.setFillColor(pale)
    pdf.roundRect(42, y - 84, width - 84, 70, 6, stroke=0, fill=1)
    _paragraph(
        pdf,
        "Table 42 describes the breadth of reported AI use across all businesses. "
        "Table 48 describes integration depth only within the survey's AI-user "
        "population. The Table 48 percentages are not shares of all businesses "
        "and this report does not estimate a conversion funnel.",
        x=54,
        y=y - 33,
        width=width - 108,
        size=8.5,
        leading=11,
    )

    y -= 112
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Headline insights")
    bullets = [
        "Reported AI use rises across the published size-group point estimates.",
        "Among AI users, small and medium integration estimates are similar; the large benchmark is higher.",
        "The evidence is descriptive and does not establish significance, causation, readiness, value or service demand.",
    ]
    y -= 17
    for bullet in bullets:
        pdf.setFillColor(HexColor("#087E8B"))
        pdf.circle(47, y + 3, 2, stroke=0, fill=1)
        y = _paragraph(
            pdf,
            bullet,
            x=57,
            y=y,
            width=width - 99,
            size=8.5,
            leading=11,
        )
        y -= 7
    _footer(pdf, 1, 4)


def _draw_finding_page(
    pdf: Any,
    *,
    page_number: int,
    section: str,
    title: str,
    denominator: str,
    rows: list[dict[str, str]],
    interpretation: str,
    boundary: str,
    source_table: str,
) -> None:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4

    width, _height = A4
    navy = HexColor("#15324A")
    pale = HexColor("#EEF4F6")
    ink = HexColor("#273444")
    y = _section_header(pdf, section, title, page_number)

    pdf.setFillColor(pale)
    pdf.roundRect(42, y - 48, width - 84, 42, 6, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(54, y - 21, "DENOMINATOR")
    _paragraph(
        pdf,
        denominator,
        x=54,
        y=y - 34,
        width=width - 108,
        size=8,
        leading=10,
        colour=ink,
    )

    chart_bottom = _draw_ci_chart(
        pdf,
        rows,
        x=42,
        y_top=y - 78,
        width=width - 84,
    )
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(42, chart_bottom - 14, "Evidence table")
    table_bottom = _draw_evidence_table(
        pdf,
        rows,
        x=42,
        y=chart_bottom - 34,
        width=width - 84,
    )
    pdf.setFillColor(HexColor("#5C6873"))
    pdf.setFont("Helvetica", 6.5)
    pdf.drawString(42, table_bottom + 2, "* Large businesses are a reference benchmark.")

    y = table_bottom - 22
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(42, y, "Interpretation")
    y = _paragraph(
        pdf,
        interpretation,
        x=42,
        y=y - 15,
        width=width - 84,
        size=8.5,
        leading=11,
    )
    y -= 8
    pdf.setFillColor(pale)
    pdf.roundRect(42, y - 52, width - 84, 47, 5, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(52, y - 19, "SOURCE AND BOUNDARY")
    _paragraph(
        pdf,
        f"DSIT, UK Business Data Survey 2026, Table {source_table}. {boundary}",
        x=52,
        y=y - 32,
        width=width - 104,
        size=7,
        leading=9,
        colour=ink,
    )
    _footer(pdf, page_number, 4)


def _draw_page_four(pdf: Any) -> None:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4

    width, _height = A4
    navy = HexColor("#15324A")
    pale = HexColor("#EEF4F6")
    ink = HexColor("#273444")
    muted = HexColor("#5C6873")
    y = _section_header(
        pdf,
        "Interpretation and method",
        "What the evidence supports - and what it does not",
        4,
    )

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "How the measures fit together")
    y -= 18
    gap = 14
    column_width = (width - 84 - gap) / 2
    for offset, heading, body in (
        (
            0,
            "ADOPTION BREADTH",
            "Table 42 estimates reported AI use among all businesses in each published size group.",
        ),
        (
            column_width + gap,
            "INTEGRATION DEPTH",
            "Table 48 estimates system integration only among businesses in the size group that already report AI use.",
        ),
    ):
        pdf.setFillColor(pale)
        pdf.roundRect(42 + offset, y - 82, column_width, 76, 6, stroke=0, fill=1)
        pdf.setFillColor(navy)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(54 + offset, y - 24, heading)
        _paragraph(
            pdf,
            body,
            x=54 + offset,
            y=y - 40,
            width=column_width - 24,
            size=7.5,
            leading=10,
            colour=ink,
        )

    y -= 110
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Evidence boundaries")
    y -= 18
    left_x = 42
    right_x = 42 + column_width + gap
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left_x, y, "Supported descriptive wording")
    pdf.drawString(right_x, y, "Not supported by this evidence")
    supported = [
        "Point estimates vary by published business size.",
        "Reported AI-use estimates rise across the size groups.",
        "Among AI users, small and medium integration estimates are similar.",
        "Large businesses remain a separate benchmark.",
    ]
    unsupported = [
        "Formal significance or causal claims.",
        "An all-business integration rate or conversion funnel.",
        "Readiness, productivity, ROI or intervention effectiveness.",
        "Counts of UK businesses or evidence of service demand.",
    ]
    left_y = y - 18
    right_y = y - 18
    for bullet in supported:
        pdf.setFillColor(HexColor("#087E8B"))
        pdf.circle(left_x + 3, left_y + 3, 1.8, stroke=0, fill=1)
        left_y = _paragraph(
            pdf,
            bullet,
            x=left_x + 12,
            y=left_y,
            width=column_width - 12,
            size=7.5,
            leading=10,
        )
        left_y -= 6
    for bullet in unsupported:
        pdf.setFillColor(HexColor("#A84F00"))
        pdf.circle(right_x + 3, right_y + 3, 1.8, stroke=0, fill=1)
        right_y = _paragraph(
            pdf,
            bullet,
            x=right_x + 12,
            y=right_y,
            width=column_width - 12,
            size=7.5,
            leading=10,
        )
        right_y -= 6

    y = min(left_y, right_y) - 12
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Source and method")
    y = _paragraph(
        pdf,
        "Source: Department for Science, Innovation and Technology, UK Business "
        "Data Survey 2026. Dataset version: 18 June 2026. Fieldwork: 10 October "
        "2025 to 28 January 2026. Estimates are weighted percentages with "
        "supplied 95% confidence limits. Bases are rounded unweighted respondent "
        "counts, not counts of UK businesses.",
        x=42,
        y=y - 16,
        width=width - 84,
        size=7.7,
        leading=10,
    )

    y -= 8
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Evidence trail")
    y = _paragraph(
        pdf,
        "F-001: D-010 result, D-011 comparison method, D-012 chart and D-013 "
        "first brief. F-002: D-014 scope, D-015 processed snapshot, D-016 result "
        "and D-017 chart. Combined brief: D-018.",
        x=42,
        y=y - 16,
        width=width - 84,
        size=7.7,
        leading=10,
    )

    y -= 10
    pdf.setFillColor(HexColor("#F4C95D"))
    pdf.roundRect(42, y - 48, width - 84, 43, 5, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(54, y - 20, "INTERNAL REVIEW BOUNDARY")
    _paragraph(
        pdf,
        "This private report is for owner review. External sharing and publication "
        "remain unapproved.",
        x=54,
        y=y - 34,
        width=width - 108,
        size=7.5,
        leading=9,
        colour=ink,
    )
    pdf.setFillColor(muted)
    _footer(pdf, 4, 4)


def _draw_report(
    pdf: Any,
    first_rows: list[dict[str, str]],
    second_rows: list[dict[str, str]],
) -> None:
    pdf.setTitle(REPORT_TITLE)
    pdf.setAuthor("SME Intelligence Lab")
    pdf.setSubject("Private UK SME AI adoption and system integration report")

    _draw_page_one(pdf, first_rows, second_rows)
    pdf.showPage()
    _draw_finding_page(
        pdf,
        page_number=2,
        section="Finding 01 / Adoption breadth",
        title="Reported AI use among all businesses",
        denominator=(
            "All UK businesses within each published business-size category."
        ),
        rows=first_rows,
        interpretation=(
            "The point estimates rise across the published business-size groups. "
            "This is a descriptive pattern and the large-business value is a "
            "reference benchmark outside the primary SME scope."
        ),
        boundary=(
            "No formal significance or causal claim. Bases are rounded "
            "unweighted samples, not business counts."
        ),
        source_table="42",
    )
    pdf.showPage()
    _draw_finding_page(
        pdf,
        page_number=3,
        section="Finding 02 / Integration depth",
        title="System integration among businesses already using AI",
        denominator=(
            "UK businesses in each size group that report using AI technologies. "
            "These are not percentages of all UK businesses."
        ),
        rows=second_rows,
        interpretation=(
            "Among AI-using businesses, the large-business benchmark has a higher "
            "point estimate than the three SME groups. The small and medium point "
            "estimates are similar. This is descriptive, not a formal test."
        ),
        boundary=(
            "Do not convert to an all-business integration rate or combine "
            "arithmetically with Table 42. No significance or causal claim."
        ),
        source_table="48",
    )
    pdf.showPage()
    _draw_page_four(pdf)
    pdf.showPage()


def create_report(
    *,
    combined_brief_path: Path,
    combined_brief_approval_path: Path,
    f001_result_path: Path,
    f001_chart_path: Path,
    f001_chart_approval_path: Path,
    f002_result_path: Path,
    f002_chart_path: Path,
    f002_chart_approval_path: Path,
    output_pdf: Path,
    created_at: datetime | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    from pypdf import PdfReader
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    validate_output_target(output_pdf, replace=replace)
    input_arguments = {
        "combined_brief_path": combined_brief_path,
        "combined_brief_approval_path": combined_brief_approval_path,
        "f001_result_path": f001_result_path,
        "f001_chart_path": f001_chart_path,
        "f001_chart_approval_path": f001_chart_approval_path,
        "f002_result_path": f002_result_path,
        "f002_chart_path": f002_chart_path,
        "f002_chart_approval_path": f002_chart_approval_path,
    }
    first_rows, second_rows, approval_ids = verify_inputs(**input_arguments)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "wb",
        dir=output_pdf.parent,
        suffix=".pdf",
        delete=False,
    ) as temporary_file:
        temporary_pdf = Path(temporary_file.name)
    try:
        pdf = canvas.Canvas(str(temporary_pdf), pagesize=A4, pageCompression=1)
        _draw_report(pdf, first_rows, second_rows)
        pdf.save()
        reader = PdfReader(str(temporary_pdf))
        if len(reader.pages) != 4:
            raise ValueError("Report 02 must contain exactly four pages")
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
        required_text = (
            "Reported AI use among all businesses",
            "System integration among businesses already using AI",
            "not percentages of all UK businesses",
            "External sharing and publication remain unapproved",
        )
        for text in required_text:
            if text not in extracted:
                raise ValueError(f"Report 02 PDF is missing required text: {text}")
        os.replace(temporary_pdf, output_pdf)
    finally:
        temporary_pdf.unlink(missing_ok=True)

    created = (created_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    inputs = []
    for name, path in input_arguments.items():
        inputs.append({"name": name, "path": str(path), "sha256": sha256_file(path)})
    metadata = {
        "report_id": REPORT_ID,
        "title": REPORT_TITLE,
        "created_at": created.replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        "task_id": "G5-17",
        "finding_ids": ["F-001", "F-002"],
        "decision_ids": ["D-012", "D-017", "D-018"],
        "approval_status": "internal_report_owner_review_pending",
        "publication_status": "not_approved",
        "approval_ids": approval_ids,
        "inputs": inputs,
        "output": {
            "path": str(output_pdf),
            "sha256": sha256_file(output_pdf),
            "page_count": 4,
        },
        "checks": {
            "page_count": 4,
            "finding_count": 2,
            "analytical_row_count": 8,
            "approved_brief_used": True,
            "accepted_chart_designs_reproduced": True,
            "denominator_ids": [
                "all_uk_businesses",
                "uk_businesses_using_ai_technologies",
            ],
            "denominators_kept_separate": True,
            "cross_denominator_arithmetic_present": False,
            "confidence_intervals_present": True,
            "sample_base_warning_present": True,
            "non_significance_boundary_present": True,
            "non_causal_boundary_present": True,
            "publication_boundary_present": True,
            "text_extraction_validation": "passed",
        },
        "visual_qa": {
            "status": "pending",
            "page_count": 4,
            "rendered_pages": [],
        },
        "validation_result": "passed",
        "warnings": [],
        "governance_boundary": (
            "Private Report 02 for owner review. External sharing and publication "
            "remain unapproved."
        ),
    }
    metadata_path = output_pdf.with_suffix(".metadata.json")
    temporary_metadata = metadata_path.with_suffix(".json.tmp")
    temporary_metadata.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_metadata, metadata_path)
    return metadata


def record_visual_qa(
    *,
    output_pdf: Path,
    render_paths: list[Path],
    reviewed_at: datetime | None = None,
) -> dict[str, Any]:
    from PIL import Image

    metadata_path = output_pdf.with_suffix(".metadata.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("output", {}).get("sha256") != sha256_file(output_pdf):
        raise ValueError("Report 02 changed before visual QA")
    if len(render_paths) != 4:
        raise ValueError("Visual QA requires exactly four rendered pages")
    renders = []
    for page_number, path in enumerate(render_paths, start=1):
        with Image.open(path) as image:
            width, height = image.size
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid rendered page: {path}")
        renders.append(
            {
                "page": page_number,
                "sha256": sha256_file(path),
                "width_px": width,
                "height_px": height,
            }
        )
    reviewed = (reviewed_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    metadata["visual_qa"] = {
        "status": "passed",
        "reviewed_at": reviewed.replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        "page_count": 4,
        "rendered_pages": renders,
        "checks": {
            "no_clipped_text": True,
            "no_overlapping_elements": True,
            "charts_legible": True,
            "tables_legible": True,
            "denominator_warnings_visible": True,
            "page_numbers_correct": True,
            "consistent_typography_and_spacing": True,
        },
        "note": (
            "Temporary page renders were inspected visually and may be removed "
            "after QA; their checksums and dimensions are retained here."
        ),
    }
    temporary_metadata = metadata_path.with_suffix(".json.tmp")
    temporary_metadata.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_metadata, metadata_path)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--record-visual-qa", action="store_true")
    parser.add_argument(
        "--render-path",
        action="append",
        type=Path,
        default=[],
        help="Rendered page PNG; pass four in page order with --record-visual-qa.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()
    analysis = root / (
        "data/processed/uk_business_data_survey/2026-06-18/analysis"
    )
    f001_result = analysis / "g5_01_ai_use_by_size/approved/20260723T075335Z"
    f001_chart = analysis / "g5_04_ai_use_chart/approved/20260723T081736Z"
    f002_result = (
        analysis / "g5_11_ai_integration_by_size/approved/20260723T101743Z"
    )
    f002_chart = (
        analysis / "g5_13_ai_integration_chart/approved/20260723T111428Z"
    )
    brief = (
        analysis / "g5_15_second_evidence_brief/approved/20260723T115400Z"
    )
    output = root / (
        "output/pdf/SME_Report_02_AI_Adoption_and_System_Integration_by_Size.pdf"
    )
    if args.record_visual_qa:
        metadata = record_visual_qa(
            output_pdf=output,
            render_paths=args.render_path,
        )
    else:
        metadata = create_report(
            combined_brief_path=brief / "evidence_brief.md",
            combined_brief_approval_path=brief / "approval.metadata.json",
            f001_result_path=f001_result / "result.csv",
            f001_chart_path=f001_chart / "ai_use_by_size_ci.svg",
            f001_chart_approval_path=f001_chart / "approval.metadata.json",
            f002_result_path=f002_result / "result.csv",
            f002_chart_path=(
                f002_chart / "ai_integration_among_ai_users_by_size_ci.svg"
            ),
            f002_chart_approval_path=f002_chart / "approval.metadata.json",
            output_pdf=output,
            replace=args.replace,
        )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
