/**
 * File: client/src/components/layout/MainLayout.jsx
 * STATUS: PRODUCTION | APP SHELL | EPITOME
 * VERSION: 1.1.4
 *
 * CHANGES:
 * - Replaced defaultProps with JS default parameters.
 * - Use transient styled prop $sidebarColumn to avoid passing unknown props to DOM.
 * - Collaboration notes included.
 *
 * OWNER: @frontend, @security, @qa, @sre
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  useCallback,
  Suspense
} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Outlet, useLocation } from 'react-router-dom';
import AuditService from '../../features/auth/services/AuditService';

// Lazy-load heavy layout pieces
const Sidebar = React.lazy(() => import('../navigation/Sidebar'));
const AppTopBar = React.lazy(() => import('../topbar/AppTopBar'));

/* -------------------------
   Constants
   ------------------------- */

const SIDEBAR_WIDTH = 280;
const SIDEBAR_COLLAPSED = 80;
const MOBILE_BREAKPOINT = 1024;

/* -------------------------
   Styled primitives (grid-based) using transient prop $sidebarColumn
   ------------------------- */

/**
 * Note: using transient prop ($sidebarColumn) prevents styled-components from
 * forwarding the prop to the DOM, eliminating the React warning.
 */
const LayoutRoot = styled.div`
  --wilsy-gap: 24px;
  --wilsy-content-max: 1600px;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  color: #0f172a;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
  display: grid;
  grid-template-rows: 72px 1fr; /* topbar + content */
  grid-template-columns: ${props => props.$sidebarColumn};
  transition: grid-template-columns 320ms cubic-bezier(0.2,0.8,0.2,1);
  width: 100%;
  position: relative;
  overflow: hidden;

  @media (max-width: ${MOBILE_BREAKPOINT}px) {
    grid-template-columns: 1fr; /* single column on mobile */
  }
`;

const TopbarSlot = styled.div`
  grid-column: 1 / -1;
  grid-row: 1;
  z-index: 70;
`;

const SidebarSlot = styled.div`
  grid-column: 1;
  grid-row: 2;
  position: relative;
  z-index: 60;
`;

const MainSlot = styled.main`
  grid-column: 2;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;

  @media (max-width: ${MOBILE_BREAKPOINT}px) {
    grid-column: 1;
  }
`;

const ContentContainer = styled.div`
  flex: 1;
  padding: calc(var(--wilsy-gap) * 1.25);
  overflow-y: auto;
  max-width: var(--wilsy-content-max);
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
`;

const MobileOverlay = styled.div`
  display: none;
  @media (max-width: ${MOBILE_BREAKPOINT}px) {
    display: ${props => (props['data-open'] === 'true' ? 'block' : 'none')};
    position: fixed;
    inset: 0;
    background: rgba(2,6,23,0.5);
    z-index: 65;
    transition: opacity 180ms ease;
  }
`;

const SkipLink = styled.a`
  position: absolute;
  left: 12px;
  top: 12px;
  z-index: 1000;
  background: white;
  color: #0b3d91;
  padding: 8px 12px;
  border-radius: 8px;
  transform: translateY(-120%);
  transition: transform 160ms ease;
  &:focus {
    transform: translateY(0);
    outline: 3px solid rgba(0,163,224,0.18);
  }
`;

const VisuallyHidden = styled.span`
  border: 0;
  clip: rect(0 0 0 0);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
`;

/* -------------------------
   Persistence helpers
   ------------------------- */

const STORAGE_KEY = 'wilsy:ui:sidebarCollapsed:v1';

function safeReadLocalStorage(key, fallback = null) {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return fallback;
    return window.localStorage.getItem(key);
  } catch {
    return fallback;
  }
}

function safeWriteLocalStorage(key, value) {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return;
    window.localStorage.setItem(key, value);
  } catch {
    // ignore storage errors
  }
}

/* -------------------------
   Layout context and hook
   ------------------------- */

const LayoutContext = createContext(null);

