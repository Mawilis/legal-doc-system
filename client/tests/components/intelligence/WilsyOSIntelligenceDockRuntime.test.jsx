/**
 * TITLE: Intelligence Dock Authentication Mount Certificate
 * VERSION: v1.0.0-AUTHENTICATED-MOUNT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves protected Intelligence Dock runtime is absent before a
 *          bounded authenticated session and responds to logout immediately.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/intelligence/WilsyOSIntelligenceDockRuntime.test.jsx
 * COLLABORATION / OWNERSHIP: Dock runtime gate, AuthProvider event bus, and App root.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.0.0-AUTHENTICATED-MOUNT-CERT — Initial focused certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic browser storage only; no protected calls.
 * TENANT BOUNDARY: Mount requires a server-projected user tenantId.
 * AUTHORITY BOUNDARY: Runtime composition only; no identity is created.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../../src/components/intelligence/WilsyOSIntelligenceDock.jsx', () => ({
  default: () => <div data-testid="dock">WILSY OS Intelligence Dock</div>,
}));

import WilsyOSIntelligenceDockRuntime from '../../../src/components/intelligence/WilsyOSIntelligenceDockRuntime.jsx';

const installStorage = () => {
  const values = new Map();
  const storage = {
    getItem: (key) => values.get(key) || null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
    clear: () => values.clear(),
  };
  Object.defineProperty(window, 'localStorage', { configurable: true, value: storage });
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
  return storage;
};

describe('authenticated Intelligence Dock mount gate', () => {
  let storage;

  beforeEach(() => {
    storage = installStorage();
    storage.clear();
    window.history.replaceState({}, '', '/discovery');
  });

  it('does not mount protected Dock before authentication or on auth routes', () => {
    render(<WilsyOSIntelligenceDockRuntime />);
    expect(screen.queryByTestId('dock')).toBeNull();
  });

  it('ignores forged persistent storage and mounts only from explicit authoritative runtime projection', async () => {
    window.history.replaceState({}, '', '/dashboard');

    storage.setItem('wilsy_auth_token', 'forged-stored-token');
    storage.setItem(
      'wilsy_sovereign_user',
      JSON.stringify({
        id: 'forged-user',
        tenantId: 'FORGED-TENANT',
        role: 'SUPER_ADMIN',
        permissions: ['*'],
      }),
    );

    const { rerender } = render(<WilsyOSIntelligenceDockRuntime />);

    fireEvent(
      window,
      new CustomEvent('wilsy-auth-state', { detail: 'AUTHENTICATED' }),
    );

    await waitFor(() => expect(screen.queryByTestId('dock')).toBeNull());

    rerender(
      <WilsyOSIntelligenceDockRuntime
        authenticated
        authUser={{ id: 'user-1', tenantId: 'tenant-1' }}
        activeTenant={{ tenantId: 'tenant-1' }}
      />,
    );

    await waitFor(() => expect(screen.getByTestId('dock')).toBeInTheDocument());

    rerender(
      <WilsyOSIntelligenceDockRuntime
        authenticated={false}
        authUser={{ id: 'user-1', tenantId: 'tenant-1' }}
        activeTenant={{ tenantId: 'tenant-1' }}
      />,
    );

    await waitFor(() => expect(screen.queryByTestId('dock')).toBeNull());
  });
});

/**
 * ARTIFACT: client/tests/components/intelligence/WilsyOSIntelligenceDockRuntime.test.jsx
 * VERSION: v1.0.0-AUTHENTICATED-MOUNT-CERT
 * AUTHORITY BOUNDARY: protected runtime mount gate only
 * TENANT POSTURE: server-projected tenant identity required
 * FAIL-CLOSED POSTURE: missing session yields no Dock
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
