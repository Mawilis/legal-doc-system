// ~/client/src/components/layout/Sidebar.jsx
import React, { useMemo, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import {
  DashboardIcon, FilesIcon, UserIcon, ChatIcon, SettingsIcon,
  AdminIcon, UsersIcon, TrackingIcon, AnalyticsIcon, GeofenceIcon,
  SheriffIcon, SearchIcon, LogoutIcon, ThemeIcon, CollapseIcon
} from '../icons/MonoIcons';

const Wrap = styled.aside`
  height: 100%;
  background: ${({ theme }) => theme.colors?.sidebarBg || '#0b1c2c'};
  color: ${({ theme }) => theme.colors?.sidebarText || '#e6eef6'};
  display: flex;
  flex-direction: column;
  border-right: 1px solid ${({ theme }) => theme.colors?.border || 'rgba(255,255,255,0.1)'};
`;

const Head = styled.div`
  display: flex; align-items: center; gap: 8px;
  padding: 12px;
  border-bottom: 1px solid ${({ theme }) => theme.colors?.border || 'rgba(255,255,255,0.1)'};
  font-weight: 600;
`;

const CollapseBtn = styled.button`
  margin-left: auto;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.25);
  color: inherit;
  border-radius: 6px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 12px;
  display: inline-flex; align-items: center; gap: 6px;
`;

const SectionLabel = styled.div`
  opacity: 0.7; font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase;
  padding: 10px 12px 4px;
`;

const Nav = styled.nav`
  flex: 1; padding: 8px; display: grid; gap: 6px;
`;

const Item = styled(NavLink)`
  display: grid; grid-template-columns: 20px 1fr;
  align-items: center; gap: 10px; color: inherit;
  text-decoration: none; padding: 10px 12px; border-radius: 8px;
  transition: background .15s ease;

  &:hover { background: rgba(255,255,255,0.06); }
  &.active { background: rgba(255,255,255,0.12); font-weight: 600; }
`;

const Tail = styled.div`
  padding: 10px 12px;
  border-top: 1px solid ${({ theme }) => theme.colors?.border || 'rgba(255,255,255,0.1)'};
  display: grid; gap: 8px;
`;
const Row = styled.div` display: flex; align-items: center; justify-content: space-between; `;

export default function Sidebar() {
  const { darkMode, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();

  // Role-based visibility (using localStorage to avoid Redux coupling here)
  const currentUser = useMemo(() => {
    try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch { return null; }
  }, []);
  const role = currentUser?.role || 'guest';
  const isAdmin = role === 'admin';
  const isSheriff = role === 'sheriff';

  const coreLinks = [
    { to: '/dashboard', label: 'Dashboard', Icon: DashboardIcon },
    { to: '/documents', label: 'Documents', Icon: FilesIcon },
    { to: '/profile',   label: 'Profile',   Icon: UserIcon },
    { to: '/chat',      label: 'Chat',      Icon: ChatIcon },
    { to: '/settings',  label: 'Settings',  Icon: SettingsIcon },
    { to: '/search',    label: 'Search',    Icon: SearchIcon },
  ];

  const adminLinks = [
    { to: '/admin',                 label: 'Admin Panel',      Icon: AdminIcon },
    { to: '/admin/users',           label: 'User Management',  Icon: UsersIcon },
    { to: '/admin/sheriff-tracking',label: 'Sheriff Tracking', Icon: TrackingIcon },
    { to: '/admin/analytics',       label: 'Analytics',        Icon: AnalyticsIcon },
    { to: '/admin/geofences',       label: 'Geofences',        Icon: GeofenceIcon },
  ];

  const sheriffLinks = [
    { to: '/sheriff/dashboard', label: 'Sheriff Dashboard', Icon: SheriffIcon },
  ];

  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login', { replace: true });
  }

  return (
    <Wrap style={{ width: collapsed ? 72 : 220 }}>
      <Head>
        <span>Navigation</span>
        <CollapseBtn onClick={() => setCollapsed(c => !c)}>
          <CollapseIcon collapsed={collapsed} size={14} />
          {collapsed ? ' ' : 'Collapse'}
        </CollapseBtn>
      </Head>

      <Nav>
        <SectionLabel>Core</SectionLabel>
        {coreLinks.map(({ to, label, Icon }) => (
          <Item key={to} to={to}>
            <Icon size={18} />
            {!collapsed && <span>{label}</span>}
          </Item>
        ))}

        {isAdmin && (
          <>
            <SectionLabel>Admin</SectionLabel>
            {adminLinks.map(({ to, label, Icon }) => (
              <Item key={to} to={to}>
                <Icon size={18} />
                {!collapsed && <span>{label}</span>}
              </Item>
            ))}
          </>
        )}

        {isSheriff && (
          <>
            <SectionLabel>Sheriff</SectionLabel>
            {sheriffLinks.map(({ to, label, Icon }) => (
              <Item key={to} to={to}>
                <Icon size={18} />
                {!collapsed && <span>{label}</span>}
              </Item>
            ))}
          </>
        )}
      </Nav>

      <Tail>
        <Row>
          {!collapsed && <span>Dark Mode</span>}
          <button
            onClick={toggleTheme}
            aria-label="toggle dark mode"
            style={{
              background: 'transparent',
              color: 'inherit',
              border: '1px solid rgba(255,255,255,0.25)',
              borderRadius: 8,
              padding: '6px 8px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            <ThemeIcon size={16} />
            {!collapsed && (darkMode ? 'On' : 'Off')}
          </button>
        </Row>
        <button
          onClick={logout}
          style={{
            background: 'transparent',
            color: 'inherit',
            border: '1px solid rgba(255,255,255,0.25)',
            borderRadius: 8,
            padding: '8px 10px',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          <LogoutIcon size={16} />
          {!collapsed && 'Logout'}
        </button>
      </Tail>
    </Wrap>
  );
}
