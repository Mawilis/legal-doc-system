/* eslint-disable */
/**
 * TITLE: WILSY OS Sovereign Application Root
 * VERSION: v20.2.2-GLOBAL-CHROME-TRANSPORT-TRUST
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Composes authenticated routing, exact tenant projection, legal
 *          admission release, and protected workspace presentation without
 *          promoting browser state into authentication or legal authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/App.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider owns browser auth projection;
 *                            TenantProvider owns bounded tenant projection;
 *                            Python EOS owns authentication, workspace and
 *                            legal-acceptance truth.
 * CERTIFICATION / UPDATE DATE: 2026-11-09
 * CHANGELOG:
 *   v20.2.2-GLOBAL-CHROME-TRANSPORT-TRUST — Uses a neutral security-chip
 *     treatment when the authenticated browser transport is not HTTPS; an
 *     authenticated session is not mislabelled as a secure channel.
 *   v20.2.1-GLOBAL-CHROME-HEALTH-SEMANTICS — Refines status copy to distinguish an EOS kernel API response from whole-platform health; records the current update date.
 *   v20.2.0-GLOBAL-AUTHENTICATED-CHROME — Adds a route-stable authenticated
 *     global top bar for protected routes, consuming the revalidated auth
 *     projection, EOS My Work summary and bounded kernel status/version.
 *     Search opens a global command surface with safe navigation shortcuts;
 *     notification state remains explicitly unavailable until an authorised
 *     EOS notification projection exists. No browser-derived authority is made.
 *   v20.1.1-ALL-PROTECTED-ROUTES-LOGOUT-PROPAGATION — Promotes the legal boundary
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
import { Bell, CheckCircle2, ChevronDown, Home, Loader2, LogOut, Search, ShieldCheck, X } from 'lucide-react';
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
import MyWorkWorkspace from './components/workspaces/MyWorkWorkspace.jsx';
import WilsyHeadquartersWorkspace from './components/workspaces/WilsyHeadquartersWorkspace.jsx';
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
 * @component AuthenticatedGlobalChrome
 * @description Persistent authenticated top-bar frame shared by protected routes.
 * @param {{user: Object, onLogout: Function, children: React.ReactNode}} props
 * @returns {JSX.Element} Stable brand, global search, bounded system trust,
 *          notification availability, identity menu, and the active route outlet.
 * @institutional Python EOS remains the authority for identity, tenant, role,
 *          work visibility, notifications, and runtime health. This component
 *          renders only server-revalidated projections and never grants access.
 */
