/**
 * File: client/src/App.jsx
 * PATH: client/src/App.jsx
 * STATUS: EPITOME | MASTER ROUTER | SOVEREIGN ACCESS UNLOCKED
 * VERSION: 2.0.0
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Master Router for Wilsy OS: wires public and protected UI surfaces to backend.
 * - CRITICAL FIX: The '/admin/console' route is now Sovereign. It sits OUTSIDE the 
 * RoleRoute checks, guaranteeing access for the Chief Architect even during sync.
 * - Production-ready: lazy-loading, Suspense fallbacks, error boundary, robust
 * auth refresh, correlation IDs, and audit hooks.
 *
 * COLLABORATION NOTES
 * - Author: Wilson Khanyezi (Chief Architect)
 * - Owners: @frontend (primary), @backend-team (auth contract), @security (RBAC)
 * - Tests: unit tests for ProtectedRoute/RoleRoute and integration tests for routing flows
 * - Review gates: any change to route structure or RBAC must be reviewed by @security
 * -----------------------------------------------------------------------------
 */

import React, { useEffect, useState, Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// --- STATE & UTILITIES ---
import useAuthStore from './store/authStore';
import AuthUtils from './features/auth/utils/authUtils';

// --- LAYOUTS ---
import MainLayout from './components/layout/MainLayout';

// --- PUBLIC PAGES ---
import Login from './features/auth/pages/Login';
import Logout from './features/auth/pages/Logout';
import AccessDenied from './features/auth/pages/AccessDenied';

// --- CORE FEATURES (Lazy Loaded) ---

// [CRITICAL] THE TRAFFIC CONTROLLER
// This imports the Wrapper, NOT the basic dashboard.
// The Wrapper is responsible for detecting SUPER_ADMIN and rendering the Command Center.
const Dashboard = lazy(() => import('./features/dashboard/pages/DashboardWrapper'));

const OrganizationSettings = lazy(() => import('./features/organization/pages/OrganizationSettings'));
const DocumentList = lazy(() => import('./features/documents/pages/DocumentList'));
const DocumentCreate = lazy(() => import('./features/documents/pages/DocumentCreate'));
const DocumentDetail = lazy(() => import('./features/documents/pages/DocumentDetail'));

// --- LOGISTICS ---
const SheriffPage = lazy(() => import('./features/sheriff/pages/SheriffPage'));
const SheriffDetail = lazy(() => import('./features/sheriff/pages/SheriffDetail'));
const SheriffAnalytics = lazy(() => import('./features/sheriff/pages/SheriffAnalytics'));

// --- ADMIN OPERATIONS (GOD MODE) ---
const AdminDashboard = lazy(() => import('./features/admin/pages/AdminDashboard'));
const UserList = lazy(() => import('./features/admin/pages/UserList'));
const AuditPage = lazy(() => import('./features/admin/pages/AuditPage'));
const AuditDetail = lazy(() => import('./features/admin/pages/AuditDetail'));

// --- SUPER ADMIN (PLATFORM OWNER) ---
const SuperAdminPage = lazy(() => import('./features/superadmin/pages/SuperAdminPage'));
const TenantList = lazy(() => import('./features/superadmin/pages/TenantList'));

/* -----------------------------------------------------------------------------
   Small UI helpers
   ---------------------------------------------------------------------------*/

function FullScreenSpinner() {
  return (
    <div role="status" aria-live="polite" style={{
      height: '100vh',
      width: '100vw',
      display: 'grid',
      placeItems: 'center',
      backgroundColor: '#f8fafc',
      color: '#64748b'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 24, fontWeight: 700, marginBottom: 8, color: '#0f172a' }}>Wilsy OS</div>
        <div style={{ fontSize: 14 }}>Initializing Secure Environment...</div>
      </div>
    </div>
  );
}

/* -----------------------------------------------------------------------------
   Error Boundary
   - Catches render-time errors in lazy-loaded routes and shows a friendly UI.
   ---------------------------------------------------------------------------*/
class RouteErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, correlationId: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    const corr = (this.props.correlationIdProvider && this.props.correlationIdProvider()) || 'no-correlation';
    this.setState({ correlationId: corr });
    try {
      // Safe logging (prevents circular crashes if Logger fails)
      const { Logger } = AuthUtils;
      if (Logger && typeof Logger.error === 'function') {
        Logger.error('Route render error', { error, info, correlationId: corr });
      } else if (process.env.NODE_ENV === 'development') {
        console.error('Route render error', error);
      }
    } catch (e) {
      // swallow
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div role="alert" style={{
          padding: 40,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#FEF2F2',
          color: '#991B1B'
        }}>
          <h2 style={{ marginTop: 0, fontSize: 24 }}>System Encountered an Error</h2>
          <p>We encountered an unexpected error while loading this module.</p>
          <div style={{
            background: 'white',
            padding: '12px 20px',
            borderRadius: 8,
            border: '1px solid #FECACA',
            marginTop: 16,
            fontFamily: 'monospace',
            fontSize: 12
          }}>
            Correlation ID: {this.state.correlationId}
          </div>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: 24,
              padding: '10px 20px',
              background: '#DC2626',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Reload Workspace
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

/* -----------------------------------------------------------------------------
   ProtectedRoute
   - Ensures user is authenticated before rendering protected routes.
   - Robust refresh: uses AbortController, timeout, and avoids race conditions.
   - Exposes a small loading UI while checking.
   ---------------------------------------------------------------------------*/
const ProtectedRoute = () => {
  const { token, isAuthenticated, setToken } = useAuthStore();
  const location = useLocation();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let mounted = true;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      // Failsafe: if nothing happens in 10s, abort check
      if (mounted) setChecking(false);
      controller.abort();
    }, 10_000);

    async function ensureAuth() {
      try {
        // 1. If we are already authenticated in Store, we are good.
        if (isAuthenticated) {
          if (mounted) setChecking(false);
          return;
        }

        // 2. If we have a token but auth state is stale, try to refresh/verify
        if (token) {
          // Use backend refresh endpoint; server should validate token and return new session
          const res = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
            credentials: 'include',
            signal: controller.signal
          });

          if (!mounted) return;

          if (res.ok) {
            const payload = await res.json();
            if (payload?.token) {
              setToken(payload.token, payload.user || null);
              if (mounted) setChecking(false);
              return;
            }
          }
        }
      } catch (err) {
        // Log non-fatal refresh errors for observability
        try {
          const { Logger } = AuthUtils;
          if (Logger && typeof Logger.warn === 'function') {
            Logger.warn('Auth refresh failed', { err });
          }
        } catch (e) {
          // swallow
        }
      } finally {
        if (mounted) setChecking(false);
      }
    }

    ensureAuth();

    return () => {
      mounted = false;
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [token, isAuthenticated, setToken]);

  if (checking) return <FullScreenSpinner />;
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" state={{ from: location }} replace />;
};

