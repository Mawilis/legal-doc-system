/**
 * TITLE: WILSY OS Sovereign Application Root
 * VERSION: v20.13.0-VERIFIED-FOUNDER-IDENTITY-HEADER
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Composes authenticated routing, exact tenant projection, legal
 *          admission release, and protected workspace presentation without
 *          promoting browser state into authentication or legal authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/App.jsx
 * COLLABORATION / OWNERSHIP: AuthProvider owns browser auth projection;
 *                            TenantProvider owns bounded tenant projection;
 *                            Python EOS owns authentication, workspace and
 *                            legal-acceptance truth.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
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
 * CHANGELOG: v20.13.0-VERIFIED-FOUNDER-IDENTITY-HEADER displays EOS-issued Founder title independently from tenant_owner capacity; it never changes workspace authorization.
 * CHANGELOG: v20.10.2-GLOBAL-SEARCH-FOCUS-RETURN returns keyboard focus to the element that opened global search after Escape, dismissal, or navigation. Search routing, auth, and authority are unchanged.
 * CHANGELOG: v20.13.0-VERIFIED-FOUNDER-IDENTITY-HEADER displays email only from AuthProvider.workspaceEmail, which is populated solely by the current EOS workspace bootstrap; existing auth.user.email compatibility remains outside personal identity chrome.
 * CHANGELOG: v20.11.0-AUTHENTICATED-ACCOUNT-IDENTITY binds account identity to the exact active AuthProvider principal and tenant, removes unsupported personal links and diagnostics, and restores keyboard focus on menu dismissal. Search, session authority, and logout ownership are unchanged.
 * CHANGELOG: v20.10.3-GLOBAL-SEARCH-POINTER-DISMISS-FOCUS defers opener focus restoration until the browser completes pointer dismissal, preventing backdrop default behavior from stealing focus.
 * CHANGELOG: v20.10.1-FOUNDER-SQUARE-CORPORATE-IDENTITY preserves the Founder-supplied square WILSY OS identity
 * and current session capacity when no sourced job title is present. Authentication,
 * notifications, search ownership and route behavior are unchanged.
 * CHANGELOG: v20.9.0-OFFICIAL-SQUARE-BRAND-CHROME enlarges the official
 * square logo to 64px inside a 72px shared header, aligned with the existing
 * wordmark/tagline; authentication, identity and notification owners are intact.
 * CHANGELOG:
 *   v20.8.2-SUPPLIED-LOGO-PLATFORM-OWNER-CHROME — Preserves the Founder-selected square
 *     navy WILSY OS bitmap through the shared brand asset constant. Exact authenticated WILSY
 *     company scope suppresses the inherited Legal footer identifier.
 *   v20.8.1-FOUNDER-SUPPLIED-SQUARE-LOGO — Restores the supplied square navy
 *     WILSY OS logo following the Founder's explicit asset selection. Retains
 *     the wordmark, tagline, compact header, protected routes and source owners.
 *   v20.8.0-REFERENCE-GOLD-BRAND-COMPACT-CHROME — Uses the existing original
 *     gold ribbon PNG selected by the Founder reference, preserving its
 *     proportions and the wordmark/tagline. Aligns the shared header to the
 *     64px Headquarters workspace; session, search and notification owners
 *     remain unchanged. Direct Headquarters routes reuse the canonical
 *     dashboard controller so authenticated product switching stays accessible.
 *     No generated or simplified logo is substituted.
 *   v20.7.1-RESTORED-SUPPLIED-WILSY-OS-TOPBAR-MARK — Restores the
 *     user-supplied /icons/icon-192.png logo in its original 48px square slot
 *     and removes the substituted gold W import. Preserves the wordmark,
 *     tagline, navigation, session projection and existing workspace behavior.
 *   v20.7.0-FOUNDER-HEADQUARTERS-CHROME — Uses the existing approved gold W
 *     header emblem at the correct proportions, labels the working navigation
 *     shortcuts honestly, and routes the account diagnostics entry to the
 *     authenticated Headquarters kernel probe. Authentication, notification
 *     projection and tenant authorization are unchanged.
 *   v20.6.2-SUPPLIED-WILSY-OS-TOPBAR-MARK — Uses the user-approved
 *     supplied WILSY OS square icon in the existing 48px emblem slot;
 *     preserves the WILSY wordmark, Build. Operate. Grow. tagline and
 *     authenticated global chrome. No session or business authority changes.
 *   v20.6.1-ATTENTION-OPERATIONS-AUTHORISED-HANDOFF — Routes existing authenticated
 *     Daily Attention Operations entry to the source-owned Headquarters
 *     Operations workspace, with no browser-owned business command.
 *   v20.6.0-SESSION-SCOPED-ATTENTION-BADGE — Coordinates authenticated global work count
 *     with current EOS My Work reads. The badge no longer runs an unrelated
 *     weakly scoped query; exact-session source invalidation revalidates the
 *     count, and logout or role revision cancels the former response.
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
 */

