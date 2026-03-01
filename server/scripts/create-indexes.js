#!/usr/bin/env node/usr/bin/env node

/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DATABASE INDEX CREATION SCRIPT                                 ║
 * ║ Creates optimized indexes for all collections to ensure peak performance  ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../.env') });

// MongoDB connection URI
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal_doc_system';

// Collection and index definitions
const INDEXES = {
  // Deal collection indexes
  deals: [
    { key: { tenantId: 1, stage: 1, createdAt: -1 }, name: 'tenant_stage_time' },
    { key: { tenantId: 1, value: -1 }, name: 'tenant_value' },
    { key: { tenantId: 1, dealType: 1 }, name: 'tenant_deal_type' },
    { key: { tenantId: 1, materiality: 1 }, name: 'tenant_materiality' },
    { key: { 'timeline.dropDeadDate': 1 }, name: 'drop_dead_date', sparse: true },
    { key: { forensicHash: 1 }, name: 'forensic_hash', unique: true },
    { key: { retentionEnd: 1 }, name: 'retention_end', expireAfterSeconds: 0 },
  ],

  // Target collection indexes
  targets: [
    { key: { tenantId: 1, status: 1 }, name: 'tenant_status' },
    { key: { tenantId: 1, industry: 1 }, name: 'tenant_industry' },
    { key: { tenantId: 1, 'financials.revenue.current': -1 }, name: 'tenant_revenue' },
    { key: { registrationNumber: 1 }, name: 'reg_number', unique: true },
    { key: { 'synergyScores.score': -1 }, name: 'synergy_scores', sparse: true },
    { key: { forensicHash: 1 }, name: 'forensic_hash', unique: true },
    { key: { retentionEnd: 1 }, name: 'retention_end', expireAfterSeconds: 0 },
  ],

  // SynergyScore collection indexes
  synergyScores: [
    {
      key: { tenantId: 1, acquirerId: 1, targetId: 1 },
      name: 'tenant_acquirer_target',
      unique: true,
    },
    { key: { tenantId: 1, totalSynergy: -1 }, name: 'tenant_synergy' },
    { key: { dealId: 1 }, name: 'deal_id', sparse: true },
    { key: { calculatedAt: -1 }, name: 'calculated_at' },
    { key: { forensicHash: 1 }, name: 'forensic_hash', unique: true },
    { key: { retentionEnd: 1 }, name: 'retention_end', expireAfterSeconds: 0 },
  ],

  // RegulatoryFiling collection indexes
  regulatoryFilings: [
    { key: { tenantId: 1, jurisdiction: 1, status: 1 }, name: 'tenant_jurisdiction_status' },
    { key: { tenantId: 1, dealId: 1 }, name: 'tenant_deal' },
    { key: { 'review.targetDecisionDate': 1 }, name: 'decision_date', sparse: true },
    { key: { 'filing.submissionDate': -1 }, name: 'submission_date' },
    { key: { forensicHash: 1 }, name: 'forensic_hash', unique: true },
    { key: { retentionEnd: 1 }, name: 'retention_end', expireAfterSeconds: 0 },
  ],

  // IntegrationSimulation collection indexes
  integrationSimulations: [
    { key: { tenantId: 1, dealId: 1 }, name: 'tenant_deal', unique: true },
    { key: { 'results.successProbability.overall': -1 }, name: 'success_probability' },
    { key: { generatedAt: -1 }, name: 'generated_at' },
    { key: { forensicHash: 1 }, name: 'forensic_hash', unique: true },
    { key: { retentionEnd: 1 }, name: 'retention_end', expireAfterSeconds: 0 },
  ],

  // Case collection indexes
  cases: [
    { key: { tenantId: 1, status: 1 }, name: 'tenant_status' },
    { key: { tenantId: 1, court: 1 }, name: 'tenant_court' },
    { key: { caseNumber: 1 }, name: 'case_number', unique: true },
    { key: { 'paiaRequests.status': 1 }, name: 'paia_status', sparse: true },
    { key: { forensicHash: 1 }, name: 'forensic_hash', unique: true },
  ],

  // Tenant collection indexes
  tenants: [
    { key: { tenantId: 1 }, name: 'tenant_id', unique: true },
    { key: { status: 1 }, name: 'status' },
    { key: { 'subscription.plan': 1 }, name: 'subscription_plan' },
  ],

  // User collection indexes
  users: [
    { key: { tenantId: 1, email: 1 }, name: 'tenant_email', unique: true },
    { key: { tenantId: 1, role: 1 }, name: 'tenant_role' },
    { key: { lastLogin: -1 }, name: 'last_login', sparse: true },
  ],

  // AuditLog collection indexes
  auditlogs: [
    { key: { tenantId: 1, timestamp: -1 }, name: 'tenant_time' },
    { key: { tenantId: 1, action: 1 }, name: 'tenant_action' },
    { key: { tenantId: 1, userId: 1 }, name: 'tenant_user' },
    { key: { retentionEnd: 1 }, name: 'retention_end', expireAfterSeconds: 0 },
  ],
};

