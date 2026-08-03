import type { Metadata } from "next";
import { PATHWAY_ROWS } from "../research-data";
import { PageHero, SiteFooter, SiteHeader } from "../site-shell";

export const metadata: Metadata = {
  title: "AI in Practice | DAL Data & AI Lab",
  description: "How UK SMEs access, integrate, automate, build and govern AI.",
};

const pathways = [
  { id: "use", number: "01", title: "Use", summary: "Employees access ready-made or general-purpose AI for specific tasks.", signal: "The broadest and most visible entry point." },
  { id: "integration", number: "02", title: "Integrate", summary: "AI tools connect with recurring workflows and business systems.", signal: "Reported by roughly 27%-32% of AI-using SMEs." },
  { id: "automation", number: "03", title: "Automate", summary: "AI supports or executes repeatable decisions and process steps.", signal: "Automated decisions remain below 6% among AI-using SMEs." },
  { id: "build", number: "04", title: "Build", summary: "The business develops or trains AI using its own data and capability.", signal: "In-house development remains below 7% across SME groups." },
  { id: "governance", number: "05", title: "Govern", summary: "Policies, approved use, human review and accountability shape operations.", signal: "Policy or guidance rises with business size but is not universal." },
];

const operatingApproaches = [
  {
    label: "Use",
    title: "Controlled task assistance",
    description: "A person uses an approved standalone AI tool for a bounded task such as research, summarisation or a first draft.",
    example: "The employee selects the task and sources, checks the output and remains responsible for the result.",
    control: "Approved tool, permitted-data rule and human review.",
  },
  {
    label: "Integrate",
    title: "AI inside an existing system",
    description: "AI suggestions and exception signals appear inside software already used to run a recurring business workflow.",
    example: "Routine items can be prioritised or proposed while unusual cases remain visible to an operator.",
    control: "Assured data flow, access, logging, override and exit route.",
  },
  {
    label: "Automate",
    title: "Bounded workflow execution",
    description: "AI or rules prepare or complete defined process steps rather than merely producing an answer for a user.",
    example: "A trigger can create a task or draft an action, but consequential external steps retain an approval gate.",
    control: "Failure tests, approval, monitoring, pause and rollback.",
  },
  {
    label: "Configure",
    title: "Approved organisational knowledge",
    description: "A general system is configured to retrieve from approved internal procedures, templates or other controlled material.",
    example: "Answers point back to the authorised source and escalate when evidence is missing or conflicting.",
    control: "Source ownership, access, citations, expiry and no-answer rules.",
  },
];

export default function AdoptionPathwaysPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to AI in practice</a>
      <SiteHeader active="AI in practice" />
      <main className="multiPage" id="main">
        <PageHero
          kicker="AI in practice"
          marker="USE · INTEGRATE · AUTOMATE · BUILD · GOVERN"
          title="AI adoption is a portfolio of operating choices—not a maturity ladder."
          introduction="Use, integration, automation, internal build and governance can advance in different combinations. The practical question is which workflow to redesign, under what controls, and how to know whether it works."
        />

        <section className="systemSignalRail" aria-label="AI adoption pathway signals">
          <span><b>01</b> USE</span><i /><span><b>02</b> INTEGRATE</span><i /><span><b>03</b> AUTOMATE</span><i /><span><b>04</b> BUILD</span><i /><span><b>05</b> GOVERN</span>
        </section>

        <section className="pageSection pathwayConcepts" id="background">
          <div className="sectionLead"><p className="kicker">Five operating choices</p><h2>The deeper the workflow change, the greater the control demand.</h2></div>
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
            <h2>Use is broad. Deeper operationalisation remains selective.</h2>
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
            <h2>Adoption activity does not automatically become operating capability.</h2>
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

        <section className="pageSection adoptionMechanisms" id="operating-approaches">
          <div className="sectionLead">
            <p className="kicker">From pathway to operation</p>
            <h2>Four ways AI enters a workflow—and the controls each one needs.</h2>
            <p>These cross-sector patterns explain the operating mechanism. The Accounting Experience Lab then makes the change visible inside a complete accounting cycle.</p>
          </div>
          <div className="adoptionMechanismGrid">
            {operatingApproaches.map((approach, index) => (
              <article key={approach.label}>
                <div><span>{String(index + 1).padStart(2, "0")}</span><b>{approach.label}</b></div>
                <h3>{approach.title}</h3>
                <p>{approach.description}</p>
                <dl>
                  <div><dt>In operation</dt><dd>{approach.example}</dd></div>
                  <div><dt>Minimum control</dt><dd>{approach.control}</dd></div>
                </dl>
              </article>
            ))}
          </div>
          <div className="governanceBand">
            <span>05 · Govern</span>
            <div><h3>A control layer—not a final stage.</h3><p>Accountability, approved data, testing, human review, incident handling and monitoring surround every approach. A business can also decide that the evidence, capability or risk case does not justify adoption.</p></div>
          </div>
        </section>

        <section className="pageSection pathwayActions">
          <div className="sectionLead"><p className="kicker">Next decision</p><h2>Move from the operating model to the evidence and test drive.</h2></div>
          <div className="actionLinkGrid">
            <a href="/ai-in-business"><span>General evidence</span><strong>See all five reports</strong></a>
            <a href="/sectors/accounting"><span>Sector application</span><strong>Accounting AI readiness</strong></a>
            <a href="/adoption-pathways/accounting-micro-case-study"><span>Interactive test drive</span><strong>Open the Accounting AI Experience Lab</strong></a>
            <a href="/methods"><span>Evidence controls</span><strong>Methods and limitations</strong></a>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
