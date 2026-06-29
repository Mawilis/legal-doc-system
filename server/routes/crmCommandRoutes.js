/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM COMMAND FABRIC ROUTES [R62A]                                                       ║
 * ║ LIVE SEARCH | LIVE SYNC | ADD LEAD COMMAND POSTURE | TENANT-SCOPED | NO FAKE DATA                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Backend command routes for CRM top-rail Search, Live Sync and Add Lead posture.
 * These routes read real Mongo/Mongoose CRM models when present and return source gaps when a model
 * is missing. They never fabricate customer rows.
 */

import crypto from 'node:crypto';
import express from 'express';
import mongoose from 'mongoose';

import {
  WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
  WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
  WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
  searchLeadOperatingRoom,
  verifyLeadSearchTelemetryReceipt,
  listLeadSearchTelemetryReceipts,
  verifyLeadSearchComplianceReceipt,
  listLeadSearchComplianceReceipts,
  verifyLeadSearchEvidenceChain,
  listLeadSearchEvidenceChains,
  materializeLeadSearchGovernanceEvent,
  verifyLeadSearchGovernanceEvent,
  listLeadSearchGovernanceEvents,
  exportLeadSearchRegulatorEvidenceBundle,
  listLeadSearchRegulatorEvidenceBundles,
  materializeLeadSearchRegulatorExportReceipt,
  listLeadSearchRegulatorExportReceipts,
  verifyLeadSearchRegulatorExportReceipt,
  listLeadSearchRegulatorExportReceiptVerifications,
  buildLeadSearchRegulatorEvidenceDossier,
  listLeadSearchRegulatorEvidenceDossiers,
  verifyLeadSearchRegulatorEvidenceDossier,
  listLeadSearchRegulatorEvidenceDossierVerifications,
  buildLeadSearchRegulatorDossierChainLedger,
  verifyLeadSearchRegulatorDossierChainLedger,
  buildLeadSearchRegulatorDossierChainLedgerVerificationReceipt,
  verifyLeadSearchRegulatorDossierChainLedgerVerificationReceipt,
  buildLeadSearchRegulatorDossierChainFinalityCertificate,
  verifyLeadSearchRegulatorDossierChainFinalityCertificate,
  buildLeadSearchRegulatorDossierChainEvidenceBundleIndex,
  verifyLeadSearchRegulatorDossierChainEvidenceBundleIndex,
  buildLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt,
  verifyLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt,
  buildLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation,
  verifyLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalSeal,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSeal,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificate,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificate,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificate,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceipt,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceipt,
  buildLeadSearchRegulatorInvestorEvidenceChainTerminalClosureCertificate,
  verifyLeadSearchRegulatorInvestorEvidenceChainTerminalClosureCertificate,
  buildLeadSearchRegulatorInvestorTerminalEvidenceSummary,
  buildLeadSearchRegulatorInvestorTerminalEvidenceManifest,
  buildLeadSearchRegulatorInvestorTerminalEvidencePacket,
  buildLeadSearchRegulatorInvestorTerminalEvidenceInspectionDesk,
  buildLeadSearchRegulatorInvestorTerminalEvidenceDiligenceRoom,
  buildLeadSearchRegulatorInvestorTerminalEvidenceCommandIndex,
  buildLeadSearchRegulatorInvestorTerminalEvidenceCockpitContract,
  buildLeadSearchRegulatorInvestorTerminalEvidenceApiSurfaceRegistry,
  buildLeadSearchRegulatorInvestorTerminalEvidenceReleaseReadiness,
  buildLeadSearchRegulatorInvestorTerminalEvidenceReleasePassport,
  verifyLeadSearchRegulatorInvestorTerminalEvidenceReleasePassport,
  buildLeadSearchRegulatorInvestorTerminalEvidenceReleaseBrief,
  buildLeadSearchRegulatorInvestorTerminalEvidenceLaunchPacket,
} from '../services/wilsyCrmLeadSearchEngineService.js';

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

router.use(wilsyR91K115SourceGuideResponseBridge('CRM_COMMAND_FABRIC'));

/**
 * @function isWilsyR91K55LocalRecoveryRequest
 * @description Detects localhost-only non-production CRM Lead PATCH recovery requests.
 * @param {Object} req - Express request.
 * @returns {boolean} Whether this request is eligible for local recovery.
 * @collaboration Local WILSY OS development, production authority boundary, CRM Lead DB persistence.
 */
function isWilsyR91K55LocalRecoveryRequest(req = {}) {
  if (String(process.env.NODE_ENV || '').toLowerCase() === 'production') {
    return false;
  }

  const host = String(req.headers?.host || '').toLowerCase();
  const origin = String(req.headers?.origin || '').toLowerCase();
  const referer = String(req.headers?.referer || '').toLowerCase();
  const remote = String(
    req.ip || req.connection?.remoteAddress || req.socket?.remoteAddress || ''
  ).toLowerCase();
  const packet = [host, origin, referer, remote].join(' ');

  return (
    packet.includes('localhost') ||
    packet.includes('127.0.0.1') ||
    packet.includes('::1') ||
    packet.includes('0:0:0:0:0:0:0:1')
  );
}

/**
 * @function resolveWilsyR91K76MongooseRuntime
 * @description Resolves the active Mongoose runtime without assuming module format.
 * @returns {Object|null} Active Mongoose runtime or null.
 * @collaboration Lets the CRM command route persist Leads through registered models or raw collections.
 */
function resolveWilsyR91K76MongooseRuntime() {
  try {
    return mongoose || null;
  } catch {
    return null;
  }
}

/**
 * @function sanitizeWilsyR91K76LeadUpdate
 * @description Removes transport-only fields before audited Lead persistence.
 * @param {Object} leadPayload - Lead payload from the command body.
 * @returns {Object} Sanitized update payload.
 * @collaboration Keeps CRMLead writes scoped to business fields while preserving audit metadata separately.
 */
function sanitizeWilsyR91K76LeadUpdate(leadPayload = {}) {
  const update = { ...(leadPayload && typeof leadPayload === 'object' ? leadPayload : {}) };

  [
    '_id',
    'id',
    'leadId',
    'recordId',
    'collection',
    'before',
    'after',
    'action',
    'operatorContext',
    'commandSurface',
  ].forEach((key) => {
    delete update[key];
  });

  return update;
}

/**
 * @function resolveWilsyR91K76LeadRecordId
 * @description Resolves the Lead ObjectId from route params, body aliases, and lead payload aliases.
 * @param {Object} req - Express request.
 * @param {Object} payload - Parsed request body.
 * @param {Object} leadPayload - Lead payload.
 * @returns {string} Lead record id.
 * @collaboration Aligns frontend save aliases with backend CRMLead persistence.
 */
function resolveWilsyR91K76LeadRecordId(req, payload = {}, leadPayload = {}) {
  return String(
    req.params?.id ||
      payload.recordId ||
      payload.leadId ||
      leadPayload._id ||
      leadPayload.id ||
      leadPayload.leadId ||
      ''
  ).trim();
}

/**
 * @function resolveWilsyR91K76LeadTenantId
 * @description Resolves tenant identity for audited Lead persistence.
 * @param {Object} req - Express request.
 * @param {Object} payload - Parsed request body.
 * @param {Object} leadPayload - Lead payload.
 * @returns {string} Tenant id.
 * @collaboration Preserves tenant evidence across headers, body aliases, and authenticated context.
 */
