/**
 * TITLE: WILSY OS Current-Session My Work Coordination Certification
 * VERSION: v1.0.1-CURRENT-SCOPE-CHANGELOG-ALIGNMENT
 * AUTHORITY: WILSY OS Core Governance; only EOS authorizes business activity.
 * EPITOME: Proves scoped shared reads, actual EOS response verification,
 *          current session safety, source-confirmed invalidation and cleanup.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/unifiedMyWorkSync.test.js
 * COLLABORATION / OWNERSHIP: unifiedMyWorkSync, AuthProvider session scope,
 *                            unifiedMyWorkProjection and source-owned commands.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.1-CURRENT-SCOPE-CHANGELOG-ALIGNMENT records the exact current certification version; assertions and runtime behavior are unchanged.
 * CHANGELOG: v1.0.0-EXACT-SCOPE-READ-CURRENTNESS-CERT covers overlapping reads, cancelled consumers, distinct
 *            tenant/principal/capacity partitions, stale network completion,
 *            session loss, source revision and corrupt payload rejection.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic work data and no stored identity token.
 * TENANT BOUNDARY: Exact tenant/principal required by every verified response.
 * AUTHORITY BOUNDARY: No UI control or cache completes or authorizes work.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({ api: { get: vi.fn() } }));
vi.mock('../../services/api.js', () => ({ default: api }));

import {
  unifiedMyWorkScopeKey,
  currentUnifiedMyWorkScope,
  readUnifiedMyWork,
  subscribeUnifiedMyWork,
  invalidateUnifiedMyWork,
  releaseUnifiedMyWork,
} from '../../services/unifiedMyWorkSync.js';

const tenant = 'WILSYTENANT-READ-SYNC-A';
const principal = 'WILSYAUTH-READ-SYNC-A';
let nextSession = 10;
const expected = (tenantId = tenant, principalId = principal) => ({ tenantId, principalId });
const scope = (changes = {}) => unifiedMyWorkScopeKey({
  sessionGeneration: ++nextSession,
  tenantId: tenant,
  principalId: principal,
  role: 'tenant_owner',
  businessRole: 'tenant_owner',
  workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
  membershipRevision: 4,
  businessRoleRevision: 9,
  ...changes,
});
const response = (tenantId = tenant, principalId = principal) => ({
  data: {
    schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
    tenant_id: tenantId,
    principal_id: principalId,
    as_of: '2026-11-09T10:00:00+00:00',
    items: [{
      source: 'OPERATIONS', source_key: 'OPERATIONS:WORK-ONE',
      work_item_id: 'WORK-ONE', title: 'Resolve production operations task',
      status: 'OPEN', priority: 'HIGH', due_at: null, is_overdue: false,
    }],
    summary: {
      active_count: 1, overdue_count: 0,
      source_counts: { OPERATIONS: 1 },
    },
    sources_included: ['OPERATIONS'],
    authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
  },
});
const deferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
};

beforeEach(() => api.get.mockReset());

describe('one EOS source-owned My Work read for current authenticated scope', () => {
  it('rejects incomplete scope and does not send protected requests', async () => {
    expect(scope({ principalId: '' })).toBeNull();
    expect(scope({ sessionGeneration: undefined })).toBeNull();
    expect(scope({ sessionGeneration: -1 })).toBeNull();
    await expect(readUnifiedMyWork(null, expected()))
      .rejects.toThrow('MY_WORK_AUTHENTICATED_SCOPE_REQUIRED');
    expect(api.get).not.toHaveBeenCalled();
  });

  it('derives scope only from a current bearer, principal and matching tenant', () => {
    const user = {
      id: principal, tenantId: tenant,
      role: 'tenant_owner', workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
      membershipRevision: 4, businessRoleRevision: 9,
    };
    const auth = {
      isAuthenticated: true, authStage: 'AUTHENTICATED',
      token: 'synthetic-candidate-authorized-by-EOS',
      sessionGeneration: 41, user,
    };
    expect(currentUnifiedMyWorkScope(auth)).toBe(unifiedMyWorkScopeKey({
      tenantId: tenant, principalId: principal,
      role: 'tenant_owner', workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
      sessionGeneration: 41,
      membershipRevision: 4, businessRoleRevision: 9,
    }));
    expect(currentUnifiedMyWorkScope({ ...auth, authStage: 'MFA_REQUIRED' })).toBeNull();
    expect(currentUnifiedMyWorkScope({ ...auth, token: null })).toBeNull();
    expect(currentUnifiedMyWorkScope({ ...auth, isAuthenticated: false })).toBeNull();
    expect(currentUnifiedMyWorkScope(auth, 'FOREIGN-TENANT')).toBeNull();
    expect(currentUnifiedMyWorkScope({
      ...auth, user: { ...user, systemServicesWorkspace: true },
    })).toBeNull();
  });

  it('coalesces overlapping reads for multiple active consumers', async () => {
    const key = scope();
    const pending = deferred();
    const listener = vi.fn();
    const unsubscribe = subscribeUnifiedMyWork(key, listener);
    api.get.mockReturnValue(pending.promise);
    const first = readUnifiedMyWork(key, expected());
    const second = readUnifiedMyWork(key, expected());
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledWith('/my-work', {
      forceNetworkRetry: true, signal: expect.any(AbortSignal),
    });
    pending.resolve(response());
    const both = await Promise.all([first, second]);
    expect(both[0]).toBe(both[1]);
    expect(both[0].summary.active_count).toBe(1);
    expect(listener).not.toHaveBeenCalled();
    unsubscribe();
  });

  it('never shares tenant, principal or revised-capacity data across scopes', async () => {
    const first = scope();
    const foreign = scope({ tenantId: 'FOREIGN-TENANT' });
    const revised = scope({ businessRoleRevision: 10 });
    expect(new Set([first, foreign, revised]).size).toBe(3);
    api.get.mockResolvedValueOnce(response())
      .mockResolvedValueOnce(response('FOREIGN-TENANT', principal))
      .mockResolvedValueOnce(response());
    await readUnifiedMyWork(first, expected());
    await readUnifiedMyWork(foreign, expected('FOREIGN-TENANT'));
    await readUnifiedMyWork(revised, expected());
    expect(api.get).toHaveBeenCalledTimes(3);
    expect(() => releaseUnifiedMyWork(first)).not.toThrow();
    releaseUnifiedMyWork(foreign);
    releaseUnifiedMyWork(revised);
  });

  it('requires the exact requested tenant and principal to match its read key', async () => {
    const key = scope();
    await expect(readUnifiedMyWork(key, expected('FOREIGN-TENANT')))
      .rejects.toThrow('MY_WORK_AUTHENTICATED_SCOPE_INVALID');
    await expect(readUnifiedMyWork(key, expected(tenant, 'FOREIGN-PRINCIPAL')))
      .rejects.toThrow('MY_WORK_AUTHENTICATED_SCOPE_INVALID');
    expect(api.get).not.toHaveBeenCalled();
  });

  it('revalidates after confirmed source-owned work and rejects a prior response', async () => {
    const key = scope();
    const old = deferred();
    const notified = vi.fn();
    const stop = subscribeUnifiedMyWork(key, notified);
    api.get.mockReturnValueOnce(old.promise).mockResolvedValueOnce(response());
    const stale = readUnifiedMyWork(key, expected());
    expect(invalidateUnifiedMyWork(key)).toBe(true);
    expect(notified).toHaveBeenCalledTimes(1);
    const fresh = await readUnifiedMyWork(key, expected());
    old.resolve(response());
    await expect(stale).rejects.toThrow('MY_WORK_READ_SUPERSEDED');
    expect(fresh.summary.active_count).toBe(1);
    expect(api.get).toHaveBeenCalledTimes(2);
    stop();
  });

  it('does not let one cancelled observer cancel other current consumers', async () => {
    const key = scope();
    const pending = deferred();
    const stop = subscribeUnifiedMyWork(key, () => {});
    api.get.mockReturnValue(pending.promise);
    const controller = new AbortController();
    const abandoned = readUnifiedMyWork(key, expected(), { signal: controller.signal });
    const current = readUnifiedMyWork(key, expected());
    controller.abort();
    pending.resolve(response());
    await expect(abandoned).rejects.toThrow('MY_WORK_READ_SUPERSEDED');
    expect((await current).items).toHaveLength(1);
    expect(api.get).toHaveBeenCalledTimes(1);
    stop();
  });

  it('rejects an out-of-date response after the final consumer unmounts', async () => {
    const key = scope();
    const pending = deferred();
    const stop = subscribeUnifiedMyWork(key, () => {});
    api.get.mockReturnValue(pending.promise);
    const old = readUnifiedMyWork(key, expected());
    stop();
    pending.resolve(response());
    await expect(old).rejects.toThrow('MY_WORK_READ_SUPERSEDED');
    releaseUnifiedMyWork(key);
  });

  it('rejects foreign EOS data and permits a later independent read', async () => {
    const key = scope();
    const stop = subscribeUnifiedMyWork(key, () => {});
    api.get.mockResolvedValueOnce(response('FOREIGN-TENANT'))
      .mockResolvedValueOnce(response());
    await expect(readUnifiedMyWork(key, expected()))
      .rejects.toThrow('MY_WORK_SCOPE_MISMATCH');
    expect((await readUnifiedMyWork(key, expected())).tenant_id).toBe(tenant);
    stop();
  });

  it('rejects malformed source counts rather than inventing zero work', async () => {
    const key = scope();
    const stop = subscribeUnifiedMyWork(key, () => {});
    const corrupted = response();
    corrupted.data.summary.active_count = 0;
    api.get.mockResolvedValue(corrupted);
    await expect(readUnifiedMyWork(key, expected()))
      .rejects.toThrow('ATTENTION_PROJECTION_INVALID');
    stop();
  });
});

/*
 * ARTIFACT: unifiedMyWorkSync.test.js
 * VERSION: v1.0.1-CURRENT-SCOPE-CHANGELOG-ALIGNMENT
 * AUTHORITY BOUNDARY: Synthetic client read-coordination certificate only.
 * TENANT POSTURE: Explicit principal, tenant and session revision isolation.
 * FAIL-CLOSED POSTURE: Unknown, stale or invalidated work is never accepted.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
