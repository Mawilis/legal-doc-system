/*
 * File: src/auth/tokenStorage.js
 * STATUS: EPITOME | IDENTITY VAULT GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The authoritative local storage engine for Wilsy OS. Manages the lifecycle 
 * of JWTs and User Identity context within the browser's persistent layer.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - SECURITY: Implements explicit keys to prevent namespace collisions.
 * - ARCHITECT: Provides a unified 'clear' method for secure logout procedures.
 * - FUTURE-PROOF: While currently localStorage, this interface allows for 
 * a seamless transition to Secure Cookies or IndexedDB without changing UI logic.
 * -----------------------------------------------------------------------------
 */

'use strict';

// --- 1. KEY CONSTANTS (THE NAMESPACE) ---
const KEYS = {
    ACCESS: 'wilsy_at_v1',
    REFRESH: 'wilsy_rt_v1',
    USER: 'wilsy_user_v1'
};

// -----------------------------------------------------------------------------
// ACCESS TOKEN LOGIC (Short-lived Identity)
// -----------------------------------------------------------------------------

/**
 * Retrieves the primary Bearer token for API requests.
 * @returns {string|null}
 */
export const getAccessToken = () => localStorage.getItem(KEYS.ACCESS) || null;

/**
 * Persists the primary Bearer token.
 * @param {string} token 
 */
export const setAccessToken = (token) => {
    if (token) localStorage.setItem(KEYS.ACCESS, token);
};

// -----------------------------------------------------------------------------
// REFRESH TOKEN LOGIC (Long-lived Session)
// -----------------------------------------------------------------------------

/**
 * Retrieves the refresh token used for silent re-authentication.
 * @returns {string|null}
 */
export const getRefreshToken = () => localStorage.getItem(KEYS.REFRESH) || null;

/**
 * Persists the refresh token.
 * @param {string} token 
 */
export const setRefreshToken = (token) => {
    if (token) localStorage.setItem(KEYS.REFRESH, token);
};

// -----------------------------------------------------------------------------
// USER CONTEXT LOGIC (UI Hydration)
// -----------------------------------------------------------------------------

/**
 * Persists the user metadata (Name, Role, Avatar) to prevent flickering on load.
 * @param {Object} userData 
 */
export const setUserContext = (userData) => {
    if (userData) localStorage.setItem(KEYS.USER, JSON.stringify(userData));
};

/**
 * Retrieves the stored user metadata.
 * @returns {Object|null}
 */
export const getUserContext = () => {
    const user = localStorage.getItem(KEYS.USER);
    try {
        return user ? JSON.parse(user) : null;
    } catch (e) {
        return null;
    }
};

// -----------------------------------------------------------------------------
// LIFECYCLE MANAGEMENT
// -----------------------------------------------------------------------------

/**
 * SECURE WIPE: Clears all identity-related data from the browser.
 * Used during logout or when a security breach/session expiry is detected.
 */
export const clearAuth = () => {
    Object.values(KEYS).forEach(key => localStorage.removeItem(key));

    // Optional: Forensic cleanup of session storage
    sessionStorage.clear();
};

/**
 * AUTH CHECK: Lightweight verification if the user is potentially logged in.
 */
export const isAuthenticated = () => !!getAccessToken();