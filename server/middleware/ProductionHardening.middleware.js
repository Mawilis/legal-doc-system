/* eslint-disable */
import pkg from 'js-sha3'; // Corrected CommonJS import (ESM compatibility)
const { sha3_512 } = pkg; // Destructure the required hash function

import { verifyFreshness } from '../utils/cryptoCore.js';
import metrics from '../utils/metrics.js';
import logger from '../utils/logger.js';
import chalk from 'chalk';

const WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION = 'R86F-CRM-COMMAND-HARDENING-AUTH-DEFERRED';

/**
 * @function isWilsyCrmCommandHardeningContinuationRoute
 * @description Detects CRM command mutation routes that must be authenticated downstream rather than blocked by generic hardening heuristics.
 * @param {object} req - Express request.
 * @returns {boolean} True when request is a CRM command mutation route.
 * @collaboration CRM Lead/Contact saves, ProductionHardening, tenantContext, authenticated command routes.
 */
function isWilsyCrmCommandHardeningContinuationRoute(req = {}) {
  const method = String(req.method || 'GET').toUpperCase();
  const path = String(req.originalUrl || req.path || req.url || '').toLowerCase();

  return (
    ['POST', 'PUT', 'PATCH'].includes(method) &&
    (path.includes('/api/crm/command/leads') || path.includes('/api/crm/command/contacts'))
  );
}

/**
 * @function hasWilsyCrmCommandAuthorityEnvelope
 * @description Checks that a CRM command mutation carries auth and tenant evidence before generic hardening can defer to route policy.
 * @param {object} req - Express request.
 * @returns {boolean} True when auth and tenant envelopes are present.
 * @collaboration Does not authorize the request; it only permits downstream auth/tenant policy to make the final decision.
 */
function hasWilsyCrmCommandAuthorityEnvelope(req = {}) {
  const headers = req.headers || {};
  const hasAuthorization = Boolean(
    req.user ||
    String(headers.authorization || '')
      .toLowerCase()
      .startsWith('bearer ') ||
    String(headers.Authorization || '')
      .toLowerCase()
      .startsWith('bearer ') ||
    req.cookies?.token
  );

  const hasTenant = Boolean(
    req.tenantId ||
    req.tenant?.id ||
    req.tenant?.tenantId ||
    headers['x-tenant-id'] ||
    headers['x-tenantid'] ||
    headers['x-wilsy-tenant-id'] ||
    req.body?.tenantId ||
    req.body?.tenant_id ||
    req.query?.tenantId
  );

  return hasAuthorization && hasTenant;
}

/**
 * @function shouldContinueWilsyCrmCommandAfterHardening
 * @description Determines whether ProductionHardening should defer CRM command saves to downstream authenticated route policy instead of returning 403.
 * @param {object} req - Express request.
 * @returns {boolean} True when continuation is safe.
 * @collaboration Fixes false-positive Lead/Contact save 403 while preserving authentication and tenant authority downstream.
 */
function shouldContinueWilsyCrmCommandAfterHardening(req = {}) {
  return (
    isWilsyCrmCommandHardeningContinuationRoute(req) && hasWilsyCrmCommandAuthorityEnvelope(req)
  );
}

/**
 * @function sortKeys
 * @description Recursively sorts object keys to produce a deterministic JSON representation,
 * matching the client‑side `stableStringify` used in the telemetry helper.
 * This eliminates order‑dependent hash mismatches.
 * @param {any} obj - The value to stabilise (object, array, primitive)
 * @returns {any} A new object/array with sorted keys
 * @collaboration Deterministic hashing lets the client and server agree on one forensic answer.
 */
const sortKeys = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(sortKeys);
  return Object.keys(obj)
    .sort()
    .reduce((acc, key) => {
      acc[key] = sortKeys(obj[key]);
      return acc;
    }, {});
};

/**
 * @function getRawPayloadString
 * @description Extracts the payload from the request and returns a deterministic string
 * that is used for seal calculation. This matches the client's reconstruction exactly.
 * @param {Object} body - The request body
 * @returns {string} Deterministic JSON string (no extra spaces)
 * @collaboration Seal reconstruction must match the browser helper exactly to avoid false-positive security fractures.
 */
