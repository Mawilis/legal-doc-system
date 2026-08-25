/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM CONTACT OPERATING ROOM [R86B-SECTION-MAPPED-BACKEND-COMMAND]                                                          ║
 * ║ [CONTACT SOURCE TRUTH | BACKEND CREATE COMMAND | CONSENT READINESS | ACCOUNT LINKAGE | ONE-SCREEN COMMAND VIEWPORT]                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: R86B-SECTION-MAPPED-BACKEND-COMMAND | PRODUCTION READY | SOURCE-BACKED CRM CONTACT MODULE                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/crm/contact/WilsyContactOperatingRoom.jsx                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated Contacts to graduate from prototype into a real-world, one-screen CRM command module.      ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Mapped every visible section, restored one-screen containment, and wired create/export        ║
 * ║   controls to backend CRM command routes while preserving live source truth.                                                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Building2,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Copy,
  Database,
  Download,
  FileCheck2,
  Filter,
  GitBranch,
  Mail,
  MoreHorizontal,
  Network,
  Plus,
  RefreshCcw,
  Search,
  Shield,
  SlidersHorizontal,
  Sparkles,
  UserRound,
  Users,
} from 'lucide-react';
import { wilsyCrmFetchJson } from '../../../services/wilsyCrmCommandClient.js';
import styles from './WilsyContactOperatingRoom.module.css';

const CONTACT_LIST_VIEWS = Object.freeze([
  { id: 'ALL_CONTACTS', label: 'All Contacts', detail: 'Every source-backed relationship' },
  { id: 'CONSENT_READY', label: 'Consent Ready', detail: 'Communication authority confirmed' },
  { id: 'ACCOUNT_LINKED', label: 'Account Linked', detail: 'Connected to business graph' },
  { id: 'ACTION_REQUIRED', label: 'Action Required', detail: 'Missing consent, account, or proof' },
]);

const CONTACT_TOP_TABS = Object.freeze([
  { id: 'records', label: 'Records', icon: Users },
  { id: 'relationships', label: 'Relationships', icon: GitBranch },
  { id: 'consent', label: 'Consent', icon: Shield },
  { id: 'sources', label: 'Sources', icon: Network },
]);

const CONTACT_SORT_OPTIONS = Object.freeze([
  { id: 'relationship', label: 'Relationship score' },
  { id: 'name', label: 'Contact name' },
  { id: 'account', label: 'Account name' },
  { id: 'activity', label: 'Latest activity' },
]);

const CONTACT_PAGE_SIZE_OPTIONS = Object.freeze([10, 25, 50, 100]);

const CONTACT_LEAD_SOURCE_OPTIONS = Object.freeze([
  '-None-',
  'Advertisement',
  'Cold Call',
  'Employee Referral',
  'External Referral',
  'Online Store',
  'Partner',
  'X (Twitter)',
  'Facebook',
  'Public Relations',
  'Sales Email Alias',
  'Seminar Partner',
  'Internal Seminar',
  'Trade Show',
  'Web Download',
  'Web Research',
  'Web Cases',
  'Web Mail',
  'Chat',
  'LinkedIn',
  'WhatsApp',
  'Referral Partner',
  'Customer Success',
  'Field Event',
  'Marketplace',
  'Website Form',
]);

const CONTACT_SALUTATION_OPTIONS = Object.freeze(['-None-', 'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Adv.', 'Hon.']);

const CONTACT_TITLE_OPTIONS = Object.freeze([
  '',
  'Chief Executive Officer',
  'Chief Revenue Officer',
  'Chief Financial Officer',
  'Chief Operating Officer',
  'Chief Technology Officer',
  'Founder',
  'Owner',
  'Managing Director',
  'Director',
  'Vice President Sales',
  'Head of Sales',
  'Head of Marketing',
  'Head of Legal',
  'Head of Operations',
  'Procurement Manager',
  'Customer Success Manager',
  'Account Manager',
  'Project Manager',
  'Legal Counsel',
  'Administrator',
  'Other'
]);

const CONTACT_DEPARTMENT_OPTIONS = Object.freeze([
  '',
  'Executive',
  'Revenue',
  'Sales',
  'Marketing',
  'Legal',
  'Finance',
  'Operations',
  'Procurement',
  'Information Technology',
  'Engineering',
  'Customer Success',
  'Support',
  'Human Resources',
  'Compliance',
  'Risk',
  'Administration',
  'Other'
]);

const CONTACT_PHONE_COUNTRY_OPTIONS = Object.freeze([
  { iso: 'ZA', country: 'South Africa', dialCode: '+27' },
  { iso: 'US', country: 'United States', dialCode: '+1' },
  { iso: 'GB', country: 'United Kingdom', dialCode: '+44' },
  { iso: 'NG', country: 'Nigeria', dialCode: '+234' },
  { iso: 'KE', country: 'Kenya', dialCode: '+254' },
  { iso: 'GH', country: 'Ghana', dialCode: '+233' },
  { iso: 'BW', country: 'Botswana', dialCode: '+267' },
  { iso: 'NA', country: 'Namibia', dialCode: '+264' },
  { iso: 'ZW', country: 'Zimbabwe', dialCode: '+263' },
  { iso: 'ZM', country: 'Zambia', dialCode: '+260' },
  { iso: 'MW', country: 'Malawi', dialCode: '+265' },
  { iso: 'MZ', country: 'Mozambique', dialCode: '+258' },
  { iso: 'IN', country: 'India', dialCode: '+91' },
  { iso: 'AE', country: 'United Arab Emirates', dialCode: '+971' },
  { iso: 'AU', country: 'Australia', dialCode: '+61' },
  { iso: 'CA', country: 'Canada', dialCode: '+1' },
  { iso: 'DE', country: 'Germany', dialCode: '+49' },
  { iso: 'FR', country: 'France', dialCode: '+33' },
  { iso: 'NL', country: 'Netherlands', dialCode: '+31' },
  { iso: 'SG', country: 'Singapore', dialCode: '+65' }
]);

const CONTACT_FILTER_GROUPS = Object.freeze([
  {
    id: 'system',
    label: 'System Defined Filters',
    options: Object.freeze([
      'Consent Ready',
      'Missing Email',
      'Account Linked',
      'Authority Pending',
      'Recently Touched',
      'Inactive Contacts',
    ]),
  },
  {
    id: 'relationship',
    label: 'Relationship Signals',
    options: Object.freeze([
      'Decision Makers',
      'Customer Success',
      'Deal Influencers',
      'Support Contacts',
      'Partner Contacts',
    ]),
  },
]);

const CONTACT_SIGNAL_FILTERS = Object.freeze({
  'Consent Ready': { id: 'CONSENT_READY', label: 'Consent Ready' },
  'Missing Email': { id: 'MISSING_EMAIL', label: 'Missing Email' },
  'Account Linked': { id: 'ACCOUNT_LINKED', label: 'Account Linked' },
  'Authority Pending': { id: 'AUTHORITY_PENDING', label: 'Authority Pending' },
  'Recently Touched': { id: 'RECENTLY_TOUCHED', label: 'Recently Touched' },
  'Inactive Contacts': { id: 'INACTIVE_CONTACTS', label: 'Inactive Contacts' },
  'Decision Makers': { id: 'DECISION_MAKERS', label: 'Decision Makers' },
  'Customer Success': { id: 'CUSTOMER_SUCCESS', label: 'Customer Success' },
  'Deal Influencers': { id: 'DEAL_INFLUENCERS', label: 'Deal Influencers' },
  'Support Contacts': { id: 'SUPPORT_CONTACTS', label: 'Support Contacts' },
  'Partner Contacts': { id: 'PARTNER_CONTACTS', label: 'Partner Contacts' },
});

/**
 * @function resolveContactId
 * @description Resolves a stable contact row id from flexible CRM contact payloads.
 * @param {Object} record - Contact record.
 * @param {number} index - Fallback index.
 * @returns {string} Stable contact id.
 * @collaboration R76C Contacts Operating Room, live CRM source records, row selection.
 */
function resolveContactId(record = {}, index = 0) {
  return String(record._id || record.id || record.uuid || record.recordId || record.contactId || record.email || `contact-${index}`);
}

/**
 * @function resolveContactValue
 * @description Resolves normalized contact field values from live CRM payloads.
 * @param {Object} record - Contact record.
 * @param {string} field - Field name.
 * @returns {string} Display value.
 * @collaboration R76C Contacts Operating Room, Zoho-coverage parity, source-flexible CRM data.
 */
function resolveContactValue(record = {}, field = '') {
  const values = {
    name: record.name || record.contactName || record.fullName || [record.firstName, record.lastName].filter(Boolean).join(' '),
    accountName: record.accountName || record.company || record.companyName || record.organization || record.account?.name,
    email: record.email || record.primaryEmail || record.contactEmail,
    phone: record.phone || record.mobile || record.mobileNumber || record.workPhone || record.telephone,
    title: record.title || record.jobTitle || record.role || record.designation,
    department: record.department || record.team || record.function,
    source: record.source || record.sourceSystem || record.connector || record.origin || record.channel,
    owner: record.owner || record.ownerName || record.assignedTo || record.createdBy,
    status: record.status || record.lifecycleStage || record.contactStatus,
    consentStatus: record.consentStatus || record.communicationConsent || record.popiaConsent || record.marketingConsent,
    lastActivity: record.lastActivity || record.lastContactedAt || record.lastTouchedAt || record.updatedAt || record.createdAt,
    provenanceHash: record.provenanceHash || record.cryptographicHash || record.rootHash || record.sealHash,
  };

  return String(values[field] || '—').trim() || '—';
}

/**
 * @function isKnownContactValue
 * @description Determines whether a contact value is meaningful.
 * @param {string} value - Candidate display value.
 * @returns {boolean} True when value is known.
 * @collaboration R76C data quality scoring, Contacts field intelligence, source proof posture.
 */
function isKnownContactValue(value = '') {
  const text = String(value || '').trim();
  return Boolean(text && text !== '—' && text !== 'UNSEALED' && text.toUpperCase() !== 'NONE');
}

/**
 * @function resolveContactStatus
 * @description Resolves operational contact status.
 * @param {Object} record - Contact record.
 * @returns {string} Status label.
 * @collaboration R76C relationship cockpit, contact status table, source-compatible CRM payloads.
 */
function resolveContactStatus(record = {}) {
  const raw = resolveContactValue(record, 'status').toUpperCase();

  if (raw.includes('ACTIVE') || raw.includes('CUSTOMER') || raw.includes('OPEN')) return 'ACTIVE';
  if (raw.includes('RISK') || raw.includes('ESCALATED')) return 'AT_RISK';
  if (raw.includes('INACTIVE') || raw.includes('LOST') || raw.includes('ARCHIVED')) return 'INACTIVE';

  return 'NEW';
}

/**
 * @function resolveContactConsent
 * @description Resolves contact communication and privacy consent posture.
 * @param {Object} record - Contact record.
 * @returns {string} Consent posture.
 * @collaboration R76C POPIA/GDPR consent posture, contact communications, compliance HUD.
 */
function resolveContactConsent(record = {}) {
  const raw = String(resolveContactValue(record, 'consentStatus')).toUpperCase();

  if (raw.includes('TRUE') || raw.includes('YES') || raw.includes('VERIFIED') || raw.includes('OPT_IN') || raw.includes('CONSENT')) return 'VERIFIED';
  if (raw.includes('FALSE') || raw.includes('NO') || raw.includes('OPT_OUT') || raw.includes('REVOKED')) return 'REVOKED';
  if (raw.includes('PENDING') || raw.includes('REVIEW')) return 'PENDING';

  return 'PENDING';
}

/**
 * @function resolveContactSource
 * @description Resolves the contact source label.
 * @param {Object} record - Contact record.
 * @returns {string} Source label.
 * @collaboration R76C source route proof, contact provenance, live CRM source registry.
 */
function resolveContactSource(record = {}) {
  return resolveContactValue(record, 'source') === '—' ? 'Backend CRM' : resolveContactValue(record, 'source');
}

/**
 * @function resolveContactScore
 * @description Calculates relationship readiness from consent, account linkage, communication fields and proof.
 * @param {Object} record - Contact record.
 * @returns {number} Relationship score.
 * @collaboration R76C relationship intelligence, contact prioritization, Wilsy OS proof scoring.
 */