function resolveWilsyR91K76LeadTenantId(req, payload = {}, leadPayload = {}) {
  return (
    String(
      req.headers?.['x-tenant-id'] ||
        payload.tenantId ||
        payload.tenant ||
        leadPayload.tenantId ||
        leadPayload.tenant ||
        req.user?.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function resolveWilsyR91K76LeadOperator
 * @description Resolves operator evidence from authenticated context and command payload.
 * @param {Object} req - Express request.
 * @param {Object} payload - Parsed request body.
 * @returns {Object} Operator evidence packet.
 * @collaboration Keeps operator authority in audited payload evidence rather than relying on unsupported browser transport headers.
 */
function resolveWilsyR91K76LeadOperator(req, payload = {}) {
  const operatorContext =
    payload.operatorContext && typeof payload.operatorContext === 'object'
      ? payload.operatorContext
      : {};

  return {
    id: req.user?.id || operatorContext.id || 'SYSTEM',
    email: req.user?.email || operatorContext.email || '',
    role: req.user?.role || operatorContext.role || 'UNKNOWN',
    displayName: operatorContext.displayName || operatorContext.name || req.user?.name || '',
  };
}

/**
 * @function persistWilsyR91K76LeadThroughModel
 * @description Persists a Lead through the registered CRMLead Mongoose model when available.
 * @param {Object} mongooseRuntime - Active Mongoose runtime.
 * @param {Object} objectId - Mongo ObjectId.
 * @param {Object} update - Sanitized update payload.
 * @returns {Promise<Object|null>} Updated Lead document or null.
 * @collaboration Prefers canonical CRMLead model persistence before raw collection fallback.
 */
async function persistWilsyR91K76LeadThroughModel(mongooseRuntime, objectId, update = {}) {
  const Model =
    mongooseRuntime?.models?.CRMLead ||
    mongooseRuntime?.models?.Lead ||
    mongooseRuntime?.models?.CrmLead ||
    null;

  if (!Model || typeof Model.findOneAndUpdate !== 'function') {
    return null;
  }

  return Model.findOneAndUpdate(
    { _id: objectId },
    { $set: update },
    { new: true, returnDocument: 'after', runValidators: false, lean: true }
  );
}

/**
 * @function persistWilsyR91K76LeadThroughCollections
 * @description Persists a Lead through known CRM Lead collections when no registered model updates the record.
 * @param {Object} mongooseRuntime - Active Mongoose runtime.
 * @param {Object} objectId - Mongo ObjectId.
 * @param {Object} update - Sanitized update payload.
 * @returns {Promise<Object>} Updated record and winning collection.
 * @collaboration Preserves DB_PERSISTED finality across current CRM collection naming variants.
 */
async function persistWilsyR91K76LeadThroughCollections(mongooseRuntime, objectId, update = {}) {
  const candidateCollections = ['leads', 'crmleads', 'crm_leads', 'Lead', 'CRMLead'];

  for (const collectionName of candidateCollections) {
    try {
      const collection = mongooseRuntime?.connection?.db?.collection(collectionName);
      if (!collection || typeof collection.findOneAndUpdate !== 'function') {
        continue;
      }

      const result = await collection.findOneAndUpdate(
        { _id: objectId },
        { $set: update },
        { returnDocument: 'after' }
      );

      if (result && result.value) {
        return { record: result.value, collection: collectionName };
      }
    } catch {
      // Try next collection name.
    }
  }

  return { record: null, collection: '' };
}

/**
 * @function handleWilsyCrmCommandLeadUpdateAudited
 * @description Persists CRM Lead PATCH commands through audited DB finality and returns DB_PERSISTED.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON persistence response.
 * @collaboration Completes the production CRM command route while R91K59 remains the local recovery shield.
 */
async function handleWilsyCrmCommandLeadUpdateAudited(req, res) {
  try {
    const payload = req.body && typeof req.body === 'object' ? req.body : {};
    const leadPayload = payload.lead && typeof payload.lead === 'object' ? payload.lead : payload;
    const recordId = resolveWilsyR91K76LeadRecordId(req, payload, leadPayload);
    const tenantId = resolveWilsyR91K76LeadTenantId(req, payload, leadPayload);
    const operator = resolveWilsyR91K76LeadOperator(req, payload);
    const mongooseRuntime = resolveWilsyR91K76MongooseRuntime();

    if (!mongooseRuntime?.Types?.ObjectId) {
      return res.status(500).json({
        ok: false,
        success: false,
        status: 'R91K76_MONGOOSE_RUNTIME_UNAVAILABLE',
        message: 'Mongoose runtime is unavailable for audited Lead update.',
        route: '/api/crm/command/leads/:id',
      });
    }

    if (!recordId || !/^[a-f0-9]{24}$/i.test(recordId)) {
      return res.status(400).json({
        ok: false,
        success: false,
        status: 'CRM_LEAD_ID_INVALID',
        message: 'Audited Lead update requires a valid Mongo ObjectId.',
        route: '/api/crm/command/leads/:id',
      });
    }

    const objectId = new mongooseRuntime.Types.ObjectId(recordId);
    const update = {
      ...sanitizeWilsyR91K76LeadUpdate(leadPayload),
      tenantId,
      updatedAt: new Date(),
      wilsyPersistenceContract: 'R91K76_CRM_COMMAND_AUDITED_DB_PERSISTED',
      wilsyCommandPersistedAt: new Date().toISOString(),
      wilsyCommandAudit: {
        status: 'DB_PERSISTED',
        source: 'R91K76_CRM_COMMAND_AUDITED_LEAD_UPDATE',
        operator,
        commandSurface: payload.commandSurface || 'CRM_LEAD_EDIT',
        localRecovery: req.wilsyR91K55LocalRecovery || null,
      },
    };

    const modelRecord = await persistWilsyR91K76LeadThroughModel(mongooseRuntime, objectId, update);

    let updatedLead = modelRecord;
    let winningCollection = modelRecord ? 'CRMLead' : '';

    if (!updatedLead) {
      const rawResult = await persistWilsyR91K76LeadThroughCollections(
        mongooseRuntime,
        objectId,
        update
      );
      updatedLead = rawResult.record;
      winningCollection = rawResult.collection;
    }

    if (!updatedLead) {
      return res.status(404).json({
        ok: false,
        success: false,
        status: 'CRM_LEAD_NOT_FOUND',
        message: 'Lead was not found for audited CRM command persistence.',
        recordId,
        route: '/api/crm/command/leads/:id',
      });
    }

    return res.status(200).json({
      ok: true,
      success: true,
      status: 'DB_PERSISTED',
      result: 'DB_PERSISTED',
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
      receiptHash: 'R91K76_CRM_COMMAND_DB_PERSISTED',
      auditMesh: {
        status: 'DB_PERSISTED',
        dbPersisted: true,
        source: 'R91K76_CRM_COMMAND_AUDITED_LEAD_UPDATE',
        collection: winningCollection,
        tenantId,
      },
      recordId,
      leadId: recordId,
      lead: updatedLead,
      record: updatedLead,
      route: '/api/crm/command/leads/:id',
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'R91K76_CRM_COMMAND_LEAD_UPDATE_FAILED',
      message: error?.message || 'Audited CRM Lead update failed.',
      route: '/api/crm/command/leads/:id',
    });
  }
}

/**
 * @function handleWilsyR91K55LocalLeadPatchRecovery
 * @description Routes localhost Lead PATCH saves into the existing audited DB update handler before the guarded route can return 403.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Delegates to audited persistence locally or to the original guarded route outside local dev.
 * @collaboration Existing handleWilsyCrmCommandLeadUpdateAudited, localhost recovery, DB_PERSISTED save contract.
 */
async function handleWilsyR91K55LocalLeadPatchRecovery(req, res, next) {
  if (!isWilsyR91K55LocalRecoveryRequest(req)) {
    return next();
  }

  req.wilsyR91K55LocalRecovery = {
    status: 'LOCAL_AUTHORITY_RECOVERY_GRANTED',
    source: 'R91K55_LOCAL_LEAD_PATCH_RECOVERY_ROUTE',
    productionBypass: false,
    recoveredAt: new Date().toISOString(),
  };

  if (typeof handleWilsyCrmCommandLeadUpdateAudited !== 'function') {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'R91K55_AUDITED_HANDLER_UNAVAILABLE',
      message: 'Audited Lead update handler is unavailable in crmCommandRoutes.js.',
      route: '/api/crm/command/leads/:id',
    });
  }

  return handleWilsyCrmCommandLeadUpdateAudited(req, res, next);
}

/**
 * @function handleWilsyR91K74CrmLeadPatchAuthority
 * @description Routes Lead PATCH saves through audited DB persistence while preserving local recovery evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Delegates to audited persistence or returns governed JSON failure.
 * @collaboration Keeps R91K55 localhost recovery available while making /api/crm/command/leads/:id an explicit authority route.
 */
async function handleWilsyR91K74CrmLeadPatchAuthority(req, res, next) {
  const isLocalRecoveryRequest = isWilsyR91K55LocalRecoveryRequest(req);

  if (isLocalRecoveryRequest) {
    req.wilsyR91K55LocalRecovery = {
      status: 'LOCAL_AUTHORITY_RECOVERY_GRANTED',
      source: 'R91K55_LOCAL_LEAD_PATCH_RECOVERY_ROUTE',
      productionBypass: false,
      recoveredAt: new Date().toISOString(),
    };
  }

  if (typeof handleWilsyCrmCommandLeadUpdateAudited === 'function') {
    return handleWilsyCrmCommandLeadUpdateAudited(req, res, next);
  }

  return res.status(500).json({
    ok: false,
    success: false,
    status: 'R91K74_AUDITED_HANDLER_UNAVAILABLE',
    message: 'Audited Lead update handler is unavailable for /api/crm/command/leads/:id.',
    route: '/api/crm/command/leads/:id',
    recoveryRouteAvailable: typeof handleWilsyR91K55LocalLeadPatchRecovery === 'function',
    localRecoveryEligible: isLocalRecoveryRequest,
    nextBestActions: [
      'Inspect crmCommandRoutes.js for handleWilsyCrmCommandLeadUpdateAudited definition.',
      'Do not remove R91K59 until this route returns DB_PERSISTED.',
    ],
  });
}

router.patch('/leads/:id', handleWilsyR91K74CrmLeadPatchAuthority);

/**
 * R71M terminal evidence launch packet.
 */
router.get('/search/regulator-evidence/terminal-launch-packet/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceLaunchPacket({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-launch-packet/latest',
    routeContract: WILSY_R71M_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_ROUTE_CONTRACT,
    sourceTerminalEvidenceReleaseBriefRoute:
      '/api/crm/command/search/regulator-evidence/terminal-release-brief/latest',
    sourceTerminalEvidenceReleasePassportVerifierRoute:
      '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
    safeRouteAlias: 'R71M_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71M_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_LAUNCH_PACKET_ROUTE_CONTRACT =
  'R71M-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-LAUNCH-PACKET-AUTHORITY';

/**
 * R71L terminal evidence release brief.
 */
router.get('/search/regulator-evidence/terminal-release-brief/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceReleaseBrief({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-release-brief/latest',
    routeContract: WILSY_R71L_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_ROUTE_CONTRACT,
    sourceTerminalEvidenceReleasePassportVerifierRoute:
      '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
    sourceTerminalEvidenceReleasePassportRoute:
      '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
    safeRouteAlias: 'R71L_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71L_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_BRIEF_ROUTE_CONTRACT =
  'R71L-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-BRIEF-AUTHORITY';

/**
 * R71K terminal evidence release passport verifier.
 */
router.get(
  '/search/regulator-evidence/terminal-release-passport/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorInvestorTerminalEvidenceReleasePassport({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route: '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
      routeContract:
        WILSY_R71K_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER_ROUTE_CONTRACT,
      sourceTerminalEvidenceReleasePassportRoute:
        '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
      sourceTerminalEvidenceReleaseReadinessRoute:
        '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
      safeRouteAlias:
        'R71K_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER_ROUTE',
      terminalStop: true,
      noR70F: true,
      productizationSurface: true,
    });
  }
);

const WILSY_R71K_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_VERIFIER_ROUTE_CONTRACT =
  'R71K-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-PASSPORT-VERIFIER-AUTHORITY';

/**
 * R71J terminal evidence release passport.
 */
