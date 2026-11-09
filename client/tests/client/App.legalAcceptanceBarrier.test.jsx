/**
 * TITLE: WILSY OS Authenticated Platform-Use Acceptance Barrier Certificate
 * VERSION: v2.0.0-CURRENT-SESSION-PLATFORM-AGREEMENT-RELEASE
 * AUTHORITY: Wilsy OS Core Governance; browser is projection only.
 * EPITOME: Certifies status-before-runtime and real mandatory agreement
 *          handoff under an authenticated current-session App boundary.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.legalAcceptanceBarrier.test.jsx
 * COLLABORATION / OWNERSHIP: AuthContext, App LegalAcceptanceBoundary,
 *                            LegalAcceptanceGate and Python EOS evidence.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v2.0.0-CURRENT-SESSION-PLATFORM-AGREEMENT-RELEASE updates
 *            pre-workspace assertions for Codex's explicit bearer and
 *            PLATFORM_WORKSPACE response contract, retaining loading,
 *            required, denial, completion, reread and evidence tests.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic principals/bearers, no real writes.
 * TENANT BOUNDARY: Exact EOS tenant/principal must match current AuthContext.
 * AUTHORITY BOUNDARY: Only server-approved evidence may release the runtime.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { readFileSync } from 'node:fs';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthContext, { AUTH_STATES } from '../../src/contexts/authContext.jsx';
import { LegalAcceptanceBoundary } from '../../src/App.jsx';
import api from '../../src/services/api';

vi.mock('../../src/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const tenantId = 'tenant-1';
const principalId = 'principal-1';
const bearer = 'synthetic-authenticated-bearer';
const auth = {
  isAuthenticated: true, authStage: AUTH_STATES.AUTHENTICATED,
  loading: false, token: bearer, sessionGeneration: 1,
  user: {
    id: principalId, tenantId, role: 'tenant_owner',
    workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
    membershipRevision: 2, businessRoleRevision: 3,
    firstName: 'Synthetic', lastName: 'Operator',
  },
  logout: vi.fn(),
};

const required = {
  status: 'DOCUMENT_APPROVAL_REQUIRED',
  admissionScope: 'PLATFORM_WORKSPACE',
  tenantId, principalId,
  missingAgreementTypes: ['USER_TERMS'],
  documents: [],
};
const requiredAcceptance = {
  status: 'USER_TERMS_REQUIRED',
  admissionScope: 'PLATFORM_WORKSPACE',
  tenantId, principalId,
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
  documents: requiredAcceptance.documents.map((document) => ({ ...document, accepted: true })),
};
const complete = {
  status: 'COMPLETE', admissionScope: 'PLATFORM_WORKSPACE',
  tenantId, principalId, documents: [],
};
const runtime = <div data-testid="protected-runtime">Headquarters</div>;
const mount = (route = '/') => render(
  <AuthContext.Provider value={auth}>
    <MemoryRouter initialEntries={[route]}>
      <LegalAcceptanceBoundary runtime={runtime} />
    </MemoryRouter>
  </AuthContext.Provider>,
);

describe('current authenticated platform-use acceptance barrier', () => {
  beforeEach(() => vi.clearAllMocks());

  it('keeps runtime unmounted while exact authenticated status is pending', async () => {
    let resolve;
    api.get.mockReturnValue(new Promise((r) => { resolve = r; }));
    mount();
    expect(screen.getByTestId('workspace-bootstrap')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
    await act(async () => resolve({ data: required }));
    expect(await screen.findByText(/legal documents are being prepared/i)).toBeInTheDocument();
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
  });

  it('shows one platform agreement presentation for incomplete approved evidence', async () => {
    api.get.mockResolvedValue({ data: required });
    mount();
    expect(await screen.findByTestId('platform-agreement-frame')).toBeInTheDocument();
    expect(screen.queryByText('LEGAL ADMISSION CONTROL')).not.toBeInTheDocument();
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
  });

  it('fails closed on unavailable server acceptance status', async () => {
    api.get.mockRejectedValue({
      response: { status: 503, data: { detail: 'LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE' } },
    });
    mount();
    expect(await screen.findByText('PLATFORM_ADMISSION_UNAVAILABLE')).toBeInTheDocument();
    expect(screen.queryByTestId('protected-runtime')).not.toBeInTheDocument();
  });

  it('mounts protected runtime only after exact current-session COMPLETE', async () => {
    api.get.mockResolvedValue({ data: complete });
    mount();
    expect(await screen.findByTestId('protected-runtime')).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/legal-acceptance/status', {
      headers: { Authorization: 'Bearer ' + bearer },
      signal: expect.any(AbortSignal),
      skipAuthRedirect: true,
    });
  });

  it('releases runtime after final server-confirmed recorded acceptance', async () => {
    api.get.mockResolvedValueOnce({ data: requiredAcceptance })
      .mockResolvedValueOnce({ data: completeAcceptance });
    api.post.mockResolvedValueOnce({ data: { status: 'RECORDED' } });
    mount('/covenant');
    fireEvent.click(await screen.findByRole('button', { name: /review document/i }));
    fireEvent.click(screen.getByRole('button', { name: /record acceptance/i }));
    expect(await screen.findByTestId('protected-runtime')).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(screen.queryByTestId('document-focus-mode')).not.toBeInTheDocument();
  });

  it('never reuses completed agreement status after a new mount', async () => {
    api.get.mockResolvedValue({ data: complete });
    const first = mount();
    expect(await screen.findByTestId('protected-runtime')).toBeInTheDocument();
    first.unmount();
    mount();
    expect(await screen.findByTestId('protected-runtime')).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(api.get).toHaveBeenNthCalledWith(1, '/legal-acceptance/status', expect.objectContaining({
      headers: { Authorization: 'Bearer ' + bearer },
    }));
    expect(api.get).toHaveBeenNthCalledWith(2, '/legal-acceptance/status', expect.objectContaining({
      headers: { Authorization: 'Bearer ' + bearer },
    }));
  });

  it('contains one canonical platform status read in the App source', () => {
    const source = readFileSync('src/App.jsx', 'utf8');
    const statusReads = source.match(/api\.get\(['"]\/legal-acceptance\/status['"]/g) || [];
    expect(statusReads).toHaveLength(1);
    expect(source).not.toContain('const AcceptanceAwareWorkspace');
  });
});

/*
 * ARTIFACT: App.legalAcceptanceBarrier.test.jsx
 * VERSION: v2.0.0-CURRENT-SESSION-PLATFORM-AGREEMENT-RELEASE
 * AUTHORITY BOUNDARY: Synthetic authenticated barrier only.
 * TENANT POSTURE: Exact signed tenant/principal scope is revalidated.
 * FAIL-CLOSED POSTURE: Unavailable, incomplete or mismatched evidence blocks.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
