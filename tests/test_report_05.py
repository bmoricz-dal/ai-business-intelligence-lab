from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from src.reporting.report_05_adoption_pathways import (
    AI_USER_DENOMINATOR_ID,
    ALL_BUSINESS_DENOMINATOR_ID,
    build_report_spec,
    extract_pathway_observations,
    generate_report,
    validate_observations,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/dsit/uk_business_data_survey/2026-06-18"
CENTRAL = RAW / "DSIT_UK_Business_Data_Survey_2026_tables.ods"
CONFIDENCE = RAW / "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods"


class Report05Tests(unittest.TestCase):
    def test_spec_preserves_two_denominators_without_score(self) -> None:
        rows = extract_pathway_observations(CENTRAL, CONFIDENCE)
        spec = build_report_spec(rows)
        self.assertEqual(len(rows), 16)
        self.assertEqual(
            {row.denominator_id for row in rows},
            {AI_USER_DENOMINATOR_ID, ALL_BUSINESS_DENOMINATOR_ID},
        )
        self.assertTrue(spec["checks"]["denominators_separated"])
        self.assertFalse(spec["checks"]["composite_score_present"])
        self.assertFalse(spec["checks"]["formal_significance_claim_present"])

    def test_rejects_interval_that_excludes_estimate(self) -> None:
        rows = extract_pathway_observations(CENTRAL, CONFIDENCE)
        changed = [replace(rows[0], upper_limit=rows[0].estimate - 0.01), *rows[1:]]
        with self.assertRaisesRegex(ValueError, "invalid interval"):
            validate_observations(changed)

    def test_refuses_to_overwrite_before_reading_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "report.pdf"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(FileExistsError, "Report 05"):
                generate_report(
                    output,
                    central_workbook=root / "missing-central.ods",
                    confidence_workbook=root / "missing-confidence.ods",
                    analysis_directory=root / "analysis",
                )


if __name__ == "__main__":
    unittest.main()
