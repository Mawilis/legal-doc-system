/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — SOURCE REGISTRY CONTROLLER                                      ║
 * ║ VERSION: 1.0.0-PRODUCTION-NO-FAKE-DATA                                     ║
 * ║ FILE: server/controllers/sourceRegistryController.js                        ║
 * ║ PURPOSE: Orchestrate live source verification, boardroom seals and packs.   ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * @description
 * This controller is intentionally strict:
 * - It never marks anything VERIFIED by itself.
 * - It delegates source truth to server/config/sourceRegistry.js and connector services.
 * - Missing connectors remain MISSING.
 * - Incomplete connector evidence remains PENDING.
 * - Boardroom proof is BLOCKED until every required source is VERIFIED.
 * - Investor pack payloads are BLOCKED until source verification allows sealing.
 */

import crypto from 'node:crypto';
import {
  SOURCE_STATUS,
  SOURCE_CONNECTORS,
  JURISDICTION_CONTROLS,
  loadConnector,
  verifySourceRegistry as runSourceRegistryVerification,
  sealBoardroomProof as createBoardroomProofSeal,
  buildInvestorPackPayload,
  createForensicHash,
} from '../config/sourceRegistry.js';

const MAX_ARTIFACTS_PER_REQUEST = Number(process.env.WILSY_SOURCE_REGISTRY_MAX_ARTIFACTS || 250);

/**
 * @function createTraceId
 * @description Creates a source-registry trace id.
 * @returns {string} Trace id.
 */
function createTraceId() {
  return `SRC-${Date.now().toString(16).toUpperCase()}-${crypto.randomBytes(5).toString('hex').toUpperCase()}`;
}

/**
 * @function readHeader
 * @description Reads a request header using multiple possible names.
 * @param {object} req - Express request.
 * @param {Array<string>} names - Header names.
 * @returns {string} Header value.
 */
function readHeader(req = {}, names = []) {
  for (const name of names) {
    const direct = req.headers?.[name];
    const lower = req.headers?.[String(name).toLowerCase()];

    if (direct) return String(direct);
    if (lower) return String(lower);

    if (typeof req.get === 'function') {
      const value = req.get(name);
      if (value) return String(value);
    }
  }

  return '';
}

/**
 * @function resolveTenantId
 * @description Resolves tenant id from body, headers, tenant context or user context.
 * @param {object} req - Express request.
 * @returns {string} Tenant id.
 */
function resolveTenantId(req = {}) {
  return (
    String(
      req.body?.tenantId ||
        req.query?.tenantId ||
        req.tenantId ||
        req.tenant?.tenantId ||
        req.tenant?.id ||
        req.user?.tenantId ||
        req.user?.tenant ||
        readHeader(req, ['x-tenant-id', 'X-Tenant-Id', 'X-Tenant-ID']) ||
        'MASTER'
    ).trim() || 'MASTER'
  );
}

/**
 * @function resolveActor
 * @description Resolves the actor performing source-registry work.
 * @param {object} req - Express request.
 * @returns {string} Actor identifier.
 */
function resolveActor(req = {}) {
  return (
    String(
      req.body?.actor ||
        req.user?.id ||
        req.user?._id ||
        req.user?.email ||
        req.user?.username ||
        readHeader(req, ['x-actor-id', 'X-Actor-Id']) ||
        'system'
    ).trim() || 'system'
  );
}

/**
 * @function resolveTraceId
 * @description Resolves or creates a trace id.
 * @param {object} req - Express request.
 * @returns {string} Trace id.
 */
function resolveTraceId(req = {}) {
  return String(
    req.body?.traceId ||
      req.query?.traceId ||
      readHeader(req, ['x-trace-id', 'X-Trace-Id', 'x-correlation-id', 'X-Correlation-Id']) ||
      createTraceId()
  ).trim();
}

/**
 * @function buildRequestContext
 * @description Builds the normalized controller context.
 * @param {object} req - Express request.
 * @returns {{tenantId:string, actor:string, traceId:string, ip:string, userAgent:string}} Context.
 */
