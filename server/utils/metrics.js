/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                                                                                        ║
 * ║   ██╗    ██╗██╗██╗     ███████╗██╗   ██╗    ██████╗ ███████╗     ██████╗ ███████╗                                               ║
 * ║   ██║    ██║██║██║     ██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝    ██╔═══██╗██╔════╝                                               ║
 * ║   ██║ █╗ ██║██║██║     ███████╗ ╚████╔╝     ██████╔╝█████╗      ██║   ██║███████╗                                               ║
 * ║   ██║███╗██║██║██║     ╚════██║  ╚██╔╝      ██╔══██╗██╔══╝      ██║   ██║╚════██║                                               ║
 * ║   ╚███╔███╔╝██║███████╗███████║   ██║       ██████╔╝███████╗    ╚██████╔╝███████║                                               ║
 * ║    ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝                                               ║
 * ║                                                                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - SOVEREIGN METRICS NEXUS [V52.0.0-SINGULARITY-TITAN]
 * [PROMETHEUS HUD | TELEMETRY QUEUE | REPLAY COUNTERS | INVESTOR SNAPSHOT | QUANTILE ANALYTICS]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 52.0.0-TITAN | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                        ║
 * ║ EPITOME: INSTITUTIONAL AUTHORITY | ZERO-DROP | BOARDROOM READY | NO CHILD'S PLACE                                                      ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/metrics.js                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-strip policy and centralized HUD ownership. [2026-05-13]                        ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Resolved redisConfig.getClient collision in snapshot logic. [2026-05-13]                         ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Fortified Prometheus Registry to survive Singularity hot-restarts. [2026-05-13]                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { EventEmitter } from 'node:events';
import os from 'node:os';
import { performance } from 'node:perf_hooks';
import { getCurrentTenant } from '../middleware/tenantContext.js';
import { broadcastTelemetry } from './telemetryHelper.js';
import loggerRaw from './logger.js';
import client, { register } from 'prom-client';

const logger = loggerRaw.default || loggerRaw;

class SovereignMetrics extends EventEmitter {
  constructor() {
    super();
    this.component = 'WILSY-OS-METRICS-V52';
    this.version = '52.0.0-SINGULARITY-TITAN';

    // 🏛️ In-Memory Sovereign Data Stores
    this.counters = new Map();
    this.timers = new Map();
    this.gauges = new Map();
    this.breakerStates = new Map();

    this.startTime = Date.now();
    this._logInitialization();

    // 📊 INSTITUTIONAL PROMETHEUS HUD REGISTRY
    this.telemetryQueueGauge = this._getOrCreateMetric(client.Gauge, {
      name: 'wilsy_telemetry_queue_size',
      help: 'Number of packets in sovereign telemetry Cold Storage'
    });

    this.telemetryReplayCounter = this._getOrCreateMetric(client.Counter, {
      name: 'wilsy_telemetry_replayed_total',
      help: 'Total packets replayed from Cold Storage to the Nucleus'
    });

    this.telemetryDroppedCounter = this._getOrCreateMetric(client.Counter, {
      name: 'wilsy_telemetry_dropped_total',
      help: 'Total packets dropped during hardware fractures'
    });
  }

  /**
   * 🛡️ COLLISION DEFENSE
   * Ensures institutional metrics are only registered once to prevent Singularity fractures.
   */
  _getOrCreateMetric(MetricType, config) {
    const existing = register.getSingleMetric(config.name);
    if (existing) return existing;
    return new MetricType(config);
  }

  _logInitialization() {
    console.log(`[METRICS] 🏛️ Sovereign Telemetry Engine v${this.version} - INVESTOR ACTIVE`);
  }

  /**
   * 🏷️ SOVEREIGN KEY GENERATOR
   */
  _buildSovereignKey(name, tags = {}) {
    const tenantId = tags.tenantId || getCurrentTenant?.() || 'GLOBAL_ROOT';
    const tagString = Object.entries({ ...tags, tenantId })
      .map(([k, v]) => `${k}=${v}`)
      .sort()
      .join(',');
    return `${name}{${tagString}}`;
  }

