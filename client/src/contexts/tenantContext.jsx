/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TENANT CONTEXT [V31.1.0-PRODUCTION-STABLE]                                                                        ║
 * ║ [DYNAMIC BRANDING NEXUS | SELF-HEALING CIRCUIT BREAKER | SOVEREIGN OVERRIDE | SLA LATENCY SENSORS | MESH-INTEGRATED]                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 31.1.0-PRODUCTION-STABLE | PRODUCTION READY | TENANT IDENTITY, BRANDING AND DISCOVERY CONTROL PLANE                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/tenantContext.jsx                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                     ║
 * ║ 1. Wilson Khanyezi - Mandated zero-leak tenant switching, sovereign founder override, cockpit-grade branding, and HMR stability.      ║
 * ║ 2. AI Engineering - Hardened context exports, guard-compliant JSDoc, tenant branding normalization, and safe profile fallbacks.        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign Tenant Context.
 * This provider discovers tenant shards, preserves tenant identity, exposes cockpit-safe branding,
 * guards backend discovery with a circuit breaker, and keeps forensic reconciliation owned by the backend.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from 'react';
import api from '../services/api';
import { useAuth } from './authContext';
import { useSovereignMesh } from '../components/sovereign/SovereignOrchestrator.jsx';
import { useSovereignData } from '../components/sovereign/DataOrchestrator.jsx';
import { generateSovereignSeal } from '../utils/cryptoCore.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const WILSY_R8Z_BROWSER_TENANT_ALIAS_CANONICALIZER = 'WILSY_R8Z_BROWSER_TENANT_ALIAS_CANONICALIZER_ACTIVE';

if (typeof window !== 'undefined') {
  try {
    ['tenantId', 'wilsyTenantId'].forEach((key) => {
      const value = window.localStorage.getItem(key) || window.sessionStorage.getItem(key);
      if (!value || /^(MASTER|WILSY_ROOT|GLOBAL_ROOT)$/i.test(String(value))) {
        window.localStorage.setItem(key, 'wilsy-sovereign-root');
        window.sessionStorage.removeItem(key);
      }
    });
  } catch (error) {
    // Browser storage may be unavailable during privacy-mode boot.
  }
}



const WILSY_R8V_AUTH_TOKEN_CAPTURE_BRIDGE_MARKER = 'WILSY_R8V_AUTH_TOKEN_CAPTURE_BRIDGE_ACTIVE';

/**
 * @function readWilsyR8VObjectPath
 * @description Reads nested response payload paths without throwing when auth responses vary by controller branch.
 * @collaboration Supports login, MFA verification, refresh-token, and session persistence across Wilsy OS auth flows.
 */
const readWilsyR8VObjectPath = (source, path) => (
  String(path || '')
    .split('.')
    .filter(Boolean)
    .reduce((value, key) => (value && typeof value === 'object' ? value[key] : undefined), source)
);

/**
 * @function findWilsyR8VTokenCandidate
 * @description Finds the first JWT-like token returned by Wilsy auth response payloads across known token key shapes.
 * @collaboration Bridges authController response shapes to frontend token storage without changing backend security.
 */
const findWilsyR8VTokenCandidate = (payload = {}) => {
  const paths = [
    'token',
    'accessToken',
    'jwt',
    'authToken',
    'bearerToken',
    'data.token',
    'data.accessToken',
    'data.jwt',
    'data.authToken',
    'session.token',
    'session.accessToken',
    'tokens.token',
    'tokens.accessToken',
    'result.token',
    'result.accessToken'
  ];

  for (const path of paths) {
    const value = readWilsyR8VObjectPath(payload, path);
    if (typeof value === 'string' && value.split('.').length === 3 && value.length > 80) {
      return value;
    }
  }

  return '';
};

/**
 * @function findWilsyR8VRefreshTokenCandidate
 * @description Finds a refresh token returned by auth endpoints while keeping raw values out of logs.
 * @collaboration Preserves session refresh continuity after successful MFA or refresh-token calls.
 */
const findWilsyR8VRefreshTokenCandidate = (payload = {}) => {
  const paths = [
    'refreshToken',
    'data.refreshToken',
    'session.refreshToken',
    'tokens.refreshToken',
    'result.refreshToken'
  ];

  for (const path of paths) {
    const value = readWilsyR8VObjectPath(payload, path);
    if (typeof value === 'string' && value.length > 20) {
      return value;
    }
  }

  return '';
};

/**
 * @function resolveWilsyR8VTenantFromPayload
 * @description Resolves the canonical tenant id from auth payloads and current browser storage.
 * @collaboration Keeps tenantContext, auth token storage, and backend tenant guard aligned.
 */
const resolveWilsyR8VTenantFromPayload = (payload = {}) => (
  readWilsyR8VObjectPath(payload, 'user.tenantId')
  || readWilsyR8VObjectPath(payload, 'data.user.tenantId')
  || readWilsyR8VObjectPath(payload, 'tenantId')
  || readWilsyR8VObjectPath(payload, 'data.tenantId')
  || readWilsyR8VObjectPath(payload, 'tenant.id')
  || readWilsyR8VObjectPath(payload, 'tenant.tenantId')
  || window.localStorage.getItem('wilsyTenantId')
  || window.localStorage.getItem('tenantId')
  || 'wilsy-sovereign-root'
);

