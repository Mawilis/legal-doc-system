/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN REQUEST LOGGER MIDDLEWARE                           ║
 * ║ [FORENSIC LOGGING | AUDIT TRAIL | PERFORMANCE MONITORING]                ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'crypto';

/**
 * Request logging middleware
 * Logs all incoming requests with forensic detail
 */
export const requestLogger = (req, res, next) => {
  // Generate unique request ID if not already present
  if (!req.id) {
    req.id = `req_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
  }

  // Add timestamp
  req.timestamp = new Date().toISOString();

  // Log request details (sanitized)
  const logEntry = {
    id: req.id,
    timestamp: req.timestamp,
    method: req.method,
    url: req.originalUrl || req.url,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.headers['user-agent'] || 'unknown',
    userId: req.user?.id || 'unauthenticated',
    tenantId: req.tenantId || 'none',
    correlationId: req.headers['x-correlation-id'] || req.id
  };

  // Log to console (in production, this would go to a logging service)
  console.log(`[REQUEST] ${JSON.stringify(logEntry)}`);

  // Capture response data
  const originalEnd = res.end;
  const startTime = process.hrtime();

  res.end = function(chunk, encoding) {
    // Calculate response time
    const diff = process.hrtime(startTime);
    const responseTime = (diff[0] * 1e3 + diff[1] / 1e6).toFixed(2);

    // Log response
    const responseLog = {
      id: req.id,
      statusCode: res.statusCode,
      responseTime: `${responseTime}ms`,
      contentLength: res.getHeader('content-length') || 'unknown'
    };

    console.log(`[RESPONSE] ${JSON.stringify(responseLog)}`);

    originalEnd.call(this, chunk, encoding);
  };

  next();
};

export default requestLogger;
