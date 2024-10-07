import axios from 'axios';
import jwtDecode from 'jwt-decode';
import { toast } from 'react-toastify';

// Login function
export const login = async (credentials) => {
    try {
        const response = await axios.post('/api/auth/login', credentials);
        const { token } = response.data;
        localStorage.setItem('token', token); // Save token in localStorage
        return response.data;
    } catch (error) {
        handleError(error);
        throw error;
    }
};

// Logout function
export const logout = () => {
    localStorage.removeItem('token'); // Remove token from localStorage
    toast.success('You have been logged out.');
};

// Get the current user's information from the JWT token
export const getCurrentUser = () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            return jwtDecode(token); // Decode JWT to get user info
        }
        return null;
    } catch (error) {
        return null;
    }
};

// Check if the user is authenticated
export const isAuthenticated = () => {
    const token = localStorage.getItem('token');
    if (token) {
        try {
            const { exp } = jwtDecode(token); // Get expiration time from token
            if (exp * 1000 > Date.now()) {
                return true;
            } else {
                logout(); // Token expired, perform logout
                return false;
            }
        } catch (error) {
            return false;
        }
    }
    return false;
};

// Get the user's role from the JWT token
export const getUserRole = () => {
    const user = getCurrentUser();
    return user ? user.role : null; // Get role from user info if available
};

// Handle errors and show toast notifications
const handleError = (error) => {
    if (error.response && error.response.data && error.response.data.message) {
        toast.error(error.response.data.message);
    } else {
        toast.error('An error occurred. Please try again.');
    }
};

// Export the auth services
const authService = {
    login,
    logout,
    getCurrentUser,
    isAuthenticated,
    getUserRole,
};

export default authService;
