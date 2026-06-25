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
import { installCrmSearchOutcomeRuntime } from './CrmSearchOutcomeRuntime.js';

import { searchCrmCommandFabric, syncCrmCommandFabric, createCrmCommandLead } from '../../services/crmService.js';

import CrmSovereignSideRail from './rail/CrmSovereignSideRail.jsx';

import WilsyLeadOperatingRoom from './lead/WilsyLeadOperatingRoom.jsx';

import TerminalEvidenceCockpitPanel from './TerminalEvidenceCockpitPanel.js';
const WILSY_R66A_LEAD_OPERATING_ROOM = 'R66A-WILSY-LEAD-OPERATING-ROOM';
const WILSY_R65A_TRI_STATE_KINETIC_RAIL = 'R65A-TRI-STATE-KINETIC-RAIL';
const WILSY_R62I_CRM_CLEAN_INLINE_COMMAND_FABRIC = 'R62I-CRM-CLEAN-INLINE-COMMAND-FABRIC';
const CRM_INTERNAL_DIAGNOSTIC_ID = 'CRM-COMMAND-CENTER';
const API_BASE = import.meta.env.VITE_API_URL || '';

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
    stage: 'Prospecting',
    aliases: ['Lead Generation'],
    probability: 10,
    lane: 'primary',
    tone: 'blue',
    clause: 'ICP fit and POPIA lead consent basis',
    proof: 'Lead source receipt'
  },
  {
    stage: 'Lead Qualification',
    aliases: ['Qualification', 'Sales Qualified'],
    probability: 25,
    lane: 'primary',
    tone: 'cyan',
    clause: 'BANT, authority and FICA identity posture',
    proof: 'Buyer authority marker'
  },
  {
    stage: 'Needs Analysis',
    aliases: ['Discovery', 'Needs Assessment'],
    probability: 40,
    lane: 'primary',
    tone: 'violet',
    clause: 'Pain, goals and buying criteria documented',
    proof: 'Discovery receipt'
  },
  {
    stage: 'Demo / Presentation',
    aliases: ['Demo', 'Presentation', 'Solution Fit', 'Proof of Concept'],
    probability: 55,
    lane: 'primary',
    tone: 'teal',
    clause: 'Solution fit and value case evidence',
    proof: 'Demo outcome proof'
  },
  {
    stage: 'Proposal',
    aliases: ['Offer', 'Commercial Proposal'],
    probability: 70,
    lane: 'primary',
    tone: 'gold',
    clause: 'Pricing, scope and implementation terms',
    proof: 'Offer pack hash'
  },
  {
    stage: 'Negotiation',
    aliases: ['Negotiation and Commitment', 'Commitment'],
    probability: 85,
    lane: 'primary',
    tone: 'amber',
    clause: 'Objections, redlines and authority trail',
    proof: 'Clause variance log'
  },
  {
    stage: 'Closed Won / Lost',
    aliases: ['Closed', 'Closed Won', 'Closed Lost', 'Won', 'Lost'],
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


/**
 * @function fetchCrmSourcePosture
 * @description Fetches live CRM source posture from the backend.
 * @param {string} tenantId - Active tenant id.
 * @param {AbortSignal} signal - Abort signal.
 * @returns {Promise<Object|null>} Source posture.
 * @collaboration Powers Root Hash and source-route counters from the live backend.
 */
async function fetchCrmSourcePosture(tenantId, signal) {
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
    roleLabel: safeText(source.roleLabel || source.role || source.accountRole || source.profile?.role, 'SUPER_ADMIN').toUpperCase(),
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
    fallback.roleLabel || 'SUPER_ADMIN'
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
  for (const endpoint of USER_PROFILE_ENDPOINTS) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'GET',
        headers: buildAuthHeaders(tenantId),
        signal
      });

      if (!response.ok) continue;

      const payload = await response.json();
      return normalizeBackendOperatorProfile(payload, fallback);
    } catch (error) {
      if (error?.name === 'AbortError') return fallback;
    }
  }

  return fallback;
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
        const backendPosture = await fetchCrmSourcePosture(tenantId, controller.signal);
        const enrichedResults = backendPosture && results.length
          ? results.map((result, index) => index === 0 ? { ...result, sourcePosture: backendPosture } : result)
          : results;
        setState({ snapshot: buildCrmSnapshot(enrichedResults), loading: false, error: null });
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
function CRMDashboard({ user = {}, tenantConfig = {}, onExit = null }) {
  useEffect(() => {
    return installCrmSearchOutcomeRuntime({
      tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
    });
  }, [
    tenantConfig?.tenantId,
    tenantConfig?.id,
    tenantConfig?.tenantKey,
    user?.tenantId,
    user?.tenant?.id,
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
  const [searchTerm, setSearchTerm] = useState('');
  const [crmRailEngineStateR65A, setCrmRailEngineStateR65A] = useState('EXPANDED');

  const [refreshSignal, setRefreshSignal] = useState(0);
  const [accountSettingsOpen, setAccountSettingsOpen] = useState(false);
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

  const readinessScore = useMemo(() => calculateReadinessScore(snapshot), [snapshot]);
  const pipelineStages = useMemo(() => buildPipelineStages(snapshot.deals), [snapshot.deals]);
  const weightedPipeline = useMemo(() => buildPipelineTotal(pipelineStages.filter(stage => stage.lane === 'primary')), [pipelineStages]);

  const primaryPipelineStages = useMemo(
    () => pipelineStages.filter(stage => stage.lane === 'primary'),
    [pipelineStages]
  );

  const sovereignPipelineStages = useMemo(
    () => pipelineStages.filter(stage => stage.lane === 'sovereign'),
    [pipelineStages]
  );

  const workspaceMeta = useMemo(
    () => CRM_WORKSPACES.find(workspace => workspace.id === activeWorkspace) || CRM_WORKSPACES[0],
    [activeWorkspace]
  );

  const sourceErrors = snapshot.sourcePosture.errors || [];
  const rootHashStatus = snapshot.sourcePosture.rootHashShort ? `Root ${snapshot.sourcePosture.rootHashShort}` : (snapshot.evidence.length ? `${snapshot.evidence.length} receipt anchor${snapshot.evidence.length === 1 ? '' : 's'}` : 'Root hash pending');

  const activeRecords = useMemo(() => {
    const collection = snapshot[activeWorkspace];
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
  }, [activeWorkspace, snapshot, searchTerm]);

  const refreshSources = useCallback(() => {
    setRefreshSignal(value => value + 1);
  }, []);

  const openCreateFlow = useCallback((workspace = 'leads') => {
    setActiveWorkspace(workspace);

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:crm:create-record', {
        detail: {
          workspace,
          tenantId: tenantIdentity.tenantId,
          source: 'CRMDashboard'
        }
      }));
    }
  }, [tenantIdentity.tenantId]);

  return (
    <div
      className={styles.crmShell}
      data-wilsy-active-workspace={activeWorkspace}
      data-wilsy-rail-engine-state={crmRailEngineStateR65A}
      data-wilsy-crm-dashboard="sovereign-sales-cockpit"
      data-wilsy-version={CRM_INTERNAL_DIAGNOSTIC_ID}
      data-wilsy-theme={themeRuntime.themeId}
      data-wilsy-mode={themeRuntime.effectiveMode}
      data-wilsy-resolved-mode={themeRuntime.resolvedMode}
      style={crmThemeVars}
    >

      <CrmSovereignSideRail
        workspaces={CRM_WORKSPACES}
        activeWorkspace={activeWorkspace}
        snapshot={snapshot}
        tenantConfig={tenantConfig}
        user={user}
        onWorkspaceSelect={(workspaceId) => setActiveWorkspace(workspaceId)}
        onRailStateChange={setCrmRailEngineStateR65A}
      />

      <section className={styles.commandSurface}>
        <header className={styles.osChrome}>
          <div className={styles.chromeTitle}>
            <small><Home size={13} /> {workspaceMeta.label}</small>
            <h1 className={styles.crmOneLineTitleLock} aria-label="Wilsy OS CRM Command Center">
                    <span className={styles.crmOneLineTitleText}>Wilsy&nbsp;OS&nbsp;<span className={styles.crmOneLineTitleGold}>CRM</span>&nbsp;Command&nbsp;Center</span>
                  </h1>
            <p>Sovereign sales intelligence. Source-led pipeline. Compliance proof.</p>
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
              <em>Live tenant boundary</em>
            </span>
          </div>

          <div className={styles.investorStrip} aria-label="Investor telemetry">
            <span><LockKeyhole size={16} /> {rootHashStatus}</span>
            <span><Network size={16} /> {snapshot.sourcePosture.connected}/{snapshot.sourcePosture.total} source routes</span>
            <span><Shield size={16} /> {readinessScore}% governance readiness</span>
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
              placeholder="Search pipeline, accounts, evidence"
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
              Command Center
            </button>
            <button type="button" onClick={() => {
                  syncCrmCommandFabric({
                    tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                    activeModule: 'leads',
                    reason: 'TOP_RAIL_LIVE_SYNC'
                  }).catch(() => {});
                }}>
              <RefreshCcw size={18} className={loading ? styles.spin : ''} />
              Live Sync
            </button>
            <button type="button" className={styles.primaryAction} onClick={() => openCreateFlow('leads')}>
              <Plus size={18} />
              Add Lead
            </button>
          </div>
        </header>

        <main className={styles.workspaceViewport}>
          {activeWorkspace === 'leads' ? (
              <WilsyLeadOperatingRoom
                leads={Array.isArray(snapshot?.leads) ? snapshot.leads : []}
                searchTerm={searchTerm}
                loading={loading}
                tenantConfig={tenantConfig}
                user={user}
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
                onSaveLead={(leadPayload) => createCrmCommandLead({
                  tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                  lead: leadPayload
                }).then(() => syncCrmCommandFabric({
                  tenantId: tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER',
                  activeModule: 'leads',
                  reason: 'R66B_LEAD_INGESTION_VALIDATION_SAVE'
                }).catch(() => {}))}
              />
            ) : activeWorkspace === 'home' ? (
            <section className={styles.homeGrid}>
              <div data-wilsy-r72f-terminal-evidence-dashboard-wire="true">
                <TerminalEvidenceCockpitPanel
                  tenantId={tenantConfig?.tenantId || 'MASTER'}
                  operator="CRM_DASHBOARD"
                  autoFetch
                />
              </div>

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
                    <em>{readinessScore ? 'Source posture improving' : 'Connect sources to lift readiness'}</em>
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
              <section className={styles.pipelineCockpit}>
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
                tenantConfig={tenantConfig}
                user={user}
                onRefresh={refreshSources}
                onCreate={() => openCreateFlow('contacts')}
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
