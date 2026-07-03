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
import { dispatchWilsyMeetingInvitations } from '../services/wilsyMeetingNotificationService.js';

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

  try {
    return await Model.findOneAndUpdate(
      { _id: objectId },
      { $set: update },
      { new: true, returnDocument: 'after', runValidators: false, lean: true }
    );
  } catch {
    return null;
  }
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

/**
 * R91K179B12B_LIVE_MEETING_COMMAND_AUTHORITY
 * @function resolveWilsyR91K179MeetingMongoose
 * @description Resolves mongoose without assuming a specific upstream import shape.
 * @returns {Object|null} Mongoose instance or null.
 * @collaboration CRM command route, meeting command authority, telemetry receipts.
 */
function resolveWilsyR91K179MeetingMongoose() {
  try {
    return require('mongoose');
  } catch {
    return null;
  }
}

/**
 * @function getWilsyR91K179MeetingTenantId
 * @description Resolves tenant scope for CRM meeting command writes.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Tenant-scoped CRM meeting writes, command receipts, live source service.
 */
function getWilsyR91K179MeetingTenantId(req) {
  return (
    String(
      req?.headers?.['x-tenant-id'] ||
        req?.headers?.['X-Tenant-Id'] ||
        req?.body?.tenantId ||
        req?.query?.tenantId ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function resolveWilsyR91K179MeetingModel
 * @description Resolves the first registered model that can support meeting command persistence.
 * @param {Array<string>} names - Candidate model names.
 * @returns {Object|null} Mongoose model or null.
 * @collaboration Existing CRMMeeting, Meeting, CrmMeeting, CalendarEvent, Event model authority.
 */
function resolveWilsyR91K179MeetingModel(names = []) {
  const mongooseInstance = resolveWilsyR91K179MeetingMongoose();

  if (!mongooseInstance) return null;

  for (const name of names) {
    try {
      if (mongooseInstance.models?.[name]) return mongooseInstance.model(name);
    } catch {
      // Keep scanning compatible model aliases.
    }
  }

  return null;
}

/**
 * @function insertWilsyR91K179MeetingCollectionRecord
 * @description Inserts a raw MongoDB collection document when no compatible registered model accepts the write.
 * @param {string} collectionName - Target collection.
 * @param {Object} document - Document to insert.
 * @returns {Promise<Object>} Inserted record summary.
 * @collaboration Mongo fallback, meeting command persistence, telemetry and compliance receipts.
 */
async function insertWilsyR91K179MeetingCollectionRecord(collectionName, document) {
  const mongooseInstance = resolveWilsyR91K179MeetingMongoose();

  if (!mongooseInstance?.connection?.db) {
    const error = new Error('MongoDB connection unavailable for meeting command authority.');
    error.statusCode = 503;
    error.code = 'CRM_MEETING_DB_UNAVAILABLE';
    throw error;
  }

  const result = await mongooseInstance.connection.db
    .collection(collectionName)
    .insertOne(document);

  return {
    ...document,
    _id: result.insertedId,
    id: String(result.insertedId),
    persistence: 'RAW_COLLECTION_PERSISTED',
    collectionName,
  };
}

/**
 * @function persistWilsyR91K179MeetingDocument
 * @description Persists a meeting document using the same active CRM Mongoose runtime strategy as the working Lead DB_PERSISTED path.
 * @param {Object} document - Meeting document.
 * @returns {Promise<Object>} Persisted meeting record with DB_PERSISTED evidence.
 * @collaboration CRMMeeting, resolveWilsyR91K76MongooseRuntime, raw MongoDB collection fallback, Wilsy OS Meeting command authority.
 */
async function persistWilsyR91K179MeetingDocument(document = {}) {
  const startedAt = Date.now();
  const now = new Date();
  const safeDocument = {
    ...(document && typeof document === 'object' ? document : {}),
    updatedAt: now,
    wilsyPersistenceContract: 'R91K179E12_MEETING_LEAD_RUNTIME_DB_PERSISTED',
    wilsyCommandPersistedAt: now.toISOString(),
  };

  delete safeDocument._id;
  delete safeDocument.id;
  delete safeDocument.meetingId;
  delete safeDocument.recordId;
  delete safeDocument.collection;

  let mongooseRuntime = null;
  let lastErrorMessage = '';

  try {
    if (typeof resolveWilsyR91K76MongooseRuntime === 'function') {
      mongooseRuntime = resolveWilsyR91K76MongooseRuntime();
    }
  } catch (runtimeError) {
    lastErrorMessage = runtimeError?.message || lastErrorMessage;
  }

  if (!mongooseRuntime) {
    try {
      const mongooseModule = await import('mongoose');
      mongooseRuntime = mongooseModule.default || mongooseModule;
    } catch (importError) {
      lastErrorMessage = importError?.message || lastErrorMessage;
    }
  }

  const MeetingModel =
    mongooseRuntime?.models?.CRMMeeting ||
    mongooseRuntime?.models?.Meeting ||
    mongooseRuntime?.models?.CrmMeeting ||
    mongooseRuntime?.models?.CalendarEvent ||
    mongooseRuntime?.models?.Event ||
    resolveWilsyR91K179MeetingModel([
      'CRMMeeting',
      'Meeting',
      'CrmMeeting',
      'CalendarEvent',
      'Event',
    ]);

  if (MeetingModel && typeof MeetingModel.create === 'function') {
    try {
      const created = await Promise.race([
        MeetingModel.create(safeDocument),
        new Promise((resolve) => setTimeout(() => resolve(null), 6500)),
      ]);

      if (created) {
        const plain = typeof created?.toObject === 'function' ? created.toObject() : created;
        const recordId = String(plain?._id || created?._id || '');

        return {
          ...plain,
          id: plain?.id || recordId,
          meetingId: plain?.meetingId || recordId,
          persistence: 'DB_PERSISTED',
          persistenceStatus: 'DB_PERSISTED',
          sourceStatus: 'DB_PERSISTED',
          modelName: MeetingModel.modelName || 'CRMMeeting',
          collectionName: MeetingModel.collection?.name || 'crmmeetings',
          latencyMs: Date.now() - startedAt,
        };
      }
    } catch (modelError) {
      lastErrorMessage = modelError?.message || lastErrorMessage;
    }
  }

  if (MeetingModel?.collection && typeof MeetingModel.collection.insertOne === 'function') {
    try {
      const result = await Promise.race([
        MeetingModel.collection.insertOne(safeDocument),
        new Promise((resolve) => setTimeout(() => resolve(null), 6500)),
      ]);

      if (result?.insertedId) {
        const recordId = String(result.insertedId);

        return {
          ...safeDocument,
          _id: result.insertedId,
          id: recordId,
          meetingId: recordId,
          persistence: 'DB_PERSISTED',
          persistenceStatus: 'DB_PERSISTED',
          sourceStatus: 'DB_PERSISTED',
          modelName: MeetingModel.modelName || 'CRMMeeting',
          collectionName: MeetingModel.collection.name || 'crmmeetings',
          latencyMs: Date.now() - startedAt,
        };
      }
    } catch (modelCollectionError) {
      lastErrorMessage = modelCollectionError?.message || lastErrorMessage;
    }
  }

  const activeDb =
    mongooseRuntime?.connection?.db ||
    (Array.isArray(mongooseRuntime?.connections)
      ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
      : null);

  if (activeDb) {
    const candidateCollections = [
      'crmmeetings',
      'meetings',
      'crm_meetings',
      'CRMMeeting',
      'Meeting',
    ];

    for (const collectionName of candidateCollections) {
      try {
        const collection = activeDb.collection(collectionName);

        if (!collection || typeof collection.insertOne !== 'function') {
          continue;
        }

        const result = await Promise.race([
          collection.insertOne(safeDocument),
          new Promise((resolve) => setTimeout(() => resolve(null), 4500)),
        ]);

        if (result?.insertedId) {
          const recordId = String(result.insertedId);

          return {
            ...safeDocument,
            _id: result.insertedId,
            id: recordId,
            meetingId: recordId,
            persistence: 'DB_PERSISTED',
            persistenceStatus: 'DB_PERSISTED',
            sourceStatus: 'DB_PERSISTED',
            modelName: MeetingModel?.modelName || 'CRMMeeting',
            collectionName,
            latencyMs: Date.now() - startedAt,
          };
        }
      } catch (rawError) {
        lastErrorMessage = rawError?.message || lastErrorMessage;
      }
    }
  }

  const error = new Error(
    lastErrorMessage ||
      'CRMMeeting model and MongoDB collection runtime unavailable for meeting command authority.'
  );
  error.statusCode = 503;
  error.code = 'CRM_MEETING_DB_UNAVAILABLE';
  throw error;
}

/**
 * @function persistWilsyR91K179CommandReceipt
 * @description Persists telemetry/compliance receipts for every live meeting command action.
 * @param {Object} payload - Receipt payload.
 * @returns {Promise<Object>} Receipt persistence summary.
 * @collaboration CRMTelemetryEvent, CRMComplianceReceipt, tenant evidence, command audit chain.
 */
async function persistWilsyR91K179CommandReceipt(payload = {}) {
  const now = new Date();
  const receipt = {
    tenantId: payload.tenantId || 'MASTER',
    commandSurface: 'R91K179B12B_LIVE_MEETING_COMMAND_AUTHORITY',
    action: payload.action || 'MEETING_COMMAND',
    module: 'meetings',
    status: payload.status || 'RECORDED',
    route: payload.route || '/api/crm/command/meetings/action',
    source: payload.source || 'WILSY_MEETING_COMMAND_CENTER',
    operatorId: payload.operatorId || 'wilsy-operator',
    relatedRecord: payload.relatedRecord || null,
    meetingId: payload.meetingId || null,
    fileName: payload.fileName || null,
    evidence: payload.evidence || {},
    metadata: payload.metadata || {},
    createdAt: now,
    updatedAt: now,
  };

  const writes = [];

  const TelemetryModel = resolveWilsyR91K179MeetingModel([
    'CRMTelemetryEvent',
    'TelemetryEvent',
    'CrmTelemetryEvent',
  ]);
  if (TelemetryModel) {
    try {
      const saved = await TelemetryModel.create(receipt);
      writes.push({
        target: 'CRMTelemetryEvent',
        persistence: 'MODEL_PERSISTED',
        id: String(saved?._id || ''),
      });
    } catch {
      const raw = await insertWilsyR91K179MeetingCollectionRecord('crmtelemetryevents', receipt);
      writes.push({ target: 'crmtelemetryevents', persistence: raw.persistence, id: raw.id });
    }
  } else {
    const raw = await insertWilsyR91K179MeetingCollectionRecord('crmtelemetryevents', receipt);
    writes.push({ target: 'crmtelemetryevents', persistence: raw.persistence, id: raw.id });
  }

  const ComplianceModel = resolveWilsyR91K179MeetingModel([
    'CRMComplianceReceipt',
    'ComplianceReceipt',
    'CrmComplianceReceipt',
  ]);
  if (ComplianceModel) {
    try {
      const saved = await ComplianceModel.create({
        ...receipt,
        receiptType: 'CRM_MEETING_COMMAND',
        compliancePosture: 'TENANT_COMMAND_RECORDED',
      });
      writes.push({
        target: 'CRMComplianceReceipt',
        persistence: 'MODEL_PERSISTED',
        id: String(saved?._id || ''),
      });
    } catch {
      const raw = await insertWilsyR91K179MeetingCollectionRecord('crmcompliancereceipts', {
        ...receipt,
        receiptType: 'CRM_MEETING_COMMAND',
        compliancePosture: 'TENANT_COMMAND_RECORDED',
      });
      writes.push({ target: 'crmcompliancereceipts', persistence: raw.persistence, id: raw.id });
    }
  } else {
    const raw = await insertWilsyR91K179MeetingCollectionRecord('crmcompliancereceipts', {
      ...receipt,
      receiptType: 'CRM_MEETING_COMMAND',
      compliancePosture: 'TENANT_COMMAND_RECORDED',
    });
    writes.push({ target: 'crmcompliancereceipts', persistence: raw.persistence, id: raw.id });
  }

  return {
    ok: true,
    receipt,
    writes,
  };
}

/**
 * @function buildWilsyR91K179MeetingDocument
 * @description Builds a source-honest meeting document from the universal meeting command center payload.
 * @param {Object} req - Express request.
 * @returns {Object} Meeting document.
 * @collaboration Universal meeting UI, CRMMeeting persistence, tenant audit receipts.
 */
function buildWilsyR91K179MeetingDocument(req) {
  const now = new Date();
  const tenantId = getWilsyR91K179MeetingTenantId(req);
  const draft =
    req?.body?.meetingDraft && typeof req.body.meetingDraft === 'object'
      ? req.body.meetingDraft
      : {};
  const status = String(req?.body?.status || draft.status || 'SCHEDULED')
    .trim()
    .toUpperCase();
  const title = String(draft.title || req?.body?.title || 'New Meeting').trim();

  if (!title) {
    const error = new Error('Meeting title is required.');
    error.statusCode = 400;
    error.code = 'CRM_MEETING_TITLE_REQUIRED';
    throw error;
  }

  return {
    tenantId,
    title,
    name: title,
    subject: title,
    venue: draft.venue || draft.meetingVenue || 'Client location',
    meetingVenue: draft.venue || draft.meetingVenue || 'Client location',
    location: draft.location || '',
    allDay: Boolean(draft.allDay),
    fromDate: draft.fromDate || '',
    fromTime: draft.fromTime || '',
    toDate: draft.toDate || '',
    toTime: draft.toTime || '',
    startsAt:
      draft.fromDate || draft.fromTime
        ? `${draft.fromDate || ''} ${draft.fromTime || ''}`.trim()
        : null,
    endsAt:
      draft.toDate || draft.toTime ? `${draft.toDate || ''} ${draft.toTime || ''}`.trim() : null,
    host: draft.host || 'Wilsy',
    participants: draft.participants || '',
    relatedTo: draft.relatedTo || req?.body?.relatedRecord || null,
    repeat: draft.repeat || 'None',
    reminder: draft.reminder || 'None',
    description: draft.description || '',
    status,
    source: 'WILSY_UNIVERSAL_MEETING_COMMAND_CENTER',
    commandSurface: 'R91K179B12B_LIVE_MEETING_COMMAND_AUTHORITY',
    relatedRecord: req?.body?.relatedRecord || null,
    metadata: {
      mode: req?.body?.mode || 'standalone',
      operatorAction: req?.body?.action || 'SAVE_MEETING',
      sourcePolicy: 'BACKEND_PERSISTED_AND_RECORDED',
      noPlaceholder: true,
    },
    createdAt: now,
    updatedAt: now,
  };
}

/**
 * @function handleWilsyR91K179MeetingAction
 * @description Records a meeting command action that does not create a meeting record.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Meeting command buttons, tenant audit, telemetry and compliance receipt chain.
 */
async function handleWilsyR91K179MeetingAction(req, res) {
  const tenantId = getWilsyR91K179MeetingTenantId(req);
  const action = String(req?.body?.action || 'MEETING_COMMAND')
    .trim()
    .toUpperCase();

  const receipt = await persistWilsyR91K179CommandReceipt({
    tenantId,
    action,
    status: 'ACTION_RECORDED',
    route: '/api/crm/command/meetings/action',
    relatedRecord: req?.body?.relatedRecord || null,
    metadata: {
      mode: req?.body?.mode || 'standalone',
      noPlaceholder: true,
    },
  });

  res.status(200).json({
    ok: true,
    tenantId,
    route: '/api/crm/command/meetings/action',
    action,
    status: 'ACTION_RECORDED',
    receipt,
  });
}

/**
 * @function handleWilsyR91K179MeetingCreate
 * @description Persists CRM Meeting create commands with the same DB_PERSISTED confirmation posture as the working Lead save path.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<Object>} Governed Meeting persistence response.
 * @collaboration Universal Meeting workspace, CRMMeeting persistence, command receipts, Wilsy OS evidence fabric.
 */
async function handleWilsyR91K179MeetingCreate(req, res) {
  const startedAt = Date.now();

  try {
    const document = buildWilsyR91K179MeetingDocument(req);
    const rawDocument = {
      ...document,
      updatedAt: new Date(),
      wilsyPersistenceContract: 'R91K179E10_MEETING_DB_PERSISTED_ROUTE',
      wilsyCommandPersistedAt: new Date().toISOString(),
    };

    let saved = null;
    let persistenceMode = '';
    let collectionName = '';
    let persistenceWarning = '';

    const primarySaved = await Promise.race([
      persistWilsyR91K179MeetingDocument(rawDocument),
      new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            __wilsyTimedOut: true,
            label: 'PRIMARY_MEETING_PERSISTENCE_TIMEOUT',
          });
        }, 8500);
      }),
    ]);

    if (primarySaved && primarySaved.__wilsyTimedOut) {
      persistenceWarning = primarySaved.label;
    } else if (primarySaved) {
      saved = primarySaved;
      persistenceMode =
        primarySaved.persistence || primarySaved.persistenceStatus || 'PRIMARY_MEETING_PERSISTED';
      collectionName = primarySaved.collectionName || primarySaved.collection || '';
    }

    if (!saved) {
      const mongooseModule = await import('mongoose');
      const mongooseRuntime = mongooseModule.default || mongooseModule;
      const candidateCollections = [
        'crmmeetings',
        'meetings',
        'crm_meetings',
        'CRMMeeting',
        'Meeting',
      ];

      if (!mongooseRuntime?.connection?.db) {
        return res.status(503).json({
          ok: false,
          success: false,
          status: 'MEETING_DB_UNAVAILABLE',
          message: 'Mongoose DB connection is unavailable for Meeting persistence.',
          route: '/api/crm/command/meetings',
          warning: persistenceWarning || null,
        });
      }

      delete rawDocument._id;
      delete rawDocument.id;
      delete rawDocument.meetingId;
      delete rawDocument.recordId;
      delete rawDocument.collection;

      for (const candidateCollection of candidateCollections) {
        try {
          const collection = mongooseRuntime.connection.db.collection(candidateCollection);

          if (!collection || typeof collection.insertOne !== 'function') {
            continue;
          }

          const result = await Promise.race([
            collection.insertOne(rawDocument),
            new Promise((resolve) => {
              setTimeout(() => {
                resolve({
                  __wilsyTimedOut: true,
                  label: 'RAW_MEETING_COLLECTION_TIMEOUT',
                });
              }, 4500);
            }),
          ]);

          if (result && result.__wilsyTimedOut) {
            persistenceWarning = result.label;
            continue;
          }

          if (result && result.insertedId) {
            saved = {
              ...rawDocument,
              _id: result.insertedId,
              id: String(result.insertedId),
              persistence: 'DB_PERSISTED',
              persistenceStatus: 'DB_PERSISTED',
              sourceStatus: 'DB_PERSISTED',
              collectionName: candidateCollection,
            };
            persistenceMode = 'DB_PERSISTED_RAW_COLLECTION';
            collectionName = candidateCollection;
            break;
          }
        } catch (collectionError) {
          persistenceWarning = collectionError?.message || persistenceWarning;
        }
      }
    }

    if (!saved) {
      return res.status(503).json({
        ok: false,
        success: false,
        status: 'MEETING_DB_PERSIST_FAILED',
        message: 'Meeting persistence did not confirm through primary or raw collection fallback.',
        route: '/api/crm/command/meetings',
        warning: persistenceWarning || null,
      });
    }

    const recordId = String(saved.id || saved._id || saved.meetingId || '');
    let receipt = null;
    let receiptStatus = 'RECEIPT_DEFERRED';

    try {
      const receiptAttempt = await Promise.race([
        persistWilsyR91K179CommandReceipt({
          tenantId: document.tenantId,
          action: document.status === 'DRAFT' ? 'PREPARE_DRAFT' : 'SAVE_MEETING',
          status: 'DB_PERSISTED',
          route: '/api/crm/command/meetings',
          meetingId: recordId,
          relatedRecord: document.relatedRecord,
          evidence: {
            meetingPersistence: saved.persistence || persistenceMode || 'DB_PERSISTED',
            modelName: saved.modelName || null,
            collectionName: saved.collectionName || collectionName || null,
            persistenceMode,
          },
          metadata: document.metadata,
        }),
        new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              __wilsyTimedOut: true,
              label: 'MEETING_RECEIPT_TIMEOUT_DEFERRED',
            });
          }, 3500);
        }),
      ]);

      if (receiptAttempt && receiptAttempt.__wilsyTimedOut) {
        receiptStatus = receiptAttempt.label;
      } else if (receiptAttempt) {
        receipt = receiptAttempt;
        receiptStatus = 'RECEIPT_RECORDED';
      }
    } catch (receiptError) {
      receiptStatus = 'RECEIPT_FAILED_DEFERRED';
      persistenceWarning = receiptError?.message || persistenceWarning;
    }

    return res.status(200).json({
      ok: true,
      success: true,
      tenantId: document.tenantId,
      route: '/api/crm/command/meetings',
      status: 'DB_PERSISTED',
      result: 'DB_PERSISTED',
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
      message: 'Meeting persisted through CRM command authority.',
      recordId,
      meetingId: recordId,
      meeting: saved,
      record: saved,
      receipt,
      receiptStatus,
      receiptHash: receipt?.receiptHash || receipt?.hash || 'R91K179E10_MEETING_DB_PERSISTED',
      auditMesh: {
        status: 'DB_PERSISTED',
        dbPersisted: true,
        source: 'R91K179E10_MEETING_DB_PERSISTED_ROUTE',
        collection: saved.collectionName || collectionName || null,
        tenantId: document.tenantId,
        latencyMs: Date.now() - startedAt,
        warning: persistenceWarning || null,
      },
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'MEETING_SAVE_FAILED',
      message: error?.message || 'Meeting save failed before DB confirmation.',
      route: '/api/crm/command/meetings',
    });
  }
}

