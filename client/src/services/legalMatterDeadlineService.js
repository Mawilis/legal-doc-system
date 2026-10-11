/**
 * WILSY OS — LEGAL MATTER DEADLINE CLIENT ADAPTER
 * VERSION: v1.0.0-D4A-MATTER-DEADLINE-CLIENT
 * AUTHORITY: Browser transport validation and presentation adaptation only.
 * EPITOME: Strict authenticated adapter for the certified D3B1 Legal Matter
 *          Deadline list/detail/create routes without browser-owned authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/legalMatterDeadlineService.js
 * COLLABORATION / OWNERSHIP: Python EOS D1/D2/D3A/D3B1 own deadline semantics,
 *                            persistence, orchestration, IAM and HTTP authority.
 *                            This adapter owns only strict client transport shape.
 * CERTIFICATION / UPDATE DATE: 2026-10-11
 * CHANGELOG: 2026-10-11 v1.0.0-D4A-MATTER-DEADLINE-CLIENT establishes exact
 *            matter-scoped list/detail reads and strict ACTIVE deadline create.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Tenant, principal, role, permission, lifecycle,
 *                             overdue, AI, payment and settlement authority are
 *                             never accepted from browser input.
 * TENANT BOUNDARY: Tenant scope remains server-derived; the browser supplies only
 *                  the explicit matter/deadline locators required by D3B1 paths.
 * AUTHORITY BOUNDARY: Transport validation only; no legal-period calculation,
 *                     court-rule inference, filing/service truth or AI authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Malformed input/response, scope drift, duplicate
 *                          identity or privilege widening rejects without fallback.
 */

import api from './api.js';
import sovereignClient from '../utils/sovereignClient.js';

export const LEGAL_MATTER_DEADLINE_CLIENT_VERSION =
  'v1.0.0-D4A-MATTER-DEADLINE-CLIENT';

const SHA3_512_PATTERN = /^[0-9a-f]{128}$/;
const RESPONSE_KEYS = Object.freeze([
  'deadline_id',
  'case_matter_id',
  'deadline_kind',
  'title',
  'due_at',
  'source_type',
  'jurisdiction_reference',
  'created_at',
  'supersedes_deadline_id',
  'status',
]);
const DEADLINE_KINDS = Object.freeze([
  'FILING',
  'HEARING',
  'RESPONSE',
  'SERVICE',
  'CONTRACTUAL',
  'INTERNAL_WORKFLOW',
  'OTHER_EVIDENCED_DEADLINE',
]);
const SOURCE_TYPES = Object.freeze([
  'COURT_ORDER',
  'RULE_OR_STATUTE',
  'CONTRACTUAL',
  'CLIENT_INSTRUCTION',
  'INTERNAL_WORKFLOW',
  'OTHER_EVIDENCED_SOURCE',
]);
const STATUSES = Object.freeze([
  'ACTIVE',
  'SATISFIED',
  'SUPERSEDED',
  'CANCELLED',
]);
const CREATE_INPUT_KEYS = Object.freeze([
  'caseMatterId',
  'deadlineId',
  'deadlineKind',
  'title',
  'dueAt',
  'sourceType',
  'sourceReference',
  'sourceEvidenceFingerprint',
  'jurisdictionReference',
  'createdAt',
  'supersedesDeadlineId',
]);

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function isCanonicalText(value) {
  return typeof value === 'string' && value.trim() === value && Boolean(value);
}

function isCanonicalTimestamp(value) {
  return (
    isCanonicalText(value)
    && /(?:Z|[+-]\d{2}:\d{2})$/.test(value)
    && Number.isFinite(Date.parse(value))
  );
}

function assertExactKeys(value, expectedKeys, code) {
  if (!isPlainObject(value)) throw new Error(code);
  const actual = Object.keys(value).sort();
  const expected = [...expectedKeys].sort();
  if (
    actual.length !== expected.length
    || actual.some((key, index) => key !== expected[index])
  ) {
    throw new Error(code);
  }
}

function assertCanonicalRow(value, expectedMatterId, expectedDeadlineId = null) {
  const code = 'LEGAL_OPERATIONS_DEADLINE_RESPONSE_INVALID';
  assertExactKeys(value, RESPONSE_KEYS, code);
  if (
    !isCanonicalText(value.deadline_id)
    || !isCanonicalText(value.case_matter_id)
    || value.case_matter_id !== expectedMatterId
    || (
      expectedDeadlineId !== null
      && value.deadline_id !== expectedDeadlineId
    )
    || !DEADLINE_KINDS.includes(value.deadline_kind)
    || !isCanonicalText(value.title)
    || !isCanonicalTimestamp(value.due_at)
    || !SOURCE_TYPES.includes(value.source_type)
    || !isCanonicalText(value.jurisdiction_reference)
    || !isCanonicalTimestamp(value.created_at)
    || !STATUSES.includes(value.status)
    || (
      value.supersedes_deadline_id !== null
      && !isCanonicalText(value.supersedes_deadline_id)
    )
  ) {
    throw new Error(code);
  }

  return Object.freeze({
    deadlineId: value.deadline_id,
    caseMatterId: value.case_matter_id,
    deadlineKind: value.deadline_kind,
    title: value.title,
    dueAt: value.due_at,
    sourceType: value.source_type,
    jurisdictionReference: value.jurisdiction_reference,
    createdAt: value.created_at,
    supersedesDeadlineId: value.supersedes_deadline_id,
    status: value.status,
  });
}

