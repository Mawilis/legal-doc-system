/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC HANDSHAKE DIAGNOSTIC [V1.0.0]                                                                                      ║
 * ║ [PROTOCOL: OTP-EXPECTATION-CHECK | BILLION DOLLAR SPEC]                                                                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import speakeasy from 'speakeasy';
import dotenv from 'dotenv';

dotenv.config();
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function diagnose() {
  try {
    await mongoose.connect(MONGODB_URI);
    const user = await User.findOne({ email: 'wilsonkhanyezi@gmail.com' }).select('+securityMetadata.mfaSecret');

    if (!user || !user.securityMetadata.mfaSecret) {
      console.error('❌ NO SECRET FOUND IN NUCLEUS');
      process.exit(1);
    }

    const serverOTP = speakeasy.totp({
      secret: user.securityMetadata.mfaSecret,
      encoding: 'base32'
    });

    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log(`║ 🛰️  SERVER EXPECTED OTP: ${serverOTP}                      ║`);
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log('║ Check your phone. If it matches, the secret is synced.     ║');
    console.log('║ If it DOES NOT match, you MUST run singularity_sync.js.    ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');
    process.exit(0);
  } catch (err) {
    console.error('❌ DIAGNOSTIC FAILED:', err.message);
    process.exit(1);
  }
}
diagnose();
