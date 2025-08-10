// ~/legal-doc-system/server/utils/auditLogger.js

const AuditLog = require('../models/auditLogModel'); // Assumes the Mongoose model is in this path
const logger = require('./logger'); // Assumes a standard logger like Winston

/**
 * A robust Express middleware to create a comprehensive audit log for every API request.
 * It captures request details, saves an initial log, and then updates it with the
 * response status and timing once the request is complete.
 *
 * @param {object} req - The Express request object.
 * @param {object} res - The Express response object.
 * @param {Function} next - The next middleware function in the chain.
 */
const auditLogger = async (req, res, next) => {
    // --- Capture Initial Request Details ---
    const startTime = Date.now();
    // Assumes you have authentication middleware that attaches the user object to `req`
    const user = req.user;

    const logData = {
        user: user?._id || null,
        email: user?.email || 'Guest', // Store email for quick reference
        method: req.method,
        path: req.originalUrl,
        ip: req.ip || req.connection.remoteAddress, // Get IP address reliably
        status: 'PENDING', // Initial status
    };

    try {
        // --- Create and Save the Initial Log Entry ---
        // We save the log immediately to record the attempt, even if the server crashes later.
        const log = new AuditLog(logData);
        await log.save();

        // --- Hijack the Response 'finish' Event ---
        // This is the modern, reliable way to capture details after the response has been sent.
        res.on('finish', async () => {
            try {
                // Determine the final status based on the HTTP status code.
                log.status = res.statusCode >= 400 ? 'FAILED' : 'SUCCESS';
                // Calculate the total time the server took to process the request.
                log.responseTime = Date.now() - startTime;
                // Save the updated log with the final status and response time.
                await log.save();
            } catch (err) {
                // Log any errors that occur during the final log update.
                logger.error('Failed to update audit log on response finish:', err);
            }
        });

    } catch (err) {
        // Log any errors that occur during the initial log creation.
        logger.error('Failed to create initial audit log:', err);
    }

    // --- Pass Control to the Next Middleware ---
    // The logging process happens in the background, so we don't block the request.
    next();
};

module.exports = auditLogger;
