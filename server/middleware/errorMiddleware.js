/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN ERROR MIDDLEWARE & RESILIENCE SHIELD [V16.1.0-FULL-JSDOC]                                                         ║
 * ║ [POPIA §19 COMPLIANT | FORENSIC TRACING | ZERO‑LEAK STACK TRACES | ASYNC DETACHMENT]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/errorMiddleware.js                                             ║
 * ║ VERSION: 16.1.0-FULL-JSDOC | PRODUCTION READY | TRILLION‑DOLLAR SPEC                                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated Sovereign error handling, POPIA compliance, and zero-latency audit detachment.       ║
 * ║ • Gemini (AI Engineering) – RECTIFIED: Removed blocking awaits on audit logs, added defensive context fallbacks, hashed fingerprints.  ║
 * ║ • AI Engineering (DeepSeek) – EPITOMISED: Added full JSDoc for all functions, cleaned inline comments.                                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import auditLogger from '../utils/auditLogger.js';
import logger from '../utils/logger.js';
import metrics from '../utils/metrics.js';
import cryptoUtils from '../utils/cryptoUtils.js';
import { getCurrentTenant, getCurrentUser, getCurrentRequestId } from './tenantContext.js';

// ============================================================================
// SOVEREIGN LEGAL COMPLIANCE CODES (South African Jurisprudence)
// ============================================================================

/**
 * POPIA compliance error codes (Protection of Personal Information Act 4 of 2013).
 * @constant {Object.<string, {status: number, message: string, code: string}>}
 */
export const POPIA_CODES = Object.freeze({
  SECURITY_BREACH: { status: 500, message: 'POPIA Section 19: Security safeguards violated', code: 'POPIA_SECURITY_BREACH' },
  CONSENT_MISSING: { status: 403, message: 'POPIA Section 11: Consent required', code: 'POPIA_CONSENT_MISSING' },
  RETENTION_EXCEEDED: { status: 403, message: 'POPIA Section 14: Retention period exceeded', code: 'POPIA_RETENTION_EXCEEDED' },
});

/**
 * Legal Practice Council (LPC) compliance error codes.
 * @constant {Object.<string, {status: number, message: string, code: string}>}
 */
export const LPC_CODES = Object.freeze({
  TRUST_ACCOUNT: { status: 403, message: 'LPC Rule 35.2: Trust account integrity violation', code: 'LPC_TRUST_ACCOUNT_ERR' },
  FIDELITY_FUND: { status: 403, message: 'LPC: Fidelity fund certificate missing', code: 'LPC_FIDELITY_MISSING' },
});

// ============================================================================
// ERROR NORMALIZATION & FINGERPRINTING ENGINE
// ============================================================================

/**
 * Normalises an error object to a standardised format with status code, message, code, classification, and details.
 * Handles common error types: ValidationError (Mongoose), Duplicate Key (11000), JWT errors.
 * @param {Error} err - The caught error object.
 * @returns {{statusCode: number, message: string, code: string, classification: string, details: Object}}
 *          Normalised error object suitable for logging and client response.
 * @example
 * const normalized = normalizeError(new Error('Database timeout'));
 * // Returns: { statusCode: 500, message: 'Database timeout', code: 'ERR_SINGULARITY_CORE', classification: 'SYSTEM', details: {} }
 */
const normalizeError = (err) => {
  let normalized = {
    statusCode: err.statusCode || 500,
    message: err.message || 'Sovereign Engine: Internal Anomaly Detected',
    code: err.code || 'ERR_SINGULARITY_CORE',
    classification: err.classification || 'SYSTEM',
    details: err.details || {},
  };

  if (err.name === 'ValidationError') {
    normalized.statusCode = 400;
    normalized.code = 'ERR_VALIDATION_FAILED';
    normalized.classification = 'DATABASE';
  }

  if (err.code === 11000) {
    normalized.statusCode = 409;
    normalized.code = 'ERR_DUPLICATE_ENTRY';
    normalized.message = 'A record with this forensic identifier already exists.';
    normalized.classification = 'DATABASE';
  }

  if (err.name === 'JsonWebTokenError') {
    normalized.statusCode = 401;
    normalized.code = 'ERR_AUTH_INVALID';
    normalized.message = 'Invalid authentication token';
    normalized.classification = 'AUTHENTICATION';
  }

  if (err.name === 'TokenExpiredError') {
    normalized.statusCode = 401;
    normalized.code = 'ERR_AUTH_EXPIRED';
    normalized.message = 'Authentication token expired';
    normalized.classification = 'AUTHENTICATION';
  }

  return normalized;
};

// ============================================================================
// 🛡️ THE GLOBAL SHIELD MIDDLEWARE
// ============================================================================

