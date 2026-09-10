import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter, SiteHeader } from "../site-shell";
import { publishedEditions } from "../../db/news";
import styles from "./news.module.css";

export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "DAL News | AI developments and business implications",
  description: "Evidence-led AI news for UK business: what changed, why it matters, and what remains uncertain.",
};

export default async function NewsPage() {
  const { available, editions } = await publishedEditions();
  const [latest, ...archive] = editions;
  return <>
    <a className="skipLink" href="#main">Skip to news</a>
    <SiteHeader active="News" />
    <main className={styles.page} id="main">
      <header className={styles.intro}>
        <p className={styles.eyebrow}>DAL NEWS · AI &amp; BUSINESS</p>
        <h1>What changed.<br />What it means for business.</h1>
        <p className={styles.description}>A considered brief on AI developments, implementation and the economy. Primary evidence, practical implications and clear limits.</p>
      </header>
      <div className={styles.principles}><span>Primary sources</span><span>Human editorial review</span><span>UK business relevance</span></div>
      <section className={styles.latest} aria-labelledby="latest-title">
        <p className={styles.eyebrow}>LATEST EDITION</p>
        {latest ? <><time dateTime={latest.date}>{latest.date}</time><h2 id="latest-title"><Link href={`/news/${latest.date}`}>{latest.title}</Link></h2><p>{latest.introduction}</p><Link className={styles.read} href={`/news/${latest.date}`}>Read the brief <span aria-hidden="true">→</span></Link></>
          : <><h2 id="latest-title">{available ? "The first brief is in preparation." : "The news desk is temporarily unavailable."}</h2><p>{available ? "Reviewed editions will appear here. Every story will distinguish the source evidence, DAL interpretation and what remains uncertain." : "Please try again later. You can continue reading DAL’s existing research below."}</p><Link href="/ai-in-business">Explore DAL’s existing AI research →</Link></>}
      </section>
      {archive.length > 0 && <section className={styles.archive} aria-labelledby="archive-title"><h2 id="archive-title">Previous editions</h2>{archive.map(item => <article key={item.date}><time dateTime={item.date}>{item.date}</time><h3><Link href={`/news/${item.date}`}>{item.title}</Link></h3><p>{item.introduction}</p></article>)}</section>}
      <section className={styles.approach}><h2>Read the evidence. Understand the implications.</h2><p>We look for changes that affect cost, capability, adoption and risk. Vendor claims are attributed, preliminary findings are labelled, and uncertainty stays visible.</p><Link href="/methods">Our approach to evidence →</Link></section>
    </main><SiteFooter />
  </>;
}
