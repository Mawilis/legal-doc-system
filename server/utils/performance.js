/**
 * Performance monitoring utilities
 */
class PerformanceMonitor {
    constructor() {
        this.metrics = new Map();
        this.records = {};
    }

    startTimer(label) {
        this.metrics.set(label, process.hrtime.bigint());
    }

    endTimer(label) {
        const start = this.metrics.get(label);
        if (!start) return null;
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1_000_000; // Convert to milliseconds
        this.metrics.delete(label);
        return duration;
    }

    async measure(label, fn) {
        this.startTimer(label);
        try {
            return await fn();
        } finally {
            const duration = this.endTimer(label);
            if (duration && process.env.NODE_ENV === 'development') {
                console.log(`⏱️ ${label}: ${duration.toFixed(2)}ms`);
            }
        }
    }

    record(metric, value, tags = {}) {
        if (!this.records[metric]) {
            this.records[metric] = [];
        }
        this.records[metric].push({
            value,
            timestamp: new Date().toISOString(),
            tags
        });
        return this.records[metric];
    }

    getMetrics() {
        return Object.fromEntries(this.metrics);
    }

    getRecords() {
        return this.records;
    }
}

module.exports = { PerformanceMonitor };
