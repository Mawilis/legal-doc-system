/**
 * TITLE: WILSY OS Legal Practice G68 Denial Presentation Certificate
 * VERSION: v1.0.0-G68-LEGAL-DASHBOARD-503-PRESENTATION
 * AUTHORITY: Browser presentation evidence only; Python EOS owns disclosure.
 * EPITOME: Proves the authenticated Legal Practice dashboard displays the exact
 *          G68 non-disclosing 503 and never substitutes empty/synthetic matter data.
 * SECURITY: Synthetic principal/tenant and mocked HTTP responses only.
 * TENANT BOUNDARY: The authenticated Legal Practice tenant is presentation context.
 * AUTHORITY BOUNDARY: This test does not ratify G64 or grant G68 confidentiality.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getLegalPracticeWorkspace, getLegalConflictScreenings } = vi.hoisted(() => ({
  getLegalPracticeWorkspace: vi.fn(),
  getLegalConflictScreenings: vi.fn(),
}));

vi.mock('../../src/services/legalOperationsService.js', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    getLegalPracticeWorkspace,
    getLegalConflictScreenings,
  };
});

vi.mock('../../src/contexts/authContext.jsx', () => ({
  useAuth: () => ({
    user: {
      id: 'SYNTHETIC-LEGAL-PARTNER',
      email: 'partner@example.test',
      role: 'tenant_legal_partner',
      tenantId: 'TENANT-G68-BROWSER',
      permissions: [
        'legal_operations:instruction:write',
        'legal_operations:return:write',
        'legal_operations:productive_work:read',
      ],
      legalPermissionsAuthoritative: true,
    },
    tenant: {
      tenantId: 'TENANT-G68-BROWSER',
      name: 'Synthetic Legal Practice',
      status: 'ACTIVE',
    },
  }),
}));

vi.mock('../../src/contexts/tenantContext.jsx', () => ({
  useTenants: () => ({
    activeTenant: {
      tenantId: 'TENANT-G68-BROWSER',
      name: 'Synthetic Legal Practice',
      status: 'ACTIVE',
    },
  }),
}));

vi.mock('../../src/hooks/useAuthenticatedTenantBrandingAsset.js', () => ({
  useAuthenticatedTenantBrandingAsset: () => ({ assetUrl: null, loading: false, error: null }),
}));

vi.mock('../../src/components/os/WilsyOSDashboardChrome.jsx', () => ({
  default: ({ children }) => <>{children}</>,
}));

vi.mock('../../src/components/account/WilsyAccountCommandCenter.jsx', () => ({
  default: () => null,
}));

import LegalDashboard from '../../src/components/industry/LegalDashboard.jsx';

describe('Legal Practice dashboard G68 denial presentation', () => {
  beforeEach(() => {
    getLegalPracticeWorkspace.mockReset();
    getLegalConflictScreenings.mockReset();
    getLegalConflictScreenings.mockResolvedValue({});
  });

  it('shows the exact confidentiality-authority denial and renders no fallback matter content', async () => {
    getLegalPracticeWorkspace.mockRejectedValueOnce({
      response: {
        status: 503,
        data: {
          detail: 'LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE',
        },
      },
    });

    render(<LegalDashboard roleView="LEGAL_PARTNER" />);

    expect(await screen.findByText('EVIDENCE_UNAVAILABLE')).toBeInTheDocument();
    expect(
      await screen.findByText(
        'LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE',
      ),
    ).toBeInTheDocument();

    await waitFor(() => expect(getLegalPracticeWorkspace).toHaveBeenCalledTimes(1));
    expect(getLegalConflictScreenings).toHaveBeenCalledTimes(1);
    expect(screen.queryByText(/CASE-2026-/)).not.toBeInTheDocument();
    expect(screen.queryByText(/matter-1/)).not.toBeInTheDocument();
    expect(screen.queryByText(/No current matters/i)).not.toBeInTheDocument();
  });
});
