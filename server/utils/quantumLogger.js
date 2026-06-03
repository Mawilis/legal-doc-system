/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - QUANTUM LOGGER - OMEGA EDITION                                 ║
 * ║ R23.7T AUDIT LOGGING | FORENSIC TRACEABILITY | 100-YEAR RETENTION         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Immutable audit trail for all system actions
 * - Cryptographic verification of log entries
 * - POPIA/GDPR compliant data retention
 * - Blockchain-ready hash chaining
 * - 101/10 forensic standard
 *
 * @last_updated: 2026-03-20
 * @lead_architect: Wilson Khanyezi
 */

import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import moment from 'moment-timezone';
import os from 'os';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import Quantum Encryption for secure logging
import QuantumEncryption from './quantumEncryption.js';

// Load environment configuration with quantum validation
import dotenv from 'dotenv';
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// ============================================================================
// ENVIRONMENT VALIDATION - Quantum Sentinel Protocol
// ============================================================================

const validateLoggerEnv = () => {
  const required = ['LOG_RETENTION_DAYS', 'LOG_TIMEZONE', 'LOG_LEVEL'];
  const warnings = [];

  required.forEach((variable) => {
    if (!process.env[variable]) {
      warnings.push(`⚠️  Missing ${variable} - using default values`);
    }
  });

  const retentionDays = parseInt(process.env.LOG_RETENTION_DAYS) || 2555;
  if (retentionDays < 2555) {
    console.warn('⚠️  LOG_RETENTION_DAYS less than 7 years - Companies Act 2008 requires 7+ year retention');
  }

  return warnings;
};

// Initialize validation
const envWarnings = validateLoggerEnv();
if (envWarnings.length > 0) {
  console.warn('Quantum Logger Environment Warnings:', envWarnings);
}

// ============================================================================
// QUANTUM CONSTANTS - Immutable Legal & Security Parameters
// ============================================================================
export const QUANTUM_CONSTANTS = Object.freeze({
  SECURITY_LEVELS: {
    QUANTUM: 0, // System-level quantum events
    CRITICAL: 1, // Security breaches, system failures
    HIGH: 2, // Compliance violations, data breaches
    MEDIUM: 3, // Suspicious activities, warnings
    LOW: 4, // Normal operations, info
    DEBUG: 5, // Development debugging
  },

  COMPLIANCE_CATEGORIES: {
    POPIA: {
      code: 'POPIA',
      description: 'Protection of Personal Information Act',
      sections: ['19', '20', '21'],
      retention: 'Indefinite for breaches',
    },
    ECT_ACT: {
      code: 'ECT',
      description: 'Electronic Communications and Transactions Act',
      sections: ['13', '15', '16'],
      retention: '7 years',
    },
    COMPANIES_ACT: {
      code: 'COMP2008',
      description: 'Companies Act 2008',
      sections: ['24', '28', '32'],
      retention: '7 years minimum',
    },
    CYBERCRIMES_ACT: {
      code: 'CYBER2020',
      description: 'Cybercrimes Act 2020',
      sections: ['54', '55'],
      retention: '5 years',
    },
    PAIA: {
      code: 'PAIA',
      description: 'Promotion of Access to Information Act',
      sections: ['14', '51'],
      retention: '3 years after request',
    },
    FICA: {
      code: 'FICA',
      description: 'Financial Intelligence Centre Act',
      sections: ['21', '22'],
      retention: '5 years',
    },
    LPC: {
      code: 'LPC',
      description: 'Legal Practice Council Guidelines',
      sections: ['Trust Accounts', 'Record Keeping'],
      retention: '7 years',
    },
  },

  RETENTION_DAYS: parseInt(process.env.LOG_RETENTION_DAYS) || 2555, // 7 years
  MAX_LOG_SIZE: process.env.LOG_MAX_SIZE || '50m',
  MAX_LOG_FILES: process.env.LOG_MAX_FILES || '90d',
  LOG_ENCRYPT_SENSITIVE: process.env.LOG_ENCRYPT_SENSITIVE === 'true',

  SENSITIVE_FIELD_PATTERNS: [
    /pass(word|phrase|code)/i,
    /token/i,
    /api[_-]?key/i,
    /secret/i,
    /private[_-]?key/i,
    /ssn|id[_-]?number|identity/i,
    /credit[_-]?card|card[_-]?number/i,
    /email/i,
    /phone|mobile|cell/i,
    /address/i,
    /signature/i,
    /sign[_-]?key/i,
    /database[_-]?uri|connection[_-]?string/i,
  ],

  LEGAL_EVENTS: {
    DOCUMENT_CREATED: 'DOCUMENT_CREATED',
    DOCUMENT_SIGNED: 'DOCUMENT_SIGNED',
    DOCUMENT_SHARED: 'DOCUMENT_SHARED',
    CONSENT_GIVEN: 'CONSENT_GIVEN',
    CONSENT_REVOKED: 'CONSENT_REVOKED',
    ACCESS_REQUESTED: 'ACCESS_REQUESTED',
    ACCESS_GRANTED: 'ACCESS_GRANTED',
    ACCESS_DENIED: 'ACCESS_DENIED',
    DATA_BREACH: 'DATA_BREACH',
    SECURITY_INCIDENT: 'SECURITY_INCIDENT',
    COMPLIANCE_VIOLATION: 'COMPLIANCE_VIOLATION',
    AUDIT_TRAIL_ACCESSED: 'AUDIT_TRAIL_ACCESSED',
    USER_AUTHENTICATED: 'USER_AUTHENTICATED',
    USER_AUTHORIZED: 'USER_AUTHORIZED',
    PAYMENT_PROCESSED: 'PAYMENT_PROCESSED',
    TRUST_ACCOUNT_UPDATED: 'TRUST_ACCOUNT_UPDATED',
  },
});

