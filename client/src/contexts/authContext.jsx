/**
 * TITLE: WILSY OS Authoritative Browser Authentication Context
 * VERSION: v58.1.0-SESSION-OPERATION-CURRENTNESS
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Represents server-issued authentication and MFA challenge state
 *          without fabricating tenant, role, permission, or enrollment truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/authContext.jsx
 * COLLABORATION / OWNERSHIP: Python EOS auth_router owns credential/MFA truth;
 *                            this context owns browser projection and navigation state.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG: 2026-11-09 v58.1.0-SESSION-OPERATION-CURRENTNESS deduplicates
 *            current candidate bootstrap reads and invalidates superseded auth
 *            operations before logout, discovery, login or MFA can publish state.
 *            Explicit bearers remain candidates until EOS revalidation; session
 *            generation keys downstream legal/business projections.
 *            2026-11-08 v58.0.0-WILSY-HEADQUARTERS-WORKSPACE-PROJECTION admits WILSY_HEADQUARTERS as a server-issued
 *            workspace identifier. It remains a presentation projection and
 *            requires the exact READY EOS workspace bootstrap contract.
 *            v57.0.0-LEGAL-CONFLICT-REVIEW-PRESENTATION-PROJECTION accepted the canonical conflict-review write permission
 *            in the closed workspace Legal presentation set. The permission remains server-derived, exact, and non-authorizing in the browser; unknown, duplicate, or malformed values still fail closed.
 *            v56.0.0-L10-P2C6-BRANDING-AUTHORITY-REFRESH — Exposes a
 *            server-revalidated workspace refresh seam for branding-management
 *            mutations; management responses never become AuthContext authority.
 *            v55.0.0-D21B8-TENANT-BRANDING-AUTHCONTEXT-PROJECTION — Accepts tenant branding only from the explicit READY workspace.branding projection produced by D21B7. The field is mandatory: null is authoritative lawful no-branding; configured branding must match the exact D21B6 browser-safe schema, exact tenant, closed tier/media/kind sets, canonical fingerprints/colours, and mandatory WILSY trust mark. Legacy tenant branding aliases are removed before authenticated tenant state is persisted, so discovery/login/MFA/local-storage/JWT branding cannot override Python EOS authority.
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

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import api, { setActiveTenantTransportId } from '@/services/api';

const WORKSPACE_CONTRACT_VERSION = 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION';
const WORKSPACE_ID_SET = new Set([
  'EXECUTIVE_COMMAND_CENTRE',
  'WILSY_HEADQUARTERS',
  'TENANT_ADMINISTRATION',
  'AUDIT_REPORTING',
  'TENANT_OPERATIONS',
  'LEGAL_PRACTICE',
  'LEGAL_FINANCE',
  'CLIENT_PORTAL',
  'PROCESS_SERVICE',
  'PEOPLE_OPERATIONS',
  'POINT_OF_SALE',
]);

const LEGAL_PRESENTATION_PERMISSION_SET = new Set([
  'legal_operations:conflict_review:write',
  'legal_operations:instruction:write',
  'legal_operations:return:write',
  'legal_operations:billing:read',
  'legal_operations:invoice:read',
  'legal_operations:matter_deadline:read',
  'legal_operations:matter_deadline:write',
  'legal_operations:productive_work:read',
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

/**
 * @description Closed browser states; only EOS revalidation may establish a session.
 * @institutional State labels grant no identity, membership or permission.
 */
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
  sessionStorage.removeItem('token');
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

const SYSTEM_SERVICES_CAPABILITY_SET = new Set([
  'system_services:queue:read',
  'system_services:identity:read',
  'system_services:incident:escalate',
]);

