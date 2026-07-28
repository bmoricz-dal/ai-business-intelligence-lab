import { NavDropdown } from "./dropdown-nav";

type DataPoint = {
  size: string;
  short: string;
  estimate: number;
  lower: number;
  upper: number;
  base: number;
  benchmark?: boolean;
};

type Insight = {
  id: string;
  number: string;
  eyebrow: string;
  title: string;
  denominator: string;
  summary: string;
  interpretation: string;
  limitation?: string;
  table: string;
  report: string;
  points: DataPoint[];
};

type PathwayMetric = {
  name: string;
  micro: string;
  small: string;
  medium: string;
  large: string;
};

const PUBLIC_REPOSITORY =
  "https://github.com/bmoricz-dal/ai-business-intelligence-lab";
const GITHUB_PROFILE = "https://github.com/bmoricz-dal";
const LINKEDIN_PROFILE = "https://www.linkedin.com/in/benedek-moricz";
const METHODS_GUIDE = `${PUBLIC_REPOSITORY}/blob/main/publications/AI_Business_Intelligence_Lab_Data_and_Methods_Guide.pdf`;
const TECHNICAL_APPENDIX = `${PUBLIC_REPOSITORY}/blob/main/publications/AI_Business_Intelligence_Lab_Technical_Reproducibility_Appendix.pdf`;

const insights: Insight[] = [
  {
    id: "adoption",
    number: "01",
    eyebrow: "Adoption",
    title: "Reported AI use rises with business size",
    denominator: "All UK businesses in each published size group",
    summary:
      "37.4% of micro businesses reported using at least one listed AI-based technology, compared with 50.8% of small and 57.1% of medium businesses.",
    interpretation:
      "The point estimates increase across the three SME groups. The large-business figure is shown as a reference, not as part of the core SME result.",
    table: "UKBDS 2026, Table 42",
    report: "/reports/SME_Preliminary_Report_01_AI_Use_by_Business_Size.pdf",
    points: [
      { size: "Micro (1 to 9 employees)", short: "Micro", estimate: 37.4, lower: 35.4, upper: 39.5, base: 2500 },
      { size: "Small (10 to 49)", short: "Small", estimate: 50.8, lower: 46.6, upper: 54.9, base: 680 },
      { size: "Medium (50 to 249)", short: "Medium", estimate: 57.1, lower: 50.0, upper: 64.3, base: 220 },
      { size: "Large (250+) benchmark", short: "Large", estimate: 78.2, lower: 70.7, upper: 85.7, base: 130, benchmark: true },
    ],
  },
  {
    id: "integration",
    number: "02",
    eyebrow: "Integration",
    title: "System integration remains limited among SME AI users",
    denominator: "UK businesses that report using AI technologies",
    summary:
      "Among AI-using businesses, 26.9% of micro, 31.5% of small and 30.9% of medium businesses said at least one AI tool was integrated with their systems.",
    interpretation:
      "The three SME estimates are relatively close. The large-business reference point is higher, but this descriptive analysis does not claim a statistically significant difference.",
    table: "UKBDS 2026, Table 48",
    report: "/reports/SME_Report_02_AI_Adoption_and_System_Integration_by_Size.pdf",
    points: [
      { size: "Micro (1 to 9 employees)", short: "Micro", estimate: 26.9, lower: 23.8, upper: 29.9, base: 960 },
      { size: "Small (10 to 49)", short: "Small", estimate: 31.5, lower: 26.1, upper: 36.8, base: 350 },
      { size: "Medium (50 to 249)", short: "Medium", estimate: 30.9, lower: 22.4, upper: 39.5, base: 130 },
      { size: "Large (250+) benchmark", short: "Large", estimate: 57.4, lower: 47.4, upper: 67.5, base: 100, benchmark: true },
    ],
  },
  {
    id: "governance",
    number: "03",
    eyebrow: "Governance",
    title: "Many SME AI users report no policy or guidance",
    denominator: "UK businesses that report using AI technologies",
    summary:
      "20.1% of micro, 29.0% of small and 36.8% of medium AI-using businesses reported a formal or informal AI policy or guidance.",
    interpretation:
      "The SME point estimates rise with size. This suggests a practical support opportunity around proportionate policies and guidance, but it does not establish cause or business impact.",
    table: "UKBDS 2026, Table 50",
    report: "/reports/SME_Report_03_AI_Governance_by_Business_Size.pdf",
    points: [
      { size: "Micro (1 to 9 employees)", short: "Micro", estimate: 20.1, lower: 17.3, upper: 22.8, base: 960 },
      { size: "Small (10 to 49)", short: "Small", estimate: 29.0, lower: 23.8, upper: 34.2, base: 350 },
      { size: "Medium (50 to 249)", short: "Medium", estimate: 36.8, lower: 27.8, upper: 45.7, base: 130 },
      { size: "Large (250+) benchmark", short: "Large", estimate: 67.7, lower: 58.1, upper: 77.2, base: 100, benchmark: true },
    ],
  },
  {
    id: "use-cases",
    number: "04",
    eyebrow: "Use cases",
    title: "Research is the leading listed AI use case",
    denominator: "All UK businesses in each published size group",
    summary:
      "Research information is the highest listed use-case point estimate in every published size group: 25.9% of micro, 36.0% of small, 38.5% of medium and 53.7% of large businesses.",
    interpretation:
      "Information work is prominent across business sizes. This describes reported purposes, not how often AI is used, how well it performs, or what business impact it produces.",
    limitation:
      "Businesses could choose more than one use case. These percentages overlap and must not be added together.",
    table: "UKBDS 2026, Table 42",
    report: "/reports/SME_Report_04_How_UK_Businesses_Use_AI.pdf",
    points: [
      { size: "Micro (1 to 9 employees)", short: "Micro", estimate: 25.9, lower: 24.0, upper: 27.7, base: 2500 },
      { size: "Small (10 to 49)", short: "Small", estimate: 36.0, lower: 32.0, upper: 39.9, base: 680 },
      { size: "Medium (50 to 249)", short: "Medium", estimate: 38.5, lower: 31.5, upper: 45.5, base: 220 },
      { size: "Large (250+) benchmark", short: "Large", estimate: 53.7, lower: 44.7, upper: 62.8, base: 130, benchmark: true },
    ],
  },
];

