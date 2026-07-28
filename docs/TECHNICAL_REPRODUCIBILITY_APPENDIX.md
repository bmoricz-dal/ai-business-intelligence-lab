# Technical Reproducibility Appendix

## 1. Pipeline overview

The workflow is:

```text
Official ODS workbooks
    -> fingerprint verification
    -> sheet and cell extraction
    -> source-specific validation
    -> long observation records
    -> CSV and SQLite
    -> saved SQL queries
    -> checked charts and PDFs
```

Raw files are immutable inputs. Interim files support validation. Processed
files contain governed observations. Public extracts contain only the evidence
needed to reproduce the published figures.

## 2. Registered source package

The two analytical workbooks are:

| File | SHA-256 |
|---|---|
| `DSIT_UK_Business_Data_Survey_2026_tables.ods` | `3ad453b41eebcc2af853d3410d649761de2c4421cbe164ebdb79ca8b6f6ae53c` |
| `DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods` | `1eff1276a0073927169941664d623a42c815c619c3e1c6ca0ebf7502a9fce4ef` |

The download helper writes them under:

```text
data/raw/dsit/uk_business_data_survey/2026-06-18/
```

## 3. ODS extraction

ODS files are ZIP archives. `src/transformation/ukbds.py` opens each archive,
reads `content.xml`, locates a named sheet and expands repeated rows and
columns.

The parser recognises numeric percentage and float cells, ordinary text, and
explicit source statuses. It does not edit the original workbook.

The shared source mappings include:

```python
SIZE_LABELS = {
    "Size: Micro (up to 9 employees)": ("micro", "primary"),
    "Size: Small (10 to 49 employees)": ("small", "primary"),
    "Size: Medium (50 to 249 employees)": ("medium", "primary"),
    "Size: Large (250 plus employees)": (
        "large",
        "reference_benchmark",
    ),
}
```

## 4. Source-specific transformations

Each extractor fixes the expected:

- source table;
- indicator column;
- published denominator;
- four size rows;
- lower and upper confidence sheets;
- source status; and
- respondent base.

The transformation stops when a required sheet, column, size group,
denominator note or value is missing or different from its controlled
definition.

## 5. Observation model

One row represents one estimate for one indicator, period and breakdown.
Important fields include:

- source and dataset identifiers;
- release version and source table;
- indicator;
- fieldwork period;
- population and denominator;
- business-size value and original source label;
- primary or benchmark role;
- estimate and supplied confidence limits;
- confidence level and respondent base;
- source status;
- pipeline run; and
- approval status.

Estimates are stored as proportions. For example, `0.3744` is displayed as
`37.44%`. Display rounding is separate from stored analytical values.

## 6. SQLite controls

`sql/schema.sql` defines five connected tables:

1. dataset releases;
2. indicators;
3. denominators;
4. pipeline runs; and
5. observations.

Foreign keys prevent observations from referring to unknown sources,
indicators, denominators or production runs.

Database checks reject:

- proportions outside zero to one;
- confidence limits that do not contain the estimate;
- one missing confidence limit when the other is present;
- non-positive respondent bases;
- numeric values attached to suppressed or missing cells;
- invalid roles, units or statuses; and
- duplicate logical observations.

## 7. Saved analysis queries

`sql/g5_01_ai_use_by_size.sql` selects only:

- Table 42;
- the AI-use indicator;
- the all-business denominator;
- business-size observations; and
- approved processed data.

`sql/g5_11_ai_integration_by_size.sql` selects only:

- Table 48;
- the system-integration indicator;
- the AI-user denominator;
- business-size observations; and
- approved processed data.

Both queries return the unrounded proportions, display percentages, confidence
limits, bases, roles, source details and pipeline identifiers.

## 8. Report mappings

| Report | Source tables | Main denominator |
|---|---|---|
| 1 | 42 | All UK businesses |
| 2 | 42 and 48 | Separate all-business and AI-user panels |
| 3 | 50 | Businesses using AI |
| 4 | 42 purpose categories | All UK businesses; multiple response |
| 5 | 43, 47, 48 and 50 | Separate all-business and AI-user panels |

No report calculates a new survey weight or changes a published estimate.

## 9. Validation design

Validation is layered:

1. SHA-256 checks confirm the registered source files.
2. Python checks confirm expected tables, labels, denominators and values.
3. Cross-workbook checks confirm matching central estimates and bases.
4. Confidence checks confirm valid interval ordering.
5. SQLite checks protect the processed layer.
6. SQL result checks reconcile analytical outputs with the database.
7. Report tests confirm values, warnings and scope.
8. PDF pages are rendered and inspected visually.

Tests also deliberately supply bad inputs. Examples include an estimate outside
its interval, an incorrect unit, a duplicate observation or a changed
denominator. The expected result is rejection.

## 10. Group comparison method

The official workbook provides weighted estimates and 95% confidence limits.
It does not provide enough published design information to reproduce a formal
pairwise test between size groups.

An approximate test derived from the intervals would require assumptions about
independence, covariance and survey design. The project therefore uses the
intervals to describe uncertainty but does not claim formal significance.

## 11. PDF production

ReportLab creates the PDFs programmatically. Charts, exact-value tables,
denominator warnings, source notes and limitations are generated from
controlled inputs.

Each PDF is rendered to PNG using Poppler. Visual review checks:

- clipping;
- overlapping labels;
- unreadable text;
- broken tables;
- unclear chart legends;
- missing denominator warnings; and
- page numbering.

Text extraction provides an additional content check but does not replace
visual inspection.

## 12. Public data extracts

The files in `data/public/` retain the published estimates, confidence limits,
business-size labels, denominators and bases used by the reports.

Raw workbooks are not committed. Run:

```bash
python scripts/download_sources.py
```

The script downloads the official files and stops if their SHA-256 values do
not match the registered release.

## 13. Reproduction commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python scripts/download_sources.py
python -m unittest discover -s tests -v
python tools/generate_public_method_pdfs.py
```

The public result extracts allow readers to inspect the reported evidence
without downloading the raw workbooks.

## 14. Known boundaries and next work

- The current evidence uses one official survey release.
- Cross-survey comparison has not been implemented.
- Clean-environment reproduction should be recorded in a future release.
- Sector analysis requires separate checks of respondent bases, suppression and
  interval width.
- A formal open-source licence for original project code remains to be chosen.
- The live website needs final Method and GitHub links, status-language cleanup
  and live accessibility testing.
