/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - FORENSIC INDEX CLEANER                                                               #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/fix/dropLegacyIndices.js    #
 * ####################################################################################################
 * # VERSION: 1.0.0-SINGULARITY                                                                       #
 * # EPITOME: BIBLICAL WORTH BILLIONS | INFRASTRUCTURE PURIFICATION                                   #
 * ####################################################################################################
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '../../.env') });

const dropIndices = async () => {
  try {
    console.log('🚀 WILSY OS - Initiating Infrastructure Purification...');
    await mongoose.connect(process.env.MONGODB_URI);

    const collection = mongoose.connection.collection('tenants');

    // Drop the specific troublesome index
    console.log('🛡️  Dropping legacy index: domain_1...');
    await collection.dropIndex('domain_1').catch(e => console.log('ℹ️  domain_1 index already cleared.'));

    // Purge any existing failed/null tenants to ensure a clean Genesis
    console.log('🧹 Purging corrupted tenant data...');
    await collection.deleteMany({ name: 'Khanyezi Global Jurisprudence' });

    console.log('✅ DATABASE PURIFIED - Ready for Genesis.');
    process.exit(0);
  } catch (err) {
    console.error('❌ Purification Failure:', err.message);
    process.exit(1);
  }
};

dropIndices();
