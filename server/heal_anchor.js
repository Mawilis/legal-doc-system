/* eslint-disable */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import crypto from 'crypto';
import fs from 'fs';
import chalk from 'chalk';
import dotenv from 'dotenv';

dotenv.config();
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function healSovereignAnchor() {
  console.log(chalk.magenta('\n🚀 [HEAL-INIT] Deriving Public Key from Private Key...'));
  try {
    await mongoose.connect(MONGODB_URI);

    // 1. Read the exact private key used for the strike
    const privateKeyPem = fs.readFileSync('private.pem', 'utf8');

    // 2. Mathematically derive the flawless SPKI public key
    const privateKeyObj = crypto.createPrivateKey(privateKeyPem);
    const publicKeyObj = crypto.createPublicKey(privateKeyObj); // 🛡️ THE MISSING LINK
    const perfectPublicKey = publicKeyObj.export({ type: 'spki', format: 'pem' });

    console.log(chalk.cyan('🧬 Flawless SPKI Anchor Derived.'));

    // 3. Inject directly into the Sovereign Database
    const user = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        $set: {
          'biometric.biometricAnchor': perfectPublicKey,
          'biometric.registered': true
        }
      },
      { new: true }
    );

    if (!user) {
      console.error(chalk.red('❌ Identity not found in database.'));
      process.exit(1);
    }

    console.log(chalk.green('✅ NUCLEUS HEALED. Anchor perfectly synchronized with private key.'));
    console.log(chalk.yellow('\n🔥 GATEWAY IS OPEN. FIRE THE STRIKE NOW: node verify_strike.js\n'));
    process.exit(0);

  } catch (err) {
    console.error(chalk.red(`\n❌ [HEAL-FRACTURE] ${err.message}`));
    process.exit(1);
  }
}

healSovereignAnchor();
