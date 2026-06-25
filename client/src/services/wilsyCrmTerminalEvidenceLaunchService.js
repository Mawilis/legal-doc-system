/* eslint-disable */

export const WILSY_CRM_TERMINAL_EVIDENCE_LAUNCH_ADAPTER_VERSION =
  'R72A-CRM-TERMINAL-EVIDENCE-LAUNCH-CLIENT-ADAPTER-AUTHORITY';

export const WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS = Object.freeze({
  launchPacket:
    '/api/crm/command/search/regulator-evidence/terminal-launch-packet/latest',
  releaseBrief:
    '/api/crm/command/search/regulator-evidence/terminal-release-brief/latest',
  releasePassportVerifier:
    '/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest',
  releasePassport:
    '/api/crm/command/search/regulator-evidence/terminal-release-passport/latest',
  releaseReadiness:
    '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
  apiSurfaceRegistry:
    '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
  cockpitContract:
    '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
  commandIndex:
    '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
});

/**
 * @function resolveTerminalEvidenceApiBase
 * @description Resolves an optional API base URL while preserving same-origin behavior for browser runtime.
 * @collaboration CRM terminal evidence adapter, Vite client services, tenant-aware fetch flows.
 */
export const resolveTerminalEvidenceApiBase = (apiBaseUrl = '') => {
  const normalizedBase = String(apiBaseUrl || '').trim();

  if (!normalizedBase) {
    return '';
  }

  return normalizedBase.endsWith('/')
    ? normalizedBase.slice(0, -1)
    : normalizedBase;
};

/**
 * @function buildTerminalEvidenceHeaders
 * @description Builds tenant/operator headers for terminal evidence client requests without embedding secrets.
 * @collaboration CRM terminal evidence adapter, backend X-Tenant-Id contract, operator evidence HUD.
 */
export const buildTerminalEvidenceHeaders = ({
  tenantId = 'MASTER',
  operator = 'SYSTEM',
  headers = {},
} = {}) => ({
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'X-Tenant-Id': String(tenantId || 'MASTER').trim() || 'MASTER',
  'X-Wilsy-Operator': String(operator || 'SYSTEM').trim() || 'SYSTEM',
  ...headers,
});

/**
 * @function buildTerminalEvidenceUrl
 * @description Builds a terminal evidence endpoint URL from a same-origin-safe base and known endpoint path.
 * @collaboration CRM terminal evidence adapter, cockpit integration, release launch packet API.
 */
export const buildTerminalEvidenceUrl = ({
  apiBaseUrl = '',
  endpoint,
  query = {},
} = {}) => {
  const base = resolveTerminalEvidenceApiBase(apiBaseUrl);
  const path = String(endpoint || '').startsWith('/')
    ? String(endpoint || '')
    : `/${String(endpoint || '')}`;

  const params = new URLSearchParams();

  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== '') {
      params.set(key, String(value));
    }
  });

  const queryString = params.toString();

  return `${base}${path}${queryString ? `?${queryString}` : ''}`;
};

/**
 * @function normalizeTerminalEvidencePayload
 * @description Normalizes terminal evidence API payloads into a stable UI-friendly status envelope.
 * @collaboration CRM launch packet API, release brief API, cockpit HUD integration.
 */
export const normalizeTerminalEvidencePayload = (payload = {}) => ({
  ok: payload.ok === true,
  version: payload.version || null,
  status: payload.status || null,
  releaseDecision: payload.releaseDecision || null,
  releaseScore:
    typeof payload.releaseScore === 'number' ? payload.releaseScore : null,
  productizationSurface: payload.productizationSurface === true,
  terminalStop: payload.terminalStop === true,
  noR70F: payload.noR70F === true,
  recursiveLoopFrozen: payload.recursiveLoopFrozen === true,
  jsonResponseOnly: payload.jsonResponseOnly === true,
  noFilesystemWrite: payload.noFilesystemWrite === true,
  persistenceMode: payload.persistenceMode || 'JSON_RESPONSE_ONLY',
  raw: payload,
});

/**
 * @function fetchTerminalEvidenceJson
 * @description Fetches a terminal evidence endpoint and returns a normalized payload envelope.
 * @collaboration CRM terminal evidence adapter, launch packet endpoint, browser fetch runtime.
 */
