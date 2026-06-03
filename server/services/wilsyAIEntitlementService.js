/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - WILSY AI ENTITLEMENT SERVICE [V1.0.0-PRODUCTION-LICENSE-CORE]                                                             ║
 * ║ [MODULE CATALOG | TENANT ENTITLEMENTS | EXECUTIVE ACCESS GATES | SOURCE-GATED ACTIVATION | FORENSIC TELEMETRY]                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-LICENSE-CORE | PRODUCTION READY | CROSS-TENANT WILSY AI MONETISATION SERVICE                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/wilsyAIEntitlementService.js                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required Wilsy AI to license across tenants and dynamically adapt to each business.                  ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Built tenant-scoped module catalog, entitlement evaluation and activation receipts.            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import WilsyAILicense, { createWilsyAILicenseHash } from '../models/WilsyAILicense.js';
import WilsyAIUsage, { createWilsyAIUsageHash } from '../models/WilsyAIUsage.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { canBypassTenant } from '../config/roles.registry.js';

/**
 * @constant {Object<string, Object>}
 * @description Commercial Wilsy AI tier policy expressed in ZAR as the South African operating currency.
 * @collaboration A tenant must understand exactly what extra monthly value they are buying beyond generic chat access.
 */
export const WILSY_AI_TIER_POLICY = Object.freeze({
  WILSY_AI_STARTER: {
    label: 'Wilsy AI Starter',
    currency: 'ZAR',
    monthlyPrice: 499,
    setupPrice: 0,
    dailyRequestLimit: 35,
    monthlyAutomationLimit: 750,
    analystSeats: 1,
    maxAutonomousActionsPerDay: 5,
    approvalRequiredAboveValue: 2500,
    overagePricePerRequest: 3,
    valuePromise: 'Daily admin reduction, inbox triage, customer follow-ups and document capture.'
  },
  WILSY_AI_GROWTH: {
    label: 'Wilsy AI Growth',
    currency: 'ZAR',
    monthlyPrice: 1499,
    setupPrice: 750,
    dailyRequestLimit: 120,
    monthlyAutomationLimit: 3000,
    analystSeats: 3,
    maxAutonomousActionsPerDay: 25,
    approvalRequiredAboveValue: 10000,
    overagePricePerRequest: 2,
    valuePromise: 'Owner-grade cash, margin, stock and customer-work automation with controlled execution.'
  },
  WILSY_AI_INSTITUTIONAL: {
    label: 'Wilsy AI Institutional',
    currency: 'ZAR',
    monthlyPrice: 5499,
    setupPrice: 2500,
    dailyRequestLimit: 450,
    monthlyAutomationLimit: 12000,
    analystSeats: 12,
    maxAutonomousActionsPerDay: 100,
    approvalRequiredAboveValue: 50000,
    overagePricePerRequest: 1,
    valuePromise: 'Executive command automation, compliance evidence, industry playbooks and audit exports.'
  }
});

/**
 * @constant {Array<Object>}
 * @description Production Wilsy AI module catalog. Modules are reusable across tenants; tenant profile decides relevance.
 * @collaboration One licensable AI service can serve a bakery, construction firm, importer or corporate tenant without new source files.
 */