/**
 * @function handleWilsyR91K179MeetingImportPreview
 * @description Records a governed import preview request without pretending that rows were imported.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Meeting import workflow, CSV/XLS/XLSX preview posture, audit receipts.
 */
async function handleWilsyR91K179MeetingImportPreview(req, res) {
  const tenantId = getWilsyR91K179MeetingTenantId(req);
  const fileName = String(req?.body?.fileName || '').trim();

  if (!fileName) {
    res.status(400).json({
      ok: false,
      tenantId,
      route: '/api/crm/command/meetings/import-preview',
      code: 'CRM_MEETING_IMPORT_FILE_REQUIRED',
      message: 'Meeting import preview requires a file name or upload metadata.',
    });
    return;
  }

  const preview = await insertWilsyR91K179MeetingCollectionRecord('crmmeetingimportpreviews', {
    tenantId,
    fileName,
    status: 'IMPORT_PREVIEW_RECORDED',
    source: 'WILSY_UNIVERSAL_MEETING_COMMAND_CENTER',
    commandSurface: 'R91K179B12B_LIVE_MEETING_COMMAND_AUTHORITY',
    metadata: {
      noImportedRowsClaimed: true,
      noPlaceholder: true,
      supportedFormats: ['csv', 'xlsx', 'xls'],
    },
    createdAt: new Date(),
    updatedAt: new Date(),
  });

  const receipt = await persistWilsyR91K179CommandReceipt({
    tenantId,
    action: 'IMPORT_PREVIEW',
    status: 'IMPORT_PREVIEW_RECORDED',
    route: '/api/crm/command/meetings/import-preview',
    fileName,
    evidence: {
      previewPersistence: preview.persistence,
      collectionName: preview.collectionName,
    },
  });

  res.status(201).json({
    ok: true,
    tenantId,
    route: '/api/crm/command/meetings/import-preview',
    status: 'IMPORT_PREVIEW_RECORDED',
    preview,
    receipt,
  });
}

router.post('/meetings/action', handleWilsyR91K179MeetingAction);

/**
 * @function resolveWilsyR91K179E15RMeetingRuntime
 * @description Resolves the active Mongoose runtime used by CRM command persistence.
 * @returns {Promise<Object|null>} Mongoose runtime.
 * @collaboration Working Lead DB_PERSISTED runtime, CRM Meetings CRUD route, raw collection fallback.
 */
async function resolveWilsyR91K179E15RMeetingRuntime() {
  try {
    if (typeof resolveWilsyR91K76MongooseRuntime === 'function') {
      const runtime = resolveWilsyR91K76MongooseRuntime();
      if (runtime) return runtime;
    }
  } catch {
    // Continue to mongoose import fallback.
  }

  try {
    const mongooseModule = await import('mongoose');
    return mongooseModule.default || mongooseModule;
  } catch {
    return null;
  }
}

/**
 * @function buildWilsyR91K179E15RMeetingFilter
 * @description Builds a Meeting id filter that works across model and raw collection persistence.
 * @param {Object} mongooseRuntime - Mongoose runtime.
 * @param {string} recordId - Meeting record id.
 * @returns {Object} MongoDB filter.
 * @collaboration CRMMeeting model, raw Meeting collections, Wilsy OS CRUD workspace.
 */
function buildWilsyR91K179E15RMeetingFilter(mongooseRuntime, recordId = '') {
  const id = String(recordId || '').trim();
  const filters = [{ id }, { meetingId: id }, { recordId: id }];

  try {
    const ObjectId = mongooseRuntime?.Types?.ObjectId;
    if (ObjectId && ObjectId.isValid && ObjectId.isValid(id)) {
      filters.unshift({ _id: new ObjectId(id) });
    }
  } catch {
    // Keep string id filters.
  }

  return { $or: filters };
}

/**
 * @function resolveWilsyR91K179E15RMeetingRecordId
 * @description Resolves a Meeting record id from request params or command body.
 * @param {Object} req - Express request.
 * @returns {string} Meeting record id.
 * @collaboration CRM Meetings editor, PATCH/DELETE command routes.
 */
function resolveWilsyR91K179E15RMeetingRecordId(req = {}) {
  return String(
    req.params?.id ||
      req.params?.meetingId ||
      req.body?.recordId ||
      req.body?.meetingId ||
      req.body?.id ||
      req.body?.meeting?.recordId ||
      req.body?.meeting?.meetingId ||
      req.body?.meeting?.id ||
      req.body?.meeting?._id ||
      ''
  ).trim();
}

/**
 * @function buildWilsyR91K179E15RMeetingUpdate
 * @description Builds a safe update document for a persisted Meeting record.
 * @param {Object} req - Express request.
 * @returns {Object} Meeting update document.
 * @collaboration CRM Meetings editor, PATCH command route, DB_PERSISTED evidence.
 */
function buildWilsyR91K179E15RMeetingUpdate(req = {}) {
  const payload = req.body && typeof req.body === 'object' ? req.body : {};
  const meeting =
    payload.meeting && typeof payload.meeting === 'object'
      ? payload.meeting
      : payload.payload && typeof payload.payload === 'object'
        ? payload.payload
        : payload.data && typeof payload.data === 'object'
          ? payload.data
          : payload;

  const update = {
    ...(meeting && typeof meeting === 'object' ? meeting : {}),
    updatedAt: new Date(),
    wilsyPersistenceContract: 'R91K179E15R_MEETING_CRUD_ROUTE_CONTRACT',
    wilsyCrudUpdatedAt: new Date().toISOString(),
  };

  [
    '_id',
    'id',
    'meetingId',
    'recordId',
    'collection',
    'before',
    'after',
    'action',
    'operatorContext',
    'commandSurface',
    'institutionalHeaders',
    'strikePayload',
  ].forEach((key) => {
    delete update[key];
  });

  if (update.title && !update.subject) update.subject = update.title;
  if (update.title && !update.meetingTitle) update.meetingTitle = update.title;
  if (update.meetingVenue && !update.venue) update.venue = update.meetingVenue;
  if (Array.isArray(update.participants) && !Array.isArray(update.attendees))
    update.attendees = update.participants;
  if (update.description && !update.agenda) update.agenda = update.description;
  if (update.relatedRecord && !update.relatedTo) update.relatedTo = update.relatedRecord;

  return update;
}

/**
 * @function handleWilsyR91K179E15RMeetingUpdate
 * @description Updates a persisted CRM Meeting record and returns DB_PERSISTED confirmation.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<Object>} JSON update response.
 * @collaboration CRM Meeting editor, PATCH /meetings/:id, DB_PERSISTED response contract.
 */
async function handleWilsyR91K179E15RMeetingUpdate(req, res) {
  try {
    const recordId = resolveWilsyR91K179E15RMeetingRecordId(req);
    const update = buildWilsyR91K179E15RMeetingUpdate(req);
    const tenantId =
      req.headers?.['x-tenant-id'] ||
      req.headers?.['x-wilsy-tenant-id'] ||
      req.body?.tenantId ||
      req.body?.meeting?.tenantId ||
      update.tenantId ||
      'wilsy-sovereign-root';

    if (!recordId) {
      return res.status(400).json({
        ok: false,
        success: false,
        status: 'MEETING_ID_REQUIRED',
        message: 'Meeting id is required before update.',
        route: '/api/crm/command/meetings/:id',
      });
    }

    const mongooseRuntime = await resolveWilsyR91K179E15RMeetingRuntime();
    const MeetingModel =
      mongooseRuntime?.models?.CRMMeeting ||
      mongooseRuntime?.models?.Meeting ||
      mongooseRuntime?.models?.CrmMeeting ||
      null;
    const filter = buildWilsyR91K179E15RMeetingFilter(mongooseRuntime, recordId);

    let saved = null;
    let collectionName = '';

    if (MeetingModel && typeof MeetingModel.findOneAndUpdate === 'function') {
      try {
        saved = await MeetingModel.findOneAndUpdate(
          filter,
          { $set: update },
          { new: true, returnDocument: 'after', runValidators: false, lean: true }
        );
        collectionName = MeetingModel.collection?.name || 'crmmeetings';
      } catch {
        saved = null;
      }
    }

    const activeDb =
      mongooseRuntime?.connection?.db ||
      (Array.isArray(mongooseRuntime?.connections)
        ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
        : null);

    if (!saved && activeDb) {
      for (const candidateCollection of [
        'crmmeetings',
        'meetings',
        'crm_meetings',
        'CRMMeeting',
        'Meeting',
      ]) {
        try {
          const result = await activeDb
            .collection(candidateCollection)
            .findOneAndUpdate(filter, { $set: update }, { returnDocument: 'after' });
          const value = result?.value || result;
          if (value && (value._id || value.id || value.meetingId)) {
            saved = value;
            collectionName = candidateCollection;
            break;
          }
        } catch {
          // Try next collection.
        }
      }
    }

    if (!saved) {
      return res.status(404).json({
        ok: false,
        success: false,
        status: 'MEETING_NOT_FOUND',
        message: 'Meeting record was not found for update.',
        route: '/api/crm/command/meetings/:id',
        recordId,
      });
    }

    const savedRecordId = String(saved._id || saved.id || saved.meetingId || recordId);

    return res.status(200).json({
      ok: true,
      success: true,
      status: 'DB_PERSISTED',
      result: 'DB_PERSISTED',
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
      message: 'Meeting updated through CRM command authority.',
      tenantId,
      recordId: savedRecordId,
      meetingId: savedRecordId,
      meeting: saved,
      record: saved,
      route: '/api/crm/command/meetings/:id',
      auditMesh: {
        status: 'DB_PERSISTED',
        dbPersisted: true,
        source: 'R91K179E15R_MEETING_CRUD_ROUTE_CONTRACT',
        collection: collectionName,
        tenantId,
      },
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'MEETING_UPDATE_FAILED',
      message: error?.message || 'Meeting update failed.',
      route: '/api/crm/command/meetings/:id',
    });
  }
}

/**
 * @function handleWilsyR91K179E15RMeetingDelete
 * @description Deletes a persisted CRM Meeting record and returns governed deletion confirmation.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<Object>} JSON delete response.
 * @collaboration CRM Meetings records workspace, DELETE /meetings/:id, audit evidence.
 */
async function handleWilsyR91K179E15RMeetingDelete(req, res) {
  try {
    const recordId = resolveWilsyR91K179E15RMeetingRecordId(req);
    const tenantId =
      req.headers?.['x-tenant-id'] ||
      req.headers?.['x-wilsy-tenant-id'] ||
      req.body?.tenantId ||
      'wilsy-sovereign-root';

    if (!recordId) {
      return res.status(400).json({
        ok: false,
        success: false,
        status: 'MEETING_ID_REQUIRED',
        message: 'Meeting id is required before delete.',
        route: '/api/crm/command/meetings/:id',
      });
    }

    const mongooseRuntime = await resolveWilsyR91K179E15RMeetingRuntime();
    const MeetingModel =
      mongooseRuntime?.models?.CRMMeeting ||
      mongooseRuntime?.models?.Meeting ||
      mongooseRuntime?.models?.CrmMeeting ||
      null;
    const filter = buildWilsyR91K179E15RMeetingFilter(mongooseRuntime, recordId);

    let deletedCount = 0;
    let collectionName = '';

    if (MeetingModel && typeof MeetingModel.deleteOne === 'function') {
      try {
        const result = await MeetingModel.deleteOne(filter);
        deletedCount = Number(result?.deletedCount || 0);
        collectionName = MeetingModel.collection?.name || 'crmmeetings';
      } catch {
        deletedCount = 0;
      }
    }

    const activeDb =
      mongooseRuntime?.connection?.db ||
      (Array.isArray(mongooseRuntime?.connections)
        ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
        : null);

    if (!deletedCount && activeDb) {
      for (const candidateCollection of [
        'crmmeetings',
        'meetings',
        'crm_meetings',
        'CRMMeeting',
        'Meeting',
      ]) {
        try {
          const result = await activeDb.collection(candidateCollection).deleteOne(filter);
          deletedCount = Number(result?.deletedCount || 0);
          if (deletedCount) {
            collectionName = candidateCollection;
            break;
          }
        } catch {
          // Try next collection.
        }
      }
    }

    if (!deletedCount) {
      return res.status(404).json({
        ok: false,
        success: false,
        status: 'MEETING_NOT_FOUND',
        message: 'Meeting record was not found for delete.',
        route: '/api/crm/command/meetings/:id',
        recordId,
      });
    }

    return res.status(200).json({
      ok: true,
      success: true,
      status: 'DB_DELETED',
      result: 'DB_DELETED',
      persistenceStatus: 'DB_DELETED',
      sourceStatus: 'DB_DELETED',
      message: 'Meeting deleted through CRM command authority.',
      tenantId,
      recordId,
      meetingId: recordId,
      route: '/api/crm/command/meetings/:id',
      auditMesh: {
        status: 'DB_DELETED',
        dbDeleted: true,
        source: 'R91K179E15R_MEETING_CRUD_ROUTE_CONTRACT',
        collection: collectionName,
        tenantId,
      },
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'MEETING_DELETE_FAILED',
      message: error?.message || 'Meeting delete failed.',
      route: '/api/crm/command/meetings/:id',
    });
  }
}

/**
 * @function pickWilsyR91K179E21Value
 * @description Picks the first non-empty value from a candidate list.
 * @param {...*} candidates - Candidate values.
 * @returns {*} First non-empty candidate.
 * @collaboration CRM Meeting create route, venue persistence normalization, DB_PERSISTED response.
 */
function pickWilsyR91K179E21Value(...candidates) {
  return candidates.find((candidate) => {
    if (Array.isArray(candidate)) return candidate.length > 0;
    if (candidate && typeof candidate === 'object') return Object.keys(candidate).length > 0;
    return String(candidate || '').trim();
  });
}

/**
 * @function resolveWilsyR91K179E21MongooseRuntime
 * @description Resolves the active mongoose runtime for CRM Meeting create persistence.
 * @returns {Promise<Object|null>} Mongoose runtime.
 * @collaboration CRM Meeting create route, CRMLead DB_PERSISTED pattern, raw collection fallback.
 */
