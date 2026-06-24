/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM COMMAND FABRIC ROUTES [R62A]                                                       ║
 * ║ LIVE SEARCH | LIVE SYNC | ADD LEAD COMMAND POSTURE | TENANT-SCOPED | NO FAKE DATA                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Backend command routes for CRM top-rail Search, Live Sync and Add Lead posture.
 * These routes read real Mongo/Mongoose CRM models when present and return source gaps when a model
 * is missing. They never fabricate customer rows.
 */

import crypto from 'node:crypto';
import express from 'express';
import mongoose from 'mongoose';

import {
  WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
  WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
  WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
  searchLeadOperatingRoom,
  verifyLeadSearchTelemetryReceipt,
  listLeadSearchTelemetryReceipts,
  verifyLeadSearchComplianceReceipt,
  listLeadSearchComplianceReceipts,
  verifyLeadSearchEvidenceChain,
  listLeadSearchEvidenceChains,
  materializeLeadSearchGovernanceEvent,
  verifyLeadSearchGovernanceEvent,
  listLeadSearchGovernanceEvents,
  exportLeadSearchRegulatorEvidenceBundle,
  listLeadSearchRegulatorEvidenceBundles,
  materializeLeadSearchRegulatorExportReceipt,
  listLeadSearchRegulatorExportReceipts,
  verifyLeadSearchRegulatorExportReceipt,
  listLeadSearchRegulatorExportReceiptVerifications,
} from '../services/wilsyCrmLeadSearchEngineService.js';

const router = express.Router();

const WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT =
  'R68K-REGULATOR-EXPORT-RECEIPT-VERIFICATION-AUTHORITY';

/**
 * R68K verified regulator export receipt ledger.
 */
router.get('/search/regulator-evidence/receipts/verified/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorExportReceiptVerifications({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/receipts/verified/latest',
    routeContract: WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68K verify regulator export receipt by id, exportReceiptHash, exportHash, or governance id.
 */
router.get('/search/regulator-evidence/receipt/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchRegulatorExportReceipt({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/receipt/:receiptId',
    routeContract: WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT =
  'R68J-REGULATOR-EXPORT-RECEIPT-MATERIALIZATION';

/**
 * R68J recent regulator export receipts.
 */
router.get('/search/regulator-evidence/receipts/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorExportReceipts({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/receipts/latest',
    routeContract: WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT,
  });
});

/**
 * R68J materialize regulator export receipt from governance id or hash.
 */
router.post('/search/regulator-evidence/:governanceId/receipt', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await materializeLeadSearchRegulatorExportReceipt({
    tenantId,
    governanceId: req.params.governanceId,
  });

  return res.status(payload.ok ? 201 : 409).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/:governanceId/receipt',
    routeContract: WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT,
  });
});

const WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT =
  'R68I-REGULATOR-EVIDENCE-EXPORT-AUTHORITY';

/**
 * R68I recent Lead search regulator evidence bundles.
 */
router.get('/search/regulator-evidence/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorEvidenceBundles({
    tenantId,
    limit: req.query.limit || 5,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/latest',
    routeContract: WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT,
  });
});

/**
 * R68I Lead search regulator evidence export by governance id or hash.
 */
router.get('/search/regulator-evidence/:governanceId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await exportLeadSearchRegulatorEvidenceBundle({
    tenantId,
    governanceId: req.params.governanceId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/:governanceId',
    routeContract: WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT,
  });
});

const WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT =
  'R68H-GOVERNANCE-EVENT-VERIFICATION-AUTHORITY';

/**
 * R68H recent Lead search governance event ledger.
 */
