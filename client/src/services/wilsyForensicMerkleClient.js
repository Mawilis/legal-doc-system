/* eslint-disable */
/*
 * WILSY OS - FORENSIC MERKLE CLIENT BRIDGE
 * @file client/src/services/wilsyForensicMerkleClient.js
 * @version R18AD1-ACCOUNT-FORENSIC-BRIDGE-WIRING
 * @description Frontend service bridge for consuming backend ForensicMerkleAuditor receipt, overlay, anchor and verification routes without duplicating Merkle/hash-chain logic in React.
 * @collaboration Connects Wilsy OS chrome, sovereign cockpit, revenue ledger, compliance HUD, forensic HUD, showroom and future executive dashboards to server-side Merkle verification authority.
 * @fileNotes
 * - This file is a client bridge only. It must never implement private-key signing or browser-owned Merkle authority.
 * - Backend services remain the source of forensic truth: server/services/ForensicMerkleAuditor.js and server/routes/forensicRoutes.js.
 * - Browser code may display auditor status, anchor history, verification posture, receipts, compliance bindings and cockpit snapshots.
 * - Browser code may trigger permitted audit-cycle requests through authenticated tenant-bound API calls.
 * - Browser code must not store secrets, hardcode privileged tokens, or fabricate cryptographic receipts.
 * @guardrails
 * - Keep first line as eslint-disable for Wilsy documentation guard compatibility.
 * - Preserve function-level JSDoc with @function, @description, and @collaboration.
 * - Run wilsy-secret-guard, wilsy-documentation-guard, bridge smoke bundle, and client build after edits.
 */

export const WILSY_FORENSIC_MERKLE_CLIENT_VERSION = 'R18AD1-ACCOUNT-FORENSIC-BRIDGE-WIRING';

const DEFAULT_API_BASE = import.meta.env.VITE_API_URL || '';
const WILSY_FORENSIC_IN_FLIGHT_REQUESTS = new Map();
const WILSY_FORENSIC_REQUEST_TIMEOUT_MS = 5000;
const WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT = 12;
const WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT = 250;
const WILSY_FORENSIC_SNAPSHOT_CACHE_TTL_MS = 30000;
const WILSY_FORENSIC_SNAPSHOT_CACHE = new Map();

const WILSY_FORENSIC_TOKEN_KEYS = [
  'wilsy_token',
  'wilsyAccessToken',
  'wilsyAuthToken',
  'wilsySovereignToken',
  'accessToken',
  'authToken',
  'access_token',
  'token',
  'jwt',
  'sovereignToken'
];

/**
 * @function parseWilsyStoredTokenValue
 * @description Extracts an access token from plain strings or JSON auth payloads stored by Wilsy runtime clients.
 * @collaboration Prevents undefined Authorization headers while keeping browser secrets out of source code.
 */
export function parseWilsyStoredTokenValue(value) {
  if (!value || value === 'null' || value === 'undefined') {
    return '';
  }

  const raw = String(value).trim();

  if (!raw) {
    return '';
  }

  if (raw.startsWith('Bearer ')) {
    return raw.replace(/^Bearer\s+/i, '').trim();
  }

  try {
    const parsed = JSON.parse(raw);
    const nested = parsed?.accessToken
      || parsed?.token
      || parsed?.jwt
      || parsed?.data?.accessToken
      || parsed?.data?.token
      || parsed?.auth?.accessToken
      || parsed?.auth?.token
      || '';

    return nested ? String(nested).replace(/^Bearer\s+/i, '').trim() : '';
  } catch {
    return raw;
  }
}

/**
 * @function getWilsyStoredAuthToken
 * @description Reads the active Wilsy auth token from localStorage or sessionStorage using known runtime keys.
 * @collaboration Keeps forensic bridge requests aligned with the wider SOVEREIGN auth runtime without hardcoding secrets.
 */
