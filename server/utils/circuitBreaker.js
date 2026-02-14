class CircuitBreaker {
    constructor(options = {}) {
        this.failureThreshold = options.failureThreshold || 5;
        this.resetTimeout = options.resetTimeout || 60000;
        this.failures = 0;
        this.state = 'CLOSED';
        this.nextAttempt = Date.now();
    }

    async execute(fn) {
        if (this.state === 'OPEN') {
            if (Date.now() > this.nextAttempt) {
                this.state = 'HALF_OPEN';
            } else {
                throw new Error('Circuit breaker is OPEN');
            }
        }

        try {
            const result = await fn();
            if (this.state === 'HALF_OPEN') {
                this.reset();
            }
            return result;
        } catch (error) {
            this.recordFailure();
            throw error;
        }
    }

    recordFailure() {
        this.failures++;
        if (this.failures >= this.failureThreshold) {
            this.trip();
        }
    }

    trip() {
        this.state = 'OPEN';
        this.nextAttempt = Date.now() + this.resetTimeout;
    }

    reset() {
        this.failures = 0;
        this.state = 'CLOSED';
    }
}

module.exports = { CircuitBreaker };
