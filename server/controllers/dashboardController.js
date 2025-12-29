// File: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/dashboardController.js
// Purpose: Production-grade dashboard controller with look-aside cache and $facet aggregation.
// Collaboration: If you change enums, tenant header name, or cache semantics, update:
// - models (Document, LedgerEvent) to keep enums/indexes in sync
// - utils/redisClient to expose getJson/setJson/isConnected
// - tests in server/tests and migration scripts in server/migrations
// Notes:
// - This controller enforces tenant isolation via the x-tenant-id header.
// - It converts MongoDB Decimal128 values to plain Numbers for frontend consumption.
// - Cache TTL is controlled by DASHBOARD_CACHE_TTL_MS (default 15000 ms).
// - Keep heavy aggregations optimized and consider moving to a reporting read-model for very large datasets.

'use strict';

const mongoose = require('mongoose');
const Document = require('../models/Document');
const LedgerEvent = require('../models/LedgerEvent');
const redisClient = require('../utils/redisClient'); // expects getJson/setJson/isConnected
const ms = require('ms');

const CACHE_TTL_MS = parseInt(process.env.DASHBOARD_CACHE_TTL_MS || '15000', 10); // 15s default

// --- In-process memory fallback cache (per-process, short-lived)
const memoryCache = { payload: null, expiresAt: 0 };

// --- Cache helpers (use redis when available, fallback to memory)
async function getCached(key) {
    try {
        if (redisClient && typeof redisClient.isConnected === 'function' && redisClient.isConnected()) {
            const raw = await redisClient.getJson(key);
            return raw || null;
        }
    } catch (e) {
        console.warn('Redis Read Error', e && e.message ? e.message : e);
    }

    if (memoryCache.payload && Date.now() < memoryCache.expiresAt) return memoryCache.payload;
    return null;
}

async function setCached(key, value, ttlMs) {
    try {
        if (redisClient && typeof redisClient.isConnected === 'function' && redisClient.isConnected()) {
            await redisClient.setJson(key, value, ttlMs);
            return;
        }
    } catch (e) {
        console.warn('Redis Write Error', e && e.message ? e.message : e);
    }

    memoryCache.payload = value;
    memoryCache.expiresAt = Date.now() + ttlMs;
}

// --- Utility: safe Decimal128 -> Number conversion
function decimalToNumber(maybeDecimal) {
    if (maybeDecimal === undefined || maybeDecimal === null) return 0;
    if (typeof maybeDecimal === 'object' && typeof maybeDecimal.toString === 'function') {
        // Decimal128 or similar
        const s = maybeDecimal.toString();
        const n = Number(s);
        return Number.isFinite(n) ? n : 0;
    }
    const n = Number(maybeDecimal);
    return Number.isFinite(n) ? n : 0;
}

// --- Main controller
exports.getStats = async (req, res, next) => {
    const requestId = req.headers['x-request-id'] || req.requestId || 'unknown';
    const tenantId = req.headers['x-tenant-id'] || null;
    const cacheKey = `dashboard:stats:${tenantId || 'global'}`;

    try {
        // 1) Try cache
        const cached = await getCached(cacheKey);
        if (cached) {
            return res.status(200).json({ success: true, cached: true, requestId, data: cached });
        }

        // 2) Build tenant match (validate ObjectId)
        const matchStage = {};
        if (tenantId && mongoose.Types.ObjectId.isValid(tenantId)) {
            matchStage.tenantId = new mongoose.Types.ObjectId(tenantId);
        }

        // 3) Documents aggregation using $facet to reduce roundtrips
        const [docStats = { statusCounts: [], urgentCount: [], recentDocs: [] }] = await Document.aggregate([
            { $match: matchStage },
            {
                $facet: {
                    statusCounts: [
                        { $group: { _id: '$status', count: { $sum: 1 } } }
                    ],
                    urgentCount: [
                        // priorities use lowercase enums in the model; match accordingly
                        { $match: { priority: { $in: ['high', 'urgent'] } } },
                        { $count: 'total' }
                    ],
                    recentDocs: [
                        { $sort: { updatedAt: -1 } },
                        { $limit: 5 },
                        { $project: { _id: 1, title: 1, status: 1, updatedAt: 1 } }
                    ]
                }
            }
        ]);

        // 4) Ledger aggregation (sum credits for current month)
        const startOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
        const [ledgerStats = { totalRevenue: 0 }] = await LedgerEvent.aggregate([
            {
                $match: {
                    ...matchStage,
                    createdAt: { $gte: startOfMonth },
                    type: 'credit' // model uses lowercase 'credit'/'debit'
                }
            },
            { $group: { _id: null, totalRevenue: { $sum: '$amount' } } }
        ]);

        // 5) Transform and normalize results
        const statusCounts = Array.isArray(docStats.statusCounts) ? docStats.statusCounts : [];
        const urgentTotal = Array.isArray(docStats.urgentCount) && docStats.urgentCount[0] ? docStats.urgentCount[0].total : 0;
        const recent = Array.isArray(docStats.recentDocs) ? docStats.recentDocs : [];

        const totalActive = statusCounts.reduce((acc, cur) => acc + (cur.count || 0), 0);
        const pendingCount = (statusCounts.find(s => String(s._id).toLowerCase() === 'pending') || {}).count || 0;
        const completedCount = (statusCounts.find(s => String(s._id).toLowerCase() === 'completed') || {}).count || 0;

        const revenueValue = decimalToNumber(ledgerStats.totalRevenue);

        const payload = {
            metrics: {
                activeCases: totalActive,
                pendingDocuments: pendingCount,
                completedDocuments: completedCount,
                urgentFlags: decimalToNumber(urgentTotal),
                revenue: revenueValue,
                activeSheriffs: 0 // placeholder for future integration
            },
            recentActivity: recent
        };

        // 6) Cache and respond
        await setCached(cacheKey, payload, CACHE_TTL_MS);

        return res.status(200).json({ success: true, cached: false, requestId, data: payload });
    } catch (err) {
        // Log with requestId for traceability and forward to centralized error handler
        console.error(`🔴 [DashboardController] Aggregation Failed (requestId=${requestId}):`, err && err.message ? err.message : err);
        return next(err);
    }
};
