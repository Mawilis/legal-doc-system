/**
 * Custom hook to manage a WebSocket connection using socket.io-client.
 *
 * This hook initializes the WebSocket connection only once,
 * sets up necessary event listeners, and cleans up when the component unmounts.
 *
 * @returns {Socket|null} The socket instance (or null if not yet connected)
 */
import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';

const useWebSocket = () => {
    // useState is used here so that components using this hook will re-render
    // once the socket connection is established.
    const [socket, setSocket] = useState(null);

    // useRef stores the socket instance persistently without triggering re-renders.
    const socketRef = useRef(null);

    useEffect(() => {
        // If the socket is not already initialized, create a new connection.
        if (!socketRef.current) {
            // Get the WebSocket URL from an environment variable or fall back to a local URL.
            const socketURL = process.env.REACT_APP_WS_URL || 'wss://localhost:3001';
            // Check if the current page is served over HTTPS.
            const isSecure = window.location.protocol === 'https:';

            // Initialize the WebSocket connection with specific options.
            // Adjust options like reconnectionAttempts and timeout as needed.
            const newSocket = io(socketURL, {
                transports: ['websocket'],     // Use WebSocket as the only transport.
                secure: isSecure,              // Enable secure connection if served over HTTPS.
                reconnectionAttempts: 5,       // Limit the number of reconnection attempts.
                timeout: 20000,                // Set a connection timeout (in milliseconds).
                rejectUnauthorized: false,     // For development with self-signed certificates.
            });

            // Save the socket instance in the ref and update the state.
            socketRef.current = newSocket;
            setSocket(newSocket);

            // Set up event listeners to monitor the WebSocket connection.

            // Log when the connection is successfully established.
            newSocket.on('connect', () => {
                console.log('WebSocket connected');
            });

            // Log when the connection is disconnected, optionally displaying the reason.
            newSocket.on('disconnect', (reason) => {
                console.log('WebSocket disconnected:', reason);
            });

            // Log any errors encountered during the connection process.
            newSocket.on('connect_error', (error) => {
                console.error('WebSocket connection error:', error);
            });

            // Log each reconnection attempt.
            newSocket.on('reconnect_attempt', (attempt) => {
                console.log(`WebSocket reconnection attempt: ${attempt}`);
            });

            // Log if reconnection ultimately fails.
            newSocket.on('reconnect_failed', () => {
                console.error('WebSocket reconnection failed');
            });
        }

        // Cleanup function: disconnect the socket when the component using this hook unmounts.
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
                console.log('WebSocket disconnected on unmount');
                socketRef.current = null;
                setSocket(null);
            }
        };
    }, []); // Empty dependency array ensures this effect runs only once when the component mounts.

    // Return the socket instance (it may be null on the first render).
    return socket;
};

export default useWebSocket;
