import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { realpathSync } from 'node:fs';
import { resolve } from 'node:path';

export const repository = 'https://github.com/bmoricz-dal/ai-business-intelligence-lab.git';
export function isExpectedRepository(remoteUrl) {
  // GitHub Actions uses the same HTTPS repository without the optional suffix.
  return remoteUrl === repository || remoteUrl === repository.slice(0, -4);
}
export function git(cwd, ...args) {
  return execFileSync('git', args, { cwd, encoding: 'utf8', timeout: 30_000 }).trim();
}
export function checkoutState(siteRoot) {
  const root = git(siteRoot, 'rev-parse', '--show-toplevel');
  return {
    canonical: realpathSync(siteRoot) === realpathSync(resolve(root, 'website')),
    branch: git(root, 'branch', '--show-current'),
    head: git(root, 'rev-parse', 'HEAD'),
    dirty: git(root, 'status', '--porcelain', '--untracked-files=all'),
    remoteUrl: git(root, 'remote', 'get-url', 'origin'),
  };
}
export function assertReleaseState(state, remoteHead) {
  assert.ok(state.canonical, 'Release must run from the repository website/ folder.');
  assert.ok(isExpectedRepository(state.remoteUrl), 'Unexpected origin repository; release stopped.');
  assert.equal(state.branch, 'main', 'Publish only from main after review and merge.');
  assert.equal(state.dirty, '', 'Uncommitted or untracked files exist. Preserve and commit the intended work before publishing.');
  assert.match(remoteHead, /^[a-f0-9]{40}$/, 'Could not verify current GitHub main.');
  assert.equal(state.head, remoteHead, 'This checkout is not current GitHub main. Publishing could overwrite newer work.');
}
export function assertLiveAncestor(live, head, isAncestor) {
  assert.equal(live.schema, 1, 'Unrecognised live release marker.');
  assert.match(live.commit ?? '', /^[a-f0-9]{40}$/, 'Invalid live commit marker.');
  assert.ok(isAncestor(live.commit, head), 'Live site is newer than, or diverges from, this checkout. Release stopped.');
}
