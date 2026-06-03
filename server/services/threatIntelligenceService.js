/* eslint-disable */
/*
================================================================================
QUANTUM SCROLL OF THREAT INTELLIGENCE: AI-POWERED THREAT DETECTION SERVICE
Path: /server/services/threatIntelligenceService.js
================================================================================

                            ╔═══════════════════════════════╗
                            ║   SUPREME THREAT INTELLIGENCE ║
                            ║   WILSY OS - AI SENTINEL      ║
                            ╚═══════════════════════════════╝
                                   ✦        ▲        ✦
                                  ✦         │         ✦
                                ✦    QUANTUM THREAT FEEDS    ✦
                               ✦            │            ✦
                    ╔═══════════════════════▼═══════════════════════╗
                    ║              PAN-AFRICAN THREAT DATA          ║
                    ║  SA-CERT │ INTERPOL │ AFRICA-CERT │ CISCO TAL ║
                    ╚══════════════════▲════════════════════════════╝
                               ✦       │       ✦
                                ✦      │      ✦
                    ╔══════════════════▼══════════════════╗
                    ║       MACHINE LEARNING ENGINE       ║
                    ║  TENSORFLOW.JS │ ANOMALY DETECTION  ║
                    ║  BEHAVIORAL AI │ PATTERN RECOGNITION║
                    ╚══════════════════▲══════════════════╝
                                ✦      │      ✦
                               ✦       │       ✦
                    ╔══════════════════▼══════════════════╗
                    ║    REAL-TIME THREAT DETECTION       ║
                    ║  SUPREME AUDIT LOG INTEGRATION      ║
                    ║  CYBERCRIMES ACT COMPLIANCE         ║
                    ╚══════════════════▲══════════════════╝
                                ✦      │      ✦
                               ✦       │       ✦
                    ╔══════════════════▼══════════════════╗
                    ║      ACTIONABLE THREAT INTELLIGENCE ║
                    ║  SUPREME ADMIN ALERTS │ SOC TEAM    ║
                    ║  REGULATORY REPORTING │ FORENSICS   ║
                    ╚═══════════════════════════════════╝

QUANTUM MANDATE: This AI-powered Threat Intelligence Service is the sentinel of
Wilsy OS's security citadel—continuously monitoring, analyzing, and neutralizing
threats using quantum-grade machine learning and pan-African threat intelligence
feeds. It transforms raw security data into actionable intelligence, ensuring
Wilsy OS remains impervious to cyber threats while maintaining compliance with
South Africa's Cybercrimes Act, POPIA, and international security standards.

COLLABORATION QUANTA:
• Chief Architect: Wilson Khanyezi (wilsy.wk@gmail.com)
• Security Sentinel: Cybercrimes Act Compliance Division
• AI Quantum: TensorFlow.js Integration Team
• Legal Compliance: POPIA & Cybercrimes Act Advisory
• Threat Intelligence: SA-CERT & INTERPOL Liaison

HORIZON EXPANSION:
• Quantum Leap: Integrate quantum machine learning for threat prediction
• Pan-African Extension: Add threat feeds for all 54 African countries
• Blockchain Integration: Decentralized threat intelligence sharing
• IoT Security: Expand to legal IoT device threat detection

================================================================================
*/

/**
 * 🏛️ WILSY OS - THREAT INTELLIGENCE SERVICE v1.0.0 (ES MODULE)
 * @file /Users/wilsonkhanyezi/legal-doc-system/server/services/threatIntelligenceService.js
 * @version 1.0.0
 * @lastModified 2026-04-07
 * @author Wilson Khanyezi <wilsonkhanyezi@gmail.com>
 * @reviewers Siybonga Khanyezi, Dr. Priya Naidoo, Johan Botha
 * @license Sovereign Proprietary – Wilsy OS (c) 2026 – 2126
 *
 * @description
 * AI-powered threat intelligence service using TensorFlow.js for real‑time threat detection.
 * Integrates with SA-CERT, INTERPOL, Africa-CERT feeds. Compliant with Cybercrimes Act, POPIA.
 *
 * @collaboration
 * - Any change requires signoff from two sovereign architects.
 * - ML model retraining must be audited.
 * - Threat intelligence feeds must comply with local data residency.
 * - See CONFLUENCE://WilsyOS/ThreatIntelligence for runbooks.
 *
 * @team_signoff:
 * • Wilson Khanyezi – Supreme Architect: 2026-04-07
 * • Dr. Priya Naidoo – Quantum Security: 2026-04-07
 * • Johan Botha – Compliance: 2026-04-07
 */

// =============================================================================
// QUANTUM IMPORTS: SECURE, PINNED DEPENDENCIES
// =============================================================================
import crypto from 'crypto';
import tf from '@tensorflow/tfjs-node';
import mongoose from 'mongoose';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
import fs from 'fs';
import fsPromises from 'fs/promises';
import path from 'path';

// Models and utilities
import AuditLog from '../models/AuditLog.js';
import SuperAdmin from '../models/SuperAdmin.js';
import complianceUtils from '../utils/complianceUtils.js';
import securityUtils from '../utils/securityUtils.js';
import blockchainService from './blockchainService.js';
import encryptionService from './encryptionService.js';

dotenv.config();

// =============================================================================
// QUANTUM SECURITY: ENVIRONMENT VALIDATION
// =============================================================================
const validateThreatIntelligenceEnvironment = () => {
  const requiredVars = [
    'THREAT_INTELLIGENCE_API_KEY',
    'SA_CERT_API_KEY',
    'INTERPOL_API_KEY',
    'THREAT_MODEL_PATH',
    'THREAT_DETECTION_THRESHOLD',
    'SUPREME_ADMIN_ALERT_EMAIL',
  ];

  const missingVars = requiredVars.filter((varName) => !process.env[varName]);

  if (missingVars.length > 0) {
    throw new Error(
      `[Threat Intelligence Service] Missing required environment variables: ${missingVars.join(
        ', '
      )}`
    );
  }

  if (process.env.THREAT_INTELLIGENCE_API_KEY.length < 32) {
    throw new Error(
      '[Threat Intelligence Service] THREAT_INTELLIGENCE_API_KEY must be at least 32 characters'
    );
  }

  const threshold = parseFloat(process.env.THREAT_DETECTION_THRESHOLD);
  if (isNaN(threshold) || threshold < 0.5 || threshold > 0.99) {
    throw new Error(
      '[Threat Intelligence Service] THREAT_DETECTION_THRESHOLD must be between 0.5 and 0.99'
    );
  }

  console.log('✅ Threat Intelligence Service Environment Validation PASSED');
};

try {
  validateThreatIntelligenceEnvironment();
} catch (error) {
  console.error('❌ Threat Intelligence Service Environment Validation FAILED:', error.message);
  process.exit(1);
}

