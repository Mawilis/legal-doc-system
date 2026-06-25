/* eslint-disable */

const CRM_SEARCH_SELECTOR = [
  'input[aria-label="Global CRM search"]',
  'input[placeholder="Search pipeline, accounts, evidence"]',
].join(',');

const CRM_SEARCH_SOURCES = Object.freeze([
  { label: 'Live leads', endpoint: '/api/crm/live/leads' },
  { label: 'Live contacts', endpoint: '/api/crm/live/contacts' },
  { label: 'Live accounts', endpoint: '/api/crm/live/accounts' },
  { label: 'Live deals', endpoint: '/api/crm/live/deals' },
  { label: 'Live tasks', endpoint: '/api/crm/live/tasks' },
  { label: 'Live meetings', endpoint: '/api/crm/live/meetings' },
  { label: 'Live evidence', endpoint: '/api/crm/live/evidence' },
  { label: 'Live connectors', endpoint: '/api/crm/live/connectors' },
  { label: 'Intelligence leads', endpoint: '/api/crm/intelligence/leads' },
  { label: 'Intelligence accounts', endpoint: '/api/crm/intelligence/accounts' },
  { label: 'Intelligence deals', endpoint: '/api/crm/intelligence/deals' },
  { label: 'Source posture', endpoint: '/api/crm/live/source-posture' },
]);

/**
 * @function resolveTenantId
 * @description Resolves a stable tenant id for CRM search source requests.
 * @collaboration R74D runtime outcome engine, tenant context, CRM source calls.
 */
function resolveTenantId(tenantId) {
  return String(tenantId || 'MASTER').trim() || 'MASTER';
}

/**
 * @function buildRuntimeStyles
 * @description Builds the fixed-position runtime outcome panel styles.
 * @collaboration R74D visible search outcomes, operator cockpit, WILSY OS UI dominance.
 */
