# Code map

This repository preserves the implementation behind the first five reports.

## Main workflow

| Purpose | Main files |
|---|---|
| Read and validate the official ODS workbooks | `src/transformation/ukbds.py` |
| Extract AI-system integration data | `src/transformation/ukbds_ai_integration.py` |
| Build the governed processed data | `src/transformation/processed.py`, `src/transformation/processed_combined.py` |
| Define database rules | `sql/schema.sql` |
| Run the first two saved analyses | `sql/g5_01_ai_use_by_size.sql`, `sql/g5_11_ai_integration_by_size.sql` |
| Reconcile published rounded figures | `src/validation/ukbds_reconciliation.py` |
| Build charts and evidence briefs | `src/analysis/` |
| Build Reports 1–5 | `src/reporting/` |
| Generate the public methods PDFs | `tools/generate_public_method_pdfs.py` |
| Publication-ready reports and synthesis | `publications/SME_Report_*.pdf`, `publications/SME_Cross_Report_*.pdf` |

## Publication suite

The repository includes the five final research reports and a separate
cross-report synthesis. The synthesis does not calculate a maturity score or
combine estimates with different denominators. It connects the reports through
bounded descriptive interpretations while the individual PDFs retain the exact
estimates, supplied confidence intervals, respondent bases and limitations.

## Tests included

The public test set focuses on the source-facing controls that matter most to
independent review:

- ODS extraction;
- confidence-interval ordering;
- denominator preservation;
- large-business benchmark labelling;
- reconciliation with the published report;
- Report 4 multiple-response handling; and
- Report 5 separation of all-business and AI-user measures.

Run the checks with:

```bash
python -m unittest discover -s tests -v
```

## Historical workflow status labels

Some modules contain labels such as `owner_review_pending` or `not_approved`.
These are retained because they show the original controlled review workflow
and are used by the validation code. They are not credentials, access settings
or a statement about the current public website. The current reader-facing
status is described in the repository `README.md`.

## Deliberate exclusions

The repository does not include:

- raw government workbooks, because the official files can be downloaded and
  fingerprint-checked with `scripts/download_sources.py`;
- local SQLite databases or temporary processing files;
- private development logs and internal working notes; or
- website deployment credentials and platform configuration.
