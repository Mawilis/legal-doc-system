/**
 * WILSY OS — RECOVERY CONTACT SECURITY BROWSER CERTIFICATE
 * VERSION: v1.0.0-R10E32-RECOVERY-CONTACT-SECURITY-BROWSER-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies authenticated recovery-email possession verification and
 * protected route/account-security reachability without browser-owned authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/RecoveryContactSecurityPortal.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * AUTHORITY BOUNDARY: deterministic browser presentation and signed API invocation only
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import RecoveryContactSecurityPortal from '../../../src/components/auth/RecoveryContactSecurityPortal.jsx';

const navigate = vi.fn();
const requestRecoveryContactVerification = vi.fn();
const completeRecoveryContactVerification = vi.fn();

const tenant = {
  tenantId: 'TENANT-R10E32',
  alias: 'wilsy',
  name: 'wilsy',
  legalName: 'Wilsy (Pty) Ltd',
  verified: true,
};

vi.mock('../../../src/contexts/authContext.jsx', () => ({
  useAuth: () => ({
    user: { id: 'PRINCIPAL-R10E32', email: 'login@example.com' },
    tenant,
  }),
}));

vi.mock('../../../src/services/api.js', () => ({
  requestRecoveryContactVerification,
  completeRecoveryContactVerification,
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigate,
  };
});

const HERE = path.dirname(fileURLToPath(import.meta.url));
const APP_SOURCE = path.resolve(HERE, '../../../src/App.jsx');
const ACCOUNT_SOURCE = path.resolve(HERE, '../../../src/components/account/WilsyAccountCommandCenter.jsx');

describe('R10E32 recovery contact security browser certificate', () => {
  beforeEach(() => {
    navigate.mockReset();
    requestRecoveryContactVerification.mockReset();
    completeRecoveryContactVerification.mockReset();
  });

  it('proposes an address without browser tenant/principal authority and advances only on 202', async () => {
    requestRecoveryContactVerification.mockResolvedValueOnce({
      status: 202,
      data: undefined,
      headers: {},
    });

    render(
      <MemoryRouter>
        <RecoveryContactSecurityPortal />
      </MemoryRouter>,
    );

    expect(screen.getByText('Wilsy (Pty) Ltd')).toBeInTheDocument();
    expect(screen.getByLabelText('Recovery email')).toHaveValue('login@example.com');
    expect(screen.queryByLabelText(/tenant/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/principal/i)).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Recovery email'), {
      target: { value: ' recovery@example.com ' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Verify recovery email' }));

    await waitFor(() => {
      expect(requestRecoveryContactVerification).toHaveBeenCalledWith({
        address: 'recovery@example.com',
      });
    });
    expect(screen.getByLabelText('Verification value')).toBeInTheDocument();
    expect(completeRecoveryContactVerification).not.toHaveBeenCalled();
  });

  it('projects VERIFIED success only after exact bodyless 204 completion', async () => {
    requestRecoveryContactVerification.mockResolvedValueOnce({ status: 202 });
    completeRecoveryContactVerification.mockResolvedValueOnce({ status: 204 });

    render(
      <MemoryRouter>
        <RecoveryContactSecurityPortal />
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Verify recovery email' }));
    await screen.findByLabelText('Verification value');

    fireEvent.change(screen.getByLabelText('Verification value'), {
      target: { value: ' R10E32-one-time-verification-value-0123456789 ' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Confirm recovery email' }));

    await waitFor(() => {
      expect(completeRecoveryContactVerification).toHaveBeenCalledWith({
        verificationToken: 'R10E32-one-time-verification-value-0123456789',
      });
    });
    expect(await screen.findByText('Recovery contact verified')).toBeInTheDocument();
    expect(screen.queryByLabelText('Verification value')).not.toBeInTheDocument();
  });

  it('keeps replacement refusal explicit without claiming browser verification', async () => {
    requestRecoveryContactVerification.mockRejectedValueOnce({
      response: { status: 409 },
    });

    render(
      <MemoryRouter>
        <RecoveryContactSecurityPortal />
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Verify recovery email' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'A verified recovery contact is already bound',
    );
    expect(screen.queryByText('Recovery contact verified')).not.toBeInTheDocument();
  });

  it('is protected in App and reachable from both Account Security presentations', () => {
    const appSource = fs.readFileSync(APP_SOURCE, 'utf8');
    const accountSource = fs.readFileSync(ACCOUNT_SOURCE, 'utf8');

    expect(appSource).toContain('path="/account/recovery-contact"');
    expect(appSource).toContain('isAuthenticated && user');
    expect(appSource).not.toContain("location.pathname === '/account/recovery-contact'");
    expect(accountSource.match(/open_recovery_contact_security/g)).toHaveLength(2);
    expect(accountSource.match(/\/account\/recovery-contact/g)).toHaveLength(2);
  });

  it('does not persist or log address/challenge values in the component source', () => {
    const source = RecoveryContactSecurityPortal.toString();
    expect(source).not.toMatch(/localStorage|sessionStorage|console\.|document\.cookie/i);
    expect(source).not.toMatch(/tenant_id|principal_id|verified\s*:/i);
  });
});

/**
 * ARTIFACT: client/tests/components/auth/RecoveryContactSecurityPortal.test.jsx
 * VERSION: v1.0.0-R10E32-RECOVERY-CONTACT-SECURITY-BROWSER-CERT
 * AUTHORITY BOUNDARY: authenticated browser possession-verification evidence only
 * TENANT POSTURE: tenant/principal derive from protected server identity
 * FAIL-CLOSED POSTURE: only HTTP 204 projects VERIFIED success
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
