/**
 * WILSY OS — LEGAL MATTER DEADLINE CLIENT ADAPTER CERTIFICATE
 * VERSION: v1.0.0-D4A-MATTER-DEADLINE-CLIENT-CERT
 * AUTHORITY: Browser transport-validation evidence only.
 * EPITOME: Certifies exact D3B1 list/detail/create transport without browser-owned authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/legalMatterDeadlineClient.test.js
 * CERTIFICATION / UPDATE DATE: 2026-10-11
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * TENANT BOUNDARY: Tenant scope is never accepted by the adapter.
 * AUTHORITY BOUNDARY: Transport certificate only; Python EOS remains sovereign.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockGet, mockSovereignPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockSovereignPost: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: { get: mockGet, post: vi.fn() },
}));

vi.mock('../../utils/sovereignClient.js', () => ({
  default: { post: mockSovereignPost },
}));

import {
  LEGAL_MATTER_DEADLINE_CLIENT_VERSION,
  createLegalMatterDeadline,
  getLegalMatterDeadline,
  getLegalMatterDeadlines,
} from '../../services/legalMatterDeadlineService.js';

const row = (overrides = {}) => ({
  deadline_id: 'deadline-1',
  case_matter_id: 'matter-1',
  deadline_kind: 'FILING',
  title: 'File answering affidavit',
  due_at: '2026-10-20T10:00:00+00:00',
  source_type: 'COURT_ORDER',
  jurisdiction_reference: 'court:gp-hc',
  created_at: '2026-10-11T10:00:00+00:00',
  supersedes_deadline_id: null,
  status: 'ACTIVE',
  ...overrides,
});

const input = (overrides = {}) => ({
  caseMatterId: 'matter-1',
  deadlineId: 'deadline-1',
  deadlineKind: 'FILING',
  title: 'File answering affidavit',
  dueAt: '2026-10-20T10:00:00+00:00',
  sourceType: 'COURT_ORDER',
  sourceReference: 'court-order:123',
  sourceEvidenceFingerprint: 'a'.repeat(128),
  jurisdictionReference: 'court:gp-hc',
  createdAt: '2026-10-11T10:00:00+00:00',
  supersedesDeadlineId: null,
  ...overrides,
});

describe('legal matter deadline client adapter', () => {
  beforeEach(() => vi.clearAllMocks());

  it('binds the certified D4A production version', () => {
    expect(LEGAL_MATTER_DEADLINE_CLIENT_VERSION)
      .toBe('v1.0.0-D4A-MATTER-DEADLINE-CLIENT');
  });

  it('lists exact matter deadlines and freezes presentation rows', async () => {
    mockGet.mockResolvedValueOnce({ data: { data: [row()] } });
    const result = await getLegalMatterDeadlines('matter-1');
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/matters/matter-1/deadlines',
    );
    expect(result[0]).toEqual({
      deadlineId: 'deadline-1',
      caseMatterId: 'matter-1',
      deadlineKind: 'FILING',
      title: 'File answering affidavit',
      dueAt: '2026-10-20T10:00:00+00:00',
      sourceType: 'COURT_ORDER',
      jurisdictionReference: 'court:gp-hc',
      createdAt: '2026-10-11T10:00:00+00:00',
      supersedesDeadlineId: null,
      status: 'ACTIVE',
    });
    expect(Object.isFrozen(result)).toBe(true);
    expect(Object.isFrozen(result[0])).toBe(true);
  });

  it('reads detail with exact matter and deadline correlation', async () => {
    mockGet.mockResolvedValueOnce({ data: { data: row() } });
    const result = await getLegalMatterDeadline('matter-1', 'deadline-1');
    expect(mockGet).toHaveBeenCalledWith(
      '/legal-operations/matters/matter-1/deadlines/deadline-1',
    );
    expect(result.deadlineId).toBe('deadline-1');
  });

  it('creates only the strict ACTIVE body through sovereignClient', async () => {
    mockSovereignPost.mockResolvedValueOnce({ data: { data: row() } });
    const result = await createLegalMatterDeadline(input());
    expect(mockSovereignPost).toHaveBeenCalledWith(
      '/legal-operations/matters/matter-1/deadlines',
      {
        deadline_id: 'deadline-1',
        deadline_kind: 'FILING',
        title: 'File answering affidavit',
        due_at: '2026-10-20T10:00:00+00:00',
        source_type: 'COURT_ORDER',
        source_reference: 'court-order:123',
        source_evidence_fingerprint: 'a'.repeat(128),
        jurisdiction_reference: 'court:gp-hc',
        created_at: '2026-10-11T10:00:00+00:00',
        supersedes_deadline_id: null,
        status: 'ACTIVE',
      },
    );
    expect(result.status).toBe('ACTIVE');
  });

  it.each([
    { tenantId: 'tenant-a' },
    { principalId: 'principal-a' },
    { status: 'SATISFIED' },
    { overdue: true },
    { aiConfidence: 0.9 },
    { paymentState: 'PAID' },
  ])('rejects extra browser authority before transport: %j', async (extra) => {
    await expect(
      createLegalMatterDeadline({ ...input(), ...extra }),
    ).rejects.toThrow('LEGAL_OPERATIONS_DEADLINE_INPUT_INVALID');
    expect(mockSovereignPost).not.toHaveBeenCalled();
  });

  it('rejects malformed provenance and naive timestamps before transport', async () => {
    await expect(createLegalMatterDeadline(input({
      sourceEvidenceFingerprint: 'bad',
    }))).rejects.toThrow('LEGAL_OPERATIONS_DEADLINE_INPUT_INVALID');
    await expect(createLegalMatterDeadline(input({
      dueAt: '2026-10-20T10:00:00',
    }))).rejects.toThrow('LEGAL_OPERATIONS_DEADLINE_INPUT_INVALID');
    expect(mockSovereignPost).not.toHaveBeenCalled();
  });

  it.each([
    row({ case_matter_id: 'matter-other' }),
    row({ deadline_kind: 'INVENTED' }),
    row({ status: 'OVERDUE' }),
    { ...row(), source_reference: 'secret-should-not-exist' },
  ])('rejects malformed or widened server rows', async (badRow) => {
    mockGet.mockResolvedValueOnce({ data: { data: [badRow] } });
    await expect(getLegalMatterDeadlines('matter-1')).rejects.toThrow(
      'LEGAL_OPERATIONS_DEADLINE_RESPONSE_INVALID',
    );
  });

  it('rejects duplicate identities and detail path mismatch', async () => {
    mockGet.mockResolvedValueOnce({ data: { data: [row(), row()] } });
    await expect(getLegalMatterDeadlines('matter-1')).rejects.toThrow(
      'LEGAL_OPERATIONS_DEADLINE_RESPONSE_INVALID',
    );

    mockGet.mockResolvedValueOnce({
      data: { data: row({ deadline_id: 'deadline-other' }) },
    });
    await expect(
      getLegalMatterDeadline('matter-1', 'deadline-1'),
    ).rejects.toThrow('LEGAL_OPERATIONS_DEADLINE_RESPONSE_INVALID');
  });
});

/**
 * ARTIFACT: legalMatterDeadlineClient.test.js
 * VERSION: v1.0.0-D4A-MATTER-DEADLINE-CLIENT-CERT
 * AUTHORITY BOUNDARY: strict deadline browser transport certificate only
 * TENANT POSTURE: browser cannot supply tenant authority
 * FAIL-CLOSED POSTURE: malformed input/response, scope mismatch and privilege widening reject
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
