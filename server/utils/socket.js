// ~/server/utils/socket.js

const { Server } = require('socket.io');
const logger = require('./logger');
const jwt = require('jsonwebtoken');
const turf = require('@turf/turf');
const AuditLog = require('../models/auditLogModel');
const { sendEmail, sendSMS } = require('./alertUtils'); // ✅ Import both alert utilities

/**
 * Initializes and configures a secure, real-time Socket.IO server.
 * This version includes server-side geofence detection with email and SMS alerts.
 */
const initializeSocketIO = (server) => {
    // --- Geofence Definition ---
    const geofencePolygon = turf.polygon([[
        [28.06, -26.02], [28.18, -26.02],
        [28.18, -25.96], [28.06, -25.96],
        [28.06, -26.02]
    ]]);

    const io = new Server(server, {
        pingTimeout: 60000,
        cors: {
            origin: process.env.CLIENT_URL || "http://localhost:3000",
            methods: ["GET", "POST"],
            credentials: true,
        },
    });

    // --- JWT Authentication Middleware ---
    io.use((socket, next) => {
        const token = socket.handshake.auth.token;
        if (!token) return next(new Error('Authentication error: No token provided'));

        jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
            if (err) return next(new Error('Authentication error: Invalid token'));
            socket.user = { id: decoded.id, name: decoded.name, role: decoded.role, email: decoded.email };
            next();
        });
    });

    // --- Main Connection Handler ---
    io.on('connection', (socket) => {
        logger.info(`Socket connected: ${socket.id}, userId: ${socket.user.id}`);

        socket.on('sheriff:locationUpdate', async (data) => {
            try {
                const { location, timestamp } = data;
                const point = turf.point([location.longitude, location.latitude]);
                const isInsideGeofence = turf.booleanPointInPolygon(point, geofencePolygon);

                // This logic block now handles the full alert process
                if (!isInsideGeofence) {
                    const breachData = { user: socket.user, location, timestamp: new Date().toISOString() };
                    io.emit('sheriff:geofenceBreach', breachData);

                    await AuditLog.create({
                        user: socket.user.id,
                        email: socket.user.email,
                        method: 'SOCKET',
                        path: 'sheriff:geofenceBreach',
                        status: 'FAILED',
                        ip: socket.handshake.address,
                    });

                    // ✅ Trigger real-time email and SMS alerts
                    const alertMessage = `🚨 GEOFENCE BREACH: Sheriff ${socket.user.name} has left the designated zone at ${new Date().toLocaleTimeString()}.`;
                    const adminEmail = process.env.ADMIN_EMAIL;
                    const adminPhone = process.env.ADMIN_PHONE_NUMBER;

                    // Send email alert if configured
                    if (adminEmail) {
                        sendEmail(adminEmail, 'High Priority: Geofence Breach Alert', alertMessage);
                    }
                    // Send SMS alert if configured
                    if (adminPhone) {
                        sendSMS(adminPhone, alertMessage);
                    }
                }

                // ... (rest of location update logic, e.g., saving to DB)

            } catch (err) {
                logger.error(`[SOCKET ERROR] in sheriff:locationUpdate: ${err.message}`);
            }
        });

        // ... (other event handlers: chat, typing, etc.)

        socket.on('disconnect', () => {
            logger.info(`Socket disconnected: ${socket.id}`);
        });
    });

    return io;
};

module.exports = initializeSocketIO;