function resolveContactScore(record = {}) {
  const consent = resolveContactConsent(record);
  const status = resolveContactStatus(record);
  const hasAccount = isKnownContactValue(resolveContactValue(record, 'accountName'));
  const hasEmail = isKnownContactValue(resolveContactValue(record, 'email'));
  const hasPhone = isKnownContactValue(resolveContactValue(record, 'phone'));
  const hasTitle = isKnownContactValue(resolveContactValue(record, 'title'));
  const hasProof = isKnownContactValue(resolveContactValue(record, 'provenanceHash'));

  const fieldScore = [hasAccount, hasEmail, hasPhone, hasTitle].filter(Boolean).length * 12;
  const consentScore = consent === 'VERIFIED' ? 22 : consent === 'PENDING' ? 8 : 0;
  const statusScore = status === 'ACTIVE' ? 14 : status === 'AT_RISK' ? 6 : status === 'INACTIVE' ? 0 : 8;
  const proofScore = hasProof ? 16 : 0;

  return Math.max(0, Math.min(100, fieldScore + consentScore + statusScore + proofScore));
}

/**
 * @function resolveContactBand
 * @description Converts contact score to an operator-facing readiness band.
 * @param {number} score - Contact relationship score.
 * @returns {string} Readiness band.
 * @collaboration R76C Contacts score pills, operator prioritization, CRM command cockpit.
 */
function resolveContactBand(score = 0) {
  if (score >= 78) return 'Command Ready';
  if (score >= 54) return 'Relationship Warm';
  if (score >= 28) return 'Needs Proof';
  return 'Unqualified';
}

/**
 * @function resolveContactHref
 * @description Builds safe contact action links.
 * @param {Object} record - Contact record.
 * @param {string} channel - Contact channel.
 * @returns {string|null} Contact href or null.
 * @collaboration R76C quick actions, contact outreach, browser-safe communication links.
 */
function resolveContactHref(record = {}, channel = 'email') {
  if (channel === 'email') {
    const email = resolveContactValue(record, 'email');
    return isKnownContactValue(email) ? `mailto:${email}` : null;
  }

  const phone = resolveContactValue(record, 'phone');
  const normalizedPhone = String(phone || '').replace(/[^\d+]/g, '');
  return isKnownContactValue(phone) && normalizedPhone ? `tel:${normalizedPhone}` : null;
}

/**
 * @function filterContactByView
 * @description Applies the active contact list view to a record.
 * @param {Object} record - Contact record.
 * @param {string} listViewId - Active view id.
 * @returns {boolean} True when record matches the view.
 * @collaboration R76C Contacts view rail, relationship operations, source-backed filtering.
 */
function filterContactByView(record = {}, listViewId = 'ALL_CONTACTS') {
  if (listViewId === 'CONSENT_READY') return resolveContactConsent(record) === 'VERIFIED';
  if (listViewId === 'ACCOUNT_LINKED') return isKnownContactValue(resolveContactValue(record, 'accountName'));
  if (listViewId === 'ACTION_REQUIRED') {
    return resolveContactConsent(record) !== 'VERIFIED'
      || !isKnownContactValue(resolveContactValue(record, 'accountName'))
      || !isKnownContactValue(resolveContactValue(record, 'email'));
  }

  return true;
}

/**
 * @function sortContactRecords
 * @description Sorts contact records for the active operator sort mode.
 * @param {Array<Object>} records - Contact records.
 * @param {string} sortMode - Sort mode.
 * @returns {Array<Object>} Sorted records.
 * @collaboration R76C Contacts sort deck, relationship cockpit, Zoho-grade list parity.
 */
function sortContactRecords(records = [], sortMode = 'relationship') {
  const sortedRecords = [...records];

  return sortedRecords.sort((leftRecord, rightRecord) => {
    if (sortMode === 'name') {
      return resolveContactValue(leftRecord, 'name').localeCompare(resolveContactValue(rightRecord, 'name'));
    }

    if (sortMode === 'account') {
      return resolveContactValue(leftRecord, 'accountName').localeCompare(resolveContactValue(rightRecord, 'accountName'));
    }

    if (sortMode === 'activity') {
      const leftDate = Date.parse(resolveContactValue(leftRecord, 'lastActivity')) || 0;
      const rightDate = Date.parse(resolveContactValue(rightRecord, 'lastActivity')) || 0;
      return rightDate - leftDate;
    }

    return resolveContactScore(rightRecord) - resolveContactScore(leftRecord);
  });
}

/**
 * @function buildContactMetrics
 * @description Builds Contacts operating metrics from live CRM records and source posture.
 * @param {Object} params - Metric inputs.
 * @returns {Array<Object>} Metric cards.
 * @collaboration R76C Contacts cockpit, source truth, relationship intelligence telemetry.
 */
function buildContactMetrics({
  contacts = [],
  accounts = [],
  deals = [],
  evidence = [],
  sourcePosture = {},
} = {}) {
  const consentReady = contacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length;
  const accountLinked = contacts.filter(record => isKnownContactValue(resolveContactValue(record, 'accountName'))).length;
  const relationshipReady = contacts.filter(record => resolveContactScore(record) >= 54).length;
  const connectedRoutes = Number(sourcePosture.connected || sourcePosture.connectedRoutes || 0);

  return [
    {
      id: 'contacts',
      label: 'Relationship Graph',
      value: String(contacts.length),
      detail: contacts.length ? 'Source-backed contacts available' : 'No contacts returned yet',
      progress: contacts.length ? Math.round((relationshipReady / Math.max(1, contacts.length)) * 100) : 0,
      icon: Users,
    },
    {
      id: 'consent',
      label: 'Consent Readiness',
      value: `${consentReady}/${contacts.length || 0}`,
      detail: 'Communication authority and privacy posture',
      progress: contacts.length ? Math.round((consentReady / Math.max(1, contacts.length)) * 100) : 0,
      icon: Shield,
    },
    {
      id: 'accounts',
      label: 'Account Linkage',
      value: `${accountLinked}/${contacts.length || 0}`,
      detail: `${accounts.length || 0} account records in current source snapshot`,
      progress: contacts.length ? Math.round((accountLinked / Math.max(1, contacts.length)) * 100) : 0,
      icon: Building2,
    },
    {
      id: 'proof',
      label: 'Proof Surface',
      value: String(evidence.length || deals.length || connectedRoutes),
      detail: evidence.length ? 'Evidence anchors available' : 'Awaiting sealed contact proof',
      progress: Math.min(100, Math.max(0, evidence.length * 12 + connectedRoutes * 8)),
      icon: FileCheck2,
    },
  ];
}

/**
 * @function buildContactPagination
 * @description Builds the Contacts list footer pagination model with exact record totals.
 * @param {number} totalRecords - Total filtered records.
 * @param {number} currentPage - Current page.
 * @param {number} pageSize - Current page size.
 * @returns {Object} Contacts pagination packet.
 * @collaboration R87C Contacts record footer, Zoho-grade total records posture, productivity viewport.
 */
function buildContactPagination(totalRecords = 0, currentPage = 1, pageSize = 10) {
  const safeTotal = Math.max(0, Number(totalRecords || 0));
  const safePageSize = Math.max(1, Number(pageSize || 10));
  const totalPages = Math.max(1, Math.ceil(safeTotal / safePageSize));
  const safePage = Math.min(Math.max(1, Number(currentPage || 1)), totalPages);
  const startIndex = safeTotal ? (safePage - 1) * safePageSize : 0;
  const endIndex = safeTotal ? Math.min(startIndex + safePageSize, safeTotal) : 0;

  return {
    currentPage: safePage,
    totalPages,
    pageSize: safePageSize,
    totalRecords: safeTotal,
    startIndex,
    endIndex,
    startRecord: safeTotal ? startIndex + 1 : 0,
    endRecord: endIndex,
    hasPrevious: safePage > 1,
    hasNext: safePage < totalPages,
  };
}

/**
 * @function resolveContactTouchAgeDays
 * @description Resolves how many days have passed since the contact was last touched.
 * @param {Object} record - Contact record.
 * @returns {number} Age in days or Infinity when no activity date exists.
 * @collaboration R86A real-world contact freshness, activity history parity, one-screen operator prioritization.
 */
function resolveContactTouchAgeDays(record = {}) {
  const rawDate = resolveContactValue(record, 'lastActivity');
  const timestamp = Date.parse(rawDate);

  if (!Number.isFinite(timestamp)) return Infinity;

  return Math.max(0, Math.floor((Date.now() - timestamp) / 86400000));
}

/**
 * @function resolveContactPersona
 * @description Infers the practical relationship role for a contact from title, department and status fields.
 * @param {Object} record - Contact record.
 * @returns {string} Contact persona label.
 * @collaboration R86A relationship intelligence, account map segmentation, contact command filters.
 */
function resolveContactPersona(record = {}) {
  const text = [
    resolveContactValue(record, 'title'),
    resolveContactValue(record, 'department'),
    resolveContactValue(record, 'status'),
    resolveContactValue(record, 'source'),
  ].join(' ').toLowerCase();

  if (/(ceo|founder|owner|director|chief|vp|head|decision|procurement|buyer)/.test(text)) return 'Decision Maker';
  if (/(success|account manager|customer|renewal|implementation|onboarding)/.test(text)) return 'Customer Success';
  if (/(sales|deal|opportunity|revenue|commercial|partner manager)/.test(text)) return 'Deal Influencer';
  if (/(support|service|help|ticket|technical|engineering|it)/.test(text)) return 'Support Contact';
  if (/(partner|channel|reseller|vendor|supplier|alliance)/.test(text)) return 'Partner Contact';

  return 'Relationship Contact';
}

/**
 * @function resolveContactNextAction
 * @description Converts contact source gaps into a practical next action for a CRM operator.
 * @param {Object} record - Contact record.
 * @returns {string} Next action label.
 * @collaboration R86A next-best-action cockpit, consent-safe outreach, source-backed contact operations.
 */
function resolveContactNextAction(record = {}) {
  const consent = resolveContactConsent(record);
  const hasEmail = isKnownContactValue(resolveContactValue(record, 'email'));
  const hasPhone = isKnownContactValue(resolveContactValue(record, 'phone'));
  const hasAccount = isKnownContactValue(resolveContactValue(record, 'accountName'));
  const hasProof = isKnownContactValue(resolveContactValue(record, 'provenanceHash'));
  const touchAge = resolveContactTouchAgeDays(record);

  if (consent === 'REVOKED') return 'Do Not Contact';
  if (consent !== 'VERIFIED') return 'Consent Review';
  if (!hasEmail && !hasPhone) return 'Add Channel';
  if (!hasAccount) return 'Link Account';
  if (!hasProof) return 'Seal Proof Trail';
  if (touchAge > 30) return 'Re-engage';

  return 'Ready for Outreach';
}

/**
 * @function resolveContactSignalFilter
 * @description Resolves a filter label into the governed contact signal filter packet.
 * @param {string} option - Filter label.
 * @returns {{id:string,label:string}} Signal filter packet.
 * @collaboration R86A contact filter rail, relationship signal operations, guard-safe UI state.
 */
function resolveContactSignalFilter(option = '') {
  return CONTACT_SIGNAL_FILTERS[option] || { id: 'ALL', label: option || 'All Signals' };
}

/**
 * @function filterContactBySignal
 * @description Applies the active relationship signal filter to a contact record.
 * @param {Object} record - Contact record.
 * @param {string} signalFilterId - Active signal filter id.
 * @returns {boolean} True when the contact matches the signal filter.
 * @collaboration R86A source-backed filtering, consent posture, account graph and persona routing.
 */
function filterContactBySignal(record = {}, signalFilterId = 'ALL') {
  const consent = resolveContactConsent(record);
  const status = resolveContactStatus(record);
  const persona = resolveContactPersona(record);
  const hasEmail = isKnownContactValue(resolveContactValue(record, 'email'));
  const hasAccount = isKnownContactValue(resolveContactValue(record, 'accountName'));
  const touchAge = resolveContactTouchAgeDays(record);

  if (!signalFilterId || signalFilterId === 'ALL') return true;
  if (signalFilterId === 'CONSENT_READY') return consent === 'VERIFIED';
  if (signalFilterId === 'MISSING_EMAIL') return !hasEmail;
  if (signalFilterId === 'ACCOUNT_LINKED') return hasAccount;
  if (signalFilterId === 'AUTHORITY_PENDING') return consent !== 'VERIFIED' || resolveContactNextAction(record) === 'Seal Proof Trail';
  if (signalFilterId === 'RECENTLY_TOUCHED') return touchAge <= 14;
  if (signalFilterId === 'INACTIVE_CONTACTS') return status === 'INACTIVE' || touchAge > 45;
  if (signalFilterId === 'DECISION_MAKERS') return persona === 'Decision Maker';
  if (signalFilterId === 'CUSTOMER_SUCCESS') return persona === 'Customer Success';
  if (signalFilterId === 'DEAL_INFLUENCERS') return persona === 'Deal Influencer';
  if (signalFilterId === 'SUPPORT_CONTACTS') return persona === 'Support Contact';
  if (signalFilterId === 'PARTNER_CONTACTS') return persona === 'Partner Contact';

  return true;
}

