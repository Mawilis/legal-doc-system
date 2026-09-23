/**
 * TITLE: Authoritative Browser Authentication State Certificate
 * VERSION: v1.1.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves exact discovery transport, MFA reconciliation projection,
 *          QR suppression, and durable-session transition in the browser.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/contexts/authContext.authoritative.test.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider and the Python EOS auth router.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.0-AUTHORITATIVE-MFA-STATE-CERT — Initial focused certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Test fixtures contain synthetic identities only.
 * TENANT BOUNDARY: Tenant projection is accepted only from discovery/session data.
 * AUTHORITY BOUNDARY: Browser projection only; server owns authentication truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    defaults: { headers: { common: {} } },
  },
}));

vi.mock('@/services/api', () => ({ default: api }));

import { AUTH_STATES, AuthProvider, useAuth } from '../../src/contexts/authContext.jsx';

const authoritativeUser = {
  id: 'WILSYAUTH-browser-user',
  email: 'person@example.com',
  tenantId: 'TENANT-BROWSER',
  permissions: ['legal:read'],
  mfaRegistered: true,
};

const workspaceBootstrap = ({
  tenantId = 'TENANT-BROWSER',
  businessRole = 'tenant_auditor',
} = {}) => ({
  data: {
    status: 'READY',
    user: {
      id: 'WILSYAUTH-browser-user',
      email: 'person@example.com',
    },
    workspace: {
      tenantId,
      businessRole,
      membershipRevision: 7,
      businessRoleRevision: 11,
      tenant: {
        tenantId,
        name: `Canonical ${tenantId}`,
        legalName: `Canonical ${tenantId} (Pty) Ltd`,
        status: 'ACTIVE',
      },
    },
  },
});

function Harness() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="stage">{auth.authStage}</span>
      <span data-testid="authenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="qr">{auth.qrCodeData || ''}</span>
      <span data-testid="role">{auth.userRole || ''}</span>
      <span data-testid="tenant-id">{auth.tenantId || ''}</span>
      <button type="button" onClick={() => auth.discoverTenant('Acme Law')}>discover</button>
      <button type="button" onClick={() => { void auth.login('person@example.com', 'password').catch(() => {}); }}>login</button>
      <button type="button" onClick={() => { void auth.verifyOTP('person@example.com', '123456').catch(() => {}); }}>verify</button>
      <button type="button" onClick={() => { void auth.logout(); }}>logout</button>
    </div>
  );
}

const renderHarness = () => render(<AuthProvider><Harness /></AuthProvider>);

describe('authoritative authentication state machine', () => {
  beforeEach(() => {
    const values = new Map();
    const storage = {
      getItem: (key) => values.get(key) || null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: (key) => values.delete(key),
      clear: () => values.clear(),
    };
    Object.defineProperty(window, 'localStorage', { configurable: true, value: storage });
    Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
    storage.clear();
    api.get.mockReset();
    api.post.mockReset();
    global.fetch = vi.fn();
  });

  it('uses exact bounded server discovery and never fabricates a tenant', async () => {
    global.fetch.mockResolvedValue(new Response(JSON.stringify({
      success: true,
      tenant: { tenantId: 'TENANT-ACME', alias: 'acme-law', name: 'Acme Law' },
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    renderHarness();

    fireEvent.click(screen.getByRole('button', { name: 'discover' }));

    await waitFor(() => expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE));
    expect(global.fetch).toHaveBeenCalledWith('/api/auth/discover', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ alias: 'acme law' }),
    }));
    expect(window.localStorage.getItem('discoveredTenant')).toContain('TENANT-ACME');
  });

  it('projects reconciliation without QR and persists only authenticated response', async () => {
    api.post
      .mockResolvedValueOnce({ data: { status: AUTH_STATES.MFA_RECONCILIATION_REQUIRED, tempToken: 'temp' } })
      .mockResolvedValueOnce({ data: { status: AUTH_STATES.AUTHENTICATED, token: 'session', user: authoritativeUser } });
    api.get.mockResolvedValueOnce(workspaceBootstrap());
    renderHarness();

    fireEvent.click(screen.getByRole('button', { name: 'login' }));
    await waitFor(() => expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.MFA_RECONCILIATION_REQUIRED));
    expect(screen.getByTestId('qr')).toHaveTextContent('');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');

    fireEvent.click(screen.getByRole('button', { name: 'verify' }));
    await waitFor(() => expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.AUTHENTICATED));
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    expect(api.defaults.headers.common.Authorization).toBe('Bearer session');
    expect(window.localStorage.getItem('wilsy_refresh_token')).toBeNull();
    expect(api.post).toHaveBeenNthCalledWith(2, '/auth/verify-otp', { email: 'person@example.com', code: '123456' });
  });

  it('fails closed when discovered and authenticated tenant identities diverge', async () => {
    global.fetch.mockResolvedValue(new Response(JSON.stringify({
      success: true,
      tenant: { tenantId: 'TENANT-DISCOVERED', alias: 'acme-law', name: 'Acme Law' },
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    api.post.mockResolvedValueOnce({ data: {
      status: AUTH_STATES.AUTHENTICATED,
      token: 'mismatched-token',
      user: { ...authoritativeUser, tenantId: 'TENANT-AUTHENTICATED' },
    } });
    api.get.mockResolvedValueOnce(workspaceBootstrap({
      tenantId: 'TENANT-AUTHENTICATED',
    }));
    renderHarness();

    fireEvent.click(screen.getByRole('button', { name: 'discover' }));
    await waitFor(() => expect(window.localStorage.getItem('discoveredTenant')).toContain('TENANT-DISCOVERED'));
    fireEvent.click(screen.getByRole('button', { name: 'login' }));

    await waitFor(() => expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.FAILED));
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(window.localStorage.getItem('wilsy_sovereign_user')).toBeNull();
  });

  it('does not elevate a restored browser user to authenticated authority without server revalidation', async () => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('wilsy_sovereign_user', JSON.stringify({
      id: 'forged-browser-user',
      email: 'forged@example.com',
      tenantId: 'FORGED-TENANT',
      role: 'OWNER',
      permissions: ['*'],
      mfaRegistered: true,
    }));

    renderHarness();

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('stage')).not.toHaveTextContent(AUTH_STATES.AUTHENTICATED);
  });

  it('updates and clears the canonical bearer synchronously at session boundaries', async () => {
    api.post
      .mockResolvedValueOnce({ data: { status: AUTH_STATES.AUTHENTICATED, token: 'first-token', user: authoritativeUser } })
      .mockResolvedValueOnce({ data: { status: AUTH_STATES.AUTHENTICATED, token: 'replacement-token', user: authoritativeUser } });
    api.get
      .mockResolvedValueOnce(workspaceBootstrap())
      .mockResolvedValueOnce(workspaceBootstrap());
    renderHarness();

    fireEvent.click(screen.getByRole('button', { name: 'login' }));
    await waitFor(() => expect(api.defaults.headers.common.Authorization).toBe('Bearer first-token'));
    fireEvent.click(screen.getByRole('button', { name: 'login' }));
    await waitFor(() => expect(api.defaults.headers.common.Authorization).toBe('Bearer replacement-token'));

    fireEvent.click(screen.getByRole('button', { name: 'logout' }));
    await waitFor(() => expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE));
    expect(api.defaults.headers.common.Authorization).toBeUndefined();
  });

  it('requires server workspace bootstrap before elevating an MFA session', async () => {
    let resolveBootstrap;
    const bootstrapPending = new Promise((resolve) => {
      resolveBootstrap = resolve;
    });

    api.post
      .mockResolvedValueOnce({
        data: {
          status: AUTH_STATES.MFA_REQUIRED,
          tempToken: 'mfa-candidate',
        },
      })
      .mockResolvedValueOnce({
        data: {
          status: AUTH_STATES.AUTHENTICATED,
          token: 'candidate-session-token',
          user: {
            id: 'WILSYAUTH-browser-user',
            email: 'person@example.com',
            tenantId: 'FORGED-BROWSER-TENANT',
            role: 'SUPER_ADMIN',
            permissions: ['*'],
            mfaRegistered: true,
          },
        },
      });

    api.get.mockReturnValueOnce(bootstrapPending);

    renderHarness();

    fireEvent.click(screen.getByRole('button', { name: 'login' }));
    await waitFor(() => {
      expect(screen.getByTestId('stage')).toHaveTextContent(
        AUTH_STATES.MFA_REQUIRED,
      );
    });

    fireEvent.click(screen.getByRole('button', { name: 'verify' }));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/auth/workspace-bootstrap',
        {
          headers: {
            Authorization: 'Bearer candidate-session-token',
          },
        },
      );
    });

    // The MFA response and candidate bearer alone are never browser authority.
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('stage')).not.toHaveTextContent(
      AUTH_STATES.AUTHENTICATED,
    );
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(window.localStorage.getItem('wilsy_sovereign_user')).toBeNull();

    resolveBootstrap({
      data: {
        status: 'READY',
        user: {
          id: 'WILSYAUTH-browser-user',
          email: 'person@example.com',
        },
        workspace: {
          tenantId: 'TENANT-BROWSER',
          businessRole: 'tenant_auditor',
          membershipRevision: 7,
          businessRoleRevision: 11,
          tenant: {
            tenantId: 'TENANT-BROWSER',
            name: 'Canonical Browser Tenant',
            legalName: 'Canonical Browser Tenant (Pty) Ltd',
            status: 'ACTIVE',
          },
        },
      },
    });

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    expect(screen.getByTestId('role')).toHaveTextContent('tenant_auditor');
    expect(screen.getByTestId('tenant-id')).toHaveTextContent('TENANT-BROWSER');

    const persistedUser = JSON.parse(
      window.localStorage.getItem('wilsy_sovereign_user'),
    );
    expect(persistedUser).toMatchObject({
      id: 'WILSYAUTH-browser-user',
      email: 'person@example.com',
      tenantId: 'TENANT-BROWSER',
      role: 'tenant_auditor',
    });
    expect(persistedUser.role).not.toBe('SUPER_ADMIN');
    expect(persistedUser.permissions || []).not.toContain('*');
  });

});

/**
 * ARTIFACT: client/tests/contexts/authContext.authoritative.test.jsx
 * VERSION: v1.1.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT
 * AUTHORITY BOUNDARY: deterministic browser projection certificate only
 * CHANGELOG: v1.1.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT — Added synchronous
 * canonical bearer replacement and logout-clearing evidence.
 * TENANT POSTURE: authenticated tenant must match the discovered server-issued tenant
 * FAIL-CLOSED POSTURE: session exists only after bounded authenticated response
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