function buildRuntimeStyles() {
  return `
    [data-wilsy-r74d-crm-search-outcome-runtime="true"] {
      position: fixed;
      z-index: 2147483000;
      width: min(960px, calc(100vw - 40px));
      max-height: min(68vh, 620px);
      overflow: hidden;
      border: 1px solid rgba(93, 255, 174, 0.36);
      border-radius: 28px;
      background:
        radial-gradient(circle at 8% 0%, rgba(93, 255, 174, 0.22), transparent 34%),
        linear-gradient(135deg, rgba(5, 18, 13, 0.98), rgba(1, 7, 5, 0.98));
      color: rgba(238, 255, 246, 0.98);
      box-shadow:
        0 0 0 1px rgba(93, 255, 174, 0.16),
        0 32px 90px rgba(0, 0, 0, 0.62),
        0 0 70px rgba(93, 255, 174, 0.24);
      backdrop-filter: blur(22px);
      transform-origin: top center;
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
      transform: translateY(-8px) scale(0.985);
      transition:
        opacity 150ms ease,
        visibility 150ms ease,
        transform 150ms ease;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    [data-wilsy-r74d-crm-search-outcome-runtime="true"][data-wilsy-r74d-open="true"] {
      opacity: 1;
      visibility: visible;
      pointer-events: auto;
      transform: translateY(0) scale(1);
    }

    .wilsy-r74d-search-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      padding: 1.05rem 1.15rem;
      border-bottom: 1px solid rgba(93, 255, 174, 0.18);
      background: rgba(255, 255, 255, 0.035);
    }

    .wilsy-r74d-search-kicker {
      color: rgba(181, 255, 214, 0.72);
      font-size: 0.68rem;
      font-weight: 950;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .wilsy-r74d-search-title {
      margin-top: 0.34rem;
      color: rgba(248, 255, 251, 0.98);
      font-size: clamp(1rem, 1.6vw, 1.45rem);
      font-weight: 950;
      letter-spacing: -0.02em;
    }

    .wilsy-r74d-search-meta {
      margin-top: 0.45rem;
      color: rgba(215, 236, 225, 0.74);
      font-size: 0.74rem;
      font-weight: 760;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .wilsy-r74d-search-close {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 2.4rem;
      height: 2.4rem;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.055);
      color: rgba(255, 255, 255, 0.86);
      cursor: pointer;
      font-size: 1rem;
      font-weight: 900;
    }

    .wilsy-r74d-search-body {
      display: grid;
      gap: 0.72rem;
      max-height: calc(min(68vh, 620px) - 7.2rem);
      overflow: auto;
      padding: 1rem;
    }

    .wilsy-r74d-search-state {
      display: grid;
      gap: 0.4rem;
      padding: 1rem;
      border: 1px solid rgba(93, 255, 174, 0.18);
      border-radius: 20px;
      background: rgba(93, 255, 174, 0.075);
      color: rgba(235, 255, 244, 0.94);
      font-weight: 820;
    }

    .wilsy-r74d-search-state[data-tone="empty"] {
      border-color: rgba(255, 207, 118, 0.34);
      background: rgba(255, 207, 118, 0.09);
      color: rgba(255, 237, 196, 0.96);
    }

    .wilsy-r74d-search-state[data-tone="error"] {
      border-color: rgba(255, 103, 103, 0.38);
      background: rgba(255, 103, 103, 0.09);
      color: rgba(255, 217, 217, 0.96);
    }

    .wilsy-r74d-result-card {
      display: grid;
      gap: 0.35rem;
      padding: 0.9rem 1rem;
      border: 1px solid rgba(93, 255, 174, 0.2);
      border-radius: 18px;
      background:
        linear-gradient(135deg, rgba(93, 255, 174, 0.08), rgba(255, 255, 255, 0.025)),
        rgba(4, 14, 10, 0.78);
    }

    .wilsy-r74d-result-card strong {
      color: rgba(248, 255, 251, 0.98);
      font-size: 0.92rem;
      font-weight: 940;
    }

    .wilsy-r74d-result-card span {
      color: rgba(215, 236, 225, 0.74);
      font-size: 0.74rem;
      font-weight: 760;
      letter-spacing: 0.035em;
      text-transform: uppercase;
    }

    .wilsy-r74d-result-card code {
      width: fit-content;
      max-width: 100%;
      overflow: hidden;
      padding: 0.24rem 0.44rem;
      border: 1px solid rgba(93, 255, 174, 0.18);
      border-radius: 999px;
      background: rgba(1, 8, 5, 0.82);
      color: rgba(202, 255, 224, 0.9);
      font-size: 0.66rem;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .wilsy-r74d-source-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 0.42rem;
      padding: 0 1rem 1rem;
    }

    .wilsy-r74d-source-pill {
      padding: 0.34rem 0.5rem;
      border: 1px solid rgba(255, 255, 255, 0.09);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.045);
      color: rgba(226, 236, 231, 0.7);
      font-size: 0.62rem;
      font-weight: 850;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    @media (max-width: 720px) {
      [data-wilsy-r74d-crm-search-outcome-runtime="true"] {
        width: calc(100vw - 20px);
      }

      .wilsy-r74d-search-head {
        padding: 0.9rem;
      }
    }
  `;
}

/**
 * @function ensureRuntimeStyle
 * @description Installs the runtime outcome panel stylesheet once per document.
 * @collaboration R74D styling, DOM runtime bridge, CRM search outcome surface.
 */
function ensureRuntimeStyle(doc) {
  const styleId = 'wilsy-r74d-crm-search-outcome-style';
  const existing = doc.getElementById(styleId);

  if (existing) {
    return existing;
  }

  const style = doc.createElement('style');
  style.id = styleId;
  style.textContent = buildRuntimeStyles();
  doc.head.appendChild(style);

  return style;
}

/**
 * @function selectVisibleSearchInput
 * @description Selects the actual visible top CRM search input from the rendered DOM.
 * @collaboration R74D DOM ownership proof, Chrome runtime evidence, CRM top search.
 */
function selectVisibleSearchInput(doc) {
  const candidates = [...doc.querySelectorAll(CRM_SEARCH_SELECTOR)];

  return candidates.find((input) => {
    const rect = input.getBoundingClientRect();

    return rect.width > 240 && rect.height > 30 && input.offsetParent !== null;
  }) || candidates[0] || null;
}

