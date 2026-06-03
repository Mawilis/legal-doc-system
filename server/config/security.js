/* eslint-disable */
/**
 * ####################################################################################################
 * # WILSY OS - SECURITY ENGINE CONFIGURATION                                                         #
 * # ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/config/security.js                  #
 * ####################################################################################################
 * # EPITOME: BIBLICAL WORTH BILLIONS | OMEGA CRYPTO SPECS                                            #
 * ####################################################################################################
 */

import crypto from 'node:crypto';

const SECURITY_ENGINE = {
  // 🔐 ENCRYPTION: AES-256-GCM (Industry Standard for High-Value Assets)
  encryption: {
    algorithm: 'aes-256-gcm',
    key: process.env.LPC_AUDIT_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex'),
    ivLength: 16,
    saltLength: 64
  },

  // 🎫 TOKEN PROTOCOL: JWT with Automated Rotation
  tokens: {
    accessExpiry: '8h',
    refreshExpiry: '7d',
    issuer: 'WILSY_SOVEREIGN_CA'
  },

  // 🏛️ AUDIT SPECS: Companies Act 2008 Requirements
  compliance: {
    retentionYears: 7,
    forensicLevel: 'DEEP',
    autoArchive: true
  }
};

export default SECURITY_ENGINE;
