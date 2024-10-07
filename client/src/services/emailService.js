import axios from 'axios';

export const sendVerificationEmail = async (email) => {
    const response = await axios.post('/api/emails/verify', { email });
    return response.data;
};

export const sendPasswordResetEmail = async (email) => {
    const response = await axios.post('/api/emails/reset-password', { email });
    return response.data;
};
