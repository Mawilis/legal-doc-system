/*
 * ====================================================================================
 * WILSY OS SOVEREIGN ROUTES
 * ====================================================================================
 * FILE:        server/routes/merkleRoutes.js
 * VERSION:     v1.1.0-OMEGA-PHASE8
 * AUTHORITY:   Wilsy OS Kennel EOS / Lead Architect @WilsyCore
 * EPITOME:     REST routing for Merkle proof operations.
 *              Exposes endpoints for proof generation, verification, root computation, and health.
 * INSTITUTIONAL CONTEXT: Phase 8 – Merkle Service Integration.
 * COMPLIANCE:  POPIA §19, GDPR §32, SOC2 §CC7.2
 * COLLABORATION: @WilsyCore @BackendLead @SecurityLead
 * ====================================================================================
 */

import express from 'express';
import MerkleController from '../controllers/merkleController.js';
import { authenticate } from '../middleware/auth.js';
import { rateLimit } from 'express-rate-limit';
import { logAuditEvent } from '../services/auditStream.js';

const router = express.Router();

// Sovereign latency logger middleware
router.use((req, res, next) => {
  const start = process.hrtime.bigint();
  res.on('finish', () => {
    const end = process.hrtime.bigint();
    const durationMs = Number(end - start) / 1e6;
    logAuditEvent({
      tenant: req.user?.tenant || 'unknown',
      action: 'route_latency',
      details: { path: req.originalUrl, durationMs },
      userId: req.user?.id
    });
  });
  next();
});

// Granular rate limits
const proofLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 50,
  message: { error: 'Too many proof requests, please try again later.' }
});

const verifyLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 50,
  message: { error: 'Too many verify requests, please try again later.' }
});

const rootLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 100,
  message: { error: 'Too many root requests, please try again later.' }
});

/**
 * @route   POST /api/merkle/proof
 * @desc    Generate a Merkle proof for a leaf at a given index.
 * @access  Private (authenticated)
 */
router.post(
  '/proof',
  authenticate,
  proofLimiter,
  async (req, res, next) => {
    try {
      await MerkleController.generateProof(req, res, next);
    } catch (err) {
      next(err);
    }
  }
);

/**
 * @route   POST /api/merkle/verify
 * @desc    Verify a Merkle proof against a root hash.
 * @access  Private (authenticated)
 */
router.post(
  '/verify',
  authenticate,
  verifyLimiter,
  async (req, res, next) => {
    try {
      await MerkleController.verifyProof(req, res, next);
    } catch (err) {
      next(err);
    }
  }
);

/**
 * @route   POST /api/merkle/root
 * @desc    Compute the Merkle root and merkleRootId for a set of leaves.
 * @access  Private (authenticated)
 */
router.post(
  '/root',
  authenticate,
  rootLimiter,
  async (req, res, next) => {
    try {
      await MerkleController.getRoot(req, res, next);
    } catch (err) {
      next(err);
    }
  }
);

/**
 * @route   GET /api/merkle/health
 * @desc    Health check for the Merkle service.
 * @access  Public
 */
router.get(
  '/health',
  async (req, res) => {
    try {
      await MerkleController.healthCheck(req, res);
    } catch (err) {
      res.status(500).json({ error: 'Health check failed' });
    }
  }
);

export default router;

/*
 * ====================================================================================
 * INSTITUTIONAL CERTIFICATION SEAL – MERKLE ROUTES
 * Status:          PRODUCTION READY
 * Version:         v1.1.0-OMEGA-PHASE8
 * Compliance:      POPIA §19 | GDPR §32 | SOC2 §CC7.2
 * Cryptographic:   Endpoints return SHA3-512 seals for verifiability.
 * Security:        Authenticated routes; granular rate limiting applied.
 * Audit Logging:   Route latency + controller actions logged.
 * Tenant Scoping:  Enforced via authentication middleware.
 * ====================================================================================
 */
