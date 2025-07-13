const { Server } = require('socket.io');
const logger = require('./logger');
const jwt = require('jsonwebtoken');

/**
 * Initialize and configure Socket.IO server.
 * @param {http.Server} server - The HTTP server to bind Socket.IO to.
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

    // --- Authentication middleware ---
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
            socket.userId = decoded.id;
            next();
        });
    });

    // --- Main connection ---
    io.on('connection', (socket) => {
        logger.info(`Socket connected: ${socket.id}, userId: ${socket.userId}`);

        // Personal room for direct messaging/notifications
        socket.join(socket.userId);
        socket.emit('connected');

        // Join a chat room
        socket.on('join_chat', (chatId) => {
            socket.join(chatId);
            logger.debug(`User ${socket.userId} joined chat room ${chatId}`);
        });

        // Handle new messages
        socket.on('new_message', (newMessage) => {
            if (!newMessage?.chat?.users) {
                logger.warn(`Malformed message: ${JSON.stringify(newMessage)}`);
                return;
            }

            newMessage.chat.users.forEach((user) => {
                if (user._id.toString() !== newMessage.sender._id.toString()) {
                    io.to(user._id).emit('message_received', newMessage);
                }
            });
        });

        // Typing indicators
        socket.on('typing', (chatId) => socket.to(chatId).emit('typing', { userId: socket.userId }));
        socket.on('stop_typing', (chatId) => socket.to(chatId).emit('stop_typing', { userId: socket.userId }));

        // Disconnect
        socket.on('disconnect', (reason) => {
            logger.info(`Socket disconnected: ${socket.id}, reason: ${reason}`);
        });
    });

    return io;
};

module.exports = initializeSocketIO;
