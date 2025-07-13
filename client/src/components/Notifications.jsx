import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styled, { keyframes } from 'styled-components';
import { FaCheckCircle, FaExclamationCircle, FaTimesCircle } from 'react-icons/fa'; // Import icons

// Define fade-in animation
const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

// Styled component for the notification container
const NotificationContainer = styled.div`
  background-color: ${({ type }) => { // Background color based on type
        switch (type) {
            case 'success': return '#4caf50'; // Green
            case 'error': return '#f44336';   // Red
            case 'warning': return '#ff9800'; // Orange
            default: return '#4caf50';       // Default to green
        }
    }};
  color: white;
  padding: 16px;
  position: fixed;
  top: 20px;
  right: 20px;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-width: 300px;
  overflow-wrap: break-word;
  animation: ${fadeIn} 0.5s ease; // Add fade-in animation
`;

// Styled component for the close button
const CloseButton = styled.button`
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
`;

// Notification component
const Notification = ({ message, type, duration = 5000 }) => { // Add type and duration props
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        // Automatically dismiss the notification after the specified duration
        const timer = setTimeout(() => {
            setIsVisible(false);
        }, duration);

        // Cleanup function to clear the timeout if the component unmounts
        return () => clearTimeout(timer);
    }, [duration]);

    // Function to dismiss the notification
    const handleClose = () => {
        setIsVisible(false);
    };

    if (!isVisible) {
        return null; // Don't render anything if not visible
    }

    return (
        <NotificationContainer type={type} role="alert" aria-live="assertive">
            {/* Display icon based on type */}
            {type === 'success' && <FaCheckCircle style={{ marginRight: '8px' }} />}
            {type === 'error' && <FaTimesCircle style={{ marginRight: '8px' }} />}
            {type === 'warning' && <FaExclamationCircle style={{ marginRight: '8px' }} />}
            {message}
            <CloseButton onClick={handleClose} aria-label="Close Notification">
                {/* Close button */}
                <FaTimesCircle />
            </CloseButton>
        </NotificationContainer>
    );
};

// PropTypes for validation
Notification.propTypes = {
    message: PropTypes.string.isRequired,
    type: PropTypes.oneOf(['success', 'error', 'warning']), // Add type prop type
    duration: PropTypes.number, // Add duration prop type
};

export default Notification;