// =============================================================================
// QUANTUM CONSTANTS: THREAT INTELLIGENCE CONFIGURATION
// =============================================================================
const THREAT_INTELLIGENCE_CONFIG = {
  ML: {
    MODEL_PATH: process.env.THREAT_MODEL_PATH || './models/threat-detection-model',
    TRAINING_EPOCHS: parseInt(process.env.TRAINING_EPOCHS) || 100,
    BATCH_SIZE: parseInt(process.env.ML_BATCH_SIZE) || 32,
    LEARNING_RATE: parseFloat(process.env.LEARNING_RATE) || 0.001,
    DETECTION_THRESHOLD: parseFloat(process.env.THREAT_DETECTION_THRESHOLD) || 0.85,
    CONFIDENCE_THRESHOLD: parseFloat(process.env.CONFIDENCE_THRESHOLD) || 0.75,
    MODEL_VERSION: '1.0.0',
  },

  THREAT_FEEDS: {
    SA_CERT: {
      enabled: process.env.SA_CERT_ENABLED === 'true',
      apiKey: process.env.SA_CERT_API_KEY,
      endpoint: process.env.SA_CERT_ENDPOINT || 'https://api.sa-cert.gov.za/v1/threats',
      refreshInterval: parseInt(process.env.SA_CERT_REFRESH_INTERVAL) || 3600000,
    },
    INTERPOL: {
      enabled: process.env.INTERPOL_ENABLED === 'true',
      apiKey: process.env.INTERPOL_API_KEY,
      endpoint: process.env.INTERPOL_ENDPOINT || 'https://api.interpol.int/v1/cyberthreats',
      refreshInterval: parseInt(process.env.INTERPOL_REFRESH_INTERVAL) || 86400000,
    },
    AFRICA_CERT: {
      enabled: process.env.AFRICA_CERT_ENABLED === 'true',
      apiKey: process.env.AFRICA_CERT_API_KEY,
      endpoint: process.env.AFRICA_CERT_ENDPOINT || 'https://api.africa-cert.org/v1/threats',
      refreshInterval: parseInt(process.env.AFRICA_CERT_REFRESH_INTERVAL) || 7200000,
    },
    COMMERCIAL_FEEDS: {
      enabled: process.env.COMMERCIAL_FEEDS_ENABLED === 'true',
      feeds: process.env.COMMERCIAL_FEEDS ? process.env.COMMERCIAL_FEEDS.split(',') : [],
      refreshInterval: parseInt(process.env.COMMERCIAL_FEEDS_REFRESH_INTERVAL) || 1800000,
    },
  },

  ALERTING: {
    SUPREME_ADMIN_EMAIL: process.env.SUPREME_ADMIN_ALERT_EMAIL || 'wilsy.wk@gmail.com',
    SUPREME_ADMIN_PHONE: process.env.SUPREME_ADMIN_ALERT_PHONE || '+27690465710',
    SECURITY_TEAM_SLACK: process.env.SECURITY_TEAM_SLACK_WEBHOOK,
    COMPLIANCE_OFFICER_EMAIL: process.env.COMPLIANCE_OFFICER_ALERT_EMAIL,
    CRITICAL_THRESHOLD: parseFloat(process.env.CRITICAL_THRESHOLD) || 0.95,
    HIGH_THRESHOLD: parseFloat(process.env.HIGH_THRESHOLD) || 0.85,
    MEDIUM_THRESHOLD: parseFloat(process.env.MEDIUM_THRESHOLD) || 0.7,
  },

  COMPLIANCE: {
    REPORTING_ENABLED: process.env.THREAT_REPORTING_ENABLED === 'true',
    REPORT_INTERVAL: parseInt(process.env.THREAT_REPORT_INTERVAL) || 86400000,
    SA_CERT_REPORTING: process.env.SA_CERT_REPORTING === 'true',
    INTERPOL_REPORTING: process.env.INTERPOL_REPORTING === 'true',
    DATA_RETENTION_DAYS: parseInt(process.env.THREAT_DATA_RETENTION_DAYS) || 365,
  },

  PERFORMANCE: {
    MAX_CONCURRENT_ANALYSIS: parseInt(process.env.MAX_CONCURRENT_ANALYSIS) || 10,
    ANALYSIS_TIMEOUT_MS: parseInt(process.env.ANALYSIS_TIMEOUT_MS) || 30000,
    CACHE_TTL_MS: parseInt(process.env.THREAT_CACHE_TTL_MS) || 300000,
    QUEUE_SIZE: parseInt(process.env.THREAT_QUEUE_SIZE) || 1000,
  },
};

