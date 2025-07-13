// ~/legal-doc-system/client/src/features/serviceQueue/reducers/serviceQueueSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    serviceQueue: [],
    attemptedServices: [],
    successfulServices: [],
};

const serviceQueueSlice = createSlice({
    name: 'serviceQueue',
    initialState,
    reducers: {
        addServiceToQueue: (state, action) => {
            state.serviceQueue.push(action.payload);
        },
        logAttemptedService: (state, action) => {
            state.attemptedServices.push(action.payload);
        },
        markServiceSuccess: (state, action) => {
            state.successfulServices.push(action.payload);
        },
    },
});

export const { addServiceToQueue, logAttemptedService, markServiceSuccess } = serviceQueueSlice.actions;
export default serviceQueueSlice.reducer;
