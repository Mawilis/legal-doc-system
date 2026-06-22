/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — SOVEREIGN CRM SERVICE                                                                                                      ║
 * ║ VERSION: 3.0.0-EPITOME-COMMAND-SPINE                                                                                                  ║
 * ║ ROLE: Frontend API client for CRM commercial truth, board readiness, Source Registry evidence, authority and contract-ledger posture.║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF                                                                                                    ║
 * ║ • Wilson Khanyezi — Founder/Lead Architect: Mandated CRM as Wilsy OS commercial truth spine, not a Zoho/HubSpot clone.              ║
 * ║ • AI Engineering — Epitomised service client: Added command-center, evidence projection, repair signals and contract/authority APIs.║
 * ║ • Source Registry — Connected CRM records to legal artifact evidence without fake VERIFIED posture.                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Wilsy OS CRM service layer.
 * This service does not create fake records and does not fabricate VERIFIED evidence.
 */

import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';
import logger from '../utils/logger';
import { TEL_EVENTS } from '../constants/telemetryConstants';

export const CRM_SERVICE_VERSION = '3.0.0-EPITOME-COMMAND-SPINE';
export const CRM_TRUTH_POLICY = 'NO_FAKE_VERIFIED';

export const CRM_RESOURCE_TYPES = Object.freeze([
  'leads',
  'contacts',
  'accounts',
  'deals',
  'tasks',
  'meetings',
  'calls',
  'campaigns',
  'documents',
  'visits',
  'projects',
  'quotes',
  'invoices',
  'cases',
  'tickets',
  'contracts',
  'authorities',
  'risks',
  'opportunities',
  'suppliers',
  'partners'
]);

/**
 * CRM REQUEST CONTRACT GUARD - STEP 4.2
 */

/**
 * @function getCrmKnownResourceTypes
 * @description Returns the supported CRM resource ids used to detect tenant/resource argument inversion.
 * @returns {Array<string>} CRM resource ids.
 * @collaboration Prevents calls like tenantId=leads and query keys 0=M,1=A from reaching CRM routes.
 */
const getCrmKnownResourceTypes = () => ([
  'leads',
  'contacts',
  'accounts',
  'deals',
  'tasks',
  'meetings',
  'calls',
  'campaigns',
  'documents',
  'visits',
  'projects',
  'quotes',
  'invoices',
  'cases',
  'tickets',
  'contracts',
  'authorities',
  'risks',
  'opportunities',
  'suppliers',
  'partners'
]);

/**
 * @function isCrmResourceType
 * @description Determines whether a candidate value is a CRM resource id instead of a tenant id.
 * @param {unknown} value - Candidate value.
 * @returns {boolean} True when the value is a CRM resource id.
 * @collaboration Keeps tenant shard routing from receiving module names such as leads or contacts.
 */
const isCrmResourceType = (value = '') => getCrmKnownResourceTypes().includes(String(value || '').trim().toLowerCase());

/**
 * @function extractCrmTenantCandidate
 * @description Extracts a string tenant id from mixed legacy CRM arguments.
 * @param {unknown} candidate - Candidate tenant source.
 * @returns {string} Extracted tenant id or empty string.
 * @collaboration Allows CRM to survive old call signatures without emitting malformed nested query params.
 */
const extractCrmTenantCandidate = (candidate = '') => {
  if (!candidate) return '';

  if (typeof candidate === 'object' && !Array.isArray(candidate)) {
    return String(
      candidate.tenantId ||
      candidate.currentTenantId ||
      candidate.activeTenantId ||
      candidate.id ||
      candidate.tenant ||
      ''
    ).trim();
  }

  return String(candidate).trim();
};

/**
 * @function normalizeCrmTenantId
 * @description Normalizes CRM tenant ids and rejects resource names, objects, arrays and blank values.
 * @param {unknown} candidate - Candidate tenant id.
 * @param {string} fallback - Safe fallback tenant id.
 * @returns {string} Safe tenant id.
 * @collaboration Stops tenant query pollution before requests reach multi-tenant shard routing.
 */
const normalizeCrmTenantId = (candidate = 'MASTER', fallback = 'MASTER') => {
  const fallbackValue = extractCrmTenantCandidate(fallback) || 'MASTER';
  const extracted = extractCrmTenantCandidate(candidate);

  if (!extracted) return fallbackValue;
  if (extracted === '[object Object]') return fallbackValue;
  if (isCrmResourceType(extracted)) return fallbackValue;

  return extracted;
};

/**
 * @function normalizeCrmQueryParams
 * @description Removes nested tenant objects, resource ids, numeric spread keys and non-scalar values from CRM query params.
 * @param {unknown} params - Candidate query params.
 * @returns {Object} Sanitized query params.
 * @collaboration Prevents URL shapes like 0=M&1=A and tenantId[tenantId]=MASTER.
 */
