/* eslint-disable */
import mongoose from 'mongoose';
import CrmLeadView from '../models/crmLeadViewModel.js';
import {
  RULE_ENGINE_VERSION,
  buildCriteriaHash,
  buildLeadCategorySummary,
  doesLeadMatchBuiltInCategory,
  doesLeadMatchCustomCriteria,
} from './crmLeadViewCategoryEngine.js';

const LEAD_COLLECTION_CANDIDATES = [
  'leads',
  'crmleads',
  'crm_leads',
  'crmLeads',
  'leadrecords',
  'lead_records',
];

/**
 * @function createAuditReceiptId
 * @description Creates a compact receipt id for Lead View registry audit trails.
 * @collaboration Lead View Registry, audit logs, Wilsy AI answers, and tenant evidence.
 * @param {string} action Registry action.
 * @returns {string} Audit receipt id.
 */
function createAuditReceiptId(action = 'view') {
  return `lead_view_${action}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

/**
 * @function normalizeViewVisibility
 * @description Normalizes saved view visibility into supported SaaS visibility values.
 * @collaboration Permissions, tenant-ready view sharing, CRUD, and audit policy.
 * @param {string} visibility Requested visibility.
 * @returns {string} Normalized visibility.
 */
function normalizeViewVisibility(visibility = 'private') {
  const normalized = String(visibility || 'private').toLowerCase();
  if (['private', 'team', 'tenant', 'role'].includes(normalized)) return normalized;
  return 'private';
}

/**
 * @function normalizeViewCriteria
 * @description Normalizes custom view criteria from frontend or API payloads.
 * @collaboration Custom View Builder, backend run, preview, persistence, and audit hashing.
 * @param {object} payload Request payload.
 * @returns {Array<object>} Criteria list.
 */
function normalizeViewCriteria(payload = {}) {
  if (Array.isArray(payload.criteria)) {
    return payload.criteria
      .map((criterion) => ({
        field: String(criterion.field || '').trim(),
        operator: String(criterion.operator || 'contains').trim(),
        value: criterion.value ?? '',
        valueLabel: String(criterion.valueLabel || '').trim(),
      }))
      .filter((criterion) => criterion.field);
  }

  if (payload.field) {
    return [
      {
        field: String(payload.field || '').trim(),
        operator: String(payload.operator || 'contains').trim(),
        value: payload.value ?? '',
        valueLabel: String(payload.valueLabel || '').trim(),
      },
    ];
  }

  return [];
}

/**
 * @function resolveRequestContext
 * @description Resolves tenant, operator, and institutional evidence context from a request.
 * @collaboration Multi-tenant CRM, institutional headers, strike payload evidence, and audit routes.
 * @param {object} req Express request.
 * @returns {object} Request context.
 */
function resolveRequestContext(req = {}) {
  const body = req.body || {};
  const headers = req.headers || {};
  const institutionalHeaders = body.institutionalHeaders || {};

  const tenantId = String(
    headers['x-tenant-id'] || institutionalHeaders.tenantId || body.tenantId || 'MASTER'
  );

  const operatorUserId = String(
    headers['x-operator-id'] ||
      headers['x-user-id'] ||
      institutionalHeaders.operatorUserId ||
      body.ownerUserId ||
      body.operatorUserId ||
      'system'
  );

  return {
    tenantId,
    operatorUserId,
    institutionalHeaders: {
      ...institutionalHeaders,
      tenantId,
      operatorUserId,
      route: req.originalUrl || req.url || '/api/crm/leads/views',
      commandSurface:
        headers['x-command-surface'] || body.commandSurface || 'CRM_LEADS_VIEW_REGISTRY',
      generatedAt: institutionalHeaders.generatedAt || new Date().toISOString(),
    },
    strikePayload: body.strikePayload || {},
  };
}

/**
 * @function buildAuditEntry
 * @description Builds one audit trail entry for a Lead View registry action.
 * @collaboration Audit receipts, Wilsy AI explainability, saved view CRUD, and tenant evidence.
 * @param {object} params Audit params.
 * @returns {object} Audit entry.
 */
function buildAuditEntry(params = {}) {
  const auditReceiptId = params.auditReceiptId || createAuditReceiptId(params.action);
  return {
    auditReceiptId,
    action: params.action || 'VIEW_ACTION',
    route: params.route || '/api/crm/leads/views',
    operatorUserId: params.operatorUserId || 'system',
    tenantId: params.tenantId || 'MASTER',
    criteriaHash: params.criteriaHash || '',
    resultCount: Number(params.resultCount || 0),
    generatedAt: new Date(),
    institutionalHeaders: params.institutionalHeaders || {},
    strikePayload: params.strikePayload || {},
  };
}

/**
 * @function listTenantLeadViews
 * @description Lists active saved Lead views visible to the current tenant/operator scope.
 * @collaboration Lead View Registry, custom views, permissions, and CRM organizer hydration.
 * @param {object} context Request context.
 * @returns {Promise<Array<object>>} Saved views.
 */
async function listTenantLeadViews(context = {}) {
  const tenantId = context.tenantId || 'MASTER';
  const operatorUserId = context.operatorUserId || 'system';

  return CrmLeadView.find({
    tenantId,
    status: 'active',
    $or: [{ ownerUserId: operatorUserId }, { visibility: { $in: ['team', 'tenant'] } }],
  })
    .sort({ pinned: -1, updatedAt: -1 })
    .lean();
}

/**
 * @function resolveLeadCollections
 * @description Resolves candidate MongoDB collections that may hold CRM Lead records.
 * @collaboration Live backend counts, category engine, saved view run, and database portability.
 * @returns {Promise<Array<object>>} Collection handles.
 */
async function resolveLeadCollections() {
  if (!mongoose.connection || !mongoose.connection.db) return [];

  const existingCollections = await mongoose.connection.db.listCollections().toArray();
  const existingNames = existingCollections.map((collection) => collection.name);
  const candidateNames = [
    ...LEAD_COLLECTION_CANDIDATES,
    ...existingNames.filter((name) => /lead/i.test(name)),
  ];

  return [...new Set(candidateNames)].map((name) => mongoose.connection.db.collection(name));
}

/**
 * @function buildTenantLeadQuery
 * @description Builds a tenant-aware query with safe fallback for legacy Lead records.
 * @collaboration Multi-tenant record scope, live counts, and migration-safe CRM data access.
 * @param {string} tenantId Tenant id.
 * @returns {object} MongoDB query.
 */
function buildTenantLeadQuery(tenantId = 'MASTER') {
  return {
    $or: [
      { tenantId },
      { tenant: tenantId },
      { organizationId: tenantId },
      { tenantId: { $exists: false } },
    ],
  };
}

/**
 * @function listLiveLeadRecords
 * @description Loads live Lead records from the backend for view run and preview operations.
 * @collaboration Lead Category Engine, saved view execution, Wilsy AI, and source-backed counts.
 * @param {object} context Request context.
 * @returns {Promise<Array<object>>} Lead records.
 */
async function listLiveLeadRecords(context = {}) {
  const tenantId = context.tenantId || 'MASTER';
  const collections = await resolveLeadCollections();

  for (const collection of collections) {
    const tenantRecords = await collection
      .find(buildTenantLeadQuery(tenantId))
      .limit(5000)
      .toArray();
    if (tenantRecords.length) return tenantRecords;
  }

  return [];
}

/**
 * @function createLeadView
 * @description Creates and persists a custom Lead view with audit evidence.
 * @collaboration Custom View Builder, backend CRUD, tenant visibility, and Wilsy AI saved view memory.
 * @param {object} payload Request payload.
 * @param {object} context Request context.
 * @returns {Promise<object>} Created view.
 */
async function createLeadView(payload = {}, context = {}) {
  const criteria = normalizeViewCriteria(payload);
  const criteriaHash = buildCriteriaHash(criteria);
  const auditReceiptId = createAuditReceiptId('create');
  const auditEntry = buildAuditEntry({
    auditReceiptId,
    action: 'CREATE_LEAD_VIEW',
    route: '/api/crm/leads/views',
    tenantId: context.tenantId,
    operatorUserId: context.operatorUserId,
    criteriaHash,
    institutionalHeaders: context.institutionalHeaders,
    strikePayload: context.strikePayload,
  });

  const view = await CrmLeadView.create({
    tenantId: context.tenantId,
    ownerUserId: context.operatorUserId,
    createdBy: context.operatorUserId,
    updatedBy: context.operatorUserId,
    name: String(payload.name || payload.label || 'Untitled Lead View').trim(),
    description: String(payload.description || '').trim(),
    visibility: normalizeViewVisibility(payload.visibility),
    criteria,
    columns: Array.isArray(payload.columns) ? payload.columns : [],
    sort: payload.sort || { field: 'updatedAt', direction: 'desc' },
    pinned: Boolean(payload.pinned),
    criteriaHash,
    auditTrail: [auditEntry],
    metadata: {
      source: payload.source || 'lead-custom-view-builder',
      uiVersion: payload.uiVersion || 'FG98',
      localFallbackId: String(payload.id || ''),
    },
  });

  return view.toObject();
}

/**
 * @function updateLeadView
 * @description Updates a saved Lead view and records before/after audit evidence.
 * @collaboration CRUD, custom views, tenant operators, and audit traceability.
 * @param {string} viewId View id.
 * @param {object} payload Request payload.
 * @param {object} context Request context.
 * @returns {Promise<object|null>} Updated view.
 */
async function updateLeadView(viewId, payload = {}, context = {}) {
  const existing = await CrmLeadView.findOne({
    _id: viewId,
    tenantId: context.tenantId,
    status: 'active',
  });

  if (!existing) return null;

  const criteria = normalizeViewCriteria(payload.criteria ? payload : existing);
  const criteriaHash = buildCriteriaHash(criteria);
  const auditReceiptId = createAuditReceiptId('update');

  existing.name = String(payload.name || existing.name).trim();
  existing.description = String(payload.description ?? existing.description).trim();
  existing.visibility = normalizeViewVisibility(payload.visibility || existing.visibility);
  existing.criteria = criteria;
  existing.criteriaHash = criteriaHash;
  existing.updatedBy = context.operatorUserId;
  existing.auditTrail.push(
    buildAuditEntry({
      auditReceiptId,
      action: 'UPDATE_LEAD_VIEW',
      route: `/api/crm/leads/views/${viewId}`,
      tenantId: context.tenantId,
      operatorUserId: context.operatorUserId,
      criteriaHash,
      institutionalHeaders: context.institutionalHeaders,
      strikePayload: {
        ...context.strikePayload,
        before: {
          name: existing.name,
          criteriaHash: existing.criteriaHash,
        },
      },
    })
  );

  await existing.save();
  return existing.toObject();
}

/**
 * @function archiveLeadView
 * @description Archives a saved Lead view instead of deleting audit history.
 * @collaboration Delete semantics, audit retention, tenant evidence, and Wilsy AI historical answers.
 * @param {string} viewId View id.
 * @param {object} context Request context.
 * @returns {Promise<object|null>} Archived view.
 */
async function archiveLeadView(viewId, context = {}) {
  const existing = await CrmLeadView.findOne({
    _id: viewId,
    tenantId: context.tenantId,
    status: 'active',
  });

  if (!existing) return null;

  existing.status = 'archived';
  existing.updatedBy = context.operatorUserId;
  existing.auditTrail.push(
    buildAuditEntry({
      action: 'ARCHIVE_LEAD_VIEW',
      route: `/api/crm/leads/views/${viewId}`,
      tenantId: context.tenantId,
      operatorUserId: context.operatorUserId,
      criteriaHash: existing.criteriaHash,
      institutionalHeaders: context.institutionalHeaders,
      strikePayload: context.strikePayload,
    })
  );

  await existing.save();
  return existing.toObject();
}

/**
 * @function runLeadView
 * @description Executes a saved Lead view against live backend Lead records.
 * @collaboration Live counts, custom views, Wilsy AI answer tools, audit receipts, and backend analytics.
 * @param {string} viewId View id.
 * @param {object} context Request context.
 * @returns {Promise<object|null>} Run result.
 */
async function runLeadView(viewId, context = {}) {
  const view = await CrmLeadView.findOne({
    _id: viewId,
    tenantId: context.tenantId,
    status: 'active',
  });

  if (!view) return null;

  const startedAt = Date.now();
  const leads = await listLiveLeadRecords(context);
  const matchedLeads = leads.filter((lead) => doesLeadMatchCustomCriteria(lead, view.criteria));
  const durationMs = Date.now() - startedAt;
  const auditReceiptId = createAuditReceiptId('run');

  view.lastRun = {
    count: matchedLeads.length,
    totalScopeCount: leads.length,
    sampleLeadIds: matchedLeads.slice(0, 25).map((lead) => String(lead._id || lead.id || '')),
    durationMs,
    executedAt: new Date(),
  };

  view.auditTrail.push(
    buildAuditEntry({
      auditReceiptId,
      action: 'RUN_LEAD_VIEW',
      route: `/api/crm/leads/views/${viewId}/run`,
      tenantId: context.tenantId,
      operatorUserId: context.operatorUserId,
      criteriaHash: view.criteriaHash,
      resultCount: matchedLeads.length,
      institutionalHeaders: context.institutionalHeaders,
      strikePayload: context.strikePayload,
    })
  );

  await view.save();

  return {
    view: view.toObject(),
    result: {
      count: matchedLeads.length,
      totalScopeCount: leads.length,
      sampleLeadIds: matchedLeads.slice(0, 25).map((lead) => String(lead._id || lead.id || '')),
      ruleEngineVersion: RULE_ENGINE_VERSION,
      auditReceiptId,
      durationMs,
    },
  };
}

/**
 * @function previewLeadViewCriteria
 * @description Previews unsaved criteria against live backend Lead records.
 * @collaboration Custom View Builder, live preview, audit-ready AI explanations, and criteria tuning.
 * @param {object} payload Request payload.
 * @param {object} context Request context.
 * @returns {Promise<object>} Preview result.
 */
async function previewLeadViewCriteria(payload = {}, context = {}) {
  const startedAt = Date.now();
  const criteria = normalizeViewCriteria(payload);
  const criteriaHash = buildCriteriaHash(criteria);
  const leads = await listLiveLeadRecords(context);
  const matchedLeads = leads.filter((lead) => doesLeadMatchCustomCriteria(lead, criteria));

  return {
    count: matchedLeads.length,
    totalScopeCount: leads.length,
    sampleLeadIds: matchedLeads.slice(0, 25).map((lead) => String(lead._id || lead.id || '')),
    criteriaHash,
    ruleEngineVersion: RULE_ENGINE_VERSION,
    durationMs: Date.now() - startedAt,
    auditReceiptId: createAuditReceiptId('preview'),
  };
}

/**
 * @function explainLeadCategories
 * @description Returns built-in category counts from live backend Leads.
 * @collaboration Wilsy AI answers, View Organizer counts, analytics, and investor-grade category evidence.
 * @param {object} context Request context.
 * @returns {Promise<object>} Category summary.
 */
async function explainLeadCategories(context = {}) {
  const leads = await listLiveLeadRecords(context);
  return buildLeadCategorySummary(leads);
}

export {
  archiveLeadView,
  createLeadView,
  explainLeadCategories,
  listLiveLeadRecords,
  listTenantLeadViews,
  previewLeadViewCriteria,
  resolveRequestContext,
  runLeadView,
  updateLeadView,
  doesLeadMatchBuiltInCategory,
};
