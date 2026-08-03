import type { Metadata } from "next";
import { METHODS_GUIDE, TECHNICAL_APPENDIX } from "../research-data";
import { PageHero, PUBLIC_REPOSITORY, SiteFooter, SiteHeader } from "../site-shell";

export const metadata: Metadata = {
  title: "Methods | DAL Data & AI Lab",
  description: "Data sources, denominator controls, comparability rules and reproducibility for DAL Data & AI Lab research.",
};

export default function MethodsPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to methods</a>
      <SiteHeader active="Methods" />
      <main className="multiPage" id="main">
        <PageHero
          kicker="Methods"
          marker="SOURCES · DENOMINATORS · UNCERTAINTY"
          title="Evidence is only useful when the trail remains visible."
          introduction="DAL uses secondary data only. Every public conclusion traces to a source, population, denominator, reference period and limitation. Missing evidence remains a gap—not an invitation to estimate."
        />

        <section className="systemSignalRail" aria-label="Evidence production pipeline">
          <span><b>01</b> SOURCE</span><i /><span><b>02</b> PROFILE</span><i /><span><b>03</b> TRANSFORM</span><i /><span><b>04</b> VALIDATE</span><i /><span><b>05</b> PUBLISH</span>
        </section>

        <section className="pageSection methodPrinciples">
          <div className="sectionLead"><p className="kicker">Core controls</p><h2>Six rules keep the conclusions inside the evidence.</h2></div>
          <div className="principleGrid methodControlGrid">
            <article><span>01</span><h3>Different denominators stay separate</h3><p>All-business estimates are not combined with estimates conditional on already using AI.</p></article>
            <article><span>02</span><h3>Descriptive, not causal</h3><p>Reported patterns do not prove that business size or AI adoption causes a performance outcome.</p></article>
            <article><span>03</span><h3>Uncertainty remains visible</h3><p>Supplied 95% confidence intervals and rounded respondent bases stay attached to estimates.</p></article>
            <article><span>04</span><h3>Multiple responses are not totals</h3><p>Use-case percentages can overlap and are never added together.</p></article>
            <article><span>05</span><h3>Proxies are labelled</h3><p>A broad-sector estimate can provide context but cannot become a sector-specific prevalence figure.</p></article>
            <article><span>06</span><h3>No unsupported score</h3><p>Adoption, integration, governance and pathways are not compressed into a readiness or maturity score.</p></article>
          </div>
        </section>

        <section className="pageSection evidenceStack">
          <div className="sectionLead"><p className="kicker">Evidence stack</p><h2>Each source has a defined job.</h2></div>
          <div className="evidenceStackRows">
            <article><span>Official statistics</span><h3>Population and comparable survey estimates</h3><p>ONS and DSIT evidence provides business frames, published definitions, confidence intervals and structured comparisons.</p></article>
            <article><span>Sector research</span><h3>Direct workflows, tools and professional context</h3><p>Accounting-specific studies contribute directional evidence where their samples and limitations are disclosed.</p></article>
            <article><span>Professional guidance</span><h3>Normative controls, not prevalence</h3><p>FRC and ICAEW guidance helps define governance expectations but is never treated as adoption-rate evidence.</p></article>
            <article><span>Reproducible layer</span><h3>Public data, code and checksums</h3><p>Publication datasets, source registers, transformations, tests and release fingerprints are maintained in GitHub.</p></article>
          </div>
        </section>

        <section className="pageSection methodDownloadsPage">
          <div><p className="kicker light">Documentation</p><h2>Audit the method. Reproduce the evidence.</h2><p>The public repository exposes the governed analytical layer behind the reports.</p></div>
          <div className="methodDownloadCards">
            <a href={METHODS_GUIDE} rel="noreferrer" target="_blank"><span>Plain-language guide</span><strong>Data and Methods Guide</strong></a>
            <a href={TECHNICAL_APPENDIX} rel="noreferrer" target="_blank"><span>Technical documentation</span><strong>Reproducibility Appendix</strong></a>
            <a href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank"><span>Public evidence</span><strong>GitHub repository</strong></a>
          </div>
        </section>

        <section className="pageSection limitationsPage">
          <div className="sectionLead"><p className="kicker">Research boundary</p><h2>Where the evidence ends, the claim stops.</h2></div>
          <p>
            Published survey tables cannot answer every sector-by-size question.
            Where evidence is missing, the report states the gap and uses a labelled
            contextual proxy only when it improves understanding. AI-assisted text
            and code remain subject to human review, and public findings are not
            released until their source and denominator controls pass validation.
          </p>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
