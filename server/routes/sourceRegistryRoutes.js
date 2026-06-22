/* eslint-disable */
import { attachSourceEvidenceRepairPlan } from '../config/sourceEvidenceRequirements.js';
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — SOURCE REGISTRY ROUTES                                          ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/routes/sourceRegistryRoutes.js                                 ║
 * ║ PURPOSE: Expose live source-registry verification endpoints.                ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This route module only wires HTTP endpoints to the Source Registry controller.
 *
 * It does not:
 * - mark sources VERIFIED
 * - invent connector data
 * - seal boardroom proof by itself
 * - export PDFs by itself
 * - bypass controller verification rules
 *
 * Truth remains inside:
 * - server/config/sourceRegistry.js
 * - server/services/sourceConnectors/*
 * - server/controllers/sourceRegistryController.js
 */

import express from 'express';
import {
  getSourceRegistryStatus,
  verifySources,
  sealBoardroomProof,
  exportInvestorPack,
} from '../controllers/sourceRegistryController.js';

const router = express.Router();

const ROUTE_VERSION = '1.0.0-PRODUCTION-NO-FAKE-DATA';

/**
 * @function noStore
 * @description Prevents browser/proxy caching for live verification endpoints.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Next middleware.
 * @returns {void}
 */
function noStore(req, res, next) {
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
}

/**
 * @function attachSourceRegistryRouteMeta
 * @description Adds route metadata headers for observability and forensic debugging.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Next middleware.
 * @returns {void}
 */
function attachSourceRegistryRouteMeta(req, res, next) {
  const traceId =
    req.headers?.['x-trace-id'] ||
    req.headers?.['x-correlation-id'] ||
    `SRC-ROUTE-${Date.now().toString(16).toUpperCase()}`;

  res.setHeader('X-Wilsy-Source-Registry', 'LIVE');
  res.setHeader('X-Wilsy-Source-Registry-Version', ROUTE_VERSION);
  res.setHeader('X-Wilsy-Source-Registry-Truth-Policy', 'NO_FAKE_VERIFIED');
  res.setHeader('X-Trace-Id', traceId);

  req.headers['x-trace-id'] = traceId;
  next();
}

/**
 * @function rejectEmptyVerifyPayload
 * @description Blocks meaningless source verification requests before controller work.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Next middleware.
 * @returns {object|void} Response or next.
 */
function rejectEmptyVerifyPayload(req, res, next) {
  const body = req.body || {};
  const hasArtifacts = Array.isArray(body.artifacts) && body.artifacts.length > 0;
  const hasCatalog = Array.isArray(body.catalog) && body.catalog.length > 0;
  const hasArtifact = body.artifact && typeof body.artifact === 'object';

  if (!hasArtifacts && !hasCatalog && !hasArtifact) {
    return res.status(422).json({
      success: false,
      error: {
        code: 'SOURCE_REGISTRY_ARTIFACT_PAYLOAD_REQUIRED',
        message:
          'Source Registry verification requires artifacts, catalog, or artifact in the request body.',
      },
      meta: {
        routeVersion: ROUTE_VERSION,
        truthPolicy: 'NO_FAKE_VERIFIED',
        generatedAt: new Date().toISOString(),
      },
    });
  }

  return next();
}

/**
 * @function rejectEmptySealPayload
 * @description Blocks seal/export calls that include neither verification nor artifacts.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Next middleware.
 * @returns {object|void} Response or next.
 */
function rejectEmptySealPayload(req, res, next) {
  const body = req.body || {};
  const hasVerification = body.verification && typeof body.verification === 'object';
  const hasArtifacts = Array.isArray(body.artifacts) && body.artifacts.length > 0;
  const hasCatalog = Array.isArray(body.catalog) && body.catalog.length > 0;
  const hasArtifact = body.artifact && typeof body.artifact === 'object';

  if (!hasVerification && !hasArtifacts && !hasCatalog && !hasArtifact) {
    return res.status(422).json({
      success: false,
      error: {
        code: 'SOURCE_REGISTRY_VERIFICATION_OR_ARTIFACTS_REQUIRED',
        message: 'This endpoint requires a verification payload or artifacts to verify.',
      },
      meta: {
        routeVersion: ROUTE_VERSION,
        truthPolicy: 'NO_FAKE_VERIFIED',
        generatedAt: new Date().toISOString(),
      },
    });
  }

  return next();
}

router.use(noStore);
router.use(attachSourceRegistryRouteMeta);

/**
 * @route GET /api/source-registry/health
 * @description Lightweight route health check. Does not verify evidence.
 */
router.get('/health', (req, res) =>
  res.status(200).json({
    success: true,
    data: {
      service: 'source-registry',
      status: 'ROUTES_READY',
      evidenceStatus: 'NOT_EVALUATED',
      truthPolicy: 'NO_FAKE_VERIFIED',
      version: ROUTE_VERSION,
      endpoints: {
        status: 'GET /api/source-registry/status',
        verify: 'POST /api/source-registry/verify',
        sealBoardroomProof: 'POST /api/source-registry/seal-boardroom-proof',
        investorPack: 'POST /api/source-registry/investor-pack',
      },
    },
    meta: {
      generatedAt: new Date().toISOString(),
    },
  })
);

/**
 * @route GET /api/source-registry/status
 * @description Inspects connector installation and required methods. Does not mark evidence verified.
 */
router.get('/status', getSourceRegistryStatus);

/**
 * @route POST /api/source-registry/verify
 * @description Verifies live source evidence for supplied artifacts/catalog.
 */

/**
 * WILSY_SOURCE_EVIDENCE_REPAIR_PLAN_RESPONSE_WRAPPER
 * Adds connector-level repair intelligence to Source Registry verification responses.
 * It never changes VERIFIED status and never fabricates evidence.
 */
function attachRepairPlanToVerifyResponse(req, res, next) {
  const originalJson = res.json.bind(res);

  res.json = (payload) => originalJson(attachSourceEvidenceRepairPlan(payload, req.body || {}));

  return next();
}

router.post('/verify', rejectEmptyVerifyPayload, attachRepairPlanToVerifyResponse, verifySources);

/**
 * @route POST /api/source-registry/seal-boardroom-proof
 * @description Creates a boardroom proof seal only when verification is fully VERIFIED.
 */
router.post('/seal-boardroom-proof', rejectEmptySealPayload, sealBoardroomProof);

/**
 * @route POST /api/source-registry/investor-pack
 * @description Builds investor pack payload only from verified source-registry evidence.
 */
router.post('/investor-pack', rejectEmptySealPayload, exportInvestorPack);

/**
 * @route ALL *
 * @description Normalized 404 for unsupported source-registry endpoints.
 */
router.all('*', (req, res) =>
  res.status(404).json({
    success: false,
    error: {
      code: 'SOURCE_REGISTRY_ROUTE_NOT_FOUND',
      message: `Unsupported Source Registry route: ${req.method} ${req.originalUrl || req.url}`,
    },
    meta: {
      routeVersion: ROUTE_VERSION,
      truthPolicy: 'NO_FAKE_VERIFIED',
      generatedAt: new Date().toISOString(),
    },
  })
);

export {
  ROUTE_VERSION,
  noStore,
  attachSourceRegistryRouteMeta,
  rejectEmptyVerifyPayload,
  rejectEmptySealPayload,
};

export default router;
