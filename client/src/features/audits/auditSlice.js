/**
 * File: client/src/features/audits/auditSlice.js
 * -----------------------------------------------------------------------------
 * STATUS: PRODUCTION-READY | Forensic State Management
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Manages the state of the Audit/Compliance logs in Redux.
 * - Handles fetching, filtering, and live socket updates.
 * -----------------------------------------------------------------------------
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async Thunk: Fetch Logs from API
export const fetchAudits = createAsyncThunk(
    'audits/fetchAudits',
    async ({ page = 1, limit = 50, filters = {} }, thunkAPI) => {
        try {
            // Build query string
            const params = new URLSearchParams({ page, limit, ...filters });
            const res = await axios.get(`/api/audits?${params}`);
            return res.data; // Expected { success: true, data: [], pagination: {} }
        } catch (error) {
            return thunkAPI.rejectWithValue(error.response?.data?.message || 'Failed to fetch audits');
        }
    }
);

const auditSlice = createSlice({
    name: 'audits',
    initialState: {
        logs: [],
        total: 0,
        page: 1,
        loading: false,
        error: null,
    },
    reducers: {
        // Socket Action: Prepend new log to the top of the list
        addLiveLog: (state, action) => {
            state.logs.unshift(action.payload);
            if (state.logs.length > 100) state.logs.pop(); // Keep memory usage low
            state.total += 1;
        },
        clearAudits: (state) => {
            state.logs = [];
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchAudits.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchAudits.fulfilled, (state, action) => {
                state.loading = false;
                state.logs = action.payload.data;
                state.total = action.payload.pagination?.total || 0;
                state.page = action.payload.pagination?.page || 1;
            })
            .addCase(fetchAudits.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

export const { addLiveLog, clearAudits } = auditSlice.actions;
export default auditSlice.reducer;