/* eslint-disable */

const CRM_SEARCH_SELECTOR = [
  'input[aria-label="Global CRM search"]',
  'input[placeholder="Search pipeline, accounts, evidence"]',
  'input[placeholder*="Search leads"]',
  'input[placeholder*="Search records"]',
  'input[aria-label*="Search Lead"]',
].join(',');

const CRM_SEARCH_SOURCES = Object.freeze([
  { label: 'Leads', endpoint: '/api/crm/live/leads' },
  { label: 'Contacts', endpoint: '/api/crm/live/contacts' },
  { label: 'Accounts', endpoint: '/api/crm/live/accounts' },
  { label: 'Deals', endpoint: '/api/crm/live/deals' },
  { label: 'Tasks', endpoint: '/api/crm/live/tasks' },
  { label: 'Meetings', endpoint: '/api/crm/live/meetings' },
  { label: 'Evidence', endpoint: '/api/crm/live/evidence' },
  { label: 'Connectors', endpoint: '/api/crm/live/connectors' },
  { label: 'Intel Leads', endpoint: '/api/crm/intelligence/leads' },
  { label: 'Intel Accounts', endpoint: '/api/crm/intelligence/accounts' },
  { label: 'Intel Deals', endpoint: '/api/crm/intelligence/deals' },
  { label: 'Source Posture', endpoint: '/api/crm/live/source-posture' },
]);

/**
 * @function resolveTenantId
 * @description Resolves the tenant id used for CRM live source searches.
 * @collaboration R74E inline result deck, tenant context, live CRM source requests.
 */
function resolveTenantId(tenantId) {
  return String(tenantId || 'MASTER').trim() || 'MASTER';
}

/**
 * @function buildRuntimeStyles
 * @description Builds compact inline result-deck styles for CRM Home and Leads search inputs.
 * @collaboration R74E OS-grade search deck, CRM Home search, Leads search.
 */
