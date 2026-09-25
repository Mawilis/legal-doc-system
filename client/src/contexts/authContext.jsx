/**
 * TITLE: WILSY OS Authoritative Browser Authentication Context
 * VERSION: v55.0.0-D21B8-TENANT-BRANDING-AUTHCONTEXT-PROJECTION
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Represents server-issued authentication and MFA challenge state
 *          without fabricating tenant, role, permission, or enrollment truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/authContext.jsx
 * COLLABORATION / OWNERSHIP: Python EOS auth_router owns credential/MFA truth;
 *                            this context owns browser projection and navigation state.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: v55.0.0-D21B8-TENANT-BRANDING-AUTHCONTEXT-PROJECTION — Accepts tenant branding only from the explicit READY workspace.branding projection produced by D21B7. The field is mandatory: null is authoritative lawful no-branding; configured branding must match the exact D21B6 browser-safe schema, exact tenant, closed tier/media/kind sets, canonical fingerprints/colours, and mandatory WILSY trust mark. Legacy tenant branding aliases are removed before authenticated tenant state is persisted, so discovery/login/MFA/local-storage/JWT branding cannot override Python EOS authority.
 *            v54.0.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION — Accepts firstName/lastName only from the READY workspace-bootstrap user projection after Python EOS has revalidated current principal, tenant membership, dedicated business role and tenant truth. Login/MFA/browser-persisted names remain non-authoritative candidate data and are never promoted. Optional null/absent names remain absent; malformed or whitespace-mutated server name values fail session promotion closed. Names create no role, permission, entitlement, Legal command, billing, payment, execution or settlement authority.
 *            v53.0.0-D17-SERVER-LEGAL-PERMISSION-PROJECTION — Accepts an optional workspace.legalPermissions
 *            projection only when it is an exact, duplicate-free subset of the
 *            four D17 Legal Command Center permissions. Server absence preserves
 *            the legacy role-baseline posture; server presence, including an
 *            empty array, is marked as authoritative presentation provenance.
 *            JWT/login/browser permission claims remain excluded from workspace
 *            projection and Python EOS remains final authorization authority.
 *            v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE — Restores a persisted
 *            access-token candidate only after Python EOS workspace-bootstrap
 *            revalidates current principal, membership, business role and exact
 *            tenant truth. Invalid, expired, mismatched or malformed candidates
 *            are purged while the server-discovered tenant selection is retained
 *            for a fresh login rather than forcing redundant discovery.
 *            v51.0.0-R1D-B0F-B4-R4-WORKSPACE-BOOTSTRAP — Anchored and cleared
 *            the canonical API bearer synchronously at MFA/session boundaries
 *            so dependent tenant bootstrap requests could not race state effects.
 *            v49.0.0-R1D-B0F-B3B-TENANT-SOURCE — Compares the discovered
 *            server-issued tenant projection with the authenticated durable
 *            principal before persisting browser session state; mismatch fails closed.
 *            v48.0.0-AUTHORITATIVE-MFA-STATE-MACHINE — Added explicit MFA
 *            reconciliation state, removed tenant/user fallbacks, and replaced
 *            reload-based auth transitions with state-driven session hydration.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Persisted bearer, tenant and user material are candidate
 *                             state only until Python EOS revalidates them. D21B8
 *                             accepts no raw asset bytes/URLs and removes legacy
 *                             branding aliases before authenticated persistence.
 * TENANT BOUNDARY: Authenticated tenant and branding tenant identity must exactly match
 *                  the READY server workspace tenant; foreign branding fails closed.
 * AUTHORITY BOUNDARY: Browser projection only; Python EOS owns authentication and
 *                     D21B2B/D21B4B/D21B5B/D21B6/D21B7 own branding truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
 */

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import api from '@/services/api';

const LEGAL_PRESENTATION_PERMISSION_SET = new Set([
  'legal_operations:instruction:write',
  'legal_operations:return:write',
  'legal_operations:billing:read',
  'legal_operations:invoice:read',
]);

