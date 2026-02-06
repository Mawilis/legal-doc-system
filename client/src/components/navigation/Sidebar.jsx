/**
 * File: client/src/components/layout/Sidebar.jsx
 * STATUS: PRODUCTION | EPITOME | NAVIGATION ENGINE
 * VERSION: 2026-01-10
 *
 * PURPOSE
 * - Role-aware, accessible, resilient navigation sidebar for Wilsy OS.
 * - Consumes the layout context (useLayout) exported by MainLayout.
 * - Emits best-effort audit events for navigation and tenant actions.
 * - Designed for a billion-dollar multi-tenant SaaS: secure, auditable, and extensible.
 *
 * KEY FEATURES
 * - Declarative NAV_CONFIG with role scoping and feature flags.
 * - Keyboard-first navigation and focus management.
 * - Mobile-first responsive behavior with slide-in panel.
 * - Durable audit emission (best-effort) via AuditService or AuthUtils fallback.
 * - Test hooks and data-testid attributes for deterministic tests.
 * - Graceful degradation when services are missing.
 *
 * INTEGRATION CONTRACTS
 * - Expects `useLayout()` from MainLayout context in the same folder:
 *     import { useLayout } from '../layout/MainLayout';
 * - Expects `useAuthStore()` to expose: { user, tenants, logout, switchTenant, refreshUser }
 * - Optional: AuditService at client/src/features/auth/services/AuditService.js
 * - Optional: AuthUtils.AuditService at client/src/features/auth/utils/authUtils.js
 *
 * SECURITY NOTES
 * - UI gating only: backend must enforce RBAC for all admin routes.
 * - Audit payloads must not contain raw PII; AuditService should mask actor fields.
 *
 * AUTHOR: Chief Architect (Wilson Khanyezi)
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import styled, { css } from 'styled-components';
import { NavLink, useLocation } from 'react-router-dom';
import {
  FiHome,
  FiFileText,
  FiActivity,
  FiSettings,
  FiShield,
  FiLogOut,
  FiBriefcase,
  FiUsers,
  FiChevronLeft,
  FiChevronRight,
  FiSearch
} from 'react-icons/fi';

import { useLayout } from '../layout/MainLayout';
import useAuthStore from '../../store/authStore';
import AuthUtils from '../../features/auth/utils/authUtils';
import AuditService from '../../features/auth/services/AuditService';

/* --------------------------------------------------------------------------
   Styled primitives
   -------------------------------------------------------------------------- */

const Aside = styled.aside`
  --sidebar-width: 280px;
  --sidebar-collapsed: 72px;
  background: var(--sidebar-bg, #0f172a);
  color: var(--sidebar-foreground, #f8fafc);
  display: flex;
  flex-direction: column;
  transition: width 220ms cubic-bezier(0.4, 0, 0.2, 1), transform 220ms ease;
  width: ${p => (p.$open ? 'var(--sidebar-width)' : 'var(--sidebar-collapsed)')};
  overflow: hidden;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 60;
  border-right: 1px solid rgba(255,255,255,0.03);

  @media (max-width: 900px) {
    position: fixed;
    left: 0;
    top: 0;
    transform: translateX(${p => (p.$open ? '0' : '-100%')});
    width: var(--sidebar-width);
    box-shadow: 0 20px 60px rgba(2,6,23,0.6);
  }
`;

const Brand = styled.div`
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 1.25rem;
  font-weight: 900;
  font-size: 1rem;
  letter-spacing: -0.2px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  gap: 12px;
  white-space: nowrap;

  .logo {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: linear-gradient(180deg,#020617,#07102a);
    display:flex; align-items:center; justify-content:center;
    color: #fff; font-weight:900; font-size:1.05rem;
    box-shadow: 0 6px 18px rgba(37,99,235,0.12);
  }

  .title {
    opacity: ${p => (p.$open ? 1 : 0)};
    transform: translateX(${p => (p.$open ? '0' : '-6px')});
    transition: opacity 180ms ease, transform 180ms ease;
  }
`;

const Nav = styled.nav`
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
`;

