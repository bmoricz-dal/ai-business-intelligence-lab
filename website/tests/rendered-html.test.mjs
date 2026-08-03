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
  ["/sectors/accounting", "Sectors"],
  ["/sectors/accounting/benefits", "Sectors"],
  ["/sectors/accounting/adoption-journeys", "Sectors"],
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
  assert.match(shell, /\/sectors\/accounting\/adoption-journeys/);
  assert.match(shell, /\/adoption-pathways#background/);
  assert.match(shell, /\/adoption-pathways\/accounting-micro-case-study/);
});

test("keeps dropdown panels visible at compact desktop widths", async () => {
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(css, /@media \(min-width: 681px\) and \(max-width: 1100px\)/);
  assert.match(css, /\.pageNavigation \{[\s\S]*?flex-wrap: wrap;[\s\S]*?overflow: visible;/);
  assert.match(css, /\.pageNavigation \.navNestedDropdown \{[\s\S]*?position: static;/);
  assert.doesNotMatch(css, /@media \(max-width: 1100px\)[\s\S]{0,220}\.pageNavigation \{[^}]*overflow-x: auto;/);
});

test("integrates reliable section navigation and varied motion scenes", async () => {
  const experience = await readFile(new URL("../app/editorial-experience.tsx", import.meta.url), "utf8");
  const shell = await readFile(new URL("../app/site-shell.tsx", import.meta.url), "utf8");
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");

  assert.match(experience, /createPortal/);
  assert.match(experience, /pageSectionNavigator/);
  assert.match(experience, /Explore this page/);
  assert.match(experience, /window\.history\.replaceState/);
  assert.match(experience, /scrollIntoView/);
  assert.match(experience, /usePathname/);
  assert.match(experience, /\[pathname\]/);
  assert.doesNotMatch(experience, /Page outline|editorialOutline/);
  assert.match(shell, /pageSectionNavigatorMount/);
  assert.match(shell, /export function SignalScene/);
  assert.match(shell, /export function LandscapeStory/);
  assert.match(shell, /"network" \| "ledger" \| "flow" \| "horizon" \| "provenance"/);
  assert.match(shell, /"city" \| "water" \| "highlands" \| "coast"/);
  assert.match(css, /\.pageSectionNavigator/);
  assert.match(css, /\.signalScene--ledger/);
  assert.match(css, /\.signalScene--horizon/);
  assert.match(css, /\.landscapeStory/);
  assert.match(css, /animation-timeline: view\(\)/);
  assert.match(css, /@keyframes landscapeScroll/);
  assert.match(css, /prefers-reduced-motion: reduce/);
});

test("sustains visual storytelling beyond the opening hero on every public route", async () => {
  for (const [path] of routes) {
    const html = await (await render(path)).text();
    assert.match(
      html,
      /landscapeStory|cityAerialStory|cinematicInterlude/,
      `${path} should include a mid-page environmental visual chapter`,
    );
  }

  const accounting = await (await render("/sectors/accounting")).text();
  const benefits = await (await render("/sectors/accounting/benefits")).text();
  const journeys = await (await render("/sectors/accounting/adoption-journeys")).text();
  const lab = await (await render("/adoption-pathways/accounting-micro-case-study")).text();
  assert.match(accounting, /manchester-skyline-cc-by\.jpg/);
  assert.match(benefits, /esthwaite-water-aerial-cc-by\.jpg/);
  assert.match(journeys, /scottish-highlands-cc-by\.jpg/);
  assert.match(lab, /felixstowe-aerial-cc-by\.jpg/);
  assert.match(lab, /John Fielding \/ CC BY 2\.0/);
});

test("provides a connected accounting-cycle test drive and secondary adoption planner", async () => {
  const response = await render("/adoption-pathways/accounting-micro-case-study");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Accounting AI Experience Lab/);
  assert.match(html, /Take one fictional client through an AI-enabled accounting cycle/);
  assert.match(html, /Synthetic work only/);
  assert.match(html, /Cedar Interiors Ltd/);
  assert.match(html, /Capture source records/);
  assert.match(html, />Bookkeeping</);
  assert.match(html, />Ledger</);
  assert.match(html, />Close</);
  assert.match(html, />Accounts</);
  assert.match(html, />Insights</);
  assert.match(html, />Review</);
  assert.match(html, /Accounting cycle control room/);
  assert.match(html, /Workflow mechanics/);
  assert.match(html, /Plan how your firm would test adoption/);
  assert.match(html, /Do not enter client data/);
  assert.match(html, /Baseline versus pilot/);
  assert.match(html, /Six gates/);
  assert.match(html, /fictional composite/i);
  assert.match(html, /promised ROI/i);
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

  const experience = await readFile(new URL("../app/adoption-pathways/accounting-micro-case-study/experience-workspace.tsx", import.meta.url), "utf8");
  assert.match(experience, /^"use client"/);
  assert.match(experience, /sourceDocuments/);
  assert.match(experience, /transactionDecisions/);
  assert.match(experience, /Categorise and post/);
  assert.match(experience, /Reconcile and close/);
  assert.match(experience, /Prepare management accounts/);
  assert.match(experience, /Explain business movements/);
  assert.match(experience, /Inspect quality and audit trail/);
  assert.match(experience, /wrong-client test/i);
  assert.match(experience, /Known-case alignment/);
  assert.match(experience, /Synthetic profit and loss/);
  assert.match(experience, /source-linked insight/i);
  assert.match(experience, /completeStage/);
  assert.match(experience, /experienceCockpit/);
  assert.match(experience, /SIMULATION ONLINE/);
  assert.match(experience, /REVIEW-FIRST MODE/);
  assert.match(experience, /data-active-stage=\{active\}/);
  assert.match(experience, /deterministic fictional accounting workflow/i);
  assert.doesNotMatch(experience, /fetch\(|axios|localStorage/);

  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(css, /\.experienceCockpit/);
  assert.match(css, /@keyframes cockpitPanelIn/);
  assert.match(css, /prefers-reduced-motion: reduce/);
});

test("publishes the accounting benefits and system-fit evidence review", async () => {
  const response = await render("/sectors/accounting/benefits");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /AI creates the clearest value inside controlled accounting workflows/);
  assert.match(html, /7\.5–7\.9/);
  assert.match(html, /not a UK accounting-SME benchmark/i);
  assert.match(html, /controlled augmentation/i);
  assert.match(html, /Higher average accuracy does not remove error risk/);
  assert.match(html, /75%/);
  assert.match(html, /77%/);
  assert.match(html, /No ROI claim/);
  assert.match(html, /UK_Accounting_SMEs_AI_Benefits_and_System_Fit_2026\.pdf/);
  assert.match(html, /accounting_ai_benefits_system_fit_2026\.csv/);
  assert.doesNotMatch(html, /proven ROI|autonomous accounting is beneficial/i);
});

test("presents accounting AI adoption journeys with evidence boundaries", async () => {
  const response = await render("/sectors/accounting/adoption-journeys");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Accounting AI Adoption Journeys/);
  assert.match(html, /Follow the workflow change—not the product announcement/);
  assert.match(html, /Integrated AI bookkeeping platform/);
  assert.match(html, /Love Your Accountants/);
  assert.match(html, /Audit-firm implementation pattern/);
  assert.match(html, /\+17\.5 percentage points/);
  assert.match(html, /10–15 hours per week/);
  assert.match(html, /self-reported/i);
  assert.match(html, /not one company/i);
  assert.match(html, /Earlier digital change reveals implementation patterns—not AI outcomes/);
  assert.match(html, /Alfa Accountants \/ Beta/);
  assert.match(html, /Hudson Accountants/);
  assert.match(html, /No DAL survey/);
  assert.match(html, /No pooled ROI or vendor ranking/);
  assert.match(html, /accounting_ai_adoption_journeys_2026\.csv/);
  assert.match(html, /Accounting AI Experience Lab/);
  assert.doesNotMatch(html, /guaranteed ROI|proves AI reduces staff/i);
});

