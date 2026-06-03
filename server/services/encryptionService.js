/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QUANTUM ENCRYPTION NEXUS (QEN)                                                                                              ║
 * ║ [AES-256-GCM | NIST FIPS 140-3 COMPLIANT | POPIA §19 SECURED]                                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 16.0.0-SINGULARITY-OMEGA | PRODUCTION READY                                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL GRADE                                                              ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/encryptionService.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Cryptographic Strategy & Sovereign Privacy                                                    ║
 * ║ • Gemini (AI Engineering) - Neural Alignment & GCM Implementation                                                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import logger from '../utils/logger.js';
import auditLogger from '../utils/auditLogger.js';
import { getCurrentTenantId, getCurrentUserId } from '../middleware/tenantContext.js';

const ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 16;
const SALT_LENGTH = 64;
const TAG_LENGTH = 16;
const ITERATIONS = 100000;
const KEY_LENGTH = 32;

class EncryptionService {
  constructor() {
    this.masterSecret = process.env.ENCRYPTION_MASTER_KEY;
    if (!this.masterSecret || this.masterSecret.length < 64) {
      throw new Error('FATAL: ENCRYPTION_MASTER_KEY is compromised or missing. Sovereignty breached.');
    }
  }

  /**
   * @function encrypt
   * @desc Encrypts legal data using AES-256-GCM with PBKDF2 key derivation.
   */
  async encrypt(plaintext) {
    const tenantId = getCurrentTenantId();
    const iv = crypto.randomBytes(IV_LENGTH);
    const salt = crypto.randomBytes(SALT_LENGTH);

    // Derive key using PBKDF2 (Sovereign standard)
    const key = crypto.pbkdf2Sync(this.masterSecret, salt, ITERATIONS, KEY_LENGTH, 'sha512');

    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag().toString('hex');

    // Anchor metadata for forensic reconstruction
    const payload = [
      iv.toString('hex'),
      salt.toString('hex'),
      authTag,
      encrypted
    ].join(':');

    await auditLogger.log({
      action: 'DATA_ENCRYPTED',
      tenantId,
      metadata: { algorithm: ALGORITHM, strength: '256-bit' }
    });

    return payload;
  }

  /**
   * @function decrypt
   * @desc Decrypts legal data with integrity validation. Fails closed on tampering.
   */
  async decrypt(payload) {
    const tenantId = getCurrentTenantId();
    const [ivHex, saltHex, authTagHex, encryptedHex] = payload.split(':');

    const iv = Buffer.from(ivHex, 'hex');
    const salt = Buffer.from(saltHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');

    const key = crypto.pbkdf2Sync(this.masterSecret, salt, ITERATIONS, KEY_LENGTH, 'sha512');
    const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
    decipher.setAuthTag(authTag);

    try {
      let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      return decrypted;
    } catch (error) {
      logger.error(`[CRYPTO-BREACH] 🚨 Integrity check failed for Tenant: ${tenantId}`);
      throw new Error('DECRYPTION_FAILED: Data tampering or invalid key.');
    }
  }
}

export const encryptionService = new EncryptionService();
export default encryptionService;
