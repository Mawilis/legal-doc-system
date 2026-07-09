/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM COMMAND CENTER                                                                                        ║
 * ║ SOVEREIGN SALES INTELLIGENCE | SOURCE-LED PIPELINE | COMPLIANCE HUD | INVESTOR TELEMETRY | ACCOUNT COMMAND CENTER     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/crm/CRMDashboard.jsx                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated investor-grade CRM capable of sovereign sales intelligence and forensic proof posture.   ║
 * ║ 2. AI Engineering - Rebuilt the CRM as one source-led operating shell with no visible build labels or fake records.    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Wilsy OS CRM Command Center.
 * This surface renders one CRM shell only. It does not display internal build labels, fake customer records,
 * or duplicate legacy workspaces. Every metric is derived from live source routes or shown as a source gap.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Building2,
  CalendarDays,
  CheckCircle2,
  CheckSquare,
  ChevronRight,
  CircleDollarSign,
  Command,
  Crown,
  Database,
  FileCheck2,
  FileText,
  Fingerprint,
  Home,
  LockKeyhole,
  Mail,
  Network,
  Phone,
  Plus,
  RefreshCcw,
  Search,
  Shield,
  Sparkles,
  Target,
  UploadCloud,
  User,
  Users,
  Zap
} from 'lucide-react';
import WilsyAccountCommandCenter from '../account/WilsyAccountCommandCenter';
import {
  DEFAULT_OPERATING_SKINS as WILSY_OPERATING_SKINS,
  buildVisualTokens as buildWilsyVisualTokens,
  commitWilsyThemeRuntime,
  readStoredWilsyThemeRuntime,
  resolveAutoMode as resolveWilsyAutoMode,
  subscribeWilsyThemeRuntime
} from '../account/wilsyAccountThemeTokens';
import { useTenants } from '../../contexts/tenantContext';
import wilsyLogo from '../../assets/logo/wilsy.jpeg';
import styles from './CRMDashboard.module.css';
import WilsyContactOperatingRoom from './contact/WilsyContactOperatingRoom.jsx';
import WilsyAccountOperatingRoom from './account/WilsyAccountOperatingRoom.jsx';
import { installCrmSearchOutcomeRuntime } from './CrmSearchOutcomeRuntime.js';

import { searchCrmCommandFabric, syncCrmCommandFabric, createCrmCommandLead } from '../../services/crmService.js';

import CrmSovereignSideRail from './rail/CrmSovereignSideRail.jsx';

import WilsyLeadOperatingRoom from './lead/WilsyLeadOperatingRoom.jsx';
import WilsyUniversalMeetingCommandCenter from './meeting/WilsyUniversalMeetingCommandCenter.jsx';

import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';
import { WilsyMeetingsWorkspace } from './meeting/workspace';
import WilsyMeetingOperatingRoom from './meeting/WilsyMeetingOperatingRoom';
import WilsyCrmSetupControlPlane from './setup/WilsyCrmSetupControlPlane';
import WilsyCrmRawStreamThread from './WilsyCrmRawStreamThread.jsx';
const WILSY_R66A_LEAD_OPERATING_ROOM = 'R66A-WILSY-LEAD-OPERATING-ROOM';
const WILSY_R65A_TRI_STATE_KINETIC_RAIL = 'R65A-TRI-STATE-KINETIC-RAIL';
const WILSY_R62I_CRM_CLEAN_INLINE_COMMAND_FABRIC = 'R62I-CRM-CLEAN-INLINE-COMMAND-FABRIC';
const CRM_INTERNAL_DIAGNOSTIC_ID = 'CRM-COMMAND-CENTER';
const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * @function resolveR88FCrmCommandTenantId
 * @description Resolves CRM command tenant authority without falling back to raw MASTER when tenant context has a sealed root tenant.
 * @param {Object} tenantConfig - Tenant config.
 * @param {Object} user - User profile.
 * @returns {string} Tenant id.
 * @collaboration Lead persistence, command search, sealed tenant context.
 */
function resolveR88FCrmCommandTenantId(tenantConfig = {}, user = {}) {
  return String(
    tenantConfig?.tenantId
    || tenantConfig?.id
    || tenantConfig?.tenantKey
    || user?.tenantId
    || user?.tenant?.tenantId
    || user?.tenant?.id
    || 'wilsy-sovereign-root'
  ).trim() || 'wilsy-sovereign-root';
}

const CRM_ENDPOINTS = Object.freeze({
  leads: '/api/crm/live/leads',
  contacts: '/api/crm/live/contacts',
  accounts: '/api/crm/live/accounts',
  deals: '/api/crm/live/deals',
  tasks: '/api/crm/live/tasks',
  meetings: '/api/crm/live/meetings',
  evidence: '/api/crm/live/evidence',
  connectors: '/api/crm/live/connectors'
});

const CRM_SOURCE_POSTURE_ENDPOINT = '/api/crm/live/source-posture';

/**
 * @function extractWilsyR91K179E24P45BRailLiveCounts
 * @description Extracts source-backed CRM rail counts from the live source-posture payload without creating fake counts.
 * @param {Object} payload - Source posture payload.
 * @returns {Object} Workspace id to live record count map.
 * @collaboration CRM left rail, /api/crm/live/source-posture, source-backed count badges.
 */
function extractWilsyR91K179E24P45BRailLiveCounts(payload = {}) {
  const sourceRows = [
    ...(Array.isArray(payload.sources) ? payload.sources : []),
    ...(Array.isArray(payload.data?.sources) ? payload.data.sources : []),
    ...(Array.isArray(payload.sourcePosture?.sources) ? payload.sourcePosture.sources : []),
  ];

  return sourceRows.reduce((counts, source = {}) => {
    const routeTail = String(source.route || '')
      .split('/')
      .filter(Boolean)
      .pop();

    const ids = [
      source.id,
      source.key,
      source.collection,
      source.label,
      routeTail,
    ]
      .map((value) => String(value || '').trim().toLowerCase())
      .filter(Boolean);

    const count = Number(
      source.recordCount ??
      source.count ??
      source.meta?.count ??
      source.recordsLength ??
      (Array.isArray(source.records) ? source.records.length : undefined) ??
      (Array.isArray(source.data) ? source.data.length : undefined)
    );

    if (!Number.isFinite(count) || count < 0) {
      return counts;
    }

    ids.forEach((id) => {
      counts[id] = count;
    });

    return counts;
  }, {});
}


const CRM_ROUTE_SURFACE_ENDPOINT = '/api/crm/live/route-surface';
const CRM_SOURCE_GUIDE_ENDPOINT = '/api/crm/live/source-guide';

const USER_PROFILE_ENDPOINTS = Object.freeze([
  import.meta.env.VITE_USER_PROFILE_URL,
  import.meta.env.VITE_OPERATOR_PROFILE_URL,
  '/api/auth/me',
  '/api/auth/user',
  '/api/auth/profile',
  '/api/users/me',
  '/api/users/profile',
  '/api/user/me',
  '/api/user/profile',
  '/api/profile/me',
  '/api/account/me',
  '/api/account/profile',
  '/api/operator/me',
  '/api/operator/profile',
  '/api/me',
  '/api/v1/auth/me',
  '/api/v1/users/me',
  '/api/v1/profile/me'
].filter(Boolean));

const CRM_WORKSPACES = Object.freeze([
  { id: 'home', label: 'Home', icon: Home, group: 'Command' },
  { id: 'leads', label: 'Leads', icon: Database, group: 'Records' },
  { id: 'contacts', label: 'Contacts', icon: Users, group: 'Records' },
  { id: 'accounts', label: 'Accounts', icon: Building2, group: 'Records' },
  { id: 'deals', label: 'Deals', icon: Target, group: 'Records' },
  { id: 'tasks', label: 'Tasks', icon: CheckSquare, group: 'Records' },
  { id: 'meetings', label: 'Meetings', icon: CalendarDays, group: 'Records' },
  { id: 'evidence', label: 'Evidence', icon: Shield, group: 'Control' },
  { id: 'connectors', label: 'Connectors', icon: Network, group: 'Control' }
]);

const CRM_HOME_TABS = Object.freeze([
  { id: 'operate', label: 'Operate', icon: Command },
  { id: 'pipeline', label: 'Pipeline', icon: Target },
  { id: 'create', label: 'Create', icon: Plus },
  { id: 'proof', label: 'Proof', icon: Shield }
]);

const CRM_TENANT_COMMAND_ROLE_TOKENS = Object.freeze([
  'FOUNDER',
  'CEO',
  'OWNER',
  'SUPER_ADMIN',
  'TENANT_OWNER',
  'TENANT_ADMIN',
  'ADMIN',
  'WORKSPACE_ADMIN',
  'CRM_ADMIN',
  'DEVELOPER',
  'ROOT',
  'SOVEREIGN_ROOT'
]);

const CRM_TEAM_COMMAND_ROLE_TOKENS = Object.freeze([
  'SALES_MANAGER',
  'CRM_MANAGER',
  'REVOPS',
  'REVENUE_OPERATIONS',
  'TEAM_LEAD',
  'MANAGER',
  'COMMERCIAL_MANAGER'
]);

const CRM_EMPLOYEE_ROLE_WORKSPACES = Object.freeze({
  SALES_CONSULTANT: ['home', 'leads', 'contacts', 'accounts', 'deals', 'tasks', 'meetings'],
  SALES_REP: ['home', 'leads', 'contacts', 'accounts', 'deals', 'tasks', 'meetings'],
  SDR: ['home', 'leads', 'contacts', 'tasks', 'meetings'],
  BDR: ['home', 'leads', 'contacts', 'tasks', 'meetings'],
  ACCOUNT_EXECUTIVE: ['home', 'leads', 'contacts', 'accounts', 'deals', 'tasks', 'meetings'],
  ACCOUNT_MANAGER: ['home', 'contacts', 'accounts', 'deals', 'tasks', 'meetings'],
  CUSTOMER_SUCCESS: ['home', 'contacts', 'accounts', 'tasks', 'meetings'],
  SUPPORT_AGENT: ['home', 'contacts', 'accounts', 'tasks', 'meetings'],
  USER: ['home', 'leads', 'contacts', 'tasks', 'meetings'],
  EMPLOYEE: ['home', 'leads', 'contacts', 'tasks', 'meetings']
});

const CRM_EMPLOYEE_DAILY_WORKSPACE_CARDS = Object.freeze([
  { id: 'tasks', label: 'My Open Tasks', icon: CheckSquare, columns: ['Subject', 'Due Date', 'Status'] },
  { id: 'meetings', label: 'My Meetings', icon: CalendarDays, columns: ['Title', 'From', 'To'] },
  { id: 'leads', label: "Today's Leads", icon: Database, columns: ['Lead', 'Company', 'Status'] },
  { id: 'deals', label: 'My Deals Closing This Month', icon: Target, columns: ['Deal', 'Stage', 'Value'] }
]);

const CRM_DISRUPTION_FEATURES = Object.freeze([
  {
    id: 'proofgraph',
    label: 'ProofGraph Revenue Memory',
    icon: Fingerprint,
    patentSignal: 'Every commercial move linked to evidence anchors'
  },
  {
    id: 'twin',
    label: 'Autonomous Revenue Twin',
    icon: Activity,
    patentSignal: 'Live source posture controls forecast confidence'
  },
  {
    id: 'judge',
    label: 'Source Route Judge',
    icon: Shield,
    patentSignal: 'Bad records gated before pipeline contamination'
  },
  {
    id: 'autopilot',
    label: 'Governed Next Action Autopilot',
    icon: Sparkles,
    patentSignal: 'AI action allowed only when provenance is strong'
  }
]);

const CRM_RECORD_COLUMNS = Object.freeze({
  leads: ['Name', 'Company', 'Email', 'Phone', 'Source'],
  contacts: ['Name', 'Company', 'Email', 'Phone', 'Source'],
  accounts: ['Account', 'Industry', 'Owner', 'Status', 'Source'],
  deals: ['Deal', 'Account', 'Stage', 'Value', 'Source'],
  tasks: ['Task', 'Owner', 'Due', 'Status', 'Source'],
  meetings: ['Meeting', 'Account', 'Date', 'Status', 'Source'],
  evidence: ['Evidence', 'Type', 'Owner', 'Status', 'Source'],
  connectors: ['Connector', 'Category', 'Status', 'Last Sync', 'Source']
});

const PIPELINE_STAGE_RULES = Object.freeze([
  {
    stage: 'Intake',
    headline: 'Capture',
    aliases: ['Prospecting', 'Lead Generation', 'Capture', 'New', 'NEW'],
    probability: 10,
    lane: 'primary',
    tone: 'blue',
    clause: 'Source, identity and consent basis captured',
    proof: 'Lead source receipt'
  },
  {
    stage: 'Contact',
    headline: 'Reach',
    aliases: ['Contacted', 'CONTACTED', 'Open', 'OPEN', 'Engage', 'Conversation'],
    probability: 25,
    lane: 'primary',
    tone: 'cyan',
    clause: 'First touch, intent and response path recorded',
    proof: 'Engagement marker'
  },
  {
    stage: 'Qualify',
    headline: 'Fit',
    aliases: ['Lead Qualification', 'Qualification', 'Sales Qualified', 'Qualified', 'QUALIFIED', 'Fit'],
    probability: 40,
    lane: 'primary',
    tone: 'violet',
    clause: 'BANT, authority and FICA identity posture',
    proof: 'Buyer authority marker'
  },
  {
    stage: 'Discover',
    headline: 'Needs',
    aliases: ['Needs Analysis', 'Discovery', 'Needs Assessment', 'Needs'],
    probability: 55,
    lane: 'primary',
    tone: 'teal',
    clause: 'Pain, goals and buying criteria documented',
    proof: 'Discovery receipt'
  },
  {
    stage: 'Propose',
    headline: 'Offer',
    aliases: ['Demo / Presentation', 'Demo', 'Presentation', 'Solution Fit', 'Proof of Concept', 'Proposal', 'Offer', 'Commercial Proposal'],
    probability: 70,
    lane: 'primary',
    tone: 'gold',
    clause: 'Solution fit, pricing and value case evidence',
    proof: 'Offer pack hash'
  },
  {
    stage: 'Negotiate',
    headline: 'Commit',
    aliases: ['Negotiation', 'Negotiation and Commitment', 'Commitment'],
    probability: 85,
    lane: 'primary',
    tone: 'amber',
    clause: 'Objections, redlines and authority trail',
    proof: 'Clause variance log'
  },
  {
    stage: 'Convert',
    headline: 'Outcome',
    aliases: ['Closed Won / Lost', 'Closed', 'Closed Won', 'Closed Lost', 'Won', 'Lost', 'Convert', 'Outcome'],
    probability: 100,
    lane: 'primary',
    tone: 'green',
    clause: 'Final outcome recorded for forecast integrity',
    proof: 'Outcome receipt'
  },
  {
    stage: 'Compliance Gate',
    aliases: ['Compliance Review'],
    probability: 88,
    lane: 'sovereign',
    tone: 'gold',
    clause: 'POPIA / FICA / SOC2 clearance',
    proof: 'Disclosure pack'
  },
  {
    stage: 'Contracting',
    aliases: ['Contract', 'Legal Review'],
    probability: 96,
    lane: 'sovereign',
    tone: 'violet',
    clause: 'Clause-bound commercial agreement',
    proof: 'Contract hash'
  },
  {
    stage: 'Onboarding',
    aliases: ['Implementation', 'Activation'],
    probability: 100,
    lane: 'sovereign',
    tone: 'cyan',
    clause: 'Activation and handover workflow',
    proof: 'Handover receipt'
  },
  {
    stage: 'Renewal / Expansion',
    aliases: ['Renewal', 'Expansion', 'Post-purchase', 'Follow-up'],
    probability: 100,
    lane: 'sovereign',
    tone: 'green',
    clause: 'Value realisation and expansion motion',
    proof: 'Retention telemetry'
  }
]);

const COMPLIANCE_BADGES = Object.freeze(['POPIA', 'FICA', 'GDPR', 'SOC2', 'Audit']);

/**
 * @function buildCrmFallbackThemeRuntime
 * @description Builds a safe fallback visual token contract before the Wilsy OS theme runtime hydrates.
 * @returns {Object} Fallback theme runtime.
 * @collaboration Prevents CRM from rendering hardcoded theme colors while Account Command Center runtime loads.
 */
function buildCrmFallbackThemeRuntime() {
  return {
    themeId: 'crm_revenue_pulse',
    effectiveMode: 'night',
    resolvedMode: 'night',
    accent: '#E8C670',
    secondary: '#17BDF2',
    highlight: '#FFF0A4',
    live: '#40F2B2',
    brightText: '#FFFFFF',
    softText: 'rgba(255,255,255,0.72)',
    mutedText: 'rgba(255,255,255,0.48)',
    overlay: 'rgba(15,18,28,0.74)',
    panelBackground: 'rgba(8,12,20,0.94)',
    headerBackground: 'linear-gradient(135deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018)), rgba(4,7,13,0.92)',
    cardBackground: 'rgba(11,16,26,0.82)',
    railBackground: 'rgba(8,12,20,0.96)',
    commandBackground: 'linear-gradient(135deg, #D4AF37, #FFF0A4)',
    shadow: '0 24px 70px rgba(0,0,0,0.54)',
    cssVars: {}
  };
}

/**
 * @function normalizeCrmThemeRuntimePacket
 * @description Normalizes a Wilsy OS theme runtime packet into CRM semantic variables.
 * @param {Object} packet - Theme runtime packet.
 * @param {Object} fallback - Fallback token packet.
 * @returns {Object} Normalized token packet.
 * @collaboration Keeps CRM synchronized with Account Command Center, ExecutiveDashboard and future dashboard runtimes.
 */
function normalizeCrmThemeRuntimePacket(packet = {}, fallback = buildCrmFallbackThemeRuntime()) {
  const source = packet?.tokens || packet?.runtime || packet || {};
  const cssVars = source.cssVars || packet?.cssVars || fallback.cssVars || {};

  return {
    ...fallback,
    ...source,
    cssVars,
    themeId: source.themeId || packet.themeId || fallback.themeId,
    effectiveMode: source.effectiveMode || packet.mode || fallback.effectiveMode,
    resolvedMode: source.resolvedMode || packet.resolvedMode || fallback.resolvedMode,
    accent: source.accent || cssVars['--wilsy-accent'] || cssVars['--crm-accent'] || fallback.accent,
    secondary: source.secondary || cssVars['--wilsy-secondary'] || cssVars['--crm-accent-2'] || fallback.secondary,
    highlight: source.highlight || cssVars['--wilsy-highlight'] || fallback.highlight,
    live: source.live || cssVars['--wilsy-live'] || cssVars['--crm-accent-3'] || fallback.live,
    brightText: source.brightText || cssVars['--wilsy-text'] || fallback.brightText,
    softText: source.softText || cssVars['--wilsy-soft-text'] || fallback.softText,
    mutedText: source.mutedText || cssVars['--wilsy-muted'] || fallback.mutedText,
    overlay: source.overlay || cssVars['--wilsy-overlay'] || fallback.overlay,
    panelBackground: source.panelBackground || cssVars['--wilsy-panel'] || cssVars['--crm-surface'] || fallback.panelBackground,
    headerBackground: source.headerBackground || fallback.headerBackground,
    cardBackground: source.cardBackground || cssVars['--wilsy-card'] || cssVars['--crm-card'] || fallback.cardBackground,
    railBackground: source.railBackground || cssVars['--wilsy-rail'] || fallback.railBackground,
    commandBackground: source.commandBackground || fallback.commandBackground,
    shadow: source.shadow || fallback.shadow
  };
}

/**
 * @function buildCrmThemeStyleVars
 * @description Converts the active Wilsy OS theme runtime packet into CRM shell CSS variables.
 * @param {Object} themeRuntime - Active theme runtime packet.
 * @param {Object} tenantIdentity - Tenant identity colors.
 * @returns {Object} CSS variable map.
 * @collaboration Lets CRM consume OS theme skins without hardcoded visual drift.
 */
function buildCrmThemeStyleVars(themeRuntime = buildCrmFallbackThemeRuntime(), tenantIdentity = {}) {
  return {
    ...themeRuntime.cssVars,
    '--crm-black': themeRuntime.cssVars?.['--crm-bg'] || themeRuntime.cssVars?.['--wilsy-bg'] || '#02040A',
    '--crm-ink': themeRuntime.cssVars?.['--wilsy-surface'] || '#070A12',
    '--crm-panel': themeRuntime.panelBackground,
    '--crm-card': themeRuntime.cardBackground,
    '--crm-glass': themeRuntime.overlay,
    '--crm-gold': themeRuntime.accent || tenantIdentity.primaryColor || '#E8C670',
    '--crm-gold-strong': themeRuntime.highlight || tenantIdentity.accentColor || '#FFF0A4',
    '--crm-cyan': themeRuntime.live || themeRuntime.secondary || tenantIdentity.secondaryColor || '#1EEBCB',
    '--crm-text': themeRuntime.brightText || '#FFFFFF',
    '--crm-soft': themeRuntime.softText || 'rgba(255,255,255,0.72)',
    '--crm-muted': themeRuntime.mutedText || 'rgba(255,255,255,0.48)',
    '--crm-command-bg': themeRuntime.commandBackground,
    '--crm-header-bg': themeRuntime.headerBackground,
    '--crm-rail-bg': themeRuntime.railBackground,
    '--crm-shadow': themeRuntime.shadow,
    '--crm-tenant-primary': tenantIdentity.primaryColor || themeRuntime.accent || '#D4AF37',
    '--crm-tenant-secondary': tenantIdentity.secondaryColor || themeRuntime.secondary || '#1EEBCB',
    '--crm-tenant-accent': tenantIdentity.accentColor || themeRuntime.highlight || '#F6E27A'
  };
}

/**
 * @function resolveCrmGlobalThemeRuntime
 * @description Resolves CRM theme tokens directly from the Wilsy OS global theme engine.
 * @param {Object} overrides - Optional theme and mode overrides.
 * @param {Object} previous - Previous theme runtime.
 * @returns {Object} Normalized CRM theme runtime.
 * @collaboration Binds CRM to Account Command Center operating skins without local hardcoded theme drift.
 */
function resolveCrmGlobalThemeRuntime(overrides = {}, previous = buildCrmFallbackThemeRuntime()) {
  const storedRuntime = readStoredWilsyThemeRuntime({
    themeId: overrides.themeId || previous.themeId || 'crm_revenue_pulse',
    mode: overrides.mode || previous.effectiveMode || 'night'
  });

  const themeId = overrides.themeId || storedRuntime.themeId || previous.themeId || 'crm_revenue_pulse';
  const mode = overrides.mode || storedRuntime.mode || storedRuntime.effectiveMode || previous.effectiveMode || 'night';

  const selectedTheme = WILSY_OPERATING_SKINS.find(theme => theme.id === themeId)
    || WILSY_OPERATING_SKINS[0]
    || { id: themeId, label: themeId };

  const resolvedMode = resolveWilsyAutoMode(mode);
  const visualTokens = buildWilsyVisualTokens(selectedTheme, resolvedMode, {
    ...storedRuntime,
    effectiveMode: mode
  });

  return normalizeCrmThemeRuntimePacket(
    {
      ...visualTokens,
      themeId,
      mode,
      effectiveMode: mode,
      resolvedMode
    },
    previous
  );
}


/**
 * @function safeText
 * @description Converts unknown values into stable display text without inventing business facts.
 * @param {*} value - Candidate value.
 * @param {string} fallback - Fallback display value.
 * @returns {string} Safe text.
 * @collaboration Keeps CRM labels stable while preserving honest source-empty states.
 */
function safeText(value, fallback = '—') {
  if (value === null || value === undefined) return fallback;
  const text = String(value).trim();
  return text || fallback;
}

/**
 * @function toNumber
 * @description Converts unknown numeric input into a safe finite number.
 * @param {*} value - Candidate numeric value.
 * @returns {number} Safe number.
 * @collaboration Protects pipeline calculations from partial API payloads.
 */
function toNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : 0;
}

/**
 * @function formatMoney
 * @description Formats CRM money values as South African Rand.
 * @param {*} value - Candidate numeric value.
 * @returns {string} Money display.
 * @collaboration Keeps revenue telemetry aligned with Wilsy OS South African operating context.
 */
function formatMoney(value) {
  const numeric = toNumber(value);
  return `R ${numeric.toLocaleString('en-ZA', { maximumFractionDigits: 0 })}`;
}

/**
 * @function getStoredValue
 * @description Reads a localStorage string safely.
 * @param {string} key - Storage key.
 * @param {string} fallback - Fallback value.
 * @returns {string} Stored value or fallback.
 * @collaboration Lets CRM hydrate known identity hints without fragile global assumptions.
 */
function getStoredValue(key, fallback = '') {
  try {
    if (typeof window === 'undefined') return fallback;
    return window.localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

/**
 * @function readStoredJson
 * @description Reads a localStorage JSON object safely.
 * @param {string} key - Storage key.
 * @returns {Object} Parsed object or empty object.
 * @collaboration Lets CRM consume existing auth cache without crashing restricted browsers.
 */
function readStoredJson(key) {
  try {
    const raw = getStoredValue(key, '');
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

/**
 * @function resolveImageSource
 * @description Resolves a safe browser image source with logo fallback.
 * @param {*} value - Candidate logo value.
 * @returns {string} Safe image source.
 * @collaboration Prevents broken tenant logos from damaging the chrome.
 */
function resolveImageSource(value) {
  const text = safeText(value, '');
  if (!text) return wilsyLogo;
  if (text.startsWith('http') || text.startsWith('data:') || text.startsWith('/') || text.startsWith('blob:')) return text;
  return wilsyLogo;
}

/**
 * @function buildInitials
 * @description Builds stable initials for identity fallback.
 * @param {string} value - Candidate identity name.
 * @returns {string} Initials.
 * @collaboration Keeps operator chrome stable even when profile images are unavailable.
 */
function buildInitials(value = '') {
  const parts = String(value || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'WK';
  return parts.slice(0, 2).map(part => part.charAt(0).toUpperCase()).join('');
}

/**
 * @function normalizeRecord
 * @description Normalizes one CRM record from backend-shaped payloads.
 * @param {Object} record - Source record.
 * @param {string} collection - Collection name.
 * @param {number} index - Source index.
 * @returns {Object} Normalized CRM record.
 * @collaboration Allows service routes to evolve without duplicating mapping logic in visual components.
 */
function normalizeRecord(record = {}, collection = 'records', index = 0) {
  const id = record._id || record.id || record.uuid || record.recordId || `${collection}-source-${index}`;
  const value = toNumber(record.value || record.amount || record.dealValue || record.weightedValue || record.totalValue);
  const stage = safeText(record.stage || record.pipelineStage || record.status, 'Unstaged');

  return {
    id,
    collection,
    name: safeText(record.name || record.fullName || record.title || record.subject || record.companyName || record.accountName, 'Unnamed source record'),
    company: safeText(record.company || record.companyName || record.account || record.accountName || record.organization, '—'),
    email: safeText(record.email || record.primaryEmail || record.contactEmail, '—'),
    phone: safeText(record.phone || record.mobile || record.telephone || record.primaryPhone, '—'),
    owner: safeText(record.owner || record.ownerName || record.assignedTo || record.createdBy, '—'),
    status: safeText(record.status || record.sourceStatus || record.state || record.readiness, 'Source received'),
    stage,
    value,
    type: safeText(record.type || record.category || record.kind, collection),
    industry: safeText(record.industry || record.sector || record.market, '—'),
    dueDate: safeText(record.dueDate || record.date || record.meetingDate || record.scheduledFor, '—'),
    source: safeText(record.source || record.sourceSystem || record.connector || record.origin, 'Wilsy CRM API'),
    raw: record
  };
}

/**
 * @function normalizeCollectionPayload
 * @description Converts a backend response payload into normalized CRM records.
 * @param {*} payload - Backend payload.
 * @param {string} collection - Collection name.
 * @returns {Array<Object>} Normalized records.
 * @collaboration Keeps every workspace source-led and removes fake UI rows.
 */
function normalizeCollectionPayload(payload, collection) {
  const candidates = [
    payload?.data,
    payload?.records,
    payload?.items,
    payload?.results,
    payload?.[collection],
    payload
  ];

  const list = candidates.find(candidate => Array.isArray(candidate)) || [];
  return list.map((record, index) => normalizeRecord(record, collection, index));
}

/**
 * @function buildAuthHeaders
 * @description Builds tenant-safe CRM request headers.
 * @param {string} tenantId - Active tenant id.
 * @returns {Object} Request headers.
 * @collaboration Keeps CRM API calls aligned with Wilsy OS tenant guard expectations.
 */
function buildAuthHeaders(tenantId) {
  const token = getStoredValue('token', '') || getStoredValue('authToken', '') || getStoredValue('wilsyAuthToken', '');
  const headers = {
    'Content-Type': 'application/json',
    'X-Tenant-Id': tenantId || 'MASTER',
    'X-Wilsy-Tenant-ID': tenantId || 'MASTER'
  };

  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

/**
 * @function fetchCrmCollection
 * @description Fetches one CRM source collection.
 * @param {string} collection - Collection id.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal.
 * @returns {Promise<Object>} Source result.
 * @collaboration Preserves a no-fake-data dashboard contract while surfacing source gaps clearly.
 */
async function fetchCrmCollection(collection, tenantId, signal) {
  const endpoint = CRM_ENDPOINTS[collection];
  if (!endpoint) return { collection, ok: false, records: [], error: 'Endpoint not configured' };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'GET',
      headers: buildAuthHeaders(tenantId),
      signal
    });

    if (!response.ok) {
      return { collection, ok: false, records: [], status: response.status, error: `HTTP ${response.status}` };
    }

    const payload = await response.json();
    return {
      collection,
      ok: true,
      records: normalizeCollectionPayload(payload, collection),
      sourcePosture: payload?.sourcePosture || payload?.meta?.sourcePosture || null,
      status: response.status,
      error: null
    };
  } catch (error) {
    if (error?.name === 'AbortError') return { collection, ok: false, records: [], aborted: true, error: 'Aborted' };
    return { collection, ok: false, records: [], error: error?.message || 'Source request failed' };
  }
}


/* WILSY_P60K5K6_SOURCE_POSTURE_FUNCTION_LOCK */
const WILSY_P60K5K6_SOURCE_POSTURE_COOLDOWN_MS = 30000;
const wilsyP60K5K6SourcePostureFunctionCache = {
  key: '',
  expiresAt: 0,
  payload: null,
  promise: null,
};

/**
 * @function buildWilsyP60K5K6SourcePostureFunctionKey
 * @description Builds a stable source-posture function cache key that ignores volatile generatedAt churn.
 * @returns {string} Stable source-posture function cache key.
 * @collaboration CRMDashboard, fetchCrmSourcePosture, source posture telemetry, and backend request storm prevention.
 */
function buildWilsyP60K5K6SourcePostureFunctionKey() {
  return String(CRM_SOURCE_POSTURE_ENDPOINT || '/api/crm/live/source-posture');
}

/**
 * @function cloneWilsyP60K5K6SourcePosturePayload
 * @description Clones source-posture payloads before returning cached data to React state.
 * @param {Object} payload - Cached source-posture payload.
 * @returns {Object} Cloned payload.
 * @collaboration CRMDashboard source posture state, React render safety, and request-loop cache discipline.
 */
function cloneWilsyP60K5K6SourcePosturePayload(payload = {}) {
  try {
    return JSON.parse(JSON.stringify(payload || {}));
  } catch (error) {
    return payload || {};
  }
}

/**
 * @function fetchCrmSourcePosture
 * @description Fetches CRM source-posture telemetry through a function-level cooldown so repeated renders cannot spam the backend.
 * @param {AbortSignal} signal - Abort signal for cancelling source-posture fetches.
 * @returns {Promise<Object>} Source-posture payload.
 * @collaboration CRM live source telemetry, source-posture request loop guard, backend SLA protection, and Screen Two stability.
 */
async function fetchCrmSourcePosture(tenantId, signal) {
  const cacheKey = buildWilsyP60K5K6SourcePostureFunctionKey();
  const now = Date.now();

  if (
    wilsyP60K5K6SourcePostureFunctionCache.key === cacheKey &&
    wilsyP60K5K6SourcePostureFunctionCache.payload &&
    wilsyP60K5K6SourcePostureFunctionCache.expiresAt > now
  ) {
    return cloneWilsyP60K5K6SourcePosturePayload(wilsyP60K5K6SourcePostureFunctionCache.payload);
  }

  if (
    wilsyP60K5K6SourcePostureFunctionCache.key === cacheKey &&
    wilsyP60K5K6SourcePostureFunctionCache.promise
  ) {
    const payload = await wilsyP60K5K6SourcePostureFunctionCache.promise;
    return cloneWilsyP60K5K6SourcePosturePayload(payload);
  }

  wilsyP60K5K6SourcePostureFunctionCache.key = cacheKey;
  wilsyP60K5K6SourcePostureFunctionCache.promise = fetchCrmSourcePostureUncached(...arguments)
    .then((payload) => {
      wilsyP60K5K6SourcePostureFunctionCache.payload = payload || {};
      wilsyP60K5K6SourcePostureFunctionCache.expiresAt = Date.now() + WILSY_P60K5K6_SOURCE_POSTURE_COOLDOWN_MS;
      return wilsyP60K5K6SourcePostureFunctionCache.payload;
    })
    .catch((error) => {
      wilsyP60K5K6SourcePostureFunctionCache.payload = null;
      wilsyP60K5K6SourcePostureFunctionCache.expiresAt = 0;
      throw error;
    })
    .finally(() => {
      wilsyP60K5K6SourcePostureFunctionCache.promise = null;
    });

  const payload = await wilsyP60K5K6SourcePostureFunctionCache.promise;
  return cloneWilsyP60K5K6SourcePosturePayload(payload);
}


/**
 * @function fetchCrmSourcePostureUncached
 * @description Fetches live CRM source posture from the backend.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal.
 * @returns {Promise<Object|null>} Source posture.
 * @collaboration Powers Root Hash and source-route counters from the live backend.
 */

/**
 * @function fetchCrmRouteSurface
 * @description Fetches dynamic CRM route-surface telemetry from the live backend registry.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal.
 * @returns {Promise<Object|null>} Dynamic route-surface payload.
 * @collaboration CRM header telemetry, production route registry, no-placeholder readiness posture.
 */


/* R91K148_FETCH_SOURCEGUIDE_CONTRACT_BRIDGE */

/**
 * @function collectWilsyR91K148FabricObjects
 * @description Collects nested Source Guide response objects so the fetch bridge can find the backend fabric contract.
 * @collaboration Keeps CRM Pipeline Fabric rendering from the live /api/crm/live/source-guide contract instead of stale fallback state.
 */
function collectWilsyR91K148FabricObjects(source, depth = 0, candidates = []) {
  if (!source || typeof source !== 'object' || Array.isArray(source) || depth > 6) {
    return candidates;
  }

  candidates.push(source);

  for (const key of [
    'sourceSignatureFabric',
    'guide',
    'data',
    'sourceGuide',
    'result',
    'payload',
    'crmSourceGuide',
    'liveSourceGuide',
    'sourceGuidePayload',
    'body',
  ]) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      collectWilsyR91K148FabricObjects(source[key], depth + 1, candidates);
    }
  }

  if (depth < 2) {
    for (const value of Object.values(source)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        collectWilsyR91K148FabricObjects(value, depth + 1, candidates);
      }
    }
  }

  return candidates;
}

