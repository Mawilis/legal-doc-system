/**
 * WILSY OS — ROLE-SCOPED LEGAL OPERATIONS CLIENT ADAPTER
 * VERSION: v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT
 * AUTHORITY: Browser transport validation and presentation adaptation only.
 * EPITOME: Preserves the certified sheriff tenant-wide queue read while adding
 *          the L8-6C binding-scoped deputy personal active-work read. Browser
 *          role labels never create authority; Python EOS independently
 *          authorizes each endpoint and owns all queue membership truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/legalOperationsService.js
 * COLLABORATION / OWNERSHIP: Python EOS IAM owns access authority; L8-5C owns
 *                            sheriff queue membership; L8-6B owns immutable
 *                            principal-to-Deputy binding; L8-6C owns deputy
 *                            personal active-work membership; this adapter owns
 *                            exact response validation and immutable adaptation.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT adds exact
 *            /legal-operations/deputy/active-work transport and fail-closed
 *            validation for tenant_id, DEPUTY_PERSONAL_ACTIVE_WORK visibility,
 *            canonical deputy_id, bound-deputy active attempts and
 *            ALLOCATED/ATTEMPTED states. Sheriff transport is unchanged.
 *            2026-09-23 v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT freezes each validated queue row as well as
 *            the aggregate and queue arrays; transport semantics are unchanged.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: No client-supplied tenant, principal, deputy,
 *                             urgency, geospatial, billing, payment or AI truth
 *                             is admitted into the validated server projection.
 * TENANT BOUNDARY: Every projected row must match the server response tenant;
 *                  deputy rows must additionally match the server-bound
 *                  canonical deputy_id.
 * AUTHORITY BOUNDARY: Read transport and validation only. Browser role/display
 *                     state never grants sheriff or deputy authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import api from './api.js';

export const LEGAL_OPERATIONS_CLIENT_VERSION =
  'v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT';

const QUEUE_KEYS = Object.freeze([
  'office_receipt',
  'deputy_assignment',
  'active_attempts',
]);

const RESPONSE_KEYS = Object.freeze([
  'tenant_id',
  'visibility',
  ...QUEUE_KEYS,
]);

const DEPUTY_RESPONSE_KEYS = Object.freeze([
  'tenant_id',
  'visibility',
  'deputy_id',
  'active_attempts',
]);

const ACTIVE_ATTEMPT_STATES = Object.freeze([
  'ALLOCATED',
  'ATTEMPTED',
]);

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function assertCanonicalQueuePayload(value) {
  if (!isPlainObject(value)) {
    throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
  }

  const keys = Object.keys(value).sort();
  const expectedKeys = [...RESPONSE_KEYS].sort();
  if (
    keys.length !== expectedKeys.length
    || keys.some((key, index) => key !== expectedKeys[index])
  ) {
    throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
  }

  if (
    typeof value.tenant_id !== 'string'
    || !value.tenant_id.trim()
    || value.visibility !== 'SHERIFF_OPERATIONAL_QUEUE'
  ) {
    throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
  }

  for (const key of QUEUE_KEYS) {
    if (!Array.isArray(value[key])) {
      throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
    }
    for (const item of value[key]) {
      if (!isPlainObject(item) || typeof item.tenant_id !== 'string') {
        throw new Error('LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID');
      }
      if (item.tenant_id !== value.tenant_id) {
        throw new Error('LEGAL_OPERATIONS_QUEUE_TENANT_MISMATCH');
      }
    }
  }

  const immutableRows = (rows) => Object.freeze(
    rows.map((item) => Object.freeze({ ...item })),
  );

  return Object.freeze({
    tenantId: value.tenant_id,
    visibility: value.visibility,
    officeReceipt: immutableRows(value.office_receipt),
    deputyAssignment: immutableRows(value.deputy_assignment),
    activeAttempts: immutableRows(value.active_attempts),
  });
}

function assertCanonicalDeputyActiveWorkPayload(value) {
  if (!isPlainObject(value)) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID');
  }

  const keys = Object.keys(value).sort();
  const expectedKeys = [...DEPUTY_RESPONSE_KEYS].sort();
  if (
    keys.length !== expectedKeys.length
    || keys.some((key, index) => key !== expectedKeys[index])
  ) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID');
  }

  if (
    typeof value.tenant_id !== 'string'
    || !value.tenant_id.trim()
    || value.visibility !== 'DEPUTY_PERSONAL_ACTIVE_WORK'
    || typeof value.deputy_id !== 'string'
    || !value.deputy_id.trim()
    || !Array.isArray(value.active_attempts)
  ) {
    throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_RESPONSE_INVALID');
  }

  for (const item of value.active_attempts) {
    if (
      !isPlainObject(item)
      || item.tenant_id !== value.tenant_id
      || item.deputy_id !== value.deputy_id
      || !ACTIVE_ATTEMPT_STATES.includes(item.state)
    ) {
      throw new Error('LEGAL_OPERATIONS_DEPUTY_WORK_SCOPE_INVALID');
    }
  }

  return Object.freeze({
    tenantId: value.tenant_id,
    visibility: value.visibility,
    deputyId: value.deputy_id,
    activeAttempts: Object.freeze(
      value.active_attempts.map((item) => Object.freeze({ ...item })),
    ),
  });
}

export async function getSheriffOperationalQueues() {
  const response = await api.get('/legal-operations/operational-queues');
  return assertCanonicalQueuePayload(response?.data);
}

export async function getDeputyPersonalActiveWork() {
  const response = await api.get('/legal-operations/deputy/active-work');
  return assertCanonicalDeputyActiveWorkPayload(response?.data);
}

export const __legalOperationsServiceInternals = Object.freeze({
  assertCanonicalQueuePayload,
  assertCanonicalDeputyActiveWorkPayload,
  QUEUE_KEYS,
  RESPONSE_KEYS,
  DEPUTY_RESPONSE_KEYS,
  ACTIVE_ATTEMPT_STATES,
});

/**
 * ARTIFACT: legalOperationsService.js
 * VERSION: v1.1.0-L8-6C-ROLE-SCOPED-LEGAL-OPERATIONS-CLIENT
 * AUTHORITY BOUNDARY: role-scoped browser read transport and exact response validation only
 * TENANT POSTURE: server tenant must match every row; deputy work must match server-bound deputy_id
 * FAIL-CLOSED POSTURE: malformed/extra/missing/cross-tenant/cross-deputy/terminal work rejects without fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
