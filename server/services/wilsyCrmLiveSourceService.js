/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM LIVE SOURCE POSTURE SERVICE                                                                             ║
 * ║ SOURCE ROUTES | MONGOOSE DISCOVERY | TENANT-SAFE RECORD LISTING | SHA3-512 SOURCE ROOT HASH                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Live CRM source-posture service.
 * This service never invents CRM records. It searches existing Mongoose models and raw collections,
 * returns real records when available, and otherwise returns source-honest empty arrays.
 */

import crypto from 'crypto';

import mongooseRuntime from 'mongoose';
import { registerWilsyCrmModels } from '../models/crm/wilsyCrmModelRegistry.js';

try {
  registerWilsyCrmModels();
} catch (error) {
  // Model registration should never block read-only CRM posture routes.
}

const SOURCE_DEFINITIONS = Object.freeze({
  leads: {
    label: 'Leads',
    modelNames: ['CRMLead', 'Lead', 'CrmLead', 'Prospect', 'ClientLead'],
    collectionNames: ['leads', 'crmleads', 'crm_leads', 'prospects', 'clientleads'],
  },
  contacts: {
    label: 'Contacts',
    modelNames: ['CRMContact', 'Contact', 'CrmContact', 'ClientContact'],
    collectionNames: ['contacts', 'crmcontacts', 'crm_contacts', 'clientcontacts'],
  },
  accounts: {
    label: 'Accounts',
    modelNames: ['CRMAccount', 'Account', 'CrmAccount', 'Company', 'ClientCompany'],
    collectionNames: ['accounts', 'crmaccounts', 'crm_accounts', 'companies', 'clientcompanies'],
  },
  deals: {
    label: 'Deals',
    modelNames: ['CRMDeal', 'Deal', 'CrmDeal', 'Opportunity', 'PipelineDeal'],
    collectionNames: ['deals', 'crmdeals', 'crm_deals', 'opportunities', 'pipelinedeals'],
  },
  tasks: {
    label: 'Tasks',
    modelNames: ['CRMTask', 'Task', 'CrmTask', 'Activity', 'Todo'],
    collectionNames: ['tasks', 'crmtasks', 'crm_tasks', 'activities', 'todos'],
  },
  meetings: {
    label: 'Meetings',
    modelNames: ['CRMMeeting', 'Meeting', 'CrmMeeting', 'CalendarEvent', 'Event'],
    collectionNames: ['meetings', 'crmmeetings', 'crm_meetings', 'calendarevents', 'events'],
  },
  evidence: {
    label: 'Evidence',
    modelNames: [
      'Evidence',
      'AuditLog',
      'AuditEvent',
      'Receipt',
      'DocumentReceipt',
      'ComplianceEvidence',
    ],
    collectionNames: [
      'evidence',
      'auditlogs',
      'auditevents',
      'receipts',
      'documentreceipts',
      'complianceevidence',
    ],
  },
  connectors: {
    label: 'Connectors',
    modelNames: [
      'CRMConnector',
      'Connector',
      'Integration',
      'DataConnector',
      'SourceConnector',
      'ServiceConnection',
    ],
    collectionNames: [
      'connectors',
      'integrations',
      'dataconnectors',
      'sourceconnectors',
      'serviceconnections',
    ],
  },
});

/**
 * @function getMongooseRuntime
 * @description Returns the optional Mongoose runtime.
 * @returns {*} Mongoose runtime or null.
 * @collaboration Allows CRM source discovery to reuse existing DB models without introducing hard coupling.
 */
function getMongooseRuntime() {
  return mongooseRuntime;
}

/**
 * @function getTenantId
 * @description Resolves the active tenant id from request headers or query.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Keeps live CRM data retrieval tenant-aware.
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
 * @function buildTenantQueries
 * @description Builds tenant-safe query candidates for known Wilsy OS tenant fields.
 * @param {string} tenantId - Active tenant id.
 * @returns {Array<Object>} Query candidates.
 * @collaboration Searches common tenant fields before allowing MASTER-level empty-query inspection.
 */
function buildTenantQueries(tenantId) {
  if (!tenantId || tenantId === 'MASTER') {
    return [
      { tenantId: 'MASTER' },
      { tenant: 'MASTER' },
      { 'tenant.id': 'MASTER' },
      { tenantAlias: 'MASTER' },
      {},
    ];
  }

  return [{ tenantId }, { tenant: tenantId }, { 'tenant.id': tenantId }, { tenantAlias: tenantId }];
}

/**
 * @function createHashDigest
 * @description Creates a SHA3-512 digest with SHA-512 fallback.
 * @param {string} value - Value to hash.
 * @returns {string} Hex digest.
 * @collaboration Provides a backend-root source hash without external dependencies.
 */
function createHashDigest(value) {
  try {
    return crypto.createHash('sha3-512').update(value).digest('hex');
  } catch (error) {
    return crypto.createHash('sha512').update(value).digest('hex');
  }
}