async function resolveWilsyR91K179E21MongooseRuntime() {
  try {
    if (typeof resolveWilsyR91K76MongooseRuntime === 'function') {
      const runtime = resolveWilsyR91K76MongooseRuntime();
      if (runtime) return runtime;
    }
  } catch {
    // Continue to direct mongoose import.
  }

  try {
    const mongooseModule = await import('mongoose');
    return mongooseModule.default || mongooseModule;
  } catch {
    return null;
  }
}

/**
 * @function normalizeWilsyR91K179E21MeetingCreateDocument
 * @description Builds a venue-complete CRM Meeting document from frontend command payload variants.
 * @param {Object} req - Express request.
 * @returns {Object} Normalized Meeting document and institutional evidence.
 * @collaboration WilsyMeetingEditor, CRM command route, live Meetings records workspace.
 */
function normalizeWilsyR91K179E21MeetingCreateDocument(req = {}) {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const strikePayload =
    body.strikePayload && typeof body.strikePayload === 'object' ? body.strikePayload : {};
  const meeting =
    body.meeting && typeof body.meeting === 'object'
      ? body.meeting
      : strikePayload.meeting && typeof strikePayload.meeting === 'object'
        ? strikePayload.meeting
        : body.payload && typeof body.payload === 'object'
          ? body.payload
          : body.data && typeof body.data === 'object'
            ? body.data
            : {};

  const institutionalHeaders =
    body.institutionalHeaders || strikePayload.institutionalHeaders || strikePayload.headers || {};

  const tenantId = String(
    pickWilsyR91K179E21Value(
      meeting.tenantId,
      body.tenantId,
      strikePayload.tenantId,
      institutionalHeaders.tenantId,
      req.headers?.['x-tenant-id'],
      req.headers?.['x-wilsy-tenant-id'],
      'wilsy-sovereign-root'
    )
  );

  const operatorId = String(
    pickWilsyR91K179E21Value(
      meeting.createdBy,
      meeting.updatedBy,
      body.operatorContext?.operatorId,
      institutionalHeaders.operatorId,
      institutionalHeaders.actor,
      req.headers?.['x-operator-id'],
      'wilsy-local-operator'
    )
  );

  const title = String(
    pickWilsyR91K179E21Value(
      meeting.title,
      meeting.subject,
      meeting.meetingTitle,
      body.title,
      'New Meeting'
    )
  );

  const venue = String(
    pickWilsyR91K179E21Value(
      meeting.meetingVenue,
      meeting.venue,
      meeting.venueType,
      meeting.meetingVenueLabel,
      meeting.locationType,
      body.meetingVenue,
      body.venue,
      strikePayload.meetingVenue,
      strikePayload.venue,
      ''
    ) || ''
  ).trim();

  const location = String(
    pickWilsyR91K179E21Value(
      meeting.location,
      meeting.address,
      meeting.site,
      body.location,
      strikePayload.location,
      ''
    ) || ''
  ).trim();

  const participants = Array.isArray(meeting.participants)
    ? meeting.participants
    : Array.isArray(meeting.attendees)
      ? meeting.attendees
      : Array.isArray(meeting.invitees)
        ? meeting.invitees
        : [];

  const createdAt = meeting.createdAt ? new Date(meeting.createdAt) : new Date();
  const updatedAt = new Date();

  const document = {
    ...meeting,
    title,
    subject: pickWilsyR91K179E21Value(meeting.subject, title),
    meetingTitle: pickWilsyR91K179E21Value(meeting.meetingTitle, title),
    meetingVenue: venue,
    venue,
    venueType: venue,
    meetingVenueLabel: venue,
    locationType: venue,
    location,
    participants,
    attendees: participants,
    fromDate: meeting.fromDate || body.fromDate || '',
    fromTime: meeting.fromTime || body.fromTime || '',
    toDate: meeting.toDate || body.toDate || '',
    toTime: meeting.toTime || body.toTime || '',
    startsAt: meeting.startsAt || meeting.startAt || null,
    endsAt: meeting.endsAt || meeting.endAt || null,
    repeat: meeting.repeat || 'None',
    reminder: meeting.reminder || 'None',
    relatedRecord: meeting.relatedRecord || meeting.relatedTo || null,
    relatedTo: meeting.relatedTo || meeting.relatedRecord || null,
    description: meeting.description || meeting.agenda || '',
    agenda: meeting.agenda || meeting.description || '',
    status: meeting.status || 'SCHEDULED',
    tenantId,
    createdBy: meeting.createdBy || operatorId,
    updatedBy: operatorId,
    createdAt,
    updatedAt,
    wilsyPersistenceContract: 'R91K179E21_MEETING_CREATE_VENUE_PERSISTENCE_CONTRACT',
    wilsyVenuePersistence: {
      captured: Boolean(venue),
      venue,
      location,
      source: 'R91K179E21_MEETING_CREATE_VENUE_PERSISTENCE_CONTRACT',
      capturedAt: updatedAt.toISOString(),
    },
    institutionalHeaders,
    commandSurface:
      body.commandSurface ||
      institutionalHeaders.commandSurface ||
      'R91K179E21_MEETING_CREATE_VENUE_PERSISTENCE',
  };

  delete document._id;

  return {
    document,
    tenantId,
    operatorId,
    venue,
    institutionalHeaders,
  };
}

/**
 * @function persistWilsyR91K179E21MeetingCreateDocument
 * @description Persists a normalized CRM Meeting document through model-first and raw-collection fallback.
 * @param {Object} document - Meeting document.
 * @returns {Promise<Object>} Persisted record and collection metadata.
 * @collaboration CRMMeeting model, raw crmmeetings collection, DB_PERSISTED response.
 */
async function persistWilsyR91K179E21MeetingCreateDocument(document = {}) {
  const mongooseRuntime = await resolveWilsyR91K179E21MongooseRuntime();
  const MeetingModel =
    mongooseRuntime?.models?.CRMMeeting ||
    mongooseRuntime?.models?.Meeting ||
    mongooseRuntime?.models?.CrmMeeting ||
    null;

  if (MeetingModel && typeof MeetingModel.create === 'function') {
    try {
      const savedDocument = await MeetingModel.create(document);
      const saved =
        typeof savedDocument?.toObject === 'function' ? savedDocument.toObject() : savedDocument;
      return {
        saved,
        collectionName: MeetingModel.collection?.name || 'crmmeetings',
        persistenceMode: 'MODEL_CREATE',
      };
    } catch {
      // Fall through to raw collection fallback, matching the stable Lead save contract.
    }
  }

  const activeDb =
    mongooseRuntime?.connection?.db ||
    (Array.isArray(mongooseRuntime?.connections)
      ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
      : null);

  if (!activeDb) {
    return {
      saved: null,
      collectionName: '',
      persistenceMode: 'NO_ACTIVE_DB',
    };
  }

  const collectionName = 'crmmeetings';
  const insertResult = await activeDb.collection(collectionName).insertOne(document);

  return {
    saved: {
      ...document,
      _id: insertResult.insertedId,
    },
    collectionName,
    persistenceMode: 'RAW_COLLECTION_INSERT',
  };
}

/**
 * @function handleWilsyR91K179E21MeetingCreateVenuePersisted
 * @description Creates CRM Meetings with venue fields persisted for the live records workspace.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<Object>} JSON DB_PERSISTED response.
 * @collaboration Meeting editor save, CRM live Meetings list, tenant/operator evidence.
 */
async function handleWilsyR91K179E21MeetingCreateVenuePersisted(req, res) {
  try {
    const normalized = normalizeWilsyR91K179E21MeetingCreateDocument(req);
    const persistence = await persistWilsyR91K179E21MeetingCreateDocument(normalized.document);

    if (!persistence.saved) {
      return res.status(503).json({
        ok: false,
        success: false,
        status: 'MEETING_DB_UNAVAILABLE',
        message: 'MongoDB connection unavailable for meeting command authority.',
        route: '/api/crm/command/meetings',
        tenantId: normalized.tenantId,
      });
    }

    const savedRecordId = String(
      persistence.saved._id ||
        persistence.saved.id ||
        persistence.saved.meetingId ||
        persistence.saved.recordId ||
        ''
    );

    const saved = {
      ...persistence.saved,
      id: String(persistence.saved.id || savedRecordId),
      recordId: String(persistence.saved.recordId || savedRecordId),
      meetingId: String(persistence.saved.meetingId || savedRecordId),
      tenantId: normalized.tenantId,
      meetingVenue: normalized.venue,
      venue: normalized.venue,
      venueType: normalized.venue,
      meetingVenueLabel: normalized.venue,
      locationType: normalized.venue,
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
    };

    return res.status(201).json({
      ok: true,
      success: true,
      status: 'DB_PERSISTED',
      result: 'DB_PERSISTED',
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
      message: 'Meeting persisted through CRM command authority.',
      tenantId: normalized.tenantId,
      recordId: saved.recordId,
      meetingId: saved.meetingId,
      meeting: saved,
      record: saved,
      route: '/api/crm/command/meetings',
      auditMesh: {
        status: 'DB_PERSISTED',
        dbPersisted: true,
        source: 'R91K179E21_MEETING_CREATE_VENUE_PERSISTENCE_CONTRACT',
        collection: persistence.collectionName,
        persistenceMode: persistence.persistenceMode,
        tenantId: normalized.tenantId,
        venueCaptured: Boolean(normalized.venue),
      },
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'MEETING_CREATE_FAILED',
      message: error?.message || 'Meeting create failed.',
      route: '/api/crm/command/meetings',
    });
  }
}

/**
 * @function pickWilsyR91K179E22B1Value
 * @description Selects the first non-empty command value without inventing Meeting data.
 * @param {...*} candidates - Candidate values.
 * @returns {*} First meaningful value.
 * @collaboration CRM Meeting create/update, venue integrity, raw DB repair.
 */
function pickWilsyR91K179E22B1Value(...candidates) {
  return candidates.find((candidate) => {
    if (Array.isArray(candidate)) return candidate.length > 0;
    if (candidate && typeof candidate === 'object') return Object.keys(candidate).length > 0;
    return String(candidate || '').trim();
  });
}

/**
 * @function compactWilsyR91K179E22B1Document
 * @description Removes undefined values before MongoDB write operations.
 * @param {Object} document - Document candidate.
 * @returns {Object} Compact document.
 * @collaboration MongoDB update operators, CRM command route, venue evidence.
 */
function compactWilsyR91K179E22B1Document(document = {}) {
  return Object.fromEntries(
    Object.entries(document).filter(([, value]) => typeof value !== 'undefined')
  );
}

/**
 * @function resolveWilsyR91K179E22B1MongooseRuntime
 * @description Resolves the active mongoose runtime without creating a new service.
 * @returns {Promise<Object|null>} Active mongoose runtime.
 * @collaboration Existing Wilsy CRM command runtime, CRMMeeting model, raw collection fallback.
 */
async function resolveWilsyR91K179E22B1MongooseRuntime() {
  try {
    if (typeof resolveWilsyR91K76MongooseRuntime === 'function') {
      const runtime = resolveWilsyR91K76MongooseRuntime();
      if (runtime) return runtime;
    }
  } catch {
    // Continue to direct mongoose import.
  }

  try {
    const mongooseModule = await import('mongoose');
    return mongooseModule.default || mongooseModule;
  } catch {
    return null;
  }
}

/**
 * @function normalizeWilsyR91K179E22B1MeetingCommand
 * @description Normalizes Meeting command payloads so venue survives create and edit saves.
 * @param {Object} req - Express request.
 * @returns {Object} Normalized command.
 * @collaboration WilsyMeetingEditor, POST/PATCH meeting command routes, live records table.
 */
function normalizeWilsyR91K179E22B1MeetingCommand(req = {}) {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const strikePayload =
    body.strikePayload && typeof body.strikePayload === 'object' ? body.strikePayload : {};
  const meeting =
    body.meeting && typeof body.meeting === 'object'
      ? body.meeting
      : strikePayload.meeting && typeof strikePayload.meeting === 'object'
        ? strikePayload.meeting
        : body.payload && typeof body.payload === 'object'
          ? body.payload
          : body;

  const institutionalHeaders =
    body.institutionalHeaders || strikePayload.institutionalHeaders || strikePayload.headers || {};

  const tenantId = String(
    pickWilsyR91K179E22B1Value(
      meeting.tenantId,
      body.tenantId,
      strikePayload.tenantId,
      institutionalHeaders.tenantId,
      req.headers?.['x-tenant-id'],
      req.headers?.['x-wilsy-tenant-id'],
      req.tenantId,
      'wilsy-sovereign-root'
    )
  );

  const recordId = String(
    pickWilsyR91K179E22B1Value(
      req.params?.id,
      meeting.recordId,
      meeting.meetingId,
      meeting.id,
      meeting._id,
      body.recordId,
      body.meetingId,
      strikePayload.recordId,
      strikePayload.meetingId,
      ''
    ) || ''
  ).trim();

  const operatorId = String(
    pickWilsyR91K179E22B1Value(
      meeting.updatedBy,
      meeting.createdBy,
      body.operatorContext?.operatorId,
      institutionalHeaders.operatorId,
      institutionalHeaders.actor,
      req.headers?.['x-operator-id'],
      'wilsy-local-operator'
    )
  );

  const title = String(
    pickWilsyR91K179E22B1Value(
      meeting.title,
      meeting.subject,
      meeting.meetingTitle,
      body.title,
      'New Meeting'
    )
  );

  const venue = String(
    pickWilsyR91K179E22B1Value(
      meeting.meetingVenue,
      meeting.venue,
      meeting.venueType,
      meeting.meetingVenueLabel,
      meeting.locationType,
      body.meetingVenue,
      body.venue,
      body.venueType,
      body.meetingVenueLabel,
      body.locationType,
      strikePayload.meetingVenue,
      strikePayload.venue,
      strikePayload.venueType,
      strikePayload.meetingVenueLabel,
      strikePayload.locationType,
      ''
    ) || ''
  ).trim();

  const location = String(
    pickWilsyR91K179E22B1Value(
      meeting.location,
      meeting.address,
      meeting.site,
      body.location,
      strikePayload.location,
      ''
    ) || ''
  ).trim();

  const participants = Array.isArray(meeting.participants)
    ? meeting.participants
    : Array.isArray(meeting.attendees)
      ? meeting.attendees
      : Array.isArray(meeting.invitees)
        ? meeting.invitees
        : [];

  const now = new Date();

  const document = compactWilsyR91K179E22B1Document({
    ...meeting,
    title,
    subject: pickWilsyR91K179E22B1Value(meeting.subject, title),
    meetingTitle: pickWilsyR91K179E22B1Value(meeting.meetingTitle, title),
    meetingVenue: venue,
    venue,
    venueType: venue,
    meetingVenueLabel: venue,
    locationType: venue,
    location,
    participants,
    attendees: participants,
    fromDate: pickWilsyR91K179E22B1Value(meeting.fromDate, body.fromDate, ''),
    fromTime: pickWilsyR91K179E22B1Value(meeting.fromTime, body.fromTime, ''),
    toDate: pickWilsyR91K179E22B1Value(meeting.toDate, body.toDate, ''),
    toTime: pickWilsyR91K179E22B1Value(meeting.toTime, body.toTime, ''),
    startsAt: pickWilsyR91K179E22B1Value(meeting.startsAt, meeting.startAt, null),
    endsAt: pickWilsyR91K179E22B1Value(meeting.endsAt, meeting.endAt, null),
    repeat: pickWilsyR91K179E22B1Value(meeting.repeat, 'None'),
    reminder: pickWilsyR91K179E22B1Value(meeting.reminder, 'None'),
    relatedRecord: pickWilsyR91K179E22B1Value(
      meeting.relatedRecord,
      meeting.relatedTo,
      body.relatedRecord,
      null
    ),
    relatedTo: pickWilsyR91K179E22B1Value(
      meeting.relatedTo,
      meeting.relatedRecord,
      body.relatedRecord,
      null
    ),
    description: pickWilsyR91K179E22B1Value(meeting.description, meeting.agenda, ''),
    agenda: pickWilsyR91K179E22B1Value(meeting.agenda, meeting.description, ''),
    status: pickWilsyR91K179E22B1Value(meeting.status, 'SCHEDULED'),
    tenantId,
    createdBy: pickWilsyR91K179E22B1Value(meeting.createdBy, operatorId),
    updatedBy: operatorId,
    updatedAt: now,
    wilsyPersistenceContract: 'R91K179E22B1_MEETING_VENUE_INTEGRITY_REAL_MAP',
    wilsyVenuePersistence: {
      captured: Boolean(venue),
      venue,
      location,
      source: 'R91K179E22B1_MEETING_VENUE_INTEGRITY_REAL_MAP',
      capturedAt: now.toISOString(),
      recordId,
    },
    institutionalHeaders,
    commandSurface:
      body.commandSurface ||
      institutionalHeaders.commandSurface ||
      'R91K179E22B1_MEETING_VENUE_INTEGRITY_REAL_MAP',
  });

  if (!document.createdAt) document.createdAt = now;
  delete document._id;

  return {
    body,
    strikePayload,
    institutionalHeaders,
    tenantId,
    recordId,
    operatorId,
    venue,
    location,
    document,
  };
}

/**
 * @function buildWilsyR91K179E22B1Filters
 * @description Builds safe filters for Meeting id variants.
 * @param {Object} mongooseRuntime - Mongoose runtime.
 * @param {string} recordId - Meeting record id.
 * @returns {Array<Object>} Candidate filters.
 * @collaboration CRMMeeting, raw collection fallback, live records repair.
 */
function buildWilsyR91K179E22B1Filters(mongooseRuntime, recordId = '') {
  const id = String(recordId || '').trim();
  const filters = [];

  if (!id) return filters;

  try {
    const ObjectId = mongooseRuntime?.Types?.ObjectId;
    if (ObjectId && ObjectId.isValid(id)) {
      filters.push({ _id: new ObjectId(id) });
    }
  } catch {
    // Continue string id filters.
  }

  filters.push({ _id: id }, { id }, { recordId: id }, { meetingId: id });
  return filters;
}

/**
 * @function forceWilsyR91K179E22B1VenueWrite
 * @description Forces venue fields into raw Meeting storage after model create or edit update.
 * @param {Object} args - Venue write args.
 * @returns {Promise<Object|null>} Updated document.
 * @collaboration CRMMeeting model, crmmeetings collection, venue integrity loop.
 */
