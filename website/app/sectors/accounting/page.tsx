import type { Metadata } from "next";
import { ReadinessConsole } from "../../intelligence-ui";
import { LandscapeStory, SignalScene, SiteFooter, SiteHeader } from "../../site-shell";

const REPORT = "/reports/UK_Accounting_SMEs_AI_Adoption_and_Operational_Readiness_2026.pdf";
const DATA = "/data/accounting_ai_readiness_2026.csv";
const BENEFITS_REPORT = "/sectors/accounting/benefits";
const REPOSITORY = "https://github.com/bmoricz-dal/ai-business-intelligence-lab";

export const metadata: Metadata = {
  title: "UK Accounting SMEs: AI Adoption and Operational Readiness, 2026",
  description:
    "Secondary-data research on the current extent, type and operational depth of AI adoption among UK accounting SMEs.",
};

const adoptionSignals = [
  {
    label: "Adopted AI",
    value: 26,
    display: "26%",
    source: "UK accounting practices, April 2024",
    role: "direct",
  },
  {
    label: "Piloting or adopted",
    value: 54,
    display: "54%",
    source: "Same 2024 practice survey",
    role: "direct",
  },
  {
    label: "External tool use",
    value: 71.38,
    display: "71.38%",
    source: "Self-selected AccountingWEB sample, 2026",
    role: "direct",
  },
  {
    label: "Any listed AI use",
    value: 50.586,
    display: "50.6%",
    source: "Broad SIC M official context, 2026",
    role: "context",
  },
];

const useCases = [
  ["Tax legislation research", "59.45%", "AccountingWEB 2026"],
  ["Drafting emails", "58.77%", "AccountingWEB 2026"],
  ["Summarising financial data", "53.76%", "AccountingWEB 2026"],
  ["Client communication chatbots", "51%", "Going for Growth 2024"],
  ["Repetitive-task automation", "34%", "Going for Growth 2024"],
  ["AI insights and reporting", "32%", "Going for Growth 2024"],
  ["Document processing", "30%", "Going for Growth 2024"],
  ["Forecasting and scenarios", "29%", "Going for Growth 2024"],
];

