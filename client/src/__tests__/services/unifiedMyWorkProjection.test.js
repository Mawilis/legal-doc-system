/**
 * TITLE: WILSY OS Unified My Work Projection Contract Tests
 * VERSION: v1.0.0-SOURCE-COVERAGE-CONTRACT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Verifies one shared fail-closed client contract for EOS aggregate
 *          scope, source coverage, row identity and summary reconciliation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/unifiedMyWorkProjection.test.js
 * COLLABORATION / OWNERSHIP: unifiedMyWorkProjection.js and EOS /api/my-work.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-SOURCE-COVERAGE-CONTRACT covers exact tenant/principal
 *            matching, included-source parity, row counts, overdue summaries
 *            and stable labels without creating client permissions.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic in-memory fixtures only.
 * TENANT BOUNDARY: Foreign aggregate scope and item tenant are rejected.
 * AUTHORITY BOUNDARY: Validator grants no source or command permission.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { describe, expect, it } from 'vitest';
import {
  assertUnifiedMyWorkProjection,
  unifiedMyWorkSourceLabel,
} from '../../services/unifiedMyWorkProjection.js';

const valid = () => ({
  schema: 'WILSY-OS-UNIFIED-MY-WORK/V1',
  tenant_id: 'tenant-a',
  principal_id: 'principal-a',
  as_of: '2026-11-09T06:00:00+00:00',
  items: [
    {
      source: 'OPERATIONS',
      source_key: 'OPERATIONS:work-1',
      work_item_id: 'work-1',
      title: 'Review dispatch evidence',
      status: 'OPEN',
      priority: 'HIGH',
      due_at: null,
      is_overdue: false,
    },
    {
      source: 'CRM',
      source_key: 'CRM:work-1',
      work_item_id: 'work-1',
      title: 'Follow up with customer',
      status: 'OPEN',
      priority: 'NORMAL',
      due_at: null,
      is_overdue: true,
    },
  ],
  summary: {
    active_count: 2,
    overdue_count: 1,
    source_counts: { OPERATIONS: 1, CRM: 1 },
  },
  sources_included: ['OPERATIONS', 'CRM'],
  authority: { commands_owned_by: 'SOURCE_SERVICES', permits_completion: false },
});

describe('unified My Work projection contract', () => {
  it('accepts source-key collisions across independently owned registries', () => {
    const payload = valid();
    expect(assertUnifiedMyWorkProjection(payload, {
      tenantId: 'tenant-a',
      principalId: 'principal-a',
    })).toBe(payload);
  });

  it('rejects a tenant or principal mismatch', () => {
    expect(() => assertUnifiedMyWorkProjection(valid(), {
      tenantId: 'tenant-b',
    })).toThrow('MY_WORK_SCOPE_MISMATCH');
    expect(() => assertUnifiedMyWorkProjection(valid(), {
      principalId: 'principal-b',
    })).toThrow('MY_WORK_SCOPE_MISMATCH');
  });

  it('rejects unknown source coverage and permits an included empty source', () => {
    const unknown = valid();
    unknown.sources_included = ['OPERATIONS', 'CRM', 'HR'];
    unknown.summary.source_counts = { OPERATIONS: 1, CRM: 1, HR: 0 };
    expect(() => assertUnifiedMyWorkProjection(unknown))
      .toThrow('ATTENTION_SOURCE_COVERAGE_INVALID');

    const empty = valid();
    empty.items = [];
    empty.sources_included = ['OPERATIONS'];
    empty.summary = { active_count: 0, overdue_count: 0, source_counts: { OPERATIONS: 0 } };
    expect(assertUnifiedMyWorkProjection(empty)).toBe(empty);
  });

  it('rejects source counts that diverge from rows and active total', () => {
    const payload = valid();
    payload.summary.source_counts.CRM = 0;
    expect(() => assertUnifiedMyWorkProjection(payload))
      .toThrow('ATTENTION_SOURCE_COVERAGE_INVALID');
  });

  it('rejects duplicate source keys and mismatched overdue totals', () => {
    const duplicate = valid();
    duplicate.items[1] = {...duplicate.items[0]};
    duplicate.summary.source_counts = { OPERATIONS: 2 };
    duplicate.sources_included = ['OPERATIONS'];
    duplicate.summary.overdue_count = 0;
    expect(() => assertUnifiedMyWorkProjection(duplicate)).toThrow('ATTENTION_ITEM_INVALID');

    const incorrectOverdue = valid();
    incorrectOverdue.summary.overdue_count = 0;
    expect(() => assertUnifiedMyWorkProjection(incorrectOverdue)).toThrow('ATTENTION_SUMMARY_INVALID');
  });

  it('returns a known source label without labelling unknown sources', () => {
    expect(unifiedMyWorkSourceLabel('LEGAL')).toBe('Legal');
    expect(unifiedMyWorkSourceLabel('HR')).toBeNull();
  });
});

/*
 * ARTIFACT: unifiedMyWorkProjection.test.js
 * VERSION: v1.0.0-SOURCE-COVERAGE-CONTRACT
 * AUTHORITY BOUNDARY: Deterministic projection contract evidence only.
 * TENANT POSTURE: Synthetic exact-scope and mismatch tests.
 * FAIL-CLOSED POSTURE: Unknown or divergent source metadata is rejected.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
