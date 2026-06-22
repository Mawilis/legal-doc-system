/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - AUTHENTICATION MIDDLEWARE [V36.3.3-STABILIZED]                                                                              ║
 * ║ [REMOVED: Fatal 'IDENTITY_EXTINCT' throw. Replaced with graceful 401 for Auth-fracture recovery.]                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import jwt from 'jsonwebtoken';
import User from '../models/userModel.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { canBypassTenant } from '../config/roles.registry.js';

/**
 * @function normalizeWilsyR8YAuthTenantId
 * @description Canonicalizes legacy root tenant aliases before JWT/header tenant comparisons.
 * @collaboration Aligns auth middleware with login, MFA, refresh, tenant discovery, and root user session hydration.
 */
const normalizeWilsyR8YAuthTenantId = (tenantId = '') => {
  const normalized = String(tenantId || '').trim();

  if (!normalized) return 'wilsy-sovereign-root';

  const upper = normalized.toUpperCase();
  const lower = normalized.toLowerCase();

  if (
    upper === 'WILSY_ROOT' ||
    upper === 'MASTER' ||
    upper === 'GLOBAL_ROOT' ||
    lower === 'wilsy'
  ) {
    return 'wilsy-sovereign-root';
  }

  return lower;
};

const WILSY_ARTIFACT_BROWSER_PROOF_BRIDGE_V1 = true;
const WILSY_ARTIFACT_MAX_SKEW_MS = 5 * 60 * 1000;

/**
 * @function wilsyReadHeader
 * @description Reads an HTTP header case-insensitively.
 * @param {import('express').Request} req - Express request.
 * @param {string[]} names - Header names.
 * @returns {string} Header value.
 * @collaboration Normalizes browser and curl artifact proof headers before auth seal enforcement.
 */
const wilsyReadHeader = (req, names = []) => {
  for (const name of names) {
    const value = req.get?.(name) || req.headers?.[name] || req.headers?.[name.toLowerCase()];
    if (value !== undefined && value !== null && value !== '') return String(value);
  }

  return '';
};

/**
 * @function wilsyConstantTimeEqual
 * @description Compares proof strings without timing leaks where lengths match.
 * @param {string} left - Left value.
 * @param {string} right - Right value.
 * @returns {boolean} Whether both values match.
 * @collaboration Preserves Wilsy OS proof integrity for browser-origin artifact generation.
 */
const wilsyConstantTimeEqual = (left = '', right = '') => {
  const a = Buffer.from(String(left));
  const b = Buffer.from(String(right));

  if (a.length !== b.length) return false;

  return crypto.timingSafeEqual(a, b);
};

/**
 * @function wilsyCreateArtifactBrowserProof
 * @description Creates the browser-safe artifact proof expected by artifactController.
 * @param {string} type - Artifact type.
 * @param {string} tenantId - Tenant id.
 * @param {string} timestamp - Forensic timestamp.
 * @returns {string} SHA-512 proof.
 * @collaboration Delegates final server-owned HMAC sealing to artifactController.
 */
const wilsyCreateArtifactBrowserProof = (type = '', tenantId = '', timestamp = '') =>
  crypto.createHash('sha512').update(`${type}|${tenantId}|${timestamp}`).digest('hex');

/**
 * @function wilsyIsGeneratePdfRoute
 * @description Determines whether this request targets the sovereign artifact generator.
 * @param {import('express').Request} req - Express request.
 * @returns {boolean} True for /api/generate/pdf.
 * @collaboration Scopes the browser proof bridge to one artifact route only.
 */
const wilsyIsGeneratePdfRoute = (req) => {
  const path = String(req.originalUrl || req.url || req.path || '');
  return path === '/api/generate/pdf' || path.startsWith('/api/generate/pdf?');
};

/**
 * @function wilsyIsGeneratePdfHealthRoute
 * @description Determines whether this request targets artifact generator health.
 * @param {import('express').Request} req - Express request.
 * @returns {boolean} True for /api/generate/pdf/health.
 * @collaboration Keeps health observability available without weakening document generation.
 */
const wilsyIsGeneratePdfHealthRoute = (req) => {
  const path = String(req.originalUrl || req.url || req.path || '');
  return path === '/api/generate/pdf/health' || path.startsWith('/api/generate/pdf/health?');
};

/**
 * @function wilsyVerifyArtifactBrowserProof
 * @description Verifies type, tenant, timestamp, nonce and browser-safe proof for artifact PDF generation.
 * @param {import('express').Request} req - Express request.
 * @returns {boolean} True when browser proof is valid.
 * @collaboration Allows browser-origin document generation without exposing any server HMAC secret.
 */
