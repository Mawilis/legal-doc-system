/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN DATABASE NUCLEUS [V12.0.0-MARS-TRANSACTIONAL]                                                                     ║
 * ║ [REPLICA SET ENFORCEMENT | ATOMIC TRANSACTIONS | RECURSIVE ANCHORING | MASTER SHARD RESOLVER]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 12.0.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                      ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/database.js                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated Transactional Integrity and Replica Set deployment for billion-dollar stability.     ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Upgraded connection URI to enforce Replica Set topology. [2026-05-17]                           ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Injected executeSovereignTransaction utility for atomic rollbacks. [2026-05-17]               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import chalk from 'chalk';
import metrics from '../utils/metrics.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const AUTH_FAILURE_PATTERN = /(auth|authentication).*(fail|failed|error)|bad auth|not authorized/i;

const isAuthFailure = (error) => {
  return AUTH_FAILURE_PATTERN.test(error?.message || '') || error?.codeName === 'AuthenticationFailed';
};

/**
 * 🛰️ CONNECT SOVEREIGN DATABASE
 * @desc Establishes the primary data link with institutional-grade auto-recovery.
 * Enforces Replica Set topology to enable multi-document ACID transactions.
 * @param {number} retryCount - Current attempt in the recursive backoff chain.
 */
export const connectDB = async (retryCount = 0) => {
  // 🛡️ RECTIFIED: Removed directConnection=true. Appended replicaSet directive if locally simulating a cluster.
  const primaryUrl = process.env.MONGODB_URI;
  const fallbackUrl = 'mongodb://127.0.0.1:27017/wilsy-sovereign-root?replicaSet=rs0';
  const MAX_RETRIES = 5;

  const sovereignOptions = {
    maxPoolSize: 50, // Increased for concurrent transaction handling
    minPoolSize: 10,
    family: 4,
    serverSelectionTimeoutMS: 15000, // Extended slightly for Replica Set discovery
    socketTimeoutMS: 45000,
    heartbeatFrequencyMS: 2000,
    appName: 'Wilsy-OS-Sovereign-Nucleus',
    // Write Concern 'majority' ensures data is written to a majority of replica nodes before acknowledging.
    writeConcern: { w: 'majority', j: true }
  };

  try {
    console.log(chalk.blue(`[DATABASE] 📡 INITIATING TRANSACTIONAL REPLICA SET LINK (Attempt ${retryCount + 1})...`));

    const connectionUrl = primaryUrl || fallbackUrl;
    await mongoose.connect(connectionUrl, sovereignOptions);

    metrics.updateBreakerState('DATABASE', 0, { tenantId: 'GLOBAL_ROOT' });
    metrics.increment('telemetry_events_total', 1, { eventType: 'DB_CONNECTION_SUCCESS' });

    console.log(chalk.green(`[DATABASE] ✅ QUANTUM REPLICA LINK ESTABLISHED | NUCLEUS: ${mongoose.connection.name}`));

  } catch (error) {
    console.warn(chalk.yellow(`[DATABASE] ⚠️ REPLICA FRACTURE DETECTED: ${error.message}`));

    metrics.increment('system_errors_total', 1, { severity: 'HIGH', type: 'DB_INIT_FRACTURE' });

    if (isAuthFailure(error)) {
      metrics.updateBreakerState('DATABASE', 1, { tenantId: 'GLOBAL_ROOT', reason: 'AUTHENTICATION_FAILED' });
      const authError = new Error('MongoDB authentication failed. Verify MONGODB_URI credentials and authSource.');
      authError.cause = error;
      throw authError;
    }

    if (retryCount < MAX_RETRIES) {
      const waitTime = 5000;
      console.log(chalk.cyan(`[DATABASE] 🔄 Socket reclamation in progress. Re-anchoring in ${waitTime}ms...`));

      broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "DB_RECONNECT_ATTEMPT", "DatabaseNucleus", {
        attempt: retryCount + 1,
        error: error.message
      });

      await new Promise(resolve => setTimeout(resolve, waitTime));
      return connectDB(retryCount + 1);
    }

    metrics.updateBreakerState('DATABASE', 1, { tenantId: 'GLOBAL_ROOT', reason: 'MAX_RETRIES_EXCEEDED' });

    console.error(chalk.red("[FATAL] SINGULARITY BREACH: Absolute replica failure. Max retries exhausted."));
    throw error;
  }

  // ────────────────────────────────────────────────────────────────
  // 🛡️ FORENSIC HANDSHAKE MONITORS
  // ────────────────────────────────────────────────────────────────

  mongoose.connection.on('error', (err) => {
    metrics.increment('telemetry_integrity_failures_total', 1, { type: 'DB_SHARD_FRACTURE' });
    console.error(chalk.red(`[DATABASE] 💥 SHARD FRACTURE: ${err.message}`));
  });

  mongoose.connection.on('disconnected', () => {
    metrics.updateBreakerState('DATABASE', 1, { tenantId: 'GLOBAL_ROOT', reason: 'LINK_SEVERED' });
    console.warn(chalk.yellow("[DATABASE] ⚠️ REPLICA LINK SEVERED: Executing automated re-anchoring protocol..."));
  });

  mongoose.connection.on('reconnected', () => {
    metrics.updateBreakerState('DATABASE', 0, { tenantId: 'GLOBAL_ROOT' });
    metrics.increment('telemetry_events_total', 1, { eventType: 'DB_LINK_RESTORED' });
    console.log(chalk.green("[DATABASE] 🔄 LINK RESTORED: Sovereign Replica Nucleus Re-anchored successfully."));
  });
};

