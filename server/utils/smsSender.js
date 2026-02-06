/*
 * File: server/utils/smsSender.js
 * STATUS: PRODUCTION-READY | RAPID DISPATCH GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages rapid-response mobile notifications. Handles South African number 
 * formatting and provides a resilient interface for the Twilio Gateway.
 * -----------------------------------------------------------------------------
 */

'use strict';

const twilio = require('twilio');
const logger = require('./logger');

// --- 1. CONFIGURATION & INITIALIZATION ---
const { TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER } = process.env;

let twilioClient = null;

if (TWILIO_ACCOUNT_SID && TWILIO_AUTH_TOKEN) {
    try {
        twilioClient = twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);
        logger.info('✅ [SMS_GATEWAY]: Twilio client initialized.');
    } catch (err) {
        logger.error(`💥 [SMS_INIT_FAULT]: ${err.message}`);
    }
} else {
    logger.warn('⚠️ [SMS_GATEWAY]: Credentials missing. SMS delivery disabled.');
}

// --- 2. FORENSIC HELPERS ---

/**
 * E.164 FORMATTER
 * Converts local SA numbers (082...) to international format (+2782...)
 */
const formatToE164 = (number) => {
    let cleaned = number.replace(/\D/g, ''); // Remove non-digits
    if (cleaned.startsWith('0')) {
        cleaned = '27' + cleaned.substring(1);
    }
    return cleaned.startsWith('+') ? cleaned : `+${cleaned}`;
};

// --- 3. DISPATCHER ---

/**
 * SEND TRANSACTIONAL SMS
 * @param {string} to - Recipient mobile number
 * @param {string} body - SMS content (Keep under 160 chars for 1-segment billing)
 */
const sendSMS = async (to, body) => {
    if (!twilioClient) {
        logger.error('❌ [SMS_DISPATCH_DENIED]: Gateway not configured.');
        return { success: false, error: 'GATEWAY_UNAVAILABLE' };
    }

    const formattedNumber = formatToE164(to);
    const maskedNumber = `${formattedNumber.substring(0, 5)}***${formattedNumber.slice(-4)}`;

    try {
        const message = await twilioClient.messages.create({
            body,
            from: TWILIO_PHONE_NUMBER,
            to: formattedNumber,
        });

        logger.info(`📱 [SMS_SENT]: SID ${message.sid} to ${maskedNumber}`);
        return { success: true, sid: message.sid };
    } catch (error) {
        logger.error(`💥 [SMS_FAULT]: Target ${maskedNumber} | Error: ${error.message}`);

        // Throwing allows the background worker to handle the retry strategy
        throw new Error(`SMS_PROVIDER_FAILURE: ${error.message}`);
    }
};

module.exports = { sendSMS };