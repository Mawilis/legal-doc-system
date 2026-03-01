#!/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - ENTERPRISE REQUEST LOGGER                                      ║
  ║ Full audit trail | GDPR compliant | Real-time monitoring                 ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import pino from 'pino';
import { getCurrentContext } from './tenantContext.js';

// ============================================================================
// LOGGER CONFIGURATION
// ============================================================================

const logger = pino({
  name: 'wilsy-os-http',
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
    bindings: () => ({}),
    log: (obj) => {
      // Sanitize sensitive data
      const sanitized = { ...obj };
      if (sanitized.headers?.authorization) {
        sanitized.headers.authorization = '[REDACTED]';
      }
      if (sanitized.headers?.cookie) {
        sanitized.headers.cookie = '[REDACTED]';
      }
      return sanitized;
    },
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
      ignore: 'pid,hostname',
    },
  },
});

// ============================================================================
// METRICS COLLECTOR
// ============================================================================

const metrics = {
  requests: 0,
  responses: 0,
  errors: 0,
  totalLatency: 0,
  endpoints: new Map(),
};

// ============================================================================
// REQUEST LOGGER MIDDLEWARE - MAIN EXPORT
// ============================================================================

export const requestLogger = (req, res, next) => {
  const start = Date.now();
  metrics.requests++;

  // Store original end function
  const originalEnd = res.end;
  const chunks = [];

  // Override end function to capture response
  res.end = function (chunk, encoding, callback) {
    if (chunk) {
      chunks.push(chunk);
    }

    const responseTime = Date.now() - start;
    const context = getCurrentContext();

    // Calculate response size
    const responseSize = chunks.reduce((acc, chunk) => acc + (chunk.length || 0), 0);

    // Update metrics
    metrics.responses++;
    metrics.totalLatency += responseTime;

    const endpoint = `${req.method} ${req.route?.path || req.path}`;
    const endpointMetrics = metrics.endpoints.get(endpoint) || { count: 0, latency: 0 };
    endpointMetrics.count++;
    endpointMetrics.latency += responseTime;
    metrics.endpoints.set(endpoint, endpointMetrics);

    // Log the request
    const logData = {
      method: req.method,
      url: req.url,
      path: req.path,
      status: res.statusCode,
      responseTime: `${responseTime}ms`,
      responseSize: `${responseSize} bytes`,
      ip: req.ip,
      userAgent: req.get('user-agent'),
      referer: req.get('referer'),
      requestId: context.requestId,
      tenantId: context.tenantId,
      userId: context.userId,
    };

    if (res.statusCode >= 400) {
      metrics.errors++;
      logger.warn(logData, 'Request completed with error');
    } else {
      logger.info(logData, 'Request completed successfully');
    }

    // Call original end function
    originalEnd.call(this, chunk, encoding, callback);
  };

  next();
};

// ============================================================================
// METRICS ENDPOINT
// ============================================================================

export const getMetrics = (req, res) => {
  const averageLatency = metrics.responses > 0 ? metrics.totalLatency / metrics.responses : 0;

  const endpointStats = Array.from(metrics.endpoints.entries()).map(([endpoint, data]) => ({
    endpoint,
    count: data.count,
    averageLatency: data.latency / data.count,
  }));

  res.json({
    requests: metrics.requests,
    responses: metrics.responses,
    errors: metrics.errors,
    errorRate:
      metrics.responses > 0 ? ((metrics.errors / metrics.responses) * 100).toFixed(2) + '%' : '0%',
    averageLatency: `${averageLatency.toFixed(2)}ms`,
    endpoints: endpointStats,
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
};

// ============================================================================
// HEALTH CHECK ENDPOINT
// ============================================================================

export const healthCheck = (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || '3.0.0',
    metrics: {
      requests: metrics.requests,
      errors: metrics.errors,
    },
  });
};

// ============================================================================
// DEFAULT EXPORT
// ============================================================================

export default requestLogger;