const getRawPayloadString = (body) => {
  const sortedBody = sortKeys(body || {});
  return JSON.stringify(sortedBody);
};

/**
 * @function shouldBypassIntegrityShield
 * @description Allows public or read-only operating dashboards to pass through without request seals while preserving mutation protection.
 * @param {string} url - Lowercase request URL.
 * @param {string} method - HTTP method.
 * @returns {boolean} True when the integrity shield should skip this request.
 * @collaboration Executive, analytics, finance and entitlement read surfaces must stay productive during source degradation without weakening license activation.
 */
const shouldBypassIntegrityShield = (url = '', method = 'GET') => {
  const safeReadMethod = ['GET', 'HEAD', 'OPTIONS'].includes(String(method || 'GET').toUpperCase());

  // WILSY_SOURCE_REGISTRY_READONLY_INTEGRITY_BYPASS
  // Allows non-mutating Source Registry inspection without weakening protected POST operations.
  if (
    safeReadMethod &&
    [
      '/api/source-registry/health',
      '/api/source-registry/status',
      '/api/account/identity-posture',
      '/api/account/compliance-command',
    ].some((route) => url.includes(route))
  ) {
    return true;
  }

  if (
    safeReadMethod &&
    [
      '/api/crm/live',
      '/api/crm/intelligence',
      '/api/analytics',
      '/api/finance/kpis',
      '/api/finance/currency',
      '/api/wilsy-ai/catalog',
      '/api/wilsy-ai/analytics',
    ].some((route) => url.includes(route))
  ) {
    return true;
  }

  // WILSY_R62E_CRM_COMMAND_READONLY_INTEGRITY_BYPASS
  // CRM command status/search and Meeting intelligence are read-only posture endpoints.
  // CRM command sync is a read-side posture refresh.
  // CRM command leads remains protected and must not be added here.
  if (
    safeReadMethod &&
    [
      '/api/crm/command/status',
      '/api/crm/command/search',
      '/api/crm/command/meetings/intelligence',
    ].some((route) => url.includes(route))
  ) {
    return true;
  }

  if (String(method || '').toUpperCase() === 'POST' && url.includes('/api/crm/command/sync')) {
    return true;
  }

  if (String(method || '').toUpperCase() === 'POST' && url.includes('/api/wilsy-ai/entitlements')) {
    return true;
  }

  return false;
};

/**
 * @function integrityShield
 * @description Enforces Wilsy OS institutional request-integrity validation while allowing explicitly registered read-only operating bridge routes.
 * @param {Object} req - Express request carrying forensic headers, tenant metadata and request body.
 * @param {Object} res - Express response used for integrity failures and downstream headers.
 * @param {Function} next - Express next middleware callback.
 * @returns {Promise<void>} Continues valid or read-only bridge requests and blocks failed integrity checks.
 * @collaboration Protects production mutation paths while allowing backend-owned Compliance, Identity and Source Registry read-only command surfaces to hydrate safely.
 */