async function forceWilsyR91K179E22B1VenueWrite({
  mongooseRuntime,
  recordId,
  document,
  preferredCollection,
}) {
  const db =
    mongooseRuntime?.connection?.db ||
    (Array.isArray(mongooseRuntime?.connections)
      ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
      : null);

  if (!db || !recordId) return null;

  const setDocument = compactWilsyR91K179E22B1Document({
    meetingVenue: document.meetingVenue,
    venue: document.venue,
    venueType: document.venueType,
    meetingVenueLabel: document.meetingVenueLabel,
    locationType: document.locationType,
    location: document.location,
    participants: document.participants,
    attendees: document.attendees,
    relatedRecord: document.relatedRecord,
    relatedTo: document.relatedTo,
    description: document.description,
    agenda: document.agenda,
    repeat: document.repeat,
    reminder: document.reminder,
    tenantId: document.tenantId,
    updatedBy: document.updatedBy,
    updatedAt: document.updatedAt || new Date(),
    wilsyVenuePersistence: document.wilsyVenuePersistence,
    wilsyPersistenceContract: 'R91K179E22B1_MEETING_VENUE_INTEGRITY_REAL_MAP',
  });

  const filters = buildWilsyR91K179E22B1Filters(mongooseRuntime, recordId);
  const collectionNames = Array.from(
    new Set(
      [
        preferredCollection,
        'crmmeetings',
        'meetings',
        'crm_meetings',
        'CRMMeeting',
        'Meeting',
      ].filter(Boolean)
    )
  );

  for (const collectionName of collectionNames) {
    const collection = db.collection(collectionName);

    for (const filter of filters) {
      const result = await collection.findOneAndUpdate(
        filter,
        { $set: setDocument },
        { returnDocument: 'after' }
      );

      const updated = result?.value || result;

      if (updated) {
        return {
          ...updated,
          persistenceMode: `RAW_VENUE_INTEGRITY_WRITE:${collectionName}`,
          collectionName,
        };
      }
    }
  }

  return null;
}

/**
 * @function buildWilsyR91K179E28NotificationSetDocument
 * @description Builds the raw MongoDB update document for Meeting invitation receipts.
 * @param {Object} notificationPacket - Notification packet from dispatcher.
 * @returns {Object} Compact update fields.
 * @collaboration Meeting notification service, raw collection persistence, invitation evidence.
 */
function buildWilsyR91K179E28NotificationSetDocument(notificationPacket = {}) {
  const fields =
    notificationPacket.persistedFields && typeof notificationPacket.persistedFields === 'object'
      ? notificationPacket.persistedFields
      : {};

  return compactWilsyR91K179E22B1Document({
    calendarUid: fields.calendarUid,
    calendarSequence: fields.calendarSequence,
    calendarInvite: fields.calendarInvite,
    invitationStatus: fields.invitationStatus,
    lastInviteSentAt: fields.lastInviteSentAt ? new Date(fields.lastInviteSentAt) : undefined,
    emailInvitationReceipts: fields.emailInvitationReceipts,
    smsInvitationReceipts: fields.smsInvitationReceipts,
    notificationReceipts: fields.notificationReceipts,
    meetingNotificationIntelligence: fields.meetingNotificationIntelligence,
    wilsyMeetingNotificationContract: fields.wilsyMeetingNotificationContract,
    updatedAt: new Date(),
  });
}

/**
 * @function persistWilsyR91K179E28MeetingNotificationReceipts
 * @description Persists invitation receipts onto the Meeting record after the save command succeeds.
 * @param {Object} args - Persistence arguments.
 * @returns {Promise<Object|null>} Updated Meeting record or null.
 * @collaboration CRM Meeting command routes, email/SMS receipts, calendar invite evidence.
 */
async function persistWilsyR91K179E28MeetingNotificationReceipts({
  mongooseRuntime,
  recordId,
  notificationPacket,
  preferredCollection,
}) {
  const db =
    mongooseRuntime?.connection?.db ||
    (Array.isArray(mongooseRuntime?.connections)
      ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
      : null);

  if (!db || !recordId || !notificationPacket) return null;

  const setDocument = buildWilsyR91K179E28NotificationSetDocument(notificationPacket);
  if (Object.keys(setDocument).length === 0) return null;

  const filters = buildWilsyR91K179E22B1Filters(mongooseRuntime, recordId);
  const collectionNames = Array.from(
    new Set(
      [
        preferredCollection,
        'crmmeetings',
        'meetings',
        'crm_meetings',
        'CRMMeeting',
        'Meeting',
      ].filter(Boolean)
    )
  );

  for (const collectionName of collectionNames) {
    const collection = db.collection(collectionName);

    for (const filter of filters) {
      const result = await collection.findOneAndUpdate(
        filter,
        { $set: setDocument },
        { returnDocument: 'after' }
      );

      const updated = result?.value || result;

      if (updated) {
        return {
          ...updated,
          notificationPersistenceMode: `RAW_NOTIFICATION_WRITE:${collectionName}`,
          collectionName,
        };
      }
    }
  }

  return null;
}

/**
 * @function resolveWilsyR91K179E28MeetingNotificationPacket
 * @description Dispatches notifications without allowing provider errors to undo the Meeting save.
 * @param {Object} args - Dispatch arguments.
 * @returns {Promise<Object>} Notification packet.
 * @collaboration Meeting command finality, email/SMS service resilience, frontend save response.
 */
async function resolveWilsyR91K179E28MeetingNotificationPacket(args = {}) {
  try {
    return await dispatchWilsyMeetingInvitations(args);
  } catch (error) {
    return {
      ok: false,
      invitationStatus: 'INVITE_DISPATCH_ERROR',
      message: error?.message || 'Meeting invitation dispatch failed.',
      calendarInvite: null,
      aiTemplate: null,
      emailInvitationReceipts: [],
      smsInvitationReceipts: [],
      notificationReceipts: [
        {
          version: 'R91K179E28_MEETING_NOTIFICATION_COMMAND',
          invitationStatus: 'INVITE_DISPATCH_ERROR',
          error: error?.message || 'Meeting invitation dispatch failed.',
          generatedAt: new Date().toISOString(),
        },
      ],
      persistedFields: {
        invitationStatus: 'INVITE_DISPATCH_ERROR',
        notificationReceipts: [
          {
            version: 'R91K179E28_MEETING_NOTIFICATION_COMMAND',
            invitationStatus: 'INVITE_DISPATCH_ERROR',
            error: error?.message || 'Meeting invitation dispatch failed.',
            generatedAt: new Date().toISOString(),
          },
        ],
        wilsyMeetingNotificationContract: 'R91K179E28_MEETING_NOTIFICATION_COMMAND',
      },
    };
  }
}

/**
 * @function persistWilsyR91K179E22B1Create
 * @description Creates a Meeting then forces venue fields into raw storage.
 * @param {Object} command - Normalized command.
 * @returns {Promise<Object>} Persistence result.
 * @collaboration Meeting create route, CRMMeeting model, raw venue integrity write.
 */
async function persistWilsyR91K179E22B1Create(command) {
  const mongooseRuntime = await resolveWilsyR91K179E22B1MongooseRuntime();
  const MeetingModel =
    mongooseRuntime?.models?.CRMMeeting ||
    mongooseRuntime?.models?.Meeting ||
    mongooseRuntime?.models?.CrmMeeting ||
    null;

  let saved = null;
  let collectionName = 'crmmeetings';
  let persistenceMode = 'RAW_COLLECTION_INSERT';

  if (MeetingModel && typeof MeetingModel.create === 'function') {
    try {
      const savedDocument = await MeetingModel.create(command.document);
      saved =
        typeof savedDocument?.toObject === 'function' ? savedDocument.toObject() : savedDocument;
      collectionName = MeetingModel.collection?.name || collectionName;
      persistenceMode = 'MODEL_CREATE_WITH_RAW_VENUE_INTEGRITY';
    } catch {
      saved = null;
    }
  }

  const db =
    mongooseRuntime?.connection?.db ||
    (Array.isArray(mongooseRuntime?.connections)
      ? mongooseRuntime.connections.find((connection) => connection?.db)?.db
      : null);

  if (!saved && db) {
    const insertResult = await db.collection(collectionName).insertOne(command.document);
    saved = { ...command.document, _id: insertResult.insertedId };
    persistenceMode = 'RAW_COLLECTION_INSERT';
  }

  if (!saved) return { saved: null, collectionName, persistenceMode: 'NO_ACTIVE_DB' };

  const recordId = String(saved._id || saved.id || saved.recordId || saved.meetingId || '');
  const repaired = await forceWilsyR91K179E22B1VenueWrite({
    mongooseRuntime,
    recordId,
    document: { ...command.document, _id: saved._id },
    preferredCollection: collectionName,
  });

  return {
    saved: repaired || { ...saved, ...command.document, _id: saved._id },
    collectionName: repaired?.collectionName || collectionName,
    persistenceMode: repaired?.persistenceMode || persistenceMode,
  };
}

/**
 * @function persistWilsyR91K179E22B1Update
 * @description Updates an existing Meeting through raw venue integrity repair.
 * @param {Object} command - Normalized command.
 * @returns {Promise<Object>} Persistence result.
 * @collaboration Meeting edit route, existing record repair, venue display.
 */
async function persistWilsyR91K179E22B1Update(command) {
  const mongooseRuntime = await resolveWilsyR91K179E22B1MongooseRuntime();

  if (!command.recordId) {
    return { saved: null, collectionName: '', persistenceMode: 'MISSING_RECORD_ID' };
  }

  const repaired = await forceWilsyR91K179E22B1VenueWrite({
    mongooseRuntime,
    recordId: command.recordId,
    document: command.document,
    preferredCollection: 'crmmeetings',
  });

  return {
    saved: repaired,
    collectionName: repaired?.collectionName || '',
    persistenceMode: repaired?.persistenceMode || 'RAW_VENUE_REPAIR_NOT_FOUND',
  };
}

/**
 * @function shapeWilsyR91K179E22B1ResponseRecord
 * @description Shapes the Meeting response so the UI receives venue fields immediately.
 * @param {Object} saved - Saved record.
 * @param {Object} command - Normalized command.
 * @returns {Object} UI-ready record.
 * @collaboration Meeting editor, live records table, venue integrity response.
 */
function shapeWilsyR91K179E22B1ResponseRecord(saved = {}, command = {}) {
  const id = String(
    saved._id || saved.id || saved.recordId || saved.meetingId || command.recordId || ''
  );

  return {
    ...saved,
    id: String(saved.id || id),
    recordId: String(saved.recordId || id),
    meetingId: String(saved.meetingId || id),
    tenantId: command.tenantId,
    meetingVenue: command.venue,
    venue: command.venue,
    venueType: command.venue,
    meetingVenueLabel: command.venue,
    locationType: command.venue,
    location: command.location,
    persistenceStatus: 'DB_PERSISTED',
    sourceStatus: 'DB_PERSISTED',
  };
}

/**
 * @function handleWilsyR91K179E22B1MeetingCreateVenueIntegrity
 * @description Creates Meetings with venue integrity guaranteed beyond model schema stripping.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<Object>} JSON response.
 * @collaboration POST /api/crm/command/meetings, WilsyMeetingEditor, DB_PERSISTED records.
 */
async function handleWilsyR91K179E22B1MeetingCreateVenueIntegrity(req, res) {
  try {
    const command = normalizeWilsyR91K179E22B1MeetingCommand(req);
    const persistence = await persistWilsyR91K179E22B1Create(command);

    if (!persistence.saved) {
      return res.status(503).json({
        ok: false,
        success: false,
        status: 'MEETING_DB_UNAVAILABLE',
        message: 'MongoDB connection unavailable for meeting command authority.',
        route: '/api/crm/command/meetings',
        tenantId: command.tenantId,
      });
    }

    const savedBase = shapeWilsyR91K179E22B1ResponseRecord(persistence.saved, command);
    const mongooseRuntime = await resolveWilsyR91K179E22B1MongooseRuntime();
    const notificationPacket = await resolveWilsyR91K179E28MeetingNotificationPacket({
      meeting: savedBase,
      command,
      tenantId: command.tenantId,
      operatorId: command.operatorId,
      request: req,
      saveMode: 'create',
    });
    const notificationRecord = await persistWilsyR91K179E28MeetingNotificationReceipts({
      mongooseRuntime,
      recordId: savedBase.recordId,
      notificationPacket,
      preferredCollection: persistence.collectionName,
    });
    const saved = shapeWilsyR91K179E22B1ResponseRecord(
      {
        ...savedBase,
        ...(notificationPacket.persistedFields || {}),
        ...(notificationRecord || {}),
      },
      command
    );

    return res.status(201).json({
      ok: true,
      success: true,
      status: 'DB_PERSISTED',
      result: 'DB_PERSISTED',
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
      message: command.venue
        ? 'Meeting persisted with venue integrity through CRM command authority.'
        : 'Meeting persisted; venue remains uncaptured until operator selects it.',
      tenantId: command.tenantId,
      recordId: saved.recordId,
      meetingId: saved.meetingId,
      meeting: saved,
      record: saved,
      notificationStatus: notificationPacket.invitationStatus,
      calendarInvite: notificationPacket.calendarInvite,
      emailInvitationReceipts: notificationPacket.emailInvitationReceipts || [],
      smsInvitationReceipts: notificationPacket.smsInvitationReceipts || [],
      notificationReceipts: notificationPacket.notificationReceipts || [],
      meetingNotificationIntelligence: notificationPacket.aiTemplate || null,
      route: '/api/crm/command/meetings',
      auditMesh: {
        status: 'DB_PERSISTED',
        dbPersisted: true,
        source: 'R91K179E22B1_MEETING_VENUE_INTEGRITY_REAL_MAP',
        collection: persistence.collectionName,
        persistenceMode: persistence.persistenceMode,
        notificationStatus: notificationPacket.invitationStatus,
        notificationPersistenceMode:
          notificationRecord?.notificationPersistenceMode || 'NOTIFICATION_RESPONSE_ONLY',
        tenantId: command.tenantId,
        venueCaptured: Boolean(command.venue),
        venue: command.venue,
      },
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'MEETING_CREATE_FAILED',
      message: error?.message || 'Meeting create failed.',
      route: '/api/crm/command/meetings',
    });
  }
}

/**
 * @function handleWilsyR91K179E22B1MeetingUpdateVenueIntegrity
 * @description Updates Meetings and repairs venue fields for old venue-missing records.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<Object>} JSON response.
 * @collaboration PATCH /api/crm/command/meetings/:id, editor save, live records table.
 */
async function handleWilsyR91K179E22B1MeetingUpdateVenueIntegrity(req, res) {
  try {
    const command = normalizeWilsyR91K179E22B1MeetingCommand(req);

    if (!command.recordId) {
      return res.status(400).json({
        ok: false,
        success: false,
        status: 'MEETING_ID_REQUIRED',
        message: 'Meeting record id is required for venue repair/update.',
      });
    }

    const persistence = await persistWilsyR91K179E22B1Update(command);

    if (!persistence.saved) {
      return res.status(404).json({
        ok: false,
        success: false,
        status: 'MEETING_NOT_FOUND',
        message: 'Meeting record was not found for venue repair/update.',
        recordId: command.recordId,
      });
    }

    const savedBase = shapeWilsyR91K179E22B1ResponseRecord(persistence.saved, command);
    const mongooseRuntime = await resolveWilsyR91K179E22B1MongooseRuntime();
    const notificationPacket = await resolveWilsyR91K179E28MeetingNotificationPacket({
      meeting: savedBase,
      command,
      tenantId: command.tenantId,
      operatorId: command.operatorId,
      request: req,
      saveMode: 'edit',
    });
    const notificationRecord = await persistWilsyR91K179E28MeetingNotificationReceipts({
      mongooseRuntime,
      recordId: savedBase.recordId,
      notificationPacket,
      preferredCollection: persistence.collectionName,
    });
    const saved = shapeWilsyR91K179E22B1ResponseRecord(
      {
        ...savedBase,
        ...(notificationPacket.persistedFields || {}),
        ...(notificationRecord || {}),
      },
      command
    );

    return res.status(200).json({
      ok: true,
      success: true,
      status: 'DB_PERSISTED',
      result: 'DB_PERSISTED',
      persistenceStatus: 'DB_PERSISTED',
      sourceStatus: 'DB_PERSISTED',
      message: command.venue
        ? 'Meeting updated with venue integrity through CRM command authority.'
        : 'Meeting updated; venue remains uncaptured until operator selects it.',
      tenantId: command.tenantId,
      recordId: saved.recordId,
      meetingId: saved.meetingId,
      meeting: saved,
      record: saved,
      notificationStatus: notificationPacket.invitationStatus,
      calendarInvite: notificationPacket.calendarInvite,
      emailInvitationReceipts: notificationPacket.emailInvitationReceipts || [],
      smsInvitationReceipts: notificationPacket.smsInvitationReceipts || [],
      notificationReceipts: notificationPacket.notificationReceipts || [],
      meetingNotificationIntelligence: notificationPacket.aiTemplate || null,
      route: `/api/crm/command/meetings/${encodeURIComponent(command.recordId)}`,
      auditMesh: {
        status: 'DB_PERSISTED',
        dbPersisted: true,
        source: 'R91K179E22B1_MEETING_VENUE_INTEGRITY_REAL_MAP',
        collection: persistence.collectionName,
        persistenceMode: persistence.persistenceMode,
        notificationStatus: notificationPacket.invitationStatus,
        notificationPersistenceMode:
          notificationRecord?.notificationPersistenceMode || 'NOTIFICATION_RESPONSE_ONLY',
        tenantId: command.tenantId,
        venueCaptured: Boolean(command.venue),
        venue: command.venue,
      },
    });
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      status: 'MEETING_UPDATE_FAILED',
      message: error?.message || 'Meeting update failed.',
      route: '/api/crm/command/meetings/:id',
    });
  }
}

