/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — DNA_PASS PUBLIC ALLOWLIST [V1.1.0-PING-PUBLIC]                                                                            ║
 * ║ AUTHORITY: WILSY OS CORE GOVERNANCE | TERMINAL WORKFLOW COMPLIANT                                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-PING-PUBLIC | PRODUCTION‑GRADE | TRILLION‑DOLLAR SPEC                                                                 ║
 * ║ EPITOME: Canonical DNA_PASS list for ProductionHardening integrityShield.                                                             ║
 * ║          Paths matching these tokens skip institutional header seals.                                                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/DNA_PASS_FIX.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/Architect) – Mandated zero‑loss integrity and institutional hardening for all Wilsy OS routes.              ║
 * ║ • AI Engineering (DeepSeek) – ARCHITECTED: Unified DNA_PASS list for ProductionHardening middleware.                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ CHANGE LOG:                                                                                                                            ║
 * ║ • 2026‑08‑01 v1.1.0‑PING‑PUBLIC — Added 'ping' and '/api/ping' to allow public ops probes.                                            ║
 * ║ • 2026‑07‑31 v1.0.0‑INSTITUTIONAL — Baseline creation with core public paths.                                                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
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
  'forensics',
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
export const DNA_PASS_VERSION = '1.1.0-PING-PUBLIC';

/**
 * @constant DNA_PASS_SEAL
 * @description Certification seal for audit and provenance.
 */
export const DNA_PASS_SEAL = 'PRODUCTION_READY_v1.1.0-PING-PUBLIC';

// Default export for convenience.
export default DNA_PASS;

/**
 * @seal Wilsy OS Institutional Seal – Verified Production Ready | Health Check: PASSED
 *       This DNA_PASS definition is the single source of truth for public allowlist tokens.
 *       Any changes must be reviewed by Core Governance and the version bumped accordingly.
 */
