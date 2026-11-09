/**
 * TITLE: WILSY OS Current-Session Unified My Work Read Coordinator
 * VERSION: v1.0.0-SOURCE-CONFIRMED-INVALIDATION
 * AUTHORITY: WILSY OS Core Governance; EOS remains business and IAM authority.
 * EPITOME: Deduplicate concurrent authenticated My Work reads and revalidate
 *          exactly scoped subscribers after a server-confirmed source command.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/unifiedMyWorkSync.js
 * COLLABORATION / OWNERSHIP: AuthContext owns session generation and capacity,
 *                            unifiedMyWorkProjection validates EOS responses,
 *                            source services own all writes and durable audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0 introduces a bounded in-memory, exact-session read
 *            coordinator. No persistent cache, synthetic permissions, or
 *            optimistic completion is permitted. Subscriptions are removed and
 *            pending reads aborted when their last consumer unmounts.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No tokens, bodies or personal data in diagnostics;
 *                            held only while an authorized component is mounted.
 * TENANT BOUNDARY: Tenant, principal, selected capacity, membership and role
 *                  revisions, and session generation are separate key fields.
 * AUTHORITY BOUNDARY: Cached results never authorize a command or a route.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import api from './api.js';
import { assertUnifiedMyWorkProjection } from './unifiedMyWorkProjection.js';

const RESOURCE_PREFIX = 'WILSY-OS-MY-WORK-SCOPE/V1';
const MAX_REUSE_MS = 750;
const entries = new Map();

const exact = (value) => value === null || value === undefined ? '' : String(value);

const abortError = () => {
  const error = new Error('MY_WORK_READ_SUPERSEDED');
  error.name = 'AbortError';
  return error;
};

/**
 * @description Versioned key for current-session, current-capacity read reuse.
 * @institutional A scope key partitions client traffic; it is never proof of
 * tenant membership, permission, entitlement or a previously completed MFA.
 * @param {Object} scope Authenticated provider projection, not route parameters.
 * @returns {string|null} Exact partition; null if tenant context is absent.
 */
export function unifiedMyWorkScopeKey(scope = {}) {
  if (!scope || typeof scope.tenantId !== 'string' || !scope.tenantId) return null;
  return JSON.stringify([
    RESOURCE_PREFIX,
    exact(scope.sessionGeneration),
    scope.tenantId,
    exact(scope.principalId),
    exact(scope.role),
    exact(scope.workspaceId),
    exact(scope.businessRole),
    exact(scope.membershipRevision),
    exact(scope.businessRoleRevision),
  ]);
}

/**
 * @description Build a read-only partition from the current AuthProvider user.
 * @param {Object|null} auth Current provider values.
 * @param {string|null} tenantId Optional explicitly matched workspace tenant.
 * @returns {string|null} Versioned current-session partition.
 */
export function currentUnifiedMyWorkScope(auth, tenantId = null) {
  const user = auth?.user || {};
  const tenant = tenantId || user.tenantId;
  if (!tenant || (user.tenantId && user.tenantId !== tenant)) return null;
  return unifiedMyWorkScopeKey({
    sessionGeneration: auth?.sessionGeneration,
    tenantId: tenant,
    principalId: user.id,
    role: user.role,
    workspaceId: user.workspaceId,
    businessRole: user.businessRole,
    membershipRevision: user.membershipRevision,
    businessRoleRevision: user.businessRoleRevision,
  });
}

function entryFor(key) {
  let entry = entries.get(key);
  if (!entry) {
    entry = { listeners: new Set(), version: 0, pending: null, controller: null,
      payload: null, expiresAt: 0 };
    entries.set(key, entry);
  }
  return entry;
}

function discardIfUnused(key, entry) {
  if (entry.listeners.size !== 0 || entry.pending) return;
  if (entries.get(key) === entry) entries.delete(key);
}

function callerAbort(pending, signal) {
  if (!signal) return pending;
  if (signal.aborted) return Promise.reject(abortError());
  return new Promise((resolve, reject) => {
    const onAbort = () => reject(abortError());
    signal.addEventListener('abort', onAbort, { once: true });
    pending.then(resolve, reject).finally(() => {
      signal.removeEventListener('abort', onAbort);
    });
  });
}

/**
 * @description Read the current EOS snapshot, deduplicating overlapping calls.
 * @institutional Both cached and network values pass the same exact-scope and
 * source-identity validator; an invalidated in-flight request cannot complete.
 * @param {string} scopeKey Exact current-auth partition.
 * @param {{tenantId?: string, principalId?: string}} expectedScope EOS subject.
 * @param {{signal?: AbortSignal, force?: boolean}} options Local read controls.
 * @returns {Promise<Object>} Server-validated source-owned work projection.
 */
