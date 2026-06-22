/* eslint-disable */
import { buildWilsyR8FCommandRouteReceipt, resolveWilsyR8FCommandRouteContracts } from './wilsyAccountCommandRouteContracts';
/**
 * @fileoverview Wilsy Account Runtime Enhancers.
 * @description Extracted DOM-safe runtime enhancers for WilsyAccountCommandCenter. This file reduces component size without changing the Account Command Center contract.
 * @collaboration Keeps Wilsy OS Chrome runtime behavior side-effect compatible while preventing the Account component from becoming a monolith.
 */

export const WILSY_ACCOUNT_RUNTIME_ENHANCERS_VERSION = 'R8A-ACCOUNT-RUNTIME-EXTRACTION';

/* WILSY_R8A_ACCOUNT_RUNTIME_ENHANCERS */

/**
 * @function deriveWilsyR7CInitials
 * @description Derives compact command initials for the Account Command Identity capsule.
 * @param {string} displayName - Account display name.
 * @returns {string} Command initials.
 * @collaboration Keeps Wilsy OS identity chrome compact without duplicating profile text.
 */
function deriveWilsyR7CInitials(displayName) {
  const safeName = String(displayName || '').trim();
  const parts = safeName.split(/\s+/).filter(Boolean);

  if (parts.length >= 2) {
    return `${parts[0][0] || ''}${parts[parts.length - 1][0] || ''}`.toUpperCase();
  }

  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }

  return 'WK';
}

/**
 * @function resolveWilsyR7CIdentityValues
 * @description Reads live identity values from the existing Account Command Center DOM.
 * @param {HTMLElement} card - Existing identity card element.
 * @returns {{name: string, account: string, tenant: string, initials: string}} Resolved values.
 * @collaboration Allows the new chrome renderer to use real runtime values instead of hardcoded text.
 */
function resolveWilsyR7CIdentityValues(card) {
  const heading = card.querySelector('h1, h2, h3');
  const select = card.querySelector('select');
  const cardText = card.textContent || '';
  const accountMatch = cardText.match(/Account:\s*Ref\s+[A-Za-z0-9._-]+(?:…|\.\.\.)?[A-Za-z0-9._-]*/i);

  const name = (heading?.textContent || '').replace(/\s+/g, ' ').trim() || 'Wilsy Operator';
  const account = (accountMatch?.[0] || 'Account: verified session').replace(/\s+/g, ' ').trim();
  const tenant = (select?.selectedOptions?.[0]?.textContent || select?.value || 'Wilsy OS Root').replace(/\s+/g, ' ').trim();

  return {
    name,
    account,
    tenant,
    initials: deriveWilsyR7CInitials(name)
  };
}

/**
 * @function buildWilsyR7CTextNode
 * @description Builds a text element for the reference identity renderer.
 * @param {string} tagName - Element tag name.
 * @param {string} className - CSS class name.
 * @param {string} value - Text content.
 * @returns {HTMLElement} Built element.
 * @collaboration Prevents unsafe HTML injection while keeping the runtime renderer dynamic.
 */
function buildWilsyR7CTextNode(tagName, className, value) {
  const node = document.createElement(tagName);
  node.className = className;
  node.textContent = value;
  return node;
}


/**
 * @function deriveWilsyR7FIdentitySeal
 * @description Creates a deterministic forensic identity seal from live account identity values.
 * @param {{name: string, account: string, tenant: string}} values - Resolved identity values.
 * @returns {string} Deterministic identity seal.
 * @collaboration Adds forensic proof to the identity capsule without hardcoded fake backend data.
 */
function deriveWilsyR7FIdentitySeal(values) {
  const input = `${values?.name || ''}|${values?.account || ''}|${values?.tenant || ''}`;
  let hash = 2166136261;

  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return `CID-${(hash >>> 0).toString(16).toUpperCase().slice(0, 8)}`;
}

/**
 * @function renderWilsyR7CIdentityCard
 * @description Renders a clean reference-grade Wilsy OS identity layer over the legacy identity DOM.
 * @param {HTMLElement} card - Existing identity card element.
 * @returns {void}
 * @collaboration Eliminates overlapping legacy internals while preserving the real tenant select control.
 */
function renderWilsyR7CIdentityCard(card) {

  if (!(card instanceof HTMLElement)) {
    return;
  }

  card.querySelectorAll('[data-wilsy-r7c-identity-ui="true"]').forEach(shell => shell.remove());
  delete card.dataset.wilsyR7cIdentityCard;
  delete card.dataset.wilsyR7cIdentitySignature;
  card.removeAttribute('data-wilsy-r7c-identity-card');
  card.style.removeProperty('overflow');
}

/**
 * @function stampWilsyR7CReferenceIdentityChrome
 * @description Finds Account identity cards and renders the reference-grade identity chrome layer.
 * @returns {void}
 * @collaboration Makes Account identity responsive, non-overlapping, and runtime-value driven.
 */
function stampWilsyR7CReferenceIdentityChrome() {

  if (typeof document === 'undefined') {
    return;
  }

  document.querySelectorAll('[data-wilsy-identity-chrome]').forEach(card => {
    if (card instanceof HTMLElement) {
      renderWilsyR7CIdentityCard(card);
    }
  });
}

/**
 * @function bootWilsyR7CReferenceIdentityRuntime
 * @description Boots a lightweight DOM observer that keeps reference identity chrome aligned with live tenant changes.
 * @returns {void}
 * @collaboration Preserves tenant switching while preventing React state loops.
 */
function bootWilsyR7CReferenceIdentityRuntime() {

  if (typeof window === 'undefined' || window.__WILSY_R9J_ORIGINAL_IDENTITY_CARD_RESTORE__) {
    return;
  }

  window.__WILSY_R9J_ORIGINAL_IDENTITY_CARD_RESTORE__ = true;

/**
   * @function schedule
   * @description Schedules a bounded restored Command Identity render pass without using document-level observers.
   * @collaboration Preserves the R9M/R9N restored Account Command Center identity shell and chrome mandate compliance.
   */
    const schedule = () => window.requestAnimationFrame(stampWilsyR7CReferenceIdentityChrome);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', schedule, { once: true });
  } else {
    schedule();
  }

  [80, 240, 600, 1200, 2200].forEach(delay => {
    window.setTimeout(schedule, delay);
  });

  window.addEventListener('wilsy-theme-runtime-applied', schedule);
  window.addEventListener('resize', schedule);
}

// WILSY_R9I_ORIGINAL_IDENTITY_CARD_RESTORE: disabled R7C replacement shell; React identity DOM is canonical.
// // WILSY_R9K_ORIGINAL_REACT_IDENTITY_VISIBLE_FIX: R7C replacement shell remains disabled.
// // WILSY_R9L_FINAL_IDENTITY_CARD_REPLACEMENT: R7C fake shell disabled; JSX card is canonical.
// // WILSY_R9M_PRESPLIT_ACCOUNT_RESTORE: external R7C replacement shell disabled; restored Account JSX is canonical.
// bootWilsyR7CReferenceIdentityRuntime();
/**
 * @function buildWilsyR7EEvidenceSeal
 * @description Builds a deterministic short forensic seal from signal text without using hardcoded IDs.
 * @param {string} value - Source value for the seal.
 * @returns {string} Deterministic seal.
 * @collaboration Gives each command signal a visible audit proof marker without inventing backend data.
 */
function buildWilsyR7EEvidenceSeal(value) {
  const input = String(value || 'wilsy-signal').trim();
  let hash = 2166136261;

  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return `SIG-${(hash >>> 0).toString(16).toUpperCase().slice(0, 8)}`;
}

/**
 * @function resolveWilsyR7ESignalProfile
 * @description Resolves evidence anchor, telemetry copy, and priority metadata for a cockpit signal card.
 * @param {string} label - Signal label.
 * @param {string} title - Signal title.
 * @param {string} body - Signal body.
 * @returns {{anchor: string, telemetry: string, priority: string, narrative: string}} Signal profile.
 * @collaboration Converts static-looking cards into forensic, role-aware command evidence surfaces.
 */
function resolveWilsyR7ESignalProfile(label, title, body) {
  const normalized = String(label || '').toLowerCase();
  const combined = `${label} ${title} ${body}`.toLowerCase();

  if (normalized.includes('tier')) {
    return {
      anchor: 'WILSY-GOV-TIER-001',
      telemetry: 'Tier posture verified from active tenant context',
      priority: 'primary',
      narrative: 'Defines the operating tier that governs command permissions, dashboard reach, and executive visibility.'
    };
  }

  if (normalized.includes('authority')) {
    return {
      anchor: 'WILSY-AUTH-SCOPE-002',
      telemetry: 'Authority scope bound to tenant command session',
      priority: 'high',
      narrative: 'Controls who may operate tenant identity, routes, receipts, and account-level command settings.'
    };
  }

  if (normalized.includes('identity')) {
    return {
      anchor: 'WILSY-ID-SESSION-003',
      telemetry: 'Identity session is tenant-bound and live',
      priority: 'high',
      narrative: 'Confirms the operator is bound to the active tenant context before command actions are trusted.'
    };
  }

  if (normalized.includes('reach') || combined.includes('backend pending')) {
    return {
      anchor: 'WILSY-API-REACH-004',
      telemetry: combined.includes('pending')
        ? 'Awaiting account intelligence endpoint'
        : 'Backend telemetry active',
      priority: combined.includes('pending') ? 'watch' : 'active',
      narrative: 'Tracks whether the command layer is receiving live backend intelligence or operating from local context.'
    };
  }

  return {
    anchor: 'WILSY-SIGNAL-000',
    telemetry: 'Signal available from current command context',
    priority: 'standard',
    narrative: 'Command signal is visible and ready for inspection.'
  };
}

/**
 * @function stampWilsyR7ESignalTile
 * @description Adds evidence, telemetry, priority, and drilldown affordances to a signal tile.
 * @param {HTMLElement} tile - Signal tile element.
 * @returns {void}
 * @collaboration Turns each cockpit card into an inspectable Wilsy OS evidence surface.
 */
function stampWilsyR7ESignalTile(tile) {
  const label = tile.querySelector('span')?.textContent?.trim() || 'Signal';
  const title = tile.querySelector('strong')?.textContent?.trim() || 'Command Signal';
  const body = tile.querySelector('small')?.textContent?.trim() || 'Context data active';
  const profile = resolveWilsyR7ESignalProfile(label, title, body);
  const seal = buildWilsyR7EEvidenceSeal(`${label}|${title}|${body}|${profile.anchor}`);

  tile.dataset.wilsyR7eSignalTile = 'true';
  tile.dataset.wilsyR7ePriority = profile.priority;
  tile.dataset.wilsyEvidenceAnchor = profile.anchor;
  tile.dataset.wilsyEvidenceSeal = seal;
  tile.dataset.wilsyTelemetryState = profile.telemetry;
  tile.dataset.wilsySignalNarrative = profile.narrative;

  tile.setAttribute('role', 'button');
  tile.setAttribute('tabindex', '0');
  tile.setAttribute('aria-label', `${label}: ${title}. ${profile.telemetry}.`);

  let evidence = tile.querySelector('[data-wilsy-r7e-evidence="true"]');

  if (!evidence) {
    evidence = document.createElement('div');
    evidence.setAttribute('data-wilsy-r7e-evidence', 'true');
    tile.appendChild(evidence);
  }

  evidence.replaceChildren();

  const anchorNode = document.createElement('span');
  anchorNode.className = 'wilsy-r7e-evidence-anchor';
  anchorNode.textContent = profile.anchor;

  const sealNode = document.createElement('span');
  sealNode.className = 'wilsy-r7e-evidence-seal';
  sealNode.textContent = seal;

  evidence.append(anchorNode, sealNode);
}

/**
 * @function ensureWilsyR7EDrilldownOverlay
 * @description Creates or returns the signal drilldown overlay element.
 * @returns {HTMLElement} Drilldown overlay.
 * @collaboration Gives command signals a sovereign overlay instead of abrupt unstructured clicks.
 */
function ensureWilsyR7EDrilldownOverlay() {
  let overlay = document.querySelector('[data-wilsy-r7e-signal-overlay="true"]');

  if (overlay instanceof HTMLElement) {
    return overlay;
  }

  overlay = document.createElement('div');
  overlay.setAttribute('data-wilsy-r7e-signal-overlay', 'true');
  overlay.hidden = true;

  const panel = document.createElement('section');
  panel.className = 'wilsy-r7e-signal-panel';

  const closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.className = 'wilsy-r7e-signal-close';
  closeButton.textContent = 'Close';

  const eyebrow = document.createElement('div');
  eyebrow.className = 'wilsy-r7e-signal-eyebrow';

  const title = document.createElement('h3');
  title.className = 'wilsy-r7e-signal-title';

  const narrative = document.createElement('p');
  narrative.className = 'wilsy-r7e-signal-narrative';

  const telemetry = document.createElement('p');
  telemetry.className = 'wilsy-r7e-signal-telemetry';

  const evidence = document.createElement('code');
  evidence.className = 'wilsy-r7e-signal-evidence';

  panel.append(closeButton, eyebrow, title, narrative, telemetry, evidence);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);

  closeButton.addEventListener('click', closeWilsyR7ESignalDrilldown);
  overlay.addEventListener('click', event => {
    if (event.target === overlay) {
      closeWilsyR7ESignalDrilldown();
    }
  });

  return overlay;
}

/**
 * @function closeWilsyR7ESignalDrilldown
 * @description Closes the signal drilldown overlay.
 * @returns {void}
 * @collaboration Keeps cockpit overlays anchored and reversible.
 */
function closeWilsyR7ESignalDrilldown() {
  const overlay = document.querySelector('[data-wilsy-r7e-signal-overlay="true"]');

  if (overlay instanceof HTMLElement) {
    overlay.hidden = true;
    overlay.dataset.wilsyR7eOpen = 'false';
  }
}

/**
 * @function openWilsyR7ESignalDrilldown
 * @description Opens a forensic drilldown panel for a command signal tile.
 * @param {HTMLElement} tile - Signal tile element.
 * @returns {void}
 * @collaboration Provides evidence anchoring and command narrative without pretending backend data exists.
 */
function openWilsyR7ESignalDrilldown(tile) {
  const overlay = ensureWilsyR7EDrilldownOverlay();
  const label = tile.querySelector('span')?.textContent?.trim() || 'Signal';
  const title = tile.querySelector('strong')?.textContent?.trim() || 'Command Signal';

  overlay.querySelector('.wilsy-r7e-signal-eyebrow').textContent = `${label} • ${tile.dataset.wilsyR7ePriority || 'standard'} priority`;
  overlay.querySelector('.wilsy-r7e-signal-title').textContent = title;
  overlay.querySelector('.wilsy-r7e-signal-narrative').textContent = tile.dataset.wilsySignalNarrative || 'Command signal is ready for inspection.';
  overlay.querySelector('.wilsy-r7e-signal-telemetry').textContent = tile.dataset.wilsyTelemetryState || 'Telemetry pending.';
  overlay.querySelector('.wilsy-r7e-signal-evidence').textContent = `${tile.dataset.wilsyEvidenceAnchor || 'WILSY-SIGNAL'} • ${tile.dataset.wilsyEvidenceSeal || 'SIG-PENDING'}`;

  overlay.hidden = false;
  overlay.dataset.wilsyR7eOpen = 'true';
}