const itemBase = css`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  color: #94a3b8;
  text-decoration: none;
  border-radius: 10px;
  font-weight: 600;
  transition: background 140ms ease, color 140ms ease, transform 120ms ease;
  white-space: nowrap;

  &:hover, &:focus {
    background: rgba(255,255,255,0.04);
    color: #fff;
    transform: translateX(4px);
    outline: none;
  }

  &.active {
    background: linear-gradient(180deg,#2563eb,#1e40af);
    color: #fff;
    box-shadow: 0 8px 20px rgba(37,99,235,0.18);
  }

  .icon {
    min-width: 20px;
    display:flex; align-items:center; justify-content:center;
    font-size: 1.15rem;
  }

  .label {
    opacity: ${p => (p.$open ? 1 : 0)};
    transition: opacity 160ms ease;
  }
`;

const Item = styled(NavLink)`
  ${itemBase}
`;

const SectionLabel = styled.div`
  padding: 6px 12px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1px;
  display: ${p => (p.$open ? 'block' : 'none')};
`;

const SectionDivider = styled.div`
  height: 1px;
  background: rgba(255,255,255,0.04);
  margin: 8px 6px;
  border-radius: 2px;
`;

const Footer = styled.footer`
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.04);
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: ${p => (p.$open ? 'space-between' : 'center')};

  .user-info {
    display: ${p => (p.$open ? 'flex' : 'none')};
    align-items: center;
    gap: 10px;
    color: #cbd5e1;
    font-size: 0.9rem;
  }

  .collapse-btn {
    background: transparent;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    padding: 8px;
    border-radius: 8px;
    &:hover { background: rgba(255,255,255,0.02); color: #fff; }
  }
`;

/* --------------------------------------------------------------------------
   NAV CONFIG (declarative)
   - Add items here; allowedRoles controls visibility; '*' means all authenticated.
   -------------------------------------------------------------------------- */

const NAV_CONFIG = [
  {
    section: 'Workspace',
    items: [
      { key: 'dashboard', label: 'Overview', to: '/dashboard', Icon: FiHome, allowedRoles: ['*'] },
      { key: 'documents', label: 'Documents', to: '/documents', Icon: FiFileText, allowedRoles: ['*'] },
      { key: 'sheriff', label: 'Sheriff Logistics', to: '/sheriff', Icon: FiActivity, allowedRoles: ['*'] }
    ]
  },
  {
    section: 'Practice & Org',
    items: [
      { key: 'organization', label: 'Organization', to: '/organization', Icon: FiBriefcase, allowedRoles: ['TENANT_ADMIN', 'SUPER_ADMIN'] },
      { key: 'users', label: 'Users', to: '/admin/users', Icon: FiUsers, allowedRoles: ['TENANT_ADMIN', 'SUPER_ADMIN'] }
    ]
  },
  {
    section: 'Administration',
    items: [
      { key: 'console', label: 'God Mode', to: '/admin/console', Icon: FiShield, allowedRoles: ['SUPER_ADMIN'] },
      { key: 'tenants', label: 'Tenants', to: '/superadmin/tenants', Icon: FiBriefcase, allowedRoles: ['SUPER_ADMIN'] },
      { key: 'system', label: 'System Settings', to: '/admin/health', Icon: FiSettings, allowedRoles: ['SUPER_ADMIN'] }
    ]
  }
];

/* --------------------------------------------------------------------------
   Helpers
   -------------------------------------------------------------------------- */

/**
 * checkAccess - UI-level role check
 * - Always return false for unauthenticated users.
 * - This is UI gating only; backend must enforce real RBAC.
 */
function checkAccess(user, allowedRoles = []) {
  if (!user) return false;
  if (!Array.isArray(allowedRoles) || allowedRoles.length === 0) return false;
  if (allowedRoles.includes('*')) return true;
  const role = String(user.role || '').toUpperCase();
  return allowedRoles.map(r => String(r).toUpperCase().trim()).includes(role);
}

/**
 * emitNavAudit - best-effort audit emitter for navigation events
 * - Uses AuditService.log if available, falls back to AuthUtils.AuditService, then console in dev.
 * - Always non-blocking and resilient.
 */
async function emitNavAudit(req) {
  try {
    if (AuditService && typeof AuditService.log === 'function') {
      await AuditService.log('UI_NAV_CLICK', req);
      return;
    }
    if (AuthUtils && AuthUtils.AuditService && typeof AuthUtils.AuditService.log === 'function') {
      await AuthUtils.AuditService.log('UI_NAV_CLICK', req);
      return;
    }
    if (process.env.NODE_ENV !== 'production') {
      // eslint-disable-next-line no-console
      console.debug('[AUDIT] NAV_CLICK', req);
    }
  } catch (e) {
    // swallow to avoid UI disruption
    // eslint-disable-next-line no-console
    console.warn('[AUDIT] NAV_CLICK failed', e);
  }
}

