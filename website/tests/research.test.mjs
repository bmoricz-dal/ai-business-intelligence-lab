import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {DatabaseSync} from 'node:sqlite';
import {buildSync} from 'esbuild';
import {fileURLToPath} from 'node:url';
const compile=p=>buildSync({entryPoints:[fileURLToPath(new URL(p,import.meta.url))],bundle:true,platform:'node',format:'esm',write:false}).outputFiles[0].text;
const load=async p=>import('data:text/javascript;base64,'+Buffer.from(compile(p)).toString('base64'));
const {researchRequest,validResearchResult}=await load('../worker/research.ts');
const {newsRequest}=await load('../worker/news.ts');
const migrations=await Promise.all((await readdir(new URL('../drizzle/',import.meta.url))).filter(f=>f.endsWith('.sql')).sort().map(f=>readFile(new URL('../drizzle/'+f,import.meta.url),'utf8')));
const token='research-test-'.repeat(4),origin='https://dal-data-ai-lab.moricz-labs.workers.dev';
function db() {
 const sqlite=new DatabaseSync(':memory:');
 for(const m of migrations) sqlite.exec(m);
 return {sqlite, prepare(sql) {
   const s=sqlite.prepare(sql); let a=[];
   return {
     bind(...v){a=v;return this},
     async first(){return s.get(...a)??null},
     async all(){return {results:s.all(...a)}},
     async run(){return {meta:{changes:Number(s.run(...a).changes)}}}
   };
 }};
}
function seed(d,n=1){const items=Array.from({length:n},(_,i)=>({item_id:'item'+i,version_id:'version'+i,canonical_url:'https://example.com/'+i,title:'AI enterprise implementation '+i}));d.sqlite.prepare('INSERT INTO news_collection_runs VALUES (?,?,?,?,?,?)').run('run','2026-09-11',new Date().toISOString(),'complete','hash',JSON.stringify({evidence_items:items}));for(const i of items)d.sqlite.prepare('INSERT INTO news_review_decisions VALUES (?,?,?,?,?,?,?,?)').run(i.item_id,i.version_id,'run','selected',1,'','{}',new Date().toISOString());}
function req(action,data={},auth=token){return new Request(origin+'/api/news/research/'+action,{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+auth},body:JSON.stringify(data)})}
const env=d=>({DB:d,NEWS_RESEARCH_TOKEN:token,NEWS_INGEST_TOKEN:'ingest-'.repeat(8),NEWS_EDITOR_TOKEN:'editor-'.repeat(8)});
const result=()=>({schema_version:1,model:'codex-chatgpt',publication_approved:false,editorial_status:'awaiting_human_review',summary:'Summary',facts:'Attributed facts',interpretation:'Proposed inference',evidence_boundary:'Not independently corroborated',watch_next:'Check outcomes',sources:[{title:'Source',url:'https://example.com/0'}],claims:[{claim:'Vendor statement',assessment:'source_reported',source_urls:['https://example.com/0']}]});
const claim=async e=>(await(await researchRequest(req('claim'),e)).json()).job;
test('research auth is separate from review, ingest and publishing and cannot publish',async()=>{const d=db();try{seed(d);const e=env(d);for(const key of ['',e.NEWS_INGEST_TOKEN,e.NEWS_EDITOR_TOKEN])assert.equal((await researchRequest(req('claim',{},key),e)).status,401);const r=await researchRequest(req('claim'),e);assert.equal(r.status,200);assert.match(r.headers.get('cache-control'),/no-store/);const publish=new Request(origin+'/api/news/editor/editions/2026-09-11/publish',{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:'{"expected_revision":1}'});assert.equal((await newsRequest(publish,e)).status,401);}finally{d.sqlite.close()}});
test('only exact selected versions are claimed, once, with an atomic daily budget',async()=>{const d=db();try{seed(d,9);const e=env(d);d.sqlite.exec("UPDATE news_review_decisions SET status='rejected' WHERE item_id='item0'; UPDATE news_review_decisions SET version_id='changed' WHERE item_id='item1'");const jobs=await Promise.all(Array.from({length:8},()=>claim(e)));assert.equal(jobs.filter(Boolean).length,6);assert.equal(new Set(jobs.filter(Boolean).map(j=>j.version_id)).size,6);assert.ok(!jobs.filter(Boolean).some(j=>['item0','item1'].includes(j.item_id)));assert.equal(d.sqlite.prepare('SELECT COUNT(*) n FROM news_editions').get().n,0);}finally{d.sqlite.close()}});
test('completed drafts persist privately, have bounded citations, and are idempotent',async()=>{const d=db();try{seed(d);const e=env(d),job=await claim(e);const data={job_id:job.job_id,lease:job.lease,result:result()};assert.equal((await researchRequest(req('complete',{...data,lease:'wrong'}),e)).status,404);assert.equal((await researchRequest(req('complete',{...data,result:{...result(),publication_approved:true}}),e)).status,400);assert.equal((await researchRequest(req('complete',{job_id:job.job_id,lease:job.lease}),e)).status,400);assert.equal((await researchRequest(req('complete',data),e)).status,200);assert.equal((await(await researchRequest(req('complete',data),e)).json()).replayed,true);assert.equal(await claim(e),null);assert.equal(d.sqlite.prepare('SELECT COUNT(*) n FROM news_editions').get().n,0);assert.equal(d.sqlite.prepare('SELECT status FROM news_research_jobs').get().status,'complete');assert.equal(validResearchResult({...result(),claims:[{claim:'Bad',assessment:'source_reported',source_urls:['https://wrong.example/a']}]}),false);}finally{d.sqlite.close()}});
test('rejecting or editing a selection during research cancels its completion',async()=>{const d=db();try{seed(d);const e=env(d),job=await claim(e);d.sqlite.exec("UPDATE news_review_decisions SET status='rejected',revision=2");const r=await researchRequest(req('complete',{job_id:job.job_id,lease:job.lease,result:result()}),e);assert.equal((await r.json()).status,'cancelled');assert.equal(d.sqlite.prepare('SELECT COUNT(*) n FROM news_editions').get().n,0);}finally{d.sqlite.close()}});
test('failed attempts do not loop or evade the daily allowance; one later-day retry is possible',async()=>{const d=db();try{seed(d);const e=env(d),job=await claim(e);await researchRequest(req('fail',{job_id:job.job_id,lease:job.lease}),e);assert.equal(await claim(e),null);d.sqlite.exec("UPDATE news_research_jobs SET started_at='2026-01-01T00:00:00Z'");const retry=await claim(e);assert.ok(retry);assert.notEqual(retry.job_id,job.job_id);await researchRequest(req('fail',{job_id:retry.job_id,lease:retry.lease}),e);d.sqlite.exec("UPDATE news_research_jobs SET started_at='2026-01-01T00:00:00Z'");assert.equal(await claim(e),null);}finally{d.sqlite.close()}});
