from dataclasses import replace
from html import escape
from pathlib import Path
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from src.transformation.accounting_sector_baseline import (
    ONS_ACCOUNTING_LABEL_PREFIX,
    UKBDS_METRICS,
    build_baseline,
    extract_accounting_population,
    extract_ukbds_sic_m_proxy,
    validate_observation,
    write_outputs,
)


ODS_NS = (
    'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
    'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
    'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
)


def _ods_string(value: str) -> str:
    return (
        '<table:table-cell office:value-type="string">'
        f"<text:p>{escape(value)}</text:p></table:table-cell>"
    )


def _ods_number(value: float, value_type: str = "percentage") -> str:
    return (
        f'<table:table-cell office:value-type="{value_type}" '
        f'office:value="{value}"><text:p>{value}</text:p></table:table-cell>'
    )


def _ods_table(name: str, headers: list[str], values: list[float]) -> str:
    rows = ["<table:table-row><table:table-cell/></table:table-row>" for _ in range(7)]
    header = [_ods_string("Breakdown"), *(_ods_string(item) for item in headers), _ods_string("Unweighted base")]
    rows.append(f"<table:table-row>{''.join(header)}</table:table-row>")
    total = [_ods_string("Total"), *(_ods_number(0.2) for _ in headers), _ods_number(1000, "float")]
    rows.append(f"<table:table-row>{''.join(total)}</table:table-row>")
    sector = [
        _ods_string("Sector: Professional, Scientific, Technical (SIC M)"),
        *(_ods_number(item) for item in values),
        _ods_number(530 if name in {"42", "47"} else 280, "float"),
    ]
    rows.append(f"<table:table-row>{''.join(sector)}</table:table-row>")
    return f'<table:table table:name="{name}">{"".join(rows)}</table:table>'


def _write_ods(path: Path, tables: list[str]) -> None:
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content {ODS_NS}><office:body><office:spreadsheet>'
        f'{"".join(tables)}</office:spreadsheet></office:body></office:document-content>'
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("content.xml", content)


def _xlsx_column(index: int) -> str:
    result = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(ord("A") + remainder) + result
    return result


def _write_xlsx(path: Path) -> None:
    shared = [
        "0-4",
        "5-9",
        "10-19",
        "20-49",
        "50-99",
        "100-249",
        "250+",
        "Total",
        ONS_ACCOUNTING_LABEL_PREFIX,
    ]
    shared_xml = "".join(f"<si><t>{escape(item)}</t></si>" for item in shared)
    header_cells = "".join(
        f'<c r="{_xlsx_column(index + 1)}1" t="s"><v>{index}</v></c>'
        for index in range(8)
    )
    values = [31295, 4995, 2190, 945, 295, 140, 115, 39975]
    value_cells = "".join(
        f'<c r="{_xlsx_column(index + 1)}2"><v>{value}</v></c>'
        for index, value in enumerate(values)
    )
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData><row r="1">{header_cells}</row><row r="2">'
        f'<c r="A2" t="s"><v>8</v></c>{value_cells}</row></sheetData></worksheet>'
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Table 4" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>'
            '</Relationships>',
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"{shared_xml}</sst>",
        )
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


class AccountingSectorBaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.ons = directory / "ons.xlsx"
        self.central = directory / "central.ods"
        self.confidence = directory / "confidence.ods"
        _write_xlsx(self.ons)

        values_by_table = {
            "42": [0.278, 0.078, 0.372, 0.097, 0.016, 0.164, 0.011, 0.065, 0.506, 0.431, 0.002],
            "43": [0.041, 0.959, 0.0],
            "47": [0.010, 0.010, 0.0, 0.495, 0.0],
            "48": [0.199, 0.787, 0.014],
            "50": [0.199, 0.798, 0.003],
        }
        headers_by_table = {
            "42": [
                "To summarise or collate in-house information, draft reports or correspondence",
                "To draft computer code",
                "To research information (e.g. in place of a traditional search engine such as Google)",
                "To analyse data or build models",
                "Customer service chatbots",
                "Generating images or videos (e.g. for marketing purposes)",
                "To protect the business' systems and networks from cybersecurity threats",
                "Other",
                "Uses any Artificial Intelligence-based technologies",
                "Do not use AI",
                "Don't know",
            ],
            "43": ["Yes", "No", "Don't know"],
            "47": [
                "Artificial Intelligence (e.g. machine learning models, generative AI)",
                "Either Artificial Intelligence or Automated Decision Making purposes",
                "Both Artificial Intelligence or Automated Decision Making purposes",
                "No, we don't use data for these purposes",
                "Don't know",
            ],
            "48": ["Yes", "No", "Don't know"],
            "50": ["Yes", "No", "Don't know"],
        }
        central_tables = []
        confidence_tables = []
        for table_id, headers in headers_by_table.items():
            values = values_by_table[table_id]
            central_tables.append(_ods_table(table_id, headers, values))
            confidence_tables.extend(
                [
                    _ods_table(table_id, headers, values),
                    _ods_table(f"{table_id}_lcl", headers, [max(value - 0.02, 0) for value in values]),
                    _ods_table(f"{table_id}_ucl", headers, [min(value + 0.02, 1) for value in values]),
                ]
            )
        _write_ods(self.central, central_tables)
        _write_ods(self.confidence, confidence_tables)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_extracts_and_reconciles_accounting_population(self) -> None:
        observations = extract_accounting_population(self.ons)
        by_dimension = {item.dimension_value: item for item in observations}
        self.assertEqual(by_dimension["sme_0_249"].estimate, 39860.0)
        self.assertEqual(by_dimension["250_plus"].estimate, 115.0)
        self.assertEqual(by_dimension["all_sizes"].estimate, 39975.0)

    def test_extracts_seven_contextual_proxy_metrics(self) -> None:
        observations = extract_ukbds_sic_m_proxy(self.central, self.confidence)
        self.assertEqual(len(observations), len(UKBDS_METRICS))
        by_indicator = {item.indicator_id: item for item in observations}
        self.assertEqual(by_indicator["uses_any_listed_ai_technology"].estimate, 0.506)
        self.assertEqual(by_indicator["uses_ai_for_research"].estimate, 0.372)
        self.assertEqual(by_indicator["ai_tools_integrated_with_systems"].sample_base, 280)
        self.assertTrue(all(item.scope_role == "context" for item in observations))

    def test_rejects_invalid_interval(self) -> None:
        observation = extract_ukbds_sic_m_proxy(self.central, self.confidence)[0]
        with self.assertRaisesRegex(ValueError, "Interval excludes estimate"):
            validate_observation(replace(observation, lower_limit=0.9))

    def test_build_and_writer_refuse_silent_overwrite(self) -> None:
        observations = build_baseline(self.ons, self.central, self.confidence)
        self.assertEqual(len(observations), 16)
        output = Path(self.temporary_directory.name) / "baseline.csv"
        write_outputs(
            output,
            observations,
            ons_workbook=self.ons,
            ukbds_central_workbook=self.central,
            ukbds_confidence_workbook=self.confidence,
        )
        self.assertTrue(output.with_suffix(".metadata.json").exists())
        with self.assertRaisesRegex(FileExistsError, "Refusing to overwrite"):
            write_outputs(
                output,
                observations,
                ons_workbook=self.ons,
                ukbds_central_workbook=self.central,
                ukbds_confidence_workbook=self.confidence,
            )


if __name__ == "__main__":
    unittest.main()
