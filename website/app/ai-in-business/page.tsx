import type { Metadata } from "next";
import Image from "next/image";
import { REPORTS, SYNTHESIS } from "../research-data";
import { PageHero, SiteFooter, SiteHeader } from "../site-shell";

export const metadata: Metadata = {
  title: "AI in Business | DAL Data & AI Lab",
  description: "Five evidence-led reports on AI use, integration, governance, use cases and operational pathways among UK businesses.",
};

const snapshots = [
  { label: "Micro businesses reporting AI use", value: "37.4%", width: "37.4%" },
  { label: "Small businesses reporting AI use", value: "50.8%", width: "50.8%" },
  { label: "Medium businesses reporting AI use", value: "57.1%", width: "57.1%" },
  { label: "Large-business benchmark", value: "78.2%", width: "78.2%", benchmark: true },
];

export default function AIInBusinessPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to AI in business</a>
      <SiteHeader active="AI in business" />
      <main className="multiPage" id="main">
        <PageHero
          kicker="AI in business"
          marker="REPORTS 01–05 · UKBDS 2026"
          title="AI use is expanding faster than operational depth."
          introduction="Five reports track reported use, system integration, governance, use cases and adoption pathways by UK business size—without turning different denominators into a false maturity score."
        />

        <section className="systemSignalRail metricRail" aria-label="General evidence signal path">
          <span><b>37.4%</b> MICRO USE</span><i /><span><b>26.9%</b> MICRO INTEGRATION</span><i /><span><b>20.1%</b> MICRO GUIDANCE</span><i /><span><b>5</b> LINKED REPORTS</span>
        </section>

        <section className="pageSection evidenceSnapshot" id="snapshot">
          <div className="sectionLead">
            <p className="kicker">Evidence snapshot</p>
            <h2>Scale remains the clearest dividing line in reported AI use.</h2>
            <p>Micro-business use is material, but it trails every larger size band. Large businesses remain a separate benchmark—not part of the SME conclusion.</p>
          </div>
          <div className="snapshotBars" aria-label="Reported AI use estimates by business size">
            {snapshots.map((item) => (
              <div key={item.label} className={item.benchmark ? "benchmark" : undefined}>
                <span>{item.label}</span><strong>{item.value}</strong>
                <i aria-hidden="true"><b style={{ width: item.width }} /></i>
              </div>
            ))}
          </div>
        </section>

        <section className="cinematicInterlude" aria-labelledby="cinematic-ai-title">
          <Image
            alt="A small business team reviewing financial work together in a London office at blue hour."
            fill
            sizes="100vw"
            src="/uk-sme-ai-workplace-2026.png"
            unoptimized
          />
          <div className="cinematicSphere" aria-hidden="true">
            <i /><i /><i />
            <span><b>AI</b><small>WORKFLOW SIGNAL</small></span>
          </div>
          <div className="cinematicCopy">
            <span>FROM ADOPTION TO OPERATION</span>
            <h2 id="cinematic-ai-title">The evidence changes the question.</h2>
            <p>Not only whether a firm uses AI, but where it enters the workflow, who reviews it, what changes, and how value is measured.</p>
          </div>
          <div className="cinematicTelemetry" aria-hidden="true"><span>USE</span><i /><span>WORKFLOW</span><i /><span>CONTROL</span><i /><span>VALUE</span></div>
        </section>

        <section className="pageSection reportLibrary" id="reports">
          <div className="sectionLead">
            <p className="kicker">Five-report series</p>
            <h2>Five reports separate reach from operational readiness.</h2>
          </div>
          <div className="reportPageGrid">
            {REPORTS.map((report) => (
              <article key={report.number}>
                <span className="reportIndex">{report.number}</span>
                <p>{report.theme}</p>
                <h3>{report.title}</h3>
                <strong>{report.finding}</strong>
                <small><b>Denominator:</b> {report.denominator}</small>
                <a href={report.href}>Read report {report.number}</a>
              </article>
            ))}
          </div>
        </section>

        <section className="pageSection synthesisFeature" id="synthesis">
          <div>
            <p className="kicker light">Cross-report synthesis</p>
            <h2>Access is not the same as operational depth.</h2>
            <p>
              Tool access, task use, system integration, governance and in-house
              development are different operating signals. The synthesis connects
              them without inventing a conversion funnel or readiness score.
            </p>
          </div>
          <div className="synthesisPoints">
            <article><span>Reach</span><strong>Use expands before integration.</strong></article>
            <article><span>Tasks</span><strong>Information work is the leading entry point.</strong></article>
            <article><span>Operations</span><strong>Integration and governance are separate workstreams.</strong></article>
            <a className="lightButton" href={SYNTHESIS.href}>Read the synthesis</a>
          </div>
        </section>

        <section className="pageSection evidenceBoundaryPage">
          <div className="sectionLead"><p className="kicker">Evidence boundary</p><h2>What these reports can—and cannot—show.</h2></div>
          <ul>
            <li>Estimates describe reported patterns, not causal business impact.</li>
            <li>All-business and AI-user percentages remain separate.</li>
            <li>Multiple-response use cases are not added together.</li>
            <li>Supplied 95% confidence intervals and respondent bases are retained.</li>
            <li>No formal pairwise significance claim is inferred from overlapping intervals alone.</li>
          </ul>
          <a className="inlineLink" href="/methods">Read the full methods and limitations</a>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
