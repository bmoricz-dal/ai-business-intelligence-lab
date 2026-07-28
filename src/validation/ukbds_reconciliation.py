"""Reconcile UKBDS 2026 Table 41 with the rounded official publication.

This is validation evidence, not an analytical finding. The official report
publishes whole percentages, while the workbooks retain unrounded proportions.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

from src.transformation.ukbds import (
    DATASET_ID,
    DATASET_VERSION,
    PERIOD,
    SOURCE_ID,
    read_ods_sheet,
    sha256_file,
    verify_registered_input,
)


TABLE_ID = "41"
INDICATOR_LABEL = "Uses any Artificial Intelligence-based technologies"
PUBLICATION_URL = (
    "https://www.gov.uk/government/statistics/uk-business-data-survey-2026/"
    "uk-business-data-survey-2026#use-of-artificial-intelligence"
)
PUBLICATION_HTML_SHA256 = (
    "26e1947308e6b5581dde83039b2ced37fb53fbdcd796dd63d25de8fa9a26a337"
)
ROUNDING_RULE = "percentage x 100; round half up to 0 decimal places"
ROUNDING_TOLERANCE_PERCENTAGE_POINTS = Decimal("0.5")

TARGET_ROWS = (
    ("Total", "total"),
    ("Size: Sole trader", "sole_trader"),
    ("Size: Micro (up to 9 employees)", "micro"),
    ("Size: Small (10 to 49 employees)", "small"),
    ("Size: Medium (50 to 249 employees)", "medium"),
    ("Size: Large (250 plus employees)", "large"),
)

OUTPUT_FIELDS = [
    "source_id",
    "dataset_id",
    "dataset_version",
    "table_id",
    "period",
    "population",
    "denominator",
    "business_size",
    "source_business_size_label",
    "workbook_estimate",
    "workbook_percent",
    "workbook_rounded_percent",
    "publication_percent",
    "unrounded_difference_percentage_points",
    "rounded_difference_percentage_points",
    "rounding_rule",
    "rounding_tolerance_percentage_points",
    "workbook_row_unweighted_base",
    "publication_overall_unweighted_base",
    "publication_reference",
    "reconciliation_status",
]


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def normalized_text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def parse_publication_values(publication_html: Path) -> tuple[dict[str, int], int]:
    """Extract the six report percentages and the reported overall base."""

    actual_hash = sha256_file(publication_html)
    if actual_hash != PUBLICATION_HTML_SHA256:
        raise ValueError(
            "Publication HTML checksum mismatch: "
            f"expected {PUBLICATION_HTML_SHA256}, got {actual_hash}"
        )

    parser = _TextExtractor()
    parser.feed(publication_html.read_text(encoding="utf-8"))
    text = parser.normalized_text()

    overall_match = re.search(
        r"of UK businesses that handled digitised data, (\d+)% said that they "
        r"used Artificial Intelligence \(\s*AI\s*\) based technologies",
        text,
    )
    size_match = re.search(
        r"Large businesses were more likely to use AI \((\d+)%\).*?whilst "
        r"medium \((\d+)%\) and small \((\d+)%\) businesses were more likely "
        r"to use AI compared to micro businesses \((\d+)%\) and sole traders "
        r"\((\d+)%\)",
        text,
    )
    base_match = re.search(
        r"Figure 14:.*?Base: ([\d,]+) UK businesses that handled digitised data",
        text,
    )
    if not overall_match or not size_match or not base_match:
        raise ValueError("Required Table 41 publication claims were not found")

    large, medium, small, micro, sole_trader = map(int, size_match.groups())
    values = {
        "total": int(overall_match.group(1)),
        "sole_trader": sole_trader,
        "micro": micro,
        "small": small,
        "medium": medium,
        "large": large,
    }
    return values, int(base_match.group(1).replace(",", ""))


def _find_column(header: list[Any], label: str) -> int:
    try:
        return header.index(label)
    except ValueError as error:
        raise ValueError(f"Required column not found: {label}") from error


def _rows_by_label(rows: list[list[Any]]) -> dict[str, list[Any]]:
    return {
        row[0]: row
        for row in rows
        if row and isinstance(row[0], str)
    }


def _value_at(row: list[Any], column: int) -> Any:
    return row[column] if column < len(row) else None


def _whole_percent(value: float) -> int:
    return int(
        (Decimal(str(value)) * Decimal("100")).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )


@dataclass(frozen=True)
class ReconciliationRow:
    source_id: str
    dataset_id: str
    dataset_version: str
    table_id: str
    period: str
    population: str
    denominator: str
    business_size: str
    source_business_size_label: str
    workbook_estimate: float
    workbook_percent: float
    workbook_rounded_percent: int
    publication_percent: int
    unrounded_difference_percentage_points: float
    rounded_difference_percentage_points: int
    rounding_rule: str
    rounding_tolerance_percentage_points: float
    workbook_row_unweighted_base: int
    publication_overall_unweighted_base: int
    publication_reference: str
    reconciliation_status: str


def reconcile_table41(
    central_workbook: Path,
    confidence_workbook: Path,
    publication_html: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> list[ReconciliationRow]:
    """Reconcile the report's rounded Table 41 values to both workbooks."""

    if enforce_registered_checksums:
        verify_registered_input(central_workbook)
        verify_registered_input(confidence_workbook)
    publication_values, publication_base = parse_publication_values(publication_html)

    central_source = read_ods_sheet(central_workbook, TABLE_ID)
    central_confidence = read_ods_sheet(confidence_workbook, TABLE_ID)
    if len(central_source) < 14 or len(central_confidence) < 14:
        raise ValueError("Table 41 does not contain the expected rows")

    header = central_confidence[7]
    estimate_column = _find_column(header, INDICATOR_LABEL)
    base_column = _find_column(header, "Unweighted base")
    source_rows = _rows_by_label(central_source)
    confidence_rows = _rows_by_label(central_confidence)

    reconciled: list[ReconciliationRow] = []
    for source_label, size_id in TARGET_ROWS:
        if source_label not in source_rows or source_label not in confidence_rows:
            raise ValueError(f"Required Table 41 row not found: {source_label}")
        source_row = source_rows[source_label]
        confidence_row = confidence_rows[source_label]
        source_estimate = _value_at(source_row, estimate_column)
        estimate = _value_at(confidence_row, estimate_column)
        source_base = _value_at(source_row, base_column)
        base = _value_at(confidence_row, base_column)
        if not isinstance(estimate, (int, float)) or not isinstance(
            source_estimate, (int, float)
        ):
            raise ValueError(f"Table 41 estimate is not numeric for {source_label}")
        if float(source_estimate) != float(estimate):
            raise ValueError(
                f"Central estimate mismatch between workbooks for {source_label}"
            )
        if not isinstance(base, (int, float)) or not isinstance(
            source_base, (int, float)
        ):
            raise ValueError(f"Table 41 base is not numeric for {source_label}")
        if int(source_base) != int(base):
            raise ValueError(
                f"Unweighted-base mismatch between workbooks for {source_label}"
            )
        if not 0 <= float(estimate) <= 1 or int(base) <= 0:
            raise ValueError(f"Invalid Table 41 value for {source_label}")

        workbook_percent = float(estimate) * 100
        rounded = _whole_percent(float(estimate))
        published = publication_values[size_id]
        rounded_difference = rounded - published
        unrounded_difference = workbook_percent - published
        status = "passed" if rounded_difference == 0 else "failed"
        reconciled.append(
            ReconciliationRow(
                source_id=SOURCE_ID,
                dataset_id=DATASET_ID,
                dataset_version=DATASET_VERSION,
                table_id=TABLE_ID,
                period=PERIOD,
                population="UK businesses that handle digitised data",
                denominator=(
                    "UK businesses that handle digitised data within the "
                    "published business-size category"
                ),
                business_size=size_id,
                source_business_size_label=source_label,
                workbook_estimate=float(estimate),
                workbook_percent=workbook_percent,
                workbook_rounded_percent=rounded,
                publication_percent=published,
                unrounded_difference_percentage_points=unrounded_difference,
                rounded_difference_percentage_points=rounded_difference,
                rounding_rule=ROUNDING_RULE,
                rounding_tolerance_percentage_points=float(
                    ROUNDING_TOLERANCE_PERCENTAGE_POINTS
                ),
                workbook_row_unweighted_base=int(base),
                publication_overall_unweighted_base=publication_base,
                publication_reference=PUBLICATION_URL,
                reconciliation_status=status,
            )
        )

    validate_reconciliation(reconciled)
    return reconciled


