# Accounting AI Adoption Journeys — public data dictionary

The public file `data/public/accounting_ai_adoption_journeys_2026.csv` contains one row per transparent case or case bundle. It is a qualitative evidence index, not a statistical dataset.

| Field | Definition |
|---|---|
| `case_id` | Stable machine-readable identifier. |
| `case_title` | Public-facing case or bundle name. |
| `case_classification` | Core practice evidence, multi-source synthesis, historical comparator or transfer case. |
| `geography` | Geography reported by the underlying source; “international” is not converted into UK evidence. |
| `firm_context` | Firm, sample or organisational setting. |
| `strongest_grade` | Strongest evidence grade present in the row. A stronger component does not upgrade weaker outcomes in the same bundle. |
| `journey_summary` | Bounded summary of reported implementation events. |
| `outcome_summary` | Outcomes with their evidential status retained. |
| `outcome_status` | Experimental, associated, qualitative, self-reported, comparator-only or transfer-only. |
| `principal_limit` | Most important constraint on interpretation or transfer. |
| `source_ids` | Semicolon-separated keys joining the source register. |

## Non-permitted uses

The file must not be used to calculate an average AI benefit, adoption success rate, ROI, vendor score, UK SME benchmark or causal workforce effect. Rows have different units, populations, designs and purposes.
