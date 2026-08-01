import csv
import hashlib
import json
from pathlib import Path
import unittest

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "publications/UK_Accounting_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf"
DATA = ROOT / "data/public/accounting_ai_readiness_2026.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class AccountingAIReadinessReportTests(unittest.TestCase):
    def test_final_report_is_publication_ready(self) -> None:
        self.assertTrue(PDF.exists())
        reader = PdfReader(str(PDF))
        self.assertGreaterEqual(len(reader.pages), 10)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        for phrase in (
            "secondary evidence only",
            "39,860",
            "26%",
            "71.38%",
            "series",
            "no impact claim",
            "SIC 69.20",
        ):
            self.assertIn(phrase.lower(), text.lower())
        self.assertNotRegex(text.lower(), r"not for publication|owner review pending|draft finding")
        for page_number, page in enumerate(reader.pages, 1):
            self.assertGreater(len((page.extract_text() or "").strip()), 80, page_number)

    def test_metadata_matches_report(self) -> None:
        metadata = json.loads(PDF.with_suffix(".metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["research_mode"], "secondary_data_only")
        self.assertEqual(metadata["approval_status"], "owner_authorised_final_publication")
        self.assertEqual(metadata["publication_status"], "approved_for_distribution")
        self.assertEqual(metadata["output"]["sha256"], sha256(PDF))
        self.assertEqual(metadata["public_data"]["sha256"], sha256(DATA))

    def test_public_data_preserves_evidence_roles(self) -> None:
        with DATA.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertGreaterEqual(len(rows), 30)
        self.assertEqual(
            {row["evidence_role"] for row in rows},
            {"direct_frame", "direct_directional", "contextual_proxy"},
        )
        accounting_adoption = [row for row in rows if row["indicator_id"] == "adopted_ai"]
        self.assertEqual(len(accounting_adoption), 1)
        self.assertEqual(accounting_adoption[0]["estimate"], "0.26")


if __name__ == "__main__":
    unittest.main()
