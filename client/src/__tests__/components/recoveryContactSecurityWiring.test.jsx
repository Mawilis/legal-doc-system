/**
 * WILSY OS — RECOVERY SECURITY PRODUCT WIRING CERTIFICATE
 * TITLE: Account recovery-contact security wiring direct certificate
 * VERSION: v1.3.0-VERIFIED-RECOVERY-LABEL-CERT
 * CHANGELOG: v1.3.0-VERIFIED-RECOVERY-LABEL-CERT checks verified-only recovery terminology and retains fail-closed unavailable semantics.
 * CHANGELOG: v1.3.0-VERIFIED-RECOVERY-LABEL-CERT — checks Account Center header/seal version alignment and retains the historical recovery changelog entry.
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies that authenticated recovery-email verification is reachable
 *          from Account Security while browser presentation cannot nominate
 *          email, tenant, principal, token, or verified-contact authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/recoveryContactSecurityWiring.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises RecoveryContactSecurityControl at the
 *                            client transport seam and certifies its bounded
 *                            WilsyAccountCommandCenter desktop/mobile wiring.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.0-R10F2-RECOVERY-SECURITY-WIRING-CERT introduces direct evidence for zero-argument
 *            verification transport, bounded success/rate-limit presentation,
 *            desktop/mobile Security-panel mounting, and rejection of Account
 *            Center fallback-email authority.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic email only; no network is contacted,
 *                             no recovery secret is created, and no browser
 *                             email/tenant/principal value is sent.
 * TENANT BOUNDARY: Account Center tenant/display fallbacks remain presentation
 *                  only and cannot enter the verification request.
 * AUTHORITY BOUNDARY: Client presentation/transport evidence only; Python EOS
 *                     owns durable principal/email and verified-contact truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { requestRecoveryContactVerification, getRecoveryContactStatus } = vi.hoisted(() => ({
  requestRecoveryContactVerification: vi.fn(),
  getRecoveryContactStatus: vi.fn(),
}));

vi.mock('../../services/api.js', () => ({
  requestRecoveryContactVerification,
  getRecoveryContactStatus,
}));

import RecoveryContactSecurityControl from '../../components/account/RecoveryContactSecurityControl.jsx';

const ACCOUNT_SOURCE = resolve(
  process.cwd(),
  'src/components/account/WilsyAccountCommandCenter.jsx',
);

describe('R10F recovery-contact security product wiring', () => {
  beforeEach(() => {
    requestRecoveryContactVerification.mockReset();
    getRecoveryContactStatus.mockReset();
    getRecoveryContactStatus.mockResolvedValue({ status: 200, data: { status: 'VERIFICATION_REQUIRED' } });
  });

  it('requests verification without browser-supplied authority and shows bounded sent state', async () => {
    requestRecoveryContactVerification.mockResolvedValue({
      status: 202,
      data: { status: 'VERIFICATION_SENT' },
    });

    render(
      <RecoveryContactSecurityControl email=" operator@example.test " />,
    );

    expect(screen.getByText('operator@example.test')).toBeInTheDocument();

    fireEvent.click(await screen.findByRole('button', { name: 'Verify recovery email' }));

    await waitFor(() => {
      expect(requestRecoveryContactVerification).toHaveBeenCalledTimes(1);
    });
    expect(requestRecoveryContactVerification).toHaveBeenCalledWith();
    expect(
      screen.getByText('Verification sent. Open the secure email link to finish.'),
    ).toBeInTheDocument();
  });

  it('uses server-owned current-email copy when no authenticated display email exists', async () => {
    getRecoveryContactStatus.mockResolvedValue({ status: 200, data: { status: 'VERIFIED' } });

    render(<RecoveryContactSecurityControl />);

    expect(
      screen.getByText('Your current account email will be verified by the server.'),
    ).toBeInTheDocument();

    expect(await screen.findByText('Email ownership confirmed by EOS.')).toBeInTheDocument();
    expect(screen.getByText('Verified recovery email')).toBeInTheDocument();
    expect(getRecoveryContactStatus).toHaveBeenCalledWith();
    expect(requestRecoveryContactVerification).not.toHaveBeenCalled();
    expect(screen.queryByRole('button', { name: 'Verify recovery email' })).not.toBeInTheDocument();
  });

  it('renders rate limiting without creating local verified state', async () => {
    requestRecoveryContactVerification.mockRejectedValue({
      response: { status: 429 },
    });

    render(<RecoveryContactSecurityControl email="operator@example.test" />);

    fireEvent.click(await screen.findByRole('button', { name: 'Verify recovery email' }));

    expect(
      await screen.findByRole('alert'),
    ).toHaveTextContent('Verification requests are temporarily rate-limited.');
    expect(
      screen.queryByText('Email ownership confirmed by EOS.'),
    ).not.toBeInTheDocument();
  });

  it('keeps recovery status unavailable and never issues a mail request on source failure', async () => {
    getRecoveryContactStatus.mockRejectedValue({ response: { status: 503 } });
    render(<RecoveryContactSecurityControl email="operator@example.test" />);
    expect(await screen.findByRole('alert')).toHaveTextContent('Recovery email status unavailable');
    expect(screen.getByText('Recovery email')).toBeInTheDocument();
    expect(screen.queryByText('Verified recovery email')).not.toBeInTheDocument();
    expect(requestRecoveryContactVerification).not.toHaveBeenCalled();
    expect(screen.queryByRole('button', { name: 'Verify recovery email' })).not.toBeInTheDocument();
  });

  it('identifies an unmounted EOS route and retries only the status read', async () => {
    getRecoveryContactStatus.mockRejectedValueOnce({ response: { status: 404 } })
      .mockResolvedValueOnce({ status: 200, data: { status: 'VERIFIED' } });
    render(<RecoveryContactSecurityControl email="operator@example.test" />);
    expect(await screen.findByRole('alert')).toHaveTextContent('does not expose the recovery status route');
    fireEvent.click(screen.getByRole('button', { name: 'Retry status read' }));
    expect(await screen.findByText('Email ownership confirmed by EOS.')).toBeInTheDocument();
    expect(getRecoveryContactStatus).toHaveBeenCalledTimes(2);
    expect(requestRecoveryContactVerification).not.toHaveBeenCalled();
  });

  it('mounts recovery verification only in Account Security using explicit user email display', () => {
    const source = readFileSync(ACCOUNT_SOURCE, 'utf8');
    const mountPattern =
      /<RecoveryContactSecurityControl email=\{recoveryDisplayEmail\}(?: compact)? \/>/g;
    const mounts = source.match(mountPattern) || [];

    expect(source).toContain(
      "import RecoveryContactSecurityControl from './RecoveryContactSecurityControl.jsx';",
    );
    expect(mounts).toHaveLength(2);
    expect(source).toContain("typeof user?.email === 'string'");
    expect(source).toContain("typeof user?.primaryEmail === 'string'");
    expect(source).not.toContain(
      '<RecoveryContactSecurityControl email={identity.email}',
    );
    expect(source).not.toContain(
      '<RecoveryContactSecurityControl email={activeTenant',
    );

    const securitySections = source.split("activePanel === 'security'");
    expect(securitySections).toHaveLength(3);
    expect(securitySections[1]).toContain(
      '<RecoveryContactSecurityControl email={recoveryDisplayEmail} compact />',
    );
    expect(securitySections[2]).toContain(
      '<RecoveryContactSecurityControl email={recoveryDisplayEmail} />',
    );
  });

  it('keeps Account Center sovereign version and recovery authority declarations aligned', () => {
    const source = readFileSync(ACCOUNT_SOURCE, 'utf8');
    const currentVersion = 'v3.2.0-L10-P2C6-BRANDING-COMMAND-CENTER';
    const recoveryChange = 'v3.1.0-R10F1-RECOVERY-SECURITY-WIRING';

    expect((source.match(new RegExp(currentVersion, 'g')) || [])).toHaveLength(3);
    expect((source.match(new RegExp(recoveryChange, 'g')) || [])).toHaveLength(1);
    expect(source).toContain(
      'Python EOS re-reads durable authenticated principal/email truth',
    );
    expect(source.trimEnd()).toMatch(
      /END OF WILSY OS SOVEREIGN ARTIFACT\n \*\/$/,
    );
  });
});

/**
 * WILSY OS SOVEREIGN ARTIFACT SEAL
 * ARTIFACT: recoveryContactSecurityWiring.test.jsx
 * VERSION: v1.3.0-VERIFIED-RECOVERY-LABEL-CERT
 * AUTHORITY BOUNDARY: deterministic client presentation/wiring evidence only
 * TENANT POSTURE: no browser tenant/email authority admitted
 * FAIL-CLOSED POSTURE: transport/rate failures never create verified state
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
