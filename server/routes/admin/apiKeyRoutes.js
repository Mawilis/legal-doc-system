#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ API KEY MANAGEMENT ROUTES - ADMIN INTERFACE                               ║
  ║ Generate keys | Manage tiers | Usage analytics | Billing                  ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

import express from 'express';
import crypto from 'crypto';
import { ApiKey } from '../../models/api/ApiKey.js';
import { generateApiKey } from '../../middleware/api/authMiddleware.js';
import { superAdminGuard } from '../../middleware/superAdminGuard.js';
import { auditMiddleware } from '../../middleware/auditLogger.js';
import loggerRaw from '../../utils/logger.js';

const logger = loggerRaw.default || loggerRaw;

const router = express.Router();

// ============================================================================
// API KEY GENERATION
// ============================================================================

/**
 * Generate new API key for tenant
 * POST /api/admin/keys
 */
router.post(
  '/keys',
  superAdminGuard,
  auditMiddleware({ action: 'API_KEY_GENERATE' }),
  async (req, res) => {
    const correlationId = req.headers['x-correlation-id'] || `admin-${Date.now()}`;

    try {
      const {
        tenantId, tier = 'BASIC', expiresInDays = 365, name, description,
      } = req.body;

      if (!tenantId) {
        return res.status(400).json({
          success: false,
          error: 'TENANT_ID_REQUIRED',
          message: 'tenantId is required',
          correlationId,
        });
      }

      const keyData = await generateApiKey(tenantId, tier, expiresInDays);

      // Add metadata
      const apiKey = await ApiKey.findOneAndUpdate(
        { key: keyData.key },
        {
          name: name || `${tier} API Key`,
          description,
          createdBy: req.user?.id || 'admin',
        },
        { new: true },
      );

      logger.info('API key generated', {
        correlationId,
        tenantId,
        tier,
        keyId: apiKey.keyId,
      });

      res.status(201).json({
        success: true,
        correlationId,
        data: {
          key: keyData.key, // Only shown once!
          keyId: apiKey.keyId,
          tier,
          expiresAt: keyData.expiresAt,
          tenantId,
        },
        message: 'Save this key immediately - it will not be shown again',
      });
    } catch (error) {
      logger.error('API key generation failed', { error: error.message, correlationId });
      res.status(500).json({
        success: false,
        error: 'KEY_GENERATION_FAILED',
        message: error.message,
        correlationId,
      });
    }
  },
);

/**
 * List all API keys
 * GET /api/admin/keys
 */
router.get('/keys', superAdminGuard, async (req, res) => {
  const correlationId = req.headers['x-correlation-id'] || `admin-${Date.now()}`;

  try {
    const { tenantId, tier, isActive } = req.query;
    const query = {};

    if (tenantId) query.tenantId = tenantId;
    if (tier) query.tier = tier;
    if (isActive !== undefined) query.isActive = isActive === 'true';

    const keys = await ApiKey.find(query)
      .select('-key -usage') // Exclude key hash and detailed usage
      .sort({ createdAt: -1 })
      .lean();

    res.json({
      success: true,
      correlationId,
      data: keys,
      metadata: {
        count: keys.length,
      },
    });
  } catch (error) {
    logger.error('List API keys failed', { error: error.message, correlationId });
    res.status(500).json({
      success: false,
      error: 'LIST_FAILED',
      message: error.message,
      correlationId,
    });
  }
});

/**
 * Get API key details
 * GET /api/admin/keys/:keyId
 */
router.get('/keys/:keyId', superAdminGuard, async (req, res) => {
  const correlationId = req.headers['x-correlation-id'] || `admin-${Date.now()}`;

  try {
    const key = await ApiKey.findOne({ keyId: req.params.keyId })
      .select('-key')
      .populate('tenantId')
      .lean();

    if (!key) {
      return res.status(404).json({
        success: false,
        error: 'KEY_NOT_FOUND',
        message: 'API key not found',
        correlationId,
      });
    }

    res.json({
      success: true,
      correlationId,
      data: key,
    });
  } catch (error) {
    logger.error('Get API key failed', { error: error.message, correlationId });
    res.status(500).json({
      success: false,
      error: 'FETCH_FAILED',
      message: error.message,
      correlationId,
    });
  }
});