function buildRuntimeStyles() {
  return `
    [data-wilsy-r74e-search-deck="true"] {
      display: none;
      width: 100%;
      margin-top: 0.7rem;
      border: 1px solid rgba(96, 255, 176, 0.28);
      border-radius: 20px;
      background:
        linear-gradient(135deg, rgba(4, 18, 12, 0.96), rgba(1, 8, 6, 0.98)),
        rgba(1, 8, 6, 0.98);
      color: rgba(240, 255, 247, 0.98);
      box-shadow:
        0 0 0 1px rgba(96, 255, 176, 0.1),
        0 18px 42px rgba(0, 0, 0, 0.42),
        0 0 34px rgba(96, 255, 176, 0.14);
      overflow: hidden;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    [data-wilsy-r74e-search-deck="true"][data-open="true"] {
      display: block;
    }

    .wilsy-r74e-head {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 0.8rem;
      align-items: center;
      padding: 0.72rem 0.84rem;
      border-bottom: 1px solid rgba(96, 255, 176, 0.16);
      background: rgba(255, 255, 255, 0.035);
    }

    .wilsy-r74e-title-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      align-items: center;
      min-width: 0;
    }

    .wilsy-r74e-kicker {
      color: rgba(174, 255, 211, 0.7);
      font-size: 0.58rem;
      font-weight: 950;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .wilsy-r74e-query {
      min-width: 0;
      max-width: 100%;
      overflow: hidden;
      color: rgba(249, 255, 252, 0.98);
      font-size: 0.78rem;
      font-weight: 950;
      letter-spacing: 0.01em;
      text-overflow: ellipsis;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .wilsy-r74e-status {
      display: inline-flex;
      align-items: center;
      min-height: 1.72rem;
      padding: 0.28rem 0.56rem;
      border: 1px solid rgba(96, 255, 176, 0.24);
      border-radius: 999px;
      background: rgba(96, 255, 176, 0.08);
      color: rgba(226, 255, 239, 0.94);
      font-size: 0.58rem;
      font-weight: 950;
      letter-spacing: 0.085em;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .wilsy-r74e-status[data-tone="found"] {
      border-color: rgba(112, 255, 184, 0.48);
      background: rgba(96, 255, 176, 0.14);
      box-shadow: 0 0 22px rgba(96, 255, 176, 0.18);
    }

    .wilsy-r74e-status[data-tone="empty"] {
      border-color: rgba(255, 209, 118, 0.5);
      background: rgba(255, 209, 118, 0.12);
      color: rgba(255, 235, 194, 0.98);
    }

    .wilsy-r74e-status[data-tone="error"] {
      border-color: rgba(255, 110, 110, 0.5);
      background: rgba(255, 110, 110, 0.11);
      color: rgba(255, 221, 221, 0.98);
    }

    .wilsy-r74e-close {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1.85rem;
      height: 1.85rem;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.055);
      color: rgba(255, 255, 255, 0.84);
      cursor: pointer;
      font-size: 0.92rem;
      font-weight: 950;
    }

    .wilsy-r74e-body {
      display: grid;
      gap: 0.5rem;
      max-height: min(34vh, 320px);
      overflow: auto;
      padding: 0.68rem;
    }

    .wilsy-r74e-state {
      padding: 0.72rem 0.78rem;
      border: 1px solid rgba(96, 255, 176, 0.16);
      border-radius: 15px;
      background: rgba(96, 255, 176, 0.055);
      color: rgba(225, 242, 233, 0.9);
      font-size: 0.78rem;
      font-weight: 760;
      line-height: 1.42;
    }

    .wilsy-r74e-state[data-tone="empty"] {
      border-color: rgba(255, 209, 118, 0.3);
      background: rgba(255, 209, 118, 0.08);
      color: rgba(255, 238, 205, 0.94);
    }

    .wilsy-r74e-state[data-tone="error"] {
      border-color: rgba(255, 110, 110, 0.34);
      background: rgba(255, 110, 110, 0.08);
      color: rgba(255, 226, 226, 0.94);
    }

    .wilsy-r74e-grid {
      display: grid;
      gap: 0.48rem;
    }

    .wilsy-r74e-card {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 0.58rem;
      align-items: center;
      padding: 0.64rem 0.72rem;
      border: 1px solid rgba(96, 255, 176, 0.18);
      border-radius: 15px;
      background:
        linear-gradient(135deg, rgba(96, 255, 176, 0.075), rgba(255, 255, 255, 0.02)),
        rgba(3, 14, 9, 0.74);
    }

    .wilsy-r74e-main {
      display: grid;
      gap: 0.22rem;
      min-width: 0;
    }

    .wilsy-r74e-source {
      color: rgba(174, 255, 211, 0.62);
      font-size: 0.55rem;
      font-weight: 950;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }

    .wilsy-r74e-name {
      overflow: hidden;
      color: rgba(248, 255, 251, 0.98);
      font-size: 0.82rem;
      font-weight: 930;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .wilsy-r74e-meta {
      overflow: hidden;
      color: rgba(210, 232, 220, 0.72);
      font-size: 0.64rem;
      font-weight: 760;
      letter-spacing: 0.035em;
      text-overflow: ellipsis;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .wilsy-r74e-code {
      max-width: 12rem;
      overflow: hidden;
      padding: 0.25rem 0.44rem;
      border: 1px solid rgba(96, 255, 176, 0.16);
      border-radius: 999px;
      background: rgba(1, 8, 5, 0.82);
      color: rgba(205, 255, 226, 0.86);
      font-size: 0.56rem;
      font-weight: 850;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .wilsy-r74e-sources {
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
      padding: 0 0.68rem 0.68rem;
    }

    .wilsy-r74e-pill {
      padding: 0.22rem 0.38rem;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.04);
      color: rgba(226, 236, 231, 0.64);
      font-size: 0.5rem;
      font-weight: 880;
      letter-spacing: 0.055em;
      text-transform: uppercase;
    }

    @media (max-width: 720px) {
      .wilsy-r74e-card {
        grid-template-columns: 1fr;
      }
    }
  `;
}

