import { AsyncLocalStorage } from "node:async_hooks";
import type { D1Database } from "@cloudflare/workers-types";
import type { Edition } from "../app/news/model";

const databaseContext = new AsyncLocalStorage<D1Database | undefined>();
export function withNewsDatabase<T>(database: D1Database | undefined, callback: () => T): T {
  return databaseContext.run(database, callback);
}
export async function publishedEditions(): Promise<{ available: boolean; editions: Edition[] }> {
  const db = databaseContext.getStore();
  if (!db) return { available: false, editions: [] };
  try {
    const result = await db.prepare("SELECT published_json FROM news_editions WHERE published_json IS NOT NULL ORDER BY edition_date DESC LIMIT 60").all<{ published_json: string }>();
    return { available: true, editions: result.results.map(row => JSON.parse(row.published_json) as Edition) };
  } catch {
    console.error(JSON.stringify({ event: "news_archive_unavailable" }));
    return { available: false, editions: [] };
  }
}
export async function publishedEdition(date: string): Promise<{ available: boolean; edition: Edition | null }> {
  const db = databaseContext.getStore();
  if (!db) return { available: false, edition: null };
  try {
    const row = await db.prepare("SELECT published_json FROM news_editions WHERE edition_date=? AND published_json IS NOT NULL").bind(date).first<{ published_json: string }>();
    return { available: true, edition: row ? JSON.parse(row.published_json) as Edition : null };
  } catch {
    console.error(JSON.stringify({ event: "news_edition_unavailable", date }));
    return { available: false, edition: null };
  }
}
