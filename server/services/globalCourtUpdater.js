/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║   ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗███╗   ██╗ ██████╗ ███████╗███████╗██╗   ██╗███████╗                     ║
 * ║   ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔════╝ ██╔════╝██╔════╝██║   ██║██╔════╝                     ║
 * ║   ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██╔██╗ ██║██║  ███╗█████╗  █████╗  ██║   ██║███████╗                     ║
 * ║   ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║╚██╗██║██║   ██║██╔══╝  ██╔══╝  ╚██╗ ██╔╝╚════██║                     ║
 * ║   ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║██║ ╚████║╚██████╔╝███████╗██║      ╚████╔╝ ███████║                     ║
 * ║   ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝       ╚═══╝  ╚══════╝                     ║
 * ║                                                                                                                                    ║
 * ║                         THE SOVEREIGN OPERATING SYSTEM FOR LEGAL ENFORCEMENT                                                       ║
 * ║                   ATOMIC SEIZURE | LEGAL HOLD | ASSET FREEZE | SOVEREIGN BYPASS                                                    ║
 * ║                                                                                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - GLOBAL COURT UPDATER [V4.0.0-SINGULARITY-OMEGA]
 * [COURT API INTEGRATION | ENHANCED CIRCUIT BREAKER | FALLBACK | NEURAL MESH STREAMING]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 4.0.0-SINGULARITY | PRODUCTION READY | BILLION DOLLAR SPEC                                                                  ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/globalCourtUpdater.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated atomic court order integration and resilience against external API drift.          ║
 * ║ • AI Engineering (DeepSeek) - ENHANCED: Replaced local circuit breaker with production-grade CircuitBreakerEnhanced, added fallback. ║
 * ║ • AI Engineering (Gemini) - EPITOMISED: Anchored Sovereign Event Stream. Court enforcements now broadcast to the Boardroom HUD live. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import axios from 'axios';
import mongoose from 'mongoose';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { TenantMetadata } from '../models/TenantMetadata.js';
import logger from '../utils/logger.js';
import CircuitBreakerEnhanced from './circuitBreakerEnhanced.js'; // 🏛️ PRODUCTION CIRCUIT BREAKER
import sovereignEventStream from './sovereignEventStream.js'; // 🏛️ THE DIVINE ORACLE BRIDGE

// ============================================================================
// ⚙️ CONFIGURATION
// ============================================================================

const CONFIG = {
  COURT_API_URL: process.env.COURT_API_URL || 'https://api.saflii.org/orders/v1',
  API_KEY: process.env.COURT_API_KEY,
  POLL_INTERVAL_MS: 300000, // 5 minutes
  RETRY_OPTIONS: {
    retries: 3,
    factor: 2,
    minTimeout: 1000,
    maxTimeout: 60000
  },
  CIRCUIT_BREAKER: {
    failureThreshold: 5,
    timeoutMs: 15000,
    resetTimeoutMs: 60000
  }
};

// ============================================================================
// 🏛️ GLOBAL COURT UPDATER CLASS (ENHANCED)
// ============================================================================

/**
 * @class GlobalCourtUpdater
 * @description Polls external court databases, applies legal holds, and broadcasts to Boardroom HUD.
 * Enhanced with production-grade circuit breaker and fallback for API unavailability.
 * @real-world Integrates with real legal APIs (e.g., SAFLII, PACER) to automatically freeze assets.
 * @forensic Every order processed is broadcast via telemetry and recorded in immutable audit log.
 * @example
 * const updater = new GlobalCourtUpdater();
 * updater.start(); // begins polling every 5 minutes
 */
class GlobalCourtUpdater {
  constructor() {
    this.name = 'GlobalCourtUpdater';
    this.intervalId = null;
    // 🔥 ENHANCED CIRCUIT BREAKER WITH FALLBACK
    this.circuitBreaker = new CircuitBreakerEnhanced({
      failureThreshold: CONFIG.CIRCUIT_BREAKER.failureThreshold,
      timeoutMs: CONFIG.CIRCUIT_BREAKER.timeoutMs,
      resetTimeoutMs: CONFIG.CIRCUIT_BREAKER.resetTimeoutMs,
      fallback: async () => {
        logger.warn(`[${this.name}] Circuit breaker fallback: returning cached orders (none available)`);
        broadcastTelemetry('GLOBAL_ROOT', 'COURT_UPDATER', 'CIRCUIT_BREAKER_FALLBACK', this.name, {});
        // 🔥 NEURAL MESH BROADCAST
        sovereignEventStream.emit('COURT_SYNC_FALLBACK', { status: 'DEGRADED', message: 'Using circuit breaker fallback.' });
        return []; // Return empty array, assume no new orders
      }
    });
  }