/**
 * @function ensureRuntimeStyle
 * @description Installs or replaces the inline search result deck stylesheet.
 * @collaboration R74E styling, compact result deck, CRM operator search UX.
 */
function ensureRuntimeStyle(doc) {
  const styleId = 'wilsy-r74e-crm-search-inline-result-style';
  const oldStyle = doc.getElementById('wilsy-r74d-crm-search-outcome-style');
  const existing = doc.getElementById(styleId);

  oldStyle?.remove();

  if (existing) {
    existing.textContent = buildRuntimeStyles();
    return existing;
  }

  const style = doc.createElement('style');
  style.id = styleId;
  style.textContent = buildRuntimeStyles();
  doc.head.appendChild(style);

  return style;
}

/**
 * @function cleanupLegacyPanels
 * @description Removes stale modal search panels from previous runtime attempts.
 * @collaboration R74E migration, R74D modal removal, clean operator UI.
 */
function cleanupLegacyPanels(doc) {
  doc
    .querySelectorAll('[data-wilsy-r74d-crm-search-outcome-runtime="true"], [data-wilsy-r74e-search-deck="true"]')
    .forEach((node) => node.remove());
}

/**
 * @function getSearchInputs
 * @description Returns visible CRM Home and Leads search inputs.
 * @collaboration R74E actual DOM inputs, CRM Home search, Leads search.
 */
function getSearchInputs(doc) {
  return [...doc.querySelectorAll(CRM_SEARCH_SELECTOR)].filter((input) => {
    const rect = input.getBoundingClientRect();
    return rect.width > 220 && rect.height > 26 && input.offsetParent !== null;
  });
}

/**
 * @function findDeckAnchor
 * @description Finds the best DOM anchor immediately around the active search input.
 * @collaboration R74E inline result placement, actual search shell, non-modal UX.
 */
function findDeckAnchor(input) {
  return input.closest('label') || input.closest('form') || input.parentElement;
}

/**
 * @function createDeckForInput
 * @description Creates or returns the compact inline result deck for one search input.
 * @collaboration R74E per-input result deck, CRM Home and Leads search, DOM runtime.
 */
function createDeckForInput(input) {
  const anchor = findDeckAnchor(input);

  if (!anchor) {
    return null;
  }

  const existing = anchor.parentElement?.querySelector(`[data-wilsy-r74e-search-deck="true"][data-owner="${input.dataset.wilsyR74eSearchOwner}"]`);

  if (existing) {
    return existing;
  }

  const deck = document.createElement('section');
  deck.setAttribute('data-wilsy-r74e-search-deck', 'true');
  deck.setAttribute('data-open', 'false');
  deck.setAttribute('data-owner', input.dataset.wilsyR74eSearchOwner || 'crm-search');
  deck.setAttribute('role', 'region');
  deck.setAttribute('aria-live', 'polite');
  deck.setAttribute('aria-label', 'CRM search results');

  anchor.insertAdjacentElement('afterend', deck);

  return deck;
}

/**
 * @function escapeHtml
 * @description Escapes values before rendering live CRM search output.
 * @collaboration R74E DOM safety, CRM result rendering, operator trust.
 */
function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * @function extractRecords
 * @description Extracts record-like objects from flexible CRM API payloads.
 * @collaboration R74E live DB compatibility, CRM route payloads, result normalization.
 */
function extractRecords(payload) {
  const records = [];
  const seen = new Set();
  const stack = [{ value: payload, depth: 0 }];

  while (stack.length > 0) {
    const current = stack.pop();

    if (!current || current.depth > 5 || current.value == null) {
      continue;
    }

    if (Array.isArray(current.value)) {
      current.value.forEach((item) => {
        if (item && typeof item === 'object' && !Array.isArray(item)) {
          const key = JSON.stringify(item).slice(0, 800);

          if (!seen.has(key)) {
            seen.add(key);
            records.push(item);
          }
        }
      });

      continue;
    }

    if (typeof current.value === 'object') {
      Object.values(current.value).forEach((child) => {
        stack.push({ value: child, depth: current.depth + 1 });
      });
    }
  }

  return records;
}

