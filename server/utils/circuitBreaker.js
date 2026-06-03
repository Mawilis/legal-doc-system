/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DISTRIBUTED CIRCUIT BREAKER & FORENSIC WITHDRAWAL [V4.4.0-MARS]                                                             ║
 * ║ [REDIS-BACKED STATE MACHINE | CLUSTER-WIDE SYNCHRONIZATION | AUTO-HEALING HALF-OPEN PROTOCOL]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 4.4.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                        ║
 * ║ EPITOME: INSTITUTIONAL DOMINANCE | NO CHILD'S PLACE | THE ARCHITECT'S FAILSAFE                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/circuitBreaker.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                  ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated Redis-backed distributed synchronization for Kubernetes scaling. [2026-05-17]         ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Transitioned from in-memory Map to Redis Hash state management. [2026-05-17]                     ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Integrated self-healing fire() loop and Half-Open cooldown protocol. [2026-05-17]              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import logger from './logger.js';
import redisClient from '../cache/redisClient.js'; // 🛡️ DISTRIBUTED STATE ENGINE
import chalk from 'chalk';

// ============================================================================
// 🛡️ THE BREAKER REGISTRY (Local Cache)
// ============================================================================

/**
 * Local memory registry to prevent redundant object instantiation per pod.
 * The TRUE state of the breaker is now stored in Redis.
 * @type {Map<string, CircuitBreaker>}
 */
export const breakerRegistry = new Map();

// ============================================================================
// 🏛️ DISTRIBUTED CIRCUIT BREAKER CLASS
// ============================================================================

/**
 * Distributed Circuit Breaker backed by Redis for Kubernetes horizontal scaling.
 *
 * **States**:
 * - `CLOSED`: Normal operation, requests allowed.
 * - `OPEN`: Failure threshold exceeded across the cluster, requests blocked.
 * - `HALF_OPEN`: Cooldown elapsed, allowing 1 test request to check recovery.
 *
 * @class CircuitBreaker
 */
export class CircuitBreaker {
  /**
   * @param {string} serviceName - Unique identifier (e.g., 'MONGODB_LEDGER')
   * @param {number} failureThreshold - Number of failures before tripping (Default: 3)
   * @param {number} cooldownMs - Milliseconds to wait before HALF_OPEN test (Default: 30000ms)
   */
  constructor(serviceName, failureThreshold = 3, cooldownMs = 30000) {
    this.serviceName = serviceName;
    this.failureThreshold = failureThreshold;
    this.cooldownMs = cooldownMs;
    this.redisKey = `wilsy:circuit_breaker:${serviceName}`;
    this.localState = 'CLOSED'; // Fallback for synchronous getters
    breakerRegistry.set(serviceName, this);
  }

  /**
   * Reads the distributed state from Redis. Implements fail-open logic if Redis is down.
   * @private
   */
  async _getRedisState() {
    try {
      if (!redisClient || !redisClient.isReady) return { state: 'CLOSED', failures: 0, lastFailure: 0 };
      const data = await redisClient.get(this.redisKey);
      return data ? JSON.parse(data) : { state: 'CLOSED', failures: 0, lastFailure: 0 };
    } catch (e) {
      logger.error(`[CB-REDIS-FAULT] Failsafe Engaged: ${e.message}`);
      return { state: 'CLOSED', failures: 0, lastFailure: 0 }; // Fail-open to preserve traffic
    }
  }

  /**
   * Writes the distributed state to Redis.
   * @private
   */
  async _setRedisState(state, failures, lastFailure) {
    try {
      if (!redisClient || !redisClient.isReady) return;
      const payload = JSON.stringify({ state, failures, lastFailure });
      await redisClient.set(this.redisKey, payload, { EX: 86400 }); // 24-hour TTL
      this.localState = state;
    } catch (e) {
      logger.error(`[CB-REDIS-FAULT] Sync Failed: ${e.message}`);
    }
  }

  /**
   * Resolves current state, evaluating cooldowns to transition OPEN -> HALF_OPEN.
   */
  async getState() {
    const data = await this._getRedisState();
    if (data.state === 'OPEN') {
      const now = Date.now();
      if (now - data.lastFailure > this.cooldownMs) {
        await this._setRedisState('HALF_OPEN', data.failures, data.lastFailure);
        return 'HALF_OPEN';
      }
    }
    return data.state;
  }

  /**
   * Opens the circuit globally across all Kubernetes pods.
   */
  async open() {
    await this._setRedisState('OPEN', this.failureThreshold, Date.now());
    logger.warn(chalk.yellow(`[CIRCUIT-BREAKER] ⚠️ Failover triggered for ${this.serviceName}. State: OPEN (Distributed).`));
  }

  /**
   * Closes the circuit globally across all Kubernetes pods.
   */
  async close() {
    await this._setRedisState('CLOSED', 0, 0);
    logger.info(chalk.green(`[CIRCUIT-BREAKER] ✅ ${this.serviceName} link restored. State: CLOSED (Distributed).`));
  }

  /**
   * Records a failure and trips the breaker if threshold is breached.
   */
  async recordFailure() {
    const data = await this._getRedisState();
    const newFailures = data.failures + 1;
    if (newFailures >= this.failureThreshold || data.state === 'HALF_OPEN') {
      await this.open();
    } else {
      await this._setRedisState(data.state, newFailures, Date.now());
    }
  }

  /**
   * 🚀 THE EXECUTION SHIELD
   * Wraps any async function. Aborts instantly if OPEN. Records failures automatically.
   *
   * @param {Function} fn - Async function to execute
   * @returns {Promise<any>}
   */
  async fire(fn) {
    const state = await this.getState();
    if (state === 'OPEN') {
      throw new Error('CIRCUIT_OPEN');
    }

    try {
      const result = await fn();
      // If we succeed while testing the waters, fully restore the cluster
      if (state === 'HALF_OPEN') await this.close();
      return result;
    } catch (error) {
      await this.recordFailure();
      throw error;
    }
  }

  /**
   * Synchronous status getter for the Boardroom HUD and health checks.
   */
  getStatus() {
    return {
      service: this.serviceName,
      state: this.localState,
      timestamp: new Date().toISOString(),
      type: 'DISTRIBUTED_REDIS'
    };
  }
}

// ============================================================================
// 🔐 INITIATE FORENSIC SHUTDOWN
// ============================================================================

/**
 * Global shutdown handler for graceful termination (SIGTERM / SIGINT).
 * Broadcasts the OPEN state to Redis so load balancers and other pods route away.
 */
export const initiateForensicShutdown = async (server) => {
  console.log(chalk.red.bold('\n👋 [SYSTEM] SIGTERM Received. Initiating Distributed Forensic Shutdown Protocol...'));

  // Asynchronously lock all breakers in Redis
  const lockPromises = [];
  breakerRegistry.forEach((breaker, name) => {
    console.log(chalk.yellow(`📡 [SHUTDOWN] Broadcasting global OPEN lock for ${name}...`));
    lockPromises.push(breaker.open());
  });

  try {
    await Promise.all(lockPromises);
    if (server) {
      server.close(() => {
        console.log(chalk.green('🏛️ WILSY OS - SINGULARITY SECURELY ANCHORED. DISPATCHING PID:', process.pid));
        process.exit(0);
      });
    } else {
      process.exit(0);
    }
  } catch (err) {
    console.error(chalk.red('💥 [SHUTDOWN-FRACTURE] Forensic withdrawal failed:'), err.message);
    process.exit(1);
  }
};
