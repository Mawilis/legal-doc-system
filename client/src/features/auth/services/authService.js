// ~/legal-doc-system/client/src/features/auth/services/authService.js
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';  // Note: Ensure you are using correct syntax here. It should be like this:


const api = axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL,
});

export const login = async (username, password) => {
    try {
        const response = await api.post('/auth/login', { username, password });
        if (response.status === 200) {
            const { accessToken } = response.data;
            localStorage.setItem('token', accessToken);
            return jwtDecode(accessToken);
        }
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
};

export const logout = () => {
    localStorage.removeItem('token');
};

const authService = {
    login,
    logout,
};

export default authService;
