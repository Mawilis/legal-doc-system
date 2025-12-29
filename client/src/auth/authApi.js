/**
 * /Users/wilsonkhanyezi/legal-doc-system/client/src/auth/authApi.js
 *
 * Auth API
 * --------
 * Login, refresh, and logout calls to backend.
 */

import axios from 'axios';

const BASE = 'http://localhost:3001/api';

export async function loginRequest({ email, password, deviceId }) {
    const res = await axios.post(`${BASE}/auth/login`, { email, password, deviceId });
    return res.data; // { accessToken, refreshToken, user }
}

export async function refreshAccessToken(refreshToken) {
    const res = await axios.post(`${BASE}/auth/refresh`, { refreshToken });
    return res.data.accessToken;
}

export async function logoutRequest(refreshToken) {
    const res = await axios.post(`${BASE}/auth/logout`, { refreshToken });
    return res.data;
}
