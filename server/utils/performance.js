/* eslint-disable */
/**
 * 🏛️ WILSYS OS - PERFORMANCE MONITORING ENGINE
 * Standard: ES Module (Surgically Standardized)
 * Purpose: High-Resolution Metric Tracking for $10B Investor-Grade Audits
 */

export class PerformanceMonitor {
    constructor(options = {}) {
        this.name = options.name || 'GlobalMonitor';
        this.timers = new Map();
        this.records = {};
        this.historySize = options.historySize || 1000; // Production buffer limit
    }

    /**
     * Starts a high-resolution timer using Node.js process.hrtime
     */
    startTimer(label) {
        this.timers.set(label, process.hrtime.bigint());
    }

    /**
     * Ends timer and returns duration in milliseconds with high precision
     */
    endTimer(label) {
        const start = this.timers.get(label);
        if (!start) return null;

        const end = process.hrtime.bigint();
        // Convert nanoseconds to milliseconds
        const duration = Number(end - start) / 1_000_000;
        this.timers.delete(label);
        return duration;
    }

    /**
     * Wraps a function to measure execution time automatically
     */
    async measure(label, fn) {
        this.startTimer(label);
        try {
            const result = await fn();
            const duration = this.endTimer(label);
            this.record(label, duration, { status: 'success' });
            return result;
        } catch (error) {
            const duration = this.endTimer(label);
            this.record(label, duration, { status: 'error', error: error.message });
            throw error;
        }
    }

    /**
     * Records a metric with a rolling buffer to prevent memory exhaustion
     */
    record(metric, value, tags = {}) {
        if (!this.records[metric]) {
            this.records[metric] = [];
        }

        const entry = {
            value: Number(value).toFixed(4),
            timestamp: new Date().toISOString(),
            tags: { ...tags, environment: process.env.NODE_ENV }
        };

        this.records[metric].push(entry);

        // Production-Safety: Maintain rolling history size
        if (this.records[metric].length > this.historySize) {
            this.records[metric].shift();
        }

        // Log long-running operations in development
        if (process.env.NODE_ENV === 'development' && value > 500) {
            console.warn(`⚠️ PERFORMANCE ALERT [${this.name}]: ${metric} took ${value}ms`);
        }

        return entry;
    }

    /**
     * Aggregates metrics for the Status Dashboard
     */
    getMetrics() {
        const stats = {};
        for (const [metric, records] of Object.entries(this.records)) {
            if (records.length === 0) continue;

            const values = records.map(r => Number(r.value));
            stats[metric] = {
                latest: values[values.length - 1],
                average: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2),
                count: records.length,
                p95: values.sort((a, b) => a - b)[Math.floor(values.length * 0.95)] || values[0]
            };
        }
        return stats;
    }

    getRecords() {
        return this.records;
    }

    reset() {
        this.records = {};
        this.timers.clear();
    }
}

// Named export for BlockchainAnchor and default for general use
export default PerformanceMonitor;