test("makes Overview the project homepage", async () => {
  const html = await (await render("/")).text();
  assert.match(html, /See where SME AI adoption is real—and where the evidence stops/);
  assert.match(html, /decision-ready intelligence on AI use/);
  assert.match(html, /Turn fragmented AI evidence into decisions leaders can defend/);
  assert.match(html, /Start broad\. Go sector-deep\. Test what changes in practice/);
  assert.match(html, /Accounting AI Experience Lab · latest release/);
  assert.match(html, /Build the evidence base from adoption signals to measured business value/);
  assert.match(html, /Accounting research programme/);
  assert.match(html, /One accounting programme\. Four questions leaders need answered/);
  assert.match(html, /Accounting AI Experience Lab/);
  assert.match(html, />5<\/strong><span>general reports/);
  assert.match(html, />1<\/strong><span>cross-report synthesis/);
  assert.match(html, />4<\/strong><span>accounting programme outputs/);
  assert.match(html, />Journeys</);
  assert.match(html, />1<\/strong><span>interactive adoption lab/);
});

test("keeps About and Methods transparent and independently addressable", async () => {
  const about = await (await render("/about")).text();
  assert.match(about, /Research profile/);
  assert.match(about, /MSc with Merit in International Business Economics/);
  assert.match(about, /Five values\. One standard: make every insight worth discovering\./);
  assert.match(about, />Truth</);
  assert.match(about, />Clarity</);
  assert.match(about, />Craft</);
  assert.match(about, />Agency</);
  assert.match(about, />Progress</);
  assert.match(about, /practical business cases/);
  assert.match(about, /technical guides/);
  assert.match(about, /benedict\.moricz@gmail\.com/);

  const methods = await (await render("/methods")).text();
  assert.match(methods, /Evidence is only useful when the trail remains visible/);
  assert.match(methods, /secondary data only/i);
  assert.match(methods, /Data and Methods Guide/);
  assert.match(methods, /Reproducibility Appendix/);
  assert.match(methods, /readiness or maturity score/);
});