/**
 * @function persistWilsyR8VAuthPayload
 * @description Persists successful auth tokens from login, MFA, and refresh responses into every token slot the app reads.
 * @collaboration Stops immediate logout by ensuring /api/auth/me receives the token minted by the backend.
 */
const persistWilsyR8VAuthPayload = (payload = {}, source = WILSY_R8V_AUTH_TOKEN_CAPTURE_BRIDGE_MARKER) => {
  if (typeof window === 'undefined' || !payload || typeof payload !== 'object') return false;

  const token = findWilsyR8VTokenCandidate(payload);
  const refreshToken = findWilsyR8VRefreshTokenCandidate(payload);
  const tenantId = resolveWilsyR8VTenantFromPayload(payload);
  const user = payload.user || payload.data?.user || payload.session?.user || payload.result?.user || null;

  if (!token && !refreshToken) return false;

  try {
    if (token) {
      [
        'wilsy_auth_token',
        'token',
        'accessToken',
        'wilsy_token',
        'wilsy_access_token'
      ].forEach((key) => window.localStorage.setItem(key, token));
    }

    if (refreshToken) {
      [
        'refreshToken',
        'wilsy_refresh_token'
      ].forEach((key) => window.localStorage.setItem(key, refreshToken));
    }

    window.localStorage.setItem('tenantId', tenantId);
    window.localStorage.setItem('wilsyTenantId', tenantId);

    if (user && typeof user === 'object') {
      const safeUser = {
        ...user,
        tenantId: user.tenantId || tenantId
      };
      window.localStorage.setItem('user', JSON.stringify(safeUser));
      window.localStorage.setItem('wilsy_user', JSON.stringify(safeUser));
    }

    window.localStorage.setItem('wilsy_auth_capture_source', source);
    window.localStorage.setItem('wilsy_auth_capture_at', new Date().toISOString());
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * @function isWilsyR8VAuthTokenRoute
 * @description Detects auth endpoints whose responses may mint access or refresh tokens.
 * @collaboration Covers login, verify-3fa, verify-otp, and refresh-token response handling.
 */
const isWilsyR8VAuthTokenRoute = (url = '') => {
  const normalizedUrl = String(url || '');
  return [
    '/api/auth/login',
    '/api/auth/verify-3fa',
    '/api/auth/verify-otp',
    '/api/auth/refresh-token'
  ].some((route) => normalizedUrl.includes(route));
};

/**
 * @function installWilsyR8VFetchTokenCapture
 * @description Wraps fetch so successful auth responses are cloned, parsed, and persisted without consuming the app response.
 * @collaboration Allows existing auth UI code to continue reading responses while the session bridge stores tokens.
 */
const installWilsyR8VFetchTokenCapture = () => {
  if (typeof window === 'undefined' || typeof window.fetch !== 'function') return;
  if (window.__wilsyR8VFetchTokenCaptureInstalled) return;

  const originalFetch = window.fetch.bind(window);
  window.__wilsyR8VFetchTokenCaptureInstalled = true;

  window.fetch = async (input, init = {}) => {
    const url = typeof input === 'string' ? input : input?.url;
    const response = await originalFetch(input, init);

    if (isWilsyR8VAuthTokenRoute(url)) {
      response.clone().json()
        .then((payload) => persistWilsyR8VAuthPayload(payload, `${WILSY_R8V_AUTH_TOKEN_CAPTURE_BRIDGE_MARKER}:fetch`))
        .catch(() => {});
    }

    return response;
  };
};

/**
 * @function installWilsyR8VXhrTokenCapture
 * @description Wraps XMLHttpRequest so Axios auth responses are parsed and stored after completion.
 * @collaboration Repairs token persistence for Axios-driven MFA/login flows.
 */
const installWilsyR8VXhrTokenCapture = () => {
  if (typeof window === 'undefined' || typeof window.XMLHttpRequest !== 'function') return;
  if (window.__wilsyR8VXhrTokenCaptureInstalled) return;

  const originalOpen = window.XMLHttpRequest.prototype.open;
  const originalSend = window.XMLHttpRequest.prototype.send;

  window.__wilsyR8VXhrTokenCaptureInstalled = true;

/**
 * @function
 * @description Captures XMLHttpRequest auth endpoint URLs before Axios sends login, MFA, or refresh requests.
 * @collaboration Supports the R8V auth token capture bridge and preserves existing XMLHttpRequest behavior.
 */
  window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.__wilsyR8VUrl = typeof url === 'string' ? url : String(url || '');
    return originalOpen.call(this, method, url, ...rest);
  };

/**
 * @function
 * @description Observes completed XMLHttpRequest auth responses and persists returned tokens without exposing raw secrets.
 * @collaboration Supports MFA token storage, refresh-token continuity, and post-login session hydration.
 */
  window.XMLHttpRequest.prototype.send = function(...args) {
    if (isWilsyR8VAuthTokenRoute(this.__wilsyR8VUrl || '')) {
      this.addEventListener('load', () => {
        try {
          const payload = JSON.parse(this.responseText || '{}');
          persistWilsyR8VAuthPayload(payload, `${WILSY_R8V_AUTH_TOKEN_CAPTURE_BRIDGE_MARKER}:xhr`);
        } catch (error) {
          // Non-JSON auth responses cannot be persisted and are ignored.
        }
      });
    }

    return originalSend.apply(this, args);
  };
};

/**
 * @function installWilsyR8VAuthTokenCaptureBridge
 * @description Installs fetch and XHR token capture bridges once during tenant context bootstrap.
 * @collaboration Ensures successful login/MFA responses create a durable browser session before /api/auth/me runs.
 */
const installWilsyR8VAuthTokenCaptureBridge = () => {
  installWilsyR8VFetchTokenCapture();
  installWilsyR8VXhrTokenCapture();
};

installWilsyR8VAuthTokenCaptureBridge();



const WILSY_R8T_AUTH_HEADER_BRIDGE_MARKER = 'WILSY_R8T_AUTH_HEADER_BRIDGE_ACTIVE';

/**
 * @function readWilsyR8TStoredValue
 * @description Reads auth and tenant values from browser storage without throwing during early app boot.
 * @collaboration Supports tenantContext, authContext, and protected Wilsy OS API calls.
 */
const readWilsyR8TStoredValue = (key) => {
  if (typeof window === 'undefined') return '';
  try {
    return window.localStorage.getItem(key) || window.sessionStorage.getItem(key) || '';
  } catch (error) {
    return '';
  }
};

/**
 * @function resolveWilsyR8TAuthToken
 * @description Resolves the active Wilsy OS bearer token from all supported browser token slots.
 * @collaboration Keeps auth/me, CRM, account intelligence, and route discovery aligned after login.
 */
const resolveWilsyR8TAuthToken = () => (
  readWilsyR8TStoredValue('wilsy_auth_token')
  || readWilsyR8TStoredValue('token')
  || readWilsyR8TStoredValue('accessToken')
  || readWilsyR8TStoredValue('wilsy_token')
  || readWilsyR8TStoredValue('wilsy_access_token')
);

/**
 * @function resolveWilsyR8TTenantId
 * @description Resolves the canonical Wilsy root tenant id for protected browser API calls.
 * @collaboration Prevents MASTER/WILSY_ROOT display aliases from breaking backend tenant guard checks.
 */
const resolveWilsyR8TTenantId = () => (
  readWilsyR8TStoredValue('wilsyTenantId')
  || readWilsyR8TStoredValue('tenantId')
  || 'wilsy-sovereign-root'
);

/**
 * @function isWilsyR8TProtectedApiUrl
 * @description Detects protected API requests that must carry Authorization and tenant identity headers.
 * @collaboration Leaves public login, discovery, refresh, and telemetry routes untouched.
 */
const isWilsyR8TProtectedApiUrl = (url = '') => {
  const normalizedUrl = String(url || '');
  if (!normalizedUrl.includes('/api/')) return false;

  return ![
    '/api/auth/login',
    '/api/auth/discover',
    '/api/auth/refresh-token',
    '/api/auth/verify-3fa',
    '/api/auth/verify-otp',
    '/api/auth/webauthn-challenge',
    '/api/auth/anchor-hardware',
    '/api/telemetry/event',
    '/api/status'
  ].some((publicRoute) => normalizedUrl.includes(publicRoute));
};

/**
 * @function writeWilsyR8TAuthHeaders
 * @description Writes bearer, tenant, request id, trace id, and client headers to a Headers-compatible object.
 * @collaboration Gives protected frontend requests the institutional context required by backend guard middleware.
 */
const writeWilsyR8TAuthHeaders = (headers, url = '') => {
  if (!isWilsyR8TProtectedApiUrl(url)) return headers;

  const token = resolveWilsyR8TAuthToken();
  const tenantId = resolveWilsyR8TTenantId();
  const traceSeed = `WILSY-R8T-${Date.now()}`;

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!headers.has('X-Tenant-Id')) {
    headers.set('X-Tenant-Id', tenantId);
  }

  if (!headers.has('X-Wilsy-Tenant-ID')) {
    headers.set('X-Wilsy-Tenant-ID', tenantId);
  }

  if (!headers.has('X-Request-ID')) {
    headers.set('X-Request-ID', traceSeed);
  }

  if (!headers.has('X-Trace-ID')) {
    headers.set('X-Trace-ID', traceSeed);
  }

  if (!headers.has('X-Wilsy-Client')) {
    headers.set('X-Wilsy-Client', WILSY_R8T_AUTH_HEADER_BRIDGE_MARKER);
  }

  return headers;
};