/**
 * @function buildContactCommandSummary
 * @description Builds the real-world Contacts command summary from live contact, account, deal and evidence state.
 * @param {Object} params - Summary inputs.
 * @returns {Object} Contact command summary.
 * @collaboration R86A executive CRM contact operations, competitor-grade single-source truth, one-screen command telemetry.
 */
function buildContactCommandSummary({
  contacts = [],
  accounts = [],
  deals = [],
  evidence = [],
  sourcePosture = {},
} = {}) {
  const safeContacts = Array.isArray(contacts) ? contacts : [];
  const total = safeContacts.length;
  const consentReady = safeContacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length;
  const accountLinked = safeContacts.filter(record => isKnownContactValue(resolveContactValue(record, 'accountName'))).length;
  const proofReady = safeContacts.filter(record => isKnownContactValue(resolveContactValue(record, 'provenanceHash'))).length;
  const missingEmail = safeContacts.filter(record => !isKnownContactValue(resolveContactValue(record, 'email'))).length;
  const dormant = safeContacts.filter(record => resolveContactTouchAgeDays(record) > 30).length;
  const readyForOutreach = safeContacts.filter(record => resolveContactNextAction(record) === 'Ready for Outreach').length;
  const connectedRoutes = Number(sourcePosture.connected || sourcePosture.connectedRoutes || 0);
  const routeTotal = Number(sourcePosture.total || sourcePosture.totalRoutes || connectedRoutes || 0);

  return {
    total,
    consentReady,
    accountLinked,
    proofReady,
    missingEmail,
    dormant,
    readyForOutreach,
    accountRecords: Array.isArray(accounts) ? accounts.length : 0,
    dealRecords: Array.isArray(deals) ? deals.length : 0,
    evidenceRecords: Array.isArray(evidence) ? evidence.length : 0,
    connectedRoutes,
    routeTotal,
    commandPosture: total && consentReady === total && accountLinked === total
      ? 'Relationship graph ready'
      : total
        ? 'Relationship proof in progress'
        : 'Source routes awaiting contacts',
  };
}

/**
 * @function buildContactComposerDraft
 * @description Builds a blank Contacts command draft for the backend-owned contact composer.
 * @returns {Object} Contact draft.
 * @collaboration R86B real Contacts create flow, CRMContact model route, no fake front-end rows.
 */
function buildContactComposerDraft() {
  return {
    owner: '',
    salutation: '-None-',
    firstName: '',
    lastName: '',
    fullName: '',
    email: '',
    secondaryEmail: '',
    phoneCountryCode: '+27',
    phone: '',
    mobileCountryCode: '+27',
    mobile: '',
    homePhoneCountryCode: '+27',
    homePhone: '',
    otherPhoneCountryCode: '+27',
    otherPhone: '',
    faxCountryCode: '+27',
    fax: '',
    accountName: '',
    title: '',
    department: '',
    assistant: '',
    assistantPhoneCountryCode: '+27',
    assistantPhone: '',
    dateOfBirth: '',
    leadSource: '-None-',
    role: '',
    emailOptOut: false,
    consentStatus: 'PENDING',
    source: 'WILSY_CONTACT_OPERATING_ROOM',
    mailingStreet: '',
    mailingCity: '',
    mailingState: '',
    mailingZip: '',
    mailingCountry: '',
    otherStreet: '',
    otherCity: '',
    otherState: '',
    otherZip: '',
    otherCountry: '',
    addressSearch: '',
    formattedAddress: '',
    addressProviderId: '',
    addressSourceProvider: 'WILSY_ADDRESS_PROVIDER_PROXY',
    addressConfidence: 0,
    addressVerificationStatus: 'AWAITING_ADDRESS_INPUT',
    addressEvidenceReceipt: 'Address evidence pending.',
    addressSuggestions: [],
    description: '',
  };
}

/**
 * @function resolveContactCommandTenantId
 * @description Resolves the tenant boundary for Contacts backend commands.
 * @param {Object} params - Tenant and operator source packet.
 * @returns {string} Tenant id.
 * @collaboration R86B Contacts backend command route, tenant-scoped CRM writes, Wilsy OS source boundary.
 */
function resolveContactCommandTenantId({ tenantConfig = {}, user = {}, sourcePosture = {} } = {}) {
  return String(
    tenantConfig.tenantId
    || tenantConfig.id
    || tenantConfig._id
    || user.tenantId
    || user.activeTenantId
    || sourcePosture.tenantId
    || sourcePosture.tenant
    || 'MASTER'
  ).trim();
}

/**
 * @function normalizeContactPhoneInput
 * @description Keeps phone input operator-friendly while removing characters that cannot belong to a telephone number.
 * @param {unknown} value - Candidate phone text.
 * @returns {string} Editable phone value.
 * @collaboration R89C global Contacts SaaS, phone productivity controls, backend-safe international formatting.
 */
function normalizeContactPhoneInput(value = '') {
  return String(value || '')
    .replace(/[^\d+\s().-]/g, '')
    .replace(/\s{2,}/g, ' ');
}

/**
 * @function normalizeContactDialCode
 * @description Normalizes a country dial code for global Contact phone persistence.
 * @param {unknown} dialCode - Candidate country dial code.
 * @returns {string} Normalized dial code.
 * @collaboration R89C international contact records, global SaaS phone capture, CRM command payload hygiene.
 */
function normalizeContactDialCode(dialCode = '+27') {
  const digits = String(dialCode || '+27').replace(/[^\d]/g, '');
  return digits ? `+${digits}` : '+27';
}

/**
 * @function resolveContactInternationalPhone
 * @description Converts editable phone input and selected country code into compact international phone format.
 * @param {unknown} value - Editable phone value.
 * @param {unknown} countryCode - Selected country dial code.
 * @returns {string} International phone value or empty string.
 * @collaboration R89C global Contacts SaaS, CRM backend contact command, source-backed phone normalization.
 */
function resolveContactInternationalPhone(value = '', countryCode = '+27') {
  const editableValue = normalizeContactPhoneInput(value).trim();
  if (!editableValue) return '';

  const digits = editableValue.replace(/[^\d]/g, '');
  if (!digits) return '';

  if (editableValue.startsWith('+')) {
    return `+${digits}`;
  }

  const normalizedCountryCode = normalizeContactDialCode(countryCode);
  const nationalDigits = digits.replace(/^0+/, '');
  return nationalDigits ? `${normalizedCountryCode}${nationalDigits}` : '';
}

/**
 * @function normalizeContactComposerPayload
 * @description Converts a Contacts composer draft into the CRM command route payload.
 * @param {Object} draft - Composer draft.
 * @param {Object} context - Tenant and operator context.
 * @returns {Object} Backend-safe contact payload.
 * @collaboration R86B CRMContact persistence, create-contact command, source-backed relationship graph.
 */
function normalizeContactComposerPayload(draft = {}, context = {}) {
  const explicitName = String(draft.fullName || draft.name || '').trim();
  const firstName = String(draft.firstName || '').trim();
  const lastName = String(draft.lastName || draft.surname || '').trim();
  const name = explicitName || [firstName, lastName].filter(Boolean).join(' ').trim();
  const tenantId = resolveContactCommandTenantId(context);
  const owner = String(context.user?.displayName || context.user?.name || context.user?.email || 'CRM Operator').trim();
  const [fallbackFirstName, ...fallbackRemainingName] = name.split(/\s+/).filter(Boolean);
  const mailingAddress = buildContactFormattedAddress(draft, 'mailing');
  const otherAddress = buildContactFormattedAddress(draft, 'other');

  return {
    tenantId,
    owner: String(draft.owner || owner).trim(),
    contactOwner: String(draft.owner || owner).trim(),
    salutation: String(draft.salutation || '-None-').trim(),
    firstName: firstName || fallbackFirstName || '',
    surname: lastName || fallbackRemainingName.join(' '),
    lastName: lastName || fallbackRemainingName.join(' '),
    fullName: name,
    name,
    email: String(draft.email || '').trim().toLowerCase(),
    secondaryEmail: String(draft.secondaryEmail || '').trim().toLowerCase(),
    phoneCountryCode: normalizeContactDialCode(draft.phoneCountryCode),
    phone: resolveContactInternationalPhone(draft.phone, draft.phoneCountryCode),
    mobileCountryCode: normalizeContactDialCode(draft.mobileCountryCode),
    mobile: resolveContactInternationalPhone(draft.mobile, draft.mobileCountryCode),
    homePhoneCountryCode: normalizeContactDialCode(draft.homePhoneCountryCode),
    homePhone: resolveContactInternationalPhone(draft.homePhone, draft.homePhoneCountryCode),
    otherPhoneCountryCode: normalizeContactDialCode(draft.otherPhoneCountryCode),
    otherPhone: resolveContactInternationalPhone(draft.otherPhone, draft.otherPhoneCountryCode),
    faxCountryCode: normalizeContactDialCode(draft.faxCountryCode),
    fax: resolveContactInternationalPhone(draft.fax, draft.faxCountryCode),
    accountName: String(draft.accountName || draft.companyName || draft.company || '').trim(),
    companyName: String(draft.accountName || draft.companyName || draft.company || '').trim(),
    title: String(draft.title || '').trim(),
    department: String(draft.department || '').trim(),
    assistant: String(draft.assistant || '').trim(),
    assistantPhoneCountryCode: normalizeContactDialCode(draft.assistantPhoneCountryCode),
    assistantPhone: resolveContactInternationalPhone(draft.assistantPhone, draft.assistantPhoneCountryCode),
    dateOfBirth: String(draft.dateOfBirth || '').trim(),
    leadSource: String(draft.leadSource || '-None-').trim(),
    role: String(draft.role || '').trim(),
    decisionRole: String(draft.role || draft.title || '').trim(),
    emailOptOut: Boolean(draft.emailOptOut),
    consentStatus: String(draft.consentStatus || 'PENDING').trim(),
    source: draft.source || 'WILSY_CONTACT_OPERATING_ROOM',
    sourceSystem: 'WILSY_OS_CRM_CONTACTS',
    status: 'ACTIVE',
    mailingStreet: String(draft.mailingStreet || draft.street || '').trim(),
    mailingCity: String(draft.mailingCity || draft.city || '').trim(),
    mailingState: String(draft.mailingState || draft.state || '').trim(),
    mailingZip: String(draft.mailingZip || draft.zipCode || draft.postalCode || '').trim(),
    mailingCountry: String(draft.mailingCountry || draft.country || '').trim(),
    otherStreet: String(draft.otherStreet || '').trim(),
    otherCity: String(draft.otherCity || '').trim(),
    otherState: String(draft.otherState || '').trim(),
    otherZip: String(draft.otherZip || '').trim(),
    otherCountry: String(draft.otherCountry || '').trim(),
    formattedAddress: draft.formattedAddress || mailingAddress,
    mailingAddress,
    otherAddress,
    addressSearch: String(draft.addressSearch || '').trim(),
    addressProviderId: String(draft.addressProviderId || '').trim(),
    addressSourceProvider: String(draft.addressSourceProvider || 'WILSY_ADDRESS_PROVIDER_PROXY').trim(),
    addressConfidence: Number(draft.addressConfidence || 0),
    addressVerificationStatus: String(draft.addressVerificationStatus || 'AWAITING_ADDRESS_INPUT').trim(),
    addressEvidenceReceipt: String(draft.addressEvidenceReceipt || '').trim(),
    description: String(draft.description || draft.notes || '').trim(),
  };
}

/**
 * @function isContactComposerPayloadReady
 * @description Confirms a Contacts create command has enough real source data to reach the backend.
 * @param {Object} payload - Normalized contact payload.
 * @returns {boolean} True when the payload can be submitted.
 * @collaboration R86B no-fake-data guard, CRMContact create route, relationship data quality.
 */
function isContactComposerPayloadReady(payload = {}) {
  return Boolean(payload.name || payload.fullName || payload.lastName || payload.email || payload.phone || payload.accountName || payload.companyName);
}

/**
 * @function normalizeContactAddressText
 * @description Normalizes Contacts address text before lookup, suggestions or command payload serialization.
 * @param {unknown} value - Candidate address value.
 * @returns {string} Normalized address text.
 * @collaboration R87C Contacts create command, reused Leads address intelligence contract, backend address provider route.
 */
function normalizeContactAddressText(value = '') {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function normalizeContactAddressEditValue
 * @description Normalizes address text while preserving the trailing space an operator just typed.
 * @param {unknown} value - Editable address value.
 * @returns {string} Address value safe for controlled text input.
 * @collaboration R89C Contacts address usability, shared address intelligence, no hostile input trimming.
 */
function normalizeContactAddressEditValue(value = '') {
  return String(value || '')
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/ {2,}/g, ' ');
}

/**
 * @function resolveContactAddressCountry
 * @description Resolves a safe country value for Contacts address intelligence.
 * @param {Object} draftPayload - Current contact draft.
 * @returns {string} Country value.
 * @collaboration R87C Contacts address component, global CRM contacts, South Africa-ready default posture.
 */
