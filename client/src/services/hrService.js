/**
 * TITLE: WILSY OS Tenant-Scoped HR Client Transport
 * VERSION: v1.9.0-CANDIDATE-EVIDENCE-CUSTODY-TRANSPORT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Transports HR reads and commands while preserving unavailable-source
 *          failures as errors and reserving all business authority for Python EOS.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/hrService.js
 * COLLABORATION / OWNERSHIP: Consumed by HrDashboard; shared API, telemetry,
 *                            logger and retry/circuit utilities remain upstream.
 * CERTIFICATION / UPDATE DATE: 2026-11-12
 * CHANGELOG:
 *   v1.9.0-CANDIDATE-EVIDENCE-CUSTODY-TRANSPORT — Adds authenticated raw-binary candidate-evidence upload and exact-version integrity-read adapters; callers must verify upload receipts by source readback.
 *   v1.8.0-EOS-HIRING-COMMAND-TRANSPORT — Adds exact-tenant, caller-idempotent adapters for existing EOS candidate and offer lifecycle commands without automatic mutation retries.
 *   v1.7.0-CANONICAL-HIRING-PAGE-READS — Adds read-only adapters for the canonical Python EOS candidate and offer pages.
 *   v1.6.0-STRICT-HR-PAGE-ENVELOPES — Requires all pagination metadata on object responses; incomplete pages reject instead of deriving an authoritative zero.
 *   v1.5.0-FAILURE-TRANSPARENT-READS — Requires explicit tenant scope, rejects
 *     unavailable/open-circuit/malformed reads instead of returning empty pages,
 *     and keeps business payloads out of failure telemetry.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Exact tenant is mandatory; errors and telemetry omit
 *                             search text, evidence bytes and HR payloads. Evidence
 *                             streams are never persisted or treated as verified until
 *                             the authenticated EOS exact-version read succeeds.
 * TENANT BOUNDARY: Every request carries one nonempty tenant identifier. Python EOS
 *                  independently authenticates and authorizes that exact tenant.
 * AUTHORITY BOUNDARY: Transport only; no HR, hiring, employment, IAM or payroll
 *                     business authority is created in this module.
 * FINANCIAL AUTHORITY BOUNDARY: No execution or settlement authority; Kennel EOS
 *                               remains exclusively responsible for financial execution.
 */
/* eslint-disable */
import api from './api';
import { broadcastTelemetry } from '../utils/telemetryHelper';
import logger from '../utils/logger';
import { TEL_EVENTS } from '../constants/telemetryConstants';
import {
  withBackoff,
  isTransient,
  createCircuitBreaker
} from '../utils/backoff';

/**
 * HR request circuit breaker shared across this legacy client transport.
 * An open circuit is unavailable source evidence and is always raised to callers.
 */
const hrCircuit = createCircuitBreaker({
  name: 'hr-api',
  failureThreshold: 2,
  coolDownMs: 60_000
});

/**
 * @description Requires an explicit exact tenant identifier for every HR request.
 * @collaboration All private GET and mutation transport helpers.
 * @institutional Prevents absent browser scope from becoming a root or default tenant.
 * @param {unknown} tenantId - Caller tenant candidate.
 * @returns {string} Validated nonempty exact tenant identifier.
 * @throws {Error} HR_TENANT_SCOPE_REQUIRED when scope is absent or malformed.
 */
const requireTenantScope = (tenantId) => {
  if (
    typeof tenantId !== 'string'
    || tenantId.length === 0
    || tenantId !== tenantId.trim()
  ) {
    const error = new Error('HR_TENANT_SCOPE_REQUIRED');
    error.code = 'HR_TENANT_SCOPE_REQUIRED';
    error.status = 403;
    throw error;
  }
  return tenantId;
};

/**
 * @description Creates a stable transport-contract error without including HR data.
 * @collaboration Read validation and circuit-open handling.
 * @institutional Callers need machine-readable failure truth to render unavailable state.
 * @param {string} code - Stable uppercase error code.
 * @param {number} status - HTTP-equivalent status for client handling.
 * @param {Error} [cause] - Original transport or response error.
 * @returns {Error} Structured client transport error.
 */
const createHrTransportError = (code, status, cause) => {
  const error = new Error(code);
  error.code = code;
  error.status = status;
  if (cause) error.cause = cause;
  return error;
};

/**
 * @description Copies a command body while removing prototype mutation keys.
 * @collaboration Private POST and PUT transport helpers.
 * @institutional Keeps caller data from altering object prototypes before transport.
 * @param {Object} payload - Caller-owned request body.
 * @returns {Object} Safe shallow copy with undefined values omitted.
 */
const sanitizePayload = (payload) => {
  if (!payload || typeof payload !== 'object') return payload;
  return Object.keys(payload).reduce((safe, key) => {
    if (key === '__proto__' || key === 'constructor') return safe;
    if (payload[key] !== undefined) safe[key] = payload[key];
    return safe;
  }, {});
};

