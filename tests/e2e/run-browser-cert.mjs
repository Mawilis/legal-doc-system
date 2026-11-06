/**
 * TITLE: WILSY OS browser-certificate runner
 * VERSION: v1.8.0-G68-INDEPENDENT-WORKSPACE-GATE
 * AUTHORITY: Test process lifecycle only.
 * EPITOME: Own the synthetic fixture, disposable EOS, isolated Node BFF, Vite,
 *          browser suite, bounded diagnostics, and ordered cleanup.
 * ABSOLUTE CANONICAL PATH:
 *   /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/run-browser-cert.mjs
 * COLLABORATION / OWNERSHIP: L8-8M browser certification; EOS retains tenant,
 *                            Legal, and authorization authority.
 * CERTIFICATION / UPDATE DATE: 2026-10-24
 * CHANGELOG: v1.5.1 requires an explicit loopback disposable replica-set URI on port 27017; v1.5.0 sends the fixture's explicit tenant scope with authenticated
 *            EOS preflights so canonical tenant authorization evaluates the
 *            synthetic principal's durable authority instead of rejecting a
 *            missing X-Tenant-ID request context.
 *            v1.8.0 does not gate browser journeys on the separately fail-closed G68 /workspace projection; it verifies Partner productive-work, Owner commercial read and Owner productive-work denial. v1.7.0 accepts an explicit loopback disposable replica set on a non-default host port using directConnection when host port 27017 is occupied.
 *            v1.4.0 tracks startup, Mongo/seed, authenticated preflight, browser,
 *            cleanup, and shutdown phases; preserves redacted child failure
 *            type/message/exit details; and reports primary and cleanup failures
 *            independently.
 *            v1.3.0 selects runner-owned available BFF/Vite ports and rewrites
 *            only the private Vite proxy copy.
 *            v1.2.0 adds bounded diagnostics and authenticated EOS preflights.
 *            v1.1.2 uses an owned temporary Vite config and ordered cleanup.
 *            v1.1.1 exposes safe lifecycle diagnostics.
 *            v1.1.0 uses alternate EOS/Vite configuration and preserves external services.
 *            v1.0.1 selects explicit, repository, or provisioned Python.
 *            v1.0.0 establishes UUID-isolated local-replica-set orchestration.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Tokens, credentials, full URIs, response bodies,
 *                             raw logs, and legal evidence are not emitted.
 * TENANT BOUNDARY: One UUID-isolated synthetic fixture database per run.
 * AUTHORITY BOUNDARY: Test orchestration only; EOS remains authoritative.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
 */

import { spawn } from 'node:child_process';
import { createConnection, createServer } from 'node:net';
import { createInterface } from 'node:readline';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const repo = resolve(new URL('../..', import.meta.url).pathname);
const python = process.env.BROWSER_CERT_PYTHON
  || (existsSync(join(repo, '.venv/bin/python'))
    ? join(repo, '.venv/bin/python')
    : 'python');
const fixture = join(repo, 'tests/e2e/browser_cert_fixture.py');
const scopeVerifier = join(repo, 'tests/e2e/browser_cert_scope_verify.py');
const playwright = join(repo, 'node_modules/.bin/playwright');
const serverDirectory = join(repo, 'server');
const clientDirectory = join(repo, 'client');
const chrome = process.env.WILSY_BROWSER_EXECUTABLE
  || (process.platform === 'darwin'
    ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    : '');
const runDirectory = await mkdtemp(join(tmpdir(), 'wilsy-l8-8m-r3-'));
const statePath = join(runDirectory, 'state.json');
const viteConfigPath = join(clientDirectory, '.wilsy-browser-cert-vite-' + process.pid + '.config.js');
const eosPort = Number.parseInt(process.env.BROWSER_CERT_EOS_PORT || '19095', 10);
const MAX_DIAGNOSTIC_LINES = 24;
const MAX_SAFE_MESSAGE_LENGTH = 240;
const SAFE_DIAGNOSTIC_CODE = /^[A-Z][A-Z0-9_]{0,95}$/;

if (!Number.isSafeInteger(eosPort) || eosPort < 1024 || eosPort > 65535) {
  throw new Error('BROWSER_CERT_EOS_PORT_INVALID');
}

