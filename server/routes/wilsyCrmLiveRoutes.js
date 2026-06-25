/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM LIVE ROUTES                                                                                             ║
 * ║ /api/crm/live/source-posture | /api/crm/live/:collection                                                               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Live CRM source routes.
 */

import express from 'express';
import {
  buildSourcePosture,
  getAllowedCollections,
  listCrmCollection,
} from '../services/wilsyCrmLiveSourceService.js';

const router = express.Router();

/**
 * @function asyncHandler
 * @description Wraps async route handlers for Express.
 * @param {Function} handler - Async route handler.
 * @returns {Function} Express middleware.
 * @collaboration Keeps live CRM routes concise and safe.
 */
function asyncHandler(handler) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

/**
 * @function sendSourcePosture
 * @description Sends live CRM source posture.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} Route result.
 * @collaboration Feeds Root Hash and source route counter in the CRM header.
 */
async function sendSourcePosture(req, res) {
  const posture = await buildSourcePosture(req);
  res.json(posture);
}

/**
 * @function sendCrmCollection
 * @description Sends one live CRM collection.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next handler.
 * @returns {Promise<void>} Route result.
 * @collaboration Serves source-honest CRM records without fake data.
 */
async function sendCrmCollection(req, res, next) {
  const collection = String(req.params.collection || '').trim();
  const allowedCollections = getAllowedCollections();

  if (!allowedCollections.includes(collection)) {
    return next();
  }

  const payload = await listCrmCollection(req, collection);
  return res.json(payload);
}

/**
 * @function sendLiveRouteIndex
 * @description Sends live CRM route index.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {void} Route result.
 * @collaboration Exposes route availability for smoke tests and diagnostics.
 */
function sendLiveRouteIndex(req, res) {
  res.json({
    ok: true,
    routes: [
      '/api/crm/live/source-posture',
      ...getAllowedCollections().map((collection) => `/api/crm/live/${collection}`),
    ],
  });
}

router.get('/', sendLiveRouteIndex);
router.get('/source-posture', asyncHandler(sendSourcePosture));
router.get('/:collection', asyncHandler(sendCrmCollection));

export default router;
