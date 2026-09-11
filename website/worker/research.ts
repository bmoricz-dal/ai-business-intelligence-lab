import { timingSafeEqual } from "node:crypto";

type Env = Pick<Cloudflare.Env, "DB"> & { NEWS_RESEARCH_TOKEN?: string };
const BASE = "/api/news/research";
export const RESEARCH_MODEL = "codex-chatgpt";
export const DAILY_RESEARCH_LIMIT = 6;
const headers = { "Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow", "X-Content-Type-Options": "nosniff" };
const reply = (data: unknown, status = 200) => Response.json(data, { status, headers });
const validText = (value: unknown, max: number): value is string => typeof value === "string" && value.trim().length > 0 && value.length <= max;
const object = (value: unknown): value is Record<string, unknown> => !!value && typeof value === "object" && !Array.isArray(value);
export function safeResearchUrl(value: unknown): value is string {
  if (!validText(value, 2000)) return false;
  try { const u = new URL(value); return u.protocol === "https:" && !u.username && !u.password && u.hostname.includes(".") && !u.hostname.endsWith(".local") && !u.hostname.endsWith(".localhost") && !/^[\d.:\[\]]+$/.test(u.hostname); } catch { return false; }
}
export function validResearchResult(value: unknown): boolean {
  if (!object(value) || value.schema_version !== 1 || value.publication_approved !== false || value.editorial_status !== "awaiting_human_review" || value.model !== RESEARCH_MODEL) return false;
  if (!["summary", "facts", "interpretation", "evidence_boundary", "watch_next"].every(k => validText(value[k], 6000))) return false;
  if (!Array.isArray(value.sources) || value.sources.length < 1 || value.sources.length > 20 || !value.sources.every(s => object(s) && validText(s.title, 300) && safeResearchUrl(s.url))) return false;
  const urls = new Set(value.sources.map(s => s.url));
  if (!Array.isArray(value.claims) || value.claims.length < 1 || value.claims.length > 12) return false;
  return value.claims.every(c => object(c) && validText(c.claim, 1200) && ["source_reported", "multiple_sources", "unresolved"].includes(String(c.assessment)) && Array.isArray(c.source_urls) && c.source_urls.length <= 8 && (c.assessment === "unresolved" || c.source_urls.length > 0) && c.source_urls.every(url => urls.has(url)));
}
async function input(request: Request) {
  if (!request.headers.get("content-type")?.startsWith("application/json") || !request.body) throw new Error("input");
  const reader = request.body.getReader(), chunks: Uint8Array[] = []; let n = 0;
  for (;;) { const { done, value } = await reader.read(); if (done) break; n += value.length; if (n > 100000) { await reader.cancel(); throw new Error("input"); } chunks.push(value); }
  const all = new Uint8Array(n); let offset = 0; for (const c of chunks) { all.set(c, offset); offset += c.length; }
  const parsed: unknown = JSON.parse(new TextDecoder().decode(all)); if (!object(parsed)) throw new Error("input"); return parsed;
}
type Job = { job_id: string; item_id: string; version_id: string; run_id: string; decision_revision: number; status: string; lease: string; started_at: string; result_json: string | null };
export async function researchRequest(request: Request, env: Env): Promise<Response | null> {
  const url = new URL(request.url), path = url.pathname;
  if (path !== BASE && !path.startsWith(BASE + "/")) return null;
  const supplied = request.headers.get("Authorization")?.replace(/^Bearer /, "") ?? "", expected = env.NEWS_RESEARCH_TOKEN ?? "";
  const a = new TextEncoder().encode(supplied), b = new TextEncoder().encode(expected);
  if (b.length < 32 || a.length !== b.length || !timingSafeEqual(a, b)) return reply({ error: "Unauthorised" }, 401);
  if (!env.DB) return reply({ error: "Research storage unavailable" }, 503);
  if (request.method !== "POST") return reply({ error: "Method not allowed" }, 405);
  const db = env.DB;
  try {
    const data = await input(request), now = new Date().toISOString(), day = now.slice(0, 10);
    if (path === BASE + "/heartbeat") {
      if (!["ready", "research_error"].includes(String(data.status))) return reply({ error: "Invalid runner status" }, 400);
      await db.prepare("INSERT INTO news_research_runner(id,status,checked_at,model) VALUES (1,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,checked_at=excluded.checked_at,model=excluded.model").bind(data.status, now, RESEARCH_MODEL).run();
      return reply({ ok: true });
    }
    if (path === BASE + "/claim") {
      // Claims reserve the entire attempt before research starts. SQLite serialises this
      // INSERT, enforcing the daily allowance even when independent runners overlap.
      await db.prepare("UPDATE news_research_jobs SET status='failed',error='Runner timed out; eligible for a single retry on a later day.',finished_at=? WHERE status='running' AND started_at<?").bind(now, new Date(Date.now() - 25 * 60000).toISOString()).run();
      const jobId = crypto.randomUUID(), lease = crypto.randomUUID();
      const result = await db.prepare(`INSERT INTO news_research_jobs(job_id,item_id,version_id,run_id,decision_revision,attempt,status,lease,started_at,model)
        SELECT ?,d.item_id,d.version_id,d.run_id,d.revision,
          (SELECT COUNT(*)+1 FROM news_research_jobs j WHERE j.version_id=d.version_id),'running',?,?,?
        FROM news_review_decisions d JOIN news_collection_runs r ON r.run_id=d.run_id
        WHERE d.status='selected'
          AND EXISTS (SELECT 1 FROM json_each(r.payload,'$.evidence_items') e WHERE json_extract(e.value,'$.version_id')=d.version_id AND json_extract(e.value,'$.item_id')=d.item_id)
          AND (SELECT COUNT(*) FROM news_research_jobs WHERE started_at>=?) < ?
          AND (SELECT COUNT(*) FROM news_research_jobs j WHERE j.version_id=d.version_id) < 2
          AND NOT EXISTS (SELECT 1 FROM news_research_jobs j WHERE j.version_id=d.version_id AND (j.status IN ('running','complete') OR j.started_at>=?))
        ORDER BY d.updated_at,d.item_id LIMIT 1 ON CONFLICT DO NOTHING`).bind(jobId, lease, now, RESEARCH_MODEL, day, DAILY_RESEARCH_LIMIT, day).run();
      if (!result.meta.changes) return reply({ job: null, reason: "No eligible selections or daily limit reached", daily_limit: DAILY_RESEARCH_LIMIT });
      const row = await db.prepare("SELECT j.*,r.payload,d.note FROM news_research_jobs j JOIN news_collection_runs r ON r.run_id=j.run_id JOIN news_review_decisions d ON d.item_id=j.item_id WHERE j.job_id=?").bind(jobId).first<Job & {payload:string;note:string}>();
      if (!row) throw new Error("missing job");
      const pack = JSON.parse(row.payload), candidate = pack.evidence_items.find((i: {version_id:string}) => i.version_id === row.version_id);
      return reply({ job: {job_id:jobId,lease,item_id:row.item_id,version_id:row.version_id,run_id:row.run_id,decision_revision:row.decision_revision,candidate,review_note:row.note,model:RESEARCH_MODEL} });
    }
    if (![BASE + "/complete", BASE + "/fail"].includes(path)) return reply({ error: "Not found" }, 404);
    if (!validText(data.job_id,64) || !validText(data.lease,64)) return reply({ error: "Invalid job" },400);
    const job = await db.prepare("SELECT * FROM news_research_jobs WHERE job_id=? AND lease=?").bind(data.job_id,data.lease).first<Job>();
    if (!job) return reply({ error: "Job not found" },404);
    const payload = path.endsWith("/complete") ? JSON.stringify(data.result) : null;
    if (path.endsWith("/complete") && !validResearchResult(data.result)) return reply({ error: "Invalid research result" },400);
    if (job.status !== "running") return job.status === "complete" && job.result_json === payload ? reply({ status:"complete",replayed:true }) : reply({ error:"Job already closed" },409);
    if (Date.now()-Date.parse(job.started_at)>25*60000) return reply({error:"Job lease expired"},409);
    const error = path.endsWith("/fail") ? "Research could not be completed. Check the private workflow run; one retry is allowed on a later day." : null;
    // The SQL condition checks selection again at the write, not only at the earlier read.
    await db.prepare(`UPDATE news_research_jobs SET status=CASE WHEN EXISTS
      (SELECT 1 FROM news_review_decisions d WHERE d.item_id=news_research_jobs.item_id AND d.version_id=news_research_jobs.version_id AND d.revision=news_research_jobs.decision_revision AND d.status='selected') THEN ? ELSE 'cancelled' END,
      result_json=?,error=?,finished_at=? WHERE job_id=? AND status='running'`).bind(payload ? "complete":"failed",payload,error,now,job.job_id).run();
    const finished = await db.prepare("SELECT status FROM news_research_jobs WHERE job_id=?").bind(job.job_id).first();
    return reply({status:finished?.status});
  } catch (error) {
    if (error instanceof SyntaxError || (error instanceof Error && error.message === "input")) return reply({error:"Invalid request"},400);
    console.error(JSON.stringify({event:"research_storage_failed",path}));
    return reply({error:"Research storage unavailable; no publication was performed"},503);
  }
}

export async function researchBoard(db: D1Database, itemIds: string[]) {
  const jobs = await db.prepare("SELECT job_id,item_id,version_id,decision_revision,attempt,status,started_at,finished_at,model,result_json,error FROM news_research_jobs WHERE item_id IN (SELECT value FROM json_each(?)) ORDER BY started_at DESC LIMIT 60").bind(JSON.stringify(itemIds)).all();
  const runner = await db.prepare("SELECT status,checked_at,model FROM news_research_runner WHERE id=1").first();
  const today = await db.prepare("SELECT COUNT(*) AS n FROM news_research_jobs WHERE started_at>=?").bind(new Date().toISOString().slice(0,10)).first<{n:number}>();
  return {jobs:jobs.results.map(j=>({...j,result:j.result_json ? JSON.parse(String(j.result_json)):null,result_json:undefined})),runner,daily_limit:DAILY_RESEARCH_LIMIT,today_attempts:today?.n??0};
}
