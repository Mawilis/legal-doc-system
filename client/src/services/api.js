/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DIPLOMATIC BRIDGE [V72.4.0-PRODUCTION-INTEGRATED]                                                                           ║
 * ║ [KEY‑SORTED SEALING | MILLISECOND PRECISION | ATOMIC QUEUE | 401 AUTO-HEALING | TENANT-FORCE | APEX-SNIFFER]                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 72.4.0-PRODUCTION-INTEGRATED | BILLION DOLLAR SPEC                                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/api.js                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated permanent 401/403/Tenant resolution.                                                 ║
 * ║ • AI Engineering (Gemini) – PATCHED: Full integration of Apex Sniffer and Tenant Forcing. JSDoc/Structure preserved exactly.           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import axios from 'axios';
import { sha3_512 } from 'js-sha3';
import { generateTraceAnchor, broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * @constant {axios.AxiosInstance} api
 * @description The primary sovereign HTTP client for WILSY OS.
 * Every request is cryptographically sealed with a deterministic SHA3-512 hash,
 * synchronised with the server's master clock (millisecond precision), and queued
 * atomically during quantum key rotation.
 *
 * @real-world
 * Used by all frontend services (auth, billing, compliance, telemetry) to communicate
 * with the backend. Injects forensic headers and handles token refresh on 401.
 *
 * @forensic
 * - Seals every request with a deterministic hash matching the backend signature precisely.
 * - Supports atomic request queueing during token refresh to prevent race conditions.
 * - Purges invalid sessions and redirects to login when refresh fails.
 * - Apex sniffer actively harvests valid JWTs from successful API responses.
 */
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-Quantum-Verified': 'true',
  },
  timeout: 15000,
});

const SOURCE_BACKOFF_MS = Number(import.meta.env?.VITE_SOURCE_BACKOFF_MS || 45000);
const sourceBackoffUntil = new Map();

/**
 * @function getSourceBackoffKey
 * @description Builds a stable key for degraded GET sources so React dev-mode duplicate effects do not reflood 503 endpoints.
 * @param {Object} config - Axios request config.
 * @returns {string} Source backoff key.
 * @collaboration Wilson Khanyezi requires source-silent posture, not console-noise theatre during backend degradation.
 */
const getSourceBackoffKey = (config = {}) => {
  const method = String(config.method || 'get').toUpperCase();
  const url = String(config.url || '');
  const params = config.params ? JSON.stringify(sortKeys(config.params)) : '';
  return `${method}:${url}:${params}`;
};

/**
 * @function isSourceBackoffEligible
 * @description Determines whether a request can be locally suppressed during a 503 source backoff window.
 * @param {Object} config - Axios request config.
 * @returns {boolean} True when the request is a safe source-read GET.
 */
const isSourceBackoffEligible = (config = {}) => (
  String(config.method || 'get').toLowerCase() === 'get'
  && !config.forceNetworkRetry
  && !config.disableSourceBackoff
);

/**
 * @function isDegradedSourceFailure
 * @description Treats 503s and request timeouts as source-silent reads eligible for short local backoff.
 * @param {Error} error - Axios error.
 * @returns {boolean} True when the source is degraded rather than operator-auth failed.
 */
const isDegradedSourceFailure = (error = {}) => (
  error.response?.status === 503
  || error.code === 'ECONNABORTED'
  || String(error.message || '').toLowerCase().includes('timeout')
);

/**
 * @function buildSourceBackoffError
 * @description Creates an axios-shaped local rejection for a suppressed degraded source read.
 * @param {Object} config - Axios request config.
 * @returns {Error} Backoff error.
 */
const buildSourceBackoffError = (config = {}) => {
  const error = new Error('SOURCE_BACKOFF_ACTIVE');
  error.config = config;
  error.isSourceBackoff = true;
  error.response = {
    status: 503,
    data: {
      success: false,
      code: 'SOURCE_BACKOFF_ACTIVE',
      message: 'Source recently returned 503. Local backoff is preserving the cockpit from duplicate degraded probes.',
      sourceStatus: 'SOURCE_SILENT'
    }
  };
  return error;
};

// ============================================================================
// 🔑 TOKEN STORAGE STANDARDISATION (single source of truth)
// ============================================================================

