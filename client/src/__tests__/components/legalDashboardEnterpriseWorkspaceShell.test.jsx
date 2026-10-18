/**
 * WILSY OS — ENTERPRISE LEGAL SPECIALIST WORKSPACE SHELL CERTIFICATE
 * VERSION: v1.1.0-LEGAL-COMMERCIAL-CONTEXT-PRESENTATION-CERT
 * AUTHORITY: Browser presentation certification only.
 * EPITOME: Certifies shared Sheriff/Deputy Legal OS chrome plus exact
 *          server-result-driven commercial presentation states without
 *          browser-owned IAM, plan, tenant, payment or settlement authority.
 * CERTIFICATION / UPDATE DATE: 2026-10-16
 * CHANGELOG: 2026-10-16 v1.1.0-LEGAL-COMMERCIAL-CONTEXT-PRESENTATION-CERT
 *            adds authorized, denied and unavailable commercial presentation
 *            proofs and preserves authenticated tenant branding as an
 *            independent identity source.
 * TENANT BOUNDARY: authenticated tenant branding and commercial projection
 *                  remain separate server-derived presentation authorities.
 * AUTHORITY BOUNDARY: role labels, browser permissions and navigation state
 *                     never grant commercial or Legal Operations authority.
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
 */
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  authState: {
    user: {
      id: 'principal-sheriff',
      email: 'sheriff.operator@example.test',
      firstName: 'Amina',
      lastName: 'Dlamini',
      role: 'tenant_sheriff',
      tenantId: 'tenant-law',
    },
    tenant: {
      tenantId: 'tenant-law',
      name: 'Fortune Legal LLP',
      legalName: 'Fortune Legal LLP',
      status: 'ACTIVE',
      branding: null,
    },
  },
  getSheriffOperationalQueues: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getLegalCommercialContext: vi.fn(),
  brandingHook: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'enterprise-specialist-shell-cert',
  getSheriffOperationalQueues: mocks.getSheriffOperationalQueues,
  getDeputyPersonalActiveWork: mocks.getDeputyPersonalActiveWork,
  getDeputyFieldCapabilities: mocks.getDeputyFieldCapabilities,
  getLegalCommercialContext: mocks.getLegalCommercialContext,
  getLegalClientMatters: vi.fn(),
  getLegalClientAcceptanceInstruments: vi.fn(),
  createLegalClientAcceptanceContext: vi.fn(),
  getLegalClientAcceptanceContent: vi.fn(),
  confirmLegalClientAcceptance: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: vi.fn(),
  getLegalProductiveWork: vi.fn(),
  generateLegalReturnOfService: vi.fn(),
  issueLegalConflictReview: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  registerLegalIntake: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
  uploadLegalEvidence: vi.fn(),
}));

vi.mock('../../services/legalMatterDeadlineService.js', () => ({
  createLegalMatterDeadline: vi.fn(),
  getLegalMatterDeadlines: vi.fn(),
}));

vi.mock('../../contexts/authContext.jsx', () => ({
  useAuth: () => mocks.authState,
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => mocks.authState,
}));

vi.mock('../../contexts/tenantContext.jsx', () => ({
  useTenants: () => ({
    activeTenant: mocks.authState.tenant,
    tenants: [],
  }),
}));

vi.mock('../../contexts/tenantContext', () => ({
  useTenants: () => ({
    activeTenant: mocks.authState.tenant,
    tenants: [],
  }),
}));

vi.mock('../../hooks/useAuthenticatedTenantBrandingAsset.js', () => ({
  useAuthenticatedTenantBrandingAsset: mocks.brandingHook,
}));

vi.mock('../../components/account/WilsyAccountCommandCenter.jsx', () => ({
  default: ({ isOpen, onClose, user }) => (
    isOpen ? (
      <div role="dialog" aria-label="Account Command Center">
        <span>{user?.email}</span>
        <button type="button" onClick={onClose}>Close account</button>
      </div>
    ) : null
  ),
}));

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const sheriffQueues = Object.freeze({
  tenantId: 'tenant-law',
  visibility: 'SHERIFF_OPERATIONAL_QUEUE',
  officeReceipt: [],
  deputyAssignment: [],
  activeAttempts: [],
});

const authorizedCommercialContext = Object.freeze({
  access: 'AUTHORIZED',
  context: Object.freeze({
    tenantId: 'tenant-law',
    product: Object.freeze({
      productId: 'LEGAL_OPERATIONS',
      workspaceKey: 'LEGAL_DASHBOARD',
      available: true,
      entitlementState: 'ACTIVE',
    }),
    subscription: Object.freeze({
      subscriptionId: 'WILSYSUB-CERT-1',
      status: 'active',
      currentPeriodEnd: '2026-11-16T09:00:00+00:00',
    }),
    plan: Object.freeze({
      planId: 'WILSYPLAN-CERT-1',
      tier: 'ENTERPRISE',
      name: 'Certified Legal Plan',
      features: Object.freeze(['legal.core']),
      catalogueVersion: 7,
    }),
    commercial: Object.freeze({
      amount: 14400,
      currency: 'ZAR',
      billingFrequency: 'annual',
      monthlyEquivalentAmount: 1200,
      financialExecutionAuthority: false,
    }),
  }),
});