/**
 * @function recordMatchesQuery
 * @description Checks whether a CRM record contains the operator search query.
 * @collaboration R74E client-side filtering, live DB result truth, CRM search outcome.
 */
function recordMatchesQuery(record, query) {
  return JSON.stringify(record || {}).toLowerCase().includes(String(query || '').toLowerCase());
}

/**
 * @function summarizeRecord
 * @description Converts a CRM source record into compact result-card data.
 * @collaboration R74E result card model, CRM evidence surface, operator decisioning.
 */
function summarizeRecord(record, sourceLabel) {
  const title =
    record.name ||
    record.fullName ||
    record.companyName ||
    record.company ||
    record.accountName ||
    record.title ||
    record.subject ||
    record.email ||
    record.id ||
    record._id ||
    'CRM record';

  const subtitle =
    record.stage ||
    record.status ||
    record.type ||
    record.kind ||
    record.channel ||
    record.owner ||
    record.email ||
    sourceLabel;

  const code =
    record.id ||
    record._id ||
    record.leadId ||
    record.accountId ||
    record.dealId ||
    record.hash ||
    record.evidenceId ||
    sourceLabel;

  return {
    title,
    subtitle,
    code,
    sourceLabel,
  };
}

/**
 * @function fetchCrmSource
 * @description Fetches one CRM source lane and filters records by query.
 * @collaboration R74E live DB search, CRM source posture, found/not-found outcome.
 */
async function fetchCrmSource(source, query, tenantId) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 8000);
  const params = new URLSearchParams({
    limit: '24',
    query,
    search: query,
    q: query,
  });

  try {
    const response = await fetch(`${source.endpoint}?${params.toString()}`, {
      credentials: 'include',
      headers: {
        Accept: 'application/json',
        'X-Tenant-Id': tenantId,
      },
      signal: controller.signal,
    });

    window.clearTimeout(timeout);

    if (!response.ok) {
      return {
        source,
        ok: false,
        code: response.status,
        records: [],
      };
    }

    const payload = await response.json().catch(() => null);
    const records = extractRecords(payload)
      .filter((record) => recordMatchesQuery(record, query))
      .slice(0, 6)
      .map((record) => summarizeRecord(record, source.label));

    return {
      source,
      ok: true,
      code: response.status,
      records,
    };
  } catch (error) {
    window.clearTimeout(timeout);

    return {
      source,
      ok: false,
      code: error?.name === 'AbortError' ? 'TIMEOUT' : 'NETWORK',
      records: [],
    };
  }
}

/**
 * @function searchCrmSources
 * @description Searches CRM live and intelligence source lanes.
 * @collaboration R74E source search, live DB outcome, source posture evidence.
 */
async function searchCrmSources(query, tenantId) {
  const sourceResults = await Promise.all(
    CRM_SEARCH_SOURCES.map((source) => fetchCrmSource(source, query, tenantId))
  );

  return {
    sourceResults,
    okSources: sourceResults.filter((sourceResult) => sourceResult.ok),
    failedSources: sourceResults.filter((sourceResult) => !sourceResult.ok),
    records: sourceResults.flatMap((sourceResult) => sourceResult.records),
  };
}

/**
 * @function renderDeck
 * @description Renders searching, found, no-records, and source-blocked outcomes into an inline deck.
 * @collaboration R74E inline results, CRM search outcome, operator UX.
 */
