/**
 * TITLE: WILSY OS Authenticated Legal Workspace Journey Certificate
 * VERSION: v1.0.0-AUTH-BOOTSTRAP-LEGAL-BOUNDARY-JOURNEY
 * AUTHORITY: Client integration evidence only; Python EOS remains authoritative.
 * EPITOME: Exercises persisted-session revalidation, exact authenticated tenant
 *          handoff, and the server-owned legal-acceptance barrier before runtime.
 * SECURITY: Synthetic identities and tokens only. No live account or credential.
 * TENANT BOUNDARY: The exact READY workspace-bootstrap tenant must match the
 *                  authenticated principal before the Legal runtime is mounted.
 * AUTHORITY BOUNDARY: This test creates no identity, membership, role, legal
 *                     acceptance, confidentiality clearance, or G68 authority.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api, sovereignClient, setActiveTenantTransportId } = vi.hoisted(() => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    defaults: { headers: { common: {} } },
  },
  sovereignClient: {
    get: vi.fn(),
  },
  setActiveTenantTransportId: vi.fn(),
}));

vi.mock('../../src/services/api', () => ({
  default: api,
  setActiveTenantTransportId,
}));
vi.mock('../../src/utils/sovereignClient', () => ({ default: sovereignClient }));

import { AuthProvider } from '../../src/contexts/authContext.jsx';
import { AuthenticatedTenantBoundary } from '../../src/App.jsx';

const tenantId = 'TENANT-LEGAL-JOURNEY';
const userId = 'PRINCIPAL-LEGAL-JOURNEY';
const runtime = <main data-testid="authenticated-legal-runtime">Authenticated Legal workspace shell</main>;

const readyWorkspace = {
  status: 'READY',
  user: {
    id: userId,
    email: 'partner@example.test',
    firstName: 'Canonical',
    lastName: 'Partner',
  },
  workspace: {
    tenantId,
    businessRole: 'tenant_legal_partner',
    workspaceId: 'LEGAL_PRACTICE',
    workspaceContractVersion: 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION',
    membershipRevision: 4,
    businessRoleRevision: 9,
    legalPermissions: [
      'legal_operations:instruction:write',
      'legal_operations:return:write',
      'legal_operations:productive_work:read',
    ],
    branding: null,
    tenant: {
      tenantId,
      name: 'Canonical Legal Practice',
      legalName: 'Canonical Legal Practice (Pty) Ltd',
      status: 'ACTIVE',
    },
  },
};

describe('authenticated Legal workspace journey', () => {
  beforeEach(() => {
    const values = new Map([
      ['wilsy_auth_token', 'synthetic-session-token'],
      ['token', 'synthetic-session-token'],
      ['wilsy_sovereign_user', JSON.stringify({ id: userId, email: 'partner@example.test' })],
    ]);
    const storage = {
      getItem: (key) => values.get(key) || null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: (key) => values.delete(key),
      clear: () => values.clear(),
    };
    Object.defineProperty(window, 'localStorage', { configurable: true, value: storage });
    Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
    api.get.mockReset();
    api.post.mockReset();
    delete api.defaults.headers.common.Authorization;
    delete api.defaults.headers.common['x-tenant-id'];
    sovereignClient.get.mockReset().mockResolvedValue({ data: {} });
    setActiveTenantTransportId.mockReset();
  });

  it('revalidates the session and exact tenant before releasing the Legal workspace after server COMPLETE', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/auth/workspace-bootstrap') return Promise.resolve({ data: readyWorkspace });
      if (path === '/legal-acceptance/status') {
        return Promise.resolve({ data: { status: 'COMPLETE', tenantId, documents: [] } });
      }
      throw new Error(`Unexpected API read: ${path}`);
    });

    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <AuthenticatedTenantBoundary runtime={runtime} />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByTestId('authenticated-legal-runtime')).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/auth/workspace-bootstrap', {
      headers: { Authorization: 'Bearer synthetic-session-token' },
    });
    expect(api.get).toHaveBeenCalledWith('/legal-acceptance/status');
    expect(api.defaults.headers.common.Authorization).toBe('Bearer synthetic-session-token');
    expect(setActiveTenantTransportId).toHaveBeenCalledWith(tenantId);
    expect(sovereignClient.get).toHaveBeenCalledWith('/billing/dunning/state', {
      headers: { 'X-Tenant-ID': tenantId },
    });
  });

  it('does not mount the Legal workspace while server legal acceptance is incomplete', async () => {
    api.get.mockImplementation((path) => {
      if (path === '/auth/workspace-bootstrap') return Promise.resolve({ data: readyWorkspace });
      if (path === '/legal-acceptance/status') {
        return Promise.resolve({
          data: {
            status: 'USER_TERMS_REQUIRED',
            tenantId,
            documents: [{
              agreementType: 'USER_TERMS',
              documentId: 'terms-v1',
              version: '1.0.0-APPROVED',
              sha3_512: 'b'.repeat(128),
              title: 'WILSY OS User Terms',
              locale: 'en-ZA',
              effectiveFrom: '2026-09-20T00:00:00Z',
              content: 'Synthetic server-issued terms for the integration test.',
              accepted: false,
            }],
          },
        });
      }
      throw new Error(`Unexpected API read: ${path}`);
    });

    render(
      <MemoryRouter initialEntries={['/']}>
        <AuthProvider>
          <AuthenticatedTenantBoundary runtime={runtime} />
        </AuthProvider>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.queryByTestId('authenticated-legal-runtime')).not.toBeInTheDocument());
    expect(await screen.findByRole("table", { name: "Required legal document records" })).toBeInTheDocument();
    expect(screen.getByText("LEGAL ADMISSION CONTROL")).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/auth/workspace-bootstrap', {
      headers: { Authorization: 'Bearer synthetic-session-token' },
    });
    expect(api.get).toHaveBeenCalledWith('/legal-acceptance/status');
  });
});
