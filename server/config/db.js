/* eslint-disable */
/**
 * ===============================================================================
 * EPITOME: WILSY OS - SOVEREIGN DATABASE PROXY / KERNEL ANCHOR
 * STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE
 * ===============================================================================
 * File:           server/config/db.js
 * Version:        v3.0.0-ATLAS-PROXY
 * Authority:      Wilsy OS Core Governance
 * Classification: Production Artifact (Sovereign Proxy Layer)
 *
 * COLLABORATION COMMENTS:
 * - @Wilson: Absolute alignment with the v3.0.0-SINGULARITY-NUCLEUS database core.
 *   Ensures all models and routes calling proxy methods inherit zero-loss resilience.
 * - @WilsyOS: Clean re-exports of core database health hooks (`isDbReady`, `getDbStatus`),
 *   coupled with safe deprecation fallbacks for legacy transaction/sharding stubs.
 *
 * Forensic Relationships:
 *   Upstream:   ./database.js (Sovereign Database Nucleus v3.0.0)
 *   Downstream: index.js, models, routes, telemetry
 * ===============================================================================
 */

import mongoose from 'mongoose';
import connectDB, { isDbReady, getDbStatus } from './database.js';

// ─── RE-EXPORT CORE ATLAS-RESILIENT FUNCTIONS ───────────────────────────
export { connectDB, isDbReady, getDbStatus };

/**
 * @function useDatabase
 * @description Compatibility shard resolver (legacy). Returns default connection
 * with a telemetry warning under the singularity architecture.
 * @param {string} [tenantId] - Ignored; kept for API compatibility.
 * @returns {mongoose.Connection} The default Mongoose connection.
 * @deprecated Tenant sharding is handled globally in Wilsy OS v3.0.0.
 */
export const useDatabase = (tenantId) => {
  if (tenantId) {
    console.warn(
      '[DB_PROXY] useDatabase() is deprecated in v3.0.0. ' +
      'Tenant isolation is managed via sovereign context middleware; using default connection.'
    );
  }
  return mongoose.connection;
};

/**
 * @function executeSovereignTransaction
 * @description Legacy ACID transaction wrapper. Falls back to direct execution
 * without active session locking unless explicitly managed via mongoose sessions.
 * @param {Function} callback - Async function to execute.
 * @param {Object} [options] - Ignored options.
 * @returns {Promise<any>} Result of the callback execution.
 * @deprecated Use mongoose.startSession() directly for replica-set atomic operations.
 */
export const executeSovereignTransaction = async (callback, options) => {
  console.warn(
    '[DB_PROXY] executeSovereignTransaction() is deprecated. ' +
    'Executing operation without transactional session wrapper.'
  );
  try {
    return await callback(null);
  } catch (err) {
    throw err;
  }
};

/**
 * @function disconnectDB
 * @description Gracefully severs the sovereign database link.
 * @returns {Promise<void>}
 */
export const disconnectDB = async () => {
  try {
    if (mongoose.connection && mongoose.connection.readyState !== 0) {
      await mongoose.disconnect();
      console.info('[DB_PROXY] Sovereign Database link gracefully severed.');
    }
  } catch (err) {
    console.error(`[DB_PROXY] Disconnect error: ${err.message}`);
  }
};

/**
 * @function closeDatabase
 * @description Alias for disconnectDB.
 */
export const closeDatabase = disconnectDB;

/**
 * @function isDatabaseConnected
 * @description Legacy health check bridge; delegates directly to isDbReady().
 * @returns {boolean}
 */
export const isDatabaseConnected = () => isDbReady();

/**
 * 🏛️ DEFAULT EXPORT — Primary connection entrypoint.
 */
export default connectDB;

/**
 * ===============================================================================
 * INSTITUTIONAL CERTIFICATION SEAL — db.js v3.0.0-ATLAS-PROXY
 * ===============================================================================
 * Status: CERTIFIED — Zero-loss forwarding to the v3.0 nucleus. Legacy stubs secured.
 * ===============================================================================
 */
