// client/src/services/userService.js
import axios from 'axios';

export const updateUserProfile = async (userData) => {
    try {
        const response = await axios.put('/api/users/profile', userData);
        return response.data;
    } catch (error) {
        console.error('Failed to update user profile', error);
    }
};

export const changeUserPassword = async (passwordData) => {
    try {
        const response = await axios.put('/api/users/password', passwordData);
        return response.data;
    } catch (error) {
        console.error('Failed to change user password', error);
    }
};

export const getUserDetails = async () => {
    try {
        const response = await axios.get('/api/users/me');
        return response.data;
    } catch (error) {
        console.error('Failed to fetch user details', error);
    }
};
