/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - WILSY AI LICENSE SERVICE [V1.0.0-STRATEGIC-MONETISATION]                                                                  ║
 * ║ [TENANT-ADAPTIVE AI LICENSING | SOURCE-GATED RECOMMENDATIONS | EXECUTIVE PRODUCTIVITY LADDERS | NO-FAKE-DATA POLICY]                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-STRATEGIC-MONETISATION | PRODUCTION READY | ADD-ON AI SERVICE COMMAND ENGINE                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/WilsyAIService.js                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Named the monetisable AI layer "Wilsy AI" and mandated tenant-specific daily business value.        ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Built source-gated AI license planning that proposes useful add-ons without synthetic data.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { sha3_512 } from 'js-sha3';
import sovereignClient from '../utils/sovereignClient';

/**
 * @constant {Object<string, string>}
 * @description Maps operational lanes to Wilsy AI license tiers without hard-coded revenue claims.
 * @collaboration Lets a bakery, logistics importer or construction firm receive the right AI service offer without rebuilding the UI.
 */
const WILSY_AI_TIER_BY_LANE = Object.freeze({
  Finance: 'WILSY_AI_GROWTH',
  Operations: 'WILSY_AI_GROWTH',
  Logistics: 'WILSY_AI_INSTITUTIONAL',
  Delivery: 'WILSY_AI_INSTITUTIONAL',
  Compliance: 'WILSY_AI_INSTITUTIONAL',
  Sales: 'WILSY_AI_GROWTH',
  Customer: 'WILSY_AI_STARTER',
  Supply: 'WILSY_AI_GROWTH',
  Administration: 'WILSY_AI_STARTER',
  Executive: 'WILSY_AI_GROWTH',
  'Wilsy AI': 'WILSY_AI_GROWTH'
});

/**
 * @constant {Object<string, Object>}
 * @description Client mirror of Wilsy AI commercial tiers for local planning when backend entitlements are source-silent.
 * @collaboration The backend remains the licensing authority; this mirror keeps the UI useful without pretending a license exists.
 */
export const WILSY_AI_TIER_POLICY = Object.freeze({
  WILSY_AI_STARTER: {
    label: 'Wilsy AI Starter',
    currency: 'ZAR',
    monthlyPriceZar: 499,
    setupPriceZar: 0,
    dailyRequestLimit: 35,
    monthlyAutomationLimit: 750,
    analystSeats: 1,
    maxAutonomousActionsPerDay: 5,
    approvalRequiredAboveValue: 2500,
    overagePricePerRequestZar: 3,
    valuePromise: 'Inbox triage, customer follow-up, document capture and admin summaries.'
  },
  WILSY_AI_GROWTH: {
    label: 'Wilsy AI Growth',
    currency: 'ZAR',
    monthlyPriceZar: 1499,
    setupPriceZar: 750,
    dailyRequestLimit: 120,
    monthlyAutomationLimit: 3000,
    analystSeats: 3,
    maxAutonomousActionsPerDay: 25,
    approvalRequiredAboveValue: 10000,
    overagePricePerRequestZar: 2,
    valuePromise: 'Cash, margin, customer and operational automation for owner-led businesses.'
  },
  WILSY_AI_INSTITUTIONAL: {
    label: 'Wilsy AI Institutional',
    currency: 'ZAR',
    monthlyPriceZar: 5499,
    setupPriceZar: 2500,
    dailyRequestLimit: 450,
    monthlyAutomationLimit: 12000,
    analystSeats: 12,
    maxAutonomousActionsPerDay: 100,
    approvalRequiredAboveValue: 50000,
    overagePricePerRequestZar: 1,
    valuePromise: 'Executive command automation, compliance evidence and industry playbooks.'
  }
});

/**
 * @constant {Object<string, string>}
 * @description Maps duty lanes to backend Wilsy AI module IDs.
 * @collaboration Keeps frontend recommendations aligned with the production server entitlement catalog.
 */
