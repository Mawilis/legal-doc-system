/* eslint-disable */
/*
 * WILSY OS - Audit Chain Verifier
 *
 * Usage: node scripts/verify-audit-chains.js
 */

import mongoose from "mongoose";
import ValidationAudit from '../models/ValidationAudit.js.js';
import TenantConfig from '../models/TenantConfig.js.js';
import dotenv from 'dotenv.js';

dotenv.config();

const log = {
  info: (...args) => console.log(...args),
  error: (...args) => console.error(...args),
};

async function verifyAllChains() {
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy');
    log.info('📊 Connected to database');

    const tenants = await TenantConfig.find({ status: 'ACTIVE' }).select('tenantId name');
    log.info(`\n🔍 Found ${tenants.length} active tenants`);

    let verified = 0;
    let tampered = 0;
    let totalEntries = 0;

    for (const tenant of tenants) {
      process.stdout.write(`\n  Verifying ${tenant.name}... `);
      const result = await ValidationAudit.verifyChain(tenant.tenantId);

      totalEntries += result.entryCount;

      if (result.verified) {
        verified++;
        log.info(`✅ (${result.entryCount} entries)`);
      } else {
        tampered++;
        log.error(`❌ TAMPERED (${result.brokenLinks.length} broken links)`);
      }
    }

    log.info('\n' + '='.repeat(50));
    log.info('📊 VERIFICATION SUMMARY');
    log.info('='.repeat(50));
    log.info(`✅ Verified: ${verified}`);
    log.info(`❌ Tampered: ${tampered}`);
    log.info(`📝 Total Entries: ${totalEntries}`);
    log.info(`📊 Total Tenants: ${tenants.length}`);
    log.info('='.repeat(50) + '\n');

    await mongoose.disconnect();
    process.exit(tampered > 0 ? 1 : 0);
  } catch (error) {
    log.error('❌ Error:', error.message);
    process.exit(1);
  }
}

verifyAllChains();