export function getWilsyStoredAuthToken() {
  if (typeof window === 'undefined') {
    return '';
  }

  for (const storage of [window.localStorage, window.sessionStorage]) {
    if (!storage) {
      continue;
    }

    for (const key of WILSY_FORENSIC_TOKEN_KEYS) {
      const token = parseWilsyStoredTokenValue(storage.getItem(key));

      if (token) {
        return token;
      }
    }
  }

  return '';
}

/**
 * @function normalizeWilsyTenantId
 * @description Normalizes tenant IDs for forensic Merkle auditor requests.
 * @collaboration Keeps the frontend bridge tenant-safe while delegating Merkle authority to backend services.
 */
export function normalizeWilsyTenantId(tenantId) {
  return String(tenantId || 'wilsy-sovereign-root').trim() || 'wilsy-sovereign-root';
}

/**
 * @function normalizeWilsyPositiveInteger
 * @description Normalizes positive integer request parameters for receipt display and replay limits.
 * @collaboration Keeps showroom pagination separate from backend forensic replay depth without leaking unsafe query values.
 */
export function normalizeWilsyPositiveInteger(value, fallback) {
  const parsed = Number(value);

  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }

  return Math.floor(parsed);
}

/**
 * @function buildWilsySnapshotCacheKey
 * @description Builds a stable cache key for lightweight forensic showroom snapshots.
 * @collaboration Prevents React StrictMode, polling and manual console tests from repeatedly forcing expensive backend forensic replays.
 */
export function buildWilsySnapshotCacheKey({
  tenantId,
  limit,
  replayLimit,
  framework,
  receiptStatus
} = {}) {
  return [
    normalizeWilsyTenantId(tenantId),
    normalizeWilsyPositiveInteger(limit, WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT),
    normalizeWilsyPositiveInteger(replayLimit, WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT),
    framework || '',
    receiptStatus || ''
  ].join('::');
}

/**
 * @function readWilsySnapshotCache
 * @description Reads a still-valid cached forensic snapshot.
 * @collaboration Lets the proof showroom stay responsive while preserving backend authority for receipt data.
 */
export function readWilsySnapshotCache(cacheKey) {
  const cached = WILSY_FORENSIC_SNAPSHOT_CACHE.get(cacheKey);

  if (!cached) {
    return null;
  }

  if (Date.now() - cached.createdAt > WILSY_FORENSIC_SNAPSHOT_CACHE_TTL_MS) {
    WILSY_FORENSIC_SNAPSHOT_CACHE.delete(cacheKey);
    return null;
  }

  return cached.snapshot;
}

/**
 * @function writeWilsySnapshotCache
 * @description Stores a lightweight forensic snapshot for short-lived showroom reuse.
 * @collaboration Shields the backend from repeated full replay pressure during development and live cockpit polling.
 */
export function writeWilsySnapshotCache(cacheKey, snapshot) {
  WILSY_FORENSIC_SNAPSHOT_CACHE.set(cacheKey, {
    createdAt: Date.now(),
    snapshot
  });

  return snapshot;
}

/**
 * @function buildWilsyReceiptQueryParams
 * @description Builds query parameters for receipt-contract endpoints.
 * @collaboration Allows the showroom to request paginated receipt rows while keeping backend replay depth authoritative.
 */
export function buildWilsyReceiptQueryParams({
  tenantId,
  limit = WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT,
  replayLimit = WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT,
  receiptId,
  receiptStatus,
  status,
  framework
} = {}) {
  const params = new URLSearchParams({
    tenantId: normalizeWilsyTenantId(tenantId),
    limit: String(normalizeWilsyPositiveInteger(limit, WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT)),
    replayLimit: String(normalizeWilsyPositiveInteger(replayLimit, WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT))
  });

  if (receiptId) {
    params.set('receiptId', String(receiptId));
  }

  if (receiptStatus || status) {
    params.set('receiptStatus', String(receiptStatus || status));
  }

  if (framework) {
    params.set('framework', String(framework));
  }

  return params;
}

/**
 * @function buildWilsyForensicHeaders
 * @description Builds request headers for Wilsy forensic API calls without exposing secrets in browser code.
 * @collaboration Allows tenant-bound requests to reuse local runtime auth while respecting the Wilsy secret guard.
 */
