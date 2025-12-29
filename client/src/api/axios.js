/**
 * /Users/wilsonkhanyezi/legal-doc-system/client/src/api/axios.js
 *
 * Axios Instance
 * --------------
 * - Attaches Authorization: Bearer <accessToken>
 * - Refreshes on 401 and retries once
 */

import axios from 'axios';
import { getAccessToken, getRefreshToken, setAccessToken, clearAuth } from '../auth/tokenStorage';
import authService from '../services/authService';

const api = axios.create({
    baseURL: 'http://localhost:3001/api',
});

api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

let isRefreshing = false;
let queue = [];

const flushQueue = (err, token = null) => {
    queue.forEach(({ resolve, reject }) => (err ? reject(err) : resolve(token)));
    queue = [];
};

api.interceptors.response.use(
    (res) => res,
    async (error) => {
        const original = error.config;
        if (error.response?.status !== 401 || original._retry) {
            return Promise.reject(error);
        }

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                queue.push({ resolve, reject });
            }).then((token) => {
                original.headers.Authorization = `Bearer ${token}`;
                original._retry = true;
                return api(original);
            });
        }

        isRefreshing = true;
        original._retry = true;

        try {
            const rt = getRefreshToken();
            if (!rt) throw new Error('No refresh token');

            const newAccess = await authService.refresh(rt);
            setAccessToken(newAccess);
            flushQueue(null, newAccess);

            original.headers.Authorization = `Bearer ${newAccess}`;
            return api(original);
        } catch (err) {
            flushQueue(err, null);
            clearAuth();
            return Promise.reject(err);
        } finally {
            isRefreshing = false;
        }
    }
);

export default api;
