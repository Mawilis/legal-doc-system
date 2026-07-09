/* eslint-disable */

import React, { useEffect, useMemo, useState } from 'react';
import * as WilsyKnowledgeBaseVaultSha3 from 'js-sha3';
import {
  Download,
  Eye,
  FileJson,
  Printer,
  RefreshCw,
  Search,
  ShieldCheck,
} from 'lucide-react';
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
 * @collaboration Knowledge Base Vault authenticated reads, authContext token storage, sovereignClient compatibility, and protected backend registry search.
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
 * @description Fetches saved Vault document data through POST with institutional evidence.
 * @param {string} url Vault document URL.
 * @param {string} commandSurface Command surface.
 * @returns {Promise<Blob>} document blob.
 * @collaboration Knowledge Base VaultE2 saved document actions and no-regeneration Vault contract.
 */
async function fetchVaultBlob(url, commandSurface) {
  const evidenceBody = await createVaultInstitutionalBody(url, commandSurface);
  const sealContract = buildVaultRequestSealHeaders(evidenceBody);
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      ...resolveVaultAuthHeaders(),
      ...sealContract.headers,
      Accept: 'application/pdf',
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

/**
 * @function useKnowledgeBaseVaultData
 * @description Loads the permissioned Knowledge Base Vault list from the read-only backend resolver.
 * @returns {object} Vault state and reload action.
 * @collaboration Knowledge Base Vault global Vault UI and saved artifact resolver route.
 */
function useKnowledgeBaseVaultData(filters = {}) {
  const [state, setState] = useState({
    loading: true,
    error: '',
    vault: null,
  });

  /**
   * @function loadVault
   * @description Loads the permissioned Knowledge Base Vault list without regenerating documents.
   * @returns {Promise<void>} Vault state update.
   * @collaboration Knowledge Base Vault Vault UI, saved artifacts only, and manifest-backed resolver.
   */
  const loadVault = async () => {
    setState((current) => ({ ...current, loading: true, error: '' }));

    try {
      const payload = await fetchVaultJson('/api/knowledge-base/vault', 'knowledge_base_vault_list', {
        filters,
        query: filters.query || '',
        category: filters.category || 'all',
      });

      setState({
        loading: false,
        error: '',
        vault: payload.vault,
      });
    } catch (error) {
      setState({
        loading: false,
        error: error.message || 'KNOWLEDGE_BASE_VAULT_LOAD_FAILED',
        vault: null,
      });
    }
  };

  useEffect(() => {
    loadVault();
  }, [JSON.stringify(filters)]);

  return {
    ...state,
    reload: loadVault,
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
 * @description Opens a Vault route in a new browser tab without regenerating an artifact.
 * @param {string} url Saved artifact route.
 * @returns {void}
 * @collaboration Knowledge Base Vault open saved document and proof verification record actions.
 */
async function openVaultUrl(url = '') {
  if (!url) return;

  const blob = await fetchVaultBlob(url, 'knowledge_base_vault_open_pdf');
  const objectUrl = URL.createObjectURL(blob);
  window.open(objectUrl, '_blank', 'noopener,noreferrer');
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
    return 'Verified saved library';
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
      value: savedDocument && evidenceRecord ? 'Complete' : 'Incomplete',
      tone: savedDocument && evidenceRecord ? 'gold' : 'risk',
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
      value: ready ? 'Access protected by proof trail' : 'Proof trail requires review',
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
      detail: 'Review the saved document in a new tab.',
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
 * @function WilsyKnowledgeBaseVault
 * @description Renders the global Knowledge Base Vault as a scalable document operating workspace with dynamic categories, selected-document tasks, and contained work areas.
 * @returns {JSX.Element} Knowledge Base Vault workspace.
 * @collaboration Knowledge Base VaultF multi-document Knowledge Base, productivity-first document operations, proof evidence, and runtime-passed request sealing.
 */
export default function WilsyKnowledgeBaseVault() {
  const [query, setQuery] = useState('');
  const [selectedEntryId, setSelectedEntryId] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [actionReceipt, setActionReceipt] = useState(null);
  const backendFilters = useMemo(() => ({
    query,
    category: activeCategory,
  }), [query, activeCategory]);
  const { loading, error, vault, reload } = useKnowledgeBaseVaultData(backendFilters);

  const entries = vault?.entries || [];
  const categoryFilters = useMemo(
    () => vault?.facets?.categories || resolveVaultCategoryFilters(entries),
    [vault?.facets, entries]
  );
  const filteredEntries = entries;
  const selectedEntry = useMemo(
    () => resolveSelectedVaultEntry(filteredEntries, selectedEntryId),
    [filteredEntries, selectedEntryId]
  );
  const selectedSummary = useMemo(() => resolveVaultDocumentSummary(selectedEntry || {}), [selectedEntry]);
  const selectedTasks = useMemo(() => resolveVaultDocumentTaskQueue(selectedEntry || {}), [selectedEntry]);

  useEffect(() => {
    if (!filteredEntries.length) {
      setSelectedEntryId('');
      return;
    }

    if (!filteredEntries.some((entry) => entry?.id === selectedEntryId)) {
      setSelectedEntryId(filteredEntries[0]?.id || '');
    }
  }, [filteredEntries, selectedEntryId]);

  return (
    <main className={styles.vaultShell} data-wilsy-surface="global-knowledge-base-vault">
      <section className={styles.vaultTopbar}>
        <div>
          <p className={styles.eyebrow}>WILSY OS KNOWLEDGE BASE</p>
          <h1>Global Vault</h1>
          <p className={styles.lede}>
            Search, classify, verify, open, print, download, and inspect permissioned documents from one operating workspace.
          </p>
        </div>

        <div className={styles.authorityPill} aria-label="Vault authority posture">
          <span>{displayVaultSourceMode(vault?.sourceMode)}</span>
          <strong>{displayVaultPermissionMode(vault?.permission?.mode)}</strong>
          <small>Saved document access only. No document regeneration.</small>
        </div>
      </section>

        <section className={styles.commandStrip} aria-label="Knowledge Base Vault command strip">
          <label className={styles.searchBox}>
            <Search size={16} aria-hidden="true" />
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  reload();
                }
              }}
              placeholder="Search saved documents, categories, owners, releases, fingerprints, or access"
              aria-label="Search Knowledge Base Vault documents"
            />
          </label>

          <button type="button" className={styles.searchButton} onClick={reload}>
            <Search size={16} aria-hidden="true" />
            Search Vault
          </button>

          <button type="button" className={styles.refreshButton} onClick={reload}>
            <RefreshCw size={16} aria-hidden="true" />
            Refresh
          </button>
        </section>

      <section className={styles.workspaceStats} aria-label="Vault workspace summary">
        <div>
          <span>Documents</span>
          <strong>{filteredEntries.length}</strong>
        </div>
        <div>
          <span>Library</span>
          <strong>{displayVaultManifestSource(vault?.manifestSource)}</strong>
        </div>
        <div>
          <span>Verification</span>
          <strong>Proof record</strong>
        </div>
        <div>
          <span>Access</span>
          <strong>Read-only</strong>
        </div>
      </section>

        <section className={styles.searchStatus} aria-live="polite" aria-label="Vault backend search status">
          <strong>
            {loading ? 'Searching backend registry' : `${filteredEntries.length} backend result${filteredEntries.length === 1 ? '' : 's'}`}
          </strong>
          <span>
            {query.trim() ? `Query: ${query.trim()}` : 'Showing all saved documents'} • {activeCategory === 'all' ? 'All categories' : activeCategory}
          </span>
        </section>

      {actionReceipt ? (
        <section className={styles.actionReceipt} aria-live="polite" aria-label="Latest Vault action receipt">
          <span>{toVaultTitleCase(actionReceipt.action)}</span>
          <strong>{actionReceipt.artifactTitle}</strong>
          <small>{actionReceipt.detail} • {actionReceipt.at}</small>
        </section>
      ) : null}

      {loading ? (
        <section className={styles.emptyState}>Loading Knowledge Base Vault.</section>
      ) : null}

      {error ? (
        <section className={styles.errorState}>
          <strong>Vault load failed</strong>
          <span>{error}</span>
        </section>
      ) : null}

      <section className={styles.vaultWorkspace} aria-label="Scalable Knowledge Base workspace">
        <aside className={styles.documentNavigator} aria-label="Document list and categories">
          <div className={styles.navigatorHeader}>
            <span>Document Library</span>
            <strong>{entries.length} total</strong>
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
              <div className={styles.emptyState}>No documents match this search or category.</div>
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

        <section className={styles.documentWorkbench} aria-label="Selected document workspace">
          {selectedEntry ? (
            <>
              <div className={styles.workbenchHeader}>
                <div>
                  <span>{resolveVaultDocumentCategory(selectedEntry)}</span>
                    <h2>Document Workbench</h2>
                    <p className={styles.selectedDocumentTitle}>{selectedEntry.title}</p>
                  <p>
                    This workspace selects one document at a time so operators can complete review, evidence, download, print, and copy tasks without leaving the Vault.
                  </p>
                </div>

                <div className={styles.workbenchStatus}>
                  <span>{resolveVaultDocumentVerificationLabel(selectedEntry)}</span>
                  <strong>{displayVaultLockStatus(selectedEntry.lockStatus)}</strong>
                </div>
              </div>

                <section className={styles.naturalOperatorSurface} aria-label="Wilsy AI natural Vault response">
                  <p>
                    <strong>Wilsy AI:</strong> I found this verified saved document in the Knowledge Base Vault. You are viewing
                    <span> {selectedEntry.title}</span>. It is {resolveVaultDocumentVerificationLabel(selectedEntry).toLowerCase()} and
                    {displayVaultLockStatus(selectedEntry.lockStatus).toLowerCase()}. You can open the saved PDF, print it, download it,
                    inspect the evidence record, or copy the fingerprint without regenerating the artifact.
                  </p>
                  <div className={styles.inlineOperatorActions} aria-label="Inline Vault operator actions">
                    <button
                      type="button"
                      onClick={() => {
                        void (async () => {
                          await openVaultUrl(selectedEntry.routes?.pdfOpenUrl);
                          setActionReceipt(buildVaultActionReceipt('Document opened', selectedEntry, 'Saved document opened from the natural operator response.'));
                        })();
                      }}
                      disabled={!selectedEntry.allowedActions?.open}
                    >
                      Open saved PDF
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        void (async () => {
                          await openVaultProofJson(selectedEntry);
                          setActionReceipt(buildVaultActionReceipt('Evidence opened', selectedEntry, 'Verification record opened from the natural operator response.'));
                        })();
                      }}
                      disabled={!selectedEntry.allowedActions?.proof}
                    >
                      Show evidence
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        void (async () => {
                          const receipt = await copyVaultClipboardText(selectedEntry.pdfSha3, 'Document fingerprint');
                          setActionReceipt(receipt);
                        })();
                      }}
                    >
                      Copy fingerprint
                    </button>
                  </div>
                </section>

              <div className={styles.taskBar} aria-label={`Tasks for ${selectedEntry.title}`}>
                <button
                  type="button"
                  onClick={() => {
                    void (async () => {
                      await openVaultUrl(selectedEntry.routes?.pdfOpenUrl);
                      setActionReceipt(buildVaultActionReceipt('Document opened', selectedEntry, 'Saved document opened from the Vault.'));
                    })();
                  }}
                  disabled={!selectedEntry.allowedActions?.open}
                >
                  <Eye size={15} aria-hidden="true" />
                  Open
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void (async () => {
                      await printVaultPdf(selectedEntry);
                      setActionReceipt(buildVaultActionReceipt('Print prepared', selectedEntry, 'Saved document prepared for printing.'));
                    })();
                  }}
                  disabled={!selectedEntry.allowedActions?.print}
                >
                  <Printer size={15} aria-hidden="true" />
                  Print
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void (async () => {
                      await downloadVaultPdf(selectedEntry);
                      setActionReceipt(buildVaultActionReceipt('Download started', selectedEntry, 'Saved document download started.'));
                    })();
                  }}
                  disabled={!selectedEntry.allowedActions?.download}
                >
                  <Download size={15} aria-hidden="true" />
                  Download
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void (async () => {
                      await openVaultProofJson(selectedEntry);
                      setActionReceipt(buildVaultActionReceipt('Evidence opened', selectedEntry, 'Verification record opened from the Vault.'));
                    })();
                  }}
                  disabled={!selectedEntry.allowedActions?.proof}
                >
                  <FileJson size={15} aria-hidden="true" />
                  Evidence
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void copyVaultClipboardText(selectedEntry.pdfSha3, 'Document fingerprint')
                      .then(setActionReceipt);
                  }}
                >
                  Copy fingerprint
                </button>
              </div>

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
                    onClick={() => {
                      void copyVaultClipboardText(selectedEntry.pdfSha3, 'Document fingerprint')
                        .then(setActionReceipt);
                    }}
                  >
                    Copy full value
                  </button>
                </div>

                <div className={styles.evidenceControlRow}>
                  <span>Release evidence</span>
                  <strong>{displayVaultSourceTag(selectedEntry.sourceTag || selectedEntry.sourceCommit)}</strong>
                  <button
                    type="button"
                    onClick={() => {
                      void copyVaultClipboardText(selectedEntry.sourceTag || selectedEntry.sourceCommit, 'Release evidence')
                        .then(setActionReceipt);
                    }}
                  >
                    Copy full value
                  </button>
                </div>

                <div className={styles.evidenceControlRow}>
                  <span>Document identity</span>
                  <strong>{displayVaultArtifactIdentity(selectedEntry)}</strong>
                  <button
                    type="button"
                    onClick={() => {
                      void copyVaultClipboardText(selectedEntry.id, 'Document ID')
                        .then(setActionReceipt);
                    }}
                  >
                    Copy ID
                  </button>
                </div>
              </section>
            </>
          ) : (
            <section className={styles.emptyState}>Select a document to begin operating.</section>
          )}
        </section>
      </section>
    </main>
  );
}



