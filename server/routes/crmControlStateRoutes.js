/* eslint-disable */
import express from 'express';
import CrmControlState from '../models/crmControlStateModel.js';

const router = express.Router();

const WILSY_CRM_CONTROL_STATE_ROUTE_ID = 'P60K5Q10FG11_LEADS_FILTER_CONTROL_STATE_ROUTE';

/**
 * @function resolveRequestTenantId
 * @description Resolves tenant id from headers, body, query, or authenticated request context.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Tenant-scoped CRM control state, Leads filter persistence, Wilsy institutional headers, and backend evidence routes.
 */
function resolveRequestTenantId(req) {
  return String(
    req.headers['x-tenant-id'] ||
      req.body?.tenantId ||
      req.query?.tenantId ||
      req.user?.tenantId ||
      'wilsy-sovereign-root'
  );
}

/**
 * @function resolveRequestOperatorId
 * @description Resolves operator id from headers, body, or authenticated request context.
 * @param {Object} req - Express request.
 * @returns {string} Operator id.
 * @collaboration Operator-scoped CRM control state, Leads filter persistence, audit receipts, and backend evidence routes.
 */
function resolveRequestOperatorId(req) {
  return String(
    req.headers['x-operator-id'] ||
      req.headers['x-user-id'] ||
      req.body?.operatorId ||
      req.body?.userId ||
      req.user?.id ||
      req.user?._id ||
      'wilsy-operator'
  );
}

/**
 * @function buildControlStateScope
 * @description Builds the unique persistence scope for a CRM control state request.
 * @param {Object} req - Express request.
 * @returns {Object} Scope object.
 * @collaboration Leads module, filter buttons, operator-specific persistence, tenant-specific persistence, and CRM source posture.
 */
function buildControlStateScope(req) {
  return {
    tenantId: resolveRequestTenantId(req),
    operatorId: resolveRequestOperatorId(req),
    moduleKey: 'leads',
    surfaceKey: 'filter-sidebar',
    stateKey: 'selected-filters',
  };
}

/**
 * @function normalizeSelectedFilters
 * @description Normalizes selected filter names.
 * @param {*} value - Candidate selected filter list.
 * @returns {Array<string>} Normalized selected filter names.
 * @collaboration Leads filters, checkbox state, frontend/backend persistence, and clean operator control state.
 */
function normalizeSelectedFilters(value) {
  if (!Array.isArray(value)) {
    return [];
  }

  return [
    ...new Set(
      value
        .map((item) =>
          String(item || '')
            .replace(/\s+/g, ' ')
            .trim()
        )
        .filter(Boolean)
    ),
  ].slice(0, 80);
}

/**
 * @function buildInstitutionalEvidenceReceipt
 * @description Builds the evidence receipt for CRM control state persistence.
 * @param {Object} req - Express request.
 * @param {Array<string>} selectedFilters - Selected filters.
 * @returns {Object} Evidence receipt.
 * @collaboration Wilsy institutional evidence, filter state persistence, tenant/operator traceability, and CRM control audit receipts.
 */
function buildInstitutionalEvidenceReceipt(req, selectedFilters) {
  const generatedAt = new Date().toISOString();

  return {
    routeId: WILSY_CRM_CONTROL_STATE_ROUTE_ID,
    route: '/api/crm/control-state/leads/filters',
    commandSurface: 'LEADS_FILTER_CONTROL_STATE',
    generatedAt,
    tenantId: resolveRequestTenantId(req),
    operatorId: resolveRequestOperatorId(req),
    selectedFilters,
    source: 'WilsyLeadOperatingRoom',
    result: 'CONTROL_STATE_PERSISTED',
  };
}

/**
 * @function assertInstitutionalMutationEnvelope
 * @description Validates the Wilsy evidence contract for mutating control state requests.
 * @param {Object} req - Express request.
 * @returns {void}
 * @collaboration Institutional headers, strike payload evidence, tenant scope, operator scope, and non-record CRM control state mutations.
 */
function assertInstitutionalMutationEnvelope(req) {
  const body = req.body || {};
  const institutionalHeaders = body.institutionalHeaders || {};
  const strikePayload = body.strikePayload || {};

  const hasTenant = Boolean(body.tenantId || req.headers['x-tenant-id']);
  const hasOperator = Boolean(
    body.operatorId || body.userId || req.headers['x-operator-id'] || req.headers['x-user-id']
  );
  const hasGeneratedAt = Boolean(body.generatedAt);
  const hasSurface = Boolean(body.commandSurface || institutionalHeaders.commandSurface);
  const hasNestedHeaders = Boolean(strikePayload.institutionalHeaders);

  if (!hasTenant || !hasOperator || !hasGeneratedAt || !hasSurface || !hasNestedHeaders) {
    const error = new Error(
      'Wilsy institutional mutation envelope missing tenant/operator/generatedAt/surface/nested headers.'
    );
    error.statusCode = 400;
    throw error;
  }
}

/**
 * @function handleGetLeadFilterControlState
 * @description Reads persisted Leads filter button state for the current tenant/operator.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Leads filter buttons, backend control state, tenant/operator scope, and source-backed UI persistence.
 */
async function handleGetLeadFilterControlState(req, res) {
  const scope = buildControlStateScope(req);
  const record = await CrmControlState.findOne(scope).lean();

  res.json({
    ok: true,
    routeId: WILSY_CRM_CONTROL_STATE_ROUTE_ID,
    ...scope,
    selectedFilters: normalizeSelectedFilters(record?.selectedFilters || []),
    controlState: record?.controlState || {},
    generatedAt: new Date().toISOString(),
    source: record ? 'backend' : 'empty-backend-state',
  });
}

/**
 * @function handlePutLeadFilterControlState
 * @description Persists Leads filter button state with Wilsy institutional evidence.
 * @param {Object} req - Express request.
 * @param {Object} res - Express response.
 * @returns {Promise<void>} JSON response.
 * @collaboration Leads filter buttons, backend persistence, institutionalHeaders, strikePayload, evidenceLedger, and audit-ready control state.
 */
async function handlePutLeadFilterControlState(req, res) {
  assertInstitutionalMutationEnvelope(req);

  const scope = buildControlStateScope(req);
  const selectedFilters = normalizeSelectedFilters(req.body?.selectedFilters);
  const receipt = buildInstitutionalEvidenceReceipt(req, selectedFilters);

  const record = await CrmControlState.findOneAndUpdate(
    scope,
    {
      $set: {
        ...scope,
        selectedFilters,
        controlState: {
          selectedFilters,
          updatedBySurface: 'Leads Filter Sidebar',
          updatedAt: receipt.generatedAt,
        },
        institutionalHeaders: req.body?.institutionalHeaders || {},
        strikePayload: req.body?.strikePayload || {},
        generatedAt: new Date(receipt.generatedAt),
      },
      $push: {
        evidenceLedger: {
          $each: [receipt],
          $slice: -80,
        },
      },
    },
    {
      upsert: true,
      new: true,
      setDefaultsOnInsert: true,
    }
  ).lean();

  res.json({
    ok: true,
    routeId: WILSY_CRM_CONTROL_STATE_ROUTE_ID,
    ...scope,
    selectedFilters: normalizeSelectedFilters(record?.selectedFilters || selectedFilters),
    receipt,
    generatedAt: new Date().toISOString(),
  });
}

router.get('/leads/filters', (req, res, next) => {
  handleGetLeadFilterControlState(req, res).catch(next);
});

router.put('/leads/filters', (req, res, next) => {
  handlePutLeadFilterControlState(req, res).catch(next);
});

export default router;
