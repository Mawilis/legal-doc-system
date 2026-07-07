/* eslint-disable */
import mongoose from 'mongoose';
import CrmLeadView from '../models/crmLeadViewModel.js';
import CrmLeadViewMembershipOverride from '../models/crmLeadViewMembershipOverrideModel.js';
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
 * @function resolveLeadViewMembershipLeadId
 * @description Resolves a stable lead id from a backend Lead document or payload value.
 * @param {object|string} lead Lead document or lead id.
 * @returns {string} Normalized lead id.
 * @collaboration Lead membership overrides, live query execution, manual include, and manual exclude controls.
 */
function resolveLeadViewMembershipLeadId(lead = {}) {
  if (typeof lead === 'string') return lead.trim();
  return String(lead?._id || lead?.id || lead?.leadId || lead?.recordId || '').trim();
}

/**
 * @function normalizeLeadViewMembershipLeadIds
 * @description Normalizes selected lead ids supplied by frontend row selection or payload tests.
 * @param {object} payload Membership payload.
 * @returns {string[]} Unique lead ids.
 * @collaboration Selected-row state, membership override writes, signed payload tests, and CRM Lead collections.
 */
function normalizeLeadViewMembershipLeadIds(payload = {}) {
  const rawLeadIds =
    payload.leadIds || payload.selectedRowIds || payload.selectedLeadIds || payload.ids || [];
  const list = Array.isArray(rawLeadIds) ? rawLeadIds : [rawLeadIds];

  return Array.from(new Set(list.map((leadId) => String(leadId || '').trim()).filter(Boolean)));
}

/**
 * @function buildLeadViewMembershipSummary
 * @description Builds an operator-grade membership summary for live rule matches plus manual include/exclude overrides.
 * @param {object} params Summary params.
 * @returns {object} Membership summary.
 * @collaboration View Command Strip, backend run endpoint, Wilsy AI explanation, and collection productivity controls.
 */
function buildLeadViewMembershipSummary(params = {}) {
  const ruleMatchCount = Number(params.ruleMatchCount || 0);
  const manualIncludeCount = Number(params.manualIncludeCount || 0);
  const manualExcludeCount = Number(params.manualExcludeCount || 0);
  const effectiveCount = Number(params.effectiveCount || 0);

  return {
    effectiveCount,
    ruleMatchCount,
    manualIncludeCount,
    manualExcludeCount,
    algorithm: 'rule_matches_plus_manual_includes_minus_manual_excludes',
    formula: 'effective = ruleMatches + manualIncludes - manualExcludes',
  };
}

/**
 * @function listLeadViewMembershipOverrides
 * @description Lists active membership overrides for a Lead view.
 * @param {string} viewId Lead view id.
 * @param {object} context Request context.
 * @returns {Promise<object>} Membership override list and summary.
 * @collaboration Custom view CRUD, manual membership controls, audit explanation, and selected-row productivity.
 */
async function listLeadViewMembershipOverrides(viewId, context = {}) {
  const overrides = await CrmLeadViewMembershipOverride.find({
    tenantId: context.tenantId,
    viewId: String(viewId || ''),
    status: 'active',
  })
    .sort({ updatedAt: -1 })
    .lean();

  return {
    overrides,
    summary: {
      includeCount: overrides.filter((override) => override.mode === 'include').length,
      excludeCount: overrides.filter((override) => override.mode === 'exclude').length,
      totalCount: overrides.length,
    },
  };
}

/**
 * @function applyLeadViewMembershipOverrides
 * @description Applies manual include/exclude overrides to rule-matched Lead records.
 * @param {object} view Lead view document.
 * @param {object[]} ruleMatchedLeads Leads matching saved criteria.
 * @param {object[]} allLeads All live leads in scope.
 * @param {object} context Request context.
 * @returns {Promise<object>} Effective leads and membership summary.
 * @collaboration Rule engine, manual include, manual exclude, live backend records, and million-record-safe collection semantics.
 */
