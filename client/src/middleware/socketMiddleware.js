// ~/client/src/middleware/socketMiddleware.js

import socket from '../services/socket';
import { toast } from 'react-toastify';
import {
    addUserFromSocket,
    removeUserFromSocket,
    updateUserFromSocket,
} from '../features/admin/reducers/adminSlice';
import { addMessage, setTyping } from '../features/chat/reducers/chatSlice';

/**
 * A Redux middleware that listens for socket events and updates the store.
 * This is the central hub for all real-time event handling.
 */
const socketMiddleware = (storeAPI) => {
    // --- Admin Listeners ---
    socket.on('user-created', (user) => {
        toast.info(`🟢 New user created: ${user.name}`);
        storeAPI.dispatch(addUserFromSocket(user));
    });

    socket.on('user-updated', (user) => {
        toast.success(`✅ User details updated for: ${user.name}`);
        storeAPI.dispatch(updateUserFromSocket(user));
    });

    socket.on('user-deleted', (userId) => {
        toast.warn(`🗑️ A user was removed.`);
        storeAPI.dispatch(removeUserFromSocket(userId));
    });

    // --- Chat Listeners ---
    socket.on('newMessage', (message) => {
        storeAPI.dispatch(addMessage(message));
    });
    socket.on('typing', (username) => {
        storeAPI.dispatch(setTyping(username));
    });
    socket.on('stopTyping', () => {
        storeAPI.dispatch(setTyping(null));
    });

    // --- Sheriff Tracking Listeners ---

    /**
     * ✅ Handles the 'geofenceBreach' event from the server.
     * Triggers a high-priority, non-dismissing toast notification for admins
     * with more detailed information from the breach log.
     * @param {object} data - The breach data, including the user and the full breach log object.
     */
    socket.on('sheriff:geofenceBreach', (data) => {
        const { user, breach } = data;
        const message = `🚨 GEOFENCE BREACH: ${user.name} has left the "${breach.breachedZone}"!`;

        toast.error(
            message,
            {
                autoClose: false, // Keep the alert on screen until manually closed
                closeOnClick: false,
                draggable: false,
            }
        );
    });

    return (next) => (action) => next(action);
};

export default socketMiddleware;