/**
 * @function installWilsyR8TAuthHeaderBridge
 * @description Installs fetch and XMLHttpRequest bridges that attach auth headers to protected API traffic.
 * @collaboration Repairs tenantContext auth/me hydration while preserving public auth bootstrap routes.
 */
const installWilsyR8TAuthHeaderBridge = () => {
  if (typeof window === 'undefined' || window.__wilsyR8TAuthHeaderBridgeInstalled) return;

  window.__wilsyR8TAuthHeaderBridgeInstalled = true;

  if (typeof window.fetch === 'function') {
    const originalFetch = window.fetch.bind(window);

    window.fetch = (input, init = {}) => {
      const url = typeof input === 'string' ? input : input?.url;
      const headers = writeWilsyR8TAuthHeaders(new Headers(init?.headers || {}), url);

      return originalFetch(input, {
        ...init,
        headers
      });
    };
  }

  if (typeof window.XMLHttpRequest === 'function') {
    const originalOpen = window.XMLHttpRequest.prototype.open;
    const originalSend = window.XMLHttpRequest.prototype.send;

    window.XMLHttpRequest.prototype.open = function (...args) {
      const [, url] = args;
      this.__wilsyR8TUrl = typeof url === 'string' ? url : String(url || '');
      return originalOpen.apply(this, args);
    };

    window.XMLHttpRequest.prototype.send = function (...args) {
      const url = this.__wilsyR8TUrl || '';

      if (isWilsyR8TProtectedApiUrl(url)) {
        const token = resolveWilsyR8TAuthToken();
        const tenantId = resolveWilsyR8TTenantId();
        const traceSeed = `WILSY-R8T-${Date.now()}`;

        try {
          if (token) this.setRequestHeader('Authorization', `Bearer ${token}`);
          this.setRequestHeader('X-Tenant-Id', tenantId);
          this.setRequestHeader('X-Wilsy-Tenant-ID', tenantId);
          this.setRequestHeader('X-Request-ID', traceSeed);
          this.setRequestHeader('X-Trace-ID', traceSeed);
          this.setRequestHeader('X-Wilsy-Client', WILSY_R8T_AUTH_HEADER_BRIDGE_MARKER);
        } catch (error) {
          // Browser may reject duplicate late headers; existing request headers remain authoritative.
        }
      }

      return originalSend.apply(this, args);
    };
  }
};

