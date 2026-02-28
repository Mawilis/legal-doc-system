/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS: ADMIN THREAT ROUTES - THE WAR ROOM API                                      ║
  ║ Real-time threat intelligence endpoints for CISO and investors                        ║
  ║ Protected by Super Admin Guard - Only Wilson can see this                             ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/admin/threatRoutes.js
 * VERSION: 1.0.0-WARROOM
 * CREATED: 2026-02-26
 * 
 * PURPOSE: Real-time security dashboard API for $5B+ infrastructure
 * ACCESS: Super Admin only (Wilson Khanyezi)
 * DATA: Live from Global Threat Intelligence, Sentinel, Kill-Switch
 */

import express from "express";
import GlobalThreatIntel from '../../services/analytics/GlobalThreatIntel.js';
import SecurityOrchestrator from '../../services/security/SecurityOrchestrator.js';
import { superAdminGuard } from '../../middleware/superAdminGuard.js';
import { auditLogger } from '../../utils/auditLogger.js';
import loggerRaw from '../../utils/logger.js';
const logger = loggerRaw.default || loggerRaw;
import { redisClient } from '../../utils/redisClient.js';
import SecurityLog from '../../models/securityLogModel.js';

const router = express.Router();

// ============================================================================
// THREAT INTELLIGENCE ENDPOINTS
// ============================================================================

/**
 * @route   GET /api/v1/admin/threat/posture
 * @desc    Get real-time global security status (Primary War Room endpoint)
 * @access  Super Admin only
 */
