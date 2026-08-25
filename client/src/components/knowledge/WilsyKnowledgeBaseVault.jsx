/* eslint-disable */

import React, { useEffect, useMemo, useState } from 'react';
import * as WilsyKnowledgeBaseVaultSha3 from 'js-sha3';
import {
  ChevronDown,
  ChevronUp,
  Download,
  Eye,
  FileJson,
  FileText,
  Library,
  PanelLeftClose,
  PanelLeftOpen,
  PanelTopClose,
  PanelTopOpen,
  Printer,
  X,
} from 'lucide-react';
import { buildWilsyDynamicSuggestions } from '../intelligence/wilsyAIDynamicSuggestionEngine';
import KnowledgeOperatingBar from './operating/KnowledgeOperatingBar';
import styles from './WilsyKnowledgeBaseVault.module.css';

/**
 * @function normalizeVaultText
 * @description Normalizes unknown Vault display values for compact UI rendering.
 * @param {unknown} value Source value.
 * @param {string} fallback Fallback value.
 * @returns {string} Display text.
 * @collaboration Knowledge Base Vault Vault UI, manifest metadata, and proof verification record display.
 */
function normalizeVaultText(value, fallback = 'Not recorded') {
  if (typeof value === 'string') return value.trim() || fallback;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}

/**
 * @function shortenDigest
 * @description Shortens long fingerprint values for readable proof-ledger rows.
 * @param {string} digest Full digest.
 * @returns {string} Short digest.
 * @collaboration Knowledge Base Vault fingerprint proof posture and compact Vault rows.
 */
function shortenDigest(digest = '') {
  const value = normalizeVaultText(digest, '');
  if (value.length <= 22) return value || 'Not recorded';
  return `${value.slice(0, 12)}...${value.slice(-10)}`;
}

const WILSY_KNOWLEDGE_BASE_ROUTE = '/knowledge-base/vault';
const WILSY_COMMAND_K_ORIGIN_KEY = 'wilsy:command-k-origin';
const WILSY_KNOWLEDGE_BASE_ORIGIN_TTL_MS = 1000 * 60 * 60 * 6;
const WILSY_KNOWLEDGE_BASE_ROUTE_LABELS = Object.freeze([
  { signal: '/founder', label: 'Founder Command' },
  { signal: '/executive', label: 'Executive Dashboard' },
  { signal: '/crm', label: 'CRM' },
  { signal: '/sales', label: 'Sales Dashboard' },
  { signal: '/finance', label: 'Finance Dashboard' },
  { signal: '/hr', label: 'HR Dashboard' },
  { signal: '/documents', label: 'Documents' },
  { signal: '/artifacts', label: 'Artifact Studio' },
  { signal: '/billing', label: 'Billing' },
  { signal: '/revenue-ledger', label: 'Revenue Ledger' },
  { signal: '/account', label: 'Account' },
  { signal: '/legal', label: 'Legal' },
  { signal: '/client-portal', label: 'Client Portal' },
]);
const WILSY_KNOWLEDGE_BASE_DASHBOARD_LABELS = Object.freeze({
  FOUNDER_DASHBOARD: 'Founder Command',
  EXECUTIVE_DASHBOARD: 'Executive Dashboard',
  CRM_DASHBOARD: 'CRM',
  SALES_DASHBOARD: 'Sales Dashboard',
  FINANCE_DASHBOARD: 'Finance Dashboard',
  HR_DASHBOARD: 'HR Dashboard',
  IT_DASHBOARD: 'IT Dashboard',
  GENERAL_DASHBOARD: 'Tenant Command Center',
  TENANT_COMMAND_CENTER: 'Tenant Command Center',
});

/**
 * @function normalizeKnowledgeBaseRoutePath
 * @description Normalizes route strings before Knowledge Base origin comparison.
 * @param {string} route Runtime route candidate.
 * @returns {string} Normalized route.
 * @collaboration Knowledge Base return button, Command K origin packets, and workspace route matching.
 */
function normalizeKnowledgeBaseRoutePath(route = '') {
  const cleanRoute = String(route || '').trim();
  if (!cleanRoute) return '';

  try {
    const baseOrigin = typeof window !== 'undefined' ? window.location.origin : 'http://wilsy.local';
    return new URL(cleanRoute, baseOrigin).pathname || cleanRoute;
  } catch {
    return cleanRoute.split('?')[0].split('#')[0] || cleanRoute;
  }
}

/**
 * @function resolveKnowledgeBaseWorkspaceLabel
 * @description Resolves a readable workspace label from a route, dashboard key, or safe display label without defaulting to CRM.
 * @param {object} origin Command K origin packet.
 * @returns {string} Workspace label.
 * @collaboration Dynamic Knowledge Base return command, global Command K, Founder Command K, and direct route fallback.
 */
function resolveKnowledgeBaseWorkspaceLabel(origin = {}) {
  const route = normalizeKnowledgeBaseRoutePath(origin.route);
  const dashboardKey = String(origin.dashboardKey || origin.currentDashboardKey || '').trim().toUpperCase();
  const genericLabels = new Set(['', 'WILSY OS 2050', 'PREVIOUS WORKSPACE', 'COMMAND PALETTE ORIGIN']);
  const explicitLabel = String(origin.label || origin.workspaceLabel || '').trim();

  const routeMatch = WILSY_KNOWLEDGE_BASE_ROUTE_LABELS.find((item) => route.toLowerCase().startsWith(item.signal));
  if (routeMatch) return routeMatch.label;
  if (WILSY_KNOWLEDGE_BASE_DASHBOARD_LABELS[dashboardKey]) return WILSY_KNOWLEDGE_BASE_DASHBOARD_LABELS[dashboardKey];
  if (!genericLabels.has(explicitLabel.toUpperCase())) return explicitLabel;

  return 'Previous workspace';
}

/**
 * @function resolveStoredKnowledgeBaseOrigin
 * @description Reads the Command K origin packet and rejects stale, malformed, or self-referential Knowledge Base origins.
 * @returns {object} Safe origin packet.
 * @collaboration Knowledge Base dynamic return button, global Command K launch packets, and stale-origin protection.
 */
function resolveStoredKnowledgeBaseOrigin() {
  if (typeof window === 'undefined') {
    return {
      route: '/',
      label: 'Previous workspace',
      dashboardKey: 'GLOBAL_WORKSPACE',
    };
  }

  try {
    const rawOrigin = window.sessionStorage.getItem(WILSY_COMMAND_K_ORIGIN_KEY)
      || window.localStorage.getItem(WILSY_COMMAND_K_ORIGIN_KEY);
    const parsedOrigin = rawOrigin ? JSON.parse(rawOrigin) : null;
    const route = normalizeKnowledgeBaseRoutePath(parsedOrigin?.route || '');
    const generatedAt = Date.parse(parsedOrigin?.generatedAt || parsedOrigin?.requestedAt || '');
    const stale = Number.isFinite(generatedAt)
      ? Date.now() - generatedAt > WILSY_KNOWLEDGE_BASE_ORIGIN_TTL_MS
      : false;

    if (parsedOrigin?.route && route !== WILSY_KNOWLEDGE_BASE_ROUTE && !stale) {
      return {
        ...parsedOrigin,
        route,
        label: resolveKnowledgeBaseWorkspaceLabel({ ...parsedOrigin, route }),
      };
    }
  } catch {
    // A malformed optional origin packet should never block the Knowledge Base.
  }

  return {
    route: '/',
    label: 'Previous workspace',
    dashboardKey: 'GLOBAL_WORKSPACE',
  };
}

/**
 * @function readStoredVaultContext
 * @description Reads tenant and operator context from browser storage without hard-coded personal identity.
 * @returns {object} Browser context for institutional Vault evidence.
 * @collaboration Knowledge Base VaultE2 Vault integrity, authenticated backend context, and tenant posture.
 */

/**
 * @function createVaultRequestProof
 * @description Creates the Knowledge Base Vault forensic request proof using the existing sha512(type|tenantId|timestamp) contract.
 * @param {string} type Vault artifact request type.
 * @param {string} tenantId Tenant id.
 * @param {string} timestamp Request timestamp.
 * @returns {Promise<string>} Request proof digest.
 * @collaboration Knowledge Base VaultK forensic seal compatibility, BusinessArtifactStudio proof pattern, and saved document Vault reads.
 */

/**
 * @function stableVaultSealValue
 * @description Sorts Vault payload values into the deterministic structure used for fingerprint request seal reconstruction.
 * @param {*} value Payload value.
 * @returns {*} Stable value.
 * @collaboration Knowledge Base VaultN Knowledge Base Vault, ProductionHardening, auth seal verification, and saved artifact reads.
 */
function stableVaultSealValue(value) {
  if (Array.isArray(value)) {
    return value.map(stableVaultSealValue);
  }

  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((nextValue, key) => {
        nextValue[key] = stableVaultSealValue(value[key]);
        return nextValue;
      }, {});
  }

  return value;
}

/**
 * @function stableVaultSealStringify
 * @description Converts a Vault request body into deterministic JSON for request seal reconstruction.
 * @param {object} payload Request payload.
 * @returns {string} Stable JSON string.
 * @collaboration Knowledge Base VaultN Vault runtime smoke, browser fetch, and backend forensic seal validation.
 */
function stableVaultSealStringify(payload = {}) {
  return JSON.stringify(stableVaultSealValue(payload));
}

/**
 * @function hashVaultSha3512
 * @description Hashes the Vault seal reconstruction string with fingerprint-512 uppercase hex output.
 * @param {string} reconstruction Seal reconstruction string.
 * @returns {string} Uppercase fingerprint-512 digest.
 * @collaboration js-sha3, auth.js forensic seal validation, and Vault request signing.
 */
function hashVaultSha3512(reconstruction = '') {
  const candidate = WilsyKnowledgeBaseVaultSha3.sha3_512
    || WilsyKnowledgeBaseVaultSha3.default?.sha3_512
    || WilsyKnowledgeBaseVaultSha3.default;

  if (typeof candidate !== 'function') {
    throw new Error('KNOWLEDGE_BASE_VAULT_fingerprint_512_UNAVAILABLE');
  }

  return String(candidate(String(reconstruction))).toUpperCase();
}

/**
 * @function buildVaultRequestSealHeaders
 * @description Builds Wilsy auth-compatible X-Request-Seal headers for a Vault request body.
 * @param {object} payload Request payload.
 * @returns {object} Signed request seal header packet.
 * @collaboration Knowledge Base VaultN auth seal layer, ProductionHardening, Knowledge Base Vault, and fingerprint request integrity.
 */
