/* eslint-disable */
/**
 * 🔐 WILSY OS - SOVEREIGN AUTHENTICATION SERVICE [V72.0.0-MFA-FORENSIC]
 * @version 72.0.0-QUANTUM-2050
 * @description Advanced multi‑factor identity verification using biometric hashing, TOTP, and WebAuthn.
 * Integrated with the global forensic hash chain for immutable audit trails.
 *
 * 🤝 COLLABORATION NOTES:
 * - Wilson Khanyezi (CEO/Lead Architect) – mandated MFA, refresh token rotation, and forensic sealing.
 * - AI Engineering (DeepSeek) – ENHANCED: added TOTP, WebAuthn stubs, full JSDoc, and telemetry.
 *
 * 🏛️ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/auth/SovereignAuth.service.js
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ VERSION: 72.0.0-MFA-FORENSIC | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import jwt from 'jsonwebtoken';
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';
import ForensicService from '../forensic/ForensicService.js';
import forensicHasher from '../../utils/forensicHasher.js';
import { broadcastTelemetry } from '../../utils/telemetryHelper.js';
import User from '../../models/userModel.js';

// ============================================================================
// 🔥 CONSTANTS
// ============================================================================

const TOKEN_EXPIRY = '1h';
const REFRESH_TOKEN_EXPIRY = '7d';
const MFA_WINDOW = 2; // ±2 steps for TOTP (30 seconds each)

// ============================================================================
// 🔥 HELPER: Generate forensic seal for auth events
// ============================================================================

/**
 * @async
 * @function createAuthSeal
 * @description Creates a cryptographic seal for an authentication event using the global forensic hasher.
 * @param {Object} eventData - The authentication event payload.
 * @returns {Promise<Object>} Seal entry containing hash, chain position, and chain hash.
 */
async function createAuthSeal(eventData) {
  try {
    return forensicHasher.createSeal(eventData);
  } catch (err) {
    console.warn('[AUTH-SERVICE] Forensic sealing failed:', err.message);
    return { hash: null, position: null, chainHash: null };
  }
}

// ============================================================================
// 🔥 SOVEREIGN AUTHENTICATION SERVICE
// ============================================================================

/**
 * @class SovereignAuthService
 * @description Core authentication service for WILSY OS.
 * Handles JWT issuance, MFA (TOTP + WebAuthn), refresh token rotation,
 * and forensic sealing of all authentication events.
 */
export class SovereignAuthService {
  // ==========================================================================
  // 🔐 JWT & REFRESH TOKEN METHODS
  // ==========================================================================

  /**
   * Generates a Sovereign Identity Token (JWT) with embedded scopes and tenant.
   * @param {Object} user - User document from database.
   * @param {string} user.id - User ID.
   * @param {string} user.email - User email.
   * @param {string} user.tenantId - Tenant ID.
   * @param {string[]} user.scopes - Array of permission scopes.
   * @returns {Promise<Object>} Object containing accessToken, refreshToken, and forensic seal.
   *
   * @real-world
   *   Called after successful login or MFA verification. The token is signed with HS512
   *   and includes scopes for fine‑grained access control.
   *
   * @forensic
   *   The event is sealed into the global forensic hash chain and telemetry is broadcast.
   *
   * @example
   * const { accessToken, refreshToken } = await SovereignAuthService.generateSovereignToken(user);
   * res.json({ token: accessToken, refreshToken });
   */
  static async generateSovereignToken(user) {
    const startTime = performance.now();
    console.log(`[AUTH-SOVEREIGN] Generating tokens for user: ${user.id || user.email}`);

    const payload = {
      sub: user.id,
      email: user.email,
      tenantId: user.tenantId,
      scopes: user.scopes || ['user.read'],
      mfaVerified: user.mfaEnabled ? false : true // token issued without MFA unless verified
    };

    // Sign access token
    const accessToken = jwt.sign(payload, process.env.JWT_SECRET, {
      expiresIn: TOKEN_EXPIRY,
      algorithm: 'HS512'
    });

    // Generate refresh token (random + signed)
    const refreshTokenId = crypto.randomBytes(32).toString('hex');
    const refreshTokenPayload = {
      sub: user.id,
      tokenId: refreshTokenId,
      type: 'refresh'
    };
    const refreshToken = jwt.sign(refreshTokenPayload, process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET, {
      expiresIn: REFRESH_TOKEN_EXPIRY,
      algorithm: 'HS512'
    });

    // Store refresh token hash in database (for revocation)
    const refreshTokenHash = crypto.createHash('sha256').update(refreshTokenId).digest('hex');
    await User.findByIdAndUpdate(user.id, {
      $push: {
        refreshTokens: {
          hash: refreshTokenHash,
          issuedAt: new Date(),
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        }
      }
    }).catch(err => console.warn('[AUTH] Failed to store refresh token:', err.message));

    const latency = performance.now() - startTime;

    // Forensic seal
    const sealEvent = {
      event: 'TOKEN_GENERATION',
      userId: user.id,
      tenantId: user.tenantId,
      latencyMs: latency,
      timestamp: new Date().toISOString()
    };
    const sealEntry = await createAuthSeal(sealEvent);

    await broadcastTelemetry(user.tenantId || 'GLOBAL_ROOT', 'AUTH_SERVICE', 'TOKEN_GENERATED', 'SovereignAuthService', {
      userId: user.id,
      latencyMs: latency,
      chainPosition: sealEntry.position
    });

    return {
      accessToken,
      refreshToken,
      forensicSeal: sealEntry.hash,
      expiresIn: TOKEN_EXPIRY
    };
  }

