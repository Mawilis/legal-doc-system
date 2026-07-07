/* eslint-disable */
import express from 'express';
import {
  clearLeadViewMembershipOverride,
  excludeLeadViewMembers,
  includeLeadViewMembers,
  listLeadViewMembershipOverrides,
  archiveLeadView,
  createLeadView,
  explainLeadCategories,
  listTenantLeadViews,
  previewLeadViewCriteria,
  resolveRequestContext,
  runLeadView,
  updateLeadView,
} from '../services/crmLeadViewRegistryService.js';

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
 * @description Executes a saved Lead view and returns cursor-paginated effective rows.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Lead View Registry run endpoint, cursor pagination, frontend hydration, membership summary, and institutional evidence.
 */
async function runLeadViewHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const result = await runLeadView(req.params.viewId, context, req.body || {});

    if (!result) {
      return res.status(404).json({ ok: false, success: false, error: 'LEAD_VIEW_NOT_FOUND' });
    }

    return res.status(200).json({
      ok: true,
      success: true,
      ...result,
      run: result.result,
      rows: result.result?.rows || [],
      records: result.result?.records || [],
      leads: result.result?.leads || [],
      pagination: result.result?.pagination || null,
      nextCursor: result.result?.nextCursor || '',
      previousCursor: result.result?.previousCursor || '',
    });
  } catch (error) {
    return sendLeadViewError(res, error);
  }
}

// P60K5Q10FG103T_RUN_ROUTE_CURSOR_RESPONSE

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

/**
 * @function listLeadViewMembershipOverridesHandler
 * @description Lists manual include/exclude overrides for a saved Lead view.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} Response promise.
 * @collaboration View Membership Engine, selected-row controls, audit evidence, and backend collection state.
 */
async function listLeadViewMembershipOverridesHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const result = await listLeadViewMembershipOverrides(req.params.viewId, context);

    res.status(200).json({
      ok: true,
      success: true,
      ...result,
    });
  } catch (error) {
    sendError(res, error);
  }
}

/**
 * @function includeLeadViewMembersHandler
 * @description Adds selected leads to a saved Lead view as manual include overrides.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} Response promise.
 * @collaboration View Membership Engine, selected rows, signed requests, and audit receipts.
 */
async function includeLeadViewMembersHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const result = await includeLeadViewMembers(req.params.viewId, req.body, context);

    if (!result) {
      return res.status(404).json({ ok: false, success: false, error: 'LEAD_VIEW_NOT_FOUND' });
    }

    return res.status(200).json({
      ok: true,
      success: true,
      ...result,
    });
  } catch (error) {
    return sendError(res, error);
  }
}

/**
 * @function excludeLeadViewMembersHandler
 * @description Removes selected leads from a saved Lead view as manual exclude overrides.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} Response promise.
 * @collaboration View Membership Engine, selected rows, signed requests, and audit receipts.
 */
async function excludeLeadViewMembersHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const result = await excludeLeadViewMembers(req.params.viewId, req.body, context);

    if (!result) {
      return res.status(404).json({ ok: false, success: false, error: 'LEAD_VIEW_NOT_FOUND' });
    }

    return res.status(200).json({
      ok: true,
      success: true,
      ...result,
    });
  } catch (error) {
    return sendError(res, error);
  }
}

/**
 * @function clearLeadViewMembershipOverrideHandler
 * @description Clears a manual include/exclude override for a saved Lead view.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<void>} Response promise.
 * @collaboration Override cleanup, selected-row correction, audit receipts, and live view membership.
 */
async function clearLeadViewMembershipOverrideHandler(req, res) {
  try {
    const context = resolveRequestContext(req);
    const result = await clearLeadViewMembershipOverride(
      req.params.viewId,
      req.params.leadId,
      context
    );

    if (!result) {
      return res.status(404).json({ ok: false, success: false, error: 'LEAD_VIEW_NOT_FOUND' });
    }

    return res.status(200).json({
      ok: true,
      success: true,
      ...result,
    });
  } catch (error) {
    return sendError(res, error);
  }
}

// P60K5Q10FG103B_VIEW_MEMBERSHIP_ROUTE_HANDLERS

router.get('/', listLeadViews);
router.post('/query', listLeadViews); // P60K5Q10FG98F_AUDITED_READ_COMMANDS
router.post('/list', listLeadViews); // P60K5Q10FG98F_AUDITED_READ_COMMANDS
router.post('/', createLeadViewHandler);
router.patch('/:viewId', updateLeadViewHandler);
router.delete('/:viewId', archiveLeadViewHandler);
router.post('/preview', previewLeadViewHandler);
router.get('/categories/summary', explainLeadCategoriesHandler);
router.post('/categories/summary', explainLeadCategoriesHandler); // P60K5Q10FG98F_AUDITED_READ_COMMANDS
router.get('/:viewId/overrides', listLeadViewMembershipOverridesHandler); // P60K5Q10FG103B_VIEW_MEMBERSHIP_ROUTES
router.post('/:viewId/overrides/include', includeLeadViewMembersHandler); // P60K5Q10FG103B_VIEW_MEMBERSHIP_ROUTES
router.post('/:viewId/overrides/exclude', excludeLeadViewMembersHandler); // P60K5Q10FG103B_VIEW_MEMBERSHIP_ROUTES
router.delete('/:viewId/overrides/:leadId', clearLeadViewMembershipOverrideHandler); // P60K5Q10FG103B_VIEW_MEMBERSHIP_ROUTES
router.post('/:viewId/run', runLeadViewHandler);

export default router;
