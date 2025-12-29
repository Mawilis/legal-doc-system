import http from '../../services/http';

// Adjust paths to match your server routes:
export const fetchInvoices = () => http.get('/billing/invoices');
export const fetchPendingPayments = () => http.get('/billing/pending-payments');
export const fetchBillingDetails = () => http.get('/billing/details');
export const createInvoice = (invoiceData) => http.post('/billing/invoices', invoiceData);
export const processPayment = (paymentData) => http.post('/billing/payments', paymentData);
