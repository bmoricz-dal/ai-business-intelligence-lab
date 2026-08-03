import type { Metadata } from "next";
import { JourneyExplorer } from "../../../intelligence-ui";
import { SiteFooter, SiteHeader } from "../../../site-shell";

const DATA = "/data/accounting_ai_adoption_journeys_2026.csv";
const METHODS = "https://github.com/bmoricz-dal/ai-business-intelligence-lab/tree/main/docs/sectors/accounting";
const LAB = "/adoption-pathways/accounting-micro-case-study";

export const metadata: Metadata = {
  title: "Accounting AI Adoption Journeys, 2026 | DAL Data & AI Lab",
  description:
    "A secondary-evidence study of how accounting practices implemented AI, encountered setbacks, adapted controls and changed work.",
};

const lifecycle = [
  ["01", "Problem", "Define the operational constraint—not a generic ambition to ‘use AI’."],
  ["02", "Prepare", "Map the workflow, data, baseline and accountability before selection."],
  ["03", "Pilot", "Test a bounded task with known cases, exceptions and human review."],
  ["04", "Adapt", "Respond to errors, staff or client friction and integration constraints."],
  ["05", "Measure", "Keep quality, corrections, review and training inside the outcome boundary."],
  ["06", "Scale conditionally", "Extend only when the evidence and controls survive real workflow use."],
];

const sources = {
  jar: "https://onlinelibrary.wiley.com/doi/10.1111/1475-679x.70052",
  lya: "https://www.icaew.com/insights/viewpoints-on-the-news/2025/dec-2025/three-use-cases-for-ai",
  audit: "https://link.springer.com/article/10.1007/s11142-022-09697-x",
  multicase: "https://www.sciencedirect.com/science/article/pii/S0040162524000477",
  challenges: "https://www.sciencedirect.com/science/article/pii/S1467089525000107",
  icaew: "https://www.icaew.com/-/media/corporate/files/regulations/practice-assurance/practice-assurance-monitoring-2025.ashx",
  alfa: "https://www.accaglobal.com/content/dam/ACCA_Global/professional-insights/passionate-practitioner/passionate-practitioner-full-report.pdf",
  hudson: "https://www.icaew.com/technical/technology/webinars-and-publications/tech-essentials-guides/case-study-automating-my-practice",
};

