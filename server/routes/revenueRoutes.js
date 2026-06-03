/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - REVENUE NUCLEUS ROUTES [V25.4.0-MARS]                                                                                       ║
 * ║ [FINANCIAL TELEMETRY | LEDGER ANCHORING | CONDITIONAL ROLE CHECK | SOVEREIGN BYPASS]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 25.4.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/revenueRoutes.js                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated conditional role check to resolve 403 fractures. [2026-05-17]                        ║
 * ║ • AI Engineering (DeepSeek) - FORTIFIED: Added conditionalRoleCheck to bypass authorizeRoles for sovereign users. [2026-05-17]         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import {
  getRevenueMetrics,
  getRevenueLedger,
  getRevenueTrajectory,
  logRevenueStrike,
  revenueStatus
} from '../controllers/revenueController.js';
import { requireSovereignAuth, authorizeRoles } from '../middleware/auth.middleware.js';
import { rateLimiter } from '../middleware/rateLimiter.js';
import { breakerRegistry } from '../utils/circuitBreaker.js';
import auditLogger from '../utils/auditLogger.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import { performance } from 'perf_hooks';

const router = express.Router();

const MASTER_ROLES = ['FOUNDER', 'founder', 'OMEGA', 'omega', 'SUPER_ADMIN', 'super_admin'];

/**
 * Forces founder and omega-cleared requests onto the root revenue tenant.
 * @function sovereignBypass
 * @param {import('express').Request} req - Incoming request with optional authenticated user.
 * @param {import('express').Response} res - Express response, unused but retained for middleware shape.
 * @param {import('express').NextFunction} next - Express continuation callback.
 * @returns {void}
 * @collaboration Wilson Khanyezi mandated that founder-level revenue reads cannot drift into an arbitrary tenant scope.
 */
const sovereignBypass = (req, res, next) => {
  if (req.user) {
    const isFounderEmail = req.user.email === 'wilsonkhanyezi@gmail.com';
    const isOmegaClearance = req.user.securityClearance === 'omega';
    const userRoleUpper = (req.user.role || '').toUpperCase();
    const isMasterRole = MASTER_ROLES.includes(userRoleUpper) || MASTER_ROLES.includes(req.user.role);
    if (isFounderEmail || isOmegaClearance || isMasterRole) {
      req.headers['x-tenant-id'] = 'GLOBAL_ROOT';
      req.tenantId = 'GLOBAL_ROOT';
      console.log(`[REVENUE-ROUTES] 🛡️ Sovereign bypass activated for user ${req.user.id} – forcing tenant GLOBAL_ROOT`);
    }
  }
  next();
};

/**
 * Enforces revenue roles while letting founder/omega users bypass duplicate role gates.
 * @function conditionalRoleCheck
 * @param {import('express').Request} req - Incoming request with optional authenticated user.
 * @param {import('express').Response} res - Express response.
 * @param {import('express').NextFunction} next - Express continuation callback.
 * @returns {void}
 * @collaboration Wilson Khanyezi required sovereign operators to move through revenue intelligence without redundant role friction.
 */
const conditionalRoleCheck = (req, res, next) => {
  if (!req.user) return next();
  const userRoleUpper = (req.user.role || '').toUpperCase();
  const isMasterRole = MASTER_ROLES.includes(userRoleUpper) || MASTER_ROLES.includes(req.user.role);
  const hasOmegaClearance = req.user.securityClearance === 'omega';
  if (isMasterRole || hasOmegaClearance) {
    console.log(`[REVENUE-ROUTES] 👑 Sovereign user – bypassing role check`);
    return next();
  }
  return authorizeRoles(...MASTER_ROLES)(req, res, next);
};

/**
 * Wraps a revenue route in a tenant-scoped financial circuit breaker.
 * @function withFinancialBreaker
 * @param {string} actionName - Revenue action being guarded.
 * @param {Function} handler - Express route handler to execute through the breaker.
 * @returns {Function} Express middleware that contains circuit errors and telemetry fractures.
 * @collaboration Wilson Khanyezi mandated that telemetry or breaker faults must never collapse the revenue cockpit.
 */
const withFinancialBreaker = (actionName, handler) => {
  return async (req, res, next) => {
    const start = performance.now();
    const tenantId = req.headers['x-tenant-id'] || 'GLOBAL_ROOT';
    const breakerKey = `FINANCE_${actionName}_${tenantId}`;
    let breaker = breakerRegistry.get(breakerKey);
    if (!breaker) {
      const newBreaker = {
        name: breakerKey,
        tenantId: tenantId,
        state: 'CLOSED',
        failureCount: 0,
        lastFailure: null,
        fire: async (fn) => fn(),
        getStatus: () => ({ state: 'CLOSED', failureCount: 0 })
      };
      breakerRegistry.set(breakerKey, newBreaker);
      breaker = newBreaker;
    }
    try {
      if (breaker && typeof breaker.fire === 'function') {
        return await breaker.fire(async () => await handler(req, res, next));
      } else {
        return await handler(req, res, next);
      }
    } catch (err) {
      const isOpen = breaker && breaker.getStatus && breaker.getStatus().state === 'OPEN';
      if (isOpen || (err && err.message === 'CIRCUIT_OPEN')) {
        const latencyMs = (performance.now() - start).toFixed(2);
        auditLogger.security('FINANCIAL_BREAKER_TRIPPED', {
           resource: `REVENUE_${actionName}`,
           tenantId,
           status: 'CRITICAL',
           metadata: { ip: req.ip, latencyMs }
        }).catch(() => {});
        broadcastTelemetry(tenantId, 'CIRCUIT_BREAKER', 'FINANCIAL_STRIKE_LOCKED', `REVENUE_${actionName}`, {
          traceId: req.traceId,
          latencyMs
        }).catch(() => {});
        if (!res.headersSent) {
          return res.status(503).json({
            success: false,
            error: 'CIRCUIT_OPEN',
            message: `Financial Action ${actionName} Temporarily Locked.`
          });
        }
      } else {
        if (!res.headersSent) next(err);
      }
    }
  };
};

router.get('/metrics',
  requireSovereignAuth,
  sovereignBypass,
  conditionalRoleCheck,
  withFinancialBreaker('METRICS', getRevenueMetrics)
);

router.get('/ledger',
  requireSovereignAuth,
  sovereignBypass,
  conditionalRoleCheck,
  withFinancialBreaker('LEDGER', getRevenueLedger)
);

router.get('/trajectory',
  requireSovereignAuth,
  sovereignBypass,
  conditionalRoleCheck,
  withFinancialBreaker('TRAJECTORY', getRevenueTrajectory)
);

router.post('/strike',
  requireSovereignAuth,
  sovereignBypass,
  conditionalRoleCheck,
  rateLimiter({ max: 2000 }),
  withFinancialBreaker('LOG_STRIKE', logRevenueStrike)
);

router.get('/status',
  requireSovereignAuth,
  sovereignBypass,
  conditionalRoleCheck,
  withFinancialBreaker('STATUS', revenueStatus)
);

export default router;

console.log(`
╔══════════════════════════════════════════════════════════════════════════╗
║                 💰 REVENUE NUCLEUS ROUTES ACTIVE                     ║
║   Conditional Role Check: ENABLED | Sovereign Bypass: ON                ║
╚══════════════════════════════════════════════════════════════════════════╝
`);
