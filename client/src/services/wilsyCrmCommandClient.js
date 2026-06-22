/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM COMMAND CLIENT [R18AD66-SALES-CRM-COMMAND-SOURCE-TRUTH]                                                 ║
 * ║ TENANT-SCOPED | NO FAKE DATA | ROUTE POSTURE | SOURCE POSTURE | RECEIPT POSTURE | MIGRATION READY                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/wilsyCrmCommandClient.js                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated a real CRM/Sales OS for every business model, not a prototype dashboard.                 ║
 * ║ 2. AI Engineering - Built the tenant-safe command client that refuses fake records and exposes route/source posture.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Browser-safe Wilsy CRM command client.
 * This service calls CRM command routes when available and returns explicit
 * SOURCE_REQUIRED / SOURCE_ERROR envelopes when a route or backend source is absent.
 * It never fabricates CRM records, metrics, tenants, receipts, or customer data.
 */

import {
  WILSY_CRM_IMPORT_VENDOR_CATALOG,
  WILSY_CRM_MODULE_CATALOG,
  WILSY_CRM_ROUTE_POSTURE,
  WILSY_CRM_SOURCE_STATUS,
  WILSY_CRM_TENANT_BOUNDARY,
  buildWilsyCrmModuleEnvelope,
  buildWilsyCrmRouteContract,
  getWilsyCrmModuleById,
  normalizeWilsyCrmCatalogKey
} from '../data/wilsyCrmModuleCatalog.js';

export const WILSY_CRM_COMMAND_CLIENT_VERSION = 'R18AD66-SALES-CRM-COMMAND-SOURCE-TRUTH';

export const WILSY_CRM_COMMAND_ENDPOINTS = Object.freeze({
  commandCenter: '/api/crm/command-center',
  sourceRegistryEvidence: '/api/crm/source-registry/evidence',
  moduleBase: '/api/crm',
  importPreview: '/api/crm/import/preview',
  importCommit: '/api/crm/import',
  exportRecords: '/api/crm/export'
});

export const WILSY_CRM_COMMAND_HEADERS = Object.freeze({
  tenantId: 'X-Tenant-Id',
  wilsyTenantId: 'X-Wilsy-Tenant-ID',
  client: 'X-Wilsy-CRM-Client',
  command: 'X-Wilsy-CRM-Command',
  requestId: 'X-Request-ID',
  traceId: 'X-Trace-ID'
});

const WILSY_CRM_BROWSER_TENANT_KEYS = Object.freeze([
  'tenantId',
  'wilsyTenantId',
  'activeTenantId',
  'wilsy:tenant:id',
  'wilsy:account-command-center:tenant'
]);

const WILSY_CRM_BROWSER_TOKEN_KEYS = Object.freeze([
  'token',
  'authToken',
  'accessToken',
  'wilsyToken',
  'wilsyAuthToken',
  'wilsy:auth:token',
  'wilsy:runtime:token'
]);

/**
 * @function readWilsyCrmBrowserStorageValue
 * @description Reads one browser storage value without throwing during SSR, private mode, or locked storage.
 * @param {string} key - Storage key.
 * @returns {string} Stored value or empty string.
 * @collaboration Keeps CRM client boot-safe across Discovery UI, FounderDashboard and tenant dashboards.
 */
export const readWilsyCrmBrowserStorageValue = key => {
  if (typeof window === 'undefined' || !key) return '';

  try {
    return window.localStorage.getItem(key) || window.sessionStorage.getItem(key) || '';
  } catch (error) {
    return '';
  }
};

/**
 * @function readWilsyCrmStoredJsonValue
 * @description Reads and parses a JSON storage slot without leaking failures into the CRM shell.
 * @param {string} key - Storage key.
 * @returns {Object|null} Parsed object or null.
 * @collaboration Allows tenant and operator identity slots to hydrate CRM headers safely.
 */
