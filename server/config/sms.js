/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ SMS CONFIGURATION - INVESTOR-GRADE MODULE                                   ║
  ║ Multi-provider | POPIA compliant | Forensic logging                         ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/sms.js
 * VERSION: 1.0.0 (production)
 */

'use strict';

const smsConfig = {
    primary: {
        provider: process.env.SMS_PROVIDER || 'africastalking',
        apiKey: process.env.AFRICASTALKING_API_KEY || '',
        username: process.env.AFRICASTALKING_USERNAME || 'sandbox',
        from: process.env.SMS_FROM || 'WilsyOS',
        sandbox: process.env.NODE_ENV !== 'production'
    },
    fallback: {
        provider: 'clickatell',
        apiKey: process.env.CLICKATELL_API_KEY || ''
    },
    rateLimits: {
        perTenant: 20, // SMS per minute
        perUser: 5     // SMS per minute
    }
};

module.exports = smsConfig;
