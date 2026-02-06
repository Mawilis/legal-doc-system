/*
 * File: src/features/auth/pages/AccessDenied.jsx
 * STATUS: EPITOME | SECURITY LOCKOUT
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The "Iron Gate" for unauthorized access attempts. 
 * Replaces friendly 404s with an authoritative Security Incident Report to 
 * deter social engineering and traversal attacks.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - SECURITY: Generates a unique 'Incident ID' to psychologically compel compliance.
 * - UX: Uses 'Slate 900' Dark Mode to visually distinguish "Safe Zone" from "Restricted Zone".
 * - ARCHITECTURE: Integrated with Zustand (authStore) for instant session termination.
 * -----------------------------------------------------------------------------
 */

'use client';

import React, { useMemo } from 'react';
import styled, { keyframes } from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, Lock, LogOut } from 'lucide-react';

// --- BRAIN: Zustand Store ---
import useAuthStore from '../../../store/authStore';

// --- ANIMATIONS ---
const pulseRed = keyframes`
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
`;

// --- STYLED ARCHITECTURE ---

const Container = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0F172A; /* Slate 900 - The Color of Authority */
  color: white;
  text-align: center;
  font-family: 'Inter', sans-serif;
`;

const IconWrapper = styled.div`
  background: #450A0A;
  color: #EF4444;
  width: 96px; height: 96px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 32px;
  border: 1px solid #7F1D1D;
  animation: ${pulseRed} 2s infinite;
`;

const Title = styled.h1`
  font-size: 2.5rem; font-weight: 900; margin: 0 0 16px 0;
  letter-spacing: -1px; background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Message = styled.p`
  color: #94A3B8; font-size: 1.1rem; max-width: 500px;
  margin-bottom: 32px; line-height: 1.6;
`;

const IncidentBadge = styled.div`
  background: #1E293B; border: 1px solid #334155;
  padding: 10px 20px; border-radius: 8px;
  font-family: 'Courier New', monospace; 
  color: #F87171; font-size: 0.9rem; font-weight: 700;
  margin-bottom: 40px;
  display: flex; align-items: center; gap: 10px;
  letter-spacing: 1px;
`;

const ButtonGroup = styled.div`
  display: flex; gap: 16px;
`;

const PrimaryButton = styled.button`
  background: white; color: #0F172A; border: none;
  padding: 14px 28px; border-radius: 12px;
  font-weight: 800; font-size: 1rem; cursor: pointer;
  display: flex; align-items: center; gap: 8px;
  transition: transform 0.2s;
  &:hover { transform: translateY(-2px); background: #F1F5F9; }
`;

const SecondaryButton = styled.button`
  background: transparent; color: #94A3B8; 
  border: 1px solid #334155;
  padding: 14px 28px; border-radius: 12px;
  font-weight: 700; font-size: 1rem; cursor: pointer;
  display: flex; align-items: center; gap: 8px;
  transition: all 0.2s;
  &:hover { background: #1E293B; color: white; border-color: #64748B; }
`;

// -----------------------------------------------------------------------------
// COMPONENT LOGIC
// -----------------------------------------------------------------------------

export default function AccessDenied() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  // Generate a random Incident ID only once per render for forensic realism
  const incidentId = useMemo(() =>
    `SEC-${Math.floor(Math.random() * 1000000).toString(16).toUpperCase()}-${new Date().getFullYear()}`,
    []);

  const handleLogout = () => {
    logout(); // Clear Zustand store
    navigate('/login');
  };

  return (
    <Container>
      <IconWrapper>
        <ShieldAlert size={48} />
      </IconWrapper>

      <Title>403 • RESTRICTED SECTOR</Title>

      <Message>
        Your clearance level does not permit access to this module.
        This event has been logged by the Wilsy OS Security Kernel for audit purposes.
      </Message>

      <IncidentBadge>
        <Lock size={14} /> INCIDENT ID: {incidentId}
      </IncidentBadge>

      <ButtonGroup>
        <SecondaryButton onClick={handleLogout}>
          <LogOut size={18} /> Switch User
        </SecondaryButton>
        <PrimaryButton onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={18} /> Return to Dashboard
        </PrimaryButton>
      </ButtonGroup>
    </Container>
  );
}

