// ~/legal-doc-system/client/src/components/Notification.jsx

import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaCheckCircle, FaExclamationCircle, FaInfoCircle, FaTimes } from 'react-icons/fa';

/**
 * A map of notification types to their corresponding colors and icons.
 * This makes it easy to extend with new notification types in the future.
 */
const notificationVariants = {
    success: {
        color: '#28a745',
        icon: <FaCheckCircle />,
    },
    error: {
        color: '#dc3545',
        icon: <FaExclamationCircle />,
    },
    info: {
        color: '#17a2b8',
        icon: <FaInfoCircle />,
    },
    warning: {
        color: '#ffc107',
        icon: <FaExclamationCircle />,
    },
};

/**
 * A styled container for the notification component.
 * It's designed to be visually distinct and includes a colored left border
 * that corresponds to the notification type.
 */
const NotificationWrapper = styled(motion.div)`
  background-color: ${({ theme }) => theme.colors.background || '#fff'};
  color: ${({ theme }) => theme.colors.text || '#333'};
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  width: 350px;
  border-left: 5px solid ${({ type }) => notificationVariants[type]?.color || '#6c757d'};
`;

const IconWrapper = styled.div`
  font-size: 1.5rem;
  color: ${({ type }) => notificationVariants[type]?.color || '#6c757d'};
  flex-shrink: 0;
`;

const Message = styled.p`
  margin: 0;
  flex-grow: 1;
  font-size: 0.95rem;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textMuted || '#6c757d'};
  cursor: pointer;
  font-size: 1rem;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.backgroundLight || '#f1f1f1'};
  }
`;

/**
 * A reusable UI component for displaying a single notification.
 * It supports different types, includes an icon, and can be dismissed.
 *
 * @param {object} props
 * @param {string} props.message - The notification message to display.
 * @param {('success'|'error'|'info'|'warning')} [props.type='info'] - The type of notification.
 * @param {Function} props.onClose - The function to call when the notification is dismissed.
 */
const Notification = ({ message, type = 'info', onClose }) => {
    const variant = notificationVariants[type] || notificationVariants.info;

    return (
        <NotificationWrapper
            type={type}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.3 }}
            role="alert"
            aria-live="assertive"
        >
            <IconWrapper type={type}>{variant.icon}</IconWrapper>
            <Message>{message}</Message>
            <CloseButton onClick={onClose} aria-label="Close notification">
                <FaTimes />
            </CloseButton>
        </NotificationWrapper>
    );
};

// --- PropTypes for Code Quality ---
Notification.propTypes = {
    message: PropTypes.string.isRequired,
    type: PropTypes.oneOf(['success', 'error', 'info', 'warning']),
    onClose: PropTypes.func.isRequired,
};

export default Notification;
