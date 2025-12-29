/**
 * /Users/wilsonkhanyezi/legal-doc-system/client/src/auth/tokenStorage.js
 *
 * Token Storage
 * -------------
 * Simple localStorage-based storage for access and refresh tokens.
 * For production, consider httpOnly cookies for refresh.
 */

const ACCESS_KEY = 'accessToken';
const REFRESH_KEY = 'refreshToken';

export const getAccessToken = () => localStorage.getItem(ACCESS_KEY) || null;
export const setAccessToken = (token) => localStorage.setItem(ACCESS_KEY, token);

export const getRefreshToken = () => localStorage.getItem(REFRESH_KEY) || null;
export const setRefreshToken = (token) => localStorage.setItem(REFRESH_KEY, token);

export const clearAuth = () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
};
