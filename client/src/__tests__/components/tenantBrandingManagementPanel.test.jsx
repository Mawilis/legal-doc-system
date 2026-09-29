/**
 * TITLE: Tenant Branding Management Panel Direct Certificate
 * VERSION: v1.1.0-L10-P2C7-D21B-BRANDING-COMMAND-CENTER-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves shared Account Center branding presentation is server-owned,
 *          refreshable, read-only when capability is absent, mutation-safe, and
 *          pending-only for governed asset uploads.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/tenantBrandingManagementPanel.test.jsx
 * COLLABORATION / OWNERSHIP: Direct Account Center panel certificate.
 * CERTIFICATION / UPDATE DATE: 2026-09-29
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 */
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { fetchManagement, createProfile, selectProfile, uploadAsset } = vi.hoisted(() => ({ fetchManagement: vi.fn(), createProfile: vi.fn(), selectProfile: vi.fn(), uploadAsset: vi.fn() }));
vi.mock('../../services/tenantBrandingManagementClient.js', () => ({
  fetchTenantBrandingManagement: fetchManagement,
  createTenantBrandingProfile: createProfile,
  selectTenantBrandingProfile: selectProfile,
  uploadTenantBrandingAsset: uploadAsset,
}));
vi.mock('../../hooks/useAuthenticatedTenantBrandingAsset.js', () => ({ default: () => ({ objectUrl: null, status: 'ABSENT' }) }));

import TenantBrandingManagementPanel from '../../components/account/TenantBrandingManagementPanel.jsx';

describe('tenant branding management panel', () => {
  beforeEach(() => {
    fetchManagement.mockReset();
    createProfile.mockReset();
    selectProfile.mockReset();
    uploadAsset.mockReset();
  });

  it('renders current entitlement and profile from the server', async () => {
    fetchManagement.mockResolvedValue({ entitlement: { brandingTier: 'PRO', lifecycleState: 'ACTIVE' }, profile: { profileId: 'p1', profileLabel: 'Legal' }, capabilities: { canManageProfile: false, canManageAssets: false } });
    render(<TenantBrandingManagementPanel />);
    await waitFor(() => expect(screen.getByText('PRO')).toBeInTheDocument());
    expect(screen.getByText('Legal')).toBeInTheDocument();
  });

  it('keeps profile controls disabled when server denies mutation', async () => {
    fetchManagement.mockResolvedValue({ entitlement: null, profile: null, capabilities: { canManageProfile: false, canManageAssets: false } });
    render(<TenantBrandingManagementPanel />);
    await waitFor(() => expect(screen.getByLabelText('Profile label')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: 'Approve profile' })).toBeDisabled();
    expect(screen.queryByLabelText('Upload logo')).not.toBeInTheDocument();
  });

  it('uploads a governed asset as pending preview without refreshing shared authority', async () => {
    fetchManagement.mockResolvedValue({ entitlement: { brandingTier: 'PRO', lifecycleState: 'ACTIVE' }, profile: null, capabilities: { canManageProfile: true, canManageAssets: true } });
    uploadAsset.mockResolvedValue({ reference: 'asset:tenant-a:logo:opaque', contentFingerprint: 'a'.repeat(128), mediaType: 'image/png', kind: 'LOGO', contentLength: 8 });
    const refreshAuthority = vi.fn();
    render(<TenantBrandingManagementPanel onAuthorityRefresh={refreshAuthority} />);
    await waitFor(() => expect(screen.getByLabelText('Upload logo')).toBeInTheDocument());
    const file = new File(['png-data'], 'logo.png', { type: 'image/png' });
    fireEvent.change(screen.getByLabelText('Upload logo'), { target: { files: [file] } });
    await waitFor(() => expect(screen.getByTestId('tenant-branding-pending-preview')).toBeInTheDocument());
    expect(uploadAsset).toHaveBeenCalledWith('LOGO', file);
    expect(refreshAuthority).not.toHaveBeenCalled();
    expect(screen.getByText(/Pending preview · not shared chrome authority/i)).toBeInTheDocument();
  });

  it('refreshes after profile approval and does not submit tenant authority', async () => {
    fetchManagement.mockResolvedValue({ entitlement: { brandingTier: 'PRO', lifecycleState: 'ACTIVE' }, profile: null, capabilities: { canManageProfile: true, canManageAssets: false } });
    createProfile.mockResolvedValue({ profileId: 'p1' });
    render(<TenantBrandingManagementPanel />);
    await waitFor(() => expect(screen.getByText('Approve profile')).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText('Profile label'), { target: { value: 'Legal' } });
    fireEvent.click(screen.getByRole('button', { name: 'Approve profile' }));
    await waitFor(() => expect(createProfile).toHaveBeenCalledWith(expect.objectContaining({ profileLabel: 'Legal' })));
    expect(createProfile.mock.calls[0][0]).not.toHaveProperty('tenantId');
  });

  it('surfaces bounded transport errors', async () => {
    fetchManagement.mockRejectedValue({ code: 'BRANDING_AUTHORITY_UNAVAILABLE' });
    render(<TenantBrandingManagementPanel />);
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('BRANDING_AUTHORITY_UNAVAILABLE'));
  });
});

// ARTIFACT: tenantBrandingManagementPanel.test.jsx
// VERSION: v1.1.0-L10-P2C7-D21B-BRANDING-COMMAND-CENTER-CERT
// END OF WILSY OS SOVEREIGN ARTIFACT