function buildRequestContext(req = {}) {
  return {
    tenantId: resolveTenantId(req),
    actor: resolveActor(req),
    traceId: resolveTraceId(req),
    ip: req.ip || req.connection?.remoteAddress || '',
    userAgent: readHeader(req, ['user-agent', 'User-Agent']),
  };
}

/**
 * @function sanitizeArtifact
 * @description Reduces an incoming artifact to fields required by the source registry.
 * @param {object} artifact - Artifact candidate.
 * @param {number} index - Artifact index.
 * @returns {object} Sanitized artifact.
 */
function sanitizeArtifact(artifact = {}, index = 0) {
  const safe = artifact && typeof artifact === 'object' ? artifact : {};

  return {
    id: String(safe.id || safe.type || safe.title || `artifact-${index + 1}`).trim(),
    type: String(safe.type || safe.id || safe.title || `artifact-${index + 1}`).trim(),
    title: String(
      safe.title || safe.name || safe.type || safe.id || `Artifact ${index + 1}`
    ).trim(),
    name: safe.name ? String(safe.name).trim() : undefined,
    category: safe.category ? String(safe.category).trim() : undefined,
    description: safe.description ? String(safe.description).slice(0, 2000) : undefined,

    tenantName: safe.tenantName,
    counterparty: safe.counterparty,
    counterpartyName: safe.counterpartyName,
    counterpartyEmail: safe.counterpartyEmail,
    counterpartyDomain: safe.counterpartyDomain,

    contractId: safe.contractId,
    agreementId: safe.agreementId,
    documentId: safe.documentId,
    invoiceId: safe.invoiceId,
    invoiceNumber: safe.invoiceNumber,
    customerId: safe.customerId,
    serviceName: safe.serviceName,
    environment: safe.environment,
    repository: safe.repository,
    repo: safe.repo,
    owner: safe.owner,

    employeeId: safe.employeeId,
    workerId: safe.workerId,
    employeeEmail: safe.employeeEmail,
    workEmail: safe.workEmail,
    signatoryEmail: safe.signatoryEmail,
    employeeName: safe.employeeName,
    signatoryName: safe.signatoryName,
    ipAssignmentId: safe.ipAssignmentId,
    authorityId: safe.authorityId,
    delegationId: safe.delegationId,
    boardResolutionId: safe.boardResolutionId,
  };
}

/**
 * @function extractArtifacts
 * @description Extracts artifact array from request body.
 * @param {object} req - Express request.
 * @returns {Array<object>} Sanitized artifacts.
 */
function extractArtifacts(req = {}) {
  const body = req.body || {};
  const candidates = Array.isArray(body.artifacts)
    ? body.artifacts
    : Array.isArray(body.catalog)
      ? body.catalog
      : body.artifact && typeof body.artifact === 'object'
        ? [body.artifact]
        : [];

  return candidates
    .filter((item) => item && typeof item === 'object')
    .slice(0, MAX_ARTIFACTS_PER_REQUEST)
    .map((item, index) => sanitizeArtifact(item, index));
}

/**
 * @function sendJson
 * @description Sends a normalized JSON response.
 * @param {object} res - Express response.
 * @param {number} statusCode - HTTP status code.
 * @param {object} payload - Response payload.
 * @returns {object} Express response.
 */
function sendJson(res, statusCode, payload) {
  return res.status(statusCode).json(payload);
}

/**
 * @function sendControllerError
 * @description Sends normalized controller errors without leaking secrets.
 * @param {object} res - Express response.
 * @param {object} context - Request context.
 * @param {Error} error - Error.
 * @param {number} statusCode - HTTP status code.
 * @returns {object} Express response.
 */
function sendControllerError(res, context, error, statusCode = 500) {
  const proof = createForensicHash({
    traceId: context.traceId,
    tenantId: context.tenantId,
    actor: context.actor,
    error: error.message,
    controller: 'sourceRegistryController',
  });

  return sendJson(res, statusCode, {
    success: false,
    error: {
      code: 'SOURCE_REGISTRY_CONTROLLER_ERROR',
      message: error.message,
    },
    meta: {
      traceId: context.traceId,
      tenantId: context.tenantId,
      actor: context.actor,
      hashAlgorithm: proof.algorithm,
      errorHash: proof.hash,
      generatedAt: new Date().toISOString(),
    },
  });
}