router.get('/threat/posture', superAdminGuard, async (req, res) => {
  const startTime = Date.now();
  const correlationId = req.headers['x-correlation-id'] || `warroom-${Date.now()}`;

  try {
    const posture = await GlobalThreatIntel.getSystemPosture();

    // Log access for forensic audit
    await auditLogger.logAction('SYSTEM', 'ADMIN', 'WARROOM_ACCESSED', req.user?.id, {
      correlationId,
      responseTimeMs: Date.now() - startTime,
      threatLevel: posture.threatLevel,
      ip: req.ip
    });

    logger.info('War Room accessed', {
      user: req.user?.email,
      threatLevel: posture.threatLevel,
      responseTimeMs: Date.now() - startTime
    });

    res.json({
      success: true,
      correlationId,
      responseTimeMs: Date.now() - startTime,
      data: posture
    });

  } catch (error) {
    logger.error('War Room endpoint failed', { 
      error: error.message,
      correlationId 
    });

    res.status(500).json({
      success: false,
      correlationId,
      error: 'GTI_SERVICE_OFFLINE',
      message: 'Global Threat Intelligence temporarily unavailable',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @route   GET /api/v1/admin/threat/history
 * @desc    Get historical threat data for trends analysis
 * @access  Super Admin only
 */
router.get('/threat/history', superAdminGuard, async (req, res) => {
  const { hours = 24 } = req.query;

  try {
    const history = GlobalThreatIntel.getThreatHistory(parseInt(hours));

    res.json({
      success: true,
      data: history,
      meta: {
        hours: parseInt(hours),
        points: history.length,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   GET /api/v1/admin/threat/feed
 * @desc    Get real-time threat feed (live events)
 * @access  Super Admin only
 */
router.get('/threat/feed', superAdminGuard, async (req, res) => {
  const { limit = 100 } = req.query;

  try {
    const feed = await GlobalThreatIntel.getThreatFeed(parseInt(limit));

    res.json({
      success: true,
      data: feed,
      meta: {
        count: feed.length,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   GET /api/v1/admin/threat/heatmap
 * @desc    Get threat heatmap by region
 * @access  Super Admin only
 */
router.get('/threat/heatmap', superAdminGuard, async (req, res) => {
  try {
    const heatmap = await GlobalThreatIntel.getRegionalHeatmap();

    res.json({
      success: true,
      data: heatmap,
      meta: {
        regions: heatmap.length,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   GET /api/v1/admin/threat/quarantines
 * @desc    Get all quarantined tenants
 * @access  Super Admin only
 */
router.get('/threat/quarantines', superAdminGuard, async (req, res) => {
  try {
    const quarantineKeys = await redisClient.keys('quarantine:*');
    const quarantines = await Promise.all(
      quarantineKeys.map(async (key) => {
        const tenantId = key.replace('quarantine:', '');
        const data = await redisClient.get(key);
        return {
          tenantId,
          ...JSON.parse(data || '{}')
        };
      })
    );

    res.json({
      success: true,
      data: quarantines,
      meta: {
        count: quarantines.length,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   POST /api/v1/admin/threat/quarantine/:tenantId
 * @desc    Manually quarantine a tenant (nuclear option)
 * @access  Super Admin only
 */
router.post('/threat/quarantine/:tenantId', superAdminGuard, async (req, res) => {
  const { tenantId } = req.params;
  const { reason = 'ADMIN_ACTION', ttl } = req.body;

  try {
    const result = await SecurityOrchestrator.tripCircuitBreaker(
      tenantId,
      reason,
      { ttl, adminId: req.user?.id }
    );

    res.json({
      success: true,
      data: result,
      message: `Tenant ${tenantId} quarantined successfully`
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   DELETE /api/v1/admin/threat/quarantine/:tenantId
 * @desc    Release tenant from quarantine
 * @access  Super Admin only
 */
router.delete('/threat/quarantine/:tenantId', superAdminGuard, async (req, res) => {
  const { tenantId } = req.params;

  try {
    const result = await SecurityOrchestrator.resetCircuitBreaker(
      tenantId,
      'ADMIN_RESTORATION'
    );

    res.json({
      success: true,
      data: result,
      message: `Tenant ${tenantId} released from quarantine`
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   GET /api/v1/admin/threat/stats
 * @desc    Get comprehensive threat statistics
 * @access  Super Admin only
 */
router.get('/threat/stats', superAdminGuard, async (req, res) => {
  try {
    const oneDayAgo = new Date(Date.now() - 24 * 3600000);
    const oneWeekAgo = new Date(Date.now() - 7 * 24 * 3600000);

    const stats = {
      daily: {
        events: await SecurityLog.countDocuments({ timestamp: { $gte: oneDayAgo } }),
        critical: await SecurityLog.countDocuments({ 
          timestamp: { $gte: oneDayAgo },
          severity: 'critical'
        }),
        quarantines: await SecurityLog.countDocuments({
          timestamp: { $gte: oneDayAgo },
          eventType: 'TENANT_QUARANTINE_TRIPPED'
        })
      },
      weekly: {
        events: await SecurityLog.countDocuments({ timestamp: { $gte: oneWeekAgo } }),
        critical: await SecurityLog.countDocuments({ 
          timestamp: { $gte: oneWeekAgo },
          severity: 'critical'
        }),
        quarantines: await SecurityLog.countDocuments({
          timestamp: { $gte: oneWeekAgo },
          eventType: 'TENANT_QUARANTINE_TRIPPED'
        })
      },
      topEvents: await SecurityLog.aggregate([
        { $match: { timestamp: { $gte: oneWeekAgo } } },
        { $group: { _id: '$eventType', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ])
    };

    res.json({
      success: true,
      data: stats,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * @route   GET /api/v1/admin/threat/health
 * @desc    Get health status of all security components
 * @access  Super Admin only
 */
router.get('/threat/health', superAdminGuard, async (req, res) => {
  try {
    const health = {
      sentinel: await GlobalThreatIntel.checkSentinelHealth(),
      killSwitch: await GlobalThreatIntel.checkKillSwitchHealth(),
      quantumLogger: await GlobalThreatIntel.checkQuantumLoggerHealth(),
      redis: await GlobalThreatIntel.checkRedisHealth(),
      timestamp: new Date().toISOString()
    };

    const allHealthy = Object.values(health)
      .filter(h => h.status !== 'unknown')
      .every(h => h.status === 'operational');

    res.json({
      success: true,
      data: health,
      overall: allHealthy ? 'HEALTHY' : 'DEGRADED'
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