export const readWilsyCrmStoredJsonValue = key => {
  const value = readWilsyCrmBrowserStorageValue(key);
  if (!value) return null;

  try {
    return JSON.parse(value);
  } catch (error) {
    return null;
  }
};

/**
 * @function normalizeWilsyCrmCommandValue
 * @description Normalizes command, route, vendor, module and action values for safe request composition.
 * @param {string} value - Candidate value.
 * @returns {string} Normalized command value.
 * @collaboration Keeps user role, module and vendor values deterministic before they reach CRM routes.
 */
export const normalizeWilsyCrmCommandValue = value => normalizeWilsyCrmCatalogKey(value);

/**
 * @function getWilsyCrmApiBaseUrl
 * @description Resolves the browser-safe API base URL for CRM command calls.
 * @returns {string} API base URL without trailing slash.
 * @collaboration Keeps CRM command routing aligned with the existing Vite API convention without hardcoding production hosts.
 */
export const getWilsyCrmApiBaseUrl = () => {
  const envBase = typeof import.meta !== 'undefined'
    ? import.meta.env?.VITE_API_URL
    : '';

  return String(envBase || 'http://localhost:5050').replace(/\/+$/, '');
};

/**
 * @function resolveWilsyCrmTenantId
 * @description Resolves the tenant id for a CRM request from explicit input, tenant object, or browser runtime.
 * @param {Object|string} tenantInput - Tenant id, tenant object, or request options.
 * @returns {string} Tenant id or TENANT_SOURCE_REQUIRED.
 * @collaboration Enforces the rule that every CRM command must carry a tenant boundary.
 */
export const resolveWilsyCrmTenantId = tenantInput => {
  if (typeof tenantInput === 'string' && tenantInput.trim()) return tenantInput.trim();

  const candidate = tenantInput?.tenantId
    || tenantInput?.tenant_id
    || tenantInput?.tenant?.tenantId
    || tenantInput?.tenant?.id
    || tenantInput?.tenant?._id
    || tenantInput?.activeTenant?.tenantId
    || tenantInput?.activeTenant?.id
    || tenantInput?.activeTenant?._id;

  if (candidate) return String(candidate).trim();

  const storedDirect = WILSY_CRM_BROWSER_TENANT_KEYS
    .map(readWilsyCrmBrowserStorageValue)
    .find(value => value && !String(value).startsWith('{'));

  if (storedDirect) return String(storedDirect).trim();

  const storedTenantObject = WILSY_CRM_BROWSER_TENANT_KEYS
    .map(readWilsyCrmStoredJsonValue)
    .find(Boolean);

  return String(
    storedTenantObject?.tenantId
    || storedTenantObject?.id
    || storedTenantObject?._id
    || storedTenantObject?.tenant?.tenantId
    || 'TENANT_SOURCE_REQUIRED'
  ).trim();
};

/**
 * @function resolveWilsyCrmBearerToken
 * @description Resolves the current browser bearer token without inventing credentials.
 * @param {Object} options - Request options.
 * @returns {string} Token value or empty string.
 * @collaboration Allows authenticated CRM calls while keeping token absence explicit.
 */
export const resolveWilsyCrmBearerToken = (options = {}) => {
  if (options.token) return String(options.token).trim();

  const fromStorage = WILSY_CRM_BROWSER_TOKEN_KEYS
    .map(readWilsyCrmBrowserStorageValue)
    .find(Boolean);

  return String(fromStorage || '').trim();
};

/**
 * @function buildWilsyCrmRequestId
 * @description Builds a non-secret request id for CRM command correlation.
 * @param {string} prefix - Request id prefix.
 * @returns {string} Request id.
 * @collaboration Gives CRM command calls traceability without exposing customer data.
 */
export const buildWilsyCrmRequestId = (prefix = 'CRM') => {
  const stamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).slice(2, 10).toUpperCase();

  return `WILSY_${prefix}_${stamp}_${random}`;
};