/* eslint-disable */
import React, { Suspense, useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AUTH_STATES, AuthProvider, useAuth } from './contexts/authContext.jsx';
import { isWilsyPlatformTenant, WILSY_PLATFORM_LOGO_SRC } from './components/os/wilsyDashboardChromeConfig.js';
import { TenantProvider, useTenants } from './contexts/tenantContext';  // ✅ NEW IMPORT
import ErrorBoundary from './components/ErrorBoundary.jsx';
import { CheckCircle2, ChevronDown, Home, Loader2, LogOut, Search, ShieldCheck, UserRound, X } from 'lucide-react';
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
import api from './services/api';
import {
  currentUnifiedMyWorkScope,
  readUnifiedMyWork,
  subscribeUnifiedMyWork,
} from './services/unifiedMyWorkSync.js';
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
const exactChromeText = (value) => {
  if (typeof value !== 'string') return '';
  const normalized = value.trim();
  if (!normalized || normalized.length > 254 || /[\u0000-\u001f\u007f]/.test(normalized)) return '';
  return normalized;
};

const safeAccountEmail = (value) => {
  const email = exactChromeText(value);
  if (!email || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return '';
  return email;
};

const accountInitials = (name) => name
  .split(/\s+/)
  .filter(Boolean)
  .slice(0, 2)
  .map((part) => Array.from(part)[0]?.toLocaleUpperCase() || '')
  .join('');

const capacityLabel = (value) => {
  const capacity = exactChromeText(value);
  if (!capacity || !/^[A-Za-z0-9_-]+$/.test(capacity)) return '';
  const words = capacity.replace(/^tenant_/i, '').replace(/[_-]+/g, ' ').toLocaleLowerCase();
  return words ? words[0].toLocaleUpperCase() + words.slice(1) : '';
};

export const AuthenticatedGlobalChrome = ({ user, onLogout, children, workspaceReleased = true }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const auth = useAuth();
  const { isAuthenticated, authStage, loading: authLoading } = auth;
  const [searchOpen, setSearchOpen] = useState(false);
  const searchReturnFocusRef = useRef(null);
  const searchWasOpenRef = useRef(false);
  const [searchValue, setSearchValue] = useState('');
  const [searchNotice, setSearchNotice] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const accountTriggerRef = useRef(null);
  const accountMenuRef = useRef(null);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [workCount, setWorkCount] = useState(null);
  const [workCountScope, setWorkCountScope] = useState(null);

  const hasAuthenticatedSession = isAuthenticated && authStage === AUTH_STATES.AUTHENTICATED;
  const activePrincipal = auth?.user;
  const activeTenant = auth?.tenant;
  const exactPrincipal = Boolean(
    hasAuthenticatedSession
    && activePrincipal?.id
    && String(activePrincipal.id) === String(user?.id || '')
    && (
      activePrincipal.systemServicesWorkspace
        ? activePrincipal.systemServicesWorkspace.principalId === activePrincipal.id
        : Boolean(activePrincipal.tenantId)
          && String(activePrincipal.tenantId) === String(user?.tenantId || '')
      )
  );
  const sessionUser = exactPrincipal ? activePrincipal : null;
  const displayName = sessionUser
    ? [exactChromeText(sessionUser.firstName), exactChromeText(sessionUser.lastName)].filter(Boolean).join(' ')
    : '';
  const accountEmail = safeAccountEmail(sessionUser?.workspaceEmail);
  const tenantIdentity = sessionUser?.tenantId
    && String(activeTenant?.tenantId || '') === String(sessionUser.tenantId)
    ? activeTenant
    : null;
  const organisationName = exactChromeText(tenantIdentity?.legalName)
    || exactChromeText(tenantIdentity?.name);
  const currentCapacity = sessionUser?.workspaceContractVersion === 'v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION'
    ? exactChromeText(sessionUser.businessRole || sessionUser.role)
    : '';
  const selectedCapacityLabel = capacityLabel(currentCapacity);
  const institutionalTitle = sessionUser?.institutionalDesignation === 'Founder'
    && sessionUser?.tenantId === 'WILSYTENANT-4CD2FZ4O'
    && currentCapacity === 'tenant_owner'
    ? 'Founder'
    : '';
  const identityLabel = displayName || accountEmail || '';
  const initials = accountInitials(displayName);
  const accountScope = sessionUser
    ? `${sessionUser.id}:${sessionUser.tenantId || 'SYSTEM'}:${currentCapacity}:${auth.sessionGeneration ?? ''}`
    : '';
  const isSecureChannel = typeof window !== 'undefined'
    && window.location.protocol === 'https:';

  // The exact AuthProvider session generation, selected capacity and both role
  // revisions partition this optional badge. It is active-work evidence, never
  // an unread-notification count or browser permission authority.
  const currentWorkScope = currentUnifiedMyWorkScope(auth, sessionUser?.tenantId);
  const isPlatformOwnerWorkspace = Boolean(currentWorkScope && isWilsyPlatformTenant(sessionUser?.tenantId));

  useEffect(() => {
    setUserMenuOpen(false);
    setNotificationsOpen(false);
  }, [accountScope]);

  useEffect(() => {
    if (!userMenuOpen) return undefined;
    const firstMenuItem = accountMenuRef.current?.querySelector('[role="menuitem"]');
    firstMenuItem?.focus();
    const dismissOutside = (event) => {
      if (!accountMenuRef.current?.contains(event.target)) setUserMenuOpen(false);
    };
    document.addEventListener('pointerdown', dismissOutside);
    return () => document.removeEventListener('pointerdown', dismissOutside);
  }, [userMenuOpen]);

  useEffect(() => {
    if (!workspaceReleased || !hasAuthenticatedSession || authLoading || !currentWorkScope) {
      setWorkCountScope(null);
      setWorkCount(null);
      return undefined;
    }
    let active = true;
    const controller = new AbortController();
    const expectedScope = { tenantId: sessionUser.tenantId, principalId: sessionUser.id };
    const refresh = async () => {
      try {
        const payload = await readUnifiedMyWork(
          currentWorkScope, expectedScope, { signal: controller.signal, force: true },
        );
        if (active) {
          setWorkCountScope(currentWorkScope);
          setWorkCount(payload.summary.active_count);
        }
      } catch (error) {
        if (active && error?.name !== 'AbortError') {
          setWorkCountScope(null);
          setWorkCount(null);
        }
      }
    };
    const unsubscribe = subscribeUnifiedMyWork(currentWorkScope, () => {
      void refresh();
    });
    void refresh();
    const interval = window.setInterval(refresh, 60000);
    return () => {
      active = false;
      controller.abort();
      window.clearInterval(interval);
      unsubscribe();
    };
  }, [workspaceReleased, hasAuthenticatedSession, authLoading, currentWorkScope, sessionUser?.id, sessionUser?.tenantId]);

  const openGlobalSearch = () => {
    const returnFocus = document.activeElement;
    const request = new CustomEvent('wilsy:open-command-search', { cancelable: true });
    const unclaimed = window.dispatchEvent(request);
    if (unclaimed) searchReturnFocusRef.current = returnFocus;
    setSearchOpen(unclaimed);
    setSearchNotice('');
    setUserMenuOpen(false);
    setNotificationsOpen(false);
  };

  useEffect(() => {
    const handleShortcut = (event) => {
      if (event.defaultPrevented) return;
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        const returnFocus = document.activeElement;
        const request = new CustomEvent('wilsy:open-command-search', { cancelable: true });
        const unclaimed = window.dispatchEvent(request);
        if (unclaimed) searchReturnFocusRef.current = returnFocus;
        setSearchOpen(unclaimed);
        setSearchNotice('');
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
      searchWasOpenRef.current = true;
      const input = document.getElementById('wilsy-global-search-input');
      input?.focus();
      return;
    }
    if (!searchWasOpenRef.current) return;
    searchWasOpenRef.current = false;
    const returnFocus = searchReturnFocusRef.current;
    searchReturnFocusRef.current = null;
    if (!returnFocus?.isConnected || typeof returnFocus.focus !== 'function') return;

    // Backdrop pointer dismissal can run the browser's default focus behavior
    // after React commits this close. Deferring one task lets that behavior
    // finish before focus returns to the actual header opener.
    const focusTimer = window.setTimeout(() => {
      if (returnFocus.isConnected) returnFocus.focus();
    }, 0);
    return () => window.clearTimeout(focusTimer);
  }, [searchOpen]);

  const submitSearch = (event) => {
    event.preventDefault();
    const query = searchValue.trim().toLowerCase();
    if (query === 'headquarters' || query === 'home') {
      navigate('/headquarters');
      setSearchOpen(false);
      setSearchValue('');
      setSearchNotice('');
    } else if (query === 'my work' || query === 'tasks') {
      navigate('/my-work');
      setSearchOpen(false);
      setSearchValue('');
      setSearchNotice('');
    } else {
      setSearchNotice('No matching workspace shortcut. Choose Headquarters or My Work.');
    }
  };

  return (
    <div className="min-h-screen bg-[#080f1d] text-slate-100" data-wilsy-platform-owner={isPlatformOwnerWorkspace ? 'true' : undefined}>
      {isPlatformOwnerWorkspace && <style>{'body:has([data-wilsy-platform-owner="true"])::after{display:none!important}'}</style>}
      <header className="sticky top-0 z-40 flex h-[72px] w-full min-w-0 items-center gap-2 border-b border-white/10 bg-gradient-to-r from-[#0b1830] via-[#112444] to-[#0b1830] px-3 shadow-lg shadow-black/10 backdrop-blur-xl sm:gap-4 sm:px-4 xl:px-5">
        <button type="button" aria-label="WILSY home" onClick={() => navigate('/headquarters')} className="flex min-w-0 shrink-0 items-center gap-2 text-left md:w-[228px] xl:w-[228px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d7ad43] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0b1830]">
          <img src={WILSY_PLATFORM_LOGO_SRC} alt="WILSY OS logo" className="h-14 w-14 shrink-0 object-contain md:h-16 md:w-16" />
          <span className="hidden min-w-0 leading-tight min-[360px]:block">
            <span className="block text-[23px] font-bold tracking-[0.045em] md:text-[30px] text-white">WILSY</span>
            <span className="block whitespace-nowrap text-[9px] font-medium text-[#f0dca5] md:text-[11px]">Build. Operate. Grow.</span>
          </span>
        </button>

        <button type="button" onClick={openGlobalSearch} aria-label="Open workspace navigation" className="mx-auto hidden h-10 min-w-0 max-w-[690px] flex-1 items-center gap-3 rounded-full border border-white/15 bg-white px-4 text-left text-sm text-[#435575] transition hover:border-[#d7ad43] hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d7ad43] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0b1830] md:flex">
          <Search size={16} className="text-[#435575]"/>
          <span className="flex-1">Search authorized work or navigate…</span>
          <kbd className="rounded-md border border-slate-200 bg-slate-100 px-2 py-1 text-[10px] text-slate-500">⌘ K / Ctrl K</kbd>
        </button>
        <button type="button" onClick={openGlobalSearch} aria-label="Open workspace navigation" className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-white/10 text-slate-300 md:hidden"><Search size={17}/></button>

        <div className="ml-auto flex min-w-0 shrink-0 items-center justify-end gap-1 sm:gap-3">
          {hasAuthenticatedSession && !authLoading && (
            <div role="status" aria-label={isSecureChannel ? 'Secure and authenticated' : 'Authenticated; secure transport not confirmed'} className={`flex items-center gap-2 rounded-full border px-2 py-2 text-[11px] font-medium sm:px-3 ${isSecureChannel ? 'border-emerald-400/20 bg-emerald-400/10 text-emerald-200' : 'border-emerald-400/25 bg-emerald-500/20 text-emerald-100'}`}>
              <ShieldCheck size={15}/>
              <span className="hidden sm:inline">{isSecureChannel ? 'Secure · Authenticated' : 'Authenticated'}</span>
            </div>
          )}
          {workspaceReleased && sessionUser && <WilsyDailyAttentionCentre
            key={currentWorkScope}
            tenantId={sessionUser?.tenantId}
            systemServicesWorkspace={Boolean(sessionUser?.systemServicesWorkspace)}
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
            onOpenOperations={() => {
              setNotificationsOpen(false);
              navigate('/headquarters?section=operations');
            }}
          />}
          {sessionUser && <div ref={accountMenuRef} className="relative">
            <button ref={accountTriggerRef} type="button" aria-label="Open account menu" aria-haspopup="menu" aria-expanded={userMenuOpen} onClick={() => { setUserMenuOpen((value) => !value); setNotificationsOpen(false); }} className="flex items-center gap-2 rounded-full py-1 pl-1 pr-2 transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d7ad43]">
              <span className="grid h-9 w-9 place-items-center rounded-full border border-amber-300/30 bg-amber-300/15 text-xs font-bold text-amber-200" aria-hidden="true">{initials || <UserRound size={17}/>}</span>
              <span className="hidden max-w-[150px] text-left leading-tight xl:block">
                <span className="block truncate text-xs font-semibold text-white">{identityLabel || 'Account identity unavailable'}</span>
                {institutionalTitle && <span className="block truncate text-[10px] font-semibold text-emerald-200">{institutionalTitle} · WILSY OS</span>}
                {selectedCapacityLabel && <span className="block truncate text-[10px] text-slate-400">{selectedCapacityLabel} capacity</span>}
              </span>
              <ChevronDown size={14} className="hidden text-slate-400 xl:block"/>
            </button>
            {userMenuOpen && (
              <div role="menu" aria-label="Account menu" onKeyDown={(event) => {
                const items = Array.from(event.currentTarget.querySelectorAll('[role="menuitem"]'));
                const index = items.indexOf(document.activeElement);
                if (event.key === 'Escape') {
                  event.preventDefault();
                  setUserMenuOpen(false);
                  accountTriggerRef.current?.focus();
                  event.stopPropagation();
                } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp' || event.key === 'Home' || event.key === 'End') {
                  event.preventDefault();
                  const next = event.key === 'Home' ? 0 : event.key === 'End' ? items.length - 1
                    : (index + (event.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length;
                  items[next]?.focus();
                }
              }} className="absolute right-0 top-12 z-50 w-[min(20rem,calc(100vw-1.5rem))] rounded-2xl border border-white/10 bg-[#101d32] p-3 shadow-2xl">
                <div className="border-b border-white/10 px-2 pb-3">
                  <p className="font-semibold text-white">{displayName || 'Name not provided by EOS'}</p>
                  {accountEmail && <p className="mt-1 break-all text-xs text-slate-400">{accountEmail}</p>}
                  {organisationName && <p className="mt-2 text-xs text-amber-200">{organisationName}</p>}
                  {institutionalTitle && <p className="mt-1 text-xs font-semibold text-emerald-200">Institutional designation: {institutionalTitle}</p>}
                  {selectedCapacityLabel && <p className="mt-1 text-xs text-slate-300">Selected capacity: {selectedCapacityLabel}</p>}
                </div>
                <button type="button" role="menuitem" onClick={() => { setUserMenuOpen(false); void onLogout(); }} className="mt-2 flex w-full items-center gap-2 rounded-lg px-2 py-3 text-left text-sm text-red-200 hover:bg-red-400/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#d7ad43]"><LogOut size={15}/> Sign out</button>
              </div>
            )}
          </div>}
        </div>
      </header>

      <div>{children}</div>

      {searchOpen && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/65 px-4 pt-[12vh] backdrop-blur-sm" onMouseDown={(event) => { if (event.target === event.currentTarget) setSearchOpen(false); }}>
          <section role="dialog" aria-modal="true" aria-labelledby="wilsy-global-search-title" className="w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-[#101d32] shadow-2xl">
            <h2 id="wilsy-global-search-title" className="sr-only">Workspace navigation</h2>
            <form onSubmit={submitSearch} className="flex items-center gap-3 border-b border-white/10 px-5 py-4 focus-within:ring-2 focus-within:ring-inset focus-within:ring-[#d7ad43]">
              <Search size={19} className="text-amber-300"/>
              <input id="wilsy-global-search-input" value={searchValue} onChange={(event) => setSearchValue(event.target.value)} aria-label="Workspace destination" placeholder="Headquarters or My Work" className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-500 focus-visible:outline-none"/>
              <kbd className="rounded border border-white/10 px-2 py-1 text-[10px] text-slate-400">ESC</kbd>
              <button type="button" aria-label="Close search" onClick={() => setSearchOpen(false)}><X size={17}/></button>
            </form>
            <div className="p-5">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">Quick navigation</p>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <button type="button" onClick={() => { navigate('/headquarters'); setSearchOpen(false); setSearchValue(''); setSearchNotice(''); }} className="flex items-center gap-3 rounded-xl border border-white/10 p-3 text-left text-sm hover:border-amber-300/40"><Home size={17} className="text-amber-300"/> Headquarters</button>
                <button type="button" onClick={() => { navigate('/my-work'); setSearchOpen(false); setSearchValue(''); setSearchNotice(''); }} className="flex items-center gap-3 rounded-xl border border-white/10 p-3 text-left text-sm hover:border-amber-300/40"><CheckCircle2 size={17} className="text-amber-300"/> My Work</button>
              </div>
              <p role={searchNotice ? 'status' : undefined} className="mt-4 text-xs leading-5 text-slate-400">{searchNotice || 'Only Headquarters and My Work shortcuts are available here. Permission-filtered record search is not connected.'}</p>
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
          ? <ErrorBoundary><SovereignDashboardController key={[user.id, user.tenantId, user.role, user.workspaceId, user.businessRole, location.key].map((part) => String(part || '')).join(':')} user={user} onLogout={logout} initialWorkspace="headquarters" /></ErrorBoundary>
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
 * VERSION: v20.13.0-VERIFIED-FOUNDER-IDENTITY-HEADER
 * AUTHORITY BOUNDARY: client route and protected-runtime composition only; Python EOS remains authentication, tenant and legal-acceptance authority
 * TENANT POSTURE: discovered tenant may choose login routing but cannot establish authenticated or protected scope
 * FAIL-CLOSED POSTURE: auth revalidation waits; unresolved legal status remains sealed; only server-confirmed legal COMPLETE mounts protected runtime
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
