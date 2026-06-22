/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — SOVEREIGN SOURCE REGISTRY                                       ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/config/sourceRegistry.js                                      ║
 * ║ PURPOSE: Bind artifacts to live source connectors before external reliance. ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This registry is intentionally strict:
 * - Missing connector file => MISSING
 * - Missing connector method => MISSING
 * - Connector returns no evidence => PENDING
 * - Connector throws => ERROR
 * - Only evidence-bearing connector responses => VERIFIED
 *
 * No UI placeholder may mark a source as verified.
 * No boardroom proof may be sealed until all required evidence is verified.
 */

import crypto from 'node:crypto';
import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export const HASH_ALGORITHM = crypto.getHashes().includes('sha3-512') ? 'sha3-512' : 'sha512';

export const SOURCE_STATUS = Object.freeze({
  VERIFIED: 'VERIFIED',
  PENDING: 'PENDING',
  MISSING: 'MISSING',
  ERROR: 'ERROR',
  BLOCKED: 'BLOCKED',
  READY_FOR_ANCHOR: 'READY_FOR_ANCHOR',
});

export const SOURCE_CONNECTORS = Object.freeze({
  Finance: Object.freeze({
    id: 'Finance',
    label: 'Finance Ledger',
    modulePath: '../services/sourceConnectors/financeSourceConnector.js',
    requiredMethods: Object.freeze([
      'getRevenueYTD',
      'getAnnualRecurringRevenue',
      'getRunwayMonths',
      'getContractValueLedger',
    ]),
  }),
  HR: Object.freeze({
    id: 'HR',
    label: 'People / HRIS Registry',
    modulePath: '../services/sourceConnectors/hrSourceConnector.js',
    requiredMethods: Object.freeze(['getEmployeeProfile', 'getIPAssignment', 'getAuthorityRecord']),
  }),
  Compliance: Object.freeze({
    id: 'Compliance',
    label: 'Compliance Registry',
    modulePath: '../services/sourceConnectors/complianceSourceConnector.js',
    requiredMethods: Object.freeze([
      'getPOPIAStatus',
      'getGDPRStatus',
      'getSOC2Status',
      'getJurisdictionControls',
    ]),
  }),
  Telemetry: Object.freeze({
    id: 'Telemetry',
    label: 'Telemetry / Reliability Evidence',
    modulePath: '../services/sourceConnectors/telemetrySourceConnector.js',
    requiredMethods: Object.freeze(['getUptime', 'getIncidentLog', 'getChangeControlLog']),
  }),
  CRM: Object.freeze({
    id: 'CRM',
    label: 'CRM / Contract Ledger',
    modulePath: '../services/sourceConnectors/crmSourceConnector.js',
    requiredMethods: Object.freeze([
      'getTenantProfile',
      'getContractLedger',
      'getCounterpartyAuthority',
    ]),
  }),
});

export const JURISDICTION_CONTROLS = Object.freeze({
  POPIA: Object.freeze({
    jurisdiction: 'South Africa',
    references: Object.freeze([
      'POPIA Section 19 — Security safeguards',
      'POPIA Section 20 — Information processed by operator',
      'POPIA Section 21 — Security measures by operator',
      'POPIA Section 22 — Security compromise notification',
    ]),
    requiredConnector: 'Compliance',
  }),
  GDPR: Object.freeze({
    jurisdiction: 'European Union',
    references: Object.freeze([
      'GDPR Article 5 — Processing principles',
      'GDPR Article 32 — Security of processing',
      'GDPR Article 44 — International transfer principle',
    ]),
    requiredConnector: 'Compliance',
  }),
  SOC2: Object.freeze({
    jurisdiction: 'SOC 2 / Trust Services Criteria',
    references: Object.freeze([
      'Security',
      'Availability',
      'Processing Integrity',
      'Confidentiality',
      'Privacy',
    ]),
    requiredConnector: 'Compliance',
  }),
});