const databaseName = 'wilsy_l8_8m_r3_' + Date.now().toString(36);
const mongoUri = (process.env.BROWSER_CERT_MONGO_URI || '').trim();
if (!mongoUri) {
  throw new Error('BROWSER_CERT_MONGO_URI_REQUIRED_DISPOSABLE_REPLICA_SET');
}
let mongoTarget;
try {
  mongoTarget = new URL(mongoUri);
} catch {
  throw new Error('BROWSER_CERT_MONGO_URI_INVALID');
}
const mongoDatabase = decodeURIComponent(mongoTarget.pathname.slice(1));
if (
  mongoTarget.protocol !== 'mongodb:'
  || !['127.0.0.1', 'localhost'].includes(mongoTarget.hostname)
  || !Number.isInteger(Number(mongoTarget.port))
  || Number(mongoTarget.port) < 1024
  || Number(mongoTarget.port) > 65535
  || mongoTarget.username
  || mongoTarget.password
  || !(
    mongoTarget.searchParams.get('replicaSet') === 'wilsyVendorCertRS'
    || mongoTarget.searchParams.get('directConnection') === 'true'
  )
  || !/^wilsy_l8_8m_r3_[a-zA-Z0-9_-]+$/.test(mongoDatabase)
) {
  throw new Error('BROWSER_CERT_DISPOSABLE_MONGO_TARGET_REQUIRED');
}
const secret = 'browser-cert-' + Date.now() + '-' + Math.random().toString(36);
const environment = {
  ...process.env,
  BROWSER_CERT_MONGO_URI: mongoUri,
  BROWSER_CERT_STATE: statePath,
  MONGODB_URI: mongoUri,
  WILSY_JWT_SECRET: secret,
  WILSY_PLATFORM_WORKFORCE_SCOPE_ID: 'browser-cert-platform-workforce',
  ENV: 'development',
  WILSY_KENNEL_DB_TLS: '0',
  PYTHONPATH: [repo, process.env.PYTHONPATH].filter(Boolean).join(':'),
};

const ownedProcesses = [];
let shutdownInProgress = false;
let fixtureSeedStarted = false;
let phase = 'startup';
let subphase = 'port_selection';
let primaryFailure = null;
let cleanupFailure = null;
let shutdownFailure = null;

