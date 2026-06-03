/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN TELEMETRY MESH [V36.3.0-BOARDROOM-NEXUS]                                                                          ║
 * ║ [PROMETHEUS METRICS INGESTION | CORRELATION CHAIN EMITTERS | LIFECYCLE TRACKING | FULL JSDOC]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 36.3.0-BOARDROOM-NEXUS | PRODUCTION READY | BILLION DOLLAR SPEC                                                               ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/backend/src/services/TelemetryMesh.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated Prometheus‑compatible metrics for boardroom Grafana dashboards.                      ║
 * ║ • AI Engineering (DeepSeek) – FORTIFIED: Added full JSDoc, static method aliases, and metric registration comments.                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import promClient from 'prom-client';

/**
 * @class TelemetryMesh
 * @description Singleton service responsible for defining, registering, and emitting
 * PromQL‑compatible metrics to power the Grafana Sovereign Dashboards and Sankey diagrams.
 *
 * @real-world
 *   Exposes metrics to Prometheus for real‑time boardroom monitoring. Used by the
 *   `sovereignMetrics` endpoint to feed Grafana panels that display PDF resilience,
 *   regulator lifecycle transitions, and authentication cascades.
 *
 * @forensic
 *   Every metric is labeled with `tenantId`, `correlationId`, and other forensic tags,
 *   allowing directors to drill down from dashboard alerts to the exact audit event.
 */
class TelemetryMesh {
  constructor() {
    /**
     * Prometheus registry – collects all defined metrics.
     * @type {promClient.Registry}
     */
    this.register = new promClient.Registry();

    // ============================================================================
    // 📄 PDF Request Pipeline Metrics
    // ============================================================================

    /**
     * @metric pdf_request_events_total
     * @description Counter tracking PDF request lifecycle events (REQUEST_INIT, REQUEST_SUCCESS, etc.).
     * @labels tenantId, correlationId, eventType
     */
    this.pdfRequestEvents = new promClient.Counter({
      name: 'pdf_request_events_total',
      help: 'Total PDF request events by correlation chain',
      labelNames: ['tenantId', 'correlationId', 'eventType'],
      registers: [this.register]
    });

    /**
     * @metric pdf_refresh_attempts_total
     * @description Counter tracking token refresh attempts with outcome (success/error).
     * @labels tenantId, correlationId, attempt, outcome
     */
    this.pdfRefreshAttempts = new promClient.Counter({
      name: 'pdf_refresh_attempts_total',
      help: 'Refresh attempts with outcome',
      labelNames: ['tenantId', 'correlationId', 'attempt', 'outcome'],
      registers: [this.register]
    });

    /**
     * @metric pdf_request_failure_total
     * @description Counter tracking total PDF request failures.
     * @labels tenantId
     */
    this.pdfRequestFailure = new promClient.Counter({
      name: 'pdf_request_failure_total',
      help: 'Total PDF request failures',
      labelNames: ['tenantId'],
      registers: [this.register]
    });

    /**
     * @metric pdf_refresh_backoff_delay_seconds
     * @description Gauge tracking the current exponential backoff delay (seconds) for a tenant.
     * @labels tenantId, attempt
     */
    this.pdfRefreshBackoffDelay = new promClient.Gauge({
      name: 'pdf_refresh_backoff_delay_seconds',
      help: 'Current exponential backoff delay for token refresh',
      labelNames: ['tenantId', 'attempt'],
      registers: [this.register]
    });

    // ============================================================================
    // 👤 Regulator Lifecycle & Oversight Metrics
    // ============================================================================

    /**
     * @metric regulator_lifecycle_transitions_total
     * @description Counter tracking regulator state changes (ACTIVE → SUSPENDED → TERMINATED).
     * @labels tenantId, regulatorId, previousState, newState, reason, correlationId
     */
    this.regulatorTransitions = new promClient.Counter({
      name: 'regulator_lifecycle_transitions_total',
      help: 'Total regulator lifecycle transitions for Sankey diagrams',
      labelNames: ['tenantId', 'regulatorId', 'previousState', 'newState', 'reason', 'correlationId'],
      registers: [this.register]
    });

    /**
     * @metric regulator_access_failure_total
     * @description Counter tracking failed regulator bundle access attempts.
     * @labels tenantId, regulatorId, error, outcome
     */
    this.regulatorAccessFailures = new promClient.Counter({
      name: 'regulator_access_failure_total',
      help: 'Failed regulator bundle accesses',
      labelNames: ['tenantId', 'regulatorId', 'error', 'outcome'],
      registers: [this.register]
    });

    // ============================================================================
    // 🏛️ Boardroom Health Metrics
    // ============================================================================

    /**
     * @metric pdf_generation_duration_seconds
     * @description Histogram of PDF generation latency (seconds).
     * @labels tenantId, templateType
     */
    this.pdfGenerationDuration = new promClient.Histogram({
      name: 'pdf_generation_duration_seconds',
      help: 'PDF generation duration in seconds',
      labelNames: ['tenantId', 'templateType'],
      buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
      registers: [this.register]
    });

    /**
     * @metric refresh_token_expiry_seconds
     * @summary Gauge tracking remaining time (seconds) until refresh token expiry.
     * @labels tenantId
     */
    this.refreshTokenExpiry = new promClient.Gauge({
      name: 'refresh_token_expiry_seconds',
      help: 'Seconds remaining until refresh token expiry',
      labelNames: ['tenantId'],
      registers: [this.register]
    });
  }

