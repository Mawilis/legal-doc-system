/* eslint-disable */
import { sha3_512 } from 'js-sha3';
import { openWilsyLeadCommandCapsule as openWilsyLeadCommandCapsuleNative } from './WilsyLeadCommandCapsule';
import { openWilsyLeadEditSurface } from './WilsyLeadEditSurface';
import WilsyUniversalMeetingCommandCenter from '../meeting/WilsyUniversalMeetingCommandCenter.jsx';
import WilsyMeetingEditor from '../meeting/workspace/WilsyMeetingEditor.jsx';
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

  return 'Unassigned';
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


const WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT = '/api/crm/control-state/leads/filters';
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
 * @function resolveWilsyLeadsFilterPanel
 * @description Resolves the Leads filter sidebar panel from the current component screen.
 * @returns {HTMLElement|null} Leads filter panel.
 * @collaboration Leads component ownership, filter sidebar, checkbox button control, and scoped DOM repair.
 */
function resolveWilsyLeadsFilterPanel() {
  if (typeof document === 'undefined') {
    return null;
  }

  return Array.from(document.querySelectorAll('aside, section, div')).find((node) => {
    const text = normalizeWilsyLeadFilterText(node.textContent);
    return /Filter Leads by/i.test(text) && /System Defined Filters|Filter By Fields|Activities|Record Action/i.test(text);
  }) || null;
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
  if (typeof window === 'undefined' || !window.localStorage) {
    return [];
  }

  try {
    const parsed = JSON.parse(window.localStorage.getItem(WILSY_LEADS_FILTER_LOCAL_STATE_KEY) || '[]');
    return Array.isArray(parsed) ? parsed.map(normalizeWilsyLeadFilterText).filter(Boolean) : [];
  } catch (error) {
    return [];
  }
}

/**
 * @function saveWilsyLeadLocalFilterState
 * @description Saves selected Leads filters locally until backend persistence confirms state.
 * @param {Array<string>} selectedFilters - Selected filter labels.
 * @returns {void}
 * @collaboration Leads filter persistence, browser continuity, backend fallback, and operator-controlled filter state.
 */
function saveWilsyLeadLocalFilterState(selectedFilters = []) {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }

  try {
    window.localStorage.setItem(WILSY_LEADS_FILTER_LOCAL_STATE_KEY, JSON.stringify(selectedFilters));
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
  const { headers } = resolveWilsyLeadOperatorHeaders();
  const response = await fetch(`${resolveWilsyLeadApiBase()}${WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT}`, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    throw new Error(`Leads filter control state GET failed with ${response.status}`);
  }

  const payload = await response.json();
  return Array.isArray(payload?.selectedFilters) ? payload.selectedFilters.map(normalizeWilsyLeadFilterText).filter(Boolean) : [];
}

/**
 * @function persistWilsyLeadFilterControlState
 * @description Persists current Leads filter checkbox state to backend with institutional evidence.
 * @param {Array<string>} selectedFilters - Selected filter labels.
 * @returns {Promise<void>} Completion promise.
 * @collaboration Leads filter buttons, backend PUT route, institutional headers, strike payload, and source-backed control state.
 */
