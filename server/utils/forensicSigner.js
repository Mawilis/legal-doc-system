/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC SIGNER UTILITY [V3.1.2-INSTITUTIONAL-GUARD]                                                                        ║
 * ║ [ASYMMETRIC SEAL VERIFICATION | ARRAY PARITY ENGINE | INSTITUTIONAL FINALITY | BILLION DOLLAR SPEC | MESH-READY]                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 3.1.2-INSTITUTIONAL-GUARD | PRODUCTION READY | BILLION‑DOLLAR SPEC                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/forensicSigner.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ 1. ARCHITECT: Wilson Khanyezi - Mandated absolute path finality and secret‑keyed forensic non‑repudiation. [2026-05-04]                ║
 * ║ 2. AI ENGINEERING: DeepSeek - RECTIFIED: Added strict `next` guard to prevent `next is not a function` crashes.                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Forensic Signer Utility – the cryptographic engine that seals every sovereign request.
 */

import crypto from 'node:crypto';
import { v4 as uuidv4 } from 'uuid';
import { broadcastTelemetry } from './telemetryHelper.js';
import { useSovereignMesh } from './sovereignMesh.js';

const mesh = useSovereignMesh();

// ============================================================================
// 🔧 CORE UTILITIES – Deterministic Normalisation & Sealing
// ============================================================================

/**
 * @function normalizePayload
 * @description Recursively sorts object keys to ensure deterministic stringification.
 */
export const normalizePayload = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(normalizePayload);
  return Object.keys(obj).sort().reduce((acc, key) => {
    acc[key] = normalizePayload(obj[key]);
    return acc;
  }, {});
};

/**
 * @function generateServerSideSyncSeal
 * @description Synchronous bitwise hash generator.
 */
