/**
 * TITLE: WILSY OS Daily Attention Feed Client Contract Certificate
 * VERSION: v1.3.0-INDEPENDENT-SOURCE-ADMISSION-CERT
 * AUTHORITY: WILSY OS Core Engineering disposable verification.
 * EPITOME: Prove current-principal feed read, real source coverage checks,
 *          command non-authority, cursor and foreign-tenant rejection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/attentionFeedClient.test.js
 * COLLABORATION / OWNERSHIP: attentionFeedClient.js and EOS attention_router.
 * CERTIFICATION / UPDATE DATE: 2026-11-11
 * CHANGELOG: v1.3.0-INDEPENDENT-SOURCE-ADMISSION-CERT
 *          proves that a failing Operations capability service cannot
 *          suppress independently verified CRM task actions.
 *          v1.2.0-IDEMPOTENT-SOURCE-CREATION-CERT verifies
 *          CRM and module create/complete routes, exact tenant readback,
 *          and source-owned idempotency header forwarding.
 *          v1.1.0-SOURCE-COMPLETION-TRANSPORT-CERT checks
 *          exact-principal command availability and real module completion
 *          dispatch, while rejecting foreign and unsupported commands.
 *          v1.0.0-EXACT-EOS-ATTENTION-SCOPE-CERT verifies bounded
 *          source-admitted list evidence and rejects fabricated client authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant/work, no browser tokens stored.
 * TENANT BOUNDARY: Current tenant/principal required for every feed page.
 * AUTHORITY BOUNDARY: EOS capability read; module IAM reauthorizes actual completion.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({ api: { get: vi.fn(), post: vi.fn() } }));
vi.mock('../../services/api.js', () => ({ default: api }));

import {
  assertAttentionFeed, readAttentionFeed,
  readAttentionSourceActions, completeAttentionSourceWork,
  createAttentionSourceWork,
} from '../../services/attentionFeedClient.js';

const tenantId = 'WILSY-ATTENTION-CLIENT-TENANT';
const principalId = 'WILSY-ATTENTION-CLIENT-PRINCIPAL';
const scope = { tenantId, principalId };
const response = () => ({
  schema: 'WILSY-OS-ATTENTION-FEED/V1',
  tenantId,
  principalId,
  syncedAt: '2026-11-10T10:00:00+00:00',
  view: 'active',
  items: [{
    id: 'OPERATIONS:WORK-1',
    tenantId,
    sourceModule: 'OPERATIONS',
    sourceRecordId: 'WORK-1',
    title: 'Complete tenant operations work',
    summary: 'Authenticated source item',
    status: 'OPEN',
    priority: 'HIGH',
    urgencyScore: 55,
    whyRanked: 'High source priority',
    dueAt: null,
    actionHints: ['OPEN'],
    deepLink: '/my-work',
    authzScope: 'SOURCE_SERVICE_ONLY',
    isOverdue: false,
  }],
  counts: { active: 1, overdue: 0, dueToday: 0, highPriority: 1 },
  sources: [{ moduleId: 'OPERATIONS', state: 'ok', count: 1 }],
  coverage: {
    admittedSources: ['OPERATIONS'],
    notRepresentedSources: ['FINANCE', 'PEOPLE'],
    completeEnterpriseCoverage: false,
  },
  filteredTotal: 1,
  nextCursor: null,
  authority: { commandsOwnedBy: 'SOURCE_SERVICES', attentionCommandsEnabled: false },
});

beforeEach(() => { api.get.mockReset(); api.post.mockReset(); });

describe('EOS authoritative AttentionItem feed browser boundary', () => {
  it('requests exact authenticated filters and validates the source snapshot', async () => {
    api.get.mockResolvedValue({ data: response() });
    const feed = await readAttentionFeed(scope, { view: 'active', limit: 50 });
    expect(feed.items[0].title).toBe('Complete tenant operations work');
    expect(api.get).toHaveBeenCalledWith('/attention/feed', {
      params: { view: 'active', limit: 50 },
      forceNetworkRetry: true,
    });
    expect(feed.authority.attentionCommandsEnabled).toBe(false);
  });

  it('does not send work requests without exact user and tenant scope', async () => {
    await expect(readAttentionFeed({ tenantId, principalId: '' }))
      .rejects.toThrow('ATTENTION_AUTHENTICATED_SCOPE_REQUIRED');
    expect(api.get).not.toHaveBeenCalled();
  });

  it('rejects foreign identity, missing source coverage or invented actions', () => {
    const foreign = response();
    foreign.tenantId = 'FOREIGN';
    expect(() => assertAttentionFeed(foreign, scope)).toThrow('ATTENTION_FEED_PROJECTION_INVALID');

    const fabricated = response();
    fabricated.items[0].actionHints = ['APPROVE'];
    expect(() => assertAttentionFeed(fabricated, scope)).toThrow('ATTENTION_ITEM_INVALID');

    const unknown = response();
    unknown.sources = [{ moduleId: 'PEOPLE', state: 'ok', count: 1 }];
    expect(() => assertAttentionFeed(unknown, scope)).toThrow('ATTENTION_SOURCE_COVERAGE_INVALID');
  });

  it('rejects inflated counts and synthetic enterprise-cleared claims', () => {
    const excessive = response();
    excessive.counts.highPriority = 2;
    expect(() => assertAttentionFeed(excessive, scope)).toThrow('ATTENTION_SOURCE_COUNTS_INVALID');

    const falselyComplete = response();
    falselyComplete.coverage.completeEnterpriseCoverage = true;
    expect(() => assertAttentionFeed(falselyComplete, scope)).toThrow('ATTENTION_FEED_PROJECTION_INVALID');
  });

  it('transports bound cursor, source and query without constructing permissions', async () => {
    api.get.mockResolvedValue({ data: { ...response(), nextCursor: 'offset-token' } });
    await readAttentionFeed(scope, {
      sources: 'OPERATIONS', q: 'record', cursor: 'cursor-1',
    });
    expect(api.get).toHaveBeenCalledWith('/attention/feed', {
      params: {
        view: 'active', sources: 'OPERATIONS', q: 'record',
        cursor: 'cursor-1', limit: 50,
      },
      forceNetworkRetry: true,
    });
  });
  it('accepts only exact-session EOS-authorised source completion availability', async () => {
    api.get.mockResolvedValue({ data: {
      schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
      tenantId, principalId, authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
      sourceActions: { OPERATIONS: ['COMPLETE'] },
    } });
    const actions = await readAttentionSourceActions(scope);
    expect(actions).toEqual({ OPERATIONS: ['COMPLETE'] });
    expect(api.get).toHaveBeenCalledWith('/attention/actions', { forceNetworkRetry: true });

    api.get.mockResolvedValueOnce({ data: {
      schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
      tenantId: 'FOREIGN', principalId,
      authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
      sourceActions: { OPERATIONS: ['COMPLETE'] },
    } });
    await expect(readAttentionSourceActions(scope))
      .rejects.toThrow('ATTENTION_ACTION_AVAILABILITY_INVALID');
    await expect(readAttentionSourceActions({ tenantId, principalId: '' }))
      .rejects.toThrow('ATTENTION_AUTHENTICATED_SCOPE_REQUIRED');
  });

  it('delegates Operations completion to source IAM without optimistic mutation', async () => {
    api.post.mockResolvedValue({ data: { work_item_id: 'WORK-1', tenant_id: tenantId, status: 'COMPLETED' } });
    const record = await completeAttentionSourceWork({
      sourceModule: 'OPERATIONS', sourceRecordId: 'WORK-1', tenantId,
    }, 'Completed all verified assigned work');
    expect(record.status).toBe('COMPLETED');
    expect(api.post).toHaveBeenCalledWith(
      '/tenant-modules/operations/workspace/work-items/WORK-1/complete',
      { completion_note: 'Completed all verified assigned work' },
    );
    api.post.mockClear();
    await expect(completeAttentionSourceWork({
      sourceModule: 'FINANCE', sourceRecordId: 'WORK-1',
    }, 'Anything')).rejects.toThrow('ATTENTION_SOURCE_COMPLETION_INPUT_INVALID');
    expect(api.post).not.toHaveBeenCalled();
  });

  it('creates CRM source work with an exact-tenant idempotent EOS command', async () => {
    api.post.mockResolvedValue({ data: {
      work_item_id: 'CRM-1', tenant_id: tenantId, status: 'OPEN',
    } });
    const record = await createAttentionSourceWork('CRM', scope, {
      title: 'Review customer contract',
      description: 'Record customer decision',
      priority: 'HIGH',
    }, 'source-intent-once');
    expect(record.work_item_id).toBe('CRM-1');
    expect(api.post).toHaveBeenCalledWith(
      '/crm/owner-workspace/work-items',
      { title: 'Review customer contract', description: 'Record customer decision',
        kind: 'TASK', priority: 'HIGH', due_at: null },
      { headers: { 'Idempotency-Key': 'source-intent-once' } },
    );
    api.post.mockClear();
    await expect(createAttentionSourceWork('FINANCE', scope, {
      title: 'Unauthorized source task',
    }, 'source-intent')).rejects.toThrow('ATTENTION_SOURCE_CREATE_INPUT_INVALID');
    expect(api.post).not.toHaveBeenCalled();
  });

  it('rejects foreign source mutation readback instead of showing fabricated success', async () => {
    api.post.mockResolvedValue({ data: {
      work_item_id: 'CRM-1', tenant_id: 'FOREIGN', status: 'OPEN',
    } });
    await expect(createAttentionSourceWork('CRM', scope, {
      title: 'Review customer contract',
    }, 'source-intent-once')).rejects.toThrow('ATTENTION_SOURCE_CREATE_READBACK_INVALID');
  });

  it('keeps CRM create/complete available if Operations command verification fails', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/attention/actions/crm') return Promise.resolve({ data: {
        schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
        tenantId, principalId, authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
        sourceActions: { CRM: ['CREATE', 'COMPLETE'] },
      } });
      if (url === '/attention/actions/operations') {
        return Promise.reject(Object.assign(new Error('AUTHORITY_DEPENDENCY_UNAVAILABLE'), {
          response: { status: 503 },
        }));
      }
      throw new Error('UNEXPECTED_ATTENTION_ACTION_ROUTE');
    });
    const result = await readAttentionSourceActions(scope, ['CRM', 'OPERATIONS']);
    expect(result).toEqual({
      sourceActions: { CRM: ['CREATE', 'COMPLETE'] },
      unavailableSources: ['OPERATIONS'],
    });
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it('distinguishes canonical denial from command unavailability', async () => {
    api.get.mockResolvedValue({ data: {
      schema: 'WILSY-OS-ATTENTION-ACTION-AVAILABILITY/V1',
      tenantId, principalId, authority: 'SOURCE_COMMAND_ENDPOINTS_REAUTHORIZE',
      sourceActions: {},
    } });
    expect(await readAttentionSourceActions(scope, ['CRM'])).toEqual({
      sourceActions: {}, unavailableSources: [],
    });
  });

});

// ARTIFACT: client/src/__tests__/services/attentionFeedClient.test.js
// VERSION: v1.3.0-INDEPENDENT-SOURCE-ADMISSION-CERT
// AUTHORITY BOUNDARY: Capability availability verified; source IAM owns each completion.
// TENANT POSTURE: Exact current tenant and principal required for every page.
// FAIL-CLOSED POSTURE: Foreign identities, unknown sources/actions and count drift reject.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
