/**
 * TITLE: WILSY OS Authenticated Tenant Branding Asset Client
 * VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-CLIENT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Fetch current tenant logo/favicon bytes only through the authenticated
 *          D21B11 endpoint and return a validated transient Blob for presentation.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/tenantBrandingAssetClient.js
 * COLLABORATION / OWNERSHIP: D21B8 supplies the admitted asset descriptor;
 *                            D21B11/D21B10/D21B6/D21B5B own server truth and bytes;
 *                            this client owns transport validation only.
 * CERTIFICATION / UPDATE DATE: 2026-09-25
 * SECURITY / PRIVACY POSTURE: Sends only the closed LOGO/FAVICON kind. Tenant,
 *                             reference, fingerprint, URL/path and bearer
 *                             authority are never constructed here; the canonical
 *                             api client supplies the anchored session bearer.
 * TENANT BOUNDARY: The browser cannot select tenant scope for this request.
 * AUTHORITY BOUNDARY: Presentation transport only; returned Blob grants no IAM,
 *                     entitlement, profile, upload, legal or financial authority.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
 */

import api from './api';

export const VERSION = 'v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-CLIENT';

const SAFE_MEDIA_TYPES = new Set([
  'image/png',
  'image/jpeg',
  'image/webp',
  'image/x-icon',
  'image/vnd.microsoft.icon',
]);

const KIND_TO_PATH = Object.freeze({
  LOGO: 'logo',
  FAVICON: 'favicon',
});

export class TenantBrandingAssetClientError extends Error {
  constructor(code, cause = null) {
    super(code);
    this.name = 'TenantBrandingAssetClientError';
    this.code = code;
    if (cause) this.cause = cause;
  }
}

function exactDescriptor(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new TenantBrandingAssetClientError('D21B12_DESCRIPTOR_REQUIRED');
  }
  const { reference, contentFingerprint, mediaType, kind } = value;
  if (
    typeof reference !== 'string'
    || !reference
    || reference !== reference.trim()
    || typeof contentFingerprint !== 'string'
    || !/^[0-9a-f]{128}$/.test(contentFingerprint)
    || typeof mediaType !== 'string'
    || !SAFE_MEDIA_TYPES.has(mediaType)
    || !Object.prototype.hasOwnProperty.call(KIND_TO_PATH, kind)
  ) {
    throw new TenantBrandingAssetClientError('D21B12_DESCRIPTOR_INVALID');
  }
  return {
    reference,
    contentFingerprint,
    mediaType,
    kind,
  };
}

function normalizedContentType(headers = {}) {
  const raw = headers?.['content-type'] || headers?.get?.('content-type') || '';
  return String(raw).split(';', 1)[0].trim().toLowerCase();
}

export async function fetchAuthenticatedTenantBrandingAsset(descriptor) {
  const expected = exactDescriptor(descriptor);
  const pathKind = KIND_TO_PATH[expected.kind];

  let response;
  try {
    response = await api.get(`/auth/workspace-branding/${pathKind}`, {
      responseType: 'blob',
      headers: {
        Accept: expected.mediaType,
      },
      disableSourceBackoff: true,
    });
  } catch (error) {
    const status = error?.response?.status;
    if (status === 404) {
      throw new TenantBrandingAssetClientError(
        'D21B12_ASSET_NOT_CONFIGURED',
        error,
      );
    }
    throw new TenantBrandingAssetClientError(
      'D21B12_ASSET_DELIVERY_UNAVAILABLE',
      error,
    );
  }

  const responseMediaType = normalizedContentType(response?.headers);
  if (
    !SAFE_MEDIA_TYPES.has(responseMediaType)
    || responseMediaType !== expected.mediaType
  ) {
    throw new TenantBrandingAssetClientError(
      'D21B12_MEDIA_TYPE_MISMATCH',
    );
  }

  const data = response?.data;
  const blob = data instanceof Blob
    ? data
    : new Blob([data], { type: responseMediaType });

  if (blob.size < 1) {
    throw new TenantBrandingAssetClientError('D21B12_EMPTY_ASSET');
  }
  if (blob.type && blob.type.toLowerCase() !== responseMediaType) {
    throw new TenantBrandingAssetClientError(
      'D21B12_BLOB_MEDIA_TYPE_MISMATCH',
    );
  }

  return blob;
}

export function createTenantBrandingObjectUrl(blob) {
  if (!(blob instanceof Blob) || blob.size < 1) {
    throw new TenantBrandingAssetClientError('D21B12_BLOB_REQUIRED');
  }
  if (
    typeof URL === 'undefined'
    || typeof URL.createObjectURL !== 'function'
  ) {
    throw new TenantBrandingAssetClientError(
      'D21B12_OBJECT_URL_UNAVAILABLE',
    );
  }
  return URL.createObjectURL(blob);
}

export function revokeTenantBrandingObjectUrl(url) {
  if (
    typeof url === 'string'
    && url.startsWith('blob:')
    && typeof URL !== 'undefined'
    && typeof URL.revokeObjectURL === 'function'
  ) {
    URL.revokeObjectURL(url);
  }
}

export default {
  fetchAuthenticatedTenantBrandingAsset,
  createTenantBrandingObjectUrl,
  revokeTenantBrandingObjectUrl,
};


// ARTIFACT: tenantBrandingAssetClient.js
// VERSION: v1.0.0-D21B12-AUTHENTICATED-BRANDING-ASSET-CLIENT
// AUTHORITY BOUNDARY: authenticated blob transport/presentation validation only
// TENANT POSTURE: request carries only closed asset kind; server derives tenant/reference/fingerprint
// FAIL-CLOSED POSTURE: malformed descriptor, media mismatch, absence or outage produces no object URL
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
