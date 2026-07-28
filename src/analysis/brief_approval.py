"""Promote the accepted G5-05 evidence brief to an approved internal snapshot."""

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
EXPECTED_TASK = "G5-05"
EXPECTED_FINDING = "F-001"


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
            raise FileNotFoundError(f"Missing evidence-brief artifact: {path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("task_id") != EXPECTED_TASK:
        raise ValueError("Unexpected evidence-brief task")
    if metadata.get("finding_id") != EXPECTED_FINDING:
        raise ValueError("Unexpected evidence-brief finding")
    if metadata.get("approval_status") != DRAFT_STATUS:
        raise ValueError("The evidence brief is not awaiting owner review")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("The evidence-brief draft did not pass cleanly")
    if metadata.get("output", {}).get("sha256") != sha256_file(brief_path):
        raise ValueError("Evidence-brief draft checksum mismatch")

    required_checks: dict[str, Any] = {
        "all_values_reconciled": True,
        "approved_chart_used": True,
        "approved_result_used": True,
        "benchmark_role_present": True,
        "confidence_intervals_present": True,
        "denominator_present": True,
        "non_causal_boundary_present": True,
        "non_significance_boundary_present": True,
        "publication_boundary_present": True,
        "row_count": 4,
        "sample_base_warning_present": True,
    }
    for check, expected in required_checks.items():
        if metadata.get("checks", {}).get(check) != expected:
            raise ValueError(f"Evidence brief failed required check: {check}")
    return metadata, brief_path, metadata_path


def approve_brief(
    draft_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-013",
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
            "Refusing to overwrite approved evidence brief: "
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
        if copied_hash != sha256_file(brief_path):
            raise ValueError("Approved evidence-brief copy changed")

        approved_text_time = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "approval_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text_time,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": EXPECTED_TASK,
            "review_task_id": "G5-06",
            "finding_id": EXPECTED_FINDING,
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
            "validation_result": "passed",
            "warnings": [],
            "brief_bytes_unchanged": True,
            "governance_boundary": (
                "Approved for continued internal brief and product-layout work. "
                "Public wording, external sharing, and publication remain "
                "unapproved."
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
        "g5_05_evidence_brief"
    )
    parser.add_argument("--draft-directory", type=Path, default=draft)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=draft / "approved" / "20260723T083141Z",
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
