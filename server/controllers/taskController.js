/*
 * File: server/controllers/taskController.js
 * STATUS: PRODUCTION-READY | WORKFLOW OPERATIONAL GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Governs internal legal workflows. Manages task assignments, case-linked 
 * to-dos, and statutory deadline tracking with strict tenant isolation.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Task = require('../models/Task');
const Case = require('../models/Case');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    CREATE CASE-LINKED TASK
 * @route   POST /api/v1/tasks
 */
exports.createTask = asyncHandler(async (req, res) => {
    const { title, caseId, assignedTo, dueDate, priority } = req.body;

    // 1. CASE SCOPE VALIDATION
    if (caseId) {
        const caseExists = await Case.exists({ _id: caseId, ...req.tenantFilter });
        if (!caseExists) {
            return errorResponse(req, res, 404, 'The referenced case matter is invalid or inaccessible.', 'ERR_CASE_NOT_FOUND');
        }
    }

    // 2. ATOMIC CREATION
    const task = await Task.create({
        ...req.body,
        tenantId: req.user.tenantId,
        createdBy: req.user.id,
        status: 'PENDING'
    });

    // 3. AUDIT THE WORKFLOW INITIATION
    await emitAudit(req, {
        resource: 'WORKFLOW_MODULE',
        action: 'TASK_CREATED',
        severity: priority === 'URGENT' ? 'WARNING' : 'INFO',
        metadata: { taskId: task._id, caseId, assignedTo }
    });

    return successResponse(req, res, task, { message: 'Workflow task assigned.' }, 201);
});

/**
 * @desc    GET PERSONAL TASK MANIFEST (Paginated)
 * @route   GET /api/v1/tasks/my-tasks
 */
exports.getMyTasks = asyncHandler(async (req, res) => {
    const { status, page = 1, limit = 20 } = req.query;

    const query = {
        ...req.tenantFilter,
        assignedTo: req.user.id
    };

    if (status) query.status = status;

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const tasks = await Task.find(query)
        .populate('caseId', 'caseNumber title')
        .sort({ urgency: -1, dueDate: 1 })
        .skip(skip)
        .limit(parseInt(limit))
        .lean();

    const total = await Task.countDocuments(query);

    return successResponse(req, res, tasks, {
        pagination: { total, page: parseInt(page) }
    });
});

/**
 * @desc    UPDATE TASK STATUS (Workflow Progression)
 * @route   PATCH /api/v1/tasks/:id
 */
exports.updateTask = asyncHandler(async (req, res) => {
    const { status, progressNotes } = req.body;

    const task = await Task.findOne({ _id: req.params.id, ...req.tenantFilter });

    if (!task) {
        return errorResponse(req, res, 404, 'Task not found in firm records.', 'ERR_TASK_NOT_FOUND');
    }

    // 1. APPLY UPDATES
    if (status) {
        task.status = status;
        if (status === 'COMPLETED') task.completedAt = new Date();
    }

    if (progressNotes) {
        task.notes = task.notes || [];
        task.notes.push({ content: progressNotes, userId: req.user.id, at: new Date() });
    }

    await task.save();

    // 2. AUDIT STATUS CHANGE
    await emitAudit(req, {
        resource: 'WORKFLOW_MODULE',
        action: 'TASK_STATUS_UPDATED',
        severity: 'INFO',
        metadata: { taskId: task._id, newStatus: status }
    });

    return successResponse(req, res, task, { message: 'Task workflow updated.' });
});

/**
 * @desc    LIST ALL FIRM TASKS (Admin/Management View)
 * @route   GET /api/v1/tasks
 */
exports.getAllTasks = asyncHandler(async (req, res) => {
    const { caseId, assignedTo, status } = req.query;

    const query = { ...req.tenantFilter };
    if (caseId) query.caseId = caseId;
    if (assignedTo) query.assignedTo = assignedTo;
    if (status) query.status = status;

    const tasks = await Task.find(query)
        .populate('assignedTo', 'name email')
        .populate('caseId', 'caseNumber')
        .sort({ createdAt: -1 })
        .limit(100);

    return successResponse(req, res, tasks, { results: tasks.length });
});

/**
 * @desc    PURGE TASK
 * @route   DELETE /api/v1/tasks/:id
 */
exports.deleteTask = asyncHandler(async (req, res) => {
    const task = await Task.findOneAndDelete({ _id: req.params.id, ...req.tenantFilter });

    if (!task) {
        return errorResponse(req, res, 404, 'Task not found.', 'ERR_TASK_NOT_FOUND');
    }

    await emitAudit(req, {
        resource: 'WORKFLOW_MODULE',
        action: 'TASK_DELETED',
        severity: 'WARNING',
        metadata: { taskId: req.params.id, taskTitle: task.title }
    });

    return successResponse(req, res, null, { message: 'Task successfully removed.' });
});