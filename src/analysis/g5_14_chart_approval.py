"""Preserve the accepted G5-13 chart as an approved internal snapshot."""

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
SOURCE_TASK = "G5-13"
APPROVAL_TASK = "G5-14"
EXPECTED_FINDING = "F-002"
EXPECTED_CHART_ID = "20260723T111428Z"
EXPECTED_SVG_NAME = "ai_integration_among_ai_users_by_size_ci.svg"
EXPECTED_SVG_SHA256 = (
    "933ce1b1dc3ff6573983bbaa5d53afa654293ce2aca72c34fbed42fcd328eeee"
)
EXPECTED_TEXT_SHA256 = (
    "b800e63da96f13fb99ee8610b30fd78d2694edcfc5287881b06b1d9eab3fa8fd"
)
EXPECTED_METADATA_SHA256 = (
    "6735fe4b25c9a8788a5727a0b7dc01c0c412c73adc6d52b5f274a55c1c72b2f5"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_chart_draft(
    draft_directory: Path,
) -> tuple[dict[str, Any], Path, Path]:
    svg_path = draft_directory / EXPECTED_SVG_NAME
    text_path = draft_directory / "text_equivalent.md"
    metadata_path = draft_directory / "chart.metadata.json"
    for path in (svg_path, text_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing G5-13 chart artifact: {path}")

    expected_hashes = {
        svg_path: EXPECTED_SVG_SHA256,
        text_path: EXPECTED_TEXT_SHA256,
        metadata_path: EXPECTED_METADATA_SHA256,
    }
    for path, expected in expected_hashes.items():
        if sha256_file(path) != expected:
            raise ValueError(f"G5-13 chart checksum mismatch: {path.name}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected_fields = {
        "task_id": SOURCE_TASK,
        "finding_id": EXPECTED_FINDING,
        "chart_id": EXPECTED_CHART_ID,
        "approval_status": DRAFT_STATUS,
        "validation_result": "passed",
    }
    for field, expected in expected_fields.items():
        if metadata.get(field) != expected:
            raise ValueError(f"Unexpected G5-13 chart field: {field}")
    if metadata.get("warnings"):
        raise ValueError("The G5-13 chart has warnings")

    recorded = {
        Path(item["path"]).name: item["sha256"] for item in metadata["outputs"]
    }
    if recorded.get(svg_path.name) != EXPECTED_SVG_SHA256:
        raise ValueError("G5-13 metadata does not match the SVG")
    if recorded.get(text_path.name) != EXPECTED_TEXT_SHA256:
        raise ValueError("G5-13 metadata does not match the text equivalent")
    if metadata.get("source_result", {}).get("approval_id") != "20260723T102425Z":
        raise ValueError("The chart does not cite the D-016 F-002 approval")

    ET.parse(svg_path)
    required_checks = {
        "row_count": 4,
        "primary_sme_count": 3,
        "reference_benchmark_count": 1,
        "source_table_ids": ["48"],
        "indicator_ids": ["ai_tools_integrated_with_systems"],
        "denominator_ids": ["uk_businesses_using_ai_technologies"],
        "has_svg_title": True,
        "has_svg_description": True,
        "has_text_equivalent": True,
        "conditional_denominator_visible": True,
        "all_business_conversion_present": False,
        "confidence_intervals_shown": True,
        "large_benchmark_distinct_by_colour_and_shape": True,
        "significance_claim_present": False,
    }
    for check, expected in required_checks.items():
        if metadata.get("checks", {}).get(check) != expected:
            raise ValueError(f"G5-13 chart failed required check: {check}")

    svg = svg_path.read_text(encoding="utf-8")
    text = text_path.read_text(encoding="utf-8")
    if "not all UK businesses" not in svg:
        raise ValueError("The chart is missing the conditional-denominator warning")
    if "not percentages of all UK businesses" not in text:
        raise ValueError("The text equivalent is missing the denominator warning")
    return metadata, svg_path, text_path


def approve_chart(
    draft_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-017",
) -> dict[str, Any]:
    draft_metadata, svg_path, text_path = verify_chart_draft(draft_directory)
    approved_svg = approved_directory / svg_path.name
    approved_text = approved_directory / text_path.name
    approval_metadata = approved_directory / "approval.metadata.json"
    outputs = (approved_svg, approved_text, approval_metadata)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved G5-13 chart: "
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
            "task_id": APPROVAL_TASK,
            "source_task_id": SOURCE_TASK,
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
                {"path": str(approved_svg), "sha256": copied[0][2]},
                {"path": str(approved_text), "sha256": copied[1][2]},
            ],
            "checks": draft_metadata["checks"],
            "validation_result": "passed",
            "warnings": [],
            "chart_bytes_unchanged": True,
            "text_bytes_unchanged": True,
            "governance_boundary": (
                "Approved for internal second-report development. The "
                "conditional AI-user denominator and limitations are mandatory. "
                "The report itself, external sharing, and publication remain "
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
        "g5_13_ai_integration_chart"
    )
    parser.add_argument("--draft-directory", type=Path, default=draft)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=draft / "approved" / EXPECTED_CHART_ID,
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
