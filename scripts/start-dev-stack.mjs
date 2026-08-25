/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - LOCAL SOVEREIGN RUNTIME ORCHESTRATOR [V1.0.0-LOGIN-AVAILABILITY]                                                           ║
 * ║ [NODE BFF | EOS KERNEL | VITE CLIENT | READINESS GATE | GRACEFUL SHUTDOWN]                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-LOGIN-AVAILABILITY | DEVELOPMENT RUNTIME CONTRACT                                                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/start-dev-stack.mjs                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Starts and verifies every local service required by Sovereign Login before exposing the Vite client.                          ║
 * ║ BIBLICAL ANCHOR: Psalm 1:3 - "And he shall be like a tree planted by the rivers of water..."                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated deterministic local login availability.                                                    ║
 * ║ • AI Engineering (Codex) – ARCHITECTED readiness-gated kernel, BFF, and client orchestration.                                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { spawn } from 'node:child_process';
import { createConnection } from 'node:net';

const LOOPBACK = '127.0.0.1';
const KERNEL_URL = `http://${LOOPBACK}:9095/kernel`;
const BFF_URL = `http://${LOOPBACK}:4000/api/kernel`;
const CLIENT_URL = `http://${LOOPBACK}:5173`;
const CLIENT_PORT = 5173;
const READY_TIMEOUT_MS = 30_000;
const RETRY_INTERVAL_MS = 300;
const managedProcesses = [];

/**
 * @function sleep
 * @description Pauses readiness polling without blocking child-process output.
 * @param {number} milliseconds - Delay duration.
 * @returns {Promise<void>} Resolution after the requested duration.
 * @collaboration Supports deterministic health verification for the EOS kernel and Node BFF.
 */
function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

/**
 * @function isOperational
 * @description Accepts only a successful HTTP health response; connection failures remain unavailable.
 * @param {string} url - Local service health endpoint.
 * @returns {Promise<boolean>} Whether the endpoint answered with a 2xx status.
 * @collaboration Prevents Vite from opening while login's upstream runtime is unavailable.
 */
async function isOperational(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 1_500);
  try {
    const response = await fetch(url, { signal: controller.signal, headers: { Accept: 'application/json' } });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * @function isPortListening
 * @description Checks whether a local listener owns the Vite port without requiring an application response.
 * @param {number} port - Loopback TCP port.
 * @returns {Promise<boolean>} Whether a listener accepted the loopback connection.
 * @collaboration Avoids starting a second Vite process when its development server already owns port 5173.
 */
function isPortListening(port) {
  return new Promise((resolve) => {
    let settled = false;
    /**
     * @function settle
     * @description Resolves the TCP probe once and clears its safety timeout.
     * @param {boolean} value - Listener availability result.
     * @returns {void}
     * @collaboration Guarantees each Vite listener probe has one deterministic completion path.
     */
    const settle = (value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      resolve(value);
    };
    const socket = createConnection({ host: LOOPBACK, port });
    const timeout = setTimeout(() => {
      socket.destroy();
      settle(false);
    }, 1_500);
    socket.once('connect', () => {
      socket.destroy();
      settle(true);
    });
    socket.once('error', () => {
      settle(false);
    });
  });
}

/**
 * @function startManagedProcess
 * @description Launches a child service and retains ownership for graceful shutdown.
 * @param {string} command - Executable name.
 * @param {string[]} args - Executable arguments.
 * @param {string} label - Human-readable service label.
 * @returns {import('node:child_process').ChildProcess} Managed child process.
 * @collaboration Makes local service ownership explicit without terminating pre-existing healthy services.
 */
function startManagedProcess(command, args, label) {
  const child = spawn(command, args, { cwd: process.cwd(), stdio: 'inherit', shell: false });
  managedProcesses.push(child);
  child.once('exit', (code, signal) => {
    if (code && !process.exitCode) {
      process.exitCode = code;
      console.error(`[WILSY-DEV-STACK] ${label} exited before the stack completed (code=${code}, signal=${signal || 'none'}).`);
    }
  });
  return child;
}

/**
 * @function ensureService
 * @description Reuses a healthy service or starts it and waits until its declared health endpoint is available.
 * @param {object} config - Service configuration.
 * @param {string} config.name - Service label.
 * @param {string} config.url - Health endpoint.
 * @param {string} config.command - Executable to start when unavailable.
 * @param {string[]} config.args - Start arguments.
 * @returns {Promise<void>} Resolves only after the health contract succeeds.
 * @throws {Error} When the service does not become healthy within the fixed readiness window.
 * @collaboration Enforces the Node BFF to EOS kernel dependency before the login screen is exposed.
 */
async function ensureService({ name, url, command, args }) {
  if (await isOperational(url)) {
    console.info(`[WILSY-DEV-STACK] Reusing healthy ${name}: ${url}`);
    return;
  }

  console.info(`[WILSY-DEV-STACK] Starting ${name}.`);
  startManagedProcess(command, args, name);
  const deadline = Date.now() + READY_TIMEOUT_MS;
  while (Date.now() < deadline) {
    if (await isOperational(url)) {
      console.info(`[WILSY-DEV-STACK] ${name} is ready: ${url}`);
      return;
    }
    await sleep(RETRY_INTERVAL_MS);
  }
  throw new Error(`${name} did not become healthy at ${url} within ${READY_TIMEOUT_MS}ms.`);
}

/**
 * @function shutdown
 * @description Stops only child processes created by this launcher.
 * @returns {void}
 * @collaboration Preserves independently-managed services while leaving the development stack clean.
 */
function shutdown() {
  for (const child of managedProcesses) {
    if (!child.killed) child.kill('SIGTERM');
  }
}

/**
 * @function keepStackAttached
 * @description Keeps this launcher attached to the terminal when it reuses an already-running Vite client.
 * @returns {Promise<never>} A deliberately pending lifecycle promise released by process termination.
 * @collaboration Ensures the newly-started API and kernel are not torn down while the user is using the existing client.
 */
function keepStackAttached() {
  return new Promise(() => {
    setInterval(() => {}, 60_000);
  });
}

process.once('SIGINT', shutdown);
process.once('SIGTERM', shutdown);
process.once('exit', shutdown);

try {
  await ensureService({
    name: 'EOS Kernel API',
    url: KERNEL_URL,
    command: 'python3',
    args: ['-m', 'uvicorn', 'tools.eos.api.server:app', '--host', LOOPBACK, '--port', '9095'],
  });
  await ensureService({
    name: 'Node API BFF',
    url: BFF_URL,
    command: 'npm',
    args: ['run', 'server:start'],
  });
  if (await isPortListening(CLIENT_PORT)) {
    console.info(`[WILSY-DEV-STACK] Reusing healthy Vite client: ${CLIENT_URL}`);
    console.info('[WILSY-DEV-STACK] Stack attached to this terminal. Press Ctrl+C to stop only services launched by this command.');
    await keepStackAttached();
  } else {
    console.info('[WILSY-DEV-STACK] Login dependency chain verified. Starting Vite client.');
    const viteClient = startManagedProcess('npm', ['run', 'dev', '--prefix', 'client'], 'Vite client');
    viteClient.once('exit', shutdown);
  }
} catch (error) {
  console.error(`[WILSY-DEV-STACK] Startup blocked: ${error.message}`);
  shutdown();
  process.exitCode = 1;
}
