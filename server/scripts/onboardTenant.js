/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MASTER TENANT ONBOARDING COMMAND [V1.3.0-PRODUCTION]                                                                        ║
 * ║ One-Command Sovereign Onboarding | Validation + Seeding + Forensic Sealing                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.3.0 | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                            ║
 * ║ IDENTITY ANCHORED: WILSON KHANYEZI | SOVEREIGN ARCHITECT                                                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { validateOnboardingData } from './validateOnboarding.js';
import seedTenant from './seedTenantFromOnboarding.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../../.env') });

/**
 * Master Onboarding Function - Validates then Seeds
 * @param {string|object} input - File path or onboarding data object
 */
const onboardTenant = async (input) => {
  try {
    console.log('\n🏛️  WILSY OS SOVEREIGN ONBOARDING ENGINE v1.3.0');
    console.log('⚡ Initializing Universal Tenant Protocol...\n');

    let onboardingData;

    // Handle both file path and direct object input
    if (typeof input === 'string') {
      const filePath = path.resolve(input);

      if (!fs.existsSync(filePath)) {
        throw new Error(`Onboarding file not found: ${filePath}`);
      }

      console.log(`📂 Loading data from: ${path.basename(filePath)}`);
      const rawData = fs.readFileSync(filePath, 'utf8');
      onboardingData = JSON.parse(rawData);
    } else if (typeof input === 'object' && input !== null) {
      onboardingData = input;
      console.log('📥 Received direct onboarding data object');
    } else {
      throw new Error('Invalid input: Must be a file path (string) or data object');
    }

    // ====================== VALIDATION ======================
    console.log('🔍 Running forensic data validation...');
    validateOnboardingData(onboardingData);

    // ====================== SEEDING ======================
    console.log('🚀 Passing to Sovereign Seeder...');
    const result = await seedTenant(onboardingData);

    // ====================== FINALITY ======================
    console.log('\n🎉════════════════════════════════════════════════════════════════════════════╗');
    console.log('║                  SOVEREIGN ONBOARDING COMPLETED SUCCESSFULLY                  ║');
    console.log('╚════════════════════════════════════════════════════════════════════════════╝\n');

    return {
      success: true,
      tenantId: onboardingData.tenantId,
      legalName: onboardingData.legalName,
      nodeSeal: result.masterNode?.nodeSeal,
      timestamp: new Date().toISOString()
    };

  } catch (err) {
    console.error('\n💥 [CRITICAL FRACTURE] Onboarding Failed');
    console.error(`Reason: ${err.message}`);
    if (err.stack) console.error(err.stack);
    process.exit(1);
  }
};

// ====================== CLI EXECUTION ======================
if (import.meta.url === `file://${process.argv[1]}`) {
  const input = process.argv[2];

  if (!input) {
    console.error('\n❌ USAGE:');
    console.error('   node onboardTenant.js <path-to-onboarding-data.json>');
    console.error('   or');
    console.error('   npm run onboard -- <path-to-onboarding-data.json>\n');
    process.exit(1);
  }

  onboardTenant(input);
}

export default onboardTenant;
