/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM INTELLIGENCE SERVICE                                                                                    ║
 * ║ BOARDROOM POSTURE | TELEMETRY | COMPLIANCE | GOVERNANCE | REVENUE | PREDICTIVE SCORING                                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign CRM intelligence service.
 */

import crypto from 'crypto';
import mongoose from 'mongoose';
import {
  CRMComplianceReceipt,
  CRMGovernanceEvent,
  CRMPredictiveScore,
  CRMRevenueLedger,
  CRMTelemetryEvent,
  registerWilsyCrmIntelligenceModels,
} from '../models/crm/wilsyCrmIntelligenceModels.js';

try {
  registerWilsyCrmIntelligenceModels();
} catch (error) {
  // Intelligence model registration must not block read-only posture.
}

const INTELLIGENCE_COLLECTIONS = Object.freeze({
  telemetry: {
    label: 'Telemetry',
    model: CRMTelemetryEvent,
    defaultSort: { emittedAt: -1, createdAt: -1 },
  },
  compliance: {
    label: 'Compliance Receipts',
    model: CRMComplianceReceipt,
    defaultSort: { sealedAt: -1, updatedAt: -1 },
  },
  governance: {
    label: 'Governance Custody',
    model: CRMGovernanceEvent,
    defaultSort: { recordedAt: -1, sequence: -1 },
  },
  revenue: {
    label: 'Revenue Ledger',
    model: CRMRevenueLedger,
    defaultSort: { recognizedAt: -1, updatedAt: -1 },
  },
  scores: {
    label: 'Predictive Scores',
    model: CRMPredictiveScore,
    defaultSort: { scoredAt: -1, score: -1 },
  },
});

/**
 * @function getTenantId
 * @description Resolves active tenant id from request.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Keeps CRM intelligence queries tenant-aware.
 */
