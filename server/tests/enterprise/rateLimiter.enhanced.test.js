/* eslint-disable */
import { expect } from 'chai';
import { getRateLimiter } from '../../enterprise/rateLimiter.js';

describe('⏱️ WILSY OS 2050 - HIGH-PRECISION RATE LIMITER VALIDATION', function() {
  this.timeout(10000);
  
  let limiter;
  const testRunId = `rate-test-${Date.now()}-${Math.random().toString(36).substring(7)}`;

  beforeEach(() => {
    limiter = getRateLimiter({ 
      defaultQPS: 1000,
      windowMs: 1000,
      seed: 0xF500F500
    });
    limiter.reset();
    limiter.disableTestMode(); // Ensure test mode is off by default
  });

  afterEach(() => {
    console.log(JSON.stringify({
      audit: {
        testRunId,
        timestamp: new Date().toISOString(),
        component: 'rate-limiter-test',
        status: 'completed'
      }
    }));
  });

  it('[F500-004] SHOULD handle 12,000 request burst deterministically', () => {
    console.log('\n╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  📝 TEST F500-004: BURST HANDLING (12,000 REQUESTS)                ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    limiter.enableTestMode();

    const tenantId = 'f500-platinum-0001';
    const BURST_SIZE = 12000;
    const EXPECTED_ALLOWED = 10000;
    const EXPECTED_BLOCKED = 2000;
    const EXPECTED_ERROR_RATE = '16.67%';

    console.log(`  🔄 Executing ${BURST_SIZE.toLocaleString()} requests...`);

    for (let i = 0; i < BURST_SIZE; i++) {
      limiter.checkRateLimit(tenantId);
      if ((i + 1) % 2000 === 0) {
        process.stdout.write(`  ⏳ Progress: ${(i + 1).toLocaleString()}/${BURST_SIZE.toLocaleString()}\r`);
      }
    }

    const stats = limiter.getStats();
    const errorRate = ((stats.blocked / BURST_SIZE) * 100).toFixed(2) + '%';

    console.log(`\n\n  📊 RESULTS:`);
    console.log(`  ├─ Allowed: ${stats.allowed.toLocaleString()} (expected: ${EXPECTED_ALLOWED.toLocaleString()})`);
    console.log(`  ├─ Blocked: ${stats.blocked.toLocaleString()} (expected: ${EXPECTED_BLOCKED.toLocaleString()})`);
    console.log(`  ├─ Error Rate: ${errorRate} (expected: ${EXPECTED_ERROR_RATE})`);
    console.log(`  └─ Active Buckets: ${stats.activeBuckets}`);

    expect(stats.allowed).to.equal(EXPECTED_ALLOWED);
    expect(stats.blocked).to.equal(EXPECTED_BLOCKED);
    expect(errorRate).to.equal(EXPECTED_ERROR_RATE);

    limiter.disableTestMode();

    console.log('\n  ✅ TEST F500-004 PASSED - BURST HANDLING VERIFIED\n');
  });

  it('[F500-005] SHOULD enforce Tier-based limits (Platinum > Gold > Silver)', () => {
    console.log('╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  📝 TEST F500-005: TIER-BASED LIMIT ENFORCEMENT                    ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    const testCases = [
      { tier: 'platinum', tenantId: 'f500-platinum-0001', expectedLimit: 10000, emoji: '🥇' },
      { tier: 'gold', tenantId: 'f500-gold-0001', expectedLimit: 5000, emoji: '🥈' },
      { tier: 'silver', tenantId: 'f500-silver-00001', expectedLimit: 1000, emoji: '🥉' }
    ];

    for (const test of testCases) {
      limiter.reset();
      
      console.log(`  ${test.emoji} Testing ${test.tier.toUpperCase()} tier: ${test.tenantId}`);
      
      let allowed = 0;
      
      // Run exactly up to expected limit
      for (let i = 0; i < test.expectedLimit; i++) {
        const result = limiter.checkRateLimit(test.tenantId);
        if (result.allowed) allowed++;
      }

      // Next request should be blocked
      const nextResult = limiter.checkRateLimit(test.tenantId);
      
      console.log(`  ├─ Expected: ${test.expectedLimit} | Actual: ${allowed}`);
      console.log(`  ├─ Next request allowed: ${nextResult.allowed ? 'YES (FAIL)' : 'NO (PASS)'}`);
      console.log(`  └─ Status: ${allowed === test.expectedLimit && !nextResult.allowed ? '✓ PASS' : '✗ FAIL'}\n`);

      expect(allowed).to.equal(test.expectedLimit);
      expect(nextResult.allowed).to.be.false;
    }

    console.log('  ✅ TEST F500-005 PASSED - TIER ENFORCEMENT VERIFIED\n');
  });

  it('[F500-006] SHOULD maintain isolation between different tenants', () => {
    console.log('╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  📝 TEST F500-006: TENANT ISOLATION VERIFICATION                   ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    limiter.reset();

    const tenant1 = 'f500-platinum-0001';
    const tenant2 = 'f500-platinum-0002';
    const REQUEST_COUNT = 500;

    console.log(`  🔄 Executing ${REQUEST_COUNT} requests for Tenant 1: ${tenant1}`);
    
    for (let i = 0; i < REQUEST_COUNT; i++) {
      limiter.checkRateLimit(tenant1);
    }

    console.log(`  ├─ Tenant 1 usage: ${REQUEST_COUNT} requests`);

    console.log(`  🔄 Testing Tenant 2: ${tenant2} (should be unaffected)`);
    
    let tenant2Allowed = 0;
    for (let i = 0; i < REQUEST_COUNT; i++) {
      const result = limiter.checkRateLimit(tenant2);
      if (result.allowed) tenant2Allowed++;
    }

    console.log(`  ├─ Tenant 2 allowed: ${tenant2Allowed}/${REQUEST_COUNT}`);
    console.log(`  └─ Expected: ${REQUEST_COUNT}/${REQUEST_COUNT}`);

    expect(tenant2Allowed).to.equal(REQUEST_COUNT);

    console.log('\n  ✅ TEST F500-006 PASSED - TENANT ISOLATION VERIFIED\n');
  });

  it('[F500-007] SHOULD reset counters after time window expires', async () => {
    console.log('╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  📝 TEST F500-007: WINDOW SLIDING ACCURACY                         ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    // Create a fresh limiter with small window for testing
    const testLimiter = getRateLimiter({ 
      defaultQPS: 10, 
      windowMs: 100,
      seed: 0xF500F500
    });
    testLimiter.disableTestMode();

    const tenantId = 'f500-platinum-0001';
    const LIMIT = 10;

    console.log(`  🔄 First window: executing ${LIMIT} requests...`);
    
    let firstWindowAllowed = 0;
    for (let i = 0; i < LIMIT; i++) {
      const result = testLimiter.checkRateLimit(tenantId);
      if (result.allowed) firstWindowAllowed++;
    }
    expect(firstWindowAllowed).to.equal(LIMIT);
    console.log(`  ├─ First window: ${firstWindowAllowed}/${LIMIT} allowed`);

    // Next request should be blocked
    const blockedRequest = testLimiter.checkRateLimit(tenantId);
    console.log(`  ├─ Request ${LIMIT + 1}: ${blockedRequest.allowed ? 'ALLOWED (FAIL)' : 'BLOCKED (PASS)'}`);
    
    // FIX: Check that the request is blocked (allowed should be false)
    expect(blockedRequest.allowed).to.be.false;

    console.log(`  ⏳ Waiting 150ms for window to reset...`);
    await new Promise(resolve => setTimeout(resolve, 150));

    console.log(`  🔄 Second window: executing ${LIMIT} requests...`);
    
    let secondWindowAllowed = 0;
    for (let i = 0; i < LIMIT; i++) {
      const result = testLimiter.checkRateLimit(tenantId);
      if (result.allowed) secondWindowAllowed++;
    }

    console.log(`  ├─ Second window: ${secondWindowAllowed}/${LIMIT} allowed`);
    expect(secondWindowAllowed).to.equal(LIMIT);

    // Next request should be blocked again
    const finalBlocked = testLimiter.checkRateLimit(tenantId);
    console.log(`  ├─ Final request: ${finalBlocked.allowed ? 'ALLOWED' : 'BLOCKED'}`);
    expect(finalBlocked.allowed).to.be.false;

    // Verify stats
    const stats = testLimiter.getStats();
    console.log(`  ├─ Total allowed: ${stats.allowed}`);
    console.log(`  ├─ Total blocked: ${stats.blocked}`);
    console.log(`  └─ Expected: allowed=${LIMIT * 2}, blocked=2`);

    expect(stats.allowed).to.equal(LIMIT * 2);
    expect(stats.blocked).to.equal(2);

    console.log('\n  ✅ TEST F500-007 PASSED - WINDOW SLIDING VERIFIED\n');
  });
});
