/**
 * WILSY OS — D21B13 LEGAL AUTHENTICATED BRANDING PRESENTATION CERTIFICATE
 * VERSION: v1.0.0-D21B13-LEGAL-AUTHENTICATED-BRANDING-PRESENTATION-CERT
 * AUTHORITY: Browser presentation/wiring evidence only.
 * EPITOME: Proves Sheriff/Deputy custom Legal chrome consumes only the D21B8
 *          authenticated branding descriptor through D21B12, ignores forged
 *          tenantConfig branding paths, and falls back to tenant initials.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/legalDashboardBrandingPresentation.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * TENANT BOUNDARY: Branding descriptor originates only from mocked AuthContext.
 * AUTHORITY BOUNDARY: Presentation evidence only; no IAM/legal/financial truth.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  getSheriffOperationalQueues: vi.fn(),
  getDeputyPersonalActiveWork: vi.fn(),
  getDeputyFieldCapabilities: vi.fn(),
  getLegalClientMatters: vi.fn(),
  getLegalFinanceEvidence: vi.fn(),
  getLegalPracticeWorkspace: vi.fn(),
  registerLegalIntake: vi.fn(),
  generateLegalReturnOfService: vi.fn(),
  recordDeputyFieldOutcome: vi.fn(),
  transitionDeputyFieldAttempt: vi.fn(),
  brandingHook: vi.fn(),
  authState: {
    user: {
      id: 'principal-law',
      email: 'operator@example.test',
      role: 'tenant_legal_sheriff',
      tenantId: 'tenant-law',
    },
    tenant: null,
  },
}));

vi.mock('../../services/legalOperationsService.js', () => ({
  LEGAL_OPERATIONS_CLIENT_VERSION: 'v-d21b13-cert',
  getSheriffOperationalQueues: mocks.getSheriffOperationalQueues,
  getDeputyPersonalActiveWork: mocks.getDeputyPersonalActiveWork,
  getDeputyFieldCapabilities: mocks.getDeputyFieldCapabilities,
  getLegalClientMatters: mocks.getLegalClientMatters,
  getLegalFinanceEvidence: mocks.getLegalFinanceEvidence,
  getLegalPracticeWorkspace: mocks.getLegalPracticeWorkspace,
  registerLegalIntake: mocks.registerLegalIntake,
  generateLegalReturnOfService: mocks.generateLegalReturnOfService,
  recordDeputyFieldOutcome: mocks.recordDeputyFieldOutcome,
  transitionDeputyFieldAttempt: mocks.transitionDeputyFieldAttempt,
}));

vi.mock('../../contexts/authContext', () => ({
  useAuth: () => mocks.authState,
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

import LegalDashboard from '../../components/industry/LegalDashboard.jsx';

const descriptor = Object.freeze({
  reference: 'asset:tenant-law:logo:primary',
  contentFingerprint: 'a'.repeat(128),
  mediaType: 'image/png',
  kind: 'LOGO',
});

const brandingTenant = () => ({
  tenantId: 'tenant-law',
  name: 'Acme Legal',
  legalName: 'Acme Legal Inc.',
  status: 'ACTIVE',
  branding: {
    tenantId: 'tenant-law',
    profileId: 'profile-1',
    profileLabel: 'Acme Institutional Brand',
    brandingTier: 'TENANT_BRANDING_INSTITUTIONAL',
    platformTrustMarkRequired: true,
    logo: descriptor,
    favicon: null,
  },
});

const sheriffQueues = () => ({
  tenantId: 'tenant-law',
  visibility: 'SHERIFF_OPERATIONAL_QUEUE',
  officeReceipt: [],
  deputyAssignment: [],
  activeAttempts: [],
});

beforeEach(() => {
  Object.assign(mocks.authState, {
    user: {
      id: 'principal-law',
      email: 'operator@example.test',
      role: 'tenant_legal_sheriff',
      tenantId: 'tenant-law',
    },
    tenant: brandingTenant(),
  });
  mocks.getSheriffOperationalQueues.mockReset();
  mocks.getSheriffOperationalQueues.mockResolvedValue(sheriffQueues());
  mocks.getDeputyPersonalActiveWork.mockReset();
  mocks.getDeputyFieldCapabilities.mockReset();
  mocks.getLegalClientMatters.mockReset();
  mocks.getLegalFinanceEvidence.mockReset();
  mocks.getLegalPracticeWorkspace.mockReset();
  mocks.registerLegalIntake.mockReset();
  mocks.generateLegalReturnOfService.mockReset();
  mocks.recordDeputyFieldOutcome.mockReset();
  mocks.transitionDeputyFieldAttempt.mockReset();
  mocks.brandingHook.mockReset();
});

describe('D21B13 Legal authenticated tenant branding presentation', () => {
  it('passes only the AuthContext branding descriptor to D21B12 and renders its blob URL', async () => {
    mocks.brandingHook.mockReturnValue({
      objectUrl: 'blob:http://localhost/legal-logo',
      status: 'READY',
      errorCode: null,
    });

    const { container } = render(
      <LegalDashboard
        roleView="SHERIFF"
        tenantConfig={{
          tenantId: 'tenant-law',
          logo: 'https://evil.invalid/forged.png',
          branding: {
            logo: {
              reference: 'asset:forged:logo:x',
            },
          },
        }}
      />,
    );

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );

    expect(mocks.brandingHook).toHaveBeenCalledWith(descriptor);
    const mark = container.querySelector('[data-wilsy-legal-tenant-logo]');
    expect(mark).not.toBeNull();
    expect(mark.getAttribute('data-wilsy-legal-tenant-logo')).toBe('ready');

    const image = mark.querySelector('img');
    expect(image).not.toBeNull();
    expect(image.getAttribute('src')).toBe('blob:http://localhost/legal-logo');
    expect(image.getAttribute('src')).not.toContain('evil.invalid');
    expect(screen.getByLabelText('WILSY Legal OS platform mark')).toBeInTheDocument();
  });

  it('uses initials when authenticated branding is absent and never promotes tenantConfig logo', async () => {
    mocks.authState.tenant = {
      tenantId: 'tenant-law',
      name: 'Acme Legal',
      status: 'ACTIVE',
      branding: null,
    };
    mocks.brandingHook.mockReturnValue({
      objectUrl: null,
      status: 'ABSENT',
      errorCode: null,
    });

    const { container } = render(
      <LegalDashboard
        roleView="SHERIFF"
        tenantConfig={{
          tenantId: 'tenant-law',
          logoUrl: 'https://evil.invalid/legacy.png',
        }}
      />,
    );

    await waitFor(() =>
      expect(mocks.getSheriffOperationalQueues).toHaveBeenCalledTimes(1),
    );

    expect(mocks.brandingHook).toHaveBeenCalledWith(null);
    const mark = container.querySelector('[data-wilsy-legal-tenant-logo]');
    expect(mark.querySelector('img')).toBeNull();
    expect(mark).toHaveTextContent('AL');
    expect(container.innerHTML).not.toContain('evil.invalid');
  });

  it('keeps practice mode on shared chrome without a duplicate parent logo fetch', async () => {
    mocks.brandingHook.mockReturnValue({
      objectUrl: null,
      status: 'ABSENT',
      errorCode: null,
    });
    mocks.getLegalPracticeWorkspace.mockResolvedValue({
      schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2',
      version: 'v-d21b13-cert',
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
        returns_total: 0,
        returns_completed: 0,
        billable_total: 0,
        invoice_ready_total: 0,
      },
      matters: [],
      instructions: [],
      documents: [],
      attempts: [],
      executions: [],
      returns: [],
    });

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    await waitFor(() =>
      expect(mocks.getLegalPracticeWorkspace).toHaveBeenCalledTimes(1),
    );

    expect(mocks.brandingHook).toHaveBeenCalledWith(null);
  });
});

// ARTIFACT: legalDashboardBrandingPresentation.test.jsx
// VERSION: v1.0.0-D21B13-LEGAL-AUTHENTICATED-BRANDING-PRESENTATION-CERT
// AUTHORITY BOUNDARY: Legal browser branding presentation certificate only
// TENANT POSTURE: only AuthContext descriptor can reach D21B12
// FAIL-CLOSED POSTURE: forged/absent branding falls back to initials, never legacy URL
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
