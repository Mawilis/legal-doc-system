/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN EXECUTIVE SUITE [V56.4.0-PRODUCTION-EPITOME]                                                                      ║
 * ║ [FINANCE-SOURCED KPIS | SHA3 EXECUTIVE MUTATIONS | TELEMETRY STREAM | SHARD PAGINATION | BOARDROOM PROOF]                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 56.4.0-PRODUCTION-EPITOME | PRODUCTION READY | BILLION-DOLLAR EXECUTIVE COMMAND ASSET                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/executive/ExecutiveDashboard.jsx                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated unified executive dashboard with cryptographic audit and pagination.                        ║
 * ║ • AI Engineering (Codex) – ARCHITECTED: Elevated suite into forensic command surface with financeService KPI sourcing, SHA3 command    ║
 * ║   envelopes, telemetry-backed mutations, source-state governance, and scalable shard pagination.                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { sha3_512 } from 'js-sha3';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Briefcase,
  Building2,
  CheckCircle,
  ClipboardCheck,
  Database,
  Download,
  Edit,
  FileText,
  Lock,
  PieChart,
  PlayCircle,
  Plus,
  RefreshCw,
  Route,
  Search,
  Send,
  Settings,
  ShieldCheck,
  Target,
  Trash2,
  Users,
  UserCog,
  X
} from 'lucide-react';
import { useTenants } from '../../contexts/tenantContext';
import useSovereignAccess from '../../hooks/useSovereignAccess';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import { exportCSV } from '../../utils/exportHelpers';
import { broadcastTelemetry } from '../../utils/telemetryHelper';
import * as financeService from '../../services/financeService';
import * as crmService from '../../services/crmService';
import * as hrService from '../../services/hrService';
import * as salesService from '../../services/salesService';
import * as customerSuccessService from '../../services/customerSuccessService';
import * as productService from '../../services/productService';
import * as marketingService from '../../services/marketingService';
import * as procurementService from '../../services/procurementService';
import * as itService from '../../services/itService';
import * as securityService from '../../services/securityService';
import {
  buildExecutiveAccessDecision,
  buildExecutiveOperatingSystem
} from '../../services/ExecutiveOperatingEngine';
import {
  buildExecutiveSourceRepairQueue,
  buildExecutiveWorkOrder,
  buildFunctionCommandPacket,
  buildTenantBrandingConfig,
  isFunctionExecutable
} from '../../services/ExecutiveCommandOrchestrator';
import {
  activateWilsyAILicense as requestWilsyAILicenseActivation,
  buildWilsyAiLicensePlan,
  recordWilsyAIUsage as requestWilsyAIUsageRecord,
  syncWilsyAIEntitlements
} from '../../services/WilsyAIService';
import {
  DEFAULT_OPERATING_CURRENCY,
  EXECUTIVE_CURRENCIES,
  convertCurrency as requestCurrencyConversion,
  formatOperatingMoney,
  normalizeCurrency,
  syncCurrencyWatchlist
} from '../../services/CurrencyIntelligenceService';
import {
  answerExecutiveNaturalLanguageQuery,
  buildExecutiveTransformationPlaybook
} from '../../services/ExecutiveTransformationEngine';
import WilsyAccountCommandCenter from '../account/WilsyAccountCommandCenter';
import BusinessArtifactStudio from '../artifacts/BusinessArtifactStudio';
import styles from './ExecutiveDashboard.module.css';


const WILSY_EXEC_THEME_STORAGE_KEYS = Object.freeze({
  theme: 'wilsy:account-command-center:theme',
  mode: 'wilsy:account-command-center:mode'
});

const WILSY_EXEC_THEME_SKINS = Object.freeze({
  wilsy_aurora: {
    accent: '#B66DFF',
    secondary: '#17BDF2',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    surface: '#060B18',
    panel: '#0B1024',
    rail: '#080C18',
    bg: '#020306',
    text: '#FFFAF0',
    muted: '#C5CCE5',
    border: 'rgba(182,109,255,0.34)'
  },
  sovereign_black: {
    accent: '#D4AF37',
    secondary: '#56D69B',
    authority: '#F6D76B',
    live: '#56D69B',
    risk: '#FF6673',
    surface: '#050505',
    panel: '#0B0B0B',
    rail: '#030303',
    bg: '#000000',
    text: '#FFFFFF',
    muted: '#A7A7A7',
    border: 'rgba(212,175,55,0.32)'
  },
  cobalt_glass: {
    accent: '#17BDF2',
    secondary: '#8DBBFF',
    authority: '#D4AF37',
    live: '#54F0D1',
    risk: '#FF7C98',
    surface: '#06142E',
    panel: '#0A1D3D',
    rail: '#07132B',
    bg: '#020817',
    text: '#F3F8FF',
    muted: '#AFC7F6',
    border: 'rgba(23,189,242,0.34)'
  },
  pearl_command: {
    accent: '#7C68FF',
    secondary: '#0F9F6E',
    authority: '#C49A18',
    live: '#0F9F6E',
    risk: '#D33F62',
    surface: '#FFFFFF',
    panel: '#EEF2FF',
    rail: '#FFFFFF',
    bg: '#F6F8FF',
    text: '#111827',
    muted: '#53617F',
    border: 'rgba(124,104,255,0.26)'
  },
  legacy_gold: {
    accent: '#D4AF37',
    secondary: '#8FE6B1',
    authority: '#F6D76B',
    live: '#8FE6B1',
    risk: '#FF8A8A',
    surface: '#0D0A03',
    panel: '#141006',
    rail: '#090702',
    bg: '#070602',
    text: '#FFF8DC',
    muted: '#B9A56D',
    border: 'rgba(246,215,107,0.32)'
  },
  forensic_violet: {
    accent: '#B66DFF',
    secondary: '#E7B7FF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF8AA4',
    surface: '#0D0718',
    panel: '#140B26',
    rail: '#090412',
    bg: '#05020A',
    text: '#FFF7FF',
    muted: '#CAB8EA',
    border: 'rgba(182,109,255,0.36)'
  },
  quantum: {
    accent: '#17F2D1',
    secondary: '#B6F6FF',
    authority: '#D4AF37',
    live: '#84F0C8',
    risk: '#FF789A',
    surface: '#06111A',
    panel: '#071C25',
    rail: '#031018',
    bg: '#01050A',
    text: '#F5FFFF',
    muted: '#9FD7E7',
    border: 'rgba(23,242,209,0.34)'
  }
});

/**
 * @function normalizeWilsyExecutiveThemeId
 * @description Normalizes saved Account Command Center theme ids for ExecutiveDashboard.
 * @param {string} themeId - Candidate theme id.
 * @returns {string} Supported operating skin id.
 * @collaboration Forces the Executive cockpit to obey the same operating skins as Account Command Center.
 */
const normalizeWilsyExecutiveThemeId = (themeId = '') => {
  const aliases = {
    forensic: 'forensic_violet',
    cobalt: 'cobalt_glass',
    wilsy_daybreak: 'pearl_command',
    dark_ops: 'sovereign_black'
  };
  const normalized = aliases[themeId] || themeId || 'wilsy_aurora';
  return WILSY_EXEC_THEME_SKINS[normalized] ? normalized : 'wilsy_aurora';
};

/**
 * @function normalizeWilsyExecutiveMode
 * @description Normalizes saved Account Command Center mode for ExecutiveDashboard.
 * @param {string} mode - Candidate mode.
 * @returns {string} Safe mode id.
 * @collaboration Keeps ExecutiveDashboard aligned with the Account mode receipt.
 */
const normalizeWilsyExecutiveMode = (mode = '') => (
  ['day', 'night', 'auto'].includes(mode) ? mode : 'night'
);

/**
 * @function resolveWilsyExecutiveMode
 * @description Resolves auto mode to day or night.
 * @param {string} mode - Candidate mode.
 * @returns {string} Resolved mode.
 * @collaboration Allows the cockpit to consume auto mode without waiting for backend preference services.
 */
const resolveWilsyExecutiveMode = (mode = 'night') => {
  const safeMode = normalizeWilsyExecutiveMode(mode);
  if (safeMode !== 'auto') return safeMode;
  const hour = new Date().getHours();
  return hour >= 7 && hour < 18 ? 'day' : 'night';
};

/**
 * @function readWilsyExecutiveThemePreference
 * @description Reads the persisted operating skin saved by Account Command Center.
 * @returns {{themeId:string,mode:string,resolvedMode:string,skin:Object}} Theme packet.
 * @collaboration Bridges saved Account receipts into ExecutiveDashboard even when controller-level theme propagation is bypassed.
 */
const readWilsyExecutiveThemePreference = () => {
  const themeId = normalizeWilsyExecutiveThemeId(
    typeof window === 'undefined'
      ? 'wilsy_aurora'
      : window.localStorage.getItem(WILSY_EXEC_THEME_STORAGE_KEYS.theme)
  );
  const mode = normalizeWilsyExecutiveMode(
    typeof window === 'undefined'
      ? 'night'
      : window.localStorage.getItem(WILSY_EXEC_THEME_STORAGE_KEYS.mode)
  );
  return {
    themeId,
    mode,
    resolvedMode: resolveWilsyExecutiveMode(mode),
    skin: WILSY_EXEC_THEME_SKINS[themeId] || WILSY_EXEC_THEME_SKINS.wilsy_aurora
  };
};

/**
 * @function buildWilsyExecutiveThemeVars
 * @description Builds CSS variable payload consumed directly by ExecutiveDashboard.
 * @param {string} themeId - Operating skin id.
 * @param {string} mode - Theme mode.
 * @returns {Object} CSS variable object.
 * @collaboration Makes ExecutiveDashboard repaint from saved theme receipts instead of local hardcoded gold defaults.
 */
const buildWilsyExecutiveThemeVars = (themeId = 'wilsy_aurora', mode = 'night') => {
  const safeThemeId = normalizeWilsyExecutiveThemeId(themeId);
  const resolvedMode = resolveWilsyExecutiveMode(mode);
  const skin = WILSY_EXEC_THEME_SKINS[safeThemeId] || WILSY_EXEC_THEME_SKINS.wilsy_aurora;

  return {
    '--wilsy-bg': skin.bg,
    '--wilsy-surface': skin.surface,
    '--wilsy-panel': skin.panel,
    '--wilsy-rail': skin.rail,
    '--wilsy-text': skin.text,
    '--wilsy-muted': skin.muted,
    '--wilsy-accent': skin.accent,
    '--wilsy-accent-2': skin.secondary,
    '--wilsy-accent-3': skin.live,
    '--wilsy-authority': skin.authority,
    '--wilsy-live': skin.live,
    '--wilsy-risk': skin.risk,
    '--wilsy-border': skin.border,
    '--exec-brand-primary': skin.accent,
    '--exec-brand-secondary': skin.secondary,
    '--exec-brand-surface': skin.bg,
    '--exec-view-bg': skin.bg,
    '--exec-view-muted': skin.muted,
    '--exec-view-border': skin.border,
    colorScheme: resolvedMode === 'day' ? 'light' : 'dark'
  };
};

/**
 * @function applyWilsyExecutiveThemeToDocument
 * @description Writes current Executive theme values to the document root.
 * @param {string} themeId - Operating skin id.
 * @param {string} mode - Theme mode.
 * @returns {void}
 * @collaboration Ensures the active dashboard and global chrome share one operating skin source of truth.
 */
const applyWilsyExecutiveThemeToDocument = (themeId = 'wilsy_aurora', mode = 'night') => {
  if (typeof document === 'undefined') return;

  const safeThemeId = normalizeWilsyExecutiveThemeId(themeId);
  const safeMode = normalizeWilsyExecutiveMode(mode);
  const resolvedMode = resolveWilsyExecutiveMode(safeMode);
  const vars = buildWilsyExecutiveThemeVars(safeThemeId, safeMode);

  document.documentElement.dataset.wilsyTheme = safeThemeId;
  document.documentElement.dataset.wilsyMode = safeMode;
  document.documentElement.dataset.wilsyResolvedMode = resolvedMode;
  document.body.dataset.wilsyTheme = safeThemeId;
  document.body.dataset.wilsyMode = safeMode;
  document.body.dataset.wilsyResolvedMode = resolvedMode;

  Object.entries(vars).forEach(([key, value]) => {
    if (key.startsWith('--')) {
      document.documentElement.style.setProperty(key, value);
      document.body.style.setProperty(key, value);
    }
  });
};

const EXECUTIVE_SUITE_VERSION = 'V56.4.0-PRODUCTION-EPITOME';
const DEFAULT_PAGE_LIMIT = 10;
const MAX_ACTIVITY_ROWS = 12;

const DEFAULT_FINANCIAL_KPIS = Object.freeze({
  revenue: 0,
  expenses: 0,
  profit: 0,
  profitMargin: 0,
  arr: 0,
  currency: 'ZAR',
  nps: null,
  employeeSatisfaction: null,
  targets: {},
  sourceStatus: 'SOURCE_SILENT',
  source: 'financeService'
});

const EXECUTIVE_OPERATING_SOURCE_PLAYBOOK = Object.freeze([
  { key: 'hr', label: 'HR / People', lane: 'People', functionKey: 'hr', loader: (tenantId) => hrService.getEmployees(tenantId, { limit: 5, offset: 0 }) },
  { key: 'crm', label: 'CRM / Customer Graph', lane: 'Sales', functionKey: 'crm', loader: (tenantId) => crmService.getCrmSummary(tenantId) },
  { key: 'sales', label: 'Sales Pipeline', lane: 'Revenue', functionKey: 'sales', loader: (tenantId) => salesService.getPipeline(tenantId, { limit: 5, offset: 0 }) },
  { key: 'customerSuccess', label: 'Customer Success', lane: 'Customer', functionKey: 'customer_success', loader: (tenantId) => customerSuccessService.getTickets(tenantId, { limit: 5, offset: 0 }) },
  { key: 'product', label: 'Product / Roadmap', lane: 'Delivery', functionKey: 'product', loader: (tenantId) => productService.getProductMetrics(tenantId, { limit: 5, offset: 0 }) },
  { key: 'marketing', label: 'Marketing Demand', lane: 'Growth', functionKey: 'marketing', loader: (tenantId) => marketingService.getAnalytics(tenantId, { limit: 5, offset: 0 }) },
  { key: 'procurement', label: 'Procurement / Supply', lane: 'Supply', functionKey: 'procurement', loader: (tenantId) => procurementService.getPurchaseOrders(tenantId, { limit: 5, offset: 0 }) },
  { key: 'security', label: 'Security / Risk', lane: 'Risk', functionKey: 'security', loader: (tenantId) => securityService.getIncidents(tenantId, { limit: 5, offset: 0 }) },
  { key: 'it', label: 'IT / Reliability', lane: 'Technology', functionKey: 'it', loader: (tenantId) => itService.getIncidents(tenantId, { limit: 5, offset: 0 }) }
]);


/**
 * @function titleCaseExecutiveText
 * @description Converts identifiers, emails and role tokens into readable executive labels.
 * @param {string} value - Candidate display text.
 * @returns {string} Human-readable label.
 * @collaboration Prevents raw tenant and role identifiers from becoming the executive story.
 */
const titleCaseExecutiveText = (value = '') => (
  String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, letter => letter.toUpperCase())
);

/**
 * @function deriveNameFromEmail
 * @description Derives a temporary operator name from email only when tenant/user names are absent.
 * @param {string} email - Operator email.
 * @returns {string} Human-readable fallback name.
 * @collaboration Keeps the UI from displaying raw email as the primary executive identity.
 */
const deriveNameFromEmail = (email = '') => {
  const localPart = String(email || '').split('@')[0] || '';
  if (!localPart) return 'Executive Operator';
  return titleCaseExecutiveText(localPart.replace(/[.]+/g, ' '));
};

/**
 * @function buildExecutiveOperatorIdentity
 * @description Builds the top-rail operator and tenant story for ExecutiveDashboard.
 * @param {Object} params - Identity inputs from user, tenant, access and operating system profile.
 * @returns {Object} Display-safe executive identity packet.
 * @collaboration Turns the top rail into a business OS identity layer instead of email/version metadata.
 */
const buildExecutiveOperatorIdentity = ({
  user = {},
  activeTenant = {},
  tenantBranding = {},
  executiveOperatingSystem = {},
  executiveReadiness = {},
  sourceSnapshot = {},
  role = 'EXECUTIVE',
  access = {}
} = {}) => {
  const email = user?.email || user?.username || '';
  const composedName = [user?.firstName, user?.lastName].filter(Boolean).join(' ').trim();

  const displayName = (
    user?.fullName ||
    user?.displayName ||
    user?.name ||
    composedName ||
    activeTenant?.ownerName ||
    activeTenant?.founderName ||
    deriveNameFromEmail(email)
  );

  const roleLabel = titleCaseExecutiveText(
    user?.title ||
    user?.position ||
    user?.roleLabel ||
    user?.tenantRole ||
    user?.role ||
    access?.role ||
    role ||
    'Executive Operator'
  );

  const tenantName = (
    tenantBranding?.displayName ||
    activeTenant?.name ||
    activeTenant?.companyName ||
    activeTenant?.tenantName ||
    'Wilsy OS Tenant'
  );

  const industryLabel = executiveOperatingSystem?.profile?.industryLabel || 'Adaptive business model';
  const readinessLabel = compactExecutiveSignal(executiveReadiness?.posture || 'COMMAND_READY');
  const financeLabel = compactExecutiveSignal(sourceSnapshot?.finance?.status || 'FINANCE_SOURCE_REQUIRED');
  const telemetryLabel = compactExecutiveSignal(sourceSnapshot?.telemetry?.status || 'STREAM_READY');
  const sourceCount = resolveExecutiveSourceCount(sourceSnapshot) || null;

  return {
    displayName,
    roleLabel,
    email,
    tenantName,
    commandLabel: 'Executive Command',
    tenantEyebrow: 'Tenant identity',
    tenantStory: 'Operating brand verified',
    storyMessages: [
      `Wilsy OS is running ${tenantName} as a branded business operating system`,
      `${displayName} is operating as ${roleLabel}`,
      `${industryLabel} command layer is active`,
      `Finance posture: ${financeLabel}`,
      `Activity posture: ${telemetryLabel}`,
      `Executive posture: ${readinessLabel}`,
      sourceCount ? `${sourceCount} business sources visible` : 'HR, CRM, Billing, Documents and Artifacts are available through Command K'
    ]
  };
};

/**
 * @function buildInitialOperatingSourceRows
 * @description Builds the default cross-functional source rows before live service hydration.
 * @returns {Array<Object>} Operating source rows.
 * @collaboration Gives CEO onboarding a complete HR, CRM, sales, customer, product and risk checklist before sources answer.
 */
const buildInitialOperatingSourceRows = () => EXECUTIVE_OPERATING_SOURCE_PLAYBOOK.map(source => ({
  ...source,
  live: false,
  status: `${source.key.toUpperCase()}_NOT_SYNCED`,
  count: null,
  lastSync: null,
  proofHash: null
}));

/**
 * @function buildInitialOperatingSourceSnapshot
 * @description Converts operating source rows into sourceSnapshot entries.
 * @returns {Object} Source snapshot keyed by source name.
 * @collaboration Lets the readiness engine reason about HR, CRM and operating systems before the first API reply.
 */
const buildInitialOperatingSourceSnapshot = () => buildInitialOperatingSourceRows().reduce((snapshot, source) => ({
  ...snapshot,
  [source.key]: {
    status: source.status,
    live: false,
    lastSync: null,
    functionKey: source.functionKey,
    lane: source.lane
  }
}), {});

const TAB_TO_MODAL_MAP = Object.freeze({
  kpis: 'kpi',
  boardReports: 'boardReport',
  investorUpdates: 'investorUpdate',
  strategicGoals: 'strategicGoal'
});

const TAB_TO_LABEL_MAP = Object.freeze({
  kpis: 'KPI',
  boardReports: 'BOARD_REPORT',
  investorUpdates: 'INVESTOR_UPDATE',
  strategicGoals: 'STRATEGIC_GOAL'
});

const MODAL_TO_TAB_MAP = Object.freeze({
  kpi: 'kpis',
  boardReport: 'boardReports',
  investorUpdate: 'investorUpdates',
  strategicGoal: 'strategicGoals'
});

const MUTATION_TYPE_MAP = Object.freeze({
  kpi: 'KPI',
  boardReport: 'BOARD_REPORT',
  investorUpdate: 'INVESTOR_UPDATE',
  strategicGoal: 'STRATEGIC_GOAL'
});

/**
 * @function stableExecutiveStringify
 * @description Serializes executive command packets with deterministic key order for repeatable SHA3 proof hashes.
 * @param {unknown} value - Value to serialize.
 * @returns {string} Canonical JSON string.
 * @collaboration Executive actions must survive reload, audit replay and boardroom proof export with the same hash answer.
 */
const stableExecutiveStringify = (value) => {
  if (typeof value === 'undefined') return 'null';
  if (value instanceof Date) return JSON.stringify(value.toISOString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => stableExecutiveStringify(item)).join(',')}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableExecutiveStringify(value[key])}`).join(',')}}`;
};

/**
 * @function createExecutiveProofHash
 * @description Creates a SHA3-512 digest for an executive command or KPI packet.
 * @param {Object} payload - Payload to seal.
 * @returns {string} Uppercase SHA3-512 digest.
 */
const createExecutiveProofHash = (payload = {}) => sha3_512(stableExecutiveStringify(payload)).toUpperCase();

/**
 * @function resolveExecutiveSourceCount
 * @description Extracts a truthful source volume from heterogeneous HR, CRM and operating service responses.
 * @param {unknown} payload - Service response payload.
 * @returns {number|null} Count when available, otherwise null.
 * @collaboration Cross-functional CEO readiness should be based on actual service responses without inventing row counts.
 */
const resolveExecutiveSourceCount = (payload = {}) => {
  if (Array.isArray(payload)) return payload.length;
  const source = payload?.data || payload?.summary || payload?.metrics || payload;
  if (Array.isArray(source)) return source.length;
  if (Array.isArray(source?.items)) return source.items.length;
  if (Array.isArray(source?.records)) return source.records.length;
  const numeric = [
    source?.total,
    source?.count,
    source?.open,
    source?.active,
    source?.itemsTotal,
    source?.pipelineValue ? 1 : null,
    source?.healthScore ? 1 : null
  ].find(value => value !== undefined && value !== null && value !== '');
  if (numeric === undefined || numeric === null) return null;
  const parsed = Number(numeric);
  return Number.isFinite(parsed) ? parsed : null;
};

/**
 * @function buildOperatingSourceRow
 * @description Normalizes a fulfilled or failed operating service check into the executive source row shape.
 * @param {Object} descriptor - Operating source descriptor.
 * @param {Object} params - Result inputs.
 * @returns {Object} Normalized operating source row.
 * @collaboration Makes HR, CRM and operating components first-class CEO onboarding evidence with proof hashes.
 */
const buildOperatingSourceRow = (descriptor = {}, { tenantId = 'MASTER', payload = null, error = null } = {}) => {
  const now = new Date().toISOString();
  const count = error ? null : resolveExecutiveSourceCount(payload);
  const live = !error;
  const status = error
    ? `${descriptor.key?.toUpperCase()}_SOURCE_SILENT`
    : count === 0
      ? `${descriptor.key?.toUpperCase()}_SOURCE_READY_EMPTY`
      : `${descriptor.key?.toUpperCase()}_SOURCE_LIVE`;
  const packet = {
    key: descriptor.key,
    label: descriptor.label,
    lane: descriptor.lane,
    functionKey: descriptor.functionKey,
    tenantId,
    status,
    live,
    count,
    syncedAt: now,
    error: error?.response?.data?.message || error?.message || null,
    suiteVersion: EXECUTIVE_SUITE_VERSION
  };
  return {
    ...descriptor,
    live,
    status,
    count,
    lastSync: now,
    error: packet.error,
    proofHash: createExecutiveProofHash(packet)
  };
};

/**
 * @function normalizeFinancialKPIs
 * @description Normalizes financeService KPI envelopes into the executive source-of-truth shape.
 * @param {Object} payload - Finance KPI payload.
 * @returns {Object} Normalized KPI fields.
 * @collaboration Keeps executive finance reads source-truthful before HR, CRM and operating sources are fused into readiness.
 */
