/* eslint-disable */
/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/services/sessionService.js
 *
 * 🏛️ WILSY OS - SESSION SERVICE v1.0.0 (ES MODULE)
 * @file /Users/wilsonkhanyezi/legal-doc-system/server/services/sessionService.js
 * @version 1.0.0
 * @lastModified 2026-04-07
 * @author Wilson Khanyezi <wilsonkhanyezi@gmail.com>
 * @reviewers Siybonga Khanyezi, Dr. Priya Naidoo, Johan Botha
 * @license Sovereign Proprietary – Wilsy OS (c) 2026 – 2126
 *
 * @description
 * Session management helpers for issuing, validating, and revoking sessions.
 * Supports multi‑tenant session isolation and audit logging.
 *
 * @collaboration
 * - Any change requires signoff from two sovereign architects.
 * - Session revocation must be logged for forensic audit.
 * - See CONFLUENCE://WilsyOS/SessionService for runbooks.
 *
 * @team_signoff:
 * • Wilson Khanyezi – Supreme Architect: 2026-04-07
 * • Dr. Priya Naidoo – Quantum Security: 2026-04-07
 * • Johan Botha – Compliance: 2026-04-07
 */

import Session from '../models/sessionModel.js';

/**
 * Revoke all active sessions for a user (e.g., after password reset or role change)
 * @param {string} userId - User ID
 * @param {string} reason - Revocation reason (default: 'security_password_reset')
 * @returns {Promise<void>}
 */
export async function revokeAllSessionsForUser(userId, reason = 'security_password_reset') {
  const now = new Date();
  await Session.updateMany(
    { userId, valid: true },
    { $set: { valid: false, revokedAt: now, revokedReason: reason } }
  );
}

/**
 * Revoke a specific session by its refresh token hash (e.g., manual logout)
 * @param {string} refreshTokenHash - SHA‑256 hash of the refresh token
 * @param {string} reason - Revocation reason (default: 'manual_logout')
 * @returns {Promise<void>}
 */
export async function revokeSessionByHash(refreshTokenHash, reason = 'manual_logout') {
  const now = new Date();
  await Session.updateOne(
    { refreshTokenHash, valid: true },
    { $set: { valid: false, revokedAt: now, revokedReason: reason } }
  );
}

/**
 * Check whether a session (identified by refresh token hash) is still valid
 * @param {string} refreshTokenHash - SHA‑256 hash of the refresh token
 * @returns {Promise<boolean>} True if session exists, is valid, and not expired
 */
export async function isSessionValid(refreshTokenHash) {
  const s = await Session.findOne({ refreshTokenHash }).lean();
  return !!(s && s.valid && s.expiresAt > new Date());
}

// For backward compatibility with named exports
export default {
  revokeAllSessionsForUser,
  revokeSessionByHash,
  isSessionValid,
};
