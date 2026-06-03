/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRYPTOGRAPHIC UNIFIED NAMESPACE [V1.0.0-SINGULARITY]                                                                        ║
 * ║ [CENTRALIZED SECURITY GATEWAY | TITAN-CORE INTEGRATION | BIBLICAL WORTH]                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SINGULARITY | PRODUCTION READY | BILLION DOLLAR SPEC                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL SECURITY NUCLEUS                                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/index.js                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated unified namespace for zero-jitter forensic auditing. [2026-05-15]                     ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Aligned exports to resolve Cipher Mismatch between Titan Bridge and Server Core. [2026-05-15]     ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Implemented explicit alias mapping for 'Institutional' naming conventions. [2026-05-15]         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import cryptoutils from './cryptoutils.js';
import cryptocore from './cryptocore.js';

/**
 * 🛡️ SOVEREIGN UTILITY EXPORTS
 * Aggregated from cryptoutils.js - The engine for hashing, signatures, and Merkle proofs.
 */
export const {
  generateSHA3_512,
  secureCompare,
  signData,
  verifySignature,
  createMerkleRoot
} = cryptoutils;

/**
 * 🔐 QUANTUM CORE EXPORTS
 * Aggregated from cryptocore.js - The engine for AES-256-GCM vaulting and POPIA redaction.
 * Aliased for Institutional Authority mapping.
 */
export const {
  encrypt: encryptForTenant,
  decrypt: decryptForTenant,
  redact: redactSovereignData,
  generateSovereignSeal,
  verifySovereignSeal,
  generateForensicId,
  generateRandomToken,
  generateRandomHash
} = cryptocore;

/**
 * ⚛️ THE NUCLEUS EXPORT
 * Unified default export for high-velocity controller injections.
 */
export default {
  // Utility Logic
  generateSHA3_512,
  secureCompare,
  signData,
  verifySignature,
  createMerkleRoot,

  // Encryption Logic
  encryptForTenant,
  decryptForTenant,
  redactSovereignData,

  // Forensic Logic
  generateSovereignSeal,
  verifySovereignSeal,
  generateForensicId,
  generateRandomToken,
  generateRandomHash,

  // Health & Integrity
  healthCheck: cryptocore.healthCheck
};

console.log(`
╔══════════════════════════════════════════════════════════════════════════╗
║                🏛️  SOVEREIGN CRYPTO SINGULARITY ACTIVE                ║
║   Namespace: UNIFIED | Visibility: GLOBAL | Build: V1.0.0-SINGULARITY    ║
╚══════════════════════════════════════════════════════════════════════════╝
`);
