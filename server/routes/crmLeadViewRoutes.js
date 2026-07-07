/* eslint-disable */
const express = require('express');
const {
  archiveLeadView,
  createLeadView,
  explainLeadCategories,
  listTenantLeadViews,
  previewLeadViewCriteria,
  resolveRequestContext,
  runLeadView,
  updateLeadView,
} = require('../services/crmLeadViewRegistryService');

const router = express.Router();

/**
 * @function sendLeadViewSuccess
 * @description Sends a normalized Lead View Registry success response.
 * @collaboration CRM API, Custom View Builder, Wilsy AI, audit receipts, and frontend hydration.
 * @param {object} res Express response.
 * @param {object} payload Response payload.
 * @returns {object} Express response.
 */
function sendLeadViewSuccess(res, payload = {}) {
  return res.status(payload.statusCode || 200).json({
    ok: true,
    generatedAt: new Date().toISOString(),
    ...payload,
  });
}

/**
 * @function sendLeadViewError
 * @description Sends a normalized Lead View Registry error response.
 * @collaboration CRM API, audit posture, frontend recovery, and Wilsy AI route diagnostics.
 * @param {object} res Express response.
 * @param {Error} error Error.
 * @param {number} statusCode HTTP status code.
 * @returns {object} Express response.
 */
function sendLeadViewError(res, error, statusCode = 500) {
  return res.status(statusCode).json({
    ok: false,
    error: error?.message || 'Lead View Registry request failed',
    generatedAt: new Date().toISOString(),
  });
}

/**
 * @function listLeadViews
 * @description Lists tenant-visible saved Lead views.
 * @collaboration View Organizer, saved custom views, tenant visibility, and CRM UX hydration.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function listLeadViews(req, res) {
  try {
    const context = resolveRequestContext(req);
    const views = await listTenantLeadViews(context);
    return sendLeadViewSuccess(res, { views });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

/**
 * @function createLeadViewHandler
 * @description Creates a saved Lead view from the Custom View Builder.
 * @collaboration Backend CRUD, audit receipts, tenant persistence, and frontend Custom View Builder.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function createLeadViewHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const view = await createLeadView(req.body || {}, context);
    return sendLeadViewSuccess(res, { statusCode: 201, view });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

/**
 * @function updateLeadViewHandler
 * @description Updates a saved Lead view.
 * @collaboration Backend CRUD, audit updates, view ownership, and tenant records.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function updateLeadViewHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const view = await updateLeadView(req.params.viewId, req.body || {}, context);

    if (!view) {
      return sendLeadViewError(res, new Error('Lead view not found'), 404);
    }

    return sendLeadViewSuccess(res, { view });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

/**
 * @function archiveLeadViewHandler
 * @description Archives a saved Lead view without deleting audit history.
 * @collaboration Backend CRUD, audit retention, custom view lifecycle, and compliance evidence.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function archiveLeadViewHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const view = await archiveLeadView(req.params.viewId, context);

    if (!view) {
      return sendLeadViewError(res, new Error('Lead view not found'), 404);
    }

    return sendLeadViewSuccess(res, { view });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

/**
 * @function runLeadViewHandler
 * @description Runs a saved Lead view against live backend Leads.
 * @collaboration Wilsy AI, analytics, view execution, audit receipts, and live counts.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function runLeadViewHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const result = await runLeadView(req.params.viewId, context);

    if (!result) {
      return sendLeadViewError(res, new Error('Lead view not found'), 404);
    }

    return sendLeadViewSuccess(res, result);
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

/**
 * @function previewLeadViewHandler
 * @description Previews unsaved Lead view criteria against live backend Leads.
 * @collaboration Custom View Builder live preview, audit-safe criteria tuning, and backend counts.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function previewLeadViewHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const preview = await previewLeadViewCriteria(req.body || {}, context);
    return sendLeadViewSuccess(res, { preview });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

/**
 * @function explainLeadCategoriesHandler
 * @description Returns live built-in Lead category counts.
 * @collaboration View Organizer, Wilsy AI questions, category explainability, and backend truth.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} Express response.
 */
async function explainLeadCategoriesHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const summary = await explainLeadCategories(context);
    return sendLeadViewSuccess(res, { summary });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

router.get('/', listLeadViews);
router.post('/', createLeadViewHandler);
router.patch('/:viewId', updateLeadViewHandler);
router.delete('/:viewId', archiveLeadViewHandler);
router.post('/preview', previewLeadViewHandler);
router.get('/categories/summary', explainLeadCategoriesHandler);
router.post('/:viewId/run', runLeadViewHandler);

module.exports = router;
