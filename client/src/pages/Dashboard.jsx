import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import styled from 'styled-components';

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

    const socket = io('https://your-backend-url.com', { secure: true });

    useEffect(() => {
        console.log('Dashboard component mounted');

        const fetchNotifications = async () => {
            try {
                const response = await fetch('/api/dashboard');
                if (!response.ok) {
                    throw new Error('Failed to fetch dashboard data');
                }
                const data = await response.json();
                console.log('Fetched dashboard data:', data);
                setNotifications(data);
            } catch (err) {
                console.error('Error fetching dashboard data:', err);
                setError('Error fetching dashboard data');
            }
        };

        fetchNotifications();

        socket.emit('fetchNotifications');
        console.log('Requested notification history from server');

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

        return () => {
            console.log('Cleaning up socket connection in Dashboard');
            socket.disconnect();
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
                        <Notification key={index}>
                            {notification.message}
                        </Notification>
                    ))
                )}
            </NotificationContainer>
        </DashboardContainer>
    );
};

export default Dashboard;