export default function AccountingAdoptionJourneysPage() {
  return (
    <>
      <a className="skipLink" href="#journeys-main">Skip to adoption journeys</a>
      <SiteHeader active="Sectors" />

      <main id="journeys-main" className="journeysPage">
        <section className="journeysHero">
          <div className="journeysHeroGrid" aria-hidden="true">
            <span>PART 03</span><span>PROBLEM → PILOT → ADAPT → SCALE</span><span>SECONDARY EVIDENCE</span>
          </div>
          <div className="journeysHeroCopy">
            <p className="kicker light">Accounting sector · implementation evidence</p>
            <h1>AI adoption becomes real when the workflow changes.</h1>
            <p>
              Published cases show how firms selected systems, piloted use,
              encountered setbacks, adapted controls and changed work—with
              experimental, associated and self-reported outcomes kept separate.
            </p>
            <div className="heroActions">
              <a className="primaryButton" href="#cases">Explore the cases</a>
              <a className="textButton accountingTextButton" href={DATA}>Download the case index</a>
            </div>
          </div>
          <aside className="journeysHeroPanel" aria-label="Evidence boundary">
            <span>Evidence boundary</span>
            <strong>3</strong>
            <p>core accounting-practice evidence bundles</p>
            <div><b>2</b><small>historical change comparators</small></div>
            <p className="panelCaveat">No DAL survey. No blended firm history. No pooled ROI or vendor ranking.</p>
          </aside>
        </section>

        <section className="journeysBoundary" aria-label="What the study can show">
          <article><strong>Can show</strong><span>implementation sequences, recurring setbacks, controls and bounded outcomes</span></article>
          <article><strong>Cannot show</strong><span>a typical UK micro-practice journey or guaranteed benefit</span></article>
          <article><strong>Outcome labels</strong><span>experimental · associated · self-reported · comparator-only</span></article>
        </section>

        <JourneyExplorer />

        <section className="journeysLifecycle">
          <div className="journeysSectionIntro">
            <p className="kicker">One comparison frame</p>
            <h2>Follow the workflow change—not the product announcement.</h2>
            <p>Every case is read against the same lifecycle. Missing steps stay missing; they are not reconstructed from another firm.</p>
          </div>
          <ol className="journeySteps">
            {lifecycle.map(([number, title, text]) => (
              <li key={number}><span>{number}</span><div><strong>{title}</strong><p>{text}</p></div></li>
            ))}
          </ol>
        </section>

        <section className="journeysCases" id="cases">
          <div className="journeysSectionIntro lightIntro">
            <p className="kicker light">Core accounting-practice evidence</p>
            <h2>Three evidence bundles show where implementation succeeds—and strains.</h2>
            <p>Evidence strength travels with each finding. A recurring mechanism does not turn a management estimate into an independently measured result.</p>
          </div>

          <article className="journeyCase featuredCase">
            <header>
              <div><span className="caseNumber">01</span><p>Peer-reviewed field study · United States · anonymised platform</p><h3>Integrated AI bookkeeping platform</h3></div>
              <strong className="gradeBadge">Grade A / B</strong>
            </header>
            <div className="caseJourneyGrid">
              <div><span>Starting point</span><p>A multi-stage bookkeeping process covering data collection, processing, categorisation, review, reconciliation and reporting.</p></div>
              <div><span>What changed</span><p>AI was integrated with standard accounting software, confidence cues, approval queues and accountant review rather than used as a detached chatbot.</p></div>
              <div><span>Setback</span><p>Some incorrect suggestions could propagate when accountants relied on the model without enough scrutiny.</p></div>
              <div><span>Adaptation</span><p>Confidence signals, review dashboards and human approval concentrated attention on uncertainty and exceptions.</p></div>
            </div>
            <div className="caseOutcomes">
              <div><span>Experimental</span><strong>+17.5 percentage points</strong><p>classification accuracy in a framed test with 99 accountants and 43 transactions</p></div>
              <div><span>Associated</span><strong>≈12%</strong><p>more ledger granularity among 79 private SME clients</p></div>
              <div><span>Associated</span><strong>≈7.5 days</strong><p>earlier reporting; adoption was not random in the operational sample</p></div>
            </div>
            <footer><p><b>Work changed:</b> attention moved away from routine bookkeeping toward quality assurance, advisory work and client communication.</p><a href={sources.jar} rel="noreferrer" target="_blank">Read the peer-reviewed study ↗</a></footer>
          </article>

          <article className="journeyCase">
            <header>
              <div><span className="caseNumber">02</span><p>Named practice case · United Kingdom</p><h3>Love Your Accountants</h3></div>
              <strong className="gradeBadge selfReport">Grade E</strong>
            </header>
            <div className="caseJourneyGrid">
              <div><span>Starting point</span><p>The firm wanted to streamline administration and introduce workplace AI gradually.</p></div>
              <div><span>Selection</span><p>Existing supplier arrangements influenced choice. Gemini supported sensitive-data applications; ChatGPT was retained for brainstorming.</p></div>
              <div><span>Implementation</span><p>An external developer built scanned-mail routing; Veryfi/Xero supported receipts and Syft supported management-account work.</p></div>
              <div><span>Constraint and control</span><p>Receipt processing was not yet used to full potential. The firm limited AI to factual or sense-checkable tasks and required references.</p></div>
            </div>
            <div className="reportedOutcome"><span>Self-reported outcome</span><strong>10–15 hours per week</strong><p>manager-estimated saving on scanned-mail administration. The source does not report an independent baseline or evaluation.</p></div>
            <footer><p><b>Transfer lesson:</b> selection, data arrangements, external implementation support and task-level controls formed part of the adoption decision.</p><a href={sources.lya} rel="noreferrer" target="_blank">Read the ICAEW case ↗</a></footer>
          </article>

          <article className="journeyCase">
            <header>
              <div><span className="caseNumber">03</span><p>Multi-source synthesis · audit firms · not one company</p><h3>Audit-firm implementation pattern</h3></div>
              <strong className="gradeBadge">Grade B / C</strong>
            </header>
            <div className="caseJourneyGrid">
              <div><span>Preparation</span><p>Readiness, communication, internal linking roles, regulation and client acceptance affected adoption trajectories.</p></div>
              <div><span>Rollout</span><p>Larger firms commonly used centralised programmes and a mix of internally developed and external tools.</p></div>
              <div><span>Setbacks</span><p>Training and scaling remained difficult. Explainability, bias, privacy, reliability, overreliance and limited guidance constrained complex use.</p></div>
              <div><span>Longer-run change</span><p>Large-firm quality, fee and staffing measures were associated with AI intensity after several years; the evidence does not establish a UK SME causal effect.</p></div>
            </div>
            <footer className="multiSourceFooter"><p><b>Evidence boundary:</b> this is a transparent cross-study pattern, not a reconstructed firm history.</p><div><a href={sources.audit} rel="noreferrer" target="_blank">Operational study ↗</a><a href={sources.multicase} rel="noreferrer" target="_blank">Multiple cases ↗</a><a href={sources.challenges} rel="noreferrer" target="_blank">Audit challenges ↗</a></div></footer>
          </article>
        </section>

        <section className="journeysComparators">
          <div className="journeysSectionIntro">
            <p className="kicker">Change-management comparators</p>
            <h2>Earlier digital change reveals implementation patterns—not AI outcomes.</h2>
            <p>These cases add detail about stalled change, staged onboarding and service redesign. They do not prove an AI benefit.</p>
          </div>
          <div className="comparatorGrid">
            <article><span>Historical comparator · Netherlands</span><h3>Alfa Accountants / Beta</h3><p>An earlier internal initiative stalled. The response was a separate younger team, a fictional practice for software selection, interested clients first and gradual scaling.</p><strong>Change seen</strong><p>More regular insight and client contact, smoother peaks and recruitment that valued IT and people skills.</p><a href={sources.alfa} rel="noreferrer" target="_blank">Open ACCA case ↗</a></article>
            <article><span>Historical micro-practice comparator · UK</span><h3>Hudson Accountants</h3><p>A practice growing from one to eight staff adopted cloud and automation tools incrementally and found that some tools did not make economic sense for smaller clients.</p><strong>Change seen</strong><p>A move toward fixed-fee bookkeeping, monthly information, management accounts and advisory work.</p><a href={sources.hudson} rel="noreferrer" target="_blank">Open ICAEW case ↗</a></article>
          </div>
        </section>

        <section className="journeysSynthesis">
          <div>
            <p className="kicker light">Cross-case synthesis</p>
            <h2>Five implementation lessons survive across the evidence.</h2>
          </div>
          <ol>
            <li><span>01</span><p><strong>Begin with a defined workflow and data foundation.</strong> Tool access alone is not the implementation.</p></li>
            <li><span>02</span><p><strong>Integration and change management are harder than initial selection.</strong> Training, staff behaviour, client readiness and workflow fit shape scale.</p></li>
            <li><span>03</span><p><strong>Human review moves; it does not disappear.</strong> Confidence checks, exceptions and final professional accountability become central.</p></li>
            <li><span>04</span><p><strong>Benefits and errors coexist.</strong> Quality, correction and review must be measured alongside time or capacity.</p></li>
            <li><span>05</span><p><strong>Outcomes take different evidential forms.</strong> One narrow experiment cannot validate every workflow; self-reported savings remain self-reported.</p></li>
          </ol>
        </section>

        <section className="journeysUKTransfer">
          <div className="journeysSectionIntro">
            <p className="kicker">For a UK accounting SME</p>
            <h2>Transfer the design principles—not another firm&apos;s ROI.</h2>
          </div>
          <div className="transferTableWrap">
            <table>
              <thead><tr><th>More transferable</th><th>Needs local testing</th><th>Not transferable as a claim</th></tr></thead>
              <tbody><tr><td>Bounded workflow, known-case testing, confidence cues, exception review, staged scaling</td><td>Staff capacity, client process, integrations, data arrangements, baseline volume and review cost</td><td>Published effect sizes, staffing outcomes, vendor performance or savings from another firm</td></tr></tbody>
            </table>
          </div>
        </section>

        <section className="journeysMethods">
          <div>
            <p className="kicker light">Methods and next step</p>
            <h2>Trace the evidence. Then test-drive the workflow.</h2>
            <p>The open research package includes the protocol, graded source register, claim-level evidence matrix, public case index and explicit evidence gaps.</p>
          </div>
          <div className="methodDownloads">
            <a href={DATA}><span>Public case index</span><strong>Download CSV</strong></a>
            <a href={METHODS} rel="noreferrer" target="_blank"><span>Research trail</span><strong>View protocol and sources</strong></a>
            <a href={LAB}><span>Practical demonstration</span><strong>Open the Accounting AI Experience Lab</strong></a>
            <a href="/sectors/accounting/benefits"><span>Prior study</span><strong>Return to benefits and system fit</strong></a>
          </div>
          <p className="journeysDisclaimer">Secondary evidence review only. Not accounting, tax, audit, legal, implementation or procurement advice. Historical and finance-function examples are not presented as accounting-practice AI outcomes.</p>
        </section>
      </main>

      <SiteFooter />
    </>
  );
}