/**
 * @function stampWilsyR7ESignalIntelligence
 * @description Stamps all Account Command signal cards with evidence metadata and interaction affordances.
 * @returns {void}
 * @collaboration Makes Wilsy OS signal cards evidence-ready and telemetry-aware.
 */
function stampWilsyR7ESignalIntelligence() {
  if (typeof document === 'undefined') {
    return;
  }

  document.querySelectorAll('[data-wilsy-role~="account-story-tile"]').forEach(tile => {
    if (tile instanceof HTMLElement) {
      stampWilsyR7ESignalTile(tile);
    }
  });
}

/**
 * @function scheduleWilsyR7ESignalIntelligence
 * @description Schedules signal intelligence stamping on the next animation frame.
 * @returns {number | void} Animation frame identifier when available.
 * @collaboration Keeps evidence stamping lightweight and separate from React rendering.
 */
function scheduleWilsyR7ESignalIntelligence() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR7ESignalIntelligence);
}

/**
 * @function bootWilsyR7ESignalIntelligenceRuntime
 * @description Boots the signal intelligence observer and click handlers once.
 * @returns {void}
 * @collaboration Adds sovereign drilldown behavior without React state churn.
 */
function bootWilsyR7ESignalIntelligenceRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R7E_SIGNAL_INTELLIGENCE_RUNTIME__) {
    return;
  }

  window.__WILSY_R7E_SIGNAL_INTELLIGENCE_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleWilsyR7ESignalIntelligence, { once: true });
  } else {
    scheduleWilsyR7ESignalIntelligence();
  }
  /* WILSY_R7J_PERFORMANCE_SAFE: broad document MutationObserver removed to prevent page-freeze observer storms. */

  document.addEventListener('click', event => {
    const tile = event.target instanceof Element
      ? event.target.closest('[data-wilsy-r7e-signal-tile="true"]')
      : null;

    if (tile instanceof HTMLElement) {
      openWilsyR7ESignalDrilldown(tile);
    }
  });

  document.addEventListener('keydown', event => {
    const tile = event.target instanceof Element
      ? event.target.closest('[data-wilsy-r7e-signal-tile="true"]')
      : null;

    if (!(tile instanceof HTMLElement)) {
      return;
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openWilsyR7ESignalDrilldown(tile);
    }

    if (event.key === 'Escape') {
      closeWilsyR7ESignalDrilldown();
    }
  });

  window.addEventListener('wilsy-theme-runtime-applied', scheduleWilsyR7ESignalIntelligence);
  window.addEventListener('resize', scheduleWilsyR7ESignalIntelligence);
}

bootWilsyR7ESignalIntelligenceRuntime();
/**
 * @function resolveWilsyR7HTabLabel
 * @description Resolves the readable label for a cockpit navigation tab button.
 * @param {HTMLElement} button - Candidate tab button.
 * @returns {string} Normalized tab label.
 * @collaboration Lets Wilsy OS mark the active cockpit tab without coupling to fragile CSS class names.
 */
function resolveWilsyR7HTabLabel(button) {
  return String(button?.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function setWilsyR7HActiveTab
 * @description Marks one Account cockpit tab as the active authority tab and demotes sibling tabs.
 * @param {HTMLElement} activeButton - Button to mark as active.
 * @returns {void}
 * @collaboration Provides persistent cockpit clarity after the user switches Account sections.
 */
function setWilsyR7HActiveTab(activeButton) {
  const tabRail = activeButton?.closest?.('[data-wilsy-role~="account-command-tabs"]');

  if (!(tabRail instanceof HTMLElement)) {
    return;
  }

  tabRail.querySelectorAll('button').forEach(button => {
    const isActive = button === activeButton;

    button.dataset.wilsyR7hTabButton = 'true';
    button.dataset.wilsyR7hActiveTab = isActive ? 'true' : 'false';
    button.setAttribute('aria-current', isActive ? 'page' : 'false');
  });
}

/**
 * @function stampWilsyR7HNavigationRail
 * @description Stamps Account cockpit navigation buttons with active-state metadata.
 * @returns {void}
 * @collaboration Ensures Preferences, My Account, Security, and Compliance communicate state like OS cockpit controls.
 */
function stampWilsyR7HNavigationRail() {
  if (typeof document === 'undefined') {
    return;
  }

  document.querySelectorAll('[data-wilsy-role~="account-command-tabs"]').forEach(tabRail => {
    if (!(tabRail instanceof HTMLElement)) {
      return;
    }

    const buttons = Array.from(tabRail.querySelectorAll('button')).filter(button => button instanceof HTMLElement);

    if (buttons.length === 0) {
      return;
    }

    buttons.forEach(button => {
      button.dataset.wilsyR7hTabButton = 'true';
    });

    const alreadyActive = buttons.find(button => button.dataset.wilsyR7hActiveTab === 'true');
    const ariaActive = buttons.find(button => (
      button.getAttribute('aria-selected') === 'true'
      || button.getAttribute('aria-current') === 'page'
      || button.dataset.active === 'true'
    ));

    const fallbackPreferences = buttons.find(button => /preferences/i.test(resolveWilsyR7HTabLabel(button)));
    setWilsyR7HActiveTab(alreadyActive || ariaActive || fallbackPreferences || buttons[0]);
  });
}

/**
 * @function resolveWilsyR7HModeCopy
 * @description Returns executive-readable copy for a Wilsy OS operating mode.
 * @param {string} modeId - Mode identifier.
 * @returns {{label: string, meta: string}} Mode label and explanatory copy.
 * @collaboration Gives Day, Night, and Auto controls operational meaning instead of unlabeled icon behavior.
 */
function resolveWilsyR7HModeCopy(modeId) {
  const normalized = String(modeId || '').toLowerCase();

  if (normalized.includes('day')) {
    return {
      label: 'Day Command',
      meta: 'Boardroom clarity for bright environments.'
    };
  }

  if (normalized.includes('auto')) {
    return {
      label: 'Auto Command',
      meta: 'Wilsy OS adapts visibility to system rhythm.'
    };
  }

  return {
    label: 'Night Command',
    meta: 'Low-light cockpit contrast for command focus.'
  };
}

/**
 * @function resolveWilsyR7HCurrentMode
 * @description Reads the visible Account mode badge and resolves the active mode.
 * @returns {string} Active mode identifier.
 * @collaboration Keeps the active mode badge honest and aligned with the existing UI state.
 */
function resolveWilsyR7HCurrentMode() {
  if (typeof document === 'undefined') {
    return 'night';
  }

  const candidates = Array.from(document.querySelectorAll('[data-wilsy-account-command-center="true"] *'));
  const badge = candidates.find(element => {
    const text = String(element.textContent || '').trim().toLowerCase();
    return ['day', 'night', 'auto'].includes(text) && element.children.length === 0;
  });

  const text = String(badge?.textContent || 'night').trim().toLowerCase();

  if (text.includes('day')) {
    return 'day';
  }

  if (text.includes('auto')) {
    return 'auto';
  }

  return 'night';
}

/**
 * @function stampWilsyR7HModeControls
 * @description Adds readable mode metadata and active-state markers to Day, Night, and Auto controls.
 * @returns {void}
 * @collaboration Makes Operating Preferences communicate the consequence of each operating mode.
 */
function stampWilsyR7HModeControls() {
  if (typeof document === 'undefined') {
    return;
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return;
  }

  const currentMode = resolveWilsyR7HCurrentMode();

  root.querySelectorAll('*').forEach(element => {
    const exactText = String(element.textContent || '').trim().toLowerCase();

    if (['day', 'night', 'auto'].includes(exactText) && element.children.length === 0) {
      element.dataset.wilsyR7hModeStateBadge = 'true';
      element.dataset.wilsyR7hModeState = exactText;
    }
  });

  root.querySelectorAll('button').forEach(button => {
    const buttonText = String(button.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();

    if (!/(day command|night command|auto command)/i.test(buttonText)) {
      return;
    }

    const modeId = buttonText.includes('day')
      ? 'day'
      : buttonText.includes('auto')
        ? 'auto'
        : 'night';

    const modeCopy = resolveWilsyR7HModeCopy(modeId);

    button.dataset.wilsyR7hModeOption = modeId;
    button.dataset.wilsyR7hActiveMode = modeId === currentMode ? 'true' : 'false';
    button.setAttribute('aria-label', `${modeCopy.label}. ${modeCopy.meta}`);

    let meta = button.querySelector('[data-wilsy-r7h-mode-meta="true"]');

    if (!meta) {
      meta = document.createElement('span');
      meta.setAttribute('data-wilsy-r7h-mode-meta', 'true');
      button.appendChild(meta);
    }

    meta.textContent = modeCopy.meta;
  });

  Array.from(root.querySelectorAll('*')).forEach(element => {
    const text = String(element.textContent || '').trim();

    if (text === 'Operating Preferences') {
      element.dataset.wilsyR7hPreferencesTitle = 'true';
    }

    if (/Control how Wilsy OS communicates contrast/i.test(text)) {
      element.dataset.wilsyR7hPreferencesDescription = 'true';
    }
  });
}

/**
 * @function scheduleWilsyR7HPreferenceChrome
 * @description Schedules Account preference chrome stamping on the next animation frame.
 * @returns {number | undefined} Animation frame identifier when available.
 * @collaboration Keeps navigation and mode metadata updates lightweight and separate from React rendering.
 */
function scheduleWilsyR7HPreferenceChrome() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(() => {
    stampWilsyR7HNavigationRail();
    stampWilsyR7HModeControls();
  });
}

/**
 * @function bootWilsyR7HPreferenceChromeRuntime
 * @description Boots Account preference navigation and mode authority stamping once.
 * @returns {void}
 * @collaboration Gives Operating Preferences persistent OS-level state clarity without fragile component rewrites.
 */
function bootWilsyR7HPreferenceChromeRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R7H_PREFERENCE_CHROME_RUNTIME__) {
    return;
  }

  window.__WILSY_R7H_PREFERENCE_CHROME_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleWilsyR7HPreferenceChrome, { once: true });
  } else {
    scheduleWilsyR7HPreferenceChrome();
  }

  document.addEventListener('click', event => {
    const tabButton = event.target instanceof Element
      ? event.target.closest('[data-wilsy-role~="account-command-tabs"] button')
      : null;

    if (tabButton instanceof HTMLElement) {
      window.requestAnimationFrame(() => setWilsyR7HActiveTab(tabButton));
    }

    const modeButton = event.target instanceof Element
      ? event.target.closest('[data-wilsy-r7h-mode-option]')
      : null;

    if (modeButton instanceof HTMLElement) {
      window.requestAnimationFrame(stampWilsyR7HModeControls);
    }
  });
  /* WILSY_R7J_PERFORMANCE_SAFE: broad document MutationObserver removed to prevent page-freeze observer storms. */

  window.addEventListener('wilsy-theme-runtime-applied', scheduleWilsyR7HPreferenceChrome);
  window.addEventListener('resize', scheduleWilsyR7HPreferenceChrome);
}

bootWilsyR7HPreferenceChromeRuntime();
/**
 * @function normalizeWilsyR7IModeId
 * @description Normalizes visible mode copy into a Wilsy OS command mode identifier.
 * @param {string} value - Visible mode text or raw mode id.
 * @returns {'day' | 'night' | 'auto'} Normalized mode identifier.
 * @collaboration Keeps the Day, Night, and Auto command rail independent from fragile class names.
 */
function normalizeWilsyR7IModeId(value) {
  const normalized = String(value || '').toLowerCase();

  if (normalized.includes('day')) {
    return 'day';
  }

  if (normalized.includes('auto') || normalized.includes('system')) {
    return 'auto';
  }

  return 'night';
}

/**
 * @function resolveWilsyR7IModeDescription
 * @description Returns operating meaning for each Wilsy OS command mode.
 * @param {'day' | 'night' | 'auto'} modeId - Normalized mode identifier.
 * @returns {string} Executive-readable mode description.
 * @collaboration Makes mode buttons communicate operational posture instead of behaving like unlabeled toggles.
 */
function resolveWilsyR7IModeDescription(modeId) {
  if (modeId === 'day') {
    return 'Bright-room clarity for executive review.';
  }

  if (modeId === 'auto') {
    return 'Adapts command visibility to system rhythm.';
  }

  return 'Low-light command focus with maximum contrast.';
}

/**
 * @function resolveWilsyR7ICurrentMode
 * @description Reads the current operating mode from visible Account UI and persisted runtime state.
 * @returns {'day' | 'night' | 'auto'} Current command mode.
 * @collaboration Keeps the active mode indicator aligned with user selection and existing theme runtime.
 */
function resolveWilsyR7ICurrentMode() {
  if (typeof document === 'undefined') {
    return 'night';
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return 'night';
  }

  const bodyMode = document.body?.dataset?.wilsyThemeMode
    || document.body?.dataset?.wilsyResolvedMode
    || document.documentElement?.dataset?.wilsyThemeMode
    || '';

  if (bodyMode) {
    return normalizeWilsyR7IModeId(bodyMode);
  }

  const possibleModeBadge = Array.from(root.querySelectorAll('*')).find(element => {
    const text = String(element.textContent || '').trim().toLowerCase();
    return ['day', 'night', 'auto'].includes(text) && element.children.length === 0;
  });

  if (possibleModeBadge) {
    return normalizeWilsyR7IModeId(possibleModeBadge.textContent || 'night');
  }

  const stored = window.localStorage?.getItem?.('wilsyThemeMode')
    || window.localStorage?.getItem?.('wilsy-mode')
    || window.localStorage?.getItem?.('wilsyAccountMode')
    || '';

  return normalizeWilsyR7IModeId(stored || 'night');
}

/**
 * @function resolveWilsyR7IModeButtons
 * @description Finds the Day, Night, and Auto command buttons in the Account preference view.
 * @returns {HTMLElement[]} Mode button elements.
 * @collaboration Avoids brittle selector assumptions while preserving the current component structure.
 */
