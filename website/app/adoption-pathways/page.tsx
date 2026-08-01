import type { Metadata } from "next";
import { PATHWAY_ROWS } from "../research-data";
import { PageHero, SiteFooter, SiteHeader } from "../site-shell";

export const metadata: Metadata = {
  title: "Adoption Pathways | DAL Data & AI Lab",
  description: "How UK SMEs access, integrate, automate, build and govern AI.",
};

const pathways = [
  { id: "use", number: "01", title: "Use", summary: "Employees access ready-made or general-purpose AI for specific tasks.", signal: "The broadest and most visible entry point." },
  { id: "integration", number: "02", title: "Integrate", summary: "AI tools connect with recurring workflows and business systems.", signal: "Reported by roughly 27%-32% of AI-using SMEs." },
  { id: "automation", number: "03", title: "Automate", summary: "AI supports or executes repeatable decisions and process steps.", signal: "Automated decisions remain below 6% among AI-using SMEs." },
  { id: "build", number: "04", title: "Build", summary: "The business develops or trains AI using its own data and capability.", signal: "In-house development remains below 7% across SME groups." },
  { id: "governance", number: "05", title: "Govern", summary: "Policies, approved use, human review and accountability shape operations.", signal: "Policy or guidance rises with business size but is not universal." },
];

export default function AdoptionPathwaysPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to adoption pathways</a>
      <SiteHeader active="Adoption pathways" />
      <main className="multiPage" id="main">
        <PageHero
          kicker="Adoption pathways"
          marker="USE · INTEGRATE · AUTOMATE · BUILD · GOVERN"
          title="AI adoption is not one linear journey."
          introduction="Businesses can use, integrate, automate, build and govern AI in different combinations. These pathways describe operating choices—not mandatory maturity stages or a readiness score."
        />

        <section className="pageSection pathwayConcepts">
          <div className="sectionLead"><p className="kicker">Five pathways</p><h2>Different routes imply different operational demands.</h2></div>
          <div className="pathwayConceptGrid">
            {pathways.map((item) => (
              <article id={item.id} key={item.number}>
                <span>{item.number}</span><h3>{item.title}</h3><p>{item.summary}</p><strong>{item.signal}</strong>
              </article>
            ))}
          </div>
        </section>

        <section className="pageSection pathwayEvidence">
          <div className="sectionLead">
            <p className="kicker">Published estimates</p>
            <h2>Operational depth varies by measure and business size.</h2>
            <p>The first three rows describe businesses already using AI. Development or training describes all businesses.</p>
          </div>
          <div className="tableWrap pathwayPageTable">
            <table>
              <thead><tr><th scope="col">Indicator</th><th scope="col">Denominator</th><th scope="col">Micro</th><th scope="col">Small</th><th scope="col">Medium</th><th scope="col">Large*</th></tr></thead>
              <tbody>
                {PATHWAY_ROWS.map((row) => (
                  <tr key={row.indicator}><th scope="row">{row.indicator}</th><td>{row.denominator}</td><td>{row.micro}</td><td>{row.small}</td><td>{row.medium}</td><td>{row.large}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="tableNote">* Large businesses are a separate benchmark. Source: UK Business Data Survey 2026, Tables 43, 47, 48 and 50.</p>
        </section>

        <section className="pageSection pathwayInterpretation">
          <div>
            <p className="kicker light">Interpretation</p>
            <h2>Access expands before deeper operationalisation.</h2>
            <p>
              Reported use is broader than system integration, automated
              decision-making, in-house development and formal or informal
              guidance. That pattern does not prove that every firm should move
              through the pathways in sequence.
            </p>
          </div>
          <div className="interpretationCards">
            <article><span>Denominators</span><strong>All-business and AI-user estimates stay separate.</strong></article>
            <article><span>Sequence</span><strong>The indicators are not a conversion funnel.</strong></article>
            <article><span>Impact</span><strong>Prevalence does not establish benefit or performance.</strong></article>
          </div>
        </section>

        <section className="pageSection pathwayActions">
          <div className="sectionLead"><p className="kicker">Explore further</p><h2>Connect the pathways to the reports.</h2></div>
          <div className="actionLinkGrid">
            <a href="/ai-in-business"><span>General evidence</span><strong>See all five reports</strong></a>
            <a href="/sectors/accounting"><span>Sector application</span><strong>Accounting AI readiness</strong></a>
            <a href="/methods"><span>Evidence controls</span><strong>Methods and limitations</strong></a>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
