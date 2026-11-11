/**
 * TITLE: WILSY OS Daily Attention Authenticated Feed Client
 * VERSION: v1.4.0-MODULE-ENTITLEMENT-ACTION-SCOPE
 * AUTHORITY: WILSY OS Core Governance; Python EOS owns authoritative work.
 * EPITOME: Validate and read the exact scoped AttentionItem feed without
 *          browser-side IAM claims, task persistence or command authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/attentionFeedClient.js
 * COLLABORATION / OWNERSHIP: AuthContext establishes the authenticated session;
 *          unifiedMyWorkSync builds its exact scope; attention_router owns the
 *          EOS feed and source-owned registries retain all business commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-11
 * CHANGELOG: v1.4.0-MODULE-ENTITLEMENT-ACTION-SCOPE uses
 *          only admitted source adapters; legal and future subscribed
 *          modules remain visible via their owning work surface without
 *          accidentally triggering unrelated command dependency checks.
 *          v1.3.0-ISOLATED-SOURCE-ACTION-READS reads
 *          command capability separately for each admitted source,
 *          retaining healthy actions despite unrelated source outages.
 *          v1.2.0-THREE-SOURCE-ACTION-CONTRACTS adds
 *          CRM and module CREATE/COMPLETE routes using already-authorized
 *          source transactions and required durable create idempotency keys.
 *          v1.1.0-SOURCE-COMMAND-AVAILABILITY verifies
 *          independent source-owned completion availability and delegates
 *          actual commands to existing tenant-module routes; no browser IAM.
 *          v1.0.0-EOS-ATTENTION-READ-CONTRACT establishes bounded read
 *          validation, explicit current-session scope, source coverage truth,
 *          server-side filters and cursor transport with no browser cache.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No persisted queue, no tokens in diagnostics,
 *          no confidential detail inference or self-granted action hints.
 * TENANT BOUNDARY: Every read checks exact EOS tenant and principal identity.
 * AUTHORITY BOUNDARY: EOS reports available source commands; existing module
 *          endpoints reauthorize every POST and own durable persistence.
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

/**
 * @description Read exact current-tenant completion availability independently
 *              verified by EOS's existing source IAM dependencies.
 * @param {{tenantId:string,principalId:string}} scope Authenticated EOS identity.
 * @returns {Promise<Object>} Validated availability only, never a grant.
 * @authority The source command endpoint independently reauthorizes every write.
 */
function isAttentionActionResponse(data, scope, expectedSource = null) {
  if (!data || data.schema !== 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1'
    || data.tenantId !== scope.tenantId || data.principalId !== scope.principalId
    || data.authority !== 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE'
    || !data.sourceActions || typeof data.sourceActions !== 'object'
    || Array.isArray(data.sourceActions)) return false;
  return Object.entries(data.sourceActions).every(([source, actions]) =>
    ['CRM', 'OPERATIONS', 'INTELLIGENCE'].includes(source)
    && (!expectedSource || source === expectedSource)
    && Array.isArray(actions) && actions.length > 0 && actions.length <= 2
    && actions.every((action) => ['CREATE', 'COMPLETE'].includes(action))
    && new Set(actions).size === actions.length);
}

export async function readAttentionSourceActions(scope, admittedSources = null) {
  if (!scope?.tenantId || !scope?.principalId) {
    throw new Error('ATTENTION_AUTHENTICATED_SCOPE_REQUIRED');
  }
  const admitted = Array.isArray(admittedSources) ? admittedSources.filter((source) =>
    ['CRM', 'OPERATIONS', 'INTELLIGENCE'].includes(source)) : null;
  if (admitted) {
    if (!admitted.length) return { sourceActions: {}, unavailableSources: [] };
    const settled = await Promise.allSettled(admitted.map((source) =>
      api.get('/attention/actions/' + source.toLowerCase(), { forceNetworkRetry: true })));
    const sourceActions = {};
    const unavailableSources = [];
    for (let i = 0; i < settled.length; i += 1) {
      const result = settled[i];
      const source = admitted[i];
      if (result.status !== 'fulfilled') {
        unavailableSources.push(source);
        continue;
      }
      const data = result.value?.data;
      if (!isAttentionActionResponse(data, scope, source)) {
        unavailableSources.push(source);
        continue;
      }
      if (data.sourceActions[source]) sourceActions[source] = data.sourceActions[source];
    }
    return { sourceActions, unavailableSources };
  }
  const response = await api.get('/attention/actions', { forceNetworkRetry: true });
  const data = response?.data;
  if (!isAttentionActionResponse(data, scope)) {
    throw new Error('ATTENTION_ACTION_AVAILABILITY_INVALID');
  }
  return data.sourceActions;
}

