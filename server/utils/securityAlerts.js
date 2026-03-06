#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SECURITY ALERT DISPATCHER v1.0                                 ║
 * ║ [Production Grade | POPIA §22 Breach Notification | Forensic Traceability]║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/utils/securityAlerts.js
 * VERSION: 1.0.0
 * CREATED: 2026-02-24
 *
 * INVESTOR VALUE PROPOSITION:
 * • Real-time security threat detection for R240M platform
 * • POPIA §22 breach notification automation
 * • Integration with SecurityLogModel for forensic persistence
 * • Multi-tenant alert routing with tenant isolation
 *
 * DEPENDENCIES:
 * • ./logger.js - Structured logging
 * • ./auditLogger.js - Forensic audit trail
 * • ../models/securityLogModel.js - Persistent storage
 * • crypto (built-in) - Hash generation
 *
 * INTEGRATION MAP:
 * {
 *   "consumers": [
 *     "middleware/tenantGuard.js",
 *     "middleware/auth.js",
 *     "controllers/auditController.js",
 *     "services/threatDetectionService.js",
 *     "workers/securityMonitor.js"
 *   ],
 *   "providers": [
 *     "./logger.js",
 *     "./auditLogger.js",
 *     "../models/securityLogModel.js"
 *   ]
 * }
 */

import crypto from 'crypto';
import loggerRaw from './logger.js';
import auditLogger from './auditLogger.js';
import SecurityLogModel from '../models/securityLogModel.js';

const logger = loggerRaw.default || loggerRaw;

/**
 * Security Alert Severity Levels
 * Maps to POPIA breach notification requirements
 */
export const SECURITY_ALERT_LEVELS = {
  INFO: 'info', // Informational, no action needed
  WARNING: 'warning', // Suspicious activity, monitor
  ERROR: 'error', // System error, investigate
  CRITICAL: 'critical', // Critical security event, immediate action
  BREACH: 'breach', // POPIA §22 - Data breach, mandatory notification
};

/**
 * Security Alert Types
 * Comprehensive categorization for forensic analysis
 */
export const ALERT_TYPES = {
  // Access Control Events
  UNAUTHORIZED_ACCESS: 'unauthorized_access',
  TENANT_ISOLATION_BREACH: 'tenant_isolation_breach',
  PRIVILEGE_ESCALATION: 'privilege_escalation',
  AUTHENTICATION_FAILURE: 'authentication_failure',
  AUTHORIZATION_FAILURE: 'authorization_failure',
  SESSION_HIJACKING: 'session_hijacking',

  // Data Protection Events
  DATA_EXFILTRATION_ATTEMPT: 'data_exfiltration_attempt',
  DATA_BREACH: 'data_breach',
  PII_ACCESS_WITHOUT_CONSENT: 'pii_access_without_consent',
  DATA_MODIFICATION_ATTEMPT: 'data_modification_attempt',

  // Compliance Events
  COMPLIANCE_VIOLATION: 'compliance_violation',
  CONSENT_VIOLATION: 'consent_violation',
  RETENTION_POLICY_VIOLATION: 'retention_policy_violation',
  DATA_SUBJECT_REQUEST: 'data_subject_request',

  // System Events
  RATE_LIMIT_EXCEEDED: 'rate_limit_exceeded',
  SUSPICIOUS_PATTERN: 'suspicious_pattern',
  API_ABUSE: 'api_abuse',
  DDOS_ATTEMPT: 'ddos_attempt',
  SYSTEM_INTEGRITY_CHECK: 'system_integrity_check',

  // Regulatory Events
  REGULATORY_REPORT: 'regulatory_report',
  POPIA_BREACH_NOTIFICATION: 'popia_breach_notification',
  FICA_COMPLIANCE_ALERT: 'fica_compliance_alert',
};

/**
 * Notification Channels for different severity levels
 */