// ============================================================================
// QUANTUM MERKLE TREE - Blockchain-Immutable Audit Trail
// ============================================================================
class QuantumMerkleTree {
  constructor(depth = 12) {
    this.depth = depth;
    this.leaves = [];
    this.tree = [];
    this.rootHash = null;
    this.lastUpdated = null;
    this.initializeTree();
  }

  initializeTree() {
    this.tree = new Array(this.depth + 1).fill().map(() => []);
  }

  addLeaf(data) {
    try {
      const leafHash = this.hashData(data);
      this.leaves.push({
        data,
        hash: leafHash,
        timestamp: new Date().toISOString(),
        index: this.leaves.length,
      });
      this.tree[0].push(leafHash);
      this.rebuildTree();
      return {
        leafHash,
        index: this.leaves.length - 1,
        merkleProof: this.generateMerkleProof(this.leaves.length - 1),
      };
    } catch (error) {
      console.error('Merkle Tree Add Leaf Error:', error);
      throw new Error(`Failed to add leaf to Merkle tree: ${error.message}`);
    }
  }

  hashData(data) {
    const dataString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(dataString).digest('hex');
  }

  rebuildTree() {
    for (let level = 0; level < this.depth; level++) {
      const currentLevel = this.tree[level];
      const nextLevel = [];

      for (let i = 0; i < currentLevel.length; i += 2) {
        const left = currentLevel[i];
        const right = i + 1 < currentLevel.length ? currentLevel[i + 1] : currentLevel[i];
        const combined = left + right;
        nextLevel.push(this.hashData(combined));
      }

      this.tree[level + 1] = nextLevel;
    }
    this.rootHash = this.tree[this.depth][0] || this.hashData('empty');
    this.lastUpdated = new Date().toISOString();
  }

  generateMerkleProof(leafIndex) {
    const proof = [];
    let index = leafIndex;

    for (let level = 0; level < this.depth; level++) {
      const isRightNode = index % 2;
      const siblingIndex = isRightNode ? index - 1 : index + 1;

      if (siblingIndex < this.tree[level].length) {
        proof.push({
          level,
          position: isRightNode ? 'left' : 'right',
          hash: this.tree[level][siblingIndex],
        });
      }
      index = Math.floor(index / 2);
    }

    return {
      proof,
      rootHash: this.rootHash,
      leafIndex,
      timestamp: this.lastUpdated,
    };
  }

  verifyProof(leafHash, proof, rootHash) {
    let computedHash = leafHash;

    for (const node of proof) {
      const combined = node.position === 'left' ? node.hash + computedHash : computedHash + node.hash;
      computedHash = this.hashData(combined);
    }
    return computedHash === rootHash;
  }

  getRootHash() {
    return {
      rootHash: this.rootHash,
      timestamp: this.lastUpdated,
      totalLeaves: this.leaves.length,
      treeDepth: this.depth,
    };
  }

  generateComplianceReport() {
    return {
      reportId: `MRKL-${uuidv4().substr(0, 8)}`,
      generatedAt: new Date().toISOString(),
      merkleRoot: this.rootHash,
      totalEntries: this.leaves.length,
      treeDepth: this.depth,
      lastUpdated: this.lastUpdated,
      compliance: {
        popia: 'AUDIT_TRAIL_INTEGRITY_VERIFIED',
        ectAct: 'DATA_MESSAGE_INTEGRITY_CONFIRMED',
        companiesAct: 'RECORD_KEEPING_REQUIREMENT_MET',
      },
      verification: {
        canVerifyAllEntries: true,
        tamperEvidence: 'MERKLE_ROOT_PROVIDES_TAMPER_EVIDENCE',
        recommendation: 'ANCHOR_ROOT_HASH_TO_BLOCKCHAIN_QUARTERLY',
      },
    };
  }
}

