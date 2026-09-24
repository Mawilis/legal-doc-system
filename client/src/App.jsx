/* eslint-disable */
/**
 * TITLE: WILSY OS Sovereign Application Root
 * VERSION: v20.0.0-LEGAL-ADMISSION-RELEASE-ROUTING
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Composes authenticated routing, exact tenant projection, legal
 *          admission release, and protected workspace presentation without
 *          promoting browser state into authentication or legal authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/App.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider owns browser auth projection;
 *                            TenantProvider owns bounded tenant projection;
 *                            Python EOS owns authentication, workspace and
 *                            legal-acceptance truth.
 * CERTIFICATION / UPDATE DATE: 2026-09-24
 * CHANGELOG:
 *   v20.0.0-LEGAL-ADMISSION-RELEASE-ROUTING — Promotes the legal boundary
 *     from REQUIRED to COMPLETE only when LegalAcceptanceGate reports the
 *     server-confirmed COMPLETE state, so the protected runtime mounts in the
 *     same browser session. Protected-route fallback now preserves an already
 *     discovered tenant by returning to login rather than forcing discovery,
 *     while authentication revalidation loading suppresses premature routing.
 *   v19.3.0-R10E25-RECOVERY-CONTACT-VERIFICATION-ROUTE — Added the public
 *     recovery-contact verification route.
 *   v19.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE — Established the
 *     server-owned versioned legal-acceptance boundary.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Client routing consumes only bounded server
 *                             projections. Authentication tokens, tenant
 *                             membership, legal evidence and legal release
 *                             remain server-owned authorities.
 * TENANT BOUNDARY: A persisted or discovered tenant is routing context only;
 *                  protected runtime still requires authenticated server
 *                  workspace bootstrap with an exact tenant match.
 * AUTHORITY BOUNDARY: Presentation and route composition only. Python EOS owns
 *                     authentication, membership, business-role, tenant and
 *                     legal-acceptance decisions.
 * FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive financial
 *                               execution and settlement authority.
 */

import React, { Suspense, useEffect, useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AUTH_STATES, AuthProvider, useAuth } from './contexts/authContext.jsx';
import { TenantProvider, useTenants } from './contexts/tenantContext';  // ✅ NEW IMPORT
import ErrorBoundary from './components/ErrorBoundary.jsx';
import { Loader2 } from 'lucide-react';
import { broadcastTelemetry } from './utils/telemetryHelper.js';

import SovereignLogin from './components/auth/SovereignLogin.jsx';
import PasswordRecoveryRequestPortal from './components/auth/PasswordRecoveryRequestPortal.jsx';
import RecoveryContactVerificationPortal from './components/auth/RecoveryContactVerificationPortal.jsx';
import PasswordResetPortal from './components/auth/PasswordResetPortal.jsx';
import TenantDiscovery from './components/sovereign/TenantDiscovery.jsx';
import LegalAcceptanceGate from './components/auth/LegalAcceptanceGate.jsx';
import SovereignDashboardController from './components/sovereign/SovereignDashboardController.jsx';
import SovereignMfaPortal from './components/auth/SovereignMfaPortal.jsx';
import Sovereign_TenantManager from './components/sovereign/Sovereign_TenantManager.jsx';
import LedgerExplorer from './components/billing/LedgerExplorer.jsx';
import api from './services/api';
import WilsyOSIntelligenceDockRuntime from './components/intelligence/WilsyOSIntelligenceDockRuntime.jsx';

import { SovereignOrchestrator, useSovereignMesh } from './components/sovereign/SovereignOrchestrator.jsx';
import { DataOrchestratorProvider, useSovereignData } from './components/sovereign/DataOrchestrator.jsx';

// 🛡️ Global development telemetry suppression flag.
const IS_DEV_MODE = import.meta.env.DEV;

/**
 * @description Permission guard for the Tenant Management System (TMS) cockpit.
 *              Only founders, superadmins, or users with explicit canManageTenants
 *              permission are allowed to access /tms.
 * @param {Object} props - Component props.
 * @param {Object} props.user - Authenticated user object from useAuth.
 * @param {React.ReactNode} props.children - Child components to render if authorized.
 * @returns {JSX.Element} The protected route or a redirect.
 * @collaboration AI Engineering (2026-08-07) – Institutional enforcement.
 * @institutional This guard ensures that tenant management operations are
 *                restricted to the highest‑authority roles, maintaining
 *                separation of duties and audit compliance.
 */
