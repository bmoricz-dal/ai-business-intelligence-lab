import { timingSafeEqual } from "node:crypto";
import { validDate, type Edition } from "../app/news/model";

type NewsEnv = Pick<Cloudflare.Env, "DB"> & { NEWS_INGEST_TOKEN?: string; NEWS_EDITOR_TOKEN?: string };
type Row = string[];
type StateName = "source_state" | "identities" | "versions" | "observations" | "pack_items";
type Json = Record<string, unknown>;
const LIMIT = 5_000_000;
const PAGE_SIZE = 100;
const stateTables: Record<StateName, { columns: string[]; keys: string[]; filter: string }> = {
  source_state: { columns: ["source_id", "last_success"], keys: ["source_id"], filter: "1=1" },
  versions: { columns: ["version_id", "item_id", "content_hash", "payload"], keys: ["version_id"], filter: "collected_at >= ?" },
  identities: { columns: ["alias", "item_id"], keys: ["alias"], filter: "item_id IN (SELECT item_id FROM news_versions WHERE collected_at >= ?)" },
  observations: { columns: ["item_id", "source_id", "source_guid", "source_url"], keys: ["item_id", "source_id", "source_guid"], filter: "item_id IN (SELECT item_id FROM news_versions WHERE collected_at >= ?)" },
  pack_items: { columns: ["pack_date", "item_id", "version_id"], keys: ["pack_date", "item_id"], filter: "pack_date >= substr(?,1,10)" },
};
class InputError extends Error {
  constructor(message: string, public status = 400) { super(message); }
}
function json(value: unknown, status = 200) {
  return Response.json(value, { status, headers: { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" } });
}
function object(value: unknown): Json {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new InputError("Expected an object");
  return value as Json;
}
function string(value: unknown, max = 1000): string {
  if (typeof value !== "string" || !value.trim() || value.length > max) throw new InputError("Invalid text field");
  return value;
}
function number(value: unknown): number {
  if (!Number.isSafeInteger(value) || Number(value) < 0) throw new InputError("Invalid revision or count");
  return Number(value);
}
function timestamp(value: unknown): string {
  const result = string(value, 40);
  if (!/^\d{4}-\d{2}-\d{2}T/.test(result) || !Number.isFinite(Date.parse(result))) throw new InputError("Invalid timestamp");
  return result;
}
function allowedLink(value: unknown): string {
  const result = string(value, 4000);
  const url = new URL(result);
  if (!["https:", "http:"].includes(url.protocol) || url.username || url.password) throw new InputError("Invalid source URL");
  return result;
}
async function body(request: Request): Promise<Json> {
  if (!request.headers.get("content-type")?.startsWith("application/json")) throw new InputError("JSON required", 415);
  if (Number(request.headers.get("content-length")) > LIMIT) throw new InputError("Request too large", 413);
  const reader = request.body?.getReader();
  if (!reader) throw new InputError("Missing body");
  const chunks: Uint8Array[] = [];
  let size = 0;
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    size += value.length;
    if (size > LIMIT) { await reader.cancel(); throw new InputError("Request too large", 413); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  return object(JSON.parse(new TextDecoder().decode(bytes)));
}
function authorised(request: Request, token?: string): boolean {
  if (!token || token.length < 32) return false;
  const supplied = new TextEncoder().encode(request.headers.get("Authorization") ?? "");
  const expected = new TextEncoder().encode("Bearer " + token);
  return supplied.length === expected.length && timingSafeEqual(supplied, expected);
}
async function generation(db: D1Database): Promise<number> {
  return (await db.prepare("SELECT COALESCE(MAX(generation),0) AS value FROM news_ingest_generations").first<{ value: number }>())?.value ?? 0;
}
async function state(request: Request, db: D1Database): Promise<Response> {
  const url = new URL(request.url);
  const name = url.searchParams.get("table") as StateName;
  if (!Object.hasOwn(stateTables, name)) throw new InputError("Unknown state table");
  const cursor = Number(url.searchParams.get("cursor") ?? 0);
  number(cursor);
  if (cursor > 100_000) throw new InputError("State cursor too large");
  const current = await generation(db);
  const expected = url.searchParams.get("generation");
  if (expected !== null && number(Number(expected)) !== current) throw new InputError("Collection state changed; restart hydration", 409);
  const config = stateTables[name];
  const since = new Date(Date.now() - 8 * 86400000).toISOString();
  const statement = db.prepare(`SELECT ${config.columns.join(",")} FROM news_${name} WHERE ${config.filter} ORDER BY ${config.keys.join(",")} LIMIT ? OFFSET ?`);
  const result = await statement.bind(...(name === "source_state" ? [] : [since]), PAGE_SIZE, cursor).all<Record<string, string>>();
  return json({ generation: current, table: name, rows: result.results.map(row => config.columns.map(column => row[column])), next_cursor: result.results.length === PAGE_SIZE ? cursor + PAGE_SIZE : null });
}
function upsert(db: D1Database, name: StateName, rows: Row[]): D1PreparedStatement {
  const config = stateTables[name];
  const columns = [...config.columns];
  const expressions = columns.map((_, index) => `json_extract(value,'$[${index}]')`);
  if (name === "versions") { columns.push("collected_at"); expressions.push("json_extract(json_extract(value,'$[3]'),'$.collected_at')"); }
  const updates = columns.filter(column => !config.keys.includes(column)).map(column => `${column}=excluded.${column}`).join(",");
  return db.prepare(`INSERT INTO news_${name} (${columns.join(",")}) SELECT ${expressions.join(",")} FROM json_each(?) WHERE 1 ON CONFLICT(${config.keys.join(",")}) DO UPDATE SET ${updates}`).bind(JSON.stringify(rows));
}
async function ingest(input: Json, db: D1Database): Promise<Response> {
  const packText = string(input.pack_json, 1_500_000);
  const expectedHash = string(input.transport_sha256, 64);
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(packText));
  const hash = Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2, "0")).join("");
  if (hash !== expectedHash) throw new InputError("Pack transport checksum mismatch");
  const pack = object(JSON.parse(packText));
  const summary = object(pack.run_summary);
  const date = string(summary.pack_date, 10);
  if (!validDate(date) || pack.schema_version !== 1 || pack.publication_approved !== false || pack.editorial_status !== "unreviewed") throw new InputError("Invalid evidence pack");
  const started = timestamp(summary.started_at);
  if (started.slice(0, 10) !== date || Date.parse(started) > Date.now() + 15 * 60000) throw new InputError("Invalid collection time");
  const runId = string(summary.run_id, 64);
  const status = string(summary.status, 32);
  if (!["complete", "incomplete", "failed", "needs_review"].includes(status)) throw new InputError("Invalid collection status");
  if (!Array.isArray(pack.evidence_items) || pack.evidence_items.length > 500 || number(summary.item_total) !== pack.evidence_items.length) throw new InputError("Invalid item count");
  object(pack.coverage_and_gaps); object(pack.integrity_checks);
  for (const value of pack.evidence_items) {
    const item = object(value);
    string(item.item_id, 64); string(item.version_id, 64); string(item.title, 500); allowedLink(item.canonical_url);
  }
  const previous = await db.prepare("SELECT transport_hash FROM news_collection_runs WHERE run_id=?").bind(runId).first<{ transport_hash: string }>();
  if (previous) {
    if (previous.transport_hash !== hash) throw new InputError("Run ID already contains different evidence", 409);
    return json({ run_id: runId, status: "already_stored" });
  }
  const expected = number(input.generation);
  if (await generation(db) !== expected) throw new InputError("Collection state changed; recollect before uploading", 409);
  const tables = object(input.state);
  const statements = [db.prepare("INSERT INTO news_ingest_generations(generation,run_id) VALUES (?,?)").bind(expected + 1, runId)];
  for (const name of Object.keys(stateTables) as StateName[]) {
    const rows = tables[name];
    if (!Array.isArray(rows) || rows.length > 10_000) throw new InputError("Invalid state rows");
    for (const row of rows) {
      if (!Array.isArray(row) || row.length !== stateTables[name].columns.length || row.some(cell => typeof cell !== "string" || cell.length > 30_000)) throw new InputError("Invalid state row");
      if (name === "versions") {
        const record = object(JSON.parse(row[3]));
        if (record.version_id !== row[0] || record.item_id !== row[1]) throw new InputError("Version identity mismatch");
        timestamp(record.collected_at);
      }
    }
    if (new TextEncoder().encode(JSON.stringify(rows)).length > 1_500_000) throw new InputError("State table exceeds upload limit", 413);
    statements.push(upsert(db, name, rows));
  }
  statements.push(db.prepare("INSERT INTO news_collection_runs(run_id,pack_date,started_at,status,transport_hash,payload) VALUES (?,?,?,?,?,?)").bind(runId, date, started, status, hash, packText));
  statements.push(db.prepare("INSERT INTO news_daily_packs(pack_date,run_id) VALUES (?,?) ON CONFLICT(pack_date) DO UPDATE SET run_id=excluded.run_id").bind(date, runId));
  // The unique generation serialises writers; D1 rolls back the batch on conflict.
  await db.batch(statements);
  return json({ run_id: runId, generation: expected + 1, status: "stored" }, 201);
}

function edition(value: unknown, date: string): Edition {
  const input = object(value);
  if (input.date !== date || !Array.isArray(input.stories) || input.stories.length < 1 || input.stories.length > 6) throw new InputError("Invalid edition");
  if (!Array.isArray(input.evidence_run_ids) || !input.evidence_run_ids.length || input.evidence_run_ids.length > 10) throw new InputError("Evidence run references required");
  const stories = input.stories.map(value => {
    const story = object(value);
    if (!Array.isArray(story.sources) || !story.sources.length || story.sources.length > 12) throw new InputError("Story sources required");
    return { headline: string(story.headline, 200), facts: string(story.facts, 8000), interpretation: string(story.interpretation, 8000), evidence_boundary: string(story.evidence_boundary, 4000), watch_next: string(story.watch_next, 4000), sources: story.sources.map(value => { const source = object(value); return { title: string(source.title, 300), url: allowedLink(source.url) }; }) };
  });
  return { date, title: string(input.title, 200), introduction: string(input.introduction, 2000), stories, evidence_run_ids: input.evidence_run_ids.map(id => string(id, 64)) };
}
async function edit(input: Json, date: string, action: string, db: D1Database): Promise<Response> {
  const expected = number(input.expected_revision);
  if (action === "draft") {
    const content = edition(input.edition, date);
    for (const id of content.evidence_run_ids) {
      if (!await db.prepare("SELECT 1 FROM news_collection_runs WHERE run_id=?").bind(id).first()) throw new InputError("Referenced evidence run not found");
    }
    const result = expected === 0
      ? await db.prepare("INSERT INTO news_editions(edition_date,draft_json,revision) VALUES (?,?,1) ON CONFLICT DO NOTHING").bind(date, JSON.stringify(content)).run()
      : await db.prepare("UPDATE news_editions SET draft_json=?,revision=revision+1,approved_revision=NULL,approved_by=NULL,approved_at=NULL WHERE edition_date=? AND revision=?").bind(JSON.stringify(content), date, expected).run();
    if (!result.meta.changes) throw new InputError("Edition changed; reload before editing", 409);
    return json({ date, status: "draft", revision: expected + 1 });
  }
  if (action === "approve") {
    const reviewer = string(input.reviewer, 120);
    const result = await db.prepare("UPDATE news_editions SET approved_revision=revision,approved_by=?,approved_at=? WHERE edition_date=? AND revision=?").bind(reviewer, new Date().toISOString(), date, expected).run();
    if (!result.meta.changes) throw new InputError("Draft revision not found", 409);
    return json({ date, status: "approved", revision: expected });
  }
  if (action === "publish") {
    const result = await db.prepare("UPDATE news_editions SET published_json=draft_json,published_revision=revision,published_at=? WHERE edition_date=? AND revision=? AND approved_revision=revision").bind(new Date().toISOString(), date, expected).run();
    if (!result.meta.changes) throw new InputError("This draft revision has not been approved", 409);
    return json({ date, status: "published", revision: expected });
  }
  throw new InputError("Unknown editorial action", 404);
}

export async function newsRequest(request: Request, env: NewsEnv): Promise<Response | null> {
  const path = new URL(request.url).pathname;
  if (!path.startsWith("/api/news/") && !path.startsWith("/briefing/evidence/")) return null;
  try {
    const collector = path.startsWith("/api/news/collector/");
    const editor = path.startsWith("/api/news/editor/");
    if ((collector || editor) && !authorised(request, collector ? env.NEWS_INGEST_TOKEN : env.NEWS_EDITOR_TOKEN)) return json({ error: "Unauthorised" }, 401);
    if (!env.DB) return json({ error: "News service is not configured" }, 503);
    if (collector && path === "/api/news/collector/state" && request.method === "GET") return await state(request, env.DB);
    if (collector && path === "/api/news/collector/runs" && request.method === "POST") return await ingest(await body(request), env.DB);
    const editionMatch = /^\/api\/news\/editor\/editions\/(\d{4}-\d{2}-\d{2})$/.exec(path);
    if (editor && editionMatch && validDate(editionMatch[1]) && request.method === "GET") {
      const row = await env.DB.prepare("SELECT edition_date,revision,approved_revision,approved_by,approved_at,published_revision,published_at,draft_json FROM news_editions WHERE edition_date=?").bind(editionMatch[1]).first();
      return row ? json(row) : json({ error: "Edition not found" }, 404);
    }
    const editMatch = /^\/api\/news\/editor\/editions\/(\d{4}-\d{2}-\d{2})\/(draft|approve|publish)$/.exec(path);
    if (editor && editMatch && validDate(editMatch[1]) && request.method === "POST") return await edit(await body(request), editMatch[1], editMatch[2], env.DB);
    const evidence = /^\/briefing\/evidence\/(latest|\d{4}-\d{2}-\d{2})\.json$/.exec(path);
    if (evidence && request.method === "GET") {
      if (evidence[1] !== "latest" && !validDate(evidence[1])) throw new InputError("Invalid date");
      const query = "SELECT r.payload FROM news_daily_packs p JOIN news_collection_runs r ON p.run_id=r.run_id " + (evidence[1] === "latest" ? "ORDER BY p.pack_date DESC LIMIT 1" : "WHERE p.pack_date=?");
      const statement = env.DB.prepare(query);
      const row = await (evidence[1] === "latest" ? statement : statement.bind(evidence[1])).first<{ payload: string }>();
      return row ? json(JSON.parse(row.payload)) : json({ error: "No evidence pack available" }, 404);
    }
    if (request.method !== "GET" && !collector && !editor) return json({ error: "Method not allowed" }, 405);
    return json({ error: "Not found" }, 404);
  } catch (error) {
    if (error instanceof InputError) return json({ error: error.message }, error.status);
    if (error instanceof SyntaxError || error instanceof TypeError || error instanceof RangeError) return json({ error: "Invalid request" }, 400);
    console.error(JSON.stringify({ event: "news_request_failed", path, error_type: error instanceof Error ? error.name : "Unknown" }));
    return json({ error: "News service temporarily unavailable; no publication confirmed" }, 503);
  }
}
