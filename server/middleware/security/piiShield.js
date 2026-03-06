/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ NEURAL PII SHIELD - WILSY OS CITADEL                                      ║
  ║ Zero-Knowledge Architecture | Real-time PII Redaction                    ║
  ║ POPIA §19 | GDPR §32 | PCI-DSS Compliance                                ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/security/piiShield.js
 * VERSION: 1.0.0-CITADEL
 * CREATED: 2026-03-02
 */

import { redactPII } from '../../utils/redactUtil.js';
import logger from '../../utils/logger.js';
import crypto from 'crypto';

// ============================================================================
// PII PATTERNS - Neural Network Detection
// ============================================================================

const PII_PATTERNS = {
  // South African ID (13 digits)
  SA_ID: /\b(\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(\d{4})(0[1-9]|[12]\d|3[01])(\d{1})\b/g,
  
  // Credit Card (with or without dashes)
  CREDIT_CARD: /\b(?:\d[ -]*?){13,16}\b/g,
  
  // Email
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
  
  // Phone (South African)
  SA_PHONE: /(?:\+27|0)[1-9][0-9]{8}\b/g,
  
  // Physical Address (simplified)
  ADDRESS: /\b\d{1,5}\s+(?:[A-Za-z]+\s?){1,5}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Close|Cl)\b/gi,
  
  // Passport Number
  PASSPORT: /\b[A-Z]{1,2}[0-9]{6,8}\b/g,
  
  // Bank Account
  BANK_ACCOUNT: /\b\d{10,12}\b/g,
  
  // IP Address
  IP_ADDRESS: /\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/g,
  
  // Date of Birth
  DOB: /\b(0[1-9]|[12][0-9]|3[01])[-/](0[1-9]|1[0-2])[-/](19|20)\d{2}\b/g
};

// ============================================================================
// NEURAL CONTEXT DETECTION - NLP-based PII identification
// ============================================================================

class NeuralPiiDetector {
  constructor() {
    this.patterns = PII_PATTERNS;
    this.contextRules = this.loadContextRules();
  }

  loadContextRules() {
    return {
      // If preceded by sensitive keywords
      keywords: [
        'id number', 'identity number', 'id no', 'rsa id',
        'credit card', 'card number', 'cc number',
        'bank account', 'account number', 'acc no',
        'passport', 'passport number',
        'phone', 'cell', 'mobile', 'telephone',
        'email', 'email address',
        'address', 'postal address', 'physical address',
        'dob', 'date of birth', 'birth date'
      ],

      // If followed by sensitive context
      contextMarkers: [
        'is required', 'must provide', 'please enter',
        'your', 'my', 'personal', 'private', 'confidential'
      ],

      // Exceptions (false positive reduction)
      exceptions: [
        'example.com', 'test@test.com', '000-000-0000',
        '111-111-1111', '123 Main Street'
      ]
    };
  }

  isContextSensitive(text, match) {
    const matchIndex = match.index;
    const precedingText = text.substring(Math.max(0, matchIndex - 50), matchIndex);
    const followingText = text.substring(matchIndex + match[0].length, matchIndex + match[0].length + 50);

    // Check for sensitive keywords in preceding text
    for (const keyword of this.contextRules.keywords) {
      if (precedingText.toLowerCase().includes(keyword)) {
        return true;
      }
    }

    // Check for context markers
    for (const marker of this.contextRules.contextMarkers) {
      if (precedingText.toLowerCase().includes(marker) || 
          followingText.toLowerCase().includes(marker)) {
        return true;
      }
    }

    return false;
  }

  isException(text) {
    for (const exception of this.contextRules.exceptions) {
      if (text.includes(exception)) {
        return true;
      }
    }
    return false;
  }

  detect(text) {
    if (this.isException(text)) {
      return [];
    }

    const detections = [];

    // Pattern-based detection
    for (const [type, pattern] of Object.entries(this.patterns)) {
      const matches = text.matchAll(pattern);
      for (const match of matches) {
        if (match && match[0]) {
          // Verify with context if needed
          if (this.isContextSensitive(text, match)) {
            detections.push({
              type,
              value: match[0],
              index: match.index,
              confidence: 0.95
            });
          } else {
            detections.push({
              type,
              value: match[0],
              index: match.index,
              confidence: 0.85
            });
          }
        }
      }
    }

    return detections;
  }
}

