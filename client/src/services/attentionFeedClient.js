/**
 * TITLE: WILSY OS Daily Attention Authenticated Feed Client
 * VERSION: v1.0.0-EOS-ATTENTION-READ-CONTRACT
 * AUTHORITY: WILSY OS Core Governance; Python EOS owns authoritative work.
 * EPITOME: Validate and read the exact scoped AttentionItem feed without
 *          browser-side IAM claims, task persistence or command authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/attentionFeedClient.js
 * COLLABORATION / OWNERSHIP: AuthContext establishes the authenticated session;
 *          unifiedMyWorkSync builds its exact scope; attention_router owns the
 *          EOS feed and source-owned registries retain all business commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.0-EOS-ATTENTION-READ-CONTRACT establishes bounded read
 *          validation, explicit current-session scope, source coverage truth,
 *          server-side filters and cursor transport with no browser cache.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No persisted queue, no tokens in diagnostics,
 *          no confidential detail inference or self-granted action hints.
 * TENANT BOUNDARY: Every read checks exact EOS tenant and principal identity.
 * AUTHORITY BOUNDARY: GET only; OPEN is navigation, not command authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes finances.
 */

import api from './api.js';

const SCHEMA = 'WILSY-OS-ATTENTION-FEED/V1';
const SOURCES = new Set(['LEGAL', 'OPERATIONS', 'INTELLIGENCE', 'CRM']);
const PRIORITIES = new Set(['CRITICAL', 'HIGH', 'NORMAL', 'LOW']);
const SOURCE_STATES = new Set(['ok', 'empty']);
const VIEWS = new Set(['active', 'overdue', 'due_today', 'high_priority']);
const validCount = (n) => Number.isSafeInteger(n) && n >= 0;

/**
 * @description Validate bounded EOS feed and admitted module coverage.
 * @param {Object} feed Source-authorised EOS AttentionItem read response.
 * @param {{tenantId: string, principalId: string}} scope Current AuthProvider identity.
 * @returns {Object} The validated response, unchanged and non-authorizing.
 * @throws {Error} Stable scope or projection validation failure.
 * @institutional No source command, transaction, idempotency or permission authority.
 */
