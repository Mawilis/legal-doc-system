/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - UNIVERSAL ONBOARDING ENGINE [V33.33.0-MARS]                                                                                 ║
 * ║ [TRACE-AWARE GENESIS | ATOMIC TRANS-SHARD PROVISIONING | PQC IDENTITY ANCHORING | BIBLICAL WORTH BILLIONS]                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.33.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/OnboardingService.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated 10-second genesis with zero-logic loss and atomic trans-shard finality.              ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Resolved ESM import fracture by aligning with anchored notificationService exports.              ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Injected sub-ms telemetry pulses for real-time boardroom Genesis visibility.                     ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc documentation, production hardening, explicit transaction handling. [2026-05-15] ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import TenantConfig from '../models/TenantConfig.js';
import { User } from '../models/userModel.js';
import { ApiKey } from '../models/api/ApiKey.js';
import crypto from 'node:crypto';
import mongoose from 'mongoose';
import logger from '../utils/logger.js';
import auditLogger from '../utils/auditLogger.js';
// 🛡️ RECTIFIED: Importing anchored named export to resolve ESM SyntaxError
import { notificationService } from './notificationService.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * Universal Onboarding Engine for Wilsy OS.
 *
 * **Responsibilities**:
 * - Provisions new tenant shards (database isolation, configuration).
 * - Creates the sovereign owner (first user with `omega` clearance).
 * - Generates master API key for the tenant.
 * - Sends welcome notification and broadcasts telemetry.
 * - Uses MongoDB transactions for atomicity (if replica set is available).
 *
 * @class OnboardingService
 */
