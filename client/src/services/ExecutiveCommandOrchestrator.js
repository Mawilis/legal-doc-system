/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - EXECUTIVE COMMAND ORCHESTRATOR [V1.0.0-DAILY-BUSINESS-OS]                                                                 ║
 * ║ [TENANT BRANDING | DAILY WORK ORDERS | MODULE ROUTING | SOURCE REPAIR | EXECUTIVE COMMAND PROOFS]                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-DAILY-BUSINESS-OS | PRODUCTION READY | ACTIONABLE EXECUTIVE OPERATING LAYER                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/ExecutiveCommandOrchestrator.js                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO/Lead Architect) - Required executives to run a business from Wilsy OS, not stare at metric cards.      ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Added command routing, work-order proofs, source repair queues and tenant branding helpers.  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { sha3_512 } from 'js-sha3';

const DEFAULT_BRAND_PRIMARY = '#D4AF37';
const DEFAULT_BRAND_SECONDARY = '#56D69B';
const DEFAULT_BRAND_SURFACE = '#030504';

export const EXECUTIVE_FUNCTION_ROUTES = Object.freeze({
  executive_dashboard: { route: '/executive', command: 'EXEC_OPEN_EXECUTIVE_OS', channel: 'Executive' },
  billing: { route: '/billing', command: 'EXEC_OPEN_BILLING', channel: 'Finance' },
  inventory: { route: '/inventory', command: 'EXEC_OPEN_INVENTORY', channel: 'Operations' },
  logistics: { route: '/logistics', command: 'EXEC_OPEN_LOGISTICS', channel: 'Logistics' },
  crm: { route: '/crm', command: 'EXEC_OPEN_CRM', channel: 'Sales' },
  contracts: { route: '/contracts', command: 'EXEC_OPEN_CONTRACTS', channel: 'Legal' },
  currency_fx: { route: '/finance/currency', command: 'EXEC_OPEN_FX', channel: 'Finance' },
  wilsy_ai: { route: '/wilsy-ai', command: 'EXEC_OPEN_WILSY_AI', channel: 'Automation' },
  recipes: { route: '/operations/recipes', command: 'EXEC_OPEN_RECIPE_COSTING', channel: 'Operations' },
  quality: { route: '/compliance/quality', command: 'EXEC_OPEN_QUALITY', channel: 'Compliance' },
  pos: { route: '/sales/pos', command: 'EXEC_OPEN_POS', channel: 'Sales' },
  project_management: { route: '/projects', command: 'EXEC_OPEN_PROJECTS', channel: 'Delivery' },
  procurement: { route: '/procurement', command: 'EXEC_OPEN_PROCUREMENT', channel: 'Supply' },
  health_safety: { route: '/compliance/health-safety', command: 'EXEC_OPEN_HEALTH_SAFETY', channel: 'Compliance' },
  time_tracking: { route: '/operations/time', command: 'EXEC_OPEN_TIME_TRACKING', channel: 'Operations' },
  projects: { route: '/projects', command: 'EXEC_OPEN_PROJECTS', channel: 'Delivery' },
  appointments: { route: '/operations/appointments', command: 'EXEC_OPEN_APPOINTMENTS', channel: 'Operations' },
  clinical_admin: { route: '/healthcare/admin', command: 'EXEC_OPEN_CLINICAL_ADMIN', channel: 'Operations' },
  compliance: { route: '/compliance', command: 'EXEC_OPEN_COMPLIANCE', channel: 'Compliance' },
  production: { route: '/operations/production', command: 'EXEC_OPEN_PRODUCTION', channel: 'Operations' },
  maintenance: { route: '/operations/maintenance', command: 'EXEC_OPEN_MAINTENANCE', channel: 'Risk' },
  orders: { route: '/orders', command: 'EXEC_OPEN_ORDERS', channel: 'Operations' },
  marketing: { route: '/marketing', command: 'EXEC_OPEN_MARKETING', channel: 'Sales' },
  support: { route: '/support', command: 'EXEC_OPEN_SUPPORT', channel: 'Customer' },
  field_operations: { route: '/operations/field', command: 'EXEC_OPEN_FIELD_OPERATIONS', channel: 'Operations' },
  donor_management: { route: '/donors', command: 'EXEC_OPEN_DONORS', channel: 'Finance' },
  reports: { route: '/reports', command: 'EXEC_OPEN_REPORTS', channel: 'Executive' },
  documents: { route: '/documents', command: 'EXEC_OPEN_DOCUMENTS', channel: 'Administration' },
  subscriptions: { route: '/billing/subscriptions', command: 'EXEC_OPEN_SUBSCRIPTIONS', channel: 'Finance' },
  security: { route: '/security', command: 'EXEC_OPEN_SECURITY', channel: 'Risk' },
  product: { route: '/product', command: 'EXEC_OPEN_PRODUCT', channel: 'Delivery' }
});

