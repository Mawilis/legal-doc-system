#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ TEMPLATE ROUTES - INVESTOR-GRADE MODULE                                   ║
  ║ Document template management for e-signature system                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import { DocumentTemplate } from '../models/DocumentTemplate.js';
import { authMiddleware } from '../middleware/auth.js';
import { tenantContext, getCurrentTenant, getCurrentUser } from '../middleware/tenantContext.js';
import logger from '../utils/logger.js';

const router = express.Router();

// Apply middleware
router.use(tenantContext);
router.use(authMiddleware);

/**
 * Create a new template
 * POST /api/templates
 */
router.post('/', async (req, res, next) => {
  try {
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const templateData = req.body;

    const template = new DocumentTemplate({
      ...templateData,
      tenantId,
      audit: {
        createdBy: userId,
        createdAt: new Date(),
      },
    });

    await template.save();

    logger.info('Template created', {
      templateId: template.templateId,
      tenantId,
      userId,
    });

    res.status(201).json(template);
  } catch (error) {
    next(error);
  }
});

/**
 * Get all templates
 * GET /api/templates
 */
router.get('/', async (req, res, next) => {
  try {
    const tenantId = getCurrentTenant();
    const templates = await DocumentTemplate.find({ tenantId }).sort({ createdAt: -1 });
    res.json(templates);
  } catch (error) {
    next(error);
  }
});

/**
 * Get template by ID
 * GET /api/templates/:templateId
 */
router.get('/:templateId', async (req, res, next) => {
  try {
    const tenantId = getCurrentTenant();
    const { templateId } = req.params;

    const template = await DocumentTemplate.findOne({ templateId, tenantId });
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }

    res.json(template);
  } catch (error) {
    next(error);
  }
});

/**
 * Update template
 * PUT /api/templates/:templateId
 */
router.put('/:templateId', async (req, res, next) => {
  try {
    const tenantId = getCurrentTenant();
    const userId = getCurrentUser();
    const { templateId } = req.params;
    const updates = req.body;

    const template = await DocumentTemplate.findOne({ templateId, tenantId });
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }

    Object.assign(template, updates);
    template.audit.updatedBy = userId;
    template.audit.updatedAt = new Date();

    await template.save();

    res.json(template);
  } catch (error) {
    next(error);
  }
});

/**
 * Delete template
 * DELETE /api/templates/:templateId
 */
router.delete('/:templateId', async (req, res, next) => {
  try {
    const tenantId = getCurrentTenant();
    const { templateId } = req.params;

    const template = await DocumentTemplate.findOne({ templateId, tenantId });
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }

    // Soft delete - mark as archived
    template.status = 'archived';
    await template.save();

    res.json({ success: true, message: 'Template archived' });
  } catch (error) {
    next(error);
  }
});

export default router;
