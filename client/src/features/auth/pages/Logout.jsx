/*
 * File: src/features/auth/pages/Logout.jsx
 * STATUS: EPITOME | SECURE SESSION TERMINATION
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Executes the 'Kill Switch' on the user session. 
 * Wipes local storage, clears global state, and redirects to the public gateway.
 * -----------------------------------------------------------------------------
 * ARCHITECTURE:
 * - Uses Zustand (authStore) for instant state clearing.
 * - Provides a brief visual feedback (Forensic Theater) before redirect.
 * -----------------------------------------------------------------------------
 */

'use client';

import React, { useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { LogOut, ShieldCheck } from 'lucide-react';

// --- BRAIN: Zustand Store ---
import useAuthStore from '../../../store/authStore';

// --- ANIMATIONS ---
const spin = keyframes`
  to { transform: rotate(360deg); }
`;

const fadeOut = keyframes`
  0% { opacity: 1; }
  100% { opacity: 0.5; }
`;

// --- STYLED ARCHITECTURE ---
const Container = styled.div`
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0F172A; /* Slate 900 */
  color: white;
  font-family: 'Inter', sans-serif;
`;

const LoaderRing = styled.div`
  width: 64px;
  height: 64px;
  border: 4px solid #1E293B;
  border-top-color: #38BDF8; /* Sky 400 */
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
  margin-bottom: 32px;
`;

const StatusText = styled.h2`
  font-size: 1.5rem;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0 0 8px 0;
  animation: ${fadeOut} 1.5s infinite alternate;
`;

const SecureBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #10B981; /* Emerald 500 */
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 16px;
  background: rgba(16, 185, 129, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(16, 185, 129, 0.2);
`;

export default function Logout() {
    const navigate = useNavigate();
    const { logout } = useAuthStore();

    useEffect(() => {
        // 1. Execute Session Kill Switch
        logout();

        // 2. Artificial Delay (800ms) for visual confirmation
        // This allows the user to see "Securing Session..." before the flash to login
        const timer = setTimeout(() => {
            navigate('/login', { replace: true });
        }, 1500);

        return () => clearTimeout(timer);
    }, [logout, navigate]);

    return (
        <Container>
            <LoaderRing />
            <StatusText>Securing Workspace...</StatusText>
            <div style={{ color: '#64748B', fontSize: '0.9rem' }}>Terminating encrypted connection</div>

            <SecureBadge>
                <ShieldCheck size={14} /> Session Wiped
            </SecureBadge>
        </Container>
    );
} 



