// ~/server/utils/breachHandler.js

const GeofenceBreach = require('../models/geofenceBreachModel'); // Assuming a dedicated model for breaches
const { sendEmail, sendSMS } = require('./alertUtils');
const logger = require('./logger');

/**
 * A centralized function to handle all actions required when a geofence breach is detected.
 * This includes logging the breach to the database, emitting a real-time alert to the admin UI,
 * and sending external notifications via email and SMS.
 *
 * @param {object} io - The main Socket.IO server instance.
 * @param {object} user - The user object of the person who breached the geofence.
 * @param {object} location - The location object containing latitude and longitude.
 * @param {string} zoneName - The name of the geofence zone that was breached.
 */
const handleGeofenceBreach = async (io, user, location, zoneName) => {
    try {
        // 1. Log the breach to the dedicated GeofenceBreach collection for detailed analysis.
        const breachLog = await GeofenceBreach.create({
            user: user.id,
            coords: {
                lat: location.latitude,
                lng: location.longitude,
            },
            breachedZone: zoneName,
            alerted: true, // Mark that an alert is being sent
        });

        // 2. Emit a real-time event to all connected admin dashboards.
        const breachData = {
            user,
            breach: breachLog,
        };
        io.emit('sheriff:geofenceBreach', breachData);

        // 3. Send external alerts via email and SMS.
        const alertMessage = `🚨 GEOFENCE BREACH: Sheriff ${user.name} has left the "${zoneName}" at ${new Date().toLocaleTimeString()}.`;
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

        logger.info(`Successfully handled geofence breach for user: ${user.name}`);

    } catch (error) {
        logger.error(`Error in handleGeofenceBreach: ${error.message}`);
    }
};

module.exports = { handleGeofenceBreach };
