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
const MONGODB_URI = process.env.MONGODB_URI || process.env.MONGODB_URI ':***@')}`);
    await mongoose.connect(MONGODB_URI);
    console.log('✅ Connected to MongoDB\n');

    const { db } = mongoose.connection;
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
          '   ⚠️  Collection does not exist yet - will be created when first document inserted',
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
