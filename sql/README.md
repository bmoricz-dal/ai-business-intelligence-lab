# SQL

This directory contains the D-008-approved SQLite schema, followed later by validation queries, reusable views, and approved analytical queries.

- `schema.sql` creates the empty long analytical structure and its safety constraints.
- Creating the tables does not approve or load processed data.
- D-008 approved the schema on 23 July 2026.
- `validate_processed.sql` checks row counts, roles, intervals, and Table 41 exclusion.
- `g5_01_ai_use_by_size.sql` is the first controlled descriptive query. It reads only D-009-approved rows and retains the denominator, confidence intervals, sample bases, and large-business benchmark flag.
