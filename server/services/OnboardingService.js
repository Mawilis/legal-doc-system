/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — UNIVERSAL ONBOARDING ENGINE [v34.2.0-MODEL-ALIGNED]                                                                      ║
 * ║ TRACE-AWARE GENESIS · ATOMIC PROVISIONING · HASHED API KEYS · SHA3-512 SEAL · MERKLE ROOT · RISK SIGNALS · OUTBOX-SAFE SIDE EFFECTS  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 34.2.0-MODEL-ALIGNED | PRODUCTION READY                                                                                    ║
 * ║ EPITOME: Institutional tenant genesis with cryptographic sealing, auto-subscription, risk signals (not hard blocks),                  ║
 * ║          secret-safe API keys, validated input, and platform-correct telemetry (tenant genesis ≠ client invoice pipeline).            ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/OnboardingService.js                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) — Mandated atomic genesis with zero-logic loss and secret hygiene.                            ║
 * ║ • AI Engineering — v34.0.0 baseline; v34.1.0: hashed API keys, input validation, safe session/regex, unique-index races,              ║
 * ║   risk signals vs hard anomalies, platform-only genesis telemetry, post-commit side-effect isolation. [2026-08-15]                    ║
 * ║ COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC6/CC7 · ISO 27001                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import mongoose from 'mongoose';
import { User } from '../models/userModel.js';
import { ApiKey } from '../models/api/ApiKey.js';
import Subscription from '../models/Subscription.js';

// Prefer Tenant (production). Fall back to TenantConfig if present in older trees.
let TenantModel = null;
try {
  const mod = await import('../models/Tenant.js');
  TenantModel = mod.default || mod.Tenant || null;
} catch {
  TenantModel = null;
}
if (!TenantModel) {
  try {
    const mod = await import('../models/TenantConfig.js');
    TenantModel = mod.default || mod.TenantConfig || null;
  } catch {
    TenantModel = null;
  }
}
if (!TenantModel) {
  throw new Error('ONBOARDING_BOOT: Tenant model unavailable (expected ../models/Tenant.js)');
}
import logger from '../utils/logger.js';
import auditLogger from '../utils/auditLogger.js';
import { notificationService } from './notificationService.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

// Optional metrics — never crash genesis if metrics module is absent or partial
let prometheusMetrics = null;
try {
  const mod = await import('../metrics/prometheusMetrics.js');
  prometheusMetrics = mod.default || mod.prometheusMetrics || mod;
} catch {
  prometheusMetrics = null;
}

// ─── Constants ───────────────────────────────────────────────────────────────
const ALLOWED_TIERS = Object.freeze(['BASIC', 'STANDARD', 'PROFESSIONAL', 'ENTERPRISE', 'SOVEREIGN']);
const ALLOWED_REGIONS = Object.freeze(['ZA', 'EU', 'US', 'UK', 'AE', 'SG', 'AU']);
const MIN_PASSWORD_LENGTH = 12;
const DEFAULT_TRIAL_DAYS = 30;

/** Consumer domains scored as elevated risk — never automatic hard-fail */
const ELEVATED_RISK_EMAIL_DOMAINS = new Set([
  'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
  'protonmail.com', 'mail.com', 'yandex.com', 'icloud.com', 'live.com',
]);

// ─── Validation ──────────────────────────────────────────────────────────────

/**
 * @param {unknown} value
 * @returns {string}
 */
function asTrimmedString(value) {
  return String(value ?? '').trim();
}

/**
 * Escape user input for safe RegExp construction.
 * @param {string} value
 * @returns {string}
 */
function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Normalize business name for uniqueness comparisons.
 * @param {string} name
 * @returns {string}
 */
function normalizeName(name) {
  return asTrimmedString(name).toUpperCase().replace(/\s+/g, ' ');
}

/**
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  // Practical production check (not full RFC)
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && email.length <= 254;
}

/**
 * Validate and normalize onboarding payload.
 * @param {Object} data
 * @returns {{ businessName: string, adminEmail: string, password: string, sector: string, tier: string, region: string, adminFirstName: string, adminLastName: string }}
 * @throws {Error} VALIDATION_ERROR
 */