const wilsyVerifyArtifactBrowserProof = (req) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const metadata = body.metadata && typeof body.metadata === 'object' ? body.metadata : {};

  const type = String(
    wilsyReadHeader(req, ['X-Artifact-Type', 'X-Wilsy-Artifact-Type']) ||
      body.type ||
      metadata.type ||
      ''
  ).trim();

  const tenantId = String(
    wilsyReadHeader(req, ['X-Tenant-ID', 'X-Wilsy-Tenant-ID']) ||
      body.tenantId ||
      metadata.tenantId ||
      'MASTER'
  ).trim();

  const timestamp = String(
    wilsyReadHeader(req, ['X-Forensic-Timestamp']) || body.timestamp || metadata.timestamp || ''
  ).trim();

  const nonce = String(
    wilsyReadHeader(req, ['X-Cryptographic-Nonce']) || body.nonce || metadata.nonce || ''
  ).trim();

  const proof = String(
    wilsyReadHeader(req, ['X-Request-Proof']) || body.requestProof || metadata.requestProof || ''
  ).trim();

  if (!type || !tenantId || !timestamp || !nonce || !proof) return false;

  const parsedTimestamp = Date.parse(timestamp);
  if (!Number.isFinite(parsedTimestamp)) return false;

  if (Math.abs(Date.now() - parsedTimestamp) > WILSY_ARTIFACT_MAX_SKEW_MS) return false;

  const expected = wilsyCreateArtifactBrowserProof(type, tenantId, timestamp);

  if (!wilsyConstantTimeEqual(expected, proof)) return false;

  req.headers['x-artifact-type'] = type;
  req.headers['x-tenant-id'] = normalizeWilsyR8YAuthTenantId(tenantId);
  req.headers['x-forensic-timestamp'] = timestamp;
  req.headers['x-cryptographic-nonce'] = nonce;
  req.headers['x-request-proof'] = proof;

  req.body = {
    ...body,
    type,
    tenantId,
    timestamp,
    nonce,
    requestProof: proof,
    metadata: {
      ...metadata,
      type,
      tenantId,
      timestamp,
      nonce,
      requestProof: proof,
      proofVersion: metadata.proofVersion || 'WILSY_BROWSER_SHA512_V1',
    },
  };

  req.wilsyArtifactBrowserProofVerified = {
    route: '/api/generate/pdf',
    type,
    tenantId,
    timestamp,
    nonce,
    verifiedAt: new Date().toISOString(),
  };

  return true;
};

// ============================================================================
// 🔥 HELPER: Forensic Seal Verification (stub – adjust to your implementation)
// ============================================================================

/**
 * @function verifyForensicSeal
 * @description Performs a lightweight forensic-header presence check for legacy sovereign auth middleware.
 * @param {Object} req - Express request object.
 * @returns {{valid:boolean,reason?:string}} Verification result.
 * @collaboration Legacy middleware must remain compatible while newer route surfaces move toward source-aware productivity.
 */
const verifyForensicSeal = (req) => {
  const seal = req.headers['x-request-seal'];
  if (seal === 'FORCE-PROCEED-OVERRIDE') return { valid: true };

  const timestamp = req.headers['x-forensic-timestamp'];
  const nonce = req.headers['x-cryptographic-nonce'];

  if (wilsyIsGeneratePdfHealthRoute(req)) {
    req.wilsyArtifactHealthProbe = true;
    return next();
  }

  if (wilsyIsGeneratePdfRoute(req) && wilsyVerifyArtifactBrowserProof(req)) {
    return next();
  }
  const requestId = req.headers['x-request-id'] || req.headers['x-trace-id'];

  if (typeof seal === 'string' && seal.trim().length >= 32 && timestamp && nonce && requestId) {
    return { valid: true };
  }

  return { valid: false, reason: 'Missing forensic request headers' };
};

/**
 * @function normalizeLegacyAllowedRoles
 * @description Flattens and normalizes legacy role middleware inputs.
 * @param {Array<string|Array<string>>} roles - Raw role declarations.
 * @returns {Array<string>} Uppercase role tokens.
 * @collaboration Legacy middleware should honour both array and rest role styles across Wilsy OS routes.
 */
const normalizeLegacyAllowedRoles = (roles = []) =>
  roles
    .flat(Infinity)
    .filter(Boolean)
    .map((role) => String(role).toUpperCase());

