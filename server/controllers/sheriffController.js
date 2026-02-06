/*
 * File: server/controllers/sheriffController.js
 * STATUS: EPITOME | LOGISTICS & GEOSPATIAL GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Manages field assets (Sheriffs). Governs real-time GPS tracking, 
 * proximity-based dispatch, and service performance analytics.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - LOGISTICS-TEAM: High-frequency GPS updates (updateLocation) are indexed.
 * - SECURITY: All field actions are forensically recorded for court affidavits.
 * - ARCHITECT: Uses MongoDB 2dsphere for proximity ($near) operations.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Sheriff = require('../models/Sheriff');
const Document = require('../models/Document');
const { successResponse, errorResponse } = require('../middleware/responseHandler');

/**
 * @desc    INITIALIZE SHERIFF PROFILE
 * @route   POST /api/v1/sheriffs
 * @access  Private/Admin
 */
exports.createSheriff = asyncHandler(async (req, res) => {
    const { userId, badgeNumber } = req.body;

    if (!userId) {
        return errorResponse(req, res, 400, 'A valid UserId is required for profile linkage.', 'ERR_USER_ID_REQUIRED');
    }

    // Anchor the sheriff to the current firm's sovereignty
    const sheriff = await Sheriff.create({
        ...req.body,
        tenantId: req.user.tenantId,
        stats: { attemptsMade: 0, documentsServed: 0 }
    });

    // Forensic Audit: Resource Creation
    await req.logAudit({
        resource: 'LOGISTICS',
        action: 'CREATE_SHERIFF',
        severity: 'INFO',
        metadata: { sheriffId: sheriff._id, badgeNumber }
    });

    return successResponse(req, res, sheriff, { message: 'Sheriff field profile initialized.' }, 201);
});

/**
 * @desc    GPS PULSE (Real-Time Location Update)
 * @route   PATCH /api/v1/sheriffs/:id/location
 * @access  Private/Sheriff
 */
exports.updateLocation = asyncHandler(async (req, res) => {
    const { lng, lat, isOnline } = req.body;

    if (typeof lng !== 'number' || typeof lat !== 'number') {
        return errorResponse(req, res, 400, 'Valid numeric GPS coordinates are required.', 'ERR_INVALID_GPS');
    }

    const sheriff = await Sheriff.findOneAndUpdate(
        { _id: req.params.id, tenantId: req.user.tenantId },
        {
            $set: {
                currentLocation: {
                    type: 'Point',
                    coordinates: [lng, lat],
                    updatedAt: new Date()
                },
                ...(typeof isOnline === 'boolean' ? { isOnline } : {})
            }
        },
        { new: true, runValidators: true }
    );

    if (!sheriff) {
        return errorResponse(req, res, 404, 'Sheriff profile not found in current scope.', 'ERR_SHERIFF_NOT_FOUND');
    }

    return successResponse(req, res, {
        isOnline: sheriff.isOnline,
        coordinates: sheriff.currentLocation.coordinates,
        updatedAt: sheriff.currentLocation.updatedAt
    });
});

/**
 * @desc    PROXIMITY SEARCH (Nearest Online Sheriffs)
 * @route   GET /api/v1/sheriffs/nearest
 * @access  Private/Lawyer/Admin
 */
exports.findNearest = asyncHandler(async (req, res) => {
    const lng = parseFloat(req.query.lng);
    const lat = parseFloat(req.query.lat);
    const radiusKm = parseFloat(req.query.radiusKm || '15');

    if (isNaN(lng) || isNaN(lat)) {
        return errorResponse(req, res, 400, 'Valid lng/lat query parameters required.', 'ERR_COORD_MISSING');
    }

    // High-performance proximity search within Tenant boundaries
    const sheriffs = await Sheriff.find({
        tenantId: req.user.tenantId,
        isOnline: true,
        status: 'ACTIVE',
        currentLocation: {
            $near: {
                $geometry: { type: 'Point', coordinates: [lng, lat] },
                $maxDistance: radiusKm * 1000 // Km to Meters
            }
        }
    })
        .select('badgeNumber vehicleReg currentLocation stats isOnline')
        .lean();

    return successResponse(req, res, sheriffs, { results: sheriffs.length });
});

/**
 * @desc    MARK SERVICE COMPLETE (Performance Update)
 * @route   POST /api/v1/sheriffs/:id/served
 * @access  Private/Sheriff/Admin
 */
exports.markServed = asyncHandler(async (req, res) => {
    const { id } = req.params;
    const { documentId } = req.body;

    // 1. IDENTITY VERIFICATION
    const sheriff = await Sheriff.findOne({ _id: id, tenantId: req.user.tenantId });
    if (!sheriff) {
        return errorResponse(req, res, 404, 'Sheriff profile not found.', 'ERR_SHERIFF_NOT_FOUND');
    }

    // 2. ATOMIC DOCUMENT STATE TRANSITION
    const doc = await Document.findOneAndUpdate(
        { _id: documentId, tenantId: req.user.tenantId },
        {
            status: 'FINAL',
            'metadata.isServed': true,
            servedAt: new Date(),
            servedBy: id
        },
        { new: true }
    );

    if (!doc) {
        return errorResponse(req, res, 404, 'Target document not found in firm registry.', 'ERR_DOC_NOT_FOUND');
    }

    // 3. STATS RECONCILIATION
    // Increments the success metrics for the field agent
    sheriff.stats.documentsServed += 1;
    sheriff.stats.attemptsMade += 1;
    sheriff.stats.lastServiceAt = new Date();
    await sheriff.save();

    // Forensic Audit: Proof of Service
    await req.logAudit({
        resource: 'LEGAL_PROCESS',
        action: 'DOCUMENT_SERVED',
        severity: 'MEDIUM',
        metadata: { documentId, sheriffId: id, badge: sheriff.badgeNumber }
    });

    return successResponse(req, res, { stats: sheriff.stats }, { message: 'Service of process successfully recorded.' });
});

/**
 * @desc    LIST ALL FIELD AGENTS
 * @route   GET /api/v1/sheriffs
 * @access  Private/Admin
 */
exports.getAllSheriffs = asyncHandler(async (req, res) => {
    const { search, status } = req.query;
    const filter = { tenantId: req.user.tenantId };

    if (search) {
        filter.$or = [
            { badgeNumber: { $regex: search, $options: 'i' } },
            { jurisdictionNames: { $regex: search, $options: 'i' } }
        ];
    }

    if (status) filter.status = status;

    const items = await Sheriff.find(filter)
        .sort({ 'stats.documentsServed': -1 })
        .populate('userId', 'firstName lastName email')
        .lean();

    return successResponse(req, res, items, { results: items.length });
});

/**
 * @desc    UPDATE SHERIFF PROFILE (Admin Override)
 * @route   PATCH /api/v1/sheriffs/:id
 * @access  Private/Admin
 */
exports.updateSheriff = asyncHandler(async (req, res) => {
    const sheriff = await Sheriff.findOneAndUpdate(
        { _id: req.params.id, tenantId: req.user.tenantId },
        { $set: req.body },
        { new: true, runValidators: true }
    );

    if (!sheriff) {
        return errorResponse(req, res, 404, 'Sheriff profile not found.', 'ERR_SHERIFF_NOT_FOUND');
    }

    await req.logAudit({
        resource: 'LOGISTICS',
        action: 'UPDATE_SHERIFF',
        severity: 'INFO',
        metadata: { sheriffId: sheriff._id, updates: Object.keys(req.body) }
    });

    return successResponse(req, res, sheriff);
});