function safeText(value) {
  return String(value ?? '')
    .replace(/mongodb(?:\+srv)?:\/\/[^\s"'<>]+/gi, 'mongodb://[REDACTED]')
    .replace(/\bBearer\s+[^\s,;]+/gi, 'Bearer [REDACTED]')
    .replace(/\b((?:access|refresh)[_-]?token|authorization|password|passwd|secret|token)\s*[:=]\s*[^\s,;]+/gi, '$1=[REDACTED]')
    .replace(/\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b/g, '[JWT_REDACTED]')
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, '[EMAIL_REDACTED]')
    .replace(/[\r\n\t]+/g, ' ')
    .slice(0, MAX_SAFE_MESSAGE_LENGTH);
}

function safeExceptionName(value) {
  const name = String(value || 'UNKNOWN');
  return /^[A-Za-z_][A-Za-z0-9_.]{0,79}$/.test(name) ? name : 'UNKNOWN';
}

function setPhase(nextPhase, nextSubphase) {
  phase = nextPhase;
  subphase = nextSubphase;
  console.info('[BROWSER-CERT-PHASE] phase=' + phase + ' subphase=' + subphase);
}

function printBoundedDiagnostic(record, code, fields = '') {
  if (record.diagnosticLines >= MAX_DIAGNOSTIC_LINES) return;
  record.diagnosticLines += 1;
  console.info(
    '[BROWSER-CERT-' + record.label + '] event=' + code + (fields ? ' ' + fields : ''),
  );
}

function captureSafeChildException(record, line) {
  const match = line.trim().match(/^([A-Za-z_][A-Za-z0-9_.]{0,79}):\s*(.*)$/);
  if (!match) return;
  record.originalException = {
    type: safeExceptionName(match[1]),
    message: safeText(match[2]),
  };
}

function classifyStartupLine(label, line) {
  const text = line.trim();
  if (label === 'EOS') {
    if (/^INFO: Started server process \[\d+\]$/.test(text)) return 'PROCESS_STARTED';
    if (text === 'INFO: Waiting for application startup.') return 'APPLICATION_STARTING';
    if (text === 'INFO: Application startup complete.') return 'APPLICATION_READY';
    if (/^INFO: Uvicorn running on http:\/\/127\.0\.0\.1:\d+/.test(text)) return 'LISTENING';
    if (/^ERROR:/.test(text)) return 'STARTUP_ERROR';
    return null;
  }
  if (label === 'BFF') {
    if (text.includes('Sovereign Runtime Bootstrap')) return 'PROCESS_STARTED';
    if (text.includes('MongoDB connection established.')) return 'DATABASE_CONNECTED';
    if (text.includes('MongoDB connection failed')) return 'DATABASE_CONNECTION_FAILED';
    if (text.includes('No MongoDB URI provided')) return 'DATABASE_URI_MISSING';
    if (text.includes('Securing TCP Port')) return 'LISTENER_STARTING';
    if (/HTTP:\s+http:\/\/localhost:\d+/.test(text)) return 'LISTENING';
    if (/^(Error|TypeError|ReferenceError|SyntaxError):/.test(text)) return 'STARTUP_ERROR';
    return null;
  }
  if (label === 'VITE') {
    if (/Local:\s+http:\/\/127\.0\.0\.1:\d+/.test(text)) return 'LISTENING';
    if (text.includes('ready in')) return 'READY';
    if (text.includes('failed to load config')) return 'CONFIG_LOAD_ERROR';
    if (text.includes('server restart failed')) return 'RESTART_ERROR';
    if (text.includes('http proxy error')) return 'PROXY_ERROR';
  }
  return null;
}

function attachSafeDiagnostics(record) {
  for (const stream of [record.child.stdout, record.child.stderr]) {
    if (!stream) continue;
    const lines = createInterface({ input: stream, crlfDelay: Infinity });
    lines.on('line', (line) => {
      if (record.label.startsWith('FIXTURE_')) captureSafeChildException(record, line);
      if (record.label === 'EOS') {
        const diagnostic = line.match(
          /OWNER_WORK_TRANSACTION_FAILURE error_type=([A-Za-z_][A-Za-z0-9_.]{0,79}) error_code=([A-Za-z0-9_.-]{1,40}|None) cause_type=([A-Za-z_][A-Za-z0-9_.]{0,79}|None) cause_code=([A-Za-z0-9_.-]{1,40}|None)/,
        );
        if (diagnostic) {
          printBoundedDiagnostic(
            record,
            'OWNER_WORK_TRANSACTION_FAILURE',
            `error_type=${diagnostic[1]} error_code=${diagnostic[2]} cause_type=${diagnostic[3]} cause_code=${diagnostic[4]}`,
          );
        }
      }
      if (record.label === 'BFF') {
        const match = line.match(/HTTP:\s+http:\/\/localhost:(\d+)/);
        if (match) record.listeningPort = Number(match[1]);
      } else if (record.label === 'VITE') {
        const match = line.match(/Local:\s+http:\/\/(?:127\.0\.0\.1|localhost):(\d+)/);
        if (match) record.listeningPort = Number(match[1]);
      }
      const event = classifyStartupLine(record.label, line);
      if (event) {
        const fields = record.listeningPort ? 'port=' + record.listeningPort : '';
        printBoundedDiagnostic(record, event, fields);
      }
    });
  }
}

function spawnOwned(command, args, options = {}, label = basename(command).toUpperCase()) {
  const child = spawn(command, args, {
    cwd: repo,
    env: environment,
    stdio: ['ignore', 'ignore', 'ignore'],
    ...options,
  });
  let closeResolve;
  const closedPromise = new Promise((resolveClose) => {
    closeResolve = resolveClose;
  });
  const record = {
    child,
    label,
    phase,
    subphase,
    diagnosticLines: 0,
    closed: false,
    listeningPort: null,
    originalException: null,
    closedPromise,
  };
  child.once('close', (code, signal) => {
    record.closed = true;
    record.exitCode = code;
    record.exitSignal = signal;
    closeResolve();
    if (!shutdownInProgress && code !== 0) {
      printBoundedDiagnostic(
        record,
        'PROCESS_EXIT',
        'code=' + (code === null ? 'NONE' : code) + ' signal=' + (signal || 'NONE'),
      );
    }
  });
  ownedProcesses.push(record);
  if (label === 'EOS' || label === 'BFF' || label === 'VITE' || label.startsWith('FIXTURE_')) {
    attachSafeDiagnostics(record);
  }
  return record;
}

function processFailure(record, code, signal, spawnError) {
  const failure = new Error('BROWSER_CERT_PROCESS_FAILED:' + record.label);
  failure.name = 'ChildProcessFailure';
  failure.phase = record.phase;
  failure.subphase = record.subphase;
  failure.childName = record.label;
  failure.exitCode = code;
  failure.exitSignal = signal;
  failure.spawnError = spawnError ? {
    type: safeExceptionName(spawnError.name),
    code: SAFE_DIAGNOSTIC_CODE.test(spawnError.code || '') ? spawnError.code : 'UNKNOWN',
    message: safeText(spawnError.message),
  } : null;
  failure.originalException = record.originalException || null;
  return failure;
}

function runAndWait(command, args, options = {}, label = basename(command).toUpperCase()) {
  return new Promise((resolveRun, rejectRun) => {
    const record = spawnOwned(command, args, options, label);
    let spawnError = null;
    record.child.once('error', (error) => {
      spawnError = error;
    });
    record.child.once('close', (code, signal) => {
      if (code === 0 && !spawnError) resolveRun(record);
      else rejectRun(processFailure(record, code, signal, spawnError));
    });
  });
}

function safeNetworkCode(error) {
  const candidate = error?.cause?.code || error?.code || error?.name || 'NETWORK_ERROR';
  return SAFE_DIAGNOSTIC_CODE.test(candidate) ? candidate : 'NETWORK_ERROR';
}

async function waitFor(url, service, timeoutMs = 45_000) {
  const deadline = Date.now() + timeoutMs;
  let lastStatus = 'UNREACHABLE';
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(3_000) });
      if (response.ok) return response;
      lastStatus = String(response.status);
    } catch (error) {
      lastStatus = safeNetworkCode(error);
    }
    await delay(250);
  }
  throw new Error('BROWSER_CERT_SERVICE_TIMEOUT:' + service + ':' + lastStatus);
}

