/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ METRICS - INVESTOR-GRADE PERFORMANCE MONITORING                            ║
  ║ Prometheus compatible | Real-time | Forensic tracking                      ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

const EventEmitter = require('events');

class Metrics extends EventEmitter {
    constructor() {
        super();
        this.metrics = new Map();
        this.timers = new Map();
        this.counters = new Map();
        this.gauges = new Map();
        this.histograms = new Map();
        
        // Start periodic metrics flush
        this._startMetricsFlush();
    }

    /**
     * Record a timing metric
     */
    recordTiming(name, duration, tags = {}) {
        const key = this._buildKey(name, tags);
        
        if (!this.timers.has(key)) {
            this.timers.set(key, []);
        }
        
        this.timers.get(key).push({
            value: duration,
            timestamp: Date.now(),
            tags
        });

        this.emit('timing', { name, duration, tags });
    }

    /**
     * Increment a counter
     */
    increment(name, value = 1, tags = {}) {
        const key = this._buildKey(name, tags);
        
        if (!this.counters.has(key)) {
            this.counters.set(key, 0);
        }
        
        const newValue = this.counters.get(key) + value;
        this.counters.set(key, newValue);
        
        this.emit('counter', { name, value: newValue, tags });
    }

    /**
     * Set a gauge value
     */
    setGauge(name, value, tags = {}) {
        const key = this._buildKey(name, tags);
        this.gauges.set(key, {
            value,
            timestamp: Date.now(),
            tags
        });
        
        this.emit('gauge', { name, value, tags });
    }

    /**
     * Record a histogram value
     */
    recordHistogram(name, value, tags = {}) {
        const key = this._buildKey(name, tags);
        
        if (!this.histograms.has(key)) {
            this.histograms.set(key, []);
        }
        
        this.histograms.get(key).push({
            value,
            timestamp: Date.now(),
            tags
        });

        this.emit('histogram', { name, value, tags });
    }

    /**
     * Get snapshot of all metrics
     */
    async getSnapshot() {
        const snapshot = {
            timers: {},
            counters: {},
            gauges: {},
            histograms: {},
            timestamp: new Date().toISOString()
        };

        // Process timers
        for (const [key, values] of this.timers) {
            if (values.length > 0) {
                const nums = values.map(v => v.value);
                snapshot.timers[key] = {
                    count: values.length,
                    sum: nums.reduce((a, b) => a + b, 0),
                    min: Math.min(...nums),
                    max: Math.max(...nums),
                    avg: nums.reduce((a, b) => a + b, 0) / nums.length,
                    p95: this._percentile(nums, 95)
                };
            }
        }

        // Process counters
        for (const [key, value] of this.counters) {
            snapshot.counters[key] = value;
        }

        // Process gauges
        for (const [key, data] of this.gauges) {
            snapshot.gauges[key] = data.value;
        }

        // Process histograms
        for (const [key, values] of this.histograms) {
            if (values.length > 0) {
                const nums = values.map(v => v.value);
                snapshot.histograms[key] = {
                    count: values.length,
                    sum: nums.reduce((a, b) => a + b, 0),
                    min: Math.min(...nums),
                    max: Math.max(...nums),
                    avg: nums.reduce((a, b) => a + b, 0) / nums.length,
                    p50: this._percentile(nums, 50),
                    p90: this._percentile(nums, 90),
                    p95: this._percentile(nums, 95),
                    p99: this._percentile(nums, 99)
                };
            }
        }

        return snapshot;
    }

    /**
     * Reset all metrics
     */
    reset() {
        this.timers.clear();
        this.counters.clear();
        this.gauges.clear();
        this.histograms.clear();
    }

    /**
     * Build metric key with tags
     */
    _buildKey(name, tags) {
        if (Object.keys(tags).length === 0) {
            return name;
        }
        
        const tagString = Object.entries(tags)
            .map(([k, v]) => `${k}=${v}`)
            .sort()
            .join(',');
        
        return `${name}|${tagString}`;
    }

    /**
     * Calculate percentile
     */
    _percentile(sorted, percentile) {
        if (sorted.length === 0) return 0;
        const copy = [...sorted].sort((a, b) => a - b);
        const index = Math.ceil((percentile / 100) * copy.length) - 1;
        return copy[Math.max(0, Math.min(index, copy.length - 1))];
    }

    /**
     * Start periodic metrics flush
     */
    _startMetricsFlush() {
        setInterval(() => {
            this.emit('flush', {
                timestamp: new Date().toISOString(),
                metrics: this.getSnapshot()
            });
        }, 60000); // Flush every minute
    }
}

// Singleton instance
class MetricsSingleton {
    constructor() {
        if (!MetricsSingleton.instance) {
            MetricsSingleton.instance = new Metrics();
        }
    }

    getInstance() {
        return MetricsSingleton.instance;
    }
}

module.exports = new MetricsSingleton().getInstance();
