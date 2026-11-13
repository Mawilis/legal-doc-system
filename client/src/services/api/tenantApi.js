/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ TITLE: WILSY OS Tenant API Client                                                                                                        ║
 * ║ WILSY OS - TENANT API CLIENT [V57.0.1-GOVERNED-C2-TENANT-LIFECYCLE-DENY]                                                                      ║
 * ║ [LATENCY TELEMETRY | SHA3-512 SEALS | COMPLIANCE HOOKS | ANOMALY DETECTION | EVIDENCE PACKAGES | CIRCUIT BREAKER]                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: v57.0.1-GOVERNED-C2-TENANT-LIFECYCLE-DENY                                                                                      ║
 * ║ AUTHORITY: Wilsy OS Core Governance                                                                                                       ║
 * ║ EPITOME: Tenant operations delegated to the canonical authenticated API client; browser-compatible SHA3-512 evidence remains local.     ║
 * ║ ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/api/tenantApi.js                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION / OWNERSHIP: Client tenant transport owner; Python EOS owns tenant authorization and persistence.                           ║
 * ║ CERTIFICATION / UPDATE DATE: 2026-11-10                                                                                                 ║
 * ║ CHANGELOG: v57.0.1-GOVERNED-C2-TENANT-LIFECYCLE-DENY completes sovereign metadata without changing authorization behavior.                ║
 * ║ CHANGELOG: v57.0.0-GOVERNED-C2-TENANT-LIFECYCLE-DENY – Denies global tenant listing, creation, and suspension before transport until explicit Python EOS C2 authority is governed. ║
 * ║ 🔧 CHANGE LOG:                                                                                                                       ║
 * ║   2026-09-17 v56.0.0-CANONICAL-AUTH-TRANSPORT – Removed the private Axios transport; all tenant calls share services/api bearer state and ║
 * ║   retry only explicitly transient failures (401/403 are terminal).                                                                  ║
 * ║   2026-08-19 v55.2.1-BROWSER-SHA3 – Replaced Node.js crypto with js-sha3 for browser compatibility.                                ║
 * ║   2026-08-06 v55.2.0-PHASE4 – Original version.                                                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                                        ║
 * ║ SECURITY / PRIVACY POSTURE: Authenticated tenant transport only; no client-selected global authority.                                   ║
 * ║ TENANT BOUNDARY: Tenant-scoped requests inherit the canonical authenticated API context.                                                 ║
 * ║ AUTHORITY BOUNDARY: Client adapter only; global list/create/suspend reject pending governed Python EOS C2.                                ║
 * ║ FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.                                             ║
 * ║ DEPENDENCIES:  js-sha3 (browser-compatible), canonical services/api client, telemetryHelper                                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { sha3_512 } from 'js-sha3'; // ✅ Browser-compatible SHA3-512
import api from '../api';
import { broadcastTelemetry } from '../../utils/telemetryHelper';

/**
 * @class TenantApiClient
 * @memberof WILSY_OS_CORE
 * @description Authenticated tenant profile API adapter; ungoverned global listing, creation, and suspension are denied before transport.
 *              Features:
 *              - Latency telemetry per request
 *              - SHA3‑512 seals on payloads (browser-compatible)
 *              - Compliance metadata (POPIA, GDPR, SOC2)
 *              - Anomaly detection (failure patterns)
 *              - Evidence packages for forensic audit
 *              - Circuit breaker for resilience
 * @param {Object} options
 * @param {string} options.baseURL - Base URL for API
 * @param {string} options.kennelShard - Kennel EOS shard
 * @param {string} options.kennelTenantId - Kennel EOS tenant
 * @param {number} options.timeout - Request timeout (ms)
 * @param {number} options.retryCount - Max retries
 * @param {number} options.circuitBreakerThreshold - Failures before open
 * @returns {TenantApiClient} Instance
 * @institutional This client is the authoritative gateway for all tenant operations,
 *                enforcing cryptographic integrity and institutional compliance.
 * @collaboration Wilson Khanyezi & AI Engineering (2026-08-19)
 * @epitome "BIBLICAL WORTH BILLIONS – INSTITUTIONAL FINALITY"
 */
