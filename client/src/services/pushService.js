// client/src/services/pushService.js
import axios from 'axios';

const publicVapidKey = process.env.REACT_APP_VAPID_PUBLIC_KEY;  // Ensure this key is in your .env file

// Subscribe to Push Notifications
export const subscribeToPushNotifications = async (subscription) => {
    try {
        await axios.post('/api/subscribe', subscription, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Failed to subscribe to notifications', error);
    }
};

// Send a Push Notification
export const sendPushNotification = async (message) => {
    try {
        await axios.post('/api/notifications', { message });
    } catch (error) {
        console.error('Failed to send push notification', error);
    }
};

// Register the Service Worker and handle subscription
export const registerServiceWorkerAndSubscribe = async () => {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: publicVapidKey,
            });

            await subscribeToPushNotifications(subscription);
        } catch (error) {
            console.error('Error during service worker registration or push subscription', error);
        }
    }
};
