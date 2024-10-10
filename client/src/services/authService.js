// Import necessary libraries and modules
import { jwtDecode } from 'jwt-decode'; // Correctly import jwtDecode
import { toast } from 'react-toastify';

// Helper function to get the current user's role
export const getCurrentUserRole = () => {
    const token = localStorage.getItem('token');
    if (token) {
        const decoded = jwtDecode(token);
        return decoded.role;
    }
    return null;
};

// Check if the user is authenticated based on JWT token expiration
export const isAuthenticated = () => {
    const token = localStorage.getItem('token');
    if (token) {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        return decoded.exp > currentTime;
    }
    return false;
};

// Login function to authenticate the user and store the token in localStorage
export const login = async (username, password) => {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.accessToken);
            toast.success('Logged in successfully!');
            return data;
        } else {
            throw new Error('Login failed');
        }
    } catch (error) {
        toast.error('Failed to log in.');
        throw error;
    }
};

// Logout function to remove the token from localStorage
export const logout = () => {
    localStorage.removeItem('token');
    toast.success('Logged out successfully!');
};

// Get the current user's information from the stored JWT token
export const getCurrentUser = () => {
    try {
        const token = localStorage.getItem('token');
        return token ? jwtDecode(token) : null;
    } catch (error) {
        return null;
    }
};

// Create an object containing all the exported functions
const authService = {
    getCurrentUserRole,
    isAuthenticated,
    login,
    logout,
    getCurrentUser,
};

// Export the object as the default export
export default authService;