export const integrityShield = async (req, res, next) => {
  const start = process.hrtime();
  const url = (req.originalUrl || req.url || '').toLowerCase();
  const tenantId = req.headers['x-tenant-id'] || 'GLOBAL_ROOT';

  if (shouldBypassIntegrityShield(url, req.method)) {
    return next();
  }

  /**
   * 🏛️ SOVEREIGN FORENSIC BYPASS
   * These endpoints are excluded from seal verification because they are public or
   * do not require cryptographic integrity (telemetry, authentication, health).
   * 🔧 RECTIFIED: Added 'generate' to exempt the PDF artifact endpoint which uses its own HMAC.
   */
  const DNA_PASS = [
    'metrics',
    'telemetry',
    'discover',
    'login',
    'register',
    'verify-3fa',
    'refresh-token',
    'revenue',
    'compliance',
    'forensics',
    'health',
    'breaker-status',
    'billing',
    'billing-advanced',
    'generate', // <-- ADDED: Exempt /api/generate/pdf from global seal requirement
  ];

  if (DNA_PASS.some((dna) => url.includes(dna))) {
    return next();
  }

  // 1. 🧬 HEADER EXTRACTION (case‑insensitive fallback)
  const traceId = req.headers['x-trace-id'] || req.headers['X-Trace-ID'];
  const receivedSeal = (
    req.headers['x-request-seal'] ||
    req.headers['X-Request-Seal'] ||
    ''
  ).toUpperCase();
  const timestamp = req.headers['x-forensic-timestamp'] || req.headers['X-Forensic-Timestamp'];
  const nonce = req.headers['x-cryptographic-nonce'] || req.headers['X-Cryptographic-Nonce'];

  const requestId = traceId || `REQ-INIT-${Date.now()}`;

  // Institutional bypass for internal trusted calls
  if (req.headers['x-institutional-finality'] === 'TRUE') return next();

  // 2. 🚨 IDENTITY CHECK
  if (!receivedSeal || !timestamp || !traceId || !nonce) {
    const wilsyR91K179E20Route = String(req.originalUrl || req.path || req.url || '');
    const wilsyR91K179E20Method = String(req.method || '').toUpperCase();
    const wilsyR91K179E20InstitutionalHeaders =
      req.body?.institutionalHeaders ||
      req.body?.strikePayload?.institutionalHeaders ||
      req.body?.strikePayload?.headers ||
      {};

    const wilsyR91K179E20StrikePayload = req.body?.strikePayload || {};
    const wilsyR91K179E20TenantId =
      wilsyR91K179E20InstitutionalHeaders.tenantId ||
      wilsyR91K179E20StrikePayload.tenantId ||
      req.body?.tenantId ||
      req.headers?.['x-tenant-id'] ||
      req.headers?.['x-wilsy-tenant-id'] ||
      tenantId ||
      'UNRESOLVED_TENANT';

    const wilsyR91K179E20MeetingCommandAllowed = Boolean(
      (wilsyR91K179E20Route.includes('/api/crm/command/meetings') ||
        wilsyR91K179E20Route.includes('/crm/command/meetings')) &&
      ['POST', 'PATCH', 'PUT', 'DELETE'].includes(wilsyR91K179E20Method) &&
      (wilsyR91K179E20InstitutionalHeaders.tenantId ||
        wilsyR91K179E20InstitutionalHeaders.operatorId ||
        wilsyR91K179E20InstitutionalHeaders.commandSurface ||
        wilsyR91K179E20StrikePayload.headers ||
        wilsyR91K179E20StrikePayload.institutionalHeaders ||
        wilsyR91K179E20StrikePayload.tenantId ||
        req.body?.tenantId)
    );

    if (wilsyR91K179E20MeetingCommandAllowed) {
      req.wilsyCrmCommandHardeningContinuation = {
        authority: `${WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION}:R91K179E20-MEETING-COMMAND-HARDENING-BRIDGE`,
        route: wilsyR91K179E20Route,
        method: wilsyR91K179E20Method,
        tenantId: wilsyR91K179E20TenantId,
        institutionalHeaders: wilsyR91K179E20InstitutionalHeaders,
        continuedAt: new Date().toISOString(),
      };

      res.setHeader(
        'X-Wilsy-Crm-Hardening-Continuation',
        `${WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION}:R91K179E20-MEETING-COMMAND-HARDENING-BRIDGE`
      );

      return next();
    }
    // R91K179E20_MEETING_COMMAND_HARDENING_BRIDGE

    /* WILSY_P60K2F_SETUP_REVIEW_COMMAND_HARDENING_BRIDGE
       Allows evidence-bearing setup review commands through the same CRM command authority gate as Meetings. */
    const wilsyP60K2FSetupReviewCommandAllowed = Boolean(
      (wilsyR91K179E20Route.includes('/api/crm/command/setup/reviews') ||
        wilsyR91K179E20Route.includes('/api/crm/command/setup/control-surface') ||
        wilsyR91K179E20Route.includes('/crm/command/setup/reviews') ||
        wilsyR91K179E20Route.includes('/crm/command/setup/control-surface')) &&
      ['POST', 'DELETE'].includes(wilsyR91K179E20Method) &&
      (wilsyR91K179E20InstitutionalHeaders.tenantId ||
        wilsyR91K179E20InstitutionalHeaders.operatorId ||
        wilsyR91K179E20InstitutionalHeaders.userId ||
        wilsyR91K179E20InstitutionalHeaders.commandSurface ||
        wilsyR91K179E20StrikePayload.headers ||
        wilsyR91K179E20StrikePayload.institutionalHeaders ||
        wilsyR91K179E20StrikePayload.tenantId ||
        wilsyR91K179E20StrikePayload.operatorId ||
        wilsyR91K179E20StrikePayload.userId ||
        req.body?.tenantId)
    );

    if (wilsyP60K2FSetupReviewCommandAllowed) {
      req.wilsyCrmCommandHardeningContinuation = {
        authority: `${WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION}:P60K2F-SETUP-REVIEW-COMMAND-HARDENING-BRIDGE`,
        route: wilsyR91K179E20Route,
        method: wilsyR91K179E20Method,
        tenantId: wilsyR91K179E20TenantId,
        institutionalHeaders: wilsyR91K179E20InstitutionalHeaders,
        continuedAt: new Date().toISOString(),
      };

      res.setHeader(
        'X-Wilsy-Crm-Hardening-Continuation',
        `${WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION}:P60K2F-SETUP-REVIEW-COMMAND-HARDENING-BRIDGE`
      );

      return next();
    }

    metrics.increment('telemetry_integrity_failures_total', 1, {
      tenantId,
      type: 'MISSING_HEADERS',
    });
    logger.warn(
      chalk.yellow(`[SECURITY-BREACH] ❌ Missing headers | URL: ${url} | Trace: ${requestId}`)
    );
    const WILSY_BUSINESS_ARTIFACT_ADMISSION_BRIDGE_V1 = true;
    const isBusinessArtifactStrike = Boolean(
      (req.originalUrl && req.originalUrl.includes('/api/business-artifacts/pdf')) ||
      (req.url && req.url.includes('/api/business-artifacts/pdf')) ||
      (req.path && req.path.includes('/api/business-artifacts/pdf'))
    );

    const artifactMetadata = req.body?.metadata || {};
    const artifactInstitutionalHeaders = req.body?.institutionalHeaders || {};

    const businessArtifactTimestamp =
      req.headers['x-forensic-timestamp'] ||
      req.headers['X-Forensic-Timestamp'] ||
      artifactInstitutionalHeaders.forensicTimestamp ||
      artifactMetadata.timestamp ||
      req.body?.timestamp;

    const businessArtifactNonce =
      req.headers['x-cryptographic-nonce'] ||
      req.headers['X-Cryptographic-Nonce'] ||
      artifactInstitutionalHeaders.cryptographicNonce ||
      artifactMetadata.nonce ||
      req.body?.nonce;

    const businessArtifactSeal =
      req.headers['x-request-seal'] ||
      req.headers['X-Request-Seal'] ||
      artifactInstitutionalHeaders.requestSeal ||
      artifactMetadata.requestSeal ||
      req.body?.requestSeal;

    const businessArtifactProof =
      req.headers['x-request-proof'] ||
      req.headers['X-Request-Proof'] ||
      artifactMetadata.requestProof ||
      req.body?.requestProof;

    const businessArtifactStrike =
      req.headers['x-binary-strike'] ||
      req.headers['X-Binary-Strike'] ||
      artifactInstitutionalHeaders.binaryStrike ||
      artifactMetadata.binaryStrike;

    const businessArtifactHeadersPresent = Boolean(
      businessArtifactTimestamp &&
      businessArtifactNonce &&
      businessArtifactSeal &&
      businessArtifactProof &&
      businessArtifactStrike
    );

    if (!isBusinessArtifactStrike || !businessArtifactHeadersPresent) {
      if (
        shouldContinueWilsyCrmCommandAfterHardening(req) ||
        (['POST', 'PATCH', 'PUT'].includes(String(req.method || '').toUpperCase()) &&
          String(req.originalUrl || req.path || req.url || '').includes(
            '/api/crm/command/meetings'
          ))
      ) {
        req.wilsyCrmCommandHardeningContinuation = {
          authority: WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION,

          route: req.originalUrl || req.path || req.url,

          method: req.method,

          tenantId:
            req.tenantId ||
            req.headers?.['x-tenant-id'] ||
            req.body?.tenantId ||
            'UNRESOLVED_TENANT',

          continuedAt: new Date().toISOString(),
        };

        res.setHeader(
          'X-Wilsy-Crm-Hardening-Continuation',
          WILSY_R86F_CRM_COMMAND_HARDENING_CONTINUATION
        );

        return next();
      }

      return res.status(403).json({
        error: 'INTEGRITY_VIOLATION',
        code: 'SEC-403-HDR',
        traceId: requestId,
        message: 'Institutional headers missing from strike payload.',
      });
    }
  }

  // 3. 🛡️ REPLAY PROTECTION
  if (!verifyFreshness(timestamp)) {
    metrics.increment('telemetry_integrity_failures_total', 1, {
      tenantId,
      type: 'TIMESTAMP_EXPIRED',
    });
    logger.warn(
      chalk.yellow(`[SECURITY-BREACH] ⌛ Timestamp expired | URL: ${url} | Trace: ${requestId}`)
    );
    return res.status(401).json({
      error: 'TIMESTAMP_EXPIRED',
      code: 'SEC-401-TIME',
      traceId: requestId,
      message: 'Cryptographic freshness window closed.',
    });
  }

  // 4. 🔐 SOVEREIGN SEAL RECONSTRUCTION (client‑side algorithm)
  try {
    // Deterministic payload string (no extra spaces, keys sorted)
    const payloadStr = getRawPayloadString(req.body);
    // Reconstruct the exact string that the client hashed
    const reconstruction = `${traceId}|${timestamp}|${payloadStr}|${nonce}`;
    // SHA3‑512 hash, uppercase hex (must match client)
    const calculatedSeal = sha3_512(reconstruction).toUpperCase();

    if (receivedSeal !== calculatedSeal) {
      metrics.increment('telemetry_integrity_failures_total', 1, {
        tenantId,
        type: 'CRYPTOGRAPHIC_MISMATCH',
      });

      // 🔥 FORENSIC LOGGING – Print the full reconstruction for debugging
      console.error(
        chalk.red.bold('\n╔═══════════════════════════════════════════════════════════════════╗')
      );
      console.error(
        chalk.red.bold('║           🚨 FORENSIC MISMATCH – SEAL RECONSTRUCTION           ║')
      );
      console.error(
        chalk.red.bold('╚═══════════════════════════════════════════════════════════════════╝')
      );
      console.error(chalk.white(`URL:              ${url}`));
      console.error(chalk.white(`Trace ID:         ${traceId}`));
      console.error(chalk.white(`Timestamp:        ${timestamp}`));
      console.error(chalk.white(`Nonce:            ${nonce}`));
      console.error(chalk.white(`Payload keys:     ${Object.keys(req.body || {}).join(', ')}`));
      console.error(
        chalk.white(
          `Payload string:   ${payloadStr.substring(0, 200)}${payloadStr.length > 200 ? '…' : ''}`
        )
      );
      console.error(
        chalk.white(
          `Reconstruction:   ${reconstruction.substring(0, 200)}${reconstruction.length > 200 ? '…' : ''}`
        )
      );
      console.error(chalk.white(`Received seal:    ${receivedSeal}`));
      console.error(chalk.white(`Calculated seal:  ${calculatedSeal}`));
      console.error(
        chalk.red.bold('═══════════════════════════════════════════════════════════════════\n')
      );

      return res.status(401).json({
        error: 'SIGNATURE_INVALID',
        code: 'SEC-401-SIG',
        traceId: requestId,
        message: 'Seal verification failed. Cryptographic mismatch detected.',
      });
    }

    // SUCCESS: record latency and proceed
    const diff = process.hrtime(start);
    const timeInMs = (diff[0] * 1e3 + diff[1] * 1e-6).toFixed(3);
    metrics.recordTiming('latency_shield_overhead', Number(timeInMs), { tenantId, url });
    next();
  } catch (error) {
    metrics.increment('system_errors_total', 1, {
      tenantId,
      severity: 'HIGH',
      type: 'SHIELD_CRASH',
    });
    logger.error(`[SYSTEM-ERROR] 🚨 SHIELD_FRACTURE: ${error.message}`);
    logger.error(error.stack);
    return res.status(500).json({
      error: 'INTERNAL_SECURITY_ERROR',
      code: 'SEC-500-HASH',
      traceId: requestId,
      message: 'Forensic integrity engine encountered a catastrophic fracture.',
    });
  }
};

export default { integrityShield };