const aiUserPathways: PathwayMetric[] = [
  { name: "System integration", micro: "26.9%", small: "31.5%", medium: "30.9%", large: "57.4%" },
  { name: "Automated decision-making", micro: "5.3%", small: "3.4%", medium: "4.9%", large: "8.4%" },
  { name: "AI policy or guidance", micro: "20.1%", small: "29.0%", medium: "36.8%", large: "67.7%" },
];

const allBusinessPathways: PathwayMetric[] = [
  { name: "In-house AI development or training", micro: "3.3%", small: "3.6%", medium: "6.5%", large: "10.5%" },
];

const reportFive = {
  number: "05",
  title: "Operational AI adoption pathways",
  report: "/reports/SME_Report_05_Operational_AI_Adoption_Pathways.pdf",
};

const reports = [
  ...insights.map(({ number, title, report }) => ({ number, title, report })),
  reportFive,
];

function ConfidenceChart({ insight }: { insight: Insight }) {
  return (
    <div className="chart" aria-label={`${insight.title}. Estimates with supplied 95% confidence intervals.`}>
      <div className="chartScale" aria-hidden="true">
        {[0, 25, 50, 75, 100].map((tick) => (
          <span key={tick} style={{ left: `${tick}%` }}>{tick}%</span>
        ))}
      </div>
      <div className="chartGrid" aria-hidden="true">
        {[0, 25, 50, 75, 100].map((tick) => (
          <i key={tick} style={{ left: `${tick}%` }} />
        ))}
      </div>
      <div className="chartRows">
        {insight.points.map((point) => (
          <div className="chartRow" key={point.short}>
            <span className="chartLabel">{point.short}</span>
            <div className="plot">
              <span
                className={`interval${point.benchmark ? " benchmark" : ""}`}
                style={{ left: `${point.lower}%`, width: `${point.upper - point.lower}%` }}
              />
              <span
                className={`point${point.benchmark ? " benchmark" : ""}`}
                style={{ left: `${point.estimate}%` }}
              />
              <strong style={{ left: `${Math.min(point.upper + 2, 90)}%` }}>
                {point.estimate.toFixed(1)}%
              </strong>
            </div>
          </div>
        ))}
      </div>
      <details className="dataDetails">
        <summary>View exact values and sample bases</summary>
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Size group</th>
                <th scope="col">Estimate</th>
                <th scope="col">95% interval</th>
                <th scope="col">Base</th>
              </tr>
            </thead>
            <tbody>
              {insight.points.map((point) => (
                <tr key={point.size}>
                  <th scope="row">{point.size}</th>
                  <td>{point.estimate.toFixed(1)}%</td>
                  <td>{point.lower.toFixed(1)}% to {point.upper.toFixed(1)}%</td>
                  <td>{point.base.toLocaleString("en-GB")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}

function PathwayTable({
  title,
  denominator,
  rows,
}: {
  title: string;
  denominator: string;
  rows: PathwayMetric[];
}) {
  return (
    <section className="pathwayGroup">
      <p className="pathwayLabel">{title}</p>
      <h4>{denominator}</h4>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Indicator</th>
              <th scope="col">Micro</th>
              <th scope="col">Small</th>
              <th scope="col">Medium</th>
              <th scope="col">Large*</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.name}>
                <th scope="row">{row.name}</th>
                <td>{row.micro}</td>
                <td>{row.small}</td>
                <td>{row.medium}</td>
                <td>{row.large}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to insights</a>
      <div className="reviewBanner">Public evidence release - five-report foundation</div>
      <header className="siteHeader">
        <a className="brand" href="#top" aria-label="SME Intelligence Lab home">
          <span className="brandMark">S</span>
          <span>SME Intelligence Lab</span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#top">Overview</a>
          <NavDropdown
            label="About"
            items={[
              { href: "#background", label: "Background" },
              { href: "#contact", label: "Contact" },
              { href: "#purpose", label: "Purpose" },
              { href: "#values", label: "Values" },
            ]}
          />
          <NavDropdown
            label="AI in business"
            items={[
              { href: "#insights", label: "Five reports" },
              { href: "#reports", label: "Report library" },
            ]}
          />
          <NavDropdown
            label="Sectors"
            items={[
              { href: "#sectors", label: "Technology" },
              { href: "#sectors", label: "Accounting" },
              { href: "#sectors", label: "Financial services" },
            ]}
          />
          <NavDropdown
            label="Adoption pathways"
            items={[
              { href: "#use-cases", label: "Use cases" },
              { href: "#integration", label: "System integration" },
              { href: "#pathways", label: "Automated decisions" },
              { href: "#pathways", label: "Build and training" },
              { href: "#governance", label: "Governance" },
            ]}
          />
          <a href="#method">Methods</a>
          <a href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">GitHub</a>
        </nav>
      </header>

      <main id="main">
        <section className="hero" id="top">
          <div className="heroCopy">
            <p className="kicker">UK SME AI adoption intelligence</p>
            <h1>A growing evidence base for how UK businesses adopt AI.</h1>
            <p className="heroLead">
              Five general reports provide a clear starting point for later
              research by sector, AI tool, business method and adoption pathway.
            </p>
            <div className="heroActions">
              <a className="primaryButton" href="#insights">Explore the evidence</a>
              <a className="textButton" href="#method">Read the methods</a>
            </div>
          </div>
          <aside className="heroPanel" aria-label="The five-report foundation">
            <p className="panelLabel">The five-report foundation</p>
            <ol>
              <li><span>01</span><strong>AI use</strong><small>Who reports using AI?</small></li>
              <li><span>02</span><strong>Integration</strong><small>Is AI connected to business systems?</small></li>
              <li><span>03</span><strong>Governance</strong><small>Is policy or guidance in place?</small></li>
              <li><span>04</span><strong>Use cases</strong><small>What is AI used for?</small></li>
              <li><span>05</span><strong>Adoption pathways</strong><small>How is AI operationalised?</small></li>
            </ol>
          </aside>
        </section>

        <section className="contextStrip" aria-label="Evidence context">
          <div><strong>Official source</strong><span>DSIT UK Business Data Survey 2026</span></div>
          <div><strong>Fieldwork</strong><span>10 Oct 2025 to 28 Jan 2026</span></div>
          <div><strong>Primary scope</strong><span>Micro, small and medium businesses</span></div>
          <div><strong>Publication status</strong><span>5 reports published · methods available</span></div>
        </section>

        <section className="aboutSection" id="about">
          <div className="sectionIntro">
            <p className="kicker">About</p>
            <h2>The research and the person behind it</h2>
            <p>
              A short introduction to the project, its direction and the
              standards used to develop it.
            </p>
          </div>
          <div className="aboutGrid">
            <details className="aboutCard" id="background">
              <summary>Background</summary>
              <div>
                <p>
                  Benedek Moricz holds an MSc with Merit in International Business
                  Economics from Coventry University and a BSc (Hons) in Economics
                  and Industrial Organisation from the University of Warwick.
                </p>
                <p>
                  His experience includes quantitative economic and financial
                  research, AI-output evaluation, accounting support and
                  evidence-led communication for non-technical audiences.
                </p>
                <p>
                  Selected certificates include CMI Level 7 Strategic Management
                  and Leadership Practice, Bloomberg Market Concepts, IBM
                  SkillsBuild AI and data courses, and SAP S/4HANA learning.
                </p>
              </div>
            </details>
            <details className="aboutCard" id="contact">
              <summary>Contact</summary>
              <div className="contactLinks">
                <a href="mailto:benedict.moricz@gmail.com">benedict.moricz@gmail.com</a>
                <a href={GITHUB_PROFILE} rel="noreferrer" target="_blank">GitHub profile</a>
                <a href={LINKEDIN_PROFILE} rel="noreferrer" target="_blank">LinkedIn profile</a>
              </div>
            </details>
            <details className="aboutCard" id="purpose">
              <summary>Purpose</summary>
              <div>
                <p>
                  The project turns reliable public evidence into clear,
                  practical intelligence about AI adoption in UK businesses,
                  with a particular focus on SMEs.
                </p>
                <p>
                  The general reports establish shared definitions and methods.
                  Future work will deepen the evidence by sector and examine
                  specific tools, business methods, use cases and routes to
                  adoption where the available data are strong enough.
                </p>
              </div>
            </details>
            <details className="aboutCard" id="values">
              <summary>Values</summary>
              <div>
                <ul className="valuesList">
                  <li><strong>Evidence before hype:</strong> claims should be traceable and proportionate.</li>
                  <li><strong>Clarity:</strong> technical findings should be understandable to non-specialists.</li>
                  <li><strong>Transparency:</strong> methods, limitations and code should be visible.</li>
                  <li><strong>Responsible use:</strong> AI-supported work still needs human judgement and review.</li>
                  <li><strong>Continuous learning:</strong> the platform should deepen as better evidence becomes available.</li>
                </ul>
              </div>
            </details>
          </div>
        </section>

        <section className="insightsSection" id="insights">
          <div className="sectionIntro">
            <p className="kicker">Current evidence</p>
            <h2>The five reports</h2>
            <p>
              A denominator is the group described by a percentage. Reports 01
              and 04 describe all businesses; Reports 02 and 03 describe only
              businesses already using AI. Report 05 keeps both groups in
              clearly separated panels.
            </p>
          </div>

          {insights.map((insight) => (
            <article className="insight" id={insight.id} key={insight.id}>
              <div className="insightCopy">
                <div className="insightNumber">{insight.number}</div>
                <p className="eyebrow">{insight.eyebrow}</p>
                <h3>{insight.title}</h3>
                <p className="summary">{insight.summary}</p>
                <div className="denominator">
                  <span>Who the percentage describes</span>
                  <strong>{insight.denominator}</strong>
                </div>
                <p className="interpretation">{insight.interpretation}</p>
                {insight.limitation ? (
                  <p className="limitation"><strong>Evidence limit:</strong> {insight.limitation}</p>
                ) : null}
                <div className="sourceLine">
                  <span>{insight.table}</span>
                  <a href={insight.report}>Read report {insight.number}</a>
                </div>
              </div>
              <ConfidenceChart insight={insight} />
            </article>
          ))}

          <article className="insight pathwayInsight" id="pathways">
            <div className="insightCopy">
              <div className="insightNumber">05</div>
              <p className="eyebrow">Adoption pathways</p>
              <h3>Operational pathways vary by measure and business size</h3>
              <p className="summary">
                Among AI-using SMEs, system integration and policy or guidance
                have higher point estimates than automated decision-making.
                In-house AI development or training remains relatively uncommon
                across all businesses.
              </p>
              <div className="denominator">
                <span>Who the percentages describe</span>
                <strong>Two published comparison groups, shown separately</strong>
              </div>
              <p className="interpretation">
                Integration, automated decisions and governance describe
                businesses already using AI. Development or training describes
                all businesses. The indicators are not a required sequence.
              </p>
              <p className="limitation">
                <strong>Evidence limit:</strong> The two groups are never added,
                compared arithmetically or converted into a readiness or maturity
                score.
              </p>
              <div className="sourceLine">
                <span>UKBDS 2026, Tables 43, 47, 48 and 50</span>
                <a href={reportFive.report}>Read report 05</a>
              </div>
            </div>
            <div className="pathwayPanel" aria-label="Operational AI adoption pathway estimates">
              <PathwayTable
                title="Conditional measures"
                denominator="Among businesses already using AI"
                rows={aiUserPathways}
              />
              <PathwayTable
                title="All-business measure"
                denominator="Across all businesses"
                rows={allBusinessPathways}
              />
              <p className="benchmarkNote">* Large businesses are a separate benchmark.</p>
            </div>
          </article>
        </section>

        <section className="architectureSection" id="research-structure">
          <div className="sectionIntro">
            <p className="kicker">Built to deepen over time</p>
            <h2>One foundation, three research branches</h2>
            <p>
              The general evidence base comes first. Later reports can reuse the
              same definitions and methods while focusing on a sector or a
              particular route to adoption.
            </p>
          </div>
          <div className="branchGrid">
            <article>
              <span>Active foundation</span>
              <h3>AI in business</h3>
              <p>
                Cross-business reports on use, integration, governance, use
                cases and operational pathways.
              </p>
              <a href="#reports">View the five-report foundation</a>
            </article>
            <article id="sectors">
              <span>Next research layer</span>
              <h3>Sectors</h3>
              <p>
                Separate evidence pages for technology, accounting, financial
                services and other sectors where the source supports comparison.
              </p>
              <small>Technology · Accounting · Financial services</small>
            </article>
            <article>
              <span>Next research layer</span>
              <h3>Tools and methods</h3>
              <p>
                Focused work on particular AI tools, business tasks,
                implementation methods and governance practices.
              </p>
              <small>Use · Integrate · Automate · Build · Govern</small>
            </article>
          </div>
        </section>

        <section className="methodSection" id="method">
          <div>
            <p className="kicker light">Methods and limitations</p>
            <h2>What the evidence can - and cannot - say</h2>
          </div>
          <div className="methodGrid">
            <article>
              <span>01</span>
              <h3>Different denominators stay separate</h3>
              <p>
                Adoption and in-house development describe all businesses.
                Integration, automated decisions and governance describe
                businesses already reporting AI use.
              </p>
            </article>
            <article>
              <span>02</span>
              <h3>Descriptive, not causal</h3>
              <p>
                The estimates show reported patterns by size. They do not prove
                that size causes adoption, integration or policy differences.
              </p>
            </article>
            <article>
              <span>03</span>
              <h3>Intervals show uncertainty</h3>
              <p>
                Supplied 95% confidence intervals are retained. The reports do
                not label pairwise differences statistically significant from
                the published tables alone.
              </p>
            </article>
            <article>
              <span>04</span>
              <h3>Bases are respondent counts</h3>
              <p>
                Rounded unweighted bases show survey respondents, not the number
                of UK businesses in each size group.
              </p>
            </article>
            <article>
              <span>05</span>
              <h3>Overlapping answers stay separate</h3>
              <p>
                Report 04 allows multiple responses, so use-case percentages are
                not added. Report 05 does not create a maturity score.
              </p>
            </article>
          </div>
          <div className="methodActions">
            <a
              className="sourceButton"
              href="https://www.gov.uk/government/statistics/uk-business-data-survey-2026"
              rel="noreferrer"
              target="_blank"
            >
              Official DSIT source
            </a>
            <a className="sourceButton secondary" href={METHODS_GUIDE} rel="noreferrer" target="_blank">
              Data and Methods Guide
            </a>
            <a className="sourceButton secondary" href={TECHNICAL_APPENDIX} rel="noreferrer" target="_blank">
              Technical Appendix
            </a>
            <a className="sourceButton secondary" href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">
              GitHub evidence repository
            </a>
          </div>
          <p className="methodDownloadNote">
            The Data and Methods Guide and Technical Appendix are public PDFs
            stored in the GitHub repository, alongside the supporting code,
            result extracts and source documentation.
          </p>
        </section>

        <section className="reportsSection" id="reports">
          <div className="sectionIntro">
            <p className="kicker">Research library</p>
            <h2>The five-report foundation</h2>
            <p>
              All five public reports are available here. The Methods section
              and GitHub repository provide the supporting evidence, code and
              limitations.
            </p>
          </div>
          <div className="reportGrid">
            {reports.map((report) => (
              <a className="reportCard" href={report.report} key={report.number}>
                <span>Report {report.number}</span>
                <strong>{report.title}</strong>
                <small>Open PDF report</small>
              </a>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <div>
          <strong>SME Intelligence Lab</strong>
          <p>Independent, evidence-led analysis of UK SME AI and digital adoption.</p>
        </div>
        <nav aria-label="Footer navigation">
          <a href="#about">About</a>
          <a href="#method">Methods</a>
          <a href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">GitHub</a>
          <a href="mailto:benedict.moricz@gmail.com">Contact</a>
        </nav>
        <p>Source: Department for Science, Innovation and Technology. UK Business Data Survey 2026.</p>
      </footer>
    </>
  );
}