/**
 * @description Execute an existing, source-owned durable completion.
 * @param {Object} item EOS-attested work identity.
 * @param {string} completionNote User-supplied completion evidence.
 * @returns {Promise<Object>} Actual source transaction response.
 * @authority This request grants no permission; source IAM and Mongo transaction
 *            independently verify tenant, item, entitlement and completion.
 * @idempotency Source registry handles completed-work replay/conflict; client
 *              does not fabricate optimistic terminal status.
 */
export async function completeAttentionSourceWork(item, completionNote) {
  const slug = { OPERATIONS: 'operations', INTELLIGENCE: 'intelligence', CRM: 'crm' }[item?.sourceModule];
  if (!slug || !item?.sourceRecordId || typeof completionNote !== 'string'
    || !completionNote.trim() || completionNote.length > 1000) {
    throw new Error('ATTENTION_SOURCE_COMPLETION_INPUT_INVALID');
  }
  const base = slug === 'crm' ? '/crm/owner-workspace'
    : '/tenant-modules/' + slug + '/workspace';
  const response = await api.post(
    base + '/work-items/' + encodeURIComponent(item.sourceRecordId) + '/complete',
    { completion_note: completionNote.trim() },
  );
  if (!response?.data || response.data.work_item_id !== item.sourceRecordId
    || response.data.tenant_id !== item.tenantId
    || response.data.status !== 'COMPLETED') {
    throw new Error('ATTENTION_SOURCE_COMPLETION_READBACK_INVALID');
  }
  return response.data;
}

/**
 * @description Create genuine source-owned work with a stable operator retry key.
 * @param {string} moduleId Authorized EOS work source.
 * @param {{tenantId:string,principalId:string}} scope Current authenticated scope.
 * @param {{title:string,description?:string,priority?:string,due_at?:string|null}} form Work inputs.
 * @param {string} idempotencyKey Random per-intent key retained across retries.
 * @returns {Promise<Object>} Persisted source record, exact tenant checked.
 * @authority No browser permission; EOS separately checks create IAM and entitlement.
 * @idempotency Source owner stores/replays the supplied same-intent key.
 */
export async function createAttentionSourceWork(moduleId, scope, form, idempotencyKey) {
  const base = {
    OPERATIONS: '/tenant-modules/operations/workspace',
    INTELLIGENCE: '/tenant-modules/intelligence/workspace',
    CRM: '/crm/owner-workspace',
  }[moduleId];
  if (!base || !scope?.tenantId || !scope?.principalId
    || typeof idempotencyKey !== 'string' || !idempotencyKey || idempotencyKey.length > 160
    || typeof form?.title !== 'string' || !form.title.trim()
    || form.title.length > 240
    || typeof (form.description || '') !== 'string'
    || (form.description || '').length > 4000
    || !['CRITICAL', 'HIGH', 'NORMAL', 'LOW'].includes(form.priority || 'NORMAL')) {
    throw new Error('ATTENTION_SOURCE_CREATE_INPUT_INVALID');
  }
  const body = {
    title: form.title.trim(),
    description: form.description || '',
    kind: 'TASK',
    priority: form.priority || 'NORMAL',
    due_at: form.due_at || null,
  };
  const response = await api.post(base + '/work-items', body, {
    headers: { 'Idempotency-Key': idempotencyKey },
  });
  if (!response?.data || response.data.tenant_id !== scope.tenantId
    || typeof response.data.work_item_id !== 'string'
    || !response.data.work_item_id) {
    throw new Error('ATTENTION_SOURCE_CREATE_READBACK_INVALID');
  }
  return response.data;
}

// ARTIFACT: client/src/services/attentionFeedClient.js
// VERSION: v1.4.0-MODULE-ENTITLEMENT-ACTION-SCOPE
// AUTHORITY BOUNDARY: EOS actions availability; source-owned POST reauthorizes.
// TENANT POSTURE: Current EOS tenant and principal required for each response.
// FAIL-CLOSED POSTURE: Foreign, invalid or overstated source evidence rejects.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
