# Data and Methods Guide

## Purpose

This guide explains, in plain language, how the evidence behind the first five
AI Business Intelligence Lab reports was collected, organised, checked and
analysed.

The project uses published official statistics. It does not survey businesses
itself and does not change the official survey estimates.

## Official source

The evidence comes from the Department for Science, Innovation and
Technology's UK Business Data Survey 2026.

- Publication date: 18 June 2026
- Fieldwork: 10 October 2025 to 28 January 2026
- Survey unit: UK business enterprise or head office
- Published estimates: weighted to represent the UK business population
- Uncertainty: official 95% confidence limits supplied in the workbook

Two official ODS workbooks were used. One provides the published central
estimates. The second provides the same estimates plus separate lower and upper
confidence-limit sheets.

## The five reports

### Report 1 - Reported AI use

- Source: Table 42
- Question: what percentage of businesses reported using any listed AI-based
  technology?
- Denominator: all UK businesses in each published size group.

### Report 2 - AI use and system integration

- Sources: Tables 42 and 48
- Table 42 describes all businesses.
- Table 48 describes businesses that already report using AI.
- The two percentages are displayed separately and are not multiplied,
  subtracted or combined.

### Report 3 - AI governance

- Source: Table 50
- Question: what percentage of AI-using businesses reported formal or informal
  AI policy or guidance?
- Denominator: businesses that report using AI.

### Report 4 - How businesses use AI

- Source: Table 42 purpose categories
- Seven categories are retained: summarising or drafting, research, computer
  code, data analysis or models, customer chatbots, images or videos, and
  cybersecurity.
- Businesses could report more than one purpose, so the percentages overlap.

### Report 5 - Operational adoption pathways

- Sources: Tables 43, 47, 48 and 50
- Integration, automated decisions and governance describe AI-using
  businesses.
- In-house AI development or training describes all businesses.
- The indicators are not combined into a readiness or maturity score.

## Business-size structure

The published employer-size groups were retained:

- micro: 1 to 9 employees;
- small: 10 to 49 employees;
- medium: 50 to 249 employees; and
- large: 250 or more employees.

Micro, small and medium businesses are the primary SME scope. Large businesses
are shown only as a reference benchmark. The separately published sole-trader
group was not included in the employer-SME comparisons.

## What data preparation meant

The source estimates were not edited or re-estimated. Preparation consisted of:

1. checking that the downloaded files matched registered fingerprints;
2. opening the required workbook sheets;
3. locating the required question columns and business-size rows;
4. matching the central, lower-limit and upper-limit sheets;
5. preserving the original labels and respondent bases;
6. assigning clear indicator and denominator identifiers;
7. restructuring the selected cells into one observation per row; and
8. writing checked CSV and SQLite outputs.

The source codes were retained:

- `c` means the result was suppressed;
- `z` means the question was not asked;
- blank means missing; and
- none of these states was changed to zero.

## Analytical method

The analysis is descriptive. It reports official weighted point estimates and
their supplied 95% confidence intervals.

The project describes patterns such as a sequence of higher point estimates
across business-size groups. It does not say that business size caused the
pattern.

The published package does not provide respondent-level data, final
respondent weights, replicate weights, covariance information or an official
pairwise testing method. For that reason, the reports do not label
size-group differences as statistically significant.

## Data-quality checks

Automated checks confirm that:

- both official workbooks have the expected fingerprints;
- the same central estimate appears in both workbooks;
- central, lower and upper sheets use matching rows and statuses;
- every lower limit is at or below its estimate;
- every upper limit is at or above its estimate;
- proportions stay between zero and one;
- respondent bases are positive;
- the expected number of rows is present;
- denominators cannot silently change;
- large businesses remain labelled as a benchmark; and
- existing approved outputs are not silently overwritten.

SQLite adds a second layer of rules. It rejects invalid percentages, broken
confidence intervals, duplicate observations, unknown denominators and numeric
values attached to suppressed or missing cells.

## Tools

- Python: source extraction, transformation, validation and report generation.
- XML and ZIP libraries: reading the internal structure of ODS workbooks.
- CSV and JSON: readable data outputs and audit metadata.
- SQLite and SQL: rule-protected storage and repeatable analytical queries.
- SHA-256: confirming that inputs and reviewed outputs have not changed.
- ReportLab: creating charts, tables and PDF reports.
- Python unittest: automated checks.
- Poppler tools: rendering PDF pages for visual inspection.
- Visual Studio Code: code development and file review.
- Git and GitHub: version history and public reproducibility.

## Important limits

- These are survey estimates, not counts of UK businesses.
- Rounded unweighted bases are respondent bases.
- Confidence intervals show uncertainty around individual estimates.
- The reports do not measure productivity, return on investment, quality or
  business impact.
- The reports do not prove causation.
- Multiple-response use-case percentages must not be added.
- Percentages with different denominators must not be combined.

## Evidence trail

The public GitHub repository provides the extraction code, saved SQL queries,
tests, source register, public result extracts and technical appendix. The
official source remains the authoritative record.
