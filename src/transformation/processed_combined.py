"""Build the G5-09 combined Table 42 and Table 48 processed candidate.

The existing D-009-approved Table 42 snapshot is copied without changing its
rows. D-014-approved Table 48 observations are added under a separate
conditional denominator and remain pending owner review.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Any

from src.transformation.processed import OUTPUT_FIELDS


SOURCE_ID = "dsit_ukbds_2026"
DATASET_ID = "uk_business_data_survey"
DATASET_VERSION = "2026-06-18"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")
BASELINE_TABLE = "42"
BASELINE_INDICATOR = "uses_any_ai_based_technologies"
BASELINE_DENOMINATOR = "all_uk_businesses"
INTEGRATION_TABLE = "48"
INTEGRATION_QUESTION = "Q_INTEGRATED_AI"
INTEGRATION_INDICATOR = "ai_tools_integrated_with_systems"
INTEGRATION_DENOMINATOR_ID = "uk_businesses_using_ai_technologies"
INTEGRATION_DENOMINATOR_LABEL = (
    "UK businesses that use Artificial Intelligence technologies"
)
NEW_ROW_STATUS = "accepted_for_schema_design"
CANDIDATE_STATUS = "processed_candidate_owner_review_pending"

EXPECTED_BASELINE_APPROVAL_SHA256 = (
    "5b44a42152cb6eb155a6c3fdbb2f29cd66f9475343e2d569e5a9b535086d29cf"
)
EXPECTED_BASELINE_CSV_SHA256 = (
    "932bc34b70b5dd16b649150ee0a8ce71107b2526b6bf5d0379e3f5cd4e09ec2a"
)
EXPECTED_BASELINE_DB_SHA256 = (
    "978f1437bb45a08334b0f5365162d0cec63395b9eccb6494777e132b1889bf45"
)
EXPECTED_INTEGRATION_APPROVAL_SHA256 = (
    "c9e8617805de4bbbf8543ddaa777ecc00021097a9d86e480dd61b8c17c173d4f"
)
EXPECTED_INTEGRATION_CSV_SHA256 = (
    "6bfbce1c9b81ffef0e8afc14c18e61fac86ca0ff43d87a52760e6de8e3c4efdc"
)
EXPECTED_SCHEMA_SHA256 = (
    "7cd27110cd30b9bd8f96b0f6d5046474b132cd75e9734ba5845f10a5a7e93017"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def _ordered_database_rows(
    connection: sqlite3.Connection,
) -> list[tuple[str, ...]]:
    columns = ", ".join(OUTPUT_FIELDS)
    values = connection.execute(
        f"""
        SELECT {columns}
        FROM observations
        ORDER BY CAST(source_table_id AS INTEGER),
                 CASE dimension_value
                     WHEN 'micro' THEN 1
                     WHEN 'small' THEN 2
                     WHEN 'medium' THEN 3
                     WHEN 'large' THEN 4
                 END
        """
    ).fetchall()
    return [
        tuple("" if value is None else str(value) for value in row)
        for row in values
    ]


def _csv_core(rows: list[dict[str, str]]) -> list[tuple[str, ...]]:
    return [tuple(row[field] for field in OUTPUT_FIELDS) for row in rows]


def verify_approved_baseline(
    baseline_directory: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> tuple[dict[str, Any], Path, Path, list[dict[str, str]]]:
    csv_path = baseline_directory / "observations.csv"
    database_path = baseline_directory / "sme_intelligence.sqlite"
    approval_path = baseline_directory / "approval.metadata.json"
    for path in (csv_path, database_path, approval_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing D-009 baseline artifact: {path}")

    if enforce_registered_checksums:
        expected = {
            csv_path: EXPECTED_BASELINE_CSV_SHA256,
            database_path: EXPECTED_BASELINE_DB_SHA256,
            approval_path: EXPECTED_BASELINE_APPROVAL_SHA256,
        }
        for path, expected_hash in expected.items():
            if sha256_file(path) != expected_hash:
                raise ValueError(f"D-009 baseline checksum mismatch: {path.name}")

    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("decision_id") != "D-009":
        raise ValueError("Baseline is not the D-009-approved snapshot")
    if approval.get("approval_status") != "approved_processed":
        raise ValueError("Baseline is not approved processed data")
    if approval.get("validation_result") != "passed" or approval.get("warnings"):
        raise ValueError("Baseline approval did not pass cleanly")
    recorded = {
        Path(item["path"]).name: item["sha256"] for item in approval["outputs"]
    }
    if recorded.get(csv_path.name) != sha256_file(csv_path):
        raise ValueError("D-009 baseline CSV does not match approval metadata")
    if recorded.get(database_path.name) != sha256_file(database_path):
        raise ValueError("D-009 baseline database does not match approval metadata")

    rows = _read_csv(csv_path)
    if len(rows) != 4:
        raise ValueError("D-009 baseline must contain four observations")
    if tuple(row["dimension_value"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("D-009 baseline size rows are incomplete")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("D-009 baseline roles are incorrect")
    if {row["source_table_id"] for row in rows} != {BASELINE_TABLE}:
        raise ValueError("D-009 baseline includes an unexpected source table")
    if {row["indicator_id"] for row in rows} != {BASELINE_INDICATOR}:
        raise ValueError("D-009 baseline includes an unexpected indicator")
    if {row["denominator_id"] for row in rows} != {BASELINE_DENOMINATOR}:
        raise ValueError("D-009 baseline denominator is incorrect")
    if {row["approval_status"] for row in rows} != {"approved_processed"}:
        raise ValueError("D-009 baseline row approval status is incorrect")

    database_hash_before = sha256_file(database_path)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("D-009 baseline database integrity check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("D-009 baseline database foreign-key check failed")
        if _ordered_database_rows(connection) != _csv_core(rows):
            raise ValueError("D-009 baseline CSV and database do not reconcile")
    finally:
        connection.close()
    if sha256_file(database_path) != database_hash_before:
        raise ValueError("Read-only baseline verification changed the database")
    return approval, csv_path, database_path, rows


def verify_approved_integration_input(
    integration_directory: Path,
    *,
    enforce_registered_checksums: bool = True,
) -> tuple[dict[str, Any], Path, list[dict[str, str]]]:
    csv_path = integration_directory / "ai_integration_among_ai_users_by_size.csv"
    approval_path = integration_directory / "approval.metadata.json"
    for path in (csv_path, approval_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing D-014 integration artifact: {path}")

    if enforce_registered_checksums:
        if sha256_file(csv_path) != EXPECTED_INTEGRATION_CSV_SHA256:
            raise ValueError("D-014 integration CSV checksum mismatch")
        if sha256_file(approval_path) != EXPECTED_INTEGRATION_APPROVAL_SHA256:
            raise ValueError("D-014 approval metadata checksum mismatch")

    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("decision_id") != "D-014":
        raise ValueError("Integration input is not approved under D-014")
    if (
        approval.get("approval_status")
        != "approved_input_for_processed_transformation"
    ):
        raise ValueError("Integration input is not approved for transformation")
    if approval.get("validation_result") != "passed" or approval.get("warnings"):
        raise ValueError("D-014 approval did not pass cleanly")
    if approval.get("denominator") != INTEGRATION_DENOMINATOR_LABEL:
        raise ValueError("D-014 approval has an unexpected denominator")
    if approval.get("outputs", [{}])[0].get("sha256") != sha256_file(csv_path):
        raise ValueError("D-014 integration CSV does not match approval metadata")

    rows = _read_csv(csv_path)
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("D-014 integration size rows are incomplete")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("D-014 integration roles are incorrect")
    required = {
        "source_id": SOURCE_ID,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "table_id": INTEGRATION_TABLE,
        "indicator_id": INTEGRATION_INDICATOR,
        "period": "2025-10-10/2026-01-28",
        "population": INTEGRATION_DENOMINATOR_LABEL,
        "denominator": INTEGRATION_DENOMINATOR_LABEL,
        "unit": "proportion",
        "source_status": "observed",
    }
    for row in rows:
        for field, expected in required.items():
            if row[field] != expected:
                raise ValueError(
                    f"Unexpected D-014 {field} for {row['business_size']}"
                )
        lower = float(row["lower_limit"])
        estimate = float(row["estimate"])
        upper = float(row["upper_limit"])
        if not 0 <= lower <= estimate <= upper <= 1:
            raise ValueError(
                f"Invalid D-014 interval for {row['business_size']}"
            )
        if int(row["sample_base"]) <= 0:
            raise ValueError(f"Invalid D-014 base for {row['business_size']}")
    return approval, csv_path, rows


def transform_table48(
    rows: list[dict[str, str]],
    *,
    run_id: str,
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for expected_size, expected_role, row in zip(
        EXPECTED_SIZES,
        EXPECTED_ROLES,
        rows,
        strict=True,
    ):
        if row["business_size"] != expected_size:
            raise ValueError("Unexpected Table 48 business-size order")
        if row["scope_role"] != expected_role:
            raise ValueError("Unexpected Table 48 analytical role")
        observations.append(
            {
                "observation_id": (
                    f"{SOURCE_ID}:{DATASET_ID}:{DATASET_VERSION}:"
                    f"{INTEGRATION_TABLE}:{INTEGRATION_INDICATOR}:"
                    f"business_size:{expected_size}"
                ),
                "source_id": SOURCE_ID,
                "dataset_id": DATASET_ID,
                "dataset_version": DATASET_VERSION,
                "source_table_id": INTEGRATION_TABLE,
                "source_question_id": INTEGRATION_QUESTION,
                "indicator_id": INTEGRATION_INDICATOR,
                "period_start": "2025-10-10",
                "period_end": "2026-01-28",
                "population_label": INTEGRATION_DENOMINATOR_LABEL,
                "denominator_id": INTEGRATION_DENOMINATOR_ID,
                "unit": "proportion",
                "dimension_type": "business_size",
                "dimension_value": expected_size,
                "source_dimension_label": row["source_business_size_label"],
                "scope_role": expected_role,
                "estimate": float(row["estimate"]),
                "lower_limit": float(row["lower_limit"]),
                "upper_limit": float(row["upper_limit"]),
                "confidence_level": 0.95,
                "sample_base": int(row["sample_base"]),
                "source_status": "observed",
                "run_id": run_id,
                "approval_status": NEW_ROW_STATUS,
                "notes": (
                    row["notes"]
                    + " Processed candidate created under D-014; "
                    "owner output review pending."
                ),
            }
        )
    return observations


def validate_combined_rows(
    baseline_rows: list[dict[str, str]],
    integration_rows: list[dict[str, Any]],
) -> None:
    if len(baseline_rows) != 4 or len(integration_rows) != 4:
        raise ValueError("Combined candidate requires four rows per indicator")
    all_rows: list[dict[str, Any]] = [*baseline_rows, *integration_rows]
    if len({row["observation_id"] for row in all_rows}) != 8:
        raise ValueError("Combined observation IDs are not unique")
    if [row["source_table_id"] for row in all_rows] != [
        "42",
        "42",
        "42",
        "42",
        "48",
        "48",
        "48",
        "48",
    ]:
        raise ValueError("Combined source-table ordering is incorrect")
    denominator_pairs = {
        (row["source_table_id"], row["denominator_id"]) for row in all_rows
    }
    if denominator_pairs != {
        (BASELINE_TABLE, BASELINE_DENOMINATOR),
        (INTEGRATION_TABLE, INTEGRATION_DENOMINATOR_ID),
    }:
        raise ValueError("Table and denominator mapping is incorrect")
    if {row["approval_status"] for row in baseline_rows} != {
        "approved_processed"
    }:
        raise ValueError("Baseline rows lost their approved status")
    if {row["approval_status"] for row in integration_rows} != {
        NEW_ROW_STATUS
    }:
        raise ValueError("New Table 48 rows have an unexpected status")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _build_database(
    *,
    database_path: Path,
    baseline_database: Path,
    integration_rows: list[dict[str, Any]],
    combined_csv_rows: list[dict[str, str]],
    run_id: str,
    started_at: str,
    completed_at: str,
    code_sha256: str,
    metadata_path: Path,
    output_csv: Path,
    output_csv_sha256: str,
) -> dict[str, Any]:
    shutil.copyfile(baseline_database, database_path)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.execute(
            "INSERT INTO indicators VALUES (?, ?, ?, ?)",
            (
                INTEGRATION_INDICATOR,
                "AI tools integrated with business systems",
                (
                    "Business reported that at least one AI tool it uses is "
                    "integrated with its systems"
                ),
                "proportion",
            ),
        )
        connection.execute(
            "INSERT INTO denominators VALUES (?, ?, ?)",
            (
                INTEGRATION_DENOMINATOR_ID,
                INTEGRATION_DENOMINATOR_LABEL,
                (
                    "UK businesses within the published business-size category "
                    "that report using Artificial Intelligence technologies"
                ),
            ),
        )
        connection.execute(
            "INSERT INTO pipeline_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                started_at,
                completed_at,
                "src/transformation/processed_combined.py",
                code_sha256,
                str(metadata_path),
                str(output_csv),
                output_csv_sha256,
                "passed",
                NEW_ROW_STATUS,
            ),
        )
        columns = ", ".join(OUTPUT_FIELDS)
        parameters = ", ".join(f":{field}" for field in OUTPUT_FIELDS)
        connection.executemany(
            f"INSERT INTO observations ({columns}) VALUES ({parameters})",
            integration_rows,
        )
        connection.commit()

        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        counts = connection.execute(
            """
            SELECT COUNT(*),
                   SUM(scope_role = 'primary'),
                   SUM(scope_role = 'reference_benchmark'),
                   SUM(approval_status = 'approved_processed'),
                   SUM(approval_status = 'accepted_for_schema_design'),
                   SUM(source_table_id = '41')
            FROM observations
            """
        ).fetchone()
        table_denominators = connection.execute(
            """
            SELECT source_table_id, denominator_id, COUNT(*)
            FROM observations
            GROUP BY source_table_id, denominator_id
            ORDER BY CAST(source_table_id AS INTEGER)
            """
        ).fetchall()
        reference_counts = {
            "indicator_count": connection.execute(
                "SELECT COUNT(*) FROM indicators"
            ).fetchone()[0],
            "denominator_count": connection.execute(
                "SELECT COUNT(*) FROM denominators"
            ).fetchone()[0],
            "pipeline_run_count": connection.execute(
                "SELECT COUNT(*) FROM pipeline_runs"
            ).fetchone()[0],
        }
        database_rows = _ordered_database_rows(connection)
    finally:
        connection.close()

    if integrity != "ok" or foreign_keys:
        raise ValueError("Combined database integrity or foreign-key check failed")
    if counts != (8, 6, 2, 4, 4, 0):
        raise ValueError(f"Combined database row reconciliation failed: {counts}")
    if table_denominators != [
        (BASELINE_TABLE, BASELINE_DENOMINATOR, 4),
        (INTEGRATION_TABLE, INTEGRATION_DENOMINATOR_ID, 4),
    ]:
        raise ValueError("Combined database denominator mapping failed")
    if reference_counts != {
        "indicator_count": 2,
        "denominator_count": 2,
        "pipeline_run_count": 2,
    }:
        raise ValueError("Combined database reference-table counts failed")
    if database_rows != _csv_core(combined_csv_rows):
        raise ValueError("Combined CSV and SQLite observations do not reconcile")
    return {
        "integrity_check": integrity,
        "foreign_key_error_count": len(foreign_keys),
        "observation_count": counts[0],
        "primary_count": counts[1],
        "reference_benchmark_count": counts[2],
        "approved_processed_count": counts[3],
        "pending_table48_count": counts[4],
        "table41_count": counts[5],
        "table_denominator_counts": [
            {
                "source_table_id": row[0],
                "denominator_id": row[1],
                "row_count": row[2],
            }
            for row in table_denominators
        ],
        **reference_counts,
        "csv_sqlite_reconciled": True,
    }


def write_combined_candidate(
    output_directory: Path,
    *,
    baseline_directory: Path,
    integration_directory: Path,
    schema_path: Path,
    started_at: datetime,
    replace: bool = False,
) -> dict[str, Any]:
    output_csv = output_directory / "observations.csv"
    output_database = output_directory / "sme_intelligence.sqlite"
    metadata_path = output_directory / "processing.metadata.json"
    existing = [
        path
        for path in (output_csv, output_database, metadata_path)
        if path.exists()
    ]
    if existing and not replace:
        raise FileExistsError(
            "Refusing to overwrite combined candidate: "
            + ", ".join(str(path) for path in existing)
        )
    if sha256_file(schema_path) != EXPECTED_SCHEMA_SHA256:
        raise ValueError("D-008 schema checksum mismatch")

    baseline_approval, baseline_csv, baseline_database, baseline_rows = (
        verify_approved_baseline(baseline_directory)
    )
    integration_approval, integration_csv, source_integration_rows = (
        verify_approved_integration_input(integration_directory)
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    started_at = started_at.astimezone(timezone.utc).replace(microsecond=0)
    completed_at = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = started_at.strftime("%Y%m%dT%H%M%SZ")
    started_text = started_at.isoformat().replace("+00:00", "Z")
    completed_text = completed_at.isoformat().replace("+00:00", "Z")
    integration_rows = transform_table48(
        source_integration_rows,
        run_id=run_id,
    )
    validate_combined_rows(baseline_rows, integration_rows)
    code_sha = sha256_file(Path(__file__))
    baseline_database_hash_before = sha256_file(baseline_database)

    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=output_directory, suffix=".csv", delete=False
        ) as temporary_csv_file:
            temporary_csv = Path(temporary_csv_file.name)
        temporary_paths.append(temporary_csv)
        _write_csv(temporary_csv, [*baseline_rows, *integration_rows])
        output_csv_sha = sha256_file(temporary_csv)
        combined_csv_rows = _read_csv(temporary_csv)

        with tempfile.NamedTemporaryFile(
            "wb", dir=output_directory, suffix=".sqlite", delete=False
        ) as temporary_database_file:
            temporary_database = Path(temporary_database_file.name)
        temporary_paths.append(temporary_database)
        database_checks = _build_database(
            database_path=temporary_database,
            baseline_database=baseline_database,
            integration_rows=integration_rows,
            combined_csv_rows=combined_csv_rows,
            run_id=run_id,
            started_at=started_text,
            completed_at=completed_text,
            code_sha256=code_sha,
            metadata_path=metadata_path,
            output_csv=output_csv,
            output_csv_sha256=output_csv_sha,
        )
        output_database_sha = sha256_file(temporary_database)
        if sha256_file(baseline_database) != baseline_database_hash_before:
            raise ValueError("G5-09 changed the D-009-approved baseline database")

        metadata: dict[str, Any] = {
            "run_id": run_id,
            "started_at": started_text,
            "completed_at": completed_text,
            "task_id": "G5-09",
            "candidate_finding_id": "F-002",
            "source_id": SOURCE_ID,
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "decision_ids": ["D-008", "D-009", "D-014"],
            "approval_status": CANDIDATE_STATUS,
            "validation_result": "passed",
            "warnings": [],
            "row_count": 8,
            "row_status_counts": {
                "approved_processed_table42": 4,
                "pending_table48": 4,
            },
            "code": {
                "path": "src/transformation/processed_combined.py",
                "sha256": code_sha,
            },
            "schema": {
                "path": str(schema_path),
                "sha256": sha256_file(schema_path),
            },
            "inputs": [
                {"path": str(baseline_csv), "sha256": sha256_file(baseline_csv)},
                {
                    "path": str(baseline_database),
                    "sha256": baseline_database_hash_before,
                },
                {
                    "path": str(baseline_directory / "approval.metadata.json"),
                    "sha256": sha256_file(
                        baseline_directory / "approval.metadata.json"
                    ),
                    "decision_id": baseline_approval["decision_id"],
                },
                {
                    "path": str(integration_csv),
                    "sha256": sha256_file(integration_csv),
                },
                {
                    "path": str(integration_directory / "approval.metadata.json"),
                    "sha256": sha256_file(
                        integration_directory / "approval.metadata.json"
                    ),
                    "decision_id": integration_approval["decision_id"],
                },
            ],
            "outputs": [
                {"path": str(output_csv), "sha256": output_csv_sha},
                {
                    "path": str(output_database),
                    "sha256": output_database_sha,
                },
            ],
            "database_checks": database_checks,
            "excluded_from_processed_load": {
                "source_table_id": "41",
                "reason": "D-008 retains Table 41 as reconciliation evidence only",
            },
            "governance_boundary": (
                "Combined processed candidate for owner review. Table 42 rows "
                "retain D-009 approval; Table 48 rows are not approved processed "
                "data. F-002 and publication remain unapproved."
            ),
        }
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output_directory,
            suffix=".json",
            delete=False,
        ) as temporary_metadata_file:
            json.dump(metadata, temporary_metadata_file, indent=2, sort_keys=True)
            temporary_metadata_file.write("\n")
            temporary_metadata = Path(temporary_metadata_file.name)
        temporary_paths.append(temporary_metadata)

        for temporary, final in zip(
            (temporary_csv, temporary_database, temporary_metadata),
            (output_csv, output_database, metadata_path),
            strict=True,
        ):
            os.replace(temporary, final)
            temporary_paths.remove(temporary)
        return metadata
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    processed = Path("data/processed/uk_business_data_survey/2026-06-18")
    interim = Path("data/interim/uk_business_data_survey/2026-06-18")
    parser.add_argument(
        "--baseline-directory",
        type=Path,
        default=processed / "approved" / "20260723T072638Z",
    )
    parser.add_argument(
        "--integration-directory",
        type=Path,
        default=interim / "approved" / "20260723T085731Z",
    )
    parser.add_argument("--schema", type=Path, default=Path("sql/schema.sql"))
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=processed / "candidates" / "g5_09_combined",
    )
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = write_combined_candidate(
        args.output_directory,
        baseline_directory=args.baseline_directory,
        integration_directory=args.integration_directory,
        schema_path=args.schema,
        started_at=datetime.now(timezone.utc),
        replace=args.replace,
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
