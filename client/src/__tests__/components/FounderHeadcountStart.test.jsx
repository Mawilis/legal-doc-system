/**
 * TITLE: WILSY OS First HR Leadership Headcount Browser Contract
 * VERSION: v1.0.0-FIRST-LEADERSHIP-REPLAY-CERT
 * AUTHORITY: Synthetic Axios transport; no production EOS or staff records.
 * EPITOME: Verify exact tenant, safe draft creation, readback distinctions,
 *          denied source entry and adverse server provenance.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/FounderHeadcountStart.test.jsx
 * COLLABORATION / OWNERSHIP: FounderHeadcountStart and Python EOS Headcount router.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
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
import FounderHeadcountStart from '../../components/hr/FounderHeadcountStart';
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

/* ARTIFACT: client/src/__tests__/components/FounderHeadcountStart.test.jsx
 * VERSION: v1.0.0-FIRST-LEADERSHIP-REPLAY-CERT
 * AUTHORITY BOUNDARY: Synthetic browser UI/transport tests only.
 * TENANT POSTURE: Exact tenant scoped request and response.
 * FAIL-CLOSED POSTURE: Unverified, denied and foreign source results never succeed.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
