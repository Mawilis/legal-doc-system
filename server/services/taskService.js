/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/services/taskService.js
 *
 * Task Service
 * ------------
 * Enqueue, start, complete, and fail tasks with status tracking.
 */

const Task = require('../models/taskModel');

exports.enqueueTask = async ({ type, payload, priority = 5, correlationId, createdBy }) => {
    return Task.create({
        type,
        status: 'queued',
        payload,
        priority,
        correlationId,
        createdBy,
        queuedAt: new Date(),
    });
};

exports.startTask = async (taskId) => {
    return Task.findByIdAndUpdate(taskId, { status: 'running', startedAt: new Date() }, { new: true });
};

exports.completeTask = async (taskId, result = {}) => {
    return Task.findByIdAndUpdate(taskId, {
        status: 'completed',
        completedAt: new Date(),
        result,
    }, { new: true });
};

exports.failTask = async (taskId, errorMessage) => {
    return Task.findByIdAndUpdate(taskId, {
        status: 'failed',
        completedAt: new Date(),
        error: errorMessage,
    }, { new: true });
};


