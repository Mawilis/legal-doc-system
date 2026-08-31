/**
 * TITLE: WILSY OS Python Authentication Projection Client
 * VERSION: v1.0.0-PYTHON-AUTHENTICATION-PROJECTION-CLIENT
 * AUTHORITY: Foreign-runtime authentication transport only; Python EOS owns authenticated identity truth.
 * EPITOME: Forwards one bearer credential to the canonical Python verify-token boundary and accepts only a bounded id/email projection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/pythonAuthenticationProjectionClient.js
 * COLLABORATION / OWNERSHIP: Wilsy Core Engineering; Node transports authenticated state, Python owns authenticated truth.
 * CERTIFICATION/UPDATE DATE: 2026-08-31
 * CHANGELOG:
 *   v1.0.0-PYTHON-AUTHENTICATION-PROJECTION-CLIENT — Establishes a fail-closed Node → Python authentication projection client for /api/auth/verify-token.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Never decodes credentials, never loads users, never accepts role/tenant/permission authority, never returns raw upstream errors.
 * TENANT BOUNDARY: No tenant membership or tenant authority is created, inferred, forwarded, or returned.
 * AUTHORITY BOUNDARY: Transport only. Python get_current_identity remains the sole authenticated identity authority for this projection.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial execution authority.
 */

const DEFAULT_PYTHON_AUTH_BASE_URL = 'http://127.0.0.1:9095';
const VERIFY_TOKEN_PATH = '/api/auth/verify-token';
const DEFAULT_TIMEOUT_MS = 2500;

const ERROR_CODES = Object.freeze({
  CONFIGURATION: 'PYTHON_AUTHENTICATION_CONFIGURATION_INVALID',
  INVALID_CREDENTIAL: 'PYTHON_AUTHENTICATION_CREDENTIAL_INVALID',
  DENIED: 'PYTHON_AUTHENTICATION_DENIED',
  UNAVAILABLE: 'PYTHON_AUTHENTICATION_UNAVAILABLE',
  INVALID_PROJECTION: 'PYTHON_AUTHENTICATION_PROJECTION_INVALID',
});

/**
 * Bounded client failure. Messages and codes never include bearer credentials,
 * upstream response bodies, stack fragments, tenant context, or database detail.
 */
export class PythonAuthenticationProjectionError extends Error {
  constructor(code, { statusCode = 503, cause } = {}) {
    super(code, cause === undefined ? undefined : { cause });
    this.name = 'PythonAuthenticationProjectionError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

/** Resolve the canonical Kennel/Python API origin without inventing authority. */
export function resolvePythonAuthenticationBaseUrl(env = process.env) {
  const raw = env.KENNEL_URL || env.KENNEL_EOS_URL || DEFAULT_PYTHON_AUTH_BASE_URL;
  if (typeof raw !== 'string' || raw.trim().length === 0) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION);
  }

  let url;
  try {
    url = new URL(raw.trim());
  } catch (error) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION, { cause: error });
  }

  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION);
  }
  if (url.username || url.password || url.search || url.hash) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION);
  }
  if (url.pathname !== '/' && url.pathname !== '') {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION);
  }

  return url.origin;
}

/** Validate transport syntax only. The credential is never decoded in Node. */
export function requireBearerAuthorization(authorization) {
  if (typeof authorization !== 'string') {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_CREDENTIAL, {
      statusCode: 401,
    });
  }
  const normalized = authorization.trim();
  if (!/^Bearer\s+\S+$/iu.test(normalized)) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_CREDENTIAL, {
      statusCode: 401,
    });
  }
  return normalized;
}

function requireTimeout(timeoutMs) {
  if (!Number.isInteger(timeoutMs) || timeoutMs < 50 || timeoutMs > 10_000) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION);
  }
  return timeoutMs;
}

function requireObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function hasExactKeys(value, expected) {
  if (!requireObject(value)) return false;
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  return actual.length === wanted.length && actual.every((key, index) => key === wanted[index]);
}

function requireBoundedString(value) {
  return typeof value === 'string' && value.trim().length > 0 && value.length <= 512;
}

/**
 * Validate the exact public projection returned by Python auth_router.
 * Any role, tenant, permission, token, credential, or unknown field is rejected.
 */
export function parsePythonAuthenticationProjection(payload) {
  if (!hasExactKeys(payload, ['success', 'status', 'user'])) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_PROJECTION);
  }
  if (payload.success !== true || payload.status !== 'VERIFIED') {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_PROJECTION);
  }
  if (!hasExactKeys(payload.user, ['id', 'email'])) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_PROJECTION);
  }
  if (!requireBoundedString(payload.user.id) || !requireBoundedString(payload.user.email)) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_PROJECTION);
  }

  return Object.freeze({ id: payload.user.id, email: payload.user.email });
}

/**
 * Verify one bearer credential through Python EOS and return only {id, email}.
 * 401 remains an authentication denial; transport, protocol, malformed projection,
 * timeout, and unexpected upstream status all fail closed as unavailable.
 */
export async function verifyPythonAuthenticationProjection({
  authorization,
  baseUrl = resolvePythonAuthenticationBaseUrl(),
  timeoutMs = DEFAULT_TIMEOUT_MS,
  fetchImpl = globalThis.fetch,
} = {}) {
  const bearer = requireBearerAuthorization(authorization);
  const timeout = requireTimeout(timeoutMs);
  const origin = resolvePythonAuthenticationBaseUrl({ KENNEL_URL: baseUrl });
  if (typeof fetchImpl !== 'function') {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.CONFIGURATION);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  let response;
  try {
    response = await fetchImpl(`${origin}${VERIFY_TOKEN_PATH}`, {
      method: 'GET',
      headers: Object.freeze({
        Accept: 'application/json',
        Authorization: bearer,
      }),
      redirect: 'error',
      cache: 'no-store',
      signal: controller.signal,
    });
  } catch (error) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.UNAVAILABLE, { cause: error });
  } finally {
    clearTimeout(timer);
  }

  if (response.status === 401) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.DENIED, { statusCode: 401 });
  }
  if (!response.ok) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.UNAVAILABLE);
  }

  let payload;
  try {
    payload = await response.json();
  } catch (error) {
    throw new PythonAuthenticationProjectionError(ERROR_CODES.INVALID_PROJECTION, {
      cause: error,
    });
  }
  return parsePythonAuthenticationProjection(payload);
}

export {
  DEFAULT_PYTHON_AUTH_BASE_URL,
  VERIFY_TOKEN_PATH,
  DEFAULT_TIMEOUT_MS,
  ERROR_CODES as PYTHON_AUTHENTICATION_ERROR_CODES,
};

// ARTIFACT: pythonAuthenticationProjectionClient.js
// VERSION: v1.0.0-PYTHON-AUTHENTICATION-PROJECTION-CLIENT
// AUTHORITY BOUNDARY: Node transports one bearer credential; Python EOS alone verifies authenticated identity truth.
// TENANT POSTURE: No tenant claim, header, membership, role, or tenant authority enters or exits this client.
// FAIL-CLOSED POSTURE: Denial, outage, timeout, malformed response, or unexpected status cannot synthesize identity.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
// END OF WILSY OS SOVEREIGN ARTIFACT
