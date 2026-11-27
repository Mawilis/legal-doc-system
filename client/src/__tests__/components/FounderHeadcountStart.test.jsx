/**
 * TITLE: WILSY OS First HR Leadership Headcount Browser Contract
 * VERSION: v1.2.0-INDEPENDENT-REVIEW-DECISION-CERT
 * AUTHORITY: Synthetic Axios transport; no production EOS or staff records.
 * EPITOME: Verify exact tenant, safe draft creation, readback distinctions,
 *          denied source entry and adverse server provenance.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/FounderHeadcountStart.test.jsx
 * COLLABORATION / OWNERSHIP: FounderHeadcountStart and Python EOS Headcount router.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.2.0-INDEPENDENT-REVIEW-DECISION-CERT verifies authorized and rejected independent-review commands with source-only maker/checker enforcement and exact tenant boundaries.
 * CHANGELOG: v1.1.0-FIRST-LEADERSHIP-SUBMIT-CERT certifies exact-tenant revision-safe draft submission, independent review messaging and denial.
 * CHANGELOG: v1.0.0-FIRST-LEADERSHIP-REPLAY-CERT covers governed draft creation
 *            without any inferred approval, admission or cross-tenant scope.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic and credential-free.
 * TENANT BOUNDARY: Exact approved tenant header and response identity.
 * AUTHORITY BOUNDARY: DRAFT request only; no employee, offer or IAM authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import FounderHeadcountStart, { HeadcountDraftSubmit, HeadcountIndependentDecision } from '../../components/hr/FounderHeadcountStart';
import api from '../../services/api';

vi.mock('../../services/api', () => ({
  default: { post: vi.fn() },
}));

const TENANT = 'WILSYTENANT-4CD2FZ4O';
const SOURCE = {
  tenant_id: TENANT,
  requisition_id: 'REQ-0123456789ABCDEF01234567',
  status: 'DRAFT',
};

const fillForm = () => {
  fireEvent.click(screen.getByRole('button', { name: 'Request first HR position' }));
  fireEvent.change(screen.getByRole('textbox', { name: 'Work location' }), {
    target: { value: 'Johannesburg' },
  });
  fireEvent.change(screen.getByRole('textbox', { name: 'Business justification' }), {
    target: { value: 'Establish the first independent HR leadership position' },
  });
};
beforeEach(() => vi.clearAllMocks());

describe('First HR leadership headcount EOS command', () => {
  it('denies request entry when the current source was not verified', () => {
    render(<FounderHeadcountStart tenantId={TENANT} admitted={false}/>);
    expect(screen.getByRole('button', { name: 'Request first HR position' })).toBeDisabled();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('creates a single DRAFT under exact current tenant, then refreshes source', async () => {
    api.post.mockResolvedValueOnce({ data: SOURCE });
    const refresh = vi.fn().mockResolvedValue(undefined);
    render(<FounderHeadcountStart tenantId={TENANT} admitted onCreated={refresh}/>);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: 'Submit draft to EOS' }));
    await waitFor(() => expect(refresh).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledTimes(1);
    const [path, body, config] = api.post.mock.calls[0];
    expect(path).toBe('/hr/headcount-requisitions');
    expect(config.headers['X-Tenant-ID']).toBe(TENANT);
    expect(config.headers['Idempotency-Key']).toEqual(expect.any(String));
    expect(body).toMatchObject({
      position_title: 'HR Director', department_id: 'HR',
      headcount: 1, work_location: 'Johannesburg',
    });
    expect(body).not.toHaveProperty('approved');
    expect(body).not.toHaveProperty('employee_id');
    expect(screen.getByRole('status')).toHaveTextContent('Approval has not been granted');
  });

  it('rejects foreign tenant or false approval response without success', async () => {
    api.post.mockResolvedValueOnce({ data: { ...SOURCE, tenant_id: 'foreign' } });
    const refresh = vi.fn();
    render(<FounderHeadcountStart tenantId={TENANT} admitted onCreated={refresh}/>);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: 'Submit draft to EOS' }));
    expect(await screen.findByRole('status')).toHaveTextContent('did not verify');
    expect(refresh).not.toHaveBeenCalled();
  });

  it('distinguishes accepted draft from unavailable subsequent list readback', async () => {
    api.post.mockResolvedValueOnce({ data: SOURCE });
    const refresh = vi.fn().mockRejectedValue(new Error('source timeout'));
    render(<FounderHeadcountStart tenantId={TENANT} admitted onCreated={refresh}/>);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: 'Submit draft to EOS' }));
    expect(await screen.findByText(/accepted the draft, but fresh list readback is unavailable/)).toBeVisible();
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('does not claim approval if EOS rejected the command', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 403, data: { detail: 'IAM_DENIED' } } });
    render(<FounderHeadcountStart tenantId={TENANT} admitted />);
    fillForm();
    fireEvent.click(screen.getByRole('button', { name: 'Submit draft to EOS' }));
    expect(await screen.findByText(/IAM_DENIED/)).toBeVisible();
    expect(screen.queryByText(/Draft requisition accepted/)).not.toBeInTheDocument();
  });
});

describe('First HR headcount independent-review submission', () => {
  const requisition = {
    id: SOURCE.requisition_id,
    title: 'HR Director',
    status: 'DRAFT',
    revision: 1,
  };

  it('sends exact revision without making an independent decision', async () => {
    api.post.mockResolvedValueOnce({ data: { ...SOURCE, status: 'SUBMITTED' } });
    const refreshed = vi.fn().mockResolvedValue(undefined);
    render(<HeadcountDraftSubmit tenantId={TENANT} admitted requisition={requisition} onSubmitted={refreshed} />);
    fireEvent.click(screen.getByRole('button', { name: 'Submit for review' }));
    await waitFor(() => expect(refreshed).toHaveBeenCalledTimes(1));
    const [path, body, config] = api.post.mock.calls[0];
    expect(path).toBe('/hr/headcount-requisitions/' + SOURCE.requisition_id + '/submit');
    expect(body).toEqual({ expected_revision: 1 });
    expect(config.headers['X-Tenant-ID']).toBe(TENANT);
    expect(config.headers['Idempotency-Key']).toEqual(expect.any(String));
    expect(screen.getByRole('status')).toHaveTextContent('independent decision remains outstanding');
  });

  it('does not submit when EOS read authority is unverified', () => {
    render(<HeadcountDraftSubmit tenantId={TENANT} admitted={false} requisition={requisition} />);
    expect(screen.getByRole('button', { name: 'Submit for review' })).toBeDisabled();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('does not claim acceptance for a foreign or decided response', async () => {
    api.post.mockResolvedValueOnce({ data: { ...SOURCE, tenant_id: 'foreign', status: 'APPROVED' } });
    render(<HeadcountDraftSubmit tenantId={TENANT} admitted requisition={requisition} />);
    fireEvent.click(screen.getByRole('button', { name: 'Submit for review' }));
    expect(await screen.findByText(/Submission unverified/)).toBeVisible();
  });

  it('rejects invalid revisions without contacting EOS', () => {
    render(<HeadcountDraftSubmit tenantId={TENANT} admitted requisition={{ ...requisition, revision: 0 }} />);
    fireEvent.click(screen.getByRole('button', { name: 'Submit for review' }));
    expect(api.post).not.toHaveBeenCalled();
  });
});

describe('First HR independent headcount decision', () => {
  const record = { id: SOURCE.requisition_id, status: 'SUBMITTED', revision: 2 };

  it('records a separately authorized decision only after EOS verifies source truth', async () => {
    api.post.mockResolvedValueOnce({ data: { ...SOURCE, status: 'APPROVED' } });
    const refreshed = vi.fn().mockResolvedValue();
    render(<HeadcountIndependentDecision tenantId={TENANT} admitted requisition={record} onDecided={refreshed}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Independent decision' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Independent decision reason' }), {
      target: { value: 'Independently verified opening approval' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Record decision through EOS' }));
    await waitFor(() => expect(refreshed).toHaveBeenCalledOnce());
    const [path, payload, config] = api.post.mock.calls[0];
    expect(path).toBe('/hr/headcount-requisitions/' + SOURCE.requisition_id + '/decision');
    expect(payload).toEqual({
      expected_revision: 2, decision: 'APPROVE',
      reason: 'Independently verified opening approval',
    });
    expect(config.headers['X-Tenant-ID']).toBe(TENANT);
    expect(config.headers['Idempotency-Key']).toEqual(expect.any(String));
  });

  it('reflects maker-checker denial without pretending approval', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 409, data: { detail: 'HEADCOUNT_SELF_APPROVAL_DENIED' } } });
    render(<HeadcountIndependentDecision tenantId={TENANT} admitted requisition={record}/>);
    fireEvent.click(screen.getByRole('button', { name: 'Independent decision' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Independent decision reason' }), {
      target: { value: 'Founder initial appointment' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Record decision through EOS' }));
    expect(await screen.findByText(/HEADCOUNT_SELF_APPROVAL_DENIED/)).toBeVisible();
    expect(screen.queryByText(/recorded the independent decision/)).not.toBeInTheDocument();
  });

  it('does not expose a submit action for unverified authority', () => {
    render(<HeadcountIndependentDecision tenantId={TENANT} admitted={false} requisition={record}/>);
    expect(screen.getByRole('button', { name: 'Independent decision' })).toBeDisabled();
    expect(api.post).not.toHaveBeenCalled();
  });
});

/* ARTIFACT: client/src/__tests__/components/FounderHeadcountStart.test.jsx
 * VERSION: v1.2.0-INDEPENDENT-REVIEW-DECISION-CERT
 * AUTHORITY BOUNDARY: Synthetic browser UI/transport tests only.
 * TENANT POSTURE: Exact tenant scoped request and response.
 * FAIL-CLOSED POSTURE: Unverified, denied and foreign source results never succeed.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
