/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QUANTUM LINK DIAGNOSTIC [V26.1.0-OMEGA]                                                                                     ║
 * ║ [FORENSIC PREFLIGHT | METRIC EXTRACTION | SOCKET DEBT VALIDATION | ZERO-SKEW AUDIT]                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 26.1.0-OMEGA | PRODUCTION READY                                                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/diagnoseQuantumLink.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated the purge of "Grade One" guesswork for Musk-Grade forensic precision.                 ║
 * ║ • Gemini (AI Engineering) - Engineered the Async Handshake Diagnostic and Admin-Level Ping telemetry.                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import quantumDatabase from '../config/database.js';
import chalk from 'chalk';

/**
 * 🛰️ [SOVEREIGN DIAGNOSTIC SEQUENCE]
 * Purpose: One command gives you a forensic health report before startup.
 * Execution: node --experimental-specifier-resolution=node scripts/diagnoseQuantumLink.js
 */
(async () => {
  console.log(chalk.cyan("\n🔬 WILSY OS - Quantum Link Diagnostic [Billion-Dollar Spec]"));
  console.log(chalk.stone ? chalk.stone("──────────────────────────────────────────────────────────") : "──────────────────────────────────────────────────────────");

  try {
    const startTime = Date.now();

    // 🛡️ PHASE 1: ATTEMPT QUANTUM HANDSHAKE
    const conn = await quantumDatabase.connect();

    if (!conn) {
      console.error(chalk.red("❌ Quantum Link could not be established. Nucleus unreachable."));
      process.exit(1);
    }

    const latency = Date.now() - startTime;

    // 🛡️ PHASE 2: EXTRACT FORENSIC METRICS
    console.log(chalk.green("✅ Quantum Link Established"));
    console.log(chalk.white(`📊 Connection Metrics:`), quantumDatabase.connectionMetrics);
    console.log(chalk.cyan(`⚡ Initial Handshake Latency: ${latency}ms`));

    // 🛡️ PHASE 3: ADMIN-LEVEL PING (THE TRUTH TEST)
    // We bypass the Mongoose abstraction to talk directly to the Admin DB.
    const admin = conn.connection.db.admin();
    const ping = await admin.ping();

    console.log(chalk.green("📡 Admin Ping Result:"), ping);

    if (ping.ok === 1) {
      console.log(chalk.magenta("\n🚀 SYSTEM STATUS: OPTIMAL | READY FOR INSTITUTIONAL IGNITION"));
    } else {
      console.log(chalk.yellow("\n⚠️ SYSTEM STATUS: SUB-OPTIMAL | PING REJECTED"));
    }

    // 🛡️ PHASE 4: GRACEFUL DISCONNECT
    await quantumDatabase.disconnect();
    console.log(chalk.cyan("🔒 Diagnostic Complete. Link Severed.\n"));
    process.exit(0);

  } catch (error) {
    console.error(chalk.red("\n💥 CRITICAL SINGULARITY BREACH IN DIAGNOSTIC:"));
    console.error(chalk.red(`[ERROR_CODE]: ${error.name}`));
    console.error(chalk.red(`[NARRATIVE]: ${error.message}`));
    process.exit(1);
  }
})();
