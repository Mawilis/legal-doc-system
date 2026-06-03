/* eslint-disable */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import qrcode from 'qrcode';
import dotenv from 'dotenv';
import speakeasy from 'speakeasy';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function hardReset() {
  try {
    await mongoose.connect(MONGODB_URI);

    // 1. Generate a Fresh Genesis Secret
    const secret = speakeasy.generateSecret({ name: `WilsyOS:wilsonkhanyezi@gmail.com` });

    // 2. Surgical DB Update
    const user = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        'securityMetadata.mfaSecret': secret.base32,
        'securityMetadata.mfaEnabled': true,
        'isTwoFactorEnabled': true,
        'biometric.registered': true
      },
      { returnDocument: 'after' }
    );

    if (!user) throw new Error('Identity not found in Nucleus');

    console.log('\n✅ DB ANCHOR UPDATED WITH FRESH SECRET');

    // 3. Manifest the New QR Shard
    qrcode.toString(secret.otpauth_url, { type: 'terminal', small: true }, (err, terminalQR) => {
      console.log('\n🚀 SCAN THIS NEW QR CODE (DELETE ALL OLD ENTRIES FIRST):');
      console.log(terminalQR);
      console.log('\n🛰️  MANUAL SECRET (IF SCAN FAILS): ' + secret.base32);
      process.exit(0);
    });
  } catch (err) {
    console.error('❌ RESET FRACTURE:', err.message);
    process.exit(1);
  }
}

hardReset();
