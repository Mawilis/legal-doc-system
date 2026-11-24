/**
 * TITLE: Post-MFA Session Ownership Certificate
 * VERSION: v1.0.2-SESSION-TENANT-BINDING-SOVEREIGN-METADATA
 * CHANGELOG: v1.0.2-SESSION-TENANT-BINDING-SOVEREIGN-METADATA completes privacy and financial boundary metadata without changing certificate behavior.
 * CHANGELOG: v1.0.1-SESSION-TENANT-BINDING-CERT — certifies discovered tenant propagation into the AuthProvider OTP handoff.
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves MFA presentation delegates session persistence to AuthProvider
 *          and performs one guarded route transition without hard reloads.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/SovereignMfaPortal.session-owner.test.jsx
 * COLLABORATION / OWNERSHIP: SovereignMfaPortal, AuthProvider, React Router.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * CHANGELOG: v1.0.0-SESSION-OWNER-CERT — Initial focused certificate.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic principal, tenant and OTP projections only.
 * TENANT BOUNDARY: AuthProvider owns tenant binding; the component cannot select tenant authority.
 * AUTHORITY BOUNDARY: Presentation certificate only; Python EOS and AuthProvider own session authority.
 * FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { verifyOTP, navigate } = vi.hoisted(() => ({
  verifyOTP: vi.fn(),
  navigate: vi.fn(),
}));

vi.mock('../../../src/contexts/authContext.jsx', () => ({
  AUTH_STATES: {
    MFA_SETUP: 'MFA_SETUP',
    MFA_REQUIRED: 'MFA_REQUIRED',
    MFA_RECONCILIATION_REQUIRED: 'MFA_RECONCILIATION_REQUIRED',
    MFA_VERIFYING: 'MFA_VERIFYING',
  },
  useAuth: () => ({
    authStage: 'MFA_REQUIRED',
    pendingEmail: 'person@example.com',
    qrCodeData: '',
    tenant: { tenantId: 'TENANT-A', name: 'Tenant A' },
    verifyOTP,
    loading: false,
    error: null,
  }),
}));
vi.mock('react-router-dom', () => ({
  useNavigate: () => navigate,
  useLocation: () => ({ pathname: '/mfa' }),
}));
vi.mock('qrcode', () => ({ default: { toDataURL: vi.fn() } }));

import SovereignMfaPortal from '../../../src/components/auth/SovereignMfaPortal.jsx';

describe('MFA session ownership', () => {
  beforeEach(() => {
    verifyOTP.mockReset();
    navigate.mockReset();
    verifyOTP.mockResolvedValue({ user: { tenantId: 'TENANT-A', hasSignedCovenant: false } });
  });

  it('delegates OTP verification to AuthProvider and navigates once without window.location', async () => {
    const locationDescriptor = Object.getOwnPropertyDescriptor(window, 'location');
    render(<SovereignMfaPortal />);
    fireEvent.change(screen.getByLabelText('Six-digit code'), { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: 'Verify identity' }));
    await waitFor(() => expect(verifyOTP).toHaveBeenCalledWith('person@example.com', '123456', null, null, false, 'TENANT-A'));
    expect(navigate).toHaveBeenCalledTimes(1);
    expect(navigate).toHaveBeenCalledWith('/covenant', { replace: true });
    expect(Object.getOwnPropertyDescriptor(window, 'location')).toEqual(locationDescriptor);
  });
});

/**
 * ARTIFACT: client/tests/components/auth/SovereignMfaPortal.session-owner.test.jsx
 * VERSION: v1.0.2-SESSION-TENANT-BINDING-SOVEREIGN-METADATA
 * AUTHORITY BOUNDARY: MFA presentation and transport only
 * TENANT POSTURE: tenant identity is display-only server evidence
 * FAIL-CLOSED POSTURE: invalid challenge state redirects to sign-in
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