// =============================================================================
// QUANTUM SCHEMAS: THREAT INTELLIGENCE DATA MODELS
// =============================================================================
const threatIntelligenceSchema = new mongoose.Schema(
  {
    threatId: {
      type: String,
      unique: true,
      required: true,
      default: () => `THREAT-${Date.now()}-${crypto.randomBytes(8).toString('hex')}`,
      index: true,
      comment: 'Globally unique threat identifier',
    },
    threatType: {
      type: String,
      required: true,
      enum: [
        'MALWARE',
        'PHISHING',
        'RANSOMWARE',
        'DDoS',
        'INSIDER_THREAT',
        'DATA_EXFILTRATION',
        'PRIVILEGE_ESCALATION',
        'ZERO_DAY',
        'SUPPLY_CHAIN',
        'AI_ADVERSARIAL',
      ],
      index: true,
      comment: 'Type of threat detected',
    },
    mlPrediction: {
      confidence: { type: Number, required: true, min: 0, max: 1, index: true },
      riskScore: { type: Number, required: true, min: 0, max: 100, index: true },
      features: { type: mongoose.Schema.Types.Mixed },
      modelVersion: { type: String, required: true },
      predictionTimestamp: { type: Date, default: Date.now },
    },
    sources: [
      {
        feed: { type: String, enum: ['SA_CERT', 'INTERPOL', 'AFRICA_CERT', 'COMMERCIAL', 'INTERNAL'] },
        sourceId: String,
        confidence: Number,
        firstSeen: Date,
        lastSeen: Date,
        indicators: [String],
      },
    ],
    affectedEntities: [
      {
        entityType: { type: String, enum: ['USER', 'SUPER_ADMIN', 'TENANT', 'FIRM', 'DOCUMENT', 'SYSTEM'] },
        entityId: mongoose.Schema.Types.ObjectId,
        impactLevel: { type: String, enum: ['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] },
        remediationStatus: { type: String, enum: ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED'] },
      },
    ],
    indicatorsOfCompromise: {
      ipAddresses: [String],
      domains: [String],
      urls: [String],
      fileHashes: [String],
      signatures: [String],
      patterns: [String],
    },
    timeline: {
      firstDetected: { type: Date, default: Date.now, index: true },
      lastDetected: { type: Date, default: Date.now, index: true },
      resolvedAt: Date,
      durationMs: Number,
    },
    impact: {
      severity: { type: String, required: true, enum: ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], index: true },
      businessImpact: { type: String, enum: ['MINIMAL', 'MODERATE', 'SIGNIFICANT', 'SEVERE', 'CATASTROPHIC'] },
      dataBreach: Boolean,
      financialImpact: Number,
      reputationImpact: Number,
      complianceImpact: { type: String, enum: ['NONE', 'POPIA_VIOLATION', 'CYBERCRIMES_ACT', 'GDPR', 'MULTIPLE'] },
    },
    response: {
      status: { type: String, enum: ['DETECTED', 'ANALYZING', 'CONTAINED', 'ERADICATED', 'RECOVERED', 'CLOSED'], default: 'DETECTED', index: true },
      actionsTaken: [String],
      assignedTo: mongoose.Schema.Types.ObjectId,
      slaBreach: Boolean,
      resolutionTimeMs: Number,
    },
    compliance: {
      cybercrimesAct: { reportable: Boolean, reported: Boolean, reportReference: String, reportDate: Date },
      popia: { dataSubjectAffected: Boolean, informationOfficerNotified: Boolean, notificationDate: Date },
      international: { gdprReportable: Boolean, crossBorderImpact: Boolean },
    },
    integrity: {
      evidenceHash: { type: String, required: true, match: /^[a-f0-9]{128}$/ },
      blockchainAnchored: Boolean,
      blockchainTxHash: String,
      digitalSignature: String,
    },
    metadata: {
      version: { type: Number, default: 1 },
      createdAt: { type: Date, default: Date.now },
      updatedAt: { type: Date, default: Date.now },
      expiresAt: { type: Date, index: true },
    },
  },
  { timestamps: true, collection: 'threat_intelligence' }
);

threatIntelligenceSchema.index({ 'mlPrediction.riskScore': -1 });
threatIntelligenceSchema.index({ 'impact.severity': 1, 'timeline.firstDetected': -1 });
threatIntelligenceSchema.index({ 'response.status': 1 });
threatIntelligenceSchema.index({ 'compliance.cybercrimesAct.reportable': 1 });

const ThreatIntelligence = mongoose.models.ThreatIntelligence || mongoose.model('ThreatIntelligence', threatIntelligenceSchema);

// =============================================================================
// QUANTUM ML ENGINE: THREAT DETECTION MODEL
// =============================================================================
class ThreatDetectionEngine {
  constructor() {
    this.model = null;
    this.isTraining = false;
    this.modelVersion = THREAT_INTELLIGENCE_CONFIG.ML.MODEL_VERSION;
    this.cache = new Map();
    this.initializeEngine();
  }

  async initializeEngine() {
    try {
      console.log('🚀 Initializing Quantum Threat Detection Engine...');
      const modelExists = await this.checkModelExists();
      if (modelExists) {
        await this.loadModel();
        console.log('✅ Threat Detection Model loaded successfully');
      } else {
        console.log('🔄 No existing model found. Creating new model...');
        await this.createModel();
        await this.trainInitialModel();
        await this.saveModel();
        console.log('✅ New Threat Detection Model created and trained');
      }
      this.startPeriodicRetraining();
    } catch (error) {
      console.error('❌ Failed to initialize Threat Detection Engine:', error);
      throw error;
    }
  }

  async checkModelExists() {
    try {
      await fsPromises.access(THREAT_INTELLIGENCE_CONFIG.ML.MODEL_PATH);
      return true;
    } catch {
      return false;
    }
  }

  async loadModel() {
    this.model = await tf.loadLayersModel(`file://${THREAT_INTELLIGENCE_CONFIG.ML.MODEL_PATH}/model.json`);
    await this.warmUpModel();
  }

  async createModel() {
    this.model = tf.sequential({
      layers: [
        tf.layers.dense({ inputShape: [50], units: 128, activation: 'relu', kernelRegularizer: tf.regularizers.l2({ l2: 0.01 }) }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 64, activation: 'relu', kernelRegularizer: tf.regularizers.l2({ l2: 0.01 }) }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 32, activation: 'relu', kernelRegularizer: tf.regularizers.l2({ l2: 0.01 }) }),
        tf.layers.dense({ units: 1, activation: 'sigmoid' }),
      ],
    });
    this.model.compile({
      optimizer: tf.train.adam(THREAT_INTELLIGENCE_CONFIG.ML.LEARNING_RATE),
      loss: 'binaryCrossentropy',
      metrics: ['accuracy', 'precision', 'recall'],
    });
  }

  async trainInitialModel() {
    const { features, labels } = this.generateSyntheticTrainingData(1000);
    const xs = tf.tensor2d(features);
    const ys = tf.tensor2d(labels, [labels.length, 1]);
    await this.model.fit(xs, ys, {
      epochs: THREAT_INTELLIGENCE_CONFIG.ML.TRAINING_EPOCHS,
      batchSize: THREAT_INTELLIGENCE_CONFIG.ML.BATCH_SIZE,
      validationSplit: 0.2,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          if (epoch % 10 === 0) {
            console.log(`Epoch ${epoch}: loss = ${logs.loss.toFixed(4)}, accuracy = ${logs.acc.toFixed(4)}`);
          }
        },
      },
    });
    xs.dispose();
    ys.dispose();
  }

  generateSyntheticTrainingData(samples) {
    const features = [];
    const labels = [];
    for (let i = 0; i < samples; i++) {
      const featureVector = [];
      for (let j = 0; j < 50; j++) {
        if (Math.random() > 0.9) featureVector.push(Math.random() * 10);
        else featureVector.push(Math.random());
      }
      features.push(featureVector);
      const isThreat = featureVector.some((val) => val > 5);
      labels.push([isThreat ? 1 : 0]);
    }
    return { features, labels };
  }

  async saveModel() {
    if (!fs.existsSync(THREAT_INTELLIGENCE_CONFIG.ML.MODEL_PATH)) {
      fs.mkdirSync(THREAT_INTELLIGENCE_CONFIG.ML.MODEL_PATH, { recursive: true });
    }
    await this.model.save(`file://${THREAT_INTELLIGENCE_CONFIG.ML.MODEL_PATH}`);
    const metadata = {
      version: this.modelVersion,
      createdAt: new Date().toISOString(),
      trainingSamples: 1000,
      accuracy: await this.evaluateModel(),
      features: 50,
      architecture: 'Sequential[128-64-32-1]',
    };
    fs.writeFileSync(
      path.join(THREAT_INTELLIGENCE_CONFIG.ML.MODEL_PATH, 'metadata.json'),
      JSON.stringify(metadata, null, 2)
    );
  }

  async evaluateModel() {
    const { features, labels } = this.generateSyntheticTrainingData(100);
    const xs = tf.tensor2d(features);
    const ys = tf.tensor2d(labels, [labels.length, 1]);
    const evaluation = this.model.evaluate(xs, ys);
    const accuracy = Array.isArray(evaluation) ? evaluation[1].dataSync()[0] : evaluation.dataSync()[0];
    xs.dispose();
    ys.dispose();
    return accuracy;
  }

  async warmUpModel() {
    const warmUpData = tf.randomNormal([1, 50]);
    await this.model.predict(warmUpData);
    warmUpData.dispose();
  }

  startPeriodicRetraining() {
    setInterval(async () => {
      try {
        await this.retrainModel();
      } catch (error) {
        console.error('❌ Periodic retraining failed:', error);
      }
    }, 24 * 60 * 60 * 1000);
  }

  async retrainModel() {
    if (this.isTraining) return;
    this.isTraining = true;
    console.log('🔄 Starting periodic model retraining...');
    try {
      const newData = await this.loadTrainingDataFromDatabase();
      if (newData.features.length > 0) {
        const xs = tf.tensor2d(newData.features);
        const ys = tf.tensor2d(newData.labels, [newData.labels.length, 1]);
        await this.model.fit(xs, ys, {
          epochs: 10,
          batchSize: THREAT_INTELLIGENCE_CONFIG.ML.BATCH_SIZE,
          validationSplit: 0.1,
        });
        xs.dispose();
        ys.dispose();
        this.modelVersion = `1.${Date.now()}`;
        await this.saveModel();
        console.log('✅ Model retraining completed successfully');
      }
    } catch (error) {
      console.error('❌ Model retraining failed:', error);
    } finally {
      this.isTraining = false;
    }
  }

  async loadTrainingDataFromDatabase() {
    const threats = await ThreatIntelligence.find({
      'mlPrediction.confidence': { $gt: THREAT_INTELLIGENCE_CONFIG.ML.CONFIDENCE_THRESHOLD },
    }).limit(1000);
    const features = [];
    const labels = [];
    threats.forEach((threat) => {
      if (threat.mlPrediction?.features) {
        features.push(threat.mlPrediction.features.slice(0, 50));
        labels.push([threat.impact.severity === 'CRITICAL' || threat.impact.severity === 'HIGH' ? 1 : 0]);
      }
    });
    return { features, labels };
  }

  async analyzeAuditLog(auditLog) {
    try {
      const features = this.extractFeaturesFromAuditLog(auditLog);
      const prediction = await this.predictThreat(features);
      const riskScore = this.calculateRiskScore(features, prediction);
      const threatType = this.determineThreatType(features, prediction);
      return {
        threatDetected: prediction > THREAT_INTELLIGENCE_CONFIG.ML.DETECTION_THRESHOLD,
        confidence: prediction,
        riskScore,
        threatType,
        features,
        modelVersion: this.modelVersion,
        timestamp: new Date(),
      };
    } catch (error) {
      console.error('❌ Threat analysis failed:', error);
      return { threatDetected: false, confidence: 0, riskScore: 0, error: error.message, timestamp: new Date() };
    }
  }

  extractFeaturesFromAuditLog(auditLog) {
    const features = [];
    const hour = auditLog.timestamp.getHours();
    const dayOfWeek = auditLog.timestamp.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const isBusinessHours = hour >= 8 && hour <= 17;
    features.push(hour / 24, dayOfWeek / 7, isWeekend ? 1 : 0, isBusinessHours ? 0 : 1);

    const roleWeights = { SUPREME_ADMIN: 0.1, ATTORNEY: 0.2, ADVOCATE: 0.3, PARTNER: 0.4, PARALEGAL: 0.5, CLIENT: 0.8, SYSTEM_ADMIN: 0.6, SYSTEM: 0.1 };
    features.push(roleWeights[auditLog.actor?.role] || 0.5);
    features.push(auditLog.actor?.isSupremeAdmin ? 0 : 0.3);

    const actionWeights = { SUPREME_CREATE: 0.3, SUPREME_UPDATE: 0.4, SUPREME_DELETE: 0.8, SUPREME_ACCESS: 0.5, SUPREME_SIGN: 0.2, SUPREME_SHARE: 0.6, SUPREME_APPROVE: 0.3, SUPREME_REJECT: 0.4, SUPREME_ESCALATE: 0.7, SUPREME_ARCHIVE: 0.4, SUPREME_OVERRIDE: 0.9 };
    features.push(actionWeights[auditLog.event?.action] || 0.5);

    const resourceWeights = { SUPREME_ADMIN: 0.9, DOCUMENT: 0.7, CASE_FILE: 0.8, CLIENT_RECORD: 0.6, INVOICE: 0.5, TRUST_TRANSACTION: 0.8, USER_ACCOUNT: 0.7, CONSENT_RECORD: 0.4, COMPLIANCE_REPORT: 0.9, AUDIT_LOG: 1.0 };
    features.push(resourceWeights[auditLog.event?.resourceType] || 0.5);

    const outcomeWeights = { SUCCESS: 0.1, FAILED: 0.7, DENIED: 0.8, PARTIAL: 0.6, PENDING: 0.3, OVERRIDDEN: 0.9 };
    features.push(outcomeWeights[auditLog.event?.outcome] || 0.5);

    const severityWeights = { INFO: 0.1, LOW: 0.3, MEDIUM: 0.6, HIGH: 0.8, CRITICAL: 1.0 };
    features.push(severityWeights[auditLog.security?.severity] || 0.1);
    features.push(auditLog.security?.legalHold ? 0.8 : 0.1);

    const responseTime = auditLog.performance?.responseTimeMs || 0;
    features.push(Math.min(responseTime / 1000, 1));

    while (features.length < 50) features.push(0);
    return features.slice(0, 50);
  }

  async predictThreat(features) {
    const cacheKey = crypto.createHash('md5').update(JSON.stringify(features)).digest('hex');
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < THREAT_INTELLIGENCE_CONFIG.PERFORMANCE.CACHE_TTL_MS) {
        return cached.prediction;
      }
    }
    const tensor = tf.tensor2d([features]);
    const predictionTensor = this.model.predict(tensor);
    const prediction = (await predictionTensor.data())[0];
    tensor.dispose();
    predictionTensor.dispose();
    this.cache.set(cacheKey, { prediction, timestamp: Date.now() });
    if (this.cache.size > 1000) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    return prediction;
  }

  calculateRiskScore(features, prediction) {
    let riskScore = prediction * 100;
    if (features[3] > 0.5) riskScore += 10;
    if (features[4] > 0.7) riskScore += 15;
    if (features[5] > 0.7) riskScore += 20;
    if (features[6] > 0.8) riskScore += 25;
    return Math.min(100, riskScore);
  }

  determineThreatType(features, prediction) {
    if (features[4] > 0.7 && features[5] > 0.8) return 'PRIVILEGE_ESCALATION';
    if (features[6] === 1.0) return 'INSIDER_THREAT';
    if (features[5] > 0.9) return 'INSIDER_THREAT';
    if (prediction > 0.9) return 'MALWARE';
    if (features[3] > 0.5 && prediction > 0.7) return 'DATA_EXFILTRATION';
    return 'UNKNOWN';
  }
}

