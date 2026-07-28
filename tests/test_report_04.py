from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from src.reporting.report_04_ai_use_cases import (
    DENOMINATOR_ID,
    build_report_spec,
    extract_use_case_observations,
    generate_report,
    validate_observations,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/dsit/uk_business_data_survey/2026-06-18"
CENTRAL = RAW / "DSIT_UK_Business_Data_Survey_2026_tables.ods"
CONFIDENCE = RAW / "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods"


class Report04Tests(unittest.TestCase):
    def test_spec_preserves_scope_and_multiple_response_warning(self) -> None:
        rows = extract_use_case_observations(CENTRAL, CONFIDENCE)
        spec = build_report_spec(rows)
        self.assertEqual(len(rows), 28)
        self.assertEqual({row.denominator_id for row in rows}, {DENOMINATOR_ID})
        self.assertEqual(spec["checks"]["indicator_count"], 7)
        self.assertTrue(spec["checks"]["multi_response_warning_present"])
        self.assertFalse(spec["checks"]["formal_significance_claim_present"])

    def test_rejects_interval_that_excludes_estimate(self) -> None:
        rows = extract_use_case_observations(CENTRAL, CONFIDENCE)
        changed = [replace(rows[0], lower_limit=rows[0].estimate + 0.01), *rows[1:]]
        with self.assertRaisesRegex(ValueError, "invalid interval"):
            validate_observations(changed)

    def test_refuses_to_overwrite_before_reading_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "report.pdf"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(FileExistsError, "Report 04"):
                generate_report(
                    output,
                    central_workbook=root / "missing-central.ods",
                    confidence_workbook=root / "missing-confidence.ods",
                    analysis_directory=root / "analysis",
                )


if __name__ == "__main__":
    unittest.main()
