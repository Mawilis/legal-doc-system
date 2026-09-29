/**
 * TITLE: Tenant Branding Management Client Direct Certificate
 * VERSION: v1.0.0-L10-P2C6-D21B-BRANDING-MANAGEMENT-CLIENT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Proves the Account Center branding transport sends only allowed
 *          presentation values and maps server failures without creating tenant
 *          or entitlement authority in the browser.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/services/tenantBrandingManagementClient.test.js
 * COLLABORATION / OWNERSHIP: Direct client transport certificate.
 * CERTIFICATION / UPDATE DATE: 2026-09-29
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: { get, post } }));

import {
  createTenantBrandingProfile,
  fetchTenantBrandingManagement,
  selectTenantBrandingProfile,
  TenantBrandingManagementError,
} from '../../services/tenantBrandingManagementClient.js';

describe('tenant branding management client', () => {
  beforeEach(() => { get.mockReset(); post.mockReset(); });

  it('loads the authenticated server-derived management projection', async () => {
    get.mockResolvedValue({ data: { data: { entitlement: null } } });
    await expect(fetchTenantBrandingManagement()).resolves.toEqual({ entitlement: null });
    expect(get).toHaveBeenCalledWith('/tenant-branding');
  });

  it('sends only approved presentation fields for profile creation', async () => {
    post.mockResolvedValue({ data: { data: { profileId: 'p1' } } });
    await createTenantBrandingProfile({ profileLabel: 'Legal', primaryColor: '#111', tenantId: 'must-not-send', entitlementId: 'must-not-send' });
    expect(post.mock.calls[0][0]).toBe('/tenant-branding/profiles');
    expect(post.mock.calls[0][1]).toEqual({ profile_label: 'Legal', primary_color: '#111' });
  });

  it('encodes profile identity for selection', async () => {
    post.mockResolvedValue({ data: { data: { selectionId: 's1' } } });
    await selectTenantBrandingProfile('profile/one');
    expect(post).toHaveBeenCalledWith('/tenant-branding/profiles/profile%2Fone/select', {});
  });

  it.each([
    [401, 'BRANDING_AUTHENTICATION_REQUIRED'],
    [403, 'BRANDING_AUTHORIZATION_DENIED'],
    [404, 'BRANDING_NOT_FOUND'],
    [409, 'BRANDING_CONFLICT'],
    [422, 'BRANDING_INPUT_INVALID'],
    [503, 'BRANDING_AUTHORITY_UNAVAILABLE'],
  ])('maps HTTP %s to stable code', async (status, code) => {
    get.mockRejectedValue({ response: { status, data: {} } });
    await expect(fetchTenantBrandingManagement()).rejects.toMatchObject({ status, code });
    expect(get).toHaveBeenCalledTimes(1);
  });

  it('exports a governed error type', () => {
    expect(new TenantBrandingManagementError('x', { code: 'C' })).toBeInstanceOf(Error);
  });
});

// ARTIFACT: tenantBrandingManagementClient.test.js
// VERSION: v1.0.0-L10-P2C6-D21B-BRANDING-MANAGEMENT-CLIENT-CERT
// END OF WILSY OS SOVEREIGN ARTIFACT
