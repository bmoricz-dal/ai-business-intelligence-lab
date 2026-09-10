import Link from "next/link";
import { PUBLIC_REPOSITORY } from "./site-shell";
import styles from "./mobile-site-nav.module.css";

export function MobileSiteNav({ active }: { active: string }) {
  return (
    <details className={styles.mobileNav}>
      <summary><span>Menu</span><strong>{active}</strong></summary>
      <nav aria-label="Mobile navigation">
        <Link aria-current={active === "Overview" ? "page" : undefined} href="/">Overview</Link>
        <Link aria-current={active === "News" ? "page" : undefined} href="/news">News</Link>
        <Link aria-current={active === "About" ? "page" : undefined} href="/about">About</Link>
        <Link aria-current={active === "AI in business" ? "page" : undefined} href="/ai-in-business">AI in business</Link>
        <Link aria-current={active === "Sectors" ? "page" : undefined} href="/sectors">Sectors</Link>
        <Link aria-current={active === "AI in practice" ? "page" : undefined} href="/adoption-pathways">AI in practice</Link>
        <Link href="/ai-business-adoption-map">Decision map</Link>
        <Link href="/adoption-pathways/accounting-micro-case-study">Accounting Experience Lab</Link>
        <Link href="/adoption-pathways/construction-tender-lab">Construction Tender Lab</Link>
        <Link aria-current={active === "Methods" ? "page" : undefined} href="/methods">Methods</Link>
        <a href={PUBLIC_REPOSITORY} rel="noreferrer" target="_blank">GitHub ↗</a>
      </nav>
    </details>
  );
}
