// client/src/services/chatService.js
import axios from 'axios';

// Fetch all messages from chat
export const getAllMessages = async () => {
    try {
        const response = await axios.get('/api/chat');
        return response.data;
    } catch (error) {
        console.error('Error fetching messages', error);
        throw error;
    }
};

// Send a chat message
export const sendMessage = async (messageData) => {
    try {
        const response = await axios.post('/api/chat', messageData);
        return response.data;
    } catch (error) {
        console.error('Error sending message', error);
        throw error;
    }
};
