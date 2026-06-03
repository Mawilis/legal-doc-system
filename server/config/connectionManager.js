/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN CONNECTION MANAGER [V1.1.0-MASTER-POOL]                                                                           ║
 * ║ [MASTER CONNECTION SINGLETON | DYNAMIC SHARD SWITCHING | SCOPE CONTAMINATION ELIMINATED]                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-MASTER-POOL | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/connectionManager.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated decoupling of pre‑scoped connection to fix 0‑user shard fracture.                    ║
 * ║ • AI Engineering (DeepSeek) - RECTIFIED: Return master connection (mongoose.connection) to allow clean useDb() in controllers.         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import chalk from 'chalk';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * ⚓ getSovereignDb
 * Returns the MASTER connection singleton (the root Mongoose connection).
 * Dynamic shard switching (useDb) MUST be performed on the master instance
 * to avoid scope contamination and ensure each shard gets a clean, isolated
 * connection pool.
 *
 * @returns {mongoose.Connection} The master Mongoose connection.
 * @real-world Called by authController to obtain a master connection,
 *   then dynamically switches to tenant‑specific shards with `useDb`.
 * @forensic The connection state is logged and broadcast via telemetry.
 */
export const getSovereignDb = () => {
  // Check if master connection is active (readyState 1 = connected)
  if (mongoose.connection.readyState === 1) {
    console.log(chalk.green(`[CONN-MANAGER] Master connection ready (state: ${mongoose.connection.readyState})`));
    return mongoose.connection;
  }

  console.log(chalk.bold.cyan('\n🏛️  ANCHORING MASTER CONNECTION...'));
  broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "MASTER_CONNECTION_REQUEST", "ConnectionManager", {
    readyState: mongoose.connection.readyState,
    timestamp: new Date().toISOString()
  });

  // Return the master connection even if not yet ready – the caller will handle readiness.
  // Mongoose will eventually connect; the controller can await connection if needed.
  return mongoose.connection;
};

/**
 * @function isSovereignDbHealthy
 * @description Institutional health check for circuit breaker integration.
 * @returns {boolean} True if the master connection is open (readyState === 1).
 */
export const isSovereignDbHealthy = () => {
  return mongoose.connection.readyState === 1;
};

export default getSovereignDb;
