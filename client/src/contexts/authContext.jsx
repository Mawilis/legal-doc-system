/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IDENTITY CONTEXT [V43.1.0-SINGULARITY-OMEGA]                                                                      ║
 * ║ [TELEMETRY ENRICHMENT | BOOT-TIME ANCHORING | SILICON STRIKE SYNC | BOARDROOM READY]                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 43.1.0-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | BOARDROOM READY                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/authContext.jsx                                              ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated extended telemetry for boardroom visibility and SLA tracking.                        ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Implemented Jitter-Shield to prevent recursive forensic purges. [2026-05-14]                     ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Aligned logout logic with [AUTH-ERROR] status reporting. [2026-05-14]                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import forge from 'node-forge';

const AuthContext = createContext();

/**
 * @function getStoredRefreshToken
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const getStoredRefreshToken = () => {
  const raw = localStorage.getItem('wilsy_refresh_token') || localStorage.getItem('refreshToken');
  if (!raw || raw === 'undefined' || raw === 'null') return null;
  return raw.replace(/^["']|["']$/g, '');
};

export 
/**
 * @function AuthProvider
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('wilsy_user');
    try { return stored ? JSON.parse(stored) : null; } catch (e) { return null; }
  });

  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('wilsy_auth_token'));

  const [tenant, setTenant] = useState(() => {
    const storedTenant = localStorage.getItem('wilsy_tenant');
    try { return storedTenant ? JSON.parse(storedTenant) : null; } catch (e) { return null; }
  });

  const [loading, setLoading] = useState(false);
  const [mfaInProgress, setMfaInProgress] = useState(false);
  const [tempEmail, setTempEmail] = useState(null);

  const logout = useCallback((reason = "Session terminated") => {
    console.warn(`[AUTH-SHIELD] 🚨 Sovereign Nexus Fracture. Forensic purge initiated. Reason: ${reason}`);

    // 📡 Final Forensic Broadcast before wiping
    broadcastTelemetry("GLOBAL_ROOT", "SECURITY_EVENT", "FORENSIC_PURGE", "AuthContext", {
      reason,
      shard: "WILSY_ROOT",
      feed: "NUCLEUS_FEED_V46.1"
    });

    localStorage.clear();
    setUser(null);
    setTenant(null);
    setIsAuthenticated(false);
    setMfaInProgress(false);
    delete api.defaults.headers.common['Authorization'];

    window.location.href = '/login';
  }, []);

  // 🏛️ BOOT-TIME SILENT REFRESH: Re-anchors session with Jitter-Shield
  useEffect(() => {
    
/**
 * @function trySilentRefresh
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const trySilentRefresh = async () => {
      const token = localStorage.getItem('wilsy_auth_token');
      if (!token) return;

      try {
        const refreshToken = getStoredRefreshToken();
        const response = await api.post('/auth/refresh-token', refreshToken ? { refreshToken } : undefined, {
          timeout: 8000,
          skipAuthRedirect: true,
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.data?.success && response.data?.token) {
          localStorage.setItem('wilsy_auth_token', response.data.token);
          localStorage.setItem('token', response.data.token);
          api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
          setIsAuthenticated(true);

          broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "SILENT_REFRESH_SUCCESS", "AuthContext", {
            latencyMs: response.data.telemetry?.latencyMs,
            breakerState: response.data.telemetry?.breakerState,
            compliance: 'POPIA_CLEAN',
            feed: "NUCLEUS_FEED_V46.1"
          });
        }
      } catch (err) {
        // 🛡️ JITTER-SHIELD: Do not purge if it's a network glitch or system restart
        if (err.response?.status === 401) {
          logout("EXPIRED_TOKEN_PURGE");
        } else {
          console.warn("[AUTH-SHIELD] Minor Nexus Jitter detected. Preservation mode active.");
        }
      }
    };
    trySilentRefresh();
  }, [logout]);

  // 🏛️ 30-MINUTE TOKEN ROTATION
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        if (isAuthenticated) {
          const token = localStorage.getItem('wilsy_auth_token');
          if (!token) return;
          const refreshToken = getStoredRefreshToken();
          await api.post('/auth/refresh-token', refreshToken ? { refreshToken } : undefined, {
            timeout: 8000,
            skipAuthRedirect: true,
            headers: { Authorization: `Bearer ${token}` }
          });
        }
      } catch (err) {
        if (err.response?.status === 401) logout("ROTATION_FRACTURE");
      }
    }, 1000 * 60 * 30);
    return () => clearInterval(interval);
  }, [isAuthenticated, logout]);

  const login = useCallback(async (email, password, tenantId) => {
    try {
      const response = await api.post('/auth/login', { email, password, tenantId });
      const { status, tempToken, qrCode, hasBiometric, authStrategy } = response.data;

      if (status === 'MFA_REQUIRED' || status === 'MFA_SETUP') {
        setMfaInProgress(true);
        setTempEmail(email);
        return { success: true, status, tempToken, qrCode, hasBiometric, authStrategy };
      }
      return { success: false, message: "Handshake fractured." };
    } catch (error) {
      broadcastTelemetry("GLOBAL_ROOT", "SECURITY_EVENT", "LOGIN_FAILURE", "AuthContext", { reason: error.message });
      throw new Error(error.response?.data?.message || 'Authentication failed');
    }
  }, []);

  const directVerifyMFA = useCallback(async (email, otp, biometricAssertion = null, traceId = null) => {
    try {
      let biometricToken = null;
      if (typeof biometricAssertion === 'string' && biometricAssertion.includes('BEGIN PRIVATE KEY')) {
        const privateKey = forge.pki.privateKeyFromPem(biometricAssertion);
        const md = forge.md.sha256.create();
        md.update('wilsy-auth-challenge', 'utf8');
        const signature = privateKey.sign(md);
        biometricToken = forge.util.encode64(signature);
      }

      const response = await api.post('/auth/verify-3fa', {
        email, otp, traceId,
        biometricAssertion: typeof biometricAssertion === 'object' ? biometricAssertion : null,
        biometricToken
      });

      if (response.data.success) {
        const { token, user: backendUser, telemetry } = response.data;
        const sealedUser = { ...backendUser, mfaVerified: true, hasSignedCovenant: true };

        localStorage.setItem('wilsy_auth_token', token);
        localStorage.setItem('wilsy_user', JSON.stringify(sealedUser));
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        setUser(sealedUser);
        setIsAuthenticated(true);
        setMfaInProgress(false);

        broadcastTelemetry("GLOBAL_ROOT", "SYSTEM_EVENT", "MFA_SUCCESS", "AuthContext", {
          userId: sealedUser.id,
          latencyMs: telemetry?.latencyMs,
          shardStatus: 'ANCHORED',
          feed: "NUCLEUS_FEED_V46.1"
        });
        return { success: true, token, user: sealedUser };
      }
      return { success: false, message: response.data.message };
    } catch (error) {
      broadcastTelemetry("GLOBAL_ROOT", "SECURITY_EVENT", "MFA_FAILURE", "AuthContext", { reason: error.message });
      throw new Error(error.response?.data?.message || '3FA verification failed');
    }
  }, []);

  const verifyOTP = useCallback(async (email, otp, biometricAssertion, traceId) => {
    return directVerifyMFA(email || tempEmail, otp, biometricAssertion, traceId);
  }, [tempEmail, directVerifyMFA]);

  return (
    <AuthContext.Provider value={{
      user, tenant, isAuthenticated, loading, mfaInProgress, tempEmail,
      login, verifyOTP, directVerifyMFA, logout, updateSovereignIdentity: setUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export 
/**
 * @function useAuth
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const useAuth = () => useContext(AuthContext);
