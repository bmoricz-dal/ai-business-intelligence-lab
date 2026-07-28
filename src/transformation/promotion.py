"""Promote a reviewed processed candidate to an approved, immutable snapshot."""

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


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_CANDIDATE_STATUS = "processed_candidate_owner_review_pending"
EXPECTED_ROW_STATUS = "accepted_for_schema_design"
APPROVED_STATUS = "approved_processed"
EXPECTED_SOURCE_TABLE = "42"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
CORE_FIELDS = (
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
    "notes",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_candidate(candidate_directory: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    csv_path = candidate_directory / "observations.csv"
    database_path = candidate_directory / "sme_intelligence.sqlite"
    metadata_path = candidate_directory / "processing.metadata.json"
    for path in (csv_path, database_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing processed candidate file: {path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("validation_result") != "passed":
        raise ValueError("Processed candidate did not pass technical validation")
    if metadata.get("approval_status") != EXPECTED_CANDIDATE_STATUS:
        raise ValueError("Processed candidate is not awaiting owner review")
    if metadata.get("warnings"):
        raise ValueError("Processed candidate contains unresolved warnings")

    recorded_outputs = {
        Path(item["path"]).name: item["sha256"] for item in metadata["outputs"]
    }
    for path in (csv_path, database_path):
        if recorded_outputs.get(path.name) != sha256_file(path):
            raise ValueError(f"Processed candidate checksum mismatch: {path.name}")

    with csv_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError(f"Expected four candidate observations, got {len(rows)}")
    if tuple(row["dimension_value"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("Candidate business-size rows are incomplete or out of order")
    if {row["source_table_id"] for row in rows} != {EXPECTED_SOURCE_TABLE}:
        raise ValueError("Candidate includes a source table outside D-008")
    if {row["approval_status"] for row in rows} != {EXPECTED_ROW_STATUS}:
        raise ValueError("Candidate rows have an unexpected approval status")
    if [row["scope_role"] for row in rows] != [
        "primary",
        "primary",
        "primary",
        "reference_benchmark",
    ]:
        raise ValueError("Candidate row roles do not match D-008")

    connection = sqlite3.connect(database_path)
    try:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Candidate SQLite integrity check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Candidate SQLite foreign-key check failed")
        database_rows = connection.execute(
            """
            SELECT observation_id, source_id, dataset_id, dataset_version,
                   source_table_id, source_question_id, indicator_id,
                   period_start, period_end, population_label, denominator_id,
                   unit, dimension_type, dimension_value, source_dimension_label,
                   scope_role, estimate, lower_limit, upper_limit,
                   confidence_level, sample_base, source_status, run_id, notes
            FROM observations
            ORDER BY CASE dimension_value
                WHEN 'micro' THEN 1 WHEN 'small' THEN 2
                WHEN 'medium' THEN 3 WHEN 'large' THEN 4 END
            """
        ).fetchall()
    finally:
        connection.close()

    csv_core = [tuple(row[field] for field in CORE_FIELDS) for row in rows]
    database_core = [tuple("" if value is None else str(value) for value in row) for row in database_rows]
    if csv_core != database_core:
        raise ValueError("Candidate CSV and SQLite core values do not reconcile")
    return metadata, rows


def _write_approved_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            approved = dict(row)
            approved["approval_status"] = APPROVED_STATUS
            writer.writerow(approved)


def _write_approved_database(
    candidate_database: Path,
    approved_database: Path,
) -> dict[str, Any]:
    shutil.copyfile(candidate_database, approved_database)
    connection = sqlite3.connect(approved_database)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.execute(
            "UPDATE dataset_releases SET release_status = ?",
            (APPROVED_STATUS,),
        )
        connection.execute(
            "UPDATE pipeline_runs SET approval_status = ?",
            (APPROVED_STATUS,),
        )
        connection.execute(
            "UPDATE observations SET approval_status = ?",
            (APPROVED_STATUS,),
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
                   SUM(source_table_id = '41')
            FROM observations
            """
        ).fetchone()
        release_statuses = [
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT release_status FROM dataset_releases"
            )
        ]
        run_statuses = [
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT approval_status FROM pipeline_runs"
            )
        ]
    finally:
        connection.close()

    if integrity != "ok" or foreign_keys:
        raise ValueError("Approved SQLite integrity or foreign-key validation failed")
    if counts != (4, 3, 1, 4, 0):
        raise ValueError(f"Approved SQLite row reconciliation failed: {counts}")
    if release_statuses != [APPROVED_STATUS] or run_statuses != [APPROVED_STATUS]:
        raise ValueError("Approved SQLite governance statuses are incomplete")
    return {
        "integrity_check": integrity,
        "foreign_key_error_count": len(foreign_keys),
        "observation_count": counts[0],
        "primary_count": counts[1],
        "reference_benchmark_count": counts[2],
        "approved_processed_count": counts[3],
        "table41_count": counts[4],
    }


def promote_candidate(
    candidate_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-009",
) -> dict[str, Any]:
    """Create a separate approved snapshot without changing the candidate."""

    candidate_metadata, candidate_rows = verify_candidate(candidate_directory)
    outputs = (
        approved_directory / "observations.csv",
        approved_directory / "sme_intelligence.sqlite",
        approved_directory / "approval.metadata.json",
    )
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved output: "
            + ", ".join(str(path) for path in existing)
        )

    approved_directory.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=approved_directory, suffix=".csv", delete=False
        ) as temporary_csv:
            temporary_csv_path = Path(temporary_csv.name)
        temporary_paths.append(temporary_csv_path)
        _write_approved_csv(temporary_csv_path, candidate_rows)

        with tempfile.NamedTemporaryFile(
            "wb", dir=approved_directory, suffix=".sqlite", delete=False
        ) as temporary_database:
            temporary_database_path = Path(temporary_database.name)
        temporary_paths.append(temporary_database_path)
        database_checks = _write_approved_database(
            candidate_directory / "sme_intelligence.sqlite",
            temporary_database_path,
        )

        approved_csv_sha = sha256_file(temporary_csv_path)
        approved_database_sha = sha256_file(temporary_database_path)
        candidate_csv_sha = sha256_file(candidate_directory / "observations.csv")
        candidate_database_sha = sha256_file(
            candidate_directory / "sme_intelligence.sqlite"
        )
        approved_text = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "promotion_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "approval_status": APPROVED_STATUS,
            "source_run_id": candidate_metadata["run_id"],
            "source_candidate_status": candidate_metadata["approval_status"],
            "candidate_inputs": [
                {
                    "path": str(candidate_directory / "observations.csv"),
                    "sha256": candidate_csv_sha,
                },
                {
                    "path": str(candidate_directory / "sme_intelligence.sqlite"),
                    "sha256": candidate_database_sha,
                },
                {
                    "path": str(candidate_directory / "processing.metadata.json"),
                    "sha256": sha256_file(
                        candidate_directory / "processing.metadata.json"
                    ),
                },
            ],
            "outputs": [
                {
                    "path": str(approved_directory / "observations.csv"),
                    "sha256": approved_csv_sha,
                },
                {
                    "path": str(approved_directory / "sme_intelligence.sqlite"),
                    "sha256": approved_database_sha,
                },
            ],
            "validation_result": "passed",
            "warnings": [],
            "core_values_unchanged": True,
            "database_checks": database_checks,
            "governance_boundary": (
                "Approved for controlled analysis; not approved for publication "
                "and no finding is approved by this promotion."
            ),
        }

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=approved_directory,
            suffix=".json",
            delete=False,
        ) as temporary_metadata:
            json.dump(metadata, temporary_metadata, indent=2, sort_keys=True)
            temporary_metadata.write("\n")
            temporary_metadata_path = Path(temporary_metadata.name)
        temporary_paths.append(temporary_metadata_path)

        for temporary, final in zip(
            (
                temporary_csv_path,
                temporary_database_path,
                temporary_metadata_path,
            ),
            outputs,
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
    base = Path("data/processed/uk_business_data_survey/2026-06-18")
    parser.add_argument("--candidate-directory", type=Path, default=base)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=base / "approved" / "20260723T072638Z",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = promote_candidate(
        args.candidate_directory,
        args.approved_directory,
        approved_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
