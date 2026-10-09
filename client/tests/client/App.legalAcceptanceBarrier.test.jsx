/**
 * TITLE: WILSY OS Pre-Workspace Legal Acceptance Barrier Certificate
 * VERSION: v1.1.0-SAME-SESSION-LEGAL-RELEASE-CERT
 * AUTHORITY: Wilsy OS Core Governance; client projection evidence only
 * EPITOME: Proves that legal status resolves before protected workspace
 *           composition and that required/unavailable states fail closed.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.legalAcceptanceBarrier.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises App's LegalAcceptanceBoundary and its
 *                            server-owned status transport.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: v1.1.0-SAME-SESSION-LEGAL-RELEASE-CERT certifies that the final
 *            server-confirmed acceptance transitions the boundary from REQUIRED
 *            to COMPLETE and mounts protected runtime without browser reload.
 *            v1.0.0 certified loading, required, unavailable, and complete
 *            composition ordering without protected endpoint prefetch.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic legal plans only; no credential,
 *                             evidence, token, or tenant authority is persisted.
 * AUTHORITY BOUNDARY: Client presentation only; Python EOS owns legal truth.
 * TENANT BOUNDARY: Only the server-issued plan tenant is represented.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */
import React from 'react';
import { readFileSync } from 'node:fs';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LegalAcceptanceBoundary } from '../../src/App.jsx';
import api from '../../src/services/api';

vi.mock('../../src/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const required = { status: 'DOCUMENT_APPROVAL_REQUIRED', tenantId: 'tenant-1', documents: [] };

const requiredAcceptance = {
  status: 'USER_TERMS_REQUIRED',
  tenantId: 'tenant-1',
  documents: [
    {
      agreementType: 'USER_TERMS',
      documentId: 'terms-v1',
      version: '1.1.0-APPROVED',
      sha3_512: 'b'.repeat(128),
      title: 'WILSY OS User Terms',
      locale: 'en-ZA',
      effectiveFrom: '2026-09-20T00:00:00Z',
      content: 'Server-issued legal terms.',
      accepted: false,
    },
  ],
};

const completeAcceptance = {
  ...requiredAcceptance,
  status: 'COMPLETE',
  documents: requiredAcceptance.documents.map((document) => ({
    ...document,
    accepted: true,
  })),
};

describe('LegalAcceptanceBoundary', () => {
  beforeEach(() => vi.clearAllMocks());

  it('keeps protected composition unmounted while status is unresolved', async () => {
    let resolve;
    api.get.mockReturnValue(new Promise((r) => { resolve = r; }));
    render(<MemoryRouter><LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} /></MemoryRouter>);
    expect(screen.getByTestId('workspace-bootstrap')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
    resolve({ data: required });
    await waitFor(() => expect(screen.getByText(/legal documents are being prepared/i)).toBeInTheDocument());
  });

  it('renders only the legal gate for an incomplete status', async () => {
    api.get.mockResolvedValue({ data: required });
    render(<MemoryRouter initialEntries={['/']}><LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText(/legal documents are being prepared/i)).toBeInTheDocument());
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
  });

  it('fails closed on unavailable status', async () => {
    api.get.mockRejectedValue({ response: { data: { detail: 'LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE' } } });
    render(<MemoryRouter><LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByText('LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE')).toBeInTheDocument());
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
  });

  it('mounts protected composition exactly after COMPLETE', async () => {
    api.get.mockResolvedValue({ data: { status: 'COMPLETE', tenantId: 'tenant-1', documents: [] } });
    render(<MemoryRouter><LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} /></MemoryRouter>);
    await waitFor(() => expect(screen.getByTestId('protected-runtime')).toBeInTheDocument());
  });

  it('releases protected runtime in the same session after final server-confirmed acceptance', async () => {
    api.get
      .mockResolvedValueOnce({ data: requiredAcceptance })
      .mockResolvedValueOnce({ data: completeAcceptance });
    api.post.mockResolvedValueOnce({ data: { status: 'RECORDED' } });

    render(
      <MemoryRouter initialEntries={['/covenant']}>
        <LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} />
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acceptance/i }));

    await waitFor(() => expect(screen.getByTestId('protected-runtime')).toBeInTheDocument());

    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(screen.queryByTestId('document-focus-mode')).not.toBeInTheDocument();
  });

  it('does not re-prompt on a fresh mount after durable server COMPLETE', async () => {
    api.get.mockResolvedValue({ data: { status: 'COMPLETE', tenantId: 'tenant-1', documents: [] } });

    const first = render(
      <MemoryRouter><LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} /></MemoryRouter>
    );
    await waitFor(() => expect(screen.getByTestId('protected-runtime')).toBeInTheDocument());
    expect(screen.queryByText(/before you enter your workspace/i)).not.toBeInTheDocument();
    first.unmount();

    render(
      <MemoryRouter><LegalAcceptanceBoundary runtime={<div data-testid="protected-runtime" />} /></MemoryRouter>
    );
    await waitFor(() => expect(screen.getByTestId('protected-runtime')).toBeInTheDocument());
    expect(screen.queryByText(/before you enter your workspace/i)).not.toBeInTheDocument();
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(api.get).toHaveBeenNthCalledWith(1, '/legal-acceptance/status');
    expect(api.get).toHaveBeenNthCalledWith(2, '/legal-acceptance/status');
  });


  it('keeps exactly one server-owned legal status read in protected workspace composition', () => {
    const source = readFileSync('src/App.jsx', 'utf8');
    const statusReads = source.match(/api\.get\(['"]\/legal-acceptance\/status['"]\)/g) || [];
    expect(statusReads).toHaveLength(1);
    expect(source).not.toContain('const AcceptanceAwareWorkspace');
  });

});

// ARTIFACT: App.legalAcceptanceBarrier.test.jsx
// VERSION: v1.1.0-SAME-SESSION-LEGAL-RELEASE-CERT
// AUTHORITY BOUNDARY: deterministic pre-workspace barrier certificate only
// TENANT POSTURE: legal status is server-issued; no local legal truth
// FAIL-CLOSED POSTURE: unresolved, required, or unavailable status blocks runtime
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
