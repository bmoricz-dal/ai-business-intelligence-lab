"""Create Preliminary Report 01 from the D-013-approved evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


REPORT_ID = "preliminary_report_01"
EXPECTED_RESULT_SHA256 = (
    "8f0d29ec30451fbec96aefb5aa0909e31d62c16c0e618bb75d95d809f51d8eb6"
)
EXPECTED_BRIEF_SHA256 = (
    "f353b4b0e94a49332dbb170238e9ea85c9035ef159841b1828f89905a827af31"
)
SIZE_ORDER = ("micro", "small", "medium", "large")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _wrap(text: str, font: str, size: float, width: float) -> list[str]:
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
    pdf: canvas.Canvas,
    text: str,
    *,
    x: float,
    y: float,
    width: float,
    font: str = "Helvetica",
    size: float = 9,
    leading: float = 12,
    colour: Color = HexColor("#273444"),
) -> float:
    pdf.setFillColor(colour)
    pdf.setFont(font, size)
    for line in _wrap(text, font, size, width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def _load_inputs(
    result_path: Path,
    approved_brief_path: Path,
    brief_approval_path: Path,
) -> list[dict[str, Any]]:
    if sha256_file(result_path) != EXPECTED_RESULT_SHA256:
        raise ValueError("Approved F-001 result checksum mismatch")
    if sha256_file(approved_brief_path) != EXPECTED_BRIEF_SHA256:
        raise ValueError("D-013-approved brief checksum mismatch")

    approval = json.loads(brief_approval_path.read_text(encoding="utf-8"))
    if approval.get("decision_id") != "D-013":
        raise ValueError("Expected D-013 brief approval")
    if approval.get("approval_status") != "approved_for_internal_product_development":
        raise ValueError("The evidence brief is not approved for internal development")
    if approval.get("brief_bytes_unchanged") is not True:
        raise ValueError("The approved brief is not recorded as unchanged")

    with result_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if [row["business_size"] for row in rows] != list(SIZE_ORDER):
        raise ValueError("Unexpected F-001 business-size rows")
    if {row["source_table_id"] for row in rows} != {"42"}:
        raise ValueError("Preliminary Report 01 must use Table 42 only")
    return rows


def _draw_report(pdf: canvas.Canvas, rows: list[dict[str, Any]]) -> None:
    page_width, page_height = A4
    navy = HexColor("#15324A")
    teal = HexColor("#087E8B")
    benchmark = HexColor("#A44A3F")
    ink = HexColor("#273444")
    muted = HexColor("#5C6873")
    pale = HexColor("#EEF4F6")
    yellow = HexColor("#F4C95D")
    grid = HexColor("#CCD7DD")

    pdf.setTitle("Preliminary Report 01 - Reported AI use by business size")
    pdf.setAuthor("SME Intelligence Lab")
    pdf.setSubject("Internal preliminary evidence report based on UKBDS 2026")

    pdf.setFillColor(navy)
    pdf.rect(0, page_height - 105, page_width, 105, stroke=0, fill=1)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(46, page_height - 37, "SME INTELLIGENCE LAB")
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(46, page_height - 70, "Preliminary insight 01")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(46, page_height - 91, "Reported AI use by business size")

    pdf.setFillColor(yellow)
    pdf.roundRect(46, page_height - 133, 142, 20, 6, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(117, page_height - 126, "INTERNAL - NOT FOR PUBLICATION")
    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(
        page_width - 46,
        page_height - 126,
        "Report 01 | UKBDS 2026 | D-013",
    )

    y = page_height - 164
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(46, y, "Key message")
    y -= 18
    key_message = (
        "Reported use of at least one listed AI-based technology was 37.4% for "
        "micro businesses, 50.8% for small businesses and 57.1% for medium "
        "businesses. The large-business reference benchmark was 78.2%."
    )
    y = _paragraph(pdf, key_message, x=46, y=y, width=page_width - 92, size=10, leading=14)
    y -= 8

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(46, y, "Estimates and supplied 95% confidence intervals")
    y -= 18

    label_x = 46
    chart_x0 = 176
    chart_x1 = page_width - 52
    chart_width = chart_x1 - chart_x0
    axis_y = y - 6
    pdf.setStrokeColor(grid)
    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 7)
    for tick in (0, 25, 50, 75, 100):
        x = chart_x0 + chart_width * tick / 100
        pdf.line(x, axis_y, x, axis_y - 108)
        pdf.drawCentredString(x, axis_y + 4, f"{tick}%")

    display_labels = {
        "micro": "Micro (1 to 9 employees)",
        "small": "Small (10 to 49)",
        "medium": "Medium (50 to 249)",
        "large": "Large (250+) benchmark",
    }
    for index, row in enumerate(rows):
        row_y = axis_y - 22 - index * 25
        estimate = float(row["estimate_percent"])
        lower = float(row["lower_limit_percent"])
        upper = float(row["upper_limit_percent"])
        colour = benchmark if row["business_size"] == "large" else teal

        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(label_x, row_y - 3, display_labels[row["business_size"]])
        x_lower = chart_x0 + chart_width * lower / 100
        x_upper = chart_x0 + chart_width * upper / 100
        x_estimate = chart_x0 + chart_width * estimate / 100
        pdf.setStrokeColor(colour)
        pdf.setLineWidth(2.5)
        pdf.line(x_lower, row_y, x_upper, row_y)
        pdf.setFillColor(colour)
        if row["business_size"] == "large":
            path = pdf.beginPath()
            path.moveTo(x_estimate, row_y + 5)
            path.lineTo(x_estimate + 5, row_y)
            path.lineTo(x_estimate, row_y - 5)
            path.lineTo(x_estimate - 5, row_y)
            path.close()
            pdf.drawPath(path, stroke=0, fill=1)
        else:
            pdf.circle(x_estimate, row_y, 4, stroke=0, fill=1)
        label = f"{estimate:.1f}%"
        label_x = min(x_estimate + 7, chart_x1 - 45)
        pdf.setFont("Helvetica-Bold", 7)
        label_width = stringWidth(label, "Helvetica-Bold", 7)
        pdf.setFillColor(white)
        pdf.rect(label_x - 1, row_y - 5, label_width + 2, 10, stroke=0, fill=1)
        pdf.setFillColor(colour)
        pdf.drawString(label_x, row_y - 3, label)

    y = axis_y - 130
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(46, y, "Evidence table")
    y -= 16
    column_x = (46, 252, 352, 466)
    headers = ("Published size group", "Estimate", "95% interval", "Base")
    pdf.setFillColor(pale)
    pdf.rect(46, y - 3, page_width - 92, 18, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 8)
    for x, header in zip(column_x, headers, strict=True):
        pdf.drawString(x, y + 3, header)
    y -= 18
    for row in rows:
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(column_x[0], y, display_labels[row["business_size"]])
        pdf.drawString(column_x[1], y, f"{float(row['estimate_percent']):.1f}%")
        pdf.drawString(
            column_x[2],
            y,
            f"{float(row['lower_limit_percent']):.1f}% to "
            f"{float(row['upper_limit_percent']):.1f}%",
        )
        pdf.drawRightString(page_width - 46, y, f"{int(row['sample_base']):,}")
        pdf.setStrokeColor(grid)
        pdf.setLineWidth(0.5)
        pdf.line(46, y - 5, page_width - 46, y - 5)
        y -= 17

    y -= 3
    gap = 18
    column_width = (page_width - 92 - gap) / 2
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(46, y, "What this preliminary result shows")
    pdf.drawString(46 + column_width + gap, y, "What it does not show")
    left_y = _paragraph(
        pdf,
        "The point estimates rise across the published business-size groups. "
        "This provides a baseline for choosing the next question.",
        x=46,
        y=y - 15,
        width=column_width,
        size=8.5,
        leading=11,
    )
    right_y = _paragraph(
        pdf,
        "It does not prove statistically significant differences, explain why "
        "use differs, or show that business size causes AI use.",
        x=46 + column_width + gap,
        y=y - 15,
        width=column_width,
        size=8.5,
        leading=11,
    )
    y = min(left_y, right_y) - 10

    pdf.setFillColor(pale)
    pdf.roundRect(46, y - 38, page_width - 92, 42, 5, stroke=0, fill=1)
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(56, y - 10, "Source and interpretation boundary")
    _paragraph(
        pdf,
        "DSIT, UK Business Data Survey 2026, Table 42. Denominator: all UK "
        "businesses within each published size group. Bases are rounded "
        "unweighted respondent counts, not counts of UK businesses.",
        x=56,
        y=y - 22,
        width=page_width - 112,
        size=7.5,
        leading=9,
        colour=ink,
    )

    pdf.setStrokeColor(grid)
    pdf.line(46, 42, page_width - 46, 42)
    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 7)
    pdf.drawString(46, 29, "Fieldwork: 10 October 2025 to 28 January 2026")
    pdf.drawRightString(page_width - 46, 29, "Internal preliminary report | Page 1 of 1")


def create_report(
    *,
    result_path: Path,
    approved_brief_path: Path,
    brief_approval_path: Path,
    output_pdf: Path,
    created_at: datetime | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    if (
        output_pdf.exists() or output_pdf.with_suffix(".metadata.json").exists()
    ) and not replace:
        raise FileExistsError(f"Refusing to overwrite report output: {output_pdf}")
    rows = _load_inputs(result_path, approved_brief_path, brief_approval_path)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_pdf), pagesize=A4, pageCompression=1)
    _draw_report(pdf, rows)
    pdf.showPage()
    pdf.save()

    created_at = (created_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    metadata = {
        "report_id": REPORT_ID,
        "title": "Preliminary insight 01 - Reported AI use by business size",
        "created_at": created_at.replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        "status": "internal_preliminary_report_not_for_publication",
        "finding_id": "F-001",
        "decision_id": "D-013",
        "inputs": [
            {"path": str(result_path), "sha256": sha256_file(result_path)},
            {
                "path": str(approved_brief_path),
                "sha256": sha256_file(approved_brief_path),
            },
            {
                "path": str(brief_approval_path),
                "sha256": sha256_file(brief_approval_path),
            },
        ],
        "output": {"path": str(output_pdf), "sha256": sha256_file(output_pdf)},
        "governance_boundary": (
            "Saved locally as a short preliminary internal report. Public "
            "wording, external sharing, and publication remain unapproved."
        ),
    }
    metadata_path = output_pdf.with_suffix(".metadata.json")
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace the named report after an explicit visual-QA revision.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path.cwd()
    result = root / (
        "data/processed/uk_business_data_survey/2026-06-18/analysis/"
        "g5_01_ai_use_by_size/approved/20260723T075335Z/result.csv"
    )
    approved_brief = root / (
        "data/processed/uk_business_data_survey/2026-06-18/analysis/"
        "g5_05_evidence_brief/approved/20260723T083141Z/evidence_brief.md"
    )
    brief_approval = approved_brief.parent / "approval.metadata.json"
    output = root / (
        "output/pdf/SME_Preliminary_Report_01_AI_Use_by_Business_Size.pdf"
    )
    metadata = create_report(
        result_path=result,
        approved_brief_path=approved_brief,
        brief_approval_path=brief_approval,
        output_pdf=output,
        replace=args.replace,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
