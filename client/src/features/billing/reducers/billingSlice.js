// ~/legal-doc-system/client/src/features/billing/reducers/billingSlice.js

import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    invoices: [],
    pendingPayments: [],
    billingDetails: {},
};

const billingSlice = createSlice({
    name: 'billing',
    initialState,
    reducers: {
        addInvoice: (state, action) => {
            state.invoices.push(action.payload);
        },
        updatePendingPayment: (state, action) => {
            state.pendingPayments.push(action.payload);
        },
        setBillingDetails: (state, action) => {
            state.billingDetails = action.payload;
        },
    },
});

export const { addInvoice, updatePendingPayment, setBillingDetails } = billingSlice.actions;
export default billingSlice.reducer;
