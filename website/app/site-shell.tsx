import Link from "next/link";
import Image from "next/image";
import { NavDropdown } from "./dropdown-nav";

type NavigationLabel =
  | "Overview"
  | "About"
  | "AI in business"
  | "Sectors"
  | "AI in practice"
  | "Methods";

export const PUBLIC_REPOSITORY =
  "https://github.com/bmoricz-dal/ai-business-intelligence-lab";

export function SiteHeader({ active }: { active: NavigationLabel }) {
  return (
    <header className="siteHeader pageSiteHeader">
      <Link className="brand" href="/" aria-label="DAL Data and AI Lab home">
        <span className="brandMark" aria-hidden="true">
          <span className="brandNote">♪</span><span>DAL</span>
        </span>
        <span className="brandName">
          <strong>DAL Data &amp; AI Lab</strong><small>SME intelligence</small>
        </span>
      </Link>
      <nav className="pageNavigation" aria-label="Main navigation">
        <Link aria-current={active === "Overview" ? "page" : undefined} href="/">Overview</Link>
        <NavDropdown
          active={active === "About"}
          href="/about"
          label="About"
          items={[
            { href: "/about#background", label: "Background" },
            { href: "/about#purpose", label: "Purpose" },
            { href: "/about#values", label: "Values" },
            { href: "/about#contact", label: "Contact" },
          ]}
        />
        <Link aria-current={active === "AI in business" ? "page" : undefined} href="/ai-in-business">AI in business</Link>
        <NavDropdown
          active={active === "Sectors"}
          href="/sectors"
          label="Sectors"
          items={[
            {
              href: "/sectors/accounting",
              label: "Accounting",
              items: [
                { href: "/sectors/accounting", label: "AI readiness" },
                { href: "/sectors/accounting/benefits", label: "Benefits & system fit" },
                { href: "/sectors/accounting/adoption-journeys", label: "Adoption journeys" },
              ],
            },
            { href: "/sectors#technology", label: "Technology" },
            { href: "/sectors#financial-services", label: "Financial services" },
          ]}
        />
        <NavDropdown
          active={active === "AI in practice"}
          href="/adoption-pathways"
          label="AI in practice"
          items={[
            { href: "/adoption-pathways#background", label: "Background" },
            { href: "/adoption-pathways/accounting-micro-case-study", label: "Accounting Experience Lab" },
          ]}
        />
        <Link aria-current={active === "Methods" ? "page" : undefined} href="/methods">Methods</Link>
        <a className="navRepository" href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">
          GitHub
        </a>
      </nav>
      <span className="headerSystemStatus" aria-hidden="true"><i /> EVIDENCE SYSTEM</span>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="siteFooter pageSiteFooter">
      <div>
        <strong>DAL Data &amp; AI Lab</strong>
        <span>Decision-ready UK SME AI adoption intelligence</span>
      </div>
      <nav aria-label="Footer navigation">
        <Link href="/">Overview</Link>
        <Link href="/about">About</Link>
        <Link href="/methods">Methods</Link>
        <a href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">GitHub</a>
      </nav>
    </footer>
  );
}

export function PageHero({
  kicker,
  title,
  introduction,
  marker,
}: {
  kicker: string;
  title: string;
  introduction: string;
  marker: string;
}) {
  return (
    <section className="pageHero">
      <div className="pageHeroGrid" aria-hidden="true">
        <span>{marker}</span><i /><i /><i />
      </div>
      <div className="pageHeroSystemLayout">
        <div className="pageHeroSystemCopy">
          <p className="kicker light">{kicker}</p>
          <h1>{title}</h1>
          <p>{introduction}</p>
          <div className="pageHeroBriefing" aria-label="Publication principles">
            <span>Independent research</span>
            <span>Open methods</span>
            <span>Practical application</span>
          </div>
        </div>
        <div className="heroSignalConsole" aria-hidden="true">
          <div className="heroSignalTop"><span>DAL / INTELLIGENCE NODE</span><b><i /> ACTIVE</b></div>
          <div className="heroSignalCore">
            <span className="signalOrbit orbitOne" /><span className="signalOrbit orbitTwo" />
            <i className="signalNode nodeA" /><i className="signalNode nodeB" /><i className="signalNode nodeC" /><i className="signalNode nodeD" />
            <div><strong>AI</strong><small>EVIDENCE</small></div>
          </div>
          <div className="heroSignalReadout"><span>TRACEABLE</span><span>SECONDARY DATA</span><span>HUMAN REVIEW</span></div>
        </div>
      </div>
      <div className="pageSectionNavigatorMount" />
    </section>
  );
}

export function SignalScene({
  variant,
  kicker,
  title,
  description,
  signals,
}: {
  variant: "network" | "ledger" | "flow" | "horizon" | "provenance";
  kicker: string;
  title: string;
  description: string;
  signals: Array<{ label: string; value: string }>;
}) {
  return (
    <section className={`signalScene signalScene--${variant}`} aria-label={`${kicker}: ${title}`}>
      <div className="signalSceneField" aria-hidden="true">
        <span className="signalSceneCore"><i /><i /><i /></span>
        <span className="signalSceneArc arcA" /><span className="signalSceneArc arcB" />
        <span className="signalSceneBeam beamA" /><span className="signalSceneBeam beamB" /><span className="signalSceneBeam beamC" />
        <span className="signalSceneNode nodeOne" /><span className="signalSceneNode nodeTwo" /><span className="signalSceneNode nodeThree" /><span className="signalSceneNode nodeFour" />
      </div>
      <div className="signalSceneCopy">
        <span>{kicker}</span>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      <div className="signalSceneReadouts">
        {signals.map((signal, index) => (
          <article key={signal.label}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{signal.value}</strong>
            <small>{signal.label}</small>
          </article>
        ))}
      </div>
    </section>
  );
}

export function LandscapeStory({
  variant,
  src,
  alt,
  kicker,
  title,
  description,
  credit,
  creditHref,
}: {
  variant: "city" | "water" | "highlands" | "coast";
  src: string;
  alt: string;
  kicker: string;
  title: string;
  description: string;
  credit: string;
  creditHref: string;
}) {
  return (
    <section className={`landscapeStory landscapeStory--${variant}`} aria-label={`${kicker}: ${title}`}>
      <Image alt={alt} fill sizes="100vw" src={src} unoptimized />
      <div className="landscapeStoryGrid" aria-hidden="true">
        <i /><i /><i /><i />
        <span className="landscapePulse pulseOne" /><span className="landscapePulse pulseTwo" /><span className="landscapePulse pulseThree" />
      </div>
      <div className="landscapeStoryCopy">
        <span>{kicker}</span>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      <div className="landscapeStoryTelemetry" aria-hidden="true"><span>CONTEXT</span><i /><span>SIGNAL</span><i /><span>DECISION</span></div>
      <a className="landscapeStoryCredit" href={creditHref} rel="noreferrer" target="_blank">{credit}</a>
    </section>
  );
}
