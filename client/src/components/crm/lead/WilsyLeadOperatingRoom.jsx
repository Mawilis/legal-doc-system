/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - LEAD OPERATING ROOM [R68B-TABBED-MODULE-OPERATING-SYSTEM]                                                 ║
 * ║ ZOHO-INSPIRED MODULE BAR | SOURCE-DERIVED PRIORITY | DROPDOWN ACTIONS | RECORDS-FIRST OS DENSITY                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/crm/lead/WilsyLeadOperatingRoom.jsx        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF                                                                                    ║
 * ║ • Wilson Khanyezi - Mandated a Zoho-inspired tabbed module bar that obliterates the continuous card runway.            ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Recast Leads into a records-first tabbed OS module with view dropdowns,        ║
 * ║   sort/filter controls, row actions, mass-action posture, and preserved backend authority/no-fake-row discipline.       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Wilsy OS Lead Operating Room.
 * The component renders a lead command surface from backend records only. It derives priority,
 * workflow lanes and source posture from existing lead fields, sync telemetry and proof hashes.
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  CalendarDays,
  ChevronDown,
  CheckCircle2,
  ClipboardList,
  Command,
  Database,
  Download,
  FileInput,
  Filter,
  Fingerprint,
  LayoutPanelTop,
  List,
  Mail,
  MoreHorizontal,
  Phone,
  Plus,
  RotateCw,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  SplitSquareHorizontal,
  SlidersHorizontal,
  Upload,
  UserRoundCog,
  WandSparkles
} from 'lucide-react';
import { WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION, resolveCrmThemeEngineOptions } from '../theme/wilsyCrmThemeEngineBridge.js';
import styles from './WilsyLeadOperatingRoom.module.css';

const WILSY_LEAD_OPERATING_ROOM_VERSION = 'R68B-TABBED-MODULE-OPERATING-SYSTEM';
const WILSY_LEAD_HEADER_BRIDGE_VERSION = 'R67D-SOVEREIGN-HEADER-COMMAND-BRIDGE';
const WILSY_LEAD_OS_CANVAS_VERSION = 'R68A-LEAD-OS-COMMAND-DECK';
const WILSY_LEAD_TABBED_APP_BAR_VERSION = 'R68B-ZOHO-INSPIRED-TABBED-APP-BAR';

const WILSY_LEAD_THEME_AUTHORITY = 'CRM_THEME_ENGINE_BRIDGE';

const EMPTY_LEAD_DRAFT = Object.freeze({
  name: '',
  company: '',
  email: '',
  phone: '',
  mobile: '',
  title: '',
  source: 'Website',
  status: 'NEW',
  industry: '',
  owner: '',
  rating: 'Warm',
  employees: '',
  website: '',
  annualRevenue: '',
  street: '',
  city: '',
  state: '',
  zipCode: '',
  country: '',
  description: ''
});

const REQUIRED_LEAD_FIELDS = Object.freeze(['name', 'company', 'email']);

const LEAD_COLUMNS = Object.freeze([
  { key: 'name', label: 'Lead Name' },
  { key: 'company', label: 'Company' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'provenanceHash', label: 'Provenance Hash' },
  { key: 'complianceStatus', label: 'Compliance Status' },
  { key: 'owner', label: 'Owner' },
  { key: 'lastActivity', label: 'Last Activity' }
]);

const LEAD_VIEWS = Object.freeze(['ALL', 'VERIFIED', 'PENDING', 'FAILED']);

const LEAD_LIST_VIEWS = Object.freeze([
  { id: 'ALL_LEADS', label: 'All Leads', filter: 'ALL', detail: 'Every source-backed row' },
  { id: 'HIGH_PRIORITY', label: 'Priority Leads', filter: 'ALL', detail: 'Score 52 and above' },
  { id: 'VERIFIED_LEADS', label: 'Verified Leads', filter: 'VERIFIED', detail: 'Compliance passed' },
  { id: 'PENDING_REVIEW', label: 'Pending Review', filter: 'PENDING', detail: 'Awaiting audit' },
  { id: 'SOURCE_GAPS', label: 'Source Gaps', filter: 'ALL', detail: 'Needs provenance' },
  { id: 'UNTOUCHED', label: 'Untouched', filter: 'ALL', detail: 'No activity signal' },
  { id: 'FAILED_GATES', label: 'Failed Gates', filter: 'FAILED', detail: 'Rejected or failed' }
]);

const LEAD_TOP_APP_TABS = Object.freeze([
  { id: 'records', label: 'Records', icon: List },
  { id: 'signals', label: 'Signals', icon: Sparkles },
  { id: 'pipeline', label: 'Pipeline', icon: Activity },
  { id: 'proof', label: 'Proof', icon: ShieldCheck },
  { id: 'sources', label: 'Sources', icon: Database }
]);

const LEAD_SORT_OPTIONS = Object.freeze([
  { id: 'priority', label: 'Priority score' },
  { id: 'name', label: 'Lead name' },
  { id: 'company', label: 'Company' },
  { id: 'recent', label: 'Last activity' }
]);

const LEAD_FILTER_GROUPS = Object.freeze([
  {
    title: 'System Defined Filters',
    options: ['Activities', 'Campaigns', 'Latest Email Status', 'Record Action', 'Related Records', 'Touched Records', 'Untouched Records']
  },
  {
    title: 'Field Filters',
    options: ['Annual Revenue', 'City', 'Company', 'Email', 'Lead Source', 'Owner', 'Phone', 'Status']
  },
  {
    title: 'Wilsy Proof Filters',
    options: ['Verified Provenance', 'Missing Root Seal', 'POPIA Ready', 'Source Gap', 'AI Ready']
  }
]);

const LEAD_JOURNEY_LANES = Object.freeze([
  {
    id: 'intake',
    label: 'Intake',
    headline: 'Capture',
    aliases: ['NEW', 'OPEN', 'UNSTAGED', 'PENDING', 'SOURCE RECEIVED'],
    action: 'Verify source'
  },
  {
    id: 'qualify',
    label: 'Qualify',
    headline: 'Fit',
    aliases: ['CONTACTED', 'QUALIFIED', 'QUALIFICATION', 'SALES QUALIFIED', 'WARM'],
    action: 'Confirm authority'
  },
  {
    id: 'engage',
    label: 'Engage',
    headline: 'Conversation',
    aliases: ['DISCOVERY', 'NEEDS ANALYSIS', 'DEMO', 'PRESENTATION', 'MEETING'],
    action: 'Schedule next step'
  },
  {
    id: 'prove',
    label: 'Prove',
    headline: 'Evidence',
    aliases: ['COMPLIANCE', 'PROPOSAL', 'NEGOTIATION', 'REVIEW'],
    action: 'Seal proof'
  },
  {
    id: 'convert',
    label: 'Convert',
    headline: 'Outcome',
    aliases: ['CONVERTED', 'WON', 'LOST', 'CLOSED', 'DISQUALIFIED'],
    action: 'Record outcome'
  }
]);

const SETUP_GROUPS = [
  { title: 'General', items: ['Personal Settings', 'Users', 'Company Settings'] },
  { title: 'Security Control', items: ['Profiles', 'Roles and Sharing', 'Compliance Settings'] },
  { title: 'Customization', items: ['Modules and Fields', 'Lead Layouts', 'Workflow Rules'] },
  { title: 'Data Administration', items: ['Import', 'Export', 'Data Backup'] },
  { title: 'Developer Hub', items: ['APIs and SDKs', 'Extensions', 'Catalyst Solutions'] }
];

/**
 * @function resolveLeadRole
 * @description Resolves a normalized CRM role for Lead workspace permissions.
 * @param {Object} user - User packet.
 * @param {Object} tenantConfig - Tenant config.
 * @returns {string} Normalized role.
 * @collaboration Keeps Lead actions role-aware without hardcoding one operator.
 */
function resolveLeadRole(user = {}, tenantConfig = {}) {
  return String(user?.role || user?.accountRole || user?.profile?.role || tenantConfig?.role || tenantConfig?.userRole || 'SALES_REP').toUpperCase();
}

/**
 * @function resolveTenantId
 * @description Resolves tenant id for Lead command fabric calls.
 * @param {Object} tenantConfig - Tenant config.
 * @param {Object} user - User packet.
 * @returns {string} Tenant id.
 * @collaboration Keeps search, sync and create tenant-bound.
 */
function resolveTenantId(tenantConfig = {}, user = {}) {
  return String(tenantConfig?.tenantId || tenantConfig?.id || tenantConfig?.tenantKey || user?.tenantId || user?.tenant?.id || 'MASTER');
}

/**
 * @function canUseLeadAction
 * @description Evaluates whether a role can use a Lead action.
 * @param {string} role - Normalized role.
 * @param {string} action - Action key.
 * @returns {boolean} Permission result.
 * @collaboration Prevents sales users from seeing admin-only controls.
 */
function canUseLeadAction(role = 'SALES_REP', action = 'view') {
  const masterRoles = ['MASTER', 'FOUNDER', 'SUPER_ADMIN', 'ROOT'];
  const adminRoles = [...masterRoles, 'TENANT_ADMIN', 'ADMIN', 'CRM_ADMIN'];
  const managerRoles = [...adminRoles, 'SALES_MANAGER', 'MANAGER'];

  if (masterRoles.includes(role)) return true;
  if (['view', 'search', 'create', 'calendar', 'note', 'call', 'meeting', 'email', 'sync'].includes(action)) return true;
  if (['import', 'export', 'bulk', 'assign'].includes(action)) return managerRoles.includes(role);
  if (['delete', 'subscription', 'tenant-admin', 'setup'].includes(action)) return adminRoles.includes(role);

  return false;
}

/**
 * @function createEmptyLeadDraft
 * @description Creates an empty Lead draft with operator owner default.
 * @param {Object} user - User packet.
 * @returns {Object} Empty draft.
 * @collaboration Keeps create state deterministic until backend save.
 */
function createEmptyLeadDraft(user = {}) {
  return {
    ...EMPTY_LEAD_DRAFT,
    owner: user?.name || user?.fullName || user?.email || ''
  };
}

/**
 * @function getComplianceStatus
 * @description Resolves compliance status from Lead source fields.
 * @param {Object} record - Lead record.
 * @returns {string} Compliance status.
 * @collaboration Shows audit posture without inventing records.
 */
function getComplianceStatus(record = {}) {
  const raw = String(record.complianceStatus || record.sourceStatus || record.verificationStatus || '').toUpperCase();

  if (raw.includes('VERIFIED') || raw.includes('SOURCE_LIVE') || raw.includes('PASSED')) return 'VERIFIED';
  if (raw.includes('FAILED') || raw.includes('REJECTED')) return 'FAILED';
  if (raw.includes('PENDING') || raw.includes('REVIEW')) return 'PENDING';

  return 'PENDING';
}

/**
 * @function getProvenanceHash
 * @description Resolves a provenance hash from available record fields.
 * @param {Object} record - Lead record.
 * @returns {string} Provenance hash.
 * @collaboration Surfaces source-trace transparency in the ledger.
 */
function getProvenanceHash(record = {}) {
  return String(record.cryptographicHash || record.provenanceHash || record.rootHash || record.sealHash || record._id || record.id || 'UNSEALED');
}

/**
 * @function isLeadDraftValid
 * @description Checks required fields before backend creation.
 * @param {Object} draft - Lead draft.
 * @returns {boolean} True when valid.
 * @collaboration Blocks empty-click lead creation.
 */
function isLeadDraftValid(draft = {}) {
  return REQUIRED_LEAD_FIELDS.every(field => String(draft[field] || '').trim().length > 0);
}

/**
 * @function normalizeLeadPayload
 * @description Adds source metadata to the lead payload.
 * @param {Object} draft - Lead draft.
 * @param {string} tenantId - Tenant id.
 * @returns {Object} Normalized payload.
 * @collaboration Separates browser action from backend authority.
 */
