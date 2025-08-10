// ~/legal-doc-system/client/src/features/auth/reducers/authSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../../services/authService';
import { toast } from 'react-toastify';

// Load from localStorage
const savedUser = localStorage.getItem('user');
const savedToken = localStorage.getItem('token');

// Initial state
const initialState = {
    user: savedUser ? JSON.parse(savedUser) : null,
    token: savedToken || null,
    loading: false,
    error: null,
};

// ✅ Async Thunks

// Load user from localStorage on app load
export const loadUser = createAsyncThunk(
    'auth/loadUser',
    async (_, { rejectWithValue }) => {
        try {
            const user = localStorage.getItem('user');
            const token = localStorage.getItem('token');

            if (user && token) {
                authService.setAuthToken(token);
                return { user: JSON.parse(user), token };
            }

            return rejectWithValue('No session found');
        } catch (err) {
            return rejectWithValue('Failed to load session');
        }
    }
);

// Login
export const loginUser = createAsyncThunk(
    'auth/loginUser',
    async ({ email, password }, { rejectWithValue }) => {
        try {
            const response = await authService.login(email, password);

            localStorage.setItem('user', JSON.stringify(response.user));
            localStorage.setItem('token', response.token);
            authService.setAuthToken(response.token);

            return response;
        } catch (err) {
            return rejectWithValue(err.message || 'Login failed. Please try again.');
        }
    }
);

// Register
export const registerUser = createAsyncThunk(
    'auth/registerUser',
    async (formData, { rejectWithValue }) => {
        try {
            const response = await authService.register(formData);
            return response;
        } catch (err) {
            return rejectWithValue(err.message || 'Registration failed. Please try again.');
        }
    }
);

// ✅ Slice
const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logoutUser: (state) => {
            state.user = null;
            state.token = null;
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            authService.setAuthToken(null);
            toast.success('✅ Logged out successfully');
        },
        clearAuthError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(loadUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(loadUser.fulfilled, (state, action) => {
                state.loading = false;
                state.user = action.payload.user;
                state.token = action.payload.token;
            })
            .addCase(loadUser.rejected, (state, action) => {
                state.loading = false;
                state.user = null;
                state.token = null;
                state.error = action.payload;
            })
            .addCase(loginUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(loginUser.fulfilled, (state, action) => {
                state.loading = false;
                state.user = action.payload.user;
                state.token = action.payload.token;
                toast.success(`🎉 Welcome back, ${action.payload.user.name}!`);
            })
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
                toast.error(`❌ ${action.payload}`);
            })
            .addCase(registerUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(registerUser.fulfilled, (state) => {
                state.loading = false;
                toast.success('🎉 Registration successful!');
            })
            .addCase(registerUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
                toast.error(`❌ ${action.payload}`);
            });
    },
});

// ✅ Exports
export const { logoutUser, clearAuthError } = authSlice.actions;
export default authSlice.reducer;
