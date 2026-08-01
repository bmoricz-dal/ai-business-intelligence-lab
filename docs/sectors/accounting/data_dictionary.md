# Accounting-sector data dictionary

Status: scope-approved sector extension; processed-schema promotion pending review

The approved general long model remains the starting point. The accounting programme adds explicit source-role and target-population controls before any cross-source synthesis.

| Field | Definition | Control |
|---|---|---|
| `target_population_match` | `direct`, `contextual_proxy`, `directional`, or `not_comparable` | Required before analysis |
| `accounting_scope` | Practice, bookkeeping, tax, audit, in-house finance, broad professional services or mixed | In-house and mixed sources cannot silently represent practices |
| `sector_code` | Source SIC code at its published granularity | Preserve SIC version and code |
| `size_measure` | Employees, employment, turnover, accounts category or unspecified | Size measures are not interchangeable |
| `ai_scope` | Source definition of AI or named technology set | Distinguish generative AI from wider AI |
| `adoption_state` | Pilot, current use, embedded, integrated, automated or in-house where directly asked | Do not infer a maturity stage |
| `multiple_response` | Whether response categories overlap | Overlapping percentages are not added |
| `comparability_grade` | `A_direct`, `B_contextual`, `C_directional`, or `D_prohibited` | Required for every proposed comparison |
| `source_locator` | File, table, question, row, page or chart | Required for claim traceability |
| `review_status` | Draft, validated, owner-approved or rejected | Only approved findings publish |

The first baseline uses the existing fields `source_id`, `dataset_id`, `dataset_version`, `source_table_id`, `indicator_id`, `period_start`, `period_end`, `population_label`, `denominator_label`, `unit`, `dimension_type`, `dimension_value`, `source_dimension_label`, `scope_role`, `estimate`, `lower_limit`, `upper_limit`, `confidence_level`, `sample_base`, `source_status` and `notes`.

The `scope_role` value is `context` for both the SIC 69.20 population frame and broad SIC M AI observations. Population counts describe who is in scope; broad-sector percentages provide comparison context. They are not mathematically combined.
