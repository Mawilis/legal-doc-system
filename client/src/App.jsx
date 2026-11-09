/**
 * TITLE: WILSY OS Sovereign Application Root
 * VERSION: v20.5.0-PLATFORM-ADMISSION-SESSION-CURRENTNESS
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
 *   v20.5.0-PLATFORM-ADMISSION-SESSION-CURRENTNESS — Owns one explicitly
 *     authenticated, scope-current platform-agreement read. Completed covenant
 *     URLs redirect to the authorized workspace; required agreements use the
 *     shared brand bar without a Legal Control rail or protected prefetch.
 *   v20.4.3-SINGLE-COMMAND-SEARCH-OWNER — Delegates shared search controls to
 *     the mounted workspace search and honors claimed keyboard events so a
 *     single shortcut cannot leave two modal backdrops open.
 *   v20.4.2-RESPONSIVE-AUTHENTICATED-CHROME — Removes fixed mobile header
 *     minimum widths while preserving the official emblem, search, session,
 *     attention and account controls. Debug output is opt-in and omits raw
 *     tenant data; lifecycle errors remain visible in every environment.
 *   v20.4.1-ACTIONABLE-FLOATING-CHROME — Routes selected EOS work items to source-owned completion
 *     and opens existing HR workspaces directly from the floating bell.
 *   v20.4.0-CHECKPOINT-DAILY-ATTENTION-MERGED — Integrates EOS-authorised Daily Attention into the preserved
 *     official brand, search, session title, avatar and security chrome.
 *     Active work is distinct from unread notifications.
 *   v20.2.3-GLOBAL-SEARCH-PLATFORM-HINT — Displays both macOS and Windows
 *     keyboard hints while preserving the shared Meta/Ctrl+K command shortcut.
 *   v20.2.2-GLOBAL-CHROME-TRANSPORT-TRUST — Uses a neutral security-chip
 *     treatment when the authenticated browser transport is not HTTPS; an
 *     authenticated session is not mislabelled as a secure channel.
 *   v20.2.1-GLOBAL-CHROME-HEALTH-SEMANTICS — Refines status copy to distinguish an EOS kernel API response from whole-platform health; records the current update date.
 *   v20.2.0-GLOBAL-AUTHENTICATED-CHROME — Adds a route-stable authenticated
 *     global top bar for protected routes, consuming the revalidated auth
 *     projection, EOS My Work summary and bounded kernel status/version.
 *     Search opens a global command surface with safe navigation shortcuts;
 *     attention is now sourced from authorised EOS My Work; genuine unread
 *     notification counts remain a separate future authority.
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

/* eslint-disable */
import React, { Suspense, useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AUTH_STATES, AuthProvider, useAuth } from './contexts/authContext.jsx';
import { TenantProvider, useTenants } from './contexts/tenantContext';  // ✅ NEW IMPORT
import ErrorBoundary from './components/ErrorBoundary.jsx';
import { CheckCircle2, ChevronDown, Home, Loader2, LogOut, Search, ShieldCheck, X } from 'lucide-react';
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
import WilsyDailyAttentionCentre from './components/chrome/WilsyDailyAttentionCentre.jsx';

import { SovereignOrchestrator, useSovereignMesh } from './components/sovereign/SovereignOrchestrator.jsx';
import { DataOrchestratorProvider, useSovereignData } from './components/sovereign/DataOrchestrator.jsx';

// 🛡️ Global development telemetry suppression flag.
const IS_DEV_MODE = import.meta.env.DEV;
const MODEL_DEBUG = import.meta.env.VITE_WILSY_MODEL_DEBUG === '1';

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
 * @collaboration Shared authenticated workspaces, source-owned My Work and EOS
 * workspace bootstrap. Header layout and navigation are presentation only.
 * @description Persistent authenticated top-bar frame shared by protected routes.
 * @param {{user: Object, onLogout: Function, children: React.ReactNode, workspaceReleased?: boolean}} props
 * @returns {JSX.Element} Stable brand, global search, bounded system trust,
 *          notification availability, identity menu, and the active route outlet.
 * @institutional Python EOS remains the authority for identity, tenant, role,
 *          work visibility, notifications, and runtime health. This component
 *          renders only server-revalidated projections and never grants access.
 */
