/**
 * /Users/wilsonkhanyezi/legal-doc-system/client/src/auth/AuthContext.js
 *
 * Auth Context
 * ------------
 * Provides auth state, login/logout helpers to the app.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { loginRequest, logoutRequest, refreshAccessToken } from './authApi';
import { getAccessToken, setAccessToken, getRefreshToken, setRefreshToken, clearAuth } from './tokenStorage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        // Optionally decode token and set user from payload here.
        // For now, just mark loaded.
        setLoaded(true);
    }, []);

    const login = async (email, password) => {
        const data = await loginRequest({ email, password, deviceId: 'web' });
        setAccessToken(data.accessToken);
        setRefreshToken(data.refreshToken);
        setUser(data.user);
        return data.user;
    };

    const logout = async () => {
        const rt = getRefreshToken();
        if (rt) {
            try {
                await logoutRequest(rt);
            } catch { /* ignore */ }
        }
        clearAuth();
        setUser(null);
    };

    const refresh = async () => {
        const rt = getRefreshToken();
        if (!rt) return null;
        const newToken = await refreshAccessToken(rt);
        setAccessToken(newToken);
        return newToken;
    };

    return (
        <AuthContext.Provider value={{ user, loaded, login, logout, refresh }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