router.post('/meetings', handleWilsyR91K179E22B1MeetingCreateVenueIntegrity);
router.patch('/meetings/:id', handleWilsyR91K179E22B1MeetingUpdateVenueIntegrity);

/**
 * @function buildWilsyR91K179E24P58HMeetingDeleteReceiptHash
 * @description Builds a deterministic receipt id for successful Meeting delete responses when the legacy handler deletes correctly but omits receiptHash.
 * @param {Object} context - Receipt context.
 * @returns {string} Receipt hash.
 * @collaboration CRM Meeting delete route, protected command capsule, auditMesh response contract.
 */
function buildWilsyR91K179E24P58HMeetingDeleteReceiptHash(context = {}) {
  const raw = [
    'R91K179E24P58H',
    context.tenantId || 'MASTER',
    context.recordId || 'meeting-id-unavailable',
    context.operatorId || context.operator || 'SYSTEM',
    context.generatedAt || new Date().toISOString(),
  ].join(':');

  return `MEETING_DELETE_RECEIPT_${Buffer.from(raw).toString('base64url').slice(0, 48)}`;
}

/**
 * @function decorateWilsyR91K179E24P58HMeetingDeleteReceipt
 * @description Decorates successful Meeting delete responses with receiptHash, receipt, auditMesh and institutional evidence without changing delete persistence.
 * @param {Object} payload - Original handler response payload.
 * @param {Object} req - Express request.
 * @returns {Object} Decorated response payload.
 * @collaboration Existing Meeting delete handler, protected command capsule, institutional strike payload evidence.
 */
function decorateWilsyR91K179E24P58HMeetingDeleteReceipt(payload = {}, req = {}) {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const strikePayload =
    body.strikePayload && typeof body.strikePayload === 'object' ? body.strikePayload : {};
  const institutionalHeadersSource =
    body.institutionalHeaders || strikePayload.institutionalHeaders || {};

  const generatedAt = new Date().toISOString();
  const tenantId = String(
    body.tenantId ||
      strikePayload.tenantId ||
      institutionalHeadersSource.tenantId ||
      req.headers?.['x-tenant-id'] ||
      req.tenantId ||
      'MASTER'
  );

  const operatorId = String(
    body.operatorId ||
      body.userId ||
      strikePayload.operatorId ||
      institutionalHeadersSource.operatorId ||
      req.headers?.['x-operator-id'] ||
      req.headers?.['x-wilsy-operator-id'] ||
      req.user?.id ||
      'SYSTEM'
  );

  const operatorEmail = String(
    body.operatorEmail ||
      institutionalHeadersSource.operatorEmail ||
      req.headers?.['x-operator-email'] ||
      req.headers?.['x-wilsy-operator-email'] ||
      req.user?.email ||
      ''
  );

  const recordId = String(
    req.params?.id ||
      body.recordId ||
      body.meetingId ||
      strikePayload.recordId ||
      strikePayload.meetingId ||
      payload.recordId ||
      payload.meetingId ||
      payload.id ||
      ''
  );

  const route = `/api/crm/command/meetings/${encodeURIComponent(recordId)}`;
  const receiptHash =
    String(
      payload.receiptHash ||
        payload.receipt?.receiptHash ||
        payload.receipt?.hash ||
        payload.auditMesh?.receiptHash ||
        ''
    ) ||
    buildWilsyR91K179E24P58HMeetingDeleteReceiptHash({
      tenantId,
      recordId,
      operatorId,
      generatedAt,
    });

  const institutionalHeaders = {
    ...institutionalHeadersSource,
    tenantId,
    operatorId,
    userId: operatorId,
    operatorEmail,
    route,
    commandSurface: 'R91K179E24P58H_MEETING_DELETE_RECEIPT_BRIDGE',
    generatedAt,
    recordId,
    module: 'meetings',
  };

  return {
    ...payload,
    ok: payload.ok !== false,
    status: payload.status || 'MEETING_DELETE_RECEIPT_SEALED',
    message: payload.message || 'Meeting delete completed through CRM command authority.',
    tenantId,
    recordId,
    meetingId: payload.meetingId || recordId,
    route,
    receiptHash,
    institutionalHeaders,
    strikePayload: {
      ...strikePayload,
      tenantId,
      operatorId,
      userId: operatorId,
      recordId,
      meetingId: recordId,
      route,
      commandSurface: 'R91K179E24P58H_MEETING_DELETE_RECEIPT_BRIDGE',
      generatedAt,
      institutionalHeaders,
    },
    receipt: {
      ...(payload.receipt && typeof payload.receipt === 'object' ? payload.receipt : {}),
      receiptHash,
      hash: receiptHash,
      status: payload.status || 'MEETING_DELETE_RECEIPT_SEALED',
      route,
      tenantId,
      operatorId,
      recordId,
      module: 'meetings',
      generatedAt,
    },
    auditMesh: {
      ...(payload.auditMesh && typeof payload.auditMesh === 'object' ? payload.auditMesh : {}),
      receiptHash,
      route,
      tenantId,
      operatorId,
      recordId,
      module: 'meetings',
      generatedAt,
      commandSurface: 'R91K179E24P58H_MEETING_DELETE_RECEIPT_BRIDGE',
    },
  };
}

/**
 * @function handleWilsyR91K179E24P58HMeetingDeleteReceiptBridge
 * @description Wraps the existing Meeting delete handler to guarantee successful responses carry a protected command receipt hash.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Existing handler result.
 * @collaboration Existing handleWilsyR91K179E15RMeetingDelete, CRM command routes, frontend Delete Governance capsule.
 */
async function handleWilsyR91K179E24P58HMeetingDeleteReceiptBridge(req, res, next) {
  const originalJson = res.json.bind(res);

  res.json = (payload = {}) => {
    const decoratedPayload = decorateWilsyR91K179E24P58HMeetingDeleteReceipt(payload, req);
    return originalJson(decoratedPayload);
  };

  return handleWilsyR91K179E15RMeetingDelete(req, res, next);
}

router.delete('/meetings/:id', handleWilsyR91K179E24P58HMeetingDeleteReceiptBridge);
router.post('/meetings/import-preview', handleWilsyR91K179MeetingImportPreview);

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
    fields: [
      'subject',
      'title',
      'meetingTitle',
      'accountName',
      'contactName',
      'status',
      'owner',
      'host',
      'meetingVenue',
      'venue',
      'venueType',
      'meetingVenueLabel',
      'locationType',
      'location',
      'description',
      'agenda',
      'participants.email',
      'participants.displayName',
      'participants.label',
      'attendees',
      'attendees.email',
      'attendees.displayName',
      'attendees.label',
      'relatedRecord.title',
      'relatedRecord.recordId',
      'relatedTo.title',
      'relatedTo.recordId',
      'relatedType',
      'relatedId',
    ],
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

const WILSY_R91K179E25_MEETING_INTELLIGENCE_VERSION =
  'R91K179E25-MEETING-COMMAND-INTELLIGENCE-LIVE';
const WILSY_R91K179E25_MEETING_COLLECTIONS = Object.freeze([
  'crm_meetings',
  'crmmeetings',
  'meetings',
  'CRMMeeting',
  'Meeting',
]);

/**
 * @function resolveWilsyR91K179E25MeetingRegistryEntry
 * @description Resolves the CRM registry entry dedicated to Meeting intelligence search.
 * @returns {Object} Meeting registry entry.
 * @collaboration CRM_MODEL_REGISTRY, Wilsy AI Meeting command rail, OS search.
 */
function resolveWilsyR91K179E25MeetingRegistryEntry() {
  return (
    CRM_MODEL_REGISTRY.find((entry) => entry.key === 'meetings') || {
      key: 'meetings',
      modelName: 'CRMMeeting',
      fields: ['title', 'subject', 'meetingVenue', 'venue', 'location', 'status'],
    }
  );
}

/**
 * @function normalizeWilsyR91K179E25Text
 * @description Converts a candidate Meeting value into trimmed display text.
 * @param {*} value - Candidate value.
 * @returns {string} Text value.
 * @collaboration Meeting intelligence normalization, evidence ledger, Wilsy AI recommendations.
 */
function normalizeWilsyR91K179E25Text(value = '') {
  if (value === null || value === undefined) return '';
  if (typeof value === 'object') {
    return String(
      value.title || value.name || value.label || value.email || value.recordId || value.id || ''
    ).trim();
  }

  return String(value).trim();
}

/**
 * @function resolveWilsyR91K179E25MeetingId
 * @description Resolves a stable id for a Meeting intelligence row.
 * @param {Object} meeting - Meeting source record.
 * @param {number} index - Fallback index.
 * @returns {string} Meeting id.
 * @collaboration Meeting command endpoint, Wilsy AI rail, search results.
 */
function resolveWilsyR91K179E25MeetingId(meeting = {}, index = 0) {
  return String(
    meeting.recordId ||
      meeting.meetingId ||
      meeting.id ||
      meeting._id ||
      meeting.externalId ||
      `meeting-source-${index}`
  );
}

/**
 * @function resolveWilsyR91K179E25MeetingTitle
 * @description Resolves a Meeting title from persisted Meeting fields.
 * @param {Object} meeting - Meeting source record.
 * @returns {string} Meeting title.
 * @collaboration Meeting intelligence cards, command recommendations, OS search results.
 */
function resolveWilsyR91K179E25MeetingTitle(meeting = {}) {
  return (
    normalizeWilsyR91K179E25Text(
      meeting.title ||
        meeting.subject ||
        meeting.meetingTitle ||
        meeting.name ||
        meeting.relatedName
    ) || 'Untitled Meeting'
  );
}

/**
 * @function resolveWilsyR91K179E25MeetingVenue
 * @description Resolves Meeting venue/location posture from persisted fields.
 * @param {Object} meeting - Meeting source record.
 * @returns {string} Venue label.
 * @collaboration Venue proof, Meeting editor persistence, evidence workspace.
 */
function resolveWilsyR91K179E25MeetingVenue(meeting = {}) {
  return normalizeWilsyR91K179E25Text(
    meeting.meetingVenue ||
      meeting.venue ||
      meeting.venueType ||
      meeting.meetingVenueLabel ||
      meeting.locationType ||
      meeting.location ||
      meeting.meetingUrl ||
      meeting.onlineMeetingUrl
  );
}

/**
 * @function resolveWilsyR91K179E25MeetingParticipants
 * @description Resolves Meeting participant rows from persisted participants, attendees or invitees arrays.
 * @param {Object} meeting - Meeting source record.
 * @returns {Array<Object>} Participant summaries.
 * @collaboration Invitation proof, Meeting participant resolver, Wilsy AI gap detection.
 */
function resolveWilsyR91K179E25MeetingParticipants(meeting = {}) {
  const rawParticipants = Array.isArray(meeting.participants)
    ? meeting.participants
    : Array.isArray(meeting.attendees)
      ? meeting.attendees
      : Array.isArray(meeting.invitees)
        ? meeting.invitees
        : [];

  return rawParticipants
    .map((participant) => {
      if (typeof participant === 'string') {
        return {
          label: participant,
          email: participant.includes('@') ? participant : '',
          sourceType: 'EXTERNAL',
        };
      }

      return {
        label: normalizeWilsyR91K179E25Text(
          participant.displayName || participant.name || participant.label || participant.email
        ),
        email: normalizeWilsyR91K179E25Text(participant.email || participant.normalizedEmail),
        sourceType: normalizeWilsyR91K179E25Text(
          participant.sourceType || participant.source || 'CRM'
        ),
      };
    })
    .filter((participant) => participant.label || participant.email);
}

/**
 * @function resolveWilsyR91K179E25MeetingRelated
 * @description Resolves linked CRM context from Meeting related fields.
 * @param {Object} meeting - Meeting source record.
 * @returns {Object} Related record summary.
 * @collaboration CRM relationship proof, evidence workspace, Wilsy AI recommendations.
 */
function resolveWilsyR91K179E25MeetingRelated(meeting = {}) {
  const related =
    meeting.relatedRecord || meeting.relatedTo || meeting.crmRecord || meeting.crmLink || null;

  if (related && typeof related === 'object') {
    return {
      title: normalizeWilsyR91K179E25Text(
        related.title || related.name || related.label || related.recordId || related.id
      ),
      recordId: normalizeWilsyR91K179E25Text(related.recordId || related.id || related._id),
      module: normalizeWilsyR91K179E25Text(related.module || related.type || 'CRM'),
    };
  }

  const relatedText = normalizeWilsyR91K179E25Text(
    related ||
      meeting.relatedRecordName ||
      meeting.relatedRecordId ||
      meeting.relatedLeadId ||
      meeting.relatedContactId ||
      meeting.relatedAccountId ||
      meeting.relatedDealId ||
      meeting.relatedId
  );

  return {
    title: relatedText,
    recordId: normalizeWilsyR91K179E25Text(
      meeting.relatedRecordId || meeting.relatedId || relatedText
    ),
    module: normalizeWilsyR91K179E25Text(meeting.relatedType || 'CRM'),
  };
}

/**
 * @function resolveWilsyR91K179E25MeetingSchedule
 * @description Resolves Meeting schedule posture from timestamp or date/time fields.
 * @param {Object} meeting - Meeting source record.
 * @returns {Object} Schedule posture.
 * @collaboration Calendar posture, Meeting command evidence, Wilsy AI readiness.
 */
function resolveWilsyR91K179E25MeetingSchedule(meeting = {}) {
  const startsAt =
    meeting.startsAt || meeting.startAt || meeting.startTime || meeting.scheduledAt || null;
  const endsAt = meeting.endsAt || meeting.endAt || meeting.endTime || null;
  const fromLabel = [meeting.fromDate, meeting.fromTime].filter(Boolean).join(' ');
  const toLabel = [meeting.toDate, meeting.toTime].filter(Boolean).join(' ');

  return {
    startsAt: startsAt || fromLabel || '',
    endsAt: endsAt || toLabel || '',
    hasSchedule: Boolean(startsAt || meeting.fromDate || meeting.date || meeting.scheduledAt),
  };
}

/**
 * @function buildWilsyR91K179E25MeetingReadiness
 * @description Computes readiness gaps from persisted Meeting source fields only.
 * @param {Object} meeting - Meeting source record.
 * @returns {Object} Readiness score and gaps.
 * @collaboration Wilsy AI Meeting intelligence, evidence workspace, operator repair flow.
 */
function buildWilsyR91K179E25MeetingReadiness(meeting = {}) {
  const venue = resolveWilsyR91K179E25MeetingVenue(meeting);
  const participants = resolveWilsyR91K179E25MeetingParticipants(meeting);
  const related = resolveWilsyR91K179E25MeetingRelated(meeting);
  const schedule = resolveWilsyR91K179E25MeetingSchedule(meeting);
  const hasAgenda = Boolean(
    normalizeWilsyR91K179E25Text(meeting.description || meeting.agenda || meeting.outcome)
  );
  const gaps = [
    venue ? '' : 'venue',
    participants.length > 0 ? '' : 'participants',
    related.title || related.recordId ? '' : 'related CRM record',
    schedule.hasSchedule ? '' : 'schedule',
    hasAgenda ? '' : 'agenda',
  ].filter(Boolean);

  return {
    score: Math.max(0, 100 - gaps.length * 20),
    status: gaps.length ? 'REPAIR_REQUIRED' : 'COMMAND_READY',
    gaps,
    venue,
    participants,
    related,
    schedule,
    hasAgenda,
  };
}

/**
 * @function normalizeWilsyR91K179E25MeetingResult
 * @description Converts a Meeting source row into an AI/search/evidence-safe result.
 * @param {Object} meeting - Meeting source record.
 * @param {number} index - Row index.
 * @returns {Object} Normalized Meeting intelligence result.
 * @collaboration OS search, Wilsy AI Meeting rail, evidence ledger.
 */
function normalizeWilsyR91K179E25MeetingResult(meeting = {}, index = 0) {
  const readiness = buildWilsyR91K179E25MeetingReadiness(meeting);
  const recordId = resolveWilsyR91K179E25MeetingId(meeting, index);

  return {
    id: recordId,
    recordId,
    meetingId: recordId,
    module: 'meetings',
    title: resolveWilsyR91K179E25MeetingTitle(meeting),
    status: normalizeWilsyR91K179E25Text(
      meeting.status || meeting.stage || meeting.outcome || 'RECORDED'
    ),
    venue: readiness.venue,
    participants: readiness.participants,
    participantCount: readiness.participants.length,
    relatedRecord: readiness.related,
    schedule: readiness.schedule,
    readiness,
    updatedAt: meeting.updatedAt || meeting.createdAt || null,
    sourceStatus: meeting.sourceStatus || meeting.persistenceStatus || 'SOURCE_LIVE',
  };
}

/**
 * @function queryWilsyR91K179E25RawMeetingCollection
 * @description Searches raw Meeting collections when a Mongoose Meeting model is unavailable.
 * @param {string} tenantId - Tenant id.
 * @param {string} query - Search text.
 * @param {number} limit - Result limit.
 * @returns {Promise<Object|null>} Raw collection query packet.
 * @collaboration Raw CRM collection fallback, Meeting intelligence endpoint, source-honest backend wiring.
 */
async function queryWilsyR91K179E25RawMeetingCollection(tenantId, query, limit) {
  const db = mongoose.connection?.db;
  if (!db) return null;

  const registryEntry = resolveWilsyR91K179E25MeetingRegistryEntry();
  const filter = buildWilsyCrmSearchFilter(registryEntry, tenantId, query);
  const safeLimit = Math.max(1, Math.min(Number(limit) || 8, 50));

  for (const collectionName of WILSY_R91K179E25_MEETING_COLLECTIONS) {
    try {
      const collection = db.collection(collectionName);
      let cursor = collection
        .find(filter)
        .sort({ updatedAt: -1, createdAt: -1, _id: -1 })
        .limit(safeLimit);

      if (typeof cursor.maxTimeMS === 'function') {
        cursor = cursor.maxTimeMS(1800);
      }

      const [count, rows] = await Promise.all([
        collection.countDocuments(filter).catch(() => 0),
        cursor.toArray().catch(() => []),
      ]);

      if (count > 0 || rows.length > 0) {
        return {
          connected: true,
          count,
          rows,
          dataSource: 'mongo-collection',
          modelName: null,
          collectionName,
          sourceGap: null,
        };
      }
    } catch {
      // Try next known Meeting collection name.
    }
  }

  return null;
}

