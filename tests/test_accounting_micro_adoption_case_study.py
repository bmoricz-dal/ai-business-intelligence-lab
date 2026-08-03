import csv
import hashlib
import json
from pathlib import Path
import unittest

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output/pdf/UK_Micro_Accounting_Practice_AI_Adoption_Worked_Case_2026.pdf"
DATA = ROOT / "data/public/accounting_micro_ai_adoption_playbook_2026.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class AccountingMicroAdoptionCaseTests(unittest.TestCase):
    def test_report_preserves_case_and_claim_boundaries(self) -> None:
        self.assertTrue(PDF.exists())
        reader = PdfReader(str(PDF))
        self.assertGreaterEqual(len(reader.pages), 14)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).lower()
        for phrase in (
            "fictional", "secondary evidence", "seven", "shadow mode",
            "no adoption", "not a sector roi", "professional review",
            "illustrative", "stop or revise",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("will save every firm", text)
        self.assertNotIn("representative practice", text)
        for page_number, page in enumerate(reader.pages, 1):
            self.assertGreater(len((page.extract_text() or "").strip()), 80, page_number)

    def test_publication_metadata_and_playbook_are_reproducible(self) -> None:
        metadata = json.loads(PDF.with_suffix(".metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["research_mode"], "secondary_data_only")
        self.assertEqual(metadata["case_status"], "fictional_composite")
        self.assertEqual(metadata["approval_status"], "owner_authorised_final_publication")
        self.assertEqual(metadata["publication_status"], "approved_for_distribution")
        self.assertEqual(metadata["output"]["sha256"], sha256(PDF))
        self.assertEqual(metadata["public_data"]["sha256"], sha256(DATA))

        with DATA.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertGreaterEqual(len(rows), 40)
        self.assertEqual({row["pathway"] for row in rows}, {"All", "Use", "Integrate", "Automate", "Configure"})
        self.assertTrue(all(row["stop_or_revise_condition"] for row in rows))


if __name__ == "__main__":
    unittest.main()
