/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SUBSCRIPTION ROUTES [V1.1.0-METHOD-PARITY]                                                                       ║
 * ║ [RECURRING BILLING LIFECYCLE | FORENSIC SEALING | IDEMPOTENCY | CLIENT POST PARITY]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-METHOD-PARITY | PRODUCTION READY                                                                                       ║
 * ║ EPITOME: Subscription REST surface aligned with useSubscriptions (POST lifecycle) and RESTful PATCH/DELETE aliases.                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/subscriptionRoutes.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated enterprise-grade subscription lifecycle.                                            ║
 * ║ • AI Engineering – V1.1.0: POST aliases for pause/resume/cancel/upgrade/downgrade (hook parity); /health before :id.                 ║
 * ║ • Compliance: POPIA §19, GDPR §32, SOC2 §CC7.2.                                                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ FORENSIC RELATIONSHIPS:                                                                                                                ║
 * ║   Upstream:   subscriptionController.js, auth.middleware.js, traceMiddleware.js                                                       ║
 * ║   Downstream: client useSubscriptions.js (POST /subscriptions, POST .../pause|resume|cancel|upgrade|downgrade|reactivate)           ║
 * ║   Mount:      app.use('/api/subscriptions') + router.use('/subscriptions') in api.js                                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import { rateLimit } from 'express-rate-limit';
import {
  createSubscription,
  getSubscription,
  listSubscriptions,
  pauseSubscription,
  resumeSubscription,
  cancelSubscription,
  upgradeSubscription,
  downgradeSubscription,
  reactivateSubscription,
  getSubscriptionAudit,
} from '../controllers/subscriptionController.js';
import { requireSovereignAuth, authorizeRoles } from '../middleware/auth.middleware.js';
import { injectTraceId } from '../middleware/traceMiddleware.js';

const router = express.Router();

const SUBSCRIPTION_WRITE_ROLES = [
  'FOUNDER',
  'founder',
  'FOUNDER_ARCHITECT',
  'founder_architect',
  'OMEGA',
  'omega',
  'SUPER_ADMIN',
  'super_admin',
  'ADMIN',
  'admin',
  'BILLING',
  'billing',
  'ACCOUNTS',
  'accounts',
];

const SUBSCRIPTION_READ_ROLES = [
  ...SUBSCRIPTION_WRITE_ROLES,
  'FINANCE',
  'finance',
  'AUDITOR',
  'auditor',
];

const subscriptionRateLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 50,
  message: {
    status: 429,
    message: 'Institutional rate limit exceeded. Subscription operations throttled.',
  },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => `${req.user?.tenantId || 'anonymous'}:${req.ip}`,
});

router.use(injectTraceId);

/**
 * @route GET /api/subscriptions/health
 * @desc Router health (must be registered before /:subscriptionId).
 * @access Public probe for BFF readiness (auth optional at mount).
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OPERATIONAL',
    module: 'subscriptionRoutes',
    version: '1.1.0-METHOD-PARITY',
    methods: {
      create: 'POST /',
      list: 'GET /',
      pause: 'POST|PATCH /:id/pause',
      resume: 'POST|PATCH /:id/resume',
      cancel: 'POST|DELETE /:id/cancel and DELETE /:id',
      upgrade: 'POST|PATCH /:id/upgrade',
      downgrade: 'POST|PATCH /:id/downgrade',
      reactivate: 'POST /:id/reactivate',
      audit: 'GET /:id/audit',
    },
    timestamp: new Date().toISOString(),
  });
});

/**
 * @route POST /api/subscriptions
 * @desc Create a new sovereign subscription.
 */
router.post(
  '/',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  createSubscription
);

/**
 * @route GET /api/subscriptions
 * @desc List subscriptions (tenant-scoped in controller).
 */
router.get(
  '/',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_READ_ROLES),
  listSubscriptions
);

/**
 * @route GET /api/subscriptions/:subscriptionId
 * @desc Retrieve one subscription.
 */
router.get(
  '/:subscriptionId',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_READ_ROLES),
  getSubscription
);

/**
 * Pause — POST (useSubscriptions) and PATCH (REST).
 */
router.post(
  '/:subscriptionId/pause',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  pauseSubscription
);
router.patch(
  '/:subscriptionId/pause',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  pauseSubscription
);

/**
 * Resume — POST + PATCH.
 */
router.post(
  '/:subscriptionId/resume',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  resumeSubscription
);
router.patch(
  '/:subscriptionId/resume',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  resumeSubscription
);

/**
 * Cancel — POST /:id/cancel (hook), DELETE /:id (REST), DELETE /:id/cancel.
 */
router.post(
  '/:subscriptionId/cancel',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  cancelSubscription
);
router.delete(
  '/:subscriptionId/cancel',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  cancelSubscription
);
router.delete(
  '/:subscriptionId',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  cancelSubscription
);

/**
 * Upgrade / Downgrade — POST + PATCH.
 */
router.post(
  '/:subscriptionId/upgrade',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  upgradeSubscription
);
router.patch(
  '/:subscriptionId/upgrade',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  upgradeSubscription
);

router.post(
  '/:subscriptionId/downgrade',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  downgradeSubscription
);
router.patch(
  '/:subscriptionId/downgrade',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  downgradeSubscription
);

/**
 * Reactivate.
 */
router.post(
  '/:subscriptionId/reactivate',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_WRITE_ROLES),
  subscriptionRateLimiter,
  reactivateSubscription
);

/**
 * Audit trail.
 */
router.get(
  '/:subscriptionId/audit',
  requireSovereignAuth,
  authorizeRoles(...SUBSCRIPTION_READ_ROLES),
  getSubscriptionAudit
);

export default router;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — subscriptionRoutes v1.1.0-METHOD-PARITY
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status: PRODUCTION READY
 * Client parity: useSubscriptions POST lifecycle paths accepted
 * Health: GET /api/subscriptions/health registered before :id
 * ═══════════════════════════════════════════════════════════════════════════════
 */