/**
 * @function buildWilsyCrmHeaders
 * @description Builds tenant, command, trace and auth headers for CRM command requests.
 * @param {Object} options - Header options.
 * @returns {Object} HTTP headers.
 * @collaboration Makes tenant scoping explicit for every Sales, CRM, SDR, Support and Customer Success call.
 */
export const buildWilsyCrmHeaders = (options = {}) => {
  const tenantId = resolveWilsyCrmTenantId(options);
  const requestId = options.requestId || buildWilsyCrmRequestId('CRM');
  const token = resolveWilsyCrmBearerToken(options);

  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    [WILSY_CRM_COMMAND_HEADERS.tenantId]: tenantId,
    [WILSY_CRM_COMMAND_HEADERS.wilsyTenantId]: tenantId,
    [WILSY_CRM_COMMAND_HEADERS.client]: 'wilsy-crm-command-client',
    [WILSY_CRM_COMMAND_HEADERS.command]: options.command || 'crm.command',
    [WILSY_CRM_COMMAND_HEADERS.requestId]: requestId,
    [WILSY_CRM_COMMAND_HEADERS.traceId]: options.traceId || requestId
  };

  if (token) headers.Authorization = `Bearer ${token}`;

  return headers;
};

/**
 * @function buildWilsyCrmQueryString
 * @description Converts a parameter object into a safe CRM query string.
 * @param {Object} params - Query params.
 * @returns {string} Query string with leading question mark or empty string.
 * @collaboration Keeps CRM pagination, filters and source posture requests consistent.
 */
export const buildWilsyCrmQueryString = (params = {}) => {
  const query = new URLSearchParams();

  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (Array.isArray(value)) {
      value.forEach(item => query.append(key, String(item)));
      return;
    }
    query.set(key, String(value));
  });

  const output = query.toString();
  return output ? `?${output}` : '';
};

/**
 * @function safeParseWilsyCrmJson
 * @description Parses a fetch response body as JSON and safely falls back to text.
 * @param {Response} response - Fetch response.
 * @returns {Promise<Object>} Parsed response object.
 * @collaboration Prevents HTML error pages or empty bodies from crashing CRM command surfaces.
 */
export const safeParseWilsyCrmJson = async response => {
  const text = await response.text();

  if (!text) {
    return {
      ok: response.ok,
      status: response.status,
      sourceStatus: response.ok ? WILSY_CRM_SOURCE_STATUS.sourceLive : WILSY_CRM_SOURCE_STATUS.sourceError
    };
  }

  try {
    return JSON.parse(text);
  } catch (error) {
    return {
      ok: response.ok,
      status: response.status,
      body: text,
      sourceStatus: response.ok ? WILSY_CRM_SOURCE_STATUS.sourceLive : WILSY_CRM_SOURCE_STATUS.sourceError
    };
  }
};

/**
 * @function normalizeWilsyCrmEnvelope
 * @description Normalizes any backend CRM response into a source-safe envelope.
 * @param {Object} payload - Backend payload.
 * @param {Object} context - Envelope context.
 * @returns {Object} Normalized CRM envelope.
 * @collaboration Lets CRMDashboard consume several backend shapes without fabricating records.
 */
export const normalizeWilsyCrmEnvelope = (payload = {}, context = {}) => {
  const data = payload?.data || payload;
  const list = Array.isArray(data)
    ? data
    : (
        data?.items
        || data?.records
        || data?.results
        || data?.rows
        || payload?.items
        || payload?.records
        || []
      );

  const sourceStatus = payload?.sourceStatus
    || data?.sourceStatus
    || payload?.status
    || data?.status
    || (Array.isArray(list) && list.length ? WILSY_CRM_SOURCE_STATUS.sourceLive : WILSY_CRM_SOURCE_STATUS.sourceRequired);

  return {
    ok: Boolean(payload?.ok ?? payload?.success ?? (sourceStatus !== WILSY_CRM_SOURCE_STATUS.sourceError)),
    moduleId: context.moduleId || data?.moduleId || payload?.moduleId || 'crm',
    tenantId: context.tenantId || data?.tenantId || payload?.tenantId || resolveWilsyCrmTenantId(context),
    items: Array.isArray(list) ? list : [],
    total: Number(data?.total ?? payload?.total ?? (Array.isArray(list) ? list.length : 0)) || 0,
    sourceStatus,
    routePosture: context.routePosture || data?.routePosture || payload?.routePosture || WILSY_CRM_ROUTE_POSTURE.live,
    receipt: payload?.receipt || data?.receipt || null,
    raw: payload,
    noFakeData: true
  };
};

