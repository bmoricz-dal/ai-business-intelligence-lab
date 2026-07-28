"""Create the accessible G5-13 confidence-interval chart from F-002."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import tempfile
from typing import Any
import xml.etree.ElementTree as ET


EXPECTED_STATUS = "approved_for_analysis"
EXPECTED_DECISION = "D-016"
EXPECTED_TASK = "G5-12"
EXPECTED_SOURCE_TASK = "G5-11"
EXPECTED_FINDING = "F-002"
EXPECTED_APPROVAL_ID = "20260723T102425Z"
EXPECTED_RESULT_SHA256 = (
    "dd84088a34c925767dc86786000e6299d6636c5e2c6fba18148c055840beda09"
)
EXPECTED_APPROVAL_METADATA_SHA256 = (
    "a59b7ae9609eb31bb52dc1ae66750d0cb9998d2a3a7a0a669b523ed7ed266236"
)
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")
EXPECTED_DENOMINATOR = "uk_businesses_using_ai_technologies"
EXPECTED_INDICATOR = "ai_tools_integrated_with_systems"
DRAFT_STATUS = "draft_chart_owner_review_pending"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_approved_result(
    result_path: Path,
    approval_metadata_path: Path,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if sha256_file(result_path) != EXPECTED_RESULT_SHA256:
        raise ValueError("The D-016-approved result checksum has changed")
    if sha256_file(approval_metadata_path) != EXPECTED_APPROVAL_METADATA_SHA256:
        raise ValueError("The D-016 approval metadata checksum has changed")

    metadata = json.loads(approval_metadata_path.read_text(encoding="utf-8"))
    expected_fields = {
        "approval_status": EXPECTED_STATUS,
        "decision_id": EXPECTED_DECISION,
        "task_id": EXPECTED_TASK,
        "source_task_id": EXPECTED_SOURCE_TASK,
        "finding_id": EXPECTED_FINDING,
        "approval_id": EXPECTED_APPROVAL_ID,
        "validation_result": "passed",
        "result_bytes_unchanged": True,
    }
    for field, expected in expected_fields.items():
        if metadata.get(field) != expected:
            raise ValueError(f"Unexpected D-016 approval field: {field}")
    if metadata.get("warnings"):
        raise ValueError("The D-016-approved result has warnings")
    if metadata.get("output", {}).get("sha256") != EXPECTED_RESULT_SHA256:
        raise ValueError("D-016 metadata does not match the approved result")
    checks = metadata.get("checks", {})
    if checks.get("source_table_ids") != ["48"]:
        raise ValueError("The approved result is not restricted to Table 48")
    if checks.get("indicator_ids") != [EXPECTED_INDICATOR]:
        raise ValueError("The approved result has an unexpected indicator")
    if checks.get("denominator_ids") != [EXPECTED_DENOMINATOR]:
        raise ValueError("The approved result has an unexpected denominator")

    with result_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError(f"Expected four approved result rows, got {len(rows)}")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("Approved result has unexpected business-size rows")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("Approved result has unexpected analytical roles")
    if {row["source_table_id"] for row in rows} != {"48"}:
        raise ValueError("Approved result contains a non-Table 48 row")
    if {row["indicator_id"] for row in rows} != {EXPECTED_INDICATOR}:
        raise ValueError("Approved result mixes indicators")
    if {row["denominator_id"] for row in rows} != {EXPECTED_DENOMINATOR}:
        raise ValueError("Approved result mixes or changes denominators")
    return metadata, rows


def _point(percent: float, left: float, width: float) -> float:
    return left + (percent / 100.0) * width


def render_svg(rows: list[dict[str, str]]) -> str:
    width = 960
    height = 600
    left = 220
    right = 90
    top = 158
    row_gap = 76
    plot_width = width - left - right
    y_positions = [top + index * row_gap for index in range(4)]
    primary = "#005EA5"
    benchmark = "#A84F00"
    foreground = "#172B4D"
    muted = "#4B5B73"
    grid = "#C8D1DC"
    background = "#FFFFFF"

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            'aria-labelledby="chart-title chart-desc">'
        ),
        (
            '<title id="chart-title">AI tools integrated with business systems '
            'among businesses already using AI, by business size</title>'
        ),
        (
            '<desc id="chart-desc">Horizontal dot plot of weighted survey '
            'estimates and supplied 95 percent confidence intervals among UK '
            'businesses already using AI. Micro 26.9 percent, small 31.5 '
            'percent, medium 30.9 percent, and large benchmark 57.4 percent. '
            'These are not percentages of all UK businesses. The chart does '
            'not claim statistical significance or causation.</desc>'
        ),
        f'<rect width="{width}" height="{height}" fill="{background}"/>',
        (
            f'<text x="32" y="38" fill="{foreground}" font-family="Arial, '
            'sans-serif" font-size="24" font-weight="700">AI tools integrated '
            'with business systems, by business size</text>'
        ),
        (
            f'<text x="32" y="70" fill="{foreground}" font-family="Arial, '
            'sans-serif" font-size="17" font-weight="700">Among UK businesses '
            'already using AI</text>'
        ),
        (
            f'<text x="32" y="98" fill="{muted}" font-family="Arial, sans-serif" '
            'font-size="15">UK Business Data Survey 2026 · weighted estimates '
            'with 95% confidence intervals</text>'
        ),
    ]

    for tick in range(0, 101, 20):
        x = _point(tick, left, plot_width)
        parts.append(
            f'<line x1="{x:.1f}" y1="{top - 28}" x2="{x:.1f}" '
            f'y2="{top + row_gap * 3 + 28}" stroke="{grid}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top + row_gap * 3 + 58}" '
            f'text-anchor="middle" fill="{muted}" font-family="Arial, sans-serif" '
            f'font-size="13">{tick}%</text>'
        )

    label_lines = {
        "micro": ("Micro", "Up to 9 employees"),
        "small": ("Small", "10 to 49 employees"),
        "medium": ("Medium", "50 to 249 employees"),
        "large": ("Large benchmark", "250 or more employees"),
    }
    for row, y in zip(rows, y_positions, strict=True):
        size = row["business_size"]
        estimate = float(row["estimate_percent"])
        lower = float(row["lower_limit_percent"])
        upper = float(row["upper_limit_percent"])
        colour = benchmark if size == "large" else primary
        lower_x = _point(lower, left, plot_width)
        estimate_x = _point(estimate, left, plot_width)
        upper_x = _point(upper, left, plot_width)
        first, second = label_lines[size]
        parts.extend(
            [
                (
                    f'<text x="{left - 20}" y="{y - 4}" text-anchor="end" '
                    f'fill="{foreground}" font-family="Arial, sans-serif" '
                    f'font-size="15" font-weight="700">{html.escape(first)}</text>'
                ),
                (
                    f'<text x="{left - 20}" y="{y + 17}" text-anchor="end" '
                    f'fill="{muted}" font-family="Arial, sans-serif" '
                    f'font-size="12">{html.escape(second)}</text>'
                ),
                (
                    f'<line x1="{lower_x:.1f}" y1="{y}" x2="{upper_x:.1f}" '
                    f'y2="{y}" stroke="{colour}" stroke-width="4"/>'
                ),
                (
                    f'<line x1="{lower_x:.1f}" y1="{y - 8}" x2="{lower_x:.1f}" '
                    f'y2="{y + 8}" stroke="{colour}" stroke-width="3"/>'
                ),
                (
                    f'<line x1="{upper_x:.1f}" y1="{y - 8}" x2="{upper_x:.1f}" '
                    f'y2="{y + 8}" stroke="{colour}" stroke-width="3"/>'
                ),
            ]
        )
        if size == "large":
            parts.append(
                (
                    f'<polygon points="{estimate_x:.1f},{y - 10} '
                    f'{estimate_x + 10:.1f},{y} {estimate_x:.1f},{y + 10} '
                    f'{estimate_x - 10:.1f},{y}" fill="{colour}"/>'
                )
            )
        else:
            parts.append(
                f'<circle cx="{estimate_x:.1f}" cy="{y}" r="9" fill="{colour}"/>'
            )
        parts.append(
            (
                f'<text x="{upper_x + 14:.1f}" y="{y - 8}" '
                f'fill="{foreground}" font-family="Arial, sans-serif" '
                f'font-size="14" font-weight="700">{estimate:.1f}%</text>'
            )
        )
        parts.append(
            (
                f'<text x="{upper_x + 14:.1f}" y="{y + 15}" fill="{muted}" '
                f'font-family="Arial, sans-serif" font-size="11">'
                f'{lower:.1f}%–{upper:.1f}%</text>'
            )
        )

    legend_y = 492
    parts.extend(
        [
            f'<circle cx="34" cy="{legend_y}" r="7" fill="{primary}"/>',
            (
                f'<text x="49" y="{legend_y + 5}" fill="{foreground}" '
                'font-family="Arial, sans-serif" font-size="13">Primary SME group</text>'
            ),
            (
                f'<polygon points="245,{legend_y - 8} 253,{legend_y} '
                f'245,{legend_y + 8} 237,{legend_y}" fill="{benchmark}"/>'
            ),
            (
                f'<text x="261" y="{legend_y + 5}" fill="{foreground}" '
                'font-family="Arial, sans-serif" font-size="13">Large-business benchmark</text>'
            ),
            (
                f'<line x1="501" y1="{legend_y}" x2="549" y2="{legend_y}" '
                f'stroke="{primary}" stroke-width="4"/>'
            ),
            (
                f'<text x="561" y="{legend_y + 5}" fill="{foreground}" '
                'font-family="Arial, sans-serif" font-size="13">95% confidence interval</text>'
            ),
            (
                f'<text x="32" y="538" fill="{foreground}" font-family="Arial, '
                'sans-serif" font-size="12" font-weight="700">Denominator: UK '
                'businesses within each size group that report using AI technologies '
                '(not all UK businesses).</text>'
            ),
            (
                f'<text x="32" y="562" fill="{muted}" font-family="Arial, '
                'sans-serif" font-size="12">Fieldwork: 10 Oct 2025–28 Jan 2026. '
                'Source: DSIT, UK Business Data Survey 2026, Table 48.</text>'
            ),
            (
                f'<text x="32" y="584" fill="{muted}" font-family="Arial, '
                'sans-serif" font-size="12">Descriptive estimates only; no '
                'significance or causal claim. Bases are rounded unweighted samples.</text>'
            ),
            "</svg>",
        ]
    )
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    return svg


def render_text_equivalent(rows: list[dict[str, str]]) -> str:
    lines = [
        "# G5-13 Chart Text Equivalent",
        "",
        "AI tools integrated with business systems by business size, among UK businesses already using AI.",
        "",
        "| Published size group | Estimate | 95% confidence interval | Rounded unweighted base | Role |",
        "|---|---:|---:|---:|---|",
    ]
    labels = {
        "micro": "Micro, up to 9 employees",
        "small": "Small, 10 to 49 employees",
        "medium": "Medium, 50 to 249 employees",
        "large": "Large, 250 or more employees",
    }
    roles = {
        "primary": "Primary SME group",
        "reference_benchmark": "Large-business benchmark",
    }
    for row in rows:
        lines.append(
            "| {label} | {estimate:.1f}% | {lower:.1f}% to {upper:.1f}% | "
            "{base:,} | {role} |".format(
                label=labels[row["business_size"]],
                estimate=float(row["estimate_percent"]),
                lower=float(row["lower_limit_percent"]),
                upper=float(row["upper_limit_percent"]),
                base=int(row["sample_base"]),
                role=roles[row["scope_role"]],
            )
        )
    lines.extend(
        [
            "",
            "Among AI-using businesses, the large-business benchmark has a higher point estimate than the three SME groups. The small and medium point estimates are similar. This is a descriptive observation, not a formal test of differences.",
            "",
            "Denominator: UK businesses within each published business-size category that report using AI technologies. These are not percentages of all UK businesses.",
            "",
            "Fieldwork: 10 October 2025 to 28 January 2026.",
            "",
            "Source: Department for Science, Innovation and Technology, UK Business Data Survey 2026, Table 48.",
            "",
            "Limitation: the chart does not establish that differences are statistically significant and does not support a causal interpretation. Rounded unweighted sample bases are not counts of UK businesses. Do not multiply these percentages by the Table 42 AI-use estimates without an approved method.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_chart_draft(
    output_directory: Path,
    *,
    result_path: Path,
    approval_metadata_path: Path,
    created_at: datetime,
) -> dict[str, Any]:
    approval, rows = verify_approved_result(result_path, approval_metadata_path)
    svg_path = output_directory / "ai_integration_among_ai_users_by_size_ci.svg"
    text_path = output_directory / "text_equivalent.md"
    metadata_path = output_directory / "chart.metadata.json"
    outputs = (svg_path, text_path, metadata_path)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite chart output: "
            + ", ".join(str(path) for path in existing)
        )
    output_directory.mkdir(parents=True, exist_ok=True)

    created_text = created_at.astimezone(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    chart_id = created_at.strftime("%Y%m%dT%H%M%SZ")
    temporary_paths: list[Path] = []
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output_directory,
            suffix=".svg",
            delete=False,
        ) as temporary_svg:
            temporary_svg.write(render_svg(rows))
            temporary_svg_path = Path(temporary_svg.name)
        temporary_paths.append(temporary_svg_path)

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output_directory,
            suffix=".md",
            delete=False,
        ) as temporary_text:
            temporary_text.write(render_text_equivalent(rows))
            temporary_text_path = Path(temporary_text.name)
        temporary_paths.append(temporary_text_path)

        svg_sha = sha256_file(temporary_svg_path)
        text_sha = sha256_file(temporary_text_path)
        metadata: dict[str, Any] = {
            "chart_id": chart_id,
            "created_at": created_text,
            "task_id": "G5-13",
            "finding_id": EXPECTED_FINDING,
            "decision_ids": ["D-011", "D-014", "D-015", "D-016"],
            "approval_status": DRAFT_STATUS,
            "source_result": {
                "path": str(result_path),
                "sha256": sha256_file(result_path),
                "approval_metadata_path": str(approval_metadata_path),
                "approval_metadata_sha256": sha256_file(approval_metadata_path),
                "approval_id": approval["approval_id"],
            },
            "outputs": [
                {"path": str(svg_path), "sha256": svg_sha},
                {"path": str(text_path), "sha256": text_sha},
            ],
            "checks": {
                "row_count": len(rows),
                "primary_sme_count": sum(
                    row["scope_role"] == "primary" for row in rows
                ),
                "reference_benchmark_count": sum(
                    row["scope_role"] == "reference_benchmark" for row in rows
                ),
                "source_table_ids": ["48"],
                "indicator_ids": [EXPECTED_INDICATOR],
                "denominator_ids": [EXPECTED_DENOMINATOR],
                "has_svg_title": True,
                "has_svg_description": True,
                "has_text_equivalent": True,
                "conditional_denominator_visible": True,
                "all_business_conversion_present": False,
                "confidence_intervals_shown": True,
                "large_benchmark_distinct_by_colour_and_shape": True,
                "significance_claim_present": False,
            },
            "validation_result": "passed",
            "warnings": [],
            "governance_boundary": (
                "Draft F-002 chart for owner review. The conditional AI-user "
                "denominator is mandatory. No report wording, external sharing, "
                "or publication is approved."
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

        for temporary, final in zip(
            (temporary_svg_path, temporary_text_path, temporary_metadata_path),
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
    approved = Path(
        "data/processed/uk_business_data_survey/2026-06-18/analysis/"
        "g5_11_ai_integration_by_size/approved/20260723T101743Z"
    )
    parser.add_argument("--result", type=Path, default=approved / "result.csv")
    parser.add_argument(
        "--approval-metadata",
        type=Path,
        default=approved / "approval.metadata.json",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path(
            "data/processed/uk_business_data_survey/2026-06-18/analysis/"
            "g5_13_ai_integration_chart"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = write_chart_draft(
        args.output_directory,
        result_path=args.result,
        approval_metadata_path=args.approval_metadata,
        created_at=datetime.now(timezone.utc),
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