const AuthenticatedGlobalChrome = ({ user, onLogout, children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [workCount, setWorkCount] = useState(null);
  const [kernel, setKernel] = useState({ state: 'CHECKING', version: null });

  const displayName = [user?.firstName, user?.lastName].filter(Boolean).join(' ')
    || user?.email
    || 'Authenticated user';
  const roleLabel = String(user?.role || user?.systemServicesWorkspace?.role || 'Authorised role')
    .replace(/[_-]+/g, ' ');
  const initials = (user?.firstName || user?.email || 'W').slice(0, 1).toUpperCase()
    + (user?.lastName || '').slice(0, 1).toUpperCase();
  const isSecureChannel = typeof window !== 'undefined'
    && window.location.protocol === 'https:';
  const isMyWork = location.pathname === '/my-work';

  useEffect(() => {
    let active = true;
    const refresh = async () => {
      try {
        const [healthResponse, statusResponse] = await Promise.all([
          api.get('/kernel'),
          api.get('/kernel/status'),
        ]);
        if (!active) return;
        const health = healthResponse?.data || {};
        const status = statusResponse?.data || {};
        const components = status.components;
        const componentStatesValid = components && typeof components === 'object'
          && !Array.isArray(components)
          && Object.values(components).every((value) => typeof value === 'string');
        setKernel({
          state: health.status === 'OPERATIONAL' && status.status === 'OPERATIONAL'
            ? 'RESPONDING'
            : 'DEGRADED',
          version: typeof health.version === 'string' ? health.version : null,
          components: componentStatesValid ? components : null,
        });
      } catch {
        if (active) setKernel({ state: 'UNAVAILABLE', version: null });
      }
    };
    void refresh();
    const interval = window.setInterval(refresh, 60000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (!user?.tenantId || user?.systemServicesWorkspace) {
      setWorkCount(null);
      return undefined;
    }
    let active = true;
    const refresh = async () => {
      try {
        const response = await api.get('/my-work');
        const payload = response?.data;
        if (
          !payload
          || payload.tenant_id !== user.tenantId
          || !payload.summary
          || !Number.isInteger(payload.summary.active_count)
          || payload.summary.active_count < 0
        ) throw new Error('MY_WORK_SUMMARY_PROJECTION_INVALID');
        if (active) setWorkCount(payload.summary.active_count);
      } catch {
        if (active) setWorkCount(null);
      }
    };
    void refresh();
    const interval = window.setInterval(refresh, 60000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [user?.tenantId, user?.id, user?.systemServicesWorkspace]);

  useEffect(() => {
    const handleShortcut = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setSearchOpen(true);
        setUserMenuOpen(false);
        setNotificationsOpen(false);
      }
      if (event.key === 'Escape') {
        setSearchOpen(false);
        setUserMenuOpen(false);
        setNotificationsOpen(false);
      }
    };
    window.addEventListener('keydown', handleShortcut);
    return () => window.removeEventListener('keydown', handleShortcut);
  }, []);

  useEffect(() => {
    if (searchOpen) {
      const input = document.getElementById('wilsy-global-search-input');
      input?.focus();
    }
  }, [searchOpen]);

  const submitSearch = (event) => {
    event.preventDefault();
    const query = searchValue.trim().toLowerCase();
    if (query === 'headquarters' || query === 'home') {
      navigate('/headquarters');
      setSearchOpen(false);
      setSearchValue('');
    } else if (query === 'my work' || query === 'tasks') {
      navigate('/my-work');
      setSearchOpen(false);
      setSearchValue('');
    }
  };

  return (
    <div className="min-h-screen bg-[#080f1d] text-slate-100">
      <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between gap-3 border-b border-white/10 bg-[#0b1830]/95 px-4 shadow-lg shadow-black/10 backdrop-blur-xl sm:px-6">
        <button type="button" aria-label="WILSY home" onClick={() => navigate('/headquarters')} className="flex min-w-[190px] items-center gap-3 text-left">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[#d7ad43] text-xl font-black text-[#081326]">W</span>
          <span className="leading-tight">
            <span className="block text-sm font-extrabold tracking-[0.2em] text-white">WILSY</span>
            <span className="block text-[10px] tracking-wide text-slate-400">Build. Operate. Grow.</span>
          </span>
        </button>

        <button type="button" onClick={() => { setSearchOpen(true); setUserMenuOpen(false); setNotificationsOpen(false); }} aria-label="Open global search" className="hidden h-10 w-full max-w-[540px] items-center gap-3 rounded-full border border-white/10 bg-white/[0.055] px-4 text-left text-sm text-slate-400 transition hover:border-amber-300/40 hover:bg-white/[0.08] md:flex">
          <Search size={16}/>
          <span className="flex-1">Search people, projects, tasks, or anything…</span>
          <kbd className="rounded-md border border-white/10 bg-black/20 px-2 py-1 text-[10px] text-slate-400">⌘ K</kbd>
        </button>
        <button type="button" onClick={() => setSearchOpen(true)} aria-label="Open global search" className="grid h-9 w-9 place-items-center rounded-full border border-white/10 text-slate-300 md:hidden"><Search size={17}/></button>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <div title={isSecureChannel ? 'Authenticated session over HTTPS' : 'Authenticated session; transport is not HTTPS'} className={`flex items-center gap-2 rounded-full border px-2 py-2 text-[11px] font-medium sm:px-3 ${isSecureChannel ? 'border-emerald-400/20 bg-emerald-400/10 text-emerald-200' : 'border-white/10 bg-white/[0.04] text-slate-300'}`}>
            <ShieldCheck size={15}/><span className="hidden sm:inline">{isSecureChannel ? 'Secure · Authenticated' : 'Authenticated'}</span>
          </div>
          <div className="relative">
            <button type="button" aria-label="Notifications" aria-expanded={notificationsOpen} onClick={() => { setNotificationsOpen((value) => !value); setUserMenuOpen(false); }} className="relative grid h-10 w-10 place-items-center rounded-full text-slate-300 transition hover:bg-white/10"><Bell size={18}/></button>
            {notificationsOpen && (
              <div role="dialog" aria-label="Notifications" className="absolute right-0 top-12 z-50 w-[min(340px,calc(100vw-2rem))] rounded-2xl border border-white/10 bg-[#101d32] p-4 shadow-2xl">
                <div className="flex items-center justify-between"><h2 className="font-semibold text-white">Notifications</h2><button type="button" aria-label="Close notifications" onClick={() => setNotificationsOpen(false)}><X size={16}/></button></div>
                <p className="mt-3 text-sm leading-6 text-slate-300">The EOS notification projection is not connected to this workspace yet. Unread count and read actions are therefore unavailable.</p>
              </div>
            )}
          </div>
          <div className="relative">
            <button type="button" aria-label="Open user menu" aria-expanded={userMenuOpen} onClick={() => { setUserMenuOpen((value) => !value); setNotificationsOpen(false); }} className="flex items-center gap-2 rounded-full py-1 pl-1 pr-2 transition hover:bg-white/10">
              <span className="grid h-8 w-8 place-items-center rounded-full border border-amber-300/30 bg-amber-300/15 text-xs font-bold text-amber-200">{initials}</span>
              <span className="hidden max-w-[150px] text-left leading-tight xl:block">
                <span className="block truncate text-xs font-semibold text-white">{displayName}</span>
                <span className="block truncate text-[10px] capitalize text-slate-400">{roleLabel}</span>
              </span>
              <ChevronDown size={14} className="hidden text-slate-400 xl:block"/>
            </button>
            {userMenuOpen && (
              <div role="menu" aria-label="User account" className="absolute right-0 top-12 z-50 w-64 rounded-2xl border border-white/10 bg-[#101d32] p-3 shadow-2xl">
                <div className="border-b border-white/10 px-2 pb-3">
                  <p className="font-semibold text-white">{displayName}</p>
                  <p className="mt-1 break-all text-xs text-slate-400">{user?.email || 'Email not provided by session'}</p>
                  <p className="mt-2 text-xs capitalize text-amber-200">{roleLabel}</p>
                </div>
                <p className="px-2 py-3 text-xs leading-5 text-slate-400">Profile and preferences are managed by the authenticated account workspace; a dedicated route is not yet connected here.</p>
                <button type="button" role="menuitem" onClick={() => { setUserMenuOpen(false); void onLogout(); }} className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm text-red-200 hover:bg-red-400/10"><LogOut size={15}/> Sign out</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="flex items-center justify-end gap-2 border-b border-white/5 bg-[#0b1628] px-4 py-2 text-[10px] text-slate-500 sm:px-6">
        <span className={kernel.state === 'RESPONDING' ? 'text-emerald-300' : kernel.state === 'CHECKING' ? 'text-amber-200' : 'text-rose-300'}>
          <span aria-hidden="true">●</span> {kernel.state === 'RESPONDING' ? 'EOS kernel API responding' : kernel.state === 'CHECKING' ? 'Checking EOS kernel…' : 'EOS kernel API unavailable'}
        </span>
        <span>·</span><span>{kernel.version ? 'Kernel v' + kernel.version : 'Version unavailable'}</span>
        {isMyWork && workCount !== null && <span className="ml-2 rounded-full bg-amber-300 px-2 py-1 font-semibold text-[#081326]">{workCount} open</span>}
        {isMyWork && workCount === null && <span className="ml-2 text-amber-200">Task count unavailable</span>}
      </div>

      <div>{children}</div>

      {searchOpen && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/65 px-4 pt-[12vh] backdrop-blur-sm" onMouseDown={(event) => { if (event.target === event.currentTarget) setSearchOpen(false); }}>
          <section role="dialog" aria-modal="true" aria-labelledby="wilsy-global-search-title" className="w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-[#101d32] shadow-2xl">
            <h2 id="wilsy-global-search-title" className="sr-only">Global search</h2>
            <form onSubmit={submitSearch} className="flex items-center gap-3 border-b border-white/10 px-5 py-4">
              <Search size={19} className="text-amber-300"/>
              <input id="wilsy-global-search-input" value={searchValue} onChange={(event) => setSearchValue(event.target.value)} placeholder="Search people, projects, tasks, or anything…" className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-500"/>
              <kbd className="rounded border border-white/10 px-2 py-1 text-[10px] text-slate-400">ESC</kbd>
              <button type="button" aria-label="Close search" onClick={() => setSearchOpen(false)}><X size={17}/></button>
            </form>
            <div className="p-5">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">Quick navigation</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <button type="button" onClick={() => { navigate('/headquarters'); setSearchOpen(false); }} className="flex items-center gap-3 rounded-xl border border-white/10 p-3 text-left text-sm hover:border-amber-300/40"><Home size={17} className="text-amber-300"/> Headquarters</button>
                <button type="button" onClick={() => { navigate('/my-work'); setSearchOpen(false); }} className="flex items-center gap-3 rounded-xl border border-white/10 p-3 text-left text-sm hover:border-amber-300/40"><CheckCircle2 size={17} className="text-amber-300"/> My Work</button>
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-400">Search across people, projects, tasks, departments and documents will appear here when the permission-filtered EOS search service is connected. No unfiltered or synthetic results are shown.</p>
            </div>
          </section>
        </div>
      )}
    </div>
  );
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
    logout,
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

      broadcastTelemetry(user?.tenantId || currentTenant?.tenantId || "unresolved", "NAV_EVENT", "ROUTE_CHANGE", "App", {
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

  // SYSTEM is a tenant-independent workforce session. Its exact EOS-issued
  // workspace projection is the only client-side discriminator; it does not
  // synthesize a tenant, membership, business capacity, or tenant permission.
  const systemServicesSession = Boolean(
    isAuthenticated
    && user?.systemServicesWorkspace?.status === 'READY'
    && user.systemServicesWorkspace.authority === 'EOS_SYSTEM_SERVICES'
    && user.systemServicesWorkspace.scope === 'SYSTEM'
    && user.systemServicesWorkspace.principalId === user.id
    && Array.isArray(user.systemServicesWorkspace.capabilities)
    && user.systemServicesWorkspace.capabilities.includes('system_services:queue:read')
  );

  const unauthenticatedEntryPath = authTenant?.tenantId ? '/login' : '/discovery';

  // 🛡️ Deterministic navigation state-machine.
  const targetPath = useMemo(() => {
    if (authLoading) return null;
    const isMfaReady = [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage);
    const isMfaPending = authStage === AUTH_STATES.PRIMARY_AUTHENTICATING
      || (Boolean(location.state?.pendingPrimaryAuth) && authStage !== AUTH_STATES.FAILED);
    if (location.pathname === '/mfa' || location.pathname === '/mfa-setup') {
      return (isMfaReady || isMfaPending) ? null : '/login';
    }
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
    return ['/', '/dashboard', '/my-work', '/headquarters'].includes(location.pathname) ? null : '/';
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

  if (isAuthenticated && !systemServicesSession && (authorityMismatch || tenantError || !currentTenant)) {
    return <WorkspaceBootstrapError message={authorityMismatch ? 'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH' : (tenantError || 'AUTHENTICATED_WORKSPACE_UNRESOLVED')} />;
  }

  const protectedRoutes = (
    <Routes>
      <Route path="/discovery" element={<TenantDiscovery />} />
      <Route path="/login" element={<SovereignLogin />} />
      <Route path="/forgot-password" element={<PasswordRecoveryRequestPortal />} />
      <Route path="/verify-recovery-contact" element={<RecoveryContactVerificationPortal />} />
      <Route path="/reset-password" element={<PasswordResetPortal />} />
      <Route path="/mfa" element={
        [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage)
          ? <SovereignMfaPortal />
          : ((authStage === AUTH_STATES.PRIMARY_AUTHENTICATING || (location.state?.pendingPrimaryAuth && authStage !== AUTH_STATES.FAILED))
            ? <div role="status" data-testid="mfa-transition">Preparing secure MFA challenge…</div>
            : <Navigate to="/login" replace />)
      } />
      <Route path="/mfa-setup" element={
        [AUTH_STATES.MFA_SETUP, AUTH_STATES.MFA_RECONCILIATION_REQUIRED, AUTH_STATES.MFA_REQUIRED, AUTH_STATES.MFA_VERIFYING].includes(authStage)
          ? <SovereignMfaPortal />
          : ((authStage === AUTH_STATES.PRIMARY_AUTHENTICATING || (location.state?.pendingPrimaryAuth && authStage !== AUTH_STATES.FAILED))
            ? <div role="status" data-testid="mfa-transition">Preparing secure MFA challenge…</div>
            : <Navigate to="/login" replace />)
      } />
      <Route path="/covenant" element={<LegalAcceptanceGate onComplete={() => navigate('/', { replace: true })} />} />
      <Route path="/headquarters" element={
        isAuthenticated && user && !systemServicesSession
          ? <ErrorBoundary><WilsyHeadquartersWorkspace /></ErrorBoundary>
          : <Navigate to="/" replace />
      } />
      <Route path="/my-work" element={
        isAuthenticated && user && !systemServicesSession
          ? <ErrorBoundary><MyWorkWorkspace /></ErrorBoundary>
          : <Navigate to="/" replace />
      } />
      <Route path="/signature" element={<Navigate to="/covenant" replace />} />
      <Route path="/" element={isAuthenticated && user ? <ErrorBoundary><SovereignDashboardController user={user} onLogout={logout} /></ErrorBoundary> : <Navigate to={unauthenticatedEntryPath} replace />} />
      {/* Explicit /dashboard route for soft navigation */}
      <Route path="/dashboard" element={
        isAuthenticated && user ? <ErrorBoundary><SovereignDashboardController user={user} onLogout={logout} /></ErrorBoundary> : <Navigate to={unauthenticatedEntryPath} replace />
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

  return isAuthenticated
    ? <AuthenticatedGlobalChrome user={user} onLogout={logout}>{protectedRoutes}</AuthenticatedGlobalChrome>
    : protectedRoutes;
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

export const AuthenticatedTenantBoundary = ({ runtime }) => {
  const { isAuthenticated, tenant, user } = useAuth();
  if (!isAuthenticated) return <RuntimeComposition />;

  // Global SYSTEM principals have no tenant membership by design. Mount the
  // existing authenticated SYSTEM dashboard path without TenantProvider or
  // tenant bootstrap; the EOS workspace projection above is still required
  // before SovereignRouter treats the session as SYSTEM.
  const systemServicesSession = Boolean(
    user?.systemServicesWorkspace?.status === 'READY'
    && user.systemServicesWorkspace.authority === 'EOS_SYSTEM_SERVICES'
    && user.systemServicesWorkspace.scope === 'SYSTEM'
    && user.systemServicesWorkspace.principalId === user.id
    && Array.isArray(user.systemServicesWorkspace.capabilities)
    && user.systemServicesWorkspace.capabilities.includes('system_services:queue:read')
  );
  if (systemServicesSession) return <RuntimeComposition />;

  return (
    <TenantProvider initialTenant={tenant} authenticatedTenantId={String(user?.tenantId || '')}>
      <AuthenticatedBootstrapBoundary runtime={runtime} />
    </TenantProvider>
  );
};

const AuthenticatedBootstrapBoundary = ({ runtime }) => {
  const { activeTenant, bootstrapReady, loading, error, authorityMismatch } = useTenants();
  if (!bootstrapReady || loading) return <WorkspaceBootstrapSurface />;
  if (authorityMismatch || error || !activeTenant) {
    return <WorkspaceBootstrapError message={authorityMismatch ? 'AUTHENTICATED_WORKSPACE_AUTHORITY_MISMATCH' : (error || 'AUTHENTICATED_WORKSPACE_UNRESOLVED')} />;
  }
  return (
    <LegalAcceptanceBoundary runtime={runtime || <AuthenticatedRuntimeComposition />} />
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
 * VERSION: v20.2.2-GLOBAL-CHROME-TRANSPORT-TRUST
 * AUTHORITY BOUNDARY: client route and protected-runtime composition only; Python EOS remains authentication, tenant and legal-acceptance authority
 * TENANT POSTURE: discovered tenant may choose login routing but cannot establish authenticated or protected scope
 * FAIL-CLOSED POSTURE: auth revalidation waits; unresolved legal status remains sealed; only server-confirmed legal COMPLETE mounts protected runtime
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
