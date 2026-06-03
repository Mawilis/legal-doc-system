/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DIRECT FILE ANCHOR SEED [V1.1.0-SINGULARITY]                                                                                ║
 * ║ [PROTOCOL: DIRECT-FS-READ | ZERO-CORRUPTION SEED | BILLION DOLLAR SPEC]                                                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function seed() {
  try {
    await mongoose.connect(MONGODB_URI);

    // 🛡️ Reading directly from the uncorrupted file on your disk
    const PUBLIC_KEY = fs.readFileSync('public.pem', 'utf8').trim();
    console.log('✅ PUBLIC KEY READ FROM DISK');

    const user = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        'biometric.biometricAnchor': PUBLIC_KEY,
        'biometric.registered': true,
        'isTwoFactorEnabled': true
      },
      { returnDocument: 'after' }
    );

    if (user) {
      console.log('✅ SOVEREIGN ANCHOR RE-SEEDED DIRECTLY FROM FILE');
      process.exit(0);
    } else {
      console.error('❌ IDENTITY NOT FOUND');
      process.exit(1);
    }
  } catch (err) {
    console.error('❌ DB STRIKE FAILED:', err.message);
    process.exit(1);
  }
}

seed();
