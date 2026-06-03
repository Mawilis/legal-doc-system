/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SECURITY SERVICE                                     ║
 * ║ [THREAT DETECTION | ANOMALY DETECTION | SECURITY MONITORING]             ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Real-time threat detection and prevention
 * - Behavioral analysis and anomaly detection
 * - Security event correlation and alerting
 * - Integration with SIEM systems
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import crypto from 'crypto';
import { promisify } from 'util';

// ============================================================================
// CONFIGURATION
// ============================================================================

const SECURITY_CONFIG = {
  // Threat detection thresholds
  thresholds: {
    failedLoginAttempts: 5,
    failedLoginWindow: 15 * 60 * 1000, // 15 minutes
    passwordResetAttempts: 3,
    passwordResetWindow: 60 * 60 * 1000, // 1 hour
    suspiciousActivityScore: 50,
    highRiskScore: 80
  },

  // Behavioral analysis
  behavioral: {
    enabled: true,
    learningPeriod: 7 * 24 * 60 * 60 * 1000, // 7 days
    maxDeviation: 2.5, // Standard deviations
    minDataPoints: 10
  },

  // IP reputation
  ipReputation: {
    enabled: true,
    cacheTTL: 30 * 60 * 1000, // 30 minutes
    minScore: 30,
    providers: ['abuseipdb', 'virustotal', 'ipqualityscore']
  },

  // Alerting
  alerts: {
    enabled: true,
    severityLevels: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
    notificationChannels: ['email', 'sms', 'webhook', 'slack']
  }
};

// ============================================================================
// SECURITY EVENT STORE
// ============================================================================

class SecurityEventStore {
  constructor() {
    this.events = [];
    this.userBehaviors = new Map();
    this.ipReputations = new Map();
    this.threatIntelligence = new Map();
    this.maxEvents = 10000;
  }

  /**
   * Add security event
   * @param {Object} event - Security event
   */
  addEvent(event) {
    this.events.unshift({
      ...event,
      id: crypto.randomBytes(16).toString('hex'),
      timestamp: new Date().toISOString()
    });

    // Limit store size
    if (this.events.length > this.maxEvents) {
      this.events.pop();
    }
  }

  /**
   * Get recent events
   * @param {Object} filters - Filter criteria
   * @returns {Array} Filtered events
   */
  getEvents(filters = {}) {
    let filtered = [...this.events];

    const {
      type,
      severity,
      userId,
      ip,
      startTime,
      endTime,
      limit = 100
    } = filters;

    if (type) {
      filtered = filtered.filter(e => e.type === type);
    }
    if (severity) {
      filtered = filtered.filter(e => e.severity === severity);
    }
    if (userId) {
      filtered = filtered.filter(e => e.userId === userId);
    }
    if (ip) {
      filtered = filtered.filter(e => e.ip === ip);
    }
    if (startTime) {
      filtered = filtered.filter(e => new Date(e.timestamp) >= new Date(startTime));
    }
    if (endTime) {
      filtered = filtered.filter(e => new Date(e.timestamp) <= new Date(endTime));
    }

    return filtered.slice(0, limit);
  }

  /**
   * Update user behavior profile
   * @param {string} userId - User ID
   * @param {Object} behavior - Behavior data
   */
  updateUserBehavior(userId, behavior) {
    if (!this.userBehaviors.has(userId)) {
      this.userBehaviors.set(userId, {
        firstSeen: new Date().toISOString(),
        events: [],
        patterns: {},
        baseline: null
      });
    }

    const userData = this.userBehaviors.get(userId);
    userData.events.push({
      ...behavior,
      timestamp: new Date().toISOString()
    });

    // Keep only recent events
    const cutoff = Date.now() - SECURITY_CONFIG.behavioral.learningPeriod;
    userData.events = userData.events.filter(e =>
      new Date(e.timestamp).getTime() > cutoff
    );

    // Update baseline after enough data
    if (userData.events.length >= SECURITY_CONFIG.behavioral.minDataPoints) {
      userData.baseline = this.calculateBaseline(userData.events);
    }
  }

