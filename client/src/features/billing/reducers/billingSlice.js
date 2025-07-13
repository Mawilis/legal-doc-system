// ~/legal-doc-system/client/src/features/billing/reducers/billingSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {
    fetchInvoices as fetchInvoicesAPI,
    fetchPendingPayments as fetchPendingPaymentsAPI,
    fetchBillingDetails as fetchBillingDetailsAPI,
    createInvoice as createInvoiceAPI,
    processPayment as processPaymentAPI,
} from '../billingService'; // Corrected path to billingService.js

// Initial state
const initialState = {
    invoices: [],
    pendingPayments: [],
    billingDetails: {},
    loading: false,
    success: null, // To store success messages
    error: null,   // To store error messages
};

// Thunk: Fetch Invoices
export const fetchInvoices = createAsyncThunk(
    'billing/fetchInvoices',
    async (_, { rejectWithValue }) => {
        try {
            const response = await fetchInvoicesAPI();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Failed to fetch invoices.');
        }
    }
);

// Thunk: Fetch Pending Payments
export const fetchPendingPayments = createAsyncThunk(
    'billing/fetchPendingPayments',
    async (_, { rejectWithValue }) => {
        try {
            const response = await fetchPendingPaymentsAPI();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Failed to fetch pending payments.');
        }
    }
);

// Thunk: Fetch Billing Details
export const fetchBillingDetails = createAsyncThunk(
    'billing/fetchBillingDetails',
    async (_, { rejectWithValue }) => {
        try {
            const response = await fetchBillingDetailsAPI();
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Failed to fetch billing details.');
        }
    }
);

// Thunk: Create Invoice
export const createInvoice = createAsyncThunk(
    'billing/createInvoice',
    async (invoiceData, { rejectWithValue }) => {
        try {
            const response = await createInvoiceAPI(invoiceData);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Failed to create invoice.');
        }
    }
);

// Thunk: Process Payment
export const processPayment = createAsyncThunk(
    'billing/processPayment',
    async (paymentData, { rejectWithValue }) => {
        try {
            const response = await processPaymentAPI(paymentData);
            return response.data;
        } catch (err) {
            return rejectWithValue(err.response?.data || 'Failed to process payment.');
        }
    }
);

// Create billing slice
const billingSlice = createSlice({
    name: 'billing',
    initialState,
    reducers: {
        clearSuccess(state) {
            state.success = null;
        },
        clearError(state) {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // Fetch Invoices
            .addCase(fetchInvoices.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.success = null;
            })
            .addCase(fetchInvoices.fulfilled, (state, action) => {
                state.loading = false;
                state.invoices = action.payload;
                state.success = 'Invoices fetched successfully.';
            })
            .addCase(fetchInvoices.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            // Fetch Pending Payments
            .addCase(fetchPendingPayments.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.success = null;
            })
            .addCase(fetchPendingPayments.fulfilled, (state, action) => {
                state.loading = false;
                state.pendingPayments = action.payload;
                state.success = 'Pending payments fetched successfully.';
            })
            .addCase(fetchPendingPayments.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            // Fetch Billing Details
            .addCase(fetchBillingDetails.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.success = null;
            })
            .addCase(fetchBillingDetails.fulfilled, (state, action) => {
                state.loading = false;
                state.billingDetails = action.payload;
                state.success = 'Billing details fetched successfully.';
            })
            .addCase(fetchBillingDetails.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            // Create Invoice
            .addCase(createInvoice.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.success = null;
            })
            .addCase(createInvoice.fulfilled, (state, action) => {
                state.loading = false;
                state.invoices.push(action.payload);
                state.success = 'Invoice created successfully.';
            })
            .addCase(createInvoice.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            // Process Payment
            .addCase(processPayment.pending, (state) => {
                state.loading = true;
                state.error = null;
                state.success = null;
            })
            .addCase(processPayment.fulfilled, (state, action) => {
                state.loading = false;
                state.pendingPayments = state.pendingPayments.filter(
                    (payment) => payment.id !== action.payload.id
                );
                state.success = 'Payment processed successfully.';
            })
            .addCase(processPayment.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            });
    },
});

// Export actions
export const { clearSuccess, clearError } = billingSlice.actions;

// Selectors
export const selectInvoices = (state) => state.billing.invoices;
export const selectPendingPayments = (state) => state.billing.pendingPayments;
export const selectBillingDetails = (state) => state.billing.billingDetails;
export const selectBillingLoading = (state) => state.billing.loading;
export const selectBillingError = (state) => state.billing.error;
export const selectBillingSuccess = (state) => state.billing.success;

// Export reducer
export default billingSlice.reducer;
