/* eslint-disable */
import sha3Pkg from 'js-sha3';

const { sha3_512 } = sha3Pkg;
/**
 * WILSY OS — CLIENT SOURCE REGISTRY SERVICE
 * VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA
 * FILE: client/src/services/sourceRegistryService.js
 *
 * Purpose:
 * - Calls the real backend Source Registry endpoints.
 * - Never fabricates VERIFIED.
 * - Treats PENDING/MISSING/ERROR as real operational states.
 */

const API_BASE_URL =
  import.meta?.env?.VITE_API_URL ||
  import.meta?.env?.VITE_API_BASE_URL ||
  'http://localhost:5050';

const SOURCE_REGISTRY_BASE = `${String(API_BASE_URL).replace(/\/$/, '')}/api/source-registry`;

export const SOURCE_REGISTRY_STATUS = Object.freeze({
  VERIFIED: 'VERIFIED',
  PENDING: 'PENDING',
  MISSING: 'MISSING',
  ERROR: 'ERROR',
  BLOCKED: 'BLOCKED',
  READY_FOR_ANCHOR: 'READY_FOR_ANCHOR',
  NOT_EVALUATED: 'NOT_EVALUATED'
});

function readToken() {
  return (
    localStorage.getItem('wilsy_token') ||
    localStorage.getItem('token') ||
    localStorage.getItem('authToken') ||
    localStorage.getItem('accessToken') ||
    sessionStorage.getItem('wilsy_token') ||
    sessionStorage.getItem('token') ||
    sessionStorage.getItem('authToken') ||
    sessionStorage.getItem('accessToken') ||
    ''
  );
}

function normalizeTenantId(tenantId) {
  return String(tenantId || localStorage.getItem('tenantId') || 'MASTER').trim() || 'MASTER';
}


// WILSY_SOURCE_REGISTRY_SIGNED_POST_HELPERS
// Mirrors backend ProductionHardening.middleware.js seal reconstruction:
// SHA3-512(traceId|timestamp|stablePayloadString|nonce)
function sortKeysForSeal(value) {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map(sortKeysForSeal);

  return Object.keys(value).sort().reduce((acc, key) => {
    acc[key] = sortKeysForSeal(value[key]);
    return acc;
  }, {});
}

function stableStringifyForSeal(value) {
  return JSON.stringify(sortKeysForSeal(value || {}));
}

function createCryptographicNonce() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();

  const bytes = new Uint8Array(16);
  window.crypto.getRandomValues(bytes);

  return Array.from(bytes)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

function buildSourceRegistryIntegrityHeaders(body, traceId) {
  const finalTraceId = traceId || `SRC-UI-${Date.now().toString(16).toUpperCase()}-${Math.random().toString(16).slice(2, 10).toUpperCase()}`;
  const timestamp = new Date().toISOString();
  const nonce = createCryptographicNonce();
  const payloadString = stableStringifyForSeal(body);
  const reconstruction = `${finalTraceId}|${timestamp}|${payloadString}|${nonce}`;
  const requestSeal = sha3_512(reconstruction).toUpperCase();

  return {
    traceId: finalTraceId,
    headers: {
      'X-Trace-ID': finalTraceId,
      'X-Forensic-Timestamp': timestamp,
      'X-Cryptographic-Nonce': nonce,
      'X-Request-Seal': requestSeal,
      'X-Request-Proof': requestSeal,
      'X-Quantum-Verified': 'true'
    }
  };
}

