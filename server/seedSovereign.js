/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY IGNITION SCRIPT [V4 OMEGA]                                                                               ║
 * ║ [SCHEMA-ALIGNED UPSERT | HOOK BYPASS | INTERNAL HANDSHAKE VERIFICATION]                                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { User } from './models/userModel.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

const igniteIdentity = async () => {
  try {
    const dbUri = process.env.MONGO_URI || process.env.MONGODB_URI || process.env.DATABASE_URL;
    if (!dbUri) throw new Error("CRITICAL: No Database URI found in .env file.");

    console.log('🚀 [IGNITION] Connecting to Sovereign Ledger...');
    await mongoose.connect(dbUri);
    console.log('✅ [IGNITION] Quantum Link Established.');

    const targetEmail = 'wilsonkhanyezi@gmail.com';
    const targetTenant = '69dd419f39c41a1b067fc048';
    const targetPassword = 'WilsyMasterPassword2026!';

    // 1. 🧬 DYNAMIC ENCRYPTION
    let bcryptMod;
    try { bcryptMod = await import('bcrypt'); }
    catch { bcryptMod = await import('bcryptjs'); }
    const hashFn = bcryptMod.hash || bcryptMod.default.hash;
    const hashedPassword = await hashFn(targetPassword, 10);

    // 2. 🚀 SCHEMA-ALIGNED UPSERT
    // We use Mongoose's updateOne. This perfectly casts the tenantId to an ObjectId
    // if your schema requires it, but strictly bypasses the broken pre('save') hooks.
    await User.updateOne(
      { email: targetEmail },
      {
        $set: {
          firstName: 'Wilson',
          lastName: 'Khanyezi',
          password: hashedPassword,
          tenantId: targetTenant,
          role: 'founder',
          'securityMetadata.mfaEnabled': false,
          'securityMetadata.failedAttempts': 0,
          status: 'ACTIVE'
        }
      },
      { upsert: true, runValidators: false }
    );

    console.log(`🧹 [IGNITION] Identity anchored with perfect schema alignment.`);

    // 3. 🔬 FORENSIC SELF-TEST
    // We simulate the exact database query your authController runs.
    console.log(`🔬 [IGNITION] Running Internal Handshake Simulation...`);
    const testUser = await User.findOne({
      email: targetEmail,
      tenantId: targetTenant
    }).select('+password');

    if (!testUser) {
      throw new Error("Self-Test Failed: Could not locate user. Schema casing mismatch fatal.");
    }

    const isMatch = await testUser.comparePassword(targetPassword);
    if (!isMatch) {
      throw new Error("Self-Test Failed: Cryptographic hash verification failed.");
    }

    console.log('👑 [IGNITION] SUPREME ARCHITECT IDENTITY FORGED & VERIFIED.');
    console.log('--------------------------------------------------');
    console.log(`EMAIL:    ${targetEmail}`);
    console.log(`PASSWORD: ${targetPassword}`);
    console.log(`TENANT:   ${targetTenant}`);
    console.log(`STATUS:   SELF-TEST PASSED ✅ (10/10 READY FOR LOGIN)`);
    console.log('--------------------------------------------------');

    process.exit(0);
  } catch (error) {
    console.error('🚨 [IGNITION FAULT]', error.message || error);
    process.exit(1);
  }
};

igniteIdentity();