// R8Z_DISABLED: installWilsyR8TAuthHeaderBridge();



const WILSY_R8S_XHR_DISCOVER_CANONICALIZER_MARKER = 'WILSY_R8S_XHR_DISCOVER_CANONICALIZER_ACTIVE';

/**
 * @function readWilsyR8SJsonBody
 * @description Safely reads an XMLHttpRequest JSON body so tenant discovery can be normalized for Axios-driven calls.
 * @collaboration Supports tenantContext, auth bootstrap, and real Wilsy root login discovery.
 */
const readWilsyR8SJsonBody = (body) => {
  if (!body || typeof body !== 'string') return {};
  try {
    return JSON.parse(body);
  } catch (error) {
    return {};
  }
};

/**
 * @function normalizeWilsyR8SDiscoverBody
 * @description Canonicalizes every auth discover payload to the backend-supported Wilsy alias while preserving request metadata.
 * @collaboration Aligns browser tenant discovery with the real Atlas user tenant wilsy-sovereign-root.
 */
const normalizeWilsyR8SDiscoverBody = (body = {}) => {
  const tenantId = body.tenantId || body.tenant || body.host || body.domain || 'wilsy-sovereign-root';
  const rawAlias = String(body.host || body.tenant || body.domain || tenantId || '').trim();
  const rootAlias = /^(MASTER|WILSY_ROOT|wilsy-sovereign-root)$/i.test(rawAlias);

  return {
    ...body,
    tenantId: tenantId === 'MASTER' || tenantId === 'WILSY_ROOT' ? 'wilsy-sovereign-root' : tenantId,
    tenant: rootAlias ? 'wilsy' : (body.tenant || 'wilsy'),
    domain: rootAlias ? 'wilsy' : (body.domain || 'wilsy'),
    host: rootAlias ? 'wilsy' : (body.host || 'wilsy'),
    source: body.source || WILSY_R8S_XHR_DISCOVER_CANONICALIZER_MARKER
  };
};

/**
 * @function installWilsyR8SXhrDiscoverCanonicalizer
 * @description Installs an XMLHttpRequest guard that rewrites only /api/auth/discover request bodies before Axios sends them.
 * @collaboration Prevents tenant discovery 404 loops while preserving all non-discovery API traffic.
 */
const installWilsyR8SXhrDiscoverCanonicalizer = () => {
  if (typeof window === 'undefined' || window.__wilsyR8SXhrDiscoverCanonicalizerInstalled) return;
  if (typeof window.XMLHttpRequest !== 'function') return;

  const originalOpen = window.XMLHttpRequest.prototype.open;
  const originalSend = window.XMLHttpRequest.prototype.send;
  const originalSetRequestHeader = window.XMLHttpRequest.prototype.setRequestHeader;

  window.__wilsyR8SXhrDiscoverCanonicalizerInstalled = true;

/**
 * @function
 * @description Captures XMLHttpRequest discover URLs so tenant discovery payloads can be canonicalized safely.
 * @collaboration Supports the R8S tenant discovery bridge and backend Wilsy root tenant resolution.
 */
  window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.__wilsyR8SMethod = method;
    this.__wilsyR8SUrl = typeof url === 'string' ? url : String(url || '');
    return originalOpen.call(this, method, url, ...rest);
  };

