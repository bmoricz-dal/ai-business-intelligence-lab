import { timingSafeEqual } from "node:crypto";
import { rankPack, type EvidencePack } from "./review-ranking";

type ReviewEnv = Pick<Cloudflare.Env, "DB"> & { NEWS_REVIEW_TOKEN?: string };
const BASE = "/api/news/review";
const privateHeaders = { "Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow, noarchive", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY" };
const reply = (data: unknown, status = 200, extra = {}) => Response.json(data, { status, headers: { ...privateHeaders, ...extra } });
const hash = async (s: string) => Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s))), b => b.toString(16).padStart(2, "0")).join("");
function equal(a: string, b: string) { const x = new TextEncoder().encode(a), y = new TextEncoder().encode(b); return x.length === y.length && timingSafeEqual(x, y); }
function cookieName(url: URL) { return url.protocol === "https:" ? "__Host-dal_review" : "dal_review_local"; }
function cookie(url: URL, value: string, age: number) { return `${cookieName(url)}=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${age}${url.protocol === "https:" ? "; Secure" : ""}`; }
async function readBody(request: Request) {
  if (!request.headers.get("content-type")?.startsWith("application/json")) throw new Error("body");
  const reader = request.body?.getReader(); if (!reader) throw new Error("body");
  const chunks: Uint8Array[] = []; let size = 0;
  for (;;) { const part = await reader.read(); if (part.done) break; size += part.value.length; if (size > 8192) { await reader.cancel(); throw new Error("body"); } chunks.push(part.value); }
  const bytes = new Uint8Array(size); let offset = 0; for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  const value = JSON.parse(new TextDecoder().decode(bytes));
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("body");
  return value as Record<string, unknown>;
}
function html(loggedIn: boolean, local: boolean) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>DAL · Private story review</title><link rel="stylesheet" href="/editorial-review.css"><script src="/editorial-review.js" defer></script></head><body><a href="#main" class="skip">Skip to review</a><header class="masthead"><a href="/editorial/review" class="brand">DAL<span>DATA &amp; AI LAB</span></a><span class="private">PRIVATE EDITORIAL DESK</span>${loggedIn ? '<button id="logout" class="quiet">Sign out</button>' : ''}</header><main id="main">${local ? '<p class="warning">LOCAL PREVIEW · Decisions are saved only in this preview database. Production is unchanged.</p>' : ''}<p class="eyebrow">SOURCE REVIEW · BEFORE ANALYSIS</p><h1>Find the stories<br>worth understanding.</h1><p class="intro">Review the evidence, weigh the business implications, and choose what deserves deeper research.</p><p id="message" role="status" aria-live="polite"></p>${loggedIn ? '<section class="workflow-note">Selecting a story starts an editorial decision. It does not trigger AI analysis, approve an edition or publish anything.</section><section class="toolbar"><label>Collection<select id="runs"></select></label><button id="older" class="quiet">Load older collections</button><button id="refresh" class="quiet">Refresh evidence</button></section><section id="collection" aria-label="Collection health"></section><details class="method"><summary>How reading priority works</summary><p>Transparent rules score collected titles and excerpts, not verified facts. AI / governance (18), implementation (18), economics / outcomes (20), enterprise / adoption (14), UK / SME signals (18), evidence available to review (12). Missing detail, routine releases, consumer features, recaps and promotional claims lose points. Publisher fame adds no points.</p><p>The shortlist contains up to eight story groups scoring at least 35/100. Scores are reading priorities, not the charter’s final editorial score. Vendor figures earn attention only as claims to investigate. No independent research or AI analysis has happened at this stage. Related headlines are suggestions, not corroboration.</p></details><section class="toolbar filters"><label>Find a candidate<input id="search" type="search" placeholder="Search title, source or excerpt"></label><label>Decision<select id="filter"><option value="all">All candidates</option><option value="selected">Selected for analysis</option><option value="needs_review">Needs review</option><option value="rejected">Rejected</option></select></label><p id="counts"></p></section><section id="shortlist" aria-label="Ranked shortlist"></section><details id="remaining"><summary id="remaining-label">Remaining candidates</summary><div id="lower"></div></details><p class="footnote">Decision changes are saved to the review database. Updated source versions need a fresh decision. Ranking and selection never change the public evidence pack or /news.</p>' : '<section class="login"><h2>Open your private review desk</h2><p>Use the separate review access key. This key can select stories, but cannot collect sources or publish news.</p><form id="login"><label for="access-key">Review access key</label><input id="access-key" name="key" type="password" autocomplete="current-password" required maxlength="256"><button type="submit">Open review desk</button></form><p class="footnote">Your session lasts up to eight hours. The key is not kept in browser storage.</p></section>'}</main><footer>DAL NEWS <span>Evidence first. Judgement stays human.</span></footer></body></html>`;
}
type Decision = { item_id: string; version_id: string; run_id: string; status: string; revision: number; note: string; updated_at: string };
export async function reviewRequest(request: Request, env: ReviewEnv): Promise<Response | null> {
  const url = new URL(request.url), path = url.pathname;
  if (path !== "/editorial/review" && path !== BASE && !path.startsWith(BASE + "/")) return null;
  if (url.protocol !== "https:" && !["localhost", "127.0.0.1"].includes(url.hostname)) return reply({ error: "Secure connection required" }, 403);
  const page = path === "/editorial/review";
  if (request.method !== "GET" && request.method !== "POST") return reply({ error: "Method not allowed" }, 405);
  if (request.method === "POST" && (request.headers.get("Origin") !== url.origin || request.headers.get("Sec-Fetch-Site") === "cross-site")) return reply({ error: "Same-origin request required" }, 403);
  if (!env.NEWS_REVIEW_TOKEN || env.NEWS_REVIEW_TOKEN.length < 32 || !env.DB) return reply({ error: "Private review is not configured" }, 503);
  try {
    if (path === BASE + "/login" && request.method === "POST") {
      const input = await readBody(request);
      if (typeof input.key !== "string" || input.key.length > 256 || !equal(input.key, env.NEWS_REVIEW_TOKEN)) return reply({ error: "Access key not recognised" }, 401);
      const session = crypto.randomUUID() + crypto.randomUUID();
      const sessionHash = await hash(env.NEWS_REVIEW_TOKEN + ":" + session);
      const now = new Date().toISOString(), expires = new Date(Date.now() + 8 * 3600000).toISOString();
      await env.DB.batch([
        env.DB.prepare("DELETE FROM news_review_sessions WHERE expires_at<=?").bind(now),
        env.DB.prepare("INSERT INTO news_review_sessions(session_hash,expires_at) VALUES (?,?)").bind(sessionHash, expires),
      ]);
      return reply({ ok: true }, 200, { "Set-Cookie": cookie(url, session, 8 * 3600) });
    }
    const raw = request.headers.get("Cookie")?.split(";").map(p => p.trim()).find(p => p.startsWith(cookieName(url) + "="))?.slice(cookieName(url).length + 1);
    const sessionHash = raw && raw.length <= 100 ? await hash(env.NEWS_REVIEW_TOKEN + ":" + raw) : null;
    const session = sessionHash ? await env.DB.prepare("SELECT session_hash FROM news_review_sessions WHERE session_hash=? AND expires_at>?").bind(sessionHash, new Date().toISOString()).first() : null;
    if (page && request.method === "GET") return new Response(html(!!session, ["localhost", "127.0.0.1"].includes(url.hostname)), { headers: { ...privateHeaders, "Content-Type": "text/html; charset=utf-8", "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'" } });
    if (!session) return reply({ error: "Sign in to private review" }, 401);
    if (path === BASE + "/logout" && request.method === "POST") {
      await env.DB.prepare("DELETE FROM news_review_sessions WHERE session_hash=?").bind(sessionHash).run();
      return reply({ ok: true }, 200, { "Set-Cookie": cookie(url, "", 0) });
    }
    if (path === BASE + "/runs" && request.method === "GET") {
      const offset = Number(url.searchParams.get("offset") ?? 0);
      if (!Number.isSafeInteger(offset) || offset < 0 || offset > 100000) return reply({ error: "Invalid collection cursor" }, 400);
      const result = await env.DB.prepare("SELECT run_id,pack_date,started_at,status FROM news_collection_runs ORDER BY started_at DESC,run_id DESC LIMIT 31 OFFSET ?").bind(offset).all();
      return reply({ runs: result.results.slice(0, 30), next_offset: result.results.length > 30 ? offset + 30 : null });
    }
    const runId = url.searchParams.get("run");
    if (path === BASE + "/board" && request.method === "GET") {
      if (!runId || runId.length > 64) return reply({ error: "Choose a collection" }, 400);
      const row = await env.DB.prepare("SELECT payload FROM news_collection_runs WHERE run_id=?").bind(runId).first<{ payload: string }>();
      if (!row) return reply({ error: "Collection not found" }, 404);
      const pack = JSON.parse(row.payload) as EvidencePack;
      const ranked = rankPack(pack);
      const ids = JSON.stringify(pack.evidence_items.map(i => i.item_id));
      const decisions = await env.DB.prepare("SELECT item_id,version_id,run_id,status,revision,note,updated_at FROM news_review_decisions WHERE item_id IN (SELECT value FROM json_each(?))").bind(ids).all<Decision>();
      return reply({ summary: pack.run_summary, coverage: pack.coverage_and_gaps, ...ranked, decisions: decisions.results });
    }
    if (path === BASE + "/decision" && request.method === "POST") {
      const input = await readBody(request);
      if (!["selected", "rejected", "needs_review"].includes(String(input.status)) || !Number.isSafeInteger(input.expected_revision) || Number(input.expected_revision) < 0 || typeof input.note !== "string" || input.note.length > 1500 || typeof input.run_id !== "string" || input.run_id.length > 64 || typeof input.item_id !== "string" || typeof input.version_id !== "string") return reply({ error: "Invalid decision" }, 400);
      const row = await env.DB.prepare("SELECT payload FROM news_collection_runs WHERE run_id=?").bind(input.run_id).first<{ payload: string }>();
      if (!row) return reply({ error: "Collection not found" }, 404);
      const pack = JSON.parse(row.payload) as EvidencePack;
      const candidate = rankPack(pack).candidates.find(i => i.item_id === input.item_id && i.version_id === input.version_id);
      if (!candidate) return reply({ error: "Candidate version not in this collection" }, 400);
      // Decisions refer to exact evidence versions. Never silently carry a selection to changed evidence.
      const ranking = JSON.stringify({ score: candidate.score, factors: candidate.factors, ranking_version: candidate.ranking_version });
      const updated = new Date().toISOString();
      const expected = Number(input.expected_revision);
      const result = expected === 0
        ? await env.DB.prepare("INSERT INTO news_review_decisions(item_id,version_id,run_id,status,revision,note,ranking_json,updated_at) VALUES (?,?,?,?,1,?,?,?) ON CONFLICT DO NOTHING").bind(candidate.item_id, candidate.version_id, input.run_id, input.status, input.note, ranking, updated).run()
        : await env.DB.prepare("UPDATE news_review_decisions SET version_id=?,run_id=?,status=?,revision=revision+1,note=?,ranking_json=?,updated_at=? WHERE item_id=? AND revision=?").bind(candidate.version_id, input.run_id, input.status, input.note, ranking, updated, candidate.item_id, expected).run();
      if (!result.meta.changes) return reply({ error: "This decision changed in another session. Refresh before saving." }, 409);
      return reply({ item_id: candidate.item_id, version_id: candidate.version_id, run_id: input.run_id, status: input.status, revision: expected + 1, note: input.note, updated_at: updated });
    }
    if (path === BASE + "/history" && request.method === "GET") {
      const item = url.searchParams.get("item"); if (!item || item.length > 64) return reply({ error: "Invalid item" }, 400);
      const history = await env.DB.prepare("SELECT version_id,run_id,status,revision,note,ranking_json,updated_at FROM news_review_events WHERE item_id=? ORDER BY revision DESC LIMIT 20").bind(item).all();
      return reply({ events: history.results });
    }
    return reply({ error: "Not found" }, 404);
  } catch (error) {
    if (error instanceof SyntaxError || (error instanceof Error && error.message === "body")) return reply({ error: "Invalid or oversized JSON request" }, 400);
    console.error(JSON.stringify({ event: "private_review_failed", path }));
    return reply({ error: "Review service unavailable. Your decision has not been confirmed; refresh before retrying." }, 503);
  }
}
