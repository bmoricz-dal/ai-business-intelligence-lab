import { execFileSync } from 'node:child_process';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { assertLiveAncestor, assertReleaseState, checkoutState, git } from './release-guard.mjs';

const siteRoot = fileURLToPath(new URL('../', import.meta.url));
const origin = 'https://dal-data-ai-lab.moricz-labs.workers.dev';
const args = process.argv.slice(2);
if (args.some(arg => !['--check', '--bootstrap-live-marker'].includes(arg))) throw new Error('Unknown release option.');
const checkOnly = args.includes('--check');
const bootstrap = args.includes('--bootstrap-live-marker');
function checkGit() {
  const state = checkoutState(siteRoot);
  // Reject the wrong folder, branch or dirty tree before making network calls.
  assertReleaseState(state, state.head);
  const remoteHead = git(siteRoot, 'ls-remote', '--exit-code', 'origin', 'refs/heads/main').split(/\s+/)[0];
  assertReleaseState(state, remoteHead);
  return state.head;
}
async function checkLive(head) {
  const response = await fetch(`${origin}/release.json`, { cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(15_000) });
  if (response.status === 404 && bootstrap) {
    console.log('First release marker: manually verify the existing live release before publishing.');
    return;
  }
  if (response.status === 404) throw new Error('Live release has no marker. First release needs a verified live baseline and --bootstrap-live-marker.');
  if (!response.ok) throw new Error(`Live release check failed: HTTP ${response.status}`);
  const text = await response.text();
  if (text.length > 4096) throw new Error('Invalid live release marker.');
  assertLiveAncestor(JSON.parse(text), head, (ancestor, descendant) => {
    try { git(siteRoot, 'merge-base', '--is-ancestor', ancestor, descendant); return true; }
    catch { return false; }
  });
}
function run(command, commandArgs) {
  execFileSync(command, commandArgs, { cwd: siteRoot, stdio: 'inherit', env: { ...process.env, WRANGLER_LOG_PATH: '.wrangler/wrangler.log' } });
}
try {
  const head = checkGit();
  await checkLive(head);
  run('npm', ['run', 'verify']);
  // Build output is recreated from the checked source on every release.
  const marker = { schema: 1, commit: head, builtAt: new Date().toISOString() };
  await writeFile(new URL('../dist/client/release.json', import.meta.url), JSON.stringify(marker, null, 2) + '\n');
  run(process.execPath, ['node_modules/wrangler/bin/wrangler.js', 'deploy', '--dry-run', '--config', 'dist/server/wrangler.json', '--name', 'dal-data-ai-lab']);
  if (checkGit() !== head) throw new Error('Source changed during validation.');
  await checkLive(head);
  if (checkOnly) console.log('Release checks passed. Nothing published.');
  else {
    run(process.execPath, ['node_modules/wrangler/bin/wrangler.js', 'deploy', '--config', 'dist/server/wrangler.json', '--name', 'dal-data-ai-lab']);
    console.log(`Published validated commit ${head}. Verify the live routes and release.json after propagation.`);
  }
} catch (error) {
  console.error(`Release stopped: ${error.message}`);
  process.exitCode = 1;
}
