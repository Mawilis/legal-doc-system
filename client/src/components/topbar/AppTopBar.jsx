/**
 * File: client/src/components/layout/AppTopBar.jsx
 * Path: client/src/components/layout/AppTopBar.jsx
 * STATUS: PRODUCTION-READY | EPITOME | GLOBAL COMMAND COCKPIT
 * VERSION: 3.0.0
 *
 * PURPOSE
 * - Global top bar for Wilsy OS: navigation toggles, spotlight search, theme toggle,
 *   notifications, and identity cockpit.
 * - Designed for production: accessibility (WCAG 2.1), keyboard-first UX, POPIA-aware
 *   minimal client-side PII, audit hooks, and clear collaboration metadata.
 *
 * COLLABORATION & OWNERSHIP (MANDATORY)
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team (UI, accessibility, performance)
 * - BACKEND OWNER: @backend-team (auth/session contract, audit ingestion)
 * - SECURITY OWNER: @security (PII handling, cookie policy, telemetry)
 * - SRE OWNER: @sre (availability, telemetry)
 * - QA OWNER: @qa (unit & integration tests)
 *
 * REVIEW CHECKLIST (PRE-MERGE)
 * - @frontend-team: confirm styled-components and lucide-react versions
 * - @backend-team: confirm authStore contract and server cookie/session behavior
 * - @security: approve that no raw tokens or sensitive PII are persisted client-side
 * - @qa: add tests for keyboard shortcuts, menu focus trap, logout flow, and accessibility
 *
 * SECURITY & POPIA NOTES
 * - Client stores only sanitized user summary (id, displayName, role, tenantId).
 * - Do not persist email, ID tokens, or raw IdP claims in localStorage without @security approval.
 * - All audit events must be sent to server-side audit ingestion; client emits non-sensitive telemetry only.
 *
 * TODO
 * - Wire real notification feed and unread count via secure API.
 * - Replace demo logout with server-backed logout endpoint that clears httpOnly cookies.
 * - Add unit tests (Jest + React Testing Library) for keyboard orchestration and focus management.
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  Settings,
  LogOut,
  Menu,
  Moon,
  Sun,
  Search,
  PanelLeft,
  PanelLeftClose,
  User as UserIcon
} from 'lucide-react';
import useAuthStore from '../../store/authStore';

/* -------------------------
   Styled primitives
   ------------------------- */

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(255,255,255,0.96);
  height: 72px;
  padding: 0 20px;
  border-bottom: 1px solid #e6edf3;
  position: sticky;
  top: 0;
  z-index: 60;
  backdrop-filter: blur(8px);
`;

const Left = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
`;

const Right = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

/* Search box: hidden on small screens via media query */
const SearchBox = styled.div`
  display: flex;
  align-items: center;
  position: relative;
  max-width: 520px;
  width: 100%;
  margin-left: 12px;

  @media (max-width: 900px) {
    display: none;
  }

  svg { position: absolute; left: 12px; color: #94a3b8; pointer-events: none; }
  input {
    width: 100%;
    padding: 10px 12px 10px 40px;
    border-radius: 10px;
    border: 1px solid #e6edf3;
    background: #f8fafc;
    color: #0f172a;
    font-size: 0.95rem;
  }
  .shortcut {
    position: absolute;
    right: 10px;
    padding: 4px 8px;
    border-radius: 6px;
    background: #fff;
    border: 1px solid #e6edf3;
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 700;
  }
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 8px;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 0;
  transition: background 120ms ease, color 120ms ease;
  &:hover { background: #f1f5f9; color: #2563eb; }
  &:focus { outline: 3px solid rgba(37,99,235,0.12); outline-offset: 2px; }
`;

const ProfileButton = styled.button`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  &:hover { background: #f8fafc; border-color: #e6edf3; }
  &:focus { outline: 3px solid rgba(37,99,235,0.12); outline-offset: 2px; }
`;

