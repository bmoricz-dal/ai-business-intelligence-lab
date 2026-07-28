"""Approve the reviewed Table 48 scope as a controlled transformation input."""

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


EXPECTED_TASK = "G5-07"
EXPECTED_CANDIDATE_FINDING = "F-002"
EXPECTED_TABLE = "48"
EXPECTED_INDICATOR = "ai_tools_integrated_with_systems"
EXPECTED_DENOMINATOR = (
    "UK businesses that use Artificial Intelligence technologies"
)
EXPECTED_CANDIDATE_STATUS = "unreviewed_interim_candidate"
APPROVED_STATUS = "approved_input_for_processed_transformation"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_candidate(
    candidate_directory: Path,
) -> tuple[dict[str, Any], Path, Path, list[dict[str, str]]]:
    csv_path = candidate_directory / "ai_integration_among_ai_users_by_size.csv"
    metadata_path = csv_path.with_suffix(".metadata.json")
    for path in (csv_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing Table 48 candidate artifact: {path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("task_id") != EXPECTED_TASK:
        raise ValueError("Unexpected Table 48 candidate task")
    if metadata.get("candidate_finding_id") != EXPECTED_CANDIDATE_FINDING:
        raise ValueError("Unexpected candidate finding identifier")
    if metadata.get("table_id") != EXPECTED_TABLE:
        raise ValueError("Unexpected source table")
    if metadata.get("indicator_id") != EXPECTED_INDICATOR:
        raise ValueError("Unexpected integration indicator")
    if metadata.get("denominator") != EXPECTED_DENOMINATOR:
        raise ValueError("Unexpected Table 48 denominator")
    if metadata.get("approval_status") != EXPECTED_CANDIDATE_STATUS:
        raise ValueError("Table 48 candidate is not awaiting scope review")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("Table 48 candidate did not pass cleanly")
    if metadata.get("output", {}).get("sha256") != sha256_file(csv_path):
        raise ValueError("Table 48 candidate checksum mismatch")

    with csv_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("Table 48 business-size rows are incomplete or out of order")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("Table 48 scope roles are incorrect")
    if {row["table_id"] for row in rows} != {EXPECTED_TABLE}:
        raise ValueError("Candidate includes an unexpected source table")
    if {row["indicator_id"] for row in rows} != {EXPECTED_INDICATOR}:
        raise ValueError("Candidate includes an unexpected indicator")
    if {row["denominator"] for row in rows} != {EXPECTED_DENOMINATOR}:
        raise ValueError("Candidate denominator is inconsistent")
    if {row["source_status"] for row in rows} != {"observed"}:
        raise ValueError("Candidate includes a non-observed target row")

    for row in rows:
        lower = float(row["lower_limit"])
        estimate = float(row["estimate"])
        upper = float(row["upper_limit"])
        if not 0 <= lower <= estimate <= upper <= 1:
            raise ValueError(
                f"Invalid estimate or interval for {row['business_size']}"
            )
        if int(row["sample_base"]) <= 0:
            raise ValueError(f"Invalid sample base for {row['business_size']}")
    return metadata, csv_path, metadata_path, rows


def approve_scope(
    candidate_directory: Path,
    approved_directory: Path,
    *,
    approved_at: datetime,
    decision_id: str = "D-014",
) -> dict[str, Any]:
    candidate, csv_path, candidate_metadata_path, rows = verify_candidate(
        candidate_directory
    )
    approved_csv = approved_directory / csv_path.name
    approval_metadata = approved_directory / "approval.metadata.json"
    outputs = (approved_csv, approval_metadata)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite approved Table 48 scope: "
            + ", ".join(str(path) for path in existing)
        )

    approved_directory.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "wb", dir=approved_directory, suffix=".csv", delete=False
        ) as temporary_file:
            temporary_csv = Path(temporary_file.name)
        temporary_paths.append(temporary_csv)
        shutil.copyfile(csv_path, temporary_csv)
        copied_hash = sha256_file(temporary_csv)
        if copied_hash != sha256_file(csv_path):
            raise ValueError("Approved Table 48 input changed during copying")

        approved_text = approved_at.astimezone(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
        metadata: dict[str, Any] = {
            "approval_id": approved_at.strftime("%Y%m%dT%H%M%SZ"),
            "approved_at": approved_text,
            "approved_by_role": "research_director",
            "decision_id": decision_id,
            "task_id": "G5-08",
            "source_task_id": EXPECTED_TASK,
            "candidate_finding_id": EXPECTED_CANDIDATE_FINDING,
            "source_run_id": candidate["run_id"],
            "source_table_id": EXPECTED_TABLE,
            "indicator_id": EXPECTED_INDICATOR,
            "denominator": EXPECTED_DENOMINATOR,
            "approval_status": APPROVED_STATUS,
            "candidate_inputs": [
                {"path": str(csv_path), "sha256": sha256_file(csv_path)},
                {
                    "path": str(candidate_metadata_path),
                    "sha256": sha256_file(candidate_metadata_path),
                },
            ],
            "outputs": [{"path": str(approved_csv), "sha256": copied_hash}],
            "checks": {
                "row_count": len(rows),
                "primary_count": sum(row["scope_role"] == "primary" for row in rows),
                "benchmark_count": sum(
                    row["scope_role"] == "reference_benchmark" for row in rows
                ),
                "candidate_bytes_unchanged": True,
                "conditional_denominator_preserved": True,
            },
            "validation_result": "passed",
            "warnings": [],
            "governance_boundary": (
                "Approved as input for controlled processed transformation and "
                "analysis design. F-002, public wording, external sharing, and "
                "publication remain unapproved."
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
            (temporary_csv, temporary_metadata),
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
    candidate = Path("data/interim/uk_business_data_survey/2026-06-18")
    parser.add_argument("--candidate-directory", type=Path, default=candidate)
    parser.add_argument(
        "--approved-directory",
        type=Path,
        default=candidate / "approved" / "20260723T085731Z",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = approve_scope(
        args.candidate_directory,
        args.approved_directory,
        approved_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
