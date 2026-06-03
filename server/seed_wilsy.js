/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ENV-SEALED TENANT SEED COMMAND [V2.0.0-PRODUCTION-CONFIG]                                                                 ║
 * ║ [TENANT SEED | COMPANY PROFILE | SERVER ENV LOADING | NO PRIVATE CONTACT DATA IN SOURCE]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-PRODUCTION-CONFIG | PRODUCTION MAINTENANCE TOOL | TENANT LEDGER ANCHORING                                            ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/seed_wilsy.js                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required tenant seeding to use env-owned business identity values rather than embedded data.       ║
 * ║ • AI Engineering (Codex) - HARDENED: Converted company profile seeding into an env-driven maintenance command.                      ║
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
 * @function requireSeedEnv
 * @description Resolves a required tenant seed value from server/.env.
 * @param {string} key - Environment key.
 * @returns {string} Environment value.
 * @collaboration Tenant seeding must fail closed when the database or admin identity is not configured.
 */
const requireSeedEnv = (key) => {
  const value = process.env[key];
  if (!value) throw new Error(`Missing required server/.env key: ${key}`);
  return value;
};

/**
 * @function readSeedEnv
 * @description Reads an optional tenant seed value from server/.env.
 * @param {string} key - Environment key.
 * @param {string} fallback - Non-sensitive fallback.
 * @returns {string} Environment value or fallback.
 * @collaboration Keeps tenant profile fields deployment-owned without forcing every tenant to provide every optional field.
 */
const readSeedEnv = (key, fallback = 'SOURCE_REQUIRED') => {
  const value = process.env[key];
  return value === undefined || value === null || value === '' ? fallback : value;
};

/**
 * @function buildTenantSeed
 * @description Builds the tenant profile from server/.env.
 * @returns {Object} Tenant seed payload.
 * @collaboration Allows Wilsy OS to seed different businesses without creating a new script for every tenant.
 */
const buildTenantSeed = () => ({
  name: readSeedEnv('DEFAULT_TENANT_NAME', readSeedEnv('APP_NAME', 'WILSY OS')),
  registrationNumber: readSeedEnv('COMPANY_REGISTRATION_NUMBER'),
  taxNumber: readSeedEnv('COMPANY_TAX_NUMBER', readSeedEnv('COMPANY_VAT_NUMBER')),
  slug: readSeedEnv('DEFAULT_TENANT_SLUG', 'wilsy'),
  dbName: readSeedEnv('MONGODB_DATABASE', 'wilsy-sovereign-root'),
  adminEmail: requireSeedEnv('ADMIN_EMAIL'),
  contactNumber: readSeedEnv('ADMIN_PHONE'),
  status: readSeedEnv('DEFAULT_TENANT_STATUS', 'active'),
  plan: readSeedEnv('DEFAULT_TENANT_TIER', 'sovereign'),
  address: {
    street: readSeedEnv('COMPANY_ADDRESS_STREET'),
    suburb: readSeedEnv('COMPANY_ADDRESS_SUBURB'),
    city: readSeedEnv('COMPANY_ADDRESS_CITY'),
    province: readSeedEnv('COMPANY_ADDRESS_PROVINCE'),
    postalCode: readSeedEnv('COMPANY_ADDRESS_POSTAL_CODE')
  },
  metadata: {
    registrationDate: readSeedEnv('COMPANY_REGISTRATION_DATE'),
    financialYearEnd: readSeedEnv('COMPANY_FINANCIAL_YEAR_END', 'February'),
    version: readSeedEnv('APP_VERSION', 'ENV_DECLARED')
  }
});

/**
 * @function seed
 * @description Anchors the configured tenant and links the configured admin user.
 * @returns {Promise<void>} Resolves after tenant seed completion or exits on failure.
 * @collaboration Turns tenant seeding into a reusable operating command instead of source-code data entry.
 */
async function seed() {
  const dbUri = requireSeedEnv('MONGODB_URI');
  const tenantData = buildTenantSeed();

  try {
    console.log('[WILSY OS] ANCHORING ENV-DECLARED ENTERPRISE TO SOVEREIGN LEDGER...');
    await mongoose.connect(dbUri);

    await mongoose.connection.db.collection('tenants').updateOne(
      { slug: tenantData.slug },
      { $set: tenantData },
      { upsert: true }
    );

    await mongoose.connection.db.collection('users').updateOne(
      { email: tenantData.adminEmail },
      { $set: { tenantId: tenantData.slug } }
    );

    console.log(`[WILSY OS] ENTERPRISE ANCHORED SUCCESSFULLY: ${tenantData.slug}`);
    process.exit(0);
  } catch (err) {
    console.error('[WILSY OS] ANCHORING FATAL:', err.message);
    process.exit(1);
  }
}

seed();
