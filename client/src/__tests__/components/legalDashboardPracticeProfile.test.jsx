/**
 * WILSY OS — LEGAL PRACTICE PROFILE PRESENTATION CERTIFICATE
 * VERSION: v1.0.1-L8-8M-R2-CONFLICT-REVIEW-READ-COMPAT-CERT
 * AUTHORITY: Browser presentation/wiring evidence only.
 * EPITOME: Certifies that Legal Practice workspaces consume only the bounded
 *          descriptive tenant profile projected by authenticated Python EOS
 *          workspace-bootstrap and do not manufacture or expose operating-model,
 *          commercial, compliance or financial authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardPracticeProfile.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * CHANGELOG: 2026-09-25 v1.0.1-L8-8M-R2-CONFLICT-REVIEW-READ-COMPAT-CERT updates the presentation fixture to provide the certified conflict-screening read projection required by the Legal Practice dashboard lifecycle; profile assertions and authority boundaries remain unchanged.
 * TENANT BOUNDARY: Synthetic same-tenant fixtures only.
 * AUTHORITY BOUNDARY: Profile presentation is descriptive only; Python EOS owns
 *                     tenant and authorization truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 * FAIL-CLOSED DECLARATION: Unsupported tenant fields are never rendered as Legal
 *                          practice authority.
 */

import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const {
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalConflictScreenings,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
} = vi.hoisted(() => ({
  generateLegalReturnOfService: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  registerLegalIntake: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.6.0-L8-7D15-MATTER-WORKSPACE-COMPATIBILITY',
  generateLegalReturnOfService,
  getDeputyFieldCapabilities,
  getDeputyPersonalActiveWork,
  getLegalClientMatters,
  getLegalConflictScreenings,
  getLegalFinanceEvidence,
  getLegalPracticeWorkspace,
  getSheriffOperationalQueues,
  recordDeputyFieldOutcome,
  registerLegalIntake,
  transitionDeputyFieldAttempt,
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => ({
    user: {
      id: 'principal-partner',
      email: 'partner@example.test',
      role: 'tenant_legal_partner',
      tenantId: 'tenant-law',
    },
    tenant: {
      tenantId: 'tenant-law',
      name: 'Canonical Legal Practice',
      legalName: 'Canonical Legal Practice (Pty) Ltd',
      alias: 'canonical-law',
      industry: 'Legal Services',
      region: 'ZA',
      sector: 'Law',
      status: 'ACTIVE',
    },
  }),
}));

vi.mock('../../contexts/tenantContext', () => ({
  useTenants: () => ({
    activeTenant: {
      tenantId: 'tenant-law',
      name: 'Canonical Legal Practice',
      status: 'ACTIVE',
    },
    tenants: [],
  }),
}));

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const workspace = () => ({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API',
  tenantId: 'tenant-law',
  visibility: 'LEGAL_PRACTICE_WORKSPACE',
  summary: {
    matters_total: 0,
    matters_open: 0,
    matters_closed: 0,
    instructions_total: 0,
    instructions_registered: 0,
    instructions_accepted: 0,
    instructions_closed: 0,
    instructions_cancelled: 0,
    documents_total: 0,
    documents_registered: 0,
    documents_received: 0,
    documents_allocated: 0,
    documents_returned: 0,
    attempts_total: 0,
    attempts_allocated: 0,
    attempts_attempted: 0,
    attempts_completed: 0,
    attempts_not_completed: 0,
    attempts_cancelled: 0,
    executions_total: 0,
    executions_completed: 0,
    executions_not_completed: 0,
    returns_total: 0,
  },
  matters: [],
  instructions: [],
  documents: [],
  attempts: [],
  executions: [],
  returns: [],
});