const WILSY_AI_MODULE_BY_LANE = Object.freeze({
  Finance: 'cash_gap_assistant',
  Operations: 'stock_and_supply_guard',
  Logistics: 'industry_command_agent',
  Delivery: 'industry_command_agent',
  Compliance: 'executive_compliance_sentinel',
  Sales: 'owner_inbox_triage',
  Customer: 'owner_inbox_triage',
  Supply: 'stock_and_supply_guard',
  Administration: 'owner_inbox_triage',
  Executive: 'owner_inbox_triage',
  'Wilsy AI': 'industry_command_agent'
});

/**
 * @function stableWilsyAIStringify
 * @description Serializes client Wilsy AI command packets with stable key ordering.
 * @param {unknown} value - Candidate value.
 * @returns {string} Stable JSON string.
 * @collaboration Client-side proofs must match the same determinism discipline as server license receipts.
 */
const stableWilsyAIStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableWilsyAIStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableWilsyAIStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createWilsyAIClientProof
 * @description Creates a client-side SHA3-512 proof for Wilsy AI plan and activation packets.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase digest.
 * @collaboration Gives the dashboard a proof before the backend activation receipt returns.
 */
export const createWilsyAIClientProof = (payload = {}) => sha3_512(stableWilsyAIStringify(payload)).toUpperCase();

/**
 * @function resolveLocalModuleId
 * @description Resolves the backend module ID for a local duty-driven Wilsy AI plan.
 * @param {Object} params - Module inputs.
 * @param {string} params.lane - Operational lane.
 * @param {string} params.industryKey - Tenant industry key.
 * @returns {string} Module ID.
 * @collaboration Ensures local planning and server licensing speak the same module language.
 */
const resolveLocalModuleId = ({ lane = 'Executive', industryKey = 'general_smb' } = {}) => {
  if (industryKey === 'import_logistics_agri' && ['Logistics', 'Operations', 'Supply', 'Wilsy AI'].includes(lane)) {
    return 'industry_command_agent';
  }
  if (industryKey === 'construction_projects' && ['Delivery', 'Operations', 'Supply', 'Wilsy AI'].includes(lane)) {
    return 'industry_command_agent';
  }
  return WILSY_AI_MODULE_BY_LANE[lane] || 'owner_inbox_triage';
};

/**
 * @function getWilsyAITierPolicy
 * @description Resolves the commercial policy for a Wilsy AI tier.
 * @param {string} tier - Tier id.
 * @returns {Object} Tier policy.
 * @collaboration Local planning can show transparent pricing even when the entitlement API is temporarily silent.
 */
export const getWilsyAITierPolicy = (tier = 'WILSY_AI_STARTER') => (
  WILSY_AI_TIER_POLICY[tier] || WILSY_AI_TIER_POLICY.WILSY_AI_STARTER
);

/**
 * @function slugWilsyAIUseCase
 * @description Creates a stable UI-only suffix for local Wilsy AI plan rows.
 * @param {string} useCase - Human use-case label.
 * @param {number} index - Fallback index.
 * @returns {string} Slug suffix.
 * @collaboration Multiple tenant duties can map to one licensed backend module; React still needs unique row identity.
 */
const slugWilsyAIUseCase = (useCase = '', index = 0) => (
  String(useCase || `use_case_${index}`)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 42)
  || `use_case_${index}`
);

/**
 * @function inferWilsyAiReadiness
 * @description Resolves whether a Wilsy AI use case can activate from available tenant sources.
 * @param {Object} params - Readiness inputs.
 * @param {Object} params.sourceSnapshot - Source registry from the Executive Dashboard.
 * @param {Object} params.accessDecision - Executive access decision.
 * @returns {{status:string,reason:string}}
 * @collaboration Wilsy AI must never promise automation when the tenant has not connected the needed evidence rails.
 */
