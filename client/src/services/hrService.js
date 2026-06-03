/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN HR SERVICE [V1.2.0-FULL-JSDOC]                                                                                    ║
 * ║ [EMPLOYEES | RECRUITMENT | PAYROLL | BENEFITS | PERFORMANCE | TIME‑OFF | PAGINATION | TELEMETRY | COMPLETE JSDOC]                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited HR API layer with complete personnel lifecycle.                        ║
 * ║ • AI Engineering (Gemini) – RECTIFIED: Hardened sanitizePayload against prototype pollution, corrected telemetry mappings,             ║
 * ║   and enforced explicit JSDoc pagination types. [2026-05-19]                                                                           ║
 * ║ • AI Engineering (DeepSeek) – DOCUMENTED: Added full JSDoc for all functions (internal utilities + exports).                         ║
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
 * Hardened payload sanitizer. Removes `undefined` values and blocks prototype pollution vectors.
 * @param {Object} obj - The payload to sanitise.
 * @returns {Object} A new object without `undefined` keys and without `__proto__` / `constructor` keys.
 * @example
 * sanitizePayload({ name: 'John', __proto__: { x: 1 } }) // => { name: 'John' }
 */
const sanitizePayload = (obj) => {
  if (!obj || typeof obj !== 'object') return obj;
  return Object.keys(obj).reduce((acc, key) => {
    if (key === '__proto__' || key === 'constructor') return acc;
    if (obj[key] !== undefined) acc[key] = obj[key];
    return acc;
  }, {});
};

/**
 * Central error handler for HR API calls: logs error, broadcasts telemetry fracture, rethrows.
 * @param {Error} error - The caught error (Axios error or generic).
 * @param {string} context - Name of the calling function (e.g., `getEmployees`).
 * @param {string} tenantId - Tenant ID for telemetry.
 * @param {string} failureEvent - Telemetry constant from `TEL_EVENTS.HR` (e.g., `TEL_EVENTS.HR.HYDRATION_FRACTURE`).
 * @param {Object} [extra={}] - Additional metadata to include in telemetry.
 * @throws {Error} Re‑throws the original error after logging.
 */
const handleApiError = async (error, context, tenantId, failureEvent, extra = {}) => {
  const message = error.response?.data?.message || error.message;
  logger.error(`[hrService] ${context} failed: ${message}`, { tenantId, ...extra });
  await broadcastTelemetry(tenantId, failureEvent, 'FRACTURE', context, { error: message, ...extra });
  throw error;
};

/**
 * Generic paginated GET helper with telemetry.
 * @param {string} endpoint - API endpoint (e.g., `/hr/employees`).
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params={}] - Query parameters (include `limit`, `offset` for pagination).
 * @param {string} successEvent - Telemetry success constant.
 * @param {string} failureEvent - Telemetry failure constant.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 *          Paginated result set.
 * @example
 * const { items, total } = await getResource('/hr/employees', 'TENANT_1', { limit: 20 });
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

    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `get${endpoint}`, { count: items.length, total, hasMore });
    return { items, total, limit, offset, hasMore };
  } catch (error) {
    await handleApiError(error, `get${endpoint}`, tenantId, failureEvent, { params });
    return { items: [], total: 0, limit: 0, offset: 0, hasMore: false };
  }
};

/**
 * Simple array‑only GET helper (backward compatibility). Uses `getResource` internally.
 * @param {string} endpoint - API endpoint.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params={}] - Query parameters.
 * @returns {Promise<Array>} Array of items (without pagination metadata).
 */
const getResourceArray = async (endpoint, tenantId, params = {}) => {
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);
  return items;
};

/**
 * Generic POST helper with telemetry and payload sanitisation.
 * @param {string} endpoint - API endpoint.
 * @param {Object} data - Request payload.
 * @param {string} tenantId - Tenant ID.
 * @param {string} successEvent - Telemetry constant for successful creation.
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<Object>} Created resource (server response).
 */
const postResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.post(endpoint, sanitized, { headers: { 'X-Tenant-ID': tenantId } });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `post${endpoint}`, { id: response.data?.id });
    return response.data;
  } catch (error) {
    await handleApiError(error, `post${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
};

/**
 * Generic PUT helper with telemetry and payload sanitisation.
 * @param {string} endpoint - API endpoint (including resource ID).
 * @param {Object} data - Request payload.
 * @param {string} tenantId - Tenant ID.
 * @param {string} successEvent - Telemetry constant for successful update.
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<Object>} Updated resource.
 */
const putResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.put(endpoint, sanitized, { headers: { 'X-Tenant-ID': tenantId } });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `put${endpoint}`, { id: response.data?.id });
    return response.data;
  } catch (error) {
    await handleApiError(error, `put${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
};

/**
 * Generic DELETE helper with telemetry.
 * @param {string} endpoint - API endpoint (including resource ID).
 * @param {string} tenantId - Tenant ID.
 * @param {string} successEvent - Telemetry constant for successful deletion.
 * @param {string} failureEvent - Telemetry constant for failure.
 * @returns {Promise<void>}
 */
const deleteResource = async (endpoint, tenantId, successEvent, failureEvent) => {
  try {
    await api.delete(endpoint, { headers: { 'X-Tenant-ID': tenantId } });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `delete${endpoint}`, {});
  } catch (error) {
    await handleApiError(error, `delete${endpoint}`, tenantId, failureEvent);
    throw error;
  }
};

// ============================================================================
// EMPLOYEES
// ============================================================================

/**
 * Retrieves a paginated list of employees.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / filter parameters.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getEmployees = (tenantId, params = {}) =>
  getResource('/hr/employees', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * Retrieves employees as a plain array (no pagination metadata).
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Query parameters.
 * @returns {Promise<Array>}
 */
export const getEmployeesArray = (tenantId, params = {}) => getResourceArray('/hr/employees', tenantId, params);

/**
 * Creates a new employee.
 * @param {Object} data - Employee data.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Created employee.
 */
export const createEmployee = (data, tenantId) =>
  postResource('/hr/employees', data, tenantId, TEL_EVENTS.HR.EMPLOYEE_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Updates an existing employee.
 * @param {string} id - Employee ID.
 * @param {Object} data - Updated fields.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated employee.
 */
export const updateEmployee = (id, data, tenantId) =>
  putResource(`/hr/employees/${id}`, data, tenantId, TEL_EVENTS.HR.EMPLOYEE_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Deletes an employee.
 * @param {string} id - Employee ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<void>}
 */
export const deleteEmployee = (id, tenantId) =>
  deleteResource(`/hr/employees/${id}`, tenantId, TEL_EVENTS.HR.EMPLOYEE_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ============================================================================
// RECRUITMENT (Candidates / Openings)
// ============================================================================

/**
 * Retrieves paginated list of recruitment candidates.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / filter parameters.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getRecruitmentCandidates = (tenantId, params = {}) =>
  getResource('/hr/recruitment/candidates', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * Creates a new candidate.
 * @param {Object} data - Candidate data (name, contact, etc.).
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Created candidate.
 */
export const createCandidate = (data, tenantId) =>
  postResource('/hr/recruitment/candidates', data, tenantId, TEL_EVENTS.HR.CANDIDATE_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Updates the stage of a candidate (e.g., "screening" → "interview").
 * @param {string} id - Candidate ID.
 * @param {string} stage - New stage name.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated candidate.
 */
export const updateCandidateStage = (id, stage, tenantId) =>
  putResource(`/hr/recruitment/candidates/${id}/stage`, { stage }, tenantId, TEL_EVENTS.HR.RECRUITMENT_STAGE_CHANGE, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Deletes a candidate.
 * @param {string} id - Candidate ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<void>}
 */
export const deleteCandidate = (id, tenantId) =>
  deleteResource(`/hr/recruitment/candidates/${id}`, tenantId, TEL_EVENTS.HR.CANDIDATE_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Retrieves paginated list of job openings.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / filter parameters.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getJobOpenings = (tenantId, params = {}) =>
  getResource('/hr/recruitment/openings', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * Creates a new job opening.
 * @param {Object} data - Job opening data (title, department, description, etc.).
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Created job opening.
 */
export const createJobOpening = (data, tenantId) =>
  postResource('/hr/recruitment/openings', data, tenantId, TEL_EVENTS.HR.JOB_OPENING_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Updates a job opening.
 * @param {string} id - Job opening ID.
 * @param {Object} data - Updated fields.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated job opening.
 */
export const updateJobOpening = (id, data, tenantId) =>
  putResource(`/hr/recruitment/openings/${id}`, data, tenantId, TEL_EVENTS.HR.JOB_OPENING_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Deletes a job opening.
 * @param {string} id - Job opening ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<void>}
 */
export const deleteJobOpening = (id, tenantId) =>
  deleteResource(`/hr/recruitment/openings/${id}`, tenantId, TEL_EVENTS.HR.JOB_OPENING_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ============================================================================
// PAYROLL SUMMARY
// ============================================================================

/**
 * Retrieves paginated payroll summary records.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / period filter.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getPayrollSummary = (tenantId, params = {}) =>
  getResource('/hr/payroll/summary', tenantId, params, TEL_EVENTS.HR.PAYROLL_SYNC_SUCCESS, TEL_EVENTS.HR.PAYROLL_SYNC_FRACTURE);

/**
 * Triggers a manual payroll synchronisation with the accounting ledger.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Sync result.
 */
export const syncPayroll = (tenantId) =>
  postResource('/hr/payroll/sync', {}, tenantId, TEL_EVENTS.HR.PAYROLL_SYNC_SUCCESS, TEL_EVENTS.HR.PAYROLL_SYNC_FRACTURE);

// ============================================================================
// BENEFITS
// ============================================================================

/**
 * Retrieves paginated list of employee benefits.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / filter parameters.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getBenefits = (tenantId, params = {}) =>
  getResource('/hr/benefits', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * Creates a new benefit (e.g., health insurance, retirement plan).
 * @param {Object} data - Benefit data.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Created benefit.
 */
export const createBenefit = (data, tenantId) =>
  postResource('/hr/benefits', data, tenantId, TEL_EVENTS.HR.BENEFIT_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Updates an existing benefit.
 * @param {string} id - Benefit ID.
 * @param {Object} data - Updated fields.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated benefit.
 */
export const updateBenefit = (id, data, tenantId) =>
  putResource(`/hr/benefits/${id}`, data, tenantId, TEL_EVENTS.HR.BENEFIT_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Deletes a benefit.
 * @param {string} id - Benefit ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<void>}
 */
export const deleteBenefit = (id, tenantId) =>
  deleteResource(`/hr/benefits/${id}`, tenantId, TEL_EVENTS.HR.BENEFIT_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ============================================================================
// PERFORMANCE REVIEWS
// ============================================================================

/**
 * Retrieves paginated list of performance reviews.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / employee filter.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getPerformanceReviews = (tenantId, params = {}) =>
  getResource('/hr/performance', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * Creates a new performance review.
 * @param {Object} data - Review data (employeeId, reviewer, rating, comments, period).
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Created performance review.
 */
export const createPerformanceReview = (data, tenantId) =>
  postResource('/hr/performance', data, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Updates an existing performance review.
 * @param {string} id - Review ID.
 * @param {Object} data - Updated fields.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated performance review.
 */
export const updatePerformanceReview = (id, data, tenantId) =>
  putResource(`/hr/performance/${id}`, data, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Deletes a performance review.
 * @param {string} id - Review ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<void>}
 */
export const deletePerformanceReview = (id, tenantId) =>
  deleteResource(`/hr/performance/${id}`, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ============================================================================
// TIME‑OFF REQUESTS
// ============================================================================

/**
 * Retrieves paginated list of time‑off requests.
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Pagination / status filter.
 * @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>}
 */
export const getTimeOffRequests = (tenantId, params = {}) =>
  getResource('/hr/timeoff', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * Submits a new time‑off request.
 * @param {Object} data - Request details (employeeId, startDate, endDate, type, reason).
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Created time‑off request.
 */
export const createTimeOffRequest = (data, tenantId) =>
  postResource('/hr/timeoff', data, tenantId, TEL_EVENTS.HR.TIME_OFF_REQUESTED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updateTimeOffRequest = (id, data, tenantId) =>
  putResource(`/hr/timeoff/${id}`, data, tenantId, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Approves a pending time‑off request.
 * @param {string} id - Request ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated request.
 */
export const approveTimeOff = (id, tenantId) =>
  putResource(`/hr/timeoff/${id}/approve`, {}, tenantId, TEL_EVENTS.HR.TIME_OFF_APPROVED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Denies a pending time‑off request.
 * @param {string} id - Request ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<Object>} Updated request.
 */
export const denyTimeOff = (id, tenantId) =>
  putResource(`/hr/timeoff/${id}/deny`, {}, tenantId, TEL_EVENTS.HR.TIME_OFF_DENIED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * Deletes a time‑off request (only allowed for pending requests).
 * @param {string} id - Request ID.
 * @param {string} tenantId - Tenant ID.
 * @returns {Promise<void>}
 */
export const deleteTimeOffRequest = (id, tenantId) =>
  deleteResource(`/hr/timeoff/${id}`, tenantId, TEL_EVENTS.HR.TIME_OFF_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ============================================================================
// DEFAULT EXPORT (object with all methods)
// ============================================================================

export default {
  getEmployees,
  getEmployeesArray,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  getRecruitmentCandidates,
  createCandidate,
  updateCandidateStage,
  deleteCandidate,
  getJobOpenings,
  createJobOpening,
  updateJobOpening,
  deleteJobOpening,
  getPayrollSummary,
  syncPayroll,
  getBenefits,
  createBenefit,
  updateBenefit,
  deleteBenefit,
  getPerformanceReviews,
  createPerformanceReview,
  updatePerformanceReview,
  deletePerformanceReview,
  getTimeOffRequests,
  createTimeOffRequest,
  updateTimeOffRequest,
  approveTimeOff,
  denyTimeOff,
  deleteTimeOffRequest,
};