export const WILSY_AI_MODULE_CATALOG = Object.freeze([
  {
    moduleId: 'owner_inbox_triage',
    name: 'Wilsy AI Owner Inbox Triage',
    tier: 'WILSY_AI_STARTER',
    lanes: ['Executive', 'Administration', 'Customer'],
    industries: ['general_smb', 'bakery_food_service', 'import_logistics_agri', 'construction_projects'],
    sourceRequirements: ['telemetry'],
    entitlements: ['ai.inbox.triage', 'ai.customer.follow_up', 'ai.admin.summary'],
    requestType: 'INBOX_TRIAGE',
    differentiator: 'Turns messy owner/customer communication into ranked action queues with audit receipts.',
    baseMinutesSavedPerRequest: 12,
    baseValueZarPerRequest: 95
  },
  {
    moduleId: 'cash_gap_assistant',
    name: 'Wilsy AI Cash Gap Assistant',
    tier: 'WILSY_AI_GROWTH',
    lanes: ['Finance', 'Executive'],
    industries: ['general_smb', 'bakery_food_service', 'import_logistics_agri', 'construction_projects'],
    sourceRequirements: ['finance'],
    entitlements: ['ai.finance.cash_gap', 'ai.invoice.follow_up', 'ai.margin.warning'],
    requestType: 'CASH_GAP_ANALYSIS',
    differentiator: 'Finds daily cash pressure, overdue drag and margin leaks before the owner feels them.',
    baseMinutesSavedPerRequest: 22,
    baseValueZarPerRequest: 260
  },
  {
    moduleId: 'stock_and_supply_guard',
    name: 'Wilsy AI Stock and Supply Guard',
    tier: 'WILSY_AI_GROWTH',
    lanes: ['Operations', 'Supply', 'Logistics'],
    industries: ['bakery_food_service', 'import_logistics_agri', 'construction_projects'],
    sourceRequirements: ['records', 'telemetry'],
    entitlements: ['ai.stock.aging', 'ai.supplier.exception', 'ai.procurement.recommendation'],
    requestType: 'STOCK_SUPPLY_CHECK',
    differentiator: 'Detects aging stock, supplier blockers and procurement exceptions from tenant records.',
    baseMinutesSavedPerRequest: 18,
    baseValueZarPerRequest: 210
  },
  {
    moduleId: 'executive_compliance_sentinel',
    name: 'Wilsy AI Executive Compliance Sentinel',
    tier: 'WILSY_AI_INSTITUTIONAL',
    lanes: ['Compliance', 'Executive', 'Delivery'],
    industries: ['general_smb', 'bakery_food_service', 'import_logistics_agri', 'construction_projects'],
    sourceRequirements: ['records', 'telemetry'],
    entitlements: ['ai.compliance.checklist', 'ai.evidence.collector', 'ai.audit.export'],
    requestType: 'COMPLIANCE_SENTINEL',
    differentiator: 'Builds daily compliance evidence packs instead of waiting for year-end audit panic.',
    baseMinutesSavedPerRequest: 30,
    baseValueZarPerRequest: 420
  },
  {
    moduleId: 'industry_command_agent',
    name: 'Wilsy AI Industry Command Agent',
    tier: 'WILSY_AI_INSTITUTIONAL',
    lanes: ['Operations', 'Logistics', 'Delivery'],
    industries: ['import_logistics_agri', 'construction_projects'],
    sourceRequirements: ['finance', 'records', 'telemetry'],
    entitlements: ['ai.industry.playbook', 'ai.exception.routing', 'ai.executive.command_recommendation'],
    requestType: 'INDUSTRY_COMMAND',
    differentiator: 'Adapts to the tenant industry and recommends the next operational command with source proof.',
    baseMinutesSavedPerRequest: 45,
    baseValueZarPerRequest: 720
  }
]);

/**
 * @function normalizeTenantId
 * @description Normalizes tenant IDs for persisted Wilsy AI entitlements.
 * @param {string} tenantId - Candidate tenant id.
 * @returns {string} Uppercase tenant id.
 * @collaboration Keeps tenant-scoped license keys stable across client, server and billing exports.
 */
export const normalizeTenantId = (tenantId = 'GLOBAL_ROOT') => String(tenantId || 'GLOBAL_ROOT').trim().toUpperCase();

/**
 * @function getWilsyAITierPolicy
 * @description Resolves commercial request policy for a Wilsy AI tier.
 * @param {string} tier - Wilsy AI tier id.
 * @returns {Object} Tier policy.
 * @collaboration Pricing, quotas and value promises must live in one place so sales, billing and dashboards do not diverge.
 */
export const getWilsyAITierPolicy = (tier = 'WILSY_AI_STARTER') => (
  WILSY_AI_TIER_POLICY[tier] || WILSY_AI_TIER_POLICY.WILSY_AI_STARTER
);

/**
 * @function getDateWindow
 * @description Builds start/end dates for daily or monthly usage aggregation.
 * @param {string} window - Window type.
 * @returns {{start:Date,end:Date}}
 * @collaboration Quota governance needs precise time windows to avoid billing disputes.
 */
const getDateWindow = (window = 'day') => {
  const end = new Date();
  const start = new Date(end);
  if (window === 'month') {
    start.setDate(1);
    start.setHours(0, 0, 0, 0);
    return { start, end };
  }
  start.setHours(0, 0, 0, 0);
  return { start, end };
};

