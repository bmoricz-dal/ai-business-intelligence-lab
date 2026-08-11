import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "../../site-shell";
import { TenderWorkspace } from "./tender-workspace";

const DATA = "/data/construction_tender_ai_adoption_playbook_2026.csv";
const REPORT = "/reports/UK_Construction_SME_AI_Tender_Worked_Case_2026.pdf";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/construction";

export const metadata: Metadata = { title: "Construction Tender Lab | DAL Data & AI Lab", description: "A browser-only synthetic tender workflow for testing controlled AI adoption." };

const gates = [
  ["G0 Scope", "Bid decision, owner and prohibited actions named", "Generic objective or unclear accountability"],
  ["G1 Data", "Approved documents, access and retention defined", "Client or sensitive data enters an unapproved tool"],
  ["G2 Known cases", "Extraction and retrieval pass pre-set tests", "Material omission, invented requirement or broken citation"],
  ["G3 Shadow", "Current process remains authoritative", "Users cannot explain or override output"],
  ["G4 Pilot", "Quality, review and total cost stay acceptable", "Draft speed disappears after correction or assurance"],
  ["G5 Scale", "Monitoring, support and rollback are approved", "Unresolved delivery, safety, commercial or lock-in risk"],
];

export default function ConstructionTenderLabPage() {
  return <>
    <a className="skipLink" href="#construction-lab-main">Skip to the Construction Tender Lab</a><SiteHeader active="AI in practice" />
    <main id="construction-lab-main" className="constructionPage">
      <section className="constructionHero"><div><p className="kicker light">Construction · AI in practice</p><h1>Test a tender workflow without using a real bid.</h1><p>Move a fictional community-centre refurbishment through six controlled workstations—from opportunity gate to human submission assurance.</p><div className="heroActions"><a className="primaryButton" href="#tender-lab">Start the test drive</a><a className="textButton accountingTextButton" href="#pilot-gates">Review the pilot gates</a></div></div><aside><span>Browser-only experience</span><strong>6</strong><p>connected tender workstations</p><small>No upload, live model, client data or construction-system connection.</small></aside></section>
      <section className="constructionContext"><article><strong>Synthetic work</strong><span>fixed fictional scenario</span><small>safe to explore</small></article><article><strong>Source linked</strong><span>clauses and evidence stay visible</span><small>gaps are not hidden</small></article><article><strong>Human controlled</strong><span>sign-off remains accountable</span><small>no autonomous submission</small></article><article><strong>No promised ROI</strong><span>local baseline required</span><small>quality and cost measured together</small></article></section>
      <TenderWorkspace />
      <section className="constructionEvidence" id="pilot-gates"><div className="sectionLead"><p className="kicker">Six decision gates</p><h2>Proceed, revise, hold or stop.</h2><p>Thresholds are owner-set controls, not research findings.</p></div><div className="constructionTable light"><table><thead><tr><th>Gate</th><th>Proceed only when</th><th>Stop or revise when</th></tr></thead><tbody>{gates.map(([gate,proceed,stop]) => <tr key={gate}><th scope="row">{gate}</th><td>{proceed}</td><td>{stop}</td></tr>)}</tbody></table></div></section>
      <section className="constructionNext"><div className="sectionLead"><p className="kicker">Reuse the method</p><h2>Turn the demonstration into a controlled local test.</h2></div><div className="actionLinkGrid"><a href={REPORT}><span>Worked case</span><strong>Download PDF</strong></a><a href={DATA}><span>Step-level playbook</span><strong>Download CSV</strong></a><a href={METHODS} target="_blank" rel="noreferrer"><span>Evidence trail</span><strong>View sources and methods</strong></a><a href="/sectors/construction/benefits"><span>Why this workflow</span><strong>Read benefits &amp; system fit</strong></a><a href="/sectors/construction/adoption-journeys"><span>How others implemented</span><strong>Read adoption journeys</strong></a></div></section>
      <section className="constructionMethods"><p className="constructionDisclaimer">Evidence-informed fictional composite. Not construction, legal, safety, regulatory, procurement or investment advice.</p></section>
    </main><SiteFooter />
  </>;
}