const BRANDING_TIER_SET = new Set([
  'TENANT_BRANDING_STARTER',
  'TENANT_BRANDING_PROFESSIONAL',
  'TENANT_BRANDING_INSTITUTIONAL',
  'TENANT_BRANDING_ENTERPRISE',
]);
const BRANDING_MEDIA_TYPE_SET = new Set([
  'image/png',
  'image/jpeg',
  'image/webp',
  'image/x-icon',
  'image/vnd.microsoft.icon',
]);
const BRANDING_PROJECTION_KEYS = Object.freeze([
  'tenantId',
  'profileId',
  'profileFingerprint',
  'selectionId',
  'selectionRevision',
  'entitlementId',
  'entitlementRevision',
  'entitlementFingerprint',
  'brandingTier',
  'profileLabel',
  'primaryColor',
  'secondaryColor',
  'accentColor',
  'emailDisplayName',
  'platformTrustMarkRequired',
  'logo',
  'favicon',
]);
const BRANDING_ASSET_KEYS = Object.freeze([
  'reference',
  'contentFingerprint',
  'mediaType',
  'kind',
]);
const LEGACY_BRANDING_KEYS = Object.freeze([
  'branding',
  'brandingNexus',
  'theme',
  'logo',
  'logoUrl',
  'logoPath',
  'logoBase64',
  'brandLogo',
  'brandColor',
  'primaryColor',
  'secondaryColor',
  'accentColor',
]);

export const AUTH_STATES = Object.freeze({
  IDLE: 'IDLE',
  PRIMARY_AUTHENTICATING: 'PRIMARY_AUTHENTICATING',
  MFA_SETUP: 'MFA_SETUP',
  MFA_RECONCILIATION_REQUIRED: 'MFA_RECONCILIATION_REQUIRED',
  MFA_REQUIRED: 'MFA_REQUIRED',
  MFA_VERIFYING: 'MFA_VERIFYING',
  AUTHENTICATED: 'AUTHENTICATED',
  FAILED: 'FAILED',
});

const AuthContext = createContext(null);
const publicAuthPaths = new Set(['/discovery', '/login', '/mfa', '/mfa-setup']);

const parseJsonResponse = async (response) => {
  const text = await response.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    throw new Error(`Server returned a non-JSON response (HTTP ${response.status}).`);
  }
};

const emitAuthState = (state) => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('wilsy-auth-state', { detail: state }));
  }
};

/**
 * @function anchorCanonicalBearer
 * @description Updates the shared API client's in-memory bearer before auth
 *              state is published, preventing a post-MFA bootstrap race.
 * @param {string|null} accessToken - Server-issued access token.
 * @returns {void}
 * @collaboration TenantApiClient consumes the same `api` instance.
 * @institutional AuthProvider owns session state; the canonical client owns
 *               request authentication propagation.
 */
const anchorCanonicalBearer = (accessToken) => {
  const commonHeaders = api?.defaults?.headers?.common;
  if (!commonHeaders) return;
  if (accessToken) commonHeaders.Authorization = `Bearer ${accessToken}`;
  else delete commonHeaders.Authorization;
};


/**
 * Return one persisted access-token candidate without treating it as authority.
 * Python EOS must revalidate it before any authenticated browser state exists.
 */
const readPersistedAccessTokenCandidate = () => {
  try {
    return String(
      localStorage.getItem('wilsy_auth_token')
      || localStorage.getItem('token')
      || '',
    ).trim();
  } catch {
    return '';
  }
};

/**
 * Return the last server-discovered tenant projection for navigation continuity.
 * This projection is not authentication, membership, role, or workspace authority.
 */
const readPersistedDiscoveredTenant = () => {
  try {
    const raw = localStorage.getItem('discoveredTenant');
    const value = raw ? JSON.parse(raw) : null;
    return value && typeof value === 'object' ? value : null;
  } catch {
    return null;
  }
};

/**
 * Return the last bounded authenticated user projection as comparison metadata.
 * The returned value never establishes authority by itself.
 */
const readPersistedUserProjection = () => {
  try {
    const raw = localStorage.getItem('wilsy_sovereign_user');
    const value = raw ? JSON.parse(raw) : null;
    return value && typeof value === 'object' ? value : null;
  } catch {
    return null;
  }
};

/**
 * Purge browser authentication authority while preserving discovered tenant
 * navigation context for a fresh login.
 */
