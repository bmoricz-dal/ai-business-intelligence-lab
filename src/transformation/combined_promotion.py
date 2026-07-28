"""Promote the accepted G5-09 combined candidate to an approved snapshot."""

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
from src.transformation.promotion import CORE_FIELDS


EXPECTED_CANDIDATE_STATUS = "processed_candidate_owner_review_pending"
APPROVED_STATUS = "approved_processed"
EXPECTED_CANDIDATE_METADATA_SHA256 = (
    "6df92a78c1a56ad2b50a825102a3ade2e05637b298dad0dd3ea01de2bd717b25"
)
EXPECTED_CANDIDATE_CSV_SHA256 = (
    "352b20dc4a529cd07a669ac70ad6dfde4a2cd2f76afb8f0f5e2824d524067042"
)
EXPECTED_CANDIDATE_DB_SHA256 = (
    "0618af3d1e384a1dd118bcf30b8e5bb114ed4e234c7bb568551d6b667bdc987e"
)
EXPECTED_SIZES = ("micro", "small", "medium", "large")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def _database_rows(
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


def _csv_values(
    rows: list[dict[str, str]],
    fields: list[str] | tuple[str, ...] = OUTPUT_FIELDS,
) -> list[tuple[str, ...]]:
    return [tuple(row[field] for field in fields) for row in rows]


def verify_combined_candidate(
    candidate_directory: Path,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    csv_path = candidate_directory / "observations.csv"
    database_path = candidate_directory / "sme_intelligence.sqlite"
    metadata_path = candidate_directory / "processing.metadata.json"
    expected = {
        csv_path: EXPECTED_CANDIDATE_CSV_SHA256,
        database_path: EXPECTED_CANDIDATE_DB_SHA256,
        metadata_path: EXPECTED_CANDIDATE_METADATA_SHA256,
    }
    for path, expected_hash in expected.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing G5-09 candidate artifact: {path}")
        if sha256_file(path) != expected_hash:
            raise ValueError(f"G5-09 candidate checksum mismatch: {path.name}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("task_id") != "G5-09":
        raise ValueError("Unexpected combined-candidate task")
    if metadata.get("candidate_finding_id") != "F-002":
        raise ValueError("Unexpected candidate finding identifier")
    if metadata.get("approval_status") != EXPECTED_CANDIDATE_STATUS:
        raise ValueError("Combined candidate is not awaiting owner review")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("Combined candidate did not pass cleanly")
    if metadata.get("decision_ids") != ["D-008", "D-009", "D-014"]:
        raise ValueError("Combined candidate approval lineage is incomplete")
    recorded = {
        Path(item["path"]).name: item["sha256"] for item in metadata["outputs"]
    }
    if recorded.get(csv_path.name) != sha256_file(csv_path):
        raise ValueError("Combined CSV does not match candidate metadata")
    if recorded.get(database_path.name) != sha256_file(database_path):
        raise ValueError("Combined database does not match candidate metadata")

    rows = _read_csv(csv_path)
    if len(rows) != 8:
        raise ValueError("Combined candidate must contain eight observations")
    if tuple(row["dimension_value"] for row in rows[:4]) != EXPECTED_SIZES:
        raise ValueError("Table 42 business-size rows are incomplete")
    if tuple(row["dimension_value"] for row in rows[4:]) != EXPECTED_SIZES:
        raise ValueError("Table 48 business-size rows are incomplete")
    if [row["source_table_id"] for row in rows] != ["42"] * 4 + ["48"] * 4:
        raise ValueError("Combined candidate table ordering is incorrect")
    if {row["approval_status"] for row in rows[:4]} != {APPROVED_STATUS}:
        raise ValueError("Table 42 rows lost their prior approval")
    if {row["approval_status"] for row in rows[4:]} != {
        "accepted_for_schema_design"
    }:
        raise ValueError("Table 48 rows have an unexpected candidate status")
    if {
        (row["source_table_id"], row["denominator_id"]) for row in rows
    } != {
        ("42", "all_uk_businesses"),
        ("48", "uk_businesses_using_ai_technologies"),
    }:
        raise ValueError("Combined candidate denominator mapping is incorrect")

    database_hash_before = sha256_file(database_path)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Combined candidate database integrity check failed")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Combined candidate database foreign-key check failed")
        if _database_rows(connection) != _csv_values(rows):
            raise ValueError("Combined candidate CSV and database do not reconcile")
    finally:
        connection.close()
    if sha256_file(database_path) != database_hash_before:
        raise ValueError("Candidate verification changed the database")
    return metadata, rows


def _write_approved_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=OUTPUT_FIELDS)
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
        release_statuses = connection.execute(
            "SELECT DISTINCT release_status FROM dataset_releases"
        ).fetchall()
        run_statuses = connection.execute(
            "SELECT DISTINCT approval_status FROM pipeline_runs"
        ).fetchall()
    finally:
        connection.close()

    if integrity != "ok" or foreign_keys:
        raise ValueError("Approved combined database integrity check failed")
    if counts != (8, 6, 2, 8, 0):
        raise ValueError(f"Approved combined row reconciliation failed: {counts}")
    if table_denominators != [
        ("42", "all_uk_businesses", 4),
        ("48", "uk_businesses_using_ai_technologies", 4),
    ]:
        raise ValueError("Approved combined denominator mapping failed")
    if reference_counts != {
        "indicator_count": 2,
        "denominator_count": 2,
        "pipeline_run_count": 2,
    }:
        raise ValueError("Approved combined reference counts failed")
    if release_statuses != [(APPROVED_STATUS,)]:
        raise ValueError("Dataset release approval is incomplete")
    if run_statuses != [(APPROVED_STATUS,)]:
        raise ValueError("Pipeline-run approval is incomplete")
    return {
        "integrity_check": integrity,
        "foreign_key_error_count": len(foreign_keys),
        "observation_count": counts[0],
        "primary_count": counts[1],
        "reference_benchmark_count": counts[2],
        "approved_processed_count": counts[3],
        "table41_count": counts[4],
        "table_denominator_counts": [
            {
                "source_table_id": row[0],
                "denominator_id": row[1],
                "row_count": row[2],
            }
            for row in table_denominators
        ],
        **reference_counts,
    }


def promote_combined_candidate(
    candidate_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-015",
) -> dict[str, Any]:
    candidate_metadata, candidate_rows = verify_combined_candidate(
        candidate_directory
    )
    approved_csv = approved_directory / "observations.csv"
    approved_database = approved_directory / "sme_intelligence.sqlite"
    approval_metadata = approved_directory / "approval.metadata.json"
    outputs = (approved_csv, approved_database, approval_metadata)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved combined snapshot: "
            + ", ".join(str(path) for path in existing)
        )

    approved_directory.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    candidate_hashes_before = {
        name: sha256_file(candidate_directory / name)
        for name in (
            "observations.csv",
            "sme_intelligence.sqlite",
            "processing.metadata.json",
        )
    }
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=approved_directory, suffix=".csv", delete=False
        ) as temporary_csv_file:
            temporary_csv = Path(temporary_csv_file.name)
        temporary_paths.append(temporary_csv)
        _write_approved_csv(temporary_csv, candidate_rows)

        with tempfile.NamedTemporaryFile(
            "wb", dir=approved_directory, suffix=".sqlite", delete=False
        ) as temporary_database_file:
            temporary_database = Path(temporary_database_file.name)
        temporary_paths.append(temporary_database)
        database_checks = _write_approved_database(
            candidate_directory / "sme_intelligence.sqlite",
            temporary_database,
        )

        approved_rows = _read_csv(temporary_csv)
        if _csv_values(candidate_rows, CORE_FIELDS) != _csv_values(
            approved_rows, CORE_FIELDS
        ):
            raise ValueError("Combined promotion changed analytical core values")
        connection = sqlite3.connect(temporary_database)
        try:
            if _database_rows(connection) != _csv_values(approved_rows):
                raise ValueError("Approved combined CSV and database do not reconcile")
        finally:
            connection.close()
        if candidate_hashes_before != {
            name: sha256_file(candidate_directory / name)
            for name in candidate_hashes_before
        }:
            raise ValueError("Combined promotion changed the reviewed candidate")

        approved_text = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "promotion_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": "G5-10",
            "candidate_finding_id": "F-002",
            "approval_status": APPROVED_STATUS,
            "source_run_id": candidate_metadata["run_id"],
            "source_candidate_status": candidate_metadata["approval_status"],
            "candidate_inputs": [
                {
                    "path": str(candidate_directory / name),
                    "sha256": file_hash,
                }
                for name, file_hash in candidate_hashes_before.items()
            ],
            "outputs": [
                {"path": str(approved_csv), "sha256": sha256_file(temporary_csv)},
                {
                    "path": str(approved_database),
                    "sha256": sha256_file(temporary_database),
                },
            ],
            "validation_result": "passed",
            "warnings": [],
            "core_values_unchanged": True,
            "candidate_files_unchanged": True,
            "database_checks": database_checks,
            "governance_boundary": (
                "Approved for controlled F-002 SQL analysis. F-002 itself, "
                "charts, report wording, external sharing, and publication "
                "remain unapproved."
            ),
        }
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=approved_directory,
            suffix=".json",
            delete=False,
        ) as temporary_metadata_file:
            json.dump(metadata, temporary_metadata_file, indent=2, sort_keys=True)
            temporary_metadata_file.write("\n")
            temporary_metadata = Path(temporary_metadata_file.name)
        temporary_paths.append(temporary_metadata)

        for temporary, final in zip(
            (temporary_csv, temporary_database, temporary_metadata),
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
    parser.add_argument(
        "--candidate-directory",
        type=Path,
        default=base / "candidates" / "g5_09_combined",
    )
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=base / "approved" / "20260723T091557Z",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = promote_combined_candidate(
        args.candidate_directory,
        args.approved_directory,
        approved_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