function renderDeck(deck, state) {
  const query = escapeHtml(state.query || '');
  const records = state.records || [];
  const sourceResults = state.sourceResults || [];
  const failedSources = state.failedSources || [];
  const okCount = sourceResults.filter((sourceResult) => sourceResult.ok).length;
  const tone = state.tone || 'loading';

  let status = 'SEARCHING';
  let body = `
    <div class="wilsy-r74e-state" data-tone="loading">
      Searching live CRM database lanes, evidence, accounts, deals and intelligence posture.
    </div>
  `;

  if (tone === 'found') {
    status = `FOUND ${records.length}`;
    body = `
      <div class="wilsy-r74e-grid">
        ${records.map((record) => `
          <article class="wilsy-r74e-card">
            <div class="wilsy-r74e-main">
              <span class="wilsy-r74e-source">${escapeHtml(record.sourceLabel)}</span>
              <strong class="wilsy-r74e-name">${escapeHtml(record.title)}</strong>
              <span class="wilsy-r74e-meta">${escapeHtml(record.subtitle)}</span>
            </div>
            <code class="wilsy-r74e-code">${escapeHtml(record.code)}</code>
          </article>
        `).join('')}
      </div>
    `;
  }

  if (tone === 'empty') {
    status = 'NO RECORDS';
    body = `
      <div class="wilsy-r74e-state" data-tone="empty">
        No live CRM records matched “${query}”. ${okCount} source lane${okCount === 1 ? '' : 's'} checked.
      </div>
    `;
  }

  if (tone === 'error') {
    status = 'SOURCE BLOCKED';
    body = `
      <div class="wilsy-r74e-state" data-tone="error">
        CRM search could not return source records. ${failedSources.length} source lane${failedSources.length === 1 ? '' : 's'} failed or returned protected status.
      </div>
    `;
  }

  const sourceStrip = sourceResults.slice(0, 12).map((sourceResult) => `
    <span class="wilsy-r74e-pill">
      ${escapeHtml(sourceResult.source.label)} · ${escapeHtml(sourceResult.ok ? 'OK' : sourceResult.code)}
    </span>
  `).join('');

  deck.innerHTML = `
    <div class="wilsy-r74e-head">
      <div class="wilsy-r74e-title-row">
        <span class="wilsy-r74e-kicker">WILSY OS · CRM SEARCH</span>
        <span class="wilsy-r74e-query">${query}</span>
        <span class="wilsy-r74e-status" data-tone="${escapeHtml(tone)}">${escapeHtml(status)}</span>
      </div>
      <button class="wilsy-r74e-close" type="button" aria-label="Close CRM search results">×</button>
    </div>
    <div class="wilsy-r74e-body">${body}</div>
    <div class="wilsy-r74e-sources">${sourceStrip}</div>
  `;

  deck.setAttribute('data-open', 'true');

  deck.querySelector('.wilsy-r74e-close')?.addEventListener('click', () => {
    deck.setAttribute('data-open', 'false');
  });
}

/**
 * @function installCrmSearchOutcomeRuntime
 * @description Installs compact inline CRM search result decks on visible CRM Home and Leads search inputs.
 * @collaboration R74E actual search inputs, live DB found/no-records outcomes, WILSY OS operator UX.
 */
