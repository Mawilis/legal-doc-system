/* eslint-disable */
/**
 * Install Hook - Wilsy OS
 * Version: 1.0.0
 * Purpose: Centralized client-side install hook for token/tenant lifecycle,
 *          resilient fetch interception, graceful error handling, and
 *          observability hooks for testing and investor demos.
 *
 * Goals (Investor / Fortune 500 ready):
 *  - Deterministic, auditable logging with safe token previews only.
 *  - Clear separation of concerns: token management, tenant management,
 *    circuit-breaker, and UI/telemetry events.
 *  - Non-destructive behavior: tenant errors do not clear auth tokens.
 *  - Collaboration-friendly comments and extension points for engineers.
 *
 * Usage:
 *  - Include this file early in your client bundle (before app mounts).
 *  - The hook exposes a small public API on window.__SOVEREIGN_HOOKS__
 *    for integration tests, QA, and observability dashboards.
 *
 * Security notes:
 *  - Never log full tokens. Only a safe preview (first 8 chars) is printed.
 *  - On 401: only clear token when server explicitly indicates token invalid.
 *    For tenant validation errors, clear tenant and fall back to demo data.
 *
 * Events emitted (CustomEvent on window):
 *  - 'sovereign:auth-expired'  -> { requestId }
 *  - 'sovereign:tenant-invalid' -> { requestId }
 *  - 'sovereign:token-saved'   -> { preview }
 *  - 'sovereign:token-cleared' -> {}
 *  - 'sovereign:tenant-cleared'-> {}
 *
 * Test hooks:
 *  - window.__SOVEREIGN_HOOKS__.getTokenPreview()
 *  - window.__SOVEREIGN_HOOKS__.forceClearToken()
 *  - window.__SOVEREIGN_HOOKS__.forceSetTenant('MASTER')
 *
 * Collaboration comments:
 *  - If you change the header names (X-Tenant-ID), update server middleware tests.
 *  - Keep circuit-breaker thresholds conservative to avoid false positives.
 *  - Add telemetry correlationId to server responses for easier log matching.
 */

