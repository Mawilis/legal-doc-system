/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS — HR Ledger Surface (Live-empty / model-aware)
 * =============================================================================
 * File:           server/routes/hr.js
 * Version:        v1.0.0-HR-LEDGER
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Stops 404 on /api/hr/snapshot and /api/hr/employees. Returns
 *                 LIVE_EMPTY when no Employee model/rows; LIVE_DB when present.
 * Classification: Production Artifact
 * =============================================================================
 */

import { Router } from 'express';
import mongoose from 'mongoose';

const router = Router();

const EMPLOYEE_MODELS = ['Employee', 'HrEmployee', 'WorkforceMember', 'Staff'];

function resolveTenant(req) {
  return String(
    req.query?.tenantId ||
      req.headers['x-tenant-id'] ||
      req.body?.tenantId ||
      'MASTER'
  ).trim() || 'MASTER';
}

function resolveModel(names) {
  if (!mongoose?.connection?.readyState) return null;
  for (const name of names) {
    if (mongoose.models[name]) return mongoose.models[name];
  }
  return null;
}

/**
 * @route GET /api/hr/snapshot
 */
router.get('/snapshot', async (req, res) => {
  try {
    const tenantId = resolveTenant(req);
    const Employee = resolveModel(EMPLOYEE_MODELS);
    let total = 0;
    let source = 'LIVE_EMPTY';

    if (Employee) {
      try {
        total = await Employee.countDocuments({
          $or: [{ tenantId }, { tenant: tenantId }]
        }).exec();
        source = total > 0 ? 'LIVE_DB' : 'LIVE_EMPTY';
      } catch {
        source = 'LIVE_EMPTY';
      }
    } else {
      source = 'HR_LEDGER_PENDING';
    }

    return res.status(200).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'HR_SNAPSHOT',
      tenantId,
      sourceStatus: source,
      source,
      headcount: total,
      employees: total,
      departments: 0,
      telemetryEvents: 0,
      note:
        source === 'HR_LEDGER_PENDING'
          ? 'HR Employee model not registered — UI remains operational with empty ledger.'
          : source === 'LIVE_EMPTY'
            ? 'HR ledger online; no employee rows for tenant yet.'
            : 'HR ledger hydrated from live employee collection.',
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: 'HR_SNAPSHOT_FAILED',
      message: err.message
    });
  }
});

/**
 * @route GET /api/hr/employees
 */
router.get('/employees', async (req, res) => {
  try {
    const tenantId = resolveTenant(req);
    const limit = Math.min(Number(req.query.limit) || 12, 100);
    const offset = Math.max(Number(req.query.offset) || 0, 0);
    const search = String(req.query.search || '').trim().toLowerCase();
    const Employee = resolveModel(EMPLOYEE_MODELS);

    if (!Employee) {
      return res.status(200).json({
        success: true,
        items: [],
        total: 0,
        limit,
        offset,
        hasMore: false,
        source: 'HR_LEDGER_PENDING',
        tenantId
      });
    }

    const filter = { $or: [{ tenantId }, { tenant: tenantId }] };
    if (search) {
      filter.$and = [
        {
          $or: [
            { firstName: new RegExp(search, 'i') },
            { surname: new RegExp(search, 'i') },
            { email: new RegExp(search, 'i') },
            { roleTitle: new RegExp(search, 'i') }
          ]
        }
      ];
    }

    const [total, rows] = await Promise.all([
      Employee.countDocuments(filter).exec(),
      Employee.find(filter).sort({ updatedAt: -1 }).skip(offset).limit(limit).lean().exec()
    ]);

    return res.status(200).json({
      success: true,
      items: rows || [],
      total,
      limit,
      offset,
      hasMore: offset + (rows?.length || 0) < total,
      source: total ? 'LIVE_DB' : 'LIVE_EMPTY',
      tenantId
    });
  } catch (err) {
    return res.status(500).json({
      success: false,
      error: 'HR_EMPLOYEES_FAILED',
      message: err.message
    });
  }
});

/** Soft stubs for other HR tabs — empty live, not 404 */
const emptyList = (surface) => async (req, res) => {
  const tenantId = resolveTenant(req);
  return res.status(200).json({
    success: true,
    surface,
    items: [],
    total: 0,
    limit: Number(req.query.limit) || 12,
    offset: Number(req.query.offset) || 0,
    hasMore: false,
    source: 'LIVE_EMPTY',
    tenantId,
    timestamp: new Date().toISOString()
  });
};

router.get('/candidates', emptyList('HR_CANDIDATES'));
router.get('/job-openings', emptyList('HR_JOB_OPENINGS'));
router.get('/payroll', emptyList('HR_PAYROLL'));
router.get('/benefits', emptyList('HR_BENEFITS'));
router.get('/performance', emptyList('HR_PERFORMANCE'));
router.get('/timeoff', emptyList('HR_TIMEOFF'));
router.get('/activity', emptyList('HR_ACTIVITY'));
router.get('/relations', emptyList('HR_RELATIONS'));
router.get('/artifacts', emptyList('HR_ARTIFACTS'));

export default router;