const normalizeCrmQueryParams = (params = {}) => {
  if (!params || typeof params !== 'object' || Array.isArray(params)) return {};

  return Object.entries(params).reduce((safe, [key, value]) => {
    if (/^\d+$/.test(String(key))) return safe;
    if (['tenantId', 'tenant', 'resourceType'].includes(String(key))) return safe;
    if (value === undefined || value === null || value === '') return safe;
    if (typeof value === 'object') return safe;

    return {
      ...safe,
      [key]: value
    };
  }, {});
};

/**
 * @function buildCrmRequestParams
 * @description Builds canonical CRM request params from legacy and current call signatures.
 * @param {unknown} tenantCandidate - Candidate tenant id.
 * @param {unknown} paramsCandidate - Candidate params.
 * @param {string} fallbackTenantId - Safe fallback tenant id.
 * @returns {Object} Canonical params containing exactly one safe tenantId plus scalar filters.
 * @collaboration Makes CRM requests shard-safe while preserving real filters like limit, offset and search.
 */
const buildCrmRequestParams = (tenantCandidate = 'MASTER', paramsCandidate = {}, fallbackTenantId = 'MASTER') => {
  const fallback = normalizeCrmTenantId(fallbackTenantId);
  const tenantFromParams = paramsCandidate && typeof paramsCandidate === 'object' && !Array.isArray(paramsCandidate)
    ? extractCrmTenantCandidate(paramsCandidate)
    : '';
  const tenantFromStringParams = typeof paramsCandidate === 'string' && !isCrmResourceType(paramsCandidate)
    ? paramsCandidate
    : '';
  const tenantFallback = tenantFromParams || tenantFromStringParams || fallback;
  const tenantId = normalizeCrmTenantId(tenantCandidate, tenantFallback);

  return {
    tenantId,
    ...normalizeCrmQueryParams(paramsCandidate)
  };
};

/**
 * @function buildCrmTenantHeaders
 * @description Builds CRM tenant headers from canonical tenant id values.
 * @param {unknown} tenantCandidate - Candidate tenant id.
 * @returns {Object} Tenant headers.
 * @collaboration Keeps X-Tenant-Id aligned with the query tenant and prevents object headers.
 */
const buildCrmTenantHeaders = (tenantCandidate = 'MASTER') => buildTenantHeaders(normalizeCrmTenantId(tenantCandidate));

const CRM_BASE = '/crm';

const DEFAULT_SUCCESS_EVENT = TEL_EVENTS.CRM?.HYDRATION_SUCCESS || 'CRM_HYDRATION_SUCCESS';
const DEFAULT_FAILURE_EVENT = TEL_EVENTS.CRM?.HYDRATION_FRACTURE || 'CRM_HYDRATION_FRACTURE';

/**
 * @function crmTelemetryEvent
 * @description Resolves a telemetry constant without breaking when a new CRM resource lacks a dedicated event.
 * @param {string} key - Telemetry key.
 * @param {string} fallback - Fallback telemetry event.
 * @returns {string} Telemetry event.
 * @collaboration Lets Wilsy OS expand CRM modules faster than telemetry constants are added.
 */
function crmTelemetryEvent(key, fallback = DEFAULT_SUCCESS_EVENT) {
  return TEL_EVENTS.CRM?.[key] || fallback;
}

/**
 * @function buildTenantHeaders
 * @description Builds tenant headers for CRM requests.
 * @param {string} tenantId - Tenant id.
 * @returns {object} HTTP headers.
 * @collaboration Keeps every CRM request tenant-aware across cockpit, command center and Source Registry surfaces.
 */
function buildTenantHeaders(tenantId) {
  return {
    'X-Tenant-ID': tenantId,
    'X-Tenant-Id': tenantId
  };
}

/**
 * @function sanitizePayload
 * @description Removes undefined values recursively while preserving explicit null and false values.
 * @param {*} value - Payload value.
 * @returns {*} Sanitized payload.
 * @collaboration Prevents frontend CRM forms from sending validation-hostile undefined values.
 */
function sanitizePayload(value) {
  if (Array.isArray(value)) {
    return value.map((item) => sanitizePayload(item));
  }

  if (!value || typeof value !== 'object') {
    return value;
  }

  return Object.keys(value).reduce((acc, key) => {
    if (value[key] !== undefined) {
      acc[key] = sanitizePayload(value[key]);
    }

    return acc;
  }, {});
}

/**
 * @function normalizeEnvelope
 * @description Normalizes Wilsy command envelopes and legacy array responses into one client shape.
 * @param {*} payload - Raw response payload.
 * @returns {object} Normalized envelope.
 * @collaboration Allows legacy dashboards and new command views to consume the same CRM service.
 */
