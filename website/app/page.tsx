import { ACCOUNTING_REPORT, SYNTHESIS } from "./research-data";
import { PageHero, SiteFooter, SiteHeader } from "./site-shell";

export default function OverviewPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to project overview</a>
      <SiteHeader active="Overview" />
      <main className="multiPage overviewPage" id="main">
        <PageHero
          kicker="Project overview"
          marker="UK · SME · AI · EVIDENCE"
          title="Clear evidence for better conversations about business AI."
          introduction="DAL Data & AI Lab is an independent research platform examining how UK SMEs adopt, use, integrate and govern artificial intelligence. It turns public evidence into practical intelligence without hiding uncertainty."
        />

        <section className="overviewStatus" aria-label="Current publication status">
          <div><strong>5</strong><span>general reports</span></div>
          <div><strong>1</strong><span>cross-report synthesis</span></div>
          <div><strong>1</strong><span>sector report</span></div>
          <div><strong>2026</strong><span>current evidence programme</span></div>
        </section>

        <section className="pageSection purposeSection">
          <div className="sectionLead">
            <p className="kicker">Purpose</p>
            <h2>Make AI adoption evidence rigorous enough to trust and clear enough to use.</h2>
          </div>
          <div className="purposeCopy">
            <p>
              AI adoption is often described through headline percentages that
              combine different businesses, tools and definitions. This project
              keeps the population, denominator, uncertainty and limitation
              attached to every finding.
            </p>
            <p>
              The intended readers are SME leaders, advisers and researchers who
              need a measured starting point for decisions—not promotional claims
              or a single unexplained readiness score.
            </p>
            <a className="inlineLink" href="/about">Read about the project and its values</a>
          </div>
        </section>

        <section className="pageSection evidenceArchitecture">
          <div className="sectionLead">
            <p className="kicker">Research model</p>
            <h2>One evidence foundation, then deeper layers.</h2>
            <p>The programme progresses from general patterns to sector detail and, later, tested business benefit.</p>
          </div>
          <div className="architectureCards">
            <article>
              <span>01 · Foundation</span>
              <h3>AI in business</h3>
              <p>Five reports covering use, integration, governance, use cases and operational pathways by business size.</p>
              <a href="/ai-in-business">Explore the general evidence</a>
            </article>
            <article>
              <span>02 · Sector depth</span>
              <h3>Accounting SMEs</h3>
              <p>The first sector study combines all five dimensions in one secondary-data assessment.</p>
              <a href="/sectors/accounting">Explore accounting AI readiness</a>
            </article>
            <article>
              <span>03 · Next programme</span>
              <h3>Benefits and system fit</h3>
              <p>Future research will test where AI improves businesses, which systems fit which workflows, and what controls are needed.</p>
              <a href="#future">View future goals</a>
            </article>
          </div>
        </section>

        <section className="pageSection currentRelease">
          <div>
            <p className="kicker light">Latest publication</p>
            <h2>UK Accounting SMEs: AI Adoption and Operational Readiness, 2026</h2>
            <p>
              AI is no longer niche in accounting, but current use is more
              established at the task level than at the level of secure,
              governed and integrated operations.
            </p>
          </div>
          <div className="releaseActions">
            <a className="lightButton" href="/sectors/accounting">Read the sector page</a>
            <a href={ACCOUNTING_REPORT}>Download the report</a>
            <a href={SYNTHESIS.href}>Read the general synthesis</a>
          </div>
        </section>

        <section className="pageSection futureSection" id="future">
          <div className="sectionLead">
            <p className="kicker">Future goals</p>
            <h2>Build a cumulative intelligence service for SME adoption decisions.</h2>
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
