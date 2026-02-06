/*
 * File: server/controllers/dispatchController.js
 * STATUS: PRODUCTION-READY | LOGISTICS LIFECYCLE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages the dispatch of legal instructions to field agents. Governs 
 * assignments, status transitions, and final outcome recording.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Dispatch = require('../models/Dispatch');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    CREATE NEW SERVICE INSTRUCTION
 * @route   POST /api/v1/dispatches
 */
exports.createDispatch = asyncHandler(async (req, res) => {
  const { caseId, sheriffId, address, type, instructions } = req.body;

  // 1. ATOMIC CREATION
  const dispatch = await Dispatch.create({
    ...req.body,
    tenantId: req.user.tenantId,
    createdBy: req.user.id,
    assignedTo: sheriffId || null,
    status: 'PENDING'
  });

  // 2. FORENSIC AUDIT
  await emitAudit(req, {
    resource: 'LOGISTICS_MODULE',
    action: 'INSTRUCTION_CREATED',
    severity: 'INFO',
    metadata: { dispatchId: dispatch._id, type, caseId }
  });

  return successResponse(req, res, dispatch, { message: 'Dispatch instruction issued.' }, 201);
});

/**
 * @desc    GET DISPATCH BOARD (Paginated & Role-Filtered)
 * @route   GET /api/v1/dispatches
 */
exports.getAllDispatches = asyncHandler(async (req, res) => {
  const { status, urgency, page = 1, limit = 20 } = req.query;

  // 1. DYNAMIC QUERY BUILDING
  const query = { ...req.tenantFilter };

  if (status) query.status = status;
  if (urgency) query.urgency = urgency;

  // ROLE-BASED VISIBILITY: Sheriffs only see their own workload
  if (req.user.role === 'sheriff') {
    query.assignedTo = req.user.id;
  }

  // 2. EXECUTION
  const skip = (parseInt(page) - 1) * parseInt(limit);
  const dispatches = await Dispatch.find(query)
    .populate('assignedTo', 'name email')
    .populate('caseId', 'caseNumber clientReference')
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(parseInt(limit));

  const total = await Dispatch.countDocuments(query);

  return successResponse(req, res, dispatches, {
    pagination: {
      total,
      page: parseInt(page),
      pages: Math.ceil(total / parseInt(limit))
    }
  });
});

/**
 * @desc    GET DISPATCH DETAILS
 * @route   GET /api/v1/dispatches/:id
 */
exports.getDispatch = asyncHandler(async (req, res) => {
  const dispatch = await Dispatch.findOne({
    _id: req.params.id,
    ...req.tenantFilter
  })
    .populate('assignedTo', 'name phone')
    .populate('caseId', 'caseNumber opponent');

  if (!dispatch) {
    return errorResponse(req, res, 404, 'Dispatch instruction not found.', 'ERR_DISPATCH_NOT_FOUND');
  }

  return successResponse(req, res, dispatch);
});

/**
 * @desc    UPDATE STATUS / ASSIGNMENT
 * @route   PATCH /api/v1/dispatches/:id
 */
exports.updateDispatch = asyncHandler(async (req, res) => {
  const { status, assignedTo, outcomeNotes } = req.body;

  const dispatch = await Dispatch.findOne({ _id: req.params.id, ...req.tenantFilter });

  if (!dispatch) {
    return errorResponse(req, res, 404, 'Update failed: Dispatch record not found.', 'ERR_DISPATCH_NOT_FOUND');
  }

  // 1. SECURITY: Prevent field agents from reassigning tasks
  if (assignedTo && req.user.role === 'sheriff') {
    return errorResponse(req, res, 403, 'Permission denied: Field agents cannot reassign workload.', 'ERR_RBAC_FORBIDDEN');
  }

  // 2. APPLY UPDATES
  if (status) {
    dispatch.status = status;
    // Auto-timestamp completion
    if (['COMPLETED', 'SERVED', 'FAILED'].includes(status)) {
      dispatch.completedAt = new Date();
    }
  }

  if (assignedTo) dispatch.assignedTo = assignedTo;
  if (outcomeNotes) dispatch.outcomeNotes = outcomeNotes;

  await dispatch.save();

  // 3. AUDIT TRANSITION
  await emitAudit(req, {
    resource: 'LOGISTICS_MODULE',
    action: 'INSTRUCTION_UPDATED',
    severity: 'INFO',
    metadata: { dispatchId: dispatch._id, newStatus: status }
  });

  return successResponse(req, res, dispatch, { message: 'Dispatch record reconciled.' });
});

/**
 * @desc    CANCEL/PURGE DISPATCH
 * @route   DELETE /api/v1/dispatches/:id
 */
exports.deleteDispatch = asyncHandler(async (req, res) => {
  const dispatch = await Dispatch.findOne({ _id: req.params.id, ...req.tenantFilter });

  if (!dispatch) {
    return errorResponse(req, res, 404, 'Cancellation failed: Instruction not found.', 'ERR_DISPATCH_NOT_FOUND');
  }

  await Dispatch.deleteOne({ _id: dispatch._id });

  await emitAudit(req, {
    resource: 'LOGISTICS_MODULE',
    action: 'INSTRUCTION_CANCELLED',
    severity: 'WARN',
    metadata: { dispatchId: req.params.id }
  });

  return successResponse(req, res, null, { message: 'Dispatch instruction successfully cancelled.' });
});