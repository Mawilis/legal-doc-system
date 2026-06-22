/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ACCOUNT IDENTITY POSTURE CLIENT [R18AD12-BUSINESS-UI-REFINEMENT]                                            ║
 * ║ ESM ONLY | READ-ONLY POSTURE PROOF | BUSINESS LANGUAGE NORMALIZATION | ACCOUNT COMMAND CENTER VISUAL BRIDGE             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Fetches read-only Account identity posture proof for the Account Command Center.
 */

export const WILSY_ACCOUNT_IDENTITY_POSTURE_CLIENT_VERSION = 'R18AD12-BUSINESS-UI-REFINEMENT';

const DEFAULT_TENANT_ID = 'wilsy-sovereign-root';

/**
 * @function normalizeWilsyAccountIdentityTenantId
 * @description Normalizes Account identity posture tenant ids for safe read-only proof calls.
 * @param {string} tenantId - Tenant id candidate from the Account cockpit.
 * @returns {string} Safe tenant id.
 * @collaboration Prevents MASTER fallback from hiding the live sovereign-root posture proof.
 */
export function normalizeWilsyAccountIdentityTenantId(tenantId = DEFAULT_TENANT_ID) {
  const candidate = String(tenantId || '').trim();

  if (!candidate || ['MASTER', 'GLOBAL_ROOT', 'ROOT'].includes(candidate.toUpperCase())) {
    return DEFAULT_TENANT_ID;
  }

  return candidate;
}

/**
 * @function dedupeWilsyPostureOrigins
 * @description Removes duplicate API origin candidates while preserving order.
 * @param {string[]} origins - Origin candidates.
 * @returns {string[]} Unique origin candidates.
 * @collaboration Keeps fetch fallback deterministic across Vite, local backend and deployed API hosts.
 */
export function dedupeWilsyPostureOrigins(origins = []) {
  const seen = new Set();

  return origins
    .map(origin => String(origin || '').replace(/\/$/, ''))
    .filter((origin) => {
      if (seen.has(origin)) return false;
      seen.add(origin);
      return true;
    });
}

/**
 * @function buildWilsyAccountIdentityPostureBaseUrls
 * @description Builds ordered API base URL candidates for Account identity posture requests.
 * @returns {string[]} API base URL candidates.
 * @collaboration Falls back to the local backend when Vite does not expose VITE_API_URL.
 */