/**
 * 🌐 TENANT SHARD RESOLVER (useDatabase)
 * @desc Dynamically switches context to a tenant-specific shard with zero-latency caching.
 */
export const useDatabase = (tenantId) => {
  const start = process.hrtime();

  if (!mongoose.connection || mongoose.connection.readyState !== 1) {
    metrics.increment('system_errors_total', 1, { type: 'DB_LINK_DEAD_ON_SWITCH' });
    console.error(chalk.red("[DATABASE] 💥 Cannot switch tenant shard: Sovereign Link is not active."));
    throw new Error("Database link severed.");
  }

  if (!tenantId) return mongoose.connection;

  const MASTER_SHARDS = ['WILSY_ROOT', 'MASTER', 'WILSY_MASTER', 'GLOBAL_ROOT', 'WILSY_GLOBAL_ROOT', 'wilsy'];
  const physicalTarget = MASTER_SHARDS.includes(tenantId) ? 'wilsy-sovereign-root' : tenantId;

  const db = mongoose.connection.useDb(physicalTarget, { useCache: true });

  const diff = process.hrtime(start);
  const timeInMs = (diff[0] * 1e3 + diff[1] * 1e-6).toFixed(3);
  metrics.recordTiming('latency_db_shard_switch', Number(timeInMs), { tenantId: physicalTarget });

  return db;
};

// ============================================================================
// 🛡️ ATOMIC TRANSACTION WRAPPER
// ============================================================================

/**
 * Executes a callback within an isolated MongoDB ACID Transaction.
 * Automatically handles commit, rollback on failure, and session termination.
 * REQUIRES Replica Set Topology.
 *
 * @param {Function} callback - Async function containing DB operations. Must accept the `session` object.
 * @returns {Promise<any>} Result of the callback.
 *
 * @example
 * await executeSovereignTransaction(async (session) => {
 *   await User.create([{ name: 'Wilson' }], { session });
 *   await Invoice.create([{ amount: 1000 }], { session });
 * });
 */
export const executeSovereignTransaction = async (callback) => {
  const session = await mongoose.startSession();
  session.startTransaction();

  try {
    const result = await callback(session);
    await session.commitTransaction();
    console.log(chalk.green(`[TRANSACTION] ✅ Atomic Ledger Commit Successful.`));
    return result;
  } catch (error) {
    await session.abortTransaction();
    console.error(chalk.red(`[TRANSACTION-FRACTURE] 💥 Rollback Executed: ${error.message}`));
    throw error;
  } finally {
    session.endSession();
  }
};

export default connectDB;