export function installCrmSearchOutcomeRuntime({ tenantId = 'MASTER' } = {}) {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return () => {};
  }

  if (typeof window.__wilsyCrmSearchOutcomeRuntimeCleanup === 'function') {
    window.__wilsyCrmSearchOutcomeRuntimeCleanup();
  }

  const doc = document;
  const resolvedTenantId = resolveTenantId(tenantId);
  const listenerRegistry = new Map();

  ensureRuntimeStyle(doc);
  cleanupLegacyPanels(doc);

  /**
   * @function closeAllDecksExcept
   * @description Closes all inline search decks except the active one.
   * @collaboration R74E multi-search cleanup, CRM Home and Leads deck coordination, operator focus.
   */
  function closeAllDecksExcept(activeDeck) {
    doc.querySelectorAll('[data-wilsy-r74e-search-deck="true"]').forEach((deck) => {
      if (deck !== activeDeck) {
        deck.setAttribute('data-open', 'false');
      }
    });
  }

  /**
   * @function bindInput
   * @description Binds Enter/Escape outcome behavior to one visible CRM search input.
   * @collaboration R74E input binding, live DB search trigger, no typing modal behavior.
   */
  function bindInput(input, index) {
    if (listenerRegistry.has(input)) {
      return;
    }

    input.setAttribute('data-wilsy-r74e-runtime-result-input', 'true');
    input.dataset.wilsyR74eSearchOwner = `crm-search-${index}`;

    /**
     * @function closeDeck
     * @description Closes the inline result deck for the active search input.
     * @collaboration R74E Escape behavior, inline deck control, operator command UX.
     */
    function closeDeck() {
      const deck = createDeckForInput(input);
      deck?.setAttribute('data-open', 'false');
    }

    /**
     * @function runSearch
     * @description Runs live CRM source search and renders found, no-records, or source-blocked inline outcome.
     * @collaboration R74E Enter key behavior, live DB query, search result deck.
     */
    async function runSearch() {
      const deck = createDeckForInput(input);
      const query = String(input.value || '').trim();

      if (!deck) {
        return;
      }

      closeAllDecksExcept(deck);

      if (!query) {
        renderDeck(deck, {
          tone: 'empty',
          query: 'EMPTY QUERY',
          records: [],
          sourceResults: [],
          failedSources: [],
        });
        return;
      }

      renderDeck(deck, {
        tone: 'loading',
        query,
        records: [],
        sourceResults: [],
        failedSources: [],
      });

      const outcome = await searchCrmSources(query, resolvedTenantId);

      if (outcome.records.length > 0) {
        renderDeck(deck, {
          tone: 'found',
          query,
          ...outcome,
        });
        return;
      }

      if (outcome.okSources.length === 0 && outcome.failedSources.length > 0) {
        renderDeck(deck, {
          tone: 'error',
          query,
          ...outcome,
        });
        return;
      }

      renderDeck(deck, {
        tone: 'empty',
        query,
        ...outcome,
      });
    }

    /**
     * @function handleKeyDown
     * @description Opens the inline result deck only on Enter and closes it on Escape.
     * @collaboration R74E keyboard search command, no-modal typing, CRM result output.
     */
    function handleKeyDown(event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        runSearch();
      }

      if (event.key === 'Escape') {
        closeDeck();
      }
    }

    input.addEventListener('keydown', handleKeyDown);

    listenerRegistry.set(input, () => {
      input.removeEventListener('keydown', handleKeyDown);
    });
  }

  /**
   * @function bindVisibleInputs
   * @description Binds all currently visible CRM search inputs.
   * @collaboration R74E CRM Home and Leads search binding, route changes, DOM lifecycle.
   */
  function bindVisibleInputs() {
    getSearchInputs(doc).forEach((input, index) => bindInput(input, index));
  }

  const observer = new MutationObserver(bindVisibleInputs);
  observer.observe(doc.body, {
    childList: true,
    subtree: true,
  });

  const interval = window.setInterval(bindVisibleInputs, 600);
  window.setTimeout(bindVisibleInputs, 0);
  bindVisibleInputs();

  /**
   * @function cleanup
   * @description Removes runtime listeners, observers, polling, styles, and inline result decks.
   * @collaboration R74E runtime cleanup, React effect lifecycle, browser hygiene.
   */
  function cleanup() {
    listenerRegistry.forEach((detach) => detach());
    listenerRegistry.clear();
    observer.disconnect();
    window.clearInterval(interval);
    doc.querySelectorAll('[data-wilsy-r74e-search-deck="true"]').forEach((deck) => deck.remove());
    doc.getElementById('wilsy-r74e-crm-search-inline-result-style')?.remove();
  }

  window.__wilsyCrmSearchOutcomeRuntimeCleanup = cleanup;

  return cleanup;
}
