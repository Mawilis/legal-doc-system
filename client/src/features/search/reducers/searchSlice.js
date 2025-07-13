// ~/legal-doc-system/client/src/features/search/reducers/searchSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    searchQuery: '',
    searchResults: [],
    loading: false,
    error: null,
};

const searchSlice = createSlice({
    name: 'search',
    initialState,
    reducers: {
        setSearchQuery: (state, action) => {
            state.searchQuery = action.payload;
        },
        setSearchResults: (state, action) => {
            state.searchResults = action.payload;
        },
        setLoading: (state, action) => {
            state.loading = action.payload;
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
    },
});

export const { setSearchQuery, setSearchResults, setLoading, setError } = searchSlice.actions;
export default searchSlice.reducer;