export function buildWilsyForensicHeaders({ tenantId, token } = {}) {
  const resolvedToken = token || getWilsyStoredAuthToken();

  return {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Tenant-Id': normalizeWilsyTenantId(tenantId),
    ...(resolvedToken ? { Authorization: `Bearer ${resolvedToken}` } : {})
  };
}

/**
 * @function parseWilsyForensicResponse
 * @description Parses a forensic API response and raises a usable error when the backend rejects the request.
 * @collaboration Keeps cockpit UI failures readable while preserving backend authority as the source of truth.
 */
export async function parseWilsyForensicResponse(response) {
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = payload?.message || payload?.error || `Wilsy forensic request failed with ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

/**
 * @function appendWilsyForensicNoCacheParam
 * @description Adds a timestamp cache-buster to GET forensic requests so browser 304 responses do not hide backend posture changes.
 * @collaboration Keeps the proof showroom synchronized with live ForensicMerkleAuditor contracts while preserving Vite/browser cache safety.
 */
export function appendWilsyForensicNoCacheParam(path) {
  const separator = String(path).includes('?') ? '&' : '?';

  return `${path}${separator}_wilsyForensicTs=${Date.now()}`;
}

/**
 * @function getWilsyForensicApiBaseCandidates
 * @description Returns ordered API base candidates for forensic browser transport.
 * @collaboration Lets the proof showroom try configured API base, local backend dev origins and Vite proxy without hardcoding secrets.
 */
export function getWilsyForensicApiBaseCandidates(configuredBase = DEFAULT_API_BASE) {
  const rawCandidates = [
    configuredBase,
    import.meta.env.DEV ? 'http://localhost:5050' : null,
    import.meta.env.DEV ? 'http://127.0.0.1:5050' : null,
    ''
  ];

  return rawCandidates.reduce((unique, candidate) => {
    const normalized = String(candidate ?? '').trim().replace(/\/$/, '');

    if (!unique.includes(normalized)) {
      unique.push(normalized);
    }

    return unique;
  }, []);
}

/**
 * @function isWilsyJsonResponse
 * @description Detects whether a forensic transport response is JSON before parsing.
 * @collaboration Prevents Vite HTML fallbacks or proxy misses from masquerading as valid forensic proof payloads.
 */
export function isWilsyJsonResponse(response) {
  const contentType = response?.headers?.get?.('content-type') || '';

  return contentType.toLowerCase().includes('application/json');
}

/**
 * @function isWilsyForensicAbortError
 * @description Detects request cancellation from AbortController, browser reloads, Vite hot refresh, and React cleanup.
 * @collaboration Prevents normal lifecycle cancellation from being reported as a forensic transport outage.
 */
export function isWilsyForensicAbortError(error) {
  const name = String(error?.name || '');
  const message = String(error?.message || '').toLowerCase();

  return name === 'AbortError'
    || message.includes('aborted')
    || message.includes('signal is aborted')
    || message.includes('the user aborted a request');
}

/**
 * @function buildWilsyForensicAbortError
 * @description Builds a classified forensic cancellation error for callers that need to ignore normal lifecycle aborts.
 * @collaboration Keeps real transport failures visible while hiding harmless React/Vite abort noise.
 */
export function buildWilsyForensicAbortError(path) {
  const error = new Error(`Forensic request cancelled for ${path}`);
  error.name = 'AbortError';
  error.wilsyCancelled = true;
  return error;
}

/**
 * @function buildWilsyForensicTimeoutError
 * @description Builds a classified timeout error when a forensic transport candidate exceeds the bridge budget.
 * @collaboration Prevents the proof showroom console and cockpit snapshot from hanging forever on stalled browser fetches.
 */
export function buildWilsyForensicTimeoutError(path, timeoutMs = WILSY_FORENSIC_REQUEST_TIMEOUT_MS) {
  const error = new Error(`Forensic request timed out for ${path} after ${timeoutMs}ms`);
  error.name = 'WilsyForensicTimeoutError';
  error.wilsyTimeout = true;
  return error;
}

/**
 * @function createWilsyForensicTimeoutSignal
 * @description Creates a timeout-aware AbortController that also respects the caller supplied signal.
 * @collaboration Gives every forensic transport candidate a deterministic exit path while preserving React cleanup cancellation.
 */
export function createWilsyForensicTimeoutSignal(path, outerSignal, timeoutMs = WILSY_FORENSIC_REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(() => {
    const timeoutError = buildWilsyForensicTimeoutError(path, timeoutMs);

    try {
      controller.abort(timeoutError);
    } catch {
      controller.abort();
    }
  }, timeoutMs);

  if (outerSignal?.aborted) {
    try {
      controller.abort(buildWilsyForensicAbortError(path));
    } catch {
      controller.abort();
    }
  } else if (outerSignal?.addEventListener) {
    outerSignal.addEventListener('abort', () => {
      try {
        controller.abort(buildWilsyForensicAbortError(path));
      } catch {
        controller.abort();
      }
    }, { once: true });
  }

  return {
    signal: controller.signal,
    timeoutId
  };
}

/**
 * @function classifyWilsyForensicFetchError
 * @description Converts fetch aborts into either lifecycle cancellation or timeout errors.
 * @collaboration Keeps real backend stalls visible while ignoring harmless React/Vite cancellation.
 */
export function classifyWilsyForensicFetchError(error, path, candidateSignal) {
  if (error?.wilsyTimeout || candidateSignal?.reason?.wilsyTimeout) {
    return buildWilsyForensicTimeoutError(path);
  }

  if (error?.wilsyCancelled || candidateSignal?.reason?.wilsyCancelled || isWilsyForensicAbortError(error)) {
    return buildWilsyForensicAbortError(path);
  }

  return error;
}

/**
 * @function buildWilsyForensicTransportError
 * @description Builds a product-safe forensic transport error after all browser API base candidates fail.
 * @collaboration Replaces raw Failed to fetch messages with operator-readable backend handshake posture.
 */
export function buildWilsyForensicTransportError(path, candidates, lastError) {
  if (isWilsyForensicAbortError(lastError)) {
    return buildWilsyForensicAbortError(path);
  }

  const candidateSummary = candidates.map(candidate => candidate || 'vite-proxy').join(' → ');
  const detail = lastError?.message || 'No response body returned';

  return new Error(`Forensic transport unavailable for ${path}. Tried ${candidateSummary}. Last failure: ${detail}`);
}

/**
 * @function buildWilsyForensicRequestKey
 * @description Builds a stable in-flight request key before cache-busting query parameters are applied.
 * @collaboration Collapses React StrictMode and duplicate cockpit reads without hiding backend posture changes.
 */
export function buildWilsyForensicRequestKey(path, options = {}) {
  return [
    String(options.method || 'GET').toUpperCase(),
    normalizeWilsyTenantId(options.tenantId),
    String(path || ''),
    JSON.stringify(options.body || {})
  ].join('::');
}

/**
 * @function requestWilsyForensicJson
 * @description Executes a JSON request against existing Wilsy forensic backend endpoints with backend-origin and Vite/proxy fallback.
 * @collaboration Prevents frontend Merkle duplication by consuming server-side auditor routes while avoiding raw browser transport hangs.
 */
export async function requestWilsyForensicJson(path, options = {}) {
  const {
    method = 'GET',
    tenantId,
    token,
    body,
    signal
  } = options;

  const safeMethod = String(method || 'GET').toUpperCase();
  const requestKey = buildWilsyForensicRequestKey(path, { method: safeMethod, tenantId, body });
  const shouldDedupe = safeMethod === 'GET' && !signal;

  if (signal?.aborted) {
    throw buildWilsyForensicAbortError(path);
  }

  if (shouldDedupe && WILSY_FORENSIC_IN_FLIGHT_REQUESTS.has(requestKey)) {
    return WILSY_FORENSIC_IN_FLIGHT_REQUESTS.get(requestKey);
  }

  /**
   * @function transportPromise
   * @description Executes the forensic transport candidate loop for one request and classifies lifecycle aborts or timeouts before they become false outages.
   * @collaboration Keeps retry, fallback and timeout-safe behavior contained while the outer request layer handles deduplication and cleanup.
   */
  const transportPromise = (async () => {
    const resolvedPath = safeMethod === 'GET' ? appendWilsyForensicNoCacheParam(path) : path;
    const candidates = getWilsyForensicApiBaseCandidates(DEFAULT_API_BASE);
    let lastError = null;

    for (const apiBase of candidates) {
      const url = `${apiBase}${resolvedPath}`;
      const timeoutSignal = createWilsyForensicTimeoutSignal(path, signal);

      try {
        const response = await fetch(url, {
          method: safeMethod,
          headers: buildWilsyForensicHeaders({ tenantId, token }),
          ...(body ? { body: JSON.stringify(body) } : {}),
          cache: 'no-store',
          signal: timeoutSignal.signal
        });

        globalThis.clearTimeout(timeoutSignal.timeoutId);

        if (!isWilsyJsonResponse(response)) {
          lastError = new Error(`Non-JSON forensic response from ${apiBase || 'vite-proxy'}`);
          continue;
        }

        return parseWilsyForensicResponse(response);
      } catch (error) {
        globalThis.clearTimeout(timeoutSignal.timeoutId);

        const classifiedError = classifyWilsyForensicFetchError(error, path, timeoutSignal.signal);

        if (signal?.aborted || classifiedError?.wilsyCancelled) {
          throw buildWilsyForensicAbortError(path);
        }

        lastError = classifiedError;
      }
    }

    throw buildWilsyForensicTransportError(path, candidates, lastError);
  })();

  if (shouldDedupe) {
    WILSY_FORENSIC_IN_FLIGHT_REQUESTS.set(requestKey, transportPromise);
    transportPromise
      .finally(() => {
        globalThis.setTimeout(() => WILSY_FORENSIC_IN_FLIGHT_REQUESTS.delete(requestKey), 250);
      })
      .catch(() => {});
  }

  return transportPromise;
}

/**
 * @function getWilsyMerkleAuditorStatus
 * @description Reads the backend ForensicMerkleAuditor worker and anchor configuration status.
 * @collaboration Powers the cockpit status tile from the existing /api/forensics/merkle-auditor/status endpoint.
 */
export function getWilsyMerkleAuditorStatus(options = {}) {
  return requestWilsyForensicJson('/api/forensics/merkle-auditor/status', options);
}

/**
 * @function runWilsyMerkleAuditCycle
 * @description Executes a backend Merkle audit cycle for the selected tenant with receipt display pagination separated from replay depth.
 * @collaboration Allows command surfaces to trigger verification without implementing Merkle logic in React.
 */
export function runWilsyMerkleAuditCycle({
  tenantId,
  anchor = true,
  limit = WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT,
  receiptLimit = limit,
  replayLimit = WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT
} = {}) {
  return requestWilsyForensicJson('/api/forensics/merkle-auditor/run', {
    method: 'POST',
    tenantId,
    body: {
      tenantId: normalizeWilsyTenantId(tenantId),
      anchor,
      limit: normalizeWilsyPositiveInteger(replayLimit, WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT),
      receiptLimit: normalizeWilsyPositiveInteger(receiptLimit, WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT)
    }
  });
}


/**
 * @function sealWilsyMerkleSafeWindow
 * @description Requests a backend-owned production seal decision for the current safe receipt window.
 * @collaboration Connects the showroom seal command to /api/forensics/merkle-auditor/seal-safe-window without allowing browser-side immutable seal claims.
 */
export function sealWilsyMerkleSafeWindow({
  tenantId,
  limit = 250,
  receiptLimit = 3,
  actor = 'wilsy-founder-console',
  reason = 'SAFE_WINDOW_SEAL_REQUEST',
  signal
} = {}) {
  const safeTenantId = normalizeWilsyTenantId(tenantId);

  return requestWilsyForensicJson('/api/forensics/merkle-auditor/seal-safe-window', {
    method: 'POST',
    tenantId: safeTenantId,
    signal,
    body: {
      tenantId: safeTenantId,
      limit,
      receiptLimit,
      actor,
      reason
    }
  });
}

/**
 * @function listWilsyMerkleAnchors
 * @description Lists recent local Merkle anchors from the backend append-only anchor queue.
 * @collaboration Supplies the cockpit proof stream from the existing backend anchor history.
 */
export function listWilsyMerkleAnchors({ tenantId, limit = 12, signal } = {}) {
  const params = new URLSearchParams({
    limit: String(normalizeWilsyPositiveInteger(limit, WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT))
  });

  return requestWilsyForensicJson(`/api/forensics/merkle-auditor/anchors?${params.toString()}`, {
    tenantId,
    signal
  });
}

/**
 * @function listWilsyMerkleReceipts
 * @description Lists route-safe forensic receipts with receiptContract and receiptOverlay metadata from the backend.
 * @collaboration Feeds the showroom with real receipt hashes, compliance bindings, receipt Merkle roots and review overlays.
 */
export function listWilsyMerkleReceipts({
  tenantId,
  limit = WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT,
  replayLimit = WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT,
  receiptId,
  receiptStatus,
  status,
  framework,
  signal
} = {}) {
  const params = buildWilsyReceiptQueryParams({
    tenantId,
    limit,
    replayLimit,
    receiptId,
    receiptStatus,
    status,
    framework
  });

  return requestWilsyForensicJson(`/api/forensics/merkle-auditor/receipts?${params.toString()}`, {
    tenantId,
    signal
  });
}

/**
 * @function getWilsyMerkleReceipt
 * @description Reads one route-safe forensic receipt with bound POPIA, GDPR, SOC2 and WORM clauses.
 * @collaboration Powers regulator-grade receipt drill-down without fabricating receipt evidence in the browser.
 */
export function getWilsyMerkleReceipt({
  tenantId,
  receiptId,
  replayLimit = WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT,
  framework,
  signal
} = {}) {
  if (!receiptId) {
    throw new Error('Receipt id is required');
  }

  const params = new URLSearchParams({
    tenantId: normalizeWilsyTenantId(tenantId),
    replayLimit: String(normalizeWilsyPositiveInteger(replayLimit, WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT))
  });

  if (framework) {
    params.set('framework', String(framework));
  }

  return requestWilsyForensicJson(`/api/forensics/merkle-auditor/receipts/${encodeURIComponent(receiptId)}?${params.toString()}`, {
    tenantId,
    signal
  });
}

/**
 * @function verifyWilsyForensicChain
 * @description Replays the tenant forensic hash chain and returns backend Merkle verification posture.
 * @collaboration Binds the cockpit proof view to the existing /api/forensics/verify-chain contract while allowing full replay depth.
 */
export function verifyWilsyForensicChain({
  tenantId,
  anchor = false,
  limit,
  replayLimit,
  signal
} = {}) {
  const effectiveLimit = normalizeWilsyPositiveInteger(
    replayLimit || limit,
    WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT
  );
  const params = new URLSearchParams({
    tenantId: normalizeWilsyTenantId(tenantId),
    anchor: String(Boolean(anchor)),
    limit: String(effectiveLimit)
  });

  return requestWilsyForensicJson(`/api/forensics/verify-chain?${params.toString()}`, {
    tenantId,
    signal
  });
}

/**
 * @function buildWilsyMerkleCockpitSnapshot
 * @description Aggregates lightweight anchors and receipt-contract overlays into one cockpit-ready proof snapshot without triggering duplicate full-chain replays.
 * @collaboration Gives Wilsy dashboards one safe frontend contract while backend services remain the forensic authority.
 */
export async function buildWilsyMerkleCockpitSnapshot({
  tenantId,
  limit = WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT,
  replayLimit = WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT,
  framework,
  receiptStatus,
  signal
} = {}) {
  const safeTenantId = normalizeWilsyTenantId(tenantId);
  const displayLimit = normalizeWilsyPositiveInteger(limit, WILSY_FORENSIC_RECEIPT_DISPLAY_DEFAULT_LIMIT);
  const proofReplayLimit = normalizeWilsyPositiveInteger(replayLimit, WILSY_FORENSIC_RECEIPT_REPLAY_DEFAULT_LIMIT);
  const cacheKey = buildWilsySnapshotCacheKey({
    tenantId: safeTenantId,
    limit: displayLimit,
    replayLimit: proofReplayLimit,
    framework,
    receiptStatus
  });
  const cachedSnapshot = readWilsySnapshotCache(cacheKey);

  if (cachedSnapshot) {
    return cachedSnapshot;
  }

  const [anchors, receipts] = await Promise.allSettled([
    listWilsyMerkleAnchors({ tenantId: safeTenantId, limit: displayLimit, signal }),
    listWilsyMerkleReceipts({
      tenantId: safeTenantId,
      limit: displayLimit,
      replayLimit: proofReplayLimit,
      framework,
      receiptStatus,
      signal
    })
  ]);

  const receiptPayload = receipts.status === 'fulfilled' ? receipts.value : null;
  const receiptContract = receiptPayload?.receiptContract || null;
  const receiptOverlay = receiptPayload?.receiptOverlay || null;
  const derivedStatus = receiptContract ? {
    success: true,
    sourceStatus: 'RECEIPT_CONTRACT',
    routeVersion: receiptPayload?.routeVersion || null,
    algorithm: receiptPayload?.algorithm || 'SHA3-512',
    anchorMode: receiptContract.anchorMode,
    anchorProvider: receiptContract.anchorProvider,
    merkleRoot: receiptContract.merkleRoot,
    receiptMerkleRoot: receiptContract.receiptMerkleRoot,
    receiptCount: receiptContract.receiptCount,
    clausesAnchored: receiptContract.clausesAnchored,
    posture: receiptOverlay?.posture || receiptContract.status
  } : null;

  const snapshot = {
    version: WILSY_FORENSIC_MERKLE_CLIENT_VERSION,
    mode: 'SAFE_SNAPSHOT_RECEIPT_CONTRACT',
    tenantId: safeTenantId,
    status: derivedStatus,
    anchors: anchors.status === 'fulfilled' ? anchors.value : null,
    chain: receiptPayload,
    receipts: receiptPayload,
    receiptRows: Array.isArray(receiptPayload?.receipts) ? receiptPayload.receipts : [],
    receiptContract,
    receiptOverlay,
    errors: [anchors, receipts]
      .filter(result => result.status === 'rejected')
      .filter(result => !result.reason?.wilsyCancelled)
      .map(result => result.reason?.message || 'Unknown forensic bridge failure')
  };

  return writeWilsySnapshotCache(cacheKey, snapshot);
}



export const wilsyForensicMerkleClient = {
  appendWilsyForensicNoCacheParam,
  buildWilsyForensicAbortError,
  buildWilsyForensicRequestKey,
  buildWilsyForensicTimeoutError,
  buildWilsyForensicTransportError,
  buildWilsyMerkleCockpitSnapshot,
  buildWilsySnapshotCacheKey,
  readWilsySnapshotCache,
  writeWilsySnapshotCache,
  buildWilsyReceiptQueryParams,
  classifyWilsyForensicFetchError,
  createWilsyForensicTimeoutSignal,
  getWilsyForensicApiBaseCandidates,
  getWilsyMerkleAuditorStatus,
  getWilsyMerkleReceipt,
  getWilsyStoredAuthToken,
  isWilsyForensicAbortError,
  isWilsyJsonResponse,
  listWilsyMerkleAnchors,
  listWilsyMerkleReceipts,
  normalizeWilsyPositiveInteger,
  normalizeWilsyTenantId,
  parseWilsyForensicResponse,
  parseWilsyStoredTokenValue,
  requestWilsyForensicJson,
  sealWilsyMerkleSafeWindow,
  runWilsyMerkleAuditCycle,
  verifyWilsyForensicChain
};

export default wilsyForensicMerkleClient;