  /**
   * Calculate behavioral baseline
   * @param {Array} events - User events
   * @returns {Object} Baseline statistics
   */
  calculateBaseline(events) {
    const times = events.map(e => new Date(e.timestamp).getHours());
    const ips = new Set(events.map(e => e.ip));
    const locations = new Set(events.map(e => e.location).filter(Boolean));
    const devices = new Set(events.map(e => e.deviceFingerprint).filter(Boolean));

    const mean = times.reduce((a, b) => a + b, 0) / times.length;
    const variance = times.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / times.length;
    const stdDev = Math.sqrt(variance);

    return {
      meanAccessTime: mean,
      stdDevAccessTime: stdDev,
      uniqueIPs: ips.size,
      uniqueLocations: locations.size,
      uniqueDevices: devices.size,
      totalEvents: events.length,
      lastUpdated: new Date().toISOString()
    };
  }

  /**
   * Detect anomalies in user behavior
   * @param {string} userId - User ID
   * @param {Object} currentBehavior - Current behavior
   * @returns {Object} Anomaly detection result
   */
  detectAnomalies(userId, currentBehavior) {
    const userData = this.userBehaviors.get(userId);

    if (!userData || !userData.baseline) {
      return {
        hasAnomaly: false,
        reason: 'INSUFFICIENT_DATA'
      };
    }

    const anomalies = [];
    const baseline = userData.baseline;

    // Check access time deviation
    const currentHour = new Date().getHours();
    const timeDeviation = Math.abs(currentHour - baseline.meanAccessTime) / baseline.stdDevAccessTime;

    if (timeDeviation > SECURITY_CONFIG.behavioral.maxDeviation) {
      anomalies.push({
        type: 'UNUSUAL_ACCESS_TIME',
        score: Math.min(100, (timeDeviation / SECURITY_CONFIG.behavioral.maxDeviation) * 100),
        details: {
          currentHour,
          meanHour: baseline.meanAccessTime,
          deviation: timeDeviation
        }
      });
    }

    // Check new IP
    if (currentBehavior.ip && !userData.events.some(e => e.ip === currentBehavior.ip)) {
      anomalies.push({
        type: 'NEW_IP_ADDRESS',
        score: 60,
        details: {
          ip: currentBehavior.ip
        }
      });
    }

    // Check new location
    if (currentBehavior.location && !userData.events.some(e => e.location === currentBehavior.location)) {
      anomalies.push({
        type: 'NEW_LOCATION',
        score: 70,
        details: {
          location: currentBehavior.location
        }
      });
    }

    // Check new device
    if (currentBehavior.deviceFingerprint && !userData.events.some(e => e.deviceFingerprint === currentBehavior.deviceFingerprint)) {
      anomalies.push({
        type: 'NEW_DEVICE',
        score: 50,
        details: {
          deviceId: currentBehavior.deviceFingerprint.substring(0, 16)
        }
      });
    }

    const hasAnomaly = anomalies.length > 0;
    const maxScore = anomalies.reduce((max, a) => Math.max(max, a.score), 0);

    return {
      hasAnomaly,
      anomalies,
      riskScore: maxScore,
      severity: this.getSeverityLevel(maxScore)
    };
  }

  /**
   * Get severity level based on score
   * @param {number} score - Risk score
   * @returns {string} Severity level
   */
  getSeverityLevel(score) {
    if (score >= 80) return 'CRITICAL';
    if (score >= 60) return 'HIGH';
    if (score >= 40) return 'MEDIUM';
    if (score >= 20) return 'LOW';
    return 'INFO';
  }
}

const eventStore = new SecurityEventStore();

// ============================================================================
// THREAT DETECTION
// ============================================================================

/**
 * Detect brute force attacks
 * @param {Object} options - Detection options
 * @returns {Object} Detection result
 */
