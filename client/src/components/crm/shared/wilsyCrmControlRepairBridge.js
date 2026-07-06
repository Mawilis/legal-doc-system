/* eslint-disable */

/**
 * @constant WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID
 * @description Runtime id for the shared CRM control repair bridge.
 */
export const WILSY_CRM_CONTROL_REPAIR_BRIDGE_ID = 'P60K5Q10FE_CRM_CONTROL_COMPLETION';

/**
 * @constant WILSY_CRM_MEETING_OUTCOME_KEY
 * @description Local non-sensitive storage key for meeting outcome learning candidates.
 */
export const WILSY_CRM_MEETING_OUTCOME_KEY = 'wilsy.crm.meetingOutcomes.v1';

/**
 * @function normalizeWilsyCrmControlText
 * @description Normalizes CRM control text for matching, storage keys, receipts, and visual labels.
 * @param {*} value - Candidate value.
 * @returns {string} Normalized text.
 * @collaboration Leads filters, Meetings filters, Setup search, meeting outcome capture, and CRM control repair proof.
 */
export function normalizeWilsyCrmControlText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyCrmStorage
 * @description Resolves browser localStorage for non-sensitive local control state.
 * @returns {Storage|null} Browser localStorage when available.
 * @collaboration CRM filter selections, meeting outcome candidates, setup search state, and safe pre-mutation UI repair.
 */
export function resolveWilsyCrmStorage() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null;
  }

  return window.localStorage;
}

/**
 * @function resolveWilsyPageTitle
 * @description Resolves the current CRM page title.
 * @returns {string} Current page title.
 * @collaboration Leads, Meetings, CRM Operating Controls, local filter keys, and meeting outcome context.
 */
export function resolveWilsyPageTitle() {
  if (typeof document === 'undefined') {
    return 'crm';
  }

  return normalizeWilsyCrmControlText(document.querySelector('h1')?.textContent || document.title || 'crm');
}

/**
 * @function buildWilsyCrmFilterKey
 * @description Builds a stable local key for a CRM filter checkbox.
 * @param {HTMLInputElement} input - Checkbox input element.
 * @returns {string} Storage key.
 * @collaboration Leads filter checkboxes, Meetings filter checkboxes, local selection state, and visual selected-row markers.
 */
export function buildWilsyCrmFilterKey(input) {
  const pageTitle = resolveWilsyPageTitle();
  const rowText = normalizeWilsyCrmControlText(input.closest('label, li, div')?.textContent || input.name || input.id || input.value || 'filter');
  return `wilsy.crm.controlRepair.${pageTitle}.${rowText}`.toLowerCase().replace(/[^a-z0-9.]+/g, '-');
}

/**
 * @function setWilsyNativeCheckboxValue
 * @description Sets a checkbox with the native HTMLInputElement setter so React/custom controls receive real checked state.
 * @param {HTMLInputElement} input - Checkbox input element.
 * @param {boolean} checked - Next checked value.
 * @returns {void}
 * @collaboration Leads filter checkboxes, Meetings filter checkboxes, custom selection rows, React change events, and real tick rendering.
 */
export function setWilsyNativeCheckboxValue(input, checked) {
  if (!input || input.type !== 'checkbox') {
    return;
  }

  const descriptor = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked');

  if (descriptor?.set) {
    descriptor.set.call(input, Boolean(checked));
  } else {
    input.checked = Boolean(checked);
  }

  if (input.checked) {
    input.setAttribute('checked', 'checked');
  } else {
    input.removeAttribute('checked');
  }

  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
}

/**
 * @function markWilsyCrmFilterSelection
 * @description Applies visible selected-state markers to a filter checkbox and its row.
 * @param {HTMLInputElement} input - Checkbox input element.
 * @returns {void}
 * @collaboration Leads selectable filters, Meetings selectable filters, filter sidebar evidence, and local UI control state.
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
 * @description Restores local filter selections after a CRM surface renders.
 * @returns {void}
 * @collaboration Leads and Meetings filter sidebars, selected-row styling, local test continuity, and safe read-only workflow.
 */