export const inferWilsyAiReadiness = ({ sourceSnapshot = {}, accessDecision = {} } = {}) => {
  if (!accessDecision.allowed) {
    return {
      status: 'ACCESS_DENIED',
      reason: accessDecision.reason || 'Executive permission is required before Wilsy AI can be licensed.'
    };
  }

  if (!sourceSnapshot.finance?.live && !sourceSnapshot.records?.live) {
    return {
      status: 'SOURCE_REQUIRED',
      reason: 'Finance or tenant record source must be connected before automation can execute.'
    };
  }

  if (!sourceSnapshot.telemetry?.live) {
    return {
      status: 'TELEMETRY_DEGRADED',
      reason: 'Automation can be planned, but execution receipts need telemetry recovery.'
    };
  }

  return {
    status: 'READY_TO_LICENSE',
    reason: 'Tenant sources and executive authority are sufficient for Wilsy AI planning.'
  };
};

/**
 * @function buildWilsyAiLicensePlan
 * @description Builds tenant-specific Wilsy AI add-on opportunities from daily duties and business profile.
 * @param {Object} params - License plan inputs.
 * @param {Object} params.tenantProfile - Tenant industry profile from ExecutiveOperatingEngine.
 * @param {Array<Object>} params.dailyDuties - Daily executive duties generated for the tenant.
 * @param {Object} params.sourceSnapshot - Source heartbeat registry.
 * @param {Object} params.accessDecision - Executive access decision.
 * @returns {Array<Object>} Source-gated Wilsy AI license opportunities.
 * @collaboration Converts Wilsy AI into a practical add-on catalogue tied to work the tenant already needs done.
 */
export const buildWilsyAiLicensePlan = ({
  tenantProfile = {},
  dailyDuties = [],
  sourceSnapshot = {},
  accessDecision = {}
} = {}) => {
  const readiness = inferWilsyAiReadiness({ sourceSnapshot, accessDecision });
  const useCases = tenantProfile.archetype?.wilsyAiUseCases || [];
  const duties = dailyDuties.length ? dailyDuties : [];

  return useCases.slice(0, 4).map((useCase, index) => {
    const matchedDuty = duties[index] || duties.find(duty => duty.status === 'READY') || {};
    const lane = matchedDuty.lane || 'Executive';
    const moduleId = resolveLocalModuleId({ lane, industryKey: tenantProfile.industryKey });
    const tier = WILSY_AI_TIER_BY_LANE[lane] || 'WILSY_AI_GROWTH';
    const tierPolicy = getWilsyAITierPolicy(tier);
    const packet = {
      moduleId,
      useCase,
      tenantProfile,
      lane,
      readiness: readiness.status
    };
    return {
      id: `${moduleId}_${slugWilsyAIUseCase(useCase, index)}`,
      moduleId,
      name: `Wilsy AI - ${useCase}`,
      tier,
      lane,
      readiness: readiness.status,
      reason: readiness.reason,
      tenantFit: tenantProfile.industryLabel || 'Tenant-adaptive business workflow',
      dailyDutyKey: matchedDuty.key || 'executive_operating_duty',
      sourceStatus: matchedDuty.sourceStatus || tenantProfile.sourceStatus || 'TENANT_PROFILE_CONTEXT',
      licenseStatus: 'UNLICENSED_LOCAL_PLAN',
      ...tierPolicy,
      usageAnalytics: {
        sourceStatus: 'USAGE_LEDGER_NOT_SYNCED',
        daily: {
          requestUnits: null,
          estimatedMinutesSaved: null,
          estimatedValueZar: null,
          roiMultiple: null
        },
        monthly: {
          requestUnits: null,
          estimatedMinutesSaved: null,
          estimatedValueZar: null,
          roiMultiple: null
        },
        remainingDailyRequests: null,
        quotaStatus: 'USAGE_SOURCE_REQUIRED'
      },
      proofHash: createWilsyAIClientProof(packet)
    };
  });
};

