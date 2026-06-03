/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ EMAIL CONFIGURATION - INVESTOR-GRADE MODULE                                                                                            ║
 * ║ [RECTIFIED: ES MODULE PARITY | POPIA COMPLIANT | FORENSIC LOGGING]                                                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import dotenv from 'dotenv';

dotenv.config();

const isProduction = process.env.NODE_ENV === 'production';
const isTest = process.env.NODE_ENV === 'test';

export const emailConfig = {
  primary: {
    provider: isProduction ? 'aws-ses' : isTest ? 'test' : 'ethereal',
    host: process.env.EMAIL_HOST || (isProduction ? 'email-smtp.af-south-1.amazonaws.com' : 'smtp.ethereal.email'),
    port: parseInt(process.env.EMAIL_PORT, 10) || 587,
    secure: process.env.EMAIL_SECURE === 'true',
    auth: {
      user: process.env.EMAIL_USER || (isProduction ? '' : 'wilsy@ethereal.email'),
      pass: process.env.EMAIL_PASS || (isProduction ? '' : 'wilsy-test-pass-2026'),
    },
    pool: true,
    maxConnections: 5,
    rateLimit: 10,
    socketTimeout: 30000,
  },
  fallback: {
    provider: 'sendgrid',
    apiKey: process.env.SENDGRID_API_KEY || '',
    host: 'smtp.sendgrid.net',
    port: 587,
    auth: {
      user: 'apikey',
      pass: process.env.SENDGRID_API_KEY || '',
    },
  }
};

export const emailTemplates = {
  paiaRequestConfirmation: {
    subject: 'PAIA Request Confirmation - {{caseNumber}}',
    template: 'paia-request-confirmation',
    footer: 'POPIA compliance assured. Confidential information protected.',
    retentionDays: 365,
  },
  annualReturnReminder: {
    subject: 'Annual Return Filing Reminder - {{companyName}}',
    template: 'annual-return-reminder',
    footer: 'Companies Act Section 33 compliance mandatory.',
    retentionDays: 2555,
  },
  securityAlert: {
    subject: 'Security Alert - Wilsy OS Access',
    template: 'security-alert',
    footer: 'Unauthorized access detected. Contact administrator immediately.',
    retentionDays: 365,
  },
};

export const getPopiaFooter = (tenantId = 'SYSTEM') => `
---
This communication is protected by POPIA (Protection of Personal Information Act, 2013).
Wilsy OS - Legal Document Management System
Tenant: ${tenantId}
Timestamp: ${new Date().toISOString()}
Reference: ${crypto.randomBytes(4).toString('hex').toUpperCase()}
`;

export const defaultOptions = {
  from: process.env.EMAIL_FROM || 'noreply@wilsyos.co.za',
  replyTo: process.env.EMAIL_REPLY_TO || 'support@wilsyos.co.za',
  headers: {
    'X-Wilsy-Version': '33.19.1',
    'X-POPIA-Compliant': 'true',
  }
};

export const loggingConfig = {
  level: isProduction ? 'info' : 'debug',
  auditEvents: ['EMAIL_SENT', 'EMAIL_FAILED', 'EMAIL_BOUNCED'],
  retentionDays: 2555,
};

export default {
  emailConfig,
  emailTemplates,
  getPopiaFooter,
  defaultOptions,
  loggingConfig,
};
