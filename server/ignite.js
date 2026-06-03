/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - GENESIS IGNITION [V42.0.5-FORTRESS-HUD]                                                                                     ║
 * ║ [TELEMETRY BROADCAST | FORENSIC AUDIT | REDIS HEALTH PRE-CHECK | GRACEFUL ABORT | LEGACY SHIELD]                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 42.0.5-FORTRESS-HUD | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                              ║
 * ║ EPITOME: INSTITUTIONAL AUTHORITY | ZERO-DROP | BOARDROOM READY                                                                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/ignite.js                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-strip policy, legacy dependency shielding, and telemetry pre-flight hooks.      ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Injected Redis Pre-check, Telemetry Broadcasts, and Audit Persistence hooks. [2026-05-10]       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

// 🛡️ STAGE -1: ABSOLUTE GENESIS COMPATIBILITY SHIELD
// Prevent fractures from legacy module hoisting before core evaluation.
import { Buffer } from 'node:buffer';
if (typeof global.SlowBuffer === 'undefined') {
  global.SlowBuffer = Buffer;
  if (!global.SlowBuffer.prototype) global.SlowBuffer.prototype = Buffer.prototype;
}

// 🚀 STAGE 0: TELEMETRY + FORENSIC ENRICHMENT
import { broadcastTelemetry } from './utils/telemetryHelper.js';
import { checkRedisHealth } from './config/redis.js';
import mongoose from 'mongoose';

// 🛡️ REDIS HEALTH PRE-CHECK
(async () => {
  try {
    const redisHealth = await checkRedisHealth();
    if (redisHealth.status !== 'HEALTHY') {
      console.warn(`⚠️ [IGNITE] Redis not healthy at Genesis: ${JSON.stringify(redisHealth)}`);
      broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "REDIS_PRECHECK_WARNING", "Ignite", { redisHealth });
    }
  } catch (err) {
    console.error("💥 [IGNITE] Redis health pre-check failed:", err.message);
  }
})();

// 🚀 STAGE 1: DYNAMIC IMPORT OF THE MASTER CORE
import('./server.js').catch(async err => {
  console.error("💥 [GENESIS FRACTURE] Failed to ignite Master Core:", err);

  // Broadcast telemetry strike
  broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "GENESIS_FRACTURE", "Ignite", { error: err.message });

  // Forensic audit persistence
  try {
    if (mongoose.models.Telemetry) {
      await mongoose.models.Telemetry.create({
        eventType: 'GENESIS_FAILURE',
        tenantId: 'GLOBAL_ROOT',
        metadata: { error: err.message, stack: err.stack }
      });
    }
  } catch (auditErr) {
    console.warn("⚠️ [AUDIT] Genesis failure persistence delayed:", auditErr.message);
  }

  // Graceful abort telemetry
  broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "GENESIS_ABORT", "Ignite", { reason: 'Server import failure' });

  process.exit(1);
});
