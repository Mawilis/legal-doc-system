/*
 * File: src/api/axiosInstance.js
 * STATUS: EPITOME | API NERVE CENTER
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Centralized Axios configuration for Wilsy OS. Manages JWT injection, 
 * request/response interception, and global error normalization.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - SECURITY: Automatically attaches 'Bearer' tokens from localStorage.
 * - UX: Redirects to login on 401 (Session Expired).
 * - ARCHITECT: Uses a base URL from environment variables for scalability.
 * -----------------------------------------------------------------------------
 */

import axios from 'axios';

// --- 1. CONFIGURATION ---
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api/v1';

const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30-second timeout for heavy legal document processing
});

// --- 2. REQUEST INTERCEPTOR ---
/* * SECURITY GATE: Injects the JWT into every outgoing request automatically. */
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('wilsy_auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// --- 3. RESPONSE INTERCEPTOR ---
/* * RESILIENCY GATE: Handles global errors and session expiration. */
axiosInstance.interceptors.response.use(
    (response) => {
        // Return only the standardized 'data' envelope from our backend
        return response.data;
    },
    (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized (Expired Session)
        if (error.response?.status === 401 && !originalRequest._retry) {
            console.warn('🛡️ [SESSION_EXPIRED]: Redirecting to Login...');
            localStorage.removeItem('wilsy_auth_token');
            localStorage.removeItem('wilsy_user_context');
            window.location.href = '/login';
        }

        // Standardize the error object for the UI
        const errorMessage =
            error.response?.data?.message ||
            'Wilsy OS encountered a connectivity issue. Please check your link.';

        return Promise.reject({
            message: errorMessage,
            code: error.response?.data?.code || 'ERR_NETWORK',
            status: error.response?.status
        });
    }
);

export default axiosInstance;