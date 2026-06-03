/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN FORENSIC SHIELD [V36.9.3-SINGULARITY]                                                                             ║
 * ║ [RECURSIVE CANONICAL PARITY | NATIVE SHA3-512 | UNIVERSAL EXEMPTIONS | HUD STABILITY | PRODUCTION READY]                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 36.9.3-SINGULARITY | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/forensicShield.js                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-fracture hydration for revenue dashboards. [2026-05-06]                         ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Implemented universal Regex exemptions to resolve sub-router path drift. [2026-05-06]           ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Enforced absolute empty-payload parity for GET strikes. [2026-05-06]                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import chalk from 'chalk';
import logger from '../utils/logger.js';

/**
 * 🛡️ RECURSIVE CANONICALIZER
 * Ensures absolute key-order parity with the Singularity Frontend.
 */
const canonicalize = (obj) => {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) return obj;
  return Object.keys(obj).sort().reduce((acc, key) => {
    acc[key] = canonicalize(obj[key]);
    return acc;
  }, {});
};

/**
 * 🏛️ VERIFY FORENSIC SEAL
 * Global entry-point guardian for the Wilsy OS Citadel.
 */
export const verifyForensicSeal = (req, res, next) => {
  const url = req.originalUrl || req.url;

  // 🏛️ RECTIFIED: UNIVERSAL PATTERN EXEMPTIONS
  // This kills the "Shadow 403" by catching metrics/telemetry regardless of path prefixing.
  const EXEMPTION_REGEX = /\/(metrics|telemetry|discover|favicon\.ico|health)/i;

  if (EXEMPTION_REGEX.test(url)) {
    return next();
  }

  const seal = req.headers['x-request-seal'] || req.headers['X-Request-Seal'];
  const traceId = req.headers['x-trace-id'] || req.headers['X-Trace-ID'] || req.headers['x-request-id'] || req.headers['X-Request-ID'];
  const timestamp = req.headers['x-forensic-timestamp'] || req.headers['X-Forensic-Timestamp'];

  // 1. 🚨 IDENTITY CHECK
  if (!seal || !traceId || !timestamp) {
    logger.warn(`[SECURITY-BREACH] 🚨 MISSING_FORENSIC_HEADERS | IP: ${req.ip} | URL: ${url}`);
    return res.status(403).json({ success: false, code: 'ERR_FORENSIC_HEADERS_REQUIRED' });
  }

  // 2. 🧬 REPLAY PROTECTION (5-Minute Window)
  const ts = new Date(timestamp).getTime();
  if (isNaN(ts) || Math.abs(Date.now() - ts) > 5 * 60 * 1000) {
    logger.warn(`[SECURITY-BREACH] 🚨 TIMESTAMP_EXPIRED | Trace: ${traceId}`);
    return res.status(403).json({ success: false, code: 'ERR_REPLAY_ATTACK' });
  }

  // 3. 🏛️ PAYLOAD RECONSTRUCTION (Singularity Parity)
  // Standardizing empty string for GET requests to prevent cryptographic drift.
  const hasBody = req.body && Object.keys(req.body).length > 0;
  const payload = hasBody ? JSON.stringify(canonicalize(req.body)) : '';
  const calculatedSealPayload = `${traceId}|${timestamp}|${payload}|${traceId}`;

  // 4. 🔐 NATIVE SEAL CALCULATION
  const expectedSeal = crypto.createHash('sha3-512').update(calculatedSealPayload).digest('hex');

  // 5. ⚖️ PARITY VERIFICATION
  if (seal !== expectedSeal) {
    logger.error(`[CRYPTOGRAPHIC_MISMATCH] 🚨 URL: ${url} | Trace: ${traceId}`);

    // 🏛️ FORENSIC AUDIT (Internal Terminal logs for billion-dollar debugging)
    console.log(chalk.yellow(` ║ Hashing String: ${calculatedSealPayload}`));
    console.log(chalk.red(` ║ Expected Seal : ${expectedSeal}`));
    console.log(chalk.red(` ║ Received Seal : ${seal}`));

    return res.status(403).json({
      success: false,
      code: 'ERR_CRYPTOGRAPHIC_MISMATCH',
      message: 'Forensic Seal Fractured. Ensure frontend and backend share the same recursive DNA.'
    });
  }

  // 6. ✅ SOVEREIGN CLEARANCE
  console.log(chalk.green(` [FORENSIC-PASS] ✅ Seal verified for Trace: ${traceId} `));
  next();
};

export default verifyForensicSeal;
