// ~/legal-doc-system/client/src/features/analytics/reducers/analyticsSlice.js

import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    userActivity: [],
};

const analyticsSlice = createSlice({
    name: "analytics",
    initialState,
    reducers: {
        logActivity: (state, action) => {
            state.userActivity.push(action.payload);
        },
        clearActivity: (state) => {
            state.userActivity = [];
        },
    },
});

export const { logActivity, clearActivity } = analyticsSlice.actions;
export default analyticsSlice.reducer;