test("keeps the general evidence library on AI in Business", async () => {
  const html = await (await render("/ai-in-business")).text();
  assert.match(html, /AI use is expanding faster than operational depth/);
  assert.match(html, /Five reports track reported use/);
  assert.match(html, /Scale remains the clearest dividing line/);
  assert.match(html, /One report per scene\. One decision signal at a time\./);
  assert.match(html, /Tool use does not mean system integration/);
  assert.match(html, /Guidance remains uneven/);
  assert.match(html, /Research is the leading listed use case at every size/);
  assert.match(html, /Integration and guidance are more visible than deeper automation/);
  assert.match(html, /Access is not the same as operational depth/);
  assert.match(html, /37\.4%/);
  assert.match(html, /50\.8%/);
  assert.match(html, /57\.1%/);
  assert.match(html, /78\.2%/);
  assert.match(html, /25\.9%/);
  assert.match(html, /53\.7%/);
  assert.match(html, /SME_Report_01_AI_Use_by_Business_Size\.pdf/);
  assert.match(html, /SME_Report_02_AI_Adoption_and_System_Integration_by_Size\.pdf/);
  assert.match(html, /SME_Report_03_AI_Governance_by_Business_Size\.pdf/);
  assert.match(html, /SME_Report_04_How_UK_Businesses_Use_AI\.pdf/);
  assert.match(html, /SME_Report_05_Operational_AI_Adoption_Pathways\.pdf/);
  assert.match(html, /SME_Cross_Report_Synthesis_AI_Adoption_and_Operationalisation\.pdf/);

  const deck = await readFile(new URL("../app/ai-in-business/report-story-deck.tsx", import.meta.url), "utf8");
  assert.match(deck, /^"use client"/);
  assert.match(deck, /useState/);
  assert.match(deck, /aria-pressed/);
  assert.match(deck, /aria-selected/);
  assert.match(deck, /UK businesses already reporting AI use/);
  assert.match(deck, /All UK businesses in each size group/);
});

test("gives sectors and adoption pathways dedicated evidence pages", async () => {
  const sectors = await (await render("/sectors")).text();
  assert.match(sectors, /Sector research/);
  assert.match(sectors, /The accounting programme connects a five-dimension readiness study/);
  assert.match(sectors, /39,860/);
  assert.match(sectors, /Technology/);
  assert.match(sectors, /Financial services/);
  assert.match(sectors, /href="\/sectors\/accounting"/);

  const sectorsSource = await readFile(new URL("../app/sectors/page.tsx", import.meta.url), "utf8");
  assert.match(sectorsSource, /import Link from "next\/link"/);
  assert.match(sectorsSource, /<Link className="lightButton" href="\/sectors\/accounting" scroll>/);

  const pathways = await (await render("/adoption-pathways")).text();
  assert.match(pathways, /AI adoption is a portfolio of operating choices—not a maturity ladder/);
  assert.match(pathways, /id="background"/);
  assert.match(pathways, /System integration/);
  assert.match(pathways, /Automated decision-making/);
  assert.match(pathways, /Policy or guidance/);
  assert.match(pathways, /In-house development/);
  assert.match(pathways, /26\.9%/);
  assert.match(pathways, /67\.7%/);
  assert.match(pathways, /Four ways AI enters a workflow—and the controls each one needs/);
  assert.match(pathways, /Controlled task assistance/);
  assert.match(pathways, /AI inside an existing system/);
  assert.match(pathways, /Bounded workflow execution/);
  assert.match(pathways, /Approved organisational knowledge/);
  assert.match(pathways, /A control layer—not a final stage/);
  assert.match(pathways, /Accounting Experience Lab then makes the change visible/);
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
  assert.match(css, /\.heroSignalConsole/);
  assert.match(css, /\.programmeConsole/);
  assert.match(css, /\.readinessConsole/);
  assert.match(css, /\.journeyExplorer/);
  assert.match(css, /\.reportStorySlide/);
  assert.match(css, /\.synthesisOrbit/);
  assert.match(css, /\.experienceCockpit/);
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(css, /\.pathwayPageTable/);
  assert.match(layout, /\/og\.png/);
  assert.match(layout, /width: 1662, height: 946/);
  assert.match(shell, /aria-current/);
  assert.ok(shareCard.length > 100_000, "share image should be a full-resolution asset");
  assert.doesNotMatch(css, /--yellow|#f6c95c|#fff6d7/i);
  assert.doesNotMatch(css, /background: var\(--navy-deep\)/);
});