export function restoreWilsyCrmFilterSelections() {
  const storage = resolveWilsyCrmStorage();

  Array.from(document.querySelectorAll('input[type="checkbox"]')).forEach((input) => {
    if (storage) {
      try {
        const stored = storage.getItem(buildWilsyCrmFilterKey(input));
        if (stored === 'true' || stored === 'false') {
          setWilsyNativeCheckboxValue(input, stored === 'true');
        }
      } catch (error) {}
    }

    markWilsyCrmFilterSelection(input);
  });
}

/**
 * @function handleWilsyCrmCheckboxChange
 * @description Marks changed checkboxes after native/React state updates.
 * @param {Event} event - Browser change event.
 * @returns {void}
 * @collaboration CRM filter sidebars, checkbox tick visibility, selected-row styling, and local selection persistence.
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
 * @description Repairs custom checkbox rows where row clicks highlighted but did not tick the actual checkbox.
 * @param {MouseEvent} event - Browser click event.
 * @returns {void}
 * @collaboration Leads filter rows, Meetings filter rows, custom checkbox shells, native checked state, and visible operator feedback.
 */
export function handleWilsyCrmCheckboxClick(event) {
  const directInput = event.target?.closest?.('input[type="checkbox"]');

  if (directInput) {
    window.setTimeout(() => {
      markWilsyCrmFilterSelection(directInput);
      persistWilsyCrmFilterSelection(directInput);
    }, 0);
    return;
  }

  const clickable = event.target?.closest?.('label, li, div, button');

  if (!clickable) {
    return;
  }

  const input = clickable.querySelector?.('input[type="checkbox"]');

  if (!input || input.disabled) {
    return;
  }

  const text = normalizeWilsyCrmControlText(clickable.textContent);

  if (!/Record Action|Related Records Action|Touched Records|Untouched Records|Last Activity Time|Annual Revenue|Activities|Campaigns|Latest Email Status|System Defined Filters|Filter By Fields/i.test(text)) {
    return;
  }

  event.preventDefault();
  event.stopPropagation();

  setWilsyNativeCheckboxValue(input, !input.checked);
  markWilsyCrmFilterSelection(input);
  persistWilsyCrmFilterSelection(input);
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
 * @collaboration CRM Operating Controls, Setup map search, domain rail repair, and production control discovery.
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
  }, 5200);
}

/**
 * @function handleWilsyPlaceholderActionReceipt
 * @description Shows a governed disabled receipt for placeholder import actions instead of pretending they are connected.
 * @param {MouseEvent} event - Browser click event.
 * @returns {boolean} True when a placeholder action was intercepted.
 * @collaboration Import Leads, Import Notes, Meetings import placeholders, guided production hardening, and mutation prevention.
 */
export function handleWilsyPlaceholderActionReceipt(event) {
  const actionNode = event.target?.closest?.('button, a, [role="button"], [data-wilsy-action]');

  if (!actionNode) {
    return false;
  }

  const label = normalizeWilsyCrmControlText(actionNode.textContent || actionNode.getAttribute('aria-label'));

  if (!/Import Leads|Import Notes|Import Meetings|Import/i.test(label)) {
    return false;
  }

  event.preventDefault();
  event.stopPropagation();

  showWilsyCrmControlRepairReceipt(
    `${label} is blocked until the governed import workflow is built: manifest preview, validation ledger, evidence receipt, duplicate handling, and approval-safe commit.`,
    'PLACEHOLDER_IMPORT_BLOCKED',
  );

  return true;
}

/**
 * @function markWilsyMeetingReadinessPills
 * @description Centers meeting readiness score pill text and marks it as a readiness metric.
 * @returns {void}
 * @collaboration Meetings readiness score, table readability, score-pill alignment, and meeting success measurement UX.
 */
export function markWilsyMeetingReadinessPills() {
  const isMeetings = /Meetings|Meeting Operations/i.test(resolveWilsyPageTitle() + ' ' + document.body.textContent.slice(0, 1200));

  if (!isMeetings) {
    return;
  }

  Array.from(document.querySelectorAll('td, div, span, strong, button')).forEach((node) => {
    const text = normalizeWilsyCrmControlText(node.textContent);
    if (/^\d{1,3}%$/.test(text)) {
      node.dataset.wilsyMeetingReadinessPill = 'true';
    }
  });
}