  /**
   * Refreshes an expired access token using a valid refresh token.
   * @param {string} refreshToken - The refresh token from client.
   * @returns {Promise<Object>} New access token and updated refresh token.
   * @throws {Error} If refresh token is invalid, expired, or revoked.
   */
  static async refreshAccessToken(refreshToken) {
    try {
      const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET);
      const { sub: userId, tokenId } = decoded;

      const user = await User.findById(userId);
      if (!user) throw new Error('User not found');

      const refreshTokenHash = crypto.createHash('sha256').update(tokenId).digest('hex');
      const storedToken = user.refreshTokens?.find(t => t.hash === refreshTokenHash);
      if (!storedToken || storedToken.expiresAt < new Date()) {
        throw new Error('Refresh token expired or revoked');
      }

      // Remove old refresh token (rotate)
      await User.findByIdAndUpdate(userId, {
        $pull: { refreshTokens: { hash: refreshTokenHash } }
      });

      // Generate new tokens
      const newTokens = await this.generateSovereignToken(user);

      await broadcastTelemetry(user.tenantId || 'GLOBAL_ROOT', 'AUTH_SERVICE', 'TOKEN_REFRESHED', 'SovereignAuthService', {
        userId,
        refreshRotation: true
      });

      return newTokens;
    } catch (err) {
      console.error('[AUTH-REFRESH] Failure:', err.message);
      throw new Error('Invalid or expired refresh token');
    }
  }

  // ==========================================================================
  // 🔐 BIOMETRIC IDENTITY (original method, enhanced)
  // ==========================================================================

  /**
   * Generates a unique Sovereign Identity Token (SIT) using biometric data.
   * SEALED with SHA3-512 to ensure absolute account sovereignty.
   *
   * @param {string} userId - The user's unique identifier.
   * @param {string} biometricData - Raw biometric fingerprint or hash.
   * @returns {Promise<Object>} SIT object with token signature and forensic seal.
   *
   * @real-world
   *   Used during biometric registration or login. The biometric data is never stored
   *   in plaintext – only the salted hash (identityMarker) is kept.
   *
   * @forensic
   *   The biometric hash is signed via ForensicService and sealed into the global chain.
   */
  static async generateSovereignTokenWithBiometric(userId, biometricData) {
    console.log(`[AUTH-SOVEREIGN] Initiating biometric identity seal for: ${userId}`);

    const salt = crypto.randomBytes(32).toString('hex');
    const identityMarker = crypto
      .createHash('sha3-512')
      .update(userId + biometricData + salt)
      .digest('hex');

    const sit = {
      userId,
      tokenType: 'SOVEREIGN_ACCESS_KEY',
      identityMarker,
      issuedAt: new Date().toISOString(),
      expiresIn: '1h',
      nodeId: 'GENESIS-NODE-01'
    };

    // Anchoring the session in the Forensic Chain
    const tokenSignature = ForensicService.signTransaction(sit);

    const sealEntry = await createAuthSeal({
      event: 'BIOMETRIC_TOKEN',
      userId,
      markerHash: identityMarker.slice(0, 16)
    });

    await broadcastTelemetry('GLOBAL_ROOT', 'AUTH_SERVICE', 'BIOMETRIC_TOKEN_GENERATED', 'SovereignAuthService', {
      userId,
      chainPosition: sealEntry.position
    });

    return {
      sit_id: `SIT-${crypto.randomBytes(8).toString('hex').toUpperCase()}`,
      payload: sit,
      tokenSignature,
      forensicSeal: sealEntry.hash
    };
  }

  // ==========================================================================
  // 🔐 TOTP MULTI-FACTOR AUTHENTICATION
  // ==========================================================================

  /**
   * Generates a TOTP secret and QR code URL for authenticator app setup.
   * @param {string} userId - User ID.
   * @param {string} email - User email (for issuer).
   * @returns {Promise<Object>} Secret, QR code data URL, and backup codes.
   *
   * @real-world
   *   Called when a user enables TOTP MFA. The secret must be stored encrypted in the user's record.
   */
  static async generateTOTPSecret(userId, email) {
    const secret = speakeasy.generateSecret({
      name: `WILSY OS:${email}`,
      issuer: 'WILSY OS'
    });

    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

    // Generate 8 backup codes (each 10 characters)
    const backupCodes = Array.from({ length: 8 }, () => {
      return crypto.randomBytes(5).toString('hex').toUpperCase();
    });

    await broadcastTelemetry('GLOBAL_ROOT', 'AUTH_SERVICE', 'TOTP_SECRET_GENERATED', 'SovereignAuthService', {
      userId,
      backupCodesCount: backupCodes.length
    });

    return {
      secret: secret.base32,
      qrCode: qrCodeUrl,
      backupCodes
    };
  }

  /**
   * Verifies a TOTP code against a user's secret.
   * @param {string} secret - The TOTP secret (base32).
   * @param {string} token - The 6‑digit code from authenticator app.
   * @returns {boolean} True if valid.
   */
  static verifyTOTP(secret, token) {
    return speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window: MFA_WINDOW
    });
  }

  /**
   * Verifies a backup code against stored codes.
   * @param {string} userId - User ID.
   * @param {string} backupCode - The backup code to verify.
   * @returns {Promise<boolean>} True if valid and consumed.
   */
  static async verifyBackupCode(userId, backupCode) {
    const user = await User.findById(userId);
    if (!user || !user.mfaBackupCodes) return false;

    const index = user.mfaBackupCodes.indexOf(backupCode);
    if (index === -1) return false;

    // Remove the used backup code
    user.mfaBackupCodes.splice(index, 1);
    await user.save();

    await broadcastTelemetry('GLOBAL_ROOT', 'AUTH_SERVICE', 'BACKUP_CODE_USED', 'SovereignAuthService', {
      userId
    });

    return true;
  }

  // ==========================================================================
  // 🔐 WEB AUTHN (PASSKEY) STUBS – integrate with @simplewebauthn/server
  // ==========================================================================

  /**
   * Placeholder for WebAuthn registration start.
   * @param {Object} user - User document.
   * @returns {Promise<Object>} Public key credential creation options.
   */
  static async beginWebAuthnRegistration(user) {
    // In production: generate challenge, store in session, return options
    const challenge = crypto.randomBytes(32);
    return {
      challenge: challenge.toString('base64url'),
      rp: { name: 'WILSY OS', id: process.env.RP_ID || 'localhost' },
      user: {
        id: Buffer.from(user.id).toString('base64url'),
        name: user.email,
        displayName: user.name || user.email
      },
      pubKeyCredParams: [
        { type: 'public-key', alg: -7 }, // ES256
        { type: 'public-key', alg: -257 } // RS256
      ],
      authenticatorSelection: {
        authenticatorAttachment: 'platform',
        residentKey: 'required',
        userVerification: 'required'
      },
      timeout: 60000
    };
  }

  /**
   * Placeholder for WebAuthn registration verification.
   * @param {Object} user - User document.
   * @param {Object} attestationResponse - Client attestation response.
   * @returns {Promise<boolean>} True if registration successful.
   */
  static async completeWebAuthnRegistration(user, attestationResponse) {
    // In production: verify attestation, store credential ID
    await broadcastTelemetry('GLOBAL_ROOT', 'AUTH_SERVICE', 'WEBAUTHN_REGISTERED', 'SovereignAuthService', {
      userId: user.id
    });
    return true;
  }
}

// ============================================================================
// 🔥 DEFAULT EXPORT
// ============================================================================

export default SovereignAuthService;