function resolveWilsyR7IModeButtons() {
  if (typeof document === 'undefined') {
    return [];
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return [];
  }

  return Array.from(root.querySelectorAll('button')).filter(button => {
    const text = String(button.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
    return text.includes('day command') || text.includes('night command') || text.includes('auto command');
  });
}

/**
 * @function stampWilsyR7IModeButton
 * @description Stamps a mode button with mode identity, active state, description, and indicator metadata.
 * @param {HTMLElement} button - Mode button element.
 * @param {'day' | 'night' | 'auto'} activeMode - Current active mode.
 * @returns {void}
 * @collaboration Turns each mode control into a sovereign cockpit command selector.
 */
function stampWilsyR7IModeButton(button, activeMode) {
  const buttonText = String(button.textContent || '').replace(/\s+/g, ' ').trim();
  const modeId = normalizeWilsyR7IModeId(buttonText);
  const description = resolveWilsyR7IModeDescription(modeId);
  const isActive = modeId === activeMode;

  button.dataset.wilsyR7iModeButton = 'true';
  button.dataset.wilsyR7iModeId = modeId;
  button.dataset.wilsyR7iActiveMode = isActive ? 'true' : 'false';
  button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
  button.setAttribute('aria-label', `${modeId.toUpperCase()} command mode. ${description}`);

  const childNodes = Array.from(button.childNodes);
  childNodes.forEach(node => {
    if (node.nodeType === Node.TEXT_NODE && node.textContent && node.textContent.trim()) {
      const label = document.createElement('span');
      label.setAttribute('data-wilsy-r7i-mode-label', 'true');
      label.textContent = node.textContent.trim();
      button.replaceChild(label, node);
    }
  });

  let labelNode = button.querySelector('[data-wilsy-r7i-mode-label="true"]');

  if (!(labelNode instanceof HTMLElement)) {
    const possibleLabel = Array.from(button.querySelectorAll('span, strong, div')).find(element => {
      const text = String(element.textContent || '').trim().toLowerCase();
      return text.includes('day command') || text.includes('night command') || text.includes('auto command');
    });

    if (possibleLabel instanceof HTMLElement) {
      possibleLabel.setAttribute('data-wilsy-r7i-mode-label', 'true');
      labelNode = possibleLabel;
    }
  }

  let metaNode = button.querySelector('[data-wilsy-r7i-mode-description="true"]');

  if (!(metaNode instanceof HTMLElement)) {
    metaNode = document.createElement('span');
    metaNode.setAttribute('data-wilsy-r7i-mode-description', 'true');
    button.appendChild(metaNode);
  }

  metaNode.textContent = description;

  let indicator = button.querySelector('[data-wilsy-r7i-mode-indicator="true"]');

  if (!(indicator instanceof HTMLElement)) {
    indicator = document.createElement('span');
    indicator.setAttribute('data-wilsy-r7i-mode-indicator', 'true');
    button.appendChild(indicator);
  }

  indicator.setAttribute('aria-hidden', 'true');
}

/**
 * @function stampWilsyR7IModeSelector
 * @description Applies active-state authority to the Account Day, Night, and Auto mode selector.
 * @returns {void}
 * @collaboration Keeps the active operating mode visually sovereign across theme switches.
 */
function stampWilsyR7IModeSelector() {
  const activeMode = resolveWilsyR7ICurrentMode();
  const buttons = resolveWilsyR7IModeButtons();

  buttons.forEach(button => {
    stampWilsyR7IModeButton(button, activeMode);
  });
}

/**
 * @function queueWilsyR7IModeSelectorStamp
 * @description Queues mode selector stamping on the browser animation frame.
 * @returns {number | undefined} Animation frame request identifier when available.
 * @collaboration Keeps mode selector updates smooth without React state churn.
 */
function queueWilsyR7IModeSelectorStamp() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR7IModeSelector);
}

/**
 * @function bootWilsyR7IModeSelectorRuntime
 * @description Boots the Wilsy OS sovereign mode selector runtime once.
 * @returns {void}
 * @collaboration Preserves active-state authority for Day, Night, and Auto command modes.
 */
function bootWilsyR7IModeSelectorRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R7I_MODE_SELECTOR_RUNTIME__) {
    return;
  }

  window.__WILSY_R7I_MODE_SELECTOR_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR7IModeSelectorStamp, { once: true });
  } else {
    queueWilsyR7IModeSelectorStamp();
  }

  document.addEventListener('click', event => {
    const button = event.target instanceof Element
      ? event.target.closest('[data-wilsy-r7i-mode-button="true"], button')
      : null;

    if (!(button instanceof HTMLElement)) {
      return;
    }

    const text = String(button.textContent || '').toLowerCase();

    if (!text.includes('day command') && !text.includes('night command') && !text.includes('auto command')) {
      return;
    }

    const selectedMode = normalizeWilsyR7IModeId(text);

    button.closest('[data-wilsy-account-command-center="true"]')?.querySelectorAll('[data-wilsy-r7i-mode-button="true"]').forEach(candidate => {
      if (candidate instanceof HTMLElement) {
        const candidateMode = candidate.dataset.wilsyR7iModeId || normalizeWilsyR7IModeId(candidate.textContent || '');
        candidate.dataset.wilsyR7iActiveMode = candidateMode === selectedMode ? 'true' : 'false';
        candidate.setAttribute('aria-pressed', candidateMode === selectedMode ? 'true' : 'false');
      }
    });

    queueWilsyR7IModeSelectorStamp();
  });
  /* WILSY_R7J_PERFORMANCE_SAFE: broad document MutationObserver removed to prevent page-freeze observer storms. */

  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR7IModeSelectorStamp);
  window.addEventListener('resize', queueWilsyR7IModeSelectorStamp);
}

bootWilsyR7IModeSelectorRuntime();
/**
 * @function dispatchWilsyR7JPerformanceSafeRestamp
 * @description Dispatches a scoped event for Wilsy OS chrome stampers without using broad document MutationObservers.
 * @returns {void}
 * @collaboration Prevents browser freeze while keeping Account chrome responsive to explicit lifecycle events.
 */
function dispatchWilsyR7JPerformanceSafeRestamp() {
  if (typeof window === 'undefined') {
    return;
  }

  window.requestAnimationFrame(() => {
    window.dispatchEvent(new CustomEvent('wilsy-r7j-performance-safe-restamp'));
  });
}

if (typeof window !== 'undefined' && !window.__WILSY_R7J_PERFORMANCE_SAFE_RESTAMP__) {
  window.__WILSY_R7J_PERFORMANCE_SAFE_RESTAMP__ = true;
  window.addEventListener('wilsy-theme-runtime-applied', dispatchWilsyR7JPerformanceSafeRestamp);
  window.addEventListener('resize', dispatchWilsyR7JPerformanceSafeRestamp);
  window.addEventListener('click', dispatchWilsyR7JPerformanceSafeRestamp);
}



/**
 * @function normalizeWilsyR7KSkinName
 * @description Normalizes a skin name for safe active-state comparison.
 * @param {string} value - Raw visible skin text.
 * @returns {string} Normalized skin name.
 * @collaboration Keeps switchboard active-state detection independent from fragile class names.
 */
function normalizeWilsyR7KSkinName(value) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .replace(/^active\s*[·•-]\s*/i, '')
    .trim()
    .toLowerCase();
}

/**
 * @function resolveWilsyR7KSkinAnchor
 * @description Resolves the operational anchor for a Wilsy OS operating skin.
 * @param {string} skinName - Visible skin name.
 * @returns {{anchor: string, rhythm: string}} Operational anchor and rhythm copy.
 * @collaboration Gives every visual skin an executive reason for existing instead of being a decorative colour option.
 */
function resolveWilsyR7KSkinAnchor(skinName) {
  const normalized = normalizeWilsyR7KSkinName(skinName);

  if (normalized.includes('crm')) {
    return {
      anchor: 'CRM-GROWTH-SIGNAL',
      rhythm: 'Revenue, pipeline and customer command surfaces.'
    };
  }

  if (normalized.includes('legal') || normalized.includes('evidence')) {
    return {
      anchor: 'LEGAL-EVIDENCE-SIGNAL',
      rhythm: 'Matter evidence, clauses and proof-heavy work.'
    };
  }

  if (normalized.includes('finance') || normalized.includes('ledger') || normalized.includes('banking')) {
    return {
      anchor: 'FINANCE-LEDGER-SIGNAL',
      rhythm: 'Ledger trust, audit posture and financial clarity.'
    };
  }

  if (normalized.includes('security') || normalized.includes('red team')) {
    return {
      anchor: 'SECURITY-RED-TEAM-SIGNAL',
      rhythm: 'Threat posture, risk review and command alerting.'
    };
  }

  if (normalized.includes('construction') || normalized.includes('field') || normalized.includes('logistics')) {
    return {
      anchor: 'FIELD-OPERATIONS-SIGNAL',
      rhythm: 'Operational movement, projects and field command.'
    };
  }

  if (normalized.includes('government') || normalized.includes('civic')) {
    return {
      anchor: 'CIVIC-AUTHORITY-SIGNAL',
      rhythm: 'Public-sector clarity, authority and accountability.'
    };
  }

  if (normalized.includes('healthcare') || normalized.includes('calm')) {
    return {
      anchor: 'CARE-CALM-SIGNAL',
      rhythm: 'Calm visibility for sensitive service environments.'
    };
  }

  if (normalized.includes('presentation') || normalized.includes('boardroom')) {
    return {
      anchor: 'BOARDROOM-PRESENTATION-SIGNAL',
      rhythm: 'Executive readability for live presentations.'
    };
  }

  if (normalized.includes('low light')) {
    return {
      anchor: 'LOW-LIGHT-OPS-SIGNAL',
      rhythm: 'Night operations with reduced visual fatigue.'
    };
  }

  if (normalized.includes('high contrast')) {
    return {
      anchor: 'ACCESSIBLE-CONTRAST-SIGNAL',
      rhythm: 'Maximum contrast for command certainty.'
    };
  }

  return {
    anchor: 'WILSY-OPERATING-SKIN',
    rhythm: 'Colour, signal tone, contrast and executive rhythm.'
  };
}

/**
 * @function resolveWilsyR7KActiveSkinName
 * @description Reads the active skin name from the Account switchboard status label or body runtime state.
 * @returns {string} Active skin name.
 * @collaboration Ties the floating active status back to the selected card without inventing backend state.
 */
function resolveWilsyR7KActiveSkinName() {
  if (typeof document === 'undefined') {
    return '';
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return '';
  }

  const activeLabel = Array.from(root.querySelectorAll('*')).find(element => {
    const text = String(element.textContent || '').trim();
    return /^active\s*[·•-]\s*/i.test(text) && element.children.length === 0;
  });

  if (activeLabel instanceof HTMLElement) {
    activeLabel.dataset.wilsyR7kActiveSkinStatus = 'true';
    return activeLabel.textContent || '';
  }

  return document.body?.dataset?.wilsyThemeRuntime || document.body?.dataset?.wilsyThemeRuntimeName || '';
}

/**
 * @function resolveWilsyR7KSkinCards
 * @description Finds operating-skin cards in the Account theme switchboard.
 * @returns {HTMLElement[]} Skin card elements.
 * @collaboration Uses existing data-wilsy-theme-option markers where available and falls back safely to switchboard buttons.
 */
function resolveWilsyR7KSkinCards() {
  if (typeof document === 'undefined') {
    return [];
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return [];
  }

  const explicitCards = Array.from(root.querySelectorAll('[data-wilsy-theme-option]')).filter(card => card instanceof HTMLElement);

  if (explicitCards.length > 0) {
    return explicitCards;
  }

  const switchboard = root.querySelector('[data-wilsy-theme-switchboard]');

  if (!(switchboard instanceof HTMLElement)) {
    return [];
  }

  return Array.from(switchboard.querySelectorAll('button, [role="button"]')).filter(card => card instanceof HTMLElement);
}

/**
 * @function extractWilsyR7KSkinName
 * @description Extracts the primary visible skin name from a skin card.
 * @param {HTMLElement} card - Candidate skin card.
 * @returns {string} Skin name.
 * @collaboration Prevents metadata appended by the runtime from corrupting active-state detection.
 */
function extractWilsyR7KSkinName(card) {
  const clone = card.cloneNode(true);

  if (clone instanceof HTMLElement) {
    clone.querySelectorAll('[data-wilsy-r7k-skin-anchor="true"], [data-wilsy-r7k-skin-rhythm="true"], [data-wilsy-r7k-active-chip="true"]').forEach(node => node.remove());
  }

  const heading = clone instanceof HTMLElement
    ? clone.querySelector('strong, h3, h4, [data-wilsy-theme-name]')
    : null;

  return String(heading?.textContent || clone?.textContent || card.textContent || '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function stampWilsyR7KSkinCard
 * @description Adds active-state, anchor, rhythm and evidence metadata to one skin card.
 * @param {HTMLElement} card - Skin card element.
 * @param {string} activeSkinName - Active skin name.
 * @returns {void}
 * @collaboration Makes the switchboard feel like a real OS skin contract rather than a decorative carousel.
 */
function stampWilsyR7KSkinCard(card, activeSkinName) {
  const skinName = extractWilsyR7KSkinName(card);
  const normalizedSkin = normalizeWilsyR7KSkinName(skinName);
  const normalizedActive = normalizeWilsyR7KSkinName(activeSkinName);
  const isActive = normalizedSkin && normalizedActive && (
    normalizedSkin === normalizedActive
    || normalizedActive.includes(normalizedSkin)
    || normalizedSkin.includes(normalizedActive)
  );

  const anchor = resolveWilsyR7KSkinAnchor(skinName);

  card.dataset.wilsyR7kSkinCard = 'true';
  card.dataset.wilsyR7kActiveSkin = isActive ? 'true' : 'false';
  card.dataset.wilsyR7kSkinAnchor = anchor.anchor;
  card.setAttribute('aria-pressed', isActive ? 'true' : 'false');

  let activeChip = card.querySelector('[data-wilsy-r7k-active-chip="true"]');

  if (!activeChip) {
    activeChip = document.createElement('span');
    activeChip.setAttribute('data-wilsy-r7k-active-chip', 'true');
    activeChip.textContent = 'Active';
    card.appendChild(activeChip);
  }

  let anchorNode = card.querySelector('[data-wilsy-r7k-skin-anchor="true"]');

  if (!anchorNode) {
    anchorNode = document.createElement('span');
    anchorNode.setAttribute('data-wilsy-r7k-skin-anchor', 'true');
    card.appendChild(anchorNode);
  }

  anchorNode.textContent = anchor.anchor;

  let rhythmNode = card.querySelector('[data-wilsy-r7k-skin-rhythm="true"]');

  if (!rhythmNode) {
    rhythmNode = document.createElement('span');
    rhythmNode.setAttribute('data-wilsy-r7k-skin-rhythm', 'true');
    card.appendChild(rhythmNode);
  }

  rhythmNode.textContent = anchor.rhythm;
}

/**
 * @function stampWilsyR7KThemeSwitchboard
 * @description Applies active authority, anchors and rhythm metadata to the theme switchboard.
 * @returns {void}
 * @collaboration Gives users clear confidence about the active Wilsy OS visual language.
 */
function stampWilsyR7KThemeSwitchboard() {
  const activeSkinName = resolveWilsyR7KActiveSkinName();
  const cards = resolveWilsyR7KSkinCards();

  cards.forEach(card => {
    stampWilsyR7KSkinCard(card, activeSkinName);
  });
}

/**
 * @function queueWilsyR7KThemeSwitchboardStamp
 * @description Queues theme switchboard stamping on the next browser animation frame.
 * @returns {number | undefined} Animation frame request identifier when available.
 * @collaboration Keeps skin-card updates smooth without broad MutationObserver loops.
 */
function queueWilsyR7KThemeSwitchboardStamp() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR7KThemeSwitchboard);
}

/**
 * @function bootWilsyR7KThemeSwitchboardRuntime
 * @description Boots the performance-safe theme switchboard active-state runtime once.
 * @returns {void}
 * @collaboration Uses explicit lifecycle events only, avoiding document-level observer storms.
 */