const ProtectedTmsRoute = ({ user, children }) => {
  const role = user?.role?.toLowerCase() || '';
  const isFounderOrSuperAdmin = ['superadmin', 'founder', 'omega'].includes(role) ||
    user?.isSuperAdmin ||
    user?.isFounder ||
    user?.isOmega;
  const hasExplicitPermission = user?.permissions?.canManageTenants || false;
  const canManageTenants = isFounderOrSuperAdmin || hasExplicitPermission;

  if (!canManageTenants) {
    // Redirect to dashboard (or home) if not authorized.
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

/**
 * @function SovereignRouter
 * @memberof WILSY_OS_CORE
 * @description Sovereign routing orchestrator. Handles authentication, tenant context,
 *              MFA, covenant signing, and navigation guard. Uses new TenantContext.
 * @returns {JSX.Element} The router component.
 * @institutional This component ensures deterministic navigation based on authentication
 *                and tenant state, enforcing institutional workflows (MFA, covenant).
 * @collaboration Wilson Khanyezi & AI Engineering (2026-08-19)
 * @epitome "Institutional Finality"
 */
const SovereignRouter = () => {
  const {
    isAuthenticated,
    user,
    tenant: authTenant,
    authStage,
    loading: authLoading,
    updateSovereignIdentity,
  } = useAuth();
  // ✅ Use the new useTenants hook instead of useTenantContext
  const {
    activeTenant: currentTenant,
    loading: tenantLoading,
    bootstrapReady,
    error: tenantError,
    authorityMismatch,
  } = useTenants();

  const mesh = useSovereignMesh();
  const dataStream = useSovereignData();

  const navigate = useNavigate();
  const location = useLocation();

  // Telemetry & Context Initialization – Suppressed in DEV to prevent console flooding
  useEffect(() => {
    try {
      if (IS_DEV_MODE) return;

      console.log('[ORCHESTRATOR-TRACE]', {
        isAuthenticated,
        userRole: user?.role,
        hasCovenant: user?.hasSignedCovenant,
        mfaRegistered: user?.mfaRegistered,
        currentTenant,
        meshHealth: mesh?.meshHealth,
        dataVersion: dataStream?.version,
        path: location.pathname
      });

      broadcastTelemetry("GLOBAL_ROOT", "NAV_EVENT", "ROUTE_CHANGE", "App", {
        path: location.pathname,
        userId: user?.id,
        tenant: currentTenant,
        meshStatus: mesh?.meshHealth
      });
    } catch (err) {
      if (!IS_DEV_MODE) {
        console.error('[ORCHESTRATOR-ERROR] Failed in lifecycle telemetry audit:', err);
      }
    }
  }, [isAuthenticated, currentTenant, user, location.pathname, mesh?.meshHealth, dataStream?.version]);

  const unauthenticatedEntryPath = authTenant?.tenantId ? '/login' : '/discovery';

  // 🛡️ Deterministic navigation state-machine.
  const targetPath = useMemo(() => {
    if (authLoading) return null;
    const isMfaChallenge = [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage);
    if (location.pathname === '/mfa' || location.pathname === '/mfa-setup') return isMfaChallenge ? null : '/login';
    if (
      location.pathname === '/reset-password'
      || location.pathname === '/forgot-password'
      || location.pathname === '/verify-recovery-contact'
    ) return null;
    if (location.pathname === '/login' || location.pathname === '/discovery') return isAuthenticated ? '/' : null;

    // Protected application routes always require an authenticated identity.
    // A server-discovered tenant is navigation context only: it may skip
    // redundant discovery, but it never authenticates the caller.
    if (!isAuthenticated) {
      return unauthenticatedEntryPath;
    }

    // Authenticated, but user object is still hydrating: wait, never bypass.
    if (!user) {
      return null;
    }

    // Versioned legal acceptance is server-derived; the gate owns its own
    // status read and remains reachable at the compatibility /covenant path.
    if (location.pathname === '/covenant') return null;
    return ['/', '/dashboard'].includes(location.pathname) ? null : '/';
  }, [
    location.pathname,
    isAuthenticated,
    user,
    currentTenant,
    authStage,
    authLoading,
    unauthenticatedEntryPath,
  ]);

  // Execute the deterministic navigation
  useEffect(() => {
    if (targetPath && targetPath !== location.pathname) {
      navigate(targetPath, { replace: true });
    }
  }, [targetPath, location.pathname, navigate]);

  // Loading Screen
  if (authLoading || (isAuthenticated && (!user || !bootstrapReady || tenantLoading))) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-black">
        <Loader2 className="w-16 h-16 text-[#D4AF37] animate-spin mb-4" />
        <p className="text-[#D4AF37] font-mono text-xs tracking-widest uppercase mb-2">Verifying Sovereign Identity...</p>
        <p className="text-gray-500 font-mono text-[10px] tracking-widest uppercase">
          Neural Mesh: {mesh?.meshHealth || 'CONNECTING'} | Data Stream V{dataStream?.version || '0'}
        </p>
      </div>
    );
  }

  if (isAuthenticated && (authorityMismatch || tenantError || !currentTenant)) {
    return <WorkspaceBootstrapError message={authorityMismatch ? 'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH' : (tenantError || 'AUTHENTICATED_WORKSPACE_UNRESOLVED')} />;
  }

  return (
    <Routes>
      <Route path="/discovery" element={<TenantDiscovery />} />
      <Route path="/login" element={<SovereignLogin />} />
      <Route path="/forgot-password" element={<PasswordRecoveryRequestPortal />} />
      <Route path="/verify-recovery-contact" element={<RecoveryContactVerificationPortal />} />
      <Route path="/reset-password" element={<PasswordResetPortal />} />
      <Route path="/mfa" element={
        [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage)
          ? <SovereignMfaPortal /> : <Navigate to="/login" replace />
      } />
      <Route path="/mfa-setup" element={
        [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage)
          ? <SovereignMfaPortal /> : <Navigate to="/login" replace />
      } />
      <Route path="/covenant" element={<LegalAcceptanceGate onComplete={() => navigate('/', { replace: true })} />} />
      <Route path="/signature" element={<Navigate to="/covenant" replace />} />
      <Route path="/" element={isAuthenticated && user ? <ErrorBoundary><SovereignDashboardController user={user} /></ErrorBoundary> : <Navigate to={unauthenticatedEntryPath} replace />} />
      {/* Explicit /dashboard route for soft navigation */}
      <Route path="/dashboard" element={
        isAuthenticated && user ? <ErrorBoundary><SovereignDashboardController user={user} /></ErrorBoundary> : <Navigate to="/discovery" replace />
      } />
      <Route path="/ledger" element={
        isAuthenticated && user ? (
          <ErrorBoundary>
            <LedgerExplorer
              tenantId={currentTenant?.id || currentTenant?.tenantId || user?.tenantId || null}
              userRole={user?.role || user?.userRole || 'viewer'}
            />
          </ErrorBoundary>
        ) : <Navigate to={unauthenticatedEntryPath} replace />
      } />
      {/* 🆕 /tms route with permission guard – ONLY for founders/superadmins */}
      <Route path="/tms" element={
        isAuthenticated && user ? (
          <ProtectedTmsRoute user={user}>
            <ErrorBoundary><Sovereign_TenantManager /></ErrorBoundary>
          </ProtectedTmsRoute>
        ) : <Navigate to={unauthenticatedEntryPath} replace />
      } />
      <Route path="/*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

/**
 * @function App
 * @memberof WILSY_OS_CORE
 * @description Root application component. Wraps the app with all sovereign providers:
 *              - SovereignOrchestrator (mesh)
 *              - DataOrchestratorProvider (data stream)
 *              - AuthProvider (authentication)
 *              - Router
 * @returns {JSX.Element} The application root.
 * @institutional This is the institutional contract root; all providers are layered
 *                to ensure cryptographic, authentication, and tenant isolation.
 * @collaboration Wilson Khanyezi & AI Engineering (2026-08-19)
 * @epitome "Institutional Finality"
 */
const WorkspaceBootstrapSurface = () => (
  <div data-testid="workspace-bootstrap" className="flex min-h-screen flex-col items-center justify-center bg-black text-center">
    <Loader2 className="mb-4 h-12 w-12 animate-spin text-[#D4AF37]" />
    <p className="font-mono text-xs tracking-widest uppercase text-[#D4AF37]">Preparing secure workspace</p>
    <p className="mt-2 max-w-md px-6 font-mono text-[10px] tracking-widest uppercase text-gray-500">Validating authenticated tenant authority...</p>
  </div>
);


const WorkspaceBootstrapError = ({ message }) => (
  <div data-testid="workspace-bootstrap-error" role="alert" className="flex min-h-screen flex-col items-center justify-center bg-black px-6 text-center">
    <p className="font-mono text-xs tracking-widest uppercase text-red-300">Workspace access is unavailable</p>
    <p className="mt-3 max-w-lg font-mono text-[10px] tracking-widest uppercase text-gray-500">{message}</p>
  </div>
);

/**
 * @description Resolve server-owned legal acceptance before mounting protected consumers.
 * @collaboration AuthenticatedTenantBoundary, LegalAcceptanceGate, and RuntimeComposition.
 * @institutional Prevents dashboard, billing, AI, and tenant-management hydration
 *              from racing ahead of the legal acceptance decision.
 * @param {{runtime?: React.ReactNode}} props Optional runtime seam for deterministic certificates.
 * @returns {JSX.Element} Loading, bounded legal, unavailable, or protected runtime surface.
 */
export const LegalAcceptanceBoundary = ({ runtime = <RuntimeComposition /> }) => {
  const navigate = useNavigate();
  const [phase, setPhase] = useState('LOADING');
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    api.get('/legal-acceptance/status').then((response) => {
      if (!active) return;
      const nextPlan = response.data;
      setPlan(nextPlan);
      setPhase(nextPlan?.status === 'COMPLETE' ? 'COMPLETE' : 'REQUIRED');
    }).catch((requestError) => {
      if (!active) return;
      setError(requestError?.response?.data?.detail || 'LEGAL_ACCEPTANCE_STATUS_UNAVAILABLE');
      setPhase('UNAVAILABLE');
    });
    return () => { active = false; };
  }, []);

  if (phase === 'LOADING') return <WorkspaceBootstrapSurface />;
  if (phase === 'UNAVAILABLE') return <WorkspaceBootstrapError message={error} />;
  const releaseWorkspace = () => {
    // LegalAcceptanceGate invokes this callback only after its refreshed
    // server status is COMPLETE. Updating phase therefore projects server truth;
    // it does not manufacture legal acceptance in the browser.
    setPhase('COMPLETE');
    navigate('/', { replace: true });
  };

  if (phase === 'REQUIRED') {
    return (
      <Routes>
        <Route
          path="/covenant"
          element={(
            <LegalAcceptanceGate
              initialPlan={plan}
              onComplete={releaseWorkspace}
            />
          )}
        />
        <Route path="*" element={<Navigate to="/covenant" replace />} />
      </Routes>
    );
  }
  return runtime;
};

