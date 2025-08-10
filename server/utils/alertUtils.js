// ~/server/utils/alertUtils.js

const nodemailer = require('nodemailer');
const twilio = require('twilio');
const logger = require('./logger');

// --- Nodemailer (Email) Setup ---
// It's recommended to use a transactional email service like SendGrid or AWS SES in production.
const transporter = nodemailer.createTransport({
    service: 'gmail', // Or your preferred SMTP provider
    auth: {
        user: process.env.EMAIL_USER, // Your email address from .env
        pass: process.env.EMAIL_PASS, // Your email password or app-specific password from .env
    },
});

/**
 * Sends an email using the configured transporter.
 * @param {string} to - The recipient's email address.
 * @param {string} subject - The subject of the email.
 * @param {string} text - The plain text body of the email.
 * @param {string} [html] - Optional HTML body for the email.
 */
exports.sendEmail = async (to, subject, text, html) => {
    try {
        await transporter.sendMail({
            from: `"LegalDocSys Alerts" <${process.env.EMAIL_USER}>`,
            to,
            subject,
            text,
            html: html || text,
        });
        logger.info(`Email alert sent to ${to}`);
    } catch (error) {
        logger.error(`Failed to send email to ${to}: ${error.message}`);
    }
};


// --- Twilio (SMS) Setup ---
const twilioClient = twilio(process.env.TWILIO_SID, process.env.TWILIO_AUTH_TOKEN);

/**
 * Sends an SMS message using the Twilio client.
 * @param {string} to - The recipient's phone number (e.g., '+27821234567').
 * @param {string} body - The content of the SMS message.
 */
exports.sendSMS = async (to, body) => {
    try {
        await twilioClient.messages.create({
            body,
            from: process.env.TWILIO_PHONE_NUMBER, // Your Twilio phone number from .env
            to,
        });
        logger.info(`SMS alert sent to ${to}`);
    } catch (error) {
        logger.error(`Failed to send SMS to ${to}: ${error.message}`);
    }
};