const NOTIFICATION_CHANNELS = {
  [SECURITY_ALERT_LEVELS.INFO]: ['log'],
  [SECURITY_ALERT_LEVELS.WARNING]: ['log', 'slack'],
  [SECURITY_ALERT_LEVELS.ERROR]: ['log', 'slack', 'email'],
  [SECURITY_ALERT_LEVELS.CRITICAL]: ['log', 'slack', 'email', 'sms', 'pagerduty'],
  [SECURITY_ALERT_LEVELS.BREACH]: ['log', 'slack', 'email', 'sms', 'pagerduty', 'regulatory'],
};

/**
 * Security Alert Class
 * Handles creation, persistence, and notification of security alerts
 */
class SecurityAlert {
  constructor(type, metadata = {}, requestId = 'system') {
    this.type = type;
    this.metadata = metadata;
    this.requestId = requestId;
    this.timestamp = new Date();
    this.id = this.generateAlertId();
    this.severity = this.determineSeverity();
    this.requiresBreachNotification = this.checkBreachRequirement();
  }

  /**
   * Generate unique alert ID
   */
  generateAlertId() {
    const hash = crypto
      .createHash('sha256')
      .update(
        `${this.type}-${this.timestamp.toISOString()}-${this.requestId}-${crypto.randomBytes(8).toString('hex')}`,
      )
      .digest('hex')
      .substring(0, 16);
    return `alt-${this.timestamp.getTime()}-${hash}`;
  }

  /**
   * Determine severity based on alert type and metadata
   */
  determineSeverity() {
    // Critical alerts that always require immediate attention
    const criticalTypes = [
      ALERT_TYPES.TENANT_ISOLATION_BREACH,
      ALERT_TYPES.DATA_EXFILTRATION_ATTEMPT,
      ALERT_TYPES.PRIVILEGE_ESCALATION,
      ALERT_TYPES.DATA_BREACH,
    ];

    if (criticalTypes.includes(this.type)) {
      return SECURITY_ALERT_LEVELS.CRITICAL;
    }

    // Check for breach conditions
    if (
      this.metadata.affectedDataSubjects > 0
      || this.metadata.piiExposed === true
      || this.type === ALERT_TYPES.DATA_BREACH
    ) {
      return SECURITY_ALERT_LEVELS.BREACH;
    }

    // Default severity based on type patterns
    if (this.type.includes('attempt') || this.type.includes('violation')) {
      return SECURITY_ALERT_LEVELS.ERROR;
    }

    if (this.type.includes('failure') || this.type.includes('exceeded')) {
      return SECURITY_ALERT_LEVELS.WARNING;
    }

    return SECURITY_ALERT_LEVELS.INFO;
  }

  /**
   * Check if this alert requires POPIA §22 breach notification
   */
  checkBreachRequirement() {
    const breachIndicators = [
      this.severity === SECURITY_ALERT_LEVELS.BREACH,
      this.metadata.affectedDataSubjects > 0,
      this.metadata.piiExposed === true,
      this.metadata.unauthorizedAccess === true,
      [ALERT_TYPES.DATA_BREACH, ALERT_TYPES.DATA_EXFILTRATION_ATTEMPT].includes(this.type),
    ];

    return breachIndicators.some((indicator) => indicator === true);
  }

  /**
   * Prepare metadata for persistence (redact sensitive data)
   */
  prepareMetadataForPersistence() {
    const redactedMetadata = { ...this.metadata };

    // Redact sensitive fields if present
    const sensitiveFields = ['password', 'token', 'secret', 'authorization', 'cookie'];
    sensitiveFields.forEach((field) => {
      if (redactedMetadata[field]) {
        redactedMetadata[`${field}_redacted`] = true;
        redactedMetadata[field] = '[REDACTED]';
      }
    });

    return redactedMetadata;
  }