/**
 * @function
 * @description Tracks XMLHttpRequest headers during tenant discovery without changing unrelated API requests.
 * @collaboration Supports canonical tenant discovery, Axios compatibility, and backend route contract alignment.
 */
  window.XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
    this.__wilsyR8SHeaders = this.__wilsyR8SHeaders || {};
    this.__wilsyR8SHeaders[String(name).toLowerCase()] = value;
    return originalSetRequestHeader.call(this, name, value);
  };

/**
 * @function
 * @description Rewrites only /api/auth/discover XMLHttpRequest payloads to the canonical Wilsy tenant alias.
 * @collaboration Prevents discovery 404 loops while preserving all non-discovery browser traffic.
 */
  window.XMLHttpRequest.prototype.send = function(body) {
    const url = this.__wilsyR8SUrl || '';
    const isDiscoverRequest = url.includes('/api/auth/discover');

    if (!isDiscoverRequest) {
      return originalSend.call(this, body);
    }

    const nextBody = normalizeWilsyR8SDiscoverBody(readWilsyR8SJsonBody(body));

    try {
      originalSetRequestHeader.call(this, 'Content-Type', 'application/json');
      originalSetRequestHeader.call(this, 'X-Tenant-Id', nextBody.tenantId || 'wilsy-sovereign-root');
      originalSetRequestHeader.call(this, 'X-Wilsy-Discover-Canonicalizer', WILSY_R8S_XHR_DISCOVER_CANONICALIZER_MARKER);
    } catch (error) {
      // Header may already be locked by the browser; body canonicalization still carries the contract.
    }

    return originalSend.call(this, JSON.stringify(nextBody));
  };
};

installWilsyR8SXhrDiscoverCanonicalizer();



const WILSY_R8R_DISCOVER_CANONICALIZER_MARKER = 'WILSY_R8R_DISCOVER_CANONICALIZER_ACTIVE';
const WILSY_R8R_CANONICAL_DISCOVER_TENANT_ID = 'wilsy-sovereign-root';
const WILSY_R8R_CANONICAL_DISCOVER_ALIAS = 'wilsy';

/**
 * @function readWilsyR8RJsonBody
 * @description Safely reads a JSON fetch body so tenant discovery can be normalized before the request leaves the browser.
 * @collaboration Supports Wilsy OS tenant discovery, auth startup, and browser-side boot resilience.
 */
const readWilsyR8RJsonBody = (body) => {
  if (!body || typeof body !== 'string') return {};
  try {
    return JSON.parse(body);
  } catch (error) {
    return {};
  }
};

/**
 * @function normalizeWilsyR8RDiscoverBody
 * @description Converts root tenant aliases into the backend-supported discover contract while preserving request metadata.
 * @collaboration Keeps tenantContext, authContext, and the Express discovery route aligned for real Wilsy root login.
 */
const normalizeWilsyR8RDiscoverBody = (body = {}) => {
  const tenantId = body.tenantId || body.tenant || body.host || body.domain || WILSY_R8R_CANONICAL_DISCOVER_TENANT_ID;
  const rawAlias = String(body.host || body.tenant || body.domain || tenantId || '').trim();
  const rootAlias = /^(MASTER|WILSY_ROOT|wilsy-sovereign-root)$/i.test(rawAlias);

  return {
    ...body,
    tenantId: tenantId === 'MASTER' || tenantId === 'WILSY_ROOT' ? WILSY_R8R_CANONICAL_DISCOVER_TENANT_ID : tenantId,
    tenant: rootAlias ? WILSY_R8R_CANONICAL_DISCOVER_ALIAS : (body.tenant || WILSY_R8R_CANONICAL_DISCOVER_ALIAS),
    domain: rootAlias ? WILSY_R8R_CANONICAL_DISCOVER_ALIAS : (body.domain || WILSY_R8R_CANONICAL_DISCOVER_ALIAS),
    host: rootAlias ? WILSY_R8R_CANONICAL_DISCOVER_ALIAS : (body.host || WILSY_R8R_CANONICAL_DISCOVER_ALIAS),
    source: body.source || WILSY_R8R_DISCOVER_CANONICALIZER_MARKER
  };
};

/**
 * @function installWilsyR8RDiscoverCanonicalizer
 * @description Installs a browser fetch guard that rewrites only /api/auth/discover requests into a canonical Wilsy root discovery payload.
 * @collaboration Prevents tenant discovery loops before real-user login and MFA verification.
 */
const installWilsyR8RDiscoverCanonicalizer = () => {
  if (typeof window === 'undefined' || window.__wilsyR8RDiscoverCanonicalizerInstalled) return;
  if (typeof window.fetch !== 'function') return;

  const originalFetch = window.fetch.bind(window);

  window.__wilsyR8RDiscoverCanonicalizerInstalled = true;
  window.fetch = (input, init = {}) => {
    const url = typeof input === 'string' ? input : input?.url;
    const isDiscoverRequest = typeof url === 'string' && url.includes('/api/auth/discover');

    if (!isDiscoverRequest) {
      return originalFetch(input, init);
    }

    const originalBody = readWilsyR8RJsonBody(init?.body);
    const nextBody = normalizeWilsyR8RDiscoverBody(originalBody);
    const headers = new Headers(init?.headers || {});

    headers.set('Content-Type', 'application/json');
    headers.set('X-Tenant-Id', nextBody.tenantId || WILSY_R8R_CANONICAL_DISCOVER_TENANT_ID);
    headers.set('X-Wilsy-Discover-Canonicalizer', WILSY_R8R_DISCOVER_CANONICALIZER_MARKER);

    return originalFetch(input, {
      ...init,
      method: init?.method || 'POST',
      headers,
      body: JSON.stringify(nextBody)
    });
  };
};

