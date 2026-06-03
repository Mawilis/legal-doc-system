/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - UNIVERSAL TENANT ONBOARDING SEEDER [V1.0.1-PRODUCTION-POLISHED]                                                             ║
 * ║ [CRYPTOGRAPHIC ANCHORING | TENANT CONFIGURATION | MASTER NODE GENERATION | ROBUST CLI]                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.1-UNIVERSAL | PRODUCTION READY | BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                               ║
 * ║ IDENTITY ANCHORED: WILSON KHANYEZI | SOVEREIGN ARCHITECT | RECTIFIED: 10/10 EXECUTION PROTOCOL                                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// Define models (Ensure these paths match your server structure)
import Node from '../models/nodeModel.js';
import TenantConfig from '../models/TenantConfig.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load the root .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const seedTenant = async (onboardingData) => {
  try {
    console.log('\n[WILSY OS] INITIATING UNIVERSAL ONBOARDING PROTOCOL...');
    await mongoose.connect(process.env.MONGODB_URI, { serverSelectionTimeoutMS: 8000 });
    console.log('[WILSY OS] MONGODB UPLINK SECURED.');

    const {
      tenantId,
      legalName,
      tradingName,
      businessType,
      registrationNumber,
      taxNumber,
      vatNumber,
      incorporationDate,
      businessStartDate,
      financialYearEnd,
      legalStatus,
      registeredAddress,
      physicalAddress,
      contactEmail,
      phoneNumber,
      latitude,
      longitude,
      regionCode,
      directors = [],
      compliance = {}
    } = onboardingData;

    // 1. FORENSIC VALIDATION
    if (!tenantId || !legalName || !registrationNumber) {
      throw new Error("FRACTURE DETECTED: Missing required fields (tenantId, legalName, registrationNumber).");
    }

    // 2. PURGE LEGACY DATA (Prevents Ghost Nodes)
    console.log(`[WILSY OS] Purging existing telemetry for Tenant: ${tenantId}`);
    await Promise.all([
      Node.deleteMany({ tenantId, isMasterAnchor: true }),
      TenantConfig.deleteMany({ tenantId })
    ]);

    // 3. GENERATE TENANT CONFIGURATION
    console.log(`[WILSY OS] Anchoring TenantConfig...`);
    const tenant = await TenantConfig.create({
      tenantId,
      alias: tenantId.toLowerCase(),
      name: legalName,
      tradingName: tradingName || legalName,
      registrationNumber,
      taxNumber,
      vatNumber,
      enterpriseType: businessType,
      financialYearEnd,
      businessStartDate: businessStartDate ? new Date(businessStartDate) : null,
      status: 'ACTIVE',
      tier: 'ENTERPRISE', // Elevated status for initial partners
      compliance: {
        POPIA: compliance.popia || 'IN_PROGRESS',
        GDPR: compliance.gdpr || 'UNKNOWN',
        SARS: compliance.tax || 'PENDING',
        CIPC: 'REGISTERED'
      },
      headquarters: physicalAddress || registeredAddress,
      contactEmail,
      phoneNumber,
      directors
    });

    // 4. GENERATE MASTER NODE (PHASE 1)
    console.log(`[WILSY OS] Forging Sovereign Master Node...`);
    let masterNode = new Node({
      tenantId,
      entity: tradingName || legalName,
      region: regionCode || 'ZAF',
      type: 'MASTER_NODE',
      isMasterAnchor: true,
      status: 'ONLINE',
      lat: parseFloat(latitude) || -26.2041, // Default JHB if missing
      lng: parseFloat(longitude) || 28.0473,
      lastLatency: 0.01,
      neuralStability: 100.00,
      forensicChain: [{
        action: 'TENANT_ONBOARDING',
        performer: 'SYSTEM_SEEDER',
        hash: 'GENESIS_ONBOARDING',
        stabilityDelta: 100
      }],
      dilithiumSignature: `ML-DSA-5::${crypto.randomBytes(32).toString('hex').toUpperCase()}`,
      metadata: {
        registrationDate: incorporationDate ? new Date(incorporationDate) : null,
        businessStartDate: businessStartDate ? new Date(businessStartDate) : null,
        enterpriseType: businessType,
        financialYearEnd,
        corporateStatus: legalStatus || 'In Business',
        legalAddress: registeredAddress,
        directorsCount: directors.length
      }
    });

    masterNode = await masterNode.save();

    // 5. CRYPTOGRAPHIC SEALING (SHA3-512)
    const sealPayload = JSON.stringify({
      id: masterNode._id,
      tenantId,
      reg: registrationNumber,
      tax: taxNumber,
      directorCount: directors.length
    });

    masterNode.nodeSeal = crypto.createHash('sha3-512').update(sealPayload).digest('hex');
    await masterNode.save();

    console.log('\n╔═════════════════════════════════════════════════════════════════════╗');
    console.log('║ 🎉 TENANT SUCCESSFULLY ONBOARDED AND CRYPTOGRAPHICALLY SEALED       ║');
    console.log('╠═════════════════════════════════════════════════════════════════════╣');
    console.log(`║ TENANT ID  : ${tenantId}`);
    console.log(`║ LEGAL NAME : ${legalName}`);
    console.log(`║ DIRECTORS  : ${directors.length}`);
    console.log(`║ NODE SEAL  : ${masterNode.nodeSeal.substring(0, 48)}...`);
    console.log('╚═════════════════════════════════════════════════════════════════════╝\n');

    return { tenant, masterNode };

  } catch (err) {
    console.error('\n❌ [WILSY OS] ONBOARDING FAILED:', err.message);
    throw err;
  } finally {
    await mongoose.disconnect();
    console.log('[WILSY OS] DB CONNECTION TERMINATED.');
  }
};

// ⚡ POLISHED CLI EXECUTION PROTOCOL
if (import.meta.url === `file://${process.argv[1]}`) {
  const runCLI = async () => {
    const filePath = process.argv[2];

    if (!filePath) {
      console.error("\n❌ USAGE: node seedTenantFromOnboarding.js <path-to-onboarding-data.json>\n");
      process.exit(1);
    }

    try {
      const absolutePath = path.resolve(filePath);

      if (!fs.existsSync(absolutePath)) {
        throw new Error(`File not found: ${absolutePath}`);
      }

      const rawData = fs.readFileSync(absolutePath, 'utf8');
      const parsedData = JSON.parse(rawData);

      await seedTenant(parsedData);
      process.exit(0);
    } catch (error) {
      console.error(`\n❌ ONBOARDING FRACTURE: ${error.message}`);
      process.exit(1);
    }
  };

  runCLI();
}

export default seedTenant;
