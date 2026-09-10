import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';
import { buildSync } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { requireNewsDatabaseId, validateNewsSecrets } from '../scripts/news-release.mjs';

const compiled = buildSync({ entryPoints: [fileURLToPath(new URL('../worker/news.ts', import.meta.url))], bundle: true, platform: 'node', format: 'esm', target: 'es2022', write: false }).outputFiles[0].text;
const { newsRequest } = await import('data:text/javascript;base64,' + Buffer.from(compiled).toString('base64'));
const migration = await readFile(new URL('../drizzle/0000_gray_thena.sql', import.meta.url), 'utf8');
const ingestToken = 'test-collector-key-'.repeat(3);
const editorToken = 'test-editor-key-'.repeat(3);
const origin = 'https://dal-data-ai-lab.moricz-labs.workers.dev';
const date = new Date().toISOString().slice(0, 10);

test('the local placeholder cannot become a production database binding', () => {
  for (const id of [undefined, '', '00000000-0000-4000-8000-000000000000', 'invalid']) assert.throws(() => requireNewsDatabaseId(id));
  assert.equal(requireNewsDatabaseId('12345678-1234-1234-1234-123456789abc'), '12345678-1234-1234-1234-123456789abc');
  assert.throws(() => validateNewsSecrets({ NEWS_INGEST_TOKEN: 'same'.repeat(10), NEWS_EDITOR_TOKEN: 'same'.repeat(10) }));
  assert.throws(() => validateNewsSecrets({ NEWS_INGEST_TOKEN: 'short' }));
  assert.doesNotThrow(() => validateNewsSecrets({ NEWS_INGEST_TOKEN: ingestToken, NEWS_EDITOR_TOKEN: editorToken }));
});

function database() {
  const sqlite = new DatabaseSync(':memory:');
  sqlite.exec(migration);
  const db = {
    prepare(sql) {
      const statement = sqlite.prepare(sql);
      let args = [];
      return {
        bind(...values) { args = values; return this; },
        async first() { return statement.get(...args) ?? null; },
        async all() { return { results: statement.all(...args) }; },
        async run() { const result = statement.run(...args); return { meta: { changes: Number(result.changes) }, success: true }; },
      };
    },
    async batch(statements) {
      sqlite.exec('BEGIN');
      try { const results = []; for (const statement of statements) results.push(await statement.run()); sqlite.exec('COMMIT'); return results; }
      catch (error) { sqlite.exec('ROLLBACK'); throw error; }
    },
    sqlite,
  };
  return db;
}
function request(path, payload, token) {
  return new Request(origin + path, { method: payload === undefined ? 'GET' : 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) }, body: payload === undefined ? undefined : JSON.stringify(payload) });
}
function pack(id = 'run-1') {
  return { schema_version: 1, run_summary: { run_id: id, pack_date: date, started_at: new Date().toISOString(), status: 'incomplete', item_total: 0 }, evidence_items: [], coverage_and_gaps: { warnings: ['Synthetic test data'] }, integrity_checks: {}, editorial_status: 'unreviewed', publication_approved: false };
}
function upload(content = pack(), generation = 0) {
  const pack_json = JSON.stringify(content);
  return { generation, pack_json, transport_sha256: createHash('sha256').update(pack_json).digest('hex'), state: { source_state: [['fixture', new Date().toISOString()]], identities: [], versions: [], observations: [], pack_items: [] } };
}
function edition() {
  return { date, title: 'Synthetic workflow validation edition', introduction: 'Test content only. Never publish this fixture to the real site.', evidence_run_ids: ['run-1'], stories: [{ headline: 'A fictional change for testing', facts: 'Synthetic fixture facts.', interpretation: 'Synthetic fixture interpretation.', evidence_boundary: 'Entirely synthetic; not a news report.', watch_next: 'No real-world implication.', sources: [{ title: 'Example source', url: 'https://example.org/source' }] }] };
}
function env(DB) { return { DB, NEWS_INGEST_TOKEN: ingestToken, NEWS_EDITOR_TOKEN: editorToken }; }

