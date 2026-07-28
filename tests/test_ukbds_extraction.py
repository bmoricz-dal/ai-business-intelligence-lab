from dataclasses import replace
from html import escape
from pathlib import Path
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from src.transformation.ukbds import (
    SIZE_LABELS,
    extract_ai_use_by_size,
    validate_observations,
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


def blank_cell() -> str:
    return "<table:table-cell/>"


def table_xml(name: str, estimates: dict[str, float]) -> str:
    rows = ["<table:table-row><table:table-cell/></table:table-row>" for _ in range(7)]
    header = [
        string_cell("Breakdown"),
        string_cell("Uses any Artificial Intelligence-based technologies"),
        string_cell("Unweighted base"),
    ]
    rows.append(f"<table:table-row>{''.join(header)}</table:table-row>")
    rows.append(
        f"<table:table-row>{string_cell('Total')}{number_cell(0.4)}"
        f"{number_cell(4450, 'float')}</table:table-row>"
    )
    bases = {"micro": 2500, "small": 680, "medium": 220, "large": 130}
    for label, (size_id, _) in SIZE_LABELS.items():
        rows.append(
            f"<table:table-row>{string_cell(label)}"
            f"{number_cell(estimates[size_id])}"
            f"{number_cell(bases[size_id], 'float')}</table:table-row>"
        )
    return f'<table:table table:name="{name}">{"".join(rows)}</table:table>'


def write_ods(path: Path, tables: list[str]) -> None:
    content = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content {NS_DECLARATIONS}>'
        f'<office:body><office:spreadsheet>{"".join(tables)}'
        f"</office:spreadsheet></office:body></office:document-content>"
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("content.xml", content)


class UkbdsExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.central = directory / "central.ods"
        self.confidence = directory / "confidence.ods"
        central = {"micro": 0.37, "small": 0.51, "medium": 0.57, "large": 0.78}
        lower = {"micro": 0.35, "small": 0.47, "medium": 0.50, "large": 0.71}
        upper = {"micro": 0.40, "small": 0.55, "medium": 0.64, "large": 0.86}
        write_ods(self.central, [table_xml("42", central)])
        write_ods(
            self.confidence,
            [
                table_xml("42", central),
                table_xml("42_lcl", lower),
                table_xml("42_ucl", upper),
            ],
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_extracts_primary_rows_and_large_benchmark(self) -> None:
        observations = extract_ai_use_by_size(
            self.central,
            self.confidence,
            enforce_registered_checksums=False,
        )

        self.assertEqual(
            [observation.business_size for observation in observations],
            ["micro", "small", "medium", "large"],
        )
        self.assertEqual(observations[0].estimate, 0.37)
        self.assertEqual(observations[0].lower_limit, 0.35)
        self.assertEqual(observations[0].upper_limit, 0.40)
        self.assertEqual(observations[-1].scope_role, "reference_benchmark")

    def test_rejects_confidence_limits_that_do_not_contain_estimate(self) -> None:
        observations = extract_ai_use_by_size(
            self.central,
            self.confidence,
            enforce_registered_checksums=False,
        )
        invalid = [replace(observations[0], lower_limit=0.50), *observations[1:]]

        with self.assertRaisesRegex(ValueError, "do not contain estimate"):
            validate_observations(invalid)

    def test_interim_writer_refuses_silent_overwrite(self) -> None:
        observations = extract_ai_use_by_size(
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
