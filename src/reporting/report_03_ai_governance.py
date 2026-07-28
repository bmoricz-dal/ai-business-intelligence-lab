"""Create private Report 03 on AI policy adoption by business size.

The source is UK Business Data Survey 2026 Table 50. The measure is
conditional on businesses that report using AI technologies and must never be
presented as a percentage of all UK businesses.
"""

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


REPORT_ID = "report_03_ai_governance"
TASK_ID = "G5-19"
FINDING_ID = "F-003"
TABLE_ID = "50"
INDICATOR_ID = "ai_policy_or_guidance_among_ai_users"
DENOMINATOR_ID = "uk_businesses_using_ai_technologies"
DENOMINATOR = "UK businesses that use Artificial Intelligence technologies"
QUESTION = (
    "Among UK businesses that use AI technologies, what proportion have a "
    "formal or informal policy or guidance regarding AI use or development, "
    "by published business-size group?"
)
SIZE_ORDER = ("micro", "small", "medium", "large")
ROLE_ORDER = ("primary", "primary", "primary", "reference_benchmark")


@dataclass(frozen=True)
class PolicyObservation:
    source_id: str
    dataset_id: str
    dataset_version: str
    table_id: str
    indicator_id: str
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


def _table_denominator(rows: list[list[str | float | None]]) -> str:
    if len(rows) < 8:
        raise ValueError("Table 50 does not contain the expected header")
    note = " ".join(str(value) for value in rows[3] if value not in (None, ""))
    expected = (
        "Figures in this table are presented as percentages of UK businesses "
        "that use Artificial Intelligence technologies."
    )
    if note != expected:
        raise ValueError("Unexpected Table 50 denominator note")
    return DENOMINATOR