installWilsyR8RDiscoverCanonicalizer();



const BREAKER_MAX_FAILURES = 3;
const BREAKER_COOLDOWN_MS = 30000;
const DEFAULT_TENANT_ALIAS = 'wilsy';
const DEFAULT_PRIMARY_COLOR = '#D4AF37';
const DEFAULT_SECONDARY_COLOR = '#8B5CF6';
const DEFAULT_ACCENT_COLOR = '#56D69B';

const TenantContext = createContext(null);

/**
 * @function resolveTenantColor
 * @description Resolves a safe tenant color from several backend-owned tenant fields.
 * @param {...string} candidates - Candidate color values.
 * @returns {string} Safe color value.
 * @collaboration Keeps every cockpit surface brand-aware without hardcoding tenant-specific styling inside dashboards.
 */
const resolveTenantColor = (...candidates) => {
  const found = candidates.find(value => typeof value === 'string' && value.trim().length > 0);
  return found || DEFAULT_PRIMARY_COLOR;
};

/**
 * @function resolveTenantLogo
 * @description Resolves the safest tenant logo reference without inventing a browser URL.
 * @param {Object} tenant - Active tenant object.
 * @returns {string} Logo reference.
 * @collaboration Lets executive and profile surfaces use the same tenant logo source without duplicating lookup logic.
 */
const resolveTenantLogo = (tenant = {}) => (
  tenant.logo
  || tenant.branding?.logo
  || tenant.brandingNexus?.logo
  || tenant.theme?.logo
  || 'DEFAULT_LOGO'
);

/**
 * @function buildTenantBranding
 * @description Converts a tenant record into a cockpit-safe branding and profile contract.
 * @param {Object|null} tenant - Tenant record from backend discovery or direct injection.
 * @returns {Object} Normalized tenant branding contract.
 * @collaboration Gives ExecutiveDashboard, profile settings, and future OS surfaces one source of truth for tenant identity.
 */
const buildTenantBranding = (tenant = null) => {
  const source = tenant || {};
  const primaryColor = resolveTenantColor(
    source.primaryColor,
    source.branding?.primaryColor,
    source.brandingNexus?.color,
    source.theme?.primaryColor,
    DEFAULT_PRIMARY_COLOR
  );
  const secondaryColor = resolveTenantColor(
    source.secondaryColor,
    source.branding?.secondaryColor,
    source.theme?.secondaryColor,
    DEFAULT_SECONDARY_COLOR
  );
  const accentColor = resolveTenantColor(
    source.accentColor,
    source.branding?.accentColor,
    source.theme?.accentColor,
    DEFAULT_ACCENT_COLOR
  );
  const tenantName = source.companyName
    || source.name
    || source.legalName
    || source.branding?.companyName
    || source.alias
    || 'Wilsy OS Root';

  return {
    tenantId: source.tenantId || source.id || 'MASTER',
    alias: source.alias || source.slug || DEFAULT_TENANT_ALIAS,
    name: tenantName,
    companyName: tenantName,
    industry: source.industry || source.industryName || source.businessFamily || source.profile?.industry || 'Technology, SaaS and Digital Product',
    businessModel: source.businessModel || source.profile?.businessModel || source.industryKey || 'tenant_auto_detect',
    logo: resolveTenantLogo(source),
    primaryColor,
    secondaryColor,
    accentColor,
    billingStatus: source.billingStatus || 'ACTIVE',
    edition: source.edition || source.plan || source.subscription?.edition || 'Sovereign Command',
    authority: source.authority || source.ownerRole || 'Root Tenant Control',
    sourceStatus: source.sourceStatus || 'TENANT_CONTEXT',
    raw: source
  };
};

/**
 * @function generateForensicHeaders
 * @description Generates trace, timestamp, nonce, and seal headers for tenant discovery requests.
 * @param {Object} payload - Discovery payload.
 * @returns {Object} Forensic request headers.
 * @collaboration Backend tenant discovery receives sealed context without exposing sensitive values in the browser.
 */
