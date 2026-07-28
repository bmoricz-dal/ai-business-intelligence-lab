"""Create private Report 04 on AI use cases by business size."""

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


REPORT_ID = "report_04_ai_use_cases"
TASK_ID = "G5-22"
FINDING_ID = "F-004"
TABLE_ID = "42"
DENOMINATOR_ID = "all_uk_businesses"
DENOMINATOR = "All UK businesses within each published business-size category"
QUESTION = (
    "What purposes do UK businesses report using Artificial Intelligence-based "
    "technologies for, by published business-size group?"
)
SIZE_ORDER = ("micro", "small", "medium", "large")
ROLE_ORDER = ("primary", "primary", "primary", "reference_benchmark")
CATEGORIES = (
    (
        "summarise_or_draft",
        "Summarising or drafting",
        "To summarise or collate in-house information, draft reports or correspondence",
    ),
    (
        "research_information",
        "Research",
        "To research information (e.g. in place of a traditional search engine such as Google)",
    ),
    (
        "draft_computer_code",
        "Computer code",
        "To draft computer code",
    ),
    (
        "analyse_data_or_models",
        "Data analysis or models",
        "To analyse data or build models",
    ),
    (
        "customer_service_chatbots",
        "Customer chatbots",
        "Customer service chatbots",
    ),
    (
        "generate_images_or_videos",
        "Images or videos",
        "Generating images or videos (e.g. for marketing purposes)",
    ),
    (
        "cybersecurity_protection",
        "Cybersecurity",
        "To protect the business' systems and networks from cybersecurity threats",
    ),
)


@dataclass(frozen=True)
class UseCaseObservation:
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


def _denominator(rows: list[list[str | float | None]]) -> str:
    note = " ".join(str(value) for value in rows[3] if value not in (None, ""))
    expected = "Figures in this table are presented as percentages of all UK businesses."
    if note != expected:
        raise ValueError("Unexpected Table 42 denominator note")
    return DENOMINATOR