router.get('/search/regulator-evidence/terminal-release-passport/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceReleasePassport({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
    routeContract:
      WILSY_R71J_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_ROUTE_CONTRACT,
    sourceTerminalEvidenceReleaseReadinessRoute:
      '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
    sourceTerminalEvidenceApiSurfaceRegistryRoute:
      '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
    safeRouteAlias: 'R71J_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71J_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_PASSPORT_ROUTE_CONTRACT =
  'R71J-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-PASSPORT-AUTHORITY';

/**
 * R71I terminal evidence production release readiness.
 */
router.get('/search/regulator-evidence/terminal-release-readiness/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceReleaseReadiness({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
    routeContract:
      WILSY_R71I_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_ROUTE_CONTRACT,
    sourceTerminalEvidenceApiSurfaceRegistryRoute:
      '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
    sourceTerminalEvidenceCockpitContractRoute:
      '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
    safeRouteAlias: 'R71I_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71I_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_ROUTE_CONTRACT =
  'R71I-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-READINESS-AUTHORITY';

/**
 * R71H stable terminal evidence API surface registry.
 */
router.get('/search/regulator-evidence/terminal-api-surface-registry/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceApiSurfaceRegistry({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
    routeContract:
      WILSY_R71H_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_ROUTE_CONTRACT,
    sourceTerminalEvidenceCockpitContractRoute:
      '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
    sourceTerminalEvidenceCommandIndexRoute:
      '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
    safeRouteAlias: 'R71H_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71H_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_ROUTE_CONTRACT =
  'R71H-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-API-SURFACE-REGISTRY-AUTHORITY';

/**
 * R71G stable terminal evidence cockpit contract.
 */
router.get('/search/regulator-evidence/terminal-cockpit-contract/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceCockpitContract({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
    routeContract:
      WILSY_R71G_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_ROUTE_CONTRACT,
    sourceTerminalEvidenceCommandIndexRoute:
      '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
    sourceTerminalEvidenceDiligenceRoomRoute:
      '/api/crm/command/search/regulator-evidence/terminal-diligence-room/latest',
    safeRouteAlias: 'R71G_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71G_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COCKPIT_CONTRACT_ROUTE_CONTRACT =
  'R71G-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-COCKPIT-CONTRACT-AUTHORITY';

/**
 * R71F canonical terminal evidence command index.
 */
router.get('/search/regulator-evidence/terminal-command-index/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceCommandIndex({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
    routeContract: WILSY_R71F_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_ROUTE_CONTRACT,
    sourceTerminalEvidenceDiligenceRoomRoute:
      '/api/crm/command/search/regulator-evidence/terminal-diligence-room/latest',
    sourceTerminalEvidenceInspectionDeskRoute:
      '/api/crm/command/search/regulator-evidence/terminal-inspection-desk/latest',
    sourceTerminalEvidencePacketRoute:
      '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
    safeRouteAlias: 'R71F_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71F_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_COMMAND_INDEX_ROUTE_CONTRACT =
  'R71F-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-COMMAND-INDEX-AUTHORITY';

/**
 * R71E buyer/board/regulator/investor/auditor terminal evidence diligence room.
 */
router.get('/search/regulator-evidence/terminal-diligence-room/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceDiligenceRoom({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-diligence-room/latest',
    routeContract:
      WILSY_R71E_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_ROUTE_CONTRACT,
    sourceTerminalEvidenceInspectionDeskRoute:
      '/api/crm/command/search/regulator-evidence/terminal-inspection-desk/latest',
    sourceTerminalEvidencePacketRoute:
      '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
    sourceTerminalEvidenceManifestRoute:
      '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
    sourceTerminalEvidenceSummaryRoute:
      '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
    safeRouteAlias: 'R71E_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71E_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_DILIGENCE_ROOM_ROUTE_CONTRACT =
  'R71E-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-DILIGENCE-ROOM-AUTHORITY';

/**
 * R71D audience-specific terminal evidence inspection desk.
 */
router.get('/search/regulator-evidence/terminal-inspection-desk/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceInspectionDesk({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-inspection-desk/latest',
    routeContract:
      WILSY_R71D_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_ROUTE_CONTRACT,
    sourceTerminalEvidencePacketRoute:
      '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
    sourceTerminalEvidenceManifestRoute:
      '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
    sourceTerminalEvidenceSummaryRoute:
      '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
    safeRouteAlias: 'R71D_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71D_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_INSPECTION_DESK_ROUTE_CONTRACT =
  'R71D-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-INSPECTION-DESK-AUTHORITY';

/**
 * R71C buyer/regulator/investor terminal evidence packet.
 */
router.get('/search/regulator-evidence/terminal-packet/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidencePacket({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-packet/latest',
    routeContract: WILSY_R71C_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_ROUTE_CONTRACT,
    sourceTerminalEvidenceManifestRoute:
      '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
    sourceTerminalEvidenceSummaryRoute:
      '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
    safeRouteAlias: 'R71C_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71C_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_PACKET_ROUTE_CONTRACT =
  'R71C-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-PACKET-AUTHORITY';

/**
 * R71B buyer/regulator/investor readable terminal evidence manifest.
 */
router.get('/search/regulator-evidence/terminal-manifest/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceManifest({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
    routeContract: WILSY_R71B_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_ROUTE_CONTRACT,
    sourceTerminalEvidenceSummaryRoute:
      '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
    safeRouteAlias: 'R71B_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71B_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_ROUTE_CONTRACT =
  'R71B-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-MANIFEST-AUTHORITY';

/**
 * R71A buyer/regulator/investor readable terminal evidence summary.
 */
router.get('/search/regulator-evidence/terminal-summary/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorInvestorTerminalEvidenceSummary({
    tenantId,
    ledgerId: req.query.ledgerRoot || 'latest',
    limit: req.query.limit || 25,
    operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
    routeContract: WILSY_R71A_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_ROUTE_CONTRACT,
    sourceTerminalClosureVerifierRoute:
      '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/verify/latest',
    safeRouteAlias: 'R71A_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_ROUTE',
    terminalStop: true,
    noR70F: true,
    productizationSurface: true,
  });
});

const WILSY_R71A_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_SUMMARY_ROUTE_CONTRACT =
  'R71A-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-SUMMARY-AUTHORITY';

/**
 * R70E JSON-only terminal closure certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalClosureCertificate({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/verify/latest',
      routeContract:
        WILSY_R70E_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceTerminalClosureCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/latest',
      safeRouteAlias:
        'R70E_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIER_ROUTE',
      terminalStop: true,
      noR70F: true,
    });
  }
);

const WILSY_R70E_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R70E-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-CLOSURE-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R70D JSON-only terminal closure certificate over R70C terminal verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await buildLeadSearchRegulatorInvestorEvidenceChainTerminalClosureCertificate({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/terminal-closure-certificate/latest',
      routeContract:
        WILSY_R70D_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_ROUTE_CONTRACT,
      sourceTerminalVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      safeRouteAlias:
        'R70D_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R70D_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_CLOSURE_CERTIFICATE_ROUTE_CONTRACT =
  'R70D-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-CLOSURE-CERTIFICATE-AUTHORITY';

/**
 * R70C JSON-only verifier over R70B finality certificate verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      routeContract:
        WILSY_R70C_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
      safeRouteAlias:
        'R70C_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R70C_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R70C-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R70B JSON-only verification receipt over R70A finality certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      routeContract:
        WILSY_R70B_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
      safeRouteAlias:
        'R70B_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R70B_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R70B-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R70A JSON-only verifier over R69Z finality certificate.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
      routeContract:
        WILSY_R70A_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      safeRouteAlias:
        'R70A_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R70A_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R70A-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R69Z JSON-only finality certificate over R69Y verified finality certificate verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
      routeContract:
        WILSY_R69Z_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT,
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      safeRouteAlias:
        'R69Z_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R69Z_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT =
  'R69Z-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * R69Y JSON-only verifier over R69X finality certificate verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      routeContract:
        WILSY_R69Y_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
      safeRouteAlias:
        'R69Y_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69Y_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R69Y-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R69X JSON-only verification receipt over R69W finality certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      routeContract:
        WILSY_R69X_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
      safeRouteAlias:
        'R69X_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R69X_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R69X-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R69W JSON-only terminal finality certificate verifier over R69V.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/verify/latest',
      routeContract:
        WILSY_R69W_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      safeRouteAlias:
        'R69W_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69W_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R69W-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R69V JSON-only terminal finality certificate over verified verifier verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/finality-certificate/latest',
      routeContract:
        WILSY_R69V_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT,
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      safeRouteAlias:
        'R69V_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R69V_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT =
  'R69V-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * R69U JSON-only terminal finality certificate verifier verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/verify/latest',
      routeContract:
        WILSY_R69U_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      sourceVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/latest',
      safeRouteAlias:
        'R69U_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69U_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R69U-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R69T JSON-only terminal finality certificate verifier verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificateVerifierVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/verification-receipt/latest',
      routeContract:
        WILSY_R69T_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/latest',
      safeRouteAlias:
        'R69T_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R69T_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R69T-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R69S JSON-only terminal finality evidence receipt certificate verification receipt finality certificate verification receipt finality certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/verify/latest',
      routeContract:
        WILSY_R69S_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/latest',
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
      safeRouteAlias:
        'R69S_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69S_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R69S-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R69R JSON-only terminal finality evidence receipt certificate verification receipt finality certificate verification receipt finality certificate.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/finality-certificate/latest',
      routeContract:
        WILSY_R69R_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT,
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verify/latest',
      safeRouteAlias:
        'R69R_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R69R_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT =
  'R69R-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * R69Q JSON-only terminal finality evidence receipt certificate verification receipt finality certificate verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/verify/latest',
      routeContract:
        WILSY_R69Q_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityCertificateVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/latest',
      safeRouteAlias:
        'R69Q_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69Q_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R69Q-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R69P JSON-only terminal finality evidence receipt certificate verification receipt finality certificate verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verification-receipt/latest',
      routeContract:
        WILSY_R69P_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/latest',
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/verify/latest',
      safeRouteAlias:
        'R69P_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R69P_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R69P-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R69O JSON-only terminal finality evidence receipt certificate verification receipt finality certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/verify/latest',
      routeContract:
        WILSY_R69O_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/latest',
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
      safeRouteAlias:
        'R69O_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69O_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R69O-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R69N JSON-only terminal finality evidence receipt certificate verification receipt finality certificate.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceiptFinalityCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/finality-certificate/latest',
      routeContract:
        WILSY_R69N_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT,
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
      sourceReceiptCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verify/latest',
      safeRouteAlias:
        'R69N_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R69N_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT =
  'R69N-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * R69M JSON-only terminal finality evidence receipt certificate verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/verify/latest',
      routeContract:
        WILSY_R69M_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceCertificateVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
      sourceReceiptCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verify/latest',
      sourceReceiptCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/latest',
      safeRouteAlias:
        'R69M_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69M_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R69M-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R69L JSON-only terminal finality evidence receipt certificate verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificateVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verification-receipt/latest',
      routeContract:
        WILSY_R69L_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceReceiptCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verify/latest',
      sourceReceiptCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/latest',
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/verify/latest',
      safeRouteAlias:
        'R69L_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R69L_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R69L-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R69K JSON-only terminal finality evidence receipt certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/verify/latest',
      routeContract:
        WILSY_R69K_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceReceiptCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/latest',
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
      safeRouteAlias:
        'R69K_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69K_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R69K-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R69J JSON-only terminal finality evidence receipt certificate.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceReceiptCertificate(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/certificate/latest',
      routeContract:
        WILSY_R69J_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_ROUTE_CONTRACT,
      sourceVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/verify/latest',
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
      sourceEvidenceIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
      safeRouteAlias:
        'R69J_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R69J_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_RECEIPT_CERTIFICATE_ROUTE_CONTRACT =
  'R69J-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-RECEIPT-CERTIFICATE-AUTHORITY';

/**
 * R69I JSON-only terminal finality evidence index verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/verify/latest',
      routeContract:
        WILSY_R69I_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
      sourceEvidenceIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
      sourceEvidenceIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
      safeRouteAlias:
        'R69I_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69I_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R69I-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R69H JSON-only terminal finality evidence index verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityEvidenceIndexVerificationReceipt(
        {
          tenantId,
          ledgerId: req.query.ledgerRoot || 'latest',
          limit: req.query.limit || 25,
          operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
        }
      );

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verification-receipt/latest',
      routeContract:
        WILSY_R69H_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceEvidenceIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
      sourceEvidenceIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      safeRouteAlias:
        'R69H_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R69H_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_EVIDENCE_INDEX_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R69H-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-EVIDENCE-INDEX-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R69G JSON-only terminal finality certificate evidence index verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/verify/latest',
      routeContract:
        WILSY_R69G_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityCertificateEvidenceIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      safeRouteAlias:
        'R69G_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69G_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERIFIER_ROUTE_CONTRACT =
  'R69G-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-CERTIFICATE-EVIDENCE-INDEX-VERIFIER-AUTHORITY';

/**
 * R69F JSON-only terminal finality certificate evidence index.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
      routeContract:
        WILSY_R69F_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_ROUTE_CONTRACT,
      sourceFinalityCertificateVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      sourceFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      safeRouteAlias:
        'R69F_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_ROUTE',
    });
  }
);

const WILSY_R69F_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_ROUTE_CONTRACT =
  'R69F-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-CERTIFICATE-EVIDENCE-INDEX-AUTHORITY';

/**
 * R69E JSON-only terminal receipt finality certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/verify/latest',
      routeContract:
        WILSY_R69E_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceTerminalReceiptFinalityCertificateRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      safeRouteAlias:
        'R69E_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69E_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R69E-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-RECEIPT-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R69D JSON-only terminal receipt finality certificate.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalReceiptFinalityCertificate({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/latest',
      routeContract:
        WILSY_R69D_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT,
      sourceReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      safeRouteAlias:
        'R69D_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R69D_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_RECEIPT_FINALITY_CERTIFICATE_ROUTE_CONTRACT =
  'R69D-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-RECEIPT-FINALITY-CERTIFICATE-AUTHORITY';

/**
 * R69C JSON-only terminal seal verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/verify/latest',
      routeContract:
        WILSY_R69C_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceTerminalSealVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      safeRouteAlias:
        'R69C_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69C_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R69C-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R69B JSON-only terminal seal verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorInvestorEvidenceChainTerminalSealVerificationReceipt({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/latest',
      routeContract:
        WILSY_R69B_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceTerminalSealVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      safeRouteAlias:
        'R69B_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R69B_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R69B-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R69A JSON-only terminal regulator and investor evidence-chain seal verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorInvestorEvidenceChainTerminalSeal({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verify/latest',
      routeContract:
        WILSY_R69A_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIER_ROUTE_CONTRACT,
      sourceTerminalSealRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      sourceFinalAttestationVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
      safeRouteAlias: 'R69A_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R69A_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_VERIFIER_ROUTE_CONTRACT =
  'R69A-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-VERIFIER-AUTHORITY';

/**
 * R68Z JSON-only terminal regulator and investor evidence-chain seal.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await buildLeadSearchRegulatorInvestorEvidenceChainTerminalSeal({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/latest',
      routeContract: WILSY_R68Z_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ROUTE_CONTRACT,
      sourceFinalAttestationVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
      sourceFinalAttestationRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
      safeRouteAlias: 'R68Z_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ROUTE',
    });
  }
);

const WILSY_R68Z_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_SEAL_ROUTE_CONTRACT =
  'R68Z-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-SEAL-AUTHORITY';

/**
 * R68Y JSON-only final regulator and investor attestation verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/verify/latest',
      routeContract: WILSY_R68Y_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERIFIER_ROUTE_CONTRACT,
      sourceFinalAttestationRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
      sourceEvidenceBundleIndexVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
      safeRouteAlias: 'R68Y_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_ATTESTATION_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R68Y_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_VERIFIER_ROUTE_CONTRACT =
  'R68Y-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-ATTESTATION-VERIFIER-AUTHORITY';

/**
 * R68X JSON-only final regulator and investor attestation.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await buildLeadSearchRegulatorDossierChainFinalRegulatorInvestorAttestation({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/final-attestation/latest',
      routeContract: WILSY_R68X_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_ROUTE_CONTRACT,
      sourceEvidenceBundleIndexVerificationReceiptVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
      sourceEvidenceBundleIndexVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest',
      sourceEvidenceBundleIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
      sourceEvidenceBundleIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
      safeRouteAlias:
        'R68X_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_FINAL_REGULATOR_INVESTOR_ATTESTATION_ROUTE',
    });
  }
);

const WILSY_R68X_REGULATOR_DOSSIER_CHAIN_FINAL_ATTESTATION_ROUTE_CONTRACT =
  'R68X-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-FINAL-REGULATOR-INVESTOR-ATTESTATION-AUTHORITY';

/**
 * R68W JSON-only regulator dossier chain evidence bundle index verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await verifyLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/verify/latest',
      routeContract:
        WILSY_R68W_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceEvidenceBundleIndexVerificationReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest',
      sourceEvidenceBundleIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
      sourceEvidenceBundleIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
      safeRouteAlias:
        'R68W_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R68W_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R68W-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

/**
 * R68V JSON-only regulator dossier chain evidence bundle index verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload =
      await buildLeadSearchRegulatorDossierChainEvidenceBundleIndexVerificationReceipt({
        tenantId,
        ledgerId: req.query.ledgerRoot || 'latest',
        limit: req.query.limit || 25,
        operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
      });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verification-receipt/latest',
      routeContract:
        WILSY_R68V_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceEvidenceBundleIndexVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
      sourceEvidenceBundleIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
      safeRouteAlias: 'R68V_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

const WILSY_R68V_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R68V-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFICATION-RECEIPT-AUTHORITY';

/**
 * R68U JSON-only regulator dossier chain evidence bundle index verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorDossierChainEvidenceBundleIndex({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/verify/latest',
      routeContract:
        WILSY_R68U_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIER_ROUTE_CONTRACT,
      sourceEvidenceBundleIndexRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
      sourceFinalityVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
      safeRouteAlias: 'R68U_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R68U_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_VERIFIER_ROUTE_CONTRACT =
  'R68U-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-VERIFIER-AUTHORITY';

/**
 * R68T JSON-only regulator dossier chain evidence bundle index.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await buildLeadSearchRegulatorDossierChainEvidenceBundleIndex({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/index/latest',
      routeContract: WILSY_R68T_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_ROUTE_CONTRACT,
      sourceFinalityVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
      safeRouteAlias: 'R68T_SAFE_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_ROUTE',
    });
  }
);

const WILSY_R68T_REGULATOR_DOSSIER_CHAIN_EVIDENCE_BUNDLE_INDEX_ROUTE_CONTRACT =
  'R68T-REGULATOR-DOSSIER-CHAIN-EVIDENCE-BUNDLE-INDEX-AUTHORITY';

/**
 * R68S JSON-only regulator dossier chain finality certificate verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorDossierChainFinalityCertificate({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/verify/latest',
      routeContract:
        WILSY_R68S_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT,
      sourceFinalityRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest',
      sourceVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
      sourceLedgerRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      safeRouteAlias: 'R68S_SAFE_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R68S_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_VERIFIER_ROUTE_CONTRACT =
  'R68S-REGULATOR-DOSSIER-CHAIN-FINALITY-CERTIFICATE-VERIFIER-AUTHORITY';

/**
 * R68R JSON-only regulator dossier chain verification finality certificate.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/finality-certificate/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await buildLeadSearchRegulatorDossierChainFinalityCertificate({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route: '/api/crm/command/search/regulator-evidence/dossier-chain/finality-certificate/latest',
      routeContract: WILSY_R68R_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_ROUTE_CONTRACT,
      sourceVerifierRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest',
      sourceReceiptRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
      sourceLedgerRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      safeRouteAlias: 'R68R_SAFE_DOSSIER_CHAIN_FINALITY_CERTIFICATE_ROUTE',
    });
  }
);

const WILSY_R68R_REGULATOR_DOSSIER_CHAIN_FINALITY_CERTIFICATE_ROUTE_CONTRACT =
  'R68R-REGULATOR-DOSSIER-CHAIN-VERIFICATION-FINALITY-CERTIFICATE-AUTHORITY';

const WILSY_R68Q_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT =
  'R68Q-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-VERIFIER-AUTHORITY';

const WILSY_R68P_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_ROUTE_CONTRACT =
  'R68P-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-RECEIPT-AUTHORITY';

const WILSY_R68O_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_ROUTE_CONTRACT =
  'R68O-REGULATOR-DOSSIER-CHAIN-LEDGER-VERIFICATION-AUTHORITY';

const WILSY_R68N_REGULATOR_DOSSIER_CHAIN_LEDGER_ROUTE_CONTRACT =
  'R68N-REGULATOR-DOSSIER-CHAIN-LEDGER-AUTHORITY';

/**
 * R68N JSON-only regulator dossier chain ledger.
 */
router.get('/search/regulator-evidence/dossier-chain/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  if (String(req.query.rootCheck || req.query.verification || '').toUpperCase() === 'R68O') {
    const payload = await verifyLeadSearchRegulatorDossierChainLedger({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route: '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      routeContract: WILSY_R68O_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_ROUTE_CONTRACT,
      safeRouteAlias: 'R68O_SAFE_EXISTING_LEDGER_ROUTE',
    });
  }

  const payload = await buildLeadSearchRegulatorDossierChainLedger({
    tenantId,
    limit: req.query.limit || 25,
  });

  return res.status(payload.ok ? 200 : 206).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/dossier-chain/latest',
    routeContract: WILSY_R68N_REGULATOR_DOSSIER_CHAIN_LEDGER_ROUTE_CONTRACT,
  });
});

/**
 * R68P JSON-only regulator dossier chain ledger verification receipt.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/verification-receipt/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await buildLeadSearchRegulatorDossierChainLedgerVerificationReceipt({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route: '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
      routeContract: WILSY_R68P_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_ROUTE_CONTRACT,
      sourceRoute: '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      safeRouteAlias: 'R68P_SAFE_EXISTING_LEDGER_VERIFICATION_RECEIPT_ROUTE',
    });
  }
);

/**
 * R68Q JSON-only regulator dossier chain ledger verification receipt verifier.
 */
router.get(
  '/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest',
  async (req, res) => {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await verifyLeadSearchRegulatorDossierChainLedgerVerificationReceipt({
      tenantId,
      ledgerId: req.query.ledgerRoot || 'latest',
      limit: req.query.limit || 25,
      operator: req.headers['x-wilsy-operator'] || req.user?.email || req.user?.id || 'SYSTEM',
    });

    return res.status(payload.ok ? 200 : 206).json({
      ...payload,
      route:
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/verify/latest',
      routeContract:
        WILSY_R68Q_REGULATOR_DOSSIER_CHAIN_LEDGER_VERIFICATION_RECEIPT_VERIFIER_ROUTE_CONTRACT,
      sourceRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/verification-receipt/latest',
      sourceLedgerRoute:
        '/api/crm/command/search/regulator-evidence/dossier-chain/latest?rootCheck=R68O',
      safeRouteAlias: 'R68Q_SAFE_EXISTING_LEDGER_VERIFICATION_RECEIPT_VERIFIER_ROUTE',
    });
  }
);

const WILSY_R68M_REGULATOR_DOSSIER_VERIFICATION_ROUTE_CONTRACT =
  'R68M-REGULATOR-DOSSIER-VERIFICATION-AUTHORITY';

/**
 * R68M recent regulator dossier verifications.
 */
router.get('/search/regulator-evidence/dossiers/verified/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorEvidenceDossierVerifications({
    tenantId,
    limit: req.query.limit || 5,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/dossiers/verified/latest',
    routeContract: WILSY_R68M_REGULATOR_DOSSIER_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68M verify regulator dossier by dossier hash, export receipt hash, export hash, or governance id.
 */
router.get('/search/regulator-evidence/dossier/verify/:dossierId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchRegulatorEvidenceDossier({
    tenantId,
    dossierId: req.params.dossierId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/dossier/verify/:dossierId',
    routeContract: WILSY_R68M_REGULATOR_DOSSIER_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68L_REGULATOR_EVIDENCE_DOSSIER_ROUTE_CONTRACT =
  'R68L-REGULATOR-EVIDENCE-DOSSIER-AUTHORITY';

/**
 * R68L recent regulator evidence dossiers.
 */
router.get('/search/regulator-evidence/dossiers/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorEvidenceDossiers({
    tenantId,
    limit: req.query.limit || 5,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/dossiers/latest',
    routeContract: WILSY_R68L_REGULATOR_EVIDENCE_DOSSIER_ROUTE_CONTRACT,
  });
});

/**
 * R68L build regulator evidence dossier by export receipt id/hash/export hash/governance id.
 */
router.get('/search/regulator-evidence/dossier/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await buildLeadSearchRegulatorEvidenceDossier({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/dossier/:receiptId',
    routeContract: WILSY_R68L_REGULATOR_EVIDENCE_DOSSIER_ROUTE_CONTRACT,
  });
});

const WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT =
  'R68K-REGULATOR-EXPORT-RECEIPT-VERIFICATION-AUTHORITY';

/**
 * R68K verified regulator export receipt ledger.
 */
router.get('/search/regulator-evidence/receipts/verified/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorExportReceiptVerifications({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/receipts/verified/latest',
    routeContract: WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68K verify regulator export receipt by id, exportReceiptHash, exportHash, or governance id.
 */
router.get('/search/regulator-evidence/receipt/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchRegulatorExportReceipt({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/receipt/:receiptId',
    routeContract: WILSY_R68K_REGULATOR_EXPORT_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT =
  'R68J-REGULATOR-EXPORT-RECEIPT-MATERIALIZATION';

/**
 * R68J recent regulator export receipts.
 */
router.get('/search/regulator-evidence/receipts/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorExportReceipts({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/receipts/latest',
    routeContract: WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT,
  });
});

/**
 * R68J materialize regulator export receipt from governance id or hash.
 */
router.post('/search/regulator-evidence/:governanceId/receipt', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await materializeLeadSearchRegulatorExportReceipt({
    tenantId,
    governanceId: req.params.governanceId,
  });

  return res.status(payload.ok ? 201 : 409).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/:governanceId/receipt',
    routeContract: WILSY_R68J_REGULATOR_EXPORT_RECEIPT_ROUTE_CONTRACT,
  });
});

const WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT =
  'R68I-REGULATOR-EVIDENCE-EXPORT-AUTHORITY';

/**
 * R68I recent Lead search regulator evidence bundles.
 */
router.get('/search/regulator-evidence/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchRegulatorEvidenceBundles({
    tenantId,
    limit: req.query.limit || 5,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/latest',
    routeContract: WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT,
  });
});

/**
 * R68I Lead search regulator evidence export by governance id or hash.
 */
router.get('/search/regulator-evidence/:governanceId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await exportLeadSearchRegulatorEvidenceBundle({
    tenantId,
    governanceId: req.params.governanceId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/regulator-evidence/:governanceId',
    routeContract: WILSY_R68I_REGULATOR_EVIDENCE_EXPORT_ROUTE_CONTRACT,
  });
});

const WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT =
  'R68H-GOVERNANCE-EVENT-VERIFICATION-AUTHORITY';

/**
 * R68H recent Lead search governance event ledger.
 */
router.get('/search/governance-events/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchGovernanceEvents({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/governance-events/latest',
    routeContract: WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68H Lead search governance event verification.
 */
router.get('/search/governance-event/:governanceId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchGovernanceEvent({
    tenantId,
    governanceId: req.params.governanceId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/governance-event/:governanceId',
    routeContract: WILSY_R68H_GOVERNANCE_EVENT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68G_SEARCH_GOVERNANCE_EVENT_ROUTE_CONTRACT =
  'R68G-SEARCH-GOVERNANCE-EVENT-MATERIALIZATION';

/**
 * R68G materialize governance event from verified Lead search evidence chain.
 */
router.post('/search/evidence-chain/:receiptId/govern', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await materializeLeadSearchGovernanceEvent({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 201 : 409).json({
    ...payload,
    route: '/api/crm/command/search/evidence-chain/:receiptId/govern',
    routeContract: WILSY_R68G_SEARCH_GOVERNANCE_EVENT_ROUTE_CONTRACT,
  });
});

const WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT = 'R68F-SEARCH-EVIDENCE-CHAIN-AUTHORITY';

/**
 * R68F recent Lead search evidence chains.
 */
router.get('/search/evidence-chains/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchEvidenceChains({
    tenantId,
    limit: req.query.limit || 5,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/evidence-chains/latest',
    routeContract: WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT,
  });
});

/**
 * R68F Lead search evidence chain verification.
 */
router.get('/search/evidence-chain/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchEvidenceChain({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 409).json({
    ...payload,
    route: '/api/crm/command/search/evidence-chain/:receiptId',
    routeContract: WILSY_R68F_SEARCH_EVIDENCE_CHAIN_ROUTE_CONTRACT,
  });
});

const WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT =
  'R68E-COMPLIANCE-RECEIPT-VERIFICATION-AUTHORITY';

