/**
 * TITLE: WILSY OS Authenticated Platform Agreement Boundary Certificate
 * VERSION: v2.0.0-SESSION-BOUND-PLATFORM-ADMISSION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves one admission boundary can only release a current, exact
 *          EOS-authenticated tenant/principal after mandatory agreements.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.p0AdmissionCurrentness.test.jsx
 * COLLABORATION / OWNERSHIP: AuthContext, LegalAcceptanceBoundary,
 *                            LegalAcceptanceGate, Python EOS agreement registry.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v2.0.0-SESSION-BOUND-PLATFORM-ADMISSION exercises the real
 *            AuthContext provider boundary, the signed admissionScope and
 *            tenant/principal contract, and classified 401/403/503 failures;
 *            its predecessor mounted the gate without any AuthProvider.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic principals and tokens only.
 * TENANT BOUNDARY: Matching exact EOS tenant and principal is mandatory.
 * AUTHORITY BOUNDARY: No browser-projected acceptance or IAM grants.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({
  api: { get: vi.fn(), post: vi.fn() },
}));
vi.mock('../../src/services/api', () => ({
  default: api,
}));

import AuthContext, { AUTH_STATES } from '../../src/contexts/authContext.jsx';
import { LegalAcceptanceBoundary } from '../../src/App.jsx';

const tenantId = 'TENANT-A';
const principalId = 'PRINCIPAL-A';
const bearer = 'synthetic-valid-session';
const session = {
  isAuthenticated: true,
  authStage: AUTH_STATES.AUTHENTICATED,
  loading: false,
  token: bearer,
  sessionGeneration: 1,
  user: {
    id: principalId, tenantId, role: 'tenant_owner',
    workspaceId: 'EXECUTIVE_COMMAND_CENTRE',
    membershipRevision: 3, businessRoleRevision: 7,
    firstName: 'Synthetic', lastName: 'Operator',
  },
  logout: vi.fn(),
};
const plan = (overrides = {}) => ({
  admissionScope: 'PLATFORM_WORKSPACE',
  status: 'COMPLETE', tenantId, principalId, documents: [],
  ...overrides,
});
const runtime = <section data-testid="authenticated-headquarters">Headquarters entry</section>;
const mount = (auth = session, route = '/') => render(
  <AuthContext.Provider value={auth}>
    <MemoryRouter initialEntries={[route]}>
      <LegalAcceptanceBoundary runtime={runtime} />
    </MemoryRouter>
  </AuthContext.Provider>,
);

beforeEach(() => {
  api.get.mockReset();
  api.post.mockReset();
});

describe('server-owned, current-session platform agreements', () => {
  it('never fetches protected acceptance status before authenticated bootstrap', async () => {
    mount({
      ...session, isAuthenticated: false, authStage: AUTH_STATES.IDLE, token: null,
    });
    expect(screen.getByTestId('workspace-bootstrap')).toBeInTheDocument();
    expect(api.get).not.toHaveBeenCalled();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('releases one runtime at /covenant only after exact server COMPLETE', async () => {
    api.get.mockResolvedValue({ data: plan() });
    mount(session, '/covenant');
    expect(await screen.findByTestId('authenticated-headquarters')).toBeInTheDocument();
    expect(screen.queryByText('LEGAL ADMISSION CONTROL')).not.toBeInTheDocument();
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledWith('/legal-acceptance/status', {
      headers: { Authorization: 'Bearer ' + bearer },
      skipAuthRedirect: true,
      signal: expect.any(AbortSignal),
    });
  });

  it('does not release a different tenant or principal after bootstrap', async () => {
    api.get.mockResolvedValue({ data: plan({ tenantId: 'OTHER-TENANT' }) });
    mount();
    expect(await screen.findByText('PLATFORM_ADMISSION_CONTRACT_INVALID')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('does not release an unaccepted document even if status falsely says COMPLETE', async () => {
    api.get.mockResolvedValue({ data: plan({
      documents: [{ agreementType: 'USER_TERMS', accepted: false }],
    }) });
    mount();
    expect(await screen.findByText('PLATFORM_ADMISSION_CONTRACT_INVALID')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('classifies a missing-credential 401 as a session failure', async () => {
    api.get.mockRejectedValue({
      response: { status: 401, data: { detail: 'Missing credentials' } },
    });
    mount();
    expect(await screen.findByText('SESSION_EXPIRED')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('distinguishes 403 permission denial from service unavailability', async () => {
    api.get.mockRejectedValue({
      response: { status: 403, data: { detail: 'Restricted access' } },
    });
    mount();
    expect(await screen.findByText('PLATFORM_ADMISSION_FORBIDDEN')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('remains sealed on a real server 503', async () => {
    api.get.mockRejectedValue({
      response: { status: 503, data: { detail: 'Server unavailable' } },
    });
    mount();
    await waitFor(() => expect(screen.getByText('PLATFORM_ADMISSION_UNAVAILABLE')).toBeInTheDocument());
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });
});

/*
 * ARTIFACT: App.p0AdmissionCurrentness.test.jsx
 * VERSION: v2.0.0-SESSION-BOUND-PLATFORM-ADMISSION
 * AUTHORITY BOUNDARY: Synthetic session integration evidence only.
 * TENANT POSTURE: Exact verified tenant/principal projection required.
 * FAIL-CLOSED POSTURE: Only matching COMPLETE releases the workspace.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