/**
 * @function auditCandidateModules
 * @description Returns possible audit logger module paths.
 * @returns {Array<string>} Module paths.
 */
function auditCandidateModules() {
  return ['../utils/auditLogger.js', '../utils/auditLogger.cjs', '../utils/logger.js'];
}

/**
 * @function callAuditLogger
 * @description Calls one detected audit logger shape safely.
 * @param {*} moduleValue - Imported module.
 * @param {object} event - Audit event.
 * @returns {Promise<boolean>} True when audit was written.
 */
async function callAuditLogger(moduleValue, event) {
  const candidate = moduleValue?.default || moduleValue;

  if (candidate && typeof candidate.log === 'function') {
    await candidate.log('source_registry', event);
    return true;
  }

  if (candidate && typeof candidate.info === 'function') {
    candidate.info('[SOURCE-REGISTRY-AUDIT]', event);
    return true;
  }

  if (candidate?.auditLogger && typeof candidate.auditLogger.log === 'function') {
    await candidate.auditLogger.log('source_registry', event);
    return true;
  }

  return false;
}

/**
 * @function writeAuditEvent
 * @description Best-effort audit logging that never blocks source verification.
 * @param {object} req - Express request.
 * @param {string} action - Audit action.
 * @param {object} details - Audit details.
 * @returns {Promise<object>} Audit result.
 */