router.get('/search/governance-events/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchGovernanceEvents({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/governance-events/latest',
    routeContract: WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68H Lead search governance event verification.
 */
router.get('/search/governance-event/:governanceId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchGovernanceEvent({
    tenantId,
    governanceId: req.params.governanceId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/governance-event/:governanceId',
    routeContract: WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68G_SEARCH_GOVERNANCE_EVENT_ROUTE_CONTRACT =
  'R68G-SEARCH-GOVERNANCE-EVENT-MATERIALIZATION';

/**
 * R68G materialize governance event from verified Lead search evidence chain.
 */
router.post('/search/evidence-chain/:receiptId/govern', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await materializeLeadSearchGovernanceEvent({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 201 : 409).json({
    ...payload,
    route: '/api/crm/command/search/evidence-chain/:receiptId/govern',
    routeContract: WILSY_R68G_SEARCH_GOVERNANCE_EVENT_ROUTE_CONTRACT,
  });
});

const WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT = 'R68F-SEARCH-EVIDENCE-CHAIN-AUTHORITY';

/**
 * R68F recent Lead search evidence chains.
 */
router.get('/search/evidence-chains/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchEvidenceChains({
    tenantId,
    limit: req.query.limit || 5,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/evidence-chains/latest',
    routeContract: WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT,
  });
});

/**
 * R68F Lead search evidence chain verification.
 */
router.get('/search/evidence-chain/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchEvidenceChain({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 409).json({
    ...payload,
    route: '/api/crm/command/search/evidence-chain/:receiptId',
    routeContract: WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT,
  });
});

const WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT =
  'R68E-COMPLIANCE-RECEIPT-VERIFICATION-AUTHORITY';

/**
 * R68E recent Lead search compliance receipt ledger.
 */