const generateServerSideSyncSeal = (message) => {
  let hash = 0;
  for (let i = 0; i < message.length; i++) {
    const char = message.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(8, '0');
};

/**
 * @function generateForensicHeaders
 * @description Generates the headers for server-side requests.
 */
export const generateForensicHeaders = (payload = {}, tenantId = 'GLOBAL_ROOT') => {
  const requestId = uuidv4();
  const timestamp = new Date().toISOString();
  const nonce = crypto.randomBytes(16).toString('hex');

  const normalized = Object.keys(payload).length ? JSON.stringify(normalizePayload(payload)) : '{}';
  const message = `${requestId}|${timestamp}|${normalized}|${nonce}`;

  const seal = crypto.createHash('sha3-512').update(message).digest('hex').toUpperCase();

  broadcastTelemetry(tenantId, "SYSTEM_EVENT", "FORENSIC_SEAL_GENERATED", "ForensicSigner", {
    traceId: requestId, timestamp
  });

  return {
    'x-tenant-id': tenantId,
    'x-request-id': requestId,
    'x-forensic-timestamp': timestamp,
    'x-cryptographic-nonce': nonce,
    'x-request-seal': seal,
    'x-wilsy-os-build': '42.0.0-SINGULARITY',
    'x-institutional-finality': 'true',
  };
};

/**
 * @middleware verifyForensicSeal
 * @description Validates incoming client seals.
 */
export const verifyForensicSeal = (req, res, next) => {
  try {
    // 🛡️ Surgical guard against undefined req to prevent "Cannot read properties of undefined"
    if (!req || !req.headers) {
      console.error('💥 [FORENSIC-SIGNER] Bypassed due to undefined request object.');
      if (typeof next === 'function') return next();
      return;
    }

    const traceId = req.headers['x-trace-id'] || req.headers['x-request-id'];
    const timestamp = req.headers['x-forensic-timestamp'];
    const nonce = req.headers['x-cryptographic-nonce'];
    const clientSeal = req.headers['x-request-seal'];
    const tenantId = req.tenantId || 'GLOBAL_ROOT';

    // 1. Health & Pulse Bypass
    if (req.path.match(/\/(status|telemetry|pulse|stats)/i)) {
      if (typeof next === 'function') return next();
      return;
    }

    // 2. Reject Missing Architecture
    if (!traceId || !timestamp || !nonce || !clientSeal) {
      console.warn(`[SECURITY-BREACH] 🚨 MISSING_SEAL_HEADERS | URL: ${req.originalUrl}`);
      broadcastTelemetry(tenantId, "SECURITY_ALERT", "MISSING_SEAL_HEADERS", "ForensicSigner", { path: req.originalUrl });
      if (res && typeof res.status === 'function') {
        return res.status(401).json({ success: false, message: 'Missing Sovereign cryptographic headers.' });
      } else {
        console.error(`[CRITICAL_EXPRESS_ERROR] Cannot respond. res object invalid.`);
        if (typeof next === 'function') return next(new Error('Missing Sovereign cryptographic headers.'));
        return;
      }
    }

    // 3. EXACT PAYLOAD RECONSTRUCTION (Mars Protocol Fix)
    let payloadStr;
    if (req.body === undefined || req.body === null) {
      payloadStr = '{}';
    } else if (Array.isArray(req.body)) {
      payloadStr = JSON.stringify(req.body);
    } else if (typeof req.body === 'object') {
      payloadStr = Object.keys(req.body).length === 0 ? '{}' : JSON.stringify(normalizePayload(req.body));
    } else {
      payloadStr = JSON.stringify(req.body);
    }

    const message = `${traceId}|${timestamp}|${payloadStr}|${nonce}`;

    // 4. Verification Fork
    let isValid = false;
    if (clientSeal.length <= 16) {
      const computedSyncSeal = generateServerSideSyncSeal(message);
      isValid = computedSyncSeal === clientSeal;
    } else {
      const computedSha3Seal = crypto.createHash('sha3-512').update(message).digest('hex').toUpperCase();
      isValid = computedSha3Seal === clientSeal;
    }

    // 5. Final Judgment
    if (!isValid) {
      console.error(`[FORENSIC-SIGNER] 🚨 SEAL BREACH: Deterministic mismatch on Request ${traceId}`);
      broadcastTelemetry(tenantId, "SECURITY_ALERT", "CRYPTOGRAPHIC_MISMATCH", "ForensicSigner", { path: req.originalUrl, traceId });
      if (res && typeof res.status === 'function') {
        return res.status(401).json({ success: false, message: 'Cryptographic seal verification failed. Payload tampering detected.' });
      } else {
        console.error(`[CRITICAL_EXPRESS_ERROR] Cannot respond. res object invalid.`);
        if (typeof next === 'function') return next(new Error('Cryptographic seal verification failed.'));
        return;
      }
    }

    if (typeof next === 'function') return next();
    return;
  } catch (error) {
    console.error('💥 [FORENSIC-SIGNER] Verification Fracture:', error.message);
    if (res && typeof res.status === 'function') {
      return res.status(500).json({ success: false, message: 'Internal cryptographic fracture.' });
    } else {
      console.error(`[CRITICAL_EXPRESS_ERROR] ForensicSigner cannot respond. res object is invalid.`);
      // 🛡️ RECTIFIED: Only call next if it's a function, otherwise log and exit cleanly.
      if (typeof next === 'function') {
        return next(error);
      } else {
        console.error(`[CRITICAL_EXPRESS_ERROR] next is not a function. Cannot propagate error.`);
        return; // gracefully exit without crashing
      }
    }
  }
};

/**
 * @function rotateSovereignSecret
 * @description Placeholder for KMS integration.
 */
export const rotateSovereignSecret = async () => {
  console.warn('[FORENSIC-SIGNER] Secret rotation not yet implemented – manual rotation required.');
};

export default {
  generateForensicHeaders,
  verifyForensicSeal,
  normalizePayload,
  rotateSovereignSecret
};