/**
 * @description Emits best-effort telemetry after source results without changing command truth.
 * @collaboration HR transport reads and mutations.
 * @institutional A telemetry outage cannot turn a completed EOS command into a false failure.
 * @param {...any} args - Existing broadcastTelemetry arguments.
 * @returns {Promise<void>} Settled telemetry attempt.
 */
const emitTelemetry = async (...args) => {
  try {
    await broadcastTelemetry(...args);
  } catch {
    // Source response and durable command outcome remain authoritative.
  }
};

/**
 * @description Records only bounded source failure metadata and tenant-scoped telemetry.
 * @collaboration HR transport read and mutation error handlers.
 * @institutional Failure evidence must not copy candidate, employee, search or command payloads.
 * @param {Error} error - Source or transport failure.
 * @param {string} context - Endpoint operation label.
 * @param {string} tenantId - Exact requested tenant.
 * @param {string} failureEvent - HR failure event key.
 * @returns {Promise<void>} Settled diagnostic attempt.
 */
const softLogError = async (error, context, tenantId, failureEvent) => {
  const status = Number.isInteger(error?.response?.status)
    ? error.response.status
    : Number.isInteger(error?.status) ? error.status : undefined;
  const candidateCode = error?.code;
  const errorCode = typeof candidateCode === 'string'
    && /^[A-Z0-9_.-]{1,80}$/.test(candidateCode)
    ? candidateCode
    : status ? `HTTP_${status}` : 'HR_API_REQUEST_FAILED';

  if (import.meta.env.DEV) {
    try {
      logger.error?.('[hrService] source request failed', { context, status, errorCode });
    } catch {
      // Diagnostic output is optional and contains no business payload.
    }
  }

  await emitTelemetry(tenantId, failureEvent, 'FRACTURE', context, {
    errorCode,
    status,
    circuit: hrCircuit.getState()
  });
};

/**
 * @description Reads one bounded HR page and preserves HTTP, network and source-contract failures.
 * @collaboration HrDashboard read adapters and exact-tenant HR client consumers.
 * @institutional A real empty EOS result is distinct from unavailable, denied or malformed truth.
 * @param {string} endpoint - API path relative to the shared /api base URL.
 * @param {string} tenantId - Exact authenticated tenant supplied by the caller.
 * @param {Object} params - Bounded paging and search inputs.
 * @param {string} successEvent - Telemetry event for a verified response.
 * @param {string} failureEvent - Telemetry event for source failure.
 * @returns {Promise<Object>} Validated paginated source response, including genuine empty results.
 * @throws {Error} Tenant scope, circuit, authorization, transport or response-contract failure.
 */
const getResource = async (endpoint, tenantId, params = {}, successEvent, failureEvent) => {
  const scopedTenantId = requireTenantScope(tenantId);
  if (!hrCircuit.allow()) {
    const error = createHrTransportError('HR_API_CIRCUIT_OPEN', 503);
    await softLogError(error, `get${endpoint}`, scopedTenantId, failureEvent);
    throw error;
  }

  try {
    const response = await withBackoff(
      () => api.get(endpoint, {
        params: { tenantId: scopedTenantId, ...params },
        headers: { 'X-Tenant-ID': scopedTenantId }
      }),
      {
        maxAttempts: 3,
        baseMs: 300,
        maxMs: 8_000,
        retryIf: (error) => {
          const status = error?.response?.status;
          if (status === 404 || status === 401 || status === 403) return false;
          return isTransient(error);
        },
        onRetry: ({ attempt, delay }) => {
          if (import.meta.env.DEV) {
            console.debug(`[hrService] retry ${endpoint} attempt=${attempt + 1} delay=${delay}ms`);
          }
        }
      }
    );

    const data = response?.data;
    const items = Array.isArray(data)
      ? data
      : data && typeof data === 'object'
        ? (Array.isArray(data.items)
          ? data.items
          : Array.isArray(data.data) ? data.data : null)
        : null;
    if (!items) {
      throw createHrTransportError('HR_SOURCE_RESPONSE_INVALID', 502);
    }

    const total = Array.isArray(data) ? items.length : data.total;
    const limit = Array.isArray(data) ? (params.limit ?? 50) : data.limit;
    const offset = Array.isArray(data) ? (params.offset ?? 0) : data.offset;
    const hasMore = Array.isArray(data)
      ? offset + items.length < total
      : data.hasMore;
    if (
      !Number.isSafeInteger(total) || total < items.length
      || !Number.isSafeInteger(limit) || limit < 1
      || !Number.isSafeInteger(offset) || offset < 0
      || typeof hasMore !== 'boolean'
    ) {
      throw createHrTransportError('HR_SOURCE_RESPONSE_INVALID', 502);
    }

    hrCircuit.success();
    await emitTelemetry(scopedTenantId, successEvent, 'SUCCESS', `get${endpoint}`, {
      count: items.length,
      total,
      hasMore
    });
    return { items, total, limit, offset, hasMore, skipped: false };
  } catch (error) {
    const status = Number.isInteger(error?.response?.status)
      ? error.response.status
      : Number.isInteger(error?.status) ? error.status : undefined;
    const reason = status ? `HTTP_${status}` : 'NETWORK_OR_SOURCE_FAILURE';

    if ([404, 502, 503].includes(status) || !status) {
      hrCircuit.trip(60_000, reason);
    } else if (status === 401 || status === 403) {
      // Authentication denial is not a transport outage; leave the circuit usable.
      hrCircuit.success();
    } else {
      hrCircuit.failure(reason);
    }

    await softLogError(error, `get${endpoint}`, scopedTenantId, failureEvent);
    throw error;
  }
};

