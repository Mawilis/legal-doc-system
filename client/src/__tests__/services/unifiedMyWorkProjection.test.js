/**
 * TITLE: WILSY OS Unified My Work Projection Contract Tests
 * VERSION: v1.5.0-SOURCE-TASK-DESTINATION-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Verifies one shared fail-closed client contract for EOS aggregate
 *          scope, source coverage, row identity and summary reconciliation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/unifiedMyWorkProjection.test.js
 * COLLABORATION / OWNERSHIP: unifiedMyWorkProjection.js and EOS /api/my-work.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.5.0-SOURCE-TASK-DESTINATION-CERT proves identical source-local IDs in CRM and Projects never cross-route: CRM opens the current source-owned My Work task shell, Projects returns its existing separately authorized task locator; malformed source keys fail closed.
 * CHANGELOG: v1.4.1-MIXED-EOS-READINESS-CERT confirms
 *            absent legacy readiness keeps the queue available with unknown
 *            readiness, while incomplete/forged evidence is rejected.
 * CHANGELOG: v1.4.0-PROJECT-READINESS-CLIENT-CERT verifies
 *            strict readiness/count reconciliation for Projects rows.
 * CHANGELOG: v1.3.0-SOURCE-AUDIENCE-CLIENT-DENIAL-CERT checks
 *            that only evidenced Operating/Platform labels pass and that
 *            absent categories, unsupported claims and fabricated critical
 *            gates cannot invent a verified work purpose.
 * CHANGELOG: v1.2.0-PROJECTS-SOURCE-READBACK-CLIENT-CERT certifies
 *            the source-admitted PROJECTS queue, own assignment, blocker,
 *            deadline-only metadata and rejection of a forged project ID.
 * CHANGELOG: v1.2.0-PROJECTS-SOURCE-READBACK-CLIENT-CERT certifies the existing,
 *            server-owned HR source label and count coverage without granting
 *            browser HR capability. v1.0.0-SOURCE-COVERAGE-CONTRACT covers exact tenant/principal
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
  resolveUnifiedWorkDestination,
  resolveUnifiedWorkRoute,
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

  it('admits proven source audience and preserves unclassified legacy rows', () => {
    const legacy = valid();
    expect(assertUnifiedMyWorkProjection(legacy)).toBe(legacy);
    const typed = valid();
    typed.items[0].audience = 'OPERATING';
    typed.items[0].audience_evidence_ref = 'source-audit-revision-3';
    typed.items[0].audience_source_revision = 3;
    typed.items[0].critical_gate = false;
    typed.items[1].audience = 'UNCLASSIFIED';
    typed.items[1].audience_evidence_ref = null;
    typed.items[1].audience_source_revision = null;
    typed.items[1].critical_gate = false;
    expect(assertUnifiedMyWorkProjection(typed)).toBe(typed);
  });

  it('rejects unsupported source audience, unproven classification and fabricated critical gate', () => {
    for (const changes of [
      { audience: 'OPERATING', critical_gate: false, audience_evidence_ref: null, audience_source_revision: 3 },
      { audience: 'PLATFORM_BUILD', critical_gate: true, audience_evidence_ref: null, audience_source_revision: 3 },
      { audience: 'OPERATING', critical_gate: true, audience_evidence_ref: 'audit', audience_source_revision: 3 },
      { audience: 'UNCLASSIFIED', critical_gate: true, audience_evidence_ref: null, audience_source_revision: null },
      { audience: 'DEVELOPMENT', critical_gate: false, audience_evidence_ref: 'audit', audience_source_revision: 3 },
    ]) {
      const payload = valid();
      payload.items[0] = { ...payload.items[0], ...changes };
      expect(() => assertUnifiedMyWorkProjection(payload)).toThrow('ATTENTION_ITEM_INVALID');
    }
  });

  it('rejects a tenant or principal mismatch', () => {
    expect(() => assertUnifiedMyWorkProjection(valid(), {
      tenantId: 'tenant-b',
    })).toThrow('MY_WORK_SCOPE_MISMATCH');
    expect(() => assertUnifiedMyWorkProjection(valid(), {
      principalId: 'principal-b',
    })).toThrow('MY_WORK_SCOPE_MISMATCH');
  });

  it('recognizes the EOS-owned HR source and permits an included empty source', () => {
    const hr = valid();
    hr.sources_included = ['OPERATIONS', 'CRM', 'HR'];
    hr.summary.source_counts = { OPERATIONS: 1, CRM: 1, HR: 0 };
    expect(assertUnifiedMyWorkProjection(hr)).toBe(hr);

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

  it('accepts a verified delegated and blocked PROJECTS source without invented due instant', () => {
    const payload = valid();
    const projectId = 'prj-' + 'a'.repeat(48);
    const taskId = 'ptk-' + 'b'.repeat(48);
    payload.items = [{
      tenant_id: 'tenant-a', source: 'PROJECTS',
      source_key: 'PROJECTS:' + taskId, work_item_id: taskId,
      title: 'Resolve external blocker', status: 'BLOCKED',
      priority: 'NORMAL', due_at: null, due_date: '2026-12-01',
      project_id: projectId, owner_principal_id: 'principal-a',
      dependency_total: 1, dependency_remaining: 1, dependency_readiness: 'WAITING',
      is_overdue: false, action_authority: 'SOURCE_SERVICE_ONLY',
      completion_route: null,
    }];
    payload.summary = {
      active_count: 1, overdue_count: 0, source_counts: { PROJECTS: 1 },
    };
    payload.sources_included = ['PROJECTS'];
    expect(assertUnifiedMyWorkProjection(payload, {
      tenantId: 'tenant-a', principalId: 'principal-a',
    })).toBe(payload);
    expect(unifiedMyWorkSourceLabel('PROJECTS')).toBe('Projects & Delivery');

    // Rolling client/backend versions must not hide otherwise authorized work.
    // Missing source evidence remains unknown rather than claiming READY.
    const legacy = structuredClone(payload);
    delete legacy.items[0].dependency_total;
    delete legacy.items[0].dependency_remaining;
    delete legacy.items[0].dependency_readiness;
    expect(assertUnifiedMyWorkProjection(legacy)).toBe(legacy);
    expect(legacy.items[0].dependency_readiness).toBeUndefined();

    const partial = structuredClone(legacy);
    partial.items[0].dependency_total = 1;
    expect(() => assertUnifiedMyWorkProjection(partial)).toThrow('ATTENTION_ITEM_INVALID');

    const tampered = structuredClone(payload);
    tampered.items[0].dependency_readiness = 'READY';
    expect(() => assertUnifiedMyWorkProjection(tampered)).toThrow('ATTENTION_ITEM_INVALID');
    const invalidCount = structuredClone(payload);
    invalidCount.items[0].dependency_remaining = 2;
    expect(() => assertUnifiedMyWorkProjection(invalidCount)).toThrow('ATTENTION_ITEM_INVALID');

    const forged = structuredClone(payload);
    forged.items[0].owner_principal_id = 'other-principal';
    expect(() => assertUnifiedMyWorkProjection(forged)).toThrow('ATTENTION_ITEM_INVALID');
    const wrongProject = structuredClone(payload);
    wrongProject.items[0].project_id = 'foreign';
    expect(() => assertUnifiedMyWorkProjection(wrongProject)).toThrow('ATTENTION_ITEM_INVALID');
    const fabricatedInstant = structuredClone(payload);
    fabricatedInstant.items[0].due_at = '2026-12-01T00:00:00+00:00';
    expect(() => assertUnifiedMyWorkProjection(fabricatedInstant)).toThrow('ATTENTION_ITEM_INVALID');
  });

  it('routes each verified work identity to its owning task experience without crossing source authority', () => {
    const crm = resolveUnifiedWorkDestination({
      source: 'CRM', source_key: 'CRM:same-local-id', work_item_id: 'same-local-id',
    });
    expect(crm).toEqual({ kind: 'MY_WORK_TASK',
      href: '/headquarters?section=my-work&work=CRM%3Asame-local-id' });
    const id = 'ptk-' + 'b'.repeat(48);
    const project = 'prj-' + 'a'.repeat(48);
    const projects = resolveUnifiedWorkDestination({
      source: 'PROJECTS', source_key: 'PROJECTS:' + id,
      work_item_id: id, project_id: project,
    });
    expect(projects).toEqual({ kind: 'PROJECTS_TASK', locator: {
      workspace: 'PROJECTS', project_id: project,
      task_id: id, participant_view: true,
    } });
    expect(() => resolveUnifiedWorkDestination({
      source: 'CRM', source_key: 'PROJECTS:same-local-id', work_item_id: 'same-local-id',
    })).toThrow('MY_WORK_NAVIGATION_SOURCE_INVALID');
    expect(() => resolveUnifiedWorkDestination({
      source: 'PROJECTS', source_key: 'PROJECTS:' + id,
      work_item_id: id, project_id: 'foreign-project',
    })).toThrow('MY_WORK_PROJECT_DESTINATION_INVALID');
  });

  it('routes Calendar and Daily Attention directly to canonical task destinations without fallback', () => {
    const projectId = 'prj-' + 'a'.repeat(48);
    const taskId = 'ptk-' + 'b'.repeat(48);
    const projects = resolveUnifiedWorkRoute({
      source: 'PROJECTS', source_key: 'PROJECTS:' + taskId,
      project_id: projectId, work_item_id: taskId,
    });
    expect(projects).toEqual({
      pathname: '/headquarters',
      search: '?section=projects&project=' + projectId + '&task=' + taskId,
      state: null,
    });
    const crm = resolveUnifiedWorkRoute({
      source: 'CRM', source_key: 'CRM:CRM-7', work_item_id: 'CRM-7',
    });
    expect(crm).toEqual({
      pathname: '/my-work', search: '',
      state: { focusWorkItem: 'CRM:CRM-7' },
    });
    expect(() => resolveUnifiedWorkRoute({
      source: 'PROJECTS', project_id: projectId,
      source_key: 'CRM:' + taskId, work_item_id: taskId,
    })).toThrow('MY_WORK_NAVIGATION_SOURCE_INVALID');
    expect(() => resolveUnifiedWorkRoute({
      source: 'PROJECTS', project_id: 'not-admitted',
      source_key: 'PROJECTS:' + taskId, work_item_id: taskId,
    })).toThrow('MY_WORK_PROJECT_DESTINATION_INVALID');
  });

  it('returns a known source label without labelling unknown sources', () => {
    expect(unifiedMyWorkSourceLabel('LEGAL')).toBe('Legal');
    expect(unifiedMyWorkSourceLabel('HR')).toBe('HR & Hiring');
    expect(unifiedMyWorkSourceLabel('UNKNOWN')).toBeNull();
  });
});

/*
 * ARTIFACT: unifiedMyWorkProjection.test.js
 * VERSION: v1.5.0-SOURCE-TASK-DESTINATION-CERT
 * AUTHORITY BOUNDARY: Deterministic projection contract evidence only.
 * TENANT POSTURE: Synthetic exact-scope and mismatch tests.
 * FAIL-CLOSED POSTURE: Unknown or divergent source metadata is rejected.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