/**
 * @function buildUsageMatch
 * @description Builds a tenant-isolated usage query for module or license analytics.
 * @param {Object} params - Match inputs.
 * @returns {Object} Mongo match query.
 * @collaboration Tenant usage must never bleed across customers, modules or licenses.
 */
const buildUsageMatch = ({ tenantId, moduleId = null, licenseId = null, window = 'day' } = {}) => {
  const { start, end } = getDateWindow(window);
  return {
    tenantId: normalizeTenantId(tenantId),
    ...(moduleId ? { moduleId } : {}),
    ...(licenseId ? { licenseId } : {}),
    createdAt: { $gte: start, $lte: end }
  };
};

/**
 * @function summarizeUsageRows
 * @description Converts usage aggregates into a compact analytics packet.
 * @param {Array<Object>} rows - Aggregate rows.
 * @returns {Object} Usage summary.
 * @collaboration Wilsy AI analytics should explain request usage and value without fabricating activity.
 */
const summarizeUsageRows = (rows = []) => {
  const row = rows?.[0] || {};
  const requestUnits = Number(row.requestUnits || 0);
  const estimatedValueZar = Number(row.estimatedValueZar || 0);
  const totalChargeZar = Number(row.totalChargeZar || 0);
  return {
    requestUnits,
    estimatedMinutesSaved: Number(row.estimatedMinutesSaved || 0),
    estimatedValueZar,
    overageChargeZar: totalChargeZar,
    roiMultiple: totalChargeZar > 0 ? Number((estimatedValueZar / totalChargeZar).toFixed(2)) : 0
  };
};

/**
 * @function aggregateWilsyAIUsage
 * @description Aggregates daily and monthly Wilsy AI usage for a tenant/module/license.
 * @param {Object} params - Aggregation inputs.
 * @returns {Promise<Object>} Usage analytics.
 * @collaboration Request limits and ROI must be measured from usage rows, not guessed by the UI.
 */
export const aggregateWilsyAIUsage = async ({ tenantId, moduleId = null, licenseId = null, tier = 'WILSY_AI_STARTER' } = {}) => {
  const policy = getWilsyAITierPolicy(tier);
  const aggregate = match => WilsyAIUsage.aggregate([
    { $match: match },
    {
      $group: {
        _id: null,
        requestUnits: { $sum: '$metering.requestUnits' },
        estimatedMinutesSaved: { $sum: '$valueMetrics.estimatedMinutesSaved' },
        estimatedValueZar: { $sum: '$valueMetrics.estimatedValueZar' },
        totalChargeZar: { $sum: '$billing.overageCharge' }
      }
    }
  ]);
  const [dailyRows, monthlyRows] = await Promise.all([
    aggregate(buildUsageMatch({ tenantId, moduleId, licenseId, window: 'day' })),
    aggregate(buildUsageMatch({ tenantId, moduleId, licenseId, window: 'month' }))
  ]);
  const daily = summarizeUsageRows(dailyRows);
  const monthly = summarizeUsageRows(monthlyRows);
  return {
    sourceStatus: 'USAGE_LEDGER_LIVE',
    policy,
    daily,
    monthly,
    remainingDailyRequests: Math.max(0, policy.dailyRequestLimit - daily.requestUnits),
    remainingMonthlyAutomations: Math.max(0, policy.monthlyAutomationLimit - monthly.requestUnits),
    quotaStatus: daily.requestUnits >= policy.dailyRequestLimit
      ? 'DAILY_QUOTA_EXHAUSTED'
      : monthly.requestUnits >= policy.monthlyAutomationLimit
        ? 'MONTHLY_AUTOMATION_QUOTA_EXHAUSTED'
        : 'QUOTA_AVAILABLE'
  };
};

/**
 * @function buildSourceSilentUsageAnalytics
 * @description Builds a no-fake-data usage packet when the usage ledger is unavailable.
 * @param {Object} params - Analytics inputs.
 * @returns {Object} Source-silent analytics packet.
 * @collaboration A source-silent usage ledger must not create fake zero-value ROI claims.
 */
