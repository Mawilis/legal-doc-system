/*
 * File: server/controllers/courtController.js
 * STATUS: PRODUCTION-READY | JURISDICTIONAL GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages the national court registry. Provides data on jurisdictions, 
 * court levels (High, Regional, District), and physical seatings for 
 * filing and service of process.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Court = require('../models/Court'); // Assumes a Court model exists
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    LIST ALL COURTS (Searchable & Categorized)
 * @route   GET /api/v1/courts
 * @access  Private
 */
exports.getAll = asyncHandler(async (req, res) => {
    const { level, province, search } = req.query;

    const query = {};
    if (level) query.courtLevel = level; // e.g., 'HIGH', 'REGIONAL', 'DISTRICT'
    if (province) query.province = province;
    if (search) query.name = { $regex: search, $options: 'i' };

    const courts = await Court.find(query).sort({ name: 1 });

    return successResponse(req, res, courts, { results: courts.length });
});

/**
 * @desc    GET SINGLE COURT REGISTRY
 * @route   GET /api/v1/courts/:id
 */
exports.getOne = asyncHandler(async (req, res) => {
    const court = await Court.findById(req.params.id);

    if (!court) {
        return errorResponse(req, res, 404, 'Court seating not found in registry.', 'ERR_COURT_NOT_FOUND');
    }

    return successResponse(req, res, court);
});

/**
 * @desc    REGISTER NEW COURT SEATING
 * @route   POST /api/v1/courts
 * @access  SuperAdmin Only
 */
exports.create = asyncHandler(async (req, res) => {
    // Note: Only SuperAdmins should manage the global court list
    if (req.user.role !== 'super_admin') {
        return errorResponse(req, res, 403, 'System registry management restricted to SuperAdmins.', 'ERR_RBAC_FORBIDDEN');
    }

    const court = await Court.create(req.body);

    await emitAudit(req, {
        resource: 'COURT_REGISTRY',
        action: 'COURT_CREATED',
        severity: 'NOTICE',
        metadata: { courtId: court._id, name: court.name }
    });

    return successResponse(req, res, court, { message: 'New court seating registered.' }, 201);
});

/**
 * @desc    UPDATE COURT METADATA (Address/Jurisdiction)
 * @route   PATCH /api/v1/courts/:id
 * @access  SuperAdmin Only
 */
exports.update = asyncHandler(async (req, res) => {
    if (req.user.role !== 'super_admin') {
        return errorResponse(req, res, 403, 'System registry management restricted to SuperAdmins.', 'ERR_RBAC_FORBIDDEN');
    }

    const court = await Court.findByIdAndUpdate(req.params.id, req.body, {
        new: true,
        runValidators: true
    });

    if (!court) {
        return errorResponse(req, res, 404, 'Court record not found.', 'ERR_COURT_NOT_FOUND');
    }

    await emitAudit(req, {
        resource: 'COURT_REGISTRY',
        action: 'COURT_UPDATED',
        severity: 'NOTICE',
        metadata: { courtId: court._id }
    });

    return successResponse(req, res, court, { message: 'Court metadata successfully updated.' });
});

/**
 * @desc    REMOVE COURT SEATING
 * @route   DELETE /api/v1/courts/:id
 * @access  SuperAdmin Only
 */
exports.remove = asyncHandler(async (req, res) => {
    if (req.user.role !== 'super_admin') {
        return errorResponse(req, res, 403, 'System registry management restricted to SuperAdmins.', 'ERR_RBAC_FORBIDDEN');
    }

    const court = await Court.findByIdAndDelete(req.params.id);

    if (!court) {
        return errorResponse(req, res, 404, 'Court record not found.', 'ERR_COURT_NOT_FOUND');
    }

    await emitAudit(req, {
        resource: 'COURT_REGISTRY',
        action: 'COURT_DELETED',
        severity: 'WARNING',
        metadata: { courtName: court.name }
    });

    return successResponse(req, res, null, { message: 'Court record purged from registry.' });
});