from dataclasses import replace
from html import escape
from pathlib import Path
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from src.transformation.ukbds import SIZE_LABELS
from src.transformation.ukbds_ai_integration import (
    DENOMINATOR,
    extract_ai_integration_by_size,
    validate_integration_observations,
    write_interim_outputs,
)


NS_DECLARATIONS = (
    'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
    'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
    'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
)


def string_cell(value: str) -> str:
    return (
        '<table:table-cell office:value-type="string">'
        f"<text:p>{escape(value)}</text:p></table:table-cell>"
    )


def number_cell(value: float, value_type: str = "percentage") -> str:
    return (
        f'<table:table-cell office:value-type="{value_type}" '
        f'office:value="{value}"><text:p>{value}</text:p></table:table-cell>'
    )


def table_xml(name: str, estimates: dict[str, float]) -> str:
    rows = ["<table:table-row><table:table-cell/></table:table-row>" for _ in range(7)]
    header = [
        string_cell("Breakdown"),
        string_cell("Yes"),
        string_cell("No"),
        string_cell("Don't know"),
        string_cell("Unweighted base"),
    ]
    rows.append(f"<table:table-row>{''.join(header)}</table:table-row>")
    rows.append(
        f"<table:table-row>{string_cell('Total')}{number_cell(0.21)}"
        f"{number_cell(0.77)}{number_cell(0.02)}"
        f"{number_cell(1870, 'float')}</table:table-row>"
    )
    rows.append(
        f"<table:table-row>{string_cell('Size: Sole trader')}"
        f"{number_cell(0.18)}{number_cell(0.80)}{number_cell(0.02)}"
        f"{number_cell(320, 'float')}</table:table-row>"
    )
    bases = {"micro": 960, "small": 350, "medium": 130, "large": 100}
    for label, (size_id, _) in SIZE_LABELS.items():
        rows.append(
            f"<table:table-row>{string_cell(label)}"
            f"{number_cell(estimates[size_id])}"
            f"{number_cell(0.60)}{number_cell(0.02)}"
            f"{number_cell(bases[size_id], 'float')}</table:table-row>"
        )
    return f'<table:table table:name="{name}">{"".join(rows)}</table:table>'


def write_ods(path: Path, tables: list[str]) -> None:
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content {NS_DECLARATIONS}>'
        f'<office:body><office:spreadsheet>{"".join(tables)}'
        "</office:spreadsheet></office:body></office:document-content>"
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("content.xml", content)


class UkbdsAiIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.central = directory / "central.ods"
        self.confidence = directory / "confidence.ods"
        central = {"micro": 0.27, "small": 0.31, "medium": 0.31, "large": 0.57}
        lower = {"micro": 0.24, "small": 0.26, "medium": 0.22, "large": 0.47}
        upper = {"micro": 0.30, "small": 0.37, "medium": 0.39, "large": 0.68}
        write_ods(self.central, [table_xml("48", central)])
        write_ods(
            self.confidence,
            [
                table_xml("48", central),
                table_xml("48_lcl", lower),
                table_xml("48_ucl", upper),
            ],
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_extracts_conditional_integration_rows(self) -> None:
        observations = extract_ai_integration_by_size(
            self.central,
            self.confidence,
            enforce_registered_checksums=False,
        )
        self.assertEqual(
            [item.business_size for item in observations],
            ["micro", "small", "medium", "large"],
        )
        self.assertEqual(observations[0].estimate, 0.27)
        self.assertEqual(observations[0].denominator, DENOMINATOR)
        self.assertEqual(observations[-1].scope_role, "reference_benchmark")

    def test_rejects_interval_that_excludes_estimate(self) -> None:
        observations = extract_ai_integration_by_size(
            self.central,
            self.confidence,
            enforce_registered_checksums=False,
        )
        invalid = [replace(observations[0], lower_limit=0.40), *observations[1:]]
        with self.assertRaisesRegex(ValueError, "do not contain estimate"):
            validate_integration_observations(invalid)

    def test_writer_refuses_silent_overwrite(self) -> None:
        observations = extract_ai_integration_by_size(
            self.central,
            self.confidence,
            enforce_registered_checksums=False,
        )
        output = Path(self.temporary_directory.name) / "interim.csv"
        write_interim_outputs(
            output,
            observations,
            central_workbook=self.central,
            confidence_workbook=self.confidence,
        )
        with self.assertRaisesRegex(FileExistsError, "Refusing to overwrite"):
            write_interim_outputs(
                output,
                observations,
                central_workbook=self.central,
                confidence_workbook=self.confidence,
            )


if __name__ == "__main__":
    unittest.main()