function bootWilsyR7KThemeSwitchboardRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R7K_THEME_SWITCHBOARD_RUNTIME__) {
    return;
  }

  window.__WILSY_R7K_THEME_SWITCHBOARD_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR7KThemeSwitchboardStamp, { once: true });
  } else {
    queueWilsyR7KThemeSwitchboardStamp();
  }

  document.addEventListener('click', event => {
    const card = event.target instanceof Element
      ? event.target.closest('[data-wilsy-theme-option], [data-wilsy-r7k-skin-card="true"]')
      : null;

    if (card instanceof HTMLElement) {
      window.requestAnimationFrame(() => {
        resolveWilsyR7KSkinCards().forEach(candidate => {
          if (candidate instanceof HTMLElement) {
            candidate.dataset.wilsyR7kActiveSkin = candidate === card ? 'true' : 'false';
            candidate.setAttribute('aria-pressed', candidate === card ? 'true' : 'false');
          }
        });

        queueWilsyR7KThemeSwitchboardStamp();
      });
    }
  });

  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR7KThemeSwitchboardStamp);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR7KThemeSwitchboardStamp);
  window.addEventListener('resize', queueWilsyR7KThemeSwitchboardStamp);
}

bootWilsyR7KThemeSwitchboardRuntime();
/**
 * @function normalizeWilsyR7LSkinName
 * @description Normalizes an operating-skin name for palette lookup and active comparison.
 * @param {string} value - Raw visible skin name.
 * @returns {string} Normalized skin name.
 * @collaboration Makes palette previews resilient to card formatting and appended metadata.
 */
function normalizeWilsyR7LSkinName(value) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .replace(/^active\s*[·•-]\s*/i, '')
    .trim()
    .toLowerCase();
}

/**
 * @function resolveWilsyR7LSkinPalette
 * @description Resolves the visual preview palette and operating meaning for a Wilsy OS skin.
 * @param {string} skinName - Visible skin name.
 * @returns {{gradient: string, anchor: string, rhythm: string, tone: string}} Skin preview contract.
 * @collaboration Lets users compare skins before selection, instead of guessing from names.
 */
function resolveWilsyR7LSkinPalette(skinName) {
  const key = normalizeWilsyR7LSkinName(skinName);

  const palettes = {
    'wilsy sovereign aurora': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #2563eb 28%, #5eead4 58%, #052e16 100%)',
      anchor: 'SOVEREIGN-AURORA',
      rhythm: 'Flagship Wilsy command colour with executive range.',
      tone: 'Founder'
    },
    'sovereign black': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #1f2937 28%, #020617 72%, #000000 100%)',
      anchor: 'SOVEREIGN-BLACK',
      rhythm: 'Boardroom authority with gold command accents.',
      tone: 'Executive'
    },
    'cobalt glass': {
      gradient: 'linear-gradient(90deg, #38bdf8 0%, #2563eb 38%, #1e40af 68%, #0f172a 100%)',
      anchor: 'COBALT-GLASS',
      rhythm: 'Crisp blue cockpit for analytical command surfaces.',
      tone: 'Analytical'
    },
    'pearl command': {
      gradient: 'linear-gradient(90deg, #f8fafc 0%, #cbd5e1 42%, #64748b 68%, #0f172a 100%)',
      anchor: 'PEARL-COMMAND',
      rhythm: 'Light executive clarity with restrained contrast.',
      tone: 'Presentation'
    },
    'legacy gold': {
      gradient: 'linear-gradient(90deg, #facc15 0%, #d4af37 36%, #92400e 68%, #111827 100%)',
      anchor: 'LEGACY-GOLD',
      rhythm: 'Institutional gold for heritage and boardroom trust.',
      tone: 'Prestige'
    },
    'forensic violet': {
      gradient: 'linear-gradient(90deg, #a855f7 0%, #7c3aed 36%, #312e81 70%, #020617 100%)',
      anchor: 'FORENSIC-VIOLET',
      rhythm: 'Investigation-led posture for evidence-heavy workflows.',
      tone: 'Forensic'
    },
    'quantum blue': {
      gradient: 'linear-gradient(90deg, #67e8f9 0%, #38bdf8 34%, #2563eb 68%, #0f172a 100%)',
      anchor: 'QUANTUM-BLUE',
      rhythm: 'High-velocity clarity for intelligence and AI surfaces.',
      tone: 'Future'
    },
    'crm revenue pulse': {
      gradient: 'linear-gradient(90deg, #22c55e 0%, #16a34a 34%, #14b8a6 66%, #052e16 100%)',
      anchor: 'CRM-GROWTH-SIGNAL',
      rhythm: 'Revenue, pipeline and customer command surfaces.',
      tone: 'Growth'
    },
    'legal evidence noir': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #334155 28%, #111827 66%, #020617 100%)',
      anchor: 'LEGAL-EVIDENCE-SIGNAL',
      rhythm: 'Matter evidence, clauses and proof-heavy work.',
      tone: 'Evidence'
    },
    'finance ledger green': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #22c55e 34%, #14532d 70%, #020617 100%)',
      anchor: 'FINANCE-LEDGER-SIGNAL',
      rhythm: 'Ledger trust, audit posture and financial clarity.',
      tone: 'Ledger'
    },
    'hr people graph': {
      gradient: 'linear-gradient(90deg, #60a5fa 0%, #ec4899 38%, #f97316 72%, #111827 100%)',
      anchor: 'PEOPLE-GRAPH-SIGNAL',
      rhythm: 'People operations, sentiment and human-capital rhythm.',
      tone: 'People'
    },
    'construction command': {
      gradient: 'linear-gradient(90deg, #f59e0b 0%, #ea580c 38%, #78350f 74%, #020617 100%)',
      anchor: 'CONSTRUCTION-COMMAND',
      rhythm: 'Project movement, site signals and field execution.',
      tone: 'Build'
    },
    'document vault steel': {
      gradient: 'linear-gradient(90deg, #cbd5e1 0%, #64748b 36%, #334155 72%, #020617 100%)',
      anchor: 'DOCUMENT-VAULT-STEEL',
      rhythm: 'Controlled document custody and vault-grade clarity.',
      tone: 'Vault'
    },
    'banking trust': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #14b8a6 34%, #0f766e 70%, #022c22 100%)',
      anchor: 'BANKING-TRUST',
      rhythm: 'Financial trust, regulated posture and audit calm.',
      tone: 'Trust'
    },
    'law firm authority': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #dc2626 34%, #7f1d1d 68%, #020617 100%)',
      anchor: 'LAW-FIRM-AUTHORITY',
      rhythm: 'Matter authority with high-contrast legal posture.',
      tone: 'Authority'
    },
    'healthcare calm': {
      gradient: 'linear-gradient(90deg, #e0f2fe 0%, #06b6d4 34%, #22c55e 68%, #0f172a 100%)',
      anchor: 'HEALTHCARE-CALM',
      rhythm: 'Calm visibility for sensitive care environments.',
      tone: 'Care'
    },
    'logistics command': {
      gradient: 'linear-gradient(90deg, #f97316 0%, #eab308 34%, #1d4ed8 72%, #020617 100%)',
      anchor: 'LOGISTICS-COMMAND',
      rhythm: 'Movement, fleet, delivery and operational routing.',
      tone: 'Motion'
    },
    'real estate prestige': {
      gradient: 'linear-gradient(90deg, #d4af37 0%, #166534 36%, #052e16 72%, #020617 100%)',
      anchor: 'REAL-ESTATE-PRESTIGE',
      rhythm: 'Property authority, deal posture and prestige surfaces.',
      tone: 'Prestige'
    },
    'government civic': {
      gradient: 'linear-gradient(90deg, #f8fafc 0%, #1d4ed8 32%, #dc2626 66%, #020617 100%)',
      anchor: 'CIVIC-AUTHORITY-SIGNAL',
      rhythm: 'Public-sector clarity, authority and accountability.',
      tone: 'Civic'
    },
    'startup velocity': {
      gradient: 'linear-gradient(90deg, #38bdf8 0%, #8b5cf6 34%, #ec4899 68%, #020617 100%)',
      anchor: 'STARTUP-VELOCITY',
      rhythm: 'Momentum, growth experiments and founder execution.',
      tone: 'Velocity'
    },
    'high contrast sovereign': {
      gradient: 'linear-gradient(90deg, #f8fafc 0%, #d4af37 34%, #000000 70%, #020617 100%)',
      anchor: 'ACCESSIBLE-CONTRAST-SIGNAL',
      rhythm: 'Maximum contrast for command certainty.',
      tone: 'Access'
    },
    'low light ops': {
      gradient: 'linear-gradient(90deg, #64748b 0%, #312e81 34%, #0f172a 74%, #020617 100%)',
      anchor: 'LOW-LIGHT-OPS-SIGNAL',
      rhythm: 'Night operations with reduced visual fatigue.',
      tone: 'Low light'
    },
    'presentation boardroom': {
      gradient: 'linear-gradient(90deg, #f8fafc 0%, #d4af37 36%, #334155 72%, #020617 100%)',
      anchor: 'BOARDROOM-PRESENTATION-SIGNAL',
      rhythm: 'Executive readability for live presentations.',
      tone: 'Boardroom'
    },
    'outdoor field mode': {
      gradient: 'linear-gradient(90deg, #84cc16 0%, #ca8a04 34%, #3f6212 72%, #0f172a 100%)',
      anchor: 'OUTDOOR-FIELD-MODE',
      rhythm: 'Field visibility, rugged contrast and mobile command.',
      tone: 'Field'
    },
    'security red team': {
      gradient: 'linear-gradient(90deg, #ef4444 0%, #dc2626 32%, #991b1b 68%, #020617 100%)',
      anchor: 'SECURITY-RED-TEAM-SIGNAL',
      rhythm: 'Threat posture, risk review and command alerting.',
      tone: 'Security'
    }
  };

  return palettes[key] || {
    gradient: 'linear-gradient(90deg, #d4af37 0%, #38bdf8 38%, #22c55e 70%, #020617 100%)',
    anchor: 'WILSY-OPERATING-SKIN',
    rhythm: 'Colour, signal tone, contrast and executive rhythm.',
    tone: 'Wilsy'
  };
}

/**
 * @function resolveWilsyR7LActiveSkinName
 * @description Reads the active skin name from the visible switchboard status label.
 * @returns {string} Active skin name.
 * @collaboration Ties the active status to the selected card without guessing from theme side effects.
 */
function resolveWilsyR7LActiveSkinName() {
  if (typeof document === 'undefined') {
    return '';
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return '';
  }

  const activeLabel = Array.from(root.querySelectorAll('*')).find(element => {
    const text = String(element.textContent || '').trim();
    return /^active\s*[·•-]\s*/i.test(text) && element.children.length === 0;
  });

  if (activeLabel instanceof HTMLElement) {
    activeLabel.dataset.wilsyR7lActiveSkinStatus = 'true';
    return activeLabel.textContent || '';
  }

  return '';
}

/**
 * @function resolveWilsyR7LSkinCards
 * @description Finds skin cards in the switchboard.
 * @returns {HTMLElement[]} Skin card elements.
 * @collaboration Uses existing theme option markers first, then safe switchboard fallbacks.
 */
function resolveWilsyR7LSkinCards() {
  if (typeof document === 'undefined') {
    return [];
  }

  const root = document.querySelector('[data-wilsy-account-command-center="true"]');

  if (!(root instanceof HTMLElement)) {
    return [];
  }

  const explicitCards = Array.from(root.querySelectorAll('[data-wilsy-theme-option]')).filter(card => card instanceof HTMLElement);

  if (explicitCards.length > 0) {
    return explicitCards;
  }

  const switchboard = root.querySelector('[data-wilsy-theme-switchboard]');

  if (!(switchboard instanceof HTMLElement)) {
    return [];
  }

  return Array.from(switchboard.querySelectorAll('button, [role="button"]')).filter(card => card instanceof HTMLElement);
}

/**
 * @function extractWilsyR7LSkinName
 * @description Extracts the visible skin name without runtime metadata.
 * @param {HTMLElement} card - Skin card element.
 * @returns {string} Skin name.
 * @collaboration Prevents palette metadata from corrupting future palette lookups.
 */
function extractWilsyR7LSkinName(card) {
  const clone = card.cloneNode(true);

  if (clone instanceof HTMLElement) {
    clone.querySelectorAll('[data-wilsy-r7l-palette-preview="true"], [data-wilsy-r7l-skin-anchor="true"], [data-wilsy-r7l-skin-rhythm="true"], [data-wilsy-r7l-active-chip="true"], [data-wilsy-r7k-skin-anchor="true"], [data-wilsy-r7k-skin-rhythm="true"], [data-wilsy-r7k-active-chip="true"]').forEach(node => node.remove());
  }

  const heading = clone instanceof HTMLElement
    ? clone.querySelector('strong, h3, h4, [data-wilsy-theme-name]')
    : null;

  return String(heading?.textContent || clone?.textContent || card.textContent || '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * @function stampWilsyR7LSkinCard
 * @description Applies a visible palette preview and active state to a skin card.
 * @param {HTMLElement} card - Skin card element.
 * @param {string} activeSkinName - Active skin name.
 * @returns {void}
 * @collaboration Makes operating skins understandable before the user selects them.
 */
function stampWilsyR7LSkinCard(card, activeSkinName) {
  const skinName = extractWilsyR7LSkinName(card);
  const palette = resolveWilsyR7LSkinPalette(skinName);
  const normalizedSkin = normalizeWilsyR7LSkinName(skinName);
  const normalizedActive = normalizeWilsyR7LSkinName(activeSkinName);
  const isActive = normalizedSkin && normalizedActive && (
    normalizedSkin === normalizedActive
    || normalizedActive.includes(normalizedSkin)
    || normalizedSkin.includes(normalizedActive)
  );

  card.dataset.wilsyR7lSkinCard = 'true';
  card.dataset.wilsyR7lActiveSkin = isActive ? 'true' : 'false';
  card.dataset.wilsyR7lSkinAnchor = palette.anchor;
  card.style.setProperty('--wilsy-r7l-skin-gradient', palette.gradient);
  card.style.setProperty('--wilsy-r7l-skin-tone', `"${palette.tone}"`);
  card.setAttribute('aria-pressed', isActive ? 'true' : 'false');

  let preview = card.querySelector('[data-wilsy-r7l-palette-preview="true"]');

  if (!(preview instanceof HTMLElement)) {
    preview = document.createElement('span');
    preview.setAttribute('data-wilsy-r7l-palette-preview', 'true');
    card.prepend(preview);
  }

  preview.style.setProperty('--wilsy-r7l-skin-gradient', palette.gradient);
  preview.setAttribute('aria-hidden', 'true');

  let activeChip = card.querySelector('[data-wilsy-r7l-active-chip="true"]');

  if (!(activeChip instanceof HTMLElement)) {
    activeChip = document.createElement('span');
    activeChip.setAttribute('data-wilsy-r7l-active-chip', 'true');
    activeChip.textContent = 'Active';
    card.appendChild(activeChip);
  }

  let anchorNode = card.querySelector('[data-wilsy-r7l-skin-anchor="true"]');

  if (!(anchorNode instanceof HTMLElement)) {
    anchorNode = document.createElement('span');
    anchorNode.setAttribute('data-wilsy-r7l-skin-anchor', 'true');
    card.appendChild(anchorNode);
  }

  anchorNode.textContent = palette.anchor;

  let rhythmNode = card.querySelector('[data-wilsy-r7l-skin-rhythm="true"]');

  if (!(rhythmNode instanceof HTMLElement)) {
    rhythmNode = document.createElement('span');
    rhythmNode.setAttribute('data-wilsy-r7l-skin-rhythm', 'true');
    card.appendChild(rhythmNode);
  }

  rhythmNode.textContent = palette.rhythm;
}

/**
 * @function stampWilsyR7LThemePaletteSwitchboard
 * @description Applies visible palette previews to all theme cards.
 * @returns {void}
 * @collaboration Converts the switchboard from blind selection into a real visual language chooser.
 */
function stampWilsyR7LThemePaletteSwitchboard() {
  const activeSkinName = resolveWilsyR7LActiveSkinName();
  resolveWilsyR7LSkinCards().forEach(card => {
    stampWilsyR7LSkinCard(card, activeSkinName);
  });
}

/**
 * @function queueWilsyR7LThemePaletteSwitchboardStamp
 * @description Queues palette switchboard stamping on the next browser animation frame.
 * @returns {number | undefined} Animation frame request identifier when available.
 * @collaboration Avoids document-level observers and protects performance.
 */
function queueWilsyR7LThemePaletteSwitchboardStamp() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR7LThemePaletteSwitchboard);
}

