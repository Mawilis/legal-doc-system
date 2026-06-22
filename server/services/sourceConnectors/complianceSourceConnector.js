/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — COMPLIANCE SOURCE CONNECTOR                                     ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/services/sourceConnectors/complianceSourceConnector.js         ║
 * ║ PURPOSE: Provide real compliance evidence to the Source Registry.           ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This connector never fabricates compliance verification.
 *
 * VERIFIED requires evidence from one of:
 * 1. WILSY_COMPLIANCE_EVIDENCE_FILE — absolute JSON evidence file path.
 * 2. WILSY_COMPLIANCE_API_URL — live compliance evidence API.
 *
 * Missing configuration returns MISSING.
 * Incomplete records return PENDING.
 * Errors return ERROR.
 *
 * Expected evidence shape:
 * {
 *   "tenantId": "MASTER",
 *   "controls": {
 *     "POPIA": {
 *       "verified": true,
 *       "sourceId": "popia-control-2026-001",
 *       "retrievedAt": "2026-06-16T00:00:00.000Z",
 *       "evidence": { ... }
 *     },
 *     "GDPR": { ... },
 *     "SOC2": { ... }
 *   }
 * }
 */

import crypto from 'node:crypto';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';

const STATUS = Object.freeze({
  VERIFIED: 'VERIFIED',
  PENDING: 'PENDING',
  MISSING: 'MISSING',
  ERROR: 'ERROR',
});

const CONTROL_REFERENCES = Object.freeze({
  POPIA: Object.freeze({
    framework: 'POPIA',
    jurisdiction: 'South Africa',
    references: Object.freeze([
      'POPIA Condition 7 — Security safeguards',
      'POPIA Section 19 — Security measures on integrity and confidentiality of personal information',
      'POPIA Section 20 — Information processed by operator or person acting under authority',
      'POPIA Section 21 — Security measures regarding information processed by operator',
      'POPIA Section 22 — Notification of security compromises',
    ]),
  }),
  GDPR: Object.freeze({
    framework: 'GDPR',
    jurisdiction: 'European Union',
    references: Object.freeze([
      'GDPR Article 5 — Principles relating to processing of personal data',
      'GDPR Article 32 — Security of processing',
      'GDPR Article 33 — Notification of personal data breach to supervisory authority',
      'GDPR Article 44 — General principle for transfers',
    ]),
  }),
  SOC2: Object.freeze({
    framework: 'SOC2',
    jurisdiction: 'Trust Services Criteria',
    references: Object.freeze([
      'Security',
      'Availability',
      'Processing Integrity',
      'Confidentiality',
      'Privacy',
    ]),
  }),
});

/**
 * @function nowIso
 * @description Returns an ISO timestamp.
 * @returns {string} ISO timestamp.
 */
function nowIso() {
  return new Date().toISOString();
}

/**
 * @function stableStringify
 * @description Deterministically serializes evidence for hashing.
 * @param {*} value - Value to serialize.
 * @returns {string} Stable JSON string.
 */