export const buildSourceSilentUsageAnalytics = ({ tier = 'WILSY_AI_STARTER', error = null } = {}) => ({
  sourceStatus: 'USAGE_LEDGER_SOURCE_SILENT',
  policy: getWilsyAITierPolicy(tier),
  daily: {
    requestUnits: null,
    estimatedMinutesSaved: null,
    estimatedValueZar: null,
    overageChargeZar: null,
    roiMultiple: null
  },
  monthly: {
    requestUnits: null,
    estimatedMinutesSaved: null,
    estimatedValueZar: null,
    overageChargeZar: null,
    roiMultiple: null
  },
  remainingDailyRequests: null,
  remainingMonthlyAutomations: null,
  quotaStatus: 'USAGE_SOURCE_REQUIRED',
  error: error?.message || null
});

/**
 * @function resolveRequestTypeForModule
 * @description Resolves a metering request type from a Wilsy AI module id.
 * @param {string} moduleId - Module id.
 * @returns {string} Usage request type.
 * @collaboration Request analytics should remain module-aware even when a workflow submits a generic usage record.
 */
export const resolveRequestTypeForModule = (moduleId = '') => (
  WILSY_AI_MODULE_CATALOG.find(module => module.moduleId === moduleId)?.requestType || 'CUSTOM_EXECUTIVE_TASK'
);

/**
 * @function estimateWilsyAIRequestValue
 * @description Estimates practical value for a Wilsy AI request using module economics.
 * @param {Object} params - Value inputs.
 * @returns {Object} Value metric packet.
 * @collaboration Wilsy AI must prove it saves time or prevents loss; this gives every request an explainable value lens.
 */
export const estimateWilsyAIRequestValue = ({ moduleId = '', requestUnits = 1, tier = 'WILSY_AI_STARTER' } = {}) => {
  const module = WILSY_AI_MODULE_CATALOG.find(item => item.moduleId === moduleId) || {};
  const policy = getWilsyAITierPolicy(tier);
  const units = Math.max(1, Number(requestUnits || 1));
  const estimatedMinutesSaved = Number(module.baseMinutesSavedPerRequest || 10) * units;
  const estimatedValueZar = Number(module.baseValueZarPerRequest || 80) * units;
  const impliedRequestCost = policy.monthlyPrice / Math.max(1, policy.monthlyAutomationLimit);
  return {
    estimatedMinutesSaved,
    estimatedValueZar,
    avoidedRiskZar: module.requestType === 'COMPLIANCE_SENTINEL' ? estimatedValueZar * 2 : 0,
    roiMultiple: impliedRequestCost > 0 ? Number((estimatedValueZar / impliedRequestCost).toFixed(2)) : 0
  };
};

/**
 * @function recordWilsyAIUsage
 * @description Records a tenant-scoped Wilsy AI usage request after quota checks.
 * @param {Object} params - Usage inputs.
 * @returns {Promise<Object>} Usage receipt.
 * @collaboration This is the monetisation spine for Wilsy AI requests: quota, value, usage ledger and telemetry.
 */
