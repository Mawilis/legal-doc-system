/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ PUSH NOTIFICATION CONFIGURATION - INVESTOR-GRADE MODULE                     ║
  ║ Firebase | OneSignal | Forensic logging                                     ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/push.js
 * VERSION: 1.0.0 (production)
 */

'use strict';

const pushConfig = {
    provider: process.env.PUSH_PROVIDER || 'firebase',
    firebase: {
        serviceAccount: process.env.FIREBASE_SERVICE_ACCOUNT || '',
        databaseURL: process.env.FIREBASE_DATABASE_URL || ''
    },
    onesignal: {
        appId: process.env.ONESIGNAL_APP_ID || '',
        apiKey: process.env.ONESIGNAL_API_KEY || ''
    },
    rateLimits: {
        perTenant: 500,
        perUser: 50
    }
};

module.exports = pushConfig;