function getTenantId(req) {
  return (
    String(
      req.headers['x-tenant-id'] ||
        req.headers['x-wilsy-tenant-id'] ||
        req.query.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function sortForStableJson
 * @description Recursively sorts payload keys for deterministic hashing.
 * @param {*} value - Value to sort.
 * @returns {*} Sorted value.
 * @collaboration Stabilizes boardroom root hash generation.
 */
function sortForStableJson(value) {
  if (Array.isArray(value)) return value.map((item) => sortForStableJson(item));

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((accumulator, key) => {
        accumulator[key] = sortForStableJson(value[key]);
        return accumulator;
      }, {});
  }

  return value;
}

/**
 * @function createHashDigest
 * @description Creates a SHA3-512 digest with SHA-512 fallback.
 * @param {string} value - String value to hash.
 * @returns {string} Digest.
 * @collaboration Produces forensic hashes without external dependencies.
 */
function createHashDigest(value) {
  try {
    return crypto.createHash('sha3-512').update(value).digest('hex');
  } catch (error) {
    return crypto.createHash('sha512').update(value).digest('hex');
  }
}

/**
 * @function buildIntelligenceRootHash
 * @description Builds a deterministic boardroom intelligence root hash.
 * @param {Object} payload - Root payload.
 * @returns {string} Root hash.
 * @collaboration Gives investors and operators a tamper-evident intelligence posture marker.
 */
function buildIntelligenceRootHash(payload) {
  return createHashDigest(JSON.stringify(sortForStableJson(payload)));
}

/**
 * @function tenantQuery
 * @description Builds tenant query for intelligence collections.
 * @param {string} tenantId - Tenant id.
 * @returns {Object} Mongo query.
 * @collaboration Supports MASTER and tenant-specific intelligence records.
 */
function tenantQuery(tenantId) {
  return tenantId === 'MASTER' ? { tenantId: 'MASTER' } : { tenantId };
}

/**
 * @function safeCount
 * @description Safely counts documents for a model.
 * @param {Object} model - Mongoose model.
 * @param {Object} query - Mongo query.
 * @returns {Promise<number>} Count.
 * @collaboration Prevents one model issue from breaking boardroom posture.
 */
async function safeCount(model, query) {
  try {
    return await model.countDocuments(query);
  } catch (error) {
    return 0;
  }
}

/**
 * @function safeAggregateAmount
 * @description Safely aggregates revenue ledger amount.
 * @param {Object} query - Mongo query.
 * @returns {Promise<number>} Amount total.
 * @collaboration Calculates real revenue ledger posture without inventing revenue.
 */
async function safeAggregateAmount(query) {
  try {
    const result = await CRMRevenueLedger.aggregate([
      { $match: query },
      { $group: { _id: null, total: { $sum: '$amount' } } },
    ]);

    return Number(result?.[0]?.total || 0);
  } catch (error) {
    return 0;
  }
}

/**
 * @function listIntelligenceRecords
 * @description Lists records for one intelligence collection.
 * @param {string} collection - Collection key.
 * @param {string} tenantId - Tenant id.
 * @param {number} limit - Maximum records.
 * @returns {Promise<Object>} Records payload.
 * @collaboration Provides read-only live intelligence records to dashboards.
 */
async function listIntelligenceRecords(collection, tenantId, limit = 50) {
  const definition = INTELLIGENCE_COLLECTIONS[collection];

  if (!definition) {
    return {
      collection,
      label: collection,
      records: [],
      meta: {
        routeLive: false,
        modelName: null,
        count: 0,
      },
    };
  }

  try {
    const records = await definition.model
      .find(tenantQuery(tenantId))
      .sort(definition.defaultSort)
      .limit(Math.min(Number(limit || 50), 250))
      .lean();

    return {
      collection,
      label: definition.label,
      records,
      meta: {
        routeLive: true,
        modelName: definition.model.modelName,
        count: records.length,
      },
    };
  } catch (error) {
    return {
      collection,
      label: definition.label,
      records: [],
      meta: {
        routeLive: true,
        modelName: definition.model.modelName,
        count: 0,
        error: error.message,
      },
    };
  }
}

/**
 * @function getRegisteredModelCount
 * @description Counts registered CRM models.
 * @returns {number} Registered CRM model count.
 * @collaboration Confirms persistence spine registration for boardroom telemetry.
 */
function getRegisteredModelCount() {
  return mongoose.modelNames().filter((modelName) => modelName.startsWith('CRM')).length;
}

/**
 * @function buildBoardroomIntelligence
 * @description Builds CRM intelligence posture for investor and executive views.
 * @param {Object} req - Express request.
 * @returns {Promise<Object>} Intelligence posture.
 * @collaboration Unifies telemetry, compliance, governance, revenue and scoring into one backend-rooted contract.
 */
async function buildBoardroomIntelligence(req) {
  const tenantId = getTenantId(req);
  const query = tenantQuery(tenantId);

  const [
    telemetryCount,
    complianceCount,
    governanceCount,
    revenueCount,
    predictiveScoreCount,
    ledgerTotal,
  ] = await Promise.all([
    safeCount(CRMTelemetryEvent, query),
    safeCount(CRMComplianceReceipt, query),
    safeCount(CRMGovernanceEvent, query),
    safeCount(CRMRevenueLedger, query),
    safeCount(CRMPredictiveScore, query),
    safeAggregateAmount(query),
  ]);

  const posture = {
    tenantId,
    registeredCrmModels: getRegisteredModelCount(),
    telemetry: {
      modelName: CRMTelemetryEvent.modelName,
      count: telemetryCount,
      route: '/api/crm/intelligence/telemetry',
    },
    compliance: {
      modelName: CRMComplianceReceipt.modelName,
      count: complianceCount,
      route: '/api/crm/intelligence/compliance',
    },
    governance: {
      modelName: CRMGovernanceEvent.modelName,
      count: governanceCount,
      route: '/api/crm/intelligence/governance',
    },
    revenue: {
      modelName: CRMRevenueLedger.modelName,
      count: revenueCount,
      total: ledgerTotal,
      currency: 'ZAR',
      route: '/api/crm/intelligence/revenue',
    },
    predictiveScoring: {
      modelName: CRMPredictiveScore.modelName,
      count: predictiveScoreCount,
      route: '/api/crm/intelligence/scores',
    },
  };

  const intelligenceRootHash = buildIntelligenceRootHash(posture);

  return {
    ok: true,
    tenantId,
    intelligenceRootHash,
    intelligenceRootHashShort: intelligenceRootHash.slice(0, 12),
    posture,
    sourceGaps: [],
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function getIntelligenceCollections
 * @description Returns allowed intelligence collection names.
 * @returns {Array<string>} Collection names.
 * @collaboration Prevents arbitrary collection access.
 */
function getIntelligenceCollections() {
  return Object.keys(INTELLIGENCE_COLLECTIONS);
}

export {
  INTELLIGENCE_COLLECTIONS,
  buildBoardroomIntelligence,
  buildIntelligenceRootHash,
  getIntelligenceCollections,
  getTenantId,
  listIntelligenceRecords,
};
