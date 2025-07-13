// ~/legal-doc-system/client/src/features/communication/reducers/communicationSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    smsLogs: [],
    emailLogs: [],
    notifications: [],
};

const communicationSlice = createSlice({
    name: 'communication',
    initialState,
    reducers: {
        sendSMS: (state, action) => {
            state.smsLogs.push(action.payload);
        },
        sendEmail: (state, action) => {
            state.emailLogs.push(action.payload);
        },
        addNotification: (state, action) => {
            state.notifications.push(action.payload);
        },
    },
});

export const { sendSMS, sendEmail, addNotification } = communicationSlice.actions;
export default communicationSlice.reducer;
