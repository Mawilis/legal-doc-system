// ~/legal-doc-system/client/src/features/admin/services/adminService.js

import axios from "axios";

// Base URL for admin-related API endpoints
const API_BASE_URL = "/api/admin";

/**
 * Handle errors from API calls.
 * @param {Object} error - The error object caught from a try-catch block.
 */
const handleError = (error) => {
    if (error.response && error.response.data && error.response.data.message) {
        throw new Error(error.response.data.message);
    } else {
        throw new Error(error.message || "An unknown error occurred");
    }
};

/**
 * Fetch all users.
 * @returns {Promise<Array>} List of users.
 */
export const getAllUsers = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/users`);
        return response.data; // Assuming the API returns an array of users
    } catch (error) {
        handleError(error);
    }
};

/**
 * Update a user's information.
 * @param {string|number} userId - The ID of the user to update.
 * @param {Object} updates - The fields to update.
 * @returns {Promise<Object>} The updated user object.
 */
export const updateUser = async (userId, updates) => { // Changed function signature
    try {
        const response = await axios.put(
            `${API_BASE_URL}/users/${userId}`,
            updates
        );
        return response.data; // Assuming the API returns the updated user object
    } catch (error) {
        handleError(error);
    }
};

/**
 * Delete a user by ID.
 * @param {string|number} userId - The ID of the user to delete.
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
 * Create a new user.
 * @param {Object} newUser - The data for the new user.
 * @returns {Promise<Object>} The created user object.
 */
export const createUser = async (newUser) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/users`, newUser);
        return response.data; // Assuming the API returns the created user object
    } catch (error) {
        handleError(error);
    }
};