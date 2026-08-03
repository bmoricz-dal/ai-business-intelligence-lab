import Image from "next/image";
import { SYNTHESIS } from "./research-data";
import { ProgrammeConsole } from "./intelligence-ui";
import { PageHero, SiteFooter, SiteHeader } from "./site-shell";

const MICRO_CASE_REPORT = "/reports/UK_Micro_Accounting_Practice_AI_Adoption_Worked_Case_2026.pdf";

export default function OverviewPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to project overview</a>
      <SiteHeader active="Overview" />
      <main className="multiPage overviewPage" id="main">
        <PageHero
          kicker="Project overview"
          marker="UK · SME · AI · EVIDENCE"
          title="See where SME AI adoption is real—and where the evidence stops."
          introduction="DAL turns public UK evidence into decision-ready intelligence on AI use, integration, governance and implementation. Every signal retains its population, denominator and limitation."
        />

        <section className="overviewStatus" aria-label="Current publication status">
          <div><strong>5</strong><span>general reports</span></div>
          <div><strong>1</strong><span>cross-report synthesis</span></div>
          <div><strong>4</strong><span>accounting programme outputs</span></div>
          <div><strong>1</strong><span>interactive adoption lab</span></div>
        </section>

        <section className="systemVisualFeature" aria-label="Accounting intelligence system visual">
          <Image
            alt="A small accounting team reviewing source documents and financial workflow screens within a connected AI control system."
            fill
            priority
            sizes="100vw"
            src="/og.png"
            unoptimized
          />
          <div className="systemVisualTelemetry" aria-hidden="true">
            <span>DOCUMENTS</span><i /><span>LEDGER</span><i /><span>REVIEW</span><i /><span>INSIGHT</span>
          </div>
          <div className="systemVisualCaption"><span>ACCOUNTING SYSTEM / 01</span><strong>Human judgement stays inside the AI-enabled workflow.</strong></div>
        </section>

        <section className="pageSection purposeSection">
          <div className="sectionLead">
            <p className="kicker">Purpose</p>
            <h2>Turn fragmented AI evidence into decisions leaders can defend.</h2>
          </div>
          <div className="purposeCopy">
            <p>
              Headline adoption percentages often combine different businesses,
              tools and definitions. DAL keeps the population, denominator,
              uncertainty and limitation attached to every finding.
            </p>
            <p>
              The result is a measured starting point for SME leaders, advisers and
              researchers—not a promotional claim or a single unexplained readiness score.
            </p>
            <a className="inlineLink" href="/about">Read about the project and its values</a>
          </div>
        </section>

        <section className="pageSection evidenceArchitecture">
          <div className="sectionLead">
            <p className="kicker">Research model</p>
            <h2>Start broad. Go sector-deep. Test what changes in practice.</h2>
            <p>The programme moves from comparable national signals to sector workflows, implementation evidence and controlled demonstrations.</p>
          </div>
          <div className="architectureCards">
            <article>
              <span>01 · Foundation</span>
              <h3>AI in business</h3>
              <p>Five linked reports separate use, integration, governance, use cases and operational pathways by business size.</p>
              <a href="/ai-in-business">Explore the general evidence</a>
            </article>
            <article>
              <span>02 · Sector depth</span>
              <h3>Accounting SMEs</h3>
              <p>The first sector programme tests what those five dimensions mean inside accounting work.</p>
              <a href="/sectors/accounting">Explore accounting AI readiness</a>
            </article>
            <article>
              <span>03 · Practical application</span>
              <h3>AI in practice</h3>
              <p>Interactive business and technical cases show how adoption changes a workflow—and which controls make it credible.</p>
              <a href="/adoption-pathways">Explore practical adoption</a>
            </article>
          </div>
        </section>

        <section className="pageSection accountingProgrammeOverview" id="accounting-research">
          <div className="sectionLead">
            <p className="kicker">Accounting research programme</p>
            <h2>One accounting programme. Four questions leaders need answered.</h2>
            <p>How far has adoption progressed? Where is value supported? What changes during implementation? What does an AI-enabled accounting cycle look like in use?</p>
          </div>
          <ProgrammeConsole />
        </section>

        <section className="pageSection currentRelease">
          <div>
            <p className="kicker light">Accounting AI Experience Lab · latest release</p>
            <h2>Test-drive an AI-enabled accounting cycle.</h2>
            <p>
              Move one fictional client from source records to ledger review,
              reconciliation, close and insight. Compare operating methods and see
              where professional review, exceptions and safe stops remain essential.
            </p>
          </div>
          <div className="releaseActions">
            <a className="lightButton" href="/adoption-pathways/accounting-micro-case-study">Start the test drive</a>
            <a href={MICRO_CASE_REPORT}>Download the supporting report</a>
            <a href={SYNTHESIS.href}>Read the general synthesis</a>
          </div>
        </section>

        <section className="pageSection futureSection" id="future">
          <div className="sectionLead">
            <p className="kicker">Future goals</p>
            <h2>Build the evidence base from adoption signals to measured business value.</h2>
          </div>
          <ol className="futureRoadmap">
            <li><span>Now</span><div><strong>Complete the current-state baseline</strong><p>Maintain general and accounting-sector adoption evidence as new secondary data becomes available.</p></div></li>
            <li><span>Next</span><div><strong>Study beneficial adoption</strong><p>Assess which workflows, system types and implementation methods create measurable value for practices and client businesses.</p></div></li>
            <li><span>Then</span><div><strong>Extend sector coverage</strong><p>Develop technology and financial-services reports where the evidence supports defensible sector comparison.</p></div></li>
            <li><span>Long term</span><div><strong>Turn research into decision tools</strong><p>Create transparent benchmarks and practical guidance while keeping claims traceable to evidence.</p></div></li>
          </ol>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
