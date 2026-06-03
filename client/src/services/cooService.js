/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN COO OPERATIONS SERVICE [V1.1.0-HARDENED]                                                                          ║
 * ║ [KPI SCORECARD | APPROVAL WORKFLOWS | OPERATIONAL ALERTS | PAGINATION | TELEMETRY]                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited COO operations API with real‑time KPI tracking.                        ║
 * ║ • AI Engineering (Gemini) – RECTIFIED: Hardened sanitizePayload, corrected telemetry mapping for approvals, and enforced pagination.   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';
import logger from '../utils/logger';
import { TEL_EVENTS } from '../constants/telemetryConstants';

const sanitizePayload = (obj) => {
  if (!obj || typeof obj !== 'object') return obj;
  return Object.keys(obj).reduce((acc, key) => {
    if (key === '__proto__' || key === 'constructor') return acc;
    if (obj[key] !== undefined) acc[key] = obj[key];
    return acc;
  }, {});
};

const handleApiError = async (error, context, tenantId, failureEvent, extra = {}) => {
  const message = error.response?.data?.message || error.message;
  logger.error(`[cooService] ${context} failed: ${message}`, { tenantId, ...extra });
  await broadcastTelemetry(tenantId, failureEvent, 'FRACTURE', context, { error: message, ...extra });
  throw error;
};

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
// KPI SCORECARD
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getKPIScorecard = (tenantId, params = {}) => getResource('/coo/kpi-scorecard', tenantId, params, TEL_EVENTS.COO.KPI_SCORECARD_UPDATED, TEL_EVENTS.COO.HYDRATION_FRACTURE);
export const updateKPI = (id, data, tenantId) => putResource(`/coo/kpi-scorecard/${id}`, data, tenantId, TEL_EVENTS.COO.KPI_SCORECARD_UPDATED, TEL_EVENTS.COO.ACTION_FRACTURE);

// ============================================================================
// APPROVAL WORKFLOWS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getApprovals = (tenantId, params = {}) => getResource('/coo/approvals', tenantId, params, TEL_EVENTS.COO.HYDRATION_SUCCESS, TEL_EVENTS.COO.HYDRATION_FRACTURE);
export const createApproval = (data, tenantId) => postResource('/coo/approvals', data, tenantId, TEL_EVENTS.COO.APPROVAL_WORKFLOW_TRIGGERED, TEL_EVENTS.COO.ACTION_FRACTURE);
export const updateApproval = (id, data, tenantId) => putResource(`/coo/approvals/${id}`, data, tenantId, TEL_EVENTS.COO.APPROVAL_WORKFLOW_TRIGGERED, TEL_EVENTS.COO.ACTION_FRACTURE);
export const deleteApproval = (id, tenantId) => deleteResource(`/coo/approvals/${id}`, tenantId, TEL_EVENTS.COO.HYDRATION_SUCCESS, TEL_EVENTS.COO.ACTION_FRACTURE);
export const approveRequest = (id, tenantId) => putResource(`/coo/approvals/${id}/approve`, {}, tenantId, TEL_EVENTS.COO.APPROVAL_GRANTED, TEL_EVENTS.COO.ACTION_FRACTURE);
export const rejectRequest = (id, tenantId) => putResource(`/coo/approvals/${id}/reject`, {}, tenantId, TEL_EVENTS.COO.APPROVAL_REJECTED, TEL_EVENTS.COO.ACTION_FRACTURE);

// ============================================================================
// OPERATIONAL ALERTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getOperationalAlerts = (tenantId, params = {}) => getResource('/coo/alerts', tenantId, params, TEL_EVENTS.COO.HYDRATION_SUCCESS, TEL_EVENTS.COO.HYDRATION_FRACTURE);
export const acknowledgeAlert = (id, tenantId) => putResource(`/coo/alerts/${id}/acknowledge`, {}, tenantId, TEL_EVENTS.COO.OPERATIONAL_ALERT, TEL_EVENTS.COO.ACTION_FRACTURE);
export const resolveAlert = (id, tenantId) => putResource(`/coo/alerts/${id}/resolve`, {}, tenantId, TEL_EVENTS.COO.OPERATIONAL_ALERT, TEL_EVENTS.COO.ACTION_FRACTURE);

export default {
  getKPIScorecard, updateKPI,
  getApprovals, createApproval, updateApproval, deleteApproval, approveRequest, rejectRequest,
  getOperationalAlerts, acknowledgeAlert, resolveAlert
};