export function useLayout() {
  const ctx = useContext(LayoutContext);
  if (!ctx) throw new Error('useLayout must be used within LayoutProvider');
  return ctx;
}

/* -------------------------
   LayoutProvider implementation
   ------------------------- */

/**
 * Use JS default parameters instead of defaultProps.
 * initialCollapsed: boolean | null
 * collapseOnRouteChange: boolean
 */
export function LayoutProvider({
  children = null,
  initialCollapsed = null,
  collapseOnRouteChange = true
}) {
  const persisted = typeof window !== 'undefined' ? safeReadLocalStorage(STORAGE_KEY, null) : null;
  const initialCollapsedResolved = (() => {
    if (initialCollapsed !== null) return !!initialCollapsed;
    if (persisted === 'true') return true;
    if (persisted === 'false') return false;
    return false;
  })();

  const [sidebarOpen, setSidebarOpenState] = useState(() => !initialCollapsedResolved);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(() => {
    try {
      if (typeof window === 'undefined') return false;
      return window.matchMedia && window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`).matches;
    } catch {
      return false;
    }
  });
  const [collapseOnRouteChangeState, setCollapseOnRouteChangeState] = useState(!!collapseOnRouteChange);

  const location = useLocation();
  const liveRef = useRef(null);
  const focusTargetRef = useRef(null);

  useEffect(() => {
    safeWriteLocalStorage(STORAGE_KEY, (!sidebarOpen).toString());
    try {
      if (liveRef.current) {
        liveRef.current.textContent = !sidebarOpen ? 'Navigation collapsed' : 'Navigation expanded';
        const t = setTimeout(() => { if (liveRef.current) liveRef.current.textContent = ''; }, 1200);
        return () => clearTimeout(t);
      }
    } catch { /* ignore */ }
    return undefined;
  }, [sidebarOpen]);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return undefined;
    const mq = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`);
    const handler = (e) => setIsMobile(!!e.matches);
    try {
      if (mq.addEventListener) mq.addEventListener('change', handler);
      else mq.addListener(handler);
    } catch {
      try { mq.addListener(handler); } catch { /* ignore */ }
    }
    return () => {
      try {
        if (mq.removeEventListener) mq.removeEventListener('change', handler);
        else mq.removeListener(handler);
      } catch { /* ignore */ }
    };
  }, []);

  useEffect(() => {
    if (isMobile && mobileMenuOpen && collapseOnRouteChangeState) {
      setMobileMenuOpen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    const onKeyDown = (e) => {
      const isMod = e.ctrlKey || e.metaKey;
      if (isMod && (e.key === 'b' || e.key === 'B')) {
        e.preventDefault();
        setSidebarOpenState(s => !s);
        try { AuditService?.log?.('UI_TOGGLE_SIDEBAR', { severity: 'info' }); } catch { /* swallow */ }
      }
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [mobileMenuOpen]);

  useEffect(() => {
    if (!mobileMenuOpen) return undefined;
    const t = setTimeout(() => {
      try {
        const root = document.querySelector('[data-wilsy-sidebar]');
        if (!root) return;
        const el = root.querySelector('button, a, [tabindex="0"]');
        if (el) el.focus();
      } catch { /* ignore */ }
    }, 120);
    return () => clearTimeout(t);
  }, [mobileMenuOpen]);

  useEffect(() => {
    const onUnload = () => {
      try { AuditService?.flush?.(); } catch { /* ignore */ }
    };
    window.addEventListener('pagehide', onUnload, { passive: true });
    window.addEventListener('beforeunload', onUnload, { passive: true });
    return () => {
      window.removeEventListener('pagehide', onUnload);
      window.removeEventListener('beforeunload', onUnload);
    };
  }, []);

  const setSidebarOpen = useCallback((open) => setSidebarOpenState(!!open), []);
  const toggleSidebar = useCallback(() => {
    setSidebarOpenState(s => !s);
    try { AuditService?.log?.('UI_TOGGLE_SIDEBAR', { severity: 'info' }); } catch { /* swallow */ }
  }, []);
  const openMobileMenu = useCallback(() => {
    setMobileMenuOpen(true);
    try { AuditService?.log?.('UI_OPEN_MOBILE_MENU', { severity: 'info' }); } catch { /* swallow */ }
  }, []);
  const closeMobileMenu = useCallback(() => {
    setMobileMenuOpen(false);
    try { AuditService?.log?.('UI_CLOSE_MOBILE_MENU', { severity: 'info' }); } catch { /* swallow */ }
  }, []);

  const contextValue = useMemo(() => ({
    sidebarOpen,
    setSidebarOpen,
    toggleSidebar,
    isMobile,
    openMobileMenu,
    closeMobileMenu,
    mobileMenuOpen,
    collapseOnRouteChange: collapseOnRouteChangeState,
    setCollapseOnRouteChange: setCollapseOnRouteChangeState,
    focusTargetRef
  }), [
    sidebarOpen,
    setSidebarOpen,
    toggleSidebar,
    isMobile,
    openMobileMenu,
    closeMobileMenu,
    mobileMenuOpen,
    collapseOnRouteChangeState
  ]);

  return (
    <LayoutContext.Provider value={contextValue}>
      {children}
      <VisuallyHidden id="wilsy-layout-live" ref={liveRef} aria-live="polite" aria-atomic="true" />
    </LayoutContext.Provider>
  );
}

LayoutProvider.propTypes = {
  children: PropTypes.node,
  initialCollapsed: PropTypes.bool,
  collapseOnRouteChange: PropTypes.bool
};

/* -------------------------
   Shell consumer (reads layout once)
   ------------------------- */

function Shell({ children = null }) {
  const layout = useLayout();
  const { sidebarOpen, toggleSidebar, openMobileMenu, mobileMenuOpen, closeMobileMenu } = layout;

  // Compute grid columns: explicit widths so layout is deterministic
  const sidebarColumn = `${sidebarOpen ? `${SIDEBAR_WIDTH}px` : `${SIDEBAR_COLLAPSED}px`} 1fr`;

  return (
    <LayoutRoot $sidebarColumn={sidebarColumn} role="application" aria-label="Wilsy OS workspace">
      <SkipLink href="#main-content">Skip to main content</SkipLink>

      <TopbarSlot>
        <Suspense fallback={<div style={{ height: 72, width: '100%', background: 'transparent' }} />}>
          <AppTopBar
            onToggleSidebar={toggleSidebar}
            onMobileMenuClick={openMobileMenu}
            isSidebarCollapsed={!sidebarOpen}
          />
        </Suspense>
      </TopbarSlot>

      <MobileOverlay
        data-open={mobileMenuOpen ? 'true' : 'false'}
        aria-hidden={!mobileMenuOpen}
        onClick={closeMobileMenu}
        data-testid="layout-mobile-overlay"
      />

      <SidebarSlot>
        <Suspense fallback={<div aria-hidden="true" style={{ width: sidebarOpen ? SIDEBAR_WIDTH : SIDEBAR_COLLAPSED, minWidth: sidebarOpen ? SIDEBAR_WIDTH : SIDEBAR_COLLAPSED, background: 'linear-gradient(180deg,#0b3d91,#08306f)' }} />}>
          <Sidebar data-wilsy-sidebar data-testid="sidebar-root" />
        </Suspense>
      </SidebarSlot>

      <MainSlot>
        <ContentContainer id="main-content" tabIndex={-1}>
          <Suspense fallback={<div>Synchronizing Wilsy Intelligence ...</div>}>
            {children || <Outlet />}
          </Suspense>
        </ContentContainer>
      </MainSlot>
    </LayoutRoot>
  );
}

Shell.propTypes = {
  children: PropTypes.node
};

/* -------------------------
   MainLayout wrapper (provider + shell)
   ------------------------- */

export default function MainLayout({ children = null }) {
  return (
    <LayoutProvider>
      <Shell>{children}</Shell>
    </LayoutProvider>
  );
}

MainLayout.propTypes = {
  children: PropTypes.node
};
