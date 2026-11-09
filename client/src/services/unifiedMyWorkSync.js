/**
 * TITLE: WILSY OS Current-Session Unified My Work Read Coordinator
 * VERSION: v1.1.1-EXACT-CREDENTIAL-READ-OWNERSHIP
 * AUTHORITY: WILSY OS Core Governance; EOS remains business and IAM authority.
 * EPITOME: Deduplicate concurrent authenticated My Work reads and revalidate
 *          exactly scoped subscribers after a server-confirmed source command.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/unifiedMyWorkSync.js
 * COLLABORATION / OWNERSHIP: AuthContext owns session generation and capacity,
 *                            unifiedMyWorkProjection validates EOS responses,
 *                            source services own all writes and durable audit.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.1.1-EXACT-CREDENTIAL-READ-OWNERSHIP requires a current bearer and excludes SYSTEM
 *            workspaces from tenant My Work reuse; isolates aborted consumers
 *            without leaking a rejected cleanup promise.
 *            v1.1.0-GOVERNED-SESSION-SCOPED-READS enforces authenticated principal, tenant and
 *            integer session generation in every read partition, validates
 *            requested read scope against the current-session key, documents
 *            exported API authority, transaction and failure boundaries, and
 *            severs superseded in-flight requests before revalidation.
 *            v1.0.0-SOURCE-CONFIRMED-INVALIDATION established the in-memory
 *            request coordinator, scoped subscriptions and no write authority.
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
 * @returns {string|null} Exact tenant/principal/session partition; null if
 *                    any essential authenticated identity field is absent.
 * @throws {Error} None; incomplete identity fails closed to null.
 * @tenant Exact server-projected tenant and principal mandatory.
 * @mutation None. Key calculation never changes EOS or business records.
 * @idempotency Deterministic for one immutable authenticated session state.
 * @transaction Not a persistence participant; EOS owns all DB sessions.
 * @financial No release, execution or settlement authority.
 */
export function unifiedMyWorkScopeKey(scope = {}) {
  if (
    !scope
    || typeof scope.tenantId !== 'string' || !scope.tenantId
    || typeof scope.principalId !== 'string' || !scope.principalId
    || !Number.isSafeInteger(scope.sessionGeneration)
    || scope.sessionGeneration < 0
  ) return null;
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
 * @returns {string|null} Versioned current-session partition or null.
 * @tenant Requires AuthProvider-authenticated identity with matching exact tenant.
 * @authority Does not infer identity from browser location, routes or cache.
 * @mutation None; read-only scope derivation.
 * @idempotency Deterministic for one current session.
 * @transaction No browser-owned DB session or command boundary.
 * @financial Kennel EOS retains sole financial execution authority.
 */
export function currentUnifiedMyWorkScope(auth, tenantId = null) {
  const user = auth?.user || {};
  const tenant = tenantId || user.tenantId;
  if (
    auth?.isAuthenticated !== true
    || auth?.authStage !== 'AUTHENTICATED'
    || typeof auth?.token !== 'string' || !auth.token.trim()
    || user?.systemServicesWorkspace === true
    || typeof user?.tenantId !== 'string' || !user.tenantId
    || typeof user?.id !== 'string' || !user.id
    || typeof tenant !== 'string'
    || user.tenantId !== tenant
  ) return null;
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
    pending.then(
      (value) => {
        signal.removeEventListener('abort', onAbort);
        resolve(value);
      },
      (error) => {
        signal.removeEventListener('abort', onAbort);
        reject(error);
      },
    );
  });
}

/**
 * @description Read the current EOS snapshot, deduplicating overlapping calls.
 * @institutional Both cached and network values pass the same exact-scope and
 * source-identity validator; an invalidated in-flight request cannot complete.
 * @param {string} scopeKey Exact current-auth partition.
 * @param {{tenantId?: string, principalId?: string}} expectedScope EOS subject.
 * @param {{signal?: AbortSignal, force?: boolean}} options Local read controls.
 * @returns {Promise<Object>} Server-validated EOS work projection.
 * @throws {Error} Missing/foreign scope, malformed source projection or aborted
 *                 session read fails closed; no partial source data emitted.
 * @tenant Exact tenant and principal must match both scope partition and EOS.
 * @mutation Transient in-memory validated read only; never a source command.
 * @idempotency Shares overlapping GETs; short-lived snapshot is not authority.
 * @transaction EOS owns every authoritative read and persistence session.
 * @financial No ability to approve, pay, execute or settle.
 */
export function readUnifiedMyWork(scopeKey, expectedScope = {}, options = {}) {
  if (!scopeKey || typeof scopeKey !== 'string') {
    return Promise.reject(new Error('MY_WORK_AUTHENTICATED_SCOPE_REQUIRED'));
  }
  let partition;
  try {
    partition = JSON.parse(scopeKey);
  } catch {
    return Promise.reject(new Error('MY_WORK_AUTHENTICATED_SCOPE_INVALID'));
  }
  if (
    !Array.isArray(partition)
    || partition.length !== 9
    || partition[0] !== RESOURCE_PREFIX
    || !Number.isSafeInteger(Number(partition[1]))
    || !partition[2] || !partition[3]
    || typeof expectedScope.tenantId !== 'string'
    || typeof expectedScope.principalId !== 'string'
    || !expectedScope.tenantId || !expectedScope.principalId
    || partition[2] !== expectedScope.tenantId
    || partition[3] !== expectedScope.principalId
  ) {
    return Promise.reject(new Error('MY_WORK_AUTHENTICATED_SCOPE_INVALID'));
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
 * @returns {Function} Idempotent subscription cleanup.
 * @tenant Only exact current-session scope subscribers receive notifications.
 * @mutation Callback registration only; no server or registry mutation.
 * @idempotency Cleanup may execute repeatedly without leaking subscriptions.
 * @transaction No MongoDB transaction; source registries own all writes.
 * @financial No payment or settlement authority.
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
 * @returns {boolean} Whether current-scope subscribers were notified.
 * @tenant One exact authenticated tenant/principal/capacity partition only.
 * @mutation Invalidates temporary browser projection; no source record write.
 * @idempotency Repeated invalidation never creates or completes business work.
 * @transaction Call only after independently confirmed source command effect.
 * @financial No release, execution, settlement or banking authority.
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
 * @tenant Removes only that scope's private transient projection.
 * @mutation Clears cached browser projection, not EOS records.
 * @idempotency Repeated release is harmless.
 * @transaction No database transaction ownership.
 * @financial No payment execution or settlement authority.
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
// VERSION: v1.1.1-EXACT-CREDENTIAL-READ-OWNERSHIP
// AUTHORITY BOUNDARY: EOS-only reads; no browser command authorization.
// TENANT POSTURE: Exact session/capacity partition, no persistent cache.
// FAIL-CLOSED POSTURE: Superseded reads and invalid/foreign results reject.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
