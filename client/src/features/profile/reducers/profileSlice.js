// ~/legal-doc-system/client/src/features/profile/reducers/profileSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { toast } from 'react-toastify';

// 📦 Async thunk: Fetch profile
export const fetchUserProfile = createAsyncThunk(
    'profile/fetchUserProfile',
    async (_, { rejectWithValue }) => {
        try {
            const response = await axios.get('/api/profile');
            return response.data;
        } catch (error) {
            const message =
                error?.response?.data?.message || error.message || 'Unable to fetch profile.';
            return rejectWithValue(message);
        }
    }
);

// ✏️ Async thunk: Update profile
export const updateUserProfile = createAsyncThunk(
    'profile/updateUserProfile',
    async (profileData, { rejectWithValue }) => {
        try {
            const response = await axios.put('/api/profile', profileData);
            toast.success('Profile updated successfully!');
            return response.data;
        } catch (error) {
            const message =
                error?.response?.data?.message || error.message || 'Unable to update profile.';
            toast.error(message);
            return rejectWithValue(message);
        }
    }
);

// 🧠 Initial state
const initialState = {
    userProfile: null,
    loading: false,
    error: null,
};

// 🧩 Profile slice
const profileSlice = createSlice({
    name: 'profile',
    initialState,
    reducers: {
        clearProfileError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // 📥 Fetch
            .addCase(fetchUserProfile.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchUserProfile.fulfilled, (state, action) => {
                state.loading = false;
                state.userProfile = action.payload;
            })
            .addCase(fetchUserProfile.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || 'Failed to load profile.';
            })

            // 💾 Update
            .addCase(updateUserProfile.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(updateUserProfile.fulfilled, (state, action) => {
                state.loading = false;
                state.userProfile = action.payload;
            })
            .addCase(updateUserProfile.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || 'Update failed.';
            });
    },
});

export const { clearProfileError } = profileSlice.actions;

export default profileSlice.reducer;
