/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN FINANCE SERVICE [V1.1.0-HARDENED]                                                                                 ║
 * ║ [INVOICES | PAYMENTS | BUDGETS | TAX REPORTS | KPI | PAGINATION | TELEMETRY]                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited finance API with full ledger lifecycle.                                ║
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
  logger.error(`[financeService] ${context} failed: ${message}`, { tenantId, ...extra });
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
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.FINANCE.HYDRATION_SUCCESS, TEL_EVENTS.FINANCE.HYDRATION_FRACTURE);
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
// INVOICES
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getInvoices = (tenantId, params = {}) => getResource('/finance/invoices', tenantId, params, TEL_EVENTS.FINANCE.HYDRATION_SUCCESS, TEL_EVENTS.FINANCE.HYDRATION_FRACTURE);
export const getInvoicesArray = (tenantId, params = {}) => getResourceArray('/finance/invoices', tenantId, params);
/** @returns {Promise<Object>} */
export const createInvoice = (data, tenantId) => postResource('/finance/invoices', data, tenantId, TEL_EVENTS.FINANCE.INVOICE_GENERATED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateInvoice = (id, data, tenantId) => putResource(`/finance/invoices/${id}`, data, tenantId, TEL_EVENTS.FINANCE.INVOICE_UPDATED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteInvoice = (id, tenantId) => deleteResource(`/finance/invoices/${id}`, tenantId, TEL_EVENTS.FINANCE.INVOICE_DELETED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);

// ============================================================================
// PAYMENTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getPayments = (tenantId, params = {}) => getResource('/finance/payments', tenantId, params, TEL_EVENTS.FINANCE.HYDRATION_SUCCESS, TEL_EVENTS.FINANCE.HYDRATION_FRACTURE);
export const getPaymentsArray = (tenantId, params = {}) => getResourceArray('/finance/payments', tenantId, params);
/** @returns {Promise<Object>} */
export const createPayment = (data, tenantId) => postResource('/finance/payments', data, tenantId, TEL_EVENTS.FINANCE.PAYMENT_RECEIVED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deletePayment = (id, tenantId) => deleteResource(`/finance/payments/${id}`, tenantId, TEL_EVENTS.FINANCE.PAYMENT_DELETED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);

// ============================================================================
// BUDGETS (Budget vs Actual)
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getBudgets = (tenantId, params = {}) => getResource('/finance/budgets', tenantId, params, TEL_EVENTS.FINANCE.HYDRATION_SUCCESS, TEL_EVENTS.FINANCE.HYDRATION_FRACTURE);
export const getBudgetsArray = (tenantId, params = {}) => getResourceArray('/finance/budgets', tenantId, params);
/** @returns {Promise<Object>} */
export const updateBudget = (id, data, tenantId) => putResource(`/finance/budgets/${id}`, data, tenantId, TEL_EVENTS.FINANCE.BUDGET_UPDATED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);

// ============================================================================
// TAX REPORTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getTaxReports = (tenantId, params = {}) => getResource('/finance/tax-reports', tenantId, params, TEL_EVENTS.FINANCE.HYDRATION_SUCCESS, TEL_EVENTS.FINANCE.HYDRATION_FRACTURE);
export const getTaxReportsArray = (tenantId, params = {}) => getResourceArray('/finance/tax-reports', tenantId, params);
/** @returns {Promise<Object>} */
export const generateTaxReport = (data, tenantId) => postResource('/finance/tax-reports/generate', data, tenantId, TEL_EVENTS.FINANCE.TAX_REPORT_EXPORTED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteTaxReport = (id, tenantId) => deleteResource(`/finance/tax-reports/${id}`, tenantId, TEL_EVENTS.FINANCE.TAX_REPORT_DELETED, TEL_EVENTS.FINANCE.ACTION_FRACTURE);

// ============================================================================
// FINANCIAL KPIS
// ============================================================================

/**
 * Retrieves financial KPIs (revenue, expenses, profit, etc.).
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Period filters.
 * @returns {Promise<Object>} KPI object.
 */
export const getFinancialKPIs = async (tenantId, params = {}) => {
  try {
    const response = await api.get('/finance/kpis', {
      params: { tenantId, ...params },
      headers: { 'X-Tenant-ID': tenantId }
    });
    await broadcastTelemetry(tenantId, TEL_EVENTS.FINANCE.HYDRATION_SUCCESS, 'SUCCESS', 'getFinancialKPIs', {});
    return response.data || {};
  } catch (error) {
    await handleApiError(error, 'getFinancialKPIs', tenantId, TEL_EVENTS.FINANCE.HYDRATION_FRACTURE, { params });
    return {};
  }
};

export default {
  getInvoices, getInvoicesArray, createInvoice, updateInvoice, deleteInvoice,
  getPayments, getPaymentsArray, createPayment, deletePayment,
  getBudgets, getBudgetsArray, updateBudget,
  getTaxReports, getTaxReportsArray, generateTaxReport, deleteTaxReport,
  getFinancialKPIs
};
