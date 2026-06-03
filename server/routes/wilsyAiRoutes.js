/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - WILSY AI ROUTES [V1.0.0-PROTECTED-LICENSE-GATEWAY]                                                                         ║
 * ║ [CATALOG | ENTITLEMENTS | ACTIVATION | EXECUTIVE ACCESS | TENANT ISOLATION | FORENSIC RECEIPTS]                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PROTECTED-LICENSE-GATEWAY | PRODUCTION READY | WILSY AI CROSS-TENANT API SURFACE                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/wilsyAiRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required Wilsy AI to be licensable across tenants with monitored access attempts.                   ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Mounted catalog, entitlement and activation routes behind the existing sovereign API guard.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import {
  getRequestTenantId,
  getWilsyAIEntitlements,
  activateWilsyAILicense,
  buildWilsyAICatalogForTenant,
  aggregateWilsyAIUsage,
  buildSourceSilentUsageAnalytics,
  recordWilsyAIUsage
} from '../services/wilsyAIEntitlementService.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

const router = express.Router();

/**
 * @function getTenantProfileFromRequest
 * @description Extracts tenant profile context submitted by the authenticated dashboard.
 * @param {Object} req - Express request.
 * @returns {Object} Tenant profile.
 * @collaboration Keeps routes source-driven; if a profile is incomplete, the service reports that state instead of inventing context.
 */
const getTenantProfileFromRequest = (req = {}) => (
  req.body?.tenantProfile
  || req.query?.tenantProfile
  || {
    tenantId: getRequestTenantId(req),
    industryKey: req.query?.industryKey || 'general_smb',
    industryLabel: req.query?.industryLabel || 'General Business',
    sourceStatus: req.query?.profileSourceStatus || 'TENANT_PROFILE_INCOMPLETE',
    sourceEvidence: req.query?.sourceEvidence || 'Tenant profile context not supplied.'
  }
);

/**
 * @function getSourceSnapshotFromRequest
 * @description Extracts source heartbeat context from request body when available.
 * @param {Object} req - Express request.
 * @returns {Object} Source snapshot.
 * @collaboration The API receives source posture from the dashboard and refuses to promote source-gated modules without it.
 */
const getSourceSnapshotFromRequest = (req = {}) => req.body?.sourceSnapshot || {};

/**
 * @function buildSourceSilentEntitlementResponse
 * @description Builds a dashboard-safe entitlement response when license persistence is temporarily unavailable.
 * @param {Object} params - Source-silent context.
 * @param {string} params.tenantId - Active tenant id.
 * @param {Object} params.tenantProfile - Tenant business profile.
 * @param {Object} params.sourceSnapshot - Source heartbeat registry.
 * @param {Error} params.error - Runtime persistence error.
 * @returns {Object} Source-silent entitlement envelope.
 * @collaboration Wilsy AI catalog visibility must survive a license-store fracture without pretending any module is active.
 */
const buildSourceSilentEntitlementResponse = ({ tenantId, tenantProfile, sourceSnapshot, error } = {}) => {
  const catalog = buildWilsyAICatalogForTenant({
    tenantId,
    tenantProfile,
    sourceSnapshot,
    licenses: []
  }).map(module => ({
    ...module,
    licenseStatus: 'LICENSE_SOURCE_SILENT',
    reason: module.readiness === 'READY_TO_LICENSE'
      ? 'Wilsy AI module is operationally eligible, but license persistence is currently source-silent.'
      : module.reason
  }));

  return {
    success: false,
    status: 'WILSY_AI_ENTITLEMENT_SOURCE_SILENT',
    tenantId,
    catalog,
    licenses: [],
    error: error?.message || 'Wilsy AI entitlement persistence unavailable.'
  };
};

/**
 * @route GET /api/wilsy-ai/catalog
 * @description Returns the reusable Wilsy AI module catalog decorated for the active tenant profile.
 * @returns {Object} Catalog response.
 * @collaboration Lets any tenant type see the right AI modules without creating a new component file.
 */
