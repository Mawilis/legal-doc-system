// ~/legal-doc-system/client/src/features/profile/reducers/profileSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk to fetch user profile
export const fetchUserProfile = createAsyncThunk(
    'profile/fetchUserProfile',
    async (_, { rejectWithValue }) => {
        try {
            const response = await axios.get('/api/profile');
            return response.data; // Assuming it returns the user profile object
        } catch (error) {
            if (error.response && error.response.data && error.response.data.message) {
                return rejectWithValue(error.response.data.message);
            } else {
                return rejectWithValue(error.message);
            }
        }
    }
);

// Async thunk to update user profile
export const updateUserProfile = createAsyncThunk(
    'profile/updateUserProfile',
    async (profileData, { rejectWithValue }) => {
        try {
            const response = await axios.put('/api/profile', profileData);
            return response.data; // Assuming it returns the updated profile object
        } catch (error) {
            if (error.response && error.response.data && error.response.data.message) {
                return rejectWithValue(error.response.data.message);
            } else {
                return rejectWithValue(error.message);
            }
        }
    }
);

const profileSlice = createSlice({
    name: 'profile',
    initialState: {
        userProfile: null,
        loading: false,
        error: null,
    },
    reducers: {
        // Define synchronous reducers if needed
    },
    extraReducers: (builder) => {
        builder
            // Fetch User Profile
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
                state.error = action.payload || 'Failed to fetch user profile';
            })

            // Update User Profile
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
                state.error = action.payload || 'Failed to update user profile';
            });
    },
});

export default profileSlice.reducer;
