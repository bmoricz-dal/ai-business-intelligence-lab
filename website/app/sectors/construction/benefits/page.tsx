import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "../../../site-shell";

const DATA = "/data/construction_ai_benefits_system_fit_2026.csv";
const REPORT = "/reports/UK_Construction_SMEs_AI_Benefits_and_System_Fit_2026.pdf";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/construction";

export const metadata: Metadata = { title: "Construction AI Benefits and System Fit, 2026", description: "Evidence review of construction AI workflow fit and claim boundaries." };

const workflowFit = [
  ["Controlled deployment", "Tender requirement extraction, document classification, first-draft responses", "Approved documents, citations, version control and named reviewer"],
  ["Conditional deployment", "Scheduling support, risk prompts, contract review and programme coordination", "Specialist review, tested integrations, escalation and audit trail"],
  ["Do not delegate autonomously", "Safety decisions, regulatory conclusions, final pricing, commitments and method statements", "Accountability and professional judgement remain human"],
];

export default function ConstructionBenefitsPage() {
  return <>
    <a className="skipLink" href="#construction-benefits">Skip to benefits evidence</a><SiteHeader active="Sectors" />
    <main id="construction-benefits" className="constructionPage">
      <section className="constructionHero compact"><div><p className="kicker light">Construction · benefits and system fit</p><h1>The strongest near-term case is controlled document work—not autonomous construction.</h1><p>Tender and pre-construction workflows are bounded enough to test, but published signals do not establish UK SME ROI.</p></div><aside><span>Research prototype</span><strong>96.25%</strong><p>average requirement-extraction F1 reported in a two-case bid study</p><small>Prototype performance; not a business-outcome or field benchmark.</small></aside></section>

      <section className="constructionEvidence"><div className="sectionLead"><p className="kicker">Evidence verdict</p><h2>There is a plausible workflow case. The benefit magnitude remains unproven.</h2><p>RICS respondents perceived document management, scheduling and risk as significant opportunities. A research prototype reported high extraction performance. A large-company case reported faster legal review. These are different claims and are not pooled.</p></div><div className="constructionVerdictGrid"><article><span>Industry perception</span><strong>30%</strong><p>identified document management as a high-significance AI application in the global RICS survey.</p></article><article><span>Prototype result</span><strong>96.25% F1</strong><p>reported for requirement extraction; narrow technical accuracy, not full tender quality.</p></article><article><span>Self-reported case</span><strong>60 → 15 minutes</strong><p>legal document review at a large housebuilder; not independently evaluated or SME-specific.</p></article></div></section>

      <section className="constructionSignals"><div><p className="kicker light">System fit</p><h2>Set autonomy by consequence, verifiability and reversibility.</h2></div><div className="constructionTable"><table><thead><tr><th>Position</th><th>Candidate workflows</th><th>Minimum boundary</th></tr></thead><tbody>{workflowFit.map(([position,workflow,boundary]) => <tr key={position}><th scope="row">{position}</th><td>{workflow}</td><td>{boundary}</td></tr>)}</tbody></table></div></section>

      <section className="constructionNext"><div className="sectionLead"><p className="kicker">Practical implication</p><h2>Test total workflow performance, not draft speed alone.</h2><p>A local pilot should measure preparation, review, correction, omissions, traceability, incidents and final approval against the same baseline.</p></div><div className="actionLinkGrid"><a href={REPORT}><span>Evidence review</span><strong>Download PDF</strong></a><a href="/sectors/construction/adoption-journeys"><span>Implementation evidence</span><strong>Explore adoption journeys</strong></a><a href="/adoption-pathways/construction-tender-lab"><span>Browser-only demonstration</span><strong>Open the Tender Lab</strong></a><a href={DATA}><span>Claim-level evidence</span><strong>Download CSV</strong></a><a href={METHODS} target="_blank" rel="noreferrer"><span>Research trail</span><strong>View methods</strong></a></div></section>
      <section className="constructionMethods"><p className="constructionDisclaimer">No published source here establishes causal UK construction-SME productivity, profit, safety or compliance improvement.</p></section>
    </main><SiteFooter />
  </>;
}
