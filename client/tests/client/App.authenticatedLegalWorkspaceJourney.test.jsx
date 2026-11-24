/**
 * TENANT BOUNDARY: Exact tenant scope, membership and entitlements remain server-governed.
 * AUTHORITY BOUNDARY: No new IAM, admission, session or business execution authority is created.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
 * TITLE: WILSY OS Authenticated Legal Workspace Journey Certificate
 * VERSION: v1.6.0-SYSTEM-ACCOUNT-IDENTITY-CERT
 * AUTHORITY: Client integration evidence only; Python EOS remains authoritative.
 * CHANGELOG: v1.6.0-SYSTEM-ACCOUNT-IDENTITY-CERT proves SYSTEM promotion displays no tenant or login-email candidate in the account menu.
 * CHANGELOG: v1.5.0-ACCOUNT-LOGOUT-DELEGATION-CERT proves the menu Sign out action delegates once to the existing canonical AuthProvider logout callback.
 * CHANGELOG: v1.4.0-ACCOUNT-EMAIL-PROVENANCE-CERT proves account chrome consumes only EOS-sourced workspaceEmail even when the compatibility email differs.
 * CHANGELOG: v1.3.1-DYNAMIC-ACCOUNT-SESSION-CLEAR-CERT adds signed-out identity removal to the exact principal, tenant, capacity, optional-field, unsupported-action and keyboard dismissal certificate.
 * CHANGELOG: v1.3.0-DYNAMIC-ACCOUNT-IDENTITY-CERT verifies exact active-principal identity, tenant and capacity projection, optional-field absence, unsupported-action omission, principal-switch clearing, and keyboard dismissal.
 * CHANGELOG: v1.2.7-GLOBAL-SEARCH-DISMISS-FOCUS-CERT verifies Escape and backdrop dismissal restore focus for the no-owner fallback.
 * CHANGELOG: v1.2.6-GLOBAL-SEARCH-FOCUS-RETURN-CERT verifies workspace search returns keyboard focus to the opener after Escape.
 * CHANGELOG: v1.2.5-FOUNDER-SQUARE-ADMISSION-CERT preserves every admission/session test while verifying the preserved square corporate logo in global chrome.
 * CHANGELOG: v1.2.3-OFFICIAL-SQUARE-LOGO-ADMISSION-CERT requires the approved vivid square
 * presentation asset while preserving all authentication and admission gates.
 * CHANGELOG: v1.2.2-FOUNDER-SUPPLIED-LOGO-ADMISSION-CERT requires the selected square navy asset
 * in authenticated chrome while preserving every admission and session gate.
 * CHANGELOG: v1.2.1-SQUARE-LOGO-ADMISSION-CERT preserves exact admission assertions while checking the Founder-selected square logo by its accurate accessible name.
 *            v1.2.0-HEADQUARTERS-ADMISSION-CURRENTNESS-CERT adds deterministic
 *            stale-covenant, duplicate-bootstrap, logout-race and identity-switch
 *            regression cases. The existing legal and dunning boundaries remain.
 *            v1.2.0-HEADQUARTERS-ADMISSION-CURRENTNESS-CERT verifies no restricted dunning read is
 *            used to determine login or subscription lifecycle authority.
 *            v1.0.0-AUTH-BOOTSTRAP-LEGAL-BOUNDARY-JOURNEY verified authenticated Legal admission.
 * EPITOME: Exercises persisted-session revalidation, exact authenticated tenant
 *          handoff, and the server-owned legal-acceptance barrier before runtime.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.authenticatedLegalWorkspaceJourney.test.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider, TenantProvider, legal acceptance and EOS IAM.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
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
import App, { AuthenticatedGlobalChrome, AuthenticatedTenantBoundary, LegalAcceptanceBoundary } from '../../src/App.jsx';

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
    expect(screen.getAllByAltText("WILSY OS logo")).toHaveLength(1);
    expect(screen.getByAltText("WILSY OS logo")).toHaveAttribute("src", "/brand/wilsy-os-official.png");
    expect(screen.getAllByText("Legal partner capacity").length).toBeGreaterThan(0);
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
    expect(screen.getAllByAltText('WILSY OS logo')).toHaveLength(1);
    expect(screen.getByAltText('WILSY OS logo')).toHaveAttribute('src', '/brand/wilsy-os-official.png');
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



  it('renders account identity only from the exact active principal and tenant, then clears it on principal switch', async () => {
    const firstUser = {
      id: 'PRINCIPAL-ACCOUNT-A',
      firstName: 'Ada',
      lastName: 'Example',
      email: 'login-candidate@example.test',
      workspaceEmail: 'ada@example.test',
      tenantId: 'TENANT-ACCOUNT-A',
      role: 'tenant_owner',
      businessRole: 'tenant_owner',
      workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
      jobTitle: 'Forged title',
      avatarUrl: 'https://invalid.example/avatar.png',
    };
    const firstAuth = {
      isAuthenticated: true,
      authStage: 'AUTHENTICATED',
      loading: false,
      sessionGeneration: 1,
      user: firstUser,
      tenant: { tenantId: firstUser.tenantId, legalName: 'Example Organisation' },
    };
    const tree = (auth, user) => (
      <MemoryRouter>
        <AuthContext.Provider value={auth}>
          <AuthenticatedGlobalChrome user={user} onLogout={vi.fn()} workspaceReleased={false}>
            <main>Workspace</main>
          </AuthenticatedGlobalChrome>
        </AuthContext.Provider>
      </MemoryRouter>
    );
    const view = render(tree(firstAuth, firstUser));
    const trigger = screen.getByRole('button', { name: 'Open account menu' });
    fireEvent.click(trigger);
    const menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Ada Example');
    expect(menu).toHaveTextContent('ada@example.test');
    expect(menu).not.toHaveTextContent('login-candidate@example.test');
    expect(menu).toHaveTextContent('Example Organisation');
    expect(menu).toHaveTextContent('Selected capacity: Owner');
    expect(menu).not.toHaveTextContent('Forged title');
    expect(menu.querySelector('img')).toBeNull();
    expect(menu).not.toHaveTextContent('Kernel diagnostics');
    expect(menu).not.toHaveTextContent('Preferences');
    expect(menu).not.toHaveTextContent('Security & sessions');
    expect(screen.getByRole('menuitem', { name: 'Sign out' })).toBeEnabled();

    const secondUser = {
      id: 'PRINCIPAL-ACCOUNT-B',
      firstName: 'Bryn',
      lastName: 'Second',
      tenantId: 'TENANT-ACCOUNT-B',
      role: 'tenant_auditor',
      businessRole: 'tenant_auditor',
      workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
    };
    view.rerender(tree({
      ...firstAuth,
      sessionGeneration: 2,
      user: secondUser,
      tenant: { tenantId: secondUser.tenantId, name: 'Second Organisation' },
    }, secondUser));
    expect(screen.queryByRole('menu', { name: 'Account menu' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    const secondMenu = screen.getByRole('menu', { name: 'Account menu' });
    expect(secondMenu).toHaveTextContent('Bryn Second');
    expect(secondMenu).toHaveTextContent('Second Organisation');
    expect(secondMenu).toHaveTextContent('Selected capacity: Auditor');
    expect(secondMenu).not.toHaveTextContent('Ada Example');
    expect(secondMenu).not.toHaveTextContent('Example Organisation');
    expect(secondMenu).not.toHaveTextContent('ada@example.test');

    view.rerender(tree({
      ...firstAuth,
      isAuthenticated: false,
      authStage: 'IDLE',
      sessionGeneration: 3,
      user: null,
      tenant: null,
    }, secondUser));
    expect(screen.queryByRole('button', { name: 'Open account menu' })).not.toBeInTheDocument();
    expect(screen.queryByText('Ada Example')).not.toBeInTheDocument();
    expect(screen.queryByText('Bryn Second')).not.toBeInTheDocument();
  });



  it('keeps SYSTEM account identity tenant-free and omits the login email candidate', () => {
    const user = {
      id: 'PRINCIPAL-SYSTEM-ACCOUNT',
      email: 'login-candidate@example.test',
      role: 'SYSTEM_SERVICES',
      workspaceId: 'SYSTEM_SERVICES',
      systemServicesWorkspace: {
        status: 'READY',
        authority: 'EOS_SYSTEM_SERVICES',
        scope: 'SYSTEM',
        principalId: 'PRINCIPAL-SYSTEM-ACCOUNT',
        capabilities: ['system_services:queue:read'],
      },
    };
    const auth = {
      isAuthenticated: true,
      authStage: 'AUTHENTICATED',
      loading: false,
      sessionGeneration: 1,
      user,
      tenant: null,
    };
    render(
      <MemoryRouter>
        <AuthContext.Provider value={auth}>
          <AuthenticatedGlobalChrome user={user} onLogout={vi.fn()} workspaceReleased={false}>
            <main>System workspace</main>
          </AuthenticatedGlobalChrome>
        </AuthContext.Provider>
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    const menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Name not provided by EOS');
    expect(menu).not.toHaveTextContent('login-candidate@example.test');
    expect(menu).not.toHaveTextContent('SYSTEM_SERVICES');
    expect(menu).not.toHaveTextContent('TENANT');
    expect(screen.getByRole('menuitem', { name: 'Sign out' })).toBeEnabled();
  });

  it('delegates Sign out exactly once to the existing logout authority', () => {
    const user = {
      id: 'PRINCIPAL-ACCOUNT-LOGOUT',
      tenantId: 'TENANT-ACCOUNT-LOGOUT',
      role: 'tenant_owner',
      workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
    };
    const auth = {
      isAuthenticated: true,
      authStage: 'AUTHENTICATED',
      loading: false,
      sessionGeneration: 1,
      user,
      tenant: { tenantId: user.tenantId },
    };
    const onLogout = vi.fn();
    render(
      <MemoryRouter>
        <AuthContext.Provider value={auth}>
          <AuthenticatedGlobalChrome user={user} onLogout={onLogout} workspaceReleased={false}>
            <main>Workspace</main>
          </AuthenticatedGlobalChrome>
        </AuthContext.Provider>
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu' }));
    fireEvent.click(screen.getByRole('menuitem', { name: 'Sign out' }));
    expect(onLogout).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole('menu', { name: 'Account menu' })).not.toBeInTheDocument();
  });

  it('does not invent optional identity values and restores focus after Escape', async () => {
    const user = {
      id: 'PRINCIPAL-ACCOUNT-MINIMAL',
      tenantId: 'TENANT-ACCOUNT-MINIMAL',
      role: 'tenant_owner',
      businessRole: 'tenant_owner',
      workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
    };
    const auth = {
      isAuthenticated: true,
      authStage: 'AUTHENTICATED',
      loading: false,
      sessionGeneration: 1,
      user,
      tenant: { tenantId: user.tenantId },
    };
    render(
      <MemoryRouter>
        <AuthContext.Provider value={auth}>
          <AuthenticatedGlobalChrome user={user} onLogout={vi.fn()} workspaceReleased={false}>
            <main>Workspace</main>
          </AuthenticatedGlobalChrome>
        </AuthContext.Provider>
      </MemoryRouter>,
    );
    const trigger = screen.getByRole('button', { name: 'Open account menu' });
    fireEvent.click(trigger);
    const menu = screen.getByRole('menu', { name: 'Account menu' });
    expect(menu).toHaveTextContent('Name not provided by EOS');
    expect(menu).not.toHaveTextContent('@');
    expect(menu).toHaveTextContent('Selected capacity: Owner');
    expect(screen.getByRole('menuitem', { name: 'Sign out' })).toHaveFocus();
    fireEvent.keyDown(screen.getByRole('menuitem', { name: 'Sign out' }), { key: 'Escape' });
    expect(screen.queryByRole('menu', { name: 'Account menu' })).not.toBeInTheDocument();
    await waitFor(() => expect(trigger).toHaveFocus());
  });

  it('returns keyboard focus to the header control that opened workspace search', async () => {
    const user = {
      id: userId,
      email: 'partner@example.test',
      firstName: 'Canonical',
      lastName: 'Partner',
      tenantId,
      role: 'tenant_owner',
      workspaceId: 'WILSY_HEADQUARTERS',
    };
    const auth = {
      isAuthenticated: true,
      authStage: 'AUTHENTICATED',
      loading: false,
      token: 'synthetic-session-token',
      sessionGeneration: 1,
      user,
    };
    const view = render(
      <MemoryRouter>
        <AuthContext.Provider value={auth}>
          <AuthenticatedGlobalChrome user={user} onLogout={vi.fn()} workspaceReleased={false}>
            <main>Authenticated workspace</main>
          </AuthenticatedGlobalChrome>
        </AuthContext.Provider>
      </MemoryRouter>,
    );
    const trigger = view.container.querySelector('button[aria-label="Open workspace navigation"]');
    expect(trigger).not.toBeNull();
    trigger.focus();
    fireEvent.click(trigger);
    expect(screen.getByRole('dialog', { name: 'Workspace navigation' })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'Workspace destination' })).toHaveFocus();

    fireEvent.keyDown(window, { key: 'Escape' });

    await waitFor(() => expect(trigger).toHaveFocus());
    expect(screen.queryByRole('dialog', { name: 'Workspace navigation' })).not.toBeInTheDocument();

    fireEvent.click(trigger);
    const dismissedDialog = screen.getByRole('dialog', { name: 'Workspace navigation' });
    expect(screen.getByRole('textbox', { name: 'Workspace destination' })).toHaveFocus();
    fireEvent.mouseDown(dismissedDialog.parentElement);

    await waitFor(() => expect(trigger).toHaveFocus());
    expect(screen.queryByRole('dialog', { name: 'Workspace navigation' })).not.toBeInTheDocument();
  });

});

/*
 * ARTIFACT: App.authenticatedLegalWorkspaceJourney.test.jsx
 * VERSION: v1.6.0-SYSTEM-ACCOUNT-IDENTITY-CERT
 * AUTHORITY BOUNDARY: Synthetic authenticated journey test only.
 * TENANT POSTURE: Server-issued exact tenant only.
 * FAIL-CLOSED POSTURE: No implicit billing permission or login bypass.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
