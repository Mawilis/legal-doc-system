/**
 * TITLE: D21B12 Authenticated Tenant Branding Asset Client Certificate
 * VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-CLIENT-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/services/tenantBrandingAssetClient.test.js
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * AUTHORITY BOUNDARY: Browser transport/presentation evidence only.
 * TENANT BOUNDARY: Requests carry only closed asset kind; server owns tenant scope.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockGet } = vi.hoisted(() => ({
  mockGet: vi.fn(),
}));

vi.mock('../../src/services/api', () => ({
  default: {
    get: mockGet,
  },
}));

import {
  TenantBrandingAssetClientError,
  createTenantBrandingObjectUrl,
  fetchAuthenticatedTenantBrandingAsset,
  revokeTenantBrandingObjectUrl,
} from '../../src/services/tenantBrandingAssetClient.js';

const fingerprint = 'a'.repeat(128);

const logo = Object.freeze({
  reference: 'asset:tenant-a:logo:primary',
  contentFingerprint: fingerprint,
  mediaType: 'image/png',
  kind: 'LOGO',
});

const favicon = Object.freeze({
  reference: 'asset:tenant-a:favicon:primary',
  contentFingerprint: 'b'.repeat(128),
  mediaType: 'image/x-icon',
  kind: 'FAVICON',
});

beforeEach(() => {
  mockGet.mockReset();
  vi.restoreAllMocks();
});

describe('D21B12 tenant branding asset client', () => {
  it('fetches logo bytes through the kind-only authenticated route', async () => {
    const blob = new Blob(['logo'], { type: 'image/png' });
    mockGet.mockResolvedValue({
      data: blob,
      headers: { 'content-type': 'image/png' },
    });

    const result = await fetchAuthenticatedTenantBrandingAsset(logo);

    expect(result).toBe(blob);
    expect(mockGet).toHaveBeenCalledTimes(1);
    expect(mockGet).toHaveBeenCalledWith(
      '/auth/workspace-branding/logo',
      {
        responseType: 'blob',
        headers: { Accept: 'image/png' },
        disableSourceBackoff: true,
      },
    );
  });

  it('fetches favicon bytes through the favicon route only', async () => {
    const blob = new Blob(['icon'], { type: 'image/x-icon' });
    mockGet.mockResolvedValue({
      data: blob,
      headers: { 'content-type': 'image/x-icon; charset=binary' },
    });

    const result = await fetchAuthenticatedTenantBrandingAsset(favicon);

    expect(result).toBe(blob);
    expect(mockGet.mock.calls[0][0]).toBe('/auth/workspace-branding/favicon');
  });

  it('never sends tenant reference fingerprint path or query authority', async () => {
    mockGet.mockResolvedValue({
      data: new Blob(['logo'], { type: 'image/png' }),
      headers: { 'content-type': 'image/png' },
    });

    await fetchAuthenticatedTenantBrandingAsset(logo);

    const [url, config] = mockGet.mock.calls[0];
    expect(url).toBe('/auth/workspace-branding/logo');
    expect(url).not.toContain('tenant-a');
    expect(url).not.toContain(logo.reference);
    expect(url).not.toContain(logo.contentFingerprint);
    expect(config).not.toHaveProperty('params');
    expect(config).not.toHaveProperty('data');
  });

  it('rejects malformed descriptors before any network request', async () => {
    await expect(
      fetchAuthenticatedTenantBrandingAsset({
        ...logo,
        mediaType: 'text/html',
      }),
    ).rejects.toMatchObject({
      code: 'D21B12_DESCRIPTOR_INVALID',
    });
    expect(mockGet).not.toHaveBeenCalled();
  });

  it('rejects server media type drift from the admitted descriptor', async () => {
    mockGet.mockResolvedValue({
      data: new Blob(['logo'], { type: 'image/webp' }),
      headers: { 'content-type': 'image/webp' },
    });

    await expect(
      fetchAuthenticatedTenantBrandingAsset(logo),
    ).rejects.toMatchObject({
      code: 'D21B12_MEDIA_TYPE_MISMATCH',
    });
  });

  it('maps HTTP 404 to not-configured without fabricating a fallback', async () => {
    mockGet.mockRejectedValue({ response: { status: 404 } });

    await expect(
      fetchAuthenticatedTenantBrandingAsset(logo),
    ).rejects.toMatchObject({
      code: 'D21B12_ASSET_NOT_CONFIGURED',
    });
  });

  it('maps delivery outages to a bounded unavailable error', async () => {
    mockGet.mockRejectedValue({ response: { status: 503 } });

    await expect(
      fetchAuthenticatedTenantBrandingAsset(logo),
    ).rejects.toMatchObject({
      code: 'D21B12_ASSET_DELIVERY_UNAVAILABLE',
    });
  });

  it('rejects empty asset responses', async () => {
    mockGet.mockResolvedValue({
      data: new Blob([], { type: 'image/png' }),
      headers: { 'content-type': 'image/png' },
    });

    await expect(
      fetchAuthenticatedTenantBrandingAsset(logo),
    ).rejects.toMatchObject({
      code: 'D21B12_EMPTY_ASSET',
    });
  });

  it('creates and revokes only transient blob object URLs', () => {
    const blob = new Blob(['logo'], { type: 'image/png' });
    const create = vi.spyOn(URL, 'createObjectURL').mockReturnValue(
      'blob:http://localhost/d21b12-logo',
    );
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {});

    const objectUrl = createTenantBrandingObjectUrl(blob);
    expect(objectUrl).toBe('blob:http://localhost/d21b12-logo');
    expect(create).toHaveBeenCalledWith(blob);

    revokeTenantBrandingObjectUrl(objectUrl);
    expect(revoke).toHaveBeenCalledWith(objectUrl);

    revokeTenantBrandingObjectUrl('https://example.invalid/logo.png');
    expect(revoke).toHaveBeenCalledTimes(1);
  });

  it('uses stable typed errors for invalid object-url input', () => {
    expect(() => createTenantBrandingObjectUrl(new Blob([]))).toThrow(
      TenantBrandingAssetClientError,
    );
    try {
      createTenantBrandingObjectUrl(new Blob([]));
    } catch (error) {
      expect(error.code).toBe('D21B12_BLOB_REQUIRED');
    }
  });
});

// ARTIFACT: tenantBrandingAssetClient.test.js
// VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-CLIENT-CERT
// AUTHORITY BOUNDARY: client transport/presentation certificate only
// TENANT POSTURE: request URL contains only closed current asset kind
// FAIL-CLOSED POSTURE: malformed/missing/mismatched/outage responses create no object URL
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
