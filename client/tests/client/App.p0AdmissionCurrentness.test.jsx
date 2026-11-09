/**
 * TITLE: WILSY OS Single-Shell Platform-Use Admission Currentness Certificate
 * VERSION: v1.0.0-SESSION-SCOPED-HEADQUARTERS-ENTRY
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Keeps platform agreements mandatory while certifying one admission
 *          gate, scoped tenant responses and safe session error classification.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/App.p0AdmissionCurrentness.test.jsx
 * COLLABORATION / OWNERSHIP: AuthenticatedBootstrapBoundary and LegalAcceptanceBoundary.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: v1.0.0-SESSION-SCOPED-HEADQUARTERS-ENTRY verifies no nested legal
 *            gate after COMPLETE, tenant mismatch denial and session 401 handling.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic plans only; no acceptance writes.
 * TENANT BOUNDARY: Legal status tenant must match expected EOS workspace tenant.
 * AUTHORITY BOUNDARY: Python EOS alone decides admission and required documents.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { readFileSync } from 'node:fs';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { api } = vi.hoisted(() => ({
  api: { get: vi.fn(), post: vi.fn() },
}));
vi.mock('../../src/services/api', () => ({
  default: api,
}));

import { LegalAcceptanceBoundary } from '../../src/App.jsx';

const runtime = <section data-testid="authenticated-headquarters">Headquarters entry</section>;
const mount = (tenant = 'TENANT-A', route = '/') => render(
  <MemoryRouter initialEntries={[route]}>
    <LegalAcceptanceBoundary expectedTenantId={tenant} runtime={runtime} />
  </MemoryRouter>,
);

beforeEach(() => {
  api.get.mockReset();
  api.post.mockReset();
});

describe('one mandatory platform-use admission boundary', () => {
  it('retains the single gate even if the browser begins at /covenant after COMPLETE', async () => {
    api.get.mockResolvedValue({
      data: { status: 'COMPLETE', tenantId: 'TENANT-A', documents: [] },
    });
    mount('TENANT-A', '/covenant');
    expect(await screen.findByTestId('authenticated-headquarters')).toBeInTheDocument();
    expect(screen.queryByText('LEGAL ADMISSION CONTROL')).not.toBeInTheDocument();
    expect(api.get).toHaveBeenCalledTimes(1);
    const app = readFileSync('src/App.jsx', 'utf8');
    // The outer acceptance boundary is the only Legal Control mount path.
    expect(app.match(/<LegalAcceptanceGate\b/g) || []).toHaveLength(1);
    expect(app).toContain('<Route path="/covenant" element={<Navigate');
  });

  it('fails closed if legal acceptance returns a different tenant after a verified bootstrap', async () => {
    api.get.mockResolvedValue({
      data: { status: 'COMPLETE', tenantId: 'TENANT-OTHER', documents: [] },
    });
    mount('TENANT-A');
    expect(await screen.findByText('LEGAL_ACCEPTANCE_TENANT_MISMATCH')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('classifies missing session credentials as revalidation, never a permanent server outage', async () => {
    api.get.mockRejectedValue({
      response: { status: 401, data: { detail: 'Missing authentication credentials' } },
    });
    mount('TENANT-A');
    expect(await screen.findByText('AUTHENTICATED_SESSION_REVALIDATION_REQUIRED')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('does not treat a 403 permission denial as legal-service unavailability', async () => {
    api.get.mockRejectedValue({
      response: { status: 403, data: { detail: 'Restricted access' } },
    });
    mount('TENANT-A');
    expect(await screen.findByText('LEGAL_ACCEPTANCE_ACCESS_DENIED')).toBeInTheDocument();
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });

  it('never releases the protected runtime on unavailable EOS legal status', async () => {
    api.get.mockRejectedValue({
      response: { status: 503, data: { detail: 'LEGAL_ACCEPTANCE_AUTHORITY_UNAVAILABLE' } },
    });
    mount('TENANT-A');
    await waitFor(() => expect(screen.getByText('LEGAL_ACCEPTANCE_AUTHORITY_UNAVAILABLE')).toBeInTheDocument());
    expect(screen.queryByTestId('authenticated-headquarters')).not.toBeInTheDocument();
  });
});

/*
 * ARTIFACT: App.p0AdmissionCurrentness.test.jsx
 * VERSION: v1.0.0-SESSION-SCOPED-HEADQUARTERS-ENTRY
 * AUTHORITY BOUNDARY: Test-only synthetic admission and navigation.
 * TENANT POSTURE: Mismatched EOS projection must never release workspace.
 * FAIL-CLOSED POSTURE: Only current COMPLETE response releases any runtime.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
