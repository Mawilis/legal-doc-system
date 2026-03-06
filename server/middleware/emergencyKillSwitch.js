/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ EMERGENCY KILL SWITCH - WILSY OS CITADEL                                  ║
  ║ Rogue Admin Detection | Auto-lock | Out-of-band Alerts                   ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/emergencyKillSwitch.js
 * VERSION: 1.0.0-CITADEL
 * CREATED: 2026-03-02
 */

import { SuperAdmin } from '../models/SuperAdmin.js';
import auditLogger from '../utils/auditLogger.js';
import logger from '../utils/logger.js';
import crypto from 'crypto';
import fetch from 'node-fetch';

// ============================================================================
// ANOMALY DETECTION CONFIG
// ============================================================================

const ANOMALY_CONFIG = {
  consecutiveSealMismatches: 3,
  geoFenceViolations: 2,
  timeFenceViolations: 3,
  failedHardwareAuth: 5,
  suspiciousIpChanges: 2,
  outOfBandAlertChannels: ['signal', 'telegram', 'email']
};

// ============================================================================
// ANOMALY DETECTOR
// ============================================================================

class AnomalyDetector {
  constructor() {
    this.violations = new Map();
    this.sealMismatches = new Map();
  }

  async checkForensicSeal(admin, currentHash) {
    const adminId = admin.adminId;
    
    if (!this.sealMismatches.has(adminId)) {
      this.sealMismatches.set(adminId, []);
    }

    const mismatches = this.sealMismatches.get(adminId);
    
    if (currentHash !== admin.forensicHash) {
      mismatches.push({
        timestamp: new Date(),
        expected: admin.forensicHash,
        received: currentHash
      });

      // Trim to last 5 mismatches
      if (mismatches.length > 5) {
        mismatches.shift();
      }

      if (mismatches.length >= ANOMALY_CONFIG.consecutiveSealMismatches) {
        await this.triggerEmergencyLock(admin, 'CONSECUTIVE_SEAL_MISMATCH', {
          mismatches: mismatches.slice(-3)
        });
        return false;
      }
    } else {
      // Reset on successful match
      this.sealMismatches.set(adminId, []);
    }

    return true;
  }

  async checkGeoFencing(admin, request) {
    const adminId = admin.adminId;
    const geoLocation = await this.getGeoLocation(request.ip);

    if (!admin.checkGeoFencing(request.ip, geoLocation)) {
      await this.recordViolation(adminId, 'GEO_FENCE', {
        ip: request.ip,
        location: geoLocation,
        allowed: admin.geoFencing.allowedCountries
      });

      const violations = this.getViolationCount(adminId, 'GEO_FENCE');
      if (violations >= ANOMALY_CONFIG.geoFenceViolations) {
        await this.triggerEmergencyLock(admin, 'GEO_FENCE_VIOLATION', {
          violations,
          lastViolation: geoLocation
        });
        return false;
      }
    }

    return true;
  }

  async checkTimeFencing(admin) {
    const adminId = admin.adminId;

    if (!admin.checkTimeFencing()) {
      await this.recordViolation(adminId, 'TIME_FENCE', {
        time: new Date().toISOString(),
        allowed: `${admin.timeFencing.allowedStartHour}-${admin.timeFencing.allowedEndHour}`
      });

      const violations = this.getViolationCount(adminId, 'TIME_FENCE');
      if (violations >= ANOMALY_CONFIG.timeFenceViolations) {
        await this.triggerEmergencyLock(admin, 'TIME_FENCE_VIOLATION', {
          violations
        });
        return false;
      }
    }

    return true;
  }

  async checkHardwareAuth(admin, keyId, success) {
    const adminId = admin.adminId;

    if (!success) {
      await this.recordViolation(adminId, 'HARDWARE_AUTH', {
        keyId,
        timestamp: new Date()
      });

      const violations = this.getViolationCount(adminId, 'HARDWARE_AUTH');
      if (violations >= ANOMALY_CONFIG.failedHardwareAuth) {
        await this.triggerEmergencyLock(admin, 'HARDWARE_AUTH_FAILED', {
          violations,
          lastKeyId: keyId
        });
        return false;
      }
    }

    return true;
  }

  async recordViolation(adminId, type, data) {
    const key = `${adminId}:${type}`;
    
    if (!this.violations.has(key)) {
      this.violations.set(key, []);
    }

    const violations = this.violations.get(key);
    violations.push({
      timestamp: new Date(),
      ...data
    });

    // Keep last 10 violations
    if (violations.length > 10) {
      violations.shift();
    }

    await auditLogger.log({
      action: 'ADMIN_VIOLATION',
      adminId,
      violationType: type,
      data
    });
  }