/**
 * R68E recent Lead search compliance receipt ledger.
 */
router.get('/search/compliance-receipts/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchComplianceReceipts({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/compliance-receipts/latest',
    routeContract: WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68E Lead search compliance receipt verification.
 */
router.get('/search/compliance-receipt/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchComplianceReceipt({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/compliance-receipt/:receiptId',
    routeContract: WILSY_R68E_COMPLIANCE_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT =
  'R68C.1-SEARCH-RECEIPT-VERIFICATION-SAFE';

/**
 * R68C.1 recent Lead search receipt ledger.
 */
router.get('/search/receipts/latest', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await listLeadSearchTelemetryReceipts({
    tenantId,
    limit: req.query.limit || 10,
  });

  return res.status(200).json({
    ...payload,
    route: '/api/crm/command/search/receipts/latest',
    routeContract: WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

/**
 * R68C.1 Lead search receipt verification.
 */
router.get('/search/receipt/:receiptId', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const payload = await verifyLeadSearchTelemetryReceipt({
    tenantId,
    receiptId: req.params.receiptId,
  });

  return res.status(payload.ok ? 200 : 404).json({
    ...payload,
    route: '/api/crm/command/search/receipt/:receiptId',
    routeContract: WILSY_R68C_SEARCH_RECEIPT_VERIFICATION_ROUTE_CONTRACT,
  });
});

const WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT = 'R68B.1-SEARCH-TELEMETRY-BREAKER';

/**
 * R68B.1 controlled Lead search route.
 * This route intentionally shadows older /search handlers so search finality does not depend on telemetry persistence success.
 */
router.get('/search', async (req, res) => {
  const tenantId =
    String(
      req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
    ).trim() || 'MASTER';

  const operatorId = String(
    req.user?.email || req.user?.id || req.headers['x-wilsy-operator'] || 'SYSTEM'
  );

  const role = String(req.user?.role || req.headers['x-wilsy-role'] || 'UNKNOWN');

  try {
    const payload = await searchLeadOperatingRoom({
      tenantId,
      query: req.query.q || req.query.query || '',
      limit: req.query.limit || 12,
      role,
      operatorId,
    });

    return res.status(200).json({
      ...payload,
      routeVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
      telemetryRouteVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      telemetryBreakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
      routeContract: 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY',
      telemetryRouteContract: 'R68B-SEARCH-TELEMETRY-PERSISTENCE',
      telemetryBreakerContract: WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT,
    });
  } catch (error) {
    const generatedAt = new Date().toISOString();

    return res.status(200).json({
      ok: false,
      success: false,
      version: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
      telemetryBreakerVersion: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
      tenantId,
      query: String(req.query.q || req.query.query || ''),
      role,
      operatorId,
      route: '/api/crm/command/search',
      searchMode: 'LEAD_OPERATING_ROOM_BACKEND_AUTHORITY',
      sourceStatus: 'SEARCH_ENGINE_ISOLATED_FAILURE',
      total: 0,
      totalRecords: 0,
      liveSources: 0,
      searchableSources: 0,
      totalSources: 0,
      results: [],
      rows: [],
      registry: [],
      sourceGaps: [
        {
          key: 'search',
          modelName: 'LeadOperatingRoomSearch',
          reason: 'SEARCH_ENGINE_EXCEPTION_ISOLATED',
          errorName: error?.name || 'UnknownError',
          errorMessage: String(error?.message || 'Unknown search failure').slice(0, 220),
        },
      ],
      telemetryPersistence: {
        persisted: false,
        status: 'SEARCH_ENGINE_EXCEPTION_ISOLATED',
        modelName: 'CRMTelemetryEvent',
        errorName: error?.name || 'UnknownError',
        version: WILSY_CRM_SEARCH_TELEMETRY_BREAKER_VERSION,
        generatedAt,
      },
      telemetryPersisted: false,
      generatedAt,
      routeContract: 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY',
      telemetryRouteContract: 'R68B-SEARCH-TELEMETRY-PERSISTENCE',
      telemetryBreakerContract: WILSY_R68B1_SEARCH_TELEMETRY_BREAKER_ROUTE_CONTRACT,
    });
  }
});

const WILSY_R68A_BACKEND_LEAD_SEARCH_ROUTE_CONTRACT = 'R68A-BACKEND-LEAD-SEARCH-AUTHORITY';
const WILSY_R68B_SEARCH_TELEMETRY_ROUTE_CONTRACT = 'R68B-SEARCH-TELEMETRY-PERSISTENCE';

/**
 * R68A backend authority search.
 * This intentionally sits before legacy /search handlers so the Lead search bar receives
 * tenant-scoped rows, source telemetry, compliance bindings and root hash posture.
 */
router.get('/search', async (req, res, next) => {
  try {
    const tenantId =
      String(
        req.headers['x-tenant-id'] || req.query.tenantId || req.user?.tenantId || 'MASTER'
      ).trim() || 'MASTER';

    const payload = await searchLeadOperatingRoom({
      tenantId,
      query: req.query.q || req.query.query || '',
      limit: req.query.limit || 12,
      role: req.user?.role || req.headers['x-wilsy-role'] || 'UNKNOWN',
      operatorId: req.user?.email || req.user?.id || req.headers['x-wilsy-operator'] || 'SYSTEM',
    });

    res.status(200).json({
      ...payload,
      routeVersion: WILSY_CRM_LEAD_SEARCH_ENGINE_VERSION,
      telemetryRouteVersion: WILSY_CRM_SEARCH_TELEMETRY_PERSISTENCE_VERSION,
      telemetryRouteContract: WILSY_R68B_SEARCH_TELEMETRY_ROUTE_CONTRACT,
      routeContract: WILSY_R68A_BACKEND_LEAD_SEARCH_ROUTE_CONTRACT,
    });
  } catch (error) {
    next(error);
  }
});

const WILSY_CRM_COMMAND_FABRIC_VERSION = 'R62A-CRM-COMMAND-FABRIC-BACKEND-WIRING';

const CRM_MODEL_REGISTRY = Object.freeze([
  {
    key: 'leads',
    modelName: 'CRMLead',
    fields: ['name', 'firstName', 'lastName', 'email', 'company', 'stage', 'status', 'owner'],
  },
  {
    key: 'contacts',
    modelName: 'CRMContact',
    fields: ['name', 'firstName', 'lastName', 'email', 'phone', 'company', 'accountName', 'status'],
  },
  {
    key: 'accounts',
    modelName: 'CRMAccount',
    fields: ['name', 'accountName', 'company', 'industry', 'status', 'owner'],
  },
  {
    key: 'deals',
    modelName: 'CRMDeal',
    fields: ['name', 'dealName', 'accountName', 'company', 'stage', 'status', 'owner'],
  },
  {
    key: 'tasks',
    modelName: 'CRMTask',
    fields: ['subject', 'title', 'accountName', 'contactName', 'status', 'owner'],
  },
  {
    key: 'meetings',
    modelName: 'CRMMeeting',
    fields: ['subject', 'title', 'accountName', 'contactName', 'status', 'owner'],
  },
  {
    key: 'connectors',
    modelName: 'CRMConnector',
    fields: ['name', 'provider', 'status', 'sourceStatus'],
  },
  {
    key: 'telemetry',
    modelName: 'CRMTelemetryEvent',
    fields: ['eventType', 'source', 'status', 'tenantId'],
  },
  {
    key: 'compliance',
    modelName: 'CRMComplianceReceipt',
    fields: ['receiptType', 'status', 'tenantId', 'source'],
  },
  {
    key: 'governance',
    modelName: 'CRMGovernanceEvent',
    fields: ['eventType', 'status', 'tenantId', 'source'],
  },
  {
    key: 'genericRecords',
    modelName: 'CrmRecord',
    fields: ['name', 'title', 'email', 'company', 'accountName', 'module', 'type', 'status'],
  },
]);

/**
 * @function escapeWilsyCrmRegex
 * @description Escapes user search input before building a Mongo regular expression.
 * @param {string} value - User supplied search value.
 * @returns {string} Regex-safe string.
 * @collaboration Prevents CRM command search from turning operator text into unsafe regex syntax.
 */
function escapeWilsyCrmRegex(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * @function getWilsyCrmTenantId
 * @description Resolves tenant scope from request headers, body or query params.
 * @param {object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Keeps all CRM command fabric reads tenant-scoped.
 */
function getWilsyCrmTenantId(req) {
  return (
    String(
      req.headers['x-tenant-id'] ||
        req.headers['x-wilsy-tenant-id'] ||
        req.body?.tenantId ||
        req.query?.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function getWilsyCrmModel
 * @description Resolves a Mongoose model when it is registered in the runtime.
 * @param {string} modelName - Mongoose model name.
 * @returns {object|null} Mongoose model or null.
 * @collaboration Allows the command fabric to report source gaps instead of fabricating data.
 */
function getWilsyCrmModel(modelName) {
  return mongoose.models?.[modelName] || null;
}

/**
 * @function buildWilsyCrmTenantFilter
 * @description Builds a tolerant tenant filter for CRM collections with different tenant field names.
 * @param {string} tenantId - Tenant id.
 * @returns {object} Mongo query filter.
 * @collaboration Supports current and legacy CRM model schemas without cross-tenant leakage.
 */
function buildWilsyCrmTenantFilter(tenantId) {
  return {
    $or: [{ tenantId }, { 'tenant.id': tenantId }, { tenant: tenantId }, { tenantKey: tenantId }],
  };
}

/**
 * @function buildWilsyCrmSearchFilter
 * @description Builds a tenant-scoped search filter for a CRM registry entry.
 * @param {object} registryEntry - CRM model registry entry.
 * @param {string} tenantId - Tenant id.
 * @param {string} query - Search text.
 * @returns {object} Mongo query filter.
 * @collaboration Powers top-rail CRM search from real backend records.
 */
function buildWilsyCrmSearchFilter(registryEntry, tenantId, query) {
  const tenantFilter = buildWilsyCrmTenantFilter(tenantId);
  const cleanQuery = String(query || '').trim();

  if (!cleanQuery) {
    return tenantFilter;
  }

  const regex = new RegExp(escapeWilsyCrmRegex(cleanQuery), 'i');
  const searchClauses = registryEntry.fields.map((field) => ({ [field]: regex }));

  return {
    $and: [tenantFilter, { $or: searchClauses }],
  };
}

/**
 * @function normalizeWilsyCrmRecord
 * @description Converts a Mongo document into a compact CRM command result.
 * @param {object} record - Raw Mongo record.
 * @param {object} registryEntry - CRM model registry entry.
 * @returns {object} Normalized result.
 * @collaboration Keeps browser search results consistent while preserving backend source truth.
 */
function normalizeWilsyCrmRecord(record, registryEntry) {
  const source = record || {};
  const id = String(
    source._id || source.id || source.externalId || `${registryEntry.key}-${Date.now()}`
  );
  const primary =
    source.name ||
    source.title ||
    source.subject ||
    source.dealName ||
    source.accountName ||
    source.company ||
    source.email ||
    'SOURCE VALUE REQUIRED';

  const secondary =
    source.company ||
    source.accountName ||
    source.email ||
    source.status ||
    source.stage ||
    source.sourceStatus ||
    registryEntry.key;

  return {
    id,
    module: registryEntry.key,
    modelName: registryEntry.modelName,
    primary,
    secondary,
    status: source.status || source.stage || source.sourceStatus || 'SOURCE_LIVE',
    sourceStatus: source.sourceStatus || 'SOURCE_LIVE',
    updatedAt: source.updatedAt || source.createdAt || null,
  };
}

/**
 * @function buildWilsyCrmCommandRootHash
 * @description Builds a deterministic hash for CRM command responses.
 * @param {object} packet - Response packet.
 * @returns {string} SHA-256 hash.
 * @collaboration Gives Live Sync and Search a compact evidence fingerprint.
 */
function buildWilsyCrmCommandRootHash(packet) {
  return crypto.createHash('sha256').update(JSON.stringify(packet)).digest('hex');
}

/**
 * @function queryWilsyCrmRegistryEntry
 * @description Reads one CRM model for search/sync without fabricating missing rows.
 * @param {object} registryEntry - CRM model registry entry.
 * @param {string} tenantId - Tenant id.
 * @param {string} query - Search query.
 * @param {number} limit - Result limit.
 * @returns {Promise<object>} Query result packet.
 * @collaboration Keeps CRM command search model-aware and source-gap aware.
 */
async function queryWilsyCrmRegistryEntry(registryEntry, tenantId, query, limit) {
  const Model = getWilsyCrmModel(registryEntry.modelName);

  if (!Model) {
    return {
      key: registryEntry.key,
      modelName: registryEntry.modelName,
      connected: false,
      count: 0,
      results: [],
      sourceGap: `${registryEntry.modelName} model not registered`,
    };
  }

  const filter = buildWilsyCrmSearchFilter(registryEntry, tenantId, query);
  const safeLimit = Math.max(1, Math.min(Number(limit) || 8, 25));

  const [count, rows] = await Promise.all([
    Model.countDocuments(filter).catch(() => 0),
    Model.find(filter)
      .sort({ updatedAt: -1, createdAt: -1, _id: -1 })
      .limit(safeLimit)
      .lean()
      .catch(() => []),
  ]);

  return {
    key: registryEntry.key,
    modelName: registryEntry.modelName,
    connected: true,
    count,
    results: rows.map((row) => normalizeWilsyCrmRecord(row, registryEntry)),
    sourceGap: null,
  };
}

/**
 * @function handleWilsyCrmCommandSearch
 * @description Handles live CRM command search.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Connects the top rail search to backend CRM source truth.
 */
async function handleWilsyCrmCommandSearch(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const query = String(req.query.q || req.query.query || '').trim();
    const limit = Math.max(1, Math.min(Number(req.query.limit) || 8, 25));

    const registryResults = await Promise.all(
      CRM_MODEL_REGISTRY.map((entry) => queryWilsyCrmRegistryEntry(entry, tenantId, query, limit))
    );

    const sourceGaps = registryResults
      .filter((item) => item.sourceGap)
      .map((item) => item.sourceGap);

    const results = registryResults.flatMap((item) => item.results).slice(0, limit);

    const packet = {
      ok: true,
      version: WILSY_CRM_COMMAND_FABRIC_VERSION,
      tenantId,
      query,
      route: '/api/crm/command/search',
      sourceStatus: sourceGaps.length ? 'SOURCE_DEGRADED' : 'SOURCE_LIVE',
      total: results.length,
      results,
      registry: registryResults.map((item) => ({
        key: item.key,
        modelName: item.modelName,
        connected: item.connected,
        count: item.count,
      })),
      sourceGaps,
      generatedAt: new Date().toISOString(),
    };

    const rootHash = buildWilsyCrmCommandRootHash(packet);

    res.json({
      ...packet,
      rootHash,
      rootHashShort: rootHash.slice(0, 12),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyCrmCommandSync
 * @description Handles live CRM command sync.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Hydrates CRM Live Sync from registered backend models and source gaps.
 */
async function handleWilsyCrmCommandSync(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const reason = req.body?.reason || 'CRM_LIVE_SYNC';
    const activeModule = req.body?.activeModule || 'leads';

    const registryResults = await Promise.all(
      CRM_MODEL_REGISTRY.map((entry) => queryWilsyCrmRegistryEntry(entry, tenantId, '', 3))
    );

    const connected = registryResults.filter((item) => item.connected);
    const sourceGaps = registryResults
      .filter((item) => item.sourceGap)
      .map((item) => item.sourceGap);

    const totalRecords = registryResults.reduce((sum, item) => sum + Number(item.count || 0), 0);

    const packet = {
      ok: true,
      version: WILSY_CRM_COMMAND_FABRIC_VERSION,
      tenantId,
      reason,
      activeModule,
      route: '/api/crm/command/sync',
      sourceStatus: sourceGaps.length ? 'SOURCE_DEGRADED' : 'SOURCE_LIVE',
      liveSources: connected.length,
      totalSources: CRM_MODEL_REGISTRY.length,
      totalRecords,
      registry: registryResults.map((item) => ({
        key: item.key,
        modelName: item.modelName,
        connected: item.connected,
        count: item.count,
        sourceStatus: item.connected ? 'SOURCE_LIVE' : 'SOURCE_REQUIRED',
      })),
      sourceGaps,
      generatedAt: new Date().toISOString(),
    };

    const rootHash = buildWilsyCrmCommandRootHash(packet);

    res.json({
      ...packet,
      rootHash,
      rootHashShort: rootHash.slice(0, 12),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyCrmCommandLeadCreate
 * @description Creates a CRM lead only when a real backend model is registered and valid source payload is provided.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Gives Add Lead a production backend path without creating fake rows from an empty click.
 */
async function handleWilsyCrmCommandLeadCreate(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const payload = req.body?.lead || req.body || {};
    const hasSourcePayload = Boolean(
      payload.name || payload.email || payload.company || payload.accountName
    );

    if (!hasSourcePayload) {
      res.status(400).json({
        ok: false,
        sourceStatus: 'SOURCE_REQUIRED',
        message: 'Lead source payload required before backend creation.',
        tenantId,
      });
      return;
    }

    const LeadModel = getWilsyCrmModel('CRMLead');
    const GenericModel = getWilsyCrmModel('CrmRecord');
    const Model = LeadModel || GenericModel;

    if (!Model) {
      res.status(503).json({
        ok: false,
        sourceStatus: 'SOURCE_REQUIRED',
        message: 'No CRM lead model is registered in this runtime.',
        tenantId,
      });
      return;
    }

    const document = await Model.create({
      ...payload,
      tenantId,
      module: payload.module || 'leads',
      type: payload.type || 'lead',
      sourceSystem: payload.sourceSystem || 'WILSY_OS_CRM_COMMAND_FABRIC',
      sourceStatus: payload.sourceStatus || 'SOURCE_LIVE',
      createdAt: payload.createdAt || new Date(),
      updatedAt: new Date(),
    });

    const normalized = normalizeWilsyCrmRecord(document.toObject ? document.toObject() : document, {
      key: 'leads',
      modelName: LeadModel ? 'CRMLead' : 'CrmRecord',
    });

    res.status(201).json({
      ok: true,
      tenantId,
      sourceStatus: 'SOURCE_LIVE',
      record: normalized,
      generatedAt: new Date().toISOString(),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function resolveWilsyCrmContactCreatePayload
 * @description Normalizes real CRM Contact command payloads without creating synthetic records.
 * @param {object} req - Express request.
 * @returns {object} Normalized contact payload.
 * @collaboration Contact save route, DB-backed CRM command fabric, POPIA-safe relationship records.
 */
function resolveWilsyCrmContactCreatePayload(req = {}) {
  const body = req.body || {};
  const payload = body.contact || body.record || body;

  return {
    ...payload,
    tenantId: getWilsyCrmTenantId(req),
    name:
      payload.name ||
      payload.contactName ||
      payload.fullName ||
      [payload.firstName, payload.lastName].filter(Boolean).join(' ') ||
      '',
    email: payload.email || payload.primaryEmail || payload.contactEmail || '',
    phone: payload.phone || payload.mobile || payload.mobileNumber || payload.workPhone || '',
    accountName:
      payload.accountName ||
      payload.company ||
      payload.companyName ||
      payload.organization ||
      payload.account?.name ||
      '',
    source:
      payload.source ||
      payload.sourceSystem ||
      payload.connector ||
      payload.origin ||
      'CRM_COMMAND',
    status: payload.status || payload.contactStatus || payload.lifecycleStage || 'ACTIVE',
    owner:
      payload.owner ||
      payload.ownerName ||
      payload.assignedTo ||
      req.user?.email ||
      req.user?.id ||
      req.headers['x-wilsy-operator'] ||
      'SYSTEM',
    createdBy: payload.createdBy || req.user?.id || req.user?.email || 'SYSTEM',
    updatedBy: payload.updatedBy || req.user?.id || req.user?.email || 'SYSTEM',
  };
}

/**
 * @function hasWilsyCrmContactSourcePayload
 * @description Confirms a Contact create command contains real relationship data.
 * @param {object} payload - Contact payload.
 * @returns {boolean} True when payload contains real contact evidence.
 * @collaboration Prevents empty clicks from becoming fake CRM Contact rows.
 */
function hasWilsyCrmContactSourcePayload(payload = {}) {
  return Boolean(
    payload.name ||
    payload.email ||
    payload.phone ||
    payload.accountName ||
    payload.company ||
    payload.companyName
  );
}

/**
 * @function handleWilsyCrmCommandContactCreate
 * @description Creates a CRM contact only when the backend CRMContact model is registered and a real payload is supplied.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Gives Contacts the same DB-backed command save authority as Leads without fake rows.
 */
async function handleWilsyCrmCommandContactCreate(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const ContactModel = getWilsyCrmModel('CRMContact');

    if (!ContactModel) {
      res.status(503).json({
        ok: false,
        route: '/api/crm/command/contacts',
        tenantId,
        sourceStatus: 'MODEL_NOT_REGISTERED',
        modelName: 'CRMContact',
        message: 'CRMContact model is not registered in the active backend runtime.',
      });
      return;
    }

    const payload = resolveWilsyCrmContactCreatePayload(req);

    if (!hasWilsyCrmContactSourcePayload(payload)) {
      res.status(422).json({
        ok: false,
        route: '/api/crm/command/contacts',
        tenantId,
        sourceStatus: 'SOURCE_PAYLOAD_REQUIRED',
        message:
          'Contact create requires name, email, phone, accountName, company, or companyName.',
      });
      return;
    }

    const contact = await ContactModel.create({
      ...payload,
      tenantId,
    });

    res.status(201).json({
      ok: true,
      route: '/api/crm/command/contacts',
      tenantId,
      sourceStatus: 'DB_PERSISTED',
      modelName: 'CRMContact',
      contact,
      record: contact,
      generatedAt: new Date().toISOString(),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyCrmCommandStatus
 * @description Returns CRM command fabric route posture.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {void} Response completion.
 * @collaboration Gives health checks a cheap route contract before live sync/search.
 */
function handleWilsyCrmCommandStatus(req, res) {
  const tenantId = getWilsyCrmTenantId(req);
  const registeredModels = CRM_MODEL_REGISTRY.filter((entry) =>
    Boolean(getWilsyCrmModel(entry.modelName))
  ).map((entry) => entry.modelName);

  res.json({
    ok: true,
    version: WILSY_CRM_COMMAND_FABRIC_VERSION,
    tenantId,
    route: '/api/crm/command/status',
    registeredModels,
    totalModels: CRM_MODEL_REGISTRY.length,
    generatedAt: new Date().toISOString(),
  });
}

const WILSY_R91K87_ADDRESS_PROVIDER_VERSION = 'R91K87-LIVE-ADDRESS-PROVIDER-COMMAND';

/**
 * @function normalizeWilsyR91K87AddressText
 * @description Normalizes address provider input and provider output values.
 * @param {unknown} value - Candidate text.
 * @returns {string} Normalized text.
 * @collaboration Address provider proxy, CRM Create Lead command, tenant-safe address capture.
 */
function normalizeWilsyR91K87AddressText(value = '') {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function resolveWilsyR91K87AddressCountry
 * @description Resolves an address search country bias without exposing provider keys.
 * @param {object} req - Express request.
 * @returns {object} Country bias packet.
 * @collaboration Supports South Africa-first CRM capture while allowing tenant supplied country hints.
 */
function resolveWilsyR91K87AddressCountry(req = {}) {
  const rawCountry = normalizeWilsyR91K87AddressText(
    req.query?.country ||
      req.query?.countryCode ||
      req.body?.country ||
      req.body?.countryCode ||
      req.body?.addressCountry ||
      req.headers?.['x-wilsy-address-country'] ||
      'ZA'
  );
  const upper = rawCountry.toUpperCase();

  if (upper === 'SOUTH AFRICA' || upper === 'ZAF') {
    return { iso2: 'ZA', iso3: 'ZAF', label: 'South Africa' };
  }

  return {
    iso2: upper.length === 2 ? upper : 'ZA',
    iso3: upper.length === 3 ? upper : 'ZAF',
    label: rawCountry || 'South Africa',
  };
}

/**
 * @function resolveWilsyR91K87ProviderPolicy
 * @description Resolves the active address provider from server environment and available keys.
 * @returns {object} Provider policy.
 * @collaboration Keeps Google, Mapbox, Loqate, HERE, and Nominatim access behind Wilsy backend authority.
 */
function resolveWilsyR91K87ProviderPolicy() {
  const requested = normalizeWilsyR91K87AddressText(
    process.env.WILSY_ADDRESS_PROVIDER || ''
  ).toUpperCase();
  const keys = {
    google: process.env.GOOGLE_PLACES_API_KEY || process.env.GOOGLE_MAPS_API_KEY || '',
    mapbox: process.env.MAPBOX_ACCESS_TOKEN || '',
    loqate: process.env.LOQATE_API_KEY || process.env.LOQATE_KEY || '',
    here: process.env.HERE_API_KEY || '',
  };

  if (requested === 'GOOGLE' && keys.google) return { provider: 'GOOGLE_PLACES', key: keys.google };
  if (requested === 'MAPBOX' && keys.mapbox)
    return { provider: 'MAPBOX_SEARCH_BOX', key: keys.mapbox };
  if (requested === 'LOQATE' && keys.loqate)
    return { provider: 'LOQATE_ADDRESS_CAPTURE', key: keys.loqate };
  if (requested === 'HERE' && keys.here) return { provider: 'HERE_AUTOCOMPLETE', key: keys.here };
  if (requested === 'NOMINATIM' || requested === 'OPENSTREETMAP')
    return { provider: 'OPENSTREETMAP_NOMINATIM', key: '' };

  if (keys.google) return { provider: 'GOOGLE_PLACES', key: keys.google };
  if (keys.mapbox) return { provider: 'MAPBOX_SEARCH_BOX', key: keys.mapbox };
  if (keys.loqate) return { provider: 'LOQATE_ADDRESS_CAPTURE', key: keys.loqate };
  if (keys.here) return { provider: 'HERE_AUTOCOMPLETE', key: keys.here };

  return { provider: 'OPENSTREETMAP_NOMINATIM', key: '' };
}

/**
 * @function fetchWilsyR91K87Json
 * @description Fetches provider JSON with timeout governance.
 * @param {string} url - Provider URL.
 * @param {object} options - Fetch options.
 * @returns {Promise<object>} Provider JSON.
 * @collaboration Gives address autocomplete live provider reach without adding frontend secrets.
 */
async function fetchWilsyR91K87Json(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 6500);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      return {
        ok: false,
        providerStatus: `HTTP_${response.status}`,
        body,
      };
    }

    return {
      ok: true,
      providerStatus: 'PROVIDER_RESPONSE_OK',
      body,
    };
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * @function buildWilsyR91K87AddressSuggestion
 * @description Builds one Wilsy normalized address suggestion.
 * @param {object} params - Suggestion parameters.
 * @returns {object} Normalized suggestion.
 * @collaboration Aligns provider payloads with CRM address fields, territory posture, and evidence metadata.
 */
function buildWilsyR91K87AddressSuggestion(params = {}) {
  const street = normalizeWilsyR91K87AddressText(params.street || params.label || '');
  const city = normalizeWilsyR91K87AddressText(params.city || '');
  const state = normalizeWilsyR91K87AddressText(params.state || '');
  const postalCode = normalizeWilsyR91K87AddressText(params.postalCode || '');
  const country = normalizeWilsyR91K87AddressText(params.country || 'South Africa');
  const formattedAddress = normalizeWilsyR91K87AddressText(
    params.formattedAddress || [street, city, state, postalCode, country].filter(Boolean).join(', ')
  );
  const confidence = Math.max(1, Math.min(99, Number(params.confidence || 72)));

  return {
    id: normalizeWilsyR91K87AddressText(params.id || params.providerId || formattedAddress),
    label: normalizeWilsyR91K87AddressText(params.label || formattedAddress),
    street,
    city,
    state,
    postalCode,
    country,
    latitude: params.latitude || '',
    longitude: params.longitude || '',
    formattedAddress,
    provider: normalizeWilsyR91K87AddressText(params.provider || 'WILSY_ADDRESS_PROVIDER'),
    providerId: normalizeWilsyR91K87AddressText(params.providerId || params.id || ''),
    confidence,
    verificationStatus: normalizeWilsyR91K87AddressText(
      params.verificationStatus || 'PROVIDER_SUGGESTED'
    ),
    territory: normalizeWilsyR91K87AddressText(
      params.territory || [city, state, country].filter(Boolean).join(' · ')
    ),
    duplicatePosture: normalizeWilsyR91K87AddressText(
      params.duplicatePosture || 'Duplicate check queued on save'
    ),
    receipt: normalizeWilsyR91K87AddressText(
      params.receipt || `ADDR-R91K87-${confidence}-${formattedAddress.length}`
    ),
    raw: params.raw || null,
  };
}

/**
 * @function parseWilsyR91K87NominatimSuggestions
 * @description Converts OpenStreetMap Nominatim search results into Wilsy address suggestions.
 * @param {Array<object>} items - Provider results.
 * @returns {Array<object>} Suggestions.
 * @collaboration Gives Wilsy OS a real no-key live provider fallback for local development.
 */
function parseWilsyR91K87NominatimSuggestions(items = []) {
  return (Array.isArray(items) ? items : [])
    .slice(0, 7)
    .map((item, index) => {
      const address = item.address || {};
      const street = [
        address.house_number,
        address.road ||
          address.pedestrian ||
          address.footway ||
          address.neighbourhood ||
          address.suburb,
      ]
        .filter(Boolean)
        .join(' ');
      const city =
        address.city ||
        address.town ||
        address.village ||
        address.municipality ||
        address.suburb ||
        address.county ||
        '';
      const state = address.state || address.province || address.region || '';
      const confidence = Math.round(
        Math.min(94, Math.max(54, Number(item.importance || 0.5) * 100))
      );

      return buildWilsyR91K87AddressSuggestion({
        id: `nominatim-${item.place_id || index}`,
        providerId: String(item.place_id || ''),
        label: item.name || item.display_name || street,
        street: street || item.display_name || '',
        city,
        state,
        postalCode: address.postcode || '',
        country: address.country || 'South Africa',
        latitude: item.lat || '',
        longitude: item.lon || '',
        formattedAddress: item.display_name || '',
        provider: 'OPENSTREETMAP_NOMINATIM',
        confidence,
        verificationStatus: 'LIVE_PROVIDER_SUGGESTED',
        raw: item,
      });
    })
    .filter((item) => item.formattedAddress || item.street);
}

/**
 * @function requestWilsyR91K87NominatimSuggestions
 * @description Requests real address suggestions from OpenStreetMap Nominatim.
 * @param {string} query - Search query.
 * @param {object} country - Country bias.
 * @returns {Promise<Array<object>>} Suggestions.
 * @collaboration Local-dev real address lookup without browser keys or paid provider dependency.
 */
async function requestWilsyR91K87NominatimSuggestions(query = '', country = {}) {
  const url = new URL('https://nominatim.openstreetmap.org/search');
  url.searchParams.set('format', 'jsonv2');
  url.searchParams.set('addressdetails', '1');
  url.searchParams.set('limit', '7');
  url.searchParams.set('q', query);

  if (country.iso2) {
    url.searchParams.set('countrycodes', country.iso2.toLowerCase());
  }

  const result = await fetchWilsyR91K87Json(url.toString(), {
    headers: {
      Accept: 'application/json',
      'Accept-Language': 'en',
      'User-Agent': 'WilsyOS/2.1 CRM Address Command local-dev',
    },
  });

  return result.ok ? parseWilsyR91K87NominatimSuggestions(result.body) : [];
}

/**
 * @function requestWilsyR91K87GoogleSuggestions
 * @description Requests Google Places autocomplete suggestions when a backend key is configured.
 * @param {string} query - Search query.
 * @param {string} key - Server-side provider key.
 * @param {object} country - Country bias.
 * @returns {Promise<Array<object>>} Suggestions.
 * @collaboration Keeps Google Places access server-side and provider-neutral.
 */
async function requestWilsyR91K87GoogleSuggestions(query = '', key = '', country = {}) {
  const result = await fetchWilsyR91K87Json(
    'https://places.googleapis.com/v1/places:autocomplete',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': key,
        'X-Goog-FieldMask': 'suggestions.placePrediction.placeId,suggestions.placePrediction.text',
      },
      body: JSON.stringify({
        input: query,
        languageCode: 'en',
        regionCode: country.iso2 || 'ZA',
      }),
    }
  );

  const suggestions = result.body?.suggestions || [];

  return suggestions
    .map((entry, index) => {
      const prediction = entry.placePrediction || {};
      const text = prediction.text?.text || '';

      return buildWilsyR91K87AddressSuggestion({
        id: `google-${prediction.placeId || index}`,
        providerId: prediction.placeId || '',
        label: text,
        street: text,
        country: country.label || 'South Africa',
        formattedAddress: text,
        provider: 'GOOGLE_PLACES',
        confidence: 88,
        verificationStatus: 'GOOGLE_PLACE_PREDICTION',
        raw: prediction,
      });
    })
    .filter((item) => item.formattedAddress);
}

/**
 * @function requestWilsyR91K87MapboxSuggestions
 * @description Requests Mapbox Search Box suggestions when a backend token is configured.
 * @param {string} query - Search query.
 * @param {string} key - Server-side provider key.
 * @param {object} country - Country bias.
 * @returns {Promise<Array<object>>} Suggestions.
 * @collaboration Keeps Mapbox sessions backend-governed.
 */
async function requestWilsyR91K87MapboxSuggestions(query = '', key = '', country = {}) {
  const url = new URL('https://api.mapbox.com/search/searchbox/v1/suggest');
  url.searchParams.set('q', query);
  url.searchParams.set('access_token', key);
  url.searchParams.set('session_token', `wilsy-r91k87-${Date.now()}`);
  url.searchParams.set('limit', '7');
  url.searchParams.set('language', 'en');

  if (country.iso2) {
    url.searchParams.set('country', country.iso2);
  }

  const result = await fetchWilsyR91K87Json(url.toString(), {
    headers: { Accept: 'application/json' },
  });

  const suggestions = result.body?.suggestions || [];

  return suggestions
    .map((item, index) =>
      buildWilsyR91K87AddressSuggestion({
        id: `mapbox-${item.mapbox_id || index}`,
        providerId: item.mapbox_id || '',
        label: item.name || item.full_address || '',
        street: item.full_address || item.name || '',
        city: item.context?.place?.name || item.context?.locality?.name || '',
        state: item.context?.region?.name || '',
        postalCode: item.context?.postcode?.name || '',
        country: item.context?.country?.name || country.label || 'South Africa',
        formattedAddress:
          item.full_address || [item.name, item.place_formatted].filter(Boolean).join(', '),
        provider: 'MAPBOX_SEARCH_BOX',
        confidence: 86,
        verificationStatus: 'MAPBOX_SUGGESTED',
        raw: item,
      })
    )
    .filter((item) => item.formattedAddress);
}

/**
 * @function requestWilsyR91K87LoqateSuggestions
 * @description Requests Loqate Address Capture suggestions when a backend key is configured.
 * @param {string} query - Search query.
 * @param {string} key - Server-side provider key.
 * @param {object} country - Country bias.
 * @returns {Promise<Array<object>>} Suggestions.
 * @collaboration Keeps Loqate Find behind Wilsy backend provider policy.
 */
async function requestWilsyR91K87LoqateSuggestions(query = '', key = '', country = {}) {
  const url = new URL('https://api.addressy.com/Capture/Interactive/Find/v1.10/json3.ws');
  url.searchParams.set('Key', key);
  url.searchParams.set('Text', query);
  url.searchParams.set('Limit', '7');
  url.searchParams.set('Countries', country.iso3 || 'ZAF');

  const result = await fetchWilsyR91K87Json(url.toString(), {
    headers: { Accept: 'application/json' },
  });

  const items = result.body?.Items || [];

  return items
    .map((item, index) =>
      buildWilsyR91K87AddressSuggestion({
        id: `loqate-${item.Id || index}`,
        providerId: item.Id || '',
        label: item.Text || '',
        street: [item.Text, item.Description].filter(Boolean).join(', '),
        country: country.label || 'South Africa',
        formattedAddress: [item.Text, item.Description].filter(Boolean).join(', '),
        provider: 'LOQATE_ADDRESS_CAPTURE',
        confidence: item.Type === 'Address' ? 90 : 78,
        verificationStatus:
          item.Type === 'Address' ? 'LOQATE_ADDRESS_SUGGESTED' : 'LOQATE_CONTAINER_SUGGESTED',
        raw: item,
      })
    )
    .filter((item) => item.formattedAddress);
}

/**
 * @function requestWilsyR91K87HereSuggestions
 * @description Requests HERE autocomplete suggestions when a backend key is configured.
 * @param {string} query - Search query.
 * @param {string} key - Server-side provider key.
 * @param {object} country - Country bias.
 * @returns {Promise<Array<object>>} Suggestions.
 * @collaboration Keeps HERE geocoding and search credentials behind the CRM backend.
 */
async function requestWilsyR91K87HereSuggestions(query = '', key = '', country = {}) {
  const url = new URL('https://autocomplete.search.hereapi.com/v1/autocomplete');
  url.searchParams.set('q', query);
  url.searchParams.set('limit', '7');
  url.searchParams.set('apiKey', key);

  if (country.iso3) {
    url.searchParams.set('in', `countryCode:${country.iso3}`);
  }

  const result = await fetchWilsyR91K87Json(url.toString(), {
    headers: { Accept: 'application/json' },
  });

  const items = result.body?.items || [];

  return items
    .map((item, index) => {
      const address = item.address || {};

      return buildWilsyR91K87AddressSuggestion({
        id: `here-${item.id || index}`,
        providerId: item.id || '',
        label: item.title || '',
        street: address.label || item.title || '',
        city: address.city || address.district || '',
        state: address.state || address.county || '',
        postalCode: address.postalCode || '',
        country: address.countryName || country.label || 'South Africa',
        latitude: item.position?.lat || '',
        longitude: item.position?.lng || '',
        formattedAddress: address.label || item.title || '',
        provider: 'HERE_AUTOCOMPLETE',
        confidence: 86,
        verificationStatus: 'HERE_SUGGESTED',
        raw: item,
      });
    })
    .filter((item) => item.formattedAddress);
}

/**
 * @function requestWilsyR91K87ProviderSuggestions
 * @description Dispatches address suggestions to the configured backend provider.
 * @param {string} query - Address query.
 * @param {object} policy - Provider policy.
 * @param {object} country - Country bias.
 * @returns {Promise<Array<object>>} Suggestions.
 * @collaboration One sovereign provider gateway for Google, Mapbox, Loqate, HERE, and Nominatim.
 */
async function requestWilsyR91K87ProviderSuggestions(query = '', policy = {}, country = {}) {
  if (policy.provider === 'GOOGLE_PLACES' && policy.key) {
    return requestWilsyR91K87GoogleSuggestions(query, policy.key, country);
  }

  if (policy.provider === 'MAPBOX_SEARCH_BOX' && policy.key) {
    return requestWilsyR91K87MapboxSuggestions(query, policy.key, country);
  }

  if (policy.provider === 'LOQATE_ADDRESS_CAPTURE' && policy.key) {
    return requestWilsyR91K87LoqateSuggestions(query, policy.key, country);
  }

  if (policy.provider === 'HERE_AUTOCOMPLETE' && policy.key) {
    return requestWilsyR91K87HereSuggestions(query, policy.key, country);
  }

  return requestWilsyR91K87NominatimSuggestions(query, country);
}

/**
 * @function titleCaseWilsyR91K92AddressQuery
 * @description Converts address queries into provider-friendly title case.
 * @param {string} value - Address query.
 * @returns {string} Title-cased address query.
 * @collaboration Improves OpenStreetMap and provider matching without changing browser secrets.
 */
function titleCaseWilsyR91K92AddressQuery(value = '') {
  return normalizeWilsyR91K87AddressText(value)
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * @function buildWilsyR91K92AddressQueryVariants
 * @description Builds expanded address provider search variants when exact lookup returns empty.
 * @param {string} query - Original operator query.
 * @param {object} country - Country bias packet.
 * @returns {Array<string>} Provider search variants.
 * @collaboration Gives Create Lead real autocomplete resilience for partial streets, uppercase input, and house-number ambiguity.
 */
function buildWilsyR91K92AddressQueryVariants(query = '', country = {}) {
  const normalized = normalizeWilsyR91K87AddressText(query);
  const titleQuery = titleCaseWilsyR91K92AddressQuery(normalized);
  const countryLabel = normalizeWilsyR91K87AddressText(
    country.label === 'ZA' ? 'South Africa' : country.label || 'South Africa'
  );
  const withoutLeadingNumber = normalizeWilsyR91K87AddressText(
    titleQuery.replace(/^\d+[A-Za-z]?\s+/, '')
  );

  return [
    normalized,
    titleQuery,
    `${titleQuery}, ${countryLabel}`,
    withoutLeadingNumber,
    `${withoutLeadingNumber}, ${countryLabel}`,
    `${withoutLeadingNumber} Avenue, ${countryLabel}`,
    `${withoutLeadingNumber} Place, ${countryLabel}`,
    `${withoutLeadingNumber} Road, ${countryLabel}`,
    `${withoutLeadingNumber} Street, ${countryLabel}`,
    `${withoutLeadingNumber} Brewery, ${countryLabel}`,
  ].filter((value, index, list) => value && value.length >= 3 && list.indexOf(value) === index);
}

/**
 * @function dedupeWilsyR91K92AddressSuggestions
 * @description Deduplicates provider address suggestions while preserving ranking.
 * @param {Array<object>} suggestions - Address suggestions.
 * @returns {Array<object>} Deduplicated suggestions.
 * @collaboration Prevents repeated Old Castle variants from cluttering the Create Lead command rail.
 */
function dedupeWilsyR91K92AddressSuggestions(suggestions = []) {
  const seen = new Set();

  return (Array.isArray(suggestions) ? suggestions : []).filter((suggestion) => {
    const key = [
      suggestion.provider,
      suggestion.providerId,
      suggestion.formattedAddress,
      suggestion.latitude,
      suggestion.longitude,
    ]
      .filter(Boolean)
      .join('|')
      .toLowerCase();

    if (!key || seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });
}

/**
 * @function requestWilsyR91K92ProviderSuggestionsWithFallback
 * @description Requests address suggestions through the configured provider and expands empty Nominatim searches.
 * @param {string} query - Operator address query.
 * @param {object} policy - Provider policy.
 * @param {object} country - Country bias packet.
 * @returns {Promise<object>} Suggestions, variants, and fallback posture.
 * @collaboration Upgrades Create Lead from exact-query lookup to resilient autocomplete-grade provider search.
 */
async function requestWilsyR91K92ProviderSuggestionsWithFallback(
  query = '',
  policy = {},
  country = {}
) {
  const shouldExpand =
    policy.provider === 'OPENSTREETMAP_NOMINATIM' ||
    policy.provider === 'WILSY_ADDRESS_PROVIDER_PROXY' ||
    !policy.key;

  const variants = shouldExpand ? buildWilsyR91K92AddressQueryVariants(query, country) : [query];

  const merged = [];
  const usedVariants = [];

  for (const variant of variants.slice(0, shouldExpand ? 8 : 1)) {
    const batch = await requestWilsyR91K87ProviderSuggestions(variant, policy, country);
    usedVariants.push(variant);
    merged.push(...batch);

    if (dedupeWilsyR91K92AddressSuggestions(merged).length >= 7) {
      break;
    }
  }

  const suggestions = dedupeWilsyR91K92AddressSuggestions(merged).slice(0, 7);

  return {
    suggestions,
    variants: usedVariants,
    fallbackApplied: usedVariants.length > 1,
  };
}

/**
 * @function handleWilsyR91K87AddressSuggest
 * @description Returns live address suggestions through a server-side provider proxy.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Powers Create Lead address intelligence without exposing provider credentials to the browser.
 */
async function handleWilsyR91K87AddressSuggest(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const query = normalizeWilsyR91K87AddressText(
      req.query?.q ||
        req.query?.query ||
        req.body?.q ||
        req.body?.query ||
        req.body?.addressSearch ||
        ''
    );
    const country = resolveWilsyR91K87AddressCountry(req);
    const policy = resolveWilsyR91K87ProviderPolicy();

    if (query.length < 3) {
      res.status(200).json({
        ok: true,
        version: WILSY_R91K87_ADDRESS_PROVIDER_VERSION,
        tenantId,
        provider: policy.provider,
        sourceStatus: 'QUERY_TOO_SHORT',
        suggestions: [],
        message: 'Type at least three characters for live address search.',
        generatedAt: new Date().toISOString(),
      });
      return;
    }

    const addressSearchResult = await requestWilsyR91K92ProviderSuggestionsWithFallback(
      query,
      policy,
      country
    );
    const suggestions = addressSearchResult.suggestions;
    const packet = {
      ok: true,
      version: WILSY_R91K87_ADDRESS_PROVIDER_VERSION,
      tenantId,
      provider: policy.provider,
      sourceStatus: suggestions.length ? 'ADDRESS_PROVIDER_LIVE' : 'ADDRESS_PROVIDER_EMPTY',
      suggestions,
      count: suggestions.length,
      query,
      country,
      searchVariants: addressSearchResult.variants,
      fallbackApplied: addressSearchResult.fallbackApplied,
      message: suggestions.length
        ? 'Live address suggestions returned by backend provider proxy.'
        : 'No live provider suggestions returned. Keep manual fallback visible.',
      generatedAt: new Date().toISOString(),
    };
    const rootHash = buildWilsyCrmCommandRootHash(packet);

    res.status(200).json({
      ...packet,
      rootHash,
      rootHashShort: rootHash.slice(0, 12),
    });
  } catch (error) {
    next(error);
  }
}

/**
 * @function handleWilsyR91K87AddressResolve
 * @description Normalizes a selected address suggestion into CRM field payload shape.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {void} Response completion.
 * @collaboration Prepares provider-selected address packets for Create Lead persistence.
 */
function handleWilsyR91K87AddressResolve(req, res) {
  const tenantId = getWilsyCrmTenantId(req);
  const suggestion = req.body?.suggestion || req.body || {};
  const normalized = buildWilsyR91K87AddressSuggestion({
    ...suggestion,
    provider: suggestion.provider || 'WILSY_ADDRESS_PROVIDER_PROXY',
    verificationStatus: suggestion.verificationStatus || 'ADDRESS_SELECTED_FOR_CRM_CREATE',
  });

  res.status(200).json({
    ok: true,
    version: WILSY_R91K87_ADDRESS_PROVIDER_VERSION,
    tenantId,
    status: 'ADDRESS_RESOLVED',
    address: normalized,
    generatedAt: new Date().toISOString(),
  });
}

/**
 * @function handleWilsyR91K87AddressVerify
 * @description Returns current verification posture for an address packet.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {void} Response completion.
 * @collaboration Gives Create Lead a provider-neutral verification endpoint before paid validation providers are configured.
 */
function handleWilsyR91K87AddressVerify(req, res) {
  const tenantId = getWilsyCrmTenantId(req);
  const address = req.body?.address || req.body || {};
  const hasCoreAddress = Boolean(address.street || address.formattedAddress || address.label);

  res.status(200).json({
    ok: true,
    version: WILSY_R91K87_ADDRESS_PROVIDER_VERSION,
    tenantId,
    status: hasCoreAddress ? 'ADDRESS_VERIFICATION_READY' : 'ADDRESS_REQUIRED',
    verificationStatus: hasCoreAddress ? 'PROVIDER_OR_MANUAL_REVIEW_READY' : 'ADDRESS_REQUIRED',
    confidence: hasCoreAddress ? Number(address.confidence || 70) : 0,
    address,
    generatedAt: new Date().toISOString(),
  });
}

router.get('/address/suggest', handleWilsyR91K87AddressSuggest);
router.post('/address/suggest', handleWilsyR91K87AddressSuggest);
router.post('/address/resolve', handleWilsyR91K87AddressResolve);
router.post('/address/verify', handleWilsyR91K87AddressVerify);

router.get('/status', handleWilsyCrmCommandStatus);
router.get('/search', handleWilsyCrmCommandSearch);
router.post('/sync', handleWilsyCrmCommandSync);
router.post('/leads', handleWilsyCrmCommandLeadCreate);
router.post('/contacts', handleWilsyCrmCommandContactCreate);

export default router;