function buildVaultRequestSealHeaders(payload = {}) {
  const traceId = String(payload.requestId || `REQ-WILSY-KB-VAULT-${Date.now()}`);
  const timestamp = String(payload.generatedAt || payload.timestamp || new Date().toISOString());
  const nonce = `NONCE-WILSY-KB-VAULT-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  const payloadString = stableVaultSealStringify(payload);
  const reconstruction = `${traceId}|${timestamp}|${payloadString}|${nonce}`;
  const requestSeal = hashVaultSha3512(reconstruction);

  return {
    traceId,
    timestamp,
    nonce,
    requestSeal,
    headers: {
      'X-Trace-Id': traceId,
      'X-Wilsy-Trace-Id': traceId,
      'X-Correlation-ID': traceId,
      'X-Request-Timestamp': timestamp,
      'X-Forensic-Timestamp': timestamp,
      'X-Timestamp': timestamp,
      'X-Generated-At': timestamp,
      'X-Cryptographic-Nonce': nonce,
      'X-Request-Nonce': nonce,
      'X-Request-Seal': requestSeal,
      'X-Wilsy-Request-Seal': requestSeal,
      'X-Wilsy-Forensic-Seal': requestSeal,
      'X-Forensic-Seal': requestSeal,
      'X-Wilsy-Evidence-Seal': requestSeal,
      'X-Wilsy-Knowledge-Base-Vault-Seal': requestSeal,
    },
  };
}

/**
 * @function createVaultRequestProof
 * @description Creates the Knowledge Base Vault forensic request proof using the existing sha512(type|tenantId|timestamp) contract.
 * @param {string} type Vault artifact request type.
 * @param {string} tenantId Tenant id.
 * @param {string} timestamp Request timestamp.
 * @returns {Promise<string>} Request proof digest.
 * @collaboration Knowledge Base VaultP forensic seal compatibility, BusinessArtifactStudio proof pattern, and saved document Vault reads.
 */
async function createVaultRequestProof(type = '', tenantId = '', timestamp = '') {
  const source = `${type}|${tenantId}|${timestamp}`;
  const buffer = new TextEncoder().encode(source);
  const digest = await crypto.subtle.digest('SHA-512', buffer);

  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

/**
 * @function readStoredVaultContext
 * @description Reads tenant and operator context from browser storage without hard-coded personal identity.
 * @returns {object} Browser context for institutional Vault evidence.
 * @collaboration Knowledge Base VaultK2 Vault integrity, authenticated backend context, and forensic request proof transport.
 */
function readStoredVaultContext() {
  const storageKeys = [
    'wilsyUser',
    'wilsy_user',
    'user',
    'authUser',
    'currentUser',
    'wilsyAuthUser',
  ];

  let parsedUser = {};

  for (const key of storageKeys) {
    try {
      const value = window.localStorage.getItem(key) || window.sessionStorage.getItem(key);
      if (!value) continue;

      const candidate = JSON.parse(value);
      if (candidate && typeof candidate === 'object') {
        parsedUser = candidate;
        break;
      }
    } catch {
      continue;
    }
  }

  const tenantId =
    window.localStorage.getItem('tenantId') ||
    window.localStorage.getItem('wilsyTenantId') ||
    window.sessionStorage.getItem('tenantId') ||
    window.sessionStorage.getItem('wilsyTenantId') ||
    parsedUser.tenantId ||
    parsedUser.tenant?._id ||
    parsedUser.tenant?.id ||
    'AUTHENTICATED_TENANT_CONTEXT';

  const operatorId =
    parsedUser._id ||
    parsedUser.id ||
    parsedUser.userId ||
    parsedUser.operatorId ||
    window.localStorage.getItem('userId') ||
    window.localStorage.getItem('operatorId') ||
    window.sessionStorage.getItem('userId') ||
    window.sessionStorage.getItem('operatorId') ||
    'AUTHENTICATED_BACKEND_USER_CONTEXT';

  return {
    tenantId,
    operatorId,
  };
}

/**
 * @function createVaultInstitutionalBody
 * @description Creates mirrored institutionalHeaders and strikePayload evidence for Vault reads.
 * @param {string} route Runtime route.
 * @param {string} commandSurface Command surface name.
 * @returns {object} Institutional request body.
 * @collaboration Knowledge Base VaultE2 institutional integrity gate and Knowledge Base Vault actions.
 */
async function createVaultInstitutionalBody(route, commandSurface) {
  const context = readStoredVaultContext();
  const generatedAt = new Date().toISOString();
  const timestamp = generatedAt;
  const type = 'KNOWLEDGE_BASE_VAULT_READ_ONLY';
  const nonce = `NONCE-WILSY-KB-VAULT-${Date.now()}`;
  const requestId = `REQ-WILSY-KB-VAULT-${Date.now()}`;
  const requestProof = await createVaultRequestProof(type, context.tenantId, timestamp);
  const institutionalHeaders = {
    tenantId: context.tenantId,
    operatorId: context.operatorId,
    route,
    commandSurface,
    generatedAt,
    requestId,
  };

  return {
    type,
    timestamp,
    nonce,
    requestProof,
    route,
    commandSurface,
    tenantId: context.tenantId,
    operatorId: context.operatorId,
    generatedAt,
    requestId,
    savedArtifactsOnly: true,
    sourceMode: 'KNOWLEDGE_BASE_VAULT_READ_ONLY',
    metadata: {
      type,
      tenantId: context.tenantId,
      timestamp,
      requestProof,
      nonce,
    },
    institutionalHeaders,
    strikePayload: {
      type,
      timestamp,
      nonce,
      requestProof,
      route,
      commandSurface,
      tenantId: context.tenantId,
      operatorId: context.operatorId,
      generatedAt,
      requestId,
      institutionalHeaders,
      sourceMode: 'KNOWLEDGE_BASE_VAULT_READ_ONLY',
      savedArtifactsOnly: true,
      metadata: {
        type,
        tenantId: context.tenantId,
        timestamp,
        requestProof,
        nonce,
      },
    },
  };
}

/**
 * @function resolveVaultAuthHeaders
 * @description Resolves Vault fetch headers using the live Wilsy OS browser token keys while preserving cookie authentication.
 * @returns {object} Fetch headers.
 * @collaboration Knowledge Base Vault authenticated reads, authContext token storage, sovereignClient compatibility, and protected sovereign library search.
 */
function resolveVaultAuthHeaders() {
  const rawToken =
    window.localStorage.getItem('wilsy_auth_token') ||
    window.localStorage.getItem('token') ||
    window.localStorage.getItem('accessToken') ||
    window.localStorage.getItem('authToken') ||
    window.localStorage.getItem('wilsy_token') ||
    window.localStorage.getItem('wilsyToken') ||
    window.localStorage.getItem('sovereignToken') ||
    window.localStorage.getItem('sovereign_token') ||
    window.sessionStorage.getItem('wilsy_auth_token') ||
    window.sessionStorage.getItem('token') ||
    window.sessionStorage.getItem('accessToken') ||
    window.sessionStorage.getItem('authToken') ||
    window.sessionStorage.getItem('wilsy_token') ||
    window.sessionStorage.getItem('wilsyToken') ||
    window.sessionStorage.getItem('sovereignToken') ||
    window.sessionStorage.getItem('sovereign_token') ||
    '';

  const token = String(rawToken || '').replace(/^Bearer\s+/i, '').replace(/^[\"']|[\"']$/g, '').trim();

  return {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    'X-Wilsy-Command-Surface': 'knowledge_base_vault',
    'X-Wilsy-Auth-Transport': token ? 'browser-bearer' : 'browser-session-missing',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/**
 * @function fetchVaultJson
 * @description Fetches Vault JSON through POST with institutionalHeaders and strikePayload evidence.
 * @param {string} url Vault API URL.
 * @param {string} commandSurface Command surface.
 * @returns {Promise<object>} Parsed JSON payload.
 * @collaboration Knowledge Base VaultE2 Vault list and proof verification record reads.
 */
async function fetchVaultJson(url, commandSurface, extraBody = {}) {
  const evidenceBody = await createVaultInstitutionalBody(url, commandSurface);
  const requestBody = {
    ...evidenceBody,
    ...extraBody,
    filters: extraBody.filters || evidenceBody.filters || {},
  };
  const sealContract = buildVaultRequestSealHeaders(requestBody);
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      ...resolveVaultAuthHeaders(),
      ...sealContract.headers,
      'X-Wilsy-Institutional-Headers': encodeURIComponent(JSON.stringify(requestBody.institutionalHeaders)),
      'X-Wilsy-Strike-Payload': encodeURIComponent(JSON.stringify(requestBody.strikePayload)),
      'X-Request-Proof': requestBody.requestProof,
      'X-Artifact-Proof': requestBody.requestProof,
      'X-Artifact-Type': requestBody.type,
      'X-Artifact-Timestamp': requestBody.timestamp,
      'X-Artifact-Nonce': requestBody.nonce,
      'X-Timestamp': requestBody.timestamp,
      'X-Nonce': requestBody.nonce,
      'X-Generated-At': requestBody.generatedAt,
      'X-Request-Id': requestBody.requestId,
      'X-Route': url,
      'X-Command-Surface': commandSurface,
      'X-Operator-Id': requestBody.operatorId,
      'X-Tenant-Id': requestBody.tenantId,
    },
    body: JSON.stringify(requestBody),
  });

  const payload = await response.json();

  if (!response.ok || !payload.success) {
    throw new Error(payload.error || payload.message || 'KNOWLEDGE_BASE_VAULT_REQUEST_FAILED');
  }

  return payload;
}

/**
 * @function fetchVaultBlob
 * @description Fetches saved Vault document or JSON data through POST with institutional evidence.
 * @param {string} url Vault artifact URL.
 * @param {string} commandSurface Command surface.
 * @param {string} acceptMime Accept MIME type.
 * @returns {Promise<Blob>} Artifact blob.
 * @collaboration Knowledge Base VaultE2 saved document actions, JSON companion actions, and no-regeneration Vault contract.
 */
async function fetchVaultBlob(url, commandSurface, acceptMime = 'application/pdf') {
  const evidenceBody = await createVaultInstitutionalBody(url, commandSurface);
  const sealContract = buildVaultRequestSealHeaders(evidenceBody);
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      ...resolveVaultAuthHeaders(),
      ...sealContract.headers,
      Accept: acceptMime,
      'X-Wilsy-Institutional-Headers': encodeURIComponent(JSON.stringify(evidenceBody.institutionalHeaders)),
      'X-Wilsy-Strike-Payload': encodeURIComponent(JSON.stringify(evidenceBody.strikePayload)),
      'X-Request-Proof': evidenceBody.requestProof,
      'X-Artifact-Proof': evidenceBody.requestProof,
      'X-Artifact-Type': evidenceBody.type,
      'X-Artifact-Timestamp': evidenceBody.timestamp,
      'X-Artifact-Nonce': evidenceBody.nonce,
      'X-Timestamp': evidenceBody.timestamp,
      'X-Nonce': evidenceBody.nonce,
      'X-Generated-At': evidenceBody.generatedAt,
      'X-Request-Id': evidenceBody.requestId,
      'X-Route': url,
      'X-Command-Surface': commandSurface,
      'X-Operator-Id': evidenceBody.operatorId,
      'X-Tenant-Id': evidenceBody.tenantId,
    },
    body: JSON.stringify(evidenceBody),
  });

  if (!response.ok) {
    let message = 'KNOWLEDGE_BASE_VAULT_document_REQUEST_FAILED';

    try {
      const payload = await response.json();
      message = payload.error || payload.message || message;
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response.blob();
}

// FG108O5C9B_VAULT_INVALID_TOKEN_RACE_GUARD
let wilsyKnowledgeVaultListInFlight = null;
let wilsyKnowledgeVaultLastPayload = null;
let wilsyKnowledgeVaultLastFiltersKey = '';

/**
 * @function useKnowledgeBaseVaultData
 * @description Loads the Knowledge Base Vault through a single in-flight request and preserves the last valid payload when a later auth race returns INVALID_TOKEN.
 * @param {object} filters Active Vault search and category filters.
 * @returns {object} Vault loader state and reload command.
 * @collaboration Knowledge Base Vault, restored advanced receipt cockpit, auth refresh race protection, and saved-document backend resolver.
 */
function useKnowledgeBaseVaultData(filters = {}) {
  const filtersKey = JSON.stringify({
    query: filters?.query || '',
    category: filters?.category || 'all',
    lifecycle: filters?.lifecycle || 'all',
    module: filters?.module || 'all',
    playbookType: filters?.playbookType || 'all',
  });

  const [state, setState] = useState({
    loading: !wilsyKnowledgeVaultLastPayload,
    error: '',
    vault: wilsyKnowledgeVaultLastPayload?.vault || null,
  });

  /**
   * @function loadVault
   * @description Executes a deduplicated Vault list request and keeps the last successful Vault payload if a duplicate auth validation race fails.
   * @param {object} options Loader options.
   * @returns {Promise<object|null>} Loaded Vault payload or cached payload.
   * @collaboration Knowledge Base Vault loader, auth-shield race protection, and frontend state integrity.
   */
  const loadVault = async (options = {}) => {
    const cachedForKey = wilsyKnowledgeVaultLastPayload && wilsyKnowledgeVaultLastFiltersKey === filtersKey
      ? wilsyKnowledgeVaultLastPayload
      : null;

    setState((current) => ({
      ...current,
      loading: true,
      error: '',
      vault: current.vault || cachedForKey?.vault || wilsyKnowledgeVaultLastPayload?.vault || null,
    }));

    if (wilsyKnowledgeVaultListInFlight && wilsyKnowledgeVaultListInFlight.key === filtersKey) {
      try {
        const payload = await wilsyKnowledgeVaultListInFlight.promise;

        wilsyKnowledgeVaultLastPayload = payload;
        wilsyKnowledgeVaultLastFiltersKey = filtersKey;

        setState({
          loading: false,
          error: '',
          vault: payload?.vault || null,
        });

        return payload;
      } catch (error) {
        const message = error?.message || String(error || 'Knowledge Base Vault request failed');
        const fallback = cachedForKey || wilsyKnowledgeVaultLastPayload;
        const isInvalidTokenRace = /INVALID_TOKEN|invalid token|Token validation fracture/i.test(message);

        if (isInvalidTokenRace && fallback?.vault) {
          setState({
            loading: false,
            error: '',
            vault: fallback.vault,
          });

          return fallback;
        }

        setState({
          loading: false,
          error: message,
          vault: fallback?.vault || null,
        });

        return fallback || null;
      }
    }

    const requestPromise = fetchVaultJson('/api/knowledge-base/vault', 'knowledge_base_vault_list', {
      filters,
      query: filters?.query || '',
      category: filters?.category || 'all',
    });

    wilsyKnowledgeVaultListInFlight = {
      key: filtersKey,
      promise: requestPromise,
      startedAt: Date.now(),
    };

    try {
      const payload = await requestPromise;

      wilsyKnowledgeVaultLastPayload = payload;
      wilsyKnowledgeVaultLastFiltersKey = filtersKey;

      setState({
        loading: false,
        error: '',
        vault: payload?.vault || null,
      });

      return payload;
    } catch (error) {
      const message = error?.message || String(error || 'Knowledge Base Vault request failed');
      const fallback = cachedForKey || wilsyKnowledgeVaultLastPayload;
      const isInvalidTokenRace = /INVALID_TOKEN|invalid token|Token validation fracture/i.test(message);

      if (isInvalidTokenRace && fallback?.vault) {
        setState({
          loading: false,
          error: '',
          vault: fallback.vault,
        });

        return fallback;
      }

      setState({
        loading: false,
        error: message,
        vault: fallback?.vault || null,
      });

      return fallback || null;
    } finally {
      if (wilsyKnowledgeVaultListInFlight?.promise === requestPromise) {
        wilsyKnowledgeVaultListInFlight = null;
      }
    }
  };

  useEffect(() => {
    void loadVault({ forceLive: true });
  }, [filtersKey]);

  return {
    ...state,
    reload: () => loadVault({ forceLive: true }),
  };
}

/**
 * @function resolveFilteredVaultEntries
 * @description Filters Vault entries by title, artifact type, posture, tag, generated by, and fingerprint proof text.
 * @param {Array<object>} entries Vault entries.
 * @param {string} query Search query.
 * @returns {Array<object>} Filtered entries.
 * @collaboration Knowledge Base Vault searchable proof library and source-aware artifact rows.
 */
function resolveFilteredVaultEntries(entries = [], query = '') {
  const search = query.trim().toLowerCase();

  if (!search) return entries;

  return entries.filter((entry) => {
    const haystack = [
      entry.title,
      entry.artifactType,
      entry.sourcePosture,
      entry.generatedByDisplayName,
      entry.sourceTag,
      entry.sourceCommit,
      entry.pdfSha3,
      entry.jsonSha3,
      entry.jsonStatus,
      entry.proofStatus,
      entry.lockStatus,
      entry.permissionMode,
    ]
      .map((item) => normalizeVaultText(item, '').toLowerCase())
      .join(' ');

    return haystack.includes(search);
  });
}

/**
 * @function openVaultUrl
 * @description Opens a saved Vault route in a browser tab without regenerating the artifact.
 * @param {string} url Saved artifact route.
 * @returns {Promise<string>} Object URL opened for the saved artifact.
 * @collaboration Knowledge Base Vault saved PDF controls, receipt cockpit actions, and no-regeneration route contract.
 */
async function openVaultUrl(url = '') {
  if (!url) {
    throw new Error('KNOWLEDGE_BASE_VAULT_URL_MISSING');
  }

  const blob = await fetchVaultBlob(url, 'knowledge_base_vault_open_pdf');
  const objectUrl = URL.createObjectURL(blob);
  const openedWindow = window.open(objectUrl, '_blank', 'noopener,noreferrer');

  if (!openedWindow) {
    throw new Error('KNOWLEDGE_BASE_VAULT_POPUP_BLOCKED');
  }

  return objectUrl;
}

/**
 * @function createVaultPdfPreview
 * @description Creates a controlled in-workspace PDF preview URL from a saved Vault document route without regenerating the artifact.
 * @param {object} entry Vault entry.
 * @returns {Promise<object>} PDF preview descriptor.
 * @collaboration Knowledge Base Vault document workspace, controlled PDF container, saved artifact routes, and MDN object URL lifecycle guidance.
 */
async function createVaultPdfPreview(entry = {}) {
  const url = entry.routes?.pdfOpenUrl || entry.pdfOpenUrl;

  if (!url) {
    throw new Error('KNOWLEDGE_BASE_VAULT_PDF_URL_MISSING');
  }

  const blob = await fetchVaultBlob(url, 'knowledge_base_vault_preview_pdf');
  const objectUrl = URL.createObjectURL(blob);

  return {
    objectUrl,
    title: entry.title || 'Knowledge Base document',
    artifactId: entry.id || '',
    openedAt: new Date().toISOString(),
  };
}

/**
 * @function downloadVaultPdf
 * @description Triggers download for a saved Knowledge Base document route.
 * @param {object} entry Vault entry.
 * @returns {void}
 * @collaboration Knowledge Base Vault saved document download and no-regeneration route contract.
 */
async function downloadVaultPdf(entry = {}) {
  const url = entry.routes?.pdfDownloadUrl;
  if (!url) return;

  const blob = await fetchVaultBlob(url, 'knowledge_base_vault_download_pdf');
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = objectUrl;
  link.download = `${entry.id || 'knowledge-base-artifact'}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

/**
 * @function printVaultPdf
 * @description Opens a saved document route for printing without calling the document generator.
 * @param {object} entry Vault entry.
 * @returns {void}
 * @collaboration Knowledge Base Vault saved document print action and browser-native document viewer.
 */
async function printVaultPdf(entry = {}) {
  const url = entry.routes?.pdfOpenUrl;
  if (!url) return;

  const blob = await fetchVaultBlob(url, 'knowledge_base_vault_print_pdf');
  const objectUrl = URL.createObjectURL(blob);
  const printWindow = window.open(objectUrl, '_blank', 'noopener,noreferrer');

  if (printWindow) {
    printWindow.addEventListener('load', () => {
      try {
        printWindow.print();
      } catch {
        return undefined;
      }

      return undefined;
    }, { once: true });
  }
}



/**
 * @function toVaultTitleCase
 * @description Converts internal Vault tokens into readable title case for frontend display.
 * @param {string} value Raw backend or manifest token.
 * @returns {string} Human-readable label.
 * @collaboration Knowledge Base VaultB frontend language sanitization, proof ledger readability, and backend enum hiding.
 */
function toVaultTitleCase(value = '') {
  return String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

/**
 * @function displayVaultSourceMode
 * @description Converts Vault source mode into customer-facing language.
 * @param {string} value Source mode token.
 * @returns {string} Customer-facing source posture.
 * @collaboration Knowledge Base VaultB no-backend-language UI policy and saved artifact discipline.
 */
function displayVaultSourceMode(value = '') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('MANIFEST') && normalized.includes('SAVED')) {
    return 'Source Authority';
  }

  if (normalized.includes('SAVED')) {
    return 'Saved artifacts only';
  }

  return 'Verified library';
}

