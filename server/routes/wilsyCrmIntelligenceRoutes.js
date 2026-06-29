/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM INTELLIGENCE ROUTES                                                                                     ║
 * ║ /api/crm/intelligence/*                                                                                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Sovereign CRM intelligence routes.
 */

import express from 'express';
import {
  buildBoardroomIntelligence,
  getIntelligenceCollections,
  getTenantId,
  listIntelligenceRecords,
} from '../services/wilsyCrmIntelligenceService.js';

const router = express.Router();

/**
 * @function resolveWilsyR91K115SourceGuideBaseUrl
 * @description Resolves an internal base URL for pulling the live Source Posture Guide into AI command surfaces.
 * @param {Object} req - Express request.
 * @returns {string} Internal API base URL.
 * @collaboration Source Posture Guide, Wilsy AI command constraints, backend route enrichment.
 */
function resolveWilsyR91K115SourceGuideBaseUrl(req = {}) {
  const configuredBase = String(
    process.env.WILSY_INTERNAL_API_BASE_URL || process.env.WILSY_API_INTERNAL_BASE_URL || ''
  ).trim();

  if (configuredBase) {
    return configuredBase.replace(/\/+$/, '');
  }

  const forwardedProto = String(req.headers?.['x-forwarded-proto'] || '')
    .split(',')[0]
    .trim();
  const protocol = forwardedProto || req.protocol || 'http';
  const host = String(
    req.headers?.host || process.env.WILSY_INTERNAL_HOST || `127.0.0.1:${process.env.PORT || 5050}`
  ).trim();

  return `${protocol}://${host}`;
}

/**
 * @function resolveWilsyR91K115BridgeTenantId
 * @description Resolves tenant id for the Source Posture Guide bridge without trusting client-only context.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Tenant-scoped source guide, CRM command fabric, Wilsy AI recommendations.
 */