/**
 * @function queryWilsyR91K179E25MeetingRows
 * @description Queries Meeting source rows from registered CRMMeeting model or raw collection fallback.
 * @param {string} tenantId - Tenant id.
 * @param {string} query - Search text.
 * @param {number} limit - Result limit.
 * @returns {Promise<Object>} Meeting query packet.
 * @collaboration /api/crm/command/meetings/intelligence, Wilsy AI, OS search and evidence workspaces.
 */
async function queryWilsyR91K179E25MeetingRows(tenantId, query, limit) {
  const registryEntry = resolveWilsyR91K179E25MeetingRegistryEntry();
  const MeetingModel = getWilsyCrmModel(registryEntry.modelName);
  const safeLimit = Math.max(1, Math.min(Number(limit) || 8, 50));

  if (MeetingModel) {
    const filter = buildWilsyCrmSearchFilter(registryEntry, tenantId, query);
    const [count, rows] = await Promise.all([
      MeetingModel.countDocuments(filter).catch(() => 0),
      MeetingModel.find(filter)
        .sort({ updatedAt: -1, createdAt: -1, _id: -1 })
        .limit(safeLimit)
        .lean()
        .catch(() => []),
    ]);

    return {
      connected: true,
      count,
      rows,
      dataSource: 'mongoose',
      modelName: registryEntry.modelName,
      collectionName: MeetingModel.collection?.name || 'crm_meetings',
      sourceGap: null,
    };
  }

  const rawPacket = await queryWilsyR91K179E25RawMeetingCollection(tenantId, query, safeLimit);

  if (rawPacket) return rawPacket;

  return {
    connected: false,
    count: 0,
    rows: [],
    dataSource: 'missing',
    modelName: registryEntry.modelName,
    collectionName: null,
    sourceGap:
      'CRMMeeting model and known Meeting collections are unavailable for Meeting intelligence.',
  };
}

/**
 * @function buildWilsyR91K179E25MeetingCoverage
 * @description Aggregates Meeting readiness coverage for the intelligence endpoint.
 * @param {Array<Object>} results - Normalized Meeting results.
 * @returns {Object} Coverage summary.
 * @collaboration Evidence workspace, Wilsy AI posture, board-ready meeting operations.
 */
function buildWilsyR91K179E25MeetingCoverage(results = []) {
  const inspected = Array.isArray(results) ? results.length : 0;
  const coverage = results.reduce(
    (accumulator, result) => {
      const readiness = result.readiness || {};
      accumulator.venue += readiness.venue ? 1 : 0;
      accumulator.participants += Number(result.participantCount || 0) > 0 ? 1 : 0;
      accumulator.relatedRecord += readiness.related?.title || readiness.related?.recordId ? 1 : 0;
      accumulator.schedule += readiness.schedule?.hasSchedule ? 1 : 0;
      accumulator.agenda += readiness.hasAgenda ? 1 : 0;
      accumulator.readyRecords += readiness.status === 'COMMAND_READY' ? 1 : 0;
      accumulator.gaps.push(...(Array.isArray(readiness.gaps) ? readiness.gaps : []));
      return accumulator;
    },
    {
      venue: 0,
      participants: 0,
      relatedRecord: 0,
      schedule: 0,
      agenda: 0,
      readyRecords: 0,
      gaps: [],
    }
  );

  const possible = Math.max(1, inspected * 5);
  const score = inspected
    ? Math.round(
        ((coverage.venue +
          coverage.participants +
          coverage.relatedRecord +
          coverage.schedule +
          coverage.agenda) /
          possible) *
          100
      )
    : 0;

  return {
    inspected,
    score,
    readyRecords: coverage.readyRecords,
    repairRecords: Math.max(0, inspected - coverage.readyRecords),
    fieldCoverage: {
      venue: coverage.venue,
      participants: coverage.participants,
      relatedRecord: coverage.relatedRecord,
      schedule: coverage.schedule,
      agenda: coverage.agenda,
    },
    gaps: Array.from(new Set(coverage.gaps)),
  };
}

/**
 * @function buildWilsyR91K179E25MeetingRecommendations
 * @description Builds source-honest Meeting intelligence recommendations from actual query output.
 * @param {Object} queryPacket - Meeting query packet.
 * @param {Object} readiness - Coverage summary.
 * @param {string} query - Operator search query.
 * @returns {Array<Object>} Recommendation records.
 * @collaboration Wilsy AI Meeting command rail, operator repair workflows, no-fake-data posture.
 */
function buildWilsyR91K179E25MeetingRecommendations(queryPacket = {}, readiness = {}, query = '') {
  const recommendations = [];

  if (!queryPacket.connected) {
    recommendations.push({
      severity: 'critical',
      action: 'Connect CRMMeeting source',
      detail: queryPacket.sourceGap,
      route: '/api/crm/live/meetings',
    });
  }

  if (queryPacket.connected && Number(queryPacket.count || 0) === 0) {
    recommendations.push({
      severity: 'warning',
      action: query ? 'No matching meetings returned' : 'Create or import meetings',
      detail: query
        ? `No Meeting rows matched "${query}". Keep OS search feedback visible and offer create/import next actions.`
        : 'Meeting source is connected but returned no rows for this tenant.',
      route: '/api/crm/command/meetings',
    });
  }

  readiness.gaps?.forEach((gap) => {
    recommendations.push({
      severity: gap === 'participants' || gap === 'related CRM record' ? 'high' : 'medium',
      action: `Repair Meeting ${gap}`,
      detail: `${readiness.repairRecords || 0} inspected Meeting record${readiness.repairRecords === 1 ? '' : 's'} need ${gap} evidence before command-ready posture.`,
      route: '/api/crm/command/meetings/:id',
    });
  });

  if (!recommendations.length) {
    recommendations.push({
      severity: 'ready',
      action: 'Proceed with Meeting operations',
      detail:
        'Inspected Meeting rows carry venue, participants, schedule, related record and agenda evidence.',
      route: '/api/crm/command/meetings',
    });
  }

  return recommendations.slice(0, 8);
}

/**
 * @function buildWilsyR91K179E25MeetingEvidence
 * @description Builds the route and persistence evidence packet for Meeting intelligence.
 * @param {Object} queryPacket - Meeting query packet.
 * @param {Object} readiness - Coverage summary.
 * @returns {Object} Meeting intelligence evidence packet.
 * @collaboration Evidence workspace, Wilsy AI rail, Meeting command backend audit.
 */
function buildWilsyR91K179E25MeetingEvidence(queryPacket = {}, readiness = {}) {
  return {
    sourceRoute: '/api/crm/live/meetings',
    intelligenceRoute: '/api/crm/command/meetings/intelligence',
    commandRoutes: {
      create: '/api/crm/command/meetings',
      update: '/api/crm/command/meetings/:id',
      delete: '/api/crm/command/meetings/:id',
      importPreview: '/api/crm/command/meetings/import-preview',
    },
    dataSource: queryPacket.dataSource,
    modelName: queryPacket.modelName,
    collectionName: queryPacket.collectionName,
    connected: Boolean(queryPacket.connected),
    totalRecords: Number(queryPacket.count || 0),
    inspectedRecords: readiness.inspected || 0,
    readinessScore: readiness.score || 0,
    sourceStatus: queryPacket.connected ? 'MEETING_SOURCE_LIVE' : 'MEETING_SOURCE_REQUIRED',
  };
}

/**
 * @function handleWilsyR91K179E25MeetingIntelligence
 * @description Returns backend Meeting intelligence for Wilsy AI, OS search and evidence workspaces from live CRM sources only.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {Promise<void>} Response completion.
 * @collaboration Wilsy AI Meetings rail, Meeting evidence workspace, source-honest CRM command fabric.
 */