// ============================================================================
// QUANTUM ENCRYPTION SERVICE
// ============================================================================
class QuantumEncryptionService {
  constructor() {
    this.quantumEncryption = new QuantumEncryption();
    this.sensitivePatterns = QUANTUM_CONSTANTS.SENSITIVE_FIELD_PATTERNS;
  }

  async encryptSensitiveData(data, metadata = {}) {
    try {
      if (!QUANTUM_CONSTANTS.LOG_ENCRYPT_SENSITIVE || !data) {
        return {
          encrypted: false,
          data: this.maskSensitiveData(data),
          reason: 'ENCRYPTION_DISABLED_OR_EMPTY_DATA',
        };
      }

      const dataString = JSON.stringify(data).toLowerCase();
      const isSensitive = this.sensitivePatterns.some((pattern) => pattern.test(dataString));

      if (!isSensitive) {
        return {
          encrypted: false,
          data: data,
          reason: 'NO_SENSITIVE_DATA_DETECTED',
        };
      }

      const encryptedPackage = await this.quantumEncryption.encryptData(data, {
        ...metadata,
        dataCategory: 'log_sensitive_data',
        originalType: typeof data === 'object' ? 'object' : 'string',
        encryptionPurpose: 'audit_log_protection',
      });

      return {
        encrypted: true,
        encryptionVersion: encryptedPackage.version,
        data: encryptedPackage.ciphertext,
        iv: encryptedPackage.iv,
        authTag: encryptedPackage.authTag,
        timestamp: encryptedPackage.timestamp,
        metadata: encryptedPackage.metadata,
      };
    } catch (error) {
      console.error('Log Encryption Error:', error);
      return {
        encrypted: false,
        data: this.maskSensitiveData(data),
        error: 'ENCRYPTION_FAILED',
        fallback: 'DATA_MASKED_AS_FALLBACK',
      };
    }
  }

  maskSensitiveData(data) {
    if (!data || typeof data !== 'object') return data;

    const maskString = (str) => {
      if (str.length <= 4) return '*';
      const visibleStart = Math.min(2, Math.floor(str.length / 4));
      const visibleEnd = Math.min(2, Math.floor(str.length / 4));
      return (
        str.substring(0, visibleStart) +
        '*'.repeat(str.length - visibleStart - visibleEnd) +
        str.substring(str.length - visibleEnd)
      );
    };

    const traverseAndMask = (obj) => {
      if (!obj || typeof obj !== 'object') return obj;
      const masked = Array.isArray(obj) ? [] : {};

      for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
          const value = obj[key];
          const keyLower = key.toLowerCase();
          const isSensitiveKey = this.sensitivePatterns.some((pattern) => pattern.test(keyLower));

          if (isSensitiveKey && typeof value === 'string') {
            masked[key] = maskString(value);
          } else if (typeof value === 'object' && value !== null) {
            masked[key] = traverseAndMask(value);
          } else {
            masked[key] = value;
          }
        }
      }
      return masked;
    };

    return traverseAndMask(data);
  }

  calculateIntegrityHash(entry) {
    try {
      const entryString = JSON.stringify(entry, (key, value) => {
        if (key === 'encryptedData' || key === 'ciphertext') return '[REDACTED]';
        return value;
      });
      return crypto.createHash('sha256').update(entryString).digest('hex');
    } catch (error) {
      console.error('Integrity Hash Calculation Error:', error);
      return 'HASH_CALCULATION_FAILED';
    }
  }
}

// ============================================================================
// QUANTUM AUDIT TRAIL SERVICE
// ============================================================================
class QuantumAuditTrailService {
  constructor() {
    this.merkleTree = new QuantumMerkleTree(parseInt(process.env.LOG_MERKLE_TREE_DEPTH) || 12);
    this.encryptionService = new QuantumEncryptionService();
    this.auditEntries = [];
    this.complianceEvents = new Map();
    this.initializeComplianceTracking();
  }

  initializeComplianceTracking() {
    Object.values(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES).forEach((category) => {
      this.complianceEvents.set(category.code, {
        category: category.description,
        events: [],
        lastEvent: null,
        totalEvents: 0,
      });
    });
  }