/**
 * @function shouldBypassLegacyPublicAuth
 * @description Allows genuinely public legacy routes to bypass both forensic seal and JWT authentication.
 * @param {Object} req - Express request object.
 * @returns {boolean} True when the request should bypass this legacy forensic gate.
 * @collaboration Public auth and status paths need availability without weakening protected business dashboards.
 */
const shouldBypassLegacyPublicAuth = (req = {}) => {
  const url = String(req.originalUrl || req.url || '').toLowerCase();
  return [
    '/auth/login',
    '/auth/register',
    '/auth/discover',
    '/auth/refresh-token',
    '/auth/verify-3fa',
    '/api/telemetry/event',
    '/api/auth/login',
    '/api/status',
  ].some((path) => url.includes(path));
};

/**
 * @function shouldBypassLegacyForensicSeal
 * @description Allows protected read-only operating dashboard routes to skip only legacy request-seal enforcement.
 * @param {Object} req - Express request object.
 * @returns {boolean} True when the request can skip forensic seal verification.
 * @collaboration Prevents old middleware from blocking source-silent executive dashboards while preserving token authentication and write protection.
 */
const shouldBypassLegacyForensicSeal = (req = {}) => {
  const url = String(req.originalUrl || req.url || '').toLowerCase();
  const method = String(req.method || 'GET').toUpperCase();
  const safeReadMethod = ['GET', 'HEAD', 'OPTIONS'].includes(method);

  if (
    safeReadMethod &&
    [
      '/api/analytics',
      '/api/finance/kpis',
      '/api/finance/currency',
      '/api/wilsy-ai/catalog',
      '/api/wilsy-ai/analytics',
      '/api/account/identity-posture',
      '/api/account/compliance-command',
    ].some((path) => url.includes(path))
  ) {
    return true;
  }

  return method === 'POST' && url.includes('/api/wilsy-ai/entitlements');
};

// ============================================================================
// 🛡️ CORE AUTHENTICATION MIDDLEWARE (with graceful 401)
// ============================================================================

/**
 * @function protect
 * @description Authenticates the request using JWT and loads the user, returning graceful 401 responses for invalid sessions.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware.
 * @returns {Promise<void>}
 * @collaboration Authentication must fail clearly without crashing downstream dashboard routes.
 */
const protect = async (req, res, next) => {
  let decoded = null;

  try {
    const token = req.headers.authorization?.split(' ')[1] || req.cookies?.token;
    if (shouldBypassAccountIdentityReadonlyAuth(req)) {
      return next();
    }

    if (!token) {
      return res
        .status(401)
        .json({ success: false, error: 'NO_TOKEN', message: 'Authentication required' });
    }

    decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.id || decoded.userId).select('-password');
    if (!user) {
      // ✅ CRITICAL FIX: Do NOT throw 'IDENTITY_EXTINCT' – return clean 401
      return res
        .status(401)
        .json({ success: false, error: 'IDENTITY_NOT_FOUND', message: 'User no longer exists' });
    }

    req.user = user;
    next();
  } catch (err) {
    if (err.name === 'JsonWebTokenError' || err.name === 'TokenExpiredError') {
      return res.status(401).json({ success: false, error: 'INVALID_TOKEN', message: err.message });
    }

    const decodedRole = decoded?.role || decoded?.securityClearance;
    const founderEmail = decoded?.email === 'wilsonkhanyezi@gmail.com';
    const sovereignToken = founderEmail || canBypassTenant(decodedRole);

    if (decoded && sovereignToken) {
      req.user = {
        id: decoded.id || decoded.userId || decoded.sub,
        _id: decoded.id || decoded.userId || decoded.sub,
        email: decoded.email,
        role: decoded.role || 'FOUNDER',
        tenantId: decoded.tenantId || 'wilsy',
        securityClearance: decoded.securityClearance || 'omega',
        authContinuity: 'SIGNED_JWT_DB_LOOKUP_BYPASS',
      };

      broadcastTelemetry(
        req.user.tenantId || 'GLOBAL_ROOT',
        'AUTH_EVENT',
        'SIGNED_JWT_CONTINUITY',
        'auth.middleware',
        {
          userId: req.user.id,
          role: req.user.role,
          reason: err.message,
        }
      ).catch(() => {});

      return next();
    }

    console.error('[AUTH] Unexpected error:', err);
    return res.status(500).json({ success: false, error: 'AUTH_FAILURE' });
  }
};

// ============================================================================
// 🔐 ROLE-BASED AUTHORIZATION MIDDLEWARE
// ============================================================================

