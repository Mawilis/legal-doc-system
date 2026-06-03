/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN KEY FORGER [V35.0.1-OMEGA]                                                                                        ║
 * ║ [RECTIFIED: KEYOBJECT GENERATION FIX | UNIVERSAL RSA-SHA256 DECODER | BILLION DOLLAR SPEC]                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ PRODUCTION READY | EPITOME: NO CHILD'S PLACE | BIBLICAL WORTH BILLIONS                                                                 ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/forge_keys.js                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION COMMENTS:                                                                                                             ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Instituted permanent structural fix shifting to universal RSA-SHA256 verification. [2026-05-06] ║
 * ║ • AI Engineering (Grok) - Implemented robust multi-format (PEM + DER) generation and clean newline injection. [2026-05-06]             ║
 * ║ • AI Engineering (Gemini) - Rectified KeyObject generation sequence to properly support multi-format exports. [2026-05-06]             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import User from './models/userModel.js';
import crypto from 'crypto';
import fs from 'fs';
import chalk from 'chalk';
import dotenv from 'dotenv';

dotenv.config();
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';

async function forgePerfectKeys() {
  console.log(chalk.magenta('\n🚀 [FORGE-INIT] Generating Sovereign RSA 4096 Keypair...'));
  try {
    await mongoose.connect(MONGODB_URI);

    // RECTIFIED: Generate raw KeyObjects first (no inline encoding)
    const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
      modulusLength: 4096
    });

    // Export to PEM strings
    const publicPem = publicKey.export({ type: 'spki', format: 'pem' });
    const privatePem = privateKey.export({ type: 'pkcs8', format: 'pem' });

    // GROK FIX: Guaranteed clean PEM with real newlines
    const cleanPublic = publicPem.toString().trim();
    const cleanPrivate = privatePem.toString().trim();

    fs.writeFileSync('private.pem', cleanPrivate);
    fs.writeFileSync('public.pem', cleanPublic);

    // GROK FIX: Also store raw DER as backup (more robust)
    const publicDer = publicKey.export({ type: 'spki', format: 'der' });
    fs.writeFileSync('public.der', publicDer);

    console.log(chalk.cyan('🧬 Clean RSA 4096 keys forged (PEM + DER). Injecting Anchor into Nucleus...'));

    const user = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        $set: {
          'biometric.biometricAnchor': cleanPublic,
          'biometric.registered': true
        }
      },
      { returnDocument: 'after' }
    );

    if (!user) {
      console.error(chalk.red('❌ Identity not found in database.'));
      process.exit(1);
    }

    console.log(chalk.green('✅ NUCLEUS HEALED. Flawless PEM Anchor locked into database.'));
    process.exit(0);

  } catch (err) {
    console.error(chalk.red(`\n❌ [FORGE-FRACTURE] ${err.message}`));
    process.exit(1);
  }
}

forgePerfectKeys();
