"""Build the first internal evidence-brief section from approved artifacts."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")
DRAFT_STATUS = "draft_evidence_brief_owner_review_pending"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_inputs(
    result_path: Path,
    result_approval_path: Path,
    chart_path: Path,
    chart_text_path: Path,
    chart_approval_path: Path,
) -> tuple[list[dict[str, str]], dict[str, Any], dict[str, Any]]:
    result_approval = json.loads(result_approval_path.read_text(encoding="utf-8"))
    if result_approval.get("decision_id") != "D-010":
        raise ValueError("Evidence result is not governed by D-010")
    if result_approval.get("approval_status") != "approved_for_analysis":
        raise ValueError("Evidence result is not approved for analysis")
    if result_approval.get("validation_result") != "passed":
        raise ValueError("Evidence result approval did not pass")
    if result_approval.get("output", {}).get("sha256") != sha256_file(result_path):
        raise ValueError("Approved evidence result checksum mismatch")

    chart_approval = json.loads(chart_approval_path.read_text(encoding="utf-8"))
    if chart_approval.get("decision_id") != "D-012":
        raise ValueError("Evidence chart is not governed by D-012")
    if (
        chart_approval.get("approval_status")
        != "approved_for_internal_product_development"
    ):
        raise ValueError("Evidence chart is not approved for internal development")
    if chart_approval.get("validation_result") != "passed":
        raise ValueError("Evidence chart approval did not pass")
    recorded_chart_outputs = {
        Path(item["path"]).name: item["sha256"]
        for item in chart_approval["outputs"]
    }
    for path in (chart_path, chart_text_path):
        if recorded_chart_outputs.get(path.name) != sha256_file(path):
            raise ValueError(f"Approved chart artifact checksum mismatch: {path.name}")

    with result_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError(f"Expected four evidence rows, got {len(rows)}")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("Evidence result has unexpected business-size rows")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("Evidence result has unexpected analytical roles")
    if {row["denominator_id"] for row in rows} != {"all_uk_businesses"}:
        raise ValueError("Evidence result mixes denominators")
    if {row["source_table_id"] for row in rows} != {"42"}:
        raise ValueError("Evidence result includes an excluded source table")

    chart_svg = chart_path.read_text(encoding="utf-8")
    chart_text = chart_text_path.read_text(encoding="utf-8")
    for row in rows:
        value = f"{float(row['estimate_percent']):.1f}%"
        if value not in chart_svg or value not in chart_text:
            raise ValueError(f"Chart artifacts do not reconcile for {value}")
    return rows, result_approval, chart_approval


def render_brief(rows: list[dict[str, str]], chart_relative_path: str) -> str:
    by_size = {row["business_size"]: row for row in rows}

    def estimate(size: str) -> float:
        return float(by_size[size]["estimate_percent"])

    def lower(size: str) -> float:
        return float(by_size[size]["lower_limit_percent"])

    def upper(size: str) -> float:
        return float(by_size[size]["upper_limit_percent"])

    def base(size: str) -> int:
        return int(by_size[size]["sample_base"])

    return f"""# Reported AI use by business size in the UK Business Data Survey 2026

Status: Internal evidence-brief draft  
Evidence status: F-001 approved for internal analysis under D-010  
Chart status: Approved for internal product development under D-012  
Publication status: Not approved

## Key message

In the UK Business Data Survey 2026, the estimated share of businesses reporting at least one listed use of AI-based technologies was {estimate("micro"):.1f}% for micro businesses, {estimate("small"):.1f}% for small businesses and {estimate("medium"):.1f}% for medium businesses. The large-business benchmark was {estimate("large"):.1f}%.

The point estimates rise across the published business-size groups. This is a descriptive result: it does not test whether group differences are statistically significant and does not show that business size causes AI use.

![Reported AI use by business size with 95% confidence intervals]({chart_relative_path})

## Evidence table

| Published size group | Estimate | 95% confidence interval | Rounded unweighted base | Role |
|---|---:|---:|---:|---|
| Micro, up to 9 employees | {estimate("micro"):.1f}% | {lower("micro"):.1f}% to {upper("micro"):.1f}% | {base("micro"):,} | Primary SME group |
| Small, 10 to 49 employees | {estimate("small"):.1f}% | {lower("small"):.1f}% to {upper("small"):.1f}% | {base("small"):,} | Primary SME group |
| Medium, 50 to 249 employees | {estimate("medium"):.1f}% | {lower("medium"):.1f}% to {upper("medium"):.1f}% | {base("medium"):,} | Primary SME group |
| Large, 250 or more employees | {estimate("large"):.1f}% | {lower("large"):.1f}% to {upper("large"):.1f}% | {base("large"):,} | Reference benchmark |

## Why this matters

The result provides a size-specific baseline for deciding which SME groups and questions to investigate next. It does not identify why reported AI use differs, measure readiness or capability, reveal barriers, or establish which intervention would be effective.

## Source and method

- Source: Department for Science, Innovation and Technology, UK Business Data Survey 2026, Table 42.
- Dataset version: 18 June 2026.
- Fieldwork: 10 October 2025 to 28 January 2026.
- Indicator: business reported at least one listed use of AI-based technologies.
- Denominator: all UK businesses within each published business-size category.
- Unit: weighted survey estimate expressed as a percentage.
- Uncertainty: supplied 95% confidence limits.
- Sample bases: published rounded unweighted respondent counts, not counts of UK businesses.
- Large businesses: reference benchmark outside the primary SME scope.