/**
 * @function mapServerCatalogToPlans
 * @description Converts backend Wilsy AI catalog rows into dashboard plan rows.
 * @param {Array<Object>} catalog - Backend module catalog.
 * @param {Object} tenantProfile - Tenant business profile.
 * @returns {Array<Object>} Dashboard-ready license plan rows.
 * @collaboration Keeps the UI powered by production entitlement state when the backend is available.
 */
export const mapServerCatalogToPlans = (catalog = [], tenantProfile = {}) => (
  catalog.map(module => {
    const tierPolicy = module.tierPolicy || getWilsyAITierPolicy(module.tier);
    return {
      id: module.moduleId,
      moduleId: module.moduleId,
      name: module.name,
      tier: module.tier,
      lane: module.lanes?.[0] || 'Executive',
      readiness: module.readiness,
      reason: module.reason,
      tenantFit: tenantProfile.industryLabel || module.industries?.join(', ') || 'Tenant-adaptive business workflow',
      dailyDutyKey: module.dailyDutyKey || module.moduleId,
      sourceStatus: module.missingSources?.length ? `MISSING_${module.missingSources.join('_')}` : 'SERVER_ENTITLEMENT_CATALOG',
      differentiator: module.differentiator,
      requestType: module.requestType,
      licenseId: module.licenseId,
      licenseStatus: module.licenseStatus,
      monthlyPriceZar: module.monthlyPriceZar ?? tierPolicy.monthlyPriceZar ?? tierPolicy.monthlyPrice,
      setupPriceZar: module.setupPriceZar ?? tierPolicy.setupPriceZar ?? tierPolicy.setupPrice,
      dailyRequestLimit: module.dailyRequestLimit ?? tierPolicy.dailyRequestLimit,
      monthlyAutomationLimit: module.monthlyAutomationLimit ?? tierPolicy.monthlyAutomationLimit,
      analystSeats: module.analystSeats ?? tierPolicy.analystSeats,
      approvalRequiredAboveValue: module.approvalRequiredAboveValue ?? tierPolicy.approvalRequiredAboveValue,
      overagePricePerRequestZar: module.overagePricePerRequestZar ?? tierPolicy.overagePricePerRequestZar ?? tierPolicy.overagePricePerRequest,
      valuePromise: module.valuePromise || tierPolicy.valuePromise,
      usageAnalytics: module.usageAnalytics || {
        sourceStatus: 'USAGE_LEDGER_NOT_SYNCED',
        daily: {},
        monthly: {},
        remainingDailyRequests: null,
        quotaStatus: 'USAGE_SOURCE_REQUIRED'
      },
      proofHash: module.proofHash
    };
  })
);

/**
 * @function syncWilsyAIEntitlements
 * @description Fetches production Wilsy AI catalog and license posture for a tenant.
 * @param {Object} params - Sync inputs.
 * @returns {Promise<Object>} Entitlement sync packet.
 * @collaboration Licenses must come from the protected backend; local fallback is clearly marked source-silent.
 */
export const syncWilsyAIEntitlements = async ({
  tenantId = 'GLOBAL_ROOT',
  tenantProfile = {},
  sourceSnapshot = {}
} = {}) => {
  try {
    const response = await sovereignClient.post('/wilsy-ai/entitlements', {
      tenantId,
      tenantProfile,
      sourceSnapshot
    }, {
      headers: { 'X-Tenant-ID': tenantId },
      disableSourceBackoff: true
    });
    const payload = response?.data?.data || response?.data || {};
    return {
      success: Boolean(payload.success),
      status: payload.status || 'WILSY_AI_ENTITLEMENTS_READY',
      tenantId: payload.tenantId || tenantId,
      plans: mapServerCatalogToPlans(payload.catalog || [], tenantProfile),
      licenses: payload.licenses || [],
      analytics: payload.analytics || null,
      proofHash: payload.proofHash || createWilsyAIClientProof(payload)
    };
  } catch (error) {
    return {
      success: false,
      status: 'WILSY_AI_ENTITLEMENT_SOURCE_SILENT',
      tenantId,
      plans: [],
      licenses: [],
      analytics: null,
      error: error.response?.data?.message || error.message || 'Wilsy AI entitlement API unavailable.',
      proofHash: createWilsyAIClientProof({
        tenantId,
        sourceStatus: 'WILSY_AI_ENTITLEMENT_SOURCE_SILENT',
        tenantProfile
      })
    };
  }
};