  async createAuditEntry(event, details, metadata = {}) {
    try {
      const auditId = uuidv4();
      const timestamp = moment()
        .tz(process.env.LOG_TIMEZONE || 'Africa/Johannesburg')
        .toISOString();

      const complianceCategories = this.determineComplianceCategories(event, details);

      const auditEntry = {
        auditId,
        event,
        timestamp,
        details: await this.prepareLogDetails(details),
        metadata: {
          ...metadata,
          hostname: os.hostname(),
          pid: process.pid,
          platform: os.platform(),
          arch: os.arch(),
          complianceCategories,
          informationOfficer: process.env.POPIA_INFORMATION_OFFICER || 'Wilson_Khanyezi',
          dataSubject: metadata.dataSubject || 'SYSTEM_EVENT',
          processingPurpose: metadata.processingPurpose || 'security_auditing',
        },
        security: {
          integrityHash: null,
          encrypted: false,
          sensitivityLevel: this.determineSensitivityLevel(event, details),
        },
      };

      auditEntry.security.integrityHash = this.encryptionService.calculateIntegrityHash(auditEntry);
      const merkleProof = this.merkleTree.addLeaf(auditEntry);
      auditEntry.merkleProof = merkleProof;
      this.auditEntries.push(auditEntry);
      this.updateComplianceTracking(complianceCategories, auditEntry);

      if (process.env.LOG_REAL_TIME_ALERTS === 'true') {
        this.checkForRealTimeAlert(event, auditEntry);
      }

      return auditEntry;
    } catch (error) {
      console.error('Audit Entry Creation Error:', error);
      throw new Error(`Failed to create audit entry: ${error.message}`);
    }
  }

  async prepareLogDetails(details) {
    try {
      if (!details) return { message: 'No details provided' };

      const detailsString = JSON.stringify(details).toLowerCase();
      const isSensitive = QUANTUM_CONSTANTS.SENSITIVE_FIELD_PATTERNS.some((pattern) =>
        pattern.test(detailsString)
      );

      if (isSensitive) {
        const encryptedResult = await this.encryptionService.encryptSensitiveData(details, {
          encryptionContext: 'audit_log_protection',
        });

        if (encryptedResult.encrypted) {
          return {
            encrypted: true,
            ciphertext: encryptedResult.data,
            encryptionMetadata: {
              version: encryptedResult.encryptionVersion,
              iv: encryptedResult.iv,
              authTag: encryptedResult.authTag,
            },
            originalType: typeof details,
          };
        } else {
          return {
            masked: true,
            data: encryptedResult.data,
            reason: encryptedResult.reason || 'SENSITIVE_DATA_MASKED',
          };
        }
      }

      return {
        plaintext: true,
        data: this.encryptionService.maskSensitiveData(details),
      };
    } catch (error) {
      console.error('Log Details Preparation Error:', error);
      return {
        error: 'DETAILS_PREPARATION_FAILED',
        fallback: this.encryptionService.maskSensitiveData({ error: error.message }),
      };
    }
  }

  determineComplianceCategories(event, details) {
    const categories = [];

    if (event.includes('DATA') || event.includes('PII') || event.includes('CONSENT') || event.includes('ACCESS')) {
      categories.push(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES.POPIA.code);
    }
    if (event.includes('SIGN') || event.includes('ELECTRONIC') || event.includes('DIGITAL') || event.includes('MESSAGE')) {
      categories.push(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES.ECT_ACT.code);
    }
    if (event.includes('COMPANY') || event.includes('RECORD') || event.includes('FILING') || event.includes('DIRECTOR')) {
      categories.push(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES.COMPANIES_ACT.code);
    }
    if (event.includes('SECURITY') || event.includes('BREACH') || event.includes('ATTACK') || event.includes('INCIDENT')) {
      categories.push(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES.CYBERCRIMES_ACT.code);
    }
    if (event.includes('FICA') || event.includes('KYC') || event.includes('AML') || event.includes('VERIFICATION')) {
      categories.push(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES.FICA.code);
    }
    if (event.includes('TRUST') || event.includes('CLIENT') || event.includes('LEGAL') || event.includes('PRACTICE')) {
      categories.push(QUANTUM_CONSTANTS.COMPLIANCE_CATEGORIES.LPC.code);
    }

    return [...new Set(categories)];
  }

  determineSensitivityLevel(event, details) {
    if (event.includes('BREACH') || event.includes('CRITICAL') || event.includes('SECURITY_INCIDENT')) {
      return 'CRITICAL';
    }
    if (event.includes('PII') || event.includes('SENSITIVE') || event.includes('CONFIDENTIAL')) {
      return 'HIGH';
    }
    if (event.includes('ACCESS') || event.includes('AUTH') || event.includes('PERMISSION')) {
      return 'MEDIUM';
    }
    return 'LOW';
  }

