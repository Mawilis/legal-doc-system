/**
 * File: client/src/services/http.js
 * ---------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Unified Axios client for the frontend.
 * - Directly targets Gateway at http://localhost:3001/api for local dev.
 * - Request interceptor: attaches Authorization and x-tenant-id headers.
 * - Response interceptor:
 *   • On 401, attempts silent refresh + retries the original request once.
 *   • If refresh fails, forces logout and redirects to /login.
 * - Dependencies:
 *   • Redux store is required to dispatch refreshUser and forceLogout.
 *   • Ensure store export path is correct.
 * ---------------------------------------------------------------------------
 */

import axios from 'axios';
import store from '../store'; // adjust if your store path differs
import { refreshUser, forceLogout } from '../features/auth/reducers/authSlice';

// Axios Instance
const http = axios.create({
  baseURL: 'http://localhost:3001/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
  withCredentials: true // important if backend uses HttpOnly cookies for refresh
});

// Request Interceptor: attach token + tenant
http.interceptors.request.use(
  (config) => {
    try {
      const rawUser = localStorage.getItem('user');
      const user = rawUser ? JSON.parse(rawUser) : null;
      const directToken = localStorage.getItem('accessToken');
      let token = null;

      if (user && user.token) token = user.token;
      else if (directToken) token = directToken;

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      const tenantId = localStorage.getItem('tenantId') || '650c1f1e1f1e1f1e1f1e1f1e';
      if (tenantId) {
        config.headers['x-tenant-id'] = tenantId;
      }
    } catch (err) {
      console.error('❌ [Http] Token retrieval error:', err);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: silent refresh + retry
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh once per request
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const resultAction = await store.dispatch(refreshUser());
        if (refreshUser.fulfilled.match(resultAction)) {
          const newToken = resultAction.payload.token;
          // Update header and retry original request
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return http(originalRequest);
        }
      } catch (refreshErr) {
        console.error('🔴 [Http] Refresh failed:', refreshErr);
      }

      // Fallback: force logout and redirect
      store.dispatch(forceLogout());
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    if (error.response && error.response.status >= 500) {
      console.error('🔥 [Http] Server Error:', error.response.data?.message);
    }

    return Promise.reject(error);
  }
);

// Convenience exports
export const apiGet = (url, config) => http.get(url, config);
export const apiPost = (url, data, config) => http.post(url, data, config);
export const apiPut = (url, data, config) => http.put(url, data, config);
export const apiPatch = (url, data, config) => http.patch(url, data, config);
export const apiDelete = (url, config) => http.delete(url, config);

export default http;
