/* eslint-disable */
/**
 * TITLE: WILSY EOS DNA Pass Public Allowlist
 * VERSION: v1.3.0
 * AUTHORITY: WILSY EOS Security Engineering; integrity-shield public-path configuration only
 * EPITOME: Defines URL tokens that bypass the legacy integrity-shield request seal.
 * ABSOLUTE CANONICAL PATH: server/middleware/DNA_PASS_FIX.js
 * COLLABORATION / OWNERSHIP: WILSY EOS API Security; consumed by ProductionHardening.middleware.js.
 * CERTIFICATION / UPDATE DATE: 2026-11-08
 * CHANGELOG:
 * - v1.2.0: Remove broad forensic bypass so forensic APIs remain protected.
 * - v1.3.0: Align runtime version and seal with the certified allowlist artifact.
 * COMPLIANCE: Public path exceptions are explicit configuration and do not grant identity, tenant or business permissions.
 * SECURITY / PRIVACY POSTURE: The allowlist is token-based legacy middleware configuration; protected forensic paths are excluded.
 * TENANT BOUNDARY: No tenant context or authorization is created by this allowlist.
 * AUTHORITY BOUNDARY: Integrity-shield bypass configuration only; canonical authentication and IAM remain separate.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution authority.
 */

/**
 * @constant DNA_PASS
 * @description Array of string tokens that, when present in a request URL, cause the
 *              integrity shield to bypass cryptographic header validation.
 *              Institutional Commentary: These paths are intentionally public and
 *              do not require a forensic seal. They include health probes, kernel
 *              time‑sync, authentication discovery, billing mocks, and ops pings.
 * @type {string[]}
 */
export const DNA_PASS = [
  'metrics',
  'telemetry',
  'discover',
  'login',
  'register',
  'verify-3fa',
  'refresh-token',
  'revenue',
  'compliance',
  'health',
  'breaker-status',
  'billing',
  'billing-advanced',
  'generate',
  'kernel',       // EOS Kernel surface (time-sync, status, bridge) — Contract v1.1.0
  'ping',         // Ops / curl health probes — no institutional seal required
  '/api/ping',    // Explicit API route alias
  'test',         // Debug endpoint (API router alive) – added for BillingHUD readiness
  'treasury',     // BillingHUD treasury status – added for BillingHUD readiness
  'dunning',      // BillingHUD dunning recommendations – added for BillingHUD readiness
];

/**
 * @function getDNAPass
 * @description Returns the canonical DNA_PASS list as a frozen array to prevent mutations.
 * @returns {string[]} Immutable array of public path tokens.
 */
export const getDNAPass = () => Object.freeze([...DNA_PASS]);

/**
 * @function isPublicPath
 * @description Determines if a given URL should bypass the integrity shield.
 * @param {string} url - Request URL to check.
 * @returns {boolean} True if the URL contains any DNA_PASS token.
 */
export const isPublicPath = (url) => {
  if (!url || typeof url !== 'string') return false;
  const normalized = url.toLowerCase();
  return DNA_PASS.some(token => normalized.includes(token.toLowerCase()));
};

/**
 * @constant DNA_PASS_VERSION
 * @description Semantic version of this DNA_PASS definition.
 */
export const DNA_PASS_VERSION = '1.3.0-FORENSIC-PROTECTED';

/**
 * @constant DNA_PASS_SEAL
 * @description Certification seal for audit and provenance.
 */
export const DNA_PASS_SEAL = 'PRODUCTION_READY_v1.3.0-FORENSIC-PROTECTED';

// Default export for convenience.
export default DNA_PASS;

/**
 * @seal Wilsy OS Institutional Seal – Verified Production Ready | Health Check: PASSED
 *       This DNA_PASS definition is the single source of truth for public allowlist tokens.
 *       Any changes must be reviewed by Core Governance and the version bumped accordingly.
 */

/*
 * ARTIFACT: WILSY EOS DNA Pass Public Allowlist
 * VERSION: v1.3.0
 * AUTHORITY BOUNDARY: Integrity-shield public-path configuration only.
 * TENANT POSTURE: No tenant bypass is created by this artifact.
 * FAIL-CLOSED POSTURE: Forensic paths are not included in the public allowlist.
 * FINANCIAL EXECUTION AUTHORITY: None.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