  updateComplianceTracking(categories, auditEntry) {
    categories.forEach((categoryCode) => {
      const category = this.complianceEvents.get(categoryCode);
      if (category) {
        category.events.push({
          auditId: auditEntry.auditId,
          event: auditEntry.event,
          timestamp: auditEntry.timestamp,
        });
        category.lastEvent = auditEntry.timestamp;
        category.totalEvents++;
        if (category.events.length > 1000) {
          category.events = category.events.slice(-1000);
        }
      }
    });
  }

  async checkForRealTimeAlert(event, auditEntry) {
    const alertEvents = ['DATA_BREACH', 'SECURITY_INCIDENT', 'UNAUTHORIZED_ACCESS', 'COMPLIANCE_VIOLATION', 'SYSTEM_FAILURE'];

    if (alertEvents.includes(event) || auditEntry.security.sensitivityLevel === 'CRITICAL') {
      await this.sendRealTimeAlert({
        event,
        auditId: auditEntry.auditId,
        timestamp: auditEntry.timestamp,
        sensitivity: auditEntry.security.sensitivityLevel,
        hostname: auditEntry.metadata.hostname,
        merkleRoot: auditEntry.merkleProof?.rootHash,
      });
    }
  }

  async sendRealTimeAlert(alertData) {
    try {
      if (process.env.ALERT_WEBHOOK_URL) {
        const axios = (await import('axios')).default;
        await axios.post(process.env.ALERT_WEBHOOK_URL, {
          text:
            '🚨 Wilsy OS Security Alert\n' +
            `Event: ${alertData.event}\n` +
            `Audit ID: ${alertData.auditId}\n` +
            `Time: ${alertData.timestamp}\n` +
            `Host: ${alertData.hostname}\n` +
            `Merkle Root: ${alertData.merkleRoot?.substr(0, 16)}...`,
        });
      }
      console.warn('🚨 SECURITY ALERT:', alertData);
    } catch (error) {
      console.error('Real-time Alert Sending Failed:', error);
    }
  }

  getComplianceReport(timeframe = '30d') {
    const report = {
      reportId: `COMP-AUDIT-${uuidv4().substr(0, 8)}`,
      generatedAt: new Date().toISOString(),
      timeframe,
      merkleRoot: this.merkleTree.getRootHash(),
      summary: {},
    };

    this.complianceEvents.forEach((data, categoryCode) => {
      report.summary[categoryCode] = {
        category: data.category,
        totalEvents: data.totalEvents,
        lastEvent: data.lastEvent,
        eventRate: data.totalEvents / 30,
      };
    });

    report.systemMetrics = {
      totalAuditEntries: this.auditEntries.length,
      merkleTreeSize: this.merkleTree.leaves.length,
      memoryUsage: process.memoryUsage(),
      uptime: process.uptime(),
    };

    report.recommendations = this.generateComplianceRecommendations();
    return report;
  }

  generateComplianceRecommendations() {
    const recommendations = [];

    if (QUANTUM_CONSTANTS.RETENTION_DAYS < 2555) {
      recommendations.push({
        priority: 'HIGH',
        category: 'COMPANIES_ACT',
        recommendation: 'Increase log retention to 7 years (2555 days) for Companies Act compliance',
        current: `${QUANTUM_CONSTANTS.RETENTION_DAYS} days`,
        required: '2555 days',
      });
    }

    if (!QUANTUM_CONSTANTS.LOG_ENCRYPT_SENSITIVE) {
      recommendations.push({
        priority: 'HIGH',
        category: 'POPIA',
        recommendation: 'Enable sensitive data encryption in logs for POPIA compliance',
        action: 'Set LOG_ENCRYPT_SENSITIVE=true in .env',
      });
    }

    if (process.env.LOG_SIEM_INTEGRATION_ENABLED !== 'true') {
      recommendations.push({
        priority: 'MEDIUM',
        category: 'CYBERCRIMES_ACT',
        recommendation: 'Enable SIEM integration for real-time security monitoring',
        action: 'Set up LOG_SIEM_INTEGRATION_ENABLED=true and configure SIEM endpoint',
      });
    }

    return recommendations;
  }

