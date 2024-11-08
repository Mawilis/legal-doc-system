import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../../services/authService'; // Corrected path

// Define initial state
const initialState = {
    user: null,
    token: null,
    loading: false,
    error: null,
};

// Async thunk to login user
export const loginUser = createAsyncThunk('auth/loginUser', async ({ email, password }, { rejectWithValue }) => {
    try {
        const response = await authService.login(email, password);
        authService.setAuthToken(response.token);
        console.log('Login successful:', response); // Log the response
        return response;
    } catch (err) {
        console.error('Login failed:', err.message); // Log the error
        return rejectWithValue(err.message);
    }
});

// Async thunk to verify token
export const verifyUserToken = createAsyncThunk('auth/verifyUserToken', async (_, { getState, rejectWithValue }) => {
    try {
        const { auth } = getState();
        const response = await authService.verifyToken(auth.token);
        console.log('Token verification successful:', response); // Log the response
        return response;
    } catch (err) {
        console.error('Token verification failed:', err.message); // Log the error
        return rejectWithValue(err.message);
    }
});

// Create auth slice
const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logoutUser: (state) => {
            console.log('Logging out user:', state.user); // Log the user before logout
            state.user = null;
            state.token = null;
            authService.setAuthToken(null);
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
                console.log('User logged in:', state.user); // Log the user after login
            })
            .addCase(loginUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || action.error.message;
                console.error('Login error state:', state.error); // Log the error state
            })
            .addCase(verifyUserToken.fulfilled, (state, action) => {
                state.user = action.payload.user;
                state.token = action.payload.token;
                console.log('Token verified:', state.user); // Log the user after token verification
            })
            .addCase(verifyUserToken.rejected, (state, action) => {
                state.error = action.payload || action.error.message;
                console.error('Token verification error:', state.error); // Log the error state
            });
    },
});

// Export actions
export const { logoutUser } = authSlice.actions;

// Export reducer
export default authSlice.reducer;
