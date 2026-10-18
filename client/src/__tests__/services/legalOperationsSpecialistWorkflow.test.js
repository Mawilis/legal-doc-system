/**
 * WILSY OS — P3 SPECIALIST-WORKFLOW CLIENT ADAPTER CERTIFICATE
 * VERSION: v1.0.0-P3-SPECIALIST-WORKFLOW-CLIENT-CERT
 * AUTHORITY: Strict browser transport validation only.
 * EPITOME: Admit only deterministic own-principal workflow explanation; never
 *          manufacture productive-work rows or execution authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/legalOperationsSpecialistWorkflow.test.js
 * CERTIFICATION / UPDATE DATE: 2026-10-18
 * TENANT BOUNDARY: No tenant or principal selector is accepted.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));

vi.mock('../../services/api.js', () => ({
  default: { get: mockGet },
}));

vi.mock('../../utils/sovereignClient.js', () => ({ default: {} }));

import { getLegalSpecialistWorkflow } from '../../services/legalOperationsService.js';

const row = (workItemId = 'work-1') => ({
  work_item_id: workItemId,
  case_matter_id: 'matter-1',
  workflow_instance_id: 'workflow-1',
  workflow_definition_id: 'definition-1',
  stage_definition_id: 'stage-review',
  readiness: 'BLOCKED_DEPENDENCY_AND_GATE',
  blocking_dependency_work_item_ids: ['work-0'],
  unsatisfied_gate_references: ['PARTNER_REVIEW'],
  materialization_transition_id: 'transition-1',
  materialization_receipt_id: 'receipt-1',
});

const payload = () => ({
  schema: 'WILSY-LEGAL-SPECIALIST-WORKFLOW-PROJECTION/V1',
  version: 'v1.0.0-P0-LEGAL-SPECIALIST-WORKFLOW-PROJECTION',
  http_version: 'v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP',
  tenant_id: 'tenant-law',
  principal_id: 'principal-law',
  as_of: '2026-10-18T10:00:00+00:00',
  rows: [row()],
});

describe('P3 specialist-workflow client adapter', () => {
  beforeEach(() => vi.clearAllMocks());

  it('uses the authenticated endpoint without browser scope selectors', async () => {
    mockGet.mockResolvedValue({ data: payload() });
    const result = await getLegalSpecialistWorkflow();

    expect(mockGet).toHaveBeenCalledWith('/legal-operations/specialist-workflow');
    expect(result.rows[0]).toEqual(expect.objectContaining({
      workItemId: 'work-1',
      readiness: 'BLOCKED_DEPENDENCY_AND_GATE',
      blockingDependencyWorkItemIds: ['work-0'],
      unsatisfiedGateReferences: ['PARTNER_REVIEW'],
    }));
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.rows)).toBe(true);
  });

  it.each([
    ['unknown readiness', (value) => { value.rows[0].readiness = 'READY_TO_EXECUTE'; }],
    ['unsorted rows', (value) => { value.rows = [row('work-2'), row('work-1')]; }],
    ['duplicate tokens', (value) => { value.rows[0].unsatisfied_gate_references = ['GATE', 'GATE']; }],
    ['extra authority', (value) => { value.rows[0].can_transition = true; }],
    ['scope drift', (value) => { value.rows[0].case_matter_id = ''; }],
  ])('rejects %s', async (_label, mutate) => {
    const malformed = payload();
    mutate(malformed);
    mockGet.mockResolvedValue({ data: malformed });

    await expect(getLegalSpecialistWorkflow()).rejects.toThrow(
      'LEGAL_OPERATIONS_SPECIALIST_WORKFLOW_RESPONSE_INVALID',
    );
  });
});

// =============================================================================
// WILSY OS SOVEREIGN ARTIFACT SEAL
// =============================================================================
// ARTIFACT: legalOperationsSpecialistWorkflow.test.js
// VERSION: v1.0.0-P3-SPECIALIST-WORKFLOW-CLIENT-CERT
// AUTHORITY BOUNDARY: Browser read validation only
// TENANT POSTURE: Server-derived scope only
// FAIL-CLOSED POSTURE: Schema, scope, order or vocabulary drift rejects
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