async function writeAuditEvent(req, action, details = {}) {
  const context = buildRequestContext(req);
  const seal = createForensicHash({
    action,
    context,
    details,
    generatedAt: new Date().toISOString(),
  });

  const event = {
    action,
    domain: 'source_registry',
    timestamp: new Date().toISOString(),
    traceId: context.traceId,
    tenantId: context.tenantId,
    actor: context.actor,
    ip: context.ip,
    userAgent: context.userAgent,
    details,
    hashAlgorithm: seal.algorithm,
    eventHash: seal.hash,
  };

  for (const modulePath of auditCandidateModules()) {
    try {
      const moduleValue = await import(modulePath);
      const written = await callAuditLogger(moduleValue, event);

      if (written) {
        return {
          status: 'WRITTEN',
          modulePath,
          eventHash: seal.hash,
          hashAlgorithm: seal.algorithm,
        };
      }
    } catch {
      // Continue. Audit module may not exist or may be CommonJS-only.
    }
  }

  return {
    status: 'SKIPPED',
    reason: 'No compatible audit logger detected.',
    eventHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function rollStatus
 * @description Rolls statuses into a single summary status.
 * @param {Array<object>} items - Status-bearing items.
 * @returns {string} Rolled status.
 */
function rollStatus(items = []) {
  if (!items.length) return SOURCE_STATUS.MISSING;
  if (items.every((item) => item.status === SOURCE_STATUS.VERIFIED)) return SOURCE_STATUS.VERIFIED;
  if (items.some((item) => item.status === SOURCE_STATUS.ERROR)) return SOURCE_STATUS.ERROR;
  if (items.some((item) => item.status === SOURCE_STATUS.MISSING)) return SOURCE_STATUS.MISSING;
  return SOURCE_STATUS.PENDING;
}

/**
 * @function summarizeStatuses
 * @description Summarizes status counts.
 * @param {Array<object>} items - Status-bearing items.
 * @returns {object} Summary.
 */
function summarizeStatuses(items = []) {
  return {
    total: items.length,
    verified: items.filter((item) => item.status === SOURCE_STATUS.VERIFIED).length,
    pending: items.filter((item) => item.status === SOURCE_STATUS.PENDING).length,
    missing: items.filter((item) => item.status === SOURCE_STATUS.MISSING).length,
    error: items.filter((item) => item.status === SOURCE_STATUS.ERROR).length,
    blocked: items.filter((item) => item.status === SOURCE_STATUS.BLOCKED).length,
  };
}

/**
 * @function inspectConnector
 * @description Inspects connector installation and required method presence without verifying evidence.
 * @param {string} connectorName - Connector key.
 * @param {object} definition - Connector definition.
 * @returns {Promise<object>} Connector inspection.
 */
async function inspectConnector(connectorName, definition) {
  const loaded = await loadConnector(definition);

  if (loaded.status === SOURCE_STATUS.MISSING || loaded.status === SOURCE_STATUS.ERROR) {
    return {
      connector: connectorName,
      label: definition.label,
      modulePath: definition.modulePath,
      status: loaded.status,
      evidenceStatus: 'NOT_EVALUATED',
      message: loaded.message,
      requiredMethods: definition.requiredMethods.map((method) => ({
        method,
        installed: false,
        status: loaded.status,
      })),
    };
  }

  const requiredMethods = definition.requiredMethods.map((method) => ({
    method,
    installed: Boolean(loaded.api && typeof loaded.api[method] === 'function'),
    status:
      loaded.api && typeof loaded.api[method] === 'function'
        ? SOURCE_STATUS.PENDING
        : SOURCE_STATUS.MISSING,
  }));

  return {
    connector: connectorName,
    label: definition.label,
    modulePath: definition.modulePath,
    status: rollStatus(requiredMethods),
    evidenceStatus: 'NOT_EVALUATED',
    message: 'Connector module loaded. Evidence verification has not been run.',
    requiredMethods,
  };
}

/**
 * @function inspectSourceRegistry
 * @description Inspects source-registry installation without marking evidence verified.
 * @returns {Promise<object>} Registry inspection.
 */
async function inspectSourceRegistry() {
  const connectors = [];

  for (const [connectorName, definition] of Object.entries(SOURCE_CONNECTORS)) {
    connectors.push(await inspectConnector(connectorName, definition));
  }

  const status = rollStatus(connectors);
  const summary = summarizeStatuses(connectors);
  const seal = createForensicHash({
    type: 'SOURCE_REGISTRY_STATUS',
    status,
    summary,
    connectors,
  });

  return {
    status,
    summary,
    connectors,
    jurisdictionControls: JURISDICTION_CONTROLS,
    evidenceStatus: 'NOT_EVALUATED',
    registryHash: seal.hash,
    hashAlgorithm: seal.algorithm,
  };
}

/**
 * @function getSourceRegistryStatus
 * @description Returns connector installation status without claiming evidence verification.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} Response.
 */
export async function getSourceRegistryStatus(req, res) {
  const context = buildRequestContext(req);

  try {
    const registry = await inspectSourceRegistry();
    const audit = await writeAuditEvent(req, 'SOURCE_REGISTRY_STATUS_VIEWED', {
      registryStatus: registry.status,
      summary: registry.summary,
    });

    return sendJson(res, 200, {
      success: true,
      data: registry,
      meta: {
        traceId: context.traceId,
        tenantId: context.tenantId,
        actor: context.actor,
        audit,
        generatedAt: new Date().toISOString(),
      },
    });
  } catch (error) {
    return sendControllerError(res, context, error);
  }
}

/**
 * @function verifySources
 * @description Verifies live source evidence for supplied artifact catalog.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} Response.
 */
export async function verifySources(req, res) {
  const context = buildRequestContext(req);

  try {
    const artifacts = extractArtifacts(req);

    if (!artifacts.length) {
      return sendJson(res, 422, {
        success: false,
        error: {
          code: 'SOURCE_REGISTRY_ARTIFACTS_REQUIRED',
          message:
            'Source verification requires at least one artifact template or artifact payload.',
        },
        meta: {
          traceId: context.traceId,
          tenantId: context.tenantId,
          actor: context.actor,
          generatedAt: new Date().toISOString(),
        },
      });
    }

    const verification = await runSourceRegistryVerification({
      artifacts,
      tenantId: context.tenantId,
      actor: context.actor,
      traceId: context.traceId,
    });

    const audit = await writeAuditEvent(req, 'SOURCE_REGISTRY_VERIFIED', {
      status: verification.status,
      summary: verification.summary,
      registryHash: verification.registryHash,
    });

    return sendJson(res, 200, {
      success: true,
      data: verification,
      meta: {
        traceId: context.traceId,
        tenantId: context.tenantId,
        actor: context.actor,
        audit,
        generatedAt: new Date().toISOString(),
      },
    });
  } catch (error) {
    return sendControllerError(res, context, error);
  }
}

/**
 * @function sealBoardroomProof
 * @description Seals source proof only when supplied or freshly verified evidence is fully VERIFIED.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} Response.
 */
export async function sealBoardroomProof(req, res) {
  const context = buildRequestContext(req);

  try {
    let verification = req.body?.verification || null;

    if (!verification && extractArtifacts(req).length) {
      verification = await runSourceRegistryVerification({
        artifacts: extractArtifacts(req),
        tenantId: context.tenantId,
        actor: context.actor,
        traceId: context.traceId,
      });
    }

    if (!verification) {
      return sendJson(res, 422, {
        success: false,
        error: {
          code: 'SOURCE_REGISTRY_VERIFICATION_REQUIRED',
          message:
            'Boardroom proof sealing requires a verification payload or artifacts to verify.',
        },
        meta: {
          traceId: context.traceId,
          tenantId: context.tenantId,
          actor: context.actor,
          generatedAt: new Date().toISOString(),
        },
      });
    }

    const seal = createBoardroomProofSeal(verification);
    const audit = await writeAuditEvent(req, 'SOURCE_REGISTRY_BOARDROOM_SEAL_REQUESTED', {
      sealStatus: seal.status,
      anchorStatus: seal.anchorStatus,
      verificationStatus: verification.status,
      verificationHash: verification.registryHash,
    });

    return sendJson(res, 200, {
      success: seal.status === SOURCE_STATUS.READY_FOR_ANCHOR,
      data: seal,
      meta: {
        traceId: context.traceId,
        tenantId: context.tenantId,
        actor: context.actor,
        audit,
        generatedAt: new Date().toISOString(),
      },
    });
  } catch (error) {
    return sendControllerError(res, context, error);
  }
}

/**
 * @function exportInvestorPack
 * @description Builds source-backed investor pack payload; PDF rendering belongs to a later exporter route/service.
 * @param {object} req - Express request.
 * @param {object} res - Express response.
 * @returns {Promise<object>} Response.
 */
export async function exportInvestorPack(req, res) {
  const context = buildRequestContext(req);

  try {
    let verification = req.body?.verification || null;

    if (!verification && extractArtifacts(req).length) {
      verification = await runSourceRegistryVerification({
        artifacts: extractArtifacts(req),
        tenantId: context.tenantId,
        actor: context.actor,
        traceId: context.traceId,
      });
    }

    if (!verification) {
      return sendJson(res, 422, {
        success: false,
        error: {
          code: 'SOURCE_REGISTRY_VERIFICATION_REQUIRED',
          message: 'Investor pack export requires a verification payload or artifacts to verify.',
        },
        meta: {
          traceId: context.traceId,
          tenantId: context.tenantId,
          actor: context.actor,
          generatedAt: new Date().toISOString(),
        },
      });
    }

    const investorPack = buildInvestorPackPayload(verification);
    const audit = await writeAuditEvent(req, 'SOURCE_REGISTRY_INVESTOR_PACK_BUILT', {
      status: investorPack.status,
      verificationStatus: verification.status,
      verificationHash: verification.registryHash,
      boardroomSealStatus: investorPack.boardroomSeal?.status,
    });

    return sendJson(res, 200, {
      success: investorPack.status === SOURCE_STATUS.READY_FOR_ANCHOR,
      data: investorPack,
      meta: {
        traceId: context.traceId,
        tenantId: context.tenantId,
        actor: context.actor,
        audit,
        generatedAt: new Date().toISOString(),
      },
    });
  } catch (error) {
    return sendControllerError(res, context, error);
  }
}

export default Object.freeze({
  getSourceRegistryStatus,
  verifySources,
  sealBoardroomProof,
  exportInvestorPack,
});
