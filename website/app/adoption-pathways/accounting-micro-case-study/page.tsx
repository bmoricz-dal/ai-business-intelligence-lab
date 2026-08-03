import type { Metadata } from "next";
import { LandscapeStory, SiteFooter, SiteHeader } from "../../site-shell";
import { AdoptionWorkspace } from "./adoption-workspace";
import { ExperienceWorkspace } from "./experience-workspace";

const REPORT = "/reports/UK_Micro_Accounting_Practice_AI_Adoption_Worked_Case_2026.pdf";
const DATA = "/data/accounting_micro_ai_adoption_playbook_2026.csv";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/accounting";

export const metadata: Metadata = {
  title: "Accounting AI Experience Lab | DAL Data & AI Lab",
  description: "Take one fictional client through an AI-enabled bookkeeping, close, reporting and insight cycle.",
};

const commonSteps = [
  ["1", "Name accountability", "Owner, reviewer, operational lead and rollback authority."],
  ["2", "Map one workflow", "Inputs, systems, hand-offs, exceptions and judgement points."],
  ["3", "Measure four weeks", "Volume, time, review, corrections, exceptions and incidents."],
  ["4", "Classify data", "Permitted data, environment, access and professional consequence."],
  ["5", "Choose a method", "Use, integrate, automate, configure—or do not adopt."],
  ["6", "Pre-register gates", "Quality, total cost, risk and stop rules fixed before testing."],
];

const gates = [
  ["G0 Scope", "Workflow, owner, users and prohibited actions named", "Generic objective or unclear responsibility"],
  ["G1 Data", "Purpose, minimisation, supplier route and access documented", "Sensitive data enter an unapproved environment"],
  ["G2 Known cases", "Quality and failure behaviour pass the pre-registered rule", "Material error, unsupported answer or missing log"],
  ["G3 Shadow", "Quality maintained and exceptions reach reviewer", "Staff cannot explain or override output"],
  ["G4 Pilot", "Full cost, correction and incidents remain acceptable", "Benefit disappears after review or controls fail"],
  ["G5 Scale", "Segment, support, monitoring and rollback approved", "Material lock-in, drift or unresolved risk"],
];