/**
 * @function displayVaultPermissionMode
 * @description Converts internal permission mode into user-facing access language.
 * @param {string} value Permission mode token.
 * @returns {string} User-facing access label.
 * @collaboration Knowledge Base VaultB founder/admin knowledge access, tenant-safe wording, and backend enum hiding.
 */
function displayVaultPermissionMode(value = '') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('FOUNDER') || normalized.includes('ADMIN')) {
    return 'Founder access';
  }

  if (normalized.includes('TENANT')) {
    return 'Team access';
  }

  return 'Permissioned access';
}

/**
 * @function displayVaultProofStatus
 * @description Converts proof status tokens into readable proof posture.
 * @param {string} value Proof status token.
 * @returns {string} Readable proof posture.
 * @collaboration Knowledge Base VaultB proof verification record UX, fingerprint confidence language, and operator readability.
 */
function displayVaultProofStatus(value = '') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('MATCH')) {
    return 'Verified';
  }

  if (normalized.includes('MISSING')) {
    return 'Proof missing';
  }

  if (normalized.includes('FAILED')) {
    return 'Proof needs review';
  }

  return toVaultTitleCase(value || 'Proof pending');
}

/**
 * @function displayVaultJsonStatus
 * @description Converts saved JSON companion state into customer-facing Knowledge Base language.
 * @param {object} entry Vault entry.
 * @returns {string} JSON companion status.
 * @collaboration Knowledge Base Vault JSON companion action, selected summary, and user-facing evidence posture.
 */
function displayVaultJsonStatus(entry = {}) {
  const status = String(entry?.jsonStatus || '').toUpperCase();

  if (status.includes('MATCH')) {
    return 'JSON verified';
  }

  if (entry?.jsonPresent || status.includes('AVAILABLE')) {
    return 'JSON ready';
  }

  return 'PDF only';
}

/**
 * @function displayVaultSourcePosture
 * @description Converts source posture into customer-facing verification language.
 * @param {string} value Source posture token.
 * @returns {string} Customer-facing source posture.
 * @collaboration Knowledge Base VaultB source posture display, Knowledge Base confidence language, and backend enum hiding.
 */
function displayVaultSourcePosture(value = '') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('VERIFIED')) {
    return 'Verified';
  }

  if (normalized.includes('PENDING')) {
    return 'Pending review';
  }

  return toVaultTitleCase(value || 'Verified');
}

/**
 * @function displayVaultLockStatus
 * @description Converts lock status into customer-facing artifact lock language.
 * @param {string} value Lock token.
 * @returns {string} Customer-facing lock label.
 * @collaboration Knowledge Base VaultB lock posture display, production Vault polish, and backend enum hiding.
 */
function displayVaultLockStatus(value = '') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('LOCK') || normalized.includes('VERIFIED')) {
    return 'Locked';
  }

  return toVaultTitleCase(value || 'Controlled');
}

/**
 * @function displayVaultArtifactType
 * @description Converts artifact type tokens into readable artifact names.
 * @param {string} value Artifact type token.
 * @returns {string} Readable artifact type.
 * @collaboration Knowledge Base VaultB artifact lane readability and customer-facing Knowledge Base language.
 */
function displayVaultArtifactType(value = '') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('KNOWLEDGE_BASE_PRODUCTION_PLAYBOOK')) {
    return 'Production Knowledge Base playbook';
  }

  if (normalized.includes('INLINE_COMMAND_PLAYBOOK')) {
    return 'AI command playbook';
  }

  if (normalized.includes('PLAYBOOK')) {
    return 'Playbook';
  }

  return toVaultTitleCase(value || 'Knowledge artifact');
}

/**
 * @function displayVaultManifestSource
 * @description Hides source file paths while preserving readable manifest identity.
 * @param {string} value Manifest source path.
 * @returns {string} Customer-facing manifest label.
 * @collaboration Knowledge Base VaultB path hiding, source evidence controls, and production Knowledge Base UI.
 */
function displayVaultManifestSource(value = '') {
  if (!value) {
    return 'Knowledge Base Manifest';
  }

  return 'Knowledge Base Manifest';
}

/**
 * @function displayVaultSourceTag
 * @description Converts long source tags into a compact customer-facing release label.
 * @param {string} value Source tag or commit.
 * @returns {string} Customer-facing release label.
 * @collaboration Knowledge Base VaultB source tag readability, proof inspector copy controls, and release evidence hiding.
 */
function displayVaultSourceTag(value = '') {
  const release = String(value || '').trim();

  if (!release) {
    return 'Release recorded';
  }

  if (release.length >= 7) {
    return 'Locked release';
  }

  return 'Verified release';
}

/**
 * @function displayVaultTextPosture
 * @description Converts required/forbidden text posture tokens into plain language.
 * @param {string} value Text posture token.
 * @param {string} kind Posture kind.
 * @returns {string} Plain-language posture.
 * @collaboration Knowledge Base VaultB proof text posture readability and backend token hiding.
 */
function displayVaultTextPosture(value = '', kind = 'text') {
  const normalized = String(value || '').toUpperCase();

  if (normalized.includes('DECLARED') && kind === 'required') {
    return 'Required checks declared';
  }

  if (normalized.includes('DECLARED') && kind === 'forbidden') {
    return 'Forbidden checks declared';
  }

  return toVaultTitleCase(value || 'Checks recorded');
}