const DUTY_LANE_FUNCTION_MAP = Object.freeze({
  Executive: 'executive_dashboard',
  Finance: 'billing',
  Sales: 'crm',
  Customer: 'crm',
  Operations: 'inventory',
  Logistics: 'logistics',
  Supply: 'procurement',
  Delivery: 'project_management',
  People: 'time_tracking',
  Compliance: 'compliance',
  Risk: 'security',
  Administration: 'documents',
  'Wilsy AI': 'wilsy_ai'
});

const LANE_WORK_STEPS = Object.freeze({
  Executive: ['Verify source heartbeat', 'Choose owner decision', 'Seal command receipt'],
  Finance: ['Review revenue/cash evidence', 'Identify margin or collection action', 'Assign financial follow-up'],
  Sales: ['Select highest-value customer move', 'Prepare next message or quote', 'Commit revenue follow-up'],
  Customer: ['Review urgent customer exceptions', 'Assign response owner', 'Record resolution target'],
  Operations: ['Find biggest operational blocker', 'Assign owner and evidence source', 'Commit unblock deadline'],
  Logistics: ['Review ETA and supplier exceptions', 'Choose shipment or clearance action', 'Record customer impact'],
  Supply: ['Check material or stock constraint', 'Approve replenishment path', 'Record supplier follow-up'],
  Delivery: ['Review milestone or project slippage', 'Assign unblock owner', 'Seal delivery checkpoint'],
  People: ['Confirm staffing and accountability', 'Assign missing owner coverage', 'Record day plan'],
  Compliance: ['Review deadline and evidence gaps', 'Assign compliance owner', 'Seal statutory checkpoint'],
  Risk: ['Review operational/security exception', 'Set mitigation owner', 'Record risk watch receipt'],
  Administration: ['Clear document and reminder backlog', 'Assign admin owner', 'Seal cleanup proof'],
  'Wilsy AI': ['Select automation use case', 'Check license and source gates', 'Record AI value receipt']
});

/**
 * @function stableExecutiveCommandStringify
 * @description Serializes command packets with stable key ordering for repeatable proof hashes.
 * @param {unknown} value - Candidate command payload.
 * @returns {string} Stable JSON string.
 * @collaboration Every executive work order must be replayable as business evidence.
 */
export const stableExecutiveCommandStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableExecutiveCommandStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableExecutiveCommandStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createExecutiveCommandProof
 * @description Creates a SHA3-512 command proof for work orders and function packets.
 * @param {Object} payload - Command payload.
 * @returns {string} Uppercase proof hash.
 * @collaboration Wilson requires executive commands to carry forensic proof, not only UI state.
 */
export const createExecutiveCommandProof = (payload = {}) => sha3_512(stableExecutiveCommandStringify(payload)).toUpperCase();

/**
 * @function normalizeExecutiveFunctionKey
 * @description Normalizes a business function label into a route-map key.
 * @param {string} value - Function key or label.
 * @returns {string} Normalized function key.
 * @collaboration Dynamic tenant functions need stable keys before they can become executable controls.
 */
export const normalizeExecutiveFunctionKey = (value = 'executive_dashboard') => (
  String(value || 'executive_dashboard')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
  || 'executive_dashboard'
);

/**
 * @function resolveFunctionCommandRoute
 * @description Resolves the command route for a tenant function.
 * @param {string} functionKey - Function key.
 * @returns {Object} Route descriptor.
 * @collaboration Lets the Executive Dashboard route work into the right Wilsy OS module without hardcoding JSX branches.
 */
export const resolveFunctionCommandRoute = (functionKey = 'executive_dashboard') => {
  const normalizedKey = normalizeExecutiveFunctionKey(functionKey);
  return EXECUTIVE_FUNCTION_ROUTES[normalizedKey] || {
    route: `/operations/${normalizedKey}`,
    command: `EXEC_OPEN_${normalizedKey.toUpperCase()}`,
    channel: 'Operations'
  };
};

