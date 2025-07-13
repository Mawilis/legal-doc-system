const nodemailer = require('nodemailer');
const logger = require('./logger');
const axios = require('axios');
const AlertLog = require('../models/alertLogModel'); // optional MongoDB alert storage

/**
 * Build a nodemailer transporter based on environment + provider.
 * Can optionally inject a mock transporter for testing.
 */
const buildTransporter = (overrideTransport = null) => {
    if (overrideTransport) return overrideTransport;

    const provider = process.env.EMAIL_PROVIDER || 'default';

    switch (provider.toLowerCase()) {
        case 'sendgrid':
            return nodemailer.createTransport({
                host: 'smtp.sendgrid.net',
                port: 587,
                auth: {
                    user: 'apikey',
                    pass: process.env.SENDGRID_API_KEY,
                },
            });

        case 'aws':
            return nodemailer.createTransport({
                SES: { apiVersion: '2010-12-01' },
                accessKeyId: process.env.AWS_SES_ACCESS_KEY_ID,
                secretAccessKey: process.env.AWS_SES_SECRET_ACCESS_KEY,
                region: process.env.AWS_SES_REGION,
            });

        case 'gmail':
            return nodemailer.createTransport({
                service: 'gmail',
                auth: {
                    user: process.env.EMAIL_USERNAME,
                    pass: process.env.EMAIL_PASSWORD,
                },
            });

        case 'default':
        default:
            if (process.env.NODE_ENV === 'production') {
                return nodemailer.createTransport({
                    service: 'gmail',
                    auth: {
                        user: process.env.EMAIL_USERNAME,
                        pass: process.env.EMAIL_PASSWORD,
                    },
                });
            } else {
                return nodemailer.createTransport({
                    host: process.env.MAILTRAP_HOST,
                    port: process.env.MAILTRAP_PORT,
                    auth: {
                        user: process.env.MAILTRAP_USERNAME,
                        pass: process.env.MAILTRAP_PASSWORD,
                    },
                });
            }
    }
};

/**
 * Optionally send alert to Slack
 */
const sendSlackAlert = async (message) => {
    const webhook = process.env.SLACK_ALERT_WEBHOOK;
    if (!webhook) return;

    try {
        await axios.post(webhook, { text: message });
        logger.info('✅ Slack alert sent.');
    } catch (error) {
        logger.warn(`⚠️ Failed to send Slack alert: ${error.message}`);
    }
};

/**
 * Send an email with retry logic.
 * @param {Object} options Email options
 * @param {string} options.email - Recipient email
 * @param {string} options.subject - Subject line
 * @param {string} options.text - Plain text message
 * @param {string} [options.html] - Optional HTML message
 * @param {boolean} [options.alert] - If true, send alert to Slack and save in DB
 * @param {Object} [overrideTransport] - Optional transport mock for testing
 */
const sendEmail = async (options, overrideTransport = null) => {
    const transporter = buildTransporter(overrideTransport);

    if (!options.email || !/\S+@\S+\.\S+/.test(options.email)) {
        throw new Error('A valid email address is required.');
    }

    const mailOptions = {
        from: `"${process.env.EMAIL_FROM_NAME || 'Legal Doc System'}" <${process.env.EMAIL_FROM || 'noreply@legaldoc.com'}>`,
        to: options.email,
        subject: options.subject,
        text: options.text,
        html: options.html,
    };

    const maxRetries = 3;
    let attempt = 0;

    while (attempt < maxRetries) {
        try {
            const info = await transporter.sendMail(mailOptions);
            logger.info(`📧 Email sent: ${info.messageId}`);

            if (process.env.NODE_ENV !== 'production') {
                const previewUrl = nodemailer.getTestMessageUrl(info);
                if (previewUrl) {
                    logger.debug(`🔎 Preview URL: ${previewUrl}`);
                }
            }

            // --- Log alert if needed
            if (options.alert) {
                await sendSlackAlert(`🚨 ${options.subject}\n${options.text}`);

                // Save to MongoDB AlertLog
                await AlertLog.create({
                    type: 'email',
                    message: options.subject,
                    context: options.text,
                });
            }

            return info;
        } catch (error) {
            attempt += 1;
            logger.warn(`❌ Attempt ${attempt} failed: ${error.message}`);

            if (attempt >= maxRetries) {
                logger.error(`🚨 All ${maxRetries} attempts failed to send email.`);

                // Optional alert on final failure
                await sendSlackAlert(`🔥 Email failed after ${maxRetries} attempts.\nSubject: ${options.subject}`);

                throw new Error('Email service failed after multiple attempts.');
            }
        }
    }
};

module.exports = sendEmail;
