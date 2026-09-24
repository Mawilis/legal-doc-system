/**
 * TITLE: Authoritative Browser Authentication State Certificate
 * VERSION: v1.4.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves exact discovery transport, MFA reconciliation projection,
 *          QR suppression, and durable-session transition in the browser.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/contexts/authContext.authoritative.test.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider and the Python EOS auth router.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: v1.4.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION-CERT certifies that firstName/lastName enter browser auth state only from READY workspace-bootstrap, overwrite forged login/MFA and persisted-browser name candidates, allow explicit null optional names without inference, and reject malformed server name values before session promotion. Person names remain descriptive and create no role, permission, tenant, entitlement, Legal command, billing, payment, execution or settlement authority.
 *            v1.3.0-D17-SERVER-LEGAL-PERMISSION-PROJECTION-CERT certifies bounded consumption of the server-owned
 *            workspace.legalPermissions projection: exact permissions and
 *            authoritative empty lists retain provenance, field absence preserves
 *            compatibility posture, and malformed/duplicate/unknown permissions
 *            fail session promotion closed without trusting login/JWT claims.
 *            v1.2.0-SERVER-REVALIDATED-SESSION-RESTORE-CERT certifies that a
 *            persisted bearer candidate survives browser remount only after
 *            workspace-bootstrap revalidates current server authority; forged,
 *            mismatched or rejected candidates fail closed while discovered
 *            tenant navigation context remains available.
 *            v1.1.0-R1D-B0F-B4-R3-CANONICAL-TRANSPORT-CERT certified synchronous
 *            bearer replacement and logout clearing.
 *            v1.0.0-AUTHORITATIVE-MFA-STATE-CERT — Initial focused certificate.
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
  firstName: 'FORGED LOGIN FIRST',
  lastName: 'FORGED LOGIN LAST',
  tenantId: 'TENANT-BROWSER',
  permissions: ['legal:read'],
  mfaRegistered: true,
};

const workspaceBootstrap = ({
  tenantId = 'TENANT-BROWSER',
  businessRole = 'tenant_auditor',
  legalPermissions,
  firstName = 'Canonical',
  lastName = 'Principal',
} = {}) => ({
  data: {
    status: 'READY',
    user: {
      id: 'WILSYAUTH-browser-user',
      email: 'person@example.com',
      firstName,
      lastName,
    },
    workspace: {
      tenantId,
      businessRole,
      membershipRevision: 7,
      businessRoleRevision: 11,
      ...(legalPermissions === undefined ? {} : { legalPermissions }),
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
    delete api.defaults.headers.common.Authorization;
    delete api.defaults.headers.common['x-tenant-id'];
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
    const promotedUser = JSON.parse(
      window.localStorage.getItem('wilsy_sovereign_user'),
    );
    expect(promotedUser.firstName).toBe('Canonical');
    expect(promotedUser.lastName).toBe('Principal');
    expect(promotedUser.firstName).not.toBe('FORGED LOGIN FIRST');
    expect(promotedUser.lastName).not.toBe('FORGED LOGIN LAST');
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

  it('restores a persisted session only after server workspace revalidation', async () => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify({
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    }));
    window.localStorage.setItem('wilsy_sovereign_user', JSON.stringify({
      id: 'WILSYAUTH-browser-user',
      email: 'person@example.com',
      firstName: 'FORGED STORED FIRST',
      lastName: 'FORGED STORED LAST',
      tenantId: 'TENANT-BROWSER',
      role: 'forged-browser-role',
      permissions: ['*'],
      mfaRegistered: true,
    }));
    api.get.mockResolvedValueOnce(workspaceBootstrap({
      businessRole: 'tenant_legal_partner',
      legalPermissions: [
        'legal_operations:instruction:write',
        'legal_operations:return:write',
      ],
    }));

    renderHarness();

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    expect(api.get).toHaveBeenCalledWith(
      '/auth/workspace-bootstrap',
      {
        headers: {
          Authorization: 'Bearer stored-token',
        },
      },
    );
    expect(api.defaults.headers.common.Authorization).toBe('Bearer stored-token');
    expect(screen.getByTestId('role')).toHaveTextContent('tenant_legal_partner');
    expect(screen.getByTestId('tenant-id')).toHaveTextContent('TENANT-BROWSER');

    const persistedUser = JSON.parse(
      window.localStorage.getItem('wilsy_sovereign_user'),
    );
    expect(persistedUser).toMatchObject({
      id: 'WILSYAUTH-browser-user',
      firstName: 'Canonical',
      lastName: 'Principal',
      tenantId: 'TENANT-BROWSER',
      role: 'tenant_legal_partner',
    });
    expect(persistedUser.firstName).not.toBe('FORGED STORED FIRST');
    expect(persistedUser.lastName).not.toBe('FORGED STORED LAST');
    expect(persistedUser.permissions).toEqual([
      'legal_operations:instruction:write',
      'legal_operations:return:write',
    ]);
    expect(persistedUser.legalPermissionsAuthoritative).toBe(true);
  });

  it('preserves an authoritative empty Legal permission projection distinctly from absence', async () => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify({
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    }));
    api.get.mockResolvedValueOnce(workspaceBootstrap({
      businessRole: 'tenant_legal_partner',
      legalPermissions: [],
    }));

    renderHarness();

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    const persistedUser = JSON.parse(
      window.localStorage.getItem('wilsy_sovereign_user'),
    );
    expect(persistedUser.permissions).toEqual([]);
    expect(persistedUser.legalPermissionsAuthoritative).toBe(true);
  });

  it('preserves legacy compatibility provenance when Legal permissions are absent', async () => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify({
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    }));
    api.get.mockResolvedValueOnce(workspaceBootstrap({
      businessRole: 'tenant_legal_partner',
    }));

    renderHarness();

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    const persistedUser = JSON.parse(
      window.localStorage.getItem('wilsy_sovereign_user'),
    );
    expect(persistedUser.permissions).toEqual([]);
    expect(persistedUser.legalPermissionsAuthoritative).toBe(false);
  });

  it('preserves explicit null optional names without inventing identity text', async () => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify({
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    }));
    api.get.mockResolvedValueOnce(workspaceBootstrap({
      firstName: null,
      lastName: null,
    }));

    renderHarness();

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    const persistedUser = JSON.parse(
      window.localStorage.getItem('wilsy_sovereign_user'),
    );
    expect(persistedUser.firstName).toBeNull();
    expect(persistedUser.lastName).toBeNull();
    expect(JSON.stringify(persistedUser)).not.toContain('person');
  });

  it.each([
    {
      label: 'whitespace-mutated first name',
      bootstrap: workspaceBootstrap({ firstName: ' Canonical ' }),
    },
    {
      label: 'empty last name',
      bootstrap: workspaceBootstrap({ lastName: '' }),
    },
    {
      label: 'non-string first name',
      bootstrap: workspaceBootstrap({ firstName: 42 }),
    },
  ])('fails session promotion closed for $label', async ({ bootstrap }) => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify({
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    }));
    api.get.mockResolvedValueOnce(bootstrap);

    renderHarness();

    await waitFor(() => {
      expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE);
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(window.localStorage.getItem('wilsy_sovereign_user')).toBeNull();
  });

  it.each([
    {
      label: 'unknown permission',
      legalPermissions: ['legal_operations:unknown:write'],
    },
    {
      label: 'duplicate permission',
      legalPermissions: [
        'legal_operations:instruction:write',
        'legal_operations:instruction:write',
      ],
    },
    {
      label: 'non-array permission projection',
      legalPermissions: 'legal_operations:instruction:write',
    },
  ])('fails session promotion closed for $label', async ({ legalPermissions }) => {
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify({
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    }));
    api.get.mockResolvedValueOnce(workspaceBootstrap({
      businessRole: 'tenant_legal_partner',
      legalPermissions,
    }));

    renderHarness();

    await waitFor(() => {
      expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE);
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(window.localStorage.getItem('wilsy_sovereign_user')).toBeNull();
  });

  it('purges a mismatched restored identity but retains discovered tenant context', async () => {
    const discovered = {
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    };
    window.localStorage.setItem('wilsy_auth_token', 'stored-token');
    window.localStorage.setItem('token', 'stored-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify(discovered));
    window.localStorage.setItem('wilsy_active_tenant', JSON.stringify(discovered));
    window.localStorage.setItem('wilsy_sovereign_user', JSON.stringify({
      id: 'forged-browser-user',
      email: 'forged@example.com',
      tenantId: 'TENANT-BROWSER',
      role: 'OWNER',
      permissions: ['*'],
      mfaRegistered: true,
    }));
    api.get.mockResolvedValueOnce(workspaceBootstrap());

    renderHarness();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE);
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(window.localStorage.getItem('token')).toBeNull();
    expect(window.localStorage.getItem('wilsy_sovereign_user')).toBeNull();
    expect(window.localStorage.getItem('wilsy_active_tenant')).toBeNull();
    expect(JSON.parse(window.localStorage.getItem('discoveredTenant'))).toEqual(discovered);
    expect(screen.getByTestId('tenant-id')).toHaveTextContent('TENANT-BROWSER');
    expect(api.defaults.headers.common.Authorization).toBeUndefined();
  });

  it('retains discovered tenant navigation context when persisted bearer is rejected', async () => {
    const discovered = {
      tenantId: 'TENANT-BROWSER',
      alias: 'browser',
      name: 'Browser Tenant',
    };
    window.localStorage.setItem('wilsy_auth_token', 'expired-token');
    window.localStorage.setItem('discoveredTenant', JSON.stringify(discovered));
    api.get.mockRejectedValueOnce({
      response: { status: 401, data: { detail: 'Invalid authentication credentials.' } },
    });

    renderHarness();

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE);
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    expect(JSON.parse(window.localStorage.getItem('discoveredTenant'))).toEqual(discovered);
    expect(screen.getByTestId('tenant-id')).toHaveTextContent('TENANT-BROWSER');
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
 * VERSION: v1.4.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION-CERT
 * AUTHORITY BOUNDARY: deterministic browser projection certificate only; workspace principal names are descriptive identity and Legal permission provenance is presentation-only; neither is authorization authority
 * CHANGELOG: v1.4.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION-CERT — Added server-only person-name projection, anti-login/persisted-name authority proofs, explicit null-name preservation, and malformed-name fail-closed evidence.
 *            v1.3.0-D17-SERVER-LEGAL-PERMISSION-PROJECTION-CERT — Added exact, empty, absent and malformed Legal
 * permission-projection evidence while retaining anti-JWT/browser-authority proofs.
 *            v1.2.0-SERVER-REVALIDATED-SESSION-RESTORE-CERT — Added valid restore, principal-mismatch denial,
 * rejected-bearer purge, discovered-tenant continuity, canonical bearer restoration
 * and server projection evidence.
 * TENANT POSTURE: authenticated tenant must match the discovered server-issued tenant
 * FAIL-CLOSED POSTURE: session exists only after bounded authenticated response; malformed/duplicate/unknown Legal permission projections prevent promotion
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
