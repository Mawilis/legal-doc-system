// ~/legal-doc-system/client/src/features/dashboard/reducers/dashboardSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// ✅ Define the API base URL from environment variables (fallback to localhost)
const API_URL = process.env.REACT_APP_API_BASE_URL || 'https://localhost:3001/api';

// ✅ Async thunk to fetch dashboard data
export const fetchDashboardData = createAsyncThunk(
    'dashboard/fetchDashboardData',
    async (_, { rejectWithValue }) => {
        try {
            console.log('[Dashboard] Fetching dashboard metrics...');
            const response = await axios.get(`${API_URL}/dashboard`, { withCredentials: true });

            // ✅ Validate response format
            if (!response.data || !response.data.metrics || !response.data.charts) {
                throw new Error('Invalid response format from API');
            }

            console.log('[Dashboard] Data successfully fetched:', response.data);
            return response.data;
        } catch (error) {
            console.error('[Dashboard] Error fetching data:', error);

            // ✅ Capture specific backend errors or fallback to generic error
            if (error.response && error.response.data) {
                return rejectWithValue(error.response.data.message || 'Server Error');
            } else {
                return rejectWithValue(error.message || 'Network Error');
            }
        }
    }
);

// ✅ Initial state with defined structure
const initialState = {
    metrics: {
        totalDocuments: 0,
        totalUsers: 0,
        monthlyGrowth: 0,
        activeCases: 0, // Added for expansion
        resolvedCases: 0, // Added for future analytics
    },
    charts: {
        documentsOverTime: [], // [{ month: 'Jan', documents: 10 }, ...]
        userActivity: [], // [{ user: 'John', actions: 5 }, ...]
        serviceTracking: [], // Track document movement for legal cases
    },
    loading: false,
    error: null,
};

// ✅ Create a Redux slice with robust handling
const dashboardSlice = createSlice({
    name: 'dashboard',
    initialState,
    reducers: {
        // ✅ Add reducers for real-time updates if needed (future-proof)
        resetDashboardError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDashboardData.pending, (state) => {
                console.log('[Dashboard] Fetching data...');
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchDashboardData.fulfilled, (state, action) => {
                console.log('[Dashboard] Data successfully updated.');
                state.loading = false;
                state.metrics = action.payload.metrics;
                state.charts = action.payload.charts || {
                    documentsOverTime: [],
                    userActivity: [],
                    serviceTracking: [],
                };
            })
            .addCase(fetchDashboardData.rejected, (state, action) => {
                console.error('[Dashboard] Error fetching data:', action.payload);
                state.loading = false;
                state.error = action.payload || 'Failed to fetch dashboard data';
            });
    },
});

// ✅ Export actions and reducer
export const { resetDashboardError } = dashboardSlice.actions;
export default dashboardSlice.reducer;