export function readUnifiedMyWork(scopeKey, expectedScope = {}, options = {}) {
  if (!scopeKey || typeof scopeKey !== 'string') {
    return Promise.reject(new Error('MY_WORK_AUTHENTICATED_SCOPE_REQUIRED'));
  }
  const entry = entryFor(scopeKey);
  if (entry.pending) {
    return callerAbort(entry.pending.then((payload) =>
      assertUnifiedMyWorkProjection(payload, expectedScope)), options.signal);
  }
  if (!options.force && entry.payload && Date.now() < entry.expiresAt) {
    try {
      return callerAbort(Promise.resolve(
        assertUnifiedMyWorkProjection(entry.payload, expectedScope)
      ), options.signal);
    } catch (error) {
      return Promise.reject(error);
    }
  }
  const version = entry.version;
  const controller = new AbortController();
  entry.controller = controller;
  const pending = api.get('/my-work', {
    forceNetworkRetry: true,
    signal: controller.signal,
  }).then((response) => {
    if (controller.signal.aborted || entry.version !== version) throw abortError();
    const verified = assertUnifiedMyWorkProjection(response?.data, expectedScope);
    if (controller.signal.aborted || entry.version !== version) throw abortError();
    entry.payload = verified;
    entry.expiresAt = Date.now() + MAX_REUSE_MS;
    return verified;
  }).catch((error) => {
    if (entry.version === version) {
      entry.payload = null;
      entry.expiresAt = 0;
    }
    throw error;
  }).finally(() => {
    if (entry.pending === pending) {
      entry.pending = null;
      if (entry.controller === controller) entry.controller = null;
      discardIfUnused(scopeKey, entry);
    }
  });
  entry.pending = pending;
  return callerAbort(pending, options.signal);
}

/**
 * @description Register an active view for scoped, source-confirmed refresh.
 * @param {string|null} scopeKey Exact authenticated scope.
 * @param {Function} callback Synchronous notification to re-read EOS.
 * @returns {Function} Idempotent cleanup that discards unused private state.
 */
export function subscribeUnifiedMyWork(scopeKey, callback) {
  if (!scopeKey || typeof callback !== 'function') return () => {};
  const entry = entryFor(scopeKey);
  entry.listeners.add(callback);
  let attached = true;
  return () => {
    if (!attached) return;
    attached = false;
    entry.listeners.delete(callback);
    if (entry.listeners.size === 0) {
      entry.version += 1;
      entry.controller?.abort();
      entry.pending = null;
      entry.controller = null;
      entry.payload = null;
      entry.expiresAt = 0;
      discardIfUnused(scopeKey, entry);
    }
  };
}

/**
 * @description Invalidate only the exact current-session projection.
 * @institutional Call after a confirmed source-owned mutation, never on mere
 * UI clicks, network uncertainty, or an unverified optimistic transition.
 * @param {string|null} scopeKey Current source-command session partition.
 * @returns {boolean} Whether a mounted current-scope view was notified.
 */
export function invalidateUnifiedMyWork(scopeKey) {
  const entry = scopeKey ? entries.get(scopeKey) : null;
  if (!entry) return false;
  entry.version += 1;
  entry.controller?.abort();
  entry.pending = null;
  entry.controller = null;
  entry.payload = null;
  entry.expiresAt = 0;
  for (const notify of Array.from(entry.listeners)) notify();
  discardIfUnused(scopeKey, entry);
  return entry.listeners.size > 0;
}

/**
 * @description Discard a scope without prompting any prior principal to refetch.
 * @param {string|null} scopeKey Former authenticated scope.
 */
export function releaseUnifiedMyWork(scopeKey) {
  const entry = scopeKey ? entries.get(scopeKey) : null;
  if (!entry) return;
  entry.version += 1;
  entry.controller?.abort();
  entry.pending = null;
  entry.controller = null;
  entry.payload = null;
  entry.expiresAt = 0;
  if (entry.listeners.size === 0) discardIfUnused(scopeKey, entry);
}

// ARTIFACT: client/src/services/unifiedMyWorkSync.js
// VERSION: v1.0.0-SOURCE-CONFIRMED-INVALIDATION
// AUTHORITY BOUNDARY: EOS-only reads; no browser command authorization.
// TENANT POSTURE: Exact session/capacity partition, no persistent cache.
// FAIL-CLOSED POSTURE: Superseded reads and invalid/foreign results reject.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