function normalizeEnvelope(payload) {
  if (Array.isArray(payload)) {
    return {
      success: true,
      items: payload,
      total: payload.length,
      limit: payload.length,
      offset: 0,
      hasMore: false,
      truthPolicy: CRM_TRUTH_POLICY
    };
  }

  return {
    success: payload?.success !== false,
    ...payload,
    truthPolicy: payload?.truthPolicy || CRM_TRUTH_POLICY
  };
}

/**
 * @function normalizeListResponse
 * @description Normalizes list responses into pagination-aware shape.
 * @param {*} payload - Raw list payload.
 * @param {object} params - Request params.
 * @returns {{items:Array,total:number,limit:number,offset:number,hasMore:boolean,truthPolicy:string,routeSeal:string|undefined}} List response.
 * @collaboration Keeps large CRM datasets ready for Wilsy OS cockpit pagination.
 */
function normalizeListResponse(payload, params = {}) {
  const envelope = normalizeEnvelope(payload);
  const items = Array.isArray(envelope.items) ? envelope.items : (envelope.data || []);
  const total = Number(envelope.total ?? items.length);
  const limit = Number(envelope.limit ?? params.limit ?? 50);
  const offset = Number(envelope.offset ?? params.offset ?? 0);

  return {
    ...envelope,
    items,
    total,
    limit,
    offset,
    hasMore: Boolean(envelope.hasMore ?? (offset + limit < total)),
    truthPolicy: envelope.truthPolicy || CRM_TRUTH_POLICY
  };
}

/**
 * @function broadcastCrmTelemetry
 * @description Broadcasts CRM telemetry without allowing telemetry failures to break CRM operations.
 * @param {string} tenantId - Tenant id.
 * @param {string} eventName - Telemetry event name.
 * @param {string} status - Event status.
 * @param {string} context - Event context.
 * @param {object} metadata - Event metadata.
 * @returns {Promise<void>}
 * @collaboration Keeps the CRM service observable while protecting primary user workflows.
 */
async function broadcastCrmTelemetry(tenantId, eventName, status, context, metadata = {}) {
  try {
    await broadcastTelemetry(tenantId, eventName, status, context, {
      serviceVersion: CRM_SERVICE_VERSION,
      truthPolicy: CRM_TRUTH_POLICY,
      ...metadata
    });
  } catch (error) {
    logger.warn?.(`[crmService] telemetry failed for ${context}: ${error.message}`, { tenantId });
  }
}

/**
 * @function handleApiError
 * @description Handles CRM API errors with standardized logging and telemetry.
 * @param {Error} error - Caught error.
 * @param {string} context - Function context.
 * @param {string} tenantId - Tenant id.
 * @param {string} failureEvent - Failure telemetry event.
 * @param {object} extra - Extra metadata.
 * @throws {Error} Original error.
 * @collaboration Gives operators a traceable failure surface instead of silent CRM fractures.
 */
async function handleApiError(error, context, tenantId, failureEvent, extra = {}) {
  const message = error.response?.data?.message || error.message;
  logger.error(`[crmService] ${context} failed: ${message}`, { tenantId, ...extra });

  await broadcastCrmTelemetry(tenantId, failureEvent, 'FRACTURE', context, {
    error: message,
    ...extra
  });

  throw error;
}

/**
 * @function getResource
 * @description Fetches one CRM resource collection with pagination and evidence filters.
 * @param {string} endpoint - API endpoint.
 * @param {string} tenantId - Tenant id.
 * @param {object} params - Query params.
 * @param {string} successEvent - Success telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<object>} Pagination-aware result.
 * @collaboration Powers Zoho-class lists while preserving Wilsy source posture fields.
 */
async function getResource(endpoint, tenantId, params = {}, successEvent = DEFAULT_SUCCESS_EVENT, failureEvent = DEFAULT_FAILURE_EVENT) {
  try {
    const response = await api.get(endpoint, {
      params: buildCrmRequestParams(tenantId, params),
      headers: buildCrmTenantHeaders(tenantId)
    });
    const normalized = normalizeListResponse(response.data, params);

    await broadcastCrmTelemetry(tenantId, successEvent, 'SUCCESS', `get${endpoint}`, {
      count: normalized.items.length,
      total: normalized.total,
      hasMore: normalized.hasMore
    });

    return normalized;
  } catch (error) {
    await handleApiError(error, `get${endpoint}`, tenantId, failureEvent, { params });

    return {
      success: false,
      items: [],
      total: 0,
      limit: 0,
      offset: 0,
      hasMore: false,
      truthPolicy: CRM_TRUTH_POLICY
    };
  }
}

/**
 * @function getResourceArray
 * @description Fetches a CRM resource collection and returns only records for legacy dashboards.
 * @param {string} endpoint - API endpoint.
 * @param {string} tenantId - Tenant id.
 * @param {object} params - Query params.
 * @returns {Promise<Array>} CRM records.
 * @collaboration Keeps existing CRM dashboard components working while the service evolves.
 */
