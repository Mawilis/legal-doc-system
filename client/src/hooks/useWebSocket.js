import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

const useWebSocket = () => {
    const socketRef = useRef(null);

    useEffect(() => {
        // Check if socket is already initialized to avoid multiple connections
        if (!socketRef.current) {
            const socketURL = process.env.REACT_APP_WS_URL || 'ws://localhost:3001';
            const isSecure = window.location.protocol === 'https:';

            // Initialize the WebSocket connection
            socketRef.current = io(socketURL, {
                transports: ['websocket'],
                secure: isSecure,
                reconnectionAttempts: 5, // Limit reconnection attempts
                timeout: 20000, // Connection timeout
            });

            // Handle connection event
            socketRef.current.on('connect', () => {
                console.log('WebSocket connected');
            });

            // Handle disconnection event
            socketRef.current.on('disconnect', () => {
                console.log('WebSocket disconnected');
            });

            // Handle connection error event
            socketRef.current.on('connect_error', (err) => {
                console.error('WebSocket connection error:', err);
            });

            // Handle reconnection attempts
            socketRef.current.on('reconnect_attempt', (attempt) => {
                console.log(`Reconnection attempt ${attempt}`);
            });

            // Handle reconnection failures
            socketRef.current.on('reconnect_failed', () => {
                console.error('Failed to reconnect to WebSocket');
            });
        }

        // Cleanup WebSocket connection on component unmount
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
                console.log('WebSocket disconnected on unmount');
                socketRef.current = null;
            }
        };
    }, []);

    return socketRef.current;
};

export default useWebSocket;
