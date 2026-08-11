import type { Metadata } from "next";
import { LandscapeStory, SiteFooter, SiteHeader } from "../../../site-shell";

const DATA = "/data/construction_ai_adoption_journeys_2026.csv";
const REPORT = "/reports/UK_Construction_SMEs_AI_Adoption_Journeys_2026.pdf";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/construction";

export const metadata: Metadata = { title: "Construction AI Adoption Journeys, 2026", description: "Three evidence-bounded construction AI implementation journeys." };

const cases = [
  { label: "UK SME transfer case", title: "Cast Consultancy", status: "Provider-supported case", start: "A roughly 90-person consultancy needed to understand a new Gateway 2 workflow.", change: "A small group tested a tool-based learning approach and fed practical issues back to the provider.", lesson: "Tie upskilling to a live workflow, build confidence through use and keep feedback close to implementation.", boundary: "Qualitative capability outcome; not an audited productivity or compliance result." },
  { label: "Large-company change case", title: "ConstructionCo", status: "Self-reported case", start: "A previous system struggled after limited consultation; AI activity was fragmented.", change: "A cross-functional group used MoSCoW requirements and selected bounded document-review use cases.", lesson: "Start with user needs and governance, not product availability.", boundary: "Several-thousand-employee housebuilder; reported 60-to-15-minute legal review is not SME transfer evidence." },
  { label: "Research prototype", title: "Construction bid preparation model", status: "Two-case technical study", start: "Bid teams faced repeated requirement extraction, evidence retrieval and drafting work.", change: "A model linked extraction, retrieval and first-draft generation across sample tender material.", lesson: "Separate extraction accuracy from evidence matching, commercial challenge and human submission assurance.", boundary: "Prototype F1 is not tender win rate, business value or field reliability." },
];

export default function ConstructionJourneysPage() {
  return <>
    <a className="skipLink" href="#construction-journeys">Skip to adoption journeys</a><SiteHeader active="Sectors" />
    <main id="construction-journeys" className="constructionPage">
      <section className="constructionHero compact"><div><p className="kicker light">Construction AI Adoption Journeys</p><h1>Follow the workflow change—not the product announcement.</h1><p>Three different evidence types show how scope, people, controls and feedback shape implementation.</p></div><aside><span>Evidence boundary</span><strong>3</strong><p>cases kept separate by organisation, method and outcome type</p><small>No pooled ROI, vendor ranking or reconstructed success story.</small></aside></section>
      <section className="constructionEvidence"><div className="sectionLead"><p className="kicker">Shared comparison frame</p><h2>Problem → selection → pilot → adaptation → outcome</h2><p>Missing stages remain missing. A lesson observed in one organisation is not treated as a measured result in another.</p></div><div className="constructionJourneyGrid">{cases.map((item,index) => <article key={item.title}><header><span>{String(index+1).padStart(2,"0")} · {item.label}</span><h2>{item.title}</h2><strong>{item.status}</strong></header><dl><div><dt>Starting point</dt><dd>{item.start}</dd></div><div><dt>What changed</dt><dd>{item.change}</dd></div><div><dt>Transfer lesson</dt><dd>{item.lesson}</dd></div><div><dt>Boundary</dt><dd>{item.boundary}</dd></div></dl></article>)}</div></section>
      <section className="constructionSignals"><div><p className="kicker light">Cross-case synthesis</p><h2>Five lessons survive without overstating the evidence.</h2></div><ol className="constructionLessons"><li>Begin with one defined workflow and a named operational owner.</li><li>Include the people who do and review the work before selecting the tool.</li><li>Keep source traceability, exception handling and human override visible.</li><li>Measure correction and review effort alongside preparation time.</li><li>Transfer the implementation design—not another organisation&apos;s result.</li></ol></section>

      <LandscapeStory
        variant="highlands"
        src="/scottish-highlands-cc-by.jpg"
        alt="A broad view across the Scottish Highlands"
        kicker="IMPLEMENTATION TERRAIN"
        title="The useful lesson is the route—not another firm’s result."
        description="Across three different evidence types, progress depends on a defined problem, staff participation, tested controls and the willingness to adapt or stop when the first design does not hold."
        credit="Scottish Highlands · Gary Ullah / CC BY 2.0"
        creditHref="https://commons.wikimedia.org/wiki/File:Scottish_Highlands_(24045266327).jpg"
      />

      <section className="constructionNext"><div className="sectionLead"><p className="kicker">Next step</p><h2>Test the mechanism with synthetic tender data.</h2></div><div className="actionLinkGrid"><a href={REPORT}><span>Journey review</span><strong>Download PDF</strong></a><a href="/adoption-pathways/construction-tender-lab"><span>Interactive test drive</span><strong>Open the Construction Tender Lab</strong></a><a href={DATA}><span>Public case index</span><strong>Download CSV</strong></a><a href={METHODS} target="_blank" rel="noreferrer"><span>Research trail</span><strong>View protocol and sources</strong></a><a href="/sectors/construction/benefits"><span>Prior study</span><strong>Return to benefits &amp; system fit</strong></a></div></section>
      <section className="constructionMethods"><p className="constructionDisclaimer">Secondary evidence only. Not construction, legal, safety, procurement, regulatory or implementation advice.</p></section>
    </main><SiteFooter />
  </>;
}