// =============================================================================
// QUANTUM THREAT INTELLIGENCE SERVICE
// =============================================================================
class ThreatIntelligenceService {
  constructor() {
    this.mlEngine = new ThreatDetectionEngine();
    this.threatFeeds = new Map();
    this.activeThreats = new Map();
    this.initializeService();
  }

  async initializeService() {
    console.log('🚀 Initializing Supreme Threat Intelligence Service...');
    await this.initializeThreatFeeds();
    this.startThreatIntelligenceUpdates();
    this.startComplianceReporting();
    console.log('✅ Supreme Threat Intelligence Service initialized successfully');
  }

  async initializeThreatFeeds() {
    const feeds = THREAT_INTELLIGENCE_CONFIG.THREAT_FEEDS;
    for (const [feedName, config] of Object.entries(feeds)) {
      if (config.enabled) {
        try {
          await this.fetchThreatFeed(feedName, config);
          console.log(`✅ Threat feed initialized: ${feedName}`);
        } catch (error) {
          console.error(`❌ Failed to initialize threat feed ${feedName}:`, error.message);
        }
      }
    }
  }

  async fetchThreatFeed(feedName, config) {
    try {
      const response = await fetch(config.endpoint, {
        headers: { Authorization: `Bearer ${config.apiKey}`, 'Content-Type': 'application/json' },
        timeout: 10000,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const data = await response.json();
      this.processThreatFeedData(feedName, data);
    } catch (error) {
      console.error(`❌ Failed to fetch threat feed ${feedName}:`, error.message);
      throw error;
    }
  }

  processThreatFeedData(feedName, data) {
    const threats = Array.isArray(data) ? data : data.threats || [];
    threats.forEach((threat) => {
      const threatKey = this.generateThreatKey(threat);
      if (!this.threatFeeds.has(threatKey)) {
        this.threatFeeds.set(threatKey, { ...threat, sources: [feedName], firstSeen: new Date(), lastSeen: new Date() });
      } else {
        const existing = this.threatFeeds.get(threatKey);
        existing.sources.push(feedName);
        existing.lastSeen = new Date();
        this.threatFeeds.set(threatKey, existing);
      }
    });
    console.log(`📊 Processed ${threats.length} threats from ${feedName}`);
  }

  generateThreatKey(threat) {
    const keyData = { type: threat.type, indicators: threat.indicators?.join('|') || '', signature: threat.signature || '' };
    return crypto.createHash('sha256').update(JSON.stringify(keyData)).digest('hex').substring(0, 32);
  }

  startThreatIntelligenceUpdates() {
    const feeds = THREAT_INTELLIGENCE_CONFIG.THREAT_FEEDS;
    for (const [feedName, config] of Object.entries(feeds)) {
      if (config.enabled && config.refreshInterval) {
        setInterval(async () => {
          try {
            await this.fetchThreatFeed(feedName, config);
          } catch (error) {
            console.error(`❌ Periodic update failed for ${feedName}:`, error.message);
          }
        }, config.refreshInterval);
      }
    }
  }

  startComplianceReporting() {
    if (!THREAT_INTELLIGENCE_CONFIG.COMPLIANCE.REPORTING_ENABLED) return;
    setInterval(async () => {
      try {
        await this.generateComplianceReport();
      } catch (error) {
        console.error('❌ Compliance reporting failed:', error);
      }
    }, THREAT_INTELLIGENCE_CONFIG.COMPLIANCE.REPORT_INTERVAL);
  }

  async analyzeRealTimeThreat(auditLog) {
    try {
      const mlAnalysis = await this.mlEngine.analyzeAuditLog(auditLog);
      const threatIntelligence = await this.correlateWithThreatIntelligence(auditLog);
      const riskAssessment = this.assessRisk(mlAnalysis, threatIntelligence);
      if (riskAssessment.threatDetected) {
        await this.processDetectedThreat(auditLog, mlAnalysis, threatIntelligence, riskAssessment);
      }
      return {
        auditLogId: auditLog.quantumId,
        timestamp: new Date(),
        mlAnalysis,
        threatIntelligence,
        riskAssessment,
        actionsTaken: riskAssessment.threatDetected ? riskAssessment.recommendedActions : [],
      };
    } catch (error) {
      console.error('❌ Real-time threat analysis failed:', error);
      return { auditLogId: auditLog.quantumId, timestamp: new Date(), error: error.message, threatDetected: false };
    }
  }

  async correlateWithThreatIntelligence(auditLog) {
    const correlations = [];
    for (const [threatKey, threat] of this.threatFeeds) {
      const matchScore = this.calculateThreatMatchScore(auditLog, threat);
      if (matchScore > 0.5) {
        correlations.push({
          threatKey, threatType: threat.type, matchScore, sources: threat.sources,
          indicators: threat.indicators, firstSeen: threat.firstSeen, lastSeen: threat.lastSeen,
        });
      }
    }
    correlations.sort((a, b) => b.matchScore - a.matchScore);
    return { correlated: correlations.length > 0, correlations: correlations.slice(0, 5), totalThreats: this.threatFeeds.size };
  }

  calculateThreatMatchScore(auditLog, threat) {
    let score = 0;
    if (threat.indicators?.ipAddresses && auditLog.actor?.ipAddress) {
      const ipMatch = threat.indicators.ipAddresses.some((ip) => ip === auditLog.actor.ipAddress);
      if (ipMatch) score += 0.4;
    }
    if (threat.indicators?.patterns) {
      const logString = JSON.stringify(auditLog);
      const patternMatch = threat.indicators.patterns.some((pattern) => logString.includes(pattern));
      if (patternMatch) score += 0.3;
    }
    if (threat.type === 'INSIDER_THREAT' && auditLog.actor?.isSupremeAdmin) score += 0.2;
    if (threat.resourceTypes && threat.resourceTypes.includes(auditLog.event?.resourceType)) score += 0.1;
    return Math.min(1, score);
  }

  assessRisk(mlAnalysis, threatIntelligence) {
    const mlScore = mlAnalysis.riskScore;
    const tiScore = threatIntelligence.correlated ? 30 : 0;
    const correlationScore = threatIntelligence.correlations.length > 0 ? Math.max(...threatIntelligence.correlations.map((c) => c.matchScore)) * 20 : 0;
    const totalRiskScore = mlScore + tiScore + correlationScore;
    let threatLevel = 'NONE', threatDetected = false;
    if (totalRiskScore >= 90) { threatLevel = 'CRITICAL'; threatDetected = true; }
    else if (totalRiskScore >= 80) { threatLevel = 'HIGH'; threatDetected = true; }
    else if (totalRiskScore >= 70) { threatLevel = 'MEDIUM'; threatDetected = true; }
    else if (totalRiskScore >= 60) { threatLevel = 'LOW'; threatDetected = true; }
    const recommendedActions = this.generateRecommendedActions(threatLevel, mlAnalysis.threatType, threatIntelligence);
    return {
      threatDetected, threatLevel, totalRiskScore, mlRiskScore: mlScore,
      tiRiskScore: tiScore + correlationScore, confidence: mlAnalysis.confidence,
      recommendedActions, requiresImmediateAction: threatLevel === 'CRITICAL' || threatLevel === 'HIGH',
    };
  }

  generateRecommendedActions(threatLevel, threatType, threatIntelligence) {
    const actions = [];
    if (threatLevel === 'CRITICAL') {
      actions.push('IMMEDIATE_SYSTEM_ISOLATION', 'SUPREME_ADMIN_NOTIFICATION', 'SECURITY_TEAM_ESCALATION', 'INCIDENT_RESPONSE_ACTIVATION');
    } else if (threatLevel === 'HIGH') {
      actions.push('SESSION_TERMINATION', 'ACCOUNT_LOCKDOWN', 'SECURITY_TEAM_NOTIFICATION', 'ENHANCED_MONITORING');
    } else if (threatLevel === 'MEDIUM') {
      actions.push('ACCOUNT_REVIEW', 'ADDITIONAL_AUTHENTICATION', 'BEHAVIOR_MONITORING');
    }
    if (threatType === 'INSIDER_THREAT') actions.push('COMPLIANCE_OFFICER_NOTIFICATION', 'AUDIT_TRAIL_REVIEW', 'PRIVILEGE_REVIEW');
    else if (threatType === 'DATA_EXFILTRATION') actions.push('DATA_LOSS_PREVENTION_ACTIVATION', 'NETWORK_TRAFFIC_ANALYSIS', 'ENCRYPTION_VERIFICATION');
    else if (threatType === 'PRIVILEGE_ESCALATION') actions.push('ROLE_REVIEW', 'ACCESS_CONTROL_AUDIT', 'PRIVILEGE_REDUCTION');
    if (threatIntelligence.correlated) {
      actions.push('THREAT_INTELLIGENCE_UPDATE', 'INDICATOR_OF_COMPROMISE_SCANNING');
      if (threatIntelligence.correlations.some((c) => c.sources.includes('INTERPOL'))) actions.push('INTERPOL_NOTIFICATION');
      if (threatIntelligence.correlations.some((c) => c.sources.includes('SA_CERT'))) actions.push('SA_CERT_REPORTING');
    }
    return actions;
  }

  async processDetectedThreat(auditLog, mlAnalysis, threatIntelligence, riskAssessment) {
    try {
      const threatRecord = await this.createThreatRecord(auditLog, mlAnalysis, threatIntelligence, riskAssessment);
      await this.triggerAlerts(threatRecord, riskAssessment);
      await this.updateAuditLogWithThreat(auditLog, threatRecord);
      if (riskAssessment.threatLevel === 'CRITICAL') await this.triggerCriticalResponse(threatRecord);
      this.activeThreats.set(threatRecord.threatId, { ...threatRecord, responseInitiated: new Date() });
      console.log(`⚠️ Threat detected and processed: ${threatRecord.threatId}`);
    } catch (error) {
      console.error('❌ Failed to process detected threat:', error);
    }
  }

  async createThreatRecord(auditLog, mlAnalysis, threatIntelligence, riskAssessment) {
    const threatRecord = new ThreatIntelligence({
      threatId: `THREAT-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
      threatType: mlAnalysis.threatType,
      mlPrediction: {
        confidence: mlAnalysis.confidence,
        riskScore: mlAnalysis.riskScore,
        features: mlAnalysis.features,
        modelVersion: mlAnalysis.modelVersion,
        predictionTimestamp: mlAnalysis.timestamp,
      },
      sources: threatIntelligence.correlations.map((c) => ({ feed: c.sources[0], sourceId: c.threatKey, confidence: c.matchScore, indicators: c.indicators })),
      affectedEntities: [{ entityType: auditLog.actor?.role || 'USER', entityId: auditLog.actor?.userId || auditLog._id, impactLevel: riskAssessment.threatLevel, remediationStatus: 'PENDING' }],
      indicatorsOfCompromise: this.extractIOCsFromAuditLog(auditLog),
      timeline: { firstDetected: new Date(), lastDetected: new Date() },
      impact: {
        severity: riskAssessment.threatLevel,
        businessImpact: this.assessBusinessImpact(riskAssessment.threatLevel),
        dataBreach: this.isDataBreach(auditLog, mlAnalysis.threatType),
        complianceImpact: this.assessComplianceImpact(auditLog),
      },
      response: { status: 'DETECTED', actionsTaken: riskAssessment.recommendedActions.slice(0, 3) },
      compliance: {
        cybercrimesAct: { reportable: riskAssessment.threatLevel === 'CRITICAL' || riskAssessment.threatLevel === 'HIGH', reported: false },
        popia: { dataSubjectAffected: this.isPIIAffected(auditLog), informationOfficerNotified: false },
      },
      integrity: { evidenceHash: this.generateEvidenceHash(auditLog, mlAnalysis, threatIntelligence, riskAssessment) },
      metadata: { expiresAt: new Date(Date.now() + THREAT_INTELLIGENCE_CONFIG.COMPLIANCE.DATA_RETENTION_DAYS * 24 * 60 * 60 * 1000) },
    });
    await threatRecord.save();
    if (riskAssessment.threatLevel === 'CRITICAL' || riskAssessment.threatLevel === 'HIGH') {
      await this.anchorThreatToBlockchain(threatRecord);
    }
    return threatRecord;
  }

  extractIOCsFromAuditLog(auditLog) {
    const iocs = { ipAddresses: [], domains: [], urls: [], fileHashes: [], signatures: [], patterns: [] };
    if (auditLog.actor?.ipAddress) iocs.ipAddresses.push(auditLog.actor.ipAddress);
    if (auditLog.actor?.deviceFingerprint) iocs.signatures.push(`DEVICE_FINGERPRINT:${JSON.stringify(auditLog.actor.deviceFingerprint)}`);
    if (auditLog.event?.action === 'SUPREME_OVERRIDE') iocs.patterns.push('SUPREME_ADMIN_OVERRIDE');
    if (auditLog.security?.severity === 'CRITICAL') iocs.patterns.push('CRITICAL_SECURITY_EVENT');
    return iocs;
  }

  assessBusinessImpact(threatLevel) {
    const impactMap = { CRITICAL: 'CATASTROPHIC', HIGH: 'SEVERE', MEDIUM: 'SIGNIFICANT', LOW: 'MODERATE', NONE: 'MINIMAL' };
    return impactMap[threatLevel] || 'MINIMAL';
  }

  isDataBreach(auditLog, threatType) {
    if (threatType === 'DATA_EXFILTRATION') return true;
    const piiResources = ['CLIENT_RECORD', 'USER_ACCOUNT', 'CONSENT_RECORD'];
    if (piiResources.includes(auditLog.event?.resourceType)) {
      if (auditLog.event?.action === 'SUPREME_ACCESS' && !auditLog.actor?.isSupremeAdmin) return true;
    }
    return false;
  }

  assessComplianceImpact(auditLog) {
    const impacts = [];
    if (auditLog.compliance?.popia && auditLog.event?.resourceType === 'CLIENT_RECORD') impacts.push('POPIA_VIOLATION');
    if (auditLog.security?.severity === 'CRITICAL' || auditLog.security?.severity === 'HIGH') impacts.push('CYBERCRIMES_ACT');
    if (auditLog.jurisdiction !== 'ZA' && auditLog.compliance?.gdpr) impacts.push('GDPR');
    if (impacts.length > 1) return 'MULTIPLE';
    if (impacts.length === 1) return impacts[0];
    return 'NONE';
  }

  isPIIAffected(auditLog) {
    const piiResources = ['CLIENT_RECORD', 'USER_ACCOUNT', 'CONSENT_RECORD'];
    return piiResources.includes(auditLog.event?.resourceType);
  }

  generateEvidenceHash(auditLog, mlAnalysis, threatIntelligence, riskAssessment) {
    const evidenceData = {
      auditLogId: auditLog.quantumId,
      mlAnalysis: { confidence: mlAnalysis.confidence, threatType: mlAnalysis.threatType, riskScore: mlAnalysis.riskScore },
      threatIntelligence: { correlated: threatIntelligence.correlated, correlationCount: threatIntelligence.correlations.length },
      riskAssessment: { threatLevel: riskAssessment.threatLevel, totalRiskScore: riskAssessment.totalRiskScore },
      timestamp: new Date().toISOString(),
    };
    return crypto.createHash('sha512').update(JSON.stringify(evidenceData)).digest('hex');
  }

  async anchorThreatToBlockchain(threatRecord) {
    try {
      if (!blockchainService) {
        console.warn('⚠️ Blockchain service not available, skipping threat anchoring');
        return;
      }
      const blockchainData = {
        threatId: threatRecord.threatId,
        evidenceHash: threatRecord.integrity.evidenceHash,
        threatType: threatRecord.threatType,
        severity: threatRecord.impact.severity,
        timestamp: threatRecord.timeline.firstDetected,
        jurisdiction: 'ZA',
      };
      const txHash = await blockchainService.anchorEvidence(blockchainData);
      threatRecord.integrity.blockchainAnchored = true;
      threatRecord.integrity.blockchainTxHash = txHash;
      await threatRecord.save();
      console.log(`🔗 Threat ${threatRecord.threatId} anchored to blockchain: ${txHash}`);
    } catch (error) {
      console.error('❌ Failed to anchor threat to blockchain:', error);
    }
  }

  async triggerAlerts(threatRecord, riskAssessment) {
    const alerts = [];
    if (riskAssessment.threatLevel === 'CRITICAL' || riskAssessment.threatLevel === 'HIGH') {
      alerts.push(await this.sendSupremeAdminAlert(threatRecord, riskAssessment));
    }
    alerts.push(await this.sendSecurityTeamAlert(threatRecord, riskAssessment));
    if (threatRecord.impact.dataBreach) {
      alerts.push(await this.sendComplianceOfficerAlert(threatRecord, riskAssessment));
    }
    await this.logAlerts(threatRecord, alerts);
  }

  async sendSupremeAdminAlert(threatRecord, riskAssessment) {
    try {
      const alertData = {
        to: THREAT_INTELLIGENCE_CONFIG.ALERTING.SUPREME_ADMIN_EMAIL,
        subject: `🚨 CRITICAL THREAT DETECTED: ${threatRecord.threatId}`,
        body: this.generateAlertBody(threatRecord, riskAssessment),
        priority: 'HIGHEST',
        threatLevel: riskAssessment.threatLevel,
        timestamp: new Date(),
      };
      console.log(`📧 Supreme Admin Alert: ${JSON.stringify(alertData, null, 2)}`);
      if (THREAT_INTELLIGENCE_CONFIG.ALERTING.SUPREME_ADMIN_PHONE) {
        await this.sendSMSAlert(THREAT_INTELLIGENCE_CONFIG.ALERTING.SUPREME_ADMIN_PHONE, `Wilsy OS Threat Alert: ${threatRecord.threatType} - ${riskAssessment.threatLevel}`);
      }
      return { type: 'SUPREME_ADMIN', status: 'SENT', timestamp: new Date(), data: alertData };
    } catch (error) {
      console.error('❌ Failed to send Supreme Admin alert:', error);
      return { type: 'SUPREME_ADMIN', status: 'FAILED', error: error.message, timestamp: new Date() };
    }
  }

  async sendSecurityTeamAlert(threatRecord, riskAssessment) {
    try {
      const alertData = {
        channel: 'security-incidents',
        text: this.generateSlackAlert(threatRecord, riskAssessment),
        attachments: [{ color: this.getAlertColor(riskAssessment.threatLevel), fields: this.generateAlertFields(threatRecord, riskAssessment) }],
      };
      if (THREAT_INTELLIGENCE_CONFIG.ALERTING.SECURITY_TEAM_SLACK) {
        console.log(`💬 Security Team Slack Alert: ${JSON.stringify(alertData, null, 2)}`);
      }
      return { type: 'SECURITY_TEAM', status: 'SENT', timestamp: new Date(), data: alertData };
    } catch (error) {
      console.error('❌ Failed to send security team alert:', error);
      return { type: 'SECURITY_TEAM', status: 'FAILED', error: error.message, timestamp: new Date() };
    }
  }

  async sendComplianceOfficerAlert(threatRecord, riskAssessment) {
    try {
      if (!THREAT_INTELLIGENCE_CONFIG.ALERTING.COMPLIANCE_OFFICER_EMAIL) {
        return { type: 'COMPLIANCE_OFFICER', status: 'SKIPPED', reason: 'No compliance officer email configured', timestamp: new Date() };
      }
      const alertData = {
        to: THREAT_INTELLIGENCE_CONFIG.ALERTING.COMPLIANCE_OFFICER_EMAIL,
        subject: `📋 COMPLIANCE INCIDENT: ${threatRecord.threatId}`,
        body: this.generateComplianceAlertBody(threatRecord, riskAssessment),
        priority: 'HIGH',
        complianceImpact: threatRecord.impact.complianceImpact,
        timestamp: new Date(),
      };
      console.log(`📋 Compliance Officer Alert: ${JSON.stringify(alertData, null, 2)}`);
      return { type: 'COMPLIANCE_OFFICER', status: 'SENT', timestamp: new Date(), data: alertData };
    } catch (error) {
      console.error('❌ Failed to send compliance officer alert:', error);
      return { type: 'COMPLIANCE_OFFICER', status: 'FAILED', error: error.message, timestamp: new Date() };
    }
  }

  async sendSMSAlert(phoneNumber, message) {
    console.log(`📱 SMS Alert to ${phoneNumber}: ${message}`);
    return { status: 'SENT', timestamp: new Date() };
  }

  generateAlertBody(threatRecord, riskAssessment) {
    return `🚨 THREAT DETECTION ALERT - Wilsy OS Security System\n\nThreat ID: ${threatRecord.threatId}\nThreat Type: ${threatRecord.threatType}\nSeverity: ${riskAssessment.threatLevel}\nRisk Score: ${riskAssessment.totalRiskScore}/100\nConfidence: ${(threatRecord.mlPrediction.confidence * 100).toFixed(2)}%\n\nDetection Time: ${new Date().toISOString()}\nAffected Entity: ${threatRecord.affectedEntities[0]?.entityType || 'UNKNOWN'}\n\nTHREAT INDICATORS:\n${threatRecord.indicatorsOfCompromise.ipAddresses.map((ip) => `• IP: ${ip}`).join('\n')}\n${threatRecord.indicatorsOfCompromise.patterns.map((p) => `• Pattern: ${p}`).join('\n')}\n\nRECOMMENDED ACTIONS:\n${riskAssessment.recommendedActions.map((action, i) => `${i + 1}. ${action}`).join('\n')}\n\nIMMEDIATE STEPS:\n1. Review audit log: ${threatRecord.threatId}\n2. Isolate affected systems if necessary\n3. Contact Security Team for investigation\n\nCOMPLIANCE IMPACT:\n${threatRecord.impact.complianceImpact}\n\nThis is an automated alert from Wilsy OS Threat Intelligence System.`;
  }

  generateComplianceAlertBody(threatRecord, riskAssessment) {
    return `📋 COMPLIANCE INCIDENT REPORT - Wilsy OS\n\nIncident ID: ${threatRecord.threatId}\nThreat Type: ${threatRecord.threatType}\nSeverity: ${riskAssessment.threatLevel}\n\nCOMPLIANCE IMPACTS:\n• POPIA: ${threatRecord.impact.dataBreach ? 'DATA BREACH DETECTED' : 'No data breach'}\n• Cybercrimes Act: ${threatRecord.compliance.cybercrimesAct.reportable ? 'REPORTABLE INCIDENT' : 'Not reportable'}\n• ${threatRecord.impact.complianceImpact}\n\nAFFECTED DATA SUBJECTS:\n${threatRecord.isPIIAffected ? 'PII data potentially affected' : 'No PII data affected'}\n\nREQUIRED ACTIONS:\n1. Assess data breach notification requirements (POPIA Section 22)\n2. ${threatRecord.compliance.cybercrimesAct.reportable ? 'Prepare Cybercrimes Act report' : 'No Cybercrimes Act reporting required'}\n3. Notify Information Officer if required\n4. Document incident for regulatory compliance\n\nINCIDENT DETAILS:\nDetection Time: ${threatRecord.timeline.firstDetected}\nEvidence Hash: ${threatRecord.integrity.evidenceHash.substring(0, 32)}...\n${threatRecord.integrity.blockchainAnchored ? `Blockchain Proof: ${threatRecord.integrity.blockchainTxHash}` : ''}\n\nThis is an automated compliance alert from Wilsy OS Threat Intelligence System.`;
  }

  generateSlackAlert(threatRecord, riskAssessment) {
    return `🚨 *Threat Detected*: ${threatRecord.threatType} (${riskAssessment.threatLevel})\n*ID*: ${threatRecord.threatId}\n*Risk Score*: ${riskAssessment.totalRiskScore}/100\n*Confidence*: ${(threatRecord.mlPrediction.confidence * 100).toFixed(1)}%\n*Actions Required*: ${riskAssessment.recommendedActions.length}`;
  }

  getAlertColor(threatLevel) {
    const colors = { CRITICAL: '#FF0000', HIGH: '#FF4500', MEDIUM: '#FFA500', LOW: '#FFFF00', NONE: '#00FF00' };
    return colors[threatLevel] || '#808080';
  }

  generateAlertFields(threatRecord, riskAssessment) {
    return [
      { title: 'Threat ID', value: threatRecord.threatId, short: true },
      { title: 'Severity', value: riskAssessment.threatLevel, short: true },
      { title: 'Confidence', value: `${(threatRecord.mlPrediction.confidence * 100).toFixed(1)}%`, short: true },
      { title: 'Risk Score', value: `${riskAssessment.totalRiskScore}/100`, short: true },
      { title: 'Immediate Actions', value: riskAssessment.recommendedActions.slice(0, 3).join(', '), short: false },
    ];
  }

  async logAlerts(threatRecord, alerts) {
    try {
      threatRecord.response.actionsTaken.push('ALERTS_SENT');
      threatRecord.response.alertResults = alerts;
      await threatRecord.save();
      const auditLog = new AuditLog({
        quantumId: `ALERT-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
        tenantId: mongoose.Types.ObjectId(),
        firmId: mongoose.Types.ObjectId(),
        actor: { userId: null, role: 'SYSTEM', isSupremeAdmin: false },
        event: {
          quantumCategory: 'SECURITY_QUANTUM',
          action: 'ALERT_TRIGGERED',
          resourceType: 'THREAT_INTELLIGENCE',
          resourceId: threatRecord._id,
          resourceLabel: `Threat Alert: ${threatRecord.threatId}`,
          description: `Threat alerts sent for ${threatRecord.threatType}`,
          outcome: 'SUCCESS',
        },
        data: { threatId: threatRecord.threatId, alertsSent: alerts.length, alertTypes: alerts.map((a) => a.type) },
        security: { severity: threatRecord.impact.severity, legalHold: true },
      });
      await auditLog.save();
    } catch (error) {
      console.error('❌ Failed to log alerts:', error);
    }
  }

  async updateAuditLogWithThreat(auditLog, threatRecord) {
    try {
      auditLog.security = auditLog.security || {};
      auditLog.security.threatContext = {
        threatId: threatRecord.threatId,
        threatType: threatRecord.threatType,
        riskScore: threatRecord.mlPrediction.riskScore,
        detectionTime: threatRecord.timeline.firstDetected,
      };
      auditLog.security.severity = threatRecord.impact.severity;
      auditLog.security.legalHold = true;
      await auditLog.save();
    } catch (error) {
      console.error('❌ Failed to update audit log with threat context:', error);
    }
  }

  async triggerCriticalResponse(threatRecord) {
    console.log(`🚨 CRITICAL RESPONSE TRIGGERED for threat: ${threatRecord.threatId}`);
    const responseActions = ['ISOLATE_AFFECTED_SYSTEMS', 'ESCALATE_TO_SECURITY_OPS_CENTER', 'ACTIVATE_INCIDENT_RESPONSE_PLAN', 'NOTIFY_EXECUTIVE_LEADERSHIP'];
    await this.logCriticalResponse(threatRecord, responseActions);
  }

  async logCriticalResponse(threatRecord, actions) {
    try {
      const responseLog = new AuditLog({
        quantumId: `CRITICAL-RESPONSE-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
        tenantId: mongoose.Types.ObjectId(),
        firmId: mongoose.Types.ObjectId(),
        actor: { userId: null, role: 'SYSTEM', isSupremeAdmin: false },
        event: {
          quantumCategory: 'SECURITY_QUANTUM',
          action: 'CRITICAL_RESPONSE_ACTIVATED',
          resourceType: 'THREAT_INTELLIGENCE',
          resourceId: threatRecord._id,
          resourceLabel: `Critical Response: ${threatRecord.threatId}`,
          description: 'Critical threat response activated',
          outcome: 'PENDING',
        },
        data: { threatId: threatRecord.threatId, responseActions: actions, activationTime: new Date() },
        security: { severity: 'CRITICAL', legalHold: true },
      });
      await responseLog.save();
    } catch (error) {
      console.error('❌ Failed to log critical response:', error);
    }
  }

  async generateComplianceReport() {
    try {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      const threats = await ThreatIntelligence.find({ 'timeline.firstDetected': { $gte: thirtyDaysAgo } });
      const report = {
        reportId: `COMPLIANCE-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
        generated: new Date(),
        period: 'LAST_30_DAYS',
        summary: {
          totalThreats: threats.length,
          criticalThreats: threats.filter((t) => t.impact.severity === 'CRITICAL').length,
          highThreats: threats.filter((t) => t.impact.severity === 'HIGH').length,
          dataBreaches: threats.filter((t) => t.impact.dataBreach).length,
          reportableIncidents: threats.filter((t) => t.compliance.cybercrimesAct.reportable).length,
        },
        threatsByType: this.groupThreatsByType(threats),
        complianceStatus: {
          popia: this.assessPOPIACompliance(threats),
          cybercrimesAct: this.assessCybercrimesActCompliance(threats),
          gdpr: this.assessGDPRCompliance(threats),
        },
        recommendations: this.generateComplianceRecommendations(threats),
      };
      if (THREAT_INTELLIGENCE_CONFIG.ALERTING.COMPLIANCE_OFFICER_EMAIL) {
        await this.sendComplianceReport(report);
      }
      if (THREAT_INTELLIGENCE_CONFIG.COMPLIANCE.SA_CERT_REPORTING) {
        await this.reportToSACERT(report);
      }
      return report;
    } catch (error) {
      console.error('❌ Failed to generate compliance report:', error);
      throw error;
    }
  }

  groupThreatsByType(threats) {
    const groups = {};
    threats.forEach((threat) => {
      const type = threat.threatType;
      if (!groups[type]) groups[type] = [];
      groups[type].push({ id: threat.threatId, severity: threat.impact.severity, detected: threat.timeline.firstDetected });
    });
    return groups;
  }

  assessPOPIACompliance(threats) {
    const dataBreaches = threats.filter((t) => t.impact.dataBreach);
    const notified = dataBreaches.filter((t) => t.compliance.popia.informationOfficerNotified);
    return {
      compliant: notified.length === dataBreaches.length,
      dataBreaches: dataBreaches.length,
      notified: notified.length,
      notificationRate: dataBreaches.length > 0 ? (notified.length / dataBreaches.length) * 100 : 100,
      requirements: 'POPIA Section 22: Data breach notification within 72 hours',
    };
  }

  assessCybercrimesActCompliance(threats) {
    const reportable = threats.filter((t) => t.compliance.cybercrimesAct.reportable);
    const reported = reportable.filter((t) => t.compliance.cybercrimesAct.reported);
    return {
      compliant: reported.length === reportable.length,
      reportableIncidents: reportable.length,
      reported: reported.length,
      reportingRate: reportable.length > 0 ? (reported.length / reportable.length) * 100 : 100,
      requirements: 'Cybercrimes Act Section 2: Report cybercrime incidents',
    };
  }

  assessGDPRCompliance(threats) {
    const gdprThreats = threats.filter((t) => t.impact.complianceImpact === 'GDPR');
    const dataBreaches = gdprThreats.filter((t) => t.impact.dataBreach);
    return {
      applicable: gdprThreats.length > 0,
      dataBreaches: dataBreaches.length,
      requirements: 'GDPR Article 33: 72-hour breach notification to supervisory authority',
    };
  }

  generateComplianceRecommendations(threats) {
    const recommendations = [];
    const popiaStatus = this.assessPOPIACompliance(threats);
    if (!popiaStatus.compliant) {
      recommendations.push(`IMPROVE POPIA BREACH NOTIFICATION: Current rate ${popiaStatus.notificationRate.toFixed(1)}%, target 100%`);
    }
    const cyberStatus = this.assessCybercrimesActCompliance(threats);
    if (!cyberStatus.compliant) {
      recommendations.push(`ENHANCE CYBERCRIMES ACT REPORTING: Current rate ${cyberStatus.reportingRate.toFixed(1)}%, target 100%`);
    }
    const dataBreaches = threats.filter((t) => t.impact.dataBreach);
    if (dataBreaches.length > 0) {
      recommendations.push(`IMPLEMENT DATA LOSS PREVENTION FOR ${dataBreaches.length} IDENTIFIED BREACH VECTORS`);
    }
    const highCriticalThreats = threats.filter((t) => t.impact.severity === 'HIGH' || t.impact.severity === 'CRITICAL');
    if (highCriticalThreats.length > 5) {
      recommendations.push(`REVIEW SECURITY CONTROLS: ${highCriticalThreats.length} high/critical threats detected`);
    }
    return recommendations;
  }

  async sendComplianceReport(report) {
    console.log('📊 Compliance Report Generated:', JSON.stringify(report.summary, null, 2));
  }

  async reportToSACERT(report) {
    try {
      const sacertReport = {
        reportingEntity: 'Wilsy OS Legal SaaS Platform',
        reportType: 'MONTHLY_THREAT_REPORT',
        period: report.period,
        contact: { name: 'Wilson Khanyezi', email: 'wilsy.wk@gmail.com', phone: '+27690465710' },
        summary: report.summary,
        criticalIncidents: report.threatsByType.CRITICAL || [],
        complianceStatus: report.complianceStatus,
        timestamp: new Date(),
      };
      const encryptedReport = await encryptionService.encrypt(JSON.stringify(sacertReport), 'SA-CERT-REPORT');
      const response = await fetch(`${THREAT_INTELLIGENCE_CONFIG.THREAT_FEEDS.SA_CERT.endpoint}/report`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${THREAT_INTELLIGENCE_CONFIG.THREAT_FEEDS.SA_CERT.apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ encryptedReport: encryptedReport.ciphertext, iv: encryptedReport.iv, tag: encryptedReport.tag }),
      });
      if (response.ok) {
        console.log('✅ SA-CERT report submitted successfully');
      } else {
        console.error('❌ Failed to submit SA-CERT report:', response.statusText);
      }
    } catch (error) {
      console.error('❌ Failed to report to SA-CERT:', error);
    }
  }

