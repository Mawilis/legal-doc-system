// ~/legal-doc-system/client/src/features/dashboard/reducers/dashboardSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk to fetch dashboard data
export const fetchDashboardData = createAsyncThunk(
    'dashboard/fetchDashboardData',
    async (_, { rejectWithValue }) => {
        try {
            const response = await axios.get('/api/dashboard'); // Ensure this endpoint exists on your backend
            return response.data;
        } catch (error) {
            if (error.response && error.response.data) {
                return rejectWithValue(error.response.data.message);
            } else {
                return rejectWithValue(error.message);
            }
        }
    }
);

const dashboardSlice = createSlice({
    name: 'dashboard',
    initialState: {
        metrics: {
            totalDocuments: 0,
            totalUsers: 0,
            monthlyGrowth: 0,
            // Add more metrics as needed
        },
        charts: {
            documentsOverTime: [], // [{ month: 'Jan', documents: 10 }, ...]
            userActivity: [], // [{ user: 'John', actions: 5 }, ...]
            // Add more chart data as needed
        },
        loading: false,
        error: null,
    },
    reducers: {
        // Define synchronous reducers if needed
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDashboardData.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchDashboardData.fulfilled, (state, action) => {
                state.loading = false;
                state.metrics = action.payload.metrics;
                state.charts = action.payload.charts;
            })
            .addCase(fetchDashboardData.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload || 'Failed to fetch dashboard data';
            });
    },
});

export default dashboardSlice.reducer;
