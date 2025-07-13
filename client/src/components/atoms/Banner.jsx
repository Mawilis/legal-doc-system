import React, { useEffect, useState, useCallback } from "react";
import styled from "styled-components";
import useWebSocket from "../../hooks/useWebSocket";
import { getNotifications } from "../../services/notificationService";
import Notifications from "../../components/molecules/Notifications";
import Banner from "../../components/atoms/Banner";
import bannerImage from "../../assets/images/legal-office.jpg";

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

    const fetchNotifications = useCallback(async () => {
        try {
            const data = await getNotifications();
            setNotifications(data);
        } catch (err) {
            console.error("Error fetching dashboard data:", err);
            setError("Error fetching dashboard data");
        }
    }, []);

    useEffect(() => {
        fetchNotifications(); // Fetch initial notifications

        if (socket) {
            socket.emit("fetchNotifications");

            // Event listeners for real-time updates
            const handleNotificationHistory = (data) => {
                setNotifications(data);
            };

            const handleNewNotification = (notification) => {
                setNotifications((prev) => [notification, ...prev]);
            };

            const handleConnectionError = (err) => {
                console.error("WebSocket connection error:", err);
                setError("Real-time connection error");
            };

            socket.on("notificationHistory", handleNotificationHistory);
            socket.on("new-notification", handleNewNotification);
            socket.on("connect_error", handleConnectionError);

            // Cleanup function to remove event listeners
            return () => {
                socket.off("notificationHistory", handleNotificationHistory);
                socket.off("new-notification", handleNewNotification);
                socket.off("connect_error", handleConnectionError);
            };
        }
    }, [socket, fetchNotifications]); // Include fetchNotifications in the dependency array

    return (
        <DashboardContainer>
            <Banner text="Welcome to the Dashboard" img={bannerImage} />
            <Title>Dashboard - Real-Time Notifications</Title>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <Notifications notifications={notifications} />
        </DashboardContainer>
    );
};

export default Dashboard;