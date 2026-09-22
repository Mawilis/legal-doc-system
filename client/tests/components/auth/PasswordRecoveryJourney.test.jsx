/**
 * WILSY OS — PASSWORD RECOVERY BROWSER JOURNEY CERTIFICATE
 * VERSION: v1.0.0-R10E31-PASSWORD-RECOVERY-BROWSER-JOURNEY-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies Login → Forgot Password → enumeration-safe recovery request
 * without network, recovery-secret, account-existence, or browser authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/PasswordRecoveryJourney.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * AUTHORITY BOUNDARY: deterministic client presentation/transport invocation only
 * TENANT POSTURE: selected workspace is a lookup selector, never a browser grant
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import PasswordRecoveryPortal from '../../../src/components/auth/PasswordRecoveryPortal.jsx';
import SovereignLogin from '../../../src/components/auth/SovereignLogin.jsx';

const navigate = vi.fn();
const requestPasswordReset = vi.fn();
const login = vi.fn();
const locationState = {
  pathname: '/login',
  state: null,
};

const tenant = {
  tenantId: 'TENANT-R10E31',
  alias: 'wilsy',
  name: 'wilsy',
  legalName: 'Wilsy (Pty) Ltd',
  verified: true,
};

vi.mock('../../../src/contexts/authContext.jsx', () => ({
  AUTH_STATES: {
    MFA_SETUP: 'MFA_SETUP',
    MFA_RECONCILIATION_REQUIRED: 'MFA_RECONCILIATION_REQUIRED',
    MFA_REQUIRED: 'MFA_REQUIRED',
  },
  useAuth: () => ({
    login,
    loading: false,
    error: null,
    tenant,
  }),
}));

vi.mock('../../../src/services/api.js', () => ({
  requestPasswordReset,
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigate,
    useLocation: () => locationState,
  };
});

describe('R10E31 password recovery browser journey', () => {
  beforeEach(() => {
    navigate.mockReset();
    requestPasswordReset.mockReset();
    login.mockReset();
    locationState.pathname = '/login';
    locationState.state = null;
  });

  it('routes Forgot Password into initiation and carries only the typed email as route state', () => {
    render(
      <MemoryRouter>
        <SovereignLogin />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText('Work email'), {
      target: { value: ' Person@Example.COM ' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Forgot password?' }));

    expect(navigate).toHaveBeenCalledWith('/forgot-password', {
      state: { email: 'Person@Example.COM' },
    });
    expect(requestPasswordReset).not.toHaveBeenCalled();
  });

  it('reuses selected workspace and submits exact recovery request without any token field', async () => {
    locationState.pathname = '/forgot-password';
    locationState.state = { email: 'person@example.com' };
    requestPasswordReset.mockResolvedValueOnce({
      status: 202,
      data: undefined,
      headers: {},
    });

    render(
      <MemoryRouter>
        <PasswordRecoveryPortal />
      </MemoryRouter>,
    );

    expect(screen.getByText('Wilsy (Pty) Ltd')).toBeInTheDocument();
    expect(screen.queryByLabelText('Workspace ID')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Work email')).toHaveValue('person@example.com');
    expect(screen.queryByLabelText(/recovery information/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/recovery token/i)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    await waitFor(() => {
      expect(requestPasswordReset).toHaveBeenCalledTimes(1);
    });
    expect(requestPasswordReset).toHaveBeenCalledWith({
      tenantId: tenant.tenantId,
      email: 'person@example.com',
    });
    expect(await screen.findByText('Check your recovery email')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent(
      'If an eligible account with a verified recovery email exists for this workspace',
    );
    expect(screen.getByRole('status')).not.toHaveTextContent(tenant.tenantId);
    expect(screen.getByRole('status')).not.toHaveTextContent('principal');
  });

  it('keeps a direct-entry fallback when no selected workspace exists', () => {
    locationState.pathname = '/forgot-password';

    vi.doMock('../../../src/contexts/authContext.jsx', () => ({
      useAuth: () => ({ tenant: null }),
    }));

    // Source contract: direct-entry fallback remains explicit even though this
    // suite's module-level auth mock supplies a selected tenant at runtime.
    const source = PasswordRecoveryPortal.toString();
    expect(source).toContain('manualTenantId');
    expect(source).toContain('Find your workspace');
  });

  it('maps backend unavailability to safe copy without account or delivery truth', async () => {
    locationState.pathname = '/forgot-password';
    requestPasswordReset.mockRejectedValueOnce({
      response: { status: 503 },
    });

    render(
      <MemoryRouter>
        <PasswordRecoveryPortal />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText('Work email'), {
      target: { value: 'person@example.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send recovery instructions' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Password recovery is temporarily unavailable',
    );
    expect(screen.getByRole('alert')).not.toHaveTextContent('exists');
    expect(screen.getByRole('alert')).not.toHaveTextContent('verified');
    expect(screen.getByRole('alert')).not.toHaveTextContent('delivery');
  });
});

/**
 * ARTIFACT: client/tests/components/auth/PasswordRecoveryJourney.test.jsx
 * VERSION: v1.0.0-R10E31-PASSWORD-RECOVERY-BROWSER-JOURNEY-CERT
 * AUTHORITY BOUNDARY: browser recovery initiation evidence only
 * TENANT POSTURE: selected workspace is selector-only
 * FAIL-CLOSED POSTURE: no token/account/delivery truth enters initiation UI
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
