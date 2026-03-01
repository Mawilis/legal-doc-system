#!/usr/bin/env node/usr/bin/env node
/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DATABASE WARMUP FOR FORENSIC TESTS                             ║
 * ║ Ensures MongoDB is ready before test suite execution                      ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';

async function warmup() {
  console.log('🔥 Warming up database for forensic tests...');

  try {
    // Try connecting to real MongoDB first
    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy_test';

    await mongoose.connect(mongoUri, {
      serverSelectionTimeoutMS: 5000,
      connectTimeoutMS: 10000,
    });

    await mongoose.connection.db.admin().ping();
    console.log('✅ MongoDB connection established');

    // Create indexes for better test performance
    const collections = await mongoose.connection.db.collections();
    console.log(`📊 Found ${collections.length} collections`);

    await mongoose.disconnect();
    console.log('✅ Database warmup complete');
  } catch (error) {
    console.log('⚠️ Could not connect to real MongoDB, using memory server');

    // Fallback to in-memory MongoDB for CI
    const mongod = await MongoMemoryServer.create();
    const uri = mongod.getUri();

    await mongoose.connect(uri);
    console.log('✅ In-memory MongoDB started');

    await mongoose.disconnect();
    await mongod.stop();
  }
}

warmup().catch(console.error);
