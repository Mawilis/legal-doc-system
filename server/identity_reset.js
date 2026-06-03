/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - IDENTITY RESET COMMAND [V2.0.0-ENV-SEALED]                                                                                ║
 * ║ [SERVER ENV LOADING | ADMIN RESET | NO EMBEDDED PASSWORDS | TENANT ANCHORING | PASSWORD OUTPUT SUPPRESSION]                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-ENV-SEALED | PRODUCTION MAINTENANCE TOOL | SECURITY-FIRST IDENTITY RECOVERY                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/identity_reset.js                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated no sensitive Wilsy OS credentials may live inside source files.                          ║
 * ║ • AI Engineering (Codex) - HARDENED: Replaced embedded Mongo credentials/passwords with server/.env keys and suppressed secret logs. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * @function requireIdentityEnv
 * @description Resolves a required identity reset value from server/.env.
 * @param {string} key - Environment key.
 * @returns {string} Required environment value.
 * @collaboration Identity recovery must fail closed when a credential or tenant anchor is not configured.
 */
const requireIdentityEnv = (key) => {
  const value = process.env[key];
  if (!value) throw new Error(`Missing required server/.env key: ${key}`);
  return value;
};

const TENANT_DB_URI = requireIdentityEnv('MONGODB_URI');
const ADMIN_EMAIL = requireIdentityEnv('ADMIN_EMAIL');
const NEW_PASSWORD = requireIdentityEnv('ADMIN_PASSWORD');
const FOUNDER_TENANT_ID = requireIdentityEnv('FOUNDER_TENANT_ID');
if (!mongoose.Types.ObjectId.isValid(FOUNDER_TENANT_ID)) {
  throw new Error('FOUNDER_TENANT_ID must be a MongoDB ObjectId for identity_reset.js.');
}
const [firstName = 'Wilsy', lastName = 'Admin'] = String(process.env.ADMIN_NAME || 'Wilsy Admin').split(/\s+/, 2);

const UserSchema = new mongoose.Schema({
  firstName: String,
  lastName: String,
  email: { type: String, unique: true, lowercase: true },
  password: { type: String, required: true },
  role: { type: String, default: process.env.ADMIN_ROLE || 'admin' },
  tenantId: mongoose.Schema.Types.ObjectId,
  securityMetadata: {
    mfaEnabled: { type: Boolean, default: false },
    lastLogin: Date
  }
}, { timestamps: true });

/**
 * @function resetIdentity
 * @description Resets the configured admin identity using server/.env credentials.
 * @returns {Promise<void>} Resolves after the identity is anchored or exits on failure.
 * @collaboration Preserves emergency recovery capability without leaking admin passwords or database credentials into git.
 */
async function resetIdentity() {
  try {
    console.log('[IDENTITY-RESET] Connecting through server/.env MONGODB_URI...');
    const conn = await mongoose.createConnection(TENANT_DB_URI).asPromise();
    const User = conn.model('User', UserSchema);

    const hashed = await bcrypt.hash(NEW_PASSWORD, Number(process.env.PASSWORD_HASH_SALT_ROUNDS || 12));

    const result = await User.findOneAndUpdate(
      { email: ADMIN_EMAIL },
      {
        firstName,
        lastName,
        password: hashed,
        role: process.env.ADMIN_ROLE || 'admin',
        tenantId: new mongoose.Types.ObjectId(FOUNDER_TENANT_ID),
        'securityMetadata.mfaEnabled': false
      },
      { upsert: true, returnDocument: 'after' }
    );

    console.log(`[IDENTITY-RESET] SUCCESS: ${result.email} anchored to tenant ${FOUNDER_TENANT_ID}.`);
    console.log('[IDENTITY-RESET] Password sourced from server/.env and intentionally not printed.');

    await conn.close();
    process.exit(0);
  } catch (error) {
    console.error('[IDENTITY-RESET] FAILED:', error.message);
    process.exit(1);
  }
}

resetIdentity();