const normalizeFinancialKPIs = (payload = {}) => {
  const sourcePayload = payload?.data?.kpis || payload?.data?.metrics || payload?.data || payload?.kpis || payload?.metrics || payload;
  /**
   * @function resolveOptionalNumber
   * @description Converts candidate KPI values into numbers while preserving null when no source provided a value.
   * @param {...unknown} values - Candidate numeric values from finance envelopes.
   * @returns {number|null} Parsed number or null.
   * @collaboration Protects Wilson's no-fake-data mandate by preventing missing finance sources from becoming synthetic zeroes.
   */
  const resolveOptionalNumber = (...values) => {
    const found = values.find(value => value !== undefined && value !== null && value !== '');
    if (found === undefined) return null;
    const numeric = Number(found);
    return Number.isFinite(numeric) ? numeric : null;
  };
  return {
    revenue: resolveOptionalNumber(sourcePayload.revenue, sourcePayload.revenueYtd, sourcePayload.totalRevenue, sourcePayload.arrRevenue),
    expenses: resolveOptionalNumber(sourcePayload.expenses, sourcePayload.totalExpenses),
    profit: resolveOptionalNumber(sourcePayload.profit, sourcePayload.netProfit),
    profitMargin: resolveOptionalNumber(sourcePayload.profitMargin, sourcePayload.margin),
    arr: resolveOptionalNumber(sourcePayload.arr, sourcePayload.annualRecurringRevenue, sourcePayload.arrRunRate),
    currency: normalizeCurrency(sourcePayload.currency || sourcePayload.reportingCurrency || sourcePayload.operatingCurrency || 'ZAR'),
    nps: resolveOptionalNumber(sourcePayload.nps, sourcePayload.customerNps),
    employeeSatisfaction: resolveOptionalNumber(sourcePayload.employeeSatisfaction, sourcePayload.employeeSat),
    targets: {
      revenue: resolveOptionalNumber(sourcePayload.revenueTarget, sourcePayload.targetRevenue, sourcePayload.targets?.revenue),
      arr: resolveOptionalNumber(sourcePayload.arrTarget, sourcePayload.targetArr, sourcePayload.targets?.arr),
      nps: resolveOptionalNumber(sourcePayload.npsTarget, sourcePayload.targetNps, sourcePayload.targets?.nps),
      employeeSatisfaction: resolveOptionalNumber(sourcePayload.employeeSatisfactionTarget, sourcePayload.targetEmployeeSatisfaction, sourcePayload.targets?.employeeSatisfaction)
    },
    sourceStatus: sourcePayload.sourceStatus || payload.sourceStatus || sourcePayload.status || payload.status || 'FINANCE_SERVICE_LIVE',
    source: 'financeService',
    syncedAt: sourcePayload.syncedAt || sourcePayload.updatedAt || payload.syncedAt || payload.updatedAt || new Date().toISOString()
  };
};

/**
 * @function buildExecutiveKpiRows
 * @description Builds boardroom KPI rows from normalized financeService metrics.
 * @param {Object} financial - Normalized finance KPI payload.
 * @returns {Array<Object>} KPI rows with proof hashes.
 * @collaboration Keeps KPI rows finance-sourced and proofed instead of hardcoded executive theatre.
 */
const buildExecutiveKpiRows = (financial = DEFAULT_FINANCIAL_KPIS) => {
  const arr = Number(financial.arr || (financial.revenue * 1.2) || 0);
  const currency = financial.currency || DEFAULT_OPERATING_CURRENCY;
  const rows = [
    { id: 'kpi_rev_ytd', name: 'Revenue (YTD)', value: financial.revenue, target: financial.targets?.revenue ?? null, unit: currency, sourceStatus: financial.sourceStatus },
    { id: 'kpi_arr_run', name: 'ARR Run Rate', value: arr, target: financial.targets?.arr ?? null, unit: currency, sourceStatus: financial.sourceStatus },
    { id: 'kpi_cust_nps', name: 'Customer NPS', value: financial.nps, target: financial.targets?.nps ?? null, unit: 'score', sourceStatus: financial.sourceStatus },
    { id: 'kpi_emp_sat', name: 'Employee Satisfaction', value: financial.employeeSatisfaction, target: financial.targets?.employeeSatisfaction ?? null, unit: '%', sourceStatus: financial.sourceStatus }
  ];

  return rows.map(row => {
    const packet = {
      ...row,
      tenantSource: financial.source,
      syncedAt: financial.syncedAt || new Date().toISOString(),
      suiteVersion: EXECUTIVE_SUITE_VERSION
    };
    return {
      ...packet,
      updatedAt: financial.syncedAt || new Date().toISOString(),
      proofHash: createExecutiveProofHash(packet)
    };
  });
};

/**
 * @function applyShardPagination
 * @description Filters and slices executive rows for shard-aware pagination.
 * @param {Array<Object>} rows - Candidate rows.
 * @param {Object} pageState - Pagination state.
 * @param {string} searchTerm - Current search term.
 * @returns {{items:Array,total:number,hasMore:boolean,offset:number,limit:number}}
 * @collaboration Lets executive record volumes scale without dumping every tenant artifact into one view.
 */
const applyShardPagination = (rows = [], pageState = {}, searchTerm = '') => {
  const limit = Number(pageState.limit || DEFAULT_PAGE_LIMIT);
  const offset = Number(pageState.offset || 0);
  const needle = String(searchTerm || '').trim().toLowerCase();
  const filtered = !needle
    ? rows
    : rows.filter(row => stableExecutiveStringify(row).toLowerCase().includes(needle));
  return {
    items: filtered.slice(offset, offset + limit),
    total: filtered.length,
    hasMore: offset + limit < filtered.length,
    offset,
    limit
  };
};

/**
 * @function mergeCommittedRows
 * @description Applies local telemetry-committed rows over source rows without inventing persistence.
 * @param {Array<Object>} baseRows - Source rows.
 * @param {Array<Object>} committedRows - Local committed command rows.
 * @returns {Array<Object>} Merged rows.
 * @collaboration Separates real source rows from local proof receipts so operators know what has persisted.
 */
const mergeCommittedRows = (baseRows = [], committedRows = []) => {
  const map = new Map(baseRows.map(row => [row.id, row]));
  committedRows.forEach(row => {
    if (row.__deleted) {
      map.delete(row.id);
      return;
    }
    map.set(row.id, { ...map.get(row.id), ...row });
  });
  return Array.from(map.values());
};

/**
 * @function buildExecutiveMutationEnvelope
 * @description Builds a sealed executive mutation envelope for telemetry and local activity receipts.
 * @param {Object} params - Mutation parameters.
 * @returns {Object} Command envelope.
 * @collaboration Every dashboard mutation becomes replayable executive evidence.
 */
const buildExecutiveMutationEnvelope = ({
  tenantId = 'MASTER',
  mutation = 'CREATE',
  recordType = 'EXECUTIVE_RECORD',
  payload = {},
  previous = null,
  pageState = {}
} = {}) => {
  const commandId = `EXEC-${recordType}-${mutation}-${Date.now().toString(36).toUpperCase()}`;
  const canonicalPayload = {
    commandId,
    tenantId,
    mutation,
    recordType,
    suiteVersion: EXECUTIVE_SUITE_VERSION,
    generatedAt: new Date().toISOString(),
    payload,
    previous,
    pageState
  };
  return {
    ...canonicalPayload,
    proof: {
      algorithm: 'SHA3-512',
      canonicalization: 'STABLE_JSON_KEY_SORT',
      hash: createExecutiveProofHash(canonicalPayload),
      canonicalPayload: stableExecutiveStringify(canonicalPayload)
    }
  };
};

/**
 * @function formatExecutiveMoney
 * @description Formats boardroom money values without fabricating currency movement.
 * @param {number|string} value - Candidate monetary amount.
 * @returns {string} Institutional monetary display.
 * @collaboration Keeps owner and investor reads clean while the source status remains explicit elsewhere.
 */
const formatExecutiveMoney = (value = 0, currency = DEFAULT_OPERATING_CURRENCY) => formatOperatingMoney(value, currency);

/**
 * @function formatExecutiveNumber
 * @description Formats scalar executive values for compact table and card display.
 * @param {number|string} value - Candidate numeric amount.
 * @returns {string} Localized number.
 * @collaboration Prevents raw JavaScript number rendering from leaking into the executive command surface.
 */
const formatExecutiveNumber = (value = 0) => Number(value || 0).toLocaleString();

/**
 * @function formatExecutiveKpiValue
 * @description Formats KPI values while preserving missing-source truth instead of converting null into zero.
 * @param {number|string|null} value - KPI value or null when the source did not provide it.
 * @param {string} unit - KPI unit.
 * @returns {string} Renderable KPI value.
 * @collaboration No executive should read a synthetic zero when Wilsy OS actually lacks the source.
 */
const formatExecutiveKpiValue = (value, unit = 'score') => {
  if (value === null || value === undefined || value === '') return 'SOURCE_REQUIRED';
  if (unit === '%') return `${formatExecutiveNumber(value)}%`;
  const rawUnit = String(unit || '').toUpperCase();
  const currencyUnit = rawUnit === 'ZA' || EXECUTIVE_CURRENCIES.includes(rawUnit);
  return currencyUnit ? formatExecutiveMoney(value, unit) : formatExecutiveNumber(value);
};

/**
 * @function formatExecutiveUsageValue
 * @description Formats Wilsy AI usage analytics while preserving source-silent nulls.
 * @param {number|string|null} value - Usage value.
 * @param {string} suffix - Optional suffix.
 * @returns {string} Usage display.
 * @collaboration AI analytics should not imply request activity when the usage ledger has not answered.
 */
const formatExecutiveUsageValue = (value, suffix = '') => {
  if (value === null || value === undefined || value === '') return 'SOURCE_REQUIRED';
  return `${formatExecutiveNumber(value)}${suffix}`;
};

/**
 * @function compactExecutiveSignal
 * @description Converts source-machine states into boardroom-readable business language.
 * @param {string} value - Source, telemetry, command or readiness state.
 * @returns {string} Executive-facing display label.
 * @collaboration Keeps backend truth available for Diagnostics while removing machine language from the CEO cockpit.
 */
const compactExecutiveSignal = (value = 'SOURCE_PENDING') => {
  const raw = String(value || 'SOURCE_PENDING').trim().toUpperCase();

  const aliases = {
    COMMAND_READY: 'Ready for decisions',
    READY: 'Ready',
    LIVE: 'Live',
    LIVE_SOURCE: 'Live sources',
    LIVE_SOURCE_READY: 'Live sources',
    LIVE_SOURCE_PARTIAL: 'Partially connected',
    STREAM_READY: 'Live activity stream',
    AWAITING_MUTATION: 'No executive action yet',
    MUTATION_READY: 'Ready to commit',
    EXEC_KPI_MUTATION: 'KPI update',
    STATE_MUTATION: 'Business update',

    SOURCE_REQUIRED: 'Source connection required',
    SOURCE_SILENT: 'Source awaiting connection',
    SOURCE_GATED: 'Access required',
    SOURCE_PENDING: 'Source pending',
    ZERO_RECORDS_FOUND_IN_SHARD: 'No records found',

    FINANCE_KPI_SOURCE_REQUIRED: 'Finance setup required',
    FINANCE_SOURCE_REQUIRED: 'Finance setup required',
    FINANCE_SERVICE_SOURCE_SILENT: 'Finance awaiting connection',
    FINANCE_SERVICE_LIVE: 'Finance connected',
    FINANCE_SOURCE_SYNC: 'Finance refresh',
    MARGIN_SOURCE_REQUIRED: 'Margin data required',

    FX_WATCHLIST_PARTIAL_LIVE: 'FX watchlist active',
    FX_NOT_SYNCED: 'FX setup required',

    TENANT_BRAND: 'Tenant',
    TENANT_BRAND_SOURCE: 'Brand source',
    TENANT_BRAND_DEFAULTED: 'Tenant branding incomplete',
    TENANT_PROFILE_INCOMPLETE: 'Tenant profile incomplete',
    PROFILE_NEEDED: 'Profile setup required',
    TENANT_COMMAND_LEDGER: 'Tenant ledger',

    WILSY_AI_ENTITLEMENT_SOURCE_SILENT: 'AI entitlement required',
    WILSY_AI_ENTITLEMENTS_READY: 'Wilsy AI ready',
    SERVER_ENTITLEMENT_CATALOG: 'License catalogue',
    QUOTA_AVAILABLE: 'Quota available',

    HR_SOURCE_SILENT: 'HR awaiting connection',
    CRM_SOURCE_SILENT: 'CRM awaiting connection',
    SALES_SOURCE_SILENT: 'Sales awaiting connection',
    PRODUCT_SOURCE_SILENT: 'Product awaiting connection',
    CUSTOMER_SUCCESS_SOURCE_SILENT: 'Customer success awaiting connection',

    TELEMETRY_DEGRADED_RETRYING_30S: 'Telemetry reconnecting',
    REQUEST_CONTEXT_FALLBACK: 'Using local context',
    COMPLIANCE_EVIDENCE: 'Review trust evidence ready',
    REVENUE_ARTIFACT_ROUTE: 'Board pack route',
    READINESS_OBJECTIVE: 'Readiness target',
    LICENSE_AUTOMATION: 'Configure Wilsy AI',
    QUICKBOOKS: 'QuickBooks',
    XERO: 'Xero'
  };

  if (aliases[raw]) return aliases[raw];

  return raw
    .replace(/^EXECUTIVE_/, '')
    .replace(/^EXEC_/, '')
    .replace(/^TENANT_/, '')
    .replace(/^WILSY_/, '')
    .replace(/^FINANCE_SERVICE_/, 'FINANCE_')
    .replace(/_SOURCE_/g, '_')
    .replace(/_SOURCE$/g, '')
    .replace(/_+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, letter => letter.toUpperCase()) || 'Setup required';
};

/**
 * @function todayIso
 * @description Produces today's browser-safe ISO date for command drafts.
 * @returns {string} Current YYYY-MM-DD date.
 * @collaboration Executive packets must use current operational time instead of stale hard-coded dates.
 */
const todayIso = () => new Date().toISOString().slice(0, 10);

/**
 * @function extractExecutiveSourceRows
 * @description Extracts tenant-provided executive rows from optional live or parent payloads without fallback fiction.
 * @param {...unknown} sources - Candidate arrays or envelopes from active tenant, metrics, analytics or services.
 * @returns {Array<Object>} Sanitized row array.
 * @collaboration Removes fake board packs, investor updates and goals while still allowing real tenant-owned data to render.
 */
const extractExecutiveSourceRows = (...sources) => {
  const rows = sources.find(source => Array.isArray(source))
    || sources.map(source => source?.items || source?.data || source?.records).find(Array.isArray)
    || [];
  return rows.filter(row => row && typeof row === 'object' && !row.__deleted);
};

/**
 * @function sealExecutiveSourceRows
 * @description Adds source labels and deterministic proof hashes to live tenant rows.
 * @param {Array<Object>} rows - Source rows.
 * @param {Object} params - Seal context.
 * @param {string} params.tabName - Active executive tab.
 * @param {string} params.tenantId - Tenant issuing the command.
 * @param {string} params.sourceStatus - Source status label.
 * @returns {Array<Object>} Sealed source rows.
 * @collaboration Lets real tenant records enter the dashboard with audit proof instead of synthetic demo IDs.
 */
const sealExecutiveSourceRows = (rows = [], { tabName = 'executive', tenantId = 'MASTER', sourceStatus = 'TENANT_SOURCE' } = {}) => (
  rows.map((row, index) => {
    const id = row.id || row._id || row.traceId || `${tabName}_${tenantId}_${index}`;
    const packet = {
      ...row,
      id,
      sourceStatus: row.sourceStatus || sourceStatus,
      tenantId,
      tabName,
      suiteVersion: EXECUTIVE_SUITE_VERSION
    };
    return {
      ...packet,
      proofHash: row.proofHash || createExecutiveProofHash(packet),
      updatedAt: row.updatedAt || row.date || row.syncedAt || new Date().toISOString()
    };
  })
);

/**
 * @function buildExecutiveModalDraft
 * @description Creates editable mutation drafts for each executive record type.
 * @param {string} type - Modal record type.
 * @param {Object|null} item - Existing item when editing.
 * @returns {Object} Modal draft state.
 * @collaboration Operators can create useful records without fake seed records polluting the ledger.
 */
const buildExecutiveModalDraft = (type = 'kpi', item = null) => {
  const base = item || {};
  if (type === 'boardReport') {
    return {
      title: base.title || `Board Pack ${todayIso()}`,
      date: base.date || todayIso(),
      author: base.author || 'CEO',
      status: base.status || 'draft'
    };
  }
  if (type === 'investorUpdate') {
    return {
      title: base.title || `Investor Brief ${todayIso()}`,
      date: base.date || todayIso(),
      audience: base.audience || 'Institutional',
      status: base.status || 'draft'
    };
  }
  if (type === 'strategicGoal') {
    return {
      title: base.title || 'Executive Strategic Objective',
      progress: Number(base.progress ?? 0),
      deadline: base.deadline || todayIso(),
      status: base.status || 'on_track'
    };
  }
  return {
    name: base.name || 'Executive KPI',
    value: Number(base.value ?? 0),
    target: Number(base.target ?? 1),
    unit: base.unit || 'ZAR'
  };
};

/**
 * @function getExecutiveStatusTone
 * @description Maps executive record statuses into stable visual tone classes.
 * @param {string} status - Record status.
 * @returns {string} CSS tone key.
 * @collaboration Keeps board packs, investor updates and strategic goals visually consistent.
 */
const getExecutiveStatusTone = (status = '') => {
  const normalized = String(status || '').toLowerCase();
  if (['published', 'sent', 'sealed', 'committed', 'on_track'].includes(normalized)) return 'ready';
  if (['at_risk', 'blocked', 'overdue'].includes(normalized)) return 'risk';
  return 'draft';
};

/**
 * Sovereign Executive Dashboard – Unified interface for executive leadership.
 * @returns {JSX.Element}
 */