/**
 * @function createOutcomePanel
 * @description Creates the fixed runtime search outcome panel.
 * @collaboration R74D operator-visible results, found/not-found state, CRM cockpit UX.
 */
function createOutcomePanel(doc) {
  const existing = doc.querySelector('[data-wilsy-r74d-crm-search-outcome-runtime="true"]');

  if (existing) {
    return existing;
  }

  const panel = doc.createElement('aside');
  panel.setAttribute('data-wilsy-r74d-crm-search-outcome-runtime', 'true');
  panel.setAttribute('data-wilsy-r74d-open', 'false');
  panel.setAttribute('role', 'region');
  panel.setAttribute('aria-live', 'polite');
  panel.setAttribute('aria-label', 'CRM search outcome results');
  doc.body.appendChild(panel);

  return panel;
}

/**
 * @function positionOutcomePanel
 * @description Positions the outcome panel directly below the live search input.
 * @collaboration R74D actual DOM anchoring, visible CRM search bar, operator acceptance.
 */
function positionOutcomePanel(panel, input) {
  if (!panel || !input) {
    return;
  }

  const rect = input.getBoundingClientRect();
  const width = Math.min(Math.max(rect.width, 620), window.innerWidth - 40);
  const left = Math.min(Math.max(rect.left, 20), window.innerWidth - width - 20);
  const top = Math.min(rect.bottom + 12, window.innerHeight - 120);

  panel.style.left = `${left}px`;
  panel.style.top = `${top}px`;
  panel.style.width = `${width}px`;
}

/**
 * @function escapeHtml
 * @description Escapes runtime CRM search values before writing outcome HTML.
 * @collaboration R74D source safety, DOM rendering, operator search result display.
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
 * @description Extracts object records from flexible CRM API payload shapes.
 * @collaboration R74D source-honest search, CRM live routes, CRM intelligence routes.
 */
function extractRecords(payload) {
  const records = [];
  const seen = new Set();

  /**
   * @function visit
   * @description Recursively visits payload branches and collects record-like objects.
   * @collaboration R74D payload normalization, CRM source compatibility, resilient search.
   */
  function visit(value, depth = 0) {
    if (!value || depth > 5) {
      return;
    }

    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item && typeof item === 'object' && !Array.isArray(item)) {
          const key = JSON.stringify(item).slice(0, 800);

          if (!seen.has(key)) {
            seen.add(key);
            records.push(item);
          }
        }
      });

      return;
    }

    if (typeof value === 'object') {
      Object.values(value).forEach((child) => visit(child, depth + 1));
    }
  }

  visit(payload);

  return records;
}

/**
 * @function recordMatchesQuery
 * @description Tests whether a CRM record contains the operator search query.
 * @collaboration R74D client-side fallback filtering, found/not-found truthfulness, CRM search.
 */
function recordMatchesQuery(record, query) {
  return JSON.stringify(record || {}).toLowerCase().includes(String(query || '').toLowerCase());
}

/**
 * @function summarizeRecord
 * @description Builds a compact operator-facing CRM search result summary.
 * @collaboration R74D result cards, CRM evidence surface, operator decisioning.
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
 * @description Fetches and filters one CRM live/intelligence source for the query.
 * @collaboration R74D source calls, found/not-found result engine, CRM route posture.
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
      .slice(0, 5)
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
 * @description Searches all configured CRM runtime sources and returns an outcome summary.
 * @collaboration R74D multi-source search, CRM results found/not-found, source posture.
 */
async function searchCrmSources(query, tenantId) {
  const sourceResults = await Promise.all(
    CRM_SEARCH_SOURCES.map((source) => fetchCrmSource(source, query, tenantId))
  );

  const records = sourceResults.flatMap((sourceResult) => sourceResult.records);
  const okSources = sourceResults.filter((sourceResult) => sourceResult.ok);
  const failedSources = sourceResults.filter((sourceResult) => !sourceResult.ok);

  return {
    records,
    sourceResults,
    okSources,
    failedSources,
  };
}

