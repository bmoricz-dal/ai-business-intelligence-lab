import assert from 'node:assert/strict';
import test from 'node:test';
import { assertLiveAncestor, assertReleaseState, checkoutState, isExpectedRepository, repository } from '../scripts/release-guard.mjs';
import { siteRoot } from './helpers/site.mjs';
const head = 'a'.repeat(40);
const current = { canonical: true, remoteUrl: repository, branch: 'main', dirty: '', head };
test('release accepts only committed current main from the canonical website', () => {
  assert.doesNotThrow(() => assertReleaseState(current, head));
  assert.doesNotThrow(() => assertReleaseState({ ...current, remoteUrl: repository.slice(0, -4) }, head));
  for (const remoteUrl of [repository + '/other', repository + '?redirect=other', repository.replace('github.com', 'github.com.invalid')]) {
    assert.throws(() => assertReleaseState({ ...current, remoteUrl }, head));
  }
  for (const changes of [{ canonical: false }, { remoteUrl: 'https://example.com/old.git' }, { branch: 'old-work' }, { branch: '' }, { dirty: ' M app/page.tsx' }, { dirty: '?? app/new-page.tsx' }, { head: 'b'.repeat(40) }]) {
    assert.throws(() => assertReleaseState({ ...current, ...changes }, head));
  }
  assert.throws(() => assertReleaseState(current, ''));
});
test('reads the actual checkout rather than trusting environment variables', () => {
  const state = checkoutState(siteRoot);
  assert.equal(state.canonical, true);
  assert.ok(isExpectedRepository(state.remoteUrl));
  assert.match(state.head, /^[a-f0-9]{40}$/);
});
test('release blocks newer, divergent, invalid or unknown live revisions', () => {
  assert.doesNotThrow(() => assertLiveAncestor({ schema: 1, commit: head }, head, () => true));
  assert.throws(() => assertLiveAncestor({ schema: 1, commit: head }, head, () => false));
  assert.throws(() => assertLiveAncestor({ schema: 1 }, head, () => true));
  assert.throws(() => assertLiveAncestor({ schema: 2, commit: head }, head, () => true));
});