async function getResourceArray(endpoint, tenantId, params = {}) {
  const { items } = await getResource(endpoint, tenantId, params, DEFAULT_SUCCESS_EVENT, DEFAULT_FAILURE_EVENT);

  return items;
}

/**
 * @function postResource
 * @description Creates CRM records or command resources through POST.
 * @param {string} endpoint - API endpoint.
 * @param {object} data - Request payload.
 * @param {string} tenantId - Tenant id.
 * @param {string} successEvent - Success telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<object>} Created resource envelope.
 * @collaboration Makes all creation calls pass through one audited CRM service path.
 */
async function postResource(endpoint, data, tenantId, successEvent = DEFAULT_SUCCESS_EVENT, failureEvent = DEFAULT_FAILURE_EVENT) {
  const sanitized = sanitizePayload(data);

  try {
    const response = await api.post(endpoint, sanitized, {
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, successEvent, 'SUCCESS', `post${endpoint}`, {
      id: envelope.record?.id || envelope.id,
      routeSeal: envelope.routeSeal
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, `post${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
}

/**
 * @function putResource
 * @description Updates CRM records through PUT.
 * @param {string} endpoint - API endpoint.
 * @param {object} data - Request payload.
 * @param {string} tenantId - Tenant id.
 * @param {string} successEvent - Success telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<object>} Updated resource envelope.
 * @collaboration Keeps CRM updates tied to route seals and telemetry.
 */
async function putResource(endpoint, data, tenantId, successEvent = DEFAULT_SUCCESS_EVENT, failureEvent = DEFAULT_FAILURE_EVENT) {
  const sanitized = sanitizePayload(data);

  try {
    const response = await api.put(endpoint, sanitized, {
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, successEvent, 'SUCCESS', `put${endpoint}`, {
      id: envelope.record?.id || envelope.id,
      routeSeal: envelope.routeSeal
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, `put${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
}

/**
 * @function patchResource
 * @description Updates CRM command sub-resources through PATCH.
 * @param {string} endpoint - API endpoint.
 * @param {object} data - Request payload.
 * @param {string} tenantId - Tenant id.
 * @param {string} successEvent - Success telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<object>} Updated command envelope.
 * @collaboration Enables authority and contract-ledger updates without generic record overwrites.
 */
async function patchResource(endpoint, data, tenantId, successEvent = DEFAULT_SUCCESS_EVENT, failureEvent = DEFAULT_FAILURE_EVENT) {
  const sanitized = sanitizePayload(data);

  try {
    const response = await api.patch(endpoint, sanitized, {
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, successEvent, 'SUCCESS', `patch${endpoint}`, {
      id: envelope.record?.id || envelope.id,
      routeSeal: envelope.routeSeal
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, `patch${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
}

/**
 * @function deleteResource
 * @description Deletes a CRM record through the route layer.
 * @param {string} endpoint - API endpoint.
 * @param {string} tenantId - Tenant id.
 * @param {string} successEvent - Success telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<object>} Delete envelope.
 * @collaboration Keeps destructive CRM operations explicit and telemetry-backed.
 */
async function deleteResource(endpoint, tenantId, successEvent = DEFAULT_SUCCESS_EVENT, failureEvent = DEFAULT_FAILURE_EVENT) {
  try {
    const response = await api.delete(endpoint, {
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, successEvent, 'SUCCESS', `delete${endpoint}`, {
      routeSeal: envelope.routeSeal
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, `delete${endpoint}`, tenantId, failureEvent);
    throw error;
  }
}

/**
 * @function getCrmSchema
 * @description Retrieves CRM schema blueprints and command capabilities.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} CRM schema envelope.
 * @collaboration Lets CRM forms render from live route metadata instead of hardcoded prototype fields.
 */
export async function getCrmSchema(tenantId) {
  const response = await api.get(`${CRM_BASE}/schema`, {
    params: buildCrmRequestParams(tenantId),
    headers: buildCrmTenantHeaders(tenantId)
  });

  return normalizeEnvelope(response.data);
}

/**
 * @function getCrmSummary
 * @description Retrieves CRM resource summary by type.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} CRM summary envelope.
 * @collaboration Feeds legacy summary widgets while command-center grows around them.
 */
export async function getCrmSummary(tenantId) {
  const response = await api.get(`${CRM_BASE}/summary`, {
    params: buildCrmRequestParams(tenantId),
    headers: buildCrmTenantHeaders(tenantId)
  });

  return normalizeEnvelope(response.data);
}

/**
 * @function getCrmCommandCenter
 * @description Retrieves the Wilsy OS CRM command-center snapshot.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} Command-center envelope.
 * @collaboration Elevates CRM from records into board-readable commercial truth.
 */
export async function getCrmCommandCenter(tenantId) {
  try {
    const response = await api.get(`${CRM_BASE}/command-center`, {
      params: buildCrmRequestParams(tenantId),
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, DEFAULT_SUCCESS_EVENT, 'SUCCESS', 'getCrmCommandCenter', {
      total: envelope.total,
      repairSignalCount: envelope.repairSignalCount
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, 'getCrmCommandCenter', tenantId, DEFAULT_FAILURE_EVENT);
    throw error;
  }
}

/**
 * @function getCrmSourceRegistryEvidence
 * @description Retrieves CRM records projected as Source Registry evidence.
 * @param {string} tenantId - Tenant id.
 * @param {object} params - Evidence lookup params.
 * @returns {Promise<object>} Source Registry evidence envelope.
 * @collaboration Connects CRM directly to Legal Artifact Studio, boardroom proof and source-repair workflows.
 */
export async function getCrmSourceRegistryEvidence(tenantId, params = {}) {
  try {
    const response = await api.get(`${CRM_BASE}/source-registry-evidence`, {
      params: buildCrmRequestParams(tenantId, params),
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, DEFAULT_SUCCESS_EVENT, 'SUCCESS', 'getCrmSourceRegistryEvidence', {
      total: envelope.total,
      routeSeal: envelope.routeSeal
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, 'getCrmSourceRegistryEvidence', tenantId, DEFAULT_FAILURE_EVENT, { params });
    throw error;
  }
}

/**
 * @function getCrmRecord
 * @description Retrieves one CRM record with its evidence projection.
 * @param {string} resourceType - CRM resource type.
 * @param {string} id - CRM record id.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} CRM record envelope.
 * @collaboration Turns a CRM detail view into an evidence dossier.
 */
export function getCrmRecord(resourceType, id, tenantId) {
  return getResource(`${CRM_BASE}/${resourceType}/${id}`, tenantId, {}, DEFAULT_SUCCESS_EVENT, DEFAULT_FAILURE_EVENT);
}

/**
 * @function attachCrmRepairSignal
 * @description Adds a repair signal to a CRM record.
 * @param {string} resourceType - CRM resource type.
 * @param {string} id - CRM record id.
 * @param {object} signal - Repair signal payload.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} Updated CRM record envelope.
 * @collaboration Converts CRM gaps into executable operating-system repair work.
 */
export function attachCrmRepairSignal(resourceType, id, signal, tenantId) {
  return postResource(`${CRM_BASE}/${resourceType}/${id}/repair-signal`, signal, tenantId, DEFAULT_SUCCESS_EVENT, DEFAULT_FAILURE_EVENT);
}

/**
 * @function patchCrmAuthority
 * @description Updates authority-to-bind posture for a CRM record.
 * @param {string} resourceType - CRM resource type.
 * @param {string} id - CRM record id.
 * @param {object} authority - Authority payload.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} Updated CRM record envelope.
 * @collaboration Makes contacts, accounts and deals authority-aware before boardroom reliance.
 */
export function patchCrmAuthority(resourceType, id, authority, tenantId) {
  return patchResource(`${CRM_BASE}/${resourceType}/${id}/authority`, authority, tenantId, DEFAULT_SUCCESS_EVENT, DEFAULT_FAILURE_EVENT);
}

/**
 * @function patchCrmContractLedger
 * @description Updates contract-ledger posture for a CRM record.
 * @param {string} resourceType - CRM resource type.
 * @param {string} id - CRM record id.
 * @param {object} contractLedger - Contract ledger payload.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} Updated CRM record envelope.
 * @collaboration Links CRM pipeline to legal artifacts, Source Registry and revenue truth.
 */
export function patchCrmContractLedger(resourceType, id, contractLedger, tenantId) {
  return patchResource(`${CRM_BASE}/${resourceType}/${id}/contract-ledger`, contractLedger, tenantId, DEFAULT_SUCCESS_EVENT, DEFAULT_FAILURE_EVENT);
}

/**
 * @function previewImportRecords
 * @description Previews a CRM import batch before persistence.
 * @param {string} resourceType - CRM resource type.
 * @param {string} tenantId - Tenant id.
 * @param {Array<object>} records - Import records.
 * @param {object} options - Preview options.
 * @returns {Promise<object>} Preview report.
 * @collaboration Makes imports reveal field coverage, duplicate risk and identity gaps before data enters Wilsy OS.
 */
export async function previewImportRecords(resourceType, tenantId, records = [], options = {}) {
  try {
    const response = await api.post(`${CRM_BASE}/${resourceType}/preview-import`, {
      records,
      dedupeKey: options.dedupeKey,
      sourceSystem: options.sourceSystem
    }, {
      headers: buildCrmTenantHeaders(tenantId)
    });

    return normalizeEnvelope(response.data);
  } catch (error) {
    await handleApiError(error, `previewCRM${resourceType}`, tenantId, DEFAULT_FAILURE_EVENT, {
      count: records.length
    });
    throw error;
  }
}

/**
 * @function importRecords
 * @description Imports CRM records with mode, dedupe key and source metadata.
 * @param {string} resourceType - CRM resource type.
 * @param {string} tenantId - Tenant id.
 * @param {Array<object>} records - Import records.
 * @param {object} options - Import options.
 * @returns {Promise<object>} Import report.
 * @collaboration Turns bulk CRM import into governed data intake rather than raw spreadsheet ingestion.
 */
export async function importRecords(resourceType, tenantId, records = [], options = {}) {
  try {
    const response = await api.post(`${CRM_BASE}/${resourceType}/import`, {
      records,
      mode: options.mode || 'upsert',
      dedupeKey: options.dedupeKey,
      sourceSystem: options.sourceSystem
    }, {
      headers: buildCrmTenantHeaders(tenantId)
    });
    const envelope = normalizeEnvelope(response.data);

    await broadcastCrmTelemetry(tenantId, DEFAULT_SUCCESS_EVENT, 'SUCCESS', `importCRM${resourceType}`, {
      received: records.length,
      inserted: envelope.inserted || 0,
      updated: envelope.updated || 0
    });

    return envelope;
  } catch (error) {
    await handleApiError(error, `importCRM${resourceType}`, tenantId, DEFAULT_FAILURE_EVENT, {
      count: records.length
    });
    throw error;
  }
}

/**
 * @function getLeads
 * @description Retrieves lead records.
 * @param {string} tenantId - Tenant id.
 * @param {object} params - Query params.
 * @returns {Promise<object>} Lead list.
 * @collaboration Treats leads as origin-of-obligation records.
 */
export const getLeads = (tenantId, params = {}) => getResource(`${CRM_BASE}/leads`, tenantId, params, DEFAULT_SUCCESS_EVENT, crmTelemetryEvent('LEAD_FRACTURE', DEFAULT_FAILURE_EVENT));

/**
 * @function getLeadsArray
 * @description Retrieves lead records as an array.
 * @param {string} tenantId - Tenant id.
 * @param {object} params - Query params.
 * @returns {Promise<Array>} Lead array.
 * @collaboration Keeps legacy lead widgets working.
 */
export const getLeadsArray = (tenantId, params = {}) => getResourceArray(`${CRM_BASE}/leads`, tenantId, params);

export const createLead = (data, tenantId) => postResource(`${CRM_BASE}/leads`, data, tenantId, crmTelemetryEvent('LEAD_CREATED'), crmTelemetryEvent('LEAD_FRACTURE', DEFAULT_FAILURE_EVENT));
export const updateLead = (id, data, tenantId) => putResource(`${CRM_BASE}/leads/${id}`, data, tenantId, crmTelemetryEvent('LEAD_UPDATED'), crmTelemetryEvent('LEAD_FRACTURE', DEFAULT_FAILURE_EVENT));
export const deleteLead = (id, tenantId) => deleteResource(`${CRM_BASE}/leads/${id}`, tenantId, crmTelemetryEvent('LEAD_DELETED'), crmTelemetryEvent('LEAD_FRACTURE', DEFAULT_FAILURE_EVENT));

export const getContacts = (tenantId, params = {}) => getResource(`${CRM_BASE}/contacts`, tenantId, params);
export const getContactsArray = (tenantId, params = {}) => getResourceArray(`${CRM_BASE}/contacts`, tenantId, params);
export const createContact = (data, tenantId) => postResource(`${CRM_BASE}/contacts`, data, tenantId, crmTelemetryEvent('CONTACT_CREATED'));
export const updateContact = (id, data, tenantId) => putResource(`${CRM_BASE}/contacts/${id}`, data, tenantId, crmTelemetryEvent('CONTACT_UPDATED'));
export const deleteContact = (id, tenantId) => deleteResource(`${CRM_BASE}/contacts/${id}`, tenantId, crmTelemetryEvent('CONTACT_DELETED'));

export const getAccounts = (tenantId, params = {}) => getResource(`${CRM_BASE}/accounts`, tenantId, params);
export const getAccountsArray = (tenantId, params = {}) => getResourceArray(`${CRM_BASE}/accounts`, tenantId, params);
export const createAccount = (data, tenantId) => postResource(`${CRM_BASE}/accounts`, data, tenantId, crmTelemetryEvent('ACCOUNT_CREATED'));
export const updateAccount = (id, data, tenantId) => putResource(`${CRM_BASE}/accounts/${id}`, data, tenantId, crmTelemetryEvent('ACCOUNT_UPDATED'));
export const deleteAccount = (id, tenantId) => deleteResource(`${CRM_BASE}/accounts/${id}`, tenantId, crmTelemetryEvent('ACCOUNT_DELETED'));

export const getDeals = (tenantId, params = {}) => getResource(`${CRM_BASE}/deals`, tenantId, params, DEFAULT_SUCCESS_EVENT, crmTelemetryEvent('DEAL_FRACTURE', DEFAULT_FAILURE_EVENT));
export const getDealsArray = (tenantId, params = {}) => getResourceArray(`${CRM_BASE}/deals`, tenantId, params);
export const createDeal = (data, tenantId) => postResource(`${CRM_BASE}/deals`, data, tenantId, crmTelemetryEvent('DEAL_CREATED'), crmTelemetryEvent('DEAL_FRACTURE', DEFAULT_FAILURE_EVENT));
export const updateDeal = (id, data, tenantId) => putResource(`${CRM_BASE}/deals/${id}`, data, tenantId, crmTelemetryEvent('DEAL_PROMOTED'), crmTelemetryEvent('DEAL_FRACTURE', DEFAULT_FAILURE_EVENT));
export const deleteDeal = (id, tenantId) => deleteResource(`${CRM_BASE}/deals/${id}`, tenantId, crmTelemetryEvent('DEAL_LOST'), crmTelemetryEvent('DEAL_FRACTURE', DEFAULT_FAILURE_EVENT));

/**
 * @function makeResourceMethods
 * @description Creates CRUD methods for non-legacy CRM resource families.
 * @param {string} resource - CRM resource path.
 * @returns {object} CRUD methods.
 * @collaboration Lets Wilsy OS add CRM modules without duplicating fragile fetch logic.
 */
function makeResourceMethods(resource) {
  return {
    list: (tenantId, params = {}) => getResource(`${CRM_BASE}/${resource}`, tenantId, params),
    listArray: (tenantId, params = {}) => getResourceArray(`${CRM_BASE}/${resource}`, tenantId, params),
    create: (data, tenantId) => postResource(`${CRM_BASE}/${resource}`, data, tenantId),
    update: (id, data, tenantId) => putResource(`${CRM_BASE}/${resource}/${id}`, data, tenantId),
    remove: (id, tenantId) => deleteResource(`${CRM_BASE}/${resource}/${id}`, tenantId)
  };
}

const taskMethods = makeResourceMethods('tasks');
const meetingMethods = makeResourceMethods('meetings');
const callMethods = makeResourceMethods('calls');
const campaignMethods = makeResourceMethods('campaigns');
const documentMethods = makeResourceMethods('documents');
const visitMethods = makeResourceMethods('visits');
const projectMethods = makeResourceMethods('projects');
const quoteMethods = makeResourceMethods('quotes');
const invoiceMethods = makeResourceMethods('invoices');
const caseMethods = makeResourceMethods('cases');
const ticketMethods = makeResourceMethods('tickets');
const contractMethods = makeResourceMethods('contracts');
const authorityMethods = makeResourceMethods('authorities');
const riskMethods = makeResourceMethods('risks');
const opportunityMethods = makeResourceMethods('opportunities');
const supplierMethods = makeResourceMethods('suppliers');
const partnerMethods = makeResourceMethods('partners');

export const getTasks = taskMethods.list;
export const getTasksArray = taskMethods.listArray;
export const createTask = taskMethods.create;
export const updateTask = taskMethods.update;
export const deleteTask = taskMethods.remove;

export const getMeetings = meetingMethods.list;
export const getMeetingsArray = meetingMethods.listArray;
export const createMeeting = meetingMethods.create;
export const updateMeeting = meetingMethods.update;
export const deleteMeeting = meetingMethods.remove;

export const getCalls = callMethods.list;
export const getCallsArray = callMethods.listArray;
export const createCall = callMethods.create;
export const updateCall = callMethods.update;
export const deleteCall = callMethods.remove;

export const getCampaigns = campaignMethods.list;
export const getCampaignsArray = campaignMethods.listArray;
export const createCampaign = campaignMethods.create;
export const updateCampaign = campaignMethods.update;
export const deleteCampaign = campaignMethods.remove;

export const getDocuments = documentMethods.list;
export const getDocumentsArray = documentMethods.listArray;
export const createDocument = documentMethods.create;
export const updateDocument = documentMethods.update;
export const deleteDocument = documentMethods.remove;

export const getVisits = visitMethods.list;
export const getVisitsArray = visitMethods.listArray;
export const createVisit = visitMethods.create;
export const updateVisit = visitMethods.update;
export const deleteVisit = visitMethods.remove;

export const getProjects = projectMethods.list;
export const getProjectsArray = projectMethods.listArray;
export const createProject = projectMethods.create;
export const updateProject = projectMethods.update;
export const deleteProject = projectMethods.remove;

export const getQuotes = quoteMethods.list;
export const getQuotesArray = quoteMethods.listArray;
export const createQuote = quoteMethods.create;
export const updateQuote = quoteMethods.update;
export const deleteQuote = quoteMethods.remove;

export const getInvoices = invoiceMethods.list;
export const getInvoicesArray = invoiceMethods.listArray;
export const createInvoice = invoiceMethods.create;
export const updateInvoice = invoiceMethods.update;
export const deleteInvoice = invoiceMethods.remove;

export const getCases = caseMethods.list;
export const getCasesArray = caseMethods.listArray;
export const createCase = caseMethods.create;
export const updateCase = caseMethods.update;
export const deleteCase = caseMethods.remove;

export const getTickets = ticketMethods.list;
export const getTicketsArray = ticketMethods.listArray;
export const createTicket = ticketMethods.create;
export const updateTicket = ticketMethods.update;
export const deleteTicket = ticketMethods.remove;

export const getContracts = contractMethods.list;
export const getContractsArray = contractMethods.listArray;
export const createContract = contractMethods.create;
export const updateContract = contractMethods.update;
export const deleteContract = contractMethods.remove;

export const getAuthorities = authorityMethods.list;
export const getAuthoritiesArray = authorityMethods.listArray;
export const createAuthority = authorityMethods.create;
export const updateAuthority = authorityMethods.update;
export const deleteAuthority = authorityMethods.remove;

export const getRisks = riskMethods.list;
export const getRisksArray = riskMethods.listArray;
export const createRisk = riskMethods.create;
export const updateRisk = riskMethods.update;
export const deleteRisk = riskMethods.remove;

export const getOpportunities = opportunityMethods.list;
export const getOpportunitiesArray = opportunityMethods.listArray;
export const createOpportunity = opportunityMethods.create;
export const updateOpportunity = opportunityMethods.update;
export const deleteOpportunity = opportunityMethods.remove;

export const getSuppliers = supplierMethods.list;
export const getSuppliersArray = supplierMethods.listArray;
export const createSupplier = supplierMethods.create;
export const updateSupplier = supplierMethods.update;
export const deleteSupplier = supplierMethods.remove;

export const getPartners = partnerMethods.list;
export const getPartnersArray = partnerMethods.listArray;
export const createPartner = partnerMethods.create;
export const updatePartner = partnerMethods.update;
export const deletePartner = partnerMethods.remove;

/**
 * @function deleteRecord
 * @description Deletes a CRM record by resource type and id.
 * @param {string} resourceType - CRM resource type.
 * @param {string} id - CRM record id.
 * @param {string} tenantId - Tenant id.
 * @returns {Promise<object>} Delete envelope.
 * @collaboration Keeps generic delete available for dynamic CRM grids.
 */
export function deleteRecord(resourceType, id, tenantId) {
  return deleteResource(`${CRM_BASE}/${resourceType}/${id}`, tenantId, DEFAULT_SUCCESS_EVENT, DEFAULT_FAILURE_EVENT);
}

export default {
  CRM_SERVICE_VERSION,
  CRM_TRUTH_POLICY,
  CRM_RESOURCE_TYPES,
  getCrmSchema,
  getCrmSummary,
  getCrmCommandCenter,
  getCrmSourceRegistryEvidence,
  getCrmRecord,
  attachCrmRepairSignal,
  patchCrmAuthority,
  patchCrmContractLedger,
  getLeads, getLeadsArray, createLead, updateLead, deleteLead,
  getContacts, getContactsArray, createContact, updateContact, deleteContact,
  getAccounts, getAccountsArray, createAccount, updateAccount, deleteAccount,
  getDeals, getDealsArray, createDeal, updateDeal, deleteDeal,
  getTasks, getTasksArray, createTask, updateTask, deleteTask,
  getMeetings, getMeetingsArray, createMeeting, updateMeeting, deleteMeeting,
  getCalls, getCallsArray, createCall, updateCall, deleteCall,
  getCampaigns, getCampaignsArray, createCampaign, updateCampaign, deleteCampaign,
  getDocuments, getDocumentsArray, createDocument, updateDocument, deleteDocument,
  getVisits, getVisitsArray, createVisit, updateVisit, deleteVisit,
  getProjects, getProjectsArray, createProject, updateProject, deleteProject,
  getQuotes, getQuotesArray, createQuote, updateQuote, deleteQuote,
  getInvoices, getInvoicesArray, createInvoice, updateInvoice, deleteInvoice,
  getCases, getCasesArray, createCase, updateCase, deleteCase,
  getTickets, getTicketsArray, createTicket, updateTicket, deleteTicket,
  getContracts, getContractsArray, createContract, updateContract, deleteContract,
  getAuthorities, getAuthoritiesArray, createAuthority, updateAuthority, deleteAuthority,
  getRisks, getRisksArray, createRisk, updateRisk, deleteRisk,
  getOpportunities, getOpportunitiesArray, createOpportunity, updateOpportunity, deleteOpportunity,
  getSuppliers, getSuppliersArray, createSupplier, updateSupplier, deleteSupplier,
  getPartners, getPartnersArray, createPartner, updatePartner, deletePartner,
  previewImportRecords,
  importRecords,
  deleteRecord
};
