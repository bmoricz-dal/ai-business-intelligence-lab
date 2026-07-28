"""Promote the accepted G5-04 chart to an approved internal snapshot."""

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
import xml.etree.ElementTree as ET


DRAFT_STATUS = "draft_chart_owner_review_pending"
APPROVED_STATUS = "approved_for_internal_product_development"
EXPECTED_TASK = "G5-04"
EXPECTED_FINDING = "F-001"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_chart_draft(
    draft_directory: Path,
) -> tuple[dict[str, Any], Path, Path]:
    svg_path = draft_directory / "ai_use_by_size_ci.svg"
    text_path = draft_directory / "text_equivalent.md"
    metadata_path = draft_directory / "chart.metadata.json"
    for path in (svg_path, text_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing chart draft artifact: {path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("task_id") != EXPECTED_TASK:
        raise ValueError("Unexpected chart task")
    if metadata.get("finding_id") != EXPECTED_FINDING:
        raise ValueError("Unexpected chart finding")
    if metadata.get("approval_status") != DRAFT_STATUS:
        raise ValueError("The chart is not awaiting owner review")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("The chart draft did not pass cleanly")

    recorded = {
        Path(item["path"]).name: item["sha256"] for item in metadata["outputs"]
    }
    for path in (svg_path, text_path):
        if recorded.get(path.name) != sha256_file(path):
            raise ValueError(f"Chart draft checksum mismatch: {path.name}")
    ET.parse(svg_path)
    required_checks = {
        "has_svg_title": True,
        "has_svg_description": True,
        "has_text_equivalent": True,
        "confidence_intervals_shown": True,
        "large_benchmark_distinct_by_colour_and_shape": True,
        "significance_claim_present": False,
    }
    for check, expected in required_checks.items():
        if metadata.get("checks", {}).get(check) is not expected:
            raise ValueError(f"Chart draft failed required check: {check}")
    return metadata, svg_path, text_path


def approve_chart(
    draft_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-012",
) -> dict[str, Any]:
    draft_metadata, svg_path, text_path = verify_chart_draft(draft_directory)
    approved_svg = approved_directory / svg_path.name
    approved_text = approved_directory / text_path.name
    approval_metadata = approved_directory / "approval.metadata.json"
    outputs = (approved_svg, approved_text, approval_metadata)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved chart: "
            + ", ".join(str(path) for path in existing)
        )

    approved_directory.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    try:
        copied: list[tuple[Path, Path, str]] = []
        for source, suffix in ((svg_path, ".svg"), (text_path, ".md")):
            with tempfile.NamedTemporaryFile(
                "wb", dir=approved_directory, suffix=suffix, delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
            temporary_paths.append(temporary_path)
            shutil.copyfile(source, temporary_path)
            copied.append((source, temporary_path, sha256_file(temporary_path)))

        for source, _temporary, copied_hash in copied:
            if copied_hash != sha256_file(source):
                raise ValueError(f"Approved chart copy changed: {source.name}")

        approved_text_time = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "approval_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text_time,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": EXPECTED_TASK,
            "finding_id": EXPECTED_FINDING,
            "approval_status": APPROVED_STATUS,
            "source_chart_id": draft_metadata["chart_id"],
            "source_approval_status": draft_metadata["approval_status"],
            "draft_inputs": [
                {"path": str(svg_path), "sha256": sha256_file(svg_path)},
                {"path": str(text_path), "sha256": sha256_file(text_path)},
                {
                    "path": str(draft_directory / "chart.metadata.json"),
                    "sha256": sha256_file(
                        draft_directory / "chart.metadata.json"
                    ),
                },
            ],
            "outputs": [
                {
                    "path": str(approved_svg),
                    "sha256": copied[0][2],
                },
                {
                    "path": str(approved_text),
                    "sha256": copied[1][2],
                },
            ],
            "validation_result": "passed",
            "warnings": [],
            "chart_bytes_unchanged": True,
            "text_bytes_unchanged": True,
            "governance_boundary": (
                "Approved for continued internal product development. Public "
                "wording, external sharing, and publication remain unapproved."
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
            (copied[0][1], copied[1][1], temporary_metadata),
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
        "g5_04_ai_use_chart"
    )
    parser.add_argument("--draft-directory", type=Path, default=draft)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=draft / "approved" / "20260723T081736Z",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = approve_chart(
        args.draft_directory,
        args.approved_directory,
        approved_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
