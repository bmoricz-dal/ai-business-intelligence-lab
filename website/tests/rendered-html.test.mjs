import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: handler } = await import(workerUrl.href);
  const request = new Request(`http://localhost${path}`, {
    headers: { accept: "text/html" },
  });
  const context = { waitUntil() {}, passThroughOnException() {} };
  return typeof handler === "function"
    ? handler(request, context)
    : handler.fetch(
        request,
        { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
        context,
      );
}

const routes = [
  ["/", "Overview"],
  ["/about", "About"],
  ["/ai-in-business", "AI in business"],
  ["/sectors", "Sectors"],
  ["/adoption-pathways", "AI in practice"],
  ["/methods", "Methods"],
  ["/sectors/accounting/benefits", "Sectors"],
  ["/adoption-pathways/accounting-micro-case-study", "AI in practice"],
];

test("serves every top-level research section as a separate page", async () => {
  for (const [path, label] of routes) {
    const response = await render(path);
    assert.equal(response.status, 200, `${path} should render`);
    assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
    const html = await response.text();
    assert.match(html, new RegExp(`aria-current="page"[^>]*>${label}<|>${label}<[^>]*aria-current="page"`));
  }
});

test("keeps headings linked to pages and restores accessible dropdown toggles", async () => {
  for (const [path] of routes) {
    const html = await (await render(path)).text();
    assert.match(html, /aria-label="Main navigation"/);
    assert.match(html, /href="\/"/);
    assert.match(html, /href="\/about"/);
    assert.match(html, /href="\/ai-in-business"/);
    assert.match(html, /href="\/sectors"/);
    assert.match(html, /href="\/adoption-pathways"/);
    assert.match(html, /href="\/methods"/);
    assert.match(html, /aria-label="Toggle About submenu"/);
    assert.match(html, /aria-label="Toggle Sectors submenu"/);
    assert.match(html, /aria-label="Toggle AI in practice submenu"/);
    assert.doesNotMatch(html, /aria-label="Toggle AI in business submenu"/);
    assert.match(html, /aria-expanded="false"/);
  }
});