async function waitForOwnedPort(record, timeoutMs = 45_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (record.closed) throw new Error('BROWSER_CERT_' + record.label + '_PROCESS_EXITED_BEFORE_LISTEN');
    if (Number.isInteger(record.listeningPort)) return record.listeningPort;
    await delay(100);
  }
  throw new Error('BROWSER_CERT_' + record.label + '_LISTEN_EVENT_TIMEOUT');
}

async function assertPortAvailable(port, service) {
  const available = await new Promise((resolveProbe) => {
    let settled = false;
    const socket = createConnection({ host: '127.0.0.1', port });
    const settle = (result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      socket.destroy();
      resolveProbe(result);
    };
    const timeout = setTimeout(() => settle(false), 1_000);
    socket.once('connect', () => settle(false));
    socket.once('error', (error) => settle(error.code === 'ECONNREFUSED'));
  });
  if (!available) throw new Error('BROWSER_CERT_' + service + '_PORT_OCCUPIED_OR_UNAVAILABLE:' + port);
}

async function availablePort() {
  const server = createServer();
  await new Promise((resolveListen, rejectListen) => {
    server.once('error', rejectListen);
    server.listen(0, '127.0.0.1', resolveListen);
  });
  const address = server.address();
  if (!address || typeof address === 'string') {
    await new Promise((resolveClose) => server.close(resolveClose));
    throw new Error('BROWSER_CERT_EPHEMERAL_PORT_UNAVAILABLE');
  }
  const port = address.port;
  await new Promise((resolveClose, rejectClose) => {
    server.close((error) => error ? rejectClose(error) : resolveClose());
  });
  return port;
}

async function readBoundedJson(response, maximumBytes = 4_096) {
  if (!response.body) return null;
  const reader = response.body.getReader();
  const chunks = [];
  let totalBytes = 0;
  try {
    while (totalBytes <= maximumBytes) {
      const { done, value } = await reader.read();
      if (done) break;
      totalBytes += value.byteLength;
      if (totalBytes > maximumBytes) {
        await reader.cancel();
        return null;
      }
      chunks.push(value);
    }
  } catch {
    return null;
  }
  try {
    const bytes = new Uint8Array(totalBytes);
    let offset = 0;
    for (const chunk of chunks) {
      bytes.set(chunk, offset);
      offset += chunk.byteLength;
    }
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    return null;
  }
}

function safeHttpDetailCode(payload) {
  if (!payload || typeof payload !== 'object') return 'DETAIL_OMITTED';
  if (payload.message === 'Tenant scope is required.') return 'TENANT_SCOPE_REQUIRED';
  if (payload.message === 'Tenant authorization denied.') return 'TENANT_AUTHORIZATION_DENIED';
  const candidates = [payload.detail, payload.code, payload.error_code, payload.error];
  if (payload.detail && typeof payload.detail === 'object') {
    candidates.push(payload.detail.code, payload.detail.error);
  }
  for (const candidate of candidates) {
    if (typeof candidate === 'string' && SAFE_DIAGNOSTIC_CODE.test(candidate)) return candidate;
  }
  return 'DETAIL_OMITTED';
}