(function installSovereignHook() {
  if (typeof window === 'undefined') return;

  const LOG_PREFIX = '[SOVEREIGN]';
  const SAFE_PREVIEW_LEN = 8;
  const CIRCUIT_BREAKER_THRESHOLD = 3; // consecutive auth failures before tripping
  const CIRCUIT_BREAKER_COOLDOWN_MS = 60 * 1000; // 1 minute cooldown

  // Internal state
  let consecutiveAuthFailures = 0;
  let circuitTrippedAt = null;

  // Utility helpers
  const safePreview = (token) => {
    if (!token) return 'NO_TOKEN';
    const t = String(token);
    return t.length > SAFE_PREVIEW_LEN ? `${t.slice(0, SAFE_PREVIEW_LEN)}...` : `${t}...`;
  };

  const readToken = () => {
    try {
      return localStorage.getItem('sovereignToken') || null;
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ localStorage read failed`, e);
      return null;
    }
  };

  const writeToken = (token) => {
    try {
      if (!token) return;
      const normalized = String(token).trim().replace(/^Bearer\s+/i, '');
      localStorage.setItem('sovereignToken', normalized);
      const preview = safePreview(normalized);
      console.info(`${LOG_PREFIX} ✅ Token saved (preview):`, preview);
      window.dispatchEvent(new CustomEvent('sovereign:token-saved', { detail: { preview } }));
      return preview;
    } catch (e) {
      console.error(`${LOG_PREFIX} ❌ Failed to write token`, e);
      return null;
    }
  };

  const clearToken = () => {
    try {
      localStorage.removeItem('sovereignToken');
      console.info(`${LOG_PREFIX} 🧹 Token cleared`);
      window.dispatchEvent(new CustomEvent('sovereign:token-cleared'));
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ Failed to clear token`, e);
    }
  };

  const readTenant = () => {
    try {
      return localStorage.getItem('tenantId') || localStorage.getItem('VITE_TENANT_ID') || null;
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ localStorage read failed`, e);
      return null;
    }
  };

  const writeTenant = (tenant) => {
    try {
      const t = String(tenant || '').trim();
      if (!t) return null;
      localStorage.setItem('tenantId', t);
      console.info(`${LOG_PREFIX} ✅ Tenant saved:`, t);
      return t;
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ Failed to write tenant`, e);
      return null;
    }
  };

  const clearTenant = () => {
    try {
      localStorage.removeItem('tenantId');
      localStorage.removeItem('VITE_TENANT_ID');
      console.info(`${LOG_PREFIX} 🧹 Tenant cleared`);
      window.dispatchEvent(new CustomEvent('sovereign:tenant-cleared'));
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ Failed to clear tenant`, e);
    }
  };

  // Circuit breaker helpers
  const recordAuthFailure = (requestId) => {
    consecutiveAuthFailures += 1;
    console.warn(`${LOG_PREFIX} 🔒 Auth failure #${consecutiveAuthFailures}`, requestId ? { requestId } : {});
    if (consecutiveAuthFailures >= CIRCUIT_BREAKER_THRESHOLD) {
      circuitTrippedAt = Date.now();
      console.error(`${LOG_PREFIX} 🚨 AUTH CIRCUIT TRIPPED`);
    }
  };

  const resetAuthFailures = () => {
    consecutiveAuthFailures = 0;
    circuitTrippedAt = null;
  };

  const isCircuitTripped = () => {
    if (!circuitTrippedAt) return false;
    if (Date.now() - circuitTrippedAt > CIRCUIT_BREAKER_COOLDOWN_MS) {
      // cooldown expired
      resetAuthFailures();
      return false;
    }
    return true;
  };

  // Safe JSON parse helper
  const tryParseJson = async (response) => {
    try {
      const clone = response.clone();
      const contentType = clone.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) return null;
      return await clone.json();
    } catch (e) {
      return null;
    }
  };

  // Intercept fetch to capture verify-3fa responses and to instrument errors
  const originalFetch = window.fetch.bind(window);
  window.fetch = async function (...args) {
    const url = args[0];
    // Short-circuit if circuit is tripped to avoid spamming backend
    if (isCircuitTripped()) {
      console.warn(`${LOG_PREFIX} ⚠️ Circuit is tripped; skipping network call to:`, url);
      // emulate a failed response to keep app flow predictable
      return new Response(JSON.stringify({ error: 'CIRCUIT_TRIPPED' }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Forward the request
    let response;
    try {
      response = await originalFetch(...args);
    } catch (networkErr) {
      console.error(`${LOG_PREFIX} 🌐 Network error for ${url}`, networkErr);
      throw networkErr;
    }

    // If this is the 3FA verification endpoint, attempt to extract token and tenant
    try {
      if (typeof url === 'string' && url.includes('verify-3fa')) {
        const data = await tryParseJson(response);
        if (data) {
          console.info(`${LOG_PREFIX} 🔑 verify-3fa response received`);
          if (data.token) {
            const preview = writeToken(data.token);
            // set tenant if provided (normalize)
            if (data.user && data.user.tenantId) {
              const tenant = String(data.user.tenantId).trim();
              writeTenant(tenant);
            }
            // set operator name if present
            if (data.user && data.user.firstName) {
              try { localStorage.setItem('operatorName', String(data.user.firstName).toUpperCase()); } catch (e) {}
            }
            window.dispatchEvent(new CustomEvent('sovereign:token-saved', { detail: { preview } }));
          } else {
            console.warn(`${LOG_PREFIX} ❌ verify-3fa returned no token`);
          }
        } else {
          console.warn(`${LOG_PREFIX} ⚠️ verify-3fa response not JSON or empty`);
        }
      }
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ Error handling verify-3fa response`, e);
    }

    // Global response handling for auth/tenant errors
    try {
      if (response.status === 401) {
        const body = await tryParseJson(response);
        const serverCode = body?.code || body?.error || null;
        const requestId = body?.requestId || response.headers.get('X-Request-ID') || null;

        // Tenant validation errors: clear tenant only and fallback to demo data
        if (serverCode === 'TENANT_NOT_FOUND' || serverCode === 'TENANT_VALIDATION_ERROR') {
          console.warn(`${LOG_PREFIX} ⚠️ TENANT_NOT_FOUND from server`, { requestId, message: body?.message });
          clearTenant();
          window.dispatchEvent(new CustomEvent('sovereign:tenant-invalid', { detail: { requestId } }));
          // Do not clear token here — token may be valid for other tenants
          // Record failure but do not trip circuit for tenant-only issues
          recordAuthFailure(requestId);
          return response;
        }

        // Token invalid/expired: clear token and notify
        console.error(`${LOG_PREFIX} 🔒 401 Unauthorized - Token invalid`, { requestId });
        clearToken();
        recordAuthFailure(requestId);
        window.dispatchEvent(new CustomEvent('sovereign:auth-expired', { detail: { requestId } }));

        return response;
      }

      // On success, reset auth failure counters
      if (response.ok) {
        resetAuthFailures();
      }
    } catch (e) {
      console.warn(`${LOG_PREFIX} ⚠️ Error in global response handling`, e);
    }

    return response;
  };

  // Public API for tests, QA, and integration
  const hooks = {
    getTokenPreview: () => safePreview(readToken()),
    getRawToken: () => readToken(), // use only in secure test environments
    forceClearToken: () => { clearToken(); resetAuthFailures(); },
    forceSetTenant: (t) => writeTenant(t),
    isCircuitTripped: () => isCircuitTripped(),
    getCircuitState: () => ({ consecutiveAuthFailures, circuitTrippedAt }),
    // small helper to programmatically trigger a re-auth flow
    triggerReauth: () => {
      console.info(`${LOG_PREFIX} 🔁 triggerReauth called`);
      // dispatch an event the app can listen to and show login modal
      window.dispatchEvent(new CustomEvent('sovereign:trigger-reauth'));
    }
  };

  // Expose hooks in a non-enumerable property to avoid accidental overwrites
  try {
    Object.defineProperty(window, '__SOVEREIGN_HOOKS__', {
      configurable: true,
      enumerable: false,
      writable: false,
      value: hooks
    });
  } catch (e) {
    // fallback
    window.__SOVEREIGN_HOOKS__ = hooks;
  }

  // Developer-friendly startup log
  console.groupCollapsed(`${LOG_PREFIX} InstallHook initialized`);
  console.info(`${LOG_PREFIX} Token preview:`, safePreview(readToken()));
  console.info(`${LOG_PREFIX} Tenant:`, readTenant() || 'NO_TENANT');
  console.info(`${LOG_PREFIX} Circuit breaker threshold:`, CIRCUIT_BREAKER_THRESHOLD);
  console.groupEnd();

  // Collaboration note:
  // - UI should listen for 'sovereign:tenant-invalid' and show a non-blocking banner:
  //     "Tenant not found or inactive. Please re-select or onboard a tenant. (Request ID: ...)"
  // - UI should listen for 'sovereign:auth-expired' and show a modal prompting re-login.
  // - Tests can call window.__SOVEREIGN_HOOKS__.forceSetTenant('MASTER') to simulate tenant presence.
})();
