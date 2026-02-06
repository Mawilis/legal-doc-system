/**
 * File: client/src/features/admin/pages/AdminPanel.jsx
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Security Gatekeeper
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The "Bouncer" for the Admin Module.
 * - Handles Privilege Verification and Unauthorized Access redirection.
 * - Wraps the actual AdminDashboard logic.
 * -----------------------------------------------------------------------------
 */

import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import styled, { keyframes } from 'styled-components';
import { FiShield, FiLock, FiArrowLeft } from 'react-icons/fi';
import AdminDashboard from './AdminDashboard';

// --- ANIMATIONS ---
const pulse = keyframes`0% { transform: scale(0.95); opacity: 0.5; } 50% { transform: scale(1); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.5; }`;
const shake = keyframes`10%, 90% { transform: translate3d(-1px, 0, 0); } 20%, 80% { transform: translate3d(2px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-4px, 0, 0); } 40%, 60% { transform: translate3d(4px, 0, 0); }`;

// --- STYLED COMPONENTS ---

const GateContainer = styled.div`
  min-height: 100vh;
  background: #F8FAFC;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', sans-serif;
`;

const AccessCard = styled.div`
  background: white;
  width: 100%;
  max-width: 480px;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  text-align: center;
  border: 1px solid #E2E8F0;
  
  &.denied {
    border-top: 6px solid #EF4444;
    animation: ${shake} 0.82s cubic-bezier(.36,.07,.19,.97) both;
  }
`;

const IconWrapper = styled.div`
  width: 80px; height: 80px; margin: 0 auto 24px;
  background: ${props => props.$denied ? '#FEF2F2' : '#EFF6FF'};
  color: ${props => props.$denied ? '#DC2626' : '#3B82F6'};
  border-radius: 20px;
  display: grid; place-items: center;
  font-size: 2.5rem;
  
  &.loading { animation: ${pulse} 2s infinite; }
`;

const Title = styled.h2`
  font-size: 1.5rem; font-weight: 800; color: #0F172A; margin-bottom: 12px;
`;

const Message = styled.p`
  color: #64748B; font-size: 1rem; line-height: 1.6; margin-bottom: 32px;
`;

const Button = styled.button`
  background: #0F172A; color: white;
  border: none; padding: 14px 24px; border-radius: 12px;
  font-size: 1rem; font-weight: 600; cursor: pointer;
  display: inline-flex; align-items: center; gap: 8px;
  transition: transform 0.2s;
  
  &:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
`;

export default function AdminPanel() {
  const navigate = useNavigate();
  const { user, isLoading } = useSelector((state) => state.auth || {});
  const [verifying, setVerifying] = useState(true);

  // Artificial delay to show the "Security Check" animation (Adds polish)
  useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => setVerifying(false), 800);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  // 1. VERIFICATION STATE (The "Pulse")
  if (isLoading || verifying) {
    return (
      <GateContainer>
        <AccessCard>
          <IconWrapper className="loading">
            <FiShield />
          </IconWrapper>
          <Title>Verifying Credentials</Title>
          <Message>Establishing secure connection to Admin Command...</Message>
        </AccessCard>
      </GateContainer>
    );
  }

  // 2. SECURITY CHECK (The Gate)
  const isAuthorized = user?.role === 'admin' || user?.role === 'super_admin';

  if (!isAuthorized) {
    return (
      <GateContainer>
        <AccessCard className="denied">
          <IconWrapper $denied>
            <FiLock />
          </IconWrapper>
          <Title>Access Restricted</Title>
          <Message>
            Your clearance level ({user?.role?.toUpperCase() || 'UNKNOWN'}) does not permit access to the System Command Center.
            This attempt has been logged.
          </Message>
          <Button onClick={() => navigate('/dashboard')}>
            <FiArrowLeft /> Return to Safety
          </Button>
        </AccessCard>
      </GateContainer>
    );
  }

  // 3. ACCESS GRANTED (Render the God Mode Dashboard)
  return <AdminDashboard />;
}