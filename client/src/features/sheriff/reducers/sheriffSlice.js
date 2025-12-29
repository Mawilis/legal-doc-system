import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const initialState = {
  breaches: [],
  replayPath: [],
  activeReplayUser: null,
  loading: false,
  error: null,
};

export const fetchBreachLogs = createAsyncThunk(
  'sheriff/fetchBreachLogs',
  async (_, { rejectWithValue }) => {
    try {
      const res = await fetch('/api/sheriff/breaches');
      if (!res.ok) throw new Error('Failed to fetch breach logs');
      return await res.json();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const sheriffSlice = createSlice({
  name: 'sheriff',
  initialState,
  reducers: {
    setReplayPath(state, action) { state.replayPath = action.payload || []; },
    clearReplay(state) { state.replayPath = []; state.activeReplayUser = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBreachLogs.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchBreachLogs.fulfilled, (state, action) => { state.loading = false; state.breaches = action.payload || []; })
      .addCase(fetchBreachLogs.rejected, (state, action) => { state.loading = false; state.error = action.payload || 'Error'; });
  }
});

export const { setReplayPath, clearReplay } = sheriffSlice.actions;
export default sheriffSlice.reducer;
