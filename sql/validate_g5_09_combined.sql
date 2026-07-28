-- Read-only reconciliation queries for the G5-09 combined processed candidate.

PRAGMA integrity_check;
PRAGMA foreign_key_check;

SELECT 'observation_count' AS check_name, COUNT(*) AS actual, 8 AS expected
FROM observations
UNION ALL
SELECT 'indicator_count', COUNT(*), 2
FROM indicators
UNION ALL
SELECT 'denominator_count', COUNT(*), 2
FROM denominators
UNION ALL
SELECT 'approved_table42_rows', COUNT(*), 4
FROM observations
WHERE source_table_id = '42' AND approval_status = 'approved_processed'
UNION ALL
SELECT 'pending_table48_rows', COUNT(*), 4
FROM observations
WHERE source_table_id = '48'
  AND approval_status = 'accepted_for_schema_design'
UNION ALL
SELECT 'table_41_rows', COUNT(*), 0
FROM observations
WHERE source_table_id = '41'
UNION ALL
SELECT 'invalid_intervals', COUNT(*), 0
FROM observations
WHERE lower_limit > estimate OR estimate > upper_limit;

SELECT
    source_table_id,
    indicator_id,
    denominator_id,
    COUNT(*) AS row_count
FROM observations
GROUP BY source_table_id, indicator_id, denominator_id
ORDER BY CAST(source_table_id AS INTEGER);