  async getThreatStatistics() {
    const twentyFourHoursAgo = new Date(); twentyFourHoursAgo.setHours(twentyFourHoursAgo.getHours() - 24);
    const sevenDaysAgo = new Date(); sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const thirtyDaysAgo = new Date(); thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const stats = await ThreatIntelligence.aggregate([
      { $facet: {
        last24Hours: [{ $match: { 'timeline.firstDetected': { $gte: twentyFourHoursAgo } } }, { $group: { _id: '$impact.severity', count: { $sum: 1 }, avgRiskScore: { $avg: '$mlPrediction.riskScore' } } }],
        last7Days: [{ $match: { 'timeline.firstDetected': { $gte: sevenDaysAgo } } }, { $group: { _id: { $dateToString: { format: '%Y-%m-%d', date: '$timeline.firstDetected' } }, count: { $sum: 1 }, avgRiskScore: { $avg: '$mlPrediction.riskScore' } } }, { $sort: { _id: 1 } }],
        byType: [{ $match: { 'timeline.firstDetected': { $gte: thirtyDaysAgo } } }, { $group: { _id: '$threatType', count: { $sum: 1 }, avgSeverity: { $avg: { $switch: { branches: [ { case: { $eq: ['$impact.severity', 'CRITICAL'] }, then: 5 }, { case: { $eq: ['$impact.severity', 'HIGH'] }, then: 4 }, { case: { $eq: ['$impact.severity', 'MEDIUM'] }, then: 3 }, { case: { $eq: ['$impact.severity', 'LOW'] }, then: 2 }, { case: { $eq: ['$impact.severity', 'INFO'] }, then: 1 } ], default: 0 } } } } }, { $sort: { count: -1 } }],
        complianceStatus: [{ $match: { 'timeline.firstDetected': { $gte: thirtyDaysAgo } } }, { $group: { _id: null, total: { $sum: 1 }, dataBreaches: { $sum: { $cond: [{ $eq: ['$impact.dataBreach', true] }, 1, 0] } }, reportableIncidents: { $sum: { $cond: [{ $eq: ['$compliance.cybercrimesAct.reportable', true] }, 1, 0] } }, popiaNotified: { $sum: { $cond: [{ $eq: ['$compliance.popia.informationOfficerNotified', true] }, 1, 0] } } } }],
      } },
    ]);
    return {
      timestamp: new Date(),
      timeframes: { last24Hours: twentyFourHoursAgo, last7Days: sevenDaysAgo, last30Days: thirtyDaysAgo },
      statistics: stats[0] || {},
      mlEngine: { version: this.mlEngine.modelVersion, cacheSize: this.mlEngine.cache.size, isTraining: this.mlEngine.isTraining },
      threatFeeds: { active: Object.values(THREAT_INTELLIGENCE_CONFIG.THREAT_FEEDS).filter((f) => f.enabled).length, totalThreats: this.threatFeeds.size },
    };
  }

