import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
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

test("publishes the decision map with decision-led framing and metadata", async () => {
  const response = await render("/ai-business-adoption-map");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Start with the work\. Then decide where AI fits\./);
  assert.match(html, /A useful AI use case starts with a measurable business problem/);
  assert.match(html, /12 common SME workflows/);
  assert.match(html, /Workflow visualisation/);
  assert.match(html, /Watch the work change before you choose a tool/);
  assert.match(html, /Comparison mode/);
  assert.match(html, /Make the trade-offs visible/);
  assert.match(html, /Turn the route into a controlled pilot/);
  assert.match(html, /rel="canonical"/);
  assert.match(html, /ai-business-adoption-map/);
});

test("keeps the map controls and route dialog keyboard accessible", async () => {
  const component = await readFile(new URL("../app/ai-business-adoption-map/adoption-decision-map.tsx", import.meta.url), "utf8");
  const worldMap = await readFile(new URL("../app/ai-business-adoption-map/futuristic-world-map.tsx", import.meta.url), "utf8");
  const css = await readFile(new URL("../app/ai-business-adoption-map/adoption-decision-map.module.css", import.meta.url), "utf8");
  assert.match(component, /htmlFor="business-function"/);
  assert.match(component, /id="business-function"/);
  assert.match(component, /htmlFor="desired-outcome"/);
  assert.match(component, /aria-live="polite"/);
  assert.match(component, /event\.key === "Escape"/);
  assert.match(component, /closeButtonRef\.current\?\.focus\(\)/);
  assert.match(component, /document\.body\.style\.overflow = "hidden"/);
  assert.match(component, /previouslyFocused\?\.focus\(\)/);
  assert.match(component, /aria-describedby="adoption-dialog-summary"/);
  assert.match(component, /<details open>/);
  assert.match(component, /toggleCompare/);
  assert.match(component, /aria-label="Selected route comparison"/);
  assert.match(component, /workflowPulse/);
  assert.match(component, /DecisionHighwayScene/);
  assert.match(component, /PlanetScene/);
  assert.match(component, /LibraryScene/);
  assert.match(component, /ComparisonScene/);
  assert.match(component, /highwayPhoto/);
  assert.match(component, /planetPhoto/);
  assert.match(component, /libraryPhoto/);
  assert.match(component, /data-ready=/);
  assert.match(worldMap, /onPointerMove=/);
  assert.match(worldMap, /mapPhoto/);
  assert.match(worldMap, /mapGraticule/);
  assert.match(worldMap, /mapTravellers/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /highwayRoad/);
  assert.match(css, /planetSpin/);
  assert.match(css, /libraryShelf/);
  assert.match(css, /adoption-map-world\.webp/);
  assert.match(css, /adoption-map-highway\.webp/);
  assert.match(css, /adoption-map-planet\.webp/);
  assert.match(css, /adoption-map-library\.webp/);
  assert.match(css, /cinematicMapPhoto/);
  assert.match(css, /cinematicHighway/);
  assert.match(css, /cinematicPlanet/);
  assert.match(css, /cinematicLibrary/);
  assert.match(component, /Route fit:/);
  assert.match(component, /Control basis:/);
});

test("provides a compact mobile navigation instead of a clipped desktop strip", async () => {
  const shell = await readFile(new URL("../app/site-shell.tsx", import.meta.url), "utf8");
  const mobile = await readFile(new URL("../app/mobile-site-nav.tsx", import.meta.url), "utf8");
  const css = await readFile(new URL("../app/mobile-site-nav.module.css", import.meta.url), "utf8");
  assert.match(shell, /desktopNavigation/);
  assert.match(shell, /<MobileSiteNav active=\{active\}/);
  assert.match(mobile, /<details/);
  assert.match(mobile, /aria-label="Mobile navigation"/);
  assert.match(css, /@media \(max-width: 680px\)/);
  assert.match(css, /:global\(\.desktopNavigation\)/);
});
