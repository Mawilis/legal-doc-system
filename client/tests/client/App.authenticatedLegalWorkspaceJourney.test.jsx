/**
 * TITLE: WILSY OS Authenticated Legal Workspace Journey Certificate
 * VERSION: v1.2.0-HEADQUARTERS-ADMISSION-CURRENTNESS-CERT
 * AUTHORITY: Client integration evidence only; Python EOS remains authoritative.
 * CHANGELOG: v1.2.0-HEADQUARTERS-ADMISSION-CURRENTNESS-CERT adds deterministic
 *            stale-covenant, duplicate-bootstrap, logout-race and identity-switch
 *            regression cases. The existing legal and dunning boundaries remain.
 *            v1.2.0-HEADQUARTERS-ADMISSION-CURRENTNESS-CERT verifies no restricted dunning read is
 *            used to determine login or subscription lifecycle authority.
 *            v1.0.0-AUTH-BOOTSTRAP-LEGAL-BOUNDARY-JOURNEY verified authenticated Legal admission.
 * EPITOME: Exercises persisted-session revalidation, exact authenticated tenant
 *          handoff, and the server-owned legal-acceptance barrier before runtime.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.authenticatedLegalWorkspaceJourney.test.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider, TenantProvider, legal acceptance and EOS IAM.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic identities and tokens only.
 * TENANT BOUNDARY: The exact READY workspace-bootstrap tenant must match the
 *                  authenticated principal before the Legal runtime is mounted.
 * AUTHORITY BOUNDARY: This test creates no identity, membership, role, legal
 *                     acceptance, confidentiality clearance, or G68 authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api, sovereignClient, setActiveTenantTransportId } = vi.hoisted(() => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    defaults: { headers: { common: {} } },
  },
  sovereignClient: {
    get: vi.fn(),
  },
  setActiveTenantTransportId: vi.fn(),
}));

vi.mock('../../src/services/api', () => ({
  default: api,
  setActiveTenantTransportId,
}));
vi.mock('../../src/utils/sovereignClient', () => ({ default: sovereignClient }));

vi.mock('../../src/components/sovereign/SovereignDashboardController.jsx', () => ({
  default: () => <main><h1>WILSY Headquarters</h1></main>,
}));
vi.mock('../../src/components/intelligence/WilsyOSIntelligenceDockRuntime.jsx', () => ({
  default: () => null,
}));

import AuthContext, { AuthProvider, useAuth } from '../../src/contexts/authContext.jsx';
import App, { AuthenticatedTenantBoundary, LegalAcceptanceBoundary } from '../../src/App.jsx';

const tenantId = 'TENANT-LEGAL-JOURNEY';
const userId = 'PRINCIPAL-LEGAL-JOURNEY';
const runtime = <main data-testid="authenticated-legal-runtime">Authenticated Legal workspace shell</main>;

const readyWorkspace = {
  status: 'READY',
  user: {
    id: userId,
    email: 'partner@example.test',
    firstName: 'Canonical',
    lastName: 'Partner',
  },
  workspace: {
    tenantId,
    businessRole: 'tenant_legal_partner',
    workspaceId: 'LEGAL_PRACTICE',
    workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
    membershipRevision: 4,
    businessRoleRevision: 9,
    legalPermissions: [
      'legal_operations:instruction:write',
      'legal_operations:return:write',
      'legal_operations:productive_work:read',
    ],
    branding: null,
    tenant: {
      tenantId,
      name: 'Canonical Legal Practice',
      legalName: 'Canonical Legal Practice (Pty) Ltd',
      status: 'ACTIVE',
    },
  },
};

describe('authenticated Legal workspace journey', () => {
  beforeEach(() => {
    const values = new Map([
      ['wilsy_auth_token', 'synthetic-session-token'],
      ['token', 'synthetic-session-token'],
      ['wilsy_sovereign_user', JSON.stringify({ id: userId, email: 'partner@example.test' })],
    ]);
    const storage = {
      getItem: (key) => values.get(key) || null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: (key) => values.delete(key),
      clear: () => values.clear(),
    };
    Object.defineProperty(window, 'localStorage', { configurable: true, value: storage });
    Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
    api.get.mockReset();
    api.post.mockReset();
    delete api.defaults.headers.common.Authorization;
    delete api.defaults.headers.common['x-tenant-id'];
    sovereignClient.get.mockReset().mockResolvedValue({ data: {} });
    setActiveTenantTransportId.mockReset();
    window.history.replaceState({}, '', '/');
  });

  it('revalidates the session and exact tenant before releasing the Legal workspace after server COMPLETE', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/auth/workspace-bootstrap') return Promise.resolve({ data: readyWorkspace });
      if (path === '/legal-acceptance/status') {
        return Promise.resolve({ data: { status: 'COMPLETE', admissionScope: 'PLATFORM_WORKSPACE', tenantId, principalId: userId, documents: [] } });
      }
      throw new Error(`Unexpected API read: ${path}`);
    });

    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <AuthenticatedTenantBoundary runtime={runtime} />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByTestId('authenticated-legal-runtime')).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/auth/workspace-bootstrap', {
      headers: { Authorization: 'Bearer synthetic-session-token' },
      skipAuthRedirect: true,
      signal: expect.any(AbortSignal),
    });
    expect(api.get).toHaveBeenCalledWith('/legal-acceptance/status', {
      headers: { Authorization: 'Bearer synthetic-session-token' },
      skipAuthRedirect: true, signal: expect.any(AbortSignal),
    });
    expect(api.defaults.headers.common.Authorization).toBe('Bearer synthetic-session-token');
    expect(setActiveTenantTransportId).toHaveBeenCalledWith(tenantId);
    // A restricted collection projection is not subscription lifecycle truth.
    // Login must not issue or require that unrelated privileged request.
    expect(sovereignClient.get).not.toHaveBeenCalled();
  });

  it('does not mount the Legal workspace while server legal acceptance is incomplete', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/auth/workspace-bootstrap') return Promise.resolve({ data: readyWorkspace });
      if (path === '/legal-acceptance/status') {
        return Promise.resolve({
          data: {
            status: 'USER_TERMS_REQUIRED',
            admissionScope: 'PLATFORM_WORKSPACE',
            principalId: userId,
            tenantId,
            documents: [{
              agreementType: 'USER_TERMS',
              documentId: 'terms-v1',
              version: '1.0.0-APPROVED',
              sha3_512: 'b'.repeat(128),
              title: 'WILSY OS User Terms',
              locale: 'en-ZA',
              effectiveFrom: '2026-09-20T00:00:00Z',
              content: 'Synthetic server-issued terms for the integration test.',
              accepted: false,
            }],
          },
        });
      }
      throw new Error(`Unexpected API read: ${path}`);
    });

    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <AuthenticatedTenantBoundary runtime={runtime} />
        </AuthProvider>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.queryByTestId('authenticated-legal-runtime')).not.toBeInTheDocument());
    expect(await screen.findByRole("table", { name: "Required legal document records" })).toBeInTheDocument();
    expect(screen.getByText("PLATFORM WORKSPACE AGREEMENTS")).toBeInTheDocument();
    expect(screen.queryByTestId("system-rail")).not.toBeInTheDocument();
    expect(screen.getAllByAltText("WILSY gold emblem")).toHaveLength(1);
    expect(api.get).toHaveBeenCalledWith('/auth/workspace-bootstrap', {
      headers: { Authorization: 'Bearer synthetic-session-token' },
      skipAuthRedirect: true,
      signal: expect.any(AbortSignal),
    });
    expect(api.get).toHaveBeenCalledWith('/legal-acceptance/status', {
      headers: { Authorization: 'Bearer synthetic-session-token' },
      skipAuthRedirect: true, signal: expect.any(AbortSignal),
    });
  });
  it('does not nest a second admission shell at a stale covenant URL after COMPLETE', async () => {
    window.history.replaceState({}, '', '/covenant');
    let statusReads = 0;
    api.get.mockImplementation((path) => {
      if (path === '/auth/workspace-bootstrap') return Promise.resolve({ data: readyWorkspace });
      if (path === '/legal-acceptance/status') {
        statusReads += 1;
        return statusReads === 1
          ? Promise.resolve({ data: { status: 'COMPLETE', admissionScope: 'PLATFORM_WORKSPACE', tenantId, principalId: userId, documents: [] } })
          : new Promise(() => {});
      }
      return Promise.resolve({ data: {} });
    });
    render(<App />);
    await waitFor(() => expect(screen.getByRole('heading', { name: 'WILSY Headquarters' })).toBeInTheDocument());
    expect(statusReads).toBe(1);
    expect(screen.queryByText('Resolving server evidence')).not.toBeInTheDocument();
    expect(screen.queryByText('LEGAL ADMISSION CONTROL')).not.toBeInTheDocument();
    expect(screen.getAllByAltText('WILSY gold emblem')).toHaveLength(1);
  });

  it('deduplicates an in-flight restoration under Strict Mode', async () => {
    let resolveBootstrap;
    const bootstrap = new Promise((resolve) => { resolveBootstrap = resolve; });
    api.get.mockImplementation((path) => {
      if (path === '/auth/workspace-bootstrap') return bootstrap;
      return Promise.resolve({ data: { status: 'COMPLETE', admissionScope: 'PLATFORM_WORKSPACE', tenantId, principalId: userId, documents: [] } });
    });
    render(<React.StrictMode><MemoryRouter><AuthProvider><AuthenticatedTenantBoundary runtime={runtime} /></AuthProvider></MemoryRouter></React.StrictMode>);
    expect(api.get.mock.calls.filter(([path]) => path === '/auth/workspace-bootstrap')).toHaveLength(1);
    await act(async () => { resolveBootstrap({ data: readyWorkspace }); });
    expect(await screen.findByTestId('authenticated-legal-runtime')).toBeInTheDocument();
  });

  it('cannot resurrect a logged-out session from a late bootstrap response', async () => {
    let resolveBootstrap;
    api.get.mockReturnValue(new Promise((resolve) => { resolveBootstrap = resolve; }));
    const Probe = () => {
      const auth = useAuth();
      return <><output data-testid="auth-status">{String(auth.isAuthenticated)}</output><button onClick={() => auth.logout()}>End session</button></>;
    };
    render(<AuthProvider><Probe /></AuthProvider>);
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'End session' })); });
    await act(async () => { resolveBootstrap({ data: readyWorkspace }); });
    expect(screen.getByTestId('auth-status')).toHaveTextContent('false');
    expect(localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(api.defaults.headers.common.Authorization).toBeUndefined();
  });

  it('invalidates completed admission immediately when the selected capacity changes', async () => {
    const first = { token: 'synthetic-scope-a', isAuthenticated: true, authStage: 'AUTHENTICATED', loading: false, user: { id: userId, tenantId, role: 'tenant_owner', workspaceId: 'WILSY_HEADQUARTERS' }, tenant: readyWorkspace.workspace.tenant };
    api.get.mockResolvedValueOnce({ data: { status: 'COMPLETE', admissionScope: 'PLATFORM_WORKSPACE', tenantId, principalId: userId, documents: [] } }).mockReturnValue(new Promise(() => {}));
    const tree = (auth) => <MemoryRouter><AuthContext.Provider value={auth}><LegalAcceptanceBoundary runtime={runtime} /></AuthContext.Provider></MemoryRouter>;
    const view = render(tree(first));
    expect(await screen.findByTestId('authenticated-legal-runtime')).toBeInTheDocument();
    view.rerender(tree({ ...first, token: 'synthetic-scope-b', user: { ...first.user, role: 'tenant_legal_partner', workspaceId: 'LEGAL_PRACTICE' } }));
    expect(screen.queryByTestId('authenticated-legal-runtime')).not.toBeInTheDocument();
    expect(screen.getByTestId('workspace-bootstrap')).toBeInTheDocument();
  });

});

/*
 * ARTIFACT: App.authenticatedLegalWorkspaceJourney.test.jsx
 * VERSION: v1.2.0-HEADQUARTERS-ADMISSION-CURRENTNESS-CERT
 * AUTHORITY BOUNDARY: Synthetic authenticated journey test only.
 * TENANT POSTURE: Server-issued exact tenant only.
 * FAIL-CLOSED POSTURE: No implicit billing permission or login bypass.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