export const recordWilsyAIUsage = async ({
  req,
  moduleId = '',
  licenseId = '',
  tier = 'WILSY_AI_STARTER',
  requestType = '',
  requestUnits = 1,
  status = 'PLANNED',
  sourceStatus = 'REQUEST_CONTEXT',
  sourceEvidence = '',
  sourceSnapshot = {}
} = {}) => {
  const tenantId = getRequestTenantId(req);
  const access = assertWilsyAIExecutiveAccess(req, tenantId);
  if (!access.allowed) {
    const proofHash = createWilsyAIUsageHash({ tenantId, moduleId, access, requestUnits });
    await broadcastTelemetry(tenantId, 'WILSY_AI_USAGE_ACCESS_DENIED', 'DENIED', 'wilsyAIEntitlementService', {
      moduleId,
      reason: access.reason,
      proofHash
    }).catch(() => {});
    const error = new Error(access.reason);
    error.status = 403;
    error.code = 'WILSY_AI_USAGE_ACCESS_DENIED';
    error.proofHash = proofHash;
    throw error;
  }

  const policy = getWilsyAITierPolicy(tier);
  const usageBefore = await aggregateWilsyAIUsage({ tenantId, moduleId, licenseId, tier }).catch(error => (
    buildSourceSilentUsageAnalytics({ tier, error })
  ));
  const units = Math.max(1, Number(requestUnits || 1));
  const quotaBlocked = Number(usageBefore.daily?.requestUnits || 0) + units > policy.dailyRequestLimit
    || Number(usageBefore.monthly?.requestUnits || 0) + units > policy.monthlyAutomationLimit;
  const finalStatus = quotaBlocked ? 'BLOCKED_BY_QUOTA' : status;
  const overageCharge = quotaBlocked ? units * policy.overagePricePerRequest : 0;
  const valueMetrics = estimateWilsyAIRequestValue({ moduleId, requestUnits: units, tier });
  const actor = {
    userId: req.user?.id || req.user?._id?.toString() || '',
    email: req.user?.email || '',
    role: req.user?.role || ''
  };
  const usage = await WilsyAIUsage.create({
    tenantId,
    licenseId,
    moduleId,
    tier,
    requestType: requestType || resolveRequestTypeForModule(moduleId),
    status: finalStatus,
    actor,
    metering: {
      requestUnits: units,
      inputTokens: Number(req.body?.inputTokens || 0),
      outputTokens: Number(req.body?.outputTokens || 0),
      automationActions: Number(req.body?.automationActions || 0)
    },
    valueMetrics,
    billing: {
      currency: 'ZAR',
      includedInPlan: !quotaBlocked,
      overageCharge
    },
    source: {
      sourceStatus,
      sourceEvidence,
      sourceSnapshotHash: createWilsyAILicenseHash(sourceSnapshot || {})
    }
  });
  const usageAfter = await aggregateWilsyAIUsage({ tenantId, moduleId, licenseId, tier }).catch(error => (
    buildSourceSilentUsageAnalytics({ tier, error })
  ));

  await broadcastTelemetry(tenantId, 'WILSY_AI_USAGE_RECORDED', finalStatus, 'wilsyAIEntitlementService', {
    usageId: usage.usageId,
    moduleId,
    tier,
    requestUnits: units,
    quotaStatus: usageAfter.quotaStatus,
    proofHash: usage.proof.hash
  }).catch(() => {});

  return {
    success: !quotaBlocked,
    status: finalStatus,
    tenantId,
    usage: usage.toObject(),
    analytics: usageAfter,
    proofHash: usage.proof.hash
  };
};

/**
 * @function getRequestTenantId
 * @description Resolves the protected tenant scope from request context, headers or payload.
 * @param {Object} req - Express request.
 * @returns {string} Tenant id.
 * @collaboration Wilsy AI cannot license across tenants without a concrete tenant anchor.
 */
export const getRequestTenantId = (req = {}) => normalizeTenantId(
  req.tenantId
  || req.tenantContext?.id
  || req.headers?.['x-tenant-id']
  || req.body?.tenantId
  || req.query?.tenantId
  || req.user?.tenantId
  || 'GLOBAL_ROOT'
);

/**
 * @function assertWilsyAIExecutiveAccess
 * @description Enforces executive/owner-only Wilsy AI licensing rights.
 * @param {Object} req - Express request.
 * @param {string} tenantId - Target tenant id.
 * @returns {{allowed:boolean,reason:string,role:string,userTenantId:string}}
 * @collaboration Sales users may use sales tools, but they cannot activate executive AI licensing.
 */
export const assertWilsyAIExecutiveAccess = (req = {}, tenantId = 'GLOBAL_ROOT') => {
  const role = String(req.user?.role || '').toLowerCase();
  const userTenantId = normalizeTenantId(req.user?.tenantId || tenantId);
  const targetTenantId = normalizeTenantId(tenantId);
  const sovereign = canBypassTenant(req.user?.role) || ['founder', 'omega', 'super_admin', 'executive'].includes(role);
  const owner = role === 'tenant_owner';
  const sameTenant = userTenantId === targetTenantId || userTenantId === 'MASTER' || targetTenantId === 'GLOBAL_ROOT';

  if ((sovereign || owner) && sameTenant) {
    return {
      allowed: true,
      reason: 'WILSY_AI_EXECUTIVE_ACCESS_GRANTED',
      role,
      userTenantId
    };
  }

  return {
    allowed: false,
    reason: role === 'sales_representative'
      ? 'Sales representatives cannot activate executive Wilsy AI licenses.'
      : `Role ${role || 'unknown'} cannot activate Wilsy AI for tenant ${targetTenantId}.`,
    role,
    userTenantId
  };
};