def validate_reconciliation(rows: list[ReconciliationRow]) -> None:
    if len(rows) != len(TARGET_ROWS):
        raise ValueError(f"Expected {len(TARGET_ROWS)} rows, got {len(rows)}")
    expected_sizes = {size_id for _, size_id in TARGET_ROWS}
    actual_sizes = [row.business_size for row in rows]
    if set(actual_sizes) != expected_sizes or len(actual_sizes) != len(set(actual_sizes)):
        raise ValueError(f"Unexpected or duplicate Table 41 categories: {actual_sizes}")
    failures = [row.business_size for row in rows if row.reconciliation_status != "passed"]
    if failures:
        raise ValueError(
            "Publication rounding reconciliation failed for: " + ", ".join(failures)
        )
    if any(
        abs(Decimal(str(row.unrounded_difference_percentage_points)))
        > ROUNDING_TOLERANCE_PERCENTAGE_POINTS
        for row in rows
    ):
        raise ValueError("Unrounded workbook value exceeds the recorded tolerance")
    total = next(row for row in rows if row.business_size == "total")
    if total.workbook_row_unweighted_base != total.publication_overall_unweighted_base:
        raise ValueError("Published overall base does not match the Table 41 total base")


def _atomic_write_csv(path: Path, rows: list[ReconciliationRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as temporary:
        writer = csv.DictWriter(temporary, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        json.dump(payload, temporary, indent=2, sort_keys=True)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def write_reconciliation_outputs(
    output_csv: Path,
    rows: list[ReconciliationRow],
    *,
    central_workbook: Path,
    confidence_workbook: Path,
    publication_html: Path,
    started_at: datetime | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    metadata_path = output_csv.with_suffix(".metadata.json")
    existing = [path for path in (output_csv, metadata_path) if path.exists()]
    if existing and not replace:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Refusing to overwrite existing output: {names}")

    completed_at = datetime.now(timezone.utc).replace(microsecond=0)
    started_at = started_at or completed_at
    _atomic_write_csv(output_csv, rows)
    metadata = {
        "run_id": completed_at.strftime("%Y%m%dT%H%M%SZ"),
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
        "source_id": SOURCE_ID,
        "dataset_version": DATASET_VERSION,
        "table_id": TABLE_ID,
        "row_count": len(rows),
        "validation_result": "passed",
        "warnings": [],
        "rounding_rule": ROUNDING_RULE,
        "rounding_tolerance_percentage_points": float(
            ROUNDING_TOLERANCE_PERCENTAGE_POINTS
        ),
        "code": {
            "path": "src/validation/ukbds_reconciliation.py",
            "sha256": sha256_file(Path(__file__)),
        },
        "inputs": [
            {"path": str(central_workbook), "sha256": sha256_file(central_workbook)},
            {
                "path": str(confidence_workbook),
                "sha256": sha256_file(confidence_workbook),
            },
            {"path": str(publication_html), "sha256": sha256_file(publication_html)},
        ],
        "output": {"path": str(output_csv), "sha256": sha256_file(output_csv)},
    }
    _atomic_write_json(metadata_path, metadata)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    raw = Path("data/raw/dsit/uk_business_data_survey/2026-06-18")
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
        "--publication-html",
        type=Path,
        default=raw / "uk-business-data-survey-2026.html",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/interim/uk_business_data_survey/2026-06-18")
        / "table41_publication_reconciliation.csv",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Explicitly replace the reconciliation CSV and metadata.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = datetime.now(timezone.utc).replace(microsecond=0)
    rows = reconcile_table41(
        args.central_workbook,
        args.confidence_workbook,
        args.publication_html,
    )
    metadata = write_reconciliation_outputs(
        args.output,
        rows,
        central_workbook=args.central_workbook,
        confidence_workbook=args.confidence_workbook,
        publication_html=args.publication_html,
        started_at=started_at,
        replace=args.replace,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
