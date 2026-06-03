/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MASTER NODE ANCHOR SCRIPT [V40.1.0-SINGULARITY-FINALITY]                                                                    ║
 * ║ [UNIVERSAL MASTER SHARDING | CIPC LEGAL FINALITY | SHA3-512 SEAL | AUTH-READY]                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 40.1.0 | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/seedMasterNode.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated absolute legal fidelity and multi-shard identity alignment. [2026-05-12]              ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Multi-identity loops implemented to resolve 401 "Unanchored" fractures in OS logs.               ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Full V40 Universal Tenant Model field coverage for institutional finality.                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import Node from '../models/nodeModel.js';
import TenantConfig, { BUSINESS_TYPES, LEGAL_STATUSES } from '../models/TenantConfig.js';

// 🛡️ SOVEREIGN PATH RESOLUTION
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const envPath = path.resolve(__dirname, '../../.env');
dotenv.config({ path: envPath });

const seedSingularity = async () => {
  try {
    console.log('🏛️  WILSY OS SINGULARITY INITIATED...');

    if (!process.env.MONGODB_URI) {
      throw new Error(`MONGODB_URI missing. Check ${envPath}`);
    }

    await mongoose.connect(process.env.MONGODB_URI);
    console.log('📡 [SEEDER] Connected to Sovereign Database Shard.');

    // =========================================================================
    //  🏛️ MASTER IDENTITY SHARDS (Resolves all 401 fractures in OS logs)
    // =========================================================================
    const masterIds = ['WILSY_ROOT', 'MASTER', 'WILSY_MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT'];

    // Official Corporate Data
    const legalName = 'Wilsy (Pty) Ltd';
    const registrationNumber = '2024/617944/07';
    const taxNumber = '9395759229';
    const directorName = 'WILSON KHANYEZI';
    const directorID = '8811045971084';
    const fullAddress = 'UNIT 29 SUMATRA ESTATE CNR 8TH RD AND 7TH RD NOORDWYK MIDRAND GAUTENG 1682';

    for (const tenantId of masterIds) {
      console.log(`\n🏗️  Anchoring Identity: ${tenantId}...`);

      // 🧹 PURGE PHASE: Specific identity cleanup
      await TenantConfig.deleteOne({ tenantId });
      await Node.deleteMany({ tenantId });

      // 🏗️ STEP 1: SEED TENANT CONFIG (UNIVERSAL V40 MODEL)
      const tenant = new TenantConfig({
        tenantId,
        shardId: 'SHARD_01_RSA',
        name: legalName,
        businessType: 'Sovereign Institution', // Matching V40 Rectification
        legalName: legalName,
        tradingName: 'WILSY OS',
        registrationNumber: registrationNumber,
        taxNumber: taxNumber,
        incorporationDate: new Date('2024-10-02'),
        businessStartDate: new Date('2024-10-02'),
        financialYearEnd: 'February',
        legalStatus: 'In Business',
        contactEmail: 'wilson@wilsy.os',
        tier: 'SOVEREIGN',
        status: 'ACTIVE',
        addresses: {
          registered: fullAddress,
          physical: fullAddress
        },
        owners: [{
          name: directorName,
          idNumber: directorID,
          shareholding: 100,
          role: 'DIRECTOR',
          appointmentDate: new Date('2024-10-02')
        }],
        compliance: {
          POPIA: 'SECURE',
          SARS: 'VERIFIED',
          CIPC: 'REGISTERED',
          dataProtectionOfficer: {
            name: directorName,
            email: 'wilson@wilsy.os'
          }
        },
        branding: {
          primaryColor: '#D4AF37',
          secondaryColor: '#000000'
        }
      });
      await tenant.save();

      // 🏗️ STEP 2: SEED MASTER NODE (Linked by TenantId)
      const masterNode = new Node({
        tenantId,
        entity: 'WILSY ROOT',
        region: 'ZAF-GP-MIDRAND',
        type: 'MASTER_NODE',
        isMasterAnchor: true,
        status: 'ONLINE',
        lat: -25.9999,
        lng: 28.1283,
        lastLatency: 0.01,
        neuralStability: 100.00,
        forensicChain: [
          {
            action: 'GENESIS_ANCHOR',
            performer: directorName,
            hash: 'ORIGIN_STRIKE_FINALITY',
            stabilityDelta: 100,
            timestamp: new Date().toISOString()
          }
        ],
        dilithiumSignature: `ML-DSA-5::${crypto.randomBytes(32).toString('hex').toUpperCase()}`,
        metadata: {
          registrationDate: new Date('2024-10-02'),
          businessStartDate: new Date('2024-10-02'),
          corporateStatus: 'In Business',
          directorID,
          legalAddress: fullAddress
        }
      });

      // Deterministic SHA3-512 Seal
      const sealPayload = JSON.stringify({
        id: masterNode._id,
        tenantId,
        reg: registrationNumber,
        tax: taxNumber,
        director: directorID
      });
      masterNode.nodeSeal = crypto.createHash('sha3-512').update(sealPayload).digest('hex');

      await masterNode.save();
      console.log(`✅ Shard Secured: [${tenantId}] Seal: ${masterNode.nodeSeal.substring(0, 16)}...`);
    }

    console.log('\n🏛️  WILSY OS SINGULARITY SECURELY ANCHORED ACROSS ALL MASTER SHARDS.');
    await mongoose.disconnect();
    process.exit(0);
  } catch (err) {
    console.error('💥 [SINGULARITY_FRACTURE]:', err.message);
    if (mongoose.connection.readyState === 1) await mongoose.disconnect();
    process.exit(1);
  }
};

seedSingularity();