/* --------------------------------------------------------------------------
   Component
   -------------------------------------------------------------------------- */

export default function Sidebar() {
  // Layout context (MainLayout)
  const { sidebarOpen, setSidebarOpen, isMobile } = useLayout();

  // Auth store
  const { user, tenants = [], logout, switchTenant, refreshUser } = useAuthStore();

  const location = useLocation();
  const isSuper = user?.role === 'SUPER_ADMIN';
  const asideRef = useRef(null);

  // Focus index for keyboard navigation
  const [focusedIndex, setFocusedIndex] = useState(-1);

  /* Keyboard: allow Esc to close on mobile */
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape' && isMobile && sidebarOpen) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isMobile, sidebarOpen, setSidebarOpen]);

  /* Close sidebar on route change for mobile (configurable in MainLayout) */
  useEffect(() => {
    if (isMobile && sidebarOpen) {
      setSidebarOpen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  const toggleCollapse = useCallback(() => {
    setSidebarOpen(!sidebarOpen);
    emitNavAudit({ actor: user?.email, action: 'toggle_sidebar', metadata: { open: !sidebarOpen } });
  }, [sidebarOpen, setSidebarOpen, user]);

  /* Memoize visible nav to avoid re-computation */
  const visibleNav = useMemo(() => {
    return NAV_CONFIG.map(section => {
      const items = section.items.filter(it => checkAccess(user, it.allowedRoles));
      return { ...section, items };
    }).filter(s => s.items.length > 0);
  }, [user]);

  /* Build a flat list of nav items for keyboard navigation */
  const flatNav = useMemo(() => {
    const arr = [];
    visibleNav.forEach(section => {
      section.items.forEach(item => arr.push(item));
    });
    // Add tenant and superadmin quick links if visible
    if (isSuper || user?.role === 'TENANT_ADMIN') {
      arr.push({ key: 'organization', label: 'Organization', to: '/organization' });
    }
    if (isSuper) {
      arr.push({ key: 'console', label: 'God Mode', to: '/admin/console' });
      arr.push({ key: 'tenants', label: 'Tenants', to: '/superadmin/tenants' });
    }
    return arr;
  }, [visibleNav, isSuper, user]);

  /* Keyboard navigation: ArrowUp/ArrowDown to move focus */
  useEffect(() => {
    const onKey = (e) => {
      if (document.activeElement && asideRef.current && asideRef.current.contains(document.activeElement)) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setFocusedIndex(i => Math.min(i + 1, flatNav.length - 1));
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setFocusedIndex(i => Math.max(i - 1, 0));
        }
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [flatNav.length]);

  /* When focusedIndex changes, focus the corresponding nav element */
  useEffect(() => {
    if (focusedIndex < 0) return;
    const el = asideRef.current?.querySelector(`[data-nav-index="${focusedIndex}"]`);
    el?.focus?.();
  }, [focusedIndex]);

  /* Tenant switch handler (SUPER_ADMIN only) */
  const handleTenantSwitch = useCallback(async (tenantId) => {
    if (!tenantId) return;
    try {
      await emitNavAudit({ actor: user?.email, action: 'tenant_switch_request', metadata: { tenantId } });
      if (typeof switchTenant === 'function') {
        await switchTenant(tenantId);
        await refreshUser?.();
      }
      try { localStorage.setItem('tenantId', tenantId); } catch { }
      await emitNavAudit({ actor: user?.email, action: 'tenant_switch_success', metadata: { tenantId } });
    } catch (e) {
      await emitNavAudit({ actor: user?.email, action: 'tenant_switch_failed', metadata: { tenantId, error: String(e) } });
      // eslint-disable-next-line no-console
      console.error('Tenant switch failed', e);
    }
  }, [switchTenant, refreshUser, user]);

  /* Render helpers */
  const renderSection = (section) => {
    return (
      <React.Fragment key={section.section}>
        <SectionLabel $open={sidebarOpen}>{section.section}</SectionLabel>
        {section.items.map((item) => {
          const index = flatNav.findIndex(n => n.key === item.key);
          return (
            <Item
              key={item.key}
              to={item.to}
              $open={sidebarOpen}
              className={({ isActive }) => (isActive ? 'active' : '')}
              onClick={() => emitNavAudit({ actor: user?.email, action: 'navigate', metadata: { to: item.to, label: item.label } })}
              data-testid={`nav-${item.key}`}
              tabIndex={0}
              aria-current={location.pathname === item.to ? 'page' : undefined}
              data-nav-index={index}
            >
              <span className="icon" aria-hidden="true"><item.Icon /></span>
              <span className="label">{item.label}</span>
            </Item>
          );
        })}
      </React.Fragment>
    );
  };

  /* Footer user info */
  const FooterUser = () => (
    <div className="user-info" aria-hidden={!sidebarOpen}>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontWeight: 800 }}>{user?.firstName || user?.name || 'Chief Architect'}</div>
        <div style={{ fontSize: 12, color: '#94a3b8' }}>{(user?.role || 'GUEST').toUpperCase()}</div>
      </div>
    </div>
  );

  /* Accessibility: tooltip text for collapsed labels (used by tests or future enhancements) */
  const Tooltip = ({ text }) => (
    <span style={{
      position: 'absolute',
      left: '100%',
      marginLeft: 8,
      background: '#111827',
      color: '#fff',
      padding: '6px 8px',
      borderRadius: 6,
      fontSize: 12,
      whiteSpace: 'nowrap',
      boxShadow: '0 6px 20px rgba(2,6,23,0.6)'
    }}>
      {text}
    </span>
  );

  /* --------------------------------------------------------------------------
     Render
     -------------------------------------------------------------------------- */

  return (
    <Aside $open={sidebarOpen} aria-label="Primary navigation" ref={asideRef} data-testid="sidebar-root">
      <Brand $open={sidebarOpen} aria-hidden={!sidebarOpen}>
        <div className="logo" aria-hidden="true">W</div>
        <div className="title">{sidebarOpen ? 'WILSY OS' : null}</div>
      </Brand>

      <Nav role="navigation" aria-label="Main">
        {visibleNav.map(renderSection)}

        {/* Tenant admin quick link (explicit) */}
        {(isSuper || user?.role === 'TENANT_ADMIN') && (
          <>
            <SectionDivider />
            <Item
              to="/organization"
              $open={sidebarOpen}
              onClick={() => emitNavAudit({ actor: user?.email, action: 'navigate', metadata: { to: '/organization', label: 'Organization' } })}
              data-testid="nav-organization"
              data-nav-index={flatNav.findIndex(n => n.key === 'organization')}
            >
              <span className="icon"><FiBriefcase /></span>
              <span className="label">Organization</span>
            </Item>
          </>
        )}

        {/* Super admin exclusive area */}
        {isSuper && (
          <>
            <SectionDivider />
            <Item
              to="/admin/console"
              $open={sidebarOpen}
              onClick={() => emitNavAudit({ actor: user?.email, action: 'navigate', metadata: { to: '/admin/console', label: 'God Mode' } })}
              data-testid="nav-console"
              data-nav-index={flatNav.findIndex(n => n.key === 'console')}
            >
              <span className="icon"><FiShield /></span>
              <span className="label">God Mode</span>
            </Item>

            <Item
              to="/superadmin/tenants"
              $open={sidebarOpen}
              onClick={() => emitNavAudit({ actor: user?.email, action: 'navigate', metadata: { to: '/superadmin/tenants', label: 'Tenants' } })}
              data-testid="nav-tenants"
              data-nav-index={flatNav.findIndex(n => n.key === 'tenants')}
            >
              <span className="icon"><FiUsers /></span>
              <span className="label">Tenants</span>
            </Item>
          </>
        )}
      </Nav>

      <Footer $open={sidebarOpen}>
        <FooterUser />

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Collapse/Expand button */}
          <button
            className="collapse-btn"
            onClick={toggleCollapse}
            aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            title={sidebarOpen ? 'Collapse' : 'Expand'}
            data-testid="sidebar-toggle"
          >
            {sidebarOpen ? <FiChevronLeft /> : <FiChevronRight />}
          </button>

          {/* Sign out quick link (visible icon always, label only when open) */}
          <NavLink
            to="/logout"
            style={{ color: '#ef4444', display: 'inline-flex', alignItems: 'center', gap: 8, textDecoration: 'none' }}
            onClick={() => emitNavAudit({ actor: user?.email, action: 'logout_click', metadata: {} })}
            data-testid="nav-logout"
            aria-label="Sign out"
          >
            <FiLogOut />
            {sidebarOpen && <span style={{ color: '#ef4444', fontWeight: 700 }}>Sign Out</span>}
          </NavLink>
        </div>
      </Footer>
    </Aside>
  );
}

/* End of Sidebar.jsx */