const ExecutiveDashboard = ({
  role = 'EXECUTIVE',
  metrics = {},
  analytics = {},
  executeCommand = null,
  user = null,
  onSignOut = null,
  onFounderReturn = null,
  founderReturnEnabled = false
}) => {
  const { activeTenant } = useTenants();
  const access = useSovereignAccess();
  const tenantId = activeTenant?.tenantId || activeTenant?.id || access.tenantId || 'MASTER';
  const accessDecision = useMemo(() => (
    buildExecutiveAccessDecision(access, activeTenant)
  ), [access.userRole, activeTenant]);

  // UI state
  const [activeTab, setActiveTab] = useState('kpis');
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeWorkspace, setActiveWorkspace] = useState('overview');
  const [businessModelOverride, setBusinessModelOverride] = useState('');
  const [executiveQuestion, setExecutiveQuestion] = useState('');
  const [executiveAnswer, setExecutiveAnswer] = useState(null);
  const [isAccountCommandCenterOpen, setIsAccountCommandCenterOpen] = useState(false);
  const [accountThemeId, setAccountThemeId] = useState(() => readWilsyExecutiveThemePreference().themeId);
  const [accountThemeMode, setAccountThemeMode] = useState(() => readWilsyExecutiveThemePreference().mode);

  const executiveThemeVars = useMemo(() => (
    buildWilsyExecutiveThemeVars(accountThemeId, accountThemeMode)
  ), [accountThemeId, accountThemeMode]);

  // Pagination states
  const [pageStates, setPageStates] = useState({
    kpis: { offset: 0, limit: 10 },
    boardReports: { offset: 0, limit: 10 },
    investorUpdates: { offset: 0, limit: 10 },
    strategicGoals: { offset: 0, limit: 10 }
  });

  // Dynamic Data States
  const [kpis, setKpis] = useState({ items: [], total: 0, hasMore: false });
  const [boardReports, setBoardReports] = useState({ items: [], total: 0, hasMore: false });
  const [investorUpdates, setInvestorUpdates] = useState({ items: [], total: 0, hasMore: false });
  const [strategicGoals, setStrategicGoals] = useState({ items: [], total: 0, hasMore: false });
  const [financialKPIs, setFinancialKPIs] = useState(DEFAULT_FINANCIAL_KPIS);
  const [sourceSnapshot, setSourceSnapshot] = useState({
    finance: { status: 'SOURCE_SILENT', live: false, lastSync: null },
    fx: { status: 'FX_NOT_SYNCED', live: false, lastSync: null },
    telemetry: { status: 'SYNCING', live: false, lastSync: null },
    records: { status: 'TENANT_COMMAND_LEDGER', live: true, lastSync: null },
    ...buildInitialOperatingSourceSnapshot()
  });
  const [operatingSources, setOperatingSources] = useState(buildInitialOperatingSourceRows);
  const [mutationReceipts, setMutationReceipts] = useState([]);
  const [committedRows, setCommittedRows] = useState({
    kpis: [],
    boardReports: [],
    investorUpdates: [],
    strategicGoals: []
  });
  const [wilsyAIEntitlements, setWilsyAIEntitlements] = useState({
    status: 'WILSY_AI_ENTITLEMENTS_NOT_SYNCED',
    plans: [],
    licenses: [],
    proofHash: null,
    error: null
  });
  const [currencyWorkbench, setCurrencyWorkbench] = useState({
    amount: '100',
    fromCurrency: 'ZAR',
    toCurrency: 'USD',
    watchlist: [],
    sourceStatus: 'FX_NOT_SYNCED',
    conversion: null,
    proofHash: null
  });
  const [executiveWorkOrders, setExecutiveWorkOrders] = useState([]);
  const [selectedWorkOrderId, setSelectedWorkOrderId] = useState('');

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('kpi');
  const [modalDraft, setModalDraft] = useState(buildExecutiveModalDraft('kpi'));

  // Telemetry feed for executive events
  const {
    events: telemetryEvents,
    isSyncing: telemetrySyncing,
    error: telemetryError,
    lastStrike: telemetryLastStrike
  } = useTelemetryFeed(tenantId);
  const executiveActivities = useMemo(() => {
    const liveEvents = telemetryEvents
      .filter(ev => `${ev.eventType || ''} ${ev.event || ''}`.toUpperCase().includes('EXEC_'))
      .map(ev => ({
        id: ev.id || ev.traceId || ev.timestamp,
        timestamp: ev.timestamp || ev.metadata?.clientTimestamp,
        eventType: ev.eventType || ev.category,
        event: ev.event || ev.status || 'STREAM_EVENT',
        message: ev.message || ev.metadata?.message || ev.source || 'TRANSACTION_LOG_COMMITTED',
        proofHash: ev.metadata?.proofHash || ev.metadata?.commandProofHash || ev.metadata?.traceId
      }));
    return [...mutationReceipts, ...liveEvents]
      .sort((left, right) => new Date(right.timestamp || 0) - new Date(left.timestamp || 0))
      .slice(0, MAX_ACTIVITY_ROWS);
  }, [mutationReceipts, telemetryEvents]);

  const executiveOperatingSystem = useMemo(() => (
    buildExecutiveOperatingSystem({
      activeTenant,
      metrics,
      analytics,
      financialKPIs,
      sourceSnapshot,
      businessModelOverride
    })
  ), [activeTenant, analytics, businessModelOverride, financialKPIs, metrics, sourceSnapshot]);
  const tenantBranding = useMemo(() => (
    buildTenantBrandingConfig(activeTenant, executiveOperatingSystem.profile)
  ), [activeTenant, executiveOperatingSystem.profile]);

  const wilsyAiPlan = useMemo(() => (
    wilsyAIEntitlements.plans.length
      ? wilsyAIEntitlements.plans
      : buildWilsyAiLicensePlan({
      tenantProfile: executiveOperatingSystem.profile,
      dailyDuties: executiveOperatingSystem.dailyDuties,
      sourceSnapshot,
      accessDecision
    })
  ), [accessDecision, executiveOperatingSystem, sourceSnapshot, wilsyAIEntitlements.plans]);

  useEffect(() => {
    if (typeof document === 'undefined') return undefined;
    document.documentElement.dataset.wilsyTheme = accountThemeId;
    document.documentElement.dataset.wilsyMode = accountThemeMode;
    return undefined;
  }, [accountThemeId, accountThemeMode]);

  /**
   * @function fetchFinancialKPIs
   * @description Hydrates executive KPIs from financeService and marks the finance source truthfully when unavailable.
   * @returns {Promise<Object>} Normalized financial KPI packet.
   * @collaboration Protects Wilson's no-fake-data mandate by using parent metrics only as a declared fallback context.
   */
  const fetchFinancialKPIs = useCallback(async () => {
    try {
      const data = await financeService.getFinancialKPIs(tenantId);
      const normalized = normalizeFinancialKPIs(data || {});
      setFinancialKPIs(normalized);
      setSourceSnapshot(prev => ({
        ...prev,
        finance: {
          status: normalized.sourceStatus || 'FINANCE_SERVICE_LIVE',
          live: true,
          lastSync: new Date().toISOString(),
          proofHash: createExecutiveProofHash({ tenantId, normalized, source: 'financeService' })
        }
      }));
      return normalized;
    } catch (error) {
      const propFallback = normalizeFinancialKPIs(metrics?.financialKPIs || metrics || analytics?.financialKPIs || analytics || {});
      const fallback = {
        ...DEFAULT_FINANCIAL_KPIS,
        ...propFallback,
        sourceStatus: 'FINANCE_SERVICE_SOURCE_SILENT',
        source: 'parentMetricsFallback',
        syncedAt: new Date().toISOString()
      };
      setFinancialKPIs(fallback);
      setSourceSnapshot(prev => ({
        ...prev,
        finance: {
          status: 'SOURCE_SILENT',
          live: false,
          lastSync: new Date().toISOString(),
          error: error.response?.data?.message || error.message
        }
      }));
      await broadcastTelemetry(tenantId, 'EXEC_FINANCE_KPI_SOURCE', 'SOURCE_SILENT', 'ExecutiveDashboard', {
        error: error.response?.data?.message || error.message
      }).catch(() => {});
      return fallback;
    }
  }, [analytics, metrics, tenantId]);

  /**
   * @function fetchCurrencyWorkbench
   * @description Hydrates the executive FX watchlist from the protected finance route.
   * @returns {Promise<Object>} FX watchlist packet.
   * @collaboration South African executives need ZAR as the operating base while still seeing cross-border exposure truthfully.
   */
  const fetchCurrencyWorkbench = useCallback(async () => {
    const watchlist = await syncCurrencyWatchlist({
      tenantId,
      baseCurrency: DEFAULT_OPERATING_CURRENCY,
      targets: ['USD', 'EUR', 'GBP', 'TZS', 'KES']
    });
    setCurrencyWorkbench(prev => ({
      ...prev,
      watchlist: watchlist.rates || [],
      sourceStatus: watchlist.sourceStatus || 'FX_WATCHLIST_SOURCE_SILENT',
      proofHash: watchlist.proofHash || prev.proofHash
    }));
    setSourceSnapshot(prev => ({
      ...prev,
      fx: {
        status: watchlist.sourceStatus || 'FX_WATCHLIST_SOURCE_SILENT',
        live: Boolean(watchlist.success),
        lastSync: new Date().toISOString(),
        proofHash: watchlist.proofHash || null
      }
    }));
    return watchlist;
  }, [tenantId]);

  /**
   * @function fetchOperatingSources
   * @description Hydrates HR, CRM and operating source readiness from their real Wilsy OS service clients.
   * @returns {Promise<Array<Object>>} Operating source rows.
   * @collaboration CEO onboarding must know whether people, customer, product, supply and risk systems are actually connected.
   */
  const fetchOperatingSources = useCallback(async () => {
    const settled = await Promise.allSettled(
      EXECUTIVE_OPERATING_SOURCE_PLAYBOOK.map(async descriptor => (
        buildOperatingSourceRow(descriptor, {
          tenantId,
          payload: await descriptor.loader(tenantId)
        })
      ))
    );
    const rows = settled.map((result, index) => (
      result.status === 'fulfilled'
        ? result.value
        : buildOperatingSourceRow(EXECUTIVE_OPERATING_SOURCE_PLAYBOOK[index], {
          tenantId,
          error: result.reason
        })
    ));
    setOperatingSources(rows);
    setSourceSnapshot(prev => ({
      ...prev,
      ...rows.reduce((snapshot, row) => ({
        ...snapshot,
        [row.key]: {
          status: row.status,
          live: row.live,
          lastSync: row.lastSync,
          count: row.count,
          functionKey: row.functionKey,
          lane: row.lane,
          proofHash: row.proofHash,
          error: row.error || null
        }
      }), {})
    }));
    await broadcastTelemetry(tenantId, 'EXEC_OPERATING_SOURCE_SYNC', 'COMMITTED', 'ExecutiveDashboard', {
      liveSources: rows.filter(row => row.live).length,
      totalSources: rows.length,
      proofHash: createExecutiveProofHash({ tenantId, rows, suiteVersion: EXECUTIVE_SUITE_VERSION })
    }).catch(() => {});
    return rows;
  }, [tenantId]);

  /**
   * @function fetchTabData
   * @description Hydrates a paginated executive tab from live tenant rows plus telemetry-committed local rows.
   * @param {string} tabName - Executive tab key.
   * @param {Object} targetPage - Pagination window.
   * @param {Object} financialOverride - Optional KPI packet for fresh finance reads.
   * @returns {Promise<void>} Resolves after tab state is updated.
   * @collaboration Removes placeholder board/investor/goal records while preserving real tenant-owned records.
   */
  const fetchTabData = useCallback(async (tabName, targetPage, financialOverride = financialKPIs) => {
    switch (tabName) {
      case 'kpis':
        setKpis(applyShardPagination(
          mergeCommittedRows(buildExecutiveKpiRows(financialOverride), committedRows.kpis),
          targetPage,
          searchTerm
        ));
        break;
      case 'boardReports':
        setBoardReports(applyShardPagination(
          mergeCommittedRows(sealExecutiveSourceRows(extractExecutiveSourceRows(
            activeTenant?.executive?.boardReports,
            activeTenant?.boardReports,
            metrics?.executive?.boardReports,
            metrics?.boardReports,
            analytics?.executive?.boardReports,
            analytics?.boardReports
          ), { tabName, tenantId, sourceStatus: 'TENANT_BOARD_SOURCE' }), committedRows.boardReports),
          targetPage,
          searchTerm
        ));
        break;
      case 'investorUpdates':
        setInvestorUpdates(applyShardPagination(
          mergeCommittedRows(sealExecutiveSourceRows(extractExecutiveSourceRows(
            activeTenant?.executive?.investorUpdates,
            activeTenant?.investorUpdates,
            metrics?.executive?.investorUpdates,
            metrics?.investorUpdates,
            analytics?.executive?.investorUpdates,
            analytics?.investorUpdates
          ), { tabName, tenantId, sourceStatus: 'TENANT_INVESTOR_SOURCE' }), committedRows.investorUpdates),
          targetPage,
          searchTerm
        ));
        break;
      case 'strategicGoals':
        setStrategicGoals(applyShardPagination(
          mergeCommittedRows(sealExecutiveSourceRows(extractExecutiveSourceRows(
            activeTenant?.executive?.strategicGoals,
            activeTenant?.strategicGoals,
            metrics?.executive?.strategicGoals,
            metrics?.strategicGoals,
            analytics?.executive?.strategicGoals,
            analytics?.strategicGoals
          ), { tabName, tenantId, sourceStatus: 'TENANT_STRATEGY_SOURCE' }), committedRows.strategicGoals),
          targetPage,
          searchTerm
        ));
        break;
      default:
        break;
    }
    setSourceSnapshot(prev => ({
      ...prev,
      records: {
        status: 'TENANT_COMMAND_LEDGER',
        live: true,
        lastSync: new Date().toISOString(),
        activeTab: tabName,
        proofHash: createExecutiveProofHash({
          tenantId,
          tabName,
          targetPage,
          suiteVersion: EXECUTIVE_SUITE_VERSION
        })
      }
    }));
  }, [activeTenant, analytics, committedRows, financialKPIs, metrics, searchTerm, tenantId]);

  /**
   * @function loadAllData
   * @description Rehydrates finance and every executive record shard for the active tenant.
   * @returns {Promise<void>} Resolves after all dashboard tabs are refreshed.
   * @collaboration Keeps the executive suite synchronized without cross-tenant leakage.
   */
  const loadAllData = useCallback(async () => {
    setIsRefreshing(true);
    const nextFinancialKPIs = await fetchFinancialKPIs();
    await Promise.all([
      fetchTabData('kpis', pageStates.kpis, nextFinancialKPIs),
      fetchTabData('boardReports', pageStates.boardReports, nextFinancialKPIs),
      fetchTabData('investorUpdates', pageStates.investorUpdates, nextFinancialKPIs),
      fetchTabData('strategicGoals', pageStates.strategicGoals, nextFinancialKPIs),
      fetchCurrencyWorkbench(),
      fetchOperatingSources()
    ]);
    setIsRefreshing(false);
  }, [pageStates, fetchTabData, fetchFinancialKPIs, fetchCurrencyWorkbench, fetchOperatingSources]);

  useEffect(() => {
    if (access.isLoading) return undefined;
    if (!accessDecision.allowed) {
      setLoading(false);
      return undefined;
    }

    /**
     * @function init
     * @description Performs first-load hydration for the allowed executive tenant context.
     * @returns {Promise<void>} Resolves when the dashboard has loaded source state.
     * @collaboration Initial hydration is access-gated so unauthorized users never trigger executive source reads.
     */
    const init = async () => {
      setLoading(true);
      await loadAllData();
      setLoading(false);
    };
    init();
    return undefined;
  }, [access.isLoading, accessDecision.allowed, tenantId]);

  useEffect(() => {
    if (access.isLoading || accessDecision.allowed) return;
    broadcastTelemetry(tenantId, 'EXEC_ACCESS_DENIED', 'DENIED', 'ExecutiveDashboard', {
      userRole: access.userRole || 'unknown',
      userEmail: access.userEmail || 'unknown',
      activeTenantId: tenantId,
      reason: accessDecision.reason,
      required: accessDecision.required,
      channel: accessDecision.channel,
      proofHash: createExecutiveProofHash({
        tenantId,
        role: access.userRole || 'unknown',
        reason: accessDecision.reason,
        suiteVersion: EXECUTIVE_SUITE_VERSION
      })
    }).catch(() => {});
  }, [
    access.isLoading,
    access.userEmail,
    access.userRole,
    accessDecision.allowed,
    accessDecision.channel,
    accessDecision.reason,
    accessDecision.required,
    tenantId
  ]);

  useEffect(() => {
    setSourceSnapshot(prev => ({
      ...prev,
      telemetry: {
        status: telemetryError || (telemetrySyncing ? 'SYNCING' : 'LIVE'),
        live: !telemetryError,
        lastSync: telemetryLastStrike || prev.telemetry.lastSync
      }
    }));
  }, [telemetryError, telemetryLastStrike, telemetrySyncing]);

  useEffect(() => {
    if (access.isLoading || !accessDecision.allowed) return undefined;
    let alive = true;
    syncWilsyAIEntitlements({
      tenantId,
      tenantProfile: executiveOperatingSystem.profile,
      sourceSnapshot
    }).then(result => {
      if (!alive) return;
      setWilsyAIEntitlements({
        status: result.status,
        plans: result.plans || [],
        licenses: result.licenses || [],
        proofHash: result.proofHash || null,
        error: result.error || null
      });
    });
    return () => {
      alive = false;
    };
  }, [
    access.isLoading,
    accessDecision.allowed,
    executiveOperatingSystem.profile.industryKey,
    executiveOperatingSystem.profile.sourceStatus,
    sourceSnapshot.finance?.status,
    sourceSnapshot.fx?.status,
    sourceSnapshot.records?.status,
    sourceSnapshot.telemetry?.status,
    tenantId
  ]);

  useEffect(() => {
    if (showModal) {
      setModalDraft(buildExecutiveModalDraft(modalType, editingItem));
    }
  }, [editingItem, modalType, showModal]);

  useEffect(() => {
    fetchTabData(activeTab, { ...pageStates[activeTab], offset: 0 });
    setPageStates(prev => ({ ...prev, [activeTab]: { ...prev[activeTab], offset: 0 } }));
  }, [searchTerm]);

  /**
   * @function updatePageOffset
   * @description Moves a tab through shard-aware pagination and broadcasts the page mutation.
   * @param {string} tab - Executive tab key.
   * @param {boolean} increment - True for next page, false for previous page.
   * @returns {Promise<void>} Resolves after the new page is loaded.
   * @collaboration Pagination itself is treated as executive evidence because access to records is operational behavior.
   */
  const updatePageOffset = async (tab, increment) => {
    const targetPage = pageStates[tab];
    const newOffset = increment ? targetPage.offset + targetPage.limit : Math.max(0, targetPage.offset - targetPage.limit);
    const updatedPage = { ...targetPage, offset: newOffset };
    setPageStates(prev => ({ ...prev, [tab]: updatedPage }));
    setIsRefreshing(true);
    await broadcastTelemetry(tenantId, 'EXEC_PAGE_Business Update', increment ? 'NEXT_PAGE' : 'PREVIOUS_PAGE', 'ExecutiveDashboard', {
      tab,
      offset: updatedPage.offset,
      limit: updatedPage.limit,
      proofHash: createExecutiveProofHash({ tenantId, tab, updatedPage, suiteVersion: EXECUTIVE_SUITE_VERSION })
    }).catch(() => {});
    await fetchTabData(tab, updatedPage);
    setIsRefreshing(false);
  };

  /**
   * @function appendMutationReceipt
   * @description Adds a bounded local receipt for telemetry-backed executive mutations.
   * @param {Object} envelope - Executive command envelope.
   * @param {string} status - Receipt status.
   * @returns {void}
   * @collaboration Gives the executive immediate forensic feedback even before external telemetry streams return.
   */
  const appendMutationReceipt = useCallback((envelope, status = 'COMMITTED') => {
    setMutationReceipts(prev => [{
      id: envelope.commandId,
      timestamp: envelope.generatedAt,
      eventType: `EXEC_${envelope.recordType}_${envelope.mutation}`,
      event: status,
      message: `${envelope.recordType} ${envelope.mutation} ${status}`,
      proofHash: envelope.proof.hash,
      envelope
    }, ...prev].slice(0, MAX_ACTIVITY_ROWS));
  }, []);

  /**
   * @function buildCommittedRow
   * @description Converts a mutation envelope into the normalized row shape for the selected executive tab.
   * @param {string} tab - Executive tab key.
   * @param {Object} envelope - Mutation envelope.
   * @returns {Object} Committed row.
   * @collaboration Keeps local user-created records explicit as telemetry committed, never as backend-persisted fiction.
   */
  const buildCommittedRow = useCallback((tab, envelope) => {
    const now = envelope.generatedAt;
    const payload = envelope.payload || {};
    const base = {
      ...(envelope.previous || {}),
      ...payload,
      id: payload.id || envelope.previous?.id || `${tab}_${Date.now().toString(36)}`,
      sourceStatus: 'TELEMETRY_COMMITTED',
      proofHash: envelope.proof.hash,
      updatedAt: now,
      mutationStatus: envelope.mutation
    };

    if (tab === 'kpis') {
      return {
        ...base,
        name: base.name || 'Executive KPI Mutation',
        value: Number(base.value ?? 0),
        target: Number(base.target ?? 1),
        unit: base.unit || 'ZAR'
      };
    }
    if (tab === 'boardReports') {
      return {
        ...base,
        title: base.title || 'Sealed Executive Board Report',
        date: base.date || now.slice(0, 10),
        author: base.author || 'CEO',
        status: base.status || 'committed'
      };
    }
    if (tab === 'investorUpdates') {
      return {
        ...base,
        title: base.title || 'Sealed Investor Update',
        date: base.date || now.slice(0, 10),
        audience: base.audience || 'Institutional',
        status: base.status || 'committed'
      };
    }
    return {
      ...base,
      title: base.title || 'Sealed Strategic Goal',
      progress: Number(base.progress ?? 0),
      deadline: base.deadline || now.slice(0, 10),
      status: base.status || 'on_track'
    };
  }, []);

  /**
   * @function mutateVisibleRows
   * @description Applies a local row mutation to the currently visible table without changing unrelated tabs.
   * @param {string} tab - Executive tab key.
   * @param {Object} row - Row or tombstone.
   * @param {string} mutation - Mutation type.
   * @returns {void}
   * @collaboration Makes executive actions feel immediate while still recording the proof envelope.
   */
  const mutateVisibleRows = useCallback((tab, row, mutation) => {
    /**
     * @function reducer
     * @description Applies a create/update/delete row mutation to one paginated table state.
     * @param {Object} prev - Previous paginated table state.
     * @returns {Object} Next paginated table state.
     * @collaboration Keeps local command receipts visible immediately without pretending they came from a backend source.
     */
    const reducer = (prev) => {
      const exists = prev.items.some(item => item.id === row.id);
      const items = mutation === 'DELETE'
        ? prev.items.filter(item => item.id !== row.id)
        : [row, ...prev.items.filter(item => item.id !== row.id)].slice(0, prev.limit || DEFAULT_PAGE_LIMIT);
      return {
        ...prev,
        items,
        total: mutation === 'DELETE'
          ? Math.max(0, prev.total - (exists ? 1 : 0))
          : prev.total + (exists ? 0 : 1),
        hasMore: prev.hasMore
      };
    };
    const setters = {
      kpis: setKpis,
      boardReports: setBoardReports,
      investorUpdates: setInvestorUpdates,
      strategicGoals: setStrategicGoals
    };
    setters[tab]?.(reducer);
  }, []);

  /**
   * @function commitExecutiveRecord
   * @description Seals, broadcasts and applies a create/update/delete executive record mutation.
   * @param {Object} params - Commit parameters.
   * @returns {Promise<{envelope:Object,committedRow:Object}>} Commit receipt.
   * @collaboration This is the suite's mutation spine: every executive action becomes a proofed command packet.
   */
  const commitExecutiveRecord = useCallback(async ({
    tab,
    type,
    payload,
    previous = null,
    mutation = 'CREATE',
    receiptStatus = 'COMMITTED'
  }) => {
    const recordType = MUTATION_TYPE_MAP[type] || 'EXECUTIVE_RECORD';
    const envelope = buildExecutiveMutationEnvelope({
      tenantId,
      mutation,
      recordType,
      payload,
      previous,
      pageState: pageStates[tab]
    });
    const committedRow = buildCommittedRow(tab, envelope);
    await broadcastTelemetry(tenantId, `EXEC_${recordType}_MUTATION`, receiptStatus, 'ExecutiveDashboard', {
      commandId: envelope.commandId,
      mutation,
      recordType,
      proofHash: envelope.proof.hash,
      envelope
    });
    setCommittedRows(prev => ({
      ...prev,
      [tab]: mutation === 'DELETE'
        ? [{ id: payload.id, __deleted: true, proofHash: envelope.proof.hash }, ...prev[tab].filter(row => row.id !== payload.id)]
        : [committedRow, ...prev[tab].filter(row => row.id !== committedRow.id)]
    }));
    mutateVisibleRows(tab, mutation === 'DELETE' ? { id: payload.id, __deleted: true, proofHash: envelope.proof.hash } : committedRow, mutation);
    appendMutationReceipt(envelope, receiptStatus);
    return { envelope, committedRow };
  }, [appendMutationReceipt, buildCommittedRow, mutateVisibleRows, pageStates, tenantId]);

  /**
   * @function handleSave
   * @description Handles modal create/update submission for executive records.
   * @param {Object} formData - Modal form data.
   * @returns {Promise<void>} Resolves after the mutation is committed or audited as failed.
   * @collaboration Lets executives create real board, investor, KPI and goal records on demand.
   */
  const handleSave = async (formData) => {
    try {
      setIsRefreshing(true);
      const tab = MODAL_TO_TAB_MAP[modalType] || activeTab;
      const mutation = editingItem ? 'UPDATE' : 'CREATE';
      await commitExecutiveRecord({
        tab,
        type: modalType,
        mutation,
        payload: { ...(editingItem || {}), ...formData },
        previous: editingItem
      });
      setShowModal(false);
      setEditingItem(null);
    } catch (error) {
      console.error('[EXEC-MUTATION-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_MUTATION_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        modalType,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function handleDelete
   * @description Commits a tombstone mutation for an executive record after operator confirmation.
   * @param {string} id - Record id.
   * @param {string} type - Modal record type.
   * @returns {Promise<void>} Resolves after deletion is broadcast.
   * @collaboration Deletion is never silent; it becomes a traceable executive erasure command.
   */
  const handleDelete = async (id, type) => {
    if (!window.confirm('Confirm ledger record erasure? This mutation will permanently commit to system logs.')) return;
    try {
      setIsRefreshing(true);
      const tab = MODAL_TO_TAB_MAP[type] || activeTab;
      const currentRows = { kpis, boardReports, investorUpdates, strategicGoals }[tab]?.items || [];
      const previous = currentRows.find(item => item.id === id) || null;
      await commitExecutiveRecord({
        tab,
        type,
        mutation: 'DELETE',
        payload: { id },
        previous,
        receiptStatus: 'DELETED'
      });
    } catch (error) {
      console.error('[EXEC-ERASURE-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_MUTATION_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        type,
        targetId: id,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function handleExport
   * @description Exports the active executive shard and records the export command.
   * @returns {Promise<void>} Resolves after CSV export starts.
   * @collaboration Boardroom artifacts should be portable, permissioned and provable.
   */
  const handleExport = async () => {
    try {
      setIsRefreshing(true);
      let dataset = [];
      if (activeTab === 'kpis') dataset = kpis.items;
      else if (activeTab === 'boardReports') dataset = boardReports.items;
      else if (activeTab === 'investorUpdates') dataset = investorUpdates.items;
      else if (activeTab === 'strategicGoals') dataset = strategicGoals.items;
      const exportProof = createExecutiveProofHash({
        tenantId,
        activeTab,
        count: dataset.length,
        pageState: pageStates[activeTab],
        suiteVersion: EXECUTIVE_SUITE_VERSION
      });
      await broadcastTelemetry(tenantId, 'EXEC_EXPORT_COMMAND', 'COMMITTED', 'ExecutiveDashboard', {
        activeTab,
        count: dataset.length,
        proofHash: exportProof
      });
      exportCSV(dataset, `wilsy_executive_${activeTab}_exhaustive_${Date.now()}`, { tenantId });
    } catch (err) {
      console.error('[EXEC-EXPORT-FRACTURE]', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function runCurrencyConversion
   * @description Converts the operator-entered FX amount through the protected finance FX route.
   * @returns {Promise<void>} Resolves after conversion receipt is stored locally.
   * @collaboration Currency conversion is an executive tool, not a decorative rate card; every conversion receives source status and proof.
   */
  const runCurrencyConversion = async () => {
    try {
      setIsRefreshing(true);
      const conversion = await requestCurrencyConversion({
        tenantId,
        amount: currencyWorkbench.amount,
        fromCurrency: currencyWorkbench.fromCurrency,
        toCurrency: currencyWorkbench.toCurrency
      });
      setCurrencyWorkbench(prev => ({
        ...prev,
        conversion,
        sourceStatus: conversion.sourceStatus || prev.sourceStatus,
        proofHash: conversion.proofHash || prev.proofHash
      }));
      setSourceSnapshot(prev => ({
        ...prev,
        fx: {
          status: conversion.sourceStatus || 'FX_CONVERSION_SOURCE_SILENT',
          live: Boolean(conversion.success),
          lastSync: new Date().toISOString(),
          proofHash: conversion.proofHash || null
        }
      }));
      await broadcastTelemetry(tenantId, 'EXEC_FX_CONVERSION_COMMAND', conversion.sourceStatus || 'FX_SOURCE_UNKNOWN', 'ExecutiveDashboard', {
        fromCurrency: currencyWorkbench.fromCurrency,
        toCurrency: currencyWorkbench.toCurrency,
        proofHash: conversion.proofHash || null
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function updateBusinessModelOverride
   * @description Applies an operator-selected business model for the current executive session and broadcasts the selection.
   * @param {string} nextModel - Business model key or empty string for tenant auto-detection.
   * @returns {Promise<void>} Resolves after local context and telemetry are updated.
   * @collaboration Wilson needs one dashboard that adapts to each tenant; this records who selected the operating model and why it changed.
   */
  const updateBusinessModelOverride = async (nextModel) => {
    setBusinessModelOverride(nextModel);
    await broadcastTelemetry(tenantId, 'EXEC_Business Model_SELECTION', nextModel || 'TENANT_AUTO_DETECT', 'ExecutiveDashboard', {
      tenantId,
      selectedModel: nextModel || null,
      previousModel: executiveOperatingSystem.profile.industryKey,
      proofHash: createExecutiveProofHash({
        tenantId,
        selectedModel: nextModel || 'TENANT_AUTO_DETECT',
        suiteVersion: EXECUTIVE_SUITE_VERSION
      })
    }).catch(() => {});
  };

  /**
   * @function acceptDailyDuty
   * @description Converts a source-aware daily duty into an executive strategic goal receipt.
   * @param {Object} duty - Daily duty selected by the executive.
   * @returns {Promise<void>} Resolves after the duty is committed to local telemetry-backed state.
   * @collaboration Makes the dashboard useful every morning: work can be accepted, tracked and audited.
   */
  const acceptDailyDuty = async (duty) => {
    if (!duty?.title) return;
    try {
      setIsRefreshing(true);
      const workOrder = buildExecutiveWorkOrder({
        duty,
        tenantId,
        tenantProfile: executiveOperatingSystem.profile,
        functionMatrix: executiveOperatingSystem.functionMatrix,
        sourceSnapshot,
        status: 'DUTY_ACCEPTED'
      });
      await commitExecutiveWorkOrder(workOrder, duty.status === 'READY' ? 'DUTY_ACCEPTED' : 'DUTY_ACCEPTED_WITH_GATES');
      setActiveTab('strategicGoals');
    } catch (error) {
      console.error('[EXEC-DUTY-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_DUTY_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        dutyKey: duty.key,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function activateWilsyAiUseCase
   * @description Commits a Wilsy AI license-intent packet for a tenant-specific automation use case.
   * @param {Object} plan - Wilsy AI license plan row.
   * @returns {Promise<void>} Resolves after telemetry and strategic-goal receipts are created.
   * @collaboration Wilsy AI becomes a monetisable tenant service while preserving source gates and permission audit.
   */
  const activateWilsyAiUseCase = async (plan) => {
    if (!plan?.name || plan.readiness === 'ACCESS_DENIED') return;
    try {
      setIsRefreshing(true);
      const activationReceipt = await requestWilsyAILicenseActivation({
        tenantId,
        plan,
        tenantProfile: executiveOperatingSystem.profile,
        sourceSnapshot
      });
      const activationSucceeded = Boolean(activationReceipt.success);
      const proofHash = activationReceipt.proofHash || createExecutiveProofHash({
        tenantId,
        plan,
        activationReceipt,
        suiteVersion: EXECUTIVE_SUITE_VERSION
      });
      await broadcastTelemetry(tenantId, 'EXEC_WILSY_AI_LICENSE_INTENT', plan.readiness, 'ExecutiveDashboard', {
        planId: plan.id,
        moduleId: plan.moduleId,
        tier: plan.tier,
        lane: plan.lane,
        readiness: plan.readiness,
        activationStatus: activationReceipt.status,
        proofHash
      });
      await commitExecutiveRecord({
        tab: 'strategicGoals',
        type: 'strategicGoal',
        payload: {
          title: `Activate ${plan.name}`,
          progress: activationSucceeded ? 20 : 0,
          deadline: todayIso(),
          status: activationSucceeded ? 'on_track' : 'at_risk',
          lane: plan.lane,
          tier: plan.tier,
          sourceStatus: plan.sourceStatus,
          licenseId: activationReceipt.license?.licenseId || plan.licenseId || '',
          activationStatus: activationReceipt.status,
          proofHash
        },
        receiptStatus: activationSucceeded ? 'WILSY_AI_LICENSED' : 'WILSY_AI_LICENSE_BLOCKED'
      });
      const entitlementSync = await syncWilsyAIEntitlements({
        tenantId,
        tenantProfile: executiveOperatingSystem.profile,
        sourceSnapshot
      });
      setWilsyAIEntitlements({
        status: entitlementSync.status,
        plans: entitlementSync.plans || [],
        licenses: entitlementSync.licenses || [],
        proofHash: entitlementSync.proofHash || null,
        error: entitlementSync.error || null
      });
      setActiveTab('strategicGoals');
    } catch (error) {
      console.error('[EXEC-WILSY-AI-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_WILSY_AI_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        planId: plan.id,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function logWilsyAiRequest
   * @description Records a Wilsy AI request against the tenant quota ledger.
   * @param {Object} plan - Active Wilsy AI plan.
   * @returns {Promise<void>} Resolves after usage receipt and entitlement refresh.
   * @collaboration This is how Wilsy AI becomes a measurable paid operating layer instead of a generic chat widget.
   */
  const logWilsyAiRequest = async (plan) => {
    if (!plan?.moduleId || plan.licenseStatus !== 'ACTIVE') return;
    try {
      setIsRefreshing(true);
      const receipt = await requestWilsyAIUsageRecord({
        tenantId,
        plan,
        requestUnits: 1,
        status: 'PLANNED',
        sourceStatus: plan.sourceStatus || 'EXECUTIVE_DASHBOARD',
        sourceEvidence: plan.differentiator || plan.valuePromise || '',
        sourceSnapshot
      });
      await broadcastTelemetry(tenantId, 'EXEC_WILSY_AI_USAGE_COMMAND', receipt.status || 'USAGE_RECORDED', 'ExecutiveDashboard', {
        moduleId: plan.moduleId,
        tier: plan.tier,
        proofHash: receipt.proofHash || null
      }).catch(() => {});
      const entitlementSync = await syncWilsyAIEntitlements({
        tenantId,
        tenantProfile: executiveOperatingSystem.profile,
        sourceSnapshot
      });
      setWilsyAIEntitlements({
        status: entitlementSync.status,
        plans: entitlementSync.plans || [],
        licenses: entitlementSync.licenses || [],
        proofHash: entitlementSync.proofHash || null,
        error: entitlementSync.error || null
      });
    } catch (error) {
      console.error('[EXEC-WILSY-AI-USAGE-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_WILSY_AI_USAGE_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        planId: plan.id,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function commitExecutiveWorkOrder
   * @description Persists a local executive work order receipt and mirrors it into the strategic-goal ledger.
   * @param {Object} workOrder - Work order generated by the command orchestrator.
   * @param {string} receiptStatus - Receipt status label.
   * @returns {Promise<void>} Resolves after telemetry and local state are updated.
   * @collaboration Daily executive work becomes a provable command artifact instead of a clicked card with no business memory.
   */
  const commitExecutiveWorkOrder = async (workOrder, receiptStatus = 'WORK_ORDER_ACCEPTED') => {
    if (!workOrder?.workOrderId) return;
    setExecutiveWorkOrders(prev => [
      workOrder,
      ...prev.filter(order => order.workOrderId !== workOrder.workOrderId)
    ].slice(0, 10));
    setSelectedWorkOrderId(workOrder.workOrderId);
    await broadcastTelemetry(tenantId, 'EXEC_WORK_ORDER_COMMAND', receiptStatus, 'ExecutiveDashboard', {
      workOrderId: workOrder.workOrderId,
      lane: workOrder.lane,
      functionKey: workOrder.functionKey,
      route: workOrder.route?.route,
      proofHash: workOrder.proofHash
    }).catch(() => {});
    await commitExecutiveRecord({
      tab: 'strategicGoals',
      type: 'strategicGoal',
      payload: {
        title: workOrder.title,
        progress: workOrder.blocked ? 0 : 15,
        deadline: todayIso(),
        status: workOrder.blocked ? 'at_risk' : 'on_track',
        lane: workOrder.lane,
        reason: workOrder.reason,
        sourceStatus: workOrder.status,
        evidenceRequired: workOrder.evidenceRequired || [],
        workflowSteps: workOrder.workflowSteps || [],
        route: workOrder.route?.route,
        functionKey: workOrder.functionKey,
        businessModel: workOrder.industryKey,
        proofHash: workOrder.proofHash
      },
      receiptStatus
    });
  };

  /**
   * @function executeFunctionCard
   * @description Opens, requests or audits a tenant operating function from the function matrix.
   * @param {Object} functionRow - Function entitlement row.
   * @returns {Promise<void>} Resolves after the function command is routed or access-requested.
   * @collaboration Every enabled function becomes usable; every denied function gives the executive the correct channel instead of dead UI.
   */
  const executeFunctionCard = async (functionRow) => {
    if (!functionRow?.key) return;
    try {
      setIsRefreshing(true);
      const commandPacket = buildFunctionCommandPacket({
        functionRow,
        tenantId,
        tenantProfile: executiveOperatingSystem.profile
      });
      await broadcastTelemetry(tenantId, 'EXEC_FUNCTION_COMMAND', commandPacket.action, 'ExecutiveDashboard', {
        functionKey: commandPacket.functionKey,
        route: commandPacket.route.route,
        proofHash: commandPacket.proofHash
      }).catch(() => {});

      if (!isFunctionExecutable(functionRow)) {
        await commitExecutiveRecord({
          tab: 'strategicGoals',
          type: 'strategicGoal',
          payload: {
            title: `Request access: ${commandPacket.functionLabel}`,
            progress: 0,
            deadline: todayIso(),
            status: 'blocked',
            lane: commandPacket.route.channel,
            functionKey: commandPacket.functionKey,
            sourceStatus: commandPacket.sourceStatus,
            reason: `Function ${commandPacket.functionLabel} is not granted for ${executiveOperatingSystem.profile.name}.`,
            route: commandPacket.route.route,
            proofHash: commandPacket.proofHash
          },
          receiptStatus: 'FUNCTION_ACCESS_REQUESTED'
        });
        setActiveTab('strategicGoals');
        return;
      }

      await executeCommand?.(commandPacket.route.command, commandPacket.route.route, 'GET', {
        tenantId,
        source: 'ExecutiveDashboard',
        functionKey: commandPacket.functionKey,
        proofHash: commandPacket.proofHash
      });
      setMutationReceipts(prev => [{
        id: commandPacket.commandId,
        timestamp: commandPacket.generatedAt,
        eventType: 'EXEC_FUNCTION_COMMAND',
        event: 'ROUTED',
        message: `${commandPacket.functionLabel} routed to ${commandPacket.route.route}`,
        proofHash: commandPacket.proofHash,
        envelope: commandPacket
      }, ...prev].slice(0, MAX_ACTIVITY_ROWS));
    } catch (error) {
      console.error('[EXEC-FUNCTION-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_FUNCTION_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        functionKey: functionRow.key,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function runExecutiveWorkOrder
   * @description Routes the selected work order into its Wilsy OS module and upgrades its local status.
   * @param {Object} workOrder - Selected work order.
   * @returns {Promise<void>} Resolves after command routing is recorded.
   * @collaboration Accepted work must move into execution; the command receipt tells the tenant what happened and why.
   */
  const runExecutiveWorkOrder = async (workOrder) => {
    if (!workOrder?.workOrderId) return;
    try {
      setIsRefreshing(true);
      const nextStatus = workOrder.blocked ? 'BLOCKED_REVIEW_REQUIRED' : 'ROUTED_TO_MODULE';
      const routedOrder = {
        ...workOrder,
        status: nextStatus,
        routedAt: new Date().toISOString(),
        proofHash: createExecutiveProofHash({ ...workOrder, nextStatus, routedAt: new Date().toISOString() })
      };
      setExecutiveWorkOrders(prev => prev.map(order => (
        order.workOrderId === workOrder.workOrderId ? routedOrder : order
      )));
      await broadcastTelemetry(tenantId, 'EXEC_WORK_ORDER_ROUTED', nextStatus, 'ExecutiveDashboard', {
        workOrderId: workOrder.workOrderId,
        route: workOrder.route?.route,
        proofHash: routedOrder.proofHash
      }).catch(() => {});
      if (!workOrder.blocked) {
        await executeCommand?.(workOrder.route?.command || 'EXEC_WORK_ORDER_ROUTED', workOrder.route?.route || '/executive', 'GET', {
          tenantId,
          workOrderId: workOrder.workOrderId,
          proofHash: routedOrder.proofHash
        });
      }
    } catch (error) {
      console.error('[EXEC-WORK-ORDER-ROUTE-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_WORK_ORDER_ROUTE_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        workOrderId: workOrder.workOrderId,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function requestSourceRepair
   * @description Converts a silent source into an explicit repair work order for the tenant owner or Wilsy administrator.
   * @param {Object} repairAction - Source repair descriptor.
   * @returns {Promise<void>} Resolves after the repair command is recorded.
   * @collaboration Source gaps should be actionable; the executive sees the exact module and channel required to repair the operating source.
   */
  const requestSourceRepair = async (repairAction) => {
    if (!repairAction?.id) return;
    try {
      setIsRefreshing(true);
      await broadcastTelemetry(tenantId, 'EXEC_SOURCE_REPAIR_REQUEST', repairAction.sourceKey, 'ExecutiveDashboard', {
        route: repairAction.route?.route,
        proofHash: repairAction.proofHash
      }).catch(() => {});
      await commitExecutiveRecord({
        tab: 'strategicGoals',
        type: 'strategicGoal',
        payload: {
          title: repairAction.title,
          progress: 0,
          deadline: todayIso(),
          status: 'at_risk',
          lane: repairAction.route?.channel || 'Administration',
          sourceStatus: repairAction.reason,
          reason: `Repair route ${repairAction.route?.route || '/settings'} for ${repairAction.tenantFit}.`,
          route: repairAction.route?.route,
          proofHash: repairAction.proofHash
        },
        receiptStatus: 'SOURCE_REPAIR_REQUESTED'
      });
      setActiveTab('strategicGoals');
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function persistBusinessModelCommand
   * @description Commits the current business model selection as a tenant-profile update instruction.
   * @returns {Promise<void>} Resolves after the instruction is proofed.
   * @collaboration Operator-selected business models are session-safe until persisted; this records the correct channel without fake backend mutation.
   */
  const persistBusinessModelCommand = async () => {
    const profile = executiveOperatingSystem.profile;
    await commitExecutiveRecord({
      tab: 'strategicGoals',
      type: 'strategicGoal',
      payload: {
        title: `Persist tenant business model: ${profile.industryLabel}`,
        progress: profile.sourceStatus === 'OPERATOR_DECLARED_Business Model' ? 10 : 100,
        deadline: todayIso(),
        status: profile.sourceStatus === 'OPERATOR_DECLARED_Business Model' ? 'on_track' : 'committed',
        lane: 'Administration',
        businessModel: profile.industryKey,
        sourceStatus: profile.sourceStatus,
        reason: profile.sourceEvidence,
        route: '/settings/tenant-profile',
        proofHash: createExecutiveProofHash({
          tenantId,
          businessModel: profile.industryKey,
          sourceStatus: profile.sourceStatus,
          suiteVersion: EXECUTIVE_SUITE_VERSION
        })
      },
      receiptStatus: 'Business Model_PROFILE_COMMAND'
    });
    setActiveTab('strategicGoals');
  };

  /**
   * @function askExecutiveOS
   * @description Answers a constrained executive natural-language question from local source-aware playbook data.
   * @param {Event} event - Optional form submit event.
   * @returns {Promise<void>} Resolves after the answer is stored and telemetry is broadcast.
   * @collaboration Adds roadmap-level natural language without pretending a remote AI answered when only local evidence was used.
   */
  const askExecutiveOS = async (event) => {
    event?.preventDefault?.();
    const answer = answerExecutiveNaturalLanguageQuery({
      question: executiveQuestion,
      financialKPIs,
      sourceRows,
      executiveReadiness,
      transformationPlaybook: executiveTransformation
    });
    if (!answer) return;
    setExecutiveAnswer(answer);
    await broadcastTelemetry(tenantId, 'EXEC_NATURAL_LANGUAGE_QUERY', answer.intent, 'ExecutiveDashboard', {
      question: executiveQuestion,
      intent: answer.intent,
      proofHash: answer.proofHash
    }).catch(() => {});
  };

  /**
   * @function handleAccountCommand
   * @description Routes account command center actions through telemetry and the host command router when available.
   * @param {string} action - Account action identifier.
   * @param {Object} payload - Account command payload.
   * @returns {Promise<void>} Resolves after the account command is routed or recorded.
   * @collaboration Turns Settings, My Account, Security, MFA, Sessions, Privacy and Compliance into real OS command routes instead of dead UI.
   */
  const handleAccountCommand = useCallback(async (action, payload = {}) => {
    const route = payload?.route || '/account';
    const commandName = `EXEC_ACCOUNT_${String(action || 'COMMAND').toUpperCase()}`;
    const proofHash = createExecutiveProofHash({
      tenantId,
      action,
      route,
      role,
      suiteVersion: EXECUTIVE_SUITE_VERSION
    });

    await broadcastTelemetry(tenantId, commandName, 'ACCOUNT_COMMAND_CAPTURED', 'ExecutiveDashboard', {
      action,
      route,
      proofHash
    }).catch(() => {});

    if (typeof executeCommand === 'function' && route) {
      await executeCommand(commandName, route, 'GET', {
        tenantId,
        source: 'ExecutiveDashboard',
        action,
        proofHash
      }).catch(error => {
        broadcastTelemetry(tenantId, 'EXEC_ACCOUNT_COMMAND_ROUTE_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
          action,
          route,
          error: error.message,
          proofHash
        }).catch(() => {});
      });
    }
  }, [executeCommand, role, tenantId]);

  /**
   * @function handleExecutiveSignOut
   * @description Routes sign out through the host auth handler or records a governed logout command.
   * @returns {Promise<void>} Resolves after sign out intent is handled.
   * @collaboration Keeps Sign Out real without assuming every dashboard host exposes the same auth callback.
   */
  const handleExecutiveSignOut = useCallback(async () => {
    if (typeof onSignOut === 'function') {
      onSignOut();
      await broadcastTelemetry(tenantId, 'EXEC_ACCOUNT_SIGN_OUT', 'ROUTED', 'ExecutiveDashboard', {
        proofHash: createExecutiveProofHash({ tenantId, action: 'sign_out', suiteVersion: EXECUTIVE_SUITE_VERSION })
      }).catch(() => {});
      return;
    }

    await handleAccountCommand('sign_out', { route: '/auth/logout' });
  }, [handleAccountCommand, onSignOut, tenantId]);

  /**
   * @function isFounderReturnEligible
   * @description Determines whether the floating Founder return command should render.
   * @returns {boolean} True when founder return should be available.
   * @collaboration Keeps founder navigation conditional and executive-safe instead of occupying permanent cockpit space.
   */
  const isFounderReturnEligible = useMemo(() => (
    Boolean(founderReturnEnabled || typeof onFounderReturn === 'function')
  ), [founderReturnEnabled, onFounderReturn]);

  /**
   * @function handleFounderReturn
   * @description Routes the operator back to the Founder command center when permitted.
   * @returns {Promise<void>} Resolves after founder return is routed or recorded.
   * @collaboration Makes founder return a smooth conditional OS transition rather than a fixed top-bar interruption.
   */
  const handleFounderReturn = useCallback(async () => {
    const proofHash = createExecutiveProofHash({
      tenantId,
      action: 'return_to_founder_dashboard',
      role,
      suiteVersion: EXECUTIVE_SUITE_VERSION
    });

    await broadcastTelemetry(tenantId, 'EXEC_FOUNDER_RETURN_REQUESTED', 'ROUTED', 'ExecutiveDashboard', {
      proofHash
    }).catch(() => {});

    if (typeof onFounderReturn === 'function') {
      onFounderReturn({ tenantId, proofHash, source: 'ExecutiveDashboard' });
      return;
    }

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:navigate-dashboard', {
        detail: {
          dashboardKey: 'founder',
          route: '/founder',
          tenantId,
          proofHash,
          source: 'ExecutiveDashboard'
        }
      }));

      window.localStorage.setItem('wilsy:requested-dashboard', JSON.stringify({
        dashboardKey: 'founder',
        route: '/founder',
        tenantId,
        proofHash,
        requestedAt: new Date().toISOString()
      }));
    }

    await handleAccountCommand('return_to_founder_dashboard', {
      route: '/founder',
      dashboardKey: 'founder',
      proofHash
    });
  }, [handleAccountCommand, onFounderReturn, role, tenantId]);

  /**
   * @function executeVerticalSystemRoute
   * @description Routes the CEO cockpit into a full Wilsy OS vertical system.
   * @param {Object} system - Vertical system descriptor.
   * @returns {Promise<void>} Resolves after the vertical transition is routed or recorded.
   * @collaboration Keeps ExecutiveDashboard as the CEO gateway while HR, CRM, Billing, Documents and Legal remain full real systems.
   */
  const executeVerticalSystemRoute = useCallback(async (system) => {
    const proofHash = createExecutiveProofHash({
      tenantId,
      action: system.command,
      route: system.route,
      dashboardKey: system.dashboardKey,
      role,
      suiteVersion: EXECUTIVE_SUITE_VERSION
    });

    await broadcastTelemetry(tenantId, 'EXEC_VERTICAL_SYSTEM_ROUTE', system.command, 'ExecutiveDashboard', {
      label: system.label,
      route: system.route,
      dashboardKey: system.dashboardKey,
      proofHash
    }).catch(() => {});

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:navigate-dashboard', {
        detail: {
          dashboardKey: system.dashboardKey,
          route: system.route,
          tenantId,
          proofHash,
          source: 'ExecutiveDashboard'
        }
      }));

      window.localStorage.setItem('wilsy:requested-dashboard', JSON.stringify({
        dashboardKey: system.dashboardKey,
        route: system.route,
        label: system.label,
        tenantId,
        proofHash,
        requestedAt: new Date().toISOString()
      }));
    }

    if (typeof executeCommand === 'function') {
      await executeCommand(system.command, system.route, 'GET', {
        tenantId,
        dashboardKey: system.dashboardKey,
        proofHash,
        source: 'ExecutiveDashboard'
      }).catch(error => {
        broadcastTelemetry(tenantId, 'EXEC_VERTICAL_ROUTE_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
          label: system.label,
          route: system.route,
          error: error.message,
          proofHash
        }).catch(() => {});
      });
      return;
    }

    await handleAccountCommand(system.command, {
      route: system.route,
      dashboardKey: system.dashboardKey,
      proofHash
    });
  }, [executeCommand, handleAccountCommand, role, tenantId]);


  /**
   * @function executeExecutiveCommand
   * @description Runs high-level executive command rail actions with telemetry and tenant isolation.
   * @param {string} commandId - Command identifier.
   * @returns {Promise<void>} Resolves when the selected command is completed or audited as failed.
   * @collaboration Keeps executive work as action, not static dashboard observation.
   */
  const executeExecutiveCommand = async (commandId) => {
    try {
      setIsRefreshing(true);
      const timestamp = new Date().toISOString();
      if (commandId === 'KPI_REBASE') {
        await loadAllData();
        await broadcastTelemetry(tenantId, 'EXEC_KPI_REBASE_COMMAND', 'COMMITTED', 'ExecutiveDashboard', {
          source: 'financeService',
          proofHash: createExecutiveProofHash({ tenantId, commandId, timestamp, financialKPIs })
        });
        return;
      }

      if (commandId === 'BOARD_PACKET') {
        const financeReady = Boolean(sourceSnapshot.finance?.live);
        const payload = {
          title: `${executiveOperatingSystem.profile.name} Board Packet ${todayIso()}`,
          date: todayIso(),
          author: role,
          status: financeReady ? 'sealed' : 'draft',
          businessModel: executiveOperatingSystem.profile.industryKey,
          sourceStatus: financeReady ? sourceSnapshot.finance.status : 'FINANCE_SOURCE_REQUIRED',
          revenue: financialKPIs.revenue,
          arr: financialKPIs.arr,
          currency: financialKPIs.currency || DEFAULT_OPERATING_CURRENCY
        };
        await commitExecutiveRecord({
          tab: 'boardReports',
          type: 'boardReport',
          payload,
          receiptStatus: financeReady ? 'SEALED' : 'BOARD_PACKET_DRAFT_SOURCE_GATED'
        });
        await executeCommand?.('EXEC_BOARD_PACKET', '/statements/revenue', 'GET', {
          tenantId,
          source: 'ExecutiveDashboard',
          businessModel: executiveOperatingSystem.profile.industryKey
        });
        setActiveTab('boardReports');
        return;
      }

      if (commandId === 'INVESTOR_BRIEF') {
        const financeReady = Boolean(sourceSnapshot.finance?.live);
        await commitExecutiveRecord({
          tab: 'investorUpdates',
          type: 'investorUpdate',
          payload: {
            title: `${executiveOperatingSystem.profile.name} Investor Brief ${todayIso()}`,
            date: todayIso(),
            audience: 'Institutional',
            status: financeReady ? 'sent' : 'draft',
            businessModel: executiveOperatingSystem.profile.industryKey,
            sourceStatus: financeReady ? sourceSnapshot.finance.status : 'FINANCE_SOURCE_REQUIRED',
            readiness: executiveReadiness.score
          },
          receiptStatus: financeReady ? 'DISPATCHED' : 'INVESTOR_BRIEF_DRAFT_SOURCE_GATED'
        });
        setActiveTab('investorUpdates');
        return;
      }

      if (commandId === 'STRATEGIC_MANDATE') {
        await commitExecutiveRecord({
          tab: 'strategicGoals',
          type: 'strategicGoal',
          payload: {
            title: `Executive Mandate: ${executiveReadiness.posture}`,
            progress: Math.min(100, executiveReadiness.score),
            deadline: todayIso(),
            status: executiveReadiness.score >= 70 ? 'on_track' : 'at_risk'
          },
          receiptStatus: 'MANDATED'
        });
        setActiveTab('strategicGoals');
        return;
      }

      if (commandId === 'TRANSFORMATION_PLAYBOOK') {
        const action = executiveTransformation.priorityActions?.[0] || {};
        await commitExecutiveRecord({
          tab: 'strategicGoals',
          type: 'strategicGoal',
          payload: {
            title: action.title || `Execute ${executiveTransformation.phase?.label || 'executive transformation playbook'}`,
            progress: executiveTransformation.phaseProgress || 0,
            deadline: todayIso(),
            status: executiveTransformation.phaseProgress >= 35 ? 'on_track' : 'at_risk',
            lane: action.lane || 'Executive',
            phase: executiveTransformation.phase?.key,
            arr: executiveTransformation.arr,
            sourceStatus: action.status || executiveReadiness.posture,
            reason: executiveTransformation.phase?.mandate,
            route: action.route || '/executive',
            proofHash: executiveTransformation.proofHash
          },
          receiptStatus: 'TRANSFORMATION_PLAYBOOK_ACCEPTED'
        });
        setActiveTab('strategicGoals');
        return;
      }

      if (commandId === 'INTEGRATION_SPRINT') {
        const connector = executiveTransformation.integrationRows?.find(row => row.status !== 'CONNECTED')
          || executiveTransformation.integrationRows?.[0];
        if (!connector) return;
        await commitExecutiveRecord({
          tab: 'strategicGoals',
          type: 'strategicGoal',
          payload: {
            title: `Connect ${connector.label}`,
            progress: connector.status === 'READY_TO_CONNECT' ? 35 : 0,
            deadline: todayIso(),
            status: connector.status === 'READY_TO_CONNECT' ? 'on_track' : 'blocked',
            lane: connector.lane,
            sourceStatus: connector.status,
            reason: connector.nextAction,
            route: connector.route,
            proofHash: connector.proofHash
          },
          receiptStatus: connector.status === 'READY_TO_CONNECT' ? 'INTEGRATION_SPRINT_READY' : 'INTEGRATION_SOURCE_GATED'
        });
        setActiveTab('strategicGoals');
        return;
      }

      if (commandId === 'TRUST_PACKET') {
        const trustScore = Math.round(
          (executiveTransformation.trustRows || []).reduce((sum, row) => sum + Number(row.score || 0), 0)
          / Math.max(1, executiveTransformation.trustRows?.length || 1)
        );
        await commitExecutiveRecord({
          tab: 'boardReports',
          type: 'boardReport',
          payload: {
            title: `${executiveOperatingSystem.profile.name} Enterprise Trust Packet ${todayIso()}`,
            date: todayIso(),
            author: role,
            status: trustScore >= 70 ? 'sealed' : 'draft',
            sourceStatus: trustScore >= 70 ? 'TRUST_EVIDENCE_READY' : 'TRUST_EVIDENCE_BUILDING',
            trustScore,
            complianceRows: executiveTransformation.trustRows?.map(row => `${row.label}:${row.status}`),
            proofHash: executiveTransformation.proofHash
          },
          receiptStatus: trustScore >= 70 ? 'TRUST_PACKET_SEALED' : 'TRUST_PACKET_DRAFT'
        });
        setActiveTab('boardReports');
        return;
      }

      if (commandId === 'WILSY_AI_LICENSE') {
        await activateWilsyAiUseCase(wilsyAiPlan[0]);
      }
    } catch (error) {
      console.error('[EXEC-COMMAND-FRACTURE]', error);
      await broadcastTelemetry(tenantId, 'EXEC_COMMAND_FRACTURE', 'FRACTURE', 'ExecutiveDashboard', {
        commandId,
        error: error.message
      }).catch(() => {});
    } finally {
      setIsRefreshing(false);
    }
  };

  const sourceRows = useMemo(() => Object.entries({
    ...sourceSnapshot,
    profile: {
      status: executiveOperatingSystem.profile.sourceStatus,
      live: executiveOperatingSystem.profile.sourceStatus !== 'TENANT_PROFILE_INCOMPLETE',
      lastSync: new Date().toISOString(),
      industry: executiveOperatingSystem.profile.industryLabel
    }
  }).map(([key, source]) => ({
    key,
    ...source
  })), [executiveOperatingSystem.profile, sourceSnapshot]);
  const sourceRepairQueue = useMemo(() => (
    buildExecutiveSourceRepairQueue(sourceRows, executiveOperatingSystem.profile)
  ), [executiveOperatingSystem.profile, sourceRows]);
  const selectedWorkOrder = useMemo(() => (
    executiveWorkOrders.find(order => order.workOrderId === selectedWorkOrderId) || executiveWorkOrders[0] || null
  ), [executiveWorkOrders, selectedWorkOrderId]);
  const operatingSourceCoverage = useMemo(() => ({
    live: operatingSources.filter(source => source.live).length,
    total: operatingSources.length
  }), [operatingSources]);

  const executiveReadiness = useMemo(() => {
    const liveSources = sourceRows.filter(source => source.live).length;
    const sourceScore = sourceRows.length ? (liveSources / sourceRows.length) * 45 : 0;
    const telemetryScore = telemetryError ? 8 : 20;
    const proofScore = mutationReceipts.length ? 20 : 12;
    const paginationScore = Object.values(pageStates).every(page => Number(page.limit) <= 25) ? 15 : 8;
    const score = Math.round(sourceScore + telemetryScore + proofScore + paginationScore);
    return {
      score: Math.min(100, score),
      posture: score >= 84 ? 'EXECUTIVE_EPITOME' : score >= 62 ? 'COMMAND_READY' : 'SOURCE_GAPS',
      liveSources,
      totalSources: sourceRows.length
    };
  }, [mutationReceipts.length, pageStates, sourceRows, telemetryError]);

  const executiveTransformation = useMemo(() => (
    buildExecutiveTransformationPlaybook({
      activeTenant,
      financialKPIs,
      sourceSnapshot,
      sourceRows,
      profile: executiveOperatingSystem.profile,
      executiveReadiness,
      wilsyAiPlan,
      accessDecision,
      mutationReceipts
    })
  ), [
    accessDecision,
    activeTenant,
    executiveOperatingSystem.profile,
    executiveReadiness,
    financialKPIs,
    mutationReceipts,
    sourceRows,
    sourceSnapshot,
    wilsyAiPlan
  ]);

  const executiveMemo = useMemo(() => {
    const arr = financialKPIs.arr ?? null;
    const revenue = financialKPIs.revenue ?? null;
    const arrNumeric = Number(arr || 0);
    const highestDuty = executiveOperatingSystem.dailyDuties[0];
    const nextAction = highestDuty?.title
      ? highestDuty.title
      : executiveReadiness.score < 62
      ? 'Stabilize finance and telemetry sources before board export.'
      : arrNumeric > 0
        ? 'Seal board packet and dispatch investor brief from current finance posture.'
        : 'Rebase KPIs, then create first revenue-backed board packet.';
    return {
      arr,
      revenue,
      industry: executiveOperatingSystem.profile.industryLabel,
      dutyReason: highestDuty?.reason || '',
      sourcePosture: `${executiveReadiness.liveSources}/${executiveReadiness.totalSources} sources live`,
      nextAction,
      proofHash: createExecutiveProofHash({
        tenantId,
        arr: arrNumeric,
        revenue: Number(revenue || 0),
        industry: executiveOperatingSystem.profile.industryKey,
        duty: highestDuty?.key,
        readiness: executiveReadiness.score,
        suiteVersion: EXECUTIVE_SUITE_VERSION
      })
    };
  }, [executiveOperatingSystem, executiveReadiness, financialKPIs, tenantId]);

  /**
   * @function renderPagination
   * @description Renders shard pagination controls for the active executive table.
   * @param {string} tabKey - Executive tab key.
   * @param {number} total - Total filtered rows.
   * @returns {JSX.Element} Pagination controls.
   * @collaboration Keeps large tenant data navigable without loading every board artifact into view.
   */
  const renderPagination = (tabKey, total) => {
    const pageState = pageStates[tabKey];
    const totalPages = Math.ceil(total / pageState.limit);
    return (
      <div className={styles.pagination}>
        <button
          onClick={() => updatePageOffset(tabKey, false)}
          disabled={pageState.offset === 0 || isRefreshing}
          className={styles.secondaryButton}
        >
          PREV
        </button>
        <div className={styles.pageReadout}>
          <span>
            PAGE {Math.floor(pageState.offset / pageState.limit) + 1} / {totalPages || 1}
          </span>
          <small>
            ROWS {total ? pageState.offset + 1 : 0}-{Math.min(pageState.offset + pageState.limit, total)} / {total}
          </small>
        </div>
        <button
          onClick={() => updatePageOffset(tabKey, true)}
          disabled={pageState.offset + pageState.limit >= total || isRefreshing}
          className={styles.secondaryButton}
        >
          NEXT
        </button>
      </div>
    );
  };

  /**
   * @function renderTable
   * @description Renders a reusable executive ledger table with empty-source honesty.
   * @param {Array<Object>} items - Visible rows.
   * @param {Array<string>} headers - Table headers.
   * @param {Function} renderRow - Row renderer.
   * @param {string} tabKey - Executive tab key.
   * @param {number} total - Total filtered rows.
   * @returns {JSX.Element} Executive data table.
   * @collaboration Prevents every tab from reinventing table mechanics and losing audit consistency.
   */
  const renderTable = (items, headers, renderRow, tabKey, total) => (
    <div className={styles.tableShell} data-refreshing={isRefreshing ? 'true' : 'false'}>
      <div className={styles.tableScroll}>
        <table className={styles.dataTable}>
          <thead>
            <tr>
              {headers.map((h) => (
                <th key={h}>
                  {h}
                </th>
              ))}
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <React.Fragment key={item.id}>{renderRow(item)}</React.Fragment>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={headers.length + 1} className={styles.emptyCell}>
                  NO_EXECUTIVE_RECORDS_FOUND
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {renderPagination(tabKey, total)}
    </div>
  );

  /**
   * @function renderContent
   * @description Chooses the active executive ledger view.
   * @returns {JSX.Element|null} Active tab content.
   * @collaboration A single command surface can serve KPI, board, investor and mandate workflows.
   */
  const renderContent = () => {
    switch (activeTab) {
      case 'kpis':
        return renderTable(
          kpis.items,
          ['Metric', 'Value', 'Target', 'Unit', 'Source', 'Proof', 'Sync'],
          (k) => (
            <tr className={styles.tableRow}>
              <td><strong>{k.name}</strong></td>
              <td className={styles.moneyCell}>
                {formatExecutiveKpiValue(k.value, k.unit)}
              </td>
              <td>
                {formatExecutiveKpiValue(k.target, k.unit)}
              </td>
              <td>{k.unit}</td>
              <td><span className={styles.sourceChip} title={k.sourceStatus || 'SOURCE_UNKNOWN'}>{compactExecutiveSignal(k.sourceStatus || 'SOURCE_UNKNOWN')}</span></td>
              <td className={styles.proofCell}>{k.proofHash?.slice(0, 14) || 'UNSEALED'}</td>
              <td>{new Date(k.updatedAt).toLocaleDateString()}</td>
              <td>
                <div className={styles.rowActions}>
                <button
                  onClick={() => {
                    setEditingItem(k);
                    setModalType('kpi');
                    setShowModal(true);
                  }}
                  className={styles.iconButton}
                >
                  <Edit size={14} />
                </button>
                <button onClick={() => handleDelete(k.id, 'kpi')} className={`${styles.iconButton} ${styles.dangerButton}`}>
                  <Trash2 size={14} />
                </button>
                </div>
              </td>
            </tr>
          ),
          'kpis',
          kpis.total
        );
      case 'boardReports':
        return renderTable(
          boardReports.items,
          ['Report', 'Date', 'Owner', 'Status', 'Source', 'Proof'],
          (r) => (
            <tr className={styles.tableRow}>
              <td><strong>{r.title}</strong></td>
              <td>{new Date(r.date).toLocaleDateString()}</td>
              <td>{r.author}</td>
              <td>
                <span className={`${styles.statusPill} ${styles[getExecutiveStatusTone(r.status)]}`}>
                  {r.status}
                </span>
              </td>
              <td><span className={styles.sourceChip} title={r.sourceStatus || 'SOURCE_UNKNOWN'}>{compactExecutiveSignal(r.sourceStatus || 'SOURCE_UNKNOWN')}</span></td>
              <td className={styles.proofCell}>{r.proofHash?.slice(0, 14) || 'UNSEALED'}</td>
              <td>
                <div className={styles.rowActions}>
                <button
                  onClick={() => {
                    setEditingItem(r);
                    setModalType('boardReport');
                    setShowModal(true);
                  }}
                  className={styles.iconButton}
                >
                  <Edit size={14} />
                </button>
                <button onClick={() => handleDelete(r.id, 'boardReport')} className={`${styles.iconButton} ${styles.dangerButton}`}>
                  <Trash2 size={14} />
                </button>
                </div>
              </td>
            </tr>
          ),
          'boardReports',
          boardReports.total
        );
      case 'investorUpdates':
        return renderTable(
          investorUpdates.items,
          ['Update', 'Date', 'Audience', 'Status', 'Source', 'Proof'],
          (u) => (
            <tr className={styles.tableRow}>
              <td><strong>{u.title}</strong></td>
              <td>{new Date(u.date).toLocaleDateString()}</td>
              <td>{u.audience}</td>
              <td><span className={`${styles.statusPill} ${styles[getExecutiveStatusTone(u.status)]}`}>{u.status}</span></td>
              <td><span className={styles.sourceChip} title={u.sourceStatus || 'SOURCE_UNKNOWN'}>{compactExecutiveSignal(u.sourceStatus || 'SOURCE_UNKNOWN')}</span></td>
              <td className={styles.proofCell}>{u.proofHash?.slice(0, 14) || 'UNSEALED'}</td>
              <td>
                <div className={styles.rowActions}>
                <button
                  onClick={() => {
                    setEditingItem(u);
                    setModalType('investorUpdate');
                    setShowModal(true);
                  }}
                  className={styles.iconButton}
                >
                  <Edit size={14} />
                </button>
                <button onClick={() => handleDelete(u.id, 'investorUpdate')} className={`${styles.iconButton} ${styles.dangerButton}`}>
                  <Trash2 size={14} />
                </button>
                </div>
              </td>
            </tr>
          ),
          'investorUpdates',
          investorUpdates.total
        );
      case 'strategicGoals':
        return renderTable(
          strategicGoals.items,
          ['Goal', 'Progress', 'Deadline', 'Status', 'Source', 'Proof'],
          (g) => (
            <tr className={styles.tableRow}>
              <td><strong>{g.title}</strong></td>
              <td>
                <div className={styles.progressCell}>
                  <div className={styles.progressTrack}>
                    <div
                      className={styles.progressFill}
                      style={{ width: `${g.progress}%` }}
                    />
                  </div>
                  <span>{g.progress}%</span>
                </div>
              </td>
              <td>{new Date(g.deadline).toLocaleDateString()}</td>
              <td>
                <span className={`${styles.statusPill} ${styles[getExecutiveStatusTone(g.status)]}`}>
                  {g.status}
                </span>
              </td>
              <td><span className={styles.sourceChip} title={g.sourceStatus || 'SOURCE_UNKNOWN'}>{compactExecutiveSignal(g.sourceStatus || 'SOURCE_UNKNOWN')}</span></td>
              <td className={styles.proofCell}>{g.proofHash?.slice(0, 14) || 'UNSEALED'}</td>
              <td>
                <div className={styles.rowActions}>
                <button
                  onClick={() => {
                    setEditingItem(g);
                    setModalType('strategicGoal');
                    setShowModal(true);
                  }}
                  className={styles.iconButton}
                >
                  <Edit size={14} />
                </button>
                <button onClick={() => handleDelete(g.id, 'strategicGoal')} className={`${styles.iconButton} ${styles.dangerButton}`}>
                  <Trash2 size={14} />
                </button>
                </div>
              </td>
            </tr>
          ),
          'strategicGoals',
          strategicGoals.total
        );
      default:
        return null;
    }
  };

  /**
   * @function renderModalFields
   * @description Renders mutation fields for the selected executive record type.
   * @returns {JSX.Element} Modal field grid.
   * @collaboration Keeps record creation functional for daily executive work instead of being a static demo shell.
   */
  const renderModalFields = () => {
    if (modalType === 'kpi') {
      return (
        <div className={styles.formGrid}>
          <label>
            <span>KPI Name</span>
            <input value={modalDraft.name || ''} onChange={event => setModalDraft(prev => ({ ...prev, name: event.target.value }))} />
          </label>
          <label>
            <span>Current Value</span>
            <input type="number" value={modalDraft.value ?? 0} onChange={event => setModalDraft(prev => ({ ...prev, value: Number(event.target.value) }))} />
          </label>
          <label>
            <span>Strategic Target</span>
            <input type="number" value={modalDraft.target ?? 1} onChange={event => setModalDraft(prev => ({ ...prev, target: Number(event.target.value) }))} />
          </label>
          <label>
            <span>Unit</span>
            <select value={modalDraft.unit || 'score'} onChange={event => setModalDraft(prev => ({ ...prev, unit: event.target.value }))}>
              <option value="ZAR">ZAR</option>
              <option value="USD">USD</option>
              <option value="%">Percent</option>
              <option value="score">Score</option>
              <option value="count">Count</option>
            </select>
          </label>
        </div>
      );
    }

    if (modalType === 'strategicGoal') {
      return (
        <div className={styles.formGrid}>
          <label className={styles.fieldWide}>
            <span>Strategic Objective</span>
            <input value={modalDraft.title || ''} onChange={event => setModalDraft(prev => ({ ...prev, title: event.target.value }))} />
          </label>
          <label>
            <span>Progress</span>
            <input type="number" min="0" max="100" value={modalDraft.progress ?? 0} onChange={event => setModalDraft(prev => ({ ...prev, progress: Number(event.target.value) }))} />
          </label>
          <label>
            <span>Deadline</span>
            <input type="date" value={modalDraft.deadline || todayIso()} onChange={event => setModalDraft(prev => ({ ...prev, deadline: event.target.value }))} />
          </label>
          <label>
            <span>Status</span>
            <select value={modalDraft.status || 'on_track'} onChange={event => setModalDraft(prev => ({ ...prev, status: event.target.value }))}>
              <option value="on_track">On track</option>
              <option value="at_risk">At risk</option>
              <option value="blocked">Blocked</option>
            </select>
          </label>
        </div>
      );
    }

    const titleLabel = modalType === 'boardReport' ? 'Report Title' : 'Update Headline';
    const ownerLabel = modalType === 'boardReport' ? 'Author Node' : 'Audience';
    const ownerKey = modalType === 'boardReport' ? 'author' : 'audience';
    return (
      <div className={styles.formGrid}>
        <label className={styles.fieldWide}>
          <span>{titleLabel}</span>
          <input value={modalDraft.title || ''} onChange={event => setModalDraft(prev => ({ ...prev, title: event.target.value }))} />
        </label>
        <label>
          <span>Date</span>
          <input type="date" value={modalDraft.date || todayIso()} onChange={event => setModalDraft(prev => ({ ...prev, date: event.target.value }))} />
        </label>
        <label>
          <span>{ownerLabel}</span>
          <input value={modalDraft[ownerKey] || ''} onChange={event => setModalDraft(prev => ({ ...prev, [ownerKey]: event.target.value }))} />
        </label>
        <label>
          <span>Status</span>
          <select value={modalDraft.status || 'draft'} onChange={event => setModalDraft(prev => ({ ...prev, status: event.target.value }))}>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="sealed">Sealed</option>
            <option value="sent">Sent</option>
          </select>
        </label>
      </div>
    );
  };

  const executiveWorkspaceOptions = [
    { id: 'overview', label: 'Overview', detail: 'Executive decision cockpit', icon: Briefcase, status: executiveReadiness.posture },
    { id: 'sources', label: 'Sources', detail: 'Tenant operating systems', icon: Database, status: `${operatingSourceCoverage.live}/${operatingSourceCoverage.total} live` },
    { id: 'playbook', label: 'Playbook', detail: executiveTransformation.phase?.target || 'ARR phase', icon: Building2, status: `${executiveTransformation.phaseProgress}%` },
    { id: 'workbench', label: 'Work', detail: 'Daily executive workbench', icon: ClipboardCheck, status: selectedWorkOrder ? compactExecutiveSignal(selectedWorkOrder.status) : 'READY' },
    { id: 'automation', label: 'AI', detail: 'Wilsy automation', icon: ShieldCheck, status: compactExecutiveSignal(wilsyAIEntitlements.status || wilsyAiPlan[0]?.readiness || 'PLAN_PENDING') },
    { id: 'finance', label: 'Finance', detail: 'Finance and FX intelligence', icon: PieChart, status: compactExecutiveSignal(sourceSnapshot.finance.status) },
    { id: 'ledger', label: 'Ledger', detail: TAB_TO_LABEL_MAP[activeTab] || 'KPI', icon: FileText, status: `${pageStates[activeTab].limit} rows` },
    { id: 'systems', label: 'Systems', detail: 'Vertical OS', icon: Route, status: 'Live gateways' },
    { id: 'diagnostics', label: 'Diagnostics', detail: 'Source truth', icon: Activity, status: compactExecutiveSignal(sourceSnapshot.telemetry.status) }
  ];
  const activeWorkspaceMeta = executiveWorkspaceOptions.find(workspace => workspace.id === activeWorkspace) || executiveWorkspaceOptions[0];
  const ActiveWorkspaceIcon = activeWorkspaceMeta.icon;

  useEffect(() => {
    /**
     * @function syncWilsyExecutiveThemeRuntime
     * @description Synchronizes ExecutiveDashboard with Account Command Center theme receipts.
     * @param {CustomEvent|StorageEvent} event - Theme change or storage event.
     * @returns {void}
     * @collaboration Makes operating skins repaint the live Executive cockpit immediately after Account saves them.
     */
    const syncWilsyExecutiveThemeRuntime = (event = {}) => {
      const stored = readWilsyExecutiveThemePreference();
      const detail = event?.detail || {};
      const nextThemeId = normalizeWilsyExecutiveThemeId(detail.themeId || stored.themeId);
      const nextMode = normalizeWilsyExecutiveMode(detail.mode || stored.mode);

      setAccountThemeId(nextThemeId);
      setAccountThemeMode(nextMode);
      applyWilsyExecutiveThemeToDocument(nextThemeId, nextMode);
    };

    syncWilsyExecutiveThemeRuntime();

    window.addEventListener('wilsy:theme-change', syncWilsyExecutiveThemeRuntime);
    window.addEventListener('storage', syncWilsyExecutiveThemeRuntime);

    return () => {
      window.removeEventListener('wilsy:theme-change', syncWilsyExecutiveThemeRuntime);
      window.removeEventListener('storage', syncWilsyExecutiveThemeRuntime);
    };
  }, []);

  const executiveCommandOptions = [
    { id: 'KPI_REBASE', label: 'KPI Rebase', detail: 'Refresh finance KPIs', icon: PieChart, targetWorkspace: 'finance' },
    { id: 'BOARD_PACKET', label: 'Seal Board Pack', detail: 'Prepare board pack', icon: FileText, targetWorkspace: 'ledger' },
    { id: 'INVESTOR_BRIEF', label: 'Investor Brief', detail: 'Create investor update', icon: Send, targetWorkspace: 'ledger' },
    { id: 'STRATEGIC_MANDATE', label: 'Mandate Goal', detail: 'Set executive mandate', icon: Target, targetWorkspace: 'ledger' },
    { id: 'WILSY_AI_LICENSE', label: 'Wilsy AI', detail: 'Configure Wilsy AI', icon: ShieldCheck, targetWorkspace: 'automation' },
    { id: 'TRANSFORMATION_PLAYBOOK', label: 'ARR Playbook', detail: executiveTransformation.phase?.target || 'Roadmap phase', icon: Building2, targetWorkspace: 'playbook' },
    { id: 'INTEGRATION_SPRINT', label: 'Integration Sprint', detail: executiveTransformation.integrationRows?.[0]?.label || 'Connector lane', icon: Database, targetWorkspace: 'sources' },
    { id: 'TRUST_PACKET', label: 'Trust Packet', detail: 'Review trust evidence', icon: ShieldCheck, targetWorkspace: 'playbook' }
  ];

  const sourceRegistryPanel = (
    <article className={styles.sourceRegistry}>
      <span><Database size={13} /> SOURCE_REGISTRY</span>
      <div>
        {sourceRows.map(source => (
          <div key={source.key}>
            <small>{source.live ? <CheckCircle size={11} /> : <AlertTriangle size={11} />} {source.key}</small>
            <strong data-live={source.live ? 'true' : 'false'} title={source.status}>
              {compactExecutiveSignal(source.status)}
            </strong>
          </div>
        ))}
      </div>
      {sourceRepairQueue.length > 0 && (
        <div className={styles.repairQueue}>
          <small>SOURCE_REPAIR_QUEUE</small>
          {sourceRepairQueue.slice(0, 4).map(action => (
            <button
              type="button"
              key={action.id}
              onClick={() => {
                setActiveWorkspace('ledger');
                requestSourceRepair(action);
              }}
              disabled={isRefreshing}
            >
              <AlertTriangle size={12} />
              <span>{action.title}</span>
            </button>
          ))}
        </div>
      )}
    </article>
  );

  /**
   * @function executiveCommandRail
   * @description Renders the fixed command launcher used by the selected executive workspace.
   * @returns {JSX.Element} Executive command rail.
   * @collaboration Replaces continuous scrolling command discovery with deliberate CEO command selection inside the OS viewport.
   */
  const executiveCommandRail = (
    <section className={styles.commandRail} aria-label="Executive command rail">
      {executiveCommandOptions.map(command => {
        const CommandIcon = command.icon;
        return (
          <button
            key={command.id}
            type="button"
            onClick={() => {
              setActiveWorkspace(command.targetWorkspace);
              executeExecutiveCommand(command.id);
            }}
          >
            <CommandIcon size={16} />
            <span>{command.label}</span>
            <small>{command.detail}</small>
          </button>
        );
      })}
    </section>
  );

  const executiveKpiStrip = (
    <section className={styles.kpiGrid}>
      <article>
        <span>REVENUE_YTD_COUNTER</span>
        <strong data-tone="green">{formatExecutiveKpiValue(financialKPIs.revenue, financialKPIs.currency || DEFAULT_OPERATING_CURRENCY)}</strong>
      </article>
      <article>
        <span>ANNUAL_RECURRING_ARR</span>
        <strong>{formatExecutiveKpiValue(financialKPIs.arr, financialKPIs.currency || DEFAULT_OPERATING_CURRENCY)}</strong>
      </article>
      <article>
        <span>PROFIT_MARGIN_EFFICIENCY</span>
        <strong>{formatExecutiveKpiValue(financialKPIs.profitMargin, '%')}</strong>
      </article>
      <article>
        <span>NET_PROMOTER_INDEX</span>
        <strong>{formatExecutiveKpiValue(financialKPIs.nps, 'score')}</strong>
      </article>
      <article>
        <span>EMPLOYEE_SAT_COEFFICIENT</span>
        <strong data-tone="green">{formatExecutiveKpiValue(financialKPIs.employeeSatisfaction, '%')}</strong>
      </article>
    </section>
  );

  /**
   * @function executiveLedgerTabs
   * @description Renders ledger mode tabs inside the focused executive workspace.
   * @returns {JSX.Element} Ledger tab controls.
   * @collaboration Keeps board, investor, KPI and goal records accessible without forcing Wilson through the full dashboard scroll stack.
   */
  const executiveLedgerTabs = (
    <nav className={styles.tabs} aria-label="Executive command workspace">
      {[
        { id: 'kpis', label: 'STRATEGIC KPIS', icon: <BarChart3 size={12} /> },
        { id: 'boardReports', label: 'BOARD REPORTS', icon: <FileText size={12} /> },
        { id: 'investorUpdates', label: 'INVESTOR UPDATES', icon: <Users size={12} /> },
        { id: 'strategicGoals', label: 'GOALS_PROJECTION', icon: <Target size={12} /> }
      ].map((tab) => (
        <button
          key={tab.id}
          onClick={() => {
            setActiveWorkspace('ledger');
            setActiveTab(tab.id);
            fetchTabData(tab.id, pageStates[tab.id]);
          }}
          className={activeTab === tab.id ? styles.tabActive : styles.tabButton}
        >
          {tab.icon} {tab.label}
        </button>
      ))}
    </nav>
  );

  const verticalSystemGateways = [
    {
      id: 'hr',
      label: 'People and HR',
      detail: 'Employees, recruitment, payroll, benefits, performance and time off.',
      command: 'EXEC_OPEN_HR_VERTICAL',
      route: '/hr',
      dashboardKey: 'hr',
      icon: Users,
      posture: 'Full vertical available'
    },
    {
      id: 'crm',
      label: 'CRM and Customers',
      detail: 'Clients, leads, accounts, deals, activities, documents and customer records.',
      command: 'EXEC_OPEN_CRM_VERTICAL',
      route: '/crm',
      dashboardKey: 'crm',
      icon: Building2,
      posture: 'Customer vertical available'
    },
    {
      id: 'billing',
      label: 'Billing Command',
      detail: 'Invoices, billing analytics, payments, subscriptions and revenue controls.',
      command: 'EXEC_OPEN_BILLING_VERTICAL',
      route: '/billing',
      dashboardKey: 'billing',
      icon: Database,
      posture: 'Billing system available'
    },
    {
      id: 'revenue-ledger',
      label: 'Revenue Ledger',
      detail: 'Sovereign revenue ledger, proof exports, invoice evidence and fiscal trail.',
      command: 'EXEC_OPEN_REVENUE_LEDGER',
      route: '/revenue-ledger',
      dashboardKey: 'revenue-ledger',
      icon: FileText,
      posture: 'Ledger vertical available'
    },
    {
      id: 'documents',
      label: 'Document Vault',
      detail: 'Document search, versions, audit, verification, sharing, watermarking and lock control.',
      command: 'EXEC_OPEN_DOCUMENT_VAULT',
      route: '/documents',
      dashboardKey: 'documents',
      icon: ClipboardCheck,
      posture: 'Document rails available'
    },
    {
      id: 'artifacts',
      label: 'Artifact Studio',
      detail: 'Board packs, NDAs, invoices, evidence packs, proof-sealed exports and templates.',
      command: 'EXEC_OPEN_ARTIFACT_STUDIO',
      route: '/artifacts',
      dashboardKey: 'artifacts',
      icon: Send,
      posture: 'Artifact engine available'
    },
    {
      id: 'legal',
      label: 'Legal and Compliance',
      detail: 'POPIA, forensic reports, legal workflows, compliance review and evidence.',
      command: 'EXEC_OPEN_LEGAL_VERTICAL',
      route: '/legal',
      dashboardKey: 'legal',
      icon: ShieldCheck,
      posture: 'Legal vertical available'
    },
    {
      id: 'client-portal',
      label: 'Client Portal',
      detail: 'Client documents, messages, invoices, matters, activity and portal records.',
      command: 'EXEC_OPEN_CLIENT_PORTAL',
      route: '/client-portal',
      dashboardKey: 'client-portal',
      icon: Route,
      posture: 'Client portal available'
    }
  ];


  const workspaceContent = {
    overview: (
      <div className={styles.overviewWorkspace}>
        <section className={styles.commandDeck}>
          <article className={styles.finalityPanel}>
            <div className={styles.finalityHeader}>
              <div>
                <span>
                  <ShieldCheck size={13} /> Executive Readiness
                </span>
                <strong>
                  {executiveReadiness.score}% // {executiveReadiness.posture}
                </strong>
              </div>
              <div>
                <span>LIVE_SOURCE_COVERAGE</span>
                <strong>{executiveReadiness.liveSources}/{executiveReadiness.totalSources}</strong>
              </div>
            </div>
            <div className={styles.sourceMatrix}>
              <div>
                <span>FINANCE_TRUTH_SOURCE</span>
                <strong title={sourceSnapshot.finance.status}>{compactExecutiveSignal(sourceSnapshot.finance.status)}</strong>
                <small>{sourceSnapshot.finance.proofHash?.slice(0, 18) || 'PROOF_PENDING'}</small>
              </div>
              <div>
                <span>TELEMETRY_STREAM</span>
                <strong title={sourceSnapshot.telemetry.status}>{compactExecutiveSignal(sourceSnapshot.telemetry.status)}</strong>
                <small>{sourceSnapshot.telemetry.lastSync || 'SYNC_PENDING'}</small>
              </div>
              <div>
                <span>SHARD_PAGINATION</span>
                <strong>{pageStates[activeTab].limit} ROW WINDOWS</strong>
                <small>{sourceSnapshot.records.proofHash?.slice(0, 18) || 'PROOF_PENDING'}</small>
              </div>
            </div>
          </article>

          <article className={styles.memoPanel}>
            <span><ClipboardCheck size={13} /> Decision Memo</span>
            <h2>{executiveMemo.nextAction}</h2>
            {executiveMemo.dutyReason && <p>{executiveMemo.dutyReason}</p>}
            <div className={styles.memoGrid}>
              <div>
                <small>ARR</small>
                <strong>{formatExecutiveMoney(executiveMemo.arr)}</strong>
              </div>
              <div>
                <small>Revenue</small>
                <strong>{formatExecutiveMoney(executiveMemo.revenue)}</strong>
              </div>
              <div>
                <small>Industry</small>
                <strong>{executiveMemo.industry}</strong>
              </div>
            </div>
            <p>MEMO_PROOF // {executiveMemo.proofHash.slice(0, 28)}</p>
          </article>
        </section>
        {executiveCommandRail}
      </div>
    ),
    sources: (
      <div className={styles.sourcesWorkspace}>
        <section className={styles.operatingSourceDeck}>
          <header>
            <div>
              <span><Database size={13} /> CEO_OPERATING_SOURCE_FABRIC</span>
              <h2>HR, CRM, revenue, product and risk rails</h2>
            </div>
            <small>{operatingSourceCoverage.live}/{operatingSourceCoverage.total} LIVE</small>
          </header>
          <div className={styles.operatingSourceGrid}>
            {operatingSources.map(source => (
              <article key={source.key} data-live={source.live ? 'true' : 'false'}>
                <small>{source.lane} // {source.count === null ? 'SOURCE_REQUIRED' : `${source.count} ROWS`}</small>
                <strong>{source.label}</strong>
                <span title={source.status}>{compactExecutiveSignal(source.status)}</span>
                <button
                  type="button"
                  className={styles.inlineAction}
                  onClick={() => executeFunctionCard({
                    key: source.functionKey,
                    label: source.label,
                    status: source.live ? 'ENABLED' : 'RECOMMENDED',
                    sourceStatus: source.status
                  })}
                  disabled={isRefreshing}
                >
                  <Route size={12} /> Open Rail
                </button>
              </article>
            ))}
          </div>
        </section>
        {sourceRegistryPanel}
      </div>
    ),
    playbook: (
      <section className={styles.transformationGrid}>
        <article className={styles.transformationHero}>
          <header>
            <div>
              <span><Building2 size={13} /> ARR_TRANSFORMATION_PLAYBOOK</span>
              <h2>{executiveTransformation.phase?.label}</h2>
            </div>
            <small>{executiveTransformation.phase?.months} // {executiveTransformation.phase?.target}</small>
          </header>
          <div className={styles.phaseMeter}>
            <div>
              <strong>{executiveTransformation.phaseProgress}%</strong>
              <span>PHASE_PROGRESS</span>
            </div>
            <div className={styles.phaseTrack}>
              <i style={{ width: `${executiveTransformation.phaseProgress}%` }} />
            </div>
          </div>
          <p>{executiveTransformation.phase?.mandate}</p>
          <div className={styles.transformationStats}>
            <div>
              <small>ARR</small>
              <strong>{formatExecutiveMoney(executiveTransformation.arr, executiveTransformation.currency)}</strong>
            </div>
            <div>
              <small>REVENUE</small>
              <strong>{formatExecutiveMoney(executiveTransformation.revenue, executiveTransformation.currency)}</strong>
            </div>
            <div>
              <small>READINESS</small>
              <strong>{executiveTransformation.readinessScore}%</strong>
            </div>
            <div>
              <small>PLAYBOOK_PROOF</small>
              <strong>{executiveTransformation.proofHash?.slice(0, 18)}</strong>
            </div>
          </div>
          <div className={styles.priorityStack}>
            {executiveTransformation.priorityActions.slice(0, 5).map(action => (
              <article key={action.id} data-status={action.status}>
                <small>{action.priority} // {action.lane}</small>
                <strong>{action.title}</strong>
                <span title={action.proofHash}>{compactExecutiveSignal(action.status)}</span>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.integrationPanel}>
          <header>
            <div>
              <span><Database size={13} /> INTEGRATION_MARKETPLACE_READINESS</span>
              <h2>Finance, CRM, alerts and identity rails</h2>
            </div>
            <small>{executiveTransformation.integrationRows.filter(row => row.status === 'READY_TO_CONNECT').length} READY</small>
          </header>
          <div className={styles.connectorGrid}>
            {executiveTransformation.integrationRows.slice(0, 8).map(connector => (
              <article key={connector.key} data-status={connector.status}>
                <small>{connector.lane} // {compactExecutiveSignal(connector.sourceStatus)}</small>
                <strong>{connector.label}</strong>
                <span>{connector.value}</span>
                <em title={connector.proofHash}>{compactExecutiveSignal(connector.status)}</em>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.trustPanel}>
          <header>
            <div>
              <span><ShieldCheck size={13} /> ENTERPRISE_TRUST_STACK</span>
              <h2>SOC2, POPIA, audit export and RBAC</h2>
            </div>
            <small>{executiveTransformation.trustRows.filter(row => ['EVIDENCE_READY', 'EXPORT_READY', 'RBAC_ACTIVE'].includes(row.status)).length} SEALED</small>
          </header>
          <div className={styles.trustRows}>
            {executiveTransformation.trustRows.map(row => (
              <article key={row.key} data-status={row.status}>
                <div>
                  <small>{row.lane} // SCORE {row.score}</small>
                  <strong>{row.label}</strong>
                </div>
                <span title={row.sourceStatus}>{compactExecutiveSignal(row.status)}</span>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.moatPanel}>
          <header>
            <div>
              <span><Target size={13} /> COMPETITIVE_KILL_MATRIX</span>
              <h2>Market counter-positioning</h2>
            </div>
            <small>{executiveTransformation.moatRows.filter(row => row.status === 'MOAT_LIVE').length} LIVE MOATS</small>
          </header>
          <div className={styles.moatRows}>
            {executiveTransformation.moatRows.map(row => (
              <article key={row.key} data-status={row.status}>
                <small>{row.label} // {compactExecutiveSignal(row.status)}</small>
                <strong>{row.wilsyMove}</strong>
                <p>{row.competitorSignal}</p>
              </article>
            ))}
          </div>
        </article>
      </section>
    ),
    automation: (
      <div className={styles.automationWorkspace}>
        <article className={styles.intelligencePanel}>
          <header>
            <div>
              <span><PieChart size={13} /> AI_POWERED_EXECUTIVE_INTELLIGENCE</span>
              <h2>Forecast, anomaly and board signals</h2>
            </div>
            <small>{executiveTransformation.insightRows.length} INSIGHT LANES</small>
          </header>
          <div className={styles.insightList}>
            {executiveTransformation.insightRows.map(insight => (
              <article key={insight.id} data-status={insight.status}>
                <div>
                  <small>{insight.lane} // {insight.confidence}%</small>
                  <strong>{insight.title}</strong>
                  <p>{insight.signal}</p>
                </div>
                <span title={insight.proofHash}>{compactExecutiveSignal(insight.status)}</span>
              </article>
            ))}
          </div>
          <form className={styles.nlqBox} onSubmit={askExecutiveOS}>
            <label>
              <Search size={13} />
              <input
                value={executiveQuestion}
                onChange={event => setExecutiveQuestion(event.target.value)}
                placeholder="ASK_REVENUE_SOURCE_BOARD_COMPLIANCE"
              />
            </label>
            <button type="submit" className={styles.primaryButton} disabled={isRefreshing || !executiveQuestion.trim()}>
              ASK
            </button>
          </form>
          {executiveAnswer && (
            <div className={styles.nlqAnswer}>
              <small>{executiveAnswer.intent} // {executiveAnswer.proofHash.slice(0, 18)}</small>
              <strong>{executiveAnswer.answer}</strong>
              <div>
                {executiveAnswer.evidenceRows.slice(0, 4).map(row => (
                  <span key={row}>{row}</span>
                ))}
              </div>
            </div>
          )}
        </article>

        <article className={styles.aiPanel}>
          <header>
            <div>
              <span><ShieldCheck size={13} /> WILSY_AI_LICENSE_LADDER</span>
              <h2>Tenant Automation Add-ons</h2>
            </div>
            <small title={wilsyAIEntitlements.status || wilsyAiPlan[0]?.readiness || 'PLAN_PENDING'}>
              {compactExecutiveSignal(wilsyAIEntitlements.status || wilsyAiPlan[0]?.readiness || 'PLAN_PENDING')}
            </small>
          </header>
          <div className={styles.aiList}>
            {wilsyAiPlan.map(plan => (
              <article key={plan.id} className={styles.aiCard} data-readiness={plan.readiness}>
                <span>{plan.tier} // {plan.licenseStatus || 'UNLICENSED'}</span>
                <h3>{plan.name}</h3>
                <p>{plan.differentiator || plan.valuePromise || plan.reason}</p>
                <div className={styles.aiEconomics}>
                  <div>
                    <small>MONTHLY</small>
                    <strong>{formatOperatingMoney(plan.monthlyPriceZar ?? plan.monthlyPrice ?? null, 'ZAR')}</strong>
                  </div>
                  <div>
                    <small>DAILY REQUESTS</small>
                    <strong>
                      {formatExecutiveUsageValue(plan.usageAnalytics?.daily?.requestUnits)}
                      /{formatExecutiveUsageValue(plan.dailyRequestLimit)}
                    </strong>
                  </div>
                  <div>
                    <small>MONTH VALUE</small>
                    <strong>{formatOperatingMoney(plan.usageAnalytics?.monthly?.estimatedValueZar ?? null, 'ZAR')}</strong>
                  </div>
                </div>
                <small title={plan.sourceStatus}>
                  {plan.tenantFit} // {compactExecutiveSignal(plan.sourceStatus)} // {compactExecutiveSignal(plan.usageAnalytics?.quotaStatus || 'USAGE_SOURCE_REQUIRED')}
                </small>
                <div className={styles.aiActions}>
                  <button
                    type="button"
                    className={styles.primaryButton}
                    onClick={() => activateWilsyAiUseCase(plan)}
                    disabled={isRefreshing || plan.readiness === 'ACCESS_DENIED' || plan.licenseStatus === 'ACTIVE'}
                  >
                    {plan.licenseStatus === 'ACTIVE' ? 'ACTIVE' : 'LICENSE'}
                  </button>
                  <button
                    type="button"
                    className={styles.secondaryButton}
                    onClick={() => logWilsyAiRequest(plan)}
                    disabled={isRefreshing || plan.licenseStatus !== 'ACTIVE'}
                  >
                    LOG REQUEST
                  </button>
                </div>
              </article>
            ))}
            {wilsyAiPlan.length === 0 && (
              <div className={styles.emptyStream}>WILSY_AI_PLAN_REQUIRES_TENANT_PROFILE...</div>
            )}
          </div>
        </article>
      </div>
    ),
    workbench: (
      <section className={styles.operatingGrid}>
        <article className={styles.dailyDutyPanel}>
          <header>
            <div>
              <span><ClipboardCheck size={13} /> DAILY_EXECUTIVE_WORKBENCH</span>
              <h2>{executiveOperatingSystem.profile.name}</h2>
            </div>
            <small title={executiveOperatingSystem.profile.sourceStatus}>{compactExecutiveSignal(executiveOperatingSystem.profile.sourceStatus)}</small>
          </header>
          <div className={styles.profileStrip}>
            <div>
              <small>Business Model</small>
              <strong>{executiveOperatingSystem.profile.industryLabel}</strong>
            </div>
            <div>
              <small>MODEL_SELECTOR</small>
              <label className={styles.modelSelector}>
                <select
                  value={businessModelOverride || ''}
                  onChange={event => updateBusinessModelOverride(event.target.value)}
                >
                  <option value="">Tenant auto-detect</option>
                  {executiveOperatingSystem.businessModels.map(model => (
                    <option key={model.key} value={model.key}>{model.label}</option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className={styles.inlineAction}
                onClick={persistBusinessModelCommand}
                disabled={isRefreshing}
              >
                <Settings size={12} /> Persist Model
              </button>
            </div>
            <div>
              <small>BUSINESS_FAMILY</small>
              <strong>{executiveOperatingSystem.profile.naicsFamily || 'General operating model'}</strong>
            </div>
            <div>
              <small>CONFIDENCE</small>
              <strong>{Math.round((executiveOperatingSystem.profile.confidence || 0) * 100)}% // {compactExecutiveSignal(executiveOperatingSystem.profile.sourceStatus)}</strong>
            </div>
            <div>
              <small>PROFILE_EVIDENCE</small>
              <strong>{executiveOperatingSystem.profile.sourceEvidence}</strong>
            </div>
          </div>
          <div className={styles.functionMatrix}>
            {executiveOperatingSystem.functionMatrix.map(item => (
              <article key={item.key} data-status={item.status}>
                <div>
                  <small>{item.label}</small>
                  <strong>{compactExecutiveSignal(item.status)}</strong>
                </div>
                <button
                  type="button"
                  className={isFunctionExecutable(item) ? styles.iconButton : `${styles.iconButton} ${styles.dangerButton}`}
                  onClick={() => executeFunctionCard(item)}
                  title={isFunctionExecutable(item) ? `Open ${item.label}` : `Request access to ${item.label}`}
                  disabled={isRefreshing}
                >
                  {isFunctionExecutable(item) ? <Route size={13} /> : <Lock size={13} />}
                </button>
              </article>
            ))}
          </div>
          <div className={styles.workOrderPanel}>
            <header>
              <div>
                <span><PlayCircle size={13} /> EXECUTIVE_WORK_ORDER</span>
                <h2>{selectedWorkOrder?.title || 'No accepted work order yet'}</h2>
              </div>
              <small>{selectedWorkOrder ? compactExecutiveSignal(selectedWorkOrder.status) : 'AWAITING_DUTY_ACCEPTANCE'}</small>
            </header>
            {selectedWorkOrder ? (
              <div className={styles.workOrderBody}>
                <div className={styles.workOrderMeta}>
                  <div>
                    <small>MODULE</small>
                    <strong>{selectedWorkOrder.functionKey}</strong>
                  </div>
                  <div>
                    <small>ROUTE</small>
                    <strong>{selectedWorkOrder.route?.route || '/executive'}</strong>
                  </div>
                  <div>
                    <small>PROOF</small>
                    <strong>{selectedWorkOrder.proofHash?.slice(0, 18)}</strong>
                  </div>
                </div>
                <ol className={styles.workSteps}>
                  {(selectedWorkOrder.workflowSteps || []).map(step => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
                {selectedWorkOrder.blockedReason && <p className={styles.blockedReason}>{selectedWorkOrder.blockedReason}</p>}
                <div className={styles.workOrderActions}>
                  <button
                    type="button"
                    className={styles.primaryButton}
                    onClick={() => runExecutiveWorkOrder(selectedWorkOrder)}
                    disabled={isRefreshing}
                  >
                    {selectedWorkOrder.blocked ? 'REVIEW GATES' : 'RUN WORK ORDER'}
                  </button>
                  <select
                    value={selectedWorkOrder.workOrderId}
                    onChange={event => setSelectedWorkOrderId(event.target.value)}
                  >
                    {executiveWorkOrders.map(order => (
                      <option key={order.workOrderId} value={order.workOrderId}>{order.title}</option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              <div className={styles.emptyStream}>ACCEPT_A_DAILY_DUTY_TO_CREATE_A_WORK_ORDER...</div>
            )}
          </div>
          <div className={styles.dutyList}>
            {executiveOperatingSystem.dailyDuties.map(duty => (
              <article key={duty.key} className={styles.dutyCard} data-status={duty.status} data-impact={duty.impact}>
                <div>
                  <span>{duty.lane} // {duty.cadence}</span>
                  <h3>{duty.title}</h3>
                  <p>{duty.reason}</p>
                  <div className={styles.evidenceRail}>
                    {(duty.evidenceRequired || []).slice(0, 4).map(evidence => (
                      <i key={evidence}>{evidence}</i>
                    ))}
                  </div>
                  {duty.blockedReason && <p className={styles.blockedReason}>{duty.blockedReason}</p>}
                  <small title={duty.sourceStatus}>{compactExecutiveSignal(duty.sourceStatus)} // IMPACT {duty.impact}</small>
                </div>
                <button
                  type="button"
                  className={styles.secondaryButton}
                  onClick={() => acceptDailyDuty(duty)}
                  disabled={isRefreshing}
                >
                  {duty.commandLabel || 'ACCEPT'}
                </button>
              </article>
            ))}
          </div>
        </article>
        {sourceRegistryPanel}
      </section>
    ),
    finance: (
      <div className={styles.financeWorkspace}>
        {executiveKpiStrip}
        <section className={styles.currencyPanel}>
          <header>
            <div>
              <span>ZA_CURRENCY_INTELLIGENCE</span>
              <h2>ZAR Operating Lens</h2>
            </div>
            <small title={currencyWorkbench.sourceStatus}>{compactExecutiveSignal(currencyWorkbench.sourceStatus)}</small>
          </header>
          <div className={styles.fxWorkbench}>
            <div className={styles.fxControls}>
              <label>
                <span>Amount</span>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={currencyWorkbench.amount}
                  onChange={event => setCurrencyWorkbench(prev => ({ ...prev, amount: event.target.value }))}
                />
              </label>
              <label>
                <span>From</span>
                <select
                  value={currencyWorkbench.fromCurrency}
                  onChange={event => setCurrencyWorkbench(prev => ({ ...prev, fromCurrency: event.target.value }))}
                >
                  {EXECUTIVE_CURRENCIES.map(currency => <option key={currency} value={currency}>{currency}</option>)}
                </select>
              </label>
              <label>
                <span>To</span>
                <select
                  value={currencyWorkbench.toCurrency}
                  onChange={event => setCurrencyWorkbench(prev => ({ ...prev, toCurrency: event.target.value }))}
                >
                  {EXECUTIVE_CURRENCIES.map(currency => <option key={currency} value={currency}>{currency}</option>)}
                </select>
              </label>
              <button type="button" className={styles.primaryButton} onClick={runCurrencyConversion} disabled={isRefreshing}>
                CONVERT
              </button>
            </div>
            <div className={styles.fxResult}>
              <span>CONVERSION_RECEIPT</span>
              <strong>
                {currencyWorkbench.conversion?.display?.converted || 'FX_SOURCE_REQUIRED'}
              </strong>
              <small>
                {currencyWorkbench.conversion?.display?.source || formatOperatingMoney(currencyWorkbench.amount, currencyWorkbench.fromCurrency)}
                {' '} // RATE {currencyWorkbench.conversion?.rate || 'SOURCE_REQUIRED'}
              </small>
              <p>
                {currencyWorkbench.conversion?.sarbReview?.status || 'SARB_INTERNAL_REVIEW_PENDING'} // PROOF{' '}
                {(currencyWorkbench.conversion?.proofHash || currencyWorkbench.proofHash || 'PENDING').slice(0, 22)}
              </p>
            </div>
            <div className={styles.fxRates}>
              {currencyWorkbench.watchlist.length === 0 ? (
                <div className={styles.emptyStream}>FX_WATCHLIST_SOURCE_REQUIRED...</div>
              ) : currencyWorkbench.watchlist.map(rate => (
                <article key={`${rate.baseCurrency}-${rate.quoteCurrency}`}>
                  <small>{rate.baseCurrency}/{rate.quoteCurrency}</small>
                  <strong>{rate.rate || 'SOURCE_REQUIRED'}</strong>
                  <span title={rate.sourceStatus}>{compactExecutiveSignal(rate.sourceStatus)}</span>
                </article>
              ))}
            </div>
          </div>
        </section>
      </div>
    ),
    ledger: (
      <div className={styles.ledgerWorkspace}>
        {executiveLedgerTabs}
        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <span>EXECUTIVE_LEDGER</span>
              <h2>{TAB_TO_LABEL_MAP[activeTab] || 'KPI'} GOVERNANCE</h2>
            </div>
            <small title={sourceSnapshot.records.status}>{pageStates[activeTab].limit} row shard // {compactExecutiveSignal(sourceSnapshot.records.status)}</small>
          </div>
          {renderContent()}
        </section>
      </div>
    ),
    systems: (
      <div className={styles.integrationWorkspace}>
        <section className={styles.integrationPanel}>
          <header>
            <span>Vertical OS</span>
            <h2>Wilsy OS System Gateways</h2>
            <p>
              ExecutiveDashboard is the CEO cockpit. Each card opens a real vertical system instead of compressing
              HR, CRM, billing, documents and legal operations into one crowded view.
            </p>
          </header>

          <div className={styles.connectorGrid}>
            {verticalSystemGateways.map(system => {
              const SystemIcon = system.icon;
              return (
                <article key={system.id}>
                  <div>
                    <SystemIcon size={18} />
                    <span>{system.posture}</span>
                  </div>
                  <h3>{system.label}</h3>
                  <p>{system.detail}</p>
                  <button
                    type="button"
                    className={styles.inlineAction}
                    onClick={() => executeVerticalSystemRoute(system)}
                  >
                    Open System
                  </button>
                </article>
              );
            })}
          </div>
        </section>

        <section className={styles.trustPanel}>
          <header>
            <span>Operating Doctrine</span>
            <h2>CEO gateway, not a table dump</h2>
          </header>
          <div className={styles.trustRows}>
            <article>
              <strong>HR</strong>
              <span>Employee detail belongs in the HR vertical; Executive gets workforce signal and route access.</span>
            </article>
            <article>
              <strong>CRM</strong>
              <span>Client detail belongs in CRM; Executive gets pipeline signal and customer-risk commands.</span>
            </article>
            <article>
              <strong>Documents</strong>
              <span>Generated artifacts and vault records stay connected to proof, audit and source posture.</span>
            </article>
            <article>
              <strong>Billing</strong>
              <span>Invoices, payments and revenue proof stay governed by billing and ledger rails.</span>
            </article>
          </div>
        </section>
      </div>
    ),

    diagnostics: (
      <div className={styles.ledgerWorkspace}>
        {sourceRegistryPanel}
        <section className={styles.telemetryPanel}>
          <header>
            <h3><Activity size={13} /> EXECUTIVE_TELEMETRY_STREAM</h3>
            <span title={sourceSnapshot.telemetry.status}>{telemetrySyncing ? 'SYNCING' : compactExecutiveSignal(sourceSnapshot.telemetry.status)}</span>
          </header>
          <div>
            {executiveActivities.length === 0 && (
              <div className={styles.emptyStream}>EXEC_STREAM_VACANT_AWAITING_MUTATIONS...</div>
            )}
            {executiveActivities.map((act, idx) => (
              <article key={act.id || idx}>
                {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : 'EXEC_NOW'} //{' '}
                {act.eventType} // {act.event || 'COMMITTED'} // {act.message || 'TRANSACTION_LOG_COMMITTED'} // PROOF{' '}
                {act.proofHash?.slice(0, 16) || 'PENDING'}
              </article>
            ))}
          </div>
        </section>
      </div>
    )
  };

  /**
   * @function executiveIdentity
   * @description Memoizes top-rail operator and business OS story copy.
   * @returns {Object} Executive identity packet.
   * @collaboration Keeps the visible top rail grounded in tenant/user/business context rather than debug identifiers.
   */
  const executiveIdentity = buildExecutiveOperatorIdentity({
    user,
    activeTenant,
    tenantBranding,
    executiveOperatingSystem,
    executiveReadiness,
    sourceSnapshot,
    role,
    access
  });

  if (loading || access.isLoading) {
    return (
      <div className={styles.loading}>
        <RefreshCw size={20} className={styles.spin} />
        <span>Loading Executive Suite</span>
      </div>
    );
  }

  if (!accessDecision.allowed) {
    return (
      <div className={styles.accessDenied}>
        <div>
          <AlertTriangle size={28} />
          <span>EXECUTIVE ACCESS DENIED</span>
          <h1>{accessDecision.reason}</h1>
          <p>{accessDecision.required}</p>
          <small>
            CHANNEL // {accessDecision.channel} // ROLE {access.userRole || 'unknown'} // TENANT {tenantId}
          </small>
        </div>
      </div>
    );
  }

  return (
    <div
      className={styles.executiveShell}
      data-refreshing={isRefreshing ? 'true' : 'false'}
      style={{ ...(tenantBranding.cssVars || {}), ...executiveThemeVars }}
      data-wilsy-theme={accountThemeId}
      data-wilsy-mode={accountThemeMode}
      data-wilsy-resolved-mode={resolveWilsyExecutiveMode(accountThemeMode)}
    >
      {isFounderReturnEligible && (
        <button
          type="button"
          data-wilsy-founder-return="true"
          onClick={handleFounderReturn}
          style={{
            position: 'fixed',
            left: 24,
            top: 78,
            zIndex: 2200,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 10,
            minHeight: 42,
            padding: '0 16px',
            borderRadius: 999,
            border: '1px solid var(--wilsy-border-authority, rgba(212,175,55,0.5))',
            color: 'var(--wilsy-text, #fffaf0)',
            background: 'rgba(2, 3, 6, 0.72)',
            backdropFilter: 'blur(14px)',
            boxShadow: '0 18px 48px rgba(0,0,0,0.28)',
            fontFamily: 'monospace',
            fontSize: 11,
            fontWeight: 900,
            letterSpacing: '0.08em',
            cursor: 'pointer'
          }}
          title="Return to Founder Dashboard"
        >
          <span aria-hidden="true">←</span>
          Founder Dashboard
        </button>
      )}
      <header className={styles.osTopRail}>
        <div className={styles.osTitleBlock}>
          <span className={styles.eyebrow}><Briefcase size={14} /> {executiveIdentity.commandLabel}</span>
          <h1>WILSY OS EXECUTIVE COMMAND CENTER</h1>
          <div className={styles.operatingStoryRail} aria-label="Wilsy OS executive operating story">
            <span>{executiveIdentity.storyMessages.join('     •     ')}</span>
          </div>
        </div>
        <div className={styles.brandPlate}>
          <div className={styles.tenantMark}>
            {tenantBranding.logo ? (
              <img src={tenantBranding.logo} alt={`${tenantBranding.displayName} mark`} />
            ) : (
              <span>{tenantBranding.initials}</span>
            )}
          </div>
          <div>
            <small>{executiveIdentity.tenantEyebrow}</small>
            <strong>{executiveIdentity.tenantName}</strong>
            <em>{executiveIdentity.tenantStory}</em>
          </div>
        </div>
        <div className={styles.toolbar}>
          <div className={styles.operatorIdentityCard} title={executiveIdentity.email || executiveIdentity.displayName}>
            <UserCog size={14} />
            <div>
              <strong>{executiveIdentity.displayName}</strong>
              <small>{executiveIdentity.roleLabel}</small>
            </div>
          </div>
          <label className={styles.searchBox}>
            <Search size={13} />
            <input
              value={searchTerm}
              onChange={event => setSearchTerm(event.target.value)}
              placeholder="Search Wilsy OS or press ⌘K" onFocus={() => window.dispatchEvent(new CustomEvent('wilsy:open-command-search'))}
            />
          </label>
          <button
            onClick={() => setIsAccountCommandCenterOpen(true)}
            className={styles.secondaryButton}
            title="Open Wilsy Account Command Center"
          >
            <UserCog size={13} /> COMMAND CENTER
          </button>
          <button
            onClick={loadAllData}
            disabled={isRefreshing}
            className={styles.secondaryButton}
          >
            <RefreshCw size={13} className={isRefreshing ? styles.spin : ''} /> LIVE SYNC
          </button>
          <button
            onClick={() => {
              setEditingItem(null);
              setModalType(TAB_TO_MODAL_MAP[activeTab] || 'kpi');
              setShowModal(true);
            }}
            className={styles.primaryButton}
          >
            <Plus size={13} /> NEW COMMAND
          </button>
        </div>
      </header>

      <section className={styles.workspaceFrame}>
        <nav className={styles.workspaceRail} aria-label="Executive operating workspaces">
          <label className={styles.workspaceSelect}>
            <span>WORKSPACE</span>
            <select value={activeWorkspace} onChange={event => setActiveWorkspace(event.target.value)}>
              {executiveWorkspaceOptions.map(workspace => (
                <option key={workspace.id} value={workspace.id}>{workspace.label}</option>
              ))}
            </select>
          </label>
          <div className={styles.workspaceButtons}>
            {executiveWorkspaceOptions.map(workspace => {
              const WorkspaceIcon = workspace.icon;
              return (
                <button
                  key={workspace.id}
                  type="button"
                  className={activeWorkspace === workspace.id ? styles.workspaceButtonActive : styles.workspaceButton}
                  onClick={() => setActiveWorkspace(workspace.id)}
                >
                  <WorkspaceIcon size={15} />
                  <span>{workspace.label}</span>
                  <small>{workspace.detail}</small>
                </button>
              );
            })}
          </div>
        </nav>

        <main className={styles.workspaceViewport}>
          <div className={styles.workspaceHeader}>
            <div>
              <span><ActiveWorkspaceIcon size={13} /> Workspace</span>
              <h2>{activeWorkspaceMeta.label}</h2>
              <p>{activeWorkspaceMeta.detail} // {compactExecutiveSignal(activeWorkspaceMeta.status)}</p>
            </div>
            <div className={styles.workspaceMetrics}>
              <div>
                <small>READINESS</small>
                <strong>{executiveReadiness.score}%</strong>
              </div>
              <div>
                <small>SOURCES</small>
                <strong>{executiveReadiness.liveSources}/{executiveReadiness.totalSources}</strong>
              </div>
              <div>
                <small>ARR</small>
                <strong>{formatExecutiveMoney(executiveMemo.arr)}</strong>
              </div>
            </div>
          </div>
          <div className={styles.workspaceContent}>
            {workspaceContent[activeWorkspace] || workspaceContent.overview}
          </div>
        </main>
          <aside className={styles.contextRail} aria-label="Executive business artifact controls">
            <header>
              <span><Settings size={13} /> Business Command</span>
              <strong>{compactExecutiveSignal(activeWorkspaceMeta.status)}</strong>
            </header>

            <label>
              <span>Run Command</span>
              <select
                value=""
                onChange={event => {
                  const command = executiveCommandOptions.find(item => item.id === event.target.value);
                  if (!command) return;
                  setActiveWorkspace(command.targetWorkspace);
                  executeExecutiveCommand(command.id);
                }}
              >
                <option value="">Select command</option>
                {executiveCommandOptions.map(command => (
                  <option key={command.id} value={command.id}>{command.label}</option>
                ))}
              </select>
            </label>

            <label>
              <span>Ledger View</span>
              <select
                value={activeTab}
                onChange={event => {
                  setActiveWorkspace('ledger');
                  setActiveTab(event.target.value);
                  fetchTabData(event.target.value, pageStates[event.target.value]);
                }}
              >
                <option value="kpis">Strategic KPIs</option>
                <option value="boardReports">Board Reports</option>
                <option value="investorUpdates">Investor Updates</option>
                <option value="strategicGoals">Goals Projection</option>
              </select>
            </label>

            <button
              type="button"
              className={styles.primaryButton}
              onClick={() => {
                const gateway = verticalSystemGateways.find(system => system.id === 'artifacts');
                window.dispatchEvent(new CustomEvent('wilsy:artifact-command', {
                  detail: {
                    openCatalog: true,
                    tenantId,
                    source: 'ExecutiveDashboard'
                  }
                }));
                if (gateway) executeVerticalSystemRoute(gateway);
              }}
              disabled={isRefreshing}
            >
              <Download size={13} /> BUSINESS ARTIFACTS
            </button>

            <section className={styles.businessArtifactRail} aria-label="Business artifact launcher">
              <header>
                <strong>Business Artifact Studio</strong>
                <small>Select the document the business needs. Wilsy OS routes it to the artifact engine.</small>
              </header>

              <div className={styles.artifactCommandStack}>
                <button
                  type="button"
                  onClick={() => {
                    const gateway = verticalSystemGateways.find(system => system.id === 'artifacts');
                    window.dispatchEvent(new CustomEvent('wilsy:artifact-command', {
                      detail: { type: 'boardPack', tenantId, source: 'ExecutiveDashboard' }
                    }));
                    if (gateway) executeVerticalSystemRoute(gateway);
                  }}
                >
                  <FileText size={15} />
                  <span>
                    <strong>Board Pack</strong>
                    <small>Investor and executive pack</small>
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    const gateway = verticalSystemGateways.find(system => system.id === 'artifacts');
                    window.dispatchEvent(new CustomEvent('wilsy:artifact-command', {
                      detail: { type: 'NDAA-ENTERPRISE', tenantId, source: 'ExecutiveDashboard' }
                    }));
                    if (gateway) executeVerticalSystemRoute(gateway);
                  }}
                >
                  <ShieldCheck size={15} />
                  <span>
                    <strong>NDA</strong>
                    <small>Confidentiality agreement</small>
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    const gateway = verticalSystemGateways.find(system => system.id === 'artifacts');
                    window.dispatchEvent(new CustomEvent('wilsy:artifact-command', {
                      detail: { type: 'invoice', tenantId, source: 'ExecutiveDashboard' }
                    }));
                    if (gateway) executeVerticalSystemRoute(gateway);
                  }}
                >
                  <Database size={15} />
                  <span>
                    <strong>Invoice</strong>
                    <small>Branded billing document</small>
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    const gateway = verticalSystemGateways.find(system => system.id === 'documents');
                    if (gateway) executeVerticalSystemRoute(gateway);
                  }}
                >
                  <ClipboardCheck size={15} />
                  <span>
                    <strong>Document Vault</strong>
                    <small>Contracts, evidence and records</small>
                  </span>
                </button>
              </div>
            </section>

            <div className={styles.contextActivity}>
              <span>Command Receipts</span>
              {executiveActivities.slice(0, 3).map((activity, index) => (
                <article key={activity.id || index}>
                  <strong>{compactExecutiveSignal(activity.eventType || activity.event || 'EXEC_EVENT')}</strong>
                  <small>{activity.message || (activity.proofHash ? `Proof ${activity.proofHash.slice(0, 14)}` : 'Awaiting command proof')}</small>
                </article>
              ))}
              {executiveActivities.length === 0 && (
                <article>
                  <strong>No command executed yet</strong>
                  <small>Open Business Artifacts, run a command, or launch a vertical system.</small>
                </article>
              )}
            </div>
          </aside>
      </section>

      <div className={styles.legacyContinuousStack} aria-hidden="true">
      <header className={styles.header}>
        <div>
          <span className={styles.eyebrow}><Briefcase size={14} /> {executiveIdentity.commandLabel}</span>
          <h1>
            SOVEREIGN EXECUTIVE SUITE
          </h1>
          <div className={styles.operatingStoryRail} aria-label="Wilsy OS executive operating story">
            <span>{executiveIdentity.storyMessages.join('     •     ')}</span>
          </div>
        </div>
        <div className={styles.brandPlate}>
          <div className={styles.tenantMark}>
            {tenantBranding.logo ? (
              <img src={tenantBranding.logo} alt={`${tenantBranding.displayName} mark`} />
            ) : (
              <span>{tenantBranding.initials}</span>
            )}
          </div>
          <div>
            <small>{executiveIdentity.tenantEyebrow}</small>
            <strong>{executiveIdentity.tenantName}</strong>
            <em>{executiveIdentity.tenantStory}</em>
          </div>
        </div>
        <div className={styles.toolbar}>
          <label className={styles.searchBox}>
            <Search size={13} />
            <input
              value={searchTerm}
              onChange={event => setSearchTerm(event.target.value)}
              placeholder="Search Wilsy OS or press ⌘K" onFocus={() => window.dispatchEvent(new CustomEvent('wilsy:open-command-search'))}
            />
          </label>
          <button
            onClick={loadAllData}
            disabled={isRefreshing}
            className={styles.secondaryButton}
          >
            <RefreshCw size={13} className={isRefreshing ? styles.spin : ''} /> LIVE SYNC
          </button>
          <button
            onClick={handleExport}
            className={styles.secondaryButton}
          >
            <Download size={13} /> EXPORT
          </button>
          <button
            onClick={() => {
              setEditingItem(null);
              setModalType(TAB_TO_MODAL_MAP[activeTab] || 'kpi');
              setShowModal(true);
            }}
            className={styles.primaryButton}
          >
            <Plus size={13} /> NEW COMMAND {TAB_TO_LABEL_MAP[activeTab] || 'KPI'}
          </button>
        </div>
      </header>

      <section className={styles.commandDeck}>
        <article className={styles.finalityPanel}>
          <div className={styles.finalityHeader}>
            <div>
              <span>
                <ShieldCheck size={13} /> Executive Readiness
              </span>
              <strong>
                {executiveReadiness.score}% // {executiveReadiness.posture}
              </strong>
            </div>
            <div>
              <span>LIVE_SOURCE_COVERAGE</span>
              <strong>{executiveReadiness.liveSources}/{executiveReadiness.totalSources}</strong>
            </div>
          </div>
          <div className={styles.sourceMatrix}>
            <div>
              <span>FINANCE_TRUTH_SOURCE</span>
              <strong title={sourceSnapshot.finance.status}>{compactExecutiveSignal(sourceSnapshot.finance.status)}</strong>
              <small>{sourceSnapshot.finance.proofHash?.slice(0, 18) || 'PROOF_PENDING'}</small>
            </div>
            <div>
              <span>TELEMETRY_STREAM</span>
              <strong title={sourceSnapshot.telemetry.status}>{compactExecutiveSignal(sourceSnapshot.telemetry.status)}</strong>
              <small>{sourceSnapshot.telemetry.lastSync || 'SYNC_PENDING'}</small>
            </div>
            <div>
              <span>SHARD_PAGINATION</span>
              <strong>{pageStates[activeTab].limit} ROW WINDOWS</strong>
              <small>{sourceSnapshot.records.proofHash?.slice(0, 18) || 'PROOF_PENDING'}</small>
            </div>
          </div>
        </article>

        <article className={styles.memoPanel}>
          <span><ClipboardCheck size={13} /> Decision Memo</span>
          <h2>{executiveMemo.nextAction}</h2>
          {executiveMemo.dutyReason && <p>{executiveMemo.dutyReason}</p>}
          <div className={styles.memoGrid}>
            <div>
              <small>ARR</small>
              <strong>{formatExecutiveMoney(executiveMemo.arr)}</strong>
            </div>
            <div>
              <small>Revenue</small>
              <strong>{formatExecutiveMoney(executiveMemo.revenue)}</strong>
            </div>
            <div>
              <small>Industry</small>
              <strong>{executiveMemo.industry}</strong>
            </div>
          </div>
          <p>MEMO_PROOF // {executiveMemo.proofHash.slice(0, 28)}</p>
        </article>

        <article className={styles.sourceRegistry}>
          <span><Database size={13} /> SOURCE_REGISTRY</span>
          <div>
            {sourceRows.map(source => (
              <div key={source.key}>
                <small>{source.live ? <CheckCircle size={11} /> : <AlertTriangle size={11} />} {source.key}</small>
                <strong data-live={source.live ? 'true' : 'false'} title={source.status}>
                  {compactExecutiveSignal(source.status)}
                </strong>
              </div>
            ))}
          </div>
          {sourceRepairQueue.length > 0 && (
            <div className={styles.repairQueue}>
              <small>SOURCE_REPAIR_QUEUE</small>
              {sourceRepairQueue.slice(0, 3).map(action => (
                <button
                  type="button"
                  key={action.id}
                  onClick={() => requestSourceRepair(action)}
                  disabled={isRefreshing}
                >
                  <AlertTriangle size={12} />
                  <span>{action.title}</span>
                </button>
              ))}
            </div>
          )}
        </article>
      </section>

      <section className={styles.commandRail}>
        <button type="button" onClick={() => executeExecutiveCommand('KPI_REBASE')}>
          <PieChart size={16} />
          <span>KPI Rebase</span>
          <small>Refresh finance KPIs</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('BOARD_PACKET')}>
          <FileText size={16} />
          <span>Seal Board Pack</span>
          <small>Prepare board pack</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('INVESTOR_BRIEF')}>
          <Send size={16} />
          <span>Investor Brief</span>
          <small>Create investor update</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('STRATEGIC_MANDATE')}>
          <Target size={16} />
          <span>Mandate Goal</span>
          <small>Readiness-linked objective</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('WILSY_AI_LICENSE')}>
          <ShieldCheck size={16} />
          <span>Wilsy AI</span>
          <small>License top automation</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('TRANSFORMATION_PLAYBOOK')}>
          <Building2 size={16} />
          <span>ARR Playbook</span>
          <small>{executiveTransformation.phase?.target || 'Roadmap phase'}</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('INTEGRATION_SPRINT')}>
          <Database size={16} />
          <span>Integration Sprint</span>
          <small>{executiveTransformation.integrationRows?.[0]?.label || 'Connector lane'}</small>
        </button>
        <button type="button" onClick={() => executeExecutiveCommand('TRUST_PACKET')}>
          <ShieldCheck size={16} />
          <span>Trust Packet</span>
          <small>Review trust evidence row</small>
        </button>
      </section>

      <section className={styles.operatingSourceDeck}>
        <header>
          <div>
            <span><Database size={13} /> CEO_OPERATING_SOURCE_FABRIC</span>
            <h2>HR, CRM, revenue, product and risk rails</h2>
          </div>
          <small>{operatingSourceCoverage.live}/{operatingSourceCoverage.total} LIVE</small>
        </header>
        <div className={styles.operatingSourceGrid}>
          {operatingSources.map(source => (
            <article key={source.key} data-live={source.live ? 'true' : 'false'}>
              <small>{source.lane} // {source.count === null ? 'SOURCE_REQUIRED' : `${source.count} ROWS`}</small>
              <strong>{source.label}</strong>
              <span title={source.status}>{compactExecutiveSignal(source.status)}</span>
              <button
                type="button"
                className={styles.inlineAction}
                onClick={() => executeFunctionCard({
                  key: source.functionKey,
                  label: source.label,
                  status: source.live ? 'ENABLED' : 'RECOMMENDED',
                  sourceStatus: source.status
                })}
                disabled={isRefreshing}
              >
                <Route size={12} /> Open Rail
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.transformationGrid}>
        <article className={styles.transformationHero}>
          <header>
            <div>
              <span><Building2 size={13} /> ARR_TRANSFORMATION_PLAYBOOK</span>
              <h2>{executiveTransformation.phase?.label}</h2>
            </div>
            <small>{executiveTransformation.phase?.months} // {executiveTransformation.phase?.target}</small>
          </header>
          <div className={styles.phaseMeter}>
            <div>
              <strong>{executiveTransformation.phaseProgress}%</strong>
              <span>PHASE_PROGRESS</span>
            </div>
            <div className={styles.phaseTrack}>
              <i style={{ width: `${executiveTransformation.phaseProgress}%` }} />
            </div>
          </div>
          <p>{executiveTransformation.phase?.mandate}</p>
          <div className={styles.transformationStats}>
            <div>
              <small>ARR</small>
              <strong>{formatExecutiveMoney(executiveTransformation.arr, executiveTransformation.currency)}</strong>
            </div>
            <div>
              <small>REVENUE</small>
              <strong>{formatExecutiveMoney(executiveTransformation.revenue, executiveTransformation.currency)}</strong>
            </div>
            <div>
              <small>READINESS</small>
              <strong>{executiveTransformation.readinessScore}%</strong>
            </div>
            <div>
              <small>PLAYBOOK_PROOF</small>
              <strong>{executiveTransformation.proofHash?.slice(0, 18)}</strong>
            </div>
          </div>
          <div className={styles.priorityStack}>
            {executiveTransformation.priorityActions.slice(0, 5).map(action => (
              <article key={action.id} data-status={action.status}>
                <small>{action.priority} // {action.lane}</small>
                <strong>{action.title}</strong>
                <span title={action.proofHash}>{compactExecutiveSignal(action.status)}</span>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.intelligencePanel}>
          <header>
            <div>
              <span><PieChart size={13} /> AI_POWERED_EXECUTIVE_INTELLIGENCE</span>
              <h2>Forecast, anomaly and board signals</h2>
            </div>
            <small>{executiveTransformation.insightRows.length} INSIGHT LANES</small>
          </header>
          <div className={styles.insightList}>
            {executiveTransformation.insightRows.map(insight => (
              <article key={insight.id} data-status={insight.status}>
                <div>
                  <small>{insight.lane} // {insight.confidence}%</small>
                  <strong>{insight.title}</strong>
                  <p>{insight.signal}</p>
                </div>
                <span title={insight.proofHash}>{compactExecutiveSignal(insight.status)}</span>
              </article>
            ))}
          </div>
          <form className={styles.nlqBox} onSubmit={askExecutiveOS}>
            <label>
              <Search size={13} />
              <input
                value={executiveQuestion}
                onChange={event => setExecutiveQuestion(event.target.value)}
                placeholder="ASK_REVENUE_SOURCE_BOARD_COMPLIANCE"
              />
            </label>
            <button type="submit" className={styles.primaryButton} disabled={isRefreshing || !executiveQuestion.trim()}>
              ASK
            </button>
          </form>
          {executiveAnswer && (
            <div className={styles.nlqAnswer}>
              <small>{executiveAnswer.intent} // {executiveAnswer.proofHash.slice(0, 18)}</small>
              <strong>{executiveAnswer.answer}</strong>
              <div>
                {executiveAnswer.evidenceRows.slice(0, 4).map(row => (
                  <span key={row}>{row}</span>
                ))}
              </div>
            </div>
          )}
        </article>

        <article className={styles.integrationPanel}>
          <header>
            <div>
              <span><Database size={13} /> INTEGRATION_MARKETPLACE_READINESS</span>
              <h2>Finance, CRM, alerts and identity rails</h2>
            </div>
            <small>{executiveTransformation.integrationRows.filter(row => row.status === 'READY_TO_CONNECT').length} READY</small>
          </header>
          <div className={styles.connectorGrid}>
            {executiveTransformation.integrationRows.slice(0, 8).map(connector => (
              <article key={connector.key} data-status={connector.status}>
                <small>{connector.lane} // {compactExecutiveSignal(connector.sourceStatus)}</small>
                <strong>{connector.label}</strong>
                <span>{connector.value}</span>
                <em title={connector.proofHash}>{compactExecutiveSignal(connector.status)}</em>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.trustPanel}>
          <header>
            <div>
              <span><ShieldCheck size={13} /> ENTERPRISE_TRUST_STACK</span>
              <h2>SOC2, POPIA, audit export and RBAC</h2>
            </div>
            <small>{executiveTransformation.trustRows.filter(row => ['EVIDENCE_READY', 'EXPORT_READY', 'RBAC_ACTIVE'].includes(row.status)).length} SEALED</small>
          </header>
          <div className={styles.trustRows}>
            {executiveTransformation.trustRows.map(row => (
              <article key={row.key} data-status={row.status}>
                <div>
                  <small>{row.lane} // SCORE {row.score}</small>
                  <strong>{row.label}</strong>
                </div>
                <span title={row.sourceStatus}>{compactExecutiveSignal(row.status)}</span>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.moatPanel}>
          <header>
            <div>
              <span><Target size={13} /> COMPETITIVE_KILL_MATRIX</span>
              <h2>Market counter-positioning</h2>
            </div>
            <small>{executiveTransformation.moatRows.filter(row => row.status === 'MOAT_LIVE').length} LIVE MOATS</small>
          </header>
          <div className={styles.moatRows}>
            {executiveTransformation.moatRows.map(row => (
              <article key={row.key} data-status={row.status}>
                <small>{row.label} // {compactExecutiveSignal(row.status)}</small>
                <strong>{row.wilsyMove}</strong>
                <p>{row.competitorSignal}</p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section className={styles.operatingGrid}>
        <article className={styles.dailyDutyPanel}>
          <header>
            <div>
              <span><ClipboardCheck size={13} /> DAILY_EXECUTIVE_WORKBENCH</span>
              <h2>{executiveOperatingSystem.profile.name}</h2>
            </div>
            <small title={executiveOperatingSystem.profile.sourceStatus}>{compactExecutiveSignal(executiveOperatingSystem.profile.sourceStatus)}</small>
          </header>
          <div className={styles.profileStrip}>
            <div>
              <small>Business Model</small>
              <strong>{executiveOperatingSystem.profile.industryLabel}</strong>
            </div>
            <div>
              <small>MODEL_SELECTOR</small>
              <label className={styles.modelSelector}>
                <select
                  value={businessModelOverride || ''}
                  onChange={event => updateBusinessModelOverride(event.target.value)}
                >
                  <option value="">Tenant auto-detect</option>
                  {executiveOperatingSystem.businessModels.map(model => (
                    <option key={model.key} value={model.key}>{model.label}</option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className={styles.inlineAction}
                onClick={persistBusinessModelCommand}
                disabled={isRefreshing}
              >
                <Settings size={12} /> Persist Model
              </button>
            </div>
            <div>
              <small>BUSINESS_FAMILY</small>
              <strong>{executiveOperatingSystem.profile.naicsFamily || 'General operating model'}</strong>
            </div>
            <div>
              <small>CONFIDENCE</small>
              <strong>{Math.round((executiveOperatingSystem.profile.confidence || 0) * 100)}% // {compactExecutiveSignal(executiveOperatingSystem.profile.sourceStatus)}</strong>
            </div>
            <div>
              <small>PROFILE_EVIDENCE</small>
              <strong>{executiveOperatingSystem.profile.sourceEvidence}</strong>
            </div>
          </div>
          <div className={styles.functionMatrix}>
            {executiveOperatingSystem.functionMatrix.map(item => (
              <article key={item.key} data-status={item.status}>
                <div>
                  <small>{item.label}</small>
                  <strong>{compactExecutiveSignal(item.status)}</strong>
                </div>
                <button
                  type="button"
                  className={isFunctionExecutable(item) ? styles.iconButton : `${styles.iconButton} ${styles.dangerButton}`}
                  onClick={() => executeFunctionCard(item)}
                  title={isFunctionExecutable(item) ? `Open ${item.label}` : `Request access to ${item.label}`}
                  disabled={isRefreshing}
                >
                  {isFunctionExecutable(item) ? <Route size={13} /> : <Lock size={13} />}
                </button>
              </article>
            ))}
          </div>
          <div className={styles.workOrderPanel}>
            <header>
              <div>
                <span><PlayCircle size={13} /> EXECUTIVE_WORK_ORDER</span>
                <h2>{selectedWorkOrder?.title || 'No accepted work order yet'}</h2>
              </div>
              <small>{selectedWorkOrder ? compactExecutiveSignal(selectedWorkOrder.status) : 'AWAITING_DUTY_ACCEPTANCE'}</small>
            </header>
            {selectedWorkOrder ? (
              <div className={styles.workOrderBody}>
                <div className={styles.workOrderMeta}>
                  <div>
                    <small>MODULE</small>
                    <strong>{selectedWorkOrder.functionKey}</strong>
                  </div>
                  <div>
                    <small>ROUTE</small>
                    <strong>{selectedWorkOrder.route?.route || '/executive'}</strong>
                  </div>
                  <div>
                    <small>PROOF</small>
                    <strong>{selectedWorkOrder.proofHash?.slice(0, 18)}</strong>
                  </div>
                </div>
                <ol className={styles.workSteps}>
                  {(selectedWorkOrder.workflowSteps || []).map(step => (
                    <li key={step}>{step}</li>
                  ))}
                </ol>
                {selectedWorkOrder.blockedReason && <p className={styles.blockedReason}>{selectedWorkOrder.blockedReason}</p>}
                <div className={styles.workOrderActions}>
                  <button
                    type="button"
                    className={styles.primaryButton}
                    onClick={() => runExecutiveWorkOrder(selectedWorkOrder)}
                    disabled={isRefreshing}
                  >
                    {selectedWorkOrder.blocked ? 'REVIEW GATES' : 'RUN WORK ORDER'}
                  </button>
                  <select
                    value={selectedWorkOrder.workOrderId}
                    onChange={event => setSelectedWorkOrderId(event.target.value)}
                  >
                    {executiveWorkOrders.map(order => (
                      <option key={order.workOrderId} value={order.workOrderId}>{order.title}</option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              <div className={styles.emptyStream}>ACCEPT_A_DAILY_DUTY_TO_CREATE_A_WORK_ORDER...</div>
            )}
          </div>
          <div className={styles.dutyList}>
            {executiveOperatingSystem.dailyDuties.map(duty => (
              <article key={duty.key} className={styles.dutyCard} data-status={duty.status} data-impact={duty.impact}>
                <div>
                  <span>{duty.lane} // {duty.cadence}</span>
                  <h3>{duty.title}</h3>
                  <p>{duty.reason}</p>
                  <div className={styles.evidenceRail}>
                    {(duty.evidenceRequired || []).slice(0, 4).map(evidence => (
                      <i key={evidence}>{evidence}</i>
                    ))}
                  </div>
                  {duty.blockedReason && <p className={styles.blockedReason}>{duty.blockedReason}</p>}
                  <small title={duty.sourceStatus}>{compactExecutiveSignal(duty.sourceStatus)} // IMPACT {duty.impact}</small>
                </div>
                <button
                  type="button"
                  className={styles.secondaryButton}
                  onClick={() => acceptDailyDuty(duty)}
                  disabled={isRefreshing}
                >
                  {duty.commandLabel || 'ACCEPT'}
                </button>
              </article>
            ))}
          </div>
        </article>

        <article className={styles.aiPanel}>
          <header>
            <div>
              <span><ShieldCheck size={13} /> WILSY_AI_LICENSE_LADDER</span>
              <h2>Tenant Automation Add-ons</h2>
            </div>
            <small title={wilsyAIEntitlements.status || wilsyAiPlan[0]?.readiness || 'PLAN_PENDING'}>
              {compactExecutiveSignal(wilsyAIEntitlements.status || wilsyAiPlan[0]?.readiness || 'PLAN_PENDING')}
            </small>
          </header>
          <div className={styles.aiList}>
            {wilsyAiPlan.map(plan => (
              <article key={plan.id} className={styles.aiCard} data-readiness={plan.readiness}>
                <span>{plan.tier} // {plan.licenseStatus || 'UNLICENSED'}</span>
                <h3>{plan.name}</h3>
                <p>{plan.differentiator || plan.valuePromise || plan.reason}</p>
                <div className={styles.aiEconomics}>
                  <div>
                    <small>MONTHLY</small>
                    <strong>{formatOperatingMoney(plan.monthlyPriceZar ?? plan.monthlyPrice ?? null, 'ZAR')}</strong>
                  </div>
                  <div>
                    <small>DAILY REQUESTS</small>
                    <strong>
                      {formatExecutiveUsageValue(plan.usageAnalytics?.daily?.requestUnits)}
                      /{formatExecutiveUsageValue(plan.dailyRequestLimit)}
                    </strong>
                  </div>
                  <div>
                    <small>MONTH VALUE</small>
                    <strong>{formatOperatingMoney(plan.usageAnalytics?.monthly?.estimatedValueZar ?? null, 'ZAR')}</strong>
                  </div>
                </div>
                <small title={plan.sourceStatus}>
                  {plan.tenantFit} // {compactExecutiveSignal(plan.sourceStatus)} // {compactExecutiveSignal(plan.usageAnalytics?.quotaStatus || 'USAGE_SOURCE_REQUIRED')}
                </small>
                <div className={styles.aiActions}>
                <button
                  type="button"
                  className={styles.primaryButton}
                  onClick={() => activateWilsyAiUseCase(plan)}
                  disabled={isRefreshing || plan.readiness === 'ACCESS_DENIED' || plan.licenseStatus === 'ACTIVE'}
                >
                  {plan.licenseStatus === 'ACTIVE' ? 'ACTIVE' : 'LICENSE'}
                </button>
                <button
                  type="button"
                  className={styles.secondaryButton}
                  onClick={() => logWilsyAiRequest(plan)}
                  disabled={isRefreshing || plan.licenseStatus !== 'ACTIVE'}
                >
                  LOG REQUEST
                </button>
                </div>
              </article>
            ))}
            {wilsyAiPlan.length === 0 && (
              <div className={styles.emptyStream}>WILSY_AI_PLAN_REQUIRES_TENANT_PROFILE...</div>
            )}
          </div>
        </article>
      </section>

      <section className={styles.kpiGrid}>
        <article>
          <span>REVENUE_YTD_COUNTER</span>
          <strong data-tone="green">{formatExecutiveKpiValue(financialKPIs.revenue, financialKPIs.currency || DEFAULT_OPERATING_CURRENCY)}</strong>
        </article>
        <article>
          <span>ANNUAL_RECURRING_ARR</span>
          <strong>{formatExecutiveKpiValue(financialKPIs.arr, financialKPIs.currency || DEFAULT_OPERATING_CURRENCY)}</strong>
        </article>
        <article>
          <span>PROFIT_MARGIN_EFFICIENCY</span>
          <strong>{formatExecutiveKpiValue(financialKPIs.profitMargin, '%')}</strong>
        </article>
        <article>
          <span>NET_PROMOTER_INDEX</span>
          <strong>{formatExecutiveKpiValue(financialKPIs.nps, 'score')}</strong>
        </article>
        <article>
          <span>EMPLOYEE_SAT_COEFFICIENT</span>
          <strong data-tone="green">{formatExecutiveKpiValue(financialKPIs.employeeSatisfaction, '%')}</strong>
        </article>
      </section>

      <section className={styles.currencyPanel}>
        <header>
          <div>
            <span>ZA_CURRENCY_INTELLIGENCE</span>
            <h2>ZAR Operating Lens</h2>
          </div>
          <small title={currencyWorkbench.sourceStatus}>{compactExecutiveSignal(currencyWorkbench.sourceStatus)}</small>
        </header>
        <div className={styles.fxWorkbench}>
          <div className={styles.fxControls}>
            <label>
              <span>Amount</span>
              <input
                type="number"
                min="0"
                step="0.01"
                value={currencyWorkbench.amount}
                onChange={event => setCurrencyWorkbench(prev => ({ ...prev, amount: event.target.value }))}
              />
            </label>
            <label>
              <span>From</span>
              <select
                value={currencyWorkbench.fromCurrency}
                onChange={event => setCurrencyWorkbench(prev => ({ ...prev, fromCurrency: event.target.value }))}
              >
                {EXECUTIVE_CURRENCIES.map(currency => <option key={currency} value={currency}>{currency}</option>)}
              </select>
            </label>
            <label>
              <span>To</span>
              <select
                value={currencyWorkbench.toCurrency}
                onChange={event => setCurrencyWorkbench(prev => ({ ...prev, toCurrency: event.target.value }))}
              >
                {EXECUTIVE_CURRENCIES.map(currency => <option key={currency} value={currency}>{currency}</option>)}
              </select>
            </label>
            <button type="button" className={styles.primaryButton} onClick={runCurrencyConversion} disabled={isRefreshing}>
              CONVERT
            </button>
          </div>
          <div className={styles.fxResult}>
            <span>CONVERSION_RECEIPT</span>
            <strong>
              {currencyWorkbench.conversion?.display?.converted || 'FX_SOURCE_REQUIRED'}
            </strong>
            <small>
              {currencyWorkbench.conversion?.display?.source || formatOperatingMoney(currencyWorkbench.amount, currencyWorkbench.fromCurrency)}
              {' '} // RATE {currencyWorkbench.conversion?.rate || 'SOURCE_REQUIRED'}
            </small>
            <p>
              {currencyWorkbench.conversion?.sarbReview?.status || 'SARB_INTERNAL_REVIEW_PENDING'} // PROOF{' '}
              {(currencyWorkbench.conversion?.proofHash || currencyWorkbench.proofHash || 'PENDING').slice(0, 22)}
            </p>
          </div>
          <div className={styles.fxRates}>
            {currencyWorkbench.watchlist.length === 0 ? (
              <div className={styles.emptyStream}>FX_WATCHLIST_SOURCE_REQUIRED...</div>
            ) : currencyWorkbench.watchlist.map(rate => (
              <article key={`${rate.baseCurrency}-${rate.quoteCurrency}`}>
                <small>{rate.baseCurrency}/{rate.quoteCurrency}</small>
                <strong>{rate.rate || 'SOURCE_REQUIRED'}</strong>
                <span title={rate.sourceStatus}>{compactExecutiveSignal(rate.sourceStatus)}</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <nav className={styles.tabs} aria-label="Executive command workspace">
        {[
          { id: 'kpis', label: 'STRATEGIC KPIS', icon: <BarChart3 size={12} /> },
          { id: 'boardReports', label: 'BOARD REPORTS', icon: <FileText size={12} /> },
          { id: 'investorUpdates', label: 'INVESTOR UPDATES', icon: <Users size={12} /> },
          { id: 'strategicGoals', label: 'GOALS_PROJECTION', icon: <Target size={12} /> }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              fetchTabData(tab.id, pageStates[tab.id]);
            }}
            className={activeTab === tab.id ? styles.tabActive : styles.tabButton}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </nav>

      <section className={styles.panel}>
        <div className={styles.panelHeader}>
          <div>
            <span>EXECUTIVE_LEDGER</span>
            <h2>{TAB_TO_LABEL_MAP[activeTab] || 'KPI'} GOVERNANCE</h2>
          </div>
          <small title={sourceSnapshot.records.status}>{pageStates[activeTab].limit} row shard // {compactExecutiveSignal(sourceSnapshot.records.status)}</small>
        </div>
        {renderContent()}
      </section>

      <section className={styles.telemetryPanel}>
        <header>
          <h3><Activity size={13} /> EXECUTIVE_TELEMETRY_STREAM</h3>
          <span title={sourceSnapshot.telemetry.status}>{telemetrySyncing ? 'SYNCING' : compactExecutiveSignal(sourceSnapshot.telemetry.status)}</span>
        </header>
        <div>
          {executiveActivities.length === 0 && (
            <div className={styles.emptyStream}>EXEC_STREAM_VACANT_AWAITING_MUTATIONS...</div>
          )}
          {executiveActivities.map((act, idx) => (
            <article key={act.id || idx}>
              {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : 'EXEC_NOW'} //{' '}
              {act.eventType} // {act.event || 'COMMITTED'} // {act.message || 'TRANSACTION_LOG_COMMITTED'} // PROOF{' '}
              {act.proofHash?.slice(0, 16) || 'PENDING'}
            </article>
          ))}
        </div>
      </section>
      </div>

      
        <BusinessArtifactStudio tenantId={tenantId} />

<WilsyAccountCommandCenter
        isOpen={isAccountCommandCenterOpen}
        onClose={() => setIsAccountCommandCenterOpen(false)}
        onNavigate={handleAccountCommand}
        onSignOut={handleExecutiveSignOut}
        user={user || access}
        activeThemeId={accountThemeId}
        themeMode={accountThemeMode}
        onThemeChange={setAccountThemeId}
        onModeChange={setAccountThemeMode}
        securitySummary={{
          identitySource: accessDecision.allowed ? 'Executive access verified' : 'Access gated',
          mfaStatus: sourceSnapshot.security?.live ? 'Risk rail online' : '',
          trustedDevices: sourceSnapshot.it?.live ? 'IT source live' : '',
          accountActivity: executiveReadiness.posture
        }}
        complianceSummary={{
          privacyStatus: 'POPIA display safe',
          complianceStatus: sourceSnapshot.security?.live ? 'Security source live' : 'Compliance source required',
          auditConfidence: `${executiveReadiness.score}% readiness`,
          retentionStatus: sourceSnapshot.records?.status || 'Tenant ledger ready'
        }}
        sessionSummary={{
          activeSessions: telemetrySyncing ? 'Telemetry syncing' : compactExecutiveSignal(sourceSnapshot.telemetry.status)
        }}
      />

      {showModal && (
        <div className={styles.modalBackdrop}>
          <form className={styles.modal} onSubmit={(event) => {
            event.preventDefault();
            handleSave(modalDraft);
          }}>
            <header>
              <div>
                <span>Business Update</span>
                <h2>{modalType.toUpperCase()}</h2>
              </div>
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className={styles.iconButton}
              >
                <X size={15} />
              </button>
            </header>
            <p>
              {EXECUTIVE_SUITE_VERSION} // EXEC_{MUTATION_TYPE_MAP[modalType] || 'EXECUTIVE_RECORD'}_MUTATION
            </p>
            {renderModalFields()}
            <div className={styles.proofPreview}>
              Audit Preview // {createExecutiveProofHash({ tenantId, modalType, activeTab, modalDraft, suiteVersion: EXECUTIVE_SUITE_VERSION }).slice(0, 36)}
            </div>
            <div className={styles.modalActions}>
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className={styles.secondaryButton}
              >
                ABORT
              </button>
              <button
                type="submit"
                className={styles.primaryButton}
              >
                COMMIT EXEC
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default ExecutiveDashboard;
