// ~/legal-doc-system/client/src/context/NotificationContext.jsx

import React, { createContext, useState, useCallback, useContext } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Notification from '../components/Notification'; // Assuming a Notification component exists

/**
 * @file This file creates a centralized system for handling application-wide notifications.
 * It uses React Context to provide a simple `showNotification` function to any component,
 * and it manages the state for displaying multiple, auto-dismissing notifications.
 */

// --- Styled Container for Notifications ---
const NotificationContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000; // Ensure it's above other UI elements
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

// --- Create the Context ---
export const NotificationContext = createContext(null);

/**
 * The NotificationProvider component.
 * It wraps the application and provides the notification functionality.
 *
 * @param {object} props
 * @param {React.ReactNode} props.children - The child components to be rendered.
 */
export const NotificationProvider = ({ children }) => {
    // State to hold an array of active notifications
    const [notifications, setNotifications] = useState([]);

    /**
     * Removes a notification from the state by its ID.
     */
    const removeNotification = useCallback((id) => {
        setNotifications((prevNotifications) =>
            prevNotifications.filter((n) => n.id !== id)
        );
    }, []);

    /**
     * Adds a new notification to be displayed.
     * It automatically removes the notification after the specified duration.
     * @param {string} message - The message to display in the notification.
     * @param {('success'|'error'|'info'|'warning')} [type='success'] - The type of notification.
     * @param {number} [duration=5000] - The duration in milliseconds to display the notification.
     */
    const showNotification = useCallback(
        (message, type = 'success', duration = 5000) => {
            const id = Date.now() + Math.random(); // Create a unique ID
            const newNotification = { id, message, type, duration };

            // Add the new notification to the array
            setNotifications((prevNotifications) => [...prevNotifications, newNotification]);

            // Set a timer to automatically remove the notification
            setTimeout(() => {
                removeNotification(id);
            }, duration);
        },
        [removeNotification]
    );

    return (
        <NotificationContext.Provider value={{ showNotification }}>
            {children}
            <NotificationContainer>
                {notifications.map((notification) => (
                    <Notification
                        key={notification.id}
                        message={notification.message}
                        type={notification.type}
                        onClose={() => removeNotification(notification.id)}
                    />
                ))}
            </NotificationContainer>
        </NotificationContext.Provider>
    );
};

NotificationProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

/**
 * A custom hook for easily accessing the notification context.
 * This is the recommended way to use the notification system.
 *
 * @example
 * const { showNotification } = useNotification();
 * showNotification('Profile updated successfully!', 'success');
 *
 * @returns {{showNotification: Function}} The showNotification function.
 */
export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};