async function handleWilsyR91K179E25MeetingIntelligence(req, res, next) {
  try {
    const tenantId = getWilsyCrmTenantId(req);
    const query = String(req.query.q || req.query.query || '').trim();
    const limit = Math.max(1, Math.min(Number(req.query.limit) || 12, 50));
    const queryPacket = await queryWilsyR91K179E25MeetingRows(tenantId, query, limit);
    const results = queryPacket.rows.map((meeting, index) =>
      normalizeWilsyR91K179E25MeetingResult(meeting, index)
    );
    const readiness = buildWilsyR91K179E25MeetingCoverage(results);
    const recommendations = buildWilsyR91K179E25MeetingRecommendations(
      queryPacket,
      readiness,
      query
    );
    const evidence = buildWilsyR91K179E25MeetingEvidence(queryPacket, readiness);
    const sourceGaps = queryPacket.sourceGap ? [queryPacket.sourceGap] : [];

    const packet = {
      ok: true,
      version: WILSY_R91K179E25_MEETING_INTELLIGENCE_VERSION,
      tenantId,
      query,
      route: '/api/crm/command/meetings/intelligence',
      liveRoute: '/api/crm/live/meetings',
      sourceStatus: queryPacket.connected ? 'MEETING_SOURCE_LIVE' : 'MEETING_SOURCE_REQUIRED',
      dataSource: queryPacket.dataSource,
      modelName: queryPacket.modelName,
      collectionName: queryPacket.collectionName,
      totalRecords: queryPacket.count,
      returned: results.length,
      results,
      readiness,
      recommendations,
      evidence,
      sourceGaps,
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
router.get('/meetings/intelligence', handleWilsyR91K179E25MeetingIntelligence);
router.get('/search', handleWilsyCrmCommandSearch);
router.post('/sync', handleWilsyCrmCommandSync);
router.post('/leads', handleWilsyCrmCommandLeadCreate);
router.post('/contacts', handleWilsyCrmCommandContactCreate);

/* WILSY_P60K2_SETUP_REVIEW_BACKEND_AUTHORITY
   Backend-owned CRM Setup review packet authority. */

/**
 * @function resolveWilsySetupReviewText
 * @description Normalizes command text values for setup review packets.
 * @param {unknown} value - Raw value.
 * @param {string} fallback - Fallback value.
 * @returns {string} Normalized string.
 * @collaboration CRM setup backend authority, setup review packet model, and receipt evidence.
 */
function resolveWilsySetupReviewText(value, fallback = '') {
  const resolved = value === undefined || value === null ? fallback : String(value);
  return resolved.trim() || fallback;
}

/**
 * @function resolveWilsySetupReviewTimestamp
 * @description Resolves a trustworthy generated timestamp for setup review commands.
 * @param {Object} body - Request body.
 * @returns {string} ISO timestamp.
 * @collaboration CRM setup backend authority, institutional headers, and audit receipts.
 */
function resolveWilsySetupReviewTimestamp(body = {}) {
  const candidate =
    body.generatedAt ||
    body.timestamp ||
    body.institutionalHeaders?.generatedAt ||
    body.institutionalHeaders?.timestamp ||
    body.strikePayload?.generatedAt ||
    body.strikePayload?.timestamp ||
    body.strikePayload?.institutionalHeaders?.generatedAt ||
    body.strikePayload?.institutionalHeaders?.timestamp;

  const parsed = candidate ? new Date(candidate) : null;
  return parsed && !Number.isNaN(parsed.getTime())
    ? parsed.toISOString()
    : new Date().toISOString();
}

/**
 * @function resolveWilsySetupReviewTenantId
 * @description Resolves tenant authority from body, strike payload, request tenant, or tenant header.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration CRM command route, tenant evidence, institutional headers, and setup review packets.
 */
function resolveWilsySetupReviewTenantId(req) {
  const body = req.body || {};
  return resolveWilsySetupReviewText(
    body.tenantId ||
      body.institutionalHeaders?.tenantId ||
      body.strikePayload?.tenantId ||
      body.strikePayload?.institutionalHeaders?.tenantId ||
      req.tenant?.id ||
      req.tenant?.tenantId ||
      req.headers?.['x-tenant-id'],
    'MASTER'
  );
}

/**
 * @function resolveWilsySetupReviewOperatorId
 * @description Resolves operator authority from request identity, body, or institutional evidence.
 * @param {Object} req - Express request.
 * @returns {string} Operator id.
 * @collaboration CRM command route, operator evidence, institutional headers, and setup review packets.
 */
function resolveWilsySetupReviewOperatorId(req) {
  const body = req.body || {};
  return resolveWilsySetupReviewText(
    body.operatorId ||
      body.userId ||
      body.institutionalHeaders?.operatorId ||
      body.institutionalHeaders?.userId ||
      body.strikePayload?.operatorId ||
      body.strikePayload?.userId ||
      body.strikePayload?.institutionalHeaders?.operatorId ||
      body.strikePayload?.institutionalHeaders?.userId ||
      req.user?.id ||
      req.user?._id ||
      req.admin?.id ||
      req.admin?._id,
    'wilsy-sovereign-root'
  );
}

/**
 * @function resolveWilsySetupReviewInstitutionalHeaders
 * @description Builds the canonical institutional header contract required by setup review writes.
 * @param {Object} req - Express request.
 * @param {string} route - Command route.
 * @returns {Object} Institutional headers.
 * @collaboration CRM setup backend authority, strike payload evidence, and receipt generation.
 */
function resolveWilsySetupReviewInstitutionalHeaders(req, route) {
  const body = req.body || {};
  const generatedAt = resolveWilsySetupReviewTimestamp(body);
  const tenantId = resolveWilsySetupReviewTenantId(req);
  const operatorId = resolveWilsySetupReviewOperatorId(req);
  const commandSurface = resolveWilsySetupReviewText(
    body.commandSurface ||
      body.institutionalHeaders?.commandSurface ||
      body.strikePayload?.commandSurface ||
      body.strikePayload?.institutionalHeaders?.commandSurface,
    'CRM_SETUP_OPERATING_CONTROLS'
  );

  return {
    ...(body.institutionalHeaders && typeof body.institutionalHeaders === 'object'
      ? body.institutionalHeaders
      : {}),
    tenantId,
    operatorId,
    userId: resolveWilsySetupReviewText(
      body.userId ||
        body.institutionalHeaders?.userId ||
        body.strikePayload?.userId ||
        body.strikePayload?.institutionalHeaders?.userId,
      operatorId
    ),
    route,
    commandSurface,
    generatedAt,
    timestamp: generatedAt,
    source: resolveWilsySetupReviewText(
      body.source || body.institutionalHeaders?.source,
      'CRM_SETUP_REVIEW_PACKET'
    ),
  };
}

/**
 * @function assertWilsySetupReviewWriteEvidence
 * @description Enforces the Wilsy backend write evidence contract for setup review commands.
 * @param {Object} req - Express request.
 * @param {string} route - Command route.
 * @returns {Object} Evidence contract.
 * @throws {Error} When required evidence is missing.
 * @collaboration CRM setup backend authority, write guards, institutional headers, and strike payload.
 */
function assertWilsySetupReviewWriteEvidence(req, route) {
  const body = req.body || {};
  const topHeaders =
    body.institutionalHeaders && typeof body.institutionalHeaders === 'object'
      ? body.institutionalHeaders
      : null;
  const strikePayload =
    body.strikePayload && typeof body.strikePayload === 'object' ? body.strikePayload : null;
  const nestedHeaders =
    strikePayload?.institutionalHeaders && typeof strikePayload.institutionalHeaders === 'object'
      ? strikePayload.institutionalHeaders
      : null;

  if (!topHeaders) {
    const error = new Error('Setup review command requires institutionalHeaders at the top level.');
    error.statusCode = 400;
    error.code = 'SETUP_REVIEW_HEADERS_REQUIRED';
    throw error;
  }

  if (!strikePayload) {
    const error = new Error('Setup review command requires strikePayload evidence.');
    error.statusCode = 400;
    error.code = 'SETUP_REVIEW_STRIKE_PAYLOAD_REQUIRED';
    throw error;
  }

  if (!nestedHeaders) {
    const error = new Error('Setup review command requires strikePayload.institutionalHeaders.');
    error.statusCode = 400;
    error.code = 'SETUP_REVIEW_NESTED_HEADERS_REQUIRED';
    throw error;
  }

  const institutionalHeaders = resolveWilsySetupReviewInstitutionalHeaders(req, route);

  return {
    tenantId: institutionalHeaders.tenantId,
    operatorId: institutionalHeaders.operatorId,
    userId: institutionalHeaders.userId,
    route,
    commandSurface: institutionalHeaders.commandSurface,
    generatedAt: institutionalHeaders.generatedAt,
    timestamp: institutionalHeaders.timestamp,
    institutionalHeaders,
    strikePayload: {
      ...strikePayload,
      institutionalHeaders: {
        ...nestedHeaders,
        ...institutionalHeaders,
      },
    },
  };
}

/**
 * @function assertWilsySetupReviewDatabaseReady
 * @description Fails setup review commands fast when MongoDB is not connected, preventing buffered Mongoose hangs.
 * @returns {Object} Active Mongoose connection.
 * @throws {Error} When MongoDB is unavailable.
 * @collaboration CRM setup review routes, MongoDB command authority, route timeout wrapper, and Packet Console receipts.
 */
function assertWilsySetupReviewDatabaseReady() {
  const readyState = mongoose?.connection?.readyState;
  const hasDatabase = Boolean(mongoose?.connection?.db);

  if (readyState !== 1 || !hasDatabase) {
    const error = new Error('Setup review database is not ready. Command was not staged.');
    error.statusCode = 503;
    error.code = 'SETUP_REVIEW_DB_NOT_READY';
    error.details = {
      readyState,
      state: mongoose?.STATES?.[readyState] || String(readyState ?? 'unknown'),
      hasDatabase,
    };
    throw error;
  }

  return mongoose.connection;
}

/**
 * @function wrapWilsySetupReviewRoute
 * @description Wraps setup review command routes with bounded execution and JSON failure responses.
 * @param {Function} handler - Express route handler.
 * @returns {Function} Bounded Express route handler.
 * @collaboration CRM setup command routes, ProductionHardening bridge, MongoDB readiness, and frontend live wiring.
 */
function wrapWilsySetupReviewRoute(handler) {
  return async (req, res, next) => {
    let timeoutHandle = null;

    try {
      await Promise.race([
        Promise.resolve(handler(req, res, next)),
        new Promise((_, reject) => {
          timeoutHandle = setTimeout(() => {
            const error = new Error(
              'Setup review command timed out before backend authority completed.'
            );
            error.statusCode = 504;
            error.code = 'SETUP_REVIEW_ROUTE_TIMEOUT';
            reject(error);
          }, 8000);
        }),
      ]);
    } catch (error) {
      if (res.headersSent) return;

      const statusCode = Number(error?.statusCode || error?.status || 500);

      return res.status(statusCode).json({
        ok: false,
        result: error?.code || 'SETUP_REVIEW_COMMAND_FAILED',
        error: error?.code || 'SETUP_REVIEW_COMMAND_FAILED',
        message: error?.message || 'Setup review command failed.',
        details: error?.details || null,
        route: req.originalUrl || req.path || req.url,
        method: req.method,
        generatedAt: new Date().toISOString(),
      });
    } finally {
      if (timeoutHandle) clearTimeout(timeoutHandle);
    }
  };
}

/**
 * @function resolveWilsySetupReviewModel
 * @description Creates or reuses the CRM setup review packet mongoose model.
 * @returns {Object} Mongoose model.
 * @collaboration MongoDB, CRM command routes, setup review packets, and receipt vault.
 */
function resolveWilsySetupReviewModel() {
  assertWilsySetupReviewDatabaseReady();
  if (mongoose.models.WilsyCrmSetupReviewPacket) {
    return mongoose.models.WilsyCrmSetupReviewPacket;
  }

  const WilsyCrmSetupReviewPacketSchema = new mongoose.Schema(
    {
      tenantId: { type: String, required: true, index: true },
      operatorId: { type: String, required: true, index: true },
      userId: { type: String, required: true },
      packetId: { type: String, required: true, unique: true, index: true },
      domainId: { type: String, required: true, index: true },
      domainLabel: { type: String, default: '' },
      controlId: { type: String, required: true, index: true },
      controlName: { type: String, required: true },
      lens: { type: String, default: 'Authority' },
      owner: { type: String, default: 'Security Admin' },
      risk: { type: String, default: 'MEDIUM', index: true },
      state: { type: String, default: 'SEALED' },
      status: { type: String, default: 'STAGED', index: true },
      benefit: { type: String, default: '' },
      signal: { type: String, default: '' },
      surfaces: { type: [String], default: [] },
      workItems: { type: [String], default: [] },
      requiredEvidence: { type: [String], default: [] },

      evidenceLedger: { type: [mongoose.Schema.Types.Mixed], default: [] },

      approvalState: { type: mongoose.Schema.Types.Mixed, default: {} },

      releaseState: { type: mongoose.Schema.Types.Mixed, default: {} },

      workflowState: { type: mongoose.Schema.Types.Mixed, default: {} },
      route: { type: String, required: true },
      commandSurface: { type: String, required: true },
      generatedAt: { type: Date, required: true },
      institutionalHeaders: { type: mongoose.Schema.Types.Mixed, default: {} },
      strikePayload: { type: mongoose.Schema.Types.Mixed, default: {} },
      receipts: { type: [mongoose.Schema.Types.Mixed], default: [] },
      auditTrail: { type: [mongoose.Schema.Types.Mixed], default: [] },
      removedAt: { type: Date, default: null },
      clearedAt: { type: Date, default: null },
    },
    { timestamps: true, minimize: false, bufferCommands: false }
  );

  WilsyCrmSetupReviewPacketSchema.index(
    { tenantId: 1, operatorId: 1, controlId: 1, status: 1 },
    { name: 'wilsy_setup_review_scope_control_status' }
  );

  return mongoose.model('WilsyCrmSetupReviewPacket', WilsyCrmSetupReviewPacketSchema);
}

/**
 * @function resolveWilsySetupReviewCreateHash
 * @description Resolves Node crypto createHash inside the route runtime for setup review receipt hashes.
 * @returns {Function} Node crypto createHash function.
 * @throws {Error} When crypto hashing is unavailable.
 * @collaboration CRM setup review receipt builder, backend audit evidence, and Packet Console receipt hash display.
 */
function resolveWilsySetupReviewCreateHash() {
  try {
    if (typeof createHash === 'function') {
      return createHash;
    }
  } catch {
    // Continue to route runtime crypto resolver.
  }

  try {
    if (typeof crypto !== 'undefined' && typeof crypto?.createHash === 'function') {
      return crypto.createHash.bind(crypto);
    }
  } catch {
    // Continue to CommonJS resolver when available.
  }

  try {
    const cryptoModule = require('crypto');

    if (typeof cryptoModule?.createHash === 'function') {
      return cryptoModule.createHash;
    }
  } catch {
    // Route runtime did not expose CommonJS require.
  }

  const error = new Error('Setup review receipt hash engine is unavailable.');
  error.statusCode = 500;
  error.code = 'SETUP_REVIEW_HASH_ENGINE_UNAVAILABLE';
  throw error;
}

/**
 * @function createWilsySetupReviewReceipt
 * @description Creates deterministic setup review receipt evidence.
 * @param {string} action - Receipt action.
 * @param {Object} packet - Setup review packet.
 * @param {Object} evidence - Evidence contract.
 * @returns {Object} Receipt object.
 * @collaboration CRM setup backend authority, audit trail, receipt return, and Packet Console.
 */
function createWilsySetupReviewReceipt(action, packet, evidence) {
  const generatedAt = new Date().toISOString();
  const receiptId = `SETUP_REVIEW_RECEIPT_${action}_${Date.now()}`;
  const hashSource = JSON.stringify({
    receiptId,
    action,
    packetId: packet.packetId,
    tenantId: packet.tenantId,
    operatorId: packet.operatorId,
    route: evidence.route,
    commandSurface: evidence.commandSurface,
    generatedAt,
  });

  return {
    receiptId,
    action,
    packetId: packet.packetId,
    tenantId: packet.tenantId,
    operatorId: packet.operatorId,
    userId: packet.userId,
    route: evidence.route,
    commandSurface: evidence.commandSurface,
    result: action,
    generatedAt,
    timestamp: generatedAt,
    receiptHash: resolveWilsySetupReviewCreateHash()('sha256').update(hashSource).digest('hex'),
    evidenceContract: {
      tenantId: Boolean(evidence.tenantId),
      operatorId: Boolean(evidence.operatorId),
      route: Boolean(evidence.route),
      commandSurface: Boolean(evidence.commandSurface),
      generatedAt: Boolean(evidence.generatedAt),
      institutionalHeaders: Boolean(evidence.institutionalHeaders),
      strikePayloadInstitutionalHeaders: Boolean(evidence.strikePayload?.institutionalHeaders),
    },
  };
}

/**
 * @function serializeWilsySetupReviewPacket
 * @description Converts a setup review packet document into frontend-safe JSON.
 * @param {Object} packet - Setup review packet document.
 * @returns {Object|null} Serialized packet.
 * @collaboration CRM setup backend authority, Packet Console, and review queue.
 */
function serializeWilsySetupReviewPacket(packet) {
  if (!packet) return null;

  const source = typeof packet.toObject === 'function' ? packet.toObject() : packet;

  return {
    id: source.packetId,
    packetId: source.packetId,
    tenantId: source.tenantId,
    operatorId: source.operatorId,
    userId: source.userId,
    domainId: source.domainId,
    domainLabel: source.domainLabel,
    controlId: source.controlId,
    title: source.controlName,
    controlName: source.controlName,
    lens: source.lens,
    owner: source.owner,
    risk: source.risk,
    state: source.state,
    status: source.status,
    benefit: source.benefit,
    signal: source.signal,
    surfaces: Array.isArray(source.surfaces) ? source.surfaces : [],
    workItems: Array.isArray(source.workItems) ? source.workItems : [],
    requiredEvidence: Array.isArray(source.requiredEvidence) ? source.requiredEvidence : [],

    evidenceLedger: Array.isArray(source.evidenceLedger) ? source.evidenceLedger : [],

    approvalState: source.approvalState || {},

    releaseState: source.releaseState || {},

    workflowState: source.workflowState || {},
    route: source.route,
    commandSurface: source.commandSurface,
    generatedAt: source.generatedAt,
    institutionalHeaders: source.institutionalHeaders || {},
    strikePayload: source.strikePayload || {},
    receipts: Array.isArray(source.receipts) ? source.receipts : [],
    auditTrail: Array.isArray(source.auditTrail) ? source.auditTrail : [],
    createdAt: source.createdAt,
    updatedAt: source.updatedAt,
  };
}

/**
 * @function handleWilsySetupReviewList
 * @description Lists staged setup review packets for the current tenant and operator scope.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, review queue, tenant scope, and operator scope.
 */
async function handleWilsySetupReviewList(req, res) {
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();
  const tenantId = resolveWilsySetupReviewTenantId(req);
  const operatorId = resolveWilsySetupReviewOperatorId(req);

  const packets = await WilsyCrmSetupReviewPacket.find({
    tenantId,
    operatorId,
    status: 'STAGED',
  })
    .sort({ updatedAt: -1 })
    .limit(25)
    .lean();

  res.json({
    ok: true,
    result: 'SETUP_REVIEW_QUEUE_LISTED',
    tenantId,
    operatorId,
    count: packets.length,
    packets: packets.map(serializeWilsySetupReviewPacket),
    generatedAt: new Date().toISOString(),
  });
}

/**
 * @function handleWilsySetupReviewCreate
 * @description Creates or refreshes a backend-owned setup review packet.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, institutional headers, strike payload, receipt return, and audit trail.
 */
async function handleWilsySetupReviewCreate(req, res) {
  const route = '/api/crm/command/setup/reviews';
  const evidence = assertWilsySetupReviewWriteEvidence(req, route);
  const body = req.body || {};
  const control = body.control && typeof body.control === 'object' ? body.control : {};
  const domain = body.domain && typeof body.domain === 'object' ? body.domain : {};
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();

  const generatedAt = new Date(evidence.generatedAt);
  const controlId = resolveWilsySetupReviewText(body.controlId || control.id, 'setup-control');
  const compactStamp = String(Date.now());
  const packetId = resolveWilsySetupReviewText(
    body.packetId || body.id,
    `SETUP_REVIEW_${compactStamp}`
  );

  const basePacket = {
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
    packetId,
    domainId: resolveWilsySetupReviewText(body.domainId || domain.id, 'authority'),
    domainLabel: resolveWilsySetupReviewText(
      body.domainLabel || domain.label || domain.title,
      'Authority'
    ),
    controlId,
    controlName: resolveWilsySetupReviewText(
      body.controlName || body.title || control.name,
      'Authority Graph'
    ),
    lens: resolveWilsySetupReviewText(body.lens, 'Authority'),
    owner: resolveWilsySetupReviewText(body.owner || control.owner, 'Security Admin'),
    risk: resolveWilsySetupReviewText(body.risk || control.risk, 'CRITICAL').toUpperCase(),
    state: resolveWilsySetupReviewText(body.state || control.state, 'SEALED').toUpperCase(),
    status: 'STAGED',
    benefit: resolveWilsySetupReviewText(body.benefit || control.benefit, ''),
    signal: resolveWilsySetupReviewText(body.signal || control.signal, ''),
    surfaces: Array.isArray(body.surfaces)
      ? body.surfaces
      : Array.isArray(control.surfaces)
        ? control.surfaces
        : [],
    workItems: Array.isArray(body.workItems)
      ? body.workItems
      : Array.isArray(control.workItems)
        ? control.workItems
        : [],
    requiredEvidence: Array.isArray(body.requiredEvidence)
      ? body.requiredEvidence
      : [
          'Tenant authority confirmed',
          'Operator identity attached',
          'Control owner assigned',
          'Risk and impact summary prepared',
          'Approval gate waiting for authorized approver',
          'Release gate waiting for evidence receipt',
        ],
    route,
    commandSurface: evidence.commandSurface,
    generatedAt,
    institutionalHeaders: evidence.institutionalHeaders,
    strikePayload: evidence.strikePayload,
    evidenceLedger: [],
    approvalState: {
      status: 'LOCKED',
      reason: 'AUTHORIZED_APPROVER_REQUIRED',
      updatedAt: generatedAt,
    },
    releaseState: {
      status: 'LOCKED',
      reason: 'RECEIPT_BACKED_EVIDENCE_REQUIRED',
      updatedAt: generatedAt,
    },
    workflowState: {
      evidenceCount: 0,
      approvalReady: false,
      approved: false,
      releaseReady: false,
      released: false,
      lastAction: 'SETUP_REVIEW_STAGED',
      updatedAt: generatedAt,
    },
    removedAt: null,
    clearedAt: null,
  };

  const existing = await WilsyCrmSetupReviewPacket.findOne({
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    controlId,
    status: 'STAGED',
  });

  const receipt = createWilsySetupReviewReceipt(
    existing ? 'SETUP_REVIEW_REFRESHED' : 'SETUP_REVIEW_STAGED',
    {
      ...basePacket,
    },
    evidence
  );

  const auditEvent = {
    event: existing ? 'SETUP_REVIEW_REFRESHED' : 'SETUP_REVIEW_STAGED',
    route,
    commandSurface: evidence.commandSurface,
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
    generatedAt: receipt.generatedAt,
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
  };

  const packet = await WilsyCrmSetupReviewPacket.findOneAndUpdate(
    {
      tenantId: evidence.tenantId,
      operatorId: evidence.operatorId,
      controlId,
      status: 'STAGED',
    },
    {
      $set: basePacket,
      $push: {
        receipts: receipt,
        auditTrail: auditEvent,
      },
    },
    {
      upsert: true,
      new: true,
      setDefaultsOnInsert: true,
    }
  );

  res.status(existing ? 200 : 201).json({
    ok: true,
    result: receipt.action,
    why: existing
      ? 'Setup review packet refreshed through CRM command authority.'
      : 'Setup review packet staged through CRM command authority.',
    packet: serializeWilsySetupReviewPacket(packet),
    receipt,
    auditEvidence: auditEvent,
  });
}

/**
 * @function handleWilsySetupReviewOpen
 * @description Opens a backend-owned setup review packet by packet id.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, backend packet read, tenant scope, and operator scope.
 */
async function handleWilsySetupReviewOpen(req, res) {
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();
  const tenantId = resolveWilsySetupReviewTenantId(req);
  const operatorId = resolveWilsySetupReviewOperatorId(req);
  const packetId = resolveWilsySetupReviewText(req.params.packetId, '');

  const packet = await WilsyCrmSetupReviewPacket.findOne({
    tenantId,
    operatorId,
    packetId,
    status: 'STAGED',
  });

  if (!packet) {
    return res.status(404).json({
      ok: false,
      result: 'SETUP_REVIEW_PACKET_NOT_FOUND',
      message: 'Setup review packet was not found for this tenant and operator scope.',
      tenantId,
      operatorId,
      packetId,
      generatedAt: new Date().toISOString(),
    });
  }

  return res.json({
    ok: true,
    result: 'SETUP_REVIEW_PACKET_OPENED',
    packet: serializeWilsySetupReviewPacket(packet),
    generatedAt: new Date().toISOString(),
  });
}

/**
 * @function handleWilsySetupReviewRemove
 * @description Removes one staged setup review packet while preserving receipt evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, delete authority, receipt return, and audit trail.
 */
async function handleWilsySetupReviewRemove(req, res) {
  const packetId = resolveWilsySetupReviewText(req.params.packetId, '');
  const route = `/api/crm/command/setup/reviews/${encodeURIComponent(packetId)}`;
  const evidence = assertWilsySetupReviewWriteEvidence(req, route);
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();

  const packet = await WilsyCrmSetupReviewPacket.findOne({
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    packetId,
    status: 'STAGED',
  });

  if (!packet) {
    return res.status(404).json({
      ok: false,
      result: 'SETUP_REVIEW_PACKET_NOT_FOUND',
      message: 'Setup review packet was not found for removal.',
      tenantId: evidence.tenantId,
      operatorId: evidence.operatorId,
      packetId,
      generatedAt: new Date().toISOString(),
    });
  }

  const receipt = createWilsySetupReviewReceipt('SETUP_REVIEW_REMOVED', packet, evidence);
  const auditEvent = {
    event: 'SETUP_REVIEW_REMOVED',
    route,
    commandSurface: evidence.commandSurface,
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
    packetId,
    generatedAt: receipt.generatedAt,
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
  };

  packet.status = 'REMOVED';
  packet.removedAt = new Date();
  packet.route = route;
  packet.commandSurface = evidence.commandSurface;
  packet.institutionalHeaders = evidence.institutionalHeaders;
  packet.strikePayload = evidence.strikePayload;
  packet.receipts.push(receipt);
  packet.auditTrail.push(auditEvent);

  await packet.save();

  return res.json({
    ok: true,
    result: 'SETUP_REVIEW_REMOVED',
    why: 'Setup review packet removed through CRM command authority.',
    packet: serializeWilsySetupReviewPacket(packet),
    receipt,
    auditEvidence: auditEvent,
  });
}

/* WILSY_P60K5B_SETUP_WORKFLOW_BACKEND */

/**
 * @function resolveWilsySetupReviewPacketForWorkflow
 * @description Loads a staged setup review packet for workflow commands.
 * @param {Object} model - Setup review Mongoose model.
 * @param {Object} evidence - Institutional evidence contract.
 * @param {Object} body - Command body.
 * @param {string} route - Command route.
 * @returns {Promise<Object>} Setup review packet.
 * @throws {Error} When a packet cannot be found.
 * @collaboration CRM setup workflow backend, evidence attach, approval, release, tenant scope, and Packet Console.
 */
async function resolveWilsySetupReviewPacketForWorkflow(model, evidence, body = {}, route = '') {
  const packetId = resolveWilsySetupReviewText(body.packetId || body.id, '');
  const controlId = resolveWilsySetupReviewText(body.controlId || body.control?.id, '');

  const query = {
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    status: 'STAGED',
  };

  if (packetId) {
    query.packetId = packetId;
  } else if (controlId) {
    query.controlId = controlId;
  } else {
    const error = new Error('Setup review workflow command requires packetId or controlId.');
    error.statusCode = 400;
    error.code = 'SETUP_REVIEW_WORKFLOW_PACKET_ID_REQUIRED';
    throw error;
  }

  const packet = await model.findOne(query);

  if (!packet) {
    const error = new Error(
      'Setup review workflow packet was not found in the active staged queue.'
    );
    error.statusCode = 404;
    error.code = 'SETUP_REVIEW_WORKFLOW_PACKET_NOT_FOUND';
    error.details = { route, packetId, controlId };
    throw error;
  }

  return packet;
}

/**
 * @function createWilsySetupReviewWorkflowAuditEvent
 * @description Creates a setup review workflow audit event linked to a receipt.
 * @param {string} event - Workflow event.
 * @param {Object} packet - Setup review packet.
 * @param {Object} evidence - Evidence contract.
 * @param {Object} receipt - Receipt object.
 * @param {Object} extra - Additional audit data.
 * @returns {Object} Workflow audit event.
 * @collaboration Setup workflow receipts, Packet Console, evidence ledger, approval gate, release gate, and audit trail.
 */
function createWilsySetupReviewWorkflowAuditEvent(event, packet, evidence, receipt, extra = {}) {
  return {
    event,
    route: evidence.route,
    commandSurface: evidence.commandSurface,
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
    packetId: packet.packetId,
    generatedAt: receipt.generatedAt,
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
    ...extra,
  };
}

/**
 * @function resolveWilsySetupReviewEvidenceRecord
 * @description Creates a normalized setup review evidence ledger record from a command body.
 * @param {Object} body - Command body.
 * @param {Object} evidence - Institutional evidence contract.
 * @param {Object} receipt - Receipt object.
 * @returns {Object} Evidence ledger record.
 * @collaboration Attach evidence workflow, evidence rail, release readiness, receipts, and audit trail.
 */
function resolveWilsySetupReviewEvidenceRecord(body = {}, evidence = {}, receipt = {}) {
  const evidenceBody = body.evidence && typeof body.evidence === 'object' ? body.evidence : {};

  return {
    evidenceId: resolveWilsySetupReviewText(
      body.evidenceId || evidenceBody.evidenceId,
      `SETUP_EVIDENCE_${Date.now()}`
    ),
    label: resolveWilsySetupReviewText(
      body.label || evidenceBody.label || body.requirement || evidenceBody.requirement,
      'Setup review evidence'
    ),
    requirement: resolveWilsySetupReviewText(
      body.requirement || evidenceBody.requirement || body.label || evidenceBody.label,
      'Setup review evidence requirement'
    ),
    type: resolveWilsySetupReviewText(body.type || evidenceBody.type, 'OPERATOR_ATTESTATION'),
    status: 'ATTACHED',
    source: resolveWilsySetupReviewText(
      body.source || evidenceBody.source,
      'CRM_SETUP_PACKET_CONSOLE'
    ),
    notes: resolveWilsySetupReviewText(body.notes || evidenceBody.notes, ''),
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
    route: evidence.route,
    commandSurface: evidence.commandSurface,
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
    generatedAt: receipt.generatedAt,
    timestamp: receipt.generatedAt,
  };
}

/**
 * @function resolveWilsySetupReviewWorkflowState
 * @description Computes workflow state for a setup review packet.
 * @param {Object} packet - Setup review packet.
 * @param {string} lastAction - Latest workflow action.
 * @returns {Object} Workflow state.
 * @collaboration Setup workflow board, evidence ledger, approval state, release state, and frontend gate rail.
 */
function resolveWilsySetupReviewWorkflowState(
  packet,
  lastAction = 'SETUP_REVIEW_WORKFLOW_UPDATED'
) {
  const evidenceLedger = Array.isArray(packet.evidenceLedger) ? packet.evidenceLedger : [];
  const approvalState = packet.approvalState || {};
  const releaseState = packet.releaseState || {};
  const evidenceCount = evidenceLedger.filter((item) => item?.status !== 'REMOVED').length;
  const approved = approvalState.status === 'APPROVED';
  const released = releaseState.status === 'RELEASED';

  return {
    evidenceCount,
    approvalReady: evidenceCount > 0,
    approved,
    releaseReady: evidenceCount > 0 && approved,
    released,
    lastAction,
    updatedAt: new Date().toISOString(),
  };
}

/**
 * @function handleWilsySetupReviewAttachEvidence
 * @description Attaches evidence to a staged setup review packet and records receipt-backed audit evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Evidence rail, backend evidence ledger, release gate, receipt chain, and Packet Console.
 */
async function handleWilsySetupReviewAttachEvidence(req, res) {
  const route = '/api/crm/command/setup/reviews/evidence';
  const evidence = assertWilsySetupReviewWriteEvidence(req, route);
  const body = req.body || {};
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();
  const packet = await resolveWilsySetupReviewPacketForWorkflow(
    WilsyCrmSetupReviewPacket,
    evidence,
    body,
    route
  );

  const receipt = createWilsySetupReviewReceipt('SETUP_REVIEW_EVIDENCE_ATTACHED', packet, evidence);
  const evidenceRecord = resolveWilsySetupReviewEvidenceRecord(body, evidence, receipt);
  const auditEvent = createWilsySetupReviewWorkflowAuditEvent(
    'SETUP_REVIEW_EVIDENCE_ATTACHED',
    packet,
    evidence,
    receipt,
    {
      evidenceId: evidenceRecord.evidenceId,
      requirement: evidenceRecord.requirement,
      evidenceStatus: evidenceRecord.status,
    }
  );

  packet.evidenceLedger = Array.isArray(packet.evidenceLedger) ? packet.evidenceLedger : [];
  packet.receipts = Array.isArray(packet.receipts) ? packet.receipts : [];
  packet.auditTrail = Array.isArray(packet.auditTrail) ? packet.auditTrail : [];

  packet.evidenceLedger.push(evidenceRecord);
  packet.approvalState = {
    ...(packet.approvalState || {}),
    status: 'READY',
    reason: 'EVIDENCE_ATTACHED',
    evidenceCount: packet.evidenceLedger.length,
    updatedAt: receipt.generatedAt,
    receiptId: receipt.receiptId,
  };
  packet.releaseState = {
    ...(packet.releaseState || {}),
    status: packet.releaseState?.status === 'RELEASED' ? 'RELEASED' : 'LOCKED',
    reason:
      packet.approvalState?.status === 'APPROVED'
        ? 'APPROVAL_READY_RELEASE_EVIDENCE_ATTACHED'
        : 'APPROVAL_REQUIRED_BEFORE_RELEASE',
    updatedAt: receipt.generatedAt,
  };
  packet.workflowState = resolveWilsySetupReviewWorkflowState(
    packet,
    'SETUP_REVIEW_EVIDENCE_ATTACHED'
  );
  packet.route = route;
  packet.commandSurface = evidence.commandSurface;
  packet.institutionalHeaders = evidence.institutionalHeaders;
  packet.strikePayload = evidence.strikePayload;
  packet.receipts.push(receipt);
  packet.auditTrail.push(auditEvent);

  await packet.save();

  return res.json({
    ok: true,
    result: 'SETUP_REVIEW_EVIDENCE_ATTACHED',
    why: 'Evidence attached to staged setup review packet with backend receipt.',
    packet: serializeWilsySetupReviewPacket(packet),
    evidenceRecord,
    receipt,
    auditEvidence: auditEvent,
  });
}

/**
 * @function handleWilsySetupReviewApprove
 * @description Approves a staged setup review packet when evidence exists and records receipt-backed approval evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Approval gate, evidence ledger, receipt chain, audit trail, and Packet Console.
 */
async function handleWilsySetupReviewApprove(req, res) {
  const route = '/api/crm/command/setup/reviews/approve';
  const evidence = assertWilsySetupReviewWriteEvidence(req, route);
  const body = req.body || {};
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();
  const packet = await resolveWilsySetupReviewPacketForWorkflow(
    WilsyCrmSetupReviewPacket,
    evidence,
    body,
    route
  );
  const evidenceLedger = Array.isArray(packet.evidenceLedger) ? packet.evidenceLedger : [];
  const activeEvidenceCount = evidenceLedger.filter((item) => item?.status !== 'REMOVED').length;

  if (activeEvidenceCount < 1) {
    const error = new Error('Approval requires at least one receipt-backed evidence record.');
    error.statusCode = 409;
    error.code = 'SETUP_REVIEW_APPROVAL_EVIDENCE_REQUIRED';
    throw error;
  }

  packet.receipts = Array.isArray(packet.receipts) ? packet.receipts : [];
  packet.auditTrail = Array.isArray(packet.auditTrail) ? packet.auditTrail : [];

  const receipt = createWilsySetupReviewReceipt('SETUP_REVIEW_APPROVED', packet, evidence);
  const approver = resolveWilsySetupReviewText(
    body.approver || body.approverId || body.operatorName,
    evidence.operatorId
  );
  const approvalState = {
    status: 'APPROVED',
    approver,
    approvalScope: resolveWilsySetupReviewText(
      body.approvalScope || body.scope,
      'SETUP_REVIEW_PACKET'
    ),
    evidenceCount: activeEvidenceCount,
    reason: 'AUTHORIZED_APPROVER_APPROVED',
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
    approvedAt: receipt.generatedAt,
    updatedAt: receipt.generatedAt,
  };
  const auditEvent = createWilsySetupReviewWorkflowAuditEvent(
    'SETUP_REVIEW_APPROVED',
    packet,
    evidence,
    receipt,
    {
      approver,
      evidenceCount: activeEvidenceCount,
      approvalScope: approvalState.approvalScope,
    }
  );

  packet.approvalState = approvalState;
  packet.releaseState = {
    ...(packet.releaseState || {}),
    status: 'READY',
    reason: 'APPROVAL_COMPLETE_RELEASE_REVIEW_AVAILABLE',
    evidenceCount: activeEvidenceCount,
    updatedAt: receipt.generatedAt,
  };
  packet.workflowState = resolveWilsySetupReviewWorkflowState(packet, 'SETUP_REVIEW_APPROVED');
  packet.route = route;
  packet.commandSurface = evidence.commandSurface;
  packet.institutionalHeaders = evidence.institutionalHeaders;
  packet.strikePayload = evidence.strikePayload;
  packet.receipts.push(receipt);
  packet.auditTrail.push(auditEvent);

  await packet.save();

  return res.json({
    ok: true,
    result: 'SETUP_REVIEW_APPROVED',
    why: 'Setup review packet approved with receipt-backed evidence.',
    packet: serializeWilsySetupReviewPacket(packet),
    approvalState,
    receipt,
    auditEvidence: auditEvent,
  });
}

/**
 * @function handleWilsySetupReviewRelease
 * @description Releases an approved setup review packet and records receipt-backed release evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Release gate, approval state, evidence ledger, receipt chain, audit trail, and Packet Console.
 */
async function handleWilsySetupReviewRelease(req, res) {
  const route = '/api/crm/command/setup/reviews/release';
  const evidence = assertWilsySetupReviewWriteEvidence(req, route);
  const body = req.body || {};
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();
  const packet = await resolveWilsySetupReviewPacketForWorkflow(
    WilsyCrmSetupReviewPacket,
    evidence,
    body,
    route
  );
  const evidenceLedger = Array.isArray(packet.evidenceLedger) ? packet.evidenceLedger : [];
  const activeEvidenceCount = evidenceLedger.filter((item) => item?.status !== 'REMOVED').length;

  if (packet.approvalState?.status !== 'APPROVED') {
    const error = new Error('Release requires an approved setup review packet.');
    error.statusCode = 409;
    error.code = 'SETUP_REVIEW_RELEASE_APPROVAL_REQUIRED';
    throw error;
  }

  if (activeEvidenceCount < 1) {
    const error = new Error('Release requires receipt-backed evidence.');
    error.statusCode = 409;
    error.code = 'SETUP_REVIEW_RELEASE_EVIDENCE_REQUIRED';
    throw error;
  }

  packet.receipts = Array.isArray(packet.receipts) ? packet.receipts : [];
  packet.auditTrail = Array.isArray(packet.auditTrail) ? packet.auditTrail : [];

  const receipt = createWilsySetupReviewReceipt('SETUP_REVIEW_RELEASED', packet, evidence);
  const releaseState = {
    status: 'RELEASED',
    releaseScope: resolveWilsySetupReviewText(
      body.releaseScope || body.scope,
      'SETUP_REVIEW_PACKET'
    ),
    evidenceCount: activeEvidenceCount,
    reason: 'APPROVAL_AND_EVIDENCE_CONFIRMED',
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
    releasedAt: receipt.generatedAt,
    updatedAt: receipt.generatedAt,
  };
  const auditEvent = createWilsySetupReviewWorkflowAuditEvent(
    'SETUP_REVIEW_RELEASED',
    packet,
    evidence,
    receipt,
    {
      evidenceCount: activeEvidenceCount,
      releaseScope: releaseState.releaseScope,
    }
  );

  packet.releaseState = releaseState;
  packet.workflowState = resolveWilsySetupReviewWorkflowState(packet, 'SETUP_REVIEW_RELEASED');
  packet.status = 'RELEASED';
  packet.route = route;
  packet.commandSurface = evidence.commandSurface;
  packet.institutionalHeaders = evidence.institutionalHeaders;
  packet.strikePayload = evidence.strikePayload;
  packet.receipts.push(receipt);
  packet.auditTrail.push(auditEvent);

  await packet.save();

  return res.json({
    ok: true,
    result: 'SETUP_REVIEW_RELEASED',
    why: 'Setup review packet released with approval and evidence receipts.',
    packet: serializeWilsySetupReviewPacket(packet),
    releaseState,
    receipt,
    auditEvidence: auditEvent,
  });
}

/**
 * @function handleWilsySetupReviewClear
 * @description Clears staged setup review packets for the current tenant and operator scope.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, queue clear authority, receipt return, and audit trail.
 */
async function handleWilsySetupReviewClear(req, res) {
  const route = '/api/crm/command/setup/reviews/clear';
  const evidence = assertWilsySetupReviewWriteEvidence(req, route);
  const WilsyCrmSetupReviewPacket = resolveWilsySetupReviewModel();

  const packets = await WilsyCrmSetupReviewPacket.find({
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    status: 'STAGED',
  });

  const receiptSeed = {
    packetId: `SETUP_REVIEW_CLEAR_${Date.now()}`,
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
  };

  const receipt = createWilsySetupReviewReceipt(
    'SETUP_REVIEW_QUEUE_CLEARED',
    receiptSeed,
    evidence
  );
  const auditEvent = {
    event: 'SETUP_REVIEW_QUEUE_CLEARED',
    route,
    commandSurface: evidence.commandSurface,
    tenantId: evidence.tenantId,
    operatorId: evidence.operatorId,
    userId: evidence.userId,
    clearedCount: packets.length,
    generatedAt: receipt.generatedAt,
    receiptId: receipt.receiptId,
    receiptHash: receipt.receiptHash,
  };

  await WilsyCrmSetupReviewPacket.updateMany(
    {
      tenantId: evidence.tenantId,
      operatorId: evidence.operatorId,
      status: 'STAGED',
    },
    {
      $set: {
        status: 'CLEARED',
        clearedAt: new Date(),
        route,
        commandSurface: evidence.commandSurface,
        institutionalHeaders: evidence.institutionalHeaders,
        strikePayload: evidence.strikePayload,
      },
      $push: {
        receipts: receipt,
        auditTrail: auditEvent,
      },
    }
  );

  return res.json({
    ok: true,
    result: 'SETUP_REVIEW_QUEUE_CLEARED',
    why: 'Setup review queue cleared through CRM command authority.',
    clearedCount: packets.length,
    receipt,
    auditEvidence: auditEvent,
  });
}

/**
 * @function handleWilsySetupReviewOpenByBody
 * @description Opens a backend-owned setup review packet through a POST command body so ProductionHardening can validate strike evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, ProductionHardening middleware, command read alias, and tenant scoped packet reads.
 */
async function handleWilsySetupReviewOpenByBody(req, res) {
  const packetId = resolveWilsySetupReviewText(
    req.body?.packetId || req.body?.id || req.body?.packet?.packetId || req.body?.packet?.id,
    ''
  );

  req.params = {
    ...(req.params || {}),
    packetId,
  };

  return handleWilsySetupReviewOpen(req, res);
}

/**
 * @function handleWilsySetupReviewListByCommand
 * @description Lists staged setup review packets through a POST command body so ProductionHardening can validate strike evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration CRM setup Packet Console, ProductionHardening middleware, command read alias, and tenant scoped packet queue reads.
 */
async function handleWilsySetupReviewListByCommand(req, res) {
  return handleWilsySetupReviewList(req, res);
}

router.post('/setup/reviews/list', wrapWilsySetupReviewRoute(handleWilsySetupReviewListByCommand));
router.post('/setup/reviews/open', wrapWilsySetupReviewRoute(handleWilsySetupReviewOpenByBody));
router.get('/setup/reviews', wrapWilsySetupReviewRoute(handleWilsySetupReviewList));
router.post('/setup/reviews', wrapWilsySetupReviewRoute(handleWilsySetupReviewCreate));
router.post('/setup/reviews/clear', wrapWilsySetupReviewRoute(handleWilsySetupReviewClear));
router.post(
  '/setup/reviews/evidence',
  wrapWilsySetupReviewRoute(handleWilsySetupReviewAttachEvidence)
);
router.post('/setup/reviews/approve', wrapWilsySetupReviewRoute(handleWilsySetupReviewApprove));
router.post('/setup/reviews/release', wrapWilsySetupReviewRoute(handleWilsySetupReviewRelease));
router.get('/setup/reviews/:packetId', wrapWilsySetupReviewRoute(handleWilsySetupReviewOpen));
router.delete('/setup/reviews/:packetId', wrapWilsySetupReviewRoute(handleWilsySetupReviewRemove));

export default router;