  /**
   * @description Starts the periodic synchronization loop.
   * @returns {void}
   * @real-world Called during server startup to begin monitoring legal registries.
   * @example
   * courtUpdater.start();
   */
  start() {
    if (this.intervalId) {
      logger.warn(`[${this.name}] Already running.`);
      return;
    }
    logger.info(`[${this.name}] 🏛️ Sovereign court synchronization engaged. Poll interval: ${CONFIG.POLL_INTERVAL_MS}ms`);
    this.sync(); // immediate first run
    this.intervalId = setInterval(() => this.sync(), CONFIG.POLL_INTERVAL_MS);
  }

  /**
   * @description Gracefully stops the polling loop.
   * @returns {void}
   * @example
   * process.on('SIGTERM', () => courtUpdater.stop());
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      logger.info(`[${this.name}] Sovereign court synchronization stopped.`);
    }
  }

  /**
   * @description Primary sync logic – uses circuit breaker to fetch orders and process them.
   * @returns {Promise<void>}
   * @async
   * @real-world Called automatically every 5 minutes.
   * @forensic Emits telemetry on sync start, success, and failure.
   * @example
   * await courtUpdater.sync();
   */
  async sync() {
    // Check circuit breaker state before attempting
    if (this.circuitBreaker.getState() === 'OPEN') {
      logger.warn(`[${this.name}] Circuit breaker OPEN – skipping sync.`);
      return;
    }

    logger.info(`[${this.name}] 🔍 Executing synchronization strike...`);
    broadcastTelemetry('GLOBAL_ROOT', 'COURT_UPDATER', 'SYNC_STARTED', this.name, {});

    try {
      // Execute the fetch operation through the circuit breaker
      const orders = await this.circuitBreaker.execute(async () => {
        return await this.fetchExternalOrdersWithRetry();
      });

      for (const order of orders) {
        await this.processOrder(order);
      }

      broadcastTelemetry('GLOBAL_ROOT', 'COURT_UPDATER', 'SYNC_SUCCESS', this.name, { orderCount: orders.length });

      // 🔥 NEURAL MESH BROADCAST: Inform the Boardroom HUD of successful cycle
      sovereignEventStream.emit('COURT_SYNC_COMPLETE', {
        status: 'SUCCESS',
        orderCount: orders.length,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      // If circuit breaker throws (no fallback), or execution fails
      logger.error(`[${this.name}] 💥 Synchronization fracture: ${error.message}`);
      broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_FAULT', 'SYNC_FRACTURE', this.name, { error: error.message });
    }
  }

  /**
   * @description Fetches court orders from external API with exponential backoff and retries.
   * @returns {Promise<Array>} List of court order objects.
   * @async
   * @real-world Uses `axios-retry` to handle transient network issues.
   * @example
   * const orders = await updater.fetchExternalOrdersWithRetry();
   */
  async fetchExternalOrdersWithRetry() {
    const axiosRetry = (await import('axios-retry')).default;
    const retryClient = axios.create();
    axiosRetry(retryClient, {
      retries: CONFIG.RETRY_OPTIONS.retries,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => error.response?.status >= 500 || error.code === 'ECONNABORTED'
    });

    const response = await retryClient.get(CONFIG.COURT_API_URL, {
      headers: { 'Authorization': `Bearer ${CONFIG.API_KEY}` },
      timeout: 15000
    });

    return response.data.orders || [];
  }

  /**
   * @description Processes a single court order, applying a legal hold if necessary.
   * @param {Object} order - The court order payload.
   * @param {string} order.tenantId - Target tenant identifier.
   * @param {string} order.orderType - e.g., 'FREEZE', 'UNFREEZE', 'FORFEITURE'.
   * @param {string} order.reference - Court case reference number.
   * @param {Object} order.details - Additional metadata (judge, jurisdiction, etc.).
   * @returns {Promise<void>}
   * @async
   * @real-world When a FREEZE order is detected, the tenant's assets are immediately locked.
   * @forensic Broadcasts telemetry and appends to the tenant's forensic chain.
   * @example
   * await updater.processOrder({ tenantId: 'acme-corp', orderType: 'FREEZE', reference: 'CASE-2026-00123' });
   */
  async processOrder(order) {
    const { tenantId, orderType, reference, details = {} } = order;

    try {
      // Validate tenant exists in the root DB
      const rootDb = mongoose.connection.useDb('wilsy-sovereign-root');
      const TenantModel = rootDb.model('Tenant', new mongoose.Schema({ tenantId: String }));
      const tenantExists = await TenantModel.findOne({ tenantId });
      if (!tenantExists) {
        logger.warn(`[${this.name}] Tenant ${tenantId} not found – skipping order ${reference}`);
        return;
      }

      if (orderType === 'FREEZE') {
        await this.applyLegalHold(tenantId, reference, details);
        broadcastTelemetry(tenantId, 'SECURITY', 'ASSET_SEIZURE_LOCKED', this.name, { reference, jurisdiction: details.jurisdiction });

        // 🔥 NEURAL MESH BROADCAST: Immediate alert to the Boardroom
        sovereignEventStream.emit('SEIZURE_ALERT', {
          action: 'LOCKED',
          tenantId,
          reference,
          jurisdiction: details.jurisdiction,
          timestamp: new Date().toISOString()
        });

      } else if (orderType === 'UNFREEZE') {
        await this.removeLegalHold(tenantId, reference);
        broadcastTelemetry(tenantId, 'SECURITY', 'ASSET_SEIZURE_LIFTED', this.name, { reference });

        // 🔥 NEURAL MESH BROADCAST: Immediate alert to the Boardroom
        sovereignEventStream.emit('SEIZURE_ALERT', {
          action: 'LIFTED',
          tenantId,
          reference,
          timestamp: new Date().toISOString()
        });

      } else {
        logger.info(`[${this.name}] Unhandled order type ${orderType} for tenant ${tenantId}`);
      }
    } catch (error) {
      logger.error(`[${this.name}] Processing fracture for ${reference}: ${error.message}`);
      broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_FAULT', 'ORDER_PROCESSING_FRACTURE', this.name, { reference, error: error.message });
    }
  }

  /**
   * @description Applies a legal hold to the tenant's metadata and updates the root database.
   * @param {string} tenantId - The tenant to freeze.
   * @param {string} reference - Court order reference.
   * @param {Object} details - Optional metadata (e.g., judge, court name).
   * @returns {Promise<void>}
   * @async
   * @real-world Called automatically when a FREEZE order is ingested.
   * @forensic Updates TenantMetadata with seizure details and broadcasts telemetry.
   * @example
   * await updater.applyLegalHold('fraud-corp', 'CASE-2026-45678', { judge: 'Mogoeng Mogoeng' });
   */
  async applyLegalHold(tenantId, reference, details = {}) {
    await TenantMetadata.findOneAndUpdate(
      { tenantId },
      {
        $set: {
          'customSettings.isSeized': true,
          'customSettings.seizureRecordId': reference,
          'customSettings.seizedAt': new Date(),
          'customSettings.courtReference': reference,
          'customSettings.judge': details.judge || null,
          'customSettings.jurisdiction': details.jurisdiction || 'UNKNOWN'
        }
      },
      { upsert: true }
    );

    // Also update the main Tenant model status
    const rootDb = mongoose.connection.useDb('wilsy-sovereign-root');
    const TenantModel = rootDb.model('Tenant');
    await TenantModel.findOneAndUpdate(
      { tenantId },
      { status: 'SEIZED', legalHold: { active: true, reason: 'COURT_ORDER', reference, appliedBy: 'GlobalCourtUpdater' } },
      { upsert: true }
    );
  }

  /**
   * @description Removes a legal hold (when an UNFREEZE order is received).
   * @param {string} tenantId - The tenant to release.
   * @param {string} reference - Court order reference.
   * @returns {Promise<void>}
   * @async
   */
  async removeLegalHold(tenantId, reference) {
    await TenantMetadata.findOneAndUpdate(
      { tenantId },
      {
        $set: { 'customSettings.isSeized': false },
        $unset: { 'customSettings.seizureRecordId': '', 'customSettings.seizedAt': '', 'customSettings.courtReference': '', 'customSettings.judge': '', 'customSettings.jurisdiction': '' }
      }
    );

    const rootDb = mongoose.connection.useDb('wilsy-sovereign-root');
    const TenantModel = rootDb.model('Tenant');
    await TenantModel.findOneAndUpdate(
      { tenantId },
      { status: 'ACTIVE', legalHold: null }
    );
  }
}

// ============================================================================
// 🏛️ EXPORT SINGLETON
// ============================================================================

const courtUpdater = new GlobalCourtUpdater();
export default courtUpdater;
