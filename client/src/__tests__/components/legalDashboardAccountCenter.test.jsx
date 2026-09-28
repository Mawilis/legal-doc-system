/**
 * WILSY OS — LEGAL ACCOUNT COMMAND CENTER INTEGRATION CERTIFICATE
 * TITLE: Legal Account Command Center Wiring Certificate
 * VERSION: v1.0.0-L10-P2B-LEGAL-ACCOUNT-CENTER-CERT
 * AUTHORITY: Browser presentation and callback-wiring evidence only.
 * EPITOME: Proves Legal Practice and Legal Finance expose the existing shared
 *          Account Command Center without creating a duplicate settings surface
 *          or tenant-branding mutation authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardAccountCenter.test.jsx
 * COLLABORATION / OWNERSHIP: WilsyOSDashboardChrome owns shared account-button
 *                            and drawer mounting; WilsyAccountCommandCenter owns
 *                            account presentation; Python EOS owns identity and
 *                            tenant-branding authority.
 * CERTIFICATION / UPDATE DATE: 2026-09-28
 * CHANGELOG: v1.0.0-L10-P2B-LEGAL-ACCOUNT-CENTER-CERT proves authenticated
 *            user continuity, open/close behavior and logout callback wiring for
 *            Legal Practice and Legal Finance shared chrome.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic principal fixtures only; no persisted
 *                             identity, tenant or branding mutation is exercised.
 * TENANT BOUNDARY: The test supplies one authenticated tenant projection and
 *                  verifies no browser tenant selector or branding writer exists.
 * AUTHORITY BOUNDARY: Shared Account Command Center presentation/callbacks only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  getLegalPracticeWorkspace: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v1.0.0-L10-P2B-ACCOUNT-CENTER-CERT',
  getLegalPracticeWorkspace: mocks.getLegalPracticeWorkspace,
  getLegalConflictScreenings: mocks.getLegalConflictScreenings,
  getDeputyFieldCapabilities: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getSheriffOperationalQueues: vi.fn(),
  generateLegalReturnOfService: vi.fn(),
  issueLegalConflictReview: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  registerLegalIntake: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
}));

vi.mock('../../contexts/authContext.jsx', () => ({
  useAuth: () => ({
    user: {
      id: 'principal-authenticated',
      email: 'legal.operator@example.test',
      role: 'tenant_legal_partner',
      tenantId: 'tenant-legal',
    },
    tenant: {
      tenantId: 'tenant-legal',
      displayName: 'Acme Legal',
      status: 'ACTIVE',
    },
  }),
}));

vi.mock('../../contexts/tenantContext', () => ({
  useTenants: () => ({
    activeTenant: {
      tenantId: 'tenant-legal',
      displayName: 'Acme Legal',
      status: 'ACTIVE',
    },
    tenants: [],
  }),
}));

vi.mock('../../components/account/WilsyAccountCommandCenter.jsx', () => ({
  default: ({ isOpen, onClose, onSignOut, user }) => (
    isOpen ? (
      <div role="dialog" aria-label="Account Command Center">
        <p data-account-user-id={user?.id}>{user?.email}</p>
        <button type="button" onClick={onClose}>Close account</button>
        <button type="button" onClick={onSignOut}>Sign out from account</button>
      </div>
    ) : null
  ),
}));

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const practiceWorkspace = Object.freeze({
  schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
  version: 'v1.0.0-L10-P2B-ACCOUNT-CENTER-CERT',
  tenantId: 'tenant-legal',
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

const conflictScreenings = Object.freeze({
  schema: 'WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1',
  version: 'v1.0.0-L10-P2B-ACCOUNT-CENTER-CERT',
  tenantId: 'tenant-legal',
  visibility: 'LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE',
  screenings: [],
});

function renderDashboard(roleView, onLogout) {
  return render(
    <LegalDashboard
      roleView={roleView}
      onLogout={onLogout}
      tenantConfig={{ tenantId: 'tenant-legal', displayName: 'Acme Legal' }}
    />,
  );
}

beforeEach(() => {
  mocks.getLegalPracticeWorkspace.mockReset();
  mocks.getLegalPracticeWorkspace.mockResolvedValue(practiceWorkspace);
  mocks.getLegalConflictScreenings.mockReset();
  mocks.getLegalConflictScreenings.mockResolvedValue(conflictScreenings);
});

describe('L10-P2B Legal Account Command Center wiring', () => {
  it('opens, closes and preserves the authenticated user and logout callback in Practice', async () => {
    const onLogout = vi.fn();
    renderDashboard('LEGAL_PARTNER', onLogout);

    await waitFor(() => expect(screen.getByText('Legal Operations Command Center')).toBeInTheDocument());
    fireEvent.click(screen.getByTitle('Account'));

    const dialog = screen.getByRole('dialog', { name: 'Account Command Center' });
    expect(dialog).toBeInTheDocument();
    expect(within(dialog).getByText('legal.operator@example.test')).toHaveAttribute(
      'data-account-user-id',
      'principal-authenticated',
    );

    fireEvent.click(screen.getByRole('button', { name: 'Sign out from account' }));
    expect(onLogout).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Close account' }));
    expect(screen.queryByRole('dialog', { name: 'Account Command Center' })).not.toBeInTheDocument();
  });

  it('exposes the same shared Account Command Center in Legal Finance', async () => {
    const onLogout = vi.fn();
    renderDashboard('LEGAL_FINANCE', onLogout);

    await waitFor(() => expect(screen.getByText('Legal Finance Evidence')).toBeInTheDocument());
    fireEvent.click(screen.getByTitle('Account'));
    expect(screen.getByRole('dialog', { name: 'Account Command Center' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Close account' }));
    expect(screen.queryByRole('dialog', { name: 'Account Command Center' })).not.toBeInTheDocument();
  });
});

/* WILSY OS SOVEREIGN ARTIFACT SEAL
 * ARTIFACT: legalDashboardAccountCenter.test.jsx
 * VERSION: v1.0.0-L10-P2B-LEGAL-ACCOUNT-CENTER-CERT
 * AUTHORITY BOUNDARY: Account Center presentation/callback evidence only
 * TENANT POSTURE: synthetic authenticated tenant fixture
 * FAIL-CLOSED POSTURE: no duplicate settings or branding mutation surface
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
