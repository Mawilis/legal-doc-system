/*
 * File: server/utils/alertUtils.js
 * STATUS: PRODUCTION-READY | RESILIENT COMMUNICATIONS
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The platform's messaging backbone. Interfaces with SMTP (Email) and 
 * SMS gateways. Designed to be called by Background Workers to ensure 
 * non-blocking performance.
 * -----------------------------------------------------------------------------
 */

'use strict';

const nodemailer = require('nodemailer');
const twilio = require('twilio');
const logger = require('./logger');

// --- 1. INDUSTRIAL GATEWAY CONFIGURATION ---

// EMAIL: Transporter Singleton
const transporter = nodemailer.createTransport({
    host: process.env.EMAIL_HOST || 'smtp.gmail.com',
    port: process.env.EMAIL_PORT || 465,
    secure: true,
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
    },
    // Production optimization: limit connection pool
    pool: true,
    maxConnections: 5,
    maxMessages: 100
});

// SMS: Twilio Singleton
let twilioClient;
if (process.env.TWILIO_SID && process.env.TWILIO_AUTH_TOKEN) {
    twilioClient = twilio(process.env.TWILIO_SID, process.env.TWILIO_AUTH_TOKEN);
}

// --- 2. ALERT ADAPTERS ---

/**
 * SEND TRANSACTIONAL EMAIL
 * Best Practice: Call this via notificationWorker to avoid blocking API threads.
 */
exports.sendEmail = async (to, subject, text, html) => {
    if (!process.env.EMAIL_USER) {
        logger.error('❌ [MAIL_SERVICE]: EMAIL_USER not configured in environment.');
        return false;
    }

    try {
        const info = await transporter.sendMail({
            from: `"Wilsy OS Notifications" <${process.env.EMAIL_USER}>`,
            to,
            subject,
            text,
            html: html || text,
        });

        logger.info(`📧 [MAIL_SENT]: ID ${info.messageId} to ${to}`);
        return true;
    } catch (error) {
        logger.error(`💥 [MAIL_FAULT]: Recipient ${to} | Error: ${error.message}`);
        // We throw the error so the BullMQ worker knows to retry
        throw error;
    }
};

/**
 * SEND STATUTORY SMS
 */
exports.sendSMS = async (to, body) => {
    if (!twilioClient) {
        logger.error('❌ [SMS_SERVICE]: Twilio client not initialized.');
        return false;
    }

    try {
        const message = await twilioClient.messages.create({
            body,
            from: process.env.TWILIO_PHONE_NUMBER,
            to,
        });

        logger.info(`📱 [SMS_SENT]: SID ${message.sid} to ${to}`);
        return true;
    } catch (error) {
        logger.error(`💥 [SMS_FAULT]: Recipient ${to} | Error: ${error.message}`);
        throw error;
    }
};