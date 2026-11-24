/**
 * TITLE: WILSY OS HR Client Transport Contract Tests
 * VERSION: v1.5.0-CANDIDATE-EVIDENCE-CUSTODY-TRANSPORT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies tenant-scoped HR transport success, verified-empty results,
 *          and honest propagation of authorization and source failures.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/hrService.test.js
 * COLLABORATION / OWNERSHIP: Vitest contract tests for hrService.js; no business records are created.
 * CERTIFICATION / UPDATE DATE: 2026-11-12
 * CHANGELOG:
 *   v1.5.0-CANDIDATE-EVIDENCE-CUSTODY-TRANSPORT — Verifies raw binary upload and exact-version evidence readback use the existing authenticated EOS routes, exact tenant, digest and byte-length contract.
 *   v1.4.0-EOS-HIRING-COMMAND-TRANSPORT — Verifies candidate and offer commands use EOS paths, exact tenant/idempotency/revision headers, and never claim transport acknowledgement as durable success.
 *   v1.3.0-CANONICAL-HIRING-PAGE-READS — Verifies candidate and offer reads use canonical EOS paths, exact tenant headers, and strict page envelopes.
 *   v1.2.0-STRICT-HR-PAGE-ENVELOPES — Rejects incomplete paginated object responses rather than inferring totals or treating missing metadata as empty truth.
 *   v1.1.0-FAILURE-TRANSPARENT-HR-READS — Covers genuine empty pages, missing
 *     scope, denied/unavailable/malformed reads, circuit-open behavior and
 *     source-success outcomes independent of optional telemetry.
 * COMPLIANCE: Test artifact; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic tenant and request values only; no persisted identities or HR data.
 * TENANT BOUNDARY: Every accepted transport call supplies one explicit test tenant.
 * AUTHORITY BOUNDARY: Tests client transport only; Python EOS remains authorization and business truth owner.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement behavior is tested or granted.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api, broadcastTelemetry } = vi.hoisted(() => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  broadcastTelemetry: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('./api', () => ({ default: api }));
vi.mock('../utils/telemetryHelper', () => ({ broadcastTelemetry }));
vi.mock('../utils/logger', () => ({ default: { error: vi.fn() } }));

import {
  approveTimeOff,
  createEmployee,
  createHiringCandidate,
  transitionHiringCandidate,
  uploadHiringCandidateEvidence,
  readHiringCandidateEvidence,
  createHiringOffer,
  submitHiringOffer,
  decideHiringOffer,
  sendHiringOffer,
  denyTimeOff,
  getEmployees,
  getHiringCandidates,
  getHiringOffers,
  getHrCircuitState,
  resetHrCircuit,
} from './hrService.js';

const tenantId = 'TENANT-PEOPLE-1';
const verifiedEmptyPage = {
  items: [],
  total: 0,
  limit: 10,
  offset: 0,
  hasMore: false,
};

const sourceError = (status, code = 'ERR_SOURCE') => {
  const error = new Error(`synthetic ${status || 'network'} failure`);
  error.code = code;
  if (status) error.response = { status };
  return error;
};

describe('HR tenant-scoped client transport', () => {
  beforeEach(() => {
    api.get.mockReset().mockResolvedValue({ data: verifiedEmptyPage });
    api.post.mockReset().mockResolvedValue({ data: { id: 'synthetic-employee-1' } });
    api.put.mockReset().mockResolvedValue({ data: { id: 'leave-1', status: 'APPROVED' } });
    api.delete.mockReset().mockResolvedValue({ data: undefined });
    broadcastTelemetry.mockReset().mockResolvedValue(undefined);
    resetHrCircuit();
  });

  it('preserves an explicitly verified empty page as a successful empty result', async () => {
    api.get.mockResolvedValueOnce({ data: verifiedEmptyPage });

    await expect(getEmployees(tenantId)).resolves.toEqual({
      ...verifiedEmptyPage,
      skipped: false,
    });
    expect(api.get).toHaveBeenCalledWith('/hr/employees', {
      params: { tenantId },
      headers: { 'X-Tenant-ID': tenantId },
    });
  });

  it('reads candidate and offer pages through canonical tenant-scoped EOS routes', async () => {
    const candidatePage = {
      items: [{ candidate_id: 'CAN-SYNTHETIC-1', tenant_id: tenantId }],
      total: 1,
      limit: 5,
      offset: 10,
      hasMore: false,
    };
    api.get.mockResolvedValueOnce({ data: candidatePage });
    api.get.mockResolvedValueOnce({ data: verifiedEmptyPage });

    await expect(getHiringCandidates(tenantId, { limit: 5, offset: 10 })).resolves.toEqual({
      ...candidatePage,
      skipped: false,
    });
    expect(api.get).toHaveBeenNthCalledWith(1, '/hr/hiring/candidates', {
      params: { tenantId, limit: 5, offset: 10 },
      headers: { 'X-Tenant-ID': tenantId },
    });

    await expect(getHiringOffers(tenantId, { limit: 10, offset: 0 })).resolves.toEqual({
      ...verifiedEmptyPage,
      skipped: false,
    });
    expect(api.get).toHaveBeenNthCalledWith(2, '/hr/hiring/offers', {
      params: { tenantId, limit: 10, offset: 0 },
      headers: { 'X-Tenant-ID': tenantId },
    });
  });

  it('transports canonical candidate and offer commands with exact tenant, idempotency, and revision headers', async () => {
    const key = 'stable-command-key-1';
    const candidate = {
      candidate_id: 'CAN-1', requisition_id: 'REQ-1',
      candidate_profile_reference: 'candidate-profile://opaque/1', source: 'FOUNDER_TEST',
    };
    const transition = {
      expected_revision: 1, target_stage: 'SCREENING', reason: 'Evidence reviewed',
      evidence_reference: 'EVIDENCE-1', evidence_fingerprint: 'a'.repeat(128),
    };
    const offer = {
      offer_id: 'OFFER-1', candidate_id: 'CAN-1', requisition_id: 'REQ-1',
      position_title: 'Platform Engineer', employment_type: 'FULL_TIME',
      work_location: 'Remote', currency: 'ZAR', gross_compensation_minor: 100000,
      pay_frequency: 'MONTHLY', start_date: '2026-12-01', expires_at: '2026-11-30T23:59:59Z',
    };

    await createHiringCandidate(candidate, tenantId, key);
    await transitionHiringCandidate('CAN-1', transition, tenantId, key);
    await createHiringOffer(offer, tenantId, key);
    await submitHiringOffer('OFFER-1', 2, tenantId, key);
    await decideHiringOffer('OFFER-1', { expected_revision: 3, approved: true, reason: 'Independent approval' }, tenantId, key);
    await sendHiringOffer('OFFER-1', 4, tenantId, key);

    expect(api.post).toHaveBeenNthCalledWith(1, '/hr/hiring/candidates', candidate, {
      headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key },
    });
    expect(api.post).toHaveBeenNthCalledWith(2, '/hr/hiring/candidates/CAN-1/transition', transition, {
      headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key },
    });
    expect(api.post).toHaveBeenNthCalledWith(3, '/hr/hiring/offers', offer, {
      headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key },
    });
    expect(api.post).toHaveBeenNthCalledWith(4, '/hr/hiring/offers/OFFER-1/submit', {}, {
      headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key, 'Expected-Revision': '2' },
    });
    expect(api.post).toHaveBeenNthCalledWith(5, '/hr/hiring/offers/OFFER-1/decision', {
      expected_revision: 3, approved: true, reason: 'Independent approval',
    }, { headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key } });
    expect(api.post).toHaveBeenNthCalledWith(6, '/hr/hiring/offers/OFFER-1/send', {}, {
      headers: { 'X-Tenant-ID': tenantId, 'Idempotency-Key': key, 'Expected-Revision': '4' },
    });
    expect(broadcastTelemetry).not.toHaveBeenCalled();
  });

  it('uploads raw candidate evidence and requires exact-version digest and byte-length readback', async () => {
    const candidateId = 'CAN-EVIDENCE-1';
    const evidenceId = 'EVD-1';
    const evidenceVersionId = 'VER-1';
    const file = new Blob(['verified profile bytes'], { type: 'application/pdf' });
    const digest = 'e'.repeat(128);
    const receipt = {
      status: 'CUSTODY_REGISTERED', custody_registered: true,
      candidate_id: candidateId, evidence_id: evidenceId,
      evidence_version_id: evidenceVersionId, byte_length: file.size,
      content_digest_sha3_512: digest,
    };
    api.put.mockResolvedValueOnce({ data: receipt });
    await expect(uploadHiringCandidateEvidence(
      candidateId, evidenceId, evidenceVersionId, file,
      { mediaType: 'application/pdf', originalFilename: 'profile.pdf' }, tenantId,
    )).resolves.toEqual(receipt);
    expect(api.put).toHaveBeenCalledWith(
      `/hr/hiring/candidates/${candidateId}/evidence/${evidenceId}/${evidenceVersionId}`,
      file,
      { headers: {
        'X-Tenant-ID': tenantId,
        'X-Evidence-Media-Type': 'application/pdf',
        'X-Evidence-Filename': 'profile.pdf',
        'X-Evidence-Kind': 'CANDIDATE_PROFILE',
      } },
    );

    api.get.mockResolvedValueOnce({
      data: file,
      headers: {
        'x-content-digest-sha3-512': digest,
        'content-length': String(file.size),
      },
    });
    await expect(readHiringCandidateEvidence(
      candidateId, evidenceId, evidenceVersionId, tenantId,
    )).resolves.toEqual({
      blob: file, contentDigestSha3_512: digest, contentLength: file.size,
    });
    expect(api.get).toHaveBeenCalledWith(
      `/hr/hiring/candidates/${candidateId}/evidence/${evidenceId}/${evidenceVersionId}`,
      { responseType: 'blob', headers: { 'X-Tenant-ID': tenantId } },
    );
  });

  it('rejects malformed custody receipts, invalid filenames, and mismatched evidence readback', async () => {
    const file = new Blob(['evidence'], { type: 'application/pdf' });
    api.put.mockResolvedValueOnce({ data: {
      status: 'CUSTODY_REGISTERED', custody_registered: true,
      candidate_id: 'CAN-EVIDENCE-1', evidence_id: 'EVD-1',
      evidence_version_id: 'VER-1', byte_length: file.size + 1,
      content_digest_sha3_512: 'f'.repeat(128),
    } });
    await expect(uploadHiringCandidateEvidence(
      'CAN-EVIDENCE-1', 'EVD-1', 'VER-1', file,
      { mediaType: 'application/pdf', originalFilename: 'profile.pdf' }, tenantId,
    )).rejects.toMatchObject({ code: 'HR_EVIDENCE_CUSTODY_RECEIPT_INVALID', status: 502 });
    await expect(uploadHiringCandidateEvidence(
      'CAN-EVIDENCE-1', 'EVD-1', 'VER-1', file,
      { mediaType: 'application/pdf', originalFilename: 'profile-☃.pdf' }, tenantId,
    )).rejects.toMatchObject({ code: 'HR_EVIDENCE_METADATA_INVALID', status: 400 });
    expect(api.put).toHaveBeenCalledTimes(1);

    api.get.mockResolvedValueOnce({
      data: file,
      headers: {
        'x-content-digest-sha3-512': 'f'.repeat(128),
        'content-length': String(file.size + 1),
      },
    });
    await expect(readHiringCandidateEvidence(
      'CAN-EVIDENCE-1', 'EVD-1', 'VER-1', tenantId,
    )).rejects.toMatchObject({ code: 'HR_EVIDENCE_READBACK_INVALID', status: 502 });
  });

  it('rejects canonical hiring commands without a stable idempotency key before transport', async () => {
    await expect(createHiringCandidate({ candidate_id: 'CAN-1' }, tenantId, ' ')).rejects.toMatchObject({
      code: 'HR_HIRING_IDEMPOTENCY_KEY_REQUIRED', status: 400,
    });
    expect(() => submitHiringOffer('OFFER-1', 0, tenantId, 'stable-key')).toThrow(
      expect.objectContaining({ code: 'HR_HIRING_EXPECTED_REVISION_INVALID', status: 400 }),
    );
    expect(api.post).not.toHaveBeenCalled();
  });

  it('rejects reads without exact tenant scope before making a request', async () => {
    await expect(getEmployees(null)).rejects.toMatchObject({
      code: 'HR_TENANT_SCOPE_REQUIRED',
      status: 403,
    });
    expect(api.get).not.toHaveBeenCalled();
  });

  it.each([401, 403])('propagates HTTP %s and leaves the transport circuit usable', async (status) => {
    const denied = sourceError(status);
    api.get.mockRejectedValueOnce(denied).mockResolvedValueOnce({ data: verifiedEmptyPage });

    await expect(getEmployees(tenantId)).rejects.toBe(denied);
    await expect(getEmployees(tenantId)).resolves.toMatchObject({ items: [], skipped: false });
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(getHrCircuitState().state).not.toBe('OPEN');
  });

  it.each([502, 503])('propagates HTTP %s and then reports an open circuit distinctly', async (status) => {
    const unavailable = sourceError(status);
    api.get.mockRejectedValue(unavailable);

    await expect(getEmployees(tenantId)).rejects.toBe(unavailable);
    await expect(getEmployees(tenantId)).rejects.toMatchObject({
      code: 'HR_API_CIRCUIT_OPEN',
      status: 503,
    });
    expect(api.get).toHaveBeenCalled();
  });

  it('propagates network failures instead of returning a successful empty page', async () => {
    const networkFailure = sourceError(undefined, 'ERR_NETWORK');
    api.get.mockRejectedValue(networkFailure);

    await expect(getEmployees(tenantId)).rejects.toBe(networkFailure);
    expect(getHrCircuitState().state).toBe('OPEN');
  });

  it('rejects malformed source pages while preserving verified zero rows', async () => {
    api.get.mockResolvedValueOnce({ data: { items: 'not-an-array', total: 0 } });

    await expect(getEmployees(tenantId)).rejects.toMatchObject({
      code: 'HR_SOURCE_RESPONSE_INVALID',
      status: 502,
    });
  });

  it('rejects an incomplete empty-page envelope instead of deriving total zero', async () => {
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    await expect(getEmployees(tenantId)).rejects.toMatchObject({
      code: 'HR_SOURCE_RESPONSE_INVALID',
      status: 502,
    });
  });

  it('does not let telemetry failure turn a successful source command into failure', async () => {
    const response = { id: 'synthetic-employee-1' };
    api.post.mockResolvedValueOnce({ data: response });
    broadcastTelemetry.mockRejectedValueOnce(new Error('synthetic telemetry outage'));

    await expect(createEmployee({ displayName: 'Synthetic Test' }, tenantId)).resolves.toEqual(response);
    expect(api.post).toHaveBeenCalledWith('/hr/employees', { displayName: 'Synthetic Test' }, {
      headers: { 'X-Tenant-ID': tenantId },
    });
  });

  it('keeps time-off decisions tenant-scoped through the People-domain client routes', async () => {
    await approveTimeOff('leave-1', tenantId);
    expect(api.put).toHaveBeenCalledWith('/hr/timeoff/leave-1/approve', {}, {
      headers: { 'X-Tenant-ID': tenantId },
    });
    expect(broadcastTelemetry).toHaveBeenCalled();

    await denyTimeOff('leave-2', tenantId);
    expect(api.put).toHaveBeenLastCalledWith('/hr/timeoff/leave-2/deny', {}, {
      headers: { 'X-Tenant-ID': tenantId },
    });
  });
});

/**
 * ARTIFACT: client/src/services/hrService.test.js
 * VERSION: v1.5.0-CANDIDATE-EVIDENCE-CUSTODY-TRANSPORT
 * AUTHORITY BOUNDARY: Client transport contract tests only; Python EOS owns authorization and source truth.
 * TENANT POSTURE: Synthetic exact-tenant values only; no live tenant is read or modified.
 * FAIL-CLOSED POSTURE: Denials and unavailable/malformed sources must reject; only verified empty pages resolve empty.
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
