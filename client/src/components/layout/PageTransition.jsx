// ~/legal-doc-system/client/src/middleware/socketMiddleware.js

import socket from '../services/socket'; // Import the singleton socket instance
import { toast } from 'react-toastify';
import {
    addUserFromSocket,
    removeUserFromSocket,
    updateUserFromSocket,
} from '../features/admin/reducers/adminSlice'; // Import the correct real-time actions

/**
 * @file This file contains the Redux middleware for handling real-time events via Socket.IO.
 * It acts as a centralized listener for all incoming socket events and dispatches
 * corresponding Redux actions to keep the client state synchronized with the server.
 */

/**
 * A Redux middleware that listens for socket events and updates the store.
 *
 * @param {object} storeAPI - The Redux store's API, providing `dispatch` and `getState`.
 * @returns {Function} A standard Redux middleware function.
 */
const socketMiddleware = (storeAPI) => {
    // --- Centralized Event Listeners ---
    // These listeners are set up once when the middleware is initialized.

    /**
     * Handles the 'user-created' event from the server.
     * @param {object} user - The new user object received from the server.
     */
    socket.on('user-created', (user) => {
        toast.info(`🟢 New user created: ${user.name}`);
        storeAPI.dispatch(addUserFromSocket(user));
    });

    /**
     * Handles the 'user-updated' event from the server.
     * This can be for a role change, permission update, or any other user detail.
     * @param {object} user - The updated user object received from the server.
     */
    socket.on('user-updated', (user) => {
        toast.success(`✅ User updated: ${user.name}`);
        storeAPI.dispatch(updateUserFromSocket(user));
    });

    /**
     * Handles the 'user-deleted' event from the server.
     * @param {string} userId - The ID of the user who was deleted.
     */
    socket.on('user-deleted', (userId) => {
        toast.warn(`🗑️ A user was removed.`);
        storeAPI.dispatch(removeUserFromSocket(userId));
    });

    // You can add more listeners for other features here, for example:
    // socket.on('new-notification', (notification) => { ... });
    // socket.on('new-chat-message', (message) => { ... });

    // The middleware function that gets called for every dispatched action.
    return (next) => (action) => {
        // In a more advanced setup, you could intercept certain actions
        // and emit socket events here. For now, we just pass the action along.
        return next(action);
    };
};

export default socketMiddleware;
