/* eslint-disable */

/**
 * @constant WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID
 * @description Runtime id for the shared CRM control repair bridge.
 */
export const WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID = 'P60K5Q10FD_SHARED_CRM_CONTROL_REPAIR';

/**
 * @function normalizeWilsyCrmControlText
 * @description Normalizes CRM control text for matching, storage keys, and visual labels.
 * @param {*} value - Candidate value.
 * @returns {string} Normalized text.
 * @collaboration Leads filters, Meetings filters, Setup map search, placeholder import receipts, and CRM control repair proof.
 */
export function normalizeWilsyCrmControlText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyCrmStorage
 * @description Resolves browser storage for local non-sensitive control state.
 * @returns {Storage|null} Browser localStorage when available.
 * @collaboration CRM filter selections, local control state, setup map query memory, and safe non-mutating UI repair.
 */
export function resolveWilsyCrmStorage() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null;
  }

  return window.localStorage;
}

/**
 * @function buildWilsyCrmFilterKey
 * @description Builds a stable local key for a CRM filter checkbox.
 * @param {HTMLInputElement} input - Checkbox input element.
 * @returns {string} Storage key.
 * @collaboration Leads filter checkboxes, Meetings filter checkboxes, local selection state, and visual selected-row markers.
 */
export function buildWilsyCrmFilterKey(input) {
  const pageTitle = normalizeWilsyCrmControlText(document.querySelector('h1')?.textContent || 'crm');
  const rowText = normalizeWilsyCrmControlText(input.closest('label, li, div')?.textContent || input.name || input.id || input.value || 'filter');
  return `wilsy.crm.controlRepair.${pageTitle}.${rowText}`.toLowerCase().replace(/[^a-z0-9.]+/g, '-');
}

/**
 * @function markWilsyCrmFilterSelection
 * @description Applies visual selected-state markers to a filter checkbox and its row.
 * @param {HTMLInputElement} input - Checkbox input element.
 * @returns {void}
 * @collaboration Leads selectable filters, Meetings selectable filters, filter sidebar evidence, and local non-mutating UI control state.
 */
export function markWilsyCrmFilterSelection(input) {
  if (!input || input.type !== 'checkbox') {
    return;
  }

  const row = input.closest('label, li, div');
  const checked = Boolean(input.checked);

  input.setAttribute('aria-checked', checked ? 'true' : 'false');
  input.dataset.wilsyCrmFilterSelected = checked ? 'true' : 'false';

  if (row) {
    row.dataset.wilsyCrmFilterRowSelected = checked ? 'true' : 'false';
    row.classList.toggle('wilsyCrmFilterRowSelected', checked);
  }
}

/**
 * @function persistWilsyCrmFilterSelection
 * @description Saves local filter checkbox state without mutating backend records.
 * @param {HTMLInputElement} input - Checkbox input element.
 * @returns {void}
 * @collaboration Leads filters, Meetings filters, browser-safe testing, and pre-mutation local state repair.
 */
export function persistWilsyCrmFilterSelection(input) {
  const storage = resolveWilsyCrmStorage();

  if (!storage || !input || input.type !== 'checkbox') {
    return;
  }

  try {
    storage.setItem(buildWilsyCrmFilterKey(input), input.checked ? 'true' : 'false');
  } catch (error) {
    return;
  }
}

/**
 * @function restoreWilsyCrmFilterSelections
 * @description Restores local filter selections after a CRM surface renders or re-renders.
 * @returns {void}
 * @collaboration Leads and Meetings filter sidebars, local test continuity, selected-row styling, and safe read-only workflow.
 */
export function restoreWilsyCrmFilterSelections() {
  const storage = resolveWilsyCrmStorage();

  Array.from(document.querySelectorAll('input[type="checkbox"]')).forEach((input) => {
    if (storage) {
      try {
        const stored = storage.getItem(buildWilsyCrmFilterKey(input));
        if (stored === 'true' || stored === 'false') {
          input.checked = stored === 'true';
        }
      } catch (error) {}
    }

    markWilsyCrmFilterSelection(input);
  });
}

