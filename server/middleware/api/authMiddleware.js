/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ API KEY AUTHENTICATION - SECURE GATEWAY FOR EXTERNAL CLIENTS             ║
  ║ Tiered access | Rate limiting | Usage tracking | Forensic audit          ║
  ║ R15k/month per license | Multi-tenant isolation                           ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import crypto from 'crypto';
import { ApiKey } from '../../models/api/ApiKey.js';
import { AuditLogger } from '../../utils/auditLogger.js';
import loggerRaw from '../../utils/logger.js';
const logger = loggerRaw.default || loggerRaw;

// ============================================================================
// CONSTANTS
// ============================================================================

const TIERS = {
  FREE: {
    name: 'free',
    requestsPerHour: 10,
    requestsPerMonth: 1000,
    price: 0
  },
  BASIC: {
    name: 'basic',
    requestsPerHour: 100,
    requestsPerMonth: 10000,
    price: 15000 // R15k/month
  },
  PREMIUM: {
    name: 'premium',
    requestsPerHour: 1000,
    requestsPerMonth: 100000,
    price: 50000 // R50k/month
  },
  ENTERPRISE: {
    name: 'enterprise',
    requestsPerHour: 10000,
    requestsPerMonth: 1000000,
    price: 150000 // R150k/month
  }
};

// ============================================================================
// MIDDLEWARE
// ============================================================================

/**
 * Validate API Key middleware
 */
export const validateApiKey = async (req, res, next) => {
  const startTime = Date.now();
  const apiKey = req.headers['x-api-key'] || req.query.apiKey;
  const correlationId = req.headers['x-correlation-id'] || 
                        `api-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  
  req.correlationId = correlationId;
  res.setHeader('x-correlation-id', correlationId);

  if (!apiKey) {
    logger.warn('API key missing', { correlationId, ip: req.ip });
    return res.status(401).json({
      success: false,
      error: 'API_KEY_MISSING',
      message: 'X-API-Key header is required',
      correlationId
    });
  }

  try {
    // Find and validate API key
    const keyDoc = await ApiKey.findOne({ 
      key: apiKey,
      isActive: true,
      expiresAt: { $gt: new Date() }
    }).populate('tenantId');

    if (!keyDoc) {
      logger.warn('Invalid API key', { correlationId, keyPrefix: apiKey.substring(0, 8) });
      
      await AuditLogger.log('api-auth', {
        action: 'API_KEY_INVALID',
        correlationId,
        keyPrefix: apiKey.substring(0, 8),
        ip: req.ip,
        timestamp: new Date().toISOString()
      });
      
      return res.status(403).json({
        success: false,
        error: 'API_KEY_INVALID',
        message: 'Invalid or expired API key',
        correlationId
      });
    }

    // Check rate limits
    const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
    const requestCount = await ApiKey.countDocuments({
      'usage.timestamp': { $gte: hourAgo },
      _id: keyDoc._id
    });

    const tier = TIERS[keyDoc.tier] || TIERS.BASIC;
    if (requestCount >= tier.requestsPerHour) {
      logger.warn('Rate limit exceeded', {
        correlationId,
        tenantId: keyDoc.tenantId,
        tier: keyDoc.tier,
        requestCount
      });
      
      await AuditLogger.log('api-auth', {
        action: 'RATE_LIMIT_EXCEEDED',
        tenantId: keyDoc.tenantId,
        correlationId,
        tier: keyDoc.tier,
        requestCount,
        timestamp: new Date().toISOString()
      });
      
      return res.status(429).json({
        success: false,
        error: 'RATE_LIMIT_EXCEEDED',
        message: `Rate limit of ${tier.requestsPerHour} requests per hour exceeded`,
        retryAfter: 3600 - Math.floor((Date.now() - hourAgo) / 1000),
        correlationId
      });
    }

    // Track usage
    await ApiKey.updateOne(
      { _id: keyDoc._id },
      {
        $push: {
          usage: {
            timestamp: new Date(),
            endpoint: req.path,
            method: req.method,
            correlationId,
            ip: req.ip,
            userAgent: req.headers['user-agent']
          }
        },
        $inc: { usageCount: 1 }
      }
    );

    // Attach to request
    req.apiKey = keyDoc;
    req.tenantId = keyDoc.tenantId;
    req.tier = keyDoc.tier;

    logger.info('API key validated', {
      correlationId,
      tenantId: keyDoc.tenantId,
      tier: keyDoc.tier
    });

    next();

  } catch (error) {
    logger.error('API key validation failed', {
      correlationId,
      error: error.message
    });
    
    res.status(500).json({
      success: false,
      error: 'AUTHENTICATION_ERROR',
      message: 'Failed to validate API key',
      correlationId
    });
  }
};

/**
 * Tier-based access control
 */
export const requireTier = (requiredTier) => {
  return (req, res, next) => {
    const tiers = Object.keys(TIERS);
    const userTierIndex = tiers.indexOf(req.tier);
    const requiredTierIndex = tiers.indexOf(requiredTier);
    
    if (userTierIndex < requiredTierIndex) {
      logger.warn('Insufficient tier', {
        correlationId: req.correlationId,
        tenantId: req.tenantId,
        userTier: req.tier,
        requiredTier
      });
      
      return res.status(403).json({
        success: false,
        error: 'INSUFFICIENT_TIER',
        message: `This endpoint requires ${requiredTier} tier or higher`,
        currentTier: req.tier,
        correlationId: req.correlationId
      });
    }
    
    next();
  };
};

/**
 * Generate new API key (admin only)
 */
export const generateApiKey = async (tenantId, tier = 'BASIC', expiresInDays = 365) => {
  const key = `wilsy_${crypto.randomBytes(24).toString('hex')}`;
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + expiresInDays);
  
  const apiKey = new ApiKey({
    key,
    tenantId,
    tier,
    expiresAt,
    createdBy: 'system'
  });
  
  await apiKey.save();
  
  return {
    key,
    tier,
    expiresAt,
    tenantId
  };
};

export default {
  validateApiKey,
  requireTier,
  generateApiKey,
  TIERS
};
