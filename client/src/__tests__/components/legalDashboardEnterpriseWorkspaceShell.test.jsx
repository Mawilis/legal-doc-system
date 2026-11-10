/**
 * TITLE: WILSY OS Enterprise Legal Specialist Workspace Shell Certificate
 * VERSION: v1.3.1-LEGAL-PRACTICE-COMMERCE-SEPARATION-SOVEREIGN-METADATA
 * CHANGELOG: v1.3.1-LEGAL-PRACTICE-COMMERCE-SEPARATION-SOVEREIGN-METADATA completes artifact ownership and privacy posture without changing certificate behavior.
 * CHANGELOG: v1.3.0-LEGAL-PRACTICE-COMMERCE-SEPARATION-CERT — certifies current Python Legal workspace fixtures, Sheriff/Deputy routes and branding while enforcing tenant-owner-only commercial context.
 * AUTHORITY: Browser presentation certification only.
 * EPITOME: Certifies shared Sheriff/Deputy Legal OS chrome plus exact
 *          server-result-driven commercial presentation states without
 *          browser-owned IAM, plan, tenant, payment or settlement authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardEnterpriseWorkspaceShell.test.jsx
 * COLLABORATION / OWNERSHIP: Enterprise Legal workspace shell and client certificate owners.
 * CERTIFICATION / UPDATE DATE: 2026-11-10
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic principal, tenant and workspace fixtures only.
 * CHANGELOG: 2026-10-16 v1.1.0-LEGAL-COMMERCIAL-CONTEXT-PRESENTATION-CERT
 *            adds authorized, denied and unavailable commercial presentation
 *            proofs and preserves authenticated tenant branding as an
 *            independent identity source.
 * TENANT BOUNDARY: authenticated tenant branding and commercial projection
 *                  remain separate server-derived presentation authorities.
 * AUTHORITY BOUNDARY: role labels, browser permissions and navigation state
 *                     never grant commercial or Legal Operations authority.
 * FINANCIAL AUTHORITY BOUNDARY: No financial authority is created by client presentation.
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
  getLegalPracticeWorkspace: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
  syncPendingDeputyLocationEvidence: vi.fn(),
  brandingHook: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'enterprise-specialist-shell-cert',
  getSheriffOperationalQueues: mocks.getSheriffOperationalQueues,
  getDeputyPersonalActiveWork: mocks.getDeputyPersonalActiveWork,
  getDeputyFieldCapabilities: mocks.getDeputyFieldCapabilities,
  getLegalCommercialContext: mocks.getLegalCommercialContext,
  getLegalPracticeWorkspace: mocks.getLegalPracticeWorkspace,
  getLegalConflictScreenings: mocks.getLegalConflictScreenings,
  syncPendingDeputyLocationEvidence: mocks.syncPendingDeputyLocationEvidence,
  getLegalClientMatters: vi.fn(),
  getLegalClientAcceptanceInstruments: vi.fn(),
  createLegalClientAcceptanceContext: vi.fn(),
  getLegalClientAcceptanceContent: vi.fn(),
  confirmLegalClientAcceptance: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
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

const emptyPracticeWorkspace = Object.freeze({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: Object.freeze({
    matters_total: 0, matters_open: 0, matters_closed: 0,
    instructions_total: 0, instructions_registered: 0, instructions_accepted: 0,
    instructions_closed: 0, instructions_cancelled: 0, documents_total: 0,
    documents_registered: 0, documents_received: 0, documents_allocated: 0,
    documents_returned: 0, attempts_total: 0, attempts_allocated: 0,
    attempts_attempted: 0, attempts_completed: 0, attempts_not_completed: 0,
    attempts_cancelled: 0, executions_total: 0, executions_completed: 0,
    executions_not_completed: 0, returns_total: 0,
  }),
  matters: Object.freeze([]), instructions: Object.freeze([]),
  documents: Object.freeze([]), attempts: Object.freeze([]),
  executions: Object.freeze([]), returns: Object.freeze([]),
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
  mocks.getLegalPracticeWorkspace.mockReset();
  mocks.getLegalPracticeWorkspace.mockResolvedValue(emptyPracticeWorkspace);
  mocks.getLegalConflictScreenings.mockReset();
  mocks.getLegalConflictScreenings.mockResolvedValue({
    schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
    version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
    tenantId: 'tenant-law',
    visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
    screenings: [],
  });
  mocks.syncPendingDeputyLocationEvidence.mockReset();
  mocks.syncPendingDeputyLocationEvidence.mockResolvedValue({ syncedAttemptIds: [] });
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
      container.querySelector('[data-legal-workspace-viewport="PROCESS_SERVICE"]'),
    ).not.toBeNull();
  });

  it('narrows Legal Practice actions to the authoritative permission projection', async () => {
    mocks.authState.user = {
      ...mocks.authState.user,
      role: 'tenant_legal_partner',
      legalPermissionsAuthoritative: true,
      permissions: [],
    };
    render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    expect(mocks.getSheriffOperationalQueues).not.toHaveBeenCalled();
    await waitFor(() =>
      expect(mocks.getLegalPracticeWorkspace).toHaveBeenCalledTimes(1),
    );

    expect(mocks.getLegalCommercialContext).not.toHaveBeenCalled();
    expect(document.querySelector('[data-commercial-context-state]')).toBeNull();
    expect(
      screen.getByRole('navigation', {
        name: 'Legal practice workspace navigation',
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Matters' })).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'New Instruction' }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Conflict Reviews' }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Finance Evidence' }),
    ).not.toBeInTheDocument();
  });

  it('routes Sheriff to Process Service and Deputy to My Work', async () => {
    const sheriff = render(<LegalDashboard roleView="SHERIFF" />);

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );
    expect(
      sheriff.container.querySelector(
        '[data-legal-workspace-viewport="PROCESS_SERVICE"]',
      ),
    ).not.toBeNull();
    expect(
      screen.queryByRole('button', { name: /^My Work$/i }),
    ).not.toBeInTheDocument();
    sheriff.unmount();

    mocks.authState.user = {
      ...mocks.authState.user,
      id: 'principal-deputy',
      email: 'deputy.operator@example.test',
      role: 'tenant_deputy',
    };
    mocks.getDeputyPersonalActiveWork.mockResolvedValue({
      tenantId: 'tenant-law',
      visibility: 'DEPUTY_PERSONAL_ACTIVE_WORK',
      deputyId: 'principal-deputy',
      activeAttempts: [],
    });
    render(<LegalDashboard roleView="DEPUTY" />);

    await waitFor(() =>
      expect(mocks.getDeputyPersonalActiveWork).toHaveBeenCalled(),
    );
    expect(
      document.querySelector('[data-legal-workspace-viewport="MY_WORK"]'),
    ).not.toBeNull();
  });
  it('keeps tenant-owner commercial details out of Legal Practice', async () => {
    mocks.authState.user = { ...mocks.authState.user, role: 'tenant_legal_partner' };
    const { container } = render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    await waitFor(() =>
      expect(mocks.getLegalPracticeWorkspace).toHaveBeenCalledTimes(1),
    );

    expect(mocks.getLegalCommercialContext).not.toHaveBeenCalled();
    expect(container.querySelector('[data-commercial-context-state]')).toBeNull();
    expect(screen.queryByText('Certified Legal Plan')).not.toBeInTheDocument();
    expect(screen.queryByText('WILSYSUB-CERT-1')).not.toBeInTheDocument();
  });

  it('keeps authenticated tenant branding independent of owner commercial context', async () => {
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
    mocks.authState.user = { ...mocks.authState.user, role: 'tenant_legal_partner' };
    const { container } = render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    await waitFor(() =>
      expect(mocks.getLegalPracticeWorkspace).toHaveBeenCalledTimes(1),
    );

    expect(container.querySelector('[data-wilsy-tenant-branding="authenticated"]')).not.toBeNull();
    expect(screen.getByText(/Fortune Legal Identity/)).toBeInTheDocument();
    expect(mocks.getLegalCommercialContext).not.toHaveBeenCalled();
    expect(container.querySelector('[data-commercial-context-state]')).toBeNull();
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
 * VERSION: v1.3.1-LEGAL-PRACTICE-COMMERCE-SEPARATION-SOVEREIGN-METADATA
 * AUTHORITY BOUNDARY: browser presentation certificate only; server response remains authoritative
 * TENANT POSTURE: authenticated tenant branding and commercial context remain separate server-derived projections
 * FAIL-CLOSED POSTURE: denied or unavailable commercial evidence never reveals or fabricates plan/subscription/value truth
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
