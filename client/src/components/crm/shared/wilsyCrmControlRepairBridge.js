/* eslint-disable */

/**
 * @constant WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID
 * @description Runtime id for the contained CRM control bridge after removing harmful global layout side effects.
 */
export const WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID = 'P60K5Q10FF_CONTAINED_CRM_CONTROL_BRIDGE';

/**
 * @function normalizeWilsyCrmControlText
 * @description Normalizes CRM control text for safe matching and local storage keys.
 * @param {*} value - Candidate value.
 * @returns {string} Normalized text.
 * @collaboration Leads filters, Meetings filters, Setup map search, import action receipts, and contained CRM control behavior.
 */
export function normalizeWilsyCrmControlText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyCrmStorage
 * @description Resolves browser localStorage for non-sensitive local control state only.
 * @returns {Storage|null} Browser localStorage when available.
 * @collaboration CRM filter persistence, local UI state, safe pre-mutation testing, and non-sensitive operator preferences.
 */
export function resolveWilsyCrmStorage() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null;
  }

  return window.localStorage;
}

/**
 * @function resolveWilsyPageTitle
 * @description Resolves the current CRM page title for stable local filter keys.
 * @returns {string} Current page title.
 * @collaboration Leads, Meetings, CRM Operating Controls, local filter state, and module-specific UI repair.
 */
export function resolveWilsyPageTitle() {
  if (typeof document === 'undefined') {
    return 'crm';
  }

  return normalizeWilsyCrmControlText(document.querySelector('h1')?.textContent || document.title || 'crm');
}

/**
 * @function buildWilsyCrmFilterKey
 * @description Builds a stable storage key for a CRM filter checkbox.
 * @param {HTMLInputElement} input - Checkbox input.
 * @returns {string} Storage key.
 * @collaboration Leads filter checkboxes, Meetings filter checkboxes, persisted selection, and visible filter state.
 */
export function buildWilsyCrmFilterKey(input) {
  const pageTitle = resolveWilsyPageTitle();
  const rowText = normalizeWilsyCrmControlText(input.closest('label, li, div')?.textContent || input.name || input.id || input.value || 'filter');

  return `wilsy.crm.filter.${pageTitle}.${rowText}`.toLowerCase().replace(/[^a-z0-9.]+/g, '-');
}

/**
 * @function setWilsyCheckboxChecked
 * @description Sets a checkbox using the native checked setter so React/custom controls can receive the real state.
 * @param {HTMLInputElement} input - Checkbox input.
 * @param {boolean} checked - Desired checked value.
 * @returns {void}
 * @collaboration Leads filter tick state, Meetings filter tick state, native checkbox rendering, and persistent filter state.
 */
export function setWilsyCheckboxChecked(input, checked) {
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

  if (input.checked) {
    input.setAttribute('checked', 'checked');
  } else {
    input.removeAttribute('checked');
  }
}

/**
 * @function markWilsyCheckbox
 * @description Marks checkbox and row state without touching backend data.
 * @param {HTMLInputElement} input - Checkbox input.
 * @returns {void}
 * @collaboration Leads filters, Meetings filters, persistent selection, visual tick state, and row state.
 */
export function markWilsyCheckbox(input) {
  if (!input || input.type !== 'checkbox') {
    return;
  }

  const row = input.closest('label, li, div');
  const checked = Boolean(input.checked);

  input.dataset.wilsyCrmFilterSelected = checked ? 'true' : 'false';
  input.setAttribute('aria-checked', checked ? 'true' : 'false');

  if (row) {
    row.dataset.wilsyCrmFilterRowSelected = checked ? 'true' : 'false';
  }
}

/**
 * @function persistWilsyCheckbox
 * @description Persists local checkbox selection until the user clears/unticks it.
 * @param {HTMLInputElement} input - Checkbox input.
 * @returns {void}
 * @collaboration Leads filters, Meetings filters, local persistence, and user-controlled filter state.
 */
export function persistWilsyCheckbox(input) {
  const storage = resolveWilsyCrmStorage();

  if (!storage || !input || input.type !== 'checkbox') {
    return;
  }

  try {
    storage.setItem(buildWilsyCrmFilterKey(input), input.checked ? 'true' : 'false');
  } catch (error) {}
}

