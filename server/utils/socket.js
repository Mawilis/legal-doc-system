// File: /utils/socket.js

// This module initializes and manages the Socket.io instance for real-time communication across the application.
let io; // Global variable to store the Socket.io instance

module.exports = {
    /**
     * Initialize the Socket.io server with the HTTP/HTTPS server instance.
     * This function should be called once when setting up the server.
     * @param {Object} httpServer - The HTTP or HTTPS server instance to bind Socket.io to.
     * @returns {Object} io - The initialized Socket.io instance.
     */
    init: (httpServer) => {
        // Initialize the Socket.io instance with the provided HTTP server and CORS configuration.
        io = require('socket.io')(httpServer, {
            cors: {
                origin: process.env.CLIENT_URL || 'http://localhost:3000', // Allow requests from frontend
                methods: ['GET', 'POST'], // Allow only GET and POST methods
                credentials: true, // Enable cookies and authorization headers
            },
        });

        console.log('Socket.io initialized'); // Log success message
        return io;
    },

    /**
     * Get the current Socket.io instance.
     * If the instance has not been initialized, this function throws an error.
     * This function allows other modules to access the same Socket.io instance.
     * @returns {Object} io - The Socket.io instance.
     * @throws {Error} If Socket.io has not been initialized.
     */
    getIo: () => {
        // Check if Socket.io instance is initialized
        if (!io) {
            throw new Error('Socket.io not initialized!'); // Throw error if not initialized
        }
        return io; // Return the Socket.io instance
    },
};
