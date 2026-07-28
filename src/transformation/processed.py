"""Build the D-008 Table 42 processed candidate and SQLite database.

The output is a validated processed candidate. It remains marked as accepted
for schema design until the research director reviews the completed outputs.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from typing import Any

from src.transformation.ukbds import REGISTERED_HASHES, sha256_file


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ID = "dsit_ukbds_2026"
DATASET_ID = "uk_business_data_survey"
DATASET_VERSION = "2026-06-18"
SOURCE_TABLE_ID = "42"
SOURCE_QUESTION_ID = "Q_AI_USE_ALL_BUSINESSES"
INDICATOR_ID = "uses_any_ai_based_technologies"
DENOMINATOR_ID = "all_uk_businesses"
APPROVAL_STATUS = "accepted_for_schema_design"
EXPECTED_INTERIM_SHA256 = (
    "775fe660b4be893d35636c1e891f0a9506e0b20425c64b89c3640f58001820cf"
)
EXPECTED_INTERIM_METADATA_SHA256 = (
    "8b4b53882fd3eb0e737ac401f1c3eb91634f81cc0d9762e9eacb2c9e00f29d22"
)
EXPECTED_SIZES = ("micro", "small", "medium", "large")

OUTPUT_FIELDS = [
    "observation_id",
    "source_id",
    "dataset_id",
    "dataset_version",
    "source_table_id",
    "source_question_id",
    "indicator_id",
    "period_start",
    "period_end",
    "population_label",
    "denominator_id",
    "unit",
    "dimension_type",
    "dimension_value",
    "source_dimension_label",
    "scope_role",
    "estimate",
    "lower_limit",
    "upper_limit",
    "confidence_level",
    "sample_base",
    "source_status",
    "run_id",
    "approval_status",
    "notes",
]


def _project_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class ProcessedObservation:
    observation_id: str
    source_id: str
    dataset_id: str
    dataset_version: str
    source_table_id: str
    source_question_id: str
    indicator_id: str
    period_start: str
    period_end: str
    population_label: str
    denominator_id: str
    unit: str
    dimension_type: str
    dimension_value: str
    source_dimension_label: str
    scope_role: str
    estimate: float
    lower_limit: float
    upper_limit: float
    confidence_level: float
    sample_base: int
    source_status: str
    run_id: str
    approval_status: str
    notes: str


def verify_interim_evidence(
    interim_csv: Path,
    interim_metadata: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> dict[str, Any]:
    """Verify the accepted interim output, metadata, code, and raw inputs."""

    csv_hash = sha256_file(interim_csv)
    metadata_hash = sha256_file(interim_metadata)
    if enforce_registered_checksums:
        if csv_hash != EXPECTED_INTERIM_SHA256:
            raise ValueError(
                "Accepted interim CSV checksum mismatch: "
                f"expected {EXPECTED_INTERIM_SHA256}, got {csv_hash}"
            )
        if metadata_hash != EXPECTED_INTERIM_METADATA_SHA256:
            raise ValueError(
                "Accepted interim metadata checksum mismatch: "
                f"expected {EXPECTED_INTERIM_METADATA_SHA256}, got {metadata_hash}"
            )

    metadata = json.loads(interim_metadata.read_text(encoding="utf-8"))
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("Interim evidence is not a warning-free passed run")
    if metadata.get("source_id") != SOURCE_ID:
        raise ValueError("Unexpected interim source ID")
    if metadata.get("dataset_version") != DATASET_VERSION:
        raise ValueError("Unexpected interim dataset version")
    if metadata.get("table_id") != SOURCE_TABLE_ID:
        raise ValueError("Unexpected interim source table")
    if metadata.get("row_count") != len(EXPECTED_SIZES):
        raise ValueError("Unexpected interim row count in metadata")
    if metadata.get("output", {}).get("sha256") != csv_hash:
        raise ValueError("Interim CSV does not match its metadata output hash")

    code = metadata.get("code", {})
    code_path = _project_path(Path(code.get("path", "")))
    if not code_path.is_file() or sha256_file(code_path) != code.get("sha256"):
        raise ValueError("Interim transformation code does not match its metadata")

    for item in metadata.get("inputs", []):
        input_path = _project_path(Path(item.get("path", "")))
        if not input_path.is_file() or sha256_file(input_path) != item.get("sha256"):
            raise ValueError(f"Interim raw input mismatch: {input_path}")
        registered = REGISTERED_HASHES.get(input_path.name)
        if enforce_registered_checksums and registered != item.get("sha256"):
            raise ValueError(f"Raw input is not registered: {input_path.name}")

    return metadata


def transform_table42(
    interim_csv: Path,
    *,
    run_id: str,
) -> list[ProcessedObservation]:
    """Map the accepted Table 42 rows into the D-008 observation contract."""

    with interim_csv.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != len(EXPECTED_SIZES):
        raise ValueError(f"Expected four Table 42 rows, got {len(rows)}")

    observations: list[ProcessedObservation] = []
    for expected_size, row in zip(EXPECTED_SIZES, rows, strict=True):
        if row["business_size"] != expected_size:
            raise ValueError(
                f"Unexpected Table 42 size order: expected {expected_size}, "
                f"got {row['business_size']}"
            )
        expected_role = "reference_benchmark" if expected_size == "large" else "primary"
        required = {
            "source_id": SOURCE_ID,
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "table_id": SOURCE_TABLE_ID,
            "indicator_id": INDICATOR_ID,
            "period": "2025-10-10/2026-01-28",
            "population": "All UK businesses",
            "denominator": (
                "All UK businesses within the published business-size category"
            ),
            "unit": "proportion",
            "scope_role": expected_role,
            "source_status": "observed",
        }
        for field, expected in required.items():
            if row[field] != expected:
                raise ValueError(
                    f"Unexpected {field} for {expected_size}: "
                    f"expected {expected!r}, got {row[field]!r}"
                )

        estimate = float(row["estimate"])
        lower = float(row["lower_limit"])
        upper = float(row["upper_limit"])
        sample_base = int(row["sample_base"])
        if not 0 <= lower <= estimate <= upper <= 1:
            raise ValueError(f"Invalid estimate interval for {expected_size}")
        if sample_base <= 0:
            raise ValueError(f"Invalid sample base for {expected_size}")

        observations.append(
            ProcessedObservation(
                observation_id=(
                    f"{SOURCE_ID}:{DATASET_ID}:{DATASET_VERSION}:"
                    f"{SOURCE_TABLE_ID}:{INDICATOR_ID}:business_size:{expected_size}"
                ),
                source_id=SOURCE_ID,
                dataset_id=DATASET_ID,
                dataset_version=DATASET_VERSION,
                source_table_id=SOURCE_TABLE_ID,
                source_question_id=SOURCE_QUESTION_ID,
                indicator_id=INDICATOR_ID,
                period_start="2025-10-10",
                period_end="2026-01-28",
                population_label="All UK businesses",
                denominator_id=DENOMINATOR_ID,
                unit="proportion",
                dimension_type="business_size",
                dimension_value=expected_size,
                source_dimension_label=row["source_business_size_label"],
                scope_role=expected_role,
                estimate=estimate,
                lower_limit=lower,
                upper_limit=upper,
                confidence_level=0.95,
                sample_base=sample_base,
                source_status="observed",
                run_id=run_id,
                approval_status=APPROVAL_STATUS,
                notes=(
                    row["notes"]
                    + " Processed candidate created under D-008; "
                    "owner output review pending."
                ),
            )
        )

    validate_processed_observations(observations)
    return observations


def validate_processed_observations(
    observations: list[ProcessedObservation],
) -> None:
    if len(observations) != len(EXPECTED_SIZES):
        raise ValueError("Processed observation count is not four")
    sizes = [item.dimension_value for item in observations]
    if sizes != list(EXPECTED_SIZES) or len(set(sizes)) != len(sizes):
        raise ValueError(f"Unexpected or duplicate processed sizes: {sizes}")
    if len({item.observation_id for item in observations}) != len(observations):
        raise ValueError("Processed observation IDs are not unique")
    if sum(item.scope_role == "primary" for item in observations) != 3:
        raise ValueError("Expected three primary SME observations")
    if sum(item.scope_role == "reference_benchmark" for item in observations) != 1:
        raise ValueError("Expected one reference benchmark")
    for item in observations:
        if item.approval_status != APPROVAL_STATUS:
            raise ValueError("Processed candidate has an unexpected approval status")
        if not 0 <= item.lower_limit <= item.estimate <= item.upper_limit <= 1:
            raise ValueError(f"Invalid processed interval for {item.dimension_value}")
        if item.sample_base <= 0:
            raise ValueError(f"Invalid processed base for {item.dimension_value}")


def _write_csv(path: Path, observations: list[ProcessedObservation]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(item) for item in observations)


def _insert_reference_rows(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    started_at: str,
    completed_at: str,
    code_sha256: str,
    metadata_path: Path,
    output_csv: Path,
    output_csv_sha256: str,
) -> None:
    connection.execute(
        """
        INSERT INTO dataset_releases VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            SOURCE_ID,
            DATASET_ID,
            DATASET_VERSION,
            "Department for Science, Innovation and Technology",
            "UK Business Data Survey 2026",
            "2026-06-18",
            "2025-10-10",
            "2026-01-28",
            "https://www.gov.uk/government/statistics/uk-business-data-survey-2026",
            "Open Government Licence v3.0 except where otherwise stated",
            APPROVAL_STATUS,
        ),
    )
    connection.execute(
        "INSERT INTO indicators VALUES (?, ?, ?, ?)",
        (
            INDICATOR_ID,
            "Uses any AI-based technologies",
            "Business reported at least one listed use of AI-based technologies",
            "proportion",
        ),
    )
    connection.execute(
        "INSERT INTO denominators VALUES (?, ?, ?)",
        (
            DENOMINATOR_ID,
            "All UK businesses",
            "All UK businesses within the published business-size category",
        ),
    )
    connection.execute(
        "INSERT INTO pipeline_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            run_id,
            started_at,
            completed_at,
            "src/transformation/processed.py",
            code_sha256,
            str(metadata_path),
            str(output_csv),
            output_csv_sha256,
            "passed",
            APPROVAL_STATUS,
        ),
    )