function validateOnboardingPayload(data = {}) {
  const businessName = asTrimmedString(data.businessName);
  const adminEmail = asTrimmedString(data.adminEmail).toLowerCase();
  const password = String(data.password ?? '');
  const sector = asTrimmedString(data.sector) || 'GENERAL';
  const tier = asTrimmedString(data.tier || 'BASIC').toUpperCase();
  const region = asTrimmedString(data.region || 'ZA').toUpperCase();
  const adminFirstName = asTrimmedString(data.adminFirstName) || 'Sovereign';
  const adminLastName = asTrimmedString(data.adminLastName) || 'Architect';

  const errors = [];
  if (!businessName || businessName.length < 2) errors.push('businessName is required (min 2 chars)');
  if (businessName.length > 200) errors.push('businessName exceeds 200 chars');
  if (!adminEmail || !isValidEmail(adminEmail)) errors.push('adminEmail must be a valid email');
  if (!password || password.length < MIN_PASSWORD_LENGTH) {
    errors.push(`password must be at least ${MIN_PASSWORD_LENGTH} characters`);
  }
  if (!ALLOWED_TIERS.includes(tier)) errors.push(`tier must be one of: ${ALLOWED_TIERS.join(', ')}`);
  if (!ALLOWED_REGIONS.includes(region)) errors.push(`region must be one of: ${ALLOWED_REGIONS.join(', ')}`);

  if (errors.length) {
    const err = new Error(`VALIDATION_ERROR: ${errors.join('; ')}`);
    err.code = 'VALIDATION_ERROR';
    err.details = errors;
    throw err;
  }

  return {
    businessName,
    adminEmail,
    password,
    sector,
    tier,
    region,
    adminFirstName,
    adminLastName,
  };
}

// ─── Risk signals (soft — stored, not hard-blocked) ──────────────────────────

/**
 * @param {string} email
 * @returns {boolean}
 */
function isElevatedRiskEmail(email) {
  const domain = email.split('@')[1]?.toLowerCase();
  return domain ? ELEVATED_RISK_EMAIL_DOMAINS.has(domain) : false;
}

/**
 * Pre-flight risk signals. Does not abort genesis unless policy later hard-fails.
 * @param {{ businessName: string, adminEmail: string }} payload
 * @param {import('mongoose').ClientSession|null} session
 * @returns {Promise<string[]>}
 */
async function collectRiskSignals(payload, session) {
  const signals = [];
  const normalized = normalizeName(payload.businessName);
  const nameQuery = TenantModel.findOne({
    $or: [
      { nameNormalized: normalized },
      { name: { $regex: new RegExp(`^${escapeRegex(payload.businessName)}$`, 'i') } },
    ],
  }).lean();
  if (session) nameQuery.session(session);
  const existingTenant = await nameQuery;
  if (existingTenant) signals.push('DUPLICATE_NAME');

  if (isElevatedRiskEmail(payload.adminEmail)) signals.push('ELEVATED_RISK_EMAIL_DOMAIN');

  return signals;
}

// ─── Cryptography ────────────────────────────────────────────────────────────

/**
 * @param {string|Buffer} data
 * @returns {string} lowercase hex
 */
function sha3_512(data) {
  return crypto.createHash('sha3-512').update(data).digest('hex');
}

/**
 * Hash API key for at-rest storage (raw key returned once to caller only).
 * @param {string} rawKey
 * @returns {string}
 */
function hashApiKey(rawKey) {
  return sha3_512(rawKey);
}

/**
 * Simplified binary Merkle root over string leaves (documented algorithm).
 * Odd nodes are promoted unchanged. Suitable as genesis fingerprint — not a
 * substitute for a full audit Merkle log unless leaves + algorithm are archived.
 * @param {string[]} values
 * @returns {string}
 */
function computeMerkleRoot(values) {
  if (!Array.isArray(values) || values.length === 0) return '';
  let layer = values.map((v) => sha3_512(String(v)));
  while (layer.length > 1) {
    const next = [];
    for (let i = 0; i < layer.length; i += 2) {
      if (i + 1 < layer.length) next.push(sha3_512(layer[i] + layer[i + 1]));
      else next.push(layer[i]);
    }
    layer = next;
  }
  return layer[0] || '';
}