export const detectBruteForce = (options = {}) => {
  const {
    userId,
    ip,
    action = 'login',
    windowMs = SECURITY_CONFIG.thresholds.failedLoginWindow,
    maxAttempts = SECURITY_CONFIG.thresholds.failedLoginAttempts
  } = options;

  const events = eventStore.getEvents({
    type: 'FAILED_' + action.toUpperCase(),
    userId,
    ip,
    startTime: new Date(Date.now() - windowMs).toISOString()
  });

  const attemptCount = events.length;
  const isAttack = attemptCount >= maxAttempts;

  if (isAttack) {
    eventStore.addEvent({
      type: 'BRUTE_FORCE_DETECTED',
      severity: 'HIGH',
      userId,
      ip,
      metadata: {
        action,
        attemptCount,
        windowMs,
        maxAttempts
      }
    });
  }

  return {
    isAttack,
    attemptCount,
    maxAttempts,
    remainingAttempts: Math.max(0, maxAttempts - attemptCount),
    resetTime: new Date(Date.now() + windowMs).toISOString()
  };
};

/**
 * Detect suspicious patterns
 * @param {Object} options - Detection options
 * @returns {Object} Detection result
 */
export const detectSuspiciousActivity = (options = {}) => {
  const {
    userId,
    ip,
    userAgent,
    deviceFingerprint,
    location
  } = options;

  const events = eventStore.getEvents({
    userId,
    startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // Last 24 hours
  });

  const suspicious = [];
  let riskScore = 0;

  // Check for multiple failed attempts
  const failedAttempts = events.filter(e => e.type?.startsWith('FAILED_')).length;
  if (failedAttempts > 3) {
    suspicious.push({
      type: 'MULTIPLE_FAILED_ATTEMPTS',
      count: failedAttempts
    });
    riskScore += 20;
  }

  // Check for password reset spam
  const passwordResets = events.filter(e => e.type === 'PASSWORD_RESET_REQUESTED').length;
  if (passwordResets > 2) {
    suspicious.push({
      type: 'EXCESSIVE_PASSWORD_RESETS',
      count: passwordResets
    });
    riskScore += 30;
  }

  // Check for rapid location changes (impossible travel)
  const locations = events
    .filter(e => e.location)
    .map(e => ({
      location: e.location,
      time: new Date(e.timestamp).getTime()
    }));

  if (locations.length >= 2) {
    for (let i = 1; i < locations.length; i++) {
      const timeDiff = Math.abs(locations[i].time - locations[i-1].time) / (1000 * 60); // minutes
      if (timeDiff < 30 && locations[i].location !== locations[i-1].location) {
        suspicious.push({
          type: 'IMPOSSIBLE_TRAVEL',
          from: locations[i-1].location,
          to: locations[i].location,
          timeDiffMinutes: timeDiff
        });
        riskScore += 40;
        break;
      }
    }
  }

  // Check for anomalies in user behavior
  if (userId && deviceFingerprint) {
    const anomalies = eventStore.detectAnomalies(userId, {
      ip,
      location,
      deviceFingerprint
    });

    if (anomalies.hasAnomaly) {
      suspicious.push(...anomalies.anomalies);
      riskScore = Math.max(riskScore, anomalies.riskScore);
    }
  }

  return {
    isSuspicious: suspicious.length > 0,
    suspicious,
    riskScore,
    severity: eventStore.getSeverityLevel(riskScore)
  };
};

// ============================================================================
// IP REPUTATION
// ============================================================================

/**
 * Check IP reputation
 * @param {string} ip - IP address
 * @returns {Promise<Object>} Reputation data
 */
export const checkIPReputation = async (ip) => {
  // Check cache
  if (eventStore.ipReputations.has(ip)) {
    const cached = eventStore.ipReputations.get(ip);
    if (Date.now() - cached.timestamp < SECURITY_CONFIG.ipReputation.cacheTTL) {
      return cached.data;
    }
    eventStore.ipReputations.delete(ip);
  }

  // In production, this would call multiple IP reputation services
  // For demo, we'll generate mock data
  const reputation = {
    ip,
    score: Math.floor(Math.random() * 100),
    threats: [],
    categories: [],
    lastReport: new Date().toISOString(),
    reports: Math.floor(Math.random() * 10),
    confidence: 85 + Math.floor(Math.random() * 15)
  };

  // Add random threats for demo
  if (reputation.score < 30) {
    reputation.threats.push('KNOWN_ATTACKER');
    reputation.categories.push('BRUTE_FORCE');
  } else if (reputation.score < 50) {
    reputation.threats.push('SUSPICIOUS_ACTIVITY');
    reputation.categories.push('SCANNER');
  } else if (reputation.score < 70) {
    reputation.threats.push('PROXY_SERVER');
    reputation.categories.push('ANONYMIZER');
  }

  // Cache result
  eventStore.ipReputations.set(ip, {
    data: reputation,
    timestamp: Date.now()
  });

  return reputation;
};

