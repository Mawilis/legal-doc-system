/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY ANCHOR [V2.0.0-ENV-SEALED]                                                                             ║
 * ║ [TENANT ANCHOR | USER ROLE SYNC | SERVER ENV LOADING | NO DATABASE CREDENTIALS IN SOURCE]                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-ENV-SEALED | PRODUCTION MAINTENANCE TOOL | LEDGER IDENTITY ALIGNMENT                                                ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/anchor_identity.js                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required identity anchoring without hardcoded Mongo credentials or private operator data.          ║
 * ║ • AI Engineering (Codex) - HARDENED: Moved runtime authority values to server/.env and kept maintenance output secret-safe.          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * @function requireAnchorEnv
 * @description Resolves required identity anchor configuration from server/.env.
 * @param {string} key - Environment key.
 * @returns {string} Environment value.
 * @collaboration Identity anchoring must be configured per deployment and never carry credentials in source code.
 */
const requireAnchorEnv = (key) => {
  const value = process.env[key];
  if (!value) throw new Error(`Missing required server/.env key: ${key}`);
  return value;
};

/**
 * @function anchor
 * @description Aligns the configured tenant and admin user to the sovereign ledger.
 * @returns {Promise<void>} Resolves after ledger alignment or exits on failure.
 * @collaboration Gives operators a repeatable recovery command without leaking private credentials.
 */
async function anchor() {
  const mongoUri = requireAnchorEnv('MONGODB_URI');
  const tenantSlug = process.env.DEFAULT_TENANT_SLUG || process.env.FOUNDER_TENANT_ID || 'wilsy';
  const tenantName = process.env.DEFAULT_TENANT_NAME || process.env.APP_NAME || 'WILSY OS';
  const tenantStatus = process.env.DEFAULT_TENANT_STATUS || 'ACTIVE';
  const tenantTier = process.env.DEFAULT_TENANT_TIER || 'SOVEREIGN';
  const adminEmail = requireAnchorEnv('ADMIN_EMAIL');
  const adminRole = process.env.ADMIN_ROLE || 'superadmin';

  try {
    console.log('[WILSY OS] INITIATING ENV-SEALED SOVEREIGN IDENTITY ANCHOR...');
    await mongoose.connect(mongoUri);
    const db = mongoose.connection.db;

    const tenantUpdate = await db.collection('tenants').updateOne(
      { slug: tenantSlug },
      {
        $set: {
          slug: tenantSlug,
          name: tenantName,
          status: tenantStatus,
          tier: tenantTier,
          updatedAt: new Date()
        }
      },
      { upsert: true }
    );
    console.log(`[LEDGER] TENANT "${tenantSlug}" ANCHORED: ${tenantUpdate.modifiedCount || tenantUpdate.upsertedCount} record(s) updated.`);

    const userUpdate = await db.collection('users').updateOne(
      { email: adminEmail },
      {
        $set: {
          tenantId: tenantSlug,
          role: adminRole,
          status: 'active',
          updatedAt: new Date()
        }
      }
    );
    console.log(`[LEDGER] USER IDENTITY SYNCED TO "${tenantSlug}": ${userUpdate.modifiedCount} record(s) updated.`);

    console.log('[WILSY OS] IDENTITY ORCHESTRATION COMPLETE.');
    process.exit(0);
  } catch (err) {
    console.error('[WILSY OS] ANCHOR FATAL:', err.message);
    process.exit(1);
  }
}

anchor();
