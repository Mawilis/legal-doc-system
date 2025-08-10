// ~/legal-doc-system/client/src/features/admin/services/adminService.js

import axios from 'axios';
import { toast } from 'react-toastify';

const API_BASE_URL = '/api/admin';

/**
 * Global error handler
 * @param {Object} error
 */
const handleError = (error) => {
    if (error.response && error.response.data && error.response.data.message) {
        toast.error(error.response.data.message);
        throw new Error(error.response.data.message);
    } else if (error.message) {
        toast.error(error.message);
        throw new Error(error.message);
    } else {
        toast.error('An unknown error occurred');
        throw new Error('An unknown error occurred');
    }
};

/**
 * Get all users
 * @returns {Promise<Array>}
 */
export const getAllUsers = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/users`);
        return response.data;
    } catch (error) {
        handleError(error);
    }
};

/**
 * Update a user by ID
 * @param {string} userId
 * @param {Object} updates
 * @returns {Promise<Object>}
 */
export const updateUser = async (userId, updates) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/users/${userId}`, updates);
        return response.data;
    } catch (error) {
        handleError(error);
    }
};

/**
 * Delete a user by ID
 * @param {string} userId
 * @returns {Promise<void>}
 */
export const deleteUser = async (userId) => {
    try {
        await axios.delete(`${API_BASE_URL}/users/${userId}`);
    } catch (error) {
        handleError(error);
    }
};

/**
 * Create a new user
 * @param {Object} newUser
 * @returns {Promise<Object>}
 */
export const createUser = async (newUser) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/users`, newUser);
        return response.data;
    } catch (error) {
        handleError(error);
    }
};

/**
 * Assign a user to a group/team
 * @param {string} userId
 * @param {string} teamId
 */
export const assignUserToTeam = async (userId, teamId) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/users/${userId}/team`, { teamId });
        return response.data;
    } catch (error) {
        handleError(error);
    }
};

/**
 * Toggle a module-level permission for a user
 * @param {string} userId
 * @param {string} module
 * @param {boolean} value
 */
export const togglePermission = async (userId, module, value) => {
    try {
        const response = await axios.patch(`${API_BASE_URL}/users/${userId}/permissions`, {
            module,
            value,
        });
        return response.data;
    } catch (error) {
        handleError(error);
    }
};

/**
 * Fetch audit logs (optional support)
 */
export const getAuditLogs = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/logs`);
        return response.data;
    } catch (error) {
        handleError(error);
    }
};