/**
 * @function sourceIsLive
 * @description Evaluates a named source heartbeat from client or backend source snapshots.
 * @param {Object} sourceSnapshot - Source registry.
 * @param {string} key - Source key.
 * @returns {boolean} True when the source is live.
 * @collaboration Entitlements are source-gated; Wilsy AI does not pretend missing rails are active.
 */
export const sourceIsLive = (sourceSnapshot = {}, key = '') => Boolean(sourceSnapshot?.[key]?.live || sourceSnapshot?.sources?.[key]?.live);

/**
 * @function resolveModuleReadiness
 * @description Resolves whether a module can activate for a tenant profile and source posture.
 * @param {Object} module - Catalog module.
 * @param {Object} params - Readiness inputs.
 * @returns {{status:string,missingSources:Array<string>,reason:string}}
 * @collaboration Makes the license decision explainable to executives and sales without fake backend claims.
 */
export const resolveModuleReadiness = (module = {}, { tenantProfile = {}, sourceSnapshot = {} } = {}) => {
  const industryKey = tenantProfile.industryKey || 'general_smb';
  const industryFit = !module.industries?.length || module.industries.includes(industryKey);
  const missingSources = (module.sourceRequirements || []).filter(source => !sourceIsLive(sourceSnapshot, source));

  if (!industryFit) {
    return {
      status: 'NOT_TENANT_FIT',
      missingSources,
      reason: `${module.name} is not the primary fit for ${tenantProfile.industryLabel || industryKey}.`
    };
  }

  if (missingSources.length) {
    return {
      status: 'PENDING_SOURCE',
      missingSources,
      reason: `Connect ${missingSources.join(', ')} before this Wilsy AI module can execute.`
    };
  }

  return {
    status: 'READY_TO_LICENSE',
    missingSources: [],
    reason: 'Tenant profile and source posture satisfy Wilsy AI licensing gates.'
  };
};

/**
 * @function buildWilsyAICatalogForTenant
 * @description Builds the tenant-filtered module catalog with active license status.
 * @param {Object} params - Catalog inputs.
 * @returns {Array<Object>} Module rows.
 * @collaboration This catalog is the reusable Wilsy AI product shelf for every tenant.
 */
export const buildWilsyAICatalogForTenant = ({ tenantId, tenantProfile = {}, sourceSnapshot = {}, licenses = [] } = {}) => {
  const licenseByModule = new Map(licenses.map(license => [license.moduleId, license]));
  return WILSY_AI_MODULE_CATALOG.map(module => {
    const readiness = resolveModuleReadiness(module, { tenantProfile, sourceSnapshot });
    const license = licenseByModule.get(module.moduleId);
    const tierPolicy = getWilsyAITierPolicy(module.tier);
    const packet = {
      tenantId: normalizeTenantId(tenantId),
      moduleId: module.moduleId,
      tier: module.tier,
      industryKey: tenantProfile.industryKey,
      readiness: readiness.status,
      licenseStatus: license?.status || 'UNLICENSED'
    };
    return {
      ...module,
      readiness: readiness.status,
      missingSources: readiness.missingSources,
      reason: readiness.reason,
      licenseId: license?.licenseId || null,
      licenseStatus: license?.status || 'UNLICENSED',
      tierPolicy,
      monthlyPriceZar: tierPolicy.monthlyPrice,
      setupPriceZar: tierPolicy.setupPrice,
      dailyRequestLimit: tierPolicy.dailyRequestLimit,
      monthlyAutomationLimit: tierPolicy.monthlyAutomationLimit,
      analystSeats: tierPolicy.analystSeats,
      approvalRequiredAboveValue: tierPolicy.approvalRequiredAboveValue,
      overagePricePerRequestZar: tierPolicy.overagePricePerRequest,
      valuePromise: tierPolicy.valuePromise,
      differentiator: module.differentiator,
      requestType: module.requestType,
      usageSnapshot: license?.usageSnapshot || null,
      proofHash: createWilsyAILicenseHash(packet)
    };
  });
};