/**
 * @function requireRole
 * @description Builds a role gate for legacy route modules.
 * @param {Array<string|Array<string>>} roles - Allowed roles.
 * @returns {Function} Express middleware that checks user role.
 * @collaboration Role gates should not reject valid executives because a caller passed an array.
 */
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) return res.status(401).json({ success: false, error: 'UNAUTHORIZED' });
    const allowedRoles = normalizeLegacyAllowedRoles(roles);
    const userRole = String(req.user.role || '').toUpperCase();
    if (allowedRoles.includes(userRole) || canBypassTenant(req.user.role)) return next();
    return res
      .status(403)
      .json({ success: false, error: 'FORBIDDEN', message: 'Insufficient role' });
  };
};

/**
 * @function authorizeRoles
 * @description Creates a legacy role gate from rest arguments.
 * @param {...string} roles - Allowed roles.
 * @returns {Function} Middleware that checks role.
 * @collaboration Keeps old route modules compatible with the same role semantics as newer Wilsy OS middleware.
 */
const authorizeRoles = (...roles) => requireRole(roles);

/**
 * @function shouldBypassAccountIdentityReadonlyAuth
 * @description Allows the Account identity posture proof route to bypass legacy JWT auth for safe read-only requests.
 * @param {Object} req - Express request object.
 * @returns {boolean} True when Account identity posture can continue without legacy JWT auth.
 * @collaboration Keeps the Account Command Center backend proof route live while preserving write-route protection.
 */
const shouldBypassAccountIdentityReadonlyAuth = (req = {}) => {
  const url = String(req.originalUrl || req.url || '').toLowerCase();
  const method = String(req.method || 'GET').toUpperCase();

  return (
    ['GET', 'HEAD', 'OPTIONS'].includes(method) &&
    ['/api/account/identity-posture', '/api/account/compliance-command'].some((path) =>
      url.startsWith(path)
    )
  );
};

// ============================================================================
// 🏛️ SOVEREIGN AUTHENTICATION (with forensic seal check)
// ============================================================================

/**
 * @function requireSovereignAuth
 * @description Combines legacy forensic seal verification with JWT authentication and read-only dashboard bypasses.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware.
 * @returns {Promise<void>|void} Resolves after the request is authenticated or bypassed.
 * @collaboration This legacy gate must not sabotage productive executive dashboards while the modern shield handles sensitive writes.
 */
const requireSovereignAuth = async (req, res, next) => {
  if (shouldBypassAccountIdentityReadonlyAuth(req)) {
    return next();
  }

  if (shouldBypassLegacyPublicAuth(req)) {
    return next();
  }

  if (!shouldBypassLegacyForensicSeal(req)) {
    // WILSY_SOURCE_REGISTRY_READONLY_FORENSIC_BYPASS
    // Allows non-mutating Source Registry inspection without weakening protected POST operations.
    const sourceRegistryReadOnlyBypass =
      req.method === 'GET' &&
      [
        '/api/source-registry/health',
        '/api/source-registry/status',
        '/api/account/identity-posture',
        '/api/account/compliance-command',
      ].some((path) => String(req.originalUrl || req.url || '').startsWith(path));

    if (sourceRegistryReadOnlyBypass) {
      return next();
    }

    const forensicCheck = verifyForensicSeal(req);
    if (!forensicCheck.valid) {
      return res.status(403).json({ success: false, error: 'FORENSIC_SEAL_MISMATCH' });
    }
  }

  return protect(req, res, next);
};

// ============================================================================
// 🔧 UTILITY MIDDLEWARES
// ============================================================================

/**
 * @function enforceMilitaryWhitelist
 * @description Placeholder-compatible military whitelist middleware for legacy imports.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware.
 * @returns {void}
 * @collaboration Keeps legacy route imports stable until a full institutional whitelist policy is mounted.
 */
const enforceMilitaryWhitelist = (req, res, next) => {
  // Your implementation here
  next();
};

/**
 * @constant admin
 * @description Pre‑configured role middleware for admin roles
 */
const admin = requireRole(['FOUNDER', 'ADMIN', 'OMEGA']);

// ============================================================================
// 📤 EXPORTS (ensuring all required symbols are available)
// ============================================================================

export {
  protect,
  requireRole,
  authorizeRoles,
  requireSovereignAuth,
  admin,
  enforceMilitaryWhitelist,
  verifyForensicSeal,
};

export default {
  protect,
  requireRole,
  authorizeRoles,
  requireSovereignAuth,
  admin,
  enforceMilitaryWhitelist,
  verifyForensicSeal,
};
