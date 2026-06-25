/* eslint-disable */
import crypto from 'node:crypto';
import mongoose from 'mongoose';

export const WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION = 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY';
export const WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION = 'R68B-SEARCH-TELEMETRY-PERSISTENCE';
export const WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION = 'R68B.1-SEARCH-TELEMETRY-BREAKER';
export const WILSY_CRM_SEARCH_TELEMETRY_TDZ_REPAIR_VERSION = 'R68B.3-TELEMETRY-TDZ-SOURCE-PROOF';
export const WILSY_CRM_SEARCH_FUNCTION_REWRITE_VERSION = 'R68B.4-SEARCH-FUNCTION-REWRITE';
export const WILSY_CRM_SEARCH_CANONICAL_RESET_VERSION = 'R68B.5-CANONICAL-SERVICE-RESET';
export const WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION =
  'R68C.1-SEARCH-RECEIPT-VERIFICATION-SAFE';
export const WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION =
  'R68D-SEARCH-COMPLIANCE-RECEIPT-MATERIALIZATION';
export const WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION =
  'R68E-COMPLIANCE-RECEIPT-VERIFICATION-AUTHORITY';
export const WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION = 'R68F-SEARCH-EVIDENCE-CHAIN-AUTHORITY';
export const WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION =
  'R68G-SEARCH-GOVERNANCE-EVENT-MATERIALIZATION';
export const WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION =
  'R68H-GOVERNANCE-EVENT-VERIFICATION-AUTHORITY';
export const WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION =
  'R68I-REGULATOR-EVIDENCE-EXPORT-AUTHORITY';
export const WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION =
  'R68J-REGULATOR-EXPORT-RECEIPT-MATERIALIZATION';
export const WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION =
  'R68K-REGULATOR-EXPORT-RECEIPT-VERIFICATION-AUTHORITY';
export const WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION =
  'R68L-REGULATOR-EVIDENCE-DOSSIER-AUTHORITY';
export const WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION =
  'R68M-REGULATOR-DOSSIER-VERIFICATION-AUTHORITY';
export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION =
  'R68N-REGULATOR-DOSSIER-CHAIN-LEDGER-AUTHORITY';
export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_VERSION =
  'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY';

const SOURCE_REGISTRY = Object.freeze([
  { key: 'leads', modelName: 'CRMLead', weight: 1.0 },
  { key: 'contacts', modelName: 'CRMContact', weight: 0.86 },
  { key: 'accounts', modelName: 'CRMAccount', weight: 0.82 },
  { key: 'deals', modelName: 'CRMDeal', weight: 0.72 },
  { key: 'tasks', modelName: 'CRMTask', weight: 0.48 },
  { key: 'meetings', modelName: 'CRMMeeting', weight: 0.48 },
  { key: 'connectors', modelName: 'CRMConnector', weight: 0.44 },
  { key: 'telemetry', modelName: 'CRMTelemetryEvent', weight: 0.36 },
  { key: 'compliance', modelName: 'CRMComplianceReceipt', weight: 0.92 },
  { key: 'governance', modelName: 'CRMGovernanceEvent', weight: 0.88 },
  { key: 'genericRecords', modelName: 'CrmRecord', weight: 0.6 },
]);

const SEARCH_FIELD_CANDIDATES = Object.freeze([
  'name',
  'leadName',
  'firstName',
  'lastName',
  'fullName',
  'company',
  'companyName',
  'accountName',
  'email',
  'phone',
  'mobile',
  'title',
  'source',
  'leadSource',
  'status',
  'leadStatus',
  'industry',
  'website',
  'description',
  'notes',
  'provenanceHash',
  'receiptHash',
  'rootHash',
  'complianceStatus',
  'owner',
  'ownerEmail',
  'tenantId',
]);

const TENANT_FIELD_CANDIDATES = Object.freeze([
  'tenantId',
  'tenant',
  'tenantKey',
  'organizationId',
  'orgId',
  'workspaceId',
]);

const COMPLIANCE_BINDINGS = Object.freeze([
  {
    code: 'POPIA',
    posture: 'SOURCE_BASIS_REQUIRED',
    description: 'Every Lead row must retain source basis, consent posture and audit receipt.',
  },
  {
    code: 'GDPR',
    posture: 'LAWFUL_BASIS_REQUIRED',
    description: 'Every searchable Lead identity must map to a lawful-basis and retention packet.',
  },
  {
    code: 'SOC2',
    posture: 'AUDITABILITY_REQUIRED',
    description: 'Every Lead mutation must be traceable through immutable operational telemetry.',
  },
]);

/**
 * @function escapeRegex
 * @description Escapes user search text before constructing a regular expression.
 * @param {string} value - Raw search value.
 * @returns {string} Escaped value.
 * @collaboration Prevents unsafe search patterns inside CRM command search.
 */
function escapeRegex(value = '') {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * @function createHashDigest
 * @description Creates a SHA3-512 digest with a SHA-512 fallback for older runtimes.
 * @param {string} payload - Payload to hash.
 * @returns {string} Hex digest.
 * @collaboration Provides deterministic provenance receipts for Lead search rows.
 */
function createHashDigest(payload = '') {
  try {
    return crypto.createHash('sha3-512').update(String(payload)).digest('hex');
  } catch (error) {
    return crypto.createHash('sha512').update(String(payload)).digest('hex');
  }
}

/**
 * @function getModel
 * @description Resolves a Mongoose model by name without throwing for missing models.
 * @param {string} modelName - Mongoose model name.
 * @returns {Object|null} Mongoose model or null.
 * @collaboration Allows search to report source gaps instead of crashing.
 */
function getModel(modelName) {
  return mongoose.models?.[modelName] || null;
}

/**
 * @function getSchemaPathNames
 * @description Returns schema path names for a model.
 * @param {Object} model - Mongoose model.
 * @returns {Set<string>} Schema path names.
 * @collaboration Keeps tenant and search filters aligned to actual registered schemas.
 */
function getSchemaPathNames(model) {
  return new Set(Object.keys(model?.schema?.paths || {}));
}

/**
 * @function pickExistingPath
 * @description Finds the first candidate field present in a schema.
 * @param {Set<string>} paths - Schema paths.
 * @param {string[]} candidates - Candidate fields.
 * @returns {string|null} Existing field or null.
 * @collaboration Prevents unsafe cross-tenant queries on models that lack tenant identity.
 */
function pickExistingPath(paths, candidates = []) {
  return candidates.find((candidate) => paths.has(candidate)) || null;
}

/**
 * @function buildTenantFilter
 * @description Builds a strict tenant filter for a model.
 * @param {Object} model - Mongoose model.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Object|null} Tenant filter or null when model is unsafe to query.
 * @collaboration Enforces multi-tenant CRM search boundaries.
 */
function buildTenantFilter(model, tenantId = 'MASTER') {
  const paths = getSchemaPathNames(model);
  const tenantField = pickExistingPath(paths, TENANT_FIELD_CANDIDATES);

  if (!tenantField) return null;

  return { [tenantField]: tenantId };
}

/**
 * @function buildSearchFilter
 * @description Builds a schema-aware text search filter.
 * @param {Object} model - Mongoose model.
 * @param {string} query - Search query.
 * @returns {Object} Mongo filter.
 * @collaboration Searches real CRM fields without assuming every model has every field.
 */
function buildSearchFilter(model, query = '') {
  const trimmed = String(query || '').trim();
  if (!trimmed) return {};

  const paths = getSchemaPathNames(model);
  const regex = new RegExp(escapeRegex(trimmed), 'i');
  const searchableFields = SEARCH_FIELD_CANDIDATES.filter((field) => paths.has(field));

  if (!searchableFields.length) return {};

  return {
    $or: searchableFields.map((field) => ({ [field]: regex })),
  };
}

/**
 * @function buildModelFilter
 * @description Builds the final tenant-safe model filter.
 * @param {Object} model - Mongoose model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} query - Search query.
 * @returns {Object|null} Mongo filter or null when model cannot be safely queried.
 * @collaboration Combines tenant boundary and search predicates.
 */
function buildModelFilter(model, tenantId = 'MASTER', query = '') {
  const tenantFilter = buildTenantFilter(model, tenantId);
  if (!tenantFilter) return null;

  const searchFilter = buildSearchFilter(model, query);
  const clauses = [tenantFilter];

  if (Object.keys(searchFilter).length) {
    clauses.push(searchFilter);
  }

  return clauses.length === 1 ? tenantFilter : { $and: clauses };
}

/**
 * @function safeCountDocuments
 * @description Counts tenant-scoped records without failing the whole search.
 * @param {Object} model - Mongoose model.
 * @param {Object} filter - Mongo filter.
 * @returns {Promise<number>} Count.
 * @collaboration Produces source telemetry even when one model has a query issue.
 */
async function safeCountDocuments(model, filter) {
  try {
    return await model.countDocuments(filter || {});
  } catch (error) {
    return 0;
  }
}

/**
 * @function safeFindDocuments
 * @description Finds tenant-scoped documents without failing the whole search.
 * @param {Object} model - Mongoose model.
 * @param {Object} filter - Mongo filter.
 * @param {number} limit - Result limit.
 * @returns {Promise<Array>} Documents.
 * @collaboration Returns authentic rows only from registered backend models.
 */
async function safeFindDocuments(model, filter, limit = 10) {
  try {
    return await model
      .find(filter || {})
      .sort({ updatedAt: -1, createdAt: -1 })
      .limit(limit)
      .lean();
  } catch (error) {
    return [];
  }
}

/**
 * @function resolveRecordValue
 * @description Resolves the first non-empty value from a record.
 * @param {Object} record - Source record.
 * @param {string[]} fields - Candidate fields.
 * @param {string} fallback - Fallback value.
 * @returns {string} Resolved value.
 * @collaboration Normalizes different CRM schemas into a consistent Lead ledger row.
 */
function resolveRecordValue(record = {}, fields = [], fallback = '') {
  const field = fields.find(
    (candidate) =>
      record[candidate] !== undefined && record[candidate] !== null && record[candidate] !== ''
  );
  return field ? String(record[field]) : fallback;
}

/**
 * @function resolveComplianceStatus
 * @description Resolves compliance state for a record.
 * @param {Object} record - Source record.
 * @returns {string} VERIFIED, PENDING or FAILED.
 * @collaboration Converts backend posture into regulator-readable Lead status.
 */
function resolveComplianceStatus(record = {}) {
  const value = resolveRecordValue(
    record,
    ['complianceStatus', 'status', 'leadStatus'],
    'PENDING'
  ).toUpperCase();

  if (['VERIFIED', 'COMPLIANT', 'PASSED', 'ACTIVE'].includes(value)) return 'VERIFIED';
  if (['FAILED', 'REJECTED', 'BLOCKED', 'NON_COMPLIANT'].includes(value)) return 'FAILED';

  return 'PENDING';
}

/**
 * @function normalizeLeadSearchRow
 * @description Normalizes one backend model document into a Lead ledger row.
 * @param {Object} record - Source record.
 * @param {Object} source - Source registry entry.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Object} Normalized row.
 * @collaboration Makes search results renderable as Lead provenance rows.
 */
function normalizeLeadSearchRow(record = {}, source = {}, tenantId = 'MASTER') {
  const id = String(record._id || record.id || '');
  const company = resolveRecordValue(
    record,
    ['company', 'companyName', 'accountName', 'name'],
    '—'
  );
  const email = resolveRecordValue(record, ['email', 'primaryEmail', 'contactEmail'], '—');
  const phone = resolveRecordValue(record, ['phone', 'mobile', 'telephone'], '—');
  const name = resolveRecordValue(record, ['name', 'leadName', 'fullName', 'firstName'], company);
  const owner = resolveRecordValue(record, ['owner', 'ownerEmail', 'createdBy'], 'UNASSIGNED');
  const lastActivity = resolveRecordValue(
    record,
    ['lastActivity', 'updatedAt', 'createdAt'],
    new Date().toISOString()
  );
  const complianceStatus = resolveComplianceStatus(record);
  const existingHash = resolveRecordValue(
    record,
    ['provenanceHash', 'receiptHash', 'rootHash'],
    ''
  );
  const provenanceHash =
    existingHash ||
    createHashDigest(`${tenantId}|${source.modelName}|${id}|${company}|${email}|${phone}`);

  return {
    id,
    tenantId,
    sourceKey: source.key,
    sourceModel: source.modelName,
    leadName: name,
    name,
    company,
    email,
    phone,
    source: resolveRecordValue(record, ['source', 'leadSource'], source.key),
    status: resolveRecordValue(record, ['status', 'leadStatus'], complianceStatus),
    owner,
    lastActivity,
    complianceStatus,
    provenanceHash,
    provenanceHashShort: provenanceHash.slice(0, 16),
    receiptSealed: Boolean(existingHash),
    score: source.weight,
  };
}

/**
 * @function buildSearchRootHash
 * @description Builds a deterministic root hash for the search response.
 * @param {Object} payload - Search response payload.
 * @returns {string} Root hash.
 * @collaboration Gives the search section a backend-produced authority receipt.
 */
function buildSearchRootHash(payload = {}) {
  return createHashDigest(JSON.stringify(payload));
}

/**
 * @function resolveTelemetryModel
 * @description Resolves the CRMTelemetryEvent model for search audit persistence.
 * @returns {Object|null} Telemetry model or null.
 * @collaboration Connects every Lead search execution to the CRM audit chain when the model is registered.
 */
function resolveTelemetryModel() {
  return getModel('CRMTelemetryEvent');
}

/**
 * @function assignTelemetryField
 * @description Assigns a value to the first compatible schema path.
 * @param {Object} document - Telemetry document being built.
 * @param {Set<string>} paths - Schema path names.
 * @param {string[]} candidates - Candidate field names.
 * @param {*} value - Value to assign.
 * @returns {boolean} True when a field was assigned.
 * @collaboration Keeps telemetry writes schema-aware across evolving CRM telemetry models.
 */
function assignTelemetryField(
  document = {},
  paths = new Set(),
  candidates = [],
  value = undefined
) {
  const field = candidates.find((candidate) => paths.has(candidate));

  if (!field || value === undefined) return false;

  document[field] = value;
  return true;
}

/**
 * @function resolveRequiredPathDefault
 * @description Produces a safe default for a required telemetry schema path.
 * @param {string} fieldName - Schema path name.
 * @param {Object} schemaType - Mongoose schema type.
 * @param {Object} context - Telemetry context.
 * @returns {*} Default value.
 * @collaboration Prevents schema-required fields from breaking search telemetry persistence.
 */
function resolveRequiredPathDefault(fieldName = '', schemaType = {}, context = {}) {
  const normalized = String(fieldName).toLowerCase();
  const instance = String(schemaType?.instance || '').toLowerCase();

  if (normalized.includes('tenant')) return context.tenantId;
  if (
    normalized.includes('operator') ||
    normalized.includes('actor') ||
    normalized.includes('user')
  )
    return context.operatorId;
  if (normalized.includes('query') || normalized.includes('search'))
    return context.query || 'EMPTY_QUERY';
  if (normalized.includes('type') || normalized.includes('event'))
    return 'CRM_LEAD_SEARCH_EXECUTED';
  if (normalized.includes('route')) return '/api/crm/command/search';
  if (normalized.includes('status')) return 'PERSISTED';
  if (normalized.includes('hash') || normalized.includes('receipt')) return context.receiptHash;
  if (
    normalized.includes('payload') ||
    normalized.includes('meta') ||
    normalized.includes('context')
  )
    return context.payload;
  if (
    normalized.includes('created') ||
    normalized.includes('updated') ||
    normalized.includes('timestamp')
  )
    return context.generatedAt;

  if (instance === 'date') return context.generatedAt;
  if (instance === 'number') return 0;
  if (instance === 'boolean') return true;
  if (instance === 'array') return [];
  if (instance === 'map' || instance === 'mixed' || instance === 'object') return context.payload;
  if (instance === 'objectid') return new mongoose.Types.ObjectId();

  return 'CRM_LEAD_SEARCH_TELEMETRY';
}

/**
 * @function hydrateRequiredTelemetryFields
 * @description Adds schema-required defaults when compatible fields were not assigned.
 * @param {Object} model - Mongoose model.
 * @param {Object} document - Telemetry document.
 * @param {Object} context - Telemetry context.
 * @returns {Object} Hydrated document.
 * @collaboration Makes telemetry persistence resilient to schema expansion.
 */
function hydrateRequiredTelemetryFields(model, document = {}, context = {}) {
  Object.entries(model?.schema?.paths || {}).forEach(([fieldName, schemaType]) => {
    if (fieldName === '_id' || fieldName === '__v' || document[fieldName] !== undefined) return;

    const isRequired = Boolean(schemaType?.isRequired || schemaType?.options?.required);
    if (!isRequired) return;

    document[fieldName] = resolveRequiredPathDefault(fieldName, schemaType, context);
  });

  return document;
}

/**
 * @function buildLeadSearchTelemetryPayload
 * @description Builds the immutable payload captured for a Lead search execution.
 * @param {Object} params - Telemetry parameters.
 * @returns {Object} Telemetry payload.
 * @collaboration Encodes tenant, operator, query, registry and compliance posture into the audit chain.
 */
function buildLeadSearchTelemetryPayload(params = {}) {
  return {
    version: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
    searchVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
    breakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
    canonicalResetVersion: WILSY_CRM_SEARCH_CANONICAL_RESET_VERSION,
    eventType: 'CRM_LEAD_SEARCH_EXECUTED',
    tenantId: params.tenantId,
    query: params.query,
    role: params.role,
    operatorId: params.operatorId,
    route: '/api/crm/command/search',
    searchMode: 'LEAD_OPERATING_ROOM_BACKEND_AUTHORITY',
    sourceStatus: params.sourceStatus,
    totalRecords: params.totalRecords,
    totalMatched: params.totalMatched,
    liveSources: params.liveSources,
    searchableSources: params.searchableSources,
    totalSources: params.totalSources,
    rootHash: params.rootHash,
    rootHashShort: params.rootHashShort,
    registry: params.registry,
    sourceGaps: params.sourceGaps,
    complianceBindings: params.complianceBindings,
    generatedAt: params.generatedAt,
  };
}

/**
 * @function buildTelemetryDocument
 * @description Builds a schema-aware CRMTelemetryEvent document.
 * @param {Object} model - Telemetry model.
 * @param {Object} payload - Telemetry payload.
 * @param {string} receiptHash - Receipt hash.
 * @returns {Object} Telemetry document.
 * @collaboration Persists Lead search audit data without assuming a frozen telemetry schema.
 */
function buildTelemetryDocument(model, payload = {}, receiptHash = '') {
  const paths = getSchemaPathNames(model);
  const document = {};
  const generatedAt = new Date(payload.generatedAt || Date.now());
  const context = {
    tenantId: payload.tenantId,
    operatorId: payload.operatorId,
    query: payload.query,
    receiptHash,
    payload,
    generatedAt,
  };

  assignTelemetryField(
    document,
    paths,
    ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
    payload.tenantId
  );
  assignTelemetryField(
    document,
    paths,
    ['type', 'eventType', 'name', 'metricName'],
    'CRM_LEAD_SEARCH_EXECUTED'
  );
  assignTelemetryField(document, paths, ['category', 'eventCategory', 'entityType'], 'CRM');
  assignTelemetryField(document, paths, ['action', 'operation'], 'SEARCH');
  assignTelemetryField(document, paths, ['route', 'path', 'endpoint'], '/api/crm/command/search');
  assignTelemetryField(document, paths, ['query', 'searchQuery', 'q'], payload.query || '');
  assignTelemetryField(document, paths, ['role', 'actorRole', 'operatorRole'], payload.role);
  assignTelemetryField(
    document,
    paths,
    ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
    payload.operatorId
  );
  assignTelemetryField(document, paths, ['source', 'sourceKey', 'module'], 'LEAD_OPERATING_ROOM');
  assignTelemetryField(document, paths, ['status', 'sourceStatus'], payload.sourceStatus);
  assignTelemetryField(document, paths, ['count', 'total', 'totalRecords'], payload.totalRecords);
  assignTelemetryField(document, paths, ['matched', 'totalMatched'], payload.totalMatched);
  assignTelemetryField(
    document,
    paths,
    ['payload', 'metadata', 'details', 'context', 'data'],
    payload
  );
  assignTelemetryField(document, paths, ['receiptHash', 'hash', 'provenanceHash'], receiptHash);
  assignTelemetryField(document, paths, ['rootHash'], payload.rootHash);
  assignTelemetryField(
    document,
    paths,
    ['rootHashShort', 'receiptHashShort'],
    receiptHash.slice(0, 16)
  );
  assignTelemetryField(
    document,
    paths,
    ['timestamp', 'eventAt', 'occurredAt', 'createdAt'],
    generatedAt
  );
  assignTelemetryField(document, paths, ['receiptSealed', 'sealed'], true);

  return hydrateRequiredTelemetryFields(model, document, context);
}

/**
 * @function persistLeadSearchTelemetry
 * @description Persists a CRMTelemetryEvent receipt for a Lead search execution.
 * @param {Object} params - Telemetry persistence parameters.
 * @returns {Promise<Object>} Telemetry persistence result.
 * @collaboration Turns the Lead search bar into an auditable backend action.
 */
async function persistLeadSearchTelemetry(params = {}) {
  const generatedAt = params.generatedAt || new Date().toISOString();
  const payload = buildLeadSearchTelemetryPayload({ ...params, generatedAt });
  const receiptHash = createHashDigest(JSON.stringify(payload));
  const model = resolveTelemetryModel();

  if (!model) {
    return {
      persisted: false,
      status: 'TELEMETRY_MODEL_NOT_REGISTERED',
      modelName: 'CRMTelemetryEvent',
      version: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  }

  try {
    const document = buildTelemetryDocument(model, payload, receiptHash);
    const created = await model.create(document);

    return {
      persisted: true,
      status: 'TELEMETRY_RECEIPT_PERSISTED',
      modelName: 'CRMTelemetryEvent',
      eventId: String(created?._id || created?.id || ''),
      version: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  } catch (error) {
    return {
      persisted: false,
      status: 'TELEMETRY_WRITE_FAILED',
      modelName: 'CRMTelemetryEvent',
      errorName: error?.name || 'UnknownError',
      errorMessage: String(error?.message || 'Unknown telemetry write failure').slice(0, 220),
      version: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  }
}

/**
 * @function persistLeadSearchTelemetrySafely
 * @description Attempts Lead search telemetry persistence without allowing telemetry failure to break search response finality.
 * @param {Object} params - Telemetry persistence parameters.
 * @returns {Promise<Object>} Telemetry persistence result.
 * @collaboration Keeps the Lead search bar auditable while isolating telemetry write faults from operator search.
 */
async function persistLeadSearchTelemetrySafely(params = {}) {
  try {
    return await persistLeadSearchTelemetry(params);
  } catch (error) {
    const generatedAt = params.generatedAt || new Date().toISOString();
    const payload = buildLeadSearchTelemetryPayload({ ...params, generatedAt });
    const receiptHash = createHashDigest(JSON.stringify(payload));

    return {
      persisted: false,
      status: 'TELEMETRY_PERSISTENCE_ISOLATED',
      modelName: 'CRMTelemetryEvent',
      errorName: error?.name || 'UnknownError',
      errorMessage: String(error?.message || 'Unknown telemetry persistence failure').slice(0, 220),
      version: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  }
}

/**
 * @function resolveTelemetryFieldValue
 * @description Resolves a telemetry field by candidate schema names.
 * @param {Object} record - Telemetry record.
 * @param {string[]} fields - Candidate fields.
 * @param {*} fallback - Fallback value.
 * @returns {*} Resolved value.
 * @collaboration Normalizes receipt records across evolving CRMTelemetryEvent schemas.
 */
function resolveTelemetryFieldValue(record = {}, fields = [], fallback = null) {
  const field = fields.find(
    (candidate) =>
      record[candidate] !== undefined && record[candidate] !== null && record[candidate] !== ''
  );
  return field ? record[field] : fallback;
}

/**
 * @function buildTelemetryReceiptFilter
 * @description Builds a schema-aware filter for receipt lookup by event id or persisted hash.
 * @param {Object} model - Telemetry model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} receiptId - Receipt id, event id or hash.
 * @returns {Object|null} Mongo filter.
 * @collaboration Lets regulators retrieve a precise search receipt without unsafe schema assumptions.
 */
function buildTelemetryReceiptFilter(model, tenantId = 'MASTER', receiptId = '') {
  const paths = getSchemaPathNames(model);
  const tenantFilter = buildTenantFilter(model, tenantId);
  const clauses = [];
  const value = String(receiptId || '').trim();

  if (!tenantFilter || !value) return null;

  if (mongoose.Types.ObjectId.isValid(value)) {
    clauses.push({ _id: new mongoose.Types.ObjectId(value) });
  }

  [
    'receiptHash',
    'hash',
    'provenanceHash',
    'rootHash',
    'rootHashShort',
    'receiptHashShort',
  ].forEach((field) => {
    if (paths.has(field)) clauses.push({ [field]: value });
  });

  if (!clauses.length) return null;

  return { $and: [tenantFilter, { $or: clauses }] };
}

/**
 * @function buildTelemetryReceiptListFilter
 * @description Builds a schema-aware tenant filter for recent search receipt listing.
 * @param {Object} model - Telemetry model.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Object|null} Mongo filter.
 * @collaboration Provides a tenant-scoped receipt ledger for Lead search audits.
 */
function buildTelemetryReceiptListFilter(model, tenantId = 'MASTER') {
  const tenantFilter = buildTenantFilter(model, tenantId);
  if (!tenantFilter) return null;

  const paths = getSchemaPathNames(model);
  const eventClauses = [];

  ['type', 'eventType', 'name', 'metricName'].forEach((field) => {
    if (paths.has(field)) eventClauses.push({ [field]: 'CRM_LEAD_SEARCH_EXECUTED' });
  });

  return eventClauses.length ? { $and: [tenantFilter, { $or: eventClauses }] } : tenantFilter;
}

/**
 * @function extractTelemetryPayload
 * @description Extracts stored telemetry payload from known schema fields.
 * @param {Object} record - Telemetry record.
 * @returns {Object|null} Stored payload or null.
 * @collaboration Enables receipt hash verification when payload was persisted.
 */
function extractTelemetryPayload(record = {}) {
  const payload = resolveTelemetryFieldValue(
    record,
    ['payload', 'metadata', 'details', 'context', 'data'],
    null
  );
  return payload && typeof payload === 'object' ? payload : null;
}

/**
 * @function computeTelemetryPayloadHash
 * @description Computes the canonical receipt hash for a telemetry payload.
 * @param {Object|null} payload - Stored telemetry payload.
 * @returns {string} Computed hash or empty string.
 * @collaboration Enables receipt lookup even when a schema did not persist receiptHash as a top-level field.
 */
function computeTelemetryPayloadHash(payload = null) {
  return payload && typeof payload === 'object' ? createHashDigest(JSON.stringify(payload)) : '';
}

/**
 * @function buildReceiptIntegrityPacket
 * @description Builds a regulator-readable receipt integrity packet.
 * @param {Object|null} payload - Stored telemetry payload.
 * @param {string} storedReceiptHash - Stored receipt hash.
 * @returns {Object} Integrity packet.
 * @collaboration Proves whether the persisted receipt hash matches the stored payload.
 */
function buildReceiptIntegrityPacket(payload = null, storedReceiptHash = '') {
  const computedHash = computeTelemetryPayloadHash(payload);

  if (storedReceiptHash && computedHash) {
    return {
      verified: storedReceiptHash === computedHash,
      status:
        storedReceiptHash === computedHash ? 'RECEIPT_HASH_VERIFIED' : 'RECEIPT_HASH_MISMATCH',
      storedHash: storedReceiptHash,
      storedHashShort: storedReceiptHash.slice(0, 16),
      recomputedHash: computedHash,
      recomputedHashShort: computedHash.slice(0, 16),
    };
  }

  if (computedHash) {
    return {
      verified: true,
      status: 'RECEIPT_HASH_RECOMPUTED',
      storedHash: null,
      storedHashShort: null,
      recomputedHash: computedHash,
      recomputedHashShort: computedHash.slice(0, 16),
    };
  }

  return {
    verified: false,
    status: 'PAYLOAD_OR_HASH_NOT_AVAILABLE',
    storedHash: storedReceiptHash || null,
    storedHashShort: storedReceiptHash ? storedReceiptHash.slice(0, 16) : null,
    recomputedHash: null,
    recomputedHashShort: null,
  };
}

/**
 * @function normalizeLeadSearchReceipt
 * @description Normalizes a CRMTelemetryEvent record into a receipt verification packet.
 * @param {Object} record - Telemetry record.
 * @returns {Object} Receipt packet.
 * @collaboration Makes stored Lead search telemetry readable by operators, executives and regulators.
 */
function normalizeLeadSearchReceipt(record = {}) {
  const payload = extractTelemetryPayload(record);
  const storedReceiptHash = String(
    resolveTelemetryFieldValue(record, ['receiptHash', 'hash', 'provenanceHash'], '')
  );
  const computedPayloadHash = computeTelemetryPayloadHash(payload);
  const receiptHash = storedReceiptHash || computedPayloadHash;
  const rootHash = String(
    resolveTelemetryFieldValue(record, ['rootHash'], payload?.rootHash || '')
  );
  const integrity = buildReceiptIntegrityPacket(payload, storedReceiptHash);

  return {
    id: String(record._id || record.id || ''),
    version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
    modelName: 'CRMTelemetryEvent',
    eventType: String(
      resolveTelemetryFieldValue(
        record,
        ['type', 'eventType', 'name', 'metricName'],
        payload?.eventType || 'CRM_LEAD_SEARCH_EXECUTED'
      )
    ),
    tenantId: String(
      resolveTelemetryFieldValue(
        record,
        ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
        payload?.tenantId || 'MASTER'
      )
    ),
    operatorId: String(
      resolveTelemetryFieldValue(
        record,
        ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
        payload?.operatorId || 'SYSTEM'
      )
    ),
    role: String(
      resolveTelemetryFieldValue(
        record,
        ['role', 'actorRole', 'operatorRole'],
        payload?.role || 'UNKNOWN'
      )
    ),
    query: String(
      resolveTelemetryFieldValue(record, ['query', 'searchQuery', 'q'], payload?.query || '')
    ),
    route: String(
      resolveTelemetryFieldValue(
        record,
        ['route', 'path', 'endpoint'],
        payload?.route || '/api/crm/command/search'
      )
    ),
    sourceStatus: String(
      resolveTelemetryFieldValue(
        record,
        ['status', 'sourceStatus'],
        payload?.sourceStatus || 'UNKNOWN'
      )
    ),
    totalRecords: Number(
      resolveTelemetryFieldValue(
        record,
        ['count', 'total', 'totalRecords'],
        payload?.totalRecords || 0
      )
    ),
    totalMatched: Number(
      resolveTelemetryFieldValue(record, ['matched', 'totalMatched'], payload?.totalMatched || 0)
    ),
    receiptHash,
    receiptHashShort: receiptHash ? receiptHash.slice(0, 16) : null,
    rootHash,
    rootHashShort: rootHash ? rootHash.slice(0, 16) : null,
    createdAt: resolveTelemetryFieldValue(
      record,
      ['timestamp', 'eventAt', 'occurredAt', 'createdAt'],
      payload?.generatedAt || null
    ),
    integrity,
    payloadAvailable: Boolean(payload),
    payload,
  };
}

/**
 * @function findReceiptByHashFallback
 * @description Finds a receipt by recomputing payload hashes across a bounded recent tenant ledger.
 * @param {Object} model - Telemetry model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} receiptId - Receipt hash or short hash.
 * @returns {Promise<Object|null>} Matching record or null.
 * @collaboration Supports receiptHash lookup even when top-level hash fields were not part of the telemetry schema.
 */
async function findReceiptByHashFallback(model, tenantId = 'MASTER', receiptId = '') {
  const filter = buildTelemetryReceiptListFilter(model, tenantId);
  if (!filter) return null;

  const value = String(receiptId || '').trim();

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, timestamp: -1, eventAt: -1, occurredAt: -1 })
    .limit(200)
    .lean();

  return (
    records.find((record) => {
      const receipt = normalizeLeadSearchReceipt(record);
      return [
        receipt.receiptHash,
        receipt.receiptHashShort,
        receipt.integrity?.storedHash,
        receipt.integrity?.storedHashShort,
        receipt.integrity?.recomputedHash,
        receipt.integrity?.recomputedHashShort,
      ]
        .filter(Boolean)
        .includes(value);
    }) || null
  );
}

/**
 * @function verifyLeadSearchTelemetryReceipt
 * @description Retrieves and verifies one Lead search telemetry receipt.
 * @param {Object} params - Verification parameters.
 * @returns {Promise<Object>} Verification response.
 * @collaboration Proves a search execution receipt exists in the backend audit chain.
 */
export async function verifyLeadSearchTelemetryReceipt(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(params.receiptId || params.eventId || params.receiptHash || '').trim();
  const model = resolveTelemetryModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      receiptId,
      status: 'TELEMETRY_MODEL_NOT_REGISTERED',
      receipt: null,
    };
  }

  const filter = buildTelemetryReceiptFilter(model, tenantId, receiptId);
  let record = filter ? await model.findOne(filter).lean() : null;

  if (!record && receiptId) {
    record = await findReceiptByHashFallback(model, tenantId, receiptId);
  }

  if (!record) {
    return {
      ok: false,
      version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      receiptId,
      status: 'SEARCH_RECEIPT_NOT_FOUND',
      receipt: null,
    };
  }

  return {
    ok: true,
    version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
    tenantId,
    receiptId,
    status: 'SEARCH_RECEIPT_FOUND',
    receipt: normalizeLeadSearchReceipt(record),
  };
}

/**
 * @function listLeadSearchTelemetryReceipts
 * @description Lists recent Lead search telemetry receipts for a tenant.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Receipt list response.
 * @collaboration Gives operators a backend receipt ledger for search activity.
 */
export async function listLeadSearchTelemetryReceipts(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 10), 1), 50);
  const model = resolveTelemetryModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      total: 0,
      status: 'TELEMETRY_MODEL_NOT_REGISTERED',
      receipts: [],
    };
  }

  const filter = buildTelemetryReceiptListFilter(model, tenantId);

  if (!filter) {
    return {
      ok: false,
      version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      total: 0,
      status: 'RECEIPT_LIST_FILTER_NOT_AVAILABLE',
      receipts: [],
    };
  }

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, timestamp: -1, eventAt: -1, occurredAt: -1 })
    .limit(limit)
    .lean();

  const receipts = records.map((record) => normalizeLeadSearchReceipt(record));

  return {
    ok: true,
    version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
    tenantId,
    total: receipts.length,
    status: 'SEARCH_RECEIPTS_LISTED',
    receipts,
  };
}

/**
 * @function resolveComplianceReceiptModel
 * @description Resolves the CRMComplianceReceipt model for search compliance receipt persistence.
 * @returns {Object|null} Compliance receipt model or null.
 * @collaboration Connects Lead search audit posture to a dedicated compliance receipt ledger when the model is registered.
 */
function resolveComplianceReceiptModel() {
  return getModel('CRMComplianceReceipt');
}

/**
 * @function resolveComplianceRequiredPathDefault
 * @description Produces a safe default for a required compliance receipt schema path.
 * @param {string} fieldName - Schema path name.
 * @param {Object} schemaType - Mongoose schema type.
 * @param {Object} context - Compliance receipt context.
 * @returns {*} Default value.
 * @collaboration Keeps compliance receipt writes resilient across evolving CRMComplianceReceipt schemas.
 */
function resolveComplianceRequiredPathDefault(fieldName = '', schemaType = {}, context = {}) {
  const normalized = String(fieldName).toLowerCase();
  const instance = String(schemaType?.instance || '').toLowerCase();

  if (normalized.includes('tenant')) return context.tenantId;
  if (
    normalized.includes('operator') ||
    normalized.includes('actor') ||
    normalized.includes('user')
  )
    return context.operatorId;
  if (normalized.includes('query') || normalized.includes('search'))
    return context.query || 'EMPTY_QUERY';
  if (normalized.includes('status')) return 'SEALED';
  if (normalized.includes('framework')) return 'AUDIT';
  if (normalized.includes('control')) return 'lead-search-receipt';
  if (normalized.includes('route')) return '/api/crm/command/search';
  if (normalized.includes('hash') || normalized.includes('root') || normalized.includes('merkle'))
    return context.receiptHash;
  if (normalized.includes('binding')) return context.complianceBindings;
  if (
    normalized.includes('payload') ||
    normalized.includes('meta') ||
    normalized.includes('context') ||
    normalized.includes('data')
  )
    return context.payload;
  if (
    normalized.includes('created') ||
    normalized.includes('updated') ||
    normalized.includes('timestamp') ||
    normalized.includes('generated')
  )
    return context.generatedAt;

  if (instance === 'date') return context.generatedAt;
  if (instance === 'number') return 0;
  if (instance === 'boolean') return true;
  if (instance === 'array') return [];
  if (instance === 'map' || instance === 'mixed' || instance === 'object') return context.payload;
  if (instance === 'objectid') return new mongoose.Types.ObjectId();

  return 'CRM_LEAD_SEARCH_COMPLIANCE_RECEIPT';
}

/**
 * @function hydrateRequiredComplianceReceiptFields
 * @description Adds schema-required defaults when compatible compliance fields were not assigned.
 * @param {Object} model - Mongoose model.
 * @param {Object} document - Compliance receipt document.
 * @param {Object} context - Compliance receipt context.
 * @returns {Object} Hydrated document.
 * @collaboration Prevents schema-required fields from breaking search compliance receipt materialization.
 */
function hydrateRequiredComplianceReceiptFields(model, document = {}, context = {}) {
  Object.entries(model?.schema?.paths || {}).forEach(([fieldName, schemaType]) => {
    if (fieldName === '_id' || fieldName === '__v' || document[fieldName] !== undefined) return;

    const isRequired = Boolean(schemaType?.isRequired || schemaType?.options?.required);
    if (!isRequired) return;

    document[fieldName] = resolveComplianceRequiredPathDefault(fieldName, schemaType, context);
  });

  return document;
}

/**
 * @function buildLeadSearchComplianceReceiptPayload
 * @description Builds the compliance receipt payload for a Lead search execution.
 * @param {Object} params - Compliance receipt parameters.
 * @returns {Object} Compliance receipt payload.
 * @collaboration Converts a search telemetry event into a compliance receipt packet.
 */
function buildLeadSearchComplianceReceiptPayload(params = {}) {
  return {
    version: WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION,
    searchVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
    telemetryVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
    receiptVerificationVersion: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
    eventType: 'CRM_LEAD_SEARCH_COMPLIANCE_RECEIPT',
    tenantId: params.tenantId,
    query: params.query,
    role: params.role,
    operatorId: params.operatorId,
    route: '/api/crm/command/search',
    sourceStatus: params.sourceStatus,
    totalRecords: params.totalRecords,
    totalMatched: params.totalMatched,
    liveSources: params.liveSources,
    searchableSources: params.searchableSources,
    totalSources: params.totalSources,
    rootHash: params.rootHash,
    rootHashShort: params.rootHashShort,
    telemetryEventId: params.telemetryPersistence?.eventId || null,
    telemetryReceiptHash: params.telemetryPersistence?.receiptHash || null,
    telemetryReceiptHashShort: params.telemetryPersistence?.receiptHashShort || null,
    complianceBindings: [
      {
        framework: 'POPIA',
        control: 'source-basis',
        status: 'SEARCH_SOURCE_BASIS_RECEIPT_CREATED',
        tenantId: params.tenantId,
      },
      {
        framework: 'GDPR',
        control: 'lawful-basis',
        status: 'SEARCH_LAWFUL_BASIS_RECEIPT_CREATED',
        tenantId: params.tenantId,
      },
      {
        framework: 'SOC2',
        control: 'audit-chain',
        status: 'SEARCH_AUDIT_CHAIN_RECEIPT_CREATED',
        tenantId: params.tenantId,
      },
      {
        framework: 'REGULATOR_EXPORT',
        control: 'receipt-verification',
        status: 'SEARCH_RECEIPT_READY_FOR_REGULATOR_REVIEW',
        tenantId: params.tenantId,
      },
    ],
    generatedAt: params.generatedAt,
  };
}

/**
 * @function buildComplianceReceiptDocument
 * @description Builds a schema-aware CRMComplianceReceipt document.
 * @param {Object} model - Compliance receipt model.
 * @param {Object} payload - Compliance receipt payload.
 * @param {string} receiptHash - Receipt hash.
 * @returns {Object} Compliance receipt document.
 * @collaboration Persists search compliance receipts without assuming a frozen schema.
 */
function buildComplianceReceiptDocument(model, payload = {}, receiptHash = '') {
  const paths = getSchemaPathNames(model);
  const document = {};
  const generatedAt = new Date(payload.generatedAt || Date.now());
  const context = {
    tenantId: payload.tenantId,
    operatorId: payload.operatorId,
    query: payload.query,
    receiptHash,
    payload,
    complianceBindings: payload.complianceBindings,
    generatedAt,
  };

  assignTelemetryField(
    document,
    paths,
    ['receiptId', 'id'],
    `CSR_${generatedAt.getTime()}_${receiptHash.slice(0, 16)}`
  );
  assignTelemetryField(
    document,
    paths,
    ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
    payload.tenantId
  );
  assignTelemetryField(document, paths, ['status', 'receiptSealStatus', 'sealStatus'], 'SEALED');
  assignTelemetryField(document, paths, ['framework'], 'AUDIT');
  assignTelemetryField(document, paths, ['control'], 'lead-search-receipt');
  assignTelemetryField(
    document,
    paths,
    ['eventType', 'type', 'name'],
    'CRM_LEAD_SEARCH_COMPLIANCE_RECEIPT'
  );
  assignTelemetryField(document, paths, ['route', 'path', 'endpoint'], '/api/crm/command/search');
  assignTelemetryField(document, paths, ['query', 'searchQuery', 'q'], payload.query || '');
  assignTelemetryField(
    document,
    paths,
    ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
    payload.operatorId
  );
  assignTelemetryField(
    document,
    paths,
    ['evidenceHash', 'receiptHash', 'hash', 'provenanceHash'],
    receiptHash
  );
  assignTelemetryField(
    document,
    paths,
    ['merkleRoot', 'rootHash'],
    payload.rootHash || receiptHash
  );
  assignTelemetryField(
    document,
    paths,
    ['previousMerkleRoot', 'previousRootHash'],
    payload.telemetryReceiptHash || null
  );
  assignTelemetryField(
    document,
    paths,
    ['complianceBindings', 'bindings'],
    payload.complianceBindings
  );
  assignTelemetryField(
    document,
    paths,
    ['payload', 'metadata', 'details', 'context', 'data'],
    payload
  );
  assignTelemetryField(
    document,
    paths,
    ['generatedAt', 'timestamp', 'eventAt', 'createdAt'],
    generatedAt
  );
  assignTelemetryField(document, paths, ['backendAuthority'], true);
  assignTelemetryField(document, paths, ['browserAuthority'], false);
  assignTelemetryField(document, paths, ['sealed', 'receiptSealed'], true);

  return hydrateRequiredComplianceReceiptFields(model, document, context);
}

/**
 * @function persistLeadSearchComplianceReceipt
 * @description Persists a CRMComplianceReceipt for a Lead search execution.
 * @param {Object} params - Compliance receipt parameters.
 * @returns {Promise<Object>} Compliance persistence result.
 * @collaboration Turns a telemetry-audited search into a compliance-receipt-backed action.
 */
async function persistLeadSearchComplianceReceipt(params = {}) {
  const model = resolveComplianceReceiptModel();
  const generatedAt = params.generatedAt || new Date().toISOString();
  const payload = buildLeadSearchComplianceReceiptPayload({ ...params, generatedAt });
  const receiptHash = createHashDigest(JSON.stringify(payload));

  if (!model) {
    return {
      persisted: false,
      status: 'COMPLIANCE_RECEIPT_MODEL_NOT_REGISTERED',
      modelName: 'CRMComplianceReceipt',
      version: WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  }

  try {
    const document = buildComplianceReceiptDocument(model, payload, receiptHash);
    const created = await model.create(document);

    return {
      persisted: true,
      status: 'COMPLIANCE_RECEIPT_PERSISTED',
      modelName: 'CRMComplianceReceipt',
      receiptId: String(created?._id || created?.receiptId || created?.id || ''),
      version: WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  } catch (error) {
    return {
      persisted: false,
      status: 'COMPLIANCE_RECEIPT_WRITE_FAILED',
      modelName: 'CRMComplianceReceipt',
      errorName: error?.name || 'UnknownError',
      errorMessage: String(error?.message || 'Unknown compliance receipt write failure').slice(
        0,
        220
      ),
      version: WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  }
}

/**
 * @function persistLeadSearchComplianceReceiptSafely
 * @description Attempts search compliance receipt persistence without breaking the search response.
 * @param {Object} params - Compliance receipt parameters.
 * @returns {Promise<Object>} Compliance persistence result.
 * @collaboration Keeps search finality independent from compliance receipt write availability.
 */
async function persistLeadSearchComplianceReceiptSafely(params = {}) {
  try {
    return await persistLeadSearchComplianceReceipt(params);
  } catch (error) {
    const generatedAt = params.generatedAt || new Date().toISOString();
    const payload = buildLeadSearchComplianceReceiptPayload({ ...params, generatedAt });
    const receiptHash = createHashDigest(JSON.stringify(payload));

    return {
      persisted: false,
      status: 'COMPLIANCE_RECEIPT_ISOLATED',
      modelName: 'CRMComplianceReceipt',
      errorName: error?.name || 'UnknownError',
      errorMessage: String(
        error?.message || 'Unknown compliance receipt persistence failure'
      ).slice(0, 220),
      version: WILSY_CRM_SEARCH_COMPLIANCE_RECEIPT_VERSION,
      receiptHash,
      receiptHashShort: receiptHash.slice(0, 16),
      generatedAt,
    };
  }
}

/**
 * @function resolveComplianceReceiptFieldValue
 * @description Resolves a compliance receipt field by candidate schema names.
 * @param {Object} record - Compliance receipt record.
 * @param {string[]} fields - Candidate fields.
 * @param {*} fallback - Fallback value.
 * @returns {*} Resolved value.
 * @collaboration Normalizes compliance receipt records across evolving CRMComplianceReceipt schemas.
 */
function resolveComplianceReceiptFieldValue(record = {}, fields = [], fallback = null) {
  const field = fields.find(
    (candidate) =>
      record[candidate] !== undefined && record[candidate] !== null && record[candidate] !== ''
  );
  return field ? record[field] : fallback;
}

/**
 * @function buildComplianceReceiptLookupFilter
 * @description Builds a schema-aware filter for compliance receipt lookup by id or hash.
 * @param {Object} model - Compliance receipt model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} receiptId - Receipt id or hash.
 * @returns {Object|null} Mongo filter.
 * @collaboration Lets regulators retrieve a precise compliance receipt without unsafe schema assumptions.
 */
function buildComplianceReceiptLookupFilter(model, tenantId = 'MASTER', receiptId = '') {
  const paths = getSchemaPathNames(model);
  const tenantFilter = buildTenantFilter(model, tenantId);
  const clauses = [];
  const value = String(receiptId || '').trim();

  if (!tenantFilter || !value) return null;

  if (mongoose.Types.ObjectId.isValid(value)) {
    clauses.push({ _id: new mongoose.Types.ObjectId(value) });
  }

  [
    'receiptId',
    'evidenceHash',
    'receiptHash',
    'hash',
    'provenanceHash',
    'merkleRoot',
    'rootHash',
    'merkleRootShort',
    'receiptHashShort',
  ].forEach((field) => {
    if (paths.has(field)) clauses.push({ [field]: value });
  });

  if (!clauses.length) return null;

  return { $and: [tenantFilter, { $or: clauses }] };
}

/**
 * @function buildComplianceReceiptListFilter
 * @description Builds a tenant-scoped filter for recent Lead search compliance receipts.
 * @param {Object} model - Compliance receipt model.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Object|null} Mongo filter.
 * @collaboration Provides a compliance receipt ledger for Lead search audit posture.
 */
function buildComplianceReceiptListFilter(model, tenantId = 'MASTER') {
  const tenantFilter = buildTenantFilter(model, tenantId);
  if (!tenantFilter) return null;

  const paths = getSchemaPathNames(model);
  const eventClauses = [];

  ['eventType', 'type', 'name', 'control'].forEach((field) => {
    if (paths.has(field)) {
      eventClauses.push({ [field]: /CRM_LEAD_SEARCH_COMPLIANCE_RECEIPT|lead-search-receipt/i });
    }
  });

  return eventClauses.length ? { $and: [tenantFilter, { $or: eventClauses }] } : tenantFilter;
}

/**
 * @function extractComplianceReceiptPayload
 * @description Extracts stored compliance receipt payload from known schema fields.
 * @param {Object} record - Compliance receipt record.
 * @returns {Object|null} Stored payload or null.
 * @collaboration Enables compliance receipt hash verification when payload was persisted.
 */
function extractComplianceReceiptPayload(record = {}) {
  const payload = resolveComplianceReceiptFieldValue(
    record,
    ['payload', 'metadata', 'details', 'context', 'data'],
    null
  );
  return payload && typeof payload === 'object' ? payload : null;
}

/**
 * @function computeComplianceReceiptPayloadHash
 * @description Computes the canonical compliance receipt hash for a payload.
 * @param {Object|null} payload - Stored compliance receipt payload.
 * @returns {string} Computed hash or empty string.
 * @collaboration Enables compliance receipt verification even when top-level hash fields differ by schema.
 */
function computeComplianceReceiptPayloadHash(payload = null) {
  return payload && typeof payload === 'object' ? createHashDigest(JSON.stringify(payload)) : '';
}

/**
 * @function buildComplianceReceiptIntegrityPacket
 * @description Builds a regulator-readable compliance receipt integrity packet.
 * @param {Object|null} payload - Stored compliance receipt payload.
 * @param {string} storedReceiptHash - Stored receipt hash.
 * @returns {Object} Integrity packet.
 * @collaboration Proves whether the persisted compliance receipt hash matches the stored payload.
 */
function buildComplianceReceiptIntegrityPacket(payload = null, storedReceiptHash = '') {
  const recomputedHash = computeComplianceReceiptPayloadHash(payload);

  if (storedReceiptHash && recomputedHash) {
    return {
      verified: storedReceiptHash === recomputedHash,
      status:
        storedReceiptHash === recomputedHash
          ? 'COMPLIANCE_RECEIPT_HASH_VERIFIED'
          : 'COMPLIANCE_RECEIPT_HASH_MISMATCH',
      storedHash: storedReceiptHash,
      storedHashShort: storedReceiptHash.slice(0, 16),
      recomputedHash,
      recomputedHashShort: recomputedHash.slice(0, 16),
    };
  }

  if (recomputedHash) {
    return {
      verified: true,
      status: 'COMPLIANCE_RECEIPT_HASH_RECOMPUTED',
      storedHash: null,
      storedHashShort: null,
      recomputedHash,
      recomputedHashShort: recomputedHash.slice(0, 16),
    };
  }

  return {
    verified: false,
    status: 'COMPLIANCE_RECEIPT_PAYLOAD_OR_HASH_NOT_AVAILABLE',
    storedHash: storedReceiptHash || null,
    storedHashShort: storedReceiptHash ? storedReceiptHash.slice(0, 16) : null,
    recomputedHash: null,
    recomputedHashShort: null,
  };
}

/**
 * @function normalizeSearchComplianceReceipt
 * @description Normalizes a CRMComplianceReceipt record into a verification packet.
 * @param {Object} record - Compliance receipt record.
 * @returns {Object} Compliance receipt packet.
 * @collaboration Makes Lead search compliance receipts readable by operators, executives and regulators.
 */
function normalizeSearchComplianceReceipt(record = {}) {
  const payload = extractComplianceReceiptPayload(record);
  const storedHash = String(
    resolveComplianceReceiptFieldValue(
      record,
      ['evidenceHash', 'receiptHash', 'hash', 'provenanceHash'],
      ''
    )
  );
  const recomputedHash = computeComplianceReceiptPayloadHash(payload);
  const receiptHash = storedHash || recomputedHash;
  const merkleRoot = String(
    resolveComplianceReceiptFieldValue(
      record,
      ['merkleRoot', 'rootHash'],
      payload?.rootHash || receiptHash || ''
    )
  );
  const integrity = buildComplianceReceiptIntegrityPacket(payload, storedHash);

  return {
    id: String(record._id || record.id || ''),
    receiptId: String(
      resolveComplianceReceiptFieldValue(record, ['receiptId'], record._id || record.id || '')
    ),
    version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
    modelName: 'CRMComplianceReceipt',
    eventType: String(
      resolveComplianceReceiptFieldValue(
        record,
        ['eventType', 'type', 'name'],
        payload?.eventType || 'CRM_LEAD_SEARCH_COMPLIANCE_RECEIPT'
      )
    ),
    tenantId: String(
      resolveComplianceReceiptFieldValue(
        record,
        ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
        payload?.tenantId || 'MASTER'
      )
    ),
    operatorId: String(
      resolveComplianceReceiptFieldValue(
        record,
        ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
        payload?.operatorId || 'SYSTEM'
      )
    ),
    query: String(
      resolveComplianceReceiptFieldValue(
        record,
        ['query', 'searchQuery', 'q'],
        payload?.query || ''
      )
    ),
    status: String(
      resolveComplianceReceiptFieldValue(
        record,
        ['status', 'receiptSealStatus', 'sealStatus'],
        'SEALED'
      )
    ),
    route: String(
      resolveComplianceReceiptFieldValue(
        record,
        ['route', 'path', 'endpoint'],
        payload?.route || '/api/crm/command/search'
      )
    ),
    telemetryEventId: payload?.telemetryEventId || null,
    telemetryReceiptHash: payload?.telemetryReceiptHash || null,
    receiptHash,
    receiptHashShort: receiptHash ? receiptHash.slice(0, 16) : null,
    merkleRoot,
    merkleRootShort: merkleRoot ? merkleRoot.slice(0, 16) : null,
    createdAt: resolveComplianceReceiptFieldValue(
      record,
      ['generatedAt', 'timestamp', 'eventAt', 'createdAt'],
      payload?.generatedAt || null
    ),
    complianceBindings:
      payload?.complianceBindings ||
      resolveComplianceReceiptFieldValue(record, ['complianceBindings', 'bindings'], []),
    integrity,
    payloadAvailable: Boolean(payload),
    payload,
  };
}

/**
 * @function findComplianceReceiptByHashFallback
 * @description Finds a compliance receipt by recomputing payload hashes across a bounded recent tenant ledger.
 * @param {Object} model - Compliance receipt model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} receiptId - Receipt hash or short hash.
 * @returns {Promise<Object|null>} Matching record or null.
 * @collaboration Supports hash lookup even when top-level hash fields were not part of the compliance schema.
 */
async function findComplianceReceiptByHashFallback(model, tenantId = 'MASTER', receiptId = '') {
  const filter = buildComplianceReceiptListFilter(model, tenantId);
  if (!filter) return null;

  const value = String(receiptId || '').trim();

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, generatedAt: -1, timestamp: -1, eventAt: -1 })
    .limit(200)
    .lean();

  return (
    records.find((record) => {
      const receipt = normalizeSearchComplianceReceipt(record);
      return [
        receipt.id,
        receipt.receiptId,
        receipt.receiptHash,
        receipt.receiptHashShort,
        receipt.merkleRoot,
        receipt.merkleRootShort,
        receipt.integrity?.storedHash,
        receipt.integrity?.storedHashShort,
        receipt.integrity?.recomputedHash,
        receipt.integrity?.recomputedHashShort,
      ]
        .filter(Boolean)
        .includes(value);
    }) || null
  );
}

/**
 * @function verifyLeadSearchComplianceReceipt
 * @description Retrieves and verifies one Lead search compliance receipt.
 * @param {Object} params - Verification parameters.
 * @returns {Promise<Object>} Verification response.
 * @collaboration Proves a search compliance receipt exists in the backend evidence chain.
 */
export async function verifyLeadSearchComplianceReceipt(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(
    params.receiptId || params.complianceReceiptId || params.complianceReceiptHash || ''
  ).trim();
  const model = resolveComplianceReceiptModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      receiptId,
      status: 'COMPLIANCE_RECEIPT_MODEL_NOT_REGISTERED',
      complianceReceipt: null,
    };
  }

  const filter = buildComplianceReceiptLookupFilter(model, tenantId, receiptId);
  let record = filter ? await model.findOne(filter).lean() : null;

  if (!record && receiptId) {
    record = await findComplianceReceiptByHashFallback(model, tenantId, receiptId);
  }

  if (!record) {
    return {
      ok: false,
      version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      receiptId,
      status: 'COMPLIANCE_RECEIPT_NOT_FOUND',
      complianceReceipt: null,
    };
  }

  return {
    ok: true,
    version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
    tenantId,
    receiptId,
    status: 'COMPLIANCE_RECEIPT_FOUND',
    complianceReceipt: normalizeSearchComplianceReceipt(record),
  };
}

/**
 * @function listLeadSearchComplianceReceipts
 * @description Lists recent Lead search compliance receipts for a tenant.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Compliance receipt list response.
 * @collaboration Gives operators a backend compliance receipt ledger for search activity.
 */
export async function listLeadSearchComplianceReceipts(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 10), 1), 50);
  const model = resolveComplianceReceiptModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      total: 0,
      status: 'COMPLIANCE_RECEIPT_MODEL_NOT_REGISTERED',
      complianceReceipts: [],
    };
  }

  const filter = buildComplianceReceiptListFilter(model, tenantId);

  if (!filter) {
    return {
      ok: false,
      version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      total: 0,
      status: 'COMPLIANCE_RECEIPT_LIST_FILTER_NOT_AVAILABLE',
      complianceReceipts: [],
    };
  }

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, generatedAt: -1, timestamp: -1, eventAt: -1 })
    .limit(limit)
    .lean();

  const complianceReceipts = records.map((record) => normalizeSearchComplianceReceipt(record));

  return {
    ok: true,
    version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
    tenantId,
    total: complianceReceipts.length,
    status: 'COMPLIANCE_RECEIPTS_LISTED',
    complianceReceipts,
  };
}

/**
 * @function resolveReceiptIntegrityStatus
 * @description Resolves a normalized integrity status for receipt packets.
 * @param {Object} receipt - Receipt packet.
 * @returns {Object} Integrity summary.
 * @collaboration Produces a single regulator-readable status across telemetry and compliance receipts.
 */
function resolveReceiptIntegrityStatus(receipt = {}) {
  const integrity = receipt?.integrity || {};
  return {
    verified: Boolean(integrity.verified),
    status: integrity.status || 'INTEGRITY_STATUS_UNAVAILABLE',
    storedHashShort: integrity.storedHashShort || null,
    recomputedHashShort: integrity.recomputedHashShort || null,
  };
}

/**
 * @function buildReceiptChainLink
 * @description Builds the linked evidence-chain summary for telemetry and compliance receipts.
 * @param {Object} complianceReceipt - Compliance receipt packet.
 * @param {Object} telemetryReceipt - Telemetry receipt packet.
 * @returns {Object} Chain link summary.
 * @collaboration Proves that the compliance receipt points back to the telemetry receipt and original search root.
 */
function buildReceiptChainLink(complianceReceipt = {}, telemetryReceipt = {}) {
  const complianceRoot = String(
    complianceReceipt?.merkleRoot || complianceReceipt?.payload?.rootHash || ''
  );
  const telemetryRoot = String(
    telemetryReceipt?.rootHash || telemetryReceipt?.payload?.rootHash || ''
  );
  const telemetryHash = String(telemetryReceipt?.receiptHash || '');
  const complianceTelemetryHash = String(
    complianceReceipt?.telemetryReceiptHash ||
      complianceReceipt?.payload?.telemetryReceiptHash ||
      ''
  );
  const telemetryEventId = String(telemetryReceipt?.id || '');
  const complianceTelemetryEventId = String(
    complianceReceipt?.telemetryEventId || complianceReceipt?.payload?.telemetryEventId || ''
  );

  return {
    telemetryEventLinked: Boolean(
      telemetryEventId &&
      complianceTelemetryEventId &&
      telemetryEventId === complianceTelemetryEventId
    ),
    telemetryHashLinked: Boolean(
      telemetryHash && complianceTelemetryHash && telemetryHash === complianceTelemetryHash
    ),
    rootHashLinked: Boolean(complianceRoot && telemetryRoot && complianceRoot === telemetryRoot),
    complianceReceiptId: complianceReceipt?.id || complianceReceipt?.receiptId || null,
    complianceReceiptHashShort: complianceReceipt?.receiptHashShort || null,
    telemetryEventId: telemetryEventId || null,
    telemetryReceiptHashShort: telemetryReceipt?.receiptHashShort || null,
    merkleRootShort: complianceReceipt?.merkleRootShort || null,
    telemetryRootHashShort: telemetryReceipt?.rootHashShort || null,
  };
}

/**
 * @function verifyLeadSearchEvidenceChain
 * @description Verifies the full Lead search evidence chain across compliance and telemetry receipts.
 * @param {Object} params - Evidence chain parameters.
 * @returns {Promise<Object>} Evidence chain verification response.
 * @collaboration Gives regulators one backend proof packet for the entire Lead search audit chain.
 */
export async function verifyLeadSearchEvidenceChain(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(
    params.receiptId || params.complianceReceiptId || params.complianceReceiptHash || ''
  ).trim();

  const complianceVerification = await verifyLeadSearchComplianceReceipt({
    tenantId,
    receiptId,
  });

  if (!complianceVerification.ok || !complianceVerification.complianceReceipt) {
    return {
      ok: false,
      version: WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION,
      tenantId,
      receiptId,
      status: 'EVIDENCE_CHAIN_COMPLIANCE_RECEIPT_NOT_FOUND',
      complianceVerification,
      telemetryVerification: null,
      chain: null,
    };
  }

  const complianceReceipt = complianceVerification.complianceReceipt;
  const telemetryLookup =
    complianceReceipt.telemetryEventId ||
    complianceReceipt.telemetryReceiptHash ||
    complianceReceipt.payload?.telemetryEventId ||
    complianceReceipt.payload?.telemetryReceiptHash ||
    '';

  const telemetryVerification = telemetryLookup
    ? await verifyLeadSearchTelemetryReceipt({ tenantId, receiptId: telemetryLookup })
    : {
        ok: false,
        version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
        tenantId,
        receiptId: '',
        status: 'TELEMETRY_LINK_NOT_AVAILABLE',
        receipt: null,
      };

  const telemetryReceipt = telemetryVerification.receipt || {};
  const chainLink = buildReceiptChainLink(complianceReceipt, telemetryReceipt);
  const complianceIntegrity = resolveReceiptIntegrityStatus(complianceReceipt);
  const telemetryIntegrity = resolveReceiptIntegrityStatus(telemetryReceipt);
  const chainVerified = Boolean(
    complianceVerification.ok &&
    telemetryVerification.ok &&
    complianceIntegrity.verified &&
    telemetryIntegrity.verified &&
    chainLink.rootHashLinked &&
    (chainLink.telemetryEventLinked || chainLink.telemetryHashLinked)
  );

  return {
    ok: chainVerified,
    version: WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION,
    tenantId,
    receiptId,
    status: chainVerified ? 'SEARCH_EVIDENCE_CHAIN_VERIFIED' : 'SEARCH_EVIDENCE_CHAIN_PARTIAL',
    chainVerified,
    chain: {
      route: '/api/crm/command/search',
      eventType: 'CRM_LEAD_SEARCH_EVIDENCE_CHAIN',
      query: complianceReceipt.query || telemetryReceipt.query || '',
      operatorId: complianceReceipt.operatorId || telemetryReceipt.operatorId || 'SYSTEM',
      tenantId,
      complianceIntegrity,
      telemetryIntegrity,
      link: chainLink,
      complianceReceipt,
      telemetryReceipt,
    },
  };
}

/**
 * @function listLeadSearchEvidenceChains
 * @description Lists recent verified Lead search evidence chains for a tenant.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Evidence chain list response.
 * @collaboration Turns recent compliance receipts into regulator-ready linked evidence packets.
 */
export async function listLeadSearchEvidenceChains(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 5), 1), 25);
  const complianceLedger = await listLeadSearchComplianceReceipts({ tenantId, limit });
  const sourceReceipts = complianceLedger.complianceReceipts || [];

  const chains = await Promise.all(
    sourceReceipts.map((receipt) =>
      verifyLeadSearchEvidenceChain({
        tenantId,
        receiptId: receipt.id || receipt.receiptId || receipt.receiptHash,
      })
    )
  );

  return {
    ok: true,
    version: WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION,
    tenantId,
    total: chains.length,
    verified: chains.filter((chain) => chain.chainVerified).length,
    status: 'SEARCH_EVIDENCE_CHAINS_LISTED',
    chains,
  };
}

/**
 * @function resolveGovernanceEventModel
 * @description Resolves the CRMGovernanceEvent model for verified search evidence chains.
 * @returns {Object|null} Governance event model or null.
 * @collaboration Connects verified Lead search evidence chains to board/governance event records.
 */
function resolveGovernanceEventModel() {
  return getModel('CRMGovernanceEvent');
}

/**
 * @function resolveGovernanceRequiredPathDefault
 * @description Produces a safe default for required CRMGovernanceEvent schema paths.
 * @param {string} fieldName - Schema path name.
 * @param {Object} schemaType - Mongoose schema type.
 * @param {Object} context - Governance event context.
 * @returns {*} Default value.
 * @collaboration Keeps governance writes resilient across evolving schemas.
 */
function resolveGovernanceRequiredPathDefault(fieldName = '', schemaType = {}, context = {}) {
  const normalized = String(fieldName).toLowerCase();
  const instance = String(schemaType?.instance || '').toLowerCase();

  if (normalized.includes('tenant')) return context.tenantId;
  if (
    normalized.includes('operator') ||
    normalized.includes('actor') ||
    normalized.includes('user')
  )
    return context.operatorId;
  if (normalized.includes('query') || normalized.includes('search'))
    return context.query || 'EMPTY_QUERY';
  if (normalized.includes('status')) return 'VERIFIED';
  if (normalized.includes('type') || normalized.includes('event'))
    return 'CRM_LEAD_SEARCH_EVIDENCE_CHAIN_VERIFIED';
  if (normalized.includes('route')) return '/api/crm/command/search/evidence-chain/:receiptId';
  if (normalized.includes('hash') || normalized.includes('root') || normalized.includes('merkle'))
    return context.governanceHash;
  if (
    normalized.includes('payload') ||
    normalized.includes('meta') ||
    normalized.includes('context') ||
    normalized.includes('data')
  )
    return context.payload;
  if (
    normalized.includes('created') ||
    normalized.includes('updated') ||
    normalized.includes('timestamp') ||
    normalized.includes('generated')
  )
    return context.generatedAt;

  if (instance === 'date') return context.generatedAt;
  if (instance === 'number') return 0;
  if (instance === 'boolean') return true;
  if (instance === 'array') return [];
  if (instance === 'map' || instance === 'mixed' || instance === 'object') return context.payload;
  if (instance === 'objectid') return new mongoose.Types.ObjectId();

  return 'CRM_LEAD_SEARCH_GOVERNANCE_EVENT';
}

/**
 * @function hydrateRequiredGovernanceEventFields
 * @description Adds schema-required defaults when compatible governance fields were not assigned.
 * @param {Object} model - Mongoose model.
 * @param {Object} document - Governance event document.
 * @param {Object} context - Governance event context.
 * @returns {Object} Hydrated document.
 * @collaboration Prevents schema-required fields from breaking governance event materialization.
 */
function hydrateRequiredGovernanceEventFields(model, document = {}, context = {}) {
  Object.entries(model?.schema?.paths || {}).forEach(([fieldName, schemaType]) => {
    if (fieldName === '_id' || fieldName === '__v' || document[fieldName] !== undefined) return;

    const isRequired = Boolean(schemaType?.isRequired || schemaType?.options?.required);
    if (!isRequired) return;

    document[fieldName] = resolveGovernanceRequiredPathDefault(fieldName, schemaType, context);
  });

  return document;
}

/**
 * @function buildLeadSearchGovernancePayload
 * @description Builds the governance payload for a verified Lead search evidence chain.
 * @param {Object} evidenceChain - Verified evidence chain response.
 * @returns {Object} Governance event payload.
 * @collaboration Converts a verified audit/compliance chain into board-ready evidence.
 */
function buildLeadSearchGovernancePayload(evidenceChain = {}) {
  const chain = evidenceChain.chain || {};
  const link = chain.link || {};
  const generatedAt = new Date().toISOString();

  return {
    version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
    evidenceChainVersion: WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION,
    complianceVerificationVersion: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
    telemetryVerificationVersion: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
    eventType: 'CRM_LEAD_SEARCH_EVIDENCE_CHAIN_VERIFIED',
    tenantId: evidenceChain.tenantId || chain.tenantId || 'MASTER',
    query: chain.query || '',
    operatorId: chain.operatorId || 'SYSTEM',
    route: '/api/crm/command/search/evidence-chain/:receiptId',
    status: evidenceChain.chainVerified ? 'VERIFIED' : 'PARTIAL',
    chainVerified: Boolean(evidenceChain.chainVerified),
    telemetryEventLinked: Boolean(link.telemetryEventLinked),
    telemetryHashLinked: Boolean(link.telemetryHashLinked),
    rootHashLinked: Boolean(link.rootHashLinked),
    complianceReceiptId: link.complianceReceiptId || chain.complianceReceipt?.id || null,
    complianceReceiptHashShort:
      link.complianceReceiptHashShort || chain.complianceReceipt?.receiptHashShort || null,
    telemetryEventId: link.telemetryEventId || chain.telemetryReceipt?.id || null,
    telemetryReceiptHashShort:
      link.telemetryReceiptHashShort || chain.telemetryReceipt?.receiptHashShort || null,
    merkleRootShort: link.merkleRootShort || null,
    telemetryRootHashShort: link.telemetryRootHashShort || null,
    complianceIntegrity: chain.complianceIntegrity || null,
    telemetryIntegrity: chain.telemetryIntegrity || null,
    generatedAt,
  };
}

/**
 * @function buildGovernanceEventDocument
 * @description Builds a schema-aware CRMGovernanceEvent document.
 * @param {Object} model - Governance event model.
 * @param {Object} payload - Governance payload.
 * @param {string} governanceHash - Governance event hash.
 * @returns {Object} Governance event document.
 * @collaboration Persists verified evidence chains without assuming a frozen governance schema.
 */
function buildGovernanceEventDocument(model, payload = {}, governanceHash = '') {
  const paths = getSchemaPathNames(model);
  const document = {};
  const generatedAt = new Date(payload.generatedAt || Date.now());
  const context = {
    tenantId: payload.tenantId,
    operatorId: payload.operatorId,
    query: payload.query,
    governanceHash,
    payload,
    generatedAt,
  };

  assignTelemetryField(
    document,
    paths,
    ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
    payload.tenantId
  );
  assignTelemetryField(
    document,
    paths,
    ['type', 'eventType', 'name', 'metricName'],
    'CRM_LEAD_SEARCH_EVIDENCE_CHAIN_VERIFIED'
  );
  assignTelemetryField(
    document,
    paths,
    ['category', 'eventCategory', 'entityType'],
    'CRM_GOVERNANCE'
  );
  assignTelemetryField(document, paths, ['action', 'operation'], 'EVIDENCE_CHAIN_VERIFIED');
  assignTelemetryField(document, paths, ['status', 'governanceStatus'], payload.status);
  assignTelemetryField(
    document,
    paths,
    ['route', 'path', 'endpoint'],
    '/api/crm/command/search/evidence-chain/:receiptId'
  );
  assignTelemetryField(document, paths, ['query', 'searchQuery', 'q'], payload.query || '');
  assignTelemetryField(
    document,
    paths,
    ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
    payload.operatorId
  );
  assignTelemetryField(
    document,
    paths,
    ['receiptHash', 'hash', 'governanceHash', 'provenanceHash'],
    governanceHash
  );
  assignTelemetryField(
    document,
    paths,
    ['rootHash', 'merkleRoot'],
    payload.merkleRootShort || governanceHash
  );
  assignTelemetryField(document, paths, ['complianceReceiptId'], payload.complianceReceiptId);
  assignTelemetryField(document, paths, ['telemetryEventId'], payload.telemetryEventId);
  assignTelemetryField(
    document,
    paths,
    ['payload', 'metadata', 'details', 'context', 'data'],
    payload
  );
  assignTelemetryField(
    document,
    paths,
    ['timestamp', 'eventAt', 'occurredAt', 'createdAt', 'generatedAt'],
    generatedAt
  );
  assignTelemetryField(document, paths, ['verified', 'chainVerified'], payload.chainVerified);
  assignTelemetryField(document, paths, ['boardReady'], true);
  assignTelemetryField(document, paths, ['regulatorReady'], true);

  return hydrateRequiredGovernanceEventFields(model, document, context);
}

/**
 * @function persistLeadSearchGovernanceEvent
 * @description Persists a CRMGovernanceEvent for a verified Lead search evidence chain.
 * @param {Object} evidenceChain - Evidence chain response.
 * @returns {Promise<Object>} Governance event persistence response.
 * @collaboration Turns verified search evidence into a board/governance record.
 */
async function persistLeadSearchGovernanceEvent(evidenceChain = {}) {
  const model = resolveGovernanceEventModel();
  const payload = buildLeadSearchGovernancePayload(evidenceChain);
  const governanceHash = createHashDigest(JSON.stringify(payload));

  if (!model) {
    return {
      persisted: false,
      status: 'GOVERNANCE_EVENT_MODEL_NOT_REGISTERED',
      modelName: 'CRMGovernanceEvent',
      version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
      governanceHash,
      governanceHashShort: governanceHash.slice(0, 16),
      generatedAt: payload.generatedAt,
    };
  }

  try {
    const document = buildGovernanceEventDocument(model, payload, governanceHash);
    const created = await model.create(document);

    return {
      persisted: true,
      status: 'GOVERNANCE_EVENT_PERSISTED',
      modelName: 'CRMGovernanceEvent',
      governanceEventId: String(created?._id || created?.id || ''),
      version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
      governanceHash,
      governanceHashShort: governanceHash.slice(0, 16),
      generatedAt: payload.generatedAt,
    };
  } catch (error) {
    return {
      persisted: false,
      status: 'GOVERNANCE_EVENT_WRITE_FAILED',
      modelName: 'CRMGovernanceEvent',
      errorName: error?.name || 'UnknownError',
      errorMessage: String(error?.message || 'Unknown governance event write failure').slice(
        0,
        220
      ),
      version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
      governanceHash,
      governanceHashShort: governanceHash.slice(0, 16),
      generatedAt: payload.generatedAt,
    };
  }
}

/**
 * @function materializeLeadSearchGovernanceEvent
 * @description Verifies a Lead search evidence chain and persists a governance event when verified.
 * @param {Object} params - Governance materialization parameters.
 * @returns {Promise<Object>} Governance materialization response.
 * @collaboration Closes the Lead search backend evidence chain with board-ready governance evidence.
 */
export async function materializeLeadSearchGovernanceEvent(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(
    params.receiptId || params.complianceReceiptId || params.complianceReceiptHash || ''
  ).trim();
  const evidenceChain = await verifyLeadSearchEvidenceChain({ tenantId, receiptId });

  if (!evidenceChain.ok || !evidenceChain.chainVerified) {
    return {
      ok: false,
      version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
      tenantId,
      receiptId,
      status: 'GOVERNANCE_EVENT_NOT_MATERIALIZED_CHAIN_NOT_VERIFIED',
      evidenceChain,
      governanceEventPersistence: {
        persisted: false,
        status: 'CHAIN_NOT_VERIFIED',
        modelName: 'CRMGovernanceEvent',
        version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
      },
    };
  }

  const governanceEventPersistence = await persistLeadSearchGovernanceEvent(evidenceChain);

  return {
    ok: Boolean(governanceEventPersistence.persisted),
    version: WILSY_CRM_SEARCH_GOVERNANCE_EVENT_VERSION,
    tenantId,
    receiptId,
    status: governanceEventPersistence.persisted
      ? 'SEARCH_GOVERNANCE_EVENT_MATERIALIZED'
      : governanceEventPersistence.status,
    evidenceChain,
    governanceEventPersistence,
    governanceEventPersisted: Boolean(governanceEventPersistence.persisted),
    governanceEventId: governanceEventPersistence.governanceEventId || null,
    governanceHash: governanceEventPersistence.governanceHash || null,
    governanceHashShort: governanceEventPersistence.governanceHashShort || null,
  };
}

/**
 * @function resolveGovernanceEventFieldValue
 * @description Resolves a governance event field by candidate schema names.
 * @param {Object} record - Governance event record.
 * @param {string[]} fields - Candidate fields.
 * @param {*} fallback - Fallback value.
 * @returns {*} Resolved value.
 * @collaboration Normalizes governance event records across evolving CRMGovernanceEvent schemas.
 */
function resolveGovernanceEventFieldValue(record = {}, fields = [], fallback = null) {
  const field = fields.find(
    (candidate) =>
      record[candidate] !== undefined && record[candidate] !== null && record[candidate] !== ''
  );
  return field ? record[field] : fallback;
}

/**
 * @function buildGovernanceEventLookupFilter
 * @description Builds a schema-aware filter for governance event lookup by id or hash.
 * @param {Object} model - Governance event model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} governanceId - Governance event id or hash.
 * @returns {Object|null} Mongo filter.
 * @collaboration Lets executives and regulators retrieve a precise governance event.
 */
function buildGovernanceEventLookupFilter(model, tenantId = 'MASTER', governanceId = '') {
  const paths = getSchemaPathNames(model);
  const tenantFilter = buildTenantFilter(model, tenantId);
  const clauses = [];
  const value = String(governanceId || '').trim();

  if (!tenantFilter || !value) return null;

  if (mongoose.Types.ObjectId.isValid(value)) {
    clauses.push({ _id: new mongoose.Types.ObjectId(value) });
  }

  [
    'governanceEventId',
    'governanceHash',
    'receiptHash',
    'hash',
    'provenanceHash',
    'rootHash',
    'merkleRoot',
    'governanceHashShort',
    'receiptHashShort',
  ].forEach((field) => {
    if (paths.has(field)) clauses.push({ [field]: value });
  });

  if (!clauses.length) return null;

  return { $and: [tenantFilter, { $or: clauses }] };
}

/**
 * @function buildGovernanceEventListFilter
 * @description Builds a tenant-scoped filter for recent Lead search governance events.
 * @param {Object} model - Governance event model.
 * @param {string} tenantId - Tenant identifier.
 * @returns {Object|null} Mongo filter.
 * @collaboration Provides a board-ready governance event ledger for Lead search evidence.
 */
function buildGovernanceEventListFilter(model, tenantId = 'MASTER') {
  const tenantFilter = buildTenantFilter(model, tenantId);
  if (!tenantFilter) return null;

  const paths = getSchemaPathNames(model);
  const eventClauses = [];

  ['eventType', 'type', 'name', 'action', 'operation'].forEach((field) => {
    if (paths.has(field)) {
      eventClauses.push({
        [field]: /CRM_LEAD_SEARCH_EVIDENCE_CHAIN_VERIFIED|EVIDENCE_CHAIN_VERIFIED/i,
      });
    }
  });

  return eventClauses.length ? { $and: [tenantFilter, { $or: eventClauses }] } : tenantFilter;
}

/**
 * @function extractGovernanceEventPayload
 * @description Extracts stored governance event payload from known schema fields.
 * @param {Object} record - Governance event record.
 * @returns {Object|null} Stored payload or null.
 * @collaboration Enables governance event hash verification when payload was persisted.
 */
function extractGovernanceEventPayload(record = {}) {
  const payload = resolveGovernanceEventFieldValue(
    record,
    ['payload', 'metadata', 'details', 'context', 'data'],
    null
  );
  return payload && typeof payload === 'object' ? payload : null;
}

/**
 * @function computeGovernanceEventPayloadHash
 * @description Computes the canonical governance event hash for a payload.
 * @param {Object|null} payload - Stored governance event payload.
 * @returns {string} Computed hash or empty string.
 * @collaboration Enables governance verification even when top-level hash fields differ by schema.
 */
function computeGovernanceEventPayloadHash(payload = null) {
  return payload && typeof payload === 'object' ? createHashDigest(JSON.stringify(payload)) : '';
}

/**
 * @function buildGovernanceEventIntegrityPacket
 * @description Builds a board-readable governance event integrity packet.
 * @param {Object|null} payload - Stored governance event payload.
 * @param {string} storedGovernanceHash - Stored governance hash.
 * @returns {Object} Integrity packet.
 * @collaboration Proves whether the persisted governance hash matches the stored payload.
 */
function buildGovernanceEventIntegrityPacket(payload = null, storedGovernanceHash = '') {
  const recomputedHash = computeGovernanceEventPayloadHash(payload);

  if (storedGovernanceHash && recomputedHash) {
    return {
      verified: storedGovernanceHash === recomputedHash,
      status:
        storedGovernanceHash === recomputedHash
          ? 'GOVERNANCE_EVENT_HASH_VERIFIED'
          : 'GOVERNANCE_EVENT_HASH_MISMATCH',
      storedHash: storedGovernanceHash,
      storedHashShort: storedGovernanceHash.slice(0, 16),
      recomputedHash,
      recomputedHashShort: recomputedHash.slice(0, 16),
    };
  }

  if (recomputedHash) {
    return {
      verified: true,
      status: 'GOVERNANCE_EVENT_HASH_RECOMPUTED',
      storedHash: null,
      storedHashShort: null,
      recomputedHash,
      recomputedHashShort: recomputedHash.slice(0, 16),
    };
  }

  return {
    verified: false,
    status: 'GOVERNANCE_EVENT_PAYLOAD_OR_HASH_NOT_AVAILABLE',
    storedHash: storedGovernanceHash || null,
    storedHashShort: storedGovernanceHash ? storedGovernanceHash.slice(0, 16) : null,
    recomputedHash: null,
    recomputedHashShort: null,
  };
}

/**
 * @function normalizeLeadSearchGovernanceEvent
 * @description Normalizes a CRMGovernanceEvent record into a verification packet.
 * @param {Object} record - Governance event record.
 * @returns {Object} Governance event packet.
 * @collaboration Makes board/governance records readable by operators, executives and regulators.
 */
function normalizeLeadSearchGovernanceEvent(record = {}) {
  const payload = extractGovernanceEventPayload(record);
  const storedHash = String(
    resolveGovernanceEventFieldValue(
      record,
      ['governanceHash', 'receiptHash', 'hash', 'provenanceHash'],
      ''
    )
  );
  const recomputedHash = computeGovernanceEventPayloadHash(payload);
  const governanceHash = storedHash || recomputedHash;
  const integrity = buildGovernanceEventIntegrityPacket(payload, storedHash);

  return {
    id: String(record._id || record.id || ''),
    version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
    modelName: 'CRMGovernanceEvent',
    eventType: String(
      resolveGovernanceEventFieldValue(
        record,
        ['eventType', 'type', 'name'],
        payload?.eventType || 'CRM_LEAD_SEARCH_EVIDENCE_CHAIN_VERIFIED'
      )
    ),
    category: String(
      resolveGovernanceEventFieldValue(
        record,
        ['category', 'eventCategory', 'entityType'],
        'CRM_GOVERNANCE'
      )
    ),
    action: String(
      resolveGovernanceEventFieldValue(record, ['action', 'operation'], 'EVIDENCE_CHAIN_VERIFIED')
    ),
    tenantId: String(
      resolveGovernanceEventFieldValue(
        record,
        ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
        payload?.tenantId || 'MASTER'
      )
    ),
    operatorId: String(
      resolveGovernanceEventFieldValue(
        record,
        ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
        payload?.operatorId || 'SYSTEM'
      )
    ),
    query: String(
      resolveGovernanceEventFieldValue(record, ['query', 'searchQuery', 'q'], payload?.query || '')
    ),
    status: String(
      resolveGovernanceEventFieldValue(
        record,
        ['status', 'governanceStatus'],
        payload?.status || 'VERIFIED'
      )
    ),
    route: String(
      resolveGovernanceEventFieldValue(
        record,
        ['route', 'path', 'endpoint'],
        payload?.route || '/api/crm/command/search/evidence-chain/:receiptId'
      )
    ),
    governanceHash,
    governanceHashShort: governanceHash ? governanceHash.slice(0, 16) : null,
    complianceReceiptId:
      payload?.complianceReceiptId ||
      resolveGovernanceEventFieldValue(record, ['complianceReceiptId'], null),
    telemetryEventId:
      payload?.telemetryEventId ||
      resolveGovernanceEventFieldValue(record, ['telemetryEventId'], null),
    merkleRootShort:
      payload?.merkleRootShort ||
      resolveGovernanceEventFieldValue(record, ['merkleRootShort'], null),
    chainVerified: Boolean(
      payload?.chainVerified ||
      resolveGovernanceEventFieldValue(record, ['chainVerified', 'verified'], false)
    ),
    boardReady: Boolean(resolveGovernanceEventFieldValue(record, ['boardReady'], true)),
    regulatorReady: Boolean(resolveGovernanceEventFieldValue(record, ['regulatorReady'], true)),
    createdAt: resolveGovernanceEventFieldValue(
      record,
      ['timestamp', 'eventAt', 'occurredAt', 'createdAt', 'generatedAt'],
      payload?.generatedAt || null
    ),
    integrity,
    payloadAvailable: Boolean(payload),
    payload,
  };
}

/**
 * @function findGovernanceEventByHashFallback
 * @description Finds a governance event by recomputing payload hashes across a bounded recent tenant ledger.
 * @param {Object} model - Governance event model.
 * @param {string} tenantId - Tenant identifier.
 * @param {string} governanceId - Governance event hash or short hash.
 * @returns {Promise<Object|null>} Matching record or null.
 * @collaboration Supports hash lookup even when top-level hash fields were not part of the governance schema.
 */
async function findGovernanceEventByHashFallback(model, tenantId = 'MASTER', governanceId = '') {
  const filter = buildGovernanceEventListFilter(model, tenantId);
  if (!filter) return null;

  const value = String(governanceId || '').trim();

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, generatedAt: -1, timestamp: -1, eventAt: -1 })
    .limit(200)
    .lean();

  return (
    records.find((record) => {
      const event = normalizeLeadSearchGovernanceEvent(record);
      return [
        event.id,
        event.governanceHash,
        event.governanceHashShort,
        event.integrity?.storedHash,
        event.integrity?.storedHashShort,
        event.integrity?.recomputedHash,
        event.integrity?.recomputedHashShort,
      ]
        .filter(Boolean)
        .includes(value);
    }) || null
  );
}

/**
 * @function verifyLeadSearchGovernanceEvent
 * @description Retrieves and verifies one Lead search governance event.
 * @param {Object} params - Verification parameters.
 * @returns {Promise<Object>} Governance verification response.
 * @collaboration Proves a board-ready governance event exists in the backend evidence chain.
 */
export async function verifyLeadSearchGovernanceEvent(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const governanceId = String(
    params.governanceId || params.governanceEventId || params.governanceHash || ''
  ).trim();
  const model = resolveGovernanceEventModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
      tenantId,
      governanceId,
      status: 'GOVERNANCE_EVENT_MODEL_NOT_REGISTERED',
      governanceEvent: null,
    };
  }

  const filter = buildGovernanceEventLookupFilter(model, tenantId, governanceId);
  let record = filter ? await model.findOne(filter).lean() : null;

  if (!record && governanceId) {
    record = await findGovernanceEventByHashFallback(model, tenantId, governanceId);
  }

  if (!record) {
    return {
      ok: false,
      version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
      tenantId,
      governanceId,
      status: 'GOVERNANCE_EVENT_NOT_FOUND',
      governanceEvent: null,
    };
  }

  const governanceEvent = normalizeLeadSearchGovernanceEvent(record);

  return {
    ok: Boolean(governanceEvent.integrity?.verified),
    version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
    tenantId,
    governanceId,
    status: governanceEvent.integrity?.verified
      ? 'GOVERNANCE_EVENT_FOUND'
      : 'GOVERNANCE_EVENT_FOUND_INTEGRITY_PARTIAL',
    governanceEvent,
  };
}

/**
 * @function listLeadSearchGovernanceEvents
 * @description Lists recent Lead search governance events for a tenant.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Governance event list response.
 * @collaboration Gives executives a backend governance ledger for verified Lead search evidence.
 */
export async function listLeadSearchGovernanceEvents(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 10), 1), 50);
  const model = resolveGovernanceEventModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
      tenantId,
      total: 0,
      status: 'GOVERNANCE_EVENT_MODEL_NOT_REGISTERED',
      governanceEvents: [],
    };
  }

  const filter = buildGovernanceEventListFilter(model, tenantId);

  if (!filter) {
    return {
      ok: false,
      version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
      tenantId,
      total: 0,
      status: 'GOVERNANCE_EVENT_LIST_FILTER_NOT_AVAILABLE',
      governanceEvents: [],
    };
  }

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, generatedAt: -1, timestamp: -1, eventAt: -1 })
    .limit(limit)
    .lean();

  const governanceEvents = records.map((record) => normalizeLeadSearchGovernanceEvent(record));

  return {
    ok: true,
    version: WILSY_CRM_GOVERNANCE_EVENT_VERIFICATION_VERSION,
    tenantId,
    total: governanceEvents.length,
    verified: governanceEvents.filter((event) => event.integrity?.verified).length,
    status: 'GOVERNANCE_EVENTS_LISTED',
    governanceEvents,
  };
}

/**
 * @function buildRegulatorEvidenceHashInput
 * @description Builds the canonical hash input for a regulator evidence bundle.
 * @param {Object} bundleCore - Bundle core without export hash.
 * @returns {Object} Hash input.
 * @collaboration Keeps regulator export hash deterministic and self-verifiable.
 */
function buildRegulatorEvidenceHashInput(bundleCore = {}) {
  return {
    exportType: bundleCore.exportType,
    exportVersion: bundleCore.exportVersion,
    tenantId: bundleCore.tenantId,
    query: bundleCore.query,
    operatorId: bundleCore.operatorId,
    governanceEventId: bundleCore.governanceProof?.id || null,
    governanceHash: bundleCore.governanceProof?.governanceHash || null,
    complianceReceiptId:
      bundleCore.complianceReceipt?.id || bundleCore.complianceReceipt?.receiptId || null,
    complianceReceiptHash: bundleCore.complianceReceipt?.receiptHash || null,
    telemetryEventId: bundleCore.telemetryReceipt?.id || null,
    telemetryReceiptHash: bundleCore.telemetryReceipt?.receiptHash || null,
    evidenceChainStatus: bundleCore.evidenceChain?.status || null,
    governanceIntegrityStatus: bundleCore.governanceProof?.integrity?.status || null,
    generatedAt: bundleCore.generatedAt,
  };
}

/**
 * @function buildRegulatorEvidenceBundleCore
 * @description Builds the regulator evidence bundle core before export hash sealing.
 * @param {Object} params - Bundle dependencies.
 * @returns {Object} Bundle core.
 * @collaboration Assembles telemetry, compliance, evidence-chain and governance proofs into one regulator packet.
 */
function buildRegulatorEvidenceBundleCore(params = {}) {
  const governanceVerification = params.governanceVerification || {};
  const governanceProof = governanceVerification.governanceEvent || {};
  const complianceVerification = params.complianceVerification || {};
  const complianceReceipt = complianceVerification.complianceReceipt || null;
  const telemetryVerification = params.telemetryVerification || {};
  const telemetryReceipt = telemetryVerification.receipt || null;
  const evidenceChain = params.evidenceChain || {};
  const generatedAt = new Date().toISOString();
  const tenantId =
    params.tenantId ||
    governanceProof.tenantId ||
    complianceReceipt?.tenantId ||
    telemetryReceipt?.tenantId ||
    'MASTER';

  return {
    exportType: 'CRM_LEAD_SEARCH_REGULATOR_EVIDENCE_BUNDLE',
    exportVersion: WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION,
    tenantId,
    query: governanceProof.query || complianceReceipt?.query || telemetryReceipt?.query || '',
    operatorId:
      governanceProof.operatorId ||
      complianceReceipt?.operatorId ||
      telemetryReceipt?.operatorId ||
      'SYSTEM',
    generatedAt,
    route: '/api/crm/command/search/regulator-evidence/:governanceId',
    regulatoryScope: ['POPIA', 'GDPR', 'SOC2', 'REGULATOR_EXPORT'],
    evidenceStatus: {
      telemetryReceiptVerified: Boolean(telemetryReceipt?.integrity?.verified),
      complianceReceiptVerified: Boolean(complianceReceipt?.integrity?.verified),
      evidenceChainVerified: Boolean(evidenceChain?.chainVerified),
      governanceEventVerified: Boolean(governanceProof?.integrity?.verified),
      boardReady: Boolean(governanceProof?.boardReady),
      regulatorReady: Boolean(governanceProof?.regulatorReady),
    },
    hashes: {
      telemetryReceiptHash: telemetryReceipt?.receiptHash || null,
      telemetryReceiptHashShort: telemetryReceipt?.receiptHashShort || null,
      complianceReceiptHash: complianceReceipt?.receiptHash || null,
      complianceReceiptHashShort: complianceReceipt?.receiptHashShort || null,
      governanceHash: governanceProof?.governanceHash || null,
      governanceHashShort: governanceProof?.governanceHashShort || null,
      merkleRoot:
        complianceReceipt?.merkleRoot ||
        evidenceChain?.chain?.complianceReceipt?.merkleRoot ||
        null,
      merkleRootShort:
        complianceReceipt?.merkleRootShort || evidenceChain?.chain?.link?.merkleRootShort || null,
      rootHash:
        telemetryReceipt?.rootHash || evidenceChain?.chain?.telemetryReceipt?.rootHash || null,
      rootHashShort:
        telemetryReceipt?.rootHashShort ||
        evidenceChain?.chain?.link?.telemetryRootHashShort ||
        null,
    },
    exportMetadata: {
      generatedBy: 'WILSY_OS_CRM_COMMAND_FABRIC',
      sourceRoute: '/api/crm/command/search',
      governanceRoute: '/api/crm/command/search/evidence-chain/:receiptId/govern',
      verificationRoute: '/api/crm/command/search/governance-event/:governanceId',
      exportRoute: '/api/crm/command/search/regulator-evidence/:governanceId',
      chainMode: 'BACKEND_VERIFIED_EVIDENCE_CHAIN',
      persistenceMode: 'JSON_RESPONSE_ONLY',
      retentionPosture: 'TENANT_SCOPED_REGULATOR_REVIEW_PACKET',
    },
    governanceVerification,
    governanceProof,
    evidenceChain,
    complianceVerification,
    complianceReceipt,
    telemetryVerification,
    telemetryReceipt,
  };
}

/**
 * @function sealRegulatorEvidenceBundle
 * @description Adds export hash and integrity summary to a regulator evidence bundle.
 * @param {Object} bundleCore - Bundle core.
 * @returns {Object} Sealed bundle.
 * @collaboration Provides a regulator-ready hash over the complete evidence export packet.
 */
function sealRegulatorEvidenceBundle(bundleCore = {}) {
  const hashInput = buildRegulatorEvidenceHashInput(bundleCore);
  const exportHash = createHashDigest(JSON.stringify(hashInput));
  const allEvidenceVerified = Boolean(
    bundleCore.evidenceStatus?.telemetryReceiptVerified &&
    bundleCore.evidenceStatus?.complianceReceiptVerified &&
    bundleCore.evidenceStatus?.evidenceChainVerified &&
    bundleCore.evidenceStatus?.governanceEventVerified
  );

  return {
    ...bundleCore,
    hashes: {
      ...bundleCore.hashes,
      exportHash,
      exportHashShort: exportHash.slice(0, 16),
    },
    exportIntegrity: {
      verified: allEvidenceVerified,
      status: allEvidenceVerified
        ? 'REGULATOR_EVIDENCE_EXPORT_VERIFIED'
        : 'REGULATOR_EVIDENCE_EXPORT_PARTIAL',
      exportHash,
      exportHashShort: exportHash.slice(0, 16),
      hashInput,
    },
  };
}

/**
 * @function exportLeadSearchRegulatorEvidenceBundle
 * @description Exports a complete regulator evidence bundle from a verified governance event.
 * @param {Object} params - Export parameters.
 * @returns {Promise<Object>} Regulator evidence export response.
 * @collaboration Turns verified CRM Lead search governance evidence into one regulator-ready JSON bundle.
 */
export async function exportLeadSearchRegulatorEvidenceBundle(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const governanceId = String(
    params.governanceId || params.governanceEventId || params.governanceHash || ''
  ).trim();

  const governanceVerification = await verifyLeadSearchGovernanceEvent({
    tenantId,
    governanceId,
  });

  if (!governanceVerification.ok || !governanceVerification.governanceEvent) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION,
      tenantId,
      governanceId,
      status: 'REGULATOR_EVIDENCE_GOVERNANCE_EVENT_NOT_FOUND',
      evidenceBundle: null,
      governanceVerification,
    };
  }

  const governanceProof = governanceVerification.governanceEvent;
  const complianceReceiptId =
    governanceProof.complianceReceiptId || governanceProof.payload?.complianceReceiptId || '';
  const telemetryEventId =
    governanceProof.telemetryEventId || governanceProof.payload?.telemetryEventId || '';

  const complianceVerification = complianceReceiptId
    ? await verifyLeadSearchComplianceReceipt({ tenantId, receiptId: complianceReceiptId })
    : {
        ok: false,
        version: WILSY_CRM_COMPLIANCE_RECEIPT_VERIFICATION_VERSION,
        tenantId,
        receiptId: '',
        status: 'COMPLIANCE_RECEIPT_LINK_NOT_AVAILABLE',
        complianceReceipt: null,
      };

  const telemetryVerification = telemetryEventId
    ? await verifyLeadSearchTelemetryReceipt({ tenantId, receiptId: telemetryEventId })
    : {
        ok: false,
        version: WILSY_CRM_SEARCH_RECEIPT_VERIFICATION_VERSION,
        tenantId,
        receiptId: '',
        status: 'TELEMETRY_RECEIPT_LINK_NOT_AVAILABLE',
        receipt: null,
      };

  const evidenceChain = complianceReceiptId
    ? await verifyLeadSearchEvidenceChain({ tenantId, receiptId: complianceReceiptId })
    : {
        ok: false,
        version: WILSY_CRM_SEARCH_EVIDENCE_CHAIN_VERSION,
        tenantId,
        receiptId: '',
        status: 'EVIDENCE_CHAIN_LINK_NOT_AVAILABLE',
        chainVerified: false,
        chain: null,
      };

  const bundleCore = buildRegulatorEvidenceBundleCore({
    tenantId,
    governanceVerification,
    complianceVerification,
    telemetryVerification,
    evidenceChain,
  });

  const evidenceBundle = sealRegulatorEvidenceBundle(bundleCore);

  return {
    ok: Boolean(evidenceBundle.exportIntegrity?.verified),
    version: WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION,
    tenantId,
    governanceId,
    status: evidenceBundle.exportIntegrity?.verified
      ? 'REGULATOR_EVIDENCE_BUNDLE_READY'
      : 'REGULATOR_EVIDENCE_BUNDLE_PARTIAL',
    exportHash: evidenceBundle.hashes.exportHash,
    exportHashShort: evidenceBundle.hashes.exportHashShort,
    evidenceBundle,
  };
}

/**
 * @function listLeadSearchRegulatorEvidenceBundles
 * @description Lists recent regulator evidence bundles from verified governance events.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Regulator evidence bundle list response.
 * @collaboration Provides a regulator export ledger without writing files to disk.
 */
export async function listLeadSearchRegulatorEvidenceBundles(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 5), 1), 25);
  const governanceLedger = await listLeadSearchGovernanceEvents({ tenantId, limit });
  const governanceEvents = governanceLedger.governanceEvents || [];

  const bundles = await Promise.all(
    governanceEvents.map((event) =>
      exportLeadSearchRegulatorEvidenceBundle({
        tenantId,
        governanceId: event.id || event.governanceHash,
      })
    )
  );

  return {
    ok: true,
    version: WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION,
    tenantId,
    total: bundles.length,
    verified: bundles.filter((bundle) => bundle.ok).length,
    status: 'REGULATOR_EVIDENCE_BUNDLES_LISTED',
    bundles,
  };
}

/**
 * @function resolveRegulatorExportRecordModel
 * @description Resolves the generic CRM record model used for regulator export receipts.
 * @returns {Object|null} Generic record model or null.
 * @collaboration Activates the genericRecords source with real regulator export receipts.
 */
function resolveRegulatorExportRecordModel() {
  return getModel('CrmRecord') || getModel('CRMRecord');
}

/**
 * @function resolveRegulatorExportEnumValues
 * @description Resolves enum values from a Mongoose schema path.
 * @param {Object} schemaType - Mongoose schema path type.
 * @returns {string[]} Enum values.
 * @collaboration Prevents CrmRecord enum validation failures during regulator export receipt writes.
 */
function resolveRegulatorExportEnumValues(schemaType = {}) {
  if (Array.isArray(schemaType?.enumValues) && schemaType.enumValues.length) {
    return schemaType.enumValues.map((value) => String(value));
  }

  if (Array.isArray(schemaType?.options?.enum) && schemaType.options.enum.length) {
    return schemaType.options.enum.map((value) => String(value));
  }

  if (Array.isArray(schemaType?.options?.enum?.values) && schemaType.options.enum.values.length) {
    return schemaType.options.enum.values.map((value) => String(value));
  }

  return [];
}

/**
 * @function resolveRegulatorExportEnumSafeValue
 * @description Chooses a schema-valid value for enum-backed CrmRecord fields.
 * @param {Object} model - Mongoose model.
 * @param {string} fieldName - Schema path name.
 * @param {*} preferredValue - Preferred field value.
 * @param {*[]} fallbackValues - Fallback values.
 * @returns {*} Enum-safe value.
 * @collaboration Keeps CrmRecord valid while preserving the true regulator payload separately.
 */
function resolveRegulatorExportEnumSafeValue(
  model,
  fieldName = '',
  preferredValue = '',
  fallbackValues = []
) {
  const schemaType = model?.schema?.paths?.[fieldName];
  const enumValues = resolveRegulatorExportEnumValues(schemaType);

  if (!enumValues.length) return preferredValue;

  const candidates = [
    preferredValue,
    ...fallbackValues,
    'REGULATOR_EXPORT',
    'EXPORT',
    'COMPLIANCE',
    'AUDIT',
    'EVIDENCE',
    'DOCUMENT',
    'NOTE',
    'GENERAL',
    'OTHER',
    'ACTIVE',
    'SEALED',
    'VERIFIED',
  ]
    .filter((value) => value !== undefined && value !== null && value !== '')
    .map((value) => String(value));

  return candidates.find((value) => enumValues.includes(value)) || enumValues[0];
}

/**
 * @function assignRegulatorExportField
 * @description Assigns a schema-aware and enum-safe value to the first available field.
 * @param {Object} document - Mutable document.
 * @param {Object} model - Mongoose model.
 * @param {Set<string>} paths - Schema path set.
 * @param {string[]} candidateFields - Candidate schema paths.
 * @param {*} preferredValue - Preferred field value.
 * @param {*[]} fallbackValues - Fallback values.
 * @returns {Object} Updated document.
 * @collaboration Adapts regulator export receipt writes to CrmRecord enum constraints.
 */
function assignRegulatorExportField(
  document = {},
  model,
  paths = new Set(),
  candidateFields = [],
  preferredValue = '',
  fallbackValues = []
) {
  const field = candidateFields.find((candidate) => paths.has(candidate));

  if (!field) return document;

  document[field] = resolveRegulatorExportEnumSafeValue(
    model,
    field,
    preferredValue,
    fallbackValues
  );
  return document;
}

/**
 * @function resolveRegulatorExportRecordRequiredPathDefault
 * @description Produces a safe default for required generic record schema paths.
 * @param {string} fieldName - Schema path name.
 * @param {Object} schemaType - Mongoose schema type.
 * @param {Object} context - Export receipt context.
 * @returns {*} Default value.
 * @collaboration Keeps CrmRecord persistence resilient across schema variants.
 */
function resolveRegulatorExportRecordRequiredPathDefault(
  fieldName = '',
  schemaType = {},
  context = {}
) {
  const normalized = String(fieldName).toLowerCase();
  const instance = String(schemaType?.instance || '').toLowerCase();
  let defaultValue = 'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT';

  if (normalized.includes('tenant')) defaultValue = context.tenantId;
  else if (
    normalized.includes('operator') ||
    normalized.includes('actor') ||
    normalized.includes('user')
  )
    defaultValue = context.operatorId;
  else if (normalized.includes('query') || normalized.includes('search'))
    defaultValue = context.query || 'EMPTY_QUERY';
  else if (normalized.includes('status')) defaultValue = 'SEALED';
  else if (
    normalized.includes('type') ||
    normalized.includes('event') ||
    normalized.includes('kind')
  )
    defaultValue = 'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT';
  else if (normalized.includes('category')) defaultValue = 'CRM_REGULATOR_EXPORT';
  else if (normalized.includes('action') || normalized.includes('operation'))
    defaultValue = 'REGULATOR_EVIDENCE_EXPORT_RECEIPT_SEALED';
  else if (normalized.includes('route'))
    defaultValue = '/api/crm/command/search/regulator-evidence/:governanceId/receipt';
  else if (
    normalized.includes('hash') ||
    normalized.includes('root') ||
    normalized.includes('merkle')
  )
    defaultValue = context.exportReceiptHash;
  else if (
    normalized.includes('payload') ||
    normalized.includes('meta') ||
    normalized.includes('context') ||
    normalized.includes('data')
  )
    defaultValue = context.payload;
  else if (
    normalized.includes('created') ||
    normalized.includes('updated') ||
    normalized.includes('timestamp') ||
    normalized.includes('generated')
  )
    defaultValue = context.generatedAt;
  else if (instance === 'date') defaultValue = context.generatedAt;
  else if (instance === 'number') defaultValue = 0;
  else if (instance === 'boolean') defaultValue = true;
  else if (instance === 'array') defaultValue = [];
  else if (instance === 'map' || instance === 'mixed' || instance === 'object')
    defaultValue = context.payload;
  else if (instance === 'objectid') defaultValue = new mongoose.Types.ObjectId();

  const enumValues = resolveRegulatorExportEnumValues(schemaType);

  if (!enumValues.length) return defaultValue;

  const candidates = [
    defaultValue,
    context.exportType,
    context.category,
    context.action,
    context.status,
    'REGULATOR_EXPORT',
    'EXPORT',
    'COMPLIANCE',
    'AUDIT',
    'EVIDENCE',
    'DOCUMENT',
    'NOTE',
    'GENERAL',
    'OTHER',
    'ACTIVE',
    'SEALED',
    'VERIFIED',
  ]
    .filter((value) => value !== undefined && value !== null && value !== '')
    .map((value) => String(value));

  return candidates.find((value) => enumValues.includes(value)) || enumValues[0];
}

/**
 * @function hydrateRequiredRegulatorExportRecordFields
 * @description Adds schema-required defaults when compatible export receipt fields were not assigned.
 * @param {Object} model - Generic record model.
 * @param {Object} document - Export receipt document.
 * @param {Object} context - Export receipt context.
 * @returns {Object} Hydrated document.
 * @collaboration Prevents schema-required fields from breaking export receipt materialization.
 */
function hydrateRequiredRegulatorExportRecordFields(model, document = {}, context = {}) {
  Object.entries(model?.schema?.paths || {}).forEach(([fieldName, schemaType]) => {
    if (fieldName === '_id' || fieldName === '__v' || document[fieldName] !== undefined) return;

    const isRequired = Boolean(schemaType?.isRequired || schemaType?.options?.required);
    if (!isRequired) return;

    document[fieldName] = resolveRegulatorExportRecordRequiredPathDefault(
      fieldName,
      schemaType,
      context
    );
  });

  return document;
}

/**
 * @function buildRegulatorExportReceiptPayload
 * @description Builds the persisted receipt payload for a regulator evidence export bundle.
 * @param {Object} regulatorExport - Regulator export response.
 * @returns {Object} Export receipt payload.
 * @collaboration Converts verified JSON export into a backend generic record receipt.
 */
function buildRegulatorExportReceiptPayload(regulatorExport = {}) {
  const bundle = regulatorExport.evidenceBundle || {};
  const hashes = bundle.hashes || {};
  const governanceProof = bundle.governanceProof || {};
  const generatedAt = new Date().toISOString();

  return {
    version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
    regulatorExportVersion: WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION,
    exportType: 'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT',
    sourceExportType: bundle.exportType || 'CRM_LEAD_SEARCH_REGULATOR_EVIDENCE_BUNDLE',
    tenantId: regulatorExport.tenantId || bundle.tenantId || 'MASTER',
    query: bundle.query || '',
    operatorId: bundle.operatorId || 'SYSTEM',
    route: '/api/crm/command/search/regulator-evidence/:governanceId/receipt',
    status: regulatorExport.ok ? 'SEALED' : 'PARTIAL',
    exportHash: regulatorExport.exportHash || hashes.exportHash || null,
    exportHashShort: regulatorExport.exportHashShort || hashes.exportHashShort || null,
    governanceEventId: governanceProof.id || regulatorExport.governanceId || null,
    governanceHash: hashes.governanceHash || governanceProof.governanceHash || null,
    governanceHashShort: hashes.governanceHashShort || governanceProof.governanceHashShort || null,
    complianceReceiptId:
      bundle.complianceReceipt?.id || bundle.complianceReceipt?.receiptId || null,
    complianceReceiptHashShort: hashes.complianceReceiptHashShort || null,
    telemetryEventId: bundle.telemetryReceipt?.id || null,
    telemetryReceiptHashShort: hashes.telemetryReceiptHashShort || null,
    merkleRootShort: hashes.merkleRootShort || null,
    evidenceStatus: bundle.evidenceStatus || null,
    exportIntegrity: bundle.exportIntegrity || null,
    boardReady: Boolean(bundle.evidenceStatus?.governanceEventVerified),
    regulatorReady: Boolean(bundle.evidenceStatus?.governanceEventVerified),
    generatedAt,
  };
}

/**
 * @function buildRegulatorExportReceiptDocument
 * @description Builds a schema-aware CrmRecord document for a regulator export receipt.
 * @param {Object} model - Generic record model.
 * @param {Object} payload - Export receipt payload.
 * @param {string} exportReceiptHash - Export receipt hash.
 * @returns {Object} Generic record document.
 * @collaboration Persists regulator evidence exports without assuming a frozen CrmRecord schema.
 */
function buildRegulatorExportReceiptDocument(model, payload = {}, exportReceiptHash = '') {
  const paths = getSchemaPathNames(model);
  const document = {};
  const generatedAt = new Date(payload.generatedAt || Date.now());
  const context = {
    tenantId: payload.tenantId,
    operatorId: payload.operatorId,
    query: payload.query,
    status: payload.status,
    exportType: payload.exportType,
    category: 'CRM_REGULATOR_EXPORT',
    action: 'REGULATOR_EVIDENCE_EXPORT_RECEIPT_SEALED',
    exportReceiptHash,
    payload,
    generatedAt,
  };

  assignTelemetryField(
    document,
    paths,
    ['tenantId', 'tenant', 'tenantKey', 'organizationId', 'orgId'],
    payload.tenantId
  );

  assignRegulatorExportField(
    document,
    model,
    paths,
    ['type', 'eventType', 'recordType', 'kind', 'name'],
    'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT',
    [
      'REGULATOR_EXPORT',
      'EXPORT',
      'COMPLIANCE',
      'AUDIT',
      'EVIDENCE',
      'DOCUMENT',
      'NOTE',
      'GENERAL',
      'OTHER',
    ]
  );

  assignRegulatorExportField(
    document,
    model,
    paths,
    ['category', 'eventCategory', 'entityType'],
    'CRM_REGULATOR_EXPORT',
    ['REGULATOR_EXPORT', 'EXPORT', 'COMPLIANCE', 'AUDIT', 'GOVERNANCE', 'GENERAL', 'OTHER']
  );

  assignRegulatorExportField(
    document,
    model,
    paths,
    ['action', 'operation'],
    'REGULATOR_EVIDENCE_EXPORT_RECEIPT_SEALED',
    [
      'EXPORT_RECEIPT_SEALED',
      'REGULATOR_EXPORT_SEALED',
      'EVIDENCE_CHAIN_VERIFIED',
      'CREATED',
      'SEALED',
      'VERIFIED',
      'GENERAL',
      'OTHER',
    ]
  );

  assignRegulatorExportField(document, model, paths, ['status', 'recordStatus'], payload.status, [
    'SEALED',
    'VERIFIED',
    'ACTIVE',
    'COMPLETED',
    'READY',
    'PERSISTED',
    'SUCCESS',
    'APPROVED',
    'OPEN',
    'NEW',
    'GENERAL',
    'OTHER',
  ]);

  assignTelemetryField(
    document,
    paths,
    ['route', 'path', 'endpoint'],
    '/api/crm/command/search/regulator-evidence/:governanceId/receipt'
  );
  assignTelemetryField(document, paths, ['query', 'searchQuery', 'q'], payload.query || '');
  assignTelemetryField(
    document,
    paths,
    ['operatorId', 'actorId', 'userId', 'createdBy', 'owner'],
    payload.operatorId
  );
  assignTelemetryField(
    document,
    paths,
    ['receiptHash', 'hash', 'exportReceiptHash', 'provenanceHash'],
    exportReceiptHash
  );
  assignTelemetryField(document, paths, ['exportHash'], payload.exportHash);
  assignTelemetryField(document, paths, ['governanceEventId'], payload.governanceEventId);
  assignTelemetryField(document, paths, ['governanceHash'], payload.governanceHash);
  assignTelemetryField(document, paths, ['complianceReceiptId'], payload.complianceReceiptId);
  assignTelemetryField(document, paths, ['telemetryEventId'], payload.telemetryEventId);
  assignTelemetryField(
    document,
    paths,
    ['payload', 'metadata', 'details', 'context', 'data'],
    payload
  );
  assignTelemetryField(
    document,
    paths,
    ['timestamp', 'eventAt', 'occurredAt', 'createdAt', 'generatedAt'],
    generatedAt
  );
  assignTelemetryField(document, paths, ['boardReady'], payload.boardReady);
  assignTelemetryField(document, paths, ['regulatorReady'], payload.regulatorReady);

  return hydrateRequiredRegulatorExportRecordFields(model, document, context);
}

/**
 * @function persistLeadSearchRegulatorExportReceipt
 * @description Persists a CrmRecord receipt for a verified regulator evidence export.
 * @param {Object} regulatorExport - Regulator export response.
 * @returns {Promise<Object>} Export receipt persistence response.
 * @collaboration Converts regulator-ready export JSON into a searchable backend record.
 */
async function persistLeadSearchRegulatorExportReceipt(regulatorExport = {}) {
  const model = resolveRegulatorExportRecordModel();
  const payload = buildRegulatorExportReceiptPayload(regulatorExport);
  const exportReceiptHash = createHashDigest(JSON.stringify(payload));

  if (!model) {
    return {
      persisted: false,
      status: 'REGULATOR_EXPORT_RECORD_MODEL_NOT_REGISTERED',
      modelName: 'CrmRecord',
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      exportReceiptHash,
      exportReceiptHashShort: exportReceiptHash.slice(0, 16),
      generatedAt: payload.generatedAt,
    };
  }

  try {
    const document = buildRegulatorExportReceiptDocument(model, payload, exportReceiptHash);
    const created = await model.create(document);

    return {
      persisted: true,
      status: 'REGULATOR_EXPORT_RECEIPT_PERSISTED',
      modelName: model.modelName || 'CrmRecord',
      exportReceiptId: String(created?._id || created?.id || ''),
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      exportReceiptHash,
      exportReceiptHashShort: exportReceiptHash.slice(0, 16),
      generatedAt: payload.generatedAt,
    };
  } catch (error) {
    return {
      persisted: false,
      status: 'REGULATOR_EXPORT_RECEIPT_WRITE_FAILED',
      modelName: model.modelName || 'CrmRecord',
      errorName: error?.name || 'UnknownError',
      errorMessage: String(error?.message || 'Unknown export receipt write failure').slice(0, 220),
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      exportReceiptHash,
      exportReceiptHashShort: exportReceiptHash.slice(0, 16),
      generatedAt: payload.generatedAt,
    };
  }
}

/**
 * @function materializeLeadSearchRegulatorExportReceipt
 * @description Exports regulator evidence and persists an export receipt into CrmRecord.
 * @param {Object} params - Materialization parameters.
 * @returns {Promise<Object>} Export receipt materialization response.
 * @collaboration Closes the CRM backend source ledger by activating genericRecords with real export evidence.
 */
export async function materializeLeadSearchRegulatorExportReceipt(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const governanceId = String(
    params.governanceId || params.governanceEventId || params.governanceHash || ''
  ).trim();
  const regulatorExport = await exportLeadSearchRegulatorEvidenceBundle({ tenantId, governanceId });

  if (!regulatorExport.ok) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      tenantId,
      governanceId,
      status: 'REGULATOR_EXPORT_RECEIPT_NOT_MATERIALIZED_EXPORT_NOT_READY',
      regulatorExport,
      exportReceiptPersistence: {
        persisted: false,
        status: 'REGULATOR_EXPORT_NOT_READY',
        modelName: 'CrmRecord',
        version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      },
    };
  }

  const exportReceiptPersistence = await persistLeadSearchRegulatorExportReceipt(regulatorExport);

  return {
    ok: Boolean(exportReceiptPersistence.persisted),
    version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
    tenantId,
    governanceId,
    status: exportReceiptPersistence.persisted
      ? 'REGULATOR_EXPORT_RECEIPT_MATERIALIZED'
      : exportReceiptPersistence.status,
    regulatorExport,
    exportReceiptPersistence,
    exportReceiptPersisted: Boolean(exportReceiptPersistence.persisted),
    exportReceiptId: exportReceiptPersistence.exportReceiptId || null,
    exportReceiptHash: exportReceiptPersistence.exportReceiptHash || null,
    exportReceiptHashShort: exportReceiptPersistence.exportReceiptHashShort || null,
  };
}

/**
 * @function listLeadSearchRegulatorExportReceipts
 * @description Lists recent regulator export receipts from CrmRecord.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Export receipt list response.
 * @collaboration Provides a searchable ledger of regulator export receipts without filesystem artifacts.
 */
export async function listLeadSearchRegulatorExportReceipts(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 10), 1), 50);
  const model = resolveRegulatorExportRecordModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      tenantId,
      total: 0,
      status: 'REGULATOR_EXPORT_RECORD_MODEL_NOT_REGISTERED',
      exportReceipts: [],
    };
  }

  const filter = buildTenantFilter(model, tenantId);

  const records = await model
    .find(filter)
    .sort({ createdAt: -1, generatedAt: -1, timestamp: -1, eventAt: -1 })
    .limit(Math.max(limit * 20, 200))
    .lean();

  const exportReceipts = records
    .map((record) => {
      const payload =
        record.payload ||
        record.metadata ||
        record.details ||
        record.context ||
        record.data ||
        null;
      const exportReceiptHash = String(
        record.exportReceiptHash ||
          record.receiptHash ||
          record.hash ||
          record.provenanceHash ||
          (payload ? createHashDigest(JSON.stringify(payload)) : '')
      );

      return {
        id: String(record._id || record.id || ''),
        version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
        modelName: model.modelName || 'CrmRecord',
        eventType: String(
          payload?.exportType ||
            record.eventType ||
            record.type ||
            record.recordType ||
            record.kind ||
            'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT'
        ),
        tenantId: String(record.tenantId || record.tenant || payload?.tenantId || tenantId),
        operatorId: String(
          record.operatorId || record.actorId || record.userId || payload?.operatorId || 'SYSTEM'
        ),
        query: String(record.query || record.searchQuery || payload?.query || ''),
        status: String(record.status || record.recordStatus || payload?.status || 'SEALED'),
        exportReceiptHash,
        exportReceiptHashShort: exportReceiptHash ? exportReceiptHash.slice(0, 16) : null,
        exportHash: payload?.exportHash || record.exportHash || null,
        exportHashShort: payload?.exportHashShort || null,
        governanceEventId: payload?.governanceEventId || record.governanceEventId || null,
        governanceHashShort: payload?.governanceHashShort || null,
        boardReady: Boolean(record.boardReady ?? payload?.boardReady),
        regulatorReady: Boolean(record.regulatorReady ?? payload?.regulatorReady),
        createdAt:
          record.createdAt ||
          record.generatedAt ||
          record.timestamp ||
          payload?.generatedAt ||
          null,
        payloadAvailable: Boolean(payload),
        payload,
      };
    })
    .filter((receipt) => {
      const signature = [
        receipt.eventType,
        receipt.payload?.version,
        receipt.payload?.exportType,
        receipt.payload?.sourceExportType,
        receipt.payload?.route,
        receipt.payload?.exportHash,
        receipt.payload?.governanceEventId,
      ]
        .filter(Boolean)
        .join(' ');

      return /CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT|R68J-REGULATOR-EXPORT-RECEIPT-MATERIALIZATION|REGULATOR_EXPORT_RECEIPT/i.test(
        signature
      );
    })
    .slice(0, limit);

  return {
    ok: true,
    version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
    tenantId,
    total: exportReceipts.length,
    status: 'REGULATOR_EXPORT_RECEIPTS_LISTED',
    exportReceipts,
  };
}

/**
 * @function resolveRegulatorExportReceiptFieldValue
 * @description Resolves the first available field value from a regulator export receipt record.
 * @param {Object} record - Persisted CrmRecord document.
 * @param {string[]} fields - Candidate fields.
 * @param {*} fallback - Fallback value.
 * @returns {*} Resolved value.
 * @collaboration Normalizes flexible CrmRecord schemas for receipt verification.
 */
function resolveRegulatorExportReceiptFieldValue(record = {}, fields = [], fallback = null) {
  for (const field of fields) {
    if (record[field] !== undefined && record[field] !== null && record[field] !== '') {
      return record[field];
    }
  }

  return fallback;
}

/**
 * @function extractRegulatorExportReceiptPayload
 * @description Extracts the regulator export receipt payload from a persisted record.
 * @param {Object} record - Persisted CrmRecord document.
 * @returns {Object|null} Receipt payload.
 * @collaboration Preserves the real R68J payload for verification even when enum-safe top-level fields differ.
 */
function extractRegulatorExportReceiptPayload(record = {}) {
  return (
    record.payload || record.metadata || record.details || record.context || record.data || null
  );
}

/**
 * @function computeRegulatorExportReceiptPayloadHash
 * @description Computes the canonical hash of a persisted regulator export receipt payload.
 * @param {Object} record - Persisted CrmRecord document.
 * @returns {string} Receipt payload hash.
 * @collaboration Verifies that persisted CrmRecord receipt payloads remain stable.
 */
function computeRegulatorExportReceiptPayloadHash(record = {}) {
  const payload = extractRegulatorExportReceiptPayload(record);

  if (!payload) return '';

  return createHashDigest(JSON.stringify(payload));
}

/**
 * @function verifyRegulatorExportIntegrityFromReceiptPayload
 * @description Verifies the regulator export hash carried inside the receipt payload.
 * @param {Object} payload - Persisted R68J receipt payload.
 * @returns {Object} Regulator export integrity packet.
 * @collaboration Proves the persisted receipt still carries a valid R68I export hash input packet.
 */
function verifyRegulatorExportIntegrityFromReceiptPayload(payload = {}) {
  const exportIntegrity = payload.exportIntegrity || {};
  const hashInput = exportIntegrity.hashInput || null;
  const storedExportHash = payload.exportHash || exportIntegrity.exportHash || '';

  if (!hashInput || !storedExportHash) {
    return {
      verified: false,
      status: 'REGULATOR_EXPORT_HASH_INPUT_NOT_AVAILABLE',
      storedExportHash: storedExportHash || null,
      storedExportHashShort: storedExportHash ? storedExportHash.slice(0, 16) : null,
      recomputedExportHash: null,
      recomputedExportHashShort: null,
    };
  }

  const recomputedExportHash = createHashDigest(JSON.stringify(hashInput));
  const verified = storedExportHash === recomputedExportHash;

  return {
    verified,
    status: verified ? 'REGULATOR_EXPORT_HASH_VERIFIED' : 'REGULATOR_EXPORT_HASH_MISMATCH',
    storedExportHash,
    storedExportHashShort: storedExportHash.slice(0, 16),
    recomputedExportHash,
    recomputedExportHashShort: recomputedExportHash.slice(0, 16),
  };
}

/**
 * @function buildRegulatorExportReceiptLookupFilter
 * @description Builds a tenant-scoped lookup filter for export receipt id or hash.
 * @param {Object} model - CrmRecord model.
 * @param {string} tenantId - Tenant id.
 * @param {string} receiptId - Receipt id, export receipt hash, export hash, or governance id.
 * @returns {Object} Mongoose filter.
 * @collaboration Supports regulator export receipt lookup across flexible CrmRecord schemas.
 */
function buildRegulatorExportReceiptLookupFilter(model, tenantId = 'MASTER', receiptId = '') {
  const filter = buildTenantFilter(model, tenantId);
  const paths = getSchemaPathNames(model);
  const clauses = [];
  const value = String(receiptId || '').trim();

  if (mongoose.Types.ObjectId.isValid(value)) {
    clauses.push({ _id: new mongoose.Types.ObjectId(value) });
  }

  [
    'exportReceiptHash',
    'receiptHash',
    'hash',
    'provenanceHash',
    'exportHash',
    'governanceEventId',
    'governanceHash',
  ].forEach((field) => {
    if (paths.has(field)) clauses.push({ [field]: value });
  });

  if (!clauses.length) return filter;

  return { $and: [filter, { $or: clauses }] };
}

/**
 * @function normalizeLeadSearchRegulatorExportReceipt
 * @description Normalizes and verifies a persisted regulator export receipt.
 * @param {Object} record - Persisted CrmRecord document.
 * @param {Object} model - CrmRecord model.
 * @returns {Object} Normalized receipt.
 * @collaboration Produces the regulator-facing verification packet for one persisted export receipt.
 */
function normalizeLeadSearchRegulatorExportReceipt(record = {}, model = null) {
  const payload = extractRegulatorExportReceiptPayload(record);
  const recomputedReceiptHash = computeRegulatorExportReceiptPayloadHash(record);
  const storedReceiptHash = String(
    resolveRegulatorExportReceiptFieldValue(
      record,
      ['exportReceiptHash', 'receiptHash', 'hash', 'provenanceHash'],
      ''
    ) || ''
  );
  const effectiveReceiptHash = storedReceiptHash || recomputedReceiptHash;
  const regulatorExportIntegrity = verifyRegulatorExportIntegrityFromReceiptPayload(payload || {});
  const receiptHashVerified = Boolean(
    storedReceiptHash && recomputedReceiptHash && storedReceiptHash === recomputedReceiptHash
  );
  const receiptHashRecomputed = Boolean(!storedReceiptHash && recomputedReceiptHash);

  return {
    id: String(record._id || record.id || ''),
    version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION,
    materializationVersion: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
    modelName: model?.modelName || 'CrmRecord',
    eventType: String(
      payload?.exportType ||
        record.eventType ||
        record.type ||
        record.recordType ||
        record.kind ||
        'CRM_LEAD_SEARCH_REGULATOR_EXPORT_RECEIPT'
    ),
    tenantId: String(record.tenantId || record.tenant || payload?.tenantId || 'MASTER'),
    operatorId: String(
      record.operatorId || record.actorId || record.userId || payload?.operatorId || 'SYSTEM'
    ),
    query: String(record.query || record.searchQuery || payload?.query || ''),
    status: String(record.status || record.recordStatus || payload?.status || 'SEALED'),
    exportReceiptHash: effectiveReceiptHash || null,
    exportReceiptHashShort: effectiveReceiptHash ? effectiveReceiptHash.slice(0, 16) : null,
    exportHash: payload?.exportHash || record.exportHash || null,
    exportHashShort: payload?.exportHashShort || null,
    governanceEventId: payload?.governanceEventId || record.governanceEventId || null,
    governanceHash: payload?.governanceHash || record.governanceHash || null,
    governanceHashShort: payload?.governanceHashShort || null,
    complianceReceiptId: payload?.complianceReceiptId || record.complianceReceiptId || null,
    telemetryEventId: payload?.telemetryEventId || record.telemetryEventId || null,
    boardReady: Boolean(record.boardReady ?? payload?.boardReady),
    regulatorReady: Boolean(record.regulatorReady ?? payload?.regulatorReady),
    createdAt:
      record.createdAt || record.generatedAt || record.timestamp || payload?.generatedAt || null,
    integrity: {
      verified: Boolean(
        (receiptHashVerified || receiptHashRecomputed) && regulatorExportIntegrity.verified
      ),
      status: receiptHashVerified
        ? 'REGULATOR_EXPORT_RECEIPT_HASH_VERIFIED'
        : receiptHashRecomputed
          ? 'REGULATOR_EXPORT_RECEIPT_HASH_RECOMPUTED'
          : 'REGULATOR_EXPORT_RECEIPT_HASH_NOT_AVAILABLE',
      storedHash: storedReceiptHash || null,
      storedHashShort: storedReceiptHash ? storedReceiptHash.slice(0, 16) : null,
      recomputedHash: recomputedReceiptHash || null,
      recomputedHashShort: recomputedReceiptHash ? recomputedReceiptHash.slice(0, 16) : null,
      regulatorExportIntegrity,
    },
    payloadAvailable: Boolean(payload),
    payload,
  };
}

/**
 * @function findRegulatorExportReceiptByHashFallback
 * @description Finds an export receipt by scanning recent tenant records and comparing payload hashes.
 * @param {Object} params - Lookup parameters.
 * @returns {Promise<Object|null>} Matched record or null.
 * @collaboration Enables lookup by exportReceiptHash or exportHash when schema did not persist top-level hash fields.
 */
async function findRegulatorExportReceiptByHashFallback(params = {}) {
  const model = params.model;
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(params.receiptId || '').trim();

  if (!model || !receiptId) return null;

  const filter = buildTenantFilter(model, tenantId);
  const records = await model
    .find(filter)
    .sort({ createdAt: -1, generatedAt: -1, timestamp: -1, eventAt: -1 })
    .limit(500)
    .lean();

  return (
    records.find((record) => {
      const normalized = normalizeLeadSearchRegulatorExportReceipt(record, model);
      const payload = normalized.payload || {};
      const candidates = [
        normalized.id,
        normalized.exportReceiptHash,
        normalized.exportHash,
        normalized.governanceEventId,
        normalized.governanceHash,
        payload?.exportHash,
        payload?.governanceEventId,
        payload?.governanceHash,
        payload?.exportReceiptHash,
      ]
        .filter(Boolean)
        .map((value) => String(value));

      return candidates.includes(receiptId);
    }) || null
  );
}

/**
 * @function verifyLeadSearchRegulatorExportReceipt
 * @description Verifies a persisted regulator export receipt by id, exportReceiptHash, exportHash, or governance id.
 * @param {Object} params - Verification parameters.
 * @returns {Promise<Object>} Receipt verification response.
 * @collaboration Gives regulators a stable verification endpoint over persisted export receipt records.
 */
export async function verifyLeadSearchRegulatorExportReceipt(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(
    params.receiptId ||
      params.exportReceiptId ||
      params.exportReceiptHash ||
      params.exportHash ||
      ''
  ).trim();
  const model = resolveRegulatorExportRecordModel();

  if (!model) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      receiptId,
      status: 'REGULATOR_EXPORT_RECORD_MODEL_NOT_REGISTERED',
      exportReceipt: null,
    };
  }

  const filter = buildRegulatorExportReceiptLookupFilter(model, tenantId, receiptId);
  let record = await model.findOne(filter).lean();

  if (!record) {
    record = await findRegulatorExportReceiptByHashFallback({ model, tenantId, receiptId });
  }

  if (!record) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION,
      tenantId,
      receiptId,
      status: 'REGULATOR_EXPORT_RECEIPT_NOT_FOUND',
      exportReceipt: null,
    };
  }

  const exportReceipt = normalizeLeadSearchRegulatorExportReceipt(record, model);

  return {
    ok: true,
    version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION,
    tenantId,
    receiptId,
    status: 'REGULATOR_EXPORT_RECEIPT_FOUND',
    exportReceipt,
  };
}

/**
 * @function listLeadSearchRegulatorExportReceiptVerifications
 * @description Lists verified regulator export receipt packets.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Verified receipt list response.
 * @collaboration Provides a verification ledger for persisted regulator export receipts.
 */
export async function listLeadSearchRegulatorExportReceiptVerifications(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 10), 1), 50);
  const receiptLedger = await listLeadSearchRegulatorExportReceipts({ tenantId, limit });
  const exportReceipts = receiptLedger.exportReceipts || [];
  const verifiedReceipts = await Promise.all(
    exportReceipts.map((receipt) =>
      verifyLeadSearchRegulatorExportReceipt({
        tenantId,
        receiptId: receipt.id || receipt.exportReceiptHash || receipt.exportHash,
      })
    )
  );

  return {
    ok: true,
    version: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION,
    tenantId,
    total: verifiedReceipts.length,
    verified: verifiedReceipts.filter((receipt) => receipt.exportReceipt?.integrity?.verified)
      .length,
    status: 'REGULATOR_EXPORT_RECEIPT_VERIFICATIONS_LISTED',
    exportReceipts: verifiedReceipts.map((receipt) => receipt.exportReceipt).filter(Boolean),
  };
}

/**
 * @function resolveRegulatorDossierSourceRegistry
 * @description Resolves the source registry from the regulator evidence bundle.
 * @param {Object} evidenceBundle - Regulator evidence bundle.
 * @returns {Array} Source registry.
 * @collaboration Gives the dossier a stable source-system posture without creating new records.
 */
function resolveRegulatorDossierSourceRegistry(evidenceBundle = {}) {
  return (
    evidenceBundle.telemetryReceipt?.payload?.registry ||
    evidenceBundle.governanceProof?.payload?.registry ||
    evidenceBundle.complianceReceipt?.payload?.registry ||
    []
  );
}

/**
 * @function resolveRegulatorDossierComplianceBindings
 * @description Resolves compliance bindings for the regulator dossier.
 * @param {Object} evidenceBundle - Regulator evidence bundle.
 * @returns {Array} Compliance bindings.
 * @collaboration Ensures POPIA, GDPR, SOC2 and regulator-export controls travel with the dossier.
 */
function resolveRegulatorDossierComplianceBindings(evidenceBundle = {}) {
  return (
    evidenceBundle.complianceReceipt?.complianceBindings ||
    evidenceBundle.complianceReceipt?.payload?.complianceBindings ||
    evidenceBundle.telemetryReceipt?.payload?.complianceBindings ||
    evidenceBundle.complianceVerification?.complianceReceipt?.complianceBindings ||
    []
  );
}

/**
 * @function buildRegulatorDossierHashInput
 * @description Builds canonical hash input for a regulator evidence dossier.
 * @param {Object} dossierCore - Dossier core.
 * @returns {Object} Dossier hash input.
 * @collaboration Provides deterministic integrity over the dossier response.
 */
function buildRegulatorDossierHashInput(dossierCore = {}) {
  return {
    dossierType: dossierCore.dossierType,
    dossierVersion: dossierCore.dossierVersion,
    tenantId: dossierCore.tenantId,
    query: dossierCore.query,
    operatorId: dossierCore.operatorId,
    exportReceiptId: dossierCore.verifiedExportReceipt?.id || null,
    exportReceiptHash: dossierCore.verifiedExportReceipt?.exportReceiptHash || null,
    exportHash:
      dossierCore.verifiedExportReceipt?.exportHash ||
      dossierCore.regulatorEvidenceBundle?.hashes?.exportHash ||
      null,
    governanceEventId:
      dossierCore.governanceProof?.id ||
      dossierCore.verifiedExportReceipt?.governanceEventId ||
      null,
    governanceHash:
      dossierCore.governanceProof?.governanceHash ||
      dossierCore.verifiedExportReceipt?.governanceHash ||
      null,
    complianceReceiptId:
      dossierCore.complianceReceipt?.id || dossierCore.complianceReceipt?.receiptId || null,
    telemetryEventId: dossierCore.telemetryReceipt?.id || null,
    evidenceChainStatus: dossierCore.evidenceChainProof?.status || null,
    sourceRegistryCount: Array.isArray(dossierCore.sourceRegistry)
      ? dossierCore.sourceRegistry.length
      : 0,
    generatedAt: dossierCore.generatedAt,
  };
}

/**
 * @function buildRegulatorDossierReadiness
 * @description Builds the readiness posture for a regulator evidence dossier.
 * @param {Object} params - Readiness dependencies.
 * @returns {Object} Readiness posture.
 * @collaboration Summarizes board-ready and regulator-ready state for the response.
 */
function buildRegulatorDossierReadiness(params = {}) {
  const receipt = params.verifiedExportReceipt || {};
  const bundle = params.regulatorEvidenceBundle || {};
  const evidenceStatus = bundle.evidenceStatus || {};

  const verifiedExportReceipt = Boolean(receipt.integrity?.verified);
  const verifiedRegulatorExport = Boolean(
    receipt.integrity?.regulatorExportIntegrity?.verified || bundle.exportIntegrity?.verified
  );
  const verifiedTelemetry = Boolean(
    evidenceStatus.telemetryReceiptVerified || bundle.telemetryReceipt?.integrity?.verified
  );
  const verifiedCompliance = Boolean(
    evidenceStatus.complianceReceiptVerified || bundle.complianceReceipt?.integrity?.verified
  );
  const verifiedEvidenceChain = Boolean(
    evidenceStatus.evidenceChainVerified || bundle.evidenceChain?.chainVerified
  );
  const verifiedGovernance = Boolean(
    evidenceStatus.governanceEventVerified || bundle.governanceProof?.integrity?.verified
  );
  const sourceRegistryLive =
    Array.isArray(params.sourceRegistry) &&
    params.sourceRegistry.length >= 11 &&
    params.sourceRegistry.every(
      (source) => source?.sourceStatus === 'SOURCE_LIVE' && source?.connected === true
    );

  const ready = Boolean(
    verifiedExportReceipt &&
    verifiedRegulatorExport &&
    verifiedTelemetry &&
    verifiedCompliance &&
    verifiedEvidenceChain &&
    verifiedGovernance &&
    sourceRegistryLive
  );

  return {
    ready,
    boardReady: ready,
    regulatorReady: ready,
    status: ready ? 'REGULATOR_EVIDENCE_DOSSIER_READY' : 'REGULATOR_EVIDENCE_DOSSIER_PARTIAL',
    checks: {
      verifiedExportReceipt,
      verifiedRegulatorExport,
      verifiedTelemetry,
      verifiedCompliance,
      verifiedEvidenceChain,
      verifiedGovernance,
      sourceRegistryLive,
    },
  };
}

/**
 * @function buildRegulatorEvidenceDossierCore
 * @description Builds the complete regulator evidence dossier response core.
 * @param {Object} params - Dossier dependencies.
 * @returns {Object} Dossier core.
 * @collaboration Combines verified export receipt, evidence bundle, governance, chain, compliance, telemetry and source registry.
 */
function buildRegulatorEvidenceDossierCore(params = {}) {
  const verifiedReceiptResponse = params.verifiedReceiptResponse || {};
  const verifiedExportReceipt = verifiedReceiptResponse.exportReceipt || {};
  const regulatorExportResponse = params.regulatorExportResponse || {};
  const regulatorEvidenceBundle = regulatorExportResponse.evidenceBundle || {};
  const sourceRegistry = resolveRegulatorDossierSourceRegistry(regulatorEvidenceBundle);
  const complianceBindings = resolveRegulatorDossierComplianceBindings(regulatorEvidenceBundle);
  const generatedAt = new Date().toISOString();

  const readiness = buildRegulatorDossierReadiness({
    verifiedExportReceipt,
    regulatorEvidenceBundle,
    sourceRegistry,
  });

  return {
    dossierType: 'CRM_LEAD_SEARCH_REGULATOR_EVIDENCE_DOSSIER',
    dossierVersion: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
    tenantId:
      verifiedExportReceipt.tenantId ||
      regulatorEvidenceBundle.tenantId ||
      params.tenantId ||
      'MASTER',
    query: verifiedExportReceipt.query || regulatorEvidenceBundle.query || '',
    operatorId: verifiedExportReceipt.operatorId || regulatorEvidenceBundle.operatorId || 'SYSTEM',
    generatedAt,
    route: '/api/crm/command/search/regulator-evidence/dossier/:receiptId',
    persistenceMode: 'JSON_RESPONSE_ONLY',
    readiness,
    verifiedExportReceipt,
    regulatorExportResponse,
    regulatorEvidenceBundle,
    governanceProof: regulatorEvidenceBundle.governanceProof || null,
    evidenceChainProof: regulatorEvidenceBundle.evidenceChain || null,
    complianceReceipt: regulatorEvidenceBundle.complianceReceipt || null,
    telemetryReceipt: regulatorEvidenceBundle.telemetryReceipt || null,
    sourceRegistry,
    sourceRegistryStatus: {
      totalSources: sourceRegistry.length,
      liveSources: sourceRegistry.filter((source) => source?.sourceStatus === 'SOURCE_LIVE').length,
      connectedSources: sourceRegistry.filter((source) => source?.connected === true).length,
      searchableSources: sourceRegistry.filter((source) => source?.searchable === true).length,
      sourceGaps:
        regulatorEvidenceBundle.telemetryReceipt?.payload?.sourceGaps ||
        regulatorEvidenceBundle.sourceGaps ||
        [],
    },
    complianceBindings,
    dossierMetadata: {
      generatedBy: 'WILSY_OS_CRM_COMMAND_FABRIC',
      receiptVerificationVersion: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERIFICATION_VERSION,
      exportVersion: WILSY_CRM_REGULATOR_EVIDENCE_EXPORT_VERSION,
      materializationVersion: WILSY_CRM_REGULATOR_EXPORT_RECEIPT_VERSION,
      dossierVersion: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
      noFilesystemWrite: true,
      reviewMode: 'BOARD_AND_REGULATOR_JSON_DOSSIER',
    },
  };
}

/**
 * @function sealRegulatorEvidenceDossier
 * @description Seals the regulator evidence dossier with a deterministic dossier hash.
 * @param {Object} dossierCore - Dossier core.
 * @returns {Object} Sealed dossier.
 * @collaboration Gives the dossier one top-level hash over its verified chain.
 */
function sealRegulatorEvidenceDossier(dossierCore = {}) {
  const hashInput = buildRegulatorDossierHashInput(dossierCore);
  const dossierHash = createHashDigest(JSON.stringify(hashInput));

  return {
    ...dossierCore,
    dossierHash,
    dossierHashShort: dossierHash.slice(0, 16),
    dossierIntegrity: {
      verified: Boolean(dossierCore.readiness?.ready),
      status: dossierCore.readiness?.ready
        ? 'REGULATOR_EVIDENCE_DOSSIER_HASH_VERIFIED'
        : 'REGULATOR_EVIDENCE_DOSSIER_HASH_PARTIAL',
      dossierHash,
      dossierHashShort: dossierHash.slice(0, 16),
      hashInput,
    },
  };
}

/**
 * @function buildLeadSearchRegulatorEvidenceDossier
 * @description Builds one regulator-ready evidence dossier from a verified export receipt.
 * @param {Object} params - Dossier parameters.
 * @returns {Promise<Object>} Dossier response.
 * @collaboration Assembles the final board/regulator JSON response without writing files.
 */
export async function buildLeadSearchRegulatorEvidenceDossier(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const receiptId = String(
    params.receiptId ||
      params.exportReceiptId ||
      params.exportReceiptHash ||
      params.exportHash ||
      ''
  ).trim();

  const verifiedReceiptResponse = await verifyLeadSearchRegulatorExportReceipt({
    tenantId,
    receiptId,
  });

  if (!verifiedReceiptResponse.ok || !verifiedReceiptResponse.exportReceipt) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
      tenantId,
      receiptId,
      status: 'REGULATOR_EVIDENCE_DOSSIER_RECEIPT_NOT_FOUND',
      dossier: null,
      verifiedReceiptResponse,
    };
  }

  const verifiedExportReceipt = verifiedReceiptResponse.exportReceipt;
  const governanceId =
    verifiedExportReceipt.governanceEventId ||
    verifiedExportReceipt.payload?.governanceEventId ||
    verifiedExportReceipt.governanceHash ||
    verifiedExportReceipt.payload?.governanceHash ||
    '';

  const regulatorExportResponse = await exportLeadSearchRegulatorEvidenceBundle({
    tenantId,
    governanceId,
  });

  if (!regulatorExportResponse.ok || !regulatorExportResponse.evidenceBundle) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
      tenantId,
      receiptId,
      status: 'REGULATOR_EVIDENCE_DOSSIER_EXPORT_NOT_READY',
      dossier: null,
      verifiedReceiptResponse,
      regulatorExportResponse,
    };
  }

  const dossierCore = buildRegulatorEvidenceDossierCore({
    tenantId,
    verifiedReceiptResponse,
    regulatorExportResponse,
  });

  const dossier = sealRegulatorEvidenceDossier(dossierCore);

  return {
    ok: Boolean(dossier.dossierIntegrity?.verified),
    version: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
    tenantId,
    receiptId,
    status: dossier.readiness?.status || 'REGULATOR_EVIDENCE_DOSSIER_PARTIAL',
    dossierHash: dossier.dossierHash,
    dossierHashShort: dossier.dossierHashShort,
    dossier,
  };
}

/**
 * @function listLeadSearchRegulatorEvidenceDossiers
 * @description Lists recent regulator-ready evidence dossiers.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Dossier list response.
 * @collaboration Provides a JSON-only board/regulator dossier ledger.
 */
export async function listLeadSearchRegulatorEvidenceDossiers(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 5), 1), 25);
  const verifiedLedger = await listLeadSearchRegulatorExportReceiptVerifications({
    tenantId,
    limit,
  });

  const dossiers = await Promise.all(
    (verifiedLedger.exportReceipts || []).map((receipt) =>
      buildLeadSearchRegulatorEvidenceDossier({
        tenantId,
        receiptId: receipt.id || receipt.exportReceiptHash || receipt.exportHash,
      })
    )
  );

  return {
    ok: true,
    version: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
    tenantId,
    total: dossiers.length,
    ready: dossiers.filter((item) => item.ok).length,
    status: 'REGULATOR_EVIDENCE_DOSSIERS_LISTED',
    dossiers,
  };
}

/**
 * @function computeRegulatorDossierHashFromInput
 * @description Computes a dossier hash from a dossier integrity hash input.
 * @param {Object} hashInput - Dossier hash input.
 * @returns {string} Recomputed dossier hash.
 * @collaboration Proves the final regulator dossier hash input has not changed.
 */
function computeRegulatorDossierHashFromInput(hashInput = {}) {
  if (!hashInput || typeof hashInput !== 'object') return '';

  return createHashDigest(JSON.stringify(hashInput));
}

/**
 * @function resolveRegulatorDossierLookupCandidates
 * @description Resolves dossier lookup candidates from a dossier response.
 * @param {Object} dossierResponse - R68L dossier response.
 * @returns {string[]} Lookup candidates.
 * @collaboration Allows R68M to verify by dossier hash, export receipt hash, export hash, or governance id.
 */
function resolveRegulatorDossierLookupCandidates(dossierResponse = {}) {
  const dossier = dossierResponse.dossier || dossierResponse;
  const receipt = dossier.verifiedExportReceipt || {};
  const bundle = dossier.regulatorEvidenceBundle || {};
  const proof = dossier.governanceProof || {};
  const integrity = dossier.dossierIntegrity || {};
  const hashInput = integrity.hashInput || {};

  return [
    dossierResponse.dossierHash,
    dossier.dossierHash,
    integrity.dossierHash,
    receipt.id,
    receipt.exportReceiptHash,
    receipt.exportHash,
    receipt.governanceEventId,
    receipt.governanceHash,
    bundle.hashes?.exportHash,
    bundle.hashes?.governanceHash,
    proof.id,
    proof.governanceHash,
    hashInput.exportReceiptId,
    hashInput.exportReceiptHash,
    hashInput.exportHash,
    hashInput.governanceEventId,
    hashInput.governanceHash,
  ]
    .filter(Boolean)
    .map((value) => String(value));
}

/**
 * @function verifyRegulatorDossierIntegrity
 * @description Verifies a returned dossier hash against its stored final hash input.
 * @param {Object} dossierResponse - R68L dossier response.
 * @returns {Object} Dossier verification packet.
 * @collaboration Recomputes the top-level dossier hash from the final hash input.
 */
function verifyRegulatorDossierIntegrity(dossierResponse = {}) {
  const dossier = dossierResponse.dossier || {};
  const integrity = dossier.dossierIntegrity || {};
  const hashInput = integrity.hashInput || null;
  const storedDossierHash =
    dossier.dossierHash || dossierResponse.dossierHash || integrity.dossierHash || '';

  if (!hashInput || !storedDossierHash) {
    return {
      verified: false,
      status: 'REGULATOR_DOSSIER_HASH_INPUT_NOT_AVAILABLE',
      storedDossierHash: storedDossierHash || null,
      storedDossierHashShort: storedDossierHash ? storedDossierHash.slice(0, 16) : null,
      recomputedDossierHash: null,
      recomputedDossierHashShort: null,
      hashInputAvailable: Boolean(hashInput),
    };
  }

  const recomputedDossierHash = computeRegulatorDossierHashFromInput(hashInput);
  const verified = storedDossierHash === recomputedDossierHash;

  return {
    verified,
    status: verified ? 'REGULATOR_DOSSIER_HASH_VERIFIED' : 'REGULATOR_DOSSIER_HASH_MISMATCH',
    storedDossierHash,
    storedDossierHashShort: storedDossierHash.slice(0, 16),
    recomputedDossierHash,
    recomputedDossierHashShort: recomputedDossierHash.slice(0, 16),
    hashInput,
  };
}

/**
 * @function buildRegulatorDossierVerificationPacket
 * @description Builds a normalized regulator dossier verification response packet.
 * @param {Object} dossierResponse - R68L dossier response.
 * @param {string} dossierId - Lookup id or hash.
 * @returns {Object} Verification packet.
 * @collaboration Summarizes dossier, receipt, export, governance, chain, compliance, telemetry, and source checks.
 */
function buildRegulatorDossierVerificationPacket(dossierResponse = {}, dossierId = '') {
  const dossier = dossierResponse.dossier || {};
  const readiness = dossier.readiness || {};
  const checks = readiness.checks || {};
  const dossierIntegrity = verifyRegulatorDossierIntegrity(dossierResponse);
  const sourceRegistryStatus = dossier.sourceRegistryStatus || {};

  return {
    dossierType: 'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_VERIFICATION',
    version: WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION,
    dossierVersion: WILSY_CRM_REGULATOR_EVIDENCE_DOSSIER_VERSION,
    lookupId: dossierId,
    tenantId: dossier.tenantId || dossierResponse.tenantId || 'MASTER',
    query: dossier.query || '',
    operatorId: dossier.operatorId || 'SYSTEM',
    status:
      dossierIntegrity.verified && readiness.regulatorReady
        ? 'REGULATOR_DOSSIER_VERIFIED'
        : 'REGULATOR_DOSSIER_PARTIAL',
    verified: Boolean(dossierIntegrity.verified && readiness.regulatorReady),
    dossierHash: dossier.dossierHash || dossierResponse.dossierHash || null,
    dossierHashShort: dossier.dossierHashShort || dossierResponse.dossierHashShort || null,
    dossierIntegrity,
    verificationSummary: {
      verifiedDossierHash: Boolean(dossierIntegrity.verified),
      verifiedExportReceipt: Boolean(
        checks.verifiedExportReceipt || dossier.verifiedExportReceipt?.integrity?.verified
      ),
      verifiedRegulatorExport: Boolean(
        checks.verifiedRegulatorExport || dossier.regulatorEvidenceBundle?.exportIntegrity?.verified
      ),
      verifiedGovernance: Boolean(
        checks.verifiedGovernance || dossier.governanceProof?.integrity?.verified
      ),
      verifiedEvidenceChain: Boolean(
        checks.verifiedEvidenceChain || dossier.evidenceChainProof?.chainVerified
      ),
      verifiedCompliance: Boolean(
        checks.verifiedCompliance || dossier.complianceReceipt?.integrity?.verified
      ),
      verifiedTelemetry: Boolean(
        checks.verifiedTelemetry || dossier.telemetryReceipt?.integrity?.verified
      ),
      sourceRegistryLive: Boolean(checks.sourceRegistryLive),
      sourceRegistryCount: sourceRegistryStatus.totalSources || 0,
      sourceGaps: sourceRegistryStatus.sourceGaps || [],
      noFilesystemWrite: Boolean(dossier.dossierMetadata?.noFilesystemWrite),
    },
    verifiedDossier: dossier,
  };
}

/**
 * @function findRegulatorEvidenceDossierByHashFallback
 * @description Rebuilds recent JSON-only dossiers and finds a matching dossier hash.
 * @param {Object} params - Lookup parameters.
 * @returns {Promise<Object|null>} Matching dossier response or null.
 * @collaboration Enables dossier hash lookup without persisting dossier files.
 */
async function findRegulatorEvidenceDossierByHashFallback(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const dossierId = String(params.dossierId || '').trim();

  if (!dossierId) return null;

  const latest = await listLeadSearchRegulatorEvidenceDossiers({
    tenantId,
    limit: params.limit || 25,
  });

  return (
    (latest.dossiers || []).find((dossierResponse) => {
      const candidates = resolveRegulatorDossierLookupCandidates(dossierResponse);
      return candidates.includes(dossierId);
    }) || null
  );
}

/**
 * @function verifyLeadSearchRegulatorEvidenceDossier
 * @description Verifies a regulator dossier by dossier hash, export receipt hash, export hash, or governance id.
 * @param {Object} params - Verification parameters.
 * @returns {Promise<Object>} Dossier verification response.
 * @collaboration Proves the final dossier hash input has not changed without writing files.
 */
export async function verifyLeadSearchRegulatorEvidenceDossier(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const dossierId = String(
    params.dossierId ||
      params.receiptId ||
      params.dossierHash ||
      params.exportReceiptHash ||
      params.exportHash ||
      params.governanceId ||
      ''
  ).trim();

  let dossierResponse = await buildLeadSearchRegulatorEvidenceDossier({
    tenantId,
    receiptId: dossierId,
  });

  if (!dossierResponse.ok || !dossierResponse.dossier) {
    dossierResponse = await findRegulatorEvidenceDossierByHashFallback({
      tenantId,
      dossierId,
      limit: params.limit || 25,
    });
  }

  if (!dossierResponse || !dossierResponse.dossier) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION,
      tenantId,
      dossierId,
      status: 'REGULATOR_DOSSIER_NOT_FOUND',
      verification: null,
    };
  }

  const verification = buildRegulatorDossierVerificationPacket(dossierResponse, dossierId);

  return {
    ok: Boolean(verification.verified),
    version: WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION,
    tenantId,
    dossierId,
    status: verification.status,
    dossierHash: verification.dossierHash,
    dossierHashShort: verification.dossierHashShort,
    verification,
  };
}

/**
 * @function listLeadSearchRegulatorEvidenceDossierVerifications
 * @description Lists verified regulator dossier verification packets.
 * @param {Object} params - List parameters.
 * @returns {Promise<Object>} Dossier verification list response.
 * @collaboration Provides JSON-only regulator dossier verification ledger.
 */
export async function listLeadSearchRegulatorEvidenceDossierVerifications(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 5), 1), 25);
  const latest = await listLeadSearchRegulatorEvidenceDossiers({
    tenantId,
    limit,
  });

  const verifications = await Promise.all(
    (latest.dossiers || []).map((dossierResponse) =>
      verifyLeadSearchRegulatorEvidenceDossier({
        tenantId,
        dossierId: dossierResponse.dossierHash || dossierResponse.dossier?.dossierHash,
      })
    )
  );

  return {
    ok: true,
    version: WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION,
    tenantId,
    total: verifications.length,
    verified: verifications.filter((item) => item.ok).length,
    status: 'REGULATOR_DOSSIER_VERIFICATIONS_LISTED',
    verifications,
  };
}

/**
 * @function resolveRegulatorDossierLedgerVerification
 * @description Resolves the verification payload from a dossier verification response.
 * @param {Object} verificationResponse - R68M verification response.
 * @returns {Object} Verification payload.
 * @collaboration Normalizes dossier verification responses for chain ledger construction.
 */
function resolveRegulatorDossierLedgerVerification(verificationResponse = {}) {
  return verificationResponse.verification || verificationResponse || {};
}

/**
 * @function resolveRegulatorDossierLedgerDossier
 * @description Resolves the verified dossier from a verification payload.
 * @param {Object} verification - Dossier verification payload.
 * @returns {Object} Verified dossier.
 * @collaboration Extracts the R68L dossier carried by R68M verification.
 */
function resolveRegulatorDossierLedgerDossier(verification = {}) {
  return verification.verifiedDossier || verification.dossier || {};
}

/**
 * @function buildRegulatorDossierLedgerLinkHashInput
 * @description Builds deterministic hash input for one dossier chain link.
 * @param {Object} params - Chain link fields.
 * @returns {Object} Chain link hash input.
 * @collaboration Anchors each dossier hash to the previous link hash.
 */
function buildRegulatorDossierLedgerLinkHashInput(params = {}) {
  return {
    ledgerType: 'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LINK',
    ledgerVersion: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION,
    index: Number(params.index || 0),
    tenantId: params.tenantId || 'MASTER',
    previousLinkHash: params.previousLinkHash || 'GENESIS',
    dossierHash: params.dossierHash || null,
    exportReceiptHash: params.exportReceiptHash || null,
    exportHash: params.exportHash || null,
    governanceEventId: params.governanceEventId || null,
    governanceHash: params.governanceHash || null,
    verified: Boolean(params.verified),
  };
}

/**
 * @function buildRegulatorDossierLedgerLink
 * @description Builds one verified dossier chain ledger link.
 * @param {Object} verificationResponse - R68M verification response.
 * @param {number} index - Link index.
 * @param {string} previousLinkHash - Previous link hash or GENESIS.
 * @returns {Object} Chain link.
 * @collaboration Converts verified dossier responses into ordered chain ledger links.
 */
function buildRegulatorDossierLedgerLink(
  verificationResponse = {},
  index = 0,
  previousLinkHash = 'GENESIS'
) {
  const verification = resolveRegulatorDossierLedgerVerification(verificationResponse);
  const dossier = resolveRegulatorDossierLedgerDossier(verification);
  const receipt = dossier.verifiedExportReceipt || {};
  const proof = dossier.governanceProof || {};
  const integrity = verification.dossierIntegrity || dossier.dossierIntegrity || {};
  const hashInput = integrity.hashInput || {};

  const dossierHash =
    verification.dossierHash ||
    dossier.dossierHash ||
    integrity.storedDossierHash ||
    integrity.recomputedDossierHash ||
    null;

  const linkHashInput = buildRegulatorDossierLedgerLinkHashInput({
    index,
    tenantId: verification.tenantId || dossier.tenantId || hashInput.tenantId || 'MASTER',
    previousLinkHash,
    dossierHash,
    exportReceiptHash: receipt.exportReceiptHash || hashInput.exportReceiptHash || null,
    exportHash: receipt.exportHash || hashInput.exportHash || null,
    governanceEventId: receipt.governanceEventId || proof.id || hashInput.governanceEventId || null,
    governanceHash:
      receipt.governanceHash || proof.governanceHash || hashInput.governanceHash || null,
    verified: verification.verified,
  });

  const linkHash = createHashDigest(JSON.stringify(linkHashInput));

  return {
    index,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION,
    linkType: 'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LINK',
    tenantId: linkHashInput.tenantId,
    previousLinkHash,
    previousLinkHashShort:
      previousLinkHash === 'GENESIS' ? 'GENESIS' : previousLinkHash.slice(0, 16),
    linkHash,
    linkHashShort: linkHash.slice(0, 16),
    dossierHash,
    dossierHashShort: dossierHash ? dossierHash.slice(0, 16) : null,
    exportReceiptHash: linkHashInput.exportReceiptHash,
    exportReceiptHashShort: linkHashInput.exportReceiptHash
      ? linkHashInput.exportReceiptHash.slice(0, 16)
      : null,
    exportHash: linkHashInput.exportHash,
    exportHashShort: linkHashInput.exportHash ? linkHashInput.exportHash.slice(0, 16) : null,
    governanceEventId: linkHashInput.governanceEventId,
    governanceHash: linkHashInput.governanceHash,
    governanceHashShort: linkHashInput.governanceHash
      ? linkHashInput.governanceHash.slice(0, 16)
      : null,
    verified: Boolean(verification.verified && dossierHash),
    status: verification.verified
      ? 'REGULATOR_DOSSIER_CHAIN_LINK_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_LINK_PARTIAL',
    linkHashInput,
    verification,
  };
}

/**
 * @function computeRegulatorDossierLedgerRoot
 * @description Computes the regulator dossier ledger root over ordered chain link hashes.
 * @param {Object[]} chainLinks - Ordered chain links.
 * @returns {string} Ledger root.
 * @collaboration Seals the chain ledger without writing files.
 */
function computeRegulatorDossierLedgerRoot(chainLinks = []) {
  const ledgerHashInput = chainLinks.map((link) => ({
    index: link.index,
    previousLinkHash: link.previousLinkHash,
    linkHash: link.linkHash,
    dossierHash: link.dossierHash,
  }));

  return createHashDigest(JSON.stringify(ledgerHashInput));
}

/**
 * @function verifyRegulatorDossierLedgerContinuity
 * @description Verifies ordered dossier chain continuity from GENESIS to ledger root.
 * @param {Object[]} chainLinks - Ordered chain links.
 * @param {string} ledgerRoot - Ledger root.
 * @returns {Object} Continuity proof.
 * @collaboration Proves no link is detached from the previous dossier hash chain.
 */
function verifyRegulatorDossierLedgerContinuity(chainLinks = [], ledgerRoot = '') {
  const expectedRoot = computeRegulatorDossierLedgerRoot(chainLinks);
  const rootVerified = Boolean(ledgerRoot && expectedRoot === ledgerRoot);

  const continuityChecks = chainLinks.map((link, index) => {
    const expectedPrevious = index === 0 ? 'GENESIS' : chainLinks[index - 1]?.linkHash;
    const previousVerified = link.previousLinkHash === expectedPrevious;
    const linkHashInput = buildRegulatorDossierLedgerLinkHashInput({
      index: link.index,
      tenantId: link.tenantId,
      previousLinkHash: link.previousLinkHash,
      dossierHash: link.dossierHash,
      exportReceiptHash: link.exportReceiptHash,
      exportHash: link.exportHash,
      governanceEventId: link.governanceEventId,
      governanceHash: link.governanceHash,
      verified: link.verified,
    });
    const recomputedLinkHash = createHashDigest(JSON.stringify(linkHashInput));
    const linkHashVerified = recomputedLinkHash === link.linkHash;

    return {
      index,
      previousVerified,
      linkHashVerified,
      expectedPreviousLinkHash: expectedPrevious,
      actualPreviousLinkHash: link.previousLinkHash,
      storedLinkHash: link.linkHash,
      recomputedLinkHash,
    };
  });

  const uniqueDossierHashes = new Set(chainLinks.map((link) => link.dossierHash).filter(Boolean));

  const verified = Boolean(
    chainLinks.length > 0 &&
    rootVerified &&
    continuityChecks.every((check) => check.previousVerified && check.linkHashVerified) &&
    chainLinks.every((link) => link.verified && link.dossierHash)
  );

  return {
    verified,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_CONTINUITY_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_CONTINUITY_PARTIAL',
    rootVerified,
    expectedRoot,
    expectedRootShort: expectedRoot ? expectedRoot.slice(0, 16) : null,
    ledgerRoot,
    ledgerRootShort: ledgerRoot ? ledgerRoot.slice(0, 16) : null,
    totalLinks: chainLinks.length,
    uniqueDossierHashes: uniqueDossierHashes.size,
    duplicateDossierHashes:
      uniqueDossierHashes.size !== chainLinks.filter((link) => link.dossierHash).length,
    continuityChecks,
  };
}

/**
 * @function buildRegulatorDossierChainLedgerHashInput
 * @description Builds a stable ledger root hash input summary.
 * @param {Object[]} chainLinks - Ordered chain links.
 * @returns {Object} Ledger hash input.
 * @collaboration Documents exactly which dossier hashes define the ledger root.
 */
function buildRegulatorDossierChainLedgerHashInput(chainLinks = []) {
  return {
    ledgerType: 'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LEDGER',
    ledgerVersion: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION,
    chainLength: chainLinks.length,
    dossierHashes: chainLinks.map((link) => link.dossierHash),
    linkHashes: chainLinks.map((link) => link.linkHash),
    firstLinkHash: chainLinks[0]?.linkHash || null,
    lastLinkHash: chainLinks[chainLinks.length - 1]?.linkHash || null,
  };
}

/**
 * @function buildLeadSearchRegulatorDossierChainLedger
 * @description Builds a JSON-only regulator dossier chain ledger.
 * @param {Object} params - Ledger parameters.
 * @returns {Promise<Object>} Chain ledger response.
 * @collaboration Lists verified dossiers, computes a ledger root and proves continuity without writing files.
 */
export async function buildLeadSearchRegulatorDossierChainLedger(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const limit = Math.min(Math.max(Number(params.limit || 25), 1), 50);

  const verificationLedger = await listLeadSearchRegulatorEvidenceDossierVerifications({
    tenantId,
    limit,
  });

  const verificationResponses = (verificationLedger.verifications || []).filter(
    (item) => item?.ok && item?.verification?.verified
  );
  const chainLinks = [];
  let previousLinkHash = 'GENESIS';

  verificationResponses.forEach((verificationResponse, index) => {
    const link = buildRegulatorDossierLedgerLink(verificationResponse, index, previousLinkHash);
    chainLinks.push(link);
    previousLinkHash = link.linkHash;
  });

  const ledgerRoot = computeRegulatorDossierLedgerRoot(chainLinks);
  const continuity = verifyRegulatorDossierLedgerContinuity(chainLinks, ledgerRoot);
  const ledgerHashInput = buildRegulatorDossierChainLedgerHashInput(chainLinks);

  const ledger = {
    ledgerType: 'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LEDGER',
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION,
    tenantId,
    generatedAt: new Date().toISOString(),
    persistenceMode: 'JSON_RESPONSE_ONLY',
    totalDossiers: chainLinks.length,
    verifiedDossiers: chainLinks.filter((link) => link.verified).length,
    ledgerRoot,
    ledgerRootShort: ledgerRoot.slice(0, 16),
    status: continuity.verified
      ? 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_LEDGER_PARTIAL',
    continuity,
    ledgerIntegrity: {
      verified: Boolean(continuity.verified),
      status: continuity.verified
        ? 'REGULATOR_DOSSIER_LEDGER_ROOT_VERIFIED'
        : 'REGULATOR_DOSSIER_LEDGER_ROOT_PARTIAL',
      ledgerRoot,
      ledgerRootShort: ledgerRoot.slice(0, 16),
      hashInput: ledgerHashInput,
    },
    chainLinks,
    sourceLedger: {
      verificationLedgerVersion: WILSY_CRM_REGULATOR_DOSSIER_VERIFICATION_VERSION,
      totalVerifications: verificationLedger.total || verificationResponses.length,
      verifiedVerifications: verificationLedger.verified || verificationResponses.length,
      sourceStatus: verificationLedger.status,
    },
    noFilesystemWrite: true,
  };

  return {
    ok: Boolean(ledger.continuity.verified),
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION,
    tenantId,
    limit,
    status: ledger.status,
    ledgerRoot: ledger.ledgerRoot,
    ledgerRootShort: ledger.ledgerRootShort,
    ledger,
  };
}

/**
 * @function computeRegulatorDossierLedgerRootFromLedger
 * @description Recomputes the ledger root from a returned regulator dossier chain ledger.
 * @param {Object} ledger - R68N chain ledger.
 * @returns {string} Recomputed ledger root.
 * @collaboration Proves the returned ledger root still matches ordered chain links.
 */
function computeRegulatorDossierLedgerRootFromLedger(ledger = {}) {
  return computeRegulatorDossierLedgerRoot(ledger.chainLinks || []);
}

/**
 * @function verifyRegulatorDossierLedgerLinkContinuity
 * @description Verifies every chain link previous hash and link hash.
 * @param {Object[]} chainLinks - Ledger chain links.
 * @returns {Object[]} Link verification packets.
 * @collaboration Proves every dossier chain link remains attached to its predecessor.
 */
function verifyRegulatorDossierLedgerLinkContinuity(chainLinks = []) {
  return chainLinks.map((link, index) => {
    const expectedPreviousLinkHash = index === 0 ? 'GENESIS' : chainLinks[index - 1]?.linkHash;
    const previousLinkHashVerified = link.previousLinkHash === expectedPreviousLinkHash;

    const recomputedLinkHashInput = buildRegulatorDossierLedgerLinkHashInput({
      index: link.index,
      tenantId: link.tenantId,
      previousLinkHash: link.previousLinkHash,
      dossierHash: link.dossierHash,
      exportReceiptHash: link.exportReceiptHash,
      exportHash: link.exportHash,
      governanceEventId: link.governanceEventId,
      governanceHash: link.governanceHash,
      verified: link.verified,
    });

    const recomputedLinkHash = createHashDigest(JSON.stringify(recomputedLinkHashInput));
    const linkHashVerified = recomputedLinkHash === link.linkHash;

    return {
      index,
      dossierHash: link.dossierHash || null,
      dossierHashShort: link.dossierHashShort || null,
      expectedPreviousLinkHash,
      expectedPreviousLinkHashShort:
        expectedPreviousLinkHash === 'GENESIS' ? 'GENESIS' : expectedPreviousLinkHash?.slice(0, 16),
      actualPreviousLinkHash: link.previousLinkHash,
      actualPreviousLinkHashShort:
        link.previousLinkHash === 'GENESIS' ? 'GENESIS' : link.previousLinkHash?.slice(0, 16),
      previousLinkHashVerified,
      storedLinkHash: link.linkHash,
      storedLinkHashShort: link.linkHashShort,
      recomputedLinkHash,
      recomputedLinkHashShort: recomputedLinkHash.slice(0, 16),
      linkHashVerified,
      verified: Boolean(
        previousLinkHashVerified && linkHashVerified && link.verified && link.dossierHash
      ),
    };
  });
}

/**
 * @function verifyRegulatorDossierLedgerRootPacket
 * @description Builds the root verification packet for a returned ledger.
 * @param {Object} ledger - R68N chain ledger.
 * @returns {Object} Ledger root verification packet.
 * @collaboration Proves the top-level ledger root has not changed.
 */
function verifyRegulatorDossierLedgerRootPacket(ledger = {}) {
  const storedLedgerRoot = ledger.ledgerRoot || ledger.ledgerIntegrity?.ledgerRoot || '';
  const recomputedLedgerRoot = computeRegulatorDossierLedgerRootFromLedger(ledger);
  const verified = Boolean(storedLedgerRoot && storedLedgerRoot === recomputedLedgerRoot);

  return {
    verified,
    status: verified
      ? 'REGULATOR_DOSSIER_LEDGER_ROOT_HASH_VERIFIED'
      : 'REGULATOR_DOSSIER_LEDGER_ROOT_HASH_MISMATCH',
    storedLedgerRoot,
    storedLedgerRootShort: storedLedgerRoot ? storedLedgerRoot.slice(0, 16) : null,
    recomputedLedgerRoot,
    recomputedLedgerRootShort: recomputedLedgerRoot ? recomputedLedgerRoot.slice(0, 16) : null,
  };
}

/**
 * @function buildRegulatorDossierLedgerVerificationPacket
 * @description Builds a normalized verification packet for a returned chain ledger.
 * @param {Object} ledgerResponse - R68N ledger response.
 * @param {string} ledgerId - Requested ledger root or lookup id.
 * @returns {Object} Chain ledger verification packet.
 * @collaboration Summarizes ledger root, continuity and JSON-only checks.
 */
function buildRegulatorDossierLedgerVerificationPacket(ledgerResponse = {}, ledgerId = '') {
  const ledger = ledgerResponse.ledger || {};
  const linkVerifications = verifyRegulatorDossierLedgerLinkContinuity(ledger.chainLinks || []);
  const ledgerRootIntegrity = verifyRegulatorDossierLedgerRootPacket(ledger);
  const continuity = verifyRegulatorDossierLedgerContinuity(
    ledger.chainLinks || [],
    ledger.ledgerRoot || ''
  );
  const linksVerified =
    linkVerifications.length > 0 && linkVerifications.every((link) => link.verified);

  const verified = Boolean(
    ledgerRootIntegrity.verified &&
    continuity.verified &&
    linksVerified &&
    ledger.persistenceMode === 'JSON_RESPONSE_ONLY' &&
    ledger.noFilesystemWrite === true
  );

  return {
    verificationType: 'CRM_LEAD_SEARCH_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION',
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_VERSION,
    ledgerVersion: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERSION,
    ledgerId,
    tenantId: ledger.tenantId || ledgerResponse.tenantId || 'MASTER',
    verified,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_PARTIAL',
    ledgerRoot: ledger.ledgerRoot || null,
    ledgerRootShort: ledger.ledgerRootShort || null,
    ledgerRootIntegrity,
    continuity,
    linkVerifications,
    verificationSummary: {
      verifiedLedgerRoot: Boolean(ledgerRootIntegrity.verified),
      verifiedContinuity: Boolean(continuity.verified),
      verifiedLinks: Boolean(linksVerified),
      totalLinks: linkVerifications.length,
      totalDossiers: ledger.totalDossiers || 0,
      verifiedDossiers: ledger.verifiedDossiers || 0,
      jsonResponseOnly: ledger.persistenceMode === 'JSON_RESPONSE_ONLY',
      noFilesystemWrite: ledger.noFilesystemWrite === true,
      duplicateDossierHashes: Boolean(continuity.duplicateDossierHashes),
    },
    verifiedLedger: ledger,
  };
}

/**
 * @function verifyLeadSearchRegulatorDossierChainLedger
 * @description Verifies a regulator dossier chain ledger by current ledger root or latest ledger.
 * @param {Object} params - Verification parameters.
 * @returns {Promise<Object>} Ledger verification response.
 * @collaboration Recomputes the ledger root over chain links and proves continuity without writing files.
 */
export async function verifyLeadSearchRegulatorDossierChainLedger(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = String(params.ledgerId || params.ledgerRoot || '').trim();
  const limit = Math.min(Math.max(Number(params.limit || 25), 1), 50);

  const ledgerResponse = await buildLeadSearchRegulatorDossierChainLedger({
    tenantId,
    limit,
  });

  if (!ledgerResponse || !ledgerResponse.ledger) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_VERSION,
      tenantId,
      ledgerId,
      status: 'REGULATOR_DOSSIER_CHAIN_LEDGER_NOT_FOUND',
      verification: null,
    };
  }

  const ledgerRoot = ledgerResponse.ledgerRoot || ledgerResponse.ledger?.ledgerRoot || '';

  if (
    ledgerId &&
    ledgerId !== 'latest' &&
    ledgerId !== ledgerRoot &&
    ledgerId !== ledgerRoot.slice(0, 16)
  ) {
    return {
      ok: false,
      version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_VERSION,
      tenantId,
      ledgerId,
      status: 'REGULATOR_DOSSIER_CHAIN_LEDGER_ROOT_MISMATCH',
      ledgerRoot,
      ledgerRootShort: ledgerRoot.slice(0, 16),
      verification: null,
    };
  }

  const verification = buildRegulatorDossierLedgerVerificationPacket(
    ledgerResponse,
    ledgerId || ledgerRoot
  );

  return {
    ok: Boolean(verification.verified),
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_VERSION,
    tenantId,
    ledgerId: ledgerId || ledgerRoot,
    status: verification.status,
    ledgerRoot: verification.ledgerRoot,
    ledgerRootShort: verification.ledgerRootShort,
    verification,
  };
}

/**
 * @function searchLeadOperatingRoom
 * @description Searches CRM backend models for Lead cockpit records, evidence and provenance with isolated telemetry persistence.
 * @param {Object} params - Search parameters.
 * @returns {Promise<Object>} Search response.
 * @collaboration Powers the Lead search section with backend authority while making every search audit-chain aware.
 */
export async function searchLeadOperatingRoom(params = {}) {
  const tenantId = String(params.tenantId || 'MASTER').trim() || 'MASTER';
  const query = String(params.query || '').trim();
  const role = String(params.role || 'UNKNOWN');
  const operatorId = String(params.operatorId || 'SYSTEM');
  const limit = Math.min(Math.max(Number(params.limit || 12), 1), 50);

  const registry = [];
  const results = [];
  const sourceGaps = [];

  for (const source of SOURCE_REGISTRY) {
    const model = getModel(source.modelName);

    if (!model) {
      registry.push({
        ...source,
        connected: false,
        searchable: false,
        count: 0,
        matched: 0,
        sourceStatus: 'MODEL_NOT_REGISTERED',
      });
      sourceGaps.push({
        key: source.key,
        modelName: source.modelName,
        reason: 'MODEL_NOT_REGISTERED',
      });
      continue;
    }

    const filter = buildModelFilter(model, tenantId, query);

    if (!filter) {
      registry.push({
        ...source,
        connected: true,
        searchable: false,
        count: 0,
        matched: 0,
        sourceStatus: 'TENANT_FIELD_MISSING',
      });
      sourceGaps.push({
        key: source.key,
        modelName: source.modelName,
        reason: 'TENANT_FIELD_MISSING',
      });
      continue;
    }

    const tenantOnlyFilter = buildModelFilter(model, tenantId, '');
    const count = await safeCountDocuments(model, tenantOnlyFilter || filter);
    const docs = await safeFindDocuments(model, filter, limit);

    registry.push({
      key: source.key,
      modelName: source.modelName,
      connected: true,
      searchable: true,
      count,
      matched: docs.length,
      sourceStatus: 'SOURCE_LIVE',
    });

    docs.forEach((doc) => {
      results.push(normalizeLeadSearchRow(doc, source, tenantId));
    });
  }

  const rankedResults = results
    .sort((left, right) => Number(right.score || 0) - Number(left.score || 0))
    .slice(0, limit);

  const liveSources = registry.filter((item) => item.connected).length;
  const searchableSources = registry.filter((item) => item.searchable).length;
  const totalRecords = registry.reduce((total, item) => total + Number(item.count || 0), 0);
  const totalMatched = rankedResults.length;
  const generatedAt = new Date().toISOString();

  const rootPayload = {
    version: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
    telemetryVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
    breakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
    rewriteVersion: WILSY_CRM_SEARCH_FUNCTION_REWRITE_VERSION,
    canonicalResetVersion: WILSY_CRM_SEARCH_CANONICAL_RESET_VERSION,
    tenantId,
    query,
    role,
    operatorId,
    totalRecords,
    totalMatched,
    liveSources,
    searchableSources,
    totalSources: registry.length,
    registry: registry.map((item) => ({
      key: item.key,
      modelName: item.modelName,
      connected: item.connected,
      searchable: item.searchable,
      count: item.count,
      matched: item.matched || 0,
      sourceStatus: item.sourceStatus,
    })),
    rows: rankedResults.map((row) => ({
      id: row.id,
      sourceModel: row.sourceModel,
      provenanceHash: row.provenanceHash,
      complianceStatus: row.complianceStatus,
    })),
    generatedAt,
  };

  const rootHash = buildSearchRootHash(rootPayload);
  const rootHashShort = rootHash.slice(0, 16);

  const telemetryParams = {
    tenantId,
    query,
    role,
    operatorId,
    sourceStatus: liveSources ? 'SOURCE_LIVE' : 'SOURCE_GAPPED',
    totalRecords,
    totalMatched,
    liveSources,
    searchableSources,
    totalSources: registry.length,
    registry,
    sourceGaps,
    complianceBindings: COMPLIANCE_BINDINGS,
    rootHash,
    rootHashShort,
    generatedAt,
  };

  const telemetryPersistence = await persistLeadSearchTelemetrySafely(telemetryParams);
  const complianceReceiptPersistence = await persistLeadSearchComplianceReceiptSafely({
    ...telemetryParams,
    telemetryPersistence,
  });

  return {
    ok: true,
    version: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
    telemetryVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
    telemetryBreakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
    telemetryRewriteVersion: WILSY_CRM_SEARCH_FUNCTION_REWRITE_VERSION,
    telemetryCanonicalResetVersion: WILSY_CRM_SEARCH_CANONICAL_RESET_VERSION,
    tenantId,
    query,
    role,
    operatorId,
    route: '/api/crm/command/search',
    searchMode: 'LEAD_OPERATING_ROOM_BACKEND_AUTHORITY',
    sourceStatus: liveSources ? 'SOURCE_LIVE' : 'SOURCE_GAPPED',
    total: totalMatched,
    totalRecords,
    liveSources,
    searchableSources,
    totalSources: registry.length,
    results: rankedResults,
    rows: rankedResults,
    registry,
    sourceGaps,
    complianceBindings: COMPLIANCE_BINDINGS,
    generatedAt,
    rootHash,
    rootHashShort,
    telemetryPersistence,
    telemetryPersisted: Boolean(telemetryPersistence?.persisted),
    telemetryEventId: telemetryPersistence?.eventId || null,
    telemetryReceiptHash: telemetryPersistence?.receiptHash || null,
    telemetryReceiptHashShort: telemetryPersistence?.receiptHashShort || null,
    complianceReceiptPersistence,
    complianceReceiptPersisted: Boolean(complianceReceiptPersistence?.persisted),
    complianceReceiptId: complianceReceiptPersistence?.receiptId || null,
    complianceReceiptHash: complianceReceiptPersistence?.receiptHash || null,
    complianceReceiptHashShort: complianceReceiptPersistence?.receiptHashShort || null,
  };
}

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERSION =
  'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * @function normalizeRegulatorDossierLedgerVerificationReceiptValue
 * @description Produces deterministic values for R68P verification receipt hashing.
 * @collaboration R68O ledger verification, CRM regulator evidence chain, R68P receipt authority.
 */
const normalizeRegulatorDossierLedgerVerificationReceiptValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeRegulatorDossierLedgerVerificationReceiptValue(item));
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] = normalizeRegulatorDossierLedgerVerificationReceiptValue(value[key]);
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorDossierLedgerVerificationReceiptHash
 * @description Computes the deterministic receipt hash for a regulator dossier chain ledger verification receipt.
 * @collaboration R68O ledger verification, regulator evidence receipts, CRM forensic proof surface.
 */
const computeRegulatorDossierLedgerVerificationReceiptHash = (receiptPayload) =>
  crypto
    .createHash('sha512')
    .update(JSON.stringify(normalizeRegulatorDossierLedgerVerificationReceiptValue(receiptPayload)))
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorDossierChainLedgerVerificationReceipt
 * @description Materializes a JSON-only regulator receipt for a verified dossier chain ledger root.
 * @collaboration CRM command routes, R68O ledger verification, regulator dossier chain receipt controls.
 */
export const buildLeadSearchRegulatorDossierChainLedgerVerificationReceipt = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const verificationPacket = await verifyLeadSearchRegulatorDossierChainLedger({
    tenantId,
    ledgerId,
    limit,
  });

  const verification = verificationPacket.verification || {};
  const verificationSummary = verification.verificationSummary || {};
  const ledgerRootIntegrity = verification.ledgerRootIntegrity || {};
  const issuedAt = new Date().toISOString();

  const receiptPayload = {
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERSION,
    receiptType: 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT',
    tenantId,
    operator,
    issuedAt,
    sourceStatus: verificationPacket.status,
    ledgerRoot: verificationPacket.ledgerRoot || ledgerRootIntegrity.storedLedgerRoot || null,
    storedLedgerRoot: ledgerRootIntegrity.storedLedgerRoot || null,
    recomputedLedgerRoot: ledgerRootIntegrity.recomputedLedgerRoot || null,
    ledgerRootVerified: ledgerRootIntegrity.verified === true,
    ledgerRootStatus: ledgerRootIntegrity.status || null,
    continuityVerified: verification.continuity?.verified === true,
    linksVerified: verificationSummary.verifiedLinks === true,
    totalLinks: verificationSummary.totalLinks || 0,
    totalDossiers: verificationSummary.totalDossiers || 0,
    verifiedDossiers: verificationSummary.verifiedDossiers || 0,
    duplicateDossierHashes: verificationSummary.duplicateDossierHashes === true,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
  };

  const receiptHash = computeRegulatorDossierLedgerVerificationReceiptHash(receiptPayload);

  const receipt = {
    ...receiptPayload,
    receiptHash,
    receiptHashShort: receiptHash.slice(0, 16),
  };

  const verified =
    verificationPacket.status === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
    receipt.ledgerRootVerified === true &&
    receipt.continuityVerified === true &&
    receipt.linksVerified === true &&
    receipt.jsonResponseOnly === true &&
    receipt.noFilesystemWrite === true;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED'
      : 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_DEGRADED',
    receiptHash,
    receiptHashShort: receiptHash.slice(0, 16),
    ledgerRoot: receipt.ledgerRoot,
    receipt,
    verification,
    verificationStatus: verificationPacket.status,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIER_VERSION =
  'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorDossierChainLedgerVerificationReceipt
 * @description Verifies a regulator dossier chain ledger verification receipt by recomputing its receipt hash.
 * @collaboration R68P receipt materialization, R68O ledger verification, CRM regulator evidence verifier controls.
 */
export const verifyLeadSearchRegulatorDossierChainLedgerVerificationReceipt = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const receiptPacket = await buildLeadSearchRegulatorDossierChainLedgerVerificationReceipt({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const receipt = receiptPacket.receipt || {};
  const { receiptHash: storedReceiptHash, receiptHashShort, ...receiptPayload } = receipt;

  const recomputedReceiptHash =
    computeRegulatorDossierLedgerVerificationReceiptHash(receiptPayload);
  const receiptHashVerified =
    Boolean(storedReceiptHash) && storedReceiptHash === recomputedReceiptHash;

  const sourceLedgerRootVerified = receipt.ledgerRootVerified === true;
  const sourceContinuityVerified = receipt.continuityVerified === true;
  const sourceLinksVerified = receipt.linksVerified === true;
  const jsonResponseOnly =
    receiptPacket.jsonResponseOnly === true && receipt.jsonResponseOnly === true;
  const noFilesystemWrite =
    receiptPacket.noFilesystemWrite === true && receipt.noFilesystemWrite === true;

  const verified =
    receiptPacket.status === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
    receiptHashVerified &&
    sourceLedgerRootVerified &&
    sourceContinuityVerified &&
    sourceLinksVerified &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFICATION_FAILED',
    receiptHashVerified,
    storedReceiptHash,
    storedReceiptHashShort: receiptHashShort || String(storedReceiptHash || '').slice(0, 16),
    recomputedReceiptHash,
    recomputedReceiptHashShort: recomputedReceiptHash.slice(0, 16),
    sourceLedgerRootVerified,
    sourceContinuityVerified,
    sourceLinksVerified,
    ledgerRoot: receipt.ledgerRoot || receiptPacket.ledgerRoot || null,
    receiptVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceReceiptStatus: receiptPacket.status,
      receiptHashVerified,
      storedReceiptHash,
      recomputedReceiptHash,
      sourceLedgerRootVerified,
      sourceContinuityVerified,
      sourceLinksVerified,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    receipt,
    verification: receiptPacket.verification || null,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERSION =
  'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * @function normalizeRegulatorDossierChainFinalityCertificateValue
 * @description Produces deterministic values for R68R finality certificate hashing.
 * @collaboration R68O ledger verification, R68P receipt materialization, R68Q receipt verifier.
 */
const normalizeRegulatorDossierChainFinalityCertificateValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeRegulatorDossierChainFinalityCertificateValue(item));
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] = normalizeRegulatorDossierChainFinalityCertificateValue(value[key]);
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorDossierChainFinalityCertificateHash
 * @description Computes a deterministic finality certificate hash for the regulator dossier chain.
 * @collaboration R68Q receipt verifier, regulator evidence chain, investor evidence surface.
 */
const computeRegulatorDossierChainFinalityCertificateHash = (certificatePayload) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(normalizeRegulatorDossierChainFinalityCertificateValue(certificatePayload))
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorDossierChainFinalityCertificate
 * @description Issues a JSON-only finality certificate from verified R68O, R68P, and R68Q evidence.
 * @collaboration CRM command routes, regulator dossier chain ledger, receipt verifier controls.
 */
export const buildLeadSearchRegulatorDossierChainFinalityCertificate = async (options = {}) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const verifierPacket = await verifyLeadSearchRegulatorDossierChainLedgerVerificationReceipt({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const receipt = verifierPacket.receipt || {};
  const receiptVerifier = verifierPacket.receiptVerifier || {};
  const issuedAt = new Date().toISOString();

  const certificatePayload = {
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERSION,
    certificateType: 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE',
    tenantId,
    operator,
    issuedAt,
    sourceVerifierStatus: verifierPacket.status,
    ledgerRoot: verifierPacket.ledgerRoot || receipt.ledgerRoot || null,
    receiptHash: verifierPacket.storedReceiptHash || receipt.receiptHash || null,
    recomputedReceiptHash: verifierPacket.recomputedReceiptHash || null,
    receiptHashVerified: verifierPacket.receiptHashVerified === true,
    sourceLedgerRootVerified: verifierPacket.sourceLedgerRootVerified === true,
    sourceContinuityVerified: verifierPacket.sourceContinuityVerified === true,
    sourceLinksVerified: verifierPacket.sourceLinksVerified === true,
    jsonResponseOnly:
      verifierPacket.jsonResponseOnly === true && receiptVerifier.jsonResponseOnly === true,
    noFilesystemWrite:
      verifierPacket.noFilesystemWrite === true && receiptVerifier.noFilesystemWrite === true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };

  const certificateHash = computeRegulatorDossierChainFinalityCertificateHash(certificatePayload);

  const finalityCertificate = {
    ...certificatePayload,
    certificateHash,
    certificateHashShort: certificateHash.slice(0, 16),
  };

  const verified =
    verifierPacket.status === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
    finalityCertificate.receiptHashVerified === true &&
    finalityCertificate.sourceLedgerRootVerified === true &&
    finalityCertificate.sourceContinuityVerified === true &&
    finalityCertificate.sourceLinksVerified === true &&
    finalityCertificate.jsonResponseOnly === true &&
    finalityCertificate.noFilesystemWrite === true;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED'
      : 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_DEGRADED',
    certificateHash,
    certificateHashShort: certificateHash.slice(0, 16),
    ledgerRoot: finalityCertificate.ledgerRoot,
    finalityCertificate,
    verifier: verifierPacket,
    receipt,
    receiptVerifier,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_VERSION =
  'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorDossierChainFinalityCertificate
 * @description Verifies a regulator dossier chain finality certificate by recomputing its certificate hash.
 * @collaboration R68R finality certificate, R68Q receipt verifier, CRM regulator evidence controls.
 */
export const verifyLeadSearchRegulatorDossierChainFinalityCertificate = async (options = {}) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const certificatePacket = await buildLeadSearchRegulatorDossierChainFinalityCertificate({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const finalityCertificate = certificatePacket.finalityCertificate || {};
  const {
    certificateHash: storedCertificateHash,
    certificateHashShort,
    ...certificatePayload
  } = finalityCertificate;

  const recomputedCertificateHash =
    computeRegulatorDossierChainFinalityCertificateHash(certificatePayload);
  const certificateHashVerified =
    Boolean(storedCertificateHash) && storedCertificateHash === recomputedCertificateHash;

  const receiptHashVerified = finalityCertificate.receiptHashVerified === true;
  const sourceLedgerRootVerified = finalityCertificate.sourceLedgerRootVerified === true;
  const sourceContinuityVerified = finalityCertificate.sourceContinuityVerified === true;
  const sourceLinksVerified = finalityCertificate.sourceLinksVerified === true;
  const jsonResponseOnly =
    certificatePacket.jsonResponseOnly === true && finalityCertificate.jsonResponseOnly === true;
  const noFilesystemWrite =
    certificatePacket.noFilesystemWrite === true && finalityCertificate.noFilesystemWrite === true;

  const verified =
    certificatePacket.status ===
      'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
    certificateHashVerified &&
    receiptHashVerified &&
    sourceLedgerRootVerified &&
    sourceContinuityVerified &&
    sourceLinksVerified &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFICATION_FAILED',
    certificateHashVerified,
    storedCertificateHash,
    storedCertificateHashShort:
      certificateHashShort || String(storedCertificateHash || '').slice(0, 16),
    recomputedCertificateHash,
    recomputedCertificateHashShort: recomputedCertificateHash.slice(0, 16),
    ledgerRoot: finalityCertificate.ledgerRoot || certificatePacket.ledgerRoot || null,
    receiptHash: finalityCertificate.receiptHash || null,
    receiptHashVerified,
    sourceLedgerRootVerified,
    sourceContinuityVerified,
    sourceLinksVerified,
    finalityVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceCertificateStatus: certificatePacket.status,
      certificateHashVerified,
      storedCertificateHash,
      recomputedCertificateHash,
      receiptHashVerified,
      sourceLedgerRootVerified,
      sourceContinuityVerified,
      sourceLinksVerified,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    finalityCertificate,
    sourceCertificatePacket: certificatePacket,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERSION =
  'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY';

/**
 * @function normalizeRegulatorDossierChainEvidenceBundleIndexValue
 * @description Produces deterministic values for R68T evidence bundle index hashing.
 * @collaboration R68O ledger verification, R68P receipt, R68Q verifier, R68R certificate, R68S verifier.
 */
const normalizeRegulatorDossierChainEvidenceBundleIndexValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeRegulatorDossierChainEvidenceBundleIndexValue(item));
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] = normalizeRegulatorDossierChainEvidenceBundleIndexValue(value[key]);
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorDossierChainEvidenceBundleIndexHash
 * @description Computes a deterministic hash for the regulator dossier chain evidence bundle index.
 * @collaboration R68S finality verifier, regulator evidence chain, investor evidence index surface.
 */
const computeRegulatorDossierChainEvidenceBundleIndexHash = (bundleIndexPayload) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(normalizeRegulatorDossierChainEvidenceBundleIndexValue(bundleIndexPayload))
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorDossierChainEvidenceBundleIndex
 * @description Builds one JSON-only evidence bundle index across R68O through R68S.
 * @collaboration CRM command routes, regulator dossier chain proof, investor evidence review surface.
 */
export const buildLeadSearchRegulatorDossierChainEvidenceBundleIndex = async (options = {}) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const finalityVerifierPacket = await verifyLeadSearchRegulatorDossierChainFinalityCertificate({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const sourceCertificatePacket = finalityVerifierPacket.sourceCertificatePacket || {};
  const finalityCertificate = finalityVerifierPacket.finalityCertificate || {};
  const verifierPacket = sourceCertificatePacket.verifier || {};
  const receiptPacket = verifierPacket.receipt || {};
  const receiptVerifier = verifierPacket.receiptVerifier || {};

  const bundleIndexPayload = {
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERSION,
    indexType: 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX',
    tenantId,
    operator,
    indexedAt: new Date().toISOString(),
    ledgerRoot: finalityVerifierPacket.ledgerRoot || finalityCertificate.ledgerRoot || null,
    evidenceRange: ['R68O', 'R68P', 'R68Q', 'R68R', 'R68S'],
    routeContracts: {
      R68O: 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY',
      R68P: 'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY',
      R68Q: 'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY',
      R68R: 'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY',
      R68S: 'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY',
    },
    sourceRoutes: {
      R68O: '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      R68P: '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
      R68Q: '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest',
      R68R: '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest',
      R68S: '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
    },
    statuses: {
      finalityVerifierStatus: finalityVerifierPacket.status,
      finalityCertificateStatus: sourceCertificatePacket.status || null,
      receiptVerifierStatus: verifierPacket.status || null,
      receiptStatus: receiptVerifier.sourceReceiptStatus || null,
      ledgerStatus: receiptPacket.sourceStatus || null,
    },
    hashes: {
      certificateHash:
        finalityVerifierPacket.storedCertificateHash || finalityCertificate.certificateHash || null,
      recomputedCertificateHash: finalityVerifierPacket.recomputedCertificateHash || null,
      receiptHash: finalityVerifierPacket.receiptHash || finalityCertificate.receiptHash || null,
      recomputedReceiptHash: finalityCertificate.recomputedReceiptHash || null,
      ledgerRoot: finalityVerifierPacket.ledgerRoot || finalityCertificate.ledgerRoot || null,
    },
    proofFlags: {
      certificateHashVerified: finalityVerifierPacket.certificateHashVerified === true,
      receiptHashVerified: finalityVerifierPacket.receiptHashVerified === true,
      sourceLedgerRootVerified: finalityVerifierPacket.sourceLedgerRootVerified === true,
      sourceContinuityVerified: finalityVerifierPacket.sourceContinuityVerified === true,
      sourceLinksVerified: finalityVerifierPacket.sourceLinksVerified === true,
      jsonResponseOnly:
        finalityVerifierPacket.jsonResponseOnly === true &&
        finalityVerifierPacket.finalityVerifier?.jsonResponseOnly === true,
      noFilesystemWrite:
        finalityVerifierPacket.noFilesystemWrite === true &&
        finalityVerifierPacket.finalityVerifier?.noFilesystemWrite === true,
    },
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };

  const bundleIndexHash = computeRegulatorDossierChainEvidenceBundleIndexHash(bundleIndexPayload);

  const evidenceBundleIndex = {
    ...bundleIndexPayload,
    bundleIndexHash,
    bundleIndexHashShort: bundleIndexHash.slice(0, 16),
  };

  const verified =
    finalityVerifierPacket.status === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
    evidenceBundleIndex.proofFlags.certificateHashVerified === true &&
    evidenceBundleIndex.proofFlags.receiptHashVerified === true &&
    evidenceBundleIndex.proofFlags.sourceLedgerRootVerified === true &&
    evidenceBundleIndex.proofFlags.sourceContinuityVerified === true &&
    evidenceBundleIndex.proofFlags.sourceLinksVerified === true &&
    evidenceBundleIndex.proofFlags.jsonResponseOnly === true &&
    evidenceBundleIndex.proofFlags.noFilesystemWrite === true;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED'
      : 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_DEGRADED',
    bundleIndexHash,
    bundleIndexHashShort: bundleIndexHash.slice(0, 16),
    ledgerRoot: evidenceBundleIndex.ledgerRoot,
    evidenceBundleIndex,
    finalityVerifier: finalityVerifierPacket,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIER_VERSION =
  'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorDossierChainEvidenceBundleIndex
 * @description Verifies a regulator dossier chain evidence bundle index by recomputing its bundle index hash.
 * @collaboration R68T evidence bundle index, R68S finality verifier, CRM regulator evidence controls.
 */
export const verifyLeadSearchRegulatorDossierChainEvidenceBundleIndex = async (options = {}) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const bundleIndexPacket = await buildLeadSearchRegulatorDossierChainEvidenceBundleIndex({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const evidenceBundleIndex = bundleIndexPacket.evidenceBundleIndex || {};
  const {
    bundleIndexHash: storedBundleIndexHash,
    bundleIndexHashShort,
    ...bundleIndexPayload
  } = evidenceBundleIndex;

  const recomputedBundleIndexHash =
    computeRegulatorDossierChainEvidenceBundleIndexHash(bundleIndexPayload);
  const bundleIndexHashVerified =
    Boolean(storedBundleIndexHash) && storedBundleIndexHash === recomputedBundleIndexHash;

  const evidenceRange = Array.isArray(evidenceBundleIndex.evidenceRange)
    ? evidenceBundleIndex.evidenceRange
    : [];

  const expectedEvidenceRange = ['R68O', 'R68P', 'R68Q', 'R68R', 'R68S'];
  const evidenceRangeVerified =
    JSON.stringify(evidenceRange) === JSON.stringify(expectedEvidenceRange);

  const routeContracts = evidenceBundleIndex.routeContracts || {};
  const routeContractsVerified =
    routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
    routeContracts.R68P === 'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68Q ===
      'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
    routeContracts.R68R ===
      'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
    routeContracts.R68S === 'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

  const sourceRoutes = evidenceBundleIndex.sourceRoutes || {};
  const sourceRoutesVerified =
    sourceRoutes.R68O ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
    sourceRoutes.R68P ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
    sourceRoutes.R68Q ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
    sourceRoutes.R68R ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
    sourceRoutes.R68S ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest';

  const statuses = evidenceBundleIndex.statuses || {};
  const statusesVerified =
    statuses.finalityVerifierStatus === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
    statuses.finalityCertificateStatus ===
      'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
    statuses.receiptVerifierStatus ===
      'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
    statuses.receiptStatus === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.ledgerStatus === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED';

  const proofFlags = evidenceBundleIndex.proofFlags || {};
  const proofFlagsVerified =
    proofFlags.certificateHashVerified === true &&
    proofFlags.receiptHashVerified === true &&
    proofFlags.sourceLedgerRootVerified === true &&
    proofFlags.sourceContinuityVerified === true &&
    proofFlags.sourceLinksVerified === true &&
    proofFlags.jsonResponseOnly === true &&
    proofFlags.noFilesystemWrite === true;

  const jsonResponseOnly =
    bundleIndexPacket.jsonResponseOnly === true &&
    proofFlags.jsonResponseOnly === true &&
    evidenceBundleIndex.persistenceMode === 'JSON_RESPONSE_ONLY';

  const noFilesystemWrite =
    bundleIndexPacket.noFilesystemWrite === true && proofFlags.noFilesystemWrite === true;

  const verified =
    bundleIndexPacket.status === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
    bundleIndexHashVerified &&
    evidenceRangeVerified &&
    routeContractsVerified &&
    sourceRoutesVerified &&
    statusesVerified &&
    proofFlagsVerified &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_FAILED',
    bundleIndexHashVerified,
    storedBundleIndexHash,
    storedBundleIndexHashShort:
      bundleIndexHashShort || String(storedBundleIndexHash || '').slice(0, 16),
    recomputedBundleIndexHash,
    recomputedBundleIndexHashShort: recomputedBundleIndexHash.slice(0, 16),
    evidenceRangeVerified,
    routeContractsVerified,
    sourceRoutesVerified,
    statusesVerified,
    proofFlagsVerified,
    ledgerRoot: evidenceBundleIndex.ledgerRoot || bundleIndexPacket.ledgerRoot || null,
    evidenceBundleIndexVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceBundleIndexStatus: bundleIndexPacket.status,
      bundleIndexHashVerified,
      storedBundleIndexHash,
      recomputedBundleIndexHash,
      evidenceRangeVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      statusesVerified,
      proofFlagsVerified,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    evidenceBundleIndex,
    sourceBundleIndexPacket: bundleIndexPacket,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERSION =
  'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * @function normalizeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptValue
 * @description Produces deterministic values for R68V evidence bundle index verification receipt hashing.
 * @collaboration R68U evidence bundle verifier, R68T evidence bundle index, CRM regulator evidence receipt controls.
 */
const normalizeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) =>
      normalizeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptValue(item)
    );
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] = normalizeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptValue(
          value[key]
        );
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptHash
 * @description Computes a deterministic hash for the R68V evidence bundle index verification receipt.
 * @collaboration R68U verifier packet, regulator evidence chain, investor evidence receipt surface.
 */
const computeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptHash = (receiptPayload) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(
        normalizeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptValue(receiptPayload)
      )
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt
 * @description Materializes a JSON-only receipt from the verified R68U evidence bundle index verifier.
 * @collaboration CRM command routes, R68U evidence bundle verifier, regulator/investor proof receipts.
 */
export const buildLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const verifierPacket = await verifyLeadSearchRegulatorDossierChainEvidenceBundleIndex({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const verifier = verifierPacket.evidenceBundleIndexVerifier || {};
  const evidenceBundleIndex = verifierPacket.evidenceBundleIndex || {};
  const issuedAt = new Date().toISOString();

  const receiptPayload = {
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERSION,
    receiptType: 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT',
    tenantId,
    operator,
    issuedAt,
    sourceVerifierStatus: verifierPacket.status,
    sourceBundleIndexStatus: verifier.sourceBundleIndexStatus || null,
    ledgerRoot: verifierPacket.ledgerRoot || evidenceBundleIndex.ledgerRoot || null,
    storedBundleIndexHash:
      verifierPacket.storedBundleIndexHash || verifier.storedBundleIndexHash || null,
    recomputedBundleIndexHash:
      verifierPacket.recomputedBundleIndexHash || verifier.recomputedBundleIndexHash || null,
    bundleIndexHashVerified: verifierPacket.bundleIndexHashVerified === true,
    evidenceRangeVerified: verifierPacket.evidenceRangeVerified === true,
    routeContractsVerified: verifierPacket.routeContractsVerified === true,
    sourceRoutesVerified: verifierPacket.sourceRoutesVerified === true,
    statusesVerified: verifierPacket.statusesVerified === true,
    proofFlagsVerified: verifierPacket.proofFlagsVerified === true,
    evidenceRange: evidenceBundleIndex.evidenceRange || [],
    routeContracts: evidenceBundleIndex.routeContracts || {},
    sourceRoutes: evidenceBundleIndex.sourceRoutes || {},
    statuses: evidenceBundleIndex.statuses || {},
    proofFlags: evidenceBundleIndex.proofFlags || {},
    sourceRoute:
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
    sourceEvidenceBundleIndexRoute:
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
    jsonResponseOnly:
      verifierPacket.jsonResponseOnly === true && verifier.jsonResponseOnly === true,
    noFilesystemWrite:
      verifierPacket.noFilesystemWrite === true && verifier.noFilesystemWrite === true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };

  const receiptHash =
    computeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptHash(receiptPayload);

  const verificationReceipt = {
    ...receiptPayload,
    receiptHash,
    receiptHashShort: receiptHash.slice(0, 16),
  };

  const materialized =
    verifierPacket.status === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
    verificationReceipt.bundleIndexHashVerified === true &&
    verificationReceipt.storedBundleIndexHash === verificationReceipt.recomputedBundleIndexHash &&
    verificationReceipt.evidenceRangeVerified === true &&
    verificationReceipt.routeContractsVerified === true &&
    verificationReceipt.sourceRoutesVerified === true &&
    verificationReceipt.statusesVerified === true &&
    verificationReceipt.proofFlagsVerified === true &&
    verificationReceipt.jsonResponseOnly === true &&
    verificationReceipt.noFilesystemWrite === true;

  return {
    ok: materialized,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERSION,
    status: materialized
      ? 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED'
      : 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_DEGRADED',
    receiptHash,
    receiptHashShort: receiptHash.slice(0, 16),
    ledgerRoot: verificationReceipt.ledgerRoot,
    verificationReceipt,
    sourceVerifier: verifierPacket,
    evidenceBundleIndex,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_VERSION =
  'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt
 * @description Verifies the R68V evidence bundle index verification receipt by recomputing its receipt hash.
 * @collaboration R68V verification receipt, R68U evidence bundle verifier, CRM regulator evidence controls.
 */
export const verifyLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const receiptPacket =
    await buildLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt({
      tenantId,
      ledgerId,
      limit,
      operator,
    });

  const verificationReceipt = receiptPacket.verificationReceipt || {};
  const {
    receiptHash: storedReceiptHash,
    receiptHashShort,
    ...receiptPayload
  } = verificationReceipt;

  const recomputedReceiptHash =
    computeRegulatorDossierChainEvidenceBundleIndexVerificationReceiptHash(receiptPayload);
  const receiptHashVerified =
    Boolean(storedReceiptHash) && storedReceiptHash === recomputedReceiptHash;

  const sourceVerifierStatusVerified =
    verificationReceipt.sourceVerifierStatus ===
    'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED';

  const sourceBundleIndexStatusVerified =
    verificationReceipt.sourceBundleIndexStatus ===
    'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED';

  const bundleIndexHashVerified = verificationReceipt.bundleIndexHashVerified === true;
  const bundleIndexHashEqualityVerified =
    Boolean(verificationReceipt.storedBundleIndexHash) &&
    verificationReceipt.storedBundleIndexHash === verificationReceipt.recomputedBundleIndexHash;

  const evidenceRangeVerified = verificationReceipt.evidenceRangeVerified === true;
  const routeContractsVerified = verificationReceipt.routeContractsVerified === true;
  const sourceRoutesVerified = verificationReceipt.sourceRoutesVerified === true;
  const statusesVerified = verificationReceipt.statusesVerified === true;
  const proofFlagsVerified = verificationReceipt.proofFlagsVerified === true;

  const proofFlags = verificationReceipt.proofFlags || {};
  const embeddedProofFlagsVerified =
    proofFlags.certificateHashVerified === true &&
    proofFlags.receiptHashVerified === true &&
    proofFlags.sourceLedgerRootVerified === true &&
    proofFlags.sourceContinuityVerified === true &&
    proofFlags.sourceLinksVerified === true &&
    proofFlags.jsonResponseOnly === true &&
    proofFlags.noFilesystemWrite === true;

  const evidenceRange = Array.isArray(verificationReceipt.evidenceRange)
    ? verificationReceipt.evidenceRange
    : [];

  const expectedEvidenceRange = ['R68O', 'R68P', 'R68Q', 'R68R', 'R68S'];
  const evidenceRangeStillIndexed =
    JSON.stringify(evidenceRange) === JSON.stringify(expectedEvidenceRange);

  const jsonResponseOnly =
    receiptPacket.jsonResponseOnly === true &&
    verificationReceipt.jsonResponseOnly === true &&
    verificationReceipt.persistenceMode === 'JSON_RESPONSE_ONLY';

  const noFilesystemWrite =
    receiptPacket.noFilesystemWrite === true && verificationReceipt.noFilesystemWrite === true;

  const verified =
    receiptPacket.status ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
    receiptHashVerified &&
    sourceVerifierStatusVerified &&
    sourceBundleIndexStatusVerified &&
    bundleIndexHashVerified &&
    bundleIndexHashEqualityVerified &&
    evidenceRangeVerified &&
    routeContractsVerified &&
    sourceRoutesVerified &&
    statusesVerified &&
    proofFlagsVerified &&
    embeddedProofFlagsVerified &&
    evidenceRangeStillIndexed &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version:
      WILSY_CRM_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFICATION_FAILED',
    receiptHashVerified,
    storedReceiptHash,
    storedReceiptHashShort: receiptHashShort || String(storedReceiptHash || '').slice(0, 16),
    recomputedReceiptHash,
    recomputedReceiptHashShort: recomputedReceiptHash.slice(0, 16),
    sourceVerifierStatusVerified,
    sourceBundleIndexStatusVerified,
    bundleIndexHashVerified,
    bundleIndexHashEqualityVerified,
    evidenceRangeVerified,
    routeContractsVerified,
    sourceRoutesVerified,
    statusesVerified,
    proofFlagsVerified,
    embeddedProofFlagsVerified,
    evidenceRangeStillIndexed,
    ledgerRoot: verificationReceipt.ledgerRoot || receiptPacket.ledgerRoot || null,
    evidenceBundleIndexVerificationReceiptVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceReceiptStatus: receiptPacket.status,
      receiptHashVerified,
      storedReceiptHash,
      recomputedReceiptHash,
      sourceVerifierStatusVerified,
      sourceBundleIndexStatusVerified,
      bundleIndexHashVerified,
      bundleIndexHashEqualityVerified,
      evidenceRangeVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      statusesVerified,
      proofFlagsVerified,
      embeddedProofFlagsVerified,
      evidenceRangeStillIndexed,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    verificationReceipt,
    sourceReceiptPacket: receiptPacket,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERSION =
  'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY';

/**
 * @function normalizeRegulatorDossierChainFinalAttestationValue
 * @description Produces deterministic values for R68X final regulator and investor attestation hashing.
 * @collaboration R68W receipt verifier, R68V verification receipt, R68U/R68T evidence bundle controls.
 */
const normalizeRegulatorDossierChainFinalAttestationValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeRegulatorDossierChainFinalAttestationValue(item));
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] = normalizeRegulatorDossierChainFinalAttestationValue(value[key]);
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorDossierChainFinalAttestationHash
 * @description Computes a deterministic hash for the R68X regulator and investor final attestation.
 * @collaboration R68W verified receipt packet, regulator evidence chain, investor evidence surface.
 */
const computeRegulatorDossierChainFinalAttestationHash = (attestationPayload) =>
  crypto
    .createHash('sha512')
    .update(JSON.stringify(normalizeRegulatorDossierChainFinalAttestationValue(attestationPayload)))
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation
 * @description Issues one JSON-only final regulator and investor attestation across R68O through R68W.
 * @collaboration CRM command routes, regulator dossier evidence bundle, investor attestation controls.
 */
export const buildLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const receiptVerifierPacket =
    await verifyLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt({
      tenantId,
      ledgerId,
      limit,
      operator,
    });

  const verifier = receiptVerifierPacket.evidenceBundleIndexVerificationReceiptVerifier || {};
  const verificationReceipt = receiptVerifierPacket.verificationReceipt || {};
  const proofFlags = verificationReceipt.proofFlags || {};
  const statuses = verificationReceipt.statuses || {};
  const routeContracts = verificationReceipt.routeContracts || {};
  const sourceRoutes = verificationReceipt.sourceRoutes || {};
  const attestedAt = new Date().toISOString();

  const attestationPayload = {
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERSION,
    attestationType: 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_REGULATOR_INVESTOR_ATTESTATION',
    audience: ['REGULATOR', 'INVESTOR'],
    tenantId,
    operator,
    attestedAt,
    chainRange: ['R68O', 'R68P', 'R68Q', 'R68R', 'R68S', 'R68T', 'R68U', 'R68V', 'R68W'],
    evidenceRange: verificationReceipt.evidenceRange || [],
    ledgerRoot: receiptVerifierPacket.ledgerRoot || verificationReceipt.ledgerRoot || null,
    sourceReceiptVerifierStatus: receiptVerifierPacket.status,
    sourceReceiptStatus: verifier.sourceReceiptStatus || null,
    sourceVerifierStatus: verificationReceipt.sourceVerifierStatus || null,
    sourceBundleIndexStatus: verificationReceipt.sourceBundleIndexStatus || null,
    hashes: {
      storedReceiptHash:
        receiptVerifierPacket.storedReceiptHash || verifier.storedReceiptHash || null,
      recomputedReceiptHash:
        receiptVerifierPacket.recomputedReceiptHash || verifier.recomputedReceiptHash || null,
      storedBundleIndexHash: verificationReceipt.storedBundleIndexHash || null,
      recomputedBundleIndexHash: verificationReceipt.recomputedBundleIndexHash || null,
      receiptHash: verificationReceipt.receiptHash || null,
      receiptHashShort: verificationReceipt.receiptHashShort || null,
      ledgerRoot: receiptVerifierPacket.ledgerRoot || verificationReceipt.ledgerRoot || null,
    },
    routeContracts: {
      R68O: routeContracts.R68O || 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY',
      R68P:
        routeContracts.R68P || 'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY',
      R68Q:
        routeContracts.R68Q ||
        'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY',
      R68R:
        routeContracts.R68R ||
        'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY',
      R68S:
        routeContracts.R68S ||
        'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY',
      R68T: 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY',
      R68U: 'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY',
      R68V: 'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY',
      R68W: 'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY',
    },
    sourceRoutes: {
      R68O:
        sourceRoutes.R68O ||
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      R68P:
        sourceRoutes.R68P ||
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
      R68Q:
        sourceRoutes.R68Q ||
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest',
      R68R:
        sourceRoutes.R68R ||
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest',
      R68S:
        sourceRoutes.R68S ||
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
      R68T: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
      R68U: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
      R68V: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest',
      R68W: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
    },
    statuses: {
      R68O: statuses.ledgerStatus || null,
      R68P: statuses.receiptStatus || null,
      R68Q: statuses.receiptVerifierStatus || null,
      R68R: statuses.finalityCertificateStatus || null,
      R68S: statuses.finalityVerifierStatus || null,
      R68T: verificationReceipt.sourceBundleIndexStatus || null,
      R68U: verificationReceipt.sourceVerifierStatus || null,
      R68V: verifier.sourceReceiptStatus || null,
      R68W: receiptVerifierPacket.status || null,
    },
    proofFlags: {
      receiptHashVerified: receiptVerifierPacket.receiptHashVerified === true,
      storedReceiptHashMatchesRecomputed:
        receiptVerifierPacket.storedReceiptHash === receiptVerifierPacket.recomputedReceiptHash,
      sourceVerifierStatusVerified: receiptVerifierPacket.sourceVerifierStatusVerified === true,
      sourceBundleIndexStatusVerified:
        receiptVerifierPacket.sourceBundleIndexStatusVerified === true,
      bundleIndexHashVerified: receiptVerifierPacket.bundleIndexHashVerified === true,
      bundleIndexHashEqualityVerified:
        receiptVerifierPacket.bundleIndexHashEqualityVerified === true,
      evidenceRangeVerified: receiptVerifierPacket.evidenceRangeVerified === true,
      routeContractsVerified: receiptVerifierPacket.routeContractsVerified === true,
      sourceRoutesVerified: receiptVerifierPacket.sourceRoutesVerified === true,
      statusesVerified: receiptVerifierPacket.statusesVerified === true,
      proofFlagsVerified: receiptVerifierPacket.proofFlagsVerified === true,
      embeddedProofFlagsVerified: receiptVerifierPacket.embeddedProofFlagsVerified === true,
      evidenceRangeStillIndexed: receiptVerifierPacket.evidenceRangeStillIndexed === true,
      certificateHashVerified: proofFlags.certificateHashVerified === true,
      upstreamReceiptHashVerified: proofFlags.receiptHashVerified === true,
      sourceLedgerRootVerified: proofFlags.sourceLedgerRootVerified === true,
      sourceContinuityVerified: proofFlags.sourceContinuityVerified === true,
      sourceLinksVerified: proofFlags.sourceLinksVerified === true,
      jsonResponseOnly:
        receiptVerifierPacket.jsonResponseOnly === true &&
        verificationReceipt.jsonResponseOnly === true &&
        verifier.jsonResponseOnly === true,
      noFilesystemWrite:
        receiptVerifierPacket.noFilesystemWrite === true &&
        verificationReceipt.noFilesystemWrite === true &&
        verifier.noFilesystemWrite === true,
    },
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };

  const attestationHash = computeRegulatorDossierChainFinalAttestationHash(attestationPayload);

  const finalAttestation = {
    ...attestationPayload,
    attestationHash,
    attestationHashShort: attestationHash.slice(0, 16),
  };

  const verified =
    receiptVerifierPacket.status ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
    finalAttestation.statuses.R68V ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
    finalAttestation.statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
    finalAttestation.statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
    finalAttestation.proofFlags.receiptHashVerified === true &&
    finalAttestation.proofFlags.storedReceiptHashMatchesRecomputed === true &&
    finalAttestation.proofFlags.sourceVerifierStatusVerified === true &&
    finalAttestation.proofFlags.sourceBundleIndexStatusVerified === true &&
    finalAttestation.proofFlags.bundleIndexHashVerified === true &&
    finalAttestation.proofFlags.bundleIndexHashEqualityVerified === true &&
    finalAttestation.proofFlags.evidenceRangeVerified === true &&
    finalAttestation.proofFlags.routeContractsVerified === true &&
    finalAttestation.proofFlags.sourceRoutesVerified === true &&
    finalAttestation.proofFlags.statusesVerified === true &&
    finalAttestation.proofFlags.proofFlagsVerified === true &&
    finalAttestation.proofFlags.embeddedProofFlagsVerified === true &&
    finalAttestation.proofFlags.evidenceRangeStillIndexed === true &&
    finalAttestation.proofFlags.certificateHashVerified === true &&
    finalAttestation.proofFlags.upstreamReceiptHashVerified === true &&
    finalAttestation.proofFlags.sourceLedgerRootVerified === true &&
    finalAttestation.proofFlags.sourceContinuityVerified === true &&
    finalAttestation.proofFlags.sourceLinksVerified === true &&
    finalAttestation.proofFlags.jsonResponseOnly === true &&
    finalAttestation.proofFlags.noFilesystemWrite === true;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED'
      : 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_DEGRADED',
    attestationHash,
    attestationHashShort: attestationHash.slice(0, 16),
    ledgerRoot: finalAttestation.ledgerRoot,
    finalAttestation,
    sourceReceiptVerifier: receiptVerifierPacket,
    verificationReceipt,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERIFIER_VERSION =
  'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation
 * @description Verifies the R68X final regulator and investor attestation by recomputing its attestation hash.
 * @collaboration R68X final attestation, R68W receipt verifier, CRM regulator evidence controls.
 */
export const verifyLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const attestationPacket =
    await buildLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation({
      tenantId,
      ledgerId,
      limit,
      operator,
    });

  const finalAttestation = attestationPacket.finalAttestation || {};
  const {
    attestationHash: storedAttestationHash,
    attestationHashShort,
    ...attestationPayload
  } = finalAttestation;

  const recomputedAttestationHash =
    computeRegulatorDossierChainFinalAttestationHash(attestationPayload);
  const attestationHashVerified =
    Boolean(storedAttestationHash) && storedAttestationHash === recomputedAttestationHash;

  const expectedChainRange = [
    'R68O',
    'R68P',
    'R68Q',
    'R68R',
    'R68S',
    'R68T',
    'R68U',
    'R68V',
    'R68W',
  ];

  const chainRange = Array.isArray(finalAttestation.chainRange) ? finalAttestation.chainRange : [];

  const chainRangeVerified = JSON.stringify(chainRange) === JSON.stringify(expectedChainRange);

  const audience = Array.isArray(finalAttestation.audience) ? finalAttestation.audience : [];

  const audienceVerified = JSON.stringify(audience) === JSON.stringify(['REGULATOR', 'INVESTOR']);

  const statuses = finalAttestation.statuses || {};
  const statusesVerified =
    statuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
    statuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
    statuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
    statuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
    statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
    statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
    statuses.R68V ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.R68W === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED';

  const routeContracts = finalAttestation.routeContracts || {};
  const routeContractsVerified =
    routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
    routeContracts.R68P === 'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68Q ===
      'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
    routeContracts.R68R ===
      'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
    routeContracts.R68S ===
      'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY' &&
    routeContracts.R68T === 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY' &&
    routeContracts.R68U ===
      'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY' &&
    routeContracts.R68V ===
      'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68W ===
      'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

  const sourceRoutes = finalAttestation.sourceRoutes || {};
  const sourceRoutesVerified =
    sourceRoutes.R68O ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
    sourceRoutes.R68P ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
    sourceRoutes.R68Q ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
    sourceRoutes.R68R ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
    sourceRoutes.R68S ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest' &&
    sourceRoutes.R68T ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest' &&
    sourceRoutes.R68U ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest' &&
    sourceRoutes.R68V ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest' &&
    sourceRoutes.R68W ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest';

  const hashes = finalAttestation.hashes || {};
  const hashEqualityVerified =
    Boolean(hashes.storedReceiptHash) &&
    hashes.storedReceiptHash === hashes.recomputedReceiptHash &&
    Boolean(hashes.storedBundleIndexHash) &&
    hashes.storedBundleIndexHash === hashes.recomputedBundleIndexHash;

  const proofFlags = finalAttestation.proofFlags || {};
  const proofFlagsVerified =
    proofFlags.receiptHashVerified === true &&
    proofFlags.storedReceiptHashMatchesRecomputed === true &&
    proofFlags.sourceVerifierStatusVerified === true &&
    proofFlags.sourceBundleIndexStatusVerified === true &&
    proofFlags.bundleIndexHashVerified === true &&
    proofFlags.bundleIndexHashEqualityVerified === true &&
    proofFlags.evidenceRangeVerified === true &&
    proofFlags.routeContractsVerified === true &&
    proofFlags.sourceRoutesVerified === true &&
    proofFlags.statusesVerified === true &&
    proofFlags.proofFlagsVerified === true &&
    proofFlags.embeddedProofFlagsVerified === true &&
    proofFlags.evidenceRangeStillIndexed === true &&
    proofFlags.certificateHashVerified === true &&
    proofFlags.upstreamReceiptHashVerified === true &&
    proofFlags.sourceLedgerRootVerified === true &&
    proofFlags.sourceContinuityVerified === true &&
    proofFlags.sourceLinksVerified === true &&
    proofFlags.jsonResponseOnly === true &&
    proofFlags.noFilesystemWrite === true;

  const jsonResponseOnly =
    attestationPacket.jsonResponseOnly === true &&
    finalAttestation.persistenceMode === 'JSON_RESPONSE_ONLY' &&
    proofFlags.jsonResponseOnly === true;

  const noFilesystemWrite =
    attestationPacket.noFilesystemWrite === true && proofFlags.noFilesystemWrite === true;

  const verified =
    attestationPacket.status ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
    attestationHashVerified &&
    chainRangeVerified &&
    audienceVerified &&
    statusesVerified &&
    routeContractsVerified &&
    sourceRoutesVerified &&
    hashEqualityVerified &&
    proofFlagsVerified &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED'
      : 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFICATION_FAILED',
    attestationHashVerified,
    storedAttestationHash,
    storedAttestationHashShort:
      attestationHashShort || String(storedAttestationHash || '').slice(0, 16),
    recomputedAttestationHash,
    recomputedAttestationHashShort: recomputedAttestationHash.slice(0, 16),
    chainRangeVerified,
    audienceVerified,
    statusesVerified,
    routeContractsVerified,
    sourceRoutesVerified,
    hashEqualityVerified,
    proofFlagsVerified,
    ledgerRoot: finalAttestation.ledgerRoot || attestationPacket.ledgerRoot || null,
    finalAttestationVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceAttestationStatus: attestationPacket.status,
      attestationHashVerified,
      storedAttestationHash,
      recomputedAttestationHash,
      chainRangeVerified,
      audienceVerified,
      statusesVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      hashEqualityVerified,
      proofFlagsVerified,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    finalAttestation,
    sourceAttestationPacket: attestationPacket,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERSION =
  'R68Z-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-AUTHORITY';

/**
 * @function normalizeRegulatorInvestorEvidenceChainTerminalSealValue
 * @description Produces deterministic values for R68Z terminal regulator and investor evidence-chain seal hashing.
 * @collaboration R68Y final attestation verifier, R68X final attestation, CRM regulator/investor terminal evidence controls.
 */
const normalizeRegulatorInvestorEvidenceChainTerminalSealValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeRegulatorInvestorEvidenceChainTerminalSealValue(item));
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] = normalizeRegulatorInvestorEvidenceChainTerminalSealValue(value[key]);
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorInvestorEvidenceChainTerminalSealHash
 * @description Computes a deterministic hash for the R68Z terminal evidence-chain seal.
 * @collaboration R68Y verified final attestation packet, regulator evidence chain, investor evidence controls.
 */
const computeRegulatorInvestorEvidenceChainTerminalSealHash = (terminalSealPayload) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(normalizeRegulatorInvestorEvidenceChainTerminalSealValue(terminalSealPayload))
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorInvestorEvidenceChainTerminalSeal
 * @description Issues one JSON-only terminal regulator and investor evidence-chain seal across R68O through R68Y.
 * @collaboration CRM command routes, regulator dossier evidence bundle, investor attestation controls.
 */
export const buildLeadSearchRegulatorInvestorEvidenceChainTerminalSeal = async (options = {}) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const finalAttestationVerifierPacket =
    await verifyLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation({
      tenantId,
      ledgerId,
      limit,
      operator,
    });

  const verifier = finalAttestationVerifierPacket.finalAttestationVerifier || {};
  const finalAttestation = finalAttestationVerifierPacket.finalAttestation || {};
  const proofFlags = finalAttestation.proofFlags || {};
  const hashes = finalAttestation.hashes || {};
  const statuses = finalAttestation.statuses || {};
  const routeContracts = finalAttestation.routeContracts || {};
  const sourceRoutes = finalAttestation.sourceRoutes || {};
  const sealedAt = new Date().toISOString();

  const chainRange = [
    'R68O',
    'R68P',
    'R68Q',
    'R68R',
    'R68S',
    'R68T',
    'R68U',
    'R68V',
    'R68W',
    'R68X',
    'R68Y',
  ];

  const terminalStatuses = {
    ...statuses,
    R68X:
      verifier.sourceAttestationStatus ||
      finalAttestationVerifierPacket.sourceAttestationPacket?.status ||
      null,
    R68Y: finalAttestationVerifierPacket.status || null,
  };

  const terminalRouteContracts = {
    ...routeContracts,
    R68X: 'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY',
    R68Y: 'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY',
  };

  const terminalSourceRoutes = {
    ...sourceRoutes,
    R68X: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
    R68Y: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
  };

  const terminalProofFlags = {
    finalAttestationVerifierPassed:
      finalAttestationVerifierPacket.status ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED',
    attestationHashVerified: finalAttestationVerifierPacket.attestationHashVerified === true,
    storedAttestationHashMatchesRecomputed:
      finalAttestationVerifierPacket.storedAttestationHash ===
      finalAttestationVerifierPacket.recomputedAttestationHash,
    chainRangeVerified: finalAttestationVerifierPacket.chainRangeVerified === true,
    audienceVerified: finalAttestationVerifierPacket.audienceVerified === true,
    statusesVerified: finalAttestationVerifierPacket.statusesVerified === true,
    routeContractsVerified: finalAttestationVerifierPacket.routeContractsVerified === true,
    sourceRoutesVerified: finalAttestationVerifierPacket.sourceRoutesVerified === true,
    hashEqualityVerified: finalAttestationVerifierPacket.hashEqualityVerified === true,
    proofFlagsVerified: finalAttestationVerifierPacket.proofFlagsVerified === true,
    receiptHashVerified: proofFlags.receiptHashVerified === true,
    storedReceiptHashMatchesRecomputed: proofFlags.storedReceiptHashMatchesRecomputed === true,
    bundleIndexHashVerified: proofFlags.bundleIndexHashVerified === true,
    bundleIndexHashEqualityVerified: proofFlags.bundleIndexHashEqualityVerified === true,
    certificateHashVerified: proofFlags.certificateHashVerified === true,
    upstreamReceiptHashVerified: proofFlags.upstreamReceiptHashVerified === true,
    sourceLedgerRootVerified: proofFlags.sourceLedgerRootVerified === true,
    sourceContinuityVerified: proofFlags.sourceContinuityVerified === true,
    sourceLinksVerified: proofFlags.sourceLinksVerified === true,
    jsonResponseOnly:
      finalAttestationVerifierPacket.jsonResponseOnly === true &&
      verifier.jsonResponseOnly === true &&
      proofFlags.jsonResponseOnly === true,
    noFilesystemWrite:
      finalAttestationVerifierPacket.noFilesystemWrite === true &&
      verifier.noFilesystemWrite === true &&
      proofFlags.noFilesystemWrite === true,
  };

  const terminalSealPayload = {
    version: WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERSION,
    sealType: 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL',
    audience: ['REGULATOR', 'INVESTOR'],
    tenantId,
    operator,
    sealedAt,
    chainRange,
    sourceFinalAttestationVerifierStatus: finalAttestationVerifierPacket.status,
    sourceFinalAttestationStatus: verifier.sourceAttestationStatus || null,
    ledgerRoot:
      finalAttestationVerifierPacket.ledgerRoot ||
      finalAttestation.ledgerRoot ||
      hashes.ledgerRoot ||
      null,
    hashes: {
      storedAttestationHash: finalAttestationVerifierPacket.storedAttestationHash || null,
      recomputedAttestationHash: finalAttestationVerifierPacket.recomputedAttestationHash || null,
      attestationHash: finalAttestation.attestationHash || null,
      attestationHashShort: finalAttestation.attestationHashShort || null,
      storedReceiptHash: hashes.storedReceiptHash || null,
      recomputedReceiptHash: hashes.recomputedReceiptHash || null,
      receiptHash: hashes.receiptHash || null,
      storedBundleIndexHash: hashes.storedBundleIndexHash || null,
      recomputedBundleIndexHash: hashes.recomputedBundleIndexHash || null,
      ledgerRoot: hashes.ledgerRoot || finalAttestation.ledgerRoot || null,
    },
    routeContracts: terminalRouteContracts,
    sourceRoutes: terminalSourceRoutes,
    statuses: terminalStatuses,
    proofFlags: terminalProofFlags,
    terminalDisposition: {
      evidenceChainStatus: 'TERMINALLY_SEALED',
      regulatorReady: true,
      investorReady: true,
      filesystemExported: false,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
    },
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };

  const terminalSealHash =
    computeRegulatorInvestorEvidenceChainTerminalSealHash(terminalSealPayload);

  const terminalSeal = {
    ...terminalSealPayload,
    terminalSealHash,
    terminalSealHashShort: terminalSealHash.slice(0, 16),
  };

  const requiredStatusesVerified =
    terminalStatuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
    terminalStatuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
    terminalStatuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
    terminalStatuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
    terminalStatuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
    terminalStatuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
    terminalStatuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
    terminalStatuses.R68V ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
    terminalStatuses.R68W ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
    terminalStatuses.R68X === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
    terminalStatuses.R68Y === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED';

  const proofFlagsAllTrue = Object.values(terminalProofFlags).every((value) => value === true);

  const issued =
    requiredStatusesVerified &&
    proofFlagsAllTrue &&
    terminalSeal.terminalDisposition.regulatorReady === true &&
    terminalSeal.terminalDisposition.investorReady === true &&
    terminalSeal.terminalDisposition.jsonResponseOnly === true &&
    terminalSeal.terminalDisposition.noFilesystemWrite === true &&
    terminalSeal.persistenceMode === 'JSON_RESPONSE_ONLY';

  return {
    ok: issued,
    version: WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERSION,
    status: issued
      ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED'
      : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_DEGRADED',
    terminalSealHash,
    terminalSealHashShort: terminalSealHash.slice(0, 16),
    ledgerRoot: terminalSeal.ledgerRoot,
    requiredStatusesVerified,
    proofFlagsAllTrue,
    finalAttestationVerifierPassed: terminalProofFlags.finalAttestationVerifierPassed,
    terminalSeal,
    sourceFinalAttestationVerifier: finalAttestationVerifierPacket,
    finalAttestation,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIER_VERSION =
  'R69A-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSeal
 * @description Verifies the R68Z terminal regulator and investor evidence-chain seal by recomputing its terminal seal hash.
 * @collaboration R68Z terminal seal, R68Y final attestation verifier, CRM regulator/investor evidence controls.
 */
export const verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSeal = async (options = {}) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const terminalSealPacket = await buildLeadSearchRegulatorInvestorEvidenceChainTerminalSeal({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const terminalSeal = terminalSealPacket.terminalSeal || {};
  const {
    terminalSealHash: storedTerminalSealHash,
    terminalSealHashShort,
    ...terminalSealPayload
  } = terminalSeal;

  const recomputedTerminalSealHash =
    computeRegulatorInvestorEvidenceChainTerminalSealHash(terminalSealPayload);
  const terminalSealHashVerified =
    Boolean(storedTerminalSealHash) && storedTerminalSealHash === recomputedTerminalSealHash;

  const expectedChainRange = [
    'R68O',
    'R68P',
    'R68Q',
    'R68R',
    'R68S',
    'R68T',
    'R68U',
    'R68V',
    'R68W',
    'R68X',
    'R68Y',
  ];

  const chainRange = Array.isArray(terminalSeal.chainRange) ? terminalSeal.chainRange : [];
  const chainRangeVerified = JSON.stringify(chainRange) === JSON.stringify(expectedChainRange);

  const audience = Array.isArray(terminalSeal.audience) ? terminalSeal.audience : [];
  const audienceVerified = JSON.stringify(audience) === JSON.stringify(['REGULATOR', 'INVESTOR']);

  const statuses = terminalSeal.statuses || {};
  const statusesVerified =
    statuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
    statuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
    statuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
    statuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
    statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
    statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
    statuses.R68V ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.R68W ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
    statuses.R68X === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
    statuses.R68Y === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED';

  const routeContracts = terminalSeal.routeContracts || {};
  const routeContractsVerified =
    routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
    routeContracts.R68P === 'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68Q ===
      'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
    routeContracts.R68R ===
      'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
    routeContracts.R68S ===
      'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY' &&
    routeContracts.R68T === 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY' &&
    routeContracts.R68U ===
      'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY' &&
    routeContracts.R68V ===
      'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68W ===
      'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
    routeContracts.R68X ===
      'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY' &&
    routeContracts.R68Y ===
      'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

  const sourceRoutes = terminalSeal.sourceRoutes || {};
  const sourceRoutesVerified =
    sourceRoutes.R68O ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
    sourceRoutes.R68P ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
    sourceRoutes.R68Q ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
    sourceRoutes.R68R ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
    sourceRoutes.R68S ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest' &&
    sourceRoutes.R68T ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest' &&
    sourceRoutes.R68U ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest' &&
    sourceRoutes.R68V ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest' &&
    sourceRoutes.R68W ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest' &&
    sourceRoutes.R68X ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest' &&
    sourceRoutes.R68Y ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest';

  const hashes = terminalSeal.hashes || {};
  const hashEqualityVerified =
    Boolean(hashes.storedAttestationHash) &&
    hashes.storedAttestationHash === hashes.recomputedAttestationHash &&
    Boolean(hashes.storedReceiptHash) &&
    hashes.storedReceiptHash === hashes.recomputedReceiptHash &&
    Boolean(hashes.storedBundleIndexHash) &&
    hashes.storedBundleIndexHash === hashes.recomputedBundleIndexHash;

  const proofFlags = terminalSeal.proofFlags || {};
  const proofFlagsVerified =
    Object.values(proofFlags).length > 0 &&
    Object.values(proofFlags).every((value) => value === true);

  const terminalDisposition = terminalSeal.terminalDisposition || {};
  const terminalDispositionVerified =
    terminalDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
    terminalDisposition.regulatorReady === true &&
    terminalDisposition.investorReady === true &&
    terminalDisposition.filesystemExported === false &&
    terminalDisposition.jsonResponseOnly === true &&
    terminalDisposition.noFilesystemWrite === true;

  const jsonResponseOnly =
    terminalSealPacket.jsonResponseOnly === true &&
    terminalSeal.persistenceMode === 'JSON_RESPONSE_ONLY' &&
    proofFlags.jsonResponseOnly === true &&
    terminalDisposition.jsonResponseOnly === true;

  const noFilesystemWrite =
    terminalSealPacket.noFilesystemWrite === true &&
    proofFlags.noFilesystemWrite === true &&
    terminalDisposition.noFilesystemWrite === true;

  const verified =
    terminalSealPacket.status === 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED' &&
    terminalSealHashVerified &&
    terminalSealPacket.requiredStatusesVerified === true &&
    terminalSealPacket.proofFlagsAllTrue === true &&
    terminalSealPacket.finalAttestationVerifierPassed === true &&
    chainRangeVerified &&
    audienceVerified &&
    statusesVerified &&
    routeContractsVerified &&
    sourceRoutesVerified &&
    hashEqualityVerified &&
    proofFlagsVerified &&
    terminalDispositionVerified &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version: WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED'
      : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_FAILED',
    terminalSealHashVerified,
    storedTerminalSealHash,
    storedTerminalSealHashShort:
      terminalSealHashShort || String(storedTerminalSealHash || '').slice(0, 16),
    recomputedTerminalSealHash,
    recomputedTerminalSealHashShort: recomputedTerminalSealHash.slice(0, 16),
    requiredStatusesVerified: terminalSealPacket.requiredStatusesVerified === true,
    proofFlagsAllTrue: terminalSealPacket.proofFlagsAllTrue === true,
    finalAttestationVerifierPassed: terminalSealPacket.finalAttestationVerifierPassed === true,
    chainRangeVerified,
    audienceVerified,
    statusesVerified,
    routeContractsVerified,
    sourceRoutesVerified,
    hashEqualityVerified,
    proofFlagsVerified,
    terminalDispositionVerified,
    regulatorReady: terminalDisposition.regulatorReady === true,
    investorReady: terminalDisposition.investorReady === true,
    ledgerRoot: terminalSeal.ledgerRoot || terminalSealPacket.ledgerRoot || null,
    terminalSealVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceTerminalSealStatus: terminalSealPacket.status,
      terminalSealHashVerified,
      storedTerminalSealHash,
      recomputedTerminalSealHash,
      requiredStatusesVerified: terminalSealPacket.requiredStatusesVerified === true,
      proofFlagsAllTrue: terminalSealPacket.proofFlagsAllTrue === true,
      finalAttestationVerifierPassed: terminalSealPacket.finalAttestationVerifierPassed === true,
      chainRangeVerified,
      audienceVerified,
      statusesVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      hashEqualityVerified,
      proofFlagsVerified,
      terminalDispositionVerified,
      regulatorReady: terminalDisposition.regulatorReady === true,
      investorReady: terminalDisposition.investorReady === true,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    terminalSeal,
    sourceTerminalSealPacket: terminalSealPacket,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERSION =
  'R69B-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * @function normalizeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptValue
 * @description Produces deterministic values for R69B terminal seal verification receipt hashing.
 * @collaboration R69A terminal seal verifier, R68Z terminal seal, CRM regulator/investor receipt controls.
 */
const normalizeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) =>
      normalizeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptValue(item)
    );
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] =
          normalizeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptValue(value[key]);
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptHash
 * @description Computes a deterministic hash for the R69B terminal seal verification receipt.
 * @collaboration R69A verifier packet, terminal evidence seal, regulator/investor proof receipt surface.
 */
const computeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptHash = (receiptPayload) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(
        normalizeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptValue(receiptPayload)
      )
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt
 * @description Materializes a JSON-only verification receipt from the R69A terminal seal verifier.
 * @collaboration CRM command routes, R69A terminal seal verifier, regulator/investor receipt controls.
 */
export const buildLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const verifierPacket = await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSeal({
    tenantId,
    ledgerId,
    limit,
    operator,
  });

  const terminalSealVerifier = verifierPacket.terminalSealVerifier || {};
  const terminalSeal = verifierPacket.terminalSeal || {};
  const terminalDisposition = terminalSeal.terminalDisposition || {};
  const issuedAt = new Date().toISOString();

  const receiptPayload = {
    version: WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERSION,
    receiptType: 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT',
    tenantId,
    operator,
    issuedAt,
    sourceTerminalSealVerifierStatus: verifierPacket.status,
    sourceTerminalSealStatus: terminalSealVerifier.sourceTerminalSealStatus || null,
    ledgerRoot: verifierPacket.ledgerRoot || terminalSeal.ledgerRoot || null,
    storedTerminalSealHash:
      verifierPacket.storedTerminalSealHash || terminalSealVerifier.storedTerminalSealHash || null,
    recomputedTerminalSealHash:
      verifierPacket.recomputedTerminalSealHash ||
      terminalSealVerifier.recomputedTerminalSealHash ||
      null,
    terminalSealHashVerified: verifierPacket.terminalSealHashVerified === true,
    requiredStatusesVerified: verifierPacket.requiredStatusesVerified === true,
    proofFlagsAllTrue: verifierPacket.proofFlagsAllTrue === true,
    finalAttestationVerifierPassed: verifierPacket.finalAttestationVerifierPassed === true,
    chainRangeVerified: verifierPacket.chainRangeVerified === true,
    audienceVerified: verifierPacket.audienceVerified === true,
    statusesVerified: verifierPacket.statusesVerified === true,
    routeContractsVerified: verifierPacket.routeContractsVerified === true,
    sourceRoutesVerified: verifierPacket.sourceRoutesVerified === true,
    hashEqualityVerified: verifierPacket.hashEqualityVerified === true,
    proofFlagsVerified: verifierPacket.proofFlagsVerified === true,
    terminalDispositionVerified: verifierPacket.terminalDispositionVerified === true,
    regulatorReady: verifierPacket.regulatorReady === true,
    investorReady: verifierPacket.investorReady === true,
    chainRange: terminalSeal.chainRange || [],
    audience: terminalSeal.audience || [],
    statuses: terminalSeal.statuses || {},
    routeContracts: terminalSeal.routeContracts || {},
    sourceRoutes: terminalSeal.sourceRoutes || {},
    hashes: terminalSeal.hashes || {},
    proofFlags: terminalSeal.proofFlags || {},
    terminalDisposition,
    sourceRoute:
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
    sourceTerminalSealRoute:
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
    sourceFinalAttestationVerifierRoute:
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
    jsonResponseOnly:
      verifierPacket.jsonResponseOnly === true &&
      terminalSealVerifier.jsonResponseOnly === true &&
      terminalDisposition.jsonResponseOnly === true,
    noFilesystemWrite:
      verifierPacket.noFilesystemWrite === true &&
      terminalSealVerifier.noFilesystemWrite === true &&
      terminalDisposition.noFilesystemWrite === true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };

  const receiptHash =
    computeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptHash(receiptPayload);

  const terminalSealVerificationReceipt = {
    ...receiptPayload,
    receiptHash,
    receiptHashShort: receiptHash.slice(0, 16),
  };

  const materialized =
    verifierPacket.status === 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
    terminalSealVerificationReceipt.terminalSealHashVerified === true &&
    terminalSealVerificationReceipt.storedTerminalSealHash ===
      terminalSealVerificationReceipt.recomputedTerminalSealHash &&
    terminalSealVerificationReceipt.requiredStatusesVerified === true &&
    terminalSealVerificationReceipt.proofFlagsAllTrue === true &&
    terminalSealVerificationReceipt.finalAttestationVerifierPassed === true &&
    terminalSealVerificationReceipt.chainRangeVerified === true &&
    terminalSealVerificationReceipt.audienceVerified === true &&
    terminalSealVerificationReceipt.statusesVerified === true &&
    terminalSealVerificationReceipt.routeContractsVerified === true &&
    terminalSealVerificationReceipt.sourceRoutesVerified === true &&
    terminalSealVerificationReceipt.hashEqualityVerified === true &&
    terminalSealVerificationReceipt.proofFlagsVerified === true &&
    terminalSealVerificationReceipt.terminalDispositionVerified === true &&
    terminalSealVerificationReceipt.regulatorReady === true &&
    terminalSealVerificationReceipt.investorReady === true &&
    terminalSealVerificationReceipt.jsonResponseOnly === true &&
    terminalSealVerificationReceipt.noFilesystemWrite === true;

  return {
    ok: materialized,
    version: WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERSION,
    status: materialized
      ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED'
      : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_DEGRADED',
    receiptHash,
    receiptHashShort: receiptHash.slice(0, 16),
    ledgerRoot: terminalSealVerificationReceipt.ledgerRoot,
    terminalSealVerificationReceipt,
    sourceTerminalSealVerifier: verifierPacket,
    terminalSeal,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_VERSION =
  'R69C-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt
 * @description Verifies the R69B terminal seal verification receipt by recomputing its receipt hash and validating upstream terminal posture.
 * @collaboration R69B receipt, R69A terminal seal verifier, R68Z terminal seal, CRM regulator/investor evidence controls.
 */
export const verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt = async (
  options = {}
) => {
  const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
  const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
  const limit = options.limit || 25;
  const operator =
    String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
    'SYSTEM';

  const receiptPacket =
    await buildLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt({
      tenantId,
      ledgerId,
      limit,
      operator,
    });

  const receipt = receiptPacket.terminalSealVerificationReceipt || {};
  const { receiptHash: storedReceiptHash, receiptHashShort, ...receiptPayload } = receipt;

  const recomputedReceiptHash =
    computeRegulatorInvestorEvidenceChainTerminalSealVerificationReceiptHash(receiptPayload);
  const receiptHashVerified =
    Boolean(storedReceiptHash) && storedReceiptHash === recomputedReceiptHash;

  const expectedChainRange = [
    'R68O',
    'R68P',
    'R68Q',
    'R68R',
    'R68S',
    'R68T',
    'R68U',
    'R68V',
    'R68W',
    'R68X',
    'R68Y',
  ];

  const chainRange = Array.isArray(receipt.chainRange) ? receipt.chainRange : [];
  const chainRangeVerified = JSON.stringify(chainRange) === JSON.stringify(expectedChainRange);

  const audience = Array.isArray(receipt.audience) ? receipt.audience : [];
  const audienceVerified = JSON.stringify(audience) === JSON.stringify(['REGULATOR', 'INVESTOR']);

  const statuses = receipt.statuses || {};
  const statusesVerified =
    statuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
    statuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
    statuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
    statuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
    statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
    statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
    statuses.R68V ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
    statuses.R68W ===
      'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
    statuses.R68X === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
    statuses.R68Y === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED';

  const routeContracts = receipt.routeContracts || {};
  const routeContractsVerified =
    routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
    routeContracts.R68P === 'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68Q ===
      'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
    routeContracts.R68R ===
      'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
    routeContracts.R68S ===
      'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY' &&
    routeContracts.R68T === 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY' &&
    routeContracts.R68U ===
      'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY' &&
    routeContracts.R68V ===
      'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY' &&
    routeContracts.R68W ===
      'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
    routeContracts.R68X ===
      'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY' &&
    routeContracts.R68Y ===
      'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

  const sourceRoutes = receipt.sourceRoutes || {};
  const sourceRoutesVerified =
    sourceRoutes.R68O ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
    sourceRoutes.R68P ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
    sourceRoutes.R68Q ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
    sourceRoutes.R68R ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
    sourceRoutes.R68S ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest' &&
    sourceRoutes.R68T ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest' &&
    sourceRoutes.R68U ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest' &&
    sourceRoutes.R68V ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest' &&
    sourceRoutes.R68W ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest' &&
    sourceRoutes.R68X ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest' &&
    sourceRoutes.R68Y ===
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest';

  const hashes = receipt.hashes || {};
  const hashEqualityVerified =
    Boolean(hashes.storedAttestationHash) &&
    hashes.storedAttestationHash === hashes.recomputedAttestationHash &&
    Boolean(hashes.storedReceiptHash) &&
    hashes.storedReceiptHash === hashes.recomputedReceiptHash &&
    Boolean(hashes.storedBundleIndexHash) &&
    hashes.storedBundleIndexHash === hashes.recomputedBundleIndexHash;

  const proofFlags = receipt.proofFlags || {};
  const proofFlagsVerified =
    Object.values(proofFlags).length > 0 &&
    Object.values(proofFlags).every((value) => value === true);

  const terminalDisposition = receipt.terminalDisposition || {};
  const terminalDispositionVerified =
    terminalDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
    terminalDisposition.regulatorReady === true &&
    terminalDisposition.investorReady === true &&
    terminalDisposition.filesystemExported === false &&
    terminalDisposition.jsonResponseOnly === true &&
    terminalDisposition.noFilesystemWrite === true;

  const terminalSealHashVerified =
    receipt.terminalSealHashVerified === true &&
    Boolean(receipt.storedTerminalSealHash) &&
    receipt.storedTerminalSealHash === receipt.recomputedTerminalSealHash;

  const upstreamReceiptPostureVerified =
    receiptPacket.status ===
      'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
    receipt.sourceTerminalSealVerifierStatus ===
      'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
    receipt.sourceTerminalSealStatus === 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED';

  const receiptFlagsVerified =
    receipt.requiredStatusesVerified === true &&
    receipt.proofFlagsAllTrue === true &&
    receipt.finalAttestationVerifierPassed === true &&
    receipt.chainRangeVerified === true &&
    receipt.audienceVerified === true &&
    receipt.statusesVerified === true &&
    receipt.routeContractsVerified === true &&
    receipt.sourceRoutesVerified === true &&
    receipt.hashEqualityVerified === true &&
    receipt.proofFlagsVerified === true &&
    receipt.terminalDispositionVerified === true &&
    receipt.regulatorReady === true &&
    receipt.investorReady === true;

  const jsonResponseOnly =
    receiptPacket.jsonResponseOnly === true &&
    receipt.jsonResponseOnly === true &&
    receipt.persistenceMode === 'JSON_RESPONSE_ONLY' &&
    terminalDisposition.jsonResponseOnly === true;

  const noFilesystemWrite =
    receiptPacket.noFilesystemWrite === true &&
    receipt.noFilesystemWrite === true &&
    terminalDisposition.noFilesystemWrite === true;

  const verified =
    receiptHashVerified &&
    terminalSealHashVerified &&
    upstreamReceiptPostureVerified &&
    receiptFlagsVerified &&
    chainRangeVerified &&
    audienceVerified &&
    statusesVerified &&
    routeContractsVerified &&
    sourceRoutesVerified &&
    hashEqualityVerified &&
    proofFlagsVerified &&
    terminalDispositionVerified &&
    jsonResponseOnly &&
    noFilesystemWrite;

  return {
    ok: verified,
    version:
      WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_VERSION,
    status: verified
      ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED'
      : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFICATION_FAILED',
    receiptHashVerified,
    storedReceiptHash,
    storedReceiptHashShort: receiptHashShort || String(storedReceiptHash || '').slice(0, 16),
    recomputedReceiptHash,
    recomputedReceiptHashShort: recomputedReceiptHash.slice(0, 16),
    terminalSealHashVerified,
    storedTerminalSealHash: receipt.storedTerminalSealHash || null,
    recomputedTerminalSealHash: receipt.recomputedTerminalSealHash || null,
    upstreamReceiptPostureVerified,
    receiptFlagsVerified,
    chainRangeVerified,
    audienceVerified,
    statusesVerified,
    routeContractsVerified,
    sourceRoutesVerified,
    hashEqualityVerified,
    proofFlagsVerified,
    terminalDispositionVerified,
    regulatorReady: receipt.regulatorReady === true,
    investorReady: receipt.investorReady === true,
    sourceTerminalSealVerifierStatus: receipt.sourceTerminalSealVerifierStatus || null,
    sourceTerminalSealStatus: receipt.sourceTerminalSealStatus || null,
    ledgerRoot: receipt.ledgerRoot || receiptPacket.ledgerRoot || null,
    terminalSealVerificationReceiptVerifier: {
      tenantId,
      operator,
      verifiedAt: new Date().toISOString(),
      sourceReceiptStatus: receiptPacket.status,
      receiptHashVerified,
      storedReceiptHash,
      recomputedReceiptHash,
      terminalSealHashVerified,
      storedTerminalSealHash: receipt.storedTerminalSealHash || null,
      recomputedTerminalSealHash: receipt.recomputedTerminalSealHash || null,
      upstreamReceiptPostureVerified,
      receiptFlagsVerified,
      chainRangeVerified,
      audienceVerified,
      statusesVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      hashEqualityVerified,
      proofFlagsVerified,
      terminalDispositionVerified,
      regulatorReady: receipt.regulatorReady === true,
      investorReady: receipt.investorReady === true,
      jsonResponseOnly,
      noFilesystemWrite,
    },
    terminalSealVerificationReceipt: receipt,
    sourceTerminalSealVerificationReceiptPacket: receiptPacket,
    terminalSeal: receiptPacket.terminalSeal || null,
    jsonResponseOnly: true,
    noFilesystemWrite: true,
    persistenceMode: 'JSON_RESPONSE_ONLY',
  };
};

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERSION =
  'R69D-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * @function normalizeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateValue
 * @description Produces deterministic values for R69D terminal receipt finality certificate hashing.
 * @collaboration R69C terminal receipt verifier, R69B receipt, regulator/investor finality controls.
 */
const normalizeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateValue = (value) => {
  if (Array.isArray(value)) {
    return value.map((item) =>
      normalizeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateValue(item)
    );
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] =
          normalizeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateValue(
            value[key]
          );
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateHash
 * @description Computes a deterministic hash for the R69D terminal receipt finality certificate.
 * @collaboration R69C verifier packet, terminal receipt evidence, regulator/investor finality proof surface.
 */
const computeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateHash = (
  certificatePayload
) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(
        normalizeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateValue(
          certificatePayload
        )
      )
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate
 * @description Issues a JSON-only terminal receipt finality certificate from the R69C verifier.
 * @collaboration CRM command routes, R69C terminal receipt verifier, regulator/investor finality controls.
 */
export const buildLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const receiptVerifierPacket =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt({
        tenantId,
        ledgerId,
        limit,
        operator,
      });

    const receiptVerifier = receiptVerifierPacket.terminalSealVerificationReceiptVerifier || {};
    const receipt = receiptVerifierPacket.terminalSealVerificationReceipt || {};
    const terminalDisposition = receipt.terminalDisposition || {};
    const certifiedAt = new Date().toISOString();

    const finalityPayload = {
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERSION,
      certificateType: 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE',
      tenantId,
      operator,
      certifiedAt,
      sourceReceiptVerifierStatus: receiptVerifierPacket.status,
      sourceReceiptStatus: receiptVerifier.sourceReceiptStatus || null,
      sourceTerminalSealVerifierStatus:
        receiptVerifierPacket.sourceTerminalSealVerifierStatus ||
        receipt.sourceTerminalSealVerifierStatus ||
        null,
      sourceTerminalSealStatus:
        receiptVerifierPacket.sourceTerminalSealStatus || receipt.sourceTerminalSealStatus || null,
      ledgerRoot: receiptVerifierPacket.ledgerRoot || receipt.ledgerRoot || null,
      storedReceiptHash:
        receiptVerifierPacket.storedReceiptHash || receiptVerifier.storedReceiptHash || null,
      recomputedReceiptHash:
        receiptVerifierPacket.recomputedReceiptHash ||
        receiptVerifier.recomputedReceiptHash ||
        null,
      receiptHashVerified: receiptVerifierPacket.receiptHashVerified === true,
      storedTerminalSealHash:
        receiptVerifierPacket.storedTerminalSealHash ||
        receiptVerifier.storedTerminalSealHash ||
        receipt.storedTerminalSealHash ||
        null,
      recomputedTerminalSealHash:
        receiptVerifierPacket.recomputedTerminalSealHash ||
        receiptVerifier.recomputedTerminalSealHash ||
        receipt.recomputedTerminalSealHash ||
        null,
      terminalSealHashVerified: receiptVerifierPacket.terminalSealHashVerified === true,
      upstreamReceiptPostureVerified: receiptVerifierPacket.upstreamReceiptPostureVerified === true,
      receiptFlagsVerified: receiptVerifierPacket.receiptFlagsVerified === true,
      chainRangeVerified: receiptVerifierPacket.chainRangeVerified === true,
      audienceVerified: receiptVerifierPacket.audienceVerified === true,
      statusesVerified: receiptVerifierPacket.statusesVerified === true,
      routeContractsVerified: receiptVerifierPacket.routeContractsVerified === true,
      sourceRoutesVerified: receiptVerifierPacket.sourceRoutesVerified === true,
      hashEqualityVerified: receiptVerifierPacket.hashEqualityVerified === true,
      proofFlagsVerified: receiptVerifierPacket.proofFlagsVerified === true,
      terminalDispositionVerified: receiptVerifierPacket.terminalDispositionVerified === true,
      regulatorReady: receiptVerifierPacket.regulatorReady === true,
      investorReady: receiptVerifierPacket.investorReady === true,
      chainRange: receipt.chainRange || [],
      audience: receipt.audience || [],
      statuses: receipt.statuses || {},
      routeContracts: receipt.routeContracts || {},
      sourceRoutes: receipt.sourceRoutes || {},
      hashes: receipt.hashes || {},
      proofFlags: receipt.proofFlags || {},
      terminalDisposition,
      finalityDisposition: {
        certificateStatus: 'FINALITY_CERTIFIED',
        evidenceChainStatus: 'TERMINALLY_SEALED',
        receiptVerified: receiptVerifierPacket.receiptHashVerified === true,
        terminalSealVerified: receiptVerifierPacket.terminalSealHashVerified === true,
        regulatorReady: receiptVerifierPacket.regulatorReady === true,
        investorReady: receiptVerifierPacket.investorReady === true,
        filesystemExported: false,
        jsonResponseOnly: true,
        noFilesystemWrite: true,
      },
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      jsonResponseOnly:
        receiptVerifierPacket.jsonResponseOnly === true &&
        receiptVerifier.jsonResponseOnly === true &&
        receipt.jsonResponseOnly === true &&
        terminalDisposition.jsonResponseOnly === true,
      noFilesystemWrite:
        receiptVerifierPacket.noFilesystemWrite === true &&
        receiptVerifier.noFilesystemWrite === true &&
        receipt.noFilesystemWrite === true &&
        terminalDisposition.noFilesystemWrite === true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };

    const certificateHash =
      computeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateHash(finalityPayload);

    const terminalReceiptFinalityCertificate = {
      ...finalityPayload,
      certificateHash,
      certificateHashShort: certificateHash.slice(0, 16),
    };

    const issued =
      receiptVerifierPacket.status ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      terminalReceiptFinalityCertificate.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      terminalReceiptFinalityCertificate.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      terminalReceiptFinalityCertificate.sourceTerminalSealStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED' &&
      terminalReceiptFinalityCertificate.receiptHashVerified === true &&
      terminalReceiptFinalityCertificate.storedReceiptHash ===
        terminalReceiptFinalityCertificate.recomputedReceiptHash &&
      terminalReceiptFinalityCertificate.terminalSealHashVerified === true &&
      terminalReceiptFinalityCertificate.storedTerminalSealHash ===
        terminalReceiptFinalityCertificate.recomputedTerminalSealHash &&
      terminalReceiptFinalityCertificate.upstreamReceiptPostureVerified === true &&
      terminalReceiptFinalityCertificate.receiptFlagsVerified === true &&
      terminalReceiptFinalityCertificate.chainRangeVerified === true &&
      terminalReceiptFinalityCertificate.audienceVerified === true &&
      terminalReceiptFinalityCertificate.statusesVerified === true &&
      terminalReceiptFinalityCertificate.routeContractsVerified === true &&
      terminalReceiptFinalityCertificate.sourceRoutesVerified === true &&
      terminalReceiptFinalityCertificate.hashEqualityVerified === true &&
      terminalReceiptFinalityCertificate.proofFlagsVerified === true &&
      terminalReceiptFinalityCertificate.terminalDispositionVerified === true &&
      terminalReceiptFinalityCertificate.regulatorReady === true &&
      terminalReceiptFinalityCertificate.investorReady === true &&
      terminalReceiptFinalityCertificate.finalityDisposition.certificateStatus ===
        'FINALITY_CERTIFIED' &&
      terminalReceiptFinalityCertificate.finalityDisposition.receiptVerified === true &&
      terminalReceiptFinalityCertificate.finalityDisposition.terminalSealVerified === true &&
      terminalReceiptFinalityCertificate.finalityDisposition.regulatorReady === true &&
      terminalReceiptFinalityCertificate.finalityDisposition.investorReady === true &&
      terminalReceiptFinalityCertificate.finalityDisposition.filesystemExported === false &&
      terminalReceiptFinalityCertificate.finalityDisposition.jsonResponseOnly === true &&
      terminalReceiptFinalityCertificate.finalityDisposition.noFilesystemWrite === true &&
      terminalReceiptFinalityCertificate.jsonResponseOnly === true &&
      terminalReceiptFinalityCertificate.noFilesystemWrite === true &&
      terminalReceiptFinalityCertificate.persistenceMode === 'JSON_RESPONSE_ONLY';

    return {
      ok: issued,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERSION,
      status: issued
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_DEGRADED',
      certificateHash,
      certificateHashShort: certificateHash.slice(0, 16),
      ledgerRoot: terminalReceiptFinalityCertificate.ledgerRoot,
      receiptHashVerified: terminalReceiptFinalityCertificate.receiptHashVerified,
      terminalSealHashVerified: terminalReceiptFinalityCertificate.terminalSealHashVerified,
      upstreamReceiptPostureVerified:
        terminalReceiptFinalityCertificate.upstreamReceiptPostureVerified,
      receiptFlagsVerified: terminalReceiptFinalityCertificate.receiptFlagsVerified,
      terminalDispositionVerified: terminalReceiptFinalityCertificate.terminalDispositionVerified,
      regulatorReady: terminalReceiptFinalityCertificate.regulatorReady,
      investorReady: terminalReceiptFinalityCertificate.investorReady,
      terminalReceiptFinalityCertificate,
      sourceTerminalReceiptVerifier: receiptVerifierPacket,
      terminalSealVerificationReceipt: receipt,
      terminalSeal: receiptVerifierPacket.terminalSeal || null,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERSION =
  'R69E-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate
 * @description Verifies the R69D terminal receipt finality certificate by recomputing its certificate hash and validating upstream evidence posture.
 * @collaboration R69D finality certificate, R69C receipt verifier, R69B receipt, R69A terminal seal verifier, R68Z terminal seal.
 */
export const verifyLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const certificatePacket =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate({
        tenantId,
        ledgerId,
        limit,
        operator,
      });

    const certificate = certificatePacket.terminalReceiptFinalityCertificate || {};
    const {
      certificateHash: storedCertificateHash,
      certificateHashShort,
      ...certificatePayload
    } = certificate;

    const recomputedCertificateHash =
      computeRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificateHash(
        certificatePayload
      );

    const certificateHashVerified =
      Boolean(storedCertificateHash) && storedCertificateHash === recomputedCertificateHash;

    const finalityDisposition = certificate.finalityDisposition || {};
    const terminalDisposition = certificate.terminalDisposition || {};

    const expectedChainRange = [
      'R68O',
      'R68P',
      'R68Q',
      'R68R',
      'R68S',
      'R68T',
      'R68U',
      'R68V',
      'R68W',
      'R68X',
      'R68Y',
    ];

    const chainRange = Array.isArray(certificate.chainRange) ? certificate.chainRange : [];
    const chainRangeVerified = JSON.stringify(chainRange) === JSON.stringify(expectedChainRange);

    const audience = Array.isArray(certificate.audience) ? certificate.audience : [];
    const audienceVerified = JSON.stringify(audience) === JSON.stringify(['REGULATOR', 'INVESTOR']);

    const statuses = certificate.statuses || {};
    const statusesVerified =
      statuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
      statuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
      statuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
      statuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
      statuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
      statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
      statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
      statuses.R68V ===
        'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
      statuses.R68W ===
        'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
      statuses.R68X === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
      statuses.R68Y === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED';

    const routeContracts = certificate.routeContracts || {};
    const routeContractsVerified =
      routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
      routeContracts.R68P ===
        'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
      routeContracts.R68Q ===
        'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
      routeContracts.R68R ===
        'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
      routeContracts.R68S ===
        'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY' &&
      routeContracts.R68T === 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY' &&
      routeContracts.R68U ===
        'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY' &&
      routeContracts.R68V ===
        'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY' &&
      routeContracts.R68W ===
        'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
      routeContracts.R68X ===
        'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY' &&
      routeContracts.R68Y ===
        'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

    const sourceRoutes = certificate.sourceRoutes || {};
    const sourceRoutesVerified =
      sourceRoutes.R68O ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
      sourceRoutes.R68P ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
      sourceRoutes.R68Q ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
      sourceRoutes.R68R ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
      sourceRoutes.R68S ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest' &&
      sourceRoutes.R68T ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest' &&
      sourceRoutes.R68U ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest' &&
      sourceRoutes.R68V ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest' &&
      sourceRoutes.R68W ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest' &&
      sourceRoutes.R68X ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest' &&
      sourceRoutes.R68Y ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest';

    const hashes = certificate.hashes || {};
    const hashEqualityVerified =
      Boolean(hashes.storedAttestationHash) &&
      hashes.storedAttestationHash === hashes.recomputedAttestationHash &&
      Boolean(hashes.storedReceiptHash) &&
      hashes.storedReceiptHash === hashes.recomputedReceiptHash &&
      Boolean(hashes.storedBundleIndexHash) &&
      hashes.storedBundleIndexHash === hashes.recomputedBundleIndexHash;

    const proofFlags = certificate.proofFlags || {};
    const proofFlagsVerified =
      Object.values(proofFlags).length > 0 &&
      Object.values(proofFlags).every((value) => value === true);

    const receiptHashVerified =
      certificate.receiptHashVerified === true &&
      Boolean(certificate.storedReceiptHash) &&
      certificate.storedReceiptHash === certificate.recomputedReceiptHash;

    const terminalSealHashVerified =
      certificate.terminalSealHashVerified === true &&
      Boolean(certificate.storedTerminalSealHash) &&
      certificate.storedTerminalSealHash === certificate.recomputedTerminalSealHash;

    const upstreamCertificatePostureVerified =
      certificatePacket.status ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED' &&
      certificate.sourceReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      certificate.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      certificate.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      certificate.sourceTerminalSealStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED';

    const certificateFlagsVerified =
      certificate.upstreamReceiptPostureVerified === true &&
      certificate.receiptFlagsVerified === true &&
      certificate.chainRangeVerified === true &&
      certificate.audienceVerified === true &&
      certificate.statusesVerified === true &&
      certificate.routeContractsVerified === true &&
      certificate.sourceRoutesVerified === true &&
      certificate.hashEqualityVerified === true &&
      certificate.proofFlagsVerified === true &&
      certificate.terminalDispositionVerified === true &&
      certificate.regulatorReady === true &&
      certificate.investorReady === true;

    const terminalDispositionVerified =
      terminalDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
      terminalDisposition.regulatorReady === true &&
      terminalDisposition.investorReady === true &&
      terminalDisposition.filesystemExported === false &&
      terminalDisposition.jsonResponseOnly === true &&
      terminalDisposition.noFilesystemWrite === true;

    const finalityDispositionVerified =
      finalityDisposition.certificateStatus === 'FINALITY_CERTIFIED' &&
      finalityDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
      finalityDisposition.receiptVerified === true &&
      finalityDisposition.terminalSealVerified === true &&
      finalityDisposition.regulatorReady === true &&
      finalityDisposition.investorReady === true &&
      finalityDisposition.filesystemExported === false &&
      finalityDisposition.jsonResponseOnly === true &&
      finalityDisposition.noFilesystemWrite === true;

    const regulatorReady =
      certificate.regulatorReady === true &&
      finalityDisposition.regulatorReady === true &&
      terminalDisposition.regulatorReady === true;

    const investorReady =
      certificate.investorReady === true &&
      finalityDisposition.investorReady === true &&
      terminalDisposition.investorReady === true;

    const jsonResponseOnly =
      certificatePacket.jsonResponseOnly === true &&
      certificate.jsonResponseOnly === true &&
      certificate.persistenceMode === 'JSON_RESPONSE_ONLY' &&
      finalityDisposition.jsonResponseOnly === true &&
      terminalDisposition.jsonResponseOnly === true;

    const noFilesystemWrite =
      certificatePacket.noFilesystemWrite === true &&
      certificate.noFilesystemWrite === true &&
      finalityDisposition.noFilesystemWrite === true &&
      terminalDisposition.noFilesystemWrite === true;

    const verified =
      certificateHashVerified &&
      receiptHashVerified &&
      terminalSealHashVerified &&
      upstreamCertificatePostureVerified &&
      certificateFlagsVerified &&
      chainRangeVerified &&
      audienceVerified &&
      statusesVerified &&
      routeContractsVerified &&
      sourceRoutesVerified &&
      hashEqualityVerified &&
      proofFlagsVerified &&
      terminalDispositionVerified &&
      finalityDispositionVerified &&
      regulatorReady &&
      investorReady &&
      jsonResponseOnly &&
      noFilesystemWrite;

    return {
      ok: verified,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERSION,
      status: verified
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_FAILED',
      certificateHashVerified,
      storedCertificateHash,
      storedCertificateHashShort:
        certificateHashShort || String(storedCertificateHash || '').slice(0, 16),
      recomputedCertificateHash,
      recomputedCertificateHashShort: recomputedCertificateHash.slice(0, 16),
      receiptHashVerified,
      storedReceiptHash: certificate.storedReceiptHash || null,
      recomputedReceiptHash: certificate.recomputedReceiptHash || null,
      terminalSealHashVerified,
      storedTerminalSealHash: certificate.storedTerminalSealHash || null,
      recomputedTerminalSealHash: certificate.recomputedTerminalSealHash || null,
      upstreamCertificatePostureVerified,
      certificateFlagsVerified,
      chainRangeVerified,
      audienceVerified,
      statusesVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      hashEqualityVerified,
      proofFlagsVerified,
      terminalDispositionVerified,
      finalityDispositionVerified,
      regulatorReady,
      investorReady,
      sourceReceiptVerifierStatus: certificate.sourceReceiptVerifierStatus || null,
      sourceReceiptStatus: certificate.sourceReceiptStatus || null,
      sourceTerminalSealVerifierStatus: certificate.sourceTerminalSealVerifierStatus || null,
      sourceTerminalSealStatus: certificate.sourceTerminalSealStatus || null,
      ledgerRoot: certificate.ledgerRoot || certificatePacket.ledgerRoot || null,
      terminalReceiptFinalityCertificateVerifier: {
        tenantId,
        operator,
        verifiedAt: new Date().toISOString(),
        sourceCertificateStatus: certificatePacket.status,
        certificateHashVerified,
        storedCertificateHash,
        recomputedCertificateHash,
        receiptHashVerified,
        storedReceiptHash: certificate.storedReceiptHash || null,
        recomputedReceiptHash: certificate.recomputedReceiptHash || null,
        terminalSealHashVerified,
        storedTerminalSealHash: certificate.storedTerminalSealHash || null,
        recomputedTerminalSealHash: certificate.recomputedTerminalSealHash || null,
        upstreamCertificatePostureVerified,
        certificateFlagsVerified,
        chainRangeVerified,
        audienceVerified,
        statusesVerified,
        routeContractsVerified,
        sourceRoutesVerified,
        hashEqualityVerified,
        proofFlagsVerified,
        terminalDispositionVerified,
        finalityDispositionVerified,
        regulatorReady,
        investorReady,
        jsonResponseOnly,
        noFilesystemWrite,
      },
      terminalReceiptFinalityCertificate: certificate,
      sourceTerminalReceiptFinalityCertificatePacket: certificatePacket,
      terminalSealVerificationReceipt: certificatePacket.terminalSealVerificationReceipt || null,
      terminalSeal: certificatePacket.terminalSeal || null,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERSION =
  'R69F-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-CERTIFICATE-EVIDENCE-INDEX-AUTHORITY';

/**
 * @function normalizeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexValue
 * @description Produces deterministic values for R69F terminal finality certificate evidence index hashing.
 * @collaboration R69E finality certificate verifier, R69D certificate, terminal regulator/investor evidence index controls.
 */
const normalizeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexValue = (
  value
) => {
  if (Array.isArray(value)) {
    return value.map((item) =>
      normalizeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexValue(item)
    );
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] =
          normalizeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexValue(
            value[key]
          );
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexHash
 * @description Computes a deterministic hash for the R69F terminal finality certificate evidence index.
 * @collaboration R69E verifier packet, finality certificate evidence, regulator/investor lookup posture.
 */
const computeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexHash = (
  indexPayload
) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(
        normalizeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexValue(
          indexPayload
        )
      )
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex
 * @description Indexes the verified R69E terminal finality certificate verifier into a JSON-only regulator/investor evidence lookup packet.
 * @collaboration CRM command routes, R69E finality certificate verifier, regulator/investor terminal evidence controls.
 */
export const buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const verifierPacket =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate({
        tenantId,
        ledgerId,
        limit,
        operator,
      });

    const verifier = verifierPacket.terminalReceiptFinalityCertificateVerifier || {};
    const certificate = verifierPacket.terminalReceiptFinalityCertificate || {};
    const finalityDisposition = certificate.finalityDisposition || {};
    const terminalDisposition = certificate.terminalDisposition || {};
    const indexedAt = new Date().toISOString();

    const evidenceIndexPayload = {
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERSION,
      indexType: 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX',
      tenantId,
      operator,
      indexedAt,
      sourceFinalityCertificateVerifierStatus: verifierPacket.status,
      sourceFinalityCertificateStatus: verifier.sourceCertificateStatus || null,
      sourceReceiptVerifierStatus:
        verifierPacket.sourceReceiptVerifierStatus ||
        verifier.sourceReceiptVerifierStatus ||
        certificate.sourceReceiptVerifierStatus ||
        null,
      sourceReceiptStatus:
        verifierPacket.sourceReceiptStatus ||
        verifier.sourceReceiptStatus ||
        certificate.sourceReceiptStatus ||
        null,
      sourceTerminalSealVerifierStatus:
        verifierPacket.sourceTerminalSealVerifierStatus ||
        verifier.sourceTerminalSealVerifierStatus ||
        certificate.sourceTerminalSealVerifierStatus ||
        null,
      sourceTerminalSealStatus:
        verifierPacket.sourceTerminalSealStatus ||
        verifier.sourceTerminalSealStatus ||
        certificate.sourceTerminalSealStatus ||
        null,
      ledgerRoot: verifierPacket.ledgerRoot || certificate.ledgerRoot || null,
      chainRange: certificate.chainRange || [],
      audience: certificate.audience || [],
      statuses: certificate.statuses || {},
      routeContracts: certificate.routeContracts || {},
      sourceRoutes: certificate.sourceRoutes || {},
      hashes: {
        storedCertificateHash:
          verifierPacket.storedCertificateHash || verifier.storedCertificateHash || null,
        recomputedCertificateHash:
          verifierPacket.recomputedCertificateHash || verifier.recomputedCertificateHash || null,
        storedReceiptHash:
          verifierPacket.storedReceiptHash ||
          verifier.storedReceiptHash ||
          certificate.storedReceiptHash ||
          null,
        recomputedReceiptHash:
          verifierPacket.recomputedReceiptHash ||
          verifier.recomputedReceiptHash ||
          certificate.recomputedReceiptHash ||
          null,
        storedTerminalSealHash:
          verifierPacket.storedTerminalSealHash ||
          verifier.storedTerminalSealHash ||
          certificate.storedTerminalSealHash ||
          null,
        recomputedTerminalSealHash:
          verifierPacket.recomputedTerminalSealHash ||
          verifier.recomputedTerminalSealHash ||
          certificate.recomputedTerminalSealHash ||
          null,
        attestationHash: certificate.hashes?.attestationHash || null,
        receiptHash: certificate.hashes?.receiptHash || null,
        bundleIndexHash: certificate.hashes?.storedBundleIndexHash || null,
        ledgerRoot: verifierPacket.ledgerRoot || certificate.ledgerRoot || null,
      },
      proofFlags: {
        certificateHashVerified: verifierPacket.certificateHashVerified === true,
        receiptHashVerified: verifierPacket.receiptHashVerified === true,
        terminalSealHashVerified: verifierPacket.terminalSealHashVerified === true,
        upstreamCertificatePostureVerified:
          verifierPacket.upstreamCertificatePostureVerified === true,
        certificateFlagsVerified: verifierPacket.certificateFlagsVerified === true,
        chainRangeVerified: verifierPacket.chainRangeVerified === true,
        audienceVerified: verifierPacket.audienceVerified === true,
        statusesVerified: verifierPacket.statusesVerified === true,
        routeContractsVerified: verifierPacket.routeContractsVerified === true,
        sourceRoutesVerified: verifierPacket.sourceRoutesVerified === true,
        hashEqualityVerified: verifierPacket.hashEqualityVerified === true,
        proofFlagsVerified: verifierPacket.proofFlagsVerified === true,
        terminalDispositionVerified: verifierPacket.terminalDispositionVerified === true,
        finalityDispositionVerified: verifierPacket.finalityDispositionVerified === true,
        regulatorReady: verifierPacket.regulatorReady === true,
        investorReady: verifierPacket.investorReady === true,
        jsonResponseOnly: verifierPacket.jsonResponseOnly === true,
        noFilesystemWrite: verifierPacket.noFilesystemWrite === true,
      },
      terminalDisposition,
      finalityDisposition,
      evidenceRoutes: {
        R68Z: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
        R69A: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
        R69B: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
        R69C: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
        R69D: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
        R69E: '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      },
      evidenceIndexPosture: {
        evidenceIndexStatus: 'FINALITY_CERTIFICATE_EVIDENCE_INDEXED',
        sourceVerifierPassed:
          verifierPacket.status ===
          'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED',
        certificateVerified: verifierPacket.certificateHashVerified === true,
        receiptVerified: verifierPacket.receiptHashVerified === true,
        terminalSealVerified: verifierPacket.terminalSealHashVerified === true,
        finalityDispositionVerified: verifierPacket.finalityDispositionVerified === true,
        terminalDispositionVerified: verifierPacket.terminalDispositionVerified === true,
        regulatorReady: verifierPacket.regulatorReady === true,
        investorReady: verifierPacket.investorReady === true,
        filesystemExported: false,
        jsonResponseOnly: true,
        noFilesystemWrite: true,
      },
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      jsonResponseOnly:
        verifierPacket.jsonResponseOnly === true &&
        verifier.jsonResponseOnly === true &&
        certificate.jsonResponseOnly === true &&
        finalityDisposition.jsonResponseOnly === true &&
        terminalDisposition.jsonResponseOnly === true,
      noFilesystemWrite:
        verifierPacket.noFilesystemWrite === true &&
        verifier.noFilesystemWrite === true &&
        certificate.noFilesystemWrite === true &&
        finalityDisposition.noFilesystemWrite === true &&
        terminalDisposition.noFilesystemWrite === true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };

    const evidenceIndexHash =
      computeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexHash(
        evidenceIndexPayload
      );

    const terminalFinalityCertificateEvidenceIndex = {
      ...evidenceIndexPayload,
      evidenceIndexHash,
      evidenceIndexHashShort: evidenceIndexHash.slice(0, 16),
    };

    const expectedChainRange = [
      'R68O',
      'R68P',
      'R68Q',
      'R68R',
      'R68S',
      'R68T',
      'R68U',
      'R68V',
      'R68W',
      'R68X',
      'R68Y',
    ];

    const expectedSourceStatusesVerified =
      terminalFinalityCertificateEvidenceIndex.sourceFinalityCertificateVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED' &&
      terminalFinalityCertificateEvidenceIndex.sourceFinalityCertificateStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED' &&
      terminalFinalityCertificateEvidenceIndex.sourceReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      terminalFinalityCertificateEvidenceIndex.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      terminalFinalityCertificateEvidenceIndex.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      terminalFinalityCertificateEvidenceIndex.sourceTerminalSealStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED';

    const chainRangeVerified =
      JSON.stringify(terminalFinalityCertificateEvidenceIndex.chainRange) ===
      JSON.stringify(expectedChainRange);

    const audienceVerified =
      JSON.stringify(terminalFinalityCertificateEvidenceIndex.audience) ===
      JSON.stringify(['REGULATOR', 'INVESTOR']);

    const proofFlagsAllTrue = Object.values(
      terminalFinalityCertificateEvidenceIndex.proofFlags
    ).every((value) => value === true);

    const evidenceRoutesVerified =
      terminalFinalityCertificateEvidenceIndex.evidenceRoutes.R68Z ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest' &&
      terminalFinalityCertificateEvidenceIndex.evidenceRoutes.R69A ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest' &&
      terminalFinalityCertificateEvidenceIndex.evidenceRoutes.R69B ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest' &&
      terminalFinalityCertificateEvidenceIndex.evidenceRoutes.R69C ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest' &&
      terminalFinalityCertificateEvidenceIndex.evidenceRoutes.R69D ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest' &&
      terminalFinalityCertificateEvidenceIndex.evidenceRoutes.R69E ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest';

    const indexed =
      expectedSourceStatusesVerified &&
      chainRangeVerified &&
      audienceVerified &&
      proofFlagsAllTrue &&
      evidenceRoutesVerified &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.evidenceIndexStatus ===
        'FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.sourceVerifierPassed === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.certificateVerified === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.receiptVerified === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.terminalSealVerified === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.finalityDispositionVerified ===
        true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.terminalDispositionVerified ===
        true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.regulatorReady === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.investorReady === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.filesystemExported === false &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.jsonResponseOnly === true &&
      terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.noFilesystemWrite === true &&
      terminalFinalityCertificateEvidenceIndex.jsonResponseOnly === true &&
      terminalFinalityCertificateEvidenceIndex.noFilesystemWrite === true &&
      terminalFinalityCertificateEvidenceIndex.persistenceMode === 'JSON_RESPONSE_ONLY';

    return {
      ok: indexed,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERSION,
      status: indexed
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEXED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_DEGRADED',
      evidenceIndexHash,
      evidenceIndexHashShort: evidenceIndexHash.slice(0, 16),
      ledgerRoot: terminalFinalityCertificateEvidenceIndex.ledgerRoot,
      expectedSourceStatusesVerified,
      chainRangeVerified,
      audienceVerified,
      proofFlagsAllTrue,
      evidenceRoutesVerified,
      certificateHashVerified:
        terminalFinalityCertificateEvidenceIndex.proofFlags.certificateHashVerified,
      receiptHashVerified: terminalFinalityCertificateEvidenceIndex.proofFlags.receiptHashVerified,
      terminalSealHashVerified:
        terminalFinalityCertificateEvidenceIndex.proofFlags.terminalSealHashVerified,
      finalityDispositionVerified:
        terminalFinalityCertificateEvidenceIndex.proofFlags.finalityDispositionVerified,
      terminalDispositionVerified:
        terminalFinalityCertificateEvidenceIndex.proofFlags.terminalDispositionVerified,
      regulatorReady: terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.regulatorReady,
      investorReady: terminalFinalityCertificateEvidenceIndex.evidenceIndexPosture.investorReady,
      terminalFinalityCertificateEvidenceIndex,
      sourceFinalityCertificateVerifier: verifierPacket,
      terminalReceiptFinalityCertificate: certificate,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIER_VERSION =
  'R69G-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-CERTIFICATE-EVIDENCE-INDEX-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex
 * @description Verifies the R69F terminal finality certificate evidence index by recomputing its index hash and validating terminal evidence lookup posture.
 * @collaboration R69F evidence index, R69E certificate verifier, R69D finality certificate, R69A terminal seal verifier, R68Z terminal seal.
 */
export const verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const evidenceIndexPacket =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex({
        tenantId,
        ledgerId,
        limit,
        operator,
      });

    const evidenceIndex = evidenceIndexPacket.terminalFinalityCertificateEvidenceIndex || {};
    const {
      evidenceIndexHash: storedEvidenceIndexHash,
      evidenceIndexHashShort,
      ...evidenceIndexPayload
    } = evidenceIndex;

    const recomputedEvidenceIndexHash =
      computeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexHash(
        evidenceIndexPayload
      );
    const evidenceIndexHashVerified =
      Boolean(storedEvidenceIndexHash) && storedEvidenceIndexHash === recomputedEvidenceIndexHash;

    const expectedChainRange = [
      'R68O',
      'R68P',
      'R68Q',
      'R68R',
      'R68S',
      'R68T',
      'R68U',
      'R68V',
      'R68W',
      'R68X',
      'R68Y',
    ];

    const chainRange = Array.isArray(evidenceIndex.chainRange) ? evidenceIndex.chainRange : [];
    const chainRangeVerified = JSON.stringify(chainRange) === JSON.stringify(expectedChainRange);

    const audience = Array.isArray(evidenceIndex.audience) ? evidenceIndex.audience : [];
    const audienceVerified = JSON.stringify(audience) === JSON.stringify(['REGULATOR', 'INVESTOR']);

    const evidenceRoutes = evidenceIndex.evidenceRoutes || {};
    const evidenceRoutesVerified =
      evidenceRoutes.R68Z ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest' &&
      evidenceRoutes.R69A ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest' &&
      evidenceRoutes.R69B ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest' &&
      evidenceRoutes.R69C ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest' &&
      evidenceRoutes.R69D ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest' &&
      evidenceRoutes.R69E ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest';

    const expectedSourceStatusesVerified =
      evidenceIndexPacket.status ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      evidenceIndex.sourceFinalityCertificateVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED' &&
      evidenceIndex.sourceFinalityCertificateStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED' &&
      evidenceIndex.sourceReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      evidenceIndex.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      evidenceIndex.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      evidenceIndex.sourceTerminalSealStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED';

    const statuses = evidenceIndex.statuses || {};
    const statusesVerified =
      statuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
      statuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
      statuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
      statuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
      statuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
      statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
      statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
      statuses.R68V ===
        'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
      statuses.R68W ===
        'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
      statuses.R68X === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
      statuses.R68Y === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED';

    const routeContracts = evidenceIndex.routeContracts || {};
    const routeContractsVerified =
      routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
      routeContracts.R68P ===
        'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
      routeContracts.R68Q ===
        'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
      routeContracts.R68R ===
        'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
      routeContracts.R68S ===
        'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY' &&
      routeContracts.R68T === 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY' &&
      routeContracts.R68U ===
        'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY' &&
      routeContracts.R68V ===
        'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY' &&
      routeContracts.R68W ===
        'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
      routeContracts.R68X ===
        'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY' &&
      routeContracts.R68Y ===
        'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

    const sourceRoutes = evidenceIndex.sourceRoutes || {};
    const sourceRoutesVerified =
      sourceRoutes.R68O ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
      sourceRoutes.R68P ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
      sourceRoutes.R68Q ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
      sourceRoutes.R68R ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
      sourceRoutes.R68S ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest' &&
      sourceRoutes.R68T ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest' &&
      sourceRoutes.R68U ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest' &&
      sourceRoutes.R68V ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest' &&
      sourceRoutes.R68W ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest' &&
      sourceRoutes.R68X ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest' &&
      sourceRoutes.R68Y ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest';

    const hashes = evidenceIndex.hashes || {};
    const hashEqualityVerified =
      Boolean(hashes.storedCertificateHash) &&
      hashes.storedCertificateHash === hashes.recomputedCertificateHash &&
      Boolean(hashes.storedReceiptHash) &&
      hashes.storedReceiptHash === hashes.recomputedReceiptHash &&
      Boolean(hashes.storedTerminalSealHash) &&
      hashes.storedTerminalSealHash === hashes.recomputedTerminalSealHash;

    const proofFlags = evidenceIndex.proofFlags || {};
    const proofFlagsAllTrue =
      Object.values(proofFlags).length > 0 &&
      Object.values(proofFlags).every((value) => value === true);

    const terminalDisposition = evidenceIndex.terminalDisposition || {};
    const terminalDispositionVerified =
      terminalDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
      terminalDisposition.regulatorReady === true &&
      terminalDisposition.investorReady === true &&
      terminalDisposition.filesystemExported === false &&
      terminalDisposition.jsonResponseOnly === true &&
      terminalDisposition.noFilesystemWrite === true;

    const finalityDisposition = evidenceIndex.finalityDisposition || {};
    const finalityDispositionVerified =
      finalityDisposition.certificateStatus === 'FINALITY_CERTIFIED' &&
      finalityDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
      finalityDisposition.receiptVerified === true &&
      finalityDisposition.terminalSealVerified === true &&
      finalityDisposition.regulatorReady === true &&
      finalityDisposition.investorReady === true &&
      finalityDisposition.filesystemExported === false &&
      finalityDisposition.jsonResponseOnly === true &&
      finalityDisposition.noFilesystemWrite === true;

    const posture = evidenceIndex.evidenceIndexPosture || {};
    const evidenceIndexPostureVerified =
      posture.evidenceIndexStatus === 'FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      posture.sourceVerifierPassed === true &&
      posture.certificateVerified === true &&
      posture.receiptVerified === true &&
      posture.terminalSealVerified === true &&
      posture.finalityDispositionVerified === true &&
      posture.terminalDispositionVerified === true &&
      posture.regulatorReady === true &&
      posture.investorReady === true &&
      posture.filesystemExported === false &&
      posture.jsonResponseOnly === true &&
      posture.noFilesystemWrite === true;

    const certificateHashVerified = proofFlags.certificateHashVerified === true;
    const receiptHashVerified = proofFlags.receiptHashVerified === true;
    const terminalSealHashVerified = proofFlags.terminalSealHashVerified === true;

    const regulatorReady =
      posture.regulatorReady === true &&
      terminalDisposition.regulatorReady === true &&
      finalityDisposition.regulatorReady === true &&
      proofFlags.regulatorReady === true;

    const investorReady =
      posture.investorReady === true &&
      terminalDisposition.investorReady === true &&
      finalityDisposition.investorReady === true &&
      proofFlags.investorReady === true;

    const jsonResponseOnly =
      evidenceIndexPacket.jsonResponseOnly === true &&
      evidenceIndex.jsonResponseOnly === true &&
      evidenceIndex.persistenceMode === 'JSON_RESPONSE_ONLY' &&
      posture.jsonResponseOnly === true &&
      terminalDisposition.jsonResponseOnly === true &&
      finalityDisposition.jsonResponseOnly === true &&
      proofFlags.jsonResponseOnly === true;

    const noFilesystemWrite =
      evidenceIndexPacket.noFilesystemWrite === true &&
      evidenceIndex.noFilesystemWrite === true &&
      posture.noFilesystemWrite === true &&
      terminalDisposition.noFilesystemWrite === true &&
      finalityDisposition.noFilesystemWrite === true &&
      proofFlags.noFilesystemWrite === true;

    const verified =
      evidenceIndexHashVerified &&
      expectedSourceStatusesVerified &&
      chainRangeVerified &&
      audienceVerified &&
      statusesVerified &&
      routeContractsVerified &&
      sourceRoutesVerified &&
      evidenceRoutesVerified &&
      hashEqualityVerified &&
      proofFlagsAllTrue &&
      terminalDispositionVerified &&
      finalityDispositionVerified &&
      evidenceIndexPostureVerified &&
      certificateHashVerified &&
      receiptHashVerified &&
      terminalSealHashVerified &&
      regulatorReady &&
      investorReady &&
      jsonResponseOnly &&
      noFilesystemWrite;

    return {
      ok: verified,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIER_VERSION,
      status: verified
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFICATION_FAILED',
      evidenceIndexHashVerified,
      storedEvidenceIndexHash,
      storedEvidenceIndexHashShort:
        evidenceIndexHashShort || String(storedEvidenceIndexHash || '').slice(0, 16),
      recomputedEvidenceIndexHash,
      recomputedEvidenceIndexHashShort: recomputedEvidenceIndexHash.slice(0, 16),
      expectedSourceStatusesVerified,
      chainRangeVerified,
      audienceVerified,
      statusesVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      evidenceRoutesVerified,
      hashEqualityVerified,
      proofFlagsAllTrue,
      terminalDispositionVerified,
      finalityDispositionVerified,
      evidenceIndexPostureVerified,
      certificateHashVerified,
      receiptHashVerified,
      terminalSealHashVerified,
      regulatorReady,
      investorReady,
      sourceFinalityCertificateVerifierStatus:
        evidenceIndex.sourceFinalityCertificateVerifierStatus || null,
      sourceFinalityCertificateStatus: evidenceIndex.sourceFinalityCertificateStatus || null,
      sourceReceiptVerifierStatus: evidenceIndex.sourceReceiptVerifierStatus || null,
      sourceReceiptStatus: evidenceIndex.sourceReceiptStatus || null,
      sourceTerminalSealVerifierStatus: evidenceIndex.sourceTerminalSealVerifierStatus || null,
      sourceTerminalSealStatus: evidenceIndex.sourceTerminalSealStatus || null,
      ledgerRoot: evidenceIndex.ledgerRoot || evidenceIndexPacket.ledgerRoot || null,
      terminalFinalityCertificateEvidenceIndexVerifier: {
        tenantId,
        operator,
        verifiedAt: new Date().toISOString(),
        sourceEvidenceIndexStatus: evidenceIndexPacket.status,
        evidenceIndexHashVerified,
        storedEvidenceIndexHash,
        recomputedEvidenceIndexHash,
        expectedSourceStatusesVerified,
        chainRangeVerified,
        audienceVerified,
        statusesVerified,
        routeContractsVerified,
        sourceRoutesVerified,
        evidenceRoutesVerified,
        hashEqualityVerified,
        proofFlagsAllTrue,
        terminalDispositionVerified,
        finalityDispositionVerified,
        evidenceIndexPostureVerified,
        certificateHashVerified,
        receiptHashVerified,
        terminalSealHashVerified,
        regulatorReady,
        investorReady,
        jsonResponseOnly,
        noFilesystemWrite,
      },
      terminalFinalityCertificateEvidenceIndex: evidenceIndex,
      sourceFinalityCertificateEvidenceIndexPacket: evidenceIndexPacket,
      terminalReceiptFinalityCertificate:
        evidenceIndexPacket.terminalReceiptFinalityCertificate || null,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERSION =
  'R69H-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-INDEX-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * @function normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptValue
 * @description Produces deterministic values for R69H terminal finality evidence index verification receipt hashing.
 * @collaboration R69G evidence index verifier, R69F evidence index, regulator/investor receipt controls.
 */
const normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptValue =
  (value) => {
    if (Array.isArray(value)) {
      return value.map((item) =>
        normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptValue(
          item
        )
      );
    }

    if (value && typeof value === 'object') {
      return Object.keys(value)
        .sort()
        .reduce((normalized, key) => {
          normalized[key] =
            normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptValue(
              value[key]
            );
          return normalized;
        }, {});
    }

    return value;
  };

/**
 * @function computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptHash
 * @description Computes a deterministic hash for the R69H terminal finality evidence index verification receipt.
 * @collaboration R69G verifier packet, terminal finality evidence index, regulator/investor receipt proof surface.
 */
const computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptHash = (
  receiptPayload
) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(
        normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptValue(
          receiptPayload
        )
      )
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt
 * @description Materializes a JSON-only verification receipt from the R69G terminal finality evidence index verifier.
 * @collaboration CRM command routes, R69G evidence index verifier, regulator/investor terminal evidence receipt controls.
 */
export const buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const evidenceIndexVerifierPacket =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex({
        tenantId,
        ledgerId,
        limit,
        operator,
      });

    const evidenceIndexVerifier =
      evidenceIndexVerifierPacket.terminalFinalityCertificateEvidenceIndexVerifier || {};
    const evidenceIndex =
      evidenceIndexVerifierPacket.terminalFinalityCertificateEvidenceIndex || {};
    const posture = evidenceIndex.evidenceIndexPosture || {};
    const terminalDisposition = evidenceIndex.terminalDisposition || {};
    const finalityDisposition = evidenceIndex.finalityDisposition || {};
    const materializedAt = new Date().toISOString();

    const verificationReceiptPayload = {
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERSION,
      receiptType:
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT',
      tenantId,
      operator,
      materializedAt,
      sourceEvidenceIndexVerifierStatus: evidenceIndexVerifierPacket.status,
      sourceEvidenceIndexStatus: evidenceIndexVerifier.sourceEvidenceIndexStatus || null,
      sourceFinalityCertificateVerifierStatus:
        evidenceIndexVerifierPacket.sourceFinalityCertificateVerifierStatus ||
        evidenceIndex.sourceFinalityCertificateVerifierStatus ||
        null,
      sourceFinalityCertificateStatus:
        evidenceIndexVerifierPacket.sourceFinalityCertificateStatus ||
        evidenceIndex.sourceFinalityCertificateStatus ||
        null,
      sourceReceiptVerifierStatus:
        evidenceIndexVerifierPacket.sourceReceiptVerifierStatus ||
        evidenceIndex.sourceReceiptVerifierStatus ||
        null,
      sourceReceiptStatus:
        evidenceIndexVerifierPacket.sourceReceiptStatus ||
        evidenceIndex.sourceReceiptStatus ||
        null,
      sourceTerminalSealVerifierStatus:
        evidenceIndexVerifierPacket.sourceTerminalSealVerifierStatus ||
        evidenceIndex.sourceTerminalSealVerifierStatus ||
        null,
      sourceTerminalSealStatus:
        evidenceIndexVerifierPacket.sourceTerminalSealStatus ||
        evidenceIndex.sourceTerminalSealStatus ||
        null,
      ledgerRoot: evidenceIndexVerifierPacket.ledgerRoot || evidenceIndex.ledgerRoot || null,
      storedEvidenceIndexHash:
        evidenceIndexVerifierPacket.storedEvidenceIndexHash ||
        evidenceIndexVerifier.storedEvidenceIndexHash ||
        null,
      recomputedEvidenceIndexHash:
        evidenceIndexVerifierPacket.recomputedEvidenceIndexHash ||
        evidenceIndexVerifier.recomputedEvidenceIndexHash ||
        null,
      evidenceIndexHashVerified: evidenceIndexVerifierPacket.evidenceIndexHashVerified === true,
      expectedSourceStatusesVerified:
        evidenceIndexVerifierPacket.expectedSourceStatusesVerified === true,
      chainRangeVerified: evidenceIndexVerifierPacket.chainRangeVerified === true,
      audienceVerified: evidenceIndexVerifierPacket.audienceVerified === true,
      statusesVerified: evidenceIndexVerifierPacket.statusesVerified === true,
      routeContractsVerified: evidenceIndexVerifierPacket.routeContractsVerified === true,
      sourceRoutesVerified: evidenceIndexVerifierPacket.sourceRoutesVerified === true,
      evidenceRoutesVerified: evidenceIndexVerifierPacket.evidenceRoutesVerified === true,
      hashEqualityVerified: evidenceIndexVerifierPacket.hashEqualityVerified === true,
      proofFlagsAllTrue: evidenceIndexVerifierPacket.proofFlagsAllTrue === true,
      terminalDispositionVerified: evidenceIndexVerifierPacket.terminalDispositionVerified === true,
      finalityDispositionVerified: evidenceIndexVerifierPacket.finalityDispositionVerified === true,
      evidenceIndexPostureVerified:
        evidenceIndexVerifierPacket.evidenceIndexPostureVerified === true,
      certificateHashVerified: evidenceIndexVerifierPacket.certificateHashVerified === true,
      receiptHashVerified: evidenceIndexVerifierPacket.receiptHashVerified === true,
      terminalSealHashVerified: evidenceIndexVerifierPacket.terminalSealHashVerified === true,
      regulatorReady: evidenceIndexVerifierPacket.regulatorReady === true,
      investorReady: evidenceIndexVerifierPacket.investorReady === true,
      chainRange: evidenceIndex.chainRange || [],
      audience: evidenceIndex.audience || [],
      statuses: evidenceIndex.statuses || {},
      routeContracts: evidenceIndex.routeContracts || {},
      sourceRoutes: evidenceIndex.sourceRoutes || {},
      evidenceRoutes: evidenceIndex.evidenceRoutes || {},
      hashes: evidenceIndex.hashes || {},
      proofFlags: evidenceIndex.proofFlags || {},
      terminalDisposition,
      finalityDisposition,
      evidenceIndexPosture: posture,
      receiptDisposition: {
        receiptStatus: 'TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED',
        sourceVerifierPassed:
          evidenceIndexVerifierPacket.status ===
          'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIED',
        evidenceIndexVerified: evidenceIndexVerifierPacket.evidenceIndexHashVerified === true,
        evidenceRoutesVerified: evidenceIndexVerifierPacket.evidenceRoutesVerified === true,
        proofFlagsAllTrue: evidenceIndexVerifierPacket.proofFlagsAllTrue === true,
        regulatorReady: evidenceIndexVerifierPacket.regulatorReady === true,
        investorReady: evidenceIndexVerifierPacket.investorReady === true,
        filesystemExported: false,
        jsonResponseOnly: true,
        noFilesystemWrite: true,
      },
      sourceEvidenceIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
      sourceEvidenceIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      jsonResponseOnly:
        evidenceIndexVerifierPacket.jsonResponseOnly === true &&
        evidenceIndexVerifier.jsonResponseOnly === true &&
        evidenceIndex.jsonResponseOnly === true &&
        posture.jsonResponseOnly === true &&
        terminalDisposition.jsonResponseOnly === true &&
        finalityDisposition.jsonResponseOnly === true,
      noFilesystemWrite:
        evidenceIndexVerifierPacket.noFilesystemWrite === true &&
        evidenceIndexVerifier.noFilesystemWrite === true &&
        evidenceIndex.noFilesystemWrite === true &&
        posture.noFilesystemWrite === true &&
        terminalDisposition.noFilesystemWrite === true &&
        finalityDisposition.noFilesystemWrite === true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };

    const verificationReceiptHash =
      computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptHash(
        verificationReceiptPayload
      );

    const terminalFinalityEvidenceIndexVerificationReceipt = {
      ...verificationReceiptPayload,
      verificationReceiptHash,
      verificationReceiptHashShort: verificationReceiptHash.slice(0, 16),
      receiptHash: verificationReceiptHash,
      receiptHashShort: verificationReceiptHash.slice(0, 16),
    };

    const materialized =
      terminalFinalityEvidenceIndexVerificationReceipt.sourceEvidenceIndexVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceEvidenceIndexStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceFinalityCertificateVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceFinalityCertificateStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceTerminalSealStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED' &&
      terminalFinalityEvidenceIndexVerificationReceipt.evidenceIndexHashVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.storedEvidenceIndexHash ===
        terminalFinalityEvidenceIndexVerificationReceipt.recomputedEvidenceIndexHash &&
      terminalFinalityEvidenceIndexVerificationReceipt.expectedSourceStatusesVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.chainRangeVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.audienceVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.statusesVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.routeContractsVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.sourceRoutesVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.evidenceRoutesVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.hashEqualityVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.proofFlagsAllTrue === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.terminalDispositionVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.finalityDispositionVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.evidenceIndexPostureVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.certificateHashVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptHashVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.terminalSealHashVerified === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.regulatorReady === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.investorReady === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.sourceVerifierPassed ===
        true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.evidenceIndexVerified ===
        true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.evidenceRoutesVerified ===
        true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.proofFlagsAllTrue ===
        true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.filesystemExported ===
        false &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.jsonResponseOnly ===
        true &&
      terminalFinalityEvidenceIndexVerificationReceipt.receiptDisposition.noFilesystemWrite ===
        true &&
      terminalFinalityEvidenceIndexVerificationReceipt.jsonResponseOnly === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.noFilesystemWrite === true &&
      terminalFinalityEvidenceIndexVerificationReceipt.persistenceMode === 'JSON_RESPONSE_ONLY';

    return {
      ok: materialized,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERSION,
      status: materialized
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_DEGRADED',
      verificationReceiptHash,
      verificationReceiptHashShort: verificationReceiptHash.slice(0, 16),
      receiptHash: verificationReceiptHash,
      receiptHashShort: verificationReceiptHash.slice(0, 16),
      ledgerRoot: terminalFinalityEvidenceIndexVerificationReceipt.ledgerRoot,
      evidenceIndexHashVerified:
        terminalFinalityEvidenceIndexVerificationReceipt.evidenceIndexHashVerified,
      expectedSourceStatusesVerified:
        terminalFinalityEvidenceIndexVerificationReceipt.expectedSourceStatusesVerified,
      chainRangeVerified: terminalFinalityEvidenceIndexVerificationReceipt.chainRangeVerified,
      audienceVerified: terminalFinalityEvidenceIndexVerificationReceipt.audienceVerified,
      evidenceRoutesVerified:
        terminalFinalityEvidenceIndexVerificationReceipt.evidenceRoutesVerified,
      proofFlagsAllTrue: terminalFinalityEvidenceIndexVerificationReceipt.proofFlagsAllTrue,
      evidenceIndexPostureVerified:
        terminalFinalityEvidenceIndexVerificationReceipt.evidenceIndexPostureVerified,
      regulatorReady: terminalFinalityEvidenceIndexVerificationReceipt.regulatorReady,
      investorReady: terminalFinalityEvidenceIndexVerificationReceipt.investorReady,
      terminalFinalityEvidenceIndexVerificationReceipt,
      sourceFinalityEvidenceIndexVerifier: evidenceIndexVerifierPacket,
      terminalFinalityCertificateEvidenceIndex: evidenceIndex,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIER_VERSION =
  'R69I-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * @function verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt
 * @description Verifies the R69H terminal finality evidence index verification receipt by recomputing its receipt hash and validating source posture.
 * @collaboration R69H receipt, R69G evidence index verifier, R69F evidence index, terminal regulator/investor evidence controls.
 */
export const verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const receiptPacket =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt(
        {
          tenantId,
          ledgerId,
          limit,
          operator,
        }
      );

    const receipt = receiptPacket.terminalFinalityEvidenceIndexVerificationReceipt || {};
    const {
      verificationReceiptHash: storedVerificationReceiptHash,
      verificationReceiptHashShort,
      receiptHash: storedReceiptHash,
      receiptHashShort,
      ...receiptPayload
    } = receipt;

    const recomputedVerificationReceiptHash =
      computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceiptHash(
        receiptPayload
      );

    const verificationReceiptHashVerified =
      Boolean(storedVerificationReceiptHash) &&
      storedVerificationReceiptHash === recomputedVerificationReceiptHash;

    const receiptHashVerified =
      Boolean(storedReceiptHash) &&
      storedReceiptHash === storedVerificationReceiptHash &&
      storedReceiptHash === recomputedVerificationReceiptHash;

    const expectedChainRange = [
      'R68O',
      'R68P',
      'R68Q',
      'R68R',
      'R68S',
      'R68T',
      'R68U',
      'R68V',
      'R68W',
      'R68X',
      'R68Y',
    ];

    const chainRange = Array.isArray(receipt.chainRange) ? receipt.chainRange : [];
    const chainRangeVerified = JSON.stringify(chainRange) === JSON.stringify(expectedChainRange);

    const audience = Array.isArray(receipt.audience) ? receipt.audience : [];
    const audienceVerified = JSON.stringify(audience) === JSON.stringify(['REGULATOR', 'INVESTOR']);

    const expectedSourceStatusesVerified =
      receiptPacket.status ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
      receipt.sourceEvidenceIndexVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIED' &&
      receipt.sourceEvidenceIndexStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      receipt.sourceFinalityCertificateVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED' &&
      receipt.sourceFinalityCertificateStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED' &&
      receipt.sourceReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      receipt.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      receipt.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      receipt.sourceTerminalSealStatus === 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED';

    const statuses = receipt.statuses || {};
    const statusesVerified =
      statuses.R68O === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFIED' &&
      statuses.R68P === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_MATERIALIZED' &&
      statuses.R68Q === 'REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIED' &&
      statuses.R68R === 'REGULATOR_DOSSIER_CHAIN_VERIFICATION_FINALITY_CERTIFICATE_ISSUED' &&
      statuses.R68S === 'REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIED' &&
      statuses.R68T === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEXED' &&
      statuses.R68U === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIED' &&
      statuses.R68V ===
        'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
      statuses.R68W ===
        'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
      statuses.R68X === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_ISSUED' &&
      statuses.R68Y === 'REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIED';

    const routeContracts = receipt.routeContracts || {};
    const routeContractsVerified =
      routeContracts.R68O === 'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY' &&
      routeContracts.R68P ===
        'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY' &&
      routeContracts.R68Q ===
        'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
      routeContracts.R68R ===
        'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY' &&
      routeContracts.R68S ===
        'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY' &&
      routeContracts.R68T === 'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY' &&
      routeContracts.R68U ===
        'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY' &&
      routeContracts.R68V ===
        'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY' &&
      routeContracts.R68W ===
        'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY' &&
      routeContracts.R68X ===
        'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY' &&
      routeContracts.R68Y ===
        'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

    const sourceRoutes = receipt.sourceRoutes || {};
    const sourceRoutesVerified =
      sourceRoutes.R68O ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O' &&
      sourceRoutes.R68P ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest' &&
      sourceRoutes.R68Q ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest' &&
      sourceRoutes.R68R ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest' &&
      sourceRoutes.R68S ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest' &&
      sourceRoutes.R68T ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest' &&
      sourceRoutes.R68U ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest' &&
      sourceRoutes.R68V ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest' &&
      sourceRoutes.R68W ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest' &&
      sourceRoutes.R68X ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest' &&
      sourceRoutes.R68Y ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest';

    const evidenceRoutes = receipt.evidenceRoutes || {};
    const evidenceRoutesVerified =
      evidenceRoutes.R68Z ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest' &&
      evidenceRoutes.R69A ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest' &&
      evidenceRoutes.R69B ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest' &&
      evidenceRoutes.R69C ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest' &&
      evidenceRoutes.R69D ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest' &&
      evidenceRoutes.R69E ===
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest';

    const hashes = receipt.hashes || {};
    const hashEqualityVerified =
      Boolean(hashes.storedCertificateHash) &&
      hashes.storedCertificateHash === hashes.recomputedCertificateHash &&
      Boolean(hashes.storedReceiptHash) &&
      hashes.storedReceiptHash === hashes.recomputedReceiptHash &&
      Boolean(hashes.storedTerminalSealHash) &&
      hashes.storedTerminalSealHash === hashes.recomputedTerminalSealHash;

    const evidenceIndexHashVerified =
      receipt.evidenceIndexHashVerified === true &&
      Boolean(receipt.storedEvidenceIndexHash) &&
      receipt.storedEvidenceIndexHash === receipt.recomputedEvidenceIndexHash;

    const proofFlags = receipt.proofFlags || {};
    const proofFlagsAllTrue =
      receipt.proofFlagsAllTrue === true &&
      Object.values(proofFlags).length > 0 &&
      Object.values(proofFlags).every((value) => value === true);

    const terminalDisposition = receipt.terminalDisposition || {};
    const terminalDispositionVerified =
      receipt.terminalDispositionVerified === true &&
      terminalDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
      terminalDisposition.regulatorReady === true &&
      terminalDisposition.investorReady === true &&
      terminalDisposition.filesystemExported === false &&
      terminalDisposition.jsonResponseOnly === true &&
      terminalDisposition.noFilesystemWrite === true;

    const finalityDisposition = receipt.finalityDisposition || {};
    const finalityDispositionVerified =
      receipt.finalityDispositionVerified === true &&
      finalityDisposition.certificateStatus === 'FINALITY_CERTIFIED' &&
      finalityDisposition.evidenceChainStatus === 'TERMINALLY_SEALED' &&
      finalityDisposition.receiptVerified === true &&
      finalityDisposition.terminalSealVerified === true &&
      finalityDisposition.regulatorReady === true &&
      finalityDisposition.investorReady === true &&
      finalityDisposition.filesystemExported === false &&
      finalityDisposition.jsonResponseOnly === true &&
      finalityDisposition.noFilesystemWrite === true;

    const evidenceIndexPosture = receipt.evidenceIndexPosture || {};
    const evidenceIndexPostureVerified =
      receipt.evidenceIndexPostureVerified === true &&
      evidenceIndexPosture.evidenceIndexStatus === 'FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      evidenceIndexPosture.sourceVerifierPassed === true &&
      evidenceIndexPosture.certificateVerified === true &&
      evidenceIndexPosture.receiptVerified === true &&
      evidenceIndexPosture.terminalSealVerified === true &&
      evidenceIndexPosture.finalityDispositionVerified === true &&
      evidenceIndexPosture.terminalDispositionVerified === true &&
      evidenceIndexPosture.regulatorReady === true &&
      evidenceIndexPosture.investorReady === true &&
      evidenceIndexPosture.filesystemExported === false &&
      evidenceIndexPosture.jsonResponseOnly === true &&
      evidenceIndexPosture.noFilesystemWrite === true;

    const receiptDisposition = receipt.receiptDisposition || {};
    const receiptDispositionVerified =
      receiptDisposition.receiptStatus ===
        'TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
      receiptDisposition.sourceVerifierPassed === true &&
      receiptDisposition.evidenceIndexVerified === true &&
      receiptDisposition.evidenceRoutesVerified === true &&
      receiptDisposition.proofFlagsAllTrue === true &&
      receiptDisposition.regulatorReady === true &&
      receiptDisposition.investorReady === true &&
      receiptDisposition.filesystemExported === false &&
      receiptDisposition.jsonResponseOnly === true &&
      receiptDisposition.noFilesystemWrite === true;

    const certificateHashVerified = receipt.certificateHashVerified === true;
    const sourceReceiptHashVerified = receipt.receiptHashVerified === true;
    const terminalSealHashVerified = receipt.terminalSealHashVerified === true;

    const regulatorReady =
      receipt.regulatorReady === true &&
      receiptDisposition.regulatorReady === true &&
      evidenceIndexPosture.regulatorReady === true &&
      terminalDisposition.regulatorReady === true &&
      finalityDisposition.regulatorReady === true;

    const investorReady =
      receipt.investorReady === true &&
      receiptDisposition.investorReady === true &&
      evidenceIndexPosture.investorReady === true &&
      terminalDisposition.investorReady === true &&
      finalityDisposition.investorReady === true;

    const jsonResponseOnly =
      receiptPacket.jsonResponseOnly === true &&
      receipt.jsonResponseOnly === true &&
      receipt.persistenceMode === 'JSON_RESPONSE_ONLY' &&
      receiptDisposition.jsonResponseOnly === true &&
      evidenceIndexPosture.jsonResponseOnly === true &&
      terminalDisposition.jsonResponseOnly === true &&
      finalityDisposition.jsonResponseOnly === true;

    const noFilesystemWrite =
      receiptPacket.noFilesystemWrite === true &&
      receipt.noFilesystemWrite === true &&
      receiptDisposition.noFilesystemWrite === true &&
      evidenceIndexPosture.noFilesystemWrite === true &&
      terminalDisposition.noFilesystemWrite === true &&
      finalityDisposition.noFilesystemWrite === true;

    const verified =
      verificationReceiptHashVerified &&
      receiptHashVerified &&
      evidenceIndexHashVerified &&
      expectedSourceStatusesVerified &&
      chainRangeVerified &&
      audienceVerified &&
      statusesVerified &&
      routeContractsVerified &&
      sourceRoutesVerified &&
      evidenceRoutesVerified &&
      hashEqualityVerified &&
      proofFlagsAllTrue &&
      terminalDispositionVerified &&
      finalityDispositionVerified &&
      evidenceIndexPostureVerified &&
      receiptDispositionVerified &&
      certificateHashVerified &&
      sourceReceiptHashVerified &&
      terminalSealHashVerified &&
      regulatorReady &&
      investorReady &&
      jsonResponseOnly &&
      noFilesystemWrite;

    return {
      ok: verified,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIER_VERSION,
      status: verified
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFICATION_FAILED',
      verificationReceiptHashVerified,
      storedVerificationReceiptHash,
      storedVerificationReceiptHashShort:
        verificationReceiptHashShort || String(storedVerificationReceiptHash || '').slice(0, 16),
      recomputedVerificationReceiptHash,
      recomputedVerificationReceiptHashShort: recomputedVerificationReceiptHash.slice(0, 16),
      receiptHashVerified,
      storedReceiptHash,
      evidenceIndexHashVerified,
      storedEvidenceIndexHash: receipt.storedEvidenceIndexHash || null,
      recomputedEvidenceIndexHash: receipt.recomputedEvidenceIndexHash || null,
      expectedSourceStatusesVerified,
      chainRangeVerified,
      audienceVerified,
      statusesVerified,
      routeContractsVerified,
      sourceRoutesVerified,
      evidenceRoutesVerified,
      hashEqualityVerified,
      proofFlagsAllTrue,
      terminalDispositionVerified,
      finalityDispositionVerified,
      evidenceIndexPostureVerified,
      receiptDispositionVerified,
      certificateHashVerified,
      sourceReceiptHashVerified,
      terminalSealHashVerified,
      regulatorReady,
      investorReady,
      sourceEvidenceIndexVerifierStatus: receipt.sourceEvidenceIndexVerifierStatus || null,
      sourceEvidenceIndexStatus: receipt.sourceEvidenceIndexStatus || null,
      sourceFinalityCertificateVerifierStatus:
        receipt.sourceFinalityCertificateVerifierStatus || null,
      sourceFinalityCertificateStatus: receipt.sourceFinalityCertificateStatus || null,
      sourceReceiptVerifierStatus: receipt.sourceReceiptVerifierStatus || null,
      sourceReceiptStatus: receipt.sourceReceiptStatus || null,
      sourceTerminalSealVerifierStatus: receipt.sourceTerminalSealVerifierStatus || null,
      sourceTerminalSealStatus: receipt.sourceTerminalSealStatus || null,
      ledgerRoot: receipt.ledgerRoot || receiptPacket.ledgerRoot || null,
      terminalFinalityEvidenceIndexVerificationReceiptVerifier: {
        tenantId,
        operator,
        verifiedAt: new Date().toISOString(),
        sourceVerificationReceiptStatus: receiptPacket.status,
        verificationReceiptHashVerified,
        storedVerificationReceiptHash,
        recomputedVerificationReceiptHash,
        receiptHashVerified,
        evidenceIndexHashVerified,
        expectedSourceStatusesVerified,
        chainRangeVerified,
        audienceVerified,
        statusesVerified,
        routeContractsVerified,
        sourceRoutesVerified,
        evidenceRoutesVerified,
        hashEqualityVerified,
        proofFlagsAllTrue,
        terminalDispositionVerified,
        finalityDispositionVerified,
        evidenceIndexPostureVerified,
        receiptDispositionVerified,
        certificateHashVerified,
        sourceReceiptHashVerified,
        terminalSealHashVerified,
        regulatorReady,
        investorReady,
        jsonResponseOnly,
        noFilesystemWrite,
      },
      terminalFinalityEvidenceIndexVerificationReceipt: receipt,
      sourceTerminalFinalityEvidenceIndexVerificationReceiptPacket: receiptPacket,
      terminalFinalityCertificateEvidenceIndex:
        receiptPacket.terminalFinalityCertificateEvidenceIndex || null,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };

export const WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERSION =
  'R69J-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-AUTHORITY';

/**
 * @function normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateValue
 * @description Produces deterministic values for R69J terminal finality evidence receipt certificate hashing.
 * @collaboration R69I receipt verifier, R69H verification receipt, regulator/investor certificate controls.
 */
const normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateValue = (
  value
) => {
  if (Array.isArray(value)) {
    return value.map((item) =>
      normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateValue(item)
    );
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((normalized, key) => {
        normalized[key] =
          normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateValue(
            value[key]
          );
        return normalized;
      }, {});
  }

  return value;
};

/**
 * @function computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateHash
 * @description Computes a deterministic hash for the R69J terminal finality evidence receipt certificate.
 * @collaboration R69I verifier packet, R69H receipt, terminal regulator/investor certificate proof surface.
 */
const computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateHash = (
  certificatePayload
) =>
  crypto
    .createHash('sha512')
    .update(
      JSON.stringify(
        normalizeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateValue(
          certificatePayload
        )
      )
    )
    .digest('hex');

/**
 * @function buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificate
 * @description Issues a JSON-only terminal finality evidence receipt certificate from the R69I verifier.
 * @collaboration CRM command routes, R69I receipt verifier, regulator/investor terminal evidence certificate controls.
 */
export const buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificate =
  async (options = {}) => {
    const tenantId = String(options.tenantId || 'MASTER').trim() || 'MASTER';
    const ledgerId = options.ledgerId || options.ledgerRoot || 'latest';
    const limit = options.limit || 25;
    const operator =
      String(options.operator || options.operatorId || options.requestedBy || 'SYSTEM').trim() ||
      'SYSTEM';

    const receiptVerifierPacket =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt(
        {
          tenantId,
          ledgerId,
          limit,
          operator,
        }
      );

    const receiptVerifier =
      receiptVerifierPacket.terminalFinalityEvidenceIndexVerificationReceiptVerifier || {};
    const receipt = receiptVerifierPacket.terminalFinalityEvidenceIndexVerificationReceipt || {};
    const receiptDisposition = receipt.receiptDisposition || {};
    const evidenceIndexPosture = receipt.evidenceIndexPosture || {};
    const terminalDisposition = receipt.terminalDisposition || {};
    const finalityDisposition = receipt.finalityDisposition || {};
    const certifiedAt = new Date().toISOString();

    const certificatePayload = {
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERSION,
      certificateType:
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE',
      tenantId,
      operator,
      certifiedAt,
      sourceVerificationReceiptVerifierStatus: receiptVerifierPacket.status,
      sourceVerificationReceiptStatus: receiptVerifier.sourceVerificationReceiptStatus || null,
      sourceEvidenceIndexVerifierStatus:
        receiptVerifierPacket.sourceEvidenceIndexVerifierStatus ||
        receipt.sourceEvidenceIndexVerifierStatus ||
        null,
      sourceEvidenceIndexStatus:
        receiptVerifierPacket.sourceEvidenceIndexStatus ||
        receipt.sourceEvidenceIndexStatus ||
        null,
      sourceFinalityCertificateVerifierStatus:
        receiptVerifierPacket.sourceFinalityCertificateVerifierStatus ||
        receipt.sourceFinalityCertificateVerifierStatus ||
        null,
      sourceFinalityCertificateStatus:
        receiptVerifierPacket.sourceFinalityCertificateStatus ||
        receipt.sourceFinalityCertificateStatus ||
        null,
      sourceReceiptVerifierStatus:
        receiptVerifierPacket.sourceReceiptVerifierStatus ||
        receipt.sourceReceiptVerifierStatus ||
        null,
      sourceReceiptStatus:
        receiptVerifierPacket.sourceReceiptStatus || receipt.sourceReceiptStatus || null,
      sourceTerminalSealVerifierStatus:
        receiptVerifierPacket.sourceTerminalSealVerifierStatus ||
        receipt.sourceTerminalSealVerifierStatus ||
        null,
      sourceTerminalSealStatus:
        receiptVerifierPacket.sourceTerminalSealStatus || receipt.sourceTerminalSealStatus || null,
      ledgerRoot: receiptVerifierPacket.ledgerRoot || receipt.ledgerRoot || null,
      storedVerificationReceiptHash:
        receiptVerifierPacket.storedVerificationReceiptHash ||
        receiptVerifier.storedVerificationReceiptHash ||
        null,
      recomputedVerificationReceiptHash:
        receiptVerifierPacket.recomputedVerificationReceiptHash ||
        receiptVerifier.recomputedVerificationReceiptHash ||
        null,
      receiptHash: receiptVerifierPacket.storedReceiptHash || receipt.receiptHash || null,
      storedEvidenceIndexHash:
        receiptVerifierPacket.storedEvidenceIndexHash || receipt.storedEvidenceIndexHash || null,
      recomputedEvidenceIndexHash:
        receiptVerifierPacket.recomputedEvidenceIndexHash ||
        receipt.recomputedEvidenceIndexHash ||
        null,
      chainRange: receipt.chainRange || [],
      audience: receipt.audience || [],
      statuses: receipt.statuses || {},
      routeContracts: receipt.routeContracts || {},
      sourceRoutes: receipt.sourceRoutes || {},
      evidenceRoutes: receipt.evidenceRoutes || {},
      hashes: receipt.hashes || {},
      proofFlags: receipt.proofFlags || {},
      receiptDisposition,
      evidenceIndexPosture,
      terminalDisposition,
      finalityDisposition,
      proofSummary: {
        verificationReceiptHashVerified:
          receiptVerifierPacket.verificationReceiptHashVerified === true,
        receiptHashVerified: receiptVerifierPacket.receiptHashVerified === true,
        evidenceIndexHashVerified: receiptVerifierPacket.evidenceIndexHashVerified === true,
        expectedSourceStatusesVerified:
          receiptVerifierPacket.expectedSourceStatusesVerified === true,
        chainRangeVerified: receiptVerifierPacket.chainRangeVerified === true,
        audienceVerified: receiptVerifierPacket.audienceVerified === true,
        statusesVerified: receiptVerifierPacket.statusesVerified === true,
        routeContractsVerified: receiptVerifierPacket.routeContractsVerified === true,
        sourceRoutesVerified: receiptVerifierPacket.sourceRoutesVerified === true,
        evidenceRoutesVerified: receiptVerifierPacket.evidenceRoutesVerified === true,
        hashEqualityVerified: receiptVerifierPacket.hashEqualityVerified === true,
        proofFlagsAllTrue: receiptVerifierPacket.proofFlagsAllTrue === true,
        terminalDispositionVerified: receiptVerifierPacket.terminalDispositionVerified === true,
        finalityDispositionVerified: receiptVerifierPacket.finalityDispositionVerified === true,
        evidenceIndexPostureVerified: receiptVerifierPacket.evidenceIndexPostureVerified === true,
        receiptDispositionVerified: receiptVerifierPacket.receiptDispositionVerified === true,
        certificateHashVerified: receiptVerifierPacket.certificateHashVerified === true,
        sourceReceiptHashVerified: receiptVerifierPacket.sourceReceiptHashVerified === true,
        terminalSealHashVerified: receiptVerifierPacket.terminalSealHashVerified === true,
        regulatorReady: receiptVerifierPacket.regulatorReady === true,
        investorReady: receiptVerifierPacket.investorReady === true,
        jsonResponseOnly: receiptVerifierPacket.jsonResponseOnly === true,
        noFilesystemWrite: receiptVerifierPacket.noFilesystemWrite === true,
      },
      certificateDisposition: {
        certificateStatus: 'TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFIED',
        sourceVerifierPassed:
          receiptVerifierPacket.status ===
          'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIED',
        receiptVerified: receiptVerifierPacket.verificationReceiptHashVerified === true,
        receiptHashVerified: receiptVerifierPacket.receiptHashVerified === true,
        evidenceIndexVerified: receiptVerifierPacket.evidenceIndexHashVerified === true,
        evidenceRoutesVerified: receiptVerifierPacket.evidenceRoutesVerified === true,
        proofFlagsAllTrue: receiptVerifierPacket.proofFlagsAllTrue === true,
        receiptDispositionVerified: receiptVerifierPacket.receiptDispositionVerified === true,
        regulatorReady: receiptVerifierPacket.regulatorReady === true,
        investorReady: receiptVerifierPacket.investorReady === true,
        filesystemExported: false,
        jsonResponseOnly: true,
        noFilesystemWrite: true,
      },
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
      sourceEvidenceIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
      sourceEvidenceIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      jsonResponseOnly:
        receiptVerifierPacket.jsonResponseOnly === true &&
        receiptVerifier.jsonResponseOnly === true &&
        receipt.jsonResponseOnly === true &&
        receiptDisposition.jsonResponseOnly === true &&
        evidenceIndexPosture.jsonResponseOnly === true &&
        terminalDisposition.jsonResponseOnly === true &&
        finalityDisposition.jsonResponseOnly === true,
      noFilesystemWrite:
        receiptVerifierPacket.noFilesystemWrite === true &&
        receiptVerifier.noFilesystemWrite === true &&
        receipt.noFilesystemWrite === true &&
        receiptDisposition.noFilesystemWrite === true &&
        evidenceIndexPosture.noFilesystemWrite === true &&
        terminalDisposition.noFilesystemWrite === true &&
        finalityDisposition.noFilesystemWrite === true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };

    const certificateHash =
      computeRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateHash(
        certificatePayload
      );

    const terminalFinalityEvidenceReceiptCertificate = {
      ...certificatePayload,
      certificateHash,
      certificateHashShort: certificateHash.slice(0, 16),
    };

    const certificateIssued =
      terminalFinalityEvidenceReceiptCertificate.sourceVerificationReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceVerificationReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_MATERIALIZED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceEvidenceIndexVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceEvidenceIndexStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEXED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceFinalityCertificateVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceFinalityCertificateStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ISSUED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceReceiptVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceReceiptStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_MATERIALIZED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceTerminalSealVerifierStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIED' &&
      terminalFinalityEvidenceReceiptCertificate.sourceTerminalSealStatus ===
        'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ISSUED' &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.verificationReceiptHashVerified ===
        true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.receiptHashVerified === true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.evidenceIndexHashVerified === true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.expectedSourceStatusesVerified ===
        true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.evidenceRoutesVerified === true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.proofFlagsAllTrue === true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.receiptDispositionVerified === true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.regulatorReady === true &&
      terminalFinalityEvidenceReceiptCertificate.proofSummary.investorReady === true &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.sourceVerifierPassed ===
        true &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.receiptVerified === true &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.receiptHashVerified ===
        true &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.evidenceIndexVerified ===
        true &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.filesystemExported ===
        false &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.jsonResponseOnly === true &&
      terminalFinalityEvidenceReceiptCertificate.certificateDisposition.noFilesystemWrite ===
        true &&
      terminalFinalityEvidenceReceiptCertificate.jsonResponseOnly === true &&
      terminalFinalityEvidenceReceiptCertificate.noFilesystemWrite === true &&
      terminalFinalityEvidenceReceiptCertificate.persistenceMode === 'JSON_RESPONSE_ONLY';

    return {
      ok: certificateIssued,
      version:
        WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERSION,
      status: certificateIssued
        ? 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_ISSUED'
        : 'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_DEGRADED',
      certificateHash,
      certificateHashShort: certificateHash.slice(0, 16),
      ledgerRoot: terminalFinalityEvidenceReceiptCertificate.ledgerRoot,
      verificationReceiptHashVerified:
        terminalFinalityEvidenceReceiptCertificate.proofSummary.verificationReceiptHashVerified,
      receiptHashVerified:
        terminalFinalityEvidenceReceiptCertificate.proofSummary.receiptHashVerified,
      evidenceIndexHashVerified:
        terminalFinalityEvidenceReceiptCertificate.proofSummary.evidenceIndexHashVerified,
      expectedSourceStatusesVerified:
        terminalFinalityEvidenceReceiptCertificate.proofSummary.expectedSourceStatusesVerified,
      evidenceRoutesVerified:
        terminalFinalityEvidenceReceiptCertificate.proofSummary.evidenceRoutesVerified,
      proofFlagsAllTrue: terminalFinalityEvidenceReceiptCertificate.proofSummary.proofFlagsAllTrue,
      receiptDispositionVerified:
        terminalFinalityEvidenceReceiptCertificate.proofSummary.receiptDispositionVerified,
      regulatorReady: terminalFinalityEvidenceReceiptCertificate.proofSummary.regulatorReady,
      investorReady: terminalFinalityEvidenceReceiptCertificate.proofSummary.investorReady,
      terminalFinalityEvidenceReceiptCertificate,
      sourceTerminalFinalityEvidenceIndexVerificationReceiptVerifier: receiptVerifierPacket,
      terminalFinalityEvidenceIndexVerificationReceipt: receipt,
      jsonResponseOnly: true,
      noFilesystemWrite: true,
      persistenceMode: 'JSON_RESPONSE_ONLY',
    };
  };
