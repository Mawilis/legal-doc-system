/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SINGULARITY SYNC SHARD [V1.0.0-OMEGA]                                                                                       ║
 * ║ [PROTOCOL: ZERO-FRACTURE DATABASE ALIGNMENT | BIBLICAL WORTH BILLIONS | PRODUCTION READY]                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import fs from 'fs';
import qrcode from 'qrcode';
import speakeasy from 'speakeasy';
import dotenv from 'dotenv';

dotenv.config();
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function synchronize() {
  try {
    await mongoose.connect(MONGODB_URI);
    const anchor = fs.readFileSync('public.pem', 'utf8').trim();
    const secret = speakeasy.generateSecret({ name: `WilsyOS:wilsonkhanyezi@gmail.com` });

    const user = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        'biometric.biometricAnchor': anchor,
        'biometric.registered': true,
        'securityMetadata.mfaSecret': secret.base32,
        'securityMetadata.mfaEnabled': true,
        'isTwoFactorEnabled': true
      },
      { returnDocument: 'after' }
    );

    if (user) {
      console.log('✅ NUCLEUS ANCHORS CLEANSED AND SYNCHRONIZED');
      qrcode.toString(secret.otpauth_url, { type: 'terminal', small: true }, (err, qr) => {
        console.log('\n🚀 SCAN THIS NEW QR CODE (DELETE ALL PREVIOUS ENTRIES ON PHONE):');
        console.log(qr);
        process.exit(0);
      });
    }
  } catch (err) {
    console.error('❌ SYNC FRACTURE:', err.message);
    process.exit(1);
  }
}
synchronize();
