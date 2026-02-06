/**
 * File: client/src/components/layout/Header.jsx
 * STATUS: PRODUCTION | EPITOME | SUPER ADMIN FIRST
 * VERSION: 2026-01-10
 *
 * PURPOSE
 * - Authoritative top navigation for Wilsy OS.
 * - Consumes layout context via useLayout for hamburger toggle and mobile menu.
 * - Integrates global search, notifications, theme toggle, tenant quick-switch,
 *   user identity cockpit, audit emission, keyboard-first UX, and accessibility.
 *
 * PRINCIPLES
 * - Defensive: safe for SSR and missing browser APIs.
 * - Non-blocking telemetry: audit calls are best-effort and never block UI.
 * - Accessibility: ARIA roles, keyboard shortcuts, focus management, visible focus states.
 * - Testable: data-testid attributes and deterministic behavior for unit and E2E tests.
 *
 * INTEGRATION CONTRACTS
 * - Expects useLayout exported from MainLayout in the same folder:
 *     import { useLayout } from './MainLayout';
 * - Expects useAuthStore at ../../store/authStore
 * - Expects UserAvatar at ../common/UserAvatar
 * - Expects AuditService at ../../features/auth/services/AuditService
 * - Expects AuthUtils at ../../features/auth/utils/authUtils
 *
 * AUTHOR: Chief Architect Wilson Khanyezi
 */

import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
  useMemo
} from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import {
  FiMenu,
  FiBell,
  FiSearch,
  FiSun,
  FiMoon,
  FiChevronDown,
  FiUser,
  FiSettings,
  FiLogOut,
  FiShield
} from 'react-icons/fi';
import PropTypes from 'prop-types';

import { useLayout } from './MainLayout';
import useAuthStore from '../../store/authStore';
import UserAvatar from '../common/UserAvatar';
import AuthUtils from '../../features/auth/utils/authUtils';
import AuditService from '../../features/auth/services/AuditService';

/* -------------------------
   Styled primitives
   ------------------------- */

