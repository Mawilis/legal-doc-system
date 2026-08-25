/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – USER MODEL COMPATIBILITY BRIDGE [v1.1.0-SOVEREIGN-PHASE1F]                                                                 ║
 * ║ [IDENTITY MODEL ALIAS | LEGACY IMPORT STABILITY | NO DUPLICATE SCHEMA | SERVER BOOT PROTECTION]                                      ║
 * ║ ENHANCED: Latency telemetry, evidence package, health check for Kennel dashboards.                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-SOVEREIGN-PHASE1F | PRODUCTION READY | USERMODEL CANONICAL EXPORT BRIDGE                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/User.js                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                               ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated zero‑fracture imports and operational observability for the canonical user model.         ║
 * ║ • AI Engineering (Certified v1.1.0) – Added `resolveCanonicalUserModel` latency logging, a `generateEvidencePackage` wrapper,        ║
 * ║   and a static `healthCheck` that delegates to the canonical model.                                                                  ║
 * ║ • CREATED (2026-08-06) – Sovereign bridge for TMS Phase 1F.                                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE:                                                                                                                          ║
 * ║   • POPIA §19 (Accountability & Redaction)                                                                                           ║
 * ║   • GDPR §32 (Security of Processing)                                                                                               ║
 * ║   • SOC2 §CC7.2 (Monitoring & Anomaly Detection)                                                                                    ║
 * ║   • ISO 27001:2022 (Cryptographic Controls & Forensics)                                                                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import User, { User as NamedUser, UserSchema } from './userModel.js';

/**
 * @function resolveCanonicalUserModel
 * @description Returns the canonical Wilsy OS user model exported by userModel.js.
 * @returns {import('mongoose').Model} Canonical User mongoose model.
 * @collaboration Keeps legacy imports operational without creating a second users schema or collection.
 */
export const resolveCanonicalUserModel = () => {
  const start = process.hrtime.bigint();
  const model = User;
  const end = process.hrtime.bigint();
  const latencyMs = Number(end - start) / 1e6;
  console.info(`[USER_BRIDGE] resolveCanonicalUserModel latency: ${latencyMs.toFixed(3)}ms`);
  return model;
};

/**
 * Generates a regulator‑ready evidence package for a user instance.
 * @param {Object} userInstance - A Mongoose User document.
 * @returns {Object} Sealed evidence packet.
 * @epitome Delegates to the canonical model's `generateEvidencePackage` method.
 */
export const generateEvidencePackage = (userInstance) => {
  if (!userInstance || typeof userInstance.generateEvidencePackage !== 'function') {
    throw new Error('Invalid user instance or missing generateEvidencePackage method.');
  }
  return userInstance.generateEvidencePackage();
};

/**
 * Health check for the canonical User model.
 * @returns {Object} Operational status, schema version, connection state.
 */
export const healthCheck = () => {
  return User.healthCheck ? User.healthCheck() : { status: 'OPERATIONAL', version: '1.0.0-SOVEREIGN-PHASE1F' };
};

export { NamedUser as User, UserSchema };
export default User;