/**
 * @description Returns validated records from the shared tenant-scoped page contract.
 * @collaboration HR dropdown and list consumers.
 * @institutional Array convenience never converts a source failure to an empty list.
 * @param {string} endpoint - API path relative to the shared /api base URL.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {Object} params - Bounded request parameters.
 * @returns {Promise<Array>} Source-owned records, possibly genuinely empty.
 * @throws {Error} On absent scope or any unavailable/invalid source response.
 */
const getResourceArray = async (endpoint, tenantId, params = {}) => {
  const { items } = await getResource(
    endpoint,
    tenantId,
    params,
    TEL_EVENTS.HR.HYDRATION_SUCCESS,
    TEL_EVENTS.HR.HYDRATION_FRACTURE
  );
  return items;
};

/**
 * @description Sends one tenant-scoped HR create command through the shared API client.
 * @collaboration HR mutation forms; Python EOS must authorize and persist the command.
 * @institutional This transport owns no authorization, transaction or idempotency authority.
 * @param {string} endpoint - API path relative to the shared /api base URL.
 * @param {Object} data - Caller command body, prototype-pollution keys removed.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} successEvent - Post-response telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<Object>} Source response body.
 * @throws {Error} Tenant, authorization, transport or source command failure.
 */
const postResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const scopedTenantId = requireTenantScope(tenantId);
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.post(endpoint, sanitized, {
      headers: { 'X-Tenant-ID': scopedTenantId }
    });
    await emitTelemetry(scopedTenantId, successEvent, 'SUCCESS', 'HR_POST_COMPLETED', {});
    return response?.data;
  } catch (error) {
    await softLogError(error, 'HR_POST_FAILED', scopedTenantId, failureEvent);
    throw error;
  }
};

/**
 * @description Sends one tenant-scoped HR update command through the shared API client.
 * @collaboration HR mutation forms; Python EOS must authorize and persist the command.
 * @institutional This transport owns no authorization, transaction or idempotency authority.
 * @param {string} endpoint - API path relative to the shared /api base URL.
 * @param {Object} data - Caller command body, prototype-pollution keys removed.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} successEvent - Post-response telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<Object>} Source response body.
 * @throws {Error} Tenant, authorization, transport or source command failure.
 */
const putResource = async (endpoint, data, tenantId, successEvent, failureEvent) => {
  const scopedTenantId = requireTenantScope(tenantId);
  const sanitized = sanitizePayload(data);
  try {
    const response = await api.put(endpoint, sanitized, {
      headers: { 'X-Tenant-ID': scopedTenantId }
    });
    await emitTelemetry(scopedTenantId, successEvent, 'SUCCESS', 'HR_PUT_COMPLETED', {});
    return response?.data;
  } catch (error) {
    await softLogError(error, 'HR_PUT_FAILED', scopedTenantId, failureEvent);
    throw error;
  }
};

/**
 * @description Sends one tenant-scoped HR delete command through the shared API client.
 * @collaboration HR list actions; Python EOS must authorize and persist the command.
 * @institutional This transport owns no authorization, transaction or idempotency authority.
 * @param {string} endpoint - API path relative to the shared /api base URL.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} successEvent - Post-response telemetry event.
 * @param {string} failureEvent - Failure telemetry event.
 * @returns {Promise<void>} Completion after source HTTP acknowledgement.
 * @throws {Error} Tenant, authorization, transport or source command failure.
 */
const deleteResource = async (endpoint, tenantId, successEvent, failureEvent) => {
  const scopedTenantId = requireTenantScope(tenantId);
  try {
    await api.delete(endpoint, { headers: { 'X-Tenant-ID': scopedTenantId } });
    await emitTelemetry(scopedTenantId, successEvent, 'SUCCESS', 'HR_DELETE_COMPLETED', {});
  } catch (error) {
    await softLogError(error, 'HR_DELETE_FAILED', scopedTenantId, failureEvent);
    throw error;
  }
};