def extract_use_case_observations(
    central_workbook: Path,
    confidence_workbook: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> list[UseCaseObservation]:
    if enforce_registered_checksums:
        verify_registered_input(central_workbook)
        verify_registered_input(confidence_workbook)

    source_rows = read_ods_sheet(central_workbook, TABLE_ID)
    central_rows = read_ods_sheet(confidence_workbook, TABLE_ID)
    lower_rows = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_lcl")
    upper_rows = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_ucl")
    for rows in (source_rows, central_rows, lower_rows, upper_rows):
        _denominator(rows)

    source_by_label = _rows_by_label(source_rows)
    central_by_label = _rows_by_label(central_rows)
    lower_by_label = _rows_by_label(lower_rows)
    upper_by_label = _rows_by_label(upper_rows)
    observations: list[UseCaseObservation] = []

    for indicator_id, indicator_label, source_column in CATEGORIES:
        estimate_column = _find_column(central_rows[7], source_column)
        base_column = _find_column(central_rows[7], "Unweighted base")
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
                    f"Table 42 central estimate mismatch: {indicator_id}/{size_id}"
                )
            if lower_status != status or upper_status != status:
                raise ValueError(
                    f"Table 42 confidence status mismatch: {indicator_id}/{size_id}"
                )
            if not all(isinstance(value, float) for value in (estimate, lower, upper)):
                raise ValueError(
                    f"Table 42 target is not numeric: {indicator_id}/{size_id}"
                )
            raw_base = _value_at(central_row, base_column)
            source_base = _value_at(source_row, base_column)
            if not isinstance(raw_base, (int, float)) or int(raw_base) != int(
                source_base
            ):
                raise ValueError(
                    f"Table 42 base mismatch: {indicator_id}/{size_id}"
                )
            observations.append(
                UseCaseObservation(
                    source_id=SOURCE_ID,
                    dataset_id=DATASET_ID,
                    dataset_version=DATASET_VERSION,
                    table_id=TABLE_ID,
                    indicator_id=indicator_id,
                    indicator_label=indicator_label,
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


def validate_observations(observations: list[UseCaseObservation]) -> None:
    if len(observations) != len(CATEGORIES) * len(SIZE_ORDER):
        raise ValueError("Report 04 must contain 28 observations")
    for category_index, (indicator_id, _, _) in enumerate(CATEGORIES):
        group = observations[category_index * 4 : (category_index + 1) * 4]
        if tuple(item.indicator_id for item in group) != (indicator_id,) * 4:
            raise ValueError("Report 04 indicator order changed")
        if tuple(item.business_size for item in group) != SIZE_ORDER:
            raise ValueError("Report 04 business-size order changed")
        if tuple(item.scope_role for item in group) != ROLE_ORDER:
            raise ValueError("Report 04 analytical roles changed")
        for item in group:
            if item.denominator_id != DENOMINATOR_ID or item.denominator != DENOMINATOR:
                raise ValueError("Report 04 denominator changed")
            if item.source_status != "observed":
                raise ValueError("Report 04 contains a suppressed target")
            if not 0 <= item.lower_limit <= item.estimate <= item.upper_limit <= 1:
                raise ValueError("Report 04 contains an invalid interval")
            if item.sample_base <= 0:
                raise ValueError("Report 04 contains an invalid base")


def build_report_spec(observations: list[UseCaseObservation]) -> dict[str, Any]:
    validate_observations(observations)
    return {
        "report_id": REPORT_ID,
        "task_id": TASK_ID,
        "finding_id": FINDING_ID,
        "title": "How UK businesses use AI",
        "research_question": QUESTION,
        "source_table_id": TABLE_ID,
        "denominator_id": DENOMINATOR_ID,
        "denominator": DENOMINATOR,
        "rows": [asdict(item) for item in observations],
        "checks": {
            "row_count": 28,
            "indicator_count": 7,
            "size_group_count": 4,
            "confidence_intervals_present": True,
            "multi_response_warning_present": True,
            "large_business_benchmark_labelled": True,
            "formal_significance_claim_present": False,
            "causal_claim_present": False,
        },
        "governance_boundary": (
            "Private Report 04 and candidate F-004 for owner review. "
            "Publication is not approved."
        ),
    }


def _atomic_csv(path: Path, observations: list[UseCaseObservation]) -> None:
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
        raise RuntimeError("Report 04 PDF generation requires reportlab") from error
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


def _colours(rl: dict[str, Any]) -> dict[str, Any]:
    HexColor = rl["HexColor"]
    return {
        "blue": HexColor("#2F83C5"),
        "blue_dark": HexColor("#1F6699"),
        "navy": HexColor("#174564"),
        "navy_deep": HexColor("#12364F"),
        "sky": HexColor("#DFF3FF"),
        "pale": HexColor("#EEF8FF"),
        "ink": HexColor("#24455D"),
        "muted": HexColor("#587286"),
        "coral": HexColor("#C95545"),
        "gold": HexColor("#F6C95C"),
        "grid": HexColor("#C4DFEF"),
        "white": rl["white"],
    }


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
    pdf.drawRightString(page_width - 42, page_height - 31, f"REPORT 04  |  PAGE {page} OF 4")


def _footer(pdf: Any, page_width: float, colours: dict[str, Any]) -> None:
    pdf.setStrokeColor(colours["grid"])
    pdf.line(42, 34, page_width - 42, 34)
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    pdf.drawString(42, 22, "DSIT UK Business Data Survey 2026 | Table 42 | Private owner-review copy")


def _by_indicator(
    observations: list[UseCaseObservation],
) -> dict[str, list[UseCaseObservation]]:
    return {
        indicator_id: [item for item in observations if item.indicator_id == indicator_id]
        for indicator_id, _, _ in CATEGORIES
    }


def _draw_pdf(path: Path, observations: list[UseCaseObservation]) -> int:
    rl = _lazy_reportlab()
    colours = _colours(rl)
    string_width = rl["stringWidth"]
    page_width, page_height = rl["A4"]
    pdf = rl["canvas"].Canvas(str(path), pagesize=rl["A4"])
    pdf.setTitle("Report 04 - How UK businesses use AI")
    pdf.setAuthor("SME Intelligence Lab")
    grouped = _by_indicator(observations)

    _header(pdf, page_width, page_height, 1, colours)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(42, page_height - 126, "How UK businesses")
    pdf.drawString(42, page_height - 158, "use AI")
    pdf.setFillColor(colours["gold"])
    pdf.roundRect(42, page_height - 192, 194, 22, 6, stroke=0, fill=1)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(139, page_height - 185, "PRIVATE CANDIDATE - OWNER REVIEW")
    y = page_height - 228
    y = _paragraph(
        pdf,
        "This report moves beyond whether a business uses AI and examines the "
        "purposes reported across seven published use-case categories.",
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
        "Research information is the highest listed use-case point estimate in "
        "each published size group. Summarising or drafting is also prominent. "
        "The large-business benchmark is higher across all seven categories.",
        x=42,
        y=y,
        width=page_width - 84,
        font="Helvetica-Bold",
        size=12,
        leading=17,
        colour=colours["blue_dark"],
        string_width=string_width,
    )
    y -= 25
    sizes = {"micro": "Micro", "small": "Small", "medium": "Medium", "large": "Large benchmark"}
    top_cards = []
    for size in SIZE_ORDER:
        top = max(
            (item for item in observations if item.business_size == size),
            key=lambda item: item.estimate,
        )
        top_cards.append((sizes[size], top.indicator_label, f"{top.estimate*100:.1f}%"))
    card_width = (page_width - 94) / 2
    for index, (size, use_case, estimate) in enumerate(top_cards):
        row = index // 2
        column = index % 2
        x = 42 + column * (card_width + 10)
        top_y = y - row * 94
        pdf.setFillColor(colours["pale"])
        pdf.roundRect(x, top_y - 82, card_width, 82, 8, stroke=0, fill=1)
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(x + 12, top_y - 19, size)
        pdf.setFillColor(colours["blue"])
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawRightString(x + card_width - 12, top_y - 21, estimate)
        _paragraph(
            pdf,
            use_case,
            x=x + 12,
            y=top_y - 44,
            width=card_width - 24,
            font="Helvetica",
            size=8.5,
            leading=12,
            colour=colours["ink"],
            string_width=string_width,
        )
    y -= 208
    pdf.setFillColor(colours["gold"])
    pdf.roundRect(42, y - 72, page_width - 84, 72, 8, stroke=0, fill=1)
    _paragraph(
        pdf,
        "Important: Table 42 is a multiple-response question. A business can "
        "report more than one use case, so the percentages overlap and must not "
        "be added together.",
        x=54,
        y=y - 25,
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
    pdf.drawString(42, page_height - 112, "Use-case profile for the three SME groups")
    _paragraph(
        pdf,
        "Point estimates with supplied 95% confidence intervals. These are "
        "descriptive comparisons; no pairwise significance test is claimed.",
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
    )
    legend_x = 42
    for _, label, colour in legend:
        pdf.setFillColor(colour)
        pdf.circle(legend_x + 4, page_height - 175, 4, stroke=0, fill=1)
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 8)
        pdf.drawString(legend_x + 13, page_height - 178, label)
        legend_x += 82
    chart_x0 = 190
    chart_x1 = page_width - 48
    chart_width = chart_x1 - chart_x0
    axis_top = page_height - 215
    pdf.setStrokeColor(colours["grid"])
    pdf.setFillColor(colours["muted"])
    pdf.setFont("Helvetica", 7)
    for tick in (0, 10, 20, 30, 40, 50, 60):
        x = chart_x0 + chart_width * tick / 60
        pdf.line(x, axis_top + 5, x, axis_top - 430)
        pdf.drawCentredString(x, axis_top + 11, f"{tick}%")
    for category_index, (indicator_id, label, _) in enumerate(CATEGORIES):
        centre_y = axis_top - 35 - category_index * 58
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 8)
        for line_index, line in enumerate(_wrap(label, "Helvetica", 8, 130, string_width)):
            pdf.drawString(42, centre_y + 7 - line_index * 10, line)
        for offset, (size, _, colour) in zip((12, 0, -12), legend):
            item = next(
                row for row in grouped[indicator_id] if row.business_size == size
            )
            row_y = centre_y + offset
            low = chart_x0 + chart_width * (item.lower_limit * 100) / 60
            high = chart_x0 + chart_width * (item.upper_limit * 100) / 60
            point = chart_x0 + chart_width * (item.estimate * 100) / 60
            pdf.setStrokeColor(colour)
            pdf.setLineWidth(1.8)
            pdf.line(low, row_y, high, row_y)
            pdf.setFillColor(colour)
            pdf.circle(point, row_y, 3.4, stroke=0, fill=1)
    _paragraph(
        pdf,
        "Research and summarising/drafting have the highest point estimates "
        "within each SME group. Coding, chatbots and cybersecurity uses have "
        "lower point estimates, but the supplied intervals overlap for some "
        "comparisons.",
        x=42,
        y=page_height - 690,
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
    pdf.drawString(42, page_height - 112, "Exact estimates and intervals")
    _paragraph(
        pdf,
        "Percentage of all UK businesses in each published size group. "
        "Large businesses are a reference benchmark.",
        x=42,
        y=page_height - 138,
        width=page_width - 84,
        font="Helvetica",
        size=9,
        leading=13,
        colour=colours["muted"],
        string_width=string_width,
    )
    y = page_height - 188
    columns = (42, 220, 310, 400, 490)
    pdf.setFillColor(colours["sky"])
    pdf.rect(42, y - 5, page_width - 84, 24, stroke=0, fill=1)
    headings = ("Use case", "Micro", "Small", "Medium", "Large*")
    for x, heading in zip(columns, headings):
        pdf.setFillColor(colours["navy"])
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(x, y + 3, heading)
    y -= 27
    for indicator_id, label, _ in CATEGORIES:
        rows = grouped[indicator_id]
        pdf.setFillColor(colours["ink"])
        pdf.setFont("Helvetica", 7.5)
        label_lines = _wrap(label, "Helvetica", 7.5, 165, string_width)
        for index, line in enumerate(label_lines):
            pdf.drawString(columns[0], y - index * 10, line)
        for x, size in zip(columns[1:], SIZE_ORDER):
            item = next(row for row in rows if row.business_size == size)
            pdf.setFont("Helvetica-Bold", 7.2)
            pdf.drawString(x, y, f"{item.estimate*100:.1f}%")
            pdf.setFont("Helvetica", 6.4)
            pdf.drawString(
                x,
                y - 11,
                f"{item.lower_limit*100:.1f}-{item.upper_limit*100:.1f}",
            )
        pdf.setStrokeColor(colours["grid"])
        pdf.line(42, y - 23, page_width - 42, y - 23)
        y -= 55
    y -= 5
    pdf.setFillColor(colours["pale"])
    pdf.roundRect(42, y - 102, page_width - 84, 102, 8, stroke=0, fill=1)
    pdf.setFillColor(colours["navy"])
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(54, y - 20, "Rounded unweighted respondent bases")
    bases = {
        size: next(item for item in observations if item.business_size == size).sample_base
        for size in SIZE_ORDER
    }
    pdf.setFillColor(colours["ink"])
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(
        54,
        y - 43,
        f"Micro {bases['micro']:,}  |  Small {bases['small']:,}  |  "
        f"Medium {bases['medium']:,}  |  Large {bases['large']:,}",
    )
    _paragraph(
        pdf,
        "Bases are survey respondents, not business counts. *Large is a "
        "benchmark outside the primary SME scope. Intervals shown beneath "
        "each estimate are supplied 95% confidence intervals.",
        x=54,
        y=y - 65,
        width=page_width - 108,
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
    pdf.drawString(42, page_height - 112, "How this supports deeper research")
    y = page_height - 150
    sections = (
        (
            "A reusable use-case baseline",
            "The seven categories create a general map that can later be "
            "repeated for technology, accounting, financial services and other "
            "sectors where sample bases and suppression permit.",
        ),
        (
            "What the pattern suggests",
            "The point estimates indicate that information work - especially "
            "research and summarising/drafting - is prominent across business "
            "sizes. This is a descriptive pattern, not evidence of effectiveness "
            "or business impact.",
        ),
        (
            "What must not be inferred",
            "The categories overlap because businesses could select more than "
            "one purpose. Percentages must not be summed. The survey does not "
            "measure frequency, quality, productivity, return on investment or "
            "causal effects.",
        ),
        (
            "Evidence trail",
            "Department for Science, Innovation and Technology, UK Business "
            "Data Survey 2026, Table 42. Fieldwork: 10 October 2025 to 28 "
            "January 2026. Central estimates, supplied 95% confidence limits "
            "and rounded unweighted bases are retained.",
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
        "Review boundary: candidate F-004 remains private until the complete "
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
            "Refusing to overwrite Report 04 output: "
            + ", ".join(str(path) for path in existing)
        )
    observations = extract_use_case_observations(
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
            "Multiple-response use-case percentages overlap and must not be summed."
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
        raise ValueError("Visual QA page count does not match Report 04")
    if not checks or not all(checks.values()):
        raise ValueError("Report 04 visual QA contains a failed check")
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
        / "g5_22_ai_use_cases_by_size",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "output/pdf/SME_Report_04_How_UK_Businesses_Use_AI.pdf",
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
