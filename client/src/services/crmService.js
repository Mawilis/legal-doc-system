/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN CRM SERVICE [V2.0.0-FORENSIC]                                                                                    ║
 * ║ [DYNAMIC TELEMETRY | PAGINATION READY | PRE‑FLIGHT SANITIZATION | NO STRING MANIPULATION]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ WHY FORTUNE 500 COMPANIES ABANDON PROPRIETARY CRM APIS FOR WILSY OS CRM SERVICE:                                                      ║
 * ║   • COMPETITORS HAVE FRAGMENTED API CLIENTS – WE PROVIDE A UNIFIED, TYPE‑SAFE SERVICE FOR 11 CRM OBJECTS                             ║
 * ║   • COMPETITORS LACK TELEMETRY OUT OF THE BOX – EVERY API CALL BROADCASTS TO SOVEREIGN TELEMETRY                                     ║
 * ║   • COMPETITORS' ERROR HANDLING IS INCONSISTENT – WE STANDARDISE FRACTURE REPORTING WITH TRACE IDS                                   ║
 * ║   • COMPETITORS FORCE YOU TO WRITE FETCH LOGIC – WE ABSTRACT ALL ENDPOINTS BEHIND SEMANTIC METHOD NAMES                               ║
 * ║   • COMPETITORS IGNORE PAGINATION – OUR SERVICE RETURNS `{ items, total, limit, offset, hasMore }` READY FOR LARGE DATASETS           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/crmService.js                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited API layer for all CRM operations.                                    ║
 * ║ • AI Engineering (DeepSeek) – INNOVATED: Built full CRUD service with telemetry hooks, error standardisation, and forensic headers.  ║
 * ║ • AI Engineering (DeepSeek) – FORENSIC UPGRADE: Dynamic telemetry routing, pagination readiness, payload sanitisation.               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';
import logger from '../utils/logger';
import { TEL_EVENTS } from '../constants/telemetryConstants';

// ============================================================================
// UTILITIES
// ============================================================================

/**
 * Removes undefined values from an object to avoid backend validation errors.
 * @param {Object} obj - The payload to sanitise.
 * @returns {Object} A new object without undefined keys.
 */
const sanitizePayload = (obj) => {
  if (!obj || typeof obj !== 'object') return obj;
  return Object.keys(obj).reduce((acc, key) => {
    if (obj[key] !== undefined) acc[key] = obj[key];
    return acc;
  }, {});
};

/**
 * Generic error handler with specific telemetry event.
 * @param {Error} error - Caught error.
 * @param {string} context - Function name.
 * @param {string} tenantId - Tenant ID.
 * @param {string} failureEvent - Telemetry constant for failure (e.g., TEL_EVENTS.CRM.LEAD_FRACTURE).
 * @param {Object} extra - Extra metadata.
 * @throws {Error} Rethrows after logging.
 */
const handleApiError = async (error, context, tenantId, failureEvent, extra = {}) => {
  const message = error.response?.data?.message || error.message;
  logger.error(`[crmService] ${context} failed: ${message}`, { tenantId, ...extra });
  await broadcastTelemetry(tenantId, failureEvent, 'FRACTURE', context, {
    error: message,
    ...extra
  });
  throw error;
};

/**
 * Generic GET helper (pagination‑aware) with telemetry.
 * @param {string} endpoint - API endpoint.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} params - Query params (include limit, offset).
 * @param {string} successEvent - Telemetry constant for success (e.g., TEL_EVENTS.CRM.HYDRATION_SUCCESS).
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
const getResource = async (endpoint, tenantId, params = {}, successEvent, failureEvent) => {
  try {
    const response = await api.get(endpoint, {
      params: { tenantId, ...params },
      headers: { 'X-Tenant-ID': tenantId }
    });
    const data = response.data;
    const items = Array.isArray(data) ? data : (data.items || data.data || []);
    const total = data.total ?? items.length;
    const limit = data.limit ?? params.limit ?? 50;
    const offset = data.offset ?? params.offset ?? 0;
    const hasMore = data.hasMore ?? (offset + limit < total);
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `get${endpoint}`, {
      count: items.length,
      total,
      hasMore
    });
    return { items, total, limit, offset, hasMore };
  } catch (error) {
    await handleApiError(error, `get${endpoint}`, tenantId, failureEvent, { params });
    return { items: [], total: 0, limit: 0, offset: 0, hasMore: false };
  }
};

/**
 * Legacy array-only GET (for backward compatibility with existing dashboards).
 * @param {string} endpoint - API endpoint.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} params - Query params.
 * @returns {Promise<Array>}
 */
const getResourceArray = async (endpoint, tenantId, params = {}) => {
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
  return items;
};

/**
 * Generic POST helper with dynamic telemetry.
 * @param {string} endpoint - API endpoint.
 * @param {Object} data - Request payload.
 * @param {string} tenantId - Tenant ID.
 * @param {string} successEvent - Telemetry constant for creation success.
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<Object>} Created resource.
 */
const postResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.post(endpoint, sanitized, {
      headers: { 'X-Tenant-ID': tenantId }
    });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `post${endpoint}`, {
      id: response.data?.id
    });
    return response.data;
  } catch (error) {
    await handleApiError(error, `post${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
};

/**
 * Generic PUT helper with dynamic telemetry.
 * @param {string} endpoint - API endpoint (with id).
 * @param {Object} data - Request payload.
 * @param {string} tenantId - Tenant ID.
 * @param {string} successEvent - Telemetry constant for update success.
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<Object>} Updated resource.
 */
const putResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.put(endpoint, sanitized, {
      headers: { 'X-Tenant-ID': tenantId }
    });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `put${endpoint}`, {
      id: response.data?.id
    });
    return response.data;
  } catch (error) {
    await handleApiError(error, `put${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
};

/**
 * Generic DELETE helper with dynamic telemetry.
 * @param {string} endpoint - API endpoint (with id).
 * @param {string} tenantId - Tenant ID.
 * @param {string} successEvent - Telemetry constant for delete success.
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<void>}
 */
const deleteResource = async (endpoint, tenantId, successEvent, failureEvent) => {
  try {
    await api.delete(endpoint, {
      headers: { 'X-Tenant-ID': tenantId }
    });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `delete${endpoint}`, {});
  } catch (error) {
    await handleApiError(error, `delete${endpoint}`, tenantId, failureEvent);
    throw error;
  }
};

export const importRecords = async (resourceType, tenantId, records = [], options = {}) => {
  try {
    const response = await api.post(`/crm/${resourceType}/import`, {
      records,
      mode: options.mode || 'upsert',
      dedupeKey: options.dedupeKey,
      sourceSystem: options.sourceSystem
    }, {
      headers: { 'X-Tenant-ID': tenantId }
    });
    await broadcastTelemetry(tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, 'SUCCESS', `importCRM${resourceType}`, {
      received: records.length,
      inserted: response.data?.inserted || 0,
      updated: response.data?.updated || 0
    });
    return response.data;
  } catch (error) {
    await handleApiError(error, `importCRM${resourceType}`, tenantId, TEL_EVENTS.CRM.HYDRATION_FRACTURE, {
      count: records.length
    });
    throw error;
  }
};

export const previewImportRecords = async (resourceType, tenantId, records = [], options = {}) => {
  try {
    const response = await api.post(`/crm/${resourceType}/preview-import`, {
      records,
      dedupeKey: options.dedupeKey,
      sourceSystem: options.sourceSystem
    }, {
      headers: { 'X-Tenant-ID': tenantId }
    });
    return response.data;
  } catch (error) {
    await handleApiError(error, `previewCRM${resourceType}`, tenantId, TEL_EVENTS.CRM.HYDRATION_FRACTURE, {
      count: records.length
    });
    throw error;
  }
};

export const getCrmSchema = async (tenantId) => {
  const response = await api.get('/crm/schema', {
    params: { tenantId },
    headers: { 'X-Tenant-ID': tenantId }
  });
  return response.data;
};

export const getCrmSummary = async (tenantId) => {
  const response = await api.get('/crm/summary', {
    params: { tenantId },
    headers: { 'X-Tenant-ID': tenantId }
  });
  return response.data;
};

// ============================================================================
// EXPORTED METHODS (One per CRM object, with exact telemetry constants)
// ============================================================================

// ----- Leads -----
export const getLeads = (tenantId, params = {}) => getResource('/crm/leads', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.LEAD_FRACTURE);
export const getLeadsArray = (tenantId, params = {}) => getResourceArray('/crm/leads', tenantId, params);
export const createLead = (data, tenantId) => postResource('/crm/leads', data, tenantId, TEL_EVENTS.CRM.LEAD_CREATED, TEL_EVENTS.CRM.LEAD_FRACTURE);
export const updateLead = (id, data, tenantId) => putResource(`/crm/leads/${id}`, data, tenantId, TEL_EVENTS.CRM.LEAD_UPDATED, TEL_EVENTS.CRM.LEAD_FRACTURE);
export const deleteLead = (id, tenantId) => deleteResource(`/crm/leads/${id}`, tenantId, TEL_EVENTS.CRM.LEAD_DELETED, TEL_EVENTS.CRM.LEAD_FRACTURE);

// ----- Contacts -----
export const getContacts = (tenantId, params = {}) => getResource('/crm/contacts', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getContactsArray = (tenantId, params = {}) => getResourceArray('/crm/contacts', tenantId, params);
export const createContact = (data, tenantId) => postResource('/crm/contacts', data, tenantId, TEL_EVENTS.CRM.CONTACT_CREATED, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateContact = (id, data, tenantId) => putResource(`/crm/contacts/${id}`, data, tenantId, TEL_EVENTS.CRM.CONTACT_UPDATED, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteContact = (id, tenantId) => deleteResource(`/crm/contacts/${id}`, tenantId, TEL_EVENTS.CRM.CONTACT_DELETED, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Accounts -----
export const getAccounts = (tenantId, params = {}) => getResource('/crm/accounts', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getAccountsArray = (tenantId, params = {}) => getResourceArray('/crm/accounts', tenantId, params);
export const createAccount = (data, tenantId) => postResource('/crm/accounts', data, tenantId, TEL_EVENTS.CRM.ACCOUNT_CREATED, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateAccount = (id, data, tenantId) => putResource(`/crm/accounts/${id}`, data, tenantId, TEL_EVENTS.CRM.ACCOUNT_UPDATED, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteAccount = (id, tenantId) => deleteResource(`/crm/accounts/${id}`, tenantId, TEL_EVENTS.CRM.ACCOUNT_DELETED, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Deals -----
export const getDeals = (tenantId, params = {}) => getResource('/crm/deals', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.DEAL_FRACTURE);
export const getDealsArray = (tenantId, params = {}) => getResourceArray('/crm/deals', tenantId, params);
export const createDeal = (data, tenantId) => postResource('/crm/deals', data, tenantId, TEL_EVENTS.CRM.DEAL_CREATED, TEL_EVENTS.CRM.DEAL_FRACTURE);
export const updateDeal = (id, data, tenantId) => putResource(`/crm/deals/${id}`, data, tenantId, TEL_EVENTS.CRM.DEAL_PROMOTED, TEL_EVENTS.CRM.DEAL_FRACTURE);
export const deleteDeal = (id, tenantId) => deleteResource(`/crm/deals/${id}`, tenantId, TEL_EVENTS.CRM.DEAL_LOST, TEL_EVENTS.CRM.DEAL_FRACTURE);

// ----- Tasks -----
export const getTasks = (tenantId, params = {}) => getResource('/crm/tasks', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getTasksArray = (tenantId, params = {}) => getResourceArray('/crm/tasks', tenantId, params);
export const createTask = (data, tenantId) => postResource('/crm/tasks', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateTask = (id, data, tenantId) => putResource(`/crm/tasks/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteTask = (id, tenantId) => deleteResource(`/crm/tasks/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Meetings -----
export const getMeetings = (tenantId, params = {}) => getResource('/crm/meetings', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getMeetingsArray = (tenantId, params = {}) => getResourceArray('/crm/meetings', tenantId, params);
export const createMeeting = (data, tenantId) => postResource('/crm/meetings', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateMeeting = (id, data, tenantId) => putResource(`/crm/meetings/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteMeeting = (id, tenantId) => deleteResource(`/crm/meetings/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Calls -----
export const getCalls = (tenantId, params = {}) => getResource('/crm/calls', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getCallsArray = (tenantId, params = {}) => getResourceArray('/crm/calls', tenantId, params);
export const createCall = (data, tenantId) => postResource('/crm/calls', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateCall = (id, data, tenantId) => putResource(`/crm/calls/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteCall = (id, tenantId) => deleteResource(`/crm/calls/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Campaigns -----
export const getCampaigns = (tenantId, params = {}) => getResource('/crm/campaigns', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getCampaignsArray = (tenantId, params = {}) => getResourceArray('/crm/campaigns', tenantId, params);
export const createCampaign = (data, tenantId) => postResource('/crm/campaigns', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateCampaign = (id, data, tenantId) => putResource(`/crm/campaigns/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteCampaign = (id, tenantId) => deleteResource(`/crm/campaigns/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Documents -----
export const getDocuments = (tenantId, params = {}) => getResource('/crm/documents', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getDocumentsArray = (tenantId, params = {}) => getResourceArray('/crm/documents', tenantId, params);
export const createDocument = (data, tenantId) => postResource('/crm/documents', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateDocument = (id, data, tenantId) => putResource(`/crm/documents/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteDocument = (id, tenantId) => deleteResource(`/crm/documents/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Visits -----
export const getVisits = (tenantId, params = {}) => getResource('/crm/visits', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getVisitsArray = (tenantId, params = {}) => getResourceArray('/crm/visits', tenantId, params);
export const createVisit = (data, tenantId) => postResource('/crm/visits', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateVisit = (id, data, tenantId) => putResource(`/crm/visits/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteVisit = (id, tenantId) => deleteResource(`/crm/visits/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Projects -----
export const getProjects = (tenantId, params = {}) => getResource('/crm/projects', tenantId, params, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const getProjectsArray = (tenantId, params = {}) => getResourceArray('/crm/projects', tenantId, params);
export const createProject = (data, tenantId) => postResource('/crm/projects', data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const updateProject = (id, data, tenantId) => putResource(`/crm/projects/${id}`, data, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
export const deleteProject = (id, tenantId) => deleteResource(`/crm/projects/${id}`, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);

// ----- Generic delete (fallback) -----
export const deleteRecord = (resourceType, id, tenantId) => {
  const endpoint = `/crm/${resourceType}/${id}`;
  return deleteResource(endpoint, tenantId, TEL_EVENTS.CRM.HYDRATION_SUCCESS, TEL_EVENTS.CRM.HYDRATION_FRACTURE);
};

export default {
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
  previewImportRecords,
  importRecords,
  getCrmSchema,
  getCrmSummary,
  deleteRecord
};