// ─── Employees ───────────────────────────────────────────────────────────────
/**
 * @description Reads the tenant employee page.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getEmployees = (tenantId, params = {}) =>
  getResource('/hr/employees', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * @description Reads tenant employee records as an array.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Array>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getEmployeesArray = (tenantId, params = {}) => getResourceArray('/hr/employees', tenantId, params);

/**
 * @description Submits an employee create command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const createEmployee = (data, tenantId) =>
  postResource('/hr/employees', data, tenantId, TEL_EVENTS.HR.EMPLOYEE_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits an employee update command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const updateEmployee = (id, data, tenantId) =>
  putResource(`/hr/employees/${id}`, data, tenantId, TEL_EVENTS.HR.EMPLOYEE_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits an employee delete command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<void>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const deleteEmployee = (id, tenantId) =>
  deleteResource(`/hr/employees/${id}`, tenantId, TEL_EVENTS.HR.EMPLOYEE_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Recruitment ─────────────────────────────────────────────────────────────
/**
 * @description Reads the tenant recruitment candidate page.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getRecruitmentCandidates = (tenantId, params = {}) =>
  getResource('/hr/recruitment/candidates', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * @description Reads a bounded candidate page from the canonical Python EOS hiring lifecycle.
 * @collaboration HrDashboard's candidate pipeline read adapter.
 * @institutional Uses existing exact-tenant HR hiring read authority; transport grants no capability.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {{limit?:number,offset?:number}} params - Bounded page coordinates.
 * @returns {Promise<Object>} Strictly validated source page, including verified empty pages.
 * @throws {Error} On missing scope, EOS denial, unavailable source, open circuit, or malformed response.
 */
export const getHiringCandidates = (tenantId, params = {}) =>
  getResource(
    '/hr/hiring/candidates',
    tenantId,
    { limit: params.limit, offset: params.offset },
    TEL_EVENTS.HR.HYDRATION_SUCCESS,
    TEL_EVENTS.HR.HYDRATION_FRACTURE
  );

/**
 * @description Reads a bounded employment-offer page from the canonical Python EOS hiring lifecycle.
 * @collaboration HrDashboard's offer pipeline read adapter.
 * @institutional EOS independently enforces the existing offer-read capability for exact tenant scope.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {{limit?:number,offset?:number}} params - Bounded page coordinates.
 * @returns {Promise<Object>} Strictly validated source page, including verified empty pages.
 * @throws {Error} On missing scope, EOS denial, unavailable source, open circuit, or malformed response.
 */
export const getHiringOffers = (tenantId, params = {}) =>
  getResource(
    '/hr/hiring/offers',
    tenantId,
    { limit: params.limit, offset: params.offset },
    TEL_EVENTS.HR.HYDRATION_SUCCESS,
    TEL_EVENTS.HR.HYDRATION_FRACTURE
  );

/**
 * @description Validates a caller-owned idempotency key for an EOS hiring mutation.
 * @collaboration Canonical candidate and offer command adapters.
 * @institutional Stable retries are explicit caller behavior; transport never resends a mutation automatically.
 * @param {unknown} value - Caller generated opaque command key.
 * @returns {string} Validated idempotency key.
 * @throws {Error} HR_HIRING_IDEMPOTENCY_KEY_REQUIRED when the key is absent or invalid.
 */
const requireHiringIdempotencyKey = (value) => {
  if (
    typeof value !== 'string' || value.length < 1 || value.length > 160
    || value !== value.trim() || /[\u0000-\u001f\u007f]/.test(value)
  ) {
    const error = createHrTransportError('HR_HIRING_IDEMPOTENCY_KEY_REQUIRED', 400);
    throw error;
  }
  return value;
};

/**
 * @description Sends one canonical EOS hiring command with exact tenant and idempotency headers.
 * @collaboration Exported candidate and offer lifecycle mutation adapters.
 * @institutional EOS owns capability checks, validation, transactions, durable replay and business truth; this transport deliberately does not retry mutations.
 * @param {string} endpoint - Existing Python EOS path relative to the shared /api base URL.
 * @param {Object} payload - Strict EOS command body with prototype mutation keys removed.
 * @param {string} tenantId - Exact authenticated tenant supplied by the caller.
 * @param {string} idempotencyKey - Stable key reused only for an exact same-command retry.
 * @param {Object} [headers] - Additional source-defined command headers such as Expected-Revision.
 * @returns {Promise<Object>} Source acknowledgement; callers must independently read back durable state.
 * @throws {Error} On missing scope/key, EOS denial, network failure or source rejection.
 */
const postHiringCommand = async (
  endpoint, payload, tenantId, idempotencyKey, headers = {},
) => {
  const scopedTenantId = requireTenantScope(tenantId);
  const commandKey = requireHiringIdempotencyKey(idempotencyKey);
  try {
    const response = await api.post(endpoint, sanitizePayload(payload || {}), {
      headers: {
        'X-Tenant-ID': scopedTenantId,
        'Idempotency-Key': commandKey,
        ...headers,
      },
    });
    // An HTTP acknowledgement is not durable lifecycle readback; do not emit a success event here.
    return response?.data;
  } catch (error) {
    await softLogError(error, 'EOS_HIRING_COMMAND_FAILED', scopedTenantId, TEL_EVENTS.HR.ACTION_FRACTURE);
    throw error;
  }
};

