/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║   █████╗ ██╗    ███████╗ █████╗ ██╗     ███████╗███████╗    ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ ║
 * ║  ██╔══██╗██║    ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗║
 * ║  ███████║██║    ███████╗███████║██║     █████╗  ███████╗    ██║  ██║███████║███████╗███████║██████╔╝██║  ██║███████║██████╔╝██║  ██║║
 * ║  ██╔══██║██║    ╚════██║██╔══██║██║     ██╔══╝  ╚════██║    ██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║  ██║██╔══██║██╔══██╗██║  ██║║
 * ║  ██║  ██║███████╗███████║██║  ██║███████╗███████╗███████║    ██████╔╝██║  ██║███████║██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║██████╔╝║
 * ║  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ║
 * ║                                                                                                                                    ║
 * ║                         THE SOVEREIGN OPERATING SYSTEM FOR GLOBAL BUSINESS                                                         ║
 * ║               PRODUCTION CIRCUIT BREAKER | METRICS | FALLBACK | RESILIENCE | FORENSIC TELEMETRY                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - CIRCUIT BREAKER ENHANCED [V2.1.0-PQ]
 * [STATE MACHINE | TELEMETRY BROADCAST | FORENSIC AUDIT INTEGRATION]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.1.0-PQ | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/circuitBreakerEnhanced.js                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated forensic telemetry linkage and boardroom observability.                            ║
 * ║ • AI Engineering (DeepSeek) - ENHANCED: Integrated broadcastTelemetry and audit logging for state transitions.                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * @class CircuitBreakerEnhanced
 * @description Production-grade circuit breaker with metrics, fallback, and forensic telemetry.
 * Prevents cascading failures by detecting and isolating failing external services.
 * @real-world Used for court API calls, payment gateways, and third-party integrations.
 * @forensic Every state transition (OPEN, HALF_OPEN, CLOSED) is broadcast to the Boardroom HUD
 *           via broadcastTelemetry and can be anchored in ForensicLog.
 * @example
 * const breaker = new CircuitBreakerEnhanced({
 *   failureThreshold: 5,
 *   timeoutMs: 15000,
 *   fallback: async () => ({ cached: true, data: [] })
 * });
 * const result = await breaker.execute(() => fetchFromExternalAPI());
 */