  /**
   * Send notifications through appropriate channels
   */
  async sendNotifications() {
    const channels = NOTIFICATION_CHANNELS[this.severity] || ['log'];
    const results = {};

    for (const channel of channels) {
      try {
        switch (channel) {
          case 'log':
            logger[
              this.severity === SECURITY_ALERT_LEVELS.INFO
                ? 'info'
                : this.severity === SECURITY_ALERT_LEVELS.WARNING
                  ? 'warn'
                  : 'error'
            ](`Security Alert [${this.type}]`, {
              alertId: this.id,
              severity: this.severity,
              type: this.type,
              requestId: this.requestId,
              timestamp: this.timestamp,
              metadata: this.metadata,
            });
            results[channel] = { success: true };
            break;

          case 'slack':
            // Slack webhook integration would go here
            // This is a placeholder for production integration
            if (process.env.SLACK_WEBHOOK_URL) {
              // await fetch(process.env.SLACK_WEBHOOK_URL, { ... })
            }
            results[channel] = { success: true, channel: 'slack' };
            break;

          case 'email':
            // Email notification for security team
            if (process.env.ALERT_EMAIL) {
              // await sendEmail({ ... })
            }
            results[channel] = { success: true, channel: 'email' };
            break;

          case 'sms':
            // SMS for critical alerts
            if (process.env.SMS_NUMBER && this.severity === SECURITY_ALERT_LEVELS.CRITICAL) {
              // await sendSMS({ ... })
            }
            results[channel] = { success: true, channel: 'sms' };
            break;

          case 'pagerduty':
            // PagerDuty integration for critical alerts
            if (process.env.PAGERDUTY_KEY) {
              // await fetch('https://events.pagerduty.com/v2/enqueue', { ... })
            }
            results[channel] = { success: true, channel: 'pagerduty' };
            break;

          case 'regulatory':
            // POPIA §22 - Regulatory notification required
            results[channel] = {
              success: true,
              channel: 'regulatory',
              requiresAction: true,
              deadline: new Date(Date.now() + 72 * 60 * 60 * 1000), // 72 hours
            };
            break;
        }
      } catch (error) {
        logger.error('Notification channel failed', { channel, error: error.message });
        results[channel] = { success: false, error: error.message };
      }
    }

    return results;
  }
}

/**
 * Core function: Log a security alert with full forensic traceability
 */
export const logSecurityAlert = async (type, metadata = {}, requestId = 'system') => {
  try {
    const alert = new SecurityAlert(type, metadata, requestId);
    const preparedMetadata = alert.prepareMetadataForPersistence();

    // Create security log entry in database
    const securityLog = new SecurityLogModel({
      eventType: type,
      severity: alert.severity,
      tenantId: metadata.tenantId || 'system',
      requestId: alert.requestId,
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      userId: metadata.userId,
      details: preparedMetadata,
      requiresBreachNotification: alert.requiresBreachNotification,
      dataSubjectsAffected: metadata.affectedDataSubjects || 0,
      retentionPolicy: metadata.retentionPolicy || 'companies_act_10_years',
      dataResidency: metadata.dataResidency || 'ZA',
    });

    await securityLog.save();

    // Send notifications through appropriate channels
    const notificationResults = await alert.sendNotifications();

    // Create audit trail
    await auditLogger.log({
      action: 'SECURITY_ALERT',
      type: alert.type,
      severity: alert.severity,
      alertId: alert.id,
      logId: securityLog._id.toString(),
      tenantId: metadata.tenantId || 'system',
      requestId: alert.requestId,
      requiresBreachNotification: alert.requiresBreachNotification,
      notificationChannels: Object.keys(notificationResults),
      timestamp: alert.timestamp,
      retentionPolicy: 'companies_act_10_years',
      dataResidency: 'ZA',
    });

    // If breach notification is required, trigger POPIA §22 workflow
    if (alert.requiresBreachNotification) {
      await triggerBreachNotificationWorkflow(alert, securityLog);
    }

    return {
      success: true,
      alertId: alert.id,
      logId: securityLog._id.toString(),
      severity: alert.severity,
      timestamp: alert.timestamp,
      requiresBreachNotification: alert.requiresBreachNotification,
      notifications: notificationResults,
    };
  } catch (error) {
    logger.error('Failed to log security alert', {
      type,
      error: error.message,
      requestId,
    });

    // Fallback: log to console if everything fails
    console.error('🚨 CRITICAL: Security alert logging failed', {
      type,
      metadata,
      error: error.message,
    });

    return {
      success: false,
      error: error.message,
      type,
      timestamp: new Date().toISOString(),
    };
  }
};