test('collector and editor permissions are separate and fail closed', async () => {
  const db = database();
  try {
    assert.equal((await newsRequest(request('/api/news/collector/state?table=source_state'), env(db))).status, 401);
    assert.equal((await newsRequest(request('/api/news/editor/editions/' + date + '/draft', { expected_revision: 0, edition: edition() }, ingestToken), env(db))).status, 401);
    assert.equal((await newsRequest(request('/api/news/collector/state?table=source_state', undefined, editorToken), env(db))).status, 401);
    assert.equal((await newsRequest(request('/briefing/evidence/latest.json'), {})).status, 503);
    assert.equal(await newsRequest(request('/about'), env(db)), null);
  } finally { db.sqlite.close(); }
});

test('atomic ingestion, idempotent recovery, public evidence and generation conflict', async () => {
  const db = database();
  try {
    const first = upload();
    assert.equal((await newsRequest(request('/api/news/collector/runs', first, ingestToken), env(db))).status, 201);
    assert.equal((await newsRequest(request('/api/news/collector/runs', first, ingestToken), env(db))).status, 200);
    assert.equal((await newsRequest(request('/api/news/collector/runs', upload(pack('run-2')), ingestToken), env(db))).status, 409);
    const result = await newsRequest(request('/briefing/evidence/latest.json'), env(db));
    assert.equal((await result.json()).run_summary.run_id, 'run-1');
    const state = await newsRequest(request('/api/news/collector/state?table=source_state', undefined, ingestToken), env(db));
    assert.equal((await state.json()).generation, 1);
    assert.equal(db.sqlite.prepare('SELECT COUNT(*) AS n FROM news_collection_runs').get().n, 1);
    assert.equal((await newsRequest(request('/api/news/collector/state?table=versions&generation=0', undefined, ingestToken), env(db))).status, 409);
  } finally { db.sqlite.close(); }
});

test('bad checksums, malformed state and invalid calendar dates do not enter storage', async () => {
  const db = database();
  try {
    const bad = upload(); bad.transport_sha256 = 'a'.repeat(64);
    assert.equal((await newsRequest(request('/api/news/collector/runs', bad, ingestToken), env(db))).status, 400);
    const invalid = upload(); invalid.state.versions = [['one']];
    assert.equal((await newsRequest(request('/api/news/collector/runs', invalid, ingestToken), env(db))).status, 400);
    assert.equal((await newsRequest(request('/briefing/evidence/2026-02-31.json'), env(db))).status, 400);
    assert.equal(db.sqlite.prepare('SELECT COUNT(*) AS n FROM news_ingest_generations').get().n, 0);
  } finally { db.sqlite.close(); }
});

test('publishing requires exact revision approval and editing preserves the last published copy', async () => {
  const db = database();
  try {
    await newsRequest(request('/api/news/collector/runs', upload(), ingestToken), env(db));
    const base = '/api/news/editor/editions/' + date;
    assert.equal((await newsRequest(request(base + '/draft', { expected_revision: 0, edition: edition() }, editorToken), env(db))).status, 200);
    assert.equal(db.sqlite.prepare('SELECT published_json FROM news_editions').get().published_json, null);
    assert.equal((await newsRequest(request(base + '/publish', { expected_revision: 1 }, editorToken), env(db))).status, 409);
    assert.equal((await newsRequest(request(base + '/approve', { expected_revision: 1, reviewer: 'Test reviewer' }, editorToken), env(db))).status, 200);
    assert.equal((await newsRequest(request(base + '/publish', { expected_revision: 1 }, editorToken), env(db))).status, 200);
    const original = db.sqlite.prepare('SELECT published_json FROM news_editions').get().published_json;
    const changed = edition(); changed.title = 'Unapproved correction';
    await newsRequest(request(base + '/draft', { expected_revision: 1, edition: changed }, editorToken), env(db));
    assert.equal((await newsRequest(request(base + '/publish', { expected_revision: 2 }, editorToken), env(db))).status, 409);
    assert.equal(db.sqlite.prepare('SELECT published_json FROM news_editions').get().published_json, original);
    assert.equal((await newsRequest(request(base + '/draft', { expected_revision: 1, edition: changed }, editorToken), env(db))).status, 409);
  } finally { db.sqlite.close(); }
});

