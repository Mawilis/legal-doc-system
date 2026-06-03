/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MFA RE-SYNC & QR MANIFEST [V1.0.0-SINGULARITY]                                                                              ║
 * ║ [PROTOCOL: SECRET EXTRACTION | TERMINAL QR RENDERING | BIBLICAL WORTH BILLIONS]                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import qrcode from 'qrcode';
import dotenv from 'dotenv';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function manifestQR() {
  try {
    await mongoose.connect(MONGODB_URI);
    const user = await User.findOne({ email: 'wilsonkhanyezi@gmail.com' }).select('+securityMetadata.mfaSecret');

    if (!user || !user.securityMetadata.mfaSecret) {
      console.error('❌ NO SECRET ANCHORED. Strike /api/auth/login first to generate a genesis secret.');
      process.exit(1);
    }

    const secret = user.securityMetadata.mfaSecret;
    const otpauth_url = `otpauth://totp/WilsyOS:wilsonkhanyezi@gmail.com?secret=${secret}&issuer=WilsyOS`;

    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║ 🛰️  SOVEREIGN MFA SECRET: ' + secret);
    console.log('╚════════════════════════════════════════════════════════════╝');

    qrcode.toString(otpauth_url, { type: 'terminal', small: true }, (err, terminalQR) => {
      if (err) throw err;
      console.log('\n🚀 SCAN THIS WITH YOUR AUTHENTICATOR APP:');
      console.log(terminalQR);
      console.log('\n✅ Once scanned, use the 6-digit code in verify_strike.js');
      process.exit(0);
    });
  } catch (err) {
    console.error('❌ MANIFEST FRACTURE:', err.message);
    process.exit(1);
  }
}

manifestQR();