const RuntimeComposition = () => (
  <SovereignOrchestrator>
    <DataOrchestratorProvider>
      <SovereignRouter />
    </DataOrchestratorProvider>
  </SovereignOrchestrator>
);

const AuthenticatedRuntimeComposition = () => {
  const { isAuthenticated, user } = useAuth();
  const { activeTenant } = useTenants();

  if (!isAuthenticated || !user?.id || !user?.tenantId || !activeTenant) {
    return <WorkspaceBootstrapError message="AUTHENTICATED_WORKSPACE_UNRESOLVED" />;
  }

  return (
    <>
      <RuntimeComposition />
      <WilsyOSIntelligenceDockRuntime
        authenticated
        authUser={user}
        activeTenant={activeTenant}
      />
    </>
  );
};

const AuthenticatedTenantBoundary = () => {
  const { isAuthenticated, tenant, user } = useAuth();
  if (!isAuthenticated) return <RuntimeComposition />;
  return (
    <TenantProvider initialTenant={tenant} authenticatedTenantId={String(user?.tenantId || '')}>
      <AuthenticatedBootstrapBoundary />
    </TenantProvider>
  );
};

const AuthenticatedBootstrapBoundary = () => {
  const { activeTenant, bootstrapReady, loading, error, authorityMismatch } = useTenants();
  if (!bootstrapReady || loading) return <WorkspaceBootstrapSurface />;
  if (authorityMismatch || error || !activeTenant) {
    return <WorkspaceBootstrapError message={authorityMismatch ? 'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH' : (error || 'AUTHENTICATED_WORKSPACE_UNRESOLVED')} />;
  }
  return (
    <LegalAcceptanceBoundary runtime={<AuthenticatedRuntimeComposition />} />
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                <Suspense fallback={
                  <div className="flex flex-col items-center justify-center h-screen bg-black">
                    <Loader2 className="w-16 h-16 text-[#D4AF37] animate-spin mb-4" />
                    <div className="text-[#D4AF37] font-mono text-xs uppercase tracking-[0.3em]">Loading Sovereign Modules...</div>
                  </div>
                }>
                  <div className="wilsy-os-container h-screen bg-black text-white">
                    <AuthenticatedTenantBoundary />
                  </div>
                </Suspense>
              </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;

/**
 * ARTIFACT: client/src/App.jsx
 * VERSION: v20.0.0-LEGAL-ADMISSION-RELEASE-ROUTING
 * AUTHORITY BOUNDARY: client route and protected-runtime composition only; Python EOS remains authentication, tenant and legal-acceptance authority
 * TENANT POSTURE: discovered tenant may choose login routing but cannot establish authenticated or protected scope
 * FAIL-CLOSED POSTURE: auth revalidation waits; unresolved legal status remains sealed; only server-confirmed legal COMPLETE mounts protected runtime
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