export const fetchTerminalEvidenceJson = async ({
  endpoint,
  tenantId = 'MASTER',
  operator = 'SYSTEM',
  apiBaseUrl = '',
  query = {},
  headers = {},
  signal,
  fetchImpl = globalThis.fetch,
} = {}) => {
  if (typeof fetchImpl !== 'function') {
    throw new Error('WILSY_TERMINAL_EVIDENCE_FETCH_UNAVAILABLE');
  }

  const response = await fetchImpl(
    buildTerminalEvidenceUrl({
      apiBaseUrl,
      endpoint,
      query,
    }),
    {
      method: 'GET',
      headers: buildTerminalEvidenceHeaders({
        tenantId,
        operator,
        headers,
      }),
      signal,
    }
  );

  const payload = await response.json();

  if (!response.ok || payload?.ok !== true) {
    const error = new Error(
      payload?.status || 'WILSY_TERMINAL_EVIDENCE_REQUEST_FAILED'
    );
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return normalizeTerminalEvidencePayload(payload);
};

/**
 * @function fetchTerminalEvidenceLaunchPacket
 * @description Fetches the R71M terminal evidence launch packet for buyer/demo/cockpit consumption.
 * @collaboration R71M launch packet API, CRM cockpit shell, buyer evidence surfaces.
 */
export const fetchTerminalEvidenceLaunchPacket = (options = {}) =>
  fetchTerminalEvidenceJson({
    ...options,
    endpoint: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.launchPacket,
  });

/**
 * @function fetchTerminalEvidenceReleaseBrief
 * @description Fetches the R71L release brief for executive, board, regulator, investor, and audit display.
 * @collaboration R71L release brief API, CRM launch packet adapter, executive evidence surfaces.
 */
export const fetchTerminalEvidenceReleaseBrief = (options = {}) =>
  fetchTerminalEvidenceJson({
    ...options,
    endpoint: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.releaseBrief,
  });

/**
 * @function fetchTerminalEvidenceCockpitContract
 * @description Fetches the R71G cockpit contract for future CRM dashboard wiring.
 * @collaboration R71G cockpit contract API, CRM dashboard HUD, command surface integration.
 */
export const fetchTerminalEvidenceCockpitContract = (options = {}) =>
  fetchTerminalEvidenceJson({
    ...options,
    endpoint: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.cockpitContract,
  });

/**
 * @function fetchTerminalEvidenceApiSurfaceRegistry
 * @description Fetches the R71H API surface registry for route/schema/client integration awareness.
 * @collaboration R71H API registry, CRM cockpit adapter, engineering integration workflow.
 */
export const fetchTerminalEvidenceApiSurfaceRegistry = (options = {}) =>
  fetchTerminalEvidenceJson({
    ...options,
    endpoint: WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS.apiSurfaceRegistry,
  });

/**
 * @function buildTerminalEvidenceLaunchSnapshot
 * @description Converts a launch packet payload into a compact cockpit-ready snapshot.
 * @collaboration R71M launch packet API, CRM cockpit cards, investor/regulator evidence HUD.
 */
export const buildTerminalEvidenceLaunchSnapshot = (payload = {}) => {
  const normalized = normalizeTerminalEvidencePayload(payload);
  const raw = normalized.raw || {};

  const launchArtifacts = Array.isArray(raw.launchArtifacts)
    ? raw.launchArtifacts
    : [];

  const launchSequence = Array.isArray(raw.launchSequence)
    ? raw.launchSequence
    : [];

  const launchReadinessMatrix = Array.isArray(raw.launchReadinessMatrix)
    ? raw.launchReadinessMatrix
    : [];

  return {
    adapterVersion: WILSY_CRM_TERMINAL_EVIDENCE_LAUNCH_ADAPTER_VERSION,
    ok: normalized.ok,
    status: normalized.status,
    releaseDecision: normalized.releaseDecision,
    releaseScore: normalized.releaseScore,
    topKpi:
      raw.launchPacketIdentity?.buyerReadableStatus ||
      raw.buyerReadableStatus ||
      'VERIFIED_TERMINAL_EVIDENCE',
    launchArtifactCount: launchArtifacts.length,
    launchSequenceCount: launchSequence.length,
    launchReadinessCount: launchReadinessMatrix.length,
    buyerDemoReady:
      raw.launchAssertions?.buyerDemoReady === true ||
      launchArtifacts.some(
        (artifact) =>
          artifact.artifact === 'buyer_demo_packet' && artifact.ready === true
      ),
    regulatorReady:
      raw.launchAssertions?.regulatorReady === true ||
      launchArtifacts.some(
        (artifact) =>
          artifact.artifact === 'regulator_inspection_packet' &&
          artifact.ready === true
      ),
    investorReady:
      raw.launchAssertions?.investorReady === true ||
      launchArtifacts.some(
        (artifact) =>
          artifact.artifact === 'investor_diligence_packet' &&
          artifact.ready === true
      ),
    auditorReady:
      raw.launchAssertions?.auditorReady === true ||
      launchArtifacts.some(
        (artifact) =>
          artifact.artifact === 'audit_assurance_packet' &&
          artifact.ready === true
      ),
    engineeringReady:
      raw.launchAssertions?.engineeringReady === true ||
      launchArtifacts.some(
        (artifact) =>
          artifact.artifact === 'engineering_handoff_packet' &&
          artifact.ready === true
      ),
    terminalStop: normalized.terminalStop,
    noR70F: normalized.noR70F,
    recursiveLoopFrozen: normalized.recursiveLoopFrozen,
    jsonResponseOnly: normalized.jsonResponseOnly,
    noFilesystemWrite: normalized.noFilesystemWrite,
    persistenceMode: normalized.persistenceMode,
    launchArtifacts,
    launchSequence,
    launchReadinessMatrix,
  };
};

export default {
  WILSY_CRM_TERMINAL_EVIDENCE_LAUNCH_ADAPTER_VERSION,
  WILSY_CRM_TERMINAL_EVIDENCE_ENDPOINTS,
  resolveTerminalEvidenceApiBase,
  buildTerminalEvidenceHeaders,
  buildTerminalEvidenceUrl,
  normalizeTerminalEvidencePayload,
  fetchTerminalEvidenceJson,
  fetchTerminalEvidenceLaunchPacket,
  fetchTerminalEvidenceReleaseBrief,
  fetchTerminalEvidenceCockpitContract,
  fetchTerminalEvidenceApiSurfaceRegistry,
  buildTerminalEvidenceLaunchSnapshot,
};