/**
 * @function sortForStableJson
 * @description Recursively sorts object keys for deterministic source-root hashing.
 * @param {*} value - Value to sort.
 * @returns {*} Sorted value.
 * @collaboration Keeps source posture hashes stable across equivalent payload key ordering.
 */
function sortForStableJson(value) {
  if (Array.isArray(value)) {
    return value.map((item) => sortForStableJson(item));
  }

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
 * @function buildSourceRootHash
 * @description Builds a deterministic source posture root hash.
 * @param {Object} payload - Source posture payload.
 * @returns {string} Root hash.
 * @collaboration Converts live route/model posture into a visible CRM authority signal.
 */
function buildSourceRootHash(payload) {
  const stablePayload = JSON.stringify(sortForStableJson(payload));
  return createHashDigest(stablePayload);
}

/**
 * @function getAllowedCollections
 * @description Lists allowed CRM live collections.
 * @returns {Array<string>} Collection ids.
 * @collaboration Prevents arbitrary collection access through the live CRM route.
 */
function getAllowedCollections() {
  return Object.keys(SOURCE_DEFINITIONS);
}

/**
 * @function getCollectionDefinition
 * @description Returns the source definition for a collection id.
 * @param {string} collection - CRM collection id.
 * @returns {Object|null} Source definition.
 * @collaboration Centralizes source definitions for routes and posture checks.
 */
function getCollectionDefinition(collection) {
  return SOURCE_DEFINITIONS[collection] || null;
}

/**
 * @function sanitizeDocument
 * @description Converts a DB document into a browser-safe plain object.
 * @param {Object} doc - DB document.
 * @returns {Object} Plain object.
 * @collaboration Keeps CRM API responses JSON-safe without fabricating fields.
 */
function sanitizeDocument(doc) {
  const plain = typeof doc?.toObject === 'function' ? doc.toObject() : { ...(doc || {}) };

  if (plain._id && typeof plain._id !== 'string') {
    plain.id = String(plain._id);
  }

  delete plain.__v;
  return plain;
}

/**
 * @function getPossibleModel
 * @description Finds the first registered Mongoose model matching a source definition.
 * @param {Object} definition - Source definition.
 * @returns {*|null} Mongoose model or null.
 * @collaboration Reuses existing backend models before falling back to raw collections.
 */
function getPossibleModel(definition) {
  const mongoose = getMongooseRuntime();
  if (!mongoose || typeof mongoose.modelNames !== 'function') return null;

  const availableModels = mongoose.modelNames();

  for (const modelName of definition.modelNames) {
    if (availableModels.includes(modelName)) {
      return mongoose.model(modelName);
    }
  }

  return null;
}

/**
 * @function queryModelRecords
 * @description Queries matching Mongoose model records with tenant-aware candidates.
 * @param {Object} model - Mongoose model.
 * @param {string} tenantId - Active tenant id.
 * @param {number} limit - Record limit.
 * @returns {Promise<Array<Object>>} Records.
 * @collaboration Pulls actual DB data while avoiding broad cross-tenant queries except MASTER fallback.
 */
async function queryModelRecords(model, tenantId, limit) {
  const queries = buildTenantQueries(tenantId);

  for (const query of queries) {
    try {
      const records = await model
        .find(query)
        .sort({ updatedAt: -1, createdAt: -1 })
        .limit(limit)
        .lean();
      if (Array.isArray(records) && records.length) return records.map(sanitizeDocument);
    } catch (error) {
      // Continue to the next tenant query candidate.
    }
  }

  return [];
}

/**
 * @function getRawCollection
 * @description Finds a raw MongoDB collection matching a source definition.
 * @param {Object} definition - Source definition.
 * @returns {Object|null} Mongo collection or null.
 * @collaboration Lets CRM use existing collections even when no Mongoose model is registered.
 */
async function getRawCollection(definition) {
  const mongoose = getMongooseRuntime();
  const db = mongoose?.connection?.db;

  if (!db || typeof db.listCollections !== 'function') return null;

  try {
    const collectionInfos = await db.listCollections().toArray();
    const names = collectionInfos.map((info) => info.name);

    for (const collectionName of definition.collectionNames) {
      if (names.includes(collectionName)) return db.collection(collectionName);
    }
  } catch (error) {
    return null;
  }

  return null;
}

/**
 * @function queryRawCollectionRecords
 * @description Queries records from a raw MongoDB collection.
 * @param {Object} collection - Mongo collection.
 * @param {string} tenantId - Active tenant id.
 * @param {number} limit - Record limit.
 * @returns {Promise<Array<Object>>} Records.
 * @collaboration Pulls existing Mongo data when Mongoose models are unavailable.
 */
async function queryRawCollectionRecords(collection, tenantId, limit) {
  const queries = buildTenantQueries(tenantId);

  for (const query of queries) {
    try {
      const records = await collection
        .find(query)
        .sort({ updatedAt: -1, createdAt: -1 })
        .limit(limit)
        .toArray();
      if (Array.isArray(records) && records.length) return records.map(sanitizeDocument);
    } catch (error) {
      // Continue to next query candidate.
    }
  }

  return [];
}

/**
 * @function listCollectionRecords
 * @description Lists actual source records for one CRM collection.
 * @param {string} collection - CRM collection id.
 * @param {string} tenantId - Active tenant id.
 * @param {number} limit - Record limit.
 * @returns {Promise<Object>} Source records and metadata.
 * @collaboration Searches existing backend data before returning an empty source-honest result.
 */
async function listCollectionRecords(collection, tenantId, limit = 50) {
  const definition = getCollectionDefinition(collection);

  if (!definition) {
    return {
      collection,
      label: collection,
      records: [],
      dataSource: 'unsupported',
      modelName: null,
      routeLive: false,
    };
  }

  const model = getPossibleModel(definition);

  if (model) {
    const records = await queryModelRecords(model, tenantId, limit);
    return {
      collection,
      label: definition.label,
      records,
      dataSource: 'mongoose',
      modelName: model.modelName,
      routeLive: true,
    };
  }

  const rawCollection = await getRawCollection(definition);

  if (rawCollection) {
    const records = await queryRawCollectionRecords(rawCollection, tenantId, limit);
    return {
      collection,
      label: definition.label,
      records,
      dataSource: 'mongo-collection',
      modelName: rawCollection.collectionName,
      routeLive: true,
    };
  }

  return {
    collection,
    label: definition.label,
    records: [],
    dataSource: 'route-only',
    modelName: null,
    routeLive: true,
  };
}

/**
 * @function inspectCollectionSource
 * @description Inspects route/model posture for one source collection.
 * @param {string} collection - CRM collection id.
 * @param {string} tenantId - Active tenant id.
 * @returns {Promise<Object>} Source posture.
 * @collaboration Feeds the source-route counter and backend root hash.
 */
async function inspectCollectionSource(collection, tenantId) {
  const result = await listCollectionRecords(collection, tenantId, 1);

  return {
    id: collection,
    label: result.label,
    route: `/api/crm/live/${collection}`,
    routeLive: result.routeLive,
    dataSource: result.dataSource,
    modelName: result.modelName,
    recordCount: result.records.length,
    status: result.routeLive ? 'live' : 'missing',
  };
}

/**
 * @function buildSourcePosture
 * @description Builds live source route posture and root hash for CRM.
 * @param {Object} req - Express request.
 * @returns {Promise<Object>} Source posture.
 * @collaboration Powers Root Hash and source-route status in the CRM header.
 */
async function buildSourcePosture(req) {
  const tenantId = getTenantId(req);
  const collections = getAllowedCollections();
  const sources = await Promise.all(
    collections.map((collection) => inspectCollectionSource(collection, tenantId))
  );
  const connectedRoutes = sources.filter((source) => source.routeLive).length;
  const sourceGaps = sources.filter(
    (source) => source.status !== 'live' || source.dataSource === 'route-only'
  );

  const rootInput = {
    tenantId,
    version: 'crm-live-source-posture-v1',
    sources: sources.map((source) => ({
      id: source.id,
      routeLive: source.routeLive,
      dataSource: source.dataSource,
      modelName: source.modelName,
      recordCount: source.recordCount,
      status: source.status,
    })),
  };

  const rootHash = buildSourceRootHash(rootInput);

  return {
    ok: true,
    tenantId,
    rootHash,
    rootHashShort: rootHash.slice(0, 12),
    connectedRoutes,
    totalRoutes: collections.length,
    sourceGaps,
    sources,
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function listCrmCollection
 * @description Lists one CRM collection and includes current source posture.
 * @param {Object} req - Express request.
 * @param {string} collection - CRM collection id.
 * @returns {Promise<Object>} Collection response.
 * @collaboration Keeps frontend collection fetches and source posture in one live backend contract.
 */
async function listCrmCollection(req, collection) {
  const tenantId = getTenantId(req);
  const limit = Math.min(Number(req.query.limit || 50), 250);
  const result = await listCollectionRecords(collection, tenantId, limit);
  const sourcePosture = await buildSourcePosture(req);

  return {
    ok: true,
    tenantId,
    collection,
    data: result.records,
    records: result.records,
    meta: {
      label: result.label,
      count: result.records.length,
      dataSource: result.dataSource,
      modelName: result.modelName,
      routeLive: result.routeLive,
    },
    sourcePosture,
  };
}

export {
  SOURCE_DEFINITIONS,
  buildSourcePosture,
  getAllowedCollections,
  getTenantId,
  listCrmCollection,
};
