/*
 * File: client/src/api/axios.js
 * STATUS: EPITOME | NETWORK CORE (VITE EDITION)
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The Central Nervous System for Data Transmission.
 * 1. ADAPTS to the Vite Engine using 'import.meta.env'.
 * 2. SECURES traffic by auto-injecting the User's Passport (JWT).
 * 3. STABILIZES the UI by normalizing error messages.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - ENVIRONMENT: Uses 'import.meta.env.VITE_API_URL' to prevent 'process is not defined' crashes.
 * - FALLBACK: Defaults to '/api' so the Proxy in vite.config.js handles the routing.
 * - SECURITY: Interceptors manually parse LocalStorage to avoid Circular Dependency with Zustand.
 * -----------------------------------------------------------------------------
 */

import axios from 'axios';

// -----------------------------------------------------------------------------
// 1. INTELLIGENT ENVIRONMENT DETECTION
// -----------------------------------------------------------------------------
// CRITICAL FIX: Vite does not support 'process.env'. We use 'import.meta.env'.
const BASE_URL = import.meta.env.VITE_API_URL || '/api';

console.log(`🚀 [Wilsy OS] Network Core Online: ${BASE_URL}`);

// -----------------------------------------------------------------------------
// 2. THE INSTANCE (SINGLETON)
// -----------------------------------------------------------------------------
const axiosInstance = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    // Timeout after 15 seconds to prevent hanging UIs
    timeout: 15000,
});

// -----------------------------------------------------------------------------
// 3. REQUEST INTERCEPTOR (The Security Gate)
// -----------------------------------------------------------------------------
axiosInstance.interceptors.request.use(
    (config) => {
        // A. Locate the Passport (Token) inside the encrypted storage
        const userStorage = localStorage.getItem('wilsy-auth-storage');

        if (userStorage) {
            const parsedStorage = JSON.parse(userStorage);
            const token = parsedStorage.state?.token;

            // B. Inject the Token into the Header
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        return config;
    },
    (error) => {
        // Request failed before leaving the browser
        return Promise.reject(error);
    }
);

// -----------------------------------------------------------------------------
// 4. RESPONSE INTERCEPTOR (The Filter)
// -----------------------------------------------------------------------------
axiosInstance.interceptors.response.use(
    (response) => {
        // 2xx Status Code: Traffic allowed
        return response.data; // Return direct data to clean up Controller logic
    },
    (error) => {
        // Non-2xx Status Code: Traffic blocked

        // A. Handle 401 (Unauthorized) - Auto Logout Trigger
        if (error.response && error.response.status === 401) {
            console.warn('⚠️ [Wilsy OS] Session Expired. Security Protocol Initiated.');
            // Future: Dispatch logout action here if needed
        }

        // B. Standardize the Error Message
        // This ensures your UI components always get a clean string, not an object.
        const message =
            (error.response && error.response.data && error.response.data.message) ||
            error.message ||
            'Unknown Network Error';

        console.error(`❌ [Wilsy OS] Network Error: ${message}`);

        return Promise.reject(error);
    }
);

export default axiosInstance;