/**
 * @function recordWilsyAIUsage
 * @description Records a source-aware Wilsy AI request for quota and ROI analytics.
 * @param {Object} params - Usage request inputs.
 * @returns {Promise<Object>} Usage receipt or source-silent failure packet.
 * @collaboration Wilsy AI is not better because it talks; it is better because every useful request becomes measurable business value.
 */
export const recordWilsyAIUsage = async ({
  tenantId = 'GLOBAL_ROOT',
  plan = {},
  requestUnits = 1,
  status = 'PLANNED',
  sourceStatus = 'REQUEST_CONTEXT',
  sourceEvidence = '',
  sourceSnapshot = {}
} = {}) => {
  try {
    const response = await sovereignClient.post('/wilsy-ai/usage/record', {
      tenantId,
      moduleId: plan.moduleId || plan.id,
      licenseId: plan.licenseId,
      tier: plan.tier,
      requestType: plan.requestType,
      requestUnits,
      status,
      sourceStatus,
      sourceEvidence,
      sourceSnapshot
    }, {
      headers: {
        'X-Tenant-ID': tenantId,
        'X-Wilsy-AI-Proof': createWilsyAIClientProof({ tenantId, plan, requestUnits, status })
      }
    });
    return response?.data?.data || response?.data || {};
  } catch (error) {
    return {
      success: false,
      status: 'WILSY_AI_USAGE_API_SOURCE_SILENT',
      code: error.response?.data?.code || 'WILSY_AI_USAGE_RECORD_FAILED',
      message: error.response?.data?.message || error.message || 'Wilsy AI usage recording failed.',
      proofHash: error.response?.data?.proofHash || createWilsyAIClientProof({ tenantId, plan, requestUnits, failed: true })
    };
  }
};

/**
 * @function activateWilsyAILicense
 * @description Requests backend activation for a tenant-scoped Wilsy AI module license.
 * @param {Object} params - Activation inputs.
 * @returns {Promise<Object>} Backend activation receipt or source-silent failure packet.
 * @collaboration The dashboard must never mark Wilsy AI as licensed unless the protected API returns a receipt.
 */
export const activateWilsyAILicense = async ({
  tenantId = 'GLOBAL_ROOT',
  plan = {},
  tenantProfile = {},
  sourceSnapshot = {}
} = {}) => {
  try {
    const response = await sovereignClient.post('/wilsy-ai/licenses/activate', {
      tenantId,
      moduleId: plan.moduleId || plan.id,
      dailyDutyKey: plan.dailyDutyKey,
      tenantProfile,
      sourceSnapshot
    }, {
      headers: {
        'X-Tenant-ID': tenantId,
        'X-Wilsy-AI-Proof': createWilsyAIClientProof({ tenantId, plan, tenantProfile })
      }
    });
    return response?.data?.data || response?.data || {};
  } catch (error) {
    return {
      success: false,
      status: 'WILSY_AI_LICENSE_API_SOURCE_SILENT',
      code: error.response?.data?.code || 'WILSY_AI_LICENSE_ACTIVATION_FAILED',
      message: error.response?.data?.message || error.message || 'Wilsy AI license activation failed.',
      proofHash: error.response?.data?.proofHash || createWilsyAIClientProof({ tenantId, plan, failed: true })
    };
  }
};

export default {
  inferWilsyAiReadiness,
  getWilsyAITierPolicy,
  buildWilsyAiLicensePlan,
  mapServerCatalogToPlans,
  syncWilsyAIEntitlements,
  activateWilsyAILicense,
  recordWilsyAIUsage
};