/**
 * @function bootWilsyR7LThemePaletteSwitchboardRuntime
 * @description Boots the performance-safe palette preview runtime once.
 * @returns {void}
 * @collaboration Makes theme cards self-explanatory without page-freeze observer loops.
 */
function bootWilsyR7LThemePaletteSwitchboardRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R7L_THEME_PALETTE_SWITCHBOARD_RUNTIME__) {
    return;
  }

  window.__WILSY_R7L_THEME_PALETTE_SWITCHBOARD_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR7LThemePaletteSwitchboardStamp, { once: true });
  } else {
    queueWilsyR7LThemePaletteSwitchboardStamp();
  }

  for (let attempt = 1; attempt <= 8; attempt += 1) {
    window.setTimeout(queueWilsyR7LThemePaletteSwitchboardStamp, attempt * 120);
  }

  document.addEventListener('click', event => {
    const card = event.target instanceof Element
      ? event.target.closest('[data-wilsy-theme-option], [data-wilsy-r7l-skin-card="true"]')
      : null;

    if (card instanceof HTMLElement) {
      window.requestAnimationFrame(() => {
        resolveWilsyR7LSkinCards().forEach(candidate => {
          if (candidate instanceof HTMLElement) {
            candidate.dataset.wilsyR7lActiveSkin = candidate === card ? 'true' : 'false';
            candidate.setAttribute('aria-pressed', candidate === card ? 'true' : 'false');
          }
        });

        queueWilsyR7LThemePaletteSwitchboardStamp();
      });
    }
  });

  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR7LThemePaletteSwitchboardStamp);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR7LThemePaletteSwitchboardStamp);
  window.addEventListener('resize', queueWilsyR7LThemePaletteSwitchboardStamp);
}

bootWilsyR7LThemePaletteSwitchboardRuntime();
/**
 * @function readWilsyR7OText
 * @description Reads normalized visible text from a DOM element.
 * @param {Element | null} element - Candidate element.
 * @returns {string} Normalized text.
 * @collaboration Keeps Account intelligence derived from rendered account context instead of hardcoded user values.
 */
function readWilsyR7OText(element) {
  return String(element?.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function findWilsyR7OTextElement
 * @description Finds an element by visible text inside the Account command center.
 * @param {HTMLElement} root - Account command center root.
 * @param {string} text - Text to locate.
 * @param {boolean} exact - Whether to require exact matching.
 * @returns {HTMLElement | null} Matching element.
 * @collaboration Uses existing UI labels as anchors without inventing account data.
 */
function findWilsyR7OTextElement(root, text, exact = true) {
  const needle = String(text || '').toLowerCase();

  return Array.from(root.querySelectorAll('*')).find(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    const value = readWilsyR7OText(element).toLowerCase();

    return exact ? value === needle : value.includes(needle);
  }) || null;
}

/**
 * @function resolveWilsyR7OAccountRoot
 * @description Resolves the Account Command Center root.
 * @returns {HTMLElement | null} Account root.
 * @collaboration Keeps all enhancements scoped to Account Command Center.
 */
function resolveWilsyR7OAccountRoot() {
  if (typeof document === 'undefined') {
    return null;
  }

  return document.querySelector('[data-wilsy-account-command-center="true"]');
}

/**
 * @function resolveWilsyR7OProfilePanel
 * @description Resolves the Executive Identity profile panel.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Profile panel.
 * @collaboration Enhances only the visible profile area without assuming backend data.
 */
function resolveWilsyR7OProfilePanel(root) {
  const heading = findWilsyR7OTextElement(root, 'Executive Identity', true);

  if (!(heading instanceof HTMLElement)) {
    return null;
  }

  let cursor = heading.parentElement;

  for (let depth = 0; depth < 8 && cursor instanceof HTMLElement; depth += 1) {
    const text = readWilsyR7OText(cursor);

    if (
      text.includes('Tenant ID')
      && text.includes('Industry')
      && text.includes('Email')
      && text.includes('Authority')
    ) {
      return cursor;
    }

    cursor = cursor.parentElement;
  }

  return heading.parentElement;
}

/**
 * @function resolveWilsyR7OProfileCard
 * @description Resolves the nearest value card for a profile label.
 * @param {HTMLElement} root - Account root.
 * @param {string} labelText - Profile label.
 * @returns {HTMLElement | null} Profile card.
 * @collaboration Anchors profile meaning to the real visible fields already rendered.
 */
function resolveWilsyR7OProfileCard(root, labelText) {
  const label = findWilsyR7OTextElement(root, labelText, true);

  if (!(label instanceof HTMLElement)) {
    return null;
  }

  let card = label.parentElement;

  for (let depth = 0; depth < 5 && card instanceof HTMLElement; depth += 1) {
    const text = readWilsyR7OText(card);

    if (text.length > labelText.length && !text.includes('Executive Identity')) {
      return card;
    }

    card = card.parentElement;
  }

  return null;
}

/**
 * @function extractWilsyR7OProfileValue
 * @description Extracts a profile value from a profile card after removing runtime metadata.
 * @param {HTMLElement} card - Profile card.
 * @param {string} labelText - Profile label.
 * @returns {string} Real visible profile value.
 * @collaboration Prevents Wilsy OS from confusing enhancement copy with account data.
 */
function extractWilsyR7OProfileValue(card, labelText) {
  const clone = card.cloneNode(true);

  if (clone instanceof HTMLElement) {
    clone.querySelectorAll('[data-wilsy-r7o-profile-role="true"], [data-wilsy-r7o-profile-proof="true"], [data-wilsy-r7o-profile-source="true"]').forEach(node => node.remove());
  }

  return readWilsyR7OText(clone)
    .replace(new RegExp(`^${labelText}\\s*`, 'i'), '')
    .trim();
}

/**
 * @function deriveWilsyR7OProfileFieldContract
 * @description Derives semantic meaning from an existing profile field label and real value.
 * @param {string} labelText - Existing profile label.
 * @param {string} value - Real visible profile value.
 * @returns {{role: string, proof: string, source: string}} Derived contract.
 * @collaboration Adds meaning without hardcoding user-specific data, tenant IDs, emails or fake timestamps.
 */
function deriveWilsyR7OProfileFieldContract(labelText, value) {
  const hasValue = Boolean(String(value || '').trim());
  const normalized = String(labelText || '').toUpperCase();

  const roleByLabel = {
    'TENANT ID': 'Tenant Passport',
    'INDUSTRY': 'Operating Context',
    'EMAIL': 'Contact Proof',
    'AUTHORITY': 'Authority Scope'
  };

  const proofByLabel = {
    'TENANT ID': 'Defines the active tenant scope for command receipts.',
    'INDUSTRY': 'Tunes boardroom language, routes and sector posture.',
    'EMAIL': 'Supports sign-in, recovery and notification identity.',
    'AUTHORITY': 'Defines the command boundary for this account.'
  };

  return {
    role: roleByLabel[normalized] || 'Account Evidence',
    proof: hasValue ? (proofByLabel[normalized] || 'Loaded from active account context.') : 'No verified value is currently available.',
    source: hasValue ? 'LIVE CONTEXT' : 'AWAITING SOURCE'
  };
}

/**
 * @function upsertWilsyR7ONode
 * @description Creates or updates a runtime metadata node inside a card.
 * @param {HTMLElement} target - Target card.
 * @param {string} selector - Existing selector.
 * @param {string} attr - Attribute to stamp.
 * @param {string} text - Text to render.
 * @returns {HTMLElement} Runtime node.
 * @collaboration Keeps runtime enhancements idempotent and duplicate-free.
 */
function upsertWilsyR7ONode(target, selector, attr, text) {
  let node = target.querySelector(selector);

  if (!(node instanceof HTMLElement)) {
    node = document.createElement('span');
    node.setAttribute(attr, 'true');
    target.appendChild(node);
  }

  node.textContent = text;
  return node;
}

/**
 * @function stampWilsyR7OProfileCard
 * @description Enhances one real profile card with derived evidence.
 * @param {HTMLElement} root - Account root.
 * @param {string} labelText - Profile label.
 * @returns {void}
 * @collaboration Makes profile fields feel like a cockpit identity hub while preserving real account data only.
 */
function stampWilsyR7OProfileCard(root, labelText) {
  const card = resolveWilsyR7OProfileCard(root, labelText);

  if (!(card instanceof HTMLElement)) {
    return;
  }

  const value = extractWilsyR7OProfileValue(card, labelText);
  const contract = deriveWilsyR7OProfileFieldContract(labelText, value);

  card.dataset.wilsyR7oProfileCard = 'true';
  card.dataset.wilsyR7oProfileLabel = labelText;
  card.dataset.wilsyR7oProfileSource = contract.source;

  upsertWilsyR7ONode(card, '[data-wilsy-r7o-profile-role="true"]', 'data-wilsy-r7o-profile-role', contract.role);
  upsertWilsyR7ONode(card, '[data-wilsy-r7o-profile-proof="true"]', 'data-wilsy-r7o-profile-proof', contract.proof);
  upsertWilsyR7ONode(card, '[data-wilsy-r7o-profile-source="true"]', 'data-wilsy-r7o-profile-source', contract.source);
}

/**
 * @function stampWilsyR7OProfileHeader
 * @description Adds a dynamic summary and evidence strip derived from visible profile fields.
 * @param {HTMLElement} root - Account root.
 * @returns {void}
 * @collaboration Avoids fake data by calculating profile readiness from real visible values.
 */
function stampWilsyR7OProfileHeader(root) {
  const panel = resolveWilsyR7OProfilePanel(root);

  if (!(panel instanceof HTMLElement)) {
    return;
  }

  panel.dataset.wilsyR7oProfileHub = 'true';

  const labels = ['TENANT ID', 'INDUSTRY', 'EMAIL', 'AUTHORITY'];
  const values = labels.map(label => {
    const card = resolveWilsyR7OProfileCard(root, label);
    return card instanceof HTMLElement ? extractWilsyR7OProfileValue(card, label) : '';
  });

  const liveCount = values.filter(Boolean).length;
  const totalCount = labels.length;

  upsertWilsyR7ONode(
    panel,
    '[data-wilsy-r7o-profile-summary="true"]',
    'data-wilsy-r7o-profile-summary',
    `${liveCount}/${totalCount} account fields are loaded from the active account context.`
  );

  upsertWilsyR7ONode(
    panel,
    '[data-wilsy-r7o-profile-evidence-strip="true"]',
    'data-wilsy-r7o-profile-evidence-strip',
    `ACCOUNT CONTEXT ${liveCount}/${totalCount} • NO FAKE DATA • NO HARDCODED USER VALUES`
  );

  const editButton = Array.from(panel.querySelectorAll('button')).find(button => (
    button instanceof HTMLElement && /edit profile/i.test(readWilsyR7OText(button))
  ));

  if (editButton instanceof HTMLElement) {
    editButton.dataset.wilsyR7oEditProfileCommand = 'true';
  }
}

/**
 * @function removeWilsyR7NHardcodedRouteNodes
 * @description Removes previous hardcoded R7N command route labels and metadata from the DOM.
 * @param {HTMLElement} root - Account root.
 * @returns {void}
 * @collaboration Guarantees Wilsy OS does not display invented account routes as if they came from the backend.
 */
function removeWilsyR7NHardcodedRouteNodes(root) {
  root.querySelectorAll('[data-wilsy-r7n-route-title="true"], [data-wilsy-r7n-route-meta="true"], [data-wilsy-r7n-route-status="true"]').forEach(node => node.remove());

  root.querySelectorAll('[data-wilsy-r7n-command-route-card="true"]').forEach(card => {
    if (card instanceof HTMLElement) {
      delete card.dataset.wilsyR7nCommandRouteCard;
      delete card.dataset.wilsyR7nCommandRoute;
      card.removeAttribute('aria-label');
    }
  });
}

/**
 * @function resolveWilsyR7ORouteSection
 * @description Resolves the Command Routes section if it exists.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Route section.
 * @collaboration Lets Wilsy OS suppress unbound route shells without manufacturing labels.
 */
function resolveWilsyR7ORouteSection(root) {
  const heading = findWilsyR7OTextElement(root, 'COMMAND ROUTES', true);

  if (!(heading instanceof HTMLElement)) {
    return null;
  }

  let cursor = heading.parentElement;

  for (let depth = 0; depth < 8 && cursor instanceof HTMLElement; depth += 1) {
    if (cursor.querySelectorAll('svg').length >= 2) {
      return cursor;
    }

    cursor = cursor.parentElement;
  }

  return heading.parentElement;
}

/**
 * @function suppressWilsyR7OUnboundRoutes
 * @description Hides route cards that have icons only and no real route contract text.
 * @param {HTMLElement} root - Account root.
 * @returns {void}
 * @collaboration Enforces source-truth-only route display instead of placeholders.
 */
function suppressWilsyR7OUnboundRoutes(root) {
  const section = resolveWilsyR7ORouteSection(root);

  if (!(section instanceof HTMLElement)) {
    return;
  }

  section.dataset.wilsyR7oRouteSection = 'true';

  const routeCandidates = Array.from(section.querySelectorAll('button, a, [role="button"], div')).filter(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    if (!element.querySelector('svg')) {
      return false;
    }

    const rect = element.getBoundingClientRect();
    return rect.width >= 180 && rect.height >= 60;
  });

  let visibleBoundRoutes = 0;

  routeCandidates.forEach(card => {
    const text = readWilsyR7OText(card);
    const hasMeaningfulText = text.length > 2 && !/^[•\s]*$/.test(text);

    if (!hasMeaningfulText) {
      card.dataset.wilsyR7oRouteUnbound = 'true';
      return;
    }

    card.dataset.wilsyR7oRouteBound = 'true';
    visibleBoundRoutes += 1;
  });

  section.dataset.wilsyR7oRouteBoundCount = String(visibleBoundRoutes);
  section.dataset.wilsyR7oRouteState = visibleBoundRoutes > 0 ? 'bound' : 'empty';
}

/**
 * @function stampWilsyR7ONoHardcodeAccountHub
 * @description Enhances My Account using only rendered account context and suppresses unbound route shells.
 * @returns {void}
 * @collaboration Establishes Wilsy OS account management as source-truth-first and no-hardcode.
 */
function stampWilsyR7ONoHardcodeAccountHub() {
  const root = resolveWilsyR7OAccountRoot();

  if (!(root instanceof HTMLElement)) {
    return;
  }

  root.dataset.wilsyR7oNoHardcodeProfileIntelligence = 'true';

  stampWilsyR7OProfileHeader(root);
  ['TENANT ID', 'INDUSTRY', 'EMAIL', 'AUTHORITY'].forEach(label => stampWilsyR7OProfileCard(root, label));
  removeWilsyR7NHardcodedRouteNodes(root);
  suppressWilsyR7OUnboundRoutes(root);
}

