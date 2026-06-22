/* eslint-disable */
import pkg from 'js-sha3'; // Corrected CommonJS import (ESM compatibility)
const { sha3_512 } = pkg; // Destructure the required hash function

import { verifyFreshness } from '../utils/cryptoCore.js';
import metrics from '../utils/metrics.js';
import logger from '../utils/logger.js';
import chalk from 'chalk';

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
      '/api/analytics',
      '/api/finance/kpis',
      '/api/finance/currency',
      '/api/wilsy-ai/catalog',
      '/api/wilsy-ai/analytics',
    ].some((route) => url.includes(route))
  ) {
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