function assertListEnvelope(value, expectedMatterId) {
  const code = 'LEGAL_OPERATIONS_DEADLINE_RESPONSE_INVALID';
  assertExactKeys(value, ['data'], code);
  if (!Array.isArray(value.data)) throw new Error(code);

  const seen = new Set();
  const rows = value.data.map((row) => {
    const adapted = assertCanonicalRow(row, expectedMatterId);
    if (seen.has(adapted.deadlineId)) throw new Error(code);
    seen.add(adapted.deadlineId);
    return adapted;
  });
  return Object.freeze(rows);
}

function assertDetailEnvelope(value, expectedMatterId, expectedDeadlineId) {
  const code = 'LEGAL_OPERATIONS_DEADLINE_RESPONSE_INVALID';
  assertExactKeys(value, ['data'], code);
  return assertCanonicalRow(
    value.data,
    expectedMatterId,
    expectedDeadlineId,
  );
}

function assertCreateInput(value) {
  const code = 'LEGAL_OPERATIONS_DEADLINE_INPUT_INVALID';
  assertExactKeys(value, CREATE_INPUT_KEYS, code);
  if (
    !isCanonicalText(value.caseMatterId)
    || !isCanonicalText(value.deadlineId)
    || !DEADLINE_KINDS.includes(value.deadlineKind)
    || !isCanonicalText(value.title)
    || !isCanonicalTimestamp(value.dueAt)
    || !SOURCE_TYPES.includes(value.sourceType)
    || !isCanonicalText(value.sourceReference)
    || !SHA3_512_PATTERN.test(value.sourceEvidenceFingerprint)
    || !isCanonicalText(value.jurisdictionReference)
    || !isCanonicalTimestamp(value.createdAt)
    || (
      value.supersedesDeadlineId !== null
      && !isCanonicalText(value.supersedesDeadlineId)
    )
  ) {
    throw new Error(code);
  }
  return Object.freeze({ ...value });
}

/**
 * Read the exact server-authorized deadline list for one matter.
 * @param {string} caseMatterId Explicit matter path locator, not tenant authority.
 * @returns {Promise<ReadonlyArray<object>>} Frozen bounded deadline rows.
 */
export async function getLegalMatterDeadlines(caseMatterId) {
  if (!isCanonicalText(caseMatterId)) {
    throw new Error('LEGAL_OPERATIONS_DEADLINE_LOOKUP_INPUT_INVALID');
  }
  const response = await api.get(
    `/legal-operations/matters/${encodeURIComponent(caseMatterId)}/deadlines`,
  );
  return assertListEnvelope(response?.data, caseMatterId);
}

/**
 * Read one exact server-authorized deadline and verify path correlation.
 */
export async function getLegalMatterDeadline(caseMatterId, deadlineId) {
  if (!isCanonicalText(caseMatterId) || !isCanonicalText(deadlineId)) {
    throw new Error('LEGAL_OPERATIONS_DEADLINE_LOOKUP_INPUT_INVALID');
  }
  const response = await api.get(
    `/legal-operations/matters/${encodeURIComponent(caseMatterId)}/deadlines/${encodeURIComponent(deadlineId)}`,
  );
  return assertDetailEnvelope(response?.data, caseMatterId, deadlineId);
}

/**
 * Create or exactly replay one evidenced ACTIVE deadline.
 * The client cannot supply tenant/principal/role/status/overdue/AI/financial truth.
 */
export async function createLegalMatterDeadline(value) {
  const input = assertCreateInput(value);
  const response = await sovereignClient.post(
    `/legal-operations/matters/${encodeURIComponent(input.caseMatterId)}/deadlines`,
    {
      deadline_id: input.deadlineId,
      deadline_kind: input.deadlineKind,
      title: input.title,
      due_at: input.dueAt,
      source_type: input.sourceType,
      source_reference: input.sourceReference,
      source_evidence_fingerprint: input.sourceEvidenceFingerprint,
      jurisdiction_reference: input.jurisdictionReference,
      created_at: input.createdAt,
      supersedes_deadline_id: input.supersedesDeadlineId,
      status: 'ACTIVE',
    },
  );
  return assertDetailEnvelope(
    response?.data,
    input.caseMatterId,
    input.deadlineId,
  );
}

export const __legalMatterDeadlineServiceInternals = Object.freeze({
  assertCanonicalRow,
  assertListEnvelope,
  assertDetailEnvelope,
  assertCreateInput,
  RESPONSE_KEYS,
  DEADLINE_KINDS,
  SOURCE_TYPES,
  STATUSES,
  CREATE_INPUT_KEYS,
});

/**
 * ARTIFACT: legalMatterDeadlineService.js
 * VERSION: v1.0.0-D4A-MATTER-DEADLINE-CLIENT
 * AUTHORITY BOUNDARY: strict deadline browser transport validation only
 * TENANT POSTURE: server-derived tenant scope only; browser supplies matter/deadline locators
 * FAIL-CLOSED POSTURE: malformed input/response, path drift, duplicate identity and privilege widening reject
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
