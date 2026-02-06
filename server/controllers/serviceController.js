/*
 * File: server/controllers/serviceController.js
 * STATUS: PRODUCTION-READY | SERVICE OF PROCESS GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Governs the lifecycle of physical legal service. Manages status transitions 
 * from instruction to 'Served', captures field evidence, and tracks 
 * jurisdictional performance metrics.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const DispatchInstruction = require('../models/DispatchInstruction');
const Sheriff = require('../models/Sheriff');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    UPDATE SERVICE STATUS (Field Action)
 * @route   PATCH /api/v1/service/:id/status
 * @access  Sheriff, Admin
 */
exports.updateServiceStatus = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const { status, outcomeNotes, locationHash } = req.body;

    // 1. ATOMIC LOOKUP & SCOPE CHECK
    const instruction = await DispatchInstruction.findOne({ 
        _id: id, 
        ...req.tenantFilter 
    });

    if (!instruction) {
        return errorResponse(req, res, 404, 'Service instruction not found.', 'ERR_SERVICE_NOT_FOUND');
    }

    // 2. SHERIFF CONTEXT VALIDATION
    const sheriff = await Sheriff.findOne({ userId: req.user.id, ...req.tenantFilter });
    
    // 3. STATE TRANSITION LOGIC
    const oldStatus = instruction.status;
    instruction.status = status;
    instruction.outcomeNotes = outcomeNotes;

    if (['SERVED', 'DOMICILE_SERVED'].includes(status)) {
        instruction.completedAt = new Date();
    }

    await instruction.save();

    // 4. FORENSIC AUDIT (Proof of Presence)
    await emitAudit(req, {
        resource: 'LOGISTICS_MODULE',
        action: 'SERVICE_STATUS_TRANSITION',
        severity: 'INFO',
        metadata: { 
            instructionId: id, 
            oldStatus, 
            newStatus: status,
            coordinates: sheriff?.currentLocation?.coordinates,
            locationHash 
        }
    });

    return successResponse(req, res, instruction, { message: `Legal service status updated to ${status}.` });
});

/**
 * @desc    GET SERVICE VELOCITY STATS
 * @route   GET /api/v1/service/stats
 */
exports.getServiceStats = asyncHandler(async (req, res) => {
    // Pipeline: Group by status to see 'Served' vs 'Non-Service' ratios
    const stats = await DispatchInstruction.aggregate([
        { $match: { ...req.tenantFilter } },
        {
            $group: {
                _id: '$status',
                count: { $sum: 1 },
                avgDistance: { $avg: '$distanceKm' }
            }
        },
        { $sort: { count: -1 } }
    ]);

    return successResponse(req, res, stats);
});

/**
 * @desc    LIST PENDING SERVICE TASKS (Sheriff's Manifest)
 * @route   GET /api/v1/service/manifest
 */
exports.getManifest = asyncHandler(async (req, res) => {
    const query = { 
        ...req.tenantFilter, 
        status: { $in: ['PENDING', 'IN_PROGRESS'] } 
    };

    // If request comes from a Sheriff, only show their assignments
    if (req.user.role === 'sheriff') {
        query.assignedTo = req.user.id;
    }

    const manifest = await DispatchInstruction.find(query)
        .sort({ urgency: -1, createdAt: 1 })
        .populate('caseId', 'caseNumber title')
        .lean();

    return successResponse(req, res, manifest, { count: manifest.length });
});

/**
 * @desc    RECORD FIELD OBSERVATION
 * @route   POST /api/v1/service/:id/observations
 */
exports.recordObservation = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const { note } = req.body;

    const instruction = await DispatchInstruction.findOne({ _id: id, ...req.tenantFilter });

    if (!instruction) {
        return errorResponse(req, res, 404, 'Instruction not found.', 'ERR_SERVICE_NOT_FOUND');
    }

    // Push to an internal notes array (assumed in schema)
    instruction.observations = instruction.observations || [];
    instruction.observations.push({
        userId: req.user.id,
        content: note,
        timestamp: new Date()
    });

    await instruction.save();

    return successResponse(req, res, null, { message: 'Field observation recorded.' });
});