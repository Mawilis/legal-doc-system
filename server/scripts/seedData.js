/*
 * File: server/scripts/seedData.js
 * STATUS: PRODUCTION-READY | MASTER ORCHESTRATOR | SINGLE-QUOTE ENFORCED
 */

'use strict';

const path = require('path');
// Load .env explicitly with single quotes
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const mongoose = require('mongoose');
const seedClients = require('../seed/seedClients');
const seedDocuments = require('../seed/seedDocuments');
const seedAudits = require('../seed/seedAudits');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';

// DEMO GUIDS
const DEMO_TENANT_ID = new mongoose.Types.ObjectId('650c1f1e1f1e1f1e1f1e1f1e');
const DEMO_USER_ID = new mongoose.Types.ObjectId('650c22222222222222222222');

async function runMasterSeed() {
    try {
        console.log('🏛️  [WILSY_OS]: Starting Master Hydration Sequence...');

        await mongoose.connect(MONGO_URI);
        console.log('✅ [DATABASE]: Connection established.');

        // 1. Clients
        const clientIds = await seedClients(DEMO_TENANT_ID);

        // 2. Documents (Linked)
        await seedDocuments(DEMO_TENANT_ID, clientIds);

        // 3. Audits (Forensic)
        await seedAudits(DEMO_TENANT_ID, DEMO_USER_ID);

        console.log('\n====================================================');
        console.log('🎉 SUCCESS: Wilsy OS Backend is Hydrated and Ready.');
        console.log(`🔑 Tenant Context: ${DEMO_TENANT_ID}`);
        console.log('====================================================');

    } catch (err) {
        console.error('\n💥 [CRITICAL_FAILURE]: Seed sequence aborted.');
        console.error(`Reason: ${err.message}`);
    } finally {
        await mongoose.connection.close();
        console.log('🔌 [DATABASE]: Connection drained. Exiting.');
        process.exit(0);
    }
}

runMasterSeed();