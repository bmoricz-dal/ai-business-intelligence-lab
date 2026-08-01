import assert from "node:assert/strict";
import test from "node:test";

async function render(path) {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: handler } = await import(workerUrl.href);
  const request = new Request(`http://localhost${path}`, { headers: { accept: "text/html" } });
  const context = { waitUntil() {}, passThroughOnException() {} };
  return typeof handler === "function"
    ? handler(request, context)
    : handler.fetch(request, { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, context);
}

test("server-renders the accounting sector evidence page", async () => {
  const response = await render("/sectors/accounting");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /UK Accounting SMEs: AI Adoption and Operational Readiness/);
  assert.match(html, /39,860/);
  assert.match(html, /26%/);
  assert.match(html, /71\.38%/);
  assert.match(html, /secondary evidence only/i);
  assert.match(html, /not averaged/);
  assert.match(html, /Use-readiness is ahead of operations-readiness/);
  assert.match(html, /Download PDF/);
  assert.doesNotMatch(html, /survey respondents needed|primary data collection planned|draft finding/i);
});