/**
 * @function displayVaultArtifactIdentity
 * @description Converts raw artifact identifiers into customer-facing document identity labels.
 * @param {object} entry Vault entry.
 * @returns {string} Customer-facing document identity.
 * @collaboration Knowledge Base VaultC backend-language hiding, inspector readability, and copy-only technical evidence posture.
 */
function displayVaultArtifactIdentity(entry = {}) {
  const title = String(entry?.title || '').trim();

  if (title) {
    return title;
  }

  return 'Knowledge Base document';
}

/**
 * @function displayVaultDigest
 * @description Displays fingerprint values without exposing an overwhelming raw digest in the primary lane.
 * @param {string} value fingerprint digest.
 * @returns {string} Compact digest display.
 * @collaboration Knowledge Base VaultB fingerprint presentation, copy controls, and proof inspector readability.
 */
function displayVaultDigest(value = '') {
  const digest = String(value || '').trim();

  if (!digest) {
    return 'Digest recorded';
  }

  return `${digest.slice(0, 10)}…${digest.slice(-6)}`;
}


/**
 * @function buildVaultComplianceSeals
 * @description Builds customer-facing compliance and governance seals from the selected Vault entry state.
 * @param {object} entry Selected Vault entry.
 * @returns {Array<object>} Compliance seal models.
 * @collaboration Knowledge Base VaultE Compliance Seals, Founder Access, verification posture, and customer-facing Vault governance.
 */
function buildVaultComplianceSeals(entry = {}) {
  const proofMatched = String(entry?.proofStatus || '').toUpperCase().includes('MATCH');
  const locked = String(entry?.lockStatus || '').toUpperCase().includes('LOCK') || String(entry?.lockStatus || '').toUpperCase().includes('VERIFIED');
  const founderAccess = String(entry?.permissionMode || '').toUpperCase().includes('FOUNDER');
  const savedDocument = Boolean(entry?.pdfPresent);
  const evidenceRecord = Boolean(entry?.proofPresent);
  const jsonCompanion = Boolean(entry?.jsonPresent);

  return [
    {
      label: 'Founder seal',
      value: founderAccess ? 'Cleared' : 'Permissioned',
      tone: founderAccess ? 'gold' : 'blue',
    },
    {
      label: 'Document lock',
      value: locked ? 'Locked' : 'Controlled',
      tone: locked ? 'gold' : 'blue',
    },
    {
      label: 'Verification',
      value: proofMatched ? 'Aligned' : 'Review needed',
      tone: proofMatched ? 'gold' : 'risk',
    },
    {
      label: 'Evidence set',
      value: savedDocument && evidenceRecord && jsonCompanion ? 'Complete' : 'Review',
      tone: savedDocument && evidenceRecord && jsonCompanion ? 'gold' : 'risk',
    },
    {
      label: 'JSON companion',
      value: displayVaultJsonStatus(entry),
      tone: jsonCompanion ? 'gold' : 'blue',
    },
  ];
}

/**
 * @function buildVaultProofTrail
 * @description Builds a collapsible proof trail from visible Vault proof state without exposing raw backend enum language.
 * @param {object} entry Selected Vault entry.
 * @param {object|null} receipt Latest UI action receipt.
 * @returns {Array<object>} Proof trail events.
 * @collaboration Knowledge Base VaultE collapsible proof trail, evidence anchors, action receipts, and saved artifact governance.
 */
function buildVaultProofTrail(entry = {}, receipt = null) {
  return [
    {
      step: '01',
      label: 'Library record',
      value: 'Knowledge Base Manifest',
      status: 'Recorded',
    },
    {
      step: '02',
      label: 'Saved document',
      value: entry?.pdfPresent ? 'Available' : 'Missing',
      status: entry?.pdfPresent ? 'Ready' : 'Review',
    },
    {
      step: '03',
      label: 'Verification record',
      value: entry?.proofPresent ? 'Available' : 'Missing',
      status: entry?.proofPresent ? 'Ready' : 'Review',
    },
    {
      step: '04',
      label: 'Integrity check',
      value: displayVaultProofStatus(entry?.proofStatus),
      status: String(entry?.proofStatus || '').toUpperCase().includes('MATCH') ? 'Verified' : 'Review',
    },
    {
      step: '05',
      label: 'Latest operator action',
      value: receipt?.action ? toVaultTitleCase(receipt.action) : 'Awaiting action',
      status: receipt?.action ? 'Recorded' : 'Idle',
    },
  ];
}

/**
 * @function buildVaultEvidenceAnchors
 * @description Builds customer-facing evidence anchors for the selected Vault artifact.
 * @param {object} entry Selected Vault entry.
 * @returns {Array<object>} Evidence anchor models.
 * @collaboration Knowledge Base VaultE evidence anchors, proof inspector, copy controls, and no raw source path display.
 */
function buildVaultEvidenceAnchors(entry = {}) {
  return [
    {
      label: 'Library anchor',
      value: 'Manifest record',
      detail: 'Permanent Knowledge Base listing.',
    },
    {
      label: 'Document anchor',
      value: entry?.pdfPresent ? 'Saved document present' : 'Document pending',
      detail: 'Opened only through the Vault.',
    },
    {
      label: 'Verification anchor',
      value: entry?.proofPresent ? 'Evidence record present' : 'Evidence pending',
      detail: 'Verification can be opened separately.',
    },
    {
      label: 'Fingerprint anchor',
      value: displayVaultDigest(entry?.pdfSha3),
      detail: 'Copy the full fingerprint from inspector controls.',
    },
  ];
}

/**
 * @function buildVaultIntelligenceSignals
 * @description Builds dynamic Vault intelligence signals from selected artifact proof, action, and permission state.
 * @param {object} entry Selected Vault entry.
 * @param {object|null} receipt Latest UI action receipt.
 * @returns {Array<object>} Intelligence signal cards.
 * @collaboration Knowledge Base VaultE Insight Engine, Action Planner, Audit Sentinel, Optimization Hub, Breach Response, and production Vault UX.
 */
function buildVaultIntelligenceSignals(entry = {}, receipt = null) {
  const proofMatched = String(entry?.proofStatus || '').toUpperCase().includes('MATCH');
  const ready = Boolean(entry?.pdfPresent && entry?.proofPresent && proofMatched);
  const canOpen = Boolean(entry?.allowedActions?.open);
  const canProof = Boolean(entry?.allowedActions?.proof);
  const canDownload = Boolean(entry?.allowedActions?.download);

  return [
    {
      label: 'Insight Engine',
      value: ready ? 'Recommended for trusted use' : 'Review verification first',
      detail: ready ? 'This playbook is verified and ready for operator reference.' : 'Evidence is incomplete or needs attention.',
    },
    {
      label: 'Action Planner',
      value: canOpen && canProof ? 'Review document, then open evidence' : 'Limited actions available',
      detail: canDownload ? 'Download only after review when an evidence package is needed.' : 'Use available actions shown in the operating lane.',
    },
    {
      label: 'Audit Sentinel',
      value: ready ? 'Access protected by verified evidence' : 'Source evidence requires review',
      detail: 'Every visible action stays tied to the selected document context.',
    },
    {
      label: 'Optimization Hub',
      value: receipt?.action ? 'Usage signal captured' : 'Awaiting first action',
      detail: receipt?.detail || 'Open, print, download, or inspect evidence to create the next usage signal.',
    },
    {
      label: 'Breach Response',
      value: ready ? 'No mismatch detected' : 'Mismatch review required',
      detail: ready ? 'Document and evidence record are aligned.' : 'Open the evidence record before relying on this document.',
    },
  ];
}

/**
 * @function resolveSelectedVaultEntry
 * @description Resolves the selected Vault entry while falling back to the first visible permissioned artifact.
 * @param {Array} entries Visible Vault entries.
 * @param {string} selectedEntryId Selected entry id.
 * @returns {object|null} Selected Vault entry.
 * @collaboration Knowledge Base VaultA operating lane, inline proof inspector, and search-filtered artifact selection.
 */
function resolveSelectedVaultEntry(entries = [], selectedEntryId = '') {
  if (!Array.isArray(entries) || entries.length === 0) {
    return null;
  }

  return entries.find((entry) => entry?.id === selectedEntryId) || entries[0] || null;
}


const WILSY_KNOWLEDGE_RECEIPT_CACHE_KEY = 'wilsy.knowledgeBase.vault.receiptCockpit.v1';

/**
 * @function createKnowledgeBaseReceiptCockpitEntry
 * @description Creates a contained Receipt Cockpit record from the latest UI action receipt and selected saved artifact.
 * @param {object} actionReceipt Latest action receipt.
 * @param {object} entry Selected Knowledge Base artifact.
 * @returns {object} Receipt cockpit record.
 * @collaboration Wilsy Knowledge Base Vault, saved PDF/proof routes, and future backend receipt ledger persistence.
 */
function createKnowledgeBaseReceiptCockpitEntry(actionReceipt = {}, entry = {}) {
  const generatedAt = new Date().toISOString();
  const action = String(actionReceipt.action || 'Vault action').trim();
  const artifactTitle = String(actionReceipt.artifactTitle || entry.title || 'Knowledge Base artifact').trim();
  const artifactId = String(entry.id || entry.artifactId || artifactTitle).trim();

  return {
    id: `${artifactId}-${action}-${generatedAt}`,
    artifactId,
    artifactTitle,
    action,
    detail: String(actionReceipt.detail || 'Receipt captured from this operating session.').trim(),
    at: String(actionReceipt.at || generatedAt).trim(),
    generatedAt,
    category: resolveVaultDocumentCategory(entry),
    status: displayVaultProofStatus(entry.proofStatus),
    lock: displayVaultLockStatus(entry.lockStatus),
    owner: String(entry.generatedByDisplayName || 'Owner recorded').trim(),
    fingerprint: String(entry.pdfSha3 || '').trim(),
    sourceTag: String(entry.sourceTag || '').trim(),
    sourceCommit: String(entry.sourceCommit || '').trim(),
    routes: {
      pdfOpenUrl: entry.routes?.pdfOpenUrl || entry.pdfOpenUrl || '',
      pdfDownloadUrl: entry.routes?.pdfDownloadUrl || entry.pdfDownloadUrl || '',
      jsonUrl: entry.routes?.jsonUrl || entry.jsonUrl || '',
      jsonDownloadUrl: entry.routes?.jsonDownloadUrl || entry.jsonDownloadUrl || '',
      proofUrl: entry.routes?.proofUrl || entry.proofUrl || '',
    },
  };
}

/**
 * @function readKnowledgeBaseReceiptCockpitCache
 * @description Reads the temporary local Receipt Cockpit cache until the backend receipt ledger is added.
 * @returns {Array<object>} Cached receipt cockpit records.
 * @collaboration Wilsy Knowledge Base Vault, operator continuity, and future server-persisted receipts.
 */
function readKnowledgeBaseReceiptCockpitCache() {
  if (typeof window === 'undefined') return [];

  try {
    const payload = window.localStorage.getItem(WILSY_KNOWLEDGE_RECEIPT_CACHE_KEY);
    const parsed = JSON.parse(payload || '[]');
    return Array.isArray(parsed) ? parsed.slice(0, 18) : [];
  } catch {
    return [];
  }
}

/**
 * @function persistKnowledgeBaseReceiptCockpitCache
 * @description Persists a bounded local Receipt Cockpit cache without claiming backend receipt persistence.
 * @param {Array<object>} receipts Receipt cockpit records.
 * @returns {Array<object>} Bounded receipt cockpit records.
 * @collaboration Wilsy Knowledge Base Vault, local continuity cache, and backend receipt ledger follow-up.
 */
function persistKnowledgeBaseReceiptCockpitCache(receipts = []) {
  const bounded = Array.isArray(receipts) ? receipts.slice(0, 18) : [];

  if (typeof window !== 'undefined') {
    try {
      window.localStorage.setItem(WILSY_KNOWLEDGE_RECEIPT_CACHE_KEY, JSON.stringify(bounded));
    } catch {
      // Local cache is a convenience only; saved PDF/proof routes remain the source of truth.
    }
  }

  return bounded;
}

