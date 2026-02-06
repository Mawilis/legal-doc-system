/*
 * File: server/controllers/eventController.js
 * STATUS: PRODUCTION-READY | TEMPORAL INTEGRITY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * Governs the firm's calendar and deadline engine. Manages court dates, 
 * filing deadlines, and internal meetings with strict case-linkage validation.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Event = require('../models/Event');
const Case = require('../models/Case');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    SCHEDULE NEW EVENT / DEADLINE
 * @route   POST /api/v1/events
 */
exports.createEvent = asyncHandler(async (req, res) => {
    const { title, start, end, caseId, type } = req.body;

    // 1. DATE INTEGRITY VALIDATION
    if (new Date(end) <= new Date(start)) {
        return errorResponse(req, res, 400, 'Temporal Logic Failure: End time must occur after start time.', 'ERR_INVALID_DATES');
    }

    // 2. CASE SCOPE VALIDATION
    if (caseId) {
        const caseFile = await Case.findOne({ _id: caseId, ...req.tenantFilter });
        if (!caseFile) {
            return errorResponse(req, res, 404, 'The associated case matter was not found.', 'ERR_CASE_NOT_FOUND');
        }
    }

    // 3. ATOMIC CREATION
    const event = await Event.create({
        ...req.body,
        tenantId: req.user.tenantId,
        createdBy: req.user.id,
        participants: [req.user.id] // Auto-include organizer
    });

    // 4. FORENSIC AUDIT
    await emitAudit(req, {
        resource: 'CALENDAR_MODULE',
        action: 'EVENT_SCHEDULED',
        severity: type === 'COURT_DATE' ? 'NOTICE' : 'INFO',
        metadata: { eventId: event._id, type, start }
    });

    return successResponse(req, res, event, { message: 'Calendar event successfully registered.' }, 201);
});

/**
 * @desc    GET CALENDAR FEED (Range Filtered)
 * @route   GET /api/v1/events
 */
exports.getAllEvents = asyncHandler(async (req, res) => {
    const { start, end, caseId, type } = req.query;

    const query = { ...req.tenantFilter };

    // Standard Calendar Range Filter
    if (start && end) {
        query.start = { $gte: new Date(start), $lte: new Date(end) };
    }

    if (caseId) query.caseId = caseId;
    if (type) query.type = type;

    const events = await Event.find(query)
        .populate('caseId', 'caseNumber clientReference')
        .populate('createdBy', 'name email')
        .sort({ start: 1 });

    return successResponse(req, res, events, { results: events.length });
});

/**
 * @desc    GET SINGLE EVENT DETAILS
 * @route   GET /api/v1/events/:id
 */
exports.getEvent = asyncHandler(async (req, res) => {
    const event = await Event.findOne({
        _id: req.params.id,
        ...req.tenantFilter
    }).populate('caseId', 'caseNumber status');

    if (!event) {
        return errorResponse(req, res, 404, 'Event record not found.', 'ERR_EVENT_NOT_FOUND');
    }

    return successResponse(req, res, event);
});

/**
 * @desc    UPDATE SCHEDULED EVENT
 * @route   PATCH /api/v1/events/:id
 */
exports.updateEvent = asyncHandler(async (req, res) => {
    const event = await Event.findOne({ _id: req.params.id, ...req.tenantFilter });

    if (!event) {
        return errorResponse(req, res, 404, 'Update failed: Event not found.', 'ERR_EVENT_NOT_FOUND');
    }

    // Protect immutable fields
    delete req.body.tenantId;

    const updatedEvent = await Event.findByIdAndUpdate(
        req.params.id,
        req.body,
        { new: true, runValidators: true }
    );

    await emitAudit(req, {
        resource: 'CALENDAR_MODULE',
        action: 'EVENT_RESCHEDULED',
        severity: 'INFO',
        metadata: { eventId: event._id }
    });

    return successResponse(req, res, updatedEvent, { message: 'Calendar record updated.' });
});

/**
 * @desc    PURGE EVENT FROM CALENDAR
 * @route   DELETE /api/v1/events/:id
 */
exports.deleteEvent = asyncHandler(async (req, res) => {
    const event = await Event.findOne({ _id: req.params.id, ...req.tenantFilter });

    if (!event) {
        return errorResponse(req, res, 404, 'Deletion failed: Event not found.', 'ERR_EVENT_NOT_FOUND');
    }

    await Event.deleteOne({ _id: event._id });

    await emitAudit(req, {
        resource: 'CALENDAR_MODULE',
        action: 'EVENT_DELETED',
        severity: 'WARN',
        metadata: { eventTitle: event.title, eventType: event.type }
    });

    return successResponse(req, res, null, { message: 'Event successfully removed from firm calendar.' });
});