describe('D19B canonical Legal practice profile presentation', () => {
beforeEach(() => {
  vi.clearAllMocks();
  getLegalConflictScreenings.mockResolvedValue({
    schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
    version: 'v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API',
    tenantId: 'tenant-law',
    visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
    screenings: [],
  });
});

  it('renders only the bounded descriptive practice profile from authenticated tenant truth', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(workspace());

    render(
      <LegalDashboard
        roleView="LEGAL_PARTNER"
        user={{
          id: 'principal-partner',
          email: 'partner@example.test',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
        tenantConfig={{
          tenantId: 'tenant-law',
          name: 'Canonical Legal Practice',
          legalName: 'Canonical Legal Practice (Pty) Ltd',
          alias: 'canonical-law',
          industry: 'Legal Services',
          region: 'ZA',
          sector: 'Law',
          plan: 'FORBIDDEN-PLAN',
          subscriptionTier: 'FORBIDDEN-SUBSCRIPTION',
          taxId: 'FORBIDDEN-TAX-ID',
          contactEmail: 'forbidden@example.invalid',
          complianceFlags: { certified: true },
          verified: true,
          operatingModel: 'FORBIDDEN-OPERATING-MODEL',
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');
    const profile = screen.getByLabelText('Canonical Legal practice profile');

    expect(within(profile).getByText('Authenticated tenant profile')).toBeInTheDocument();
    expect(within(profile).getByText('Canonical Legal Practice (Pty) Ltd')).toBeInTheDocument();
    expect(within(profile).getByText('canonical-law')).toBeInTheDocument();
    expect(within(profile).getByText('Legal Services')).toBeInTheDocument();
    expect(within(profile).getByText('ZA')).toBeInTheDocument();
    expect(within(profile).getByText('Law')).toBeInTheDocument();
    expect(within(profile).getByText(/do not create operating-model, role, permission, plan, subscription, branding, billing or financial authority/i)).toBeInTheDocument();

    for (const forbidden of [
      'FORBIDDEN-PLAN',
      'FORBIDDEN-SUBSCRIPTION',
      'FORBIDDEN-TAX-ID',
      'forbidden@example.invalid',
      'FORBIDDEN-OPERATING-MODEL',
    ]) {
      expect(screen.queryByText(forbidden)).not.toBeInTheDocument();
    }
    expect(screen.queryByText('certified')).not.toBeInTheDocument();
    expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(1);
  });

  it('does not manufacture missing optional profile fields', async () => {
    getLegalPracticeWorkspace.mockResolvedValueOnce(workspace());

    render(
      <LegalDashboard
        roleView="LEGAL_ATTORNEY"
        user={{
          id: 'principal-attorney',
          email: 'attorney@example.test',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
        tenantConfig={{
          tenantId: 'tenant-law',
          legalName: 'Sparse Legal Practice',
        }}
      />,
    );

    await screen.findByText('Legal Operations Command Center');
    const profile = screen.getByLabelText('Canonical Legal practice profile');
    expect(within(profile).getByText('Sparse Legal Practice')).toBeInTheDocument();
    expect(within(profile).queryByText('Practice alias')).not.toBeInTheDocument();
    expect(within(profile).queryByText('Industry')).not.toBeInTheDocument();
    expect(within(profile).queryByText('Region')).not.toBeInTheDocument();
    expect(within(profile).queryByText('Sector')).not.toBeInTheDocument();
  });

  it('keeps the practice-profile panel out of the Legal Finance workspace', async () => {
    render(
      <LegalDashboard
        roleView="LEGAL_FINANCE"
        user={{
          id: 'principal-finance',
          email: 'finance@example.test',
          permissions: [],
          legalPermissionsAuthoritative: true,
        }}
        tenantConfig={{
          tenantId: 'tenant-law',
          legalName: 'Canonical Legal Practice (Pty) Ltd',
          alias: 'canonical-law',
          industry: 'Legal Services',
          region: 'ZA',
          sector: 'Law',
        }}
      />,
    );

    expect(await screen.findByText('Legal Finance Evidence')).toBeInTheDocument();
    expect(screen.queryByLabelText('Canonical Legal practice profile')).not.toBeInTheDocument();
    expect(getLegalPracticeWorkspace).not.toHaveBeenCalled();
  });
});

/**
 * ARTIFACT: legalDashboardPracticeProfile.test.jsx
 * VERSION: v1.0.1-L8-8M-R2-CONFLICT-REVIEW-READ-COMPAT-CERT
 * AUTHORITY BOUNDARY: browser descriptive presentation only
 * TENANT POSTURE: exact authenticated tenant projection only
 * FAIL-CLOSED POSTURE: unsupported profile fields are absent rather than inferred
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