const clearPersistedSessionAuthority = () => {
  anchorCanonicalBearer(null);
  localStorage.removeItem('wilsy_auth_token');
  localStorage.removeItem('token');
  localStorage.removeItem('wilsy_sovereign_user');
  localStorage.removeItem('wilsy_refresh_token');
  localStorage.removeItem('wilsy_active_tenant');
};

const candidateSessionProjection = (data, fallbackEmail = '') => {
  const candidate = data?.user;
  const token = data?.token || data?.accessToken;

  if (!token || !candidate || typeof candidate !== 'object' || !candidate.id) {
    throw new Error('Authenticated response omitted required candidate session fields.');
  }

  return {
    token,
    user: {
      id: String(candidate.id),
      email: candidate.email || fallbackEmail,
      mfaRegistered: candidate.mfaRegistered === true,
    },
  };
};

const exactOptionalWorkspaceName = (value) => {
  if (value === null || value === undefined) return null;
  if (
    typeof value !== 'string'
    || !value
    || value !== value.trim()
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_PROJECTION_INVALID');
  }
  return value;
};

const exactBrandingText = (value) => {
  if (
    typeof value !== 'string'
    || !value
    || value !== value.trim()
    || [...value].some((character) => character.codePointAt(0) < 32)
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }
  return value;
};

const exactBrandingFingerprint = (value) => {
  if (typeof value !== 'string' || !/^[0-9a-f]{128}$/.test(value)) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }
  return value;
};

const exactOptionalBrandingColor = (value) => {
  if (value === null) return null;
  if (typeof value !== 'string' || !/^#[0-9A-F]{6}$/.test(value)) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }
  return value;
};

const exactObjectKeys = (value, expectedKeys) => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }
  const keys = Object.keys(value);
  if (
    keys.length !== expectedKeys.length
    || expectedKeys.some(
      (key) => !Object.prototype.hasOwnProperty.call(value, key),
    )
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }
};

const boundedBrandingAssetProjection = (
  value,
  { tenantId, expectedKind },
) => {
  if (value === null) return null;
  exactObjectKeys(value, BRANDING_ASSET_KEYS);
  const reference = exactBrandingText(value.reference);
  const contentFingerprint = exactBrandingFingerprint(
    value.contentFingerprint,
  );
  const mediaType = exactBrandingText(value.mediaType);
  const kind = exactBrandingText(value.kind);

  if (
    !reference.startsWith(`asset:${tenantId}:`)
    || !/^asset:[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/.test(reference)
    || !BRANDING_MEDIA_TYPE_SET.has(mediaType)
    || kind !== expectedKind
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }

  return {
    reference,
    contentFingerprint,
    mediaType,
    kind,
  };
};

const boundedWorkspaceBrandingProjection = (workspace, tenantId) => {
  if (!Object.prototype.hasOwnProperty.call(workspace || {}, 'branding')) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }
  const branding = workspace.branding;
  if (branding === null) return null;

  exactObjectKeys(branding, BRANDING_PROJECTION_KEYS);

  const brandingTenantId = exactBrandingText(branding.tenantId);
  const profileId = exactBrandingText(branding.profileId);
  const profileFingerprint = exactBrandingFingerprint(
    branding.profileFingerprint,
  );
  const selectionId = exactBrandingText(branding.selectionId);
  const selectionRevision = branding.selectionRevision;
  const entitlementId = exactBrandingText(branding.entitlementId);
  const entitlementRevision = branding.entitlementRevision;
  const entitlementFingerprint = exactBrandingFingerprint(
    branding.entitlementFingerprint,
  );
  const brandingTier = exactBrandingText(branding.brandingTier);
  const profileLabel = exactBrandingText(branding.profileLabel);
  const primaryColor = exactOptionalBrandingColor(branding.primaryColor);
  const secondaryColor = exactOptionalBrandingColor(branding.secondaryColor);
  const accentColor = exactOptionalBrandingColor(branding.accentColor);
  const emailDisplayName = exactOptionalWorkspaceName(
    branding.emailDisplayName,
  );

  if (
    brandingTenantId !== tenantId
    || !Number.isInteger(selectionRevision)
    || selectionRevision < 1
    || !Number.isInteger(entitlementRevision)
    || entitlementRevision < 1
    || !BRANDING_TIER_SET.has(brandingTier)
    || branding.platformTrustMarkRequired !== true
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_BRANDING_INVALID');
  }

  return {
    tenantId: brandingTenantId,
    profileId,
    profileFingerprint,
    selectionId,
    selectionRevision,
    entitlementId,
    entitlementRevision,
    entitlementFingerprint,
    brandingTier,
    profileLabel,
    primaryColor,
    secondaryColor,
    accentColor,
    emailDisplayName,
    platformTrustMarkRequired: true,
    logo: boundedBrandingAssetProjection(
      branding.logo,
      { tenantId, expectedKind: 'LOGO' },
    ),
    favicon: boundedBrandingAssetProjection(
      branding.favicon,
      { tenantId, expectedKind: 'FAVICON' },
    ),
  };
};

