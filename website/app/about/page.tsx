import type { Metadata } from "next";
import { PageHero, PUBLIC_REPOSITORY, SiteFooter, SiteHeader } from "../site-shell";

export const metadata: Metadata = {
  title: "About | DAL Data & AI Lab",
  description: "The background, purpose and values behind DAL Data & AI Lab.",
};

export default function AboutPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to about</a>
      <SiteHeader active="About" />
      <main className="multiPage" id="main">
        <PageHero
          kicker="About"
          marker="ECONOMICS · DATA · APPLIED AI"
          title="Independent research built for real AI adoption decisions."
          introduction="DAL combines economics, reproducible data work and applied AI to translate complex evidence into practical choices for SME leaders, advisers and researchers."
        />

        <section className="systemSignalRail" aria-label="Research capability system">
          <span><b>01</b> ECONOMIC REASONING</span><i /><span><b>02</b> DATA PROVENANCE</span><i /><span><b>03</b> APPLIED AI</span><i /><span><b>04</b> SME DECISIONS</span>
        </section>

        <section className="pageSection profileSection" id="background">
          <div className="profileMark" aria-hidden="true"><span>BM</span><small>DAL</small></div>
          <div>
            <p className="kicker">Research profile</p>
            <h2>Economic reasoning, research discipline and applied AI.</h2>
            <p>
              I hold an MSc with Merit in International Business Economics from
              Coventry University and a BSc (Hons) in Economics and Industrial
              Organisation from the University of Warwick.
            </p>
            <p>
              My experience spans quantitative economic and financial research,
              AI-output evaluation, accounting support and evidence-led
              communication for non-technical audiences.
            </p>
            <p>
              Continued development includes CMI Level 7 Strategic Management
              and Leadership Practice, Bloomberg Market Concepts, IBM AI and data
              learning, and SAP S/4HANA learning.
            </p>
          </div>
        </section>

        <section className="pageSection aboutPurpose" id="purpose">
          <div className="sectionLead">
            <p className="kicker">Why the lab exists</p>
            <h2>Evidence should narrow uncertainty—and clarify the next decision.</h2>
          </div>
          <div className="purposeCopy">
            <p>
              The immediate goal is to make adoption, integration, governance, use
              cases and operating pathways easier to compare without obscuring
              differences between survey populations.
            </p>
            <p>
              The longer-term ambition is an SME-facing intelligence service that
              connects adoption evidence with system choice, workflow design,
              governance and demonstrable business value. Research reports will sit
              alongside practical business cases, technical guides and interactive
              labs that show how adoption can be applied, tested and governed.
            </p>
          </div>
        </section>

        <section className="pageSection valuesSection" id="values">
          <div className="sectionLead"><p className="kicker">Research principles</p><h2>The standards behind every published claim.</h2></div>
          <div className="valueCards">
            <article><span>01</span><h3>Meaning before metrics</h3><p>A percentage is useful only when its population, definition and uncertainty remain attached.</p></article>
            <article><span>02</span><h3>Evidence without distance</h3><p>Research should be rigorous enough to trust and clear enough to use in a real business conversation.</p></article>
            <article><span>03</span><h3>Transparency as infrastructure</h3><p>Methods, source trails and evidence limits are part of the product.</p></article>
            <article><span>04</span><h3>Human judgement</h3><p>AI can support delivery, while professional review and accountability remain central.</p></article>
            <article><span>05</span><h3>Cumulative intelligence</h3><p>Each report should create a reusable layer for deeper sector and adoption research.</p></article>
          </div>
        </section>

        <section className="pageSection contactSection" id="contact">
          <div><p className="kicker light">Contact</p><h2>Continue the conversation.</h2><p>Research, methodology and future sector-study enquiries are welcome.</p></div>
          <div className="contactCards">
            <a href="mailto:benedict.moricz@gmail.com"><span>Email</span><strong>benedict.moricz@gmail.com</strong></a>
            <a href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank"><span>GitHub</span><strong>Public evidence repository</strong></a>
            <a href="https://www.linkedin.com/in/benedek-moricz" rel="noreferrer" target="_blank"><span>LinkedIn</span><strong>benedek-moricz</strong></a>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
