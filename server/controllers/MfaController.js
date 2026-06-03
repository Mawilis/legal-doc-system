/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN MFA CONTROLLER [V15.0.1-IGNITION]                                                                                 ║
 * ║ [TOTP ORCHESTRATION | CRYPTO VAULT INTEGRATION | FORENSIC IDENTITY VERIFICATION]                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 15.0.1-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/MfaController.js                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated encrypted secret storage and immutable backup code generation.                       ║
 * ║ • Gemini (AI Engineering) - RECTIFIED: Export alignment and error handling for zero-latency ignition.                                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import cryptoUtils from '../utils/cryptoUtils.js'; // 🛡️ RECTIFIED: Default import for cryptoUtils
import User from '../models/userModel.js';
import logger from '../utils/logger.js';
import speakeasy from 'speakeasy';
import qrcode from 'qrcode';

/**
 * @function nativeAsync
 * @desc Sovereign wrapper for zero-dependency promise handling.
 */
const nativeAsync = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

/**
 * @desc Initialize MFA Setup - Generates Secret and QR Code
 * @route POST /api/mfa/setup
 */
export const setupMfa = nativeAsync(async (req, res) => {
  const user = await User.findById(req.user._id);
  if (!user) {
    return res.status(404).json({ success: false, message: 'IDENTITY_FRAGMENT_NOT_FOUND' });
  }

  const secret = speakeasy.generateSecret({
    name: `WilsyOS:${user.email}`,
    issuer: 'Wilsy OS Citadel'
  });

  // 🔐 ENCRYPT: Store the secret in the vault using Wilsy Crypto Core
  user.mfaSecret = cryptoUtils.encrypt(secret.base32);
  user.mfaEnabled = false; // Pending verification anchor
  await user.save();

  // 🛰️ GENERATE: Forensic QR Code for Google Authenticator
  const qrCodeUrl = await qrcode.toDataURL(secret.otpauth_url);

  res.status(200).json({
    success: true,
    qrCode: qrCodeUrl,
    manualEntryKey: secret.base32,
    forensicTrace: cryptoUtils.generateForensicId('MFA-SETUP')
  });
});

/**
 * @desc Verify and Enable MFA - The Final Anchor
 * @route POST /api/mfa/verify
 */
export const verifyMfa = nativeAsync(async (req, res) => {
  const { token } = req.body;
  if (!token) {
    return res.status(400).json({ success: false, message: 'TOKEN_REQUIRED' });
  }

  const user = await User.findById(req.user._id).select('+mfaSecret');
  if (!user || !user.mfaSecret) {
    return res.status(400).json({ success: false, message: 'MFA_NOT_INITIALIZED' });
  }

  // 🔓 DECRYPT: Retrieve secret from the encrypted vault
  const decryptedSecret = cryptoUtils.decrypt(user.mfaSecret);

  const verified = speakeasy.totp.verify({
    secret: decryptedSecret,
    encoding: 'base32',
    token
  });

  if (!verified) {
    logger.warn(`[MFA-BREACH] 🚨 Failed verification attempt for User: ${user._id}`);
    return res.status(401).json({ success: false, message: 'INVALID_TOKEN' });
  }

  // 💎 GENERATE: Immutable Backup Codes for Sovereign Recovery
  const backupCodes = Array.from({ length: 10 }, () => cryptoUtils.generateForensicId('BC'));

  // Store only SHA3-512 hashes of backup codes for biblical security
  user.mfaBackupCodes = backupCodes.map(code => cryptoUtils.hash(code));
  user.mfaEnabled = true;
  await user.save();

  res.status(200).json({
    success: true,
    message: 'MFA_ENABLED_SOVEREIGN_FINALITY',
    backupCodes, // Exposed exactly once for user archival
    forensicTrace: cryptoUtils.generateForensicId('MFA-VERIFY')
  });
});

// 🏛️ EXPORT ALIGNMENT: Supporting both named and default exports for AMC stability
const MfaController = {
  setupMfa,
  verifyMfa
};

export default MfaController;