export const AuthenticatedGlobalChrome = ({ user, onLogout, children, workspaceReleased = true }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, authStage, loading: authLoading } = useAuth();
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [workCount, setWorkCount] = useState(null);
  const [workCountScope, setWorkCountScope] = useState(null);

  const displayName = [user?.firstName, user?.lastName].filter(Boolean).join(' ')
    || user?.email
    || 'Authenticated user';
  // Operating titles are presentation-only and must come from the authenticated
  // session projection; never substitute an ACL role such as TENANT_OWNER.
  const operatingTitle = user?.operatingTitle || user?.jobTitle || user?.displayTitle || 'Account';
  const avatarUrl = user?.avatarUrl || user?.avatar_url || user?.profileImageUrl || null;
  const initials = (user?.firstName || user?.email || 'W').slice(0, 1).toUpperCase()
    + (user?.lastName || '').slice(0, 1).toUpperCase();
  const isSecureChannel = typeof window !== 'undefined'
    && window.location.protocol === 'https:';
  const hasAuthenticatedSession = isAuthenticated && authStage === AUTH_STATES.AUTHENTICATED;

  const currentWorkScope = [user?.tenantId, user?.id, user?.role, user?.workspaceId, user?.businessRole]
    .map((part) => String(part || '')).join(':');

  useEffect(() => {
    if (!workspaceReleased || !hasAuthenticatedSession || authLoading || !user?.tenantId || user?.systemServicesWorkspace) {
      setWorkCountScope(null);
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
        if (active) {
          setWorkCountScope(currentWorkScope);
          setWorkCount(payload.summary.active_count);
        }
      } catch {
        if (active) {
          setWorkCountScope(null);
          setWorkCount(null);
        }
      }
    };
    void refresh();
    const interval = window.setInterval(refresh, 60000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [workspaceReleased, hasAuthenticatedSession, authLoading, user?.tenantId, user?.id, user?.role, user?.workspaceId, user?.businessRole, user?.systemServicesWorkspace]);

  const openGlobalSearch = () => {
    const request = new CustomEvent('wilsy:open-command-search', { cancelable: true });
    const unclaimed = window.dispatchEvent(request);
    setSearchOpen(unclaimed);
    setUserMenuOpen(false);
    setNotificationsOpen(false);
  };

  useEffect(() => {
    const handleShortcut = (event) => {
      if (event.defaultPrevented) return;
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        const request = new CustomEvent('wilsy:open-command-search', { cancelable: true });
        setSearchOpen(window.dispatchEvent(request));
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
      <header className="sticky top-0 z-40 flex h-16 w-full min-w-0 items-center gap-2 border-b border-white/10 bg-[#0b1830]/95 px-3 shadow-lg shadow-black/10 backdrop-blur-xl sm:gap-4 sm:px-6">
        <button type="button" aria-label="WILSY home" onClick={() => navigate('/headquarters')} className="flex min-w-0 shrink-0 items-center gap-2 text-left md:w-[200px] xl:w-[240px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d7ad43] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0b1830]">
          <img src="/brand/wilsy-gold-emblem.png" alt="WILSY gold emblem" className="h-12 w-12 shrink-0 object-contain" />
          <span className="hidden min-w-0 leading-tight min-[360px]:block">


            <span className="block text-lg font-semibold tracking-[0.025em] text-white">WILSY</span>
            <span className="block whitespace-nowrap text-[10px] font-medium text-[#f0dca5]">Build. Operate. Grow.</span>
          </span>
        </button>

        <button type="button" onClick={openGlobalSearch} aria-label="Open global search" className="mx-auto hidden h-10 min-w-0 max-w-[690px] flex-1 items-center gap-3 rounded-full border border-white/15 bg-white px-4 text-left text-sm text-[#435575] transition hover:border-[#d7ad43] hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d7ad43] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0b1830] md:flex">
          <Search size={16} className="text-[#435575]"/>
          <span className="flex-1">Search people, projects, tasks, or anything…</span>
          <kbd className="rounded-md border border-slate-200 bg-slate-100 px-2 py-1 text-[10px] text-slate-500">⌘ K / Ctrl K</kbd>
        </button>
        <button type="button" onClick={openGlobalSearch} aria-label="Open global search" className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-white/10 text-slate-300 md:hidden"><Search size={17}/></button>

        <div className="ml-auto flex min-w-0 shrink-0 items-center justify-end gap-1 sm:gap-3">
          {hasAuthenticatedSession && !authLoading && (
            <div role="status" aria-label={isSecureChannel ? 'Secure and authenticated' : 'Authenticated; secure transport not confirmed'} className={`flex items-center gap-2 rounded-full border px-2 py-2 text-[11px] font-medium sm:px-3 ${isSecureChannel ? 'border-emerald-400/20 bg-emerald-400/10 text-emerald-200' : 'border-emerald-400/25 bg-emerald-500/20 text-emerald-100'}`}>
              <ShieldCheck size={15}/>
              <span className="hidden sm:inline">{isSecureChannel ? 'Secure · Authenticated' : 'Authenticated'}</span>
            </div>
          )}
          {workspaceReleased && <WilsyDailyAttentionCentre
            key={currentWorkScope}
            tenantId={user?.tenantId}
            systemServicesWorkspace={Boolean(user?.systemServicesWorkspace)}
            activeCount={workCountScope === currentWorkScope ? workCount : null}
            open={notificationsOpen}
            onToggle={() => { setNotificationsOpen((value) => !value); setUserMenuOpen(false); }}
            onClose={() => setNotificationsOpen(false)}
            onOpenWork={(item) => {
              setNotificationsOpen(false);
              navigate('/my-work', { state: item?.source_key ? { focusWorkItem: item.source_key } : null });
            }}
            onOpenWorkforce={() => {
              setNotificationsOpen(false);
              navigate('/headquarters?section=hr-workspace');
            }}
          />}
          <div className="relative">
            <button type="button" aria-label="Open user menu" aria-expanded={userMenuOpen} onClick={() => { setUserMenuOpen((value) => !value); setNotificationsOpen(false); }} className="flex items-center gap-2 rounded-full py-1 pl-1 pr-2 transition hover:bg-white/10">
              {avatarUrl ? <img src={avatarUrl} alt="" className="h-9 w-9 rounded-full border border-amber-300/30 object-cover" referrerPolicy="no-referrer" /> : <span className="grid h-9 w-9 place-items-center rounded-full border border-amber-300/30 bg-amber-300/15 text-xs font-bold text-amber-200">{initials}</span>}
              <span className="hidden max-w-[150px] text-left leading-tight xl:block">
                <span className="block truncate text-xs font-semibold text-white">{displayName}</span>
                <span className="block truncate text-[10px] text-slate-400">{operatingTitle}</span>
              </span>
              <ChevronDown size={14} className="hidden text-slate-400 xl:block"/>
            </button>
            {userMenuOpen && (
              <div role="menu" aria-label="User account" className="absolute right-0 top-12 z-50 w-64 rounded-2xl border border-white/10 bg-[#101d32] p-3 shadow-2xl">
                <div className="border-b border-white/10 px-2 pb-3">
                  <p className="font-semibold text-white">{displayName}</p>
                  <p className="mt-1 break-all text-xs text-slate-400">{user?.email || 'Email not provided by session'}</p>
                  <p className="mt-2 text-xs text-amber-200">{operatingTitle}</p>
                </div>
                <button type="button" role="menuitem" onClick={() => { setUserMenuOpen(false); navigate("/system-status"); }} className="w-full rounded-lg px-2 py-2 text-left text-sm text-slate-200 hover:bg-white/5">System status</button>
                <button type="button" role="menuitem" disabled className="w-full cursor-not-allowed rounded-lg px-2 py-2 text-left text-sm text-slate-500" title="Profile route is not yet connected">Profile <span className="float-right text-[10px]">Unavailable</span></button>
                <button type="button" role="menuitem" disabled className="w-full cursor-not-allowed rounded-lg px-2 py-2 text-left text-sm text-slate-500" title="Preferences route is not yet connected">Preferences <span className="float-right text-[10px]">Unavailable</span></button>
                <button type="button" role="menuitem" onClick={() => { setUserMenuOpen(false); void onLogout(); }} className="mt-2 flex w-full items-center gap-2 rounded-lg border-t border-white/10 px-2 py-3 text-left text-sm text-red-200 hover:bg-red-400/10"><LogOut size={15}/> Sign out</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div>{children}</div>

      {searchOpen && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/65 px-4 pt-[12vh] backdrop-blur-sm" onMouseDown={(event) => { if (event.target === event.currentTarget) setSearchOpen(false); }}>
          <section role="dialog" aria-modal="true" aria-labelledby="wilsy-global-search-title" className="w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-[#101d32] shadow-2xl">
            <h2 id="wilsy-global-search-title" className="sr-only">Global search</h2>
            <form onSubmit={submitSearch} className="flex items-center gap-3 border-b border-white/10 px-5 py-4 focus-within:ring-2 focus-within:ring-inset focus-within:ring-[#d7ad43]">
              <Search size={19} className="text-amber-300"/>
              <input id="wilsy-global-search-input" value={searchValue} onChange={(event) => setSearchValue(event.target.value)} placeholder="Search people, projects, tasks, or anything…" className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-500 focus-visible:outline-none"/>
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

      if (MODEL_DEBUG) console.info('[ORCHESTRATOR-TRACE]', {
        isAuthenticated,
        userRole: user?.role,
        hasCovenant: user?.hasSignedCovenant,
        mfaRegistered: user?.mfaRegistered,
        tenantContextPresent: Boolean(currentTenant),
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
      console.error('[ORCHESTRATOR-ERROR]', { error: 'LIFECYCLE_TELEMETRY_FAILED' });
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
      <Route path="/covenant" element={<Navigate to="/" replace />} />
      <Route path="/headquarters" element={
        isAuthenticated && user && !systemServicesSession
          ? <ErrorBoundary><WilsyHeadquartersWorkspace key={[user.id, user.tenantId, user.role, user.workspaceId, user.businessRole].map((part) => String(part || '')).join(':')} tenantId={user.tenantId} /></ErrorBoundary>
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
 * @description Render the loading surface while EOS workspace authority resolves.
 * @collaboration Authenticated bootstrap and legal-acceptance boundaries.
 * @institutional Loading presentation grants no admission or financial authority.
 * @returns {JSX.Element} A bounded loading message; no provider or session is created.
 */
const WorkspaceBootstrapSurface = () => (
  <div data-testid="workspace-bootstrap" className="flex min-h-screen flex-col items-center justify-center bg-black text-center">
    <Loader2 className="mb-4 h-12 w-12 animate-spin text-[#D4AF37]" />
    <p className="font-mono text-xs tracking-widest uppercase text-[#D4AF37]">Preparing secure workspace</p>
    <p className="mt-2 max-w-md px-6 font-mono text-[10px] tracking-widest uppercase text-gray-500">Validating authenticated tenant authority...</p>
  </div>
);


const WorkspaceBootstrapError = ({ message, title = 'Workspace access is unavailable' }) => (
  <div data-testid="workspace-bootstrap-error" role="alert" className="flex min-h-screen flex-col items-center justify-center bg-black px-6 text-center">
    <p className="font-mono text-xs tracking-widest uppercase text-red-300">{title}</p>
    <p className="mt-3 max-w-lg font-mono text-[10px] tracking-widest uppercase text-gray-500">{typeof message === 'string' ? message : 'WORKSPACE_AUTHORITY_UNAVAILABLE'}</p>
  </div>
);

// In-flight transport sharing only: no completed acceptance is cached as
// authority. Keys include the exact bearer and scope and are never logged.
const platformAdmissionReads = new Map();
const PLATFORM_ADMISSION_STATES = new Set([
  'COMPLETE', 'USER_TERMS_REQUIRED', 'ADMIN_ACK_REQUIRED',
  'OWNER_AGREEMENTS_REQUIRED', 'MATERIAL_REACCEPTANCE_REQUIRED',
  'DOCUMENT_APPROVAL_REQUIRED',
]);

const acquirePlatformAdmission = (token, scope) => {
  const key = JSON.stringify([token, scope]);
  let entry = platformAdmissionReads.get(key);
  if (!entry) {
    const controller = new AbortController();
    entry = { controller, subscribers: 0, promise: null };
    const owned = entry;
    entry.promise = api.get('/legal-acceptance/status', {
      headers: { Authorization: 'Bearer ' + token },
      skipAuthRedirect: true,
      signal: controller.signal,
    }).finally(() => {
      if (platformAdmissionReads.get(key) === owned) platformAdmissionReads.delete(key);
    });
    platformAdmissionReads.set(key, entry);
  }
  entry.subscribers += 1;
  let released = false;
  return {
    promise: entry.promise,
    release: () => {
      if (released) return;
      released = true;
      entry.subscribers -= 1;
      queueMicrotask(() => {
        if (entry.subscribers === 0 && platformAdmissionReads.get(key) === entry) {
          platformAdmissionReads.delete(key);
          entry.controller.abort();
        }
      });
    },
  };
};

const validatePlatformAdmission = (plan, user) => {
  if (
    !plan || plan.admissionScope !== 'PLATFORM_WORKSPACE'
    || plan.tenantId !== user.tenantId || plan.principalId !== user.id
    || !PLATFORM_ADMISSION_STATES.has(plan.status)
    || !Array.isArray(plan.documents)
    || (plan.status === 'COMPLETE' && plan.documents.some((document) => document.accepted !== true))
  ) throw new Error('PLATFORM_ADMISSION_CONTRACT_INVALID');
  return plan;
};

const platformAdmissionError = (error) => {
  const status = error?.response?.status;
  if (status === 401) return { code: 'SESSION_EXPIRED', title: 'Sign-in needs verification' };
  if (status === 403) return { code: 'PLATFORM_ADMISSION_FORBIDDEN', title: 'Workspace admission is not authorized' };
  if (error?.message === 'PLATFORM_ADMISSION_CONTRACT_INVALID') {
    return { code: 'PLATFORM_ADMISSION_CONTRACT_INVALID', title: 'Workspace admission could not be verified' };
  }
  if (error?.code === 'ECONNABORTED' || error?.code === 'ETIMEDOUT') {
    return { code: 'PLATFORM_ADMISSION_SLOW', title: 'Workspace agreement verification is slow' };
  }
  return status
    ? { code: 'PLATFORM_ADMISSION_UNAVAILABLE', title: 'Workspace agreement service is unavailable' }
    : { code: 'PLATFORM_ADMISSION_UNREACHABLE', title: 'Workspace agreement service could not be reached' };
};

const PlatformAdmissionSession = ({ auth, scope, runtime }) => {
  const navigate = useNavigate();
  const [phase, setPhase] = useState('LOADING');
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const activeRef = useRef(false);
  const ownedReadsRef = useRef(new Set());

  const readStatus = useCallback(async () => {
    if (!activeRef.current) throw new Error('PLATFORM_ADMISSION_REQUEST_SUPERSEDED');
    const read = acquirePlatformAdmission(auth.token, scope);
    ownedReadsRef.current.add(read.release);
    try {
      const response = await read.promise;
      if (!activeRef.current) throw new Error('PLATFORM_ADMISSION_REQUEST_SUPERSEDED');
      return validatePlatformAdmission(response?.data, auth.user);
    } finally {
      read.release();
      ownedReadsRef.current.delete(read.release);
    }
  }, [auth.token, auth.user.id, auth.user.tenantId, scope]);

  const classifyFailure = useCallback((requestError) => {
    if (!activeRef.current) return;
    const classified = platformAdmissionError(requestError);
    setError(classified);
    setPhase('UNAVAILABLE');
    if (requestError?.response?.status === 401) {
      window.dispatchEvent(new CustomEvent('wilsy:session-invalidated'));
    }
  }, []);

  useEffect(() => {
    let current = true;
    activeRef.current = true;
    readStatus().then((nextPlan) => {
      if (!current || !activeRef.current) return;
      setPlan(nextPlan);
      setPhase(nextPlan.status === 'COMPLETE' ? 'COMPLETE' : 'REQUIRED');
    }).catch((requestError) => {
      if (current) classifyFailure(requestError);
    });
    return () => {
      current = false;
      activeRef.current = false;
      for (const release of ownedReadsRef.current) release();
      ownedReadsRef.current.clear();
    };
  }, [classifyFailure, readStatus]);

  const releaseWorkspace = (confirmedPlan) => {
    if (!activeRef.current) return;
    try {
      const confirmed = validatePlatformAdmission(confirmedPlan, auth.user);
      if (confirmed.status !== 'COMPLETE') return;
      setPlan(confirmed);
      setPhase('COMPLETE');
      navigate('/', { replace: true });
    } catch (requestError) {
      classifyFailure(requestError);
    }
  };

  const requestOptions = useMemo(() => ({
    headers: { Authorization: 'Bearer ' + auth.token },
    skipAuthRedirect: true,
  }), [auth.token]);

  if (phase === 'LOADING') return <WorkspaceBootstrapSurface />;
  if (phase === 'COMPLETE') return runtime;

  return (
    <AuthenticatedGlobalChrome user={auth.user} onLogout={auth.logout} workspaceReleased={false}>
      {phase === 'UNAVAILABLE' ? (
        <WorkspaceBootstrapError title={error?.title} message={error?.code} />
      ) : (
        <Routes>
          <Route path="/covenant" element={
            <LegalAcceptanceGate initialPlan={plan} presentation="platform"
              loadStatus={readStatus} requestOptions={requestOptions}
              onRequestError={classifyFailure} onComplete={releaseWorkspace} />
          } />
          <Route path="*" element={<Navigate to="/covenant" replace />} />
        </Routes>
      )}
    </AuthenticatedGlobalChrome>
  );
};

/**
 * @description Resolve mandatory platform-use agreements for one current EOS
 * session. This is not a Legal Operations product or practice admission gate.
 * @collaboration AuthProvider, TenantProvider, approved document/acceptance
 * registries, LegalAcceptanceGate presentation and protected runtime composition.
 * @institutional No read starts before authenticated bootstrap, exact tenant and
 * a non-empty canonical bearer. Session/capacity changes remount the boundary;
 * late responses cannot reuse a prior COMPLETE projection. No IAM, commercial,
 * persistence, transaction or financial authority is created.
 * @param {{runtime?: React.ReactNode}} props Optional deterministic render seam.
 * @returns {JSX.Element} Unverified loading, platform agreement/error or released runtime.
 */
export const LegalAcceptanceBoundary = ({ runtime = <RuntimeComposition /> }) => {
  const auth = useAuth();
  const credentialRevision = useRef({ token: auth.token, revision: 0 });
  if (credentialRevision.current.token !== auth.token) {
    credentialRevision.current = { token: auth.token, revision: credentialRevision.current.revision + 1 };
  }
  const tenantId = auth.user?.tenantId;
  const ready = Boolean(
    auth.isAuthenticated && auth.authStage === AUTH_STATES.AUTHENTICATED
    && !auth.loading && auth.user?.id && tenantId
    && typeof auth.token === 'string' && auth.token.trim() === auth.token
    && auth.token && !/^(undefined|null)$/i.test(auth.token)
  );
  if (!ready) return <WorkspaceBootstrapSurface />;
  const scope = JSON.stringify([
    auth.user.id, tenantId, auth.user.role, auth.user.workspaceId,
    auth.user.membershipRevision, auth.user.businessRoleRevision,
    auth.sessionGeneration, credentialRevision.current.revision,
  ]);
  return <PlatformAdmissionSession key={scope} auth={auth} scope={scope} runtime={runtime} />;
};

const RuntimeComposition = () => (
  <SovereignOrchestrator>
    <DataOrchestratorProvider>
      <SovereignRouter />
    </DataOrchestratorProvider>
  </SovereignOrchestrator>
);

const AuthenticatedRuntimeComposition = () => {
  const { isAuthenticated, authStage, loading, token, sessionGeneration, user } = useAuth();
  const { activeTenant } = useTenants();

  if (!isAuthenticated || loading || authStage !== AUTH_STATES.AUTHENTICATED || !token || !user?.id || !user?.tenantId || !activeTenant) {
    return <WorkspaceBootstrapError message="AUTHENTICATED_WORKSPACE_UNRESOLVED" />;
  }

  return (
    <>
      <RuntimeComposition />
      <WilsyOSIntelligenceDockRuntime
        key={JSON.stringify([user.id, user.tenantId, user.role, user.workspaceId, sessionGeneration])}
        sessionGeneration={sessionGeneration}
        authenticated
        authUser={user}
        activeTenant={activeTenant}
      />
    </>
  );
};

/**
 * @description Bind authenticated tenant presentation to exact EOS bootstrap truth.
 * @collaboration AuthProvider, TenantProvider and AuthenticatedBootstrapBoundary.
 * @institutional SYSTEM admission remains separately server-owned; tenant and
 * business capacities are never merged. Browser state cannot create membership,
 * legal acceptance or financial authority. No mutation or transaction is owned.
 * @param {{runtime?: React.ReactNode}} props Optional test-owned render seam.
 * @returns {JSX.Element} Independently gated SYSTEM, tenant or unauthenticated UI.
 */
export const AuthenticatedTenantBoundary = ({ runtime }) => {
  const { isAuthenticated, authStage, loading, token, sessionGeneration, tenant, user } = useAuth();
  if (!isAuthenticated) return <RuntimeComposition />;
  if (loading || authStage !== AUTH_STATES.AUTHENTICATED || !token || !user?.id) return <WorkspaceBootstrapSurface />;

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
    <TenantProvider key={JSON.stringify([user.id, user.tenantId, user.role, user.workspaceId, user.membershipRevision, user.businessRoleRevision, sessionGeneration])} initialTenant={tenant} authenticatedTenantId={String(user?.tenantId || '')}>
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

/**
 * @function App
 * @description Compose the single browser root and server-authorized tenant boundary.
 * @collaboration ErrorBoundary, AuthProvider, Router and AuthenticatedTenantBoundary.
 * @institutional Browser composition cannot issue identity, membership, MFA,
 * permission, legal-acceptance, payment or settlement authority. No persistence
 * or transaction is owned here; protected requests revalidate current EOS truth.
 * @returns {JSX.Element} Application root with bounded loading and denial states.
 */
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
 * VERSION: v20.5.0-PLATFORM-ADMISSION-SESSION-CURRENTNESS
 * AUTHORITY BOUNDARY: client route and protected-runtime composition only; Python EOS remains authentication, tenant and legal-acceptance authority
 * TENANT POSTURE: discovered tenant may choose login routing but cannot establish authenticated or protected scope
 * FAIL-CLOSED POSTURE: auth revalidation waits; unresolved legal status remains sealed; only server-confirmed legal COMPLETE mounts protected runtime
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
