export const REPORTS = [
  {
    number: "01",
    theme: "AI use",
    title: "AI Use by Business Size",
    finding: "Reported use rises from 37.4% of micro businesses to 57.1% of medium businesses.",
    denominator: "All UK businesses in each published size group",
    href: "/reports/SME_Report_01_AI_Use_by_Business_Size.pdf",
  },
  {
    number: "02",
    theme: "Integration",
    title: "AI Adoption and System Integration",
    finding: "Among AI users, SME system-integration estimates range from 26.9% to 31.5%.",
    denominator: "UK businesses already reporting AI use",
    href: "/reports/SME_Report_02_AI_Adoption_and_System_Integration_by_Size.pdf",
  },
  {
    number: "03",
    theme: "Governance",
    title: "AI Governance by Business Size",
    finding: "20.1% of micro AI users report formal or informal policy or guidance.",
    denominator: "UK businesses already reporting AI use",
    href: "/reports/SME_Report_03_AI_Governance_by_Business_Size.pdf",
  },
  {
    number: "04",
    theme: "Use cases",
    title: "How UK Businesses Use AI",
    finding: "Research is the leading listed use case in every published size group.",
    denominator: "All UK businesses in each published size group",
    href: "/reports/SME_Report_04_How_UK_Businesses_Use_AI.pdf",
  },
  {
    number: "05",
    theme: "Pathways",
    title: "Operational AI Adoption Pathways",
    finding: "Integration and guidance are more common than automated decisions or in-house development.",
    denominator: "All-business and AI-user measures shown separately",
    href: "/reports/SME_Report_05_Operational_AI_Adoption_Pathways.pdf",
  },
];

export const SYNTHESIS = {
  href: "/reports/SME_Cross_Report_Synthesis_AI_Adoption_and_Operationalisation.pdf",
  title: "AI Adoption and Operationalisation",
};

export const ACCOUNTING_REPORT =
  "/reports/UK_Accounting_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf";

export const METHODS_GUIDE =
  "https://github.com/bmoricz-dal/ai-business-intelligence-lab/blob/main/publications/AI_Business_Intelligence_Lab_Data_and_Methods_Guide.pdf";

export const TECHNICAL_APPENDIX =
  "https://github.com/bmoricz-dal/ai-business-intelligence-lab/blob/main/publications/AI_Business_Intelligence_Lab_Technical_Reproducibility_Appendix.pdf";

export const PATHWAY_ROWS = [
  { indicator: "System integration", denominator: "AI users", micro: "26.9%", small: "31.5%", medium: "30.9%", large: "57.4%" },
  { indicator: "Automated decision-making", denominator: "AI users", micro: "5.3%", small: "3.4%", medium: "4.9%", large: "8.4%" },
  { indicator: "AI policy or guidance", denominator: "AI users", micro: "20.1%", small: "29.0%", medium: "36.8%", large: "67.7%" },
  { indicator: "In-house development or training", denominator: "All businesses", micro: "3.3%", small: "3.6%", medium: "6.5%", large: "10.5%" },
];
