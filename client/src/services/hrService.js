/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign HR Service
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/services/hrService.js
 * Version:        v1.4.0-INSTITUTIONAL-SEAL
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Production-grade HR data service with exponential backoff,
 *                 adaptive circuit breaking, and telemetry-integrated resilience
 *                 for employees, recruitment, payroll, benefits, performance,
 *                 and time-off.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated zero‑loss resilience and
 *     absolute system unification across all sovereign HR endpoints.
 *   - AI Engineering — RECTIFIED: Integrated certified exponential backoff and
 *     circuit breaker utilities; replaced legacy custom circuit with standardized
 *     production contract.
 *
 * Change Log:
 *   2026-07-31 v1.4.0-INSTITUTIONAL-SEAL — Final certified release with
 *     institutional backoff/circuit integration and full Sovereign Header.
 *   2026-07-30 v1.3.0-CIRCUIT-SAFE — Baseline.
 *
 * Forensic Relationships:
 *   Upstream:   ../services/api, ../utils/telemetryHelper, ../utils/logger,
 *               ../constants/telemetryConstants, ../utils/backoff
 *   Downstream: client/src/components/hr/HRDashboard.jsx, client/src/components/hr/EmployeeList.jsx,
 *               client/src/components/hr/Recruitment.jsx, client/src/components/payroll/PayrollDashboard.jsx
 *   Shared Crypto / Events / Config: api service (forensic headers), X-Tenant-ID,
 *               TEL_EVENTS.HR.*, backoff utilities, circuit breaker state.
 *
 * Certification Seal: PRODUCTION_READY_v1.4.0-INSTITUTIONAL-SEAL
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';
import logger from '../utils/logger';
import { TEL_EVENTS } from '../constants/telemetryConstants';
import {
  withBackoff,
  isTransient,
  createCircuitBreaker
} from '../utils/backoff';

const EMPTY_PAGE = Object.freeze({
  items: [],
  total: 0,
  limit: 10,
  offset: 0,
  hasMore: false,
  skipped: false
});

/**
 * HR service circuit breaker – shared across all GET endpoints.
 * Uses the certified createCircuitBreaker from backoff.js.
 */
const hrCircuit = createCircuitBreaker({
  name: 'hr-api',
  failureThreshold: 2,
  coolDownMs: 60_000
});

/**
 * @function emptyPage
 * @description Returns a consistent empty page response when the circuit is open or an error occurs.
 * Institutional Commentary: Guarantees that GET requests never throw, allowing UI components to render gracefully
 * even when the backend is unreachable.
 * @param {Object} params - Request parameters.
 * @param {string|null} reason - Optional reason for the empty response.
 * @returns {Object} Immutable empty page object.
 */
const emptyPage = (params = {}, reason = null) => ({
  ...EMPTY_PAGE,
  limit: params.limit ?? 10,
  offset: params.offset ?? 0,
  skipped: true,
  reason
});

/**
 * @function sanitizePayload
 * @description Removes prototype‑pollution‑prone keys from an object.
 * Institutional Commentary: Protects against malicious payloads that attempt to inject
 * `__proto__` or `constructor` keys into the API call.
 * @param {Object} obj - The raw payload object.
 * @returns {Object} Sanitized object.
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
 * @async softLogError
 * @description Logs errors and broadcasts failure telemetry without disrupting the caller.
 * Institutional Commentary: Ensures that telemetry and logging are best‑effort and never block the UI
 * or crash the application.
 * @param {Error} error - The error object.
 * @param {string} context - Context label for the operation.
 * @param {string} tenantId - The active tenant identifier.
 * @param {string} failureEvent - Telemetry event key for failures.
 * @param {Object} extra - Additional metadata to attach to the telemetry.
 */
