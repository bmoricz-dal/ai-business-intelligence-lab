import type { Metadata } from "next";
import { ACCOUNTING_REPORT } from "../research-data";
import { PageHero, SiteFooter, SiteHeader } from "../site-shell";

export const metadata: Metadata = {
  title: "Sector Research | DAL Data & AI Lab",
  description: "Sector-focused research on AI adoption among UK SMEs, beginning with accounting practices.",
};

export default function SectorsPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to sector research</a>
      <SiteHeader active="Sectors" />
      <main className="multiPage" id="main">
        <PageHero
          kicker="Sector research"
          marker="GENERAL EVIDENCE → SECTOR DEPTH"
          title="Different sectors need different adoption questions."
          introduction="The sector programme applies a common evidence framework while respecting differences in workflows, regulation, data sensitivity, firm structure and available sources."
        />

        <section className="pageSection sectorPrinciples">
          <div className="sectionLead">
            <p className="kicker">Why sector depth matters</p>
            <h2>Broad business averages cannot answer every operational question.</h2>
          </div>
          <div className="principleGrid">
            <article><span>01</span><h3>Define the business population</h3><p>Use industry classifications and size bands that match the firms the report is intended to describe.</p></article>
            <article><span>02</span><h3>Keep direct and contextual evidence separate</h3><p>A broad-sector proxy can add context but cannot become a sector-specific estimate.</p></article>
            <article><span>03</span><h3>Reflect real work</h3><p>Use cases and controls should map to the tasks, professional duties and data handled in that sector.</p></article>
          </div>
        </section>

        <section className="pageSection accountingSectorFeature" id="accounting">
          <div>
            <p className="kicker light">Published sector report · 01</p>
            <h2>UK Accounting SMEs: AI Adoption and Operational Readiness, 2026</h2>
            <p>
              The first sector report combines adoption, integration, governance,
              use cases and pathways in one secondary-data study of SIC 69.20
              accounting practices.
            </p>
            <div className="sectorMetrics">
              <div><strong>39,860</strong><span>registered accounting SMEs</span></div>
              <div><strong>26%</strong><span>adopted AI in the direct 2024 practice benchmark</span></div>
              <div><strong>54%</strong><span>piloting or adopted in the same survey</span></div>
            </div>
          </div>
          <div className="releaseActions">
            <a className="lightButton" href="/sectors/accounting">Explore the accounting page</a>
            <a href={ACCOUNTING_REPORT}>Download the final report</a>
            <a href="/data/accounting_ai_readiness_2026.csv">Download the public evidence</a>
          </div>
        </section>

        <section className="pageSection upcomingSectors">
          <div className="sectionLead"><p className="kicker">Future sector programme</p><h2>Planned only where evidence is strong enough.</h2></div>
          <div className="sectorCardGrid">
            <article id="technology"><span>In development</span><h3>Technology SMEs</h3><p>Adoption depth, product development, technical capability, internal build pathways and governance.</p><small>Publication depends on sector-specific source coverage and comparability review.</small></article>
            <article id="financial-services"><span>Research candidate</span><h3>Financial services SMEs</h3><p>AI use in regulated workflows, customer service, risk, compliance, data controls and human oversight.</p><small>Scope will distinguish regulated firms from in-house finance functions.</small></article>
            <article><span>Evidence-led expansion</span><h3>Additional sectors</h3><p>New sectors will be prioritised by SME relevance, open-data quality and the practical value of a dedicated study.</p><small>No sector will be published from a broad proxy alone.</small></article>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
