import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import useWebSocket from '../hooks/useWebSocket'; // Updated path to be relative to src/pages
import { getNotifications } from '../services/notificationService'; // Updated path to be relative to src/pages
import Notifications from '../components/Notifications'; // Assuming Notifications is in src/components

const DashboardContainer = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
  max-width: 800px;
  margin: 0 auto;
  background-color: ${({ theme }) => theme.colors.background};
  border-radius: ${({ theme }) => theme.spacing.sm};
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  margin-bottom: ${({ theme }) => theme.spacing.md};
  color: ${({ theme }) => theme.colors.text};
`;

const Dashboard = () => {
    const [notifications, setNotifications] = useState([]);
    const [error, setError] = useState(null);
    const socket = useWebSocket();

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const data = await getNotifications();
                setNotifications(data);
            } catch (err) {
                console.error('Error fetching dashboard data:', err);
                setError('Error fetching dashboard data');
            }
        };

        fetchNotifications();

        if (socket) {
            socket.emit('fetchNotifications');

            socket.on('notificationHistory', (data) => {
                setNotifications(data);
            });

            socket.on('new-notification', (notification) => {
                setNotifications((prev) => [notification, ...prev]);
            });

            socket.on('connect_error', (err) => {
                console.error('WebSocket connection error:', err);
                setError('Real-time connection error');
            });
        }

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
            <Notifications notifications={notifications} />
        </DashboardContainer>
    );
};

export default Dashboard;