/**
 * @function queueWilsyR7ONoHardcodeAccountHubStamp
 * @description Queues Account hub stamping on the next animation frame.
 * @returns {number | undefined} Browser animation frame request identifier when available.
 * @collaboration Keeps Account enhancements performance-safe and observer-free.
 */
function queueWilsyR7ONoHardcodeAccountHubStamp() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR7ONoHardcodeAccountHub);
}

/**
 * @function bootWilsyR7ONoHardcodeAccountHubRuntime
 * @description Boots the no-hardcode My Account runtime once.
 * @returns {void}
 * @collaboration Runs only on explicit lifecycle events, never broad document observers.
 */
function bootWilsyR7ONoHardcodeAccountHubRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R7O_NO_HARDCODE_ACCOUNT_HUB_RUNTIME__) {
    return;
  }

  window.__WILSY_R7O_NO_HARDCODE_ACCOUNT_HUB_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR7ONoHardcodeAccountHubStamp, { once: true });
  } else {
    queueWilsyR7ONoHardcodeAccountHubStamp();
  }

  for (let attempt = 1; attempt <= 8; attempt += 1) {
    window.setTimeout(queueWilsyR7ONoHardcodeAccountHubStamp, attempt * 140);
  }

  document.addEventListener('click', queueWilsyR7ONoHardcodeAccountHubStamp);
  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR7ONoHardcodeAccountHubStamp);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR7ONoHardcodeAccountHubStamp);
  window.addEventListener('resize', queueWilsyR7ONoHardcodeAccountHubStamp);
}

bootWilsyR7ONoHardcodeAccountHubRuntime();


const WILSY_R8C_THEME_VIEWPORT_SWITCHBOARD_MARKER = 'data-wilsy-r8c-theme-viewport-switchboard';
const WILSY_R8C_THEME_SCROLL_GRID_MARKER = 'data-wilsy-r8c-theme-scroll-grid';
const WILSY_R8C_THEME_STICKY_HEADER_MARKER = 'data-wilsy-r8c-theme-sticky-header';

/**
 * @function readWilsyR8CText
 * @description Reads normalized visible text from a DOM element.
 * @param {Element | null} element - Candidate element.
 * @returns {string} Normalized text.
 * @collaboration Lets the theme viewport runtime find existing UI regions without hardcoding user data.
 */
function readWilsyR8CText(element) {
  return String(element?.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyR8CAccountRoot
 * @description Resolves the Account Command Center DOM root.
 * @returns {HTMLElement | null} Account root.
 * @collaboration Keeps the viewport switchboard scoped to Account Command Center only.
 */
function resolveWilsyR8CAccountRoot() {
  if (typeof document === 'undefined') {
    return null;
  }

  return document.querySelector('[data-wilsy-account-command-center="true"]');
}

/**
 * @function findWilsyR8CTextElement
 * @description Finds an element whose visible text contains a phrase.
 * @param {HTMLElement} root - Search root.
 * @param {string} phrase - Phrase to find.
 * @returns {HTMLElement | null} Matching element.
 * @collaboration Anchors viewport chrome to existing interface labels instead of brittle generated classes.
 */
function findWilsyR8CTextElement(root, phrase) {
  const needle = String(phrase || '').toLowerCase();

  return Array.from(root.querySelectorAll('*')).find(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    return readWilsyR8CText(element).toLowerCase().includes(needle);
  }) || null;
}

/**
 * @function resolveWilsyR8CThemeSwitchboard
 * @description Resolves the theme switchboard region from existing labels and theme option cards.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Theme switchboard region.
 * @collaboration Builds a viewport-first switchboard without adding fake theme data.
 */
function resolveWilsyR8CThemeSwitchboard(root) {
  const direct = root.querySelector('[data-wilsy-theme-switchboard], [data-wilsy-r7l-palette-preview]');

  if (direct instanceof HTMLElement) {
    let cursor = direct;

    for (let depth = 0; depth < 8 && cursor instanceof HTMLElement; depth += 1) {
      const text = readWilsyR8CText(cursor);

      if (/Operating Skin Switchboard|Theme Control Panel/i.test(text)) {
        return cursor;
      }

      cursor = cursor.parentElement;
    }

    return direct.parentElement instanceof HTMLElement ? direct.parentElement : direct;
  }

  const heading = findWilsyR8CTextElement(root, 'Operating Skin Switchboard')
    || findWilsyR8CTextElement(root, 'Theme Control Panel');

  if (!(heading instanceof HTMLElement)) {
    return null;
  }

  let cursor = heading.parentElement;

  for (let depth = 0; depth < 10 && cursor instanceof HTMLElement; depth += 1) {
    const text = readWilsyR8CText(cursor);
    const optionCount = cursor.querySelectorAll('[data-wilsy-theme-option], [data-wilsy-r7l-skin-card], button, article').length;

    if (/Operating Skin Switchboard|Theme Control Panel/i.test(text) && optionCount >= 4) {
      return cursor;
    }

    cursor = cursor.parentElement;
  }

  return heading.parentElement;
}

/**
 * @function resolveWilsyR8CThemeHeader
 * @description Resolves or creates a local sticky header wrapper inside the theme switchboard.
 * @param {HTMLElement} switchboard - Theme switchboard region.
 * @returns {HTMLElement | null} Sticky header region.
 * @collaboration Keeps theme context visible while the palette grid scrolls beneath it.
 */
function resolveWilsyR8CThemeHeader(switchboard) {
  const existing = switchboard.querySelector(`[${WILSY_R8C_THEME_STICKY_HEADER_MARKER}="true"]`);

  if (existing instanceof HTMLElement) {
    return existing;
  }

  const heading = findWilsyR8CTextElement(switchboard, 'Operating Skin Switchboard')
    || findWilsyR8CTextElement(switchboard, 'Theme Control Panel');

  if (!(heading instanceof HTMLElement)) {
    return null;
  }

  const header = document.createElement('div');
  header.setAttribute(WILSY_R8C_THEME_STICKY_HEADER_MARKER, 'true');

  let cursor = heading.parentElement;
  const headerChildren = [];

  if (cursor instanceof HTMLElement) {
    Array.from(cursor.children).forEach(child => {
      if (!(child instanceof HTMLElement)) {
        return;
      }

      const text = readWilsyR8CText(child);

      if (
        /Theme Control Panel|Operating Skin Switchboard|Select the Wilsy visual language|Active ·/i.test(text)
        || child.contains(heading)
      ) {
        headerChildren.push(child);
      }
    });
  }

  if (headerChildren.length === 0) {
    headerChildren.push(heading);
  }

  const first = headerChildren[0];
  first.parentElement?.insertBefore(header, first);

  headerChildren.forEach(child => header.appendChild(child));

  return header;
}

/**
 * @function resolveWilsyR8CThemeGrid
 * @description Resolves or stamps the scrollable theme grid inside the switchboard.
 * @param {HTMLElement} switchboard - Theme switchboard region.
 * @returns {HTMLElement | null} Theme grid region.
 * @collaboration Gives theme previews their own cinematic viewport without consuming the whole Account page.
 */
function resolveWilsyR8CThemeGrid(switchboard) {
  const existing = switchboard.querySelector(`[${WILSY_R8C_THEME_SCROLL_GRID_MARKER}="true"]`);

  if (existing instanceof HTMLElement) {
    return existing;
  }

  const cards = Array.from(switchboard.querySelectorAll('[data-wilsy-theme-option], [data-wilsy-r7l-skin-card], article, button')).filter(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    const text = readWilsyR8CText(element);
    const rect = element.getBoundingClientRect();

    return rect.width >= 120 && rect.height >= 70 && /Aurora|Black|Glass|Command|Gold|Violet|Blue|Revenue|Security|Government|Startup|Mode|Boardroom|Field/i.test(text);
  });

  if (cards.length < 4) {
    return null;
  }

  const commonParent = cards[0].parentElement;

  if (!(commonParent instanceof HTMLElement)) {
    return null;
  }

  commonParent.setAttribute(WILSY_R8C_THEME_SCROLL_GRID_MARKER, 'true');

  cards.forEach((card, index) => {
    if (card instanceof HTMLElement) {
      card.setAttribute('data-wilsy-r8c-theme-card', 'true');
      card.style.setProperty('--wilsy-r8c-theme-index', String(index));
    }
  });

  return commonParent;
}

/**
 * @function resolveWilsyR8CModeSelector
 * @description Resolves the Day, Night and Auto command selector region.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Mode selector region.
 * @collaboration Compacts the mode strip so the actual skin switchboard enters the viewport sooner.
 */
function resolveWilsyR8CModeSelector(root) {
  const day = findWilsyR8CTextElement(root, 'Day Command');
  const night = findWilsyR8CTextElement(root, 'Night Command');
  const auto = findWilsyR8CTextElement(root, 'Auto Command');

  if (!(day instanceof HTMLElement) || !(night instanceof HTMLElement) || !(auto instanceof HTMLElement)) {
    return null;
  }

  let cursor = day.parentElement;

  for (let depth = 0; depth < 8 && cursor instanceof HTMLElement; depth += 1) {
    const text = readWilsyR8CText(cursor);

    if (text.includes('Day Command') && text.includes('Night Command') && text.includes('Auto Command')) {
      return cursor;
    }

    cursor = cursor.parentElement;
  }

  return day.parentElement;
}

/**
 * @function stampWilsyR8CThemeViewport
 * @description Applies viewport-first chrome to the theme switchboard and mode selector.
 * @returns {void}
 * @collaboration Makes the Account preferences experience scrollable, uniform and readable without changing data contracts.
 */
function stampWilsyR8CThemeViewport() {
  const root = resolveWilsyR8CAccountRoot();

  if (!(root instanceof HTMLElement)) {
    return;
  }

  root.dataset.wilsyR8cThemeViewportRuntime = 'true';

  const modeSelector = resolveWilsyR8CModeSelector(root);

  if (modeSelector instanceof HTMLElement) {
    modeSelector.setAttribute('data-wilsy-r8c-mode-selector', 'true');
  }

  const switchboard = resolveWilsyR8CThemeSwitchboard(root);

  if (!(switchboard instanceof HTMLElement)) {
    return;
  }

  switchboard.setAttribute(WILSY_R8C_THEME_VIEWPORT_SWITCHBOARD_MARKER, 'true');

  const header = resolveWilsyR8CThemeHeader(switchboard);

  if (header instanceof HTMLElement) {
    header.setAttribute(WILSY_R8C_THEME_STICKY_HEADER_MARKER, 'true');
  }

  const grid = resolveWilsyR8CThemeGrid(switchboard);

  if (grid instanceof HTMLElement) {
    grid.setAttribute(WILSY_R8C_THEME_SCROLL_GRID_MARKER, 'true');
  }
}

/**
 * @function queueWilsyR8CThemeViewportStamp
 * @description Queues theme viewport stamping on the next animation frame.
 * @returns {number | undefined} Browser animation frame request identifier.
 * @collaboration Avoids document-level observer storms while keeping Account chrome responsive.
 */
function queueWilsyR8CThemeViewportStamp() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR8CThemeViewport);
}

/**
 * @function bootWilsyR8CThemeViewportRuntime
 * @description Boots the theme viewport switchboard runtime once.
 * @returns {void}
 * @collaboration Runs on explicit lifecycle events only and preserves Account Command Center stability.
 */
function bootWilsyR8CThemeViewportRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R8C_THEME_VIEWPORT_RUNTIME__) {
    return;
  }

  window.__WILSY_R8C_THEME_VIEWPORT_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR8CThemeViewportStamp, { once: true });
  } else {
    queueWilsyR8CThemeViewportStamp();
  }

  for (let attempt = 1; attempt <= 8; attempt += 1) {
    window.setTimeout(queueWilsyR8CThemeViewportStamp, attempt * 140);
  }

  document.addEventListener('click', queueWilsyR8CThemeViewportStamp);
  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR8CThemeViewportStamp);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR8CThemeViewportStamp);
  window.addEventListener('resize', queueWilsyR8CThemeViewportStamp);
}

bootWilsyR8CThemeViewportRuntime();



const WILSY_R8D_COMMAND_IDENTITY_LABEL_MARKER = 'data-wilsy-r8d-command-identity-label';
const WILSY_R8D_TENANT_VERIFIED_LABEL_MARKER = 'data-wilsy-r8d-tenant-verified-label';
const WILSY_R8D_COMMAND_IDENTITY_HEADER_ROW_MARKER = 'data-wilsy-r8d-command-identity-header-row';
const WILSY_R8D_COMMAND_IDENTITY_SAFE_ZONE_MARKER = 'data-wilsy-r8d-command-identity-safe-zone';

/**
 * @function readWilsyR8DText
 * @description Reads normalized visible text from a DOM element.
 * @param {Element | null} element - Candidate DOM element.
 * @returns {string} Normalized text.
 * @collaboration Lets Wilsy OS identify command identity labels without brittle generated class selectors.
 */