test('rendered news pages show published content only and parameterised missing editions return 404', async () => {
  const db = database();
  const { default: worker } = await import('../dist/server/index.js');
  const bindings = { ...env(db), ASSETS: { fetch: async () => new Response('Not found', { status: 404 }) } };
  const ctx = { waitUntil() {} };
  try {
    await newsRequest(request('/api/news/collector/runs', upload(), ingestToken), env(db));
    const base = '/api/news/editor/editions/' + date;
    await newsRequest(request(base + '/draft', { expected_revision: 0, edition: edition() }, editorToken), env(db));
    let response = await worker.fetch(request('/news'), bindings, ctx);
    assert.equal(response.status, 200);
    assert.doesNotMatch(await response.text(), /Synthetic workflow validation edition/);
    assert.equal((await worker.fetch(request('/news/' + date), bindings, ctx)).status, 404);
    await newsRequest(request(base + '/approve', { expected_revision: 1, reviewer: 'Test reviewer' }, editorToken), env(db));
    await newsRequest(request(base + '/publish', { expected_revision: 1 }, editorToken), env(db));
    response = await worker.fetch(request('/news/' + date), bindings, ctx);
    assert.equal(response.status, 200);
    assert.match(await response.text(), /Synthetic workflow validation edition/);
    assert.equal((await worker.fetch(request('/news/2026-02-31'), bindings, ctx)).status, 404);
    response = await worker.fetch(request('/news'), bindings, ctx);
    assert.match(await response.text(), /Synthetic workflow validation edition/);
  } finally { db.sqlite.close(); }
});

test('real local Cloudflare D1 accepts the migration and atomic ingestion batch', async () => {
  const mf = new Miniflare(convertV4MiniflareOptions({ name: 'news-test', modules: true, script: compiled + '\nexport default { fetch: newsRequest };', compatibilityDate: '2026-05-15', compatibilityFlags: ['nodejs_compat'], d1Databases: ['DB'], bindings: { NEWS_INGEST_TOKEN: ingestToken, NEWS_EDITOR_TOKEN: editorToken } }));
  try {
    const db = await mf.getD1Database('DB');
    await db.batch(migration.split('--> statement-breakpoint').filter(sql => sql.trim()).map(sql => db.prepare(sql)));
    const payload = upload();
    const item = { item_id: 'fixture-item', version_id: 'fixture-version', title: 'Synthetic D1 item', canonical_url: 'https://example.org/source', collected_at: new Date().toISOString() };
    const content = JSON.parse(payload.pack_json);
    content.evidence_items = [item]; content.run_summary.item_total = 1;
    payload.pack_json = JSON.stringify(content);
    payload.transport_sha256 = createHash('sha256').update(payload.pack_json).digest('hex');
    payload.state.versions = [[item.version_id, item.item_id, 'fixture-hash', JSON.stringify(item)]];
    payload.state.identities = [['fixture-alias', item.item_id]];
    payload.state.observations = [[item.item_id, 'fixture', 'guid', item.canonical_url]];
    payload.state.pack_items = [[date, item.item_id, item.version_id]];
    let response = await mf.dispatchFetch(origin + '/api/news/collector/runs', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + ingestToken }, body: JSON.stringify(payload) });
    assert.equal(response.status, 201, await response.text());
    response = await mf.dispatchFetch(origin + '/briefing/evidence/latest.json');
    assert.equal((await response.json()).run_summary.run_id, 'run-1');
    response = await mf.dispatchFetch(origin + '/api/news/collector/state?table=source_state', { headers: { Authorization: 'Bearer ' + ingestToken } });
    assert.equal((await response.json()).rows.length, 1);
    response = await mf.dispatchFetch(origin + '/api/news/collector/state?table=versions', { headers: { Authorization: 'Bearer ' + ingestToken } });
    const recovered = await response.json();
    assert.equal(recovered.rows[0][0], item.version_id);
    assert.equal(JSON.parse(recovered.rows[0][3]).item_id, item.item_id);
    const dbCount = await db.prepare('SELECT COUNT(*) AS n FROM news_pack_items').first();
    assert.equal(dbCount.n, 1);
  } finally { await mf.dispose(); }
});
