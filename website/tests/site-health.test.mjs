import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
import { resolve, relative } from 'node:path';
import test from 'node:test';
import { productionOrigin, render, routes, siteRoot, tags } from './helpers/site.mjs';

const expectedRoutes = [ '/', '/about', '/adoption-pathways', '/adoption-pathways/accounting-micro-case-study', '/adoption-pathways/construction-tender-lab', '/ai-business-adoption-map', '/ai-in-business', '/methods', '/sectors', '/sectors/accounting', '/sectors/accounting/adoption-journeys', '/sectors/accounting/benefits', '/sectors/construction', '/sectors/construction/adoption-journeys', '/sectors/construction/benefits' ];
const rendered = new Map();
for (const route of await routes()) {
  const response = await render(route);
  const html = await response.text();
  rendered.set(route, { status: response.status, html, tags: tags(html) });
}

test('preserves all released routes and checks every discovered page', () => {
  for (const route of expectedRoutes) assert.ok(rendered.has(route), `Released route removed: ${route}`);
  for (const [route, page] of rendered) {
    assert.equal(page.status, 200, route);
    assert.equal(page.tags.filter(tag => tag.name === 'h1').length, 1, `${route}: one primary heading`);
    assert.equal(page.tags.filter(tag => tag.name === 'main').length, 1, `${route}: one main landmark`);
    assert.match(page.html, /<title>[^<]+<\/title>/, `${route}: title`);
    assert.ok(page.tags.some(tag => tag.name === 'meta' && tag.attrs.name === 'description' && tag.attrs.content), `${route}: description`);
    const ids = page.tags.map(tag => tag.attrs.id).filter(Boolean);
    assert.equal(new Set(ids).size, ids.length, `${route}: duplicate IDs`);
  }
});

test('all rendered internal links, fragments and public downloads resolve', async () => {
  for (const [route, page] of rendered) {
    for (const tag of page.tags.filter(tag => tag.name === 'a' && tag.attrs.href)) {
      const target = new URL(tag.attrs.href, productionOrigin + route);
      if (target.origin !== productionOrigin) continue;
      const path = decodeURIComponent(target.pathname);
      const destination = rendered.get(path);
      if (destination) {
        if (target.hash) assert.ok(destination.tags.some(tag => tag.attrs.id === decodeURIComponent(target.hash.slice(1))), `${route}: missing fragment ${tag.attrs.href}`);
      } else {
        const asset = resolve(siteRoot, 'public', '.' + path);
        assert.ok(!relative(resolve(siteRoot, 'public'), asset).startsWith('..'), 'Asset escaped public directory');
        assert.ok((await stat(asset)).isFile(), `${route}: missing download ${tag.attrs.href}`);
        if (path.endsWith('.pdf')) assert.equal((await readFile(asset)).subarray(0, 5).toString(), '%PDF-', `${path}: not a PDF`);
      }
    }
  }
});

test('all generated script, stylesheet and image references exist', async () => {
  for (const [route, page] of rendered) {
    const sources = [...page.html.matchAll(/<(?:script|img)\b[^>]*\bsrc="([^"]+)"/g)].map(match => match[1]);
    sources.push(...page.tags.filter(tag => tag.name === 'link' && ['stylesheet', 'modulepreload', 'preload'].includes(tag.attrs.rel)).map(tag => tag.attrs.href).filter(Boolean));
    for (const source of sources) {
      const url = new URL(source, productionOrigin);
      if (url.origin !== productionOrigin) continue;
      assert.ok((await stat(resolve(siteRoot, 'dist/client', '.' + decodeURIComponent(url.pathname)))).isFile(), `${route}: missing asset ${source}`);
    }
  }
});

test('unknown pages return 404', async () => {
  assert.equal((await render('/audit-nonexistent-page')).status, 404);
});

test('forwarded headers cannot replace public share-image URLs', async () => {
  const html = await (await render('/', { host: 'attacker.invalid', 'x-forwarded-host': 'attacker.invalid', 'x-forwarded-proto': 'http' })).text();
  const images = tags(html).filter(tag => tag.name === 'meta' && ['og:image', 'twitter:image'].includes(tag.attrs.property ?? tag.attrs.name));
  assert.ok(images.length >= 2);
  for (const image of images) assert.equal(image.attrs.content, productionOrigin + '/og.png');
});

test('image endpoint works without an Images binding and rejects remote image URLs', async () => {
  const response = await render('/_vinext/image?url=%2Fog.png&w=640&q=75', {}, async () => new Response(new Uint8Array([137, 80, 78, 71]), { headers: { 'content-type': 'image/png' } }));
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
  assert.deepEqual(new Uint8Array(await response.arrayBuffer()), new Uint8Array([137, 80, 78, 71]));
  assert.equal((await render('/_vinext/image?url=https%3A%2F%2Fexample.com%2Fimage.png&w=640')).status, 400);
});

test('stylesheets reference existing local images and fonts', async () => {
  const { readdir } = await import('node:fs/promises');
  const client = resolve(siteRoot, 'dist/client');
  for (const file of (await readdir(client, { recursive: true })).filter(file => file.endsWith('.css'))) {
    const css = await readFile(resolve(client, file), 'utf8');
    for (const [, reference] of css.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)) {
      if (reference.startsWith('#')) continue;
      const url = new URL(reference.trim(), productionOrigin + '/' + file);
      if (url.origin !== productionOrigin) continue;
      assert.ok((await stat(resolve(client, '.' + decodeURIComponent(url.pathname)))).isFile(), `${file}: missing ${reference}`);
    }
  }
});
