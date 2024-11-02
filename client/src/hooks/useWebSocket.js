// ~/legal-doc-system/client/src/hooks/useWebSocket.js
import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

const useWebSocket = () => {
    const socketRef = useRef(null);

    useEffect(() => {
        if (!socketRef.current) {
            socketRef.current = io(process.env.REACT_APP_WS_URL || 'ws://localhost:3001', {
                transports: ['websocket'],
                secure: window.location.protocol === 'https:',
            });

            socketRef.current.on('connect', () => {
                console.log('WebSocket connected');
            });

            socketRef.current.on('disconnect', () => {
                console.log('WebSocket disconnected');
            });

            socketRef.current.on('connect_error', (err) => {
                console.error('WebSocket connection error:', err);
            });
        }

        // Cleanup the socket connection on component unmount
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
                console.log('WebSocket disconnected on unmount');
            }
        };
    }, []);

    return socketRef.current;
};

export default useWebSocket;
