"""Run and validate the D-015-approved Table 48 descriptive analysis."""

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
APPROVED_RUN_ID = "20260723T091557Z"
APPROVED_STATUS = "approved_processed"
DRAFT_STATUS = "draft_analysis_owner_review_pending"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")
EXPECTED_DATABASE_SHA256 = (
    "e10767b28ed6073186642c9f10f5c238bfa319fe9b02f2c33d4e9155f6239fde"
)
EXPECTED_APPROVAL_METADATA_SHA256 = (
    "b95c482bb97dd94e052261a12ec456d076b4d274fc22aeb2e87c1eedfe72fc1d"
)


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
    if sha256_file(approval_metadata_path) != EXPECTED_APPROVAL_METADATA_SHA256:
        raise ValueError("D-015 approval metadata checksum mismatch")
    metadata = json.loads(approval_metadata_path.read_text(encoding="utf-8"))
    expected_fields = {
        "approval_status": APPROVED_STATUS,
        "decision_id": "D-015",
        "task_id": "G5-10",
        "candidate_finding_id": "F-002",
        "source_run_id": APPROVED_RUN_ID,
        "validation_result": "passed",
    }
    for field, expected in expected_fields.items():
        if metadata.get(field) != expected:
            raise ValueError(f"Unexpected D-015 approval field: {field}")
    if metadata.get("warnings"):
        raise ValueError("The D-015-approved snapshot has warnings")
    if not metadata.get("core_values_unchanged"):
        raise ValueError("The approved snapshot lacks unchanged-value confirmation")
    if not metadata.get("candidate_files_unchanged"):
        raise ValueError("The approved snapshot lacks unchanged-candidate confirmation")

    recorded = {
        Path(item["path"]).name: item["sha256"] for item in metadata["outputs"]
    }
    actual_database_sha = sha256_file(database_path)
    if actual_database_sha != EXPECTED_DATABASE_SHA256:
        raise ValueError("D-015 approved database checksum mismatch")
    if recorded.get(database_path.name) != actual_database_sha:
        raise ValueError("Approved database does not match D-015 metadata")
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
    if {row["source_table_id"] for row in rows} != {"48"}:
        raise ValueError("The descriptive result includes a non-Table 48 row")
    if {row["indicator_id"] for row in rows} != {
        "ai_tools_integrated_with_systems"
    }:
        raise ValueError("The descriptive result mixes indicators")
    if {row["denominator_id"] for row in rows} != {
        "uk_businesses_using_ai_technologies"
    }:
        raise ValueError("The descriptive result mixes or changes denominators")
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
            "task_id": "G5-11",
            "decision_ids": ["D-011", "D-014", "D-015"],
            "candidate_finding_id": "F-002",
            "research_question": (
                "Among UK businesses that report using AI technologies, what "
                "proportion say at least one AI tool is integrated with their "
                "systems, by published business-size group?"
            ),
            "analysis_type": "descriptive_conditional",
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
                "indicator_ids": sorted(
                    {row["indicator_id"] for row in rows}
                ),
                "denominator_ids": sorted(
                    {row["denominator_id"] for row in rows}
                ),
                "confidence_levels": sorted(
                    {row["confidence_level"] for row in rows}
                ),
            },
            "interpretation_boundary": (
                "Draft descriptive conditional result only. Percentages refer "
                "only to businesses reporting AI use, not all UK businesses. "
                "The result does not support denominator conversion, formal "
                "significance, causation, finding approval, or publication."
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
        default=Path("sql/g5_11_ai_integration_by_size.sql"),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=(
            Path("data/processed/uk_business_data_survey/2026-06-18/analysis")
            / "g5_11_ai_integration_by_size"
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