/**
 * @function buildWilsyCrmSourceRequiredEnvelope
 * @description Builds an explicit SOURCE_REQUIRED envelope when a route, tenant, method or source is not available.
 * @param {Object} context - Envelope context.
 * @returns {Object} Source-required envelope.
 * @collaboration Ensures missing CRM backend capabilities are visible and never replaced by fake customer data.
 */
export const buildWilsyCrmSourceRequiredEnvelope = (context = {}) => {
  const moduleConfig = getWilsyCrmModuleById(context.moduleId || WILSY_CRM_MODULE_CATALOG[0]?.id);
  const tenantId = resolveWilsyCrmTenantId(context);

  return {
    ok: false,
    moduleId: moduleConfig.id,
    tenantId,
    items: [],
    total: 0,
    sourceStatus: context.sourceStatus || WILSY_CRM_SOURCE_STATUS.sourceRequired,
    routePosture: context.routePosture || WILSY_CRM_ROUTE_POSTURE.required,
    message: context.message || 'CRM source route required before live records can be shown.',
    route: buildWilsyCrmRouteContract(moduleConfig.id, context.action || 'list'),
    moduleEnvelope: buildWilsyCrmModuleEnvelope(moduleConfig.id, {
      tenantId,
      sourceStatus: context.sourceStatus || WILSY_CRM_SOURCE_STATUS.sourceRequired,
      action: context.action || 'list'
    }),
    receipt: {
      required: true,
      status: 'RECEIPT_ROUTE_REQUIRED',
      latestReceiptId: null
    },
    noFakeData: true
  };
};

/**
 * @function buildWilsyCrmHttpErrorEnvelope
 * @description Builds a CRM error envelope from failed HTTP calls.
 * @param {Error|Object} error - Error object.
 * @param {Object} context - Envelope context.
 * @returns {Object} Source error envelope.
 * @collaboration Keeps CRM failures visible without leaking secrets or fabricating fallback rows.
 */
export const buildWilsyCrmHttpErrorEnvelope = (error, context = {}) => {
  const moduleConfig = getWilsyCrmModuleById(context.moduleId || WILSY_CRM_MODULE_CATALOG[0]?.id);

  return {
    ok: false,
    moduleId: moduleConfig.id,
    tenantId: resolveWilsyCrmTenantId(context),
    items: [],
    total: 0,
    sourceStatus: context.status === 403 ? WILSY_CRM_SOURCE_STATUS.sourceForbidden : WILSY_CRM_SOURCE_STATUS.sourceError,
    routePosture: context.status === 404 ? WILSY_CRM_ROUTE_POSTURE.required : WILSY_CRM_ROUTE_POSTURE.degraded,
    status: context.status || error?.status || 0,
    message: error?.message || context.message || 'CRM command source error.',
    noFakeData: true
  };
};

/**
 * @function wilsyCrmFetchJson
 * @description Executes a tenant-scoped CRM fetch and returns a normalized JSON payload.
 * @param {string} path - API path.
 * @param {Object} options - Fetch options.
 * @returns {Promise<Object>} Parsed response payload.
 * @collaboration Centralizes CRM command HTTP behavior across modules, imports, exports and evidence routes.
 */
