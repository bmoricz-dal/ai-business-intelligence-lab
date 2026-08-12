import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "../site-shell";
import { AdoptionDecisionMap } from "./adoption-decision-map";
import { FuturisticWorldMap } from "./futuristic-world-map";
import styles from "./adoption-decision-map.module.css";

const pageTitle = "AI Business Adoption Decision Map | DAL Data & AI Lab";
const pageDescription =
  "Start with a UK SME workflow, see where AI may help, and check the data, people, controls and measures needed for a safe pilot.";
const pageUrl = "https://dal-data-ai-lab.moricz-labs.workers.dev/ai-business-adoption-map";

export const metadata: Metadata = {
  title: pageTitle,
  description: pageDescription,
  alternates: { canonical: pageUrl },
  openGraph: {
    type: "website",
    title: pageTitle,
    description: pageDescription,
    url: pageUrl,
    images: [{ url: "/og.png", width: 1662, height: 946, alt: "DAL AI Business Adoption Decision Map" }],
  },
  twitter: {
    card: "summary_large_image",
    title: pageTitle,
    description: pageDescription,
    images: ["/og.png"],
  },
};

export default function AIAdoptionDecisionMapPage() {
  return (
    <>
      <a className="skipLink" href="#main">Skip to AI Business Adoption Decision Map</a>
      <SiteHeader active="AI in practice" />
      <main className={`multiPage adoptionDecisionPage ${styles.page}`} id="main">
        <section className={`adoptionDecisionHero ${styles.heroStage}`}>
          <div className="adoptionDecisionHeroGrid" aria-hidden="true"><span>PROJECT 01</span><i /><i /><i /></div>
          <FuturisticWorldMap />
          <p className="kicker light">Project 1 · decision support and learning tool</p>
          <h1>Start with the work. Then decide where AI fits.</h1>
          <p className="heroIntroduction">Choose a common SME workflow, see where AI may help, and check the data, people, controls and measures needed for a safe pilot.</p>
          <div className="adoptionDecisionMeta"><span>12 SME workflows</span><span>Value · feasibility · risk</span><span>Evidence boundaries shown</span><span>Reviewed 09 Aug 2026</span></div>
          <div className={`heroSignalConsole ${styles.adoptionHeroConsole}`} aria-hidden="true">
            <div className="heroSignalTop"><span>DAL / INTELLIGENCE NODE</span><b><i /> ACTIVE</b></div>
            <div className="heroSignalCore">
              <span className="signalStarField" />
              <span className="signalGalaxy galaxyOne" /><span className="signalGalaxy galaxyTwo" /><span className="signalGalaxy galaxyThree" />
              <span className="signalLaser laserOne" /><span className="signalLaser laserTwo" /><span className="signalLaser laserThree" />
              <i className="signalNode nodeA" /><i className="signalNode nodeB" /><i className="signalNode nodeC" /><i className="signalNode nodeD" />
              <div className="signalOrb"><strong>AI</strong><small>EVIDENCE</small></div>
            </div>
            <div className="heroSignalReadout"><span>TRACEABLE</span><span>SECONDARY DATA</span><span>HUMAN REVIEW</span></div>
          </div>
        </section>
        <AdoptionDecisionMap />
      </main>
      <SiteFooter />
    </>
  );
}
