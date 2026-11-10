/**
 * TITLE: WILSY OS Daily Attention Feed Client Contract Certificate
 * VERSION: v1.0.0-EXACT-EOS-ATTENTION-SCOPE-CERT
 * AUTHORITY: WILSY OS Core Engineering disposable verification.
 * EPITOME: Prove current-principal feed read, real source coverage checks,
 *          command non-authority, cursor and foreign-tenant rejection.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/attentionFeedClient.test.js
 * COLLABORATION / OWNERSHIP: attentionFeedClient.js and EOS attention_router.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.0-EXACT-EOS-ATTENTION-SCOPE-CERT verifies bounded
 *          source-admitted list evidence and rejects fabricated client authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant/work, no browser tokens stored.
 * TENANT BOUNDARY: Current tenant/principal required for every feed page.
 * AUTHORITY BOUNDARY: GET only; no completion/approval write.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({ api: { get: vi.fn() } }));
vi.mock('../../services/api.js', () => ({ default: api }));

import {
  assertAttentionFeed, readAttentionFeed,
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

beforeEach(() => api.get.mockReset());

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
});

// ARTIFACT: client/src/__tests__/services/attentionFeedClient.test.js
// VERSION: v1.0.0-EXACT-EOS-ATTENTION-SCOPE-CERT
// AUTHORITY BOUNDARY: Verified HTTP read only; no browser command authority.
// TENANT POSTURE: Exact current tenant and principal required for every page.
// FAIL-CLOSED POSTURE: Foreign identities, unknown sources/actions and count drift reject.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
