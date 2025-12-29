const fs = require('fs');
const path = require('path');

console.log('🛠️ OVERWRITING SIDEBAR.JS (Adding Audit + Fixing Warnings)...');

// 1. Target the specific file
const filePath = path.join(__dirname, 'components/layout/Sidebar.js');

// 2. The New "Billion-Dollar" Code
// - Uses '$collapsed' to kill warnings
// - Includes 'System Audit' menu item
const newCode = `import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { 
  FiGrid, FiFileText, FiMap, FiActivity, FiSettings, 
  FiSearch, FiMessageSquare, FiUser, FiLogOut, FiPlusCircle,
  FiChevronLeft, FiChevronRight, FiShield
} from 'react-icons/fi';
import { useDispatch } from 'react-redux';
import { logoutUser } from '../../features/auth/reducers/authSlice';

// --- STYLES (Transient Props used: $collapsed) ---

const Container = styled.div\`
  width: \${props => props.$collapsed ? '80px' : '260px'};
  background: #0f172a;
  color: #fff;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 50;
  box-shadow: 4px 0 10px rgba(0,0,0,0.1);
\`;

const LogoArea = styled.div\`
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: \${props => props.$collapsed ? 'center' : 'space-between'};
  padding: 0 \${props => props.$collapsed ? '0' : '20px'};
  border-bottom: 1px solid #1e293b;
  color: #38bdf8;
  font-weight: 800;
  letter-spacing: 1px;
  white-space: nowrap;
  overflow: hidden;
\`;

const ToggleBtn = styled.button\`
  background: #1e293b;
  border: none;
  color: #94a3b8;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover { color: #fff; background: #334155; }
\`;

const Menu = styled.div\`
  flex: 1;
  padding: 20px 10px;
  overflow-y: auto;
  overflow-x: hidden;
  &::-webkit-scrollbar { width: 0; display: none; }
\`;

const GroupTitle = styled.div\`
  font-size: 0.7rem;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
  margin: 25px 0 10px 12px;
  opacity: \${props => props.$collapsed ? 0 : 1};
  transition: opacity 0.2s;
  white-space: nowrap;
  display: \${props => props.$collapsed ? 'none' : 'block'};
\`;

const MenuItem = styled(NavLink)\`
  display: flex;
  align-items: center;
  justify-content: \${props => props.$collapsed ? 'center' : 'flex-start'};
  padding: 12px;
  color: #94a3b8;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 4px;
  font-size: 0.95rem;
  transition: all 0.2s;
  height: 48px;
  position: relative;

  &.active {
    background: #2563eb;
    color: #fff;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
  }

  &:hover:not(.active) {
    background: #1e293b;
    color: #fff;
  }

  svg {
    font-size: 1.25rem;
    min-width: 24px;
    margin-right: \${props => props.$collapsed ? '0' : '12px'};
  }

  span {
    display: \${props => props.$collapsed ? 'none' : 'block'};
    white-space: nowrap;
    opacity: \${props => props.$collapsed ? 0 : 1};
    transition: opacity 0.2s;
  }
  
  /* Tooltip logic for collapsed state */
  &:hover::after {
    content: "\${props => props.$collapsed ? props.label : ''}";
    position: absolute;
    left: 70px;
    background: #0f172a;
    color: #fff;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    display: \${props => props.$collapsed ? 'block' : 'none'};
  }
\`;

const Footer = styled.div\`
  padding: 15px;
  border-top: 1px solid #1e293b;
  display: flex;
  justify-content: center;
\`;

const LogoutBtn = styled.button\`
  background: transparent;
  border: 1px solid #334155;
  color: #cbd5e1;
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: \${props => props.$collapsed ? '0' : '10px'};
  transition: all 0.2s;
  height: 44px;

  &:hover {
    background: #ef4444;
    border-color: #ef4444;
    color: #fff;
  }
\`;

export default function Sidebar() {
  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);

  const toggle = () => setCollapsed(!collapsed);

  return (
    <Container $collapsed={collapsed}>
      <LogoArea $collapsed={collapsed}>
        {collapsed ? 'LX' : 'LEX TECH OS'}
        {!collapsed && (
            <ToggleBtn onClick={toggle}>
                <FiChevronLeft />
            </ToggleBtn>
        )}
      </LogoArea>
      
      {collapsed && (
          <div style={{display:'flex', justifyContent:'center', padding:'10px 0', borderBottom:'1px solid #1e293b'}}>
             <ToggleBtn onClick={toggle}><FiChevronRight /></ToggleBtn>
          </div>
      )}

      <Menu>
        <GroupTitle $collapsed={collapsed}>Core</GroupTitle>
        <MenuItem to="/dashboard" $collapsed={collapsed} label="Dashboard">
            <FiGrid /> <span>Dashboard</span>
        </MenuItem>
        <MenuItem to="/documents" $collapsed={collapsed} label="Documents">
            <FiFileText /> <span>Documents</span>
        </MenuItem>
        <MenuItem to="/sheriff/new-instruction" $collapsed={collapsed} label="New Instruction">
            <FiPlusCircle /> <span>New Instruction</span>
        </MenuItem>
        
        <GroupTitle $collapsed={collapsed}>Sheriff Ops</GroupTitle>
        <MenuItem to="/sheriff/tracking" $collapsed={collapsed} label="Live Tracking">
            <FiMap /> <span>Live Tracking</span>
        </MenuItem>
        <MenuItem to="/sheriff/analytics" $collapsed={collapsed} label="Analytics">
            <FiActivity /> <span>Analytics</span>
        </MenuItem>
        
        {/* --- HERE IS THE MISSING AUDIT LINK --- */}
        <MenuItem to="/sheriff/audit" $collapsed={collapsed} label="System Audit">
            <FiShield /> <span>System Audit</span>
        </MenuItem>

        <GroupTitle $collapsed={collapsed}>Tools</GroupTitle>
        <MenuItem to="/chat" $collapsed={collapsed} label="Chat">
            <FiMessageSquare /> <span>Chat</span>
        </MenuItem>
        <MenuItem to="/search" $collapsed={collapsed} label="Search">
            <FiSearch /> <span>Search</span>
        </MenuItem>
        <MenuItem to="/profile" $collapsed={collapsed} label="Profile">
            <FiUser /> <span>Profile</span>
        </MenuItem>
        <MenuItem to="/settings" $collapsed={collapsed} label="Settings">
            <FiSettings /> <span>Settings</span>
        </MenuItem>
      </Menu>

      <Footer>
        <LogoutBtn onClick={() => dispatch(logoutUser())} $collapsed={collapsed}>
          <FiLogOut /> {collapsed ? '' : 'Logout'}
        </LogoutBtn>
      </Footer>
    </Container>
  );
}
`;

fs.writeFileSync(filePath, newCode);
console.log('✅ SIDEBAR UPDATED: System Audit added & Warnings fixed.');
