/* eslint-disable */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import speakeasy from 'speakeasy';
import qrcode from 'qrcode';
import dotenv from 'dotenv';
import chalk from 'chalk';

dotenv.config();
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function generateFreshQR() {
  console.log(chalk.magenta('\n🚀 [QR-INIT] Forging Fresh Sovereign MFA Secret...'));
  try {
    await mongoose.connect(MONGODB_URI);

    const user = await User.findOne({ email: 'wilsonkhanyezi@gmail.com' });
    if (!user) {
      console.error(chalk.red('❌ Identity not found.'));
      process.exit(1);
    }

    // 1. Generate new cryptographically secure secret
    const secret = speakeasy.generateSecret({ name: `WilsyOS:${user.email}` });

    // 2. Lock the new secret into the Nucleus (Preserving the biometric anchor we just healed)
    user.securityMetadata.mfaSecret = secret.base32;
    await user.save();

    console.log(chalk.cyan(`\n🔐 NEW MFA SECRET (Base32): ${secret.base32}\n`));

    // 3. Render the QR code straight to the terminal console
    qrcode.toString(secret.otpauth_url, { type: 'terminal', small: true }, function (err, url) {
      if (err) throw err;
      console.log(url);
      console.log(chalk.green('✅ NUCLEUS UPDATED. SCAN THIS QR CODE WITH YOUR AUTHENTICATOR APP.'));
      console.log(chalk.yellow('🔥 THEN FIRE THE STRIKE WITH THE NEW OTP: node verify_strike.js\n'));
      process.exit(0);
    });

  } catch (err) {
    console.error(chalk.red(`\n❌ [QR-FRACTURE] ${err.message}`));
    process.exit(1);
  }
}

generateFreshQR();
