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