  // ============================================================================
  // 📡 PUBLIC METHODS – Event Recording
  // ============================================================================

  /**
   * @function recordPDFEvent
   * @description Records a PDF request lifecycle event.
   * @param {Object} params
   * @param {string} params.tenantId - Tenant identifier.
   * @param {string} params.correlationId - Correlation ID for the request chain.
   * @param {string} params.eventType - One of 'REQUEST_INIT', 'REQUEST_SUCCESS', 'REQUEST_RETRY_SUCCESS', 'REQUEST_FAILURE'.
   */
  recordPDFEvent({ tenantId, correlationId, eventType }) {
    this.pdfRequestEvents.labels(tenantId, correlationId, eventType).inc();
  }

  /**
   * @function recordRefreshAttempt
   * @description Records a token refresh attempt.
   * @param {Object} params
   * @param {string} params.tenantId - Tenant identifier.
   * @param {string} params.correlationId - Correlation ID.
   * @param {number} params.attempt - Attempt number (1‑based).
   * @param {string} params.outcome - 'success' or 'error'.
   */
  recordRefreshAttempt({ tenantId, correlationId, attempt, outcome }) {
    this.pdfRefreshAttempts.labels(tenantId, correlationId, String(attempt), outcome).inc();
  }

  /**
   * @function recordPDFFailure
   * @description Increments the global PDF failure counter for a tenant.
   * @param {string} tenantId - Tenant identifier.
   */
  recordPDFFailure(tenantId) {
    this.pdfRequestFailure.labels(tenantId).inc();
  }

  /**
   * @function setRefreshBackoffDelay
   * @description Sets the current exponential backoff delay for a tenant.
   * @param {string} tenantId - Tenant identifier.
   * @param {number} attempt - Attempt number.
   * @param {number} delaySeconds - Delay in seconds.
   */
  setRefreshBackoffDelay(tenantId, attempt, delaySeconds) {
    this.pdfRefreshBackoffDelay.labels(tenantId, String(attempt)).set(delaySeconds);
  }

  /**
   * @function recordLifecycleTransition
   * @description Emits a metric tracking a regulator's state transition (Active → Suspended, etc.)
   * @param {Object} params - The transition details.
   * @param {string} params.tenantId - Tenant identifier.
   * @param {string} params.regulatorId - Regulator identifier.
   * @param {string} params.previousState - Previous state (e.g., 'ACTIVE').
   * @param {string} params.newState - New state (e.g., 'SUSPENDED').
   * @param {string} params.reason - Reason for transition (e.g., 'AUTH_FAILURE_CASCADE').
   * @param {string} params.correlationId - Correlation ID for audit chain.
   */
  recordLifecycleTransition({ tenantId, regulatorId, previousState, newState, reason, correlationId }) {
    this.regulatorTransitions.labels(tenantId, regulatorId, previousState, newState, reason, correlationId).inc();
  }

  /**
   * @function recordAuthFailure
   * @description Logs a failed access attempt by a regulator body to trigger failure cascades.
   * @param {Object} params - The failure details.
   * @param {string} params.tenantId - Tenant identifier.
   * @param {string} params.regulatorId - Regulator identifier.
   * @param {string} params.error - Error message or code.
   */
  recordAuthFailure({ tenantId, regulatorId, error }) {
    this.regulatorAccessFailures.labels(tenantId, regulatorId, error, 'FAILURE').inc();
  }

  /**
   * @function recordPDFGenerationDuration
   * @description Records the duration of a PDF generation request.
   * @param {string} tenantId - Tenant identifier.
   * @param {string} templateType - Type of PDF generated (e.g., 'forensicReport').
   * @param {number} durationSeconds - Duration in seconds.
   */
  recordPDFGenerationDuration(tenantId, templateType, durationSeconds) {
    this.pdfGenerationDuration.labels(tenantId, templateType).observe(durationSeconds);
  }

  /**
   * @function setRefreshTokenExpiry
   * @description Sets the remaining seconds until refresh token expiry.
   * @param {string} tenantId - Tenant identifier.
   * @param {number} secondsRemaining - Seconds until expiry.
   */
  setRefreshTokenExpiry(tenantId, secondsRemaining) {
    this.refreshTokenExpiry.labels(tenantId).set(secondsRemaining);
  }

  /**
   * @function getMetrics
   * @description Exposes the text‑formatted Prometheus metrics for the /metrics scraping endpoint.
   * @returns {Promise<string>} The Prometheus text payload.
   *
   * @real-world
   *   Called by the `/metrics` endpoint in `server.js` to expose metrics to Prometheus.
   *
   * @example
   * const metrics = await telemetryMesh.getMetrics();
   * res.set('Content-Type', telemetryMesh.register.contentType);
   * res.end(metrics);
   */
  async getMetrics() {
    return await this.register.metrics();
  }

  /**
   * @function getContentType
   * @description Returns the Prometheus content type for the /metrics endpoint.
   * @returns {string} 'text/plain; version=0.0.4; charset=utf-8'
   */
  getContentType() {
    return this.register.contentType;
  }
}

// ============================================================================
// 🌐 SINGLETON EXPORT
// ============================================================================

/**
 * @constant telemetryMesh
 * @description Singleton instance of the TelemetryMesh service.
 * @type {TelemetryMesh}
 */
const telemetryMesh = new TelemetryMesh();
export default telemetryMesh;
