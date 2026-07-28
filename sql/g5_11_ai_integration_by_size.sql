-- G5-11: descriptive AI-system-integration estimates by business-size group.
-- D-015-approved Table 48 data only. The denominator is businesses using AI.
-- This query does not create an all-business estimate or test differences.

SELECT
    o.source_id,
    o.dataset_id,
    o.dataset_version,
    o.source_table_id,
    o.indicator_id,
    i.label AS indicator_label,
    o.period_start,
    o.period_end,
    o.population_label,
    o.denominator_id,
    d.label AS denominator_label,
    d.definition AS denominator_definition,
    o.dimension_type,
    o.dimension_value AS business_size,
    o.source_dimension_label,
    o.scope_role,
    o.estimate,
    ROUND(o.estimate * 100.0, 2) AS estimate_percent,
    o.lower_limit,
    ROUND(o.lower_limit * 100.0, 2) AS lower_limit_percent,
    o.upper_limit,
    ROUND(o.upper_limit * 100.0, 2) AS upper_limit_percent,
    o.confidence_level,
    o.sample_base,
    o.source_status,
    o.run_id,
    o.approval_status
FROM observations AS o
JOIN indicators AS i
  ON i.indicator_id = o.indicator_id
JOIN denominators AS d
  ON d.denominator_id = o.denominator_id
JOIN dataset_releases AS r
  ON r.source_id = o.source_id
 AND r.dataset_id = o.dataset_id
 AND r.dataset_version = o.dataset_version
JOIN pipeline_runs AS p
  ON p.run_id = o.run_id
WHERE o.indicator_id = 'ai_tools_integrated_with_systems'
  AND o.source_table_id = '48'
  AND o.denominator_id = 'uk_businesses_using_ai_technologies'
  AND o.dimension_type = 'business_size'
  AND o.approval_status = 'approved_processed'
  AND r.release_status = 'approved_processed'
  AND p.approval_status = 'approved_processed'
ORDER BY CASE o.dimension_value
    WHEN 'micro' THEN 1
    WHEN 'small' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'large' THEN 4
END;
