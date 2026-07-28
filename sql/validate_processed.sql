-- Read-only reconciliation queries for the UKBDS 2026 processed candidate.

PRAGMA integrity_check;
PRAGMA foreign_key_check;

SELECT 'observation_count' AS check_name, COUNT(*) AS actual, 4 AS expected
FROM observations
UNION ALL
SELECT 'primary_count', COUNT(*), 3
FROM observations
WHERE scope_role = 'primary'
UNION ALL
SELECT 'reference_benchmark_count', COUNT(*), 1
FROM observations
WHERE scope_role = 'reference_benchmark'
UNION ALL
SELECT 'table_41_rows', COUNT(*), 0
FROM observations
WHERE source_table_id = '41'
UNION ALL
SELECT 'invalid_intervals', COUNT(*), 0
FROM observations
WHERE lower_limit > estimate OR estimate > upper_limit;

SELECT
    dimension_value,
    estimate,
    lower_limit,
    upper_limit,
    sample_base,
    scope_role,
    approval_status
FROM observations
ORDER BY CASE dimension_value
    WHEN 'micro' THEN 1
    WHEN 'small' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'large' THEN 4
END;
