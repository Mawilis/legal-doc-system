import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const NotificationContainer = styled.div`
  background-color: ${({ theme }) => theme.colors.background};
  border-radius: ${({ theme }) => theme.spacing.sm};
  padding: ${({ theme }) => theme.spacing.md};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: ${({ theme }) => theme.spacing.md};
`;

const Notification = styled.div`
  padding: ${({ theme }) => theme.spacing.sm};
  border-bottom: 1px solid #e0e0e0;

  &:last-child {
    border-bottom: none;
  }
`;

const Notifications = ({ notifications }) => (
    <NotificationContainer>
        <h3>Notifications</h3>
        {notifications.length === 0 ? (
            <p>No notifications yet...</p>
        ) : (
            notifications.map((notification, index) => (
                <Notification key={index}>{notification.message}</Notification>
            ))
        )}
    </NotificationContainer>
);

Notifications.propTypes = {
    notifications: PropTypes.array.isRequired,
};

export default Notifications;
