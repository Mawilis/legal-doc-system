import axios from 'axios';
import { toast } from 'react-toastify';

// Admin-specific service
const API_URL = '/api/admin';

// Get all users (Admin functionality)
export const getAllUsers = async () => {
    try {
        const response = await axios.get(`${API_URL}/users`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error; // Re-throw to handle the error in calling functions
    }
};

// Delete user (Admin functionality)
export const deleteUser = async (userId) => {
    try {
        const response = await axios.delete(`${API_URL}/users/${userId}`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Promote user to admin (Admin functionality)
export const promoteUser = async (userId) => {
    try {
        const response = await axios.put(`${API_URL}/users/${userId}/promote`);
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Handle and display errors
const handleError = (error) => {
    if (error.response) {
        // Server responded with a status other than 200 range
        toast.error(error.response.data.message || 'An error occurred');
    } else if (error.request) {
        // No response was received
        toast.error('No response from server. Please try again later.');
    } else {
        // Other errors
        toast.error('Something went wrong. Please try again.');
    }
};

// Export default service object for easy import
const adminService = {
    getAllUsers,
    deleteUser,
    promoteUser,
};

export default adminService;
