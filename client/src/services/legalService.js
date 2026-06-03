/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN LEGAL SERVICE [V1.1.0-HARDENED]                                                                                   ║
 * ║ [CONTRACTS | COMPLIANCE | RISK | INTELLECTUAL PROPERTY | POLICIES | PAGINATION | TELEMETRY]                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited legal API with full contract lifecycle.                                ║
 * ║ • AI Engineering (Gemini) – RECTIFIED: Aligned keys to frozen outcomes, added complete JSDoc layers, and resolved mapping leakages.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';
import logger from '../utils/logger';
import { TEL_EVENTS } from '../constants/telemetryConstants';

// ============================================================================
// UTILITIES
// ============================================================================

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
  logger.error(`[legalService] ${context} failed: ${message}`, { tenantId, ...extra });
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

const getResourceArray = async (endpoint, tenantId, params = {}) => {
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.LEGAL.HYDRATION_SUCCESS, TEL_EVENTS.LEGAL.HYDRATION_FRACTURE);
  return items;
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
// CONTRACTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getContracts = (tenantId, params = {}) => getResource('/legal/contracts', tenantId, params, TEL_EVENTS.LEGAL.HYDRATION_SUCCESS, TEL_EVENTS.LEGAL.HYDRATION_FRACTURE);
export const getContractsArray = (tenantId, params = {}) => getResourceArray('/legal/contracts', tenantId, params);
/** @returns {Promise<Object>} */
export const createContract = (data, tenantId) => postResource('/legal/contracts', data, tenantId, TEL_EVENTS.LEGAL.CONTRACT_SIGNED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateContract = (id, data, tenantId) => putResource(`/legal/contracts/${id}`, data, tenantId, TEL_EVENTS.LEGAL.CONTRACT_UPDATED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteContract = (id, tenantId) => deleteResource(`/legal/contracts/${id}`, tenantId, TEL_EVENTS.LEGAL.CONTRACT_DELETED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);

// ============================================================================
// COMPLIANCE RECORDS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getComplianceRecords = (tenantId, params = {}) => getResource('/legal/compliance', tenantId, params, TEL_EVENTS.LEGAL.HYDRATION_SUCCESS, TEL_EVENTS.LEGAL.HYDRATION_FRACTURE);
export const getComplianceRecordsArray = (tenantId, params = {}) => getResourceArray('/legal/compliance', tenantId, params);
/** @returns {Promise<Object>} */
export const updateComplianceRecord = (id, data, tenantId) => putResource(`/legal/compliance/${id}`, data, tenantId, TEL_EVENTS.LEGAL.COMPLIANCE_UPDATED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteComplianceRecord = (id, tenantId) => deleteResource(`/legal/compliance/${id}`, tenantId, TEL_EVENTS.LEGAL.COMPLIANCE_DELETED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);

// ============================================================================
// RISK REGISTER
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getRisks = (tenantId, params = {}) => getResource('/legal/risks', tenantId, params, TEL_EVENTS.LEGAL.HYDRATION_SUCCESS, TEL_EVENTS.LEGAL.HYDRATION_FRACTURE);
export const getRisksArray = (tenantId, params = {}) => getResourceArray('/legal/risks', tenantId, params);
/** @returns {Promise<Object>} */
export const createRisk = (data, tenantId) => postResource('/legal/risks', data, tenantId, TEL_EVENTS.LEGAL.RISK_DETECTED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateRisk = (id, data, tenantId) => putResource(`/legal/risks/${id}`, data, tenantId, TEL_EVENTS.LEGAL.RISK_UPDATED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteRisk = (id, tenantId) => deleteResource(`/legal/risks/${id}`, tenantId, TEL_EVENTS.LEGAL.RISK_DELETED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);

// ============================================================================
// INTELLECTUAL PROPERTY (Patents, Trademarks, Copyrights)
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getIP = (tenantId, params = {}) => getResource('/legal/ip', tenantId, params, TEL_EVENTS.LEGAL.HYDRATION_SUCCESS, TEL_EVENTS.LEGAL.HYDRATION_FRACTURE);
export const getIPArray = (tenantId, params = {}) => getResourceArray('/legal/ip', tenantId, params);
/** @returns {Promise<Object>} */
export const createIP = (data, tenantId) => postResource('/legal/ip', data, tenantId, TEL_EVENTS.LEGAL.IP_CREATED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateIP = (id, data, tenantId) => putResource(`/legal/ip/${id}`, data, tenantId, TEL_EVENTS.LEGAL.IP_UPDATED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteIP = (id, tenantId) => deleteResource(`/legal/ip/${id}`, tenantId, TEL_EVENTS.LEGAL.IP_DELETED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);

// ============================================================================
// LEGAL POLICIES
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getPolicies = (tenantId, params = {}) => getResource('/legal/policies', tenantId, params, TEL_EVENTS.LEGAL.HYDRATION_SUCCESS, TEL_EVENTS.LEGAL.HYDRATION_FRACTURE);
export const getPoliciesArray = (tenantId, params = {}) => getResourceArray('/legal/policies', tenantId, params);
/** @returns {Promise<Object>} */
export const updatePolicy = (id, data, tenantId) => putResource(`/legal/policies/${id}`, data, tenantId, TEL_EVENTS.LEGAL.POLICY_UPDATED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deletePolicy = (id, tenantId) => deleteResource(`/legal/policies/${id}`, tenantId, TEL_EVENTS.LEGAL.POLICY_DELETED, TEL_EVENTS.LEGAL.ACTION_FRACTURE);

export default {
  getContracts, getContractsArray, createContract, updateContract, deleteContract,
  getComplianceRecords, getComplianceRecordsArray, updateComplianceRecord, deleteComplianceRecord,
  getRisks, getRisksArray, createRisk, updateRisk, deleteRisk,
  getIP, getIPArray, createIP, updateIP, deleteIP,
  getPolicies, getPoliciesArray, updatePolicy, deletePolicy
};