export const wilsyCrmFetchJson = async (path, options = {}) => {
  if (typeof fetch !== 'function') {
    return buildWilsyCrmSourceRequiredEnvelope({
      ...options,
      message: 'Browser fetch is unavailable for CRM command client.'
    });
  }

  const url = `${getWilsyCrmApiBaseUrl()}${path}`;
  const response = await fetch(url, {
    method: options.method || 'GET',
    headers: buildWilsyCrmHeaders(options),
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    credentials: options.credentials || 'include'
  });

  const payload = await safeParseWilsyCrmJson(response);

  if (!response.ok) {
    return buildWilsyCrmHttpErrorEnvelope(
      { message: payload?.message || payload?.error || `CRM HTTP ${response.status}` },
      { ...options, status: response.status }
    );
  }

  return payload;
};

/**
 * @function listWilsyCrmRecords
 * @description Lists tenant-scoped CRM records for one governed module.
 * @param {string} moduleId - CRM module id.
 * @param {Object} options - List options.
 * @returns {Promise<Object>} CRM record envelope.
 * @collaboration Provides the primary no-fake-data list command for CRMDashboard.
 */
export const listWilsyCrmRecords = async (moduleId, options = {}) => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);
  const query = buildWilsyCrmQueryString({
    tenantId: resolveWilsyCrmTenantId(options),
    page: options.page,
    pageSize: options.pageSize,
    limit: options.limit,
    search: options.search,
    sourceStatus: options.sourceStatus,
    sort: options.sort
  });

  const payload = await wilsyCrmFetchJson(`${WILSY_CRM_COMMAND_ENDPOINTS.moduleBase}/${moduleConfig.route}${query}`, {
    ...options,
    moduleId: moduleConfig.id,
    action: 'list',
    command: `crm.${moduleConfig.id}.list`
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: moduleConfig.id,
    tenantId: resolveWilsyCrmTenantId(options),
    routePosture: moduleConfig.routePosture
  });
};

/**
 * @function getWilsyCrmCommandCenter
 * @description Retrieves the CRM command center packet for the active tenant.
 * @param {Object} options - Command center options.
 * @returns {Promise<Object>} CRM command center envelope.
 * @collaboration Gives the CRM shell a single executive packet without inventing metrics.
 */
export const getWilsyCrmCommandCenter = async (options = {}) => {
  const query = buildWilsyCrmQueryString({
    tenantId: resolveWilsyCrmTenantId(options),
    limit: options.limit || 50
  });

  const payload = await wilsyCrmFetchJson(`${WILSY_CRM_COMMAND_ENDPOINTS.commandCenter}${query}`, {
    ...options,
    moduleId: 'command',
    action: 'command_center',
    command: 'crm.command.center'
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: 'command',
    tenantId: resolveWilsyCrmTenantId(options)
  });
};

/**
 * @function getWilsyCrmSourceRegistryEvidence
 * @description Retrieves source registry evidence for CRM connectors and module routes.
 * @param {Object} options - Evidence options.
 * @returns {Promise<Object>} Source registry evidence envelope.
 * @collaboration Makes connector gaps, stale sources and live sources visible to operators.
 */
export const getWilsyCrmSourceRegistryEvidence = async (options = {}) => {
  const query = buildWilsyCrmQueryString({
    tenantId: resolveWilsyCrmTenantId(options),
    limit: options.limit || 25
  });

  const payload = await wilsyCrmFetchJson(`${WILSY_CRM_COMMAND_ENDPOINTS.sourceRegistryEvidence}${query}`, {
    ...options,
    moduleId: 'evidence',
    action: 'source_registry',
    command: 'crm.source.registry.evidence'
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: 'evidence',
    tenantId: resolveWilsyCrmTenantId(options)
  });
};

