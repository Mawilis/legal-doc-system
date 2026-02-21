/* eslint-disable */
/**
 * 🏛️ WILSYS OS - CIRCUIT BREAKER UTILITY
 * Standard: ES Module (Surgically Standardized)
 * Purpose: Fault Tolerance & High Availability for Regulatory APIs
 */

export class CircuitBreaker {
    constructor(options = {}) {
        this.name = options.name || 'GenericBreaker';
        this.failureThreshold = options.failureThreshold || 5;
        this.successThreshold = options.successThreshold || 2;
        this.timeoutMs = options.timeoutMs || 30000;
        this.resetTimeoutMs = options.resetTimeoutMs || 60000;

        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
        this.failureCount = 0;
        this.successCount = 0;
        this.nextRetryTimestamp = 0;
        this.openSince = null;
    }

    getState() {
        return this.state;
    }

    isOpen() {
        if (this.state === 'OPEN') {
            if (Date.now() >= this.nextRetryTimestamp) {
                this.state = 'HALF_OPEN';
                return false;
            }
            return true;
        }
        return false;
    }

    async execute(action) {
        if (this.isOpen()) {
            throw new Error(`Circuit Breaker [${this.name}] is OPEN`);
        }

        try {
            const result = await action();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            throw error;
        }
    }

    onSuccess() {
        this.failureCount = 0;
        if (this.state === 'HALF_OPEN') {
            this.successCount++;
            if (this.successCount >= this.successThreshold) {
                this.state = 'CLOSED';
                this.successCount = 0;
            }
        }
    }

    onFailure() {
        this.failureCount++;
        if (this.state === 'HALF_OPEN' || this.failureCount >= this.failureThreshold) {
            this.state = 'OPEN';
            this.openSince = new Date().toISOString();
            this.nextRetryTimestamp = Date.now() + this.resetTimeoutMs;
        }
    }
}

// Default export for singleton-like usage if required
export default CircuitBreaker;