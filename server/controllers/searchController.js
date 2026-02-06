/*
 * File: server/controllers/searchController.js
 * STATUS: PRODUCTION-READY | UNIVERSAL DISCOVERY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The platform's high-speed discovery engine. Provides a unified search 
 * interface across Cases, Clients, and Documents while strictly enforcing 
 * the Iron Wall of tenant isolation.
 * -----------------------------------------------------------------------------
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Client = require('../models/Client');
const Case = require('../models/Case');
const Document = require('../models/Document');
const { successResponse, errorResponse } = require('../middleware/responseHandler');
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    GLOBAL UNIFIED SEARCH
 * @route   GET /api/v1/search
 */
exports.globalSearch = asyncHandler(async (req, res) => {
    const { q, limit = 10 } = req.query;

    if (!q || q.length < 2) {
        return successResponse(req, res, { clients: [], cases: [], documents: [] });
    }

    const searchLimit = Math.min(parseInt(limit), 50);
    const searchRegex = { $regex: q, $options: 'i' };
    const filter = { ...req.tenantFilter };

    // PARALLEL DISCOVERY: Query all primary legal entities simultaneously
    const [clients, cases, documents] = await Promise.all([
        // 1. Search Clients by Name or Email
        Client.find({
            ...filter,
            $or: [{ name: searchRegex }, { email: searchRegex }]
        }).limit(searchLimit).select('name email type').lean(),

        // 2. Search Cases by Number or Reference
        Case.find({
            ...filter,
            $or: [{ caseNumber: searchRegex }, { clientReference: searchRegex }, { title: searchRegex }]
        }).limit(searchLimit).select('caseNumber title status').lean(),

        // 3. Search Documents by Title or Code
        Document.find({
            ...filter,
            $or: [{ title: searchRegex }, { documentCode: searchRegex }]
        }).limit(searchLimit).select('title documentCode status').lean()
    ]);

    // FORENSIC AUDIT (Track Discovery Behavior)
    await emitAudit(req, {
        resource: 'SEARCH_ENGINE',
        action: 'GLOBAL_DISCOVERY_QUERY',
        severity: 'INFO',
        metadata: {
            query: q,
            resultCounts: {
                clients: clients.length,
                cases: cases.length,
                documents: documents.length
            }
        }
    });

    return successResponse(req, res, {
        query: q,
        results: {
            clients,
            cases,
            documents
        }
    });
});

/**
 * @desc    ADVANCED DOCUMENT DISCOVERY
 * @route   GET /api/v1/search/documents
 */
exports.searchDocuments = asyncHandler(async (req, res) => {
    const { q, status, type } = req.query;

    const query = {
        ...req.tenantFilter,
        $or: [
            { title: { $regex: q, $options: 'i' } },
            { documentCode: { $regex: q, $options: 'i' } }
        ]
    };

    if (status) query.status = status;
    if (type) query.type = type;

    const documents = await Document.find(query)
        .sort({ updatedAt: -1 })
        .limit(100)
        .lean();

    return successResponse(req, res, documents);
});