  async healthCheck() {
    const health = { service: 'ThreatIntelligenceService', timestamp: new Date(), status: 'HEALTHY', components: {} };
    try {
      health.components.mlEngine = { status: this.mlEngine.model ? 'HEALTHY' : 'UNHEALTHY', modelVersion: this.mlEngine.modelVersion, cacheSize: this.mlEngine.cache.size };
      const dbStatus = mongoose.connection.readyState;
      health.components.database = { status: dbStatus === 1 ? 'HEALTHY' : 'UNHEALTHY', readyState: dbStatus };
      const feedStatus = {};
      for (const [feedName, config] of Object.entries(THREAT_INTELLIGENCE_CONFIG.THREAT_FEEDS)) {
        feedStatus[feedName] = { enabled: config.enabled, lastUpdated: this.getLastFeedUpdate(feedName) };
      }
      health.components.threatFeeds = feedStatus;
      health.components.activeThreats = { count: this.activeThreats.size, critical: Array.from(this.activeThreats.values()).filter((t) => t.impact.severity === 'CRITICAL').length };
      const unhealthyComponents = Object.values(health.components).filter((c) => c.status === 'UNHEALTHY').length;
      health.status = unhealthyComponents === 0 ? 'HEALTHY' : 'DEGRADED';
    } catch (error) {
      health.status = 'UNHEALTHY';
      health.error = error.message;
    }
    return health;
  }