/**
 * @function restoreWilsyCheckboxes
 * @description Restores persisted checkbox states without broad layout manipulation.
 * @returns {void}
 * @collaboration Leads filter persistence, Meetings filter persistence, checkbox tick visibility, and safe runtime refresh.
 */
export function restoreWilsyCheckboxes() {
  const storage = resolveWilsyCrmStorage();

  Array.from(document.querySelectorAll('input[type="checkbox"]')).forEach((input) => {
    if (storage) {
      try {
        const stored = storage.getItem(buildWilsyCrmFilterKey(input));
        if (stored === 'true' || stored === 'false') {
          setWilsyCheckboxChecked(input, stored === 'true');
        }
      } catch (error) {}
    }

    markWilsyCheckbox(input);
  });
}

/**
 * @function handleWilsyCheckboxChange
 * @description Persists checkbox state after real input changes.
 * @param {Event} event - Change event.
 * @returns {void}
 * @collaboration Leads filter checkboxes, Meetings filter checkboxes, user-controlled ticking, and persistent filter state.
 */
export function handleWilsyCheckboxChange(event) {
  const input = event.target?.closest?.('input[type="checkbox"]');

  if (!input) {
    return;
  }

  window.setTimeout(() => {
    markWilsyCheckbox(input);
    persistWilsyCheckbox(input);
  }, 0);
}

/**
 * @function handleWilsyCheckboxRowClick
 * @description Turns row clicks into native checkbox clicks for filter rows only.
 * @param {MouseEvent} event - Click event.
 * @returns {void}
 * @collaboration Leads filter row clicks, Meetings filter row clicks, checkbox tick reliability, and local persisted selection.
 */
export function handleWilsyCheckboxRowClick(event) {
  const directInput = event.target?.closest?.('input[type="checkbox"]');

  if (directInput) {
    return;
  }

  const row = event.target?.closest?.('label, li, div');

  if (!row) {
    return;
  }

  const rowText = normalizeWilsyCrmControlText(row.textContent);

  if (!/Record Action|Related Records Action|Touched Records|Untouched Records|Annual Revenue|Last Activity Time|Activities|Campaigns|Latest Email Status|System Defined Filters|Filter By Fields/i.test(rowText)) {
    return;
  }

  const input = row.querySelector?.('input[type="checkbox"]');

  if (!input || input.disabled) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();

  setWilsyCheckboxChecked(input, !input.checked);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  markWilsyCheckbox(input);
  persistWilsyCheckbox(input);
}

/**
 * @function resolveWilsySetupSearchInput
 * @description Finds the Setup map search input.
 * @returns {HTMLInputElement|null} Setup search input when present.
 * @collaboration Setup map search, CRM Operating Controls, domain filtering, and connected control discovery.
 */
export function resolveWilsySetupSearchInput() {
  return Array.from(document.querySelectorAll('input')).find((input) => {
    const placeholder = normalizeWilsyCrmControlText(input.getAttribute('placeholder'));
    const aria = normalizeWilsyCrmControlText(input.getAttribute('aria-label'));

    return /Find controls|Setup map|controls/i.test(`${placeholder} ${aria}`);
  }) || null;
}

/**
 * @function filterWilsySetupMapControls
 * @description Filters Setup map cards by search query without changing rail layout or open/close behavior.
 * @param {string} query - Search text.
 * @returns {number} Visible candidate count.
 * @collaboration Setup search, Authority/Revenue/Schema domain cards, control discovery, and non-mutating UI filtering.
 */
export function filterWilsySetupMapControls(query = '') {
  const cleanQuery = normalizeWilsyCrmControlText(query).toLowerCase();
  const domainTerms = ['authority', 'revenue', 'schema', 'automation', 'custody', 'integration', 'board proof'];
  let visibleCount = 0;

  Array.from(document.querySelectorAll('button, [role="button"], [data-domain], [data-control-id], li, article')).forEach((node) => {
    const text = normalizeWilsyCrmControlText(node.textContent).toLowerCase();
    const isDomain = domainTerms.some((term) => text.includes(term));

    if (!isDomain) {
      return;
    }

    const visible = !cleanQuery || text.includes(cleanQuery);
    node.dataset.wilsySetupSearchVisible = visible ? 'true' : 'false';

    if (node.style) {
      node.style.display = visible ? '' : 'none';
    }

    if (visible) {
      visibleCount += 1;
    }
  });

  document.documentElement.dataset.wilsySetupSearchQuery = cleanQuery;
  document.documentElement.dataset.wilsySetupSearchVisibleCount = String(visibleCount);

  return visibleCount;
}

