#!/usr/bin/env node
/* eslint-disable */
import mongoose from 'mongoose';
import crypto from 'node:crypto';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '../.env') });

import TenantBranding from '../models/TenantBranding.js';

const MONGO_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy_os';
const tenantId = (process.argv[2] && !process.argv[2].startsWith('--')) ? process.argv[2] : 'WILSY_GLOBAL_ROOT';
const jsonOutput = process.argv.includes('--json');

const colours = { reset: '\x1b[0m', green: '\x1b[32m', red: '\x1b[31m', yellow: '\x1b[33m', cyan: '\x1b[36m' };

const log = (msg, colour = 'reset') => {
  if (jsonOutput) return;
  console.log(`${colours[colour]}${msg}${colours.reset}`);
};

const recalculateHash = (bankDetails) => {
  if (!bankDetails) return '';
  const sensitiveString = `${bankDetails.accountNumber || ''}:${bankDetails.branchCode || ''}:${bankDetails.swift || ''}`;
  return crypto.createHash('sha3-512').update(sensitiveString).digest('hex');
};

const verifySeal = async () => {
  try {
    await mongoose.connect(MONGO_URI);
    const record = await TenantBranding.findOne({ tenantId }).lean();
    if (!record) {
      log(`❌ Tenant "${tenantId}" not found.`, 'red');
      process.exit(2);
    }
    const storedHash = record.documentHash || '';
    const recalculatedHash = recalculateHash(record.bankDetails);
    const isValid = storedHash === recalculatedHash;
    if (jsonOutput) {
      console.log(JSON.stringify({ tenantId: record.tenantId, verified: isValid, storedHash, recalculatedHash }, null, 2));
    } else {
      log(`\n📋 Tenant: ${record.tenantId}`, 'cyan');
      log(`🔐 Stored Hash: ${storedHash}`, 'yellow');
      if (isValid) log('\n✅ SEAL VERIFIED', 'green');
      else log('\n❌ SEAL BROKEN', 'red');
    }
    process.exit(isValid ? 0 : 1);
  } catch (err) {
    log(`❌ Error: ${err.message}`, 'red');
    process.exit(2);
  } finally {
    await mongoose.disconnect();
  }
};
verifySeal();