const TOKEN_KEY = 'wilsy_auth_token';
const REFRESH_TOKEN_KEY = 'wilsy_refresh_token';

/**
 * @function getStoredToken
 * @description Retrieves the stored authentication token, stripping any JSON quotes.
 * @returns {string|null}
 */
const getStoredToken = () => {
  const raw = localStorage.getItem(TOKEN_KEY) || localStorage.getItem('token') || sessionStorage.getItem('token');
  if (!raw || raw === 'undefined' || raw === 'null') return null;
  return raw.replace(/^["']|["']$/g, '');
};

/**
 * @function getStoredRefreshToken
 * @description Retrieves the stored refresh token, stripping quotes.
 * @returns {string|null}
 */
const getStoredRefreshToken = () => {
  const raw = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!raw || raw === 'undefined' || raw === 'null') return null;
  return raw.replace(/^["']|["']$/g, '');
};

/**
 * @function setTokens
 * @description Stores access and refresh tokens consistently.
 * @param {string} accessToken
 * @param {string} refreshToken
 */
const setTokens = (accessToken, refreshToken) => {
  if (accessToken) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem('token', accessToken); // Backup sync
  }
  if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

/**
 * @function purgeTokens
 * @description Clears all authentication artifacts.
 */
const purgeTokens = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem('token');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('jwt');
  sessionStorage.removeItem('token');
};

// ============================================================================
// ⏱️ SERVER-TIME SYNCHRONISATION (millisecond precision)
// ============================================================================

let serverTimeOffset = 0;
const TIME_SYNC_INTERVAL = 5 * 60 * 1000;

/**
 * @function syncServerTime
 * @description Performs a non‑recursive status check to calculate the drift
 * between the local client clock and the server master clock.
 * @returns {Promise<void>}
 */
const syncServerTime = async () => {
  try {
    const start = Date.now();
    const response = await axios.get('/api/status', { timeout: 5000 });
    const serverTime = new Date(response.data.timestamp).getTime();
    const roundTrip = Date.now() - start;
    serverTimeOffset = serverTime - (start + roundTrip / 2);
  } catch (err) {
    console.warn('[TIME-SYNC] Falling back to local clock.', err.message);
  }
};

/**
 * @function getSyncedTimestamp
 * @returns {string} ISO timestamp adjusted by server offset.
 */
const getSyncedTimestamp = () => {
  const now = Date.now() + serverTimeOffset;
  return new Date(now).toISOString();
};

syncServerTime();
setInterval(syncServerTime, TIME_SYNC_INTERVAL);

// ============================================================================
// ⚙️ ATOMIC QUEUE ENGINE
// ============================================================================

let isRotating = false;
let requestQueue = [];

const processQueue = (error, token = null) => {
  requestQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  requestQueue = [];
};

// ============================================================================
// 🧹 DETERMINISTIC SORTING (for seal parity)
// ============================================================================

const sortKeys = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(sortKeys);
  return Object.keys(obj).sort().reduce((acc, key) => {
    acc[key] = sortKeys(obj[key]);
    return acc;
  }, {});
};

// ============================================================================
// 🛡️ INTERCEPTORS – FORENSIC SEALING
// ============================================================================

api.interceptors.request.use(
  async (config) => {
    config.metadata = { startTime: performance.now() };

    if (config.url) {
      config.url = config.url.replace(/^\/?api\//, '/');
      if (!config.url.startsWith('/')) config.url = '/' + config.url;
    }

    if (isSourceBackoffEligible(config)) {
      const backoffKey = getSourceBackoffKey(config);
      const blockedUntil = sourceBackoffUntil.get(backoffKey) || 0;
      if (Date.now() < blockedUntil) {
        return Promise.reject(buildSourceBackoffError(config));
      }
    }

    if (isRotating) {
      return new Promise((resolve, reject) => {
        requestQueue.push({ resolve, reject });
      }).then(() => config);
    }

    const token = getStoredToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;

    // FORCE: Tenant ID injection to prevent 403s
    let tenantId = localStorage.getItem('discoveredTenant');
    if (!tenantId || tenantId === 'undefined' || tenantId === 'null') {
      tenantId = 'GLOBAL_ROOT';
      localStorage.setItem('discoveredTenant', tenantId);
    }
    config.headers['X-Tenant-ID'] = tenantId;

    const isPublicPath = /^\/status$/i.test(config.url)
      || /^\/telemetry\/(pulse|event|error)$/i.test(config.url);

    if (!isPublicPath) {
      const traceId = generateTraceAnchor ? generateTraceAnchor() : `TRC-${Date.now()}`;
      const timestamp = getSyncedTimestamp();
      const nonce = `NONCE-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;

      if (config.data && typeof config.data === 'object') {
        config.data.timestamp = timestamp;
      }

      const sortedPayload = sortKeys(config.data || {});
      const payloadStr = ['GET', 'DELETE', 'HEAD', 'OPTIONS'].includes(config.method?.toUpperCase()) ? '{}' : JSON.stringify(sortedPayload);

      const message = `${traceId}|${timestamp}|${payloadStr}|${nonce}`;
      const calculatedSeal = sha3_512(message).toLowerCase();

      config.headers['x-trace-id'] = traceId;
      config.headers['x-forensic-timestamp'] = timestamp;
      config.headers['x-cryptographic-nonce'] = nonce;
      config.headers['x-request-seal'] = calculatedSeal;

      if (process.env.NODE_ENV === 'development') {
        console.log(`[BRIDGE] 🔒 Sealed ${config.method?.toUpperCase()} ${config.url}`);
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ============================================================================
// 🔄 RESPONSE INTERCEPTOR – 401 AUTO-HEALING WITH REFRESH TOKEN
// ============================================================================

api.interceptors.response.use(
  (response) => {
    // 💥 APEX SNIFFER: Intercept every successful response and aggressively harvest tokens
    const harvestedToken = response.data?.token || response.data?.accessToken || response.headers['authorization']?.replace(/^Bearer\s+/i, '');
    const harvestedRefresh = response.data?.refreshToken;

    if (harvestedToken) {
      setTokens(harvestedToken, harvestedRefresh);
      if (process.env.NODE_ENV === 'development') {
        console.log('[BRIDGE] 🔐 Neural Sniffer captured and anchored fresh Identity Token.');
      }
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const url = originalRequest?.url || '';

    if (error.isSourceBackoff) {
      return Promise.reject(error);
    }

    if (isDegradedSourceFailure(error) && originalRequest && isSourceBackoffEligible(originalRequest)) {
      sourceBackoffUntil.set(getSourceBackoffKey(originalRequest), Date.now() + SOURCE_BACKOFF_MS);
    }

    if (error.response?.status === 401 && originalRequest?.skipAuthRedirect) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401) {
      // Prevent infinite loop on refresh or login endpoints
      if (url.includes('/auth/refresh-token') || url.includes('/auth/login')) {
        purgeTokens();
        window.location.href = '/login?expired=true';
        return Promise.reject(error);
      }

      if (!originalRequest._retry) {
        if (isRotating) {
          return new Promise((resolve, reject) => {
            requestQueue.push({ resolve, reject });
          }).then(() => api(originalRequest));
        }

        originalRequest._retry = true;
        isRotating = true;

        try {
          const refreshToken = getStoredRefreshToken();
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          // Send the refresh token in the body – this is what the backend expects
          const refreshResponse = await axios.post('/api/auth/refresh-token', {
            refreshToken: refreshToken
          }, {
            timeout: 8000,
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${getStoredToken() || refreshToken}`,
              'X-Tenant-ID': localStorage.getItem('discoveredTenant') || localStorage.getItem('tenantId') || 'wilsy'
            }
          });

          const newAccessToken = refreshResponse.data?.token || refreshResponse.data?.accessToken;
          const newRefreshToken = refreshResponse.data?.refreshToken;

          if (!newAccessToken) {
            throw new Error('Refresh response missing access token');
          }

          // Store the new tokens
          setTokens(newAccessToken, newRefreshToken);

          // Update the failed request's Authorization header
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

          isRotating = false;
          processQueue(null, newAccessToken);

          // Retry the original request
          return api(originalRequest);
        } catch (refreshError) {
          console.error('[BRIDGE] Token refresh failed:', refreshError);
          isRotating = false;
          processQueue(refreshError, null);
          purgeTokens();
          window.location.href = '/login?expired=true';
          return Promise.reject(error);
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
