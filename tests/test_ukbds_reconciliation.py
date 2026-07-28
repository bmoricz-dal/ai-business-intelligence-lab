from dataclasses import replace
from html import escape
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

from src.validation.ukbds_reconciliation import (
    TARGET_ROWS,
    reconcile_table41,
    validate_reconciliation,
    write_reconciliation_outputs,
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


def table_xml(estimates: dict[str, float]) -> str:
    rows = ["<table:table-row><table:table-cell/></table:table-row>" for _ in range(7)]
    rows.append(
        "<table:table-row>"
        + string_cell("Breakdown")
        + string_cell("Uses any Artificial Intelligence-based technologies")
        + string_cell("Unweighted base")
        + "</table:table-row>"
    )
    bases = {
        "total": 4090,
        "sole_trader": 770,
        "micro": 2310,
        "small": 670,
        "medium": 210,
        "large": 130,
    }
    for label, size_id in TARGET_ROWS:
        rows.append(
            "<table:table-row>"
            + string_cell(label)
            + number_cell(estimates[size_id])
            + number_cell(bases[size_id], "float")
            + "</table:table-row>"
        )
    return '<table:table table:name="41">' + "".join(rows) + "</table:table>"


def write_ods(path: Path, estimates: dict[str, float]) -> None:
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<office:document-content {NS_DECLARATIONS}>"
        "<office:body><office:spreadsheet>"
        + table_xml(estimates)
        + "</office:spreadsheet></office:body></office:document-content>"
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("content.xml", content)


class UkbdsReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.central = directory / "central.ods"
        self.confidence = directory / "confidence.ods"
        self.publication = directory / "publication.html"
        estimates = {
            "total": 0.406987,
            "sole_trader": 0.397437,
            "micro": 0.407718,
            "small": 0.514938,
            "medium": 0.577541,
            "large": 0.81753,
        }
        write_ods(self.central, estimates)
        write_ods(self.confidence, estimates)
        self.publication.write_text("test fixture", encoding="utf-8")
        self.publication_values = {
            "total": 41,
            "sole_trader": 40,
            "micro": 41,
            "small": 51,
            "medium": 58,
            "large": 82,
        }

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def reconcile(self):
        with patch(
            "src.validation.ukbds_reconciliation.parse_publication_values",
            return_value=(self.publication_values, 4090),
        ):
            return reconcile_table41(
                self.central,
                self.confidence,
                self.publication,
                enforce_registered_checksums=False,
            )

    def test_reconciles_all_six_rounded_publication_values(self) -> None:
        rows = self.reconcile()

        self.assertEqual(len(rows), 6)
        self.assertEqual([row.workbook_rounded_percent for row in rows], [41, 40, 41, 51, 58, 82])
        self.assertTrue(all(row.reconciliation_status == "passed" for row in rows))
        self.assertEqual(rows[0].workbook_row_unweighted_base, 4090)

    def test_rejects_a_rounded_publication_mismatch(self) -> None:
        rows = self.reconcile()
        invalid = [replace(rows[0], reconciliation_status="failed"), *rows[1:]]

        with self.assertRaisesRegex(ValueError, "reconciliation failed"):
            validate_reconciliation(invalid)

    def test_rejects_central_workbook_disagreement(self) -> None:
        changed = {
            "total": 0.40,
            "sole_trader": 0.397437,
            "micro": 0.407718,
            "small": 0.514938,
            "medium": 0.577541,
            "large": 0.81753,
        }
        write_ods(self.central, changed)

        with self.assertRaisesRegex(ValueError, "Central estimate mismatch"):
            self.reconcile()

    def test_writer_refuses_silent_overwrite(self) -> None:
        rows = self.reconcile()
        output = Path(self.temporary_directory.name) / "reconciliation.csv"
        write_reconciliation_outputs(
            output,
            rows,
            central_workbook=self.central,
            confidence_workbook=self.confidence,
            publication_html=self.publication,
        )

        with self.assertRaisesRegex(FileExistsError, "Refusing to overwrite"):
            write_reconciliation_outputs(
                output,
                rows,
                central_workbook=self.central,
                confidence_workbook=self.confidence,
                publication_html=self.publication,
            )


if __name__ == "__main__":
    unittest.main()
