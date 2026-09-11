/** Deterministic reading priority, not verified editorial merit or publication approval. */
export const RANKING_VERSION = "dal-reading-priority-1";
export type EvidenceItem = {
  item_id: string; version_id: string; title: string; source_name: string; source_id: string;
  source_excerpt?: string; canonical_url: string; published_at?: string; effective_at?: string;
  primary_source?: boolean; geography?: string; item_type?: string;
  evidence_cautions?: { vendor_origin?: boolean; preprint?: boolean; prerelease?: boolean; corroboration_needed?: boolean };
};
export type EvidencePack = {
  run_summary: { run_id: string; pack_date: string; started_at: string; finished_at?: string; status: string; source_total: number; source_ok: number; source_failed: number; item_total: number };
  evidence_items: EvidenceItem[];
  coverage_and_gaps: { sources: { source_id: string; name: string; status: string; issues: string[]; latest_source_item_at?: string }[]; warnings?: string[]; search_only?: string[] };
};
type Factor = { label: string; points: number; max: number; reason: string };
const normal = (s: string) => s.normalize("NFKC").toLowerCase().replace(/[‐‑–—]/g, "-");
const clean = (s = "") => s.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
export function rankItem(item: EvidenceItem) {
  const excerpt = clean(item.source_excerpt).slice(0, 1000);
  const title = normal(item.title);
  const text = normal(item.title + " " + excerpt);
  const vendor = item.evidence_cautions?.vendor_origin === true;
  const factors: Factor[] = [];
  const add = (label: string, points: number, max: number, reason: string) => factors.push({ label, points, max, reason });
  const governance = /\b(regulation|regulatory|governance|policy|legislation|compliance|privacy|pii|audit\w*|cyber defense|cybersecurity)\b/.test(text);
  const capability = /\b(model|models|agents?|llms?|inference|reasoning|evaluation|benchmark|multimodal|voice|embeddings?|ai)\b/.test(text);
  add("AI capability / governance", governance ? 18 : capability ? 12 : 0, 18, governance ? "Governance, privacy or policy signal in the collected text." : capability ? "A capability or evaluation signal; its significance still needs verification." : "No clear capability or governance signal in this excerpt.");
  const implementation = /\b(deploy\w*|integration|workflow|how to|walkthrough|provisioning|quantization|caching|detector|evaluation|serving|implementation|orchestration|prototyp\w*|operational data)\b/.test(text);
  const practical = /\b(how to|walkthrough|learn how|end-to-end|configur\w*|provisioning|how it works|when to use)\b/.test(text);
  add("Implementation", implementation ? (practical ? 18 : 12) : 0, 18, implementation ? (practical ? "Describes a concrete implementation method or workflow." : "Implementation detail is signalled; inspect the actual method.") : "No concrete implementation method signalled.");
  const economic = /\b(cost\w*|productivity|latency|throughput|cold starts|efficien\w*|time sav\w*|license fees|pricing|payments|per query|delays|concurrent users|performance)\b/.test(text);
  const measured = /\d+(?:\.\d+)?\s*(?:%|x\b|times\b)|\b(?:minutes to seconds|days to hours|hours to minutes)\b/.test(text);
  add("Economics / outcomes", economic || measured ? (measured ? (vendor ? 14 : 20) : 12) : 0, 20, measured ? (vendor ? "A vendor numerical or time-saving claim is present, capped at 14; this is a claim to check, not proof." : "A numerical or time-saving claim is present; this is a claim to check, not proof.") : economic ? "A cost, performance or operational outcome mechanism is signalled." : "No explicit economic or measured outcome signal.");
  const enterprise = /\b(enterprise|business|company|customer|operational|production|financial services|workbench|teams?|managers|crm|rfi|company data|investment|airline|government\w*)\b/.test(text);
  const adoption = /\b(customer story|prototyped|built(?!-)|uses|adopt\w*|operational data)\b/.test(text);
  add("Enterprise / adoption", enterprise ? (adoption ? 14 : 10) : adoption ? 5 : 0, 14, enterprise ? (adoption ? "A named use case or adoption example is described; outcomes remain unverified." : "A business or public-sector use case is explicit.") : adoption ? "An application is described, but business transfer is unclear." : "No explicit enterprise or adoption context.");
  const uk = /\b(uk|u\.k\.|united kingdom|british|britain|smes?|small businesses|small business|small firms)\b/.test(text);
  const smallTeam = /\bsmall team\b/.test(text);
  add("UK / SME relevance", uk ? 18 : smallTeam ? 8 : 0, 18, uk ? "Explicit UK or small-business context; check scope and applicability." : smallTeam ? "Small-team constraints may transfer to SME implementation; this is not UK / SME outcome evidence." : "No explicit UK / SME evidence. Global availability does not establish local relevance.");
  const primary = item.primary_source === true;
  add("Evidence available to review", excerpt.length >= 80 ? (primary ? (vendor ? 6 : 10) : 4) : 0, 12, excerpt.length < 80 ? "Too little excerpt detail to assess the claim." : primary ? (vendor ? "Source-owned vendor account only; independent corroboration needed." : "Classified as a primary source, but item authorship and claims still need checking.") : "Provenance is not established as primary evidence.");
  if (!excerpt || excerpt.length < 80) add("Thin evidence", -10, 0, "Missing or very short excerpt; open the original before judging relevance.");
  if (/^(?:release\s+)?v?\d+\.\d+/.test(title)) add("Routine release", -20, 0, "A version-number announcement provides no demonstrated material change.");
  if (/\b(football|next big race|sports|wallpaper|celebrity)\b/.test(title)) add("Consumer feature", -25, 0, "Consumer-interest framing without an evidenced business implication.");
  if (/\b(icymi|recap|roundup|round-up|what landed)\b/.test(title)) add("Recap", -12, 0, "An aggregation or recap may repeat older developments.");
  if (/\b(revolutionary|game-changing|game changing|unprecedented|everyone|best ever)\b/.test(title)) add("Promotional framing", -8, 0, "Promotional language is not evidence of materiality.");
  if (item.evidence_cautions?.prerelease || item.evidence_cautions?.preprint) add("Preliminary", -6, 0, "Pre-release or preprint evidence needs extra validation.");
  const score = Math.max(0, Math.min(100, factors.reduce((sum, f) => sum + f.points, 0)));
  return { ...item, source_excerpt: excerpt, score, factors, ranking_version: RANKING_VERSION,
    summary: excerpt || "No usable source excerpt was collected. Open the source before making a decision.",
    relevance: factors.filter(f => f.points >= 10).map(f => f.reason).slice(0, 3).join(" ") || "Limited DAL relevance is visible in the available metadata; manual inspection may reveal more.",
    provenance: primary ? (vendor ? "Primary / vendor" : "Primary classification — unverified") : "Primary status unconfirmed",
    corroboration_needed: vendor || !primary || item.evidence_cautions?.corroboration_needed === true,
  };
}
const stop = new Set("a an and are as at be by for from how in into is it its more new now of on or our the their this to using with ai amazon openai google nvidia build introducing learn".split(" "));
const tokens = (s: string) => new Set(normal(s).match(/[a-z0-9]+/g)?.filter(t => t.length > 2 && !stop.has(t)) ?? []);
function canonical(s: string) {
  try { const u = new URL(s); u.hash = ""; for (const k of [...u.searchParams.keys()]) if (/^(utm_|fbclid|gclid)/.test(k)) u.searchParams.delete(k); return u.toString().replace(/\/$/, ""); } catch { return s; }
}
function relation(a: EvidenceItem, b: EvidenceItem): string | null {
  if (canonical(a.canonical_url) === canonical(b.canonical_url)) return "Same canonical source link";
  // Version numbers and different quantified claims must not collapse into one headline group.
  if (/^(?:release\s+)?v?\d+\.\d+/.test(normal(a.title)) || /^(?:release\s+)?v?\d+\.\d+/.test(normal(b.title))) return null;
  const numbersA = a.title.match(/\d+(?:\.\d+)*/g)?.join(","), numbersB = b.title.match(/\d+(?:\.\d+)*/g)?.join(",");
  if (numbersA && numbersB && numbersA !== numbersB) return null;
  if (normal(a.title) === normal(b.title)) return "Matching headline — verify that these refer to the same event";
  const x = tokens(a.title), y = tokens(b.title);
  const shared = [...x].filter(t => y.has(t)).length;
  return shared >= 3 && shared / (x.size + y.size - shared) >= 0.6 ? "Strong headline overlap — potentially related, not verified duplicates" : null;
}
export function rankPack(pack: EvidencePack) {
  const candidates = pack.evidence_items.map(rankItem).sort((a, b) => b.score - a.score || a.item_id.localeCompare(b.item_id));
  const groups: { id: string; lead: ReturnType<typeof rankItem>; related: { candidate: ReturnType<typeof rankItem>; reason: string }[]; shortlisted: boolean }[] = [];
  for (const candidate of candidates) {
    const match = groups.map(group => ({ group, reason: relation(group.lead, candidate) })).find(x => x.reason);
    if (match) match.group.related.push({ candidate, reason: match.reason! });
    else groups.push({ id: candidate.item_id, lead: candidate, related: [], shortlisted: false });
  }
  groups.forEach((g, i) => { g.shortlisted = i < 8 && g.lead.score >= 35; });
  return { ranking_version: RANKING_VERSION, candidates, groups };
}