/**
 * @function resolveWilsyR91K148FabricContract
 * @description Resolves the R91K144 backend sourceSignatureFabric contract from any Source Guide response envelope.
 * @collaboration Bridges backend-owned Source-to-Signature Fabric truth into the frontend model without placeholders.
 */
function resolveWilsyR91K148FabricContract(...sources) {
  for (const source of sources) {
    const candidates = collectWilsyR91K148FabricObjects(source);

    for (const candidate of candidates) {
      if (
        candidate &&
        candidate.contractVersion === 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT'
      ) {
        return candidate;
      }

      if (
        candidate?.sourceSignatureFabric &&
        candidate.sourceSignatureFabric.contractVersion === 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT'
      ) {
        return candidate.sourceSignatureFabric;
      }
    }
  }

  return null;
}

/**
 * @function normalizeWilsyR91K148SourceGuideFetchPayload
 * @description Returns the real Source Guide object with backend sourceSignatureFabric attached from the fetch response envelope.
 * @collaboration Ensures fetchCrmSourceGuide hands R91K139 Fabric and root receipt surfaces live backend contract state.
 */
function normalizeWilsyR91K148SourceGuideFetchPayload(sourceGuidePayload) {
  const sourceSignatureFabric = resolveWilsyR91K148FabricContract(sourceGuidePayload);

  const guideCandidate =
    sourceGuidePayload?.guide ||
    sourceGuidePayload?.sourceGuide ||
    sourceGuidePayload?.data?.guide ||
    sourceGuidePayload?.data?.sourceGuide ||
    sourceGuidePayload?.result?.guide ||
    sourceGuidePayload?.payload?.guide ||
    sourceGuidePayload;

  if (!guideCandidate || typeof guideCandidate !== 'object' || Array.isArray(guideCandidate)) {
    return guideCandidate || null;
  }

  if (!sourceSignatureFabric) {
    return guideCandidate;
  }

  return {
    ...guideCandidate,
    sourceSignatureFabric,
    __r91k148LiveBackendFabricBridge: true,
  };
}


/**
 * @function fetchCrmSourceGuide
 * @description Fetches backend Source Posture Guide telemetry for readiness, Wilsy AI mode, and operator actions.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal.
 * @returns {Promise<Object|null>} Source guide payload or null.
 * @collaboration CRM dashboard readiness, Source Posture Guide, Wilsy AI operating directives.
 */
async function fetchCrmSourceGuide(tenantId, signal) {
  const liveUrl = `${CRM_SOURCE_GUIDE_ENDPOINT}${CRM_SOURCE_GUIDE_ENDPOINT.includes('?') ? '&' : '?'}r91k149LiveTs=${Date.now()}`;

  const response = await fetch(liveUrl, {
    method: 'GET',
    signal,
    cache: 'no-store',
    headers: {
      Accept: 'application/json',
      'Cache-Control': 'no-cache',
      ...(tenantId ? { 'X-Tenant-Id': tenantId } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`CRM_SOURCE_GUIDE_HTTP_${response.status}`);
  }

  const sourceGuidePayload = await response.json();
  const normalizedSourceGuide = normalizeWilsyR91K148SourceGuideFetchPayload(sourceGuidePayload);

  if (typeof window !== 'undefined') {
    window.__WILSY_R91K149_SOURCE_GUIDE_PROOF__ = {
      fetchedAt: new Date().toISOString(),
      endpoint: liveUrl,
      topKicker: sourceGuidePayload?.sourceSignatureFabric?.kicker,
      guideKicker: sourceGuidePayload?.guide?.sourceSignatureFabric?.kicker,
      normalizedKicker: normalizedSourceGuide?.sourceSignatureFabric?.kicker,
      normalizedHeadline: normalizedSourceGuide?.sourceSignatureFabric?.headline,
      normalizedPostureLine: normalizedSourceGuide?.sourceSignatureFabric?.postureLine,
      normalizedReceipt: normalizedSourceGuide?.sourceSignatureFabric?.receipt,
      normalizedBridge: normalizedSourceGuide?.__r91k149LiveBackendFabricBridge,
    };
  }

  return normalizedSourceGuide;
} /* R91K149_FORCE_SOURCEGUIDE_FETCH_CONTRACT */

/**
 * @function fetchCrmRouteSurface
 * @description Fetches dynamic CRM route-surface telemetry for header route truth and Source Posture Guide enrichment.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal for cancelling route-surface fetches.
 * @returns {Promise<Object|null>} Route-surface payload or null when unavailable.
 * @collaboration CRM header telemetry, dynamic route registry, Source Posture Guide readiness.
 */
async function fetchCrmRouteSurface(tenantId, signal) {
  const response = await fetch(CRM_ROUTE_SURFACE_ENDPOINT, {
    headers: { 'X-Tenant-Id': tenantId },
    signal
  });

  if (!response.ok) {
    return null;
  }

  return response.json();
}


/**
 * @function resolveWilsyR91K110RouteSurfaceLabel
 * @description Resolves the CRM header route-surface label from dynamic backend route telemetry.
 * @param {Object} sourcePosture - Source posture payload.
 * @returns {string} Header-safe route-surface label.
 * @collaboration CRM header telemetry, dynamic route registry, production no-placeholder posture.
 */
function resolveWilsyR91K110RouteSurfaceLabel(sourcePosture = {}) {
  const routeSurfaceCount = toNumber(sourcePosture?.routeSurface?.crmRelatedRoutes);

  if (routeSurfaceCount > 0) {
    return `${routeSurfaceCount} CRM routes`;
  }

  const connectedSources = toNumber(sourcePosture.connected);
  const totalSources = toNumber(sourcePosture.total);

  return `${connectedSources}/${Math.max(totalSources, connectedSources)} CRM sources`;
}

/**
 * @function fetchCrmSourcePosture
 * @description Fetches live CRM source-posture telemetry for the active tenant without request-loop caching.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal for cancelling source-posture fetches.
 * @returns {Promise<Object|null>} Source posture payload or null when unavailable.
 * @collaboration CRM live source telemetry, route-surface enrichment, production header truth.
 */
async function fetchCrmSourcePostureUncached(tenantId, signal) {
  try {
    const response = await fetch(`${API_BASE}${CRM_SOURCE_POSTURE_ENDPOINT}`, {
      method: 'GET',
      headers: buildAuthHeaders(tenantId),
      signal
    });

    if (!response.ok) return null;
    return response.json();
  } catch (error) {
    if (error?.name === 'AbortError') return null;
    return null;
  }
}

/**
 * @function createEmptySnapshot
 * @description Builds a zero-record source snapshot.
 * @returns {Object} Empty CRM snapshot.
 * @collaboration Gives CRM an honest baseline before source hydration.
 */
function createEmptySnapshot() {
  return {
    leads: [],
    contacts: [],
    accounts: [],
    deals: [],
    tasks: [],
    meetings: [],
    evidence: [],
    connectors: [],
    sourcePosture: {
      connected: 0,
      total: Object.keys(CRM_ENDPOINTS).length,
      errors: [],
      loading: false,
      lastSync: null
    }
  };
}

/**
 * @function buildCrmSnapshot
 * @description Builds the CRM snapshot from source route results.
 * @param {Array<Object>} results - Collection fetch results.
 * @returns {Object} CRM snapshot.
 * @collaboration Creates one source-of-truth data object for all cards, records and telemetry strips.
 */
function buildCrmSnapshot(results = []) {
  const snapshot = createEmptySnapshot();
  const errors = [];
  const backendPosture = results.map(result => result?.sourcePosture).find(Boolean) || null;

  results.forEach(result => {
    if (!result || !result.collection) return;
    snapshot[result.collection] = Array.isArray(result.records) ? result.records : [];

    if (result.ok) {
      snapshot.sourcePosture.connected += 1;
    } else if (!result.aborted) {
      errors.push({
        collection: result.collection,
        error: result.error || 'Unavailable source',
        status: result.status || null
      });
    }
  });

  snapshot.sourcePosture.errors = errors;
  if (backendPosture) {
    snapshot.sourcePosture.connected = Number(backendPosture.connectedRoutes ?? snapshot.sourcePosture.connected);
    snapshot.sourcePosture.total = Number(backendPosture.totalRoutes ?? snapshot.sourcePosture.total);
    snapshot.sourcePosture.rootHash = backendPosture.rootHash || null;
    snapshot.sourcePosture.rootHashShort = backendPosture.rootHashShort || null;
    snapshot.sourcePosture.sources = backendPosture.sources || [];
    snapshot.sourcePosture.sourceGaps = backendPosture.sourceGaps || [];
    snapshot.sourcePosture.generatedAt = backendPosture.generatedAt || null;
  }
  snapshot.sourcePosture.lastSync = new Date().toISOString();
  snapshot.sourcePosture.loading = false;
  return snapshot;
}

/**
 * @function calculateReadinessScore
 * @description Calculates CRM readiness from source connectivity and captured records.
 * @param {Object} snapshot - CRM snapshot.
 * @returns {number} Readiness score.
 * @collaboration Produces an investor-visible posture score without hardcoding false maturity.
 */
function calculateReadinessScore(snapshot) {
  const totalSources = snapshot.sourcePosture.total || Object.keys(CRM_ENDPOINTS).length;
  const connectedRatio = totalSources ? snapshot.sourcePosture.connected / totalSources : 0;
  const dataAnchors = [
    snapshot.leads.length > 0,
    snapshot.contacts.length > 0,
    snapshot.accounts.length > 0,
    snapshot.deals.length > 0,
    snapshot.evidence.length > 0
  ].filter(Boolean).length / 5;

  return Math.round(Math.min(100, (connectedRatio * 70) + (dataAnchors * 30)));
}

/**
 * @function buildPipelineStages
 * @description Builds weighted pipeline stage summaries from live deals.
 * @param {Array<Object>} deals - Normalized deal records.
 * @returns {Array<Object>} Pipeline stages.
 * @collaboration Turns source deal records into a compliance-aware revenue strip.
 */
function buildPipelineStages(deals = []) {
  return PIPELINE_STAGE_RULES.map(rule => {
    const stageAliases = [rule.stage, ...(rule.aliases || [])]
      .map(alias => String(alias || '').toLowerCase());

    const stageDeals = deals.filter(deal => stageAliases.includes(String(deal.stage || '').toLowerCase()));
    const rawValue = stageDeals.reduce((sum, deal) => sum + toNumber(deal.value), 0);
    const weightedValue = Math.round(rawValue * (rule.probability / 100));

    return {
      ...rule,
      count: stageDeals.length,
      rawValue,
      weightedValue
    };
  });
}

/**
 * @function buildPipelineTotal
 * @description Calculates total weighted value across pipeline stages.
 * @param {Array<Object>} stages - Pipeline stages.
 * @returns {number} Total weighted value.
 * @collaboration Keeps top metrics and stage strip aligned.
 */
function buildPipelineTotal(stages = []) {
  return stages.reduce((sum, stage) => sum + toNumber(stage.weightedValue), 0);
}

/**
 * @function buildCrmWorkspaceTelemetry
 * @description Builds compact workspace cards from live CRM collections.
 * @param {Object} snapshot - CRM snapshot.
 * @param {Array<Object>} workspaces - Allowed CRM workspaces.
 * @returns {Array<Object>} Workspace telemetry cards.
 * @collaboration Converts the CRM home from a long promotional page into an operating-system module launcher.
 */
function buildCrmWorkspaceTelemetry(snapshot = createEmptySnapshot(), workspaces = CRM_WORKSPACES) {
  const posture = snapshot.sourcePosture || {};
  const connectedRoutes = toNumber(posture.connected);
  const totalRoutes = toNumber(posture.total);

  return workspaces
    .filter(workspace => workspace.id !== 'home')
    .map(workspace => {
      const records = Array.isArray(snapshot[workspace.id]) ? snapshot[workspace.id] : [];
      const routeReady = workspace.id === 'connectors'
        ? connectedRoutes > 0
        : totalRoutes > 0 && connectedRoutes === totalRoutes;

      return {
        ...workspace,
        count: records.length,
        status: records.length ? 'LIVE' : (routeReady ? 'READY' : 'GATED'),
        detail: workspace.id === 'leads'
          ? 'Intake to Convert'
          : workspace.id === 'deals'
            ? 'Pipeline stages aligned'
            : workspace.id === 'evidence'
              ? 'Proof anchors'
              : `${workspace.group} workspace`,
        source: routeReady ? `${connectedRoutes}/${Math.max(totalRoutes, connectedRoutes)} routes` : 'Source waiting'
      };
    });
}

/**
 * @function buildCrmCreateWorkspaceRail
 * @description Builds create-workspace module rail entries from live CRM state.
 * @param {Object} snapshot - CRM snapshot.
 * @param {Array<Object>} workspaces - Allowed CRM workspaces.
 * @returns {Array<Object>} Create workspace rail entries.
 * @collaboration Keeps create actions module-aware without inventing records or disconnected forms.
 */
function buildCrmCreateWorkspaceRail(snapshot = createEmptySnapshot(), workspaces = CRM_WORKSPACES) {
  return buildCrmWorkspaceTelemetry(snapshot, workspaces)
    .filter(workspace => ['leads', 'contacts', 'accounts', 'deals', 'tasks', 'meetings', 'evidence'].includes(workspace.id))
    .map(workspace => ({
      ...workspace,
      actionLabel: workspace.id === 'leads'
        ? 'Open Lead intake'
        : `Open ${workspace.label}`,
      readiness: workspace.count ? 'Source rows returned' : 'Ready for live creation'
    }));
}

/**
 * @function buildCrmDisruptionFeatures
 * @description Builds live invention-grade CRM intelligence cards from source posture.
 * @param {Object} snapshot - CRM snapshot.
 * @param {Array<Object>} primaryStages - Primary pipeline stages.
 * @param {number} readinessScore - Governance readiness score.
 * @returns {Array<Object>} Disruption feature cards.
 * @collaboration Gives Wilsy CRM a defensible operating thesis beyond ordinary record management.
 */
function buildCrmDisruptionFeatures(snapshot = createEmptySnapshot(), primaryStages = [], readinessScore = 0) {
  const connected = toNumber(snapshot.sourcePosture?.connected);
  const total = Math.max(1, toNumber(snapshot.sourcePosture?.total));
  const weightedPipeline = buildPipelineTotal(primaryStages);
  const proofAnchors = Array.isArray(snapshot.evidence) ? snapshot.evidence.length : 0;
  const liveLeadCount = Array.isArray(snapshot.leads) ? snapshot.leads.length : 0;
  const dealCount = Array.isArray(snapshot.deals) ? snapshot.deals.length : 0;

  return CRM_DISRUPTION_FEATURES.map(feature => {
    if (feature.id === 'proofgraph') {
      return {
        ...feature,
        status: proofAnchors ? 'LIVE' : 'ARMED',
        metric: `${proofAnchors} anchors`,
        detail: proofAnchors ? 'Evidence anchors are available for commercial proof.' : 'Proof memory is armed and waiting for evidence anchors.'
      };
    }

    if (feature.id === 'twin') {
      return {
        ...feature,
        status: dealCount ? 'SIMULATING' : 'READY',
        metric: formatMoney(weightedPipeline),
        detail: dealCount ? `${dealCount} deal rows feed the weighted twin.` : 'Revenue twin is ready for source deals.'
      };
    }

    if (feature.id === 'judge') {
      return {
        ...feature,
        status: connected === total ? 'CLEAR' : 'GATED',
        metric: `${connected}/${total}`,
        detail: connected === total ? 'All source routes clear the operating gate.' : 'Source route judge is holding incomplete routes.'
      };
    }

    return {
      ...feature,
      status: readinessScore >= 70 ? 'ONLINE' : 'CONTROLLED',
      metric: `${readinessScore}%`,
      detail: liveLeadCount ? `${liveLeadCount} live lead rows can receive governed next actions.` : 'Autopilot stays controlled until live lead rows arrive.'
    };
  });
}

/**
 * @function normalizeCrmRoleToken
 * @description Normalizes CRM role names into stable permission tokens.
 * @param {*} value - Candidate role value.
 * @returns {string} Normalized role token.
 * @collaboration Keeps founder, admin, manager and employee workspaces consistent across auth providers.
 */
function normalizeCrmRoleToken(value) {
  return String(value || '')
    .trim()
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toUpperCase();
}

/**
 * @function collectCrmRoleTokens
 * @description Extracts all role/profile signals from user, tenant and operator packets.
 * @param {Object} user - User packet.
 * @param {Object} tenantConfig - Tenant packet.
 * @param {Object} operatorIdentity - Operator identity packet.
 * @returns {Array<string>} Role tokens.
 * @collaboration Makes permissions data-driven instead of hardcoded to one local founder account.
 */
function collectCrmRoleTokens(user = {}, tenantConfig = {}, operatorIdentity = {}) {
  const candidateValues = [
    user?.role,
    user?.roleLabel,
    user?.accountRole,
    user?.profile?.role,
    user?.profile?.roleLabel,
    user?.permissions?.role,
    user?.crmRole,
    user?.departmentRole,
    tenantConfig?.role,
    tenantConfig?.operatorRole,
    tenantConfig?.crmRole,
    operatorIdentity?.roleLabel
  ];

  const arrayValues = [
    user?.roles,
    user?.roleTokens,
    user?.permissions?.roles,
    user?.profile?.roles,
    tenantConfig?.roles,
    tenantConfig?.crmRoles
  ].flatMap(value => Array.isArray(value) ? value : []);

  return [...candidateValues, ...arrayValues]
    .map(normalizeCrmRoleToken)
    .filter(Boolean);
}

/**
 * @function collectCrmOperatorKeys
 * @description Builds stable operator ownership keys for employee-scoped CRM rows.
 * @param {Object} user - User packet.
 * @param {Object} operatorIdentity - Operator identity packet.
 * @returns {Array<string>} Ownership keys.
 * @collaboration Lets sales consultants see their own work without exposing tenant-wide rows.
 */
function collectCrmOperatorKeys(user = {}, operatorIdentity = {}) {
  const keys = [
    user?._id,
    user?.id,
    user?.userId,
    user?.email,
    user?.primaryEmail,
    user?.username,
    user?.displayName,
    user?.fullName,
    user?.name,
    operatorIdentity?.email,
    operatorIdentity?.displayName,
    operatorIdentity?.firstName && operatorIdentity?.surname
      ? `${operatorIdentity.firstName} ${operatorIdentity.surname}`
      : '',
    operatorIdentity?.initials
  ];

  return [...new Set(
    keys
      .map(value => String(value || '').trim().toLowerCase())
      .filter(value => value && value !== '—' && value !== 'undefined' && value !== 'null')
  )];
}

/**
 * @function resolveCrmPermissionProfile
 * @description Resolves tenant, team or owned CRM workspace permissions.
 * @param {Object} user - User packet.
 * @param {Object} tenantConfig - Tenant packet.
 * @param {Object} operatorIdentity - Operator identity packet.
 * @returns {Object} CRM permission profile.
 * @collaboration Enforces separate founder/developer command cockpit and employee daily workspace behavior.
 */
function resolveCrmPermissionProfile(user = {}, tenantConfig = {}, operatorIdentity = {}) {
  const roleTokens = collectCrmRoleTokens(user, tenantConfig, operatorIdentity);
  const hasTenantCommand = roleTokens.some(token => CRM_TENANT_COMMAND_ROLE_TOKENS.includes(token));
  const hasTeamCommand = roleTokens.some(token => CRM_TEAM_COMMAND_ROLE_TOKENS.includes(token));
  const employeeToken = roleTokens.find(token => CRM_EMPLOYEE_ROLE_WORKSPACES[token]);
  const allowedWorkspaceIds = hasTenantCommand
    ? CRM_WORKSPACES.map(workspace => workspace.id)
    : hasTeamCommand
      ? ['home', 'leads', 'contacts', 'accounts', 'deals', 'tasks', 'meetings', 'evidence']
      : CRM_EMPLOYEE_ROLE_WORKSPACES[employeeToken] || CRM_EMPLOYEE_ROLE_WORKSPACES.EMPLOYEE;

  const allowedHomeTabIds = hasTenantCommand
    ? CRM_HOME_TABS.map(tab => tab.id)
    : hasTeamCommand
      ? ['operate', 'pipeline', 'create']
      : ['operate', 'create'];

  const sourceLabels = allowedWorkspaceIds
    .filter(id => CRM_ENDPOINTS[id])
    .map(id => CRM_WORKSPACES.find(workspace => workspace.id === id)?.label)
    .filter(Boolean);

  return {
    roleTokens,
    roleLabel: roleTokens[0] || normalizeCrmRoleToken(operatorIdentity?.roleLabel) || 'EMPLOYEE',
    scope: hasTenantCommand ? 'tenant' : (hasTeamCommand ? 'team' : 'owned'),
    accessLabel: hasTenantCommand ? 'Tenant Command' : (hasTeamCommand ? 'Team Workspace' : 'My Workspace'),
    canSeeTenantWideData: hasTenantCommand,
    canSeeTeamData: hasTeamCommand || hasTenantCommand,
    includePrivilegedSearch: hasTenantCommand,
    allowedWorkspaceIds,
    allowedHomeTabIds,
    sourceLabels,
    ownerKeys: collectCrmOperatorKeys(user, operatorIdentity)
  };
}

/**
 * @function collectCrmRecordOwnershipValues
 * @description Extracts likely owner/assignee fields from a normalized CRM record.
 * @param {Object} record - Normalized CRM record.
 * @returns {Array<string>} Ownership field values.
 * @collaboration Supports row-level UI scoping without depending on one backend schema spelling.
 */
function collectCrmRecordOwnershipValues(record = {}) {
  const raw = record.raw || record;
  const candidates = [
    record.owner,
    raw.owner,
    raw.ownerName,
    raw.ownerId,
    raw.ownerEmail,
    raw.assignedTo,
    raw.assignee,
    raw.assignedUserId,
    raw.createdBy,
    raw.createdById,
    raw.createdByEmail,
    raw.updatedBy,
    raw.userId,
    raw.operatorId,
    raw.salesOwner,
    raw.accountOwner,
    raw.relationshipOwner,
    raw?.owner?.id,
    raw?.owner?.email,
    raw?.owner?.name,
    raw?.assignedTo?.id,
    raw?.assignedTo?.email,
    raw?.assignedTo?.name,
    raw?.createdBy?.id,
    raw?.createdBy?.email,
    raw?.createdBy?.name
  ];

  return candidates
    .flatMap(value => Array.isArray(value) ? value : [value])
    .map(value => {
      if (value && typeof value === 'object') {
        return [value.id, value._id, value.email, value.name, value.displayName, value.fullName]
          .filter(Boolean)
          .join(' ');
      }
      return String(value || '');
    })
    .map(value => value.trim().toLowerCase())
    .filter(Boolean);
}

/**
 * @function recordBelongsToCrmOperator
 * @description Checks if a CRM row belongs to the current operator or their permitted scope.
 * @param {Object} record - Normalized CRM record.
 * @param {Object} permissionProfile - CRM permission profile.
 * @returns {boolean} Whether the row can be shown.
 * @collaboration Prevents non-admin CRM views from leaking tenant-wide records in the client surface.
 */
function recordBelongsToCrmOperator(record = {}, permissionProfile = {}) {
  if (permissionProfile.canSeeTenantWideData) return true;
  const ownerKeys = permissionProfile.ownerKeys || [];
  if (!ownerKeys.length) return false;

  const ownershipValues = collectCrmRecordOwnershipValues(record);
  return ownershipValues.some(value => ownerKeys.some(key => value === key || value.includes(key)));
}

/**
 * @function scopeCrmSourcePosture
 * @description Filters source posture totals to the visible workspace routes.
 * @param {Object} posture - Full source posture.
 * @param {Object} permissionProfile - CRM permission profile.
 * @returns {Object} Scoped source posture.
 * @collaboration Keeps source route counters honest for employee workspaces.
 */
function scopeCrmSourcePosture(posture = {}, permissionProfile = {}) {
  const allowedRouteIds = new Set((permissionProfile.allowedWorkspaceIds || []).filter(id => CRM_ENDPOINTS[id]));
  const allSources = Array.isArray(posture.sources) ? posture.sources : [];
  const scopedSources = allSources.filter(source => allowedRouteIds.has(source.id));
  const sourceCount = scopedSources.length || allowedRouteIds.size || toNumber(posture.total);
  const connectedCount = scopedSources.length
    ? scopedSources.filter(source => source.routeLive || source.status === 'live').length
    : Math.min(toNumber(posture.connected), sourceCount);

  return {
    ...posture,
    sources: scopedSources,
    sourceGaps: Array.isArray(posture.sourceGaps)
      ? posture.sourceGaps.filter(source => allowedRouteIds.has(source.id))
      : [],
    errors: Array.isArray(posture.errors)
      ? posture.errors.filter(error => allowedRouteIds.has(error.collection))
      : [],
    connected: connectedCount,
    total: sourceCount || Object.keys(CRM_ENDPOINTS).length
  };
}

/**
 * @function scopeCrmSnapshotForOperator
 * @description Applies workspace and row-level permission scope to the CRM snapshot.
 * @param {Object} snapshot - Full CRM snapshot.
 * @param {Object} permissionProfile - CRM permission profile.
 * @returns {Object} Scoped CRM snapshot.
 * @collaboration Gives employees their own workspace while preserving founder/developer command authority.
 */
function scopeCrmSnapshotForOperator(snapshot = createEmptySnapshot(), permissionProfile = {}) {
  if (permissionProfile.canSeeTenantWideData) return snapshot;

  const allowedWorkspaceIds = new Set(permissionProfile.allowedWorkspaceIds || []);
  const scoped = createEmptySnapshot();

  Object.keys(CRM_ENDPOINTS).forEach(collection => {
    if (!allowedWorkspaceIds.has(collection)) {
      scoped[collection] = [];
      return;
    }

    const records = Array.isArray(snapshot[collection]) ? snapshot[collection] : [];
    scoped[collection] = records.filter(record => recordBelongsToCrmOperator(record, permissionProfile));
  });

  scoped.sourcePosture = scopeCrmSourcePosture(snapshot.sourcePosture || {}, permissionProfile);
  return scoped;
}

/**
 * @function buildCrmDailyWorkspaceCards
 * @description Builds Zoho-inspired but Wilsy-governed employee home cards from scoped data.
 * @param {Object} snapshot - Scoped CRM snapshot.
 * @returns {Array<Object>} Daily work cards.
 * @collaboration Turns employee CRM Home into personal duties instead of tenant-wide founder telemetry.
 */
function buildCrmDailyWorkspaceCards(snapshot = createEmptySnapshot()) {
  return CRM_EMPLOYEE_DAILY_WORKSPACE_CARDS.map(card => {
    const rows = Array.isArray(snapshot[card.id]) ? snapshot[card.id] : [];
    return {
      ...card,
      rows: rows.slice(0, 6),
      total: rows.length
    };
  });
}

/**
 * @function buildOperatorIdentity
 * @description Builds the current operator identity from props and browser cache while prioritizing first name and surname.
 * @param {Object} user - User prop.
 * @returns {Object} Operator identity.
 * @collaboration Uses backend/cache identity fields before falling back to browser-safe defaults.
 */
function buildOperatorIdentity(user = {}) {
  const storedUser = readStoredJson('user');
  const source = Object.keys(user || {}).length ? user : storedUser;

  const firstName = safeText(source.firstName || source.givenName || source.nameFirst || source.profile?.firstName, '');
  const surname = safeText(source.surname || source.lastName || source.familyName || source.nameLast || source.profile?.surname, '');
  const joinedName = `${firstName} ${surname}`.trim();

  const displayName = safeText(
    joinedName || source.displayName || source.fullName || source.name || getStoredValue('wilsyUserName', ''),
    'Wilson Khanyezi'
  );

  return {
    displayName,
    firstName,
    surname,
    roleLabel: safeText(source.roleLabel || source.role || source.accountRole || source.profile?.role, 'Workspace Admin').toUpperCase(),
    email: safeText(source.email || source.primaryEmail || source.username, 'wilsonkhanyezi@gmail.com'),
    avatar: resolveImageSource(source.avatar || source.avatarUrl || source.profileImage || source.photoURL || source.profile?.avatar),
    initials: buildInitials(displayName),
    source: source._id || source.id || source.userId ? 'cache' : 'fallback'
  };
}


/**
 * @function normalizeBackendOperatorProfile
 * @description Normalizes authenticated backend user profile payloads into the CRM operator identity contract.
 * @param {Object} payload - Backend profile payload.
 * @param {Object} fallback - Existing identity fallback.
 * @returns {Object} Normalized operator identity.
 * @collaboration Ensures CRM displays DB-backed name, surname, email and role when the live backend exposes them.
 */
function normalizeBackendOperatorProfile(payload = {}, fallback = {}) {
  const candidate = payload?.user || payload?.data?.user || payload?.data || payload?.profile || payload?.operator || payload || {};

  const firstName = safeText(candidate.firstName || candidate.givenName || candidate.nameFirst, '');
  const surname = safeText(candidate.surname || candidate.lastName || candidate.familyName || candidate.nameLast, '');
  const joinedName = `${firstName} ${surname}`.trim();

  const displayName = safeText(
    joinedName || candidate.displayName || candidate.fullName || candidate.name,
    fallback.displayName || 'Wilson Khanyezi'
  );

  const roleLabel = safeText(
    candidate.roleLabel || candidate.role || candidate.accountRole || candidate.permissions?.role || candidate.accessRole,
    fallback.roleLabel || 'Workspace Admin'
  ).toUpperCase();

  const email = safeText(candidate.email || candidate.primaryEmail || candidate.username, fallback.email || 'wilsonkhanyezi@gmail.com');

  return {
    ...fallback,
    displayName,
    firstName: firstName || fallback.firstName || '',
    surname: surname || fallback.surname || '',
    roleLabel,
    email,
    avatar: resolveImageSource(candidate.avatar || candidate.avatarUrl || candidate.profileImage || candidate.photoURL || candidate.profile?.avatar || fallback.avatar),
    initials: buildInitials(displayName),
    source: 'backend'
  };
}

/**
 * @function fetchBackendOperatorProfile
 * @description Attempts to retrieve the authenticated operator profile from live backend routes.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal.
 * @param {Object} fallback - Existing fallback identity.
 * @returns {Promise<Object>} Operator identity.
 * @collaboration Starts the CRM identity chain from backend/DB data without breaking when a route is unavailable.
 */
async function fetchBackendOperatorProfile(tenantId, signal, fallback = {}) {
  const fallbackProfile = normalizeBackendOperatorProfile(fallback, fallback);
  const profileLookupEnabled = Boolean(window?.__WILSY_ENABLE_CRM_BACKEND_PROFILE_LOOKUP);

  if (!profileLookupEnabled) {
    return fallbackProfile;
  }

  const headers = buildAuthHeaders(tenantId);
  const authHeader = String(headers.Authorization || '').trim();
  const tokenHeader = String(headers['X-Auth-Token'] || headers['X-Wilsy-Auth-Token'] || '').trim();
  const hasBearer = authHeader.startsWith('Bearer ') && !authHeader.includes('undefined') && !authHeader.includes('null');
  const hasTokenHeader = tokenHeader && tokenHeader !== 'undefined' && tokenHeader !== 'null';

  if (!hasBearer && !hasTokenHeader) {
    return fallbackProfile;
  }

  try {
    const response = await fetch(`${API_BASE}/api/auth/me`, {
      method: 'GET',
      headers,
      signal,
      credentials: 'include'
    });

    if (response.status === 401 || response.status === 403 || response.status === 404) {
      return fallbackProfile;
    }

    if (!response.ok) {
      return fallbackProfile;
    }

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return fallbackProfile;
    }

    const payload = await response.json();
    return normalizeBackendOperatorProfile(payload, fallbackProfile);
  } catch (error) {
    if (error?.name === 'AbortError') return fallbackProfile;

    return fallbackProfile;
  }
}
/**
 * @function useBackendOperatorIdentity
 * @description Hydrates operator identity from backend profile routes with safe fallback.
 * @param {Object} user - User prop fallback.
 * @param {string} tenantId - Active tenant id.
 * @param {number} refreshSignal - Refresh signal.
 * @returns {Object} Operator identity.
 * @collaboration Connects CRM chrome to live backend user details while preserving resilience.
 */
function useBackendOperatorIdentity(user = {}, tenantId = 'MASTER', refreshSignal = 0) {
  const fallbackIdentity = useMemo(() => buildOperatorIdentity(user), [user]);
  const [operatorIdentity, setOperatorIdentity] = useState(fallbackIdentity);

  useEffect(() => {
    setOperatorIdentity(fallbackIdentity);
  }, [fallbackIdentity]);

  useEffect(() => {
    const controller = new AbortController();

    fetchBackendOperatorProfile(tenantId, controller.signal, fallbackIdentity)
      .then(profile => setOperatorIdentity(profile))
      .catch(() => setOperatorIdentity(fallbackIdentity));

    return () => controller.abort();
  }, [tenantId, refreshSignal, fallbackIdentity]);

  return operatorIdentity;
}

/**
 * @function buildTenantIdentity
 * @description Builds tenant identity from tenant context and props.
 * @param {Object} tenantRuntime - Tenant context runtime.
 * @param {Object} tenantConfig - Tenant prop config.
 * @returns {Object} Tenant identity.
 * @collaboration Uses tenantContext as the governed identity source while preserving safe fallbacks.
 */
function buildTenantIdentity(tenantRuntime = {}, tenantConfig = {}) {
  const activeTenant = tenantRuntime.activeTenant || {};
  const branding = tenantRuntime.tenantBranding || {};
  const source = { ...activeTenant, ...branding, ...tenantConfig };

  const name = safeText(
    source.companyName || source.name || source.label || source.tenantName,
    'Wilsy OS Root'
  );

  return {
    tenantId: safeText(source.tenantId || source.id || source.alias || getStoredValue('tenantId', ''), 'MASTER'),
    name,
    subtitle: safeText(source.authority || source.industry || source.businessModel, 'Tenant Identity Live'),
    logo: resolveImageSource(source.logo || source.logoUrl || source.brandLogo),
    primaryColor: source.primaryColor || source.primary || '#D4AF37',
    secondaryColor: source.secondaryColor || source.secondary || '#1EEBCB',
    accentColor: source.accentColor || source.accent || '#F6E27A'
  };
}

/**
 * @function getRecordCellValue
 * @description Resolves a table cell display value.
 * @param {Object} record - Normalized CRM record.
 * @param {string} column - Column label.
 * @returns {string} Display value.
 * @collaboration Keeps record tables consistent across source collections.
 */
function getRecordCellValue(record, column) {
  const key = column.toLowerCase();
  const valueMap = {
    name: record.name,
    company: record.company,
    email: record.email,
    phone: record.phone,
    source: record.source,
    account: record.company,
    industry: record.industry,
    owner: record.owner,
    status: record.status,
    deal: record.name,
    stage: record.stage,
    value: formatMoney(record.value),
    task: record.name,
    due: record.dueDate,
    meeting: record.name,
    date: record.dueDate,
    evidence: record.name,
    type: record.type,
    connector: record.name,
    category: record.type,
    'last sync': record.dueDate
  };

  return safeText(valueMap[key], '—');
}


/**
 * @function resolveWilsyR91K114ReadinessScore
 * @description Resolves CRM readiness from the backend Source Posture Guide before falling back to local snapshot math.
 * @param {Object} snapshot - CRM operating snapshot.
 * @returns {number} Readiness percentage.
 * @collaboration CRM header telemetry, backend Source Posture Guide, Wilsy AI truth layer.
 */
function resolveWilsyR91K114ReadinessScore(snapshot = {}) {
  const guideScore = toNumber(
    snapshot?.sourceGuide?.readinessScore ||
      snapshot?.sourcePosture?.sourceGuide?.readinessScore
  );

  if (guideScore > 0) {
    return guideScore;
  }

  return toNumber(snapshot?.readinessScore);
}

/**
 * @function resolveWilsyR91K114ReadinessNarrative
 * @description Builds a readiness narrative from the backend Source Posture Guide.
 * @param {Object} snapshot - CRM operating snapshot.
 * @param {number} readinessScore - Active readiness score.
 * @returns {string} Readiness narrative.
 * @collaboration CRM metric deck, Source Posture Guide, Wilsy AI operating mode.
 */
function resolveWilsyR91K114ReadinessNarrative(snapshot = {}, readinessScore = 0) {
  const guide = snapshot?.sourceGuide || snapshot?.sourcePosture?.sourceGuide || null;

  if (guide?.postureGrade && guide?.aiOperatingMode) {
    return `${guide.postureGrade} · ${guide.aiOperatingMode}`;
  }

  if (guide?.postureGrade) {
    return guide.postureGrade;
  }

  return readinessScore ? 'Source posture improving' : 'Connect sources to lift readiness';
}

/**
 * @function useCrmSnapshot
 * @description Loads source-led CRM collections for the active tenant.
 * @param {string} tenantId - Active tenant id.
 * @param {number} refreshSignal - Refresh trigger.
 * @returns {Object} Snapshot state.
 * @collaboration Separates CRM data hydration from presentation so the cockpit remains testable.
 */
function useCrmSnapshot(tenantId, refreshSignal) {
  const [state, setState] = useState(() => ({
    snapshot: createEmptySnapshot(),
    loading: true,
    error: null
  }));

  useEffect(() => {
    const controller = new AbortController();
    const collections = Object.keys(CRM_ENDPOINTS);

    setState(previous => ({
      ...previous,
      loading: true,
      snapshot: {
        ...previous.snapshot,
        sourcePosture: { ...previous.snapshot.sourcePosture, loading: true }
      }
    }));

    Promise.all(collections.map(collection => fetchCrmCollection(collection, tenantId, controller.signal)))
      .then(async results => {
        const [
          backendPosture,
          routeSurfacePayload,
          sourceGuidePayload
        ] = await Promise.all([
          fetchCrmSourcePosture(tenantId, controller.signal).catch(() => null),
          typeof fetchCrmRouteSurface === 'function'
            ? fetchCrmRouteSurface(tenantId, controller.signal).catch(() => null)
            : Promise.resolve(null),
          fetchCrmSourceGuide(tenantId, controller.signal).catch(() => null)
        ]);
        const sourceGuide = normalizeWilsyR91K147SourceGuideState(
          sourceGuidePayload?.guide ||
          sourceGuidePayload?.sourceGuide ||
          sourceGuidePayload?.data?.guide ||
          sourceGuidePayload?.data?.sourceGuide ||
          sourceGuidePayload?.result?.guide ||
          sourceGuidePayload?.payload?.guide ||
          sourceGuidePayload ||
          null,
          sourceGuidePayload
        ); /* R91K147C_SOURCEGUIDE_ASSIGNMENT_BRIDGE */
        const routeSurface = routeSurfacePayload?.routeSurface || sourceGuide?.routeSurface || null;
        const guideSourcePosture = sourceGuide?.sourcePosture || null;
        const enrichedPosture = backendPosture
          ? { ...backendPosture, routeSurface, sourceGuide }
          : guideSourcePosture
            ? {
              ...guideSourcePosture,
              connectedRoutes: guideSourcePosture.connectedRoutes,
              totalRoutes: guideSourcePosture.totalRoutes,
              sourceGaps: guideSourcePosture.sourceGaps || [],
              routeSurface,
              sourceGuide
            }
            : routeSurface
              ? { connectedRoutes: 0, totalRoutes: 0, sourceGaps: [], sources: [], routeSurface, sourceGuide }
              : sourceGuide
                ? { connectedRoutes: 0, totalRoutes: 0, sourceGaps: [], sources: [], sourceGuide }
                : null;
        const enrichedResults = enrichedPosture && results.length
          ? results.map((result, index) => index === 0 ? { ...result, sourcePosture: enrichedPosture } : result)
          : results;
        const hydratedSnapshot = buildCrmSnapshot(enrichedResults);
        const sourceGuideReadiness = toNumber(sourceGuide?.readinessScore);
        const hydratedSourcePosture = {
          ...(hydratedSnapshot.sourcePosture || {}),
          routeSurface: routeSurface || hydratedSnapshot.sourcePosture?.routeSurface || null,
          sourceGuide
        };

        setState({
          snapshot: {
            ...hydratedSnapshot,
            sourcePosture: hydratedSourcePosture,
            sourceGuide,
            readinessScore: sourceGuideReadiness || toNumber(hydratedSnapshot.readinessScore),
            readinessPostureGrade: sourceGuide?.postureGrade || null,
            aiOperatingMode: sourceGuide?.aiOperatingMode || null
          },
          loading: false,
          error: null
        });
      })
      .catch(error => {
        const snapshot = createEmptySnapshot();
        snapshot.sourcePosture.errors = [{ collection: 'all', error: error?.message || 'CRM source failure' }];
        setState({ snapshot, loading: false, error: error?.message || 'CRM source failure' });
      });

    return () => controller.abort();
  }, [tenantId, refreshSignal]);

  return state;
}

/**
 * @function CRMDashboard
 * @description Renders the Wilsy OS CRM Command Center as a sovereign sales intelligence cockpit.
 * @param {Object} props - Dashboard props.
 * @returns {JSX.Element} CRM dashboard.
 * @collaboration Gives Sovereign routing one production CRM surface with Account Command Center integration.
 */

const R73B_SOVEREIGN_SEARCH_RUNTIME_HELPERS = true;

const SOVEREIGN_SEARCH_LIVE_COLLECTIONS = Object.freeze([
  'leads',
  'accounts',
  'contacts',
  'deals',
  'tasks',
  'meetings',
  'evidence',
  'connectors',
]);

const SOVEREIGN_SEARCH_INTELLIGENCE_COLLECTIONS = Object.freeze([
  'telemetry',
  'compliance',
  'governance',
  'revenue',
  'scores',
]);

/**
 * @function shouldOpenSovereignSearchFromKeyboard
 * @description Detects the platform command shortcut used to open the CRM sovereign search overlay.
 * @collaboration R73B keyboard command runtime, existing command shell, CRM operator workflow.
 */
function shouldOpenSovereignSearchFromKeyboard(event) {
  return Boolean((event.metaKey || event.ctrlKey) && String(event.key || '').toLowerCase() === 'k');
}

/**
 * @function resolveSovereignSearchApiBase
 * @description Resolves the CRM search API base from the existing Vite runtime configuration.
 * @collaboration R73B search runtime transport, CRM backend route mount, tenant-safe browser execution.
 */
function resolveSovereignSearchApiBase() {
  return String(import.meta.env?.VITE_API_URL || '').replace(/\/$/, '');
}

/**
 * @function resolveSovereignSearchHeaders
 * @description Builds safe runtime headers for CRM search calls without exposing browser-side secrets.
 * @collaboration R73B search runtime transport, tenant posture, auth/security hardening compatibility.
 */
function resolveSovereignSearchHeaders() {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Tenant-Id': window.localStorage.getItem('tenantId') || window.localStorage.getItem('wilsyTenantId') || 'MASTER',
  };

  const runtimeCredential = window.localStorage.getItem('token') || window.localStorage.getItem('authToken') || window.localStorage.getItem('wilsyToken');
  if (runtimeCredential) {
    headers.Authorization = ['Bearer', runtimeCredential].join(' ');
  }

  return headers;
}

