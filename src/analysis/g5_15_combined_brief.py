"""Build the second internal evidence brief from approved F-001 and F-002."""

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

EXPECTED_HASHES = {
    "f001_result": "8f0d29ec30451fbec96aefb5aa0909e31d62c16c0e618bb75d95d809f51d8eb6",
    "f001_result_approval": "3705ea24deea8096bb3c99c8c0a4d4e68b27d451d24bb6951304ae90310476d8",
    "f001_chart": "096df1115a0fde319df3ff2cdfc4d16fa4f1d27973460577411715eb6bc0b8f8",
    "f001_chart_text": "cb8d9bf4a6625944d5776bbcc966b6f16abab6381ca97e700b3e1b9cdebe42c6",
    "f001_chart_approval": "1216452b86fb7270f4bf7cc39768035cf7306cea34059d1c8f7f54dcc2d101a4",
    "f001_brief": "f353b4b0e94a49332dbb170238e9ea85c9035ef159841b1828f89905a827af31",
    "f001_brief_approval": "5e71b14f3daf91d53a47ee4fdd7f4e0a64cb83b9bb5cf933699b63fe52a83321",
    "f002_result": "dd84088a34c925767dc86786000e6299d6636c5e2c6fba18148c055840beda09",
    "f002_result_approval": "a59b7ae9609eb31bb52dc1ae66750d0cb9998d2a3a7a0a669b523ed7ed266236",
    "f002_chart": "933ce1b1dc3ff6573983bbaa5d53afa654293ce2aca72c34fbed42fcd328eeee",
    "f002_chart_text": "b800e63da96f13fb99ee8610b30fd78d2694edcfc5287881b06b1d9eab3fa8fd",
    "f002_chart_approval": "039795fd66e383c0c077509cfe04debdc3a4a163332bb578ba6a17f2ccf76d08",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_hash(path: Path, key: str) -> None:
    if sha256_file(path) != EXPECTED_HASHES[key]:
        raise ValueError(f"Approved input checksum mismatch: {key}")


def _load_rows(
    path: Path,
    *,
    denominator_id: str,
    source_table_id: str,
    indicator_id: str,
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError(f"Expected four approved rows in {path.name}")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError(f"Unexpected business-size rows in {path.name}")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError(f"Unexpected analytical roles in {path.name}")
    if {row["denominator_id"] for row in rows} != {denominator_id}:
        raise ValueError(f"Unexpected denominator in {path.name}")
    if {row["source_table_id"] for row in rows} != {source_table_id}:
        raise ValueError(f"Unexpected source table in {path.name}")
    if {row["indicator_id"] for row in rows} != {indicator_id}:
        raise ValueError(f"Unexpected indicator in {path.name}")
    return rows


def _verify_values_in_chart(
    rows: list[dict[str, str]],
    chart_path: Path,
    chart_text_path: Path,
) -> None:
    svg = chart_path.read_text(encoding="utf-8")
    text = chart_text_path.read_text(encoding="utf-8")
    for row in rows:
        value = f"{float(row['estimate_percent']):.1f}%"
        if value not in svg or value not in text:
            raise ValueError(f"Approved chart artifacts do not reconcile for {value}")


def verify_inputs(
    *,
    f001_result_path: Path,
    f001_result_approval_path: Path,
    f001_chart_path: Path,
    f001_chart_text_path: Path,
    f001_chart_approval_path: Path,
    f001_brief_path: Path,
    f001_brief_approval_path: Path,
    f002_result_path: Path,
    f002_result_approval_path: Path,
    f002_chart_path: Path,
    f002_chart_text_path: Path,
    f002_chart_approval_path: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    paths = {
        "f001_result": f001_result_path,
        "f001_result_approval": f001_result_approval_path,
        "f001_chart": f001_chart_path,
        "f001_chart_text": f001_chart_text_path,
        "f001_chart_approval": f001_chart_approval_path,
        "f001_brief": f001_brief_path,
        "f001_brief_approval": f001_brief_approval_path,
        "f002_result": f002_result_path,
        "f002_result_approval": f002_result_approval_path,
        "f002_chart": f002_chart_path,
        "f002_chart_text": f002_chart_text_path,
        "f002_chart_approval": f002_chart_approval_path,
    }
    for key, path in paths.items():
        _require_hash(path, key)

    f001_result_approval = json.loads(
        f001_result_approval_path.read_text(encoding="utf-8")
    )
    if (
        f001_result_approval.get("decision_id") != "D-010"
        or f001_result_approval.get("finding_id") != "F-001"
        or f001_result_approval.get("approval_status") != "approved_for_analysis"
        or f001_result_approval.get("validation_result") != "passed"
    ):
        raise ValueError("F-001 result is not governed by D-010")
    if f001_result_approval.get("output", {}).get("sha256") != EXPECTED_HASHES[
        "f001_result"
    ]:
        raise ValueError("D-010 metadata does not match the F-001 result")

    f001_chart_approval = json.loads(
        f001_chart_approval_path.read_text(encoding="utf-8")
    )
    if (
        f001_chart_approval.get("decision_id") != "D-012"
        or f001_chart_approval.get("finding_id") != "F-001"
        or f001_chart_approval.get("approval_status")
        != "approved_for_internal_product_development"
        or f001_chart_approval.get("validation_result") != "passed"
    ):
        raise ValueError("F-001 chart is not governed by D-012")

    f001_brief_approval = json.loads(
        f001_brief_approval_path.read_text(encoding="utf-8")
    )
    if (
        f001_brief_approval.get("decision_id") != "D-013"
        or f001_brief_approval.get("finding_id") != "F-001"
        or f001_brief_approval.get("approval_status")
        != "approved_for_internal_product_development"
        or f001_brief_approval.get("validation_result") != "passed"
        or not f001_brief_approval.get("brief_bytes_unchanged")
    ):
        raise ValueError("F-001 baseline brief is not governed by D-013")

    f002_result_approval = json.loads(
        f002_result_approval_path.read_text(encoding="utf-8")
    )
    if (
        f002_result_approval.get("decision_id") != "D-016"
        or f002_result_approval.get("finding_id") != "F-002"
        or f002_result_approval.get("approval_status") != "approved_for_analysis"
        or f002_result_approval.get("validation_result") != "passed"
        or not f002_result_approval.get("result_bytes_unchanged")
    ):
        raise ValueError("F-002 result is not governed by D-016")

    f002_chart_approval = json.loads(
        f002_chart_approval_path.read_text(encoding="utf-8")
    )
    if (
        f002_chart_approval.get("decision_id") != "D-017"
        or f002_chart_approval.get("finding_id") != "F-002"
        or f002_chart_approval.get("approval_status")
        != "approved_for_internal_product_development"
        or f002_chart_approval.get("validation_result") != "passed"
        or not f002_chart_approval.get("chart_bytes_unchanged")
        or not f002_chart_approval.get("text_bytes_unchanged")
    ):
        raise ValueError("F-002 chart is not governed by D-017")
    checks = f002_chart_approval.get("checks", {})
    if checks.get("denominator_ids") != [
        "uk_businesses_using_ai_technologies"
    ]:
        raise ValueError("D-017 does not retain the AI-user denominator")
    if checks.get("all_business_conversion_present") is not False:
        raise ValueError("D-017 does not prohibit all-business conversion")

    f001_rows = _load_rows(
        f001_result_path,
        denominator_id="all_uk_businesses",
        source_table_id="42",
        indicator_id="uses_any_ai_based_technologies",
    )
    f002_rows = _load_rows(
        f002_result_path,
        denominator_id="uk_businesses_using_ai_technologies",
        source_table_id="48",
        indicator_id="ai_tools_integrated_with_systems",
    )
    _verify_values_in_chart(f001_rows, f001_chart_path, f001_chart_text_path)
    _verify_values_in_chart(f002_rows, f002_chart_path, f002_chart_text_path)

    baseline = f001_brief_path.read_text(encoding="utf-8")
    if "Denominator: all UK businesses" not in baseline:
        raise ValueError("The approved F-001 baseline lacks its denominator")

    approval_ids = {
        "f001_result": f001_result_approval["approval_id"],
        "f001_chart": f001_chart_approval["approval_id"],
        "f001_brief": f001_brief_approval["approval_id"],
        "f002_result": f002_result_approval["approval_id"],
        "f002_chart": f002_chart_approval["approval_id"],
    }
    return f001_rows, f002_rows, approval_ids


def _table_rows(rows: list[dict[str, str]]) -> str:
    labels = {
        "micro": "Micro, up to 9 employees",
        "small": "Small, 10 to 49 employees",
        "medium": "Medium, 50 to 249 employees",
        "large": "Large, 250 or more employees",
    }
    roles = {
        "primary": "Primary SME group",
        "reference_benchmark": "Reference benchmark",
    }
    return "\n".join(
        "| {label} | {estimate:.1f}% | {lower:.1f}% to {upper:.1f}% | "
        "{base:,} | {role} |".format(
            label=labels[row["business_size"]],
            estimate=float(row["estimate_percent"]),
            lower=float(row["lower_limit_percent"]),
            upper=float(row["upper_limit_percent"]),
            base=int(row["sample_base"]),
            role=roles[row["scope_role"]],
        )
        for row in rows
    )


def render_brief(
    f001_rows: list[dict[str, str]],
    f002_rows: list[dict[str, str]],
    *,
    f001_chart_relative_path: str,
    f002_chart_relative_path: str,
) -> str:
    first = {row["business_size"]: row for row in f001_rows}
    second = {row["business_size"]: row for row in f002_rows}

    def value(rows: dict[str, dict[str, str]], size: str) -> float:
        return float(rows[size]["estimate_percent"])

    return f"""# From reported AI use to system integration: evidence by business size

Status: Internal second evidence-brief draft  
F-001 status: Result and first brief accepted through D-013  
F-002 status: Result and chart accepted through D-017  
Publication status: Not approved

## Executive message

The UK Business Data Survey 2026 provides two related but distinct views of AI adoption.

1. **Reported AI use among all businesses:** {value(first, "micro"):.1f}% of micro businesses, {value(first, "small"):.1f}% of small businesses and {value(first, "medium"):.1f}% of medium businesses reported at least one listed use of AI-based technologies. The large-business benchmark was {value(first, "large"):.1f}%.
2. **System integration among businesses already using AI:** {value(second, "micro"):.1f}% of micro AI users, {value(second, "small"):.1f}% of small AI users and {value(second, "medium"):.1f}% of medium AI users reported that at least one AI tool was integrated with their systems. The large-business benchmark was {value(second, "large"):.1f}%.

These percentages must not be compared as though they have the same denominator. The second measure describes integration only among businesses that already report AI use; it is not the share of all businesses with integrated AI.

Both findings are descriptive. They do not establish that differences between size groups are statistically significant, and they do not show that business size causes AI use or integration.

## 1. Reported AI use among all businesses

> **Denominator: all UK businesses within each published business-size category.**

![Reported AI use by business size with 95% confidence intervals]({f001_chart_relative_path})

| Published size group | Estimate | 95% confidence interval | Rounded unweighted base | Role |
|---|---:|---:|---:|---|
{_table_rows(f001_rows)}

The point estimates rise across the published business-size groups. The large-business value is a reference benchmark outside the primary SME scope.

## 2. AI-system integration among businesses already using AI

> **Denominator: UK businesses within each published business-size category that report using AI technologies. These are not percentages of all UK businesses.**

![AI tools integrated with business systems among businesses already using AI, with 95% confidence intervals]({f002_chart_relative_path})

| Published size group | Estimate | 95% confidence interval | Rounded unweighted base | Role |
|---|---:|---:|---:|---|
{_table_rows(f002_rows)}

Among AI-using businesses, the large-business benchmark has a higher point estimate than the three SME groups. The small and medium point estimates are similar. This is a descriptive observation, not a formal test of differences.

## How the two measures fit together

| Measure | Source table | Denominator | What it can describe |
|---|---|---|---|
| Reported use of AI-based technologies | Table 42 | All UK businesses in the size group | The breadth of reported AI use across the business population |
| AI tools integrated with business systems | Table 48 | Businesses in the size group that report using AI technologies | Integration depth within the survey's AI-user population |

The measures can be presented as two stages of evidence, but not combined arithmetically. This brief does not multiply, divide or subtract the percentages, estimate an all-business integration rate, or describe a conversion funnel.

## Why this matters

The first measure gives a baseline for how widely businesses report using AI. The second adds a narrower view of whether AI users report integrating tools with their systems. Keeping both measures visible can help separate questions about **adoption breadth** from questions about **integration depth**.

The evidence does not explain why the patterns differ, measure organisational readiness, identify barriers, show the quality or business value of integration, or establish which intervention would be effective.

## Shared source and method

- Source: Department for Science, Innovation and Technology, UK Business Data Survey 2026.
- Dataset version: 18 June 2026.
- Fieldwork: 10 October 2025 to 28 January 2026.
- Unit: weighted survey estimates expressed as percentages.
- Uncertainty: supplied 95% confidence limits.
- Sample bases: published rounded unweighted respondent counts, not counts of UK businesses.
- Primary SME scope: micro, small and medium published size groups.
- Large businesses: reference benchmark outside the primary SME scope.

## Limitations and permitted wording

- Keep the Table 42 all-business denominator and Table 48 AI-user denominator visibly separate.
- Do not convert Table 48 into an all-business percentage or combine it mathematically with Table 42 without a separately approved method and sufficient design evidence.
- Do not claim formal statistical significance from the published tables alone.
- Do not imply that business size causes AI use or integration.
- Do not treat rounded respondent bases as counts of UK businesses.
- Do not infer readiness, productivity, return on investment, barriers or service demand from these two measures.
- Do not share externally or publish until a separate review approves the full wording, charts, source notes, accessibility and context.

## Evidence trail

### F-001 baseline

- Finding: F-001.
- Result approval: D-010, approval `20260723T080810Z`.
- Comparison method: D-011.
- Chart approval: D-012, approval `20260723T082541Z`.
- First brief approval: D-013, approval `20260723T083948Z`.
- Query: `sql/g5_01_ai_use_by_size.sql`.

### F-002 extension

- Finding: F-002.
- Scope and denominator: D-014.
- Processed snapshot: D-015.
- Result approval: D-016, approval `20260723T102425Z`.
- Chart approval: D-017, approval `20260723T113016Z`.
- Query: `sql/g5_11_ai_integration_by_size.sql`.

## Owner review boundary

This combined draft is ready for G5-16 research-director review. Acceptance would authorise internal Report 02 development only. It would not approve external sharing or publication.
"""


def write_brief_draft(
    output_directory: Path,
    *,
    f001_result_path: Path,
    f001_result_approval_path: Path,
    f001_chart_path: Path,
    f001_chart_text_path: Path,
    f001_chart_approval_path: Path,
    f001_brief_path: Path,
    f001_brief_approval_path: Path,
    f002_result_path: Path,
    f002_result_approval_path: Path,
    f002_chart_path: Path,
    f002_chart_text_path: Path,
    f002_chart_approval_path: Path,
    created_at: datetime,
) -> dict[str, Any]:
    input_arguments = {
        "f001_result_path": f001_result_path,
        "f001_result_approval_path": f001_result_approval_path,
        "f001_chart_path": f001_chart_path,
        "f001_chart_text_path": f001_chart_text_path,
        "f001_chart_approval_path": f001_chart_approval_path,
        "f001_brief_path": f001_brief_path,
        "f001_brief_approval_path": f001_brief_approval_path,
        "f002_result_path": f002_result_path,
        "f002_result_approval_path": f002_result_approval_path,
        "f002_chart_path": f002_chart_path,
        "f002_chart_text_path": f002_chart_text_path,
        "f002_chart_approval_path": f002_chart_approval_path,
    }
    f001_rows, f002_rows, approval_ids = verify_inputs(**input_arguments)
    brief_path = output_directory / "evidence_brief.md"
    metadata_path = output_directory / "brief.metadata.json"
    existing = [path for path in (brief_path, metadata_path) if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite combined evidence brief: "
            + ", ".join(str(path) for path in existing)
        )
    output_directory.mkdir(parents=True, exist_ok=True)

    brief = render_brief(
        f001_rows,
        f002_rows,
        f001_chart_relative_path=(
            "../g5_04_ai_use_chart/approved/20260723T081736Z/"
            "ai_use_by_size_ci.svg"
        ),
        f002_chart_relative_path=(
            "../g5_13_ai_integration_chart/approved/20260723T111428Z/"
            "ai_integration_among_ai_users_by_size_ci.svg"
        ),
    )
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

        inputs = []
        for name, path in input_arguments.items():
            approval_key = (
                "f001_brief"
                if name.startswith("f001_brief")
                else "f001_chart"
                if name.startswith("f001_chart")
                else "f001_result"
                if name.startswith("f001_result")
                else "f002_chart"
                if name.startswith("f002_chart")
                else "f002_result"
            )
            inputs.append(
                {
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "approval_id": approval_ids[approval_key],
                }
            )

        metadata: dict[str, Any] = {
            "brief_id": brief_id,
            "created_at": created_text,
            "task_id": "G5-15",
            "finding_ids": ["F-001", "F-002"],
            "decision_ids": [
                "D-010",
                "D-011",
                "D-012",
                "D-013",
                "D-014",
                "D-015",
                "D-016",
                "D-017",
            ],
            "approval_status": DRAFT_STATUS,
            "inputs": inputs,
            "output": {
                "path": str(brief_path),
                "sha256": brief_sha,
            },
            "checks": {
                "approved_f001_result_used": True,
                "approved_f001_chart_used": True,
                "approved_f001_brief_baseline_used": True,
                "approved_f002_result_used": True,
                "approved_f002_chart_used": True,
                "measure_count": 2,
                "row_count": len(f001_rows) + len(f002_rows),
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
            },
            "validation_result": "passed",
            "warnings": [],
            "governance_boundary": (
                "Internal second evidence-brief draft for G5-16 owner review. "
                "Report 02, external sharing, and publication remain unapproved."
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
    f001_result = analysis / "g5_01_ai_use_by_size/approved/20260723T075335Z"
    f001_chart = analysis / "g5_04_ai_use_chart/approved/20260723T081736Z"
    f001_brief = analysis / "g5_05_evidence_brief/approved/20260723T083141Z"
    f002_result = (
        analysis / "g5_11_ai_integration_by_size/approved/20260723T101743Z"
    )
    f002_chart = (
        analysis / "g5_13_ai_integration_chart/approved/20260723T111428Z"
    )
    defaults = {
        "f001-result": f001_result / "result.csv",
        "f001-result-approval": f001_result / "approval.metadata.json",
        "f001-chart": f001_chart / "ai_use_by_size_ci.svg",
        "f001-chart-text": f001_chart / "text_equivalent.md",
        "f001-chart-approval": f001_chart / "approval.metadata.json",
        "f001-brief": f001_brief / "evidence_brief.md",
        "f001-brief-approval": f001_brief / "approval.metadata.json",
        "f002-result": f002_result / "result.csv",
        "f002-result-approval": f002_result / "approval.metadata.json",
        "f002-chart": (
            f002_chart / "ai_integration_among_ai_users_by_size_ci.svg"
        ),
        "f002-chart-text": f002_chart / "text_equivalent.md",
        "f002-chart-approval": f002_chart / "approval.metadata.json",
    }
    for option, default in defaults.items():
        parser.add_argument(f"--{option}", type=Path, default=default)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=analysis / "g5_15_second_evidence_brief",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = write_brief_draft(
        args.output_directory,
        f001_result_path=args.f001_result,
        f001_result_approval_path=args.f001_result_approval,
        f001_chart_path=args.f001_chart,
        f001_chart_text_path=args.f001_chart_text,
        f001_chart_approval_path=args.f001_chart_approval,
        f001_brief_path=args.f001_brief,
        f001_brief_approval_path=args.f001_brief_approval,
        f002_result_path=args.f002_result,
        f002_result_approval_path=args.f002_result_approval,
        f002_chart_path=args.f002_chart,
        f002_chart_text_path=args.f002_chart_text,
        f002_chart_approval_path=args.f002_chart_approval,
        created_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
