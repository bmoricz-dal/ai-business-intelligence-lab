from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from src.reporting.report_03_ai_governance import (
    DENOMINATOR,
    DENOMINATOR_ID,
    INDICATOR_ID,
    PolicyObservation,
    build_report_spec,
    generate_report,
    validate_observations,
)


def observations() -> list[PolicyObservation]:
    values = [
        ("micro", "primary", 0.201, 0.173, 0.228, 960),
        ("small", "primary", 0.290, 0.238, 0.342, 350),
        ("medium", "primary", 0.368, 0.278, 0.457, 130),
        ("large", "reference_benchmark", 0.677, 0.581, 0.772, 100),
    ]
    return [
        PolicyObservation(
            source_id="dsit_ukbds_2026",
            dataset_id="uk_business_data_survey",
            dataset_version="2026-06-18",
            table_id="50",
            indicator_id=INDICATOR_ID,
            period="2025-10-10 to 2026-01-28",
            denominator_id=DENOMINATOR_ID,
            denominator=DENOMINATOR,
            business_size=size,
            source_business_size_label=size,
            scope_role=role,
            estimate=estimate,
            lower_limit=lower,
            upper_limit=upper,
            sample_base=base,
            source_status="observed",
        )
        for size, role, estimate, lower, upper, base in values
    ]


class Report03Tests(unittest.TestCase):
    def test_spec_preserves_conditional_scope(self) -> None:
        spec = build_report_spec(observations())
        self.assertEqual(spec["finding_id"], "F-003")
        self.assertEqual(spec["denominator_id"], DENOMINATOR_ID)
        self.assertEqual(spec["checks"]["row_count"], 4)
        self.assertTrue(spec["checks"]["conditional_denominator_visible"])
        self.assertFalse(spec["checks"]["all_business_conversion_present"])
        self.assertIn("not approved", spec["governance_boundary"])

    def test_rejects_interval_that_excludes_estimate(self) -> None:
        rows = observations()
        invalid = [replace(rows[0], lower_limit=0.30), *rows[1:]]
        with self.assertRaisesRegex(ValueError, "Invalid Table 50 interval"):
            validate_observations(invalid)

    def test_refuses_to_overwrite_before_reading_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "report.pdf"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(FileExistsError, "Refusing to overwrite"):
                generate_report(
                    output,
                    central_workbook=root / "missing-central.ods",
                    confidence_workbook=root / "missing-confidence.ods",
                    analysis_directory=root / "analysis",
                )


if __name__ == "__main__":
    unittest.main()
