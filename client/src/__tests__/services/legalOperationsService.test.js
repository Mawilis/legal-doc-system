/**
 * WILSY OS — SHERIFF OPERATIONAL QUEUE CLIENT CERTIFICATE
 * VERSION: v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT-CERT
 * AUTHORITY: Client transport-adapter contract certification only.
 * EPITOME: Certifies exact endpoint use, bounded response adaptation, immutable
 *          queue arrays, malformed-shape rejection, and tenant-drift rejection
 *          without network, IAM, lifecycle, deputy, billing, AI, or financial
 *          authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/legalOperationsService.test.js
 * CERTIFICATION / UPDATE DATE: 2026-09-23
 * CHANGELOG: 2026-09-23 v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT-CERT certifies immutable queue-row objects and
 *            rebinds the adapter certificate to production v1.0.1.
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

import {
  LEGAL_OPERATIONS_CLIENT_VERSION,
  __legalOperationsServiceInternals,
  getSheriffOperationalQueues,
} from '../../services/legalOperationsService.js';

const payload = () => ({
  tenant_id: 'tenant-sheriff',
  visibility: 'SHERIFF_OPERATIONAL_QUEUE',
  office_receipt: [
    {
      tenant_id: 'tenant-sheriff',
      document_id: 'document-1',
      state: 'REGISTERED',
    },
  ],
  deputy_assignment: [
    {
      tenant_id: 'tenant-sheriff',
      document_id: 'document-2',
      state: 'RECEIVED',
    },
  ],
  active_attempts: [
    {
      tenant_id: 'tenant-sheriff',
      attempt_id: 'attempt-1',
      deputy_id: 'deputy-1',
      state: 'ALLOCATED',
    },
  ],
});

describe('L8-6A sheriff operational queue client adapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('uses the governed queue endpoint and adapts only the certified queues', async () => {
    mockGet.mockResolvedValueOnce({ data: payload() });

    const result = await getSheriffOperationalQueues();

    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/operational-queues',
    );
    expect(result).toEqual({
      tenantId: 'tenant-sheriff',
      visibility: 'SHERIFF_OPERATIONAL_QUEUE',
      officeReceipt: payload().office_receipt,
      deputyAssignment: payload().deputy_assignment,
      activeAttempts: payload().active_attempts,
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result.officeReceipt)).toBe(true);
    expect(Object.isFrozen(result.deputyAssignment)).toBe(true);
    expect(Object.isFrozen(result.activeAttempts)).toBe(true);
    expect(Object.isFrozen(result.officeReceipt[0])).toBe(true);
    expect(Object.isFrozen(result.deputyAssignment[0])).toBe(true);
    expect(Object.isFrozen(result.activeAttempts[0])).toBe(true);
  });

  it('rejects missing, extra, or malformed response fields without fallback', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalQueuePayload;

    const missing = payload();
    delete missing.active_attempts;
    expect(() => validate(missing)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID',
    );

    const extra = { ...payload(), monthlyRevenue: 999999 };
    expect(() => validate(extra)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID',
    );

    const malformed = { ...payload(), office_receipt: {} };
    expect(() => validate(malformed)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_RESPONSE_INVALID',
    );
  });

  it('rejects cross-tenant queue rows rather than presenting leaked work', () => {
    const validate =
      __legalOperationsServiceInternals.assertCanonicalQueuePayload;
    const crossTenant = payload();
    crossTenant.active_attempts = [
      {
        tenant_id: 'tenant-foreign',
        attempt_id: 'attempt-foreign',
        state: 'ALLOCATED',
      },
    ];

    expect(() => validate(crossTenant)).toThrow(
      'LEGAL_OPERATIONS_QUEUE_TENANT_MISMATCH',
    );
  });

  it('does not manufacture unsupported dashboard truth', () => {
    const result = __legalOperationsServiceInternals.assertCanonicalQueuePayload(
      payload(),
    );
    expect(Object.keys(result).sort()).toEqual([
      'activeAttempts',
      'deputyAssignment',
      'officeReceipt',
      'tenantId',
      'visibility',
    ]);
    const serialized = JSON.stringify(result).toLowerCase();
    for (const forbidden of [
      'urgent',
      'distance',
      'billing',
      'invoice',
      'payment',
      'settlement',
      'revenue',
      'client_name',
      'ai_score',
    ]) {
      expect(serialized).not.toContain(forbidden);
    }
    expect(LEGAL_OPERATIONS_CLIENT_VERSION).toBe(
      'v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT',
    );
  });
});

/**
 * ARTIFACT: legalOperationsService.test.js
 * VERSION: v1.0.1-L8-6A-SHERIFF-QUEUE-CLIENT-CERT
 * AUTHORITY BOUNDARY: client adapter contract certificate only
 * TENANT POSTURE: cross-tenant rows reject before presentation
 * FAIL-CLOSED POSTURE: malformed/extra/missing response shape rejects without mock fallback
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