/**
 * @function handleWilsyCrmCheckboxChange
 * @description Handles checkbox changes and makes selected filters visibly selected.
 * @param {Event} event - Browser change event.
 * @returns {void}
 * @collaboration CRM filter sidebars, checkbox state repair, read-only UI testing, and local selection persistence.
 */
export function handleWilsyCrmCheckboxChange(event) {
  const input = event.target?.closest?.('input[type="checkbox"]');

  if (!input) {
    return;
  }

  markWilsyCrmFilterSelection(input);
  persistWilsyCrmFilterSelection(input);
}

/**
 * @function handleWilsyCrmCheckboxClick
 * @description Repairs custom checkbox rows where the label container receives the click but the input does not visibly toggle.
 * @param {MouseEvent} event - Browser click event.
 * @returns {void}
 * @collaboration Leads filter rows, Meetings filter rows, custom checkbox shells, and operator filter selection feedback.
 */
export function handleWilsyCrmCheckboxClick(event) {
  const clickable = event.target?.closest?.('label, li, div, button');

  if (!clickable) {
    return;
  }

  const input = clickable.querySelector?.('input[type="checkbox"]');

  if (!input || event.target === input || input.disabled) {
    return;
  }

  const text = normalizeWilsyCrmControlText(clickable.textContent);

  if (!/Record Action|Related Records Action|Touched Records|Untouched Records|Last Activity Time|Activities|Campaigns|Latest Email Status|System Defined Filters|Filter By Fields/i.test(text)) {
    return;
  }

  input.checked = !input.checked;
  markWilsyCrmFilterSelection(input);
  persistWilsyCrmFilterSelection(input);
  event.preventDefault();
  event.stopPropagation();
}

/**
 * @function resolveWilsySetupSearchInput
 * @description Finds the Setup map search input.
 * @returns {HTMLInputElement|null} Setup search input when present.
 * @collaboration Setup map, domain rail, control search, authority map, and local control navigation.
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
 * @description Filters Setup map domain/control cards from the search query.
 * @param {string} query - Search text.
 * @returns {number} Number of visible controls.
 * @collaboration CRM Operating Controls, Setup map search, domain rail repair, authority/revenue/schema navigation, and production control discovery.
 */