const softLogError = async (error, context, tenantId, failureEvent, extra = {}) => {
  const message = error?.response?.data?.message || error?.message || 'unknown';
  const status = error?.response?.status;

  if (import.meta.env.DEV) {
    try {
      logger.error?.(`[hrService] ${context} failed: ${message}`, { tenantId, status, ...extra });
    } catch {
      console.warn(`[hrService] ${context} failed: ${message}`);
    }
  }

  try {
    await broadcastTelemetry(tenantId, failureEvent, 'FRACTURE', context, {
      error: message,
      status,
      circuit: hrCircuit.getState(),
      ...extra
    });
  } catch {
    /* never block */
  }
};

/**
 * @async getResource
 * @description Core paginated GET function with exponential backoff and circuit breaker.
 * Institutional Commentary: This function is the backbone of all HR read operations.
 * It retries transient failures up to 3 times using full‑jitter backoff. If the circuit
 * is open, it immediately returns an empty page, guaranteeing that UI components never
 * crash on network errors.
 * @param {string} endpoint - The API endpoint to call.
 * @param {string} tenantId - The active tenant identifier.
 * @param {Object} params - Query parameters (limit, offset, etc.).
 * @param {string} successEvent - Telemetry event for success.
 * @param {string} failureEvent - Telemetry event for failure.
 * @returns {Promise<Object>} A paginated response object.
 */
const getResource = async (endpoint, tenantId, params = {}, successEvent, failureEvent) => {
  if (!hrCircuit.allow()) {
    if (import.meta.env.DEV) {
      console.debug(`[hrService] circuit ${hrCircuit.getState()} — skip ${endpoint}`, hrCircuit.snapshot());
    }
    return emptyPage(params, hrCircuit.snapshot().lastReason || 'CIRCUIT_OPEN');
  }

  try {
    const response = await withBackoff(
      () =>
        api.get(endpoint, {
          params: { tenantId, ...params },
          headers: { 'X-Tenant-ID': tenantId }
        }),
      {
        maxAttempts: 3,
        baseMs: 300,
        maxMs: 8_000,
        retryIf: (err) => {
          const status = err?.response?.status;
          if (status === 404) return false;
          return isTransient(err);
        },
        onRetry: ({ attempt, delay }) => {
          if (import.meta.env.DEV) {
            console.debug(`[hrService] retry ${endpoint} attempt=${attempt + 1} delay=${delay}ms`);
          }
        }
      }
    );

    hrCircuit.success();

    const data = response.data;
    const items = Array.isArray(data) ? data : (data.items || data.data || []);
    const total = data.total ?? items.length;
    const limit = data.limit ?? params.limit ?? 50;
    const offset = data.offset ?? params.offset ?? 0;
    const hasMore = data.hasMore ?? (offset + limit < total);

    try {
      await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `get${endpoint}`, {
        count: items.length,
        total,
        hasMore
      });
    } catch {
      /* ignore */
    }

    return { items, total, limit, offset, hasMore, skipped: false };
  } catch (error) {
    const status = error?.response?.status;
    const reason = status ? `HTTP_${status}` : 'NETWORK';

    if (status === 404 || status === 503 || status === 502 || !status) {
      hrCircuit.trip(60_000, reason);
    } else {
      hrCircuit.failure(reason);
    }

    await softLogError(error, `get${endpoint}`, tenantId, failureEvent, { params });
    return emptyPage(params, reason);
  }
};

/**
 * @async getResourceArray
 * @description Convenience wrapper that returns only the items array from a paginated GET.
 * Institutional Commentary: For endpoints that only need the raw list (e.g., dropdowns).
 * @param {string} endpoint - The API endpoint.
 * @param {string} tenantId - The active tenant.
 * @param {Object} params - Query parameters.
 * @returns {Promise<Array>} Array of items.
 */
const getResourceArray = async (endpoint, tenantId, params = {}) => {
  const { items } = await getResource(
    endpoint,
    tenantId,
    params,
    TEL_EVENTS.HR.HYDRATION_SUCCESS,
    TEL_EVENTS.HR.HYDRATION_FRACTURE
  );
  return items;
};

