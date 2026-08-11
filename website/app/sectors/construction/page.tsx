import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "../../site-shell";

const DATA = "/data/construction_ai_readiness_2026.csv";
const REPORT = "/reports/UK_Construction_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/construction";

export const metadata: Metadata = {
  title: "UK Construction SMEs: AI Adoption and Operational Readiness, 2026",
  description: "Official and industry evidence on AI adoption and operational readiness among UK construction SMEs.",
};

const dimensions = [
  ["01", "AI use", "21.5% reported any listed AI use in the broad construction sector estimate.", "All business sizes; not an SME-only rate"],
  ["02", "Integration", "14.0% of construction AI users reported integration with applications or systems.", "Approximate base 100; wide uncertainty"],
  ["03", "Governance", "3.1% of construction AI users reported a policy or guidance for AI use.", "Estimate is imprecise and compatible with zero"],
  ["04", "Use cases", "Tender preparation, document management, scheduling and coordination are visible priorities.", "Signals come from different evidence types"],
  ["05", "Pathways", "The strongest next step is a bounded, reviewable workflow—not autonomous delivery.", "Local baseline and controls still required"],
];

export default function ConstructionSectorPage() {
  return <>
    <a className="skipLink" href="#construction-main">Skip to construction insights</a>
    <SiteHeader active="Sectors" />
    <main id="construction-main" className="constructionPage">
      <section className="constructionHero">
        <div>
          <p className="kicker light">Construction sector research · 2026</p>
          <h1>AI experimentation is visible. Operating controls are not keeping pace.</h1>
          <p>A five-dimension view of adoption, integration, governance and practical workflow fit for UK construction SMEs.</p>
          <div className="heroActions"><a className="primaryButton" href={REPORT}>Download the report</a><a className="textButton accountingTextButton" href="#evidence">Explore the evidence</a></div>
        </div>
        <aside><span>Registered business frame</span><strong>384,525</strong><p>registered construction SMEs, March 2025</p><small>VAT/PAYE businesses in SIC F with 0–249 employees; excludes unregistered firms.</small></aside>
      </section>

      <section className="constructionContext" aria-label="Headline evidence">
        <article><strong>21.5%</strong><span>any listed AI use</span><small>95% CI 14.2%–28.8%; base ≈330</small></article>
        <article><strong>14.0%</strong><span>integration among AI users</span><small>95% CI 1.9%–26.2%; base ≈100</small></article>
        <article><strong>3.1%</strong><span>policy or guidance among AI users</span><small>95% CI 0%–9.2%; base ≈100</small></article>
        <article><strong>Secondary only</strong><span>no DAL survey</span><small>no causal or ROI claim</small></article>
      </section>

      <section className="constructionEvidence" id="evidence">
        <div className="sectionLead"><p className="kicker">Evidence-led answer</p><h2>Construction combines large SME reach with a measurable readiness gap.</h2><p>The official survey can isolate construction, but not construction SMEs by size. Each estimate therefore keeps its denominator, uncertainty and transfer boundary.</p></div>
        <div className="constructionDimensionGrid">{dimensions.map(([number,title,text,note]) => <article key={number}><span>{number}</span><h3>{title}</h3><p>{text}</p><small>{note}</small></article>)}</div>
      </section>

      <section className="constructionSignals">
        <div><p className="kicker light">Direct industry context</p><h2>Most firms in the RICS survey were still before regular operational use.</h2><p>The global 2025 RICS survey is not SME-only and is not a UK prevalence benchmark. It adds industry implementation context.</p></div>
        <div className="constructionSignalCards"><article><strong>45%</strong><span>reported no AI implementation</span></article><article><strong>34%</strong><span>reported early pilots</span></article><article><strong>&lt;12%</strong><span>reported regular use in specific processes</span></article><article><strong>&lt;1%</strong><span>reported organisation-wide use</span></article></div>
      </section>

      <section className="constructionNext">
        <div className="sectionLead"><p className="kicker">Connected programme</p><h2>Move from the readiness signal to the workflow evidence.</h2></div>
        <div className="actionLinkGrid"><a href="/sectors/construction/benefits"><span>Evidence review</span><strong>Benefits &amp; system fit</strong></a><a href="/sectors/construction/adoption-journeys"><span>Implementation evidence</span><strong>Adoption journeys</strong></a><a href="/adoption-pathways/construction-tender-lab"><span>Synthetic test drive</span><strong>Construction Tender Lab</strong></a><a href={DATA}><span>Open data</span><strong>Download readiness CSV</strong></a></div>
      </section>

      <section className="constructionMethods"><div><p className="kicker light">Methods and limits</p><h2>Decision-ready means keeping the evidence boundary visible.</h2><p>ONS provides the registered SME population frame. DSIT supplies official sector estimates. RICS and implementation cases add workflow context. None establishes UK construction-SME ROI.</p></div><div className="methodDownloads"><a href={REPORT}><span>Final report</span><strong>Download PDF</strong></a><a href={DATA}><span>Public evidence</span><strong>Download CSV</strong></a><a href={METHODS} target="_blank" rel="noreferrer"><span>Source trail</span><strong>View methods on GitHub</strong></a></div><p className="constructionDisclaimer">Descriptive secondary research only; not construction, safety, legal, regulatory, procurement or investment advice.</p></section>
    </main>
    <SiteFooter />
  </>;
}
