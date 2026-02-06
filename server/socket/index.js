/**
 * File: server/socket/index.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Real-Time Nervous System (Secure & Isolated)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - SECURITY: Middleware intercepts handshake and validates JWT.
 * - ISOLATION: Automatically joins users to 'Tenant' and 'Role' rooms.
 * - LOGGING: Tracks specific users (Name/ID) instead of random socket IDs.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');

module.exports = (httpServer) => {
    // 1. CONFIGURATION
    const allowedOrigins = process.env.CLIENT_URL
        ? [process.env.CLIENT_URL]
        : ['http://localhost:3000', 'http://127.0.0.1:3000'];

    const io = new Server(httpServer, {
        cors: {
            origin: allowedOrigins,
            methods: ['GET', 'POST'],
            credentials: true
        }
    });

    // 2. MIDDLEWARE: SECURITY GATEKEEPER
    // This runs BEFORE a connection is accepted.
    io.use((socket, next) => {
        const token = socket.handshake.auth.token;

        if (!token) {
            console.warn(`⛔ [Socket] Blocked connection attempt (No Token): ${socket.id}`);
            return next(new Error('Authentication Error: Token missing'));
        }

        try {
            // Verify Token against Secret
            const secret = process.env.JWT_SECRET || 'wilsy_secret_key_2025';
            const decoded = jwt.verify(token, secret);

            // Attach Identity to Socket Session
            socket.user = {
                id: decoded.id || decoded._id,
                name: decoded.name || 'Unknown Agent',
                role: decoded.role,
                tenantId: decoded.tenantId
            };

            next(); // Access Granted
        } catch (err) {
            console.warn(`⛔ [Socket] Blocked invalid token from ${socket.id}`);
            next(new Error('Authentication Error: Invalid Token'));
        }
    });

    // 3. CONNECTION LIFECYCLE
    io.on('connection', (socket) => {
        const { name, role, tenantId } = socket.user;

        // A. JOIN SECURE ROOMS
        // 1. Tenant Room: Broadcasts only to this firm (e.g., "wilsy")
        socket.join(tenantId);
        // 2. Role Room: Broadcasts only to this rank (e.g., "sheriff")
        socket.join(`role:${role}`);
        // 3. Personal Room: Direct messages
        socket.join(socket.user.id);

        console.log(`🔌 [Socket] Connected: ${name} (${role}) | 🏢 Tenant: ${tenantId}`);

        // B. HANDLING DISCONNECT
        socket.on('disconnect', (reason) => {
            console.log(`🔌 [Socket] Disconnected: ${name} | Reason: ${reason}`);
        });

        // C. ERROR LOGGING
        socket.on('error', (err) => {
            console.error(`❌ [Socket] Error on ${name}:`, err);
        });
    });

    return io;
};