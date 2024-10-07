// src/hooks/useWebSocket.js

import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

export const useWebSocket = () => {
    const socketRef = useRef(null);

    useEffect(() => {
        // Initialize WebSocket connection
        socketRef.current = io(process.env.REACT_APP_WS_URL || 'ws://localhost:3001', {
            transports: ['websocket'],
            secure: window.location.protocol === 'https:',
        });

        console.log('WebSocket connected:', socketRef.current);

        // Cleanup on component unmount
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
                console.log('WebSocket disconnected');
            }
        };
    }, []);

    return socketRef.current;
};
