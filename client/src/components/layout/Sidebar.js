/**
 * Copyright (c) 2025 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * Brand: Wilsy - Touching Lives.
 */
import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { 
  FiGrid, FiFileText, FiPlusCircle, FiMap, FiShield, 
  FiSettings, FiLogOut, FiMessageSquare, FiSearch, 
  FiUser, FiBarChart2 
} from 'react-icons/fi';
import { useDispatch } from 'react-redux';
import { logoutUser } from '../../features/auth/reducers/authSlice';

const Container = styled.div`
  width: 260px;
  background: #0b1120;
  color: #fff;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: fixed;
  z-index: 50;
`;

const LogoArea = styled.div`
  padding: 30px 20px;
  border-bottom: 1px solid #1e293b;
  text-align: center;
  .brand-name { 
    font-size: 1.8rem; 
    font-weight: 900; 
    color: #38bdf8; 
    letter-spacing: 2px;
    text-transform: lowercase;
    margin-bottom: 4px;
  }
  .slogan { 
    font-size: 0.65rem; 
    color: #94a3b8; 
    text-transform: uppercase; 
    letter-spacing: 1.5px;
    font-weight: 600;
  }
`;

const NavSection = styled.div`
  margin-top: 25px;
  padding: 0 15px;
`;

const SectionLabel = styled.div`
  font-size: 0.7rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  padding-left: 12px;
`;

const MenuItem = styled(NavLink)`
  display: flex;
  align-items: center;
  padding: 12px 15px;
  color: #94a3b8;
  text-decoration: none;
  border-radius: 10px;
  margin-bottom: 5px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(56, 189, 248, 0.05);
    color: #38bdf8;
  }

  &.active {
    background: #2563eb;
    color: #fff;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  }

  svg { margin-right: 15px; font-size: 1.1rem; }
`;

export default function Sidebar() {
  const dispatch = useDispatch();

  return (
    <Container>
      <LogoArea>
        <div className="brand-name">wilsy</div>
        <div className="slogan">Touching Lives</div>
      </LogoArea>

      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '20px' }}>
        {/* CORE SECTION */}
        <NavSection>
          <SectionLabel>Core</SectionLabel>
          <MenuItem to="/dashboard"><FiGrid /> Dashboard</MenuItem>
          <MenuItem to="/documents"><FiFileText /> Documents</MenuItem>
          <MenuItem to="/new-instruction"><FiPlusCircle /> New Instruction</MenuItem>
        </NavSection>

        {/* SHERIFF OPS SECTION */}
        <NavSection>
          <SectionLabel>Sheriff Ops</SectionLabel>
          <MenuItem to="/live-tracking"><FiMap /> Live Tracking</MenuItem>
          <MenuItem to="/analytics"><FiBarChart2 /> Analytics</MenuItem>
          <MenuItem to="/trust-ledger"><FiShield /> Trust Ledger</MenuItem>
        </NavSection>

        {/* TOOLS SECTION */}
        <NavSection>
          <SectionLabel>Tools</SectionLabel>
          <MenuItem to="/chat"><FiMessageSquare /> Chat</MenuItem>
          <MenuItem to="/search"><FiSearch /> Search</MenuItem>
          <MenuItem to="/profile"><FiUser /> Profile</MenuItem>
          <MenuItem to="/settings"><FiSettings /> Settings</MenuItem>
        </NavSection>
      </div>

      <div style={{ padding: '15px', borderTop: '1px solid #1e293b' }}>
        <MenuItem as="button" onClick={() => dispatch(logoutUser())} style={{ background: 'none', border: 'none', width: '100%', cursor: 'pointer' }}>
          <FiLogOut /> Logout
        </MenuItem>
      </div>
    </Container>
  );
}
