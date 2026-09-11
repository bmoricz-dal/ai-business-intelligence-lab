/** Limited research transport. Deliberately has no approval, publication or AI billing client. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const ORIGIN = 'https://dal-data-ai-lab.moricz-labs.workers.dev';
export function validUrl(value) {
  try {const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&u.hostname.includes('.')&&!u.hostname.endsWith('.local')&&!u.hostname.endsWith('.localhost')&&!/^[\d.:\[\]]+$/.test(u.hostname);}catch{return false;}
}
export function validateResult(result, job) {
  if (!result || result.schema_version!==1 || result.model!=='codex-chatgpt' || result.publication_approved!==false || result.editorial_status!=='awaiting_human_review') throw Error('Research must remain an unapproved draft.');
  for(const k of ['summary','facts','interpretation','evidence_boundary','watch_next']) if(typeof result[k]!=='string'||!result[k].trim()||result[k].length>6000) throw Error('Missing or oversized '+k);
  if(!Array.isArray(result.sources)||!result.sources.length||result.sources.length>20||!result.sources.every(s=>typeof s.title==='string'&&s.title.length>0&&s.title.length<=300&&validUrl(s.url))) throw Error('Invalid source links.');
  const urls=new Set(result.sources.map(s=>s.url));
  if(!urls.has(job.candidate.canonical_url)) throw Error('Include the selected primary source, and state any access limitation.');
  if(!Array.isArray(result.claims)||!result.claims.length||result.claims.length>12) throw Error('A claim-by-claim evidence check is required.');
  for(const c of result.claims) if(typeof c.claim!=='string'||!c.claim.trim()||c.claim.length>1200||!['source_reported','multiple_sources','unresolved'].includes(c.assessment)||!Array.isArray(c.source_urls)||c.source_urls.length>8||(c.assessment!=='unresolved'&&!c.source_urls.length)||!c.source_urls.every(u=>urls.has(u))) throw Error('A claim has invalid or missing source references.');
  if(!result.verification || result.verification.method!=='codex_web_source_review'||!Number.isFinite(Date.parse(result.verification.checked_at))||!Array.isArray(result.verification.opened_urls)||!result.verification.opened_urls.every(validUrl)) throw Error('Record the actual source review method, date and opened URLs.');
  for(const c of result.claims) if(c.assessment!=='unresolved'&&!c.source_urls.every(u=>result.verification.opened_urls.includes(u))) throw Error('Supported claims must point to sources actually opened.');
  if(!result.verification.opened_urls.includes(job.candidate.canonical_url)&&result.claims.some(c=>c.assessment!=='unresolved'&&c.source_urls.includes(job.candidate.canonical_url))) throw Error('Do not imply an inaccessible primary page was checked.');
  if(Buffer.byteLength(JSON.stringify(result))>85000) throw Error('Research result exceeds upload limit.');
  return result;
}
export async function api(action, payload, token, fetcher=fetch) {
  if(!['claim','complete','fail','heartbeat'].includes(action)) throw Error('Unsupported research action.');
  if(typeof token!=='string'||token.length<32) throw Error('Configure the separate NEWS_RESEARCH_TOKEN.');
  const r=await fetcher(ORIGIN+'/api/news/research/'+action,{method:'POST',redirect:'error',signal:AbortSignal.timeout(45000),headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!r.ok) throw Error('Research service returned HTTP '+r.status+'; success is not confirmed.');
  const reader=r.body.getReader(),chunks=[];let n=0;
  for(;;){const {done,value}=await reader.read();if(done)break;n+=value.length;if(n>250000){await reader.cancel();throw Error('Oversized response.');}chunks.push(Buffer.from(value));}
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}
async function main() {
  const [action,...args]=process.argv.slice(2),options={};
  for(let i=0;i<args.length;i+=2){if(!['--secrets-file','--output','--job','--result'].includes(args[i])||!args[i+1])throw Error('Invalid research command options.');options[args[i]]=args[i+1];}
  let token=process.env.NEWS_RESEARCH_TOKEN;
  if(options['--secrets-file']) token=JSON.parse(await fs.readFile(options['--secrets-file'],'utf8')).NEWS_RESEARCH_TOKEN;
  if(action==='claim') {
    if(!options['--output'])throw Error('Choose a private output file before claiming work.');
    // Fail before reserving if output already exists: never lose a running lease.
    await fs.mkdir(path.dirname(options['--output']),{recursive:true});
    const handle=await fs.open(options['--output'],'wx',0o600);
    try {
      await api('heartbeat',{status:'ready'},token);
      const data=await api('claim',{},token);await handle.writeFile(JSON.stringify(data,null,2)+'\n');
      const {lease,...publicJob}=data.job??{};void lease;
      console.log(JSON.stringify(data.job?{job:publicJob}:{job:null,reason:data.reason},null,2));
    }finally{await handle.close();}
  } else if(action==='complete'||action==='fail') {
    if(!options['--job'])throw Error('Supply the saved job file.');
    const {job}=JSON.parse(await fs.readFile(options['--job'],'utf8'));if(!job)throw Error('No claimed job in this file.');
    const payload={job_id:job.job_id,lease:job.lease};
    if(action==='complete') {
      if(!options['--result'])throw Error('Supply the reviewed research JSON file.');
      payload.result=validateResult(JSON.parse(await fs.readFile(options['--result'],'utf8')),job);
    }
    const response=await api(action,payload,token);
    await fs.writeFile(options['--job']+'.receipt.json',JSON.stringify({checked_at:new Date().toISOString(),job_id:job.job_id,...response},null,2)+'\n',{mode:0o600});
    console.log(JSON.stringify(response));
  } else if(action==='heartbeat') console.log(JSON.stringify(await api(action,{status:'ready'},token)));
  else throw Error('Use claim, complete, fail or heartbeat.');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(e=>{console.error(e.message);process.exitCode=1;});
