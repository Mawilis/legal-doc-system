/**
 * WILSY OS — PASSWORD RECOVERY CLIENT FLOW CERTIFICATE
 * VERSION: v1.0.0-R10E56-PASSWORD-RECOVERY-CLIENT-FLOW-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies the browser projection from recovery request through
 *          verification-link confirmation and reset-link completion, including
 *          immediate fragment secret scrubbing and no automatic login.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/PasswordRecoveryClientFlow.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises PasswordRecoveryRequestPortal,
 *                            RecoveryContactVerificationPortal, and
 *                            PasswordResetPortal with mocked transport only.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E56-PASSWORD-RECOVERY-CLIENT-FLOW-CERT — Adds direct client-flow evidence for generic 202
 *            recovery acknowledgement, explicit verification confirmation,
 *            fragment secret removal, exact capability transport, bodyless-204
 *            reset success, and absence of automatic authenticated navigation.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic tokens/passwords only; URL fragments are
 *                             asserted scrubbed before human confirmation.
 * TENANT BOUNDARY: Fragment and workspace tenant values remain lookup selectors;
 *                  no browser value grants tenant or principal authority.
 * AUTHORITY BOUNDARY: Client presentation and mocked transport evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
  navigate,
  authState,
  requestPasswordRecovery,
  completeRecoveryContactVerification,
  resetPassword,
} = vi.hoisted(() => ({
  navigate: vi.fn(),
  authState: { tenant: null },
  requestPasswordRecovery: vi.fn(),
  completeRecoveryContactVerification: vi.fn(),
  resetPassword: vi.fn(),
}));

vi.mock('../../../src/contexts/authContext.jsx', () => ({
  useAuth: () => ({ tenant: authState.tenant }),
}));

vi.mock('../../../src/services/api.js', () => ({
  requestPasswordRecovery,
  completeRecoveryContactVerification,
  resetPassword,
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigate,
  };
});

vi.mock('../../../src/components/auth/TenantIdentityCard.jsx', () => ({
  default: ({ tenant }) => (
    <div data-testid="tenant-identity-projection">
      {tenant?.legalName || tenant?.name || tenant?.tenantId || 'workspace'}
    </div>
  ),
}));

import PasswordRecoveryRequestPortal from '../../../src/components/auth/PasswordRecoveryRequestPortal.jsx';
import RecoveryContactVerificationPortal from '../../../src/components/auth/RecoveryContactVerificationPortal.jsx';
import PasswordResetPortal from '../../../src/components/auth/PasswordResetPortal.jsx';

const TENANT = Object.freeze({
  tenantId: 'TENANT-R10E56',
  legalName: 'Synthetic Recovery Institution',
  name: 'synthetic',
  alias: 'synthetic',
  verified: true,
});

describe('R10E56 password recovery client flow certificate', () => {
  beforeEach(() => {
    navigate.mockReset();
    requestPasswordRecovery.mockReset();
    completeRecoveryContactVerification.mockReset();
    resetPassword.mockReset();
    authState.tenant = null;
  });

  it('submits selected workspace and email but always renders generic recovery acknowledgement', async () => {
    requestPasswordRecovery.mockResolvedValue({
      status: 202,
      data: { status: 'RECOVERY_REQUEST_ACCEPTED' },
    });

    render(
      <MemoryRouter initialEntries={[{
        pathname: '/forgot-password',
        state: { tenant: TENANT, email: 'member@example.test' },
      }]}>
        <PasswordRecoveryRequestPortal />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('tenant-identity-projection')).toHaveTextContent(
      'Synthetic Recovery Institution',
    );
    expect(screen.getByLabelText(/work email/i)).toHaveValue('member@example.test');
    expect(screen.queryByLabelText(/recovery information/i)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /send recovery instructions/i }));

    await waitFor(() => expect(requestPasswordRecovery).toHaveBeenCalledWith({
      tenantId: TENANT.tenantId,
      email: 'member@example.test',
    }));
    expect(await screen.findByRole('status')).toHaveTextContent(
      'If recovery is available for this account, secure instructions will be sent.',
    );
    expect(screen.queryByText(/account exists|contact exists|verified contact found/i)).not.toBeInTheDocument();
  });

  it('scrubs verification capability from the address bar before explicit completion', async () => {
    completeRecoveryContactVerification.mockResolvedValue({ status: 204, data: undefined });
    const replaceSpy = vi.spyOn(window.history, 'replaceState');

    render(
      <MemoryRouter initialEntries={[
        '/verify-recovery-contact#tenant=TENANT-R10E56&verification=verify-secret-r10e59',
      ]}>
        <RecoveryContactVerificationPortal />
      </MemoryRouter>,
    );

    await waitFor(() => expect(replaceSpy).toHaveBeenCalledWith(
      window.history.state,
      '',
      '/verify-recovery-contact',
    ));
    expect(screen.getByText(/capability has been removed from the address bar/i)).toBeInTheDocument();
    expect(screen.queryByText('verify-secret-r10e59')).not.toBeInTheDocument();
    expect(completeRecoveryContactVerification).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /^verify recovery email$/i }));

    await waitFor(() => expect(completeRecoveryContactVerification).toHaveBeenCalledWith({
      tenantId: 'TENANT-R10E56',
      verificationToken: 'verify-secret-r10e59',
    }));
    expect(await screen.findByRole('status')).toHaveTextContent('Recovery email verified');
    expect(navigate).not.toHaveBeenCalled();

    replaceSpy.mockRestore();
  });

  it('rejects incomplete verification links without invoking verification transport', () => {
    render(
      <MemoryRouter initialEntries={['/verify-recovery-contact#tenant=TENANT-R10E56']}>
        <RecoveryContactVerificationPortal />
      </MemoryRouter>,
    );

    expect(screen.getByRole('alert')).toHaveTextContent('verification link is incomplete');
    expect(screen.getByRole('button', { name: /verify recovery email/i })).toBeDisabled();
    expect(completeRecoveryContactVerification).not.toHaveBeenCalled();
  });

  it('scrubs reset capability, hides manual recovery input, and submits the exact link capability', async () => {
    resetPassword.mockResolvedValue({ status: 204, data: undefined });
    const replaceSpy = vi.spyOn(window.history, 'replaceState');

    render(
      <MemoryRouter initialEntries={[
        '/reset-password#tenant=TENANT-R10E56&recovery=reset-secret-r10e59',
      ]}>
        <PasswordResetPortal />
      </MemoryRouter>,
    );

    await waitFor(() => expect(replaceSpy).toHaveBeenCalledWith(
      window.history.state,
      '',
      '/reset-password',
    ));
    expect(screen.getByText(/secure recovery link loaded/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/recovery information/i)).not.toBeInTheDocument();
    expect(screen.queryByText('reset-secret-r10e59')).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'synthetic strong password 12345' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'synthetic strong password 12345' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^reset password$/i }));

    await waitFor(() => expect(resetPassword).toHaveBeenCalledWith({
      tenantId: 'TENANT-R10E56',
      recoveryToken: 'reset-secret-r10e59',
      newPassword: 'synthetic strong password 12345',
    }));
    expect(await screen.findByRole('status')).toHaveTextContent('Password reset complete');
    expect(navigate).not.toHaveBeenCalled();

    replaceSpy.mockRestore();
  });

  it('keeps password confirmation local and blocks mismatches before transport', async () => {
    render(
      <MemoryRouter initialEntries={[
        '/reset-password#tenant=TENANT-R10E56&recovery=reset-secret-r10e59',
      ]}>
        <PasswordResetPortal />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'first synthetic password 123' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'different synthetic password 456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^reset password$/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('password confirmation does not match');
    expect(resetPassword).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: PasswordRecoveryClientFlow.test.jsx
 * VERSION: v1.0.0-R10E56-PASSWORD-RECOVERY-CLIENT-FLOW-CERT
 * AUTHORITY BOUNDARY: deterministic browser projection and mocked transport evidence only
 * TENANT POSTURE: workspace/fragment tenant values remain lookup selectors only
 * FAIL-CLOSED POSTURE: missing/mismatched capability inputs cannot create verified contact or reset
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