/**
 * @description Creates an EOS candidate application using an opaque profile reference.
 * @collaboration HR hiring candidate intake.
 * @institutional The exact tenant and actor are derived again by EOS; no applicant PII or tenant authority is inferred here.
 * @param {Object} data - Canonical candidate_id, requisition_id, candidate_profile_reference and source command.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} idempotencyKey - Stable exact-command retry key.
 * @returns {Promise<Object>} EOS acknowledgement requiring tenant-scoped durable readback.
 * @throws {Error} On scope, key, network, EOS authorization or source failure.
 */
export const createHiringCandidate = (data, tenantId, idempotencyKey) =>
  postHiringCommand('/hr/hiring/candidates', data, tenantId, idempotencyKey);

/**
 * @description Advances one candidate using evidence and expected-revision control.
 * @collaboration HR candidate pipeline command surface.
 * @institutional EOS validates candidate state, evidence, actor capability, revision and durable replay.
 * @param {string} candidateId - Exact candidate identifier from the current tenant source page.
 * @param {Object} data - expected_revision, target_stage, reason, evidence_reference and evidence_fingerprint.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} idempotencyKey - Stable exact-command retry key.
 * @returns {Promise<Object>} EOS acknowledgement requiring tenant-scoped durable readback.
 * @throws {Error} On invalid inputs, denial, network failure or source rejection.
 */
export const transitionHiringCandidate = (candidateId, data, tenantId, idempotencyKey) =>
  postHiringCommand(
    `/hr/hiring/candidates/${encodeURIComponent(candidateId)}/transition`,
    data, tenantId, idempotencyKey,
  );

/**
 * @description Uploads one candidate evidence object to the authenticated EOS custody route.
 * @collaboration HR hiring evidence preparation and candidate-stage transition workflow.
 * @institutional The Python EOS provider inspector and custody registry own object verification; this adapter never retries an uncertain stream.
 * @param {string} candidateId - Exact candidate identity from the current tenant source page.
 * @param {string} evidenceId - Caller-selected opaque evidence identity.
 * @param {string} evidenceVersionId - Caller-selected immutable evidence version identity.
 * @param {Blob} file - In-memory binary object; it is streamed and never written to browser storage.
 * @param {{mediaType:string,originalFilename:string,evidenceKind?:string,offerId?:string}} metadata - Source-defined evidence metadata.
 * @param {string} tenantId - Exact authenticated tenant.
 * @returns {Promise<Object>} EOS custody receipt that remains unverified until exact-version readback.
 * @throws {Error} On invalid metadata, tenant denial, uncertain upload, provider failure or malformed receipt.
 */
export const uploadHiringCandidateEvidence = async (
  candidateId, evidenceId, evidenceVersionId, file, metadata, tenantId,
) => {
  const scopedTenantId = requireTenantScope(tenantId);
  const identityPattern = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$/;
  for (const [label, value] of Object.entries({ candidateId, evidenceId, evidenceVersionId })) {
    if (typeof value !== 'string' || !identityPattern.test(value)) {
      throw createHrTransportError(`HR_EVIDENCE_${label.toUpperCase()}_INVALID`, 400);
    }
  }
  const isBinary = typeof Blob !== 'undefined' && file instanceof Blob;
  if (!isBinary || file.size < 1 || file.size > 100 * 1024 * 1024) {
    throw createHrTransportError('HR_EVIDENCE_FILE_INVALID', 400);
  }
  const mediaType = metadata?.mediaType;
  const originalFilename = metadata?.originalFilename;
  const evidenceKind = metadata?.evidenceKind || 'CANDIDATE_PROFILE';
  const offerId = metadata?.offerId;
  if (
    typeof mediaType !== 'string' || !/^[A-Za-z0-9.+-]+[/][A-Za-z0-9.+-]+$/.test(mediaType)
    || typeof originalFilename !== 'string' || originalFilename.length < 1
    || originalFilename.length > 255 || !/^[ -~]+$/.test(originalFilename)
    || !['CANDIDATE_PROFILE', 'SIGNED_OFFER'].includes(evidenceKind)
    || (evidenceKind === 'SIGNED_OFFER' && (typeof offerId !== 'string' || !identityPattern.test(offerId)))
    || (evidenceKind === 'CANDIDATE_PROFILE' && offerId !== undefined)
  ) {
    throw createHrTransportError('HR_EVIDENCE_METADATA_INVALID', 400);
  }
  const endpoint = `/hr/hiring/candidates/${encodeURIComponent(candidateId)}/evidence/${encodeURIComponent(evidenceId)}/${encodeURIComponent(evidenceVersionId)}`;
  try {
    const response = await api.put(endpoint, file, {
      headers: {
        'X-Tenant-ID': scopedTenantId,
        'X-Evidence-Media-Type': mediaType,
        'X-Evidence-Filename': originalFilename,
        'X-Evidence-Kind': evidenceKind,
        ...(offerId ? { 'X-Offer-Id': offerId } : {}),
      },
    });
    const receipt = response?.data;
    if (
      receipt?.status !== 'CUSTODY_REGISTERED' || receipt?.custody_registered !== true
      || receipt?.candidate_id !== candidateId || receipt?.evidence_id !== evidenceId
      || receipt?.evidence_version_id !== evidenceVersionId || receipt?.byte_length !== file.size
      || typeof receipt?.content_digest_sha3_512 !== 'string'
      || !/^[0-9a-f]{128}$/.test(receipt.content_digest_sha3_512)
    ) {
      throw createHrTransportError('HR_EVIDENCE_CUSTODY_RECEIPT_INVALID', 502);
    }
    return receipt;
  } catch (error) {
    await softLogError(error, 'EOS_CANDIDATE_EVIDENCE_UPLOAD_FAILED', scopedTenantId, TEL_EVENTS.HR.ACTION_FRACTURE);
    throw error;
  }
};

