/**
 * TITLE: WILSY OS Authenticated Session Restoration Currentness Certificate
 * VERSION: v1.0.0-STRICT-RESTORE-LOGOUT-OWNERSHIP
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Demonstrates one current EOS workspace bootstrap during Strict Mode
 *          and rejects stale responses after logout or a superseding session.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/contexts/authContext.sessionCurrentness.test.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider and Python EOS workspace bootstrap.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-STRICT-RESTORE-LOGOUT-OWNERSHIP validates exact bearer
 *            pending GET coalescing, immediate logout invalidation, and
 *            late post-logout workspace-refresh denial without bypassing MFA.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic bearer and identity only; no secrets.
 * TENANT BOUNDARY: Server fixture binds one canonical synthetic tenant.
 * AUTHORITY BOUNDARY: Tests observe browser projection, never authorize login.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    defaults: { headers: { common: {} } },
  },
}));
vi.mock('@/services/api', () => ({
  default: api,
  setActiveTenantTransportId: vi.fn(),
}));

import { AUTH_STATES, AuthProvider, useAuth } from '../../src/contexts/authContext.jsx';

const id = 'WILSYAUTH-SESSION-CURRENTNESS-TEST';
const tenantId = 'WILSYTENANT-SESSION-CURRENTNESS-TEST';
const bearer = 'synthetic-persisted-session-currentness-token';

const serverWorkspace = () => ({
  data: {
    status: 'READY',
    user: { id, email: 'currentness@example.test', firstName: 'Test', lastName: 'Principal' },
    workspace: {
      tenantId,
      workspaceId: 'WILSY_HEADQUARTERS',
      businessRole: 'tenant_owner',
      workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
      membershipRevision: 3,
      businessRoleRevision: 7,
      branding: null,
      tenant: { tenantId, name: 'Test Organization', legalName: 'Test Organization (Pty) Ltd', status: 'ACTIVE' },
    },
  },
});

const deferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((done, fail) => {
    resolve = done;
    reject = fail;
  });
  return { promise, resolve, reject };
};

function Harness() {
  const auth = useAuth();
  return (
    <main>
      <span data-testid="authentication">{String(auth.isAuthenticated)}</span>
      <span data-testid="stage">{auth.authStage}</span>
      <span data-testid="principal">{auth.user?.id || ''}</span>
      <button type="button" onClick={() => { void auth.logout(); }}>Logout</button>
      <button type="button" onClick={() => { void auth.refreshWorkspace().catch(() => {}); }}>Refresh workspace</button>
    </main>
  );
}

const mount = ({ strict = false } = {}) => {
  const element = <AuthProvider><Harness/></AuthProvider>;
  return render(strict ? <React.StrictMode>{element}</React.StrictMode> : element);
};

beforeEach(() => {
  const store = new Map([
    ['wilsy_auth_token', bearer],
    ['token', bearer],
    ['wilsy_sovereign_user', JSON.stringify({ id, email: 'currentness@example.test' })],
  ]);
  const storage = {
    getItem: (key) => store.get(key) || null,
    setItem: (key, value) => store.set(key, String(value)),
    removeItem: (key) => store.delete(key),
    clear: () => store.clear(),
  };
  Object.defineProperty(window, 'localStorage', { configurable: true, value: storage });
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
  api.get.mockReset();
  api.post.mockReset().mockResolvedValue({ data: { status: 'LOGGED_OUT' } });
  delete api.defaults.headers.common.Authorization;
});

describe('authoritative session restoration currentness', () => {
  it('coalesces one EOS bootstrap read when Strict Mode replays the effect', async () => {
    const pending = deferred();
    api.get.mockReturnValue(pending.promise);
    mount({ strict: true });
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));
    expect(screen.getByTestId('authentication')).toHaveTextContent('false');
    await act(async () => pending.resolve(serverWorkspace()));
    await waitFor(() => expect(screen.getByTestId('authentication')).toHaveTextContent('true'));
    expect(screen.getByTestId('principal')).toHaveTextContent(id);
    expect(api.get).toHaveBeenCalledWith('/auth/workspace-bootstrap', {
      headers: { Authorization: 'Bearer ' + bearer },
    });
  });

  it('never restores a logged-out identity from an older pending response', async () => {
    const pending = deferred();
    api.get.mockReturnValue(pending.promise);
    mount();
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole('button', { name: 'Logout' }));
    expect(screen.getByTestId('authentication')).toHaveTextContent('false');
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    await act(async () => pending.resolve(serverWorkspace()));
    expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE);
    expect(screen.getByTestId('principal')).toHaveTextContent('');
    expect(api.defaults.headers.common.Authorization).toBeUndefined();
  });

  it('rejects a late workspace refresh after the user signs out', async () => {
    const pending = deferred();
    api.get
      .mockResolvedValueOnce(serverWorkspace())
      .mockReturnValueOnce(pending.promise);
    mount();
    await waitFor(() => expect(screen.getByTestId('authentication')).toHaveTextContent('true'));
    fireEvent.click(screen.getByRole('button', { name: 'Refresh workspace' }));
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
    fireEvent.click(screen.getByRole('button', { name: 'Logout' }));
    expect(window.localStorage.getItem('wilsy_auth_token')).toBeNull();
    await act(async () => pending.resolve(serverWorkspace()));
    expect(screen.getByTestId('authentication')).toHaveTextContent('false');
    expect(screen.getByTestId('stage')).toHaveTextContent(AUTH_STATES.IDLE);
    expect(screen.getByTestId('principal')).toHaveTextContent('');
  });
});

/*
 * ARTIFACT: client/tests/contexts/authContext.sessionCurrentness.test.jsx
 * VERSION: v1.0.0-STRICT-RESTORE-LOGOUT-OWNERSHIP
 * AUTHORITY BOUNDARY: Synthetic client integration evidence only.
 * TENANT POSTURE: Exact EOS-like projection and no cross-tenant state.
 * FAIL-CLOSED POSTURE: Stale requests cannot promote a former identity.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
