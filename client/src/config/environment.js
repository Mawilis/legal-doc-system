/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CLIENT ENVIRONMENT RESOLVER [V1.0.0-PRODUCTION-CONFIG]                                                                    ║
 * ║ [VITE ENV ACCESS | API ROUTING | WEBSOCKET ROUTING | TIMEOUT GOVERNANCE | CLIENT SECRET WARNING]                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-CONFIG | PRODUCTION READY | CLIENT-SAFE CONFIGURATION SURFACE                                             ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/config/environment.js                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated that Wilsy OS uses env keys and never embeds sensitive runtime values in code files.      ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Centralized client-safe env reads and blocked secret-thinking from browser bundles.          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @function readClientEnv
 * @description Reads a Vite-exposed client environment key with a non-sensitive fallback.
 * @param {string} key - Vite environment key.
 * @param {string|number|boolean} fallback - Non-sensitive fallback value.
 * @returns {string|number|boolean} Environment value or fallback.
 * @collaboration Gives every client module one disciplined access path into client/.env without scattering raw import.meta.env reads.
 */
export const readClientEnv = (key, fallback = '') => {
  const value = import.meta.env?.[key];
  return value === undefined || value === null || value === '' ? fallback : value;
};

/**
 * @function getClientApiBaseUrl
 * @description Resolves the API base URL from client/.env and falls back to the same-origin API proxy.
 * @returns {string} Client API base URL.
 * @collaboration Removes hardcoded localhost endpoints from production client code while keeping local proxy support possible.
 */
export const getClientApiBaseUrl = () => String(readClientEnv('VITE_API_URL', '/api')).replace(/\/$/, '');

/**
 * @function getClientApiTimeout
 * @description Resolves the outbound API timeout from client/.env.
 * @returns {number} API timeout in milliseconds.
 * @collaboration Keeps network timing policy configurable per deployment without editing source files.
 */
export const getClientApiTimeout = () => {
  const timeout = Number(readClientEnv('VITE_API_TIMEOUT', 30000));
  return Number.isFinite(timeout) && timeout > 0 ? timeout : 30000;
};

/**
 * @function getClientWebSocketUrl
 * @description Resolves the browser websocket endpoint from client/.env.
 * @returns {string} Websocket base URL.
 * @collaboration Prevents websocket routing from being hardwired to a developer machine in production builds.
 */
export const getClientWebSocketUrl = () => String(readClientEnv('VITE_WS_URL', '')).replace(/\/$/, '');

/**
 * @function getClientEnvSecurityWarnings
 * @description Detects Vite keys that appear to expose secrets to the browser bundle.
 * @returns {Array<string>} Suspicious client environment keys.
 * @collaboration Reminds future maintainers that every VITE_ value is public to tenants and browsers.
 */
export const getClientEnvSecurityWarnings = () => Object.keys(import.meta.env || {})
  .filter(key => /^VITE_/i.test(key))
  .filter(key => /(SECRET|TOKEN|PASSWORD|PRIVATE|HMAC|JWT)/i.test(key));