router.get('/catalog', async (req, res, next) => {
  try {
    const tenantId = getRequestTenantId(req);
    const tenantProfile = getTenantProfileFromRequest(req);
    const catalog = buildWilsyAICatalogForTenant({ tenantId, tenantProfile, sourceSnapshot: {} });
    await broadcastTelemetry(tenantId, 'WILSY_AI_CATALOG_READ', 'COMMITTED', 'wilsyAiRoutes', {
      count: catalog.length
    }).catch(() => {});
    res.json({
      success: true,
      status: 'WILSY_AI_CATALOG_READY',
      tenantId,
      catalog
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route POST /api/wilsy-ai/entitlements
 * @description Returns license and entitlement posture for the active tenant.
 * @returns {Object} Entitlement posture.
 * @collaboration This is the dashboard's production source of truth for whether Wilsy AI is licensed.
 */
router.post('/entitlements', async (req, res, next) => {
  const tenantId = getRequestTenantId(req);
  const tenantProfile = getTenantProfileFromRequest(req);
  const sourceSnapshot = getSourceSnapshotFromRequest(req);
  try {
    const response = await getWilsyAIEntitlements({
      tenantId,
      tenantProfile,
      sourceSnapshot
    });
    res.json(response);
  } catch (error) {
    const response = buildSourceSilentEntitlementResponse({
      tenantId,
      tenantProfile,
      sourceSnapshot,
      error
    });
    await broadcastTelemetry(tenantId, 'WILSY_AI_ENTITLEMENT_SOURCE_SILENT', 'SOURCE_SILENT', 'wilsyAiRoutes', {
      message: error.message,
      catalogCount: response.catalog.length
    }).catch(() => {});
    res.status(200).json(response);
  }
});

/**
 * @route POST /api/wilsy-ai/licenses/activate
 * @description Activates a tenant-scoped Wilsy AI module license.
 * @returns {Object} Activation receipt with proof hash.
 * @collaboration Licensing is an executive command, not a frontend-only optimistic state mutation.
 */
router.post('/licenses/activate', async (req, res, next) => {
  try {
    const receipt = await activateWilsyAILicense({
      req,
      moduleId: req.body?.moduleId || req.body?.planId,
      tenantProfile: getTenantProfileFromRequest(req),
      sourceSnapshot: getSourceSnapshotFromRequest(req),
      dailyDutyKey: req.body?.dailyDutyKey || ''
    });
    res.status(201).json(receipt);
  } catch (error) {
    if (error.status) {
      return res.status(error.status).json({
        success: false,
        code: error.code || 'WILSY_AI_LICENSE_ERROR',
        message: error.message,
        proofHash: error.proofHash || null
      });
    }
    next(error);
  }
});

/**
 * @route GET /api/wilsy-ai/analytics
 * @description Returns tenant-scoped Wilsy AI usage, quota and ROI analytics for a module or license.
 * @returns {Object} Usage analytics packet.
 * @collaboration Wilsy AI must prove daily value and quota posture before tenants are asked to pay for more automation.
 */
router.get('/analytics', async (req, res) => {
  const tenantId = getRequestTenantId(req);
  const tier = req.query?.tier || 'WILSY_AI_STARTER';
  try {
    const analytics = await aggregateWilsyAIUsage({
      tenantId,
      moduleId: req.query?.moduleId || null,
      licenseId: req.query?.licenseId || null,
      tier
    });
    await broadcastTelemetry(tenantId, 'WILSY_AI_ANALYTICS_READ', analytics.quotaStatus, 'wilsyAiRoutes', {
      moduleId: req.query?.moduleId || null,
      licenseId: req.query?.licenseId || null,
      sourceStatus: analytics.sourceStatus
    }).catch(() => {});
    res.status(200).json({
      success: true,
      status: analytics.sourceStatus,
      tenantId,
      analytics
    });
  } catch (error) {
    const analytics = buildSourceSilentUsageAnalytics({ tier, error });
    await broadcastTelemetry(tenantId, 'WILSY_AI_ANALYTICS_SOURCE_SILENT', 'SOURCE_SILENT', 'wilsyAiRoutes', {
      message: error.message
    }).catch(() => {});
    res.status(200).json({
      success: false,
      status: analytics.sourceStatus,
      tenantId,
      analytics
    });
  }
});

/**
 * @route POST /api/wilsy-ai/usage/record
 * @description Records a Wilsy AI request for quota, billing and ROI analytics.
 * @returns {Object} Usage receipt.
 * @collaboration Every AI request should be measurable before it becomes an invoice line or investor metric.
 */
router.post('/usage/record', async (req, res, next) => {
  try {
    const receipt = await recordWilsyAIUsage({
      req,
      moduleId: req.body?.moduleId,
      licenseId: req.body?.licenseId || '',
      tier: req.body?.tier || 'WILSY_AI_STARTER',
      requestType: req.body?.requestType || '',
      requestUnits: req.body?.requestUnits || 1,
      status: req.body?.status || 'PLANNED',
      sourceStatus: req.body?.sourceStatus || 'REQUEST_CONTEXT',
      sourceEvidence: req.body?.sourceEvidence || '',
      sourceSnapshot: getSourceSnapshotFromRequest(req)
    });
    res.status(receipt.success ? 201 : 200).json(receipt);
  } catch (error) {
    if (error.status) {
      return res.status(error.status).json({
        success: false,
        code: error.code || 'WILSY_AI_USAGE_ERROR',
        message: error.message,
        proofHash: error.proofHash || null
      });
    }
    next(error);
  }
});

export default router;