/**
 * @function renderOutcome
 * @description Renders loading, found, not-found, and source-blocked states into the runtime panel.
 * @collaboration R74D operator outcome visibility, CRM search results, evidence surface.
 */
function renderOutcome(panel, state) {
  const query = escapeHtml(state.query || '');
  const records = state.records || [];
  const failedSources = state.failedSources || [];
  const sourceResults = state.sourceResults || [];
  const tone = state.tone || 'ready';

  let title = 'READY — PRESS ENTER';
  let meta = 'Search CRM live and intelligence sources.';
  let body = `
    <div class="wilsy-r74d-search-state" data-tone="ready">
      Type a query and press Enter to search CRM records, evidence and source posture.
    </div>
  `;

  if (tone === 'loading') {
    title = `SEARCHING CRM SOURCES — ${query}`;
    meta = 'Live source query in progress.';
    body = `
      <div class="wilsy-r74d-search-state" data-tone="loading">
        Searching leads, accounts, deals, evidence, connectors and intelligence sources for “${query}”.
      </div>
    `;
  }

  if (tone === 'found') {
    title = `FOUND ${records.length} RESULT${records.length === 1 ? '' : 'S'} — ${query}`;
    meta = `${sourceResults.filter((item) => item.ok).length} source lanes responded.`;

    body = records.map((record) => `
      <article class="wilsy-r74d-result-card">
        <span>${escapeHtml(record.sourceLabel)}</span>
        <strong>${escapeHtml(record.title)}</strong>
        <span>${escapeHtml(record.subtitle)}</span>
        <code>${escapeHtml(record.code)}</code>
      </article>
    `).join('');
  }

  if (tone === 'empty') {
    title = `NO CRM RECORDS FOUND — ${query}`;
    meta = `${sourceResults.filter((item) => item.ok).length} source lanes checked.`;
    body = `
      <div class="wilsy-r74d-search-state" data-tone="empty">
        No live CRM records matched “${query}”. This is a real not-found outcome, not a silent search.
      </div>
    `;
  }

  if (tone === 'error') {
    title = `CRM SEARCH SOURCE BLOCKED — ${query}`;
    meta = `${failedSources.length} source lane${failedSources.length === 1 ? '' : 's'} failed or returned protected status.`;
    body = `
      <div class="wilsy-r74d-search-state" data-tone="error">
        Search could not return source records. Check auth/session, tenant context, and backend CRM route posture.
      </div>
    `;
  }

  const sourceStrip = sourceResults.slice(0, 12).map((sourceResult) => `
    <span class="wilsy-r74d-source-pill">
      ${escapeHtml(sourceResult.source.label)} · ${escapeHtml(sourceResult.ok ? 'OK' : sourceResult.code)}
    </span>
  `).join('');

  panel.innerHTML = `
    <div class="wilsy-r74d-search-head">
      <div>
        <div class="wilsy-r74d-search-kicker">WILSY OS · CRM SEARCH OUTCOME</div>
        <div class="wilsy-r74d-search-title">${title}</div>
        <div class="wilsy-r74d-search-meta">${meta}</div>
      </div>
      <button class="wilsy-r74d-search-close" type="button" aria-label="Close CRM search results">×</button>
    </div>
    <div class="wilsy-r74d-search-body">${body}</div>
    <div class="wilsy-r74d-source-strip">${sourceStrip}</div>
  `;

  panel.setAttribute('data-wilsy-r74d-open', 'true');

  const closeButton = panel.querySelector('.wilsy-r74d-search-close');
  closeButton?.addEventListener('click', () => {
    panel.setAttribute('data-wilsy-r74d-open', 'false');
  });
}

