/* eslint-env jest */
// File: /Users/wilsonkhanyezi/legal-doc-system/server/tests/dashboardController.test.js
'use strict';

const request = require('supertest');
const express = require('express');
const mongoose = require('mongoose');

describe('Dashboard Controller', () => {
    let Document;
    let LedgerEvent;
    let redisClient;
    let dashboardController;
    let app;

    beforeEach(() => {
        // Reset module registry so controller's in-memory cache is fresh each test
        jest.resetModules();

        // Recreate mocks and require modules after reset
        jest.mock('../models/Document', () => ({ aggregate: jest.fn() }));
        jest.mock('../models/LedgerEvent', () => ({ aggregate: jest.fn() }));
        jest.mock('../utils/redisClient', () => ({
            getJson: jest.fn(),
            setJson: jest.fn(),
            isConnected: jest.fn(() => false)
        }));

        // Now require the modules under test
        Document = require('../models/Document');
        LedgerEvent = require('../models/LedgerEvent');
        redisClient = require('../utils/redisClient');
        dashboardController = require('../controllers/dashboardController');

        // Create a fresh express app and mount the controller route
        app = express();
        app.use((req, res, next) => { req.requestId = 'test-id'; next(); });
        app.get('/api/dashboard', dashboardController.getStats);
    });

    afterEach(() => {
        jest.clearAllMocks();
        jest.resetAllMocks();
    });

    it('should return aggregated metrics correctly (cache miss)', async () => {
        Document.aggregate.mockResolvedValue([{
            statusCounts: [{ _id: 'Pending', count: 5 }],
            urgentCount: [{ total: 2 }],
            recentDocs: []
        }]);

        // Return Decimal128 to mirror production
        LedgerEvent.aggregate.mockResolvedValue([{ totalRevenue: mongoose.Types.Decimal128.fromString('5000') }]);

        // Ensure Redis reports disconnected for this test (use memory cache path)
        redisClient.isConnected.mockReturnValue(false);
        redisClient.getJson.mockResolvedValue(null);

        const res = await request(app).get('/api/dashboard');

        expect(res.status).toBe(200);
        expect(res.body.success).toBe(true);
        expect(res.body.data.metrics.pendingDocuments).toBe(5);
        expect(res.body.data.metrics.urgentFlags).toBe(2);
        expect(res.body.data.metrics.revenue).toBe(5000);
        expect(res.body.cached).toBe(false);
    });

    it('should return cached payload when cache hit', async () => {
        // Prepare a cached payload that differs from DB values to assert cache is used
        const cachedPayload = {
            metrics: { activeCases: 1, pendingDocuments: 1, completedDocuments: 0, urgentFlags: 0, revenue: 0, activeSheriffs: 0 },
            recentActivity: []
        };

        // Simulate Redis being connected and returning the cached payload
        redisClient.isConnected.mockReturnValue(true);
        redisClient.getJson.mockResolvedValue(cachedPayload);

        // Ensure DB aggregates would return different values if called (they should not be called)
        Document.aggregate.mockResolvedValue([{
            statusCounts: [{ _id: 'Pending', count: 5 }],
            urgentCount: [{ total: 2 }],
            recentDocs: []
        }]);
        LedgerEvent.aggregate.mockResolvedValue([{ totalRevenue: mongoose.Types.Decimal128.fromString('5000') }]);

        const res = await request(app).get('/api/dashboard');

        expect(res.status).toBe(200);
        expect(res.body.success).toBe(true);
        expect(res.body.cached).toBe(true);
        expect(res.body.data).toEqual(cachedPayload);

        // Ensure DB aggregates were not called when cache hit
        expect(Document.aggregate).not.toHaveBeenCalled();
        expect(LedgerEvent.aggregate).not.toHaveBeenCalled();
    });
});