function resolveContactAddressCountry(draftPayload = {}) {
  return normalizeContactAddressText(
    draftPayload.mailingCountry ||
    draftPayload.country ||
    draftPayload.otherCountry ||
    'South Africa'
  );
}

/**
 * @function resolveContactAddressPostalCode
 * @description Extracts a likely postal code from a contact address query or draft aliases.
 * @param {string} query - Address search query.
 * @param {Object} draftPayload - Current contact draft.
 * @returns {string} Postal code candidate.
 * @collaboration R87C address reuse, contact mailing address normalization, backend payload quality.
 */
function resolveContactAddressPostalCode(query = '', draftPayload = {}) {
  const direct = normalizeContactAddressText(draftPayload.mailingZip || draftPayload.zipCode || draftPayload.postalCode || '');
  if (direct) return direct;

  const match = String(query || '').match(/\b\d{4,6}\b/);
  return match ? match[0] : '';
}

/**
 * @function buildContactFormattedAddress
 * @description Builds a formatted address string from mailing or other address fields.
 * @param {Object} draftPayload - Current contact draft.
 * @param {string} addressType - Address type prefix.
 * @returns {string} Formatted address.
 * @collaboration R87C Zoho-grade Contact address information, backend-safe address payload, Contacts create command.
 */
function buildContactFormattedAddress(draftPayload = {}, addressType = 'mailing') {
  const prefix = addressType === 'other' ? 'other' : 'mailing';
  const parts = [
    draftPayload[`${prefix}Street`] || draftPayload.street,
    draftPayload[`${prefix}City`] || draftPayload.city,
    draftPayload[`${prefix}State`] || draftPayload.state,
    draftPayload[`${prefix}Zip`] || draftPayload.zipCode || draftPayload.postalCode,
    draftPayload[`${prefix}Country`] || draftPayload.country,
  ].map(normalizeContactAddressText).filter(Boolean);

  return parts.join(', ');
}

/**
 * @function buildContactAddressSuggestion
 * @description Builds one Contacts address suggestion using the Leads address-intelligence packet shape.
 * @param {Object} params - Address suggestion inputs.
 * @returns {Object} Contact address suggestion.
 * @collaboration R87C Contacts address component reuse, Leads provider parity, address evidence receipts.
 */
function buildContactAddressSuggestion(params = {}) {
  const query = normalizeContactAddressText(params.query);
  const draftPayload = params.draft || {};
  const parts = query.split(',').map(part => normalizeContactAddressText(part)).filter(Boolean);
  const street = normalizeContactAddressText(params.street || draftPayload.mailingStreet || parts[0] || query);
  const city = normalizeContactAddressText(params.city || draftPayload.mailingCity || parts[1] || '');
  const state = normalizeContactAddressText(params.state || draftPayload.mailingState || parts[2] || '');
  const country = normalizeContactAddressText(params.country || resolveContactAddressCountry(draftPayload));
  const postalCode = normalizeContactAddressText(params.postalCode || resolveContactAddressPostalCode(query, draftPayload));
  const formattedAddress = [street, city, state, postalCode, country].filter(Boolean).join(', ');
  const confidence = Number(params.confidence || (street && city && country ? 84 : street && country ? 66 : 42));

  return {
    id: params.id || `wilsy-contact-address-${String(params.rank || 1)}-${formattedAddress.length}`,
    label: params.label || 'Contact address candidate',
    street,
    city,
    state,
    postalCode,
    country,
    latitude: params.latitude || '',
    longitude: params.longitude || '',
    formattedAddress,
    provider: params.provider || 'WILSY_LOCAL_INTELLIGENCE',
    providerId: params.providerId || `CONTACT-LOCAL-${confidence}-${formattedAddress.length}`,
    confidence,
    verificationStatus: params.verificationStatus || (confidence >= 80 ? 'LOCAL_READY_FOR_PROVIDER_VERIFY' : 'MANUAL_REVIEW_REQUIRED'),
    territory: params.territory || [city, state, country].filter(Boolean).join(' · '),
    receipt: params.receipt || `CONTACT-ADDR-R87C-${confidence}-${formattedAddress.length}`,
  };
}

/**
 * @function buildContactAddressSuggestions
 * @description Builds local Contacts address suggestions when the live provider route is still returning empty.
 * @param {Object} params - Suggestion build params.
 * @returns {Array<Object>} Address suggestions.
 * @collaboration R87C one-screen Contacts create, address provider fallback, no leaked provider keys.
 */
function buildContactAddressSuggestions(params = {}) {
  const draftPayload = params.draft || {};
  const query = normalizeContactAddressText(params.query || draftPayload.addressSearch || draftPayload.formattedAddress || draftPayload.mailingStreet || '');

  if (query.length < 3 && !draftPayload.mailingStreet) return [];

  const primary = buildContactAddressSuggestion({
    id: 'wilsy-contact-primary-address',
    label: 'Primary mailing address',
    query,
    draft: draftPayload,
    rank: 1,
    confidence: query.includes(',') ? 86 : 68,
  });
  const territory = buildContactAddressSuggestion({
    id: 'wilsy-contact-territory-address',
    label: 'Territory routing address',
    query,
    draft: {
      ...draftPayload,
      mailingStreet: draftPayload.mailingStreet || primary.street,
      mailingCity: draftPayload.mailingCity || primary.city,
      mailingState: draftPayload.mailingState || primary.state,
      mailingZip: draftPayload.mailingZip || primary.postalCode,
      mailingCountry: draftPayload.mailingCountry || primary.country,
    },
    rank: 2,
    confidence: primary.city ? 78 : 58,
    provider: 'WILSY_TERRITORY_ROUTER',
    verificationStatus: primary.city ? 'ROUTING_READY' : 'CITY_REQUIRED_FOR_ROUTING',
    territory: primary.territory || 'Territory pending city',
    receipt: `CONTACT-ADDR-R87C-TERRITORY-${primary.formattedAddress.length}`,
  });

  return [primary, territory].filter((suggestion, index, list) => (
    suggestion.formattedAddress &&
    list.findIndex(item => item.formattedAddress === suggestion.formattedAddress && item.provider === suggestion.provider) === index
  ));
}

/**
 * @function formatContactAddressProviderLabel
 * @description Converts Contacts address provider codes into business-facing text.
 * @param {string} provider - Provider code.
 * @returns {string} Business-facing provider label.
 * @collaboration R87C shared address intelligence language, Contacts composer, operator proof readability.
 */
function formatContactAddressProviderLabel(provider = '') {
  const normalized = normalizeContactAddressText(provider).toUpperCase();
  if (normalized.includes('MAPBOX')) return 'Mapbox Address Intelligence';
  if (normalized.includes('GOOGLE')) return 'Google Places Intelligence';
  if (normalized.includes('LOQATE')) return 'Loqate Address Verification';
  if (normalized.includes('HERE')) return 'HERE Address Intelligence';
  if (normalized.includes('OPENSTREETMAP') || normalized.includes('NOMINATIM')) return 'OpenStreetMap fallback';
  return 'Wilsy OS address intelligence';
}

/**
 * @function formatContactAddressStatusLabel
 * @description Converts raw Contacts address status codes into readable command language.
 * @param {string} status - Address status.
 * @returns {string} Business-facing status label.
 * @collaboration R87C address provider route, Contacts create modal, source-proof UX.
 */
function formatContactAddressStatusLabel(status = '') {
  const normalized = normalizeContactAddressText(status).toUpperCase();
  if (normalized.includes('LIVE_PROVIDER_SUGGESTED')) return 'Verified provider suggestion';
  if (normalized.includes('LIVE_PROVIDER_LOOKUP_RUNNING')) return 'Searching verified address providers';
  if (normalized.includes('ADDRESS_PROVIDER_LIVE')) return 'Live address intelligence active';
  if (normalized.includes('ADDRESS_PROVIDER_EMPTY')) return 'No verified match returned yet';
  if (normalized.includes('ADDRESS_PROVIDER_UNREACHABLE')) return 'Address provider temporarily unavailable';
  if (normalized.includes('ROUTING_READY')) return 'Territory routing ready';
  if (normalized.includes('QUERY_TOO_SHORT') || normalized.includes('AWAITING')) return 'Ready for address search';
  if (normalized.includes('MANUAL')) return 'Manual review pending';
  return 'Address evidence captured';
}

/**
 * @function formatContactAddressConfidenceLabel
 * @description Formats Contacts address confidence into a compact operator label.
 * @param {number|string} confidence - Confidence value.
 * @returns {string} Confidence label.
 * @collaboration R87C address evidence strip, CRM create productivity, provider proof.
 */
function formatContactAddressConfidenceLabel(confidence = 0) {
  const numericConfidence = Number(confidence || 0);
  return numericConfidence ? `${numericConfidence}% match confidence` : 'Confidence pending';
}

/**
 * @function formatContactAddressReceiptLabel
 * @description Formats Contacts address evidence receipt text.
 * @param {string} receipt - Receipt value.
 * @returns {string} Business-facing receipt.
 * @collaboration R87C address evidence, source posture, Contact create forensic trail.
 */
function formatContactAddressReceiptLabel(receipt = '') {
  const normalized = normalizeContactAddressText(receipt);
  return normalized ? `Evidence receipt ${normalized}` : 'Evidence receipt pending';
}

/**
 * @function buildContactAddressVerificationPacket
 * @description Builds the visible Contacts address verification evidence packet.
 * @param {Object} draftPayload - Current contact draft.
 * @returns {Object} Address evidence packet.
 * @collaboration R87C shared address intelligence contract, Contacts create surface, address source proof.
 */
function buildContactAddressVerificationPacket(draftPayload = {}) {
  return {
    status: formatContactAddressStatusLabel(draftPayload.addressVerificationStatus || (draftPayload.mailingStreet ? 'MANUAL_REVIEW_REQUIRED' : 'AWAITING_ADDRESS_INPUT')),
    provider: formatContactAddressProviderLabel(draftPayload.addressSourceProvider || 'WILSY_LOCAL_INTELLIGENCE'),
    confidenceLabel: formatContactAddressConfidenceLabel(draftPayload.addressConfidence),
    receipt: formatContactAddressReceiptLabel(draftPayload.addressEvidenceReceipt),
  };
}

/**
 * @function requestContactAddressSuggestions
 * @description Requests Contacts address suggestions through the same CRM command provider route used by Leads.
 * @param {string} query - Address search query.
 * @param {Object} context - Tenant command context.
 * @returns {Promise<Object>} Address provider envelope.
 * @collaboration R87C Contacts address component reuse, /api/crm/command/address/suggest, provider-backed address capture.
 */
async function requestContactAddressSuggestions(query = '', context = {}) {
  const tenantId = resolveContactCommandTenantId(context);

  return wilsyCrmFetchJson('/api/crm/command/address/suggest', {
    method: 'POST',
    tenantId,
    moduleId: 'contacts',
    action: 'address_suggest',
    command: 'crm.contacts.address.suggest',
    body: {
      q: query,
      query,
      country: 'ZA',
      countryCode: 'ZA',
      commandSurface: 'R87C_CONTACT_ADDRESS_INTELLIGENCE',
    },
  });
}

/**
 * @function createContactThroughCommandBackend
 * @description Persists a contact through the CRM command fabric instead of creating local placeholder rows.
 * @param {Object} payload - Normalized contact payload.
 * @param {Object} context - Tenant context.
 * @returns {Promise<Object>} Backend command envelope.
 * @collaboration R86B Contacts-to-backend link, /api/crm/command/contacts, live snapshot refresh.
 */
async function createContactThroughCommandBackend(payload = {}, context = {}) {
  return wilsyCrmFetchJson('/api/crm/command/contacts', {
    method: 'POST',
    tenantId: payload.tenantId || resolveContactCommandTenantId(context),
    moduleId: 'contacts',
    action: 'create',
    command: 'crm.contacts.command.create',
    body: {
      tenantId: payload.tenantId || resolveContactCommandTenantId(context),
      contact: payload,
    },
  });
}

/**
 * @function requestContactExportFromBackend
 * @description Requests a backend Contacts export command and falls back to an explicit route envelope if export is unavailable.
 * @param {Object} context - Export context.
 * @returns {Promise<Object>} Export command envelope.
 * @collaboration R86B Contacts export action, CRM command client, real route posture instead of dead UI.
 */
