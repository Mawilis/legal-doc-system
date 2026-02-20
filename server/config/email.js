/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ EMAIL CONFIGURATION - INVESTOR-GRADE MODULE                                 ║
  ║ Multi-provider support | POPIA compliant | Forensic logging                 ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/email.js
 * VERSION: 2.0.0 (production - cleaned)
 */

'use strict';

const crypto = require('crypto');

// Environment-based configuration with secure defaults
const isProduction = process.env.NODE_ENV === 'production';
const isTest = process.env.NODE_ENV === 'test';

/**
 * Email provider configuration with failover support
 */
const emailConfig = {
    // Primary provider (AWS SES in production, Ethereal in development)
    primary: {
        provider: isProduction ? 'aws-ses' : (isTest ? 'test' : 'ethereal'),
        host: process.env.EMAIL_HOST || (isProduction ? 'email-smtp.af-south-1.amazonaws.com' : 'smtp.ethereal.email'),
        port: parseInt(process.env.EMAIL_PORT, 10) || (isProduction ? 587 : 587),
        secure: process.env.EMAIL_SECURE === 'true' || false,
        auth: {
            user: process.env.EMAIL_USER || (isProduction ? '' : 'wilsy@ethereal.email'),
            pass: process.env.EMAIL_PASS || (isProduction ? '' : 'wilsy-test-pass-2026')
        },
        pool: true,
        maxConnections: 5,
        maxMessages: 100,
        rateDelta: 1000,
        rateLimit: 10,
        socketTimeout: 30000,
        connectionTimeout: 30000
    },
    
    // Fallback provider (SendGrid as backup)
    fallback: {
        provider: 'sendgrid',
        apiKey: process.env.SENDGRID_API_KEY || '',
        host: 'smtp.sendgrid.net',
        port: 587,
        secure: false,
        auth: {
            user: 'apikey',
            pass: process.env.SENDGRID_API_KEY || ''
        },
        pool: true,
        maxConnections: 3,
        rateLimit: 5
    },
    
    // Test provider (for CI/CD and local testing)
    test: {
        provider: 'test',
        host: 'smtp.ethereal.email',
        port: 587,
        secure: false,
        auth: {
            user: 'wilsy.test@ethereal.email',
            pass: 'test-pass-2026'
        },
        pool: false
    }
};

/**
 * Default email templates with POPIA-compliant footers
 */
const emailTemplates = {
    paiaRequestConfirmation: {
        subject: 'PAIA Request Confirmation - {{caseNumber}}',
        template: 'paia-request-confirmation',
        footer: 'This communication contains confidential information. If you are not the intended recipient, please notify us immediately. POPIA compliance assured.',
        retentionDays: 365
    },
    paiaResponse: {
        subject: 'Response to PAIA Request - {{caseNumber}}',
        template: 'paia-response',
        footer: 'This response is sent in compliance with PAIA Section 25. Records retained for 5 years.',
        retentionDays: 1825
    },
    annualReturnReminder: {
        subject: 'Annual Return Filing Reminder - {{companyName}}',
        template: 'annual-return-reminder',
        footer: 'Companies Act Section 33 requires annual returns within 12 months of financial year end.',
        retentionDays: 2555
    },
    directorValidation: {
        subject: 'Director Information Validation Required',
        template: 'director-validation',
        footer: 'FICA compliance requires validation of director information. POPIA protected.',
        retentionDays: 1825
    },
    securityAlert: {
        subject: 'Security Alert - Wilsy OS Access',
        template: 'security-alert',
        footer: 'If you did not authorize this access, please contact your system administrator immediately.',
        retentionDays: 365
    }
};

/**
 * POPIA-compliant email footer
 */
const getPopiaFooter = (tenantId = 'SYSTEM') => {
    return `
---
This communication is protected by POPIA (Protection of Personal Information Act, 2013).
Wilsy OS - Legal Document Management System
Tenant: ${tenantId}
Timestamp: ${new Date().toISOString()}
Reference: ${crypto.randomBytes(4).toString('hex').toUpperCase()}
`;
};

/**
 * Email sending options with forensic tracking
 */
const defaultOptions = {
    from: process.env.EMAIL_FROM || 'noreply@wilsyos.co.za',
    replyTo: process.env.EMAIL_REPLY_TO || 'support@wilsyos.co.za',
    headers: {
        'X-Wilsy-Version': '6.0.0',
        'X-POPIA-Compliant': 'true',
        'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN'
    },
    tracking: {
        enabled: true,
        openTracking: true,
        clickTracking: true,
        unsubscribeTracking: true
    }
};

/**
 * Rate limiting configuration per tenant
 */
const rateLimits = {
    perTenant: {
        maxEmailsPerMinute: 60,
        maxEmailsPerHour: 1000,
        maxRecipientsPerEmail: 50
    },
    perUser: {
        maxEmailsPerMinute: 10,
        maxEmailsPerHour: 200
    }
};

/**
 * DKIM signing configuration for email authentication
 */
const dkimConfig = {
    domainName: process.env.DKIM_DOMAIN || 'wilsyos.co.za',
    keySelector: process.env.DKIM_SELECTOR || 'wilsy2026',
    privateKey: process.env.DKIM_PRIVATE_KEY || '',
    headerFields: ['from', 'to', 'subject', 'date', 'message-id']
};

/**
 * Health check configuration
 */
const healthCheck = {
    enabled: true,
    interval: 300000,
    recipients: process.env.HEALTH_CHECK_RECIPIENTS ? 
        process.env.HEALTH_CHECK_RECIPIENTS.split(',') : 
        ['admin@wilsyos.co.za'],
    subject: 'Wilsy OS Email Service Health Check'
};

/**
 * Queue configuration for background email processing
 */
const queueConfig = {
    enabled: true,
    concurrency: 5,
    maxRetries: 3,
    retryDelay: 60000,
    deadLetterQueue: true,
    priority: {
        high: 1,
        normal: 2,
        low: 3
    }
};

/**
 * Attachment configuration with security limits
 */
const attachmentConfig = {
    maxSize: 10 * 1024 * 1024,
    allowedTypes: [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ],
    virusScan: isProduction,
    encrypt: isProduction
};

/**
 * Logging configuration for forensic audit
 */
const loggingConfig = {
    level: isProduction ? 'info' : 'debug',
    auditEvents: [
        'EMAIL_SENT',
        'EMAIL_DELIVERED',
        'EMAIL_OPENED',
        'EMAIL_CLICKED',
        'EMAIL_BOUNCED',
        'EMAIL_COMPLAINT',
        'EMAIL_FAILED'
    ],
    retentionDays: 2555,
    includeHeaders: !isProduction,
    includeBody: false
};

module.exports = {
    emailConfig,
    emailTemplates,
    getPopiaFooter,
    defaultOptions,
    rateLimits,
    dkimConfig,
    healthCheck,
    queueConfig,
    attachmentConfig,
    loggingConfig
};