function readWilsyR8DText(element) {
  return String(element?.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyR8DAccountRoot
 * @description Resolves the Account Command Center root.
 * @returns {HTMLElement | null} Account root.
 * @collaboration Scopes command identity label repair to the Account Command Center only.
 */
function resolveWilsyR8DAccountRoot() {
  if (typeof document === 'undefined') {
    return null;
  }

  return document.querySelector('[data-wilsy-account-command-center="true"]');
}

/**
 * @function findWilsyR8DElementsByText
 * @description Finds elements by normalized text pattern.
 * @param {HTMLElement} root - Search root.
 * @param {RegExp} pattern - Text pattern.
 * @returns {HTMLElement[]} Matching elements.
 * @collaboration Enables source-safe chrome stamping without mutating user data.
 */
function findWilsyR8DElementsByText(root, pattern) {
  return Array.from(root.querySelectorAll('*')).filter(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    return pattern.test(readWilsyR8DText(element));
  });
}

/**
 * @function resolveWilsyR8DCommandIdentityLabel
 * @description Resolves the visible Command Identity label that currently truncates.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Command Identity label.
 * @collaboration Gives the command label a first-class Wilsy OS Chrome contract.
 */
function resolveWilsyR8DCommandIdentityLabel(root) {
  const labels = findWilsyR8DElementsByText(root, /^COMMAND IDEN(?:TITY|\.\.\.)?$/i)
    .filter(element => !/^FOUNDER COMMAND IDENTITY$/i.test(readWilsyR8DText(element)));

  return labels[0] || null;
}

/**
 * @function resolveWilsyR8DTenantVerifiedLabel
 * @description Resolves the Tenant Verified label near Command Identity.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Tenant verified label.
 * @collaboration Preserves verification authority beside the command identity label.
 */
function resolveWilsyR8DTenantVerifiedLabel(root) {
  return findWilsyR8DElementsByText(root, /TENANT VERIFIED/i)[0] || null;
}

/**
 * @function resolveWilsyR8DCommonHeaderRow
 * @description Resolves the nearest shared header row for command identity and tenant verification.
 * @param {HTMLElement} label - Command Identity label.
 * @param {HTMLElement | null} verified - Tenant verified label.
 * @returns {HTMLElement | null} Header row.
 * @collaboration Prevents label truncation and badge crowding in the command identity card.
 */
function resolveWilsyR8DCommonHeaderRow(label, verified) {
  let cursor = label.parentElement;

  for (let depth = 0; depth < 7 && cursor instanceof HTMLElement; depth += 1) {
    const text = readWilsyR8DText(cursor);

    if (
      text.includes('COMMAND')
      && (!verified || cursor.contains(verified))
      && text.length < 180
    ) {
      return cursor;
    }

    cursor = cursor.parentElement;
  }

  return label.parentElement;
}

/**
 * @function stampWilsyR8DCommandIdentitySafeZones
 * @description Stamps overflow-safe ancestors so the command identity label can breathe.
 * @param {HTMLElement} label - Command Identity label.
 * @param {HTMLElement | null} row - Header row.
 * @returns {void}
 * @collaboration Removes cheap ellipsis behavior without changing Account data.
 */
function stampWilsyR8DCommandIdentitySafeZones(label, row) {
  let cursor = label.parentElement;

  for (let depth = 0; depth < 5 && cursor instanceof HTMLElement; depth += 1) {
    cursor.setAttribute(WILSY_R8D_COMMAND_IDENTITY_SAFE_ZONE_MARKER, 'true');
    cursor = cursor.parentElement;
  }

  if (row instanceof HTMLElement) {
    row.setAttribute(WILSY_R8D_COMMAND_IDENTITY_HEADER_ROW_MARKER, 'true');
  }
}

/**
 * @function stampWilsyR8DCommandIdentityLabel
 * @description Applies Wilsy OS Chrome authority to the Command Identity label and verification row.
 * @returns {void}
 * @collaboration Makes the label read like a command system, not a truncated admin form caption.
 */
function stampWilsyR8DCommandIdentityLabel() {
  const root = resolveWilsyR8DAccountRoot();

  if (!(root instanceof HTMLElement)) {
    return;
  }

  root.dataset.wilsyR8dCommandIdentityLabelAuthority = 'true';

  const label = resolveWilsyR8DCommandIdentityLabel(root);
  const verified = resolveWilsyR8DTenantVerifiedLabel(root);

  if (!(label instanceof HTMLElement)) {
    return;
  }

  label.textContent = 'COMMAND IDENTITY';
  label.setAttribute(WILSY_R8D_COMMAND_IDENTITY_LABEL_MARKER, 'true');

  if (verified instanceof HTMLElement) {
    verified.setAttribute(WILSY_R8D_TENANT_VERIFIED_LABEL_MARKER, 'true');
  }

  const row = resolveWilsyR8DCommonHeaderRow(label, verified);
  stampWilsyR8DCommandIdentitySafeZones(label, row);
}

/**
 * @function queueWilsyR8DCommandIdentityLabelStamp
 * @description Queues command identity label stamping on the next animation frame.
 * @returns {number | undefined} Browser animation frame request identifier.
 * @collaboration Keeps Wilsy OS Chrome repair performance-safe and observer-free.
 */
function queueWilsyR8DCommandIdentityLabelStamp() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR8DCommandIdentityLabel);
}

/**
 * @function bootWilsyR8DCommandIdentityLabelRuntime
 * @description Boots the Command Identity label authority runtime once.
 * @returns {void}
 * @collaboration Applies the R8D chrome contract without growing WilsyAccountCommandCenter.jsx.
 */
function bootWilsyR8DCommandIdentityLabelRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R8D_COMMAND_IDENTITY_LABEL_RUNTIME__) {
    return;
  }

  window.__WILSY_R8D_COMMAND_IDENTITY_LABEL_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR8DCommandIdentityLabelStamp, { once: true });
  } else {
    queueWilsyR8DCommandIdentityLabelStamp();
  }

  for (let attempt = 1; attempt <= 8; attempt += 1) {
    window.setTimeout(queueWilsyR8DCommandIdentityLabelStamp, attempt * 140);
  }

  document.addEventListener('click', queueWilsyR8DCommandIdentityLabelStamp);
  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR8DCommandIdentityLabelStamp);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR8DCommandIdentityLabelStamp);
  window.addEventListener('resize', queueWilsyR8DCommandIdentityLabelStamp);
}

bootWilsyR8DCommandIdentityLabelRuntime();


/**
 * @function bootWilsyAccountRuntimeEnhancers
 * @description Confirms the extracted Wilsy Account runtime enhancer module has loaded.
 * @returns {version: string, loaded: boolean} Runtime enhancer status.
 * @collaboration Gives the Account Command Center and guards a stable extraction marker without changing visual behavior.
 */
export function bootWilsyAccountRuntimeEnhancers() {
  return {
    version: WILSY_ACCOUNT_RUNTIME_ENHANCERS_VERSION,
    loaded: true
  };
}


const WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND_MARKER = 'data-wilsy-r8f-command-routes-source-bound';
const WILSY_R8F_COMMAND_ROUTE_CARD_MARKER = 'data-wilsy-r8f-command-route-card';
const WILSY_R8F_COMMAND_ROUTE_DETAIL_MARKER = 'data-wilsy-r8f-command-route-detail';

/**
 * @function readWilsyR8FText
 * @description Reads normalized text from a DOM element.
 * @param {Element | null} element - Candidate DOM element.
 * @returns {string} Normalized text.
 * @collaboration Locates existing route regions without generated class assumptions.
 */
function readWilsyR8FText(element) {
  return String(element?.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyR8FAccountRoot
 * @description Resolves the Account Command Center DOM root.
 * @returns {HTMLElement | null} Account root.
 * @collaboration Keeps route binding scoped to Account Command Center.
 */
function resolveWilsyR8FAccountRoot() {
  if (typeof document === 'undefined') {
    return null;
  }

  return document.querySelector('[data-wilsy-account-command-center="true"]');
}

/**
 * @function findWilsyR8FElementByText
 * @description Finds the first element matching a text pattern.
 * @param {HTMLElement} root - Search root.
 * @param {RegExp} pattern - Text pattern.
 * @returns {HTMLElement | null} Matching element.
 * @collaboration Lets the route binder attach to the Command Routes section without fake source.
 */
function findWilsyR8FElementByText(root, pattern) {
  return Array.from(root.querySelectorAll('*')).find(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    return pattern.test(readWilsyR8FText(element));
  }) || null;
}

/**
 * @function resolveWilsyR8FCommandRoutesRegion
 * @description Resolves the visual Command Routes card region.
 * @param {HTMLElement} root - Account root.
 * @returns {HTMLElement | null} Route region.
 * @collaboration Converts existing blank route cards into source-bound Wilsy OS command gateways.
 */
function resolveWilsyR8FCommandRoutesRegion(root) {
  const direct = root.querySelector('[data-wilsy-r7o-route-section], [data-wilsy-r7p-route-section], [data-wilsy-command-routes]');

  if (direct instanceof HTMLElement) {
    return direct;
  }

  const heading = findWilsyR8FElementByText(root, /COMMAND ROUTES/i);

  if (heading instanceof HTMLElement) {
    let cursor = heading.parentElement;

    for (let depth = 0; depth < 8 && cursor instanceof HTMLElement; depth += 1) {
      const boxes = Array.from(cursor.querySelectorAll('button, article, div')).filter(element => {
        if (!(element instanceof HTMLElement)) {
          return false;
        }

        const rect = element.getBoundingClientRect();

        return rect.width >= 240 && rect.height >= 80 && rect.height <= 260 && element.querySelector('svg');
      });

      if (boxes.length >= 4) {
        return cursor;
      }

      cursor = cursor.parentElement;
    }

    return heading.parentElement;
  }

  const routeCandidates = Array.from(root.querySelectorAll('[data-wilsy-r7o-route-unbound], [data-wilsy-r7p-route-unbound], [data-wilsy-r7o-route-pending-card], [data-wilsy-r7p-route-pending-card]'));

  if (routeCandidates.length) {
    let cursor = routeCandidates[0].parentElement;

    for (let depth = 0; depth < 6 && cursor instanceof HTMLElement; depth += 1) {
      if (cursor.querySelectorAll('[data-wilsy-r7o-route-unbound], [data-wilsy-r7p-route-unbound], [data-wilsy-r7o-route-pending-card], [data-wilsy-r7p-route-pending-card]').length >= 4) {
        return cursor;
      }

      cursor = cursor.parentElement;
    }
  }

  return null;
}

/**
 * @function resolveWilsyR8FCommandRouteCards
 * @description Resolves route cards inside the command routes region.
 * @param {HTMLElement} region - Route region.
 * @returns {HTMLElement[]} Route cards.
 * @collaboration Gives each visible route card a real source-bound contract.
 */
function resolveWilsyR8FCommandRouteCards(region) {
  const marked = Array.from(region.querySelectorAll('[data-wilsy-r7o-route-unbound], [data-wilsy-r7p-route-unbound], [data-wilsy-r7o-route-pending-card], [data-wilsy-r7p-route-pending-card], [data-wilsy-r8f-command-route-card="true"]'))
    .filter(element => element instanceof HTMLElement);

  if (marked.length >= 4) {
    return marked;
  }

  return Array.from(region.querySelectorAll('button, article, div')).filter(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    const rect = element.getBoundingClientRect();
    const hasIcon = Boolean(element.querySelector('svg'));

    return hasIcon && rect.width >= 240 && rect.height >= 82 && rect.height <= 260;
  }).slice(0, 8);
}

/**
 * @function writeWilsyR8FRouteCopy
 * @description Writes readable, source-bound route copy into a card.
 * @param {HTMLElement} card - Route card.
 * @param {object} contract - Source-bound route contract.
 * @returns {void}
 * @collaboration Removes blank route cards and gives executives real route readiness.
 */
function writeWilsyR8FRouteCopy(card, contract) {
  card.setAttribute(WILSY_R8F_COMMAND_ROUTE_CARD_MARKER, 'true');
  card.setAttribute('data-wilsy-r8f-route-key', contract.key);
  card.setAttribute('role', 'button');
  card.setAttribute('tabindex', '0');

  const previous = card.querySelector('[data-wilsy-r8f-route-copy="true"]');

  if (previous instanceof HTMLElement) {
    previous.remove();
  }

  const receipt = buildWilsyR8FCommandRouteReceipt(contract);
  const copy = document.createElement('div');
  copy.setAttribute('data-wilsy-r8f-route-copy', 'true');

  const label = document.createElement('strong');
  label.setAttribute('data-wilsy-r8f-route-label', 'true');
  label.textContent = contract.label;

  const purpose = document.createElement('p');
  purpose.setAttribute('data-wilsy-r8f-route-purpose', 'true');
  purpose.textContent = contract.purpose;

  const meta = document.createElement('span');
  meta.setAttribute('data-wilsy-r8f-route-meta', 'true');
  meta.textContent = `${receipt.status} · ${receipt.readiness}% · ${receipt.preferredAction}`;

  const evidence = document.createElement('span');
  evidence.setAttribute('data-wilsy-r8f-route-evidence', 'true');
  evidence.textContent = `tenant ${receipt.signalSummary.tenantSignals} · audit ${receipt.signalSummary.auditSignals} · auth ${receipt.signalSummary.authSignals} · db ${receipt.signalSummary.databaseSignals}`;

  copy.append(label, purpose, meta, evidence);
  card.appendChild(copy);

  card.onclick = () => renderWilsyR8FRouteDetail(card, contract);

  card.onkeydown = event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      renderWilsyR8FRouteDetail(card, contract);
    }
  };
}

/**
 * @function renderWilsyR8FRouteDetail
 * @description Renders source-bound drill-down details for a selected command route.
 * @param {HTMLElement} card - Selected route card.
 * @param {object} contract - Source-bound route contract.
 * @returns {void}
 * @collaboration Turns command route cards into operational gateways with evidence, targets and receipts.
 */
function renderWilsyR8FRouteDetail(card, contract) {
  const region = card.closest('[data-wilsy-r8f-command-routes-source-bound="true"]') || card.parentElement;

  if (!(region instanceof HTMLElement)) {
    return;
  }

  Array.from(region.querySelectorAll('[data-wilsy-r8f-command-route-card="true"]')).forEach(routeCard => {
    if (routeCard instanceof HTMLElement) {
      routeCard.dataset.wilsyR8fRouteActive = String(routeCard === card);
    }
  });

  let detail = region.querySelector(`[${WILSY_R8F_COMMAND_ROUTE_DETAIL_MARKER}="true"]`);

  if (!(detail instanceof HTMLElement)) {
    detail = document.createElement('section');
    detail.setAttribute(WILSY_R8F_COMMAND_ROUTE_DETAIL_MARKER, 'true');
    region.appendChild(detail);
  }

  const receipt = buildWilsyR8FCommandRouteReceipt(contract);
  detail.replaceChildren();

  const eyebrow = document.createElement('span');
  eyebrow.setAttribute('data-wilsy-r8f-detail-eyebrow', 'true');
  eyebrow.textContent = 'SOURCE-BOUND COMMAND ROUTE';

  const title = document.createElement('h3');
  title.textContent = contract.label;

  const summary = document.createElement('p');
  summary.textContent = contract.purpose;

  const action = document.createElement('button');
  action.type = 'button';
  action.setAttribute('data-wilsy-r8f-detail-action', 'true');
  action.textContent = contract.executiveAction || 'Open Route Contract';

  action.onclick = () => {
    window.dispatchEvent(new CustomEvent('wilsy-command-route-selected', {
      detail: {
        contract,
        receipt,
        source: 'WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND'
      }
    }));

    if (contract.target?.clientRoute) {
      window.history.pushState({}, '', contract.target.clientRoute);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  const evidence = document.createElement('div');
  evidence.setAttribute('data-wilsy-r8f-detail-evidence', 'true');

  [
    ['Client route', contract.target?.clientRoute || 'Server/API contract available'],
    ['API contract', contract.target?.apiCall || 'No direct client API captured'],
    ['Server route', contract.target?.serverRoute || 'No direct server route captured'],
    ['Services', String(receipt.signalSummary.serviceFiles || 0)],
    ['Models', String(receipt.signalSummary.modelFiles || 0)],
    ['Signals', `tenant ${receipt.signalSummary.tenantSignals} · audit ${receipt.signalSummary.auditSignals} · auth ${receipt.signalSummary.authSignals} · db ${receipt.signalSummary.databaseSignals}`]
  ].forEach(([key, value]) => {
    const item = document.createElement('div');
    const k = document.createElement('span');
    const v = document.createElement('strong');

    k.textContent = key;
    v.textContent = value;

    item.append(k, v);
    evidence.appendChild(item);
  });

  detail.append(eyebrow, title, summary, evidence, action);
}

/**
 * @function stampWilsyR8FSourceBoundCommandRoutes
 * @description Binds command route cards to source-bound route contracts.
 * @returns {void}
 * @collaboration Connects visual cards to repository-discovered Wilsy OS routes, services and evidence.
 */
function stampWilsyR8FSourceBoundCommandRoutes() {
  const root = resolveWilsyR8FAccountRoot();

  if (!(root instanceof HTMLElement)) {
    return;
  }

  const region = resolveWilsyR8FCommandRoutesRegion(root);

  if (!(region instanceof HTMLElement)) {
    return;
  }

  const contracts = resolveWilsyR8FCommandRouteContracts();
  const cards = resolveWilsyR8FCommandRouteCards(region);

  if (!contracts.length || !cards.length) {
    return;
  }

  region.setAttribute(WILSY_R8F_COMMAND_ROUTES_SOURCE_BOUND_MARKER, 'true');

  cards.slice(0, contracts.length).forEach((card, index) => {
    writeWilsyR8FRouteCopy(card, contracts[index]);
  });
}

/**
 * @function queueWilsyR8FSourceBoundCommandRoutes
 * @description Queues route binding on the next animation frame.
 * @returns {number | undefined} Animation frame handle.
 * @collaboration Keeps source-bound command route binding performance-safe.
 */
function queueWilsyR8FSourceBoundCommandRoutes() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(stampWilsyR8FSourceBoundCommandRoutes);
}

/**
 * @function bootWilsyR8FSourceBoundCommandRoutesRuntime
 * @description Boots the source-bound command routes runtime once.
 * @returns {void}
 * @collaboration Turns Account command route cards into real Wilsy OS gateways without Account JSX growth.
 */
function bootWilsyR8FSourceBoundCommandRoutesRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R8F_COMMAND_ROUTES_RUNTIME__) {
    return;
  }

  window.__WILSY_R8F_COMMAND_ROUTES_RUNTIME__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR8FSourceBoundCommandRoutes, { once: true });
  } else {
    queueWilsyR8FSourceBoundCommandRoutes();
  }

  for (let attempt = 1; attempt <= 10; attempt += 1) {
    window.setTimeout(queueWilsyR8FSourceBoundCommandRoutes, attempt * 140);
  }

  document.addEventListener('click', queueWilsyR8FSourceBoundCommandRoutes);
  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR8FSourceBoundCommandRoutes);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR8FSourceBoundCommandRoutes);
  window.addEventListener('resize', queueWilsyR8FSourceBoundCommandRoutes);
}

