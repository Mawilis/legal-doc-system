/**
 * WILSY OS — RECOVERY CONTACT CLIENT CERTIFICATE
 * VERSION: v1.0.1-R10E56-RECOVERY-CONTACT-CLIENT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies the authenticated recovery-email security control and its
 *          reachable account-security mounts without granting browser email,
 *          tenant, principal, token, or verified-contact authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/account/RecoveryContactSecurityControl.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises RecoveryContactSecurityControl and
 *                            statically certifies its Account Command Center
 *                            desktop/mobile mount contract.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.1-R10E56-RECOVERY-CONTACT-CLIENT-CERT — Reconciles the recovery campaign gate sequence after
 *            the branch had already advanced through R10E54; certificate
 *            behavior is unchanged from the immediately prior client evidence.
 *            v1.0.0-R10E38-RECOVERY-CONTACT-CLIENT-CERT — Adds direct client evidence for request semantics,
 *            pending suppression, bounded success/failure states, zero-argument
 *            authenticated transport, and two reachable account-security mounts.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic email only; no network, token, password,
 *                             SMTP credential, or durable contact mutation.
 * TENANT BOUNDARY: The mocked client request accepts no tenant/email payload;
 *                  Python EOS re-reads authenticated durable identity.
 * AUTHORITY BOUNDARY: Deterministic client presentation/transport evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { readFileSync } from 'node:fs';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import RecoveryContactSecurityControl from '../../../src/components/account/RecoveryContactSecurityControl.jsx';
import { requestRecoveryContactVerification } from '../../../src/services/api.js';

vi.mock('../../../src/services/api.js', () => ({
  requestRecoveryContactVerification: vi.fn(),
}));

const requestVerification = vi.mocked(requestRecoveryContactVerification);

describe('authenticated recovery contact security control', () => {
  beforeEach(() => {
    requestVerification.mockReset();
  });

  it('requests server-derived current-email verification without browser authority', async () => {
    requestVerification.mockResolvedValue({
      status: 202,
      data: { status: 'VERIFICATION_SENT' },
    });

    render(<RecoveryContactSecurityControl email="member@example.test" />);

    expect(screen.getByText('member@example.test')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /verify recovery email/i }));

    await waitFor(() => expect(requestVerification).toHaveBeenCalledTimes(1));
    expect(requestVerification).toHaveBeenCalledWith();
    expect(await screen.findByText(/verification sent/i)).toBeInTheDocument();
  });

  it('suppresses duplicate submissions while one verification request is pending', async () => {
    let resolveRequest;
    requestVerification.mockImplementation(() => new Promise((resolve) => {
      resolveRequest = resolve;
    }));

    render(<RecoveryContactSecurityControl email="member@example.test" />);
    const button = screen.getByRole('button', { name: /verify recovery email/i });

    fireEvent.click(button);
    fireEvent.click(button);

    expect(requestVerification).toHaveBeenCalledTimes(1);
    expect(button).toBeDisabled();

    resolveRequest({ status: 202, data: { status: 'VERIFICATION_SENT' } });
    expect(await screen.findByText(/verification sent/i)).toBeInTheDocument();
  });

  it('renders an already-verified result without inventing local verified state', async () => {
    requestVerification.mockResolvedValue({
      status: 202,
      data: { status: 'VERIFICATION_NOT_REQUIRED' },
    });

    render(<RecoveryContactSecurityControl email="member@example.test" />);
    fireEvent.click(screen.getByRole('button', { name: /verify recovery email/i }));

    expect(await screen.findByText(/already verified/i)).toBeInTheDocument();
    expect(requestVerification).toHaveBeenCalledWith();
  });

  it.each([
    [429, 'Verification requests are temporarily rate-limited.'],
    [401, 'Sign in again before managing recovery security.'],
    [403, 'Sign in again before managing recovery security.'],
    [503, 'Recovery-email verification is temporarily unavailable.'],
  ])('maps HTTP %s to bounded client copy', async (status, expected) => {
    requestVerification.mockRejectedValue({ response: { status } });

    render(<RecoveryContactSecurityControl email="member@example.test" />);
    fireEvent.click(screen.getByRole('button', { name: /verify recovery email/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(expected);
    expect(requestVerification).toHaveBeenCalledTimes(1);
  });

  it('is mounted in both mobile and desktop Account Command Center security surfaces', () => {
    const source = readFileSync(
      new URL('../../../src/components/account/WilsyAccountCommandCenter.jsx', import.meta.url),
      'utf8',
    );

    expect(source.match(/<RecoveryContactSecurityControl/g)).toHaveLength(2);
    expect(source.match(/email=\{user\?\.email \|\| ''\}/g)).toHaveLength(2);
    expect(source).toContain('<RecoveryContactSecurityControl email={user?.email || \'\'} compact />');
    expect(source).toContain('<RecoveryContactSecurityControl email={user?.email || \'\'} />');
    expect(source).not.toContain('RecoveryContactSecurityControl tenantId=');
    expect(source).not.toContain('RecoveryContactSecurityControl principalId=');
  });
});

/**
 * ARTIFACT: RecoveryContactSecurityControl.test.jsx
 * VERSION: v1.0.1-R10E56-RECOVERY-CONTACT-CLIENT-CERT
 * AUTHORITY BOUNDARY: deterministic recovery client presentation/transport evidence only
 * TENANT POSTURE: no browser-supplied tenant/email/recovery-contact authority
 * FAIL-CLOSED POSTURE: unexpected server outcomes render bounded unavailable copy
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
