"""Extract AI-system integration by business size from UKBDS 2026 Table 48.

This is conditional evidence about businesses that already report using AI
technologies. It must not be presented as a percentage of all UK businesses.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
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
    sha256_file,
    verify_registered_input,
)


TABLE_ID = "48"
INDICATOR_ID = "ai_tools_integrated_with_systems"
DENOMINATOR = "UK businesses that use Artificial Intelligence technologies"

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


@dataclass(frozen=True)
class IntegrationObservation:
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


def extract_ai_integration_by_size(
    central_workbook: Path,
    confidence_workbook: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> list[IntegrationObservation]:
    """Extract the Table 48 'Yes' response for the four employer-size rows."""

    if enforce_registered_checksums:
        verify_registered_input(central_workbook)
        verify_registered_input(confidence_workbook)

    central_source = read_ods_sheet(central_workbook, TABLE_ID)
    central_ci = read_ods_sheet(confidence_workbook, TABLE_ID)
    lower = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_lcl")
    upper = read_ods_sheet(confidence_workbook, f"{TABLE_ID}_ucl")
    if len(central_ci) < 14:
        raise ValueError("Table 48 does not contain the expected rows")

    header = central_ci[7]
    estimate_column = _find_column(header, "Yes")
    base_column = _find_column(header, "Unweighted base")
    central_source_rows = _rows_by_label(central_source)
    central_rows = _rows_by_label(central_ci)
    lower_rows = _rows_by_label(lower)
    upper_rows = _rows_by_label(upper)

    observations: list[IntegrationObservation] = []
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
        source_base = _value_at(source_row, base_column)
        sample_base = int(raw_base) if isinstance(raw_base, (int, float)) else None
        if sample_base is None or not isinstance(source_base, (int, float)):
            raise ValueError(f"Missing unweighted base for {source_label}")
        if int(source_base) != sample_base:
            raise ValueError(f"Unweighted-base mismatch for {source_label}")

        observations.append(
            IntegrationObservation(
                source_id=SOURCE_ID,
                dataset_id=DATASET_ID,
                dataset_version=DATASET_VERSION,
                table_id=TABLE_ID,
                indicator_id=INDICATOR_ID,
                period=PERIOD,
                population=DENOMINATOR,
                denominator=DENOMINATOR,
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
                    "Conditional on reported AI use; 'Yes' means at least one "
                    "AI tool is integrated with business systems. Large is a "
                    "separate reference benchmark."
                ),
            )
        )

    validate_integration_observations(observations)
    return observations


def validate_integration_observations(
    observations: list[IntegrationObservation],
) -> None:
    if [item.business_size for item in observations] != [
        "micro",
        "small",
        "medium",
        "large",
    ]:
        raise ValueError("Unexpected Table 48 business-size rows")
    if [item.scope_role for item in observations] != [
        "primary",
        "primary",
        "primary",
        "reference_benchmark",
    ]:
        raise ValueError("Unexpected Table 48 scope roles")

    for observation in observations:
        if observation.table_id != TABLE_ID:
            raise ValueError("Unexpected source table")
        if observation.denominator != DENOMINATOR:
            raise ValueError("Unexpected Table 48 denominator")
        if observation.source_status != "observed":
            raise ValueError(
                f"Target row is not observed: {observation.business_size}"
            )
        values = (
            observation.lower_limit,
            observation.estimate,
            observation.upper_limit,
        )
        if any(value is None or not 0 <= value <= 1 for value in values):
            raise ValueError(
                f"Invalid value or interval for {observation.business_size}"
            )
        lower, estimate, upper = values
        if not lower <= estimate <= upper:
            raise ValueError(
                "Confidence limits do not contain estimate for "
                f"{observation.business_size}"
            )
        if observation.sample_base is None or observation.sample_base <= 0:
            raise ValueError(f"Invalid sample base for {observation.business_size}")


def _atomic_write_csv(
    path: Path,
    observations: list[IntegrationObservation],
) -> None:
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
    observations: list[IntegrationObservation],
    *,
    central_workbook: Path,
    confidence_workbook: Path,
    started_at: datetime | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    metadata_path = output_csv.with_suffix(".metadata.json")
    existing = [path for path in (output_csv, metadata_path) if path.exists()]
    if existing and not replace:
        raise FileExistsError(
            "Refusing to overwrite existing output: "
            + ", ".join(str(path) for path in existing)
        )

    completed_at = datetime.now(timezone.utc).replace(microsecond=0)
    started_at = started_at or completed_at
    _atomic_write_csv(output_csv, observations)
    metadata = {
        "run_id": completed_at.strftime("%Y%m%dT%H%M%SZ"),
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
        "task_id": "G5-07",
        "candidate_finding_id": "F-002",
        "source_id": SOURCE_ID,
        "dataset_version": DATASET_VERSION,
        "table_id": TABLE_ID,
        "indicator_id": INDICATOR_ID,
        "denominator": DENOMINATOR,
        "row_count": len(observations),
        "validation_result": "passed",
        "warnings": [],
        "approval_status": "unreviewed_interim_candidate",
        "code": {
            "path": "src/transformation/ukbds_ai_integration.py",
            "sha256": sha256_file(Path(__file__)),
        },
        "inputs": [
            {"path": str(central_workbook), "sha256": sha256_file(central_workbook)},
            {
                "path": str(confidence_workbook),
                "sha256": sha256_file(confidence_workbook),
            },
        ],
        "output": {"path": str(output_csv), "sha256": sha256_file(output_csv)},
        "governance_boundary": (
            "Unreviewed conditional evidence. The denominator is AI-using "
            "businesses, not all UK businesses. No finding or publication is "
            "approved."
        ),
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
            / "ai_integration_among_ai_users_by_size.csv"
        ),
    )
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = datetime.now(timezone.utc).replace(microsecond=0)
    observations = extract_ai_integration_by_size(
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
