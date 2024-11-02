import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

const NotificationContainer = styled.div`
    background-color: #4caf50;
    color: white;
    padding: 16px;
    position: fixed;
    top: 20px;
    right: 20px;
    border-radius: 5px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Notification = ({ message }) => {
    return (
        <NotificationContainer>
            {message}
        </NotificationContainer>
    );
};

Notification.propTypes = {
    message: PropTypes.string.isRequired,
};

export default Notification;
