"""Run and validate the first D-009-approved descriptive SQL analysis."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APPROVED_RUN_ID = "20260723T072638Z"
APPROVED_STATUS = "approved_processed"
DRAFT_STATUS = "draft_analysis_owner_review_pending"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_approved_snapshot(
    database_path: Path,
    approval_metadata_path: Path,
) -> dict[str, Any]:
    metadata = json.loads(approval_metadata_path.read_text(encoding="utf-8"))
    if metadata.get("approval_status") != APPROVED_STATUS:
        raise ValueError("The selected snapshot is not approved_processed")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("The selected approved snapshot did not pass cleanly")
    if not metadata.get("core_values_unchanged"):
        raise ValueError("The approved snapshot lacks unchanged-value confirmation")
    recorded = {
        Path(item["path"]).name: item["sha256"] for item in metadata["outputs"]
    }
    actual_database_sha = sha256_file(database_path)
    if recorded.get(database_path.name) != actual_database_sha:
        raise ValueError("Approved database checksum mismatch")
    return metadata


def execute_query(
    database_path: Path,
    query_path: Path,
) -> tuple[list[str], list[dict[str, Any]]]:
    query = query_path.read_text(encoding="utf-8")
    connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        rows = [dict(row) for row in connection.execute(query).fetchall()]
        columns = list(rows[0]) if rows else []
    finally:
        connection.close()
    validate_result(rows)
    return columns, rows


def validate_result(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 4:
        raise ValueError(f"Expected four descriptive rows, got {len(rows)}")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("The descriptive result has unexpected size rows or order")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("The descriptive result has unexpected analytical roles")
    if {row["approval_status"] for row in rows} != {APPROVED_STATUS}:
        raise ValueError("The descriptive result includes an unapproved row")
    if {row["source_table_id"] for row in rows} != {"42"}:
        raise ValueError("The descriptive result includes an excluded source table")
    if {row["denominator_id"] for row in rows} != {"all_uk_businesses"}:
        raise ValueError("The descriptive result mixes denominators")
    if {row["confidence_level"] for row in rows} != {0.95}:
        raise ValueError("The descriptive result has an unexpected confidence level")
    for row in rows:
        if not 0 <= row["lower_limit"] <= row["estimate"] <= row["upper_limit"] <= 1:
            raise ValueError(f"Invalid interval for {row['business_size']}")
        if row["sample_base"] <= 0:
            raise ValueError(f"Invalid sample base for {row['business_size']}")


def write_draft_result(
    output_directory: Path,
    *,
    database_path: Path,
    approval_metadata_path: Path,
    query_path: Path,
    started_at: datetime,
) -> dict[str, Any]:
    approval_metadata = verify_approved_snapshot(
        database_path,
        approval_metadata_path,
    )
    columns, rows = execute_query(database_path, query_path)
    output_csv = output_directory / "result.csv"
    metadata_path = output_directory / "result.metadata.json"
    existing = [path for path in (output_csv, metadata_path) if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite analysis output: "
            + ", ".join(str(path) for path in existing)
        )

    output_directory.mkdir(parents=True, exist_ok=True)
    completed_at = datetime.now(timezone.utc).replace(microsecond=0)
    started_text = started_at.astimezone(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    completed_text = completed_at.isoformat().replace("+00:00", "Z")
    analysis_id = started_at.strftime("%Y%m%dT%H%M%SZ")

    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=output_directory,
            suffix=".csv",
            delete=False,
        ) as temporary_csv:
            writer = csv.DictWriter(temporary_csv, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
            temporary_csv_path = Path(temporary_csv.name)
        temporary_paths.append(temporary_csv_path)
        result_sha = sha256_file(temporary_csv_path)

        metadata: dict[str, Any] = {
            "analysis_id": analysis_id,
            "started_at": started_text,
            "completed_at": completed_text,
            "task_id": "G5-01",
            "decision_ids": ["D-005", "D-008", "D-009"],
            "research_question": (
                "What proportion of businesses in each published size group "
                "reported using any AI-based technology?"
            ),
            "analysis_type": "descriptive",
            "approval_status": DRAFT_STATUS,
            "validation_result": "passed",
            "warnings": [],
            "source_run_id": approval_metadata["source_run_id"],
            "approved_snapshot": {
                "database_path": str(database_path),
                "database_sha256": sha256_file(database_path),
                "approval_metadata_path": str(approval_metadata_path),
                "approval_metadata_sha256": sha256_file(approval_metadata_path),
            },
            "query": {
                "path": str(query_path),
                "sha256": sha256_file(query_path),
            },
            "output": {
                "path": str(output_csv),
                "sha256": result_sha,
                "row_count": len(rows),
            },
            "checks": {
                "approved_row_count": len(rows),
                "primary_sme_count": sum(
                    row["scope_role"] == "primary" for row in rows
                ),
                "reference_benchmark_count": sum(
                    row["scope_role"] == "reference_benchmark" for row in rows
                ),
                "source_table_ids": sorted(
                    {row["source_table_id"] for row in rows}
                ),
                "denominator_ids": sorted(
                    {row["denominator_id"] for row in rows}
                ),
                "confidence_levels": sorted(
                    {row["confidence_level"] for row in rows}
                ),
            },
            "interpretation_boundary": (
                "Draft descriptive result only. It does not test statistical "
                "differences, establish causation, or authorise publication."
            ),
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
        os.replace(temporary_metadata_path, metadata_path)
        temporary_paths.remove(temporary_metadata_path)
        return metadata
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    approved = (
        Path("data/processed/uk_business_data_survey/2026-06-18/approved")
        / APPROVED_RUN_ID
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=approved / "sme_intelligence.sqlite",
    )
    parser.add_argument(
        "--approval-metadata",
        type=Path,
        default=approved / "approval.metadata.json",
    )
    parser.add_argument(
        "--query",
        type=Path,
        default=Path("sql/g5_01_ai_use_by_size.sql"),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=(
            Path("data/processed/uk_business_data_survey/2026-06-18/analysis")
            / "g5_01_ai_use_by_size"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = write_draft_result(
        args.output_directory,
        database_path=args.database,
        approval_metadata_path=args.approval_metadata,
        query_path=args.query,
        started_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
