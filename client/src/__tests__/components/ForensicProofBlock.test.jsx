/**
 * TITLE: WILSY OS Forensic Proof Reference Client Certificate
 * VERSION: v1.2.1-TEST-ASYNC-CLEANUP
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves the billing proof panel uses authenticated Python EOS for
 *          legacy signed QR issuance, tenant-scoped verification, and a separate
 *          persisted seal-reference check.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ForensicProofBlock.test.jsx
 * COLLABORATION / OWNERSHIP: Covers ForensicProofBlock, API transport and the
 *                            Python EOS billing proof-reference route contract.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.2.1-TEST-ASYNC-CLEANUP awaits issuance effects in malformed
 *            reference coverage and keeps absence queries non-throwing.
 *            v1.2.0-AUTHENTICATED-LEGACY-QR-CONTRACT certifies authenticated
 *            QR issue and verify GETs, tenantless seal-reference POST, stale
 *            legacy flag treatment, and fail-closed transport/configuration.
 *            v1.1.0-EOS-TENANT-SCOPED-REFERENCE-CHECK restores the authenticated
 *            seal-reference check while explicitly separating it from QR
 *            signature and document-content verification.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic hash and URL only; no live identity or network.
 * TENANT BOUNDARY: The request carries no tenant field; EOS session authorization
 *                  owns exact tenant scope.
 * AUTHORITY BOUNDARY: UI test evidence only; no invoice or legal truth is created.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
 */
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

const { apiGet, apiPost } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  default: { get: apiGet, post: apiPost },
}));

vi.mock('qrcode', () => ({
  default: { toDataURL: vi.fn().mockResolvedValue('data:image/png;base64,synthetic') },
}));

import ForensicProofBlock from '../../components/billing/ForensicProofBlock.jsx';

const sealHash = 'a'.repeat(128);
const encodedPayload = 'eyJpbnZvaWNlSWQiOiJpbnZvaWNlLTEifQ.SYNTHETIC-SIGNATURE';
const verificationUrl = `https://wilsy.example/api/qr/verify/${encodedPayload}`;
const invoice = Object.freeze({
  invoiceId: 'INV-SYNTHETIC-1',
  invoiceNumber: 'INV-SYNTHETIC-1',
  traceId: 'TRACE-SYNTHETIC-1',
  sealHash,
  qrVerified: true,
});

const issueResult = {
  data: {
    verificationUrl,
    encodedPayload,
    persisted: false,
  },
};

const validQrResult = {
  data: {
    valid: true,
    verificationMode: 'LEGACY_SIGNED_QR_PERSISTED_INVOICE_MATCH',
  },
};

describe('ForensicProofBlock authenticated Python EOS evidence boundary', () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiGet.mockImplementation((path) => (
      path.startsWith('/qr/verify/') ? Promise.resolve(validQrResult) : Promise.resolve(issueResult)
    ));
    apiPost.mockResolvedValue({ data: { valid: true } });
  });

  it('issues and verifies the legacy QR separately from the persisted seal reference', async () => {
    render(<ForensicProofBlock invoice={invoice} />);

    expect(screen.getByTestId('forensic-proof-status')).toHaveTextContent('NOT CHECKED');
    expect(screen.getByText(/stored legacy qrVerified flag is present/i)).toBeInTheDocument();
    expect(await screen.findByAltText(/signed qr reference for invoice/i)).toBeInTheDocument();
    expect(screen.getByTestId('signed-qr-state')).toHaveTextContent('SIGNED QR AVAILABLE');
    expect(apiGet).toHaveBeenCalledWith(
      '/billing/invoices/INV-SYNTHETIC-1/qr',
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );

    fireEvent.click(screen.getByRole('button', { name: 'Verify signed QR' }));
    expect(await screen.findByTestId('signed-qr-state')).toHaveTextContent('SIGNED QR VERIFIED');
    expect(apiGet).toHaveBeenCalledWith(
      `/qr/verify/${encodeURIComponent(encodedPayload)}`,
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );
    expect(screen.getByText(/pki, payment, and settlement were not evaluated/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Check seal reference' }));
    expect(await screen.findByTestId('forensic-proof-status')).toHaveTextContent(
      'SEAL REFERENCE MATCHED',
    );
    expect(screen.getByText(/does not verify a qr signature or invoice content/i)).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith(
      '/billing/merkle/verify',
      { seal_hash: sealHash },
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );
    expect(apiPost.mock.calls[0][1]).not.toHaveProperty('tenant_id');
    expect(apiPost.mock.calls[0][1]).not.toHaveProperty('tenantId');
  });

  it('keeps a tenant-scoped miss distinct from unavailable verification', async () => {
    apiPost.mockResolvedValueOnce({ data: { valid: false } });
    render(<ForensicProofBlock invoice={invoice} />);

    fireEvent.click(screen.getByRole('button', { name: 'Check seal reference' }));

    expect(await screen.findByTestId('forensic-proof-status')).toHaveTextContent(
      'SEAL REFERENCE NOT FOUND',
    );
  });

  it('reports transport failure without presenting a seal-reference match', async () => {
    apiPost.mockRejectedValueOnce(new Error('transport unavailable'));
    render(<ForensicProofBlock invoice={invoice} />);

    fireEvent.click(screen.getByRole('button', { name: 'Check seal reference' }));

    expect(await screen.findByTestId('forensic-proof-status')).toHaveTextContent(
      'VERIFICATION UNAVAILABLE',
    );
    expect(screen.getByText(/authenticated seal-reference check is unavailable/i))
      .toBeInTheDocument();
  });

  it('fails closed when the signed QR request is unavailable', async () => {
    apiGet.mockRejectedValueOnce(new Error('configuration unavailable'));
    render(<ForensicProofBlock invoice={invoice} />);

    await waitFor(() => {
      expect(screen.getByTestId('signed-qr-state')).toHaveTextContent('SIGNED QR UNAVAILABLE');
    });
    expect(screen.getByTestId('signed-qr-state')).toHaveTextContent('configuration unavailable');
    expect(screen.getByRole('button', { name: 'Verify signed QR' })).toBeDisabled();
  });

  it('does not send malformed seal references', async () => {
    render(<ForensicProofBlock invoice={{ ...invoice, sealHash: 'not-a-seal' }} />);

    await waitFor(() => expect(apiGet).toHaveBeenCalledWith(
      '/billing/invoices/INV-SYNTHETIC-1/qr',
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    ));
    expect(screen.queryByRole('button', { name: 'Check seal reference' })).not.toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: WILSY OS Forensic Proof Reference Client Certificate
 * VERSION: v1.2.1-TEST-ASYNC-CLEANUP
 * AUTHORITY BOUNDARY: Deterministic client transport evidence only.
 * TENANT POSTURE: Tenant scope remains in authenticated EOS context.
 * FAIL-CLOSED POSTURE: QR flags, malformed hashes, and transport errors never prove a match.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