def _build_database(
    database_path: Path,
    schema_path: Path,
    observations: list[ProcessedObservation],
    *,
    run_id: str,
    started_at: str,
    completed_at: str,
    code_sha256: str,
    metadata_path: Path,
    output_csv: Path,
    output_csv_sha256: str,
) -> dict[str, Any]:
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        _insert_reference_rows(
            connection,
            run_id=run_id,
            started_at=started_at,
            completed_at=completed_at,
            code_sha256=code_sha256,
            metadata_path=metadata_path,
            output_csv=output_csv,
            output_csv_sha256=output_csv_sha256,
        )
        payloads = [asdict(item) for item in observations]
        columns = ", ".join(OUTPUT_FIELDS)
        parameters = ", ".join(f":{field}" for field in OUTPUT_FIELDS)
        connection.executemany(
            f"INSERT INTO observations ({columns}) VALUES ({parameters})",
            payloads,
        )
        connection.commit()

        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        observation_count = connection.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]
        primary_count = connection.execute(
            "SELECT COUNT(*) FROM observations WHERE scope_role = 'primary'"
        ).fetchone()[0]
        benchmark_count = connection.execute(
            """
            SELECT COUNT(*) FROM observations
            WHERE scope_role = 'reference_benchmark'
            """
        ).fetchone()[0]
        table_ids = [
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT source_table_id FROM observations"
            ).fetchall()
        ]
        if integrity != "ok" or foreign_key_errors:
            raise ValueError("SQLite integrity or foreign-key validation failed")
        if (observation_count, primary_count, benchmark_count) != (4, 3, 1):
            raise ValueError("SQLite role or row-count reconciliation failed")
        if table_ids != [SOURCE_TABLE_ID]:
            raise ValueError(f"Unexpected source tables in database: {table_ids}")
        return {
            "integrity_check": integrity,
            "foreign_key_error_count": len(foreign_key_errors),
            "observation_count": observation_count,
            "primary_count": primary_count,
            "reference_benchmark_count": benchmark_count,
            "source_table_ids": table_ids,
        }
    finally:
        connection.close()


