import test from 'node:test';
import assert from 'node:assert/strict';
import {api,validateResult} from '../research-desk.mjs';
const url='https://example.com/source';
const job={candidate:{canonical_url:url}};
const result=()=>({schema_version:1,model:'codex-chatgpt',publication_approved:false,editorial_status:'awaiting_human_review',summary:'Summary',facts:'Attributed fact',interpretation:'DAL inference',evidence_boundary:'Uncorroborated vendor claim',watch_next:'Check',sources:[{title:'Source',url}],claims:[{claim:'A product was announced.',assessment:'source_reported',source_urls:[url]}],verification:{method:'codex_web_source_review',checked_at:new Date().toISOString(),opened_urls:[url]}});
test('validates private source-backed drafts and rejects uncited or unopened support',()=>{
 assert.equal(validateResult(result(),job).publication_approved,false);
 for(const alter of [r=>r.publication_approved=true,r=>r.claims[0].source_urls=['https://fabricated.example/a'],r=>r.verification.opened_urls=[],r=>r.sources[0].url='javascript:alert(1)',r=>r.editorial_status='published']) {const r=result();alter(r);assert.throws(()=>validateResult(r,job));}
});
test('research credential can only travel to fixed DAL origin and limited actions',async()=>{
 let request;
 const fetcher=async(url,init)=>{request={url,init};return new Response('{"job":null}')};
 await api('claim',{},'test-'.repeat(8),fetcher);
 assert.equal(request.url,'https://dal-data-ai-lab.moricz-labs.workers.dev/api/news/research/claim');
 assert.equal(request.init.redirect,'error');
 await assert.rejects(api('publish',{},'test-'.repeat(8),fetcher));
 await assert.rejects(api('//attacker.example',{},'test-'.repeat(8),fetcher));
});
