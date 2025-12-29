/**
 * File: client/src/features/auth/reducers/authSlice.js
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Centralizes auth state: user, token, tenantId, flags.
 * - Thunks:
 *   • loginUser: authenticates and persists session data.
 *   • logoutUser: clears session (storage + state).
 *   • refreshUser: obtains a new access token silently.
 * - Persistence: localStorage keys 'accessToken', 'tenantId', and 'user' (email+token).
 * - Security:
 *   • Prefer HttpOnly cookies for refresh tokens in production.
 *   • Frontend only stores access tokens + minimal context.
 * -----------------------------------------------------------------------------
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../../services/authService';

// Hydrate from storage
const storedUser = JSON.parse(localStorage.getItem('user'));
const storedToken = localStorage.getItem('accessToken');
const storedTenant = localStorage.getItem('tenantId');

const initialState = {
  user: storedUser || null,
  accessToken: storedToken || (storedUser ? storedUser.token : null),
  tenantId: storedTenant || null,
  isAuthenticated: !!storedToken || !!storedUser,
  isError: false,
  isSuccess: false,
  isLoading: false,
  message: ''
};

// Login
export const loginUser = createAsyncThunk('auth/login', async (credentials, thunkAPI) => {
  try {
    const payload = await authService.login(credentials);
    const { token, user, tenantId } = payload;

    if (token) localStorage.setItem('accessToken', token);
    if (tenantId) localStorage.setItem('tenantId', tenantId);
    if (user) localStorage.setItem('user', JSON.stringify({ email: user.email, token }));

    return payload;
  } catch (error) {
    const message =
      (error.response && error.response.data && error.response.data.message) ||
      error.message ||
      error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

// Logout
export const logoutUser = createAsyncThunk('auth/logout', async () => {
  await authService.logout();
  localStorage.removeItem('user');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('tenantId');
});

// Refresh (silent renew)
export const refreshUser = createAsyncThunk('auth/refresh', async (_, thunkAPI) => {
  try {
    const payload = await authService.refreshToken();
    const { token, user, tenantId } = payload;

    if (token) localStorage.setItem('accessToken', token);
    if (tenantId) localStorage.setItem('tenantId', tenantId);
    if (user) localStorage.setItem('user', JSON.stringify({ email: user.email, token }));

    return payload;
  } catch (error) {
    const message =
      (error.response && error.response.data && error.response.data.message) ||
      error.message ||
      error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

// Slice
export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    reset: (state) => {
      state.isLoading = false;
      state.isSuccess = false;
      state.isError = false;
      state.message = '';
    },
    forceLogout: (state) => {
      authService.logout();
      localStorage.clear();
      state.user = null;
      state.accessToken = null;
      state.tenantId = null;
      state.isAuthenticated = false;
    }
  },
  extraReducers: (builder) => {
    builder
      // login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.isError = false;
        state.isSuccess = false;
        state.message = '';
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isSuccess = true;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.accessToken = action.payload.token;
        state.tenantId = action.payload.tenantId;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
        state.user = null;
        state.accessToken = null;
        state.tenantId = null;
        state.isAuthenticated = false;
      })
      // logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null;
        state.accessToken = null;
        state.tenantId = null;
        state.isAuthenticated = false;
      })
      // refresh
      .addCase(refreshUser.fulfilled, (state, action) => {
        state.accessToken = action.payload.token;
        state.user = action.payload.user;
        state.tenantId = action.payload.tenantId;
        state.isAuthenticated = true;
        state.isError = false;
        state.message = '';
      })
      .addCase(refreshUser.rejected, (state, action) => {
        state.isAuthenticated = false;
        state.accessToken = null;
        state.user = null;
        state.tenantId = null;
        state.isError = true;
        state.message = action.payload;
      });
  }
});

export const { reset, forceLogout } = authSlice.actions;
export default authSlice.reducer;