def write_processed_candidate(
    output_directory: Path,
    observations: list[ProcessedObservation],
    *,
    interim_csv: Path,
    interim_metadata: Path,
    schema_path: Path,
    source_run_id: str,
    started_at: datetime,
    replace: bool = False,
) -> dict[str, Any]:
    output_csv = output_directory / "observations.csv"
    database_path = output_directory / "sme_intelligence.sqlite"
    metadata_path = output_directory / "processing.metadata.json"
    existing = [
        path
        for path in (output_csv, database_path, metadata_path)
        if path.exists()
    ]
    if existing and not replace:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"Refusing to overwrite existing output: {names}")

    output_directory.mkdir(parents=True, exist_ok=True)
    code_sha = sha256_file(Path(__file__))
    schema_sha = sha256_file(schema_path)
    completed_at = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = started_at.strftime("%Y%m%dT%H%M%SZ")
    started_text = started_at.isoformat().replace("+00:00", "Z")
    completed_text = completed_at.isoformat().replace("+00:00", "Z")

    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=output_directory, suffix=".csv", delete=False
        ) as temporary_csv:
            temporary_csv_path = Path(temporary_csv.name)
        temporary_paths.append(temporary_csv_path)
        _write_csv(temporary_csv_path, observations)
        csv_sha = sha256_file(temporary_csv_path)

        with tempfile.NamedTemporaryFile(
            "wb", dir=output_directory, suffix=".sqlite", delete=False
        ) as temporary_database:
            temporary_database_path = Path(temporary_database.name)
        temporary_paths.append(temporary_database_path)
        database_checks = _build_database(
            temporary_database_path,
            schema_path,
            observations,
            run_id=run_id,
            started_at=started_text,
            completed_at=completed_text,
            code_sha256=code_sha,
            metadata_path=metadata_path,
            output_csv=output_csv,
            output_csv_sha256=csv_sha,
        )
        database_sha = sha256_file(temporary_database_path)

        metadata: dict[str, Any] = {
            "run_id": run_id,
            "started_at": started_text,
            "completed_at": completed_text,
            "source_run_id": source_run_id,
            "source_id": SOURCE_ID,
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "decision_ids": ["D-005", "D-007", "D-008"],
            "approval_status": "processed_candidate_owner_review_pending",
            "validation_result": "passed",
            "warnings": [],
            "row_count": len(observations),
            "excluded_from_processed_load": {
                "source_table_id": "41",
                "reason": "D-008 retains Table 41 as reconciliation evidence only",
            },
            "code": {
                "path": "src/transformation/processed.py",
                "sha256": code_sha,
            },
            "schema": {"path": str(schema_path), "sha256": schema_sha},
            "inputs": [
                {"path": str(interim_csv), "sha256": sha256_file(interim_csv)},
                {
                    "path": str(interim_metadata),
                    "sha256": sha256_file(interim_metadata),
                },
            ],
            "outputs": [
                {"path": str(output_csv), "sha256": csv_sha},
                {"path": str(database_path), "sha256": database_sha},
            ],
            "database_checks": database_checks,
        }

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output_directory,
            suffix=".json",
            delete=False,
        ) as temporary_metadata:
            json.dump(metadata, temporary_metadata, indent=2, sort_keys=True)
            temporary_metadata.write("\n")
            temporary_metadata_path = Path(temporary_metadata.name)
        temporary_paths.append(temporary_metadata_path)

        os.replace(temporary_csv_path, output_csv)
        temporary_paths.remove(temporary_csv_path)
        os.replace(temporary_database_path, database_path)
        temporary_paths.remove(temporary_database_path)
        os.replace(temporary_metadata_path, metadata_path)
        temporary_paths.remove(temporary_metadata_path)
        return metadata
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    interim = Path("data/interim/uk_business_data_survey/2026-06-18")
    parser.add_argument(
        "--interim-csv",
        type=Path,
        default=interim / "ai_use_by_size.csv",
    )
    parser.add_argument(
        "--interim-metadata",
        type=Path,
        default=interim / "ai_use_by_size.metadata.json",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("sql/schema.sql"),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=(
            Path("data/processed/uk_business_data_survey/2026-06-18")
        ),
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Explicitly replace all three versioned processed candidate files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = datetime.now(timezone.utc).replace(microsecond=0)
    interim_metadata = verify_interim_evidence(
        args.interim_csv,
        args.interim_metadata,
    )
    run_id = started_at.strftime("%Y%m%dT%H%M%SZ")
    observations = transform_table42(args.interim_csv, run_id=run_id)
    metadata = write_processed_candidate(
        args.output_directory,
        observations,
        interim_csv=args.interim_csv,
        interim_metadata=args.interim_metadata,
        schema_path=args.schema,
        source_run_id=interim_metadata["run_id"],
        started_at=started_at,
        replace=args.replace,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