async function applyLeadViewMembershipOverrides(
  view,
  ruleMatchedLeads = [],
  allLeads = [],
  context = {}
) {
  const overrides = await CrmLeadViewMembershipOverride.find({
    tenantId: context.tenantId,
    viewId: String(view?._id || view?.id || ''),
    status: 'active',
  }).lean();

  const includes = overrides.filter((override) => override.mode === 'include');
  const excludes = overrides.filter((override) => override.mode === 'exclude');
  const excludeIds = new Set(excludes.map((override) => String(override.leadId)));
  const includeIds = new Set(includes.map((override) => String(override.leadId)));
  const leadsById = new Map(allLeads.map((lead) => [resolveLeadViewMembershipLeadId(lead), lead]));

  const effectiveById = new Map();

  for (const lead of ruleMatchedLeads) {
    const leadId = resolveLeadViewMembershipLeadId(lead);
    if (leadId && !excludeIds.has(leadId)) {
      effectiveById.set(leadId, lead);
    }
  }

  for (const leadId of includeIds) {
    if (!excludeIds.has(leadId) && leadsById.has(leadId)) {
      effectiveById.set(leadId, leadsById.get(leadId));
    }
  }

  const effectiveLeads = Array.from(effectiveById.values());

  return {
    effectiveLeads,
    summary: buildLeadViewMembershipSummary({
      effectiveCount: effectiveLeads.length,
      ruleMatchCount: ruleMatchedLeads.length,
      manualIncludeCount: includes.length,
      manualExcludeCount: excludes.length,
    }),
    overrides: {
      includes,
      excludes,
    },
  };
}

/**
 * @function writeLeadViewMembershipOverrides
 * @description Writes manual include or exclude overrides for a Lead view and records audit evidence on the view.
 * @param {string} viewId Lead view id.
 * @param {object} payload Membership payload.
 * @param {object} context Request context.
 * @param {string} mode Override mode.
 * @returns {Promise<object|null>} Write result.
 * @collaboration Selected rows, view membership engine, auditTrail, institutionalHeaders, and strikePayload.
 */
async function writeLeadViewMembershipOverrides(
  viewId,
  payload = {},
  context = {},
  mode = 'include'
) {
  const view = await CrmLeadView.findOne({
    _id: viewId,
    tenantId: context.tenantId,
    status: 'active',
  });

  if (!view) return null;

  const leadIds = normalizeLeadViewMembershipLeadIds(payload);
  if (!leadIds.length) {
    const error = new Error('No lead ids supplied for membership override.');
    error.code = 'LEAD_VIEW_MEMBERSHIP_IDS_REQUIRED';
    throw error;
  }

  const normalizedMode = mode === 'exclude' ? 'exclude' : 'include';
  const auditReceiptId = createAuditReceiptId(normalizedMode === 'include' ? 'include' : 'exclude');
  const now = new Date();

  await CrmLeadViewMembershipOverride.bulkWrite(
    leadIds.map((leadId) => ({
      updateOne: {
        filter: {
          tenantId: context.tenantId,
          viewId: String(viewId),
          leadId,
        },
        update: {
          $set: {
            mode: normalizedMode,
            reason: String(payload.reason || '').trim(),
            status: 'active',
            updatedBy: context.operatorUserId,
            institutionalHeaders: context.institutionalHeaders,
            strikePayload: context.strikePayload,
            updatedAt: now,
          },
          $setOnInsert: {
            tenantId: context.tenantId,
            viewId: String(viewId),
            leadId,
            createdBy: context.operatorUserId,
            createdAt: now,
          },
        },
        upsert: true,
      },
    }))
  );

  view.updatedBy = context.operatorUserId;
  view.auditTrail.push(
    buildAuditEntry({
      auditReceiptId,
      action: normalizedMode === 'include' ? 'INCLUDE_LEADS_IN_VIEW' : 'EXCLUDE_LEADS_FROM_VIEW',
      route: `/api/crm/leads/views/${viewId}/overrides/${normalizedMode}`,
      tenantId: context.tenantId,
      operatorUserId: context.operatorUserId,
      criteriaHash: view.criteriaHash,
      resultCount: leadIds.length,
      institutionalHeaders: context.institutionalHeaders,
      strikePayload: {
        ...context.strikePayload,
        leadIds,
        mode: normalizedMode,
      },
    })
  );

  await view.save();

  return {
    view: view.toObject(),
    leadIds,
    mode: normalizedMode,
    auditReceiptId,
    membership: await listLeadViewMembershipOverrides(viewId, context),
  };
}

