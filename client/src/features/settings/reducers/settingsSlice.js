// ~/legal-doc-system/client/src/features/settings/reducers/settingsSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    darkMode: false,
    language: 'en',
};

const settingsSlice = createSlice({
    name: 'settings',
    initialState,
    reducers: {
        toggleDarkMode: (state) => {
            state.darkMode = !state.darkMode;
        },
        setLanguage: (state, action) => {
            state.language = action.payload;
        },
    },
});

export const { toggleDarkMode, setLanguage } = settingsSlice.actions;
export default settingsSlice.reducer;