async function preflightEosRoute(routeName, token, tenantId, eosBaseUrl) {
  const route = '/api/legal-operations/' + routeName;
  let response;
  try {
    response = await fetch(eosBaseUrl + route, {
      method: 'GET',
      headers: {
        Authorization: 'Bearer ' + token,
        'X-Tenant-ID': tenantId,
      },
      signal: AbortSignal.timeout(10_000),
    });
  } catch (error) {
    const errorCode = safeNetworkCode(error);
    console.error(
      '[BROWSER-CERT-PREFLIGHT] service=EOS method=GET path=' + route
        + ' status=UNREACHABLE error_code=' + errorCode,
    );
    return { routeName, status: 'UNREACHABLE', detailCode: errorCode };
  }
  const detailCode = response.status === 200
    ? 'NONE'
    : safeHttpDetailCode(await readBoundedJson(response));
  console.info(
    '[BROWSER-CERT-PREFLIGHT] service=EOS method=GET path=' + route
      + ' status=' + response.status + ' detail_code=' + detailCode,
  );
  return { routeName, status: response.status, detailCode };
}

async function preflightAuthenticatedEos(eosBaseUrl) {
  let state;
  try {
    state = JSON.parse(await readFile(statePath, 'utf-8'));
  } catch {
    throw new Error('BROWSER_CERT_FIXTURE_STATE_UNAVAILABLE');
  }
  const partnerToken = state?.actors?.partner?.access_token;
  const ownerToken = state?.actors?.tenant_owner?.access_token;
  if (
    typeof partnerToken !== 'string' || partnerToken.length === 0
    || typeof ownerToken !== 'string' || ownerToken.length === 0
  ) {
    throw new Error('BROWSER_CERT_FIXTURE_SESSION_UNAVAILABLE');
  }
  const tenantId = state?.tenant_id;
  if (typeof tenantId !== 'string' || tenantId.length === 0 || tenantId !== tenantId.trim()) {
    throw new Error('BROWSER_CERT_FIXTURE_TENANT_SCOPE_UNAVAILABLE');
  }
  // The legacy /workspace confidentiality projection remains independently
  // fail-closed under G68 and is not consumed by these browser journeys.
  // Certify the actual Partner productive-work path and Owner commercial read;
  // explicitly prove that Owner productive-work remains denied.
  const results = await Promise.all([
    preflightEosRoute('productive-work', partnerToken, tenantId, eosBaseUrl),
    preflightEosRoute('commercial-context', ownerToken, tenantId, eosBaseUrl),
    preflightEosRoute('productive-work', ownerToken, tenantId, eosBaseUrl),
  ]);
  const ownerPracticeRead = results[2];
  if (ownerPracticeRead.status !== 403) {
    throw new Error(
      'BROWSER_CERT_OWNER_PRACTICE_READ_NOT_DENIED:' + ownerPracticeRead.status,
    );
  }
  return results.slice(0, 2);
}


async function preflightSystemServices(eosBaseUrl) {
  let state;
  try {
    state = JSON.parse(await readFile(statePath, 'utf-8'));
  } catch {
    throw new Error('BROWSER_CERT_FIXTURE_STATE_UNAVAILABLE');
  }
  const responder = state?.system_actors?.system_responder;
  const triage = state?.system_actors?.system_triage;
  if (!responder?.access_token || !triage?.access_token) {
    throw new Error('BROWSER_CERT_SYSTEM_ACTOR_SESSIONS_UNAVAILABLE');
  }
  const request = async (path, token) => {
    const response = await fetch(eosBaseUrl + '/api/system-services/' + path, {
      headers: { Authorization: 'Bearer ' + token },
      signal: AbortSignal.timeout(10_000),
    });
    return { status: response.status, payload: await readBoundedJson(response) };
  };
  const [bootstrap, queue, inbox, triageInbox] = await Promise.all([
    request('workspace-bootstrap', responder.access_token),
    request('security-incidents', responder.access_token),
    request('security-incident-assignments/mine', responder.access_token),
    request('security-incident-assignments/mine', triage.access_token),
  ]);
  console.info(
    '[BROWSER-CERT-SYSTEM-SERVICES] bootstrap=' + bootstrap.status
      + ' queue=' + queue.status + ' responder_inbox=' + inbox.status
      + ' non_responder_inbox=' + triageInbox.status,
  );
  if (
    bootstrap.status !== 200
    || bootstrap.payload?.status !== 'READY'
    || bootstrap.payload?.authority !== 'EOS_SYSTEM_SERVICES'
    || !bootstrap.payload?.capabilities?.includes('system_services:incident:escalate')
    || queue.status !== 200
    || inbox.status !== 200
    || triageInbox.status !== 403
  ) {
    throw new Error('BROWSER_CERT_SYSTEM_SERVICES_AUTHORIZATION_BOUNDARY_FAILED');
  }
  const incidents = queue.payload;
  const assignments = inbox.payload;
  if (
    !Array.isArray(incidents)
    || !incidents.some((item) => item.incidentId === state.system_incident_id)
    || !Array.isArray(assignments)
    || !assignments.some((item) => item.assignmentId === state.system_assignment_id)
  ) {
    throw new Error('BROWSER_CERT_SYSTEM_SERVICES_SEEDED_EVIDENCE_MISSING');
  }
}


