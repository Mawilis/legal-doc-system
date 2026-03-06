#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ NEURAL PRECEDENT API ROUTES - QUANTUM LEGAL SEARCH GATEWAY                ║
  ║ R25M/year revenue | Rate limited | Tiered access | Forensic audit         ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

import express from 'express';
import rateLimit from 'express-rate-limit';
import {
  searchPrecedents,
  getPrecedentById,
  getSimilarPrecedents,
  getSearchStats,
} from '../../controllers/api/precedentApiController.js';
import { validateApiKey, requireTier } from '../../middleware/api/authMiddleware.js';
import { validateRequest } from '../../middleware/requestValidator.js';
import auditMiddleware from '../../middleware/auditLogger.js';

const router = express.Router();

// ============================================================================
// RATE LIMITING CONFIGURATION
// ============================================================================

// General API rate limit (per API key)
const apiLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 100, // Default max, will be overridden by tier
  keyGenerator: (req) => req.apiKey?.key || req.ip,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      success: false,
      error: 'RATE_LIMIT_EXCEEDED',
      message: 'Rate limit exceeded. Please upgrade your plan for higher limits.',
      retryAfter: Math.ceil((req.rateLimit.resetTime - Date.now()) / 1000),
      correlationId: req.correlationId,
    });
  },
});

// Strict limiter for expensive operations
const strictLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 20,
  keyGenerator: (req) => req.apiKey?.key || req.ip,
});

// ============================================================================
// VALIDATION SCHEMAS
// ============================================================================

const searchSchema = {
  body: {
    query: {
      type: 'string', required: true, minLength: 3, maxLength: 500,
    },
    limit: {
      type: 'number', min: 1, max: 100, optional: true,
    },
    mode: { type: 'string', enum: ['semantic', 'keyword', 'hybrid'], optional: true },
    filters: { type: 'object', optional: true },
  },
};

const similarSchema = {
  body: {
    limit: {
      type: 'number', min: 1, max: 20, optional: true,
    },
  },
};

// ============================================================================
// ROUTES
// ============================================================================

/**
 * @openapi
 * /api/v1/precedents/search:
 *   post:
 *     summary: Search legal precedents using neural embeddings
 *     tags: [Neural Precedent API]
 *     security:
 *       - ApiKeyAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - query
 *             properties:
 *               query:
 *                 type: string
 *                 minLength: 3
 *                 example: "right to life death penalty"
 *               limit:
 *                 type: integer
 *                 default: 10
 *               mode:
 *                 type: string
 *                 enum: [semantic, keyword, hybrid]
 *                 default: semantic
 *               filters:
 *                 type: object
 *                 properties:
 *                   court:
 *                     type: string
 *                   yearFrom:
 *                     type: integer
 *                   yearTo:
 *                     type: integer
 *     responses:
 *       200:
 *         description: Search results with similarity scores
 *       429:
 *         description: Rate limit exceeded
 */
router.post(
  '/search',
  validateApiKey,
  apiLimiter,
  validateRequest(searchSchema),
  auditMiddleware({ action: 'NEURAL_API_SEARCH' }),
  searchPrecedents,
);

/**
 * @openapi
 * /api/v1/precedents/{id}:
 *   get:
 *     summary: Get precedent by ID
 *     tags: [Neural Precedent API]
 *     security:
 *       - ApiKeyAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Quantum ID, MongoDB ID, or citation
 *     responses:
 *       200:
 *         description: Precedent details
 *       404:
 *         description: Precedent not found
 */
router.get(
  '/:id',
  validateApiKey,
  apiLimiter,
  auditMiddleware({ action: 'NEURAL_API_GET' }),
  getPrecedentById,
);

/**
 * @openapi
 * /api/v1/precedents/{id}/similar:
 *   post:
 *     summary: Find similar precedents
 *     tags: [Neural Precedent API]
 *     security:
 *       - ApiKeyAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               limit:
 *                 type: integer
 *                 default: 5
 *     responses:
 *       200:
 *         description: Similar precedents
 */
router.post(
  '/:id/similar',
  validateApiKey,
  strictLimiter,
  validateRequest(similarSchema),
  auditMiddleware({ action: 'NEURAL_API_SIMILAR' }),
  getSimilarPrecedents,
);

/**
 * @openapi
 * /api/v1/precedents/stats:
 *   get:
 *     summary: Get search statistics
 *     tags: [Neural Precedent API]
 *     security:
 *       - ApiKeyAuth: []
 *       - TierAuth: [premium, enterprise]
 *     responses:
 *       200:
 *         description: Usage statistics
 */
router.get(
  '/stats',
  validateApiKey,
  requireTier('PREMIUM'),
  apiLimiter,
  auditMiddleware({ action: 'NEURAL_API_STATS' }),
  getSearchStats,
);

export default router;