/**
 * @function normalizeSovereignSearchPayloadRecords
 * @description Extracts record arrays from route payloads while preserving source-honest empty results.
 * @collaboration R73B search runtime parsing, CRM live source routes, intelligence collection routes.
 */
function normalizeSovereignSearchPayloadRecords(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (!payload || typeof payload !== 'object') {
    return [];
  }

  const candidate =
    payload.records ||
    payload.items ||
    payload.results ||
    payload.data ||
    payload.collection ||
    payload.payload ||
    [];

  if (Array.isArray(candidate)) {
    return candidate;
  }

  if (candidate && typeof candidate === 'object' && Array.isArray(candidate.records)) {
    return candidate.records;
  }

  return [];
}

/**
 * @function buildSovereignSearchRecordLabel
 * @description Builds a human-readable label for a CRM search record without inventing data.
 * @collaboration R73B result rendering, source-honest CRM records, operator-readable command overlay.
 */
function buildSovereignSearchRecordLabel(record, fallbackLabel) {
  if (!record || typeof record !== 'object') {
    return fallbackLabel;
  }

  return (
    record.name ||
    record.title ||
    record.companyName ||
    record.accountName ||
    record.contactName ||
    record.email ||
    record.reference ||
    record.hash ||
    record.rootHash ||
    record._id ||
    record.id ||
    fallbackLabel
  );
}

/**
 * @function buildSovereignSearchRecordDescription
 * @description Builds a compact source-honest description for a CRM search record.
 * @collaboration R73B result rendering, evidence and connector posture, operator-readable search output.
 */
function buildSovereignSearchRecordDescription(record) {
  if (!record || typeof record !== 'object') {
    return 'No additional source fields returned.';
  }

  return (
    record.description ||
    record.summary ||
    record.status ||
    record.stage ||
    record.type ||
    record.source ||
    record.collection ||
    record.tenantId ||
    'Source record returned by CRM backend.'
  );
}

/**
 * @function recordMatchesSovereignSearchQuery
 * @description Checks whether a returned CRM record matches the operator query.
 * @collaboration R73B client-side refinement, live source routes, source-honest search filtering.
 */
function recordMatchesSovereignSearchQuery(record, normalizedQuery) {
  if (!normalizedQuery) {
    return true;
  }

  return JSON.stringify(record || {}).toLowerCase().includes(normalizedQuery);
}

/**
 * @function mapSovereignSearchRecords
 * @description Maps route records into normalized overlay result objects.
 * @collaboration R73B search results overlay, source grouping, CRM command center output.
 */
function mapSovereignSearchRecords(records, sourceGroup, query) {
  const normalizedQuery = query.toLowerCase();

  return records
    .filter((record) => recordMatchesSovereignSearchQuery(record, normalizedQuery))
    .slice(0, 8)
    .map((record, index) => ({
      id: record?._id || record?.id || [sourceGroup.key, index, buildSovereignSearchRecordLabel(record, sourceGroup.label)].join(':'),
      group: sourceGroup.label,
      type: sourceGroup.key,
      label: buildSovereignSearchRecordLabel(record, sourceGroup.label),
      description: buildSovereignSearchRecordDescription(record),
      evidence: record?.hash || record?.rootHash || record?.evidenceId || record?.receiptId || record?.tenantId || 'SOURCE-LIVE',
    }));
}

/**
 * @function fetchSovereignSearchCollection
 * @description Fetches one CRM live or intelligence collection for the sovereign search overlay.
 * @collaboration R73B search transport, R72W mounted CRM APIs, auth/security/hardening compatibility.
 */
async function fetchSovereignSearchCollection(endpoint, sourceGroup, query) {
  const apiBase = resolveSovereignSearchApiBase();
  const response = await fetch(`${apiBase}${endpoint}`, {
    method: 'GET',
    headers: resolveSovereignSearchHeaders(),
  });

  if (!response.ok) {
    return [];
  }

  const payload = await response.json();
  const records = normalizeSovereignSearchPayloadRecords(payload);

  return mapSovereignSearchRecords(records, sourceGroup, query);
}

/**
 * @function runSovereignSearchRuntime
 * @description Runs CRM sovereign search across mounted live and intelligence backend surfaces.
 * @collaboration R73B visible search payoff, R72W route mount activation, CRM source-honest results.
 */
async function runSovereignSearchRuntime(query) {
  const normalizedQuery = String(query || '').trim();

  if (!normalizedQuery) {
    return [];
  }

  const liveGroups = SOVEREIGN_SEARCH_LIVE_COLLECTIONS.map((collection) => ({
    key: collection,
    label: collection.replace(/(^|-)\w/g, (value) => value.toUpperCase()),
    endpoint: `/api/crm/live/${collection}?limit=24`,
  }));

  const intelligenceGroups = SOVEREIGN_SEARCH_INTELLIGENCE_COLLECTIONS.map((collection) => ({
    key: `intelligence-${collection}`,
    label: `Intelligence ${collection.replace(/(^|-)\w/g, (value) => value.toUpperCase())}`,
    endpoint: `/api/crm/intelligence/${collection}?limit=24`,
  }));

  const results = await Promise.all(
    [...liveGroups, ...intelligenceGroups].map((group) =>
      fetchSovereignSearchCollection(group.endpoint, group, normalizedQuery)
    )
  );

  return results.flat().slice(0, 36);
}

/**
 * @function SovereignSearchCommandOverlay
 * @description Renders the CRM sovereign search results overlay with loading, empty, error, and grouped result states.
 * @collaboration R73B operator-grade search UI, existing CRM dashboard shell, source-honest backend results.
 */
function SovereignSearchCommandOverlay({ isOpen, query, searchState, styles, onClose }) {
  if (!isOpen) {
    return null;
  }

  const hasQuery = Boolean(String(query || '').trim());
  const resultCount = searchState?.results?.length || 0;

  return (
    <section
      className={styles.sovereignSearchOverlay}
      data-wilsy-r73b-sovereign-search-overlay="true"
      aria-label="Sovereign CRM search results"
    >
      <div className={styles.sovereignSearchPanel}>
        <div className={styles.sovereignSearchHeader}>
          <div>
            <p className={styles.sovereignSearchEyebrow}>SOVEREIGN SEARCH ENGINE</p>
            <h3>CRM command results</h3>
          </div>
          <button
            type="button"
            className={styles.sovereignSearchClose}
            onClick={onClose}
            aria-label="Close sovereign search"
          >
            Esc
          </button>
        </div>

        <div className={styles.sovereignSearchStatus}>
          {!hasQuery && 'Type to search leads, accounts, contacts, deals, evidence, hashes, connectors and intelligence.'}
          {hasQuery && searchState?.status === 'loading' && `Searching sovereign CRM sources for “${query}”…`}
          {hasQuery && searchState?.status === 'ready' && `${resultCount} source-honest result${resultCount === 1 ? '' : 's'} for “${query}”.`}
          {hasQuery && searchState?.status === 'error' && searchState?.error}
        </div>

        {hasQuery && searchState?.status === 'ready' && resultCount === 0 && (
          <div className={styles.sovereignSearchEmpty}>
            No live CRM records matched this query yet. The search engine returned a source-honest empty state, not fake data.
          </div>
        )}

        {hasQuery && searchState?.status === 'ready' && resultCount > 0 && (
          <div className={styles.sovereignSearchResults}>
            {searchState.results.map((result) => (
              <article className={styles.sovereignSearchResult} key={result.id}>
                <div>
                  <span className={styles.sovereignSearchGroup}>{result.group}</span>
                  <strong>{result.label}</strong>
                  <p>{result.description}</p>
                </div>
                <code>{result.evidence}</code>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

/**
 * @function CRMDashboard
 * @description Renders the sovereign CRM operating dashboard, including the R73B source-guided search results overlay, account command center integration, command rail, lead room, theme runtime, and backend evidence surfaces.
 * @collaboration Coordinates CRM frontend search, mounted CRM live/intelligence APIs, tenant-aware service posture, account command center controls, and Wilsy OS production guard discipline.
 */

/* R91K131_CRM_FULL_VIEWPOINT_OPERATING_CONTRACT
   Real operating surface: explicit React state, live model, no placeholder records. */

const WILSY_R91K131_STAGE_CONTRACT = [
  { id: 'intake', index: '01', label: 'Intake', probability: 10, proof: 'Lead source receipt', description: 'Source, identity and consent basis captured for governed conversion.' },
  { id: 'contact', index: '02', label: 'Contact', probability: 25, proof: 'Engagement marker', description: 'First touch, intent and response path recorded against the buyer journey.' },
  { id: 'qualify', index: '03', label: 'Qualify', probability: 40, proof: 'Buyer authority marker', description: 'BANT, authority and FICA identity posture verified before pipeline advance.' },
  { id: 'discover', index: '04', label: 'Discover', probability: 55, proof: 'Discovery receipt', description: 'Pain, goals and buying criteria documented for revenue evidence.' },
  { id: 'propose', index: '05', label: 'Propose', probability: 70, proof: 'Offer pack hash', description: 'Solution fit, pricing and value case evidence prepared for decision.' },
  { id: 'negotiate', index: '06', label: 'Negotiate', probability: 85, proof: 'Clause variance log', description: 'Objections, redlines and authority trail governed before contract seal.' },
  { id: 'convert', index: '07', label: 'Convert', probability: 100, proof: 'Outcome receipt', description: 'Final outcome recorded for forecast integrity and revenue assurance.' },
];

const WILSY_R91K131_INTELLIGENCE_TABS = [
  { id: 'email', label: 'Email', receipt: 'SOURCE LIVE' },
  { id: 'evidence', label: 'Evidence', receipt: 'ANCHOR STATUS' },
  { id: 'connectors', label: 'Connectors', receipt: 'SOURCE POSTURE' },
  { id: 'revenue', label: 'Revenue', receipt: 'PIPELINE POSTURE' },
];

/**
 * @function sanitizeWilsyR91K131Text
 * @description Normalizes live CRM display text without inventing replacement data.
 * @collaboration Used by R91K131 viewpoint model builders to keep production truth readable.
 */
function sanitizeWilsyR91K131Text(value, fallback = 'Unavailable') {
  if (value === null || value === undefined) return fallback;
  const nextValue = String(value).trim();
  return nextValue.length > 0 ? nextValue : fallback;
}

/**
 * @function readWilsyR91K131Path
 * @description Safely reads nested live CRM values from operating snapshots and source guides.
 * @collaboration Keeps the full viewpoint model coupled to live production telemetry only.
 */
function readWilsyR91K131Path(source, paths, fallback = null) {
  if (!source || !Array.isArray(paths)) return fallback;

  for (const pathKey of paths) {
    const parts = String(pathKey).split('.');
    let cursor = source;
    let resolved = true;

    for (const part of parts) {
      if (cursor && Object.prototype.hasOwnProperty.call(cursor, part)) {
        cursor = cursor[part];
      } else {
        resolved = false;
        break;
      }
    }

    if (resolved && cursor !== null && cursor !== undefined && cursor !== '') {
      return cursor;
    }
  }

  return fallback;
}

/**
 * @function formatWilsyR91K131Currency
 * @description Formats live monetary values for the CRM pipeline surface.
 * @collaboration Shared by stage cards, proof ledger and revenue rail.
 */
function formatWilsyR91K131Currency(value, currency = 'ZAR') {
  const numericValue = Number(value || 0);

  if (!Number.isFinite(numericValue) || numericValue === 0) {
    return currency === 'ZAR' ? 'R 0' : `${currency} 0`;
  }

  try {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency,
      maximumFractionDigits: 0,
    }).format(numericValue);
  } catch (error) {
    return `${currency} ${Math.round(numericValue).toLocaleString('en-ZA')}`;
  }
}

/**
 * @function normalizeWilsyR91K131Percent
 * @description Converts live readiness and compliance values into safe percentage scores.
 * @collaboration Powers compliance gradients, stage posture and proof ledger status.
 */
function normalizeWilsyR91K131Percent(value, fallback = 0) {
  const numericValue = Number(value ?? fallback);
  if (!Number.isFinite(numericValue)) return fallback;
  return Math.max(0, Math.min(100, Math.round(numericValue)));
}


/* R91K145_LIVE_FABRIC_BACKEND_CONTRACT_CONSUMER */

/**
 * @function collectWilsyR91K145ObjectCandidates
 * @description Collects nested response-envelope objects so the CRM fabric can find the live backend sourceSignatureFabric contract.
 * @collaboration Used by the R91K131 model builder to prefer /api/crm/live/source-guide backend truth over frontend fallback text.
 */
function collectWilsyR91K145ObjectCandidates(source, depth = 0, candidates = []) {
  if (!source || typeof source !== 'object' || Array.isArray(source) || depth > 5) {
    return candidates;
  }

  candidates.push(source);

  for (const key of [
    'sourceSignatureFabric',
    'guide',
    'data',
    'sourceGuide',
    'result',
    'payload',
    'crmSourceGuide',
    'liveSourceGuide',
    'sourceGuidePayload',
  ]) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      collectWilsyR91K145ObjectCandidates(source[key], depth + 1, candidates);
    }
  }

  if (depth < 2) {
    for (const value of Object.values(source)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        collectWilsyR91K145ObjectCandidates(value, depth + 1, candidates);
      }
    }
  }

  return candidates;
}

/**
 * @function resolveWilsyR91K145SourceSignatureFabricContract
 * @description Resolves the first live R91K144 backend sourceSignatureFabric contract from any Source Guide response envelope.
 * @collaboration Prevents the Fabric header from falling back to frontend-owned route/posture copy when backend truth exists.
 */
function resolveWilsyR91K145SourceSignatureFabricContract(sourceGuideEnvelope) {
  const candidates = collectWilsyR91K145ObjectCandidates(sourceGuideEnvelope);

  for (const candidate of candidates) {
    if (
      candidate &&
      candidate.contractVersion === 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT'
    ) {
      return candidate;
    }

    if (
      candidate?.sourceSignatureFabric &&
      candidate.sourceSignatureFabric.contractVersion === 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT'
    ) {
      return candidate.sourceSignatureFabric;
    }
  }

  return null;
}

/**
 * @function normalizeWilsyR91K145FabricNodes
 * @description Normalizes live backend fabric nodes while preserving the existing frontend fallback nodes if backend nodes are not available.
 * @collaboration Feeds the R91K139 Fabric visual chain from backend Source Guide truth without placeholder records.
 */
function normalizeWilsyR91K145FabricNodes(backendNodes, fallbackNodes) {
  if (!Array.isArray(backendNodes) || backendNodes.length === 0) {
    return fallbackNodes;
  }

  return backendNodes.map((node, index) => ({
    id: sanitizeWilsyR91K131Text(node.id, fallbackNodes[index]?.id, `node-${index + 1}`),
    label: sanitizeWilsyR91K131Text(node.label, fallbackNodes[index]?.label, 'Signal'),
    status: sanitizeWilsyR91K131Text(node.status, fallbackNodes[index]?.status, 'LIVE'),
    value: sanitizeWilsyR91K131Text(node.value, fallbackNodes[index]?.value, 'Unavailable'),
    detail: sanitizeWilsyR91K131Text(node.detail, fallbackNodes[index]?.detail, 'Backend detail unavailable'),
    route: sanitizeWilsyR91K131Text(node.route, fallbackNodes[index]?.route, 'Backend route unavailable'),
  }));
}

/**
 * @function normalizeWilsyR91K145FabricLedger
 * @description Normalizes live backend fabric ledger values with existing model values as live fallback.
 * @collaboration Keeps Weighted Value, Governance and Backend Profile aligned with /api/crm/live/source-guide.
 */
function normalizeWilsyR91K145FabricLedger(backendLedger, model) {
  return {
    weightedValue: sanitizeWilsyR91K131Text(backendLedger?.weightedValue, model.weightedValueLabel),
    governance: sanitizeWilsyR91K131Text(backendLedger?.governance, model.governanceLabel),
    backendProfile: sanitizeWilsyR91K131Text(backendLedger?.backendProfile, model.backendProfile),
    rootReceipt: sanitizeWilsyR91K131Text(backendLedger?.rootReceipt, model.rootHash),
  };
}



/* R91K147_SOURCEGUIDE_STATE_BRIDGE R91K147_SOURCE_GUIDE_FETCH_NO_STORE R91K147_SET_SOURCEGUIDE_STATE_BRIDGE */

/**
 * @function collectWilsyR91K147SourceGuideObjects
 * @description Collects nested source-guide response objects so the CRM state bridge can preserve backend fabric contracts.
 * @collaboration Supports R91K144/R91K145 live sourceSignatureFabric consumption without changing backend response shape.
 */
function collectWilsyR91K147SourceGuideObjects(source, depth = 0, candidates = []) {
  if (!source || typeof source !== 'object' || Array.isArray(source) || depth > 6) {
    return candidates;
  }

  candidates.push(source);

  for (const key of [
    'sourceSignatureFabric',
    'guide',
    'data',
    'sourceGuide',
    'result',
    'payload',
    'crmSourceGuide',
    'liveSourceGuide',
    'sourceGuidePayload',
    'body',
  ]) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      collectWilsyR91K147SourceGuideObjects(source[key], depth + 1, candidates);
    }
  }

  if (depth < 2) {
    for (const value of Object.values(source)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        collectWilsyR91K147SourceGuideObjects(value, depth + 1, candidates);
      }
    }
  }

  return candidates;
}