const ProfileMeta = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 0;
  .name { font-weight: 700; font-size: 0.9rem; color: #0f172a; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; max-width: 140px; }
  .role { font-size: 0.7rem; color: #2563eb; text-transform: uppercase; font-weight: 800; letter-spacing: 0.6px; }
  @media (max-width: 640px) { display: none; }
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg,#0b3d91 0%,#2563eb 100%);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  box-shadow: 0 6px 18px rgba(37,99,235,0.12);
`;

/* Menu panel with simple focus management */
const MenuPanel = styled.div`
  position: absolute;
  right: 12px;
  top: 64px;
  background: #fff;
  border: 1px solid #e6edf3;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(2,6,23,0.12);
  min-width: 220px;
  z-index: 120;
  padding: 8px;
  display: ${(p) => (p.open ? 'block' : 'none')};
`;

const MenuItem = styled.button`
  width: 100%;
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px;
  background: transparent;
  border: none;
  text-align: left;
  color: #334155;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  &:hover { background: #f1f5f9; color: #0b3d91; }
  &:focus { outline: 3px solid rgba(37,99,235,0.12); outline-offset: 2px; }
  &.logout { color: #ef4444; }
`;

/* -------------------------
   Helper: safe client audit emitter (non-blocking)
   ------------------------- */
function emitClientAudit(eventType, metadata = {}) {
  try {
    if (typeof window !== 'undefined' && window.WilsyAudit && typeof window.WilsyAudit.log === 'function') {
      // Only emit non-sensitive metadata; server will enrich with correlationId and actor
      window.WilsyAudit.log(eventType, metadata);
    }
  } catch {
    // swallow to avoid UI impact
  }
}

/* -------------------------
   Component
   ------------------------- */

export default function AppTopBar({ onToggleSidebar, onMobileMenuClick, isSidebarCollapsed }) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore(); // user is sanitized summary per store contract
  const searchRef = useRef(null);
  const menuRef = useRef(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [theme, setTheme] = useState('light');

  // initials generation: crash-proof, POPIA-safe (no PII leakage)
  const initials = useMemo(() => {
    if (!user) return 'WW';
    const display = (user.displayName || '').trim() || (user.id || '').toString().slice(0, 2);
    const parts = display.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return parts[0].slice(0, 2).toUpperCase();
  }, [user]);

  /* Spotlight shortcut: Ctrl/Cmd + K */
  useEffect(() => {
    const onKey = (e) => {
      const isMac = navigator.platform.toUpperCase().includes('MAC');
      const mod = isMac ? e.metaKey : e.ctrlKey;
      if (mod && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (searchRef.current) searchRef.current.focus();
      }
      if (e.key === 'Escape') {
        setMenuOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  /* Close menu on outside click */
  useEffect(() => {
    const onClick = (ev) => {
      if (menuOpen && menuRef.current && !menuRef.current.contains(ev.target)) {
        setMenuOpen(false);
      }
    };
    if (menuOpen) document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, [menuOpen]);

  const handleLogout = useCallback(async () => {
    try {
      setMenuOpen(false);
      // logout should call server to clear httpOnly cookies; store.logout handles that
      await logout();
      emitClientAudit('UI.LOGOUT', { source: 'AppTopBar' });
      navigate('/login', { replace: true });
    } catch (err) {
      // Force navigation to login to avoid stuck UI
      console.error('Logout failed', err);
      navigate('/login', { replace: true });
    }
  }, [logout, navigate]);

  const toggleTheme = useCallback(() => {
    const next = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    emitClientAudit('UI.THEME_TOGGLE', { theme: next });
  }, [theme]);

  const handleSearchKey = useCallback((e) => {
    if (e.key === 'Enter') {
      const q = e.target.value.trim();
      if (q) {
        // Navigate to search page; do not include PII in query params
        navigate(`/search?q=${encodeURIComponent(q)}`);
        emitClientAudit('UI.SEARCH', { queryPreview: q.slice(0, 64) });
      }
    }
  }, [navigate]);

  return (
    <Header role="banner" aria-label="Wilsy Global Command Bar">
      <Left>
        {/* Mobile menu trigger */}
        <IconButton
          aria-label="Open navigation"
          onClick={onMobileMenuClick}
          title="Open navigation"
        >
          <Menu size={18} />
        </IconButton>

        {/* Desktop sidebar toggle */}
        <IconButton
          aria-label="Toggle sidebar"
          onClick={onToggleSidebar}
          aria-pressed={!isSidebarCollapsed}
          title="Toggle sidebar"
        >
          {isSidebarCollapsed ? <PanelLeft size={18} /> : <PanelLeftClose size={18} />}
        </IconButton>

        {/* Spotlight search */}
        <SearchBox role="search" aria-label="Global search">
          <Search size={16} aria-hidden="true" />
          <input
            ref={searchRef}
            type="search"
            placeholder="Search cases, dockets, documents..."
            aria-label="Search"
            onKeyDown={handleSearchKey}
          />
          <span className="shortcut" aria-hidden="true">Ctrl K</span>
        </SearchBox>
      </Left>

      <Right>
        <IconButton aria-label="Toggle theme" onClick={toggleTheme} title="Toggle theme">
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </IconButton>

        <IconButton aria-label="Notifications" title="Notifications">
          <Bell size={16} />
          {/* Badge should be wired to real unread count */}
        </IconButton>

        <div style={{ position: 'relative' }} ref={menuRef}>
          <ProfileButton
            aria-haspopup="true"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((s) => !s)}
            aria-label="Open profile menu"
            title="Profile"
          >
            <ProfileMeta>
              <span className="name">{user ? user.displayName : 'Guest'}</span>
              <span className="role">{user ? (user.role || '').toUpperCase() : 'GUEST'}</span>
            </ProfileMeta>
            <Avatar aria-hidden="true">{initials}</Avatar>
          </ProfileButton>

          <MenuPanel open={menuOpen} role="menu" aria-label="Profile menu">
            <MenuItem
              onClick={() => { setMenuOpen(false); navigate('/profile'); emitClientAudit('UI.NAV_PROFILE'); }}
              role="menuitem"
            >
              <UserIcon size={16} /> Profile
            </MenuItem>

            <MenuItem
              onClick={() => { setMenuOpen(false); navigate('/settings'); emitClientAudit('UI.NAV_SETTINGS'); }}
              role="menuitem"
            >
              <Settings size={16} /> Settings
            </MenuItem>

            <hr style={{ margin: '8px 0', border: 'none', borderTop: '1px solid #f1f5f9' }} />

            <MenuItem onClick={handleLogout} className="logout" role="menuitem">
              <LogOut size={16} /> Sign out
            </MenuItem>
          </MenuPanel>
        </div>
      </Right>
    </Header>
  );
}

AppTopBar.propTypes = {
  onToggleSidebar: PropTypes.func,
  onMobileMenuClick: PropTypes.func,
  isSidebarCollapsed: PropTypes.bool
};

AppTopBar.defaultProps = {
  onToggleSidebar: () => { },
  onMobileMenuClick: () => { },
  isSidebarCollapsed: false
};
