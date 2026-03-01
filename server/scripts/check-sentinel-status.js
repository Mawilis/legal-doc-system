#!/usr/bin/env node/usr/bin/env node

/**
 * WILSY OS: SENTINEL STATUS CHECK
 * Displays current sentinel metrics and quarantined tenants
 */

import { getQuarantinedTenants } from 'wilsy-os-server/middleware/emergencyKillSwitch.js';
import RecoverySentinel from './RecoverySentinel.js';

async function checkStatus() {
  console.log(`\n${'='.repeat(70)}`);
  console.log('🛡️ WILSY OS RECOVERY SENTINEL STATUS');
  console.log('='.repeat(70));

  try {
    // Get sentinel status
    const status = RecoverySentinel.getStatus();

    console.log('\n📋 SENTINEL INFO:');
    console.log(`  ID: ${status.sentinelId}`);
    console.log(`  PID: ${status.pid}`);
    console.log(`  Uptime: ${Math.floor(status.uptime / 60)} minutes`);
    console.log(`  Running: ${status.isRunning ? '✅' : '❌'}`);

    console.log('\n📊 HEALTH STATUS:');
    status.healthStatus.forEach((health) => {
      const icon = health.isHealthy ? '✅' : '❌';
      console.log(`  ${icon} ${health.service}: ${health.responseTime || 0}ms`);
    });

    console.log('\n🔌 CIRCUIT BREAKERS:');
    status.circuitBreakers.forEach((breaker) => {
      console.log(`  ${breaker.state} ${breaker.service} (failures: ${breaker.failureCount})`);
    });

    console.log('\n🚫 FAILURES:');
    status.failures.forEach((failure) => {
      console.log(`  ${failure.service}: ${failure.count} attempts`);
    });

    // Check quarantined tenants
    const quarantined = await getQuarantinedTenants();

    console.log(`\n🔒 QUARANTINED TENANTS: ${quarantined.length}`);
    quarantined.forEach((q) => {
      console.log(
        `  🚫 ${q.tenantId}: ${q.quarantine.reason} (expires: ${q.quarantine.expiresAt})`
      );
    });

    console.log(`\n${'='.repeat(70)}`);
    console.log(`📅 ${new Date().toISOString()}`);
    console.log('='.repeat(70));
  } catch (error) {
    console.error('❌ Failed to get sentinel status:', error);
    process.exit(1);
  }
}

checkStatus();
