import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { searchAll } from '../services/searchService';

// Minimal, always-safe initial state
const initialState = {
  query: '',
  results: [],
  loading: false,
  error: null,
};

// Async thunk to hit backend. Falls back to empty here; component can add demo.
export const performSearch = createAsyncThunk(
  'search/performSearch',
  async (query, { getState, rejectWithValue }) => {
    try {
      const token = getState()?.auth?.token || localStorage.getItem('token');
      const { results } = await searchAll(query, token);
      return { query, results };
    } catch (err) {
      // surface typed code so component can decide on demo fallback
      return rejectWithValue({ message: err?.message || 'Search failed', status: err?.status });
    }
  }
);

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    setSearchQuery(state, action) {
      state.query = action.payload ?? '';
    },
    setSearchResults(state, action) {
      state.results = Array.isArray(action.payload) ? action.payload : [];
    },
    setLoading(state, action) {
      state.loading = !!action.payload;
    },
    setError(state, action) {
      state.error = action.payload ?? null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(performSearch.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.results = []; // clear for new run
      })
      .addCase(performSearch.fulfilled, (state, action) => {
        state.loading = false;
        state.error = null;
        state.query = action.payload?.query ?? state.query;
        state.results = Array.isArray(action.payload?.results) ? action.payload.results : [];
      })
      .addCase(performSearch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Search failed';
      });
  },
});

export const { setSearchQuery, setSearchResults, setLoading, setError } = searchSlice.actions;
export default searchSlice.reducer;
