/*
 * File: server/utils/breachHandler.js
 * STATUS: PRODUCTION-READY | OPERATIONAL SECURITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The system's automated "Internal Affairs" agent. Reacts to GPS anomalies, 
 * logs jurisdictional violations, and synchronizes real-time admin dashboards.
 * -----------------------------------------------------------------------------
 */

'use strict';

const GeofenceBreach = require('../models/GeofenceBreach');
const User = require('../models/User');
const { sendEmail, sendSMS } = require('./alertUtils');
const logger = require('./logger');

/**
 * HANDLE GEOFENCE VIOLATION
 * @param {object} io - Socket.IO instance for real-time reactivity
 * @param {object} actor - The user (Sheriff) triggering the breach
 * @param {object} location - GPS coordinates { lat, lng }
 * @param {string} zoneName - The jurisdiction name
 */
const handleGeofenceBreach = async (io, actor, location, zoneName) => {
    try {
        // 1. FORENSIC PERSISTENCE
        // We log this immediately as an immutable record of non-compliance.
        const breachLog = await GeofenceBreach.create({
            tenantId: actor.tenantId,
            userId: actor._id,
            userName: actor.name,
            coordinates: {
                type: 'Point',
                coordinates: [location.lng, location.lat] // GeoJSON format: [lng, lat]
            },
            zoneName,
            timestamp: new Date()
        });

        // 2. REAL-TIME BROADCAST
        // Targeted emit to the specific firm's admin room to prevent cross-tenant leakage
        if (io) {
            io.to(`admin_room_${actor.tenantId}`).emit('ALERT_GEOFENCE_BREACH', {
                breachId: breachLog._id,
                actorName: actor.name,
                zoneName,
                location
            });
        }

        // 3. MULTI-CHANNEL ESCALATION
        // Fetch the firm administrator's contact details dynamically
        const firmAdmin = await User.findOne({
            tenantId: actor.tenantId,
            role: 'admin'
        }).select('email phone');

        const alertMessage = `🚨 GEOFENCE BREACH: Sheriff ${actor.name} has exited the authorized zone "${zoneName}". Timestamp: ${breachLog.timestamp.toISOString()}`;

        // Asynchronous triggers (don't 'await' these to keep the GPS processing loop fast)
        if (firmAdmin?.email) {
            sendEmail(firmAdmin.email, 'CRITICAL: Jurisdictional Breach Alert', alertMessage);
        }

        if (firmAdmin?.phone) {
            sendSMS(firmAdmin.phone, alertMessage);
        }

        logger.warn(`🛡️ [BREACH_HANDLED]: User ${actor.name} violated zone ${zoneName}.`);

    } catch (error) {
        logger.error(`💥 [BREACH_HANDLER_FAULT]: ${error.message}`);
    }
};

module.exports = { handleGeofenceBreach };