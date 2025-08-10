// ~/client/src/features/sheriff/reducers/sheriffSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios'; // Assuming a pre-configured axios instance
import { toast } from 'react-toastify';

// --- Initial State ---
const initialState = {
    breaches: [],
    replayPath: [],
    activeReplayUser: null,
    loading: false,
    error: null,
};

// --- Async Thunks ---

/**
 * Fetches all historical geofence breach logs from the server.
 */
export const fetchBreachLogs = createAsyncThunk(
    'sheriff/fetchBreachLogs',
    async (_, { rejectWithValue }) => {
        try {
            const res = await axios.get('/api/geofence/breaches'); // This route needs to be created on the backend
            return res.data.data; // Assuming the API returns { success, data }
        } catch (err) {
            const message = err.response?.data?.message || 'Failed to fetch breach logs';
            toast.error(message);
            return rejectWithValue(message);
        }
    }
);

// --- Redux Slice Definition ---
const sheriffSlice = createSlice({
    name: 'sheriff',
    initialState,
    reducers: {
        /**
         * Sets the replay path and active user in the state.
         * @param {object} state - The current Redux state.
         * @param {object} action - The action containing the path and userId.
         */
        setReplayPath: (state, action) => {
            state.replayPath = action.payload.path;
            state.activeReplayUser = action.payload.userId;
        },
        /**
         * Clears the replay path and active user from the state.
         */
        clearReplay: (state) => {
            state.replayPath = [];
            state.activeReplayUser = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchBreachLogs.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchBreachLogs.fulfilled, (state, action) => {
                state.breaches = action.payload;
                state.loading = false;
            })
            .addCase(fetchBreachLogs.rejected, (state, action) => {
                state.error = action.payload;
                state.loading = false;
            });
    },
});

export const { setReplayPath, clearReplay } = sheriffSlice.actions;
export default sheriffSlice.reducer;