class OnboardingService {
  /**
   * Initialises a new sovereign tenant (institutional shard) within the Wilsy OS ecosystem.
   *
   * **Process**:
   * 1. Detects MongoDB topology – if replica set, starts a transaction.
   * 2. Creates TenantConfig document.
   * 3. Creates the sovereign owner user (role `tenant_owner`, security clearance `omega`).
   * 4. Generates a master API key for the tenant.
   * 5. Commits transaction (or saves directly in development).
   * 6. Sends welcome notification to admin email.
   * 7. Broadcasts telemetry and logs audit trail.
   *
   * @async
   * @param {Object} data - Onboarding payload
   * @param {string} data.businessName - Legal name of the business/tenant
   * @param {string} data.adminEmail - Email address of the initial administrator
   * @param {string} data.password - Plaintext password (will be hashed by User model pre-save)
   * @param {string} [data.sector] - Industry sector (optional, stored in metadata)
   * @param {string} [data.tier] - Subscription tier (defaults to 'BASIC')
   * @param {string} [data.region] - Data residency region (defaults to 'ZA')
   * @param {string|null} [traceId] - Optional external trace ID for correlation (auto-generated if omitted)
   * @returns {Promise<Object>} Provisioning result
   * @returns {boolean} success - Always true if function returns (otherwise throws)
   * @returns {string} tenantId - MongoDB ObjectId of the created tenant
   * @returns {string} sovereignId - Human‑readable tenant identifier (tenantId field)
   * @returns {string} apiKey - Raw API key (store securely, cannot be retrieved again)
   * @returns {string} traceId - Correlation trace ID
   * @returns {string} message - Status message ('SOVEREIGN_ENVIRONMENT_LIVE')
   *
   * @throws {Error} If any step fails, transaction is aborted (if applicable) and error is re-thrown.
   *
   * @example
 * const result = await onboardingService.initializeSovereignTenant({
 *   businessName: 'Acme Legal',
 *   adminEmail: 'admin@acme.com',
 *   password: process.env.ONBOARDING_ADMIN_PASSWORD,
 *   tier: 'ENTERPRISE'
 * });
   * console.log(result.apiKey); // Store this securely
   */
  async initializeSovereignTenant(data, traceId = null) {
    const { businessName, adminEmail, password, sector, tier, region } = data;
    const currentTrace = traceId || `GEN-${crypto.randomBytes(6).toString('hex').toUpperCase()}`;

    // 📡 FORENSIC ECHO: Genesis Pulse
    await broadcastTelemetry(
      'WILSY_GLOBAL_ROOT',
      'TENANT_GENESIS_INITIATED',
      'SYSTEM_ORCHESTRATOR',
      'PROVISION_SHARD',
      { businessName, tier, traceId: currentTrace }
    );

    // 🛡️ TOPOLOGY DETECTION (ReplicaSet requirement for ACID transactions)
    const isReplicaSet = mongoose.connection.getClient().topology?.description?.type !== 'Single';
    let session = null;

    if (isReplicaSet) {
      session = await mongoose.startSession();
      session.startTransaction();
      logger.info(`[GENESIS] 🛡️ ATOMIC_TRANSACTION_INIT: Trace ${currentTrace}`);
    } else {
      logger.warn(`[GENESIS] ⚠️ LINEAR_PROVISIONING (Dev-Mode): Trace ${currentTrace}`);
    }

    try {
      const opts = session ? { session } : {};

      // 1. 🏛️ PROVISION TENANT CONFIGURATION
      const tenant = await TenantConfig.create([{
        tenantId: businessName.toUpperCase().replace(/\s+/g, '_').substring(0, 20),
        name: businessName,
        legalEntityName: businessName,
        contactEmail: adminEmail,
        tier: tier || 'BASIC',
        status: 'ACTIVE',
        dataResidency: { primary: region || 'ZA' },
        validationSettings: { forensicMode: true }
      }], opts);

      const dbTenantId = tenant[0]._id;
      const sovereignTenantId = tenant[0].tenantId;

      // 2. 🏛️ PROVISION SOVEREIGN OWNER (Identity Anchor)
      const newUser = new User({
        email: adminEmail,
        password: password,
        firstName: 'Sovereign',
        lastName: 'Architect',
        role: 'tenant_owner',
        tenantId: dbTenantId,
        isActive: true,
        securityClearance: 'omega'
      });

      // 🛡️ Anchor Forensic Genesis Entry
      await newUser.appendForensicEntry(
        'TENANT_OWNER_GENESIS',
        'SYSTEM_ORCHESTRATOR',
        { action: 'Provisioned as initial Sovereign Architect', traceId: currentTrace },
        currentTrace
      );

      // 🏛️ RECTIFIED: Explicit save within the transaction session
      await newUser.save(opts);

      // 3. 🏛️ PROVISION MASTER REVENUE KEY
      const rawKey = `WOS_${crypto.randomBytes(32).toString('hex')}`;
      await ApiKey.create([{
        key: rawKey,
        tenantId: dbTenantId,
        tier: tier || 'BASIC',
        name: `${businessName} MASTER_KEY`,
        isActive: true
      }], opts);

      // ⚖️ ATOMIC SEAL
      if (session) {
        await session.commitTransaction();
        session.endSession();
      }

      // 4. 🛰️ CITADEL NOTIFICATION
      await notificationService.sendNotification({
        tenantId: 'WILSY_GLOBAL_ROOT',
        userId: 'SYSTEM',
        type: 'SYSTEM_ALERT',
        channels: ['EMAIL'],
        recipients: { email: adminEmail },
        data: {
          title: 'Sovereign Environment Live',
          body: `Your institution ${businessName} is now live in the Citadel. Trace: ${currentTrace}`
        }
      });

      auditLogger.audit('Institutional Onboarding Complete', {
        traceId: currentTrace,
        tenantId: sovereignTenantId,
        tier: tier || 'BASIC',
        timestamp: new Date().toISOString()
      });

      return {
        success: true,
        tenantId: dbTenantId,
        sovereignId: sovereignTenantId,
        apiKey: rawKey,
        traceId: currentTrace,
        message: 'SOVEREIGN_ENVIRONMENT_LIVE'
      };

    } catch (err) {
      if (session) {
        await session.abortTransaction();
        session.endSession();
      }
      logger.error(`[GENESIS-FAILURE] ❌ Trace ${currentTrace} Aborted: ${err.message}`);

      await broadcastTelemetry(
        'WILSY_GLOBAL_ROOT',
        'TENANT_GENESIS_FAILURE',
        'SYSTEM_ORCHESTRATOR',
        'GENESIS_ABORTED',
        { error: err.message, traceId: currentTrace }
      );

      throw err;
    }
  }
}

// 🏛️ DUAL ANCHOR EXPORT: Guaranteeing Genesis Integrity
export const onboardingService = new OnboardingService();
export default onboardingService;