function missingBffDependencies() {
  const required = ['cors', 'dotenv', 'express', 'express-fileupload', 'helmet', 'httpxy', 'mongoose'];
  return required.filter(
    (name) => !existsSync(join(serverDirectory, 'node_modules', name, 'package.json')),
  );
}

async function verifyBffHealth(response) {
  const payload = await readBoundedJson(response);
  const acceptedStates = new Set([
    'CONNECTED', 'CONNECTING', 'DEGRADED', 'DISCONNECTED', 'DISCONNECTING', 'UNKNOWN',
  ]);
  const databaseState = acceptedStates.has(payload?.database) ? payload.database : 'UNKNOWN';
  console.info(
    '[BROWSER-CERT-PREFLIGHT] service=BFF method=GET path=/health'
      + ' status=' + response.status + ' database=' + databaseState,
  );
  if (response.status !== 200 || databaseState !== 'CONNECTED') {
    throw new Error('BROWSER_CERT_BFF_HEALTH_FAILED:' + response.status + ':' + databaseState);
  }
}

function failureEvidence(error, errorPhase, errorSubphase) {
  const evidence = {
    phase: safeText(error?.phase || errorPhase),
    subphase: safeText(error?.subphase || errorSubphase),
    error_type: safeExceptionName(error?.name),
    message: safeText(error?.message),
  };
  if (error?.childName) evidence.child = safeText(error.childName);
  if (Number.isInteger(error?.exitCode) || error?.exitCode === null) {
    evidence.exit_code = error.exitCode;
  }
  if (error?.exitSignal) evidence.exit_signal = safeText(error.exitSignal);
  if (error?.spawnError) evidence.spawn_error = error.spawnError;
  if (error?.originalException) evidence.original_exception = error.originalException;
  return evidence;
}

async function stopOwned() {
  const active = ownedProcesses.filter((record) => !record.closed).reverse();
  for (const record of active) {
    try {
      record.child.kill('SIGTERM');
    } catch {
      record.signalFailure = 'SIGTERM_FAILED';
    }
  }
  let closed = await Promise.race([
    Promise.all(active.map((record) => record.closedPromise)).then(() => true),
    delay(5_000).then(() => false),
  ]);
  if (!closed) {
    for (const record of active.filter((candidate) => !candidate.closed)) {
      try {
        record.child.kill('SIGKILL');
      } catch {
        record.signalFailure = 'SIGKILL_FAILED';
      }
    }
    closed = await Promise.race([
      Promise.all(active.map((record) => record.closedPromise)).then(() => true),
      delay(10_000).then(() => false),
    ]);
  }
  return { stopped: closed, remaining: active.filter((record) => !record.closed) };
}

let failed = false;
let ownedServicesStopped = true;
let bffPort = null;
let vitePort = null;