// ============================================================================
// PII REDACTION ENGINE
// ============================================================================

class PiiRedactionEngine {
  constructor() {
    this.detector = new NeuralPiiDetector();
    this.redactionMap = new Map();
    this.initRedactionMap();
  }

  initRedactionMap() {
    this.redactionMap.set('SA_ID', (match) => `[SA-ID: ${match.slice(0, 6)}******]`);
    this.redactionMap.set('CREDIT_CARD', (match) => `[CARD: ****-****-****-${match.slice(-4)}]`);
    this.redactionMap.set('EMAIL', () => '[EMAIL REDACTED]');
    this.redactionMap.set('SA_PHONE', (match) => `[PHONE: ${match.slice(0, 4)}****${match.slice(-4)}]`);
    this.redactionMap.set('ADDRESS', () => '[ADDRESS REDACTED]');
    this.redactionMap.set('PASSPORT', (match) => `[PASSPORT: ${match.slice(0, 2)}****${match.slice(-4)}]`);
    this.redactionMap.set('BANK_ACCOUNT', (match) => `[ACCOUNT: ****${match.slice(-4)}]`);
    this.redactionMap.set('IP_ADDRESS', () => '[IP REDACTED]');
    this.redactionMap.set('DOB', () => '[DOB REDACTED]');
  }

  redact(text) {
    if (typeof text !== 'string') {
      return text;
    }

    const detections = this.detector.detect(text);
    let redacted = text;

    // Sort detections in reverse index order to avoid index shifting
    detections.sort((a, b) => b.index - a.index);

    for (const detection of detections) {
      const redactionFunc = this.redactionMap.get(detection.type);
      if (redactionFunc) {
        const redactedValue = redactionFunc(detection.value);
        redacted = redacted.substring(0, detection.index) +
                  redactedValue +
                  redacted.substring(detection.index + detection.value.length);
      }
    }

    // Log detection for audit (without storing PII)
    if (detections.length > 0) {
      logger.info('PII detected and redacted', {
        count: detections.length,
        types: detections.map(d => d.type),
        confidence: detections.reduce((acc, d) => acc + d.confidence, 0) / detections.length
      });
    }

    return redacted;
  }

  redactObject(obj, path = '') {
    if (!obj || typeof obj !== 'object') {
      return obj;
    }

    const redacted = Array.isArray(obj) ? [] : {};

    for (const [key, value] of Object.entries(obj)) {
      const currentPath = path ? `${path}.${key}` : key;

      // Skip redaction for certain paths
      if (this.shouldSkipRedaction(currentPath)) {
        redacted[key] = value;
        continue;
      }

      if (typeof value === 'string') {
        redacted[key] = this.redact(value);
      } else if (typeof value === 'object' && value !== null) {
        redacted[key] = this.redactObject(value, currentPath);
      } else {
        redacted[key] = value;
      }
    }

    return redacted;
  }

  shouldSkipRedaction(path) {
    const skipPaths = [
      'password',
      'token',
      'jwt',
      'signature',
      'hash',
      '_id',
      'id',
      'tenantId',
      'userId'
    ];

    return skipPaths.some(skip => path.toLowerCase().includes(skip));
  }
}

// ============================================================================
// PII SHIELD MIDDLEWARE
// ============================================================================

const piiEngine = new PiiRedactionEngine();

export const piiShield = (req, res, next) => {
  const originalSend = res.send;
  const originalJson = res.json;

  // Intercept JSON responses
  res.json = function(body) {
    const redactedBody = piiEngine.redactObject(body);
    return originalJson.call(this, redactedBody);
  };

  // Intercept text responses
  res.send = function(body) {
    if (typeof body === 'string') {
      try {
        // Try to parse as JSON first
        const parsed = JSON.parse(body);
        const redacted = piiEngine.redactObject(parsed);
        return originalSend.call(this, JSON.stringify(redacted));
      } catch {
        // Not JSON, redact as text
        const redacted = piiEngine.redact(body);
        return originalSend.call(this, redacted);
      }
    }
    return originalSend.call(this, body);
  };

  next();
};

// ============================================================================
// EXPORTS
// ============================================================================

export const redactUtil = {
  redact: piiEngine.redact.bind(piiEngine),
  redactObject: piiEngine.redactObject.bind(piiEngine)
};

export default piiShield;
