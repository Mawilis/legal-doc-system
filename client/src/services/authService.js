import axios from 'axios';

// Get API URL from environment variable (or use the fallback)
const API_URL = process.env.REACT_APP_API_BASE_URL;

// Log the API URL for verification
console.log('[authService] API_URL:', API_URL);

// Create a custom Axios instance
const axiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 10000, // Timeout after 10 seconds
    withCredentials: true, // Send cookies with requests
});

// Function to set the authorization token in headers and local storage
const setAuthToken = (token) => {
    if (token) {
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('token', token);
    } else {
        delete axiosInstance.defaults.headers.common['Authorization'];
        localStorage.removeItem('token');
    }
};

// Function to handle Axios errors
const handleAxiosError = (error) => {
    if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('[authService] Response Error:', {
            data: error.response.data,
            status: error.response.status,
            headers: error.response.headers,
        });

        // Check for specific error messages (e.g., related to credentials)
        if (
            error.response.status === 401 &&
            (error.response.data.message.includes('Invalid credentials') ||
                error.response.data.message.includes('Unauthorized'))
        ) {
            throw new Error('Invalid credentials. Please try again.');
        } else {
            // Generic error handling
            throw new Error(
                error.response.data.message ||
                'An error occurred while processing your request.'
            );
        }
    } else if (error.request) {
        // The request was made but no response was received
        console.error('[authService] No Response Received:', error.request);
        throw new Error(
            'Server could not be reached. Please check your network connection or server status.'
        );
    } else {
        // Something happened in setting up the request that triggered an Error
        console.error('[authService] Request Configuration Error:', error.message);
        throw new Error('An unexpected error occurred. Please try again.');
    }
};

// Login function
const login = async (email, password) => {
    try {
        console.log('[authService] Attempting login with email:', email);
        const response = await axiosInstance.post('/login', {
            email,
            password,
        });
        setAuthToken(response.data.token);
        console.log('[authService] Login successful:', response.data);
        return response.data;
    } catch (error) {
        console.error('[authService] Login failed:', error);
        handleAxiosError(error);
    }
};

// Logout function
const logout = async () => {
    try {
        console.log('[authService] Logging out...');
        await axiosInstance.post('/logout'); // Make sure you have a /logout route on your backend
        setAuthToken(null);
        console.log('[authService] Logout successful.');
    } catch (error) {
        console.error('[authService] Logout failed:', error);
        handleAxiosError(error);
    }
};

// Register function
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

// Verify token function
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

// Refresh token function
const refreshToken = async (refreshTokenValue) => {
    try {
        console.log('[authService] Refreshing token...');
        const response = await axiosInstance.post('/refresh-token', {
            refreshToken: refreshTokenValue,
        });
        setAuthToken(response.data.token);
        console.log('[authService] Token refreshed:', response.data);
        return response.data.token;
    } catch (error) {
        console.error('[authService] Token refresh failed:', error);
        handleAxiosError(error);
    }
};

// Forgot password function
const forgotPassword = async (email) => {
    try {
        console.log('[authService] Requesting password reset for email:', email);
        const response = await axiosInstance.post('/forgot-password', {
            email,
        });
        console.log('[authService] Password reset email sent:', response.data);
        return response.data;
    } catch (error) {
        console.error('[authService] Forgot password request failed:', error);
        handleAxiosError(error);
    }
};

// Reset password function
const resetPassword = async (token, newPassword) => {
    try {
        console.log('[authService] Resetting password with token:', token);
        const response = await axiosInstance.post(`/reset-password/${token}`, {
            password: newPassword,
        });
        console.log('[authService] Password reset successful:', response.data);
        return response.data;
    } catch (error) {
        console.error('[authService] Password reset failed:', error);
        handleAxiosError(error);
    }
};

// Handle expired tokens globally using an interceptor
axiosInstance.interceptors.response.use(
    (response) => response, // Return responses directly
    (error) => {
        if (
            error.response?.status === 401 && // Check for 401 Unauthorized
            error.config && // Check if config exists
            !error.config.__isRetryRequest // Check if it's not already a retry
        ) {
            console.warn('[authService] 401 error. Attempting to refresh token...');
            // Try to refresh the token
            return refreshToken(localStorage.getItem('refreshToken'))
                .then((newToken) => {
                    console.log('[authService] Token refreshed successfully.');
                    error.config.__isRetryRequest = true; // Mark request as a retry
                    error.config.headers['Authorization'] = `Bearer ${newToken}`;
                    return axiosInstance(error.config); // Retry the original request
                })
                .catch((refreshError) => {
                    console.error('[authService] Failed to refresh token:', refreshError);
                    // Handle refresh token failure (e.g., redirect to login)
                    setAuthToken(null);
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                });
        }
        return Promise.reject(error); // Reject other errors
    }
);

// Export all authentication services as an object
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