async function createIndexes() {
  console.log('🔧 WILSY OS - Database Index Creation Tool');
  console.log('==========================================\n');

  try {
    // Connect to MongoDB
    console.log(`📡 Connecting to MongoDB: ${MONGODB_URI.replace(/:[^:]*@/, ':***@')}`);
    await mongoose.connect(MONGODB_URI);
    console.log('✅ Connected to MongoDB\n');

    const db = mongoose.connection.db;
    const collections = await db.listCollections().toArray();
    const collectionNames = collections.map((c) => c.name);

    let totalIndexes = 0;
    let createdIndexes = 0;
    let skippedIndexes = 0;

    // Create indexes for each collection
    for (const [collectionName, indexes] of Object.entries(INDEXES)) {
      console.log(`\n📁 Processing collection: ${collectionName}`);

      if (!collectionNames.includes(collectionName)) {
        console.log(
          `   ⚠️  Collection does not exist yet - will be created when first document inserted`
        );
        skippedIndexes += indexes.length;
        continue;
      }

      const collection = db.collection(collectionName);

      for (const indexSpec of indexes) {
        totalIndexes++;
        try {
          // Check if index already exists
          const existingIndexes = await collection.indexExists(indexSpec.name);

          if (existingIndexes) {
            console.log(`   ⏭️  Index already exists: ${indexSpec.name}`);
            skippedIndexes++;
          } else {
            // Create the index
            await collection.createIndex(indexSpec.key, {
              name: indexSpec.name,
              unique: indexSpec.unique || false,
              sparse: indexSpec.sparse || false,
              expireAfterSeconds: indexSpec.expireAfterSeconds,
            });
            console.log(`   ✅ Created index: ${indexSpec.name}`);
            createdIndexes++;
          }
        } catch (error) {
          console.error(`   ❌ Failed to create index ${indexSpec.name}:`, error.message);
        }
      }
    }

    console.log('\n📊 Index Creation Summary:');
    console.log('==========================================');
    console.log(`Total indexes defined:   ${totalIndexes}`);
    console.log(`Created:                 ${createdIndexes}`);
    console.log(`Skipped (already exist): ${skippedIndexes}`);
    console.log(`Collections processed:   ${Object.keys(INDEXES).length}`);
    console.log('==========================================\n');

    // List all indexes for verification
    console.log('🔍 Current Indexes by Collection:');
    console.log('==========================================');

    for (const collectionName of Object.keys(INDEXES)) {
      if (collectionNames.includes(collectionName)) {
        const indexes = await db.collection(collectionName).indexes();
        console.log(`\n📁 ${collectionName}: ${indexes.length} indexes`);
        indexes.forEach((idx) => {
          const options = [];
          if (idx.unique) options.push('unique');
          if (idx.sparse) options.push('sparse');
          if (idx.expireAfterSeconds) options.push(`ttl:${idx.expireAfterSeconds}s`);
          const optionsStr = options.length ? ` (${options.join(', ')})` : '';
          console.log(`   - ${idx.name}${optionsStr}`);
        });
      } else {
        console.log(`\n📁 ${collectionName}: collection not yet created`);
      }
    }
  } catch (error) {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    console.log('\n👋 Disconnected from MongoDB');
  }
}

// Run the script
createIndexes();
