/*
 * File: server/middleware/userAgentMiddleware.js
 * STATUS: PRODUCTION-READY | SECURITY TELEMETRY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Mandates the presence of a User-Agent header for every request. This is 
 * essential for device fingerprinting, risk scoring, and traffic analysis.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Anti-Bot Baseline: Blocks the simplest class of headless automated scrapers.
 * 2. Risk Context: Attaches device/browser strings to the request lifecycle.
 * 3. Structured Errors: Provides clear feedback for API integration developers.
 * 4. Audit-Ready: Logs missing identity headers as security warnings.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { emitAudit } = require('./auditMiddleware');

/**
 * USER-AGENT REQUIREMENT MIDDLEWARE
 */
const userAgentRequired = async (req, res, next) => {
    try {
        const ua = req.headers['user-agent'];

        // 1. VALIDATION: Block requests with empty or missing User-Agent
        if (!ua || !ua.trim()) {
            // Log the suspicious activity for forensic review
            await emitAudit(req, {
                resource: 'user_agent',
                action: 'DENIED_MISSING_UA',
                severity: 'warning',
                metadata: {
                    ip: req.ip,
                    path: req.originalUrl,
                    method: req.method
                }
            });

            return res.status(400).json({
                success: false,
                status: 'error',
                code: 'ERR_MISSING_USER_AGENT',
                message: 'Security Requirement: A valid User-Agent header is required for all API requests.',
                correlationId: req.correlationId || req.context?.correlationId
            });
        }

        // 2. NORMALIZATION
        // Clean the string and attach to the context for downstream logging
        const sanitizedUA = ua.trim();
        req.context = {
            ...req.context,
            userAgent: sanitizedUA
        };

        // 3. TELEMETRY LOGGING (Info Level)
        // We log the capture once, then it is available for all other logs.
        if (req.logAudit) {
            await req.logAudit('USER_AGENT_CAPTURED', {
                userAgent: sanitizedUA
            });
        }

        next();
    } catch (err) {
        // FAIL-SAFE: Log internal errors but don't leak logic to the client
        console.error('USER_AGENT_MIDDLEWARE_FAULT:', err);

        return res.status(500).json({
            success: false,
            status: 'error',
            code: 'ERR_UA_PROCESSOR_FAULT',
            message: 'An internal error occurred during security header processing.',
            correlationId: req.correlationId || req.context?.correlationId
        });
    }
};

module.exports = { userAgentRequired };