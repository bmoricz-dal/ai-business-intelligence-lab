import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { DatabaseSync } from 'node:sqlite';
import { buildSync } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { Miniflare, convertV4MiniflareOptions } from 'miniflare';
import { validateNewsSecrets } from '../scripts/news-release.mjs';
const compile = path => buildSync({ entryPoints: [fileURLToPath(new URL(path, import.meta.url))], bundle:true, platform:'node', format:'esm', target:'es2022', write:false }).outputFiles[0].text;
const moduleFor = async path => import('data:text/javascript;base64,'+Buffer.from(compile(path)).toString('base64'));
const { reviewRequest } = await moduleFor('../worker/review.ts');
const { rankItem, rankPack } = await moduleFor('../worker/review-ranking.ts');
const { newsRequest } = await moduleFor('../worker/news.ts');
const migrations = await Promise.all((await readdir(new URL('../drizzle/',import.meta.url))).filter(f=>f.endsWith('.sql')).sort().map(f=>readFile(new URL('../drizzle/'+f,import.meta.url),'utf8')));
const origin='https://dal-data-ai-lab.moricz-labs.workers.dev';
const key='review-test-only-'.repeat(4);
const ingest='collector-test-only-'.repeat(4);
const editor='publisher-test-only-'.repeat(4);
function db() {
 const sqlite=new DatabaseSync(':memory:'); for(const m of migrations) sqlite.exec(m);
 return {sqlite,prepare(sql){const s=sqlite.prepare(sql);let args=[];return {bind(...a){args=a;return this},async first(){return s.get(...args)??null},async all(){return {results:s.all(...args)}},async run(){const r=s.run(...args);return {meta:{changes:Number(r.changes)},success:true}}}},async batch(statements){sqlite.exec('BEGIN');try{const out=[];for(const s of statements)out.push(await s.run());sqlite.exec('COMMIT');return out}catch(e){sqlite.exec('ROLLBACK');throw e}}};
}
function item(overrides={}) {return {item_id:'item-a',version_id:'version-a',title:'AI adoption by UK small businesses cuts invoice processing costs by 25%',source_name:'Example source',source_id:'example',source_excerpt:'A detailed customer study describes how small businesses deployed an invoice workflow, reporting a 25% cost reduction. The measurement method needs review.',canonical_url:'https://example.com/evidence',published_at:'2026-09-10T10:00:00Z',primary_source:true,evidence_cautions:{vendor_origin:true,corroboration_needed:true},...overrides};}
function pack(items=[item()],run='run-a') {return {run_summary:{run_id:run,pack_date:'2026-09-10',started_at:'2026-09-10T12:00:00Z',status:'incomplete',source_total:1,source_ok:0,source_failed:0,item_total:items.length},evidence_items:items,coverage_and_gaps:{sources:[{source_id:'example',name:'Example',status:'partial',issues:['Freshness warning']}],search_only:['Independent research needed']},publication_approved:false,editorial_status:'unreviewed'};}
function seed(database,p=pack()){database.sqlite.prepare('INSERT INTO news_collection_runs VALUES (?,?,?,?,?,?)').run(p.run_summary.run_id,'2026-09-10',p.run_summary.started_at,'incomplete','fixture',JSON.stringify(p));database.sqlite.prepare('INSERT OR REPLACE INTO news_daily_packs VALUES (?,?)').run('2026-09-10',p.run_summary.run_id);}
const env=database=>({DB:database,NEWS_REVIEW_TOKEN:key,NEWS_INGEST_TOKEN:ingest,NEWS_EDITOR_TOKEN:editor});
function req(path,body,cookie,headers={}){return new Request(origin+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',Origin:origin,...(cookie?{Cookie:cookie}:{}),...headers},body:body===undefined?undefined:JSON.stringify(body)})}
async function login(e){const r=await reviewRequest(req('/api/news/review/login',{key}),e);assert.equal(r.status,200);return r.headers.get('set-cookie').split(';')[0]}
const decision=(overrides={})=>({run_id:'run-a',item_id:'item-a',version_id:'version-a',expected_revision:0,status:'selected',note:'Check the measured denominator.',...overrides});

test('ranking rewards meaningful business evidence, not publisher fame or minor launches',()=>{
 const useful=rankItem(item());const trivial=rankItem(item({title:'Release 5.17.0',source_excerpt:'',source_name:'OpenAI'}));
 assert.ok(useful.score>=60);assert.equal(trivial.score,0);
 assert.equal(rankItem(item({source_name:'OpenAI',source_id:'openai'})).score,rankItem(item({source_name:'Unknown publisher',source_id:'unknown'})).score);
 assert.ok(rankItem(item({title:'New football features in Search',source_excerpt:'An illustrated football trophy.'})).score<useful.score);
 const global=rankItem(item({title:'An enterprise model',source_excerpt:'This model is available around the world. It is a new model offering with an enterprise interface.'}));
 assert.equal(global.factors.find(f=>f.label==='UK / SME relevance').points,0);
 assert.equal(useful.corroboration_needed,true);assert.match(useful.factors.find(f=>f.label==='Economics / outcomes').reason,/claim.*not proof/);
 assert.ok(rankItem(item({title:'Revolutionary AI for everyone'})).factors.some(f=>f.points<0));
});
test('grouping is conservative, preserves every candidate and never boosts repeated claims',()=>{
 const a=item(), b=item({item_id:'b',version_id:'b',canonical_url:a.canonical_url+'?utm_source=email'}), c=item({item_id:'c',title:'Deploying a new inference model',canonical_url:'https://example.com/other'});
 const ranked=rankPack(pack([a,b,c]));assert.equal(ranked.groups.length,2);assert.equal(ranked.groups[0].related.length,1);assert.equal(ranked.candidates.length,3);assert.equal(ranked.groups[0].lead.score,rankItem(a).score);
 const releases=rankPack(pack([item({title:'Release 5.17.0',canonical_url:'https://github.com/a/5',item_id:'one'}),item({title:'Release 5.18.0',canonical_url:'https://github.com/a/6',item_id:'two'})]));assert.equal(releases.groups.length,2);
 const overlap=rankPack(pack([item({title:'UK invoice automation reduces processing costs in small firms',item_id:'one'}),item({title:'UK invoice automation reduces processing costs for small firms',canonical_url:'https://other.com/report',item_id:'two'})]));assert.equal(overlap.groups.length,1);assert.match(overlap.groups[0].related[0].reason,/potentially related/);
 assert.equal(rankPack(pack([])).groups.length,0);
 assert.equal(rankPack(pack(Array.from({length:10},(_,i)=>item({item_id:String(i),title:'Distinct business study '+i,canonical_url:'https://example.com/'+i})))).groups.filter(g=>g.shortlisted).length,8);
});
test('private pages and all APIs fail closed, including forged identity headers and publication tokens',async()=>{
 const d=db();try{seed(d);const e=env(d);const r=await reviewRequest(req('/editorial/review'),e);const html=await r.text();assert.match(html,/Open your private review desk/);assert.ok(!html.includes('25%'));assert.match(r.headers.get('cache-control'),/no-store/);assert.match(r.headers.get('content-security-policy'),/frame-ancestors 'none'/);assert.match(r.headers.get('x-robots-tag'),/noindex/);
 for(const path of ['/api/news/review/runs','/api/news/review/board?run=run-a','/api/news/review/history?item=item-a']){assert.equal((await reviewRequest(req(path,undefined,undefined,{Authorization:'Bearer '+editor,'oai-authenticated-user-email':'owner@example.com'}),e)).status,401)}
 assert.equal((await reviewRequest(req('/api/news/review/decision',decision()),e)).status,401);
 assert.equal((await reviewRequest(req('/api/news/review/login',{key:ingest}),e)).status,401);
 assert.equal((await reviewRequest(req('/api/news/review/login',{key:editor}),e)).status,401);
 assert.equal((await reviewRequest(req('/editorial/review'),{DB:d})).status,503);
 assert.equal(await reviewRequest(req('/news'),e),null);
 }finally{d.sqlite.close()}
});
test('session cookies are secure, hashed, expiring, revocable and invalidated by key rotation',async()=>{
 const d=db();try{seed(d);const e=env(d);const response=await reviewRequest(req('/api/news/review/login',{key}),e);const full=response.headers.get('set-cookie');assert.match(full,/HttpOnly/);assert.match(full,/Secure/);assert.match(full,/SameSite=Strict/);const c=full.split(';')[0];assert.ok(!d.sqlite.prepare('SELECT * FROM news_review_sessions').get().session_hash.includes(c.split('=')[1]));
 assert.equal((await reviewRequest(req('/api/news/review/runs',undefined,c),e)).status,200);
 assert.equal((await reviewRequest(req('/api/news/review/runs',undefined,c),{...e,NEWS_REVIEW_TOKEN:'rotated-'.repeat(8)})).status,401);
 await reviewRequest(req('/api/news/review/logout',{},c),e);assert.equal((await reviewRequest(req('/api/news/review/runs',undefined,c),e)).status,401);
 const expired=await login(e);d.sqlite.exec("UPDATE news_review_sessions SET expires_at='2000-01-01'");assert.equal((await reviewRequest(req('/api/news/review/runs',undefined,expired),e)).status,401);
 }finally{d.sqlite.close()}
});
test('cross-origin writes, malformed bodies, wrong versions and oversized notes are rejected',async()=>{
 const d=db();try{seed(d);const e=env(d),c=await login(e);
 for(const path of ['login','logout','decision']) assert.equal((await reviewRequest(req('/api/news/review/'+path,decision(),c,{Origin:'https://attacker.example'}),e)).status,403);
 for(const change of [{status:'published'},{expected_revision:-1},{note:'x'.repeat(1501)},{version_id:'made-up'},{item_id:'made-up'}]) assert.equal((await reviewRequest(req('/api/news/review/decision',decision(change),c),e)).status,400);
 assert.equal((await reviewRequest(req('/api/news/review/login',{key:'a'.repeat(9000)}),e)).status,400);
 const missingOrigin=req('/api/news/review/decision',decision(),c);missingOrigin.headers.delete('Origin');assert.equal((await reviewRequest(missingOrigin,e)).status,403);
 }finally{d.sqlite.close()}
});
test('decisions persist across sessions, reject stale saves, and append history atomically',async()=>{
 const d=db();try{seed(d);const e=env(d),c=await login(e);assert.equal((await reviewRequest(req('/api/news/review/decision',decision(),c),e)).status,200);
 assert.equal((await reviewRequest(req('/api/news/review/decision',decision({status:'rejected'}),c),e)).status,409);
 const fresh=await login(e);const b=await(await reviewRequest(req('/api/news/review/board?run=run-a',undefined,fresh),e)).json();assert.equal(b.decisions[0].status,'selected');assert.equal(b.decisions[0].note,'Check the measured denominator.');
 assert.equal((await reviewRequest(req('/api/news/review/decision',decision({status:'rejected',expected_revision:1}),fresh),e)).status,200);
 assert.equal((await reviewRequest(req('/api/news/review/decision',decision({status:'needs_review',expected_revision:2}),fresh),e)).status,200);
 const history=await(await reviewRequest(req('/api/news/review/history?item=item-a',undefined,fresh),e)).json();assert.deepEqual(history.events.map(x=>x.revision),[3,2,1]);assert.equal(history.events[2].status,'selected');assert.ok(JSON.parse(history.events[0].ranking_json).factors.length>3);
 }finally{d.sqlite.close()}
});
test('changed versions retain the old decision without promoting the new version or publishing',async()=>{
 const d=db();try{seed(d);const e=env(d),c=await login(e);await reviewRequest(req('/api/news/review/decision',decision(),c),e);
 seed(d,pack([item({version_id:'version-b',source_excerpt:'Updated source claims with new caveats.'})],'run-b'));
 const b=await(await reviewRequest(req('/api/news/review/board?run=run-b',undefined,c),e)).json();assert.equal(b.decisions[0].version_id,'version-a');assert.equal(b.candidates[0].version_id,'version-b');
 assert.equal(d.sqlite.prepare('SELECT COUNT(*) AS n FROM news_editions').get().n,0);
 const publicPack=await(await newsRequest(req('/briefing/evidence/latest.json'),e)).json();assert.equal(publicPack.publication_approved,false);assert.ok(!JSON.stringify(publicPack).includes('Check the measured denominator.'));
 assert.equal((await newsRequest(req('/api/news/editor/editions/2026-09-10/publish',{expected_revision:1},c),e)).status,401);
 assert.equal((await newsRequest(req('/api/news/collector/runs',{},c),e)).status,401);
 }finally{d.sqlite.close()}
});
test('collection browsing supports pagination, empty collections, missing runs and visible source warnings',async()=>{
 const d=db();try{const e=env(d),c=await login(e);assert.deepEqual((await(await reviewRequest(req('/api/news/review/runs',undefined,c),e)).json()).runs,[]);
 for(let i=0;i<32;i++)seed(d,pack([],'run-'+String(i).padStart(2,'0')));
 const first=await(await reviewRequest(req('/api/news/review/runs',undefined,c),e)).json();assert.equal(first.runs.length,30);assert.equal(first.next_offset,30);
 const second=await(await reviewRequest(req('/api/news/review/runs?offset=30',undefined,c),e)).json();assert.equal(second.runs.length,2);assert.equal(second.next_offset,null);
 assert.equal((await reviewRequest(req('/api/news/review/board?run=missing',undefined,c),e)).status,404);
 const b=await(await reviewRequest(req('/api/news/review/board?run=run-01',undefined,c),e)).json();assert.equal(b.groups.length,0);assert.equal(b.coverage.sources[0].issues[0],'Freshness warning');
 }finally{d.sqlite.close()}
});
test('new review secret must be distinct and existing two-secret release files remain valid',()=>{
 assert.doesNotThrow(()=>validateNewsSecrets({NEWS_INGEST_TOKEN:ingest,NEWS_EDITOR_TOKEN:editor}));
 assert.doesNotThrow(()=>validateNewsSecrets({NEWS_INGEST_TOKEN:ingest,NEWS_EDITOR_TOKEN:editor,NEWS_REVIEW_TOKEN:key}));
 assert.throws(()=>validateNewsSecrets({NEWS_INGEST_TOKEN:ingest,NEWS_EDITOR_TOKEN:editor,NEWS_REVIEW_TOKEN:editor}));
});
test('browser code keeps source text out of HTML sinks and secrets out of browser storage',async()=>{
 const js=await readFile(new URL('../public/editorial-review.js',import.meta.url),'utf8');
 assert.ok(!/innerHTML|outerHTML|insertAdjacentHTML|localStorage\.|sessionStorage\./.test(js));assert.match(js,/textContent/);assert.match(js,/noopener noreferrer/);
 const d=db();try{seed(d,pack([item({title:'<script>alert(1)</script>'})]));const e=env(d),c=await login(e);const html=await(await reviewRequest(req('/editorial/review',undefined,c),e)).text();assert.ok(!html.includes('<script>alert'));assert.ok(!html.includes(key));}finally{d.sqlite.close()}
});
test('real Cloudflare D1 applies additive review migration and atomic history triggers',async()=>{
 const mf=new Miniflare(convertV4MiniflareOptions({modules:true,script:'export default { fetch(){return new Response("ok")} }',compatibilityDate:'2026-05-15',d1Databases:{DB:'review-tests'}}));
 try{const database=await mf.getD1Database('DB');for(const m of migrations)for(const sql of m.split('--> statement-breakpoint'))if(sql.trim())await database.prepare(sql).run();
 const e=env(database), p=pack();await database.prepare('INSERT INTO news_collection_runs VALUES (?,?,?,?,?,?)').bind('run-a','2026-09-10','2026-09-10T12:00:00Z','incomplete','fixture',JSON.stringify(p)).run();
 const c=await login(e);assert.equal((await reviewRequest(req('/api/news/review/decision',decision(),c),e)).status,200);
 assert.equal((await database.prepare('SELECT COUNT(*) AS n FROM news_review_events').first()).n,1);
 assert.equal((await database.prepare('SELECT COUNT(*) AS n FROM news_editions').first()).n,0);
 }finally{await mf.dispose()}
});

test('built production Worker routes the private review before public rendering without leaking decisions',async()=>{
 const {default:worker}=await import('../dist/server/index.js');const d=db();
 try{seed(d);const e={...env(d),ASSETS:{fetch:async()=>new Response('Not found',{status:404})}},ctx={waitUntil(){},passThroughOnException(){}};
 const anonymous=await worker.fetch(req('/editorial/review?_rsc=1'),e,ctx);assert.equal(anonymous.status,200);assert.match(await anonymous.text(),/Open your private review desk/);
 const loginResponse=await worker.fetch(req('/api/news/review/login',{key}),e,ctx);const c=loginResponse.headers.get('set-cookie').split(';')[0];
 const board=await worker.fetch(req('/api/news/review/board?run=run-a',undefined,c),e,ctx);assert.equal((await board.json()).candidates.length,1);
 assert.equal((await worker.fetch(req('/api/news/review/decision',decision(),c),e,ctx)).status,200);
 const publicNews=await(await worker.fetch(req('/news'),e,ctx)).text();assert.match(publicNews,/first brief is in preparation/);assert.ok(!publicNews.includes('Check the measured denominator.'));assert.ok(!publicNews.includes('UK small businesses cuts'));
 }finally{d.sqlite.close()}
});
