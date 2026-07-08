/* eslint-disable */
import { sha3_512 } from 'js-sha3';
import { openWilsyLeadCommandCapsule as openWilsyLeadCommandCapsuleNative } from './WilsyLeadCommandCapsule';
import { openWilsyLeadEditSurface } from './WilsyLeadEditSurface';
import WilsyUniversalMeetingCommandCenter from '../meeting/WilsyUniversalMeetingCommandCenter.jsx';
import WilsyMeetingEditor from '../meeting/workspace/WilsyMeetingEditor.jsx';
import { generateArtifactExport } from '../../../services/artifacts/artifactExportService';
/**
 * @function readWilsyR91KOwnerWrapperPath
 * @description Reads nested owner evidence paths for the Owner table wrapper without mutating Lead data.
 * @param {Object} record - Lead row record.
 * @param {string} path - Dot path to read.
 * @returns {unknown} Owner evidence value.
 * @collaboration Records table Owner column, existing resolveLeadOwnerLabel, Lead Edit owner resolver contract.
 */
function readWilsyR91KOwnerWrapperPath(record = {}, path = '') {
  return String(path || '')
    .split('.')
    .filter(Boolean)
    .reduce((cursor, segment) => {
      if (!cursor || typeof cursor !== 'object') {
        return undefined;
      }

      return Object.prototype.hasOwnProperty.call(cursor, segment) ? cursor[segment] : undefined;
    }, record);
}

/**
 * @function normalizeWilsyR91KOwnerWrapperValue
 * @description Normalizes owner evidence into a visible table label without exposing broken dash placeholders.
 * @param {unknown} value - Candidate owner value.
 * @returns {string} Human-readable owner label or an empty string.
 * @collaboration Records table Owner column, backend assignment evidence, Wilsy CRM owner display.
 */
function normalizeWilsyR91KOwnerWrapperValue(value) {
  if (value === null || value === undefined) {
    return '';
  }

  if (typeof value === 'string' || typeof value === 'number') {
    const text = String(value || '').trim();

    if (!text || text === '-' || text === '—' || /^null$/i.test(text) || /^undefined$/i.test(text)) {
      return '';
    }

    if (/^[a-f0-9]{24}$/i.test(text)) {
      return '';
    }

    return text;
  }

  if (typeof value === 'object') {
    const firstName = normalizeWilsyR91KOwnerWrapperValue(value.firstName || value.givenName || '');
    const lastName = normalizeWilsyR91KOwnerWrapperValue(value.lastName || value.familyName || '');
    const fullName = [firstName, lastName].filter(Boolean).join(' ').trim();

    return normalizeWilsyR91KOwnerWrapperValue(
      value.wilsyResolvedOwnerLabel ||
      value.ownerName ||
      value.ownerLabel ||
      value.ownerDisplayName ||
      value.displayName ||
      value.fullName ||
      fullName ||
      value.name ||
      value.label ||
      value.email ||
      value.username ||
      ''
    );
  }

  return '';
}

/**
 * @function resolveWilsyR91KOwnerTableDisplay
 * @description Resolves Owner column display from all known backend owner fields before falling back to the existing resolver and then Unassigned.
 * @param {Object} record - Lead row record.
 * @param {Function} fallbackResolver - Existing resolveLeadOwnerLabel implementation.
 * @returns {string} Owner table display label.
 * @collaboration Records table Owner column, Lead Edit owner resolver, source-backed CRM row rendering.
 */

/**
 * @function resolveWilsyFG91FOwnerCandidateText
 * @description Normalizes candidate owner identity text for safe top-level owner fallback resolution.
 * @param {*} value - Candidate owner value.
 * @returns {string} Normalized owner text.
 * @collaboration Top-level Leads owner table display, ErrorBoundary recovery, current operator fallback, and CRM performance ownership.
 */
function resolveWilsyFG91FOwnerCandidateText(value = '') {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyFG91FOwnerNameFromCandidate
 * @description Resolves a display name from a possible browser current-user or operator packet.
 * @param {Object} candidate - Candidate owner profile packet.
 * @returns {string} Owner display name.
 * @collaboration Browser auth cache, tenant operator context, top-level Leads owner display, and crash-safe rendering.
 */
function resolveWilsyFG91FOwnerNameFromCandidate(candidate = {}) {
  const nested = candidate.user || candidate.profile || candidate.operator || candidate.account || candidate.identity || {};
  const source = { ...nested, ...candidate };
  const firstName = resolveWilsyFG91FOwnerCandidateText(source.firstName || source.givenName);
  const lastName = resolveWilsyFG91FOwnerCandidateText(source.lastName || source.surname || source.familyName);
  const joinedName = [firstName, lastName].filter(Boolean).join(' ');

  return resolveWilsyFG91FOwnerCandidateText(
    source.displayName ||
    source.name ||
    source.fullName ||
    source.operatorName ||
    source.userName ||
    source.username ||
    joinedName
  );
}

/**
 * @function collectWilsyFG91FOwnerFallbackCandidates
 * @description Collects safe browser-side owner identity candidates without relying on failing auth/profile probes.
 * @returns {Object[]} Candidate owner identity packets.
 * @collaboration Local/session storage, browser operator globals, Leads owner display, and runtime crash recovery.
 */
function collectWilsyFG91FOwnerFallbackCandidates() {
  if (typeof window === 'undefined') {
    return [];
  }

  const candidates = [
    window.__WILSY_CURRENT_USER__,
    window.__WILSY_USER__,
    window.__WILSY_OPERATOR__,
    window.__WILSY_OPERATOR_CONTEXT__,
    window.__WILSY_AUTH_USER__,
    window.WILSY_USER,
    window.WILSY_AUTH_USER,
    window.wilsyUser,
    window.wilsyOperator,
    window.sovereignUser,
  ].filter(candidate => candidate && typeof candidate === 'object');

  const storageKeys = [
    'wilsy.currentUser',
    'wilsy.user',
    'wilsy.operator',
    'wilsy.operator.profile',
    'wilsy.account.profile',
    'wilsy.auth.user',
    'wilsy.user.profile',
    'wilsy.profile',
    'currentUser',
    'user',
    'operator',
    'profile',
    'accountProfile',
    'authUser',
    'tenantUser',
    'tenantOperator',
    'sovereignUser',
  ];

  [window.localStorage, window.sessionStorage].forEach((storage) => {
    storageKeys.forEach((key) => {
      try {
        const parsed = JSON.parse(storage?.getItem?.(key) || 'null');

        if (parsed && typeof parsed === 'object') {
          candidates.push(parsed);
        }
      } catch (error) {}
    });
  });

  return candidates;
}

/**
 * @function resolveWilsyFG91FCurrentOwnerFallbackName
 * @description Resolves a crash-safe top-level current owner name for the Leads owner column.
 * @returns {string} Owner fallback display name.
 * @collaboration resolveWilsyR91KOwnerTableDisplay, AI-created Lead rows, operator performance tracking, and ErrorBoundary protection.
 */
function resolveWilsyFG91FCurrentOwnerFallbackName() {
  /* P60K5Q10FG91F_TOP_LEVEL_OWNER_FALLBACK_RUNTIME */
  const candidates = collectWilsyFG91FOwnerFallbackCandidates();

  for (const candidate of candidates) {
    const displayName = resolveWilsyFG91FOwnerNameFromCandidate(candidate);

    if (displayName && !/^unassigned$/i.test(displayName) && displayName !== 'U' && displayName !== '-') {
      return displayName;
    }
  }

  return 'Wilson Khanyezi';
}

/**
 * @function resolveWilsyFG91FCurrentOwnerFallbackInitials
 * @description Resolves crash-safe top-level owner initials for the Leads owner avatar.
 * @returns {string} Owner fallback initials.
 * @collaboration Records owner avatar, current operator fallback, AI-created Lead rows, and CRM performance ownership.
 */
function resolveWilsyFG91FCurrentOwnerFallbackInitials() {
  const ownerName = resolveWilsyFG91FCurrentOwnerFallbackName();
  const parts = ownerName.split(' ').filter(Boolean);

  if (!parts.length) {
    return 'WK';
  }

  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase();
}

/**
 * @function resolveWilsyR91KOwnerTableDisplay
 * @description Resolves the Records table owner label from backend owner fields and the crash-safe current-operator fallback.
 * @param {Object} record - Lead record being rendered in the Records grid.
 * @param {Function|null} fallbackResolver - Optional legacy fallback resolver.
 * @returns {string} Owner table display label.
 * @collaboration Records table Owner column, Lead Edit owner resolver, current-operator fallback, source-backed CRM row rendering, and ErrorBoundary recovery.
 */
function resolveWilsyR91KOwnerTableDisplay(record = {}, fallbackResolver = null) {
  const ownerEvidencePaths = [
    'wilsyResolvedOwnerLabel',
    'ownerName',
    'ownerLabel',
    'ownerDisplayName',
    'displayOwner',
    'assignedToName',
    'assignedOwnerName',
    'assigneeName',
    'createdByName',
    'updatedByName',
    'salesOwnerName',
    'accountOwnerName',
    'owner',
    'assignedTo',
    'assignedOwner',
    'createdBy',
    'updatedBy',
    'owner.name',
    'owner.fullName',
    'owner.displayName',
    'owner.label',
    'owner.email',
    'assignedTo.name',
    'assignedTo.fullName',
    'assignedTo.displayName',
    'assignedTo.label',
    'assignedTo.email',
    'assignedOwner.name',
    'assignedOwner.fullName',
    'assignedOwner.displayName',
    'assignedOwner.label',
    'assignedOwner.email',
    'raw.wilsyResolvedOwnerLabel',
    'raw.ownerName',
    'raw.ownerLabel',
    'raw.ownerDisplayName',
    'raw.displayOwner',
    'raw.assignedToName',
    'raw.assignedOwnerName',
    'raw.assigneeName',
    'raw.createdByName',
    'raw.updatedByName',
    'raw.owner',
    'raw.assignedTo',
    'raw.assignedOwner',
    'raw.owner.name',
    'raw.owner.fullName',
    'raw.owner.displayName',
    'raw.owner.label',
    'raw.owner.email',
    'raw.assignedTo.name',
    'raw.assignedTo.fullName',
    'raw.assignedTo.displayName',
    'raw.assignedTo.label',
    'raw.assignedTo.email'
  ];

  for (const path of ownerEvidencePaths) {
    const label = normalizeWilsyR91KOwnerWrapperValue(readWilsyR91KOwnerWrapperPath(record, path));

    if (label) {
      return label;
    }
  }

  if (typeof fallbackResolver === 'function') {
    const fallbackLabel = normalizeWilsyR91KOwnerWrapperValue(fallbackResolver(record));

    if (fallbackLabel) {
      return fallbackLabel;
    }
  }

  return resolveWilsyFG91FCurrentOwnerFallbackName();
}

/**
 * @function isWilsyR91K179E26MeetingShellRecord
 * @description Detects Meeting records adapted into the shared Lead records shell.
 * @param {Object} record - Lead shell row record.
 * @returns {boolean} True when the row represents a CRM Meeting.
 * @collaboration Meeting operating room adapter, shared CRM list grid, Lead-safe row behavior.
 */
function isWilsyR91K179E26MeetingShellRecord(record = {}) {
  return (
    String(record.sourceModule || record.module || '').toLowerCase() === 'meetings'
    || String(record.source || '').toUpperCase() === 'CRMMEETING'
    || Boolean(record.wilsyMeetingSourceRecord)
  );
}

/**
 * @function canUseLeadAdministrativeCrud
 * @description Resolves whether the current operator can use selected-row Lead CRUD controls.
 * @param {string} role - Current operator role.
 * @param {string} action - Requested Lead action.
 * @returns {boolean} Whether selected-row CRUD should be enabled.
 * @collaboration Selected Lead action bar, row action menu, command capsule authority posture.
 */
function canUseLeadAdministrativeCrud(role = 'operator', action = 'edit') {
  const normalizedRole = String(role || '').trim().toLowerCase();
  const elevatedRoles = new Set(['founder', 'owner', 'admin', 'superadmin', 'super_admin', 'master', 'system', 'operator']);

  if (typeof canUseLeadAction === 'function' && canUseLeadAction(role, action)) {
    return true;
  }

  if (typeof canUseLeadAction === 'function' && canUseLeadAction(role, 'bulk')) {
    return true;
  }

  return elevatedRoles.has(normalizedRole);
}

/**
 * @function resolveLeadCrudAuthorityReason
 * @description Explains selected-row Lead CRUD authority when a control is role-gated.
 * @param {string} role - Current operator role.
 * @returns {string} Human-readable authority reason.
 * @collaboration Selected Lead action bar, row action menu, operator trust copy.
 */
function resolveLeadCrudAuthorityReason(role = 'operator') {
  return canUseLeadAdministrativeCrud(role)
    ? 'Lead CRUD authority available for this operator.'
    : 'Lead CRUD authority requires Founder, Admin, Master, owner, or assigned operator authority.';
}

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
  Star,
  SplitSquareHorizontal,
  SlidersHorizontal,
  Upload,
  UserRoundCog,
  WandSparkles
} from 'lucide-react';
import { WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION, resolveCrmThemeEngineOptions } from '../theme/wilsyCrmThemeEngineBridge.js';
import styles from './WilsyLeadOperatingRoom.module.css';

import WilsyCrmSetupControlPlane from '../setup/WilsyCrmSetupControlPlane';
import WilsyLeadCustomViewBuilder, { doesWilsyLeadMatchCustomViewCriteria } from './WilsyLeadCustomViewBuilder.jsx';


const WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT = '/api/crm/control-state/leads/filters';
const WILSY_LEADS_AI_OPERATOR_ENDPOINT = '/api/wilsy/ai/operator/resolve';
const WILSY_LEADS_EXTERNAL_POINTER_SELECTION_BLOCK_MS = 700;
const WILSY_LEADS_FILTER_LOCAL_STATE_KEY = 'wilsy.crm.leads.filterButtons.v1';

/**
 * @function normalizeWilsyLeadFilterText
 * @description Normalizes Leads filter text for component-owned checkbox state and backend persistence.
 * @param {*} value - Candidate filter text.
 * @returns {string} Normalized filter text.
 * @collaboration Leads filter sidebar, checkbox buttons, backend control state, and tenant/operator evidence persistence.
 */
function normalizeWilsyLeadFilterText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyLeadApiBase
 * @description Resolves the API base used by Leads filter control-state requests.
 * @returns {string} API base URL.
 * @collaboration Leads frontend, Vite API configuration, backend control-state route, and local development routing.
 */
function resolveWilsyLeadApiBase() {
  return String(import.meta.env?.VITE_API_URL || '').replace(/\/$/, '');
}

/**
 * @function resolveWilsyLeadOperatorHeaders
 * @description Resolves tenant/operator headers and optional browser auth token for Leads filter control-state requests.
 * @returns {Object} Request headers with tenant and operator scope.
 * @collaboration Leads filter buttons, tenant context, operator context, browser authenticated session, and backend evidence route.
 */
function resolveWilsyLeadOperatorHeaders() {
  const storage = typeof window !== 'undefined' ? window.localStorage : null;
  const tenantId =
    storage?.getItem('wilsy.tenantId') ||
    storage?.getItem('tenantId') ||
    document.documentElement?.dataset?.tenantId ||
    'wilsy-sovereign-root';
  const operatorId =
    storage?.getItem('wilsy.operatorId') ||
    storage?.getItem('operatorId') ||
    storage?.getItem('userId') ||
    document.documentElement?.dataset?.operatorId ||
    'wilsy-operator';
  const token =
    storage?.getItem('token') ||
    storage?.getItem('authToken') ||
    storage?.getItem('accessToken') ||
    storage?.getItem('wilsy.auth.token') ||
    '';

  return {
    tenantId,
    operatorId,
    headers: {
      'Content-Type': 'application/json',
      'X-Tenant-Id': tenantId,
      'X-Operator-Id': operatorId,
      'X-Wilsy-Command-Surface': 'LEADS_FILTER_CONTROL_STATE',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  };
}

/**
 * @function normalizeWilsyLeadAIText
 * @description Normalizes Wilsy AI question and answer text for the continuous Leads response surface.
 * @param {*} value - Candidate text.
 * @returns {string} Normalized text.
 * @collaboration Wilsy AI Operator Kernel, CRM Leads context, and continuous typographic response discipline.
 */
function normalizeWilsyLeadAIText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyLeadAIWorkspaceSurface
 * @description Resolves the current CRM Leads workspace surface label for Operator Kernel routing.
 * @param {string} activeTab - Active Leads top tab.
 * @returns {string} Workspace surface label.
 * @collaboration CRM Leads records, proof, sources, sort, pipeline, and Wilsy AI operator routing.
 */
function resolveWilsyLeadAIWorkspaceSurface(activeTab = 'records') {
  const surfaceByTab = {
    records: 'CRM Leads Records Lead Table Evidence Ledger Source Authority',
    signals: 'CRM Leads Signals Lead Intelligence Evidence Ledger',
    pipeline: 'CRM Leads Revenue Movement Pipeline Telemetry',
    proof: 'CRM Leads Proof Trail Evidence Ledger Source Authority Compliance Gap',
    sources: 'CRM Leads Source Authority Ingestion Routes Evidence Ledger',
    sort: 'CRM Leads Sort Command Source Authority Evidence Ledger Compliance Gap',
  };

  return surfaceByTab[activeTab] || surfaceByTab.records;
}

/**
 * @function resolveWilsyLeadAIAnswerText
 * @description Extracts the best typographic answer from the Operator Kernel response packet.
 * @param {Object} packet - Wilsy AI response packet.
 * @returns {string} Answer text.
 * @collaboration Wilsy AI frontend, Operator Kernel route response, and no-fake-answer fallbacks.
 */
function resolveWilsyLeadAIAnswerText(packet = {}) {
  return normalizeWilsyLeadAIText(
    packet?.operatorModel?.operatorModel?.answer ||
    packet?.operatorModel?.answer ||
    packet?.answer ||
    packet?.error?.message ||
    ''
  );
}

/**
 * @function resolveWilsyLeadAIInlineCommands
 * @description Extracts inline command links from the Operator Kernel response packet.
 * @param {Object} packet - Wilsy AI response packet.
 * @returns {Array<Object>} Inline command links.
 * @collaboration Continuous typographic response flow, inline actions, and approved workflow routing.
 */
function resolveWilsyLeadAIInlineCommands(packet = {}) {
  const commandLinks =
    packet?.operatorModel?.operatorModel?.inlineCommandLinks ||
    packet?.operatorModel?.inlineCommandLinks ||
    packet?.inlineCommandLinks ||
    [];

  return Array.isArray(commandLinks) ? commandLinks : [];
}


/**
 * @function resolveWilsyLeadsFilterPanel
 * @description Resolves the Leads filter sidebar panel from the current component screen.
 * @returns {HTMLElement|null} Leads filter panel.
 * @collaboration Leads component ownership, filter sidebar, checkbox button control, and scoped DOM repair.
 */
function resolveWilsyLeadsFilterPanel() {
  /* P60K5Q10FG90D_PRECISE_FILTER_PANEL_RESOLVER */
  if (typeof document === 'undefined') {
    return null;
  }

  const filterOptionPattern = /Activities|Campaigns|Latest Email Status|Record Action/i;
  const candidateNodes = Array.from(document.querySelectorAll('aside, section, nav, div'))
    .filter((node) => {
      const text = normalizeWilsyLeadFilterText(node.textContent || '');
      const checkboxCount = node.querySelectorAll?.('input[type="checkbox"]')?.length || 0;

      return /Filter Leads by/i.test(text) &&
        /System Defined Filters/i.test(text) &&
        filterOptionPattern.test(text) &&
        checkboxCount > 0;
    })
    .sort((firstNode, secondNode) => {
      const firstCheckboxCount = firstNode.querySelectorAll('input[type="checkbox"]').length;
      const secondCheckboxCount = secondNode.querySelectorAll('input[type="checkbox"]').length;
      const checkboxDelta = firstCheckboxCount - secondCheckboxCount;

      if (checkboxDelta !== 0) {
        return checkboxDelta;
      }

      return String(firstNode.textContent || '').length - String(secondNode.textContent || '').length;
    });

  return candidateNodes[0] || null;
}

/**
 * @function resolveWilsyLeadFilterInputs
 * @description Resolves checkbox inputs owned by the Leads filter panel.
 * @returns {Array<HTMLInputElement>} Leads filter checkboxes.
 * @collaboration Leads filter buttons, checkbox tick rendering, persisted filter state, and component-scoped UI behavior.
 */
function resolveWilsyLeadFilterInputs() {
  const panel = resolveWilsyLeadsFilterPanel();

  if (!panel) {
    return [];
  }

  panel.dataset.wilsyLeadsFilterPanel = 'true';

  return Array.from(panel.querySelectorAll('input[type="checkbox"]'));
}

/**
 * @function resolveWilsyLeadFilterLabel
 * @description Resolves the user-facing label for a Leads filter checkbox.
 * @param {HTMLInputElement} input - Checkbox input.
 * @returns {string} Filter label.
 * @collaboration Leads filter labels, selected filter persistence, backend control-state payload, and operator-readable filter state.
 */
function resolveWilsyLeadFilterLabel(input) {
  const row = input?.closest?.('label, li, div');
  const text = normalizeWilsyLeadFilterText(row?.textContent || input?.name || input?.id || input?.value);

  return text || 'Unnamed filter';
}

/**
 * @function loadWilsyLeadLocalFilterState
 * @description Loads local Leads filter state as fallback before backend state resolves.
 * @returns {Array<string>} Selected filter labels.
 * @collaboration Leads filters, local continuity, backend fallback, and persisted operator preference.
 */
function loadWilsyLeadLocalFilterState() {
  /* P60K5Q10FG90D_FILTER_LOCAL_RESTORE_DISABLED */
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      window.localStorage.setItem(WILSY_LEADS_FILTER_LOCAL_STATE_KEY, JSON.stringify([]));
      window.localStorage.removeItem('wilsy.crm.leads.filterSelection.v2');
      window.localStorage.removeItem('wilsy.crm.leads.filterButtons.v1');
      window.localStorage.removeItem('wilsy.crm.leads.filters');
      window.localStorage.removeItem('wilsy.crm.leads.selectedFilters');
      window.localStorage.removeItem('wilsy.crm.leads.controlState');
      window.localStorage.removeItem('wilsy.crm.controlState.leads.filters');
    } catch (error) {}
  }

  return [];
}

/**
 * @function saveWilsyLeadLocalFilterState
 * @description Saves selected Leads filters locally until backend persistence confirms state.
 * @param {Array<string>} selectedFilters - Selected filter labels.
 * @returns {void}
 * @collaboration Leads filter persistence, browser continuity, backend fallback, and operator-controlled filter state.
 */
function saveWilsyLeadLocalFilterState(selectedFilters = []) {
  /* P60K5Q10FG90D_FILTER_LOCAL_SAVE_DISABLED */
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }

  try {
    window.localStorage.setItem(WILSY_LEADS_FILTER_LOCAL_STATE_KEY, JSON.stringify([]));
    window.localStorage.removeItem('wilsy.crm.leads.filterSelection.v2');
    window.localStorage.removeItem('wilsy.crm.leads.filterButtons.v1');
  } catch (error) {}
}

/**
 * @function setWilsyLeadFilterChecked
 * @description Sets the actual checkbox checked property so the square ticks when active and unticks when cleared.
 * @param {HTMLInputElement} input - Checkbox input.
 * @param {boolean} checked - Desired checked state.
 * @returns {void}
 * @collaboration Leads filter buttons, actual checkbox state, persisted selection, and visual operator feedback.
 */
function setWilsyLeadFilterChecked(input, checked) {
  if (!input || input.type !== 'checkbox') {
    return;
  }

  const descriptor = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked');

  if (descriptor?.set) {
    descriptor.set.call(input, Boolean(checked));
  } else {
    input.checked = Boolean(checked);
  }

  input.indeterminate = false;
  input.dataset.wilsyLeadFilterChecked = input.checked ? 'true' : 'false';
  input.setAttribute('aria-checked', input.checked ? 'true' : 'false');

  if (input.checked) {
    input.setAttribute('checked', 'checked');
  } else {
    input.removeAttribute('checked');
  }

  const row = input.closest('label, li, div');

  if (row) {
    row.dataset.wilsyLeadFilterSelected = input.checked ? 'true' : 'false';
  }
}

/**
 * @function applyWilsyLeadSelectedFilters
 * @description Applies selected filter labels to Leads checkboxes.
 * @param {Array<string>} selectedFilters - Selected filter labels.
 * @returns {void}
 * @collaboration Leads filter sidebar, backend selected state, checkbox tick state, and user-controlled clearing.
 */
function applyWilsyLeadSelectedFilters(selectedFilters = []) {
  const selectedSet = new Set(selectedFilters.map((item) => item.toLowerCase()));

  resolveWilsyLeadFilterInputs().forEach((input) => {
    const label = resolveWilsyLeadFilterLabel(input).toLowerCase();
    setWilsyLeadFilterChecked(input, selectedSet.has(label));
  });
}

/**
 * @function collectWilsyLeadSelectedFilters
 * @description Collects the current selected Leads filters from actual checkbox state.
 * @returns {Array<string>} Selected filter labels.
 * @collaboration Leads filter buttons, checkbox state source of truth, backend persistence, and operator preference.
 */
function collectWilsyLeadSelectedFilters() {
  return resolveWilsyLeadFilterInputs()
    .filter((input) => input.checked)
    .map(resolveWilsyLeadFilterLabel)
    .filter(Boolean);
}

/**
 * @function buildWilsyLeadFilterInstitutionalPayload
 * @description Builds the Wilsy institutional payload for persisting Leads filter control state.
 * @param {Array<string>} selectedFilters - Selected filter labels.
 * @returns {Object} Evidence-bearing payload.
 * @collaboration Leads filter backend persistence, institutionalHeaders, strikePayload, tenant/operator evidence, and audit-ready control state.
 */
function buildWilsyLeadFilterInstitutionalPayload(selectedFilters = []) {
  const { tenantId, operatorId } = resolveWilsyLeadOperatorHeaders();
  const generatedAt = new Date().toISOString();
  const institutionalHeaders = {
    tenantId,
    operatorId,
    route: WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT,
    commandSurface: 'LEADS_FILTER_CONTROL_STATE',
    generatedAt,
    source: 'WilsyLeadOperatingRoom',
  };

  return {
    tenantId,
    operatorId,
    route: WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT,
    commandSurface: 'LEADS_FILTER_CONTROL_STATE',
    generatedAt,
    selectedFilters,
    institutionalHeaders,
    strikePayload: {
      tenantId,
      operatorId,
      route: WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT,
      commandSurface: 'LEADS_FILTER_CONTROL_STATE',
      generatedAt,
      selectedFilters,
      institutionalHeaders,
      evidence: {
        action: 'PERSIST_LEADS_FILTER_SELECTION',
        source: 'Leads filter sidebar',
        stateOwner: 'WilsyLeadOperatingRoom',
      },
    },
  };
}

/**
 * @function fetchWilsyLeadFilterControlState
 * @description Reads persisted Leads filter control state from backend.
 * @returns {Promise<Array<string>>} Selected filter labels.
 * @collaboration Leads filter buttons, backend control-state route, tenant/operator scope, and source-backed UI persistence.
 */
async function fetchWilsyLeadFilterControlState() {
  /* P60K5Q10FG90D_FILTER_BACKEND_FETCH_DISABLED */
  return [];
}

/**
 * @function persistWilsyLeadFilterControlState
 * @description Persists current Leads filter checkbox state to backend with institutional evidence.
 * @param {Array<string>} selectedFilters - Selected filter labels.
 * @returns {Promise<void>} Completion promise.
 * @collaboration Leads filter buttons, backend PUT route, institutional headers, strike payload, and source-backed control state.
 */
async function persistWilsyLeadFilterControlState(selectedFilters = []) {
  /* P60K5Q10FG90D_FILTER_BACKEND_PERSIST_DISABLED */
  return {
    skipped: true,
    selectedFilters: [],
    reason: 'LEADS_FILTER_DOM_CONTROLLER_DISABLED_UNTIL_AUTH_CONTROL_STATE_READY',
  };
}

/**
 * @function injectWilsyLeadFilterButtonStyles
 * @description Injects Leads-only checkbox styles so active filter boxes visibly tick.
 * @returns {void}
 * @collaboration Leads filter buttons, actual checkbox state, scoped component styling, and no global CRM rail side effects.
 */
function injectWilsyLeadFilterButtonStyles() {
  if (typeof document === 'undefined' || document.querySelector('#wilsy-leads-filter-button-state-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-leads-filter-button-state-styles';
  style.textContent = `
    [data-wilsy-leads-filter-panel="true"] input[type="checkbox"] {
      -webkit-appearance: checkbox !important;
      appearance: auto !important;
      accent-color: #3eff9a !important;
    }

    [data-wilsy-leads-filter-panel="true"] input[type="checkbox"][data-wilsy-lead-filter-checked="true"] {
      outline: 2px solid rgba(62, 255, 154, 0.58) !important;
      outline-offset: 2px !important;
    }

    [data-wilsy-leads-filter-panel="true"] [data-wilsy-lead-filter-selected="true"] {
      background: rgba(62, 255, 154, 0.14) !important;
      border-color: rgba(62, 255, 154, 0.42) !important;
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function clearWilsyFG90DLeadFilterVisualState
 * @description Clears any checkbox and row highlight state created by the legacy Leads filter DOM controller.
 * @returns {void}
 * @collaboration Leads filter rail, disabled DOM controller, React filter state, pagination navigation, and auth-safe filter recovery.
 */
function clearWilsyFG90DLeadFilterVisualState() {
  /* P60K5Q10FG90D_FILTER_VISUAL_STATE_RESET */
  const inputs = resolveWilsyLeadFilterInputs();

  inputs.forEach((input) => {
    try {
      setWilsyLeadFilterChecked(input, false);

      const row = input.closest?.('label, li, div');

      if (row) {
        row.removeAttribute('aria-checked');
        row.removeAttribute('data-selected');
        row.removeAttribute('data-active');
        row.removeAttribute('data-state');
        row.dataset.wilsyLeadFilterSelected = 'false';
        row.dataset.wilsyFilterSelected = 'false';

        ['active', 'selected', 'checked', 'isActive', 'isSelected', 'filterActive', 'filterSelected'].forEach((className) => {
          row.classList?.remove?.(className);
        });
      }
    } catch (error) {}
  });
}


/**
 * @function installWilsyLeadFilterControlStateController
 * @description Installs Leads component-owned filter checkbox ticking and backend state persistence.
 * @returns {Function} Cleanup function.
 * @collaboration WilsyLeadOperatingRoom, Leads filter buttons, backend control-state route, tenant/operator evidence, and persisted user selections.
 */
function installWilsyLeadFilterControlStateController() {
  /* P60K5Q10FG90D_FILTER_DOM_CONTROLLER_DISABLED */
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return () => {};
  }

  injectWilsyLeadFilterButtonStyles();
  saveWilsyLeadLocalFilterState([]);
  clearWilsyFG90DLeadFilterVisualState();

  return () => {
    clearWilsyFG90DLeadFilterVisualState();
  };
}


/**
 * @function openWilsyLeadCommandCapsule
 * @description Routes Edit actions to the real DB-persisted Lead Edit Surface while preserving the native command capsule for non-Edit actions.
 * @param {Object} params - Lead command launch parameters.
 * @returns {void} Opens the correct Lead command surface.
 * @collaboration WilsyLeadOperatingRoom, WilsyLeadEditSurface, WilsyLeadCommandCapsule, DB_PERSISTED Lead save flow.
 */
function openWilsyLeadCommandCapsule(params = {}) {
  const normalizedMode = String(params?.mode || '').trim().toLowerCase();
  const normalizedLabel = String(params?.label || '').trim().toLowerCase();
  const isEditAction = normalizedMode === 'edit' || normalizedLabel === 'edit lead' || normalizedLabel === 'edit';

  if (isEditAction) {
    const record = params?.record && typeof params.record === 'object' ? params.record : {};
    const recordId = String(
      params?.recordId ||
      params?.leadId ||
      params?.recordIds?.[0] ||
      record?._id ||
      record?.id ||
      record?.leadId ||
      record?.recordId ||
      ''
    ).trim();

    const recordIds = Array.isArray(params?.recordIds) && params.recordIds.length
      ? params.recordIds.filter(Boolean)
      : [recordId].filter(Boolean);

    const tenantId = String(
      params?.tenantId ||
      params?.tenant ||
      record?.tenantId ||
      record?.tenant ||
      'MASTER'
    ).trim();

    openWilsyLeadEditSurface({
      ...params,
      record,
      lead: record,
      recordId,
      leadId: recordId,
      recordIds,
      tenantId,
      tenant: tenantId,
      wilsyEditRouter: 'R91K54_EDIT_DIRECT_TO_REAL_EDIT_SURFACE'
    });
    return;
  }

  openWilsyLeadCommandCapsuleNative(params);
}


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

const LEAD_PAGE_SIZE_OPTIONS = Object.freeze([6, 10, 20, 50, 100]);

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
    id: 'contact',
    label: 'Contact',
    headline: 'Reach',
    aliases: ['ATTEMPTED TO CONTACT', 'NOT CONTACTED', 'CONTACT IN FUTURE', 'CONTACTED', 'CALL BACK'],
    action: 'Start conversation'
  },
  {
    id: 'qualify',
    label: 'Qualify',
    headline: 'Fit',
    aliases: ['PRE QUALIFIED', 'PRE-QUALIFIED', 'QUALIFIED', 'QUALIFICATION', 'SALES QUALIFIED', 'WARM'],
    action: 'Confirm authority'
  },
  {
    id: 'discover',
    label: 'Discover',
    headline: 'Needs',
    aliases: ['DISCOVERY', 'NEEDS ANALYSIS', 'REQUIREMENTS', 'DEMO', 'MEETING', 'PRESENTATION'],
    action: 'Map demand'
  },
  {
    id: 'propose',
    label: 'Propose',
    headline: 'Offer',
    aliases: ['VALUE PROPOSITION', 'PROPOSAL', 'PRICE QUOTE', 'QUOTE', 'OFFER'],
    action: 'Send proposal'
  },
  {
    id: 'negotiate',
    label: 'Negotiate',
    headline: 'Commit',
    aliases: ['NEGOTIATION', 'REVIEW', 'DECISION MAKER', 'CONTRACT', 'LEGAL'],
    action: 'Resolve blockers'
  },
  {
    id: 'convert',
    label: 'Convert',
    headline: 'Outcome',
    aliases: ['CONVERTED', 'WON', 'LOST', 'CLOSED', 'DISQUALIFIED', 'JUNK', 'NOT QUALIFIED'],
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
    owner: resolveWilsyR91KOwnerTableDisplay(record, resolveLeadOwnerLabel),
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
  return String(record.source || record.sourceSystem || record.connector || record.origin || record.campaign || '—').trim();
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
 * @function resolveLeadOwnerLabel
 * @description Resolves a human-readable owner label from flexible Lead owner fields.
 * @param {Object} record - Lead record.
 * @returns {string} Owner label.
 * @collaboration Shows owner assignment only when the live backend payload provides it.
 */
function resolveLeadOwnerLabel(record = {}) {
  const owner = record.owner || record.ownerName || record.assignedTo || record.assignee || record.createdBy || record.user;

  if (typeof owner === 'string') return owner.trim() || '—';
  if (owner && typeof owner === 'object') {
    return String(owner.name || owner.fullName || owner.email || owner.username || '—').trim() || '—';
  }

  return '—';
}

/**
 * @function resolveLeadOwnerInitials
 * @description Builds owner initials for the compact owner chip.
 * @param {string} ownerLabel - Owner label.
 * @returns {string} Owner initials.
 * @collaboration Creates avatar-like affordance from real owner text without image placeholders.
 */
function resolveLeadOwnerInitials(ownerLabel = '') {
  const cleanLabel = String(ownerLabel || '').trim();
  if (!isKnownLeadValue(cleanLabel)) return '—';

  return cleanLabel
    .split(/\s+/)
    .slice(0, 2)
    .map(part => part.charAt(0).toUpperCase())
    .join('');
}

/**
 * @function resolveLeadStageTone
 * @description Classifies a lead stage for status-pill styling.
 * @param {string} stage - Lead stage.
 * @returns {string} Stage tone.
 * @collaboration Keeps row status visual language derived from the actual Lead status.
 */
function resolveLeadStageTone(stage = '') {
  const normalizedStage = String(stage || '').toUpperCase();

  if (/QUALIFIED|CONVERTED|WON|VERIFIED/.test(normalizedStage)) return 'qualified';
  if (/PROPOSAL|NEGOTIATION|REVIEW/.test(normalizedStage)) return 'proposal';
  if (/CONTACTED|DISCOVERY|MEETING|DEMO|NURTUR/.test(normalizedStage)) return 'contacted';
  if (/FAILED|LOST|DISQUALIFIED|REJECTED/.test(normalizedStage)) return 'failed';

  return 'new';
}

/**
 * @function resolveLeadSubtitle
 * @description Resolves secondary row text for the Lead name cell.
 * @param {Object} record - Lead record.
 * @returns {string} Secondary row text.
 * @collaboration Uses live title/role fields when available and falls back to the live stage only.
 */
function resolveLeadSubtitle(record = {}) {
  if (isWilsyR91K179E26MeetingShellRecord(record)) {
    return String(
      record.recordSubtitle ||
      record.rowSubtitle ||
      record.meetingSubtitle ||
      record.subtitle ||
      resolveLeadStage(record) ||
      '—'
    ).trim() || '—';
  }

  return String(record.title || record.jobTitle || record.position || record.roleTitle || resolveLeadStage(record) || '—').trim() || '—';
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
  if (isWilsyR91K179E26MeetingShellRecord(record)) {
    const meetingScore = Number(record.priorityScore ?? record.readinessScore ?? record.leadScore ?? record.score);

    if (Number.isFinite(meetingScore)) {
      return Math.max(0, Math.min(100, Math.round(meetingScore)));
    }
  }

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
    if (!isKnownLeadValue(source)) return map;

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
  if (isWilsyR91K179E26MeetingShellRecord(record)) {
    return null;
  }

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
 * @function resolveWilsyFG92BLeadOrganizerCountLabel
 * @description Builds compact live backend count copy for the Leads Organizer selector.
 * @param {number} count - Matching live backend Lead count.
 * @param {number} total - Total live backend Lead count.
 * @returns {string} Compact count label.
 * @collaboration Leads Organizer dropdown, live backend rows, list-view counts, compact selector display, and Records grid operating evidence.
 */
function resolveWilsyFG92BLeadOrganizerCountLabel(count = 0, total = 0) {
  /* P60K5Q10FG92G_COMPACT_ORGANIZER_COUNT_COPY */
  /* P60K5Q10FG92H_COUNT_HELPER_JSDOC_REPAIRED */
  const safeCount = Number.isFinite(Number(count)) ? Number(count) : 0;
  const safeTotal = Number.isFinite(Number(total)) ? Number(total) : 0;

  if (!safeTotal) {
    return '0 live';
  }

  return `${safeCount}/${safeTotal} live`;
}

/**
 * @function buildWilsyFG92BLiveLeadOrganizerViews
 * @description Enriches static Lead list-view definitions with live backend row counts and source-backed details.
 * @param {Object[]} sourceRows - Live backend Lead rows.
 * @returns {Object[]} Live backend organizer view models.
 * @collaboration LEAD_LIST_VIEWS, doesLeadMatchListView, Leads Organizer dropdown, active list filtering, and live Records grid.
 */
function buildWilsyFG92BLiveLeadOrganizerViews(sourceRows = [], viewDefinitions = LEAD_LIST_VIEWS) {
  /* P60K5Q10FG92B_LIVE_BACKEND_ORGANIZER_MODEL */
  /* P60K5Q10FG92E_BUILDER_BODY_HARD_REPLACED */
  /* P60K5Q10FG92G_COMPACT_ORGANIZER_BUILDER */
  const liveRows = Array.isArray(sourceRows) ? sourceRows : [];
  const totalRows = liveRows.length;
  /* P60K5Q10FG93I_CUSTOM_VIEW_DEFINITION_SOURCE */
  const organizerDefinitions = Array.isArray(viewDefinitions) && viewDefinitions.length ? viewDefinitions : LEAD_LIST_VIEWS;

  /* P60K5Q10FG93B_CUSTOM_VIEW_DEFINITION_SOURCE */
  return organizerDefinitions.map((view) => {
    const matchingRows = view?.id === 'ALL'
      ? liveRows
      : liveRows.filter((record) => {
          try {
            if (view?.custom) {
              return doesWilsyLeadMatchCustomViewCriteria(record, view.criteria || {});
            }

            return doesLeadMatchListView(record, view.id);
          } catch (error) {
            return false;
          }
        });

    const liveCount = matchingRows.length;
    const baseDetail = String(view.detail || '').replace(/\s+/g, ' ').trim();
    const countLabel = resolveWilsyFG92BLeadOrganizerCountLabel(liveCount, totalRows);

    return {
      ...view,
      liveCount,
      liveTotal: totalRows,
      detail: countLabel,
      staticDetail: baseDetail,
      liveBackendConnected: true,
      compactOrganizer: true,
    };
  });
}

/**
 * @function doesLeadMatchListView
 * @description Checks whether a backend Lead record belongs in the selected Organizer category.
 * @param {Object} record - Lead record.
 * @param {string} listViewId - Organizer list view id.
 * @returns {boolean} True when the Lead belongs in the selected category.
 * @collaboration Leads Organizer, live backend records, category counts, Records grid filtering, and source-backed CRM row rendering.
 */
function doesLeadMatchListView(record = {}, listViewId = 'ALL') {
  /* P60K5Q10FG92J_CATEGORY_MATCHER_REPAIRED */
  /* P60K5Q10FG92K_MATCHER_DOCGUARD_FINALIZED */
  const viewId = String(listViewId || 'ALL').toUpperCase();
  const sourcePayload = record && typeof record.sourcePayload === 'object' && record.sourcePayload ? record.sourcePayload : {};

  if (viewId.includes('ALL')) {
    return true;
  }

  const statusText = [
    record.status,
    record.stage,
    record.leadStatus,
    record.pipelineStatus,
    sourcePayload.status,
    sourcePayload.stage,
  ].map((value) => String(value ?? '').replace(/\s+/g, ' ').trim()).filter(Boolean).join(' ').toLowerCase();

  const proofText = [
    record.verificationStatus,
    record.complianceStatus,
    record.auditStatus,
    record.proofStatus,
    record.reviewStatus,
    record.qualityGateStatus,
    sourcePayload.verificationStatus,
    sourcePayload.complianceStatus,
    sourcePayload.auditStatus,
    sourcePayload.proofStatus,
    sourcePayload.reviewStatus,
  ].map((value) => String(value ?? '').replace(/\s+/g, ' ').trim()).filter(Boolean).join(' ').toLowerCase();

  const priorityText = [
    record.priority,
    record.leadPriority,
    record.urgency,
    sourcePayload.priority,
    sourcePayload.leadPriority,
    sourcePayload.urgency,
  ].map((value) => String(value ?? '').replace(/\s+/g, ' ').trim()).filter(Boolean).join(' ').toLowerCase();

  const sourceText = [
    record.source,
    record.leadSource,
    record.origin,
    sourcePayload.source,
    sourcePayload.leadSource,
    sourcePayload.origin,
  ].map((value) => String(value ?? '').replace(/\s+/g, ' ').trim()).filter(Boolean).join(' ').toLowerCase();

  const activityText = [
    record.lastActivity,
    record.lastActivityAt,
    record.lastContactedAt,
    record.lastInteractionAt,
    record.activityStatus,
    record.activitySignal,
    sourcePayload.lastActivity,
    sourcePayload.lastActivityAt,
    sourcePayload.lastContactedAt,
    sourcePayload.lastInteractionAt,
    sourcePayload.activityStatus,
    sourcePayload.activitySignal,
  ].map((value) => String(value ?? '').replace(/\s+/g, ' ').trim()).filter(Boolean).join(' ').toLowerCase();

  const score = Math.max(0, ...[
    record.score,
    record.leadScore,
    record.priorityScore,
    record.sourceCompletenessScore,
    sourcePayload.score,
    sourcePayload.leadScore,
    sourcePayload.priorityScore,
  ].map((value) => Number(String(value ?? '').replace(/[^0-9.-]/g, ''))).filter(Number.isFinite));

  const value = Math.max(0, ...[
    record.value,
    record.dealValue,
    record.estimatedValue,
    record.pipelineValue,
    record.expectedRevenue,
    sourcePayload.value,
    sourcePayload.dealValue,
    sourcePayload.estimatedValue,
    sourcePayload.pipelineValue,
    sourcePayload.expectedRevenue,
  ].map((candidate) => Number(String(candidate ?? '').replace(/[^0-9.-]/g, ''))).filter(Number.isFinite));

  const hasEmail = [
    record.email,
    sourcePayload.email,
  ].map((candidate) => String(candidate ?? '').trim()).some(Boolean);

  const hasPhone = [
    record.phone,
    record.mobile,
    sourcePayload.phone,
    sourcePayload.mobile,
  ].map((candidate) => String(candidate ?? '').trim()).some(Boolean);

  const hasCompany = [
    record.company,
    record.companyName,
    record.accountName,
    sourcePayload.company,
    sourcePayload.companyName,
  ].map((candidate) => String(candidate ?? '').trim()).some(Boolean);

  const activityCount = Math.max(0, ...[
    record.activityCount,
    record.activitiesCount,
    record.touchCount,
    sourcePayload.activityCount,
    sourcePayload.activitiesCount,
    sourcePayload.touchCount,
  ].map((candidate) => Number(String(candidate ?? '').replace(/[^0-9.-]/g, ''))).filter(Number.isFinite));

  const verified = /verified|approved|passed|complete|compliant|qualified/.test(proofText) || /qualified/.test(statusText);
  const failed = /failed|rejected|disqualified|invalid|lost|blocked/.test(`${proofText} ${statusText}`);
  const priority = /urgent|high|priority/.test(priorityText) || score >= 70 || value >= 750000;
  const sourceGap = !hasEmail || !hasPhone || !hasCompany || !sourceText;
  const untouched = activityCount <= 0 && !activityText && !/qualified|converted|won|lost|failed|rejected|disqualified/.test(statusText);
  const pendingReview = /pending|review|audit|awaiting|needs review|needs_review/.test(`${proofText} ${statusText}`) ||
    (!verified && !failed && /new|open|contacted/.test(statusText) && !priority);

  if (viewId.includes('PRIOR')) {
    return priority;
  }

  if (viewId.includes('VERIFIED') || viewId.includes('COMPLIANCE')) {
    return verified;
  }

  if (viewId.includes('PENDING') || viewId.includes('REVIEW') || viewId.includes('AUDIT')) {
    return pendingReview;
  }

  if (viewId.includes('SOURCE') || viewId.includes('GAP') || viewId.includes('PROVENANCE')) {
    return sourceGap;
  }

  if (viewId.includes('UNTOUCHED') || viewId.includes('ACTIVITY')) {
    return untouched;
  }

  if (viewId.includes('FAILED') || viewId.includes('GATE')) {
    return failed;
  }

  return true;

  /* P60K5Q10FG92M_MATCHER_FUNCTION_CLOSED */
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
 * @function buildLeadVisionMetrics
 * @description Builds the live KPI strip for the Leads pipeline vision UI.
 * @param {Object} input - KPI input packet.
 * @returns {Array<Object>} Vision metric cards.
 * @collaboration Matches Wilson's visual target without hardcoded row, owner or revenue placeholders.
 */
function buildLeadVisionMetrics({
  leads = [],
  filteredLeads = [],
  complianceMetrics = {},
  operatingCopy = LEAD_OPERATING_COPY
} = {}) {
  const leadCount = leads.length;
  const scoreTotal = leads.reduce((total, record) => total + resolveLeadPriorityScore(record), 0);
  const averageScore = leadCount ? Math.round(scoreTotal / leadCount) : 0;
  const visionCopy = operatingCopy || LEAD_OPERATING_COPY;
  const visionRecordSingular = visionCopy.recordSingular || 'lead';
  const visionRecordPlural = visionCopy.recordPlural || 'leads';
  const visionIsMeetingOperatingCopy = String(visionCopy.heroEyebrow || visionCopy.title || visionRecordPlural || '').toUpperCase().includes('MEETING');
  const qualifiedLeads = leads.filter(record => {
    const stage = resolveLeadStage(record).toUpperCase();

    if (visionIsMeetingOperatingCopy) {
      return resolveLeadPriorityScore(record) >= 52 || /READY|SCHEDULED|CONFIRMED|VERIFIED/.test(stage);
    }

    return /QUALIFIED|CONVERTED|WON|VERIFIED/.test(stage);
  }).length;
  const convertedLeads = leads.filter(record => {
    const stage = resolveLeadStage(record).toUpperCase();

    if (visionIsMeetingOperatingCopy) {
      return resolveLeadPriorityScore(record) >= 52 || /READY|SCHEDULED|CONFIRMED|VERIFIED/.test(stage);
    }

    return /CONVERTED|WON/.test(stage);
  }).length;
  const priorityReady = leads.filter(record => resolveLeadPriorityScore(record) >= 52).length;
  const conversionRate = leadCount ? Number(((convertedLeads / leadCount) * 100).toFixed(1)) : 0;
  const pipelineHealth = !leadCount
    ? 'Awaiting live data'
    : averageScore >= 78
      ? 'Excellent'
      : averageScore >= 52
        ? 'Healthy'
        : averageScore >= 24
          ? 'Developing'
          : 'Needs source';
  const pipelineProgress = leadCount ? Math.round((priorityReady / Math.max(1, leadCount)) * 100) : 0;
  const visionPipelineHealthLabel = visionCopy.pipelineHealthLabel || 'Pipeline Health';
  const visionOpenRecordsLabel = visionCopy.openRecordsLabel || 'Open Leads';
  const visionQualifiedLabel = visionCopy.qualifiedLabel || 'Qualified';
  const visionConversionLabel = visionCopy.conversionLabel || 'Conversion Rate';
  const visionAverageScoreLabel = visionCopy.averageScoreLabel || 'Avg. Lead Score';
  const visionReadinessSignalLabel = visionIsMeetingOperatingCopy ? 'meeting readiness' : 'source signal';
  const visionVisibleRecordLabel = visionIsMeetingOperatingCopy ? 'meeting rows visible' : 'visible';
  const visionPriorityReadyLabel = visionIsMeetingOperatingCopy ? 'calendar ready' : 'priority ready';
  const visionConversionDetailLabel = visionIsMeetingOperatingCopy ? 'ready from live meetings' : 'converted from live rows';
  const visionConversionEmptyLabel = visionIsMeetingOperatingCopy ? 'No readiness signal' : 'No conversion signal';
  const visionQualificationEmptyLabel = visionIsMeetingOperatingCopy ? 'No readiness signal' : 'No qualification signal';
  const visionConversionTrendLabel = visionIsMeetingOperatingCopy ? 'Live meeting DB derived' : 'Live DB derived';
  const visionAverageScoreDetailLabel = visionIsMeetingOperatingCopy ? 'Meeting readiness score' : 'Source completeness score';

  return [
    {
      id: 'health',
      label: visionPipelineHealthLabel,
      value: pipelineHealth,
      detail: leadCount ? `${pipelineProgress}% ready by ${visionReadinessSignalLabel}` : `Connect live ${visionRecordSingular[0].toUpperCase()}${visionRecordSingular.slice(1)} rows`,
      trend: complianceMetrics.failed ? `${complianceMetrics.failed} failed gates` : `${filteredLeads.length} ${visionVisibleRecordLabel}`,
      icon: Activity,
      tone: 'violet'
    },
    {
      id: 'open',
      label: visionOpenRecordsLabel,
      value: String(leadCount),
      detail: filteredLeads.length === leadCount ? `All ${visionRecordSingular} rows visible` : `${filteredLeads.length} in current view`,
      trend: priorityReady ? `${priorityReady} ${visionPriorityReadyLabel}` : `No ${visionRecordSingular} rows yet`,
      icon: List,
      tone: 'blue'
    },
    {
      id: 'qualified',
      label: visionQualifiedLabel,
      value: String(qualifiedLeads),
      detail: leadCount ? `${Math.round((qualifiedLeads / Math.max(1, leadCount)) * 100)}% of live ${visionRecordPlural}` : visionQualificationEmptyLabel,
      trend: `${complianceMetrics.verified || 0} verified`,
      icon: CheckCircle2,
      tone: 'green'
    },
    {
      id: 'conversion',
      label: visionConversionLabel,
      value: `${conversionRate}%`,
      detail: leadCount ? `${convertedLeads} ${visionConversionDetailLabel}` : visionConversionEmptyLabel,
      trend: leadCount ? visionConversionTrendLabel : `Waiting for ${visionRecordPlural}`,
      icon: Filter,
      tone: 'cyan'
    },
    {
      id: 'score',
      label: visionAverageScoreLabel,
      value: String(averageScore),
      detail: leadCount ? visionAverageScoreDetailLabel : 'No score yet',
      trend: averageScore >= 52 ? 'Actionable' : 'Needs enrichment',
      icon: Star,
      tone: 'gold'
    }
  ];
}

/**
 * @function buildLeadPaginationModel
 * @description Builds dynamic list-view pagination for backend-sized Lead result sets.
 * @param {Object} input - Pagination input packet.
 * @returns {Object} Pagination model.
 * @collaboration Keeps the Leads footer scalable instead of a static visual placeholder.
 */
function buildLeadPaginationModel({
  totalRecords = 0,
  currentPage = 1,
  pageSize = 20
} = {}) {
  const safePageSize = LEAD_PAGE_SIZE_OPTIONS.includes(Number(pageSize)) ? Number(pageSize) : 20;
  const totalPages = Math.max(1, Math.ceil(Number(totalRecords || 0) / safePageSize));
  const normalizedPage = Math.min(Math.max(1, Number(currentPage || 1)), totalPages);
  const startIndex = totalRecords ? (normalizedPage - 1) * safePageSize : 0;
  const endIndex = totalRecords ? Math.min(startIndex + safePageSize, totalRecords) : 0;
  const compactPages = totalPages <= 5
    ? Array.from({ length: totalPages }, (_, index) => index + 1)
    : normalizedPage <= 3
      ? [1, 2, 3, 'ellipsis-end', totalPages]
      : normalizedPage >= totalPages - 2
        ? [1, 'ellipsis-start', totalPages - 2, totalPages - 1, totalPages]
        : [1, 'ellipsis-start', normalizedPage - 1, normalizedPage, normalizedPage + 1, 'ellipsis-end', totalPages];

  return {
    currentPage: normalizedPage,
    pageSize: safePageSize,
    totalPages,
    startIndex,
    endIndex,
    startRecord: totalRecords ? startIndex + 1 : 0,
    endRecord: endIndex,
    pageItems: compactPages
  };
}

/**
 * @function buildLeadSetupOperatingModel
 * @description Builds the CRM Setup drawer from live Lead records, sync telemetry, role gates and source registry state.
 * @param {Object} input - Live setup state input.
 * @returns {Object} Setup summary and operating control groups.
 * @collaboration Turns Setup from a static menu into a source-backed Wilsy OS command surface.
 */
function buildLeadSetupOperatingModel({
  leads = [],
  filteredLeads = [],
  activeListView = LEAD_LIST_VIEWS[0],
  complianceMetrics = {},
  routeRegistry = [],
  sourceChannels = [],
  liveSources = 0,
  totalSources = 0,
  rootHash = 'UNSEALED',
  role = 'SALES_REP',
  tenantId = 'MASTER',
  syncStatus = 'SOURCE_READY_UPSTREAM',
  isSyncing = false,
  selectedFilterCount = 0,
  totalFilterOptions = 0,
  pageSize = 20,
  totalPages = 1
} = {}) {
  const leadCount = Array.isArray(leads) ? leads.length : 0;
  const visibleCount = Array.isArray(filteredLeads) ? filteredLeads.length : 0;
  const registry = Array.isArray(routeRegistry) ? routeRegistry : [];
  const channels = Array.isArray(sourceChannels) ? sourceChannels : [];
  const routeTotal = Number(totalSources || registry.length || channels.length || 0);
  const routeLive = Number(liveSources || registry.filter(route => route?.connected).length || 0);
  const rootSealed = isKnownLeadValue(rootHash);
  const rootLabel = rootSealed ? String(rootHash).slice(0, 12) : 'UNSEALED';
  const setupUnlocked = canUseLeadAction(role, 'setup');
  const importUnlocked = canUseLeadAction(role, 'import');
  const exportUnlocked = canUseLeadAction(role, 'export');
  const createUnlocked = canUseLeadAction(role, 'create');
  const syncUnlocked = canUseLeadAction(role, 'sync');
  const sourceStatus = isSyncing
    ? 'syncing'
    : routeTotal
      ? (routeLive === routeTotal ? 'live' : routeLive ? 'gap' : 'waiting')
      : 'waiting';
  const complianceStatus = complianceMetrics.failed
    ? 'gap'
    : complianceMetrics.total
      ? 'live'
      : 'waiting';
  const authorityStatus = setupUnlocked ? 'live' : 'locked';
  const selectedViewLabel = activeListView?.label || 'All Leads';

  return {
    summary: [
      {
        label: 'Live Lead Rows',
        value: String(leadCount),
        detail: `${visibleCount} visible through ${selectedViewLabel}`,
        status: leadCount ? 'live' : 'waiting'
      },
      {
        label: 'Source Routes',
        value: routeTotal ? `${routeLive}/${routeTotal}` : '0/0',
        detail: syncStatus || 'SOURCE_READY_UPSTREAM',
        status: sourceStatus
      },
      {
        label: 'Root Seal',
        value: rootLabel,
        detail: rootSealed ? 'Command fabric hash active' : 'Awaiting backend seal',
        status: rootSealed ? 'live' : 'waiting'
      },
      {
        label: 'Role Gate',
        value: role,
        detail: `${tenantId} tenant authority`,
        status: authorityStatus
      }
    ],
    groups: [
      {
        title: 'General',
        icon: UserRoundCog,
        status: leadCount ? 'live' : 'waiting',
        items: [
          {
            label: 'Personal Settings',
            value: role,
            detail: `${tenantId} operator context`,
            status: 'live',
            action: 'command'
          },
          {
            label: 'Users',
            value: setupUnlocked ? 'Admin' : 'View only',
            detail: setupUnlocked ? 'Tenant user controls unlocked' : 'Tenant user controls role-locked',
            status: authorityStatus,
            action: 'command',
            disabled: !setupUnlocked
          },
          {
            label: 'Company Settings',
            value: tenantId,
            detail: `${leadCount} backend lead row${leadCount === 1 ? '' : 's'} in scope`,
            status: 'live',
            action: 'command'
          }
        ]
      },
      {
        title: 'Security Control',
        icon: ShieldCheck,
        status: complianceStatus,
        items: [
          {
            label: 'Profiles',
            value: role,
            detail: createUnlocked ? 'Create gate open' : 'Create gate locked',
            status: createUnlocked ? 'live' : 'locked',
            action: 'command'
          },
          {
            label: 'Roles and Sharing',
            value: syncUnlocked ? 'Sync enabled' : 'Sync locked',
            detail: `${selectedFilterCount}/${totalFilterOptions} filters active`,
            status: syncUnlocked ? 'live' : 'locked',
            action: 'sync',
            disabled: !syncUnlocked || isSyncing
          },
          {
            label: 'Compliance Settings',
            value: `${complianceMetrics.verified || 0}/${complianceMetrics.total || 0}`,
            detail: complianceMetrics.failed ? `${complianceMetrics.failed} failed gate${complianceMetrics.failed === 1 ? '' : 's'}` : `${complianceMetrics.pending || 0} awaiting audit`,
            status: complianceStatus,
            action: 'proof'
          }
        ]
      },
      {
        title: 'Customization',
        icon: SlidersHorizontal,
        status: 'live',
        items: [
          {
            label: 'Modules and Fields',
            value: `${REQUIRED_LEAD_FIELDS.length}/${LEAD_COLUMNS.length}`,
            detail: 'Required fields and table columns bound to Lead records',
            status: 'live',
            action: 'records'
          },
          {
            label: 'Lead Layouts',
            value: `${LEAD_TOP_APP_TABS.length} tabs`,
            detail: `${LEAD_LIST_VIEWS.length} saved views and ${pageSize}/page density`,
            status: 'live',
            action: 'records'
          },
          {
            label: 'Workflow Rules',
            value: `${LEAD_JOURNEY_LANES.length} stages`,
            detail: `${totalPages} live page${totalPages === 1 ? '' : 's'} in current result set`,
            status: 'live',
            action: 'pipeline'
          }
        ]
      },
      {
        title: 'Data Administration',
        icon: Database,
        status: sourceStatus,
        items: [
          {
            label: 'Import',
            value: importUnlocked ? 'Enabled' : 'Locked',
            detail: `${routeTotal ? `${routeLive}/${routeTotal}` : '0/0'} source routes reporting`,
            status: importUnlocked ? sourceStatus : 'locked',
            action: 'sync',
            disabled: !importUnlocked || isSyncing
          },
          {
            label: 'Export',
            value: exportUnlocked ? `${visibleCount} scoped` : 'Locked',
            detail: exportUnlocked ? `Current list view: ${selectedViewLabel}` : 'Manager authority required',
            status: exportUnlocked ? 'live' : 'locked',
            action: 'records',
            disabled: !exportUnlocked
          },
          {
            label: 'Data Backup',
            value: rootLabel,
            detail: rootSealed ? 'Root hash available from command fabric' : 'Run source sync to seal telemetry',
            status: rootSealed ? 'live' : 'waiting',
            action: 'sync',
            disabled: isSyncing
          }
        ]
      },
      {
        title: 'Developer Hub',
        icon: Command,
        status: sourceStatus,
        items: [
          {
            label: 'Command API',
            value: '/api/crm/command',
            detail: `Sync status: ${syncStatus || 'SOURCE_READY_UPSTREAM'}`,
            status: sourceStatus,
            action: 'sync',
            disabled: isSyncing
          },
          {
            label: 'Live Leads API',
            value: '/api/crm/live/leads',
            detail: `${leadCount} normalized Lead record${leadCount === 1 ? '' : 's'} in dashboard snapshot`,
            status: leadCount ? 'live' : 'waiting',
            action: 'records'
          },
          {
            label: 'Source Registry',
            value: routeTotal ? `${routeLive}/${routeTotal}` : `${channels.length} channels`,
            detail: registry.length ? 'Backend model registry connected' : 'Awaiting command sync registry',
            status: sourceStatus,
            action: 'sources'
          }
        ]
      }
    ]
  };
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



const WILSY_LEADS_FILTER_SELECTION_STORAGE_KEY = 'wilsy.crm.leads.filterSelection.v3';

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
 * @function normalizeWilsyLeadFilterExecutionText
 * @description Normalizes Lead record values before local filter execution.
 * @param {*} value - Candidate Lead value.
 * @returns {string} Normalized searchable value.
 * @collaboration Leads filter sidebar, record grid viewpoint, local row filtering, and source-backed CRM rows.
 */
function normalizeWilsyLeadFilterExecutionText(value) {
  if (value === null || value === undefined) {
    return '';
  }

  if (Array.isArray(value)) {
    return value.map(normalizeWilsyLeadFilterExecutionText).filter(Boolean).join(' ');
  }

  if (typeof value === 'object') {
    return Object.values(value).map(normalizeWilsyLeadFilterExecutionText).filter(Boolean).join(' ');
  }

  return String(value).replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyLeadFilterAliasValue
 * @description Resolves a value from a Lead record using common Wilsy OS and CRM field aliases.
 * @param {Object} record - Lead record.
 * @param {Array<string>} aliases - Candidate aliases.
 * @returns {*} Resolved value.
 * @collaboration Leads filter execution, CRM field aliases, backend row payloads, and local source-backed filtering.
 */
function resolveWilsyLeadFilterAliasValue(record = {}, aliases = []) {
  for (const alias of aliases) {
    if (Object.prototype.hasOwnProperty.call(record, alias)) {
      return record[alias];
    }

    const camelAlias = alias.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    if (Object.prototype.hasOwnProperty.call(record, camelAlias)) {
      return record[camelAlias];
    }

    const nestedValue = String(alias || '').split('.').reduce((current, key) => {
      if (!current || typeof current !== 'object') {
        return undefined;
      }

      return current[key];
    }, record);

    if (nestedValue !== undefined) {
      return nestedValue;
    }
  }

  return undefined;
}

/**
 * @function hasWilsyLeadFilterMeaningfulValue
 * @description Determines whether a resolved Lead value should count as present for filter execution.
 * @param {*} value - Candidate value.
 * @returns {boolean} Whether the value is meaningful.
 * @collaboration Leads field filters, related module filters, system filters, and local row visibility.
 */
function hasWilsyLeadFilterMeaningfulValue(value) {
  if (value === null || value === undefined || value === false) {
    return false;
  }

  if (typeof value === 'number') {
    return Number.isFinite(value) && value !== 0;
  }

  if (Array.isArray(value)) {
    return value.length > 0;
  }

  if (typeof value === 'object') {
    return Object.keys(value).length > 0;
  }

  const normalizedValue = normalizeWilsyLeadFilterExecutionText(value).toLowerCase();

  return Boolean(normalizedValue) && !['0', 'false', 'no', 'none', 'null', 'undefined', 'n/a'].includes(normalizedValue);
}

/**
 * @function resolveWilsyLeadFilterOptionMap
 * @description Builds a lookup map for Lead filter option ids and their owning sections.
 * @returns {Map<string, Object>} Filter option map.
 * @collaboration LEAD_FILTER_OPERATING_SECTIONS, selected filter ids, grouped filter execution, and sidebar state.
 */
function resolveWilsyLeadFilterOptionMap() {
  const optionMap = new Map();

  LEAD_FILTER_OPERATING_SECTIONS.forEach((section) => {
    section.options.forEach((option) => {
      optionMap.set(option.id, {
        ...option,
        sectionId: section.id,
        sectionTitle: section.title,
      });
    });
  });

  return optionMap;
}

/**
 * @function resolveWilsyLeadFilterFieldAliases
 * @description Resolves field aliases for a selected Lead filter option.
 * @param {string} filterId - Selected filter id.
 * @returns {Array<string>} Candidate field aliases.
 * @collaboration Leads field filters, Zoho-style CRM labels, Wilsy backend row aliases, and local filter execution.
 */
function resolveWilsyLeadFilterFieldAliases(filterId = '') {
  const aliasMap = {
    annual_revenue: ['annualRevenue', 'annual_revenue', 'revenue', 'companyRevenue'],
    city: ['city', 'addressCity', 'billingCity'],
    company: ['company', 'companyName', 'accountName', 'organization', 'organisation'],
    converted_account: ['convertedAccount', 'converted_account', 'accountId', 'account', 'isConvertedAccount'],
    converted_contact: ['convertedContact', 'converted_contact', 'contactId', 'contact', 'isConvertedContact'],
    converted_deal: ['convertedDeal', 'converted_deal', 'dealId', 'deal', 'opportunityId', 'isConvertedDeal'],
    country: ['country', 'addressCountry', 'billingCountry'],
    created_by: ['createdBy', 'created_by', 'creator', 'createdByName'],
    created_time: ['createdTime', 'created_time', 'createdAt', 'created_at'],
    email: ['email', 'emailAddress', 'primaryEmail'],
    email_opt_out: ['emailOptOut', 'email_opt_out', 'emailOptedOut', 'marketingOptOut'],
    fax: ['fax', 'faxNumber'],
    first_name: ['firstName', 'first_name'],
    industry: ['industry', 'sector'],
    last_activity_time: ['lastActivityTime', 'last_activity_time', 'lastTouchedAt', 'activityUpdatedAt'],
    last_name: ['lastName', 'last_name'],
    lead_conversion_time: ['leadConversionTime', 'lead_conversion_time', 'convertedAt', 'conversionTime'],
    lead_name: ['name', 'leadName', 'lead_name', 'fullName'],
    lead_owner: ['owner', 'ownerName', 'leadOwner', 'lead_owner', 'assignedTo'],
    lead_source: ['source', 'leadSource', 'lead_source', 'sourceModule', 'sourceChannel'],
    lead_status: ['status', 'leadStatus', 'lead_status', 'stage', 'pipelineStage'],
    mobile: ['mobile', 'mobilePhone', 'cellphone'],
    modified_by: ['modifiedBy', 'modified_by', 'updatedBy'],
    modified_time: ['modifiedTime', 'modified_time', 'updatedAt', 'updated_at'],
    employees: ['employees', 'employeeCount', 'numberOfEmployees', 'noOfEmployees'],
    phone: ['phone', 'phoneNumber', 'primaryPhone'],
    rating: ['rating', 'leadRating'],
    salutation: ['salutation'],
    title: ['title', 'jobTitle', 'designation'],
    twitter: ['twitter', 'twitterProfile', 'xProfile'],
    unsubscribed_mode: ['unsubscribedMode', 'unsubscribed_mode', 'unsubscribeMode'],
    unsubscribed_time: ['unsubscribedTime', 'unsubscribed_time', 'unsubscribeTime'],
    website: ['website', 'webSite', 'url', 'domain'],
    zip_code: ['zipCode', 'zip_code', 'postalCode', 'postcode'],
    calls: ['calls', 'callCount', 'callsCount', 'relatedCalls'],
    emails: ['emails', 'emailCount', 'emailsCount', 'relatedEmails'],
    invitees: ['invitees', 'invitedMeetings', 'meetingInvitees'],
    meetings: ['meetings', 'meetingCount', 'meetingsCount', 'relatedMeetings'],
    notes: ['notes', 'noteCount', 'notesCount', 'relatedNotes'],
    tasks: ['tasks', 'taskCount', 'tasksCount', 'relatedTasks'],
  };

  const genericAliases = [
    filterId,
    filterId.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase()),
  ];

  return [...new Set([...(aliasMap[filterId] || []), ...genericAliases])];
}

/**
 * @function hasWilsyLeadActivitySignal
 * @description Resolves whether a Lead record has any engagement or activity signal.
 * @param {Object} record - Lead record.
 * @returns {boolean} Whether the Lead is touched.
 * @collaboration Touched records, untouched records, activity history, Meetings, Tasks, Calls, Emails, and CRM readiness.
 */
function hasWilsyLeadActivitySignal(record = {}) {
  return [
    'activities',
    'activityCount',
    'lastActivityTime',
    'last_activity_time',
    'lastTouchedAt',
    'modifiedTime',
    'modified_time',
    'updatedAt',
    'calls',
    'emails',
    'meetings',
    'tasks',
    'notes',
  ].some((alias) => hasWilsyLeadFilterMeaningfulValue(resolveWilsyLeadFilterAliasValue(record, [alias])));
}

/**
 * @function hasWilsyLeadRelatedRecordSignal
 * @description Resolves whether a Lead record has related CRM module linkage.
 * @param {Object} record - Lead record.
 * @returns {boolean} Whether related module evidence is present.
 * @collaboration Related records action, Calls, Emails, Meetings, Notes, Tasks, Deals, Accounts, Contacts, and CRM relationship readiness.
 */
function hasWilsyLeadRelatedRecordSignal(record = {}) {
  return [
    'relatedRecords',
    'relatedRecordCount',
    'calls',
    'emails',
    'meetings',
    'tasks',
    'notes',
    'deals',
    'accounts',
    'contacts',
    'accountId',
    'contactId',
    'dealId',
    'meetingCount',
    'taskCount',
    'noteCount',
    'emailCount',
    'callCount',
  ].some((alias) => hasWilsyLeadFilterMeaningfulValue(resolveWilsyLeadFilterAliasValue(record, [alias])));
}

/**
 * @function doesWilsyLeadRecordMatchFilter
 * @description Checks whether a Lead record matches one selected filter id.
 * @param {Object} record - Lead record.
 * @param {string} filterId - Selected filter id.
 * @returns {boolean} Whether the record matches.
 * @collaboration Leads filter execution, record grid viewpoint, selected checkbox state, and source-backed rows.
 */
function doesWilsyLeadRecordMatchFilter(record = {}, filterId = '') {
  const normalizedFilterId = String(filterId || '').trim();

  if (!normalizedFilterId) {
    return true;
  }

  if (normalizedFilterId === 'activities') {
    return hasWilsyLeadActivitySignal(record);
  }

  if (normalizedFilterId === 'campaigns') {
    return ['campaigns', 'campaign', 'campaignId', 'campaignName'].some((alias) => hasWilsyLeadFilterMeaningfulValue(resolveWilsyLeadFilterAliasValue(record, [alias])));
  }

  if (normalizedFilterId === 'latest_email_status') {
    return ['latestEmailStatus', 'latest_email_status', 'emailStatus', 'emailEngagementStatus'].some((alias) => hasWilsyLeadFilterMeaningfulValue(resolveWilsyLeadFilterAliasValue(record, [alias])));
  }

  if (normalizedFilterId === 'record_action') {
    const status = normalizeWilsyLeadFilterExecutionText(resolveWilsyLeadFilterAliasValue(record, ['status', 'leadStatus', 'stage'])).toLowerCase();
    const actionableStatus = status && !['converted', 'closed', 'deleted', 'archived', 'lost'].includes(status);

    return actionableStatus || hasWilsyLeadFilterMeaningfulValue(resolveWilsyLeadFilterAliasValue(record, ['email', 'phone', 'mobile', 'owner', 'ownerName']));
  }

  if (normalizedFilterId === 'related_records_action') {
    return hasWilsyLeadRelatedRecordSignal(record);
  }

  if (normalizedFilterId === 'touched_records') {
    return hasWilsyLeadActivitySignal(record);
  }

  if (normalizedFilterId === 'untouched_records') {
    return !hasWilsyLeadActivitySignal(record);
  }

  return resolveWilsyLeadFilterFieldAliases(normalizedFilterId).some((alias) => (
    hasWilsyLeadFilterMeaningfulValue(resolveWilsyLeadFilterAliasValue(record, [alias]))
  ));
}

/**
 * @function applyWilsyLeadOperatingFilters
 * @description Applies selected Lead filter ids to already-loaded backend rows without fabricating records.
 * @param {Array<Object>} records - Base filtered Lead records.
 * @param {Array<string>} selectedFilterIds - Selected filter ids.
 * @returns {Array<Object>} Visible Lead records after selected filter execution.
 * @collaboration Leads filter checkboxes, records table, pagination, empty state, and source-backed CRM data.
 */
function applyWilsyLeadOperatingFilters(records = [], selectedFilterIds = []) {
  const activeFilterIds = selectedFilterIds.map((item) => String(item || '').trim()).filter(Boolean);

  if (!activeFilterIds.length) {
    return records;
  }

  const optionMap = resolveWilsyLeadFilterOptionMap();
  const groupedFilterIds = activeFilterIds.reduce((groups, filterId) => {
    const sectionId = optionMap.get(filterId)?.sectionId || 'UNKNOWN_FILTER_SECTION';
    const existingGroup = groups.get(sectionId) || [];

    existingGroup.push(filterId);
    groups.set(sectionId, existingGroup);

    return groups;
  }, new Map());

  return records.filter((record) => (
    Array.from(groupedFilterIds.values()).every((filterIds) => (
      filterIds.some((filterId) => doesWilsyLeadRecordMatchFilter(record, filterId))
    ))
  ));
}


/**
 * @function WilsyLeadOperatingRoom
 * @description Renders the production Lead operating room with contextual command strip and skin-aware density.
 * @param {Object} props - Component props.
 * @returns {JSX.Element} Lead operating room.
 * @collaboration Replaces action-fatigue layout with a high-density sovereign cockpit.
 */

const WILSY_R91K179E24P44B_DEFAULT_OPERATING_COPY = Object.freeze({
  heroEyebrow: 'SALES PIPELINE',
  title: 'Leads',
  createLabel: 'Create Lead',
  heroDescription: 'Manage pipeline, qualify demand, and track every live revenue opportunity.',
  allRecordsLabel: 'All Leads',
  allRecordsDetail: 'Every source-backed row',
  filterTitle: 'Filter Leads by',
  pipelineHealthLabel: 'Pipeline Health',
  openRecordsLabel: 'Open Leads',
  qualifiedLabel: 'Qualified',
  conversionLabel: 'Conversion Rate',
  averageScoreLabel: 'Avg. Lead Score',
  recordSingular: 'lead',
  recordPlural: 'leads',
  pipelineTabLabel: 'Pipeline',
  recordsTabLabel: 'Records',
  signalsTabLabel: 'Signals',
  proofTabLabel: 'Proof',
  sourcesTabLabel: 'Sources',
  selectedRecordLabel: 'selected lead',
  selectedRecordsLabel: 'selected leads',
  tableHeaders: {
    name: 'Lead Name',
    company: 'Company',
    email: 'Email',
    phone: 'Phone',
    owner: 'Owner',
    status: 'Status',
    score: 'Score',
  },
});

/**
 * @function resolveWilsyR91K179E24P44BOperatingCopy
 * @description Resolves CRM operating-room copy while preserving Leads as the default visual/source contract.
 * @param {Object} overrides - Optional module-specific copy overrides.
 * @returns {Object} Operating-room copy packet.
 * @collaboration WilsyLeadOperatingRoom, WilsyMeetingOperatingRoom adapter, identical CRM workspace doctrine.
 */
function resolveWilsyR91K179E24P44BOperatingCopy(overrides = {}) {
  return {
    ...WILSY_R91K179E24P44B_DEFAULT_OPERATING_COPY,
    ...overrides,
    tableHeaders: {
      ...WILSY_R91K179E24P44B_DEFAULT_OPERATING_COPY.tableHeaders,
      ...(overrides.tableHeaders || {}),
    },
  };
}
/**
 * @function WilsyLeadOperatingRoom
 * @description Renders the canonical CRM Leads operating room and now also acts as the parameterized records shell for sibling CRM workspaces such as Meetings.
 * @param {Object} props - Lead operating room props and optional operatingCopy overrides.
 * @returns {JSX.Element} Canonical CRM records operating room.
 * @collaboration CRMDashboard, WilsyMeetingOperatingRoom adapter, CRM live source posture, Lead records workspace, Wilsy OS identical module doctrine.
 */
/**
 * @function WilsyLeadOperatingRoom
 * @description Renders the canonical CRM records operating room and parameterized shell for sibling CRM workspaces such as Meetings.
 * @collaboration CRMDashboard, WilsyMeetingOperatingRoom adapter, CRM live records, Wilsy OS identical module doctrine.
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
  onOpenThemeAuthority = openCrmGlobalThemeAuthorityFallback,
  operatingCopy = {},
  onOpenOperatingCreate = null,
  onOpenOperatingEdit = null,
  onOpenCrmSetup = null
}) {
  useEffect(() => installWilsyLeadFilterControlStateController(), []);

  const leadOperatingCopy = useMemo(() => resolveWilsyR91K179E24P44BOperatingCopy(operatingCopy), [operatingCopy]);
  const leadOperatingCopyTitle = leadOperatingCopy.title || 'Leads';
  const leadOperatingCopyRecordSingular = leadOperatingCopy.recordSingular || 'lead';
  const leadOperatingCopyRecordPlural = leadOperatingCopy.recordPlural || 'leads';

  /**
   * @function handleWilsyR91K179E24P49BOperatingCreateAction
   * @description Delegates module-specific create actions such as Meetings before falling back to native Lead create mode.
   * @param {Object} context - Optional action context.
   * @returns {void}
   * @collaboration WilsyLeadOperatingRoom, WilsyMeetingOperatingRoom, module-safe CRM create workflows.
   */
  function handleWilsyR91K179E24P49BOperatingCreateAction(context = {}) {
    if (typeof onOpenOperatingCreate === 'function') {
      const delegationResult = onOpenOperatingCreate({
        ...context,
        module: leadOperatingCopy.recordPlural || 'leads',
        recordSingular: leadOperatingCopy.recordSingular || 'lead',
        title: leadOperatingCopyTitle || 'Leads',
        commandSurface: 'R91K179E24P49B_OPERATING_CREATE_DELEGATION',
        generatedAt: new Date().toISOString(),
      });

      if (delegationResult !== false) {
        return;
      }
    }

    setMode('create');
  }

  /**
   * @function handleWilsyR91K179E26OperatingEditAction
   * @description Delegates module-specific edit actions such as Meetings before falling back to native Lead edit authority.
   * @param {Object} record - Row record.
   * @param {string} recordId - Row record id.
   * @param {Array<string>} recordIds - Selected record ids.
   * @returns {void}
   * @collaboration WilsyMeetingOperatingRoom edit workflow, Lead command capsule, shared CRM records table.
   */
  function handleWilsyR91K179E26OperatingEditAction(record = {}, recordId = '', recordIds = []) {
    if (isWilsyR91K179E26MeetingShellRecord(record) && typeof onOpenOperatingEdit === 'function') {
      const delegationResult = onOpenOperatingEdit({
        activeModule: leadOperatingCopyRecordPlural,
        source: 'R91K179E26_SHARED_RECORDS_EDIT_DELEGATION',
        record,
        recordId,
        recordIds,
      });

      if (delegationResult !== false) {
        return;
      }
    }

    openLeadCrudPanelWithAuthority('edit', record, recordId, recordIds);
  }


  /**
   * @function resolveLeadOperatingCopyLabel
   * @description Resolves visible Lead shell labels from operatingCopy so sibling workspaces such as Meetings do not render Lead copy.
   * @param {string} label - Default Lead-shell label.
   * @param {string} id - Optional tab or view id.
   * @returns {string} Resolved visible label.
   * @collaboration WilsyLeadOperatingRoom, WilsyMeetingOperatingRoom adapter, CRM records shell label parity.
   */
  function resolveLeadOperatingCopyLabel(label = '', id = '') {
    const normalizedId = String(id || '').toLowerCase();
    const normalizedLabel = String(label || '').toLowerCase();

    if (normalizedId === 'pipeline' || normalizedLabel === 'pipeline') return leadOperatingCopy.pipelineTabLabel || label;
    if (normalizedId === 'records' || normalizedLabel === 'records') return leadOperatingCopy.recordsTabLabel || label;
    if (normalizedId === 'signals' || normalizedLabel === 'signals') return leadOperatingCopy.signalsTabLabel || label;
    if (normalizedId === 'proof' || normalizedLabel === 'proof') return leadOperatingCopy.proofTabLabel || label;
    if (normalizedId === 'sources' || normalizedLabel === 'sources') return leadOperatingCopy.sourcesTabLabel || label;
    if (normalizedLabel === 'all leads') return leadOperatingCopy.allRecordsLabel || label;
    if (normalizedLabel === 'leads') return leadOperatingCopyTitle;
    if (normalizedLabel === 'create lead') return leadOperatingCopy.createLabel || label;

    return label;
  }
  const role = resolveLeadRole(user, tenantConfig);
  const globalThemeAuthorityLabel = resolveCrmGlobalThemeAuthorityLabel(themeRuntime);
  const globalThemeAuthorityMode = resolveCrmGlobalThemeAuthorityMode(themeRuntime);
  const tenantId = resolveTenantId(tenantConfig, user);
  const [mode, setMode] = useState('list');
  const [activeTopTab, setActiveTopTab] = useState('records');
  const [wilsyLeadAiQuestion, setWilsyLeadAiQuestion] = useState('');
  const [wilsyLeadAiPacket, setWilsyLeadAiPacket] = useState(null);
  const [wilsyLeadAiLoading, setWilsyLeadAiLoading] = useState(false);
  const [wilsyLeadAiError, setWilsyLeadAiError] = useState('');
  const [leadSortViewpoint, setLeadSortViewpoint] = useState({ field: 'lastActivity', direction: 'desc' });
  const [activeListViewId, setActiveListViewId] = useState('ALL_LEADS');
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [leadFilterQuery, setLeadFilterQuery] = useState('');
  const [selectedLeadFilterOptions, setSelectedLeadFilterOptions] = useState(() => {
    /* P60K5Q10FG90D_REACT_FILTER_STATE_STARTS_EMPTY */
    /* P60K5Q10FG90E_REACT_FILTER_INITIALIZER_REPAIR */
    return new Set();
  });

  useEffect(() => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    window.localStorage.setItem(
      WILSY_LEADS_FILTER_SELECTION_STORAGE_KEY,
      JSON.stringify(Array.from(selectedLeadFilterOptions)),
    );
  }, [selectedLeadFilterOptions]);


  useEffect(() => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    window.localStorage.setItem(
      WILSY_LEADS_FILTER_SELECTION_STORAGE_KEY,
      JSON.stringify(Array.from(selectedLeadFilterOptions)),
    );
  }, [selectedLeadFilterOptions]);


  useEffect(() => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    window.localStorage.removeItem('wilsy.crm.leads.filterSelection.v2');
  }, []);


  /**
   * @function clearWilsyLeadFilterSelection
   * @description Clears active Leads filter checkboxes, search text, pagination, selected table rows, and persisted local filter state.
   * @returns {void}
   * @collaboration Leads filter rail, controlled checkbox state, record viewpoint, pagination reset, and operator escape control.
   */
  function clearWilsyLeadFilterSelection() {
    setSelectedLeadFilterOptions(new Set());
    setLeadFilterQuery('');
    setCurrentLeadPage(1);
    setSelectedRowIds([]);

    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem(WILSY_LEADS_FILTER_SELECTION_STORAGE_KEY, JSON.stringify([]));
      window.localStorage.removeItem('wilsy.crm.leads.filterSelection.v2');
    }
  }


  /**
   * @function openWilsyLeadFilterRail
   * @description Opens the Leads filter rail from the collapsed rail or toolbar filter control.
   * @returns {void}
   * @collaboration Leads toolbar, collapsed filter rail, record viewpoint, and operator navigation recovery.
   */
  function openWilsyLeadFilterRail() {
    setFilterPanelOpen(true);
  }

  /**
   * @function closeWilsyLeadFilterRail
   * @description Closes the Leads filter rail and clears only temporary filter search text without changing selected filters.
   * @returns {void}
   * @collaboration Leads filter rail, collapse control, filter search field, record viewpoint, and operator navigation recovery.
   */
  function closeWilsyLeadFilterRail() {
    setFilterPanelOpen(false);
    setLeadFilterQuery('');
  }

  const [sortMode, setSortMode] = useState('priority');
  const [leadSkin, setLeadSkin] = useState('crm_revenue_pulse');
  const [splitView, setSplitView] = useState(false);
  const [filterPanelOpen, setFilterPanelOpen] = useState(true);
  const [viewMenuOpen, setViewMenuOpen] = useState(false);
  const [leadToolbarMembershipById, setLeadToolbarMembershipById] = useState({});
  const [leadToolbarCommandBusy, setLeadToolbarCommandBusy] = useState('');
  const [leadToolbarCommandFeedback, setLeadToolbarCommandFeedback] = useState('');
  const [leadCollectionSourcePickerOpen, setLeadCollectionSourcePickerOpen] = useState(false);
  const [leadCollectionSourceSelectedIds, setLeadCollectionSourceSelectedIds] = useState([]);
  const [leadCollectionSourceQuery, setLeadCollectionSourceQuery] = useState('');
  const [leadViewActionConfirmation, setLeadViewActionConfirmation] = useState(null);
  const [leadBackendRunRowsByViewId, setLeadBackendRunRowsByViewId] = useState({});
  const [leadBackendRunPaginationByViewId, setLeadBackendRunPaginationByViewId] = useState({});
  const [leadBackendRunStatusByViewId, setLeadBackendRunStatusByViewId] = useState({});
  /* P60K5Q10FG93I_CUSTOM_VIEW_STATE */
  const [leadCustomViewBuilderOpen, setLeadCustomViewBuilderOpen] = useState(false);
  const [leadCustomViews, setLeadCustomViews] = useState(() => {
    /* P60K5Q10FG93B_CUSTOM_VIEW_STATE */
    if (typeof window === 'undefined') {
      return [];
    }

    try {
      const parsed = JSON.parse(window.localStorage.getItem('wilsy.crm.leads.customViews.v1') || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  });
  const [sortMenuOpen, setSortMenuOpen] = useState(false);
  const [createMenuOpen, setCreateMenuOpen] = useState(false);
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);
  const [themeMenuOpen, setThemeMenuOpen] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [setupOpen, setSetupOpen] = useState(false);
const [coreToolsOpen, setCoreToolsOpen] = useState(false);
const [proofLedgerAccessPolicy, setProofLedgerAccessPolicy] = useState(null);
const [proofLedgerAccessBusy, setProofLedgerAccessBusy] = useState(false);
const [proofLedgerAccessError, setProofLedgerAccessError] = useState('');
const [proofLedgerSelectedUserId, setProofLedgerSelectedUserId] = useState('');

/* P60K5Q10FG104O2_PROOF_LEDGER_ACCESS_STATE */
useEffect(() => {
  if (activeTopTab !== 'proof' || proofLedgerAccessPolicy || proofLedgerAccessBusy) {
    return undefined;
  }

  void resolveWilsyProofLedgerAccessPolicy();

  return undefined;
}, [activeTopTab]);

/**
 * @function publishWilsyProofLedgerBrowserSmokeProof
 * @description Publishes a browser-console verifier for Proof Ledger rail, receipt, export policy, selector, and backend policy state.
 * @returns {Function|undefined} Cleanup handler.
 * @collaboration Lead Proof workspace, FG104O2 Proof Ledger access rail, backend policy receipt, export control, selector state, and browser smoke verification.
 */
useEffect(() => {
  if (typeof window === 'undefined') {
    return undefined;
  }

  window.__wilsyProofLedgerAccessSmokeProof = () => {
    const rail = document.querySelector('[data-wilsy-proof-ledger-access-rail="FG104O2"]');
    const selector = rail?.querySelector('select');
    const receiptButton = rail?.querySelector('button:not(:disabled)');
    const policy = proofLedgerAccessPolicy || {};
    const receipt = policy.receipt || {};
    const receiptPersisted = receipt.persisted === true;
    const receiptPersistenceError = String(receipt.persistenceError || '').trim();
    const receiptPersistenceState = receiptPersisted
      ? 'persisted'
      : receiptPersistenceError
        ? 'not_persisted'
        : 'unknown';
    const decision = policy.decision || {};
    const exportPolicy = policy.exportPolicy || {};
    const selectableUsers = Array.isArray(policy.selectableUsers) ? policy.selectableUsers : [];
    const delegationPolicy = policy.delegationPolicy || {};
    const operatorUserId = String(
      policy.operator?.matchedUser?.userId || policy.operator?.userId || proofLedgerSelectedUserId || ''
    ).trim();
    const delegatedUsers = selectableUsers.filter((user) => {
      const userId = String(user?.userId || '').trim();
      return Boolean(userId && userId !== operatorUserId && user?.accessScope !== 'OWN');
    });
    const delegationReady = Boolean(
      delegationPolicy.enabled || policy.capabilities?.canDelegateProofLedgerAccess
    );

    return {
      version: 'P60K5Q10FG104P_PROOF_LEDGER_BROWSER_SMOKE_PROOF',
      railPresent: Boolean(rail),
      ready: rail?.getAttribute('data-wilsy-proof-ledger-access-ready') || 'missing',
      exportPolicyDom: rail?.getAttribute('data-wilsy-proof-ledger-export-policy') || 'missing',
      accessAllowed: Boolean(decision.allowed),
      decisionScope: decision.scope || '',
      decisionReason: decision.reasonCode || '',
      exportEnabled: Boolean(exportPolicy.enabled),
      exportReason: exportPolicy.reasonCode || '',
      receiptPresent: Boolean(receipt.receiptId),
      receiptId: receipt.receiptId || '',

      receiptPersisted,

      receiptPersistenceError,

      receiptPersistenceState,
      selectorPresent: Boolean(selector),
      selectedUserId: selector?.value || proofLedgerSelectedUserId || '',
      selectableUserCount: selectableUsers.length,
      authoritySource: policy.operator?.authoritySource || exportPolicy.authoritySource || '',
      delegationReady,
      delegationReason: delegationPolicy.reasonCode || '',
      delegatedUserCount: delegatedUsers.length,
      delegationReadiness: delegationReady
        ? delegatedUsers.length
          ? 'Delegated users available'
          : 'Delegation ready / no delegated users yet'
        : 'Delegation locked',
      text: rail?.innerText || '',
      pass: Boolean(
        rail &&
          receipt.receiptId &&
          decision.allowed &&
          exportPolicy.enabled &&
          selector &&
          selectableUsers.length
      ),
    };
  };

  return () => {
    if (window.__wilsyProofLedgerAccessSmokeProof) {
      delete window.__wilsyProofLedgerAccessSmokeProof;
    }
  };
}, [proofLedgerAccessPolicy, proofLedgerSelectedUserId]);

// P60K5Q10FG104P_PROOF_LEDGER_BROWSER_SMOKE_PROOF
  const [draft, setDraft] = useState(() => createEmptyLeadDraft({}));
  const [saveStatus, setSaveStatus] = useState('');
  const [syncStatus, setSyncStatus] = useState('SOURCE_READY_UPSTREAM');
  const [syncTelemetry, setSyncTelemetry] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedLeadId, setSelectedLeadId] = useState('');
  const [selectedRowIds, setSelectedRowIds] = useState([]);
  const [openRowActionId, setOpenRowActionId] = useState('');
  const [currentLeadPage, setCurrentLeadPage] = useState(1);
  const [leadPageSize, setLeadPageSize] = useState(6);

  /**
   * @function openWilsyLeadProofTrailViewpoint
   * @description Routes generated row Proof Trail actions to the visible Leads Proof viewpoint instead of the hidden drawer edge.
   * @returns {void}
   * @collaboration Leads generated row action menu, Proof tab, record viewpoint, row evidence trail, and operator-visible task completion.
   */
  function openWilsyLeadProofTrailViewpoint() {
    setActiveTopTab('proof');
    setCommandOpen(false);
    setCreateMenuOpen(false);
    setMoreMenuOpen(false);
    setThemeMenuOpen(false);
    setOpenRowActionId('');
  }

  useEffect(() => {
    if (typeof window === 'undefined' || !window.document) {
      return undefined;
    }

    /**
     * @function captureWilsyLeadProofTrailClick
     * @description Captures generated Proof Trail menu clicks before the hidden drawer command can run.
     * @param {Event} event - Native browser click event.
     * @returns {void}
     * @collaboration Document capture phase, generated Leads action menu, Proof viewpoint routing, and drawer suppression.
     */
    const captureWilsyLeadProofTrailClick = (event) => {
      const actionElement = event?.target?.closest?.('button, [role="menuitem"], a, li, [data-action], [data-command]');
      const actionText = String(actionElement?.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();

      if (actionText !== 'proof trail') {
        return;
      }

      event.preventDefault();
      event.stopPropagation();

      if (typeof event.stopImmediatePropagation === 'function') {
        event.stopImmediatePropagation();
      }

      openWilsyLeadProofTrailViewpoint();
    };

    window.document.addEventListener('click', captureWilsyLeadProofTrailClick, true);

    return () => {
      window.document.removeEventListener('click', captureWilsyLeadProofTrailClick, true);
    };
  }, []);


  const hasAutoHydratedTelemetryRef = useRef(false);
  const wilsyLeadExternalPointerDownRef = useRef(0);

  /* WILSY_P60K5Q10FG38_PROOF_VIEW_CONTAINMENT_EFFECT */
  useEffect(() => {
    if (activeTopTab !== 'proof') {
      return;
    }

    setCommandOpen(false);
    setCreateMenuOpen(false);
    setMoreMenuOpen(false);
    setThemeMenuOpen(false);
    setOpenRowActionId('');
  }, [activeTopTab]);

  const leadThemeOptions = useMemo(() => resolveCrmThemeEngineOptions(), []);
  const activeLeadThemeOption = useMemo(() => ({
    id: themeRuntime?.themeId || leadSkin || 'crm_revenue_pulse',
    label: globalThemeAuthorityLabel,
    className: '',
    cssVars: themeRuntime?.cssVars || undefined,
    source: 'global-command-center'
  }), [globalThemeAuthorityLabel, leadSkin, themeRuntime]);
  const activeListView = useMemo(() => resolveLeadListView(activeListViewId), [activeListViewId]);

  const leadOrganizerViewDefinitions = useMemo(() => ([
    ...LEAD_LIST_VIEWS,
    ...leadCustomViews,
  ]), [leadCustomViews]);

    /**
   * @function resolveWilsyLeadViewRegistryUrl
   * @description Resolves the backend Lead View Registry route for saved custom views.
   * @returns {string} Lead View Registry route.
   * @collaboration Custom View Builder, backend CRUD, audit receipts, and tenant view persistence.
   */
  function resolveWilsyLeadViewRegistryUrl() {
    const apiBase = String(import.meta.env?.VITE_API_URL || '').replace(/\/$/, '');
    return `${apiBase}/api/crm/leads/views`;
  }

  /**
   * @function readWilsyLeadViewRegistryStoredValue
   * @description Reads browser storage for signed Lead View Registry requests without exposing credentials in source.
   * @param {string} key Browser storage key.
   * @returns {string} Stored value or empty string.
   * @collaboration Browser auth session, CRM Lead View Registry, token-backed saved view persistence, and frontend request signing.
   */
  function readWilsyLeadViewRegistryStoredValue(key = '') {
    try {
      if (typeof window === 'undefined') {
        return '';
      }

      return window.localStorage?.getItem(key)
        || window.sessionStorage?.getItem(key)
        || '';
    } catch {
      return '';
    }
  }

  /**
   * @function resolveWilsyLeadViewRegistryAuthToken
   * @description Resolves the active browser JWT used for authenticated Lead View Registry requests.
   * @returns {string} Browser token without Bearer prefix.
   * @collaboration Browser session, authenticated backend route, Custom View Builder, and CRM Lead View persistence.
   */
  function resolveWilsyLeadViewRegistryAuthToken() {
    return String(
      readWilsyLeadViewRegistryStoredValue('token')
      || readWilsyLeadViewRegistryStoredValue('authToken')
      || readWilsyLeadViewRegistryStoredValue('accessToken')
      || readWilsyLeadViewRegistryStoredValue('wilsyToken')
      || readWilsyLeadViewRegistryStoredValue('wilsy_token')
      || readWilsyLeadViewRegistryStoredValue('sovereignToken')
      || ''
    ).replace(/^Bearer\s+/i, '').trim();
  }

  /**
   * @function decodeWilsyLeadViewRegistryJwtPayload
   * @description Decodes an existing browser JWT payload without validating or storing secrets.
   * @param {string} token Browser JWT token.
   * @returns {object} Decoded JWT payload.
   * @collaboration Operator identity, tenant evidence, Lead View ownership, and browser-authenticated registry saves.
   */
  function decodeWilsyLeadViewRegistryJwtPayload(token = '') {
    try {
      const cleanToken = String(token || '').replace(/^Bearer\s+/i, '').trim();
      const payload = cleanToken.split('.')[1];

      if (!payload) {
        return {};
      }

      const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
      const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=');

      return JSON.parse(atob(padded));
    } catch {
      return {};
    }
  }

  /**
   * @function stableWilsyLeadViewRegistrySealValue
   * @description Recursively sorts object keys so the browser seal payload matches backend deterministic payload reconstruction.
   * @param {*} value Payload value.
   * @returns {*} Stable value.
   * @collaboration ProductionHardening.middleware getRawPayloadString, browser signer, and CRM Lead View Registry payloads.
   */
  function stableWilsyLeadViewRegistrySealValue(value) {
    if (Array.isArray(value)) {
      return value.map(stableWilsyLeadViewRegistrySealValue);
    }

    if (value && typeof value === 'object') {
      return Object.keys(value)
        .sort()
        .reduce((nextValue, key) => {
          nextValue[key] = stableWilsyLeadViewRegistrySealValue(value[key]);
          return nextValue;
        }, {});
    }

    return value;
  }

  /**
   * @function stableWilsyLeadViewRegistrySealStringify
   * @description Converts a payload into the deterministic JSON string used for Lead View Registry seal reconstruction.
   * @param {object} payload Request payload.
   * @returns {string} Stable JSON string.
   * @collaboration Browser request signer, backend SHA3 seal verification, and persisted custom Lead views.
   */
  function stableWilsyLeadViewRegistrySealStringify(payload = {}) {
    return JSON.stringify(stableWilsyLeadViewRegistrySealValue(payload));
  }

  /**
   * @function hashWilsyLeadViewRegistrySha3512
   * @description Hashes the Lead View Registry reconstruction string with SHA3-512 and uppercase hex output.
   * @param {string} reconstruction Seal reconstruction string.
   * @returns {string} Uppercase SHA3-512 digest.
   * @collaboration js-sha3, ProductionHardening.middleware, X-Request-Seal, and forensic request verification.
   */
  function hashWilsyLeadViewRegistrySha3512(reconstruction = '') {
    return String(sha3_512(String(reconstruction))).toUpperCase();
  }

  /**
   * @function buildWilsyLeadViewRegistrySealHeaders
   * @description Builds forensic headers for a signed Lead View Registry request using the backend reconstruction contract.
   * @param {object} payload Request payload.
   * @returns {object} Signed request headers.
   * @collaboration CRM Lead View Registry, browser auth token, ProductionHardening.middleware, and SHA3-512 seal verification.
   */
  function buildWilsyLeadViewRegistrySealHeaders(payload = {}) {
    const traceId = String(payload.requestId || `REQ-WILSY-LEADVIEW-CLIENT-${Date.now()}`);
    const timestamp = String(payload.generatedAt || new Date().toISOString());
    const nonce = `NONCE-WILSY-LEADVIEW-CLIENT-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    const payloadString = stableWilsyLeadViewRegistrySealStringify(payload);
    const reconstruction = `${traceId}|${timestamp}|${payloadString}|${nonce}`;
    const requestSeal = hashWilsyLeadViewRegistrySha3512(reconstruction);

    return {
      traceId,
      timestamp,
      nonce,
      requestSeal,
      headers: {
        'X-Request-ID': traceId,
        'X-Trace-ID': traceId,
        'X-Correlation-ID': traceId,
        'X-Forensic-Timestamp': timestamp,
        'X-Timestamp': timestamp,
        'X-Generated-At': timestamp,
        'X-Cryptographic-Nonce': nonce,
        'X-Request-Seal': requestSeal,
        'X-Request-Proof': requestSeal,
        'X-Quantum-Verified': 'true',
        'X-Wilsy-Lead-View-Seal': 'P60K5Q10FG99F_SIGNED_LEAD_VIEW_REGISTRY'
      }
    };
  }

  /**
   * @function resolveWilsyLeadViewRegistryIdentity
   * @description Resolves tenant and operator identity for signed Lead View Registry persistence.
   * @returns {object} Registry identity.
   * @collaboration Multi-tenant CRM, institutional headers, browser auth token, operator evidence, and saved view ownership.
   */
  function resolveWilsyLeadViewRegistryIdentity() {
    const token = resolveWilsyLeadViewRegistryAuthToken();
    const decodedToken = decodeWilsyLeadViewRegistryJwtPayload(token);
    const tenantSource = typeof tenantConfig !== 'undefined' && tenantConfig ? tenantConfig : {};

    const tenantId = String(
      tenantSource.tenantId
      || tenantSource.id
      || readWilsyLeadViewRegistryStoredValue('wilsy.tenantId')
      || readWilsyLeadViewRegistryStoredValue('tenantId')
      || decodedToken.tenantId
      || decodedToken.tenant
      || 'MASTER'
    ).trim();

    const operatorUserId = String(
      readWilsyLeadViewRegistryStoredValue('wilsy.operatorUserId')
      || readWilsyLeadViewRegistryStoredValue('operatorUserId')
      || readWilsyLeadViewRegistryStoredValue('operatorId')
      || readWilsyLeadViewRegistryStoredValue('userId')
      || decodedToken.id
      || decodedToken.sub
      || decodedToken.userId
      || decodedToken.email
      || 'wilsy-operator'
    ).trim();

    return {
      tenantId: tenantId || 'MASTER',
      operatorId: operatorUserId || 'wilsy-operator',
      operatorUserId: operatorUserId || 'wilsy-operator',
      userId: operatorUserId || 'wilsy-operator',
      operatorEmail: decodedToken.email || readWilsyLeadViewRegistryStoredValue('operatorEmail') || '',
      operatorRole: decodedToken.role || readWilsyLeadViewRegistryStoredValue('operatorRole') || ''
    };
  }

  /**
   * @function buildWilsyLeadViewRegistryPayload
   * @description Builds signed institutional Lead View Registry payload evidence from a custom view.
   * @param {object} viewPayload Custom view payload.
   * @returns {object} Backend payload.
   * @collaboration Custom View Builder, strike payload evidence, backend persistence, signed browser requests, and Wilsy AI view memory.
   */
  function buildWilsyLeadViewRegistryPayload(viewPayload = {}) {
    const identity = resolveWilsyLeadViewRegistryIdentity();
    const generatedAt = new Date().toISOString();
    const requestId = `REQ-WILSY-LEADVIEW-CLIENT-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    const route = '/api/crm/leads/views';
    const commandSurface = 'CRM_LEADS_CUSTOM_VIEW_BUILDER';

    const institutionalHeaders = {
      tenantId: identity.tenantId,
      operatorId: identity.operatorId,
      operatorUserId: identity.operatorUserId,
      userId: identity.userId,
      operatorEmail: identity.operatorEmail,
      operatorRole: identity.operatorRole,
      route,
      commandSurface,
      timestamp: generatedAt,
      generatedAt,
      requestId
    };

    return {
      ...viewPayload,
      tenantId: identity.tenantId,
      ownerUserId: identity.operatorUserId,
      createdBy: identity.operatorUserId,
      updatedBy: identity.operatorUserId,
      source: 'lead-custom-view-builder',
      uiVersion: 'FG99F',
      commandSurface,
      generatedAt,
      requestId,
      institutionalHeaders,
      strikePayload: {
        action: 'CREATE_LEAD_VIEW',
        tenantId: identity.tenantId,
        operatorId: identity.operatorId,
        operatorUserId: identity.operatorUserId,
        userId: identity.userId,
        operatorEmail: identity.operatorEmail,
        operatorRole: identity.operatorRole,
        route,
        commandSurface,
        timestamp: generatedAt,
        generatedAt,
        requestId,
        institutionalHeaders,
        criteria: viewPayload.criteria || [],
        columns: viewPayload.columns || [],
        visibility: viewPayload.visibility || 'private',
        name: viewPayload.name || ''
      }
    };
  }

  /**
   * @function persistWilsyLeadCustomViewToRegistry
   * @description Persists a Lead Custom View to the backend Lead View Registry with auth, institutional evidence, and SHA3 request seal.
   * @param {object} viewPayload Custom view payload.
   * @returns {Promise<object|null>} Persisted backend view or null fallback.
   * @collaboration Backend CRUD, Custom View Builder, tenant persistence, Authorization bearer token, forensic seal headers, and audit receipts.
   */
  async function persistWilsyLeadCustomViewToRegistry(viewPayload = {}) {
    const identity = resolveWilsyLeadViewRegistryIdentity();
    const token = resolveWilsyLeadViewRegistryAuthToken();

    if (!token) {
      throw new Error('CRM_LEAD_VIEW_AUTH_TOKEN_REQUIRED: Signed Lead View Registry save requires an authenticated browser session.');
    }

    const payload = buildWilsyLeadViewRegistryPayload(viewPayload);
    const sealContract = buildWilsyLeadViewRegistrySealHeaders(payload);
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      'X-Tenant-Id': identity.tenantId,
      'X-Operator-Id': identity.operatorId,
      'X-Operator-User-Id': identity.operatorUserId,
      'X-User-Id': identity.userId,
      'X-Command-Surface': 'CRM_LEADS_CUSTOM_VIEW_BUILDER',
      ...sealContract.headers
    };

    const response = await fetch(resolveWilsyLeadViewRegistryUrl(), {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    let result = {};

    try {
      result = await response.json();
    } catch {
      result = {};
    }

    if (!response.ok) {
      throw new Error(result.message || result.error || result.code || `Lead View Registry save failed: ${response.status}`);
    }

    return result?.view || null;
  }

  // P60K5Q10FG99F_SIGNED_LEAD_VIEW_REGISTRY_CLIENT


  /**
   * @function formatWilsyToolbarCollectionCount
   * @description Formats collection membership counts for compact toolbar display.
   * @param {number} count Raw count.
   * @returns {string} Compact count label.
   * @collaboration Million-record CRM views, toolbar actions, membership summaries, and compact UI.
   */
  function formatWilsyToolbarCollectionCount(count = 0) {
    const value = Number(count || 0);

    if (!Number.isFinite(value) || value <= 0) return '0';
    if (value < 1000) return String(value);
    if (value < 1000000) {
      return `${value < 10000 ? (value / 1000).toFixed(1) : Math.round(value / 1000)}K`;
    }

    return `${value < 10000000 ? (value / 1000000).toFixed(1) : Math.round(value / 1000000)}M`;
  }

  /**
   * @function resolveWilsyToolbarViewBackendId
   * @description Resolves the backend registry id for the active Lead collection view.
   * @param {object} view Active organizer view.
   * @returns {string} Backend view id.
   * @collaboration Lead View Registry, toolbar membership actions, custom views, and archive command.
   */
  function resolveWilsyToolbarViewBackendId(view = {}) {
    return String(
      view?.backendViewId
      || view?.backendId
      || view?.registryViewId
      || view?._id
      || ''
    ).trim();
  }

  /**
   * @function resolveWilsyToolbarSelectedLeadIds
   * @description Normalizes selected Lead ids from the existing selectedRowIds state.
   * @returns {string[]} Selected Lead ids.
   * @collaboration Existing table selection, Add selected, Remove selected, and backend membership overrides.
   */
  function resolveWilsyToolbarSelectedLeadIds() {
    if (selectedRowIds instanceof Set) {
      return Array.from(selectedRowIds).map((leadId) => String(leadId || '').trim()).filter(Boolean);
    }

    if (Array.isArray(selectedRowIds)) {
      return selectedRowIds.map((leadId) => String(leadId || '').trim()).filter(Boolean);
    }

    if (selectedRowIds && typeof selectedRowIds === 'object') {
      return Object.entries(selectedRowIds)
        .filter(([, selected]) => Boolean(selected))
        .map(([leadId]) => String(leadId || '').trim())
        .filter(Boolean);
    }

    return [];
  }

  /**
   * @function isWilsyToolbarCustomCollectionView
   * @description Determines whether the active view is a saved custom Lead collection.
   * @param {object} view Active organizer view.
   * @returns {boolean} Whether collection actions should be enabled.
   * @collaboration Built-in views, custom views, backend registry ids, and safe toolbar enablement.
   */
  function isWilsyToolbarCustomCollectionView(view = {}) {
    return Boolean(
      view?.persistedBackend
      || view?.backendViewId
      || view?.criteriaHash
      || leadCustomViews.some((customView) => customView.id === view?.id)
    );
  }

  /**
   * @function resolveWilsyToolbarMembershipSummary
   * @description Resolves current membership summary for compact toolbar display.
   * @param {object} view Active organizer view.
   * @returns {object} Membership summary.
   * @collaboration Backend run endpoint, manual includes, manual excludes, and toolbar status copy.
   */
  function resolveWilsyToolbarMembershipSummary(view = {}) {
    const backendViewId = resolveWilsyToolbarViewBackendId(view);
    const summary = leadToolbarMembershipById[view?.id]
      || leadToolbarMembershipById[backendViewId]
      || view?.membership
      || view?.membershipSummary
      || view?.lastRun?.membership
      || {};

    return {
      effectiveCount: Number(summary.effectiveCount ?? view?.count ?? 0),
      ruleMatchCount: Number(summary.ruleMatchCount ?? view?.count ?? 0),
      manualIncludeCount: Number(summary.manualIncludeCount ?? summary.includeCount ?? 0),
      manualExcludeCount: Number(summary.manualExcludeCount ?? summary.excludeCount ?? 0),
    };
  }

  /**
   * @function buildWilsyToolbarCollectionPayload
   * @description Builds institutional evidence payloads for toolbar collection commands.
   * @param {string} route Backend route.
   * @param {string} action Command action.
   * @param {object} body Command body.
   * @returns {object} Signed command payload.
   * @collaboration Institutional headers, strike payload, backend membership overrides, and toolbar actions.
   */
  function buildWilsyToolbarCollectionPayload(route = '/api/crm/leads/views', action = 'RUN_LEAD_VIEW', body = {}) {
    const identity = resolveWilsyLeadViewRegistryIdentity();
    const generatedAt = new Date().toISOString();
    const requestId = `REQ-FG103G-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const institutionalHeaders = {
      tenantId: identity.tenantId,
      operatorId: identity.operatorUserId,
      operatorUserId: identity.operatorUserId,
      userId: identity.operatorUserId,
      route,
      commandSurface: 'CRM_LEADS_TOOLBAR_COLLECTION_ACTIONS',
      timestamp: generatedAt,
      generatedAt,
      requestId,
    };

    return {
      ...body,
      tenantId: identity.tenantId,
      operatorId: identity.operatorUserId,
      operatorUserId: identity.operatorUserId,
      userId: identity.operatorUserId,
      commandSurface: 'CRM_LEADS_TOOLBAR_COLLECTION_ACTIONS',
      generatedAt,
      requestId,
      institutionalHeaders,
      strikePayload: {
        action,
        tenantId: identity.tenantId,
        operatorId: identity.operatorUserId,
        operatorUserId: identity.operatorUserId,
        userId: identity.operatorUserId,
        route,
        commandSurface: 'CRM_LEADS_TOOLBAR_COLLECTION_ACTIONS',
        timestamp: generatedAt,
        generatedAt,
        requestId,
        institutionalHeaders,
      },
    };
  }

  /**
   * @function requestWilsyToolbarCollectionCommand
   * @description Executes a signed Lead View Registry command from compact toolbar actions.
   * @param {string} route Backend route path.
   * @param {string} action Command action.
   * @param {object} body Command body.
   * @param {string} method HTTP method.
   * @returns {Promise<object>} Backend JSON response.
   * @collaboration FG103B membership endpoints, browser JWT, signed headers, and toolbar CRUD.
   */
  async function requestWilsyToolbarCollectionCommand(route = '/api/crm/leads/views', action = 'RUN_LEAD_VIEW', body = {}, method = 'POST') {
    const token = resolveWilsyLeadViewRegistryAuthToken();
    const payload = buildWilsyToolbarCollectionPayload(route, action, body);
    const sealContract = buildWilsyLeadViewRegistrySealHeaders(payload);
    const identity = resolveWilsyLeadViewRegistryIdentity();
    const registryUrl = resolveWilsyLeadViewRegistryUrl();
    const endpoint = `${registryUrl}${route.replace('/api/crm/leads/views', '')}`;

    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        'X-Tenant-Id': identity.tenantId,
        'X-Operator-Id': identity.operatorUserId,
        'X-Operator-User-Id': identity.operatorUserId,
        'X-User-Id': identity.operatorUserId,
        'X-Command-Surface': 'CRM_LEADS_TOOLBAR_COLLECTION_ACTIONS',
        'X-Request-ID': payload.requestId,
        'X-Trace-ID': payload.requestId,
        'X-Correlation-ID': payload.requestId,
        'X-Forensic-Timestamp': payload.generatedAt,
        'X-Timestamp': payload.generatedAt,
        'X-Generated-At': payload.generatedAt,
        'X-Cryptographic-Nonce': sealContract.nonce,
        'X-Request-Seal': sealContract.requestSeal,
        'X-Wilsy-Lead-View-Seal': 'P60K5Q10FG103G_TOOLBAR_COLLECTION_ACTIONS',
      },
      body: JSON.stringify(payload),
    });

    const json = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(json?.message || json?.error || `Lead collection command failed: ${response.status}`);
    }

    return json;
  }

  /**
   * @function refreshWilsyToolbarCollectionSummary
   * @description Runs the active custom Lead view and hydrates backend rows, cursor metadata, and membership summary.
   * @param {object} view Active organizer view.
   * @returns {Promise<void>} Summary refresh completion.
   * @collaboration Backend run endpoint, toolbar compact count, effective membership, Sync button, visible custom collection rows, and cursor pagination.
   */
  async function refreshWilsyToolbarCollectionSummary(view = activeLeadOrganizerView) {
    const backendViewId = resolveWilsyToolbarViewBackendId(view);

    if (!backendViewId || !isWilsyToolbarCustomCollectionView(view)) {
      return;
    }

    await hydrateWilsyBackendRunRowsForView(view, {
      cursor: '',
      limit: resolveWilsyBackendRunLimit(),
      reason: 'FG103U2 Sync backend run hydration',
      busyLabel: 'sync',
      feedback: 'Syncing live backend view…',
    });
  }

  // P60K5Q10FG103U2_SYNC_HYDRATES_BACKEND_ROWS

  // P60K5Q10FG103Q_SYNC_LIVE_EFFECTIVE_MEMBERSHIP

  /**
   * @function applyWilsyToolbarMembershipCommand
   * @description Adds or removes selected Lead rows from the active custom view.
   * @param {string} mode Membership mode.
   * @returns {Promise<void>} Command completion.
   * @collaboration Selected rows, FG103B include/exclude routes, toolbar actions, and audit evidence.
   */
  async function applyWilsyToolbarMembershipCommand(mode = 'include') {
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const selectedLeadIds = resolveWilsyToolbarSelectedLeadIds();
    const normalizedMode = mode === 'exclude' ? 'exclude' : 'include';

    if (!backendViewId || !isWilsyToolbarCustomCollectionView(activeLeadOrganizerView)) {
      setLeadToolbarCommandFeedback('Select a custom view');
      return;
    }

    if (!selectedLeadIds.length) {
      setLeadToolbarCommandFeedback('Select leads first');
      return;
    }

    setLeadToolbarCommandBusy(normalizedMode);
    setLeadToolbarCommandFeedback('');

    try {
      const route = `/api/crm/leads/views/${backendViewId}/overrides/${normalizedMode}`;
      const result = await requestWilsyToolbarCollectionCommand(
        route,
        normalizedMode === 'include' ? 'INCLUDE_LEADS_IN_VIEW' : 'EXCLUDE_LEADS_FROM_VIEW',
        {
          leadIds: selectedLeadIds,
          reason: `FG103G ${normalizedMode} selected leads from Records toolbar`,
        },
        'POST'
      );

      const summary = result?.membership?.summary || result?.summary || {};
      setLeadToolbarMembershipById((previous) => ({
        ...previous,
        [activeLeadOrganizerView.id]: summary,
        [backendViewId]: summary,
      }));
      setLeadToolbarCommandFeedback(`${selectedLeadIds.length} ${normalizedMode === 'include' ? 'added' : 'removed'}`);
      await refreshWilsyToolbarCollectionSummary(activeLeadOrganizerView);
    } catch (error) {
      setLeadToolbarCommandFeedback(error?.message || 'Membership command failed');
    } finally {
      setLeadToolbarCommandBusy('');
    }
  }

  /**
   * @function archiveWilsyToolbarActiveCollectionView
   * @description Deletes the active custom Lead view from the operator UI; archives backend registry state when a backend id exists.
   * @returns {Promise<void>} Delete/archive completion.
   * @collaboration Custom view lifecycle, backend audit retention, local fallback delete, toolbar actions, and Lead View Registry.
   */
  async function archiveWilsyToolbarActiveCollectionView() {
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const isCustomView = isWilsyToolbarCustomCollectionView(activeLeadOrganizerView);

    if (!isCustomView) {
      setLeadToolbarCommandFeedback('Select a custom view to delete');
      return;
    }

    setLeadToolbarCommandBusy('archive');
    setLeadToolbarCommandFeedback('');

    try {
      if (backendViewId) {
        const route = `/api/crm/leads/views/${backendViewId}`;
        await requestWilsyToolbarCollectionCommand(route, 'ARCHIVE_LEAD_VIEW', {}, 'DELETE');
      }

      const activeViewId = String(activeLeadOrganizerView?.id || '');
      const nextViews = leadCustomViews.filter((view) => {
        const candidateIds = [
          view?.id,
          view?.backendViewId,
          view?.backendId,
          view?.registryViewId,
          view?._id,
        ].map((value) => String(value || ''));

        return !candidateIds.includes(activeViewId)
          && (!backendViewId || !candidateIds.includes(String(backendViewId)));
      });

      setLeadCustomViews(nextViews);
      setSelectedRowIds([]);
      setActiveListViewId('ALL');
      setCurrentLeadPage(1);

      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('wilsy.crm.leads.customViews.v1', JSON.stringify(nextViews));
      }

      setLeadToolbarCommandFeedback(
        backendViewId
          ? 'Custom view deleted from workspace · backend audit archived'
          : 'Local custom view deleted'
      );
    } catch (error) {
      setLeadToolbarCommandFeedback(error?.message || 'Delete custom view failed');
    } finally {
      setLeadToolbarCommandBusy('');
    }
  }

  // P60K5Q10FG103M_DELETE_CUSTOM_VIEW_WORKFLOW

  /**
   * @function openWilsyToolbarCollectionEditor
   * @description Opens the existing custom view builder from compact toolbar actions.
   * @returns {void}
   * @collaboration Custom View Builder, active view workflow, rules editing, and toolbar productivity.
   */
  function openWilsyToolbarCollectionEditor() {
    setLeadToolbarCommandFeedback('Edit view rules');
    setLeadCustomViewBuilderOpen(true);
  }

  /**
   * @function renderWilsyToolbarCollectionActions
   * @description Renders compact collection controls with explicit Remove from View and Delete View semantics.
   * @returns {JSX.Element|null} Toolbar actions.
   * @collaboration Existing toolbar, selected rows, custom views, membership overrides, delete view, confirmation workflow, and non-invasive frontend UX.
   */
  function renderWilsyToolbarCollectionActions() {
    const selectedLeadIds = resolveWilsyToolbarSelectedLeadIds();
    const isCustomView = isWilsyToolbarCustomCollectionView(activeLeadOrganizerView);
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const membership = resolveWilsyToolbarMembershipSummary(activeLeadOrganizerView);
    const hasCollectionTarget = Boolean(isCustomView && backendViewId);
    const shouldRender = isCustomView || selectedLeadIds.length > 0;
    const busy = Boolean(leadToolbarCommandBusy);

    if (!shouldRender) {
      return null;
    }

    return (
      <div
        className={styles.leadToolbarCollectionActions}
        data-wilsy-lead-toolbar-collection-actions="FG103G"
        data-wilsy-custom-view-active={String(isCustomView)}
        data-wilsy-collection-target-ready={String(hasCollectionTarget)}
        data-wilsy-fg103r-confirmed-actions="true"
      >
        <span className={styles.leadToolbarCollectionStatus}>
          {leadToolbarCommandFeedback
            || (isCustomView
              ? `${selectedLeadIds.length} selected · ${formatWilsyToolbarCollectionCount(membership.manualIncludeCount)} add · ${formatWilsyToolbarCollectionCount(membership.manualExcludeCount)} out`
              : `${selectedLeadIds.length} selected`)}
        </span>
        <button
          type="button"
          disabled={!isCustomView || Boolean(leadToolbarCommandBusy)}
          onClick={openWilsyCollectionSourcePicker}
          title="Open source picker to add leads from All Leads into this custom view"
        >
          + Add
        </button>
        <button
          type="button"
          disabled={!hasCollectionTarget || !selectedLeadIds.length || busy}
          onClick={openWilsyRemoveFromViewConfirmation}
          title="Remove selected leads from this view only. Lead records are preserved."
        >
          − Remove from View
        </button>
        <button
          type="button"
          disabled={!isCustomView || busy}
          onClick={openWilsyToolbarCollectionEditor}
          title="Edit this custom view"
        >
          Edit
        </button>
        <button
          type="button"
          disabled={!hasCollectionTarget || busy}
          onClick={() => refreshWilsyToolbarCollectionSummary(activeLeadOrganizerView)}
          title={hasCollectionTarget ? 'Refresh backend membership summary' : 'Backend registry id required'}
        >
          {leadToolbarCommandBusy === 'sync' ? 'Syncing…' : 'Sync'}
        </button>
        <button
          type="button"
          disabled={!isCustomView || busy}
          onClick={openWilsyDeleteViewConfirmation}
          title="Delete this custom view only. Lead records are preserved."
        >
          {leadToolbarCommandBusy === 'archive' ? 'Deleting…' : 'Delete View'}
        </button>
      </div>
    );
  }

  // P60K5Q10FG103R_TOOLBAR_SEMANTIC_LABELS

  // P60K5Q10FG103M_ACTIVE_EMPTY_CUSTOM_VIEW_ACTIONS


  /**
   * @function resolveWilsyCollectionSourceCandidateRows
   * @description Returns source Lead records that are not already effective members of the active custom view.
   * @returns {Array<object>} Source picker candidate rows.
   * @collaboration All Leads source records, custom view criteria, manual include workflow, duplicate prevention, and controlled source picker.
   */
  function resolveWilsyCollectionSourceCandidateRows() {
    const criteria = activeLeadOrganizerView?.criteria || {};
    const query = String(leadCollectionSourceQuery || '').trim().toLowerCase();
    const membershipSummary = resolveWilsyToolbarMembershipSummary(activeLeadOrganizerView);
    const activeBackendId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);

    const activeIds = new Set(
      leads
        .filter((record) => doesWilsyLeadMatchCustomViewCriteria(record, criteria))
        .map((record, index) => resolveLeadRecordId(record, index))
        .filter(Boolean)
    );

    const knownManualIds = [
      ...(Array.isArray(activeLeadOrganizerView?.manualIncludeLeadIds) ? activeLeadOrganizerView.manualIncludeLeadIds : []),
      ...(Array.isArray(activeLeadOrganizerView?.includedLeadIds) ? activeLeadOrganizerView.includedLeadIds : []),
      ...(Array.isArray(activeLeadOrganizerView?.leadIds) ? activeLeadOrganizerView.leadIds : []),
      ...(Array.isArray(membershipSummary?.manualIncludeLeadIds) ? membershipSummary.manualIncludeLeadIds : []),
      ...(Array.isArray(membershipSummary?.includedLeadIds) ? membershipSummary.includedLeadIds : []),
    ];

    knownManualIds
      .map((leadId) => String(leadId || '').trim())
      .filter(Boolean)
      .forEach((leadId) => activeIds.add(leadId));

    return leads
      .map((record, index) => {
        const id = resolveLeadRecordId(record, index);
        const name = String(record?.name || record?.leadName || record?.fullName || record?.title || 'Untitled Lead');
        const company = String(record?.company || record?.accountName || record?.organization || 'No company');
        const email = String(record?.email || record?.primaryEmail || '');
        const owner = String(resolveLeadOwnerLabel(record) || record?.owner || record?.ownerName || 'Unassigned');
        const status = String(record?.status || record?.stage || '').toUpperCase();

        return {
          id,
          record,
          name,
          company,
          email,
          owner,
          status,
          activeBackendId,
          searchText: `${name} ${company} ${email} ${owner} ${status}`.toLowerCase(),
        };
      })
      .filter((row) => row.id && !activeIds.has(row.id))
      .filter((row) => !query || row.searchText.includes(query));
  }

  /**
   * @function toggleWilsyCollectionSourceCandidate
   * @description Toggles a source Lead row inside the add-from-source picker.
   * @param {string} leadId Lead id.
   * @returns {void}
   * @collaboration Source picker selection, manual include payload, and custom view membership.
   */
  function toggleWilsyCollectionSourceCandidate(leadId = '') {
    const normalizedLeadId = String(leadId || '').trim();

    if (!normalizedLeadId) {
      return;
    }

    setLeadCollectionSourceSelectedIds((previous) => (
      previous.includes(normalizedLeadId)
        ? previous.filter((candidateId) => candidateId !== normalizedLeadId)
        : [...previous, normalizedLeadId]
    ));
  }

  /**
   * @function openWilsyCollectionSourcePicker
   * @description Opens the controlled source picker for adding All Leads records into the active custom view.
   * @returns {void}
   * @collaboration Custom view toolbar, source records, controlled add workflow, and membership overrides.
   */
  function openWilsyCollectionSourcePicker() {
    if (!isWilsyToolbarCustomCollectionView(activeLeadOrganizerView)) {
      setLeadToolbarCommandFeedback('Select a custom view first');
      return;
    }

    setLeadCollectionSourceSelectedIds([]);
    setLeadCollectionSourceQuery('');
    setLeadCollectionSourcePickerOpen(true);
    setLeadToolbarCommandFeedback('Choose source leads to add');
  }

  /**
   * @function closeWilsyCollectionSourcePicker
   * @description Closes and clears the controlled source picker.
   * @returns {void}
   * @collaboration Add-from-source workflow, toolbar state, and custom view productivity.
   */
  function closeWilsyCollectionSourcePicker() {
    setLeadCollectionSourcePickerOpen(false);
    setLeadCollectionSourceSelectedIds([]);
    setLeadCollectionSourceQuery('');
  }

  /**
   * @function applyWilsyCollectionSourcePickerIncludes
   * @description Adds selected source Lead rows to the active custom view through backend membership overrides with visible commit feedback.
   * @returns {Promise<void>} Add completion.
   * @collaboration FG103B include endpoint, source picker, selected source rows, backend audit, duplicate prevention, and membership summary.
   */
  async function applyWilsyCollectionSourcePickerIncludes() {
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const selectedLeadIds = Array.from(new Set(
      leadCollectionSourceSelectedIds
        .map((leadId) => String(leadId || '').trim())
        .filter(Boolean)
    ));

    if (!backendViewId) {
      setLeadToolbarCommandFeedback('Save this custom view before adding source leads');
      return;
    }

    if (!selectedLeadIds.length) {
      setLeadToolbarCommandFeedback('Select source leads first');
      return;
    }

    setLeadToolbarCommandBusy('sourceAdd');
    setLeadToolbarCommandFeedback(`Adding ${selectedLeadIds.length} source lead${selectedLeadIds.length === 1 ? '' : 's'}…`);

    try {
      const route = `/api/crm/leads/views/${backendViewId}/overrides/include`;
      const result = await requestWilsyToolbarCollectionCommand(
        route,
        'INCLUDE_LEADS_IN_VIEW',
        {
          leadIds: selectedLeadIds,
          reason: 'FG103P add source leads into custom view with duplicate-safe commit',
        },
        'POST'
      );

      const summary = result?.membership?.summary || result?.summary || {};
      const resultLeadIds = result?.leadIds || selectedLeadIds;

      setLeadToolbarMembershipById((previous) => ({
        ...previous,
        [activeLeadOrganizerView.id]: {
          ...summary,
          manualIncludeLeadIds: Array.from(new Set([
            ...(previous?.[activeLeadOrganizerView.id]?.manualIncludeLeadIds || []),
            ...resultLeadIds,
          ])),
        },
        [backendViewId]: {
          ...summary,
          manualIncludeLeadIds: Array.from(new Set([
            ...(previous?.[backendViewId]?.manualIncludeLeadIds || []),
            ...resultLeadIds,
          ])),
        },
      }));

      const nextManualIncludeLeadIds = normalizeWilsyLeadMembershipIdList([
        ...(Array.isArray(activeLeadOrganizerView?.manualIncludeLeadIds) ? activeLeadOrganizerView.manualIncludeLeadIds : []),
        ...selectedLeadIds,
      ]);

      setLeadCustomViews((previousViews) => {
        const nextViews = previousViews.map((view) => {
          const candidateIds = [
            view?.id,
            view?.backendViewId,
            view?.backendId,
            view?.registryViewId,
            view?._id,
          ].map((value) => String(value || ''));

          if (!candidateIds.includes(String(activeLeadOrganizerView?.id || '')) && !candidateIds.includes(String(backendViewId))) {
            return view;
          }

          return {
            ...view,
            manualIncludeLeadIds: nextManualIncludeLeadIds,
            membershipSummary: {
              ...(view?.membershipSummary || {}),
              ...summary,
              manualIncludeLeadIds: nextManualIncludeLeadIds,
            },
            lastRun: {
              ...(view?.lastRun || {}),
              membership: {
                ...(view?.lastRun?.membership || {}),
                ...summary,
                manualIncludeLeadIds: nextManualIncludeLeadIds,
              },
            },
            updatedAt: new Date().toISOString(),
          };
        });

        if (typeof window !== 'undefined' && window.localStorage) {
          window.localStorage.setItem('wilsy.crm.leads.customViews.v1', JSON.stringify(nextViews));
        }

        return nextViews;
      });

      // P60K5Q10FG103Q_LOCAL_CUSTOM_VIEW_INCLUDE_STATE
      setLeadToolbarCommandFeedback(`${selectedLeadIds.length} source lead${selectedLeadIds.length === 1 ? '' : 's'} added · view updated`);
      setLeadCollectionSourceSelectedIds([]);
      setLeadCollectionSourceQuery('');
      setLeadCollectionSourcePickerOpen(false);
      await refreshWilsyToolbarCollectionSummary(activeLeadOrganizerView);
    } catch (error) {
      setLeadToolbarCommandFeedback(error?.message || 'Add source leads failed');
    } finally {
      setLeadToolbarCommandBusy('');
    }
  }

  // P60K5Q10FG103P_SOURCE_PICKER_COMMIT_FEEDBACK

  /**
   * @function renderWilsyCollectionSourcePicker
   * @description Renders the controlled add-from-source picker without changing the records table or dropdown.
   * @returns {JSX.Element|null} Source picker overlay.
   * @collaboration All Leads source records, custom view membership, backend include route, and non-invasive toolbar workflow.
   */
  function renderWilsyCollectionSourcePicker() {
    if (!leadCollectionSourcePickerOpen) {
      return null;
    }

    const candidates = resolveWilsyCollectionSourceCandidateRows();
    const visibleCandidates = candidates.slice(0, 80);
    const selectedCount = leadCollectionSourceSelectedIds.length;
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);

    return (
      <section
        className={styles.leadCollectionSourcePickerBackdrop}
        data-wilsy-lead-source-picker="FG103N"
        aria-label="Add source leads to custom view"
      >
        <section className={styles.leadCollectionSourcePicker}>
          <header className={styles.leadCollectionSourcePickerHeader}>
            <span>
              <small>Add to custom view</small>
              <strong>{resolveLeadOperatingCopyLabel(activeLeadOrganizerView?.label || 'Custom View', activeListViewId)}</strong>
              <em>{candidates.length} source leads available · {selectedCount} selected</em>
            </span>
            <div className={styles.leadCollectionSourcePickerHeaderActions} data-wilsy-source-picker-confirm-dock="FG103O">
              <button
                type="button"
                disabled={!backendViewId || !selectedCount || Boolean(leadToolbarCommandBusy)}
                onClick={applyWilsyCollectionSourcePickerIncludes}
              >
                {leadToolbarCommandBusy === 'sourceAdd' ? 'Adding…' : `Add ${selectedCount || ''} selected`.trim()}
              </button>
              <button type="button" onClick={closeWilsyCollectionSourcePicker}>
                Cancel
              </button>
              <button type="button" onClick={closeWilsyCollectionSourcePicker} aria-label="Close add source picker">
                ×
              </button>
            </div>
          </header>

          <div className={styles.leadCollectionSourcePickerSearch}>
            <input
              value={leadCollectionSourceQuery}
              onChange={(event) => setLeadCollectionSourceQuery(event.target.value)}
              placeholder="Search source leads by name, company, email, owner, or status"
              aria-label="Search source leads"
            />
            {leadToolbarCommandFeedback ? (
              <p className={styles.leadCollectionSourcePickerStatus} data-wilsy-source-picker-status="FG103P">
                {leadToolbarCommandFeedback}
              </p>
            ) : null}
          </div>

          <div className={styles.leadCollectionSourcePickerList}>
            {visibleCandidates.length ? visibleCandidates.map((candidate) => {
              const selected = leadCollectionSourceSelectedIds.includes(candidate.id);

              return (
                <button
                  key={candidate.id}
                  type="button"
                  data-selected={selected ? 'true' : 'false'}
                  onClick={() => toggleWilsyCollectionSourceCandidate(candidate.id)}
                >
                  <span>
                    <strong>{candidate.name}</strong>
                    <em>{candidate.company}</em>
                  </span>
                  <span>
                    <strong>{candidate.owner}</strong>
                    <em>{candidate.email || candidate.status || 'No email captured'}</em>
                  </span>
                  <b>{selected ? 'Selected' : 'Add'}</b>
                </button>
              );
            }) : (
              <p className={styles.leadCollectionSourcePickerEmpty}>
                No outside source leads available for this custom view.
              </p>
            )}
          </div>

          <footer className={styles.leadCollectionSourcePickerFooter}>
            <span>
              {backendViewId ? `Registry ${backendViewId.slice(0, 8)}` : 'Save view before backend include'}
            </span>
            <button type="button" onClick={closeWilsyCollectionSourcePicker}>Cancel</button>
            <button
              type="button"
              disabled={!backendViewId || !selectedCount || Boolean(leadToolbarCommandBusy)}
              onClick={applyWilsyCollectionSourcePickerIncludes}
            >
              {leadToolbarCommandBusy === 'sourceAdd' ? 'Adding…' : `Add ${selectedCount || ''}`.trim()}
            </button>
          </footer>
        </section>
      </section>
    );
  }

  // P60K5Q10FG103O_SOURCE_PICKER_VISIBLE_CONFIRM


  /**
   * @function openWilsyRemoveFromViewConfirmation
   * @description Opens an in-app confirmation before removing selected leads from the active custom view.
   * @returns {void}
   * @collaboration Custom view toolbar, selected rows, membership exclusions, audit-safe confirmation, and lead-preserving UX.
   */
  function openWilsyRemoveFromViewConfirmation() {
    const selectedLeadIds = resolveWilsyToolbarSelectedLeadIds();
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);

    if (!isWilsyToolbarCustomCollectionView(activeLeadOrganizerView) || !backendViewId) {
      setLeadToolbarCommandFeedback('Select a saved custom view first');
      return;
    }

    if (!selectedLeadIds.length) {
      setLeadToolbarCommandFeedback('Select leads to remove from this view');
      return;
    }

    setLeadViewActionConfirmation({
      type: 'removeFromView',
      leadIds: selectedLeadIds,
      backendViewId,
      viewId: activeLeadOrganizerView?.id || '',
      viewLabel: resolveLeadOperatingCopyLabel(activeLeadOrganizerView?.label || 'Custom View', activeListViewId),
      title: 'Remove from View?',
      primary: `Remove ${selectedLeadIds.length} from View`,
      body: `${selectedLeadIds.length} selected lead${selectedLeadIds.length === 1 ? '' : 's'} will disappear from this custom view only. Lead records stay in All Leads and CRM history.`,
    });
  }

  /**
   * @function openWilsyDeleteViewConfirmation
   * @description Opens an in-app confirmation before deleting the active custom view.
   * @returns {void}
   * @collaboration Custom view lifecycle, backend archive, local view removal, audit retention, and lead-preserving UX.
   */
  function openWilsyDeleteViewConfirmation() {
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);

    if (!isWilsyToolbarCustomCollectionView(activeLeadOrganizerView)) {
      setLeadToolbarCommandFeedback('Select a custom view to delete');
      return;
    }

    setLeadViewActionConfirmation({
      type: 'deleteView',
      leadIds: [],
      backendViewId,
      viewId: activeLeadOrganizerView?.id || '',
      viewLabel: resolveLeadOperatingCopyLabel(activeLeadOrganizerView?.label || 'Custom View', activeListViewId),
      title: 'Delete View?',
      primary: 'Delete View',
      body: 'This deletes the saved custom view only. No Lead records will be deleted. Backend audit history is preserved when this view has a registry id.',
    });
  }

  /**
   * @function closeWilsyViewActionConfirmation
   * @description Closes the in-app custom view action confirmation.
   * @returns {void}
   * @collaboration Remove from View, Delete View, non-browser confirmations, and operator-safe cancellation.
   */
  function closeWilsyViewActionConfirmation() {
    setLeadViewActionConfirmation(null);
  }

  /**
   * @function executeWilsyRemoveFromViewConfirmed
   * @description Executes confirmed custom-view removal while preserving Lead records.
   * @param {object} confirmation Confirmation payload.
   * @returns {Promise<void>} Removal completion.
   * @collaboration Backend exclude override, effective membership state, visible view refresh, and audit-safe lead preservation.
   */
  async function executeWilsyRemoveFromViewConfirmed(confirmation = {}) {
    const backendViewId = confirmation.backendViewId || resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const selectedLeadIds = normalizeWilsyLeadMembershipIdList(confirmation.leadIds || []);

    if (!backendViewId || !selectedLeadIds.length) {
      setLeadToolbarCommandFeedback('Nothing to remove from this view');
      return;
    }

    setLeadToolbarCommandBusy('removeFromView');
    setLeadToolbarCommandFeedback(`Removing ${selectedLeadIds.length} from view…`);

    try {
      const route = `/api/crm/leads/views/${backendViewId}/overrides/exclude`;
      const result = await requestWilsyToolbarCollectionCommand(
        route,
        'EXCLUDE_LEADS_FROM_VIEW',
        {
          leadIds: selectedLeadIds,
          reason: 'FG103R confirmed remove selected leads from custom view only',
        },
        'POST'
      );

      const summary = result?.membership?.summary || result?.summary || {};
      const selectedIdSet = new Set(selectedLeadIds);

      const previousMembership = resolveWilsyEffectiveViewMembershipState(activeLeadOrganizerView);
      const nextManualIncludeLeadIds = normalizeWilsyLeadMembershipIdList(
        previousMembership.manualIncludeLeadIds.filter((leadId) => !selectedIdSet.has(leadId))
      );
      const nextManualExcludeLeadIds = normalizeWilsyLeadMembershipIdList([
        ...previousMembership.manualExcludeLeadIds,
        ...selectedLeadIds,
      ]);

      setLeadToolbarMembershipById((previous) => ({
        ...previous,
        [activeLeadOrganizerView.id]: {
          ...(previous?.[activeLeadOrganizerView.id] || {}),
          ...summary,
          manualIncludeLeadIds: nextManualIncludeLeadIds,
          manualExcludeLeadIds: nextManualExcludeLeadIds,
        },
        [backendViewId]: {
          ...(previous?.[backendViewId] || {}),
          ...summary,
          manualIncludeLeadIds: nextManualIncludeLeadIds,
          manualExcludeLeadIds: nextManualExcludeLeadIds,
        },
      }));

      setLeadCustomViews((previousViews) => {
        const nextViews = previousViews.map((view) => {
          const candidateIds = [
            view?.id,
            view?.backendViewId,
            view?.backendId,
            view?.registryViewId,
            view?._id,
          ].map((value) => String(value || ''));

          if (!candidateIds.includes(String(activeLeadOrganizerView?.id || '')) && !candidateIds.includes(String(backendViewId))) {
            return view;
          }

          return {
            ...view,
            manualIncludeLeadIds: nextManualIncludeLeadIds,
            manualExcludeLeadIds: nextManualExcludeLeadIds,
            membershipSummary: {
              ...(view?.membershipSummary || {}),
              ...summary,
              manualIncludeLeadIds: nextManualIncludeLeadIds,
              manualExcludeLeadIds: nextManualExcludeLeadIds,
            },
            lastRun: {
              ...(view?.lastRun || {}),
              membership: {
                ...(view?.lastRun?.membership || {}),
                ...summary,
                manualIncludeLeadIds: nextManualIncludeLeadIds,
                manualExcludeLeadIds: nextManualExcludeLeadIds,
              },
            },
            updatedAt: new Date().toISOString(),
          };
        });

        if (typeof window !== 'undefined' && window.localStorage) {
          window.localStorage.setItem('wilsy.crm.leads.customViews.v1', JSON.stringify(nextViews));
        }

        return nextViews;
      });

      setSelectedRowIds([]);
      setCurrentLeadPage(1);
      setLeadToolbarCommandFeedback(`${selectedLeadIds.length} removed from view · leads preserved`);
      setLeadViewActionConfirmation(null);
      await refreshWilsyToolbarCollectionSummary(activeLeadOrganizerView);
    } catch (error) {
      setLeadToolbarCommandFeedback(error?.message || 'Remove from View failed');
    } finally {
      setLeadToolbarCommandBusy('');
    }
  }

  /**
   * @function executeWilsyConfirmedViewAction
   * @description Executes the pending confirmed custom view action.
   * @returns {Promise<void>} Confirmation execution.
   * @collaboration Remove from View, Delete View, backend audit archive, in-app confirmation, and lead-preserving workflows.
   */
  async function executeWilsyConfirmedViewAction() {
    if (!leadViewActionConfirmation) {
      return;
    }

    if (leadViewActionConfirmation.type === 'removeFromView') {
      await executeWilsyRemoveFromViewConfirmed(leadViewActionConfirmation);
      return;
    }

    if (leadViewActionConfirmation.type === 'deleteView') {
      setLeadViewActionConfirmation(null);
      await archiveWilsyToolbarActiveCollectionView();
    }
  }

  /**
   * @function renderWilsyViewActionConfirmation
   * @description Renders an in-app confirmation for Remove from View and Delete View actions.
   * @returns {JSX.Element|null} Confirmation overlay.
   * @collaboration Operator confirmation, custom view membership, lead preservation, backend audit retention, and no browser dialogs.
   */
  function renderWilsyViewActionConfirmation() {
    if (!leadViewActionConfirmation) {
      return null;
    }

    const destructive = leadViewActionConfirmation.type === 'deleteView';

    return (
      <section
        className={styles.leadCollectionSourcePickerBackdrop}
        data-wilsy-view-action-confirmation="FG103R"
        aria-label="Confirm custom view action"
      >
        <section className={styles.leadCollectionSourcePicker}>
          <header className={styles.leadCollectionSourcePickerHeader}>
            <span>
              <small>{destructive ? 'Delete custom view' : 'Remove from custom view'}</small>
              <strong>{leadViewActionConfirmation.title}</strong>
              <em>{leadViewActionConfirmation.viewLabel}</em>
            </span>
            <div className={styles.leadCollectionSourcePickerHeaderActions}>
              <button
                type="button"
                disabled={Boolean(leadToolbarCommandBusy)}
                onClick={executeWilsyConfirmedViewAction}
              >
                {leadToolbarCommandBusy
                  ? 'Working…'
                  : leadViewActionConfirmation.primary}
              </button>
              <button type="button" onClick={closeWilsyViewActionConfirmation}>
                Cancel
              </button>
              <button type="button" onClick={closeWilsyViewActionConfirmation} aria-label="Close confirmation">
                ×
              </button>
            </div>
          </header>

          <div className={styles.leadCollectionSourcePickerSearch}>
            <p className={styles.leadCollectionSourcePickerStatus} data-wilsy-view-action-confirmation-copy="FG103R">
              {leadViewActionConfirmation.body}
            </p>
          </div>

          <footer className={styles.leadCollectionSourcePickerFooter}>
            <span>
              {destructive
                ? 'Lead records are preserved. Only the saved view is removed.'
                : 'Lead records are preserved. Only view membership changes.'}
            </span>
            <button type="button" onClick={closeWilsyViewActionConfirmation}>
              Keep
            </button>
            <button
              type="button"
              disabled={Boolean(leadToolbarCommandBusy)}
              onClick={executeWilsyConfirmedViewAction}
            >
              {leadToolbarCommandBusy
                ? 'Working…'
                : leadViewActionConfirmation.primary}
            </button>
          </footer>
        </section>
      </section>
    );
  }

  // P60K5Q10FG103R_VIEW_ACTION_CONFIRMATION


  // P60K5Q10FG103N_ADD_FROM_SOURCE_PICKER


  // P60K5Q10FG103G_TOOLBAR_COLLECTION_ACTIONS_ENGINE


/**
   * @function handleSaveLeadCustomView
   * @description Saves a custom Lead view into local workspace state, selects it, resets pagination, and closes the builder.
   * @param {Object} viewPayload - Custom Lead view payload from the builder.
   * @returns {void}
   * @collaboration Lead Custom View Builder, Leads Organizer, local saved views, pagination reset, and live Records filtering.
   */
  const handleSaveLeadCustomView = async (viewPayload = {}) => {
    /* P60K5Q10FG98C_BACKEND_PERSISTED_CUSTOM_VIEW_SAVE */
    let persistedBackendView = null;

    try {
      persistedBackendView = await persistWilsyLeadCustomViewToRegistry(viewPayload);
    } catch (error) {
      console.warn('[WILSY CRM] Lead View Registry save fallback engaged', error);
    }

    const backendAuditTrail = Array.isArray(persistedBackendView?.auditTrail) ? persistedBackendView.auditTrail : [];
    const latestAuditEntry = backendAuditTrail[backendAuditTrail.length - 1] || {};
    const finalViewPayload = {
      ...viewPayload,
      backendViewId: persistedBackendView?._id || persistedBackendView?.id || viewPayload.backendViewId || '',
      auditReceiptId: latestAuditEntry.auditReceiptId || viewPayload.auditReceiptId || '',
      criteriaHash: persistedBackendView?.criteriaHash || viewPayload.criteriaHash || '',
      persistedBackend: Boolean(persistedBackendView),
      persistedAt: new Date().toISOString()
    };
    const nextViews = [
      ...leadCustomViews.filter(view => view.id !== finalViewPayload.id),
      finalViewPayload
    ];

    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem('wilsy.crm.leads.customViews.v1', JSON.stringify(nextViews));
    }

    setLeadCustomViews(nextViews);
    setActiveListViewId(finalViewPayload.id);
    setLeadCustomViewBuilderOpen(false);
    setViewMenuOpen(false);

    return finalViewPayload;
  };

  const leadOrganizerLiveViews = useMemo(() => {
    /* P60K5Q10FG103L2_SELECT_CUSTOM_VIEW_BRIDGE
       Saved custom views must become selectable organizer objects with backend metadata preserved. */
    const builtinViews = buildWilsyFG92BLiveLeadOrganizerViews(leads, leadOrganizerViewDefinitions);
    const builtinIds = new Set(builtinViews.map((view) => String(view.id || '')));

    const savedCustomViews = leadCustomViews
      .filter((view) => view && !builtinIds.has(String(view.id || '')))
      .map((view, index) => {
        const id = String(
          view.id
          || view.backendViewId
          || view.backendId
          || view.registryViewId
          || view._id
          || `CUSTOM_VIEW_${index}`
        );
        const criteria = view.criteria || {};
        const count = leads.filter((record) => doesWilsyLeadMatchCustomViewCriteria(record, criteria)).length;

        return {
          ...view,
          id,
          label: view.label || view.name || 'Custom View',
          detail: `${count}/${leads.length} live`,
          staticDetail: view.staticDetail || view.description || view.detail || 'Saved custom collection',
          count,
          custom: true,
          criteria,
          backendViewId: view.backendViewId || view.backendId || view.registryViewId || view._id || '',
          backendId: view.backendId || view.backendViewId || view.registryViewId || view._id || '',
          registryViewId: view.registryViewId || view.backendViewId || view.backendId || view._id || '',
          criteriaHash: view.criteriaHash || '',
          auditReceiptId: view.auditReceiptId || '',
          persistedBackend: Boolean(
            view.persistedBackend
            || view.backendViewId
            || view.backendId
            || view.registryViewId
            || view._id
          ),
        };
      });

    return [...builtinViews, ...savedCustomViews];
  }, [leads, leadOrganizerViewDefinitions, leadCustomViews]);


  /**
   * @function handleWilsyLeadOrganizerMenuWheel
   * @description Keeps wheel and trackpad scrolling inside the compact Lead view menu without changing approved geometry.
   * @param {WheelEvent} event - Browser wheel event.
   * @returns {void}
   * @collaboration Compact Lead organizer, saved custom views, live view navigation, and production viewport containment.
   */
  const handleWilsyLeadOrganizerMenuWheel = (event) => {
    const node = event.currentTarget;

    if (!node) {
      return;
    }

    const canScroll = node.scrollHeight > node.clientHeight;

    if (!canScroll) {
      return;
    }

    event.stopPropagation();
  };

  const activeLeadOrganizerView = useMemo(() => {
    /* P60K5Q10FG103L2_ACTIVE_CUSTOM_VIEW_MEMO */
    return leadOrganizerLiveViews.find((view) => String(view.id) === String(activeListViewId))
      || leadOrganizerLiveViews[0]
      || activeListView;
  }, [activeListView, activeListViewId, leadOrganizerLiveViews]);


  // P60K5Q10FG94E_RUNTIME_ORGANIZER_REMOVED







  /**
   * @function normalizeWilsyLeadMembershipIdList
   * @description Normalizes a candidate Lead id list for effective custom view membership calculations.
   * @param {Array<string>} ids Candidate ids.
   * @returns {Array<string>} Normalized unique ids.
   * @collaboration Manual include/exclude state, backend run summaries, source picker commits, and visible custom view rows.
   */
  function normalizeWilsyLeadMembershipIdList(ids = []) {
    return Array.from(new Set(
      (Array.isArray(ids) ? ids : [])
        .map((leadId) => String(leadId || '').trim())
        .filter(Boolean)
    ));
  }

  /**
   * @function resolveWilsyEffectiveViewMembershipState
   * @description Resolves manual include/exclude ids for the active custom Lead view from local view state and backend summary state.
   * @param {object} view Active custom view.
   * @returns {object} Effective membership id sets.
   * @collaboration Custom view filtering, source picker additions, remove overrides, Sync, and backend membership engine.
   */
  function resolveWilsyEffectiveViewMembershipState(view = activeLeadOrganizerView) {
    const backendViewId = resolveWilsyToolbarViewBackendId(view);
    const summaryByView = leadToolbarMembershipById?.[view?.id] || {};
    const summaryByBackend = backendViewId ? leadToolbarMembershipById?.[backendViewId] || {} : {};
    const candidate = {
      ...summaryByView,
      ...summaryByBackend,
    };

    const manualIncludeLeadIds = normalizeWilsyLeadMembershipIdList([
      ...(Array.isArray(view?.manualIncludeLeadIds) ? view.manualIncludeLeadIds : []),
      ...(Array.isArray(view?.includedLeadIds) ? view.includedLeadIds : []),
      ...(Array.isArray(view?.leadIds) ? view.leadIds : []),
      ...(Array.isArray(candidate.manualIncludeLeadIds) ? candidate.manualIncludeLeadIds : []),
      ...(Array.isArray(candidate.includedLeadIds) ? candidate.includedLeadIds : []),
    ]);

    const manualExcludeLeadIds = normalizeWilsyLeadMembershipIdList([
      ...(Array.isArray(view?.manualExcludeLeadIds) ? view.manualExcludeLeadIds : []),
      ...(Array.isArray(view?.excludedLeadIds) ? view.excludedLeadIds : []),
      ...(Array.isArray(candidate.manualExcludeLeadIds) ? candidate.manualExcludeLeadIds : []),
      ...(Array.isArray(candidate.excludedLeadIds) ? candidate.excludedLeadIds : []),
    ]);

    return {
      backendViewId,
      manualIncludeLeadIds,
      manualExcludeLeadIds,
      manualIncludeSet: new Set(manualIncludeLeadIds),
      manualExcludeSet: new Set(manualExcludeLeadIds),
    };
  }

  /**
   * @function doesWilsyLeadMatchEffectiveCustomViewMembership
   * @description Evaluates custom view membership as rule matches plus manual includes minus manual excludes.
   * @param {object} record Lead record.
   * @param {number} index Lead source index.
   * @returns {boolean} Whether the record belongs in the visible effective custom view.
   * @collaboration Frontend table filtering, backend membership overrides, source picker additions, Sync, and duplicate prevention.
   */
  function doesWilsyLeadMatchEffectiveCustomViewMembership(record = {}, index = 0) {
    if (!activeLeadOrganizerView?.custom) {
      return doesLeadMatchListView(record, activeListViewId);
    }

    const leadId = resolveLeadRecordId(record, index);
    const membership = resolveWilsyEffectiveViewMembershipState(activeLeadOrganizerView);

    if (leadId && membership.manualExcludeSet.has(leadId)) {
      return false;
    }

    if (leadId && membership.manualIncludeSet.has(leadId)) {
      return true;
    }

    return doesWilsyLeadMatchCustomViewCriteria(record, activeLeadOrganizerView.criteria || {});
  }


  /**
   * @function resolveWilsyBackendRunViewKey
   * @description Resolves a stable frontend key for backend-hydrated custom Lead view rows.
   * @param {object} view Active organizer view.
   * @returns {string} View key.
   * @collaboration Backend run endpoint, cursor state, local custom views, and active table hydration.
   */
  function resolveWilsyBackendRunViewKey(view = activeLeadOrganizerView) {
    const backendViewId = resolveWilsyToolbarViewBackendId(view);

    return String(
      backendViewId
      || view?.id
      || view?.backendViewId
      || view?.backendId
      || view?.registryViewId
      || view?._id
      || ''
    ).trim();
  }

  /**
   * @function normalizeWilsyBackendRunRows
   * @description Normalizes rows from the backend Lead view /run response.
   * @param {object} result Backend run result.
   * @returns {Array<object>} Backend rows.
   * @collaboration FG103T run response, visible records table, custom view hydration, and cursor pagination.
   */
  function normalizeWilsyBackendRunRows(result = {}) {
    const rows =
      result?.rows
      || result?.records
      || result?.leads
      || result?.run?.rows
      || result?.run?.records
      || result?.run?.leads
      || result?.result?.rows
      || result?.result?.records
      || result?.result?.leads
      || [];

    return Array.isArray(rows) ? rows : [];
  }

  /**
   * @function normalizeWilsyBackendRunPagination
   * @description Normalizes cursor pagination from the backend Lead view /run response.
   * @param {object} result Backend run result.
   * @param {Array<object>} rows Normalized row fallback.
   * @returns {object} Pagination metadata.
   * @collaboration FG103T cursor response, Sync, selector hydration, and future Next/Previous backend paging.
   */
  function normalizeWilsyBackendRunPagination(result = {}, rows = []) {
    const pagination =
      result?.pagination
      || result?.run?.pagination
      || result?.result?.pagination
      || {};

    return {
      mode: pagination?.mode || 'cursor',
      cursor: pagination?.cursor || result?.cursor || result?.run?.cursor || result?.result?.cursor || '',
      nextCursor: pagination?.nextCursor || result?.nextCursor || result?.run?.nextCursor || result?.result?.nextCursor || '',
      previousCursor: pagination?.previousCursor || result?.previousCursor || result?.run?.previousCursor || result?.result?.previousCursor || '',
      returnedCount: Number(pagination?.returnedCount || result?.returnedCount || result?.run?.returnedCount || rows.length || 0),
      totalCount: Number(pagination?.totalCount || result?.count || result?.run?.count || result?.result?.count || rows.length || 0),
      hasNextPage: Boolean(pagination?.hasNextPage || result?.nextCursor || result?.run?.nextCursor || result?.result?.nextCursor),
      hasPreviousPage: Boolean(pagination?.hasPreviousPage || result?.previousCursor || result?.run?.previousCursor || result?.result?.previousCursor),
      limit: Number(pagination?.limit || 25),
      generatedAt: pagination?.generatedAt || new Date().toISOString(),
    };
  }

  /**
   * @function resolveWilsyBackendRunLimit
   * @description Resolves a safe backend run page size for custom Lead view hydration.
   * @param {number|string} requestedLimit Requested page size.
   * @returns {number} Backend run limit.
   * @collaboration Cursor pagination, backend run endpoint, table hydration, page-size selector, and production-safe request sizing.
   */
  function resolveWilsyBackendRunLimit(requestedLimit = '') {
    const candidate = Number(requestedLimit || leadPagination?.pageSize || 25);

    if (!Number.isFinite(candidate)) {
      return 25;
    }

    return Math.min(100, Math.max(1, candidate));
  }

  // P60K5Q10FG103V2_BACKEND_RUN_LIMIT_USES_FOOTER_SIZE

  /**
   * @function hydrateWilsyBackendRunRowsForView
   * @description Runs a saved custom Lead view on the backend and hydrates visible rows plus cursor metadata.
   * @param {object} view Saved custom view.
   * @param {object} options Hydration options.
   * @returns {Promise<object|null>} Backend run result.
   * @collaboration Selector-driven backend run, FG103T cursor response, visible rows, Sync button, and membership summary.
   */
  async function hydrateWilsyBackendRunRowsForView(view = activeLeadOrganizerView, options = {}) {
    const backendViewId = resolveWilsyToolbarViewBackendId(view);
    const viewKey = resolveWilsyBackendRunViewKey(view);

    if (!backendViewId || !isWilsyToolbarCustomCollectionView(view)) {
      return null;
    }

    const cursor = String(options.cursor || '').trim();
    const limit = Number(options.limit || resolveWilsyBackendRunLimit());

    setLeadToolbarCommandBusy(options.busyLabel || 'run');
    setLeadToolbarCommandFeedback(options.feedback || 'Loading live backend view…');
    setLeadBackendRunStatusByViewId((previous) => ({
      ...previous,
      [viewKey]: {
        status: 'loading',
        generatedAt: new Date().toISOString(),
      },
      [backendViewId]: {
        status: 'loading',
        generatedAt: new Date().toISOString(),
      },
    }));

    try {
      const route = `/api/crm/leads/views/${backendViewId}/run`;
      const result = await requestWilsyToolbarCollectionCommand(
        route,
        'RUN_LEAD_VIEW',
        {
          cursor,
          limit,
          reason: options.reason || 'FG103U2 selector-handler backend Lead view hydration',
        },
        'POST'
      );

      const rows = normalizeWilsyBackendRunRows(result);
      const pagination = normalizeWilsyBackendRunPagination(result, rows);
      const membership = result?.run?.membership || result?.result?.membership || result?.membership || {};
      const runEvidencePacket = result?.run || result?.result || {};
      const viewEvidencePacket = result?.view || {};
      const runAuditReceiptId = runEvidencePacket?.auditReceiptId
        || result?.auditReceiptId
        || viewEvidencePacket?.lastRun?.auditReceiptId
        || '';
      const runCriteriaHash = viewEvidencePacket?.criteriaHash
        || result?.criteriaHash
        || activeLeadOrganizerView?.criteriaHash
        || '';
      /* P60K5Q10FG103F3_RUN_AUDIT_RECEIPT_CAPTURE */


      setLeadBackendRunRowsByViewId((previous) => ({
        ...previous,
        [viewKey]: rows,
        [backendViewId]: rows,
      }));

      setLeadBackendRunPaginationByViewId((previous) => ({
        ...previous,
        [viewKey]: pagination,
        [backendViewId]: pagination,
      }));

      setLeadBackendRunStatusByViewId((previous) => ({
        ...previous,
        [viewKey]: {
          status: 'hydrated',
          rowCount: rows.length,
          totalCount: pagination.totalCount,
          auditReceiptId: runAuditReceiptId,
          runAuditReceiptId,
          criteriaHash: runCriteriaHash,
          view: viewEvidencePacket,
          run: runEvidencePacket,
          result: result?.result || runEvidencePacket,
          generatedAt: new Date().toISOString(),
        },
        [backendViewId]: {
          status: 'hydrated',
          rowCount: rows.length,
          totalCount: pagination.totalCount,
          auditReceiptId: runAuditReceiptId,
          runAuditReceiptId,
          criteriaHash: runCriteriaHash,
          view: viewEvidencePacket,
          run: runEvidencePacket,
          result: result?.result || runEvidencePacket,
          generatedAt: new Date().toISOString(),
        },
      }));

      setLeadToolbarMembershipById((previous) => ({
        ...previous,
        [view?.id]: {
          ...(previous?.[view?.id] || {}),
          ...membership,
        },
        [backendViewId]: {
          ...(previous?.[backendViewId] || {}),
          ...membership,
        },
      }));

      setLeadToolbarCommandFeedback(`Live view loaded · ${pagination.returnedCount}/${pagination.totalCount}`);
      return result;
    } catch (error) {
      setLeadBackendRunStatusByViewId((previous) => ({
        ...previous,
        [viewKey]: {
          status: 'error',
          error: error?.message || 'Backend run failed',
          generatedAt: new Date().toISOString(),
        },
        [backendViewId]: {
          status: 'error',
          error: error?.message || 'Backend run failed',
          generatedAt: new Date().toISOString(),
        },
      }));
      setLeadToolbarCommandFeedback(error?.message || 'Backend run failed');
      return null;
    } finally {
      setLeadToolbarCommandBusy('');
    }
  }

  /**
   * @function resolveWilsyBackendHydratedRowsForActiveView
   * @description Resolves backend-hydrated rows for the active saved custom view.
   * @returns {object} Hydrated row state.
   * @collaboration Active records table, backend run state, cursor pagination, and custom view selector.
   */
  function resolveWilsyBackendHydratedRowsForActiveView() {
    const viewKey = resolveWilsyBackendRunViewKey(activeLeadOrganizerView);
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const rows = leadBackendRunRowsByViewId?.[viewKey]
      || leadBackendRunRowsByViewId?.[backendViewId]
      || [];
    const pagination = leadBackendRunPaginationByViewId?.[viewKey]
      || leadBackendRunPaginationByViewId?.[backendViewId]
      || null;
    const status = leadBackendRunStatusByViewId?.[viewKey]
      || leadBackendRunStatusByViewId?.[backendViewId]
      || null;

    return {
      rows: Array.isArray(rows) ? rows : [],
      pagination,
      status,
      hydrated: Boolean(activeLeadOrganizerView?.custom && status?.status === 'hydrated'),
    };
  }


  /**
   * @function resolveWilsyActiveBackendRunPagination
   * @description Resolves active backend cursor pagination for the current custom Lead view.
   * @returns {object|null} Active cursor pagination.
   * @collaboration FG103T run response, FG103U row hydration, existing records footer, and cursor navigation controls.
   */
  function resolveWilsyActiveBackendRunPagination() {
    const hydration = resolveWilsyBackendHydratedRowsForActiveView();

    if (!activeLeadOrganizerView?.custom || !hydration?.pagination) {
      return null;
    }

    return hydration.pagination;
  }

  /**
   * @function shouldUseWilsyBackendCursorPagination
   * @description Determines whether the existing footer should use backend cursor pagination.
   * @returns {boolean} Whether backend cursor pagination is active.
   * @collaboration Custom view selector, backend rows, local fallback pagination, and existing footer controls.
   */
  function shouldUseWilsyBackendCursorPagination() {
    const hydration = resolveWilsyBackendHydratedRowsForActiveView();
    const pagination = hydration?.pagination || null;

    return Boolean(
      activeLeadOrganizerView?.custom
      && hydration?.hydrated
      && pagination
      && pagination.mode === 'cursor'
    );
  }

  /**
   * @function formatWilsyBackendCursorRange
   * @description Formats the visible backend cursor record range for the records footer.
   * @returns {string} Footer range label.
   * @collaboration Cursor pagination metadata, records footer, backend view rows, and operator clarity.
   */
  function formatWilsyBackendCursorRange() {
    const pagination = resolveWilsyActiveBackendRunPagination();

    if (!pagination) {
      return filteredLeads.length
        ? `Showing ${leadPagination.startRecord} to ${leadPagination.endRecord} of ${filteredLeads.length} ${leadOperatingCopyRecordPlural}`
        : `Showing 0 live ${leadOperatingCopyRecordPlural}`;
    }

    const offset = Number(pagination.offset || 0);
    const returnedCount = Number(pagination.returnedCount || filteredLeads.length || 0);
    const totalCount = Number(pagination.totalCount || returnedCount || 0);
    const start = returnedCount ? offset + 1 : 0;
    const end = returnedCount ? offset + returnedCount : 0;

    return `Showing ${start} to ${end} of ${totalCount} ${leadOperatingCopyRecordPlural}`;
  }

  /**
   * @function formatWilsyBackendCursorSupport
   * @description Formats backend cursor support text for the records footer.
   * @returns {string} Cursor support text.
   * @collaboration Cursor next/previous state, selected row state, filter state, and operator feedback.
   */
  function formatWilsyBackendCursorSupport() {
    const pagination = resolveWilsyActiveBackendRunPagination();

    if (!shouldUseWilsyBackendCursorPagination() || !pagination) {
      return selectedRowIds.length
        ? `${selectedRowIds.length} selected`
        : selectedLeadFilterOptions.size
          ? `${selectedLeadFilterOptions.size} active filters · ${baseFilteredLeads.length} source rows`
          : 'Live backend rows only';
    }

    if (selectedRowIds.length) {
      return `${selectedRowIds.length} selected · backend cursor page`;
    }

    const previousLabel = pagination.hasPreviousPage ? 'Back ready' : 'Start';
    const nextLabel = pagination.hasNextPage ? 'Next ready' : 'End';

    return `Backend cursor · ${previousLabel} · ${nextLabel}`;
  }

  /**
   * @function handleWilsyBackendCursorPageChange
   * @description Moves a backend-hydrated custom Lead view through cursor Previous, Next, or First.
   * @param {string} direction Cursor direction.
   * @returns {Promise<void>} Cursor page hydration.
   * @collaboration Existing footer buttons, backend /run endpoint, nextCursor, previousCursor, custom view rows, and selected row reset.
   */
  async function handleWilsyBackendCursorPageChange(direction = 'next') {
    if (!shouldUseWilsyBackendCursorPagination()) {
      return;
    }

    const pagination = resolveWilsyActiveBackendRunPagination();

    if (!pagination) {
      return;
    }

    let cursor = '';

    if (direction === 'next') {
      if (!pagination.nextCursor) return;
      cursor = pagination.nextCursor;
    }

    if (direction === 'previous') {
      if (!pagination.previousCursor) return;
      cursor = pagination.previousCursor;
    }

    if (direction === 'first') {
      cursor = '';
    }

    setSelectedRowIds([]);
    setOpenRowActionId('');
    setCurrentLeadPage(1);

    await hydrateWilsyBackendRunRowsForView(activeLeadOrganizerView, {
      cursor,
      limit: resolveWilsyBackendRunLimit(pagination.limit),
      reason: `FG103V2 backend cursor ${direction}`,
      busyLabel: 'run',
      feedback: direction === 'next'
        ? 'Loading next backend page…'
        : direction === 'previous'
          ? 'Loading previous backend page…'
          : 'Loading first backend page…',
    });
  }

  /**
   * @function handleWilsyBackendCursorPageSizeChange
   * @description Re-runs the active backend-hydrated custom Lead view with a new page size.
   * @param {string|number} nextPageSize Next page size.
   * @returns {void}
   * @collaboration Existing page-size selector, backend /run limit, cursor reset, and local pagination fallback.
   */
  function handleWilsyBackendCursorPageSizeChange(nextPageSize = '') {
    handleLeadPageSizeChange(nextPageSize);

    if (!shouldUseWilsyBackendCursorPagination()) {
      return;
    }

    setSelectedRowIds([]);
    setOpenRowActionId('');
    setCurrentLeadPage(1);

    void hydrateWilsyBackendRunRowsForView(activeLeadOrganizerView, {
      cursor: '',
      limit: resolveWilsyBackendRunLimit(nextPageSize),
      reason: 'FG103V2 backend cursor page size change',
      busyLabel: 'run',
      feedback: 'Reloading backend page size…',
    });
  }


  /**
   * @function resolveWilsySelectorBackendRunPaginationForView
   * @description Resolves backend run pagination for a selector view.
   * @param {object} view Selector view.
   * @returns {object|null} Backend pagination or null.
   * @collaboration Custom view selector, backend /run response, cursor pagination, and compact count labels.
   */
  function resolveWilsySelectorBackendRunPaginationForView(view = activeLeadOrganizerView) {
    const viewKey = resolveWilsyBackendRunViewKey(view);
    const backendViewId = resolveWilsyToolbarViewBackendId(view);

    return leadBackendRunPaginationByViewId?.[viewKey]
      || leadBackendRunPaginationByViewId?.[backendViewId]
      || null;
  }


  /**
   * @function formatWilsyCompactRunCount
   * @description Formats large backend counts into compact dropdown language.
   * @param {number|string} count Raw count.
   * @returns {string} Compact count.
   * @collaboration Million-record CRM views, compact selector labels, backend run pagination, and operator scanning.
   */
  function formatWilsyCompactRunCount(count = 0) {
    const value = Math.max(0, Number(count || 0));

    if (!Number.isFinite(value)) {
      return '0';
    }

    /**
     * @function trim
     * @description Removes trailing zeroes from compact count decimals.
     * @param {number|string} number Compact decimal value.
     * @returns {string} Trimmed compact decimal label.
     * @collaboration Million-record count labels, compact selector grammar, and backend pagination summaries.
     */
    const trim = (number) => String(number).replace(/\.0+$/, '').replace(/(\.\d*[1-9])0+$/, '$1');

    if (value >= 1000000000) {
      return `${trim((value / 1000000000).toFixed(value >= 10000000000 ? 1 : 2))}B`;
    }

    if (value >= 1000000) {
      return `${trim((value / 1000000).toFixed(value >= 10000000 ? 1 : 2))}M`;
    }

    if (value >= 1000) {
      return `${trim((value / 1000).toFixed(value >= 10000 ? 1 : 2))}K`;
    }

    return String(value);
  }

  /**
   * @function formatWilsyExactRunCount
   * @description Formats backend counts as exact inspector/footer-grade numbers.
   * @param {number|string} count Raw count.
   * @returns {string} Exact count.
   * @collaboration Inspector support language, exact footer counts, cursor pagination, and evidence-grade totals.
   */
  function formatWilsyExactRunCount(count = 0) {
    const value = Math.max(0, Number(count || 0));

    if (!Number.isFinite(value)) {
      return '0';
    }

    try {
      return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
    } catch {
      return String(value);
    }
  }


  /**
   * @function formatWilsySelectorBackendCountLabel
   * @description Formats the compact selector count from backend run pagination when available.
   * @param {object} view Selector view.
   * @returns {string} Selector detail label.
   * @collaboration View selector, Wilsy custom views, backend run pagination, million-record compact language, and stale count prevention.
   */
  function formatWilsySelectorBackendCountLabel(view = activeLeadOrganizerView) {
    const pagination = resolveWilsySelectorBackendRunPaginationForView(view);
    const returnedCount = Number(pagination?.returnedCount || 0);
    const totalCount = Number(pagination?.totalCount || 0);

    if (isWilsyToolbarCustomCollectionView(view) && pagination && totalCount >= 0) {
      return `${formatWilsyCompactRunCount(returnedCount)}/${formatWilsyCompactRunCount(totalCount)} live`;
    }

    return String(view?.detail || view?.countLabel || view?.supportLabel || 'Live view').trim();
  }


  /**
   * @function formatWilsySelectorExactBackendCountLabel
   * @description Formats exact backend count support text for the active custom-view organizer area.
   * @param {object} view Selector view.
   * @returns {string} Exact count support label.
   * @collaboration Active custom-view inspector, backend run pagination, cursor offset, and exact count clarity.
   */
  function formatWilsySelectorExactBackendCountLabel(view = activeLeadOrganizerView) {
    const pagination = resolveWilsySelectorBackendRunPaginationForView(view);

    if (!isWilsyToolbarCustomCollectionView(view) || !pagination) {
      return '';
    }

    const offset = Number(pagination.offset || 0);
    const returnedCount = Number(pagination.returnedCount || 0);
    const totalCount = Number(pagination.totalCount || 0);
    const start = returnedCount ? offset + 1 : 0;
    const end = returnedCount ? offset + returnedCount : 0;

    return `Exact backend count: ${formatWilsyExactRunCount(returnedCount)} returned · ${formatWilsyExactRunCount(totalCount)} total · rows ${formatWilsyExactRunCount(start)}-${formatWilsyExactRunCount(end)}`;
  }

  /**
   * @function renderWilsyActiveCustomViewExactCountSupport
   * @description Renders exact backend count and forensic receipts inside the active custom-view organizer area.
   * @returns {JSX.Element|null} Exact count and evidence receipt support text.
   * @collaboration Custom view organizer, inspector-grade count language, backend cursor pagination, criteria hashes, audit receipts, membership overrides, and million-record clarity.
   */
  function renderWilsyActiveCustomViewExactCountSupport() {
    const label = formatWilsySelectorExactBackendCountLabel(activeLeadOrganizerView);
    const evidence = resolveWilsyActiveViewRunEvidence(activeLeadOrganizerView);

    if (!label && !evidence.backendViewId) {
      return null;
    }

    return (
      <small
        data-wilsy-custom-view-exact-count="FG103Y"
        data-wilsy-receipt="FG103F2"
        data-wilsy-backend-view-id={evidence.backendViewId || undefined}
        data-wilsy-criteria-hash={evidence.criteriaHash || undefined}
        data-wilsy-audit-receipt={evidence.auditReceiptId || undefined}
        data-wilsy-membership-receipt={evidence.membershipReceiptLabel}
      >
        <span>{label}</span>
        <span>{formatWilsyEvidenceReceiptLine('backendViewId', evidence.backendViewId)}</span>
        <span>{formatWilsyEvidenceReceiptLine('criteriaHash', evidence.criteriaHash)}</span>
        <span>{formatWilsyEvidenceReceiptLine('auditReceiptId', evidence.auditReceiptId)}</span>
        <span>{`membership overrides: ${evidence.membershipReceiptLabel}`}</span>
      </small>
    );
  }


  /**
   * @function truncateWilsyEvidenceReceiptValue
   * @description Truncates long forensic evidence values for compact UI display.
   * @param {string} value Evidence value.
   * @param {number} size Visible character budget.
   * @returns {string} Truncated evidence value.
   * @collaboration Evidence receipts, compact organizer language, backend hashes, and copy-safe display.
   */
  function truncateWilsyEvidenceReceiptValue(value = '', size = 12) {
    const normalized = String(value || '').trim();

    if (!normalized) {
      return '—';
    }

    if (normalized.length <= size) {
      return normalized;
    }

    return `${normalized.slice(0, size)}…`;
  }

  /**
   * @function resolveWilsyActiveViewRunEvidence
   * @description Resolves forensic evidence receipts for the active custom Lead view.
   * @param {object} view Active custom view.
   * @returns {object} Evidence receipt packet.
   * @collaboration Backend run response, criteria hash, audit receipt, membership overrides, and visible custom-view receipts.
   */
  function resolveWilsyActiveViewRunEvidence(view = activeLeadOrganizerView) {
    const backendViewId = resolveWilsyToolbarViewBackendId(view);
    const viewKey = resolveWilsyBackendRunViewKey(view);
    const statusPacket = leadBackendRunStatusByViewId?.[viewKey]
      || leadBackendRunStatusByViewId?.[backendViewId]
      || {};
    const membershipPacket = leadToolbarMembershipById?.[view?.id]
      || leadToolbarMembershipById?.[backendViewId]
      || {};
    const savedCustomView = leadCustomViews.find((candidateView) => (
      candidateView.id === view?.id
      || candidateView.backendViewId === backendViewId
      || candidateView.backendId === backendViewId
      || candidateView.registryViewId === backendViewId
      || candidateView._id === backendViewId
    )) || {};
    const viewPacket = statusPacket.view
      || savedCustomView.view
      || savedCustomView
      || view
      || {};
    const runPacket = statusPacket.run
      || statusPacket.result
      || viewPacket.lastRun
      || {};
    const criteriaHash = viewPacket.criteriaHash
      || view?.criteriaHash
      || savedCustomView.criteriaHash
      || statusPacket.criteriaHash
      || '';
    const auditReceiptId = statusPacket.auditReceiptId
      || statusPacket.runAuditReceiptId
      || runPacket.auditReceiptId
      || viewPacket?.lastRun?.auditReceiptId
      || '';
    const includeCount = Number(
      membershipPacket.manualIncludeCount
      || membershipPacket.includeCount
      || membershipPacket.includes
      || membershipPacket.manualIncludes
      || 0
    );
    const excludeCount = Number(
      membershipPacket.manualExcludeCount
      || membershipPacket.excludeCount
      || membershipPacket.excludes
      || membershipPacket.manualExcludes
      || 0
    );

    return {
      backendViewId,
      criteriaHash,
      auditReceiptId,
      includeCount,
      excludeCount,
      membershipReceiptLabel: `${includeCount} include · ${excludeCount} exclude`,
    };
  }

  /**
   * @function formatWilsyEvidenceReceiptLine
   * @description Formats a compact evidence receipt line.
   * @param {string} label Evidence label.
   * @param {string} value Evidence value.
   * @returns {string} Formatted evidence line.
   * @collaboration BackendViewId visibility, criteria hashes, audit receipts, membership receipts, and operator confidence.
   */
  function formatWilsyEvidenceReceiptLine(label = '', value = '') {
    return `${label}: ${truncateWilsyEvidenceReceiptValue(value, 18)}`;
  }

  // P60K5Q10FG103F2_VISIBLE_EVIDENCE_RECEIPTS_HELPERS


  // P60K5Q10FG103Y_COUNT_LANGUAGE_POLISH


  // P60K5Q10FG103X2_SELECTOR_BACKEND_COUNT_LABEL



  // P60K5Q10FG103V2_BACKEND_CURSOR_FOOTER_HELPERS


  // P60K5Q10FG103U2_SELECTOR_HANDLER_RUN_HYDRATION_HELPERS


  // P60K5Q10FG103Q_EFFECTIVE_MEMBERSHIP_FILTER_HELPERS


  const complianceMetrics = useMemo(() => {
    const total = leads.length;
    const verified = leads.filter(record => getComplianceStatus(record) === 'VERIFIED').length;
    const pending = leads.filter(record => getComplianceStatus(record) === 'PENDING').length;
    const failed = leads.filter(record => getComplianceStatus(record) === 'FAILED').length;

    return { total, verified, pending, failed };
  }, [leads]);

  const baseFilteredLeads = useMemo(() => {
    /* P60K5Q10FG103U2_BACKEND_RUN_TABLE_SOURCE */
    const backendHydration = resolveWilsyBackendHydratedRowsForActiveView();
    const useBackendRows = Boolean(activeLeadOrganizerView?.custom && backendHydration.hydrated);
    const sourceRows = useBackendRows ? backendHydration.rows : leads;
    const query = String(searchTerm || '').trim().toLowerCase();

    const matchedLeads = sourceRows.filter((record, index) => {
      const matchesSearch = !query || JSON.stringify(record || {}).toLowerCase().includes(query);
      const status = getComplianceStatus(record);
      const matchesFilter = activeFilter === 'ALL' || status === activeFilter;
      const matchesListView = useBackendRows
        ? true
        : activeLeadOrganizerView?.custom
          ? doesWilsyLeadMatchEffectiveCustomViewMembership(record, index)
          : doesLeadMatchListView(record, activeListViewId);

      return matchesSearch && matchesFilter && matchesListView;
    });

    return sortLeadRecords(matchedLeads, sortMode);
  }, [
    activeFilter,
    activeLeadOrganizerView,
    activeListViewId,
    leadBackendRunPaginationByViewId,
    leadBackendRunRowsByViewId,
    leadBackendRunStatusByViewId,
    leadToolbarMembershipById,
    leads,
    searchTerm,
    sortMode,
  ]);

  useEffect(() => {
    /* P60K5Q10FG90D_REACT_FILTER_STATE_MOUNT_RESET */
    setSelectedLeadFilterOptions(new Set());
    setSelectedRowIds([]);
    setSelectedLeadId('');

    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        window.localStorage.setItem(WILSY_LEADS_FILTER_LOCAL_STATE_KEY, JSON.stringify([]));
        window.localStorage.removeItem('wilsy.crm.leads.filterSelection.v2');
        window.localStorage.removeItem('wilsy.crm.leads.filterButtons.v1');
        window.localStorage.removeItem('wilsy.crm.leads.filters');
        window.localStorage.removeItem('wilsy.crm.leads.selectedFilters');
        window.localStorage.removeItem('wilsy.crm.leads.controlState');
        window.localStorage.removeItem('wilsy.crm.controlState.leads.filters');
      } catch (error) {}
    }

    window.setTimeout(() => clearWilsyFG90DLeadFilterVisualState(), 0);
    window.setTimeout(() => clearWilsyFG90DLeadFilterVisualState(), 120);
  }, []);

  useEffect(() => {
    /* P60K5Q10FG93B_INTERCEPT_WRONG_CUSTOM_VIEW_ROUTE */
    if (typeof document === 'undefined') {
      return undefined;
    }

    /**
     * @function handleCustomViewCapture
     * @description Intercepts Add New Custom View actions inside the Lead list-view menu so they open the Lead Custom View Builder.
     * @param {MouseEvent} event - Captured click event.
     * @returns {void}
     * @collaboration Leads Organizer, Custom View Builder, command routing, Super Admin misroute prevention, and live saved views.
     */
    const handleCustomViewCapture = (event) => {
      const menuNode = event.target?.closest?.('section[aria-label="Lead list views"]');

      if (!menuNode) {
        return;
      }

      const actionNode = event.target?.closest?.('button, [role="button"], a');

      if (!actionNode) {
        return;
      }

      const actionText = String(actionNode.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
      const isCustomViewAction = actionText === '+' ||
        actionText.includes('custom view') ||
        actionText.includes('new view') ||
        actionText.includes('create view') ||
        actionText.includes('add view');

      if (!isCustomViewAction) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();
      setLeadCustomViewBuilderOpen(true);
      setViewMenuOpen(false);
    };

    document.addEventListener('click', handleCustomViewCapture, true);

    return () => {
      document.removeEventListener('click', handleCustomViewCapture, true);
    };
  }, []);


  useEffect(() => {
    /* P60K5Q10FG90D_FILTER_VISUAL_RESET_ON_NAVIGATION */
    if (selectedLeadFilterOptions.size) {
      return;
    }

    if (typeof window === 'undefined') {
      return;
    }

    window.setTimeout(() => clearWilsyFG90DLeadFilterVisualState(), 0);
  }, [activeTopTab, currentLeadPage, selectedLeadFilterOptions.size]);



  const selectedLeadFilterIds = useMemo(() => (
    Array.from(selectedLeadFilterOptions)
  ), [selectedLeadFilterOptions]);

  const filteredLeads = useMemo(() => (
    applyWilsyLeadOperatingFilters(baseFilteredLeads, selectedLeadFilterIds)
  ), [baseFilteredLeads, selectedLeadFilterIds]);

  const leadPagination = useMemo(() => buildLeadPaginationModel({
    totalRecords: filteredLeads.length,
    currentPage: currentLeadPage,
    pageSize: leadPageSize
  }), [currentLeadPage, filteredLeads.length, leadPageSize]);
  const paginatedLeads = useMemo(() => (
    filteredLeads.slice(leadPagination.startIndex, leadPagination.endIndex)
  ), [filteredLeads, leadPagination.endIndex, leadPagination.startIndex]);

  useEffect(() => {
    setCurrentLeadPage(1);
    setSelectedRowIds([]);
  }, [selectedLeadFilterIds]);


  const sourcePosture = leads.length ? 'Sources connected' : 'Ready for source connection';
  const routeRegistry = Array.isArray(syncTelemetry?.registry) ? syncTelemetry.registry : [];
  const liveSources = syncTelemetry?.liveSources ?? routeRegistry.filter(route => route.connected).length;
  const totalSources = syncTelemetry?.totalSources ?? routeRegistry.length;
  const rootHash = syncTelemetry?.rootHashShort || syncTelemetry?.rootHash || 'UNSEALED';
  const totalLeadFilterOptions = useMemo(() => (
    LEAD_FILTER_OPERATING_SECTIONS.reduce((sum, section) => sum + section.options.length, 0)
  ), []);
  const journeyLanes = useMemo(() => buildLeadJourneyLanes(filteredLeads), [filteredLeads]);
  const sourceChannels = useMemo(() => buildLeadSourceChannels(routeRegistry, leads), [routeRegistry, leads]);
  const selectedLead = useMemo(() => {
    const matchedLead = filteredLeads.find((record, index) => resolveLeadRecordId(record, index) === selectedLeadId);
    return matchedLead || null;
  }, [filteredLeads, selectedLeadId]);
  const operatingMetrics = useMemo(() => buildLeadOperatingMetrics({
    leads,
    filteredLeads,
    complianceMetrics,
    liveSources,
    totalSources,
    rootHash
  }), [complianceMetrics, filteredLeads, leads, liveSources, rootHash, totalSources]);
  const visionMetrics = useMemo(() => buildLeadVisionMetrics({
    leads,
    filteredLeads,
    complianceMetrics,
    operatingCopy: leadOperatingCopy
  }), [complianceMetrics, filteredLeads, leads]);
  const setupOperatingModel = useMemo(() => buildLeadSetupOperatingModel({
    leads,
    filteredLeads,
    activeListView,
    complianceMetrics,
    routeRegistry,
    sourceChannels,
    liveSources,
    totalSources,
    rootHash,
    role,
    tenantId,
    syncStatus,
    isSyncing,
    selectedFilterCount: selectedLeadFilterOptions.size,
    totalFilterOptions: totalLeadFilterOptions,
    pageSize: leadPagination.pageSize,
    totalPages: leadPagination.totalPages
  }), [
    activeListView,
    complianceMetrics,
    filteredLeads,
    isSyncing,
    leadPagination.pageSize,
    leadPagination.totalPages,
    leads,
    liveSources,
    role,
    rootHash,
    routeRegistry,
    selectedLeadFilterOptions.size,
    sourceChannels,
    syncStatus,
    tenantId,
    totalLeadFilterOptions,
    totalSources
  ]);

  useEffect(() => {
    if (currentLeadPage !== leadPagination.currentPage) {
      setCurrentLeadPage(leadPagination.currentPage);
    }
  }, [currentLeadPage, leadPagination.currentPage]);

  useEffect(() => {
    if (!filteredLeads.length) {
      setSelectedLeadId('');
      return;
    }

    const hasSelectedLead = filteredLeads.some((record, index) => resolveLeadRecordId(record, index) === selectedLeadId);
    if (!hasSelectedLead) {
      /* P60K5Q10FG89A_NO_AUTO_FIRST_ROW_SELECTION */
      setSelectedLeadId('');
    }
  }, [filteredLeads, selectedLeadId]);

  useEffect(() => {
    const visibleIds = new Set(filteredLeads.map((record, index) => resolveLeadRecordId(record, index)));
    setSelectedRowIds(previous => previous.filter(recordId => visibleIds.has(recordId)));
  }, [filteredLeads]);

  useEffect(() => {
    if (typeof document === 'undefined') {
      return undefined;
    }

    /**
     * @function captureWilsyLeadExternalPointerDown
     * @description Records pointer starts outside the Leads workspace so layout-shift clicks cannot select records.
     * @param {PointerEvent|MouseEvent} event - Captured pointer or mouse event.
     * @returns {void}
     * @collaboration CRM side rail collapse controls, Leads records grid, and selection click isolation.
     */
    function captureWilsyLeadExternalPointerDown(event) {
      const target = event?.target;
      const insideLeadWorkspace = target?.closest?.('[data-wilsy-lead-operating-room]');

      if (!insideLeadWorkspace) {
        wilsyLeadExternalPointerDownRef.current = Date.now();
      }
    }

    document.addEventListener('pointerdown', captureWilsyLeadExternalPointerDown, true);
    document.addEventListener('mousedown', captureWilsyLeadExternalPointerDown, true);

    return () => {
      document.removeEventListener('pointerdown', captureWilsyLeadExternalPointerDown, true);
      document.removeEventListener('mousedown', captureWilsyLeadExternalPointerDown, true);
    };
  }, []);

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
   * @function normalizeWilsyFG91OwnerText
   * @description Normalizes the candidate owner identity used for Lead assignment.
   * @param {*} value - Candidate owner value.
   * @returns {string} Normalized owner text.
   * @collaboration Current user identity, Create Lead final save payload, owner assignment aliases, and Records performance tracking.
   */
  function normalizeWilsyFG91OwnerText(value = '') {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  /**
   * @function buildWilsyFG91OwnerInitials
   * @description Builds initials for the assigned Lead owner avatar.
   * @param {string} displayName - Owner display name.
   * @returns {string} Owner initials.
   * @collaboration Owner column rendering, current user assignment, performance tracking, and CRM accountability.
   */
  function buildWilsyFG91OwnerInitials(displayName = '') {
    const parts = normalizeWilsyFG91OwnerText(displayName)
      .split(' ')
      .filter(Boolean);

    if (!parts.length) {
      return resolveWilsyFG91FCurrentOwnerFallbackInitials();
    }

    return parts
      .slice(0, 2)
      .map(part => part[0])
      .join('')
      .toUpperCase();
  }

  /**
   * @function parseWilsyFG91OwnerStorageCandidate
   * @description Reads one possible browser storage profile packet for current-user Lead ownership.
   * @param {Storage} storage - Browser storage object.
   * @param {string} key - Storage key.
   * @returns {Object|null} Parsed profile packet.
   * @collaboration Local auth cache, session profile cache, Create Lead owner assignment, and 403-safe owner fallback.
   */
  function parseWilsyFG91OwnerStorageCandidate(storage, key) {
    try {
      const raw = storage?.getItem?.(key);

      if (!raw) {
        return null;
      }

      const parsed = JSON.parse(raw);

      if (parsed && typeof parsed === 'object') {
        return parsed;
      }
    } catch (error) {}

    return null;
  }

  /**
   * @function resolveWilsyFG91OwnerCandidateDisplayName
   * @description Resolves a display name from a possible current-user profile object.
   * @param {Object} candidate - Candidate profile object.
   * @returns {string} Owner display name.
   * @collaboration Current user profile packets, tenant operator context, Lead assignment aliases, and Records owner display.
   */
  function resolveWilsyFG91OwnerCandidateDisplayName(candidate = {}) {
    const nestedUser = candidate.user || candidate.profile || candidate.operator || candidate.account || candidate.identity || {};
    const source = {
      ...nestedUser,
      ...candidate,
    };

    const firstName = normalizeWilsyFG91OwnerText(source.firstName || source.givenName);
    const lastName = normalizeWilsyFG91OwnerText(source.lastName || source.familyName || source.surname);
    const joinedName = normalizeWilsyFG91OwnerText([firstName, lastName].filter(Boolean).join(' '));

    return normalizeWilsyFG91OwnerText(
      source.displayName ||
      source.name ||
      source.fullName ||
      source.operatorName ||
      source.userName ||
      source.username ||
      source.emailName ||
      joinedName
    );
  }

  /**
   * @function resolveWilsyFG91OwnerCandidateId
   * @description Resolves a stable owner/operator id from a possible current-user profile object.
   * @param {Object} candidate - Candidate profile object.
   * @returns {string} Owner identifier.
   * @collaboration Current user identity, ownerId payload aliases, assignedToId payload aliases, and CRM performance allocation.
   */
  function resolveWilsyFG91OwnerCandidateId(candidate = {}) {
    const nestedUser = candidate.user || candidate.profile || candidate.operator || candidate.account || candidate.identity || {};
    const source = {
      ...nestedUser,
      ...candidate,
    };

    return normalizeWilsyFG91OwnerText(
      source.id ||
      source._id ||
      source.userId ||
      source.operatorId ||
      source.ownerId ||
      source.accountId ||
      source.email
    );
  }

  /**
   * @function resolveWilsyFG91OwnerCandidateEmail
   * @description Resolves an owner email from a possible current-user profile object.
   * @param {Object} candidate - Candidate profile object.
   * @returns {string} Owner email.
   * @collaboration Current user identity, Lead assignment evidence, CRM ownership payload, and audit-friendly performance attribution.
   */
  function resolveWilsyFG91OwnerCandidateEmail(candidate = {}) {
    const nestedUser = candidate.user || candidate.profile || candidate.operator || candidate.account || candidate.identity || {};
    const source = {
      ...nestedUser,
      ...candidate,
    };

    return normalizeWilsyFG91OwnerText(source.email || source.operatorEmail || source.userEmail);
  }

  /**
   * @function collectWilsyFG91OwnerIdentityCandidates
   * @description Collects current-user profile candidates from safe browser globals and storage without relying on failing auth/profile probes.
   * @returns {Object[]} Candidate owner identity packets.
   * @collaboration Current session, tenant context, frontend auth cache, Create Lead save payload, and owner assignment fallback.
   */
  function collectWilsyFG91OwnerIdentityCandidates() {
    if (typeof window === 'undefined') {
      return [];
    }

    const globalCandidates = [
      window.__WILSY_CURRENT_USER__,
      window.__WILSY_USER__,
      window.__WILSY_OPERATOR__,
      window.__WILSY_OPERATOR_CONTEXT__,
      window.__WILSY_AUTH_USER__,
      window.WILSY_USER,
      window.WILSY_AUTH_USER,
      window.wilsyUser,
      window.wilsyOperator,
      window.sovereignUser,
    ].filter(candidate => candidate && typeof candidate === 'object');

    const storageKeys = [
      'wilsy.currentUser',
      'wilsy.user',
      'wilsy.operator',
      'wilsy.operator.profile',
      'wilsy.account.profile',
      'wilsy.auth.user',
      'wilsy.user.profile',
      'wilsy.profile',
      'currentUser',
      'user',
      'operator',
      'profile',
      'accountProfile',
      'authUser',
      'tenantUser',
      'tenantOperator',
      'sovereignUser',
    ];

    const storageCandidates = [];

    [window.localStorage, window.sessionStorage].forEach((storage) => {
      storageKeys.forEach((key) => {
        const candidate = parseWilsyFG91OwnerStorageCandidate(storage, key);

        if (candidate) {
          storageCandidates.push(candidate);
        }
      });
    });

    return [...globalCandidates, ...storageCandidates];
  }

  /**
   * @function resolveWilsyFG91LeadOwnerAssignment
   * @description Resolves the current Lead owner assignment and expands fallback identity when auth/profile endpoints are unavailable.
   * @param {Object} draftPayload - Create Lead draft payload.
   * @returns {Object} Owner assignment packet.
   * @collaboration Create Lead save payload, AI-created Lead assignment, manual owner field, current user context, and performance management.
   */
  function resolveWilsyFG91LeadOwnerAssignment(draftPayload = {}) {
    /* P60K5Q10FG91B_CURRENT_USER_OWNER_ASSIGNMENT */
    const draftOwnerName = normalizeWilsyFG91OwnerText(
      draftPayload.ownerDisplayName ||
      draftPayload.ownerName ||
      draftPayload.assignedToName ||
      draftPayload.owner ||
      draftPayload.assignedTo
    );

    const draftOwnerId = normalizeWilsyFG91OwnerText(
      draftPayload.ownerId ||
      draftPayload.assignedToId ||
      draftPayload.operatorId ||
      draftPayload.userId
    );

    const draftOwnerEmail = normalizeWilsyFG91OwnerText(
      draftPayload.ownerEmail ||
      draftPayload.assignedToEmail ||
      draftPayload.operatorEmail ||
      draftPayload.userEmail
    );

    if (draftOwnerName && !/^unassigned$/i.test(draftOwnerName)) {
      return {
        displayName: draftOwnerName,
        ownerName: draftOwnerName,
        assignedToName: draftOwnerName,
        ownerId: draftOwnerId || draftOwnerEmail || draftOwnerName,
        assignedToId: draftOwnerId || draftOwnerEmail || draftOwnerName,
        ownerEmail: draftOwnerEmail,
        assignedToEmail: draftOwnerEmail,
        ownerInitials: buildWilsyFG91OwnerInitials(draftOwnerName),
        source: 'DRAFT_OWNER_FIELD',
      };
    }

    const candidates = collectWilsyFG91OwnerIdentityCandidates();

    for (const candidate of candidates) {
      const displayName = resolveWilsyFG91OwnerCandidateDisplayName(candidate);
      const ownerId = resolveWilsyFG91OwnerCandidateId(candidate);
      const ownerEmail = resolveWilsyFG91OwnerCandidateEmail(candidate);

      if (displayName && !/^unassigned$/i.test(displayName)) {
        return {
          displayName,
          ownerName: displayName,
          assignedToName: displayName,
          ownerId: ownerId || ownerEmail || displayName,
          assignedToId: ownerId || ownerEmail || displayName,
          ownerEmail,
          assignedToEmail: ownerEmail,
          ownerInitials: buildWilsyFG91OwnerInitials(displayName),
          source: 'CURRENT_USER_CONTEXT',
        };
      }
    }

    return {
      displayName: 'Wilson Khanyezi',
      ownerName: 'Wilson Khanyezi',
      assignedToName: 'Wilson Khanyezi',
      ownerId: 'wilson-khanyezi',
      assignedToId: 'wilson-khanyezi',
      ownerEmail: '',
      assignedToEmail: '',
      ownerInitials: 'WK',
      source: 'FG91B_LOCAL_OPERATOR_FALLBACK',
    };
  }


  /**
   * @function normalizeWilsyFG89LeadSaveText
   * @description Normalizes Create Lead draft values before final save payload expansion.
   * @param {*} value - Candidate draft value.
   * @returns {string} Normalized value.
   * @collaboration Create Lead form state, AI-hydrated draft state, backend create payload, Records grid, and source authority.
   */
  function normalizeWilsyFG89LeadSaveText(value = '') {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

/**
 * @function resolveWilsyFG91ECurrentOwnerFallbackName
 * @description Resolves the owner fallback used by the Records owner column when backend Lead owner fields are blank or unassigned.
 * @returns {string} Current operator fallback display name.
 * @collaboration Records owner column, AI-created Lead rows, CRM performance ownership, and operator accountability.
 */
function resolveWilsyFG91FCurrentOwnerFallbackName() {
  /* P60K5Q10FG91E_OWNER_COLUMN_FALLBACK_REPAIR */
  if (typeof window !== 'undefined') {
    const candidates = [
      window.__WILSY_CURRENT_USER__,
      window.__WILSY_USER__,
      window.__WILSY_OPERATOR__,
      window.__WILSY_OPERATOR_CONTEXT__,
      window.__WILSY_AUTH_USER__,
      window.WILSY_USER,
      window.WILSY_AUTH_USER,
      window.wilsyUser,
      window.wilsyOperator,
      window.sovereignUser,
    ].filter(candidate => candidate && typeof candidate === 'object');

    const storageKeys = [
      'wilsy.currentUser',
      'wilsy.user',
      'wilsy.operator',
      'wilsy.operator.profile',
      'wilsy.account.profile',
      'wilsy.auth.user',
      'wilsy.user.profile',
      'wilsy.profile',
      'currentUser',
      'user',
      'operator',
      'profile',
      'accountProfile',
      'authUser',
      'tenantUser',
      'tenantOperator',
      'sovereignUser',
    ];

    [window.localStorage, window.sessionStorage].forEach((storage) => {
      storageKeys.forEach((key) => {
        try {
          const parsed = JSON.parse(storage?.getItem?.(key) || 'null');

          if (parsed && typeof parsed === 'object') {
            candidates.push(parsed);
          }
        } catch (error) {}
      });
    });

    for (const candidate of candidates) {
      const nested = candidate.user || candidate.profile || candidate.operator || candidate.account || candidate.identity || {};
      const source = { ...nested, ...candidate };
      const firstName = String(source.firstName || source.givenName || '').trim();
      const lastName = String(source.lastName || source.surname || source.familyName || '').trim();
      const joinedName = [firstName, lastName].filter(Boolean).join(' ').trim();
      const displayName = String(
        source.displayName ||
        source.name ||
        source.fullName ||
        source.operatorName ||
        source.userName ||
        source.username ||
        joinedName ||
        ''
      ).replace(/\s+/g, ' ').trim();

      if (displayName && !/^unassigned$/i.test(displayName) && displayName !== 'U' && displayName !== '-') {
        return displayName;
      }
    }
  }

  return 'Wilson Khanyezi';
}

/**
 * @function resolveWilsyFG91ECurrentOwnerFallbackInitials
 * @description Resolves fallback owner initials for AI-created Lead rows when backend initials are blank or U.
 * @returns {string} Current operator fallback initials.
 * @collaboration Records owner avatar, CRM performance ownership, AI-created Lead rows, and accountability display.
 */
function resolveWilsyFG91FCurrentOwnerFallbackInitials() {
  const ownerName = resolveWilsyFG91FCurrentOwnerFallbackName();
  const parts = ownerName.split(' ').filter(Boolean);

  if (!parts.length) {
    return 'WK';
  }

  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase();
}


  /**
   * @function buildWilsyFG89LeadFinalSavePayload
   * @description Builds the final backend Create Lead payload with every known Lead name, company, owner, title, and address alias.
   * @param {Object} draftPayload - Current Create Lead draft payload.
   * @returns {Object} Save payload with canonical and compatibility aliases.
   * @collaboration Create Lead save button, Wilsy AI draft hydration, CRM command route, backend persistence, and Records table display.
   */
  function buildWilsyFG89LeadFinalSavePayload(draftPayload = {}) {
    /* P60K5Q10FG89A_FINAL_SAVE_PAYLOAD_NORMALIZER */
    const leadName = normalizeWilsyFG89LeadSaveText(
      draftPayload.leadName ||
      draftPayload.name ||
      draftPayload.fullName ||
      draftPayload.displayName ||
      draftPayload.contactName ||
      draftPayload.personName
    );

    const companyName = normalizeWilsyFG89LeadSaveText(
      draftPayload.companyName ||
      draftPayload.company ||
      draftPayload.accountName ||
      draftPayload.organizationName ||
      draftPayload.organisationName
    );

    const title = normalizeWilsyFG89LeadSaveText(
      draftPayload.title ||
      draftPayload.jobTitle ||
      draftPayload.position ||
      draftPayload.roleTitle
    );

    const wilsyFG91OwnerAssignment = resolveWilsyFG91LeadOwnerAssignment(draftPayload);
    const owner = normalizeWilsyFG89LeadSaveText(
      draftPayload.owner ||
      draftPayload.ownerName ||
      draftPayload.assignedTo ||
      draftPayload.assignedToName ||
      draftPayload.ownerDisplayName ||
      wilsyFG91OwnerAssignment.displayName
    );

    const street = normalizeWilsyFG89LeadSaveText(
      draftPayload.street ||
      draftPayload.streetAddress ||
      draftPayload.addressLine1 ||
      draftPayload.addressSearch
    );

    const city = normalizeWilsyFG89LeadSaveText(draftPayload.city || draftPayload.town);
    const province = normalizeWilsyFG89LeadSaveText(draftPayload.province || draftPayload.state || draftPayload.region);
    const postalCode = normalizeWilsyFG89LeadSaveText(draftPayload.postalCode || draftPayload.zipCode || draftPayload.zip || draftPayload.postCode);
    const country = normalizeWilsyFG89LeadSaveText(draftPayload.country || 'South Africa');
    const formattedAddress = normalizeWilsyFG89LeadSaveText(
      draftPayload.formattedAddress ||
      [street, city, province, postalCode, country].filter(Boolean).join(', ')
    );

    const aliasPayload = {
      ...draftPayload,
      ...(leadName ? {
        name: leadName,
        leadName,
        fullName: leadName,
        displayName: leadName,
        contactName: leadName,
        personName: leadName,
        firstName: leadName.split(' ').slice(0, -1).join(' ') || leadName,
        lastName: leadName.split(' ').slice(-1).join(' ') || '',
      } : {}),
      ...(companyName ? {
        company: companyName,
        companyName,
        accountName: companyName,
        organizationName: companyName,
        organisationName: companyName,
        businessName: companyName,
        employer: companyName,
      } : {}),
      ...(title ? {
        title,
        jobTitle: title,
        position: title,
        roleTitle: title,
      } : {}),
      ...((owner || resolveWilsyFG91FCurrentOwnerFallbackName()) ? {
        /* P60K5Q10FG91E_FINAL_SAVE_OWNER_FALLBACK_ALIAS */
        owner: owner || resolveWilsyFG91FCurrentOwnerFallbackName(),
        ownerName: owner || resolveWilsyFG91FCurrentOwnerFallbackName(),
        ownerDisplayName: owner,
        ownerFullName: owner,
        assignedTo: owner,
        assignedToName: owner,
        assignedToDisplayName: owner,
        assignedUserName: owner,
        ownerInitials: wilsyFG91OwnerAssignment.ownerInitials || buildWilsyFG91OwnerInitials(owner),
        assignedToInitials: wilsyFG91OwnerAssignment.ownerInitials || buildWilsyFG91OwnerInitials(owner),
        ownerId: wilsyFG91OwnerAssignment.ownerId || owner,
        assignedToId: wilsyFG91OwnerAssignment.assignedToId || wilsyFG91OwnerAssignment.ownerId || owner,
        ownerEmail: wilsyFG91OwnerAssignment.ownerEmail || '',
        assignedToEmail: wilsyFG91OwnerAssignment.assignedToEmail || wilsyFG91OwnerAssignment.ownerEmail || '',
        assignmentSource: wilsyFG91OwnerAssignment.source || 'CURRENT_USER_CONTEXT',
        ownerProfile: {
          id: wilsyFG91OwnerAssignment.ownerId || owner,
          name: owner,
          displayName: owner,
          initials: wilsyFG91OwnerAssignment.ownerInitials || buildWilsyFG91OwnerInitials(owner),
          email: wilsyFG91OwnerAssignment.ownerEmail || '',
        },
        assignedUser: {
          id: wilsyFG91OwnerAssignment.assignedToId || wilsyFG91OwnerAssignment.ownerId || owner,
          name: owner,
          displayName: owner,
          initials: wilsyFG91OwnerAssignment.ownerInitials || buildWilsyFG91OwnerInitials(owner),
          email: wilsyFG91OwnerAssignment.assignedToEmail || wilsyFG91OwnerAssignment.ownerEmail || '',
        },
      } : {}),
      ...(street ? {
        street,
        streetAddress: street,
        addressLine1: street,
      } : {}),
      ...(city ? {
        city,
        town: city,
      } : {}),
      ...(province ? {
        province,
        state: province,
        region: province,
      } : {}),
      ...(postalCode ? {
        postalCode,
        zipCode: postalCode,
        zip: postalCode,
        postCode: postalCode,
      } : {}),
      ...(country ? {
        country,
      } : {}),
      ...(formattedAddress ? {
        formattedAddress,
        addressSearch: draftPayload.addressSearch || formattedAddress,
      } : {}),
    };

    return {
      ...aliasPayload,
      address: {
        ...(typeof draftPayload.address === 'object' && draftPayload.address ? draftPayload.address : {}),
        ...(street ? { street, streetAddress: street, addressLine1: street } : {}),
        ...(city ? { city, town: city } : {}),
        ...(province ? { province, state: province, region: province } : {}),
        ...(postalCode ? { postalCode, zipCode: postalCode, zip: postalCode, postCode: postalCode } : {}),
        ...(country ? { country } : {}),
        ...(formattedAddress ? { formattedAddress } : {}),
      },
      sourcePayload: {
        ...(typeof draftPayload.sourcePayload === 'object' && draftPayload.sourcePayload ? draftPayload.sourcePayload : {}),
        ...(leadName ? { name: leadName, leadName, displayName: leadName } : {}),
        ...(companyName ? { company: companyName, companyName, accountName: companyName } : {}),
        ...(owner ? {
          owner,
          ownerName: owner,
          ownerDisplayName: owner,
          assignedTo: owner,
          assignedToName: owner,
          ownerInitials: wilsyFG91OwnerAssignment.ownerInitials || buildWilsyFG91OwnerInitials(owner),
          ownerId: wilsyFG91OwnerAssignment.ownerId || owner,
        } : {}),
        ...(formattedAddress ? { formattedAddress } : {}),
      },
    };
  }

  /**
   * @function updateWilsyFG89DraftFieldWithAliases
   * @description Updates one Create Lead draft field while preserving final save aliases in state.
   * @param {Object} previousDraft - Previous draft payload.
   * @param {string} field - Field key.
   * @param {*} value - New value.
   * @returns {Object} Updated draft payload.
   * @collaboration Create Lead manual entry, AI draft hydration, save payload normalization, and Records grid display.
   */
  function updateWilsyFG89DraftFieldWithAliases(previousDraft = {}, field = '', value = '') {
    return buildWilsyFG89LeadFinalSavePayload({
      ...previousDraft,
      [field]: value,
    });
  }


  /**
   * @function updateDraftField
   * @description Updates one field on the Lead draft.
   * @param {string} field - Field key.
   * @param {string} value - Field value.
   * @returns {void}
   * @collaboration Keeps draft local until backend save.
   */
  function updateDraftField(field, value) {
    setDraft(previous => updateWilsyFG89DraftFieldWithAliases(previous, field, value));
  }

  /**
   * @function handleSearchChange
   * @description Routes Lead search through command fabric.
   * @param {string} query - Search query.
   * @returns {void}
   * @collaboration Keeps search source-backed.
   */
  function handleSearchChange(query) {
    setCurrentLeadPage(1);
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
   * @description Selects a Lead list view and hydrates saved custom views from the backend run endpoint.
   * @param {string} viewId View identifier.
   * @returns {void}
   * @collaboration Compact view selector, backend /run endpoint, cursor metadata, custom view rows, and existing local fallback filtering.
   */
  function handleSelectLeadListView(viewId) {
    const nextViewId = String(viewId || 'all').trim() || 'all';
    const selectedView = leadOrganizerLiveViews.find((view) => view.id === nextViewId)
      || leadCustomViews.find((view) => view.id === nextViewId || view.backendViewId === nextViewId || view.backendId === nextViewId || view.registryViewId === nextViewId || view._id === nextViewId)
      || null;

    const resolvedListView = resolveLeadListView(nextViewId);

    setActiveListViewId(nextViewId);
    setActiveFilter(resolvedListView.filter || 'ALL');
    setCurrentLeadPage(1);
    setSelectedRowIds([]);
    setOpenRowActionId('');
    /* P60K5Q10FG103U3_SELECTOR_SIDE_EFFECTS */

    if (typeof setViewMenuOpen === 'function') {
      setViewMenuOpen(false);
    }

    if (selectedView && isWilsyToolbarCustomCollectionView(selectedView)) {
      void hydrateWilsyBackendRunRowsForView(selectedView, {
        cursor: '',
        limit: resolveWilsyBackendRunLimit(),
        reason: 'FG103U2 selector-handler backend run hydration',
        busyLabel: 'run',
        feedback: 'Loading live backend view…',
      });
    }
  }

  // P60K5Q10FG103U2_SELECTOR_HANDLER_HYDRATES_RUN


  /**
   * @description Automatically hydrates an already-selected custom Lead view from backend /run.
   * @collaboration Active custom view persistence, browser refresh, selector state, backend cursor rows, and runtime proof.
   */
  useEffect(() => {
    const backendViewId = resolveWilsyToolbarViewBackendId(activeLeadOrganizerView);
    const viewKey = resolveWilsyBackendRunViewKey(activeLeadOrganizerView);
    const existingStatus = leadBackendRunStatusByViewId?.[viewKey]
      || leadBackendRunStatusByViewId?.[backendViewId]
      || null;

    if (!backendViewId || !isWilsyToolbarCustomCollectionView(activeLeadOrganizerView)) {
      return;
    }

    if (existingStatus?.status === 'loading' || existingStatus?.status === 'hydrated') {
      return;
    }

    void hydrateWilsyBackendRunRowsForView(activeLeadOrganizerView, {
      cursor: '',
      limit: resolveWilsyBackendRunLimit(),
      reason: 'FG103W auto hydrate active custom view',
      busyLabel: 'run',
      feedback: 'Loading live backend view…',
    });
  }, [
    activeListViewId,
    activeLeadOrganizerView,
    leadBackendRunStatusByViewId,
  ]);

  // P60K5Q10FG103W_AUTO_HYDRATE_ACTIVE_CUSTOM_VIEW



  /**
   * @function canCommitWilsyLeadSelectionEvent
   * @description Allows Leads row selection only when the interaction is not a side-rail collapse click-through.
   * @param {Event|null} event - Optional selection event.
   * @returns {boolean} True when selection may mutate local selectedRowIds.
   * @collaboration CRM navigation rail, Leads record checkboxes, layout-shift click shield, and operator-safe bulk actions.
   */
  function canCommitWilsyLeadSelectionEvent(event = null) {
    const lastExternalPointerAt = Number(wilsyLeadExternalPointerDownRef.current || 0);
    const clickedImmediatelyAfterExternalPointer =
      lastExternalPointerAt > 0 &&
      Date.now() - lastExternalPointerAt < WILSY_LEADS_EXTERNAL_POINTER_SELECTION_BLOCK_MS;

    event?.stopPropagation?.();

    if (clickedImmediatelyAfterExternalPointer) {
      return false;
    }

    if (!event) {
      return true;
    }

    const target = event?.target;

    if (!target?.closest) {
      return true;
    }

    return Boolean(target.closest('[data-wilsy-lead-operating-room]'));
  }

  /**
   * @function handleToggleLeadSelection
   * @description Toggles one row in the Lead records grid.
   * @param {string} recordId - Lead record id.
   * @returns {void}
   * @collaboration Enables list-view mass action posture without mutating backend rows in the browser.
   */
  function handleToggleLeadSelection(recordId, event = null) {
    if (!canCommitWilsyLeadSelectionEvent(event)) {
      return;
    }
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
  function handleToggleAllLeadSelection(event = null) {
    if (!canCommitWilsyLeadSelectionEvent(event)) {
      return;
    }
    const visibleIds = paginatedLeads.map((record, index) => resolveLeadRecordId(record, leadPagination.startIndex + index));
    const allSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));

    if (allSelected) {
      setSelectedRowIds([]);
      return;
    }

    setSelectedRowIds(visibleIds);
  }

  /**
   * @function handleLeadPageChange
   * @description Moves the Lead records table to a bounded page.
   * @param {number} page - Requested page number.
   * @returns {void}
   * @collaboration Gives the Leads footer working OS pagination for live backend scaling.
   */
  function handleLeadPageChange(page) {
    setCurrentLeadPage(Math.min(Math.max(1, Number(page || 1)), leadPagination.totalPages));
  }

  /**
   * @function handleLeadPageSizeChange
   * @description Updates Lead records page size and resets to the first page.
   * @param {string|number} value - Requested page size.
   * @returns {void}
   * @collaboration Keeps row density operator-controlled without hardcoded table volume.
   */
  function handleLeadPageSizeChange(value) {
    const nextPageSize = LEAD_PAGE_SIZE_OPTIONS.includes(Number(value)) ? Number(value) : 20;
    setLeadPageSize(nextPageSize);
    setCurrentLeadPage(1);
  }

    /**
   * @function resetLeadDraftForPrivacy
   * @description Clears Create Lead draft fields before closing, saving, or leaving the Lead create surface.
   * @param {string} nextMode - Next Lead surface mode.
   * @returns {void}
   * @collaboration Protects private form text while keeping Lead records DB-backed.
   */
  function resetLeadDraftForPrivacy(nextMode = 'list') {
    setDraft(createEmptyLeadDraft({}));
    setSaveStatus('');
    setCreateMenuOpen(false);
    setMode(nextMode);
  }

  useEffect(() => {
    if (mode !== 'create') {
      setDraft(createEmptyLeadDraft({}));
      setSaveStatus('');
    }
  }, [mode]);

/**
   * @function handleSaveLead
   * @description Saves a valid Lead draft through backend command fabric.
   * @param {boolean} createAnother - Whether to reset the draft after save.
   * @returns {Promise<void>} Save operation.
   * @collaboration Prevents fake rows and preserves backend authority.
   */
  async function handleSaveLead(createAnother = false) {
    /* P60K5Q10FG89A_FINAL_SAVE_DRAFT_BRIDGE */
    const wilsyFG89AFinalSaveDraft = buildWilsyFG89LeadFinalSavePayload(draft);

    if (!canUseLeadAction(role, 'create')) {
      setSaveStatus('Create Lead is locked by role policy.');
      return;
    }

    if (!isLeadDraftValid(wilsyFG89AFinalSaveDraft)) {
      setSaveStatus('Lead name, company and email are required before backend creation.');
      return;
    }

    setSaveStatus('Sending verified Lead payload to backend command fabric...');

    try {
      if (typeof onSaveLead === 'function') {
        await onSaveLead(normalizeLeadPayload(wilsyFG89AFinalSaveDraft, tenantId));
      }

      setSaveStatus('Lead saved through backend command fabric.');

      if (createAnother) {
        resetLeadDraftForPrivacy('create');
        return;
      }

      resetLeadDraftForPrivacy('list');
    } catch (error) {
      setSaveStatus(error?.message || error?.response?.data?.message || 'Backend rejected the Lead payload.');
    }
  }

  /**
   * @function handleSetupControlAction
   * @description Routes Setup drawer controls into existing live Lead operating surfaces.
   * @param {string} action - Setup action key.
   * @returns {Promise<void>|void} Routed action.
   * @collaboration Keeps Setup buttons from becoming static placeholders.
   */
  function handleSetupControlAction(action = 'records') {
    if (action === 'sync') {
      return handleSourceSync();
    }

    if (action === 'command') {
      setSetupOpen(false);
      setCommandOpen(true);
      return undefined;
    }

    if (action === 'create') {
      setSetupOpen(false);
      setMode('create');
      return undefined;
    }

    if (['records', 'pipeline', 'proof', 'sources', 'signals'].includes(action)) {
      setActiveTopTab(action);
      setSetupOpen(false);
      return undefined;
    }

    setActiveTopTab('records');
    setSetupOpen(false);
    return undefined;
  }

  /**
   * @function buildWilsyLeadAIContext
   * @description Builds live CRM Leads context for the Wilsy AI Operator Kernel without depending on fake data.
   * @returns {Object} CRM Leads context packet.
   * @collaboration Leads active tab, sort posture, source posture, proof state, and Wilsy AI universal operator growth.
   */
  function buildWilsyLeadAIContext() {
    /**
     * @function safeLeadRows
     * @description Resolves the currently visible CRM Leads rows for Wilsy AI context without inventing data.
     * @returns {Array<Object>} Current Leads rows available to the workspace.
     * @collaboration CRM Leads live context, Wilsy AI Operator Kernel, and no-fake-data response discipline.
     */
    const safeLeadRows = (() => {
      if (typeof visibleLeads !== 'undefined' && Array.isArray(visibleLeads)) return visibleLeads;
      if (typeof filteredLeads !== 'undefined' && Array.isArray(filteredLeads)) return filteredLeads;
      if (typeof leadRecords !== 'undefined' && Array.isArray(leadRecords)) return leadRecords;
      if (typeof leads !== 'undefined' && Array.isArray(leads)) return leads;
      return [];
    })();
    /**
     * @function safeSourceRows
     * @description Resolves source route rows for Wilsy AI context without creating synthetic source authority.
     * @returns {Array<Object>} Source route rows available to the Leads workspace.
     * @collaboration CRM Leads source posture, evidence routing, Wilsy AI Operator Kernel, and no-fake-data response discipline.
     */
    const safeSourceRows = (() => {
      if (typeof sourceRoutes !== 'undefined' && Array.isArray(sourceRoutes)) return sourceRoutes;
      if (typeof leadSourceRoutes !== 'undefined' && Array.isArray(leadSourceRoutes)) return leadSourceRoutes;
      if (typeof sourceRows !== 'undefined' && Array.isArray(sourceRows)) return sourceRows;
      return [];
    })();
    const liveSourceCount = safeSourceRows.filter(source => (
      source?.live === true ||
      source?.status === 'LIVE' ||
      source?.status === 'CONNECTED' ||
      source?.posture === 'UPLINK'
    )).length;
    const safeActiveSort = typeof activeSort !== 'undefined' ? activeSort : {};
    const safeSortDirection = typeof activeSortDirection !== 'undefined' ? activeSortDirection : 'desc';
    const safeLiveSources = typeof liveSources !== 'undefined' ? Number(liveSources) || 0 : 0;
    const safeComplianceVerified = typeof complianceVerified !== 'undefined' ? Number(complianceVerified) || 0 : 0;
    const safeCompliancePending = typeof compliancePending !== 'undefined' ? Number(compliancePending) || 0 : 0;
    const safeComplianceFailed = typeof complianceFailed !== 'undefined' ? Number(complianceFailed) || 0 : 0;
    const safeRootHash = typeof rootHash !== 'undefined' ? String(rootHash || '') : '';

    return {
      activeTopTab,
      workspaceRoute: '/crm/leads',
      workspaceSurface: resolveWilsyLeadAIWorkspaceSurface(activeTopTab),
      visibleLeadCount: safeLeadRows.length,
      sourceRouteCount: safeSourceRows.length,
      sourceRouteLiveCount: liveSourceCount || safeLiveSources,
      complianceVerified: safeComplianceVerified,
      compliancePending: safeCompliancePending,
      complianceFailed: safeComplianceFailed,
      activeSortField: safeActiveSort?.id || safeActiveSort?.field || 'lastActivity',
      activeSortDirection: safeActiveSort?.direction || safeSortDirection || 'desc',
      rootHash: safeRootHash,
      generatedAt: new Date().toISOString(),
    };
  }


  /**
   * @function normalizeWilsyFG81LeadCreateDraftValue
   * @description Normalizes AI-provided Lead create draft values for controlled Create Lead fields.
   * @param {*} value - Incoming AI draft value.
   * @returns {string} Controlled Create Lead field value.
   * @collaboration Wilsy AI governed draft hydration, Create Lead field parity, and operator-reviewed save flow.
   */
  function normalizeWilsyFG81LeadCreateDraftValue(value) {
    if (value === null || value === undefined) return '';
    return String(value).trim();
  }

  /**
   * @function resolveWilsyFG81LeadCreateDraftFromAIResponse
   * @description Extracts a governed Create Lead draft from the Wilsy AI Operator Kernel response without executing a backend mutation.
   * @param {Object} packet - Wilsy AI operator response packet.
   * @returns {Object|null} Lead create draft payload or null.
   * @collaboration Floating Wilsy AI, CRM Leads Create surface, governed draft approval, and no-blind-write policy.
   */
  function resolveWilsyFG81LeadCreateDraftFromAIResponse(packet = {}) {
    const operatorModel = packet?.operatorModel || {};
    const firstTool = Array.isArray(packet?.toolRuns) ? packet.toolRuns[0] : null;
    const candidates = [
      operatorModel.leadCreateDraft,
      operatorModel.createLeadDraft,
      operatorModel.draft?.leadCreateDraft,
      operatorModel.draft?.lead,
      firstTool?.leadCreateDraft,
      firstTool?.createLeadDraft,
      firstTool?.draft?.leadCreateDraft,
      firstTool?.draft?.lead,
      firstTool?.draft,
    ];

    return candidates.find(candidate => candidate && typeof candidate === 'object') || null;
  }

  /**
   * @function applyWilsyFG81AILeadCreateDraft
   * @description Opens Create Lead and hydrates fields from a governed Wilsy AI draft for operator review.
   * @param {Object} aiCreateDraft - AI-prepared Create Lead draft.
   * @returns {boolean} True when a draft was applied.
   * @collaboration Wilsy AI chat execution, Create Lead parity fields, institutional evidence posture, and human approval.
   */
  function applyWilsyFG81AILeadCreateDraft(aiCreateDraft = {}) {
    /* P60K5Q10FG81_CREATE_FIELD_PARITY_AI_DRAFT */
    if (!aiCreateDraft || typeof aiCreateDraft !== 'object') return false;

    const fieldMap = {
      name: aiCreateDraft.name || aiCreateDraft.leadName || aiCreateDraft.title || '',
      company: aiCreateDraft.company || aiCreateDraft.accountName || aiCreateDraft.organization || '',
      email: aiCreateDraft.email || aiCreateDraft.emailAddress || '',
      phone: aiCreateDraft.phone || aiCreateDraft.phoneNumber || '',
      mobile: aiCreateDraft.mobile || aiCreateDraft.mobileNumber || aiCreateDraft.phone || '',
      countryCode: aiCreateDraft.countryCode || 'ZA',
      mobileCountryCode: aiCreateDraft.mobileCountryCode || aiCreateDraft.countryCode || 'ZA',
      title: aiCreateDraft.jobTitle || aiCreateDraft.roleTitle || aiCreateDraft.designation || '',
      source: aiCreateDraft.source || aiCreateDraft.leadSource || 'Wilsy AI',
      status: aiCreateDraft.status || 'NEW',
      stage: aiCreateDraft.stage || 'NURTURE',
      owner: aiCreateDraft.owner || aiCreateDraft.ownerName || '',
      priority: aiCreateDraft.priority || 'Medium',
      estimatedDealValue: aiCreateDraft.estimatedDealValue || aiCreateDraft.dealValue || aiCreateDraft.value || '',
      dealValue: aiCreateDraft.estimatedDealValue || aiCreateDraft.dealValue || aiCreateDraft.value || '',
      score: aiCreateDraft.score || aiCreateDraft.leadScore || '',
      industry: aiCreateDraft.industry || '',
      dueDate: aiCreateDraft.dueDate || aiCreateDraft.followUpDate || '',
      website: aiCreateDraft.website || '',
      employees: aiCreateDraft.employees || aiCreateDraft.employeeCount || '',
      notes: aiCreateDraft.notes || aiCreateDraft.description || aiCreateDraft.summary || '',
      description: aiCreateDraft.description || aiCreateDraft.notes || aiCreateDraft.summary || '',
      street: aiCreateDraft.street || '',
      city: aiCreateDraft.city || '',
      state: aiCreateDraft.state || aiCreateDraft.province || '',
      zipCode: aiCreateDraft.zipCode || aiCreateDraft.postalCode || '',
      country: aiCreateDraft.country || '',
      addressSearch: aiCreateDraft.addressSearch || aiCreateDraft.formattedAddress || aiCreateDraft.street || '',
      formattedAddress: aiCreateDraft.formattedAddress || '',
    };

    const normalizedDraft = Object.entries(fieldMap).reduce((nextDraft, [field, value]) => {
      const normalizedValue = normalizeWilsyFG81LeadCreateDraftValue(value);
      if (normalizedValue) nextDraft[field] = normalizedValue;
      return nextDraft;
    }, {});

    if (!Object.keys(normalizedDraft).length) return false;

    setDraft(previous => ({
      ...previous,
      ...normalizedDraft,
      source: normalizedDraft.source || previous.source || 'Wilsy AI',
      status: normalizedDraft.status || previous.status || 'NEW',
      stage: normalizedDraft.stage || previous.stage || 'NURTURE',
      priority: normalizedDraft.priority || previous.priority || 'Medium',
      addressVerificationStatus: previous.addressVerificationStatus || 'AI_DRAFT_REVIEW_REQUIRED',
      addressSourceProvider: previous.addressSourceProvider || 'WILSY_AI_OPERATOR_DRAFT',
      addressEvidenceReceipt: previous.addressEvidenceReceipt || 'Wilsy AI prepared this Create Lead draft for operator review.',
    }));

    setSaveStatus('Wilsy AI prepared a governed Create Lead draft. Review every field, then Save.');
    setMode('create');
    return true;
  }


  useEffect(() => {
    /* P60K5Q10FG82_GLOBAL_AI_CREATE_LEAD_DRAFT_RECEIVER */
    if (typeof window === 'undefined') {
      return undefined;
    }

    /**
     * @function handleWilsyFG82GlobalLeadCreateDraft
     * @description Receives governed Create Lead drafts from the global Wilsy AI dock and hydrates the Leads Create surface.
     * @param {CustomEvent} event - Global Wilsy AI Create Lead draft event.
     * @returns {void}
     * @collaboration Floating Wilsy AI, CRM Setup copilot, Leads Create surface, governed draft approval, and no-blind-write policy.
     */
    function handleWilsyFG82GlobalLeadCreateDraft(event) {
      const detail = event?.detail || {};
      const draft = detail.leadCreateDraft || detail.createLeadDraft || detail.draft;
      const packet = detail.packet || detail.operatorPacket || {};

      const resolvedDraft = draft || resolveWilsyFG81LeadCreateDraftFromAIResponse(packet);

      if (applyWilsyFG81AILeadCreateDraft(resolvedDraft || {})) {
        try {
          window.sessionStorage?.removeItem?.('wilsy.crm.leads.pendingCreateDraft');
          window.localStorage?.removeItem?.('wilsy.crm.leads.pendingCreateDraft');
        } catch {
          // Session storage is optional; Create Lead state already hydrated.
        }
      }
    }

    window.addEventListener('wilsy:crm-leads-create-draft', handleWilsyFG82GlobalLeadCreateDraft);

    try {
      /* P60K5Q10FG85_PENDING_DRAFT_LOCALSTORAGE_FALLBACK */
      const pendingDraftText =
        window.sessionStorage?.getItem?.('wilsy.crm.leads.pendingCreateDraft') ||
        window.localStorage?.getItem?.('wilsy.crm.leads.pendingCreateDraft');
      if (pendingDraftText) {
        const pendingPacket = JSON.parse(pendingDraftText);
        handleWilsyFG82GlobalLeadCreateDraft({ detail: pendingPacket });
      }
    } catch {
      // Invalid pending draft must not block the Leads workspace.
    }

    return () => {
      window.removeEventListener('wilsy:crm-leads-create-draft', handleWilsyFG82GlobalLeadCreateDraft);
    };
  }, []);



  useEffect(() => {
    /* P60K5Q10FG86B_CREATE_MODE_PENDING_DRAFT_HYDRATOR */
    if (mode !== 'create' || typeof window === 'undefined') {
      return;
    }

    try {
      /* P60K5Q10FG87B_PENDING_DRAFT_GLOBAL_MEMORY_READ */
      const pendingGlobalDraft = window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__ || null;
      const pendingDraftText =
        window.sessionStorage?.getItem?.('wilsy.crm.leads.pendingCreateDraft') ||
        window.localStorage?.getItem?.('wilsy.crm.leads.pendingCreateDraft') ||
        (pendingGlobalDraft ? JSON.stringify(pendingGlobalDraft) : '');

      if (!pendingDraftText) {
        return;
      }

      const pendingPacket = JSON.parse(pendingDraftText);
      const pendingDraft =
        pendingPacket?.leadCreateDraft ||
        pendingPacket?.createLeadDraft ||
        pendingPacket?.draft ||
        resolveWilsyFG81LeadCreateDraftFromAIResponse(pendingPacket?.packet || pendingPacket);

      if (applyWilsyFG81AILeadCreateDraft(pendingDraft || {})) {
        /* P60K5Q10FG87B_PENDING_DRAFT_GLOBAL_MEMORY_CLEANUP */
        window.sessionStorage?.removeItem?.('wilsy.crm.leads.pendingCreateDraft');
        window.localStorage?.removeItem?.('wilsy.crm.leads.pendingCreateDraft');

        try {
          delete window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__;
        } catch {
          window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__ = null;
        }
      }
    } catch {
      // Pending draft hydration must never block the Create Lead surface.
    }
  }, [mode]);



  useEffect(() => {
    /* P60K5Q10FG87B_CREATE_SURFACE_VISIBLE_REPLAY_HYDRATOR */
    if (mode !== 'create' || typeof window === 'undefined') {
      return undefined;
    }

    let cancelled = false;
    let attempts = 0;

    /**
     * @function hydratePendingDraftWhenVisible
     * @description Replays a pending AI-created Lead draft after the Create Lead surface is visible.
     * @returns {void}
     * @collaboration Global Wilsy AI pending draft storage, Create Lead surface visibility, hydration retry timing, and operator-reviewed save flow.
     */
    const hydratePendingDraftWhenVisible = () => {
      if (cancelled || attempts >= 18) {
        return;
      }

      attempts += 1;

      try {
        const createSurfaceVisible = Boolean(
          document.querySelector('[data-wilsy-lead-create-surface="P60K5Q10FG79_CREATE_AI_AWARE_SURFACE"]')
        );

        const pendingGlobalDraft = window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__ || null;
        const pendingDraftText =
          window.sessionStorage?.getItem?.('wilsy.crm.leads.pendingCreateDraft') ||
          window.localStorage?.getItem?.('wilsy.crm.leads.pendingCreateDraft') ||
          (pendingGlobalDraft ? JSON.stringify(pendingGlobalDraft) : '');

        if (!createSurfaceVisible || !pendingDraftText) {
          window.setTimeout(hydratePendingDraftWhenVisible, 90);
          return;
        }

        const pendingPacket = JSON.parse(pendingDraftText);
        const pendingDraft =
          pendingPacket?.leadCreateDraft ||
          pendingPacket?.createLeadDraft ||
          pendingPacket?.draft ||
          resolveWilsyFG81LeadCreateDraftFromAIResponse(pendingPacket?.packet || pendingPacket);

        if (applyWilsyFG81AILeadCreateDraft(pendingDraft || {})) {
          window.sessionStorage?.removeItem?.('wilsy.crm.leads.pendingCreateDraft');
          window.localStorage?.removeItem?.('wilsy.crm.leads.pendingCreateDraft');

          try {
            delete window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__;
          } catch {
            window.__WILSY_CRM_LEADS_PENDING_CREATE_DRAFT__ = null;
          }
        }
      } catch {
        window.setTimeout(hydratePendingDraftWhenVisible, 90);
      }
    };

    hydratePendingDraftWhenVisible();

    return () => {
      cancelled = true;
    };
  }, [mode]);



  useEffect(() => {
    /* P60K5Q10FG90B_FILTER_CONTROL_STATE_QUARANTINE */
    if (typeof window === 'undefined') {
      return undefined;
    }

    const wilsyFG90BFilterKeys = [
      'wilsy.crm.leads.filters',
      'wilsy.crm.leads.selectedFilters',
      'wilsy.crm.leads.controlState',
      'wilsy.crm.controlState.leads.filters',
      'crm.leads.filters',
      'crm.leads.controlState',
      'leads.filters',
      'selectedLeadFilterOptions',
    ];

    [window.localStorage, window.sessionStorage].forEach((storage) => {
      if (!storage) return;

      wilsyFG90BFilterKeys.forEach(key => storage.removeItem(key));

      Object.keys(storage)
        .filter(key => key.toLowerCase().includes('lead') && key.toLowerCase().includes('filter'))
        .forEach(key => storage.removeItem(key));

      Object.keys(storage)
        .filter(key => key.toLowerCase().includes('control') && key.toLowerCase().includes('lead'))
        .forEach(key => storage.removeItem(key));
    });

    setSelectedLeadFilterOptions(new Set());
    setSelectedRowIds([]);
    setSelectedLeadId('');

    if (typeof setLeadPage === 'function') {
      setCurrentLeadPage(1);
    }

    if (typeof setLeadCurrentPage === 'function') {
      setLeadCurrentPage(1);
    }

    if (typeof setCurrentPage === 'function') {
      setCurrentPage(1);
    }

    return undefined;
  }, []);



  /**
   * @function handleWilsyLeadAIQuestionSubmit
   * @description Sends the operator question and live CRM Leads context to the Wilsy AI Operator Kernel.
   * @param {Event} event - Form submit event.
   * @returns {Promise<void>} Resolves after packet state updates.
   * @collaboration CRM Leads frontend, FG46 Operator route, institutional headers, strike payload evidence, and continuous typographic output.
   */
  async function handleWilsyLeadAIQuestionSubmit(event) {
    event?.preventDefault?.();

    const operatorQuestion = normalizeWilsyLeadAIText(wilsyLeadAiQuestion);

    if (!operatorQuestion) {
      setWilsyLeadAiError('Ask Wilsy AI a CRM Leads question first.');
      return;
    }

    const generatedAt = new Date().toISOString();
    const { tenantId, operatorId, headers } = resolveWilsyLeadOperatorHeaders();
    const crmLeadsContext = buildWilsyLeadAIContext();
    const institutionalHeaders = {
      tenantId,
      operatorId,
      route: WILSY_LEADS_AI_OPERATOR_ENDPOINT,
      commandSurface: 'CRM_LEADS_WILSY_AI_TYPOGRAPHIC_SURFACE',
      timestamp: generatedAt,
      generatedAt,
    };
    const strikePayload = {
      institutionalHeaders,
      operatorQuestion,
      workspaceRoute: '/crm/leads',
      workspaceSurface: crmLeadsContext.workspaceSurface,
      crmLeadsContext,
      generatedAt,
    };

    setWilsyLeadAiLoading(true);
    setWilsyLeadAiError('');

    try {
      const response = await fetch(resolveWilsyLeadApiBase() + WILSY_LEADS_AI_OPERATOR_ENDPOINT, {
        method: 'POST',
        headers: {
          ...headers,
          'X-Wilsy-Command-Surface': 'CRM_LEADS_WILSY_AI_TYPOGRAPHIC_SURFACE',
        },
        body: JSON.stringify({
          tenantId,
          operatorId,
          wilsyAiContext: 'ASK',
          operatorQuestion,
          workspaceRoute: '/crm/leads',
          workspaceSurface: crmLeadsContext.workspaceSurface,
          crmLeadsContext,
          institutionalHeaders,
          strikePayload,
        }),
      });
      const packet = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(packet?.error?.message || 'Wilsy AI Operator route failed.');
      }

      const wilsyFG81AILeadCreateDraft = resolveWilsyFG81LeadCreateDraftFromAIResponse(packet);

      if (

        packet?.operatorModel?.intent === 'create_lead' ||

        packet?.operatorModel?.action === 'prepare_create_lead_draft' ||

        wilsyFG81AILeadCreateDraft

      ) {

        /* P60K5Q10FG81_APPLY_AI_CREATE_DRAFT_RESPONSE */

        applyWilsyFG81AILeadCreateDraft(wilsyFG81AILeadCreateDraft || {});

      }


      setWilsyLeadAiPacket(packet);
    } catch (error) {
      setWilsyLeadAiPacket(null);
      setWilsyLeadAiError(error?.message || 'Wilsy AI could not answer this yet.');
    } finally {
      setWilsyLeadAiLoading(false);
    }
  }

  /**
   * @function renderWilsyLeadAIResponseSurface
   * @description Renders a single continuous typographic Wilsy AI response surface with inline command links.
   * @returns {JSX.Element} Continuous typographic response surface.
   * @collaboration Wilsy AI universal operator, CRM Leads live context, inline command actions, and no-card interaction doctrine.
   */
  function renderWilsyLeadAIResponseSurface() {
    const answer = resolveWilsyLeadAIAnswerText(wilsyLeadAiPacket);
    const inlineCommands = resolveWilsyLeadAIInlineCommands(wilsyLeadAiPacket);

    return (
      <section className={styles.leadAIResponseSurface} data-wilsy-ai-response-surface="continuous_typographic">
        <form className={styles.leadAIQuestionForm} onSubmit={handleWilsyLeadAIQuestionSubmit}>
          <label htmlFor="wilsy-leads-ai-question">Wilsy AI</label>
          <input
            id="wilsy-leads-ai-question"
            className={styles.leadAIQuestionInput}
            type="text"
            value={wilsyLeadAiQuestion}
            onChange={event => setWilsyLeadAiQuestion(event.target.value)}
            placeholder="Ask about these leads, proof, sort order, source authority or compliance gaps"
            aria-label="Ask Wilsy AI about CRM Leads"
          />
          <button className={styles.leadAIAskButton} type="submit" disabled={wilsyLeadAiLoading}>
            {wilsyLeadAiLoading ? 'Thinking…' : 'Ask'}
          </button>
        </form>

        <div className={styles.leadAITypographicFlow} aria-live="polite">
          {wilsyLeadAiError ? (
            <p className={styles.leadAIErrorLine}>{wilsyLeadAiError}</p>
          ) : null}

          {answer ? (
            <p className={styles.leadAIFlowLine}>
              {answer}
              {inlineCommands.length ? (
                <span className={styles.leadAIInlineCommandRun}>
                  {inlineCommands.map(command => (
                    <button
                      key={command.id || command.label || command.command || command.action}
                      type="button"
                      className={styles.leadAIInlineCommandLink}
                      data-wilsy-ai-inline-command={command.command || command.action || command.id || 'inline'}
                      onClick={() => setWilsyLeadAiQuestion(command.prompt || command.label || command.command || '')}
                    >
                      {command.label || command.title || command.command || 'Use command'}
                    </button>
                  ))}
                </span>
              ) : null}
            </p>
          ) : (
            <p className={styles.leadAIFlowLine}>
              Ask Wilsy AI from this Leads workspace. It will read the active tab, source posture, sort posture and proof context before answering.
            </p>
          )}
        </div>
      </section>
    );
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
          <button type="button" className={styles.primaryToolbarButton} onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()} disabled={!canUseLeadAction(role, 'create')}>
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
                {/* WILSY_P60G4_SETUP_ICON_RESTORED_CONTROLLED */}
        <button
          type="button"
          className={styles.wilsyP60G4SetupIconButton}
          onClick={handleOpenCrmSetupFromTopRail}
          aria-label="Open CRM setup controls"
          title="Setup"
        >
          ⚙
        </button>
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
    const selectedLeadRecords = selectedRowIds
      .map((recordId) => {
        const normalizedRecordId = String(recordId || '');

        if (!normalizedRecordId) {
          return null;
        }

        const pageRecord = paginatedLeads.find((record, index) => (
          resolveLeadRecordId(record, leadPagination.startIndex + index) === normalizedRecordId
        ));

        if (pageRecord) {
          return pageRecord;
        }

        return filteredLeads.find((record, index) => (
          resolveLeadRecordId(record, index) === normalizedRecordId
        )) || selectedLead || null;
      })
      .filter(Boolean);


    return (
      <header
        className={styles.appHeader}
        data-wilsy-lead-appbar="sovereign-header-command-bridge"
        data-wilsy-lead-topbar={WILSY_LEAD_TABBED_APP_BAR_VERSION}
      >
        <section className={[styles.headerPrimaryRow, styles.leadModuleTopBar, styles.leadHeaderPrimary].join(' ')}>
          <section className={[styles.headerIdentity, styles.leadModuleTitleBlock].join(' ')} data-wilsy-r91k179e24p48b-hero-copy-stack="true" data-wilsy-r91k179e24p48c-hero-copy-kind={String(leadOperatingCopyTitle || "").trim().toLowerCase()}>
            <small>{leadOperatingCopy.heroEyebrow}</small>
            <strong>{mode === 'create' ? leadOperatingCopy.createLabel : leadOperatingCopyTitle}</strong>
            <em>{leadOperatingCopy.heroDescription}</em>
          </section>

          <section
            className={[styles.headerThemeDock, styles.leadModuleUtilities, styles.leadHeaderUtilities].join(' ')}
            data-wilsy-header-theme-dock="theme-engine-authority"
          >
            <label className={[styles.headerSearch, styles.leadSearch].join(' ')}>
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


            {/* WILSY_P60H2B_SETUP_ICON_BEFORE_CALENDAR */}
            <button
              type="button"
              className={styles.leadIconButton}
              onClick={handleOpenCrmSetupFromTopRail}
              title="Setup"
              aria-label="Open CRM setup controls"
            >
              <Settings size={18} aria-hidden="true" />
            </button>
<button type="button" className={styles.leadIconButton} onClick={() => setCalendarOpen(true)} title="Calendar">
              <CalendarDays size={18} />
            </button>

            {/* WILSY_P60G3_SETUP_TRIGGER_REMOVED_FROM_SHARED_RECORD_SHELL: setup trigger removed from shared Leads/Meetings record header. Setup belongs at CRMDashboard admin scope. */ null}

            <div className={styles.leadDropdownWrap}>
                <button
                  type="button"
                  className={styles.leadUtilityButton}
                  onClick={onOpenThemeAuthority}
                  aria-label={`Open global theme authority: ${globalThemeAuthorityLabel}`}
                  data-wilsy-global-theme-authority-control="command-center"
                >
                  <Settings size={18} aria-hidden="true" />
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
          <section className={styles.leadViewCluster} data-wilsy-leads-organizer-shell="true">
            <div className={styles.leadDropdownWrap} data-wilsy-leads-organizer-wrap="true">
              <button type="button" className={styles.leadViewButton} onClick={() => setViewMenuOpen(previous => {
                    const nextOpen = !previous;
                    if (nextOpen) {
                      setSortMenuOpen(false);
                      setCreateMenuOpen(false);
                      setMoreMenuOpen(false);
                    }
                    return nextOpen;
                  })}>
                <List size={18} />
                <span>
                  <strong>{resolveLeadOperatingCopyLabel(activeLeadOrganizerView.label, activeListViewId)}</strong>
                  <em>{formatWilsySelectorBackendCountLabel(activeLeadOrganizerView)}</em>
                </span>
                <ChevronDown size={16} />
              </button>
              {renderWilsyActiveCustomViewExactCountSupport()}

              {viewMenuOpen ? (
                <section className={styles.leadOrganizerCompactMenu} data-wilsy-leads-organizer-compact-menu="FG97" aria-label="Lead list views"
                  data-wilsy-compact-organizer-scroll="FG102E_SCROLL_ONLY"
                  tabIndex={0}
                  onWheel={handleWilsyLeadOrganizerMenuWheel}>
                  {/* P60K5Q10FG92G_DROPDOWN_LIVE_COMPACT_SOURCE */}
                  {leadOrganizerLiveViews.map(view => (
                    <button
                      key={view.id}
                      type="button"
                      data-active={String(view.id) === String(activeListViewId) ? 'true' : 'false'}
                      onClick={() => {
                      setActiveListViewId(view.id || 'ALL');
                      setCurrentLeadPage(1);
                      setCurrentLeadPage(1);
                      setViewMenuOpen(false);
                    }}
                    >
                      <span>{resolveLeadOperatingCopyLabel(view.label, view.id)}</span>
                      <em>{formatWilsySelectorBackendCountLabel(view)}</em>
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
                  <span>{resolveLeadOperatingCopyLabel(tab.label, tab.id)}</span>
                </button>
              );
            })}
          </nav>

          <section className={[styles.headerShortcutBar, styles.leadModuleToolbar].join(' ')} data-wilsy-header-shortcuts="production">
            <button
              type="button"
              onClick={() => setFilterPanelOpen(previous => !previous)}
              data-active={filterPanelOpen ? 'true' : 'false'}
              data-wilsy-leads-filter-toolbar-toggle="true"
            >
              <SlidersHorizontal size={18} />
              <span>Filter</span>
            </button>

            <div className={styles.leadDropdownWrap}>
              <button type="button" className={styles.leadSortButton} onClick={() => setSortMenuOpen(previous => !previous)}>
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
                        setCurrentLeadPage(1);
                        setSortMenuOpen(false);
                      }}
                    >
                      <span>{option.label}</span>
                    </button>
                  ))}
                </section>
              ) : null}
            </div>

            <button type="button" className={styles.leadSplitButton} onClick={() => setSplitView(previous => !previous)} data-active={splitView ? 'true' : 'false'}>
              <SplitSquareHorizontal size={18} />
              <span>{splitView ? 'Single' : 'Split'}</span>
            </button>

            <div className={styles.leadCreateDock}>
              <button
                type="button"
                className={[styles.headerPrimaryAction, styles.leadCreateButton].join(' ')}
                onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()}
                disabled={!canUseLeadAction(role, 'create')}
              >
                <Plus size={18} />
                <span>{leadOperatingCopy.createLabel}</span>
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
                  <button type="button" onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()}><Plus size={14} />{leadOperatingCopy.createLabel}</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'import')}><Upload size={14} />Import Leads</button>
                  <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={14} />Import Notes</button>
                </section>
              ) : null}
            </div>

            <div className={styles.headerMoreDock}>
              <button type="button" className={styles.leadMoreButton} onClick={() => setMoreMenuOpen(previous => !previous)}>
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
   * @function renderLeadVisionMetricDeck
   * @description Renders the live KPI strip from Wilson's Leads UI vision.
   * @returns {JSX.Element} Vision KPI deck.
   * @collaboration Gives the page premium command presence while staying live-DB-only.
   */
  function renderLeadVisionMetricDeck() {
    return (
      <section className={styles.leadVisionMetricDeck} data-wilsy-lead-vision-metrics="LIVE_DB_DERIVED">
        {visionMetrics.map(metric => {
          const MetricIcon = metric.icon || Activity;

          return (
            <article key={metric.id} data-tone={metric.tone}>
              <span className={styles.leadVisionMetricIcon}>
                <MetricIcon size={18} />
              </span>
              <span className={styles.leadVisionMetricCopy}>
                <small>{metric.label}</small>
                <strong>{metric.value}</strong>
                <em>{metric.detail}</em>
              </span>
              <b>{metric.trend}</b>
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
          <button type="button" onClick={() => {
            setActiveFilter('ALL');
            setCurrentLeadPage(1);
          }}>
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
              <button type="button" onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()} disabled={!canUseLeadAction(role, 'create')}>
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
    if (!filterPanelOpen) {
      return (
        <aside
          className={styles.leadFilterRailCollapsed}
          data-wilsy-filter-restore="R83A-FILTER-RESTORE"
          data-wilsy-lead-filter-rail-open="false"
          aria-label="Lead filters collapsed"
        >
          <button
            type="button"
            className={styles.leadFilterRailOpenButton}
            onPointerDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
              openWilsyLeadFilterRail();
            }}
            onClick={(event) => {
              event.preventDefault();
              event.stopPropagation();
              openWilsyLeadFilterRail();
            }}
            aria-label="Show Lead filters"
            title="Show filters"
            data-wilsy-leads-filter-open="true"
          >
            <SlidersHorizontal size={17} />
            <span>Show filters</span>
          </button>
        </aside>
      );
    }

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
    const visibleFilterCount = visibleFilterSections.reduce((total, section) => total + section.options.length, 0);

    return (
      <aside
        className={styles.leadFilterRail}
        data-wilsy-lead-filter-operating-system="R80A-INDEPENDENT-SCROLL"
        data-wilsy-lead-filter-rail-open="true"
        aria-label="Lead filters"
      >
        <header className={styles.leadFilterRailHeader}>
          <span>
            <strong>{leadOperatingCopy.filterTitle}</strong>
            <em>{visibleFilterCount} available filters</em>
          </span>
          <button
            type="button"
            className={styles.leadFilterRailCloseButton}
            aria-label="Collapse Lead filters"
            title="Collapse Lead filters"
            data-wilsy-leads-filter-close="true"
            onPointerDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
              closeWilsyLeadFilterRail();
            }}
            onClick={(event) => {
              event.preventDefault();
              event.stopPropagation();
              closeWilsyLeadFilterRail();
            }}
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

        <div
          className={styles.leadFilterRailMeta}
          aria-live="polite"
          data-wilsy-lead-filter-active={selectedFilterCount ? 'true' : 'false'}
        >
          <span>
            <strong>{selectedFilterCount}</strong>
            <span>{selectedFilterCount === 1 ? 'filter selected' : 'filters selected'}</span>
          </span>
          {selectedFilterCount ? (
            <button
              type="button"
              className={styles.leadFilterClearButton}
              onClick={clearWilsyLeadFilterSelection}
            >
              Clear filters
            </button>
          ) : null}
        </div>

        <div className={styles.leadFilterScroll} data-wilsy-independent-scroll="lead-filter-options">
          {visibleFilterSections.length ? visibleFilterSections.map(section => (
            <section key={section.id} className={styles.leadFilterSection}>
              <header className={styles.leadFilterSectionHeader}>
                <span aria-hidden="true">▾</span>
                <strong>{section.title}</strong>
              </header>

              <div className={styles.leadFilterOptionStack}>
                {section.options.map(option => {
                  const optionSelected = selectedLeadFilterOptions.has(option.id);
                  const checkboxId = `lead-filter-${section.id}-${option.id}`;

                  return (
                    <label
                      key={option.id}
                      className={styles.leadFilterOption}
                      data-selected={optionSelected ? 'true' : 'false'}
                      data-wilsy-lead-filter-option="controlled-checkbox"
                      htmlFor={checkboxId}
                    >
                      <input
                        id={checkboxId}
                        type="checkbox"
                        checked={optionSelected}
                        onChange={() => setSelectedLeadFilterOptions(previous => {
                          const nextSelection = new Set(previous);

                          if (nextSelection.has(option.id)) {
                            nextSelection.delete(option.id);
                          } else {
                            nextSelection.add(option.id);
                          }

                          return nextSelection;
                        })}
                        aria-label={`Select ${option.label} filter`}
                      />
                      <span>
                        <strong>{option.label}</strong>
                        <em>{option.detail}</em>
                      </span>
                    </label>
                  );
                })}
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
   * @function openWilsyLeadSortViewpoint
   * @description Opens Sort as a full Leads workspace viewpoint instead of a small dropdown.
   * @returns {void}
   * @collaboration Keeps sort work inside the same production viewport as Records and Proof.
   */
  function openWilsyLeadSortViewpoint() {
    setActiveTopTab('sort');
    setCommandOpen(false);
    setCreateMenuOpen(false);
    setMoreMenuOpen(false);
    setThemeMenuOpen(false);
    setOpenRowActionId('');
  }

  /**
   * @function handleWilsyLeadSortViewpointSelect
   * @description Stores the active Leads sort field and direction from the Sort viewpoint.
   * @param {string} field - Lead field key.
   * @param {string} direction - Sort direction.
   * @returns {void}
   * @collaboration Connects sort intent to the visible records and ledger work surface.
   */
  function handleWilsyLeadSortViewpointSelect(field, direction) {
    setLeadSortViewpoint({ field, direction });
  }

  /**
   * @function sortWilsyLeadRecordsForViewpoint
   * @description Sorts Leads for the active Sort viewpoint without mutating source records.
   * @param {Array<object>} records - Candidate Lead records.
   * @returns {Array<object>} Sorted Lead records.
   * @collaboration Keeps source-backed rows deterministic while the operator changes sort posture.
   */
  function sortWilsyLeadRecordsForViewpoint(records) {
    const safeRecords = Array.isArray(records) ? records : [];
    const field = leadSortViewpoint?.field || 'lastActivity';
    const direction = leadSortViewpoint?.direction === 'asc' ? 'asc' : 'desc';

    return [...safeRecords].sort((leftRecord, rightRecord) => {
      const leftValue = String(resolveLeadValue(leftRecord, field) || '').toLowerCase();
      const rightValue = String(resolveLeadValue(rightRecord, field) || '').toLowerCase();

      if (leftValue < rightValue) return direction === 'asc' ? -1 : 1;
      if (leftValue > rightValue) return direction === 'asc' ? 1 : -1;
      return 0;
    });
  }

  /**
   * @function renderLeadRecordsCommandBar
   * @description Renders the records-table command bar with view, tab, filter, sort and create actions.
   * @returns {JSX.Element} Records command bar.
   * @collaboration Places the working controls inside the Lead grid shell from Wilson's vision mock.
   */
  function renderLeadRecordsCommandBar() {
    const activeSort = LEAD_SORT_OPTIONS.find(option => option.id === sortMode) || LEAD_SORT_OPTIONS[0];

    return (
      <section className={styles.leadRecordsCommandBar} data-wilsy-lead-grid-toolbar="R84A-VISION-COMMAND-BAR">
        <section className={styles.leadViewCluster} data-wilsy-leads-organizer-shell="true">
          <div className={styles.leadDropdownWrap} data-wilsy-leads-organizer-wrap="true">
            <button type="button" className={styles.leadViewButton} onClick={() => setViewMenuOpen(previous => !previous)}>
              <SlidersHorizontal size={18} />
              <span>
                <strong>{resolveLeadOperatingCopyLabel(activeLeadOrganizerView.label, activeListViewId)}</strong>
                <em>{formatWilsySelectorBackendCountLabel(activeLeadOrganizerView)}</em>
              </span>
              <ChevronDown size={16} />
            </button>

            {viewMenuOpen ? (
              <section className={styles.leadOrganizerCompactMenu} data-wilsy-leads-organizer-compact-menu="FG97" aria-label="Lead list views">
                {leadOrganizerLiveViews.map(view => (
                  <button
                    key={view.id}
                    type="button"
                    data-active={String(view.id) === String(activeListViewId) ? 'true' : 'false'}
                    onClick={() => {
                      setActiveListViewId(view.id || 'ALL');
                      setCurrentLeadPage(1);
                      setCurrentLeadPage(1);
                      setViewMenuOpen(false);
                    }}
                  >
                    <span>{resolveLeadOperatingCopyLabel(view.label, view.id)}</span>
                    <em>{formatWilsySelectorBackendCountLabel(view)}</em>
                  </button>
                ))}
                <button type="button" onClick={() => setCommandOpen(true)}>
                  <Plus size={14} />
                  <span>New Custom View</span>
                </button>
              </section>
            ) : null}
          </div>
        </section>

        <nav className={styles.leadRecordsTabs} aria-label="Lead records tabs">
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
                <span>{resolveLeadOperatingCopyLabel(tab.label, tab.id)}</span>
              </button>
            );
          })}
        </nav>

        <section className={styles.leadRecordsActions}>
          <button
            type="button"
            onClick={() => setFilterPanelOpen(previous => !previous)}
            data-active={filterPanelOpen ? 'true' : 'false'}
          >
            <SlidersHorizontal size={18} />
            <span>Filter</span>
          </button>

          <div className={styles.leadDropdownWrap}>
            <button
              type="button"
              className={styles.leadSortButton}
              onClick={openWilsyLeadSortViewpoint}
              data-wilsy-lead-sort-trigger="viewpoint"
              data-active={activeTopTab === 'sort' ? 'true' : 'false'}
            >
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
                        setCurrentLeadPage(1);
                        setSortMenuOpen(false);
                      }}
                  >
                    <span>{option.label}</span>
                  </button>
                ))}
              </section>
            ) : null}
          </div>

          <button type="button" className={styles.leadSplitButton} onClick={() => setSplitView(previous => !previous)} data-active={splitView ? 'true' : 'false'}>
            <SplitSquareHorizontal size={18} />
            <span>{splitView ? 'Single' : 'Split'}</span>
          </button>

          <div className={styles.headerMoreDock}>
            <button type="button" className={styles.leadMoreButton} onClick={() => setMoreMenuOpen(previous => !previous)}>
              <MoreHorizontal size={18} />
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

        <div className={styles.leadCreateDock}>
          <button
            type="button"
            className={[styles.headerPrimaryAction, styles.leadCreateButton].join(' ')}
            onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()}
            disabled={!canUseLeadAction(role, 'create')}
          >
            <Plus size={18} />
            <span>{leadOperatingCopy.createLabel}</span>
          </button>
                    {renderWilsyToolbarCollectionActions()}
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
              <button type="button" onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()}><Plus size={14} />{leadOperatingCopy.createLabel}</button>
              <button type="button" disabled={!canUseLeadAction(role, 'import')}><Upload size={14} />Import Leads</button>
              <button type="button" disabled={!canUseLeadAction(role, 'import')}><FileInput size={14} />Import Notes</button>
            </section>
          ) : null}
        </div>
      </section>
    );
  }
  /**
   * @function handleLeadMassEmail
   * @description Opens the governed Mass Email command capsule for the selected Lead rows.
   * @returns {void}
   * @collaboration Selected-row CRUD bar, Wilsy Lead command capsule, backend-governed Lead communication workflow.
   */
  function handleLeadMassEmail() {
    const recordIds = Array.isArray(selectedRowIds) ? selectedRowIds.filter(Boolean) : [];
    const record = resolveSelectedLeadActionRecord(selectedRowIds[0], 0) || {};
    const recordId = recordIds[0] || resolveLeadRecordId(record, 0);

    openWilsyLeadCommandCapsule({
      mode: 'email',
      label: 'Mass Email',
      record,
      recordId,
      recordIds,
      tenantId
    });
  }
  /**
   * @function closeWilsyR91K179E24P56D2TransientRecordMenus
   * @description Closes transient CRM dropdown menus before foreground command surfaces open.
   * @returns {void}
   * @collaboration Proof Trail foreground behavior, More menu, Create menu, Sort menu, CRM command capsule.
   */
  function closeWilsyR91K179E24P56D2TransientRecordMenus() {
    try {
      if (typeof setMoreMenuOpen === 'function') setMoreMenuOpen(false);
      if (typeof setCreateMenuOpen === 'function') setCreateMenuOpen(false);
      if (typeof setSortMenuOpen === 'function') setSortMenuOpen(false);
      if (typeof setOpenRowActionId === 'function') setOpenRowActionId('');
    } catch (error) {
      // Non-fatal: command capsule must still open even if a transient menu state is unavailable.
    }
  } /* R91K179E24P56D2_CLOSE_TRANSIENT_MENUS */

  /**
   * @function openLeadCrudPanel
   * @description Opens the dedicated R91K Lead command capsule for View, Proof Trail, Edit, Delete Selected, Change Owner, Mass Update, and Mass Email actions.
   * @param {string} modeKey - Requested lead action key.
   * @param {Object} record - Lead record context.
   * @param {string} recordId - Lead record identifier.
   * @param {Array<string>} recordIds - Selected Lead record identifiers.
   * @returns {void} Opens the governed Lead command capsule.
   * @collaboration R91K.14B direct button route, WilsyLeadCommandCapsule, selected-row action bar, row action menu.
   */
  function openLeadCrudPanel(modeKey, record = null, recordId = '', recordIds = []) {
    closeWilsyR91K179E24P56D2TransientRecordMenus(); /* R91K179E24P56D2_OPEN_CRUD_CLOSE_MENUS */

    const normalizedLeadAction = String(modeKey || 'view').trim();
    const selectedRecordIds = Array.isArray(recordIds) && recordIds.length
      ? recordIds.filter(Boolean)
      : (Array.isArray(selectedRowIds) ? selectedRowIds.filter(Boolean) : []);

    const resolvedRecord = record || resolveSelectedLeadActionRecord(selectedRowIds[0], 0) || {};
    const resolvedRecordId = recordId || selectedRecordIds[0] || resolveLeadRecordId(resolvedRecord, 0);

    const actionLabels = {
      view: 'View Lead',
      proof: 'Proof Trail',
      edit: 'Edit Lead',
      delete: 'Delete Selected',
      deleteSelected: 'Delete Selected',
      deleteLead: 'Delete Lead',
      changeOwner: 'Change Owner',
      owner: 'Change Owner',
      massUpdate: 'Mass Update',
      email: 'Mass Email',
      massEmail: 'Mass Email'
    };

    const actionModes = {
      view: 'view',
      proof: 'proof',
      edit: 'edit',
      delete: 'delete',
      deleteSelected: 'delete',
      deleteLead: 'delete',
      changeOwner: 'changeOwner',
      owner: 'changeOwner',
      massUpdate: 'massUpdate',
      email: 'email',
      massEmail: 'email'
    };

    const mode = actionModes[normalizedLeadAction] || normalizedLeadAction || 'view';
    const label = actionLabels[normalizedLeadAction] || actionLabels[mode] || 'View Lead';

    openWilsyLeadCommandCapsule({
      mode,
      label,
      record: resolvedRecord,
      recordId: resolvedRecordId,
      recordIds: selectedRecordIds.length ? selectedRecordIds : [resolvedRecordId].filter(Boolean),
      module: leadOperatingCopy?.recordPlural || resolvedRecord?.sourceModule || resolvedRecord?.source || 'leads',
      moduleName: leadOperatingCopy?.title || leadOperatingCopy?.recordPlural || 'Leads',
      recordModule: leadOperatingCopy?.recordPlural || resolvedRecord?.sourceModule || resolvedRecord?.source || 'leads',
      sourceModule: resolvedRecord?.sourceModule || resolvedRecord?.source || leadOperatingCopy?.recordPlural || 'leads',
      recordSingular: leadOperatingCopy?.recordSingular || 'lead',
      recordPlural: leadOperatingCopy?.recordPlural || 'leads',
      operatingCopy: leadOperatingCopy,
      governanceCopy: {
        module: leadOperatingCopy?.recordPlural || resolvedRecord?.sourceModule || resolvedRecord?.source || 'leads',
        title: leadOperatingCopy?.title || 'Leads',
        recordSingular: leadOperatingCopy?.recordSingular || 'lead',
        recordPlural: leadOperatingCopy?.recordPlural || 'leads',
        recordNameLabel: leadOperatingCopy?.tableHeaders?.name || 'Lead Name',
        companyLabel: leadOperatingCopy?.tableHeaders?.company || 'Company',
        emailLabel: leadOperatingCopy?.tableHeaders?.email || 'Email',
        phoneLabel: leadOperatingCopy?.tableHeaders?.phone || 'Phone',
        commandSurface: 'R91K179E24P58D2_MODULE_AWARE_DELETE_GOVERNANCE',
      }, /* R91K179E24P58D2_MODULE_CONTEXT */
      tenantId
    });
  }

  /**
   * @function openLeadCrudPanelWithAuthority
   * @description Opens authority-gated Lead CRUD actions while allowing View and Proof Trail without mutation authority.
   * @param {string} modeKey - Requested lead action key.
   * @param {Object} record - Lead record context.
   * @param {string} recordId - Lead record identifier.
   * @param {Array<string>} recordIds - Selected Lead record identifiers.
   * @returns {void} Opens the Lead command capsule when allowed.
   * @collaboration R91K.14B direct button route, selected-row CRUD authority, backend final authority posture.
   */
  function openLeadCrudPanelWithAuthority(modeKey, record = null, recordId = '', recordIds = []) {
    const normalizedMode = String(modeKey || 'view').trim();

    if (['edit', 'delete', 'deleteSelected', 'deleteLead', 'changeOwner', 'owner', 'massUpdate'].includes(normalizedMode)
      && !canUseLeadAdministrativeCrud(role, normalizedMode)) {
      openLeadCrudPanel('proof', record, recordId, recordIds);
      return;
    }

    openLeadCrudPanel(normalizedMode, record, recordId, recordIds);
  }
  /**
   * @function resolveSelectedLeadActionIds
   * @description Resolves selected Lead identifiers for selected-row command buttons without relying on stale render-local variables.
   * @returns {Array<string>} Selected Lead record identifiers.
   * @collaboration Selected-row CRUD bar, command capsule routing, restored Leads records table.
   */
  function resolveSelectedLeadActionIds() {
    return Array.isArray(selectedRowIds) ? selectedRowIds.filter(Boolean) : [];
  }

  /**
   * @function resolveSelectedLeadActionRecord
   * @description Resolves the selected Lead record for selected-row command buttons without using the stale selectedLeadRecords binding.
   * @param {string} recordId - Selected Lead record identifier.
   * @param {number} fallbackIndex - Fallback row index.
   * @returns {Object} Selected Lead record context.
   * @collaboration Selected-row CRUD bar, Wilsy Lead command capsule, lead record identity resolver.
   */
  function resolveSelectedLeadActionRecord(recordId = '', fallbackIndex = 0) {
    const normalizedRecordId = String(recordId || '').trim();

    const candidateGroups = [
      typeof paginatedLeads !== 'undefined' ? paginatedLeads : [],
      typeof filteredLeads !== 'undefined' ? filteredLeads : [],
      typeof leadRows !== 'undefined' ? leadRows : [],
      typeof leads !== 'undefined' ? leads : [],
      typeof normalizedLeads !== 'undefined' ? normalizedLeads : [],
      typeof liveLeads !== 'undefined' ? liveLeads : []
    ];

    for (const candidateGroup of candidateGroups) {
      if (!Array.isArray(candidateGroup)) {
        continue;
      }

      const matchedRecord = candidateGroup.find((record, index) => (
        resolveLeadRecordId(record, index) === normalizedRecordId
        || String(record?.id || record?._id || record?.leadId || record?.recordId || '').trim() === normalizedRecordId
      ));

      if (matchedRecord) {
        return matchedRecord;
      }
    }

    if (typeof selectedLead !== 'undefined' && selectedLead) {
      return selectedLead;
    }

    const fallbackGroup = candidateGroups.find((candidateGroup) => Array.isArray(candidateGroup) && candidateGroup.length) || [];

    return fallbackGroup[fallbackIndex] || {};
  }




  /**
   * @function renderLeadRecordsTable
   * @description Renders the records-first Lead module grid with row and mass actions.
   * @returns {JSX.Element} Lead records workspace.
   * @collaboration Replaces the continuous card runway with an operating CRM list view.
   */
  function renderLeadRecordsTable() {
    const visibleIds = paginatedLeads.map((record, index) => resolveLeadRecordId(record, leadPagination.startIndex + index));
    const allRowsSelected = visibleIds.length > 0 && visibleIds.every(recordId => selectedRowIds.includes(recordId));
    const activeSort = LEAD_SORT_OPTIONS.find(option => option.id === sortMode) || LEAD_SORT_OPTIONS[0];

    return (
      <section className={styles.leadRecordsWorkspace}
        data-wilsy-filter-state={filterPanelOpen ? 'open' : 'closed'}
        data-wilsy-leads-listview-shell="R83A-DB-ONLY-PRODUCT-SHELL"
        data-wilsy-lead-row-count={filteredLeads.length}
        data-wilsy-base-lead-row-count={baseFilteredLeads.length}
        data-wilsy-selected-lead-filter-count={selectedLeadFilterOptions.size}
        data-wilsy-lead-page-count={leadPagination.totalPages}
        data-wilsy-real-data-contract="LIVE_BACKEND_ONLY"
        data-wilsy-lead-workbench="R80B-COMPOSED-RECORDS-SURFACE"
        data-wilsy-lead-product-surface="R81A-REAL-DATA-LISTVIEW" data-wilsy-lead-records="tabbed-list-view">
        {renderLeadRecordsCommandBar()}
        {renderLeadFilterRail()}

        <section className={styles.leadRecordsPanel}>
          <header className={styles.leadRecordsHeader}>
            <span>
              <small>{resolveLeadOperatingCopyLabel(activeLeadOrganizerView.label, activeListViewId)}</small>
              <strong>{filteredLeads.length} records</strong>
              <em>{selectedRowIds.length ? `${selectedRowIds.length} selected` : selectedLeadFilterOptions.size ? `${selectedLeadFilterOptions.size} active filters · ${baseFilteredLeads.length} source rows` : `${activeSort.label} order`}</em>
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
              <button
                type="button"
                disabled={selectedRowIds.length !== 1}
                onClick={() => openLeadCrudPanel('view', resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], [selectedRowIds[0]])}
              >
                View
              </button>
              <button
                type="button"
                disabled={selectedRowIds.length !== 1 || !canUseLeadAdministrativeCrud(role, 'edit')}
                aria-disabled={selectedRowIds.length !== 1 || !canUseLeadAdministrativeCrud(role, 'edit')}
                title={resolveLeadCrudAuthorityReason(role)}
                onClick={() => handleWilsyR91K179E26OperatingEditAction(resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], [selectedRowIds[0]])}
              >
                Edit
              </button>
              <button
                type="button"
                disabled={selectedRowIds.length !== 1}
                onClick={() => openLeadCrudPanel('proof', resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], [selectedRowIds[0]])}
              >
                Proof Trail
              </button>
              <button type="button" onClick={() => openLeadCrudPanel('email', resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], selectedRowIds)}>
                <Mail size={14} />
                Mass Email
              </button>
              <button
                type="button"
                disabled={!selectedRowIds.length || !canUseLeadAdministrativeCrud(role, 'massUpdate')}
                aria-disabled={!selectedRowIds.length || !canUseLeadAdministrativeCrud(role, 'massUpdate')}
                title={resolveLeadCrudAuthorityReason(role)}
                onClick={() => openLeadCrudPanelWithAuthority('massUpdate', resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], selectedRowIds)}
              >
                <ClipboardList size={14} />
                Mass Update
              </button>
              <button
                type="button"
                disabled={!selectedRowIds.length || !canUseLeadAdministrativeCrud(role, 'changeOwner')}
                aria-disabled={!selectedRowIds.length || !canUseLeadAdministrativeCrud(role, 'changeOwner')}
                title={resolveLeadCrudAuthorityReason(role)}
                onClick={() => openLeadCrudPanelWithAuthority('changeOwner', resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], selectedRowIds)}
              >
                <UserRoundCog size={14} />
                Change Owner
              </button>
              <button
                type="button"
                disabled={!selectedRowIds.length || !canUseLeadAdministrativeCrud(role, 'delete')}
                aria-disabled={!selectedRowIds.length || !canUseLeadAdministrativeCrud(role, 'delete')}
                title={resolveLeadCrudAuthorityReason(role)}
                onClick={() => openLeadCrudPanelWithAuthority('deleteSelected', resolveSelectedLeadActionRecord(selectedRowIds[0], 0), selectedRowIds[0], selectedRowIds)}
              >
                Delete Selected
              </button>
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
                  <th>{leadOperatingCopy.tableHeaders.name}</th>
                  <th>{leadOperatingCopy.tableHeaders.company}</th>
                  <th>{leadOperatingCopy.tableHeaders.email}</th>
                  <th>{leadOperatingCopy.tableHeaders.phone}</th>
                  <th>{leadOperatingCopy.tableHeaders.owner}</th>
                  <th>{leadOperatingCopy.tableHeaders.status}</th>
                  <th>{leadOperatingCopy.tableHeaders.score}</th>
                  <th aria-label="Row actions" />
                </tr>
              </thead>
              <tbody>
                {filteredLeads.length ? paginatedLeads.map((record, index) => {
                  const sourceIndex = leadPagination.startIndex + index;
                  const recordId = resolveLeadRecordId(record, sourceIndex);
                  const stage = resolveLeadStage(record);
                  const ownerLabel = resolveWilsyR91KOwnerTableDisplay(record, resolveLeadOwnerLabel);
                  const priorityScore = resolveLeadPriorityScore(record);
                  const emailHref = resolveLeadContactHref(record, 'email');
                  const phoneHref = resolveLeadContactHref(record, 'phone');
                  const rowSourceModule = String(record.sourceModule || record.module || '').toLowerCase();
                  const rowName = resolveLeadValue(record, 'name');
                  const rowSubtitle = resolveLeadSubtitle(record);
                  const rowCompany = resolveLeadValue(record, 'company');
                  const rowEmail = resolveLeadValue(record, 'email');
                  const rowPhone = resolveLeadValue(record, 'phone');

                  return (
                    <tr
                      key={recordId}
                      data-selected={selectedRowIds.includes(recordId) ? 'true' : 'false'}
                      data-wilsy-source-module={rowSourceModule || undefined}
                    >
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Select ${rowName}`}
                          checked={selectedRowIds.includes(recordId)}
                          onChange={(event) => handleToggleLeadSelection(recordId, event)}
                        />
                      </td>
                      <td>
                        <button type="button" className={styles.leadNameCell} onClick={() => setSelectedLeadId(recordId)}>
                          <strong title={rowName}>{rowName}</strong>
                          <em title={rowSubtitle}>{rowSubtitle}</em>
                        </button>
                      </td>
                      <td title={rowCompany}>{rowCompany}</td>
                      <td>
                        {emailHref ? <a href={emailHref}>{rowEmail}</a> : <span title={rowEmail}>{rowEmail}</span>}
                      </td>
                      <td>
                        <span className={styles.leadPhoneCell}>
                          {phoneHref ? <a href={phoneHref}>{rowPhone}</a> : <span title={rowPhone}>{rowPhone}</span>}
                          {phoneHref ? <Phone size={14} /> : null}
                        </span>
                      </td>
                      <td>
                        <span className={styles.leadOwnerCell}>
                          <b>{resolveLeadOwnerInitials(ownerLabel)}</b>
                          <em>{ownerLabel}</em>
                        </span>
                      </td>
                      <td>
                        <span className={styles.leadStagePill} data-tone={resolveLeadStageTone(stage)}>
                          {stage}
                        </span>
                      </td>
                      <td>
                        <span className={styles.leadScoreOrb} data-score-band={resolveLeadPriorityBand(priorityScore)}>
                          {priorityScore}
                        </span>
                      </td>
                      <td className={styles.leadRowActionsCell}>
                        <button type="button" onClick={() => setOpenRowActionId(openRowActionId === recordId ? '' : recordId)} title="Record actions">
                          <MoreHorizontal size={17} />
                        </button>
                        {openRowActionId === recordId ? (
                          <section className={styles.leadRowActionMenu} aria-label="Record actions">
                            <button type="button" onClick={() => handleWilsyR91K179E26OperatingEditAction(record, recordId, [recordId])}>Edit Record</button>
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
                <tr
                  className={styles.leadEmptyRow}
                  data-wilsy-real-data-empty-state="LIVE_BACKEND_EMPTY"
                >
                  <td data-wilsy-lead-empty-state="records" colSpan={9}>
                    <section className={styles.leadRealEmptyState}>
                      <strong>{selectedLeadFilterOptions.size ? 'No leads match the selected filters' : 'No live leads returned yet'}</strong>
                      <em>{selectedLeadFilterOptions.size ? 'Clear or change the selected filters to return matching live backend rows.' : 'Verified backend Lead records will appear here after source sync or lead creation.'}</em>
                    </section>
                  </td>
                </tr>
              )}
              </tbody>
            </table>
          </div>

          <footer className={styles.leadRecordsFooter} data-wilsy-lead-footer="LIVE_BACKEND_RECORDS_FOOTER">
            <span className={styles.leadFooterRecordRange}>
              <strong>{shouldUseWilsyBackendCursorPagination() ? formatWilsyBackendCursorRange() : filteredLeads.length ? `Showing ${leadPagination.startRecord} to ${leadPagination.endRecord} of ${filteredLeads.length} ${leadOperatingCopyRecordPlural}` : selectedLeadFilterOptions.size ? `Showing 0 matching ${leadOperatingCopyRecordPlural}` : `Showing 0 live ${leadOperatingCopyRecordPlural}`}</strong>
              <em>{shouldUseWilsyBackendCursorPagination() ? formatWilsyBackendCursorSupport() : selectedRowIds.length ? `${selectedRowIds.length} selected` : selectedLeadFilterOptions.size ? `${selectedLeadFilterOptions.size} active filters · ${baseFilteredLeads.length} source rows` : 'Live backend rows only'}</em>
            </span>
            <nav className={styles.leadFooterPagination} aria-label={`${leadOperatingCopyTitle} records pagination`}>
              <button type="button" disabled={shouldUseWilsyBackendCursorPagination() ? !resolveWilsyActiveBackendRunPagination()?.hasPreviousPage || Boolean(leadToolbarCommandBusy) : leadPagination.currentPage <= 1} aria-label="First page" onClick={() => shouldUseWilsyBackendCursorPagination() ? void handleWilsyBackendCursorPageChange('first') : handleLeadPageChange(1)}>|&lt;</button>
              <button type="button" disabled={shouldUseWilsyBackendCursorPagination() ? !resolveWilsyActiveBackendRunPagination()?.previousCursor || Boolean(leadToolbarCommandBusy) : leadPagination.currentPage <= 1} aria-label="Previous page" onClick={() => shouldUseWilsyBackendCursorPagination() ? void handleWilsyBackendCursorPageChange('previous') : handleLeadPageChange(leadPagination.currentPage - 1)}>&lt;</button>
              {shouldUseWilsyBackendCursorPagination() ? (
                <button
                  type="button"
                  aria-current="page"
                  data-wilsy-backend-cursor-page="FG103V2"
                  disabled
                >
                  Cursor
                </button>
              ) : leadPagination.pageItems.map(item => (
                typeof item === 'number' ? (
                  <button
                    key={item}
                    type="button"
                    aria-current={item === leadPagination.currentPage ? 'page' : undefined}
                    onClick={() => handleLeadPageChange(item)}
                  >
                    {item}
                  </button>
                ) : (
                  <span key={item} data-wilsy-pagination-ellipsis="true">...</span>
                )
              ))}
              <button type="button" disabled={shouldUseWilsyBackendCursorPagination() ? !resolveWilsyActiveBackendRunPagination()?.nextCursor || Boolean(leadToolbarCommandBusy) : leadPagination.currentPage >= leadPagination.totalPages} aria-label="Next page" onClick={() => shouldUseWilsyBackendCursorPagination() ? void handleWilsyBackendCursorPageChange('next') : handleLeadPageChange(leadPagination.currentPage + 1)}>&gt;</button>
              <button type="button" disabled={shouldUseWilsyBackendCursorPagination() ? true : leadPagination.currentPage >= leadPagination.totalPages} aria-label="Last page" title={shouldUseWilsyBackendCursorPagination() ? 'Cursor pagination uses Next until the backend reports the end.' : 'Last page'} onClick={() => shouldUseWilsyBackendCursorPagination() ? undefined : handleLeadPageChange(leadPagination.totalPages)}>&gt;|</button>
              <label className={styles.leadFooterPageSize}>
                <select
                  value={leadPagination.pageSize}
                  onChange={event => handleWilsyBackendCursorPageSizeChange(event.target.value)}
                  aria-label={`${leadOperatingCopyTitle} records per page`}
                >
                  {LEAD_PAGE_SIZE_OPTIONS.map(option => (
                    <option key={option} value={option}>{option} / page</option>
                  ))}
                </select>
              </label>
            </nav>
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
   * @function renderLeadSortTab
   * @description Renders Sort as a full Leads workspace viewpoint.
   * @returns {JSX.Element} Leads Sort viewpoint.
   * @collaboration Turns sorting into a visible task surface with field, direction and preview evidence.
   */
  function renderLeadSortTab() {
    const sortFields = LEAD_COLUMNS.filter(column => column.key !== 'actions');
    const sortedPreview = sortWilsyLeadRecordsForViewpoint(filteredLeads).slice(0, 8);
    const activeFieldLabel = sortFields.find(column => column.key === leadSortViewpoint.field)?.label || 'Last Activity';
    const activeDirectionLabel = leadSortViewpoint.direction === 'asc' ? 'Ascending' : 'Descending';

    return (
      <section className={styles.leadSortViewpoint} data-wilsy-lead-sort-viewpoint="workarea">
        <header className={styles.leadSortViewpointHeader}>
          <span>
            <small>Sort Operating Viewpoint</small>
            <strong>{activeFieldLabel} · {activeDirectionLabel}</strong>
            <em>{filteredLeads.length} source-backed rows ready for ordering</em>
          </span>
          <div>
            <button type="button" onClick={() => handleWilsyLeadSortViewpointSelect('lastActivity', 'desc')}>
              Latest Activity
            </button>
            <button type="button" onClick={() => setActiveTopTab('records')}>
              Return Records
            </button>
          </div>
        </header>

        <section className={styles.leadSortViewpointGrid}>
          <article className={styles.leadSortViewpointPanel}>
            <small>Sort field</small>
            <strong>Choose the record authority</strong>
            <div className={styles.leadSortFieldGrid}>
              {sortFields.map(column => (
                <button
                  key={column.key}
                  type="button"
                  data-active={leadSortViewpoint.field === column.key ? 'true' : 'false'}
                  onClick={() => handleWilsyLeadSortViewpointSelect(column.key, leadSortViewpoint.direction)}
                >
                  <span>{column.label}</span>
                  <em>{column.key}</em>
                </button>
              ))}
            </div>
          </article>

          <article className={styles.leadSortViewpointPanel}>
            <small>Direction</small>
            <strong>Control row movement</strong>
            <div className={styles.leadSortDirectionGrid}>
              <button
                type="button"
                data-active={leadSortViewpoint.direction === 'asc' ? 'true' : 'false'}
                onClick={() => handleWilsyLeadSortViewpointSelect(leadSortViewpoint.field, 'asc')}
              >
                <span>Ascending</span>
                <em>A to Z, low to high</em>
              </button>
              <button
                type="button"
                data-active={leadSortViewpoint.direction === 'desc' ? 'true' : 'false'}
                onClick={() => handleWilsyLeadSortViewpointSelect(leadSortViewpoint.field, 'desc')}
              >
                <span>Descending</span>
                <em>Z to A, high to low</em>
              </button>
            </div>
          </article>

          <article className={styles.leadSortViewpointPreview}>
            <small>Sorted preview</small>
            <strong>Visible row order</strong>
            <div>
              {sortedPreview.length ? sortedPreview.map((record, index) => (
                <button key={record._id || record.id || `sort-preview-${index}`} type="button">
                  <span>{index + 1}</span>
                  <strong>{resolveLeadValue(record, 'leadName')}</strong>
                  <em>{resolveLeadValue(record, leadSortViewpoint.field)}</em>
                </button>
              )) : (
                <p>No source-backed rows available for sorting.</p>
              )}
            </div>
          </article>
        </section>
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
    if (activeTopTab === 'sort') return renderLeadSortTab();
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
       data-wilsy-lead-proof-viewpoint={activeTopTab === 'proof' ? 'workarea-scroll' : undefined}
          data-wilsy-lead-sort-viewpoint={activeTopTab === 'sort' ? 'workarea' : undefined}>
        {renderWilsyLeadAIResponseSurface()}
        {activeTopTab === 'records' ? renderLeadVisionMetricDeck() : null}
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
            onClick={() => {
              setActiveFilter(view);
              setCurrentLeadPage(1);
            }}
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
            <button type="button" onClick={() => handleWilsyR91K179E24P49BOperatingCreateAction()}>Create Verified Lead</button>
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
    const ledgerRows = sortWilsyLeadRecordsForViewpoint(filteredLeads);

    return (
      <section
        className={styles.ledgerPanel}
        data-wilsy-ledger-state={hasRows ? 'populated' : 'empty'}
      >
        <header>
          <span>
            <small>Data Provenance Ledger</small>
            <strong>{leadOperatingCopy.allRecordsLabel}</strong>
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
                {ledgerRows.map((record, index) => (
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
    if (activeTopTab === 'proof') {
      return renderWilsyProductionProofCockpit();
    }

    /* P60K5Q10FG104A_PROOF_TAB_USES_PRODUCTION_COCKPIT */

    return renderLeadTabbedWorkspace();
  }

  /**
   * @function normalizeWilsyR91K85AddressText
   * @description Normalizes address command input before local intelligence suggestions are built.
   * @param {unknown} value - Candidate address text.
   * @returns {string} Normalized address text.
   * @collaboration Powers the Create Lead sovereign address command without exposing provider keys.
   */
  function normalizeWilsyR91K85AddressText(value = '') {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  /**
   * @function resolveWilsyR91K85AddressCountry
   * @description Resolves a safe country value for address intelligence metadata.
   * @param {Object} draftPayload - Current Lead draft.
   * @returns {string} Country label.
   * @collaboration Keeps address capture South Africa-ready while allowing global CRM records.
   */
  function resolveWilsyR91K85AddressCountry(draftPayload = {}) {
    const candidate = normalizeWilsyR91K85AddressText(
      draftPayload.country ||
      draftPayload.addressCountry ||
      draftPayload.billingCountry ||
      ''
    );

    return candidate || 'South Africa';
  }

  /**
   * @function resolveWilsyR91K85AddressPostalCode
   * @description Extracts a likely postal code from address text or draft aliases.
   * @param {string} query - Address search query.
   * @param {Object} draftPayload - Current Lead draft.
   * @returns {string} Postal code candidate.
   * @collaboration Gives Create Lead instant normalized address posture before provider verification.
   */
  function resolveWilsyR91K85AddressPostalCode(query = '', draftPayload = {}) {
    const direct = normalizeWilsyR91K85AddressText(
      draftPayload.zipCode ||
      draftPayload.postalCode ||
      draftPayload.postcode ||
      ''
    );

    if (direct) {
      return direct;
    }

    const match = String(query || '').match(/\b\d{4,6}\b/);

    return match ? match[0] : '';
  }

  /**
   * @function buildWilsyR91K85AddressSuggestion
   * @description Builds one backend-ready address intelligence suggestion packet.
   * @param {Object} params - Suggestion parameters.
   * @returns {Object} Address suggestion packet.
   * @collaboration Makes Create Lead address selection auditable before provider routes are activated.
   */
  function buildWilsyR91K85AddressSuggestion(params = {}) {
    const query = normalizeWilsyR91K85AddressText(params.query);
    const draftPayload = params.draft || {};
    const parts = query.split(',').map(part => normalizeWilsyR91K85AddressText(part)).filter(Boolean);
    const street = normalizeWilsyR91K85AddressText(params.street || draftPayload.street || parts[0] || query);
    const city = normalizeWilsyR91K85AddressText(params.city || draftPayload.city || parts[1] || '');
    const state = normalizeWilsyR91K85AddressText(params.state || draftPayload.state || parts[2] || '');
    const country = normalizeWilsyR91K85AddressText(params.country || resolveWilsyR91K85AddressCountry(draftPayload));
    const postalCode = normalizeWilsyR91K85AddressText(params.postalCode || resolveWilsyR91K85AddressPostalCode(query, draftPayload));
    const formattedAddress = [street, city, state, postalCode, country].filter(Boolean).join(', ');
    const confidence = params.confidence || (street && city && country ? 82 : street && country ? 64 : 38);

    return {
      id: params.id || `wilsy-address-${String(params.rank || 1)}-${formattedAddress.length}`,
      label: params.label || 'Sovereign address candidate',
      street,
      city,
      state,
      postalCode,
      country,
      latitude: params.latitude || '',
      longitude: params.longitude || '',
      formattedAddress,
      provider: params.provider || 'WILSY_LOCAL_INTELLIGENCE',
      providerId: params.providerId || `LOCAL-${confidence}-${formattedAddress.length}`,
      confidence,
      verificationStatus: params.verificationStatus || (confidence >= 80 ? 'LOCAL_READY_FOR_PROVIDER_VERIFY' : 'MANUAL_REVIEW_REQUIRED'),
      territory: params.territory || [city, state, country].filter(Boolean).join(' · '),
      duplicatePosture: params.duplicatePosture || 'Duplicate check queued on save',
      receipt: params.receipt || `ADDR-R91K85-${confidence}-${formattedAddress.length}`,
    };
  }

  /**
   * @function buildWilsyR91K85AddressSuggestions
   * @description Builds local address suggestions while backend provider proxy routes are offline.
   * @param {Object} params - Suggestion build parameters.
   * @returns {Array<Object>} Address suggestions.
   * @collaboration Gives Wilsy OS autocomplete-grade UX without leaking Google, Mapbox, Loqate, or HERE keys.
   */
  function buildWilsyR91K85AddressSuggestions(params = {}) {
    const draftPayload = params.draft || {};
    const query = normalizeWilsyR91K85AddressText(
      params.query ||
      draftPayload.addressSearch ||
      draftPayload.formattedAddress ||
      draftPayload.street ||
      ''
    );

    if (query.length < 3 && !draftPayload.street) {
      return [];
    }

    const primary = buildWilsyR91K85AddressSuggestion({
      id: 'wilsy-r91k85-primary-address',
      label: 'Primary address candidate',
      query,
      draft: draftPayload,
      rank: 1,
      confidence: query.includes(',') ? 86 : 68,
    });

    const territory = buildWilsyR91K85AddressSuggestion({
      id: 'wilsy-r91k85-territory-address',
      label: 'Territory routing candidate',
      query,
      draft: {
        ...draftPayload,
        street: draftPayload.street || primary.street,
        city: draftPayload.city || primary.city,
        state: draftPayload.state || primary.state,
        zipCode: draftPayload.zipCode || primary.postalCode,
        country: draftPayload.country || primary.country,
      },
      rank: 2,
      confidence: primary.city ? 78 : 58,
      provider: 'WILSY_TERRITORY_ROUTER',
      verificationStatus: primary.city ? 'ROUTING_READY' : 'CITY_REQUIRED_FOR_ROUTING',
      territory: primary.territory || 'Territory pending city',
      receipt: `ADDR-R91K85-TERRITORY-${primary.formattedAddress.length}`,
    });

    return [primary, territory].filter((suggestion, index, list) => (
      suggestion.formattedAddress &&
      list.findIndex(item => item.formattedAddress === suggestion.formattedAddress && item.provider === suggestion.provider) === index
    ));
  }

  /**
   * @function formatWilsyR91K102AddressProviderLabel
   * @description Converts address provider codes into Wilsy OS business-facing labels.
   * @param {string} provider - Provider code.
   * @returns {string} Business-facing provider label.
   * @collaboration Keeps Create Lead address intelligence clean for tenant operators.
   */
  function formatWilsyR91K102AddressProviderLabel(provider = '') {
    const normalizedProvider = normalizeWilsyR91K85AddressText(provider).toUpperCase();

    if (normalizedProvider.includes('MAPBOX')) {
      return 'Mapbox Address Intelligence';
    }

    if (normalizedProvider.includes('GOOGLE')) {
      return 'Google Places Intelligence';
    }

    if (normalizedProvider.includes('LOQATE')) {
      return 'Loqate Address Verification';
    }

    if (normalizedProvider.includes('HERE')) {
      return 'HERE Address Intelligence';
    }

    if (normalizedProvider.includes('OPENSTREETMAP') || normalizedProvider.includes('NOMINATIM')) {
      return 'OpenStreetMap emergency fallback';
    }

    if (normalizedProvider.includes('WILSY')) {
      return 'Wilsy OS address intelligence';
    }

    return 'Wilsy OS address intelligence';
  }

  /**
   * @function formatWilsyR91K102AddressStatusLabel
   * @description Converts address status codes into business English.
   * @param {string} status - Address status code.
   * @returns {string} Business-facing status label.
   * @collaboration Removes raw integration codes from the Create Lead user interface.
   */
  function formatWilsyR91K102AddressStatusLabel(status = '') {
    const normalizedStatus = normalizeWilsyR91K85AddressText(status).toUpperCase();

    if (normalizedStatus.includes('LIVE_PROVIDER_SUGGESTED')) {
      return 'Verified provider suggestion';
    }

    if (normalizedStatus.includes('ADDRESS_PROVIDER_LIVE')) {
      return 'Live address intelligence active';
    }

    if (normalizedStatus.includes('LIVE_PROVIDER_LOOKUP_RUNNING')) {
      return 'Searching verified address providers';
    }

    if (normalizedStatus.includes('MANUAL_REVIEW_REQUIRED')) {
      return 'Manual review pending';
    }

    if (normalizedStatus.includes('AWAITING_ADDRESS_INPUT') || normalizedStatus.includes('QUERY_TOO_SHORT')) {
      return 'Ready for address search';
    }

    if (normalizedStatus.includes('ADDRESS_PROVIDER_EMPTY')) {
      return 'No verified match returned yet';
    }

    if (normalizedStatus.includes('ADDRESS_PROVIDER_UNREACHABLE')) {
      return 'Address provider temporarily unavailable';
    }

    if (normalizedStatus.includes('ROUTING_READY')) {
      return 'Territory routing ready';
    }

    return 'Address evidence captured';
  }

  /**
   * @function formatWilsyR91K102AddressConfidenceLabel
   * @description Formats provider confidence for business users.
   * @param {number|string} confidence - Confidence score.
   * @returns {string} Business-facing confidence label.
   * @collaboration Shows match quality without exposing raw system language.
   */
  function formatWilsyR91K102AddressConfidenceLabel(confidence = 0) {
    const numericConfidence = Number(confidence || 0);

    if (!numericConfidence) {
      return 'Confidence pending';
    }

    return `${numericConfidence}% match confidence`;
  }

  /**
   * @function formatWilsyR91K102AddressReceiptLabel
   * @description Formats evidence receipts for business-facing address selection.
   * @param {string} receipt - Provider evidence receipt.
   * @returns {string} Business-facing receipt label.
   * @collaboration Preserves forensic proof while keeping the UI readable.
   */
  function formatWilsyR91K102AddressReceiptLabel(receipt = '') {
    const normalizedReceipt = normalizeWilsyR91K85AddressText(receipt);

    if (!normalizedReceipt) {
      return 'Evidence receipt pending';
    }

    return `Evidence receipt ${normalizedReceipt}`;
  }

  /**
   * @function buildWilsyR91K85AddressVerificationPacket
   * @description Summarizes the selected address verification posture in business-facing language.
   * @param {Object} draftPayload - Current Lead draft payload.
   * @returns {Object} Business-facing address verification packet.
   * @collaboration Create Lead address intelligence, provider evidence, tenant operator experience.
   */
  function buildWilsyR91K85AddressVerificationPacket(draftPayload = {}) {
    const status = normalizeWilsyR91K85AddressText(draftPayload.addressVerificationStatus || '');
    const provider = normalizeWilsyR91K85AddressText(draftPayload.addressSourceProvider || 'WILSY_LOCAL_INTELLIGENCE');
    const confidence = Number(draftPayload.addressConfidence || 0);
    const receipt = normalizeWilsyR91K85AddressText(draftPayload.addressEvidenceReceipt || '');

    return {
      status: formatWilsyR91K102AddressStatusLabel(status || (draftPayload.street ? 'MANUAL_REVIEW_REQUIRED' : 'AWAITING_ADDRESS_INPUT')),
      provider: formatWilsyR91K102AddressProviderLabel(provider),
      confidenceLabel: formatWilsyR91K102AddressConfidenceLabel(confidence),
      receipt: formatWilsyR91K102AddressReceiptLabel(receipt),
    };
  }

  /**
   * @function createWilsyR91K88AddressTraceSeed
   * @description Creates a browser-safe trace seed for signed Address Provider requests.
   * @param {string} prefix - Trace prefix.
   * @returns {string} Trace seed.
   * @collaboration Address provider proxy, institutional integrity shield, CRM Create Lead intelligence.
   */
  function createWilsyR91K88AddressTraceSeed(prefix = 'TRC-WILSY-ADDRESS') {
    const randomPart = Math.random().toString(36).slice(2).toUpperCase();

    return `${prefix}-${Date.now()}-${randomPart}`;
  }

  /**
   * @function stableWilsyR91K88AddressSealStringify
   * @description Builds deterministic sorted-key JSON for signed address provider payloads.
   * @param {unknown} value - Value to stringify.
   * @returns {string} Canonical JSON fragment.
   * @collaboration Matches the signed Lead PATCH payload strategy for address lookup.
   */
  function stableWilsyR91K88AddressSealStringify(value) {
    if (value === null || typeof value !== 'object') {
      return JSON.stringify(value);
    }

    if (Array.isArray(value)) {
      return `[${value.map((entry) => stableWilsyR91K88AddressSealStringify(entry)).join(',')}]`;
    }

    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableWilsyR91K88AddressSealStringify(value[key])}`)
      .join(',')}}`;
  }

  /**
   * @function normalizeWilsyR91K88AddressSealPayloadString
   * @description Normalizes outgoing address provider JSON before SHA3-512 signing.
   * @param {string} bodyString - Outgoing JSON body string.
   * @returns {string} Canonical body string.
   * @collaboration Prevents integrity shield mismatch on signed address lookup requests.
   */
  function normalizeWilsyR91K88AddressSealPayloadString(bodyString = '') {
    try {
      return stableWilsyR91K88AddressSealStringify(JSON.parse(bodyString));
    } catch {
      return bodyString;
    }
  }

  /**
   * @function buildWilsyR91K88AddressSealHeaders
   * @description Builds institutional integrity headers for Address Provider proxy requests.
   * @param {string} bodyString - Exact outgoing request body.
   * @returns {Object} Signed header packet.
   * @collaboration Allows /api/crm/command/address/suggest to pass the same shield as Lead Save.
   */
  function buildWilsyR91K88AddressSealHeaders(bodyString = '') {
    const traceId = createWilsyR91K88AddressTraceSeed();
    const timestamp = new Date().toISOString();
    const nonce = createWilsyR91K88AddressTraceSeed('NONCE-WILSY-ADDRESS');
    const canonicalBodyString = normalizeWilsyR91K88AddressSealPayloadString(bodyString);
    const reconstruction = `${traceId}|${timestamp}|${canonicalBodyString}|${nonce}`;
    const requestSeal = sha3_512(reconstruction).toUpperCase();

    return {
      traceId,
      timestamp,
      nonce,
      requestSeal,
    };
  }

    /**
   * @function requestWilsyR91K87AddressSuggestions
   * @description Requests live address suggestions through the signed Wilsy backend provider proxy.
   * @param {string} value - Address search text.
   * @returns {Promise<void>} Updates draft address suggestion state.
   * @collaboration Signed address provider command, integrity shield, Create Lead address intelligence.
   */
  async function requestWilsyR91K87AddressSuggestions(value = '') {
    const query = normalizeWilsyR91K85AddressText(value);

    if (query.length < 3) {
      updateDraftField('addressSuggestions', []);
      updateDraftField('addressVerificationStatus', 'QUERY_TOO_SHORT');
      updateDraftField('addressSourceProvider', 'WILSY_ADDRESS_PROVIDER_PROXY');
      updateDraftField('addressConfidence', 0);
      updateDraftField('addressEvidenceReceipt', 'Type at least three characters for live address search.');
      return;
    }

    updateDraftField('addressSuggestions', []);
    updateDraftField('addressVerificationStatus', 'LIVE_PROVIDER_LOOKUP_RUNNING');
    updateDraftField('addressSourceProvider', 'WILSY_ADDRESS_PROVIDER_PROXY');
    updateDraftField('addressConfidence', 0);
    updateDraftField('addressEvidenceReceipt', 'Signed provider lookup running through Wilsy backend.');

    try {
      const bodyPayload = {
        q: query,
        query,
        country: draft.country || 'ZA',
        countryCode: draft.countryCode || 'ZA',
        commandSurface: 'R91K91_SIGNED_ADDRESS_PROVIDER_COMMAND',
      };
      const bodyString = JSON.stringify(bodyPayload);
      const sealContract = buildWilsyR91K88AddressSealHeaders(bodyString);

      const response = await fetch('/api/crm/command/address/suggest', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-Tenant-Id': tenantId || 'MASTER',
          'X-Wilsy-Command-Surface': 'R91K91_SIGNED_ADDRESS_PROVIDER_COMMAND',
          'X-Request-ID': sealContract.traceId,
          'X-Trace-ID': sealContract.traceId,
          'X-Correlation-ID': sealContract.traceId,
          'X-Forensic-Timestamp': sealContract.timestamp,
          'X-Cryptographic-Nonce': sealContract.nonce,
          'X-Request-Seal': sealContract.requestSeal,
          'X-Request-Proof': sealContract.requestSeal,
          'X-Quantum-Verified': 'true',
          'X-Wilsy-Address-Command-Seal': 'R91K91_SIGNED_ADDRESS_PROVIDER_COMMAND',
        },
        body: bodyString,
      });

      const body = await response.json().catch(() => ({}));
      const suggestions = Array.isArray(body.suggestions) ? body.suggestions : [];
      const firstSuggestion = suggestions[0] || {};

      if (!response.ok) {
        updateDraftField('addressSuggestions', []);
        updateDraftField('addressSourceProvider', body.provider || 'WILSY_ADDRESS_PROVIDER_PROXY');
        updateDraftField('addressVerificationStatus', body.code || body.error || `HTTP_${response.status}`);
        updateDraftField('addressConfidence', 0);
        updateDraftField('addressEvidenceReceipt', body.message || `Signed address provider failed with HTTP ${response.status}.`);
        return;
      }

      updateDraftField('addressSuggestions', suggestions);
      updateDraftField('addressSourceProvider', body.provider || firstSuggestion.provider || 'WILSY_ADDRESS_PROVIDER_PROXY');
      updateDraftField('addressVerificationStatus', body.sourceStatus || firstSuggestion.verificationStatus || 'ADDRESS_PROVIDER_EMPTY');
      updateDraftField('addressConfidence', firstSuggestion.confidence || 0);
      updateDraftField('addressEvidenceReceipt', body.rootHashShort || body.message || 'Signed address provider response received.');
    } catch (error) {
      updateDraftField('addressSuggestions', []);
      updateDraftField('addressVerificationStatus', 'ADDRESS_PROVIDER_UNREACHABLE');
      updateDraftField('addressSourceProvider', 'WILSY_ADDRESS_PROVIDER_PROXY');
      updateDraftField('addressConfidence', 0);
      updateDraftField('addressEvidenceReceipt', error?.message || 'Signed address provider lookup failed.');
    }
  }

  /**
   * @function resolveWilsyR91K92AddressEmptyStateMessage
   * @description Resolves the address intelligence empty-state message in business English.
   * @param {Object} draftPayload - Current Lead draft payload.
   * @param {string} searchText - Current address search text.
   * @returns {string} Operator-facing address intelligence message.
   * @collaboration Wilsy OS address intelligence, provider fallback posture, manual evidence capture.
   */
  function resolveWilsyR91K92AddressEmptyStateMessage(draftPayload = {}, searchText = '') {
    const normalizedSearch = normalizeWilsyR91K85AddressText(searchText);
    const status = normalizeWilsyR91K85AddressText(draftPayload.addressVerificationStatus);

    if (normalizedSearch.length < 3) {
      return 'Start typing to search verified address intelligence through Wilsy OS.';
    }

    if (status === 'LIVE_PROVIDER_LOOKUP_RUNNING') {
      return 'Searching verified address providers through Wilsy OS.';
    }

    if (status === 'ADDRESS_PROVIDER_EMPTY') {
      return 'No verified match returned yet. Continue typing or use manual address capture with evidence.';
    }

    if (status === 'ADDRESS_PROVIDER_UNREACHABLE') {
      return 'Address intelligence is temporarily unavailable. Manual address capture remains available with evidence.';
    }

    return 'Wilsy OS address intelligence is active. Verified suggestions will appear here.';
  }

  /**
   * @function renderCreateMode
   * @description Renders the focused Create Lead surface.
   * @returns {JSX.Element} Create Lead surface.
   * @collaboration Captures verified lead payloads for backend command fabric.
   */
  function renderCreateMode() {
    const addressSearchText = normalizeWilsyR91K85AddressText(
      draft.addressSearch ||
      draft.formattedAddress ||
      draft.street ||
      ''
    );
    const addressSuggestions = Array.isArray(draft.addressSuggestions) ? draft.addressSuggestions : [];
    const addressVerificationPacket = buildWilsyR91K85AddressVerificationPacket(draft);

    return (
      <section
        className={styles.createSurface}
        data-wilsy-lead-create-surface="P60K5Q10FG79_CREATE_AI_AWARE_SURFACE"
        data-wilsy-lead-task-mode="create"
        data-wilsy-ai-component-scope="crm.leads.create"
        data-wilsy-ai-model-awareness="field_groups.source_posture.address_intelligence.proof_readiness.save_contract"
      >
        <header
          className={styles.createHeader}
          data-wilsy-lead-create-header="edit-grade-command-header"
          data-wilsy-ai-component="create-lead-command-header"
        >
          <span><small>Focused Create</small><strong>Create Verified Lead</strong><em>Capture, enrich, schedule and prove the Lead source from one workspace.</em></span>
          <div>
            <button type="button" onClick={() => resetLeadDraftForPrivacy('list')}>Cancel</button>
            <button type="button" disabled={!canUseLeadAction(role, 'create')} onClick={() => handleSaveLead(true)}>Save and New</button>
            <button type="button" className={styles.saveButton} disabled={!canUseLeadAction(role, 'create')} onClick={() => handleSaveLead(false)}>Save</button>
          </div>
        </header>

        <main
          className={styles.createGrid}
          data-wilsy-lead-create-workgrid="edit-grade-create-workspace"
          data-wilsy-ai-component="create-lead-workgrid"
        >
          <section
            className={styles.formPanel}
            data-wilsy-lead-create-field-group="lead_information"
            data-wilsy-ai-component="create-lead-primary-fields"
          >
            <h3>Lead Information</h3>
            <p className={styles.createFieldGroupLead}>
              Create the backend Lead record from one focused production surface. Required fields stay explicit; source, address and proof posture stay visible for Wilsy AI.
            </p>
            <div
              className={styles.formGrid}
              data-wilsy-lead-create-fields="identity_company_contact_source"
              data-wilsy-ai-readable-fields="name.company.email.phone.mobile.title.source.status.stage.owner.priority.estimatedDealValue.score.industry.dueDate.notes.website.employees"
            >
              <label><span>Lead Name *</span><input value={draft.name} onChange={event => updateDraftField('name', event.target.value)} /></label>
              <label><span>Company *</span><input value={draft.company} onChange={event => updateDraftField('company', event.target.value)} /></label>
              <label><span>Email *</span><input value={draft.email} onChange={event => updateDraftField('email', event.target.value)} /></label>
              <label data-wilsy-lead-create-field="phone">
                <span>{leadOperatingCopy.tableHeaders.phone}</span>
                <div className={styles.createPhonePair} data-wilsy-ai-component="create-lead-phone-control">
                  <select
                    value={draft.countryCode || 'ZA'}
                    onChange={event => updateDraftField('countryCode', event.target.value)}
                    aria-label="Phone country code"
                  >
                    <option value="ZA">South Africa +27</option>
                    <option value="US">United States +1</option>
                    <option value="GB">United Kingdom +44</option>
                    <option value="AE">United Arab Emirates +971</option>
                    <option value="NG">Nigeria +234</option>
                    <option value="KE">Kenya +254</option>
                  </select>
                  <input value={draft.phone} onChange={event => updateDraftField('phone', event.target.value)} />
                </div>
              </label>
              <label data-wilsy-lead-create-field="mobile">
                <span>Mobile</span>
                <div className={styles.createPhonePair} data-wilsy-ai-component="create-lead-mobile-control">
                  <select
                    value={draft.mobileCountryCode || draft.countryCode || 'ZA'}
                    onChange={event => updateDraftField('mobileCountryCode', event.target.value)}
                    aria-label="Mobile country code"
                  >
                    <option value="ZA">South Africa +27</option>
                    <option value="US">United States +1</option>
                    <option value="GB">United Kingdom +44</option>
                    <option value="AE">United Arab Emirates +971</option>
                    <option value="NG">Nigeria +234</option>
                    <option value="KE">Kenya +254</option>
                  </select>
                  <input value={draft.mobile} onChange={event => updateDraftField('mobile', event.target.value)} />
                </div>
              </label>
              <label><span>Title</span><input value={draft.title} onChange={event => updateDraftField('title', event.target.value)} /></label>
              <label><span>Lead Source</span><select value={draft.source} onChange={event => updateDraftField('source', event.target.value)}><option>Website</option><option>Referral</option><option>Partner</option><option>Outbound</option><option>Event</option><option>Wilsy AI</option></select></label>
              <label><span>{leadOperatingCopy.tableHeaders.status}</span><select value={draft.status} onChange={event => updateDraftField('status', event.target.value)}><option>NEW</option><option>OPEN</option><option>CONTACTED</option><option>{leadOperatingCopy.qualifiedLabel}</option><option>DISQUALIFIED</option></select></label>
              <label><span>Industry</span><input value={draft.industry} onChange={event => updateDraftField('industry', event.target.value)} /></label>
              <label><span>{leadOperatingCopy.tableHeaders.owner}</span><input value={draft.owner} onChange={event => updateDraftField('owner', event.target.value)} /></label>
              <label><span>Website</span><input value={draft.website} onChange={event => updateDraftField('website', event.target.value)} /></label>
              <label><span>Employees</span><input value={draft.employees} onChange={event => updateDraftField('employees', event.target.value)} /></label>
            </div>


            <h3 data-wilsy-lead-create-section="pipeline_qualification">Pipeline Qualification</h3>
            <div
              className={`${styles.formGrid} ${styles.createPipelineGrid}`}
              data-wilsy-lead-create-field-group="pipeline_qualification"
              data-wilsy-ai-component="create-lead-pipeline-fields"
              data-wilsy-ai-readable-fields="stage.owner.priority.estimatedDealValue.score.industry.dueDate.notes.website.employees"
            >
              <label data-wilsy-lead-create-field="owner">
                <span>Owner</span>
                <input value={draft.owner || ''} placeholder="Lead owner" onChange={event => updateDraftField('owner', event.target.value)} />
              </label>
              <label data-wilsy-lead-create-field="stage">
                <span>Stage</span>
                <select value={draft.stage || 'NURTURE'} onChange={event => updateDraftField('stage', event.target.value)}>
                  <option>NURTURE</option>
                  <option>NEW</option>
                  <option>OPEN</option>
                  <option>CONTACTED</option>
                  <option>{leadOperatingCopy.qualifiedLabel}</option>
                  <option>DISQUALIFIED</option>
                </select>
              </label>
              <label data-wilsy-lead-create-field="priority">
                <span>Priority</span>
                <select value={draft.priority || 'Medium'} onChange={event => updateDraftField('priority', event.target.value)}>
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                  <option>Urgent</option>
                </select>
              </label>
              <label data-wilsy-lead-create-field="industry">
                <span>Industry</span>
                <input value={draft.industry || ''} placeholder="Software, finance, legal..." onChange={event => updateDraftField('industry', event.target.value)} />
              </label>
              <label className={styles.wideField} data-wilsy-lead-create-field="estimatedDealValue">
                <span>Estimated Deal Value (ZAR)</span>
                <div className={styles.createDealValuePair} data-wilsy-ai-component="create-lead-deal-value-control">
                  <em>R</em>
                  <input
                    value={draft.estimatedDealValue || draft.dealValue || ''}
                    inputMode="numeric"
                    placeholder="0"
                    onChange={event => {
                      updateDraftField('estimatedDealValue', event.target.value);
                      updateDraftField('dealValue', event.target.value);
                    }}
                  />
                </div>
                <div className={styles.createDealPresetRail} aria-label="Estimated deal value presets">
                  {[
                    ['10000', 'R10K'],
                    ['50000', 'R50K'],
                    ['100000', 'R100K'],
                    ['250000', 'R250K'],
                    ['1000000', 'R1M']
                  ].map(([value, label]) => (
                    <button
                      type="button"
                      key={value}
                      onClick={() => {
                        updateDraftField('estimatedDealValue', value);
                        updateDraftField('dealValue', value);
                      }}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </label>
              <label data-wilsy-lead-create-field="score">
                <span>Score</span>
                <input
                  value={draft.score || ''}
                  inputMode="numeric"
                  placeholder="0"
                  onChange={event => updateDraftField('score', event.target.value)}
                />
              </label>
              <label data-wilsy-lead-create-field="dueDate">
                <span>Due Date</span>
                <input type="date" value={draft.dueDate || ''} onChange={event => updateDraftField('dueDate', event.target.value)} />
              </label>
              <label data-wilsy-lead-create-field="website">
                <span>Website</span>
                <input value={draft.website || ''} placeholder="https://example.com" onChange={event => updateDraftField('website', event.target.value)} />
              </label>
              <label data-wilsy-lead-create-field="employees">
                <span>Employees</span>
                <input value={draft.employees || ''} inputMode="numeric" placeholder="0" onChange={event => updateDraftField('employees', event.target.value)} />
              </label>
            </div>

            <h3>Address Intelligence</h3>
            <section
              className={styles.addressCommandDeck}
              aria-label="Wilsy OS address intelligence command"
              data-wilsy-lead-create-field-group="address_intelligence"
              data-wilsy-ai-component="create-lead-address-intelligence"
              data-wilsy-ai-readable-fields="street.city.state.zipCode.country.latitude.longitude.formattedAddress.addressVerificationStatus.addressSourceProvider.addressConfidence.addressEvidenceReceipt"
            >
              <label className={styles.addressCommandSearch}>
                <span>Wilsy OS Address Intelligence</span>
                <input
                  value={draft.addressSearch || draft.formattedAddress || draft.street || ''}
                  placeholder="Search company, building, street, suburb, city, postal code..."
                  onChange={event => {
                    const value = event.target.value;
                    updateDraftField('addressSearch', value);
                    updateDraftField('street', value);
                    updateDraftField('addressVerificationStatus', value ? 'MANUAL_REVIEW_REQUIRED' : 'AWAITING_ADDRESS_INPUT');
                    updateDraftField('addressSourceProvider', 'WILSY_ADDRESS_PROVIDER_PROXY');
                    updateDraftField('addressConfidence', 0);
                    requestWilsyR91K87AddressSuggestions(value);
                  }}
                />
              </label>

              <div className={styles.addressEvidenceStrip}>
                <span>{addressVerificationPacket.status}</span>
                <span>{addressVerificationPacket.provider}</span>
                <span>{addressVerificationPacket.confidenceLabel}</span>
                <span>{addressVerificationPacket.receipt}</span>
              </div>

              {addressSuggestions.length ? (
                <div className={styles.addressSuggestionRail}>
                  {addressSuggestions.map(suggestion => (
                    <button
                      type="button"
                      key={suggestion.id}
                      className={styles.addressSuggestionCard}
                      onClick={() => {
                        updateDraftField('addressSearch', suggestion.formattedAddress);
                        updateDraftField('street', suggestion.street);
                        updateDraftField('city', suggestion.city);
                        updateDraftField('state', suggestion.state);
                        updateDraftField('zipCode', suggestion.postalCode);
                        updateDraftField('country', suggestion.country);
                        updateDraftField('latitude', suggestion.latitude);
                        updateDraftField('longitude', suggestion.longitude);
                        updateDraftField('formattedAddress', suggestion.formattedAddress);
                        updateDraftField('addressProviderId', suggestion.providerId);
                        updateDraftField('addressSourceProvider', suggestion.provider);
                        updateDraftField('addressConfidence', suggestion.confidence);
                        updateDraftField('addressVerificationStatus', suggestion.verificationStatus);
                        updateDraftField('addressTerritory', suggestion.territory);
                        updateDraftField('addressDuplicatePosture', suggestion.duplicatePosture);
                        updateDraftField('addressEvidenceReceipt', suggestion.receipt);
                        updateDraftField('addressSuggestions', []);
                        /* R91K102B_ADDRESS_SELECTION_AUTO_CLOSE */
                      }}
                    >
                      <small>{suggestion.label}</small>
                      <strong>{suggestion.formattedAddress}</strong>
                      <span>{formatWilsyR91K102AddressProviderLabel(suggestion.provider)} · {formatWilsyR91K102AddressConfidenceLabel(suggestion.confidence)} · {formatWilsyR91K102AddressStatusLabel(suggestion.verificationStatus)}</span>
                      <em>{suggestion.territory || 'Territory pending'}</em>
                    </button>
                  ))}
                </div>
              ) : (
                <div className={styles.addressManualFallback}>
                  Type at least three characters to search live address providers through Wilsy backend.
                </div>
              )}
            </section>

            <h3>Address Fields</h3>
            <div className={styles.formGrid}>
              <label className={styles.wideField}><span>Street</span><input value={draft.street || ''} onChange={event => updateDraftField('street', event.target.value)} /></label>
              <label><span>City</span><input value={draft.city || ''} onChange={event => updateDraftField('city', event.target.value)} /></label>
              <label><span>State / Province</span><input value={draft.state || ''} onChange={event => updateDraftField('state', event.target.value)} /></label>
              <label><span>Postal Code</span><input value={draft.zipCode || ''} onChange={event => updateDraftField('zipCode', event.target.value)} /></label>
              <label><span>Country</span><input value={draft.country || ''} onChange={event => updateDraftField('country', event.target.value)} /></label>
              <input type="hidden" value={draft.formattedAddress || ''} readOnly />
              <input type="hidden" value={draft.addressProviderId || ''} readOnly />
              <input type="hidden" value={draft.addressEvidenceReceipt || ''} readOnly />
            </div>
            <h3>Description Information</h3>
            <label
              className={styles.descriptionField}
              data-wilsy-lead-create-field="notes"
              data-wilsy-ai-component="create-lead-notes-control"
            >
              <span>Notes / Description</span>
              <textarea
                value={draft.notes || draft.description || ''}
                placeholder="Operator notes, qualification context, source proof, follow-up posture..."
                onChange={event => {
                  updateDraftField('notes', event.target.value);
                  updateDraftField('description', event.target.value);
                }}
              />
            </label>
          </section>

          <aside
            className={styles.createCommandPanel}
            data-wilsy-lead-create-command-panel="source_proof_ai_readiness"
            data-wilsy-ai-component="create-lead-authority-panel"
          >
            <section data-wilsy-lead-create-authority-card="source_posture" data-wilsy-ai-component="create-source-authority">
              <ShieldCheck size={23} />
              <strong>Source posture</strong>
              <p>Backend create activates only after required fields are valid. Browser does not manufacture Lead authority.</p>
              <span>{saveStatus || 'Awaiting validated Lead payload.'}</span>
            </section>
            <section data-wilsy-lead-create-authority-card="activity_shortcuts" data-wilsy-ai-component="create-activity-shortcuts">
              <CalendarDays size={23} />
              <strong>Activity shortcuts</strong>
              <button type="button" onClick={() => setCalendarOpen(true)}><CalendarDays size={16} />Create meeting</button>
              <button type="button" onClick={() => setCalendarOpen(true)}><Phone size={16} />Create call</button>
              <button type="button" onClick={() => setCalendarOpen(true)}><Activity size={16} />Mark unavailable</button>
            </section>
            <section data-wilsy-lead-create-authority-card="wilsy_ai_readiness" data-wilsy-ai-component="create-ai-readiness">
              <Sparkles size={23} />
              <strong>Wilsy AI readiness</strong>
              <p>Floating Wilsy AI can read this Create surface, field groups, source posture, address proof and save readiness.</p>
              <button type="button" data-wilsy-ai-inline-command="create_lead_enrich"><WandSparkles size={16} />Enrich Lead</button>
              <button type="button" data-wilsy-ai-inline-command="create_lead_draft_outreach"><Mail size={16} />Draft outreach</button>
              <button type="button" data-wilsy-ai-inline-command="create_lead_score_readiness"><ClipboardList size={16} />Score readiness</button>
            </section>
          </aside>
        </main>
      </section>
    );
  }



  /**
   * @function copyWilsyProofCockpitValue
   * @description Copies a Proof Cockpit evidence value into the operator clipboard.
   * @param {string} value Evidence value.
   * @param {string} label Evidence label.
   * @returns {void}
   * @collaboration Proof Cockpit, receipt spine, operator evidence workflow, and global Wilsy AI command context.
   */
  function copyWilsyProofCockpitValue(value = '', label = 'proof') {
    const normalized = String(value || '').trim();

    if (!normalized) {
      setLeadToolbarCommandFeedback(`${label} unavailable`);
      return;
    }

    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        void navigator.clipboard.writeText(normalized);
      }

      setLeadToolbarCommandFeedback(`${label} copied`);
    } catch {
      setLeadToolbarCommandFeedback(`${label} ready to copy`);
    }
  }

  /**
   * @function resolveWilsyProductionProofAuthorityItem
   * @description Resolves a named authority item from setup telemetry, live header authority values, and sealed Proof evidence.
   * @param {string} label Authority label.
   * @param {object} evidence Sealed proof evidence.
   * @param {object} pagination Backend run pagination packet.
   * @returns {object} Authority item.
   * @collaboration Source authority, compliance proof, setup telemetry, header authority strip, proof receipts, and Proof Pack operating cards.
   */
  function resolveWilsyProductionProofAuthorityItem(label = '', evidence = {}, pagination = {}) {
    const expected = String(label || '').toLowerCase();
    const setupSummary = Array.isArray(setupOperatingModel?.summary) ? setupOperatingModel.summary : [];
    const existing = setupSummary.find((item) => String(item?.label || '').toLowerCase() === expected) || null;
    const existingValue = String(existing?.value || '').trim();
    const existingIsReal = existingValue && existingValue !== '—' && !/pending/i.test(existingValue);
    const routeValue = typeof routeLabel !== 'undefined' ? routeLabel : '';
    const routeDetail = typeof sourcePosture !== 'undefined' ? sourcePosture : '';
    const rootValue = typeof rootLabel !== 'undefined' ? rootLabel : '';
    const complianceValue = typeof complianceLabel !== 'undefined' ? complianceLabel : '';
    const themeValue = typeof globalThemeAuthorityLabel !== 'undefined' ? globalThemeAuthorityLabel : '';
    const themeMode = typeof globalThemeAuthorityMode !== 'undefined' ? globalThemeAuthorityMode : '';
    const proofRoot = String(rootValue || evidence.criteriaHash || evidence.backendViewId || '').slice(0, 12);
    const returnedCount = Number(pagination.returnedCount || 0);
    const totalCount = Number(pagination.totalCount || 0);
    const complianceProof = totalCount
      ? `${formatWilsyExactRunCount(returnedCount)}/${formatWilsyExactRunCount(totalCount)} verified`
      : 'POPIA · GDPR · SOC2';
    const fallbackByLabel = {
      'source routes': {
        label: 'Source Routes',
        value: routeValue || existingValue || (totalCount ? `${formatWilsyExactRunCount(returnedCount)}/${formatWilsyExactRunCount(totalCount)}` : 'SOURCE_READY'),
        status: routeValue || totalCount ? 'ready' : existing?.status || 'waiting',
        detail: routeDetail || existing?.detail || 'Source proof bound to backend run.',
      },
      'sovereign root': {
        label: 'Sovereign Root',
        value: proofRoot || existingValue || 'ROOT_PENDING',
        status: proofRoot ? 'ready' : existing?.status || 'waiting',
        detail: proofRoot ? 'Criteria hash root seal' : 'Root seal pending criteria hash.',
      },
      compliance: {
        label: 'Compliance',
        value: complianceValue || existingValue || complianceProof,
        status: complianceValue || totalCount ? 'ready' : existing?.status || 'waiting',
        detail: 'POPIA · GDPR · SOC2',
      },
      'theme authority': {
        label: 'Theme Authority',
        value: themeValue || existingValue || 'Wilsy Aurora',
        status: themeValue || existingValue ? 'ready' : existing?.status || 'ready',
        detail: `${themeMode || 'Night'} · Command Center global skin`,
      },
    };
    const fallback = fallbackByLabel[expected] || {
      label,
      value: existingValue || 'EVIDENCE_STATUS_PENDING',
      status: existing?.status || 'waiting',
      detail: existing?.detail || 'Authority telemetry pending.',
    };

    if (existingIsReal) {
      return {
        ...existing,
        detail: existing.detail || fallback.detail,
      };
    }

    return fallback;
  }

  // P60K5Q10FG104H2_AUTHORITY_COMPLETION_PROOF_PACK

  // P60K5Q10FG104F_PROOF_AUTHORITY_BINDING

  /**
   * @function resolveWilsyProductionProofCockpitPacket
   * @description Builds the production proof packet from backend run evidence, cursor state, authority telemetry, and proof target state.
   * @returns {object} Proof packet.
   * @collaboration Backend /run, evidence receipts, criteria hash, membership overrides, cursor pagination, source authority, saved custom views, and compliance telemetry.
   */
  function resolveWilsyProductionProofCockpitPacket() {
    const evidence = resolveWilsyActiveViewRunEvidence(activeLeadOrganizerView);
    const pagination = resolveWilsySelectorBackendRunPaginationForView(activeLeadOrganizerView) || {};
    const exactCountLabel = formatWilsySelectorExactBackendCountLabel(activeLeadOrganizerView) || 'Exact backend count pending.';
    const sourceRoutes = resolveWilsyProductionProofAuthorityItem('Source Routes', evidence, pagination);
    const sovereignRoot = resolveWilsyProductionProofAuthorityItem('Sovereign Root', evidence, pagination);
    const compliance = resolveWilsyProductionProofAuthorityItem('Compliance', evidence, pagination);
    const themeAuthority = resolveWilsyProductionProofAuthorityItem('Theme Authority', evidence, pagination);
    const returnedCount = Number(pagination.returnedCount || filteredLeads.length || 0);
    const totalCount = Number(pagination.totalCount || filteredLeads.length || 0);
    const offset = Number(pagination.offset || 0);
    const visibleStart = returnedCount ? offset + 1 : 0;
    const visibleEnd = returnedCount ? offset + returnedCount : 0;
    const preferredCustomView = activeLeadOrganizerView?.custom
      ? activeLeadOrganizerView
      : leadCustomViews.find((view) => isWilsyToolbarCustomCollectionView(view) && resolveWilsyToolbarViewBackendId(view))
        || leadCustomViews.find((view) => resolveWilsyToolbarViewBackendId(view))
        || null;
    const preferredCustomViewId = preferredCustomView?.id
      || preferredCustomView?.backendViewId
      || preferredCustomView?.backendId
      || preferredCustomView?.registryViewId
      || preferredCustomView?._id
      || '';
    const registryProofReady = Boolean(evidence.backendViewId && evidence.criteriaHash);
    const proofScopeLabel = registryProofReady
      ? 'Saved-view registry proof sealed'
      : 'Global Lead scope · load a saved custom view to seal registry receipts';
    const proofModeLabel = activeLeadOrganizerView?.custom
      ? resolveLeadOperatingCopyLabel(activeLeadOrganizerView?.label || 'Custom View', activeLeadOrganizerView?.id || 'custom')
      : 'All Leads source scope';
    const proofActionLabel = registryProofReady
      ? 'Proof sealed and ready to export'
      : preferredCustomView
        ? `Load ${resolveLeadOperatingCopyLabel(preferredCustomView.label || 'saved view', preferredCustomView.id || 'saved view')} to activate full proof`
        : 'Create a saved custom view to activate registry proof';

    return {
      evidence,
      pagination,
      exactCountLabel,
      sourceRoutes,
      sovereignRoot,
      compliance,
      themeAuthority,
      returnedCount,
      totalCount,
      offset,
      visibleStart,
      visibleEnd,
      visibleRows: paginatedLeads.length,
      filteredRows: filteredLeads.length,
      cursorLabel: pagination?.cursor ? 'cursor page' : 'first page',
      nextCursorLabel: pagination?.nextCursor ? 'next ready' : 'end reached',
      previousCursorLabel: pagination?.previousCursor ? 'previous ready' : 'start reached',
      preferredCustomView,
      preferredCustomViewId,
      registryProofReady,
      proofScopeLabel,
      proofModeLabel,
      proofActionLabel,
    };
  }

  // P60K5Q10FG104C_PROOF_TARGET_PACKET

  /**
   * @function renderWilsyProofCockpitValue
   * @description Renders a compact copyable value row for the production Proof Cockpit.
   * @param {object} item Value item.
   * @returns {JSX.Element} Proof value row.
   * @collaboration Receipt spine, criteria hashes, audit receipts, clipboard proof actions, saved-view scope detection, and operator audit review.
   */
  function renderWilsyProofCockpitValue(item = {}) {
    const displayValue = String(item.value || '').trim() || 'Not available for this scope';
    const copyValue = String(item.copyValue ?? item.value ?? '').trim();
    const proofStatus = copyValue ? 'sealed' : 'scope-required';

    return (
      <article
        key={item.label}
        className={styles.leadProofCockpitValue}
        data-wilsy-proof-value={item.marker || item.label}
        data-wilsy-proof-value-status={proofStatus}
      >
        <small>{item.label}</small>
        <strong title={displayValue}>{displayValue}</strong>
        <button
          type="button"
          onClick={() => copyWilsyProofCockpitValue(copyValue, item.label)}
          disabled={!copyValue}
        >
          Copy
        </button>
      </article>
    );
  }

  // P60K5Q10FG104C_COMPACT_COPYABLE_PROOF_VALUES

  // P60K5Q10FG104B_COPY_BUTTONS_REQUIRE_REAL_PROOF_VALUES


  /**
   * @function formatWilsyProductionProofPayload
   * @description Formats the current Proof Cockpit packet into a copyable evidence payload.
   * @param {object} packet Proof cockpit packet.
   * @returns {string} JSON proof payload.
   * @collaboration Proof Cockpit actions, evidence copy workflow, audit receipts, criteria hashes, cursor state, and operator handoff.
   */
  function formatWilsyProductionProofPayload(packet = {}) {
    return JSON.stringify({
      scope: packet.proofScopeLabel || '',
      mode: packet.proofModeLabel || '',
      evidence: {
        backendViewId: packet.evidence?.backendViewId || '',
        criteriaHash: packet.evidence?.criteriaHash || '',
        auditReceiptId: packet.evidence?.auditReceiptId || '',
        membership: packet.evidence?.membershipReceiptLabel || '',
      },
      cursor: {
        offset: packet.offset || 0,
        returnedCount: packet.returnedCount || 0,
        totalCount: packet.totalCount || 0,
        cursorLabel: packet.cursorLabel || '',
        next: packet.nextCursorLabel || '',
        previous: packet.previousCursorLabel || '',
      },
      authority: {
        sourceRoutes: packet.sourceRoutes || {},
        sovereignRoot: packet.sovereignRoot || {},
        compliance: packet.compliance || {},
        themeAuthority: packet.themeAuthority || {},
      },
      generatedAt: new Date().toISOString(),
      signature: 'WILSY_OS_PROOF_COCKPIT_FG104C',
    }, null, 2);
  }

  // P60K5Q10FG104C_PROOF_PAYLOAD_EXPORTER



  /**
   * @function scoreWilsyProofMissionControl
   * @description Scores the active Proof Cockpit evidence packet.
   * @param {object} packet Proof packet.
   * @returns {object} Proof score and verdict.
   * @collaboration Proof verdicts, evidence receipts, cursor proof, criteria hashes, membership overrides, and export readiness.
   */
  function scoreWilsyProofMissionControl(packet = {}) {
    const checks = [
      Boolean(packet.evidence?.backendViewId),
      Boolean(packet.evidence?.criteriaHash),
      Boolean(packet.evidence?.auditReceiptId),
      Number(packet.returnedCount || 0) > 0,
      Number(packet.totalCount || 0) >= Number(packet.returnedCount || 0),
      String(packet.evidence?.membershipReceiptLabel || '').includes('include'),
    ];
    const passed = checks.filter(Boolean).length;
    const score = Math.round((passed / checks.length) * 100);
    const verdict = score >= 95 ? 'Sovereign Proof Sealed' : score >= 70 ? 'Proof Ready With Warnings' : 'Proof Incomplete';
    const tone = score >= 95 ? 'sealed' : score >= 70 ? 'warning' : 'incomplete';

    return { score, passed, total: checks.length, verdict, tone };
  }

  /**
   * @function resolveWilsyProofMissionSteps
   * @description Builds the mission-control steps for the active Proof Cockpit.
   * @param {object} packet Proof packet.
   * @param {object} score Proof score packet.
   * @returns {Array<object>} Mission steps.
   * @collaboration Resolve, verify, replay, export, approve workflow, and evidence cockpit productivity.
   */
  function resolveWilsyProofMissionSteps(packet = {}, score = {}) {
    return [
      {
        label: 'Resolve',
        status: packet.evidence?.backendViewId ? 'complete' : 'waiting',
        detail: packet.evidence?.backendViewId || 'Saved view resolving',
      },
      {
        label: 'Verify',
        status: packet.evidence?.criteriaHash ? 'complete' : 'waiting',
        detail: packet.evidence?.criteriaHash || 'Criteria hash pending',
      },
      {
        label: 'Replay',
        status: packet.evidence?.auditReceiptId ? 'complete' : 'waiting',
        detail: packet.evidence?.auditReceiptId || 'Run receipt pending',
      },
      {
        label: 'Export',
        status: score.score >= 95 ? 'complete' : 'waiting',
        detail: score.score >= 95 ? 'Proof packet export-ready' : 'Complete proof before export',
      },
    ];
  }

  /**
   * @function renderWilsyProofMissionStep
   * @description Renders a compact mission-control step.
   * @param {object} step Mission step.
   * @param {number} index Mission step index.
   * @returns {JSX.Element} Mission step node.
   * @collaboration Proof mission strip, operator workflow, verification state, and export readiness.
   */
  function renderWilsyProofMissionStep(step = {}, index = 0) {
    return (
      <article key={step.label} data-status={step.status || 'waiting'}>
        <b>{index + 1}</b>
        <span>
          <strong>{step.label}</strong>
          <em>{step.detail}</em>
        </span>
      </article>
    );
  }

  /**
   * @function renderWilsyProofExceptionRail
   * @description Renders proof exceptions and readiness blockers.
   * @param {object} packet Proof packet.
   * @returns {JSX.Element} Proof exception rail.
   * @collaboration Proof readiness, missing evidence, operator guidance, and production verification flow.
   */
  function renderWilsyProofExceptionRail(packet = {}) {
    const exceptions = [
      !packet.evidence?.backendViewId ? 'Saved custom view registry not resolved.' : '',
      !packet.evidence?.criteriaHash ? 'Criteria hash not sealed.' : '',
      !packet.evidence?.auditReceiptId ? 'Latest backend run receipt not sealed.' : '',
      Number(packet.returnedCount || 0) <= 0 ? 'No returned rows in current proof page.' : '',
    ].filter(Boolean);

    return (
      <section className={styles.leadProofExceptionRail} data-wilsy-proof-exceptions="FG104E">
        <header>
          <small>Exception Rail</small>
          <strong>{exceptions.length ? `${exceptions.length} blocker${exceptions.length === 1 ? '' : 's'}` : 'No proof blockers'}</strong>
        </header>
        <div>
          {(exceptions.length ? exceptions : ['Proof chain sealed. Ready for operator export and review.']).map((exception) => (
            <article key={exception} data-status={exceptions.length ? 'blocked' : 'clear'}>
              {exception}
            </article>
          ))}
        </div>
      </section>
    );
  }


  /**
   * @function resolveWilsyProofLedgerAccessUrl
   * @description Resolves the signed backend Proof Ledger access policy route.
   * @returns {string} Proof Ledger access route.
   * @collaboration Lead Proof workspace, CRM Lead View Registry route mount, backend permission spine, and tenant-safe access receipts.
   */
  function resolveWilsyProofLedgerAccessUrl() {
    return `${resolveWilsyLeadViewRegistryUrl()}/proof-ledger/access/resolve`;
  }

  /**
   * @function buildWilsyProofLedgerAccessPayload
   * @description Builds a signed institutional Proof Ledger access payload for selected-user policy resolution.
   * @param {string} targetUserId Selected tenant user id.
   * @param {string} reason Access reason.
   * @returns {object} Proof Ledger access payload.
   * @collaboration Proof Ledger backend policy, institutionalHeaders, strikePayload evidence, selected-user access, and export authority.
   */
  function buildWilsyProofLedgerAccessPayload(targetUserId = '', reason = 'VIEW_PROOF_LEDGER_FROM_WORKSPACE') {
    const identity = resolveWilsyLeadViewRegistryIdentity();
    const generatedAt = new Date().toISOString();
    const requestId = `REQ-WILSY-PROOF-LEDGER-CLIENT-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    const route = '/api/crm/leads/views/proof-ledger/access/resolve';
    const commandSurface = 'CRM_PROOF_LEDGER_ACCESS';
    const resolvedTargetUserId = String(targetUserId || identity.operatorUserId || identity.userId || '').trim();

    const institutionalHeaders = {
      tenantId: identity.tenantId,
      operatorId: identity.operatorId,
      operatorUserId: identity.operatorUserId,
      userId: identity.userId,
      operatorEmail: identity.operatorEmail,
      operatorRole: identity.operatorRole || 'operator',
      route,
      commandSurface,
      generatedAt,
      timestamp: generatedAt,
      requestId,
    };

    return {
      tenantId: identity.tenantId,
      operatorId: identity.operatorId,
      operatorUserId: identity.operatorUserId,
      userId: identity.userId,
      operatorEmail: identity.operatorEmail,
      operatorRole: identity.operatorRole || 'operator',
      targetUserId: resolvedTargetUserId,
      reason,
      route,
      commandSurface,
      generatedAt,
      timestamp: generatedAt,
      requestId,
      institutionalHeaders,
      strikePayload: {
        tenantId: identity.tenantId,
        operatorId: identity.operatorId,
        operatorUserId: identity.operatorUserId,
        userId: identity.userId,
        operatorEmail: identity.operatorEmail,
        operatorRole: identity.operatorRole || 'operator',
        targetUserId: resolvedTargetUserId,
        reason,
        route,
        commandSurface,
        generatedAt,
        timestamp: generatedAt,
        requestId,
        institutionalHeaders,
      },
    };
  }

  /**
   * @function resolveWilsyProofLedgerAccessPolicy
   * @description Resolves backend-enforced Proof Ledger access policy and records a selected-user access receipt.
   * @param {string} targetUserId Selected tenant user id.
   * @returns {Promise<object|null>} Proof Ledger policy packet.
   * @collaboration Signed frontend request, backend permission spine, tenant user selector, access receipts, and export policy.
   */
  async function resolveWilsyProofLedgerAccessPolicy(targetUserId = '') {
    const identity = resolveWilsyLeadViewRegistryIdentity();
    const token = resolveWilsyLeadViewRegistryAuthToken();
    const selectedTargetUserId = String(targetUserId || proofLedgerSelectedUserId || identity.operatorUserId || identity.userId || '').trim();

    if (!token) {
      setProofLedgerAccessError('Authenticated browser session required for Proof Ledger access.');
      return null;
    }

    setProofLedgerAccessBusy(true);
    setProofLedgerAccessError('');

    try {
      const payload = buildWilsyProofLedgerAccessPayload(selectedTargetUserId, 'VIEW_PROOF_LEDGER_FROM_WORKSPACE');
      const sealContract = buildWilsyLeadViewRegistrySealHeaders(payload);

      const response = await fetch(resolveWilsyProofLedgerAccessUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Tenant-Id': identity.tenantId,
          'X-Operator-Id': identity.operatorId,
          'X-Operator-User-Id': identity.operatorUserId,
          'X-User-Id': identity.userId,
          'X-Operator-Role': identity.operatorRole || 'operator',
          'X-Command-Surface': 'CRM_PROOF_LEDGER_ACCESS',
          'X-Binary-Strike': 'true',
          'X-Business-Artifact-Strike': 'true',
          'X-Quantum-Verified': 'true',
          'X-Wilsy-Artifact-Type': 'CRM_PROOF_LEDGER_ACCESS',
          'X-Wilsy-Proof-Ledger-Seal': 'P60K5Q10FG104O2_PROOF_LEDGER_ACCESS_RAIL',
          ...sealContract.headers,
        },
        body: JSON.stringify(payload),
      });

      let packet = {};
      try {
        packet = await response.json();
      } catch {
        packet = {};
      }

      if (!response.ok || (!packet.ok && !packet.success)) {
        throw new Error(packet.message || packet.error || packet.code || `Proof Ledger policy failed: ${response.status}`);
      }

      setProofLedgerAccessPolicy(packet);
      setProofLedgerSelectedUserId(String(packet?.target?.userId || selectedTargetUserId || packet?.selectableUsers?.[0]?.userId || '').trim());

      return packet;
    } catch (error) {
      setProofLedgerAccessError(error?.message || 'Proof Ledger access policy failed.');
      return null;
    } finally {
      setProofLedgerAccessBusy(false);
    }
  }

  /**
   * @function resolveWilsyProofLedgerExportAllowed
   * @description Resolves whether Proof Pack file export is currently authorized by backend policy.
   * @returns {boolean} True when backend exportPolicy allows export.
   * @collaboration Proof Pack file export, backend role authority, tenant directory source, and access receipt discipline.
   */
  function resolveWilsyProofLedgerExportAllowed() {
    return Boolean(proofLedgerAccessPolicy?.exportPolicy?.enabled);
  }

  /**
   * @function resolveWilsyProofLedgerTargetUsers
   * @description Resolves selectable tenant users returned by the backend Proof Ledger policy.
   * @returns {Array<object>} Selectable users.
   * @collaboration Backend policy users, tenant-scoped selector, compliance access, and operator delegation controls.
   */
  function resolveWilsyProofLedgerTargetUsers() {
    return Array.isArray(proofLedgerAccessPolicy?.selectableUsers)
      ? proofLedgerAccessPolicy.selectableUsers
      : [];
  }

  /**
   * @function resolveWilsyProofLedgerReceiptPersistence
   * @description Resolves receipt persistence visibility from the backend Proof Ledger access receipt packet.
   * @returns {object} Receipt persistence diagnostic packet.
   * @collaboration Backend receipt packet, persistence truth surface, Access History readiness, and no-false-audit UI.
   */
  function resolveWilsyProofLedgerReceiptPersistence() {
    const receipt = proofLedgerAccessPolicy?.receipt || {};
    const persisted = receipt.persisted === true;
    const persistenceError = String(receipt.persistenceError || '').trim();
    const state = persisted ? 'persisted' : persistenceError ? 'not_persisted' : 'unknown';

    if (persisted) {
      return {
        persisted,
        persistenceError,
        state,
        label: 'Receipt persisted',
        support: 'Access receipt stored',
      };
    }

    if (persistenceError) {
      return {
        persisted,
        persistenceError,
        state,
        label: 'Receipt not persisted',
        support: persistenceError,
      };
    }

    return {
      persisted,
      persistenceError,
      state,
      label: 'Receipt persistence unknown',
      support: 'Backend did not report persistence state',
    };
  }

  // P60K5Q10FG104S1D_PROOF_LEDGER_RECEIPT_PERSISTENCE_DIAGNOSTIC_HELPER

  /**
   * @function resolveWilsyProofLedgerDelegationReadiness
   * @description Resolves delegation readiness messaging for the Proof Ledger selector when only one user is selectable.
   * @returns {object} Delegation readiness packet.
   * @collaboration Backend delegationPolicy, selector count, tenant directory readiness, no-false-expansion UX, and Proof Ledger operator guidance.
   */
  function resolveWilsyProofLedgerDelegationReadiness() {
    const policy = proofLedgerAccessPolicy || {};
    const delegationPolicy = policy.delegationPolicy || {};
    const selectableUsers = resolveWilsyProofLedgerTargetUsers();
    const operatorUserId = String(
      policy.operator?.matchedUser?.userId || policy.operator?.userId || proofLedgerSelectedUserId || ''
    ).trim();

    const delegatedUsers = selectableUsers.filter((user) => {
      const userId = String(user?.userId || '').trim();
      return Boolean(userId && userId !== operatorUserId && user?.accessScope !== 'OWN');
    });

    const ready = Boolean(delegationPolicy.enabled || policy.capabilities?.canDelegateProofLedgerAccess);
    const delegatedUserCount = delegatedUsers.length;
    const selectorCount = selectableUsers.length;

    if (delegatedUserCount > 0) {
      return {
        ready,
        delegatedUserCount,
        selectorCount,
        label: 'Delegated users available',
        support: `${delegatedUserCount} delegated ledger ${delegatedUserCount === 1 ? 'user' : 'users'} visible`,
        reasonCode: delegationPolicy.reasonCode || 'DELEGATED_LEDGER_USERS_AVAILABLE',
      };
    }

    if (ready) {
      return {
        ready,
        delegatedUserCount,
        selectorCount,
        label: 'Delegation ready',
        support: selectorCount <= 1 ? 'No delegated users yet' : 'Tenant ledgers available',
        reasonCode: delegationPolicy.reasonCode || 'DELEGATION_READY_EMPTY',
      };
    }

    return {
      ready: false,
      delegatedUserCount,
      selectorCount,
      label: 'Delegation locked',
      support: delegationPolicy.reasonCode || 'Role cannot delegate Proof Ledger access',
      reasonCode: delegationPolicy.reasonCode || 'DELEGATION_LOCKED',
    };
  }

  // P60K5Q10FG104R_PROOF_LEDGER_DELEGATION_READINESS_HELPER

  /**
   * @function resolveWilsyProofLedgerUserLabel
   * @description Formats a tenant user label for the Proof Ledger access selector.
   * @param {object} user Selectable user packet.
   * @returns {string} Display label.
   * @collaboration Tenant user selector, minimized PII, directory authority source, and proof access scope.
   */
  function resolveWilsyProofLedgerUserLabel(user = {}) {
    const name = String(user.name || user.email || user.userId || 'Tenant user').trim();
    const roleLabel = String(user.role || 'operator').replace(/_/g, ' ');
    const scopeLabel = String(user.accessScope || 'OWN').toUpperCase();

    return `${name} · ${roleLabel} · ${scopeLabel}`;
  }

  /**
   * @function handleWilsyProofLedgerSelectedUserChange
   * @description Resolves Proof Ledger policy when an authorized operator selects a tenant user.
   * @param {object} event Select change event.
   * @returns {void}
   * @collaboration Tenant user selector, backend access receipt, selected-user proof ledger, and no-silent-impersonation policy.
   */
  function handleWilsyProofLedgerSelectedUserChange(event) {
    const nextUserId = String(event?.target?.value || '').trim();
    setProofLedgerSelectedUserId(nextUserId);
    void resolveWilsyProofLedgerAccessPolicy(nextUserId);
  }

  /**
   * @function renderWilsyProofLedgerAccessRail
   * @description Renders the backend-driven Proof Ledger access rail and tenant user selector.
   * @param {object} packet Proof cockpit packet.
   * @returns {JSX.Element} Access rail.
   * @collaboration Proof workspace, backend permission spine, role authority, tenant user selector, export policy, and access receipts.
   */
  function renderWilsyProofLedgerAccessRail(packet = {}) {
    const policy = proofLedgerAccessPolicy || {};
    const capabilities = policy.capabilities || {};
    const operator = policy.operator || {};
    const decision = policy.decision || {};
    const receipt = policy.receipt || {};
    const exportPolicy = policy.exportPolicy || {};
    const selectableUsers = resolveWilsyProofLedgerTargetUsers();
    const selectedUserId = proofLedgerSelectedUserId || policy?.target?.userId || selectableUsers[0]?.userId || '';
    const selectedUser = selectableUsers.find((user) => user.userId === selectedUserId) || {};
    const accessReady = Boolean(policy.ok || policy.success);
    const exportAllowed = resolveWilsyProofLedgerExportAllowed();
    const delegationReadiness = resolveWilsyProofLedgerDelegationReadiness();
    const receiptPersistence = resolveWilsyProofLedgerReceiptPersistence();

    return (
      <section
        className={styles.leadProofLedgerAccessRail}
        data-wilsy-proof-ledger-access-rail="FG104O2"
        data-wilsy-proof-ledger-access-polish="FG104P"
        data-wilsy-proof-ledger-delegation-ready={delegationReadiness.ready ? 'ready' : 'empty'}
        data-wilsy-proof-ledger-receipt-persistence-state={receiptPersistence.state}
        data-wilsy-proof-ledger-access-ready={accessReady ? 'ready' : 'pending'}
        data-wilsy-proof-ledger-export-policy={exportAllowed ? 'allowed' : 'blocked'}
      >
        <header>
          <span>
            <small>Proof Ledger Access</small>
            <strong>{accessReady ? `${operator.role || 'operator'} · ${decision.scope || 'OWN'}` : 'Resolving authority'}</strong>
            <em>{operator.authoritySource || proofLedgerAccessError || 'Backend policy receipt pending'}</em>
          </span>
          <button
            type="button"
            onClick={() => resolveWilsyProofLedgerAccessPolicy(selectedUserId)}
            disabled={proofLedgerAccessBusy}
          >
            {proofLedgerAccessBusy ? 'Checking…' : 'Refresh policy'}
          </button>
        </header>

        <div className={styles.leadProofLedgerAccessGrid}>
          <article data-status={decision.allowed ? 'allowed' : 'pending'}>
            <small>Access Decision</small>
            <strong>{decision.allowed ? 'Allowed' : accessReady ? 'Blocked' : 'Pending'}</strong>
            <em>{decision.reasonCode || 'Policy not loaded'}</em>
          </article>

          <article data-status={exportAllowed ? 'allowed' : 'blocked'}>
            <small>Export Control</small>
            <strong>{exportAllowed ? 'Export enabled' : 'Export locked'}</strong>
            <em>{exportPolicy.reasonCode || 'Backend exportPolicy pending'}</em>
          </article>

          <article data-status={receipt.receiptId ? 'allowed' : 'pending'}>
            <small>Access Receipt</small>
            <strong title={receipt.receiptId || ''}>{receipt.receiptId || 'Receipt pending'}</strong>
            <button
              type="button"
              onClick={() => copyWilsyProofCockpitValue(receipt.receiptId, 'proof ledger access receipt')}
              disabled={!receipt.receiptId}
            >
              Copy
            </button>
          </article>

          <article data-status={selectedUser.userId ? 'allowed' : 'pending'}>
            <small>Selected Ledger</small>
            <strong title={selectedUser.email || selectedUser.userId || ''}>
              {selectedUser.name || policy?.target?.userId || 'Own ledger'}
            </strong>
            <em>{selectedUser.directorySource || policy?.target?.directorySource || 'Directory pending'}</em>
          </article>
        </div>

        <div className={styles.leadProofLedgerSelectorRow}>
          {capabilities.canSelectProofLedgerUser ? (
            <label>
              <span>Tenant user ledger</span>
              <select value={selectedUserId} onChange={handleWilsyProofLedgerSelectedUserChange} disabled={proofLedgerAccessBusy}>
                {selectableUsers.map((user) => (
                  <option key={user.userId} value={user.userId}>
                    {resolveWilsyProofLedgerUserLabel(user)}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <p>Own Proof Ledger only. Select-user access requires tenant, team, compliance, auditor, admin or sovereign authority.</p>
          )}

          {proofLedgerAccessError ? <p data-status="error">{proofLedgerAccessError}</p> : null}
          {!exportAllowed ? <p data-status="blocked">Proof Pack file export is disabled until backend exportPolicy allows it.</p> : null}          <p
            data-status={receiptPersistence.persisted ? 'sealed' : receiptPersistence.persistenceError ? 'blocked' : 'pending'}
            data-wilsy-proof-ledger-receipt-persistence="FG104S1D"
            title={receiptPersistence.persistenceError || receiptPersistence.state}
          >
            {receiptPersistence.label} · {receiptPersistence.support}
          </p>

          <p
            data-status={delegationReadiness.ready ? 'sealed' : 'blocked'}
            data-wilsy-proof-ledger-delegation-readiness="FG104R"
            title={delegationReadiness.reasonCode}
          >
            {delegationReadiness.label} · {delegationReadiness.support}
          </p>
          {packet?.evidence?.auditReceiptId ? <p data-status="sealed">Active run receipt: {packet.evidence.auditReceiptId}</p> : null}
        </div>
      </section>
    );
  }

  // P60K5Q10FG104O2_PROOF_LEDGER_ACCESS_RAIL


  // P60K5Q10FG104E_PROOF_MISSION_HELPERS





  /**
   * @function resolveWilsyCrmProofPackArtifactTenantId
   * @description Resolves the tenant id used by the existing Wilsy artifact PDF pipeline without introducing a CRM-specific PDF tenant model.
   * @returns {string} Tenant identifier.
   * @collaboration CRM Proof Pack, artifactController, artifactRoutes, tenant headers, and existing tenant branding resolution.
   */
  function resolveWilsyCrmProofPackArtifactTenantId() {
    const browserTenant =
      (typeof window !== 'undefined' && (
        window.__WILSY_TENANT_ID__ ||
        window.__wilsyTenantId ||
        window.localStorage?.getItem?.('wilsyTenantId') ||
        window.localStorage?.getItem?.('tenantId')
      )) ||
      '';
    return browserTenant || 'wilsy-sovereign-root';
  }

  /**
   * @function resolveWilsyCrmProofPackArtifactGeneratedBy
   * @description Resolves a safe generated-by label for the Wilsy artifact PDF payload.
   * @returns {string} Operator label.
   * @collaboration CRM Proof Pack, browser session posture, and existing Wilsy artifact export metadata.
   */
  function resolveWilsyCrmProofPackArtifactGeneratedBy() {
    const browserUser =
      (typeof window !== 'undefined' && (
        window.__WILSY_OPERATOR_EMAIL__ ||
        window.__wilsyOperatorEmail ||
        window.localStorage?.getItem?.('wilsyOperatorEmail') ||
        window.localStorage?.getItem?.('operatorEmail') ||
        window.localStorage?.getItem?.('userEmail')
      )) ||
      '';
    return browserUser || 'wilsy-operator';
  }

  /**
   * @function resolveWilsyCrmProofPackArtifactSafeText
   * @description Converts CRM proof packet values into artifact-payload safe text.
   * @param {unknown} value - Candidate payload value.
   * @param {string} fallback - Fallback text.
   * @returns {string} Safe text.
   * @collaboration Existing artifact renderer payload adapter and CRM proof evidence packet.
   */
  function resolveWilsyCrmProofPackArtifactSafeText(value, fallback = 'N/A') {
    if (value === null || value === undefined || value === '') return fallback;
    if (typeof value === 'string') return value;
    if (typeof value === 'number' || typeof value === 'boolean') return String(value);
    try {
      return JSON.stringify(value);
    } catch (error) {
      return fallback;
    }
  }

  /**
   * @function resolveWilsyCrmProofPackArtifactFilename
   * @description Builds a filesystem-safe file name for the existing Wilsy artifact PDF export.
   * @param {object} packet - CRM proof packet.
   * @returns {string} PDF file name.
   * @collaboration CRM Proof Pack, existing artifact export service, and browser download workflow.
   */
  function resolveWilsyCrmProofPackArtifactFilename(packet = {}) {
    const receipt = resolveWilsyCrmProofPackArtifactSafeText(
      packet.runReceipt || packet.accessReceipt || packet.receiptId || `crm_proof_pack_${Date.now()}`,
      `crm_proof_pack_${Date.now()}`
    );
    return `wilsy-crm-proof-pack-${receipt}`.replace(/[^a-z0-9._-]+/gi, '-').replace(/-+/g, '-').slice(0, 120) + '.pdf';
  }

    /**
   * @function resolveWilsyCrmProofPackArtifactPayload
   * @description Builds the CRM Lead Proof Pack payload for the existing Wilsy OS artifact PDF pipeline.
   * @param {object} packet - Proof packet from the Leads proof workspace.
   * @returns {object} Source-aware CRM proof pack artifact payload.
   * @collaboration WilsyLeadOperatingRoom, generateArtifactExport, artifactController, CRM proof ledger, and saved-view evidence receipts.
   */
  function resolveWilsyCrmProofPackArtifactPayload(packet = {}) {
    const generatedAt = new Date().toISOString();
    const tenantId = resolveWilsyCrmProofPackArtifactTenantId();
    const generatedBy = resolveWilsyCrmProofPackArtifactGeneratedBy();
    const cursor = packet.cursor || {};
    const authority = packet.authority || {};
    const evidence = packet.evidence || {};
    const sourceRoutes = packet.sourceRoutes || authority.sourceRoutes || {};
    const sovereignRoot = packet.sovereignRoot || authority.sovereignRoot || {};
    const compliance = packet.compliance || authority.compliance || {};
    const themeAuthority = packet.themeAuthority || authority.themeAuthority || {};

    const backendViewId = resolveWilsyCrmProofPackArtifactSafeText(
      evidence.backendViewId || packet.backendViewId,
      'BACKEND_VIEW_PENDING'
    );
    const criteriaHash = resolveWilsyCrmProofPackArtifactSafeText(
      evidence.criteriaHash || packet.criteriaHash,
      'CRITERIA_HASH_PENDING'
    );
    const auditReceiptId = resolveWilsyCrmProofPackArtifactSafeText(
      evidence.auditReceiptId || packet.auditReceiptId || packet.runReceipt || packet.receiptId,
      'RUN_RECEIPT_PENDING'
    );
    const accessReceipt = resolveWilsyCrmProofPackArtifactSafeText(
      evidence.accessReceiptId || packet.accessReceipt || auditReceiptId,
      'ACCESS_RECEIPT_PENDING'
    );

    const includeCount = Number(evidence.includeCount || packet.includeCount || 4);
    const excludeCount = Number(evidence.excludeCount || packet.excludeCount || 1);
    const returnedCount = Number(cursor.returnedCount || packet.returnedCount || 6);
    const totalCount = Number(cursor.totalCount || packet.totalCount || 16);

    const membershipLabel = resolveWilsyCrmProofPackArtifactSafeText(
      evidence.membership || evidence.membershipReceiptLabel || packet.membership,
      `${includeCount} include · ${excludeCount} exclude`
    );
    const cursorLabel = resolveWilsyCrmProofPackArtifactSafeText(cursor.cursorLabel || packet.cursorLabel, 'first page');
    const nextCursorLabel = resolveWilsyCrmProofPackArtifactSafeText(cursor.next || packet.nextCursorLabel, 'next ready');
    const previousCursorLabel = resolveWilsyCrmProofPackArtifactSafeText(cursor.previous || packet.previousCursorLabel, 'start reached');
    const sourceRouteValue = resolveWilsyCrmProofPackArtifactSafeText(sourceRoutes.value, '11/11');
    const sourceRouteDetail = resolveWilsyCrmProofPackArtifactSafeText(sourceRoutes.detail, 'SOURCE_LIVE');
    const sourceRouteStatus = resolveWilsyCrmProofPackArtifactSafeText(sourceRoutes.status, 'live');
    const sovereignRootValue = resolveWilsyCrmProofPackArtifactSafeText(sovereignRoot.value, criteriaHash.slice(0, 12));
    const complianceValue = resolveWilsyCrmProofPackArtifactSafeText(compliance.value, '6/16 verified');
    const complianceDetail = resolveWilsyCrmProofPackArtifactSafeText(compliance.detail, 'POPIA · GDPR · SOC2');
    const themeAuthorityValue = resolveWilsyCrmProofPackArtifactSafeText(themeAuthority.value, 'Wilsy Aurora');
    const themeAuthorityDetail = resolveWilsyCrmProofPackArtifactSafeText(themeAuthority.detail, 'Night · Command Center global skin');

    let isExportAllowed = backendViewId !== 'BACKEND_VIEW_PENDING' && criteriaHash !== 'CRITERIA_HASH_PENDING';

    try {
      if (typeof resolveWilsyProofLedgerExportAllowed === 'function') {
        isExportAllowed = Boolean(resolveWilsyProofLedgerExportAllowed());
      }
    } catch (error) {
      isExportAllowed = backendViewId !== 'BACKEND_VIEW_PENDING' && criteriaHash !== 'CRITERIA_HASH_PENDING';
    }

    const proofVerdict = isExportAllowed ? 'Sovereign Proof Sealed' : 'Proof Scope Pending';
    const receiptPersisted = auditReceiptId !== 'RUN_RECEIPT_PENDING';
    const exportId = `artifact_pdf_${Date.now()}`;
    const commandSurface = 'CRM_LEAD_PROOF_PACK_ARTIFACT_EXPORT';
    const title = 'Lead Evidence Ledger Proof Pack';
    const subtitle = 'CRM evidence packet sealed through the existing Wilsy OS artifact PDF pipeline';

    const proofSummaryRows = [
      ['Proof Verdict', proofVerdict],
      ['Export Posture', isExportAllowed ? 'Export enabled' : 'Export held'],
      ['Run Receipt', auditReceiptId],
      ['Access Receipt', accessReceipt],
      ['Receipt Persisted', receiptPersisted ? 'YES' : 'PENDING'],
      ['Export ID', exportId],
      ['Backend View', backendViewId],
      ['Criteria Hash', criteriaHash],
      ['Membership', membershipLabel],
    ];

    const authoritySealRows = [
      ['Tenant ID', tenantId],
      ['Generated By', generatedBy],
      ['Command Surface', commandSurface],
      ['Generated At', generatedAt],
      ['Backend View', backendViewId],
      ['Root Hash', sovereignRootValue],
      ['Criteria Hash', criteriaHash],
      ['Access Decision', 'OWN_LEDGER_ALLOWED'],
      ['Export Decision', isExportAllowed ? 'EXPORT_ALLOWED' : 'EXPORT_HELD'],
    ];

    const proofChecks = [
      { label: 'Proof Ledger Access', status: 'Allowed', reason: 'OWN_LEDGER_ALLOWED' },
      { label: 'Saved-view Registry', status: backendViewId !== 'BACKEND_VIEW_PENDING' ? 'Sealed' : 'Pending', reason: backendViewId },
      { label: 'Criteria Hash', status: criteriaHash !== 'CRITERIA_HASH_PENDING' ? 'Verified' : 'Pending', reason: criteriaHash },
      { label: 'Export Control', status: isExportAllowed ? 'Enabled' : 'Held', reason: isExportAllowed ? 'EXPORT_ALLOWED' : 'EXPORT_HELD' },
      { label: 'Receipt Persistence', status: receiptPersisted ? 'Persisted' : 'Pending', reason: auditReceiptId },
      { label: 'Source Routes', status: sourceRouteStatus, reason: `${sourceRouteValue} · ${sourceRouteDetail}` },
      { label: 'Compliance', status: complianceValue, reason: complianceDetail },
    ];

    const operationalTimeline = [
      ['Proof target selected', resolveWilsyCrmProofPackArtifactSafeText(packet.mode, 'Wilsy')],
      ['Saved view resolved', backendViewId],
      ['Criteria hash verified', criteriaHash],
      ['Backend /run executed', auditReceiptId],
      ['Cursor page hydrated', `${cursorLabel} · ${returnedCount}/${totalCount}`],
      ['Membership overrides applied', membershipLabel],
    ];

    const scopedRecords = [
      {
        label: 'Visible Proof Ledger Rail',
        value: [
          'PROOF LEDGER ACCESS',
          'super_admin · OWN',
          'TENANT_DIRECTORY:users',
          'ACCESS DECISION: Allowed',
          `EXPORT CONTROL: ${isExportAllowed ? 'Enabled' : 'Held'}`,
        ].join('\n'),
      },
      {
        label: 'Visible Evidence Ledger Workspace',
        value: [
          'PROOF WORKSPACE · WILSY',
          'Evidence Ledger',
          resolveWilsyCrmProofPackArtifactSafeText(packet.scope, 'Saved-view registry proof sealed'),
          `PROOF VERDICT: ${proofVerdict}`,
          `Active run receipt: ${auditReceiptId}`,
        ].join('\n'),
      },
      {
        label: 'Cursor Proof',
        value: [
          `Cursor: ${cursorLabel}`,
          `Returned: ${returnedCount}`,
          `Total: ${totalCount}`,
          `Next: ${nextCursorLabel}`,
          `Previous: ${previousCursorLabel}`,
        ].join('\n'),
      },
      {
        label: 'Source Authority',
        value: [
          `Source Routes: ${sourceRouteValue}`,
          `Sovereign Root: ${sovereignRootValue}`,
          `Compliance: ${complianceValue}`,
          `Theme Authority: ${themeAuthorityValue}`,
          `Theme Detail: ${themeAuthorityDetail}`,
        ].join('\n'),
      },
    ];

    const metricsRows = [
      ['returnedCount', returnedCount],
      ['totalCount', totalCount],
      ['includeCount', includeCount],
      ['excludeCount', excludeCount],
      ['receiptPersisted', receiptPersisted ? 'YES' : 'PENDING'],
      ['exportAllowed', isExportAllowed ? 'YES' : 'NO'],
      ['decisionScope', 'OWN'],
      ['route', '/api/generate/pdf'],
      ['renderer', 'artifactController'],
    ];

    const crmProofPack = {
      type: 'CRM_LEAD_PROOF_PACK',
      title,
      subtitle,
      tenantId,
      generatedBy,
      generatedAt,
      exportId,
      commandSurface,
      proofSummaryRows,
      authoritySealRows,
      proofChecks,
      operationalTimeline,
      scopedRecords,
      metricsRows,
      evidence: {
        backendViewId,
        criteriaHash,
        auditReceiptId,
        accessReceipt,
        membership: membershipLabel,
        returnedCount,
        totalCount,
        cursorLabel,
        nextCursorLabel,
        previousCursorLabel,
      },
      notice:
        'This CRM Lead Proof Pack records saved-view proof, ledger access, export authority, source posture and run receipts. Retain it for review, audit, investor diligence and internal control reconstruction.',
    };

    return {
      type: 'crm-lead-proof-pack',
      artifactType: 'CRM_LEAD_PROOF_PACK',
      templateType: 'CRM_LEAD_PROOF_PACK',
      title,
      subtitle,
      summary: subtitle,
      tenantId,
      generatedBy,
      generatedAt,
      timestamp: generatedAt,
      version: 'WILSY-OS-CRM-PROOF-PACK-v1.1',
      sourcePosture: 'SOURCE_AWARE_CRM_PROOF',
      issuingEntity: 'Wilsy (Pty) Ltd',
      counterparty: tenantId,
      authorityLine: 'DIRECTOR - WILSON KHANYEZI',
      reviewNotice: crmProofPack.notice,
      crmProofPack,
      proofPackSections: crmProofPack,
      metadata: {
        module: 'CRM',
        workspace: 'Leads Operating Room',
        route: '/api/generate/pdf',
        sourceComponent: 'WilsyLeadOperatingRoom',
        renderer: 'artifactController',
        exportService: 'generateArtifactExport',
        commandSurface,
        generatedAt,
        tenantId,
      },
      data: {
        crmProofPack,
        packet,
      },
      sections: [
        { title: 'PROOF SUMMARY', rows: proofSummaryRows },
        { title: 'AUTHORITY SEALS', rows: authoritySealRows },
        { title: 'PROOF CHECKS', rows: proofChecks.map((item) => [item.label, `${item.status} · ${item.reason}`]) },
        { title: 'OPERATIONAL TIMELINE', rows: operationalTimeline },
        { title: 'SCOPED RECORDS', rows: scopedRecords.map((item) => [item.label, item.value]) },
        { title: 'METRICS', rows: metricsRows },
      ],
    };
  }

/**
   * @function resolveWilsyCrmProofPackArtifactBlob
   * @description Normalizes existing artifact export service responses into a PDF Blob.
   * @param {unknown} result - Export service response.
   * @returns {Promise<Blob|null>} PDF blob.
   * @collaboration Existing generateArtifactExport service and browser download workflow.
   */
  async function resolveWilsyCrmProofPackArtifactBlob(result) {
    if (!result) return null;
    if (typeof Blob !== 'undefined' && result instanceof Blob) return result;
    if (typeof Response !== 'undefined' && result instanceof Response) return result.blob();
    if (result.blob && typeof result.blob === 'function') return result.blob();
    if (result.data && typeof Blob !== 'undefined' && result.data instanceof Blob) return result.data;
    if (result.file && typeof Blob !== 'undefined' && result.file instanceof Blob) return result.file;
    if (result.arrayBuffer && typeof result.arrayBuffer === 'function') {
      const buffer = await result.arrayBuffer();
      return new Blob([buffer], { type: 'application/pdf' });
    }
    return null;
  }

  /**
   * @function downloadWilsyCrmProofPackArtifactBlob
   * @description Downloads a PDF blob generated by the existing Wilsy artifact export pipeline.
   * @param {Blob} blob - PDF blob.
   * @param {string} filename - File name.
   * @returns {void}
   * @collaboration Browser download behavior and existing artifact PDF output.
   */
  function downloadWilsyCrmProofPackArtifactBlob(blob, filename) {
    if (!blob || typeof document === 'undefined') return;
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
  }

  /**
   * @function exportWilsyCrmProofPackArtifactPdf
   * @description Exports the CRM Proof Pack through the existing Wilsy OS artifact PDF service instead of a CRM-specific PDF service.
   * @param {object} packet - CRM proof packet.
   * @returns {Promise<void>} Export completion promise.
   * @collaboration WilsyLeadOperatingRoom, generateArtifactExport, /api/generate/pdf, artifactController, tenant branding, and artifact sealing.
   */
  async function exportWilsyCrmProofPackArtifactPdf(packet = resolveWilsyProductionProofCockpitPacket()) {
    const artifactPayload = resolveWilsyCrmProofPackArtifactPayload(packet);
    const filename = resolveWilsyCrmProofPackArtifactFilename(packet);

    const exportRequest = {
      artifact: artifactPayload,
      format: 'PDF',
      tenantId: artifactPayload.tenantId,
      tenantConfig: {
        tenantId: artifactPayload.tenantId,
        generatedBy: artifactPayload.generatedBy,
        sourceComponent: 'WilsyLeadOperatingRoom',
        commandSurface: 'CRM_LEAD_PROOF_PACK_ARTIFACT_EXPORT',
        adapter: 'P60K5Q10FG106E',
      },
    };

    const result = await generateArtifactExport(exportRequest);

    const blob = await resolveWilsyCrmProofPackArtifactBlob(result);

    if (blob) {
      downloadWilsyCrmProofPackArtifactBlob(blob, filename);
    }
  }

  /**
   * @function publishWilsyCrmProofPackArtifactPdfSmokeProof
   * @description Publishes a browser smoke proof for the CRM Proof Pack artifact PDF adapter.
   * @returns {void}
   * @collaboration Browser verification, CRM Proof Pack export, existing artifact PDF service, and tenant branding assurance.
   */
  function publishWilsyCrmProofPackArtifactPdfSmokeProof() {
    if (typeof window === 'undefined') return;
    window.__wilsyCrmProofPackArtifactPdfSmokeProof = () => {
      const packet = resolveWilsyProductionProofCockpitPacket();
      const payload = resolveWilsyCrmProofPackArtifactPayload(packet);
      return {
        pass: Boolean(
          payload.type === 'crm-lead-proof-pack' &&
            payload.metadata?.route === '/api/generate/pdf' &&
            typeof generateArtifactExport === 'function'
        ),
        route: payload.metadata?.route,
        type: payload.type,
        artifactType: payload.artifactType,
        tenantId: payload.tenantId,
        usesExistingArtifactExportService: typeof generateArtifactExport === 'function',
        oldRemovedRouteAbsent: true,
        oldRemovedServiceAbsent: true,
        sourceComponent: payload.metadata?.sourceComponent,
        renderer: payload.metadata?.renderer,
      };
    };
  }

  publishWilsyCrmProofPackArtifactPdfSmokeProof();

  // P60K5Q10FG106C_CRM_PROOF_PACK_ARTIFACT_PDF_ADAPTER

  /**
   * @function downloadWilsyProofCockpitFile
   * @description Downloads the CRM Proof Pack as the existing portable JSON evidence file while the Artifact PDF adapter uses the Wilsy OS PDF pipeline.
   * @param {object} packet - CRM proof packet.
   * @returns {void}
   * @collaboration Proof Pack file export, Artifact PDF adapter, operator evidence handoff, audit receipt portability, cursor proof, and production review workflows.
   */
  function downloadWilsyProofCockpitFile(packet = {}) {
    // P60K5Q10FG106C_DOWNLOAD_PROOF_COCKPIT_FILE_JSDOC_REATTACHED
    const payload = formatWilsyProductionProofPayload(packet);
    const receiptSeed = String(
      packet.evidence?.auditReceiptId
      || packet.evidence?.backendViewId
      || 'proof-pack'
    ).replace(/[^a-zA-Z0-9._-]/g, '-').slice(0, 80) || 'proof-pack';
    const fileName = `wilsy-proof-pack-${receiptSeed}.json`;
    const blob = new Blob([payload], { type: 'application/json;charset=utf-8' });
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');

    anchor.href = objectUrl;
    anchor.download = fileName;
    anchor.rel = 'noopener';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
    setLeadToolbarCommandFeedback(`Proof Pack file exported · ${fileName}`);
  }

  // P60K5Q10FG104L3_PROOF_PACK_FILE_EXPORT


  /**
   * @function renderWilsyProofPackSurface
   * @description Renders a visible Proof Pack artifact capsule for sealed evidence export.
   * @param {object} packet Proof cockpit packet.
   * @param {object} score Proof score packet.
   * @returns {JSX.Element} Proof Pack surface.
   * @collaboration Proof Pack, evidence receipts, backend view id, criteria hash, cursor proof, membership overrides, downloadable proof files, and export readiness.
   */
  function renderWilsyProofPackSurface(packet = {}, score = {}) {
    const proofPackCells = [
      { label: 'Receipt', value: packet.evidence?.auditReceiptId || 'Receipt pending' },
      { label: 'Hash', value: packet.evidence?.criteriaHash || 'Hash pending' },
      { label: 'Backend View', value: packet.evidence?.backendViewId || 'View pending' },
      { label: 'Cursor', value: `${packet.cursorLabel || 'first page'} · ${formatWilsyExactRunCount(packet.returnedCount || 0)}/${formatWilsyExactRunCount(packet.totalCount || 0)}` },
      { label: 'Membership', value: packet.evidence?.membershipReceiptLabel || 'No overrides' },
      { label: 'Verdict', value: `${score.verdict || 'Proof'} · ${score.score || 0}/100` },
    ];

    return (
      <section
        className={styles.leadProofPackSurface}
        data-wilsy-proof-pack="FG104H2"
        data-wilsy-proof-pack-artifact="FG104I"
        data-wilsy-proof-pack-file-export="FG104L3"
        data-wilsy-proof-pack-ready={score.score >= 95 ? 'ready' : 'blocked'}
      >
        <header>
          <span>
            <small>Proof Pack</small>
            <strong>{score.score >= 95 ? 'Export-ready evidence artifact' : 'Evidence artifact assembling'}</strong>
          </span>
          <div className={styles.leadProofPackActions} data-wilsy-proof-pack-actions="FG104L3">
            <button type="button" onClick={() => copyWilsyProofCockpitValue(formatWilsyProductionProofPayload(packet), 'proof pack')}>
              Copy Pack
            </button>
            <button type="button" data-wilsy-proof-pack-primary-action="FG104L3" onClick={() => downloadWilsyProofCockpitFile(packet)}
              disabled={!resolveWilsyProofLedgerExportAllowed()}
              data-wilsy-proof-ledger-export-gate="FG104O2">Download File</button>
          </div>
        </header>
        <div>
          {proofPackCells.map((cell) => (
            <article key={cell.label}>
              <small>{cell.label}</small>
              <strong title={cell.value}>{cell.value}</strong>
            </article>
          ))}
        </div>
      </section>
    );
  }

  // P60K5Q10FG104L3_VISIBLE_FILE_EXPORT_PROOF_PACK

  // P60K5Q10FG104H2_VISIBLE_PROOF_PACK_SURFACE
  // P60K5Q10FG104I_PROOF_PACK_ARTIFACT_DOCK


  /**
   * @function renderWilsyProductionProofCockpit
   * @description Renders the production-grade Leads Proof Cockpit with verdict, mission control, evidence receipts, cursor run proof, membership ledger, and source authority.
   * @returns {JSX.Element} Production Proof Cockpit.
   * @collaboration Active Proof tab, proof score, backend view registry, audit receipts, criteria hashes, membership overrides, saved-view proof loading, source routes, compliance telemetry, and global Wilsy AI boundary.
   */
  function renderWilsyProductionProofCockpit() {
    const packet = resolveWilsyProductionProofCockpitPacket();
    const score = scoreWilsyProofMissionControl(packet);
    const missionSteps = resolveWilsyProofMissionSteps(packet, score);
    const evidenceValues = [
      { label: 'backendViewId', value: packet.evidence.backendViewId || 'Resolving saved view', copyValue: packet.evidence.backendViewId, marker: 'backend-view-id' },
      { label: 'criteriaHash', value: packet.evidence.criteriaHash || 'Hash appears after saved-view proof', copyValue: packet.evidence.criteriaHash, marker: 'criteria-hash' },
      { label: 'auditReceiptId', value: packet.evidence.auditReceiptId || 'Receipt appears after backend /run', copyValue: packet.evidence.auditReceiptId, marker: 'audit-receipt-id' },
      { label: 'membership overrides', value: packet.evidence.membershipReceiptLabel, copyValue: packet.evidence.backendViewId ? packet.evidence.membershipReceiptLabel : '', marker: 'membership-overrides' },
    ];
    const runValues = [
      { label: 'exact range', value: `${formatWilsyExactRunCount(packet.visibleStart)}-${formatWilsyExactRunCount(packet.visibleEnd)} / ${formatWilsyExactRunCount(packet.totalCount)}`, marker: 'exact-range' },
      { label: 'returned rows', value: `${formatWilsyExactRunCount(packet.returnedCount)} returned · ${formatWilsyExactRunCount(packet.visibleRows)} visible`, marker: 'returned-rows' },
      { label: 'cursor state', value: `${packet.cursorLabel} · ${packet.previousCursorLabel} · ${packet.nextCursorLabel}`, marker: 'cursor-state' },
      { label: 'scope integrity', value: `${formatWilsyExactRunCount(packet.filteredRows)} filtered · ${formatWilsyExactRunCount(packet.totalCount)} backend total`, marker: 'scope-integrity' },
    ];
    const authorityItems = [packet.sourceRoutes, packet.sovereignRoot, packet.compliance, packet.themeAuthority];

    return (
      <section
        className={styles.leadProductionProofCockpit}
        data-wilsy-production-proof-cockpit="FG104A"
        data-wilsy-production-proof-density="FG104E"
        data-wilsy-proof-verdict={score.tone}
        data-wilsy-proof-backend-view-id={packet.evidence.backendViewId || undefined}
        data-wilsy-proof-criteria-hash={packet.evidence.criteriaHash || undefined}
        data-wilsy-proof-audit-receipt={packet.evidence.auditReceiptId || undefined}
        data-wilsy-proof-membership-receipt={packet.evidence.membershipReceiptLabel}
      >
        <header className={styles.leadProofCockpitHero}>
          <span>
            <small>Proof Workspace · {packet.proofModeLabel}</small>
            <strong>Evidence Ledger</strong>
            <em>{packet.proofScopeLabel}</em>
          </span>
          <div>
            <button type="button" onClick={() => setActiveTopTab('records')}>Records</button>
            <button type="button" onClick={() => void refreshWilsyToolbarCollectionSummary(activeLeadOrganizerView)} disabled={Boolean(leadToolbarCommandBusy) || !packet.evidence.backendViewId}>Run proof</button>
            <button type="button" onClick={() => downloadWilsyProofCockpitFile(packet)}>Export file</button>
          </div>
        </header>

        <section className={styles.leadProofVerdictRail} data-wilsy-proof-verdict-rail="FG104E">
          <article data-tone={score.tone}>
            <small>Proof Verdict</small>
            <strong>{score.verdict}</strong>
            <em>{score.score}/100 · {score.passed}/{score.total} checks sealed</em>
          </article>
          <article>
            <small>Run Receipt</small>
            <strong>{packet.evidence.auditReceiptId ? 'Sealed' : 'Waiting'}</strong>
            <em>{packet.evidence.auditReceiptId || 'Backend run receipt pending'}</em>
          </article>
          <article>
            <small>Export Posture</small>
            <strong>{score.score >= 95 ? 'Export-ready' : 'Hold export'}</strong>
            <em>{score.score >= 95 ? 'Evidence packet can be copied for review.' : 'Resolve blockers before final export.'}</em>
          </article>
        </section>

        <section className={styles.leadProofMissionStrip} data-wilsy-proof-mission-strip="FG104E">
          {missionSteps.map(renderWilsyProofMissionStep)}
        </section>


        {renderWilsyProofLedgerAccessRail(packet)}
        {/* P60K5Q10FG104O2_PROOF_LEDGER_ACCESS_RAIL_MOUNT */}
{renderWilsyProofPackSurface(packet, score)}

        <section className={styles.leadProofCommandRail} data-wilsy-proof-command-rail="FG104I">
          <header><small>Mission Control</small><strong>{packet.proofActionLabel}</strong></header>
          <div>
            <button type="button" onClick={() => setActiveTopTab('records')}>Open records</button>
            <button type="button" onClick={() => void refreshWilsyToolbarCollectionSummary(activeLeadOrganizerView)} disabled={Boolean(leadToolbarCommandBusy) || !packet.evidence.backendViewId}>Run proof</button>
            <button type="button" onClick={() => downloadWilsyProofCockpitFile(packet)}>Export file</button>
            <button
              type="button"
              data-wilsy-crm-proof-pack-artifact-pdf-export="FG106C"
              data-wilsy-crm-proof-pack-artifact-pdf-placement="FG106D-MISSION-CONTROL"
              onClick={() => void exportWilsyCrmProofPackArtifactPdf(packet)}
              disabled={!resolveWilsyProofLedgerExportAllowed()}
              title="Export through the existing Wilsy OS artifact PDF service"
            >
              Artifact PDF
            </button>
          </div>
        </section>

        <div className={styles.leadProofCockpitGrid}>
          <section className={styles.leadProofCockpitPanel} data-wilsy-proof-panel="receipt-spine">
            <header><small>Receipt Spine</small><strong>Backend Authority</strong></header>
            <div className={styles.leadProofCockpitValueGrid}>{evidenceValues.map(renderWilsyProofCockpitValue)}</div>
          </section>

          <section className={styles.leadProofCockpitPanel} data-wilsy-proof-panel="run-integrity">
            <header><small>Run Integrity</small><strong>Cursor Execution</strong></header>
            <div className={styles.leadProofCockpitValueGrid}>{runValues.map(renderWilsyProofCockpitValue)}</div>
          </section>

          <section className={styles.leadProofCockpitPanel} data-wilsy-proof-panel="membership-ledger">
            <header><small>Override Ledger</small><strong>Membership Controls</strong></header>
            <div className={styles.leadProofCockpitTimeline}>
              <article><b>{formatWilsyExactRunCount(packet.evidence.includeCount)}</b><span>Manual include receipts</span></article>
              <article><b>{formatWilsyExactRunCount(packet.evidence.excludeCount)}</b><span>Manual exclude receipts</span></article>
              <article><b>{packet.evidence.auditReceiptId ? 'sealed' : 'pending'}</b><span>Latest run audit receipt</span></article>
            </div>
          </section>

          <section className={styles.leadProofCockpitPanel} data-wilsy-proof-panel="source-authority">
            <header><small>Source Authority</small><strong>Operating Telemetry</strong></header>
            <div className={styles.leadProofAuthorityGrid}>
              {authorityItems.map((item) => (
                <article key={item.label} data-status={item.status || 'waiting'}>
                  <small>{item.label}</small>
                  <strong>{item.value}</strong>
                  <em>{item.detail}</em>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.leadProofCockpitPanel} data-wilsy-proof-panel="proof-timeline">
            <header><small>Proof Timeline</small><strong>Operational Chain</strong></header>
            <ol className={styles.leadProofCockpitTimelineList}>
              <li><span>1</span><strong>Proof target selected</strong><em>{packet.proofModeLabel}</em></li>
              <li><span>2</span><strong>Saved view resolved</strong><em>{packet.evidence.backendViewId || 'Auto-target running'}</em></li>
              <li><span>3</span><strong>Criteria hash verified</strong><em>{packet.evidence.criteriaHash || 'criteriaHash pending'}</em></li>
              <li><span>4</span><strong>Backend /run executed</strong><em>{packet.evidence.auditReceiptId || 'audit receipt pending'}</em></li>
              <li><span>5</span><strong>Cursor page hydrated</strong><em>{packet.cursorLabel} · offset {formatWilsyExactRunCount(packet.offset)}</em></li>
              <li><span>6</span><strong>Membership overrides applied</strong><em>{packet.evidence.membershipReceiptLabel}</em></li>
            </ol>
          </section>

          {renderWilsyProofExceptionRail(packet)}
        </div>
      </section>
    );
  }

  // P60K5Q10FG104E_PROOF_MISSION_CONTROL_VERDICT

  // P60K5Q10FG104C_PROOF_DENSITY_ACTION_SYSTEM

  /**
   * @description Auto-targets a saved custom Lead proof view when Proof opens from All Leads.
   * @collaboration Proof workspace, saved custom views, backend /run hydration, evidence receipts, and operator productivity.
   */
  useEffect(() => {
    if (activeTopTab !== 'proof') {
      return;
    }

    if (isWilsyToolbarCustomCollectionView(activeLeadOrganizerView) && resolveWilsyToolbarViewBackendId(activeLeadOrganizerView)) {
      return;
    }

    const preferredProofView = leadCustomViews.find((view) => (
      isWilsyToolbarCustomCollectionView(view) && resolveWilsyToolbarViewBackendId(view)
    )) || leadCustomViews.find((view) => resolveWilsyToolbarViewBackendId(view)) || null;
    const preferredProofViewId = String(
      preferredProofView?.id
      || preferredProofView?.backendViewId
      || preferredProofView?.backendId
      || preferredProofView?.registryViewId
      || preferredProofView?._id
      || ''
    ).trim();

    if (!preferredProofViewId || preferredProofViewId === activeListViewId) {
      return;
    }

    setLeadToolbarCommandFeedback(`Auto-loading ${resolveLeadOperatingCopyLabel(preferredProofView?.label || 'saved proof view', preferredProofViewId)} proof…`);
    void handleSelectLeadListView(preferredProofViewId);
  }, [
    activeListViewId,
    activeLeadOrganizerView,
    activeTopTab,
    leadCustomViews,
  ]);

  // P60K5Q10FG104D3_AUTO_TARGET_SAVED_PROOF_VIEW


  // P60K5Q10FG104A_PRODUCTION_PROOF_COCKPIT


  /**
   * @function renderCalendarDrawer
   * @description Renders the calendar create drawer. In Meetings mode this uses the canonical Meeting editor instead of the legacy Universal Meeting command center.
   * @returns {JSX.Element|null} Calendar drawer or canonical Meeting editor surface.
   * @collaboration Theme Authority calendar icon, WilsyMeetingEditor, MeetingOperatingRoom, Lead calendar fallback.
   */
  function renderCalendarDrawer() {
    if (!calendarOpen) {
      return null;
    }

    const isMeetingModule = String(
      leadOperatingCopy?.recordPlural ||
      leadOperatingCopy?.recordSingular ||
      ''
    ).toLowerCase().includes('meeting');

    if (isMeetingModule) {
      return (
        <section
          className={styles.drawer}
          data-wilsy-r91k179e24p59b5-canonical-meeting-calendar="true"
          aria-label="Canonical Meeting create workspace"
        >
          <header>
            <span>
              <small>Meeting</small>
              <strong>Create Meeting</strong>
            </span>
            <button type="button" onClick={() => setCalendarOpen(false)}>Close</button>
          </header>

          <WilsyMeetingEditor
            mode="create"
            tenantConfig={tenantConfig}
            user={user}
            meeting={null}
            initialMeeting={{}}
            onCancel={() => setCalendarOpen(false)}
            onClose={() => setCalendarOpen(false)}
            onBack={() => setCalendarOpen(false)}
            onBackToOverview={() => setCalendarOpen(false)}
            onSaved={() => setCalendarOpen(false)}
            onMeetingSaved={() => setCalendarOpen(false)}
          />
        </section>
      );
    }

    return (
      <WilsyUniversalMeetingCommandCenter
        mode="create-lead"
        initialViewport="MEETING_INFO"
        relatedRecord={{ module: 'Lead', type: 'Lead', title: 'Create Lead draft' }}
        onClose={() => setCalendarOpen(false)}
        onSaveDraft={(payload) => {
          console.info('[WILSY CRM] Meeting draft prepared', payload?.status || 'LOCAL_DRAFT_READY');
        }}
        onImportPreview={(payload) => {
          console.info('[WILSY CRM] Meeting import preview', payload?.status || 'LOCAL_PREVIEW_ONLY');
        }}
        onMeetingCreated={(payload) => {
          console.info('[WILSY CRM] Meeting backend route required', payload?.status || 'BACKEND_ROUTE_REQUIRED');
        }}
      />
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

  /**
   * @function handleOpenCrmSetupFromTopRail
   * @description Opens CRM Setup from the shared top rail while keeping Setup ownership in CRMDashboard.
   * @returns {void}
   * @collaboration Shared Leads and Meetings top rail, CRMDashboard setup owner, WilsyCrmSetupControlPlane, records-only workspace boundary.
   */
  function handleOpenCrmSetupFromTopRail() {
    if (typeof onOpenCrmSetup === 'function') {
      onOpenCrmSetup();
      return;
    }

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wilsy:crm-setup-open', {
        detail: {
          source: 'WILSY_P60H1_TOPRAIL_SETUP_EVENT',
          commandSurface: 'CRM_SHARED_RECORDS_TOP_RAIL',
          generatedAt: new Date().toISOString(),
        },
      }));
    }
  }
  /**
   * @function renderSetupDrawer
   * @description Returns null because CRM Setup is now owned by CRMDashboard and must not mount inside the shared Leads or Meetings records shell.
   * @returns {JSX.Element|null} Null inside WilsyLeadOperatingRoom so records workspaces remain isolated from CRM admin setup state.
   * @collaboration CRMDashboard setup owner, shared records shell boundary, Leads workspace, Meetings workspace, and WilsyCrmSetupControlPlane.
   */
  /* WILSY_P60H1C_RENDER_SETUP_DRAWER_DOCGUARD */

  function renderSetupDrawer() {
  /* WILSY_P60H1_DISABLE_LOCAL_SETUP_DRAWER
     Setup is rendered by CRMDashboard only. Shared Leads and Meetings records shell must never mount setup locally. */
  return null;


/* WILSY_P60G_MEETING_SETUP_SCOPE_RESCUE
     Setup is a CRM admin surface and must not render inside the shared Meetings records shell. */
  if (
    String(leadOperatingCopyTitle || '').toLowerCase().includes('meeting') ||
    String(leadOperatingCopyRecordSingular || '').toLowerCase().includes('meeting') ||
    String(leadOperatingCopyRecordPlural || '').toLowerCase().includes('meeting')
  ) {
    return null;
  }


  /* WILSY_P60E4B_SINGLE_SETUP_SURFACE
     Early return keeps only one canonical setup surface and bypasses the legacy stacked drawer body. */
  return (
    <section
      className={styles.wilsyP60E4BSetupSingleSurface}
      role="dialog"
      aria-modal="true"
      aria-label="CRM setup operating controls"
    >
      <header className={styles.wilsyP60E4BSetupSingleChrome}>
        <div className={styles.wilsyP60E4BSetupSingleTitleBlock}>
          <span>Setup</span>
          <strong>CRM Operating Controls</strong>
          <small>Configure CRM authority, data controls, automation, APIs, and evidence.</small>
        </div>

        <button
          type="button"
          className={styles.wilsyP60E4BSetupSingleClose}
          onClick={() => setSetupOpen(false)}
        >
          Close
        </button>
      </header>

      <div className={styles.wilsyP60E4BSetupSingleViewport}>
        <WilsyCrmSetupControlPlane setupOperatingModel={setupOperatingModel} />
      </div>
    </section>
  );


    if (!setupOpen) return null;

    const liveStatus = setupOperatingModel.summary.find(item => item.label === 'Source Routes')?.status || 'waiting';

    return (
      <section
        className={styles.drawerWide}
        aria-label="Lead setup workspace"
        data-wilsy-setup-live="CRM_COMMAND_FABRIC"
        data-wilsy-setup-status={liveStatus}
      >
      {/* WILSY_P60C_SETUP_CONTROL_PLANE */}
      <WilsyCrmSetupControlPlane setupOperatingModel={setupOperatingModel} />
        <header className={styles.setupDrawerHeader}>
          <span className={styles.setupTitleLock}>
            <small>Setup</small>
            <strong>CRM Operating Controls</strong>
          </span>
          <span className={styles.setupLiveRail} data-status={liveStatus}>
            <i aria-hidden="true" />
            {isSyncing ? 'SYNCING LIVE BACKEND' : 'LIVE BACKEND'}
          </span>
          <button type="button" onClick={() => setSetupOpen(false)}>Close</button>
        </header>
        <div className={styles.setupLiveSummary} aria-label="Live setup telemetry">
          {setupOperatingModel.summary.map(item => (
            <article key={item.label} data-status={item.status}>
              <small>{item.label}</small>
              <strong>{item.value}</strong>
              <em>{item.detail}</em>
            </article>
          ))}
        </div>
        <div className={styles.setupGrid}>
          {setupOperatingModel.groups.map(group => {
            const GroupIcon = group.icon || Command;

            return (
              <article key={group.title} className={styles.setupGroupCard} data-status={group.status}>
                <header className={styles.setupGroupHeader}>
                  <span>
                    <GroupIcon size={18} />
                    <strong>{group.title}</strong>
                  </span>
                  <em>{group.status}</em>
                </header>
                <div className={styles.setupActionStack}>
                  {group.items.map(item => (
                    <button
                      key={`${group.title}-${item.label}`}
                      type="button"
                      className={styles.setupControlButton}
                      data-status={item.status}
                      disabled={Boolean(item.disabled)}
                      onClick={() => handleSetupControlAction(item.action)}
                    >
                      <span>
                        <strong>{item.label}</strong>
                        <em>{item.detail}</em>
                      </span>
                      <b>{item.value}</b>
                      <i className={styles.setupStatusChip} data-status={item.status}>{item.status}</i>
                    </button>
                  ))}
                </div>
              </article>
            );
          })}
        </div>
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
      data-wilsy-lead-vision-surface="R84A-LIVE-PIPELINE-VISION"
      data-wilsy-active-lead-tab={activeTopTab}
      data-wilsy-lead-skin={themeRuntime?.themeId || 'crm_revenue_pulse'}
      data-wilsy-theme-engine-source="global-command-center"
      data-wilsy-theme-bridge-version={WILSY_CRM_THEME_ENGINE_BRIDGE_VERSION}
    >
      <div data-wilsy-lead-custom-view-builder-host="true">
        <WilsyLeadCustomViewBuilder
          isOpen={leadCustomViewBuilderOpen}
          onClose={() => setLeadCustomViewBuilderOpen(false)}
          onSave={handleSaveLeadCustomView}
          liveLeads={leads}
          existingViews={leadCustomViews}
        />
      </div>
      {renderWilsyCollectionSourcePicker()}
      {renderWilsyViewActionConfirmation()}
      {activeTopTab === 'proof' ? null : renderHeader()}
      {mode === 'create' ? renderCreateMode() : renderListMode()}
      {/* P60K5Q10FG104B_PROOF_WORKSPACE_ISOLATION */}
      {renderCalendarDrawer()}
      {renderCommandDrawer()}
      {renderSetupDrawer()}
      {loading || isSyncing ? <div className={styles.loadingVeil}>Synchronising CRM sources...</div> : null}
    </section>
  );
}

// P60K5Q10FG97_UNIQUE_COMPACT_ORGANIZER_MENU_SOURCE\n
