/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN PRODUCT SERVICE [V1.1.0-HARDENED]                                                                                 ║
 * ║ [ROADMAPS | RELEASES | USER RESEARCH | REQUIREMENTS | PROTOTYPES | METRICS | PAGINATION | TELEMETRY]                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited product API with full lifecycle management.                             ║
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
  logger.error(`[productService] ${context} failed: ${message}`, { tenantId, ...extra });
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
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE);
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
// ROADMAPS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getRoadmaps = (tenantId, params = {}) => getResource('/product/roadmaps', tenantId, params, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE);
export const getRoadmapsArray = (tenantId, params = {}) => getResourceArray('/product/roadmaps', tenantId, params);
/** @returns {Promise<Object>} */
export const createRoadmap = (data, tenantId) => postResource('/product/roadmaps', data, tenantId, TEL_EVENTS.PRODUCT.ROADMAP_CREATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateRoadmap = (id, data, tenantId) => putResource(`/product/roadmaps/${id}`, data, tenantId, TEL_EVENTS.PRODUCT.ROADMAP_UPDATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteRoadmap = (id, tenantId) => deleteResource(`/product/roadmaps/${id}`, tenantId, TEL_EVENTS.PRODUCT.ROADMAP_DELETED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);

// ============================================================================
// RELEASES
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getReleases = (tenantId, params = {}) => getResource('/product/releases', tenantId, params, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE);
export const getReleasesArray = (tenantId, params = {}) => getResourceArray('/product/releases', tenantId, params);
/** @returns {Promise<Object>} */
export const createRelease = (data, tenantId) => postResource('/product/releases', data, tenantId, TEL_EVENTS.PRODUCT.RELEASE_CREATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateRelease = (id, data, tenantId) => putResource(`/product/releases/${id}`, data, tenantId, TEL_EVENTS.PRODUCT.RELEASE_UPDATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteRelease = (id, tenantId) => deleteResource(`/product/releases/${id}`, tenantId, TEL_EVENTS.PRODUCT.RELEASE_DELETED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);

// ============================================================================
// USER RESEARCH
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getUserResearch = (tenantId, params = {}) => getResource('/product/research', tenantId, params, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE);
export const getUserResearchArray = (tenantId, params = {}) => getResourceArray('/product/research', tenantId, params);
/** @returns {Promise<Object>} */
export const createUserResearch = (data, tenantId) => postResource('/product/research', data, tenantId, TEL_EVENTS.PRODUCT.RESEARCH_CREATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateUserResearch = (id, data, tenantId) => putResource(`/product/research/${id}`, data, tenantId, TEL_EVENTS.PRODUCT.RESEARCH_UPDATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteUserResearch = (id, tenantId) => deleteResource(`/product/research/${id}`, tenantId, TEL_EVENTS.PRODUCT.RESEARCH_DELETED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);

// ============================================================================
// REQUIREMENTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getRequirements = (tenantId, params = {}) => getResource('/product/requirements', tenantId, params, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE);
export const getRequirementsArray = (tenantId, params = {}) => getResourceArray('/product/requirements', tenantId, params);
/** @returns {Promise<Object>} */
export const createRequirement = (data, tenantId) => postResource('/product/requirements', data, tenantId, TEL_EVENTS.PRODUCT.REQUIREMENT_CREATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateRequirement = (id, data, tenantId) => putResource(`/product/requirements/${id}`, data, tenantId, TEL_EVENTS.PRODUCT.REQUIREMENT_UPDATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteRequirement = (id, tenantId) => deleteResource(`/product/requirements/${id}`, tenantId, TEL_EVENTS.PRODUCT.REQUIREMENT_DELETED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);

// ============================================================================
// PROTOTYPES
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getPrototypes = (tenantId, params = {}) => getResource('/product/prototypes', tenantId, params, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE);
export const getPrototypesArray = (tenantId, params = {}) => getResourceArray('/product/prototypes', tenantId, params);
/** @returns {Promise<Object>} */
export const createPrototype = (data, tenantId) => postResource('/product/prototypes', data, tenantId, TEL_EVENTS.PRODUCT.PROTOTYPE_CREATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updatePrototype = (id, data, tenantId) => putResource(`/product/prototypes/${id}`, data, tenantId, TEL_EVENTS.PRODUCT.PROTOTYPE_UPDATED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deletePrototype = (id, tenantId) => deleteResource(`/product/prototypes/${id}`, tenantId, TEL_EVENTS.PRODUCT.PROTOTYPE_DELETED, TEL_EVENTS.PRODUCT.ACTION_FRACTURE);

// ============================================================================
// PRODUCT METRICS
// ============================================================================

/**
 * Retrieves product metrics (e.g., feature adoption, velocity).
 * @param {string} tenantId - Tenant ID.
 * @param {Object} [params] - Period filters.
 * @returns {Promise<Object>} Metrics object.
 */
export const getProductMetrics = async (tenantId, params = {}) => {
  try {
    const response = await api.get('/product/metrics', {
      params: { tenantId, ...params },
      headers: { 'X-Tenant-ID': tenantId }
    });
    await broadcastTelemetry(tenantId, TEL_EVENTS.PRODUCT.HYDRATION_SUCCESS, 'SUCCESS', 'getProductMetrics', {});
    return response.data || {};
  } catch (error) {
    await handleApiError(error, 'getProductMetrics', tenantId, TEL_EVENTS.PRODUCT.HYDRATION_FRACTURE, { params });
    return {};
  }
};

export default {
  getRoadmaps, getRoadmapsArray, createRoadmap, updateRoadmap, deleteRoadmap,
  getReleases, getReleasesArray, createRelease, updateRelease, deleteRelease,
  getUserResearch, getUserResearchArray, createUserResearch, updateUserResearch, deleteUserResearch,
  getRequirements, getRequirementsArray, createRequirement, updateRequirement, deleteRequirement,
  getPrototypes, getPrototypesArray, createPrototype, updatePrototype, deletePrototype,
  getProductMetrics
};
