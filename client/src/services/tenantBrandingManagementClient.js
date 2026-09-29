/**
 * TITLE: WILSY OS Tenant Branding Management Client
 * VERSION: v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-CLIENT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Transport the authenticated tenant-branding management contract to
 *          Python EOS without sending tenant, entitlement, revision, current-
 *          pointer, subscription, plan, or authorization claims.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/tenantBrandingManagementClient.js
 * COLLABORATION / OWNERSHIP: Account Command Center consumes this transport;
 *                            Python EOS owns identity, authorization,
 *                            entitlement, profile, selection, and asset truth.
 * CERTIFICATION / UPDATE DATE: 2026-09-29
 * CHANGELOG: v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-CLIENT adds governed
 *            multipart asset admission and server-issued asset descriptor
 *            binding while preserving server-owned tenant and fingerprint truth.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No localStorage branding authority, public URL,
 *                             raw bytes, or caller-supplied tenant selector.
 * TENANT BOUNDARY: Server derives exact tenant from authenticated identity.
 * AUTHORITY BOUNDARY: Client transport only; no browser authority is created.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import api from './api.js';

export const VERSION = 'v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-CLIENT';
const BASE = '/tenant-branding';

const ERROR_BY_STATUS = Object.freeze({
  401: 'BRANDING_AUTHENTICATION_REQUIRED',
  403: 'BRANDING_AUTHORIZATION_DENIED',
  404: 'BRANDING_NOT_FOUND',
  409: 'BRANDING_CONFLICT',
  413: 'BRANDING_CONTENT_TOO_LARGE',
  422: 'BRANDING_INPUT_INVALID',
  503: 'BRANDING_AUTHORITY_UNAVAILABLE',
});

export class TenantBrandingManagementError extends Error {
  constructor(message, { code = 'BRANDING_MANAGEMENT_FAILED', status = null, cause = null } = {}) {
    super(message);
    this.name = 'TenantBrandingManagementError';
    this.code = code;
    this.status = status;
    this.cause = cause;
  }
}

const unwrap = (response) => response?.data?.data ?? response?.data ?? {};

const mapError = (error) => {
  const status = error?.response?.status ?? null;
  const body = error?.response?.data?.detail;
  const detail = typeof body === 'object' && body !== null ? body : {};
  const code = typeof detail.code === 'string' && detail.code
    ? detail.code
    : ERROR_BY_STATUS[status] || 'BRANDING_MANAGEMENT_FAILED';
  return new TenantBrandingManagementError('Tenant branding management request failed.', {
    code,
    status,
    cause: error,
  });
};

const request = async (promise) => {
  try {
    return unwrap(await promise);
  } catch (error) {
    throw mapError(error);
  }
};

/** @description Loads fresh authenticated tenant-branding management truth. */
export const fetchTenantBrandingManagement = () => request(api.get(BASE));

/** @description Approves one immutable server-validated profile from allowed presentation fields. */
export const createTenantBrandingProfile = (fields = {}) => request(api.post(`${BASE}/profiles`, {
  profile_label: fields.profileLabel,
  ...(fields.primaryColor ? { primary_color: fields.primaryColor } : {}),
  ...(fields.secondaryColor ? { secondary_color: fields.secondaryColor } : {}),
  ...(fields.accentColor ? { accent_color: fields.accentColor } : {}),
  ...(fields.emailDisplayName ? { email_display_name: fields.emailDisplayName } : {}),
  ...((fields.logoAssetReference !== undefined || fields.logoAssetFingerprint !== undefined)
    ? { logo_asset_reference: fields.logoAssetReference, logo_asset_fingerprint: fields.logoAssetFingerprint }
    : {}),
  ...((fields.faviconAssetReference !== undefined || fields.faviconAssetFingerprint !== undefined)
    ? { favicon_asset_reference: fields.faviconAssetReference, favicon_asset_fingerprint: fields.faviconAssetFingerprint }
    : {}),
}));

/** @description Uploads one bounded logo/favicon through authenticated multipart transport. */
export const uploadTenantBrandingAsset = (kind, file) => {
  const normalizedKind = String(kind || '').toUpperCase();
  if (!['LOGO', 'FAVICON'].includes(normalizedKind) || typeof Blob === 'undefined' || !(file instanceof Blob)) {
    return Promise.reject(new TenantBrandingManagementError('Invalid branding asset upload.', {
      code: 'BRANDING_ASSET_UPLOAD_INPUT_INVALID',
      status: 422,
    }));
  }
  const form = new FormData();
  form.append('file', file);
  return request(api.post(`${BASE}/assets/${normalizedKind.toLowerCase()}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    skipForensicBodyMutation: true,
    disableSourceBackoff: true,
  }));
};

/** @description Advances the server-owned current-profile pointer. */
export const selectTenantBrandingProfile = (profileId) => request(api.post(`${BASE}/profiles/${encodeURIComponent(profileId)}/select`, {}));

export default {
  VERSION,
  fetchTenantBrandingManagement,
  createTenantBrandingProfile,
  selectTenantBrandingProfile,
  uploadTenantBrandingAsset,
  TenantBrandingManagementError,
};

// ARTIFACT: tenantBrandingManagementClient.js
// VERSION: v1.1.0-L10-P2C7-D21B-BRANDING-MANAGEMENT-CLIENT
// AUTHORITY BOUNDARY: authenticated tenant-branding transport only
// TENANT POSTURE: no tenant selector is sent as authority
// FAIL-CLOSED POSTURE: HTTP failures map to stable bounded client errors
// FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
// END OF WILSY OS SOVEREIGN ARTIFACT
