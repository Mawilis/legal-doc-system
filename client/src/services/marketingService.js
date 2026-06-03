/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN MARKETING SERVICE [V1.1.0-HARDENED]                                                                               ║
 * ║ [CAMPAIGNS | LEAD SCORES | CONTENT | SOCIAL | SEO | ANALYTICS | BRAND | EVENTS | PR | PAGINATION | TELEMETRY]                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated centralised, audited marketing API with full campaign lifecycle.                             ║
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
  logger.error(`[marketingService] ${context} failed: ${message}`, { tenantId, ...extra });
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
  const { items } = await getResource(endpoint, tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
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
// CAMPAIGNS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getCampaigns = (tenantId, params = {}) => getResource('/marketing/campaigns', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getCampaignsArray = (tenantId, params = {}) => getResourceArray('/marketing/campaigns', tenantId, params);
/** @returns {Promise<Object>} */
export const createCampaign = (data, tenantId) => postResource('/marketing/campaigns', data, tenantId, TEL_EVENTS.MARKETING.CAMPAIGN_LAUNCHED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateCampaign = (id, data, tenantId) => putResource(`/marketing/campaigns/${id}`, data, tenantId, TEL_EVENTS.MARKETING.CAMPAIGN_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteCampaign = (id, tenantId) => deleteResource(`/marketing/campaigns/${id}`, tenantId, TEL_EVENTS.MARKETING.CAMPAIGN_DELETED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// LEAD SCORES
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getLeadScores = (tenantId, params = {}) => getResource('/marketing/lead-scores', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getLeadScoresArray = (tenantId, params = {}) => getResourceArray('/marketing/lead-scores', tenantId, params);
/** @returns {Promise<Object>} */
export const updateLeadScore = (id, data, tenantId) => putResource(`/marketing/lead-scores/${id}`, data, tenantId, TEL_EVENTS.MARKETING.LEAD_SCORE_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// CONTENT
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getContent = (tenantId, params = {}) => getResource('/marketing/content', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getContentArray = (tenantId, params = {}) => getResourceArray('/marketing/content', tenantId, params);
/** @returns {Promise<Object>} */
export const createContent = (data, tenantId) => postResource('/marketing/content', data, tenantId, TEL_EVENTS.MARKETING.CONTENT_CREATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateContent = (id, data, tenantId) => putResource(`/marketing/content/${id}`, data, tenantId, TEL_EVENTS.MARKETING.CONTENT_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteContent = (id, tenantId) => deleteResource(`/marketing/content/${id}`, tenantId, TEL_EVENTS.MARKETING.CONTENT_DELETED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// SOCIAL MEDIA POSTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getSocialPosts = (tenantId, params = {}) => getResource('/marketing/social', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getSocialPostsArray = (tenantId, params = {}) => getResourceArray('/marketing/social', tenantId, params);
/** @returns {Promise<Object>} */
export const createSocialPost = (data, tenantId) => postResource('/marketing/social', data, tenantId, TEL_EVENTS.MARKETING.SOCIAL_POST_CREATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateSocialPost = (id, data, tenantId) => putResource(`/marketing/social/${id}`, data, tenantId, TEL_EVENTS.MARKETING.SOCIAL_POST_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteSocialPost = (id, tenantId) => deleteResource(`/marketing/social/${id}`, tenantId, TEL_EVENTS.MARKETING.SOCIAL_POST_DELETED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// SEO METRICS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getSEOMetrics = (tenantId, params = {}) => getResource('/marketing/seo', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getSEOMetricsArray = (tenantId, params = {}) => getResourceArray('/marketing/seo', tenantId, params);
/** @returns {Promise<Object>} */
export const updateSEOMetric = (id, data, tenantId) => putResource(`/marketing/seo/${id}`, data, tenantId, TEL_EVENTS.MARKETING.SEO_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// ANALYTICS (Performance Metrics)
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getAnalytics = (tenantId, params = {}) => getResource('/marketing/analytics', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getAnalyticsArray = (tenantId, params = {}) => getResourceArray('/marketing/analytics', tenantId, params);
/** @returns {Promise<Object>} */
export const updateAnalytic = (id, data, tenantId) => putResource(`/marketing/analytics/${id}`, data, tenantId, TEL_EVENTS.MARKETING.ANALYTICS_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// BRAND ASSETS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getBrandAssets = (tenantId, params = {}) => getResource('/marketing/brand', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getBrandAssetsArray = (tenantId, params = {}) => getResourceArray('/marketing/brand', tenantId, params);
/** @returns {Promise<Object>} */
export const createBrandAsset = (data, tenantId) => postResource('/marketing/brand', data, tenantId, TEL_EVENTS.MARKETING.BRAND_ASSET_CREATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteBrandAsset = (id, tenantId) => deleteResource(`/marketing/brand/${id}`, tenantId, TEL_EVENTS.MARKETING.BRAND_ASSET_DELETED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// EVENTS
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getEvents = (tenantId, params = {}) => getResource('/marketing/events', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getEventsArray = (tenantId, params = {}) => getResourceArray('/marketing/events', tenantId, params);
/** @returns {Promise<Object>} */
export const createEvent = (data, tenantId) => postResource('/marketing/events', data, tenantId, TEL_EVENTS.MARKETING.EVENT_CREATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updateEvent = (id, data, tenantId) => putResource(`/marketing/events/${id}`, data, tenantId, TEL_EVENTS.MARKETING.EVENT_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deleteEvent = (id, tenantId) => deleteResource(`/marketing/events/${id}`, tenantId, TEL_EVENTS.MARKETING.EVENT_DELETED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

// ============================================================================
// PR / PRESS RELEASES
// ============================================================================

/** @returns {Promise<{items: Array, total: number, limit: number, offset: number, hasMore: boolean}>} */
export const getPressReleases = (tenantId, params = {}) => getResource('/marketing/pr', tenantId, params, TEL_EVENTS.MARKETING.HYDRATION_SUCCESS, TEL_EVENTS.MARKETING.HYDRATION_FRACTURE);
export const getPressReleasesArray = (tenantId, params = {}) => getResourceArray('/marketing/pr', tenantId, params);
/** @returns {Promise<Object>} */
export const createPressRelease = (data, tenantId) => postResource('/marketing/pr', data, tenantId, TEL_EVENTS.MARKETING.PR_CREATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<Object>} */
export const updatePressRelease = (id, data, tenantId) => putResource(`/marketing/pr/${id}`, data, tenantId, TEL_EVENTS.MARKETING.PR_UPDATED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);
/** @returns {Promise<void>} */
export const deletePressRelease = (id, tenantId) => deleteResource(`/marketing/pr/${id}`, tenantId, TEL_EVENTS.MARKETING.PR_DELETED, TEL_EVENTS.MARKETING.ACTION_FRACTURE);

export default {
  getCampaigns, getCampaignsArray, createCampaign, updateCampaign, deleteCampaign,
  getLeadScores, getLeadScoresArray, updateLeadScore,
  getContent, getContentArray, createContent, updateContent, deleteContent,
  getSocialPosts, getSocialPostsArray, createSocialPost, updateSocialPost, deleteSocialPost,
  getSEOMetrics, getSEOMetricsArray, updateSEOMetric,
  getAnalytics, getAnalyticsArray, updateAnalytic,
  getBrandAssets, getBrandAssetsArray, createBrandAsset, deleteBrandAsset,
  getEvents, getEventsArray, createEvent, updateEvent, deleteEvent,
  getPressReleases, getPressReleasesArray, createPressRelease, updatePressRelease, deletePressRelease
};