export function buildWilsyAccountIdentityPostureBaseUrls() {
  const viteApiUrl = String(import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
  const browserOrigin = typeof window !== 'undefined' ? String(window.location?.origin || '') : '';
  const isViteDevOrigin = /:(5173|5174|5175|5176)$/.test(browserOrigin);

  return dedupeWilsyPostureOrigins([
    viteApiUrl,
    isViteDevOrigin ? 'http://127.0.0.1:5050' : '',
    isViteDevOrigin ? 'http://localhost:5050' : '',
    ''
  ]);
}

/**
 * @function buildWilsyAccountIdentityPostureUrl
 * @description Builds the read-only identity posture URL for a tenant and API base URL.
 * @param {string} tenantId - Tenant id.
 * @param {string} baseUrl - API base URL.
 * @returns {string} Account identity posture endpoint URL.
 * @collaboration Ensures the frontend calls the backend route that proved Mongo and collection posture.
 */
export function buildWilsyAccountIdentityPostureUrl(tenantId = DEFAULT_TENANT_ID, baseUrl = '') {
  const safeTenantId = encodeURIComponent(normalizeWilsyAccountIdentityTenantId(tenantId));
  return `${String(baseUrl || '').replace(/\/$/, '')}/api/account/identity-posture?tenantId=${safeTenantId}`;
}

/**
 * @function buildWilsyBusinessSourceLabel
 * @description Converts backend collection proof into boardroom-grade source authority language.
 * @param {Object} input - Source label input.
 * @param {string} input.kind - Source kind.
 * @param {string} input.collectionName - Mongo collection name.
 * @param {number} input.collectionCount - Total Mongo collection count.
 * @returns {string} Business-facing source authority label.
 * @collaboration Removes diagnostic implementation language from the Account Command Center while preserving backend proof.
 */
export function buildWilsyBusinessSourceLabel({ kind = 'source', collectionName = '', collectionCount = 0 } = {}) {
  const sourceName = String(collectionName || '').trim();

  if (kind === 'identity') {
    return sourceName
      ? `Identity authority anchored · ${sourceName}`
      : 'Identity authority pending';
  }

  if (kind === 'crm') {
    return sourceName
      ? `Client intelligence anchored · ${sourceName}`
      : 'Client intelligence pending';
  }

  if (kind === 'database') {
    return collectionCount
      ? `Data command fabric live · ${collectionCount} collections`
      : 'Data command fabric pending';
  }

  return sourceName ? `Source authority anchored · ${sourceName}` : 'Source authority pending';
}

/**
 * @function buildWilsyBusinessSourceMapLabel
 * @description Converts matched backend collections into business-facing authority language.
 * @param {Object} input - Source map input.
 * @param {string} input.identitySource - Identity collection source.
 * @param {string} input.crmSource - CRM collection source.
 * @param {string[]} input.matchedCollections - Matched backend collections.
 * @returns {string} Business-facing source map label.
 * @collaboration Makes the Identity Command drill-down read like an operating proof rather than a database diagnostic.
 */
export function buildWilsyBusinessSourceMapLabel({ identitySource = '', crmSource = '', matchedCollections = [] } = {}) {
  const identity = String(identitySource || matchedCollections[0] || '').trim();
  const crm = String(crmSource || matchedCollections[1] || '').trim();

  if (identity && crm) return `Identity: ${identity} · Client intelligence: ${crm}`;
  if (identity) return `Identity authority: ${identity}`;
  if (crm) return `Client intelligence: ${crm}`;

  return 'Source authority pending';
}

/**
 * @function normalizeWilsyAccountIdentityPosturePayload
 * @description Normalizes backend Account identity posture into cockpit-safe business labels.
 * @param {Object} payload - Backend posture payload.
 * @returns {Object} Normalized visual posture packet.
 * @collaboration Converts backend proof fields into Account Command Center display values without mutating the cockpit contract.
 */
export function normalizeWilsyAccountIdentityPosturePayload(payload = {}) {
  const packet = payload && typeof payload === 'object' ? payload : {};
  const visual = packet.visual || {};
  const security = packet.security || {};
  const trustedDevices = packet.trustedDevices || {};
  const sessions = packet.sessions || {};
  const crmSources = packet.crmSources || {};
  const diagnostics = packet.diagnostics || {};
  const matchedCollections = Array.isArray(diagnostics.matchedCollections) ? diagnostics.matchedCollections : [];
  const identitySource = visual.deviceSourceLabel || trustedDevices.collectionName || matchedCollections[0] || '';
  const crmSource = visual.crmSourceLabel || crmSources.collectionName || sessions.collectionName || matchedCollections[1] || '';
  const collectionCount = Number(diagnostics.collectionCount || 0);

  return {
    ok: packet.ok === true,
    version: packet.version || WILSY_ACCOUNT_IDENTITY_POSTURE_CLIENT_VERSION,
    tenantId: normalizeWilsyAccountIdentityTenantId(packet.tenantId || DEFAULT_TENANT_ID),
    dbOnline: packet.dbOnline === true,
    status: packet.ok === true ? 'Identity authority verified' : 'Identity authority pending',
    sessionDetail: packet.sessionDetail || visual.backendLabel || 'Backend proof pending',
    backendLabel: packet.dbOnline ? 'Operating backend live' : 'Operating backend pending',
    dbLabel: buildWilsyBusinessSourceLabel({ kind: 'database', collectionCount }),
    trustedDevicesLabel: buildWilsyBusinessSourceLabel({ kind: 'identity', collectionName: identitySource }),
    sessionsLabel: buildWilsyBusinessSourceLabel({ kind: 'crm', collectionName: crmSource }),
    deviceSourceLabel: identitySource || 'identity source pending',
    crmSourceLabel: crmSource || 'client intelligence source pending',
    matchedCollectionsLabel: buildWilsyBusinessSourceMapLabel({
      identitySource,
      crmSource,
      matchedCollections
    }),
    mfaStatus: security.mfaStatus || 'Ready for enforcement',
    activityStatus: packet.dbOnline
      ? buildWilsyBusinessSourceLabel({ kind: 'database', collectionCount })
      : security.activityStatus || 'Command receipts active',
    collectionCount,
    generatedAt: packet.generatedAt || new Date().toISOString()
  };
}

/**
 * @function parseWilsyAccountIdentityPostureResponse
 * @description Parses and validates an Account identity posture response.
 * @param {Response} response - Fetch response.
 * @param {string} baseUrl - API base URL attempted.
 * @returns {Promise<Object>} Normalized posture packet.
 * @collaboration Makes failed fallback attempts debuggable without leaking browser authority.
 */
export async function parseWilsyAccountIdentityPostureResponse(response, baseUrl = '') {
  const contentType = String(response.headers?.get?.('content-type') || '');

  if (!response.ok) {
    throw new Error(`Posture ${response.status} from ${baseUrl || 'relative client origin'}`);
  }

  if (!contentType.includes('application/json')) {
    throw new Error(`Posture response was not JSON from ${baseUrl || 'relative client origin'}`);
  }

  const payload = await response.json();
  return normalizeWilsyAccountIdentityPosturePayload(payload);
}

/**
 * @function fetchWilsyAccountIdentityPostureFromBase
 * @description Fetches Account identity posture from a specific API base URL.
 * @param {Object} input - Fetch input.
 * @param {string} input.tenantId - Tenant id.
 * @param {string} input.baseUrl - API base URL.
 * @returns {Promise<Object>} Normalized posture packet.
 * @collaboration Isolates each fallback attempt for deterministic Account Center hydration.
 */
export async function fetchWilsyAccountIdentityPostureFromBase({ tenantId = DEFAULT_TENANT_ID, baseUrl = '' } = {}) {
  const safeTenantId = normalizeWilsyAccountIdentityTenantId(tenantId);

  const response = await fetch(buildWilsyAccountIdentityPostureUrl(safeTenantId, baseUrl), {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      'X-Tenant-Id': safeTenantId,
      'X-Wilsy-Account-Client': WILSY_ACCOUNT_IDENTITY_POSTURE_CLIENT_VERSION
    }
  });

  return parseWilsyAccountIdentityPostureResponse(response, baseUrl);
}

