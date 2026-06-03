/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT PLAN CONTROLLER - OMEGA SINGULARITY                                                                                  ║
 * ║ [SUBSCRIPTION GOVERNANCE | REVENUE OPTIMISATION | FORENSIC AUDIT]                                                                      ║
 * ║ VERSION: 31.0.0-SINGULARITY                                                                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE                                                                                    ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/tenantPlanController.js                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import Tenant from '../models/Tenant.js';
import ValidationAudit from '../models/ValidationAudit.js';
import { AppError } from '../utils/errorHandler.js';
import * as auditLogger from '../utils/auditLogger.js';

export const getPlanDetails = async (req, res, next) => {
  const traceId = req.headers['x-request-id'] || crypto.randomBytes(8).toString('hex');
  const tenantId = req.tenantContext?.tenantId || req.user?.tenantId;

  try {
    const tenant = await Tenant.findOne({ tenantId });
    if (!tenant) throw new AppError('Tenant not found', 404);

    const planDetails = {
      tier: tenant.tier,
      features: tenant.features || [],
      limits: tenant.limits || {},
      validUntil: tenant.subscriptionValidUntil || null
    };

    await auditLogger.log({
      action: 'PLAN_DETAILS_VIEWED',
      category: 'BILLING',
      tenantId,
      status: 'SUCCESS',
      metadata: { tier: tenant.tier, traceId }
    });

    res.status(200).json({ success: true, data: planDetails, traceId });
  } catch (error) {
    next(error);
  }
};

export const upgradePlan = async (req, res, next) => {
  const traceId = req.headers['x-request-id'] || crypto.randomBytes(8).toString('hex');
  const tenantId = req.tenantContext?.tenantId || req.user?.tenantId;
  const { newTier } = req.body;

  try {
    const tenant = await Tenant.findOne({ tenantId });
    if (!tenant) throw new AppError('Tenant not found', 404);

    const oldTier = tenant.tier;
    tenant.tier = newTier;
    tenant.updatedAt = new Date();
    await tenant.save();

    await auditLogger.log({
      action: 'PLAN_UPGRADED',
      category: 'BILLING',
      tenantId,
      resource: tenant._id,
      status: 'SUCCESS',
      metadata: { oldTier, newTier, traceId }
    });

    res.status(200).json({ success: true, message: 'Plan upgraded', data: { oldTier, newTier }, traceId });
  } catch (error) {
    next(error);
  }
};

export const downgradePlan = async (req, res, next) => {
  const traceId = req.headers['x-request-id'] || crypto.randomBytes(8).toString('hex');
  const tenantId = req.tenantContext?.tenantId || req.user?.tenantId;
  const { newTier } = req.body;

  try {
    const tenant = await Tenant.findOne({ tenantId });
    if (!tenant) throw new AppError('Tenant not found', 404);

    const oldTier = tenant.tier;
    tenant.tier = newTier;
    tenant.updatedAt = new Date();
    await tenant.save();

    await auditLogger.log({
      action: 'PLAN_DOWNGRADED',
      category: 'BILLING',
      tenantId,
      resource: tenant._id,
      status: 'SUCCESS',
      metadata: { oldTier, newTier, traceId }
    });

    res.status(200).json({ success: true, message: 'Plan downgraded', data: { oldTier, newTier }, traceId });
  } catch (error) {
    next(error);
  }
};

export default {
  getPlanDetails,
  upgradePlan,
  downgradePlan
};