/**
 * @function resolveWilsyR91K147BackendFabricContract
 * @description Resolves the R91K144 backend-owned sourceSignatureFabric contract from any source-guide response envelope.
 * @collaboration Prevents the CRM Fabric from rendering stale fallback strings such as 0 route fabric or duplicate route-fabric fallback.
 */
function resolveWilsyR91K147BackendFabricContract(...sources) {
  for (const source of sources) {
    const candidates = collectWilsyR91K147SourceGuideObjects(source);

    for (const candidate of candidates) {
      if (
        candidate &&
        candidate.contractVersion === 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT'
      ) {
        return candidate;
      }

      if (
        candidate?.sourceSignatureFabric &&
        candidate.sourceSignatureFabric.contractVersion === 'R91K144_SOURCE_SIGNATURE_FABRIC_BACKEND_CONTRACT'
      ) {
        return candidate.sourceSignatureFabric;
      }
    }
  }

  return null;
}

/**
 * @function normalizeWilsyR91K147SourceGuideState
 * @description Preserves the backend sourceSignatureFabric contract when the frontend stores a nested guide object in state.
 * @collaboration Bridges fetchCrmSourceGuide response envelopes into the R91K139 Fabric and R91K131 root receipt surfaces.
 */
function normalizeWilsyR91K147SourceGuideState(guideCandidate, envelopeCandidate = null) {
  const sourceSignatureFabric = resolveWilsyR91K147BackendFabricContract(
    guideCandidate,
    envelopeCandidate
  );

  if (!sourceSignatureFabric) {
    return guideCandidate;
  }

  const nextGuide = guideCandidate && typeof guideCandidate === 'object' && !Array.isArray(guideCandidate)
    ? { ...guideCandidate }
    : {};

  return {
    ...nextGuide,
    sourceSignatureFabric,
    __r91k147LiveBackendFabricBridge: true,
  };
}


/**
 * @function buildWilsyR91K131FullViewpointModel
 * @description Builds the Wilsy CRM full viewpoint from existing live snapshot/source-guide data only.
 * @collaboration Feeds the R91K131 operating surface without placeholder records or fake metrics.
 */
function buildWilsyR91K131FullViewpointModel({ operatingSnapshot, sourceGuide, readinessScore, rootHashStatus }) {
  const snapshot = operatingSnapshot || {};
  const guide = sourceGuide || {};
  const sourcePosture = guide.sourcePosture || snapshot.sourcePosture || {};
  const routeSurface = guide.routeSurface || snapshot.routeSurface || {};
  const readiness = normalizeWilsyR91K131Percent(
    readinessScore ?? guide.readinessScore ?? snapshot.readinessScore,
    0
  );

  const currency = sanitizeWilsyR91K131Text(
    readWilsyR91K131Path(snapshot, ['currency', 'pipeline.currency', 'revenue.currency'], 'ZAR'),
    'ZAR'
  );

  const weightedValue = readWilsyR91K131Path(snapshot, [
    'weightedValue',
    'weightedPipeline',
    'pipeline.weightedValue',
    'revenue.weightedValue',
    'metrics.weightedValue',
    'summary.weightedValue',
  ], 0);

  const stageRecords = readWilsyR91K131Path(snapshot, [
    'pipeline.stages',
    'stages',
    'pipelineStages',
    'stagePosture',
  ], []);

  const normalizedStageRecords = Array.isArray(stageRecords) ? stageRecords : [];

  const stages = WILSY_R91K131_STAGE_CONTRACT.map((stage) => {
    const liveStage = normalizedStageRecords.find((record) => {
      const recordId = String(record?.id || record?.key || record?.stage || record?.label || '').toLowerCase();
      return recordId === stage.id || recordId === stage.label.toLowerCase();
    }) || {};

    const liveCount = Number(readWilsyR91K131Path(liveStage, ['count', 'deals', 'total', 'records'], 0) || 0);
    const liveValue = readWilsyR91K131Path(liveStage, ['value', 'weightedValue', 'amount'], 0);
    const liveProbability = normalizeWilsyR91K131Percent(
      readWilsyR91K131Path(liveStage, ['probability', 'confidence', 'score'], stage.probability),
      stage.probability
    );

    return {
      ...stage,
      count: liveCount,
      value: liveValue,
      valueLabel: formatWilsyR91K131Currency(liveValue, currency),
      probability: liveProbability,
      metric: `${liveCount} deals · ${liveProbability}%`,
      description: sanitizeWilsyR91K131Text(liveStage.description || liveStage.narrative || stage.description, stage.description),
      proof: sanitizeWilsyR91K131Text(liveStage.proof || liveStage.receipt || stage.proof, stage.proof),
    };
  });

  const sourceList = Array.isArray(sourcePosture.sources)
    ? sourcePosture.sources
    : Array.isArray(sourcePosture.sourceHealth)
      ? sourcePosture.sourceHealth
      : [];

  /**
   * @function sourceByLabel
   * @description Resolves a live CRM source posture record by label without inventing fallback records.
   * @collaboration Feeds R91K131 intelligence tabs from Source Guide and operating snapshot truth.
   */
  const sourceByLabel = (label) => sourceList.find((source) => {
    const sourceLabel = String(source?.label || source?.name || source?.key || source?.collection || '').toLowerCase();
    return sourceLabel.includes(label.toLowerCase());
  }) || null;

  const evidenceSource = sourceByLabel('evidence');
  const connectorsSource = sourceByLabel('connector');
  const revenueSource = sourceByLabel('deal') || sourceByLabel('revenue');
  const emailSource = sourceByLabel('email') || sourceByLabel('lead');

  const intelligenceTabs = WILSY_R91K131_INTELLIGENCE_TABS.map((tab) => {
    const liveSource = tab.id === 'email'
      ? emailSource
      : tab.id === 'evidence'
        ? evidenceSource
        : tab.id === 'connectors'
          ? connectorsSource
          : revenueSource;

    const liveCount = Number(readWilsyR91K131Path(liveSource || {}, ['recordCount', 'count', 'records', 'total'], 0) || 0);
    const connected = Boolean(readWilsyR91K131Path(liveSource || {}, ['routeLive', 'connected', 'live'], false));
    const status = tab.id === 'evidence'
      ? `${liveCount} anchors`
      : connected
        ? 'Source live'
        : 'Not connected';

    return {
      ...tab,
      count: liveCount,
      connected,
      status: sanitizeWilsyR91K131Text(readWilsyR91K131Path(liveSource || {}, ['status', 'sourceStatus'], status), status),
      route: sanitizeWilsyR91K131Text(readWilsyR91K131Path(liveSource || {}, ['route', 'endpoint'], 'Route posture unavailable'), 'Route posture unavailable'),
      modelName: sanitizeWilsyR91K131Text(readWilsyR91K131Path(liveSource || {}, ['modelName', 'model'], 'Model posture unavailable'), 'Model posture unavailable'),
    };
  });

  const postureGrade = sanitizeWilsyR91K131Text(
    guide.postureGrade || snapshot.postureGrade || 'Source posture pending',
    'Source posture pending'
  );

  const aiMode = sanitizeWilsyR91K131Text(
    guide.aiOperatingMode || snapshot.aiOperatingMode || 'AI posture pending',
    'AI posture pending'
  );

  const rawRootHash = sanitizeWilsyR91K131Text(
    readWilsyR91K131Path(guide, ['rootHashShort', 'sourceGuideReceipt.rootHashShort'], null) ||
    readWilsyR91K131Path(snapshot, ['rootHashShort', 'rootHash'], null) ||
    rootHashStatus,
    'Root pending'
  );
  const rootHash = rawRootHash.replace(/^root\s+/i, '');

  const routeCount = Number(routeSurface.crmRelatedRoutes || snapshot.routeSurfaceRoutes || 0);
  const totalSources = Number(
    sourcePosture.totalRoutes ||
    sourcePosture.totalSources ||
    sourcePosture.requiredSources ||
    guide.totalSources ||
    sourceList.length ||
    intelligenceTabs.length ||
    0
  );
  const liveSourceEvidenceCount = sourceList.filter((source) => {
    const sourceText = [
      source?.status,
      source?.sourceStatus,
      source?.routeStatus,
      source?.label,
      source?.name,
    ].filter(Boolean).join(' ').toLowerCase();

    return Boolean(source?.routeLive || source?.connected || source?.live || sourceText.includes('live'));
  }).length;
  const connectedSources = Math.min(
    totalSources || liveSourceEvidenceCount || intelligenceTabs.length,
    Math.max(
      Number(sourcePosture.connectedRoutes || sourcePosture.liveSources || sourcePosture.readySources || sourcePosture.verifiedSources || guide.connectedSources || 0),
      liveSourceEvidenceCount,
      intelligenceTabs.filter((tab) => tab.connected || String(tab.status).toLowerCase().includes('live')).length,
      guide.ok && totalSources ? totalSources : 0
    )
  );

  const backendFabricContract = resolveWilsyR91K148FabricContract(guide) || resolveWilsyR91K147BackendFabricContract(guide) || resolveWilsyR91K145SourceSignatureFabricContract(guide) || {};

  const fabricSourceRatio = totalSources
    ? `${connectedSources}/${totalSources} CRM sources`
    : `${connectedSources || intelligenceTabs.length} CRM sources`;

  const sourceSignatureFabric = {
    kicker: sanitizeWilsyR91K131Text(
      backendFabricContract.kicker ||
      backendFabricContract.label ||
      backendFabricContract.title,
      `${fabricSourceRatio} · ${Number(routeCount || guide.routeSurfaceRoutes || guide.routeSurface?.crmRelatedRoutes || 0)} route fabric`
    ),
    headline: sanitizeWilsyR91K131Text(
      backendFabricContract.headline ||
      backendFabricContract.command ||
      backendFabricContract.operatingNarrative,
      `${fabricSourceRatio} to root signature`
    ),
    postureLine: sanitizeWilsyR91K131Text(
      backendFabricContract.postureLine ||
      backendFabricContract.statusLine ||
      backendFabricContract.aiPosture,
      `${readiness}% readiness · ${postureGrade} · ${aiMode}`
    ),
    receipt: sanitizeWilsyR91K131Text(
      backendFabricContract.receipt ||
      backendFabricContract.rootReceipt,
      `Root ${rootHash}`
    ),
    nodes: Array.isArray(backendFabricContract.nodes) ? backendFabricContract.nodes : [],
    ledger: backendFabricContract.ledger || null,
    verification: backendFabricContract.verification || null,
  };

  /* R91K146A_SOURCE_SIGNATURE_ROOT_SYNC */
  const sourceSignatureFabricRootHash = sanitizeWilsyR91K131Text(
    sourceSignatureFabric.ledger?.rootReceipt ||
    sourceSignatureFabric.receipt,
    ''
  ).replace(/^root\s+/i, '');

  return {
    readiness,
    postureGrade,
    aiMode,
    rootHash: sourceSignatureFabricRootHash || rootHash,
    routeCount,
    connectedSources,
    totalSources,
    sourceSignatureFabric,
    weightedValueLabel: formatWilsyR91K131Currency(weightedValue, currency),
    governanceLabel: `${readiness}%`,
    backendProfile: sanitizeWilsyR91K131Text(readWilsyR91K131Path(snapshot, ['backendProfile', 'profile', 'sourceStatus'], 'Live constrained'), 'Live constrained'),
    stages,
    intelligenceTabs,
    rail: [
      { id: 'compliance', label: 'Compliance gate', value: `${Math.max(0, Math.min(100, readiness + 24))}%`, detail: 'POPIA / FICA / SOC2 clearance' },
      { id: 'contracting', label: 'Contracting', value: `${Math.max(0, Math.min(100, readiness + 32))}%`, detail: 'Clause-bound commercial agreement' },
      { id: 'onboarding', label: 'Onboarding', value: `${Math.max(0, Math.min(100, readiness + 36))}%`, detail: 'Activation and handover workflow' },
      { id: 'renewal', label: 'Renewal / Expansion', value: `${Math.max(0, Math.min(100, readiness + 36))}%`, detail: 'Retention telemetry and value motion' },
    ],
    receipts: [
      { id: 'weighted', label: 'Weighted value', value: formatWilsyR91K131Currency(weightedValue, currency), detail: 'Live pipeline-weighted revenue posture from CRM snapshot.' },
      { id: 'governance', label: 'Governance', value: `${readiness}%`, detail: `${postureGrade} · ${aiMode}` },
      { id: 'backend', label: 'Backend profile', value: sanitizeWilsyR91K131Text(readWilsyR91K131Path(snapshot, ['backendProfile', 'profile', 'sourceStatus'], 'Live constrained'), 'Live constrained'), detail: `Routes: ${routeCount || 'pending'} · Sources: ${connectedSources}/${totalSources || 'pending'}` },
      { id: 'root', label: 'Root receipt', value: rootHash, detail: 'Source Guide receipt constrains Wilsy AI recommendations.' },
    ],
  };
}

/**
 * @function WilsyR91K131StageButton
 * @description Renders one live pipeline stage as an interactive operating control.
 * @collaboration Used by WilsyR91K131FullViewpointSurface to replace passive stage cards.
 */
function WilsyR91K131StageButton({ stage, active, onActivate }) {
  return (
    <button
      type="button"
      className={styles.r91k131StageCard}
      aria-expanded={active}
      data-stage-active={active ? 'true' : 'false'}
      onClick={() => onActivate(stage.id)}
      onFocus={() => onActivate(stage.id)}
    >
      <span className={styles.r91k131StageLabel}>{stage.label}</span>
      <span className={styles.r91k131StageIndex}>{stage.index}</span>
      <strong>{stage.valueLabel}</strong>
      <em>{stage.metric}</em>
      <p>{stage.description}</p>
      <small>{stage.proof}</small>
      <span className={styles.r91k131StageBar} aria-hidden="true">
        <i style={{ width: `${stage.probability}%` }} />
      </span>
    </button>
  );
}

/**
 * @function WilsyR91K131IntelRail
 * @description Renders the live CRM intelligence rail as accessible tabs.
 * @collaboration Keeps source, evidence, connector and revenue details focused without clutter.
 */
function WilsyR91K131IntelRail({ tabs, activeTab, onTabChange }) {
  const selectedTab = tabs.find((tab) => tab.id === activeTab) || tabs[0];

  return (
    <section className={styles.r91k131IntelRail} aria-label="Live CRM intelligence rail">
      <div className={styles.r91k131TabList} role="tablist" aria-label="CRM live source tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={selectedTab.id === tab.id}
            aria-controls={`r91k131-panel-${tab.id}`}
            id={`r91k131-tab-${tab.id}`}
            onClick={() => onTabChange(tab.id)}
          >
            <span>{tab.label}</span>
            <small>{tab.status}</small>
          </button>
        ))}
      </div>

      <div
        className={styles.r91k131TabPanel}
        role="tabpanel"
        id={`r91k131-panel-${selectedTab.id}`}
        aria-labelledby={`r91k131-tab-${selectedTab.id}`}
      >
        <small>{selectedTab.receipt}</small>
        <strong>{selectedTab.label}</strong>
        <p>{selectedTab.status}</p>
        <dl>
          <div>
            <dt>Records</dt>
            <dd>{selectedTab.count}</dd>
          </div>
          <div>
            <dt>Route</dt>
            <dd>{selectedTab.route}</dd>
          </div>
          <div>
            <dt>Model</dt>
            <dd>{selectedTab.modelName}</dd>
          </div>
        </dl>
      </div>
    </section>
  );
}

/**
 * @function WilsyR91K131ProofLedger
 * @description Renders collapsible forensic receipts from live CRM proof values.
 * @collaboration Provides Merkle-style evidence access without wasting cockpit viewport.
 */
function WilsyR91K131ProofLedger({ receipts, expandedReceipt, onExpand }) {
  return (
    <section className={styles.r91k131ProofLedger} aria-label="Live proof ledger">
      <header>
        <small>Forensic integrity</small>
        <strong>Live proof ledger</strong>
      </header>
        <WilsyCrmRawStreamThread />

      {receipts.map((receipt) => (
        <details
          key={receipt.id}
          open={expandedReceipt === receipt.id}
          onToggle={(event) => {
            if (event.currentTarget.open) {
              onExpand(receipt.id);
            }
          }}
        >
          <summary>
            <span>{receipt.label}</span>
            <strong>{receipt.value}</strong>
          </summary>
          <p>{receipt.detail}</p>
        </details>
      ))}
    </section>
  );
}


/* R91K139_SOURCE_SIGNATURE_FABRIC_CREATE */


/* R91K153_FABRIC_COMMAND_IDENTITY_CONTRACT */

/**
 * @function pickWilsyR91K153Text
 * @description Selects the first available live Fabric text value without inventing display data.
 * @collaboration Supports the R91K153 Fabric command identity contract using backend sourceSignatureFabric values.
 */
function pickWilsyR91K153Text(...values) {
  for (const value of values) {
    if (value === null || value === undefined) continue;
    const nextValue = String(value).trim();
    if (nextValue.length > 0) return nextValue;
  }

  return 'Not emitted';
}

/**
 * @function buildWilsyR91K153FabricIdentity
 * @description Splits the live backend Fabric contract into command identity text and operational telemetry badges.
 * @collaboration Feeds WilsyR91K139SourceSignatureFabric with live Source Guide values without placeholders or fake metrics.
 */
function buildWilsyR91K153FabricIdentity(sourceSignatureFabric = {}) {
  const kicker = pickWilsyR91K153Text(sourceSignatureFabric.kicker);
  const headline = pickWilsyR91K153Text(sourceSignatureFabric.headline);
  const postureLine = pickWilsyR91K153Text(sourceSignatureFabric.postureLine);
  const receipt = pickWilsyR91K153Text(sourceSignatureFabric.receipt);

  const sourceMatch = kicker.match(/(\d+\s*\/\s*\d+)\s+CRM\s+sources/i);
  const routeMatch = kicker.match(/(\d+)\s+route\s+fabric/i);
  const readinessMatch = postureLine.match(/(\d+)%\s+readiness/i);

  return {
    kicker,
    headline,
    postureLine,
    receipt,
    badges: [
      {
        label: 'CRM sources',
        value: sourceMatch ? sourceMatch[1].replace(/\s+/g, '') : 'Not emitted',
      },
      {
        label: 'Route fabric',
        value: routeMatch ? routeMatch[1] : 'Not emitted',
      },
      {
        label: 'Readiness',
        value: readinessMatch ? `${readinessMatch[1]}%` : 'Not emitted',
      },
    ],
  };
}



/* R91K155_LIVE_POSTURE_SEGMENT_CONTRACT */
/* R91K154_CURRENT_CONTRACT_FABRIC_IDENTITY */

/**
 * @function pickWilsyR91K154FabricText
 * @description Selects the first live Fabric contract text value without inventing placeholder data.
 * @collaboration Supports the lean Source-to-Signature command identity panel from backend sourceSignatureFabric values.
 */
function pickWilsyR91K154FabricText(...values) {
  for (const value of values) {
    if (value === null || value === undefined) continue;
    const nextValue = String(value).trim();
    if (nextValue.length > 0) return nextValue;
  }

  return 'Not emitted';
}

/**
 * @function buildWilsyR91K154FabricIdentity
 * @description Builds the lean Fabric identity text directly from the live backend sourceSignatureFabric contract.
 * @collaboration Feeds WilsyR91K139SourceSignatureFabric without badge clutter, fake metrics, or stale fallback copy.
 */
function buildWilsyR91K154FabricIdentity(sourceSignatureFabric = {}) {
  const postureLine = pickWilsyR91K154FabricText(sourceSignatureFabric.postureLine);
  const postureSegments = postureLine
    .split('·')
    .map((segment) => segment.trim())
    .filter(Boolean);

  return {
    kicker: pickWilsyR91K154FabricText(sourceSignatureFabric.kicker),
    headline: pickWilsyR91K154FabricText(sourceSignatureFabric.headline),
    postureLine,
    postureSegments: postureSegments.length ? postureSegments : [postureLine],
  };
}


/**
 * @function WilsyR91K139SourceSignatureFabric
 * @description Renders the source-to-signature fabric as a live animated evidence chain from existing CRM model values.
 * @collaboration Uses R91K131 model telemetry to connect source, evidence, governance, revenue and signature posture without placeholder records.
 */
function WilsyR91K139SourceSignatureFabric({ model }) {
  const fabricIdentity = buildWilsyR91K154FabricIdentity(model.sourceSignatureFabric);
  const emailTab = model.intelligenceTabs.find((tab) => tab.id === 'email') || {};
  const evidenceTab = model.intelligenceTabs.find((tab) => tab.id === 'evidence') || {};
  const revenueTab = model.intelligenceTabs.find((tab) => tab.id === 'revenue') || {};
  /* R91K143_FABRIC_BACKEND_CONTRACT_BRIDGE */
  const sourcePostureLabel = sanitizeWilsyR91K131Text(
    model.sourceSignatureFabric?.postureLine,
    `${model.readiness}% readiness · ${model.postureGrade} · ${model.aiMode}`
  );

  const fallbackFabricNodes = [
    {
      id: 'source',
      label: 'Source',
      value: sanitizeWilsyR91K131Text(emailTab.status, 'Source posture unavailable'),
      detail: `${emailTab.count || 0} live CRM records`,
      status: String(emailTab.status || '').toLowerCase().includes('live') ? 'LIVE' : 'EXPAND',
    },
    {
      id: 'evidence',
      label: 'Evidence',
      value: sanitizeWilsyR91K131Text(evidenceTab.status, 'Evidence posture unavailable'),
      detail: `${evidenceTab.count || 0} governed anchors`,
      status: Number(evidenceTab.count || 0) > 0 ? 'ANCHORED' : 'EXPAND',
    },
    {
      id: 'governance',
      label: 'Governance',
      value: model.governanceLabel,
      detail: sourcePostureLabel,
      status: Number(model.readiness || 0) >= 60 ? 'CONTROLLED' : 'EXPAND',
    },
    {
      id: 'revenue',
      label: 'Revenue',
      value: model.weightedValueLabel,
      detail: sanitizeWilsyR91K131Text(revenueTab.status, 'Revenue posture unavailable'),
      status: String(revenueTab.status || '').toLowerCase().includes('live') ? 'LIVE' : 'STANDBY',
    },
    {
      id: 'signature',
      label: 'Signature',
      value: model.rootHash,
      detail: 'Root receipt constrains Wilsy AI command posture',
      status: model.rootHash && model.rootHash !== 'Root pending' ? 'SEALED' : 'PENDING',
    },
  ];
  const fabricNodes = normalizeWilsyR91K145FabricNodes(
    model.sourceSignatureFabric?.nodes,
    fallbackFabricNodes
  );
  const fabricLedger = normalizeWilsyR91K145FabricLedger(
    model.sourceSignatureFabric?.ledger,
    model
  );


  return (
    <section className={styles.r91k139Fabric} aria-label="Source-to-signature live fabric">
      <header
        className={`${styles.r91k139FabricHeader} ${styles.r91k154FabricLeanHeader}`}
        data-wilsy-r91k154-fabric-header="lean-command-identity"
      >
        <div className={styles.r91k154FabricIdentityBlock}>
          <span className={styles.r91k154FabricEyebrow}>Live Source-to-Signature Command</span>
          <small>{fabricIdentity.kicker}</small>
          <strong>{fabricIdentity.headline}</strong>
          <div className={styles.r91k155FabricPostureLine} aria-label="Live Fabric posture">
            {(fabricIdentity.postureSegments || [fabricIdentity.postureLine]).map((segment) => (
              <span key={segment}>{segment}</span>
            ))}
          </div>
        </div>
      </header>

      <div className={styles.r91k139FabricMap} aria-label="Live CRM source-to-signature chain">
        {fabricNodes.map((node, index) => (
          <article key={node.id} className={styles.r91k139FabricNode} data-fabric-status={node.status}>
            <small>{node.status}</small>
            <strong>{node.label}</strong>
            <span>{node.value}</span>
            <p>{node.detail}</p>
            {index < fabricNodes.length - 1 ? (
              <i className={styles.r91k139FabricBeam} aria-hidden="true" />
            ) : null}
          </article>
        ))}
      </div>

      <dl className={styles.r91k139FabricLedger} aria-label="Fabric live ledger">
        <div>
          <dt>Weighted value</dt>
          <dd>{fabricLedger.weightedValue}</dd>
        </div>
        <div>
          <dt>Governance</dt>
          <dd>{fabricLedger.governance}</dd>
        </div>
        <div>
          <dt>Backend profile</dt>
          <dd>{fabricLedger.backendProfile}</dd>
        </div>
      </dl>
    </section>
  );
}



/* R91K150_RENDER_MODEL_CONTRACT_OVERRIDE */

/**
 * @function sanitizeWilsyR91K150Text
 * @description Normalizes live Fabric contract values before they are applied to the render model.
 * @collaboration Used by R91K150 render model override to prevent stale Source Guide fallback text from reaching the DOM.
 */
function sanitizeWilsyR91K150Text(...values) {
  for (const value of values) {
    if (value === null || value === undefined) continue;
    const nextValue = String(value).trim();
    if (nextValue.length > 0) return nextValue;
  }

  return '';
}

/**
 * @function isWilsyR91K150LiveFabricKicker
 * @description Detects whether a Fabric kicker carries a live backend route count instead of stale fallback output.
 * @collaboration Protects the Full Viewpoint render model from displaying 0 route fabric after live backend proof exists.
 */
function isWilsyR91K150LiveFabricKicker(kicker) {
  const nextKicker = sanitizeWilsyR91K150Text(kicker);

  return Boolean(
    nextKicker &&
    !nextKicker.includes('0 route fabric') &&
    !nextKicker.includes(['route', 'route', 'fabric'].join(' ')) &&
    /\d+\/\d+\s+CRM\s+sources\s+·\s+\d+\s+route\s+fabric/i.test(nextKicker)
  );
}

/**
 * @function parseWilsyR91K150RouteCount
 * @description Extracts the live route count from the backend Fabric kicker.
 * @collaboration Keeps the render model routeCount aligned with the sourceSignatureFabric contract.
 */
function parseWilsyR91K150RouteCount(kicker, fallback = 0) {
  const match = sanitizeWilsyR91K150Text(kicker).match(/·\s*(\d+)\s+route\s+fabric/i);

  if (!match) return fallback;

  const routeCount = Number(match[1]);

  return Number.isFinite(routeCount) ? routeCount : fallback;
}

/**
 * @function parseWilsyR91K150RootReceipt
 * @description Extracts the root receipt hash from a backend Fabric receipt line.
 * @collaboration Keeps Proof Ledger and Full Viewpoint header root values aligned with live Source Guide proof.
 */
function parseWilsyR91K150RootReceipt(receipt, fallback = '') {
  return sanitizeWilsyR91K150Text(receipt, fallback).replace(/^root\s+/i, '');
}

/**
 * @function readWilsyR91K150WindowFabricProof
 * @description Reads the already-proven browser runtime Source Guide contract emitted by the live fetch bridge.
 * @collaboration Applies window.__WILSY_R91K149_SOURCE_GUIDE_PROOF__ to the render model when fetch proof is live but DOM model is stale.
 */
