"""Promote an accepted G5-01 draft result to an approved internal snapshot."""

from __future__ import annotations

import argparse
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
EXPECTED_TASK_ID = "G5-01"
EXPECTED_ROWS = 4


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
    metadata = json.loads(result_metadata_path.read_text(encoding="utf-8"))
    if metadata.get("task_id") != EXPECTED_TASK_ID:
        raise ValueError("Unexpected analysis task")
    if metadata.get("approval_status") != DRAFT_STATUS:
        raise ValueError("The analysis result is not awaiting owner review")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("The analysis result did not pass cleanly")
    if metadata.get("output", {}).get("row_count") != EXPECTED_ROWS:
        raise ValueError("Unexpected draft analysis row count")
    if metadata.get("output", {}).get("sha256") != sha256_file(result_path):
        raise ValueError("Draft analysis result checksum mismatch")
    return metadata


def approve_result(
    draft_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-010",
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
            "Refusing to overwrite approved analysis: "
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
        if approved_result_sha != draft_metadata["output"]["sha256"]:
            raise ValueError("Approved copy changed the analysis result")

        approved_text = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "approval_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": EXPECTED_TASK_ID,
            "finding_id": "F-001",
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
            "validation_result": "passed",
            "warnings": [],
            "result_bytes_unchanged": True,
            "governance_boundary": (
                "Approved for continued internal analysis only. No chart, public "
                "claim, significance claim, or publication is approved."
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
        "g5_01_ai_use_by_size"
    )
    parser.add_argument("--draft-directory", type=Path, default=base)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=base / "approved" / "20260723T075335Z",
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
