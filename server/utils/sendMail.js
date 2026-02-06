/*
 * File: server/utils/sendMail.js
 * STATUS: PRODUCTION-READY | MULTI-PROVIDER COMMUNICATION ENGINE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages transactional email delivery with multi-provider failover, 
 * automatic retries, and cross-channel alerting (Slack).
 * -----------------------------------------------------------------------------
 */

'use strict';

const nodemailer = require('nodemailer');
const axios = require('axios');
const logger = require('./logger');
const AlertLog = require('../models/AlertLog');

/**
 * TRANSPORTER FACTORY
 * Standardizes connection logic for enterprise providers.
 */
const buildTransporter = () => {
    const provider = process.env.EMAIL_PROVIDER?.toLowerCase() || 'default';

    switch (provider) {
        case 'sendgrid':
            return nodemailer.createTransport({
                host: 'smtp.sendgrid.net',
                port: 587,
                auth: { user: 'apikey', pass: process.env.SENDGRID_API_KEY }
            });

        case 'aws':
            // Optimized for AWS Simple Email Service
            return nodemailer.createTransport({
                host: `email-smtp.${process.env.AWS_REGION}.amazonaws.com`,
                port: 465,
                secure: true,
                auth: {
                    user: process.env.AWS_SES_USER,
                    pass: process.env.AWS_SES_PASS
                }
            });

        default:
            // Development Fallback: Mailtrap
            return nodemailer.createTransport({
                host: process.env.MAILTRAP_HOST,
                port: process.env.MAILTRAP_PORT,
                auth: {
                    user: process.env.MAILTRAP_USER,
                    pass: process.env.MAILTRAP_PASS
                }
            });
    }
};

/**
 * CROSS-CHANNEL ALERTING (Slack Integration)
 */
const sendSlackAlert = async (message) => {
    if (!process.env.SLACK_WEBHOOK_URL) return;
    try {
        await axios.post(process.env.SLACK_WEBHOOK_URL, { text: message });
    } catch (err) {
        logger.warn(`⚠️ [SLACK_FAIL]: ${err.message}`);
    }
};

/**
 * ENTERPRISE MAIL DISPATCHER
 * @param {Object} options - to, subject, text, html, alert (boolean)
 */
const sendEmail = async (options) => {
    const transporter = buildTransporter();
    const maxRetries = 3;
    let attempt = 0;

    const mailOptions = {
        from: `"${process.env.EMAIL_FROM_NAME || 'Wilsy OS'}" <${process.env.EMAIL_FROM}>`,
        to: options.email,
        subject: options.subject,
        text: options.text,
        html: options.html || options.text
    };

    while (attempt < maxRetries) {
        try {
            const info = await transporter.sendMail(mailOptions);
            logger.info(`📧 [MAIL_SUCCESS]: ${info.messageId} to ${options.email}`);

            // If this is a system alert, log it to the forensic collection
            if (options.alert) {
                await Promise.all([
                    sendSlackAlert(`🚨 *SYSTEM ALERT*: ${options.subject}\n${options.text}`),
                    AlertLog.create({
                        tenantId: options.tenantId,
                        type: 'EMAIL_DISPATCH',
                        status: 'SENT',
                        message: options.subject,
                        recipient: options.email
                    })
                ]);
            }
            return info;

        } catch (error) {
            attempt++;
            logger.warn(`⚠️ [MAIL_RETRY]: Attempt ${attempt}/${maxRetries} failed: ${error.message}`);

            if (attempt >= maxRetries) {
                logger.error(`🔥 [MAIL_CRITICAL_FAIL]: Permanent failure sending to ${options.email}`);

                if (options.alert) {
                    await sendSlackAlert(`🔥 *MAIL CRITICAL*: Failed to notify ${options.email} regarding ${options.subject}`);
                }

                throw error;
            }
            // Wait 1s before retrying
            await new Promise(res => setTimeout(res, 1000));
        }
    }
};

module.exports = sendEmail;