/**
 * @function resolveDutyFunctionKey
 * @description Maps a daily duty lane to the best Wilsy OS module function.
 * @param {Object} duty - Daily duty row.
 * @returns {string} Function key.
 * @collaboration A daily task becomes useful only when it points to the module that can complete it.
 */
export const resolveDutyFunctionKey = (duty = {}) => (
  duty.functionKey
  || DUTY_LANE_FUNCTION_MAP[duty.lane]
  || 'executive_dashboard'
);

/**
 * @function isFunctionExecutable
 * @description Determines whether a function card can be executed in the current tenant context.
 * @param {Object} functionRow - Function entitlement row.
 * @returns {boolean} True when execution should be allowed.
 * @collaboration Recommended functions can be explored, denied functions become access requests rather than broken buttons.
 */
export const isFunctionExecutable = (functionRow = {}) => (
  ['ENABLED', 'RECOMMENDED'].includes(String(functionRow.status || '').toUpperCase())
);

/**
 * @function buildExecutiveWorkOrder
 * @description Converts a daily duty into an executable executive work order.
 * @param {Object} params - Work-order inputs.
 * @returns {Object} Work order with route, source gates, steps and proof.
 * @collaboration This is the daily productivity spine: every accepted duty becomes a trackable piece of business execution.
 */
export const buildExecutiveWorkOrder = ({
  duty = {},
  tenantId = 'UNRESOLVED_TENANT',
  tenantProfile = {},
  functionMatrix = [],
  sourceSnapshot = {},
  status = 'ACCEPTED'
} = {}) => {
  const functionKey = resolveDutyFunctionKey(duty);
  const route = resolveFunctionCommandRoute(functionKey);
  const functionRow = functionMatrix.find(item => normalizeExecutiveFunctionKey(item.key) === functionKey) || {};
  const sourceGates = Object.entries(sourceSnapshot || {}).map(([key, source]) => ({
    key,
    live: Boolean(source?.live),
    status: source?.status || 'SOURCE_UNKNOWN'
  }));
  const blocked = duty.status !== 'READY' || functionRow.status === 'NOT_GRANTED';
  const packet = {
    workOrderId: `EXEC-WORK-${tenantId}-${duty.key || functionKey}-${Date.now().toString(36).toUpperCase()}`,
    tenantId,
    tenantName: tenantProfile.name || 'Tenant Executive',
    industryKey: tenantProfile.industryKey || 'general_smb',
    industryLabel: tenantProfile.industryLabel || 'General Business',
    dutyKey: duty.key || functionKey,
    lane: duty.lane || route.channel,
    title: duty.title || route.command,
    reason: duty.reason || 'Executive command generated from operating workflow.',
    functionKey,
    functionStatus: functionRow.status || 'FUNCTION_CONTEXT_REQUIRED',
    route,
    status: blocked ? 'BLOCKED_REVIEW_REQUIRED' : status,
    blocked,
    blockedReason: duty.blockedReason || (functionRow.status === 'NOT_GRANTED' ? 'Tenant function permission is not granted.' : ''),
    evidenceRequired: duty.evidenceRequired || [],
    workflowSteps: LANE_WORK_STEPS[duty.lane] || LANE_WORK_STEPS.Executive,
    sourceGates,
    generatedAt: new Date().toISOString()
  };
  return {
    ...packet,
    proofHash: createExecutiveCommandProof(packet)
  };
};

/**
 * @function buildFunctionCommandPacket
 * @description Builds a command packet for opening or requesting a tenant function.
 * @param {Object} params - Function command inputs.
 * @returns {Object} Function command packet.
 * @collaboration Function cards become action surfaces: open enabled modules or create permission requests for missing ones.
 */
export const buildFunctionCommandPacket = ({
  functionRow = {},
  tenantId = 'UNRESOLVED_TENANT',
  tenantProfile = {},
  action = 'OPEN'
} = {}) => {
  const functionKey = normalizeExecutiveFunctionKey(functionRow.key || functionRow.label);
  const route = resolveFunctionCommandRoute(functionKey);
  const packet = {
    commandId: `EXEC-FUNCTION-${functionKey}-${Date.now().toString(36).toUpperCase()}`,
    tenantId,
    tenantName: tenantProfile.name || 'Tenant Executive',
    industryKey: tenantProfile.industryKey || 'general_smb',
    functionKey,
    functionLabel: functionRow.label || functionKey.replace(/_/g, ' ').toUpperCase(),
    functionStatus: functionRow.status || 'FUNCTION_CONTEXT_REQUIRED',
    sourceStatus: functionRow.sourceStatus || 'TENANT_FUNCTION_CONTEXT',
    action: isFunctionExecutable(functionRow) ? action : 'REQUEST_ACCESS',
    route,
    generatedAt: new Date().toISOString()
  };
  return {
    ...packet,
    proofHash: createExecutiveCommandProof(packet)
  };
};

