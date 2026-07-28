"""Extract the approved UKBDS 2026 AI-use-by-size slice from ODS files.

This module preserves published labels and conditional meanings. It produces an
interim evidence table only; it does not generate findings or public claims.
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
import xml.etree.ElementTree as ET
from zipfile import ZipFile


NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}

SOURCE_ID = "dsit_ukbds_2026"
DATASET_ID = "uk_business_data_survey"
DATASET_VERSION = "2026-06-18"
TABLE_ID = "42"
INDICATOR_ID = "uses_any_ai_based_technologies"
PERIOD = "2025-10-10/2026-01-28"

REGISTERED_HASHES = {
    "DSIT_UK_Business_Data_Survey_2026_tables.ods": (
        "3ad453b41eebcc2af853d3410d649761de2c4421cbe164ebdb79ca8b6f6ae53c"
    ),
    "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods": (
        "1eff1276a0073927169941664d623a42c815c619c3e1c6ca0ebf7502a9fce4ef"
    ),
}

SIZE_LABELS = {
    "Size: Micro (up to 9 employees)": ("micro", "primary"),
    "Size: Small (10 to 49 employees)": ("small", "primary"),
    "Size: Medium (50 to 249 employees)": ("medium", "primary"),
    "Size: Large (250 plus employees)": ("large", "reference_benchmark"),
}

OUTPUT_FIELDS = [
    "source_id",
    "dataset_id",
    "dataset_version",
    "table_id",
    "indicator_id",
    "period",
    "population",
    "denominator",
    "unit",
    "business_size",
    "source_business_size_label",
    "scope_role",
    "estimate",
    "lower_limit",
    "upper_limit",
    "sample_base",
    "source_status",
    "notes",
]


def _attribute(prefix: str, name: str) -> str:
    return f"{{{NS[prefix]}}}{name}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_registered_input(path: Path) -> str:
    actual = sha256_file(path)
    expected = REGISTERED_HASHES.get(path.name)
    if expected is None:
        raise ValueError(f"No registered checksum for {path.name}")
    if actual != expected:
        raise ValueError(
            f"Checksum mismatch for {path.name}: expected {expected}, got {actual}"
        )
    return actual


def _cell_value(cell: ET.Element) -> str | float | None:
    value_type = cell.get(_attribute("office", "value-type"))
    if value_type in {"percentage", "float", "currency"}:
        raw = cell.get(_attribute("office", "value"))
        return float(raw) if raw is not None else None
    text = "".join(cell.itertext()).strip()
    return text or None


def read_ods_sheet(path: Path, sheet_name: str) -> list[list[str | float | None]]:
    """Read one ODS sheet without changing the source workbook."""

    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("content.xml"))

    target = None
    for table in root.findall(".//table:table", NS):
        if table.get(_attribute("table", "name")) == sheet_name:
            target = table
            break
    if target is None:
        raise ValueError(f"Sheet {sheet_name!r} not found in {path.name}")

    result: list[list[str | float | None]] = []
    for row in target.findall("table:table-row", NS):
        row_repeat = int(row.get(_attribute("table", "number-rows-repeated"), "1"))
        populated: dict[int, str | float | None] = {}
        column_index = 0
        for cell in list(row):
            if cell.tag not in {
                _attribute("table", "table-cell"),
                _attribute("table", "covered-table-cell"),
            }:
                continue
            column_repeat = int(
                cell.get(_attribute("table", "number-columns-repeated"), "1")
            )
            value = _cell_value(cell)
            if value is not None:
                for offset in range(column_repeat):
                    populated[column_index + offset] = value
            column_index += column_repeat

        if not populated:
            result.extend([[] for _ in range(min(row_repeat, 1))])
            continue
        width = max(populated) + 1
        values = [populated.get(index) for index in range(width)]
        result.extend([list(values) for _ in range(row_repeat)])
    return result


def _find_column(header: list[str | float | None], label: str) -> int:
    try:
        return header.index(label)
    except ValueError as error:
        raise ValueError(f"Required column not found: {label}") from error


def _rows_by_label(rows: list[list[str | float | None]]) -> dict[str, list[Any]]:
    labelled: dict[str, list[Any]] = {}
    for row in rows:
        if row and isinstance(row[0], str):
            labelled[row[0]] = row
    return labelled


def _value_at(row: list[Any], column: int) -> Any:
    return row[column] if column < len(row) else None


def _numeric_or_status(value: Any) -> tuple[float | None, str]:
    if isinstance(value, (int, float)):
        return float(value), "observed"
    if value == "c":
        return None, "suppressed_c"
    if value == "z":
        return None, "not_asked_z"
    if value in {None, ""}:
        return None, "missing"
    return None, "unknown"


@dataclass(frozen=True)
class Observation:
    source_id: str
    dataset_id: str
    dataset_version: str
    table_id: str
    indicator_id: str
    period: str
    population: str
    denominator: str
    unit: str
    business_size: str
    source_business_size_label: str
    scope_role: str
    estimate: float | None
    lower_limit: float | None
    upper_limit: float | None
    sample_base: int | None
    source_status: str
    notes: str


def extract_ai_use_by_size(
    central_workbook: Path,
    confidence_workbook: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> list[Observation]:
    """Extract Table 42 for micro, small, medium, and large size groups."""

    if enforce_registered_checksums:
        verify_registered_input(central_workbook)
        verify_registered_input(confidence_workbook)

    central_source = read_ods_sheet(central_workbook, TABLE_ID)
    central_ci = read_ods_sheet(confidence_workbook, TABLE_ID)
    lower = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_lcl")
    upper = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_ucl")

    if len(central_ci) < 9:
        raise ValueError("Table 42 does not contain the expected header and data rows")
    header = central_ci[7]
    estimate_column = _find_column(
        header, "Uses any Artificial Intelligence-based technologies"
    )
    base_column = _find_column(header, "Unweighted base")

    central_source_rows = _rows_by_label(central_source)
    central_rows = _rows_by_label(central_ci)
    lower_rows = _rows_by_label(lower)
    upper_rows = _rows_by_label(upper)

    observations: list[Observation] = []
    for source_label, (size_id, scope_role) in SIZE_LABELS.items():
        try:
            source_row = central_source_rows[source_label]
            central_row = central_rows[source_label]
            lower_row = lower_rows[source_label]
            upper_row = upper_rows[source_label]
        except KeyError as error:
            raise ValueError(f"Required size row not found: {source_label}") from error

        estimate, status = _numeric_or_status(
            _value_at(central_row, estimate_column)
        )
        lower_limit, lower_status = _numeric_or_status(
            _value_at(lower_row, estimate_column)
        )
        upper_limit, upper_status = _numeric_or_status(
            _value_at(upper_row, estimate_column)
        )
        source_estimate, source_status = _numeric_or_status(
            _value_at(source_row, estimate_column)
        )
        if source_status != status or source_estimate != estimate:
            raise ValueError(
                f"Central estimate mismatch between workbooks for {source_label}"
            )
        if lower_status != status or upper_status != status:
            raise ValueError(f"Confidence-limit status mismatch for {source_label}")

        raw_base = _value_at(central_row, base_column)
        sample_base = int(raw_base) if isinstance(raw_base, (int, float)) else None
        source_base = _value_at(source_row, base_column)
        if sample_base is None or int(source_base) != sample_base:
            raise ValueError(f"Unweighted-base mismatch for {source_label}")

        observations.append(
            Observation(
                source_id=SOURCE_ID,
                dataset_id=DATASET_ID,
                dataset_version=DATASET_VERSION,
                table_id=TABLE_ID,
                indicator_id=INDICATOR_ID,
                period=PERIOD,
                population="All UK businesses",
                denominator=(
                    "All UK businesses within the published business-size category"
                ),
                unit="proportion",
                business_size=size_id,
                source_business_size_label=source_label,
                scope_role=scope_role,
                estimate=estimate,
                lower_limit=lower_limit,
                upper_limit=upper_limit,
                sample_base=sample_base,
                source_status=status,
                notes=(
                    "Self-reported use for at least one listed AI purpose; "
                    "large is a separate reference benchmark."
                ),
            )
        )

    validate_observations(observations)
    return observations


def validate_observations(observations: list[Observation]) -> None:
    if len(observations) != len(SIZE_LABELS):
        raise ValueError(f"Expected {len(SIZE_LABELS)} rows, got {len(observations)}")
    sizes = [observation.business_size for observation in observations]
    if set(sizes) != {"micro", "small", "medium", "large"}:
        raise ValueError(f"Unexpected business-size categories: {sizes}")
    if len(sizes) != len(set(sizes)):
        raise ValueError("Business-size keys are not unique")

    for observation in observations:
        if observation.source_status != "observed":
            raise ValueError(
                f"Target row is not observed: {observation.business_size} "
                f"({observation.source_status})"
            )
        values = (
            observation.lower_limit,
            observation.estimate,
            observation.upper_limit,
        )
        if any(value is None or not 0 <= value <= 1 for value in values):
            raise ValueError(
                f"Invalid percentage or confidence limit for {observation.business_size}"
            )
        lower, estimate, upper = values
        if not lower <= estimate <= upper:
            raise ValueError(
                f"Confidence limits do not contain estimate for "
                f"{observation.business_size}"
            )
        if observation.sample_base is None or observation.sample_base <= 0:
            raise ValueError(f"Invalid sample base for {observation.business_size}")


def _atomic_write_csv(path: Path, observations: list[Observation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as temporary:
        writer = csv.DictWriter(temporary, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(observation) for observation in observations)
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


def write_interim_outputs(
    output_csv: Path,
    observations: list[Observation],
    *,
    central_workbook: Path,
    confidence_workbook: Path,
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
    run_id = completed_at.strftime("%Y%m%dT%H%M%SZ")
    _atomic_write_csv(output_csv, observations)
    metadata = {
        "run_id": run_id,
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
        "source_id": SOURCE_ID,
        "dataset_version": DATASET_VERSION,
        "table_id": TABLE_ID,
        "row_count": len(observations),
        "warnings": [],
        "validation_result": "passed",
        "code": {
            "path": "src/transformation/ukbds.py",
            "sha256": sha256_file(Path(__file__)),
        },
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
        "output": {
            "path": str(output_csv),
            "sha256": sha256_file(output_csv),
        },
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
        default=(
            raw / "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            Path("data/interim/uk_business_data_survey/2026-06-18")
            / "ai_use_by_size.csv"
        ),
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Explicitly replace the versioned interim CSV and metadata.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = datetime.now(timezone.utc).replace(microsecond=0)
    observations = extract_ai_use_by_size(
        args.central_workbook,
        args.confidence_workbook,
    )
    metadata = write_interim_outputs(
        args.output,
        observations,
        central_workbook=args.central_workbook,
        confidence_workbook=args.confidence_workbook,
        started_at=started_at,
        replace=args.replace,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
