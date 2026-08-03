import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "../../../site-shell";

const REPORT = "/reports/UK_Accounting_SMEs_AI_Benefits_and_System_Fit_2026.pdf";
const DATA = "/data/accounting_ai_benefits_system_fit_2026.csv";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/accounting";

export const metadata: Metadata = {
  title: "UK Accounting SMEs: AI Benefits and System Fit, 2026",
  description:
    "A secondary-evidence review of where AI creates measurable value in accounting workflows and what the evidence cannot yet support.",
};

const workflowPositions = [
  {
    position: "Controlled deployment",
    workflows: "Transaction coding, reconciliations, close checklists, draft explanations and internal research",
    boundary: "Approved data, workflow rules, exception handling and documented human review",
  },
  {
    position: "Conditional deployment",
    workflows: "Client communications, advisory preparation, forecasting and contract or document review",
    boundary: "Qualified review, source checking, known-case testing and escalation",
  },
  {
    position: "Do not delegate autonomously",
    workflows: "Tax conclusions, audit conclusions, material postings and regulated or financial decisions",
    boundary: "Professional judgement and accountability remain with a qualified person",
  },
];

const evidenceLevels = [
  ["A", "Narrow experiment", "Classification accuracy improved on average, but non-consensus AI suggestions could increase error risk."],
  ["B", "Operational field evidence", "Integrated AI use was associated with faster reporting timeliness and less routine data-entry attention."],
  ["C", "Official UK self-report", "AI-using businesses frequently reported productivity and process benefits; this is not a measured causal effect."],
  ["D", "Guidance and workflow maps", "FRC and ICAEW evidence defines controls and plausible workflows, not benefit magnitude."],
];