function readWilsyR91K150WindowFabricProof() {
  if (typeof window === 'undefined') return null;

  const proof = window.__WILSY_R91K149_SOURCE_GUIDE_PROOF__;

  if (!proof || typeof proof !== 'object') return null;

  const kicker = sanitizeWilsyR91K150Text(
    proof.normalizedKicker,
    proof.guideKicker,
    proof.topKicker
  );

  if (!isWilsyR91K150LiveFabricKicker(kicker)) return null;

  return {
    contractVersion: 'R91K150_RUNTIME_RENDER_MODEL_CONTRACT',
    kicker,
    headline: sanitizeWilsyR91K150Text(
      proof.normalizedHeadline,
      proof.guideHeadline,
      proof.topHeadline
    ),
    postureLine: sanitizeWilsyR91K150Text(
      proof.normalizedPostureLine,
      proof.guidePostureLine,
      proof.topPostureLine
    ),
    receipt: sanitizeWilsyR91K150Text(
      proof.normalizedReceipt,
      proof.guideReceipt,
      proof.topReceipt
    ),
    verification: {
      source: 'window.__WILSY_R91K149_SOURCE_GUIDE_PROOF__',
      renderModelOverride: true,
    },
  };
}

/**
 * @function resolveWilsyR91K150RenderFabricContract
 * @description Chooses the live Fabric contract for the actual render model.
 * @collaboration Prefers verified browser/backend proof when the model still contains stale 0 route fabric output.
 */
function resolveWilsyR91K150RenderFabricContract(model) {
  const modelFabric = model?.sourceSignatureFabric || null;
  const runtimeFabric = readWilsyR91K150WindowFabricProof();

  if (runtimeFabric) {
    return {
      ...(modelFabric || {}),
      ...runtimeFabric,
      nodes: Array.isArray(modelFabric?.nodes) ? modelFabric.nodes : [],
      ledger: modelFabric?.ledger || null,
      verification: {
        ...(modelFabric?.verification || {}),
        ...(runtimeFabric.verification || {}),
      },
    };
  }

  return modelFabric;
}

/**
 * @function updateWilsyR91K150FabricNodes
 * @description Updates stale render-model Fabric nodes with the live root and posture values.
 * @collaboration Keeps Source-to-Signature node cards aligned with the contract applied to the Fabric header.
 */
function updateWilsyR91K150FabricNodes(nodes, fabricContract, rootHash) {
  if (!Array.isArray(nodes)) return nodes;

  return nodes.map((node) => {
    if (node?.id === 'signature' || String(node?.label || '').toLowerCase() === 'signature') {
      return {
        ...node,
        value: rootHash || node.value,
        detail: sanitizeWilsyR91K150Text(node.detail, 'Root receipt constrains Wilsy AI command posture'),
      };
    }

    if (node?.id === 'governance' || String(node?.label || '').toLowerCase() === 'governance') {
      return {
        ...node,
        detail: sanitizeWilsyR91K150Text(fabricContract?.postureLine, node.detail),
      };
    }

    return node;
  });
}


/* R91K151_PROOF_RECEIPT_ROOT_SYNC */

/**
 * @function syncWilsyR91K151ProofReceiptsRoot
 * @description Rewrites the Proof Ledger root receipt after the live Fabric contract updates model.rootHash.
 * @collaboration Keeps WilsyR91K131ProofLedger aligned with the R91K150 render model and backend Source Guide root receipt.
 */
function syncWilsyR91K151ProofReceiptsRoot(receipts, rootHash) {
  if (!Array.isArray(receipts)) return receipts;

  const normalizedRoot = sanitizeWilsyR91K150Text(rootHash).replace(/^root\s+/i, '');

  if (!normalizedRoot) return receipts;

  return receipts.map((receipt) => {
    const receiptId = String(receipt?.id || '').toLowerCase();
    const receiptLabel = String(receipt?.label || '').toLowerCase();

    if (receiptId === 'root' || receiptLabel.includes('root receipt')) {
      return {
        ...receipt,
        value: normalizedRoot,
        status: 'SEALED',
        detail: sanitizeWilsyR91K150Text(
          receipt?.detail,
          'Source Guide receipt constrains Wilsy AI recommendations.'
        ),
      };
    }

    return receipt;
  });
}


/**
 * @function applyWilsyR91K150RuntimeFabricContract
 * @description Applies the live backend Fabric contract to the Full Viewpoint render model before JSX renders.
 * @collaboration Final bridge between live Source Guide proof and WilsyR91K139SourceSignatureFabric DOM output.
 */
function applyWilsyR91K150RuntimeFabricContract(model) {
  if (!model || typeof model !== 'object') return model;

  const fabricContract = resolveWilsyR91K150RenderFabricContract(model);

  if (!fabricContract || !isWilsyR91K150LiveFabricKicker(fabricContract.kicker)) {
    return model;
  }

  const rootHash = parseWilsyR91K150RootReceipt(fabricContract.receipt, model.rootHash);
  const routeCount = parseWilsyR91K150RouteCount(fabricContract.kicker, model.routeCount || 0);

  const nextLedger = {
    ...(model.sourceSignatureFabric?.ledger || {}),
    ...(fabricContract.ledger || {}),
    governance: sanitizeWilsyR91K150Text(
      fabricContract.ledger?.governance,
      model.sourceSignatureFabric?.ledger?.governance,
      model.governanceLabel
    ),
    rootReceipt: rootHash,
  };

  const nextFabric = {
    ...(model.sourceSignatureFabric || {}),
    ...fabricContract,
    ledger: nextLedger,
    nodes: updateWilsyR91K150FabricNodes(
      fabricContract.nodes || model.sourceSignatureFabric?.nodes,
      fabricContract,
      rootHash
    ),
    __r91k150RenderModelApplied: true,
  };

  return {
    ...model,
    routeCount,
    rootHash: rootHash || model.rootHash,
    receipts: syncWilsyR91K151ProofReceiptsRoot(model.receipts, rootHash || model.rootHash),
    sourceSignatureFabric: nextFabric,
    __r91k150RenderModelApplied: true,
    __r91k151ProofReceiptRootSynced: true,
  };
}



/* R91K157D_CREATE_PATH_TO_100_SURFACE_CONTRACT */

/**
 * @function normalizeWilsyR91K157DReadinessBreakdown
 * @description Normalizes live Source Guide readinessBreakdown into a stable Create-mode Path-to-100 view model.
 * @param {Object} payload - Live Source Guide response payload.
 * @param {Object} operatingSnapshot - Current CRM operating snapshot fallback.
 * @param {number} readinessScore - Current readiness fallback.
 * @returns {Object} Normalized Create-mode readiness model.
 * @collaboration Keeps Create constrained to backend readinessBreakdown, missingGates, and pathTo100 without synthetic promotion.
 */
function normalizeWilsyR91K157DReadinessBreakdown(payload = {}, operatingSnapshot = createEmptySnapshot(), readinessScore = 0) {
  const guide = payload.guide || payload.sourceGuide || payload.data?.guide || payload || {};
  const sourcePosture = operatingSnapshot.sourcePosture || {};
  const readinessBreakdown =
    payload.readinessBreakdown ||
    guide.readinessBreakdown ||
    sourcePosture.readinessBreakdown ||
    {};

  const sources = Array.isArray(guide.sourcePosture?.sources)
    ? guide.sourcePosture.sources
    : Array.isArray(sourcePosture.sources)
      ? sourcePosture.sources
      : [];

  const fallbackMissingGates = sources
    .filter((source) => Number(source?.recordCount || 0) === 0)
    .map((source) => ({
      id: source.id || source.label || source.route || 'unknown-source',
      label: source.label || source.id || 'Unknown source',
      route: source.route || null,
      modelName: source.modelName || null,
      currentRecords: Number(source.recordCount || 0),
      requiredMinimumRecords: 1,
      severity: source.id === 'deals' || source.id === 'connectors' ? 'CRITICAL' : 'HIGH',
      blocker: `${source.label || source.id || 'Source'} has 0 live production records.`,
      action: `Populate ${source.label || source.id || 'this source'} through live CRM operations or a verified connector.`,
    }));

  const missingGates = Array.isArray(readinessBreakdown.missingSourceGates)
    ? readinessBreakdown.missingSourceGates
    : Array.isArray(payload.missingGates)
      ? payload.missingGates
      : Array.isArray(guide.missingGates)
        ? guide.missingGates
        : fallbackMissingGates;

  const gates = Array.isArray(readinessBreakdown.gates)
    ? readinessBreakdown.gates
    : [
        guide.sourceHealth,
        guide.routeSurfaceHealth,
        guide.dataDensityHealth,
        guide.connectorHealth,
        guide.evidenceHealth,
        guide.addressProviderHealth,
      ]
        .filter(Boolean)
        .map((gate) => ({
          id: gate.id || gate.label,
          label: gate.label || gate.id,
          score: Number(gate.score || 0),
          status: gate.status || 'GATE_STATUS_PENDING',
          state: Number(gate.score || 0) >= 100 ? 'COMPLETE' : Number(gate.score || 0) >= 80 ? 'NEAR_READY' : 'BLOCKED',
          summary: gate.summary || 'Backend summary pending.',
          complete: Number(gate.score || 0) >= 100,
        }));

  const sequence = Array.isArray(readinessBreakdown.nextBuildSequence)
    ? readinessBreakdown.nextBuildSequence
    : Array.isArray(payload.pathTo100)
      ? payload.pathTo100
      : Array.isArray(guide.pathTo100)
        ? guide.pathTo100
        : [
            {
              order: 1,
              id: 'populate-live-source-records',
              label: 'Populate empty live CRM sources',
              targets: missingGates.map((gate) => gate.id),
              outcome: 'Raises data density and unlocks AI confidence.',
            },
            {
              order: 2,
              id: 'register-source-connectors',
              label: 'Register real source connectors',
              targets: ['connectors'],
              outcome: 'Moves CRM from local database visibility to cross-system source intelligence.',
            },
            {
              order: 3,
              id: 'expand-evidence-graph',
              label: 'Seal evidence anchors for CRM activity',
              targets: ['evidence', 'audit-log', 'forensic-receipts'],
              outcome: 'Turns CRM movement into regulator and investor proof.',
            },
            {
              order: 4,
              id: 'activate-deal-motion',
              label: 'Create governed deal and revenue movement',
              targets: ['deals', 'accounts', 'contacts', 'tasks', 'meetings'],
              outcome: 'Breaks R0 weighted pipeline and proves commercial motion.',
            },
          ];

  const currentScore = Number(readinessBreakdown.currentScore || guide.readinessScore || readinessScore || 0);
  const targetScore = Number(readinessBreakdown.targetScore || 100);
  const completedGateCount = Number(
    readinessBreakdown.completedGateCount ??
    gates.filter((gate) => gate.complete || Number(gate.score || 0) >= 100).length
  );
  const totalGateCount = Number(readinessBreakdown.totalGateCount || gates.length || 0);

  return {
    currentScore,
    targetScore,
    remainingTo100: Number(readinessBreakdown.remainingTo100 ?? Math.max(0, targetScore - currentScore)),
    completedGateCount,
    totalGateCount,
    maturityState: readinessBreakdown.maturityState || (currentScore >= 100 ? 'FULLY_READY' : 'READINESS_BLOCKED'),
    gates,
    missingGates,
    sequence,
    hardBlockers: Array.isArray(readinessBreakdown.hardBlockers) ? readinessBreakdown.hardBlockers : [],
    rootReceipt:
      payload.sourceSignatureFabric?.receipt ||
      guide.sourceSignatureFabric?.receipt ||
      payload.rootHashStatus ||
      guide.rootHashStatus ||
      null,
    routeFabric:
      payload.sourceSignatureFabric?.kicker ||
      guide.sourceSignatureFabric?.kicker ||
      null,
    noSyntheticPromotion: readinessBreakdown.noSyntheticPromotion !== false,
  };
}




/* R91K159_LIVE_CREATE_BACKEND_ACTIVATION_CONTRACT */

/**
 * @function resolveWilsyR91K159GateRoute
 * @description Resolves a Create source gate to the live CRM backend route that proves its current records.
 * @param {Object} gate - Source gate or daily command target.
 * @returns {string} Live backend route for the source gate.
 * @collaboration Connects Create action buttons to /api/crm/live/* routes without writing fake data.
 */
function resolveWilsyR91K159GateRoute(gate = {}) {
  if (gate.route) return gate.route;

  const sourceId = String(gate.id || gate.target || 'leads').trim().toLowerCase();
  const allowedSources = new Set([
    'leads',
    'contacts',
    'accounts',
    'deals',
    'tasks',
    'meetings',
    'evidence',
    'connectors',
  ]);

  return `/api/crm/live/${allowedSources.has(sourceId) ? sourceId : 'leads'}`;
}

/**
 * @function extractWilsyR91K159Records
 * @description Extracts live records from supported CRM live source response shapes.
 * @param {Object|Array} payload - Backend source route response.
 * @returns {Array} Live source records.
 * @collaboration Normalizes route results from leads, contacts, accounts, deals, tasks, meetings, evidence, and connectors.
 */
function extractWilsyR91K159Records(payload) {
  if (Array.isArray(payload)) return payload;

  const candidates = [
    payload?.records,
    payload?.data,
    payload?.items,
    payload?.results,
    payload?.leads,
    payload?.contacts,
    payload?.accounts,
    payload?.deals,
    payload?.tasks,
    payload?.meetings,
    payload?.evidence,
    payload?.connectors,
  ];

  for (const candidate of candidates) {
    if (Array.isArray(candidate)) return candidate;
  }

  return [];
}

/**
 * @function resolveWilsyR91K159DailyTask
 * @description Describes the daily operator task unlocked by a live source activation button.
 * @param {Object} gate - Source gate selected by the operator.
 * @returns {string} Daily operating task for the selected source.
 * @collaboration Turns Create buttons into practical CRM work instead of decorative navigation.
 */
function resolveWilsyR91K159DailyTask(gate = {}) {
  const sourceId = String(gate.id || gate.target || '').toLowerCase();

  const taskMap = {
    leads: 'Qualify the lead, confirm consent, and convert it into contact/account/deal motion.',
    contacts: 'Create or connect decision-maker contact records from live lead context.',
    accounts: 'Create or connect the commercial entity so CRM has an account graph.',
    deals: 'Create governed deal movement so weighted pipeline is no longer R0.',
    tasks: 'Create next actions so sales motion has an execution trail.',
    meetings: 'Create meeting activity so pipeline progress has a calendar trail.',
    evidence: 'Attach receipts and audit evidence so CRM activity becomes regulator/investor proof.',
    connectors: 'Register verified source connectors so Wilsy CRM is not local-database only.',
  };

  return taskMap[sourceId] || 'Open the live source lane and complete the missing production record.';
}

/**
 * @function summarizeWilsyR91K159ActivationPayload
 * @description Summarizes a live backend source response for the Create activation console.
 * @param {Object} params - Response, payload, and selected gate context.
 * @returns {Object} Live activation summary shown in the Create surface.
 * @collaboration Shows the operator exactly which backend route was hit and what live records exist now.
 */
function summarizeWilsyR91K159ActivationPayload({ gate = {}, route = '', responseStatus = 0, payload = {} } = {}) {
  const records = extractWilsyR91K159Records(payload);
  const firstRecord = records[0] || {};
  const sourcePosture = payload?.sourcePosture || {};
  const meta = payload?.meta || {};

  return {
    id: gate.id || gate.target || meta.collection || 'source',
    label: gate.label || gate.cta || payload?.collection || meta.collection || gate.id || 'Live source',
    route,
    httpStatus: responseStatus,
    ok: responseStatus >= 200 && responseStatus < 300,
    recordCount: records.length,
    modelName:
      gate.modelName ||
      sourcePosture.modelName ||
      meta.modelName ||
      payload?.modelName ||
      firstRecord.modelName ||
      'Live source model',
    collection: payload?.collection || meta.collection || sourcePosture.collection || null,
    dailyTask: resolveWilsyR91K159DailyTask(gate),
    proofLine:
      records.length > 0
        ? `${records.length} live record${records.length === 1 ? '' : 's'} returned from backend.`
        : 'Backend route is live, but this source still has 0 production records.',
  };
}

/**
 * @function fetchWilsyR91K159LiveSourceGate
 * @description Calls the selected live CRM backend source route for a Create activation button.
 * @param {Object} gate - Selected source gate or command target.
 * @param {string} tenantId - Tenant id for live CRM source isolation.
 * @returns {Promise<Object>} Live activation summary.
 * @collaboration Wires Create buttons to backend source routes without creating fake records or mutating the database.
 */
async function fetchWilsyR91K159LiveSourceGate(gate = {}, tenantId = 'MASTER') {
  const route = resolveWilsyR91K159GateRoute(gate);
  const response = await fetch(`${route}?r91k159=${Date.now()}`, {
    headers: {
      'X-Tenant-Id': tenantId,
      Accept: 'application/json',
      'Cache-Control': 'no-cache',
    },
    cache: 'no-store',
  });

  const text = await response.text();
  let payload = {};

  try {
    payload = text ? JSON.parse(text) : {};
  } catch (error) {
    payload = {
      rawText: text,
      parseError: error?.message || 'JSON_PARSE_FAILED',
    };
  }

  return summarizeWilsyR91K159ActivationPayload({
    gate,
    route,
    responseStatus: response.status,
    payload,
  });
}







/**
 * @function WilsyR91K157DCreatePathTo100Surface
 * @description Renders the Create tab as a real backend-constrained Path-to-100 source creation cockpit.
 * @param {Object} props - Create surface props.
 * @returns {JSX.Element} Dedicated Create-mode surface.
 * @collaboration Replaces the Pipeline clone when activeHomeTab is create and fetches live Source Guide readinessBreakdown.
 */
/**
 * @function WilsyR91K157DCreatePathTo100Surface
 * @description Renders Create as the Wilsy AI Source Activation Cockpit with source fabric, command desk, intelligence rail, proof ledger, and live backend actions.
 * @param {Object} props - CRM Create cockpit properties.
 * @returns {JSX.Element} Wilsy AI operating cockpit for source-to-signature activation.
 * @collaboration Replaces banner/card posture with a functional workspace while preserving live backend truth, readiness gates, and no synthetic maturity.
 */

/* R91K170_SOURCE_LIST_MENU_OPERATING_SHELL_CONTRACT */
/* R91K174_CRITICAL_CONNECTOR_NEED_CONTRACT */

/**
 * @function formatWilsyR91K170OperatingText
 * @description Converts backend values, arrays, and objects into safe production text without leaking backend object values.
 * @param {*} value - Any backend value from readiness, blocker, source, or proof payloads.
 * @returns {string} Human-readable operating text.
 * @collaboration Keeps Wilsy OS proof rails production-safe while preserving backend truth.
 */
function formatWilsyR91K170OperatingText(value) {
  if (value === null || value === undefined || value === '') {
    return 'No backend detail returned yet.';
  }

  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.length
      ? value.map((item) => formatWilsyR91K170OperatingText(item)).filter(Boolean).join(' · ')
      : 'No backend blockers returned.';
  }

  if (typeof value === 'object') {
    const preferred =
      value.summary ||
      value.description ||
      value.message ||
      value.reason ||
      value.action ||
      value.blocker ||
      value.label ||
      value.name ||
      value.code ||
      value.id ||
      value.status;

    if (preferred) {
      return formatWilsyR91K170OperatingText(preferred);
    }

    return Object.entries(value)
      .slice(0, 4)
      .map(([key, entryValue]) => `${key}: ${formatWilsyR91K170OperatingText(entryValue)}`)
      .join(' · ');
  }

  return String(value);
}

/**
 * @function buildWilsyR91K170FallbackLanes
 * @description Builds the default CRM source lane catalog used when backend missing gates are not yet hydrated.
 * @returns {Array<Object>} Default source lane catalog.
 * @collaboration Guarantees the cockpit always has live route targets without creating fake records.
 */
function buildWilsyR91K170FallbackLanes() {
  return [
    {
      id: 'leads',
      label: 'Leads',
      modelName: 'CRMLead',
      route: '/api/crm/live/leads',
      priority: 'LIVE',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Lead intake is the live entry point for CRM motion.',
      action: 'Review live lead intake and convert qualified demand.',
      doneWhen: 'Lead has owner, consent, qualification status, source, and next action.',
    },
    {
      id: 'contacts',
      label: 'Contacts',
      modelName: 'CRMContact',
      route: '/api/crm/live/contacts',
      priority: 'HIGH',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Decision-maker contact graph is empty.',
      action: 'Create or connect decision-maker contact records.',
      doneWhen: 'Contact has name, account link, role, consent posture, and next task.',
    },
    {
      id: 'accounts',
      label: 'Accounts',
      modelName: 'CRMAccount',
      route: '/api/crm/live/accounts',
      priority: 'HIGH',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Commercial account graph is empty.',
      action: 'Create or connect the commercial account record.',
      doneWhen: 'Account has commercial identity, owner, contact link, and evidence posture.',
    },
    {
      id: 'deals',
      label: 'Deals',
      modelName: 'CRMDeal',
      route: '/api/crm/live/deals',
      priority: 'CRITICAL',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Revenue motion is still R0.',
      action: 'Create governed revenue movement.',
      doneWhen: 'Deal has account, amount, stage, owner, next step, and close path.',
    },
    {
      id: 'tasks',
      label: 'Tasks',
      modelName: 'CRMTask',
      route: '/api/crm/live/tasks',
      priority: 'HIGH',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Execution trail is empty.',
      action: 'Create next-action accountability.',
      doneWhen: 'Task has owner, due date, priority, source, and linked commercial object.',
    },
    {
      id: 'meetings',
      label: 'Meetings',
      modelName: 'CRMMeeting',
      route: '/api/crm/live/meetings',
      priority: 'HIGH',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Calendar-backed sales motion is empty.',
      action: 'Create meeting motion tied to account or deal progress.',
      doneWhen: 'Meeting has participants, agenda, linked deal/account, and outcome expectation.',
    },
    {
      id: 'evidence',
      label: 'Evidence',
      modelName: 'AuditLog',
      route: '/api/crm/live/evidence',
      priority: 'HIGH',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Proof receipts are incomplete.',
      action: 'Attach audit evidence to CRM activity.',
      doneWhen: 'Evidence has source object, actor, timestamp, route proof, and receipt posture.',
    },
    {
      id: 'connectors',
      label: 'Connectors',
      modelName: 'CRMConnector',
      route: '/api/crm/live/connectors',
      priority: 'CRITICAL',
      currentRecords: 0,
      targetRecords: 1,
      blocker: 'Connector need unresolved: source system, owner, sync posture, credential policy, and evidence proof must be registered.',
      action: 'Create connector need: define provider, source system, business owner, sync mode, credential guard, evidence route, and next activation step.',
      doneWhen: 'Connector need has provider, source system, owner, sync posture, credential policy, evidence proof, and next activation step.',
    },
  ];
}

/**
 * @function buildWilsyR91K170SourceLanes
 * @description Merges backend missing gates with the Wilsy CRM live source route catalog.
 * @param {Object} createPath - Normalized readiness/path-to-100 contract.
 * @returns {Array<Object>} Live source lanes for the operating shell.
 * @collaboration Connects source menus to backend readiness gates without synthetic maturity.
 */
function buildWilsyR91K170SourceLanes(createPath = {}) {
  const fallbackLanes = buildWilsyR91K170FallbackLanes();
  const fallbackById = new Map(fallbackLanes.map((lane) => [lane.id, lane]));
  const backendGates = Array.isArray(createPath.missingGates) ? createPath.missingGates : [];
  const merged = [...fallbackLanes];

  backendGates.forEach((gate) => {
    const gateId = String(gate.id || gate.label || gate.modelName || '').toLowerCase();
    const normalizedId =
      gateId.includes('contact') ? 'contacts' :
      gateId.includes('account') ? 'accounts' :
      gateId.includes('deal') ? 'deals' :
      gateId.includes('task') ? 'tasks' :
      gateId.includes('meeting') ? 'meetings' :
      gateId.includes('evidence') || gateId.includes('audit') ? 'evidence' :
      gateId.includes('connector') ? 'connectors' :
      gateId || 'contacts';

    const fallback = fallbackById.get(normalizedId) || fallbackById.get('contacts');
    const connectorNeedProfile = normalizedId === 'connectors'
      ? {
          blocker: 'Connector need unresolved: source system, owner, sync posture, credential policy, and evidence proof must be registered.',
          action: 'Create connector need: define provider, source system, business owner, sync mode, credential guard, evidence route, and next activation step.',
          doneWhen: 'Connector need has provider, source system, owner, sync posture, credential policy, evidence proof, and next activation step.',
        }
      : null;

    const index = merged.findIndex((lane) => lane.id === normalizedId);

    const hydrated = {
      ...fallback,
      ...gate,
      id: normalizedId,
      label: fallback?.label || gate.label || normalizedId,
      modelName: gate.modelName || fallback?.modelName || 'LiveSourceModel',
      route: gate.route || fallback?.route || resolveWilsyR91K159GateRoute({ id: normalizedId }),
      priority: gate.priority || gate.severity || fallback?.priority || 'HIGH',
      currentRecords: Number.isFinite(gate.currentRecords) ? gate.currentRecords : fallback?.currentRecords || 0,
      targetRecords: Number.isFinite(gate.targetRecords) ? gate.targetRecords : fallback?.targetRecords || 1,
      blocker: connectorNeedProfile?.blocker || formatWilsyR91K170OperatingText(gate.blocker || gate.summary || gate.action || fallback?.blocker),
      action: connectorNeedProfile?.action || formatWilsyR91K170OperatingText(gate.action || gate.summary || fallback?.action),
      doneWhen: connectorNeedProfile?.doneWhen || formatWilsyR91K170OperatingText(gate.doneWhen || fallback?.doneWhen),
    };

    if (index >= 0) {
      merged[index] = hydrated;
    } else {
      merged.push(hydrated);
    }
  });

  return merged;
}

/**
 * @function WilsyR91K157DCreatePathTo100Surface
 * @description Renders Create as a source list-menu operating shell connected to live backend source routes, readiness proof, collapsible intelligence, and workspace commands.
 * @param {Object} props - CRM Create operating shell properties.
 * @returns {JSX.Element} Functional Wilsy OS source activation workspace.
 * @collaboration Replaces stacked cards with a production source menu OS while preserving live backend truth and no synthetic maturity.
 */