export default function AccountingMicroCaseStudyPage() {
  return (
    <>
      <a className="skipLink" href="#case-main">Skip to the Accounting AI Experience Lab</a>
      <SiteHeader active="AI in practice" />
      <main id="case-main" className="microCasePage">
        <section className="microCaseHero">
          <div className="microCaseHeroMarker" aria-hidden="true"><span>PHASE 2B</span><span>7 PEOPLE</span><span>SECONDARY EVIDENCE</span></div>
          <div>
            <p className="kicker light">Accounting · AI in practice</p>
            <h1>See an AI-enabled accounting cycle at work.</h1>
            <p>Take one fictional client from source records and bookkeeping through reconciliation, management accounts, business insight and final quality control.</p>
            <div className="heroActions">
              <a className="primaryButton" href="#experience-lab">Start the test drive</a>
              <a className="textButton accountingTextButton" href="#adoption-planner">Plan your adoption</a>
            </div>
          </div>
          <aside><span>Interactive test drive</span><strong>See what adoption changes—and what it should not</strong><p>One synthetic practice, one fictional client and six connected accounting workstations.</p></aside>
          <div className="pageSectionNavigatorMount" />
        </section>

        <section className="microCaseBoundary" aria-label="Case boundaries">
          <div><strong>Synthetic accounting work</strong><span>realistic fixed scenarios without client data</span></div>
          <div><strong>Illustrative comparisons</strong><span>experience the mechanism—not promised ROI</span></div>
          <div><strong>Human quality control</strong><span>review, overrides, citations and safe stops remain visible</span></div>
          <div><strong>Browser-only experience</strong><span>no upload, live model or accounting-system connection</span></div>
        </section>

        <ExperienceWorkspace />

        <section className="microCaseProfile">
          <div className="sectionLead"><p className="kicker">The fictional firm</p><h2>Cedar Ledger Ltd: specific enough to test, fictional by design.</h2><p>The practice profile makes each operating decision visible. Any adopter should replace its assumptions with a measured local baseline.</p></div>
          <div className="microProfileGrid">
            <article><span>People</span><strong>7 payroll employees</strong><p>Owner-director, senior accountant, three accountants/bookkeepers, payroll specialist and administrator.</p></article>
            <article><span>Clients</span><strong>180 illustrative clients</strong><p>A scenario input—not a UK accounting-practice average.</p></article>
            <article><span>Initial problem</span><strong>Exceptions and close review</strong><p>A hypothesis to measure, not a pre-existing empirical result.</p></article>
            <article><span>Excluded</span><strong>Autonomous professional conclusions</strong><p>No unreviewed tax, audit, material posting or client-advice decisions.</p></article>
          </div>
        </section>

        <AdoptionWorkspace />

        <LandscapeStory
          variant="coast"
          src="/felixstowe-aerial-cc-by.jpg"
          alt="Aerial view along Felixstowe beach and the Suffolk coast"
          kicker="FROM TEST TO CONTROLLED ROUTE"
          title="A good pilot makes the boundary visible."
          description="The lab turns the accounting cycle into a navigable route: defined inputs, observable exceptions, accountable review and an explicit decision to proceed, revise or stop."
          credit="Felixstowe coast · John Fielding / CC BY 2.0"
          creditHref="https://commons.wikimedia.org/wiki/File:Felixstowe_Beach_aerial_image_-_Suffolk_UK_coast_(14871964066).jpg"
        />

        <section className="microFoundation" id="foundation">
          <div className="sectionLead"><p className="kicker">Common foundation</p><h2>Six decisions before any pilot.</h2><p>Governance is not a final checkpoint. It shapes scope, data, testing and accountability from the first design choice.</p></div>
          <ol>{commonSteps.map(([number, title, description]) => <li key={number}><span>{number}</span><div><strong>{title}</strong><p>{description}</p></div></li>)}</ol>
        </section>

        <section className="microSequence">
          <div className="sectionLead"><p className="kicker light">Worked sequence</p><h2>Twelve illustrative weeks from scope to scale decision.</h2></div>
          <div className="microSequenceBar" aria-label="Illustrative 12 week adoption sequence">
            <article><span>Weeks 1–5</span><strong>Scope and baseline</strong><p>Map, measure, classify and assure.</p></article>
            <article><span>Weeks 3–6</span><strong>Known-case tests</strong><p>Standalone and embedded tools.</p></article>
            <article><span>Weeks 7–8</span><strong>Shadow mode</strong><p>Current process remains authoritative.</p></article>
            <article><span>Weeks 9–10</span><strong>Controlled pilot</strong><p>Limited clients and draft-only automation.</p></article>
            <article><span>Weeks 11–12</span><strong>Decide</strong><p>Scale, revise, hold or stop.</p></article>
          </div>
        </section>

        <section className="microMeasurement">
          <div><p className="kicker">Measurement</p><h2>Efficiency without quality control is not a complete result.</h2><p>Measure preparation, review, correction, quality, incidents and capacity against the same workflow baseline.</p></div>
          <div className="microFormulaCards">
            <article><span>Total pilot cost</span><strong>licences + setup + training + review + correction + assurance + incidents</strong></article>
            <article><span>Net measured capacity value</span><strong>(baseline hours − pilot hours) × documented loaded cost − total pilot cost</strong></article>
          </div>
        </section>

        <section className="microGates">
          <div className="sectionLead"><p className="kicker light">Six decision gates</p><h2>Proceed, revise or stop.</h2></div>
          <div className="pathwayPageTable"><table><thead><tr><th>Gate</th><th>Proceed only when</th><th>Stop or revise when</th></tr></thead><tbody>{gates.map(([gate, proceed, stop]) => <tr key={gate}><th scope="row">{gate}</th><td>{proceed}</td><td>{stop}</td></tr>)}</tbody></table></div>
          <p>Thresholds are owner-set controls, not research findings. Zero tolerance applies to unauthorised disclosure and unapproved material postings.</p>
        </section>

        <section className="microDownloads">
          <div><p className="kicker light">Reuse the method</p><h2>Turn the demonstration into a controlled local test.</h2><p>Replace every scenario assumption with your workflow, people, data and baseline. Keep the same evidence, testing and decision discipline.</p></div>
          <div className="methodDownloads">
            <a href={REPORT}><span>15-page worked case</span><strong>Download PDF</strong></a>
            <a href={DATA}><span>Step-level project tracker</span><strong>Download CSV</strong></a>
            <a href={METHODS} rel="noreferrer" target="_blank"><span>Evidence trail</span><strong>View sources and methods</strong></a>
            <a href="/sectors/accounting/benefits"><span>Why this workflow</span><strong>Read the benefits evidence</strong></a>
          </div>
          <p className="benefitsDisclaimer">Evidence-informed fictional composite. This is not accounting, legal, tax, audit, data-protection or procurement advice.</p>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