function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(',')}}`;
}

/**
 * @function hashEvidence
 * @description Creates a forensic hash for evidence payloads.
 * @param {*} payload - Evidence payload.
 * @returns {{algorithm:string, hash:string}} Hash result.
 */
function hashEvidence(payload) {
  const algorithm = crypto.getHashes().includes('sha3-512') ? 'sha3-512' : 'sha512';

  return {
    algorithm,
    hash: crypto.createHash(algorithm).update(stableStringify(payload)).digest('hex'),
  };
}

/**
 * @function normalizeTenantId
 * @description Normalizes tenant id for evidence lookup.
 * @param {string} tenantId - Tenant id.
 * @returns {string} Normalized tenant id.
 */
function normalizeTenantId(tenantId = 'MASTER') {
  return String(tenantId || 'MASTER').trim() || 'MASTER';
}

/**
 * @function safeJsonParse
 * @description Parses JSON with a descriptive error.
 * @param {string} content - JSON content.
 * @param {string} label - Source label.
 * @returns {*} Parsed JSON.
 */
function safeJsonParse(content, label) {
  try {
    return JSON.parse(content);
  } catch (error) {
    const enriched = new Error(`Invalid compliance evidence JSON from ${label}: ${error.message}`);
    enriched.cause = error;
    throw enriched;
  }
}

/**
 * @function evidenceFilePath
 * @description Resolves compliance evidence file path from environment.
 * @returns {string} Evidence file path.
 */
function evidenceFilePath() {
  return String(process.env.WILSY_COMPLIANCE_EVIDENCE_FILE || '').trim();
}

/**
 * @function complianceApiUrl
 * @description Resolves compliance evidence API base URL from environment.
 * @returns {string} API URL.
 */
function complianceApiUrl() {
  return String(process.env.WILSY_COMPLIANCE_API_URL || '')
    .replace(/\/$/, '')
    .trim();
}

/**
 * @function readFileEvidence
 * @description Reads local compliance evidence from configured JSON file.
 * @returns {Promise<object|null>} Evidence object or null.
 */
async function readFileEvidence() {
  const filePath = evidenceFilePath();

  if (!filePath) return null;

  if (!existsSync(filePath)) {
    return {
      __connectorStatus: STATUS.MISSING,
      __message: `Configured compliance evidence file does not exist: ${filePath}`,
    };
  }

  const content = await readFile(filePath, 'utf8');

  return safeJsonParse(content, filePath);
}

/**
 * @function fetchApiEvidence
 * @description Fetches compliance evidence from configured API.
 * @param {object} context - Connector context.
 * @returns {Promise<object|null>} API evidence.
 */
async function fetchApiEvidence(context = {}) {
  const baseUrl = complianceApiUrl();

  if (!baseUrl) return null;

  const url = new URL(`${baseUrl}/compliance/evidence`);
  url.searchParams.set('tenantId', normalizeTenantId(context.tenantId));
  url.searchParams.set('framework', context.framework || 'ALL');

  const token = String(process.env.WILSY_COMPLIANCE_API_TOKEN || '').trim();

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Wilsy-Trace-Id': context.traceId || `COMP-${Date.now().toString(16).toUpperCase()}`,
    },
  });

  if (!response.ok) {
    return {
      __connectorStatus: STATUS.ERROR,
      __message: `Compliance evidence API failed ${response.status}: ${await response.text()}`,
    };
  }

  return response.json();
}

/**
 * @function readEvidenceStore
 * @description Reads compliance evidence from API first, then file fallback.
 * @param {object} context - Connector context.
 * @returns {Promise<object>} Evidence store result.
 */
async function readEvidenceStore(context = {}) {
  const hasApi = Boolean(complianceApiUrl());
  const hasFile = Boolean(evidenceFilePath());

  if (!hasApi && !hasFile) {
    return {
      __connectorStatus: STATUS.MISSING,
      __message:
        'No compliance evidence source configured. Set WILSY_COMPLIANCE_API_URL or WILSY_COMPLIANCE_EVIDENCE_FILE.',
    };
  }

  if (hasApi) {
    const apiEvidence = await fetchApiEvidence(context);
    if (apiEvidence) return apiEvidence;
  }

  if (hasFile) {
    const fileEvidence = await readFileEvidence();
    if (fileEvidence) return fileEvidence;
  }

  return {
    __connectorStatus: STATUS.MISSING,
    __message: 'No compliance evidence was returned from configured sources.',
  };
}

/**
 * @function selectTenantEvidence
 * @description Selects tenant-specific evidence from supported evidence shapes.
 * @param {object} store - Evidence store.
 * @param {string} tenantId - Tenant id.
 * @returns {object} Tenant evidence.
 */
function selectTenantEvidence(store = {}, tenantId = 'MASTER') {
  const normalizedTenantId = normalizeTenantId(tenantId);

  if (store.tenantId && normalizeTenantId(store.tenantId) === normalizedTenantId) {
    return store;
  }

  if (store.tenants && store.tenants[normalizedTenantId]) {
    return store.tenants[normalizedTenantId];
  }

  if (store[normalizedTenantId]) {
    return store[normalizedTenantId];
  }

  if (store.controls) {
    return store;
  }

  return null;
}

/**
 * @function normalizeControlRecord
 * @description Converts a control evidence record into the strict Source Registry evidence shape.
 * @param {string} framework - POPIA/GDPR/SOC2.
 * @param {object} record - Evidence record.
 * @param {object} context - Connector context.
 * @returns {object} Normalized connector result.
 */
function normalizeControlRecord(framework, record, context = {}) {
  const references = CONTROL_REFERENCES[framework];

  if (!record) {
    return {
      status: STATUS.PENDING,
      framework,
      message: `${framework} evidence record not found.`,
      evidence: {
        references,
        tenantId: normalizeTenantId(context.tenantId),
        artifact: context.artifact?.id || context.artifact?.type || context.artifact?.title || null,
      },
    };
  }

  const evidencePayload = record.evidence || record.data || record.record || null;
  const sourceId = record.sourceId || record.recordId || record.id || null;
  const retrievedAt = record.retrievedAt || record.timestamp || record.generatedAt || null;
  const verified = record.status === STATUS.VERIFIED || record.verified === true;

  const baseEvidence = {
    framework,
    references,
    tenantId: normalizeTenantId(context.tenantId),
    artifact: context.artifact?.id || context.artifact?.type || context.artifact?.title || null,
    sourceId,
    retrievedAt,
    evidence: evidencePayload,
  };

  const seal = hashEvidence(baseEvidence);

  if (!verified || !sourceId || !retrievedAt || !evidencePayload) {
    return {
      status: STATUS.PENDING,
      verified: false,
      framework,
      sourceId,
      retrievedAt,
      message: `${framework} evidence is present but incomplete for boardroom reliance.`,
      requirements: {
        verifiedStatus: verified,
        sourceId: Boolean(sourceId),
        retrievedAt: Boolean(retrievedAt),
        evidencePayload: Boolean(evidencePayload),
      },
      evidence: baseEvidence,
      evidenceHash: seal.hash,
      hashAlgorithm: seal.algorithm,
    };
  }

  return {
    status: STATUS.VERIFIED,
    verified: true,
    framework,
    sourceId,
    retrievedAt,
    evidence: baseEvidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function getControlStatus
 * @description Resolves one compliance control from the configured evidence source.
 * @param {string} framework - POPIA/GDPR/SOC2.
 * @param {object} context - Connector context.
 * @returns {Promise<object>} Connector evidence result.
 */
async function getControlStatus(framework, context = {}) {
  try {
    const store = await readEvidenceStore({ ...context, framework });

    if (store.__connectorStatus) {
      return {
        status: store.__connectorStatus,
        framework,
        message: store.__message,
        evidence: {
          references: CONTROL_REFERENCES[framework],
          tenantId: normalizeTenantId(context.tenantId),
        },
      };
    }

    const tenantEvidence = selectTenantEvidence(store, context.tenantId);

    if (!tenantEvidence) {
      return {
        status: STATUS.MISSING,
        framework,
        message: `No compliance evidence found for tenant ${normalizeTenantId(context.tenantId)}.`,
        evidence: {
          references: CONTROL_REFERENCES[framework],
          tenantId: normalizeTenantId(context.tenantId),
        },
      };
    }

    const controls = tenantEvidence.controls || tenantEvidence.compliance || tenantEvidence;
    const record = controls[framework] || controls[framework.toLowerCase()];

    return normalizeControlRecord(framework, record, context);
  } catch (error) {
    return {
      status: STATUS.ERROR,
      framework,
      message: error.message,
      evidence: {
        references: CONTROL_REFERENCES[framework],
        tenantId: normalizeTenantId(context.tenantId),
      },
    };
  }
}

/**
 * @function getPOPIAStatus
 * @description Returns verified POPIA evidence only from configured live/file evidence sources.
 * @param {object} context - Connector context.
 * @returns {Promise<object>} POPIA evidence.
 */
export async function getPOPIAStatus(context = {}) {
  return getControlStatus('POPIA', context);
}

/**
 * @function getGDPRStatus
 * @description Returns verified GDPR evidence only from configured live/file evidence sources.
 * @param {object} context - Connector context.
 * @returns {Promise<object>} GDPR evidence.
 */
export async function getGDPRStatus(context = {}) {
  return getControlStatus('GDPR', context);
}

/**
 * @function getSOC2Status
 * @description Returns verified SOC2 evidence only from configured live/file evidence sources.
 * @param {object} context - Connector context.
 * @returns {Promise<object>} SOC2 evidence.
 */
export async function getSOC2Status(context = {}) {
  return getControlStatus('SOC2', context);
}

/**
 * @function getJurisdictionControls
 * @description Returns jurisdiction control metadata plus strict evidence status.
 * @param {object} context - Connector context.
 * @returns {Promise<object>} Jurisdiction controls evidence.
 */
export async function getJurisdictionControls(context = {}) {
  const controls = await Promise.all([
    getPOPIAStatus(context),
    getGDPRStatus(context),
    getSOC2Status(context),
  ]);

  const status = controls.every((item) => item.status === STATUS.VERIFIED)
    ? STATUS.VERIFIED
    : controls.some((item) => item.status === STATUS.ERROR)
      ? STATUS.ERROR
      : controls.some((item) => item.status === STATUS.MISSING)
        ? STATUS.MISSING
        : STATUS.PENDING;

  const evidence = {
    tenantId: normalizeTenantId(context.tenantId),
    controls,
    references: CONTROL_REFERENCES,
    evaluatedAt: nowIso(),
  };

  const seal = hashEvidence(evidence);

  if (status !== STATUS.VERIFIED) {
    return {
      status,
      verified: false,
      sourceId: `jurisdiction-controls-${normalizeTenantId(context.tenantId)}`,
      retrievedAt: evidence.evaluatedAt,
      message: 'Jurisdiction controls are not fully verified.',
      evidence,
      evidenceHash: seal.hash,
      hashAlgorithm: seal.algorithm,
    };
  }

  return {
    status: STATUS.VERIFIED,
    verified: true,
    sourceId: `jurisdiction-controls-${normalizeTenantId(context.tenantId)}`,
    retrievedAt: evidence.evaluatedAt,
    evidence,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

export default Object.freeze({
  getPOPIAStatus,
  getGDPRStatus,
  getSOC2Status,
  getJurisdictionControls,
});
