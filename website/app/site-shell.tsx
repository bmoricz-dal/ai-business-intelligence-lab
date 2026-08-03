import Link from "next/link";
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
            { href: "/adoption-pathways/accounting-micro-case-study", label: "Accounting adoption lab" },
          ]}
        />
        <Link aria-current={active === "Methods" ? "page" : undefined} href="/methods">Methods</Link>
        <a className="navRepository" href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">
          GitHub
        </a>
      </nav>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="siteFooter pageSiteFooter">
      <div>
        <strong>DAL Data &amp; AI Lab</strong>
        <span>Independent UK SME AI adoption intelligence</span>
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
      <div>
        <p className="kicker light">{kicker}</p>
        <h1>{title}</h1>
        <p>{introduction}</p>
      </div>
    </section>
  );
}