/**
 * @function includeLeadViewMembers
 * @description Adds selected leads to a Lead view as manual include overrides.
 * @param {string} viewId Lead view id.
 * @param {object} payload Membership payload.
 * @param {object} context Request context.
 * @returns {Promise<object|null>} Include result.
 * @collaboration Selected-row add action, live collection membership, backend evidence, and audit receipts.
 */
async function includeLeadViewMembers(viewId, payload = {}, context = {}) {
  return writeLeadViewMembershipOverrides(viewId, payload, context, 'include');
}

/**
 * @function excludeLeadViewMembers
 * @description Removes selected leads from a Lead view as manual exclude overrides.
 * @param {string} viewId Lead view id.
 * @param {object} payload Membership payload.
 * @param {object} context Request context.
 * @returns {Promise<object|null>} Exclude result.
 * @collaboration Selected-row remove action, live collection membership, backend evidence, and audit receipts.
 */
async function excludeLeadViewMembers(viewId, payload = {}, context = {}) {
  return writeLeadViewMembershipOverrides(viewId, payload, context, 'exclude');
}

/**
 * @function clearLeadViewMembershipOverride
 * @description Clears a manual membership override for a Lead view and records audit evidence.
 * @param {string} viewId Lead view id.
 * @param {string} leadId Lead id.
 * @param {object} context Request context.
 * @returns {Promise<object|null>} Clear result.
 * @collaboration Manual membership cleanup, audit retention, selected-row correction, and view productivity.
 */
async function clearLeadViewMembershipOverride(viewId, leadId, context = {}) {
  const view = await CrmLeadView.findOne({
    _id: viewId,
    tenantId: context.tenantId,
    status: 'active',
  });

  if (!view) return null;

  const existing = await CrmLeadViewMembershipOverride.findOne({
    tenantId: context.tenantId,
    viewId: String(viewId),
    leadId: String(leadId || ''),
    status: 'active',
  });

  if (!existing) {
    return {
      view: view.toObject(),
      cleared: false,
      leadId: String(leadId || ''),
      membership: await listLeadViewMembershipOverrides(viewId, context),
    };
  }

  existing.status = 'cleared';
  existing.updatedBy = context.operatorUserId;
  existing.institutionalHeaders = context.institutionalHeaders;
  existing.strikePayload = context.strikePayload;
  await existing.save();

  const auditReceiptId = createAuditReceiptId('clear');
  view.updatedBy = context.operatorUserId;
  view.auditTrail.push(
    buildAuditEntry({
      auditReceiptId,
      action: 'CLEAR_LEAD_VIEW_MEMBERSHIP_OVERRIDE',
      route: `/api/crm/leads/views/${viewId}/overrides/${leadId}`,
      tenantId: context.tenantId,
      operatorUserId: context.operatorUserId,
      criteriaHash: view.criteriaHash,
      institutionalHeaders: context.institutionalHeaders,
      strikePayload: {
        ...context.strikePayload,
        leadId: String(leadId || ''),
        previousMode: existing.mode,
      },
    })
  );

  await view.save();

  return {
    view: view.toObject(),
    cleared: true,
    leadId: String(leadId || ''),
    auditReceiptId,
    membership: await listLeadViewMembershipOverrides(viewId, context),
  };
}

// P60K5Q10FG103B_VIEW_MEMBERSHIP_OVERRIDE_ENGINE

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
  const ruleMatchedLeads = leads.filter((lead) => doesLeadMatchCustomCriteria(lead, view.criteria));
  const membership = await applyLeadViewMembershipOverrides(view, ruleMatchedLeads, leads, context);
  const matchedLeads = membership.effectiveLeads;
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
      membership: membership.summary,
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
  clearLeadViewMembershipOverride,
  excludeLeadViewMembers,
  includeLeadViewMembers,
  listLeadViewMembershipOverrides,
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
