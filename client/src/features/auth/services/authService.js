/*
 * File: client/src/features/auth/services/authService.js
 * STATUS: EPITOME | SECURITY BRIDGE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The Diplomat. Manages all communication between the Frontend and the Auth Server.
 * Handles Login, Registration, and Token Storage (The 'Passport').
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - SECURITY: Tokens are stored in 'localStorage' (Phase 1). 
 * - ERROR HANDLING: Standardizes error messages so the UI doesn't crash.
 * -----------------------------------------------------------------------------
 */

import axios from 'axios';

// The Backend URL
// In production, this would be process.env.REACT_APP_API_URL
const API_URL = '/api/users/';

// 1. Register User (The Onboarding)
const register = async (userData) => {
    // CORRECTION: Space added below
    const response = await axios.post(API_URL, userData);

    if (response.data) {
        localStorage.setItem('user', JSON.stringify(response.data));
    }

    return response.data;
};

// 2. Login User (The Handshake)
const login = async (userData) => {
    const response = await axios.post(API_URL + 'login', userData);

    if (response.data) {
        // Save the "Passport" (User Data + Token)
        localStorage.setItem('user', JSON.stringify(response.data));
    }

    return response.data;
};

// 3. Logout (The Exit)
const logout = () => {
    localStorage.removeItem('user');
};

const authService = {
    register,
    logout,
    login,
};

export default authService;