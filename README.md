# AI Business Intelligence Lab

An evidence-led research project examining how UK businesses report adopting,
using, integrating and governing artificial intelligence.

## Public outputs

- [Live evidence website](https://ai-business-intelligence-lab.moricz-labs.workers.dev/)
- [Report 1 — AI Use by Business Size](publications/SME_Report_01_AI_Use_by_Business_Size.pdf)
- [Report 2 — AI Adoption and System Integration](publications/SME_Report_02_AI_Adoption_and_System_Integration_by_Size.pdf)
- [Report 3 — AI Governance by Business Size](publications/SME_Report_03_AI_Governance_by_Business_Size.pdf)
- [Report 4 — How UK Businesses Use AI](publications/SME_Report_04_How_UK_Businesses_Use_AI.pdf)
- [Report 5 — Operational AI Adoption Pathways](publications/SME_Report_05_Operational_AI_Adoption_Pathways.pdf)
- [Cross-report synthesis — AI Adoption and Operationalisation](publications/SME_Cross_Report_Synthesis_AI_Adoption_and_Operationalisation.pdf)
- [Plain-language Data and Methods Guide](publications/AI_Business_Intelligence_Lab_Data_and_Methods_Guide.pdf)
- [Technical Reproducibility Appendix](publications/AI_Business_Intelligence_Lab_Technical_Reproducibility_Appendix.pdf)
- [Code map](docs/CODE_MAP.md)
- [Release fingerprints](CHECKSUMS.sha256)
- [Official UK Business Data Survey 2026](https://www.gov.uk/government/statistics/uk-business-data-survey-2026)

## What the project does

The first five reports use published tables from the Department for Science,
Innovation and Technology's UK Business Data Survey 2026. They cover:

1. reported use of AI by business size;
2. system integration among businesses already using AI;
3. AI policy or guidance among businesses already using AI;
4. reported AI use cases; and
5. operational adoption pathways.

The primary analytical scope is micro, small and medium businesses. Large
businesses are shown only as a separately labelled reference benchmark.

The cross-report synthesis brings the five reports together without combining
incompatible percentages. Its main evidence-led interpretation is that reported
AI reach and operational depth are different questions: wider reported use does
not mean that tools are integrated, governed or developed in the same way.

## Evidence rules

- Every estimate keeps its published denominator.
- Supplied 95% confidence intervals are retained.
- Rounded unweighted bases are treated as respondent bases, not business counts.
- Suppressed, not-asked and missing cells are never changed to zero.
- Multiple-response percentages are not added together.
- All-business and AI-user percentages are not combined.
- Findings are descriptive. The project does not claim causation or formal
  pairwise statistical significance from the published tables.

## Repository structure

```text
data/public/       Publication-ready result extracts
docs/              Methods, source register and website completion plan
publications/      Five research reports, synthesis and methods documents
scripts/           Source acquisition helper
sql/               Analytical schema and saved queries
src/               Extraction, validation, analysis and reporting code
tests/             Selected automated checks
tools/             PDF generation code
```

The [code map](docs/CODE_MAP.md) connects each research step to its main
implementation files and explains the historical review-status labels retained
in the workflow code.

## Reproduce the workflow

Python 3.12 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python scripts/download_sources.py
python -m unittest discover -s tests -v
python tools/generate_public_method_pdfs.py
```

The source download script retrieves the two official ODS workbooks and checks
their SHA-256 fingerprints before they are used.

## Data availability

Raw official workbooks are not stored in this repository. The acquisition
script downloads them from the official government publication service. Small
derived result extracts used in the reports are available in `data/public/`.

## Status

This repository is the public evidence and reproducibility layer. The five
reports and cross-report synthesis are owner-reviewed publication editions.
The website remains the main reader-facing product.

## Licensing

The official survey material is published under the Open Government Licence
v3.0 except where otherwise stated. See [NOTICE.md](NOTICE.md). A separate
reuse licence for the project's original code and written material has not yet
been selected.
