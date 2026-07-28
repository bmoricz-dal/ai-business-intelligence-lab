"""Create private Report 05 on operational AI adoption pathways."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from src.reporting.report_04_ai_use_cases import (
    _colours,
    _lazy_reportlab,
    _paragraph,
    _wrap,
)
from src.transformation.ukbds import (
    DATASET_ID,
    DATASET_VERSION,
    PERIOD,
    SIZE_LABELS,
    SOURCE_ID,
    _find_column,
    _numeric_or_status,
    _rows_by_label,
    _value_at,
    read_ods_sheet,
    verify_registered_input,
)


REPORT_ID = "report_05_adoption_pathways"
TASK_ID = "G5-23"
FINDING_ID = "F-005"
SIZE_ORDER = ("micro", "small", "medium", "large")
ROLE_ORDER = ("primary", "primary", "primary", "reference_benchmark")
AI_USER_DENOMINATOR_ID = "uk_businesses_using_ai_technologies"
AI_USER_DENOMINATOR = "UK businesses that use Artificial Intelligence technologies"
ALL_BUSINESS_DENOMINATOR_ID = "all_uk_businesses"
ALL_BUSINESS_DENOMINATOR = (
    "All UK businesses within each published business-size category"
)
QUESTION = (
    "Which operational AI adoption pathways are visible in the published data "
    "after initial AI use, by business size?"
)
INDICATORS = (
    (
        "system_integration",
        "System integration",
        "48",
        "Yes",
        AI_USER_DENOMINATOR_ID,
        AI_USER_DENOMINATOR,
    ),
    (
        "automated_decision_making",
        "Automated decision-making",
        "43",
        "Yes",
        AI_USER_DENOMINATOR_ID,
        AI_USER_DENOMINATOR,
    ),
    (
        "ai_policy_guidance",
        "AI policy or guidance",
        "50",
        "Yes",
        AI_USER_DENOMINATOR_ID,
        AI_USER_DENOMINATOR,
    ),
    (
        "ai_development_training",
        "In-house AI development/training",
        "47",
        "Artificial Intelligence (e.g. machine learning models, generative AI)",
        ALL_BUSINESS_DENOMINATOR_ID,
        ALL_BUSINESS_DENOMINATOR,
    ),
)


@dataclass(frozen=True)
class PathwayObservation:
    source_id: str
    dataset_id: str
    dataset_version: str
    table_id: str
    indicator_id: str
    indicator_label: str
    period: str
    denominator_id: str
    denominator: str
    business_size: str
    source_business_size_label: str
    scope_role: str
    estimate: float
    lower_limit: float
    upper_limit: float
    sample_base: int
    source_status: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_denominator(
    rows: list[list[str | float | None]], denominator_id: str
) -> None:
    note = " ".join(str(value) for value in rows[3] if value not in (None, ""))
    expected = {
        AI_USER_DENOMINATOR_ID: (
            "Figures in this table are presented as percentages of UK businesses "
            "that use Artificial Intelligence technologies."
        ),
        ALL_BUSINESS_DENOMINATOR_ID: (
            "Figures in this table are presented as percentages of all UK businesses."
        ),
    }[denominator_id]
    if note != expected:
        raise ValueError(f"Unexpected denominator note: {note}")


def extract_pathway_observations(
    central_workbook: Path,
    confidence_workbook: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> list[PathwayObservation]:
    if enforce_registered_checksums:
        verify_registered_input(central_workbook)
        verify_registered_input(confidence_workbook)
    observations: list[PathwayObservation] = []
    for (
        indicator_id,
        indicator_label,
        table_id,
        source_column,
        denominator_id,
        denominator,
    ) in INDICATORS:
        source_rows = read_ods_sheet(central_workbook, table_id)
        central_rows = read_ods_sheet(confidence_workbook, table_id)
        lower_rows = read_ods_sheet(confidence_workbook, f"{table_id}_lcl")
        upper_rows = read_ods_sheet(confidence_workbook, f"{table_id}_ucl")
        for rows in (source_rows, central_rows, lower_rows, upper_rows):
            _check_denominator(rows, denominator_id)
        estimate_column = _find_column(central_rows[7], source_column)
        base_column = _find_column(central_rows[7], "Unweighted base")
        source_by_label = _rows_by_label(source_rows)
        central_by_label = _rows_by_label(central_rows)
        lower_by_label = _rows_by_label(lower_rows)
        upper_by_label = _rows_by_label(upper_rows)
        for source_label, (size_id, scope_role) in SIZE_LABELS.items():
            source_row = source_by_label[source_label]
            central_row = central_by_label[source_label]
            lower_row = lower_by_label[source_label]
            upper_row = upper_by_label[source_label]
            estimate, status = _numeric_or_status(_value_at(central_row, estimate_column))
            source_estimate, source_status = _numeric_or_status(
                _value_at(source_row, estimate_column)
            )
            lower, lower_status = _numeric_or_status(
                _value_at(lower_row, estimate_column)
            )
            upper, upper_status = _numeric_or_status(
                _value_at(upper_row, estimate_column)
            )
            if (source_estimate, source_status) != (estimate, status):
                raise ValueError(
                    f"Central estimate mismatch: {indicator_id}/{size_id}"
                )
            if lower_status != status or upper_status != status:
                raise ValueError(
                    f"Confidence status mismatch: {indicator_id}/{size_id}"
                )
            if not all(isinstance(value, float) for value in (estimate, lower, upper)):
                raise ValueError(f"Target is not numeric: {indicator_id}/{size_id}")
            raw_base = _value_at(central_row, base_column)
            source_base = _value_at(source_row, base_column)
            if not isinstance(raw_base, (int, float)) or int(raw_base) != int(
                source_base
            ):
                raise ValueError(f"Base mismatch: {indicator_id}/{size_id}")
            observations.append(
                PathwayObservation(
                    source_id=SOURCE_ID,
                    dataset_id=DATASET_ID,
                    dataset_version=DATASET_VERSION,
                    table_id=table_id,
                    indicator_id=indicator_id,
                    indicator_label=indicator_label,
                    period=PERIOD,
                    denominator_id=denominator_id,
                    denominator=denominator,
                    business_size=size_id,
                    source_business_size_label=source_label,
                    scope_role=scope_role,
                    estimate=estimate,
                    lower_limit=lower,
                    upper_limit=upper,
                    sample_base=int(raw_base),
                    source_status=status,
                )
            )
    validate_observations(observations)
    return observations


def validate_observations(observations: list[PathwayObservation]) -> None:
    if len(observations) != 16:
        raise ValueError("Report 05 must contain 16 observations")
    for indicator_index, indicator in enumerate(INDICATORS):
        indicator_id, _, table_id, _, denominator_id, denominator = indicator
        group = observations[indicator_index * 4 : (indicator_index + 1) * 4]
        if tuple(item.indicator_id for item in group) != (indicator_id,) * 4:
            raise ValueError("Report 05 indicator order changed")
        if tuple(item.business_size for item in group) != SIZE_ORDER:
            raise ValueError("Report 05 business-size order changed")
        if tuple(item.scope_role for item in group) != ROLE_ORDER:
            raise ValueError("Report 05 analytical roles changed")
        for item in group:
            if (
                item.table_id != table_id
                or item.denominator_id != denominator_id
                or item.denominator != denominator
            ):
                raise ValueError("Report 05 table or denominator changed")
            if item.source_status != "observed":
                raise ValueError("Report 05 contains a suppressed target")
            if not 0 <= item.lower_limit <= item.estimate <= item.upper_limit <= 1:
                raise ValueError("Report 05 contains an invalid interval")
            if item.sample_base <= 0:
                raise ValueError("Report 05 contains an invalid base")


def build_report_spec(observations: list[PathwayObservation]) -> dict[str, Any]:
    validate_observations(observations)
    return {
        "report_id": REPORT_ID,
        "task_id": TASK_ID,
        "finding_id": FINDING_ID,
        "title": "Operational AI adoption pathways",
        "research_question": QUESTION,
        "source_table_ids": ["43", "47", "48", "50"],
        "rows": [asdict(item) for item in observations],
        "checks": {
            "row_count": 16,
            "indicator_count": 4,
            "denominator_count": 2,
            "denominators_separated": True,
            "confidence_intervals_present": True,
            "large_business_benchmark_labelled": True,
            "composite_score_present": False,
            "formal_significance_claim_present": False,
            "causal_claim_present": False,
        },
        "governance_boundary": (
            "Private Report 05 and candidate F-005 for owner review. "
            "Publication is not approved."
        ),
    }


def _atomic_csv(path: Path, observations: list[PathwayObservation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(observations[0]))
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as temporary:
        writer = csv.DictWriter(temporary, fieldnames=fields)
        writer.writeheader()
        writer.writerows(asdict(item) for item in observations)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        json.dump(payload, temporary, indent=2, sort_keys=True)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def _header(
    pdf: Any,
    page_width: float,
    page_height: float,
    page: int,
    colours: dict[str, Any],
) -> None:
    pdf.setFillColor(colours["sky"])
    pdf.rect(0, page_height - 76, page_width, 76, stroke=0, fill=1)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(42, page_height - 31, "SME INTELLIGENCE LAB")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(page_width - 42, page_height - 31, f"REPORT 05  |  PAGE {page} OF 4")


def _footer(pdf: Any, page_width: float, colours: dict[str, Any]) -> None:
    pdf.setStrokeColor(colours["grid"])
    pdf.line(42, 34, page_width - 42, 34)
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    pdf.drawString(42, 22, "DSIT UK Business Data Survey 2026 | Tables 43, 47, 48 and 50 | Private owner-review copy")


def _grouped(
    observations: list[PathwayObservation],
) -> dict[str, list[PathwayObservation]]:
    return {
        indicator_id: [item for item in observations if item.indicator_id == indicator_id]
        for indicator_id, *_ in INDICATORS
    }


def _draw_pdf(path: Path, observations: list[PathwayObservation]) -> int:
    rl = _lazy_reportlab()
    colours = _colours(rl)
    string_width = rl["stringWidth"]
    page_width, page_height = rl["A4"]
    pdf = rl["canvas"].Canvas(str(path), pagesize=rl["A4"])
    pdf.setTitle("Report 05 - Operational AI adoption pathways")
    pdf.setAuthor("SME Intelligence Lab")
    grouped = _grouped(observations)

    _header(pdf, page_width, page_height, 1, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawString(42, page_height - 126, "Operational AI")
    pdf.drawString(42, page_height - 158, "adoption pathways")
    pdf.setFillColor(colours["gold"])
    pdf.roundRect(42, page_height - 192, 194, 22, 6, stroke=0, fill=1)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(139, page_height - 185, "PRIVATE CANDIDATE - OWNER REVIEW")
    y = page_height - 230
    y = _paragraph(
        pdf,
        "This report maps four distinct operational choices visible in the "
        "published survey: integration, automated decisions, in-house "
        "development or training, and governance.",
        x=42,
        y=y,
        width=page_width - 84,
        font="Helvetica",
        size=11,
        leading=16,
        colour=colours["ink"],
        string_width=string_width,
    )
    y -= 22
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(42, y, "Key descriptive pattern")
    y -= 22
    y = _paragraph(
        pdf,
        "Among AI-using SMEs, system integration and policy/guidance have "
        "higher point estimates than automated decision-making. In-house AI "
        "development or training is less common when measured across all "
        "businesses.",
        x=42,
        y=y,
        width=page_width - 84,
        font="Helvetica-Bold",
        size=12,
        leading=17,
        colour=colours["blue_dark"],
        string_width=string_width,
    )
    y -= 28
    cards = (
        ("INTEGRATE", "AI users", "Connect AI tools to business systems"),
        ("AUTOMATE", "AI users", "Use automated decision-making systems"),
        ("BUILD", "All businesses", "Use data to develop or train AI"),
        ("GOVERN", "AI users", "Put policy or guidance in place"),
    )
    card_width = (page_width - 94) / 2
    for index, (label, denominator, meaning) in enumerate(cards):
        row = index // 2
        column = index % 2
        x = 42 + column * (card_width + 10)
        top_y = y - row * 110
        pdf.setFillColor(colours["pale"])
        pdf.roundRect(x, top_y - 96, card_width, 96, 8, stroke=0, fill=1)
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x + 12, top_y - 20, label)
        pdf.setFillColor(colours["blue"])
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(x + 12, top_y - 40, denominator)
        _paragraph(
            pdf,
            meaning,
            x=x + 12,
            y=top_y - 61,
            width=card_width - 24,
            font="Helvetica",
            size=8.5,
            leading=12,
            colour=colours["ink"],
            string_width=string_width,
        )
    y -= 245
    pdf.setFillColor(colours["gold"])
    pdf.roundRect(42, y - 76, page_width - 84, 76, 8, stroke=0, fill=1)
    _paragraph(
        pdf,
        "Denominator rule: integration, automated decisions and governance "
        "describe businesses already using AI. Development/training describes "
        "all businesses. The measures are shown separately and are not combined "
        "into a score.",
        x=54,
        y=y - 24,
        width=page_width - 108,
        font="Helvetica-Bold",
        size=9,
        leading=14,
        colour=colours["navy"],
        string_width=string_width,
    )
    _footer(pdf, page_width, colours)
    pdf.showPage()

    _header(pdf, page_width, page_height, 2, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(42, page_height - 112, "Operational pathways among AI users")
    _paragraph(
        pdf,
        "Three indicators with the same conditional denominator: UK businesses "
        "that use AI technologies. Point estimates include supplied 95% intervals.",
        x=42,
        y=page_height - 138,
        width=page_width - 84,
        font="Helvetica",
        size=9,
        leading=13,
        colour=colours["muted"],
        string_width=string_width,
    )
    legend = (
        ("micro", "Micro", colours["blue"]),
        ("small", "Small", colours["blue_dark"]),
        ("medium", "Medium", colours["navy_deep"]),
        ("large", "Large benchmark", colours["coral"]),
    )
    legend_x = 42
    for size, label, colour in legend:
        pdf.setFillColor(colour)
        if size == "large":
            pdf.rect(legend_x, page_height - 180, 8, 8, stroke=0, fill=1)
        else:
            pdf.circle(legend_x + 4, page_height - 176, 4, stroke=0, fill=1)
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(legend_x + 13, page_height - 179, label)
        legend_x += 105 if size != "large" else 120
    chart_x0 = 190
    chart_x1 = page_width - 48
    chart_width = chart_x1 - chart_x0
    axis_top = page_height - 225
    pdf.setStrokeColor(colours["grid"])
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    for tick in (0, 20, 40, 60, 80):
        x = chart_x0 + chart_width * tick / 80
        pdf.line(x, axis_top + 6, x, axis_top - 260)
        pdf.drawCentredString(x, axis_top + 12, f"{tick}%")
    ai_user_indicators = (
        ("system_integration", "System integration"),
        ("automated_decision_making", "Automated decisions"),
        ("ai_policy_guidance", "Policy or guidance"),
    )
    for indicator_index, (indicator_id, label) in enumerate(ai_user_indicators):
        centre_y = axis_top - 52 - indicator_index * 86
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 8.5)
        pdf.drawString(42, centre_y + 4, label)
        for offset, (size, _, colour) in zip((20, 7, -6, -19), legend):
            item = next(
                row for row in grouped[indicator_id] if row.business_size == size
            )
            row_y = centre_y + offset
            low = chart_x0 + chart_width * (item.lower_limit * 100) / 80
            high = chart_x0 + chart_width * (item.upper_limit * 100) / 80
            point = chart_x0 + chart_width * (item.estimate * 100) / 80
            pdf.setStrokeColor(colour)
            pdf.setLineWidth(1.8)
            pdf.line(low, row_y, high, row_y)
            pdf.setFillColor(colour)
            if size == "large":
                pdf.rect(point - 3.5, row_y - 3.5, 7, 7, stroke=0, fill=1)
            else:
                pdf.circle(point, row_y, 3.4, stroke=0, fill=1)
    y = page_height - 540
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Point estimates")
    y -= 21
    columns = (42, 218, 300, 382, 464)
    pdf.setFillColor(colours["sky"])
    pdf.rect(42, y - 4, page_width - 84, 20, stroke=0, fill=1)
    for x, heading in zip(columns, ("Indicator", "Micro", "Small", "Medium", "Large*")):
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(x, y + 2, heading)
    y -= 24
    for indicator_id, label in ai_user_indicators:
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(columns[0], y, label)
        for x, size in zip(columns[1:], SIZE_ORDER):
            item = next(row for row in grouped[indicator_id] if row.business_size == size)
            pdf.drawString(x, y, f"{item.estimate*100:.1f}%")
        pdf.setStrokeColor(colours["grid"])
        pdf.line(42, y - 7, page_width - 42, y - 7)
        y -= 24
    _paragraph(
        pdf,
        "*Large is a benchmark. The chart retains the full supplied intervals. "
        "No pairwise significance test is claimed.",
        x=42,
        y=y - 3,
        width=page_width - 84,
        font="Helvetica",
        size=8,
        leading=12,
        colour=colours["muted"],
        string_width=string_width,
    )
    _footer(pdf, page_width, colours)
    pdf.showPage()

    _header(pdf, page_width, page_height, 3, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(42, page_height - 112, "In-house AI development or training")
    _paragraph(
        pdf,
        "Percentage of all UK businesses using data to develop, train or improve "
        "AI, including machine-learning models or generative AI.",
        x=42,
        y=page_height - 138,
        width=page_width - 84,
        font="Helvetica",
        size=9,
        leading=13,
        colour=colours["muted"],
        string_width=string_width,
    )
    rows = grouped["ai_development_training"]
    chart_x0 = 190
    chart_x1 = page_width - 55
    chart_width = chart_x1 - chart_x0
    axis_y = page_height - 220
    pdf.setStrokeColor(colours["grid"])
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    for tick in (0, 5, 10, 15, 20):
        x = chart_x0 + chart_width * tick / 20
        pdf.line(x, axis_y + 8, x, axis_y - 148)
        pdf.drawCentredString(x, axis_y + 13, f"{tick}%")
    labels = {
        "micro": "Micro (1 to 9 employees)",
        "small": "Small (10 to 49)",
        "medium": "Medium (50 to 249)",
        "large": "Large (250+) benchmark",
    }
    for index, item in enumerate(rows):
        row_y = axis_y - 22 - index * 34
        colour = colours["coral"] if item.business_size == "large" else colours["blue"]
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 8)
        pdf.drawString(42, row_y - 3, labels[item.business_size])
        low = chart_x0 + chart_width * (item.lower_limit * 100) / 20
        high = chart_x0 + chart_width * (item.upper_limit * 100) / 20
        point = chart_x0 + chart_width * (item.estimate * 100) / 20
        pdf.setStrokeColor(colour)
        pdf.setLineWidth(2.2)
        pdf.line(low, row_y, high, row_y)
        pdf.setFillColor(colour)
        if item.business_size == "large":
            pdf.rect(point - 4, row_y - 4, 8, 8, stroke=0, fill=1)
        else:
            pdf.circle(point, row_y, 4, stroke=0, fill=1)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(min(high + 6, chart_x1 - 28), row_y - 3, f"{item.estimate*100:.1f}%")
    y = axis_y - 190
    pdf.setFillColor(colours["pale"])
    pdf.roundRect(42, y - 82, page_width - 84, 82, 8, stroke=0, fill=1)
    _paragraph(
        pdf,
        "The point estimate is 3.3% for micro, 3.6% for small, 6.5% for medium "
        "and 10.5% for the large-business benchmark. This all-business measure "
        "must not be compared arithmetically with the AI-user indicators.",
        x=54,
        y=y - 25,
        width=page_width - 108,
        font="Helvetica-Bold",
        size=9,
        leading=14,
        colour=colours["navy"],
        string_width=string_width,
    )
    y -= 118
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Exact values and rounded respondent bases")
    y -= 21
    columns = (42, 236, 322, 420, 510)
    pdf.setFillColor(colours["sky"])
    pdf.rect(42, y - 4, page_width - 84, 20, stroke=0, fill=1)
    for x, heading in zip(columns, ("Size group", "Estimate", "95% interval", "Base", "Role")):
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 7.2)
        pdf.drawString(x, y + 2, heading)
    y -= 24
    for item in rows:
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 7.2)
        pdf.drawString(columns[0], y, labels[item.business_size])
        pdf.drawString(columns[1], y, f"{item.estimate*100:.1f}%")
        pdf.drawString(
            columns[2],
            y,
            f"{item.lower_limit*100:.1f}-{item.upper_limit*100:.1f}%",
        )
        pdf.drawString(columns[3], y, f"{item.sample_base:,}")
        pdf.drawString(columns[4], y, "Benchmark" if item.business_size == "large" else "SME")
        pdf.setStrokeColor(colours["grid"])
        pdf.line(42, y - 7, page_width - 42, y - 7)
        y -= 24
    _paragraph(
        pdf,
        "Rounded unweighted bases are survey respondents, not numbers of UK businesses.",
        x=42,
        y=y - 5,
        width=page_width - 84,
        font="Helvetica",
        size=8,
        leading=12,
        colour=colours["muted"],
        string_width=string_width,
    )
    _footer(pdf, page_width, colours)
    pdf.showPage()

    _header(pdf, page_width, page_height, 4, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(42, page_height - 112, "A framework, not a maturity ladder")
    y = page_height - 150
    sections = (
        (
            "Why these are pathways",
            "Businesses may adopt AI through task-focused tools, system "
            "integration, automated decisions, in-house development or formal "
            "governance. The survey does not establish a single required order.",
        ),
        (
            "What the evidence supports",
            "The point estimates provide a general business-size baseline. They "
            "can later support separate pathway reports and cautious sector cuts "
            "where the sample and suppression rules permit.",
        ),
        (
            "What the evidence does not support",
            "No readiness score, maturity score or causal sequence is calculated. "
            "The report does not measure effectiveness, return on investment or "
            "whether integration, automation, development or governance is "
            "appropriate for an individual business.",
        ),
        (
            "Evidence trail",
            "Department for Science, Innovation and Technology, UK Business "
            "Data Survey 2026, Tables 43, 47, 48 and 50. Fieldwork: 10 October "
            "2025 to 28 January 2026. Central estimates, supplied 95% confidence "
            "limits and rounded unweighted bases are retained.",
        ),
    )
    for heading, body in sections:
        pdf.setFillColor(colours["pale"])
        pdf.roundRect(42, y - 105, page_width - 84, 105, 8, stroke=0, fill=1)
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(54, y - 20, heading)
        _paragraph(
            pdf,
            body,
            x=54,
            y=y - 43,
            width=page_width - 108,
            font="Helvetica",
            size=9,
            leading=13,
            colour=colours["ink"],
            string_width=string_width,
        )
        y -= 118
    pdf.setFillColor(colours["gold"])
    pdf.roundRect(42, y - 56, page_width - 84, 56, 8, stroke=0, fill=1)
    _paragraph(
        pdf,
        "Review boundary: candidate F-005 remains private until the complete "
        "five-report and website review is accepted.",
        x=54,
        y=y - 23,
        width=page_width - 108,
        font="Helvetica-Bold",
        size=9,
        leading=13,
        colour=colours["navy"],
        string_width=string_width,
    )
    _footer(pdf, page_width, colours)
    pdf.save()
    return 4


def generate_report(
    output_pdf: Path,
    *,
    central_workbook: Path,
    confidence_workbook: Path,
    analysis_directory: Path,
    replace: bool = False,
) -> dict[str, Any]:
    metadata_path = output_pdf.with_suffix(".metadata.json")
    result_csv = analysis_directory / "result.csv"
    existing = [path for path in (output_pdf, metadata_path, result_csv) if path.exists()]
    if existing and not replace:
        raise FileExistsError(
            "Refusing to overwrite Report 05 output: "
            + ", ".join(str(path) for path in existing)
        )
    observations = extract_pathway_observations(
        central_workbook, confidence_workbook
    )
    spec = build_report_spec(observations)
    _atomic_csv(result_csv, observations)
    page_count = _draw_pdf(output_pdf, observations)
    metadata = {
        **spec,
        "created_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "approval_status": "candidate_finding_owner_review_pending",
        "publication_status": "not_approved",
        "validation_result": "passed",
        "inputs": [
            {"path": str(central_workbook), "sha256": sha256_file(central_workbook)},
            {
                "path": str(confidence_workbook),
                "sha256": sha256_file(confidence_workbook),
            },
        ],
        "analysis_output": {"path": str(result_csv), "sha256": sha256_file(result_csv)},
        "output": {
            "path": str(output_pdf),
            "sha256": sha256_file(output_pdf),
            "page_count": page_count,
        },
        "visual_qa": {"status": "pending", "rendered_pages": [], "checks": {}},
        "warnings": [
            "All-business and AI-user indicators are separated and must not be combined.",
            "No readiness or maturity score is calculated.",
        ],
    }
    _atomic_json(metadata_path, metadata)
    return metadata


def record_visual_qa(
    metadata_path: Path,
    rendered_pages: list[dict[str, Any]],
    *,
    checks: dict[str, bool],
) -> dict[str, Any]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if len(rendered_pages) != metadata["output"]["page_count"]:
        raise ValueError("Visual QA page count does not match Report 05")
    if not checks or not all(checks.values()):
        raise ValueError("Report 05 visual QA contains a failed check")
    metadata["visual_qa"] = {
        "status": "passed",
        "reviewed_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "rendered_pages": rendered_pages,
        "checks": checks,
    }
    _atomic_json(metadata_path, metadata)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    raw = root / "data/raw/dsit/uk_business_data_survey/2026-06-18"
    parser.add_argument(
        "--central-workbook",
        type=Path,
        default=raw / "DSIT_UK_Business_Data_Survey_2026_tables.ods",
    )
    parser.add_argument(
        "--confidence-workbook",
        type=Path,
        default=raw
        / "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods",
    )
    parser.add_argument(
        "--analysis-directory",
        type=Path,
        default=root
        / "data/processed/uk_business_data_survey/2026-06-18/analysis"
        / "g5_23_operational_ai_pathways",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "output/pdf/SME_Report_05_Operational_AI_Adoption_Pathways.pdf",
    )
    parser.add_argument("--replace", action="store_true")
    arguments = parser.parse_args()
    metadata = generate_report(
        arguments.output,
        central_workbook=arguments.central_workbook,
        confidence_workbook=arguments.confidence_workbook,
        analysis_directory=arguments.analysis_directory,
        replace=arguments.replace,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
