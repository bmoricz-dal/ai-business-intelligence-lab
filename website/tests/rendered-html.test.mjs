import assert from "node:assert/strict";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: handler } = await import(workerUrl.href);
  const request = new Request(`http://localhost${path}`, {
    headers: { accept: "text/html" },
  });
  const context = {
    waitUntil() {},
    passThroughOnException() {},
  };
  return typeof handler === "function"
    ? handler(request, context)
    : handler.fetch(
        request,
        {
          ASSETS: {
            fetch: async () => new Response("Not found", { status: 404 }),
          },
        },
        context,
      );
}

test("server-renders the public five-report evidence page", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /Public evidence release - five-report foundation/);
  assert.match(html, /5 reports published · methods available/);
  assert.match(html, /The five reports/);
  assert.match(html, /Reported AI use rises with business size/);
  assert.match(html, /System integration remains limited among SME AI users/);
  assert.match(html, /Many SME AI users report no policy or guidance/);
  assert.match(html, /Research is the leading listed AI use case/);
  assert.match(html, /Operational pathways vary by measure and business size/);
  assert.match(html, /37\.4%/);
  assert.match(html, /26\.9%/);
  assert.match(html, /20\.1%/);
  assert.match(html, /53\.7%/);
  assert.match(html, /67\.7%/);
  assert.doesNotMatch(html, /private review|owner review pending|public access remains off/i);
});

test("makes About, Methods and public contact links visible", async () => {
  const response = await render();
  const html = await response.text();
  assert.match(html, />About</);
  assert.match(html, />Background</);
  assert.match(html, />Contact</);
  assert.match(html, />Purpose</);
  assert.match(html, />Values</);
  assert.match(html, /MSc with Merit in International Business Economics/);
  assert.match(html, /BSc \(Hons\) in Economics and Industrial Organisation/);
  assert.match(html, /CMI Level 7 Strategic Management/);
  assert.match(html, /benedict\.moricz@gmail\.com/);
  assert.match(html, /github\.com\/bmoricz-dal/);
  assert.match(html, /linkedin\.com\/in\/benedek-moricz/);
  assert.match(html, /Data and Methods Guide/);
  assert.match(html, /Technical Appendix/);
  assert.match(html, /GitHub evidence repository/);
  assert.match(html, /public PDFs stored in the GitHub repository/);
});

test("keeps denominators and evidence limitations explicit", async () => {
  const response = await render();
  const html = await response.text();
  assert.match(html, /A denominator is the group described by a percentage/);
  assert.match(html, /All UK businesses in each published size group/);
  assert.match(html, /UK businesses that report using AI technologies/);
  assert.match(html, /Among businesses already using AI/);
  assert.match(html, /Across all businesses/);
  assert.match(html, /Two published comparison groups, shown separately/);
  assert.match(html, /must not be added together/);
  assert.match(html, /readiness or maturity score/);
  assert.match(html, /Intervals show uncertainty/);
  assert.match(html, /respondent counts/);
});

test("includes accessible navigation, exact data and all reports", async () => {
  const response = await render();
  const html = await response.text();
  assert.match(html, /Skip to insights/);
  assert.match(html, /aria-label="Main navigation"/);
  assert.match(html, /Technology/);
  assert.match(html, /Accounting/);
  assert.match(html, /Financial services/);
  assert.match(html, /View exact values and sample bases/);
  assert.match(html, /95% interval/);
  assert.match(html, /SME_Preliminary_Report_01_AI_Use_by_Business_Size\.pdf/);
  assert.match(html, /SME_Report_02_AI_Adoption_and_System_Integration_by_Size\.pdf/);
  assert.match(html, /SME_Report_03_AI_Governance_by_Business_Size\.pdf/);
  assert.match(html, /SME_Report_04_How_UK_Businesses_Use_AI\.pdf/);
  assert.match(html, /SME_Report_05_Operational_AI_Adoption_Pathways\.pdf/);
  assert.match(html, />2,500</);
  assert.doesNotMatch(html, />2,160</);
  assert.doesNotMatch(html, /Planned report|Evidence scope identified/);
});

test("uses the light-blue expandable publication theme", async () => {
  const css = await import("node:fs/promises").then(({ readFile }) =>
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
  );
  assert.match(css, /--sky: #dff3ff/);
  assert.match(css, /--teal: #2f83c5/);
  assert.match(css, /\.navDropdown/);
  assert.match(css, /\.aboutGrid/);
  assert.match(css, /\.pathwayPanel/);
  assert.match(css, /\.methodActions/);
  assert.doesNotMatch(css, /background: var\(--navy-deep\)/);
});

test("navigation menus support hover, click, selection and pointer-leave closing", async () => {
  const component = await import("node:fs/promises").then(({ readFile }) =>
    readFile(new URL("../app/dropdown-nav.tsx", import.meta.url), "utf8"),
  );
  assert.match(component, /onMouseEnter=\{\(\) => setOpen\(true\)\}/);
  assert.match(component, /onMouseLeave=\{\(\) => setOpen\(false\)\}/);
  assert.match(component, /onClick=\{\(\) => setOpen\(\(current\) => !current\)\}/);
  assert.match(component, /onClick=\{\(\) => setOpen\(false\)\}/);
  assert.match(component, /aria-expanded=\{open\}/);
});