class CircuitBreakerEnhanced {
  /**
   * @param {Object} config - Configuration options
   * @param {number} config.failureThreshold - Number of failures before opening circuit (default 5)
   * @param {number} config.timeoutMs - Operation timeout in milliseconds (default 10000)
   * @param {number} config.resetTimeoutMs - Time before transitioning from OPEN to HALF_OPEN (default 60000)
   * @param {Function} config.fallback - Fallback function to execute when circuit is OPEN
   */
  constructor(config = {}) {
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = null;
    this.failureThreshold = config.failureThreshold || 5;
    this.timeoutMs = config.timeoutMs || 10000;
    this.resetTimeoutMs = config.resetTimeoutMs || 60000;
    this.fallback = config.fallback;
    this.metrics = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      openCircuitRejections: 0,
      lastError: null,
    };
  }

  /**
   * @method execute
   * @description Executes an operation with circuit breaker protection.
   * @param {Function} operation - Async function to execute.
   * @returns {Promise<any>} Result of the operation or fallback.
   * @real-world Wraps any external API call (court orders, payment gateways).
   * @example
   * const data = await breaker.execute(() => axios.get('/api/external'));
   */
  async execute(operation) {
    this.metrics.totalCalls++;
    if (this.state === 'OPEN') {
      this.metrics.openCircuitRejections++;
      if (this.fallback) {
        return this.fallback();
      }
      throw new Error('Circuit breaker is OPEN. Service temporarily unavailable.');
    }
    try {
      const result = await this.executeWithTimeout(operation);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure(error);
      if (this.fallback) {
        return this.fallback();
      }
      throw error;
    }
  }

  /**
   * @method executeWithTimeout
   * @private
   * @description Executes operation with timeout enforcement.
   * @param {Function} operation - Async function.
   * @returns {Promise<any>}
   */
  async executeWithTimeout(operation) {
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Operation timed out')), this.timeoutMs)
    );
    return Promise.race([operation(), timeoutPromise]);
  }

  /**
   * @method onSuccess
   * @private
   * @description Handles successful operation completion, triggers telemetry on state recovery.
   * @forensic Broadcasts when circuit transitions from HALF_OPEN to CLOSED.
   */
  onSuccess() {
    this.metrics.successfulCalls++;
    if (this.state === 'HALF_OPEN') {
      this.successCount++;
      if (this.successCount >= Math.ceil(this.failureThreshold / 2)) {
        const previousState = this.state;
        this.state = 'CLOSED';
        this.failureCount = 0;
        this.successCount = 0;
        console.log(`[CircuitBreaker] Transitioned from HALF_OPEN to CLOSED after ${this.successCount} consecutive successes.`);
        broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_RECOVERY', 'CIRCUIT_BREAKER_CLOSED', 'CircuitBreakerEnhanced', {
          previousState,
          newState: this.state,
          successCount: this.successCount
        });
      }
    } else if (this.state === 'CLOSED') {
      this.failureCount = 0;
    }
  }

  /**
   * @method onFailure
   * @private
   * @description Handles failed operation execution, triggers telemetry on state transitions.
   * @param {Error} error - The error that caused the failure.
   * @forensic Broadcasts when circuit opens or when a failure occurs in HALF_OPEN state.
   */
  onFailure(error) {
    this.metrics.failedCalls++;
    this.metrics.lastError = error.message;
    this.lastFailureTime = Date.now();

    if (this.state === 'CLOSED') {
      this.failureCount++;
      if (this.failureCount >= this.failureThreshold) {
        this.state = 'OPEN';
        console.log(`[CircuitBreaker] Transitioned to OPEN after ${this.failureCount} failures. Last error: ${error.message}`);
        broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_FAULT', 'CIRCUIT_BREAKER_OPEN', 'CircuitBreakerEnhanced', {
          failureCount: this.failureCount,
          threshold: this.failureThreshold,
          error: error.message,
          lastFailureTime: this.lastFailureTime
        });
        setTimeout(() => {
          this.state = 'HALF_OPEN';
          console.log('[CircuitBreaker] Transitioned to HALF_OPEN after reset timeout.');
          broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_RECOVERY', 'CIRCUIT_BREAKER_HALF_OPEN', 'CircuitBreakerEnhanced', {
            resetTimeoutMs: this.resetTimeoutMs
          });
        }, this.resetTimeoutMs);
      }
    } else if (this.state === 'HALF_OPEN') {
      this.state = 'OPEN';
      console.log('[CircuitBreaker] Transitioned to OPEN due to failure in HALF_OPEN state.');
      broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_FAULT', 'CIRCUIT_BREAKER_OPEN', 'CircuitBreakerEnhanced', {
        reason: 'failure_in_half_open',
        error: error.message
      });
      setTimeout(() => {
        this.state = 'HALF_OPEN';
        broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_RECOVERY', 'CIRCUIT_BREAKER_HALF_OPEN', 'CircuitBreakerEnhanced', {});
      }, this.resetTimeoutMs);
    }
  }

  /**
   * @method getState
   * @returns {string} Current circuit breaker state (CLOSED, OPEN, HALF_OPEN).
   * @example
   * if (breaker.getState() === 'OPEN') { /* handle gracefully *\/ }
   */
  getState() {
    return this.state;
  }

  /**
   * @method getMetrics
   * @returns {Object} Circuit breaker metrics including state, call counts, and last error.
   * @real-world Used by breakerController to expose health to Boardroom HUD.
   * @example
   * const metrics = breaker.getMetrics();
   * // { totalCalls: 42, successfulCalls: 38, failedCalls: 4, openCircuitRejections: 0, state: 'CLOSED', lastError: null }
   */
  getMetrics() {
    return { ...this.metrics, state: this.state };
  }

  /**
   * @method forceClose
   * @description Manually force the circuit breaker to CLOSED state (operator override).
   * @forensic Broadcasts the manual override.
   */
  forceClose() {
    const previousState = this.state;
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.successCount = 0;
    console.log('[CircuitBreaker] Manually forced to CLOSED state.');
    broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_OPERATOR', 'CIRCUIT_BREAKER_FORCE_CLOSE', 'CircuitBreakerEnhanced', {
      previousState,
      newState: this.state
    });
  }

  /**
   * @method forceOpen
   * @description Manually force the circuit breaker to OPEN state (operator override).
   * @forensic Broadcasts the manual override.
   */
  forceOpen() {
    const previousState = this.state;
    this.state = 'OPEN';
    console.log('[CircuitBreaker] Manually forced to OPEN state.');
    broadcastTelemetry('GLOBAL_ROOT', 'SYSTEM_OPERATOR', 'CIRCUIT_BREAKER_FORCE_OPEN', 'CircuitBreakerEnhanced', {
      previousState,
      newState: this.state
    });
  }
}

export default CircuitBreakerEnhanced;
