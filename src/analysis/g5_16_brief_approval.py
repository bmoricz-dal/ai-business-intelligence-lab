"""Preserve the accepted G5-15 combined brief as an approved snapshot."""

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


DRAFT_STATUS = "draft_evidence_brief_owner_review_pending"
APPROVED_STATUS = "approved_for_internal_product_development"
SOURCE_TASK = "G5-15"
APPROVAL_TASK = "G5-16"
EXPECTED_BRIEF_ID = "20260723T115400Z"
EXPECTED_BRIEF_SHA256 = (
    "363a370dbd6647a62f2d367305987e431308a6eddccb3b72cd66251c4f090599"
)
EXPECTED_METADATA_SHA256 = (
    "0c91c5b59076add8fde8e6d840c888b743569ede2b249d6bc553ebef55905978"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_brief_draft(
    draft_directory: Path,
) -> tuple[dict[str, Any], Path, Path]:
    brief_path = draft_directory / "evidence_brief.md"
    metadata_path = draft_directory / "brief.metadata.json"
    for path in (brief_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing G5-15 brief artifact: {path}")
    if sha256_file(brief_path) != EXPECTED_BRIEF_SHA256:
        raise ValueError("G5-15 evidence-brief checksum mismatch")
    if sha256_file(metadata_path) != EXPECTED_METADATA_SHA256:
        raise ValueError("G5-15 brief metadata checksum mismatch")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected_fields = {
        "task_id": SOURCE_TASK,
        "brief_id": EXPECTED_BRIEF_ID,
        "finding_ids": ["F-001", "F-002"],
        "approval_status": DRAFT_STATUS,
        "validation_result": "passed",
    }
    for field, expected in expected_fields.items():
        if metadata.get(field) != expected:
            raise ValueError(f"Unexpected G5-15 brief field: {field}")
    if metadata.get("warnings"):
        raise ValueError("The G5-15 brief has warnings")
    if metadata.get("output", {}).get("sha256") != EXPECTED_BRIEF_SHA256:
        raise ValueError("G5-15 metadata does not match the evidence brief")

    required_checks: dict[str, Any] = {
        "approved_f001_result_used": True,
        "approved_f001_chart_used": True,
        "approved_f001_brief_baseline_used": True,
        "approved_f002_result_used": True,
        "approved_f002_chart_used": True,
        "measure_count": 2,
        "row_count": 8,
        "all_values_reconciled": True,
        "denominator_ids": [
            "all_uk_businesses",
            "uk_businesses_using_ai_technologies",
        ],
        "denominators_kept_separate": True,
        "cross_denominator_arithmetic_present": False,
        "confidence_intervals_present": True,
        "sample_base_warning_present": True,
        "benchmark_role_present": True,
        "non_significance_boundary_present": True,
        "non_causal_boundary_present": True,
        "publication_boundary_present": True,
    }
    for check, expected in required_checks.items():
        if metadata.get("checks", {}).get(check) != expected:
            raise ValueError(f"G5-15 brief failed required check: {check}")

    brief = brief_path.read_text(encoding="utf-8")
    required_phrases = (
        "Denominator: all UK businesses",
        "These are not percentages of all UK businesses",
        "not combined arithmetically",
        "does not multiply, divide or subtract",
        "Publication status: Not approved",
    )
    for phrase in required_phrases:
        if phrase not in brief:
            raise ValueError(f"G5-15 brief is missing safeguard: {phrase}")
    return metadata, brief_path, metadata_path


def approve_brief(
    draft_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-018",
) -> dict[str, Any]:
    draft_metadata, brief_path, draft_metadata_path = verify_brief_draft(
        draft_directory
    )
    approved_brief = approved_directory / brief_path.name
    approval_metadata = approved_directory / "approval.metadata.json"
    outputs = (approved_brief, approval_metadata)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved G5-15 brief: "
            + ", ".join(str(path) for path in existing)
        )

    approved_directory.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "wb", dir=approved_directory, suffix=".md", delete=False
        ) as temporary_file:
            temporary_brief = Path(temporary_file.name)
        temporary_paths.append(temporary_brief)
        shutil.copyfile(brief_path, temporary_brief)
        copied_hash = sha256_file(temporary_brief)
        if copied_hash != EXPECTED_BRIEF_SHA256:
            raise ValueError("Approved G5-15 brief copy changed")

        approved_text_time = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "approval_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text_time,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": APPROVAL_TASK,
            "source_task_id": SOURCE_TASK,
            "finding_ids": ["F-001", "F-002"],
            "approval_status": APPROVED_STATUS,
            "source_brief_id": draft_metadata["brief_id"],
            "source_approval_status": draft_metadata["approval_status"],
            "draft_inputs": [
                {"path": str(brief_path), "sha256": sha256_file(brief_path)},
                {
                    "path": str(draft_metadata_path),
                    "sha256": sha256_file(draft_metadata_path),
                },
            ],
            "outputs": [
                {"path": str(approved_brief), "sha256": copied_hash},
            ],
            "checks": draft_metadata["checks"],
            "validation_result": "passed",
            "warnings": [],
            "brief_bytes_unchanged": True,
            "governance_boundary": (
                "Approved for internal Report 02 production. Both denominators "
                "and all limitations are mandatory. The generated PDF, external "
                "sharing, and publication require separate review."
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
            (temporary_brief, temporary_metadata),
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
    draft = Path(
        "data/processed/uk_business_data_survey/2026-06-18/analysis/"
        "g5_15_second_evidence_brief"
    )
    parser.add_argument("--draft-directory", type=Path, default=draft)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=draft / "approved" / EXPECTED_BRIEF_ID,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = approve_brief(
        args.draft_directory,
        args.approved_directory,
        approved_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
