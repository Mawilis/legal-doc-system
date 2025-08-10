// ~/legal-doc-system/server/socket/index.js

const { Server } = require('socket.io');
const logger = require('../utils/logger'); // Assuming a standard logger like Winston
const jwt = require('jsonwebtoken');
const Location = require('../models/locationModel'); // Import the location model
const AuditLog = require('../models/auditLogModel'); // Import the audit log model

/**
 * Initializes and configures a secure, real-time Socket.IO server.
 * This masterpiece version includes JWT authentication for all connections
 * and handles all application-specific events, including creating audit logs
 * for critical real-time actions.
 *
 * @param {http.Server} server - The HTTP server to bind Socket.IO to.
 * @returns {Server} The configured Socket.IO server instance.
 */
const initializeSocketIO = (server) => {
    const io = new Server(server, {
        pingTimeout: 60000,
        cors: {
            origin: process.env.CLIENT_URL || "http://localhost:3000",
            methods: ["GET", "POST"],
            credentials: true,
        },
    });

    // --- JWT Authentication Middleware for Sockets ---
    // This professional pattern secures the connection itself, so we don't
    // need to re-authenticate every single event.
    io.use((socket, next) => {
        const token = socket.handshake.auth.token;
        if (!token) {
            logger.warn(`Socket connection rejected: No token provided [socketId: ${socket.id}]`);
            return next(new Error('Authentication error: No token provided'));
        }

        jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
            if (err) {
                logger.warn(`Socket connection rejected: Invalid token [socketId: ${socket.id}]`);
                return next(new Error('Authentication error: Invalid token'));
            }
            // Attach user details to the socket instance for use in all event handlers.
            socket.user = { id: decoded.id, name: decoded.name, email: decoded.email }; // Assumes JWT payload has these
            next();
        });
    });

    // --- Main Connection Handler ---
    io.on('connection', (socket) => {
        logger.info(`Socket connected: ${socket.id}, userId: ${socket.user.id}`);

        // --- Sheriff Location Tracking Events ---
        socket.on('sheriff:locationUpdate', async (data) => {
            try {
                const { location, timestamp } = data;
                const userId = socket.user.id;

                // Broadcast the update to all connected admin clients.
                // The event name 'sheriff:locationUpdated' matches the dashboard's listener.
                io.emit('sheriff:locationUpdated', {
                    user: { _id: userId, name: socket.user.name },
                    location: { coordinates: [location.longitude, location.latitude] },
                    updatedAt: timestamp,
                });

                // Save the location to the database.
                await Location.findOneAndUpdate(
                    { user: userId },
                    { location: { type: 'Point', coordinates: [location.longitude, location.latitude] } },
                    { upsert: true, new: true }
                );

                // ✅ Create a detailed audit log for this critical real-time event.
                await AuditLog.create({
                    user: userId,
                    email: socket.user.email,
                    method: 'SOCKET',
                    path: 'sheriff:locationUpdate',
                    status: 'SUCCESS',
                    ip: socket.handshake.address,
                    timestamp: new Date(),
                });

            } catch (err) {
                logger.error(`[SOCKET ERROR] in sheriff:locationUpdate: ${err.message}`);
            }
        });

        socket.on('sheriff:trackingStopped', () => {
            io.emit('sheriff:trackingStopped', { userId: socket.user.id });
        });

        // --- Chat Events ---
        socket.on('joinRoom', (roomId) => socket.join(roomId));
        socket.on('leaveRoom', (roomId) => socket.leave(roomId));
        socket.on('sendMessage', (messageData) => {
            io.to(messageData.roomId).emit('newMessage', messageData);
        });
        socket.on('typing', ({ roomId, user }) => socket.broadcast.to(roomId).emit('typing', user));
        socket.on('stopTyping', ({ roomId }) => socket.broadcast.to(roomId).emit('stopTyping'));

        // --- Disconnect Handler ---
        socket.on('disconnect', (reason) => {
            logger.info(`Socket disconnected: ${socket.id}, reason: ${reason}`);
        });
    });

    return io;
};

module.exports = initializeSocketIO;