export function assertAttentionFeed(feed, scope) {
  if (
    !feed || typeof feed !== 'object' || Array.isArray(feed)
    || feed.schema !== SCHEMA
    || feed.tenantId !== scope?.tenantId
    || feed.principalId !== scope?.principalId
    || typeof feed.syncedAt !== 'string'
    || Number.isNaN(Date.parse(feed.syncedAt))
    || !VIEWS.has(feed.view)
    || !Array.isArray(feed.items) || feed.items.length > 100
    || !feed.counts || !['active', 'overdue', 'dueToday', 'highPriority']
      .every((key) => validCount(feed.counts[key]))
    || !Array.isArray(feed.sources)
    || !feed.coverage
    || feed.coverage.completeEnterpriseCoverage !== false
    || !Array.isArray(feed.coverage.admittedSources)
    || !Array.isArray(feed.coverage.notRepresentedSources)
    || !validCount(feed.filteredTotal)
    || feed.filteredTotal < feed.items.length
    || (feed.nextCursor !== null && (
      typeof feed.nextCursor !== 'string' || !feed.nextCursor
      || feed.nextCursor.length > 256
    ))
    || feed.authority?.commandsOwnedBy !== 'SOURCE_SERVICES'
    || feed.authority?.attentionCommandsEnabled !== false
  ) throw new Error('ATTENTION_FEED_PROJECTION_INVALID');

  const admitted = new Set(feed.coverage.admittedSources);
  if (
    admitted.size !== feed.coverage.admittedSources.length
    || feed.coverage.admittedSources.some((s) => !SOURCES.has(s))
    || feed.sources.length !== admitted.size
    || feed.coverage.notRepresentedSources.some((s) => typeof s !== 'string')
  ) throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');

  const seenSources = new Set();
  for (const source of feed.sources) {
    if (
      !source || !admitted.has(source.moduleId)
      || seenSources.has(source.moduleId)
      || !SOURCE_STATES.has(source.state)
      || !validCount(source.count)
      || (source.state === 'empty') !== (source.count === 0)
    ) throw new Error('ATTENTION_SOURCE_COVERAGE_INVALID');
    seenSources.add(source.moduleId);
  }
  const seen = new Set();
  for (const item of feed.items) {
    if (
      !item || typeof item !== 'object'
      || item.tenantId !== scope.tenantId
      || !admitted.has(item.sourceModule)
      || typeof item.sourceRecordId !== 'string' || !item.sourceRecordId
      || item.id !== item.sourceModule + ':' + item.sourceRecordId
      || seen.has(item.id)
      || typeof item.title !== 'string' || !item.title.trim()
      || !PRIORITIES.has(item.priority)
      || !Number.isSafeInteger(item.urgencyScore)
      || item.urgencyScore < 0 || item.urgencyScore > 100
      || typeof item.whyRanked !== 'string'
      || (item.dueAt !== null && (
        typeof item.dueAt !== 'string' || Number.isNaN(Date.parse(item.dueAt))
      ))
      || !Array.isArray(item.actionHints)
      || item.actionHints.length !== 1 || item.actionHints[0] !== 'OPEN'
      || item.deepLink !== '/my-work'
      || item.authzScope !== 'SOURCE_SERVICE_ONLY'
      || typeof item.isOverdue !== 'boolean'
    ) throw new Error('ATTENTION_ITEM_INVALID');
    seen.add(item.id);
  }
  if (
    feed.counts.overdue > feed.counts.active
    || feed.counts.dueToday > feed.counts.active
    || feed.counts.highPriority > feed.counts.active
    || feed.filteredTotal > feed.counts.active
  ) throw new Error('ATTENTION_SOURCE_COUNTS_INVALID');
  return feed;
}

/**
 * @description Request one exact-session, server-filtered AttentionItem page.
 * @param {{tenantId: string, principalId: string}} scope Server-issued session subject.
 * @param {{view?: string, sources?: string, q?: string, cursor?: string,
 *          limit?: number, signal?: AbortSignal}} options Bounded read only.
 * @returns {Promise<Object>} Exact-identity verified attention feed page.
 * @throws {Error} Network/auth rejection or structured projection error.
 * @institutional GET only; no optimistic writes or transaction participation.
 */
export async function readAttentionFeed(scope, options = {}) {
  if (
    typeof scope?.tenantId !== 'string' || !scope.tenantId
    || typeof scope?.principalId !== 'string' || !scope.principalId
  ) throw new Error('ATTENTION_AUTHENTICATED_SCOPE_REQUIRED');
  const view = options.view || 'active';
  if (!VIEWS.has(view)) throw new Error('ATTENTION_FILTER_INVALID');
  const response = await api.get('/attention/feed', {
    params: {
      view,
      ...(options.sources ? { sources: options.sources } : {}),
      ...(options.q ? { q: options.q } : {}),
      ...(options.cursor ? { cursor: options.cursor } : {}),
      limit: options.limit || 50,
    },
    forceNetworkRetry: true,
    ...(options.signal ? { signal: options.signal } : {}),
  });
  const verified = assertAttentionFeed(response?.data, scope);
  if (verified.view !== view) throw new Error('ATTENTION_FEED_VIEW_MISMATCH');
  return verified;
}

// ARTIFACT: client/src/services/attentionFeedClient.js
// VERSION: v1.0.0-EOS-ATTENTION-READ-CONTRACT
// AUTHORITY BOUNDARY: Exact source-authorized GET only; OPEN is navigation.
// TENANT POSTURE: Current EOS tenant and principal required for each response.
// FAIL-CLOSED POSTURE: Foreign, invalid or overstated source evidence rejects.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