/**
 * @description Reads an exact candidate evidence version through EOS and validates source integrity metadata.
 * @collaboration Candidate evidence custody workflow before any stage transition.
 * @institutional EOS rechecks tenant custody and provider bytes; successful readback is required before the UI treats a receipt as verified.
 * @param {string} candidateId - Exact candidate identity.
 * @param {string} evidenceId - Exact immutable evidence identity.
 * @param {string} evidenceVersionId - Exact immutable evidence version.
 * @param {string} tenantId - Exact authenticated tenant.
 * @returns {Promise<{blob:Blob,contentDigestSha3_512:string,contentLength:number}>} Authenticated binary readback and EOS digest metadata.
 * @throws {Error} On denial, unavailable storage, malformed response, invalid digest or size mismatch.
 */
export const readHiringCandidateEvidence = async (
  candidateId, evidenceId, evidenceVersionId, tenantId,
) => {
  const scopedTenantId = requireTenantScope(tenantId);
  const identityPattern = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$/;
  for (const [label, value] of Object.entries({ candidateId, evidenceId, evidenceVersionId })) {
    if (typeof value !== 'string' || !identityPattern.test(value)) {
      throw createHrTransportError(`HR_EVIDENCE_${label.toUpperCase()}_INVALID`, 400);
    }
  }
  try {
    const response = await api.get(
      `/hr/hiring/candidates/${encodeURIComponent(candidateId)}/evidence/${encodeURIComponent(evidenceId)}/${encodeURIComponent(evidenceVersionId)}`,
      { responseType: 'blob', headers: { 'X-Tenant-ID': scopedTenantId } },
    );
    const blob = response?.data;
    const headers = response?.headers;
    const getHeader = (name) => typeof headers?.get === 'function'
      ? headers.get(name)
      : headers?.[name.toLowerCase()] ?? headers?.[name];
    const digest = getHeader('X-Content-Digest-SHA3-512');
    const contentLength = Number(getHeader('Content-Length'));
    if (
      typeof Blob === 'undefined' || !(blob instanceof Blob) || blob.size < 1
      || typeof digest !== 'string' || !/^[0-9a-f]{128}$/.test(digest)
      || !Number.isSafeInteger(contentLength) || contentLength !== blob.size
    ) {
      throw createHrTransportError('HR_EVIDENCE_READBACK_INVALID', 502);
    }
    return { blob, contentDigestSha3_512: digest, contentLength };
  } catch (error) {
    await softLogError(error, 'EOS_CANDIDATE_EVIDENCE_READBACK_FAILED', scopedTenantId, TEL_EVENTS.HR.ACTION_FRACTURE);
    throw error;
  }
};

/**
 * @description Creates an offer for an EOS-selected candidate within the exact tenant.
 * @collaboration HR employment-offer preparation.
 * @institutional EOS validates candidate stage and tenant before recording offer terms; client transport creates no offer authority.
 * @param {Object} data - Canonical offer identity, candidate/requisition links and terms.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} idempotencyKey - Stable exact-command retry key.
 * @returns {Promise<Object>} EOS acknowledgement requiring tenant-scoped durable readback.
 * @throws {Error} On scope, key, authorization, network or source failure.
 */
export const createHiringOffer = (data, tenantId, idempotencyKey) =>
  postHiringCommand('/hr/hiring/offers', data, tenantId, idempotencyKey);

/**
 * @description Submits a prepared offer for independent EOS approval.
 * @collaboration HR offer approval workflow.
 * @institutional The source checks expected revision and distinct submit capability.
 * @param {string} offerId - Exact offer identifier from the current tenant page.
 * @param {number} expectedRevision - Current verified source revision.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} idempotencyKey - Stable exact-command retry key.
 * @returns {Promise<Object>} EOS acknowledgement requiring tenant-scoped durable readback.
 * @throws {Error} On invalid inputs, denial, network failure or source rejection.
 */
export const submitHiringOffer = (offerId, expectedRevision, tenantId, idempotencyKey) => {
  if (!Number.isSafeInteger(expectedRevision) || expectedRevision < 1) {
    throw createHrTransportError('HR_HIRING_EXPECTED_REVISION_INVALID', 400);
  }
  return postHiringCommand(
    `/hr/hiring/offers/${encodeURIComponent(offerId)}/submit`, {}, tenantId, idempotencyKey,
    { 'Expected-Revision': String(expectedRevision) },
  );
};