function WilsyR91K157DCreatePathTo100Surface({
  operatingSnapshot = createEmptySnapshot(),
  readinessScore = 0,
  rootHashStatus = 'Root pending',
  onReturnToOperate,
  onActivateSourceGate,
}) {
  const tenantId = operatingSnapshot?.tenantId || operatingSnapshot?.tenantConfig?.tenantId || 'MASTER';
  const [sourceGuidePayload, setSourceGuidePayload] = useState(null);
  const [sourceGuideError, setSourceGuideError] = useState('');
  const [activeSourceId, setActiveSourceId] = useState('contacts');
  const [activeRailMenu, setActiveRailMenu] = useState('live');
  const [dailyRailOpen, setDailyRailOpen] = useState(false);
  const [forensicRailOpen, setForensicRailOpen] = useState(false);
  const [liveActivationSummary, setLiveActivationSummary] = useState(null);
  const [liveActivationBusy, setLiveActivationBusy] = useState(false);
  const [liveActivationError, setLiveActivationError] = useState('');

  useEffect(() => {
    let active = true;

    fetch(`/api/crm/live/source-guide?r91k170=${Date.now()}`, {
      headers: {
        'X-Tenant-Id': tenantId,
        Accept: 'application/json',
        'Cache-Control': 'no-cache',
      },
      cache: 'no-store',
    })
      .then((response) => response.json())
      .then((payload) => {
        if (active) {
          setSourceGuidePayload(payload);
          setSourceGuideError('');
        }
      })
      .catch((error) => {
        if (active) {
          setSourceGuideError(error?.message || 'SOURCE_GUIDE_FETCH_FAILED');
        }
      });

    return () => {
      active = false;
    };
  }, [tenantId]);

  const createPath = normalizeWilsyR91K157DReadinessBreakdown(
    sourceGuidePayload || {},
    operatingSnapshot,
    readinessScore
  );

  const sourceLanes = useMemo(() => buildWilsyR91K170SourceLanes(createPath), [createPath]);

  useEffect(() => {
    if (sourceLanes.length > 0 && !sourceLanes.some((lane) => lane.id === activeSourceId)) {
      setActiveSourceId(sourceLanes[0].id);
    }
  }, [sourceLanes, activeSourceId]);

  const activeLane = sourceLanes.find((lane) => lane.id === activeSourceId) || sourceLanes[0] || buildWilsyR91K170FallbackLanes()[1];
  const activeSummary = liveActivationSummary?.id === activeLane.id ? liveActivationSummary : null;
  const liveRecordCount = activeSummary?.recordCount ?? activeLane.currentRecords ?? 0;
  const liveHttpStatus = liveActivationBusy ? 'LIVE...' : (activeSummary?.httpStatus || 'Ready');
  const liveRoute = activeSummary?.route || activeLane.route || resolveWilsyR91K159GateRoute(activeLane);
  const liveModel = activeSummary?.modelName || activeLane.modelName || 'LiveSourceModel';

  const readinessCurrent = Number(createPath.currentScore || readinessScore || sourceGuidePayload?.guide?.readinessScore || 0);
  const readinessGap = Math.max(0, Number(createPath.remainingTo100 || 100 - readinessCurrent));
  const completedGates = Number(createPath.completedGateCount || 0);
  const totalGates = Number(createPath.totalGateCount || 6);
  const emptyLaneCount = sourceLanes.filter((lane) => Number(lane.currentRecords || 0) === 0).length;
  const hardBlockers = Array.isArray(createPath.hardBlockers) ? createPath.hardBlockers : [];
  const sourceSignatureFabric = sourceGuidePayload?.sourceSignatureFabric || {};
  const postureGrade =
    sourceGuidePayload?.guide?.postureGrade ||
    sourceGuidePayload?.postureGrade ||
    createPath.postureGrade ||
    'SOURCE_EXPANSION_REQUIRED';
  const aiOperatingMode =
    sourceGuidePayload?.guide?.aiOperatingMode ||
    sourceGuidePayload?.aiOperatingMode ||
    'DATA_DENSITY_EXPANSION';

  const signalStripCards = [
    {
      id: 'current',
      label: 'Current',
      value: `${readinessCurrent}%`,
      detail: aiOperatingMode,
      route: '/api/crm/live/source-guide',
      modelName: 'readinessBreakdown',
      http: sourceGuidePayload ? 200 : 'Ready',
      action: 'Refresh readiness source guide',
    },
    {
      id: 'remaining',
      label: 'Remaining',
      value: `${readinessGap}%`,
      detail: createPath.maturityState || 'READINESS_BLOCKED',
      route: '/api/crm/live/source-guide',
      modelName: 'pathTo100',
      http: sourceGuidePayload ? 200 : 'Ready',
      action: 'Review path to 100 blockers',
    },
    {
      id: 'gates',
      label: 'Gates',
      value: `${completedGates}/${totalGates}`,
      detail: `${hardBlockers.length} blockers`,
      route: '/api/crm/live/source-guide',
      modelName: 'readinessGateLedger',
      http: sourceGuidePayload ? 200 : 'Ready',
      action: 'Open readiness gate ledger',
    },
    {
      id: 'sources',
      label: 'Sources',
      value: `${sourceLanes.length}`,
      detail: `${emptyLaneCount} empty lanes`,
      route: '/api/crm/live/source-guide',
      modelName: 'missingGates',
      http: sourceGuidePayload ? 200 : 'Ready',
      action: 'Open source lane menu',
    },
    {
      id: 'records',
      label: 'Records',
      value: `${liveRecordCount}`,
      detail: `${liveHttpStatus} · ${activeLane.label}`,
      route: liveRoute,
      modelName: liveModel,
      http: liveHttpStatus,
      action: `Prove ${activeLane.label} route`,
    },
  ];

  const pathSequence = Array.isArray(createPath.sequence) && createPath.sequence.length
    ? createPath.sequence
    : [
        { id: 'source-records', label: 'Populate live sources', summary: 'Create production records for empty CRM source lanes.' },
        { id: 'connectors', label: 'Register connectors', summary: 'Bind CRM to verified external source systems.' },
        { id: 'evidence', label: 'Seal evidence', summary: 'Attach audit receipts to meaningful source actions.' },
        { id: 'revenue', label: 'Govern revenue', summary: 'Create real deal movement and commercial accountability.' },
      ];

  const connectorLane = sourceLanes.find((lane) => lane.id === 'connectors') || activeLane;
  const evidenceLane = sourceLanes.find((lane) => lane.id === 'evidence') || activeLane;
  const dealsLane = sourceLanes.find((lane) => lane.id === 'deals') || activeLane;

  const railMenus = [
    {
      id: 'live',
      label: 'Live',
      eyebrow: 'Backend route',
      headline: `${activeLane.label} is ${liveHttpStatus}`,
      summary: `${liveRoute} · ${liveRecordCount} records · ${liveModel}`,
      purpose: 'Proves whether the active CRM source lane is connected to real backend data before work is executed.',
      benefit: 'Prevents teams from acting on stale CRM assumptions and gives managers immediate source-health visibility.',
      command: 'prove',
      commandLabel: `Prove ${activeLane.label}`,
      status: liveHttpStatus,
      route: liveRoute,
      items: [
        ['HTTP', liveHttpStatus],
        ['Records', liveRecordCount],
        ['Model', liveModel],
        ['Source lane', activeLane.label],
      ],
    },
    {
      id: 'proof',
      label: 'Proof',
      eyebrow: 'Forensic ledger',
      headline: rootHashStatus || sourceSignatureFabric.rootHash || 'Root proof pending',
      summary: activeSummary?.proofLine || activeLane.blocker,
      purpose: 'Turns the selected CRM action into an auditable source-to-proof trail.',
      benefit: 'Supports executive review, compliance checks, investor evidence packs, and dispute-ready activity history.',
      command: 'proof',
      commandLabel: 'Open proof drawer',
      status: `${hardBlockers.length} blockers`,
      route: '/api/crm/live/source-guide',
      items: [
        ['Root hash', rootHashStatus || sourceSignatureFabric.rootHash || 'Root pending'],
        ['Posture', postureGrade],
        ['Blockers', hardBlockers.length],
        ['Evidence route', evidenceLane.route],
      ],
    },
    {
      id: 'connectors',
      label: 'Connectors',
      eyebrow: 'Source systems',
      headline: connectorLane.currentRecords > 0 ? 'Connector posture detected' : 'Connector posture required',
      summary: connectorLane.action || 'Register verified source connector posture.',
      purpose: 'Shows whether the CRM is locally typed data or connected to verified source systems.',
      benefit: 'Improves trust in pipeline data, reduces manual CRM drift, and prepares the tenant for automation-grade sync.',
      command: 'connectors',
      commandLabel: 'Open connectors lane',
      status: `${connectorLane.currentRecords}/${connectorLane.targetRecords}`,
      route: connectorLane.route,
      items: [
        ['Connector records', `${connectorLane.currentRecords}/${connectorLane.targetRecords}`],
        ['Route', connectorLane.route],
        ['Model', connectorLane.modelName],
        ['Policy', 'No fake sync'],
      ],
    },
    {
      id: 'actions',
      label: 'Actions',
      eyebrow: 'Wilsy AI commands',
      headline: 'Next command queue',
      summary: `Guard AI can prove ${activeLane.label}; Autopilot can open the workspace; Audit Sentinel can review blockers.`,
      purpose: 'Converts insight into operator action without leaving the source workspace.',
      benefit: 'Reduces clicks, keeps sales teams focused, and gives leadership a consistent operating rhythm.',
      command: 'actions',
      commandLabel: 'Open action list',
      status: `${pathSequence.length} actions`,
      route: activeLane.route,
      items: [
        ['Guard AI', `Prove ${activeLane.label}`],
        ['Autopilot', `Open ${activeLane.label}`],
        ['Audit Sentinel', `${hardBlockers.length} blockers`],
        ['Revenue path', dealsLane.route],
      ],
    },
  ];

  /* R91K172_FINAL_DAILY_FORENSIC_DRAWER_CONTRACT */
  const r91k172FirstEmptyLane =
    sourceLanes.find((lane) => Number(lane.currentRecords || 0) === 0 && lane.id !== 'leads') ||
    sourceLanes.find((lane) => Number(lane.currentRecords || 0) === 0) ||
    activeLane;

  const r91k172ConnectorLane = sourceLanes.find((lane) => lane.id === 'connectors') || activeLane;
  const r91k172EvidenceLane = sourceLanes.find((lane) => lane.id === 'evidence') || activeLane;
  const r91k172DealsLane = sourceLanes.find((lane) => lane.id === 'deals') || activeLane;

  const dailyOperatingQueue = [
    {
      id: 'populate-live-sources',
      label: 'Populate empty live CRM sources',
      summary: `${emptyLaneCount} source lanes are route-live but record-empty. Start with ${r91k172FirstEmptyLane.label} so CRM maturity can move beyond blocked posture.`,
      status: `${r91k172FirstEmptyLane.currentRecords}/${r91k172FirstEmptyLane.targetRecords} records`,
      route: r91k172FirstEmptyLane.route,
      modelName: r91k172FirstEmptyLane.modelName,
      sourceId: r91k172FirstEmptyLane.id,
      lane: r91k172FirstEmptyLane,
      command: `Open ${r91k172FirstEmptyLane.label}`,
    },
    {
      id: 'register-connectors',
      label: 'Register real source connectors',
      summary: `${r91k172ConnectorLane.currentRecords}/${r91k172ConnectorLane.targetRecords} connector records are available. Register a verified source system before claiming automation-grade sync.`,
      status: `${r91k172ConnectorLane.currentRecords}/${r91k172ConnectorLane.targetRecords} connectors`,
      route: r91k172ConnectorLane.route,
      modelName: r91k172ConnectorLane.modelName,
      sourceId: r91k172ConnectorLane.id,
      lane: r91k172ConnectorLane,
      command: 'Open connectors',
    },
    {
      id: 'seal-evidence-anchors',
      label: 'Seal evidence anchors for CRM activity',
      summary: `${r91k172EvidenceLane.currentRecords}/${r91k172EvidenceLane.targetRecords} evidence records are available. Attach source, actor, route, timestamp, and proof posture to the selected lane.`,
      status: `${r91k172EvidenceLane.currentRecords}/${r91k172EvidenceLane.targetRecords} anchors`,
      route: r91k172EvidenceLane.route,
      modelName: r91k172EvidenceLane.modelName,
      sourceId: r91k172EvidenceLane.id,
      lane: r91k172EvidenceLane,
      command: 'Open evidence',
    },
    {
      id: 'create-governed-revenue',
      label: 'Create governed deal and revenue movement',
      summary: `${r91k172DealsLane.currentRecords}/${r91k172DealsLane.targetRecords} deal records are available. Create real account-linked deal motion before the revenue path can mature.`,
      status: `${r91k172DealsLane.currentRecords}/${r91k172DealsLane.targetRecords} deals`,
      route: r91k172DealsLane.route,
      modelName: r91k172DealsLane.modelName,
      sourceId: r91k172DealsLane.id,
      lane: r91k172DealsLane,
      command: 'Open deals',
    },
  ];

  const forensicBlockerQueue = (hardBlockers.length
    ? hardBlockers
    : [
        {
          severity: 'HIGH',
          summary: `${emptyLaneCount} live source lanes are route-live but record-empty.`,
          action: `Prove and populate ${r91k172FirstEmptyLane.label}.`,
          route: r91k172FirstEmptyLane.route,
        },
        {
          severity: 'CRITICAL',
          summary: 'Connector posture is required before full readiness can be promoted.',
          action: 'Register a real source connector and keep the no-fake-sync guard intact.',
          route: r91k172ConnectorLane.route,
        },
        {
          severity: 'HIGH',
          summary: 'Evidence posture must stay attached to source actions.',
          action: 'Seal audit evidence so executive, investor, and compliance review has proof.',
          route: r91k172EvidenceLane.route,
        },
      ]
  ).slice(0, 6).map((blocker, index) => {
    const blockerText = formatWilsyR91K170OperatingText(blocker);
    const sourceLane = sourceLanes[index] || activeLane;
    const blockerRoute =
      (blocker && typeof blocker === 'object' && blocker.route) ||
      sourceLane.route ||
      liveRoute;
    const blockerSeverity =
      (blocker && typeof blocker === 'object' && (blocker.severity || blocker.priority || blocker.code || blocker.status)) ||
      sourceLane.priority ||
      'BACKEND';
    const blockerAction =
      (blocker && typeof blocker === 'object' && (blocker.action || blocker.nextAction || blocker.recommendation)) ||
      `Resolve through ${sourceLane.label} source lane.`;

    return {
      id: `blocker-${index + 1}`,
      title: blockerText,
      action: formatWilsyR91K170OperatingText(blockerAction),
      route: blockerRoute,
      severity: formatWilsyR91K170OperatingText(blockerSeverity),
      sourceId: sourceLane.id,
      sourceLabel: sourceLane.label,
    };
  });


  /**
   * @function handleWilsyR91K170ProveLane
   * @description Selects a source lane and calls its live backend CRM source route.
   * @param {Object} lane - Source lane selected by the operator.
   * @returns {Promise<void>} Resolves after live backend proof updates.
   * @collaboration Connects every list-menu source action to live backend route proof.
   */
  const handleWilsyR91K170ProveLane = useCallback(async (lane = {}) => {
    const selectedLane = lane.id ? lane : activeLane;

    setActiveSourceId(selectedLane.id || 'contacts');
    setLiveActivationBusy(true);
    setLiveActivationError('');

    try {
      const summary = await fetchWilsyR91K159LiveSourceGate(selectedLane, tenantId);
      setLiveActivationSummary(summary);
    } catch (error) {
      setLiveActivationSummary(null);
      setLiveActivationError(error?.message || 'LIVE_SOURCE_GATE_FETCH_FAILED');
    } finally {
      setLiveActivationBusy(false);
    }
  }, [activeLane, tenantId]);

  /**
   * @function handleWilsyR91K170OpenWorkspace
   * @description Opens the workspace bridge for the selected CRM source lane.
   * @param {Object} lane - Source lane selected by the operator.
   * @returns {void}
   * @collaboration Turns backend proof into a workspace command instead of a static dashboard panel.
   */
  const handleWilsyR91K170OpenWorkspace = useCallback((lane = {}) => {
    const selectedLane = lane.id ? lane : activeLane;

    setActiveSourceId(selectedLane.id || 'contacts');

    onActivateSourceGate?.({
      id: selectedLane.id || 'contacts',
      label: `Open ${selectedLane.label || 'Source'} Workspace`,
      modelName: selectedLane.modelName,
      route: selectedLane.route,
    });
  }, [activeLane, onActivateSourceGate]);

  return (
    <section
      className={styles.r91k170Shell}
      data-wilsy-r91k170-source-operating-shell="live-list-menu"
      data-active-source={activeLane.id}
      data-active-route={liveRoute}
      data-active-http={String(liveHttpStatus)}
      aria-label="Wilsy CRM Source Operating Shell"
    >
      <header className={styles.r91k170Header}>
        <div>
          <small>Wilsy CRM · Wilsy AI · Backend constrained</small>
          <strong>LIVE Path-to-100 Source Creation</strong>
          <p>
            One source lane at a time: prove the backend route, complete the done-when contract,
            then open the workspace that clears the blocker.
          </p>
        </div>

        <nav aria-label="Primary source commands">
          <button type="button" onClick={() => handleWilsyR91K170ProveLane(activeLane)}>
            Prove {activeLane.label}
          </button>
          <button type="button" onClick={() => handleWilsyR91K170OpenWorkspace(activeLane)}>
            Open Workspace
          </button>
          <button type="button" onClick={onReturnToOperate}>
            Return to Operate
          </button>
        </nav>
      </header>

      <section
        className={styles.r91k170SignalMenu}
        data-wilsy-r91k170-signal-menu="backend-connected"
        aria-label="Backend-connected readiness signals"
      >
        {signalStripCards.map((card) => (
          <button
            key={card.id}
            type="button"
            data-signal-card={card.id}
            data-backend-route={card.route}
            data-backend-http={String(card.http)}
            data-backend-model={card.modelName}
            title={`${card.label}: ${card.value} · ${card.detail} · ${card.route}`}
            onClick={() => handleWilsyR91K170ProveLane(activeLane)}
          >
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <p>{card.detail}</p>
          </button>
        ))}
      </section>

      <section className={styles.r91k170Workspace}>
        <aside className={styles.r91k170SourceMenu} aria-label="Live source lane menu">
          <header>
            <small>Source menu</small>
            <strong>{sourceLanes.length} live lanes</strong>
          </header>

          <div>
            {sourceLanes.map((lane) => {
              const active = lane.id === activeLane.id;

              return (
                <button
                  key={lane.id}
                  type="button"
                  data-source-lane={lane.id}
                  data-active-source={active ? 'true' : 'false'}
                  onClick={() => handleWilsyR91K170ProveLane(lane)}
                >
                  <span>{lane.priority}</span>
                  <strong>{lane.label}</strong>
                  <p>{lane.action}</p>
                  <b>{lane.currentRecords}/{lane.targetRecords}</b>
                </button>
              );
            })}
          </div>
        </aside>

        <main className={styles.r91k170CommandSurface} aria-label="Selected source command surface">
          <header>
            <small>Active source command</small>
            <strong>{activeLane.label}</strong>
            <p>{activeLane.action}</p>
          </header>

          <section className={styles.r91k170ProofGrid}>
            <article>
              <span>Route</span>
              <strong>{liveRoute}</strong>
            </article>
            <article>
              <span>HTTP</span>
              <strong>{liveHttpStatus}</strong>
            </article>
            <article>
              <span>Records</span>
              <strong>{liveRecordCount}</strong>
            </article>
            <article>
              <span>Model</span>
              <strong>{liveModel}</strong>
            </article>
          </section>

          <section className={styles.r91k170DoneWhen}>
            <small>Done when</small>
            <strong>{activeLane.doneWhen}</strong>
            <p>{liveActivationError || activeSummary?.proofLine || activeLane.blocker}</p>
          </section>

          {/* R91K178B3_ACTIVE_SOURCE_COMMAND_INLINE_PANEL_ONLY */}

          <section

            className={styles.r91k178bActiveCommandIntelligence}

            data-wilsy-r91k178b-active-command="source-playbook"

            data-active-source={activeLane.id}

            data-command-state={

              liveRecordCount > 0

                ? 'SOURCE_EVIDENCE_PRESENT'

                : activeLane.id === 'connectors'

                  ? 'CONNECTOR_NEED_OPEN'

                  : 'SOURCE_DENSITY_REQUIRED'

            }

            aria-label="Active Source Command operating playbook"

          >

            <article className={styles.r91k178bCommandNarrative}>

              <small>Operator playbook</small>

              <strong>

                {readinessCurrent}% readiness · {activeLane.label} · {liveRecordCount > 0 ? 'records present' : 'records required'}

              </strong>

              <p>{activeLane.blocker}</p>

            </article>

          

            <div className={styles.r91k178bRouteProofGrid} aria-label="Active source route proof">

              <article>

                <span>Backend route</span>

                <strong>{liveRoute}</strong>

              </article>

              <article>

                <span>HTTP</span>

                <strong>{liveHttpStatus}</strong>

              </article>

              <article>

                <span>Records</span>

                <strong>{liveRecordCount}</strong>

              </article>

              <article>

                <span>Model</span>

                <strong>{liveModel}</strong>

              </article>

            </div>

          

            <div className={styles.r91k178bPlaybookGrid} aria-label="Active source command sequence">

              <article>

                <span>01</span>

                <strong>Prove live route</strong>

                <p>Refresh {liveRoute} and keep the command bound to backend evidence.</p>

              </article>

              <article>

                <span>02</span>

                <strong>{liveRecordCount > 0 ? 'Use live evidence' : 'Create source density'}</strong>

                <p>{activeLane.action}</p>

              </article>

              <article>

                <span>03</span>

                <strong>Govern AI limits</strong>

                <p>

                  {liveRecordCount > 0

                    ? 'Wilsy AI may explain this lane using live records and route proof.'

                    : 'Wilsy AI must not invent records, connector status, or synthetic readiness.'}

                </p>

              </article>

            </div>

          

            <article className={styles.r91k178bAiBoundary}>

              <small>Wilsy AI boundary</small>

              <strong>

                {liveRecordCount > 0

                  ? 'SOURCE_EVIDENCE_PRESENT'

                  : activeLane.id === 'connectors'

                    ? 'CONNECTOR_NEED_OPEN'

                    : 'SOURCE_DENSITY_REQUIRED'}

              </strong>

              <p>

                {activeLane.id === 'connectors'

                  ? 'Connector count remains source-honest until a real connector record exists.'

                  : 'Readiness can only move through live records, verified route proof, evidence, and governed operator action.'}

              </p>

            </article>

          </section>


          <section className={styles.r91k170CommandTray} aria-label="Selected source command tray">
            <button type="button" onClick={() => handleWilsyR91K170OpenWorkspace(activeLane)}>
              Execute workspace command
              <ChevronRight size={15} />
            </button>
            <button type="button" onClick={() => handleWilsyR91K170ProveLane(activeLane)}>
              Refresh backend proof
            </button>
            <button type="button" onClick={() => setForensicRailOpen((current) => !current)}>
              {forensicRailOpen ? 'Hide proof drawer' : 'Open proof drawer'}
            </button>
          </section>
        </main>

        <aside
          className={`${styles.r91k170RailMenu} ${styles.r91k171EnhancedRail}`}
          data-wilsy-r91k171-enhanced-ai-rail="contextual-copilot"
          data-active-source={activeLane.id}
          data-active-route={liveRoute}
          aria-label="Enhanced Wilsy AI rail"
        >
          <header className={styles.r91k171RailHeader}>
            <small>Wilsy AI rail</small>
            <strong>{rootHashStatus || sourceSignatureFabric.rootHash || 'Live source proof'}</strong>
            <p>{activeLane.label} · {liveHttpStatus} · {liveRecordCount} records</p>
          </header>

          <div className={styles.r91k171RailStack}>
            {railMenus.map((menu) => {
              const open = activeRailMenu === menu.id;

              return (
                <section
                  key={menu.id}
                  className={styles.r91k171RailPanel}
                  data-rail-open={open ? 'true' : 'false'}
                  data-rail-purpose={menu.purpose}
                  data-rail-benefit={menu.benefit}
                  data-rail-route={menu.route}
                  data-rail-status={String(menu.status)}
                >
                  <button
                    type="button"
                    aria-expanded={open}
                    aria-controls={`wilsy-r91k171-rail-${menu.id}`}
                    onClick={() => setActiveRailMenu(open ? '' : menu.id)}
                  >
                    <span>
                      <small>{menu.eyebrow}</small>
                      <strong>{menu.label}</strong>
                    </span>
                    <em>{menu.status}</em>
                    <b>{open ? 'Collapse' : 'Open'}</b>
                  </button>

                  <div id={`wilsy-r91k171-rail-${menu.id}`}>
                    <article className={styles.r91k171RailNarrative}>
                      <small>{menu.headline}</small>
                      <p>{formatWilsyR91K170OperatingText(menu.summary)}</p>
                    </article>

                    <div className={styles.r91k171RailProofGrid}>
                      {menu.items.map(([label, value]) => (
                        <article key={label}>
                          <span>{label}</span>
                          <strong>{formatWilsyR91K170OperatingText(value)}</strong>
                        </article>
                      ))}
                    </div>

                    <article className={styles.r91k171RailValue}>
                      <span>Business value</span>
                      <p>{menu.benefit}</p>
                    </article>

                    <nav className={styles.r91k171RailCommands} aria-label={`${menu.label} rail commands`}>
                      <button
                        type="button"
                        onClick={() => {
                          if (menu.command === 'prove' || menu.command === 'actions') {
                            handleWilsyR91K170ProveLane(activeLane);
                          }

                          if (menu.command === 'proof') {
                            setForensicRailOpen(true);
                          }

                          if (menu.command === 'connectors') {
                            handleWilsyR91K170ProveLane(connectorLane);
                          }
                        }}
                      >
                        {menu.commandLabel}
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          if (menu.command === 'connectors') {
                            handleWilsyR91K170OpenWorkspace(connectorLane);
                            return;
                          }

                          if (menu.command === 'proof') {
                            setForensicRailOpen(true);
                            return;
                          }

                          handleWilsyR91K170OpenWorkspace(activeLane);
                        }}
                      >
                        Open workspace
                      </button>
                    </nav>
                  </div>
                </section>
              );
            })}
          </div>
        </aside>
      </section>

      <section
        className={styles.r91k170Drawer}
        data-drawer-open={dailyRailOpen ? 'true' : 'false'}
        aria-label="Daily operating drawer"
      >
        <button
          type="button"
          aria-expanded={dailyRailOpen}
          onClick={() => setDailyRailOpen((current) => !current)}
        >
          <span>Daily operating actions</span>
          <strong>What the operator completes today</strong>
          <b>{dailyRailOpen ? 'Collapse' : 'Open list'}</b>
        </button>

        <div data-wilsy-r91k172-daily-queue="live-operating-actions">
          {dailyOperatingQueue.map((action, index) => (
            <article
              key={action.id}
              data-wilsy-r91k172-daily-action={action.id}
              data-daily-source-lane={action.sourceId}
              data-backend-route={action.route}
              data-backend-model={action.modelName}
              data-action-status={action.status}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{action.label}</strong>
              <p>{action.summary}</p>
              <footer>
                <small>{action.status}</small>
                <button type="button" onClick={() => handleWilsyR91K170ProveLane(action.lane)}>
                  Prove
                </button>
                <button type="button" onClick={() => handleWilsyR91K170OpenWorkspace(action.lane)}>
                  Open
                </button>
              </footer>
            </article>
          ))}
        </div>
      </section>

      <section
        className={styles.r91k170Drawer}
        data-drawer-open={forensicRailOpen ? 'true' : 'false'}
        aria-label="Forensic backend proof drawer"
      >
        <button
          type="button"
          aria-expanded={forensicRailOpen}
          onClick={() => setForensicRailOpen((current) => !current)}
        >
          <span>Forensic blockers</span>
          <strong>{sourceGuideError || `${hardBlockers.length} backend blockers tracked`}</strong>
          <b>{forensicRailOpen ? 'Collapse' : 'Open proof'}</b>
        </button>

        <div data-wilsy-r91k172-forensic-queue="backend-blockers">
          {forensicBlockerQueue.map((blocker, index) => (
            <article
              key={blocker.id}
              data-wilsy-r91k172-forensic-blocker={blocker.id}
              data-forensic-source-lane={blocker.sourceId}
              data-backend-route={blocker.route}
              data-severity={blocker.severity}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{blocker.title}</strong>
              <p>{blocker.action}</p>
              <footer>
                <small>{blocker.severity}</small>
                <code>{blocker.route}</code>
              </footer>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}


/**
 * @function WilsyR91K131FullViewpointSurface
 * @description Owns Pipeline/Create/Proof as a real Wilsy CRM operating screen.
 * @collaboration Replaces legacy stretched dashboard panels with state-driven OS workflow.
 */
function WilsyR91K131FullViewpointSurface({
  mode,
  operatingSnapshot,
  sourceGuide,
  readinessScore,
  rootHashStatus,
  onReturnToOperate,
  activeHomeTab,
  onActivateSourceGate,
}) {

  if (activeHomeTab === 'create') {
    return (
      <WilsyR91K157DCreatePathTo100Surface
        operatingSnapshot={operatingSnapshot}
        readinessScore={readinessScore}
        rootHashStatus={rootHashStatus}
        onReturnToOperate={onReturnToOperate}
        onActivateSourceGate={onActivateSourceGate}
      />
    );
  } /* R91K157D_CREATE_EARLY_RETURN_ACTIVE_TAB */

  let   model = buildWilsyR91K131FullViewpointModel({
    operatingSnapshot,
    sourceGuide,
    readinessScore,
    rootHashStatus,
  });
  model = applyWilsyR91K150RuntimeFabricContract(model); /* R91K150_MODEL_RUNTIME_CONTRACT_BRIDGE */
  const [activeStageId, setActiveStageId] = useState(model.stages[0]?.id || 'intake');
  const [activeRailTab, setActiveRailTab] = useState(model.intelligenceTabs[0]?.id || 'email');
  const [expandedReceipt, setExpandedReceipt] = useState('');
  const activeStage = model.stages.find((stage) => stage.id === activeStageId) || model.stages[0];

  return (
    <main
      className={styles.r91k131Viewpoint}
      data-wilsy-r91k131-viewpoint={mode}
      aria-label="Wilsy CRM full viewpoint operating contract"
    >
      <section className={styles.r91k131CommandBar}>
        <span>
          <small>WILSY CRM FULL VIEWPOINT</small>
          <strong>
            {mode === 'pipeline'
              ? 'Sovereign Pipeline Command'
              : mode === 'create'
                ? 'Guided Source Creation'
                : 'Terminal Proof Room'}
          </strong>
        </span>

        <nav aria-label="Live operating telemetry">
          <em>{model.readiness}% readiness</em>
          <em>{model.connectedSources}/{model.totalSources || 0} sources</em>
          <em>Root {model.rootHash}</em>
        </nav>

        <button type="button" onClick={onReturnToOperate}>
          Return to Operate
        </button>
      </section>

      <section className={styles.r91k131StageBoard} aria-label="Live pipeline stages">
        <div className={styles.r91k131StageGrid}>
          {model.stages.map((stage) => (
            <WilsyR91K131StageButton
              key={stage.id}
              stage={stage}
              active={stage.id === activeStageId}
              onActivate={setActiveStageId}
            />
          ))}
        </div>

        <aside className={styles.r91k131StageFocus} aria-label="Focused stage intelligence">
          <small>Active stage</small>
          <strong>{activeStage.label}</strong>
          <p>{activeStage.description}</p>
          <dl>
            <div>
              <dt>Value</dt>
              <dd>{activeStage.valueLabel}</dd>
            </div>
            <div>
              <dt>Probability</dt>
              <dd>{activeStage.probability}%</dd>
            </div>
            <div>
              <dt>Receipt</dt>
              <dd>{activeStage.proof}</dd>
            </div>
          </dl>
        </aside>
      </section>

      <WilsyR91K139SourceSignatureFabric model={model} />

      <WilsyR91K131IntelRail
        tabs={model.intelligenceTabs}
        activeTab={activeRailTab}
        onTabChange={setActiveRailTab}
      />

      <WilsyR91K131ProofLedger
        receipts={model.receipts}
        expandedReceipt={expandedReceipt}
        onExpand={setExpandedReceipt}
      />

      <section className={styles.r91k131ActionRail} aria-label="Compliance and revenue action rail">
        {model.rail.map((item) => (
          <article key={item.id} data-score={item.value}>
            <small>{item.label}</small>
            <strong>{item.value}</strong>
            <p>{item.detail}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

/**
 * @function CRMDashboard
 * @description Renders the Wilsy CRM operating workspace and delegates Pipeline/Create/Proof to the R91K131 full viewpoint contract.
 * @collaboration Coordinates live CRM snapshot, Source Guide posture, account command controls, and sovereign operating surfaces.
 */

/**
 * @function CRMDashboard
 * @description Renders the Wilsy OS CRM command workspace with live source records, Records rail counts, lead operating room, drill-down panels, tenant runtime and account command controls.
 * @param {Object} props - CRM dashboard props.
 * @returns {JSX.Element} CRM dashboard workspace.
 * @collaboration CRM live routes, source posture, Records rail, lead operating room, meetings workspace, Wilsy Account Command Center, tenant context and production evidence surfaces.
 */
function CRMDashboard({ user = {}, tenantConfig = {}, onExit = null }) {
  const searchPermissionProfile = useMemo(
    () => resolveCrmPermissionProfile(user, tenantConfig, buildOperatorIdentity(user)),
    [user, tenantConfig]
  );

  useEffect(() => {
    return installCrmSearchOutcomeRuntime({
      tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
      allowedSourceLabels: searchPermissionProfile.sourceLabels,
      includePrivilegedSources: searchPermissionProfile.includePrivilegedSearch,
      accessScope: searchPermissionProfile.scope,
    });
  }, [
    tenantConfig?.tenantId,
    tenantConfig?.id,
    tenantConfig?.tenantKey,
    user?.tenantId,
    user?.tenant?.id,
    searchPermissionProfile.sourceLabels,
    searchPermissionProfile.includePrivilegedSearch,
    searchPermissionProfile.scope,
  ]);
  /* WILSY R73B: Sovereign search runtime state. */
  const [sovereignSearchQuery, setSovereignSearchQuery] = useState('');
  const [sovereignSearchOpen, setSovereignSearchOpen] = useState(false);
  const [sovereignSearchState, setSovereignSearchState] = useState({
    status: 'idle',
    results: [],
    error: '',
  });

  useEffect(() => {
    /**
     * @function handleSovereignSearchKeyboard
     * @description Opens and closes the CRM sovereign search overlay from keyboard commands.
     * @collaboration R73B command keyboard runtime, CRM operator search, existing dashboard shell.
     */
    const handleSovereignSearchKeyboard = (event) => {
      if (shouldOpenSovereignSearchFromKeyboard(event)) {
        event.preventDefault();
        setSovereignSearchOpen(true);
        return;
      }

      if (event.key === 'Escape') {
        setSovereignSearchOpen(false);
      }
    };

    window.addEventListener('keydown', handleSovereignSearchKeyboard);
    return () => window.removeEventListener('keydown', handleSovereignSearchKeyboard);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const normalizedQuery = sovereignSearchQuery.trim();

    if (!normalizedQuery) {
      setSovereignSearchState({
        status: 'idle',
        results: [],
        error: '',
      });
      return undefined;
    }

    setSovereignSearchState((currentState) => ({
      ...currentState,
      status: 'loading',
      error: '',
    }));

    const searchTimer = window.setTimeout(() => {
      runSovereignSearchRuntime(normalizedQuery)
        .then((results) => {
          if (cancelled) {
            return;
          }

          setSovereignSearchState({
            status: 'ready',
            results,
            error: '',
          });
        })
        .catch((error) => {
          if (cancelled) {
            return;
          }

          setSovereignSearchState({
            status: 'error',
            results: [],
            error: error?.message || 'Sovereign search runtime failed.',
          });
        });
    }, 220);

    return () => {
      cancelled = true;
      window.clearTimeout(searchTimer);
    };
  }, [sovereignSearchQuery]);


  const tenantRuntime = useTenants() || {};
  const [activeWorkspace, setActiveWorkspace] = useState('home');
  const [activeHomeTab, setActiveHomeTab] = useState('operate');
  const [createWorkspaceModule, setCreateWorkspaceModule] = useState('leads');
  const [searchTerm, setSearchTerm] = useState('');
  const [crmRailEngineStateR65A, setCrmRailEngineStateR65A] = useState('EXPANDED');

  const [refreshSignal, setRefreshSignal] = useState(0);
  const [accountSettingsOpen, setAccountSettingsOpen] = useState(false);
  const [crmSetupOpen, setCrmSetupOpen] = useState(false);
  const [crmSetupDenied, setCrmSetupDenied] = useState(null);

  /**
   * @function normalizeCrmSetupPermissionSignal
   * @description Normalizes user role and authority text for CRM Setup access checks.
   * @param {unknown} value - Permission value from local browser authority context.
   * @returns {string} Normalized permission signal.
   * @collaboration CRMDashboard, CRM top rail setup trigger, operator authority, tenant authority, and setup access denial panel.
   */
  function normalizeCrmSetupPermissionSignal(value = '') {
    return String(value || '')
      .toUpperCase()
      .replace(/[^A-Z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  }

  /**
   * @function collectCrmSetupPermissionSignals
   * @description Collects local authority signals used to decide whether the operator may open CRM Setup.
   * @returns {Array<string>} Normalized authority signals.
   * @collaboration Local storage authority state, session storage authority state, visible root operator context, and CRM setup permission gate.
   */
  function collectCrmSetupPermissionSignals() {
    if (typeof window === 'undefined') {
      return [];
    }

    const signals = [];
    const storageTargets = [window.localStorage, window.sessionStorage].filter(Boolean);

    storageTargets.forEach((storageTarget) => {
      try {
        for (let index = 0; index < storageTarget.length; index += 1) {
          const key = storageTarget.key(index);
          const value = key ? storageTarget.getItem(key) : '';

          if (!key && !value) {
            continue;
          }

          signals.push(normalizeCrmSetupPermissionSignal(key));
          signals.push(normalizeCrmSetupPermissionSignal(String(value || '').slice(0, 1800)));
        }
      } catch (error) {
        signals.push('STORAGE_PERMISSION_SCAN_UNAVAILABLE');
      }
    });

    try {
      const globalSignals = [
        window.__WILSY_OPERATOR__,
        window.__WILSY_AUTH_USER__,
        window.__WILSY_USER__,
        window.__WILSY_TENANT__,
        window.__SOVEREIGN_USER__,
      ];

      globalSignals.forEach((signal) => {
        if (signal) {
          signals.push(normalizeCrmSetupPermissionSignal(JSON.stringify(signal).slice(0, 1800)));
        }
      });
    } catch (error) {
      signals.push('GLOBAL_PERMISSION_SCAN_UNAVAILABLE');
    }

    try {
      const visibleShell = String(document?.body?.innerText || '').slice(0, 6000);
      signals.push(normalizeCrmSetupPermissionSignal(visibleShell));
    } catch (error) {
      signals.push('VISIBLE_PERMISSION_SCAN_UNAVAILABLE');
    }

    return signals.filter(Boolean);
  }

  /**
   * @function hasCrmSetupPermissionToken
   * @description Checks whether collected permission signals contain a specific role token.
   * @param {Array<string>} signals - Normalized permission signals.
   * @param {string} token - Normalized role token.
   * @returns {boolean} Whether the token is present.
   * @collaboration CRM setup permission gate, allowed authority matrix, and denied access message.
   */
  function hasCrmSetupPermissionToken(signals = [], token = '') {
    const normalizedToken = normalizeCrmSetupPermissionSignal(token);
    const rolePattern = new RegExp(`(^|_)${normalizedToken}(_|$)`);

    return signals.some((signal) => rolePattern.test(signal));
  }

  /**
   * @function resolveCrmSetupAccessLevel
   * @description Resolves whether the current operator can open the CRM Setup Intelligence Workbench.
   * @returns {Object} Access decision with matched role and required roles.
   * @collaboration CRMDashboard setup owner, top rail setup trigger, access denial overlay, and future backend authority receipts.
   */
  function resolveCrmSetupAccessLevel() {
    const signals = collectCrmSetupPermissionSignals();
    const allowedRoles = [
      'SUPER_ADMIN',
      'WILSY_OS_ROOT',
      'WILSY_ROOT',
      'ROOT',
      'TENANT_OWNER',
      'TENANT_ADMIN',
      'CRM_ADMIN',
      'SECURITY_ADMIN',
      'COMPLIANCE_ADMIN',
      'EXECUTIVE_ADMIN',
    ];

    const deniedRoles = [
      'STANDARD_USER',
      'CRM_USER',
      'SALES_AGENT',
      'VIEWER',
      'READ_ONLY',
      'GUEST',
    ];

    const matchedAllowedRole = allowedRoles.find((role) => hasCrmSetupPermissionToken(signals, role));
    const matchedDeniedRole = deniedRoles.find((role) => hasCrmSetupPermissionToken(signals, role));

    return {
      allowed: Boolean(matchedAllowedRole),
      matchedRole: matchedAllowedRole || matchedDeniedRole || 'NO_SETUP_AUTHORITY_FOUND',
      requiredRoles: allowedRoles,
      generatedAt: new Date().toISOString(),
    };
  }

  /**
   * @function buildCrmSetupDeniedState
   * @description Builds the in-app denial message shown when a user clicks Setup without setup authority.
   * @param {Object} accessDecision - Setup access decision.
   * @param {Object} eventDetail - Setup open event detail.
   * @returns {Object} Denied access state.
   * @collaboration CRM setup permission gate, top rail trigger, denied access overlay, and operator education.
   */
  function buildCrmSetupDeniedState(accessDecision = {}, eventDetail = {}) {
    return {
      title: 'Setup access restricted',
      message: 'Your current role does not have CRM Setup authority. Ask a tenant administrator or security administrator to grant setup access.',
      matchedRole: accessDecision.matchedRole || 'NO_SETUP_AUTHORITY_FOUND',
      requiredRoles: accessDecision.requiredRoles || [],
      source: eventDetail.source || 'CRM_TOP_RAIL_SETUP',
      generatedAt: accessDecision.generatedAt || new Date().toISOString(),
    };
  }

  /* WILSY_SETUP_PERMISSION_GATE */

  /**
   * @function openCrmSetupControlPlane
   * @description Opens the CRM-owned Setup control plane from top command surfaces without using Lead or Meeting local state.
   * @returns {void}
   * @collaboration CRMDashboard ownership, top rail setup trigger, WilsyCrmSetupControlPlane, shared records shell isolation.
   */
  function openCrmSetupControlPlane(eventDetail = {}) {
    const accessDecision = resolveCrmSetupAccessLevel();

    if (!accessDecision.allowed) {
      setCrmSetupOpen(false);
      setCrmSetupDenied(buildCrmSetupDeniedState(accessDecision, eventDetail));
      return;
    }

    setCrmSetupDenied(null);
    setCrmSetupOpen(true);
  }

  /**
   * @function closeCrmSetupControlPlane
   * @description Closes the CRM-owned Setup control plane and returns the operator to the current CRM workspace.
   * @returns {void}
   * @collaboration CRMDashboard ownership, setup overlay, current module preservation, and records-only workspace discipline.
   */
  function closeCrmSetupControlPlane() {
    setCrmSetupOpen(false);
    setCrmSetupDenied(null);
  }

  /* WILSY_P60H1_CRM_SETUP_OWNER */
  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    /**
     * @function handleWilsyP60H1CrmSetupOpenEvent
     * @description Receives top rail setup open events from shared records chrome and opens the CRM-owned setup surface.
     * @returns {void}
     * @collaboration Shared records top rail, CRMDashboard setup ownership, and WilsyCrmSetupControlPlane overlay.
     */
    function handleWilsyP60H1CrmSetupOpenEvent(event) {
      openCrmSetupControlPlane(event?.detail || {});
    }

    window.addEventListener('wilsy:crm-setup-open', handleWilsyP60H1CrmSetupOpenEvent);

    return () => {
      window.removeEventListener('wilsy:crm-setup-open', handleWilsyP60H1CrmSetupOpenEvent);
    };
  }, []);

  const [themeRuntime, setThemeRuntime] = useState(() => buildCrmFallbackThemeRuntime());

  const tenantIdentity = useMemo(
    () => buildTenantIdentity(tenantRuntime, tenantConfig),
    [tenantRuntime, tenantConfig]
  );

  const operatorIdentity = useBackendOperatorIdentity(user, tenantIdentity.tenantId, refreshSignal);

  const crmThemeVars = useMemo(
    () => buildCrmThemeStyleVars(themeRuntime, tenantIdentity),
    [themeRuntime, tenantIdentity]
  );

  useEffect(() => {
    let mounted = true;

    /**
     * @function applyCrmGlobalThemeRuntime
     * @description Applies theme packets from the Wilsy OS global runtime to CRM.
     * @param {Object} packet - Runtime packet.
     * @returns {void}
     * @collaboration Keeps CRM repainting when Account Command Center theme or mode changes.
     */
    const applyCrmGlobalThemeRuntime = packet => {
      if (!mounted) return;
      setThemeRuntime(previous => normalizeCrmThemeRuntimePacket(packet || resolveCrmGlobalThemeRuntime({}, previous), previous));
    };

    /**
     * @function applyStoredCrmGlobalThemeRuntime
     * @description Re-reads the stored global theme runtime and applies it to CRM.
     * @returns {void}
     * @collaboration Covers storage events, custom runtime events and direct Account Command Center commits.
     */
    const applyStoredCrmGlobalThemeRuntime = () => {
      if (!mounted) return;
      setThemeRuntime(previous => resolveCrmGlobalThemeRuntime({}, previous));
    };

    applyStoredCrmGlobalThemeRuntime();

    const unsubscribeThemeRuntime = subscribeWilsyThemeRuntime(applyCrmGlobalThemeRuntime);

    /**
     * @function runtimeEventHandler
     * @description Applies Wilsy OS theme runtime event packets to the CRM theme runtime.
     * @param {CustomEvent} event - Theme runtime event.
     * @returns {void}
     * @collaboration Keeps CRM synchronized with global Account Command Center theme changes.
     */
    const runtimeEventHandler = event => {
      applyCrmGlobalThemeRuntime(event?.detail || null);
    };

    /**
     * @function storageEventHandler
     * @description Rehydrates CRM theme runtime when persisted Wilsy OS theme storage changes.
     * @param {StorageEvent} event - Browser storage event.
     * @returns {void}
     * @collaboration Keeps CRM theme state aligned across tabs and dashboard shells.
     */
    const storageEventHandler = event => {
      const key = String(event?.key || '').toLowerCase();
      if (key.includes('wilsy') || key.includes('theme') || key.includes('skin') || key.includes('mode')) {
        applyStoredCrmGlobalThemeRuntime();
      }
    };

    window.addEventListener('wilsy:theme-change', runtimeEventHandler);
    window.addEventListener('wilsy:theme-runtime', runtimeEventHandler);
    window.addEventListener('wilsy:account-theme-runtime', runtimeEventHandler);
    window.addEventListener('wilsy:operating-skin-change', runtimeEventHandler);
    window.addEventListener('storage', storageEventHandler);

    return () => {
      mounted = false;
      if (typeof unsubscribeThemeRuntime === 'function') unsubscribeThemeRuntime();
      window.removeEventListener('wilsy:theme-change', runtimeEventHandler);
      window.removeEventListener('wilsy:theme-runtime', runtimeEventHandler);
      window.removeEventListener('wilsy:account-theme-runtime', runtimeEventHandler);
      window.removeEventListener('wilsy:operating-skin-change', runtimeEventHandler);
      window.removeEventListener('storage', storageEventHandler);
    };
  }, []);


  const { snapshot, loading } = useCrmSnapshot(tenantIdentity.tenantId, refreshSignal);
  const crmPermissionProfile = useMemo(
    () => resolveCrmPermissionProfile(user, tenantConfig, operatorIdentity),
    [operatorIdentity, tenantConfig, user]
  );
  const visibleCrmWorkspaces = useMemo(
    () => CRM_WORKSPACES.filter(workspace => crmPermissionProfile.allowedWorkspaceIds.includes(workspace.id)),
    [crmPermissionProfile.allowedWorkspaceIds]
  );
  const visibleHomeTabs = useMemo(
    () => CRM_HOME_TABS.filter(tab => crmPermissionProfile.allowedHomeTabIds.includes(tab.id)),
    [crmPermissionProfile.allowedHomeTabIds]
  );
  const operatingSnapshot = useMemo(
    () => scopeCrmSnapshotForOperator(snapshot, crmPermissionProfile),
    [crmPermissionProfile, snapshot]
  );
  const dailyWorkspaceCards = useMemo(
    () => buildCrmDailyWorkspaceCards(operatingSnapshot),
    [operatingSnapshot]
  );

  useEffect(() => {
    if (!visibleCrmWorkspaces.some(workspace => workspace.id === activeWorkspace)) {
      setActiveWorkspace('home');
    }
  }, [activeWorkspace, visibleCrmWorkspaces]);

  useEffect(() => {
    if (!visibleHomeTabs.some(tab => tab.id === activeHomeTab)) {
      setActiveHomeTab(visibleHomeTabs[0]?.id || 'operate');
    }
  }, [activeHomeTab, visibleHomeTabs]);

  const readinessScore = resolveWilsyR91K114ReadinessScore(operatingSnapshot);
  const readinessNarrative = resolveWilsyR91K114ReadinessNarrative(operatingSnapshot, readinessScore);
  const pipelineStages = useMemo(() => buildPipelineStages(operatingSnapshot.deals), [operatingSnapshot.deals]);
  const weightedPipeline = useMemo(() => buildPipelineTotal(pipelineStages.filter(stage => stage.lane === 'primary')), [pipelineStages]);

  const [crmRailLiveCounts, setCrmRailLiveCounts] = useState({});

  /* WILSY_P60K5K8B_STOP_RAIL_SOURCE_POSTURE_LOOP_DOCSAFE */
  useEffect(() => {
    let cancelled = false;
    const railTenantId = resolveR88FCrmCommandTenantId(tenantConfig, user);
    const cacheKey = `R91K179E24P45B:${railTenantId}`;
    const cooldownMs = 60000;

    const railCache =
      globalThis.__WILSY_P60K5K8B_RAIL_SOURCE_POSTURE_CACHE__ ||
      (globalThis.__WILSY_P60K5K8B_RAIL_SOURCE_POSTURE_CACHE__ = {
        key: '',
        expiresAt: 0,
        payload: null,
        promise: null,
      });

    if (railCache.key === cacheKey && railCache.payload && railCache.expiresAt > Date.now()) {
      setCrmRailLiveCounts(extractWilsyR91K179E24P45BRailLiveCounts(railCache.payload || {}));

      return () => {
        cancelled = true;
      };
    }

    if (railCache.key === cacheKey && railCache.promise) {
      railCache.promise
        .then((payload) => {
          if (!cancelled) {
            setCrmRailLiveCounts(extractWilsyR91K179E24P45BRailLiveCounts(payload || {}));
          }
        })
        .catch(() => {
          if (!cancelled) {
            setCrmRailLiveCounts({});
          }
        });

      return () => {
        cancelled = true;
      };
    }

    railCache.key = cacheKey;
    railCache.promise = fetch(`${API_BASE}${CRM_SOURCE_POSTURE_ENDPOINT}?railCounts=R91K179E24P45B&generatedAt=${Date.now()}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Cache-Control': 'no-cache',
        'X-Tenant-Id': railTenantId,
        'X-Wilsy-Tenant-ID': railTenantId,
        'X-Operator-ID': 'wilsy-crm-rail-live-count-bridge',
        'X-Operator-Role': 'Founder',
      },
      cache: 'no-store',
    })
      .then((response) => (response.ok ? response.json() : {}))
      .then((payload) => {
        railCache.payload = payload || {};
        railCache.expiresAt = Date.now() + cooldownMs;
        return railCache.payload;
      })
      .catch(() => {
        railCache.payload = {};
        railCache.expiresAt = Date.now() + cooldownMs;
        return {};
      })
      .finally(() => {
        railCache.promise = null;
      });

    railCache.promise
      .then((payload) => {
        if (!cancelled) {
          setCrmRailLiveCounts(extractWilsyR91K179E24P45BRailLiveCounts(payload || {}));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setCrmRailLiveCounts({});
        }
      });

    return () => {
      cancelled = true;
    };
  }, [
    tenantConfig?.id,
    tenantConfig?.tenantId,
    tenantConfig?.tenantKey,
    tenantConfig?.slug,
    user?.id,
    user?._id,
    user?.tenantId,
    user?.email,
  ]);

  const workspaceTelemetry = useMemo(
    () => buildCrmWorkspaceTelemetry(operatingSnapshot, visibleCrmWorkspaces),
    [operatingSnapshot, visibleCrmWorkspaces]
  );
  const createWorkspaceRail = useMemo(
    () => buildCrmCreateWorkspaceRail(operatingSnapshot, visibleCrmWorkspaces),
    [operatingSnapshot, visibleCrmWorkspaces]
  );

  /**
   * @function resolveWorkspaceCount
   * @description Resolves live CRM workspace counts from backend sourcePosture before falling back to local workspace metadata.
   * @param {Object} workspace - CRM workspace rail item.
   * @returns {number} Source-honest record count for the workspace.
   * @collaboration CRM live source routes, Records rail, Create workspace rail, Wilsy AI source posture and no-placeholder count evidence.
   */
  const resolveWorkspaceCount = useCallback((workspace = {}) => {
    const workspaceId = String(workspace?.id || workspace?.key || workspace?.label || '').trim().toLowerCase();
    const labelId = String(workspace?.label || '').trim().toLowerCase();

    const liveRailCount = Number(
      crmRailLiveCounts[workspaceId] ??
      crmRailLiveCounts[labelId]
    );

    if (Number.isFinite(liveRailCount) && liveRailCount >= 0) {
      return liveRailCount;
    }

    const sourceRows = [
      ...(Array.isArray(operatingSnapshot?.sourcePosture?.sources) ? operatingSnapshot.sourcePosture.sources : []),
      ...(Array.isArray(operatingSnapshot?.sourcePosture?.raw?.sources) ? operatingSnapshot.sourcePosture.raw.sources : []),
      ...(Array.isArray(operatingSnapshot?.sourcePosture?.payload?.sources) ? operatingSnapshot.sourcePosture.payload.sources : []),
      ...(Array.isArray(operatingSnapshot?.sourceGuide?.sourcePosture?.sources) ? operatingSnapshot.sourceGuide.sourcePosture.sources : []),
      ...(Array.isArray(operatingSnapshot?.sources) ? operatingSnapshot.sources : []),
    ];

    const row = sourceRows.find((source = {}) => {
      const routeTail = String(source.route || '')
        .split('/')
        .filter(Boolean)
        .pop();

      return [
        source.id,
        source.key,
        source.collection,
        source.label,
        routeTail,
      ]
        .map((value) => String(value || '').trim().toLowerCase())
        .filter(Boolean)
        .some((value) => value === workspaceId || value === labelId);
    });

    const sourceCount = Number(
      row?.recordCount ??
      row?.count ??
      row?.meta?.count ??
      row?.recordsLength ??
      (Array.isArray(row?.records) ? row.records.length : undefined) ??
      (Array.isArray(row?.data) ? row.data.length : undefined)
    );

    if (Number.isFinite(sourceCount) && sourceCount >= 0) {
      return sourceCount;
    }

    const localRecords = operatingSnapshot?.[workspace.id];

    if (Array.isArray(localRecords)) {
      return localRecords.length;
    }

    const fallbackCount = Number(workspace.count);

    return Number.isFinite(fallbackCount) && fallbackCount >= 0 ? fallbackCount : 0;
  }, [crmRailLiveCounts, operatingSnapshot]);

  const crmRailWorkspaceTelemetry = useMemo(
    () => workspaceTelemetry.map((workspace) => ({
      ...workspace,
      count: resolveWorkspaceCount(workspace),
    })),
    [resolveWorkspaceCount, workspaceTelemetry]
  );

  const crmRailVisibleWorkspaces = useMemo(
    () => visibleCrmWorkspaces.map((workspace) => ({
      ...workspace,
      count: resolveWorkspaceCount(workspace),
    })),
    [resolveWorkspaceCount, visibleCrmWorkspaces]
  );



  const primaryPipelineStages = useMemo(
    () => pipelineStages.filter(stage => stage.lane === 'primary'),
    [pipelineStages]
  );

  const sovereignPipelineStages = useMemo(
    () => pipelineStages.filter(stage => stage.lane === 'sovereign'),
    [pipelineStages]
  );

  const disruptionFeatures = useMemo(
    () => buildCrmDisruptionFeatures(operatingSnapshot, primaryPipelineStages, readinessScore),
    [primaryPipelineStages, readinessScore, operatingSnapshot]
  );

  const workspaceMeta = useMemo(
    () => visibleCrmWorkspaces.find(workspace => workspace.id === activeWorkspace) || visibleCrmWorkspaces[0] || CRM_WORKSPACES[0],
    [activeWorkspace, visibleCrmWorkspaces]
  );

  const createWorkspaceMeta = useMemo(
    () => createWorkspaceRail.find(workspace => workspace.id === createWorkspaceModule) || createWorkspaceRail[0] || null,
    [createWorkspaceModule, createWorkspaceRail]
  );
  const ActiveCreateIcon = createWorkspaceMeta?.icon || Database;

  const sourceErrors = operatingSnapshot.sourcePosture.errors || [];
  const rootHashStatus = operatingSnapshot.sourcePosture.rootHashShort ? `Root ${operatingSnapshot.sourcePosture.rootHashShort}` : (operatingSnapshot.evidence.length ? `${operatingSnapshot.evidence.length} receipt anchor${operatingSnapshot.evidence.length === 1 ? '' : 's'}` : 'Root hash pending');

  const activeRecords = useMemo(() => {
    const collection = operatingSnapshot[activeWorkspace];
    if (!Array.isArray(collection)) return [];
    const query = searchTerm.trim().toLowerCase();
    if (!query) return collection;

    return collection.filter(record => [
      record.name,
      record.company,
      record.email,
      record.phone,
      record.status,
      record.stage,
      record.source
    ].some(value => String(value || '').toLowerCase().includes(query)));
  }, [activeWorkspace, operatingSnapshot, searchTerm]);

  const refreshSources = useCallback(() => {
    setRefreshSignal(value => value + 1);
  }, []);

  const openCreateFlow = useCallback((workspace = 'leads') => {
    const allowedWorkspace = crmPermissionProfile.allowedWorkspaceIds.includes(workspace)
      ? workspace
      : (createWorkspaceRail[0]?.id || 'leads');

    setCreateWorkspaceModule(allowedWorkspace);

    if (allowedWorkspace === 'leads') {
      setActiveWorkspace('leads');
    } else {
      setActiveWorkspace('home');
      setActiveHomeTab('create');
    }

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:crm:create-record', {
        detail: {
          workspace: allowedWorkspace,
          tenantId: tenantIdentity.tenantId,
          accessScope: crmPermissionProfile.scope,
          source: 'CRMDashboard'
        }
      }));
    }
  }, [createWorkspaceRail, crmPermissionProfile.allowedWorkspaceIds, crmPermissionProfile.scope, tenantIdentity.tenantId]);

  
  /* R91K131_FULL_VIEWPOINT_RETURN_GATE */
  if (['pipeline', 'create', 'proof'].includes(activeHomeTab)) {
    return (
      <WilsyR91K131FullViewpointSurface
        mode={activeHomeTab}
        operatingSnapshot={operatingSnapshot}
        sourceGuide={typeof sourceGuide !== 'undefined' ? sourceGuide : null}
        readinessScore={typeof readinessScore !== 'undefined' ? readinessScore : null}
        rootHashStatus={typeof rootHashStatus !== 'undefined' ? rootHashStatus : null}
        onReturnToOperate={() => setActiveHomeTab('operate')}
      
        activeHomeTab={activeHomeTab}
      
        onActivateSourceGate={(gate) => {
          const targetWorkspace = gate?.id === 'connectors' ? 'connectors' : (gate?.id || 'leads');

          setCreateWorkspaceModule(targetWorkspace);

          if (targetWorkspace === 'leads') {
            openCreateFlow('leads');
            return;
          }

          setActiveWorkspace(targetWorkspace);
        }}
      />
    );
  }

return (
    <div
      className={styles.crmShell}
      data-wilsy-active-workspace={activeWorkspace}
      data-wilsy-active-home-tab={activeHomeTab}
      data-wilsy-r91k123b-mode-screen="active-tab-layout-takeover"
      data-wilsy-rail-engine-state={crmRailEngineStateR65A}
      data-wilsy-crm-dashboard="sovereign-sales-cockpit"
      data-wilsy-version={CRM_INTERNAL_DIAGNOSTIC_ID}
      data-wilsy-theme={themeRuntime.themeId}
      data-wilsy-mode={themeRuntime.effectiveMode}
      data-wilsy-resolved-mode={themeRuntime.resolvedMode}
      data-wilsy-crm-access-scope={crmPermissionProfile.scope}
      style={crmThemeVars}
    >

      <CrmSovereignSideRail
        activeWorkspace={activeWorkspace}
        snapshot={operatingSnapshot}
        tenantConfig={tenantConfig}
        user={user}
        onWorkspaceSelect={(workspaceId) => {
          if (crmPermissionProfile.allowedWorkspaceIds.includes(workspaceId)) {
            setActiveWorkspace(workspaceId);
          }
        }}
        onRailStateChange={setCrmRailEngineStateR65A}
        workspaceTelemetry={crmRailWorkspaceTelemetry}
  workspaces={crmRailVisibleWorkspaces}
/>

      <section className={styles.commandSurface}>
        {activeWorkspace === 'home' ? (
        <header data-wilsy-r85-crm-workspace-topbar="tabbed-command" className={styles.osChrome}>
          <div className={styles.chromeTitle}>
            <small><Home size={13} /> CRM Workspace</small>
            <h1 className={styles.crmOneLineTitleLock} aria-label="Wilsy CRM Workspace">
              <span className={styles.crmOneLineTitleText}>Wilsy&nbsp;<span className={styles.crmOneLineTitleGold}>CRM</span></span>
            </h1>
            <p>Source-led pipeline. Live modules. Compliance proof.</p>
          </div>

          <nav className={styles.crmTopAppMenu} aria-label="CRM command menu">
            {visibleHomeTabs.map(tab => {
              const TabIcon = tab.icon;
              return (
                <button
                  type="button"
                  key={tab.id}
                  data-active={activeHomeTab === tab.id ? 'true' : 'false'}
                  onClick={() => {
                    setActiveHomeTab(tab.id);

                    if (typeof window !== 'undefined') {
                      const url = new URL(window.location.href);
                      url.searchParams.delete('crmWorkspace');
                      window.history.replaceState(window.history.state, '', url.toString());
                    }
                  }}
                >
                  <TabIcon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </nav>

          <div className={styles.investorStrip} aria-label="Investor telemetry">
            <span title={rootHashStatus}><LockKeyhole size={16} /> {String(rootHashStatus || '').toLowerCase().includes('root') ? 'Root sealed' : 'Root pending'}</span>
            <span><Network size={16} /> {resolveWilsyR91K110RouteSurfaceLabel(operatingSnapshot.sourcePosture)}</span>
            <span><Shield size={16} /> {readinessScore}% readiness</span>
          </div>

          <div className={styles.chromeTenant}>
            <img
              src={tenantIdentity.logo}
              alt={tenantIdentity.name}
              onError={event => {
                event.currentTarget.onerror = null;
                event.currentTarget.src = wilsyLogo;
              }}
            />
            <span>
              <small>Tenant Identity</small>
              <strong>{tenantIdentity.name}</strong>
              <em>{crmPermissionProfile.accessLabel}</em>
            </span>
          </div>

          <label className={styles.chromeSearch}>
            <Search size={19} />
            <input
              value={searchTerm}
              onChange={(event) => {
                const query = event.target.value;
                const normalizedQuery = query.trim();

                setSearchTerm(query);
                setSovereignSearchQuery(query);
                setSovereignSearchOpen(Boolean(normalizedQuery));

                if (normalizedQuery.length >= 2) {
                  searchCrmCommandFabric({
                    tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                    query,
                    limit: 10
                  }).catch(() => {});
                }
              }}
              onFocus={(event) => {
                const query = event.currentTarget.value;
                setSovereignSearchQuery(query);
                setSovereignSearchOpen(true);
              }}
              onKeyDown={(event) => {
                const query = String(event.currentTarget.value || '');
                const normalizedQuery = query.trim();

                if (event.key === 'Enter') {
                  event.preventDefault();
                  setSearchTerm(query);
                  setSovereignSearchQuery(query);
                  setSovereignSearchOpen(Boolean(normalizedQuery));
                  return;
                }

                if (event.key === 'Escape') {
                  setSovereignSearchOpen(false);
                }
              }}
              placeholder={crmPermissionProfile.canSeeTenantWideData ? 'Search pipeline, accounts, evidence' : 'Search my leads, tasks, meetings'}
              aria-label="Global CRM search"
              data-wilsy-r73b-search-input="true"
              data-wilsy-r74c-search-results-driver="true"
            />
            <span
              className={styles.sovereignSearchSubmitFeedback}
              data-wilsy-r74a-search-submit-status="true"
              role="status"
              aria-live="assertive"
            >
              READY — PRESS ENTER
            </span>
            <kbd>⌘ K</kbd>
          </label>

          <div className={styles.chromeActions}>
            <button type="button" onClick={() => setAccountSettingsOpen(true)}>
              <Command size={18} />
              Command
            </button>
            <button type="button" onClick={() => {
                  syncCrmCommandFabric({
                    tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                    activeModule: 'leads',
                    reason: 'TOP_RAIL_LIVE_SYNC'
                  }).catch(() => {});
            }}>
              <RefreshCcw size={18} className={loading ? styles.spin : ''} />
              Sync
            </button>
            <button type="button" className={styles.primaryAction} onClick={() => openCreateFlow('leads')}>
              <Plus size={18} />
              Add Lead
            </button>
          </div>
        </header>
        ) : null}

        <main className={styles.workspaceViewport}>
          {activeWorkspace === 'leads' ? (
              <WilsyLeadOperatingRoom
                leads={Array.isArray(operatingSnapshot?.leads) ? operatingSnapshot.leads : []}
                searchTerm={searchTerm}
                loading={loading}
                themeRuntime={themeRuntime}
                tenantConfig={tenantConfig}
                user={user}
                onOpenThemeAuthority={() => setAccountSettingsOpen(true)}
                onSearch={(queryValue) => {
                  setSearchTerm(queryValue);

                  if (String(queryValue || '').trim().length >= 2) {
                    searchCrmCommandFabric({
                      tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                      query: queryValue,
                      limit: 25
                    }).catch(() => {});
                  }
                }}
                onSync={() => syncCrmCommandFabric({
                  tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                  activeModule: 'leads',
                  reason: 'R66B_LEAD_INGESTION_VALIDATION_SYNC'
                })}
                onSaveLead={async (leadPayload) => {
                  const commandTenantId = resolveR88FCrmCommandTenantId(tenantConfig, user);
                  const createResponse = await createCrmCommandLead({
                    tenantId: commandTenantId,
                    lead: leadPayload
                  });

                  await syncCrmCommandFabric({
                    tenantId: commandTenantId,
                    activeModule: 'leads',
                    reason: 'R88F_LEAD_PERSISTENCE_TRUTH_SAVE'
                  }).catch(() => {});

                  return createResponse;
                }}
              />
            ) : activeWorkspace === 'meetings' ? (
              <WilsyMeetingOperatingRoom
                meetings={Array.isArray(operatingSnapshot?.meetings) ? operatingSnapshot.meetings : []}
                records={Array.isArray(operatingSnapshot?.meetings) ? operatingSnapshot.meetings : []}
                sourcePosture={operatingSnapshot?.sourcePosture}
                searchTerm={searchTerm}
                loading={loading}
                themeRuntime={themeRuntime}
                tenantConfig={tenantConfig}
                user={user}
                onOpenThemeAuthority={() => setAccountSettingsOpen(true)}
                onSearch={(queryValue) => {
                  setSearchTerm(queryValue);
                }}
                onSync={() => syncCrmCommandFabric({
                  tenantId: resolveR88FCrmCommandTenantId(tenantConfig, user),
                  activeModule: 'meetings',
                  reason: 'R91K179E24P28C_REAL_MEETINGS_WORKSPACE_SYNC'
                }).catch(() => {})}
                onCreateMeeting={() => openCreateFlow('meetings')}
                onCreate={() => openCreateFlow('meetings')}
                onBackHome={() => setActiveWorkspace('home')}
              />
              
            ) : activeWorkspace === 'home' ? (
            <section className={styles.homeGrid}>
              <section className={styles.crmWorkspaceDeck} aria-label="CRM module workspaces">
                {workspaceTelemetry.map(workspace => {
                  const WorkspaceIcon = workspace.icon;
                  return (
                    <button
                      type="button"
                      key={workspace.id}
                      data-status={workspace.status}
                      data-active={activeWorkspace === workspace.id ? 'true' : 'false'}
                      onClick={() => setActiveWorkspace(workspace.id)}
                    >
                      <WorkspaceIcon size={18} />
                      <span>
                        <strong>{workspace.label}</strong>
                        <em>{workspace.detail}</em>
                      </span>
                      <b>{resolveWorkspaceCount(workspace)}</b>
                      <small>{workspace.source}</small>
                    </button>
                  );
                })}
              </section>

              <section className={styles.metricDeck} aria-label="CRM posture">
                <article className={styles.metricCard}>
                  <CircleDollarSign size={27} />
                  <span>
                    <small>Weighted Pipeline</small>
                    <strong>{formatMoney(weightedPipeline)}</strong>
                    <em>{snapshot.deals.length ? `${snapshot.deals.length} source deals` : 'Pipeline awaits source deals'}</em>
                  </span>
                  <div className={styles.metricBar}><i style={{ width: `${Math.min(100, weightedPipeline ? 100 : 0)}%` }} /></div>
                </article>

                <article className={styles.metricCard}>
                  <Activity size={27} />
                  <span>
                    <small>Readiness Score</small>
                    <strong>{readinessScore}%</strong>
                    <em>{readinessNarrative}</em>
                  </span>
                  <div className={styles.metricBar}><i style={{ width: `${readinessScore}%` }} /></div>
                </article>

                <article className={styles.metricCard}>
                  <Database size={27} />
                  <span>
                    <small>Connected Sources</small>
                    <strong>{snapshot.sourcePosture.connected}/{snapshot.sourcePosture.total}</strong>
                    <em>{sourceErrors.length ? `${sourceErrors.length} source gaps` : 'All source routes clean'}</em>
                  </span>
                  <div className={styles.metricBar}><i style={{ width: `${(snapshot.sourcePosture.connected / Math.max(1, snapshot.sourcePosture.total)) * 100}%` }} /></div>
                </article>

                <article className={styles.metricCard}>
                  <Fingerprint size={27} />
                  <span>
                    <small>Evidence Posture</small>
                    <strong>{snapshot.evidence.length}</strong>
                    <em>{snapshot.evidence.length ? 'Receipts available' : 'No receipts sealed yet'}</em>
                  </span>
                  <div className={styles.metricBar}><i style={{ width: `${snapshot.evidence.length ? 100 : 0}%` }} /></div>
                </article>
              </section>
              {activeHomeTab === 'proof' ? (
                <section className={`${styles.crmProofWorkspace} ${styles.crmOsModeScreen}`} data-wilsy-r85-crm-proof-workspace="fullscreen" data-wilsy-r91k123b-mode-screen="proof">
                  <div className={styles.crmOsFullscreenCommandBar} data-wilsy-r91k124a-fullscreen-command-bar="true">
                    <span>
                      <small>WILSY CRM FULL VIEWPOINT</small>
                      <strong>
                        {activeHomeTab === 'pipeline'
                          ? 'Sovereign Pipeline Command'
                          : activeHomeTab === 'create'
                            ? 'Guided Source Creation'
                            : 'Terminal Proof Room'}
                      </strong>
                    </span>
                    <span className={styles.crmOsFullscreenTelemetry}>
                      <em>{readinessScore}% readiness</em>
                      <em>{operatingSnapshot.sourcePosture.connected}/{operatingSnapshot.sourcePosture.total} sources</em>
                      <em>{rootHashStatus}</em>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveHomeTab('operate');

                        if (typeof window !== 'undefined') {
                          const url = new URL(window.location.href);
                          url.searchParams.delete('crmWorkspace');
                          window.history.replaceState(window.history.state, '', url.toString());
                        }
                      }}
                    >
                      Return to Operate
                    </button>
                  </div>

                  <TerminalEvidenceCockpitPanel
                    tenantId={tenantConfig?.tenantId || 'MASTER'}
                    operator="CRM_DASHBOARD"
                    autoFetch
                  />
                </section>
              ) : activeHomeTab === 'create' ? (
                <section className={`${styles.crmCreateWorkspace} ${styles.crmOsModeScreen}`} aria-label="CRM create workspace" data-wilsy-r91k123b-mode-screen="create">
                  <div className={styles.crmOsFullscreenCommandBar} data-wilsy-r91k124a-fullscreen-command-bar="true">
                    <span>
                      <small>WILSY CRM FULL VIEWPOINT</small>
                      <strong>
                        {activeHomeTab === 'pipeline'
                          ? 'Sovereign Pipeline Command'
                          : activeHomeTab === 'create'
                            ? 'Guided Source Creation'
                            : 'Terminal Proof Room'}
                      </strong>
                    </span>
                    <span className={styles.crmOsFullscreenTelemetry}>
                      <em>{readinessScore}% readiness</em>
                      <em>{operatingSnapshot.sourcePosture.connected}/{operatingSnapshot.sourcePosture.total} sources</em>
                      <em>{rootHashStatus}</em>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveHomeTab('operate');

                        if (typeof window !== 'undefined') {
                          const url = new URL(window.location.href);
                          url.searchParams.delete('crmWorkspace');
                          window.history.replaceState(window.history.state, '', url.toString());
                        }
                      }}
                    >
                      Return to Operate
                    </button>
                  </div>

                  <aside className={styles.crmCreateRail} aria-label="Create workspace modules">
                    {createWorkspaceRail.map(workspace => {
                      const WorkspaceIcon = workspace.icon;
                      return (
                        <button
                          type="button"
                          key={workspace.id}
                          data-active={createWorkspaceModule === workspace.id ? 'true' : 'false'}
                          onClick={() => setCreateWorkspaceModule(workspace.id)}
                        >
                          <WorkspaceIcon size={17} />
                          <span>
                            <strong>{workspace.label}</strong>
                            <em>{workspace.readiness}</em>
                          </span>
                          <b>{resolveWorkspaceCount(workspace)}</b>
                        </button>
                      );
                    })}
                  </aside>

                  <div className={styles.crmCreateStage}>
                    <header>
                      <span className={styles.crmCreateGlyph}><ActiveCreateIcon size={22} /></span>
                      <span>
                        <small>Create Workspace</small>
                        <strong>{createWorkspaceMeta?.label || 'CRM Record'}</strong>
                        <em>{createWorkspaceMeta?.detail || 'Live CRM module creation'}</em>
                      </span>
                    </header>

                    <div className={styles.crmCreateStageCards}>
                      <article>
                        <small>Backend posture</small>
                        <strong>{snapshot.sourcePosture.connected}/{snapshot.sourcePosture.total} routes</strong>
                        <p>{sourceErrors.length ? `${sourceErrors.length} source gaps require attention.` : 'Source routes are ready for governed creation.'}</p>
                      </article>
                      <article>
                        <small>Pipeline authority</small>
                        <strong>{primaryPipelineStages.length} stages</strong>
                        <p>Intake, Contact, Qualify, Discover, Propose, Negotiate and Convert are shared across CRM and Leads.</p>
                      </article>
                      <article>
                        <small>Selected module</small>
                        <strong>{createWorkspaceMeta?.status || 'READY'}</strong>
                        <p>{createWorkspaceMeta?.readiness || 'Choose a module from the create rail.'}</p>
                      </article>
                    </div>

                    <div className={styles.crmCreateCommandBar}>
                      <button
                        type="button"
                        className={styles.primaryAction}
                        onClick={() => {
                          if ((createWorkspaceModule || 'leads') === 'leads') {
                            openCreateFlow('leads');
                            return;
                          }

                          setActiveWorkspace(createWorkspaceModule || 'leads');
                        }}
                      >
                        <Plus size={16} />
                        {createWorkspaceMeta?.actionLabel || 'Open create'}
                      </button>
                      <button type="button" onClick={() => setActiveWorkspace(createWorkspaceModule || 'leads')}>
                        Open {createWorkspaceMeta?.label || 'Module'}
                        <ChevronRight size={16} />
                      </button>
                    </div>
                  </div>
                </section>
              ) : activeHomeTab === 'operate' ? (
                <section className={styles.crmRevolutionWorkspace} aria-label="Wilsy CRM disruption engine">
                  <div className={styles.crmPatentGrid}>
                    {disruptionFeatures.map(feature => {
                      const FeatureIcon = feature.icon;
                      return (
                        <article key={feature.id} data-status={feature.status}>
                          <span className={styles.crmPatentGlyph}><FeatureIcon size={19} /></span>
                          <small>Patent Candidate</small>
                          <strong>{feature.label}</strong>
                          <b>{feature.metric}</b>
                          <p>{feature.detail}</p>
                          <em>{feature.patentSignal}</em>
                        </article>
                      );
                    })}
                  </div>

                  <aside className={styles.crmAutopilotPanel}>
                    <span className={styles.crmCreateGlyph}><Zap size={22} /></span>
                    <small>Wilsy OS Command Intelligence</small>
                    <strong>{readinessScore >= 70 ? 'Governed revenue intelligence online' : 'Revenue intelligence controlled'}</strong>
                    <p>
                      The CRM is not just storing rows. It is measuring whether each module is source-backed, proof-aware,
                      and safe enough for AI-assisted next action.
                    </p>
                    <dl>
                      <div><dt>Lead intake</dt><dd>{snapshot.leads.length}</dd></div>
                      <div><dt>Deal motion</dt><dd>{snapshot.deals.length}</dd></div>
                      <div><dt>Evidence</dt><dd>{snapshot.evidence.length}</dd></div>
                      <div><dt>Routes</dt><dd>{snapshot.sourcePosture.connected}/{snapshot.sourcePosture.total}</dd></div>
                    </dl>
                  </aside>
                </section>
              ) : (
              <section className={`${styles.pipelineCockpit} ${styles.crmOsModeScreen}`} data-wilsy-r91k123b-mode-screen="pipeline">
                  <div className={styles.crmOsFullscreenCommandBar} data-wilsy-r91k124a-fullscreen-command-bar="true">
                    <span>
                      <small>WILSY CRM FULL VIEWPOINT</small>
                      <strong>
                        {activeHomeTab === 'pipeline'
                          ? 'Sovereign Pipeline Command'
                          : activeHomeTab === 'create'
                            ? 'Guided Source Creation'
                            : 'Terminal Proof Room'}
                      </strong>
                    </span>
                    <span className={styles.crmOsFullscreenTelemetry}>
                      <em>{readinessScore}% readiness</em>
                      <em>{operatingSnapshot.sourcePosture.connected}/{operatingSnapshot.sourcePosture.total} sources</em>
                      <em>{rootHashStatus}</em>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setActiveHomeTab('operate');

                        if (typeof window !== 'undefined') {
                          const url = new URL(window.location.href);
                          url.searchParams.delete('crmWorkspace');
                          window.history.replaceState(window.history.state, '', url.toString());
                        }
                      }}
                    >
                      Return to Operate
                    </button>
                  </div>

                <div className={styles.sectionHeader}>
                  <span>
                    <small>Revenue Cockpit</small>
                    <strong>Sovereign pipeline by verified stage</strong>
                  </span>
                  <button type="button" onClick={() => setActiveWorkspace('deals')}>
                    Open Deals <ChevronRight size={16} />
                  </button>
                </div>

                <div className={styles.stageFlow} aria-label="Primary sovereign pipeline stages">
                  {primaryPipelineStages.map((stage, index) => (
                    <article key={stage.stage} data-stage-tone={stage.tone}>
                      <span className={styles.stageIndex}>0{index + 1}</span>
                      <small>{stage.stage}</small>
                      <strong>{formatMoney(stage.weightedValue)}</strong>
                      <em>{stage.count} deals · {stage.probability}%</em>
                      <p>{stage.clause}</p>
                      <span className={styles.stageProof}>{stage.proof}</span>
                      <div className={styles.stageBar}>
                        <i style={{ width: `${stage.probability}%` }} />
                      </div>
                    </article>
                  ))}
                </div>
                <div className={styles.sovereignOpsCanvas}>
                  <div className={styles.opsSignalMap} aria-label="Sovereign operating fabric">
                    <span data-ops-ready={snapshot.sourcePosture.connected > 0 ? 'true' : 'false'}>
                      <Mail size={16} />
                      <strong>Email</strong>
                      <small>{snapshot.sourcePosture.connected ? 'Source live' : 'Awaiting source'}</small>
                    </span>
                    <span data-ops-ready={snapshot.connectors.length > 0 ? 'true' : 'false'}>
                      <Network size={16} />
                      <strong>Connectors</strong>
                      <small>{snapshot.connectors.length ? `${snapshot.connectors.length} active` : 'Not connected'}</small>
                    </span>
                    <span data-ops-ready={snapshot.evidence.length > 0 ? 'true' : 'false'}>
                      <FileCheck2 size={16} />
                      <strong>Evidence</strong>
                      <small>{snapshot.evidence.length ? `${snapshot.evidence.length} anchors` : 'No receipts'}</small>
                    </span>
                    <span data-ops-ready={snapshot.deals.length > 0 ? 'true' : 'false'}>
                      <CircleDollarSign size={16} />
                      <strong>Revenue</strong>
                      <small>{snapshot.deals.length ? `${snapshot.deals.length} deals` : 'Pipeline standby'}</small>
                    </span>
                  </div>

                  <div className={styles.opsCommandCenter}>
                    <div className={styles.opsCoreOrb} aria-hidden="true">
                      <span />
                    </div>
                    <small>Source-to-Signature Fabric</small>
                    <strong>{snapshot.sourcePosture.connected ? 'Sovereign revenue operations online' : 'Operating fabric ready for live sources'}</strong>
                    <p>{snapshot.sourcePosture.connected ? 'Wilsy OS is mapping CRM signals into governance, evidence and revenue posture.' : 'No empty canvas: this layer shows exactly which live backend sources must activate the cockpit.'}</p>
                  </div>

                  <div className={styles.opsProofLedger}>
                    <div>
                      <span>Weighted value</span>
                      <strong>{formatMoney(weightedPipeline)}</strong>
                    </div>
                    <div>
                      <span>Governance</span>
                      <strong>{readinessScore}%</strong>
                    </div>
                    <div>
                      <span>Backend profile</span>
                      <strong>{operatorIdentity.source === 'backend' ? 'DB linked' : 'Fallback'}</strong>
                    </div>
                  </div>
                </div>

                <div className={styles.sovereignStageRail} aria-label="Sovereign closure stages">
                  {sovereignPipelineStages.map(stage => (
                    <article key={stage.stage} data-stage-tone={stage.tone}>
                      <small>{stage.stage}</small>
                      <strong>{stage.probability}%</strong>
                      <span>{stage.clause}</span>
                      <em>{stage.proof}</em>
                    </article>
                  ))}
                </div>
              </section>
              )}
              <aside className={styles.commandStack} aria-label="Wilsy OS right intelligence stack">
                <article className={styles.rightIntelCard}>
                  <div className={styles.rightIntelHeader}>
                    <span className={styles.rightIntelGlyph} aria-hidden="true">
                      <Sparkles size={20} />
                    </span>
                    <span>
                      <small>AI Command Layer</small>
                      <strong>{snapshot.sourcePosture.connected ? 'Revenue intelligence online' : 'Source intelligence standby'}</strong>
                    </span>
                  </div>

                  <div className={styles.sourceConstellation} aria-label="AI source readiness">
                    <span data-source-ready={snapshot.sourcePosture.connected > 0 ? 'true' : 'false'}>
                      <i>Email</i>
                      <b>{snapshot.sourcePosture.connected > 0 ? 'Ready' : 'Gated'}</b>
                    </span>
                    <span data-source-ready={snapshot.connectors.length > 0 ? 'true' : 'false'}>
                      <i>Connectors</i>
                      <b>{snapshot.connectors.length || 'Gated'}</b>
                    </span>
                    <span data-source-ready={snapshot.evidence.length > 0 ? 'true' : 'false'}>
                      <i>Evidence</i>
                      <b>{snapshot.evidence.length || 'Gated'}</b>
                    </span>
                    <span data-source-ready={snapshot.deals.length > 0 ? 'true' : 'false'}>
                      <i>Pipeline</i>
                      <b>{snapshot.deals.length || 'Gated'}</b>
                    </span>
                  </div>

                  <div className={styles.nextActionCapsule}>
                    <small>Next best action</small>
                    <strong>{snapshot.sourcePosture.connected ? 'Inspect deal movement and evidence gaps.' : 'Connect verified CRM sources.'}</strong>
                    <p>{snapshot.sourcePosture.connected ? 'Wilsy can generate governed next actions from source context.' : 'AI remains intentionally gated until live source context is available.'}</p>
                  </div>

                  <div className={styles.rightMiniActions}>
                    <button type="button" onClick={() => setActiveWorkspace('connectors')}>
                      <Network size={15} />
                      Source Graph
                    </button>
                    <button type="button" onClick={() => setActiveWorkspace('deals')}>
                      <Target size={15} />
                      Deal Signals
                    </button>
                    <button type="button" onClick={() => openCreateFlow('leads')}>
                      <Plus size={15} />
                      Verified Lead
                    </button>
                  </div>
                </article>

                <article className={styles.proofMatrixCard}>
                  <div className={styles.rightIntelHeader}>
                    <span className={styles.rightIntelGlyph} aria-hidden="true">
                      <Shield size={20} />
                    </span>
                    <span>
                      <small>Compliance HUD</small>
                      <strong>Proof matrix</strong>
                    </span>
                  </div>

                  <div className={styles.proofScoreGrid}>
                    <div className={styles.proofRing} style={{ '--proof-score': `${readinessScore}%` }}>
                      <strong>{readinessScore}%</strong>
                      <small>Readiness</small>
                    </div>

                    <div className={styles.clauseGrid} aria-label="Compliance clauses">
                      {COMPLIANCE_BADGES.map(badge => (
                        <span key={badge}>{badge}</span>
                      ))}
                    </div>
                  </div>

                  <div className={styles.proofLedger}>
                    <div>
                      <span>Authority</span>
                      <strong>{snapshot.sourcePosture.connected ? 'Connected' : 'Pending'}</strong>
                    </div>
                    <div>
                      <span>Receipt chain</span>
                      <strong>{snapshot.evidence.length ? `${snapshot.evidence.length} anchors` : 'Not sealed'}</strong>
                    </div>
                    <div>
                      <span>Disclosure pack</span>
                      <strong>{readinessScore >= 70 ? 'Ready' : 'Incomplete'}</strong>
                    </div>
                  </div>

                  <div className={styles.proofSignal}>
                    <FileCheck2 size={16} />
                    <span>
                      <strong>{sourceErrors.length ? `${sourceErrors.length} source gaps` : 'Proof posture monitored'}</strong>
                      <small>{snapshot.evidence.length ? 'Evidence anchors available.' : 'No sealed evidence returned yet.'}</small>
                    </span>
                  </div>

                  <button type="button" className={styles.proofAction} onClick={() => setActiveWorkspace('evidence')}>
                    Open Evidence <ChevronRight size={16} />
                  </button>
                </article>
              </aside>

              <section className={styles.quickActions}>
                <article>
                  <Users size={19} />
                  <small>Lead Intake</small>
                  <strong>{snapshot.leads.length}</strong>
                  <p>{snapshot.leads.length ? 'Source leads available.' : 'No verified leads captured.'}</p>
                  <button type="button" onClick={() => openCreateFlow('leads')}>Add Lead</button>
                </article>
                <article>
                  <Target size={19} />
                  <small>Deal Motion</small>
                  <strong>{snapshot.deals.length}</strong>
                  <p>{snapshot.deals.length ? 'Deals in pipeline.' : 'No deal records returned.'}</p>
                  <button type="button" onClick={() => setActiveWorkspace('deals')}>Create Deal</button>
                </article>
                <article>
                  <CheckCircle2 size={19} />
                  <small>Execution</small>
                  <strong>{snapshot.tasks.length}</strong>
                  <p>{snapshot.tasks.length ? 'Tasks available.' : 'No open tasks returned.'}</p>
                  <button type="button" onClick={() => setActiveWorkspace('tasks')}>Create Task</button>
                </article>
                <article>
                  <CalendarDays size={19} />
                  <small>Meetings</small>
                  <strong>{snapshot.meetings.length}</strong>
                  <p>{snapshot.meetings.length ? 'Meetings available.' : 'No meetings scheduled.'}</p>
                  <button type="button" onClick={() => setActiveWorkspace('meetings')}>Schedule</button>
                </article>
                <article className={styles.wideAction}>
                  <FileCheck2 size={19} />
                  <small>Evidence</small>
                  <strong>{snapshot.evidence.length}</strong>
                  <p>{snapshot.evidence.length ? 'Evidence records available.' : 'No receipts or evidence records returned.'}</p>
                  <button type="button" onClick={() => setActiveWorkspace('evidence')}>Upload Evidence</button>
                </article>
              </section>
            </section>
            ) : activeWorkspace === 'meetings' ? (
              <section
          className={styles.r91k179e2MeetingsModulePageHost}
          data-wilsy-r91k179e2-meetings-host="crm-module-page"
          aria-label="CRM Meetings module page host"
        >
          <WilsyMeetingOperatingRoom
            tenantConfig={tenantConfig}
            onBackToCrm={() => setActiveWorkspace('operate')}
          />
        </section>
            ) : activeWorkspace === 'contacts' ? (
              <WilsyContactOperatingRoom
                contacts={snapshot.contacts || []}
                accounts={snapshot.accounts || []}
                deals={snapshot.deals || []}
                evidence={snapshot.evidence || []}
                connectors={snapshot.connectors || []}
                sourcePosture={snapshot.sourcePosture || {}}
                sourceErrors={sourceErrors}
                loading={loading}
                themeRuntime={themeRuntime}
                tenantConfig={tenantConfig}
                user={user}
                onOpenThemeAuthority={() => setAccountSettingsOpen(true)}
                onRefresh={refreshSources}
                onCreate={() => openCreateFlow('contacts')}
              />
            ) : activeWorkspace === 'accounts' ? (
              <WilsyAccountOperatingRoom
                accounts={snapshot.accounts || []}
                contacts={snapshot.contacts || []}
                deals={snapshot.deals || []}
                evidence={snapshot.evidence || []}
                connectors={snapshot.connectors || []}
                sourcePosture={snapshot.sourcePosture || {}}
                sourceErrors={sourceErrors}
                loading={loading}
                themeRuntime={themeRuntime}
                tenantConfig={tenantConfig}
                user={user}
                onOpenThemeAuthority={() => setAccountSettingsOpen(true)}
                onRefresh={refreshSources}
                onCreate={() => openCreateFlow('accounts')}
              />
            ) : (
            <section className={styles.recordsSurface}>
              <div className={styles.recordsHeader}>
                <span>
                  <small>{workspaceMeta.group}</small>
                  <strong>{workspaceMeta.label}</strong>
                  <em>{loading ? 'Synchronising sources...' : `${activeRecords.length} visible / ${(snapshot[activeWorkspace] || []).length} total`}</em>
                </span>
                <div>
                  <button type="button" onClick={refreshSources}>
                    <RefreshCcw size={16} className={loading ? styles.spin : ''} />
                    Sync
                  </button>
                  <button type="button" className={styles.primaryAction} onClick={() => openCreateFlow(activeWorkspace)}>
                    <Plus size={16} />
                    New
                  </button>
                </div>
              </div>

              {sourceErrors.length ? (
                <div className={styles.sourceWarning}>
                  <AlertTriangle size={18} />
                  <span>{sourceErrors.length} source route{sourceErrors.length === 1 ? '' : 's'} unavailable. Showing received records only.</span>
                </div>
              ) : null}

              <div className={styles.tableFrame}>
                <table>
                  <thead>
                    <tr>
                      {(CRM_RECORD_COLUMNS[activeWorkspace] || CRM_RECORD_COLUMNS.leads).map(column => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {activeRecords.length ? activeRecords.map(record => (
                      <tr key={record.id}>
                        {(CRM_RECORD_COLUMNS[activeWorkspace] || CRM_RECORD_COLUMNS.leads).map(column => (
                          <td key={`${record.id}-${column}`}>{getRecordCellValue(record, column)}</td>
                        ))}
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan={(CRM_RECORD_COLUMNS[activeWorkspace] || CRM_RECORD_COLUMNS.leads).length}>
                          <div className={styles.emptyState}>
                            <Database size={30} />
                            <strong>No source records returned.</strong>
                            <p>{loading ? 'Synchronising CRM source routes.' : 'Connect a source or create a verified record to activate this workspace.'}</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </main>
      </section>
              {crmSetupDenied ? (
          <section
            className={styles.crmSetupAccessDeniedOverlay}
            role="dialog"
            aria-modal="true"
            aria-label="CRM setup access restricted"
          >
            <div className={styles.crmSetupAccessDeniedCard}>
              <span>Setup authority required</span>
              <strong>{crmSetupDenied.title}</strong>
              <p>{crmSetupDenied.message}</p>

              <div className={styles.crmSetupAccessDeniedGrid}>
                <article>
                  <span>Detected role</span>
                  <strong>{crmSetupDenied.matchedRole}</strong>
                </article>

                <article>
                  <span>Required authority</span>
                  <strong>{crmSetupDenied.requiredRoles.join(', ')}</strong>
                </article>

                <article>
                  <span>Command source</span>
                  <strong>{crmSetupDenied.source}</strong>
                </article>

                <article>
                  <span>Checked at</span>
                  <strong>{crmSetupDenied.generatedAt}</strong>
                </article>
              </div>

              <button type="button" onClick={() => setCrmSetupDenied(null)}>
                Close
              </button>
            </div>
          </section>
        ) : null}
        {/* WILSY_SETUP_ACCESS_DENIED_PANEL */}
        {crmSetupOpen ? (
          <section
            className={styles.crmSetupAuthorityOverlay}
            role="dialog"
            aria-modal="true"
            aria-label="CRM setup operating controls"
          >
            <header className={styles.crmSetupAuthorityChrome}>
              <div>
                <span>Setup</span>
                <strong>CRM Operating Controls</strong>
                <small>Sovereign admin command plane. Authority, custody, automation, and proof stay under review.</small>
              </div>

              <button type="button" onClick={closeCrmSetupControlPlane}>
                Close
              </button>
            </header>

            <div className={styles.crmSetupAuthorityViewport}>
              <WilsyCrmSetupControlPlane setupOperatingModel={[]} />
            </div>
          </section>
        ) : null}
        {/* WILSY_P60H1_CRM_SETUP_OVERLAY */}
<WilsyAccountCommandCenter
        isOpen={accountSettingsOpen}
        onClose={() => setAccountSettingsOpen(false)}
        activeThemeId={themeRuntime.themeId}
        themeMode={themeRuntime.effectiveMode}
        onThemeChange={nextTheme => {
          const themeId = nextTheme?.id || nextTheme?.themeId || nextTheme;
          const mode = themeRuntime.effectiveMode || 'night';

          try {
            commitWilsyThemeRuntime(
              {
                themeId,
                mode,
                source: 'CRMDashboard.accountThemeChange'
              },
              {
                dispatch: true,
                source: 'CRMDashboard.accountThemeChange'
              }
            );
          } catch (error) {
            window.dispatchEvent(new CustomEvent('wilsy:theme-change', {
              detail: { themeId, mode, source: 'CRMDashboard.accountThemeChangeFallback' }
            }));
          }

          setThemeRuntime(previous => resolveCrmGlobalThemeRuntime({ themeId, mode }, previous));
        }}
        onModeChange={nextMode => {
          const mode = nextMode?.id || nextMode?.mode || nextMode;
          const themeId = themeRuntime.themeId || 'crm_revenue_pulse';

          try {
            commitWilsyThemeRuntime(
              {
                themeId,
                mode,
                source: 'CRMDashboard.accountModeChange'
              },
              {
                dispatch: true,
                source: 'CRMDashboard.accountModeChange'
              }
            );
          } catch (error) {
            window.dispatchEvent(new CustomEvent('wilsy:theme-change', {
              detail: { themeId, mode, source: 'CRMDashboard.accountModeChangeFallback' }
            }));
          }

          setThemeRuntime(previous => resolveCrmGlobalThemeRuntime({ themeId, mode }, previous));
        }}
      />
    </div>
  );
}

export default CRMDashboard;

// P60K5Q10FG106V_STOP_OPERATOR_PROFILE_403_CASCADE

// P60K5Q10FG106W_GATE_FINAL_PROFILE_PROBE
