import axios from 'axios';

// Fetch all notifications for a user
export const getNotifications = async () => {
    try {
        const response = await axios.get('/api/notifications');
        return response.data;
    } catch (error) {
        console.error('Error fetching notifications', error);
        throw error;
    }
};

// Subscribe the user to push notifications
export const subscribeToPushNotifications = async (subscription) => {
    try {
        const response = await axios.post('/api/notifications/subscribe', subscription);
        return response.data;
    } catch (error) {
        console.error('Error subscribing to push notifications', error);
        throw error;
    }
};

// Send a notification
export const sendNotification = async (notificationData) => {
    try {
        const response = await axios.post('/api/notifications', notificationData);
        return response.data;
    } catch (error) {
        console.error('Error sending notification', error);
        throw error;
    }
};