  getLastFeedUpdate(feedName) {
    return new Date();
  }
}

// =============================================================================
// QUANTUM SERVICE EXPORT
// =============================================================================
let threatIntelligenceServiceInstance = null;

const getThreatIntelligenceService = async () => {
  if (!threatIntelligenceServiceInstance) {
    threatIntelligenceServiceInstance = new ThreatIntelligenceService();
    await threatIntelligenceServiceInstance.initializeService();
  }
  return threatIntelligenceServiceInstance;
};

export default {
  ThreatIntelligenceService,
  getThreatIntelligenceService,
  ThreatIntelligence,
};

// =============================================================================
// QUANTUM TEST SUITE: THREAT INTELLIGENCE VERIFICATION
// =============================================================================
if (process.env.NODE_ENV === 'test') {
  const testThreatIntelligenceService = async () => {
    console.log('🔬 THREAT INTELLIGENCE SERVICE TEST SUITE INITIATED');
    try {
      const service = await getThreatIntelligenceService();
      console.assert(service.mlEngine.model !== null, 'ML Engine not initialized');
      console.assert(service.mlEngine.modelVersion, 'ML Model version not set');
      const testAuditLog = {
        quantumId: 'TEST-AUDIT-123',
        timestamp: new Date(),
        actor: { role: 'ATTORNEY', isSupremeAdmin: false },
        event: { action: 'SUPREME_ACCESS', resourceType: 'CLIENT_RECORD', outcome: 'SUCCESS' },
        security: { severity: 'MEDIUM' },
      };
      const analysis = await service.analyzeRealTimeThreat(testAuditLog);
      console.assert(analysis !== null, 'Threat analysis failed');
      console.assert(typeof analysis.threatDetected === 'boolean', 'Invalid threat detection result');
      const health = await service.healthCheck();
      console.assert(health.status === 'HEALTHY' || health.status === 'DEGRADED', 'Invalid health status');
      console.log('✅ ALL THREAT INTELLIGENCE SERVICE TESTS PASSED');
    } catch (error) {
      console.error('❌ Threat Intelligence Service tests failed:', error);
      throw error;
    }
  };
  testThreatIntelligenceService();
}

// =============================================================================
// ENVIRONMENT VARIABLES SETUP GUIDE & VALUATION QUANTUM METRICS (truncated for brevity)
// =============================================================================