## Limitations and permitted wording

- The chart and table may say that the point estimates rise across the published size groups.
- They must not claim formal statistical significance from the published tables alone.
- They must not imply that business size causes AI use.
- They must not treat the respondent bases as UK business counts.
- They must not substitute the conditional Table 41 denominator.
- They must not be published or shared externally until a separate publication review approves the wording, visual, source note and context.

## Evidence trail

- Finding: F-001.
- Result approval: D-010, approval `20260723T080810Z`.
- Comparison method: D-011.
- Chart approval: D-012, approval `20260723T082541Z`.
- Query: `sql/g5_01_ai_use_by_size.sql`.
- Approved result: `data/processed/uk_business_data_survey/2026-06-18/analysis/g5_01_ai_use_by_size/approved/20260723T075335Z/result.csv`.
- Approved chart: `data/processed/uk_business_data_survey/2026-06-18/analysis/g5_04_ai_use_chart/approved/20260723T081736Z/ai_use_by_size_ci.svg`.
- Full chart text equivalent: `data/processed/uk_business_data_survey/2026-06-18/analysis/g5_04_ai_use_chart/approved/20260723T081736Z/text_equivalent.md`.

## Owner review boundary

This draft is ready for research-director review. Acceptance would authorise continued internal brief and product-layout work only; it would not approve publication or external sharing.
"""


def write_brief_draft(
    output_directory: Path,
    *,
    result_path: Path,
    result_approval_path: Path,
    chart_path: Path,
    chart_text_path: Path,
    chart_approval_path: Path,
    created_at: datetime,
) -> dict[str, Any]:
    rows, result_approval, chart_approval = verify_inputs(
        result_path,
        result_approval_path,
        chart_path,
        chart_text_path,
        chart_approval_path,
    )
    brief_path = output_directory / "evidence_brief.md"
    metadata_path = output_directory / "brief.metadata.json"
    existing = [path for path in (brief_path, metadata_path) if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite evidence brief: "
            + ", ".join(str(path) for path in existing)
        )
    output_directory.mkdir(parents=True, exist_ok=True)

    chart_relative_path = (
        "../g5_04_ai_use_chart/approved/20260723T081736Z/"
        "ai_use_by_size_ci.svg"
    )
    brief = render_brief(rows, chart_relative_path)
    created_text = created_at.astimezone(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    brief_id = created_at.strftime("%Y%m%dT%H%M%SZ")
    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output_directory,
            suffix=".md",
            delete=False,
        ) as temporary_brief:
            temporary_brief.write(brief)
            temporary_brief_path = Path(temporary_brief.name)
        temporary_paths.append(temporary_brief_path)
        brief_sha = sha256_file(temporary_brief_path)

        metadata: dict[str, Any] = {
            "brief_id": brief_id,
            "created_at": created_text,
            "task_id": "G5-05",
            "finding_id": "F-001",
            "decision_ids": ["D-010", "D-011", "D-012"],
            "approval_status": DRAFT_STATUS,
            "inputs": [
                {
                    "path": str(result_path),
                    "sha256": sha256_file(result_path),
                    "approval_id": result_approval["approval_id"],
                },
                {
                    "path": str(chart_path),
                    "sha256": sha256_file(chart_path),
                    "approval_id": chart_approval["approval_id"],
                },
                {
                    "path": str(chart_text_path),
                    "sha256": sha256_file(chart_text_path),
                    "approval_id": chart_approval["approval_id"],
                },
            ],
            "output": {
                "path": str(brief_path),
                "sha256": brief_sha,
            },
            "checks": {
                "approved_result_used": True,
                "approved_chart_used": True,
                "row_count": len(rows),
                "all_values_reconciled": True,
                "denominator_present": True,
                "confidence_intervals_present": True,
                "sample_base_warning_present": True,
                "benchmark_role_present": True,
                "non_significance_boundary_present": True,
                "non_causal_boundary_present": True,
                "publication_boundary_present": True,
            },
            "validation_result": "passed",
            "warnings": [],
            "governance_boundary": (
                "Internal evidence-brief draft for owner review. Publication "
                "and external sharing remain unapproved."
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

        os.replace(temporary_brief_path, brief_path)
        temporary_paths.remove(temporary_brief_path)
        os.replace(temporary_metadata_path, metadata_path)
        temporary_paths.remove(temporary_metadata_path)
        return metadata
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    analysis = Path(
        "data/processed/uk_business_data_survey/2026-06-18/analysis"
    )
    result = analysis / "g5_01_ai_use_by_size/approved/20260723T075335Z"
    chart = analysis / "g5_04_ai_use_chart/approved/20260723T081736Z"
    parser.add_argument("--result", type=Path, default=result / "result.csv")
    parser.add_argument(
        "--result-approval",
        type=Path,
        default=result / "approval.metadata.json",
    )
    parser.add_argument(
        "--chart",
        type=Path,
        default=chart / "ai_use_by_size_ci.svg",
    )
    parser.add_argument(
        "--chart-text",
        type=Path,
        default=chart / "text_equivalent.md",
    )
    parser.add_argument(
        "--chart-approval",
        type=Path,
        default=chart / "approval.metadata.json",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=analysis / "g5_05_evidence_brief",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = write_brief_draft(
        args.output_directory,
        result_path=args.result,
        result_approval_path=args.result_approval,
        chart_path=args.chart,
        chart_text_path=args.chart_text,
        chart_approval_path=args.chart_approval,
        created_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
