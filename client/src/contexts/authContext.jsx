/**
 * TITLE: WILSY OS Authoritative Browser Authentication Context
 * VERSION: v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Represents server-issued authentication and MFA challenge state
 *          without fabricating tenant, role, permission, or enrollment truth.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/authContext.jsx
 * COLLABORATION / OWNERSHIP: Python EOS auth_router owns credential/MFA truth;
 *                            this context owns browser projection and navigation state.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG: v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE — Restores a persisted
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
 * SECURITY / PRIVACY POSTURE: Persisted bearer material is candidate state only
 *                             and never becomes authority until Python EOS
 *                             revalidates it; no MFA secret or QR is inferred.
 * TENANT BOUNDARY: Tenant context is accepted only from the authoritative API response.
 * AUTHORITY BOUNDARY: Client projection only; Python EOS remains authentication truth.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
 */

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import api from '@/services/api';

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

const boundedWorkspaceProjection = (data, fallbackEmail = '') => {
  const principal = data?.user;
  const workspace = data?.workspace;
  const tenantProjection = workspace?.tenant;

  const principalId = String(principal?.id || '').trim();
  const tenantId = String(workspace?.tenantId || '').trim();
  const tenantProjectionId = String(tenantProjection?.tenantId || '').trim();
  const businessRole = String(workspace?.businessRole || '').trim();
  const membershipRevision = workspace?.membershipRevision;
  const businessRoleRevision = workspace?.businessRoleRevision;

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
      tenantId,
      role: businessRole,
      permissions: [],
      membershipRevision,
      businessRoleRevision,
      mfaRegistered: true,
    },
    tenant: {
      ...tenantProjection,
      tenantId,
    },
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
 * VERSION: v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE
 * AUTHORITY BOUNDARY: browser projection only; Python EOS owns authentication truth
 * TENANT POSTURE: authenticated tenant must match the discovered server-issued tenant
 * FAIL-CLOSED POSTURE: unrecognized or incomplete server responses fail closed
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * CHANGELOG: v52.0.0-SERVER-REVALIDATED-SESSION-RESTORE — Persisted bearer
 * candidates are restored only after Python EOS workspace-bootstrap revalidates
 * current principal, tenant membership, business role and canonical tenant.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