function normalizeLeadPayload(draft = {}, tenantId = 'MASTER') {
  return {
    ...draft,
    tenantId,
    complianceStatus: 'PENDING',
    sourceStatus: 'SOURCE_LIVE',
    sourceSystem: 'WILSY_OS_LEAD_CONTEXTUAL_COMMAND_STRIP',
    operatingRoom: 'LEADS'
  };
}

/**
 * @function resolveLeadValue
 * @description Resolves grid values from flexible backend Lead records.
 * @param {Object} record - Lead record.
 * @param {string} field - Logical field.
 * @returns {string} Display value.
 * @collaboration Supports current and future CRM schemas.
 */
function resolveLeadValue(record = {}, field = '') {
  const values = {
    name: record.name || record.fullName || [record.firstName, record.lastName].filter(Boolean).join(' '),
    company: record.company || record.accountName || record.organization,
    email: record.email || record.primaryEmail,
    phone: record.phone || record.mobile || record.primaryPhone,
    provenanceHash: getProvenanceHash(record),
    complianceStatus: getComplianceStatus(record),
    owner: record.owner || record.ownerName || record.assignedTo,
    lastActivity: record.lastActivity || record.updatedAt || record.createdAt
  };

  return String(values[field] || '—');
}

/**
 * @function resolveLeadRecordId
 * @description Resolves a stable browser key for one lead row.
 * @param {Object} record - Lead record.
 * @param {number} index - Record index.
 * @returns {string} Stable id.
 * @collaboration Lets list selection stay deterministic without inventing backend identifiers.
 */
function resolveLeadRecordId(record = {}, index = 0) {
  return String(record._id || record.id || record.uuid || record.recordId || record.provenanceHash || `lead-${index}`);
}

/**
 * @function resolveLeadSource
 * @description Resolves a lead source label from flexible backend fields.
 * @param {Object} record - Lead record.
 * @returns {string} Source label.
 * @collaboration Keeps source channels tied to backend payload fields only.
 */
function resolveLeadSource(record = {}) {
  return String(record.source || record.sourceSystem || record.connector || record.origin || record.campaign || 'Backend CRM').trim();
}

/**
 * @function resolveLeadStage
 * @description Resolves a normalized workflow stage from lead status fields.
 * @param {Object} record - Lead record.
 * @returns {string} Normalized stage label.
 * @collaboration Maps existing backend stage/status vocabulary into one operator journey board.
 */
function resolveLeadStage(record = {}) {
  return String(record.stage || record.pipelineStage || record.status || record.leadStatus || record.rating || 'Unstaged').trim() || 'Unstaged';
}

/**
 * @function isKnownLeadValue
 * @description Checks whether a resolved lead field has useful source content.
 * @param {string} value - Resolved display value.
 * @returns {boolean} True when content is useful.
 * @collaboration Prevents priority and action links from treating placeholders as real data.
 */
function isKnownLeadValue(value = '') {
  const text = String(value || '').trim();
  return Boolean(text && text !== '—' && text !== 'UNSEALED');
}

/**
 * @function resolveLeadPriorityScore
 * @description Calculates a source-derived priority score without using synthetic lead facts.
 * @param {Object} record - Lead record.
 * @returns {number} Priority score from 0 to 100.
 * @collaboration Gives operators a useful working order while preserving no-fake-data discipline.
 */
function resolveLeadPriorityScore(record = {}) {
  const complianceStatus = getComplianceStatus(record);
  const provenanceHash = getProvenanceHash(record);
  const stage = resolveLeadStage(record).toUpperCase();
  const source = resolveLeadSource(record);

  const fieldScore = [
    isKnownLeadValue(resolveLeadValue(record, 'name')),
    isKnownLeadValue(resolveLeadValue(record, 'company')),
    isKnownLeadValue(resolveLeadValue(record, 'email')),
    isKnownLeadValue(resolveLeadValue(record, 'phone')),
    isKnownLeadValue(source)
  ].filter(Boolean).length * 9;

  const complianceScore = complianceStatus === 'VERIFIED' ? 28 : complianceStatus === 'PENDING' ? 13 : 0;
  const proofScore = isKnownLeadValue(provenanceHash) ? 18 : 0;
  const motionScore = /QUALIFIED|CONTACTED|DEMO|PRESENTATION|PROPOSAL|NEGOTIATION|CONVERTED|WON/.test(stage) ? 9 : 0;

  return Math.max(0, Math.min(100, fieldScore + complianceScore + proofScore + motionScore));
}

/**
 * @function resolveLeadPriorityBand
 * @description Converts a numeric priority score into an operator-facing band.
 * @param {number} score - Priority score.
 * @returns {string} Priority band.
 * @collaboration Keeps urgency labels deterministic and explainable.
 */
function resolveLeadPriorityBand(score = 0) {
  if (score >= 78) return 'PRIORITY';
  if (score >= 52) return 'READY';
  if (score >= 24) return 'VERIFY';
  return 'SOURCE GAP';
}

/**
 * @function matchLeadJourneyLane
 * @description Finds the buyer journey lane for one lead record.
 * @param {Object} record - Lead record.
 * @returns {Object} Journey lane.
 * @collaboration Lets Wilsy OS show CRM motion without relying on a single vendor schema.
 */
function matchLeadJourneyLane(record = {}) {
  const stage = resolveLeadStage(record).toUpperCase();
  const complianceStatus = getComplianceStatus(record);

  if (complianceStatus === 'FAILED') return LEAD_JOURNEY_LANES[0];

  return LEAD_JOURNEY_LANES.find(lane => lane.aliases.some(alias => stage.includes(alias))) || LEAD_JOURNEY_LANES[0];
}

/**
 * @function buildLeadJourneyLanes
 * @description Groups lead records into OS buyer-journey lanes.
 * @param {Array<Object>} records - Lead records.
 * @returns {Array<Object>} Journey lanes with records and score averages.
 * @collaboration Replaces passive record presentation with an operating workflow map.
 */
function buildLeadJourneyLanes(records = []) {
  return LEAD_JOURNEY_LANES.map(lane => {
    const laneRecords = records.filter(record => matchLeadJourneyLane(record).id === lane.id);
    const scoreTotal = laneRecords.reduce((sum, record) => sum + resolveLeadPriorityScore(record), 0);
    const averageScore = laneRecords.length ? Math.round(scoreTotal / laneRecords.length) : 0;

    return {
      ...lane,
      records: laneRecords,
      count: laneRecords.length,
      averageScore
    };
  });
}

/**
 * @function buildLeadSourceChannels
 * @description Builds source channel chips from sync registry or live lead source fields.
 * @param {Array<Object>} routeRegistry - Sync route registry.
 * @param {Array<Object>} leads - Lead records.
 * @returns {Array<Object>} Source channels.
 * @collaboration Keeps upstream visibility real while giving operators a compact route map.
 */
function buildLeadSourceChannels(routeRegistry = [], leads = []) {
  if (Array.isArray(routeRegistry) && routeRegistry.length) {
    return routeRegistry.map(route => ({
      id: String(route.key || route.id || route.name || 'route'),
      label: String(route.label || route.key || route.id || route.name || 'Route'),
      count: Number(route.count || route.total || 0),
      connected: Boolean(route.connected || route.status === 'live' || route.sourceStatus === 'SOURCE_LIVE')
    }));
  }

  const sourceCounts = leads.reduce((map, record) => {
    const source = resolveLeadSource(record);
    map.set(source, (map.get(source) || 0) + 1);
    return map;
  }, new Map());

  return Array.from(sourceCounts.entries()).map(([label, count]) => ({
    id: label,
    label,
    count,
    connected: count > 0
  }));
}

/**
 * @function resolveLeadContactHref
 * @description Builds safe contact links for email and phone actions.
 * @param {Object} record - Lead record.
 * @param {string} channel - Contact channel.
 * @returns {string|null} Contact href or null.
 * @collaboration Makes quick actions operate on real lead fields without unsafe script links.
 */
function resolveLeadContactHref(record = {}, channel = 'email') {
  if (channel === 'email') {
    const email = resolveLeadValue(record, 'email');
    return isKnownLeadValue(email) ? `mailto:${email}` : null;
  }

  const phone = resolveLeadValue(record, 'phone');
  const normalizedPhone = String(phone || '').replace(/[^\d+]/g, '');
  return isKnownLeadValue(phone) && normalizedPhone ? `tel:${normalizedPhone}` : null;
}

/**
 * @function resolveLeadListView
 * @description Resolves a configured Lead list view from dropdown state.
 * @param {string} listViewId - List view id.
 * @returns {Object} Lead list view config.
 * @collaboration Keeps the Zoho-inspired view dropdown deterministic and source-backed.
 */
function resolveLeadListView(listViewId = 'ALL_LEADS') {
  return LEAD_LIST_VIEWS.find(view => view.id === listViewId) || LEAD_LIST_VIEWS[0];
}

/**
 * @function doesLeadMatchListView
 * @description Checks whether a lead belongs in the active module list view.
 * @param {Object} record - Lead record.
 * @param {string} listViewId - List view id.
 * @returns {boolean} True when the lead matches the view.
 * @collaboration Adds serious list-view organization without fabricating backend rows.
 */
function doesLeadMatchListView(record = {}, listViewId = 'ALL_LEADS') {
  const activeView = resolveLeadListView(listViewId);
  const complianceStatus = getComplianceStatus(record);
  const priorityScore = resolveLeadPriorityScore(record);
  const provenanceHash = getProvenanceHash(record);
  const source = resolveLeadSource(record);
  const activityValue = resolveLeadValue(record, 'lastActivity');
  const hasActivitySignal = isKnownLeadValue(activityValue)
    || Boolean(record.activityCount || record.touchCount || record.lastTouchedAt || record.lastContactedAt || record.activities?.length);

  switch (activeView.id) {
    case 'HIGH_PRIORITY':
      return priorityScore >= 52;
    case 'VERIFIED_LEADS':
      return complianceStatus === 'VERIFIED';
    case 'PENDING_REVIEW':
      return complianceStatus === 'PENDING';
    case 'SOURCE_GAPS':
      return !isKnownLeadValue(provenanceHash) || !isKnownLeadValue(source);
    case 'UNTOUCHED':
      return !hasActivitySignal;
    case 'FAILED_GATES':
      return complianceStatus === 'FAILED';
    case 'ALL_LEADS':
    default:
      return true;
  }
}

/**
 * @function sortLeadRecords
 * @description Sorts lead records for the active module list view.
 * @param {Array<Object>} records - Lead records.
 * @param {string} sortMode - Sort mode.
 * @returns {Array<Object>} Sorted records.
 * @collaboration Gives the Leads module list behavior operators expect from a world-class CRM.
 */
function sortLeadRecords(records = [], sortMode = 'priority') {
  const sortedRecords = [...records];

  return sortedRecords.sort((leftRecord, rightRecord) => {
    if (sortMode === 'name') {
      return resolveLeadValue(leftRecord, 'name').localeCompare(resolveLeadValue(rightRecord, 'name'));
    }

    if (sortMode === 'company') {
      return resolveLeadValue(leftRecord, 'company').localeCompare(resolveLeadValue(rightRecord, 'company'));
    }

    if (sortMode === 'recent') {
      const leftDate = Date.parse(resolveLeadValue(leftRecord, 'lastActivity')) || 0;
      const rightDate = Date.parse(resolveLeadValue(rightRecord, 'lastActivity')) || 0;
      return rightDate - leftDate;
    }

    return resolveLeadPriorityScore(rightRecord) - resolveLeadPriorityScore(leftRecord);
  });
}

/**
 * @function buildLeadOperatingMetrics
 * @description Builds the top Lead OS metric deck from live state.
 * @param {Object} input - Metric input packet.
 * @returns {Array<Object>} Metric cards.
 * @collaboration Turns screenshots into a scannable command deck without adding fabricated totals.
 */
