import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import http from '../../../services/http';

export const fetchDashboard = createAsyncThunk(
  'dashboard/fetch',
  async (_, thunkAPI) => {
    try {
      const { data } = await http.get('/dashboard');
      return data;
    } catch (err) {
      return thunkAPI.rejectWithValue(err.response?.data || err.message);
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: {
    data: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboard.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to load dashboard';
      });
  },
});

export default dashboardSlice.reducer;
