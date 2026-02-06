/**
 * File: client/src/services/httpSetup.js
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Purpose: Attach Redux-aware refresh logic to the pure http client.
 * - Engineers:
 *   • Import this in your app entry (e.g., index.js) after store is created.
 *   • Keeps http.js decoupled from Redux to avoid circular imports.
 * -----------------------------------------------------------------------------
 */

import http from './http';
import { refreshUser, forceLogout } from '../features/auth/reducers/authSlice';

export const setupHttpInterceptors = (store) => {
    http.interceptors.response.use(
        (response) => response,
        async (error) => {
            const originalRequest = error.config;

            if (error.response && error.response.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;
                try {
                    const resultAction = await store.dispatch(refreshUser());
                    if (refreshUser.fulfilled.match(resultAction)) {
                        const newToken = resultAction.payload.token;
                        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                        return http(originalRequest);
                    }
                } catch (refreshErr) {
                    console.error('🔴 [HTTP] Refresh failed:', refreshErr);
                }

                store.dispatch(forceLogout());
                if (window.location.pathname !== '/login') {
                    window.location.href = '/login';
                }
            }

            return Promise.reject(error);
        }
    );
};