function buildLeadOperatingMetrics({
  leads = [],
  filteredLeads = [],
  complianceMetrics = {},
  liveSources = 0,
  totalSources = 0,
  rootHash = 'UNSEALED'
} = {}) {
  const priorityReady = leads.filter(record => resolveLeadPriorityScore(record) >= 52).length;
  const sourceProgress = totalSources ? Math.round((liveSources / Math.max(1, totalSources)) * 100) : 0;
  const rootSealed = isKnownLeadValue(String(rootHash || ''));

  return [
    {
      id: 'intake',
      label: 'Lead Intake',
      value: String(leads.length),
      detail: filteredLeads.length === leads.length ? 'All source rows visible' : `${filteredLeads.length} filtered`,
      progress: leads.length ? 100 : 0,
      icon: Database
    },
    {
      id: 'priority',
      label: 'Work Queue',
      value: String(priorityReady),
      detail: priorityReady ? 'Ready for operator action' : 'Awaiting enough source signal',
      progress: leads.length ? Math.round((priorityReady / Math.max(1, leads.length)) * 100) : 0,
      icon: Sparkles
    },
    {
      id: 'compliance',
      label: 'Verified',
      value: `${complianceMetrics.verified || 0}/${complianceMetrics.total || 0}`,
      detail: complianceMetrics.failed ? `${complianceMetrics.failed} failed gates` : 'No failed gates visible',
      progress: complianceMetrics.total ? Math.round(((complianceMetrics.verified || 0) / Math.max(1, complianceMetrics.total)) * 100) : 0,
      icon: ShieldCheck
    },
    {
      id: 'source',
      label: 'Source Trust',
      value: totalSources ? `${liveSources}/${totalSources}` : 'SYNC',
      detail: rootSealed ? `Root ${String(rootHash).slice(0, 12)}` : 'Root seal pending',
      progress: sourceProgress,
      icon: Fingerprint
    }
  ];
}

/**
 * @function buildCalendarDays
 * @description Builds day cells for the Lead calendar shell.
 * @returns {number[]} Day slots.
 * @collaboration Provides activity planning without fake backend events.
 */
function buildCalendarDays() {
  return Array.from({ length: 35 }, (_, index) => index + 1);
}


/**
 * @function resolveCrmGlobalThemeAuthorityLabel
 * @description Resolves a business-facing label for the active Command Center operating skin.
 * @param {Object} themeRuntime - Active CRM/global theme runtime packet.
 * @returns {string} Business-facing theme label.
 * @collaboration R79B Command Center theme authority, CRM module chrome, 26-skin global registry.
 */
function resolveCrmGlobalThemeAuthorityLabel(themeRuntime = {}) {
  const rawLabel = themeRuntime.label
    || themeRuntime.name
    || themeRuntime.title
    || themeRuntime.displayName
    || themeRuntime.themeLabel
    || themeRuntime.skinLabel
    || themeRuntime.themeId
    || 'Command Center Theme';

  return String(rawLabel)
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, letter => letter.toUpperCase());
}

/**
 * @function resolveCrmGlobalThemeAuthorityMode
 * @description Resolves a business-facing mode label for the active global theme runtime.
 * @param {Object} themeRuntime - Active CRM/global theme runtime packet.
 * @returns {string} Business-facing mode label.
 * @collaboration R79B Day/Night/Auto command mode, Command Center runtime, CRM module chrome.
 */
function resolveCrmGlobalThemeAuthorityMode(themeRuntime = {}) {
  const rawMode = themeRuntime.resolvedMode || themeRuntime.effectiveMode || themeRuntime.mode || 'night';
  const normalized = String(rawMode).replace(/[-_]+/g, ' ').trim();

  return normalized ? normalized.replace(/\b\w/g, letter => letter.toUpperCase()) : 'Night';
}

/**
 * @function openCrmGlobalThemeAuthorityFallback
 * @description Opens the global theme authority through the CRM/Command Center event bridge when no direct handler is provided.
 * @returns {void}
 * @collaboration R79B module theme authority button, Account Command Center, global skin governance.
 */
function openCrmGlobalThemeAuthorityFallback() {
  if (typeof window === 'undefined') return;

  window.dispatchEvent(new CustomEvent('wilsy:crm:open-command-center', {
    detail: {
      panel: 'preferences',
      section: 'theme-authority',
      source: 'CRM_GLOBAL_THEME_AUTHORITY'
    }
  }));
}


const LEAD_FILTER_OPERATING_SECTIONS = Object.freeze([
  {
    id: 'SYSTEM_DEFINED_FILTERS',
    title: 'System Defined Filters',
    options: [
      { id: 'activities', label: 'Activities', detail: 'Leads with activity history' },
      { id: 'campaigns', label: 'Campaigns', detail: 'Campaign-attributed leads' },
      { id: 'latest_email_status', label: 'Latest Email Status', detail: 'Email engagement state' },
      { id: 'record_action', label: 'Record Action', detail: 'Actionable CRM records' },
      { id: 'related_records_action', label: 'Related Records Action', detail: 'Linked record action signals' },
      { id: 'touched_records', label: 'Touched Records', detail: 'Recently engaged leads' },
      { id: 'untouched_records', label: 'Untouched Records', detail: 'No recent engagement' }
    ]
  },
  {
    id: 'FILTER_BY_FIELDS_PRIMARY',
    title: 'Filter By Fields',
    options: [
      { id: 'annual_revenue', label: 'Annual Revenue', detail: 'Revenue size band' },
      { id: 'city', label: 'City', detail: 'City or operating region' },
      { id: 'company', label: 'Company', detail: 'Company or organization' },
      { id: 'converted_account', label: 'Converted Account', detail: 'Converted account status' },
      { id: 'converted_contact', label: 'Converted Contact', detail: 'Converted contact status' },
      { id: 'converted_deal', label: 'Converted Deal', detail: 'Converted opportunity status' },
      { id: 'country', label: 'Country', detail: 'Country or jurisdiction' },
      { id: 'created_by', label: 'Created By', detail: 'Creator identity' },
      { id: 'created_time', label: 'Created Time', detail: 'Creation window' },
      { id: 'email', label: 'Email', detail: 'Email availability' },
      { id: 'email_opt_out', label: 'Email Opt Out', detail: 'Marketing consent posture' },
      { id: 'fax', label: 'Fax', detail: 'Fax number availability' },
      { id: 'first_name', label: 'First Name', detail: 'First-name field' },
      { id: 'industry', label: 'Industry', detail: 'Industry classification' },
      { id: 'last_activity_time', label: 'Last Activity Time', detail: 'Most recent engagement time' },
      { id: 'last_name', label: 'Last Name', detail: 'Last-name field' },
      { id: 'lead_conversion_time', label: 'Lead Conversion Time', detail: 'Conversion date and time' },
      { id: 'lead_name', label: 'Lead Name', detail: 'Lead identity' },
      { id: 'lead_owner', label: 'Lead Owner', detail: 'Assigned owner' },
      { id: 'lead_source', label: 'Lead Source', detail: 'Source channel' },
      { id: 'lead_status', label: 'Lead Status', detail: 'Lead stage' },
      { id: 'mobile', label: 'Mobile', detail: 'Mobile number availability' },
      { id: 'modified_by', label: 'Modified By', detail: 'Last modifier' },
      { id: 'modified_time', label: 'Modified Time', detail: 'Last modified time' },
      { id: 'employees', label: 'No. of Employees', detail: 'Company headcount' },
      { id: 'phone', label: 'Phone', detail: 'Phone number availability' },
      { id: 'rating', label: 'Rating', detail: 'Lead rating' },
      { id: 'salutation', label: 'Salutation', detail: 'Formal salutation' },
      { id: 'title', label: 'Title', detail: 'Job title' },
      { id: 'twitter', label: 'Twitter', detail: 'Social profile' },
      { id: 'unsubscribed_mode', label: 'Unsubscribed Mode', detail: 'Unsubscribe channel' },
      { id: 'unsubscribed_time', label: 'Unsubscribed Time', detail: 'Unsubscribe timestamp' },
      { id: 'website', label: 'Website', detail: 'Website availability' },
      { id: 'zip_code', label: 'Zip Code', detail: 'Postal code' }
    ]
  },
  {
    id: 'FILTER_BY_RELATED_MODULES',
    title: 'Filter By Related Modules',
    options: [
      { id: 'calls', label: 'Calls', detail: 'Call-linked leads' },
      { id: 'emails', label: 'Emails', detail: 'Email-linked leads' },
      { id: 'invitees', label: 'Invitees (Invited Meetings)', detail: 'Meeting invitees' },
      { id: 'meetings', label: 'Meetings', detail: 'Meeting-linked leads' },
      { id: 'notes', label: 'Notes', detail: 'Note-linked leads' },
      { id: 'tasks', label: 'Tasks', detail: 'Task-linked leads' }
    ]
  }
]);

/**
 * @function WilsyLeadOperatingRoom
 * @description Renders the production Lead operating room with contextual command strip and skin-aware density.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Lead operating room.
 * @collaboration Replaces action-fatigue layout with a high-density sovereign cockpit.
 */
