import { readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

export const siteRoot = fileURLToPath(new URL('../../', import.meta.url));
export const productionOrigin = 'https://dal-data-ai-lab.moricz-labs.workers.dev';
export async function routes() {
  return (await readdir(new URL('../../app/', import.meta.url), { recursive: true }))
    .filter(path => /(^|\/)page\.tsx$/.test(path))
    .map(path => '/' + path.replace(/(^|\/)page\.tsx$/, '')).sort();
}
export async function render(path, headers = {}, assets) {
  const { default: worker } = await import('../../dist/server/index.js');
  return worker.fetch(new Request(productionOrigin + path, { headers }), {
    ASSETS: { fetch: assets ?? (async () => new Response('Not found', { status: 404 })) },
  }, { waitUntil() {}, passThroughOnException() {} });
}
export function decode(value) {
  return value.replace(/&#(x[\da-f]+|\d+);/gi, (_, code) => String.fromCodePoint(code[0].toLowerCase() === 'x' ? parseInt(code.slice(1), 16) : Number(code)))
    .replaceAll('&amp;', '&').replaceAll('&quot;', '"').replaceAll('&#39;', "'").replaceAll('&lt;', '<').replaceAll('&gt;', '>');
}
// Inspect start tags only; embedded RSC/JavaScript strings are not document links.
export function tags(html) {
  return [...html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').matchAll(/<([a-z][\w-]*)\b([^>]*)>/gi)].map(([, name, source]) => ({
    name: name.toLowerCase(),
    attrs: Object.fromEntries([...source.matchAll(/([\w:-]+)\s*=\s*"([^"]*)"/g)].map(([, key, value]) => [key, decode(value)])),
  }));
}