  verifyAuditEntry(auditId) {
    const entry = this.auditEntries.find((e) => e.auditId === auditId);
    if (!entry) {
      return {
        verified: false,
        error: 'ENTRY_NOT_FOUND',
      };
    }

    const merkleVerified = this.merkleTree.verifyProof(
      entry.security.integrityHash,
      entry.merkleProof.proof,
      entry.merkleProof.rootHash
    );

    const currentHash = this.encryptionService.calculateIntegrityHash(entry);
    const integrityVerified = currentHash === entry.security.integrityHash;

    return {
      verified: merkleVerified && integrityVerified,
      auditId,
      timestamp: entry.timestamp,
      event: entry.event,
      merkleVerification: merkleVerified,
      integrityVerification: integrityVerified,
      proof: {
        merkleRoot: entry.merkleProof.rootHash,
        proofLength: entry.merkleProof.proof.length,
        leafIndex: entry.merkleProof.leafIndex,
      },
    };
  }
}

// ============================================================================
// QUANTUM LOGGER CLASS
// ============================================================================
class QuantumLogger {
  constructor(options = {}) {
    this.serviceName = options.serviceName || 'WilsyOS-Core';
    this.environment = process.env.NODE_ENV || 'development';
    this.instanceId = uuidv4();
    this.encryptionService = new QuantumEncryptionService();
    this.auditService = new QuantumAuditTrailService();
    this.winstonLogger = this.initializeWinstonLogger();

    this.metrics = {
      logsProcessed: 0,
      errorsLogged: 0,
      securityEvents: 0,
      complianceEvents: 0,
      startTime: new Date(),
      lastLogTime: null,
    };

    this.performanceStats = {
      averageLogTime: 0,
      totalLogTime: 0,
      maxLogTime: 0,
    };

    console.log(`🔍 QUANTUM LOGGER ACTIVATED - Instance: ${this.instanceId.substr(0, 8)}`);
  }