  /**
   * 📈 INCREMENT COUNTER
   */
  increment(name, value = 1, tags = {}) {
    const key = this._buildSovereignKey(name, tags);
    const current = this.counters.get(key) || 0;
    this.counters.set(key, current + value);

    if (tags.severity === 'CRITICAL') {
      logger.warn(`[METRIC-CRITICAL] ${name} incremented by ${value}`, { tags });
      broadcastTelemetry(tags.tenantId || 'GLOBAL_ROOT', 'SECURITY_EVENT', 'METRIC_CRITICAL_THRESHOLD', 'SovereignMetrics', {
        name, value, tags,
        compliance: { POPIA: 'AUDIT_REQUIRED', GDPR: 'SECURITY_ALERT' }
      });
    }

    if (name === 'telemetry_replayed_total') this.telemetryReplayCounter.inc(value);
    if (name === 'telemetry_dropped_total') this.telemetryDroppedCounter.inc(value);
  }

  /**
   * ⚡ UPDATE BREAKER STATE
   */
  updateBreakerState(component, state, tags = {}) {
    const key = this._buildSovereignKey(`wilsy_breaker_state`, { ...tags, component });
    this.breakerStates.set(key, state);

    if (state === 1) {
      this.increment('failover_events_total', 1, { ...tags, component, severity: 'CRITICAL' });
      logger.error(`[CIRCUIT-BREAKER] ⚠️ Failover triggered for ${component}. State: OPEN.`);
    }
  }

  /**
   * ⏱️ RECORD TIMING (LATENCY)
   */
  recordTiming(name, durationMs, tags = {}) {
    const key = this._buildSovereignKey(name, tags);
    if (!this.timers.has(key)) this.timers.set(key, []);
    const measurements = this.timers.get(key);
    measurements.push({ v: durationMs, t: Date.now() });

    const threshold = tags.threshold || 500;
    if (durationMs > threshold) {
      this._handleSlaViolation(name, durationMs, threshold, tags);
    }
    // Limit memory footprint of high-frequency measurements
    if (measurements.length > 500) measurements.shift();
  }

  startTimer(name, tags = {}) {
    const start = performance.now();
    return () => {
      const duration = Number((performance.now() - start).toFixed(2));
      this.recordTiming(name, duration, tags);
      return duration;
    };
  }

  _handleSlaViolation(name, duration, threshold, tags) {
    const tenantId = tags.tenantId || 'GLOBAL_ROOT';
    logger.error(`[SLA-FRACTURE] Metric '${name}' exceeded threshold: ${duration}ms > ${threshold}ms`);
    broadcastTelemetry(tenantId, 'SYSTEM_EVENT', 'SLA_VIOLATION', 'SovereignMetrics', {
      metricName: name,
      actualDuration: duration,
      threshold,
      severity: 'HIGH',
      compliance: { POPIA: 'VERIFIED', GDPR: 'SLA_RISK' },
      boardroomSummary: { status: 'FRACTURED', anomalyCount: 1 }
    });
  }

  /**
   * 📊 SET GAUGE
   */
  setGauge(name, value, tags = {}) {
    const key = this._buildSovereignKey(name, tags);
    this.gauges.set(key, { v: value, t: Date.now() });

    if (name === 'telemetry_queue_size') this.telemetryQueueGauge.set(value);
  }

  /**
   * 🛰️ GET INVESTOR SNAPSHOT
   * @description Direct real-time state extraction for the Boardroom HUD.
   * RECTIFIED: Removed any dependency on external Redis getClient to avoid deadlock.
   */
  getSnapshot() {
    const snapshot = {
      timestamp: new Date().toISOString(),
      version: this.version,
      uptimeSeconds: Math.floor((Date.now() - this.startTime) / 1000),
      metrics: {
        counters: Object.fromEntries(this.counters),
        gauges: Object.fromEntries(this.gauges),
        breakerStates: Object.fromEntries(this.breakerStates),
        performance: {}
      },
      system: {
        load: os.loadavg(),
        freeMem: Math.round(os.freemem() / 1024 / 1024) + 'MB',
        totalMem: Math.round(os.totalmem() / 1024 / 1024) + 'MB',
        cpuCores: os.cpus().length,
        pid: process.pid
      }
    };

    // Calculate percentiles for Boardroom Performance Analytics
    for (const [key, values] of this.timers) {
      const sorted = values.map(m => m.v).sort((a, b) => a - b);
      const len = sorted.length;
      if (len === 0) continue;

      snapshot.metrics.performance[key] = {
        count: len,
        p50: sorted[Math.floor(len * 0.5)] || 0,
        p95: sorted[Math.floor(len * 0.95)] || 0,
        p99: sorted[Math.floor(len * 0.99)] || 0,
        max: sorted[len - 1] || 0,
        min: sorted[0] || 0,
        average: Number((sorted.reduce((a, b) => a + b, 0) / len).toFixed(2))
      };
    }

    return snapshot;
  }
}

const metrics = new SovereignMetrics();
export default metrics;