/**
 * @function getWilsyAIEntitlements
 * @description Loads active tenant licenses and returns the current Wilsy AI entitlement posture.
 * @param {Object} params - Entitlement inputs.
 * @returns {Promise<Object>} Entitlement response.
 * @collaboration Gives dashboards and APIs the same source of truth for licensed Wilsy AI modules.
 */
export const getWilsyAIEntitlements = async ({ tenantId, tenantProfile = {}, sourceSnapshot = {} } = {}) => {
  const normalizedTenantId = normalizeTenantId(tenantId);
  const licenses = await WilsyAILicense.find({ tenantId: normalizedTenantId }).lean();
  const baseCatalog = buildWilsyAICatalogForTenant({
    tenantId: normalizedTenantId,
    tenantProfile,
    sourceSnapshot,
    licenses
  });
  const catalog = await Promise.all(baseCatalog.map(async module => {
    const usageAnalytics = await aggregateWilsyAIUsage({
      tenantId: normalizedTenantId,
      moduleId: module.moduleId,
      licenseId: module.licenseId,
      tier: module.tier
    }).catch(error => buildSourceSilentUsageAnalytics({ tier: module.tier, error }));
    return {
      ...module,
      usageAnalytics
    };
  }));

  return {
    success: true,
    status: 'WILSY_AI_ENTITLEMENTS_READY',
    tenantId: normalizedTenantId,
    catalog,
    licenses,
    analytics: {
      sourceStatus: 'USAGE_LEDGER_LIVE',
      totalDailyRequests: catalog.reduce((sum, item) => sum + Number(item.usageAnalytics?.daily?.requestUnits || 0), 0),
      totalMonthlyRequests: catalog.reduce((sum, item) => sum + Number(item.usageAnalytics?.monthly?.requestUnits || 0), 0),
      totalEstimatedValueZar: catalog.reduce((sum, item) => sum + Number(item.usageAnalytics?.monthly?.estimatedValueZar || 0), 0),
      activeLicenses: licenses.filter(license => license.status === 'ACTIVE').length
    },
    proofHash: createWilsyAILicenseHash({
      tenantId: normalizedTenantId,
      catalog: catalog.map(item => ({
        moduleId: item.moduleId,
        readiness: item.readiness,
        licenseStatus: item.licenseStatus,
        quotaStatus: item.usageAnalytics?.quotaStatus
      }))
    })
  };
};

/**
 * @function activateWilsyAILicense
 * @description Activates or updates a tenant-scoped Wilsy AI module license.
 * @param {Object} params - Activation inputs.
 * @returns {Promise<Object>} Activation receipt.
 * @collaboration Turns Wilsy AI into a real product entitlement with billing-ready proof.
 */
