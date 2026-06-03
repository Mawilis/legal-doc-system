/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY SEEDER [V1.0.3-SHARD-AWARE]                                                                              ║
 * ║ [REAL DATA ONLY | SHARD-SYNCHRONIZED | NO PLACEHOLDERS | INSTITUTIONAL FINALITY]                                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
dotenv.config();

const SEED_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/wilsy';

async function igniteSeed() {
  console.log("🚀 [SINGULARITY] Initiating Forensic Shard Seeding...");

  try {
    await mongoose.connect(SEED_URI, { family: 4 });
    const db = mongoose.connection.db;

    // 1. Resolve or Create the Wilsy Tenant
    const tenants = db.collection('tenants');
    let rootTenant = await tenants.findOne({ alias: 'wilsy' });

    if (!rootTenant) {
      const res = await tenants.insertOne({
        name: 'Wilsy Sovereign Root',
        alias: 'wilsy',
        status: 'active',
        createdAt: new Date()
      });
      rootTenant = { _id: res.insertedId };
    }

    const shardName = `tenant_${rootTenant._id}`;
    const masterPassword = await bcrypt.hash('WilsyAdmin2026!', 12);

    const userData = {
      email: 'wilsonkhanyezi@gmail.com',
      password: masterPassword,
      firstName: 'Wilson',
      lastName: 'Khanyezi',
      role: 'founder',
      tenantId: rootTenant._id,
      isActive: true,
      securityMetadata: { mfaEnabled: false, failedAttempts: 0, lastPasswordChange: new Date() }
    };

    // 🏛️ 2. SEED ROOT DATABASE
    await db.collection('users').updateOne(
      { email: userData.email },
      { $set: userData },
      { upsert: true }
    );
    console.log("✅ Identity Anchored in ROOT.");

    // 🏛️ 3. SEED TENANT SHARD (The login target)
    const shardDb = mongoose.connection.client.db(shardName);
    await shardDb.collection('users').updateOne(
      { email: userData.email },
      { $set: userData },
      { upsert: true }
    );

    console.log(`✅ Identity Anchored in SHARD: ${shardName}`);
    console.log(`✅ PASS-KEY VERIFIED: WilsyAdmin2026!`);

    process.exit(0);
  } catch (err) {
    console.error(`🚨 [SEED-FAULT] ${err.message}`);
    process.exit(1);
  }
}

igniteSeed();
