/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Sovereign Authentication Context
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/contexts/authContext.jsx
 * Version:        v47.1.1-MFA-ENROLLMENT-ROUTING
 * Authority:      Wilsy OS Core Governance (POPIA §19, GDPR §32, SOC2 §CC7.2)
 * Epitome:        Removed default 'Founder' role fallback; now uses 'GENERAL' to resolve to GeneralDashboard.
 * Classification: Production Artifact
 *
 * Change Log:
 *   2026-08-22 v47.1.1-MFA-ENROLLMENT-ROUTING — Routes persisted enrollment attempts to validation and sends the strict EOS body contract.
 *   2026-08-20 v47.1.0-ROLE-FIX — Changed default role to 'GENERAL' to prevent non-Founder users from being hijacked to Founder Dashboard.
 *   2026-08-14 v47.0.0-INSTITUTIONAL-SEAL — Original version.
 *
 * Certification Seal: PRODUCTION_READY_v47.1.0-ROLE-FIX
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from "@/services/api";

const AuthContext = createContext(null);

const parseSafeJSON = async (response) => {
    const text = await response.text();
    try {
        return text ? JSON.parse(text) : {};
    } catch (err) {
        throw new Error(`Server returned non-JSON payload (Status ${response.status}).`);
    }
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(() => {
        try {
            const saved = localStorage.getItem('wilsy_sovereign_user');
            if (saved) {
                const parsed = JSON.parse(saved);
                return { mfaRegistered: false, hasSignedCovenant: false, ...parsed };
            }
            return null;
        } catch { return null; }
    });

    const [token, setToken] = useState(() => localStorage.getItem('wilsy_auth_token') || null);
    const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('wilsy_auth_token'));
    const [tenant, setTenant] = useState(() => {
        try {
            const saved = localStorage.getItem('discoveredTenant');
            return saved ? JSON.parse(saved) : null;
        } catch { return null; }
    });

    const [authStage, setAuthStage] = useState('IDLE');
    const [pendingEmail, setPendingEmail] = useState('');
    const [qrCodeData, setQrCodeData] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const mfaRequired = authStage === 'MFA_REQUIRED' || authStage === 'MFA_SETUP';

    useEffect(() => {
        if (token) {
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete api.defaults.headers.common['Authorization'];
        }

        if (tenant && (tenant.tenantId || tenant.id)) {
            api.defaults.headers.common['x-tenant-id'] = tenant.tenantId || tenant.id;
        } else {
            delete api.defaults.headers.common['x-tenant-id'];
        }
    }, [token, tenant]);

    const discoverTenant = async (tenantAlias) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('/api/auth/discover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({ alias: tenantAlias || 'WILSY' })
            });
            const data = await parseSafeJSON(response);
            
            if (response.ok && (data.success || data.tenant)) {
                const activeTenant = data.tenant || data;
                setTenant(activeTenant);
                localStorage.setItem('discoveredTenant', JSON.stringify(activeTenant));
                localStorage.setItem('wilsy_active_tenant', activeTenant.tenantId || 'WILSY');
                return activeTenant;
            }
            throw new Error(data.message || 'Tenant discovery failed');
        } catch (err) {
            console.warn('[WILSY-AUTH-WARNING] Tenant discovery endpoint unreachable. Fallback engaged.', err.message);
            const defaultTenant = { tenantId: 'WILSY', alias: 'wilsy', name: 'Wilsy Sovereign Shard' };
            setTenant(defaultTenant);
            localStorage.setItem('discoveredTenant', JSON.stringify(defaultTenant));
            localStorage.setItem('wilsy_active_tenant', 'WILSY');
            return defaultTenant;
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.post('/auth/login', { email, password });
            const data = response.data;
            console.log('[AUTH-CONTEXT] Authentication Vector Response:', data.status || 'SUCCESS');

            setPendingEmail(email);

            const isSetup = data.status === 'MFA_SETUP' || data.mfaSetup || data.qrCode;
            const isMfaRequired = data.status === 'MFA_REQUIRED' || data.requiresMFA || data.mfaRequired;
            const hasToken = data.token || data.accessToken;

            if (isSetup) {
                const qr = data.qrCode || data.secret || '';
                setQrCodeData(qr);
                setAuthStage('MFA_SETUP');
                return { status: 'MFA_SETUP', qrCode: qr, requiresMFA: true, tempToken: data.tempToken || null, email };
            } 
            
            if (isMfaRequired) {
                setAuthStage('MFA_REQUIRED');
                return { status: 'MFA_REQUIRED', requiresMFA: true, tempToken: data.tempToken || null, qrCode: data.qrCode || null, email };
            } 
            
            if (hasToken) {
                const actualToken = data.token || data.accessToken;
                
                // 🛡️ FIX: Do NOT default to 'Founder'. Use backend role or fallback to 'GENERAL'
                const userData = {
                    email,
                    mfaRegistered: true,
                    hasSignedCovenant: false,
                    role: data.user?.role || 'GENERAL',           // ← CHANGED
                    tenantAlias: data.user?.tenantAlias || 'WILSY',
                    ...(data.user || {})
                };
                
                if (!userData.firstName) userData.firstName = email.split('@')[0];
                if (!userData.lastName) userData.lastName = '';
                
                setToken(actualToken);
                setUser(userData);
                localStorage.setItem('wilsy_auth_token', actualToken);
                localStorage.setItem('token', actualToken);
                localStorage.setItem('wilsy_sovereign_user', JSON.stringify(userData));
                setAuthStage('AUTHENTICATED');
                setIsAuthenticated(true);
                
                return { status: 'AUTHENTICATED', requiresMFA: false, success: true, user: userData, token: actualToken };
            } 
            
            if (data.success) {
                setAuthStage('MFA_REQUIRED');
                return { status: 'MFA_REQUIRED', requiresMFA: true, tempToken: data.tempToken || null, qrCode: data.qrCode || null, email };
            }
            
            throw new Error('Unrecognized sovereign payload structure from Kernel.');
        } catch (err) {
            console.error('[AUTH-CONTEXT-ERROR] Login execution failed:', err);
            setError(err.response?.data?.message || err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const verifyOTP = async (email, code, biometricAssertion = null, traceId = null, mfaSetup = false) => {
        setLoading(true);
        setError(null);
        const targetEmail = email || pendingEmail;
        const targetCode = code || '';

        const endpoints = [
            mfaSetup || authStage === 'MFA_SETUP' ? '/auth/validate-mfa-setup' : '/auth/verify-otp',
            '/auth/verify-3fa'
        ];

        let lastError = new Error('Verification endpoints exhausted.');

        for (const endpoint of endpoints) {
            try {
                const response = await api.post(endpoint, { email: targetEmail, code: targetCode });
                const data = response.data;

                if (data.success || data.token || data.accessToken || data.status === 'AUTHENTICATED') {
                    const authToken = data.token || data.accessToken;
                    if (!authToken) throw new Error('Token missing from successful MFA verification.');
                    
                    const authUser = {
                        email: targetEmail,
                        mfaRegistered: true,
                        hasSignedCovenant: data.user?.hasSignedCovenant || false,
                        role: data.user?.role || 'GENERAL',           // ← CHANGED
                        tenantAlias: data.user?.tenantAlias || 'WILSY',
                        ...data.user
                    };
                    
                    if (!authUser.firstName) authUser.firstName = targetEmail.split('@')[0];
                    if (!authUser.lastName) authUser.lastName = '';
                    
                    setToken(authToken);
                    setUser(authUser);
                    localStorage.setItem('wilsy_auth_token', authToken);
                    localStorage.setItem('token', authToken);
                    localStorage.setItem('wilsy_sovereign_user', JSON.stringify(authUser));
                    if (data.refreshToken) localStorage.setItem('wilsy_refresh_token', data.refreshToken);
                    
                    setAuthStage('AUTHENTICATED');
                    setIsAuthenticated(true);
                    return { success: true, ...data, user: authUser, token: authToken };
                }
            } catch (err) {
                lastError = err;
            }
        }
        
        setLoading(false);
        throw lastError || new Error('All MFA verification endpoints failed.');
    };

    const verify3FA = async (code) => verifyOTP(pendingEmail, code);

    const updateSovereignIdentity = useCallback(async (updates) => {
        let currentUser = user;
        if (!currentUser) {
            try {
                const saved = localStorage.getItem('wilsy_sovereign_user');
                if (saved) currentUser = JSON.parse(saved);
            } catch { /* fall through */ }
        }
        if (!currentUser) {
            currentUser = { email: pendingEmail || 'founder@wilsyos.com', mfaRegistered: true, hasSignedCovenant: false };
        }
        
        const updatedUser = { ...currentUser, ...updates };
        setUser(updatedUser);
        localStorage.setItem('wilsy_sovereign_user', JSON.stringify(updatedUser));
        if (token) setIsAuthenticated(true);
        return updatedUser;
    }, [user, pendingEmail, token]);

    const reportError = async (errorPayload) => {
        try {
            await api.post('/telemetry/error', { ...errorPayload, timestamp: new Date().toISOString() });
        } catch { /* suppress */ }
    };

    const logout = useCallback(async () => {
        try {
            if (token) await api.post('/auth/logout');
        } catch { 
            console.warn('[AUTH-CONTEXT-WARNING] Backend logout request failed, enforcing client-side purge.');
        } finally {
            setToken(null); 
            setUser(null); 
            setIsAuthenticated(false); 
            setAuthStage('IDLE');
            setPendingEmail(''); 
            setQrCodeData('');
            
            localStorage.removeItem('wilsy_auth_token');
            localStorage.removeItem('wilsy_sovereign_user');
            localStorage.removeItem('wilsy_refresh_token');
            localStorage.removeItem('token');
        }
    }, [token]);

    const tenantId = user?.tenantId || tenant?.tenantId || tenant?.id || null;
    const userRole = user?.role || user?.userRole || null;
    
    const value = {
        user, token, isAuthenticated, tenant, tenantId, userRole, authStage, mfaRequired, pendingEmail, qrCodeData,
        loading, error, discoverTenant, login, verifyOTP, verify3FA, reportError, logout,
        setAuthStage, updateSovereignIdentity
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be executed within an active Sovereign AuthProvider instance.');
    return context;
};

export default AuthContext;
