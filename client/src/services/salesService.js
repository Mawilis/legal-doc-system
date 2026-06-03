/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SALES SERVICE [V1.1.0-HARDENED]                                                                                   ║
 * ║ [PIPELINE | QUOTES | ORDERS | COMMISSIONS | FORECASTS | PAGINATION | TELEMETRY]                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited sales API layer with full pipeline lifecycle.                        ║
 * ║ • AI Engineering (Gemini) – RECTIFIED: Hardened sanitizePayload against prototype pollution, corrected telemetry mappings,             ║
 * ║   enforced explicit JSDoc pagination types, and implemented dynamic generateForecast endpoints. [2026-05-19]                           ║
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
  logger.error(`[salesService] ${context} failed: ${message}`, { tenantId, ...extra });
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
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.SALES.HYDRATION_SUCCESS, TEL_EVENTS.SALES.HYDRATION_FRACTURE);
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
// PIPELINE
// ============================================================================
/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getPipeline = (tenantId, params = {}) => getResource('/sales/pipeline', tenantId, params, TEL_EVENTS.SALES.HYDRATION_SUCCESS, TEL_EVENTS.SALES.HYDRATION_FRACTURE);
export const getPipelineArray = (tenantId, params = {}) => getResourceArray('/sales/pipeline', tenantId, params);
export const createPipelineDeal = (data, tenantId) => postResource('/sales/pipeline', data, tenantId, TEL_EVENTS.SALES.DEAL_CREATED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const updatePipelineDeal = (id, data, tenantId) => putResource(`/sales/pipeline/${id}`, data, tenantId, TEL_EVENTS.SALES.DEAL_UPDATED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const deletePipelineDeal = (id, tenantId) => deleteResource(`/sales/pipeline/${id}`, tenantId, TEL_EVENTS.SALES.DEAL_DELETED, TEL_EVENTS.SALES.ACTION_FRACTURE);

// ============================================================================
// QUOTES
// ============================================================================
/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getQuotes = (tenantId, params = {}) => getResource('/sales/quotes', tenantId, params, TEL_EVENTS.SALES.HYDRATION_SUCCESS, TEL_EVENTS.SALES.HYDRATION_FRACTURE);
export const getQuotesArray = (tenantId, params = {}) => getResourceArray('/sales/quotes', tenantId, params);
export const createQuote = (data, tenantId) => postResource('/sales/quotes', data, tenantId, TEL_EVENTS.SALES.QUOTE_GENERATED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const updateQuote = (id, data, tenantId) => putResource(`/sales/quotes/${id}`, data, tenantId, TEL_EVENTS.SALES.QUOTE_UPDATED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const deleteQuote = (id, tenantId) => deleteResource(`/sales/quotes/${id}`, tenantId, TEL_EVENTS.SALES.QUOTE_DELETED, TEL_EVENTS.SALES.ACTION_FRACTURE);

// ============================================================================
// ORDERS
// ============================================================================
/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getOrders = (tenantId, params = {}) => getResource('/sales/orders', tenantId, params, TEL_EVENTS.SALES.HYDRATION_SUCCESS, TEL_EVENTS.SALES.HYDRATION_FRACTURE);
export const getOrdersArray = (tenantId, params = {}) => getResourceArray('/sales/orders', tenantId, params);
export const createOrder = (data, tenantId) => postResource('/sales/orders', data, tenantId, TEL_EVENTS.SALES.ORDER_PROCESSED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const updateOrder = (id, data, tenantId) => putResource(`/sales/orders/${id}`, data, tenantId, TEL_EVENTS.SALES.ORDER_UPDATED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const deleteOrder = (id, tenantId) => deleteResource(`/sales/orders/${id}`, tenantId, TEL_EVENTS.SALES.ORDER_DELETED, TEL_EVENTS.SALES.ACTION_FRACTURE);

// ============================================================================
// COMMISSIONS
// ============================================================================
/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getCommissions = (tenantId, params = {}) => getResource('/sales/commissions', tenantId, params, TEL_EVENTS.SALES.HYDRATION_SUCCESS, TEL_EVENTS.SALES.HYDRATION_FRACTURE);
export const getCommissionsArray = (tenantId, params = {}) => getResourceArray('/sales/commissions', tenantId, params);
export const calculateCommissions = (tenantId, params = {}) => postResource('/sales/commissions/calculate', params, tenantId, TEL_EVENTS.SALES.COMMISSION_CALCULATED, TEL_EVENTS.SALES.ACTION_FRACTURE);

// ============================================================================
// FORECASTS
// ============================================================================
/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getForecasts = (tenantId, params = {}) => getResource('/sales/forecasts', tenantId, params, TEL_EVENTS.SALES.HYDRATION_SUCCESS, TEL_EVENTS.SALES.HYDRATION_FRACTURE);
export const getForecastsArray = (tenantId, params = {}) => getResourceArray('/sales/forecasts', tenantId, params);
export const updateForecast = (id, data, tenantId) => putResource(`/sales/forecasts/${id}`, data, tenantId, TEL_EVENTS.SALES.FORECAST_UPDATED, TEL_EVENTS.SALES.ACTION_FRACTURE);
export const generateForecast = (tenantId, params = {}) => postResource('/sales/forecasts/generate', params, tenantId, TEL_EVENTS.SALES.FORECAST_GENERATED, TEL_EVENTS.SALES.ACTION_FRACTURE);

export default {
  getPipeline, getPipelineArray, createPipelineDeal, updatePipelineDeal, deletePipelineDeal,
  getQuotes, getQuotesArray, createQuote, updateQuote, deleteQuote,
  getOrders, getOrdersArray, createOrder, updateOrder, deleteOrder,
  getCommissions, getCommissionsArray, calculateCommissions,
  getForecasts, getForecastsArray, updateForecast, generateForecast
};
