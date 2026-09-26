/**
 * TITLE: WILSY OS browser-certificate runner
 * VERSION: v1.0.0-L8-8M-R3-BROWSER-CERT-RUNNER
 * AUTHORITY: Test process lifecycle only.
 * EPITOME: Own the disposable seed, EOS process, Vite process, Playwright
 *          process, and cleanup without killing unrelated repository services.
 * ABSOLUTE CANONICAL PATH:
 *   /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/run-browser-cert.mjs
 * COLLABORATION / OWNERSHIP: L8-8M-R3 browser infrastructure.
 * CERTIFICATION / UPDATE DATE: 2026-09-26
 * CHANGELOG: v1.0.0 establishes isolated local-replica-set orchestration on
 *             EOS port 9095 and Vite port 5174; it refuses an occupied EOS port.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Random signing secret and database name remain
 *                              process-local; no secret is printed.
 * TENANT BOUNDARY: One UUID database and fixture tenant per run.
 * AUTHORITY BOUNDARY: Test orchestration; no production data or application logic.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { spawn } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const repo = resolve(new URL('../..', import.meta.url).pathname);
const python = join(repo, '.venv/bin/python');
const fixture = join(repo, 'tests/e2e/browser_cert_fixture.py');
const playwright = join(repo, 'node_modules/.bin/playwright');
const chrome = process.env.WILSY_BROWSER_EXECUTABLE
  || (process.platform === 'darwin'
    ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    : '');
const runDirectory = await mkdtemp(join(tmpdir(), 'wilsy-l8-8m-r3-'));
const statePath = join(runDirectory, 'state.json');
const databaseName = `wilsy_l8_8m_r3_${Date.now().toString(36)}`;
const mongoUri = process.env.BROWSER_CERT_MONGO_URI
  || `mongodb://127.0.0.1:27027/${databaseName}?replicaSet=wilsyVendorCertRS`;
const secret = `browser-cert-${Date.now()}-${Math.random().toString(36)}`;
const environment = {
  ...process.env,
  BROWSER_CERT_MONGO_URI: mongoUri,
  BROWSER_CERT_STATE: statePath,
  MONGODB_URI: mongoUri,
  WILSY_JWT_SECRET: secret,
  ENV: 'development',
  WILSY_KENNEL_DB_TLS: '0',
  PYTHONPATH: [repo, process.env.PYTHONPATH].filter(Boolean).join(':'),
};

const owned = [];
const spawnOwned = (command, args, options = {}) => {
  const child = spawn(command, args, {
    cwd: repo,
    env: environment,
    stdio: ['ignore', 'ignore', 'ignore'],
    ...options,
  });
  owned.push(child);
  return child;
};

const runAndWait = (command, args, options = {}) => new Promise((resolveRun, rejectRun) => {
  const child = spawnOwned(command, args, { stdio: ['ignore', 'ignore', 'ignore'], ...options });
  child.once('error', rejectRun);
  child.once('exit', (code, signal) => {
    if (code === 0) resolveRun();
    else rejectRun(new Error(`BROWSER_CERT_PROCESS_FAILED:${command}:${code ?? signal}`));
  });
});

const waitFor = async (url, timeoutMs = 45_000) => {
  const deadline = Date.now() + timeoutMs;
  let last = null;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
      last = response.status;
    } catch (error) {
      last = error?.name || 'unreachable';
    }
    await delay(250);
  }
  throw new Error(`BROWSER_CERT_SERVICE_TIMEOUT:${url}:${String(last)}`);
};

const stopOwned = async () => {
  for (const child of [...owned].reverse()) {
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGTERM');
  }
  await delay(500);
  for (const child of [...owned].reverse()) {
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
  }
};

let failed = false;
try {
  try {
    const existing = await fetch('http://127.0.0.1:9095/api/kernel');
    if (existing.ok || existing.status > 0) {
      throw new Error('BROWSER_CERT_EOS_PORT_9095_OCCUPIED');
    }
  } catch (error) {
    if (error instanceof Error && error.message === 'BROWSER_CERT_EOS_PORT_9095_OCCUPIED') throw error;
  }
  await runAndWait(python, [fixture, 'seed', '--state', statePath]);
  spawnOwned(python, ['-m', 'uvicorn', 'tools.eos.api.server:app', '--host', '127.0.0.1', '--port', '9095']);
  await waitFor('http://127.0.0.1:9095/api/kernel');
  spawnOwned('npm', ['run', 'dev', '--', '--host', '127.0.0.1', '--port', '5174'], { cwd: join(repo, 'client') });
  await waitFor('http://127.0.0.1:5174/');
  const playwrightEnvironment = {
    ...environment,
    BROWSER_CERT_BASE_URL: 'http://127.0.0.1:5174',
  };
  if (chrome) playwrightEnvironment.WILSY_BROWSER_EXECUTABLE = chrome;
  await runAndWait(playwright, ['test', '--config', 'tests/e2e/playwright.config.js'], {
    env: playwrightEnvironment,
    stdio: ['ignore', 'inherit', 'inherit'],
  });
  await runAndWait(python, [fixture, 'verify', '--state', statePath], {
    env: playwrightEnvironment,
  });
} catch (error) {
  failed = true;
  console.error(error instanceof Error ? error.message : 'BROWSER_CERT_FAILED');
} finally {
  await stopOwned();
  try {
    await runAndWait(python, [fixture, 'cleanup'], { env: environment });
  } catch {
    failed = true;
    console.error('BROWSER_CERT_CLEANUP_FAILED');
  }
  await rm(runDirectory, { recursive: true, force: true });
}

if (failed) process.exitCode = 1;

// ARTIFACT: run-browser-cert.mjs
// VERSION: v1.0.0-L8-8M-R3-BROWSER-CERT-RUNNER
// AUTHORITY BOUNDARY: owned test-process lifecycle only
// TENANT POSTURE: UUID-isolated disposable database
// FAIL-CLOSED POSTURE: service/process/fixture failures return non-zero
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