/**
 * @description Records a separate EOS approval or rejection decision for one offer revision.
 * @collaboration HR offer maker-checker decision workflow.
 * @institutional EOS applies independent decision authority and durable audit evidence.
 * @param {string} offerId - Exact offer identifier from the current tenant page.
 * @param {Object} data - expected_revision, approved and decision reason.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} idempotencyKey - Stable exact-command retry key.
 * @returns {Promise<Object>} EOS acknowledgement requiring tenant-scoped durable readback.
 * @throws {Error} On invalid inputs, denial, network failure or source rejection.
 */
export const decideHiringOffer = (offerId, data, tenantId, idempotencyKey) =>
  postHiringCommand(
    `/hr/hiring/offers/${encodeURIComponent(offerId)}/decision`, data,
    tenantId, idempotencyKey,
  );

/**
 * @description Sends an independently approved offer at its verified current revision.
 * @collaboration HR offer delivery workflow.
 * @institutional EOS enforces offer state, revision and distinct send capability; this transport does not mark acceptance or employment.
 * @param {string} offerId - Exact offer identifier from the current tenant page.
 * @param {number} expectedRevision - Current verified source revision.
 * @param {string} tenantId - Exact authenticated tenant.
 * @param {string} idempotencyKey - Stable exact-command retry key.
 * @returns {Promise<Object>} EOS acknowledgement requiring tenant-scoped durable readback.
 * @throws {Error} On invalid inputs, denial, network failure or source rejection.
 */
export const sendHiringOffer = (offerId, expectedRevision, tenantId, idempotencyKey) => {
  if (!Number.isSafeInteger(expectedRevision) || expectedRevision < 1) {
    throw createHrTransportError('HR_HIRING_EXPECTED_REVISION_INVALID', 400);
  }
  return postHiringCommand(
    `/hr/hiring/offers/${encodeURIComponent(offerId)}/send`, {}, tenantId, idempotencyKey,
    { 'Expected-Revision': String(expectedRevision) },
  );
};

/**
 * @description Submits a candidate create command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const createCandidate = (data, tenantId) =>
  postResource('/hr/recruitment/candidates', data, tenantId, TEL_EVENTS.HR.CANDIDATE_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a candidate stage transition to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} stage - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const updateCandidateStage = (id, stage, tenantId) =>
  putResource(`/hr/recruitment/candidates/${id}/stage`, { stage }, tenantId, TEL_EVENTS.HR.RECRUITMENT_STAGE_CHANGE, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a candidate delete command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<void>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const deleteCandidate = (id, tenantId) =>
  deleteResource(`/hr/recruitment/candidates/${id}`, tenantId, TEL_EVENTS.HR.CANDIDATE_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Reads the tenant job-opening page.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getJobOpenings = (tenantId, params = {}) =>
  getResource('/hr/recruitment/openings', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * @description Submits a job-opening create command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const createJobOpening = (data, tenantId) =>
  postResource('/hr/recruitment/openings', data, tenantId, TEL_EVENTS.HR.JOB_OPENING_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a job-opening update command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const updateJobOpening = (id, data, tenantId) =>
  putResource(`/hr/recruitment/openings/${id}`, data, tenantId, TEL_EVENTS.HR.JOB_OPENING_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a job-opening delete command to the configured HR route.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<void>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const deleteJobOpening = (id, tenantId) =>
  deleteResource(`/hr/recruitment/openings/${id}`, tenantId, TEL_EVENTS.HR.JOB_OPENING_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Payroll ─────────────────────────────────────────────────────────────────
/**
 * @description Reads the tenant payroll summary.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getPayrollSummary = (tenantId, params = {}) =>
  getResource('/hr/payroll/summary', tenantId, params, TEL_EVENTS.HR.PAYROLL_SYNC_SUCCESS, TEL_EVENTS.HR.PAYROLL_SYNC_FRACTURE);

/**
 * @description Submits the configured tenant payroll synchronization command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const syncPayroll = (tenantId) =>
  postResource('/hr/payroll/sync', {}, tenantId, TEL_EVENTS.HR.PAYROLL_SYNC_SUCCESS, TEL_EVENTS.HR.PAYROLL_SYNC_FRACTURE);

// ─── Benefits ─────────────────────────────────────────────────────────────────
/**
 * @description Reads the tenant benefits page.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getBenefits = (tenantId, params = {}) =>
  getResource('/hr/benefits', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * @description Submits a tenant benefit create command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const createBenefit = (data, tenantId) =>
  postResource('/hr/benefits', data, tenantId, TEL_EVENTS.HR.BENEFIT_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a tenant benefit update command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const updateBenefit = (id, data, tenantId) =>
  putResource(`/hr/benefits/${id}`, data, tenantId, TEL_EVENTS.HR.BENEFIT_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a tenant benefit delete command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<void>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const deleteBenefit = (id, tenantId) =>
  deleteResource(`/hr/benefits/${id}`, tenantId, TEL_EVENTS.HR.BENEFIT_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Performance ─────────────────────────────────────────────────────────────
/**
 * @description Reads the tenant performance-review page.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getPerformanceReviews = (tenantId, params = {}) =>
  getResource('/hr/performance', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * @description Submits a performance-review create command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const createPerformanceReview = (data, tenantId) =>
  postResource('/hr/performance', data, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_CREATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a performance-review update command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const updatePerformanceReview = (id, data, tenantId) =>
  putResource(`/hr/performance/${id}`, data, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_UPDATED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a performance-review delete command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<void>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const deletePerformanceReview = (id, tenantId) =>
  deleteResource(`/hr/performance/${id}`, tenantId, TEL_EVENTS.HR.PERFORMANCE_REVIEW_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Time-off ─────────────────────────────────────────────────────────────────
/**
 * @description Reads the tenant time-off request page.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @param {Object} params - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const getTimeOffRequests = (tenantId, params = {}) =>
  getResource('/hr/timeoff', tenantId, params, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.HYDRATION_FRACTURE);

/**
 * @description Submits a tenant time-off request command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const createTimeOffRequest = (data, tenantId) =>
  postResource('/hr/timeoff', data, tenantId, TEL_EVENTS.HR.TIME_OFF_REQUESTED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a tenant time-off update command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {Object} data - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const updateTimeOffRequest = (id, data, tenantId) =>
  putResource(`/hr/timeoff/${id}`, data, tenantId, TEL_EVENTS.HR.HYDRATION_SUCCESS, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a tenant time-off approval command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const approveTimeOff = (id, tenantId) =>
  putResource(`/hr/timeoff/${id}/approve`, {}, tenantId, TEL_EVENTS.HR.TIME_OFF_APPROVED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a tenant time-off denial command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<Object>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const denyTimeOff = (id, tenantId) =>
  putResource(`/hr/timeoff/${id}/deny`, {}, tenantId, TEL_EVENTS.HR.TIME_OFF_DENIED, TEL_EVENTS.HR.ACTION_FRACTURE);

/**
 * @description Submits a tenant time-off delete command.
 * @collaboration HrDashboard and explicitly registered HR client consumers.
 * @institutional Client transport creates no authorization, business truth, transaction or idempotency authority; Python EOS is authoritative.
 * @param {string} id - Source command input.
 * @param {string} tenantId - Exact tenant-scoped request input.
 * @returns {Promise<void>} Source-owned response or circuit state.
 * @throws {Error} Error when scope is absent, authorization denies, or the source is unavailable; mutations retain the source HTTP contract.
 */
