/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - INFRASTRUCTURE PURIFICATION [SLUG INDEX REMOVAL]                                    #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/fix/dropLegacySlugIndex.js  #
 * ####################################################################################################
 * # VERSION: 1.0.1-SINGULARITY                                                                       #
 * # EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                              #
 * ####################################################################################################
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '../../.env') });

const purify = async () => {
  try {
    console.log('🚀 WILSY OS - Purifying Database Indices...');
    await mongoose.connect(process.env.MONGODB_URI);

    const collection = mongoose.connection.collection('tenants');

    // Drop the legacy slug index that is blocking multi-tenancy
    console.log('🛡️  Dropping legacy index: slug_1...');
    await collection.dropIndex('slug_1').catch(e => console.log('ℹ️  slug_1 index already cleared.'));

    // Purge any partial retail records to allow a clean restart
    await collection.deleteMany({ name: 'Khanyezi Fish & Chips Global' });

    console.log('✅ DATABASE PURIFIED - Ready for Multi-Sector Genesis.');
    process.exit(0);
  } catch (err) {
    console.error('❌ Purification Failure:', err.message);
    process.exit(1);
  }
};

purify();