export const activateWilsyAILicense = async ({ req, moduleId, tenantProfile = {}, sourceSnapshot = {}, dailyDutyKey = '' } = {}) => {
  const tenantId = getRequestTenantId(req);
  const access = assertWilsyAIExecutiveAccess(req, tenantId);
  if (!access.allowed) {
    const proofHash = createWilsyAILicenseHash({ tenantId, moduleId, access });
    await broadcastTelemetry(tenantId, 'WILSY_AI_ACCESS_DENIED', 'DENIED', 'wilsyAIEntitlementService', {
      moduleId,
      reason: access.reason,
      proofHash
    }).catch(() => {});
    const error = new Error(access.reason);
    error.status = 403;
    error.code = 'WILSY_AI_ACCESS_DENIED';
    error.proofHash = proofHash;
    throw error;
  }

  const module = WILSY_AI_MODULE_CATALOG.find(item => item.moduleId === moduleId);
  if (!module) {
    const error = new Error(`Unknown Wilsy AI module: ${moduleId}`);
    error.status = 404;
    error.code = 'WILSY_AI_MODULE_NOT_FOUND';
    throw error;
  }

  const readiness = resolveModuleReadiness(module, { tenantProfile, sourceSnapshot });
  const status = readiness.status === 'READY_TO_LICENSE' ? 'ACTIVE' : 'PENDING_SOURCE';
  const tierPolicy = getWilsyAITierPolicy(module.tier);
  const usageAnalytics = await aggregateWilsyAIUsage({
    tenantId,
    moduleId,
    tier: module.tier
  }).catch(error => buildSourceSilentUsageAnalytics({ tier: module.tier, error }));
  const traceId = `WAI-${crypto.randomBytes(6).toString('hex').toUpperCase()}`;
  const actor = req.user?.email || req.user?.id || 'EXECUTIVE_OPERATOR';
  const receiptProof = createWilsyAILicenseHash({
    tenantId,
    moduleId,
    status,
    actor,
    traceId,
    readiness
  });
  const licenseId = `WILSY-AI-${tenantId}-${crypto.randomBytes(5).toString('hex').toUpperCase()}`;

  const license = await WilsyAILicense.findOneAndUpdate(
    { tenantId, moduleId },
    {
      $setOnInsert: {
        licenseId
      },
      $set: {
        tenantId,
        moduleId,
        moduleName: module.name,
        tier: module.tier,
        status,
        businessProfile: {
          industryKey: tenantProfile.industryKey,
          industryLabel: tenantProfile.industryLabel,
          sourceStatus: tenantProfile.sourceStatus,
          sourceEvidence: tenantProfile.sourceEvidence
        },
        dailyDutyKey,
        lane: module.lanes?.[0] || 'Executive',
        commercials: {
          currency: tierPolicy.currency,
          monthlyPrice: tierPolicy.monthlyPrice,
          setupPrice: tierPolicy.setupPrice,
          overagePricePerRequest: tierPolicy.overagePricePerRequest,
          vatRate: 0.15,
          billingModel: 'MONTHLY_ADD_ON',
          valuePromise: tierPolicy.valuePromise
        },
        requestPolicy: {
          dailyRequestLimit: tierPolicy.dailyRequestLimit,
          monthlyAutomationLimit: tierPolicy.monthlyAutomationLimit,
          analystSeats: tierPolicy.analystSeats,
          maxAutonomousActionsPerDay: tierPolicy.maxAutonomousActionsPerDay,
          approvalRequiredAboveValue: tierPolicy.approvalRequiredAboveValue,
          currency: tierPolicy.currency
        },
        usageSnapshot: {
          dailyRequestsUsed: usageAnalytics.daily?.requestUnits || 0,
          monthlyRequestsUsed: usageAnalytics.monthly?.requestUnits || 0,
          estimatedMinutesSaved: usageAnalytics.monthly?.estimatedMinutesSaved || 0,
          estimatedValueZar: usageAnalytics.monthly?.estimatedValueZar || 0,
          roiMultiple: usageAnalytics.monthly?.roiMultiple || 0,
          sourceStatus: usageAnalytics.sourceStatus,
          lastSync: new Date()
        },
        sourceRequirements: module.sourceRequirements,
        entitlements: module.entitlements,
        activation: {
          mode: 'EXECUTIVE_COMMAND',
          activatedBy: actor,
          activatedAt: new Date(),
          reason: readiness.reason
        }
      },
      $push: {
        receipts: {
          eventType: 'WILSY_AI_LICENSE_ACTIVATION',
          status,
          actor,
          traceId,
          proofHash: receiptProof
        }
      }
    },
    { upsert: true, new: true, runValidators: true, setDefaultsOnInsert: true }
  );

  license.sealLicense();
  await license.save();

  await broadcastTelemetry(tenantId, 'WILSY_AI_LICENSE_ACTIVATION', status, 'wilsyAIEntitlementService', {
    moduleId,
    licenseId: license.licenseId,
    tier: license.tier,
    readiness,
    proofHash: license.proof.hash,
    traceId
  }).catch(() => {});

  return {
    success: true,
    status,
    tenantId,
    license: license.toObject(),
    readiness,
    traceId,
    proofHash: license.proof.hash
  };
};

export default {
  WILSY_AI_MODULE_CATALOG,
  WILSY_AI_TIER_POLICY,
  getWilsyAITierPolicy,
  getRequestTenantId,
  assertWilsyAIExecutiveAccess,
  resolveModuleReadiness,
  buildWilsyAICatalogForTenant,
  aggregateWilsyAIUsage,
  buildSourceSilentUsageAnalytics,
  resolveRequestTypeForModule,
  estimateWilsyAIRequestValue,
  getWilsyAIEntitlements,
  activateWilsyAILicense,
  recordWilsyAIUsage
};