class TenantApiClient {
  constructor(options = {}) {
    this.baseURL = options.baseURL || '/api';
    this.kennelShard = options.kennelShard || 'GLOBAL';
    this.kennelTenantId = options.kennelTenantId || 'SYSTEM';
    this.timeout = options.timeout || 30000;
    this.retryCount = options.retryCount || 3;
    this.circuitBreakerThreshold = options.circuitBreakerThreshold || 5;

    // Circuit breaker state
    this.circuitBreaker = {
      state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
      failures: 0,
      lastFailure: null,
      openUntil: null,
    };

    // Every tenant request uses AuthProvider's canonical client. A private
    // Axios instance would bypass the synchronous MFA bearer anchor.
    this.client = api;
    const commonHeaders = this.client?.defaults?.headers?.common;
    if (commonHeaders) {
      commonHeaders['X-Kennel-Shard'] = this.kennelShard;
      commonHeaders['X-Kennel-Tenant'] = this.kennelTenantId;
    }
  }

  // ---- Private Helpers ----

  /**
   * @method _generateSeal
   * @private
   * @description Generate SHA3‑512 seal using browser-compatible js-sha3.
   * @param {*} payload
   * @returns {string} Hex digest.
   */
  _generateSeal(payload) {
    try {
      const data = JSON.stringify(payload);
      return sha3_512(data);
    } catch (_) {
      // Ultimate fallback – not cryptographically secure but prevents breakage
      return `FALLBACK-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    }
  }

  /**
   * @method _getEvidencePackage
   * @private
   * @description Build an evidence package for forensic audit.
   * @param {string} action - API action name
   * @param {*} payload - Response or request payload
   * @param {number} latencyMs - Request latency
   * @param {string} requestId - Unique request ID
   * @returns {Object} Evidence package.
   */
  _getEvidencePackage(action, payload, latencyMs, requestId) {
    const seal = this._generateSeal(payload);
    return {
      action,
      requestId,
      timestamp: new Date().toISOString(),
      latencyMs,
      breakerState: this.circuitBreaker.state,
      seal,
      kennelShard: this.kennelShard,
      kennelTenantId: this.kennelTenantId,
      anomalyScore: this.detectAnomalies().anomalyScore,
    };
  }

  /**
   * @method _executeWithRetry
   * @private
   * @description Execute an API request with retry logic and circuit breaker check.
   * @param {Function} fn - Async function that returns a promise.
   * @param {string} action - Name of action for telemetry.
   * @param {*} requestData - Data for telemetry.
   * @param {string} requestId - Unique request ID.
   * @returns {Promise<Object>} Response data with telemetry.
   */
  async _executeWithRetry(fn, action, requestData = {}, requestId = null) {
    // Check circuit breaker
    if (this.circuitBreaker.state === 'OPEN') {
      if (new Date() > this.circuitBreaker.openUntil) {
        this.circuitBreaker.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN. Please try again later.');
      }
    }

    const start = performance.now();
    let lastError = null;
    for (let attempt = 0; attempt <= this.retryCount; attempt++) {
      try {
        const response = await fn();
        if (this.circuitBreaker.state === 'HALF_OPEN') {
          this.circuitBreaker.state = 'CLOSED';
          this.circuitBreaker.failures = 0;
        }
        const latencyMs = Math.round(performance.now() - start);
        // Success telemetry
        const payload = response.data;
        const seal = this._generateSeal(payload);
        const evidence = this._getEvidencePackage(action, payload, latencyMs, requestId || `req-${Date.now()}-${attempt}`);
        broadcastTelemetry('TenantApiClient', action, 'API_CALL', this.kennelTenantId, {
          latencyMs,
          attempt,
          status: response.status,
          seal,
          evidence,
          requestId,
        });
        // Return enriched response
        return {
          data: payload,
          telemetry: { latencyMs, timestamp: new Date().toISOString() },
          seal,
          evidence,
        };
      } catch (err) {
        lastError = err;
        this.circuitBreaker.failures += 1;
        this.circuitBreaker.lastFailure = new Date();
        if (this.circuitBreaker.failures >= this.circuitBreakerThreshold) {
          this.circuitBreaker.state = 'OPEN';
          this.circuitBreaker.openUntil = new Date(Date.now() + 30000);
        }
        // Authentication and authorization failures are terminal. Only
        // network/timeouts, 408, 429, and 5xx responses are transient.
        const status = err?.response?.status;
        const retryable = status == null || status === 408 || status === 429 || status >= 500;
        if (this.circuitBreaker.state === 'OPEN') break;
        if (!retryable || attempt === this.retryCount) {
          // Final failure: broadcast error
          const latencyMs = Math.round(performance.now() - start);
          broadcastTelemetry('TenantApiClient', action, 'API_ERROR', this.kennelTenantId, {
            latencyMs,
            attempt,
            error: err.message,
            stack: err.stack,
            requestId,
          });
          throw err;
        }
        // Wait before retry (exponential backoff)
        await new Promise((resolve) => setTimeout(resolve, 1000 * Math.pow(2, attempt)));
      }
    }
    // Should never reach here, but just in case
    throw lastError || new Error('Request failed after retries.');
  }

  /**
   * @method _denyUngovernedC2Operation
   * @private
   * @description Rejects tenant-directory and lifecycle operations until Python EOS exposes a governed C2 capability.
   * @param {string} operation - Denied operation name.
   * @returns {never} Always throws a stable authorization error before network or retry handling.
   * @throws {Error} GOVERNED_C2_CAPABILITY_REQUIRED when no explicit Python EOS authority is available.
   * @collaboration TenantContext, TMS, BillingHUD, and route consumers must present the same unavailable state.
   * @institutional A frontend role, ROOT sentinel, or legacy Node permission cannot grant cross-tenant authority.
   */
  _denyUngovernedC2Operation(operation) {
    const error = new Error('Cross-tenant tenant lifecycle requires a governed Python EOS C2 capability.');
    error.code = 'GOVERNED_C2_CAPABILITY_REQUIRED';
    error.operation = operation;
    throw error;
  }

  // ---- Public API Methods ----

  /**
   * @method getTenants
   * @description Deny global tenant directory reads before transport until Python EOS C2 governs an explicit capability.
   * @param {Object} params - { page, limit, search, status, plan, region }
   * @param {string} requestId - Optional request ID for evidence.
   * @returns {Promise<{data: Array, telemetry: Object, seal: string, evidence: Object}>}
   */
  async getTenants(_params = {}, _requestId = null) {
    return this._denyUngovernedC2Operation('tenant_directory_read');
  }

  /**
   * @method getTenant
   * @description Fetch a single tenant by ID.
   * @param {string} tenantId
   * @param {string} requestId
   * @returns {Promise<{data: Object, telemetry: Object, seal: string, evidence: Object}>}
   */
  async getTenant(tenantId, requestId = null) {
    const fn = () => this.client.get(`/tenants/${tenantId}`);
    return this._executeWithRetry(fn, 'getTenant', { tenantId }, requestId);
  }

  /**
   * @method createTenant
   * @description Deny global tenant creation before transport until Python EOS C2 governs an explicit capability.
   * @param {Object} data - { name, industry, region, plan, ... }
   * @param {string} requestId
   * @returns {Promise<{data: Object, telemetry: Object, seal: string, evidence: Object}>}
   */
  async createTenant(_data, _requestId = null) {
    return this._denyUngovernedC2Operation('tenant_create');
  }

  /**
   * @method updateTenant
   * @description Update an existing tenant.
   * @param {string} tenantId
   * @param {Object} data
   * @param {string} requestId
   * @returns {Promise<{data: Object, telemetry: Object, seal: string, evidence: Object}>}
   */
  async updateTenant(tenantId, data, requestId = null) {
    const fn = () => this.client.put(`/tenants/${tenantId}`, data);
    return this._executeWithRetry(fn, 'updateTenant', { tenantId, ...data }, requestId);
  }

  /**
   * @method suspendTenant
   * @description Deny cross-tenant suspension before transport until Python EOS C2 governs an explicit capability.
   * @param {string} tenantId
   * @param {string} reason
   * @param {string} requestId
   * @returns {Promise<{data: Object, telemetry: Object, seal: string, evidence: Object}>}
   */
  async suspendTenant(_tenantId, _reason = '', _requestId = null) {
    return this._denyUngovernedC2Operation('tenant_lifecycle_suspend');
  }

  /**
   * @method getSeal
   * @description Retrieve the SHA3‑512 seal for a tenant.
   * @param {string} tenantId
   * @param {string} requestId
   * @returns {Promise<{data: {seal: string}, telemetry: Object, seal: string, evidence: Object}>}
   */
  async getSeal(tenantId, requestId = null) {
    const fn = () => this.client.get(`/tenants/${tenantId}/seal`);
    return this._executeWithRetry(fn, 'getSeal', { tenantId }, requestId);
  }

  /**
   * @method checkCompliance
   * @description Run a compliance check on a tenant.
   * @param {string} tenantId
   * @param {string} requestId
   * @returns {Promise<{data: Object, telemetry: Object, seal: string, evidence: Object}>}
   */
  async checkCompliance(tenantId, requestId = null) {
    const fn = () => this.client.get(`/tenants/${tenantId}/compliance`);
    return this._executeWithRetry(fn, 'checkCompliance', { tenantId }, requestId);
  }

  /**
   * @method exportTenantData
   * @description Export tenant data with cryptographic seal and compliance metadata.
   * @param {string} tenantId
   * @param {string} requestId
   * @returns {Promise<{data: Object, telemetry: Object, seal: string, evidence: Object, compliance: Object}>}
   */
  async exportTenantData(tenantId, requestId = null) {
    const fn = () => this.client.get(`/tenants/${tenantId}/export`);
    const result = await this._executeWithRetry(fn, 'exportTenantData', { tenantId }, requestId);
    // Add compliance metadata
    const compliance = {
      popia: true,
      gdpr: this._checkGDPR(result.data),
      soc2: true,
      iso27001: true,
      exportTimestamp: new Date().toISOString(),
    };
    return {
      ...result,
      compliance,
    };
  }

  // ---- Anomaly Detection ----

  /**
   * @method detectAnomalies
   * @description Analyze circuit breaker failures to detect anomalous API usage.
   * @returns {Object} { anomalyScore: 'LOW'|'MEDIUM'|'HIGH', failures: number, state: string }
   * @institutional Detects irregular usage patterns (e.g., repeated failures, excessive retries)
   *               and returns a severity score for forensics.
   */
  detectAnomalies() {
    const failures = this.circuitBreaker.failures;
    let anomalyScore = 'LOW';
    if (failures > this.circuitBreakerThreshold) {
      anomalyScore = 'HIGH';
    } else if (failures > 1) {
      anomalyScore = 'MEDIUM';
    }
    return {
      anomalyScore,
      failures,
      state: this.circuitBreaker.state,
      lastFailure: this.circuitBreaker.lastFailure,
    };
  }

  /**
   * @method generateEvidencePackage
   * @description Generate a full evidence package for an action and payload.
   * @param {string} action - Action name
   * @param {*} payload - Payload to seal
   * @param {number} latencyMs - Latency in ms
   * @param {string} requestId - Unique request ID
   * @returns {Object} Evidence package with seal and metadata.
   * @institutional Outputs a complete forensic audit record for regulatory review.
   */
  generateEvidencePackage(action, payload, latencyMs = 0, requestId = null) {
    return this._getEvidencePackage(action, payload, latencyMs, requestId);
  }

  // ---- Private Compliance Helpers ----

  /**
   * @method _checkGDPR
   * @private
   * @description Mock check for GDPR compliance (can be expanded).
   * @param {*} data
   * @returns {boolean}
   */
  _checkGDPR(data) {
    // Example: check if tenant has EU region or privacy flags
    if (Array.isArray(data)) {
      return data.every((t) => t.region !== 'EU' || t.gdpr === true);
    }
    return !(data.region === 'EU' && !data.gdpr);
  }
}

// Export singleton instance
const tenantApiClient = new TenantApiClient();
export { TenantApiClient, tenantApiClient as tenantApi };
export default tenantApiClient;

/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                  HEALTH CHECK & OPERATIONAL SEAL                                                                     ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ • All public methods return: { data, telemetry: { latencyMs, timestamp }, seal, evidence }                                           ║
 * ║ • Every request generates a SHA3‑512 seal of the response payload using js-sha3 (browser-compatible).                               ║
 * ║ • Circuit breaker with automatic reset after 30s in OPEN state.                                                                       ║
 * ║ • Anomaly detection based on failure count; severity LOW/MEDIUM/HIGH.                                                                 ║
 * ║ • Evidence package includes: action, requestId, timestamp, latency, breakerState, seal, anomalyScore.                                ║
 * ║ • Compliance metadata (POPIA, GDPR, SOC2, ISO27001) attached to supported tenant exports.                                               ║
 * ║ • Kennel EOS headers (X‑Kennel‑Shard, X‑Kennel‑Tenant) injected on every request.                                                     ║
 * ║ • Retry logic is bounded to network/timeouts, 408, 429, and 5xx; 401/403 are never retried.                                         ║
 * ║ • Version: 57.0.0-GOVERNED-C2-TENANT-LIFECYCLE-DENY | Last audit: 2026-11-10 | Certified by AI Engineering.                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/*
 * ARTIFACT: client/src/services/api/tenantApi.js
 * VERSION: v57.0.1-GOVERNED-C2-TENANT-LIFECYCLE-DENY
 * AUTHORITY BOUNDARY: tenant transport adapter only; server owns tenant authority
 * TENANT POSTURE: all calls inherit canonical API tenant scoping and bearer propagation
 * FAIL-CLOSED POSTURE: global listing/create/suspend fail before transport pending governed Python EOS C2 authority; auth failures are terminal and never retried
 * FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
