import json
import unittest
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf"
REPORTS = {
    "UK_Construction_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf": ["384,525", "21.5%", "not SME-only"],
    "UK_Construction_SMEs_AI_Benefits_and_System_Fit_2026.pdf": ["96.25%", "60 to 15", "does not establish"],
    "UK_Construction_SMEs_AI_Adoption_Journeys_2026.pdf": ["Cast Consultancy", "ConstructionCo", "No pooled ROI"],
    "UK_Construction_SME_AI_Tender_Worked_Case_2026.pdf": ["Northstar Build Ltd", "SIX WORKSTATIONS", "not ROI"],
}


class ConstructionPublicationReportTests(unittest.TestCase):
    def test_reports_exist_with_expected_boundaries_and_metadata(self):
        for filename, phrases in REPORTS.items():
            pdf = OUTPUT / filename
            self.assertTrue(pdf.exists(), filename)
            reader = PdfReader(str(pdf))
            self.assertGreaterEqual(len(reader.pages), 5)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            for phrase in phrases:
                self.assertIn(phrase, text, f"{phrase} missing from {filename}")
            metadata = json.loads((OUTPUT / filename.replace(".pdf", ".metadata.json")).read_text())
            self.assertEqual(metadata["page_count"], len(reader.pages))
            self.assertEqual(metadata["status"], "owner-approved publication")
            self.assertEqual(len(metadata["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