async function requestContactExportFromBackend(context = {}) {
  const tenantId = resolveContactCommandTenantId(context);

  return wilsyCrmFetchJson('/api/crm/export', {
    method: 'POST',
    tenantId,
    moduleId: 'contacts',
    action: 'export',
    command: 'crm.contacts.export',
    body: {
      tenantId,
      moduleId: 'contacts',
      format: 'csv',
      filters: context.filters || {},
    },
  });
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

/**
 * @function WilsyContactOperatingRoom
 * @description Renders the sovereign Contacts operating room for relationship intelligence, consent posture and source proof.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Contacts operating room.
 * @collaboration R76C Contacts module, CRMDashboard route ownership, Wilsy OS CRM competitive surface.
 */
export default function WilsyContactOperatingRoom({
  contacts = [],
  accounts = [],
  deals = [],
  evidence = [],
  connectors = [],
  sourcePosture = {},
  sourceErrors = [],
  loading = false,
  themeRuntime = {},
  tenantConfig = {},
  user = {},
  onRefresh = () => {},
  onCreate = () => {},
  onOpenThemeAuthority = openCrmGlobalThemeAuthorityFallback,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTopTab, setActiveTopTab] = useState('records');
  const [activeListView, setActiveListView] = useState('ALL_CONTACTS');
  const [sortMode, setSortMode] = useState('relationship');
  const [sortMenuOpen, setSortMenuOpen] = useState(false);
  const [selectedRowIds, setSelectedRowIds] = useState([]);
  const [openRowActionId, setOpenRowActionId] = useState('');
  const [filterRailOpen, setFilterRailOpen] = useState(true);
  const [activeSignalFilter, setActiveSignalFilter] = useState('ALL');
  const [contactPage, setContactPage] = useState(1);
  const [contactPageSize, setContactPageSize] = useState(10);
  const [contactComposerOpen, setContactComposerOpen] = useState(false);
  const [contactDraft, setContactDraft] = useState(() => buildContactComposerDraft());
  const [contactCommandBusy, setContactCommandBusy] = useState(false);
  const [contactCommandStatus, setContactCommandStatus] = useState({
    status: 'BACKEND_READY',
    message: 'Contacts command route mapped to /api/crm/command/contacts.',
  });

  const normalizedContacts = Array.isArray(contacts) ? contacts : [];
  const activeView = CONTACT_LIST_VIEWS.find(view => view.id === activeListView) || CONTACT_LIST_VIEWS[0];
  const activeSort = CONTACT_SORT_OPTIONS.find(option => option.id === sortMode) || CONTACT_SORT_OPTIONS[0];
  const activeSignalFilterLabel = Object.values(CONTACT_SIGNAL_FILTERS).find(filter => filter.id === activeSignalFilter)?.label || 'All Signals';
  const tenantLabel = tenantConfig?.legalName || tenantConfig?.name || tenantConfig?.tenantName || 'Wilsy OS Root';
  const role = String(user?.role || user?.accountRole || tenantConfig?.role || 'RELATIONSHIP_OPERATOR').toUpperCase();
  const globalThemeAuthorityLabel = resolveCrmGlobalThemeAuthorityLabel(themeRuntime);
  const globalThemeAuthorityMode = resolveCrmGlobalThemeAuthorityMode(themeRuntime);
  const sourceRouteConnected = Number(sourcePosture.connected || sourcePosture.connectedRoutes || 0);
  const sourceRouteTotal = Number(sourcePosture.total || sourcePosture.totalRoutes || connectors.length || sourceRouteConnected || 0);

  const filteredContacts = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return sortContactRecords(
      normalizedContacts.filter((record) => {
        if (!filterContactByView(record, activeListView)) return false;
        if (!filterContactBySignal(record, activeSignalFilter)) return false;

        if (!query) return true;

        return [
          'name',
          'accountName',
          'email',
          'phone',
          'title',
          'department',
          'source',
          'owner',
          'status',
          'consentStatus',
        ].some(field => resolveContactValue(record, field).toLowerCase().includes(query));
      }),
      sortMode
    );
  }, [activeListView, activeSignalFilter, normalizedContacts, searchQuery, sortMode]);

  const contactMetrics = useMemo(() => buildContactMetrics({
    contacts: normalizedContacts,
    accounts,
    deals,
    evidence,
    sourcePosture,
  }), [accounts, deals, evidence, normalizedContacts, sourcePosture]);

  const contactCommandSummary = useMemo(() => buildContactCommandSummary({
    contacts: normalizedContacts,
    accounts,
    deals,
    evidence,
    sourcePosture,
  }), [accounts, deals, evidence, normalizedContacts, sourcePosture]);

  const contactPagination = useMemo(() => (
    buildContactPagination(filteredContacts.length, contactPage, contactPageSize)
  ), [contactPage, contactPageSize, filteredContacts.length]);

  const paginatedContacts = useMemo(() => (
    filteredContacts.slice(contactPagination.startIndex, contactPagination.endIndex)
  ), [contactPagination.endIndex, contactPagination.startIndex, filteredContacts]);

  const visibleIds = paginatedContacts.map((record, index) => resolveContactId(record, contactPagination.startIndex + index));
  const allRowsSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));

  useEffect(() => {
    setContactPage(1);
    setSelectedRowIds([]);
  }, [activeListView, activeSignalFilter, contactPageSize, searchQuery, sortMode]);

  useEffect(() => {
    if (contactPage !== contactPagination.currentPage) {
      setContactPage(contactPagination.currentPage);
    }
  }, [contactPage, contactPagination.currentPage]);

  /**
   * @function handleToggleAllContactSelection
   * @description Toggles selection for every visible contact row.
   * @collaboration R76C Contacts table, bulk action posture, operator list control.
   */
  function handleToggleAllContactSelection() {
    if (allRowsSelected) {
      setSelectedRowIds([]);
      return;
    }

    setSelectedRowIds(visibleIds);
  }

  /**
   * @function handleToggleContactSelection
   * @description Toggles one contact row selection.
   * @param {string} recordId - Contact record id.
   * @collaboration R76C Contacts table, row action state, bulk operations.
   */
  function handleToggleContactSelection(recordId) {
    setSelectedRowIds(previous => (
      previous.includes(recordId)
        ? previous.filter(value => value !== recordId)
        : [...previous, recordId]
    ));
  }

  /**
   * @function handleSignalFilterToggle
   * @description Toggles a contact signal filter from the left filter rail.
   * @param {string} filterId - Signal filter id.
   * @collaboration R86A real-world Contacts filtering, one-screen cockpit ergonomics, source-backed relationship command.
   */
  function handleSignalFilterToggle(filterId = 'ALL') {
    setActiveSignalFilter(previous => (previous === filterId ? 'ALL' : filterId));
  }

  /**
   * @function openContactComposer
   * @description Opens the Contacts-owned backend create composer.
   * @collaboration R86B Create Contact command, CRMContact persistence, one-screen modal ownership.
   */
  function openContactComposer() {
    setContactDraft(buildContactComposerDraft());
    setContactCommandStatus({
      status: 'COMPOSER_OPEN',
      message: 'Enter source-backed contact details, then save through the CRM command backend.',
    });
    setContactComposerOpen(true);
  }

  /**
   * @function closeContactComposer
   * @description Closes the Contacts create composer without mutating records.
   * @collaboration R86B guarded contact create flow, no local fake rows, operator escape path.
   */
  function closeContactComposer() {
    setContactComposerOpen(false);
    setContactDraft(buildContactComposerDraft());
  }

  /**
   * @function handleContactDraftChange
   * @description Updates one field in the Contacts create draft.
   * @param {string} field - Draft field.
   * @param {string} value - Draft value.
   * @collaboration R86B controlled Contacts composer, backend payload safety, CRMContact field mapping.
   */
  function handleContactDraftChange(field, value) {
    const phoneFields = ['phone', 'mobile', 'homePhone', 'otherPhone', 'assistantPhone', 'fax'];
    const nextValue = phoneFields.includes(field) ? normalizeContactPhoneInput(value) : value;

    setContactDraft(previous => ({
      ...previous,
      [field]: nextValue,
    }));
  }

  /**
   * @function handleContactAddressSearch
   * @description Updates the Contacts address draft and requests provider suggestions through the shared CRM address route.
   * @param {string} value - Address search value.
   * @returns {Promise<void>} Address lookup completion.
   * @collaboration R87C Contacts create address intelligence, Leads address provider route, source-proof capture.
   */
  async function handleContactAddressSearch(value = '') {
    const editableQuery = normalizeContactAddressEditValue(value);
    const query = normalizeContactAddressText(editableQuery);
    const localSuggestions = buildContactAddressSuggestions({
      query,
      draft: {
        ...contactDraft,
        addressSearch: editableQuery,
        mailingStreet: editableQuery,
      },
    });

    setContactDraft(previous => ({
      ...previous,
      addressSearch: editableQuery,
      mailingStreet: editableQuery,
      formattedAddress: editableQuery,
      addressSuggestions: localSuggestions,
      addressVerificationStatus: query.length < 3 ? 'QUERY_TOO_SHORT' : 'LIVE_PROVIDER_LOOKUP_RUNNING',
      addressSourceProvider: 'WILSY_ADDRESS_PROVIDER_PROXY',
      addressConfidence: 0,
      addressEvidenceReceipt: query.length < 3
        ? 'Type at least three characters for live address search.'
        : 'Signed provider lookup running through Wilsy backend.',
    }));

    if (query.length < 3) return;

    try {
      const envelope = await requestContactAddressSuggestions(query, { tenantConfig, user, sourcePosture });
      const suggestions = Array.isArray(envelope?.suggestions)
        ? envelope.suggestions
        : Array.isArray(envelope?.data?.suggestions)
          ? envelope.data.suggestions
          : [];
      const fallbackSuggestions = suggestions.length ? suggestions : localSuggestions;
      const firstSuggestion = fallbackSuggestions[0] || {};

      setContactDraft(previous => ({
        ...previous,
        addressSuggestions: fallbackSuggestions,
        addressSourceProvider: envelope?.provider || firstSuggestion.provider || 'WILSY_ADDRESS_PROVIDER_PROXY',
        addressVerificationStatus: envelope?.sourceStatus || firstSuggestion.verificationStatus || 'ADDRESS_PROVIDER_EMPTY',
        addressConfidence: Number(firstSuggestion.confidence || 0),
        addressEvidenceReceipt: envelope?.rootHashShort || envelope?.message || firstSuggestion.receipt || 'Signed address provider response received.',
      }));
    } catch (error) {
      setContactDraft(previous => ({
        ...previous,
        addressSuggestions: localSuggestions,
        addressVerificationStatus: 'ADDRESS_PROVIDER_UNREACHABLE',
        addressSourceProvider: 'WILSY_ADDRESS_PROVIDER_PROXY',
        addressConfidence: localSuggestions[0]?.confidence || 0,
        addressEvidenceReceipt: error?.message || 'Signed address provider lookup failed. Local address capture remains available.',
      }));
    }
  }

  /**
   * @function handleContactAddressSuggestionSelect
   * @description Applies a selected address suggestion to the Contacts mailing address fields.
   * @param {Object} suggestion - Address suggestion packet.
   * @collaboration R87C Contacts address component, provider evidence, mailing address normalization.
   */
  function handleContactAddressSuggestionSelect(suggestion = {}) {
    setContactDraft(previous => ({
      ...previous,
      addressSearch: suggestion.formattedAddress || previous.addressSearch,
      mailingStreet: suggestion.street || previous.mailingStreet,
      mailingCity: suggestion.city || previous.mailingCity,
      mailingState: suggestion.state || previous.mailingState,
      mailingZip: suggestion.postalCode || previous.mailingZip,
      mailingCountry: suggestion.country || previous.mailingCountry,
      formattedAddress: suggestion.formattedAddress || previous.formattedAddress,
      addressProviderId: suggestion.providerId || previous.addressProviderId,
      addressSourceProvider: suggestion.provider || previous.addressSourceProvider,
      addressConfidence: suggestion.confidence || previous.addressConfidence,
      addressVerificationStatus: suggestion.verificationStatus || previous.addressVerificationStatus,
      addressEvidenceReceipt: suggestion.receipt || previous.addressEvidenceReceipt,
      addressSuggestions: [],
    }));
  }

  /**
   * @function handleCopyMailingAddressToOther
   * @description Copies the Contacts mailing address into the secondary address fields.
   * @collaboration R87C Zoho-grade Contact address information, operator productivity, duplicate address entry reduction.
   */
  function handleCopyMailingAddressToOther() {
    setContactDraft(previous => ({
      ...previous,
      otherStreet: previous.mailingStreet,
      otherCity: previous.mailingCity,
      otherState: previous.mailingState,
      otherZip: previous.mailingZip,
      otherCountry: previous.mailingCountry,
    }));
  }

  /**
   * @function handleContactCreateSubmit
   * @description Sends a Contacts create command to the backend and refreshes live source records.
   * @param {Event} event - Form submit event.
   * @returns {Promise<void>} Backend command completion.
   * @collaboration R86B direct Contacts backend link, CRMContact model route, live snapshot refresh.
   */
  async function handleContactCreateSubmit(event) {
    event.preventDefault();

    const context = { tenantConfig, user, sourcePosture };
    const payload = normalizeContactComposerPayload(contactDraft, context);

    if (!isContactComposerPayloadReady(payload)) {
      setContactCommandStatus({
        status: 'SOURCE_PAYLOAD_REQUIRED',
        message: 'Add a name, email, phone, or account before saving a contact.',
      });
      return;
    }

    setContactCommandBusy(true);
    setContactCommandStatus({
      status: 'SAVING',
      message: 'Sending contact to CRM command backend.',
    });

    try {
      const envelope = await createContactThroughCommandBackend(payload, context);
      const commandStatus = envelope?.sourceStatus || envelope?.status || (envelope?.ok ? 'DB_PERSISTED' : 'SOURCE_REQUIRED');

      if (envelope?.ok === false || String(commandStatus).includes('ERROR')) {
        setContactCommandStatus({
          status: commandStatus,
          message: envelope?.message || envelope?.error || 'Contact backend command did not accept the record.',
        });
        return;
      }

      setContactCommandStatus({
        status: commandStatus,
        message: 'Contact saved through backend command route. Refreshing live source graph.',
      });
      setContactComposerOpen(false);
      setContactDraft(buildContactComposerDraft());
      await onRefresh();
    } catch (error) {
      setContactCommandStatus({
        status: 'COMMAND_ERROR',
        message: error?.message || 'Contact backend command failed.',
      });
    } finally {
      setContactCommandBusy(false);
    }
  }

  /**
   * @function handleContactExport
   * @description Routes Contacts export through the backend export command.
   * @returns {Promise<void>} Export command completion.
   * @collaboration R86B Contacts export command, route posture visibility, no dead buttons.
   */
  async function handleContactExport() {
    setContactCommandBusy(true);
    setContactCommandStatus({
      status: 'EXPORTING',
      message: 'Requesting Contacts export from CRM backend.',
    });

    try {
      const envelope = await requestContactExportFromBackend({
        tenantConfig,
        user,
        sourcePosture,
        filters: {
          searchQuery,
          activeListView,
          activeSignalFilter,
          sortMode,
        },
      });
      const exportStatus = envelope?.sourceStatus || envelope?.status || (envelope?.ok ? 'EXPORT_READY' : 'EXPORT_ROUTE_REQUIRED');

      setContactCommandStatus({
        status: exportStatus,
        message: envelope?.downloadUrl
          ? 'Contacts export is ready.'
          : envelope?.message || 'Contacts export route posture returned by backend.',
      });

      if (envelope?.downloadUrl && typeof window !== 'undefined') {
        window.open(envelope.downloadUrl, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setContactCommandStatus({
        status: 'EXPORT_ERROR',
        message: error?.message || 'Contacts export command failed.',
      });
    } finally {
      setContactCommandBusy(false);
    }
  }

  /**
   * @function renderContactCommandStrip
   * @description Renders compact contact operations intelligence above the tab deck.
   * @returns {JSX.Element} Contact command intelligence strip.
   * @collaboration R86A one-screen relationship command, Salesforce single-source truth parity, HubSpot activity-history parity.
   */
  function renderContactCommandStrip() {
    return (
      <section className={styles.contactCommandIntelligenceStrip} aria-label="Contact command intelligence">
        <article>
          <small>Outreach Ready</small>
          <strong>{contactCommandSummary.readyForOutreach}/{contactCommandSummary.total || 0}</strong>
          <em>{contactCommandSummary.commandPosture}</em>
        </article>
        <article>
          <small>Needs Consent</small>
          <strong>{Math.max(0, contactCommandSummary.total - contactCommandSummary.consentReady)}</strong>
          <em>POPIA, GDPR and SOC2 posture</em>
        </article>
        <article>
          <small>Missing Email</small>
          <strong>{contactCommandSummary.missingEmail}</strong>
          <em>Communication channel coverage</em>
        </article>
        <article>
          <small>Stale Touches</small>
          <strong>{contactCommandSummary.dormant}</strong>
          <em>Last activity over 30 days</em>
        </article>
        <article>
          <small>Source Graph</small>
          <strong>{contactCommandSummary.connectedRoutes}/{contactCommandSummary.routeTotal || connectors.length || 0}</strong>
          <em>{contactCommandSummary.accountRecords} accounts · {contactCommandSummary.dealRecords} deals · {contactCommandSummary.evidenceRecords} proof</em>
        </article>
      </section>
    );
  }

  /**
   * @function renderContactBackendStatus
   * @description Renders the active Contacts backend command route posture.
   * @returns {JSX.Element} Backend status strip.
   * @collaboration R86B backend linkage visibility, Contacts command fabric, operator trust surface.
   */
  function renderContactBackendStatus() {
    return (
      <section className={styles.contactBackendStatus} aria-label="Contacts backend command status">
        <span>
          <Database size={14} />
          <strong>{contactCommandStatus.status}</strong>
        </span>
        <em>{contactCommandStatus.message}</em>
      </section>
    );
  }

  /**
   * @function renderContactPhoneField
   * @description Renders a global dial-code selector with an editable phone input for the Contacts composer.
   * @param {Object} params - Phone field configuration.
   * @returns {JSX.Element} Phone field row.
   * @collaboration R89C global Contacts SaaS, international phone persistence, operator-friendly CRM data entry.
   */
  function renderContactPhoneField({ label, field, countryField, placeholder = '82 000 0000' } = {}) {
    return (
      <label className={styles.contactPhoneField}>
        <span>{label}</span>
        <span className={styles.contactPhoneInputGroup}>
          <select
            value={contactDraft[countryField] || '+27'}
            onChange={event => handleContactDraftChange(countryField, event.target.value)}
            aria-label={`${label} country dial code`}
          >
            {CONTACT_PHONE_COUNTRY_OPTIONS.map(option => (
              <option key={`${field}-${option.iso}`} value={option.dialCode}>
                {option.iso} {option.dialCode}
              </option>
            ))}
          </select>
          <input
            type="tel"
            inputMode="tel"
            value={contactDraft[field] || ''}
            onChange={event => handleContactDraftChange(field, event.target.value)}
            placeholder={placeholder}
            aria-label={`${label} number`}
          />
        </span>
      </label>
    );
  }

  /**
   * @function renderContactComposer
   * @description Renders the backend-owned Contacts create composer inside the one-screen operating room.
   * @returns {JSX.Element|null} Contact composer modal.
   * @collaboration R86B CRMContact create route, guarded source payloads, no decorative local rows.
   */
  function renderContactComposer() {
    if (!contactComposerOpen) return null;

    const addressSuggestions = Array.isArray(contactDraft.addressSuggestions) ? contactDraft.addressSuggestions : [];
    const addressPacket = buildContactAddressVerificationPacket(contactDraft);

    return (
      <section className={styles.contactComposerOverlay} aria-label="Create source-backed contact">
        <form className={styles.contactComposerPanel} onSubmit={handleContactCreateSubmit}>
          <header>
            <span>
              <small>Backend Contact Command</small>
              <strong>Create Contact</strong>
              <em>{contactCommandStatus.message}</em>
            </span>
            <button type="button" onClick={closeContactComposer} aria-label="Close contact composer">
              X
            </button>
          </header>

          <section className={styles.contactComposerBody}>
            <section className={styles.contactComposerSection}>
              <h3>Contact Information</h3>
              <div className={styles.contactComposerGrid}>
                <label>
                  <span>Contact Owner</span>
                  <input
                    value={contactDraft.owner || ''}
                    onChange={event => handleContactDraftChange('owner', event.target.value)}
                    placeholder={user?.displayName || user?.name || 'Wilsy'}
                  />
                </label>
                <label>
                  <span>Lead Source</span>
                  <select value={contactDraft.leadSource} onChange={event => handleContactDraftChange('leadSource', event.target.value)}>
                    {CONTACT_LEAD_SOURCE_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label className={styles.contactComposerNameRow}>
                  <span>First Name</span>
                  <span className={styles.contactNameInputGroup}>
                    <select value={contactDraft.salutation} onChange={event => handleContactDraftChange('salutation', event.target.value)}>
                      {CONTACT_SALUTATION_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                    </select>
                    <input value={contactDraft.firstName || ''} onChange={event => handleContactDraftChange('firstName', event.target.value)} placeholder="First name" />
                  </span>
                </label>
                <label>
                  <span>Last Name *</span>
                  <input value={contactDraft.lastName || ''} onChange={event => handleContactDraftChange('lastName', event.target.value)} placeholder="Last name" required />
                </label>
                <label>
                  <span>Account Name *</span>
                  <input value={contactDraft.accountName || ''} onChange={event => handleContactDraftChange('accountName', event.target.value)} placeholder="Customer or company" required />
                </label>
                <label>
                  <span>Title</span>
                  <select value={contactDraft.title || ''} onChange={event => handleContactDraftChange('title', event.target.value)}>
                    {CONTACT_TITLE_OPTIONS.map(option => (
                      <option key={option || 'select-title'} value={option}>
                        {option || 'Select title'}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Department</span>
                  <select value={contactDraft.department || ''} onChange={event => handleContactDraftChange('department', event.target.value)}>
                    {CONTACT_DEPARTMENT_OPTIONS.map(option => (
                      <option key={option || 'select-department'} value={option}>
                        {option || 'Select department'}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>Relationship Role</span>
                  <input value={contactDraft.role || ''} onChange={event => handleContactDraftChange('role', event.target.value)} placeholder="Decision maker, buyer, champion" />
                </label>
              </div>
            </section>

            <section className={styles.contactComposerSection}>
              <h3>Email and Phone Details</h3>
              <div className={styles.contactComposerGrid}>
                <label>
                  <span>Email</span>
                  <input type="email" value={contactDraft.email || ''} onChange={event => handleContactDraftChange('email', event.target.value)} placeholder="name@company.com" />
                </label>
                <label>
                  <span>Secondary Email</span>
                  <input type="email" value={contactDraft.secondaryEmail || ''} onChange={event => handleContactDraftChange('secondaryEmail', event.target.value)} placeholder="alternate@company.com" />
                </label>
                {renderContactPhoneField({ label: 'Phone', field: 'phone', countryField: 'phoneCountryCode' })}
                {renderContactPhoneField({ label: 'Mobile', field: 'mobile', countryField: 'mobileCountryCode' })}
                {renderContactPhoneField({ label: 'Home Phone', field: 'homePhone', countryField: 'homePhoneCountryCode', placeholder: '11 000 0000' })}
                {renderContactPhoneField({ label: 'Other Phone', field: 'otherPhone', countryField: 'otherPhoneCountryCode', placeholder: '21 000 0000' })}
                {renderContactPhoneField({ label: 'Fax', field: 'fax', countryField: 'faxCountryCode', placeholder: '11 000 0001' })}
                <label>
                  <span>Date of Birth</span>
                  <input type="date" value={contactDraft.dateOfBirth || ''} onChange={event => handleContactDraftChange('dateOfBirth', event.target.value)} />
                </label>
                <label>
                  <span>Assistant</span>
                  <input value={contactDraft.assistant || ''} onChange={event => handleContactDraftChange('assistant', event.target.value)} />
                </label>
                {renderContactPhoneField({ label: 'Asst Phone', field: 'assistantPhone', countryField: 'assistantPhoneCountryCode', placeholder: '82 000 0000' })}
                <label>
                  <span>Consent Status</span>
                  <select value={contactDraft.consentStatus} onChange={event => handleContactDraftChange('consentStatus', event.target.value)}>
                    <option value="PENDING">Pending</option>
                    <option value="VERIFIED">Verified</option>
                    <option value="REVOKED">Revoked</option>
                  </select>
                </label>
                <label className={styles.contactComposerCheckbox}>
                  <input type="checkbox" checked={Boolean(contactDraft.emailOptOut)} onChange={event => handleContactDraftChange('emailOptOut', event.target.checked)} />
                  <span>Email Opt Out</span>
                </label>
              </div>
            </section>

            <section className={styles.contactComposerSection}>
              <h3>Address Intelligence</h3>
              <section
                className={styles.contactAddressCommandDeck}
                aria-label="Wilsy OS contact address intelligence"
                data-wilsy-ai-component="create-lead-address-intelligence"
                data-wilsy-contact-address-contract="R87C-REUSED-ADDRESS-INTELLIGENCE"
              >
                <label className={styles.contactAddressCommandSearch}>
                  <span>Type address here</span>
                  <input
                    value={contactDraft.addressSearch || contactDraft.formattedAddress || contactDraft.mailingStreet || ''}
                    placeholder="Type address here, for example 53 Rivonia Road, Sandton"
                    onChange={event => handleContactAddressSearch(event.target.value)}
                    aria-label="Type contact address for address intelligence"
                    autoComplete="street-address"
                  />
                  <small className={styles.contactFieldHint}>
                    Start typing a street address. Spaces are kept while you type; verified suggestions appear below.
                  </small>
                </label>
                <div className={styles.contactAddressEvidenceStrip}>
                  <span>{addressPacket.status}</span>
                  <span>{addressPacket.provider}</span>
                  <span>{addressPacket.confidenceLabel}</span>
                  <span>{addressPacket.receipt}</span>
                </div>
                {addressSuggestions.length ? (
                  <div className={styles.contactAddressSuggestionRail}>
                    {addressSuggestions.map(suggestion => (
                      <button
                        type="button"
                        key={suggestion.id || suggestion.formattedAddress}
                        className={styles.contactAddressSuggestionCard}
                        onClick={() => handleContactAddressSuggestionSelect(suggestion)}
                      >
                        <small>{suggestion.label || 'Address candidate'}</small>
                        <strong>{suggestion.formattedAddress}</strong>
                        <span>{formatContactAddressProviderLabel(suggestion.provider)} · {formatContactAddressConfidenceLabel(suggestion.confidence)} · {formatContactAddressStatusLabel(suggestion.verificationStatus)}</span>
                        <em>{suggestion.territory || 'Territory pending'}</em>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className={styles.contactAddressManualFallback}>
                    Type at least three characters to search live address providers through Wilsy backend.
                  </div>
                )}
              </section>
            </section>

            <section className={styles.contactComposerSection}>
              <header className={styles.contactComposerSectionHeader}>
                <h3>Address Information</h3>
                <button type="button" onClick={handleCopyMailingAddressToOther}>
                  <Copy size={15} />
                  Copy Address
                </button>
              </header>
              <div className={styles.contactAddressGrid}>
                <section>
                  <strong>Mailing Address</strong>
                  <label><span>Mailing Street</span><input value={contactDraft.mailingStreet || ''} onChange={event => handleContactDraftChange('mailingStreet', event.target.value)} /></label>
                  <label><span>Mailing City</span><input value={contactDraft.mailingCity || ''} onChange={event => handleContactDraftChange('mailingCity', event.target.value)} /></label>
                  <label><span>Mailing State</span><input value={contactDraft.mailingState || ''} onChange={event => handleContactDraftChange('mailingState', event.target.value)} /></label>
                  <label><span>Mailing Zip</span><input value={contactDraft.mailingZip || ''} onChange={event => handleContactDraftChange('mailingZip', event.target.value)} /></label>
                  <label><span>Mailing Country</span><input value={contactDraft.mailingCountry || ''} onChange={event => handleContactDraftChange('mailingCountry', event.target.value)} /></label>
                </section>
                <section>
                  <strong>Other Address</strong>
                  <label><span>Other Street</span><input value={contactDraft.otherStreet || ''} onChange={event => handleContactDraftChange('otherStreet', event.target.value)} /></label>
                  <label><span>Other City</span><input value={contactDraft.otherCity || ''} onChange={event => handleContactDraftChange('otherCity', event.target.value)} /></label>
                  <label><span>Other State</span><input value={contactDraft.otherState || ''} onChange={event => handleContactDraftChange('otherState', event.target.value)} /></label>
                  <label><span>Other Zip</span><input value={contactDraft.otherZip || ''} onChange={event => handleContactDraftChange('otherZip', event.target.value)} /></label>
                  <label><span>Other Country</span><input value={contactDraft.otherCountry || ''} onChange={event => handleContactDraftChange('otherCountry', event.target.value)} /></label>
                </section>
              </div>
            </section>

            <section className={styles.contactComposerSection}>
              <h3>Description Information</h3>
              <label className={styles.contactDescriptionField}>
                <span>Type relationship notes here</span>
                <textarea
                  value={contactDraft.description || ''}
                  onChange={event => handleContactDraftChange('description', event.target.value)}
                  placeholder="Type notes here: relationship context, source proof, outreach posture, consent notes..."
                  aria-label="Type contact relationship notes"
                />
                <small className={styles.contactFieldHint}>
                  Use this text area for relationship context, source evidence, consent notes and outreach instructions.
                </small>
              </label>
            </section>
          </section>

          <footer>
            <span>
              <Database size={14} />
              {contactCommandStatus.status}
            </span>
            <button type="button" onClick={closeContactComposer}>
              Cancel
            </button>
            <button type="submit" disabled={contactCommandBusy}>
              <Plus size={15} />
              {contactCommandBusy ? 'Saving' : 'Save'}
            </button>
          </footer>
        </form>
      </section>
    );
  }

  /**
   * @function renderContactMetrics
   * @description Renders relationship, consent, account and proof telemetry.
   * @returns {JSX.Element} Contact metrics deck.
   * @collaboration R76C Contacts command surface, Wilsy OS operating metrics, source proof.
   */
  function renderContactMetrics() {
    return (
      <section className={styles.contactMetricDeck} aria-label="Contacts operating metrics">
        {contactMetrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <article key={metric.id}>
              <span className={styles.contactMetricIcon}>
                <Icon size={20} />
              </span>
              <span className={styles.contactMetricCopy}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
                <em>{metric.detail}</em>
              </span>
              <i className={styles.contactMetricBar}>
                <b style={{ width: `${metric.progress}%` }} />
              </i>
            </article>
          );
        })}
      </section>
    );
  }

  /**
   * @function renderFilterRail
   * @description Renders Contacts list views and relationship filters.
   * @returns {JSX.Element|null} Filter rail.
   * @collaboration R76C Contacts filtering, Zoho parity, Wilsy relationship intelligence.
   */
  function renderFilterRail() {
    if (!filterRailOpen) {
      return (
        <aside
          className={styles.contactFilterRailCollapsed}
          data-wilsy-contact-filter-restore="R85A-FILTER-RESTORE"
          aria-label="Contact filters collapsed"
        >
          <button
            type="button"
            onClick={() => setFilterRailOpen(previous => !previous)}
            aria-label="Show Contact filters"
            title="Show filters"
          >
            <Filter size={17} />
            <span>Show filters</span>
          </button>
        </aside>
      );
    }

    return (
      <aside
        className={styles.contactFilterRail}
        data-wilsy-contact-filter-operating-system="R85A-INDEPENDENT-SCROLL"
        aria-label="Contact filters"
      >
        <header>
          <span>
            <small>Filter Contacts by</small>
            <strong>Relationship Signals</strong>
          </span>
          <button type="button" onClick={() => setFilterRailOpen(false)} aria-label="Collapse Contact filters" title="Collapse filters">
            <MoreHorizontal size={17} />
          </button>
        </header>

        <label className={styles.contactFilterSearch}>
          <Search size={18} />
          <input
            value={searchQuery}
            onChange={event => setSearchQuery(event.target.value)}
            placeholder="Search filters"
            aria-label="Search contact filters"
          />
        </label>

        <div
          className={styles.contactFilterScroll}
          data-wilsy-independent-scroll="contact-filter-options"
        >
          {CONTACT_FILTER_GROUPS.map(group => (
            <section key={group.id} className={styles.contactFilterGroup}>
              <strong>{group.label}</strong>
              {group.options.map((option) => {
                const signalFilter = resolveContactSignalFilter(option);
                const isActive = activeSignalFilter === signalFilter.id;

                return (
                  <button
                    key={option}
                    type="button"
                    data-active={isActive ? 'true' : 'false'}
                    onClick={() => handleSignalFilterToggle(signalFilter.id)}
                  >
                    <span aria-hidden="true" />
                    <em>{option}</em>
                  </button>
                );
              })}
            </section>
          ))}
        </div>
      </aside>
    );
  }

  /**
   * @function renderRecordsTab
   * @description Renders the source-backed Contacts records cockpit.
   * @returns {JSX.Element} Records tab.
   * @collaboration R76C Contacts list cockpit, consent-aware rows, source-honest empty state.
   */
  function renderRecordsTab() {
    return (
      <section
        className={styles.contactRecordsWorkspace}
        data-wilsy-contact-records="relationship-list-view"
        data-wilsy-contact-listview-shell="R85A-LEADS-PARITY"
        data-wilsy-filter-state={filterRailOpen ? 'open' : 'closed'}
        data-wilsy-contact-row-count={filteredContacts.length}
      >
        {renderFilterRail()}

        <section className={styles.contactRecordsPanel}>
          <header className={styles.contactRecordsHeader}>
            <span>
              <small>{activeView.label}</small>
              <strong>{filteredContacts.length} contacts</strong>
              <em>{selectedRowIds.length ? `${selectedRowIds.length} selected` : `${activeSort.label} order · ${activeSignalFilterLabel}`}</em>
            </span>

            <div>
              {!filterRailOpen ? (
                <button type="button" onClick={() => setFilterRailOpen(previous => !previous)}>
                  <Filter size={15} />
                  Filters
                </button>
              ) : null}
              <button type="button" onClick={onRefresh}>
                <RefreshCcw size={15} className={loading ? styles.spin : ''} />
                Refresh
              </button>
              <button type="button" onClick={handleContactExport} disabled={contactCommandBusy}>
                <Download size={15} />
                Export
              </button>
            </div>
          </header>

          {renderContactBackendStatus()}

          {selectedRowIds.length ? (
            <section className={styles.contactBulkActionBar} aria-label="Contact bulk actions">
              <strong>{selectedRowIds.length} selected</strong>
              <button type="button"><Mail size={14} />Mass Email</button>
              <button type="button"><Shield size={14} />Consent Review</button>
              <button type="button"><Building2 size={14} />Link Account</button>
              <button type="button" onClick={() => setSelectedRowIds([])}>Clear</button>
            </section>
          ) : null}

          <div className={styles.contactRecordsTableFrame}>
            <table className={styles.contactRecordsTable}>
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      aria-label="Select all visible contacts"
                      checked={allRowsSelected}
                      onChange={handleToggleAllContactSelection}
                    />
                  </th>
                  <th>Contact Name</th>
                  <th>Account Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Title</th>
                  <th>Consent</th>
                  <th>Score</th>
                  <th>Next Action</th>
                  <th>Owner</th>
                  <th aria-label="Row actions" />
                </tr>
              </thead>
              <tbody>
                {paginatedContacts.length ? paginatedContacts.map((record, index) => {
                  const recordId = resolveContactId(record, contactPagination.startIndex + index);
                  const score = resolveContactScore(record);
                  const consent = resolveContactConsent(record);
                  const emailHref = resolveContactHref(record, 'email');
                  const phoneHref = resolveContactHref(record, 'phone');
                  const nextAction = resolveContactNextAction(record);

                  return (
                    <tr key={recordId} data-selected={selectedRowIds.includes(recordId) ? 'true' : 'false'}>
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Select ${resolveContactValue(record, 'name')}`}
                          checked={selectedRowIds.includes(recordId)}
                          onChange={() => handleToggleContactSelection(recordId)}
                        />
                      </td>
                      <td>
                        <button type="button" className={styles.contactNameCell}>
                          <strong>{resolveContactValue(record, 'name')}</strong>
                          <em>{resolveContactStatus(record)} · {resolveContactSource(record)}</em>
                        </button>
                      </td>
                      <td>{resolveContactValue(record, 'accountName')}</td>
                      <td>
                        {emailHref ? <a href={emailHref}>{resolveContactValue(record, 'email')}</a> : resolveContactValue(record, 'email')}
                      </td>
                      <td>
                        {phoneHref ? <a href={phoneHref}>{resolveContactValue(record, 'phone')}</a> : resolveContactValue(record, 'phone')}
                      </td>
                      <td>{resolveContactValue(record, 'title')}</td>
                      <td>
                        <span className={styles[`contactStatus${consent}`] || styles.contactStatusPENDING}>
                          {consent}
                        </span>
                      </td>
                      <td>
                        <span className={styles.contactScorePill}>{resolveContactBand(score)} · {score}</span>
                      </td>
                      <td>
                        <span className={styles.contactActionPill}>{nextAction}</span>
                      </td>
                      <td>{resolveContactValue(record, 'owner')}</td>
                      <td className={styles.contactRowActionsCell}>
                        <button type="button" onClick={() => setOpenRowActionId(openRowActionId === recordId ? '' : recordId)} title="Contact actions">
                          <MoreHorizontal size={17} />
                        </button>
                        {openRowActionId === recordId ? (
                          <section className={styles.contactRowActionMenu} aria-label="Contact actions">
                            <a href={emailHref || undefined} onClick={(event) => { if (!emailHref) event.preventDefault(); }}>Send Email</a>
                            <a href={phoneHref || undefined} onClick={(event) => { if (!phoneHref) event.preventDefault(); }}>Call Contact</a>
                            <button type="button">Consent Review</button>
                            <button type="button">Link Account</button>
                            <button type="button">Open Proof Trail</button>
                          </section>
                        ) : null}
                      </td>
                    </tr>
                  );
                }) : (
                  <tr className={styles.contactEmptyRow}>
                    <td colSpan={11}>
                      <section>
                        <Database size={34} />
                        <span>
                          <strong>No live contact records in this view yet.</strong>
                          <em>Sync relationship sources, import verified contacts, or create a governed contact. WILSY OS will surface consent, account linkage and proof posture as soon as records arrive.</em>
                        </span>
                        <div>
                          <button type="button" onClick={onRefresh} disabled={loading}>
                            <RefreshCcw size={15} />
                            Sync Sources
                          </button>
                          <button type="button" onClick={openContactComposer}>
                            <Plus size={15} />
                            Create Contact
                          </button>
                        </div>
                      </section>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <footer className={styles.contactRecordsFooter}>
            <span>Total Records <strong>{filteredContacts.length}</strong></span>
            <em>
              {filteredContacts.length
                ? `Showing ${contactPagination.startRecord} to ${contactPagination.endRecord} of ${filteredContacts.length} contacts`
                : 'Showing 0 contacts'}
            </em>
            <section className={styles.contactFooterPagination} aria-label="Contact records pagination">
              <button type="button" disabled={!contactPagination.hasPrevious} onClick={() => setContactPage(1)}>|&lt;</button>
              <button type="button" disabled={!contactPagination.hasPrevious} onClick={() => setContactPage(page => Math.max(1, page - 1))}>&lt;</button>
              <strong>{contactPagination.currentPage}</strong>
              <button type="button" disabled={!contactPagination.hasNext} onClick={() => setContactPage(page => Math.min(contactPagination.totalPages, page + 1))}>&gt;</button>
              <button type="button" disabled={!contactPagination.hasNext} onClick={() => setContactPage(contactPagination.totalPages)}>&gt;|</button>
              <select value={contactPageSize} onChange={event => setContactPageSize(Number(event.target.value))}>
                {CONTACT_PAGE_SIZE_OPTIONS.map(option => (
                  <option key={option} value={option}>{option} / page</option>
                ))}
              </select>
            </section>
          </footer>
        </section>
      </section>
    );
  }

  /**
   * @function renderRelationshipTab
   * @description Renders contact-account-deal relationship graph intelligence.
   * @returns {JSX.Element} Relationship tab.
   * @collaboration R76C Contacts relationship graph, account linkage, deal influence intelligence.
   */
  function renderRelationshipTab() {
    const linkedContacts = filteredContacts.filter(record => isKnownContactValue(resolveContactValue(record, 'accountName')));

    return (
      <section className={styles.contactTabSurface} data-contact-tab="relationships">
        <section className={styles.relationshipGrid}>
          <article className={styles.relationshipPanel}>
            <header>
              <small>Relationship Graph</small>
              <strong>{linkedContacts.length}/{filteredContacts.length} account-linked</strong>
            </header>
            <div className={styles.relationshipNodeGrid}>
              {filteredContacts.slice(0, 12).map((record, index) => (
                <span key={resolveContactId(record, index)} data-linked={isKnownContactValue(resolveContactValue(record, 'accountName')) ? 'true' : 'false'}>
                  <UserRound size={15} />
                  <em>{resolveContactValue(record, 'name')}</em>
                  <b>{resolveContactValue(record, 'accountName')}</b>
                </span>
              ))}
            </div>
          </article>

          <article className={styles.relationshipPanel}>
            <header>
              <small>Influence Posture</small>
              <strong>{deals.length || 0} deal links</strong>
            </header>
            <p>Contacts become operating graph nodes: account influence, deal motion, support posture, consent, and evidence all stay visible in one relationship cockpit.</p>
            <div className={styles.relationshipStats}>
              <span><Building2 size={16} />{accounts.length || 0} accounts</span>
              <span><GitBranch size={16} />{deals.length || 0} deals</span>
              <span><FileCheck2 size={16} />{evidence.length || 0} proof anchors</span>
            </div>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderConsentTab
   * @description Renders consent, communication readiness and compliance posture.
   * @returns {JSX.Element} Consent tab.
   * @collaboration R76C Contacts compliance HUD, POPIA/GDPR posture, communication authority.
   */
  function renderConsentTab() {
    const verified = filteredContacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length;
    const pending = filteredContacts.filter(record => resolveContactConsent(record) === 'PENDING').length;
    const revoked = filteredContacts.filter(record => resolveContactConsent(record) === 'REVOKED').length;

    return (
      <section className={styles.contactTabSurface} data-contact-tab="consent">
        <section className={styles.consentGrid}>
          <article className={styles.consentPanel}>
            <Shield size={24} />
            <span>
              <small>Communication Authority</small>
              <strong>{verified}/{filteredContacts.length} verified</strong>
              <em>POPIA · GDPR · SOC2 contact communication posture.</em>
            </span>
          </article>
          <article className={styles.consentPanel}>
            <AlertTriangle size={24} />
            <span>
              <small>Review Queue</small>
              <strong>{pending} pending · {revoked} revoked</strong>
              <em>Contacts without clear consent stay visible before outreach.</em>
            </span>
          </article>
          <article className={styles.consentPanel}>
            <CheckCircle2 size={24} />
            <span>
              <small>Evidence Chain</small>
              <strong>{evidence.length || 0} anchors</strong>
              <em>Consent and source receipts belong to the contact graph.</em>
            </span>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderSourcesTab
   * @description Renders source route and connector posture for Contacts.
   * @returns {JSX.Element} Sources tab.
   * @collaboration R76C Contacts source proof, connector readiness, migration parity.
   */
  function renderSourcesTab() {
    return (
      <section className={styles.contactTabSurface} data-contact-tab="sources">
        <section className={styles.sourceGrid}>
          <article className={styles.sourcePanel}>
            <header>
              <small>Source Routes</small>
              <strong>{sourceRouteConnected}/{sourceRouteTotal}</strong>
            </header>
            <p>{sourceErrors.length ? `${sourceErrors.length} source route gaps detected.` : 'Contacts source posture is monitored.'}</p>
            <button type="button" onClick={onRefresh}>
              <RefreshCcw size={15} />
              Sync Sources
            </button>
          </article>

          <article className={styles.sourcePanel}>
            <header>
              <small>Connector Matrix</small>
              <strong>{connectors.length || 0}</strong>
            </header>
            <div className={styles.connectorMatrix}>
              {connectors.length ? connectors.slice(0, 10).map((connector, index) => (
                <span key={connector.id || connector.key || connector.name || `connector-${index}`}>
                  <Network size={14} />
                  <em>{connector.label || connector.name || connector.key || 'Connector'}</em>
                  <b>{connector.status || connector.posture || 'WATCH'}</b>
                </span>
              )) : (
                <span>
                  <Network size={14} />
                  <em>No connector payload returned</em>
                  <b>GATED</b>
                </span>
              )}
            </div>
          </article>
        </section>
      </section>
    );
  }

  /**
   * @function renderTabContent
   * @description Resolves the active Contacts tab content.
   * @returns {JSX.Element} Active tab content.
   * @collaboration R76C Contacts tabbed workspace, Leads-grade operating principles, CRM OS consistency.
   */
  function renderTabContent() {
    if (activeTopTab === 'relationships') return renderRelationshipTab();
    if (activeTopTab === 'consent') return renderConsentTab();
    if (activeTopTab === 'sources') return renderSourcesTab();

    return renderRecordsTab();
  }

  return (
    <section
      className={styles.contactOperatingRoom}
      data-wilsy-crm-visual-contract="R78B-UNIFIED-CRM-SHELL"
      data-wilsy-contact-operating-room="R76C-CONTACTS-OPERATING-ROOM"
      data-wilsy-contact-module="relationship-intelligence"
      data-wilsy-contact-canvas-parity="LEADS_FULL_CANVAS_R76E"
      data-wilsy-contact-section-map="header-command-intelligence-tabs-metrics-records-backend"
    >
      <header className={styles.contactAppHeader}>
        <section className={styles.contactHeaderPrimary}>
          <span className={styles.contactTitleBlock}>
            <small>Customer Relationships</small>
            <strong>Contacts</strong>
            <em>{tenantLabel} · Relationship workspace · consent and source records monitored</em>
          </span>

          <section className={styles.contactHeaderUtilities}>
            <button type="button" className={styles.contactIconButton} onClick={onRefresh} aria-label="Refresh contacts">
              <RefreshCcw size={18} className={loading ? styles.spin : ''} />
            </button>
            <button type="button" className={styles.contactIconButton} aria-label="Open calendar">
              <CalendarDays size={18} />
            </button>
            <button type="button" className={styles.contactIconButton} aria-label="Contact settings">
              <SlidersHorizontal size={18} />
            </button>
            <button
              type="button"
              className={styles.contactThemeAuthority}
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
          </section>
        </section>

        <section className={styles.contactCommandRow}>
          <label className={styles.contactSearch}>
            <Search size={19} />
            <input
              value={searchQuery}
              onChange={event => setSearchQuery(event.target.value)}
              placeholder="Search contacts, accounts, consent, email, phone"
              aria-label="Search contacts"
            />
            <kbd>⌘K</kbd>
          </label>

          <section className={styles.contactToolbar}>
            <div className={styles.contactListViewWrap}>
              <button type="button" className={styles.contactViewButton}>
                <Users size={17} />
                <span>
                  <strong>{activeView.label}</strong>
                  <em>{activeView.detail}</em>
                </span>
                <ChevronDown size={15} />
              </button>
              <section className={styles.contactDropdownMenu} aria-label="Contact list views">
                {CONTACT_LIST_VIEWS.map(view => (
                  <button
                    key={view.id}
                    type="button"
                    data-active={view.id === activeListView ? 'true' : 'false'}
                    onClick={() => setActiveListView(view.id)}
                  >
                    <span>{view.label}</span>
                    <em>{view.detail}</em>
                  </button>
                ))}
              </section>
            </div>

            <button type="button" data-active={filterRailOpen ? 'true' : 'false'} onClick={() => setFilterRailOpen(value => !value)}>
              <Filter size={17} />
              Filter
            </button>

            <div className={styles.contactSortWrap}>
              <button type="button" onClick={() => setSortMenuOpen(value => !value)}>
                <SlidersHorizontal size={17} />
                Sort
                <ChevronDown size={15} />
              </button>
              {sortMenuOpen ? (
                <section className={styles.contactDropdownMenu} aria-label="Contact sort options">
                  {CONTACT_SORT_OPTIONS.map(option => (
                    <button
                      key={option.id}
                      type="button"
                      data-active={option.id === sortMode ? 'true' : 'false'}
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

            <label className={styles.contactInsightWrap}>
              <Database size={17} />
              <select defaultValue="INSIGHTS" aria-label="Contacts insights">
                <option value="INSIGHTS">Insights</option>
                {contactMetrics.map(metric => (
                  <option key={metric.id} value={metric.id}>
                    {metric.label}: {metric.value} · {metric.progress}%
                  </option>
                ))}
              </select>
            </label>

            <button type="button" className={styles.contactPrimaryAction} onClick={openContactComposer} disabled={contactCommandBusy}>
              <Plus size={17} />
              Create Contact
            </button>
          </section>
        </section>

        {renderContactCommandStrip()}

        <section className={styles.contactTabBar}>
          <div className={styles.contactTabs}>
            {CONTACT_TOP_TABS.map(tab => {
              const Icon = tab.icon;

              return (
                <button
                  key={tab.id}
                  type="button"
                  data-active={activeTopTab === tab.id ? 'true' : 'false'}
                  onClick={() => setActiveTopTab(tab.id)}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <section className={styles.contactInvestorStrip}>
            <article>
              <small>Source Routes</small>
              <strong>{sourceRouteConnected}/{sourceRouteTotal}</strong>
              <em>Source readiness</em>
            </article>
            <article>
              <small>Relationship Root</small>
              <strong>{String(sourcePosture.rootHash || sourcePosture.hash || 'UNSEALED').slice(0, 12)}</strong>
              <em>PROVENANCE</em>
            </article>
            <article>
              <small>Consent</small>
              <strong>{filteredContacts.filter(record => resolveContactConsent(record) === 'VERIFIED').length}/{filteredContacts.length}</strong>
              <em>POPIA · GDPR · SOC2</em>
            </article>
            <article>
              <small>Graph Authority</small>
              <strong>{accounts.length || deals.length ? 'ONLINE' : 'WATCH'}</strong>
              <em>ACCOUNT · DEAL · PROOF</em>
            </article>
          </section>
        </section>
      </header>

      {sourceErrors.length ? (
        <section className={styles.contactSourceWarning}>
          <AlertTriangle size={18} />
          <span>{sourceErrors.length} source route{sourceErrors.length === 1 ? '' : 's'} unavailable. Showing received contacts only.</span>
        </section>
      ) : null}
      {renderTabContent()}
      {renderContactComposer()}
    </section>
  );
}