const generateForensicHeaders = (payload = {}) => {
  const traceId = `TRC-TENANT-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;
  const timestamp = new Date().toISOString();
  const nonce = `NONCE-CTX-${Math.random().toString(36).substring(2, 15)}`;
  const messageToSeal = `${traceId}|${timestamp}|${JSON.stringify(payload)}|${nonce}`;
  const seal = generateSovereignSeal(messageToSeal);

  return {
    'x-trace-id': traceId,
    'x-forensic-timestamp': timestamp,
    'x-cryptographic-nonce': nonce,
    'x-request-seal': seal
  };
};

/**
 * @function safeMeshBroadcast
 * @description Sends mesh events when available and degrades safely when the frontend mesh is not mounted.
 * @param {Object} meshContext - Sovereign mesh context.
 * @param {string} targetId - Mesh target id.
 * @param {Object} payload - Event payload.
 * @param {string} eventType - Event label.
 * @returns {void}
 * @collaboration Tenant discovery must never crash the React tree because a mesh transport is unavailable.
 */
const safeMeshBroadcast = (meshContext, targetId, payload, eventType) => {
  try {
    if (meshContext && typeof meshContext.propagate === 'function') {
      meshContext.propagate(targetId, payload, eventType)
        .catch(err => console.warn(`[Mesh] ${eventType} propagation failed:`, err));
      return;
    }

    if (meshContext && typeof meshContext.emit === 'function') {
      meshContext.emit(eventType, { target: targetId, ...payload });
      return;
    }

    console.debug(`[Mesh-Simulated] Frontend decoupled. Suppressed broadcast: ${eventType}`);
  } catch (err) {
    console.warn('[Mesh] Safe broadcast failure:', err);
  }
};

/**
 * @function TenantProvider
 * @description Provides tenant discovery, tenant branding, circuit breaker state, and boardroom-safe tenant telemetry to the app.
 * @param {Object} props - Provider props.
 * @param {React.ReactNode} props.children - Child React tree.
 * @returns {JSX.Element} Tenant context provider.
 * @collaboration This is the tenant control plane used by ExecutiveDashboard, profile settings, and sovereign shell routing.
 */
export const TenantProvider = ({ children }) => {
  const mesh = useSovereignMesh();
  const sovereignData = useSovereignData();
  const { isAuthenticated, user } = useAuth();

  const [activeTenant, setActiveTenantState] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [circuitBreaker, setCircuitBreaker] = useState('CLOSED');
  const [boardroomSummary, setBoardroomSummary] = useState({
    uptimeStatus: 'STABLE',
    avgSlaLatencyMs: 0,
    breakerTransitions: 0,
    complianceStatus: 'VERIFIED'
  });

  const failureCountRef = useRef(0);
  const lastFailureTimeRef = useRef(0);
  const latencyHistoryRef = useRef([]);

  /**
   * @function updateBreakerState
   * @description Updates the discovery circuit breaker and broadcasts the transition.
   * @param {string} newState - Next circuit breaker state.
   * @param {string} tenantAlias - Tenant alias involved in the transition.
   * @returns {void}
   * @collaboration Backend outage states become visible without allowing cascading tenant discovery failures.
   */
  const updateBreakerState = useCallback((newState, tenantAlias) => {
    setCircuitBreaker(current => {
      if (current === newState) return current;

      setBoardroomSummary(prev => ({
        ...prev,
        breakerTransitions: prev.breakerTransitions + 1,
        uptimeStatus: newState === 'OPEN' ? 'FRACTURED' : 'STABLE'
      }));

      broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_EVENT', 'BREAKER_STATE_TRANSITION', 'TenantContext', {
        previousState: current,
        newState,
        tenantAlias,
        severity: newState === 'OPEN' ? 'HIGH' : 'LOW'
      }).catch(() => {});

      safeMeshBroadcast(mesh, 'GLOBAL_ROOT', { previousState: current, newState, tenantAlias }, 'BREAKER_STATE_CHANGE');

      return newState;
    });
  }, [mesh]);

  /**
   * @function hydrateTenantObject
   * @description Enriches a tenant object with required cockpit fields and persists the alias.
   * @param {Object} tenantData - Tenant record.
   * @param {string} fallbackAlias - Alias used when the tenant object lacks one.
   * @returns {Object} Enriched tenant record.
   * @collaboration Centralizes tenant branding and profile enrichment so dashboards do not invent missing identity fields.
   */
  const hydrateTenantObject = useCallback((tenantData = {}, fallbackAlias = DEFAULT_TENANT_ALIAS) => {
    const branding = buildTenantBranding({
      ...tenantData,
      alias: tenantData.alias || fallbackAlias
    });
    const enrichedTenant = {
      ...tenantData,
      alias: tenantData.alias || branding.alias,
      tenantId: tenantData.tenantId || tenantData.id || branding.tenantId,
      billingStatus: tenantData.billingStatus || branding.billingStatus,
      primaryColor: branding.primaryColor,
      secondaryColor: branding.secondaryColor,
      accentColor: branding.accentColor,
      logo: branding.logo,
      tenantBranding: branding,
      profile: {
        ...(tenantData.profile || {}),
        name: branding.name,
        industry: branding.industry,
        businessModel: branding.businessModel,
        sourceStatus: branding.sourceStatus
      }
    };

    setActiveTenantState(enrichedTenant);
    localStorage.setItem('discoveredTenant', enrichedTenant.alias || fallbackAlias);

    return enrichedTenant;
  }, []);

  /**
   * @function resolveTenantSingularity
   * @description Resolves a tenant alias or tenant object into the active tenant context.
   * @param {string|Object} tenantIdOrObject - Tenant alias, tenant id, or already resolved tenant object.
   * @returns {Promise<Object|null>} Resolved tenant or null when discovery is blocked or unavailable.
   * @collaboration Founder and Omega users route to the sovereign root shard while normal tenants retain isolated discovery.
   */
  const resolveTenantSingularity = useCallback(async (tenantIdOrObject) => {
    if (typeof tenantIdOrObject === 'object' && tenantIdOrObject !== null) {
      const enrichedTenant = hydrateTenantObject(tenantIdOrObject, tenantIdOrObject.alias || tenantIdOrObject.tenantId || DEFAULT_TENANT_ALIAS);
      safeMeshBroadcast(mesh, enrichedTenant.tenantId, { source: 'direct_object' }, 'TENANT_LOADED');
      return enrichedTenant;
    }

    let target = tenantIdOrObject && tenantIdOrObject !== 'undefined'
      ? tenantIdOrObject
      : localStorage.getItem('discoveredTenant');

    const userRole = user?.role?.toUpperCase();
    if (userRole === 'FOUNDER' || userRole === 'OMEGA') {
      target = DEFAULT_TENANT_ALIAS;
    }

    const anchorTarget = target && target !== 'undefined' ? target : DEFAULT_TENANT_ALIAS;

    if (circuitBreaker === 'OPEN') {
      const timeSinceFailure = Date.now() - lastFailureTimeRef.current;
      if (timeSinceFailure > BREAKER_COOLDOWN_MS) {
        updateBreakerState('HALF_OPEN', anchorTarget);
      } else {
        safeMeshBroadcast(mesh, 'GLOBAL_ROOT', { target: anchorTarget, reason: 'BREAKER_OPEN' }, 'DISCOVERY_BLOCKED');
        return null;
      }
    }

    setIsSyncing(true);

    const payload = { host: anchorTarget };
    const forensicHeaders = generateForensicHeaders(payload);

    try {
      const start = performance.now();
      const response = await api.post('/auth/discover', payload, { headers: { ...forensicHeaders } });
      const tenantData = response.data.tenant;
      const chainSeal = response.data.chainSeal;

      safeMeshBroadcast(mesh, tenantData.tenantId, { alias: anchorTarget, chainSeal }, 'FORENSIC_CHAIN_VERIFICATION');

      const duration = performance.now() - start;
      latencyHistoryRef.current.push(duration);
      if (latencyHistoryRef.current.length > 10) latencyHistoryRef.current.shift();

      const movingAvg = Math.round(
        latencyHistoryRef.current.reduce((sum, value) => sum + value, 0) / latencyHistoryRef.current.length
      );

      setBoardroomSummary(prev => ({ ...prev, avgSlaLatencyMs: movingAvg }));
      failureCountRef.current = 0;

      if (circuitBreaker !== 'CLOSED') {
        updateBreakerState('CLOSED', anchorTarget);
      }

      const enrichedTenant = hydrateTenantObject(tenantData, anchorTarget);

      safeMeshBroadcast(mesh, enrichedTenant.tenantId, { alias: anchorTarget, latencyMs: duration }, 'TENANT_DISCOVERY_SUCCESS');

      return enrichedTenant;
    } catch (err) {
      failureCountRef.current += 1;
      lastFailureTimeRef.current = Date.now();

      safeMeshBroadcast(mesh, 'GLOBAL_ROOT', { target: anchorTarget, error: err.message }, 'DISCOVERY_FAILURE');

      if (failureCountRef.current >= BREAKER_MAX_FAILURES && circuitBreaker !== 'OPEN') {
        updateBreakerState('OPEN', anchorTarget);
      }

      return null;
    } finally {
      setIsSyncing(false);
    }
  }, [circuitBreaker, hydrateTenantObject, mesh, updateBreakerState, user?.role]);

  useEffect(() => {
    if (!isAuthenticated || activeTenant) return;

    const fallbackTenant = user?.tenantAlias
      || user?.tenantId
      || localStorage.getItem('discoveredTenant')
      || DEFAULT_TENANT_ALIAS;

    resolveTenantSingularity(fallbackTenant).catch(() => {});
  }, [activeTenant, isAuthenticated, resolveTenantSingularity, user]);

  useEffect(() => {
    const saved = localStorage.getItem('discoveredTenant');

    if (saved && saved !== 'undefined' && !activeTenant && circuitBreaker === 'CLOSED') {
      resolveTenantSingularity(saved).catch(() => {});
    }
  }, [activeTenant, circuitBreaker, resolveTenantSingularity]);

  const tenantBranding = useMemo(() => buildTenantBranding(activeTenant), [activeTenant]);

  const value = useMemo(() => ({
    activeTenant,
    tenantBranding,
    isSyncing,
    circuitBreaker,
    boardroomSummary,
    sovereignData,
    resolveTenant: resolveTenantSingularity,
    setActiveTenant: resolveTenantSingularity
  }), [
    activeTenant,
    boardroomSummary,
    circuitBreaker,
    isSyncing,
    resolveTenantSingularity,
    sovereignData,
    tenantBranding
  ]);

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
};

/**
 * @function useTenants
 * @description Reads the Wilsy OS tenant context.
 * @returns {Object|null} Tenant context value.
 * @collaboration Gives dashboards, settings, and service clients one governed way to read tenant identity and branding.
 */
export const useTenants = () => useContext(TenantContext);

export default TenantContext;