/**
 * @function handleWilsySetupSearchInput
 * @description Connects Setup map search input to domain filtering only.
 * @param {InputEvent} event - Input event.
 * @returns {void}
 * @collaboration Setup map search, left domain list, control discovery, and safe local filtering.
 */
export function handleWilsySetupSearchInput(event) {
  const input = resolveWilsySetupSearchInput();

  if (!input || event.target !== input) {
    return;
  }

  filterWilsySetupMapControls(input.value);
}

/**
 * @function showWilsyControlReceipt
 * @description Shows a short receipt for blocked placeholder actions.
 * @param {string} message - Receipt message.
 * @param {string} status - Receipt status.
 * @returns {void}
 * @collaboration Import Leads, Import Notes, placeholder blocking, operator feedback, and production workflow hardening.
 */
export function showWilsyControlReceipt(message, status = 'CRM_CONTROL_NOTICE') {
  if (typeof document === 'undefined') {
    return;
  }

  let receipt = document.querySelector('[data-wilsy-crm-control-repair-receipt="true"]');

  if (!receipt) {
    receipt = document.createElement('div');
    receipt.setAttribute('data-wilsy-crm-control-repair-receipt', 'true');
    document.body.appendChild(receipt);
  }

  receipt.textContent = message;
  receipt.dataset.status = status;
  receipt.dataset.generatedAt = new Date().toISOString();

  window.clearTimeout(window.__wilsyCrmControlReceiptTimer);
  window.__wilsyCrmControlReceiptTimer = window.setTimeout(() => receipt.remove(), 4200);
}

/**
 * @function handleWilsyPlaceholderAction
 * @description Blocks placeholder import actions until a real import manifest workflow exists.
 * @param {MouseEvent} event - Click event.
 * @returns {boolean} True when blocked.
 * @collaboration Import Leads, Import Notes, governed import manifest, duplicate handling, and receipt-backed production workflow.
 */
export function handleWilsyPlaceholderAction(event) {
  const node = event.target?.closest?.('button, a, [role="button"], [data-wilsy-action]');

  if (!node) {
    return false;
  }

  const label = normalizeWilsyCrmControlText(node.textContent || node.getAttribute('aria-label'));

  if (!/Import Leads|Import Notes|Import Meetings|Import/i.test(label)) {
    return false;
  }

  event.preventDefault();
  event.stopPropagation();

  showWilsyControlReceipt(
    `${label} is blocked until the real import manifest, preview ledger, duplicate policy, and evidence receipt workflow is connected.`,
    'PLACEHOLDER_IMPORT_BLOCKED',
  );

  return true;
}

/**
 * @function injectContainedWilsyControlStyles
 * @description Injects narrow styles only for checkbox ticks, setup search visibility, receipts, and meeting readiness centering.
 * @returns {void}
 * @collaboration Checkbox ticks, persisted filter state, setup search filtering, meeting readiness alignment, and import placeholder receipts.
 */