const deniedCommercialContext = Object.freeze({
  access: 'DENIED',
  context: null,
});

beforeEach(() => {
  mocks.authState.user = {
    id: 'principal-sheriff',
    email: 'sheriff.operator@example.test',
    firstName: 'Amina',
    lastName: 'Dlamini',
    role: 'tenant_sheriff',
    tenantId: 'tenant-law',
  };
  mocks.authState.tenant = {
    tenantId: 'tenant-law',
    name: 'Fortune Legal LLP',
    legalName: 'Fortune Legal LLP',
    status: 'ACTIVE',
    branding: null,
  };
  mocks.getSheriffOperationalQueues.mockReset();
  mocks.getSheriffOperationalQueues.mockResolvedValue(sheriffQueues);
  mocks.getDeputyPersonalActiveWork.mockReset();
  mocks.getDeputyFieldCapabilities.mockReset();
  mocks.getLegalCommercialContext.mockReset();
  mocks.getLegalCommercialContext.mockResolvedValue(
    deniedCommercialContext,
  );
  mocks.brandingHook.mockReset();
  mocks.brandingHook.mockReturnValue({
    objectUrl: null,
    status: 'ABSENT',
    errorCode: null,
  });
});

describe('WILSY Legal OS enterprise specialist shell', () => {
  it('converges Sheriff onto shared OS chrome with tenant and operator identity', async () => {
    const { container } = render(
      <LegalDashboard roleView="SHERIFF" />,
    );

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );

    expect(
      container.querySelector('[data-wilsy-os-dashboard-chrome="true"]'),
    ).not.toBeNull();

    expect(screen.getByText('Fortune Legal LLP')).toBeInTheDocument();
    expect(screen.getAllByText('Amina Dlamini').length).toBeGreaterThanOrEqual(1);

    expect(
      screen.getByRole('navigation', {
        name: 'WILSY Legal OS workspace navigation',
      }),
    ).toBeInTheDocument();

    expect(
      container.querySelector('[data-legal-workspace-viewport="MY_WORK"]'),
    ).not.toBeNull();
  });

  it('shows grey locked menu entries and explains attempted access', async () => {
    render(<LegalDashboard roleView="SHERIFF" />);

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );

    await waitFor(() =>
      expect(mocks.getLegalCommercialContext).toHaveBeenCalledTimes(1),
    );

    await waitFor(() => {
      expect(
        document.querySelector(
          '[data-commercial-context-state="DENIED"]',
        ),
      ).not.toBeNull();
    });

    const matters = screen.getByRole('button', { name: /Matters/i });
    expect(matters).toHaveAttribute('aria-disabled', 'true');
    expect(matters).toHaveAttribute('data-access-state', 'DENIED');

    fireEvent.click(matters);

    const notice = screen.getByRole('status', {
      name: 'Workspace access notice',
    });
    expect(notice).toHaveTextContent('Access not permitted');
    expect(notice).toHaveTextContent('Matter-practice workspace');

    const calendar = screen.getByRole('button', { name: /Calendar/i });
    expect(calendar).toHaveAttribute('data-access-state', 'UNAVAILABLE');

    fireEvent.click(calendar);
    expect(
      screen.getByRole('status', { name: 'Workspace access notice' }),
    ).toHaveTextContent('certified specialist calendar source');
  });

  it('switches available My Work and Process Service navigation', async () => {
    const { container } = render(
      <LegalDashboard roleView="SHERIFF" />,
    );

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );

    fireEvent.click(
      screen.getByRole('button', { name: /^Process Service$/i }),
    );

    expect(
      container.querySelector(
        '[data-legal-workspace-viewport="PROCESS_SERVICE"]',
      ),
    ).not.toBeNull();
    expect(screen.getByRole('heading', { name: 'Process Service' }))
      .toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^My Work$/i }));

    expect(
      container.querySelector(
        '[data-legal-workspace-viewport="MY_WORK"]',
      ),
    ).not.toBeNull();
  });

  it('renders canonical commercial detail only after server-authorized result', async () => {
    mocks.getLegalCommercialContext.mockResolvedValueOnce(
      authorizedCommercialContext,
    );

    const { container } = render(
      <LegalDashboard roleView="SHERIFF" />,
    );

    await waitFor(() => {
      expect(
        container.querySelector(
          '[data-commercial-context-state="AUTHORIZED"]',
        ),
      ).not.toBeNull();
    });

    expect(
      mocks.getLegalCommercialContext,
    ).toHaveBeenCalledTimes(1);

    const commercial = container.querySelector(
      '[data-commercial-context-state="AUTHORIZED"]',
    );

    expect(commercial).toHaveTextContent('Certified Legal Plan');
    expect(commercial).toHaveTextContent('ENTERPRISE');
    expect(commercial).toHaveTextContent('LEGAL_OPERATIONS');
    expect(commercial).toHaveTextContent('WILSYSUB-CERT-1');
    expect(commercial).toHaveTextContent('Monthly equivalent');
    expect(commercial).toHaveTextContent(/ZAR\s+1[,\s]?200/);
    expect(commercial).toHaveTextContent(
      'Financial execution authority: none',
    );
  });

  it('renders commercial detail as locked when the server denies access', async () => {
    mocks.getLegalCommercialContext.mockResolvedValueOnce(
      deniedCommercialContext,
    );

    const { container } = render(
      <LegalDashboard roleView="SHERIFF" />,
    );

    await waitFor(() => {
      expect(
        container.querySelector(
          '[data-commercial-context-state="DENIED"]',
        ),
      ).not.toBeNull();
    });

    const commercial = container.querySelector(
      '[data-commercial-context-state="DENIED"]',
    );

    expect(commercial).toHaveTextContent(
      'Commercial details locked',
    );
    expect(commercial).toHaveTextContent(
      'Legal role does not grant subscription authority.',
    );

    expect(
      screen.queryByText('Certified Legal Plan'),
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText('WILSYSUB-CERT-1'),
    ).not.toBeInTheDocument();
  });

  it('renders commercial source unavailable without manufacturing plan truth', async () => {
    mocks.getLegalCommercialContext.mockRejectedValueOnce(
      new Error('COMMERCIAL_SOURCE_UNAVAILABLE'),
    );

    const { container } = render(
      <LegalDashboard roleView="SHERIFF" />,
    );

    await waitFor(() => {
      expect(
        container.querySelector(
          '[data-commercial-context-state="UNAVAILABLE"]',
        ),
      ).not.toBeNull();
    });

    const commercial = container.querySelector(
      '[data-commercial-context-state="UNAVAILABLE"]',
    );

    expect(commercial).toHaveTextContent(
      'Commercial context unavailable',
    );
    expect(commercial).toHaveTextContent(
      'will not infer plan, subscription or price evidence',
    );
    expect(
      screen.queryByText('Certified Legal Plan'),
    ).not.toBeInTheDocument();
  });

  it('keeps authenticated tenant branding independent from authorized commercial context', async () => {
    mocks.authState.tenant = {
      tenantId: 'tenant-law',
      name: 'Fortune Legal LLP',
      legalName: 'Fortune Legal LLP',
      status: 'ACTIVE',
      branding: {
        tenantId: 'tenant-law',
        profileId: 'branding-profile-1',
        profileLabel: 'Fortune Legal Identity',
        brandingTier: 'ENTERPRISE',
        platformTrustMarkRequired: true,
        primaryColor: null,
        secondaryColor: null,
        accentColor: null,
        emailDisplayName: null,
        logo: {
          reference: 'branding-asset:logo:1',
          contentFingerprint: 'a'.repeat(128),
          mediaType: 'image/png',
          kind: 'LOGO',
        },
        favicon: null,
      },
    };

    mocks.brandingHook.mockReturnValue({
      objectUrl: 'blob:authenticated-tenant-logo',
      status: 'READY',
      errorCode: null,
    });

    mocks.getLegalCommercialContext.mockResolvedValueOnce(
      authorizedCommercialContext,
    );

    const { container } = render(
      <LegalDashboard roleView="SHERIFF" />,
    );

    await waitFor(() => {
      expect(
        container.querySelector(
          '[data-commercial-context-state="AUTHORIZED"]',
        ),
      ).not.toBeNull();
    });

    expect(
      container.querySelector(
        '[data-wilsy-tenant-branding="authenticated"]',
      ),
    ).not.toBeNull();

    expect(
      screen.getByText(/Fortune Legal Identity/),
    ).toBeInTheDocument();

    expect(
      screen.getByText('Certified Legal Plan'),
    ).toBeInTheDocument();

    expect(
      mocks.getLegalCommercialContext,
    ).toHaveBeenCalledTimes(1);
  });

  it('opens shared account surface for authenticated Sheriff identity', async () => {
    render(<LegalDashboard roleView="SHERIFF" />);

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );

    fireEvent.click(screen.getByTitle('Account'));

    const dialog = screen.getByRole('dialog', {
      name: 'Account Command Center',
    });
    expect(dialog).toHaveTextContent('sheriff.operator@example.test');
  });
});

/**
 * ARTIFACT: legalDashboardEnterpriseWorkspaceShell.test.jsx
 * VERSION: v1.1.0-LEGAL-COMMERCIAL-CONTEXT-PRESENTATION-CERT
 * AUTHORITY BOUNDARY: browser presentation certificate only; server response remains authoritative
 * TENANT POSTURE: authenticated tenant branding and commercial context remain separate server-derived projections
 * FAIL-CLOSED POSTURE: denied or unavailable commercial evidence never reveals or fabricates plan/subscription/value truth
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