/**
 * Update API key
 * PATCH /api/admin/keys/:keyId
 */
router.patch(
  '/keys/:keyId',
  superAdminGuard,
  auditMiddleware({ action: 'API_KEY_UPDATE' }),
  async (req, res) => {
    const correlationId = req.headers['x-correlation-id'] || `admin-${Date.now()}`;

    try {
      const updates = {};
      const allowedUpdates = [
        'tier',
        'isActive',
        'name',
        'description',
        'expiresAt',
        'rateLimits',
        'allowedIPs',
        'allowedDomains',
        'webhookUrl',
      ];

      allowedUpdates.forEach((field) => {
        if (req.body[field] !== undefined) {
          updates[field] = req.body[field];
        }
      });

      updates.updatedBy = req.user?.id;
      updates.updatedAt = new Date();

      const key = await ApiKey.findOneAndUpdate({ keyId: req.params.keyId }, updates, {
        new: true,
      }).select('-key');

      if (!key) {
        return res.status(404).json({
          success: false,
          error: 'KEY_NOT_FOUND',
          message: 'API key not found',
          correlationId,
        });
      }

      logger.info('API key updated', {
        correlationId,
        keyId: key.keyId,
        tenantId: key.tenantId,
        updates: Object.keys(updates),
      });

      res.json({
        success: true,
        correlationId,
        data: key,
      });
    } catch (error) {
      logger.error('Update API key failed', { error: error.message, correlationId });
      res.status(500).json({
        success: false,
        error: 'UPDATE_FAILED',
        message: error.message,
        correlationId,
      });
    }
  },
);

/**
 * Revoke API key (soft delete)
 * DELETE /api/admin/keys/:keyId
 */
router.delete(
  '/keys/:keyId',
  superAdminGuard,
  auditMiddleware({ action: 'API_KEY_REVOKE' }),
  async (req, res) => {
    const correlationId = req.headers['x-correlation-id'] || `admin-${Date.now()}`;

    try {
      const key = await ApiKey.findOneAndUpdate(
        { keyId: req.params.keyId },
        {
          isActive: false,
          updatedBy: req.user?.id,
          updatedAt: new Date(),
        },
        { new: true },
      );

      if (!key) {
        return res.status(404).json({
          success: false,
          error: 'KEY_NOT_FOUND',
          message: 'API key not found',
          correlationId,
        });
      }

      logger.info('API key revoked', {
        correlationId,
        keyId: key.keyId,
        tenantId: key.tenantId,
      });

      res.json({
        success: true,
        correlationId,
        message: 'API key revoked successfully',
      });
    } catch (error) {
      logger.error('Revoke API key failed', { error: error.message, correlationId });
      res.status(500).json({
        success: false,
        error: 'REVOKE_FAILED',
        message: error.message,
        correlationId,
      });
    }
  },
);

/**
 * Get usage analytics
 * GET /api/admin/keys/:keyId/usage
 */
router.get('/keys/:keyId/usage', superAdminGuard, async (req, res) => {
  const correlationId = req.headers['x-correlation-id'] || `admin-${Date.now()}`;

  try {
    const { days = 30 } = req.query;

    const key = await ApiKey.findOne({ keyId: req.params.keyId });
    if (!key) {
      return res.status(404).json({
        success: false,
        error: 'KEY_NOT_FOUND',
        message: 'API key not found',
        correlationId,
      });
    }

    const stats = await ApiKey.getUsageStats(key.tenantId, parseInt(days));

    res.json({
      success: true,
      correlationId,
      data: {
        keyId: key.keyId,
        tenantId: key.tenantId,
        tier: key.tier,
        totalUsage: key.usageCount,
        lastUsed: key.lastUsedAt,
        usageByDay: stats,
      },
    });
  } catch (error) {
    logger.error('Get usage analytics failed', { error: error.message, correlationId });
    res.status(500).json({
      success: false,
      error: 'ANALYTICS_FAILED',
      message: error.message,
      correlationId,
    });
  }
});

export default router;