/**
 * @function loadWilsyMeetingOutcomeCandidates
 * @description Loads local meeting outcome candidates.
 * @returns {Array} Meeting outcome candidates.
 * @collaboration Meeting completion, outcome capture, AI improvement candidates, local proof store, and future backend promotion.
 */
export function loadWilsyMeetingOutcomeCandidates() {
  const storage = resolveWilsyCrmStorage();

  if (!storage) {
    return [];
  }

  try {
    const parsed = JSON.parse(storage.getItem(WILSY_CRM_MEETING_OUTCOME_KEY) || '[]');
    return Array.isArray(parsed) ? parsed.slice(0, 80) : [];
  } catch (error) {
    return [];
  }
}

/**
 * @function saveWilsyMeetingOutcomeCandidate
 * @description Saves a local meeting outcome candidate for future backend/evidence route promotion.
 * @param {Object} candidate - Outcome candidate.
 * @returns {Array} Updated candidates.
 * @collaboration Meeting completion, success measurement, negative-result learning, AI preparation improvement, and governed data capture.
 */
export function saveWilsyMeetingOutcomeCandidate(candidate = {}) {
  const storage = resolveWilsyCrmStorage();
  const candidates = [
    {
      ...candidate,
      id: candidate.id || `meeting-outcome-${Date.now()}-${Math.floor(Math.random() * 100000)}`,
      generatedAt: candidate.generatedAt || new Date().toISOString(),
      status: 'OUTCOME_CAPTURED_PENDING_BACKEND_PROMOTION',
    },
    ...loadWilsyMeetingOutcomeCandidates(),
  ].slice(0, 80);

  if (storage) {
    try {
      storage.setItem(WILSY_CRM_MEETING_OUTCOME_KEY, JSON.stringify(candidates));
    } catch (error) {}
  }

  return candidates;
}

/**
 * @function countWilsySelectedMeetingRows
 * @description Counts selected meeting rows from checked table checkboxes.
 * @returns {number} Selected meeting row count.
 * @collaboration Meetings row selection, completion workflow, outcome capture, and safe local data collection.
 */
export function countWilsySelectedMeetingRows() {
  if (!/Meetings|Meeting Operations/i.test(resolveWilsyPageTitle() + ' ' + document.body.textContent.slice(0, 900))) {
    return 0;
  }

  return Array.from(document.querySelectorAll('table input[type="checkbox"], [role="row"] input[type="checkbox"]'))
    .filter((input) => input.checked)
    .length;
}

/**
 * @function renderWilsyMeetingOutcomeAction
 * @description Adds a Complete Meeting action to Meetings when row selection is active.
 * @returns {void}
 * @collaboration Meetings selected rows, completion workflow, outcome capture, success scoring, and AI improvement candidates.
 */
export function renderWilsyMeetingOutcomeAction() {
  const selectedCount = countWilsySelectedMeetingRows();
  const existing = document.querySelector('[data-wilsy-meeting-outcome-action="true"]');

  if (!selectedCount) {
    existing?.remove();
    return;
  }

  if (existing) {
    existing.querySelector('span').textContent = `Complete ${selectedCount} meeting${selectedCount === 1 ? '' : 's'}`;
    return;
  }

  const toolbar = Array.from(document.querySelectorAll('div, section, header'))
    .find((node) => /\d+\s+selected/i.test(normalizeWilsyCrmControlText(node.textContent)));

  if (!toolbar) {
    return;
  }

  const button = document.createElement('button');
  button.type = 'button';
  button.dataset.wilsyMeetingOutcomeAction = 'true';
  button.innerHTML = `<span>Complete ${selectedCount} meeting${selectedCount === 1 ? '' : 's'}</span><small>Capture outcome</small>`;
  button.addEventListener('click', () => showWilsyMeetingOutcomePanel(selectedCount));
  toolbar.appendChild(button);
}

