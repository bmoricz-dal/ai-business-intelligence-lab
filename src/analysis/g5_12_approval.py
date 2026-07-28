"""Preserve the accepted G5-11 result as an approved internal snapshot."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any


DRAFT_STATUS = "draft_analysis_owner_review_pending"
APPROVED_STATUS = "approved_for_analysis"
SOURCE_TASK_ID = "G5-11"
APPROVAL_TASK_ID = "G5-12"
EXPECTED_ANALYSIS_ID = "20260723T101743Z"
EXPECTED_RESULT_SHA256 = (
    "dd84088a34c925767dc86786000e6299d6636c5e2c6fba18148c055840beda09"
)
EXPECTED_METADATA_SHA256 = (
    "8b2fdb221ccc54c135b58feaf2823107335f8d161760046eeafd7a950aad86c2"
)
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_draft_result(
    result_path: Path,
    result_metadata_path: Path,
) -> dict[str, Any]:
    if sha256_file(result_path) != EXPECTED_RESULT_SHA256:
        raise ValueError("G5-11 result checksum mismatch")
    if sha256_file(result_metadata_path) != EXPECTED_METADATA_SHA256:
        raise ValueError("G5-11 metadata checksum mismatch")

    metadata = json.loads(result_metadata_path.read_text(encoding="utf-8"))
    expected_fields = {
        "task_id": SOURCE_TASK_ID,
        "analysis_id": EXPECTED_ANALYSIS_ID,
        "candidate_finding_id": "F-002",
        "analysis_type": "descriptive_conditional",
        "approval_status": DRAFT_STATUS,
        "validation_result": "passed",
    }
    for field, expected in expected_fields.items():
        if metadata.get(field) != expected:
            raise ValueError(f"Unexpected G5-11 metadata field: {field}")
    if metadata.get("warnings"):
        raise ValueError("The G5-11 result has warnings")
    if metadata.get("output", {}).get("row_count") != 4:
        raise ValueError("Unexpected G5-11 row count")
    if metadata.get("output", {}).get("sha256") != EXPECTED_RESULT_SHA256:
        raise ValueError("G5-11 metadata does not match the result")

    checks = metadata.get("checks", {})
    expected_checks = {
        "approved_row_count": 4,
        "primary_sme_count": 3,
        "reference_benchmark_count": 1,
        "source_table_ids": ["48"],
        "indicator_ids": ["ai_tools_integrated_with_systems"],
        "denominator_ids": ["uk_businesses_using_ai_technologies"],
        "confidence_levels": [0.95],
    }
    for field, expected in expected_checks.items():
        if checks.get(field) != expected:
            raise ValueError(f"Unexpected G5-11 analytical check: {field}")

    with result_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError("Unexpected G5-11 CSV row count")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("Unexpected G5-11 size rows")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("Unexpected G5-11 analytical roles")
    if {row["source_table_id"] for row in rows} != {"48"}:
        raise ValueError("G5-11 result contains a non-Table 48 row")
    if {row["indicator_id"] for row in rows} != {
        "ai_tools_integrated_with_systems"
    }:
        raise ValueError("G5-11 result mixes indicators")
    if {row["denominator_id"] for row in rows} != {
        "uk_businesses_using_ai_technologies"
    }:
        raise ValueError("G5-11 result changes or mixes denominators")
    return metadata


def approve_result(
    draft_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-016",
) -> dict[str, Any]:
    result_path = draft_directory / "result.csv"
    result_metadata_path = draft_directory / "result.metadata.json"
    draft_metadata = verify_draft_result(result_path, result_metadata_path)

    approved_result = approved_directory / "result.csv"
    approval_metadata = approved_directory / "approval.metadata.json"
    existing = [
        path for path in (approved_result, approval_metadata) if path.exists()
    ]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved G5-11 result: "
            + ", ".join(str(path) for path in existing)
        )

    approved_directory.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "wb", dir=approved_directory, suffix=".csv", delete=False
        ) as temporary_result_file:
            temporary_result = Path(temporary_result_file.name)
        temporary_paths.append(temporary_result)
        shutil.copyfile(result_path, temporary_result)
        approved_result_sha = sha256_file(temporary_result)
        if approved_result_sha != EXPECTED_RESULT_SHA256:
            raise ValueError("Approved copy changed the G5-11 result")

        approved_text = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "approval_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": APPROVAL_TASK_ID,
            "source_task_id": SOURCE_TASK_ID,
            "finding_id": "F-002",
            "approval_status": APPROVED_STATUS,
            "source_analysis_id": draft_metadata["analysis_id"],
            "source_approval_status": draft_metadata["approval_status"],
            "draft_inputs": [
                {"path": str(result_path), "sha256": sha256_file(result_path)},
                {
                    "path": str(result_metadata_path),
                    "sha256": sha256_file(result_metadata_path),
                },
            ],
            "output": {
                "path": str(approved_result),
                "sha256": approved_result_sha,
                "row_count": draft_metadata["output"]["row_count"],
            },
            "checks": draft_metadata["checks"],
            "validation_result": "passed",
            "warnings": [],
            "result_bytes_unchanged": True,
            "governance_boundary": (
                "Approved for controlled internal analysis only. Percentages "
                "retain the conditional AI-user denominator. No all-business "
                "conversion, formal significance claim, causal claim, chart, "
                "report wording, external sharing, or publication is approved."
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

        os.replace(temporary_result, approved_result)
        temporary_paths.remove(temporary_result)
        os.replace(temporary_metadata, approval_metadata)
        temporary_paths.remove(temporary_metadata)
        return metadata
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(
        "data/processed/uk_business_data_survey/2026-06-18/analysis/"
        "g5_11_ai_integration_by_size"
    )
    parser.add_argument("--draft-directory", type=Path, default=base)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=base / "approved" / EXPECTED_ANALYSIS_ID,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = approve_result(
        args.draft_directory,
        args.approved_directory,
        approved_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
