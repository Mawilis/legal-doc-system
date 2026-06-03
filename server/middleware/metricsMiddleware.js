/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - SOVEREIGN METRICS MIDDLEWARE [OMEGA SINGULARITY]                                      #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/metricsMiddleware.js    #
 * ####################################################################################################
 * # [PERFORMANCE METRICS | SYSTEM MONITORING | FORENSIC DATA]                                       #
 * # EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                                           #
 * ####################################################################################################
 *
 * 👥 COLLABORATION:
 * • Wilson Khanyezi (Lead Architect) - Metrics design
 * • Gemini (AI Engineering) - ESM hardening
 *
 * @last_verified: 2026-04-10
 */

// Metrics store
const metrics = {
  totalRequests: 0,
  requestsByMethod: {},
  requestsByEndpoint: {},
  responseTimes: [],
  statusCodes: {},
  startTime: Date.now()
};

/**
 * Metrics collection middleware
 * Tracks request metrics for monitoring and forensics
 */
export const metricsMiddleware = (req, res, next) => {
  // Increment total requests
  metrics.totalRequests++;

  // Track by method
  const method = req.method;
  metrics.requestsByMethod[method] = (metrics.requestsByMethod[method] || 0) + 1;

  // Track by endpoint (sanitized - remove IDs)
  let endpoint = req.route?.path || req.path;
  endpoint = endpoint.replace(/\/[0-9a-f]{24,}/gi, '/:id').replace(/\/[0-9]+/g, '/:id');
  metrics.requestsByEndpoint[endpoint] = (metrics.requestsByEndpoint[endpoint] || 0) + 1;

  // Track start time for response time calculation
  const start = process.hrtime();

  // Capture response
  const originalEnd = res.end;

  res.end = function(chunk, encoding) {
    // Calculate response time
    const diff = process.hrtime(start);
    const responseTime = (diff[0] * 1e3 + diff[1] / 1e6);

    // Store response time (keep last 1000)
    metrics.responseTimes.push({
      time: responseTime,
      timestamp: Date.now()
    });
    if (metrics.responseTimes.length > 1000) {
      metrics.responseTimes.shift();
    }

    // Track status code
    const statusCode = res.statusCode;
    metrics.statusCodes[statusCode] = (metrics.statusCodes[statusCode] || 0) + 1;

    originalEnd.call(this, chunk, encoding);
  };

  // Attach metrics to request for route handlers
  req.metrics = {
    getSummary: () => getMetricsSummary()
  };

  next();
};

/**
 * Get metrics summary
 * @returns {Object} Metrics summary
 */
export const getMetricsSummary = () => {
  const now = Date.now();
  const uptime = now - metrics.startTime;

  // Calculate average response time
  const avgResponseTime = metrics.responseTimes.length > 0
    ? metrics.responseTimes.reduce((sum, r) => sum + r.time, 0) / metrics.responseTimes.length
    : 0;

  // Calculate requests per second (last minute)
  const oneMinuteAgo = now - 60000;
  const recentRequests = metrics.responseTimes.filter(r => r.timestamp > oneMinuteAgo).length;
  const rps = recentRequests / 60;

  return {
    uptime,
    totalRequests: metrics.totalRequests,
    requestsPerSecond: rps.toFixed(2),
    averageResponseTime: avgResponseTime.toFixed(2),
    requestsByMethod: metrics.requestsByMethod,
    requestsByEndpoint: metrics.requestsByEndpoint,
    statusCodes: metrics.statusCodes,
    timestamp: new Date().toISOString()
  };
};

/**
 * Metrics endpoint handler
 * @param {Object} req - Express request
 * @param {Object} res - Express response
 */
export const metricsHandler = (req, res) => {
  res.json({
    success: true,
    data: getMetricsSummary()
  });
};

export default metricsMiddleware;