/**
 * @function mergeKnowledgeBaseReceiptCockpitEntry
 * @description Prepends a new receipt while avoiding repeated identical action bursts.
 * @param {Array<object>} receipts Existing receipt cockpit records.
 * @param {object} receipt New receipt cockpit record.
 * @returns {Array<object>} Bounded merged receipt cockpit records.
 * @collaboration Wilsy Knowledge Base Vault, action receipts, and contained receipt cockpit.
 */
function mergeKnowledgeBaseReceiptCockpitEntry(receipts = [], receipt = {}) {
  if (!receipt.id) return Array.isArray(receipts) ? receipts.slice(0, 18) : [];

  const signature = `${receipt.artifactId}-${receipt.action}-${receipt.detail}`;
  const filtered = (Array.isArray(receipts) ? receipts : []).filter((item) => {
    const itemSignature = `${item.artifactId}-${item.action}-${item.detail}`;
    return itemSignature !== signature;
  });

  return [receipt, ...filtered].slice(0, 18);
}

/**
 * @function compactKnowledgeBaseReceiptFingerprint
 * @description Produces a short readable fingerprint for the Receipt Cockpit.
 * @param {string} value Fingerprint value.
 * @returns {string} Compact fingerprint.
 * @collaboration Wilsy Knowledge Base Vault, evidence controls, and receipt cockpit proof display.
 */
function compactKnowledgeBaseReceiptFingerprint(value = '') {
  const clean = String(value || '').trim();
  if (!clean) return 'Fingerprint pending';
  if (clean.length <= 20) return clean;
  return `${clean.slice(0, 10)}…${clean.slice(-8)}`;
}

/**
 * @function buildVaultActionReceipt
 * @description Builds a visible non-persisted UI receipt after a Vault action completes.
 * @param {string} action Action code.
 * @param {object} entry Vault entry.
 * @param {string} detail Operator-readable detail.
 * @returns {object} UI action receipt.
 * @collaboration Knowledge Base VaultA saved document actions, proof verification record actions, and visible operator feedback.
 */
function buildVaultActionReceipt(action = '', entry = {}, detail = '') {
  return {
    id: `VAULT-RECEIPT-${Date.now()}`,
    action: String(action || 'VAULT_ACTION_RECORDED').toUpperCase(),
    artifactId: entry?.id || 'UNKNOWN_ARTIFACT',
    artifactTitle: entry?.title || 'Knowledge Base artifact',
    detail: detail || 'Action completed against saved Knowledge Base artifact.',
    at: new Date().toISOString(),
  };
}

/**
 * @function copyVaultClipboardText
 * @description Copies Vault proof evidence to the clipboard without browser prompts.
 * @param {string} value Value to copy.
 * @param {string} label Evidence label.
 * @returns {Promise<object>} UI action receipt.
 * @collaboration Knowledge Base VaultA copy controls, fingerprint evidence handling, source tag review, and proof inspector productivity.
 */
async function copyVaultClipboardText(value = '', label = 'Evidence') {
  const text = String(value || '').trim();

  if (!text) {
    return buildVaultActionReceipt('COPY_SKIPPED', { title: label }, 'No value was available to copy.');
  }

  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
  } else if (typeof document !== 'undefined') {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', 'readonly');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';

    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    textarea.remove();
  }

  return buildVaultActionReceipt(`${label}_COPIED`, { title: label }, `${label} copied to clipboard.`);
}

/**
 * @function openVaultProofJson
 * @description Opens the saved proof verification record JSON through the Vault read-only proof route.
 * @param {object} entry Vault entry.
 * @returns {Promise<object>} Proof verification record payload and object URL.
 * @collaboration Knowledge Base VaultA proof JSON action, saved verification record route, and no-regeneration Knowledge Base contract.
 */
async function openVaultProofJson(entry = {}) {
  const proofUrl = entry.routes?.proofUrl;

  if (!proofUrl) {
    throw new Error('KNOWLEDGE_BASE_VAULT_PROOF_URL_MISSING');
  }

  const payload = await fetchVaultJson(proofUrl, 'knowledge_base_vault_open_proof');
  const objectUrl = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));

  window.open(objectUrl, '_blank', 'noopener,noreferrer');

  return {
    payload,
    objectUrl,
  };
}

/**
 * @function openVaultPlaybookJson
 * @description Opens the saved machine-readable playbook JSON companion through the Vault read-only JSON route.
 * @param {object} entry Vault entry.
 * @returns {Promise<object>} JSON companion object URL.
 * @collaboration Knowledge Base Vault FG109 JSON action, manifest jsonPath, and future AI retrieval/playbook automation.
 */
async function openVaultPlaybookJson(entry = {}) {
  const jsonUrl = entry.routes?.jsonUrl;

  if (!jsonUrl) {
    throw new Error('KNOWLEDGE_BASE_VAULT_JSON_URL_MISSING');
  }

  const blob = await fetchVaultBlob(jsonUrl, 'knowledge_base_vault_open_json', 'application/json');
  const objectUrl = URL.createObjectURL(blob);
  const openedWindow = window.open(objectUrl, '_blank', 'noopener,noreferrer');

  if (!openedWindow) {
    throw new Error('KNOWLEDGE_BASE_VAULT_JSON_POPUP_BLOCKED');
  }

  return {
    objectUrl,
  };
}

/**
 * @function downloadVaultPlaybookJson
 * @description Downloads the saved machine-readable playbook JSON companion through the Vault route.
 * @param {object} entry Vault entry.
 * @returns {Promise<void>} Resolves when browser download is triggered.
 * @collaboration Knowledge Base Vault JSON companion download, manifest-backed saved artifacts, and no-regeneration route contract.
 */