export default function AccountingSectorPage() {
  return (
    <>
      <a className="skipLink" href="#accounting-main">Skip to accounting insights</a>
      <SiteHeader active="Sectors" />

      <main id="accounting-main" className="accountingPage">
        <section className="accountingHero" id="top">
          <div className="accountingHeroGrid" aria-hidden="true">
            <span>SIC 69.20</span><span>UK / SME / AI</span><span>SECONDARY DATA</span>
          </div>
          <div className="accountingHeroCopy">
            <p className="kicker light">Sector research · 2026</p>
            <h1>AI use is established. Operational readiness is uneven.</h1>
            <p>
              A five-dimension view of how far adoption has progressed, where
              accounting teams use AI, and which integration, governance and skills
              capabilities remain unresolved.
            </p>
            <div className="heroActions">
              <a className="primaryButton" href={REPORT}>Download the report</a>
              <a className="textButton accountingTextButton" href="#evidence">Explore the evidence</a>
            </div>
          </div>
          <aside className="accountingHeroPanel" aria-label="Headline evidence">
            <span>Direct practice benchmark</span>
            <strong>26%</strong>
            <p>adopted AI in April 2024</p>
            <div><b>54%</b><small>piloting or adopted</small></div>
            <p className="panelCaveat">Includes large practices; not an official accounting-SME prevalence estimate.</p>
          </aside>
          <div className="pageSectionNavigatorMount" />
        </section>

        <section className="accountingContext" aria-label="Research context">
          <div><strong>39,860</strong><span>registered SIC 69.20 SMEs</span></div>
          <div><strong>Secondary only</strong><span>no survey or primary collection</span></div>
          <div><strong>Five dimensions</strong><span>one combined report</span></div>
          <div><strong>Current state</strong><span>benefit is assessed separately</span></div>
        </section>

        <SignalScene
          variant="ledger"
          kicker="ACCOUNTING OPERATING SYSTEM"
          title="From source record to reviewed insight."
          description="AI readiness becomes meaningful when adoption is traced through bookkeeping, ledger control, close, reporting and professional review."
          signals={[
            { label: "Registered SMEs", value: "39,860" },
            { label: "Direct adoption signal", value: "26%" },
            { label: "Study dimensions", value: "05" },
          ]}
        />

        <ReadinessConsole />

        <section className="accountingLead" id="evidence">
          <div className="sectionIntro">
            <p className="kicker">Evidence-led answer</p>
            <h2>Adoption is material—but there is no single defensible sector rate.</h2>
            <p>
              No official open source isolates both accounting and SME size. The
              evidence is therefore triangulated and each percentage keeps its own
              population, question and denominator.
            </p>
          </div>
          <div className="adoptionSignalGrid">
            {adoptionSignals.map((signal) => (
              <article key={signal.label} className={`adoptionSignal ${signal.role}`}>
                <span>{signal.label}</span>
                <strong>{signal.display}</strong>
                <div className="adoptionTrack" aria-hidden="true">
                  <i style={{ width: `${signal.value}%` }} />
                </div>
                <small>{signal.source}</small>
              </article>
            ))}
          </div>
          <p className="evidenceBoundary">
            These are not four estimates of the same quantity. They are not averaged,
            turned into a range or presented as a time series.
          </p>
        </section>

        <section className="accountingDimensions" id="dimensions">
          <div className="sectionIntro">
            <p className="kicker">The five dimensions</p>
            <h2>Task-level use has moved ahead of operational capability.</h2>
            <p>
              Access and task-level use are visible across the accounting evidence.
              Integration, governance and skills remain separate capabilities.
            </p>
          </div>
          <div className="accountingDimensionGrid">
            <article>
              <span>01</span><h3>AI use</h3>
              <p>AI has moved beyond niche experimentation, but no defensible single accounting-SME adoption rate exists.</p>
              <strong>26% adopted · 54% piloting/adopted</strong>
            </article>
            <article>
              <span>02</span><h3>Integration</h3>
              <p>External tools and perceived vendor embedding are widespread in direct survey evidence; verified system integration is less visible.</p>
              <strong>19.9% integration in broad SIC M context</strong>
            </article>
            <article>
              <span>03</span><h3>Governance</h3>
              <p>Data security, skills, approved tools and human review cannot be inferred from tool use.</p>
              <strong>16% well prepared for AI skills in 2024</strong>
            </article>
            <article>
              <span>04</span><h3>Use cases</h3>
              <p>Research, drafting, summarisation, chatbots and document work are the clearest entry points.</p>
              <strong>Text and information work lead</strong>
            </article>
            <article>
              <span>05</span><h3>Pathways</h3>
              <p>Practices mainly access AI through general-purpose tools, vendor features and task-specific applications.</p>
              <strong>Build and automated decisions remain specialised</strong>
            </article>
          </div>
        </section>

        <LandscapeStory
          variant="city"
          src="/manchester-skyline-cc-by.jpg"
          alt="A wide view across the Manchester skyline"
          kicker="OPERATING CONTEXT"
          title="Adoption becomes real when it reaches the operating core."
          description="For accounting practices, the decisive shift is from isolated assistance to controlled use across records, reconciliation, close, reporting and review."
          credit="Manchester skyline · Pete Morris / CC BY 2.0"
          creditHref="https://commons.wikimedia.org/wiki/File:Manchester_Skyline_2025.jpg"
        />

        <section className="accountingUseCases" id="use-cases">
          <div>
            <p className="kicker light">Current pattern</p>
            <h2>Language and information work lead current use.</h2>
            <p>
              The source-defined task lists overlap and come from different surveys.
              They show direction, not a cross-survey ranking.
            </p>
          </div>
          <div className="useCaseList">
            {useCases.map(([label, value, source], index) => (
              <article key={label}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><strong>{label}</strong><small>{source}</small></div>
                <b>{value}</b>
              </article>
            ))}
          </div>
        </section>

        <section className="accountingConclusion">
          <div className="sectionIntro">
            <p className="kicker">Concluding insight</p>
            <h2>Accounting is adopting AI as an assistant—not an autonomous operating model.</h2>
          </div>
          <div className="conclusionGrid">
            <article>
              <span>How much?</span>
              <p>Adoption is no longer niche. The available sources still do not support one exact official accounting-SME rate.</p>
            </article>
            <article>
              <span>What kind?</span>
              <p>Predominantly research, drafting, summarisation and document tasks, with selected automation and reporting use.</p>
            </article>
            <article>
              <span>What is missing?</span>
              <p>Representative SME prevalence, verified workflow integration, consistent governance measures and evidence of business benefit.</p>
            </article>
          </div>
          <a className="accountingNextStudy" href={BENEFITS_REPORT}>
            <span>Next research phase</span>
            <strong>Explore AI benefits and system fit →</strong>
            <small>Bookkeeping, transaction processing and month-end close</small>
          </a>
          <a className="accountingNextStudy" href="/sectors/accounting/adoption-journeys">
            <span>Real implementation evidence</span>
            <strong>Explore Accounting AI Adoption Journeys →</strong>
            <small>Starting problems, pilots, setbacks, controls and outcomes</small>
          </a>
        </section>

        <section className="accountingMethods" id="methods">
          <div>
            <p className="kicker light">Methods and openness</p>
            <h2>Every conclusion traces to secondary evidence.</h2>
            <p>
              ONS business demography provides the population frame. Direct
              accounting surveys provide directional adoption and task evidence.
              Official DSIT data provide broad-sector context. FRC and ICAEW
              guidance inform governance concepts, not prevalence.
            </p>
          </div>
          <div className="methodDownloads">
            <a href={REPORT}><span>Final report</span><strong>Download PDF</strong></a>
            <a href={DATA}><span>Public evidence</span><strong>Download CSV</strong></a>
            <a href={`${REPOSITORY}/tree/main/docs/sectors/accounting`} rel="noreferrer" target="_blank">
              <span>Source trail</span><strong>View methods on GitHub</strong>
            </a>
          </div>
          <p className="accountingDisclaimer">
            The study is descriptive. It does not claim that AI improves productivity,
            accuracy, revenue or client outcomes. Those questions are assessed separately
            in the benefits and system-fit evidence review.
          </p>
        </section>
      </main>

      <SiteFooter />
    </>
  );
}
