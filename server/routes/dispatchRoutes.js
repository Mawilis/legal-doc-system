/*
 * File: server/routes/dispatchRoutes.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Master Dispatch Gateway. Manages the overall Dispatch Board, route optimization, and bulk assignment of instructions.
 * AUTHOR: Wilsy Core Team
 * REVIEWERS: @ops,@logistics,@platform
 * MIGRATION_NOTES: Migrated to Joi Validation; added route optimization endpoints.
 * TESTS: mocha@9.x + chai@4.x; tests bulk assignment and geospatial filtering.
 */

'use strict';

// 1. USAGE COMMENTS
// -----------------------------------------------------------------------------
// Usage:
//   app.use('/api/dispatch', dispatchRoutes);
//
// Functionality:
//   - GET /board: View all active dispatches (Kanban/Map view data).
//   - POST /optimize: Run route optimization algorithm for a specific zone.
//   - POST /bulk-assign: Assign multiple instructions to a single Sheriff.
// -----------------------------------------------------------------------------

const express = require('express');
const router = express.Router();

const dispatchController = require('../controllers/dispatchController');

// 2. MIDDLEWARE (The "Godly" Stack)
const { protect } = require('../middleware/authMiddleware');
const { requireSameTenant, restrictTo } = require('../middleware/rbacMiddleware');
const { emitAudit } = require('../middleware/auditMiddleware');
const validate = require('../middleware/validationMiddleware');

// 3. VALIDATION SCHEMAS (Joi)
const { Joi } = validate;

const boardFilterSchema = {
  status: Joi.string().valid('PENDING', 'IN_PROGRESS', 'COMPLETED', 'PROBLEM').optional(),
  zoneId: Joi.string().optional(),
  sheriffId: Joi.string().optional(),
  date: Joi.date().iso().optional()
};

const optimizeRouteSchema = {
  sheriffId: Joi.string().required(),
  instructionIds: Joi.array().items(Joi.string()).min(2).required(), // Need at least 2 points to optimize
  startLocation: Joi.object({
    lat: Joi.number().required(),
    lng: Joi.number().required()
  }).optional() // Defaults to Sheriff's current location or HQ
};

const bulkAssignSchema = {
  sheriffId: Joi.string().required(),
  instructionIds: Joi.array().items(Joi.string()).min(1).required()
};

// ------------------------------
// ROUTES
// ------------------------------

/**
 * @route   GET /api/dispatch/board
 * @desc    Get Master Dispatch Board Data
 * @access  Admin, Dispatcher
 */
router.get(
  '/board',
  protect,
  requireSameTenant,
  restrictTo('admin', 'dispatcher', 'superadmin'),
  validate(boardFilterSchema, 'query'),
  async (req, res, next) => {
    try {
      const result = await dispatchController.getDispatchBoard(req, res);

      // Light audit for dashboard views (optional, keeps logs clean)
      // await emitAudit(req, { ... }); 

      if (!res.headersSent && result) res.json({ status: 'success', data: result });
    } catch (err) {
      err.code = 'DISPATCH_BOARD_FAILED';
      next(err);
    }
  }
);

/**
 * @route   POST /api/dispatch/optimize
 * @desc    Calculate Optimal Route (TSP Solver)
 * @access  Dispatcher, Sheriff
 */
router.post(
  '/optimize',
  protect,
  requireSameTenant,
  restrictTo('admin', 'dispatcher', 'sheriff'),
  validate(optimizeRouteSchema, 'body'),
  async (req, res, next) => {
    try {
      const result = await dispatchController.optimizeRoute(req, res);

      await emitAudit(req, {
        resource: 'dispatch_engine',
        action: 'OPTIMIZE_ROUTE',
        severity: 'INFO',
        metadata: { sheriffId: req.body.sheriffId, stops: req.body.instructionIds.length }
      });

      if (!res.headersSent && result) res.json({ status: 'success', data: result });
    } catch (err) {
      err.code = 'ROUTE_OPTIMIZE_FAILED';
      next(err);
    }
  }
);

/**
 * @route   POST /api/dispatch/bulk-assign
 * @desc    Bulk Assign Instructions to Sheriff
 * @access  Admin, Dispatcher
 */
router.post(
  '/bulk-assign',
  protect,
  requireSameTenant,
  restrictTo('admin', 'dispatcher'),
  validate(bulkAssignSchema, 'body'),
  async (req, res, next) => {
    try {
      const result = await dispatchController.bulkAssign(req, res);

      await emitAudit(req, {
        resource: 'dispatch_logistics',
        action: 'BULK_ASSIGN',
        severity: 'INFO',
        summary: `Assigned ${req.body.instructionIds.length} tasks to Sheriff ${req.body.sheriffId}`,
        metadata: { taskCount: req.body.instructionIds.length }
      });

      if (!res.headersSent && result) res.json({ status: 'success', data: result });
    } catch (err) {
      err.code = 'BULK_ASSIGN_FAILED';
      next(err);
    }
  }
);

module.exports = router;

// 4. USAGE EXAMPLE
// -----------------------------------------------------------------------------
/*
const dispatchRoutes = require('./server/routes/dispatchRoutes');
app.use('/api/dispatch', dispatchRoutes);
*/

// 5. ACCEPTANCE CRITERIA
// -----------------------------------------------------------------------------
/*
1. [ ] Correctly imports 'validationMiddleware' (Joi).
2. [ ] Validates optimize requests (minimum 2 stops).
3. [ ] Restricts board access to 'dispatcher'/'admin' roles.
4. [ ] Emits Audit Events for route optimization and bulk assignment.
5. [ ] Handles map-based filtering parameters correctly.
*/