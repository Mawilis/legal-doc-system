#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - CORRELATION ID MIDDLEWARE                                      ║
  ║ Distributed tracing | Request correlation | Production grade             ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

import { v4 as uuidv4 } from 'uuid';

/**
 * Correlation ID middleware for distributed tracing
 * Generates or propagates correlation IDs across requests
 */
export const correlationId = (req, res, next) => {
  // Get correlation ID from header or generate new one
  const correlationId = req.headers['x-correlation-id'] || req.headers['correlation-id'] || uuidv4();

  // Attach to request object
  req.correlationId = correlationId;

  // Set response header for client-side tracing
  res.setHeader('x-correlation-id', correlationId);

  // Store in res.locals for logging
  res.locals.correlationId = correlationId;

  next();
};

/**
 * Get current correlation ID from request
 */
export const getCorrelationId = (req) => req?.correlationId || 'unknown';

export default correlationId;
