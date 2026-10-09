/**
 * TITLE: D21B12 Authenticated Branding Asset Hook Certificate
 * VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-LIFECYCLE-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/hooks/useAuthenticatedTenantBrandingAsset.test.jsx
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * AUTHORITY BOUNDARY: Transient browser presentation lifecycle evidence only.
 * TENANT BOUNDARY: Hook accepts no tenant selector.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
 */

import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  fetchAsset: vi.fn(),
  createUrl: vi.fn(),
  revokeUrl: vi.fn(),
}));

vi.mock('../../src/services/tenantBrandingAssetClient.js', () => ({
  fetchAuthenticatedTenantBrandingAsset: mocks.fetchAsset,
  createTenantBrandingObjectUrl: mocks.createUrl,
  revokeTenantBrandingObjectUrl: mocks.revokeUrl,
}));

import { useAuthenticatedTenantBrandingAsset } from '../../src/hooks/useAuthenticatedTenantBrandingAsset.js';

const fingerprint = (character) => character.repeat(128);

const logo = Object.freeze({
  reference: 'asset:tenant-a:logo:primary',
  contentFingerprint: fingerprint('a'),
  mediaType: 'image/png',
  kind: 'LOGO',
});

const newerLogo = Object.freeze({
  reference: 'asset:tenant-a:logo:secondary',
  contentFingerprint: fingerprint('b'),
  mediaType: 'image/png',
  kind: 'LOGO',
});

const deferred = () => {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
};

beforeEach(() => {
  mocks.fetchAsset.mockReset();
  mocks.createUrl.mockReset();
  mocks.revokeUrl.mockReset();
});

describe('D21B12 authenticated branding object-url lifecycle', () => {
  it('treats an absent descriptor as no branding and performs no fetch', () => {
    const { result } = renderHook(() =>
      useAuthenticatedTenantBrandingAsset(null),
    );

    expect(result.current).toEqual({
      objectUrl: null,
      status: 'ABSENT',
      errorCode: null,
    });
    expect(mocks.fetchAsset).not.toHaveBeenCalled();
    expect(mocks.createUrl).not.toHaveBeenCalled();
  });

  it('creates one transient object URL after authenticated blob delivery', async () => {
    const blob = new Blob(['logo'], { type: 'image/png' });
    mocks.fetchAsset.mockResolvedValue(blob);
    mocks.createUrl.mockReturnValue('blob:http://localhost/logo-1');

    const { result } = renderHook(() =>
      useAuthenticatedTenantBrandingAsset(logo),
    );

    expect(result.current.status).toBe('LOADING');
    await waitFor(() => expect(result.current.status).toBe('READY'));

    expect(mocks.fetchAsset).toHaveBeenCalledWith(logo);
    expect(mocks.createUrl).toHaveBeenCalledWith(blob);
    expect(result.current.objectUrl).toBe('blob:http://localhost/logo-1');
  });

  it('revokes the previous URL when the admitted descriptor changes', async () => {
    mocks.fetchAsset
      .mockResolvedValueOnce(new Blob(['one'], { type: 'image/png' }))
      .mockResolvedValueOnce(new Blob(['two'], { type: 'image/png' }));
    mocks.createUrl
      .mockReturnValueOnce('blob:http://localhost/logo-1')
      .mockReturnValueOnce('blob:http://localhost/logo-2');

    const { result, rerender } = renderHook(
      ({ descriptor }) => useAuthenticatedTenantBrandingAsset(descriptor),
      { initialProps: { descriptor: logo } },
    );
    await waitFor(() =>
      expect(result.current.objectUrl).toBe('blob:http://localhost/logo-1'),
    );

    rerender({ descriptor: newerLogo });
    expect(mocks.revokeUrl).toHaveBeenCalledWith(
      'blob:http://localhost/logo-1',
    );
    await waitFor(() =>
      expect(result.current.objectUrl).toBe('blob:http://localhost/logo-2'),
    );
    expect(mocks.fetchAsset).toHaveBeenLastCalledWith(newerLogo);
  });

  it('revokes its owned URL on unmount', async () => {
    mocks.fetchAsset.mockResolvedValue(
      new Blob(['logo'], { type: 'image/png' }),
    );
    mocks.createUrl.mockReturnValue('blob:http://localhost/logo-owned');

    const { result, unmount } = renderHook(() =>
      useAuthenticatedTenantBrandingAsset(logo),
    );
    await waitFor(() => expect(result.current.status).toBe('READY'));

    unmount();
    expect(mocks.revokeUrl).toHaveBeenCalledWith(
      'blob:http://localhost/logo-owned',
    );
  });

  it('fails closed to no renderable URL when delivery is unavailable', async () => {
    const error = Object.assign(new Error('unavailable'), {
      code: 'D21B12_ASSET_DELIVERY_UNAVAILABLE',
    });
    mocks.fetchAsset.mockRejectedValue(error);

    const { result } = renderHook(() =>
      useAuthenticatedTenantBrandingAsset(logo),
    );

    await waitFor(() =>
      expect(result.current.status).toBe('UNAVAILABLE'),
    );
    expect(result.current.objectUrl).toBeNull();
    expect(result.current.errorCode).toBe(
      'D21B12_ASSET_DELIVERY_UNAVAILABLE',
    );
    expect(mocks.createUrl).not.toHaveBeenCalled();
  });

  it('prevents a late old response from replacing newer branding and revokes it', async () => {
    const oldRequest = deferred();
    const newRequest = deferred();
    mocks.fetchAsset
      .mockImplementationOnce(() => oldRequest.promise)
      .mockImplementationOnce(() => newRequest.promise);
    mocks.createUrl
      .mockReturnValueOnce('blob:http://localhost/new-logo')
      .mockReturnValueOnce('blob:http://localhost/stale-old-logo');

    const { result, rerender } = renderHook(
      ({ descriptor }) => useAuthenticatedTenantBrandingAsset(descriptor),
      { initialProps: { descriptor: logo } },
    );

    rerender({ descriptor: newerLogo });

    await act(async () => {
      newRequest.resolve(new Blob(['new'], { type: 'image/png' }));
      await newRequest.promise;
    });
    await waitFor(() =>
      expect(result.current.objectUrl).toBe(
        'blob:http://localhost/new-logo',
      ),
    );

    await act(async () => {
      oldRequest.resolve(new Blob(['old'], { type: 'image/png' }));
      await oldRequest.promise;
    });

    expect(result.current.objectUrl).toBe(
      'blob:http://localhost/new-logo',
    );
    expect(mocks.revokeUrl).toHaveBeenCalledWith(
      'blob:http://localhost/stale-old-logo',
    );
  });
});

// ARTIFACT: useAuthenticatedTenantBrandingAsset.test.jsx
// VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-LIFECYCLE-CERT
// AUTHORITY BOUNDARY: transient object-URL lifecycle certificate only
// TENANT POSTURE: no browser tenant selector is introduced
// FAIL-CLOSED POSTURE: absent/error/stale responses cannot leave a renderable stale URL
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
