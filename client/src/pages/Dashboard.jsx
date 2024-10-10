// src/pages/Dashboard.js
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import useWebSocket from '../hooks/useWebSocket';  // Correctly import WebSocket hook
import { getNotifications } from '../services/notificationService';

const DashboardContainer = styled.div`
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const NotificationContainer = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const Notification = styled.div`
  padding: 10px;
  border-bottom: 1px solid #e0e0e0;
  &:last-child {
    border-bottom: none;
  }
`;

const Title = styled.h2`
  margin-bottom: 20px;
  color: #333;
`;

const Dashboard = () => {
    const [notifications, setNotifications] = useState([]);
    const [error, setError] = useState(null);
    const socket = useWebSocket();  // Using WebSocket hook correctly inside the functional component

    useEffect(() => {
        console.log('Dashboard component mounted');

        // Fetch notifications on mount
        const fetchNotifications = async () => {
            try {
                const data = await getNotifications();  // Fetch notifications
                console.log('Fetched dashboard data:', data);
                setNotifications(data);
            } catch (err) {
                console.error('Error fetching dashboard data:', err);
                setError('Error fetching dashboard data');
            }
        };

        fetchNotifications();

        // Setting up WebSocket listeners for real-time updates
        if (socket) {
            socket.emit('fetchNotifications');

            socket.on('notificationHistory', (data) => {
                console.log('Received notification history:', data);
                setNotifications(data);
            });

            socket.on('new-notification', (notification) => {
                console.log('Received new notification:', notification);
                setNotifications((prev) => [notification, ...prev]);
            });

            socket.on('connect_error', (err) => {
                console.error('WebSocket connection error:', err);
                setError('Real-time connection error');
            });
        }

        // Cleanup listeners on unmount
        return () => {
            if (socket) {
                socket.off('notificationHistory');
                socket.off('new-notification');
                socket.off('connect_error');
            }
        };
    }, [socket]);

    return (
        <DashboardContainer>
            <Title>Dashboard - Real-Time Notifications</Title>

            {error && <p style={{ color: 'red' }}>{error}</p>}

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
        </DashboardContainer>
    );
};

export default Dashboard;
