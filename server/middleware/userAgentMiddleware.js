/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/userAgentMiddleware.js
 *
 * User-Agent Requirement
 * ----------------------
 * Ensures User-Agent header is present for risk scoring and telemetry.
 */

const userAgentRequired = (req, res, next) => {
    const ua = req.headers['user-agent'];
    if (!ua || !ua.trim()) {
        return res.status(400).json({
            error: 'Missing User-Agent header.',
        });
    }
    next();
};

module.exports = { userAgentRequired };
