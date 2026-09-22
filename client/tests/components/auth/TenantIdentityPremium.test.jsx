/**
 * WILSY OS — PREMIUM TENANT IDENTITY CERTIFICATE
 * VERSION: v1.7.0-R10D9G-RESET-PARITY-LOGIN-ARCHITECTURE-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies the bounded discovery/login identity projection, permanent
 *          platform trust mark, and neutral tenant-logo fallback.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/components/auth/TenantIdentityPremium.test.jsx
 * COLLABORATION / OWNERSHIP: Exercises TenantDiscovery, SovereignLogin, and
 *                            TenantIdentityCard without network or auth writes.
 * CERTIFICATION / UPDATE DATE: 2026-09-17
 * CHANGELOG: v1.7.0-R10D9G-RESET-PARITY-LOGIN-ARCHITECTURE-CERT — Certifies
 *            reset-parity login architecture: one full-width page heading
 *            precedes the balanced identity/credentials grid, panel width is
 *            bounded to the shared auth grammar, and existing tenant/auth
 *            presentation safeguards remain intact.
 *            v1.6.0-R10D9F-INSTITUTIONAL-LOGIN-COMPOSITION-CERT — Certifies the
 *            final login composition: no redundant workspace-identity eyebrow,
 *            top-aligned identity/form columns, bounded natural-flow geometry,
 *            and unchanged authoritative tenant projection semantics.
 *            v1.5.0-R10D9E-PREMIUM-TENANT-IDENTITY-HIERARCHY-CERT — Certifies
 *            presentation-duplicate alias suppression, preservation of genuinely
 *            distinct workspace aliases, compact verified-state evidence, and
 *            continued absence of internal tenant identifiers.
 *            v1.4.0-FINAL-PIXEL-CLOSURE-CERT — Certifies display-first
 *            monograms, punctuation-free corporate-name fallbacks, a single
 *            platform mark, and balanced natural-flow login geometry.
 *            v1.3.0-VIEWPORT-SAFE-AUTH-CERT — Added natural-flow viewport
 *            assertions for the final auth panel.
 *            v1.2.0-PUBLIC-IDENTITY-CONTRACT-CERT — Added exact legal-name
 *            precedence and public tenant-ID absence assertions.
 *            v1.1.0-INSTITUTIONAL-AUTH-BRAND-CERT — Added established brand
 *            asset and integrated panel assertions.
 *            v1.0.0-PREMIUM-TENANT-IDENTITY-CERT — Added focused presentation
 *            and no-client-inference assertions.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic server-shaped projections only.
 * TENANT BOUNDARY: The rendered tenant is supplied by the mocked authoritative
 *                  discovery/session seam.
 * AUTHORITY BOUNDARY: Presentation evidence only; no login or tenant grant.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import TenantIdentityCard, { tenantMonogram } from '../../../src/components/auth/TenantIdentityCard.jsx';
import SovereignLogin from '../../../src/components/auth/SovereignLogin.jsx';
import TenantDiscovery from '../../../src/components/sovereign/TenantDiscovery.jsx';

const navigate = vi.fn();
const discoverTenant = vi.fn();
const login = vi.fn();
const locationState = { pathname: '/discovery', state: null };

vi.mock('../../../src/contexts/authContext.jsx', () => ({
  AUTH_STATES: {
    MFA_SETUP: 'MFA_SETUP',
    MFA_RECONCILIATION_REQUIRED: 'MFA_RECONCILIATION_REQUIRED',
    MFA_REQUIRED: 'MFA_REQUIRED',
  },
  useAuth: () => ({
    discoverTenant,
    login,
    loading: false,
    error: null,
    tenant: null,
  }),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigate,
    useLocation: () => locationState,
  };
});

const verifiedTenant = {
  tenantId: 'TENANT-ACME',
  alias: 'acme',
  name: 'Acme Display',
  legalName: 'Acme Legal Holdings (Pty) Ltd',
  verified: true,
  region: 'Africa',
  plan: 'ENTERPRISE',
  status: 'ACTIVE',
};

describe('premium tenant identity projection', () => {
  beforeEach(() => {
    navigate.mockReset();
    discoverTenant.mockReset();
    login.mockReset();
    locationState.pathname = '/discovery';
    locationState.state = null;
  });

  it('keeps the WILSY OS mark visible and makes legal name primary', () => {
    render(<TenantIdentityCard tenant={verifiedTenant} />);

    expect(screen.getByText('Secured by WILSY OS')).toBeInTheDocument();
    expect(screen.queryByAltText('WILSY OS platform mark')).not.toBeInTheDocument();
    expect(screen.getByText('Acme Legal Holdings (Pty) Ltd')).toBeInTheDocument();
    expect(screen.getByText('Acme Display')).toBeInTheDocument();
    expect(screen.getByText('Workspace: acme')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('Verified workspace');
    expect(screen.queryByText('Tenant ID: TENANT-ACME')).not.toBeInTheDocument();
    expect(screen.queryByAltText(/tenant logo/i)).not.toBeInTheDocument();
  });

  it('uses only the authoritative display name when legal name is absent', () => {
    render(<TenantIdentityCard tenant={{ ...verifiedTenant, legalName: undefined, verified: false }} />);

    expect(screen.getByText('Acme Display')).toBeInTheDocument();
    expect(screen.queryByText('Verified workspace')).not.toBeInTheDocument();
    expect(screen.queryByText('Acme Legal Holdings (Pty) Ltd')).not.toBeInTheDocument();
  });

  it('derives the neutral fallback from identity text, never from the workspace alias', () => {
    expect(tenantMonogram({ name: 'wilsy', legalName: 'Wilsy (Pty) Ltd', alias: 'wilsy' })).toBe('W');
    expect(tenantMonogram({ name: 'Bowman Gilfillan' })).toBe('BG');
    expect(tenantMonogram({ name: 'Acme Law' })).toBe('AL');
    expect(tenantMonogram({ legalName: 'Wilsy (Pty) Ltd' })).toBe('W');
    expect(tenantMonogram({ legalName: 'Acme Legal (Pty) Ltd' })).toBe('AL');
    expect(tenantMonogram({ legalName: 'Example Holdings Limited' })).toBe('EH');
    expect(tenantMonogram({ name: 'Acme Display', alias: 'different-alias' })).toBe('AD');
    expect(tenantMonogram({ legalName: 'Acme Legal Holdings', alias: 'wilsy' })).toBe('AL');
    expect(tenantMonogram({ name: 'Acme, (Pty) Ltd' })).toMatch(/^[A-Z]{1,2}$/);
  });

  it('suppresses a presentation-duplicate alias for the live wilsy-shaped projection', () => {
    render(<TenantIdentityCard tenant={{
      tenantId: 'WILSYTENANT-4CD2FZ4O',
      alias: 'wilsy',
      name: 'wilsy',
      legalName: 'Wilsy (Pty) Ltd',
      verified: true,
    }} />);

    expect(screen.getByText('Wilsy (Pty) Ltd')).toBeInTheDocument();
    expect(screen.getByText('wilsy')).toBeInTheDocument();
    expect(screen.queryByText('Workspace: wilsy')).not.toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('Verified workspace');
    expect(screen.queryByText('WILSYTENANT-4CD2FZ4O')).not.toBeInTheDocument();
  });

  it('restores the platform mark on discovery and preserves the discovery-to-login transition', async () => {
    discoverTenant.mockResolvedValue(verifiedTenant);
    render(
      <MemoryRouter>
        <TenantDiscovery />
      </MemoryRouter>,
    );

    expect(screen.getByAltText('WILSY OS platform mark')).toHaveAttribute('src', expect.stringContaining('wilsy.jpeg'));
    fireEvent.change(screen.getByLabelText('Organization / workspace'), { target: { value: 'acme' } });
    fireEvent.click(screen.getByRole('button', { name: /continue securely/i }));

    await waitFor(() => expect(navigate).toHaveBeenCalledWith('/login', expect.objectContaining({
      state: { tenant: verifiedTenant, from: '/discovery' },
    })));
  });

  it('renders the platform mark and premium identity on login without alias-based branding', () => {
    locationState.pathname = '/login';
    locationState.state = { tenant: verifiedTenant };
    render(
      <MemoryRouter>
        <SovereignLogin />
      </MemoryRouter>,
    );

    expect(screen.getAllByAltText('WILSY OS platform mark')).toHaveLength(1);
    expect(screen.getAllByAltText('WILSY OS platform mark')[0]).toHaveAttribute('src', expect.stringContaining('wilsy.jpeg'));
    expect(screen.getByText('WILSY OS')).toBeInTheDocument();
    expect(screen.getByText('Acme Legal Holdings (Pty) Ltd')).toBeInTheDocument();
    expect(screen.getByText('Workspace: acme')).toBeInTheDocument();
    expect(screen.queryByText(/Tenant ID:/i)).not.toBeInTheDocument();
    expect(screen.getByTestId('login-panel')).not.toHaveStyle({ height: '100vh' });
    expect(screen.getByTestId('login-panel').parentElement).toHaveStyle({ minHeight: '100dvh', overflowX: 'hidden', overflowY: 'auto' });
    expect(screen.getByTestId('login-panel').getAttribute('style')).toContain('min-height: 0');
    expect(screen.getByTestId('login-panel').getAttribute('style')).toContain('width: min(1080px, 100%)');
    expect(screen.getByTestId('login-page-heading')).toHaveTextContent('Sign in');
    expect(screen.getByTestId('login-page-heading').nextElementSibling).toBe(screen.getByTestId('login-content-grid'));
    expect(screen.getByTestId('login-content-grid').getAttribute('style')).toContain('auto-fit');
    expect(screen.getByTestId('login-content-grid').getAttribute('style')).toContain('min(100%, 320px)');
    expect(screen.getByTestId('login-content-grid').getAttribute('style')).toContain('align-items: start');
    expect(screen.queryByText('Workspace identity')).not.toBeInTheDocument();
  });
});

/**
 * ARTIFACT: TenantIdentityPremium.test.jsx
 * VERSION: v1.7.0-R10D9G-RESET-PARITY-LOGIN-ARCHITECTURE-CERT
 * AUTHORITY BOUNDARY: deterministic client projection certificate only
 * TENANT POSTURE: no alias-specific logo or inferred legal identity
 * FAIL-CLOSED POSTURE: absent tenant identity is never fabricated
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
