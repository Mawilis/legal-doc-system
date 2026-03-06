#!/* eslint-disable */
import express from 'express';
import RetentionPolicy from '../models/RetentionPolicy.js';
import { authenticate } from '../middleware/auth.js';
import { extractTenant } from '../middleware/tenantContext.js';
import { rateLimiter } from '../middleware/rateLimiter.js';
import { auditLogger } from '../utils/auditLogger.js';
import loggerRaw from '../utils/logger.js';

const logger = loggerRaw.default || loggerRaw;

const router = express.Router();

// Apply middleware
router.use(extractTenant);
router.use(authenticate({ required: true }));

/**
 * Create new retention policy
 */
router.post('/policies', rateLimiter({ mode: 'standard' }), async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;

    const policyData = {
      ...req.body,
      tenantId,
      createdBy: req.user?.id || 'system',
    };

    const policy = new RetentionPolicy(policyData);
    await policy.save();

    await auditLogger.log(tenantId, 'RETENTION_POLICY_CREATED', req.user?.id, {
      policyId: policy.policyId,
      policyName: policy.policyName,
    });

    res.status(201).json({
      success: true,
      data: policy,
    });
  } catch (error) {
    logger.error('Failed to create retention policy', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get policies by tenant
 */
router.get('/policies', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;
    const { matterType, status } = req.query;

    const query = { tenantId };
    if (matterType) query.matterType = matterType;
    if (status) query.status = status;

    const policies = await RetentionPolicy.find(query).sort({ createdAt: -1 });

    res.json({
      success: true,
      data: policies,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get active policy for matter type
 */
router.get('/policies/active/:matterType', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;
    const { matterType } = req.params;

    const policy = await RetentionPolicy.getActivePolicy(tenantId, matterType);

    if (!policy) {
      return res.status(404).json({ error: 'No active policy found' });
    }

    res.json({
      success: true,
      data: policy,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get policies expiring soon
 */
router.get('/policies/expiring', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;
    const days = parseInt(req.query.days) || 30;

    const policies = await RetentionPolicy.getExpiringPolicies(tenantId, days);

    res.json({
      success: true,
      data: policies,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get compliance report
 */
router.get('/compliance-report', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;

    const report = await RetentionPolicy.getComplianceReport(tenantId);

    res.json({
      success: true,
      data: report,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get policy by ID
 */
router.get('/policies/:policyId', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;
    const { policyId } = req.params;

    const policy = await RetentionPolicy.findOne({
      policyId,
      tenantId,
    });

    if (!policy) {
      return res.status(404).json({ error: 'Policy not found' });
    }

    res.json({
      success: true,
      data: policy,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Update policy
 */
router.put('/policies/:policyId', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;
    const { policyId } = req.params;
    const userId = req.user?.id;

    const existing = await RetentionPolicy.findOne({
      policyId,
      tenantId,
    });

    if (!existing) {
      return res.status(404).json({ error: 'Policy not found' });
    }

    const newVersion = await existing.createNewVersion(req.body, userId);

    res.json({
      success: true,
      data: newVersion,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * Delete policy (soft delete by archiving)
 */
router.delete('/policies/:policyId', async (req, res) => {
  try {
    const tenantId = req.headers['x-tenant-id'] || req.tenantContext?.tenantId;
    const { policyId } = req.params;

    const policy = await RetentionPolicy.findOne({
      policyId,
      tenantId,
    });

    if (!policy) {
      return res.status(404).json({ error: 'Policy not found' });
    }

    policy.status = 'archived';
    policy.effectiveTo = new Date();
    await policy.save();

    res.json({
      success: true,
      message: 'Policy archived successfully',
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