/**
 * @function mutateWilsyCrmRecord
 * @description Runs a create, update or delete CRM command for one module.
 * @param {string} moduleId - CRM module id.
 * @param {string} action - create, update or delete.
 * @param {Object} record - Record payload.
 * @param {Object} options - Mutation options.
 * @returns {Promise<Object>} Mutation envelope.
 * @collaboration Forces material CRM mutations through tenant-scoped receipt-aware routes.
 */
export const mutateWilsyCrmRecord = async (moduleId, action, record = {}, options = {}) => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);
  const safeAction = normalizeWilsyCrmCommandValue(action || 'create');
  const id = record?.id || record?._id || options.id;
  const method = safeAction === 'delete' ? 'DELETE' : (safeAction === 'update' ? 'PATCH' : 'POST');
  const path = safeAction === 'create'
    ? `${WILSY_CRM_COMMAND_ENDPOINTS.moduleBase}/${moduleConfig.route}`
    : `${WILSY_CRM_COMMAND_ENDPOINTS.moduleBase}/${moduleConfig.route}/${encodeURIComponent(String(id || 'SOURCE_REQUIRED_ID'))}`;

  if (safeAction !== 'create' && !id) {
    return buildWilsyCrmSourceRequiredEnvelope({
      ...options,
      moduleId: moduleConfig.id,
      action: safeAction,
      message: `${moduleConfig.singular} id is required for ${safeAction}.`
    });
  }

  const payload = await wilsyCrmFetchJson(path, {
    ...options,
    method,
    moduleId: moduleConfig.id,
    action: safeAction,
    command: `crm.${moduleConfig.id}.${safeAction}`,
    body: {
      ...record,
      tenantId: resolveWilsyCrmTenantId(options),
      sourceStatus: record?.sourceStatus || WILSY_CRM_SOURCE_STATUS.sourcePending
    }
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: moduleConfig.id,
    tenantId: resolveWilsyCrmTenantId(options),
    routePosture: moduleConfig.routePosture
  });
};

/**
 * @function createWilsyCrmRecord
 * @description Creates a tenant-scoped CRM record through the command client.
 * @param {string} moduleId - CRM module id.
 * @param {Object} record - Record payload.
 * @param {Object} options - Request options.
 * @returns {Promise<Object>} Mutation envelope.
 * @collaboration Provides a direct create helper for future CRMDashboard wiring.
 */
export const createWilsyCrmRecord = (moduleId, record = {}, options = {}) => mutateWilsyCrmRecord(moduleId, 'create', record, options);

/**
 * @function updateWilsyCrmRecord
 * @description Updates a tenant-scoped CRM record through the command client.
 * @param {string} moduleId - CRM module id.
 * @param {Object} record - Record payload.
 * @param {Object} options - Request options.
 * @returns {Promise<Object>} Mutation envelope.
 * @collaboration Provides a direct update helper for future CRMDashboard wiring.
 */
export const updateWilsyCrmRecord = (moduleId, record = {}, options = {}) => mutateWilsyCrmRecord(moduleId, 'update', record, options);

/**
 * @function deleteWilsyCrmRecord
 * @description Deletes or archives a tenant-scoped CRM record through the command client.
 * @param {string} moduleId - CRM module id.
 * @param {string} id - Record id.
 * @param {Object} options - Request options.
 * @returns {Promise<Object>} Mutation envelope.
 * @collaboration Provides a direct delete helper for future CRMDashboard wiring.
 */
export const deleteWilsyCrmRecord = (moduleId, id, options = {}) => mutateWilsyCrmRecord(moduleId, 'delete', { id }, options);

/**
 * @function validateWilsyCrmImportVendor
 * @description Resolves an import vendor contract from the governed CRM import catalog.
 * @param {string} vendorId - Import vendor id.
 * @returns {Object} Import vendor contract.
 * @collaboration Keeps competitor migration posture explicit across HubSpot, Zoho, Zendesk and other sources.
 */