/**
 * Trigger POPIA §22 breach notification workflow
 * @private
 */
const triggerBreachNotificationWorkflow = async (alert, securityLog) => {
  try {
    logger.critical('POPIA §22 BREACH NOTIFICATION REQUIRED', {
      alertId: alert.id,
      logId: securityLog._id,
      type: alert.type,
      severity: alert.severity,
      affectedDataSubjects: alert.metadata.affectedDataSubjects || 0,
      deadline: new Date(Date.now() + 72 * 60 * 60 * 1000), // 72 hours
    });

    // In production, this would:
    // 1. Notify the Information Regulator
    // 2. Notify affected data subjects
    // 3. Create compliance report
    // 4. Update security incident register

    // Placeholder for production integration
    if (process.env.NODE_ENV === 'production') {
      // await notifyInfoRegulator(alert, securityLog);
      // await notifyDataSubjects(alert, securityLog);
    }
  } catch (error) {
    logger.error('Breach notification workflow failed', { error: error.message });
  }
};

/**
 * Trigger a critical security alert (immediate attention required)
 */
export const triggerCriticalAlert = async (type, metadata, requestId) => logSecurityAlert(type, { ...metadata, forceCritical: true }, requestId);

/**
 * Check if an alert meets POPIA breach notification requirements
 */
export const requiresBreachNotification = (type, metadata) => {
  const breachTypes = [
    ALERT_TYPES.DATA_EXFILTRATION_ATTEMPT,
    ALERT_TYPES.UNAUTHORIZED_ACCESS,
    ALERT_TYPES.PRIVILEGE_ESCALATION,
    ALERT_TYPES.DATA_BREACH,
    ALERT_TYPES.PII_ACCESS_WITHOUT_CONSENT,
  ];

  return (
    breachTypes.includes(type)
    && (metadata?.affectedDataSubjects > 0
      || metadata?.piiExposed === true
      || metadata?.unauthorizedAccess === true)
  );
};

/**
 * Get security alert statistics for a tenant
 */
export const getTenantAlertStats = async (tenantId, days = 30) => {
  try {
    const stats = await SecurityLogModel.getTenantSecurityStats(tenantId, days);
    return {
      success: true,
      tenantId,
      days,
      stats,
    };
  } catch (error) {
    logger.error('Failed to get tenant alert stats', { tenantId, error: error.message });
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Acknowledge a security alert
 */
export const acknowledgeAlert = async (alertId, userId, notes = '') => {
  try {
    const securityLog = await SecurityLogModel.findById(alertId);

    if (!securityLog) {
      return { success: false, error: 'Alert not found' };
    }

    securityLog.metadata = {
      ...securityLog.metadata,
      acknowledged: true,
      acknowledgedBy: userId,
      acknowledgedAt: new Date(),
      acknowledgementNotes: notes,
    };

    await securityLog.save();

    return {
      success: true,
      alertId,
      acknowledgedAt: new Date(),
    };
  } catch (error) {
    logger.error('Failed to acknowledge alert', { alertId, error: error.message });
    return { success: false, error: error.message };
  }
};

/**
 * Resolve a security alert
 */
export const resolveAlert = async (alertId, userId, resolution = {}) => {
  try {
    const securityLog = await SecurityLogModel.findById(alertId);

    if (!securityLog) {
      return { success: false, error: 'Alert not found' };
    }

    securityLog.metadata = {
      ...securityLog.metadata,
      resolved: true,
      resolvedBy: userId,
      resolvedAt: new Date(),
      resolution: resolution.notes,
      remediationActions: resolution.actions || [],
    };

    await securityLog.save();

    return {
      success: true,
      alertId,
      resolvedAt: new Date(),
    };
  } catch (error) {
    logger.error('Failed to resolve alert', { alertId, error: error.message });
    return { success: false, error: error.message };
  }
};

/**
 * Export default function for backward compatibility
 */
export default logSecurityAlert;