export const ARTIFACT_SOURCE_BINDING_RULES = Object.freeze([
  Object.freeze({
    group: 'NDA & Confidentiality',
    match: Object.freeze(['nda', 'non-disclosure', 'confidentiality']),
    requiredConnectors: Object.freeze(['CRM', 'Compliance']),
  }),
  Object.freeze({
    group: 'Services & Commercial',
    match: Object.freeze([
      'master-services',
      'statement-of-work',
      'service agreement',
      'msa',
      'sow',
      'terms-of-service',
    ]),
    requiredConnectors: Object.freeze(['CRM', 'Finance', 'Compliance']),
  }),
  Object.freeze({
    group: 'SaaS & Subscription',
    match: Object.freeze(['saas', 'subscription', 'service-level', 'sla', 'uptime']),
    requiredConnectors: Object.freeze(['CRM', 'Finance', 'Telemetry', 'Compliance']),
  }),
  Object.freeze({
    group: 'Privacy & Data',
    match: Object.freeze(['privacy', 'popia', 'gdpr', 'data-processing', 'cookie', 'paia']),
    requiredConnectors: Object.freeze(['CRM', 'Compliance']),
  }),
  Object.freeze({
    group: 'Governance & Compliance',
    match: Object.freeze([
      'board',
      'governance',
      'resolution',
      'risk-register',
      'compliance',
      'audit',
    ]),
    requiredConnectors: Object.freeze(['Compliance']),
  }),
  Object.freeze({
    group: 'Finance & Procurement',
    match: Object.freeze([
      'invoice',
      'quotation',
      'purchase',
      'supplier',
      'vendor',
      'rfp',
      'finance',
      'payment',
    ]),
    requiredConnectors: Object.freeze(['Finance', 'Compliance']),
  }),
  Object.freeze({
    group: 'People & Operations',
    match: Object.freeze([
      'employment',
      'hr',
      'employee',
      'contractor',
      'leave',
      'disciplinary',
      'ip assignment',
    ]),
    requiredConnectors: Object.freeze(['HR', 'Compliance']),
  }),
  Object.freeze({
    group: 'Project Delivery',
    match: Object.freeze([
      'project',
      'evm',
      'variation',
      'payment-certificate',
      'site-instruction',
      'milestone',
    ]),
    requiredConnectors: Object.freeze(['Finance', 'Telemetry', 'Compliance']),
  }),
  Object.freeze({
    group: 'Security & IT',
    match: Object.freeze([
      'security',
      'access',
      'backup',
      'vulnerability',
      'change-advisory',
      'incident',
    ]),
    requiredConnectors: Object.freeze(['Telemetry', 'Compliance']),
  }),
]);

/**
 * @function deterministicStringify
 * @description Stable JSON serialization for forensic hashing.
 * @param {*} value - Value to serialize.
 * @returns {string} Deterministic JSON string.
 */
export function deterministicStringify(value) {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return `[${value.map((item) => deterministicStringify(item)).join(',')}]`;
  }

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${deterministicStringify(value[key])}`)
    .join(',')}}`;
}

/**
 * @function createForensicHash
 * @description Creates a deterministic SHA3-512 hash where available, otherwise SHA-512 fallback.
 * @param {*} payload - Payload to hash.
 * @returns {{algorithm:string, hash:string}} Hash result.
 */
export function createForensicHash(payload) {
  const body = deterministicStringify(payload);

  return {
    algorithm: HASH_ALGORITHM,
    hash: crypto.createHash(HASH_ALGORITHM).update(body).digest('hex'),
  };
}

/**
 * @function normalizeArtifactText
 * @description Normalizes an artifact into searchable binding text.
 * @param {object} artifact - Artifact template or payload.
 * @returns {string} Normalized binding text.
 */
export function normalizeArtifactText(artifact = {}) {
  return `${artifact.id || ''} ${artifact.type || ''} ${artifact.title || ''} ${artifact.name || ''} ${artifact.category || ''} ${artifact.description || ''}`
    .toLowerCase()
    .replace(/_/g, '-');
}

/**
 * @function resolveArtifactBinding
 * @description Resolves artifact group and required connectors.
 * @param {object} artifact - Artifact template or payload.
 * @returns {{group:string, requiredConnectors:string[]}} Source binding.
 */