  getViolationCount(adminId, type) {
    const key = `${adminId}:${type}`;
    const violations = this.violations.get(key) || [];
    return violations.length;
  }

  async triggerEmergencyLock(admin, reason, details) {
    logger.error('🚨 EMERGENCY LOCK TRIGGERED', {
      adminId: admin.adminId,
      reason,
      details
    });

    // Update admin status
    admin.status = 'locked';
    admin.killSwitch = {
      triggeredAt: new Date(),
      triggeredBy: 'system',
      reason: `${reason}: ${JSON.stringify(details)}`
    };

    // Add to forensic chain
    admin.addToForensicChain('EMERGENCY_LOCK', {
      reason,
      details
    });

    await admin.save();

    // Purge all sessions
    await this.purgeAdminSessions(admin.adminId);

    // Send out-of-band alerts
    await this.sendOutOfBandAlerts(admin, reason, details);

    await auditLogger.log({
      action: 'EMERGENCY_LOCK',
      adminId: admin.adminId,
      reason,
      details
    });
  }

  async purgeAdminSessions(adminId) {
    // In production: Redis session purge
    logger.info('Purging admin sessions', { adminId });
    
    // Simulate session purge
    return true;
  }

  async sendOutOfBandAlerts(admin, reason, details) {
    const alertMessage = `
🚨 WILSY OS EMERGENCY ALERT 🚨
Admin: ${admin.adminId}
Reason: ${reason}
Details: ${JSON.stringify(details)}
Time: ${new Date().toISOString()}
    `.trim();

    // Signal alert (in production)
    if (process.env.SIGNAL_NUMBER) {
      try {
        await fetch('https://api.signal.org/v1/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            number: process.env.SIGNAL_NUMBER,
            message: alertMessage
          })
        });
      } catch (error) {
        logger.error('Signal alert failed', { error: error.message });
      }
    }

    // Telegram alert
    if (process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID) {
      try {
        await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: process.env.TELEGRAM_CHAT_ID,
            text: alertMessage,
            parse_mode: 'Markdown'
          })
        });
      } catch (error) {
        logger.error('Telegram alert failed', { error: error.message });
      }
    }

    // Email alert (in production)
    console.log('📧 OOB ALERT:', alertMessage);
  }

  async getGeoLocation(ip) {
    // In production: Call geolocation API
    return {
      country: 'ZA',
      city: 'Johannesburg',
      coordinates: '-26.195246,28.034088'
    };
  }
}

// ============================================================================
// KILL SWITCH MIDDLEWARE
// ============================================================================

export const anomalyDetector = new AnomalyDetector();

export const emergencyKillSwitch = {
  async checkRequest(req, admin) {
    if (!admin) return true;

    // Check geo-fencing
    const geoPass = await anomalyDetector.checkGeoFencing(admin, req);
    if (!geoPass) return false;

    // Check time-fencing
    const timePass = await anomalyDetector.checkTimeFencing(admin);
    if (!timePass) return false;

    return true;
  },

  async checkForensicSeal(admin, currentHash) {
    return await anomalyDetector.checkForensicSeal(admin, currentHash);
  },

  async recordHardwareAuth(adminId, keyId, success) {
    const admin = await SuperAdmin.findOne({ adminId });
    if (admin) {
      await anomalyDetector.checkHardwareAuth(admin, keyId, success);
    }
  },

  async purgeAdminSessions(adminId) {
    await anomalyDetector.purgeAdminSessions(adminId);
  },

  getViolations(adminId) {
    const violations = [];
    for (const [key, value] of anomalyDetector.violations) {
      if (key.startsWith(`${adminId}:`)) {
        violations.push({
          type: key.split(':')[1],
          records: value
        });
      }
    }
    return violations;
  }
};

// ============================================================================
// KILL SWITCH MIDDLEWARE
// ============================================================================

export const killSwitchMiddleware = (req, res, next) => {
  // Attach kill switch to request for admin routes
  req.killSwitch = emergencyKillSwitch;
  next();
};

// ============================================================================
// AUTOMATIC KILL SWITCH DETECTOR (Runs every minute)
// ============================================================================

export const startKillSwitchMonitor = () => {
  setInterval(async () => {
    try {
      const admins = await SuperAdmin.find({ status: 'active' });
      
      for (const admin of admins) {
        // Check for forensic seal mismatches from logs
        const sealCheck = await anomalyDetector.checkForensicSeal(
          admin, 
          admin.forensicHash // Would check against computed hash
        );

        if (!sealCheck) {
          logger.warn('Auto-kill switch triggered', { adminId: admin.adminId });
        }
      }
    } catch (error) {
      logger.error('Kill switch monitor error', { error: error.message });
    }
  }, 60000); // Every minute
};

export default emergencyKillSwitch;
