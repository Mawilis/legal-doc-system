/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FULL ONBOARDING PIPELINE TESTER [V1.0.0-PRODUCTION]                                                                         ║
 * ║ Validation → Seeding → Forensic Sealing | End-to-End Test                                                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0 | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                            ║
 * ║ IDENTITY ANCHORED: WILSON KHANYEZI | SOVEREIGN ARCHITECT                                                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { validateOnboardingData } from './validateOnboarding.js';
import seedTenant from './seedTenantFromOnboarding.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const testOnboardingPipeline = async (dataPath = null) => {
  try {
    console.log('\n🏛️  WILSY OS FULL ONBOARDING PIPELINE TESTER v1.0.0');
    console.log('⚡ Running complete Validation → Seeding sequence...\n');

    // Default to example file if none provided (Pointing to our Royal Logistics payload)
    const defaultPath = path.resolve(__dirname, '../data/royal-logistics-onboarding.json');
    const filePath = dataPath ? path.resolve(dataPath) : defaultPath;

    console.log(`📂 Target Data File: ${path.basename(filePath)}`);

    // Step 1: Load Data
    let onboardingData;
    try {
      const rawData = fs.readFileSync(filePath, 'utf8');
      onboardingData = JSON.parse(rawData);
      console.log('✅ Data file loaded successfully');
    } catch (err) {
      throw new Error(`Failed to load data file: ${err.message}`);
    }

    // Step 2: Validation Phase
    console.log('\n🔍 PHASE 1 — FORENSIC VALIDATION');
    validateOnboardingData(onboardingData);
    console.log('✅ Validation Phase: PASSED\n');

    // Step 3: Onboarding Phase
    console.log('🚀 PHASE 2 — SOVEREIGN ONBOARDING & SEALING');
    const result = await seedTenant(onboardingData);

    // Final Success Report
    console.log('\n🎉════════════════════════════════════════════════════════════════════════════╗');
    console.log('║             FULL PIPELINE TEST COMPLETED SUCCESSFULLY                    ║');
    console.log('╠════════════════════════════════════════════════════════════════════════════╣');
    console.log(`║ Tenant ID     : ${onboardingData.tenantId}`);
    console.log(`║ Legal Name    : ${onboardingData.legalName}`);
    console.log(`║ Node Seal     : ${result.masterNode?.nodeSeal?.substring(0, 48)}...`);
    console.log(`║ Status        : ✅ FULLY ANCHORED & CRYPTOGRAPHICALLY SEALED`);
    console.log('╚════════════════════════════════════════════════════════════════════════════╝\n');
    console.log('🎯 TEST RESULT: SUCCESS — System is ready for production onboarding.');

    return { success: true, tenantId: onboardingData.tenantId };
  } catch (err) {
    console.error('\n💥 PIPELINE TEST FAILED');
    console.error(err.message);
    console.error('\n🔧 Fix the issue above and run the test again.');
    process.exit(1);
  }
};

// ====================== CLI EXECUTION ======================
if (import.meta.url === `file://${process.argv[1]}`) {
  const argPath = process.argv[2];
  testOnboardingPipeline(argPath);
}

export default testOnboardingPipeline;