try {
  const eosBaseUrl = 'http://127.0.0.1:' + eosPort;
  await assertPortAvailable(eosPort, 'EOS');
  bffPort = await availablePort();
  vitePort = await availablePort();
  while (vitePort === bffPort) vitePort = await availablePort();

  setPhase('mongo_connectivity', 'disposable_replica_set_hello_in_fixture_seed');
  fixtureSeedStarted = true;
  setPhase('seed_attempt', 'uuid_scoped_synthetic_fixture');
  await runAndWait(
    python,
    [fixture, 'seed', '--state', statePath],
    { stdio: ['ignore', 'pipe', 'pipe'] },
    'FIXTURE_SEED',
  );

  setPhase('startup', 'eos_startup');
  console.info('[BROWSER-CERT-STARTUP] service=EOS action=starting port=' + eosPort);
  const eosProcess = spawnOwned(
    python,
    ['-m', 'uvicorn', 'tools.eos.api.server:app', '--host', '127.0.0.1', '--port', String(eosPort)],
    { stdio: ['ignore', 'pipe', 'pipe'] },
    'EOS',
  );
  const eosReady = await waitFor(eosBaseUrl + '/api/kernel', 'EOS');
  if (eosProcess.closed) throw new Error('BROWSER_CERT_EOS_EXITED_DURING_STARTUP');
  if (!eosReady.ok) throw new Error('BROWSER_CERT_EOS_KERNEL_HEALTH_FAILED:' + eosReady.status);

  setPhase('authenticated_preflights', 'partner_practice_and_owner_commercial_authority');
  const preflightResults = await preflightAuthenticatedEos(eosBaseUrl);
  await preflightSystemServices(eosBaseUrl);
  const failedPreflights = preflightResults.filter((result) => result.status !== 200);
  if (failedPreflights.length > 0) {
    const summary = preflightResults.map(
      (result) => result.routeName + '=' + result.status + ':' + result.detailCode,
    ).join(',');
    throw new Error('BROWSER_CERT_EOS_PREFLIGHT_FAILED:' + summary);
  }

  const baseViteConfigPath = join(clientDirectory, 'vite.config.js');
  const baseViteConfig = await readFile(baseViteConfigPath, 'utf-8');
  const hasEosProxy = baseViteConfig.includes('http://localhost:9095')
    || baseViteConfig.includes('http://127.0.0.1:9095');
  const usesBffProxy = baseViteConfig.includes('http://localhost:4000')
    || baseViteConfig.includes('http://127.0.0.1:4000');
  if (!hasEosProxy) {
    throw new Error('BROWSER_CERT_VITE_EOS_PROXY_TARGET_NOT_FOUND');
  }
  if (usesBffProxy) {
    setPhase('startup', 'bff_dependency_check_and_launch');
    const missingDependencies = missingBffDependencies();
    if (missingDependencies.length > 0) {
      throw new Error('BROWSER_CERT_BFF_DEPENDENCIES_MISSING:' + missingDependencies.join(','));
    }
    const bffEnvironment = {
      ...environment,
      PORT: String(bffPort),
      MONGODB_URI: mongoUri,
      MONGO_URI: mongoUri,
      KENNEL_URL: eosBaseUrl,
    };
    console.info('[BROWSER-CERT-STARTUP] service=BFF action=starting port=' + bffPort);
    const bffProcess = spawnOwned(
      process.execPath,
      ['--import', './preload-shield.js', 'server.js'],
      { cwd: serverDirectory, env: bffEnvironment, stdio: ['ignore', 'pipe', 'pipe'] },
      'BFF',
    );
    bffPort = await waitForOwnedPort(bffProcess);
    const bffHealthResponse = await waitFor('http://127.0.0.1:' + bffPort + '/health', 'BFF');
    if (bffProcess.closed) throw new Error('BROWSER_CERT_BFF_EXITED_DURING_STARTUP');
    await verifyBffHealth(bffHealthResponse);
  } else {
    console.info('[BROWSER-CERT-STARTUP] service=BFF action=skipped reason=EOS_OWNS_ALL_API_PROXY_ROUTES');
  }
  const configuredVite = baseViteConfig
    .replaceAll('http://localhost:9095', eosBaseUrl)
    .replaceAll('http://127.0.0.1:9095', eosBaseUrl)
    .replaceAll('http://localhost:4000', 'http://127.0.0.1:' + bffPort)
    .replaceAll('http://127.0.0.1:4000', 'http://127.0.0.1:' + bffPort);
  await writeFile(viteConfigPath, configuredVite, { encoding: 'utf-8', mode: 0o600 });

  setPhase('startup', 'vite_startup');
  console.info('[BROWSER-CERT-STARTUP] service=VITE action=starting port=' + vitePort);
  const viteProcess = spawnOwned(
    process.execPath,
    [
      join(clientDirectory, 'node_modules/vite/bin/vite.js'),
      '--config', viteConfigPath,
      '--host', '127.0.0.1',
      '--port', String(vitePort),
      '--strictPort',
    ],
    { cwd: clientDirectory, stdio: ['ignore', 'pipe', 'pipe'] },
    'VITE',
  );
  // The selected ephemeral port is authoritative; certify it by HTTP rather
  // than depending on Vite-version-specific console URL formatting.
  await waitFor('http://127.0.0.1:' + vitePort + '/', 'VITE');
  if (viteProcess.closed) throw new Error('BROWSER_CERT_VITE_EXITED_DURING_STARTUP');
  const viteListeningPort = vitePort;
  if (viteListeningPort !== vitePort) {
    throw new Error('BROWSER_CERT_VITE_LISTEN_PORT_MISMATCH:' + viteListeningPort + ':' + vitePort);
  }

  setPhase('browser_suite', 'playwright_authenticated_journeys');
  const playwrightEnvironment = {
    ...environment,
    BROWSER_CERT_BASE_URL: 'http://127.0.0.1:' + vitePort,
  };
  if (chrome) playwrightEnvironment.WILSY_BROWSER_EXECUTABLE = chrome;
  await runAndWait(
    playwright,
    ['test', '--config', 'tests/e2e/playwright.config.js', ...process.argv.slice(2)],
    { env: playwrightEnvironment, stdio: ['ignore', 'inherit', 'inherit'] },
    'PLAYWRIGHT',
  );
  setPhase('browser_suite', 'durable_fixture_verification');
  const browserTestArguments = process.argv.slice(2);
  const systemSuite = browserTestArguments.length === 2
    && browserTestArguments.includes('tests/e2e/system-services-incident.browser.spec.js')
    && browserTestArguments.includes('tests/e2e/system-services-response.browser.spec.js');
  const broadSuite = browserTestArguments.includes('--grep-invert');
  const verificationScope = systemSuite ? 'system' : broadSuite ? 'broad' : 'combined';
  await runAndWait(
    python,
    [scopeVerifier, '--state', statePath, '--scope', verificationScope],
    { env: playwrightEnvironment, stdio: ['ignore', 'pipe', 'pipe'] },
    'FIXTURE_VERIFY',
  );
} catch (error) {
  failed = true;
  primaryFailure = failureEvidence(error, phase, subphase);
  console.error('[BROWSER-CERT-PRIMARY-FAILURE] ' + JSON.stringify(primaryFailure));
} finally {
  setPhase('owned_process_shutdown', 'runner_spawned_children_only');
  shutdownInProgress = true;
  const shutdown = await stopOwned();
  ownedServicesStopped = shutdown.stopped;
  if (!ownedServicesStopped) {
    failed = true;
    shutdownFailure = {
      phase,
      error_type: 'OwnedProcessShutdownTimeout',
      remaining: shutdown.remaining.map((record) => ({
        child: record.label,
        pid: record.child.pid || null,
        signal_failure: record.signalFailure || null,
      })),
    };
    console.error('[BROWSER-CERT-SHUTDOWN-FAILURE] ' + JSON.stringify(shutdownFailure));
  }

  if (fixtureSeedStarted) {
    setPhase('fixture_cleanup', 'owned_uuid_database_only');
    try {
      await runAndWait(
        python,
        [fixture, 'cleanup'],
        { env: environment, stdio: ['ignore', 'pipe', 'pipe'] },
        'FIXTURE_CLEANUP',
      );
      console.info('[BROWSER-CERT-CLEANUP] fixture_database=removed');
    } catch (error) {
      failed = true;
      cleanupFailure = failureEvidence(error, 'fixture_cleanup', 'owned_uuid_database_only');
      console.error('[BROWSER-CERT-CLEANUP-FAILURE] ' + JSON.stringify(cleanupFailure));
    }
  } else {
    console.info('[BROWSER-CERT-CLEANUP] fixture_database=not_created cleanup=not_required');
  }

  await rm(runDirectory, { recursive: true, force: true });
  if (ownedServicesStopped) {
    await rm(viteConfigPath, { force: true });
  } else {
    console.error('BROWSER_CERT_VITE_CONFIG_RETAINED:owned_services_still_running');
  }
  if (primaryFailure || cleanupFailure || shutdownFailure) {
    console.error('[BROWSER-CERT-FAILURE-SUMMARY] ' + JSON.stringify({
      primary: primaryFailure,
      fixture_cleanup: cleanupFailure,
      owned_process_shutdown: shutdownFailure,
    }));
  }
}

if (failed) process.exitCode = 1;

// ARTIFACT: run-browser-cert.mjs
// VERSION: v1.5.1-L8-8M-EXPLICIT-DISPOSABLE-MONGO-TARGET
// AUTHORITY BOUNDARY: runner-owned disposable certification services only
// TENANT POSTURE: UUID-isolated fixture database; external tenants are untouched
// FAIL-CLOSED POSTURE: phase, health, preflight, browser, or cleanup failure returns non-zero
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
