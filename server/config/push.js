/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PUSH NOTIFICATION CONFIGURATION [V33.40.1-OMEGA-HERALD]                                                                     ║
 * ║ [FIREBASE | ONESIGNAL | FORENSIC RATE LIMITING | BILLION DOLLAR SPEC]                                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 33.40.1-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/push.js                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-trust provider logic and forensic rate limits. [2026-05-04]                     ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Integrated Service Account and OneSignal shards for multi-region failover.             ║
 * ║ • AI Engineering (Gemini) - ENHANCED: Hardened provider matrix for institutional-grade device reach.                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import dotenv from 'dotenv';
dotenv.config();

/**
 * 🛡️ PUSH CONFIGURATION MATRIX
 * Provisions multi-provider support for global device reach.
 */
export const pushConfig = {
  // 🛰️ SOVEREIGN TOGGLE: Resolves to 'firebase' if PUSH_PROVIDER is not set in .env
  provider: process.env.PUSH_PROVIDER || 'firebase',

  // 🛡️ FIREBASE CLOUD MESSAGING (FCM) - ANCHORED TO PROD DASHBOARD
  firebase: {
    apiKey: process.env.FCM_API_KEY || '',
    projectId: process.env.FCM_PROJECT_ID || '',
    senderId: process.env.FCM_SENDER_ID || '',
    serviceAccount: process.env.FIREBASE_SERVICE_ACCOUNT || '', // JSON master key
    databaseURL: process.env.FIREBASE_DATABASE_URL || '',       // DB transport URL
  },

  // 🛡️ ONESIGNAL - SECONDARY DISPATCH SHARD
  onesignal: {
    appId: process.env.ONESIGNAL_APP_ID || '',
    apiKey: process.env.ONESIGNAL_API_KEY || '',
  },

  /**
   * ⚖️ FORENSIC RATE LIMITS
   * Governs throughput to prevent notification flooding across institutional shards.
   */
  rateLimits: {
    perTenant: 500,
    perUser: 50,
  },
};

export default pushConfig;