export function injectContainedWilsyControlStyles() {
  if (typeof document === 'undefined' || document.querySelector('#wilsy-contained-crm-control-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-contained-crm-control-styles';
  style.textContent = `
    input[type="checkbox"][data-wilsy-crm-filter-selected="true"] {
      -webkit-appearance: checkbox !important;
      appearance: auto !important;
      accent-color: #3eff9a !important;
      outline: 2px solid rgba(62, 255, 154, 0.5) !important;
      outline-offset: 2px !important;
    }

    [data-wilsy-crm-filter-row-selected="true"] {
      background: rgba(62, 255, 154, 0.14) !important;
      border-color: rgba(62, 255, 154, 0.42) !important;
    }

    [data-wilsy-setup-search-visible="false"] {
      display: none !important;
    }

    [data-wilsy-crm-control-repair-receipt="true"] {
      position: fixed !important;
      left: 50% !important;
      bottom: 92px !important;
      z-index: 999999 !important;
      max-width: min(760px, calc(100vw - 40px)) !important;
      transform: translateX(-50%) !important;
      padding: 14px 18px !important;
      border: 1px solid rgba(255, 218, 121, 0.45) !important;
      border-radius: 18px !important;
      background: rgba(7, 15, 24, 0.96) !important;
      color: rgba(255, 246, 205, 0.98) !important;
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.42) !important;
      font-size: 0.84rem !important;
      font-weight: 850 !important;
      letter-spacing: 0.06em !important;
    }

    [data-wilsy-meeting-readiness-pill="true"] {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      text-align: center !important;
      line-height: 1 !important;
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function cleanupPreviousWilsyGlobalBridgeEffects
 * @description Removes harmful global styles/datasets from the previous bridge version that damaged Setup side rails.
 * @returns {void}
 * @collaboration Setup side rail recovery, CRM Operating Controls open/close behavior, containment, and safe rollback from broad DOM repair.
 */
export function cleanupPreviousWilsyGlobalBridgeEffects() {
  if (typeof document === 'undefined') {
    return;
  }

  document.querySelector('#wilsy-crm-control-repair-styles')?.remove();
  document.querySelector('[data-wilsy-meeting-outcome-panel="true"]')?.remove();

  Array.from(document.querySelectorAll('[data-wilsy-setup-domain-rail-repaired], [data-wilsy-setup-inspector-rail-repaired], [data-wilsy-setup-adaptive-stage-repaired]')).forEach((node) => {
    delete node.dataset.wilsySetupDomainRailRepaired;
    delete node.dataset.wilsySetupInspectorRailRepaired;
    delete node.dataset.wilsySetupAdaptiveStageRepaired;
  });
}

/**
 * @function refreshWilsyContainedControlBridge
 * @description Refreshes contained control behavior without manipulating CRM layout rails.
 * @returns {void}
 * @collaboration Leads filters, Meetings filters, Setup search, import receipt blocking, and safe runtime refresh.
 */
export function refreshWilsyContainedControlBridge() {
  cleanupPreviousWilsyGlobalBridgeEffects();
  restoreWilsyCheckboxes();

  const setupSearch = resolveWilsySetupSearchInput();

  if (setupSearch) {
    filterWilsySetupMapControls(setupSearch.value);
  }

  Array.from(document.querySelectorAll('td, div, span, strong')).forEach((node) => {
    const text = normalizeWilsyCrmControlText(node.textContent);
    if (/^\d{1,3}%$/.test(text)) {
      node.dataset.wilsyMeetingReadinessPill = 'true';
    }
  });
}

/**
 * @function handleContainedWilsyControlClick
 * @description Handles contained click behaviors only: placeholder imports and filter row ticking.
 * @param {MouseEvent} event - Click event.
 * @returns {void}
 * @collaboration CRM filter rows, placeholder import blocking, Setup rail safety, and local UI state.
 */
export function handleContainedWilsyControlClick(event) {
  if (handleWilsyPlaceholderAction(event)) {
    return;
  }

  handleWilsyCheckboxRowClick(event);
}

/**
 * @function installWilsyCrmControlRepairBridge
 * @description Installs the contained CRM control bridge without broad rail/stage layout manipulation.
 * @param {string} surface - Surface requesting installation.
 * @returns {string} Bridge id.
 * @collaboration Leads, Meetings, Setup search, import workflow hardening, checkbox persistence, and safe production containment.
 */
export function installWilsyCrmControlRepairBridge(surface = 'crm') {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID;
  }

  injectContainedWilsyControlStyles();
  cleanupPreviousWilsyGlobalBridgeEffects();

  window.__wilsyCrmControlRepairSurfaces = window.__wilsyCrmControlRepairSurfaces || new Set();
  window.__wilsyCrmControlRepairSurfaces.add(surface);

  if (!window.__wilsyContainedCrmControlBridgeInstalled) {
    document.addEventListener('change', handleWilsyCheckboxChange, true);
    document.addEventListener('click', handleContainedWilsyControlClick, true);
    document.addEventListener('input', handleWilsySetupSearchInput, true);
    window.__wilsyContainedCrmControlBridgeInstalled = true;
  }

  window.clearTimeout(window.__wilsyContainedCrmControlRefreshTimer);
  window.__wilsyContainedCrmControlRefreshTimer = window.setTimeout(refreshWilsyContainedControlBridge, 80);

  return WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID;
}