export function filterWilsySetupMapControls(query = '') {
  const cleanQuery = normalizeWilsyCrmControlText(query).toLowerCase();
  const domainTerms = ['authority', 'revenue', 'schema', 'automation', 'custody', 'integration', 'board proof'];
  const candidates = Array.from(document.querySelectorAll('button, [role="button"], [data-domain], [data-control-id], [data-wilsy-control], li, article, section div'))
    .filter((node) => {
      const text = normalizeWilsyCrmControlText(node.textContent).toLowerCase();
      return domainTerms.some((term) => text.includes(term));
    });

  let visibleCount = 0;

  candidates.forEach((node) => {
    const text = normalizeWilsyCrmControlText(node.textContent).toLowerCase();
    const visible = !cleanQuery || text.includes(cleanQuery);

    node.dataset.wilsySetupSearchVisible = visible ? 'true' : 'false';

    if (node.style && node.closest('aside, nav, section')) {
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
 * @description Connects Setup map search input to live local domain/control filtering.
 * @param {InputEvent} event - Browser input event.
 * @returns {void}
 * @collaboration CRM Operating Controls, Setup map search, left rail repair, and authority graph navigation.
 */
export function handleWilsySetupSearchInput(event) {
  const input = resolveWilsySetupSearchInput();

  if (!input || event.target !== input) {
    return;
  }

  filterWilsySetupMapControls(input.value);
}

/**
 * @function installWilsyPlaceholderActionReceipt
 * @description Shows a governed disabled receipt for placeholder import actions instead of pretending they are connected.
 * @param {HTMLElement} target - Click target.
 * @returns {boolean} True when a placeholder action was intercepted.
 * @collaboration Import Leads, Import Notes, Meetings import placeholders, guided production hardening, and mutation prevention.
 */
export function installWilsyPlaceholderActionReceipt(target) {
  const actionNode = target?.closest?.('button, a, [role="button"], [data-wilsy-action]');

  if (!actionNode) {
    return false;
  }

  const label = normalizeWilsyCrmControlText(actionNode.textContent || actionNode.getAttribute('aria-label'));

  if (!/Import Leads|Import Notes|Import Meetings|Import/i.test(label)) {
    return false;
  }

  event?.preventDefault?.();
  event?.stopPropagation?.();

  showWilsyCrmControlRepairReceipt(`${label} is not connected yet. Build a governed import manifest, preview route, validation ledger, and receipt before enabling this action.`, 'PLACEHOLDER_IMPORT_BLOCKED');

  return true;
}

/**
 * @function showWilsyCrmControlRepairReceipt
 * @description Displays a compact in-app receipt for blocked placeholder actions and repaired controls.
 * @param {string} message - Receipt message.
 * @param {string} status - Receipt status.
 * @returns {void}
 * @collaboration CRM control repair, operator feedback, import workflow hardening, readiness source labels, and non-mutating testing.
 */
export function showWilsyCrmControlRepairReceipt(message, status = 'CONTROL_REPAIR_NOTICE') {
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

  window.clearTimeout(window.__wilsyCrmControlRepairReceiptTimer);
  window.__wilsyCrmControlRepairReceiptTimer = window.setTimeout(() => {
    receipt.remove();
  }, 4200);
}

/**
 * @function markWilsyReadinessSourceStatus
 * @description Marks readiness score panels with a visible source-of-truth warning until live backend derivation is proven.
 * @returns {void}
 * @collaboration CRM readiness score, source expansion status, setup quality telemetry, and production evidence labelling.
 */
export function markWilsyReadinessSourceStatus() {
  const nodes = Array.from(document.querySelectorAll('section, article, div')).filter((node) => {
    const text = normalizeWilsyCrmControlText(node.textContent);
    return /Readiness Score|SOURCE_EXPANSION_REQUIRED|DATA_DENSITY_EXPANSION|67%/i.test(text);
  });

  nodes.slice(0, 4).forEach((node) => {
    if (node.dataset.wilsyReadinessSourceMarked === 'true') {
      return;
    }

    node.dataset.wilsyReadinessSourceMarked = 'true';
    node.dataset.wilsyReadinessSource = 'UI_MODEL_SNAPSHOT_PENDING_LIVE_RECHECK';

    const badge = document.createElement('small');
    badge.setAttribute('data-wilsy-readiness-source-badge', 'true');
    badge.textContent = 'Source: UI model snapshot · live recheck required';
    node.appendChild(badge);
  });
}

/**
 * @function injectWilsyCrmControlRepairStyles
 * @description Injects control repair styles for selected filters, setup search, placeholder receipts, readiness labels, and rail clipping.
 * @returns {void}
 * @collaboration Leads filters, Meetings filters, Setup left rail, CRM home bottom cards, and readable production control surfaces.
 */
export function injectWilsyCrmControlRepairStyles() {
  if (typeof document === 'undefined' || document.querySelector('#wilsy-crm-control-repair-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'wilsy-crm-control-repair-styles';
  style.textContent = `
    [data-wilsy-crm-filter-row-selected="true"],
    .wilsyCrmFilterRowSelected {
      background: rgba(62, 255, 154, 0.14) !important;
      border-color: rgba(62, 255, 154, 0.42) !important;
      color: rgba(239, 255, 246, 0.98) !important;
    }

    input[type="checkbox"][data-wilsy-crm-filter-selected="true"] {
      accent-color: #3eff9a !important;
      box-shadow: 0 0 0 3px rgba(62, 255, 154, 0.16) !important;
    }

    [data-wilsy-setup-search-visible="false"] {
      display: none !important;
    }

    [data-wilsy-crm-control-repair-receipt="true"] {
      position: fixed;
      left: 50%;
      bottom: 92px;
      z-index: 999999;
      max-width: min(760px, calc(100vw - 40px));
      transform: translateX(-50%);
      padding: 14px 18px;
      border: 1px solid rgba(255, 218, 121, 0.45);
      border-radius: 18px;
      background: rgba(7, 15, 24, 0.96);
      color: rgba(255, 246, 205, 0.98);
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.42);
      font-size: 0.84rem;
      font-weight: 850;
      letter-spacing: 0.06em;
    }

    [data-wilsy-readiness-source-badge="true"] {
      display: inline-flex;
      width: fit-content;
      margin-top: 10px;
      padding: 6px 10px;
      border: 1px solid rgba(255, 218, 121, 0.28);
      border-radius: 999px;
      color: rgba(255, 238, 173, 0.92);
      font-size: 0.68rem;
      font-weight: 900;
      letter-spacing: 0.09em;
      text-transform: uppercase;
    }

    [class*="rail"],
    [class*="Rail"],
    [class*="map"],
    [class*="Map"] {
      min-width: 0 !important;
    }

    [class*="rail"] *,
    [class*="Rail"] *,
    [class*="map"] *,
    [class*="Map"] * {
      overflow-wrap: anywhere !important;
      text-overflow: ellipsis;
    }

    [class*="Source"],
    [class*="source"],
    [class*="Next"],
    [class*="next"] {
      max-width: 100%;
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function handleWilsyCrmControlClick
 * @description Handles placeholder import blocking and custom checkbox toggles.
 * @param {MouseEvent} event - Browser click event.
 * @returns {void}
 * @collaboration CRM action menus, import placeholders, filter checkbox repair, and safe pre-mutation testing.
 */
export function handleWilsyCrmControlClick(event) {
  if (installWilsyPlaceholderActionReceipt(event.target)) {
    return;
  }

  handleWilsyCrmCheckboxClick(event);
}

/**
 * @function refreshWilsyCrmControlRepairBridge
 * @description Re-applies repair state after React renders CRM surfaces.
 * @returns {void}
 * @collaboration CRM surface rendering, filter selection persistence, setup map search, readiness labelling, and visual control containment.
 */
export function refreshWilsyCrmControlRepairBridge() {
  restoreWilsyCrmFilterSelections();
  markWilsyReadinessSourceStatus();

  const setupSearch = resolveWilsySetupSearchInput();

  if (setupSearch) {
    filterWilsySetupMapControls(setupSearch.value);
  }
}

/**
 * @function installWilsyCrmControlRepairBridge
 * @description Installs the shared non-mutating CRM control repair bridge once per browser runtime.
 * @param {string} surface - Surface requesting installation.
 * @returns {string} Bridge id.
 * @collaboration Leads, Meetings, CRM Setup, Wilsy AI, source readiness, placeholder import governance, and shared CRM module hardening.
 */
export function installWilsyCrmControlRepairBridge(surface = 'crm') {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID;
  }

  injectWilsyCrmControlRepairStyles();

  window.__wilsyCrmControlRepairSurfaces = window.__wilsyCrmControlRepairSurfaces || new Set();
  window.__wilsyCrmControlRepairSurfaces.add(surface);

  if (!window.__wilsyCrmControlRepairBridgeInstalled) {
    document.addEventListener('change', handleWilsyCrmCheckboxChange, true);
    document.addEventListener('click', handleWilsyCrmControlClick, true);
    document.addEventListener('input', handleWilsySetupSearchInput, true);

    const observer = new MutationObserver(() => {
      window.clearTimeout(window.__wilsyCrmControlRepairRefreshTimer);
      window.__wilsyCrmControlRepairRefreshTimer = window.setTimeout(refreshWilsyCrmControlRepairBridge, 120);
    });

    observer.observe(document.body, { childList: true, subtree: true });
    window.__wilsyCrmControlRepairBridgeObserver = observer;
    window.__wilsyCrmControlRepairBridgeInstalled = true;
  }

  window.requestAnimationFrame(refreshWilsyCrmControlRepairBridge);

  return WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID;
}