/**
 * @function installCrmSearchOutcomeRuntime
 * @description Installs a runtime bridge on the actual visible CRM top search input and shows found/not-found/error results.
 * @collaboration R74D runtime DOM owner, CRM search outcome engine, WILSY OS competitive search UX.
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
  let disposed = false;
  let attachedInput = null;
/**
   * @function detachInput
   * @description Stores the active CRM search input event-detach callback for safe runtime rebinding and teardown.
   * @collaboration R74D runtime outcome engine, DOM listener lifecycle, WILSY OS CRM search stability.
   */
  let detachInput = () => {};

  ensureRuntimeStyle(doc);

  const panel = createOutcomePanel(doc);

  /**
   * @function attachToInput
   * @description Attaches runtime search handlers to the actual visible CRM search input.
   * @collaboration R74D live DOM handler, operator search entry, CRM outcome panel.
   */
  function attachToInput() {
    if (disposed) {
      return;
    }

    const input = selectVisibleSearchInput(doc);

    if (!input || input === attachedInput) {
      return;
    }

    detachInput();
    attachedInput = input;
    input.setAttribute('data-wilsy-r74d-runtime-outcome-input', 'true');

    /**
     * @function openReadyState
     * @description Shows ready-state feedback for the current CRM search query.
     * @collaboration R74D ready feedback, visible input anchoring, CRM search outcome.
     */
    function openReadyState() {
      positionOutcomePanel(panel, input);

      const query = String(input.value || '').trim();

      if (query) {
        renderOutcome(panel, {
          tone: 'ready',
          query,
          records: [],
          sourceResults: [],
          failedSources: [],
        });
      }
    }

    /**
     * @function runSearch
     * @description Executes the source-honest CRM search and renders found/not-found/error outcomes.
     * @collaboration R74D Enter key search, CRM route calls, found-not-found UX.
     */
    async function runSearch() {
      const query = String(input.value || '').trim();
      positionOutcomePanel(panel, input);

      if (!query) {
        renderOutcome(panel, {
          tone: 'empty',
          query: 'EMPTY QUERY',
          records: [],
          sourceResults: [],
          failedSources: [],
        });
        return;
      }

      renderOutcome(panel, {
        tone: 'loading',
        query,
        records: [],
        sourceResults: [],
        failedSources: [],
      });

      const outcome = await searchCrmSources(query, resolvedTenantId);

      if (outcome.records.length > 0) {
        renderOutcome(panel, {
          tone: 'found',
          query,
          ...outcome,
        });
        return;
      }

      if (outcome.okSources.length === 0 && outcome.failedSources.length > 0) {
        renderOutcome(panel, {
          tone: 'error',
          query,
          ...outcome,
        });
        return;
      }

      renderOutcome(panel, {
        tone: 'empty',
        query,
        ...outcome,
      });
    }

    /**
     * @function handleKeyDown
     * @description Handles Enter and Escape for the runtime CRM search outcome panel.
     * @collaboration R74D keyboard UX, Enter search, Escape close.
     */
    function handleKeyDown(event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        runSearch();
      }

      if (event.key === 'Escape') {
        panel.setAttribute('data-wilsy-r74d-open', 'false');
      }
    }

    input.addEventListener('focus', openReadyState);
    input.addEventListener('input', openReadyState);
    input.addEventListener('keydown', handleKeyDown);
    window.addEventListener('resize', openReadyState);
    window.addEventListener('scroll', openReadyState, true);

    detachInput = () => {
      input.removeEventListener('focus', openReadyState);
      input.removeEventListener('input', openReadyState);
      input.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('resize', openReadyState);
      window.removeEventListener('scroll', openReadyState, true);
    };

    if (String(input.value || '').trim()) {
      openReadyState();
    }
  }

  const observer = new MutationObserver(attachToInput);
  observer.observe(doc.body, {
    childList: true,
    subtree: true,
  });

  const interval = window.setInterval(attachToInput, 500);
  window.setTimeout(attachToInput, 0);
  attachToInput();

/**
   * @function cleanup
   * @description Tears down the CRM runtime search outcome panel, listeners, observer, and polling interval.
   * @collaboration R74D runtime outcome engine, React effect cleanup, WILSY OS production browser hygiene.
   */
  const cleanup = () => {
    disposed = true;
    detachInput();
    observer.disconnect();
    window.clearInterval(interval);
    panel.remove();
  };

  window.__wilsyCrmSearchOutcomeRuntimeCleanup = cleanup;

  return cleanup;
}
