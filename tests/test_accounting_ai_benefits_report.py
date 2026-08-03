import csv
import hashlib
import json
from pathlib import Path
import unittest

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output/pdf/UK_Accounting_SMEs_AI_Benefits_and_System_Fit_2026.pdf"
DATA = ROOT / "data/public/accounting_ai_benefits_system_fit_2026.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class AccountingAIBenefitsReportTests(unittest.TestCase):
    def test_report_preserves_the_claim_boundary(self) -> None:
        self.assertTrue(PDF.exists())
        reader = PdfReader(str(PDF))
        self.assertGreaterEqual(len(reader.pages), 9)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).lower()
        for phrase in (
            "secondary evidence",
            "7.5-7.9",
            "not a uk benchmark",
            "human review",
            "vendor ranking",
            "transaction processing",
            "self-reported",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("proven roi", text)
        self.assertNotIn("autonomous accounting is beneficial", text)
        for page_number, page in enumerate(reader.pages, 1):
            self.assertGreater(len((page.extract_text() or "").strip()), 80, page_number)

    def test_metadata_and_public_data_are_reproducible(self) -> None:
        metadata = json.loads(PDF.with_suffix(".metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["research_mode"], "secondary_data_only")
        self.assertEqual(metadata["approval_status"], "owner_authorised_final_publication")
        self.assertEqual(metadata["publication_status"], "approved_for_distribution")
        self.assertEqual(metadata["output"]["sha256"], sha256(PDF))
        self.assertEqual(metadata["public_data"]["sha256"], sha256(DATA))

        with DATA.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertGreaterEqual(len(rows), 15)
        self.assertEqual({row["evidence_grade"] for row in rows}, {"A", "B", "C", "D", "evidence synthesis"})
        self.assertTrue(all(row["main_limitation"] for row in rows))


if __name__ == "__main__":
    unittest.main()