export default function WilsyLeadOperatingRoom({
  leads = [],
  searchTerm = '',
  onSearch,
  onSync,
  onSaveLead,
  tenantConfig = {},
  user = {},
  loading = false,
  themeRuntime = {},
  onOpenThemeAuthority = openCrmGlobalThemeAuthorityFallback
}) {
  const role = resolveLeadRole(user, tenantConfig);
  const globalThemeAuthorityLabel = resolveCrmGlobalThemeAuthorityLabel(themeRuntime);
  const globalThemeAuthorityMode = resolveCrmGlobalThemeAuthorityMode(themeRuntime);
  const tenantId = resolveTenantId(tenantConfig, user);
  const [mode, setMode] = useState('list');
  const [activeTopTab, setActiveTopTab] = useState('records');
  const [activeListViewId, setActiveListViewId] = useState('ALL_LEADS');
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [leadFilterQuery, setLeadFilterQuery] = useState('');
  const [selectedLeadFilterOptions, setSelectedLeadFilterOptions] = useState(() => new Set());
  const [sortMode, setSortMode] = useState('priority');
  const [leadSkin, setLeadSkin] = useState('crm_revenue_pulse');
  const [splitView, setSplitView] = useState(false);
  const [filterPanelOpen, setFilterPanelOpen] = useState(true);
  const [viewMenuOpen, setViewMenuOpen] = useState(false);
  const [sortMenuOpen, setSortMenuOpen] = useState(false);
  const [createMenuOpen, setCreateMenuOpen] = useState(false);
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);
  const [themeMenuOpen, setThemeMenuOpen] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [setupOpen, setSetupOpen] = useState(false);
  const [coreToolsOpen, setCoreToolsOpen] = useState(false);
  const [draft, setDraft] = useState(() => createEmptyLeadDraft(user));
  const [saveStatus, setSaveStatus] = useState('');
  const [syncStatus, setSyncStatus] = useState('SOURCE_READY_UPSTREAM');
  const [syncTelemetry, setSyncTelemetry] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedLeadId, setSelectedLeadId] = useState('');
  const [selectedRowIds, setSelectedRowIds] = useState([]);
  const [openRowActionId, setOpenRowActionId] = useState('');
  const hasAutoHydratedTelemetryRef = useRef(false);
  const leadThemeOptions = useMemo(() => resolveCrmThemeEngineOptions(), []);
  const activeLeadThemeOption = useMemo(() => ({
    id: themeRuntime?.themeId || leadSkin || 'crm_revenue_pulse',
    label: globalThemeAuthorityLabel,
    className: '',
    cssVars: themeRuntime?.cssVars || undefined,
    source: 'global-command-center'
  }), [globalThemeAuthorityLabel, leadSkin, themeRuntime]);
  const activeListView = useMemo(() => resolveLeadListView(activeListViewId), [activeListViewId]);


  const complianceMetrics = useMemo(() => {
    const total = leads.length;
    const verified = leads.filter(record => getComplianceStatus(record) === 'VERIFIED').length;
    const pending = leads.filter(record => getComplianceStatus(record) === 'PENDING').length;
    const failed = leads.filter(record => getComplianceStatus(record) === 'FAILED').length;

    return { total, verified, pending, failed };
  }, [leads]);

  const filteredLeads = useMemo(() => {
    const query = String(searchTerm || '').trim().toLowerCase();

    const matchedLeads = leads.filter(record => {
      const matchesSearch = !query || JSON.stringify(record || {}).toLowerCase().includes(query);
      const status = getComplianceStatus(record);
      const matchesFilter = activeFilter === 'ALL' || status === activeFilter;
      const matchesListView = doesLeadMatchListView(record, activeListViewId);

      return matchesSearch && matchesFilter && matchesListView;
    });

    return sortLeadRecords(matchedLeads, sortMode);
  }, [activeFilter, activeListViewId, leads, searchTerm, sortMode]);

  const sourcePosture = leads.length ? 'Sources connected' : 'Ready for source connection';
  const routeRegistry = Array.isArray(syncTelemetry?.registry) ? syncTelemetry.registry : [];
  const liveSources = syncTelemetry?.liveSources ?? routeRegistry.filter(route => route.connected).length;
  const totalSources = syncTelemetry?.totalSources ?? routeRegistry.length;
  const rootHash = syncTelemetry?.rootHashShort || syncTelemetry?.rootHash || 'UNSEALED';
  const journeyLanes = useMemo(() => buildLeadJourneyLanes(filteredLeads), [filteredLeads]);
  const sourceChannels = useMemo(() => buildLeadSourceChannels(routeRegistry, leads), [routeRegistry, leads]);
  const selectedLead = useMemo(() => {
    const matchedLead = filteredLeads.find((record, index) => resolveLeadRecordId(record, index) === selectedLeadId);
    return matchedLead || filteredLeads[0] || null;
  }, [filteredLeads, selectedLeadId]);
  const operatingMetrics = useMemo(() => buildLeadOperatingMetrics({
    leads,
    filteredLeads,
    complianceMetrics,
    liveSources,
    totalSources,
    rootHash
  }), [complianceMetrics, filteredLeads, leads, liveSources, rootHash, totalSources]);

  useEffect(() => {
    if (!filteredLeads.length) {
      setSelectedLeadId('');
      return;
    }

    const hasSelectedLead = filteredLeads.some((record, index) => resolveLeadRecordId(record, index) === selectedLeadId);
    if (!hasSelectedLead) {
      setSelectedLeadId(resolveLeadRecordId(filteredLeads[0], 0));
    }
  }, [filteredLeads, selectedLeadId]);

  useEffect(() => {
    const visibleIds = new Set(filteredLeads.map((record, index) => resolveLeadRecordId(record, index)));
    setSelectedRowIds(previous => previous.filter(recordId => visibleIds.has(recordId)));
  }, [filteredLeads]);

  useEffect(() => {
    if (hasAutoHydratedTelemetryRef.current) return;
    hasAutoHydratedTelemetryRef.current = true;

    if (typeof onSync === 'function') {
      setIsSyncing(true);
      setSyncStatus('R66G_AUTO_TELEMETRY_HYDRATION');

      onSync()
        .then((telemetry) => {
          setSyncTelemetry(telemetry || null);
          setSyncStatus(telemetry?.sourceStatus || 'SOURCE_SYNC_COMPLETE');
        })
        .catch((error) => {
          setSyncStatus(error?.message || 'SOURCE_SYNC_FAILED');
        })
        .finally(() => {
          setIsSyncing(false);
        });
    }
  }, []);


  /**
   * @function updateDraftField
   * @description Updates one field on the Lead draft.
   * @param {string} field - Field key.
   * @param {string} value - Field value.
   * @returns {void}
   * @collaboration Keeps draft local until backend save.
   */
  function updateDraftField(field, value) {
    setDraft(previous => ({
      ...previous,
      [field]: value
    }));
  }

  /**
   * @function handleSearchChange
   * @description Routes Lead search through command fabric.
   * @param {string} query - Search query.
   * @returns {void}
   * @collaboration Keeps search source-backed.
   */
  function handleSearchChange(query) {
    if (typeof onSearch === 'function') {
      onSearch(query);
    }
  }

  /**
   * @function handleSourceSync
   * @description Executes backend source sync and captures telemetry.
   * @returns {Promise<void>} Sync operation.
   * @collaboration Converts empty state into a source ingestion control plane.
   */
  async function handleSourceSync() {
    if (!canUseLeadAction(role, 'sync')) {
      setSyncStatus('SYNC_LOCKED_BY_ROLE');
      return;
    }

    setIsSyncing(true);
    setSyncStatus('SYNCING_SOURCE_ROUTES');

    try {
      const telemetry = typeof onSync === 'function' ? await onSync() : null;
      setSyncTelemetry(telemetry || null);
      setSyncStatus(telemetry?.sourceStatus || 'SOURCE_SYNC_COMPLETE');
    } catch (error) {
      setSyncStatus(error?.message || 'SOURCE_SYNC_FAILED');
    } finally {
      setIsSyncing(false);
    }
  }

  /**
   * @function handleSelectLeadListView
   * @description Applies a Lead list view from the module dropdown.
   * @param {string} listViewId - List view id.
   * @returns {void}
   * @collaboration Converts the Zoho-inspired dropdown into source-backed Wilsy OS filtering.
   */
  function handleSelectLeadListView(listViewId) {
    const nextView = resolveLeadListView(listViewId);
    setActiveListViewId(nextView.id);
    setActiveFilter(nextView.filter || 'ALL');
    setViewMenuOpen(false);
    setOpenRowActionId('');
  }

  /**
   * @function handleToggleLeadSelection
   * @description Toggles one row in the Lead records grid.
   * @param {string} recordId - Lead record id.
   * @returns {void}
   * @collaboration Enables list-view mass action posture without mutating backend rows in the browser.
   */
  function handleToggleLeadSelection(recordId) {
    setSelectedRowIds(previous => (
      previous.includes(recordId)
        ? previous.filter(value => value !== recordId)
        : [...previous, recordId]
    ));
  }

  /**
   * @function handleToggleAllLeadSelection
   * @description Toggles selection for every visible Lead row.
   * @returns {void}
   * @collaboration Mirrors enterprise CRM list-view behavior while keeping actions explicit.
   */
  function handleToggleAllLeadSelection() {
    const visibleIds = filteredLeads.map((record, index) => resolveLeadRecordId(record, index));
    const allSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));

    if (allSelected) {
      setSelectedRowIds([]);
      return;
    }

    setSelectedRowIds(visibleIds);
  }

  /**
   * @function handleSaveLead
   * @description Saves a valid Lead draft through backend command fabric.
   * @param {boolean} createAnother - Whether to reset the draft after save.
   * @returns {Promise<void>} Save operation.
   * @collaboration Prevents fake rows and preserves backend authority.
   */
  async function handleSaveLead(createAnother = false) {
    if (!canUseLeadAction(role, 'create')) {
      setSaveStatus('Create Lead is locked by role policy.');
      return;
    }

    if (!isLeadDraftValid(draft)) {
      setSaveStatus('Lead name, company and email are required before backend creation.');
      return;
    }

    setSaveStatus('Sending verified Lead payload to backend command fabric...');

    try {
      if (typeof onSaveLead === 'function') {
        await onSaveLead(normalizeLeadPayload(draft, tenantId));
      }

      setSaveStatus('Lead saved through backend command fabric.');

      if (createAnother) {
        setDraft(createEmptyLeadDraft(user));
        return;
      }

      setMode('list');
    } catch (error) {
      setSaveStatus(error?.message || 'Backend rejected the Lead payload.');
    }
  }

  /**
   * @function renderSkinSwitcher
   * @description Renders local Lead skin switcher.
   * @returns {JSX.Element} Skin switcher.
   * @collaboration Proves layout survives skin switching before global token provider rollout.
   */
  function renderSkinSwitcher() {
    return (
      <section className={styles.skinSwitcher} aria-label="Lead skin switcher">
        {leadThemeOptions.map(option => (
          <button
            key={option.id}
            type="button"
            className={option.id === activeLeadThemeOption.id ? styles.skinActive : styles.skinButton}
            onClick={() => setLeadSkin(option.id)}
            title={`Theme source: ${option.source}`}
          >
            {option.label}
          </button>
        ))}
      </section>
    );
  }

  /**
   * @function renderContextualCommandStrip
   * @description Renders the condensed command strip.
   * @returns {JSX.Element} Command strip.
   * @collaboration Removes button fatigue while keeping high-velocity actions one click away.
   */
  function renderContextualCommandStrip() {
    return (
      <section className={styles.commandStrip} data-wilsy-command-strip="contextual">
        <label className={styles.commandSearch}>
          <Search size={17} />
          <input
            value={searchTerm}
            onChange={event => handleSearchChange(event.target.value)}
            placeholder="Search records, evidence, hashes... (⌘K)"
            aria-label="Search Lead records"
          />
          <kbd>⌘K</kbd>
        </label>

        <div className={styles.commandActions}>
          <button type="button" className={styles.primaryToolbarButton} onClick={() => setMode('create')} disabled={!canUseLeadAction(role, 'create')}>
            <Plus size={17} />
            <span>New Lead</span>
          </button>

          <button type="button" className={styles.toolbarButton} onClick={handleSourceSync} disabled={!canUseLeadAction(role, 'sync') || isSyncing}>
            <RotateCw size={17} />
            <span>{isSyncing ? 'Syncing' : 'Sync Sources'}</span>
          </button>

          <div className={styles.coreToolsWrap}>
            <button type="button" className={styles.toolbarButton} onClick={() => setCoreToolsOpen(previous => !previous)}>
              <MoreHorizontal size={17} />
              <span>Core Tools</span>
            </button>

            {coreToolsOpen ? (
              <section className={styles.coreToolsMenu} aria-label="Lead core tools">
                <button type="button" disabled={!canUseLeadAction(role, 'import')}><Upload size={15} />Import Leads</button>
                <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={15} />Import Notes</button>
                <button type="button" onClick={() => setCalendarOpen(true)}><CalendarDays size={15} />Calendar View</button>
                <button type="button" onClick={() => setSplitView(previous => !previous)}><SplitSquareHorizontal size={15} />{splitView ? 'Single Interface' : 'Split Interface'}</button>
                <button type="button" onClick={() => setCommandOpen(true)}><Command size={15} />Command Center</button>
                <button type="button" disabled={!canUseLeadAction(role, 'setup')} onClick={() => setSetupOpen(true)}><Settings size={15} />Setup</button>
                <button type="button" disabled={!canUseLeadAction(role, 'export')}><Download size={15} />Export Leads</button>
              </section>
            ) : null}
          </div>
        </div>
      </section>
    );
  }

  /**
   * @function renderHeader
   * @description Renders the sovereign Lead command header with shortcuts, telemetry, search and theme authority.
   * @returns {JSX.Element} Header.
   * @collaboration Converts the Lead header from a title card into the operating app bar.
   */
  function renderHeader() {
    const routeLabel = totalSources ? `${liveSources}/${totalSources}` : 'Awaiting sync';
    const rootLabel = String(rootHash || 'UNSEALED').slice(0, 14);
    const complianceLabel = complianceMetrics.total
      ? `${complianceMetrics.verified}/${complianceMetrics.total} verified`
      : 'No records yet';
    const activeSort = LEAD_SORT_OPTIONS.find(option => option.id === sortMode) || LEAD_SORT_OPTIONS[0];

    return (
      <header
        className={styles.appHeader}
        data-wilsy-lead-appbar="sovereign-header-command-bridge"
        data-wilsy-lead-topbar={WILSY_LEAD_TABBED_APP_BAR_VERSION}
      >
        <section className={[styles.headerPrimaryRow, styles.leadModuleTopBar].join(' ')}>
          <section className={[styles.headerIdentity, styles.leadModuleTitleBlock].join(' ')}>
            <small>Sales Pipeline</small>
            <strong>{mode === 'create' ? 'Create Lead' : 'Leads'}</strong>
            <em>Sales workspace · source records monitored</em>
          </section>

          <section
            className={[styles.headerThemeDock, styles.leadModuleUtilities].join(' ')}
            data-wilsy-header-theme-dock="theme-engine-authority"
          >
            <label className={styles.headerSearch}>
              <Search size={18} />
              <input
                value={searchTerm}
                onChange={event => handleSearchChange(event.target.value)}
                placeholder="Search records"
                aria-label="Search Lead records"
              />
              <kbd>⌘K</kbd>
            </label>

            <button type="button" className={styles.leadIconButton} onClick={handleSourceSync} disabled={!canUseLeadAction(role, 'sync') || isSyncing} title="Refresh sources">
              <RotateCw size={18} />
            </button>

            <button type="button" className={styles.leadIconButton} onClick={() => setCalendarOpen(true)} title="Calendar">
              <CalendarDays size={18} />
            </button>

            <button type="button" className={styles.leadIconButton} disabled={!canUseLeadAction(role, 'setup')} onClick={() => setSetupOpen(true)} title="Setup">
              <Settings size={18} />
            </button>

            <div className={styles.leadDropdownWrap}>
                <button
                  type="button"
                  className={styles.leadUtilityButton}
                  onClick={onOpenThemeAuthority}
                  aria-label={`Open global theme authority: ${globalThemeAuthorityLabel}`}
                  data-wilsy-global-theme-authority-control="command-center"
                >
                  <Sparkles size={17} />
                  <span>
                    <small>Theme Authority</small>
                    <strong>{globalThemeAuthorityLabel}</strong>
                    <em>{globalThemeAuthorityMode}</em>
                  </span>
                  <ChevronDown size={15} />
                </button>
              </div>
          </section>
        </section>

        <section
          className={[styles.headerCommandGrid, styles.leadModuleViewBar].join(' ')}
          data-wilsy-header-command-grid="investor-grade"
        >
          <section className={styles.leadViewCluster}>
            <div className={styles.leadDropdownWrap}>
              <button type="button" className={styles.leadViewButton} onClick={() => setViewMenuOpen(previous => !previous)}>
                <List size={18} />
                <span>
                  <strong>{activeListView.label}</strong>
                  <em>{activeListView.detail}</em>
                </span>
                <ChevronDown size={16} />
              </button>

              {viewMenuOpen ? (
                <section className={styles.leadDropdownMenu} aria-label="Lead list views">
                  {LEAD_LIST_VIEWS.map(view => (
                    <button
                      key={view.id}
                      type="button"
                      data-active={view.id === activeListView.id ? 'true' : 'false'}
                      onClick={() => handleSelectLeadListView(view.id)}
                    >
                      <span>{view.label}</span>
                      <em>{view.detail}</em>
                    </button>
                  ))}
                  <button type="button" onClick={() => setCommandOpen(true)}>
                    <Plus size={14} />
                    <span>New Custom View</span>
                  </button>
                </section>
              ) : null}
            </div>

            <button type="button" className={styles.leadViewMoreButton} onClick={() => setCommandOpen(true)} title="Manage views">
              <MoreHorizontal size={18} />
            </button>
          </section>

          <section className={styles.headerInvestorStrip} data-wilsy-investor-strip="source-root-compliance">
            <article>
              <small>Source Routes</small>
              <strong>{routeLabel}</strong>
              <em>{sourcePosture}</em>
            </article>
            <article>
              <small>Sovereign Root</small>
              <strong>{rootLabel}</strong>
              <em>Provenance</em>
            </article>
            <article>
              <small>Compliance</small>
              <strong>{complianceLabel}</strong>
              <em>POPIA · GDPR · SOC2</em>
            </article>
            <article>
              <small>Theme Authority</small>
                <strong>{globalThemeAuthorityLabel}</strong>
                <em>{globalThemeAuthorityMode} · Command Center global skin</em>
            </article>
          </section>

          <nav className={styles.leadModuleTabs} aria-label="Lead operating tabs">
            {LEAD_TOP_APP_TABS.map(tab => {
              const TabIcon = tab.icon;

              return (
                <button
                  key={tab.id}
                  type="button"
                  data-active={activeTopTab === tab.id ? 'true' : 'false'}
                  onClick={() => setActiveTopTab(tab.id)}
                >
                  <TabIcon size={16} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          <section className={[styles.headerShortcutBar, styles.leadModuleToolbar].join(' ')} data-wilsy-header-shortcuts="production">
            <button
              type="button"
              onClick={() => setFilterPanelOpen(previous => !previous)}
              data-active={filterPanelOpen ? 'true' : 'false'}
            >
              <SlidersHorizontal size={18} />
              <span>Filter</span>
            </button>

            <div className={styles.leadDropdownWrap}>
              <button type="button" onClick={() => setSortMenuOpen(previous => !previous)}>
                <Filter size={18} />
                <span>Sort</span>
                <ChevronDown size={15} />
              </button>
              {sortMenuOpen ? (
                <section className={styles.leadDropdownMenu} aria-label="Lead sort options">
                  {LEAD_SORT_OPTIONS.map(option => (
                    <button
                      key={option.id}
                      type="button"
                      data-active={option.id === activeSort.id ? 'true' : 'false'}
                      onClick={() => {
                        setSortMode(option.id);
                        setSortMenuOpen(false);
                      }}
                    >
                      <span>{option.label}</span>
                    </button>
                  ))}
                </section>
              ) : null}
            </div>

            <button type="button" onClick={() => setSplitView(previous => !previous)} data-active={splitView ? 'true' : 'false'}>
              <SplitSquareHorizontal size={18} />
              <span>{splitView ? 'Single' : 'Split'}</span>
            </button>

            <div className={styles.leadCreateDock}>
              <button
                type="button"
                className={styles.headerPrimaryAction}
                onClick={() => setMode('create')}
                disabled={!canUseLeadAction(role, 'create')}
              >
                <Plus size={18} />
                <span>Create Lead</span>
              </button>
              <button
                type="button"
                className={styles.leadCreateMenuButton}
                onClick={() => setCreateMenuOpen(previous => !previous)}
                disabled={!canUseLeadAction(role, 'create')}
                title="Create options"
              >
                <ChevronDown size={16} />
              </button>
              {createMenuOpen ? (
                <section className={styles.leadDropdownMenu} aria-label="Create Lead options">
                  <button type="button" onClick={() => setMode('create')}><Plus size={14} />Create Lead</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'import')}><Upload size={14} />Import Leads</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={14} />Import Notes</button>
                </section>
              ) : null}
            </div>

            <div className={styles.headerMoreDock}>
              <button type="button" onClick={() => setMoreMenuOpen(previous => !previous)}>
                <MoreHorizontal size={18} />
                <span>More</span>
              </button>

              {moreMenuOpen ? (
                <section className={styles.headerMoreMenu} aria-label="Lead more actions">
                  <button type="button" disabled={!selectedRowIds.length}><ClipboardList size={15} />Mass Update</button>
                  <button type="button" disabled={!selectedRowIds.length}><Mail size={15} />Mass Email</button>
                  <button type="button" disabled={!selectedRowIds.length}><CheckCircle2 size={15} />Approve Leads</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'bulk')}><UserRoundCog size={15} />Change Owner</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={15} />Import Notes</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'export')}><Download size={15} />Export Leads</button>
                  <button type="button" onClick={() => setCommandOpen(true)}><Command size={15} />Command Center</button>
                  <button type="button"><Sparkles size={15} />Wilsy AI Services</button>
                </section>
              ) : null}
            </div>
          </section>
        </section>
      </header>
    );
  }

  /**
   * @function renderLeadOsMetricDeck
   * @description Renders the source-derived Lead OS metric deck.
   * @returns {JSX.Element} Lead metric deck.
   * @collaboration Converts the Lead first viewport into a measurable operating surface.
   */
  function renderLeadOsMetricDeck() {
    return (
      <section className={styles.leadOsMetricDeck} data-wilsy-lead-os-metrics="R68A-SOURCE-DERIVED">
        {operatingMetrics.map(metric => {
          const MetricIcon = metric.icon || Activity;

          return (
            <article key={metric.id} data-metric={metric.id}>
              <span className={styles.leadOsMetricIcon}>
                <MetricIcon size={22} />
              </span>
              <span className={styles.leadOsMetricCopy}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
                <em>{metric.detail}</em>
              </span>
              <div className={styles.leadOsMetricBar}>
                <i style={{ width: `${Math.max(0, Math.min(100, metric.progress || 0))}%` }} />
              </div>
            </article>
          );
        })}
      </section>
    );
  }

  /**
   * @function renderLeadQueue
   * @description Renders the active operator work queue from filtered leads.
   * @returns {JSX.Element} Lead queue.
   * @collaboration Gives operators a CRM inbox they can work instead of a static table.
   */
  function renderLeadQueue() {
    const visibleLeads = filteredLeads.slice(0, 10);

    return (
      <section className={styles.leadQueuePanel} data-wilsy-lead-queue="operator-priority">
        <header className={styles.leadPanelHeader}>
          <span>
            <small>Operator Queue</small>
            <strong>Priority Leads</strong>
          </span>
          <button type="button" onClick={() => setActiveFilter('ALL')}>
            <Filter size={15} />
            {activeFilter}
          </button>
        </header>

        {visibleLeads.length ? (
          <div className={styles.leadQueueList}>
            {visibleLeads.map((record, index) => {
              const recordId = resolveLeadRecordId(record, index);
              const priorityScore = resolveLeadPriorityScore(record);
              const complianceStatus = getComplianceStatus(record);

              return (
                <button
                  key={recordId}
                  type="button"
                  className={styles.leadQueueRow}
                  data-selected={selectedLeadId === recordId ? 'true' : 'false'}
                  onClick={() => setSelectedLeadId(recordId)}
                >
                  <span className={styles.leadQueuePrimary}>
                    <strong>{resolveLeadValue(record, 'name')}</strong>
                    <em>{resolveLeadValue(record, 'company')}</em>
                  </span>
                  <span className={styles.leadQueueMeta}>
                    <small data-status={complianceStatus}>{complianceStatus}</small>
                    <b>{resolveLeadPriorityBand(priorityScore)} · {priorityScore}</b>
                  </span>
                </button>
              );
            })}
          </div>
        ) : (
          <section className={styles.leadQueueEmpty}>
            <Database size={28} />
            <strong>No backend lead rows returned</strong>
            <p>Sync a real source, import authenticated data, or create a verified lead to activate the queue.</p>
            <div>
              <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
                <RotateCw size={15} />
                Sync Sources
              </button>
              <button type="button" onClick={() => setMode('create')} disabled={!canUseLeadAction(role, 'create')}>
                <Plus size={15} />
                New Lead
              </button>
            </div>
          </section>
        )}
      </section>
    );
  }

  /**
   * @function renderLeadJourneyBoard
   * @description Renders buyer journey lanes from live lead records.
   * @returns {JSX.Element} Journey board.
   * @collaboration Brings Pipedrive-style visual flow into Wilsy OS without copying vendor UI.
   */
  function renderLeadJourneyBoard() {
    return (
      <section className={styles.leadJourneyBoard} data-wilsy-lead-journey="buyer-motion">
        <header className={styles.leadPanelHeader}>
          <span>
            <small>Buyer Journey</small>
            <strong>Pipeline Operating Map</strong>
          </span>
          <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
            <RotateCw size={15} />
            Refresh
          </button>
        </header>

        <div className={styles.leadJourneyLanes}>
          {journeyLanes.map((lane, laneIndex) => (
            <article key={lane.id} data-lane-has-records={lane.count > 0 ? 'true' : 'false'}>
              <span className={styles.leadLaneIndex}>0{laneIndex + 1}</span>
              <small>{lane.label}</small>
              <strong>{lane.headline}</strong>
              <em>{lane.count} leads · score {lane.averageScore}</em>
              <div className={styles.leadLaneProgress}>
                <i style={{ width: `${Math.max(0, Math.min(100, lane.averageScore))}%` }} />
              </div>
              <div className={styles.leadLaneRecords}>
                {lane.records.slice(0, 3).map((record, recordIndex) => {
                  const recordId = resolveLeadRecordId(record, filteredLeads.indexOf(record));

                  return (
                  <button
                    key={recordId || `lane-${lane.id}-${recordIndex}`}
                    type="button"
                    onClick={() => setSelectedLeadId(recordId)}
                  >
                    <span>{resolveLeadValue(record, 'name')}</span>
                    <b>{resolveLeadPriorityScore(record)}</b>
                  </button>
                  );
                })}
                {!lane.records.length ? <span>{lane.action}</span> : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  /**
   * @function renderLeadActionDock
   * @description Renders selected-lead actions and source channel posture.
   * @returns {JSX.Element} Lead action dock.
   * @collaboration Makes the lead surface operate with mail, phone, calendar, proof and command actions.
   */
  function renderLeadActionDock() {
    const priorityScore = selectedLead ? resolveLeadPriorityScore(selectedLead) : 0;
    const priorityBand = resolveLeadPriorityBand(priorityScore);
    const emailHref = selectedLead ? resolveLeadContactHref(selectedLead, 'email') : null;
    const phoneHref = selectedLead ? resolveLeadContactHref(selectedLead, 'phone') : null;

    return (
      <aside className={styles.leadActionDock} data-wilsy-lead-action-dock="selected-record">
        <header className={styles.leadPanelHeader}>
          <span>
            <small>Action Dock</small>
            <strong>{selectedLead ? priorityBand : 'Activation'}</strong>
          </span>
          <b>{selectedLead ? priorityScore : 0}</b>
        </header>

        {selectedLead ? (
          <section className={styles.leadSelectedCard}>
            <span className={styles.leadSelectedSeal}>
              <Fingerprint size={25} />
            </span>
            <strong>{resolveLeadValue(selectedLead, 'name')}</strong>
            <em>{resolveLeadValue(selectedLead, 'company')}</em>
            <p>{resolveLeadSource(selectedLead)} · {resolveLeadStage(selectedLead)} · {getComplianceStatus(selectedLead)}</p>
            <code title={getProvenanceHash(selectedLead)}>{getProvenanceHash(selectedLead).slice(0, 18)}</code>

            <div className={styles.leadQuickActions}>
              <a
                href={phoneHref || undefined}
                className={!phoneHref ? styles.leadActionLinkDisabled : styles.leadActionLink}
                onClick={event => { if (!phoneHref) event.preventDefault(); }}
              >
                <Phone size={15} />
                Call
              </a>
              <a
                href={emailHref || undefined}
                className={!emailHref ? styles.leadActionLinkDisabled : styles.leadActionLink}
                onClick={event => { if (!emailHref) event.preventDefault(); }}
              >
                <Mail size={15} />
                Email
              </a>
              <button type="button" onClick={() => setCalendarOpen(true)}>
                <CalendarDays size={15} />
                Meet
              </button>
              <button type="button" onClick={() => setCommandOpen(true)}>
                <ShieldCheck size={15} />
                Proof
              </button>
            </div>
          </section>
        ) : (
          <section className={styles.leadSelectedEmpty}>
            <Sparkles size={28} />
            <strong>Lead OS ready</strong>
            <p>Source rows unlock selected-lead actions, proof trail, call/email shortcuts and Wilsy AI recommendations.</p>
          </section>
        )}

        <section className={styles.leadSourceChannels}>
          <header>
            <small>Source Channels</small>
            <strong>{sourceChannels.length || 0}</strong>
          </header>
          {sourceChannels.length ? sourceChannels.slice(0, 7).map(channel => (
            <span key={channel.id} data-connected={channel.connected ? 'true' : 'false'}>
              <Database size={14} />
              <em>{channel.label}</em>
              <b>{channel.count}</b>
            </span>
          )) : (
            <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
              <RotateCw size={15} />
              Initialize source registry
            </button>
          )}
        </section>
      </aside>
    );
  }

  /**
   * @function renderLeadFilterRail
   * @description Renders a Zoho-inspired filter rail with Wilsy proof filters.
   * @returns {JSX.Element|null} Lead filter rail.
   * @collaboration Keeps filters organized beside the records table instead of scattering cards down the page.
   */
  function renderLeadFilterRail() {
    if (!filterPanelOpen) return null;

    const normalizedFilterQuery = leadFilterQuery.trim().toLowerCase();
    const visibleFilterSections = LEAD_FILTER_OPERATING_SECTIONS
      .map(section => ({
        ...section,
        options: section.options.filter(option => {
          const searchable = [section.title, option.label, option.detail].join(' ').toLowerCase();

          return !normalizedFilterQuery || searchable.includes(normalizedFilterQuery);
        })
      }))
      .filter(section => section.options.length > 0);
    const selectedFilterCount = selectedLeadFilterOptions.size;

    return (
      <aside
        className={styles.leadFilterRail}
        data-wilsy-lead-filter-operating-system="R80A-INDEPENDENT-SCROLL"
        aria-label="Lead filters"
      >
        <header className={styles.leadFilterRailHeader}>
          <span>
            <small>Filter Leads by</small>
            <strong>Operating criteria</strong>
          </span>
          <button
            type="button"
            aria-label="Collapse Lead filters"
            onClick={() => setFilterPanelOpen(false)}
          >
            ‹‹
          </button>
        </header>

        <label className={styles.leadFilterSearch}>
          <Search size={18} aria-hidden="true" />
          <input
            value={leadFilterQuery}
            onChange={event => setLeadFilterQuery(event.target.value)}
            placeholder="Search filters..."
            aria-label="Search Lead filters"
          />
        </label>

        <div className={styles.leadFilterRailMeta} aria-live="polite">
          <strong>{selectedFilterCount}</strong>
          <span>{selectedFilterCount === 1 ? 'filter selected' : 'filters selected'}</span>
        </div>

        <div className={styles.leadFilterScroll} data-wilsy-independent-scroll="lead-filter-options">
          {visibleFilterSections.length ? visibleFilterSections.map(section => (
            <section key={section.id} className={styles.leadFilterSection}>
              <header className={styles.leadFilterSectionHeader}>
                <span aria-hidden="true">▾</span>
                <strong>{section.title}</strong>
              </header>

              <div className={styles.leadFilterOptionStack}>
                {section.options.map(option => (
                  <button
                    key={option.id}
                    type="button"
                    className={styles.leadFilterOption}
                    data-selected={selectedLeadFilterOptions.has(option.id) ? 'true' : 'false'}
                    onClick={() => setSelectedLeadFilterOptions(previous => {
                      const nextSelection = new Set(previous);

                      if (nextSelection.has(option.id)) {
                        nextSelection.delete(option.id);
                      } else {
                        nextSelection.add(option.id);
                      }

                      return nextSelection;
                    })}
                  >
                    <span aria-hidden="true" />
                    <em>{option.label}</em>
                  </button>
                ))}
              </div>
            </section>
          )) : (
            <section className={styles.leadFilterEmptyState}>
              <strong>No matching filters</strong>
              <em>Try a field, module, owner, status or activity term.</em>
            </section>
          )}
        </div>
      </aside>
    );
  }

  /**
   * @function renderLeadRecordsTable
   * @description Renders the records-first Lead module grid with row and mass actions.
   * @returns {JSX.Element} Lead records workspace.
   * @collaboration Replaces the continuous card runway with an operating CRM list view.
   */
  function renderLeadRecordsTable() {
    const visibleIds = filteredLeads.map((record, index) => resolveLeadRecordId(record, index));
    const allRowsSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));
    const activeSort = LEAD_SORT_OPTIONS.find(option => option.id === sortMode) || LEAD_SORT_OPTIONS[0];

    return (
      <section className={styles.leadRecordsWorkspace} data-wilsy-lead-records="tabbed-list-view">
        {renderLeadFilterRail()}

        <section className={styles.leadRecordsPanel}>
          <header className={styles.leadRecordsHeader}>
            <span>
              <small>{activeListView.label}</small>
              <strong>{filteredLeads.length} records</strong>
              <em>{selectedRowIds.length ? `${selectedRowIds.length} selected` : `${activeSort.label} order`}</em>
            </span>

            <div>
              <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
                <RotateCw size={15} />
                Refresh
              </button>
              <button type="button" disabled={!canUseLeadAction(role, 'export')}>
                <Download size={15} />
                Export
              </button>
            </div>
          </header>

          {selectedRowIds.length ? (
            <section className={styles.leadBulkActionBar} aria-label="Lead mass actions">
              <strong>{selectedRowIds.length} selected</strong>
              <button type="button"><Mail size={14} />Mass Email</button>
              <button type="button"><ClipboardList size={14} />Mass Update</button>
              <button type="button"><UserRoundCog size={14} />Change Owner</button>
              <button type="button" onClick={() => setSelectedRowIds([])}>Clear</button>
            </section>
          ) : null}

          <div className={styles.leadRecordsTableFrame}>
            <table className={styles.leadRecordsTable}>
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      aria-label="Select all visible leads"
                      checked={allRowsSelected}
                      onChange={handleToggleAllLeadSelection}
                    />
                  </th>
                  <th>Lead Name</th>
                  <th>Company</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Lead Source</th>
                  <th>Score</th>
                  <th>Compliance</th>
                  <th>Owner</th>
                  <th aria-label="Row actions" />
                </tr>
              </thead>
              <tbody>
                {filteredLeads.length ? filteredLeads.map((record, index) => {
                  const recordId = resolveLeadRecordId(record, index);
                  const complianceStatus = getComplianceStatus(record);
                  const priorityScore = resolveLeadPriorityScore(record);
                  const emailHref = resolveLeadContactHref(record, 'email');
                  const phoneHref = resolveLeadContactHref(record, 'phone');

                  return (
                    <tr key={recordId} data-selected={selectedRowIds.includes(recordId) ? 'true' : 'false'}>
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Select ${resolveLeadValue(record, 'name')}`}
                          checked={selectedRowIds.includes(recordId)}
                          onChange={() => handleToggleLeadSelection(recordId)}
                        />
                      </td>
                      <td>
                        <button type="button" className={styles.leadNameCell} onClick={() => setSelectedLeadId(recordId)}>
                          <strong>{resolveLeadValue(record, 'name')}</strong>
                          <em>{resolveLeadStage(record)}</em>
                        </button>
                      </td>
                      <td>{resolveLeadValue(record, 'company')}</td>
                      <td>
                        {emailHref ? <a href={emailHref}>{resolveLeadValue(record, 'email')}</a> : resolveLeadValue(record, 'email')}
                      </td>
                      <td>
                        {phoneHref ? <a href={phoneHref}>{resolveLeadValue(record, 'phone')}</a> : resolveLeadValue(record, 'phone')}
                      </td>
                      <td>{resolveLeadSource(record)}</td>
                      <td>
                        <span className={styles.leadScorePill}>{resolveLeadPriorityBand(priorityScore)} · {priorityScore}</span>
                      </td>
                      <td>
                        <span className={styles[`status${complianceStatus}`] || styles.statusPENDING}>
                          {complianceStatus}
                        </span>
                      </td>
                      <td>{resolveLeadValue(record, 'owner')}</td>
                      <td className={styles.leadRowActionsCell}>
                        <button type="button" onClick={() => setOpenRowActionId(openRowActionId === recordId ? '' : recordId)} title="Record actions">
                          <MoreHorizontal size={17} />
                        </button>
                        {openRowActionId === recordId ? (
                          <section className={styles.leadRowActionMenu} aria-label="Record actions">
                            <button type="button" onClick={() => setMode('create')}>Edit Record</button>
                            <a href={emailHref || undefined} onClick={(event) => { if (!emailHref) event.preventDefault(); }}>Send Email</a>
                            <button type="button" onClick={() => setCalendarOpen(true)}>Create Task</button>
                            <button type="button" onClick={() => setCommandOpen(true)}>Add Tags</button>
                            <button type="button" onClick={() => setCommandOpen(true)}>Change Owner</button>
                            <button type="button" onClick={() => setCommandOpen(true)}>Convert Lead</button>
                            <button type="button" onClick={() => setSelectedLeadId(recordId)}>Proof Trail</button>
                          </section>
                        ) : null}
                      </td>
                    </tr>
                  );
                }) : (
                  <tr className={styles.leadEmptyRow}>
                    <td colSpan={10}>
                      <section>
                        <Database size={28} />
                        <span>
                          <strong>No live lead records in this view yet.</strong>
                          <em>Sync source routes, import verified records, or create a validated lead. WILSY OS will surface the evidence trail as soon as records arrive.</em>
                        </span>
                        <div>
                          <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
                            <RotateCw size={15} />
                            Sync Sources
                          </button>
                          <button type="button" onClick={() => setMode('create')} disabled={!canUseLeadAction(role, 'create')}>
                            <Plus size={15} />
                            Create Lead
                          </button>
                        </div>
                      </section>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <footer className={styles.leadRecordsFooter}>
            <span>Live Records  {filteredLeads.length}</span>
            <strong>{filteredLeads.length ? `1 to ${filteredLeads.length}` : '0 to 0'}</strong>
          </footer>
        </section>
      </section>
    );
  }

  /**
   * @function renderLeadSignalsTab
   * @description Renders priority, action and metric signals behind the Signals tab.
   * @returns {JSX.Element} Signals tab.
   * @collaboration Moves operating cards behind an intentional tab instead of forcing them into the first scroll.
   */
  function renderLeadSignalsTab() {
    return (
      <section className={styles.leadTabSurface} data-lead-tab="signals">
        {renderLeadOsMetricDeck()}
        <section className={styles.leadSignalGrid}>
          {renderLeadQueue()}
          {renderLeadActionDock()}
        </section>
      </section>
    );
  }

  /**
   * @function renderLeadPipelineTab
   * @description Renders buyer journey lanes behind the Pipeline tab.
   * @returns {JSX.Element} Pipeline tab.
   * @collaboration Preserves pipeline intelligence without making Records compete with it.
   */
  function renderLeadPipelineTab() {
    return (
      <section className={styles.leadTabSurface} data-lead-tab="pipeline">
        {renderLeadJourneyBoard()}
      </section>
    );
  }

  /**
   * @function renderLeadProofTab
   * @description Renders compliance telemetry and ledger proof behind the Proof tab.
   * @returns {JSX.Element} Proof tab.
   * @collaboration Keeps audit posture powerful but intentionally organized.
   */
  function renderLeadProofTab() {
    return (
      <section className={styles.leadTabSurface} data-lead-tab="proof">
        <section className={styles.leadProofGrid}>
          {renderPipelineTelemetry()}
          {renderComplianceTabs()}
          <section className={styles.leadProofLedger}>
            {renderLedger()}
          </section>
        </section>
      </section>
    );
  }

  /**
   * @function renderLeadSourcesTab
   * @description Renders source ingestion and channel status behind the Sources tab.
   * @returns {JSX.Element} Sources tab.
   * @collaboration Separates ingestion setup from daily record work while keeping it one click away.
   */
  function renderLeadSourcesTab() {
    return (
      <section className={styles.leadTabSurface} data-lead-tab="sources">
        <section className={styles.leadSourcesGrid}>
          {renderSourceRoutes()}
          <aside className={styles.leadSourceMatrix}>
            <header>
              <small>Source Channels</small>
              <strong>{sourceChannels.length || 0}</strong>
            </header>
            {sourceChannels.length ? sourceChannels.map(channel => (
              <span key={channel.id} data-connected={channel.connected ? 'true' : 'false'}>
                <Database size={15} />
                <em>{channel.label}</em>
                <b>{channel.count}</b>
              </span>
            )) : (
              <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
                <RotateCw size={15} />
                Initialize source registry
              </button>
            )}
          </aside>
        </section>
      </section>
    );
  }

  /**
   * @function renderLeadTabContent
   * @description Resolves the active Lead top tab content.
   * @returns {JSX.Element} Active tab content.
   * @collaboration Makes the Leads module organized like an enterprise CRM operating system.
   */
  function renderLeadTabContent() {
    if (activeTopTab === 'signals') return renderLeadSignalsTab();
    if (activeTopTab === 'pipeline') return renderLeadPipelineTab();
    if (activeTopTab === 'proof') return renderLeadProofTab();
    if (activeTopTab === 'sources') return renderLeadSourcesTab();

    return renderLeadRecordsTable();
  }

  /**
   * @function renderLeadTabbedWorkspace
   * @description Renders the tabbed Lead module workspace.
   * @returns {JSX.Element} Tabbed Lead workspace.
   * @collaboration Replaces the earlier continuous OS canvas with a records-first module shell.
   */
  function renderLeadTabbedWorkspace() {
    return (
      <section
        className={styles.leadTabbedShell}
        data-wilsy-lead-os-canvas={WILSY_LEAD_TABBED_APP_BAR_VERSION}
        data-wilsy-lead-split-view={splitView ? 'true' : 'false'}
      >
        {renderLeadTabContent()}
      </section>
    );
  }

  /**
   * @function renderLeadOperatingCanvas
   * @description Renders the unified Lead OS command canvas.
   * @returns {JSX.Element} Lead operating canvas.
   * @collaboration Replaces the previous stacked report layout with OS-grade command posture.
   */
  function renderLeadOperatingCanvas() {
    return (
      <section
        className={styles.leadOsCanvas}
        data-wilsy-lead-os-canvas={WILSY_LEAD_OS_CANVAS_VERSION}
        data-wilsy-lead-split-view={splitView ? 'true' : 'false'}
      >
        {renderLeadOsMetricDeck()}

        <section className={styles.leadOsWorkgrid}>
          {renderLeadQueue()}
          {renderLeadJourneyBoard()}
          {renderLeadActionDock()}
        </section>

        <section className={styles.leadOsProofRail}>
          {renderComplianceTabs()}
          {renderSourceRoutes()}
        </section>

        {renderLedger()}
      </section>
    );
  }

  /**
   * @function renderPipelineTelemetry
   * @description Renders high-density pipeline telemetry.
   * @returns {JSX.Element} Telemetry panel.
   * @collaboration Moves counters into a compact scannable column.
   */
  function renderPipelineTelemetry() {
    const rows = [
      { label: 'Total Ingested', value: complianceMetrics.total, posture: sourcePosture },
      { label: 'Compliance Passed', value: complianceMetrics.verified, posture: 'VERIFIED' },
      { label: 'Audit Pending', value: complianceMetrics.pending, posture: 'PENDING' },
      { label: 'Failed Gates', value: complianceMetrics.failed, posture: 'FAILED' },
      { label: 'Source Routes', value: totalSources ? `${liveSources}/${totalSources}` : '—', posture: 'UPLINK' },
      { label: 'Root Hash', value: String(rootHash).slice(0, 12), posture: 'PROVENANCE' }
    ];

    return (
      <section className={styles.telemetryPanel} data-wilsy-telemetry-panel="dense">
        <h3>Pipeline Telemetry</h3>
        {rows.map(row => (
          <article key={row.label}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
            <em>{row.posture}</em>
          </article>
        ))}
      </section>
    );
  }

  /**
   * @function renderSourceRoutes
   * @description Renders source ingestion routes.
   * @returns {JSX.Element} Source route panel.
   * @collaboration Turns empty state into source activation instead of dead space.
   */
  function renderSourceRoutes() {
    return (
      <section className={styles.sourcePanel}>
        <h3>Source Ingestion Routes</h3>

        {routeRegistry.length ? routeRegistry.map(route => (
          <button key={route.key} type="button" className={route.connected ? styles.routeLive : styles.routeGap}>
            <span>{route.key}</span>
            <strong>{route.count ?? 0}</strong>
          </button>
        )) : (
          <div className={styles.routeEmpty}>
            <Database size={22} />
            <strong>No upstream telemetry sealed.</strong>
            <p>Attach authentic source routes to seal the provenance ledger.</p>
            <button type="button" onClick={handleSourceSync}>Initialize Upstream Channels</button>
          </div>
        )}
      </section>
    );
  }

  /**
   * @function renderComplianceTabs
   * @description Renders compact compliance filter tabs.
   * @returns {JSX.Element} Compliance tabs.
   * @collaboration Lets operators isolate verified, pending and failed records.
   */
  function renderComplianceTabs() {
    const counts = {
      ALL: complianceMetrics.total,
      VERIFIED: complianceMetrics.verified,
      PENDING: complianceMetrics.pending,
      FAILED: complianceMetrics.failed
    };

    return (
      <section className={styles.complianceTabs}>
        {LEAD_VIEWS.map(view => (
          <button
            key={view}
            type="button"
            className={activeFilter === view ? styles.complianceTabActive : styles.complianceTab}
            onClick={() => setActiveFilter(view)}
          >
            {view}<span>{counts[view]}</span>
          </button>
        ))}
      </section>
    );
  }


  /**
   * @function renderEmptyActivationBoard
   * @description Renders a sovereign activation board when the Lead ledger has no records.
   * @returns {JSX.Element} Empty ledger activation board.
   * @collaboration Converts empty data into useful operator actions without fabricating rows.
   */
  function renderEmptyActivationBoard() {
    const routeLabel = totalSources ? `${liveSources}/${totalSources}` : 'AWAITING SYNC';
    const rootLabel = String(rootHash || 'UNSEALED').slice(0, 12);

    return (
      <section
        className={styles.emptyActivationBoard}
        data-wilsy-empty-activation-board="R67D-SOVEREIGN-HEADER-COMMAND-BRIDGE"
      >
        <header className={styles.activationHero}>
          <span>
            <Fingerprint size={38} />
          </span>
          <div>
            <small>Sovereign Ledger Activation</small>
            <strong>No Backend Lead Rows Returned.</strong>
            <p>
              The ledger is empty because Wilsy OS refuses to fake records. Activate a verified
              upstream channel, import real source data, or create a validated lead to seal the first row.
            </p>
          </div>
          <em>{tenantId} · {role}</em>
        </header>

        <section className={styles.activationGrid}>
          <article className={styles.activationCard}>
            <Database size={22} />
            <small>Source Routes</small>
            <strong>{routeLabel}</strong>
            <p>Initialize CRM, email, webform, partner, import and governance channels.</p>
            <button type="button" onClick={handleSourceSync}>Initialize Upstream Channels</button>
          </article>

          <article className={styles.activationCard}>
            <ShieldCheck size={22} />
            <small>Root Seal</small>
            <strong>{rootLabel}</strong>
            <p>Every accepted lead must produce a provenance hash and auditable source posture.</p>
            <button type="button" onClick={handleSourceSync}>Refresh Seal Telemetry</button>
          </article>

          <article className={styles.activationCard}>
            <Upload size={22} />
            <small>Import Dock</small>
            <strong>CSV / Notes / Evidence</strong>
            <p>Prepare real source ingestion without allowing decorative sample rows.</p>
            <button type="button" disabled={!canUseLeadAction(role, 'import')}>Open Import Queue</button>
          </article>

          <article className={styles.activationCard}>
            <WandSparkles size={22} />
            <small>Wilsy AI</small>
            <strong>Enrichment Ready</strong>
            <p>Score, enrich, deduplicate and draft outreach after a real lead is present.</p>
            <button type="button">Prepare AI Enrichment</button>
          </article>

          <article className={styles.activationCard}>
            <ClipboardList size={22} />
            <small>Compliance Matrix</small>
            <strong>POPIA · GDPR · SOC2</strong>
            <p>Bind consent, source basis, retention posture and audit events to every lead.</p>
            <button type="button" onClick={() => setCommandOpen(true)}>Open Command Center</button>
          </article>

          <article className={styles.activationCardPrimary}>
            <Plus size={22} />
            <small>Verified Create</small>
            <strong>Create the first real Lead</strong>
            <p>Lead name, company and email are required before backend creation activates.</p>
            <button type="button" onClick={() => setMode('create')}>Create Verified Lead</button>
          </article>
        </section>

        <footer className={styles.activationFooter}>
          <span>No synthetic rows</span>
          <span>Backend authority only</span>
          <span>Provenance hash required</span>
          <span>Compliance binding required</span>
        </footer>
      </section>
    );
  }


  /**
   * @function renderLedger
   * @description Renders the Data Provenance Ledger without leaving dead space when empty.
   * @returns {JSX.Element} Ledger.
   * @collaboration Keeps provenance dominant while turning empty state into a responsive activation board.
   */
  function renderLedger() {
    const hasRows = filteredLeads.length > 0;

    return (
      <section
        className={styles.ledgerPanel}
        data-wilsy-ledger-state={hasRows ? 'populated' : 'empty'}
      >
        <header>
          <span>
            <small>Data Provenance Ledger</small>
            <strong>All Leads</strong>
          </span>
          <div>
            <button type="button" onClick={handleSourceSync} disabled={isSyncing}>
              <CheckCircle2 size={16} />
              {isSyncing ? 'Syncing' : 'Sync'}
            </button>
            <button type="button" disabled={!canUseLeadAction(role, 'export')}>
              <Download size={16} />
              Export
            </button>
          </div>
        </header>

        {hasRows ? (
          <div className={styles.tableFrame}>
            <table>
              <thead>
                <tr>
                  <th><input type="checkbox" aria-label="Select all leads" /></th>
                  {LEAD_COLUMNS.map(column => <th key={column.key}>{column.label}</th>)}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLeads.map((record, index) => (
                  <tr key={record._id || record.id || `lead-record-${index}`}>
                    <td><input type="checkbox" aria-label={`Select lead ${index + 1}`} /></td>
                    {LEAD_COLUMNS.map(column => (
                      <td key={column.key}>
                        {column.key === 'complianceStatus' ? (
                          <span className={styles[`status${resolveLeadValue(record, column.key)}`] || styles.statusPENDING}>
                            {resolveLeadValue(record, column.key)}
                          </span>
                        ) : column.key === 'provenanceHash' ? (
                          <code title={resolveLeadValue(record, column.key)}>
                            {resolveLeadValue(record, column.key).slice(0, 18)}
                          </code>
                        ) : resolveLeadValue(record, column.key)}
                      </td>
                    ))}
                    <td><button type="button">Manage</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.ledgerEmptyFrame}>
            {renderEmptyActivationBoard()}
          </div>
        )}
      </section>
    );
  }

  /**
   * @function renderListMode
   * @description Renders the high-density Lead command canvas.
   * @returns {JSX.Element} List mode.
   * @collaboration Replaces button flood with telemetry, source routes and provenance ledger.
   */
  function renderListMode() {
    return renderLeadTabbedWorkspace();
  }

  /**
   * @function renderCreateMode
   * @description Renders the focused Create Lead surface.
   * @returns {JSX.Element} Create Lead surface.
   * @collaboration Captures verified lead payloads for backend command fabric.
   */
  function renderCreateMode() {
    return (
      <section className={styles.createSurface}>
        <header className={styles.createHeader}>
          <span><small>Focused Create</small><strong>Create Verified Lead</strong><em>Capture, enrich, schedule and prove the Lead source from one workspace.</em></span>
          <div>
            <button type="button" onClick={() => setMode('list')}>Cancel</button>
            <button type="button" disabled={!canUseLeadAction(role, 'create')} onClick={() => handleSaveLead(true)}>Save and New</button>
            <button type="button" className={styles.saveButton} disabled={!canUseLeadAction(role, 'create')} onClick={() => handleSaveLead(false)}>Save</button>
          </div>
        </header>

        <main className={styles.createGrid}>
          <section className={styles.formPanel}>
            <h3>Lead Information</h3>
            <div className={styles.formGrid}>
              <label><span>Lead Name *</span><input value={draft.name} onChange={event => updateDraftField('name', event.target.value)} /></label>
              <label><span>Company *</span><input value={draft.company} onChange={event => updateDraftField('company', event.target.value)} /></label>
              <label><span>Email *</span><input value={draft.email} onChange={event => updateDraftField('email', event.target.value)} /></label>
              <label><span>Phone</span><input value={draft.phone} onChange={event => updateDraftField('phone', event.target.value)} /></label>
              <label><span>Mobile</span><input value={draft.mobile} onChange={event => updateDraftField('mobile', event.target.value)} /></label>
              <label><span>Title</span><input value={draft.title} onChange={event => updateDraftField('title', event.target.value)} /></label>
              <label><span>Lead Source</span><select value={draft.source} onChange={event => updateDraftField('source', event.target.value)}><option>Website</option><option>Referral</option><option>Partner</option><option>Outbound</option><option>Event</option><option>Wilsy AI</option></select></label>
              <label><span>Status</span><select value={draft.status} onChange={event => updateDraftField('status', event.target.value)}><option>NEW</option><option>OPEN</option><option>CONTACTED</option><option>QUALIFIED</option><option>DISQUALIFIED</option></select></label>
              <label><span>Industry</span><input value={draft.industry} onChange={event => updateDraftField('industry', event.target.value)} /></label>
              <label><span>Owner</span><input value={draft.owner} onChange={event => updateDraftField('owner', event.target.value)} /></label>
              <label><span>Website</span><input value={draft.website} onChange={event => updateDraftField('website', event.target.value)} /></label>
              <label><span>Employees</span><input value={draft.employees} onChange={event => updateDraftField('employees', event.target.value)} /></label>
            </div>

            <h3>Address Information</h3>
            <div className={styles.formGrid}>
              <label className={styles.wideField}><span>Street</span><input value={draft.street} onChange={event => updateDraftField('street', event.target.value)} /></label>
              <label><span>City</span><input value={draft.city} onChange={event => updateDraftField('city', event.target.value)} /></label>
              <label><span>State</span><input value={draft.state} onChange={event => updateDraftField('state', event.target.value)} /></label>
              <label><span>Zip Code</span><input value={draft.zipCode} onChange={event => updateDraftField('zipCode', event.target.value)} /></label>
              <label><span>Country</span><input value={draft.country} onChange={event => updateDraftField('country', event.target.value)} /></label>
            </div>

            <h3>Description Information</h3>
            <label className={styles.descriptionField}><span>Description / Notes</span><textarea value={draft.description} onChange={event => updateDraftField('description', event.target.value)} /></label>
          </section>

          <aside className={styles.createCommandPanel}>
            <section><ShieldCheck size={23} /><strong>Source posture</strong><p>Backend create activates only after required fields are valid. Browser does not manufacture Lead authority.</p><span>{saveStatus || 'Awaiting validated Lead payload.'}</span></section>
            <section><CalendarDays size={23} /><strong>Activity shortcuts</strong><button type="button" onClick={() => setCalendarOpen(true)}><CalendarDays size={16} />Create meeting</button><button type="button" onClick={() => setCalendarOpen(true)}><Phone size={16} />Create call</button><button type="button" onClick={() => setCalendarOpen(true)}><Activity size={16} />Mark unavailable</button></section>
            <section><Sparkles size={23} /><strong>Wilsy AI services</strong><button type="button"><WandSparkles size={16} />Enrich Lead</button><button type="button"><Mail size={16} />Draft outreach</button><button type="button"><ClipboardList size={16} />Score readiness</button></section>
          </aside>
        </main>
      </section>
    );
  }

  /**
   * @function renderCalendarDrawer
   * @description Renders the Lead calendar drawer.
   * @returns {JSX.Element|null} Calendar drawer.
   * @collaboration Gives Leads call, meeting and unavailable planning.
   */
  function renderCalendarDrawer() {
    if (!calendarOpen) return null;

    return (
      <section className={styles.drawer} aria-label="Lead calendar workspace">
        <header><span><small>Calendar</small><strong>Lead Activity Month</strong></span><button type="button" onClick={() => setCalendarOpen(false)}>Close</button></header>
        <nav><button type="button">Meeting</button><button type="button">Call</button><button type="button">Mark As Unavailable</button></nav>
        <div className={styles.calendarGrid}>{buildCalendarDays().map(day => <button key={day} type="button"><strong>{day <= 31 ? day : ''}</strong>{day % 7 === 0 ? <span>Call</span> : null}{day % 11 === 0 ? <em>Meeting</em> : null}</button>)}</div>
      </section>
    );
  }

  /**
   * @function renderCommandDrawer
   * @description Renders tenant and subscription command drawer.
   * @returns {JSX.Element|null} Command drawer.
   * @collaboration Surfaces Master and tenant administration controls.
   */
  function renderCommandDrawer() {
    if (!commandOpen) return null;

    const isMaster = ['MASTER', 'FOUNDER', 'SUPER_ADMIN', 'ROOT'].includes(role);
    const isAdmin = isMaster || ['TENANT_ADMIN', 'ADMIN', 'CRM_ADMIN'].includes(role);

    return (
      <section className={styles.drawer} aria-label="Lead command center">
        <header><span><small>Command Center</small><strong>{tenantId} · {role}</strong></span><button type="button" onClick={() => setCommandOpen(false)}>Close</button></header>
        <div className={styles.commandTiles}>
          {isMaster ? <button type="button"><UserRoundCog size={18} />Manage Organizations</button> : null}
          {isMaster ? <button type="button"><LayoutPanelTop size={18} />Tenant Activities</button> : null}
          {isAdmin ? <button type="button"><ShieldCheck size={18} />Manage Subscription</button> : null}
          {isAdmin ? <button type="button"><Sparkles size={18} />Upgrade Tier</button> : null}
          <button type="button"><WandSparkles size={18} />Wilsy AI Services</button>
          <button type="button"><ClipboardList size={18} />Sales Shortcuts</button>
        </div>
      </section>
    );
  }

  /**
   * @function renderSetupDrawer
   * @description Renders CRM setup drawer.
   * @returns {JSX.Element|null} Setup drawer.
   * @collaboration Groups operating controls into enterprise setup domains.
   */
  function renderSetupDrawer() {
    if (!setupOpen) return null;

    const groups = [
      { title: 'General', items: ['Personal Settings', 'Users', 'Company Settings'] },
      { title: 'Security Control', items: ['Profiles', 'Roles and Sharing', 'Compliance Settings'] },
      { title: 'Customization', items: ['Modules and Fields', 'Lead Layouts', 'Workflow Rules'] },
      { title: 'Data Administration', items: ['Import', 'Export', 'Data Backup'] },
      { title: 'Developer Hub', items: ['APIs and SDKs', 'Extensions', 'Catalyst Solutions'] }
    ];

    return (
      <section className={styles.drawerWide} aria-label="Lead setup workspace">
        <header><span><small>Setup</small><strong>CRM Operating Controls</strong></span><button type="button" onClick={() => setSetupOpen(false)}>Close</button></header>
        <div className={styles.setupGrid}>{groups.map(group => <article key={group.title}><strong>{group.title}</strong>{group.items.map(item => <button key={item} type="button">{item}</button>)}</article>)}</div>
      </section>
    );
  }

  return (
    <section
      className={[styles.leadOperatingRoom, activeLeadThemeOption?.className].filter(Boolean).join(' ')}
      style={activeLeadThemeOption?.cssVars || undefined}
      data-wilsy-lead-operating-room={WILSY_LEAD_OPERATING_ROOM_VERSION}
      data-wilsy-lead-header-bridge-version={WILSY_LEAD_HEADER_BRIDGE_VERSION}
      data-wilsy-lead-workspace-grade="R75C-SOVEREIGN-LEAD-WORKSPACE"
      data-wilsy-crm-visual-contract="R78B-UNIFIED-CRM-SHELL"
      data-wilsy-lead-skin={themeRuntime?.themeId || 'crm_revenue_pulse'}
      data-wilsy-theme-engine-source="global-command-center"
      data-wilsy-theme-bridge-version={WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION}
    >
      {renderHeader()}
      {mode === 'create' ? renderCreateMode() : renderListMode()}
      {renderCalendarDrawer()}
      {renderCommandDrawer()}
      {renderSetupDrawer()}
      {loading || isSyncing ? <div className={styles.loadingVeil}>Synchronising CRM sources...</div> : null}
    </section>
  );
}