router.get('/search/compliance-receipts/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchComplianceReceipts({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/compliance-receipts/latest',
    routeContract: WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68E Lead search compliance receipt verification.
 */
router.get('/search/compliance-receipt/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchComplianceReceipt({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/compliance-receipt/:receiptId',
    routeContract: WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT =
  'R68C.1-SEARCH-RECEIPT-VERIFICATION-SAFE';

/**
 * R68C.1 recent Lead search receipt ledger.
 */
router.get('/search/receipts/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchTelemetryReceipts({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/receipts/latest',
    routeContract: WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68C.1 Lead search receipt verification.
 */
router.get('/search/receipt/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchTelemetryReceipt({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/receipt/:receiptId',
    routeContract: WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT = 'R68B.1-SEARCH-TELEMETRY-BREAKER';

/**
 * R68B.1 controlled Lead search route.
 * This route intentionally shadows older /search handlers so search finality does not depend on telemetry persistence success.
 */
router.get('/search', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const operatorId = String(
    req.user?.email || req.user?.id || req.headers['x-wilsy-operator'] || 'SYSTEM'
  );

  const role = String(req.user?.role || req.headers['x-wilsy-role'] || 'UNKNOWN');

  try {
    const payload = await searchLeadOperatingRoom({
      tenantId,
      query: req.query.q || req.query.query || '',
      limit: req.query.limit || 12,
      role,
      operatorId,
    });

    return res.status(200).json({
      ...payload,
      routeVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
      telemetryRouteVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      telemetryBreakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
      routeContract: 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY',
      telemetryRouteContract: 'R68B-SEARCH-TELEMETRY-PERSISTENCE',
      telemetryBreakerContract: WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT,
    });
  } catch (error) {
    const generatedAt = new Date().toISOString();

    return res.status(200).json({
      ok: false,
      success: false,
      version: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
      telemetryBreakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
      tenantId,
      query: String(req.query.q || req.query.query || ''),
      role,
      operatorId,
      route: '/api/crm/command/search',
      searchMode: 'LEAD_OPERATING_ROOM_BACKEND_AUTHORITY',
      sourceStatus: 'SEARCH_ENGINE_ISOLATED_FAILURE',
      total: 0,
      totalRecords: 0,
      liveSources: 0,
      searchableSources: 0,
      totalSources: 0,
      results: [],
      rows: [],
      registry: [],
      sourceGaps: [
        {
          key: 'search',
          modelName: 'LeadOperatingRoomSearch',
          reason: 'SEARCH_ENGINE_EXCEPTION_ISOLATED',
          errorName: error?.name || 'UnknownError',
          errorMessage: String(error?.message || 'Unknown search failure').slice(0, 220),
        },
      ],
      telemetryPersistence: {
        persisted: false,
        status: 'SEARCH_ENGINE_EXCEPTION_ISOLATED',
        modelName: 'CRMTelemetryEvent',
        errorName: error?.name || 'UnknownError',
        version: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
        generatedAt,
      },
      telemetryPersisted: false,
      generatedAt,
      routeContract: 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY',
      telemetryRouteContract: 'R68B-SEARCH-TELEMETRY-PERSISTENCE',
      telemetryBreakerContract: WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT,
    });
  }
});

const WILSY_R68A_BACKEND_LEAD_SEARCH_ROUTE_CONTRACT = 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY';
const WILSY_R68B_SEARCH_TELEMETRY_ROUTE_CONTRACT = 'R68B-SEARCH-TELEMETRY-PERSISTENCE';

/**
 * R68A backend authority search.
 * This intentionally sits before legacy /search handlers so the Lead search bar receives
 * tenant-scoped rows, source telemetry, compliance bindings and root hash posture.
 */
router.get('/search', async (req, res, next) => {
  try {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await searchLeadOperatingRoom({
      tenantId,
      query: req.query.q || req.query.query || '',
      limit: req.query.limit || 12,
      role: req.user?.role || req.headers['x-wilsy-role'] || 'UNKNOWN',
      operatorId: req.user?.email || req.user?.id || req.headers['x-wilsy-operator'] || 'SYSTEM',
    });

    res.status(200).json({
      ...payload,
      routeVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
      telemetryRouteVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      telemetryRouteContract: WILSY_R68B_SEARCH_TELEMETRY_ROUTE_CONTRACT,
      routeContract: WILSY_R68A_BACKEND_LEAD_SEARCH_ROUTE_CONTRACT,
    });
  } catch (error) {
    next(error);
  }
});

const WILSY_CRM_COMMAND_FABRIC_VERSION = 'R62A-CRM-COMMAND-FABRIC-BACKEND-WIRING';

const CRM_MODEL_REGISTRY = Object.freeze([
  {
    key: 'leads',
    modelName: 'CRMLead',
    fields: ['name', 'firstName', 'lastName', 'email', 'company', 'stage', 'status', 'owner'],
  },
  {
    key: 'contacts',
    modelName: 'CRMContact',
    fields: ['name', 'firstName', 'lastName', 'email', 'phone', 'company', 'accountName', 'status'],
  },
  {
    key: 'accounts',
    modelName: 'CRMAccount',
    fields: ['name', 'accountName', 'company', 'industry', 'status', 'owner'],
  },
  {
    key: 'deals',
    modelName: 'CRMDeal',
    fields: ['name', 'dealName', 'accountName', 'company', 'stage', 'status', 'owner'],
  },
  {
    key: 'tasks',
    modelName: 'CRMTask',
    fields: ['subject', 'title', 'accountName', 'contactName', 'status', 'owner'],
  },
  {
    key: 'meetings',
    modelName: 'CRMMeeting',
    fields: ['subject', 'title', 'accountName', 'contactName', 'status', 'owner'],
  },
  {
    key: 'connectors',
    modelName: 'CRMConnector',
    fields: ['name', 'provider', 'status', 'sourceStatus'],
  },
  {
    key: 'telemetry',
    modelName: 'CRMTelemetryEvent',
    fields: ['eventType', 'source', 'status', 'tenantId'],
  },
  {
    key: 'compliance',
    modelName: 'CRMComplianceReceipt',
    fields: ['receiptType', 'status', 'tenantId', 'source'],
  },
  {
    key: 'governance',
    modelName: 'CRMGovernanceEvent',
    fields: ['eventType', 'status', 'tenantId', 'source'],
  },
  {
    key: 'genericRecords',
    modelName: 'CrmRecord',
    fields: ['name', 'title', 'email', 'company', 'accountName', 'module', 'type', 'status'],
  },
]);

/**
 * @function escapeWilsyCrmRegex
 * @description Escapes user search input before building a Mongo regular expression.
 * @param {string} value - User supplied search value.
 * @returns {string} Regex-safe string.
 * @collaboration Prevents CRM command search from turning operator text into unsafe regex syntax.
 */
function escapeWilsyCrmRegex(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * @function getWilsyCrmTenantId
 * @description Resolves tenant scope from request headers, body or query params.
 * @param {object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Keeps all CRM command fabric reads tenant-scoped.
 */
function getWilsyCrmTenantId(req) {
  return (
    String(
      req.headers['x-tenant-id'] ||
        req.headers['x-wilsy-tenant-id'] ||
        req.body?.tenantId ||
        req.query?.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function getWilsyCrmModel
 * @description Resolves a Mongoose model when it is registered in the runtime.
 * @param {string} modelName - Mongoose model name.
 * @returns {object|null} Mongoose model or null.
 * @collaboration Allows the command fabric to report source gaps instead of fabricating data.
 */
function getWilsyCrmModel(modelName) {
  return mongoose.models?.[modelName] || null;
}

/**
 * @function buildWilsyCrmTenantFilter
 * @description Builds a tolerant tenant filter for CRM collections with different tenant field names.
 * @param {string} tenantId - Tenant id.
 * @returns {object} Mongo query filter.
 * @collaboration Supports current and legacy CRM model schemas without cross-tenant leakage.
 */
function buildWilsyCrmTenantFilter(tenantId) {
  return {
    $or: [{ tenantId }, { 'tenant.id': tenantId }, { tenant: tenantId }, { tenantKey: tenantId }],
  };
}

/**
 * @function buildWilsyCrmSearchFilter
 * @description Builds a tenant-scoped search filter for a CRM registry entry.
 * @param {object} registryEntry - CRM model registry entry.
 * @param {string} tenantId - Tenant id.
 * @param {string} query - Search text.
 * @returns {object} Mongo query filter.
 * @collaboration Powers top-rail CRM search from real backend records.
 */
function buildWilsyCrmSearchFilter(registryEntry, tenantId, query) {
  const tenantFilter = buildWilsyCrmTenantFilter(tenantId);
  const cleanQuery = String(query || '').trim();

  if (!cleanQuery) {
    return tenantFilter;
  }

  const regex = new RegExp(escapeWilsyCrmRegex(cleanQuery), 'i');
  const searchClauses = registryEntry.fields.map((field) => ({ [field]: regex }));

  return {
    $and: [tenantFilter, { $or: searchClauses }],
  };
}

/**
 * @function normalizeWilsyCrmRecord
 * @description Converts a Mongo document into a compact CRM command result.
 * @param {object} record - Raw Mongo record.
 * @param {object} registryEntry - CRM model registry entry.
 * @returns {object} Normalized result.
 * @collaboration Keeps browser search results consistent while preserving backend source truth.
 */
function normalizeWilsyCrmRecord(record, registryEntry) {
  const source = record || {};
  const id = String(
    source._id || source.id || source.externalId || `${registryEntry.key}-${Date.now()}`
  );
  const primary =
    source.name ||
    source.title ||
    source.subject ||
    source.dealName ||
    source.accountName ||
    source.company ||
    source.email ||
    'SOURCE VALUE REQUIRED';

  const secondary =
    source.company ||
    source.accountName ||
    source.email ||
    source.status ||
    source.stage ||
    source.sourceStatus ||
    registryEntry.key;

  return {
    id,
    module: registryEntry.key,
    modelName: registryEntry.modelName,
    primary,
    secondary,
    status: source.status || source.stage || source.sourceStatus || 'SOURCE_LIVE',
    sourceStatus: source.sourceStatus || 'SOURCE_LIVE',
    updatedAt: source.updatedAt || source.createdAt || null,
  };
}

/**
 * @function buildWilsyCrmCommandRootHash
 * @description Builds a deterministic hash for CRM command responses.
 * @param {object} packet - Response packet.
 * @returns {string} SHA-256 hash.
 * @collaboration Gives Live Sync and Search a compact evidence fingerprint.
 */
function buildWilsyCrmCommandRootHash(packet) {
  return crypto.createHash('sha256').update(JSON.stringify(packet)).digest('hex');
}

/**
 * @function queryWilsyCrmRegistryEntry
 * @description Reads one CRM model for search/sync without fabricating missing rows.
 * @param {object} registryEntry - CRM model registry entry.
 * @param {string} tenantId - Tenant id.
 * @param {string} query - Search query.
 * @param {number} limit - Result limit.
 * @returns {Promise<object>} Query result packet.
 * @collaboration Keeps CRM command search model-aware and source-gap aware.
 */
async function queryWilsyCrmRegistryEntry(registryEntry, tenantId, query, limit) {
  const Model = getWilsyCrmModel(registryEntry.modelName);

  if (!Model) {
    return {
      key: registryEntry.key,
      modelName: registryEntry.modelName,
      connected: false,
      count: 0,
      results: [],
      sourceGap: `${registryEntry.modelName} model not registered`,
    };
  }

  const filter = buildWilsyCrmSearchFilter(registryEntry, tenantId, query);
  const safeLimit = Math.max(1, Math.min(Number(limit) || 8, 25));

  const [count, rows] = await Promise.all([
    Model.countDocuments(filter).catch(() => 0),
    Model.find(filter)
      .sort({ updatedAt: -1, createdAt: -1, _id: -1 })
      .limit(safeLimit)
      .lean()
      .catch(() => []),
  ]);

  return {
    key: registryEntry.key,
    modelName: registryEntry.modelName,
    connected: true,
    count,
    results: rows.map((row) => normalizeWilsyCrmRecord(row, registryEntry)),
    sourceGap: null,
  };
}

/**
 * @function handleWilsyCrmCommandSearch
 * @description Handles live CRM command search.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Connects the top rail search to backend CRM source truth.
 */
async function handleWilsyCrmCommandSearch(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const query = String(req.query.q || req.query.query || '').trim();
    const limit = Math.max(1, Math.min(Number(req.query.limit) || 8, 25));

    const registryResults = await Promise.all(
      CRM_MODEL_REGISTRY.map((entry) => queryWilsyCrmRegistryEntry(entry, tenantId, query, limit))
    );

    const sourceGaps = registryResults
      .filter((item) => item.sourceGap)
      .map((item) => item.sourceGap);

    const results = registryResults.flatMap((item) => item.results).slice(0, limit);

    const packet = {
      ok: true,
      version: WILSY_CRM_COMMAND_FABRIC_VERSION,
      tenantId,
      query,
      route: '/api/crm/command/search',
      sourceStatus: sourceGaps.length ? 'SOURCE_DEGRADED' : 'SOURCE_LIVE',
      total: results.length,
      results,
      registry: registryResults.map((item) => ({
        key: item.key,
        modelName: item.modelName,
        connected: item.connected,
        count: item.count,
      })),
      sourceGaps,
      generatedAt: new Date().toISOString(),
    };

    const rootHash = buildWilsyCrmCommandRootHash(packet);

    res.json({
      ...packet,
      rootHash,
      rootHashShort: rootHash.slice(0, 12),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyCrmCommandSync
 * @description Handles live CRM command sync.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Hydrates CRM Live Sync from registered backend models and source gaps.
 */
async function handleWilsyCrmCommandSync(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const reason = req.body?.reason || 'CRM_LIVE_SYNC';
    const activeModule = req.body?.activeModule || 'leads';

    const registryResults = await Promise.all(
      CRM_MODEL_REGISTRY.map((entry) => queryWilsyCrmRegistryEntry(entry, tenantId, '', 3))
    );

    const connected = registryResults.filter((item) => item.connected);
    const sourceGaps = registryResults
      .filter((item) => item.sourceGap)
      .map((item) => item.sourceGap);

    const totalRecords = registryResults.reduce((sum, item) => sum + Number(item.count || 0), 0);

    const packet = {
      ok: true,
      version: WILSY_CRM_COMMAND_FABRIC_VERSION,
      tenantId,
      reason,
      activeModule,
      route: '/api/crm/command/sync',
      sourceStatus: sourceGaps.length ? 'SOURCE_DEGRADED' : 'SOURCE_LIVE',
      liveSources: connected.length,
      totalSources: CRM_MODEL_REGISTRY.length,
      totalRecords,
      registry: registryResults.map((item) => ({
        key: item.key,
        modelName: item.modelName,
        connected: item.connected,
        count: item.count,
        sourceStatus: item.connected ? 'SOURCE_LIVE' : 'SOURCE_REQUIRED',
      })),
      sourceGaps,
      generatedAt: new Date().toISOString(),
    };

    const rootHash = buildWilsyCrmCommandRootHash(packet);

    res.json({
      ...packet,
      rootHash,
      rootHashShort: rootHash.slice(0, 12),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyCrmCommandLeadCreate
 * @description Creates a CRM lead only when a real backend model is registered and valid source payload is provided.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Gives Add Lead a production backend path without creating fake rows from an empty click.
 */
async function handleWilsyCrmCommandLeadCreate(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const payload = req.body?.lead || req.body || {};
    const hasSourcePayload = Boolean(
      payload.name || payload.email || payload.company || payload.accountName
    );

    if (!hasSourcePayload) {
      res.status(400).json({
        ok: false,
        sourceStatus: 'SOURCE_REQUIRED',
        message: 'Lead source payload required before backend creation.',
        tenantId,
      });
      return;
    }

    const LeadModel = getWilsyCrmModel('CRMLead');
    const GenericModel = getWilsyCrmModel('CrmRecord');
    const Model = LeadModel || GenericModel;

    if (!Model) {
      res.status(503).json({
        ok: false,
        sourceStatus: 'SOURCE_REQUIRED',
        message: 'No CRM lead model is registered in this runtime.',
        tenantId,
      });
      return;
    }

    const document = await Model.create({
      ...payload,
      tenantId,
      module: payload.module || 'leads',
      type: payload.type || 'lead',
      sourceSystem: payload.sourceSystem || 'WILSY_OS_CRM_COMMAND_FABRIC',
      sourceStatus: payload.sourceStatus || 'SOURCE_LIVE',
      createdAt: payload.createdAt || new Date(),
      updatedAt: new Date(),
    });

    const normalized = normalizeWilsyCrmRecord(document.toObject ? document.toObject() : document, {
      key: 'leads',
      modelName: LeadModel ? 'CRMLead' : 'CrmRecord',
    });

    res.status(201).json({
      ok: true,
      tenantId,
      sourceStatus: 'SOURCE_LIVE',
      record: normalized,
      generatedAt: new Date().toISOString(),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyCrmCommandStatus
 * @description Returns CRM command fabric route posture.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {void} Response completion.
 * @collaboration Gives health checks a cheap route contract before live sync/search.
 */
function handleWilsyCrmCommandStatus(req, res) {
  const tenantId = getWilsyCrmTenantId(req);
  const registeredModels = CRM_MODEL_REGISTRY.filter((entry) =>
    Boolean(getWilsyCrmModel(entry.modelName))
  ).map((entry) => entry.modelName);

  res.json({
    ok: true,
    version: WILSY_CRM_COMMAND_FABRIC_VERSION,
    tenantId,
    route: '/api/crm/command/status',
    registeredModels,
    totalModels: CRM_MODEL_REGISTRY.length,
    generatedAt: new Date().toISOString(),
  });
}

router.get('/status', handleWilsyCrmCommandStatus);
router.get('/search', handleWilsyCrmCommandSearch);
router.post('/sync', handleWilsyCrmCommandSync);
router.post('/leads', handleWilsyCrmCommandLeadCreate);

export default router;
