// ~/legal-doc-system/client/src/features/movementTracking/reducers/movementTrackingSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    movements: [],
    couriers: [],
};

const movementTrackingSlice = createSlice({
    name: 'movementTracking',
    initialState,
    reducers: {
        logMovement: (state, action) => {
            state.movements.push(action.payload);
        },
        addCourierInfo: (state, action) => {
            state.couriers.push(action.payload);
        },
    },
});

export const { logMovement, addCourierInfo } = movementTrackingSlice.actions;
export default movementTrackingSlice.reducer;