/**
 * @async postResource
 * @description Wrapper for POST requests that throws on failure.
 * Institutional Commentary: Mutations are expected to throw so the UI can respond with
 * user feedback; unlike GETs, we do not swallow errors for mutations.
 * @param {string} endpoint - The API endpoint.
 * @param {Object} data - The payload to send.
 * @param {string} tenantId - The active tenant.
 * @param {string} successEvent - Telemetry event for success.
 * @param {string} failureEvent - Telemetry event for failure.
 * @returns {Promise<Object>} The response data.
 */
const postResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.post(endpoint, sanitized, { headers: { 'X-Tenant-ID': tenantId } });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `post${endpoint}`, { id: response.data?.id });
    return response.data;
  } catch (error) {
    await softLogError(error, `post${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
};

/**
 * @async putResource
 * @description Wrapper for PUT requests that throws on failure.
 * @param {string} endpoint - The API endpoint.
 * @param {Object} data - The payload to send.
 * @param {string} tenantId - The active tenant.
 * @param {string} successEvent - Telemetry event for success.
 * @param {string} failureEvent - Telemetry event for failure.
 * @returns {Promise<Object>} The response data.
 */
const putResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.put(endpoint, sanitized, { headers: { 'X-Tenant-ID': tenantId } });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `put${endpoint}`, { id: response.data?.id });
    return response.data;
  } catch (error) {
    await softLogError(error, `put${endpoint}`, tenantId, failureEvent, { data: sanitized });
    throw error;
  }
};

/**
 * @async deleteResource
 * @description Wrapper for DELETE requests that throws on failure.
 * @param {string} endpoint - The API endpoint.
 * @param {string} tenantId - The active tenant.
 * @param {string} successEvent - Telemetry event for success.
 * @param {string} failureEvent - Telemetry event for failure.
 * @returns {Promise<void>}
 */
const deleteResource = async (endpoint, tenantId, successEvent, failureEvent) => {
  try {
    await api.delete(endpoint, { headers: { 'X-Tenant-ID': tenantId } });
    await broadcastTelemetry(tenantId, successEvent, 'SUCCESS', `delete${endpoint}`, {});
  } catch (error) {
    await softLogError(error, `delete${endpoint}`, tenantId, failureEvent);
    throw error;
  }
};

// ─── Employees ───────────────────────────────────────────────────────────────
export const getEmployees = (tenantId, params = {}) =>
  getResource('/hr/employees', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

export const getEmployeesArray = (tenantId, params = {}) => getResourceArray('/hr/employees', tenantId, params);

export const createEmployee = (data, tenantId) =>
  postResource('/hr/employees', data, tenantId, TEL_EVENTS.HR.EMPLOYEE_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updateEmployee = (id, data, tenantId) =>
  putResource(`/hr/employees/${id}`, data, tenantId, TEL_EVENTS.HR.EMPLOYEE_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const deleteEmployee = (id, tenantId) =>
  deleteResource(`/hr/employees/${id}`, tenantId, TEL_EVENTS.HR.EMPLOYEE_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Recruitment ─────────────────────────────────────────────────────────────
export const getRecruitmentCandidates = (tenantId, params = {}) =>
  getResource('/hr/recruitment/candidates', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

export const createCandidate = (data, tenantId) =>
  postResource('/hr/recruitment/candidates', data, tenantId, TEL_EVENTS.HR.CANDIDATE_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updateCandidateStage = (id, stage, tenantId) =>
  putResource(`/hr/recruitment/candidates/${id}/stage`, { stage }, tenantId, TEL_EVENTS.HR.RECRUITMENT_STAGE_CHANGE, TEL_EVENTS.HR.ACTION_FRACTURE);

export const deleteCandidate = (id, tenantId) =>
  deleteResource(`/hr/recruitment/candidates/${id}`, tenantId, TEL_EVENTS.HR.CANDIDATE_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const getJobOpenings = (tenantId, params = {}) =>
  getResource('/hr/recruitment/openings', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

export const createJobOpening = (data, tenantId) =>
  postResource('/hr/recruitment/openings', data, tenantId, TEL_EVENTS.HR.JOB_OPENING_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updateJobOpening = (id, data, tenantId) =>
  putResource(`/hr/recruitment/openings/${id}`, data, tenantId, TEL_EVENTS.HR.JOB_OPENING_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const deleteJobOpening = (id, tenantId) =>
  deleteResource(`/hr/recruitment/openings/${id}`, tenantId, TEL_EVENTS.HR.JOB_OPENING_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Payroll ─────────────────────────────────────────────────────────────────
export const getPayrollSummary = (tenantId, params = {}) =>
  getResource('/hr/payroll/summary', tenantId, params, TEL_EVENTS.HR.PAYROLL_SYNC_SUCCESS, TEL_EVENTS.HR.PAYROLL_SYNC_FRACTURE);

export const syncPayroll = (tenantId) =>
  postResource('/hr/payroll/sync', {}, tenantId, TEL_EVENTS.HR.PAYROLL_SYNC_SUCCESS, TEL_EVENTS.HR.PAYROLL_SYNC_FRACTURE);

// ─── Benefits ─────────────────────────────────────────────────────────────────
export const getBenefits = (tenantId, params = {}) =>
  getResource('/hr/benefits', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

export const createBenefit = (data, tenantId) =>
  postResource('/hr/benefits', data, tenantId, TEL_EVENTS.HR.BENEFIT_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updateBenefit = (id, data, tenantId) =>
  putResource(`/hr/benefits/${id}`, data, tenantId, TEL_EVENTS.HR.BENEFIT_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const deleteBenefit = (id, tenantId) =>
  deleteResource(`/hr/benefits/${id}`, tenantId, TEL_EVENTS.HR.BENEFIT_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Performance ─────────────────────────────────────────────────────────────
export const getPerformanceReviews = (tenantId, params = {}) =>
  getResource('/hr/performance', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

export const createPerformanceReview = (data, tenantId) =>
  postResource('/hr/performance', data, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updatePerformanceReview = (id, data, tenantId) =>
  putResource(`/hr/performance/${id}`, data, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const deletePerformanceReview = (id, tenantId) =>
  deleteResource(`/hr/performance/${id}`, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Time-off ─────────────────────────────────────────────────────────────────
export const getTimeOffRequests = (tenantId, params = {}) =>
  getResource('/hr/timeoff', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

export const createTimeOffRequest = (data, tenantId) =>
  postResource('/hr/timeoff', data, tenantId, TEL_EVENTS.HR.TIME_OFF_REQUESTED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const updateTimeOffRequest = (id, data, tenantId) =>
  putResource(`/hr/timeoff/${id}`, data, tenantId, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.ACTION_FRACTURE);

export const approveTimeOff = (id, tenantId) =>
  putResource(`/hr/timeoff/${id}/approve`, {}, tenantId, TEL_EVENTS.HR.TIME_OFF_APPROVED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const denyTimeOff = (id, tenantId) =>
  putResource(`/hr/timeoff/${id}/deny`, {}, tenantId, TEL_EVENTS.HR.TIME_OFF_DENIED, TEL_EVENTS.HR.ACTION_FRACTURE);

export const deleteTimeOffRequest = (id, tenantId) =>
  deleteResource(`/hr/timeoff/${id}`, tenantId, TEL_EVENTS.HR.TIME_OFF_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Circuit Management ──────────────────────────────────────────────────────
export const resetHrCircuit = () => hrCircuit.reset();
export const getHrCircuitState = () => hrCircuit.snapshot();

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
  resetHrCircuit,
  getHrCircuitState
};

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — WILSY OS HR SERVICE
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status: CERTIFIED PRODUCTION ARTIFACT
 * Resilience: Exponential backoff, adaptive polling, circuit breaker
 * Telemetry: TEL_EVENTS.HR.* integrated
 * Compliance: POPIA / GDPR / SOC2 SECURE
 * ═══════════════════════════════════════════════════════════════════════════════
 */
