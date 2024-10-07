// src/services/authService.js

import jwtDecode from 'jwt-decode';
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

export const isAuthenticated = () => {
    const token = localStorage.getItem('token');
    if (token) {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        return decoded.exp > currentTime;
    }
    return false;
};

export const login = async (username, password) => {
    try {
        // Replace with your API call
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

export const logout = () => {
    localStorage.removeItem('token');
    toast.success('Logged out successfully!');
};

export const getCurrentUser = () => {
    try {
        const token = localStorage.getItem('token');
        return token ? jwtDecode(token) : null;
    } catch (error) {
        return null;
    }
};

export default { getCurrentUserRole, isAuthenticated, login, logout, getCurrentUser };