export const validateWilsyCrmImportVendor = vendorId => {
  const normalizedVendor = normalizeWilsyCrmCommandValue(vendorId || 'GENERIC_CRM').toUpperCase();

  return WILSY_CRM_IMPORT_VENDOR_CATALOG.find(vendor => vendor.id === normalizedVendor)
    || WILSY_CRM_IMPORT_VENDOR_CATALOG[0];
};

/**
 * @function previewWilsyCrmImportRecords
 * @description Sends CRM import rows to the preview route without committing records.
 * @param {string} moduleId - CRM module id.
 * @param {Array<Object>} records - Import records.
 * @param {Object} options - Import options.
 * @returns {Promise<Object>} Import preview envelope.
 * @collaboration Makes competitor migration safe by requiring preview before tenant data entry.
 */
export const previewWilsyCrmImportRecords = async (moduleId, records = [], options = {}) => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);
  const vendor = validateWilsyCrmImportVendor(options.vendor || options.vendorId || 'GENERIC_CRM');

  if (!Array.isArray(records) || records.length === 0) {
    return buildWilsyCrmSourceRequiredEnvelope({
      ...options,
      moduleId: moduleConfig.id,
      action: 'import_preview',
      message: 'Import preview requires records.'
    });
  }

  const payload = await wilsyCrmFetchJson(WILSY_CRM_COMMAND_ENDPOINTS.importPreview, {
    ...options,
    method: 'POST',
    moduleId: moduleConfig.id,
    action: 'import_preview',
    command: `crm.${moduleConfig.id}.import.preview`,
    body: {
      tenantId: resolveWilsyCrmTenantId(options),
      moduleId: moduleConfig.id,
      vendor,
      records,
      dedupeKey: options.dedupeKey || vendor.dedupeKeys?.[0] || 'externalId'
    }
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: moduleConfig.id,
    tenantId: resolveWilsyCrmTenantId(options)
  });
};

/**
 * @function importWilsyCrmRecords
 * @description Commits CRM import rows after preview and dedupe posture are available.
 * @param {string} moduleId - CRM module id.
 * @param {Array<Object>} records - Import records.
 * @param {Object} options - Import options.
 * @returns {Promise<Object>} Import envelope.
 * @collaboration Converts competitor CRM exports into tenant-scoped Wilsy CRM records with receipt posture.
 */
export const importWilsyCrmRecords = async (moduleId, records = [], options = {}) => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);
  const vendor = validateWilsyCrmImportVendor(options.vendor || options.vendorId || 'GENERIC_CRM');

  if (!options.previewAccepted) {
    return buildWilsyCrmSourceRequiredEnvelope({
      ...options,
      moduleId: moduleConfig.id,
      action: 'import',
      message: 'Import requires previewAccepted=true before records enter Wilsy OS CRM.'
    });
  }

  const payload = await wilsyCrmFetchJson(WILSY_CRM_COMMAND_ENDPOINTS.importCommit, {
    ...options,
    method: 'POST',
    moduleId: moduleConfig.id,
    action: 'import',
    command: `crm.${moduleConfig.id}.import`,
    body: {
      tenantId: resolveWilsyCrmTenantId(options),
      moduleId: moduleConfig.id,
      vendor,
      records,
      dedupeKey: options.dedupeKey || vendor.dedupeKeys?.[0] || 'externalId',
      previewAccepted: true
    }
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: moduleConfig.id,
    tenantId: resolveWilsyCrmTenantId(options)
  });
};

/**
 * @function exportWilsyCrmRecords
 * @description Requests a tenant-scoped CRM export envelope for one module.
 * @param {string} moduleId - CRM module id.
 * @param {Object} options - Export options.
 * @returns {Promise<Object>} Export envelope.
 * @collaboration Keeps CRM exports governed and auditable instead of raw data dumps.
 */
