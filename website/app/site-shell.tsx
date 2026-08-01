import Link from "next/link";

type NavigationLabel =
  | "Overview"
  | "About"
  | "AI in business"
  | "Sectors"
  | "Adoption pathways"
  | "Methods";

const navigation: Array<{ href: string; label: NavigationLabel }> = [
  { href: "/", label: "Overview" },
  { href: "/about", label: "About" },
  { href: "/ai-in-business", label: "AI in business" },
  { href: "/sectors", label: "Sectors" },
  { href: "/adoption-pathways", label: "Adoption pathways" },
  { href: "/methods", label: "Methods" },
];

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
        {navigation.map((item) => (
          <Link
            aria-current={item.label === active ? "page" : undefined}
            href={item.href}
            key={item.href}
          >
            {item.label}
          </Link>
        ))}
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
