/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ONBOARDING DATA VALIDATOR [V1.1.0-PRODUCTION]                                                                               ║
 * ║ Forensic Schema Validation | Strict Compliance Enforcement                                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0 | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                            ║
 * ║ IDENTITY ANCHORED: WILSON KHANYEZI | SOVEREIGN ARCHITECT                                                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load JSON Schema
const schemaPath = path.resolve(__dirname, '../schemas/tenantOnboardingSchema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'));

const ajv = new Ajv({
  allErrors: true,
  strict: true,
  verbose: true
});
addFormats(ajv);

const validateSchema = ajv.compile(schema);

/**
 * Validates onboarding data with forensic-level checks
 * @param {Object} data - Onboarding data object
 * @returns {boolean} - True if valid
 */
export const validateOnboardingData = (data) => {
  console.log('🔍 [WILSY OS] Running Forensic Validation Protocol...');

  if (!data || typeof data !== 'object') {
    throw new Error("FRACTURE: Onboarding data must be a valid object");
  }

  // Schema Validation
  const valid = validateSchema(data);
  if (!valid) {
    const errors = validateSchema.errors.map(err => {
      const field = err.instancePath ? err.instancePath.replace('/', '') : 'root';
      return `→ ${field}: ${err.message}`;
    });
    throw new Error(`VALIDATION FRACTURE:\n${errors.join('\n')}`);
  }

  // Business Logic & Integrity Checks
  const criticalErrors = [];

  if (!data.tenantId || data.tenantId.length < 3) {
    criticalErrors.push("→ tenantId must be at least 3 characters (e.g., ACME_CORP)");
  }
  if (!data.legalName || data.legalName.trim().length < 3) {
    criticalErrors.push("→ legalName is required and must be meaningful");
  }
  if (!data.registrationNumber) {
    criticalErrors.push("→ registrationNumber (CIPC / Equivalent) is required");
  }
  if (!data.taxNumber) {
    criticalErrors.push("→ taxNumber (SARS / Equivalent) is required");
  }

  if (typeof data.latitude === 'undefined' || typeof data.longitude === 'undefined') {
    criticalErrors.push("→ Geolocation (latitude & longitude) is mandatory for Master Node anchoring");
  } else {
    if (data.latitude < -90 || data.latitude > 90) {
      criticalErrors.push("→ latitude must be between -90 and 90");
    }
    if (data.longitude < -180 || data.longitude > 180) {
      criticalErrors.push("→ longitude must be between -180 and 180");
    }
  }

  if (criticalErrors.length > 0) {
    throw new Error(`BUSINESS RULE FRACTURE:\n${criticalErrors.join('\n')}`);
  }

  console.log('✅ [WILSY OS] Forensic Validation PASSED — Data Integrity Confirmed');
  return true;
};

// ====================== CLI EXECUTION ======================
if (import.meta.url === `file://${process.argv[1]}`) {
  const filePath = process.argv[2];

  if (!filePath) {
    console.error('\n❌ USAGE:');
    console.error('   node validateOnboarding.js <path-to-onboarding-data.json>\n');
    process.exit(1);
  }

  try {
    const absolutePath = path.resolve(filePath);

    if (!fs.existsSync(absolutePath)) {
      throw new Error(`File not found: ${absolutePath}`);
    }

    const rawData = fs.readFileSync(absolutePath, 'utf8');
    const data = JSON.parse(rawData);

    validateOnboardingData(data);

    console.log('\n🎉 VALIDATION SUCCESSFUL — Ready for Sovereign Onboarding');
    console.log(`Tenant ID: ${data.tenantId}`);
    console.log(`Legal Name: ${data.legalName}`);
  } catch (err) {
    console.error('\n💥 [VALIDATION FAILED]');
    console.error(err.message);
    process.exit(1);
  }
}

export default validateOnboardingData;