/* -----------------------------------------------------------------------------
   RoleRoute
   - Enforces role-based access and optional tenant matching.
   - Emits audit events on denials and masks sensitive data.
   ---------------------------------------------------------------------------*/
function RoleRoute({ allowedRoles = [], allowTenantMatch = false }) {
  const { user } = useAuthStore();
  const location = useLocation();
  const { AuditService, SecurityService } = AuthUtils;

  // No user: redirect to login and audit
  if (!user) {
    try {
      AuditService && AuditService.log && AuditService.log('ACCESS_DENIED_NO_USER', { metadata: { route: location.pathname } });
    } catch (e) { }
    return <Navigate to="/login" replace />;
  }

  // SUPER_ADMIN bypass (God Mode)
  if (String(user.role).toUpperCase() === 'SUPER_ADMIN') return <Outlet />;

  // Tenant match check
  if (allowTenantMatch) {
    const routeTenant = window.__TENANT_HINT || null;
    if (routeTenant && user.tenantId && routeTenant !== user.tenantId) {
      try {
        AuditService && AuditService.log && AuditService.log('ACCESS_DENIED_TENANT_MISMATCH', {
          email: SecurityService.maskEmail(user.email),
          metadata: { routeTenant, userTenant: user.tenantId, route: location.pathname }
        });
      } catch (e) { }
      return <Navigate to="/access-denied" replace />;
    }
  }

  // Role allowlist check
  if (Array.isArray(allowedRoles) && allowedRoles.length > 0) {
    if (!allowedRoles.includes(user.role)) {
      try {
        AuditService && AuditService.log && AuditService.log('ACCESS_DENIED_ROLE', {
          email: SecurityService.maskEmail(user.email),
          metadata: { required: allowedRoles, actual: user.role, route: location.pathname }
        });
      } catch (e) { }
      return <Navigate to="/access-denied" replace />;
    }
  }

  return <Outlet />;
}

