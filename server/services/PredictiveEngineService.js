/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ PREDICTIVE TEMPLATE ENGINE SERVICE - FORENSIC EDITION                     ║
  ║ Features: Safe concurrency queue, idempotent metrics, bulletproof async   ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import fs from 'fs';
import path from 'path';
import { createHash } from 'crypto';
import pino from 'pino';
import client from 'prom-client';
import PredictiveTemplateEngine from '../algorithms/predictive/PredictiveTemplateEngine.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

// FORENSIC FIX: Global, idempotent metric registration
const register = client.register;

let analyzeHistogram = register.getSingleMetric('predictive_engine_analyze_duration_seconds');
if (!analyzeHistogram) {
  analyzeHistogram = new client.Histogram({
    name: 'predictive_engine_analyze_duration_seconds',
    help: 'Duration of template analysis in seconds',
    registers: [register],
    buckets: [0.1, 0.5, 1, 2, 5, 10, 30]
  });
}

let analyzeCounter = register.getSingleMetric('predictive_engine_analyze_requests_total');
if (!analyzeCounter) {
  analyzeCounter = new client.Counter({
    name: 'predictive_engine_analyze_requests_total',
    help: 'Total analyze requests',
    registers: [register]
  });
}

let analyzeFailures = register.getSingleMetric('predictive_engine_analyze_failures_total');
if (!analyzeFailures) {
  analyzeFailures = new client.Counter({
    name: 'predictive_engine_analyze_failures_total',
    help: 'Total analyze failures',
    registers: [register]
  });
}

let predictionGauge = register.getSingleMetric('predictive_engine_active_predictions');
if (!predictionGauge) {
  predictionGauge = new client.Gauge({
    name: 'predictive_engine_active_predictions',
    help: 'Number of active predictions stored',
    registers: [register]
  });
}

export class PredictiveEngineService {
  constructor(options = {}) {
    this.engine = new PredictiveTemplateEngine();
    this.snapshotDir = options.snapshotDir || path.resolve(process.cwd(), 'snapshots/predictive');
    this.modelDir = options.modelDir || path.resolve(process.cwd(), 'models');
    this.concurrentLimit = options.concurrentLimit || 4;
    this.activeCount = 0;
    this.queue = [];

    this._ensureDirs();
    logger.info('PredictiveEngineService initialized', { snapshotDir: this.snapshotDir });
  }

  _ensureDirs() {
    if (!fs.existsSync(this.snapshotDir)) fs.mkdirSync(this.snapshotDir, { recursive: true });
    if (!fs.existsSync(this.modelDir)) fs.mkdirSync(this.modelDir, { recursive: true });
  }

  metrics() {
    return register;
  }

  // FORENSIC FIX: Native async queue without Promise constructor anti-pattern
  async analyzeTemplate(template) {
    analyzeCounter.inc();

    if (this.activeCount >= this.concurrentLimit) {
      logger.debug('Job queued', { queueLength: this.queue.length + 1 });
      await new Promise(resolve => this.queue.push(resolve));
    }

    this.activeCount++;
    predictionGauge.set(this.engine.predictions.size);
    const endTimer = analyzeHistogram.startTimer();

    try {
      const result = await this._runAnalysis(template);
      return result;
    } catch (err) {
      analyzeFailures.inc();
      logger.error('Template analysis failed', { err: err.message, templateId: template?.templateId });
      throw err;
    } finally {
      endTimer();
      this.activeCount--;
      predictionGauge.set(this.engine.predictions.size);
      this._dequeueNext();
    }
  }

  _dequeueNext() {
    if (this.queue.length > 0) {
      const nextResolver = this.queue.shift();
      // Unblock the next waiting job in the queue
      nextResolver(); 
    }
  }

  async _runAnalysis(template) {
    if (!template || !template.templateId) {
      throw new Error('Template must include templateId');
    }

    logger.info('Starting analysis', { templateId: template.templateId, practiceArea: template.practiceArea });

    const templateCopy = JSON.parse(JSON.stringify(template));
    const analysis = await this.engine.analyzeTemplate(templateCopy);

    const datasetHash = createHash('sha256').update(JSON.stringify({
      template: templateCopy,
      analysis: analysis
    })).digest('hex');

    const snapshotPath = path.join(this.snapshotDir, `${template.templateId}_${datasetHash}.json`);
    try {
      fs.writeFileSync(snapshotPath, JSON.stringify({ template: templateCopy, analysis }, null, 2), 'utf8');
      logger.info('Snapshot persisted', { templateId: template.templateId, snapshotPath });
    } catch (err) {
      logger.warn('Failed to persist snapshot', { err: err.message, templateId: template.templateId });
    }

    this.engine.predictions.set(template.templateId, { 
      ...analysis, 
      datasetHash, 
      snapshotPath, 
      timestamp: new Date().toISOString() 
    });
    
    predictionGauge.set(this.engine.predictions.size);

    return { templateId: template.templateId, datasetHash, snapshotPath, analysis };
  }

  getPrediction(templateId) {
    const pred = this.engine.predictions.get(templateId);
    if (!pred) throw new Error('Prediction not found');
    return pred;
  }

  listPredictions() {
    return Array.from(this.engine.predictions.values());
  }

  getSnapshotPath(templateId) {
    const pred = this.getPrediction(templateId);
    return pred.snapshotPath;
  }

  health() {
    return {
      status: 'ok',
      predictionsStored: this.engine.predictions.size,
      queueLength: this.queue.length,
      active: this.activeCount,
      lastUpdated: new Date().toISOString()
    };
  }

  async shutdown({ timeoutMs = 10000 } = {}) {
    logger.info('Shutdown initiated for PredictiveEngineService');
    const start = Date.now();

    while (this.activeCount > 0 && (Date.now() - start) < timeoutMs) {
      await new Promise(r => setTimeout(r, 200));
    }

    try {
      const index = Array.from(this.engine.predictions.entries()).map(([id, p]) => ({ 
        id, 
        timestamp: p.timestamp, 
        datasetHash: p.datasetHash 
      }));
      fs.writeFileSync(path.join(this.snapshotDir, 'index.json'), JSON.stringify(index, null, 2), 'utf8');
      logger.info('Prediction index persisted');
    } catch (err) {
      logger.warn('Failed to persist prediction index during shutdown', { err: err.message });
    }

    logger.info('Shutdown complete');
  }
}

export default PredictiveEngineService;
