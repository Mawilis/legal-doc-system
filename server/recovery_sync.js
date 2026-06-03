/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MFA RE-SYNC PROTOCOL [V1.0.0-OMEGA]                                                                                         ║
 * ║ [PROTOCOL: SECRET EXTRACTION & QR REGEN | BIBLICAL WORTH BILLIONS | PRODUCTION READY]                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import qrcode from 'qrcode';
import dotenv from 'dotenv';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function sync() {
  try {
    await mongoose.connect(MONGODB_URI);
    const user = await User.findOne({ email: 'wilsonkhanyezi@gmail.com' }).select('+securityMetadata.mfaSecret');

    if (!user || !user.securityMetadata.mfaSecret) {
      console.error('❌ NO SECRET FOUND. RUN LOGIN FIRST TO GENERATE ONE.');
      process.exit(1);
    }

    console.log(`✅ SECRET FOUND: ${user.securityMetadata.mfaSecret}`);

    // Generate the URL for manual entry or QR scanning
    const otpauth_url = `otpauth://totp/WilsyOS:wilsonkhanyezi@gmail.com?secret=${user.securityMetadata.mfaSecret}&issuer=WilsyOS`;

    console.log('\n🛰️  MANUAL SECRET FOR AUTHENTICATOR APP:');
    console.log('========================================');
    console.log(user.securityMetadata.mfaSecret);
    console.log('========================================');

    qrcode.toString(otpauth_url, { type: 'terminal' }, (err, url) => {
      console.log('\n🚀 SCAN THIS NEW QR CODE TO RE-SYNC:');
      console.log(url);
      process.exit(0);
    });
  } catch (err) {
    console.error('❌ SYNC FAILED:', err.message);
    process.exit(1);
  }
}

sync();
