import axios from 'axios';

export const initiatePayment = async (paymentDetails) => {
    const response = await axios.post('/api/payments/initiate', paymentDetails);
    return response.data;
};

export const verifyPayment = async (paymentId) => {
    const response = await axios.get(`/api/payments/verify/${paymentId}`);
    return response.data;
};

export const getPaymentHistory = async (userId) => {
    const response = await axios.get(`/api/payments/history/${userId}`);
    return response.data;
};
