/**
 * WILSY OS — NODE PASSWORD-RECOVERY AUTHORITY ABSENCE CERTIFICATE
 * TITLE: Node Recovery Authority Absence Certificate
 * VERSION: v1.0.0-R10E66-NODE-RECOVERY-AUTHORITY-ABSENCE-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies that the mounted Node auth router exposes no password
 *          recovery/reset endpoint and imports no recovery/reset controller,
 *          leaving canonical recovery/reset HTTP authority to Python EOS.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/unit/AuthRecoveryAuthority.test.js
 * COLLABORATION / OWNERSHIP: server/routes/authRoutes.js is the certified Node
 *                            routing surface; tools/eos/api/auth_router.py is
 *                            the canonical Python recovery/reset HTTP authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E66-NODE-RECOVERY-AUTHORITY-ABSENCE-CERT — Adds direct
 *            source certification for retired Node reset route/controller
 *            binding while preserving unrelated Node auth transport.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Static source inspection only; no credentials,
 *                             tokens, email addresses, or production data.
 * TENANT BOUNDARY: No tenant data is read or inferred by this certificate.
 * AUTHORITY BOUNDARY: Evidence only; grants no authentication or recovery authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED POSTURE: Any executable Node reset route or controller binding
 *                      fails the certificate.
 */

import { expect } from 'chai';
import { readFile } from 'node:fs/promises';

const AUTH_ROUTES_URL = new URL('../../routes/authRoutes.js', import.meta.url);

describe('R10E66 Node recovery authority absence', () => {
  let source;

  before(async () => {
    source = await readFile(AUTH_ROUTES_URL, 'utf8');
  });

  it('does not expose the retired Node reset route', () => {
    expect(source).not.to.include("router.post('/reset-password-sovereign'");
    expect(source).not.to.include('router.get(\'/reset-password-sovereign\'');
  });

  it('does not import or bind the retired reset controller', () => {
    expect(source).not.to.match(/\bresetPasswordSovereign\b/);
  });

  it('retains canonical recovery delegation language', () => {
    expect(source).to.include('Python EOS');
    expect(source).to.include('no recovery/reset authority');
  });

  it('retains the unrelated auth transport bindings', () => {
    for (const route of [
      '/discover',
      '/register',
      '/login',
      '/verify-3fa',
      '/verify-otp',
      '/refresh',
      '/webauthn-challenge',
      '/me',
      '/logout',
      '/anchor-hardware',
      '/revoke-biometric',
      '/verify-forensic-chain',
      '/setup-mfa',
      '/validate-mfa-setup',
    ]) {
      expect(source).to.include(`'${route}'`);
    }
  });
});

/**
 * ARTIFACT: server/tests/unit/AuthRecoveryAuthority.test.js
 * VERSION: v1.0.0-R10E66-NODE-RECOVERY-AUTHORITY-ABSENCE-CERT
 * AUTHORITY BOUNDARY: static Node recovery-route absence evidence only
 * TENANT POSTURE: no tenant data or cross-tenant inference
 * FAIL-CLOSED POSTURE: any executable Node recovery/reset route or binding fails
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
