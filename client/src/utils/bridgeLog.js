/**
 * =============================================================================
 * Wilsy OS — Bridge Log (Console Hygiene)
 * =============================================================================
 * File:           client/src/utils/bridgeLog.js
 * Version:        v1.0.0-CONSOLE-QUIET
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Conditional logger for [BRIDGE] messages to reduce noise.
 *                 Enable verbose mode in DevTools with:
 *                 window.__WILSY_VERBOSE_BRIDGE__ = true;
 * Classification: Production Artifact
 * =============================================================================
 */

const IS_VERBOSE = () =>
  typeof window !== 'undefined' && window.__WILSY_VERBOSE_BRIDGE__ === true;

export function bridgeLog(method, url, extra = '') {
  if (!IS_VERBOSE()) return;
  console.log(`[BRIDGE] 🔒 Sealed ${method} ${url}${extra ? ' ' + extra : ''}`);
}

export function setBridgeVerbose(enabled) {
  if (typeof window !== 'undefined') {
    window.__WILSY_VERBOSE_BRIDGE__ = Boolean(enabled);
  }
}

export default { bridgeLog, setBridgeVerbose };
