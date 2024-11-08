// ~/legal-doc-system/client/src/services/authService.js

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api/auth';

const setAuthToken = (token) => {
    if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete axios.defaults.headers.common['Authorization'];
    }
};

// User login
const login = async (email, password) => {
    const response = await axios.post(`${API_URL}/login`, { email, password });
    return response.data;
};

// User registration
const register = async (userData) => {
    const response = await axios.post(`${API_URL}/register`, userData);
    return response.data;
};

// User logout
const logout = async () => {
    await axios.post(`${API_URL}/logout`);
};

// Verify user token
const verifyToken = async (token) => {
    const response = await axios.get(`${API_URL}/verify-token`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    return response.data;
};

const authService = {
    login,
    register,
    logout,
    verifyToken,
    setAuthToken,
};

export default authService;