const HeaderRoot = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  padding: 0 20px;
  background: var(--topbar-bg, #ffffff);
  border-bottom: 1px solid var(--border, #e6eef8);
  position: sticky;
  top: 0;
  z-index: 60;
  box-shadow: 0 1px 0 rgba(2,6,23,0.03);
`;

const LeftGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const RightGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
`;

const IconButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--muted, #64748b);
  cursor: pointer;
  transition: background 160ms ease, color 160ms ease, transform 120ms ease;

  &:hover,
  &:focus {
    background: var(--hover, #f1f5f9);
    color: var(--accent, #0f172a);
    outline: none;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const SearchBox = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--search-bg, #f8fafc);
  border: 1px solid transparent;
  min-width: 320px;
  max-width: 640px;
  transition: box-shadow 160ms ease, border-color 160ms ease;

  &:focus-within {
    background: #fff;
    border-color: rgba(37,99,235,0.08);
    box-shadow: 0 6px 20px rgba(37,99,235,0.06);
  }

  @media (max-width: 880px) {
    min-width: 180px;
  }

  @media (max-width: 640px) {
    display: none;
  }
`;

const SearchInput = styled.input`
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  font-size: 0.95rem;
  color: var(--text, #0f172a);

  &::placeholder {
    color: #94a3b8;
  }
`;

const SearchShortcut = styled.span`
  font-size: 0.72rem;
  padding: 4px 8px;
  border-radius: 6px;
  background: #fff;
  border: 1px solid rgba(14,165,233,0.06);
  color: #94a3b8;
  font-weight: 800;
`;

const Divider = styled.div`
  width: 1px;
  height: 28px;
  background: var(--border, #e6eef8);
`;

const NotificationBadge = styled.span`
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 6px rgba(239,68,68,0.28);
`;

const ProfileButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 160ms ease, border-color 160ms ease;

  &:hover,
  &:focus {
    background: var(--hover, #f8fafc);
    border-color: var(--border, #e6eef8);
    outline: none;
  }
`;

const ProfileMeta = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 120px;

  .name {
    font-weight: 700;
    color: var(--text, #0f172a);
    font-size: 0.92rem;
  }

  .role {
    font-size: 0.68rem;
    color: var(--accent, #3b82f6);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.6px;
  }

  @media (max-width: 640px) {
    display: none;
  }
`;

const MenuPanel = styled.div`
  position: absolute;
  top: 72px;
  right: 16px;
  width: 320px;
  max-width: calc(100% - 32px);
  background: var(--panel-bg, #ffffff);
  border: 1px solid var(--border, #e6eef8);
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(2,6,23,0.12);
  padding: 8px;
  z-index: 120;
  transform-origin: top right;
  animation: menuIn 160ms ease-out;

  @keyframes menuIn {
    from { opacity: 0; transform: translateY(-6px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
`;

const MenuItem = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--muted, #334155);
  font-weight: 700;
  cursor: pointer;
  text-align: left;

  &:hover,
  &:focus {
    background: rgba(14,165,233,0.04);
    color: var(--accent, #0b3d91);
    outline: none;
  }

  &.danger {
    color: #ef4444;
  }
`;

/* -------------------------
   Helper utilities
   ------------------------- */

/**
 * safeEmitAudit
 * - Best-effort audit emitter that never throws.
 * - Attaches a correlationId when possible.
 */
async function safeEmitAudit(eventType, details = {}) {
  try {
    const payload = { ...details };
    if (!payload.correlationId) {
      payload.correlationId = AuthUtils?.SecurityService?.generateCorrelationId?.() || `ui_${Date.now()}`;
    }
    if (AuditService && typeof AuditService.log === 'function') {
      await AuditService.log(eventType, payload);
      return;
    }
    if (AuthUtils && AuthUtils.AuditService && typeof AuthUtils.AuditService.log === 'function') {
      await AuthUtils.AuditService.log(eventType, payload);
      return;
    }
    if (process.env.NODE_ENV !== 'production') {
      // eslint-disable-next-line no-console
      console.debug('[AUDIT] fallback', eventType, payload);
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('[AUDIT] emit failed', e);
  }
}

/**
 * maskForUi
 * - Lightweight masking for UI display.
 */
function maskForUi(value = '') {
  try {
    if (!value || typeof value !== 'string') return '';
    if (value.includes('@')) {
      return AuthUtils?.SecurityService?.maskEmail?.(value) || value;
    }
    if (value.length > 24) return `${value.slice(0, 12)}...${value.slice(-8)}`;
    return value;
  } catch {
    return value;
  }
}

/* -------------------------
   Component
   ------------------------- */

export default function Header({ showSearch = true }) {
  const navigate = useNavigate();
  const { sidebarOpen, toggleSidebar, openMobileMenu } = useLayout();
  const { user, tenants = [], logout, switchTenant, refreshUser, getAuthHeaders } = useAuthStore();

  // UI state
  const [menuOpen, setMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isDark, setIsDark] = useState(() => {
    try {
      return document?.documentElement?.getAttribute('data-theme') === 'dark';
    } catch {
      return false;
    }
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [spotlightOpen, setSpotlightOpen] = useState(false);
  const [tenantSwitching, setTenantSwitching] = useState(false);

  const profileRef = useRef(null);
  const menuRef = useRef(null);
  const notifRef = useRef(null);
  const searchRef = useRef(null);

  const displayName = useMemo(() => {
    if (!user) return 'Chief Architect';
    const name = user.firstName || user.name || '';
    const last = user.lastName || '';
    const full = `${name} ${last}`.trim();
    return full || user.email || 'Chief Architect';
  }, [user]);

  const roleLabel = useMemo(() => (user?.role || 'GUEST').toUpperCase(), [user]);

  // Initialize unread notifications from persisted store
  useEffect(() => {
    try {
      const raw = localStorage.getItem('wilsy_unread_notifications');
      const n = raw ? parseInt(raw, 10) : 0;
      setUnreadCount(Number.isFinite(n) ? n : 0);
    } catch {
      setUnreadCount(0);
    }
  }, []);

  // Keyboard shortcuts: Cmd/Ctrl+K to open search, Esc to close menus
  useEffect(() => {
    const onKey = (e) => {
      const isMac = navigator?.platform?.toUpperCase().includes('MAC');
      const mod = isMac ? e.metaKey : e.ctrlKey;
      if (mod && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSpotlightOpen(true);
        setTimeout(() => searchRef.current?.focus?.(), 50);
        safeEmitAudit('UI_SPOTLIGHT_OPEN', { actor: user?.email, severity: 'info' });
      }
      if (e.key === 'Escape') {
        if (menuOpen) setMenuOpen(false);
        if (notifOpen) setNotifOpen(false);
        if (spotlightOpen) setSpotlightOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [menuOpen, notifOpen, spotlightOpen, user]);

  // Click outside to close menus
  useEffect(() => {
    const onDocDown = (e) => {
      if (menuOpen && menuRef.current && !menuRef.current.contains(e.target) && profileRef.current && !profileRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
      if (notifOpen && notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocDown);
    document.addEventListener('touchstart', onDocDown);
    return () => {
      document.removeEventListener('mousedown', onDocDown);
      document.removeEventListener('touchstart', onDocDown);
    };
  }, [menuOpen, notifOpen]);

  // Toggle theme and persist
  const toggleTheme = useCallback(() => {
    const next = isDark ? 'light' : 'dark';
    try {
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('wilsy_theme', next);
    } catch {
      // ignore storage errors
    }
    setIsDark(next === 'dark');
    safeEmitAudit('UI_THEME_TOGGLE', { actor: user?.email, severity: 'info', metadata: { theme: next } });
  }, [isDark, user]);

  // Toggle sidebar via layout context
  const handleToggleSidebar = useCallback(() => {
    toggleSidebar();
    safeEmitAudit('UI_TOGGLE_SIDEBAR', { actor: user?.email, severity: 'info' });
  }, [toggleSidebar, user]);

  // Open notifications panel
  const openNotifications = useCallback(() => {
    setNotifOpen(true);
    safeEmitAudit('UI_OPEN_NOTIFICATIONS', { actor: user?.email, severity: 'info' });
    navigate('/notifications');
  }, [user, navigate]);

  // Toggle profile menu
  const toggleProfileMenu = useCallback(() => {
    setMenuOpen(s => !s);
    safeEmitAudit('UI_TOGGLE_PROFILE_MENU', { actor: user?.email, severity: 'info', metadata: { open: !menuOpen } });
  }, [menuOpen, user]);

  // Search submit
  const handleSearchSubmit = useCallback((q) => {
    if (!q || !q.trim()) return;
    safeEmitAudit('UI_SEARCH', { actor: user?.email, severity: 'info', metadata: { query: q } });
    navigate(`/search?q=${encodeURIComponent(q)}`);
    setSearchQuery('');
    setSpotlightOpen(false);
  }, [navigate, user]);

  // Debounced search placeholder
  useEffect(() => {
    if (!searchQuery) return undefined;
    const t = setTimeout(() => {
      // placeholder for suggestions or API calls
    }, 300);
    return () => clearTimeout(t);
  }, [searchQuery]);

  // Logout sequence
  const handleLogout = useCallback(async () => {
    try {
      await safeEmitAudit('AUTH_LOGOUT_REQUEST', { actor: user?.email, severity: 'info', metadata: { reason: 'user_initiated' } });
    } catch {
      // swallow
    } finally {
      try {
        await logout();
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Logout failed', e);
      } finally {
        navigate('/login');
      }
    }
  }, [logout, navigate, user]);

  // Tenant switch for SUPER_ADMIN
  const handleTenantSwitch = useCallback(async (tenantId) => {
    if (!tenantId) return;
    setTenantSwitching(true);
    try {
      await safeEmitAudit('UI_TENANT_SWITCH_REQUEST', { actor: user?.email, severity: 'info', metadata: { tenantId } });
      if (typeof switchTenant === 'function') {
        await switchTenant(tenantId);
        await refreshUser?.();
      }
      try { localStorage.setItem('tenantId', tenantId); } catch { }
      await safeEmitAudit('UI_TENANT_SWITCH_SUCCESS', { actor: user?.email, severity: 'info', metadata: { tenantId } });
    } catch (e) {
      await safeEmitAudit('UI_TENANT_SWITCH_FAILED', { actor: user?.email, severity: 'warn', metadata: { tenantId, error: String(e) } });
      // eslint-disable-next-line no-console
      console.error('Tenant switch failed', e);
    } finally {
      setTenantSwitching(false);
    }
  }, [switchTenant, refreshUser, user]);

  // Impersonation stub for SUPER_ADMIN
  const handleImpersonate = useCallback(async (targetUserId) => {
    try {
      await safeEmitAudit('UI_IMPERSONATION_REQUEST', { actor: user?.email, severity: 'critical', metadata: { targetUserId } });
      // Placeholder: backend call required for real impersonation
      navigate(`/admin/users/${targetUserId}`);
    } catch (e) {
      await safeEmitAudit('UI_IMPERSONATION_FAILED', { actor: user?.email, severity: 'warn', metadata: { targetUserId, error: String(e) } });
    }
  }, [user, navigate]);

  // Focus first actionable element when menu opens
  useEffect(() => {
    if (menuOpen) {
      setTimeout(() => {
        const el = menuRef.current?.querySelector('button');
        el?.focus?.();
      }, 80);
    }
  }, [menuOpen]);

  // Tenant selector for SUPER_ADMIN
  const TenantSelector = useMemo(() => {
    if (user?.role !== 'SUPER_ADMIN') return null;
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <label htmlFor="header-tenant" style={{ display: 'none' }}>Active tenant</label>
        <select
          id="header-tenant"
          aria-label="Active tenant"
          defaultValue={user?.tenantId || ''}
          onChange={(e) => handleTenantSwitch(e.target.value)}
          disabled={tenantSwitching}
          style={{
            padding: '8px 10px',
            borderRadius: 8,
            border: '1px solid rgba(0,0,0,0.06)',
            background: 'transparent',
            color: '#0f172a'
          }}
        >
          {(tenants || []).map(t => <option key={t._id || t.id} value={t._id || t.id}>{t.name}</option>)}
        </select>
      </div>
    );
  }, [user, tenants, tenantSwitching, handleTenantSwitch]);

  /* -------------------------
     Render
     ------------------------- */

  return (
    <HeaderRoot role="banner" aria-label="Wilsy Global Command Bar" data-testid="app-topbar">
      <LeftGroup>
        <IconButton
          aria-label={sidebarOpen ? 'Close navigation' : 'Open navigation'}
          aria-pressed={sidebarOpen}
          onClick={handleToggleSidebar}
          title={sidebarOpen ? 'Close navigation' : 'Open navigation'}
          data-testid="topbar-toggle"
        >
          <FiMenu size={20} aria-hidden="true" />
        </IconButton>

        {showSearch && (
          <SearchBox role="search" aria-label="Global search">
            <FiSearch size={16} aria-hidden="true" />
            <SearchInput
              ref={searchRef}
              placeholder="Search cases, documents, clients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleSearchSubmit(searchQuery); }}
              aria-label="Search input"
              data-testid="topbar-search"
            />
            <SearchShortcut aria-hidden="true">K</SearchShortcut>
          </SearchBox>
        )}
      </LeftGroup>

      <RightGroup>
        <IconButton aria-label="Toggle theme" title="Toggle theme" onClick={toggleTheme} data-testid="topbar-theme">
          {isDark ? <FiSun size={18} aria-hidden="true" /> : <FiMoon size={18} aria-hidden="true" />}
        </IconButton>

        <div style={{ position: 'relative' }} ref={notifRef}>
          <IconButton
            aria-label="Notifications"
            title="Notifications"
            onClick={openNotifications}
            aria-haspopup="true"
            aria-expanded={notifOpen}
            data-testid="topbar-notifications"
          >
            <FiBell size={18} aria-hidden="true" />
          </IconButton>
          {unreadCount > 0 && <NotificationBadge aria-hidden="true" data-testid="topbar-unread" />}
        </div>

        <Divider aria-hidden="true" />

        {TenantSelector}

        <div style={{ position: 'relative' }}>
          <ProfileButton
            ref={profileRef}
            aria-haspopup="true"
            aria-expanded={menuOpen}
            onClick={toggleProfileMenu}
            title="Account menu"
            data-testid="topbar-profile-trigger"
          >
            <UserAvatar />
            <ProfileMeta aria-hidden="true">
              <div className="name">{displayName}</div>
              <div className="role">{roleLabel}</div>
            </ProfileMeta>
            <FiChevronDown size={16} aria-hidden="true" />
          </ProfileButton>

          {menuOpen && (
            <MenuPanel ref={menuRef} role="menu" aria-label="Account menu" data-testid="topbar-profile-menu">
              <div style={{ padding: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <UserAvatar />
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ fontWeight: 800 }}>{displayName}</div>
                    <div style={{ fontSize: 12, color: '#64748b' }}>{maskForUi(user?.email || '')}</div>
                    <div style={{ fontSize: 11, color: '#3b82f6', fontWeight: 800, marginTop: 6 }}>{roleLabel}</div>
                  </div>
                </div>

                <div style={{ height: 8 }} />

                <MenuItem onClick={() => { setMenuOpen(false); navigate('/profile'); safeEmitAudit('UI_NAV_PROFILE', { actor: user?.email }); }}>
                  <FiUser size={16} /> <span>Personal Profile</span>
                </MenuItem>

                <MenuItem onClick={() => { setMenuOpen(false); navigate('/settings'); safeEmitAudit('UI_NAV_SETTINGS', { actor: user?.email }); }}>
                  <FiSettings size={16} /> <span>System Settings</span>
                </MenuItem>

                <MenuItem onClick={() => { setMenuOpen(false); navigate('/admin/audits'); safeEmitAudit('UI_NAV_AUDITS', { actor: user?.email }); }}>
                  <FiShield size={16} /> <span>View Audit Trail</span>
                </MenuItem>

                <div style={{ height: 8 }} />

                {user?.role === 'SUPER_ADMIN' && (
                  <>
                    <MenuItem onClick={() => { setMenuOpen(false); navigate('/admin/health'); safeEmitAudit('UI_NAV_HEALTH', { actor: user?.email }); }}>
                      <FiSettings size={16} /> <span>System Health</span>
                    </MenuItem>

                    <MenuItem onClick={() => { setMenuOpen(false); navigate('/admin/keys'); safeEmitAudit('UI_NAV_KEYS', { actor: user?.email }); }}>
                      <FiShield size={16} /> <span>System Keys</span>
                    </MenuItem>
                  </>
                )}

                <div style={{ height: 8 }} />

                <hr style={{ border: 'none', borderTop: '1px solid rgba(0,0,0,0.04)', margin: '8px 0' }} />

                <MenuItem className="danger" onClick={() => { setMenuOpen(false); handleLogout(); }}>
                  <FiLogOut size={16} /> <span>Terminate Session</span>
                </MenuItem>
              </div>
            </MenuPanel>
          )}
        </div>
      </RightGroup>
    </HeaderRoot>
  );
}

Header.propTypes = {
  showSearch: PropTypes.bool
};

Header.defaultProps = {
  showSearch: true
};