export const deleteTimeOffRequest = (id, tenantId) =>
  deleteResource(`/hr/timeoff/${id}`, tenantId, TEL_EVENTS.HR.TIME_OFF_DELETED, TEL_EVENTS.HR.ACTION_FRACTURE);

// ─── Circuit Management ──────────────────────────────────────────────────────
/**
 * @description Resets this module-local transport breaker without changing source records.
 * @collaboration Local client transport recovery and focused tests.
 * @institutional A transport circuit reset grants no HR or tenant authority.
 * @returns {void} Completion of the local breaker reset.
 */
export const resetHrCircuit = () => hrCircuit.reset();
/**
 * @description Returns the module-local transport circuit snapshot.
 * @collaboration Local client diagnostics and focused tests.
 * @institutional Circuit posture is operational metadata, not source or authorization truth.
 * @returns {Object} Current breaker snapshot.
 */
export const getHrCircuitState = () => hrCircuit.snapshot();

export default {
  getEmployees,
  getEmployeesArray,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  getRecruitmentCandidates,
  getHiringCandidates,
  getHiringOffers,
  createHiringCandidate,
  transitionHiringCandidate,
  uploadHiringCandidateEvidence,
  readHiringCandidateEvidence,
  createHiringOffer,
  submitHiringOffer,
  decideHiringOffer,
  sendHiringOffer,
  createCandidate,
  updateCandidateStage,
  deleteCandidate,
  getJobOpenings,
  createJobOpening,
  updateJobOpening,
  deleteJobOpening,
  getPayrollSummary,
  syncPayroll,
  getBenefits,
  createBenefit,
  updateBenefit,
  deleteBenefit,
  getPerformanceReviews,
  createPerformanceReview,
  updatePerformanceReview,
  deletePerformanceReview,
  getTimeOffRequests,
  createTimeOffRequest,
  updateTimeOffRequest,
  approveTimeOff,
  denyTimeOff,
  deleteTimeOffRequest,
  resetHrCircuit,
  getHrCircuitState
};

/**
 * ARTIFACT: client/src/services/hrService.js
 * VERSION: v1.9.0-CANDIDATE-EVIDENCE-CUSTODY-TRANSPORT
 * AUTHORITY BOUNDARY: Transport only; Python EOS owns all HR authorization and business truth.
 * TENANT POSTURE: Exact nonempty tenant scope is required for every API operation.
 * FAIL-CLOSED POSTURE: Network, authorization, source, circuit and response-contract failures reject; verified empty pages remain empty.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; this module cannot execute or settle funds.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
