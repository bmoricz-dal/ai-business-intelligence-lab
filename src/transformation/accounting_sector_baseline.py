"""Build the first governed baseline for UK accounting-sector AI research.

The baseline intentionally keeps two evidence roles separate:

* ONS Table 4 defines the VAT/PAYE-registered SIC 69.20 enterprise population.
* UKBDS 2026 supplies AI measures for broad SIC M as contextual proxies only.

It does not estimate the percentage of UK accounting SMEs using AI.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from src.transformation.ukbds import (
    _find_column,
    _numeric_or_status,
    _rows_by_label,
    _value_at,
    read_ods_sheet,
    sha256_file,
)


ONS_SOURCE_ID = "ons_uk_business_activity_size_location_2025"
ONS_DATASET_ID = "uk_business_activity_size_location"
ONS_DATASET_VERSION = "2025-09-24"
ONS_TABLE_ID = "Table 4"
ONS_PERIOD = "2025-03-14"
ONS_ACCOUNTING_LABEL_PREFIX = "6920 : Accounting; bookkeeping and auditing activities; tax consultancy"

UKBDS_SOURCE_ID = "dsit_ukbds_2026"
UKBDS_DATASET_ID = "uk_business_data_survey"
UKBDS_DATASET_VERSION = "2026-06-18"
UKBDS_PERIOD_START = "2025-10-10"
UKBDS_PERIOD_END = "2026-01-28"
UKBDS_SECTOR_LABEL = "Sector: Professional, Scientific, Technical (SIC M)"

XLSX_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

OUTPUT_FIELDS = [
    "source_id",
    "dataset_id",
    "dataset_version",
    "source_table_id",
    "indicator_id",
    "period_start",
    "period_end",
    "population_label",
    "denominator_label",
    "unit",
    "dimension_type",
    "dimension_value",
    "source_dimension_label",
    "scope_role",
    "estimate",
    "lower_limit",
    "upper_limit",
    "confidence_level",
    "sample_base",
    "source_status",
    "notes",
]


@dataclass(frozen=True)
class BaselineObservation:
    source_id: str
    dataset_id: str
    dataset_version: str
    source_table_id: str
    indicator_id: str
    period_start: str
    period_end: str
    population_label: str
    denominator_label: str
    unit: str
    dimension_type: str
    dimension_value: str
    source_dimension_label: str
    scope_role: str
    estimate: float | None
    lower_limit: float | None
    upper_limit: float | None
    confidence_level: float | None
    sample_base: int | None
    source_status: str
    notes: str


@dataclass(frozen=True)
class UkbdsMetric:
    table_id: str
    indicator_id: str
    column_label: str
    denominator_label: str
    notes: str


UKBDS_METRICS = (
    UkbdsMetric(
        "42",
        "uses_any_listed_ai_technology",
        "Uses any Artificial Intelligence-based technologies",
        "All UK businesses in the published SIC M sector category",
        "Contextual proxy only; the published sector includes SIC divisions 69 to 75 and is not SME-only.",
    ),
    UkbdsMetric(
        "42",
        "uses_ai_for_research",
        "To research information (e.g. in place of a traditional search engine such as Google)",
        "All UK businesses in the published SIC M sector category",
        "Multiple-response use case; contextual proxy only and not an accounting-task measure.",
    ),
    UkbdsMetric(
        "42",
        "uses_ai_for_summarising_or_drafting",
        "To summarise or collate in-house information, draft reports or correspondence",
        "All UK businesses in the published SIC M sector category",
        "Multiple-response use case; contextual proxy only and not an accounting-task measure.",
    ),
    UkbdsMetric(
        "43",
        "uses_automated_decision_making",
        "Yes",
        "UK businesses using AI technologies in the published SIC M sector category",
        "Conditional AI-user denominator; contextual proxy only.",
    ),
    UkbdsMetric(
        "47",
        "uses_data_to_develop_or_train_ai",
        "Artificial Intelligence (e.g. machine learning models, generative AI)",
        "All UK businesses in the published SIC M sector category",
        "Contextual proxy only; this does not capture purchase or use of ready-made tools.",
    ),
    UkbdsMetric(
        "48",
        "ai_tools_integrated_with_systems",
        "Yes",
        "UK businesses using AI technologies in the published SIC M sector category",
        "Conditional AI-user denominator; contextual proxy only.",
    ),
    UkbdsMetric(
        "50",
        "has_ai_policy_or_guidance",
        "Yes",
        "UK businesses using AI technologies in the published SIC M sector category",
        "Conditional AI-user denominator; policy presence does not measure policy quality.",
    ),
)


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference)
    if letters is None:
        raise ValueError(f"Invalid XLSX cell reference: {reference}")
    result = 0
    for character in letters.group(0):
        result = result * 26 + ord(character) - ord("A") + 1
    return result - 1


def _xlsx_target_path(target: str) -> str:
    pure = PurePosixPath(target.lstrip("/"))
    if pure.parts and pure.parts[0] == "xl":
        return str(pure)
    return str(PurePosixPath("xl") / pure)


def _xlsx_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(item.itertext()) for item in root.findall("main:si", XLSX_NS)]


def read_xlsx_sheet(path: Path, sheet_name: str) -> list[list[str | float | None]]:
    """Read cell values from one XLSX sheet using only the standard library."""

    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relation_targets = {
            item.get("Id"): item.get("Target")
            for item in relationships.findall("pkgrel:Relationship", XLSX_NS)
        }
        target = None
        for sheet in workbook.findall("main:sheets/main:sheet", XLSX_NS):
            if sheet.get("name") == sheet_name:
                relation_id = sheet.get(f"{{{XLSX_NS['rel']}}}id")
                target = relation_targets.get(relation_id)
                break
        if not target:
            raise ValueError(f"Sheet {sheet_name!r} not found in {path.name}")

        shared_strings = _xlsx_shared_strings(archive)
        worksheet = ET.fromstring(archive.read(_xlsx_target_path(target)))

    matrix: list[list[str | float | None]] = []
    for row in worksheet.findall(".//main:sheetData/main:row", XLSX_NS):
        populated: dict[int, str | float | None] = {}
        for cell in row.findall("main:c", XLSX_NS):
            reference = cell.get("r")
            if reference is None:
                continue
            index = _column_index(reference)
            cell_type = cell.get("t")
            if cell_type == "inlineStr":
                inline = cell.find("main:is", XLSX_NS)
                value: str | float | None = (
                    "".join(inline.itertext()) if inline is not None else None
                )
            else:
                raw_node = cell.find("main:v", XLSX_NS)
                raw = raw_node.text if raw_node is not None else None
                if raw is None:
                    value = None
                elif cell_type == "s":
                    value = shared_strings[int(raw)]
                elif cell_type == "str":
                    value = raw
                elif cell_type == "b":
                    value = 1.0 if raw == "1" else 0.0
                else:
                    value = float(raw)
            if value is not None:
                populated[index] = value
        if not populated:
            matrix.append([])
        else:
            width = max(populated) + 1
            matrix.append([populated.get(index) for index in range(width)])
    return matrix


def extract_accounting_population(workbook: Path) -> list[BaselineObservation]:
    """Extract the 2025 SIC 69.20 registered-enterprise population."""

    rows = read_xlsx_sheet(workbook, ONS_TABLE_ID)
    header = None
    source_row = None
    for row in rows:
        labels = {value for value in row if isinstance(value, str)}
        if {"0-4", "5-9", "10-19", "20-49", "50-99", "100-249", "250+"}.issubset(labels):
            header = row
        if row and isinstance(row[0], str) and row[0].startswith(ONS_ACCOUNTING_LABEL_PREFIX):
            source_row = row
    if header is None:
        raise ValueError("ONS Table 4 employment-size header not found")
    if source_row is None:
        raise ValueError("ONS Table 4 SIC 69.20 row not found")

    source_label = str(source_row[0])
    band_map = (
        ("0-4", "0_4"),
        ("5-9", "5_9"),
        ("10-19", "10_19"),
        ("20-49", "20_49"),
        ("50-99", "50_99"),
        ("100-249", "100_249"),
        ("250+", "250_plus"),
        ("Total", "all_sizes"),
    )
    counts: dict[str, int] = {}
    observations: list[BaselineObservation] = []
    for label, key in band_map:
        column = _find_column(header, label)
        raw = _value_at(source_row, column)
        if not isinstance(raw, (int, float)) or int(raw) != raw or raw < 0:
            raise ValueError(f"Invalid ONS enterprise count for {label}: {raw!r}")
        count = int(raw)
        if count % 5:
            raise ValueError(f"ONS enterprise count is not control-rounded to base 5: {label}")
        counts[key] = count
        observations.append(
            BaselineObservation(
                source_id=ONS_SOURCE_ID,
                dataset_id=ONS_DATASET_ID,
                dataset_version=ONS_DATASET_VERSION,
                source_table_id=ONS_TABLE_ID,
                indicator_id="registered_enterprises",
                period_start=ONS_PERIOD,
                period_end=ONS_PERIOD,
                population_label="VAT and/or PAYE based UK enterprises classified to SIC 69.20",
                denominator_label="Registered enterprises in SIC 69.20",
                unit="count",
                dimension_type="employment_size",
                dimension_value=key,
                source_dimension_label=label,
                scope_role="context",
                estimate=float(count),
                lower_limit=None,
                upper_limit=None,
                confidence_level=None,
                sample_base=None,
                source_status="observed",
                notes=(
                    "ONS control-rounded count; registered-enterprise frame excludes "
                    "businesses not registered for VAT or PAYE."
                ),
            )
        )

    component_total = sum(counts[key] for _, key in band_map if key != "all_sizes")
    if component_total != counts["all_sizes"]:
        raise ValueError(
            f"ONS size-band counts do not reconcile: {component_total} != {counts['all_sizes']}"
        )
    sme_count = sum(
        counts[key]
        for key in ("0_4", "5_9", "10_19", "20_49", "50_99", "100_249")
    )
    observations.append(
        BaselineObservation(
            source_id=ONS_SOURCE_ID,
            dataset_id=ONS_DATASET_ID,
            dataset_version=ONS_DATASET_VERSION,
            source_table_id=ONS_TABLE_ID,
            indicator_id="registered_enterprises",
            period_start=ONS_PERIOD,
            period_end=ONS_PERIOD,
            population_label="VAT and/or PAYE based UK enterprises classified to SIC 69.20",
            denominator_label="Registered enterprises in SIC 69.20",
            unit="count",
            dimension_type="employment_size",
            dimension_value="sme_0_249",
            source_dimension_label="Derived sum: 0-4 through 100-249 employees",
            scope_role="context",
            estimate=float(sme_count),
            lower_limit=None,
            upper_limit=None,
            confidence_level=None,
            sample_base=None,
            source_status="observed",
            notes=(
                "Derived from six published control-rounded bands; not an independently "
                "published total and may inherit small rounding differences."
            ),
        )
    )
    return observations


def extract_ukbds_sic_m_proxy(
    central_workbook: Path,
    confidence_workbook: Path,
) -> list[BaselineObservation]:
    """Extract seven SIC M observations as broad contextual proxies."""

    observations: list[BaselineObservation] = []
    table_cache: dict[str, tuple[list[list[Any]], ...]] = {}
    for metric in UKBDS_METRICS:
        if metric.table_id not in table_cache:
            table_cache[metric.table_id] = (
                read_ods_sheet(central_workbook, metric.table_id),
                read_ods_sheet(confidence_workbook, metric.table_id),
                read_ods_sheet(confidence_workbook, f"{metric.table_id}_lcl"),
                read_ods_sheet(confidence_workbook, f"{metric.table_id}_ucl"),
            )
        central_source, central, lower, upper = table_cache[metric.table_id]
        header = central[7]
        estimate_column = _find_column(header, metric.column_label)
        base_column = _find_column(header, "Unweighted base")
        row_sets = tuple(_rows_by_label(rows) for rows in (central_source, central, lower, upper))
        try:
            source_row, central_row, lower_row, upper_row = (
                rows[UKBDS_SECTOR_LABEL] for rows in row_sets
            )
        except KeyError as error:
            raise ValueError(f"UKBDS SIC M row missing from Table {metric.table_id}") from error

        estimate, status = _numeric_or_status(_value_at(central_row, estimate_column))
        source_estimate, source_status = _numeric_or_status(
            _value_at(source_row, estimate_column)
        )
        lower_limit, lower_status = _numeric_or_status(
            _value_at(lower_row, estimate_column)
        )
        upper_limit, upper_status = _numeric_or_status(
            _value_at(upper_row, estimate_column)
        )
        if (source_estimate, source_status) != (estimate, status):
            raise ValueError(f"UKBDS central-workbook mismatch for {metric.indicator_id}")
        if lower_status != status or upper_status != status:
            raise ValueError(f"UKBDS confidence-status mismatch for {metric.indicator_id}")
        raw_base = _value_at(central_row, base_column)
        source_base = _value_at(source_row, base_column)
        if not isinstance(raw_base, (int, float)) or int(raw_base) != raw_base:
            raise ValueError(f"Invalid UKBDS base for {metric.indicator_id}")
        sample_base = int(raw_base)
        if not isinstance(source_base, (int, float)) or int(source_base) != sample_base:
            raise ValueError(f"UKBDS base mismatch for {metric.indicator_id}")

        observation = BaselineObservation(
            source_id=UKBDS_SOURCE_ID,
            dataset_id=UKBDS_DATASET_ID,
            dataset_version=UKBDS_DATASET_VERSION,
            source_table_id=metric.table_id,
            indicator_id=metric.indicator_id,
            period_start=UKBDS_PERIOD_START,
            period_end=UKBDS_PERIOD_END,
            population_label="UK businesses in Professional, Scientific and Technical activities (SIC M)",
            denominator_label=metric.denominator_label,
            unit="proportion",
            dimension_type="sector",
            dimension_value="professional_scientific_technical_sic_m",
            source_dimension_label=UKBDS_SECTOR_LABEL,
            scope_role="context",
            estimate=estimate,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            confidence_level=0.95,
            sample_base=sample_base,
            source_status=status,
            notes=metric.notes,
        )
        validate_observation(observation)
        observations.append(observation)
    return observations


def validate_observation(observation: BaselineObservation) -> None:
    if observation.source_status != "observed":
        raise ValueError(f"Target observation is not numeric: {observation.indicator_id}")
    if observation.estimate is None:
        raise ValueError(f"Missing estimate: {observation.indicator_id}")
    if observation.unit == "proportion":
        values = (observation.lower_limit, observation.estimate, observation.upper_limit)
        if any(value is None or not 0 <= value <= 1 for value in values):
            raise ValueError(f"Invalid proportion or interval: {observation.indicator_id}")
        lower, estimate, upper = values
        if not lower <= estimate <= upper:
            raise ValueError(f"Interval excludes estimate: {observation.indicator_id}")
        if observation.confidence_level != 0.95:
            raise ValueError(f"Unexpected confidence level: {observation.indicator_id}")
        if observation.sample_base is None or observation.sample_base <= 0:
            raise ValueError(f"Invalid sample base: {observation.indicator_id}")


def build_baseline(
    ons_workbook: Path,
    ukbds_central_workbook: Path,
    ukbds_confidence_workbook: Path,
) -> list[BaselineObservation]:
    observations = [
        *extract_accounting_population(ons_workbook),
        *extract_ukbds_sic_m_proxy(ukbds_central_workbook, ukbds_confidence_workbook),
    ]
    keys = [
        (item.source_id, item.source_table_id, item.indicator_id, item.dimension_value)
        for item in observations
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("Baseline contains duplicate logical observations")
    return observations


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(text)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def write_outputs(
    output_csv: Path,
    observations: list[BaselineObservation],
    *,
    ons_workbook: Path,
    ukbds_central_workbook: Path,
    ukbds_confidence_workbook: Path,
) -> None:
    metadata_path = output_csv.with_suffix(".metadata.json")
    for target in (output_csv, metadata_path):
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite existing output: {target}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=output_csv.parent, delete=False
    ) as temporary:
        writer = csv.DictWriter(temporary, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(item) for item in observations)
        temporary_path = Path(temporary.name)
    temporary_path.replace(output_csv)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "output_path": str(output_csv),
        "output_sha256": sha256_file(output_csv),
        "row_count": len(observations),
        "inputs": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in (ons_workbook, ukbds_central_workbook, ukbds_confidence_workbook)
        ],
        "method_control": (
            "ONS SIC 69.20 population counts and UKBDS broad SIC M AI estimates are "
            "stored as separate observations and are never multiplied or merged."
        ),
        "claim_limit": (
            "This baseline does not estimate the percentage of UK accounting SMEs using AI."
        ),
    }
    _atomic_write(metadata_path, json.dumps(metadata, indent=2) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ons-workbook", type=Path, required=True)
    parser.add_argument("--ukbds-central", type=Path, required=True)
    parser.add_argument("--ukbds-confidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    observations = build_baseline(
        args.ons_workbook,
        args.ukbds_central,
        args.ukbds_confidence,
    )
    write_outputs(
        args.output,
        observations,
        ons_workbook=args.ons_workbook,
        ukbds_central_workbook=args.ukbds_central,
        ukbds_confidence_workbook=args.ukbds_confidence,
    )


if __name__ == "__main__":
    main()