bootWilsyR8FSourceBoundCommandRoutesRuntime();


const WILSY_R8G_COMMAND_ROUTES_DOM_PROOF_MARKER = 'data-wilsy-r8g-command-routes-dom-proof';
const WILSY_R8G_COMMAND_ROUTE_DECK_MARKER = 'data-wilsy-r8g-command-route-deck';
const WILSY_R8G_COMMAND_ROUTE_CARD_MARKER = 'data-wilsy-r8g-command-route-card';
const WILSY_R8G_COMMAND_ROUTE_DETAIL_MARKER = 'data-wilsy-r8g-command-route-detail';

/**
 * @function readWilsyR8GText
 * @description Reads normalized visible text from a DOM element.
 * @param {Element | null} element - Candidate DOM element.
 * @returns {string} Normalized text.
 * @collaboration Helps Wilsy OS locate the Command Routes section without generated class selectors.
 */
function readWilsyR8GText(element) {
  return String(element?.textContent || '').replace(/\s+/g, ' ').trim();
}

/**
 * @function resolveWilsyR8GAccountRoot
 * @description Resolves the Account Command Center root.
 * @returns {HTMLElement | null} Account root.
 * @collaboration Keeps DOM-proof route replacement scoped to Account Command Center only.
 */
function resolveWilsyR8GAccountRoot() {
  if (typeof document === 'undefined') {
    return null;
  }

  return document.querySelector('[data-wilsy-account-command-center="true"]');
}

/**
 * @function findWilsyR8GElementByText
 * @description Finds the first element matching a text pattern.
 * @param {HTMLElement} root - Search root.
 * @param {RegExp} pattern - Text pattern.
 * @returns {HTMLElement | null} Matching element.
 * @collaboration Locates Account sub-sections in the current rendered DOM.
 */
function findWilsyR8GElementByText(root, pattern) {
  return Array.from(root.querySelectorAll('*')).find(element => {
    if (!(element instanceof HTMLElement)) {
      return false;
    }

    return pattern.test(readWilsyR8GText(element));
  }) || null;
}

/**
 * @function resolveWilsyR8GCommandRoutesSection
 * @description Resolves the rendered Command Routes section.
 * @param {HTMLElement} root - Account root.
 * @returns {{ section: HTMLElement, heading: HTMLElement } | null} Route section and heading.
 * @collaboration Finds the existing blank route deck so Wilsy can replace it with source-bound contracts.
 */
function resolveWilsyR8GCommandRoutesSection(root) {
  const heading = findWilsyR8GElementByText(root, /^COMMAND ROUTES$/i);

  if (!(heading instanceof HTMLElement)) {
    return null;
  }

  let cursor = heading.parentElement;

  for (let depth = 0; depth < 8 && cursor instanceof HTMLElement; depth += 1) {
    const iconCount = cursor.querySelectorAll('svg').length;
    const rect = cursor.getBoundingClientRect();

    if (iconCount >= 4 && rect.width >= 600) {
      return { section: cursor, heading };
    }

    cursor = cursor.parentElement;
  }

  if (heading.parentElement instanceof HTMLElement) {
    return { section: heading.parentElement, heading };
  }

  return null;
}

/**
 * @function isWilsyR8GBlankRouteCard
 * @description Detects one of the current blank route icon cards.
 * @param {HTMLElement} element - Candidate route card.
 * @returns {boolean} Whether the element is a blank route card.
 * @collaboration Lets R8G hide decorative empty cards while rendering real route contracts.
 */
function isWilsyR8GBlankRouteCard(element) {
  if (!(element instanceof HTMLElement)) {
    return false;
  }

  if (element.closest(`[${WILSY_R8G_COMMAND_ROUTE_DECK_MARKER}="true"]`)) {
    return false;
  }

  const rect = element.getBoundingClientRect();
  const hasIcon = Boolean(element.querySelector('svg'));
  const text = readWilsyR8GText(element);

  return hasIcon && rect.width >= 240 && rect.height >= 70 && rect.height <= 280 && text.length <= 8;
}

/**
 * @function hideWilsyR8GBlankRouteCards
 * @description Hides existing blank route cards after the source-bound deck is rendered.
 * @param {HTMLElement} section - Command Routes section.
 * @returns {void}
 * @collaboration Prevents duplicate decks and removes empty icon-only UI.
 */
function hideWilsyR8GBlankRouteCards(section) {
  Array.from(section.querySelectorAll('button, article, div')).forEach(element => {
    if (!(element instanceof HTMLElement)) {
      return;
    }

    if (isWilsyR8GBlankRouteCard(element)) {
      element.setAttribute('data-wilsy-r8g-hidden-blank-route-card', 'true');
      element.style.display = 'none';
    }
  });
}

/**
 * @function buildWilsyR8GEvidenceLine
 * @description Builds a concise evidence line from a route receipt.
 * @param {object} receipt - Route receipt.
 * @returns {string} Evidence summary.
 * @collaboration Surfaces tenant, audit, auth and database source signals on every card.
 */
function buildWilsyR8GEvidenceLine(receipt) {
  const signal = receipt.signalSummary || {};

  return `tenant ${signal.tenantSignals || 0} · audit ${signal.auditSignals || 0} · auth ${signal.authSignals || 0} · db ${signal.databaseSignals || 0}`;
}

/**
 * @function renderWilsyR8GRouteDetail
 * @description Renders source-bound evidence for the selected route.
 * @param {HTMLElement} deck - Source-bound route deck.
 * @param {object} contract - Route contract.
 * @returns {void}
 * @collaboration Converts a command route click into a real evidence drill-down.
 */
function renderWilsyR8GRouteDetail(deck, contract) {
  const receipt = buildWilsyR8FCommandRouteReceipt(contract);
  let detail = deck.querySelector(`[${WILSY_R8G_COMMAND_ROUTE_DETAIL_MARKER}="true"]`);

  if (!(detail instanceof HTMLElement)) {
    detail = document.createElement('section');
    detail.setAttribute(WILSY_R8G_COMMAND_ROUTE_DETAIL_MARKER, 'true');
    deck.appendChild(detail);
  }

  Array.from(deck.querySelectorAll(`[${WILSY_R8G_COMMAND_ROUTE_CARD_MARKER}="true"]`)).forEach(card => {
    if (card instanceof HTMLElement) {
      card.dataset.wilsyR8gRouteActive = String(card.dataset.wilsyR8gRouteKey === contract.key);
    }
  });

  detail.replaceChildren();

  const eyebrow = document.createElement('span');
  eyebrow.setAttribute('data-wilsy-r8g-detail-eyebrow', 'true');
  eyebrow.textContent = 'SOURCE-BOUND ROUTE RECEIPT';

  const title = document.createElement('h3');
  title.textContent = contract.label;

  const summary = document.createElement('p');
  summary.textContent = contract.purpose;

  const matrix = document.createElement('div');
  matrix.setAttribute('data-wilsy-r8g-detail-matrix', 'true');

  [
    ['Status', `${receipt.status} · ${receipt.readiness}%`],
    ['Action', receipt.preferredAction],
    ['Client route', contract.target?.clientRoute || 'Not captured'],
    ['API contract', contract.target?.apiCall || 'Not captured'],
    ['Server route', contract.target?.serverRoute || 'Not captured'],
    ['Evidence', buildWilsyR8GEvidenceLine(receipt)]
  ].forEach(([label, value]) => {
    const cell = document.createElement('div');
    const key = document.createElement('span');
    const val = document.createElement('strong');

    key.textContent = label;
    val.textContent = value;

    cell.append(key, val);
    matrix.appendChild(cell);
  });

  const action = document.createElement('button');
  action.type = 'button';
  action.setAttribute('data-wilsy-r8g-route-action', 'true');
  action.textContent = contract.executiveAction || 'Open Source Route';

  action.onclick = () => {
    window.dispatchEvent(new CustomEvent('wilsy-command-route-selected', {
      detail: {
        contract,
        receipt,
        source: 'WILSY_R8G_COMMAND_ROUTES_DOM_PROOF'
      }
    }));

    if (contract.target?.clientRoute) {
      window.history.pushState({}, '', contract.target.clientRoute);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  detail.append(eyebrow, title, summary, matrix, action);
}

/**
 * @function renderWilsyR8GRouteCard
 * @description Renders one source-bound command route card.
 * @param {object} contract - Source-bound route contract.
 * @param {HTMLElement} deck - Route deck.
 * @returns {HTMLElement} Rendered route card.
 * @collaboration Replaces blank icon-only cards with operational Wilsy OS route contracts.
 */
function renderWilsyR8GRouteCard(contract, deck) {
  const receipt = buildWilsyR8FCommandRouteReceipt(contract);
  const card = document.createElement('button');

  card.type = 'button';
  card.setAttribute(WILSY_R8G_COMMAND_ROUTE_CARD_MARKER, 'true');
  card.dataset.wilsyR8gRouteKey = contract.key || receipt.key;

  const top = document.createElement('div');
  top.setAttribute('data-wilsy-r8g-route-topline', 'true');

  const label = document.createElement('strong');
  label.textContent = contract.label;

  const status = document.createElement('span');
  status.textContent = `${receipt.readiness}%`;

  top.append(label, status);

  const purpose = document.createElement('p');
  purpose.textContent = contract.purpose;

  const meta = document.createElement('span');
  meta.setAttribute('data-wilsy-r8g-route-meta', 'true');
  meta.textContent = `${receipt.status} · ${receipt.preferredAction}`;

  const evidence = document.createElement('span');
  evidence.setAttribute('data-wilsy-r8g-route-evidence', 'true');
  evidence.textContent = buildWilsyR8GEvidenceLine(receipt);

  card.append(top, purpose, meta, evidence);

  card.onclick = () => renderWilsyR8GRouteDetail(deck, contract);

  return card;
}

/**
 * @function replaceWilsyR8GCommandRoutesDeck
 * @description Replaces the blank command routes deck with a source-bound contract deck.
 * @returns {void}
 * @collaboration Makes Command Routes visible even when backend APIs return 503.
 */
function replaceWilsyR8GCommandRoutesDeck() {
  const root = resolveWilsyR8GAccountRoot();

  if (!(root instanceof HTMLElement)) {
    return;
  }

  const resolved = resolveWilsyR8GCommandRoutesSection(root);

  if (!resolved) {
    return;
  }

  const { section, heading } = resolved;
  const contracts = resolveWilsyR8FCommandRouteContracts();

  if (!Array.isArray(contracts) || contracts.length === 0) {
    return;
  }

  section.setAttribute(WILSY_R8G_COMMAND_ROUTES_DOM_PROOF_MARKER, 'true');

  let deck = section.querySelector(`[${WILSY_R8G_COMMAND_ROUTE_DECK_MARKER}="true"]`);

  if (!(deck instanceof HTMLElement)) {
    deck = document.createElement('div');
    deck.setAttribute(WILSY_R8G_COMMAND_ROUTE_DECK_MARKER, 'true');

    const afterHeading = heading.nextElementSibling;

    if (afterHeading instanceof HTMLElement) {
      section.insertBefore(deck, afterHeading);
    } else {
      section.appendChild(deck);
    }
  }

  const activeKey = deck.querySelector(`[${WILSY_R8G_COMMAND_ROUTE_CARD_MARKER}="true"][data-wilsy-r8g-route-active="true"]`)?.dataset?.wilsyR8gRouteKey;

  deck.replaceChildren();

  contracts.forEach(contract => {
    deck.appendChild(renderWilsyR8GRouteCard(contract, deck));
  });

  if (activeKey) {
    const activeContract = contracts.find(contract => contract.key === activeKey);

    if (activeContract) {
      renderWilsyR8GRouteDetail(deck, activeContract);
    }
  }

  hideWilsyR8GBlankRouteCards(section);
}

/**
 * @function queueWilsyR8GCommandRoutesDomProof
 * @description Queues DOM-proof deck replacement on the next animation frame.
 * @returns {number | undefined} Animation frame handle.
 * @collaboration Keeps route deck replacement fast and scoped.
 */
function queueWilsyR8GCommandRoutesDomProof() {
  if (typeof window === 'undefined') {
    return undefined;
  }

  return window.requestAnimationFrame(replaceWilsyR8GCommandRoutesDeck);
}

/**
 * @function bootWilsyR8GCommandRoutesDomProofRuntime
 * @description Boots the DOM-proof source-bound command routes deck runtime.
 * @returns {void}
 * @collaboration Ensures Command Routes never render as blank decorative cards.
 */
function bootWilsyR8GCommandRoutesDomProofRuntime() {
  if (typeof window === 'undefined' || window.__WILSY_R8G_COMMAND_ROUTES_DOM_PROOF__) {
    return;
  }

  window.__WILSY_R8G_COMMAND_ROUTES_DOM_PROOF__ = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueWilsyR8GCommandRoutesDomProof, { once: true });
  } else {
    queueWilsyR8GCommandRoutesDomProof();
  }

  for (let attempt = 1; attempt <= 14; attempt += 1) {
    window.setTimeout(queueWilsyR8GCommandRoutesDomProof, attempt * 160);
  }

  document.addEventListener('click', queueWilsyR8GCommandRoutesDomProof);
  window.addEventListener('wilsy-theme-runtime-applied', queueWilsyR8GCommandRoutesDomProof);
  window.addEventListener('wilsy-r7j-performance-safe-restamp', queueWilsyR8GCommandRoutesDomProof);
  window.addEventListener('resize', queueWilsyR8GCommandRoutesDomProof);
}

bootWilsyR8GCommandRoutesDomProofRuntime();

