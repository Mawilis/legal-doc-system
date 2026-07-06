/* eslint-disable */
import express from 'express';
import { resolveWilsyAISovereignContext } from '../services/wilsyAI/wilsyAISovereignContextService.js';
import { resolveWilsyAIOperatorModel } from '../services/wilsyAI/wilsyAIOperatorModelService.js';

const router = express.Router();

/* WILSY_P60K5Q10F_ROUTE_LOCAL_EVIDENCE_GATE */
router.use(express.json({ limit: '1mb' }));
router.use(express.urlencoded({ extended: true, limit: '1mb' }));

/**
 * @function isWilsyAIPlainObject
 * @description Checks whether a value is a plain object for route-local evidence validation.
 * @param {*} value - Unknown value.
 * @returns {boolean} True when the value is a non-array object.
 * @collaboration Wilsy AI route guard, institutional headers, strike payload evidence, and no-mutation context resolution.
 */
function isWilsyAIPlainObject(value) {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

/**
 * @function validateWilsyAIContextEvidence
 * @description Validates institutionalHeaders and strikePayload.institutionalHeaders before read-only context resolution.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @param {Function} next - Express next callback.
 * @returns {void} Continues or returns evidence error.
 * @collaboration ProductionHardening contract, Wilsy AI context resolver, global dock evidence payload, and tenant-safe operator guidance.
 */
function validateWilsyAIContextEvidence(req, res, next) {
  const generatedAt = new Date().toISOString();
  const body = req.body || {};
  const institutionalHeaders = body.institutionalHeaders;
  const strikePayload = body.strikePayload;
  const nestedInstitutionalHeaders = strikePayload?.institutionalHeaders;

  if (
    isWilsyAIPlainObject(institutionalHeaders) &&
    isWilsyAIPlainObject(strikePayload) &&
    isWilsyAIPlainObject(nestedInstitutionalHeaders)
  ) {
    return next();
  }

  return res.status(403).json({
    result: 'WILSY_AI_CONTEXT_EVIDENCE_REQUIRED',
    mutation: false,
    generatedAt,
    institutionalHeaders: {
      tenantId: req.headers?.['x-tenant-id'] || body.tenantId || 'MASTER',
      operatorId: req.headers?.['x-operator-id'] || body.operatorId || 'UNKNOWN_OPERATOR',
      generatedAt,
      route: '/api/wilsy/ai/context/resolve',
      commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
      contractVersion: 'P60K5Q10F_ROUTE_LOCAL_EVIDENCE_GATE',
    },
    strikePayload: {
      institutionalHeaders: {
        tenantId: req.headers?.['x-tenant-id'] || body.tenantId || 'MASTER',
        operatorId: req.headers?.['x-operator-id'] || body.operatorId || 'UNKNOWN_OPERATOR',
        generatedAt,
        route: '/api/wilsy/ai/context/resolve',
        commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
      },
      commandType: 'READ_ONLY_AI_CONTEXT_RESOLUTION_REJECTED',
      mutation: false,
    },
    error: {
      code: 'WILSY_AI_EVIDENCE_CONTRACT_REQUIRED',
      message:
        'institutionalHeaders and strikePayload.institutionalHeaders are required for Wilsy AI context resolution.',
    },
  });
}
/* WILSY_P60K5Q10F_ROUTE_LOCAL_EVIDENCE_GATE_END */

/**
 * @function handleWilsyAIContextResolve
 * @description Resolves the read-only Wilsy AI sovereign context contract for the global intelligence dock.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} Sends context response.
 * @collaboration Wilsy OS Intelligence Dock, sovereign context service, tenant scope, evidence contract, billing entitlement, and future execution bridge.
 */
async function handleWilsyAIContextResolve(req, res) {
  try {
    const context = await resolveWilsyAISovereignContext(req);
    res.status(200).json(context);
  } catch (error) {
    const generatedAt = new Date().toISOString();
    const tenantId = req.headers?.['x-tenant-id'] || req.body?.tenantId || 'MASTER';

    res.status(500).json({
      result: 'WILSY_AI_CONTEXT_RESOLVE_FAILED',
      mutation: false,
      generatedAt,
      institutionalHeaders: {
        tenantId,
        operatorId: req.user?.id || req.headers?.['x-operator-id'] || 'UNKNOWN_OPERATOR',
        generatedAt,
        route: '/api/wilsy/ai/context/resolve',
        commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
        contractVersion: 'P60K5Q10_WILSY_AI_SOVEREIGN_CONTEXT_RESOLVER',
      },
      strikePayload: {
        institutionalHeaders: {
          tenantId,
          generatedAt,
          route: '/api/wilsy/ai/context/resolve',
          commandSurface: 'WILSY_OS_INTELLIGENCE_DOCK',
        },
        commandType: 'READ_ONLY_AI_CONTEXT_RESOLUTION_FAILURE',
        mutation: false,
      },
      error: {
        code: 'WILSY_AI_CONTEXT_RESOLVE_FAILED',
        message: error?.message || 'Unable to resolve Wilsy AI context.',
      },
    });
  }
}

/* WILSY_P60K5Q10FG46_OPERATOR_ROUTE */
/**
 * @function handleWilsyAIOperatorResolve
 * @description Resolves workspace-aware Wilsy AI operator questions through the Operator Kernel without mutating records.
 * @param {Object} req - Express request with institutional evidence, tenant/operator headers, and workspace context.
 * @param {Object} res - Express response with continuous typographic answer payload.
 * @returns {Promise<void>} Sends Operator Kernel response.
 * @collaboration Wilsy AI Operator Kernel, CRM Leads viewpoint context, institutional evidence gate, and frontend continuous response surface.
 */
async function handleWilsyAIOperatorResolve(req, res) {
  const generatedAt = new Date().toISOString();

  try {
    const body = req.body || {};
    const institutionalHeaders = body.institutionalHeaders || {};
    const tenantId =
      institutionalHeaders.tenantId || req.headers['x-tenant-id'] || body.tenantId || 'MASTER';
    const operatorId =
      institutionalHeaders.operatorId ||
      req.headers['x-operator-id'] ||
      body.operatorId ||
      'WILSY_AI_OPERATOR';
    const operatorQuestion =
      body.operatorQuestion || body.question || req.query?.operatorQuestion || '';

    if (!String(operatorQuestion || '').trim()) {
      return res.status(400).json({
        result: 'WILSY_AI_OPERATOR_QUESTION_REQUIRED',
        mutation: false,
        generatedAt,
        error: {
          code: 'OPERATOR_QUESTION_REQUIRED',
          message: 'A Wilsy AI operator question is required.',
        },
      });
    }

    const operatorRequest = {
      ...req,
      query: {
        ...(req.query || {}),
        wilsyAiContext: req.query?.wilsyAiContext || body.wilsyAiContext || 'ASK',
        operatorQuestion,
        tenantId,
        operatorId,
        workspaceRoute: body.workspaceRoute || req.query?.workspaceRoute || '/crm/leads',
        workspaceSurface: body.workspaceSurface || req.query?.workspaceSurface || 'CRM Leads',
      },
      body: {
        ...body,
        tenantId,
        operatorId,
        operatorQuestion,
        workspaceRoute: body.workspaceRoute || req.query?.workspaceRoute || '/crm/leads',
        workspaceSurface: body.workspaceSurface || req.query?.workspaceSurface || 'CRM Leads',
        crmLeadsContext: body.crmLeadsContext || {},
      },
      headers: {
        ...(req.headers || {}),
        'x-tenant-id': tenantId,
        'x-operator-id': operatorId,
      },
    };

    const operatorModel = await resolveWilsyAIOperatorModel(operatorRequest);

    return res.status(200).json({
      result: 'WILSY_AI_OPERATOR_RESOLVED',
      contractVersion: 'P60K5Q10FG46_WILSY_AI_OPERATOR_ROUTE',
      route: '/api/wilsy/ai/operator/resolve',
      mutation: Boolean(operatorModel?.mutation),
      generatedAt,
      tenantId,
      operatorId,
      operatorModel,
      responseSurface:
        operatorModel?.operatorModel?.responseSurface ||
        operatorModel?.responseSurface ||
        'continuous_typographic',
      inlineCommandLinks:
        operatorModel?.operatorModel?.inlineCommandLinks || operatorModel?.inlineCommandLinks || [],
      crmLeadsViewpoint:
        operatorModel?.operatorModel?.crmLeadsViewpoint || operatorModel?.crmLeadsViewpoint || null,
      institutionalHeaders,
      strikePayload: body.strikePayload || null,
    });
  } catch (error) {
    return res.status(500).json({
      result: 'WILSY_AI_OPERATOR_RESOLVE_FAILED',
      contractVersion: 'P60K5Q10FG46_WILSY_AI_OPERATOR_ROUTE',
      route: '/api/wilsy/ai/operator/resolve',
      mutation: false,
      generatedAt,
      error: {
        code: error?.code || 'OPERATOR_RESOLVE_FAILED',
        message: error?.message || 'Unable to resolve Wilsy AI operator question.',
      },
    });
  }
}

/**
 * @function handleWilsyAIHealth
 * @description Reports read-only Wilsy AI route health and contract posture.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {void} Sends health response.
 * @collaboration Wilsy AI route, server health checks, global dock diagnostics, and protected no-mutation contract posture.
 */
function handleWilsyAIHealth(req, res) {
  const generatedAt = new Date().toISOString();

  res.status(200).json({
    result: 'WILSY_AI_ROUTE_HEALTHY',
    contractVersion: 'P60K5Q10_WILSY_AI_SOVEREIGN_CONTEXT_RESOLVER',
    route: '/api/wilsy/ai',
    mutation: false,
    generatedAt,
  });
}

router.get('/health', handleWilsyAIHealth);
router.post('/context/resolve', validateWilsyAIContextEvidence, handleWilsyAIContextResolve);
router.post('/operator/resolve', validateWilsyAIContextEvidence, handleWilsyAIOperatorResolve);

export default router;
