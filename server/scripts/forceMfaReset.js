/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORCED MFA GENESIS RESET [V1.0.0-MARS-OMEGA]                                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-MARS | PRODUCTION READY                                                                                                ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/forceMfaReset.js                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated forced MFA reset to recover QR code flow.                                          ║
 * ║ • AI Engineering (DeepSeek) - CREATED: One‑time script to clear MFA flags, forcing fresh MFA setup.                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @module forceMfaReset
 * @description Resets the MFA state of the founder user, clearing the `mfaSetupComplete`
 *              flag and the stored secret. After running this script, the login flow
 *              will present a new QR code for MFA setup instead of asking for a token.
 *
 * @real-world Fixes login issues where the system incorrectly believes MFA is fully
 *             configured (due to seeding or testing) and demands a code that doesn't exist.
 * @forensic Logs the reset action; can be extended to record in forensic ledger.
 *
 * @example
 * node scripts/forceMfaReset.js
 */

import mongoose from 'mongoose';
import { UserSchema } from '../models/userModel.js';

async function reset() {
  try {
    const conn = await mongoose.connect('mongodb://127.0.0.1:27017/wilsy');
    const UserModel = conn.model('User', UserSchema);

    const user = await UserModel.findOne({ email: 'wilsonkhanyezi@gmail.com' });
    if (!user) {
      console.error('❌ User not found!');
      process.exit(1);
    }

    // Wipe the existing MFA state to force the QR code flow
    user.securityMetadata.mfaSetupComplete = false;
    user.securityMetadata.mfaSecret = null;
    user.securityMetadata.mfaEnabled = false;
    user.isTwoFactorEnabled = false;

    await user.save();
    console.log('✅ MFA state reset to [DISABLED]. You will now be forced into the QR code setup flow.');
    await mongoose.disconnect();
    process.exit(0);
  } catch (error) {
    console.error('❌ Reset failed:', error.message);
    process.exit(1);
  }
}

reset();