async function downloadVaultPlaybookJson(entry = {}) {
  const jsonUrl = entry.routes?.jsonDownloadUrl || entry.routes?.jsonUrl;
  if (!jsonUrl) return;

  const blob = await fetchVaultBlob(jsonUrl, 'knowledge_base_vault_download_json', 'application/json');
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = objectUrl;
  link.download = `${entry.id || 'knowledge-base-artifact'}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}


/**
 * @function resolveVaultDocumentCategory
 * @description Dynamically categorizes a Vault document from its metadata without hard-coded document ids.
 * @param {object} entry Vault entry.
 * @returns {string} Dynamic document category.
 * @collaboration Knowledge Base VaultF scalable Knowledge Base, manifest-backed document classification, and multi-document productivity.
 */
function resolveVaultDocumentCategory(entry = {}) {
  const source = [
    entry?.artifactType,
    entry?.title,
    entry?.sourcePosture,
    entry?.permissionMode,
  ].join(' ').toLowerCase();

  if (source.includes('playbook')) return 'Playbooks';
  if (source.includes('policy')) return 'Policies';
  if (source.includes('training')) return 'Training';
  if (source.includes('manual')) return 'Manuals';
  if (source.includes('guide')) return 'Guides';
  if (source.includes('contract')) return 'Contracts';
  if (source.includes('evidence')) return 'Evidence';
  if (source.includes('report')) return 'Reports';

  return 'Documents';
}

/**
 * @function resolveVaultDocumentVerificationLabel
 * @description Resolves a customer-facing verification label for a Vault document.
 * @param {object} entry Vault entry.
 * @returns {string} Verification label.
 * @collaboration Knowledge Base VaultF document list status, proof posture, and customer-facing verification display.
 */
function resolveVaultDocumentVerificationLabel(entry = {}) {
  const proof = String(entry?.proofStatus || '').toUpperCase();

  if (proof.includes('MATCH')) return 'Verified';
  if (proof.includes('MISSING')) return 'Evidence missing';
  if (proof.includes('FAILED')) return 'Needs review';

  return 'Review ready';
}

/**
 * @function resolveVaultCategoryFilters
 * @description Builds category filters dynamically from the current Vault entries.
 * @param {Array} entries Vault entries.
 * @returns {Array<object>} Category filters.
 * @collaboration Knowledge Base VaultF scalable document navigation, manifest-backed category discovery, and SaaS productivity.
 */
function resolveVaultCategoryFilters(entries = []) {
  const counts = new Map();

  entries.forEach((entry) => {
    const category = resolveVaultDocumentCategory(entry);
    counts.set(category, (counts.get(category) || 0) + 1);
  });

  return [
    { key: 'all', label: 'All', count: entries.length },
    ...Array.from(counts.entries())
      .sort((first, second) => first[0].localeCompare(second[0]))
      .map(([label, count]) => ({
        key: label,
        label,
        count,
      })),
  ];
}

/**
 * @function resolveVaultWorkspaceEntries
 * @description Filters Vault entries by query and active dynamic category.
 * @param {Array} entries Vault entries.
 * @param {string} query Search query.
 * @param {string} activeCategory Active category key.
 * @returns {Array} Filtered entries.
 * @collaboration Knowledge Base VaultF scalable document search, dynamic categories, and selected-document workflow.
 */
function resolveVaultWorkspaceEntries(entries = [], query = '', activeCategory = 'all') {
  const filteredByQuery = resolveFilteredVaultEntries(entries, query);

  if (!activeCategory || activeCategory === 'all') {
    return filteredByQuery;
  }

  return filteredByQuery.filter((entry) => resolveVaultDocumentCategory(entry) === activeCategory);
}

/**
 * @function resolveVaultDocumentTaskQueue
 * @description Builds a selected-document task queue from available actions and verification state.
 * @param {object} entry Selected Vault entry.
 * @returns {Array<object>} Task queue rows.
 * @collaboration Knowledge Base VaultF task completion workflow, selected document actions, and productivity-first Vault operation.
 */
function resolveVaultDocumentTaskQueue(entry = {}) {
  const tasks = [];

  if (entry?.allowedActions?.open) {
    tasks.push({
      key: 'open',
      label: 'Open document',
      detail: 'Review the saved document inside the controlled workspace viewer.',
    });
  }

  if (entry?.allowedActions?.proof) {
    tasks.push({
      key: 'evidence',
      label: 'Open evidence record',
      detail: 'Inspect the verification record for this document.',
    });
  }

  if (entry?.allowedActions?.download) {
    tasks.push({
      key: 'download',
      label: 'Download document',
      detail: 'Save the verified document for approved use.',
    });
  }

  tasks.push({
    key: 'copy',
    label: 'Copy evidence',
    detail: 'Copy fingerprint or release evidence when proof is needed.',
  });

  return tasks;
}

/**
 * @function resolveVaultDocumentSummary
 * @description Builds compact summary fields for the selected document workspace.
 * @param {object} entry Selected Vault entry.
 * @returns {Array<object>} Summary fields.
 * @collaboration Knowledge Base VaultF selected document productivity, copy-only evidence, and customer-facing proof language.
 */
function resolveVaultDocumentSummary(entry = {}) {
  return [
    {
      label: 'Category',
      value: resolveVaultDocumentCategory(entry),
    },
    {
      label: 'Status',
      value: resolveVaultDocumentVerificationLabel(entry),
    },
    {
      label: 'Owner',
      value: entry?.generatedByDisplayName || 'Recorded owner',
    },
    {
      label: 'Release',
      value: displayVaultSourceTag(entry?.sourceTag || entry?.sourceCommit),
    },
    {
      label: 'Access',
      value: displayVaultPermissionMode(entry?.permissionMode),
    },
    {
      label: 'Fingerprint',
      value: displayVaultDigest(entry?.pdfSha3),
    },
  ];
}

/**
 * @function resolveKnowledgeOperatingBarSuggestions
 * @description Converts filtered Vault entries and Wilsy AI dynamic prompts into executable instant suggestion rows for the consolidated Knowledge Operating Bar.
 * @param {Array<object>} entries Filtered Vault entries.
 * @param {object|null} selectedEntry Selected Vault entry.
 * @param {Function} onSelectEntry Artifact selection handler.
 * @param {Array<object>} dynamicSuggestions Wilsy AI dynamic suggestion rows.
 * @param {Function} onSelectSuggestion Wilsy AI prompt selection handler.
 * @returns {Array<object>} Display-ready suggestion rows.
 * @collaboration KnowledgeOperatingBar, WilsyKnowledgeBaseVault search state, dynamic Vault entries, Wilsy AI dynamic suggestion engine, and customer-safe proof status display.
 */
function resolveKnowledgeOperatingBarSuggestions(
  entries = [],
  selectedEntry = null,
  onSelectEntry = () => undefined,
  dynamicSuggestions = [],
  onSelectSuggestion = () => undefined,
) {
  const documentRows = entries.slice(0, 3).map((entry, index) => ({
    key: entry?.id || entry?.title || entry?.pdfSha3 || `knowledge-suggestion-${index}`,
    title: entry?.title || 'Verified artifact',
    detail: `${resolveVaultDocumentVerificationLabel(entry)} | ${entry?.generatedByDisplayName || 'Owner recorded'}`,
    selected: selectedEntry?.id === entry?.id,
    onSelect: () => onSelectEntry(entry?.id || ''),
  }));
  const aiRows = dynamicSuggestions.slice(0, 3).map((suggestion, index) => ({
    key: suggestion?.id || suggestion?.stableId || `knowledge-ai-suggestion-${index}`,
    title: suggestion?.label || 'Ask Wilsy AI',
    detail: suggestion?.intent ? toVaultTitleCase(suggestion.intent) : 'Dynamic workspace suggestion',
    selected: false,
    onSelect: () => onSelectSuggestion(suggestion),
  }));

  return [...documentRows, ...aiRows].slice(0, 6);
}

/**
 * @function resolveKnowledgeVaultAIResponse
 * @description Builds the live Wilsy AI written response from the current verified Vault query, selected artifact, load state, and workspace category.
 * @param {object} payload Live Vault response payload.
 * @returns {string} Customer-facing Wilsy AI written response.
 * @collaboration WilsyKnowledgeBaseVault live search, KnowledgeOperatingBar query state, dynamic suggestions, selected artifact controls, and no-regeneration Vault contract.
 */
function resolveKnowledgeVaultAIResponse(payload = {}) {
  const query = String(payload.query || '').trim();
  const entries = Array.isArray(payload.entries) ? payload.entries : [];
  const selectedEntry = payload.selectedEntry || null;
  const category = payload.activeCategory && payload.activeCategory !== 'all' ? payload.activeCategory : 'all saved knowledge';

  if (payload.loading) {
    return 'Wilsy AI: I am verifying the saved Knowledge Base before answering, keeping the workspace usable while the Vault confirms the latest artifact list.';
  }

  if (payload.error && entries.length > 0) {
    const fallbackTitle = selectedEntry?.title || entries[0]?.title || 'the cached verified artifact';
    return `Wilsy AI: The live Vault is restoring, but I can still work from the last verified library state. Start with ${fallbackTitle}; it remains controlled by saved-document access until the Vault refresh completes.`;
  }

  if (query && entries.length > 0) {
    const leadEntry = selectedEntry || entries[0];
    const owner = leadEntry?.generatedByDisplayName || 'the recorded owner';
    const posture = resolveVaultDocumentVerificationLabel(leadEntry).toLowerCase();
    return `Wilsy AI: I found ${entries.length} verified artifact${entries.length === 1 ? '' : 's'} for "${query}" in ${category}. Start with ${leadEntry?.title || 'the selected artifact'} because it is ${posture} and owned by ${owner}. Open it in the workspace viewer, inspect evidence, download, print, or copy the fingerprint without regenerating the document.`;
  }

  if (query) {
    return `Wilsy AI: I cannot verify a saved artifact for "${query}" yet. Try a title, owner, release label, category, or fingerprint; I will only answer from artifacts the Knowledge Base can prove.`;
  }

  if (selectedEntry) {
    return `Wilsy AI: ${selectedEntry.title} is selected. It is ${resolveVaultDocumentVerificationLabel(selectedEntry).toLowerCase()} and ${displayVaultLockStatus(selectedEntry.lockStatus).toLowerCase()}; use the workspace controls to view, prove, print, download, or copy evidence on demand.`;
  }

  return 'Wilsy AI: Select a verified artifact or start typing. I will search the saved Knowledge Base live and return an answer only from proven workspace knowledge.';
}

/**
 * @function resolveKnowledgeVaultAIBriefs
 * @description Builds context-aware Knowledge Base suggestion briefs from the selected artifact, live task queue, summary facts, and Wilsy AI dynamic prompts.
 * @param {object} payload Selected artifact, summary, task, suggestion, and search state.
 * @returns {Array<object>} Four source-aware Wilsy AI brief rows.
 * @collaboration Knowledge Base Vault dynamic guidance, selected artifact source posture, Wilsy AI suggestions, and no hard-coded unrelated teaching copy.
 */
function resolveKnowledgeVaultAIBriefs(payload = {}) {
  const entry = payload.selectedEntry || {};
  const selectedSummary = Array.isArray(payload.selectedSummary) ? payload.selectedSummary : [];
  const selectedTasks = Array.isArray(payload.selectedTasks) ? payload.selectedTasks : [];
  const dynamicSuggestions = Array.isArray(payload.dynamicSuggestions) ? payload.dynamicSuggestions : [];
  const firstSuggestion = dynamicSuggestions[0] || null;
  const firstTask = selectedTasks[0] || null;
  const owner = normalizeVaultText(entry.generatedByDisplayName, 'Recorded owner');
  const category = entry?.id ? resolveVaultDocumentCategory(entry) : normalizeVaultText(payload.activeCategory, 'Knowledge Base');
  const proofSummary = selectedSummary
    .slice(0, 3)
    .map((item) => `${item.label}: ${item.value}`)
    .join(' | ');

  return [
    {
      label: 'Selected knowledge',
      title: entry?.title || normalizeVaultText(payload.query, 'Awaiting verified Knowledge Base content'),
      detail: entry?.id
        ? `${resolveVaultDocumentVerificationLabel(entry)} | ${displayVaultLockStatus(entry.lockStatus)} | ${owner}`
        : 'Start a search or choose a saved artifact before Wilsy AI recommends source-bound content.',
    },
    {
      label: 'Suggested question',
      title: firstSuggestion?.label || 'Ask from the selected Knowledge Base artifact',
      detail: firstSuggestion?.prompt || 'Wilsy AI will suggest prompts from the current document, source posture, evidence, and active category.',
    },
    {
      label: 'Evidence posture',
      title: entry?.id ? displayVaultDigest(entry.pdfSha3) : 'Evidence waits for selection',
      detail: proofSummary || 'Proof, owner, access, release, and fingerprint facts appear when the Vault has a selected source.',
    },
    {
      label: 'Next safe action',
      title: firstTask?.label || `Review ${category}`,
      detail: firstTask?.detail || 'Choose a verified source first; Wilsy AI will route open, proof, print, download, or copy actions from that source only.',
    },
  ];
}

/**
 * @function WilsyKnowledgeBaseVault
 * @description Renders the global Knowledge Base Vault as a scalable document operating workspace with dynamic categories, selected-document tasks, and contained work areas.
 * @returns {JSX.Element} Knowledge Base Vault workspace.
 * @collaboration Knowledge Base VaultF multi-document Knowledge Base, productivity-first document operations, proof evidence, and runtime-passed request sealing.
 */
export default function WilsyKnowledgeBaseVault() {
  const [knowledgeBaseOrigin, setKnowledgeBaseOrigin] = useState(null);

  useEffect(() => {
    setKnowledgeBaseOrigin(resolveStoredKnowledgeBaseOrigin());
  }, []);

  /**
   * @function resolveKnowledgeBaseOriginLabel
   * @description Resolves a human-safe return label for the Knowledge Base operating corridor.
   * @returns {string} Return command label.
   * @collaboration FG108O4B Knowledge Base Operating Room, Command K origin packet, CRM workspace, and global operating fallback.
   */
  const resolveKnowledgeBaseOriginLabel = () => {
    return `Return to ${resolveKnowledgeBaseWorkspaceLabel(knowledgeBaseOrigin || {})}`;
  };

  /**
   * @function handleKnowledgeBaseOriginReturn
   * @description Sends the operator back to the workspace that opened the Knowledge Base, with a CRM fallback.
   * @returns {void}
   * @collaboration FG108O4B Knowledge Base Operating Room, Command K origin packet, BrowserRouter, and workspace continuity.
   */
  const handleKnowledgeBaseOriginReturn = () => {
    const route = normalizeKnowledgeBaseRoutePath(knowledgeBaseOrigin?.route || '/') || '/';

    window.history.pushState({}, '', route);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const knowledgeBaseOriginLabel = resolveKnowledgeBaseOriginLabel();

  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [searchNonce, setSearchNonce] = useState(0);
  const [selectedEntryId, setSelectedEntryId] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [actionReceipt, setActionReceipt] = useState(null);
  const [receiptCockpitOpen, setReceiptCockpitOpen] = useState(false);
  const [receiptCockpitEntries, setReceiptCockpitEntries] = useState(() => readKnowledgeBaseReceiptCockpitCache());
  const [documentNavigatorOpen, setDocumentNavigatorOpen] = useState(true);
  const [knowledgeInsightsOpen, setKnowledgeInsightsOpen] = useState(true);
  const [pdfPreview, setPdfPreview] = useState(null);
  const [vaultErrorVisible, setVaultErrorVisible] = useState(false);
  const backendFilters = useMemo(() => ({
    query: submittedQuery,
    category: activeCategory,
    searchNonce,
  }), [submittedQuery, activeCategory, searchNonce]);
  const { loading, error, vault, reload } = useKnowledgeBaseVaultData(backendFilters);

  const entries = vault?.entries || [];
  const categoryFilters = useMemo(
    () => vault?.facets?.categories || resolveVaultCategoryFilters(entries),
    [vault?.facets, entries]
  );
  const filteredEntries = useMemo(
    () => resolveVaultWorkspaceEntries(entries, submittedQuery, activeCategory),
    [entries, submittedQuery, activeCategory]
  );
  const selectedEntry = useMemo(
    () => resolveSelectedVaultEntry(filteredEntries, selectedEntryId),
    [filteredEntries, selectedEntryId]
  );
  const selectedSummary = useMemo(() => resolveVaultDocumentSummary(selectedEntry || {}), [selectedEntry]);
  const selectedTasks = useMemo(() => resolveVaultDocumentTaskQueue(selectedEntry || {}), [selectedEntry]);
  const dynamicOperatingSuggestions = useMemo(() => buildWilsyDynamicSuggestions({
    promptText: query || submittedQuery,
    model: {
      workspace: 'Knowledge Base',
      commandTokens: selectedTasks.map((task) => ({
        label: task.label,
        intent: task.key,
      })),
      sourceTrace: selectedSummary.map((item) => ({
        label: item.label,
        statusLabel: item.value,
      })),
      evidenceAnchors: selectedEntry
        ? [
            {
              label: 'Selected fingerprint',
              statusLabel: displayVaultDigest(selectedEntry.pdfSha3),
            },
          ]
        : [],
    },
    context: {
      workspace: 'Knowledge Base',
      focus: selectedEntry?.title || 'Saved knowledge',
    },
    refreshKey: searchNonce,
    storage: typeof window !== 'undefined' ? window.localStorage : null,
  }), [query, submittedQuery, searchNonce, selectedEntry, selectedSummary, selectedTasks]);
  const operatingBarSuggestions = useMemo(
    () => resolveKnowledgeOperatingBarSuggestions(
      filteredEntries,
      selectedEntry,
      setSelectedEntryId,
      dynamicOperatingSuggestions,
      handleKnowledgeSuggestionSelect,
    ),
    [dynamicOperatingSuggestions, filteredEntries, selectedEntry]
  );
  const knowledgeVaultAIResponse = useMemo(() => resolveKnowledgeVaultAIResponse({
    query: submittedQuery,
    entries: filteredEntries,
    selectedEntry,
    activeCategory,
    loading,
    error,
  }), [activeCategory, error, filteredEntries, loading, selectedEntry, submittedQuery]);
  const knowledgeVaultAIResponseBody = knowledgeVaultAIResponse.replace(/^Wilsy AI:\s*/i, '');
  const knowledgeVaultAIBriefs = useMemo(() => resolveKnowledgeVaultAIBriefs({
    selectedEntry,
    selectedSummary,
    selectedTasks,
    dynamicSuggestions: dynamicOperatingSuggestions,
    query: submittedQuery || query,
    activeCategory,
  }), [activeCategory, dynamicOperatingSuggestions, query, selectedEntry, selectedSummary, selectedTasks, submittedQuery]);

  /**
   * @function handleKnowledgeOperatingSearchSubmit
   * @description Commits the current Knowledge Base search draft into the backend-backed Vault filters and resets the draft command field.
   * @returns {void}
   * @collaboration KnowledgeOperatingBar search controls, WilsyKnowledgeBaseVault backendFilters, useKnowledgeBaseVaultData, and dynamic suggestion continuity.
   */
  function handleKnowledgeOperatingSearchSubmit() {
    setSubmittedQuery(query.trim());
    setQuery('');
    setSearchNonce((current) => current + 1);
  }

  /**
   * @function handleKnowledgeOperatingClearSearch
   * @description Clears both draft and submitted Knowledge Base searches so the operating bar clear button is executable.
   * @returns {void}
   * @collaboration KnowledgeOperatingBar clear command, backendFilters state, and selected artifact continuity.
   */
  function handleKnowledgeOperatingClearSearch() {
    setQuery('');
    setSubmittedQuery('');
    setSearchNonce((current) => current + 1);
  }

  /**
   * @function handleKnowledgeSuggestionSelect
   * @description Executes a dynamic Knowledge Base suggestion by turning its prompt into the next verified search.
   * @param {object} suggestion Suggestion row.
   * @returns {void}
   * @collaboration KnowledgeOperatingBar live suggestions, Wilsy AI dynamic suggestions, and backend-backed Vault filtering.
   */
  function handleKnowledgeSuggestionSelect(suggestion = {}) {
    const prompt = String(suggestion.prompt || suggestion.label || '').trim();
    if (!prompt) return;

    setQuery('');
    setSubmittedQuery(prompt);
    setSearchNonce((current) => current + 1);
  }

  /**
   * @function handleVaultActionCommand
   * @description Runs a Vault action and converts success or failure into a visible receipt instead of a silent console error.
   * @param {string} action Receipt action label.
   * @param {object} entry Selected Vault entry.
   * @param {string} successDetail Success receipt detail.
   * @param {Function} command Action command.
   * @returns {void}
   * @collaboration Knowledge Base action buttons, receipt cockpit feedback, and saved artifact route reliability.
   */
  function handleVaultActionCommand(action = 'Vault action', entry = selectedEntry, successDetail = '', command = async () => undefined) {
    void (async () => {
      try {
        await command();
        setActionReceipt(buildVaultActionReceipt(action, entry, successDetail));
      } catch (error) {
        const message = error?.message || String(error || 'Browser action failed');
        setActionReceipt(buildVaultActionReceipt(
          `${action} failed`,
          entry,
          `${toVaultTitleCase(action)} could not complete: ${message}.`,
        ));
      }
    })();
  }

  /**
   * @function handleVaultPreviewCommand
   * @description Opens a saved Knowledge Base PDF inside the controlled workspace viewer instead of a detached browser tab.
   * @param {object} entry Selected Vault entry.
   * @param {string} successDetail Visible receipt detail.
   * @returns {void}
   * @collaboration Knowledge Base in-app PDF preview, no-popup open command, object URL cleanup, and operator-contained document review.
   */
  function handleVaultPreviewCommand(entry = selectedEntry, successDetail = 'Saved document opened inside the Knowledge Base workspace.') {
    void (async () => {
      try {
        const preview = await createVaultPdfPreview(entry);
        setPdfPreview(preview);
        setActionReceipt(buildVaultActionReceipt('Document opened', entry, successDetail));
      } catch (error) {
        const message = error?.message || String(error || 'Document preview failed');
        setActionReceipt(buildVaultActionReceipt(
          'Document preview failed',
          entry,
          `Document preview could not complete: ${message}.`,
        ));
      }
    })();
  }

  /**
   * @function closeVaultPdfPreview
   * @description Closes the in-workspace PDF preview and lets the object URL cleanup effect revoke the browser URL.
   * @returns {void}
   * @collaboration Knowledge Base viewer hide control, PDF object URL lifecycle, and contained document review.
   */
  function closeVaultPdfPreview() {
    setPdfPreview(null);
  }

  /**
   * @function handleVaultCopyCommand
   * @description Copies a Vault evidence value and surfaces the resulting receipt.
   * @param {string} value Evidence value.
   * @param {string} label Evidence label.
   * @returns {void}
   * @collaboration Knowledge Base copy buttons, clipboard fallback, and receipt cockpit feedback.
   */
  function handleVaultCopyCommand(value = '', label = 'Evidence') {
    void copyVaultClipboardText(value, label)
      .then(setActionReceipt)
      .catch((error) => {
        const message = error?.message || String(error || 'Clipboard copy failed');
        setActionReceipt(buildVaultActionReceipt(
          `${label} copy failed`,
          selectedEntry || { title: label },
          `${label} could not be copied: ${message}.`,
        ));
      });
  }

  useEffect(() => {
    if (!filteredEntries.length) {
      setSelectedEntryId('');
      return;
    }

    if (!filteredEntries.some((entry) => entry?.id === selectedEntryId)) {
      setSelectedEntryId(filteredEntries[0]?.id || '');
    }
  }, [filteredEntries, selectedEntryId]);

  useEffect(() => {
    if (!actionReceipt || !selectedEntry?.id) return;

    const nextReceipt = createKnowledgeBaseReceiptCockpitEntry(actionReceipt, selectedEntry);
    setReceiptCockpitOpen(true);
    setReceiptCockpitEntries((previousReceipts) => {
      const mergedReceipts = mergeKnowledgeBaseReceiptCockpitEntry(previousReceipts, nextReceipt);
      return persistKnowledgeBaseReceiptCockpitCache(mergedReceipts);
    });
  }, [actionReceipt, selectedEntry]);

  useEffect(() => {
    if (!actionReceipt) return undefined;

    const receiptTimer = window.setTimeout(() => {
      setActionReceipt(null);
    }, 6200);

    return () => window.clearTimeout(receiptTimer);
  }, [actionReceipt]);

  useEffect(() => {
    if (!error) {
      setVaultErrorVisible(false);
      return undefined;
    }

    setVaultErrorVisible(true);
    const errorTimer = window.setTimeout(() => {
      setVaultErrorVisible(false);
    }, 7200);

    return () => window.clearTimeout(errorTimer);
  }, [error]);

  useEffect(() => {
    if (!pdfPreview?.objectUrl) return undefined;

    return () => {
      URL.revokeObjectURL(pdfPreview.objectUrl);
    };
  }, [pdfPreview?.objectUrl]);

  useEffect(() => {
    if (!pdfPreview?.artifactId) return;
    if (!selectedEntry?.id || pdfPreview.artifactId !== selectedEntry.id) {
      setPdfPreview(null);
    }
  }, [pdfPreview?.artifactId, selectedEntry?.id]);

  const activeReceiptCockpitEntries = useMemo(() => {
    if (!selectedEntry?.id) return receiptCockpitEntries.slice(0, 8);

    return receiptCockpitEntries
      .filter((receipt) => String(receipt.artifactId || '') === String(selectedEntry.id || ''))
      .slice(0, 8);
  }, [receiptCockpitEntries, selectedEntry?.id]);

  const latestReceiptCockpitEntry = activeReceiptCockpitEntries[0] || (
    actionReceipt && selectedEntry
      ? createKnowledgeBaseReceiptCockpitEntry(actionReceipt, selectedEntry)
      : null
  );


  /**
   * @function handleKnowledgeBaseExit
   * @description Returns the operator from the Knowledge Base Vault to the previous workspace using browser history with a safe root fallback.
   * @returns {void}
   * @collaboration Wilsy Knowledge Base Vault, Command K route entry, and dynamic workspace return flow.
   */
  function handleKnowledgeBaseExit() {
    if (typeof window === 'undefined') return;

    if (window.history.length > 1) {
      window.history.back();
      return;
    }

    window.location.assign('/');
  }

  const receiptCockpitVisible = Boolean(receiptCockpitOpen && latestReceiptCockpitEntry);
  const vaultWorkspaceClassName = [
    styles.vaultWorkspace,
    receiptCockpitVisible ? styles.vaultWorkspaceReceiptOpen : '',
    !documentNavigatorOpen ? styles.vaultWorkspaceNavigatorClosed : '',
    !documentNavigatorOpen && receiptCockpitVisible ? styles.vaultWorkspaceNavigatorClosedReceiptOpen : '',
  ].filter(Boolean).join(' ');


  return (
    <main className={styles.vaultShell} data-wilsy-surface="global-knowledge-base-vault">
      <KnowledgeOperatingBar
        query={query}
        onQueryChange={setQuery}
        onSubmitSearch={handleKnowledgeOperatingSearchSubmit}
        onClearSearch={handleKnowledgeOperatingClearSearch}
        onRefresh={reload}
        loading={loading}
        matchesCount={filteredEntries.length}
        libraryLabel={displayVaultManifestSource(vault?.manifestSource)}
        authoritySourceLabel={displayVaultSourceMode(vault?.sourceMode)}
        authorityAccessLabel={displayVaultPermissionMode(vault?.permission?.mode)}
        originLabel={knowledgeBaseOriginLabel}
        originRoute={knowledgeBaseOrigin?.route || '/'}
        onReturn={handleKnowledgeBaseOriginReturn}
        suggestions={operatingBarSuggestions}
        selectedTitle={selectedEntry?.title || 'Awaiting artifact'}
        selectedOwner={selectedEntry?.generatedByDisplayName || 'Verified owner required'}
        trustPosture={selectedEntry ? resolveVaultDocumentVerificationLabel(selectedEntry) : 'Permissioned'}
        submittedQuery={submittedQuery}
        activeCategoryLabel={activeCategory === 'all' ? 'All categories' : activeCategory}
      />

      <section className={styles.vaultRuntimeNotices} aria-label="Vault runtime notices">
        {actionReceipt ? (
          <section className={styles.actionReceipt} aria-live="polite" aria-label="Latest Vault action receipt">
            <div>
              <span>{toVaultTitleCase(actionReceipt.action)}</span>
              <strong>{actionReceipt.artifactTitle}</strong>
              <small>{actionReceipt.detail} | {actionReceipt.at}</small>
            </div>
            <button
              type="button"
              onClick={() => setActionReceipt(null)}
              aria-label="Hide latest Vault action receipt"
            >
              <X size={14} aria-hidden="true" />
            </button>
          </section>
        ) : null}

        {loading ? (
          <section className={styles.emptyState}>Loading Knowledge Base Vault.</section>
        ) : null}

        {error && vaultErrorVisible ? (
          <section className={styles.errorState}>
            <div>
              <strong>Vault load failed</strong>
              <span>{error}</span>
            </div>
            <button
              type="button"
              onClick={() => setVaultErrorVisible(false)}
              aria-label="Hide Vault load failure"
            >
              <X size={14} aria-hidden="true" />
            </button>
          </section>
        ) : null}
      </section>

      <section className={vaultWorkspaceClassName} aria-label="Scalable Knowledge Base workspace">

        {documentNavigatorOpen ? (
        <aside className={styles.documentNavigator} aria-label="Document list and categories">
          <div className={styles.navigatorHeader}>
            <div className={styles.navigatorTitle}>
              <span><Library size={14} aria-hidden="true" /> Document Library</span>
              <strong>{entries.length} total</strong>
            </div>
            <button
              type="button"
              className={styles.navigatorToggleButton}
              onClick={() => setDocumentNavigatorOpen(false)}
              aria-label="Close document library"
              title="Close document library"
            >
              <PanelLeftClose size={16} aria-hidden="true" />
            </button>
          </div>

          <div className={styles.categoryRail} aria-label="Dynamic document categories">
            {categoryFilters.map((category) => (
              <button
                type="button"
                key={category.key}
                className={activeCategory === category.key ? styles.categoryButtonActive : styles.categoryButton}
                onClick={() => setActiveCategory(category.key)}
              >
                <span>{category.label}</span>
                <strong>{category.count}</strong>
              </button>
            ))}
          </div>

          <div className={styles.documentList} aria-label="Filtered documents">
            {!loading && !error && filteredEntries.length === 0 ? (
              <div className={styles.emptyState}>No verified Vault match for this signal. Try a title, owner, release, category, or fingerprint.</div>
            ) : null}

            {filteredEntries.map((entry) => {
              const selected = selectedEntry?.id === entry.id;

              return (
                <button
                  type="button"
                  className={selected ? styles.documentRowActive : styles.documentRow}
                  key={entry.id}
                  onClick={() => setSelectedEntryId(entry.id)}
                >
                  <span>{resolveVaultDocumentCategory(entry)}</span>
                  <strong>{entry.title}</strong>
                  <small>{resolveVaultDocumentVerificationLabel(entry)} • {entry.generatedByDisplayName || 'Recorded owner'}</small>
                </button>
              );
            })}
          </div>
        </aside>
        ) : null}

        <section className={styles.documentWorkbench} aria-label="Selected document workspace">
          {!documentNavigatorOpen ? (
            <button
              type="button"
              className={styles.libraryRailOpenButton}
              onClick={() => setDocumentNavigatorOpen(true)}
              aria-label="Open document library"
            >
              <PanelLeftOpen size={16} aria-hidden="true" />
              <span>Open library</span>
              <strong>{filteredEntries.length} match{filteredEntries.length === 1 ? '' : 'es'}</strong>
            </button>
          ) : null}

          {selectedEntry ? (
            <>
              <div className={styles.workbenchHeader}>
                <div>
                  <span>{resolveVaultDocumentCategory(selectedEntry)}</span>
                    <h2>{displayVaultArtifactType(selectedEntry.artifactType)}</h2>
                    <p className={styles.selectedDocumentTitle}>{selectedEntry.title}</p>
                  <p>
                    {resolveVaultDocumentVerificationLabel(selectedEntry)} | {displayVaultLockStatus(selectedEntry.lockStatus)} | {selectedEntry.generatedByDisplayName || 'Recorded owner'}
                  </p>
                </div>

                <div className={styles.workbenchStatus}>
                  <span>{resolveVaultDocumentVerificationLabel(selectedEntry)}</span>
                  <strong>{displayVaultLockStatus(selectedEntry.lockStatus)}</strong>
                </div>
              </div>

                <section className={styles.naturalOperatorSurface} aria-label="Wilsy AI natural Vault response">
                  <header className={styles.operatorSurfaceHeader}>
                    <p>
                      <strong>Wilsy AI:</strong> {knowledgeVaultAIResponseBody}
                    </p>
                    <button
                      type="button"
                      onClick={() => setKnowledgeInsightsOpen((current) => !current)}
                      aria-expanded={knowledgeInsightsOpen}
                      aria-controls="wilsy-knowledge-source-brief"
                    >
                      {knowledgeInsightsOpen ? <PanelTopClose size={14} aria-hidden="true" /> : <PanelTopOpen size={14} aria-hidden="true" />}
                      <span>{knowledgeInsightsOpen ? 'Hide brief' : 'Show brief'}</span>
                    </button>
                  </header>

                {knowledgeInsightsOpen ? (
                  <section
                    className={styles.knowledgeSourceBrief}
                    aria-label="Selected artifact source intelligence"
                    id="wilsy-knowledge-source-brief"
                  >
                    {knowledgeVaultAIBriefs.map((brief) => (
                      <div tabIndex={0} key={`${brief.label}-${brief.title}`}>
                        <span>{brief.label}</span>
                        <strong>{brief.title}</strong>
                        <p>{brief.detail}</p>
                      </div>
                    ))}
                  </section>
                ) : null}

                  <div className={styles.inlineOperatorActions} aria-label="Inline Vault operator actions">
                    <button
                      type="button"
                      onClick={() => handleVaultPreviewCommand(
                        selectedEntry,
                        'Saved document opened from the natural operator response.',
                      )}
                      disabled={!selectedEntry.allowedActions?.open}
                    >
                      Open saved PDF
                    </button>
<button
  type="button"
  onClick={() => handleVaultActionCommand(
    'JSON companion opened',
    selectedEntry,
    'Machine-readable JSON companion opened from the Vault.',
    () => openVaultPlaybookJson(selectedEntry),
  )}
  disabled={!selectedEntry.allowedActions?.json}
>
  JSON Companion
</button>
                    <button
                      type="button"
                      onClick={() => handleVaultCopyCommand(selectedEntry.pdfSha3, 'Document fingerprint')}
                      disabled={!selectedEntry?.pdfSha3}
                    >
                      Copy fingerprint
                    </button>
                  </div>
                </section>

              <div className={styles.taskBar} aria-label={`Tasks for ${selectedEntry.title}`}>
                <button
                  type="button"
                  onClick={() => handleVaultPreviewCommand(
                    selectedEntry,
                    'Saved document opened from the Vault.',
                  )}
                  disabled={!selectedEntry.allowedActions?.open}
                >
                  <Eye size={15} aria-hidden="true" />
                  Open
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultActionCommand(
                    'Print prepared',
                    selectedEntry,
                    'Saved document prepared for printing.',
                    () => printVaultPdf(selectedEntry),
                  )}
                  disabled={!selectedEntry.allowedActions?.print}
                >
                  <Printer size={15} aria-hidden="true" />
                  Print
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultActionCommand(
                    'Download started',
                    selectedEntry,
                    'Saved document download started.',
                    () => downloadVaultPdf(selectedEntry),
                  )}
                  disabled={!selectedEntry.allowedActions?.download}
                >
                  <Download size={15} aria-hidden="true" />
                  Download
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultActionCommand(
                    'Evidence opened',
                    selectedEntry,
                    'Verification record opened from the Vault.',
                    () => openVaultProofJson(selectedEntry),
                  )}
                  disabled={!selectedEntry.allowedActions?.proof}
                >
                  <FileJson size={15} aria-hidden="true" />
                  Evidence
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultCopyCommand(selectedEntry.pdfSha3, 'Document fingerprint')}
                  disabled={!selectedEntry?.pdfSha3}
                >
                  Copy fingerprint
                </button>
              </div>

              {pdfPreview ? (
                <section className={styles.pdfPreviewPanel} aria-label="In-workspace Knowledge Base PDF preview">
                  <header>
                    <div>
                      <span><FileText size={14} aria-hidden="true" /> Workspace viewer</span>
                      <strong>{pdfPreview.title}</strong>
                    </div>
                    <button
                      type="button"
                      onClick={closeVaultPdfPreview}
                      aria-label="Hide PDF preview"
                    >
                      <X size={15} aria-hidden="true" />
                    </button>
                  </header>
                  <iframe
                    src={pdfPreview.objectUrl}
                    title={`Knowledge Base PDF preview: ${pdfPreview.title}`}
                    loading="lazy"
                  />
                </section>
              ) : null}

              <section className={styles.summaryTable} aria-label="Selected document summary">
                {selectedSummary.map((item) => (
                  <div key={`${item.label}-${item.value}`}>
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                  </div>
                ))}
              </section>

              <section className={styles.taskQueue} aria-label="Selected document task queue">
                <div className={styles.sectionHeader}>
                  <span>Task queue</span>
                  <strong>Next actions for this document</strong>
                </div>

                {selectedTasks.map((task) => (
                  <div className={styles.taskRow} key={task.key}>
                    <span>{task.label}</span>
                    <small>{task.detail}</small>
                  </div>
                ))}
              </section>

              <section className={styles.evidencePanel} aria-label="Copy-only evidence controls">
                <div className={styles.sectionHeader}>
                  <span>Evidence controls</span>
                  <strong>Technical proof stays hidden until copied</strong>
                </div>

                <div className={styles.evidenceControlRow}>
                  <span>Document fingerprint</span>
                  <strong>{displayVaultDigest(selectedEntry.pdfSha3)}</strong>
                  <button
                    type="button"
                    onClick={() => handleVaultCopyCommand(selectedEntry.pdfSha3, 'Document fingerprint')}
                    disabled={!selectedEntry?.pdfSha3}
                  >
                    Copy full value
                  </button>
                </div>

                <div className={styles.evidenceControlRow}>
                  <span>Release evidence</span>
                  <strong>{displayVaultSourceTag(selectedEntry.sourceTag || selectedEntry.sourceCommit)}</strong>
                  <button
                    type="button"
                    onClick={() => handleVaultCopyCommand(selectedEntry.sourceTag || selectedEntry.sourceCommit, 'Release evidence')}
                    disabled={!(selectedEntry?.sourceTag || selectedEntry?.sourceCommit)}
                  >
                    Copy full value
                  </button>
                </div>

                <div className={styles.evidenceControlRow}>
                  <span>Document identity</span>
                  <strong>{displayVaultArtifactIdentity(selectedEntry)}</strong>
                  <button
                    type="button"
                    onClick={() => handleVaultCopyCommand(selectedEntry.id, 'Document ID')}
                    disabled={!selectedEntry?.id}
                  >
                    Copy ID
                  </button>
                </div>
              </section>
            </>
          ) : (
            <section className={styles.emptyState}>{submittedQuery ? 'Wilsy AI: I could not verify a matching operating artifact for this signal. Adjust the question, search by release, or clear the search.' : 'Wilsy AI: Select a verified artifact to ask, inspect, prove, print, or copy evidence from this Knowledge Base.'}</section>
          )}
        </section>

          {receiptCockpitOpen && latestReceiptCockpitEntry ? (
            <aside className={styles.receiptCockpit} aria-label="Knowledge Base receipt cockpit">
              <header className={styles.receiptCockpitHeader}>
                <div>
                  <span>Receipt cockpit</span>
                  <strong>{latestReceiptCockpitEntry.action}</strong>
                  <small>{latestReceiptCockpitEntry.artifactTitle}</small>
                </div>
                <button
                  type="button"
                  onClick={() => setReceiptCockpitOpen(false)}
                  aria-label="Collapse receipt cockpit"
                >
                  Collapse
                </button>
              </header>

              <div className={styles.receiptCockpitCommandRow} aria-label="Receipt cockpit actions">
                <button
                  type="button"
                  onClick={() => handleVaultActionCommand(
                    'Reprint prepared',
                    selectedEntry,
                    'Saved document prepared for printing from the receipt cockpit.',
                    () => printVaultPdf(selectedEntry),
                  )}
                  disabled={!selectedEntry?.allowedActions?.print}
                >
                  Reprint
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultPreviewCommand(
                    selectedEntry,
                    'Saved PDF reopened from the receipt cockpit.',
                  )}
                  disabled={!selectedEntry?.allowedActions?.open}
                >
                  Reopen
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultActionCommand(
                    'Download restarted',
                    selectedEntry,
                    'Saved document download restarted from the receipt cockpit.',
                    () => downloadVaultPdf(selectedEntry),
                  )}
                  disabled={!selectedEntry?.allowedActions?.download}
                >
                  Download again
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultActionCommand(
                    'Evidence opened',
                    selectedEntry,
                    'Verification record opened from the receipt cockpit.',
                    () => openVaultProofJson(selectedEntry),
                  )}
                  disabled={!selectedEntry?.allowedActions?.proof}
                >
                  Evidence
                </button>
                <button
                  type="button"
                  onClick={() => handleVaultCopyCommand(selectedEntry.pdfSha3, 'Document fingerprint')}
                  disabled={!selectedEntry?.pdfSha3}
                >
                  Copy fingerprint
                </button>
              </div>

              <section className={styles.receiptCockpitProof} aria-label="Receipt proof summary">
                <div>
                  <span>Status</span>
                  <strong>{latestReceiptCockpitEntry.status}</strong>
                </div>
                <div>
                  <span>Lock</span>
                  <strong>{latestReceiptCockpitEntry.lock}</strong>
                </div>
                <div>
                  <span>Fingerprint</span>
                  <strong>{compactKnowledgeBaseReceiptFingerprint(latestReceiptCockpitEntry.fingerprint)}</strong>
                </div>
              </section>

              <section className={styles.receiptCockpitList} aria-label="Contained receipt history">
                <header>
                  <span>Contained receipt list</span>
                  <strong>{activeReceiptCockpitEntries.length} session receipts</strong>
                </header>
                {activeReceiptCockpitEntries.map((receipt) => (
                  <button
                    type="button"
                    key={receipt.id}
                    onClick={() => setActionReceipt({
                      action: receipt.action,
                      artifactTitle: receipt.artifactTitle,
                      detail: receipt.detail,
                      at: receipt.at,
                    })}
                    aria-label={`Open receipt ${receipt.action}`}
                  >
                    <span>{receipt.action}</span>
                    <strong>{receipt.artifactTitle}</strong>
                    <small>{receipt.detail}</small>
                  </button>
                ))}
              </section>

              <p className={styles.receiptCockpitPersistenceNote}>
                Receipt captured for this saved document. Verified PDF and proof record remain available.
              </p>
            </aside>
          ) : null}

</section>
    </main>
  );
}
