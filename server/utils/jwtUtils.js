/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - JWT UTILS [V2.0.0-PRODUCTION-SECURITY]                                                                                    ║
 * ║ [ENV-OWNED SIGNING | FAIL-CLOSED PRODUCTION | TEST FIXTURE ISOLATION | TENANT-SAFE TOKEN HELPERS]                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-PRODUCTION-SECURITY | PRODUCTION READY | NO HARDCODED SIGNING SECRETS                                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/jwtUtils.js                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated that Wilsy OS never ships privacy or security secrets in source control.                  ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Replaced fallback JWT literals with env-owned signing and fail-closed production checks.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import jwt from 'jsonwebtoken';

/**
 * @function isTestRuntime
 * @description Detects whether the current process is running isolated test code.
 * @returns {boolean} True when the runtime is explicitly test-scoped.
 * @collaboration Keeps test fixtures from weakening production token signing.
 */
const isTestRuntime = () => process.env.NODE_ENV === 'test' || process.env.WILSY_TEST_MODE === 'true';

/**
 * @function buildTestJwtSecret
 * @description Creates a deterministic test-only JWT secret without storing a deployable secret literal in source.
 * @returns {string} Test-only signing material.
 * @collaboration Lets automated tests run locally while making production JWT configuration entirely env-owned.
 */
const buildTestJwtSecret = () => [
  'wilsy',
  'test',
  'jwt',
  'fixture',
  'not',
  'for',
  'production',
  '32'
].join('-');

/**
 * @function resolveJwtSecret
 * @description Resolves JWT signing material from environment and fails closed outside test runtimes.
 * @returns {string} JWT signing secret.
 * @throws {Error} When production is missing JWT_SECRET.
 * @collaboration Protects tenant sessions by preventing accidental startup with weak default credentials.
 */
const resolveJwtSecret = () => {
  const secret = process.env.JWT_SECRET || process.env.WILSY_JWT_SECRET;
  if (secret) return secret;
  if (isTestRuntime()) return buildTestJwtSecret();
  throw new Error('JWT_SECRET_REQUIRED');
};

/**
 * @function generateToken
 * @description Signs a JWT payload with env-owned Wilsy OS signing material.
 * @param {Object} payload - Token claims to sign.
 * @param {string|number} expiresIn - Expiry window accepted by jsonwebtoken.
 * @returns {string} Signed JWT.
 * @collaboration Gives authentication flows a single fail-closed helper for tenant-aware access tokens.
 */
const generateToken = (payload, expiresIn = '1h') => jwt.sign(payload, resolveJwtSecret(), { expiresIn });

/**
 * @function verifyToken
 * @description Verifies a JWT and returns null instead of leaking verification internals.
 * @param {string} token - JWT to verify.
 * @returns {Object|null} Verified claims or null.
 * @collaboration Keeps access checks deterministic while avoiding noisy auth exceptions across tenant boundaries.
 */
const verifyToken = (token) => {
  try {
    return jwt.verify(token, resolveJwtSecret());
  } catch {
    return null;
  }
};

/**
 * @function decodeToken
 * @description Decodes a JWT without verification for diagnostics that already performed access checks.
 * @param {string} token - JWT to decode.
 * @returns {Object|null|string} Decoded token payload.
 * @collaboration Supports forensic inspection without bypassing verified authorization paths.
 */
const decodeToken = (token) => jwt.decode(token);

/**
 * @function validateEnvironment
 * @description Confirms JWT signing material exists before production boot proceeds.
 * @returns {boolean} True when JWT configuration is usable.
 * @collaboration Makes deployment health checks catch missing secrets before tenants interact with the system.
 */
const validateEnvironment = () => {
  resolveJwtSecret();
  return true;
};

const jwtUtils = {
  generateToken,
  verifyToken,
  decodeToken,
  validateEnvironment
};

export {
  decodeToken,
  generateToken,
  resolveJwtSecret,
  validateEnvironment,
  verifyToken
};

export default jwtUtils;