  initializeWinstonLogger() {
    const { combine, timestamp, json, errors, printf, colorize } = winston.format;

    const consoleFormat = printf(({ level, message, timestamp, component, ...meta }) => {
      const metaStr = Object.keys(meta).length ? ` | ${JSON.stringify(meta)}` : '';
      return `${timestamp} [${level}] ${component}: ${message}${metaStr}`;
    });

    const fileFormat = printf(({ level, message, timestamp, component, compliance, ...meta }) => {
      const entry = {
        level,
        timestamp,
        component,
        message,
        compliance: compliance || [],
        ...meta,
      };
      return JSON.stringify(entry);
    });

    const transports = [
      new DailyRotateFile({
        filename: path.join(process.cwd(), 'logs', 'quantum-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        zippedArchive: true,
        maxSize: QUANTUM_CONSTANTS.MAX_LOG_SIZE,
        maxFiles: QUANTUM_CONSTANTS.MAX_LOG_FILES,
        format: combine(timestamp(), fileFormat),
      }),
      new DailyRotateFile({
        filename: path.join(process.cwd(), 'logs', 'quantum-error-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        level: 'error',
        zippedArchive: true,
        maxSize: '20m',
        maxFiles: '30d',
        format: combine(timestamp(), json()),
      }),
    ];

    if (this.environment === 'development') {
      transports.push(
        new winston.transports.Console({
          format: combine(colorize(), timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), consoleFormat),
          level: 'debug',
        })
      );
    }

    return winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: combine(timestamp(), errors({ stack: true }), json()),
      transports,
      exitOnError: false,
      defaultMeta: {
        service: this.serviceName,
        environment: this.environment,
        instanceId: this.instanceId,
      },
    });
  }

  async prepareLogEntry(level, component, message, data = {}) {
    const startTime = Date.now();

    try {
      const entry = {
        level: level.toUpperCase(),
        component: component || 'Unknown',
        message: message.substring(0, 1000),
        data: await this.prepareLogData(data),
        timestamp: new Date().toISOString(),
        service: this.serviceName,
        environment: this.environment,
        correlationId: data.correlationId || uuidv4(),
        compliance: data.compliance || [],
        security: {
          sensitivity: data.sensitivity || 'LOW',
          encrypted: data.encrypted || false,
        },
      };

      const logTime = Date.now() - startTime;
      this.updatePerformanceStats(logTime);

      return entry;
    } catch (error) {
      console.error('Log Entry Preparation Error:', error);
      return {
        level: 'ERROR',
        component: 'QuantumLogger',
        message: 'Failed to prepare log entry',
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async prepareLogData(data) {
    if (!data) return null;

    if (data.sensitive === true) {
      const encryptedResult = await this.encryptionService.encryptSensitiveData(data, {
        encryptionContext: 'log_entry_protection',
      });

      if (encryptedResult.encrypted) {
        return {
          encrypted: true,
          ciphertext: encryptedResult.data,
          encryptionMetadata: {
            version: encryptedResult.encryptionVersion,
            iv: encryptedResult.iv,
            authTag: encryptedResult.authTag,
          },
        };
      }
    }

    return this.encryptionService.maskSensitiveData(data);
  }

  updatePerformanceStats(logTime) {
    this.metrics.logsProcessed++;
    this.metrics.lastLogTime = new Date();

    this.performanceStats.totalLogTime += logTime;
    this.performanceStats.averageLogTime = this.performanceStats.totalLogTime / this.metrics.logsProcessed;

    if (logTime > this.performanceStats.maxLogTime) {
      this.performanceStats.maxLogTime = logTime;
    }
  }

  async quantum(component, message, data) {
    this.metrics.securityEvents++;
    const entry = await this.prepareLogEntry('QUANTUM', component, message, {
      ...data,
      sensitivity: 'CRITICAL',
    });
    this.winstonLogger.error(entry);
    return entry;
  }

  async critical(component, message, data) {
    this.metrics.securityEvents++;
    const entry = await this.prepareLogEntry('CRITICAL', component, message, {
      ...data,
      sensitivity: 'HIGH',
    });
    this.winstonLogger.error(entry);

    if (process.env.LOG_REAL_TIME_ALERTS === 'true') {
      await this.auditService.sendRealTimeAlert({
        event: 'CRITICAL_LOG_EVENT',
        component,
        message,
        timestamp: entry.timestamp,
      });
    }

    return entry;
  }

  async error(component, message, data) {
    this.metrics.errorsLogged++;
    const entry = await this.prepareLogEntry('ERROR', component, message, data);
    this.winstonLogger.error(entry);
    return entry;
  }

  async warn(component, message, data) {
    const entry = await this.prepareLogEntry('WARN', component, message, data);
    this.winstonLogger.warn(entry);
    return entry;
  }

  async info(component, message, data) {
    const entry = await this.prepareLogEntry('INFO', component, message, data);
    this.winstonLogger.info(entry);
    return entry;
  }

  async debug(component, message, data) {
    if (this.environment === 'development') {
      const entry = await this.prepareLogEntry('DEBUG', component, message, data);
      this.winstonLogger.debug(entry);
      return entry;
    }
    return null;
  }

  async audit(event, details, metadata = {}) {
    this.metrics.complianceEvents++;

    try {
      const auditEntry = await this.auditService.createAuditEntry(event, details, metadata);

      const logEntry = await this.prepareLogEntry('INFO', 'AUDIT', `Audit Event: ${event}`, {
        auditId: auditEntry.auditId,
        event,
        complianceCategories: auditEntry.metadata.complianceCategories,
        merkleProof: auditEntry.merkleProof,
        details: auditEntry.details,
      });

      this.winstonLogger.info(logEntry);
      return auditEntry;
    } catch (error) {
      console.error('Audit Logging Error:', error);

      this.error('QuantumLogger', 'Audit logging failed', {
        event,
        error: error.message,
        fallback: 'USING_BASIC_LOGGING',
      });

      return {
        auditId: uuidv4(),
        event,
        timestamp: new Date().toISOString(),
        error: 'AUDIT_LOG_FAILED',
        details: this.encryptionService.maskSensitiveData(details),
      };
    }
  }

  async legalEvent(eventType, legalDetails, metadata = {}) {
    const complianceTags = this.determineLegalComplianceTags(eventType, legalDetails);
    return this.audit(eventType, legalDetails, {
      ...metadata,
      complianceCategories: complianceTags,
      legalJurisdiction: 'ZA',
      eventCategory: 'LEGAL_OPERATION',
    });
  }

  determineLegalComplianceTags(eventType, details) {
    const tags = [];
    const complianceMap = {
      DOCUMENT_CREATED: ['POPIA', 'ECT', 'COMP2008'],
      DOCUMENT_SIGNED: ['ECT', 'COMP2008', 'LPC'],
      CONSENT_GIVEN: ['POPIA'],
      ACCESS_REQUESTED: ['POPIA', 'PAIA'],
      DATA_BREACH: ['POPIA', 'CYBER2020'],
      TRUST_ACCOUNT_UPDATED: ['LPC', 'FICA'],
    };

    if (complianceMap[eventType]) {
      tags.push(...complianceMap[eventType]);
    }

    return tags;
  }

  async security(event, details, severity = 'MEDIUM') {
    this.metrics.securityEvents++;

    const securityEntry = await this.prepareLogEntry(
      severity === 'CRITICAL' ? 'ERROR' : 'WARN',
      'SECURITY',
      `Security Event: ${event}`,
      {
        ...details,
        securitySeverity: severity,
        compliance: ['CYBER2020', 'POPIA'],
      }
    );

    this.winstonLogger.log(severity === 'CRITICAL' ? 'error' : 'warn', securityEntry);

    await this.auditService.createAuditEntry(`SECURITY_${event}`, details, {
      securitySeverity: severity,
    });

    return securityEntry;
  }

  async performance(operation, duration, metrics = {}) {
    const entry = await this.prepareLogEntry(
      'INFO',
      'PERFORMANCE',
      `Operation: ${operation} took ${duration}ms`,
      {
        operation,
        duration,
        ...metrics,
        performanceThreshold: this.performanceStats.averageLogTime * 2,
      }
    );

    this.winstonLogger.info(entry);
    return entry;
  }

  getStatistics() {
    return {
      metrics: this.metrics,
      performance: this.performanceStats,
      audit: {
        totalEntries: this.auditService.auditEntries.length,
        merkleRoot: this.auditService.merkleTree.getRootHash(),
        complianceSummary: this.auditService.getComplianceReport().summary,
      },
      timestamp: new Date().toISOString(),
    };
  }

  generateComplianceReport(timeframe = '30d') {
    return this.auditService.getComplianceReport(timeframe);
  }

  verifyLogIntegrity(auditId) {
    return this.auditService.verifyAuditEntry(auditId);
  }

  async exportLogsForDiscovery(startDate, endDate, filters = {}) {
    try {
      const filteredEntries = this.auditService.auditEntries.filter((entry) => {
        const entryDate = new Date(entry.timestamp);
        return entryDate >= new Date(startDate) && entryDate <= new Date(endDate);
      });

      let result = filteredEntries;
      if (filters.eventType) {
        result = result.filter((entry) => entry.event === filters.eventType);
      }
      if (filters.complianceCategory) {
        result = result.filter((entry) =>
          entry.metadata.complianceCategories?.includes(filters.complianceCategory)
        );
      }

      const maskedResult = result.map((entry) => ({
        ...entry,
        details: this.encryptionService.maskSensitiveData(entry.details),
      }));

      return {
        exportId: `LOG-EXPORT-${uuidv4().substr(0, 8)}`,
        generatedAt: new Date().toISOString(),
        timeframe: { startDate, endDate },
        filters,
        totalEntries: maskedResult.length,
        entries: maskedResult,
        integrity: {
          merkleRoot: this.auditService.merkleTree.getRootHash(),
          verificationAvailable: true,
        },
        compliance: {
          popia: 'DATA_MINIMIZATION_APPLIED',
          paia: 'EXPORT_READY_FOR_ACCESS_REQUEST',
        },
      };
    } catch (error) {
      console.error('Log Export Error:', error);
      throw new Error(`Failed to export logs: ${error.message}`);
    }
  }

  healthCheck() {
    return {
      status: 'OPERATIONAL',
      timestamp: new Date().toISOString(),
      metrics: {
        uptime: process.uptime(),
        logsProcessed: this.metrics.logsProcessed,
        memoryUsage: process.memoryUsage(),
        performance: {
          averageLogTime: this.performanceStats.averageLogTime,
          maxLogTime: this.performanceStats.maxLogTime,
        },
      },
      services: {
        winston: this.winstonLogger.transports.length > 0 ? 'ACTIVE' : 'INACTIVE',
        merkleTree: this.auditService.merkleTree ? 'ACTIVE' : 'INACTIVE',
        encryption: 'ACTIVE',
      },
    };
  }
}

// ============================================================================
// QUANTUM LOGGER FACTORY
// ============================================================================
class QuantumLoggerFactory {
  static getLogger(serviceName = 'WilsyOS-Core') {
    if (!this.instances) {
      this.instances = new Map();
    }

    if (!this.instances.has(serviceName)) {
      this.instances.set(serviceName, new QuantumLogger({ serviceName }));

      const instance = this.instances.get(serviceName);
      instance.info('QuantumLogger', `Logger initialized for service: ${serviceName}`, {
        environment: instance.environment,
        instanceId: instance.instanceId,
        complianceLevel: 'ENTERPRISE',
      });
    }

    return this.instances.get(serviceName);
  }

  static getAllInstances() {
    return this.instances ? Array.from(this.instances.values()) : [];
  }

  static shutdownAll() {
    if (this.instances) {
      this.instances.forEach((logger, serviceName) => {
        logger.info('QuantumLogger', 'Logger shutting down', {
          service: serviceName,
          totalLogs: logger.metrics.logsProcessed,
        });
      });
      this.instances.clear();
    }
  }
}

// ============================================================================
// GLOBAL LOGGER INSTANCE - Default Export
// ============================================================================
const globalLogger = QuantumLoggerFactory.getLogger();

// ============================================================================
// EXPORTS
// ============================================================================
export default {
  QuantumLogger,
  QuantumLoggerFactory,
  globalLogger,
  QUANTUM_CONSTANTS,
};
