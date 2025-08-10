// ~/server/utils/smsSender.js

const twilio = require('twilio');
const logger = require('./logger'); // Assuming a standard logger like Winston

// --- Twilio Client Initialization ---
// It's crucial to pull these credentials from environment variables for security.
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const fromNumber = process.env.TWILIO_PHONE_NUMBER;

// Ensure all required Twilio credentials are present before initializing the client.
let twilioClient;
if (accountSid && authToken && fromNumber) {
    twilioClient = twilio(accountSid, authToken);
} else {
    logger.warn('Twilio credentials are not fully configured in .env file. SMS sending will be disabled.');
}

/**
 * Sends an SMS message using the configured Twilio client.
 * It includes robust error handling and will not attempt to send if the client is not configured.
 *
 * @param {string} to - The recipient's phone number in E.164 format (e.g., '+27821234567').
 * @param {string} body - The content of the SMS message.
 * @returns {Promise<void>}
 */
const sendSMS = async (to, body) => {
    // Only proceed if the Twilio client was successfully initialized.
    if (!twilioClient) {
        logger.error('Cannot send SMS: Twilio client is not configured.');
        return;
    }

    try {
        await twilioClient.messages.create({
            body,
            from: fromNumber,
            to,
        });
        logger.info(`SMS alert sent successfully to ${to}`);
    } catch (error) {
        logger.error(`Failed to send SMS to ${to}: ${error.message}`);
    }
};

module.exports = { sendSMS };
