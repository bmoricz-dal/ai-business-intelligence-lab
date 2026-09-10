import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteFooter, SiteHeader } from "../../site-shell";
import { publishedEdition } from "../../../db/news";
import { validDate } from "../model";
import styles from "../news.module.css";

type Props = { params: Promise<{ date: string }> };
export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { date } = await params;
  if (!validDate(date)) return { title: "Edition not found | DAL News" };
  const { edition } = await publishedEdition(date);
  return { title: edition ? `${edition.title} | DAL News` : "Edition unavailable | DAL News", description: edition?.introduction };
}
export default async function EditionPage({ params }: Props) {
  const { date } = await params;
  if (!validDate(date)) notFound();
  const { available, edition } = await publishedEdition(date);
  if (available && !edition) notFound();
  return <><a className="skipLink" href="#main">Skip to the brief</a><SiteHeader active="News" /><main className={styles.page} id="main">
    <Link href="/news">← All editions</Link>
    {edition ? <><header className={styles.intro}><p className={styles.eyebrow}>DAL NEWS · <time dateTime={date}>{date}</time></p><h1>{edition.title}</h1><p className={styles.description}>{edition.introduction}</p></header>
      {edition.stories.map((story, index) => <article className={styles.story} key={index}><p className={styles.eyebrow}>{index === 0 ? "LEAD ANALYSIS" : `BRIEF ${index}`}</p><h2>{story.headline}</h2><h3>Confirmed facts</h3><p>{story.facts}</p><h3>DAL interpretation</h3><p>{story.interpretation}</p><aside><h3>Evidence boundary</h3><p>{story.evidence_boundary}</p></aside><h3>What to watch</h3><p>{story.watch_next}</p><h3>Sources</h3><ul>{story.sources.map((source, sourceIndex) => <li key={sourceIndex}><a href={source.url} rel="noreferrer">{source.title}</a></li>)}</ul></article>)}
    </> : <section className={styles.latest}><h1>This edition is temporarily unavailable.</h1><p>Please try again later. The news archive remains available from the link above.</p></section>}
  </main><SiteFooter /></>;
}
