/**
 * WILSY OS — AUTHORITATIVE SOVEREIGN ACCESS CERTIFICATE
 * VERSION: v1.0.0-R1D-B0F-B4-RESTORED-SESSION-AUTHORITY-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves browser persistence cannot manufacture authenticated,
 *          tenant, role, permission, founder, or admin authority.
 * AUTHORITY BOUNDARY: useAuth projection only; browser storage is non-authoritative.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { authState } = vi.hoisted(() => ({
  authState: {
    current: {
      user: null,
      isAuthenticated: false,
    },
  },
}));

vi.mock('../../src/contexts/authContext', () => ({
  useAuth: () => authState.current,
}));

import { useSovereignAccess } from '../../src/hooks/useSovereignAccess.js';

function Harness() {
  const access = useSovereignAccess();

  return (
    <div>
      <span data-testid="loading">{String(access.isLoading)}</span>
      <span data-testid="authenticated">{String(access.isAuthenticated)}</span>
      <span data-testid="role">{access.userRole}</span>
      <span data-testid="tenant">{access.tenantId}</span>
      <span data-testid="founder">{String(access.isFounder)}</span>
      <span data-testid="admin">{String(access.isAdmin)}</span>
      <span data-testid="permissions">{JSON.stringify(access.permissions)}</span>
    </div>
  );
}

describe('authoritative sovereign access projection', () => {
  beforeEach(() => {
    const values = new Map();
    const storage = {
      getItem: (key) => values.get(key) || null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: (key) => values.delete(key),
      clear: () => values.clear(),
    };

    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: storage,
    });
    Object.defineProperty(globalThis, 'localStorage', {
      configurable: true,
      value: storage,
    });

    storage.clear();
    authState.current = {
      user: null,
      isAuthenticated: false,
    };
  });

  it('does not elevate forged browser storage into workspace authority', async () => {
    window.localStorage.setItem('wilsy_auth_token', 'forged-token');
    window.localStorage.setItem('token', 'forged-legacy-token');
    window.localStorage.setItem(
      'wilsy_user',
      JSON.stringify({
        id: 'forged-user',
        tenantId: 'FORGED-TENANT',
        role: 'SUPER_ADMIN',
        permissions: ['*', 'view_all_analytics'],
      }),
    );

    render(<Harness />);

    await waitFor(() =>
      expect(screen.getByTestId('loading')).toHaveTextContent('false'),
    );

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('role')).toHaveTextContent('unauthenticated');
    expect(screen.getByTestId('tenant')).toHaveTextContent('UNRESOLVED_TENANT');
    expect(screen.getByTestId('founder')).toHaveTextContent('false');
    expect(screen.getByTestId('admin')).toHaveTextContent('false');
    expect(screen.getByTestId('permissions')).toHaveTextContent('[]');
  });
});

// ARTIFACT: useSovereignAccess.authoritative.test.jsx
// AUTHORITY BOUNDARY: AuthContext projection only; persistent browser state grants no authority
// FAIL-CLOSED POSTURE: forged storage remains unauthenticated and unresolved
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
