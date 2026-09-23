/**
 * WILSY OS — SHERIFF OPERATIONAL QUEUE CLIENT ADAPTER
 * VERSION: v1.0.0-L8-6A-SHERIFF-QUEUE-CLIENT
 * AUTHORITY: Browser transport validation and presentation adaptation only.
 * EPITOME: Reads the authenticated sheriff queue endpoint through the governed
 *          api.js transport, validates its exact bounded shape, and returns no
 *          invented deputy, urgency, distance, billing, client, AI, or
 *          financial truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/legalOperationsService.js
 * COLLABORATION / OWNERSHIP: Python EOS IAM and L8-5C own authorization and
 *                            queue truth; this adapter owns browser transport
 *                            validation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import api from './api.js';

export const LEGAL_OPERATIONS_CLIENT_VERSION =
  'v1.0.0-L8-6A-SHERIFF-QUEUE-CLIENT';

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

  return Object.freeze({
    tenantId: value.tenant_id,
    visibility: value.visibility,
    officeReceipt: Object.freeze([...value.office_receipt]),
    deputyAssignment: Object.freeze([...value.deputy_assignment]),
    activeAttempts: Object.freeze([...value.active_attempts]),
  });
}

export async function getSheriffOperationalQueues() {
  const response = await api.get('/legal-operations/operational-queues');
  return assertCanonicalQueuePayload(response?.data);
}

export const __legalOperationsServiceInternals = Object.freeze({
  assertCanonicalQueuePayload,
  QUEUE_KEYS,
  RESPONSE_KEYS,
});

/**
 * ARTIFACT: legalOperationsService.js
 * VERSION: v1.0.0-L8-6A-SHERIFF-QUEUE-CLIENT
 * AUTHORITY BOUNDARY: browser read transport and exact response validation only
 * TENANT POSTURE: server-issued queue tenant must match every projected row
 * FAIL-CLOSED POSTURE: malformed shape or tenant drift rejects without mock fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
