/**
 * WILSY OS — PW-P11C PRODUCTIVE-WORK CLIENT ADAPTER CERTIFICATE
 * VERSION: v1.0.0-PW-P11C-PRODUCTIVE-WORK-CLIENT-CERT
 * AUTHORITY: Browser transport validation only.
 * TENANT BOUNDARY: No tenant/principal selector is accepted by the adapter.
 * FINANCIAL AUTHORITY BOUNDARY: None.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockGet } = vi.hoisted(() => ({
  mockGet: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: {
    get: mockGet,
  },
}));

vi.mock('../../utils/sovereignClient.js', () => ({
  default: {},
}));

import {
  getLegalProductiveWork,
} from '../../services/legalOperationsService.js';

const workItem = (id, dueAt = null) => ({
  schema: 'WILSY-LEGAL-WORK-ITEM/V1',
  work_item_version: 'v1.0.1-G7E-LEGAL-WORK-ITEM',
  work_item_id: id,
  tenant_id: 'tenant-law',
  case_matter_id: 'matter-1',
  title: `Work ${id}`,
  source_kind: 'LEGAL_WORKFLOW_STAGE',
  source_reference: `stage:${id}`,
  source_evidence_fingerprint: 'a'.repeat(128),
  status: 'OPEN',
  created_at: '2026-10-16T00:00:00+00:00',
  due_at: dueAt,
  completion_evidence_reference: null,
  completion_evidence_fingerprint: null,
  completed_at: null,
  cancellation_reason_reference: null,
  cancelled_at: null,
  fingerprint: 'b'.repeat(128),
});

const payload = () => ({
  schema: 'WILSY-LEGAL-PROFILE-PRODUCTIVE-WORK/V1',
  version: 'v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION',
  http_version: 'v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-READ-API',
  tenant_id: 'tenant-law',
  principal_id: 'principal-law',
  as_of: '2026-10-16T01:00:00+00:00',
  operating_contexts: [
    {
      operating_role_id: 'role-corporate',
      operating_role_revision: 2,
      display_name: 'Corporate Attorney',
      capability_ids: ['PRACTICE_CORPORATE'],
      office_references: ['office:jhb'],
      practice_references: ['practice:corporate'],
      business_unit_references: [],
      jurisdiction_references: ['jurisdiction:ZA'],
    },
  ],
  capability_ids: ['PRACTICE_CORPORATE'],
  assigned_work_items: [
    workItem('work-1', '2026-10-16T08:00:00+00:00'),
  ],
  supervised_work_items: [],
  overdue_work_items: [],
  due_soon_work_items: [
    workItem('work-1', '2026-10-16T08:00:00+00:00'),
  ],
});

describe('PW-P11C productive-work client adapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('uses the exact authenticated own-principal endpoint with no browser scope selectors', async () => {
    mockGet.mockResolvedValue({
      data: payload(),
    });

    const result = await getLegalProductiveWork();

    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/productive-work',
    );

    expect(result.tenantId).toBe('tenant-law');
    expect(result.principalId).toBe('principal-law');

    expect(result.assignedWorkItems).toEqual([
      expect.objectContaining({
        workItemId: 'work-1',
        caseMatterId: 'matter-1',
        status: 'OPEN',
      }),
    ]);

    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.assignedWorkItems)).toBe(true);
  });

  it('rejects foreign-tenant work rows instead of filtering them silently', async () => {
    const malformed = payload();
    malformed.assigned_work_items[0] = {
      ...malformed.assigned_work_items[0],
      tenant_id: 'foreign-tenant',
    };

    mockGet.mockResolvedValue({
      data: malformed,
    });

    await expect(
      getLegalProductiveWork(),
    ).rejects.toThrow(
      'LEGAL_OPERATIONS_PRODUCTIVE_WORK_RESPONSE_INVALID',
    );
  });

  it('rejects extra response fields and terminal work posture', async () => {
    const malformed = payload();

    malformed.extra_authority = true;
    malformed.assigned_work_items[0] = {
      ...malformed.assigned_work_items[0],
      status: 'COMPLETED',
    };

    mockGet.mockResolvedValue({
      data: malformed,
    });

    await expect(
      getLegalProductiveWork(),
    ).rejects.toThrow(
      'LEGAL_OPERATIONS_PRODUCTIVE_WORK_RESPONSE_INVALID',
    );
  });
});

/**
 * ARTIFACT: legalOperationsProductiveWork.test.js
 * VERSION: v1.0.0-PW-P11C-PRODUCTIVE-WORK-CLIENT-CERT
 * AUTHORITY BOUNDARY: authenticated read adaptation only
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
