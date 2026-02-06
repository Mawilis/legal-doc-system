/*
 * File: server/middleware/correlationId.js
 * STATUS: PRODUCTION-READY | FORENSIC TRACEABILITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Assigns a unique, immutable identity to every request lifecycle.
 * This is the "Thread" that sews all logs together during a forensic audit.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Traceability: Allows you to search 'Correlation-ID' in logs to see the 
 * complete journey of a single request.
 * 2. Cross-Service Propagation: Pass this ID to any external microservices or 
 * internal background workers.
 * 3. Client-Side Visibility: Returns the ID in response headers so the frontend 
 * can report it during errors ("Please quote ID: XXX-XXX").
 * -----------------------------------------------------------------------------
 */

'use strict';

const { v4: uuidv4 } = require('uuid');

/**
 * CORRELATION ID MIDDLEWARE
 * Ensures every incoming request is tagged with a unique identifier.
 */
const correlationIdMiddleware = (req, res, next) => {
    try {
        // 1. IDENTITY RESOLUTION
        // Check if an ID already exists (e.g., passed from a Load Balancer or Frontend)
        const existingId = req.headers['x-correlation-id'] ||
            req.headers['x-request-id'] ||
            req.headers['correlation-id'];

        // 2. GENERATION
        // If no ID is present, we generate a new UUID v4.
        const correlationId = existingId || uuidv4();

        // 3. ATTACHMENT
        // We attach the ID to the request and a context object for logger accessibility.
        req.correlationId = correlationId;
        req.context = {
            ...req.context,
            correlationId
        };

        // 4. PROPAGATION
        // We set the header so the client/browser receives the ID in the response.
        res.setHeader('X-Correlation-Id', correlationId);

        next();
    } catch (err) {
        // FAIL-SAFE: If UUID generation fails (rare), log it and move on.
        // We never block a request because of a logging failure.
        console.error('CRITICAL_CORRELATION_ID_GENERATION_FAILURE:', err);
        next();
    }
};

/**
 * NOTE FOR ENGINEERS:
 * When making external API calls (e.g., to the AI service), always include 
 * 'X-Correlation-Id': req.correlationId in your request headers.
 */

module.exports = correlationIdMiddleware;