/**
 * @function buildTenantBrandingConfig
 * @description Resolves tenant branding from active tenant metadata into safe CSS variables and display labels.
 * @param {Object} activeTenant - Active tenant context.
 * @param {Object} profile - Executive business profile.
 * @returns {Object} Branding config.
 * @collaboration Tenant A must feel like Tenant A, while Wilsy founder context can still carry the sovereign root brand.
 */
export const buildTenantBrandingConfig = (activeTenant = {}, profile = {}) => {
  const tenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};
  const branding = tenant.branding || tenant.brandingNexus || tenant.theme || {};
  const displayName = tenant.name || tenant.companyName || tenant.legalName || profile.name || 'Wilsy OS Tenant';
  const primaryColor = tenant.primaryColor || branding.primaryColor || branding.color || DEFAULT_BRAND_PRIMARY;
  const secondaryColor = tenant.secondaryColor || branding.secondaryColor || DEFAULT_BRAND_SECONDARY;
  const rawLogo = tenant.logo || branding.logo || branding.icon || null;
  const logo = rawLogo && !['DEFAULT_LOGO', 'DEFAULT', 'NONE'].includes(String(rawLogo).toUpperCase()) ? rawLogo : null;
  const initials = String(displayName)
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(word => word[0]?.toUpperCase())
    .join('')
    || 'WK';

  return {
    displayName,
    initials,
    logo,
    primaryColor,
    secondaryColor,
    surfaceColor: branding.surfaceColor || DEFAULT_BRAND_SURFACE,
    cssVars: {
      '--exec-brand-primary': primaryColor,
      '--exec-brand-secondary': secondaryColor,
      '--exec-brand-surface': branding.surfaceColor || DEFAULT_BRAND_SURFACE
    },
    sourceStatus: logo || tenant.primaryColor || branding.primaryColor ? 'TENANT_BRAND_SOURCE' : 'TENANT_BRAND_DEFAULTED'
  };
};

/**
 * @function buildExecutiveSourceRepairQueue
 * @description Converts source heartbeat rows into repair actions for the executive.
 * @param {Array<Object>} sourceRows - Source registry rows.
 * @param {Object} profile - Tenant profile.
 * @returns {Array<Object>} Repair actions.
 * @collaboration Source gaps should become clear work, not mysterious red badges.
 */
export const buildExecutiveSourceRepairQueue = (sourceRows = [], profile = {}) => (
  sourceRows
    .filter(source => !source.live)
    .map(source => {
      const key = normalizeExecutiveFunctionKey(source.key);
      const route = key === 'finance'
        ? resolveFunctionCommandRoute('billing')
        : key === 'fx'
          ? resolveFunctionCommandRoute('currency_fx')
          : key === 'profile'
            ? { route: '/settings/tenant-profile', command: 'EXEC_OPEN_TENANT_PROFILE', channel: 'Administration' }
            : resolveFunctionCommandRoute(key);
      const packet = {
        id: `source_repair_${key}`,
        sourceKey: key,
        title: `Repair ${String(source.key || 'source').replace(/_/g, ' ')} source`,
        reason: source.status || 'SOURCE_SILENT',
        tenantFit: profile.industryLabel || 'General Business',
        route,
        generatedAt: new Date().toISOString()
      };
      return {
        ...packet,
        proofHash: createExecutiveCommandProof(packet)
      };
    })
);

export default {
  EXECUTIVE_FUNCTION_ROUTES,
  stableExecutiveCommandStringify,
  createExecutiveCommandProof,
  normalizeExecutiveFunctionKey,
  resolveFunctionCommandRoute,
  resolveDutyFunctionKey,
  isFunctionExecutable,
  buildExecutiveWorkOrder,
  buildFunctionCommandPacket,
  buildTenantBrandingConfig,
  buildExecutiveSourceRepairQueue
};
