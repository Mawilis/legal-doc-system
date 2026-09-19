/**
 * WILSY OS — LEGAL ACCEPTANCE GATE CERTIFICATE
 * VERSION: v1.0.1-R1D-B0F-B4-R9A-P3-EMPTY-STATE
 * AUTHORITY: Wilsy OS Core Governance; client projection evidence only
 * EPITOME: Proves unresolved legal status blocks workspace entry, while a
 *           complete server status permits one bounded completion transition.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/LegalAcceptanceGate.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises LegalAcceptanceGate against the
 *                            server-owned legal-acceptance HTTP contract.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.1 adds direct live-shape coverage for USER_TERMS_REQUIRED
 *            with no renderable documents and preserves all existing flows.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * AUTHORITY BOUNDARY: Presentation evidence only; Python EOS owns legal truth.
 */
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import LegalAcceptanceGate from '../../../src/components/auth/LegalAcceptanceGate.jsx';
import api from '../../../src/services/api';

vi.mock('../../../src/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const requiredPlan = {
  status: 'USER_TERMS_REQUIRED',
  tenantId: 'tenant-1',
  documents: [{
    agreementType: 'USER_TERMS', documentId: 'terms-v1', version: '1.0.0',
    sha3_512: 'a'.repeat(128), title: 'User Terms', jurisdiction: 'ZA',
    locale: 'en-ZA', effectiveFrom: '2026-09-17T00:00:00Z', summary: 'Terms',
    content: 'Full terms', accepted: false,
  }],
};

describe('LegalAcceptanceGate pre-workspace barrier', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.post.mockResolvedValue({ data: { status: 'RECORDED' } });
  });

  it('renders the required gate and never renders signature authority', async () => {
    api.get.mockResolvedValue({ data: requiredPlan });
    render(<LegalAcceptanceGate />);
    expect(await screen.findByRole('heading', { name: /before you enter/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /acknowledge and continue/i })).toBeInTheDocument();
    expect(screen.queryByText(/signature pad|execute enterprise seal/i)).not.toBeInTheDocument();
  });

  it('fails closed when legal status is unavailable', async () => {
    api.get.mockRejectedValue({ response: { data: { detail: 'LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE' } } });
    render(<LegalAcceptanceGate />);
    expect(await screen.findByText('LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE')).toBeInTheDocument();
    expect(screen.queryByText(/before you enter/i)).not.toBeInTheDocument();
  });

  it('renders an explicit server-driven empty state without fake legal actions', async () => {
    api.get.mockResolvedValue({ data: {
      status: 'DOCUMENT_APPROVAL_REQUIRED', tenantId: 'tenant-1', documents: [],
      missingAgreementTypes: ['INSTITUTIONAL_CHARTER'],
    } });
    render(<LegalAcceptanceGate />);
    expect(await screen.findByRole('heading', { name: /legal documents are being prepared/i })).toBeInTheDocument();
    expect(screen.getByText(/institutional documents are awaiting approval/i)).toBeInTheDocument();
    expect(screen.getByText(/workspace access remains protected/i)).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
    expect(screen.queryByText(/before you enter/i)).not.toBeInTheDocument();
  });

  it('renders the live USER_TERMS_REQUIRED empty state fail-closed', async () => {
    const onComplete = vi.fn();
    api.get.mockResolvedValue({ data: {
      status: 'USER_TERMS_REQUIRED', tenantId: 'tenant-live', documents: [],
      missingAgreementTypes: [
        'INSTITUTIONAL_CHARTER', 'USER_TERMS', 'ACCEPTABLE_USE',
        'PRIVACY_NOTICE', 'AI_ASSISTANCE_NOTICE', 'ADMIN_RESPONSIBILITY_NOTICE',
      ],
    } });
    render(<LegalAcceptanceGate onComplete={onComplete}><div data-testid="protected-workspace" /></LegalAcceptanceGate>);

    expect(await screen.findByRole('heading', { name: /required institutional documents are not yet approved and available/i })).toBeInTheDocument();
    expect(screen.getByText(/workspace access will remain unavailable until the required documents are published and accepted/i)).toBeInTheDocument();
    expect(screen.getByText(/seeing this screen does not record an acceptance/i)).toBeInTheDocument();
    for (const agreementType of ['INSTITUTIONAL_CHARTER', 'USER_TERMS', 'ACCEPTABLE_USE', 'PRIVACY_NOTICE', 'AI_ASSISTANCE_NOTICE', 'ADMIN_RESPONSIBILITY_NOTICE']) {
      expect(screen.getByText(agreementType)).toBeInTheDocument();
    }
    expect(screen.queryByTestId('protected-workspace')).not.toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
    expect(screen.queryByText(/acknowledge and continue|continue|skip|bypass/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/before you enter/i)).not.toBeInTheDocument();
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.get.mock.calls.some(([path]) => String(path).includes('/documents/'))).toBe(false);
    expect(api.post).not.toHaveBeenCalled();
    expect(onComplete).not.toHaveBeenCalled();
  });


  it('permits one completion transition only after server COMPLETE', async () => {
    const onComplete = vi.fn();
    api.get.mockResolvedValue({ data: { status: 'COMPLETE', tenantId: 'tenant-1', documents: [] } });
    render(<LegalAcceptanceGate onComplete={onComplete} />);
    await waitFor(() => expect(onComplete).toHaveBeenCalledTimes(1));
  });

  it('submits server-issued document identity with an idempotency key', async () => {
    api.get.mockResolvedValue({ data: requiredPlan });
    render(<LegalAcceptanceGate />);
    fireEvent.click(await screen.findByRole('button', { name: /acknowledge and continue/i }));
    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post.mock.calls[0][0]).toBe('/legal-acceptance/accept');
    expect(api.post.mock.calls[0][1]).toMatchObject({
      document_id: 'terms-v1', document_version: '1.0.0',
      document_sha3_512: 'a'.repeat(128), acceptance_method: 'ACCEPTANCE',
    });
    expect(api.post.mock.calls[0][2].headers['Idempotency-Key']).toEqual(expect.any(String));
  });
});

// ARTIFACT: LegalAcceptanceGate.test.jsx
// VERSION: v1.0.1-R1D-B0F-B4-R9A-P3-EMPTY-STATE
// AUTHORITY BOUNDARY: deterministic client projection certificate only
// TENANT POSTURE: server-issued plan is displayed; no local legal truth
// FAIL-CLOSED POSTURE: unavailable or incomplete status never opens workspace
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
