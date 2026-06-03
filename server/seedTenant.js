/* eslint-disable */
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import TenantConfig from './models/TenantConfig.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

const igniteTenant = async () => {
  try {
    const dbUri = process.env.MONGO_URI || process.env.MONGODB_URI || process.env.DATABASE_URL;
    if (!dbUri) throw new Error("CRITICAL: No Database URI found in .env file.");

    console.log('🚀 [IGNITION] Connecting to Sovereign Ledger...');
    await mongoose.connect(dbUri);
    console.log('✅ [IGNITION] Quantum Link Established.');

    const targetTenant = '69dd419f39c41a1b067fc048'; // Your exact Tenant ID

    await TenantConfig.updateOne(
      { _id: targetTenant },
      {
        $set: {
          tenantId: targetTenant,
          name: 'Wilsy OS',
          slug: 'wilsy',
          alias: 'wilsy',
          legalEntityName: 'Wilsy (Pty) Ltd',
          registrationNumber: '2024/123456/07',
          businessType: 'CORPORATE',
          tier: 'ENTERPRISE',
          status: 'ACTIVE',
          branding: { primaryColor: '#D4AF37', theme: 'dark' },
          settings: { enforceMFA: false, retentionYears: 100 },
          features: ['QUANTUM_SECURITY', 'FORENSIC_AUDIT']
        }
      },
      { upsert: true, runValidators: false }
    );

    console.log('👑 [IGNITION] MASTER TENANT CITADEL FORGED.');
    console.log(`SLUG: wilsy -> RESOLVES TO: ${targetTenant}`);

    process.exit(0);
  } catch (error) {
    console.error('🚨 [IGNITION FAULT]', error.message || error);
    process.exit(1);
  }
};

igniteTenant();