export const exportWilsyCrmRecords = async (moduleId, options = {}) => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);

  const payload = await wilsyCrmFetchJson(WILSY_CRM_COMMAND_ENDPOINTS.exportRecords, {
    ...options,
    method: 'POST',
    moduleId: moduleConfig.id,
    action: 'export',
    command: `crm.${moduleConfig.id}.export`,
    body: {
      tenantId: resolveWilsyCrmTenantId(options),
      moduleId: moduleConfig.id,
      format: options.format || 'csv',
      filters: options.filters || {},
      sourceStatus: options.sourceStatus
    }
  });

  return normalizeWilsyCrmEnvelope(payload, {
    moduleId: moduleConfig.id,
    tenantId: resolveWilsyCrmTenantId(options)
  });
};

/**
 * @function buildWilsyCrmCommandClientCapabilities
 * @description Builds the CRM command client capability map for diagnostics and dashboard readiness.
 * @returns {Object} Capability map.
 * @collaboration Gives investors and operators proof that CRM command routes are governed before data is shown.
 */
export const buildWilsyCrmCommandClientCapabilities = () => Object.freeze({
  version: WILSY_CRM_COMMAND_CLIENT_VERSION,
  moduleCount: WILSY_CRM_MODULE_CATALOG.length,
  tenantBoundary: WILSY_CRM_TENANT_BOUNDARY.noSharedDataDoctrine,
  sourceStatuses: Object.freeze(Object.values(WILSY_CRM_SOURCE_STATUS)),
  routePostures: Object.freeze(Object.values(WILSY_CRM_ROUTE_POSTURE)),
  endpoints: WILSY_CRM_COMMAND_ENDPOINTS,
  noFakeData: true,
  supports: Object.freeze({
    list: true,
    create: true,
    update: true,
    delete: true,
    commandCenter: true,
    sourceRegistryEvidence: true,
    importPreview: true,
    importCommit: true,
    export: true,
    competitorMigration: true,
    tenantScopedHeaders: true,
    bearerTokenPassthrough: true
  })
});

/**
 * @function assertWilsyCrmCommandClient
 * @description Validates command client readiness without making network calls.
 * @returns {Object} Command client readiness.
 * @collaboration Provides a deterministic frontend guard for the CRM command client.
 */
export const assertWilsyCrmCommandClient = () => {
  const issues = [];

  if (!WILSY_CRM_MODULE_CATALOG.length) issues.push('CRM module catalog is empty');
  if (!WILSY_CRM_COMMAND_ENDPOINTS.moduleBase) issues.push('CRM module base endpoint missing');
  if (WILSY_CRM_TENANT_BOUNDARY.noSharedDataDoctrine !== 'TENANTS_NEVER_SHARE_DATA') {
    issues.push('CRM tenant boundary doctrine mismatch');
  }

  return Object.freeze({
    ok: issues.length === 0,
    version: WILSY_CRM_COMMAND_CLIENT_VERSION,
    capability: buildWilsyCrmCommandClientCapabilities(),
    issues: Object.freeze(issues)
  });
};

export const WILSY_CRM_COMMAND_CLIENT_HEALTH = assertWilsyCrmCommandClient();

export const wilsyCrmCommandClient = Object.freeze({
  listRecords: listWilsyCrmRecords,
  getCommandCenter: getWilsyCrmCommandCenter,
  getSourceRegistryEvidence: getWilsyCrmSourceRegistryEvidence,
  createRecord: createWilsyCrmRecord,
  updateRecord: updateWilsyCrmRecord,
  deleteRecord: deleteWilsyCrmRecord,
  previewImportRecords: previewWilsyCrmImportRecords,
  importRecords: importWilsyCrmRecords,
  exportRecords: exportWilsyCrmRecords,
  buildHeaders: buildWilsyCrmHeaders,
  buildRouteContract: buildWilsyCrmRouteContract,
  buildSourceRequiredEnvelope: buildWilsyCrmSourceRequiredEnvelope,
  capabilities: buildWilsyCrmCommandClientCapabilities,
  assertReady: assertWilsyCrmCommandClient
});

export default wilsyCrmCommandClient;