export default function AccountingBenefitsPage() {
  return (
    <>
      <a className="skipLink" href="#benefits-main">Skip to benefits evidence</a>
      <SiteHeader active="Sectors" />

      <main id="benefits-main" className="benefitsPage">
        <section className="benefitsHero">
          <div className="benefitsHeroGrid" aria-hidden="true">
            <span>PHASE 2A</span><span>WORKFLOW / OUTCOME / CONTROL</span><span>SECONDARY DATA</span>
          </div>
          <div className="benefitsHeroCopy">
            <p className="kicker light">Accounting sector · benefits evidence</p>
            <h1>Where AI creates measurable value in accounting work</h1>
            <p>
              A system-fit review of bookkeeping, transaction processing and
              month-end close—showing what is supported, what transfers cautiously,
              and what remains unproven for UK accounting SMEs.
            </p>
            <div className="heroActions">
              <a className="primaryButton" href={REPORT}>Download the evidence review</a>
              <a className="textButton accountingTextButton" href="#verdict">Read the verdict</a>
            </div>
          </div>
          <aside className="benefitsHeroPanel" aria-label="Strongest operational result">
            <span>Strongest field signal</span>
            <strong>7.5–7.9</strong>
            <p>days faster on a reporting-timeliness proxy</p>
            <div><b>79</b><small>US private SME clients</small></div>
            <p className="panelCaveat">Peer-reviewed transfer evidence; not a UK accounting-SME benchmark.</p>
          </aside>
        </section>

        <section className="benefitsContext" aria-label="Research boundaries">
          <div><strong>Secondary only</strong><span>no project survey or primary collection</span></div>
          <div><strong>Workflow first</strong><span>outcomes tied to specific systems and tasks</span></div>
          <div><strong>Transfer evidence</strong><span>international results remain explicitly labelled</span></div>
          <div><strong>No ROI claim</strong><span>no vendor ranking or composite score</span></div>
        </section>

        <section className="benefitsVerdict" id="verdict">
          <div className="benefitsSectionIntro">
            <p className="kicker">Research verdict</p>
            <h2>The strongest case is controlled augmentation, not autonomous accounting.</h2>
            <p>
              Bookkeeping, transaction categorisation, reconciliation and close support
              have the clearest measurable signal. The observed system combines accounting
              data, workflow rules, confidence or exception handling and professional review.
            </p>
          </div>
          <div className="benefitsVerdictGrid">
            <article>
              <span>Supported</span>
              <h3>Faster reporting timeliness</h3>
              <p>About 7.5 to 7.9 days in robust alternative specifications from one peer-reviewed US field setting.</p>
            </article>
            <article>
              <span>Promising</span>
              <h3>Less routine work</h3>
              <p>Time shifted away from routine data entry, with positive client-capacity associations that vary by specification.</p>
            </article>
            <article>
              <span>Not established</span>
              <h3>UK SME ROI</h3>
              <p>No open source supports a causal UK accounting-SME productivity uplift, revenue effect or vendor comparison.</p>
            </article>
          </div>
        </section>

        <section className="benefitsEvidence" id="evidence">
          <div>
            <p className="kicker light">Evidence ladder</p>
            <h2>Different evidence supports different wording.</h2>
            <p>
              Operational associations, self-reported impacts and professional
              guidance are not treated as interchangeable proof.
            </p>
          </div>
          <div className="benefitsEvidenceRows">
            {evidenceLevels.map(([grade, label, description]) => (
              <article key={grade}>
                <b>{grade}</b>
                <div><strong>{label}</strong><p>{description}</p></div>
              </article>
            ))}
          </div>
        </section>

        <section className="benefitsHumanAI">
          <div className="benefitsSectionIntro">
            <p className="kicker">Human–AI performance</p>
            <h2>Benefits and errors coexist.</h2>
            <p>
              A framed experiment with professional accountants found that AI
              assistance improved classification accuracy on average. It also found
              that reliance on non-consensus AI recommendations could increase error risk.
            </p>
          </div>
          <div className="humanAIFlow" aria-label="Human AI control flow">
            <article><span>01</span><strong>AI suggestion</strong><p>Classification plus a confidence signal</p></article>
            <i aria-hidden="true">→</i>
            <article><span>02</span><strong>Exception route</strong><p>Low-confidence or unusual items are surfaced</p></article>
            <i aria-hidden="true">→</i>
            <article><span>03</span><strong>Professional review</strong><p>Accountant checks, overrides or escalates</p></article>
          </div>
        </section>

        <section className="benefitsUKContext">
          <div>
            <p className="kicker light">UK business context</p>
            <h2>Reported productivity is common; measured revenue change is not.</h2>
            <p>
              Official DSIT research asked 700 UK AI-using businesses about impact.
              These are broad-sector self-reports, not accounting-SME causal estimates.
            </p>
          </div>
          <div className="ukContextMetrics">
            <article><strong>75%</strong><span>reported improved workforce productivity</span></article>
            <article><strong>57%</strong><span>reported new or improved processes</span></article>
            <article><strong>77%</strong><span>reported no revenue change</span></article>
            <article><strong>10%</strong><span>reported no impact so far</span></article>
          </div>
        </section>

        <section className="benefitsPathway" id="system-fit">
          <div className="benefitsSectionIntro">
            <p className="kicker">System-fit pathway</p>
            <h2>Match autonomy to verifiability and consequence.</h2>
            <p>
              Tasks that are bounded, repeatable and reviewable are the strongest fit.
              Higher-stakes conclusions need stronger assurance and human accountability.
            </p>
          </div>
          <div className="benefitsPathwayTable">
            <table>
              <thead><tr><th>Position</th><th>Workflow examples</th><th>Minimum boundary</th></tr></thead>
              <tbody>
                {workflowPositions.map((row) => (
                  <tr key={row.position}>
                    <th scope="row">{row.position}</th>
                    <td>{row.workflows}</td>
                    <td>{row.boundary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="evidenceBoundary">
            Time saved is not the whole benefit. Correction, review, training,
            confidentiality and governance costs must remain inside the measurement boundary.
          </p>
        </section>

        <section className="benefitsMethods">
          <div>
            <p className="kicker light">Methods and openness</p>
            <h2>Every result keeps its population and claim limit.</h2>
            <p>
              The evidence review separates narrow experiments, operational field
              associations, official self-reports and professional guidance. No
              international effect size is converted into a UK SME estimate.
            </p>
          </div>
          <div className="methodDownloads">
            <a href={REPORT}><span>Evidence review</span><strong>Download PDF</strong></a>
            <a href={DATA}><span>Public evidence matrix</span><strong>Download CSV</strong></a>
            <a href={METHODS} rel="noreferrer" target="_blank"><span>Research trail</span><strong>View sources and methods</strong></a>
            <a href="/sectors/accounting"><span>Current-state baseline</span><strong>Return to AI adoption and readiness</strong></a>
          </div>
          <p className="benefitsDisclaimer">
            This is an evidence review, not accounting, legal, tax, audit, investment or procurement advice.
          </p>
        </section>
      </main>

      <SiteFooter />
    </>
  );
}