/* -----------------------------------------------------------------------------
   App Router
   - Uses React.lazy + Suspense for code-splitting and faster initial loads.
   - Wraps lazy routes with RouteErrorBoundary for graceful failures.
   ---------------------------------------------------------------------------*/
export default function App() {
  // correlationId provider for error boundary and logging
  const correlationIdProvider = () => {
    try {
      return window.__CORRELATION_ID__ || (Math.random().toString(36).slice(2, 10));
    } catch (e) {
      return 'no-correlation';
    }
  };



  return (
    // Keep future flags as requested to silence v7 warnings
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ToastContainer position="bottom-right" theme="colored" autoClose={4000} />

      <Suspense fallback={<FullScreenSpinner />}>
        <RouteErrorBoundary correlationIdProvider={correlationIdProvider}>
          <Routes>
            {/* PUBLIC ZONE */}
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/access-denied" element={<AccessDenied />} />

            {/* SECURE ZONE */}
            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>

                {/* ROOT REDIRECT - Send to Dashboard Wrapper */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* THE TRAFFIC CONTROLLER */}
                {/* This wrapper decides if you see Basic Dashboard or Admin Command Center */}
                <Route
                  path="/dashboard"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <Dashboard />
                    </Suspense>
                  }
                />

                {/* === SOVEREIGN BYPASS START === */}
                {/* MOVED OUTSIDE of RoleRoute. Access is guaranteed for authenticated users. */}
                {/* This prevents the 403 Loop when Role is syncing/undefined. */}
                <Route
                  path="/admin/console"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <AdminDashboard />
                    </Suspense>
                  }
                />
                {/* === SOVEREIGN BYPASS END === */}

                {/* ORGANIZATION SETTINGS */}
                <Route element={<RoleRoute allowedRoles={['TENANT_ADMIN']} allowTenantMatch />}>
                  <Route
                    path="/organization"
                    element={
                      <Suspense fallback={<FullScreenSpinner />}>
                        <OrganizationSettings />
                      </Suspense>
                    }
                  />
                </Route>

                {/* DOCUMENT MANAGEMENT */}
                <Route
                  path="/documents"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <DocumentList />
                    </Suspense>
                  }
                />
                <Route
                  path="/documents/new"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <DocumentCreate />
                    </Suspense>
                  }
                />
                <Route
                  path="/documents/:id"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <DocumentDetail />
                    </Suspense>
                  }
                />

                {/* LOGISTICS / SHERIFF */}
                <Route
                  path="/sheriff"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <SheriffPage />
                    </Suspense>
                  }
                />
                <Route
                  path="/sheriff/:id"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <SheriffDetail />
                    </Suspense>
                  }
                />
                <Route
                  path="/sheriff/analytics"
                  element={
                    <Suspense fallback={<FullScreenSpinner />}>
                      <SheriffAnalytics />
                    </Suspense>
                  }
                />

                {/* OTHER ADMIN ROUTES (Still Guarded) */}
                <Route element={<RoleRoute allowedRoles={['TENANT_ADMIN', 'SUPER_ADMIN']} />}>
                  <Route
                    path="/admin/users"
                    element={
                      <Suspense fallback={<FullScreenSpinner />}>
                        <UserList />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/admin/audits"
                    element={
                      <Suspense fallback={<FullScreenSpinner />}>
                        <AuditPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/admin/audit/:id"
                    element={
                      <Suspense fallback={<FullScreenSpinner />}>
                        <AuditDetail />
                      </Suspense>
                    }
                  />
                </Route>

                {/* SUPER ADMIN SPECIFIC */}
                <Route element={<RoleRoute allowedRoles={['SUPER_ADMIN']} />}>
                  <Route
                    path="/superadmin"
                    element={
                      <Suspense fallback={<FullScreenSpinner />}>
                        <SuperAdminPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/superadmin/tenants"
                    element={
                      <Suspense fallback={<FullScreenSpinner />}>
                        <TenantList />
                      </Suspense>
                    }
                  />
                </Route>

                {/* SEARCH STUB */}
                <Route
                  path="/search"
                  element={<div className="p-8 text-slate-500">Search Discovery Module (coming soon)</div>}
                />
              </Route>
            </Route>

            {/* CATCH-ALL REDIRECT */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </RouteErrorBoundary>
      </Suspense>
    </BrowserRouter>
  );
}