def extract_policy_observations(
    central_workbook: Path,
    confidence_workbook: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> list[PolicyObservation]:
    if enforce_registered_checksums:
        verify_registered_input(central_workbook)
        verify_registered_input(confidence_workbook)

    source_rows = read_ods_sheet(central_workbook, TABLE_ID)
    central_rows = read_ods_sheet(confidence_workbook, TABLE_ID)
    lower_rows = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_lcl")
    upper_rows = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_ucl")
    for rows in (source_rows, central_rows, lower_rows, upper_rows):
        _table_denominator(rows)

    header = central_rows[7]
    estimate_column = _find_column(header, "Yes")
    base_column = _find_column(header, "Unweighted base")
    source_by_label = _rows_by_label(source_rows)
    central_by_label = _rows_by_label(central_rows)
    lower_by_label = _rows_by_label(lower_rows)
    upper_by_label = _rows_by_label(upper_rows)

    observations: list[PolicyObservation] = []
    for source_label, (size_id, scope_role) in SIZE_LABELS.items():
        try:
            source_row = source_by_label[source_label]
            central_row = central_by_label[source_label]
            lower_row = lower_by_label[source_label]
            upper_row = upper_by_label[source_label]
        except KeyError as error:
            raise ValueError(f"Required Table 50 row not found: {source_label}") from error

        estimate, status = _numeric_or_status(_value_at(central_row, estimate_column))
        source_estimate, source_status = _numeric_or_status(
            _value_at(source_row, estimate_column)
        )
        lower, lower_status = _numeric_or_status(_value_at(lower_row, estimate_column))
        upper, upper_status = _numeric_or_status(_value_at(upper_row, estimate_column))
        if source_estimate != estimate or source_status != status:
            raise ValueError(f"Central estimate mismatch for {source_label}")
        if lower_status != status or upper_status != status:
            raise ValueError(f"Confidence-limit status mismatch for {source_label}")
        if not all(isinstance(value, float) for value in (estimate, lower, upper)):
            raise ValueError(f"Table 50 target value is not numeric for {source_label}")

        raw_base = _value_at(central_row, base_column)
        source_base = _value_at(source_row, base_column)
        if not isinstance(raw_base, (int, float)) or not isinstance(
            source_base, (int, float)
        ):
            raise ValueError(f"Missing Table 50 sample base for {source_label}")
        if int(raw_base) != int(source_base):
            raise ValueError(f"Table 50 sample-base mismatch for {source_label}")

        observations.append(
            PolicyObservation(
                source_id=SOURCE_ID,
                dataset_id=DATASET_ID,
                dataset_version=DATASET_VERSION,
                table_id=TABLE_ID,
                indicator_id=INDICATOR_ID,
                period=PERIOD,
                denominator_id=DENOMINATOR_ID,
                denominator=DENOMINATOR,
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


def validate_observations(observations: list[PolicyObservation]) -> None:
    if tuple(item.business_size for item in observations) != SIZE_ORDER:
        raise ValueError("Unexpected Table 50 business-size rows")
    if tuple(item.scope_role for item in observations) != ROLE_ORDER:
        raise ValueError("Unexpected Table 50 analytical roles")
    for item in observations:
        if item.table_id != TABLE_ID or item.indicator_id != INDICATOR_ID:
            raise ValueError("Report 03 mixes source tables or indicators")
        if item.denominator_id != DENOMINATOR_ID or item.denominator != DENOMINATOR:
            raise ValueError("Report 03 changes the conditional AI-user denominator")
        if item.source_status != "observed":
            raise ValueError(f"Table 50 row is not observed: {item.business_size}")
        if not 0 <= item.lower_limit <= item.estimate <= item.upper_limit <= 1:
            raise ValueError(f"Invalid Table 50 interval for {item.business_size}")
        if item.sample_base <= 0:
            raise ValueError(f"Invalid Table 50 sample base for {item.business_size}")


def build_report_spec(observations: list[PolicyObservation]) -> dict[str, Any]:
    validate_observations(observations)
    return {
        "report_id": REPORT_ID,
        "task_id": TASK_ID,
        "finding_id": FINDING_ID,
        "title": "AI governance among AI-using businesses",
        "research_question": QUESTION,
        "source_table_id": TABLE_ID,
        "indicator_id": INDICATOR_ID,
        "denominator_id": DENOMINATOR_ID,
        "denominator": DENOMINATOR,
        "rows": [asdict(item) for item in observations],
        "checks": {
            "row_count": len(observations),
            "primary_sme_count": sum(item.scope_role == "primary" for item in observations),
            "reference_benchmark_count": sum(
                item.scope_role == "reference_benchmark" for item in observations
            ),
            "confidence_intervals_present": True,
            "conditional_denominator_visible": True,
            "all_business_conversion_present": False,
            "formal_significance_claim_present": False,
            "causal_claim_present": False,
        },
        "governance_boundary": (
            "Private Report 03 and candidate F-003 for consolidated owner review. "
            "The finding is not approved for external sharing or publication."
        ),
    }


def _atomic_csv(path: Path, observations: list[PolicyObservation]) -> None:
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


def _lazy_reportlab() -> dict[str, Any]:
    try:
        from reportlab.lib.colors import HexColor, white
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase.pdfmetrics import stringWidth
        from reportlab.pdfgen import canvas
    except ImportError as error:
        raise RuntimeError("Report 03 PDF generation requires reportlab") from error
    return {
        "HexColor": HexColor,
        "white": white,
        "A4": A4,
        "stringWidth": stringWidth,
        "canvas": canvas,
    }


def _wrap(text: str, font: str, size: float, width: float, string_width: Any) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and string_width(candidate, font, size) > width:
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
    font: str,
    size: float,
    leading: float,
    colour: Any,
    string_width: Any,
) -> float:
    pdf.setFillColor(colour)
    pdf.setFont(font, size)
    for line in _wrap(text, font, size, width, string_width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def _header(pdf: Any, page_width: float, page_height: float, page: int, colours: dict[str, Any]) -> None:
    pdf.setFillColor(colours["navy"])
    pdf.rect(0, page_height - 76, page_width, 76, stroke=0, fill=1)
    pdf.setFillColor(colours["white"])
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(42, page_height - 31, "SME INTELLIGENCE LAB")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(page_width - 42, page_height - 31, f"REPORT 03  |  PAGE {page} OF 3")


def _footer(pdf: Any, page_width: float, colours: dict[str, Any]) -> None:
    pdf.setStrokeColor(colours["grid"])
    pdf.line(42, 34, page_width - 42, 34)
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    pdf.drawString(42, 22, "DSIT UK Business Data Survey 2026 | Table 50 | Private owner-review copy")


def _draw_pdf(path: Path, observations: list[PolicyObservation]) -> int:
    rl = _lazy_reportlab()
    HexColor = rl["HexColor"]
    A4 = rl["A4"]
    string_width = rl["stringWidth"]
    canvas = rl["canvas"]
    colours = {
        "navy": HexColor("#15324A"),
        "teal": HexColor("#087E8B"),
        "rust": HexColor("#A44A3F"),
        "ink": HexColor("#273444"),
        "muted": HexColor("#5C6873"),
        "pale": HexColor("#EEF4F6"),
        "yellow": HexColor("#F4C95D"),
        "grid": HexColor("#CCD7DD"),
        "white": rl["white"],
    }
    page_width, page_height = A4
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.setTitle("Report 03 - AI governance among AI-using businesses")
    pdf.setAuthor("SME Intelligence Lab")

    _header(pdf, page_width, page_height, 1, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(42, page_height - 120, "AI governance among")
    pdf.drawString(42, page_height - 150, "AI-using businesses")
    pdf.setFillColor(colours["yellow"])
    pdf.roundRect(42, page_height - 184, 194, 22, 6, stroke=0, fill=1)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(139, page_height - 177, "PRIVATE CANDIDATE - OWNER REVIEW")

    y = page_height - 220
    y = _paragraph(
        pdf,
        "The third insight adds governance to the adoption and integration story. "
        "It asks whether businesses already using AI have any formal or informal "
        "policy or guidance for its use or development.",
        x=42,
        y=y,
        width=page_width - 84,
        font="Helvetica",
        size=11,
        leading=16,
        colour=colours["ink"],
        string_width=string_width,
    )
    y -= 18
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(42, y, "Key finding")
    y -= 22
    key = (
        "Among AI-using businesses, 20.1% of micro, 29.0% of small and 36.8% "
        "of medium businesses reported a formal or informal AI policy or guidance. "
        "The large-business reference benchmark was 67.7%."
    )
    y = _paragraph(
        pdf,
        key,
        x=42,
        y=y,
        width=page_width - 84,
        font="Helvetica-Bold",
        size=12,
        leading=17,
        colour=colours["teal"],
        string_width=string_width,
    )
    y -= 24
    cards = [
        ("ADOPTION", "All businesses", "Breadth of reported AI use"),
        ("INTEGRATION", "AI-using businesses", "Connection to business systems"),
        ("GOVERNANCE", "AI-using businesses", "Policy or guidance in place"),
    ]
    card_width = (page_width - 100) / 3
    for index, (label, denominator, meaning) in enumerate(cards):
        x = 42 + index * (card_width + 8)
        pdf.setFillColor(colours["pale"])
        pdf.roundRect(x, y - 104, card_width, 104, 8, stroke=0, fill=1)
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(x + 10, y - 18, label)
        _paragraph(
            pdf,
            denominator,
            x=x + 10,
            y=y - 39,
            width=card_width - 20,
            font="Helvetica-Bold",
            size=8,
            leading=11,
            colour=colours["teal"],
            string_width=string_width,
        )
        _paragraph(
            pdf,
            meaning,
            x=x + 10,
            y=y - 70,
            width=card_width - 20,
            font="Helvetica",
            size=8,
            leading=11,
            colour=colours["ink"],
            string_width=string_width,
        )
    y -= 138
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "How to read this")
    _paragraph(
        pdf,
        "This is a conditional measure. It says nothing about businesses that do "
        "not report using AI. The point estimates are descriptive and do not prove "
        "that size causes governance differences.",
        x=42,
        y=y - 18,
        width=page_width - 84,
        font="Helvetica",
        size=9,
        leading=13,
        colour=colours["ink"],
        string_width=string_width,
    )
    _footer(pdf, page_width, colours)
    pdf.showPage()

    _header(pdf, page_width, page_height, 2, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(42, page_height - 112, "Policy or guidance among AI users")
    _paragraph(
        pdf,
        "Percentage of UK businesses in each published size group that use AI "
        "technologies and report any formal or informal AI policy or guidance.",
        x=42,
        y=page_height - 136,
        width=page_width - 84,
        font="Helvetica",
        size=9,
        leading=13,
        colour=colours["muted"],
        string_width=string_width,
    )
    chart_x0 = 184
    chart_x1 = page_width - 50
    chart_width = chart_x1 - chart_x0
    axis_y = page_height - 205
    pdf.setStrokeColor(colours["grid"])
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    for tick in (0, 20, 40, 60, 80, 100):
        x = chart_x0 + chart_width * tick / 100
        pdf.line(x, axis_y + 8, x, axis_y - 148)
        pdf.drawCentredString(x, axis_y + 13, f"{tick}%")
    labels = {
        "micro": "Micro (1 to 9 employees)",
        "small": "Small (10 to 49)",
        "medium": "Medium (50 to 249)",
        "large": "Large (250+) benchmark",
    }
    for index, item in enumerate(observations):
        row_y = axis_y - 22 - index * 34
        colour = colours["rust"] if item.business_size == "large" else colours["teal"]
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 8)
        pdf.drawString(42, row_y - 3, labels[item.business_size])
        low = chart_x0 + chart_width * item.lower_limit
        high = chart_x0 + chart_width * item.upper_limit
        point = chart_x0 + chart_width * item.estimate
        pdf.setStrokeColor(colour)
        pdf.setLineWidth(2.5)
        pdf.line(low, row_y, high, row_y)
        pdf.setFillColor(colour)
        if item.business_size == "large":
            marker = pdf.beginPath()
            marker.moveTo(point, row_y + 6)
            marker.lineTo(point + 6, row_y)
            marker.lineTo(point, row_y - 6)
            marker.lineTo(point - 6, row_y)
            marker.close()
            pdf.drawPath(marker, stroke=0, fill=1)
        else:
            pdf.circle(point, row_y, 4.5, stroke=0, fill=1)
        value_label = f"{item.estimate*100:.1f}%"
        value_width = string_width(value_label, "Helvetica-Bold", 8)
        value_x = min(high + 7, chart_x1 - value_width)
        pdf.setFillColor(colours["white"])
        pdf.rect(value_x - 2, row_y - 6, value_width + 4, 12, stroke=0, fill=1)
        pdf.setFillColor(colour)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(value_x, row_y - 3, value_label)

    y = axis_y - 184
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(42, y, "Evidence table")
    y -= 18
    pdf.setFillColor(colours["pale"])
    pdf.rect(42, y - 2, page_width - 84, 18, stroke=0, fill=1)
    columns = (42, 264, 354, 464)
    for x, heading in zip(columns, ("Published size", "Estimate", "95% interval", "Base")):
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(x, y + 4, heading)
    y -= 20
    for item in observations:
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 8)
        pdf.drawString(columns[0], y, labels[item.business_size])
        pdf.drawString(columns[1], y, f"{item.estimate*100:.1f}%")
        pdf.drawString(
            columns[2],
            y,
            f"{item.lower_limit*100:.1f}% to {item.upper_limit*100:.1f}%",
        )
        pdf.drawString(columns[3], y, f"{item.sample_base:,}")
        pdf.setStrokeColor(colours["grid"])
        pdf.line(42, y - 6, page_width - 42, y - 6)
        y -= 23
    y -= 10
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, y, "Interpretation")
    _paragraph(
        pdf,
        "The point estimates rise across the published size groups. Within the "
        "primary SME groups, the estimate is lowest for micro businesses and "
        "highest for medium businesses. The large-business benchmark is higher "
        "than the three SME estimates. No pairwise significance test is claimed.",
        x=42,
        y=y - 18,
        width=page_width - 84,
        font="Helvetica",
        size=9,
        leading=13,
        colour=colours["ink"],
        string_width=string_width,
    )
    _footer(pdf, page_width, colours)
    pdf.showPage()

    _header(pdf, page_width, page_height, 3, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(42, page_height - 112, "What this insight supports")
    y = page_height - 150
    sections = [
        (
            "A practical message",
            "AI use does not automatically mean formal governance is in place. "
            "For SME support, policy templates and clear guidance may be useful "
            "alongside tools and technical integration.",
        ),
        (
            "What the evidence does not establish",
            "The survey does not show that business size causes policy adoption. "
            "Rounded unweighted bases are respondent counts, not numbers of UK "
            "businesses. The confidence intervals are retained, but no new "
            "pairwise significance test has been performed.",
        ),
        (
            "Why the denominator matters",
            "These percentages apply only to businesses that report using AI "
            "technologies. They must not be described as the share of all UK "
            "businesses with an AI policy and must not be multiplied by the "
            "adoption percentages without a separately approved method.",
        ),
        (
            "Evidence trail",
            "Department for Science, Innovation and Technology, UK Business Data "
            "Survey 2026, Table 50. Fieldwork ran from 10 October 2025 to "
            "28 January 2026. Central estimates, supplied 95% confidence limits "
            "and rounded unweighted bases are preserved.",
        ),
    ]
    for heading, body in sections:
        pdf.setFillColor(colours["pale"])
        pdf.roundRect(42, y - 103, page_width - 84, 103, 8, stroke=0, fill=1)
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(54, y - 20, heading)
        _paragraph(
            pdf,
            body,
            x=54,
            y=y - 42,
            width=page_width - 108,
            font="Helvetica",
            size=9,
            leading=13,
            colour=colours["ink"],
            string_width=string_width,
        )
        y -= 116
    pdf.setFillColor(colours["yellow"])
    pdf.roundRect(42, y - 58, page_width - 84, 58, 8, stroke=0, fill=1)
    _paragraph(
        pdf,
        "Review boundary: candidate F-003 remains private until the consolidated "
        "three-report and website review is accepted.",
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
    return 3


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
    existing = [
        path for path in (output_pdf, metadata_path, result_csv) if path.exists()
    ]
    if existing and not replace:
        raise FileExistsError(
            "Refusing to overwrite Report 03 output: "
            + ", ".join(str(path) for path in existing)
        )
    observations = extract_policy_observations(
        central_workbook,
        confidence_workbook,
    )
    spec = build_report_spec(observations)
    _atomic_csv(result_csv, observations)
    completed = datetime.now(timezone.utc).replace(microsecond=0)
    page_count = _draw_pdf(output_pdf, observations)
    metadata = {
        **spec,
        "created_at": completed.isoformat().replace("+00:00", "Z"),
        "approval_status": "candidate_finding_owner_review_pending",
        "publication_status": "not_approved",
        "validation_result": "passed",
        "inputs": [
            {
                "path": str(central_workbook),
                "sha256": sha256_file(central_workbook),
            },
            {
                "path": str(confidence_workbook),
                "sha256": sha256_file(confidence_workbook),
            },
        ],
        "analysis_output": {
            "path": str(result_csv),
            "sha256": sha256_file(result_csv),
        },
        "output": {
            "path": str(output_pdf),
            "sha256": sha256_file(output_pdf),
            "page_count": page_count,
        },
        "visual_qa": {
            "status": "pending",
            "rendered_pages": [],
            "checks": {},
        },
        "warnings": [],
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
        raise ValueError("Visual QA page count does not match Report 03")
    if not checks or not all(checks.values()):
        raise ValueError("Report 03 visual QA contains a failed check")
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
        default=raw / "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods",
    )
    parser.add_argument(
        "--analysis-directory",
        type=Path,
        default=(
            root
            / "data/processed/uk_business_data_survey/2026-06-18/analysis"
            / "g5_19_ai_policy_by_size"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "output/pdf/SME_Report_03_AI_Governance_by_Business_Size.pdf",
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
