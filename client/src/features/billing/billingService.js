import axios from 'axios';

const API_URL = process.env.REACT_APP_API_BASE_URL;

export const fetchInvoices = () => axios.get(`${API_URL}/billing/invoices`);
export const fetchPendingPayments = () => axios.get(`${API_URL}/billing/pending-payments`);
export const fetchBillingDetails = () => axios.get(`${API_URL}/billing/details`);
export const createInvoice = (invoiceData) => axios.post(`${API_URL}/billing/invoices`, invoiceData);
export const processPayment = (paymentData) => axios.post(`${API_URL}/billing/payments`, paymentData);
