/**
 * TITLE: WILSY OS Unified My Work Client Projection Contract
 * VERSION: v1.0.0-SOURCE-COVERAGE-CONTRACT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Validates the existing EOS My Work read shape consistently across
 *          Daily Attention, Headquarters, and My Work without creating authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/unifiedMyWorkProjection.js
 * COLLABORATION / OWNERSHIP: Python EOS owns visibility, records and commands;
 *                            authenticated client views consume this validator.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-SOURCE-COVERAGE-CONTRACT establishes one pure validation
 *            contract for tenant/principal scope, source admission, source
 *            counts, row identity, summary counts and command-authority claims.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Pure in-memory validation; no persistence, logs,
 *                             network requests, or browser storage.
 * TENANT BOUNDARY: Requires exact requested tenant and principal when supplied.
 * AUTHORITY BOUNDARY: Source metadata is projection scope only; source services
 *                     remain exclusive command owners.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
 */
const SCHEMA = 'WILSY-OS-UNIFIED-MY-WORK/V1';
const SOURCES = Object.freeze({
  LEGAL: 'Legal',
  OPERATIONS: 'Operations',
  INTELLIGENCE: 'Intelligence',
  CRM: 'CRM',
});
const VALID_PRIORITIES = new Set(['CRITICAL', 'HIGH', 'NORMAL', 'LOW']);

const validCount = (value) => Number.isSafeInteger(value) && value >= 0;

/**
 * Validate the established EOS aggregate without adding client authority.
 *
 * @description Checks schema, exact optional caller scope, row identity,
 *   summary counts, source admission/count parity, and source-owned command
 *   declarations before any consumer renders a projection.
 * @collaboration Daily Attention, Headquarters Daily Brief, and My Work.
 * @institutional A shared fail-closed contract prevents consumers from
 *   disagreeing about which authorized sources contributed to one snapshot.
 * @param {Object} payload EOS WILSY-OS-UNIFIED-MY-WORK/V1 response body.
 * @param {{tenantId?: string, principalId?: string}} [expectedScope]
 *   Authenticated client scope used only to reject a mismatched response.
 * @returns {Object} The same validated payload; no copy or new authority.
 * @throws {Error} Stable projection contract codes for invalid data or scope.
 */
export function assertUnifiedMyWorkProjection(payload, expectedScope = {}) {
  if (
    !payload || typeof payload !== 'object' || Array.isArray(payload)
    || payload.schema !== SCHEMA
    || typeof payload.tenant_id !== 'string' || !payload.tenant_id
    || typeof payload.principal_id !== 'string' || !payload.principal_id
    || typeof payload.as_of !== 'string'
    || Number.isNaN(new Date(payload.as_of).getTime())
    || !Array.isArray(payload.items)
    || !payload.summary || typeof payload.summary !== 'object'
    || Array.isArray(payload.summary)
    || !validCount(payload.summary.active_count)
    || !validCount(payload.summary.overdue_count)
    || payload.summary.active_count !== payload.items.length
    || payload.authority?.commands_owned_by !== 'SOURCE_SERVICES'
    || payload.authority?.permits_completion !== false
  ) {
    throw new Error('ATTENTION_PROJECTION_INVALID');
  }

  if (
    (expectedScope.tenantId && payload.tenant_id !== expectedScope.tenantId)
    || (expectedScope.principalId && payload.principal_id !== expectedScope.principalId)
  ) {
    throw new Error('MY_WORK_SCOPE_MISMATCH');
  }

  const included = payload.sources_included;
  const sourceCounts = payload.summary.source_counts;
  if (
    !Array.isArray(included)
    || !sourceCounts || typeof sourceCounts !== 'object'
    || Array.isArray(sourceCounts)
  ) {
    throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');
  }

  const includedSet = new Set();
  for (const source of included) {
    if (
      typeof source !== 'string'
      || !Object.hasOwn(SOURCES, source)
      || includedSet.has(source)
    ) {
      throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');
    }
    includedSet.add(source);
  }

  const countSources = Object.keys(sourceCounts);
  if (
    countSources.length !== includedSet.size
    || countSources.some((source) => !includedSet.has(source))
  ) {
    throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');
  }

  const seen = new Set();
  const observedCounts = new Map();
  let observedOverdue = 0;
  for (const item of payload.items) {
    if (
      !item || typeof item !== 'object' || Array.isArray(item)
      || !Object.hasOwn(SOURCES, item.source)
      || !includedSet.has(item.source)
      || typeof item.work_item_id !== 'string' || !item.work_item_id.trim()
      || item.source_key !== item.source + ':' + item.work_item_id
      || seen.has(item.source_key)
      || typeof item.title !== 'string' || !item.title.trim()
      || !VALID_PRIORITIES.has(item.priority)
      || typeof item.is_overdue !== 'boolean'
      || (item.due_at !== null && item.due_at !== undefined
        && (typeof item.due_at !== 'string'
          || Number.isNaN(new Date(item.due_at).getTime())))
      || (Object.hasOwn(item, 'tenant_id') && item.tenant_id !== payload.tenant_id)
    ) {
      throw new Error('ATTENTION_ITEM_INVALID');
    }
    seen.add(item.source_key);
    if (item.is_overdue) observedOverdue += 1;
    observedCounts.set(item.source, (observedCounts.get(item.source) || 0) + 1);
  }

  if (payload.summary.overdue_count !== observedOverdue) {
    throw new Error('ATTENTION_SUMMARY_INVALID');
  }

  let total = 0;
  for (const source of included) {
    const count = sourceCounts[source];
    if (
      !validCount(count)
      || count !== (observedCounts.get(source) || 0)
    ) {
      throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');
    }
    total += count;
  }
  if (total !== payload.summary.active_count) {
    throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');
  }

  return payload;
}

/**
 * Resolve the presentation label for a source admitted by EOS.
 *
 * @description Returns a stable UI label only for a known projection source.
 * @collaboration Daily Attention and Headquarters source filters and cards.
 * @institutional Labels describe existing source identity and do not confer
 *   source access or command permission.
 * @param {string} source EOS source identifier.
 * @returns {string|null} Known source label or null for an unknown identifier.
 */
export function unifiedMyWorkSourceLabel(source) {
  return Object.hasOwn(SOURCES, source) ? SOURCES[source] : null;
}

/*
 * ARTIFACT: unifiedMyWorkProjection.js
 * VERSION: v1.0.0-SOURCE-COVERAGE-CONTRACT
 * AUTHORITY BOUNDARY: Client projection validation and source labels only.
 * TENANT POSTURE: Exact supplied scope is checked; server authorization remains canonical.
 * FAIL-CLOSED POSTURE: Malformed scope, counts, rows or source metadata are rejected.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