/**
 * Validate IP against threat intelligence
 * @param {string} ip - IP address
 * @returns {Promise<Object>} Validation result
 */
export const validateIP = async (ip) => {
  const reputation = await checkIPReputation(ip);

  const result = {
    valid: reputation.score >= SECURITY_CONFIG.ipReputation.minScore,
    score: reputation.score,
    threats: reputation.threats,
    confidence: reputation.confidence
  };

  if (!result.valid) {
    eventStore.addEvent({
      type: 'SUSPICIOUS_IP_DETECTED',
      severity: 'MEDIUM',
      ip,
      metadata: reputation
    });
  }

  return result;
};

// ============================================================================
// SECURITY EVENT LOGGING
// ============================================================================

/**
 * Log security event
 * @param {Object} event - Security event
 */
export const logSecurityEvent = (event) => {
  eventStore.addEvent(event);

  // Trigger alerts for high severity events
  if (event.severity === 'CRITICAL' || event.severity === 'HIGH') {
    triggerAlert(event);
  }
};

/**
 * Trigger security alert
 * @param {Object} event - Security event
 */
const triggerAlert = async (event) => {
  console.warn('[SECURITY ALERT]', {
    ...event,
    timestamp: new Date().toISOString()
  });

  // In production, this would send notifications via configured channels
  // emailService.sendSecurityAlert(event);
  // smsService.sendSecurityAlert(event);
  // webhookService.trigger(event);
};

// ============================================================================
// THREAT INTELLIGENCE
// ============================================================================

/**
 * Update threat intelligence data
 * @param {Object} data - Threat intelligence data
 */
export const updateThreatIntelligence = (data) => {
  const { type, indicators } = data;

  eventStore.threatIntelligence.set(type, {
    indicators,
    updatedAt: new Date().toISOString()
  });
};

/**
 * Check against threat intelligence
 * @param {string} value - Value to check
 * @param {string} type - Threat type
 * @returns {Object} Check result
 */
export const checkThreatIntelligence = (value, type) => {
  const threatData = eventStore.threatIntelligence.get(type);

  if (!threatData) {
    return {
      matched: false,
      confidence: 0
    };
  }

  const matched = threatData.indicators.some(i => i.value === value);

  return {
    matched,
    confidence: matched ? threatData.indicators.find(i => i.value === value)?.confidence || 0 : 0,
    threatType: type
  };
};

// ============================================================================
// SESSION SECURITY
// ============================================================================

/**
 * Validate session security
 * @param {Object} session - Session object
 * @param {Object} context - Current context
 * @returns {Object} Validation result
 */
export const validateSessionSecurity = async (session, context) => {
  const issues = [];
  let score = 100;

  // Check IP change
  if (session.ipAddress && context.ip && session.ipAddress !== context.ip) {
    const ipReputation = await checkIPReputation(context.ip);
    if (ipReputation.score < 50) {
      issues.push({
        type: 'SUSPICIOUS_IP_CHANGE',
        severity: 'HIGH',
        oldIP: session.ipAddress,
        newIP: context.ip
      });
      score -= 40;
    } else {
      issues.push({
        type: 'IP_ADDRESS_CHANGE',
        severity: 'MEDIUM',
        oldIP: session.ipAddress,
        newIP: context.ip
      });
      score -= 20;
    }
  }

  // Check user agent change
  if (session.userAgent && context.userAgent && session.userAgent !== context.userAgent) {
    issues.push({
      type: 'USER_AGENT_CHANGE',
      severity: 'LOW',
      oldUA: session.userAgent.substring(0, 50),
      newUA: context.userAgent.substring(0, 50)
    });
    score -= 10;
  }

  // Check device fingerprint change
  if (session.deviceFingerprint && context.deviceFingerprint &&
      session.deviceFingerprint !== context.deviceFingerprint) {
    issues.push({
      type: 'DEVICE_FINGERPRINT_CHANGE',
      severity: 'MEDIUM',
      oldDevice: session.deviceFingerprint.substring(0, 16),
      newDevice: context.deviceFingerprint.substring(0, 16)
    });
    score -= 30;
  }

  // Check location change
  if (session.location && context.location && session.location !== context.location) {
    const timeSinceLastActivity = Date.now() - new Date(session.lastActivity).getTime();
    const hoursSinceLastActivity = timeSinceLastActivity / (1000 * 60 * 60);

    if (hoursSinceLastActivity < 2) {
      issues.push({
        type: 'RAPID_LOCATION_CHANGE',
        severity: 'HIGH',
        oldLocation: session.location,
        newLocation: context.location,
        hoursElapsed: hoursSinceLastActivity
      });
      score -= 50;
    } else {
      issues.push({
        type: 'LOCATION_CHANGE',
        severity: 'LOW',
        oldLocation: session.location,
        newLocation: context.location,
        hoursElapsed: hoursSinceLastActivity
      });
      score -= 10;
    }
  }

  return {
    valid: score >= 50,
    score,
    issues,
    severity: eventStore.getSeverityLevel(100 - score)
  };
};