export function resolveArtifactBinding(artifact = {}) {
  const normalized = normalizeArtifactText(artifact);

  const rule = ARTIFACT_SOURCE_BINDING_RULES.find((candidate) =>
    candidate.match.some((fragment) => normalized.includes(fragment))
  );

  if (rule) {
    return {
      group: rule.group,
      requiredConnectors: Array.from(rule.requiredConnectors),
    };
  }

  return {
    group: 'Other Legal Artifacts',
    requiredConnectors: ['Compliance'],
  };
}

/**
 * @function connectorAbsolutePath
 * @description Resolves connector module path from registry config.
 * @param {object} connector - Connector definition.
 * @returns {string} Absolute module path.
 */
export function connectorAbsolutePath(connector) {
  return resolve(__dirname, connector.modulePath);
}

/**
 * @function loadConnector
 * @description Dynamically loads a connector without breaking the server if the connector is missing.
 * @param {object} connector - Connector definition.
 * @returns {Promise<{status:string, api?:object, message?:string}>} Load result.
 */
export async function loadConnector(connector) {
  const absolutePath = connectorAbsolutePath(connector);

  if (!existsSync(absolutePath)) {
    return {
      status: SOURCE_STATUS.MISSING,
      message: `Connector file missing: ${connector.modulePath}`,
    };
  }

  try {
    const module = await import(pathToFileURL(absolutePath).href);
    return {
      status: SOURCE_STATUS.PENDING,
      api: module.default || module,
    };
  } catch (error) {
    return {
      status: SOURCE_STATUS.ERROR,
      message: error.message,
    };
  }
}

/**
 * @function evaluateConnectorEvidence
 * @description Strictly evaluates whether a connector response contains real evidence.
 * @param {*} result - Connector method result.
 * @param {object} context - Evaluation context.
 * @returns {object} Evidence status.
 */