const authenticatedTenantProjection = (
  tenantProjection,
  tenantId,
  branding,
) => {
  const bounded = {
    ...tenantProjection,
    tenantId,
  };
  LEGACY_BRANDING_KEYS.forEach((key) => {
    delete bounded[key];
  });
  bounded.branding = branding;
  return bounded;
};

const boundedWorkspaceProjection = (data, fallbackEmail = '') => {
  const principal = data?.user;
  const workspace = data?.workspace;
  const tenantProjection = workspace?.tenant;

  const principalId = String(principal?.id || '').trim();
  const firstName = exactOptionalWorkspaceName(principal?.firstName);
  const lastName = exactOptionalWorkspaceName(principal?.lastName);
  const tenantId = String(workspace?.tenantId || '').trim();
  const tenantProjectionId = String(tenantProjection?.tenantId || '').trim();
  const businessRole = String(workspace?.businessRole || '').trim();
  const membershipRevision = workspace?.membershipRevision;
  const businessRoleRevision = workspace?.businessRoleRevision;
  const branding = boundedWorkspaceBrandingProjection(workspace, tenantId);
  const hasLegalPermissionProjection = Object.prototype.hasOwnProperty.call(
    workspace || {},
    'legalPermissions',
  );
  const legalPermissions = hasLegalPermissionProjection
    ? workspace.legalPermissions
    : [];

  if (
    hasLegalPermissionProjection
    && (
      !Array.isArray(legalPermissions)
      || legalPermissions.some(
        (permission) => (
          typeof permission !== 'string'
          || permission !== permission.trim()
          || !LEGAL_PRESENTATION_PERMISSION_SET.has(permission)
        ),
      )
      || new Set(legalPermissions).size !== legalPermissions.length
    )
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_PROJECTION_INVALID');
  }

  if (
    data?.status !== 'READY'
    || !principalId
    || !tenantId
    || !tenantProjection
    || tenantProjectionId !== tenantId
    || !businessRole
    || !Number.isInteger(membershipRevision)
    || membershipRevision < 0
    || !Number.isInteger(businessRoleRevision)
    || businessRoleRevision < 0
  ) {
    throw new Error('AUTHENTICATED_WORKSPACE_PROJECTION_INVALID');
  }

  return {
    user: {
      id: principalId,
      email: principal?.email || fallbackEmail,
      firstName,
      lastName,
      tenantId,
      role: businessRole,
      permissions: [...legalPermissions],
      legalPermissionsAuthoritative: hasLegalPermissionProjection,
      membershipRevision,
      businessRoleRevision,
      mfaRegistered: true,
    },
    tenant: authenticatedTenantProjection(
      tenantProjection,
      tenantId,
      branding,
    ),
  };
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Persisted bearer material is only a candidate. It remains unanchored until
  // Python EOS revalidates it through workspace-bootstrap.
  const [token, setToken] = useState(null);
  const [tenant, setTenant] = useState(() => readPersistedDiscoveredTenant());
  const [authStage, setAuthStage] = useState(AUTH_STATES.IDLE);
  const [pendingEmail, setPendingEmail] = useState('');
  const [qrCodeData, setQrCodeData] = useState(null);
  const [mfaTempToken, setMfaTempToken] = useState(null);
  const [loading, setLoading] = useState(
    () => Boolean(readPersistedAccessTokenCandidate()),
  );
  const [error, setError] = useState(null);

  const isAuthenticated = Boolean(token && user && authStage === AUTH_STATES.AUTHENTICATED);
  const mfaRequired = [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage);

  useEffect(() => {
    let active = true;
    const candidateToken = readPersistedAccessTokenCandidate();

    if (!candidateToken) {
      anchorCanonicalBearer(null);
      setLoading(false);
      return () => { active = false; };
    }

    const restore = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.get('/auth/workspace-bootstrap', {
          headers: {
            Authorization: `Bearer ${candidateToken}`,
          },
        });
        if (!active) return;

        const persistedUser = readPersistedUserProjection();
        const authoritative = boundedWorkspaceProjection(
          response?.data || {},
          persistedUser?.email || '',
        );

        const persistedPrincipalId = String(persistedUser?.id || '').trim();
        if (
          persistedPrincipalId
          && persistedPrincipalId !== authoritative.user.id
        ) {
          throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
        }

        const discoveredTenant = readPersistedDiscoveredTenant();
        const discoveredTenantId = String(
          discoveredTenant?.tenantId || '',
        ).trim();
        if (
          discoveredTenantId
          && discoveredTenantId !== authoritative.user.tenantId
        ) {
          throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
        }

        // Only the revalidated READY server projection may restore authority.
        anchorCanonicalBearer(candidateToken);
        localStorage.setItem('wilsy_auth_token', candidateToken);
        localStorage.setItem('token', candidateToken);
        localStorage.setItem(
          'wilsy_sovereign_user',
          JSON.stringify(authoritative.user),
        );
        localStorage.setItem(
          'wilsy_active_tenant',
          JSON.stringify(authoritative.tenant),
        );

        setToken(candidateToken);
        setUser(authoritative.user);
        setTenant(authoritative.tenant);
        setAuthStage(AUTH_STATES.AUTHENTICATED);
        emitAuthState(AUTH_STATES.AUTHENTICATED);
      } catch {
        if (!active) return;
        clearPersistedSessionAuthority();
        setToken(null);
        setUser(null);
        setTenant(readPersistedDiscoveredTenant());
        setAuthStage(AUTH_STATES.IDLE);
        setError(null);
        emitAuthState(AUTH_STATES.IDLE);
      } finally {
        if (active) setLoading(false);
      }
    };

    void restore();
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`;
    else delete api.defaults.headers.common.Authorization;
    if (tenant?.tenantId) api.defaults.headers.common['x-tenant-id'] = tenant.tenantId;
    else delete api.defaults.headers.common['x-tenant-id'];
  }, [token, tenant]);

  const discoverTenant = useCallback(async (tenantAlias) => {
    const alias = String(tenantAlias || '').trim().toLowerCase();
    if (!alias) throw new Error('Enter an organization or workspace identifier.');
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/auth/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ alias }),
      });
      const data = await parseJsonResponse(response);
      if (!response.ok || !data.success || !data.tenant?.tenantId) {
        throw new Error(data.message || data.detail || 'Organization or workspace was not found.');
      }
      const authoritativeTenant = data.tenant;
      setTenant(authoritativeTenant);
      localStorage.setItem('discoveredTenant', JSON.stringify(authoritativeTenant));
      // TenantProvider hydrates this key as a bounded tenant projection; keep
      // the server-issued shape so the authenticated context cannot degrade to
      // an identifier-only or inferred tenant record.
      localStorage.setItem('wilsy_active_tenant', JSON.stringify(authoritativeTenant));
      return authoritativeTenant;
    } catch (discoveryError) {
      setTenant(null);
      localStorage.removeItem('discoveredTenant');
      localStorage.removeItem('wilsy_active_tenant');
      setError(discoveryError.message || 'Organization discovery is unavailable.');
      throw discoveryError;
    } finally {
      setLoading(false);
    }
  }, []);

  const persistSession = useCallback(async (session, fallbackEmail = '') => {
    const candidateToken = String(session?.token || '').trim();
    const candidatePrincipalId = String(session?.user?.id || '').trim();

    if (!candidateToken || !candidatePrincipalId) {
      throw new Error('AUTHENTICATED_SESSION_CANDIDATE_INVALID');
    }

    // Candidate credentials are not browser authority. Python EOS must first
    // re-resolve current principal, membership, business role, and tenant truth.
    const response = await api.get('/auth/workspace-bootstrap', {
      headers: {
        Authorization: `Bearer ${candidateToken}`,
      },
    });

    const authoritative = boundedWorkspaceProjection(
      response?.data || {},
      fallbackEmail || session?.user?.email || '',
    );

    if (authoritative.user.id !== candidatePrincipalId) {
      throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
    }

    const discoveredTenantId = String(tenant?.tenantId || '').trim();
    if (
      discoveredTenantId
      && discoveredTenantId !== authoritative.user.tenantId
    ) {
      throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
    }

    // Only the READY server-owned projection may establish browser authority.
    anchorCanonicalBearer(candidateToken);

    localStorage.setItem('wilsy_auth_token', candidateToken);
    localStorage.setItem('token', candidateToken);
    localStorage.setItem(
      'wilsy_sovereign_user',
      JSON.stringify(authoritative.user),
    );
    localStorage.setItem(
      'wilsy_active_tenant',
      JSON.stringify(authoritative.tenant),
    );

    if (session.refreshToken) {
      localStorage.setItem('wilsy_refresh_token', session.refreshToken);
    } else {
      localStorage.removeItem('wilsy_refresh_token');
    }

    setToken(candidateToken);
    setUser(authoritative.user);
    setTenant(authoritative.tenant);
    setAuthStage(AUTH_STATES.AUTHENTICATED);
    emitAuthState(AUTH_STATES.AUTHENTICATED);

    return {
      token: candidateToken,
      user: authoritative.user,
      tenant: authoritative.tenant,
    };
  }, [tenant]);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    setAuthStage(AUTH_STATES.PRIMARY_AUTHENTICATING);
    try {
      const response = await api.post('/auth/login', { email, password });
      const data = response.data || {};
      const currentStatus = data.status;
      if (![AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, 'AUTHENTICATED'].includes(currentStatus)) {
        throw new Error('Authentication service returned an unrecognized state.');
      }
      setPendingEmail(email);
      setMfaTempToken(data.tempToken || null);
      if (currentStatus === AUTH_STATES.MFA_SETUP) {
        if (!data.qrCode) throw new Error('First-time MFA setup did not return a provisioning QR.');
        setQrCodeData(data.qrCode);
        setAuthStage(AUTH_STATES.MFA_SETUP);
      } else if (currentStatus === AUTH_STATES.MFA_RECONCILIATION_REQUIRED) {
        setQrCodeData(null);
        setAuthStage(AUTH_STATES.MFA_RECONCILIATION_REQUIRED);
      } else if (currentStatus === AUTH_STATES.MFA_REQUIRED) {
        setQrCodeData(null);
        setAuthStage(AUTH_STATES.MFA_REQUIRED);
      } else {
        const promoted = await persistSession(
          {
            ...candidateSessionProjection(data, email),
            refreshToken: data.refreshToken,
          },
          email,
        );
        return {
          ...data,
          email,
          status: currentStatus,
          token: promoted.token,
          user: promoted.user,
        };
      }
      return { ...data, email, status: currentStatus };
    } catch (loginError) {
      setAuthStage(AUTH_STATES.FAILED);
      setError(loginError?.response?.data?.detail || loginError?.response?.data?.message || loginError.message || 'Authentication failed.');
      throw loginError;
    } finally {
      setLoading(false);
    }
  }, [persistSession]);

  const verifyOTP = useCallback(async (email, code, _biometricAssertion = null, _traceId = null, mfaSetup = false) => {
    const targetEmail = email || pendingEmail;
    const targetCode = String(code || '').trim();
    if (!/^\d{6}$/.test(targetCode)) throw new Error('Enter the current six-digit code from your authenticator app.');
    setLoading(true);
    setError(null);
    setAuthStage(AUTH_STATES.MFA_VERIFYING);
    try {
      const endpoint = mfaSetup || authStage === AUTH_STATES.MFA_SETUP ? '/auth/validate-mfa-setup' : '/auth/verify-otp';
      const response = await api.post(endpoint, { email: targetEmail, code: targetCode });
      const data = response.data || {};
      const candidate = candidateSessionProjection(data, targetEmail);
      const promoted = await persistSession(
        { ...candidate, refreshToken: data.refreshToken },
        targetEmail,
      );
      setPendingEmail('');
      setQrCodeData(null);
      setMfaTempToken(null);
      return {
        ...data,
        success: true,
        token: promoted.token,
        user: promoted.user,
      };
    } catch (verificationError) {
      setAuthStage(AUTH_STATES.FAILED);
      setError(verificationError?.response?.data?.detail || verificationError?.response?.data?.message || verificationError.message || 'Identity verification failed.');
      throw verificationError;
    } finally {
      setLoading(false);
    }
  }, [authStage, pendingEmail, persistSession]);

  const updateSovereignIdentity = useCallback(async (updates) => {
    if (!user) throw new Error('No authenticated identity is available.');
    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify(updatedUser));
    return updatedUser;
  }, [user]);

  const logout = useCallback(async () => {
    try {
      if (token) await api.post('/auth/logout');
    } catch {
      // Local purge is still required; server logout is best-effort.
    } finally {
      anchorCanonicalBearer(null);
      setToken(null);
      setUser(null);
      setTenant(null);
      setAuthStage(AUTH_STATES.IDLE);
      setPendingEmail('');
      setQrCodeData(null);
      setMfaTempToken(null);
      localStorage.removeItem('wilsy_auth_token');
      localStorage.removeItem('token');
      localStorage.removeItem('wilsy_sovereign_user');
      localStorage.removeItem('wilsy_refresh_token');
      localStorage.removeItem('discoveredTenant');
      localStorage.removeItem('wilsy_active_tenant');
      emitAuthState(AUTH_STATES.IDLE);
    }
  }, [token]);

  const value = useMemo(() => ({
    user,
    token,
    isAuthenticated,
    tenant,
    tenantId: user?.tenantId || tenant?.tenantId || null,
    userRole: user?.role || null,
    authStage,
    mfaRequired,
    pendingEmail,
    qrCodeData,
    mfaTempToken,
    loading,
    error,
    discoverTenant,
    login,
    verifyOTP,
    verify3FA: (code) => verifyOTP(pendingEmail, code),
    logout,
    updateSovereignIdentity,
    setAuthStage,
    publicAuthPaths,
  }), [user, token, isAuthenticated, tenant, authStage, mfaRequired, pendingEmail, qrCodeData, mfaTempToken, loading, error, discoverTenant, login, verifyOTP, logout, updateSovereignIdentity]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be executed within an active AuthProvider.');
  return context;
};

export default AuthContext;

/**
 * ARTIFACT: client/src/contexts/authContext.jsx
 * VERSION: v55.0.0-D21B8-TENANT-BRANDING-AUTHCONTEXT-PROJECTION
 * AUTHORITY BOUNDARY: browser projection only; workspace branding is exact D21B7 presentation provenance, workspace firstName/lastName are descriptive authenticated-person projection, and workspace legalPermissions are presentation provenance from Python EOS; none is browser authorization authority and Python EOS owns authentication/authorization/branding truth
 * TENANT POSTURE: authenticated tenant must match the discovered server-issued tenant and any non-null D21B7 branding tenant must match that exact workspace tenant
 * FAIL-CLOSED POSTURE: unrecognized/incomplete workspace responses, absent/malformed/foreign branding, malformed principal names, and malformed/duplicate/unknown legalPermissions fail closed; explicit branding null is authoritative no-branding, legacy branding aliases are removed, optional names are never inferred, and absent legalPermissions retains legacy role-baseline presentation only
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * CHANGELOG: v55.0.0-D21B8-TENANT-BRANDING-AUTHCONTEXT-PROJECTION — Carries only exact READY workspace.branding into authenticated tenant state, requires explicit null/configured branding provenance, strictly validates the D21B6 schema, strips legacy branding aliases, and prevents discovery/login/MFA/persisted/JWT branding from becoming authenticated authority.
 *            v54.0.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION — Carries only READY workspace-bootstrap firstName/lastName into authenticated browser state; login/MFA/persisted names are never promoted and malformed server name values fail closed.
 *            v53.0.0-D17-SERVER-LEGAL-PERMISSION-PROJECTION — Preserves the bounded server-owned Legal permission
 * projection plus explicit provenance for presentation narrowing without trusting
 * browser/JWT/login permission claims.
 *            v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE — Persisted bearer
 * candidates are restored only after Python EOS workspace-bootstrap revalidates
 * current principal, tenant membership, business role and canonical tenant.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
