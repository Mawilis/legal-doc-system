#!/usr/bin/env node

/**
 * WILSY OS: SENTINEL HEALTHCHECK
 * Verifies Recovery Sentinel is operational
 */

import mongoose from "mongoose";
import { redisClient } from 'wilsy-os-server/utils/redisClient.js.js';
import RecoverySentinel from './RecoverySentinel.js.js';

async function checkHealth() {
  console.log('🔍 Checking Wilsy OS Sentinel Health...');

  const checks = {
    sentinel: false,
    redis: false,
    mongodb: false,
    timestamp: new Date().toISOString(),
  };

  try {
    // Check sentinel instance
    if (RecoverySentinel && RecoverySentinel.isRunning) {
      checks.sentinel = true;
      console.log('✅ Sentinel: Running');
    } else {
      console.log('❌ Sentinel: Not running');
    }

    // Check Redis
    try {
      await redisClient.ping();
      checks.redis = true;
      console.log('✅ Redis: Connected');
    } catch {
      console.log('❌ Redis: Disconnected');
    }

    // Check MongoDB
    if (mongoose.connection.readyState === 1) {
      checks.mongodb = true;
      console.log('✅ MongoDB: Connected');
    } else {
      console.log('❌ MongoDB: Disconnected');
    }

    // Overall status
    const healthy = checks.sentinel && checks.redis && checks.mongodb;

    console.log('\n📊 Sentinel Health Summary:');
    console.log(`🛡️ Sentinel: ${checks.sentinel ? '✅' : '❌'}`);
    console.log(`📦 Redis: ${checks.redis ? '✅' : '❌'}`);
    console.log(`🗄️ MongoDB: ${checks.mongodb ? '✅' : '❌'}`);
    console.log(`\n${healthy ? '✅ SYSTEM HEALTHY' : '❌ SYSTEM DEGRADED'}`);

    process.exit(healthy ? 0 : 1);
  } catch (error) {
    console.error('❌ Healthcheck failed:', error);
    process.exit(1);
  }
}

checkHealth();
