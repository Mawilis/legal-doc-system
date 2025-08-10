import axios from 'axios';

const API_URL = process.env.REACT_APP_API_BASE_URL;
console.log('[authService] API_URL:', API_URL);

const axiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    withCredentials: true,
});

const setAuthToken = (token) => {
    if (token) {
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('token', token);
    } else {
        delete axiosInstance.defaults.headers.common['Authorization'];
        localStorage.removeItem('token');
    }
};

const handleAxiosError = (error) => {
    if (error.response) {
        console.error('[authService] Response Error:', {
            data: error.response.data,
            status: error.response.status,
            headers: error.response.headers,
        });

        if (
            error.response.status === 401 &&
            (error.response.data.message?.includes('Invalid credentials') ||
                error.response.data.message?.includes('Unauthorized'))
        ) {
            throw new Error('Invalid credentials. Please try again.');
        } else {
            throw new Error(
                error.response.data.message || 'An error occurred while processing your request.'
            );
        }
    } else if (error.request) {
        console.error('[authService] No Response Received:', error.request);
        throw new Error('Server could not be reached. Please check your network connection.');
    } else {
        console.error('[authService] Request Configuration Error:', error.message);
        throw new Error('An unexpected error occurred. Please try again.');
    }
};

const login = async (email, password) => {
    try {
        console.log('[authService] Attempting login with email:', email);
        const response = await axiosInstance.post('/login', { email, password });

        setAuthToken(response.data.token);

        // ✅ Save refresh token
        if (response.data.refreshToken) {
            localStorage.setItem('refreshToken', response.data.refreshToken);
        }

        console.log('[authService] Login successful:', response.data);
        return response.data;
    } catch (error) {
        console.error('[authService] Login failed:', error);
        handleAxiosError(error);
    }
};

const logout = async () => {
    try {
        console.log('[authService] Logging out...');
        await axiosInstance.post('/logout');
        setAuthToken(null);
        localStorage.removeItem('refreshToken'); // ✅ Clear refresh token
        console.log('[authService] Logout successful.');
    } catch (error) {
        console.error('[authService] Logout failed:', error);
        handleAxiosError(error);
    }
};

const register = async (userData) => {
    try {
        console.log('[authService] Registering new user:', userData.email);
        const response = await axiosInstance.post('/register', userData);
        console.log('[authService] Registration successful. User data:', response.data);
        return response.data;
    } catch (error) {
        console.error('[authService] Registration failed:', error);
        handleAxiosError(error);
    }
};

const verifyToken = async () => {
    const token = localStorage.getItem('token');
    if (token) {
        setAuthToken(token);
        try {
            console.log('[authService] Verifying token...');
            const response = await axiosInstance.get('/verify-token');
            console.log('[authService] Token verified:', response.data);
            return response.data;
        } catch (error) {
            console.error('[authService] Token verification failed:', error);
            setAuthToken(null);
            handleAxiosError(error);
        }
    } else {
        console.warn('[authService] No token found for verification.');
    }
    return null;
};

const refreshToken = async (refreshTokenValue) => {
    try {
        console.log('[authService] Refreshing token...');
        const response = await axiosInstance.post('/refresh-token', {
            refreshToken: refreshTokenValue,
        });
        setAuthToken(response.data.token);

        if (response.data.refreshToken) {
            localStorage.setItem('refreshToken', response.data.refreshToken);
        }

        console.log('[authService] Token refreshed:', response.data);
        return response.data.token;
    } catch (error) {
        console.error('[authService] Token refresh failed:', error);
        setAuthToken(null);
        localStorage.removeItem('refreshToken');
        handleAxiosError(error);
    }
};

const forgotPassword = async (email) => {
    try {
        console.log('[authService] Requesting password reset for:', email);
        const response = await axiosInstance.post('/forgot-password', { email });
        return response.data;
    } catch (error) {
        handleAxiosError(error);
    }
};

const resetPassword = async (token, newPassword) => {
    try {
        const response = await axiosInstance.post(`/reset-password/${token}`, {
            password: newPassword,
        });
        return response.data;
    } catch (error) {
        handleAxiosError(error);
    }
};

// Interceptor for auto-refresh logic
axiosInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        if (
            error.response?.status === 401 &&
            error.config &&
            !error.config.__isRetryRequest
        ) {
            const storedRefreshToken = localStorage.getItem('refreshToken');
            if (!storedRefreshToken) {
                console.warn('[authService] No refresh token available.');
                return Promise.reject(error);
            }

            console.warn('[authService] 401 error. Attempting to refresh token...');
            return refreshToken(storedRefreshToken)
                .then((newToken) => {
                    error.config.__isRetryRequest = true;
                    error.config.headers['Authorization'] = `Bearer ${newToken}`;
                    return axiosInstance(error.config);
                })
                .catch((refreshError) => {
                    console.error('[authService] Token refresh failed:', refreshError);
                    setAuthToken(null);
                    localStorage.removeItem('refreshToken');
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                });
        }

        return Promise.reject(error);
    }
);

const authService = {
    login,
    logout,
    register,
    verifyToken,
    refreshToken,
    forgotPassword,
    resetPassword,
    setAuthToken,
};

export default authService;