/**
 * @function showWilsyMeetingOutcomePanel
 * @description Opens the meeting outcome capture panel.
 * @param {number} selectedCount - Selected meeting count.
 * @returns {void}
 * @collaboration Meeting completion, outcome data capture, negative-result learning, future AI preparation, and CRM readiness analytics.
 */
export function showWilsyMeetingOutcomePanel(selectedCount = 1) {
  let panel = document.querySelector('[data-wilsy-meeting-outcome-panel="true"]');

  if (!panel) {
    panel = document.createElement('aside');
    panel.setAttribute('data-wilsy-meeting-outcome-panel', 'true');
    document.body.appendChild(panel);
  }

  panel.innerHTML = `
    <div>
      <strong>Meeting outcome capture</strong>
      <button type="button" data-wilsy-meeting-outcome-close="true">Close</button>
    </div>
    <p>${selectedCount} selected meeting${selectedCount === 1 ? '' : 's'} · capture result data for future AI preparation.</p>
    <label>
      Outcome
      <select data-wilsy-meeting-outcome-status="true">
        <option value="SUCCESSFUL">Successful</option>
        <option value="FOLLOW_UP_REQUIRED">Follow-up required</option>
        <option value="NO_SHOW">No-show</option>
        <option value="NEGATIVE_RESULT">Negative result</option>
        <option value="CANCELLED">Cancelled</option>
      </select>
    </label>
    <label>
      Outcome notes
      <textarea data-wilsy-meeting-outcome-notes="true" placeholder="Capture decisions, objections, risks, promises, and next commitments..."></textarea>
    </label>
    <label>
      Next action
      <input data-wilsy-meeting-outcome-next-action="true" placeholder="Follow up, send proposal, schedule next meeting..." />
    </label>
    <button type="button" data-wilsy-meeting-outcome-save="true">Save outcome data</button>
  `;

  panel.querySelector('[data-wilsy-meeting-outcome-close="true"]')?.addEventListener('click', () => panel.remove());
  panel.querySelector('[data-wilsy-meeting-outcome-save="true"]')?.addEventListener('click', () => {
    const outcome = panel.querySelector('[data-wilsy-meeting-outcome-status="true"]')?.value || 'SUCCESSFUL';
    const notes = normalizeWilsyCrmControlText(panel.querySelector('[data-wilsy-meeting-outcome-notes="true"]')?.value);
    const nextAction = normalizeWilsyCrmControlText(panel.querySelector('[data-wilsy-meeting-outcome-next-action="true"]')?.value);

    saveWilsyMeetingOutcomeCandidate({
      selectedCount,
      outcome,
      notes,
      nextAction,
      successSignal: outcome === 'SUCCESSFUL' ? 100 : outcome === 'NEGATIVE_RESULT' || outcome === 'NO_SHOW' ? 15 : 62,
      improvementSignal: outcome === 'NEGATIVE_RESULT' || outcome === 'NO_SHOW' || outcome === 'FOLLOW_UP_REQUIRED',
      sourceSurface: 'Meetings',
    });

    showWilsyCrmControlRepairReceipt(
      `Meeting outcome saved locally as a learning candidate. Next production step: promote this through a backend receipt route for permanent CRM intelligence.`,
      'MEETING_OUTCOME_CAPTURED',
    );

    panel.remove();
  });
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
 * @function markWilsySetupRailAndStageLayout
 * @description Marks Setup rails and staged review containers for adaptive layout repair.
 * @returns {void}
 * @collaboration CRM Operating Controls, Setup map rail, Authority Graph, Stage Review, adaptive view area, and inspector readability.
 */
export function markWilsySetupRailAndStageLayout() {
  if (!/CRM Operating Controls|Setup map|Authority Graph/i.test(document.body.textContent.slice(0, 3000))) {
    return;
  }

  Array.from(document.querySelectorAll('aside, nav, section, article, div')).forEach((node) => {
    const text = normalizeWilsyCrmControlText(node.textContent);

    if (/Setup map|DOMAINS|Find controls/i.test(text)) {
      node.dataset.wilsySetupDomainRailRepaired = 'true';
    }

    if (/Hover Trust|Exposure|Queue|Authority Inspector|Source Intelligence/i.test(text)) {
      node.dataset.wilsySetupInspectorRailRepaired = 'true';
    }

    if (/Evidence required|Copy Workflow Receipt|Approval locked|Release locked|affected systems|Gate Control/i.test(text)) {
      node.dataset.wilsySetupAdaptiveStageRepaired = 'true';
    }
  });
}

/**
 * @function injectWilsyCrmControlRepairStyles
 * @description Injects control repair styles for checkboxes, meeting outcomes, setup rails, readiness labels, and adaptive stage layout.
 * @returns {void}
 * @collaboration Leads filters, Meetings completion, Setup left rail, stage review layout, and readable production control surfaces.
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
      appearance: none !important;
      width: 24px !important;
      height: 24px !important;
      display: inline-grid !important;
      place-items: center !important;
      border: 2px solid rgba(62, 255, 154, 0.9) !important;
      border-radius: 6px !important;
      background: rgba(62, 255, 154, 0.22) !important;
      box-shadow: 0 0 0 3px rgba(62, 255, 154, 0.16) !important;
    }

    input[type="checkbox"][data-wilsy-crm-filter-selected="true"]::after {
      content: "✓" !important;
      color: #06130d !important;
      width: 16px !important;
      height: 16px !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      border-radius: 4px !important;
      background: #3eff9a !important;
      font-size: 14px !important;
      font-weight: 1000 !important;
      line-height: 1 !important;
    }

    [data-wilsy-setup-search-visible="false"] {
      display: none !important;
    }

    [data-wilsy-meeting-readiness-pill="true"] {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      text-align: center !important;
      min-width: 92px !important;
      min-height: 54px !important;
      padding: 0 16px !important;
      line-height: 1 !important;
    }

    [data-wilsy-meeting-outcome-action="true"] {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 10px !important;
      min-height: 44px !important;
      padding: 0 18px !important;
      border: 1px solid rgba(62, 255, 154, 0.38) !important;
      border-radius: 14px !important;
      background: rgba(8, 45, 25, 0.88) !important;
      color: rgba(242, 255, 247, 0.98) !important;
      font-weight: 950 !important;
      cursor: pointer !important;
    }

    [data-wilsy-meeting-outcome-action="true"] small {
      color: rgba(255, 236, 180, 0.88) !important;
      font-size: 0.66rem !important;
      letter-spacing: 0.12em !important;
      text-transform: uppercase !important;
    }

    [data-wilsy-meeting-outcome-panel="true"] {
      position: fixed !important;
      right: 36px !important;
      bottom: 108px !important;
      z-index: 999998 !important;
      width: min(520px, calc(100vw - 48px)) !important;
      display: grid !important;
      gap: 14px !important;
      padding: 20px !important;
      border: 1px solid rgba(62, 255, 154, 0.36) !important;
      border-radius: 24px !important;
      background: rgba(5, 15, 23, 0.97) !important;
      color: rgba(245, 252, 255, 0.98) !important;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.48) !important;
    }

    [data-wilsy-meeting-outcome-panel="true"] > div {
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      gap: 12px !important;
    }

    [data-wilsy-meeting-outcome-panel="true"] label {
      display: grid !important;
      gap: 8px !important;
      color: rgba(255, 235, 179, 0.92) !important;
      font-size: 0.76rem !important;
      font-weight: 900 !important;
      letter-spacing: 0.12em !important;
      text-transform: uppercase !important;
    }

    [data-wilsy-meeting-outcome-panel="true"] select,
    [data-wilsy-meeting-outcome-panel="true"] input,
    [data-wilsy-meeting-outcome-panel="true"] textarea {
      width: 100% !important;
      border: 1px solid rgba(97, 147, 255, 0.24) !important;
      border-radius: 14px !important;
      background: rgba(8, 18, 31, 0.92) !important;
      color: rgba(245, 252, 255, 0.98) !important;
      padding: 12px 14px !important;
      font: inherit !important;
      text-transform: none !important;
    }

    [data-wilsy-meeting-outcome-panel="true"] textarea {
      min-height: 120px !important;
      resize: vertical !important;
    }

    [data-wilsy-meeting-outcome-panel="true"] button {
      border: 1px solid rgba(62, 255, 154, 0.34) !important;
      border-radius: 14px !important;
      background: rgba(8, 45, 25, 0.88) !important;
      color: rgba(245, 252, 255, 0.98) !important;
      padding: 12px 16px !important;
      font-weight: 950 !important;
      cursor: pointer !important;
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

    [data-wilsy-readiness-source-badge="true"] {
      display: inline-flex !important;
      width: fit-content !important;
      margin-top: 10px !important;
      padding: 6px 10px !important;
      border: 1px solid rgba(255, 218, 121, 0.28) !important;
      border-radius: 999px !important;
      color: rgba(255, 238, 173, 0.92) !important;
      font-size: 0.68rem !important;
      font-weight: 900 !important;
      letter-spacing: 0.09em !important;
      text-transform: uppercase !important;
    }

    [data-wilsy-setup-domain-rail-repaired="true"] {
      min-width: clamp(320px, 24vw, 430px) !important;
      overflow: visible !important;
      word-break: normal !important;
    }

    [data-wilsy-setup-domain-rail-repaired="true"] * {
      max-width: 100% !important;
      white-space: normal !important;
      overflow-wrap: anywhere !important;
    }

    [data-wilsy-setup-inspector-rail-repaired="true"] {
      min-width: clamp(250px, 18vw, 360px) !important;
      writing-mode: horizontal-tb !important;
      overflow: visible !important;
    }

    [data-wilsy-setup-inspector-rail-repaired="true"] * {
      writing-mode: horizontal-tb !important;
      text-orientation: mixed !important;
      white-space: normal !important;
      overflow-wrap: anywhere !important;
    }

    [data-wilsy-setup-adaptive-stage-repaired="true"] {
      min-height: auto !important;
      align-content: start !important;
      align-items: stretch !important;
    }

    [data-wilsy-setup-adaptive-stage-repaired="true"] > * {
      min-height: fit-content !important;
    }

    body:has([data-wilsy-setup-adaptive-stage-repaired="true"]) [class*="workspace"],
    body:has([data-wilsy-setup-adaptive-stage-repaired="true"]) [class*="Workspace"],
    body:has([data-wilsy-setup-adaptive-stage-repaired="true"]) [class*="canvas"],
    body:has([data-wilsy-setup-adaptive-stage-repaired="true"]) [class*="Canvas"] {
      min-height: auto !important;
      align-content: start !important;
    }
  `;

  document.head.appendChild(style);
}

/**
 * @function handleWilsyCrmControlClick
 * @description Handles placeholder import blocking, custom checkbox toggles, and meeting outcome actions.
 * @param {MouseEvent} event - Browser click event.
 * @returns {void}
 * @collaboration CRM action menus, import placeholders, filter checkbox repair, meeting outcome capture, and safe testing.
 */
export function handleWilsyCrmControlClick(event) {
  if (handleWilsyPlaceholderActionReceipt(event)) {
    return;
  }

  handleWilsyCrmCheckboxClick(event);

  window.setTimeout(() => {
    renderWilsyMeetingOutcomeAction();
  }, 80);
}

/**
 * @function refreshWilsyCrmControlRepairBridge
 * @description Re-applies repair state after React renders CRM surfaces.
 * @returns {void}
 * @collaboration CRM rendering, filter selection persistence, setup map search, meeting outcome action, readiness labelling, and rail containment.
 */
export function refreshWilsyCrmControlRepairBridge() {
  restoreWilsyCrmFilterSelections();
  markWilsyReadinessSourceStatus();
  markWilsyMeetingReadinessPills();
  markWilsySetupRailAndStageLayout();
  renderWilsyMeetingOutcomeAction();

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
 * @collaboration Leads, Meetings, CRM Setup, Wilsy AI, source readiness, meeting outcome learning, and CRM module hardening.
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