export function evaluateConnectorEvidence(result, context = {}) {
  if (!result) {
    return {
      status: SOURCE_STATUS.PENDING,
      message: 'Connector returned no evidence.',
    };
  }

  if (result.status === SOURCE_STATUS.MISSING) {
    return {
      status: SOURCE_STATUS.MISSING,
      message: result.message || 'Connector reported missing evidence.',
    };
  }

  if (result.status === SOURCE_STATUS.ERROR) {
    return {
      status: SOURCE_STATUS.ERROR,
      message: result.message || 'Connector reported an error.',
    };
  }

  const evidencePayload = result.evidence || result.data || result.record || null;
  const hasVerifiedStatus = result.status === SOURCE_STATUS.VERIFIED || result.verified === true;
  const hasSourceId = Boolean(result.sourceId || result.recordId || result.id);
  const hasTimestamp = Boolean(result.retrievedAt || result.timestamp || result.generatedAt);

  if (!hasVerifiedStatus || !hasSourceId || !hasTimestamp || !evidencePayload) {
    return {
      status: SOURCE_STATUS.PENDING,
      message: 'Connector responded, but evidence is not complete enough for boardroom reliance.',
      requirements: {
        verifiedStatus: hasVerifiedStatus,
        sourceId: hasSourceId,
        timestamp: hasTimestamp,
        evidencePayload: Boolean(evidencePayload),
      },
    };
  }

  const evidence = {
    connector: context.connector,
    method: context.method,
    sourceId: result.sourceId || result.recordId || result.id,
    retrievedAt: result.retrievedAt || result.timestamp || result.generatedAt,
    evidence: evidencePayload,
  };

  const seal = createForensicHash(evidence);

  return {
    status: SOURCE_STATUS.VERIFIED,
    sourceId: evidence.sourceId,
    retrievedAt: evidence.retrievedAt,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function verifyConnectorMethod
 * @description Runs one connector method and evaluates its evidence.
 * @param {object} api - Connector API.
 * @param {string} connectorName - Connector key.
 * @param {string} method - Required method.
 * @param {object} context - Verification context.
 * @returns {Promise<object>} Method verification result.
 */
export async function verifyConnectorMethod(api, connectorName, method, context = {}) {
  if (!api || typeof api[method] !== 'function') {
    return {
      connector: connectorName,
      method,
      status: SOURCE_STATUS.MISSING,
      message: `Required connector method missing: ${connectorName}.${method}`,
    };
  }

  try {
    const result = await api[method]({
      tenantId: context.tenantId,
      artifact: context.artifact,
      actor: context.actor,
      traceId: context.traceId,
    });

    return {
      connector: connectorName,
      method,
      ...evaluateConnectorEvidence(result, { connector: connectorName, method }),
    };
  } catch (error) {
    return {
      connector: connectorName,
      method,
      status: SOURCE_STATUS.ERROR,
      message: error.message,
    };
  }
}

/**
 * @function rollupStatus
 * @description Rolls method statuses into one connector/artifact/registry status.
 * @param {Array<object>} items - Items with status fields.
 * @returns {string} Rolled status.
 */
export function rollupStatus(items = []) {
  if (!items.length) return SOURCE_STATUS.MISSING;
  if (items.every((item) => item.status === SOURCE_STATUS.VERIFIED)) return SOURCE_STATUS.VERIFIED;
  if (items.some((item) => item.status === SOURCE_STATUS.ERROR)) return SOURCE_STATUS.ERROR;
  if (items.some((item) => item.status === SOURCE_STATUS.MISSING)) return SOURCE_STATUS.MISSING;
  return SOURCE_STATUS.PENDING;
}

/**
 * @function verifyConnector
 * @description Verifies all required methods for a connector.
 * @param {string} connectorName - Connector key.
 * @param {object} context - Verification context.
 * @returns {Promise<object>} Connector verification.
 */
export async function verifyConnector(connectorName, context = {}) {
  const connector = SOURCE_CONNECTORS[connectorName];

  if (!connector) {
    return {
      connector: connectorName,
      status: SOURCE_STATUS.MISSING,
      message: `Unknown connector: ${connectorName}`,
      methods: [],
    };
  }

  const loaded = await loadConnector(connector);

  if (loaded.status === SOURCE_STATUS.MISSING || loaded.status === SOURCE_STATUS.ERROR) {
    return {
      connector: connectorName,
      label: connector.label,
      status: loaded.status,
      message: loaded.message,
      methods: connector.requiredMethods.map((method) => ({
        connector: connectorName,
        method,
        status: loaded.status,
        message: loaded.message,
      })),
    };
  }

  const methods = [];

  for (const method of connector.requiredMethods) {
    methods.push(await verifyConnectorMethod(loaded.api, connectorName, method, context));
  }

  const status = rollupStatus(methods);
  const seal = createForensicHash({
    connector: connectorName,
    status,
    methods,
  });

  return {
    connector: connectorName,
    label: connector.label,
    status,
    methods,
    evidenceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function verifyArtifactSources
 * @description Verifies the live sources required by one artifact.
 * @param {object} artifact - Artifact template or payload.
 * @param {object} context - Tenant and actor context.
 * @returns {Promise<object>} Artifact source verification.
 */
export async function verifyArtifactSources(artifact = {}, context = {}) {
  const binding = resolveArtifactBinding(artifact);
  const connectors = [];

  for (const connectorName of binding.requiredConnectors) {
    connectors.push(
      await verifyConnector(connectorName, {
        ...context,
        artifact,
      })
    );
  }

  const status = rollupStatus(connectors);
  const seal = createForensicHash({
    artifact: {
      id: artifact.id,
      type: artifact.type,
      title: artifact.title,
      category: artifact.category,
    },
    binding,
    connectors,
    status,
  });

  return {
    artifactId: artifact.id || artifact.type || artifact.title || 'artifact',
    artifactTitle: artifact.title || artifact.name || 'Untitled Artifact',
    artifactType: artifact.type || artifact.id || 'artifact',
    group: binding.group,
    requiredConnectors: binding.requiredConnectors,
    status,
    connectors,
    sourceHash: seal.hash,
    hashAlgorithm: seal.algorithm,
    verifiedAt: status === SOURCE_STATUS.VERIFIED ? new Date().toISOString() : null,
  };
}

/**
 * @function verifySourceRegistry
 * @description Verifies source evidence for a catalog of artifacts.
 * @param {object} args - Verification arguments.
 * @returns {Promise<object>} Registry verification result.
 */
export async function verifySourceRegistry({
  artifacts = [],
  tenantId = 'MASTER',
  actor = 'system',
  traceId = `SRC-${Date.now().toString(16).toUpperCase()}`,
} = {}) {
  const startedAt = new Date().toISOString();

  if (!Array.isArray(artifacts) || artifacts.length === 0) {
    return {
      registryId: traceId,
      tenantId,
      actor,
      status: SOURCE_STATUS.MISSING,
      startedAt,
      completedAt: new Date().toISOString(),
      message: 'No artifact catalog supplied for source verification.',
      summary: {
        total: 0,
        verified: 0,
        pending: 0,
        missing: 0,
        error: 0,
      },
      artifacts: [],
    };
  }

  const results = [];

  for (const artifact of artifacts) {
    results.push(await verifyArtifactSources(artifact, { tenantId, actor, traceId }));
  }

  const status = rollupStatus(results);
  const summary = {
    total: results.length,
    verified: results.filter((item) => item.status === SOURCE_STATUS.VERIFIED).length,
    pending: results.filter((item) => item.status === SOURCE_STATUS.PENDING).length,
    missing: results.filter((item) => item.status === SOURCE_STATUS.MISSING).length,
    error: results.filter((item) => item.status === SOURCE_STATUS.ERROR).length,
  };

  const completedAt = new Date().toISOString();
  const registrySeal = createForensicHash({
    registryId: traceId,
    tenantId,
    actor,
    startedAt,
    completedAt,
    status,
    summary,
    artifacts: results,
  });

  return {
    registryId: traceId,
    tenantId,
    actor,
    status,
    startedAt,
    completedAt,
    summary,
    artifacts: results,
    registryHash: registrySeal.hash,
    hashAlgorithm: registrySeal.algorithm,
  };
}

/**
 * @function sealBoardroomProof
 * @description Creates a seal-ready payload only after all sources are verified.
 * @param {object} verification - Source registry verification result.
 * @returns {object} Boardroom proof seal result.
 */
export function sealBoardroomProof(verification = {}) {
  if (verification.status !== SOURCE_STATUS.VERIFIED) {
    return {
      status: SOURCE_STATUS.BLOCKED,
      anchorStatus: 'NOT_ANCHORED',
      message:
        'Boardroom proof seal blocked until every required source returns VERIFIED evidence.',
      verificationStatus: verification.status || SOURCE_STATUS.MISSING,
      summary: verification.summary || null,
    };
  }

  const sealedAt = new Date().toISOString();
  const seal = createForensicHash({
    type: 'WILSY_BOARDROOM_SOURCE_PROOF',
    sealedAt,
    verification,
  });

  return {
    status: SOURCE_STATUS.READY_FOR_ANCHOR,
    anchorStatus: 'NOT_ANCHORED',
    message:
      'Source evidence verified. Payload is ready for vault/blockchain anchoring by the proof controller.',
    sealedAt,
    seal: seal.hash,
    hashAlgorithm: seal.algorithm,
    verificationHash: verification.registryHash,
  };
}

/**
 * @function buildInvestorPackPayload
 * @description Builds a source-backed investor pack payload without pretending to generate a PDF here.
 * @param {object} verification - Source registry verification result.
 * @returns {object} Investor pack payload.
 */
export function buildInvestorPackPayload(verification = {}) {
  const seal = sealBoardroomProof(verification);

  return {
    type: 'WILSY_INVESTOR_SOURCE_PACK',
    generatedAt: new Date().toISOString(),
    status:
      seal.status === SOURCE_STATUS.READY_FOR_ANCHOR
        ? SOURCE_STATUS.READY_FOR_ANCHOR
        : SOURCE_STATUS.BLOCKED,
    jurisdictionControls: JURISDICTION_CONTROLS,
    verification,
    boardroomSeal: seal,
  };
}

export default Object.freeze({
  HASH_ALGORITHM,
  SOURCE_STATUS,
  SOURCE_CONNECTORS,
  JURISDICTION_CONTROLS,
  ARTIFACT_SOURCE_BINDING_RULES,
  deterministicStringify,
  createForensicHash,
  normalizeArtifactText,
  resolveArtifactBinding,
  loadConnector,
  evaluateConnectorEvidence,
  verifyConnectorMethod,
  rollupStatus,
  verifyConnector,
  verifyArtifactSources,
  verifySourceRegistry,
  sealBoardroomProof,
  buildInvestorPackPayload,
});