/**
 * @function fetchWilsyAccountIdentityPosture
 * @description Fetches read-only Account identity posture from the backend with local development fallback.
 * @param {Object} input - Fetch input.
 * @param {string} input.tenantId - Tenant id.
 * @returns {Promise<Object>} Normalized posture packet.
 * @collaboration Allows the Identity Command drill-down to show live backend and Mongo source proof.
 */
export async function fetchWilsyAccountIdentityPosture({ tenantId = DEFAULT_TENANT_ID } = {}) {
  const bases = buildWilsyAccountIdentityPostureBaseUrls();
  const failures = [];

  for (const baseUrl of bases) {
    try {
      const packet = await fetchWilsyAccountIdentityPostureFromBase({ tenantId, baseUrl });
      return {
        ...packet,
        transportBaseUrl: baseUrl || 'relative'
      };
    } catch (error) {
      failures.push(error?.message || `Posture failed from ${baseUrl || 'relative'}`);
    }
  }

  throw new Error(failures.join(' | '));
}

/**
 * @function fetchWilsyAccountComplianceCommand
 * @description Fetches the live backend-owned Account Compliance Command payload for the Account Command Center rail.
 * @param {Object} params - Fetch options.
 * @param {string} params.tenantId - Tenant identifier for the compliance command payload.
 * @param {number} params.limit - Receipt replay limit.
 * @returns {Promise<Object>} Live backend compliance command payload.
 * @collaboration Connects the Account Compliance UI to /api/account/compliance-command without browser-generated proof authority.
 */
export async function fetchWilsyAccountComplianceCommand({ tenantId = 'wilsy-sovereign-root', limit = 250 } = {}) {
  const safeTenantId = String(tenantId || 'wilsy-sovereign-root').trim() || 'wilsy-sovereign-root';
  const safeLimit = Math.min(Math.max(Number(limit || 250), 1), 1000);
  const apiBase = String(import.meta.env?.VITE_API_URL || 'http://localhost:5050').replace(/\/$/, '');
  const endpoint = `${apiBase}/api/account/compliance-command?tenantId=${encodeURIComponent(safeTenantId)}&limit=${encodeURIComponent(String(safeLimit))}`;

  let response;

  try {
    response = await fetch(endpoint, {
    method: 'GET',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      'X-Tenant-Id': safeTenantId
    }
  });
  } catch (error) {
    throw new Error(`ACCOUNT_COMPLIANCE_COMMAND_FETCH_FAILED: ${error?.message || 'network blocked'}`);
  }

  const packet = await response.json().catch(() => ({}));

  if (!response.ok || packet?.ok === false) {
    throw new Error(packet?.message || packet?.error || `ACCOUNT_COMPLIANCE_COMMAND_HTTP_${response.status}`);
  }

  return packet;
}