/**
 * @returns {boolean}
 */
function isReplicaSetTopology() {
  try {
    const type = mongoose.connection.getClient()?.topology?.description?.type;
    return Boolean(type && type !== 'Single');
  } catch {
    return false;
  }
}

/**
 * @template T
 * @param {import('mongoose').Query<T>} query
 * @param {import('mongoose').ClientSession|null} session
 * @returns {import('mongoose').Query<T>}
 */
function withSession(query, session) {
  return session ? query.session(session) : query;
}

// ─── Service ─────────────────────────────────────────────────────────────────

class OnboardingService {
  /**
   * Initialise a sovereign tenant (institutional shard).
   *
   * @async
   * @param {Object} data
   * @param {string} data.businessName
   * @param {string} data.adminEmail
   * @param {string} data.password
   * @param {string} [data.sector]
   * @param {string} [data.tier='BASIC']
   * @param {string} [data.region='ZA']
   * @param {string} [data.adminFirstName]
   * @param {string} [data.adminLastName]
   * @param {string|null} [traceId]
   * @returns {Promise<Object>}
   */
  async initializeSovereignTenant(data, traceId = null) {
    const payload = validateOnboardingPayload(data);
    const currentTrace = traceId || `GEN-${crypto.randomBytes(6).toString('hex').toUpperCase()}`;

    await broadcastTelemetry(
      'WILSY_GLOBAL_ROOT',
      'TENANT_GENESIS_INITIATED',
      'SYSTEM_ORCHESTRATOR',
      'PROVISION_SHARD',
      {
        businessName: payload.businessName,
        tier: payload.tier,
        region: payload.region,
        traceId: currentTrace,
      }
    );

    const useTxn = isReplicaSetTopology();
    let session = null;
    if (useTxn) {
      session = await mongoose.startSession();
      session.startTransaction();
      logger.info(`[GENESIS] ATOMIC_TRANSACTION_INIT trace=${currentTrace}`);
    } else {
      logger.warn(`[GENESIS] LINEAR_PROVISIONING (non-replica) trace=${currentTrace}`);
    }

    const opts = session ? { session } : {};

    try {
      // Risk signals (soft)
      const riskSignals = await collectRiskSignals(payload, session);

      // Unique tenantId
      const baseId = payload.businessName
        .toUpperCase()
        .replace(/[^A-Z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .substring(0, 20) || 'TENANT';
      let tenantId = baseId;
      let counter = 0;
      // Cap loop; unique index is ultimate authority
      while (counter < 50) {
        // eslint-disable-next-line no-await-in-loop
        const hit = await withSession(
          TenantModel.findOne({ tenantId }).lean(),
          session
        );
        if (!hit) break;
        counter += 1;
        tenantId = `${baseId}_${counter}`;
      }
      if (counter >= 50) {
        const err = new Error('TENANT_ID_EXHAUSTED: could not allocate unique tenantId');
        err.code = 'TENANT_ID_EXHAUSTED';
        throw err;
      }

      const tenantData = {
        tenantId,
        name: payload.businessName,
        nameNormalized: normalizeName(payload.businessName),
        legalName: payload.businessName,
        legalEntity: payload.businessName,
        businessName: payload.businessName,
        contactEmail: payload.adminEmail,
        email: payload.adminEmail,
        jurisdiction: payload.region,
        country: payload.region,
        sellerJurisdiction: payload.region,
        status: 'ACTIVE',
        riskSignals,
        anomalyFlags: riskSignals,
        genesisTraceId: currentTrace,
        onboardingProofHash: '',
        genesisMerkleRoot: '',
        subscription: {
          tier: ['BASIC', 'PRO', 'ULTRA', 'ENTERPRISE'].includes(payload.tier)
            ? payload.tier
            : payload.tier === 'PROFESSIONAL'
              ? 'PRO'
              : payload.tier === 'SOVEREIGN' || payload.tier === 'ENTERPRISE'
                ? 'ENTERPRISE'
                : 'BASIC',
          isActive: true,
          trialExpires: new Date(Date.now() + DEFAULT_TRIAL_DAYS * 24 * 60 * 60 * 1000),
        },
        metadata: {
          industry: 'GENERAL',
          region: payload.region,
          complianceFrameworks: [
            ...(payload.region === 'ZA' ? ['POPIA'] : []),
            ...(['EU', 'UK'].includes(payload.region) ? ['GDPR'] : []),
          ],
          dataResidency: payload.region,
          onboardedAt: new Date(),
        },
        billingDefaults: {
          currency: 'ZAR',
          jurisdiction: payload.region,
          paymentTermsDays: 30,
          defaultTaxRate: payload.region === 'ZA' ? 0.15 : 0,
          taxType: payload.region === 'ZA' ? 'VAT' : 'NONE',
        },
      };

      let tenant;
      try {
        const created = await TenantModel.create([tenantData], opts);
        tenant = created[0];
      } catch (dupErr) {
        if (dupErr?.code === 11000) {
          const err = new Error('DUPLICATE_TENANT: tenantId or name already exists');
          err.code = 'DUPLICATE_TENANT';
          err.cause = dupErr;
          throw err;
        }
        throw dupErr;
      }

      const dbTenantId = tenant._id;
      const sovereignTenantId = tenant.tenantId;

      // Sovereign owner
      const newUser = new User({
        email: payload.adminEmail,
        password: payload.password, // hashed by User model pre-save
        firstName: payload.adminFirstName,
        lastName: payload.adminLastName,
        role: 'tenant_owner',
        tenantId: dbTenantId,
        isActive: true,
        securityClearance: 'omega',
      });

      if (typeof newUser.appendForensicEntry === 'function') {
        await newUser.appendForensicEntry(
          'TENANT_OWNER_GENESIS',
          'SYSTEM_ORCHESTRATOR',
          { action: 'Provisioned as initial Sovereign Architect', traceId: currentTrace },
          currentTrace
        );
      }
      await newUser.save(opts);

      // API key — store HASH only; return raw once
      const rawKey = `WOS_${crypto.randomBytes(32).toString('hex')}`;
      const keyHash = hashApiKey(rawKey);
      const keyPrefix = rawKey.slice(0, 12);

      await ApiKey.create(
        [
          {
            keyHash,
            keyPrefix,
            // Do not persist raw `key` if schema still has it — prefer keyHash only
            tenantId: dbTenantId,
            tier: payload.tier,
            name: `${payload.businessName} MASTER_KEY`,
            isActive: true,
            createdTraceId: currentTrace,
          },
        ],
        opts
      );

      // Subscription trial
      const startDate = new Date();
      const endDate = new Date(Date.now() + DEFAULT_TRIAL_DAYS * 24 * 60 * 60 * 1000);
      // Subscription model: tenantId is STRING shard id; status lowercase; plan/planId/amount required
      const planId = `PLAN_${payload.tier}_MONTHLY`;
      const subscriptionDocs = await Subscription.create(
        [
          {
            tenantId: sovereignTenantId, // string shard id
            tenantRef: dbTenantId, // ObjectId
            plan: 'FOUNDER_ENTERPRISE',
            planId,
            planName: `${payload.tier} trial`,
            billingFrequency: 'monthly',
            amount: 0,
            currency: 'ZAR',
            status: 'active',
            startDate,
            trialEndDate: endDate,
            currentPeriodStart: startDate,
            currentPeriodEnd: endDate,
            nextBillingAt: endDate,
            onboardingRef: currentTrace,
            billingMode: 'PLATFORM',
            idempotencyKey: `ONBOARD-${currentTrace}`,
            traceId: currentTrace,
            metadata: { genesis: true, tier: payload.tier },
            tags: ['onboarding', 'genesis'],
          },
        ],
        opts
      );
      const subscriptionId = subscriptionDocs[0]._id;

      // Cryptographic seal (never include raw API key in durable audit leaves)
      const genesisValues = [
        tenantId,
        payload.adminEmail,
        keyPrefix, // prefix only — not full secret
        String(subscriptionId),
        currentTrace,
        new Date().toISOString(),
      ];
      const proofHash = sha3_512(genesisValues.join('|'));
      const merkleRoot = computeMerkleRoot(genesisValues);

      tenant.onboardingProofHash = proofHash;
      tenant.genesisMerkleRoot = merkleRoot;
      await tenant.save(opts);

      if (session) {
        await session.commitTransaction();
        session.endSession();
        session = null;
      }

      // ── Post-commit side effects (isolated — must not roll back committed state) ──
      try {
        if (prometheusMetrics?.incrementOnboardingCounter) {
          // Tenant institutional genesis is PLATFORM onboarding, not client-invoice genesis
          prometheusMetrics.incrementOnboardingCounter('platform');
        }
        if (prometheusMetrics?.incrementOnboardingCounterWithTier) {
          prometheusMetrics.incrementOnboardingCounterWithTier(payload.tier);
        }

        await broadcastTelemetry(
          'WILSY_GLOBAL_ROOT',
          'TENANT_GENESIS_SUCCESS',
          'SYSTEM_ORCHESTRATOR',
          'GENESIS_COMPLETE',
          {
            tenantId: sovereignTenantId,
            tier: payload.tier,
            region: payload.region,
            riskSignals,
            traceId: currentTrace,
          }
        );

        // Tenant-scoped pulse (tenant as subject) — not "client invoice pipeline"
        await broadcastTelemetry(
          sovereignTenantId,
          'TENANT_SHARD_READY',
          'TENANT_OWNER',
          'GENESIS_COMPLETE',
          {
            tenantId: sovereignTenantId,
            tier: payload.tier,
            traceId: currentTrace,
          }
        );

        await notificationService.sendNotification({
          tenantId: 'WILSY_GLOBAL_ROOT',
          userId: 'SYSTEM',
          type: 'SYSTEM_ALERT',
          channels: ['EMAIL'],
          recipients: { email: payload.adminEmail },
          data: {
            title: 'Sovereign Environment Live',
            body: `Your institution ${payload.businessName} is live. Trace: ${currentTrace}. Store your API key securely — it is shown only once.`,
          },
        });

        auditLogger.audit('Institutional Onboarding Complete', {
          traceId: currentTrace,
          tenantId: sovereignTenantId,
          tier: payload.tier,
          region: payload.region,
          riskSignals,
          subscriptionId: String(subscriptionId),
          proofHash,
          merkleRoot,
          keyPrefix,
          // never audit rawKey
          timestamp: new Date().toISOString(),
        });
      } catch (sideErr) {
        // Committed state stands; surface side-effect failure in logs only
        logger.error(
          `[GENESIS] post-commit side effects failed trace=${currentTrace}: ${sideErr.message}`
        );
      }

      return {
        success: true,
        tenantId: dbTenantId,
        sovereignId: sovereignTenantId,
        subscriptionId,
        apiKey: rawKey, // one-time return of secret
        apiKeyPrefix: keyPrefix,
        traceId: currentTrace,
        riskSignals,
        anomalies: riskSignals, // backward-compatible
        proofHash,
        merkleRoot,
        message: 'SOVEREIGN_ENVIRONMENT_LIVE',
        warning:
          riskSignals.length > 0
            ? `Provisioned with risk signals: ${riskSignals.join(', ')}`
            : undefined,
      };
    } catch (err) {
      if (session) {
        try {
          await session.abortTransaction();
        } catch (abortErr) {
          logger.error(`[GENESIS] abort failed: ${abortErr.message}`);
        }
        try {
          session.endSession();
        } catch {
          /* ignore */
        }
      }

      logger.error(`[GENESIS-FAILURE] trace=${currentTrace} ${err.message}`);

      try {
        await broadcastTelemetry(
          'WILSY_GLOBAL_ROOT',
          'TENANT_GENESIS_FAILURE',
          'SYSTEM_ORCHESTRATOR',
          'GENESIS_ABORTED',
          {
            error: err.message,
            code: err.code || 'GENESIS_ERROR',
            traceId: currentTrace,
          }
        );
      } catch {
        /* ignore */
      }

      throw err;
    }
  }
}

export const onboardingService = new OnboardingService();
export default onboardingService;
