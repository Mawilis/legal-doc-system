// ~/client/src/mobile/SheriffApp.jsx

import React, { useEffect, useState, useCallback, useRef } from 'react';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import socket from '../services/socket'; // Import the shared socket instance
import Button from '../components/atoms/Button'; // Import our masterpiece Button
import { FaPlayCircle, FaStopCircle } from 'react-icons/fa';

// --- Styled Components for a Professional Mobile UI ---

const Container = styled.div`
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.background || '#f4f6f8'};
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Card = styled.div`
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  text-align: center;
`;

const Header = styled.h2`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.primary || '#007bff'};
  margin-top: 0;
  margin-bottom: 1rem;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  color: ${({ $active, theme }) => ($active ? theme.colors.success : theme.colors.textMuted) || ($active ? '#28a745' : '#6c757d')};

  &::before {
    content: '●';
    font-size: 1.5rem;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const InfoGrid = styled.div`
  margin-top: 1.5rem;
  text-align: left;
  border-top: 1px solid ${({ theme }) => theme.colors.border || '#e0e0e0'};
  padding-top: 1.5rem;
`;

const InfoItem = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  
  strong {
    color: ${({ theme }) => theme.colors.text || '#333'};
  }
`;

const ErrorText = styled.p`
  color: ${({ theme }) => theme.colors.danger || '#dc3545'};
  margin-top: 1rem;
  font-weight: 500;
`;

/**
 * A mobile-focused component for sheriffs to track and broadcast their GPS location in real-time.
 */
const SheriffApp = () => {
    // --- Hooks ---
    const { isAuthenticated, user } = useSelector((state) => state.auth);
    const watchIdRef = useRef(null); // Use a ref to store the watchId to avoid re-renders

    // --- State Management ---
    const [location, setLocation] = useState(null);
    const [error, setError] = useState(null);
    const [isTracking, setTracking] = useState(false);
    const [isConnected, setConnected] = useState(socket.connected);

    // --- Real-time Connection Management ---
    useEffect(() => {
        // Manually connect the socket when the component mounts for an authenticated sheriff
        if (isAuthenticated && user?.role === 'sheriff') {
            socket.connect();
        }

        const handleConnect = () => setConnected(true);
        const handleDisconnect = () => setConnected(false);

        socket.on('connect', handleConnect);
        socket.on('disconnect', handleDisconnect);

        // Cleanup on unmount: stop tracking and disconnect the socket
        return () => {
            if (watchIdRef.current) {
                navigator.geolocation.clearWatch(watchIdRef.current);
            }
            socket.off('connect', handleConnect);
            socket.off('disconnect', handleDisconnect);
            if (socket.connected) {
                socket.disconnect();
            }
        };
    }, [isAuthenticated, user]);

    // --- Geolocation Logic ---
    const startTracking = useCallback(() => {
        if (!navigator.geolocation) {
            setError('Geolocation is not supported by your browser.');
            return;
        }

        setError(null);
        setTracking(true);

        // Start watching the user's position
        watchIdRef.current = navigator.geolocation.watchPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                const newLocation = { latitude, longitude, timestamp: new Date().toISOString() };
                setLocation(newLocation);

                // Emit location update to the server via the secure, authenticated socket
                if (socket.connected) {
                    socket.emit('sheriff:locationUpdate', {
                        // The backend will get the user ID from the authenticated socket instance
                        location: { latitude, longitude },
                        timestamp: newLocation.timestamp,
                    });
                }
            },
            (err) => {
                setError(`Location error: ${err.message}`);
                setTracking(false);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }, []);

    const stopTracking = useCallback(() => {
        if (watchIdRef.current) {
            navigator.geolocation.clearWatch(watchIdRef.current);
            watchIdRef.current = null;
            setTracking(false);
            if (socket.connected) {
                socket.emit('sheriff:trackingStopped');
            }
        }
    }, []);

    // --- Authentication Check ---
    // Redirect if not an authenticated sheriff
    if (!isAuthenticated || user?.role !== 'sheriff') {
        return <Navigate to="/login" />;
    }

    // --- Render Logic ---
    return (
        <Container>
            <Card>
                <Header>Sheriff Mobile Tracker</Header>
                <StatusIndicator $active={isTracking}>
                    {isTracking ? 'Tracking Active' : 'Tracking Inactive'}
                </StatusIndicator>

                <ButtonGroup>
                    {!isTracking ? (
                        <Button variant="success" size="large" onClick={startTracking} disabled={!isConnected}>
                            <FaPlayCircle /> Start Tracking
                        </Button>
                    ) : (
                        <Button variant="danger" size="large" onClick={stopTracking}>
                            <FaStopCircle /> Stop Tracking
                        </Button>
                    )}
                </ButtonGroup>

                {!isConnected && <ErrorText>Disconnected from server. Trying to reconnect...</ErrorText>}

                {location && (
                    <InfoGrid>
                        <InfoItem>
                            <strong>Latitude:</strong> {location.latitude.toFixed(6)}
                        </InfoItem>
                        <InfoItem>
                            <strong>Longitude:</strong> {location.longitude.toFixed(6)}
                        </InfoItem>
                        <InfoItem>
                            <strong>Last Update:</strong> {new Date(location.timestamp).toLocaleTimeString()}
                        </InfoItem>
                    </InfoGrid>
                )}

                {error && <ErrorText>{error}</ErrorText>}
            </Card>
        </Container>
    );
};

export default SheriffApp;