function resolveWilsyR91K115BridgeTenantId(req = {}) {
  return (
    String(
      req.tenantId ||
        req.headers?.['x-tenant-id'] ||
        req.headers?.['x-wilsy-tenant-id'] ||
        req.query?.tenantId ||
        req.body?.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function shouldWilsyR91K115BridgeSourceGuide
 * @description Determines whether a route response should be constrained by Source Posture Guide truth.
 * @param {Object} req - Express request.
 * @returns {boolean} True when response should be enriched.
 * @collaboration AI-safe recommendations, CRM command search, CRM intelligence outputs.
 */
function shouldWilsyR91K115BridgeSourceGuide(req = {}) {
  const routePath = String(req.path || req.originalUrl || '').toLowerCase();
  const method = String(req.method || 'GET').toUpperCase();

  if (method === 'OPTIONS') {
    return false;
  }

  return (
    ['/search', '/sync', '/status', '/boardroom', '/intelligence', '/catalog'].some((fragment) =>
      routePath.includes(fragment)
    ) || method === 'GET'
  );
}

/**
 * @function fetchWilsyR91K115SourceGuide
 * @description Fetches the live Source Posture Guide so command and intelligence surfaces inherit the same truth layer as CRM telemetry.
 * @param {Object} req - Express request.
 * @returns {Promise<Object|null>} Source guide or null.
 * @collaboration Source Posture Guide, Wilsy AI directives, route-surface constraints.
 */
async function fetchWilsyR91K115SourceGuide(req = {}) {
  if (typeof fetch !== 'function') {
    return null;
  }

  const tenantId = resolveWilsyR91K115BridgeTenantId(req);
  const baseUrl = resolveWilsyR91K115SourceGuideBaseUrl(req);
  const controller = typeof AbortController === 'function' ? new AbortController() : null;
  const timeout = controller ? setTimeout(() => controller.abort(), 2500) : null;

  try {
    const response = await fetch(`${baseUrl}/api/crm/live/source-guide`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'X-Tenant-Id': tenantId,
        'X-Wilsy-Source-Guide-Bridge': 'R91K115B_AI_COMMAND_SOURCE_GUIDE_BRIDGE',
      },
      signal: controller?.signal,
    });

    if (!response.ok) {
      return null;
    }

    const payload = await response.json();
    return payload?.guide || null;
  } catch (error) {
    return null;
  } finally {
    if (timeout) {
      clearTimeout(timeout);
    }
  }
}

/**
 * @function buildWilsyR91K115AiConstraintPacket
 * @description Builds the AI-safe constraint packet carried by command and intelligence responses.
 * @param {Object|null} guide - Source Posture Guide.
 * @param {string} surface - Response surface name.
 * @returns {Object} Constraint packet.
 * @collaboration Wilsy AI recommendation safety, Source Posture Guide, investor-grade evidence posture.
 */
function buildWilsyR91K115AiConstraintPacket(guide = null, surface = 'CRM_AI_SURFACE') {
  if (!guide) {
    return {
      bridgeVersion: 'R91K115B_AI_COMMAND_SOURCE_GUIDE_BRIDGE',
      surface,
      sourceGuideStatus: 'SOURCE_GUIDE_UNAVAILABLE',
      recommendationPolicy: 'DO_NOT_EXPAND_BEYOND_LOCAL_RESPONSE',
      generatedAt: new Date().toISOString(),
    };
  }

  return {
    bridgeVersion: 'R91K115B_AI_COMMAND_SOURCE_GUIDE_BRIDGE',
    surface,
    sourceGuideStatus: 'SOURCE_GUIDE_ATTACHED',
    recommendationPolicy: 'CONSTRAIN_RECOMMENDATIONS_TO_SOURCE_GUIDE',
    readinessScore: guide.readinessScore,
    postureGrade: guide.postureGrade,
    aiOperatingMode: guide.aiOperatingMode,
    routeSurfaceRoutes: guide.routeSurface?.crmRelatedRoutes || 0,
    dataDensityStatus: guide.dataDensityHealth?.status || 'UNKNOWN',
    evidenceStatus: guide.evidenceHealth?.status || 'UNKNOWN',
    connectorStatus: guide.connectorHealth?.status || 'UNKNOWN',
    sourceGuideRootHash: guide.rootHash || null,
    sourceGuideRootHashShort: guide.rootHashShort || null,
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function attachWilsyR91K115SourceGuide
 * @description Attaches source-guide constraints to a JSON response before it leaves an AI or command route.
 * @param {*} body - Original response body.
 * @param {Object} req - Express request.
 * @param {string} surface - Surface label.
 * @returns {Promise<*>} Enriched response body.
 * @collaboration CRM command search, Wilsy AI recommendations, Source Posture Guide constraints.
 */
async function attachWilsyR91K115SourceGuide(body, req = {}, surface = 'CRM_AI_SURFACE') {
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return body;
  }

  if (
    body.sourceGuide ||
    body.aiRecommendationConstraints?.sourceGuideStatus === 'SOURCE_GUIDE_ATTACHED'
  ) {
    return body;
  }

  const guide = await fetchWilsyR91K115SourceGuide(req);
  const constraintPacket = buildWilsyR91K115AiConstraintPacket(guide, surface);
  const guideNextBestActions = Array.isArray(guide?.nextBestActions) ? guide.nextBestActions : [];
  const originalNextBestActions = Array.isArray(body.nextBestActions) ? body.nextBestActions : [];
  const guideDirectives = Array.isArray(guide?.wilsyAiDirectives) ? guide.wilsyAiDirectives : [];

  return {
    ...body,
    sourceGuide: guide,
    sourceGuideStatus: constraintPacket.sourceGuideStatus,
    aiRecommendationConstraints: constraintPacket,
    wilsyAiDirectives: guideDirectives,
    nextBestActions: originalNextBestActions.length
      ? [...originalNextBestActions, ...guideNextBestActions]
      : guideNextBestActions,
    readinessScore: guide?.readinessScore ?? body.readinessScore,
    postureGrade: guide?.postureGrade ?? body.postureGrade,
    aiOperatingMode: guide?.aiOperatingMode ?? body.aiOperatingMode,
    routeSurface: guide?.routeSurface || body.routeSurface,
    sourcePosture: guide?.sourcePosture || body.sourcePosture,
    sourceGuideReceipt: guide
      ? {
          rootHash: guide.rootHash || null,
          rootHashShort: guide.rootHashShort || null,
          algorithmVersion: guide.algorithmVersion || null,
          generatedAt: guide.generatedAt || null,
        }
      : null,
  };
}

/**
 * @function wilsyR91K115SourceGuideResponseBridge
 * @description Wraps route JSON responses so Wilsy AI and command surfaces carry live source truth.
 * @param {string} surface - Response surface label.
 * @returns {Function} Express middleware.
 * @collaboration Source Posture Guide, CRM command fabric, CRM intelligence fabric, Wilsy AI directives.
 */
function wilsyR91K115SourceGuideResponseBridge(surface = 'CRM_AI_SURFACE') {
  return (req, res, next) => {
    if (!shouldWilsyR91K115BridgeSourceGuide(req)) {
      next();
      return;
    }

    const originalJson = res.json.bind(res);
    let sent = false;

    res.json = (body) => {
      if (sent) {
        return originalJson(body);
      }

      sent = true;
      attachWilsyR91K115SourceGuide(body, req, surface)
        .then((enrichedBody) => originalJson(enrichedBody))
        .catch(() => originalJson(body));

      return res;
    };

    next();
  };
}

router.use(wilsyR91K115SourceGuideResponseBridge('CRM_INTELLIGENCE_FABRIC'));

/**
 * @function asyncHandler
 * @description Wraps async Express handlers.
 * @param {Function} handler - Async route handler.
 * @returns {Function} Express middleware.
 * @collaboration Keeps CRM intelligence route errors centralized.
 */
function asyncHandler(handler) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

/**
 * @function sendRouteIndex
 * @description Sends CRM intelligence route index.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {void} Route response.
 * @collaboration Makes intelligence route posture smoke-testable.
 */
function sendRouteIndex(req, res) {
  res.json({
    ok: true,
    routes: [
      '/api/crm/intelligence/boardroom',
      ...getIntelligenceCollections().map((collection) => `/api/crm/intelligence/${collection}`),
    ],
  });
}

/**
 * @function sendBoardroomIntelligence
 * @description Sends boardroom CRM intelligence posture.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} Route response.
 * @collaboration Feeds investor-grade CRM telemetry, compliance, governance, revenue and scoring posture.
 */
async function sendBoardroomIntelligence(req, res) {
  res.json(await buildBoardroomIntelligence(req));
}

/**
 * @function sendIntelligenceCollection
 * @description Sends one CRM intelligence collection.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next handler.
 * @returns {Promise<void>} Route response.
 * @collaboration Provides read-only access to intelligence records without fake data.
 */
async function sendIntelligenceCollection(req, res, next) {
  const collection = String(req.params.collection || '').trim();

  if (!getIntelligenceCollections().includes(collection)) {
    return next();
  }

  const tenantId = getTenantId(req);
  const payload = await listIntelligenceRecords(collection, tenantId, req.query.limit);

  return res.json({
    ok: true,
    tenantId,
    collection,
    data: payload.records,
    records: payload.records,
    meta: payload.meta,
  });
}

router.get('/', sendRouteIndex);
router.get('/boardroom', asyncHandler(sendBoardroomIntelligence));
router.get('/:collection', asyncHandler(sendIntelligenceCollection));

export default router;
