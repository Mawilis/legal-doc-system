/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ELEVATE TO FOUNDER STATUS [V1.0.0-MARS-OMEGA]                                                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-MARS | PRODUCTION READY                                                                                                ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/elevateFounder.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated ultimate boardroom clearance.                                                       ║
 * ║ • AI Engineering (DeepSeek) - CREATED: Script to elevate user to FOUNDER role and reset MFA state.                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @module elevateFounder
 * @description Elevates the specified user to FOUNDER role and resets MFA setup flag,
 *              granting full boardroom access and forcing a fresh MFA handshake.
 *
 * @real-world Resolves 403 Forbidden errors on boardroom dashboards caused by insufficient privileges.
 * @forensic Logs elevation action; can be extended to record in forensic ledger.
 *
 * @example
 * node scripts/elevateFounder.js
 */

import mongoose from 'mongoose';
import { UserSchema } from '../models/userModel.js';

async function elevate() {
  try {
    await mongoose.connect('mongodb://127.0.0.1:27017/wilsy');
    console.log('🔗 Connection Established to wilsy shard.');

    const UserModel = mongoose.model('User', UserSchema);
    const user = await UserModel.findOne({ email: 'wilsonkhanyezi@gmail.com' });

    if (!user) {
      console.error('❌ Identity not found in wilsy shard!');
      process.exit(1);
    }

    // Grant ultimate boardroom clearance
    user.role = 'FOUNDER';
    // Reset MFA to ensure a clean handshake
    user.securityMetadata.mfaSetupComplete = false;

    await user.save();
    console.log('✅ Identity elevated to FOUNDER status. Boardroom clearance granted.');
    console.log('🔐 Please clear your browser storage (Application → Clear site data) and log in again.');

    await mongoose.disconnect();
    process.exit(0);
  } catch (error) {
    console.error('❌ Elevation failed:', error.message);
    process.exit(1);
  }
}

elevate();