test("dropdowns support hover, click, focus departure and Escape", async () => {
  const component = await readFile(new URL("../app/dropdown-nav.tsx", import.meta.url), "utf8");
  const shell = await readFile(new URL("../app/site-shell.tsx", import.meta.url), "utf8");
  assert.match(component, /className="navMenuLink"/);
  assert.match(component, /href=\{href\}/);
  assert.match(component, /onMouseEnter=\{\(\) => setOpen\(true\)\}/);
  assert.match(component, /onMouseLeave=\{\(\) => \{/);
  assert.match(component, /setOpen\(false\)/);
  assert.match(component, /onClick=\{\(\) => setOpen\(\(current\) => !current\)\}/);
  assert.match(component, /event\.key === "Escape"/);
  assert.match(component, /event\.currentTarget\.contains\(event\.relatedTarget\)/);
  assert.match(component, /className="navDropdownPanel"/);
  assert.match(component, /className="navNestedDropdown"/);
  assert.match(component, /setNestedOpen/);
  assert.match(component, /Toggle \$\{item\.label\} studies submenu/);
  assert.match(shell, /\/about#background/);
  assert.doesNotMatch(shell, /\/ai-in-business#reports/);
  assert.match(shell, /\/sectors\/accounting/);
  assert.match(shell, /\/sectors\/accounting\/benefits/);
  assert.match(shell, /\/adoption-pathways#background/);
  assert.match(shell, /\/adoption-pathways\/accounting-micro-case-study/);
});

test("provides an interactive micro-accounting adoption workspace", async () => {
  const response = await render("/adoption-pathways/accounting-micro-case-study");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /A micro practice puts AI adoption into practice/);
  assert.match(html, /Interactive adoption lab/);
  assert.match(html, /Build and test your pathway/);
  assert.match(html, /Do not enter client data/);
  assert.match(html, /Baseline versus pilot/);
  assert.match(html, /Six gates/);
  assert.match(html, /Fictional composite/);
  assert.match(html, /No promised ROI/);
  assert.match(html, /UK_Micro_Accounting_Practice_AI_Adoption_Worked_Case_2026\.pdf/);
  assert.match(html, /accounting_micro_ai_adoption_playbook_2026\.csv/);

  const component = await readFile(new URL("../app/adoption-pathways/accounting-micro-case-study/adoption-workspace.tsx", import.meta.url), "utf8");
  assert.match(component, /^"use client"/);
  assert.match(component, /useState/);
  assert.match(component, /shadow mode/i);
  assert.match(component, /gateOutcome/);
  assert.match(component, /netCapacityValue/);
  assert.match(component, /Export session/);
  assert.match(component, /Blob/);
  assert.match(component, /not sent to DAL/);
  assert.doesNotMatch(component, /fetch\(|axios|localStorage/);
});

test("publishes the accounting benefits and system-fit evidence review", async () => {
  const response = await render("/sectors/accounting/benefits");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Where AI creates measurable value in accounting work/);
  assert.match(html, /7\.5–7\.9/);
  assert.match(html, /not a UK accounting-SME benchmark/i);
  assert.match(html, /controlled augmentation/i);
  assert.match(html, /Benefits and errors coexist/);
  assert.match(html, /75%/);
  assert.match(html, /77%/);
  assert.match(html, /No ROI claim/);
  assert.match(html, /UK_Accounting_SMEs_AI_Benefits_and_System_Fit_2026\.pdf/);
  assert.match(html, /accounting_ai_benefits_system_fit_2026\.csv/);
  assert.doesNotMatch(html, /proven ROI|autonomous accounting is beneficial/i);
});

test("makes Overview the project homepage", async () => {
  const html = await (await render("/")).text();
  assert.match(html, /Clear evidence for better conversations about business AI/);
  assert.match(html, /independent research platform examining how UK SMEs adopt/);
  assert.match(html, /Make AI adoption evidence rigorous enough to trust/);
  assert.match(html, /One evidence foundation, then deeper layers/);
  assert.match(html, /Latest practical release/);
  assert.match(html, /Build a cumulative intelligence service/);
  assert.match(html, /Accounting research programme/);
  assert.match(html, /From sector readiness to evidence-led implementation/);
  assert.match(html, /Micro-practice adoption lab/);
  assert.match(html, />5<\/strong><span>general reports/);
  assert.match(html, />1<\/strong><span>cross-report synthesis/);
  assert.match(html, />3<\/strong><span>accounting research outputs/);
  assert.match(html, />1<\/strong><span>interactive adoption lab/);
});

test("keeps About and Methods transparent and independently addressable", async () => {
  const about = await (await render("/about")).text();
  assert.match(about, /Research profile/);
  assert.match(about, /MSc with Merit in International Business Economics/);
  assert.match(about, /Meaning before metrics/);
  assert.match(about, /practical business case studies/);
  assert.match(about, /technical case studies and guides/);
  assert.match(about, /benedict\.moricz@gmail\.com/);

  const methods = await (await render("/methods")).text();
  assert.match(methods, /The evidence trail is part of the product/);
  assert.match(methods, /secondary data only/i);
  assert.match(methods, /Data and Methods Guide/);
  assert.match(methods, /Reproducibility Appendix/);
  assert.match(methods, /readiness or maturity score/);
});

test("keeps the general evidence library on AI in Business", async () => {
  const html = await (await render("/ai-in-business")).text();
  assert.match(html, /The general evidence foundation/);
  assert.match(html, /Five reports examine reported AI use/);
  assert.match(html, /Reported AI use rises with business size/);
  assert.match(html, /SME system-integration estimates range/);
  assert.match(html, /micro AI users report formal or informal policy/);
  assert.match(html, /Research is the leading listed use case/);
  assert.match(html, /Integration and guidance are more common/);
  assert.match(html, /37\.4%/);
  assert.match(html, /50\.8%/);
  assert.match(html, /57\.1%/);
  assert.match(html, /78\.2%/);
  assert.match(html, /SME_Cross_Report_Synthesis_AI_Adoption_and_Operationalisation\.pdf/);
});

test("gives sectors and adoption pathways dedicated evidence pages", async () => {
  const sectors = await (await render("/sectors")).text();
  assert.match(sectors, /Sector research/);
  assert.match(sectors, /The first sector report combines adoption/);
  assert.match(sectors, /39,860/);
  assert.match(sectors, /Technology/);
  assert.match(sectors, /Financial services/);
  assert.match(sectors, /href="\/sectors\/accounting"/);

  const pathways = await (await render("/adoption-pathways")).text();
  assert.match(pathways, /AI adoption is not one linear journey/);
  assert.match(pathways, /id="background"/);
  assert.match(pathways, /System integration/);
  assert.match(pathways, /Automated decision-making/);
  assert.match(pathways, /Policy or guidance/);
  assert.match(pathways, /In-house development/);
  assert.match(pathways, /26\.9%/);
  assert.match(pathways, /67\.7%/);
});

test("uses the shared DAL multi-page publication theme and generated share card", async () => {
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  const layout = await readFile(new URL("../app/layout.tsx", import.meta.url), "utf8");
  const shell = await readFile(new URL("../app/site-shell.tsx", import.meta.url), "utf8");
  const shareCard = await readFile(new URL("../public/og.png", import.meta.url));
  assert.match(css, /--black: #0b0d0f/);
  assert.match(css, /--white: #ffffff/);
  assert.match(css, /--sky: #dff3ff/);
  assert.match(css, /\.pageSiteHeader/);
  assert.match(css, /\.pageNavigation/);
  assert.match(css, /\.navMenuLink/);
  assert.match(css, /\.navMenuToggle/);
  assert.match(css, /\.pageHero/);
  assert.match(css, /\.pathwayPageTable/);
  assert.match(layout, /\/og\.png/);
  assert.match(shell, /aria-current/);
  assert.ok(shareCard.length > 100_000, "share image should be a full-resolution asset");
  assert.doesNotMatch(css, /--yellow|#f6c95c|#fff6d7/i);
  assert.doesNotMatch(css, /background: var\(--navy-deep\)/);
});
