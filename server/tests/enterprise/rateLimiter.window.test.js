/* eslint-disable */
import { expect } from 'chai';
import { HighPrecisionRateLimiter } from '../../enterprise/rateLimiter.js';

describe('⏱️ WILSY OS 2050 - WINDOW SLIDING TEST (ISOLATED)', function() {
  this.timeout(5000);

  it('[F500-007] SHOULD reset counters after time window expires', async () => {
    console.log('\n╔════════════════════════════════════════════════════════════════════╗');
    console.log('║  📝 TEST F500-007: WINDOW SLIDING ACCURACY (ISOLATED)              ║');
    console.log('╚════════════════════════════════════════════════════════════════════╝\n');

    // Create a fresh limiter for this test only
    const testLimiter = new HighPrecisionRateLimiter({ 
      defaultQPS: 10, 
      windowMs: 100
    });

    // FIX: Use silver tier tenant (limit = defaultQPS = 10)
    const tenantId = 'f500-silver-00001';
    const LIMIT = 10;

    console.log(`  🔄 First window: executing ${LIMIT} requests...`);
    console.log(`  📊 Tier: SILVER (limit = ${LIMIT} QPS)`);
    
    let results = [];
    for (let i = 0; i < LIMIT; i++) {
      const result = testLimiter.checkRateLimit(tenantId);
      results.push(result);
      console.log(`  ├─ Request ${i+1}: ${result.allowed ? 'ALLOWED' : 'BLOCKED'}`);
    }

    // All first 10 should be allowed
    const firstWindowAllowed = results.filter(r => r.allowed).length;
    console.log(`  ├─ First window: ${firstWindowAllowed}/${LIMIT} allowed`);
    expect(firstWindowAllowed).to.equal(LIMIT);

    // Request 11 should be BLOCKED
    const request11 = testLimiter.checkRateLimit(tenantId);
    console.log(`  ├─ Request 11: ${request11.allowed ? 'ALLOWED (FAIL)' : 'BLOCKED (PASS)'}`);
    
    expect(request11.allowed).to.be.false;

    console.log(`  ⏳ Waiting 150ms for window to reset...`);
    await new Promise(resolve => setTimeout(resolve, 150));

    console.log(`  🔄 Second window: executing ${LIMIT} requests...`);
    
    let secondResults = [];
    for (let i = 0; i < LIMIT; i++) {
      const result = testLimiter.checkRateLimit(tenantId);
      secondResults.push(result);
      console.log(`  ├─ Request ${i+11}: ${result.allowed ? 'ALLOWED' : 'BLOCKED'}`);
    }

    const secondWindowAllowed = secondResults.filter(r => r.allowed).length;
    console.log(`  ├─ Second window: ${secondWindowAllowed}/${LIMIT} allowed`);
    expect(secondWindowAllowed).to.equal(LIMIT);

    // Request after second window should be blocked
    const finalRequest = testLimiter.checkRateLimit(tenantId);
    console.log(`  ├─ Final request: ${finalRequest.allowed ? 'ALLOWED' : 'BLOCKED'}`);
    expect(finalRequest.allowed).to.be.false;

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