const boundedSystemServicesWorkspaceProjection = (
  value,
  expectedPrincipalId = '',
  fallbackEmail = '',
) => {
  const invalid = () => new Error('AUTHENTICATED_SYSTEM_SERVICES_WORKSPACE_INVALID');
  const expectedKeys = [
    'status', 'authority', 'principalId', 'scope',
    'capabilities', 'summary', 'cases',
  ];
  if (
    !value || typeof value !== 'object' || Array.isArray(value)
    || Object.keys(value).length !== expectedKeys.length
    || expectedKeys.some((key) => !Object.prototype.hasOwnProperty.call(value, key))
    || value.status !== 'READY'
    || value.authority !== 'EOS_SYSTEM_SERVICES'
    || value.scope !== 'SYSTEM'
    || typeof value.principalId !== 'string'
    || !value.principalId
    || value.principalId !== value.principalId.trim()
    || (expectedPrincipalId && value.principalId !== expectedPrincipalId)
    || !Array.isArray(value.capabilities)
    || value.capabilities.length === 0
    || new Set(value.capabilities).size !== value.capabilities.length
    || value.capabilities.some((item) => (
      typeof item !== 'string' || !SYSTEM_SERVICES_CAPABILITY_SET.has(item)
    ))
    || !value.capabilities.includes('system_services:queue:read')
    || !value.summary || typeof value.summary !== 'object'
    || Array.isArray(value.summary)
    || Object.keys(value.summary).length !== 2
    || !['openCases', 'securityEscalations'].every(
      (key) => Object.prototype.hasOwnProperty.call(value.summary, key),
    )
    || !['openCases', 'securityEscalations'].every((key) => (
      Number.isSafeInteger(value.summary[key]) && value.summary[key] >= 0
    ))
    || !Array.isArray(value.cases)
  ) {
    throw invalid();
  }

  const cases = value.cases.map((item) => {
    const keys = ['caseId', 'reference', 'category', 'status'];
    if (
      !item || typeof item !== 'object' || Array.isArray(item)
      || Object.keys(item).length !== keys.length
      || keys.some((key) => !Object.prototype.hasOwnProperty.call(item, key))
      || keys.some((key) => (
        typeof item[key] !== 'string' || !item[key] || item[key] !== item[key].trim()
      ))
    ) {
      throw invalid();
    }
    return {
      caseId: item.caseId,
      reference: item.reference,
      category: item.category,
      status: item.status,
    };
  });

  return {
    user: {
      id: value.principalId,
      email: typeof fallbackEmail === 'string' ? fallbackEmail : '',
      role: 'SYSTEM_SERVICES',
      workspaceId: 'SYSTEM_SERVICES',
      systemServicesWorkspace: {
        status: value.status,
        authority: value.authority,
        principalId: value.principalId,
        scope: value.scope,
        capabilities: [...value.capabilities],
        summary: {
          openCases: value.summary.openCases,
          securityEscalations: value.summary.securityEscalations,
        },
        cases,
      },
    },
    tenant: null,
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
  const workspaceId = String(workspace?.workspaceId || '').trim();
  const workspaceContractVersion = String(workspace?.workspaceContractVersion || '').trim();
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
    || workspaceContractVersion !== WORKSPACE_CONTRACT_VERSION
    || !WORKSPACE_ID_SET.has(workspaceId)
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
      workspaceId,
      workspaceContractVersion,
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

const authenticatedSystemServicesUser = (projection, principalId, email) => {
  if (
    !projection
    || projection.status !== 'READY'
    || projection.authority !== 'EOS_SYSTEM_SERVICES'
    || projection.scope !== 'SYSTEM'
    || projection.principalId !== principalId
    || !Array.isArray(projection.capabilities)
    || projection.capabilities.length > 16
    || new Set(projection.capabilities).size !== projection.capabilities.length
    || !projection.capabilities.includes('system_services:queue:read')
    || !projection.capabilities.every((value) => [
      'system_services:queue:read',
      'system_services:identity:read',
      'system_services:incident:escalate',
    ].includes(value))
    || !projection.summary
    || !Number.isInteger(projection.summary.openCases)
    || projection.summary.openCases < 0
    || !Number.isInteger(projection.summary.securityEscalations)
    || projection.summary.securityEscalations < 0
    || !Array.isArray(projection.cases)
    || projection.cases.length > 100
  ) {
    throw new Error('SYSTEM_WORKSPACE_PROJECTION_INVALID');
  }
  const cases = projection.cases.map((item) => {
    if (
      !item
      || typeof item.caseId !== 'string'
      || !item.caseId
      || item.reference !== item.caseId
      || typeof item.category !== 'string'
      || typeof item.status !== 'string'
    ) throw new Error('SYSTEM_WORKSPACE_CASE_PROJECTION_INVALID');
    return {
      caseId: item.caseId,
      reference: item.reference,
      category: item.category,
      status: item.status,
    };
  });
  return {
    id: principalId,
    email,
    role: 'SYSTEM_SERVICES',
    workspaceId: 'SYSTEM_SERVICES',
    systemServicesWorkspace: {
      status: projection.status,
      authority: projection.authority,
      scope: projection.scope,
      principalId: projection.principalId,
      capabilities: [...projection.capabilities],
      summary: {
        openCases: projection.summary.openCases,
        securityEscalations: projection.summary.securityEscalations,
      },
      cases,
    },
  };
};

/**
 * @description Own one browser session operation and project only EOS-validated
 * identity, exact membership/capacity revisions and workspace truth.
 * @collaboration App admission, TenantProvider, canonical API and MFA portals.
 * @institutional Candidates remain untrusted; logout/switch invalidates all
 * superseded operations. No server transaction, IAM or financial authority is owned.
 * @param {{children: React.ReactNode}} props Browser application subtree.
 * @returns {JSX.Element} A session-current authenticated context provider.
 */
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
  const [globalMfaChallenge, setGlobalMfaChallenge] = useState(null);
  const [loading, setLoading] = useState(
    () => Boolean(readPersistedAccessTokenCandidate()),
  );
  const [error, setError] = useState(null);


  const authEpochRef = useRef(0);
  const mountedRef = useRef(true);
  const bootstrapReadsRef = useRef(new Map());
  const [sessionGeneration, setSessionGeneration] = useState(0);

  // One in-flight read per exact credential/path; settled results are never
  // cached as session authority. Strict Mode reuses the pending request only.
  const readWorkspace = useCallback((candidateToken, path = '/auth/workspace-bootstrap') => {
    const key = path + ':' + candidateToken;
    const existing = bootstrapReadsRef.current.get(key);
    if (existing) return existing.promise;
    const controller = new AbortController();
    const entry = { controller, promise: null };
    const promise = api.get(path, {
      headers: { Authorization: `Bearer ${candidateToken}` },
      skipAuthRedirect: true,
      signal: controller.signal,
    }).finally(() => {
      if (bootstrapReadsRef.current.get(key) === entry) {
        bootstrapReadsRef.current.delete(key);
      }
    });
    entry.promise = promise;
    bootstrapReadsRef.current.set(key, entry);
    return promise;
  }, []);

  const invalidateSession = useCallback(() => {
    authEpochRef.current += 1;
    for (const entry of bootstrapReadsRef.current.values()) entry.controller.abort();
    bootstrapReadsRef.current.clear();
    clearPersistedSessionAuthority();
    setActiveTenantTransportId(null);
    setToken(null);
    setUser(null);
    setSessionGeneration((generation) => generation + 1);
    return authEpochRef.current;
  }, []);

  const ensureCurrent = useCallback((epoch) => {
    if (!mountedRef.current || epoch !== authEpochRef.current) {
      throw new Error('AUTHENTICATION_OPERATION_SUPERSEDED');
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      // Strict Mode immediately reacquires the same mounted owner. A real
      // unmount cancels its requests after that synchronous ownership decision.
      queueMicrotask(() => {
        if (!mountedRef.current) {
          for (const entry of bootstrapReadsRef.current.values()) entry.controller.abort();
          bootstrapReadsRef.current.clear();
        }
      });
    };
  }, []);

  const isAuthenticated = Boolean(token && user && authStage === AUTH_STATES.AUTHENTICATED);
  const mfaRequired = [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage);

  useEffect(() => {
    let active = true;
    const epoch = ++authEpochRef.current;
    const isCurrent = () => active && mountedRef.current && epoch === authEpochRef.current;
    const candidateToken = readPersistedAccessTokenCandidate();

    if (!candidateToken) {
      anchorCanonicalBearer(null);
      setActiveTenantTransportId(null);
      setLoading(false);
      return () => { active = false; };
    }

    const restore = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await readWorkspace(candidateToken);
        if (!isCurrent()) return;

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
        setActiveTenantTransportId(authoritative.user.tenantId);
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
        if (!isCurrent()) return;

        // A tenant workspace denial may be a platform SYSTEM principal. It is
        // never promoted from a role label: EOS must independently authorize
        // and return the exact SYSTEM workspace projection. A selected tenant
        // remains a hard boundary and cannot be bypassed by this fallback.
        let systemWorkspace = null;
        const discoveredTenant = readPersistedDiscoveredTenant();
        const persistedUser = readPersistedUserProjection();
        const persistedPrincipalId = String(persistedUser?.id || '').trim();
        if (!discoveredTenant?.tenantId && persistedPrincipalId) {
          try {
            const response = await readWorkspace(candidateToken, '/system-services/workspace-bootstrap');
            if (!isCurrent()) return;
            systemWorkspace = boundedSystemServicesWorkspaceProjection(
              response?.data || {},
              persistedPrincipalId,
              persistedUser?.email || '',
            );
          } catch {
            systemWorkspace = null;
          }
        }

        if (!isCurrent()) return;
        if (systemWorkspace) {
          anchorCanonicalBearer(candidateToken);
          setActiveTenantTransportId(null);
          localStorage.setItem('wilsy_auth_token', candidateToken);
          localStorage.setItem('token', candidateToken);
          localStorage.setItem(
            'wilsy_sovereign_user',
            JSON.stringify(systemWorkspace.user),
          );
          localStorage.removeItem('wilsy_active_tenant');
          localStorage.removeItem('tenantId');
          localStorage.removeItem('wilsy_tenant_id');
          setToken(candidateToken);
          setUser(systemWorkspace.user);
          setTenant(null);
          setAuthStage(AUTH_STATES.AUTHENTICATED);
          setError(null);
          emitAuthState(AUTH_STATES.AUTHENTICATED);
        } else {
          clearPersistedSessionAuthority();
          setActiveTenantTransportId(null);
          setToken(null);
          setUser(null);
          setTenant(readPersistedDiscoveredTenant());
          setAuthStage(AUTH_STATES.IDLE);
          setError(null);
          emitAuthState(AUTH_STATES.IDLE);
        }
      } finally {
        if (isCurrent()) setLoading(false);
      }
    };

    void restore();
    return () => { active = false; };
  }, [readWorkspace]);

  useEffect(() => {
    if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`;
    else delete api.defaults.headers.common.Authorization;
    setActiveTenantTransportId(token && user?.tenantId ? user.tenantId : null);
  }, [token, user?.tenantId]);

  const discoverTenant = useCallback(async (tenantAlias) => {
    const alias = String(tenantAlias || '').trim().toLowerCase();
    if (!alias) throw new Error('Enter an organization or workspace identifier.');
    const epoch = invalidateSession();
    setAuthStage(AUTH_STATES.IDLE);
    setLoading(true);
    setError(null);
    setActiveTenantTransportId(null);
    try {
      const response = await fetch('/api/auth/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ alias }),
      });
      const data = await parseJsonResponse(response);
      ensureCurrent(epoch);
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
      if (epoch !== authEpochRef.current || !mountedRef.current) throw discoveryError;
      setTenant(null);
      localStorage.removeItem('discoveredTenant');
      localStorage.removeItem('wilsy_active_tenant');
      setError(discoveryError.message || 'Organization discovery is unavailable.');
      throw discoveryError;
    } finally {
      if (epoch === authEpochRef.current && mountedRef.current) setLoading(false);
    }
  }, [ensureCurrent, invalidateSession]);

  const persistSession = useCallback(async (session, fallbackEmail = '', epoch = authEpochRef.current) => {
    ensureCurrent(epoch);
    const candidateToken = String(session?.token || '').trim();
    const candidatePrincipalId = String(session?.user?.id || '').trim();

    if (!candidateToken || !candidatePrincipalId) {
      throw new Error('AUTHENTICATED_SESSION_CANDIDATE_INVALID');
    }

    // Candidate credentials are not browser authority. Python EOS must first
    // re-resolve current principal, membership, business role, and tenant truth.
    const response = await readWorkspace(candidateToken);
    ensureCurrent(epoch);

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
    setActiveTenantTransportId(authoritative.user.tenantId);

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
  }, [ensureCurrent, readWorkspace, tenant]);

  const refreshWorkspace = useCallback(async () => {
    if (!token) throw new Error('AUTHENTICATED_WORKSPACE_REFRESH_REQUIRES_SESSION');
    const epoch = authEpochRef.current;
    const response = await readWorkspace(token);
    ensureCurrent(epoch);
    const authoritative = boundedWorkspaceProjection(
      response?.data || {},
      user?.email || '',
    );
    const currentTenantId = String(tenant?.tenantId || '').trim();
    if (authoritative.user.id !== user?.id || (currentTenantId && currentTenantId !== authoritative.user.tenantId)) {
      throw new Error('AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH');
    }
    setSessionGeneration((generation) => generation + 1);
    setUser(authoritative.user);
    setTenant(authoritative.tenant);
    setActiveTenantTransportId(authoritative.user.tenantId);
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify(authoritative.user));
    localStorage.setItem('wilsy_active_tenant', JSON.stringify(authoritative.tenant));
    return authoritative;
  }, [ensureCurrent, readWorkspace, tenant, token, user?.id, user?.email]);

  useEffect(() => {
    if (!token || !user?.systemServicesWorkspace) return undefined;
    let active = true;
    const epoch = authEpochRef.current;
    let refreshing = false;
    const refreshSystemSession = async () => {
      if (refreshing) return;
      const refreshToken = localStorage.getItem('wilsy_refresh_token');
      if (!refreshToken) return;
      refreshing = true;
      try {
        const response = await api.post(
          '/auth/global/refresh',
          { refresh_token: refreshToken },
          { skipAuth: true, skipAuthRedirect: true },
        );
        const data = response?.data || {};
        if (
          !active
          || epoch !== authEpochRef.current
          || data.status !== 'REFRESHED'
          || data.scope !== 'SYSTEM'
          || typeof data.access_token !== 'string'
          || typeof data.refresh_token !== 'string'
        ) throw new Error('SYSTEM_SESSION_REFRESH_PROJECTION_INVALID');
        anchorCanonicalBearer(data.access_token);
        localStorage.setItem('wilsy_auth_token', data.access_token);
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('wilsy_refresh_token', data.refresh_token);
        setToken(data.access_token);
      } catch (refreshError) {
        if (active && epoch === authEpochRef.current) {
          setError(refreshError?.response?.data?.detail || refreshError.message || 'SYSTEM_SESSION_REFRESH_FAILED');
        }
      } finally {
        refreshing = false;
      }
    };
    const interval = window.setInterval(refreshSystemSession, 10 * 60 * 1000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [token, user?.systemServicesWorkspace]);

  useEffect(() => {
    const handleBrandingAuthorityRefresh = () => {
      const epoch = authEpochRef.current;
      void refreshWorkspace().catch((refreshError) => {
        if (!mountedRef.current || epoch !== authEpochRef.current) return;
        setError(refreshError?.message || 'AUTHENTICATED_WORKSPACE_REFRESH_FAILED');
      });
    };
    if (typeof window !== 'undefined') {
      window.addEventListener('wilsy-branding-authority-refresh-request', handleBrandingAuthorityRefresh);
      return () => window.removeEventListener('wilsy-branding-authority-refresh-request', handleBrandingAuthorityRefresh);
    }
    return undefined;
  }, [refreshWorkspace]);

  const login = useCallback(async (email, password, discoveredTenantId = tenant?.tenantId) => {
    const tenantId = String(discoveredTenantId || '').trim();
    const epoch = invalidateSession();
    setLoading(true);
    setError(null);
    setAuthStage(AUTH_STATES.PRIMARY_AUTHENTICATING);
    try {
      if (!tenantId) {
        anchorCanonicalBearer(null);
        setActiveTenantTransportId(null);
        localStorage.removeItem('wilsy_active_tenant');
        localStorage.removeItem('wilsy_tenant_id');
        localStorage.removeItem('tenantId');
        const response = await api.post('/auth/global/login', { email, password });
        ensureCurrent(epoch);
        const data = response.data || {};
        if (
          data.status !== AUTH_STATES.MFA_REQUIRED
          || data.scope !== 'SYSTEM'
          || typeof data.mfa_challenge !== 'string'
          || !data.mfa_challenge.startsWith('sysmfa_')
        ) {
          throw new Error('Global sign-in did not return an authorized SYSTEM MFA challenge.');
        }
        setPendingEmail(email);
        setGlobalMfaChallenge(data.mfa_challenge);
        setMfaTempToken(null);
        setQrCodeData(null);
        setAuthStage(AUTH_STATES.MFA_REQUIRED);
        return { ...data, status: AUTH_STATES.MFA_REQUIRED };
      }

      const response = await api.post('/auth/login', { email, password, tenant_id: tenantId });
      const data = response.data || {};
      const currentStatus = data.status;
      if (![AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, 'AUTHENTICATED'].includes(currentStatus)) {
        throw new Error('Authentication service returned an unrecognized state.');
      }
      setPendingEmail(email);
      setMfaTempToken(data.tempToken || null);
      setGlobalMfaChallenge(null);
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
          epoch,
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
      if (epoch !== authEpochRef.current || !mountedRef.current) throw loginError;
      setAuthStage(AUTH_STATES.FAILED);
      setError(loginError?.response?.data?.detail || loginError?.response?.data?.message || loginError.message || 'Authentication failed.');
      throw loginError;
    } finally {
      if (epoch === authEpochRef.current && mountedRef.current) setLoading(false);
    }
  }, [ensureCurrent, invalidateSession, persistSession, tenant]);

  const verifyOTP = useCallback(async (email, code, _biometricAssertion = null, _traceId = null, mfaSetup = false, discoveredTenantId = tenant?.tenantId) => {
    const targetEmail = email || pendingEmail;
    const targetCode = String(code || '').trim();
    if (!/^\d{6}$/.test(targetCode)) throw new Error('Enter the current six-digit code from your authenticator app.');
    const epoch = invalidateSession();
    setLoading(true);
    setError(null);
    setAuthStage(AUTH_STATES.MFA_VERIFYING);
    try {
      if (globalMfaChallenge) {
        const response = await api.post('/auth/global/verify-mfa', {
          mfa_challenge: globalMfaChallenge,
          code: targetCode,
        });
        ensureCurrent(epoch);
        const data = response.data || {};
        if (
          data.status !== 'AUTHENTICATED'
          || data.scope !== 'SYSTEM'
          || typeof data.access_token !== 'string'
          || typeof data.refresh_token !== 'string'
          || !data.refresh_token.startsWith('sysrefresh_')
          || typeof data.principal_id !== 'string'
          || data.workspace_id !== 'SYSTEM_SERVICES'
        ) throw new Error('EOS did not issue a valid SYSTEM session.');

        try {
          const workspaceResponse = await readWorkspace(data.access_token, '/system-services/workspace-bootstrap');
          ensureCurrent(epoch);
          const projectedUser = authenticatedSystemServicesUser(
            workspaceResponse?.data || {},
            data.principal_id,
            targetEmail,
          );
          anchorCanonicalBearer(data.access_token);
          setActiveTenantTransportId(null);
          localStorage.setItem('wilsy_auth_token', data.access_token);
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('wilsy_refresh_token', data.refresh_token);
          localStorage.setItem('wilsy_sovereign_user', JSON.stringify(projectedUser));
          localStorage.removeItem('wilsy_active_tenant');
          localStorage.removeItem('wilsy_tenant_id');
          localStorage.removeItem('tenantId');
          localStorage.removeItem('discoveredTenant');
          setToken(data.access_token);
          setUser(projectedUser);
          setTenant(null);
          setGlobalMfaChallenge(null);
          setPendingEmail('');
          setQrCodeData(null);
          setMfaTempToken(null);
          setAuthStage(AUTH_STATES.AUTHENTICATED);
          emitAuthState(AUTH_STATES.AUTHENTICATED);
          return { ...data, success: true, token: data.access_token, user: projectedUser };
        } catch (projectionError) {
          ensureCurrent(epoch);
          anchorCanonicalBearer(null);
          setActiveTenantTransportId(null);
          throw projectionError;
        }
      }

      const tenantId = String(discoveredTenantId || '').trim();
      if (!tenantId) throw new Error('Discover your organization before verifying identity.');
      const endpoint = mfaSetup || authStage === AUTH_STATES.MFA_SETUP ? '/auth/validate-mfa-setup' : '/auth/verify-otp';
      const response = await api.post(endpoint, { email: targetEmail, code: targetCode, tenant_id: tenantId });
      const data = response.data || {};
      const candidate = candidateSessionProjection(data, targetEmail);
      const promoted = await persistSession(
        { ...candidate, refreshToken: data.refreshToken },
        targetEmail,
        epoch,
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
      if (epoch !== authEpochRef.current || !mountedRef.current) throw verificationError;
      setAuthStage(AUTH_STATES.FAILED);
      setError(verificationError?.response?.data?.detail || verificationError?.response?.data?.message || verificationError.message || 'Identity verification failed.');
      throw verificationError;
    } finally {
      if (epoch === authEpochRef.current && mountedRef.current) setLoading(false);
    }
  }, [authStage, ensureCurrent, globalMfaChallenge, invalidateSession, pendingEmail, persistSession, readWorkspace, tenant]);

  const updateSovereignIdentity = useCallback(async (updates) => {
    if (!user) throw new Error('No authenticated identity is available.');
    if (Object.keys(updates || {}).some((key) => key !== 'hasSignedCovenant')) {
      throw new Error('AUTHENTICATED_IDENTITY_MUTATION_REQUIRES_EOS');
    }
    // Compatibility display hint only; admission always re-reads EOS evidence.
    const updatedUser = { ...user, hasSignedCovenant: updates?.hasSignedCovenant === true };
    setUser(updatedUser);
    localStorage.setItem('wilsy_sovereign_user', JSON.stringify(updatedUser));
    return updatedUser;
  }, [user]);

  const logout = useCallback(async () => {
    const previousToken = token;
    const path = user?.systemServicesWorkspace ? '/auth/global/logout' : '/auth/logout';
    invalidateSession();
    setTenant(null);
    setAuthStage(AUTH_STATES.IDLE);
    setLoading(false);
    setError(null);
    setPendingEmail('');
    setQrCodeData(null);
    setMfaTempToken(null);
    setGlobalMfaChallenge(null);
    localStorage.removeItem('discoveredTenant');
    emitAuthState(AUTH_STATES.IDLE);
    // Local invalidation precedes network I/O. A delayed logout response cannot
    // clear a later session; only the old explicit credential is submitted.
    if (previousToken) {
      try {
        await api.post(path, {}, {
          headers: { Authorization: `Bearer ${previousToken}` },
          skipAuthRedirect: true,
        });
      } catch {
        console.error('[AUTH] LOGOUT_SERVER_CONFIRMATION_UNAVAILABLE');
      }
    }
  }, [invalidateSession, token, user]);

  useEffect(() => {
    const invalidate = () => {
      invalidateSession();
      setAuthStage(AUTH_STATES.IDLE);
      setLoading(false);
      setError('SESSION_EXPIRED');
      emitAuthState(AUTH_STATES.IDLE);
    };
    window.addEventListener('wilsy:session-invalidated', invalidate);
    return () => window.removeEventListener('wilsy:session-invalidated', invalidate);
  }, [invalidateSession]);

  const value = useMemo(() => ({
    user,
    token,
    sessionGeneration,
    isAuthenticated,
    tenant,
    tenantId: user?.tenantId || tenant?.tenantId || null,
    userRole: user?.role || null,
    authStage,
    mfaRequired,
    pendingEmail,
    qrCodeData,
    mfaTempToken,
    globalMfaChallenge,
    loading,
    error,
    discoverTenant,
    login,
    verifyOTP,
    verify3FA: (code) => verifyOTP(pendingEmail, code, null, null, false, tenant?.tenantId),
    logout,
    updateSovereignIdentity,
    refreshWorkspace,
    setAuthStage,
    publicAuthPaths,
  }), [user, token, sessionGeneration, isAuthenticated, tenant, authStage, mfaRequired, pendingEmail, qrCodeData, mfaTempToken, globalMfaChallenge, loading, error, discoverTenant, login, verifyOTP, logout, updateSovereignIdentity, refreshWorkspace]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * @description Read the current provider-owned session projection.
 * @collaboration Authenticated UI, admission and workspace request consumers.
 * @institutional The context cannot replace server authorization or persisted
 * evidence. Public auth operations retain the provider's currentness guards.
 * @returns {Object} Current browser session and bounded authentication operations.
 * @throws {Error} If no AuthProvider owns this consumer.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be executed within an active AuthProvider.');
  return context;
};

export default AuthContext;

/**
 * ARTIFACT: client/src/contexts/authContext.jsx
 * VERSION: v58.1.0-SESSION-OPERATION-CURRENTNESS
 * AUTHORITY BOUNDARY: browser projection only; workspace branding is exact D21B7 presentation provenance, workspace firstName/lastName are descriptive authenticated-person projection, and workspace legalPermissions are presentation provenance from Python EOS; none is browser authorization authority and Python EOS owns authentication/authorization/branding truth
 * TENANT POSTURE: authenticated tenant must match the discovered server-issued tenant and any non-null D21B7 branding tenant must match that exact workspace tenant
 * FAIL-CLOSED POSTURE: unrecognized/incomplete workspace responses, absent/malformed/foreign branding, malformed principal names, and malformed/duplicate/unknown legalPermissions fail closed; explicit branding null is authoritative no-branding, legacy branding aliases are removed, optional names are never inferred, and absent legalPermissions retains legacy role-baseline presentation only
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * CHANGELOG: v58.1.0-SESSION-OPERATION-CURRENTNESS — Admits only the canonical server-projected conflict-review write permission into the closed Legal presentation set; browser state remains non-authorizing and malformed projections fail closed.
 *            v56.0.0-L10-P2C6-BRANDING-AUTHORITY-REFRESH — Refreshes exact READY workspace authority after a certified branding mutation request; management response fields never become AuthContext authority.
 *            v55.0.0-D21B8-TENANT-BRANDING-AUTHCONTEXT-PROJECTION — Carries only exact READY workspace.branding into authenticated tenant state, requires explicit null/configured branding provenance, strictly validates the D21B6 schema, strips legacy branding aliases, and prevents discovery/login/MFA/persisted/JWT branding from becoming authenticated authority.
 *            v54.0.0-D24B-AUTHENTICATED-PRINCIPAL-NAME-PROJECTION — Carries only READY workspace-bootstrap firstName/lastName into authenticated browser state; login/MFA/persisted names are never promoted and malformed server name values fail closed.
 *            v53.0.0-D17-SERVER-LEGAL-PERMISSION-PROJECTION — Preserves the bounded server-owned Legal permission
 * projection plus explicit provenance for presentation narrowing without trusting
 * browser/JWT/login permission claims.
 *            v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE — Persisted bearer
 * candidates are restored only after Python EOS workspace-bootstrap revalidates
 * current principal, tenant membership, business role and canonical tenant.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
