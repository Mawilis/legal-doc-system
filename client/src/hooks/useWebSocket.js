// src/hooks/useWebSocket.js
import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

// Correctly implemented useWebSocket hook
const useWebSocket = () => {
    const socketRef = useRef(null);

    useEffect(() => {
        // Establish WebSocket connection
        socketRef.current = io(process.env.REACT_APP_WS_URL || 'http://localhost:3001', {
            transports: ['websocket'],
            secure: window.location.protocol === 'https:',
        });

        console.log('WebSocket connected:', socketRef.current);

        // Handle disconnect events
        socketRef.current.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });

        // Handle error events
        socketRef.current.on('connect_error', (err) => {
            console.error('WebSocket connection error:', err);
        });

        // Cleanup connection when unmounting
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
                console.log('WebSocket disconnected');
            }
        };
    }, []);

    return socketRef.current;
};

export default useWebSocket;
