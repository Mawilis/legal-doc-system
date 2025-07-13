import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../../services/authService';

const initialState = {
    user: null,
    token: null,
    loading: false,
    error: null,
};

export const loginUser = createAsyncThunk(
    'auth/loginUser',
    async ({ email, password }, { rejectWithValue }) => {
        try {
            const response = await authService.login(email, password);
            return response;
        } catch (err) {
            return rejectWithValue(err.message || 'Login failed. Please try again.'); // Use err.message for more specific error messages
        }
    }
);

export const registerUser = createAsyncThunk(
    'auth/registerUser',
    async (formData, { rejectWithValue }) => {
        try {
            const response = await authService.register(formData);
            return response;
        } catch (err) {
            return rejectWithValue(err.message || 'Registration failed. Please try again.'); // Use err.message
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logoutUser: (state) => {
            state.user = null;
            state.token = null;
            authService.setAuthToken(null);
        },
        clearAuthError: (state) => { // Add clearAuthError reducer
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(loginUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(loginUser.fulfilled, (state, action) => {
                state.loading = false;
                state.user = action.payload.user;
                state.token = action.payload.token;
            })
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(registerUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(registerUser.fulfilled, (state) => {
                state.loading = false;
            })
            .addCase(registerUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

export const { logoutUser, clearAuthError } = authSlice.actions; // Export clearAuthError
export default authSlice.reducer;