function buildHeaders({ tenantId, traceId, json = true } = {}) {
  const token = readToken();
  const headers = {
    Accept: 'application/json',
    'X-Tenant-Id': normalizeTenantId(tenantId),
    'X-Trace-ID': traceId || `SRC-UI-${Date.now().toString(16).toUpperCase()}`
  };

  if (json) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function parseJsonResponse(response) {
  const raw = await response.text();

  let payload = null;
  try {
    payload = raw ? JSON.parse(raw) : null;
  } catch {
    payload = {
      success: false,
      error: {
        code: 'SOURCE_REGISTRY_INVALID_JSON',
        message: raw || 'Backend returned non-JSON response.'
      }
    };
  }

  if (!response.ok) {
    const message =
      payload?.error?.message ||
      payload?.message ||
      payload?.error ||
      `Source Registry request failed with HTTP ${response.status}`;

    const error = new Error(message);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

async function requestSourceRegistry(path, options = {}) {
  const {
    method = 'GET',
    tenantId = 'MASTER',
    traceId,
    body,
    signal
  } = options;

  const methodUpper = String(method || 'GET').toUpperCase();
  const hasBody = body !== undefined;
  const requiresIntegritySeal = hasBody && !['GET', 'HEAD', 'OPTIONS'].includes(methodUpper);
  const integrity = requiresIntegritySeal
    ? buildSourceRegistryIntegrityHeaders(body, traceId)
    : { traceId, headers: {} };

  const response = await fetch(`${SOURCE_REGISTRY_BASE}${path}`, {
    method: methodUpper,
    headers: {
      ...buildHeaders({
        tenantId,
        traceId: integrity.traceId || traceId,
        json: hasBody
      }),
      ...integrity.headers
    },
    body: hasBody ? JSON.stringify(body) : undefined,
    credentials: 'include',
    signal
  });

  const payload = await parseJsonResponse(response);

  if (typeof window !== 'undefined' && path === '/verify') {
    window.__WILSY_LAST_SOURCE_REGISTRY__ = payload;
  }

  return payload;
}

export async function getSourceRegistryHealth(options = {}) {
  return requestSourceRegistry('/health', {
    ...options,
    method: 'GET'
  });
}

export async function getSourceRegistryStatus(options = {}) {
  return requestSourceRegistry('/status', {
    ...options,
    method: 'GET'
  });
}

export async function verifySourceRegistry({ artifacts = [], artifact = null, catalog = null, tenantId = 'MASTER', traceId } = {}) {
  const body = {
    tenantId,
    traceId,
    ...(Array.isArray(catalog) ? { catalog } : {}),
    ...(Array.isArray(artifacts) && artifacts.length ? { artifacts } : {}),
    ...(artifact ? { artifact } : {})
  };

  return requestSourceRegistry('/verify', {
    method: 'POST',
    tenantId,
    traceId,
    body
  });
}

export async function sealBoardroomProof({ verification = null, artifacts = [], artifact = null, tenantId = 'MASTER', traceId } = {}) {
  const body = {
    tenantId,
    traceId,
    ...(verification ? { verification } : {}),
    ...(Array.isArray(artifacts) && artifacts.length ? { artifacts } : {}),
    ...(artifact ? { artifact } : {})
  };

  return requestSourceRegistry('/seal-boardroom-proof', {
    method: 'POST',
    tenantId,
    traceId,
    body
  });
}

export async function buildInvestorPack({ verification = null, artifacts = [], artifact = null, tenantId = 'MASTER', traceId } = {}) {
  const body = {
    tenantId,
    traceId,
    ...(verification ? { verification } : {}),
    ...(Array.isArray(artifacts) && artifacts.length ? { artifacts } : {}),
    ...(artifact ? { artifact } : {})
  };

  return requestSourceRegistry('/investor-pack', {
    method: 'POST',
    tenantId,
    traceId,
    body
  });
}

export function summarizeSourceRegistry(registryPayload) {
  const data = registryPayload?.data || registryPayload || {};
  const summary = data.summary || {};

  return {
    status: data.status || SOURCE_REGISTRY_STATUS.NOT_EVALUATED,
    total: Number(summary.total || 0),
    verified: Number(summary.verified || 0),
    pending: Number(summary.pending || 0),
    missing: Number(summary.missing || 0),
    error: Number(summary.error || 0),
    blocked: Number(summary.blocked || 0),
    evidenceStatus: data.evidenceStatus || SOURCE_REGISTRY_STATUS.NOT_EVALUATED,
    registryHash: data.registryHash || null,
    hashAlgorithm: data.hashAlgorithm || null,
    connectors: Array.isArray(data.connectors) ? data.connectors : []
  };
}

export function statusTone(status) {
  switch (String(status || '').toUpperCase()) {
    case SOURCE_REGISTRY_STATUS.VERIFIED:
    case SOURCE_REGISTRY_STATUS.READY_FOR_ANCHOR:
      return 'verified';
    case SOURCE_REGISTRY_STATUS.PENDING:
    case SOURCE_REGISTRY_STATUS.NOT_EVALUATED:
      return 'pending';
    case SOURCE_REGISTRY_STATUS.MISSING:
      return 'missing';
    case SOURCE_REGISTRY_STATUS.ERROR:
    case SOURCE_REGISTRY_STATUS.BLOCKED:
      return 'error';
    default:
      return 'unknown';
  }
}

export function isSourceRegistryReady(registryPayload) {
  const summary = summarizeSourceRegistry(registryPayload);
  return summary.status === SOURCE_REGISTRY_STATUS.VERIFIED && summary.total > 0 && summary.verified === summary.total;
}

export default Object.freeze({
  getSourceRegistryHealth,
  getSourceRegistryStatus,
  verifySourceRegistry,
  sealBoardroomProof,
  buildInvestorPack,
  summarizeSourceRegistry,
  statusTone,
  isSourceRegistryReady,
  SOURCE_REGISTRY_STATUS
});