// ============================================================================
// RATE LIMITING
// ============================================================================

const rateLimitStore = new Map();

/**
 * Check rate limit
 * @param {string} key - Rate limit key
 * @param {Object} options - Rate limit options
 * @returns {Object} Rate limit status
 */
export const checkRateLimit = (key, options = {}) => {
  const {
    windowMs = 60 * 1000,
    max = 10,
    blockDuration = 15 * 60 * 1000
  } = options;

  const now = Date.now();
  let data = rateLimitStore.get(key);

  if (!data) {
    data = {
      attempts: [],
      blockedUntil: null
    };
    rateLimitStore.set(key, data);
  }

  // Check if blocked
  if (data.blockedUntil && now < data.blockedUntil) {
    return {
      allowed: false,
      blocked: true,
      retryAfter: Math.ceil((data.blockedUntil - now) / 1000),
      reason: 'RATE_LIMIT_EXCEEDED'
    };
  }

  // Clean up old attempts
  data.attempts = data.attempts.filter(t => now - t < windowMs);

  // Check limit
  if (data.attempts.length >= max) {
    data.blockedUntil = now + blockDuration;
    return {
      allowed: false,
      blocked: true,
      retryAfter: blockDuration / 1000,
      reason: 'RATE_LIMIT_EXCEEDED'
    };
  }

  // Add attempt
  data.attempts.push(now);

  return {
    allowed: true,
    remaining: max - data.attempts.length,
    reset: new Date(now + windowMs).toISOString()
  };
};

// ============================================================================
// SECURITY METRICS
// ============================================================================

/**
 * Get security metrics
 * @returns {Object} Security metrics
 */
export const getSecurityMetrics = () => {
  const now = Date.now();
  const last24h = new Date(now - 24 * 60 * 60 * 1000).toISOString();

  const recentEvents = eventStore.getEvents({
    startTime: last24h
  });

  const criticalEvents = recentEvents.filter(e => e.severity === 'CRITICAL').length;
  const highEvents = recentEvents.filter(e => e.severity === 'HIGH').length;
  const mediumEvents = recentEvents.filter(e => e.severity === 'MEDIUM').length;
  const lowEvents = recentEvents.filter(e => e.severity === 'LOW').length;

  const threatsByType = recentEvents.reduce((acc, e) => {
    if (e.type) {
      acc[e.type] = (acc[e.type] || 0) + 1;
    }
    return acc;
  }, {});

  return {
    totalEvents: recentEvents.length,
    criticalEvents,
    highEvents,
    mediumEvents,
    lowEvents,
    threatsByType,
    topThreats: Object.entries(threatsByType)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([type, count]) => ({ type, count })),
    activeBlocks: rateLimitStore.size,
    ipReputationCache: eventStore.ipReputations.size,
    timestamp: new Date().toISOString()
  };
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  detectBruteForce,
  detectSuspiciousActivity,
  checkIPReputation,
  validateIP,
  logSecurityEvent,
  validateSessionSecurity,
  checkRateLimit,
  getSecurityMetrics,
  updateThreatIntelligence,
  checkThreatIntelligence
};