/**
 * Global error handling middleware for Express. Catches all unhandled errors, normalises them,
 * logs forensically (with POPIA‑compliant IP hashing), records metrics, and sends a safe response.
 * @async
 * @param {Error} err - The error object thrown somewhere in the middleware chain.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next function (unused, but required for signature).
 * @returns {Promise<void>} Sends JSON response and terminates the request.
 *
 * @description
 * - Defensively resolves tenant/user/request ID (falls back to defaults if context unavailable).
 * - Redacts database IDs in the path to avoid leaking internal structure.
 * - Logs errors with appropriate severity (ERROR for 5xx, WARN for 4xx).
 * - Asynchronously logs to the sovereign audit logger (non‑blocking).
 * - Increments Prometheus metrics by error code.
 * - Returns a client‑safe JSON response (no stack traces in production).
 * - Adds legal reference headers for POPIA/LPC errors.
 *
 * @example
 * app.use(errorHandler);
 */
export const errorHandler = async (err, req, res, next) => {
  const startTime = Date.now();

  // Defensive Context Resolution - Prevents cascading failures if context layer is dead
  const tenantId = getCurrentTenant() || 'GLOBAL_ROOT_ANOMALY';
  const userId = getCurrentUser() || 'SYSTEM_ENTITY';
  const requestId = getCurrentRequestId() || crypto.randomUUID();

  const error = normalizeError(err);
  const redactedPath = req.path ? req.path.replace(/\/[a-f0-9]{24}/g, '/:id') : '/unknown_path';

  const forensicLog = {
    requestId,
    tenantId,
    userId: userId !== 'ANON_ENTITY' && userId !== 'SYSTEM_ENTITY'
      ? cryptoUtils.hash(userId).substring(0, 12)
      : userId,
    error: {
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      classification: error.classification,
    },
    request: {
      method: req.method || 'UNKNOWN',
      path: redactedPath,
      ip: req.ip ? cryptoUtils.hash(req.ip).substring(0, 8) : 'NO_IP',
    },
  };

  if (error.statusCode >= 500) {
    logger.error(`💥 SOVEREIGN CRITICAL: ${error.code}`, forensicLog);
    if (process.env.NODE_ENV !== 'production') {
      console.error(err.stack);
    }
  } else {
    logger.warn(`⚠️  SOVEREIGN WARNING: ${error.code}`, forensicLog);
  }

  // Asynchronous Audit Detachment - Removes latency from the response cycle
  if (error.classification === 'LPC' || error.classification === 'POPIA' || error.statusCode >= 500) {
    auditLogger.audit({
      action: 'SYSTEM_ERROR_TRAP',
      tenantId,
      userId,
      requestId,
      details: forensicLog.error,
    }).catch((e) => logger.error('Audit Link Severed during async error handling', { error: e.message }));
  }

  metrics.increment(`error.count.${error.code}`);
  metrics.recordTiming('error.resolution_time', Date.now() - startTime);

  const response = {
    success: false,
    error: process.env.NODE_ENV === 'production' ? error.message : err.message,
    code: error.code,
    traceId: requestId,
    timestamp: new Date().toISOString(),
  };

  if (error.classification === 'POPIA') {
    response.legalReference = 'Protection of Personal Information Act 4 of 2013';
  } else if (error.classification === 'LPC') {
    response.legalReference = 'Legal Practice Act 28 of 2014';
  }

  return res.status(error.statusCode).json(response);
};

// ============================================================================
// GLOBAL UNCAUGHT EXCEPTION & REJECTION HANDLERS
// ============================================================================

/**
 * Handles uncaught exceptions (synchronous errors that bubble up to the event loop).
 * Logs the exception, then waits 1 second and exits the process with code 1.
 * @param {Error} error - The uncaught exception.
 * @returns {void}
 */
process.on('uncaughtException', (error) => {
  logger.error('💥 UNCAUGHT EXCEPTION – Process will exit after forensic capture', {
    error: { name: error.name, message: error.message, stack: error.stack },
    timestamp: new Date().toISOString(),
  });
  setTimeout(() => process.exit(1), 1000);
});

/**
 * Handles unhandled promise rejections (asynchronous errors without `.catch()`).
 * Logs the rejection reason, but does NOT exit the process (allows recovery).
 * @param {*} reason - The rejection reason (usually an Error object).
 * @param {Promise} promise - The promise that was rejected.
 * @returns {void}
 */
process.on('unhandledRejection', (reason, promise) => {
  logger.error('💥 UNHANDLED REJECTION – Process continues, but forensic record created', {
    reason: { message: reason?.message || 'Unknown reason', stack: reason?.stack },
    timestamp: new Date().toISOString(),
  });
});

export default errorHandler;
