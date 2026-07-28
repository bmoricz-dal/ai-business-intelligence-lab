"""Create the accessible G5-04 confidence-interval chart from F-001."""

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
EXPECTED_TASK = "G5-01"
EXPECTED_FINDING = "F-001"
EXPECTED_SIZES = ("micro", "small", "medium", "large")
EXPECTED_ROLES = ("primary", "primary", "primary", "reference_benchmark")
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
    metadata = json.loads(approval_metadata_path.read_text(encoding="utf-8"))
    if metadata.get("approval_status") != EXPECTED_STATUS:
        raise ValueError("The selected result is not approved_for_analysis")
    if metadata.get("task_id") != EXPECTED_TASK:
        raise ValueError("The selected result has an unexpected task ID")
    if metadata.get("finding_id") != EXPECTED_FINDING:
        raise ValueError("The selected result has an unexpected finding ID")
    if metadata.get("validation_result") != "passed" or metadata.get("warnings"):
        raise ValueError("The selected result did not pass cleanly")
    if metadata.get("output", {}).get("sha256") != sha256_file(result_path):
        raise ValueError("Approved analysis result checksum mismatch")
    if not metadata.get("result_bytes_unchanged"):
        raise ValueError("The analysis approval lacks unchanged-result confirmation")

    with result_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 4:
        raise ValueError(f"Expected four approved result rows, got {len(rows)}")
    if tuple(row["business_size"] for row in rows) != EXPECTED_SIZES:
        raise ValueError("Approved result has unexpected business-size rows")
    if tuple(row["scope_role"] for row in rows) != EXPECTED_ROLES:
        raise ValueError("Approved result has unexpected analytical roles")
    return metadata, rows


def _point(percent: float, left: float, width: float) -> float:
    return left + (percent / 100.0) * width


def render_svg(rows: list[dict[str, str]]) -> str:
    width = 960
    height = 560
    left = 220
    right = 90
    top = 128
    bottom = 112
    plot_width = width - left - right
    row_gap = 76
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
        '<title id="chart-title">Reported use of AI-based technologies by business size</title>',
        (
            '<desc id="chart-desc">Horizontal dot plot of weighted survey '
            'estimates and 95 percent confidence intervals. Micro 37.4 percent, '
            'small 50.8 percent, medium 57.1 percent, and large benchmark 78.2 '
            'percent. The point estimates rise with business size. The chart '
            'does not claim statistical significance or causation.</desc>'
        ),
        f'<rect width="{width}" height="{height}" fill="{background}"/>',
        (
            f'<text x="32" y="38" fill="{foreground}" font-family="Arial, '
            'sans-serif" font-size="24" font-weight="700">Reported use of '
            'AI-based technologies by business size</text>'
        ),
        (
            f'<text x="32" y="68" fill="{muted}" font-family="Arial, sans-serif" '
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
                f'<text x="{estimate_x + 16:.1f}" y="{y - 13}" '
                f'fill="{foreground}" font-family="Arial, sans-serif" '
                f'font-size="14" font-weight="700">{estimate:.1f}%</text>'
            )
        )
        parts.append(
            (
                f'<text x="{estimate_x + 16:.1f}" y="{y + 8}" fill="{muted}" '
                f'font-family="Arial, sans-serif" font-size="11">'
                f'{lower:.1f}%–{upper:.1f}%</text>'
            )
        )

    legend_y = 452
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
                f'<text x="32" y="505" fill="{muted}" font-family="Arial, '
                'sans-serif" font-size="12">Denominator: all UK businesses within '
                'each published size category. Fieldwork: 10 Oct 2025–28 Jan 2026.</text>'
            ),
            (
                f'<text x="32" y="528" fill="{muted}" font-family="Arial, '
                'sans-serif" font-size="12">Source: DSIT, UK Business Data Survey '
                '2026, Table 42. Descriptive estimates only; no significance or '
                'causal claim.</text>'
            ),
            "</svg>",
        ]
    )
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    return svg


def render_text_equivalent(rows: list[dict[str, str]]) -> str:
    lines = [
        "# G5-04 Chart Text Equivalent",
        "",
        "Reported use of AI-based technologies by business size, UK Business Data Survey 2026.",
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
            "The point estimates rise across the published size groups. Large businesses are shown only as a benchmark.",
            "",
            "Denominator: all UK businesses within each published business-size category.",
            "",
            "Fieldwork: 10 October 2025 to 28 January 2026.",
            "",
            "Source: Department for Science, Innovation and Technology, UK Business Data Survey 2026, Table 42.",
            "",
            "Limitation: this is a descriptive comparison. The chart does not establish that differences are statistically significant and does not support a causal interpretation.",
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
    svg_path = output_directory / "ai_use_by_size_ci.svg"
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
            "task_id": "G5-04",
            "finding_id": EXPECTED_FINDING,
            "decision_ids": ["D-008", "D-010", "D-011"],
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
                "has_svg_title": True,
                "has_svg_description": True,
                "has_text_equivalent": True,
                "confidence_intervals_shown": True,
                "large_benchmark_distinct_by_colour_and_shape": True,
                "significance_claim_present": False,
            },
            "validation_result": "passed",
            "warnings": [],
            "governance_boundary": (
                "Draft chart for owner review. Not approved for public wording "
                "or publication."
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
        "g5_01_ai_use_by_size/approved/20260723T075335Z"
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
            "g5_04_ai_use_chart"
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