async function persistWilsyLeadFilterControlState(selectedFilters = []) {
  const { headers } = resolveWilsyLeadOperatorHeaders();
  const response = await fetch(`${resolveWilsyLeadApiBase()}${WILSY_LEADS_FILTER_CONTROL_STATE_ENDPOINT}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(buildWilsyLeadFilterInstitutionalPayload(selectedFilters)),
  });

  if (!response.ok) {
    throw new Error(`Leads filter control state PUT failed with ${response.status}`);
  }
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
 * @function installWilsyLeadFilterControlStateController
 * @description Installs Leads component-owned filter checkbox ticking and backend state persistence.
 * @returns {Function} Cleanup function.
 * @collaboration WilsyLeadOperatingRoom, Leads filter buttons, backend control-state route, tenant/operator evidence, and persisted user selections.
 */
function installWilsyLeadFilterControlStateController() {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return () => {};
  }

  injectWilsyLeadFilterButtonStyles();
  applyWilsyLeadSelectedFilters(loadWilsyLeadLocalFilterState());

  fetchWilsyLeadFilterControlState()
    .then((selectedFilters) => {
      saveWilsyLeadLocalFilterState(selectedFilters);
      applyWilsyLeadSelectedFilters(selectedFilters);
    })
    .catch(() => {
      applyWilsyLeadSelectedFilters(loadWilsyLeadLocalFilterState());
    });

  /**
   * @function handleLeadFilterClick
   * @description Handles Leads filter row and checkbox clicks so the actual checkbox square ticks or unticks, then persists the selected filter state.
   * @param {MouseEvent} event - Browser click event from the Leads filter sidebar.
   * @returns {void}
   * @collaboration Leads filter sidebar, checkbox source of truth, backend control-state persistence, local fallback state, and operator-controlled filtering.
   */
  const handleLeadFilterClick = (event) => {
    const panel = resolveWilsyLeadsFilterPanel();

    if (!panel || !panel.contains(event.target)) {
      return;
    }

    const directInput = event.target?.closest?.('input[type="checkbox"]');
    const row = event.target?.closest?.('label, li, div');
    const input = directInput || row?.querySelector?.('input[type="checkbox"]');

    if (!input || input.disabled) {
      return;
    }

    if (!directInput) {
      event.preventDefault();
      event.stopPropagation();
      setWilsyLeadFilterChecked(input, !input.checked);
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }

    window.setTimeout(() => {
      const selectedFilters = collectWilsyLeadSelectedFilters();
      saveWilsyLeadLocalFilterState(selectedFilters);
      persistWilsyLeadFilterControlState(selectedFilters).catch(() => {});
    }, 0);
  };

  /**
   * @function handleLeadFilterChange
   * @description Handles native Leads checkbox changes and synchronizes selected filters to local storage and the backend control-state route.
   * @param {Event} event - Browser change event from a Leads filter checkbox.
   * @returns {void}
   * @collaboration Leads checkbox state, selected filter persistence, Wilsy institutional evidence payload, and backend control-state route.
   */
  const handleLeadFilterChange = (event) => {
    const panel = resolveWilsyLeadsFilterPanel();
    const input = event.target?.closest?.('input[type="checkbox"]');

    if (!panel || !input || !panel.contains(input)) {
      return;
    }

    setWilsyLeadFilterChecked(input, input.checked);

    const selectedFilters = collectWilsyLeadSelectedFilters();
    saveWilsyLeadLocalFilterState(selectedFilters);
    persistWilsyLeadFilterControlState(selectedFilters).catch(() => {});
  };

  document.addEventListener('click', handleLeadFilterClick, true);
  document.addEventListener('change', handleLeadFilterChange, true);

  const refreshTimer = window.setInterval(() => {
    applyWilsyLeadSelectedFilters(loadWilsyLeadLocalFilterState());
  }, 1600);

  return () => {
    document.removeEventListener('click', handleLeadFilterClick, true);
    document.removeEventListener('change', handleLeadFilterChange, true);
    window.clearInterval(refreshTimer);
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

const LEAD_PAGE_SIZE_OPTIONS = Object.freeze([10, 20, 50, 100]);

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


const WILSY_LEADS_FILTER_SELECTION_STORAGE_KEY = 'wilsy.crm.leads.filterSelection.v2';

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
  const [activeListViewId, setActiveListViewId] = useState('ALL_LEADS');
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [leadFilterQuery, setLeadFilterQuery] = useState('');
  const [selectedLeadFilterOptions, setSelectedLeadFilterOptions] = useState(() => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return new Set();
    }

    try {
      const parsed = JSON.parse(window.localStorage.getItem(WILSY_LEADS_FILTER_SELECTION_STORAGE_KEY) || '[]');
      return new Set(Array.isArray(parsed) ? parsed.filter(Boolean) : []);
    } catch (error) {
      return new Set();
    }
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
  const [draft, setDraft] = useState(() => createEmptyLeadDraft({}));
  const [saveStatus, setSaveStatus] = useState('');
  const [syncStatus, setSyncStatus] = useState('SOURCE_READY_UPSTREAM');
  const [syncTelemetry, setSyncTelemetry] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedLeadId, setSelectedLeadId] = useState('');
  const [selectedRowIds, setSelectedRowIds] = useState([]);
  const [openRowActionId, setOpenRowActionId] = useState('');
  const [currentLeadPage, setCurrentLeadPage] = useState(1);
  const [leadPageSize, setLeadPageSize] = useState(20);
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

  const baseFilteredLeads = useMemo(() => {
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
   * @description Applies a Lead list view from the module dropdown.
   * @param {string} listViewId - List view id.
   * @returns {void}
   * @collaboration Converts the Zoho-inspired dropdown into source-backed Wilsy OS filtering.
   */
  function handleSelectLeadListView(listViewId) {
    const nextView = resolveLeadListView(listViewId);
    setActiveListViewId(nextView.id);
    setActiveFilter(nextView.filter || 'ALL');
    setCurrentLeadPage(1);
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
          <section className={styles.leadViewCluster}>
            <div className={styles.leadDropdownWrap}>
              <button type="button" className={styles.leadViewButton} onClick={() => setViewMenuOpen(previous => !previous)}>
                <List size={18} />
                <span>
                  <strong>{resolveLeadOperatingCopyLabel(activeListView.label, activeListView.id)}</strong>
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
                      <span>{resolveLeadOperatingCopyLabel(view.label, view.id)}</span>
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
          aria-label="Lead filters collapsed"
        >
          <button
            type="button"
            onClick={() => setFilterPanelOpen(previous => !previous)}
            aria-label="Show Lead filters"
            title="Show filters"
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
        aria-label="Lead filters"
      >
        <header className={styles.leadFilterRailHeader}>
          <span>
            <strong>{leadOperatingCopy.filterTitle}</strong>
            <em>{visibleFilterCount} available filters</em>
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
   * @function renderLeadRecordsCommandBar
   * @description Renders the records-table command bar with view, tab, filter, sort and create actions.
   * @returns {JSX.Element} Records command bar.
   * @collaboration Places the working controls inside the Lead grid shell from Wilson's vision mock.
   */
  function renderLeadRecordsCommandBar() {
    const activeSort = LEAD_SORT_OPTIONS.find(option => option.id === sortMode) || LEAD_SORT_OPTIONS[0];

    return (
      <section className={styles.leadRecordsCommandBar} data-wilsy-lead-grid-toolbar="R84A-VISION-COMMAND-BAR">
        <section className={styles.leadViewCluster}>
          <div className={styles.leadDropdownWrap}>
            <button type="button" className={styles.leadViewButton} onClick={() => setViewMenuOpen(previous => !previous)}>
              <SlidersHorizontal size={18} />
              <span>
                <strong>{resolveLeadOperatingCopyLabel(activeListView.label, activeListView.id)}</strong>
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
                    <span>{resolveLeadOperatingCopyLabel(view.label, view.id)}</span>
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
              <small>{resolveLeadOperatingCopyLabel(activeListView.label, activeListView.id)}</small>
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
                          onChange={() => handleToggleLeadSelection(recordId)}
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
                  <td colSpan={9}>
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
              <strong>{filteredLeads.length ? `Showing ${leadPagination.startRecord} to ${leadPagination.endRecord} of ${filteredLeads.length} ${leadOperatingCopyRecordPlural}` : selectedLeadFilterOptions.size ? `Showing 0 matching ${leadOperatingCopyRecordPlural}` : `Showing 0 live ${leadOperatingCopyRecordPlural}`}</strong>
              <em>{selectedRowIds.length ? `${selectedRowIds.length} selected` : selectedLeadFilterOptions.size ? `${selectedLeadFilterOptions.size} active filters · ${baseFilteredLeads.length} source rows` : 'Live backend rows only'}</em>
            </span>
            <nav className={styles.leadFooterPagination} aria-label={`${leadOperatingCopyTitle} records pagination`}>
              <button type="button" disabled={leadPagination.currentPage <= 1} aria-label="First page" onClick={() => handleLeadPageChange(1)}>|&lt;</button>
              <button type="button" disabled={leadPagination.currentPage <= 1} aria-label="Previous page" onClick={() => handleLeadPageChange(leadPagination.currentPage - 1)}>&lt;</button>
              {leadPagination.pageItems.map(item => (
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
              <button type="button" disabled={leadPagination.currentPage >= leadPagination.totalPages} aria-label="Next page" onClick={() => handleLeadPageChange(leadPagination.currentPage + 1)}>&gt;</button>
              <button type="button" disabled={leadPagination.currentPage >= leadPagination.totalPages} aria-label="Last page" onClick={() => handleLeadPageChange(leadPagination.totalPages)}>&gt;|</button>
              <label className={styles.leadFooterPageSize}>
                <select
                  value={leadPagination.pageSize}
                  onChange={event => handleLeadPageSizeChange(event.target.value)}
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
      <section className={styles.createSurface}>
        <header className={styles.createHeader}>
          <span><small>Focused Create</small><strong>Create Verified Lead</strong><em>Capture, enrich, schedule and prove the Lead source from one workspace.</em></span>
          <div>
            <button type="button" onClick={() => resetLeadDraftForPrivacy('list')}>Cancel</button>
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
              <label><span>{leadOperatingCopy.tableHeaders.phone}</span><input value={draft.phone} onChange={event => updateDraftField('phone', event.target.value)} /></label>
              <label><span>Mobile</span><input value={draft.mobile} onChange={event => updateDraftField('mobile', event.target.value)} /></label>
              <label><span>Title</span><input value={draft.title} onChange={event => updateDraftField('title', event.target.value)} /></label>
              <label><span>Lead Source</span><select value={draft.source} onChange={event => updateDraftField('source', event.target.value)}><option>Website</option><option>Referral</option><option>Partner</option><option>Outbound</option><option>Event</option><option>Wilsy AI</option></select></label>
              <label><span>{leadOperatingCopy.tableHeaders.status}</span><select value={draft.status} onChange={event => updateDraftField('status', event.target.value)}><option>NEW</option><option>OPEN</option><option>CONTACTED</option><option>{leadOperatingCopy.qualifiedLabel}</option><option>DISQUALIFIED</option></select></label>
              <label><span>Industry</span><input value={draft.industry} onChange={event => updateDraftField('industry', event.target.value)} /></label>
              <label><span>{leadOperatingCopy.tableHeaders.owner}</span><input value={draft.owner} onChange={event => updateDraftField('owner', event.target.value)} /></label>
              <label><span>Website</span><input value={draft.website} onChange={event => updateDraftField('website', event.target.value)} /></label>
              <label><span>Employees</span><input value={draft.employees} onChange={event => updateDraftField('employees', event.target.value)} /></label>
            </div>

            <h3>Address Intelligence</h3>
            <section className={styles.addressCommandDeck} aria-label="Wilsy OS address intelligence command">
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
      {renderHeader()}
      {mode === 'create' ? renderCreateMode() : renderListMode()}
      {renderCalendarDrawer()}
      {renderCommandDrawer()}
      {renderSetupDrawer()}
      {loading || isSyncing ? <div className={styles.loadingVeil}>Synchronising CRM sources...</div> : null}
    </section>
  );
}
