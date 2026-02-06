/*
 * File: server/controllers/settingsController.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Tenant Configuration Engine. Manages firm-wide rules and UI preferences.
 * AUTHOR: Wilsy Core Team
 * SECURITY: Strict Tenant Isolation. Audited Configuration Changes.
 */

'use strict';

const asyncHandler = require('express-async-handler');
const Tenant = require('../models/Tenant'); // Assuming settings live on Tenant or dedicated Settings model
const { emitAudit } = require('../middleware/auditMiddleware');

/**
 * @desc    Get Firm/Tenant Settings
 * @route   GET /api/settings
 * @access  Authenticated User
 */
exports.getSettings = asyncHandler(async (req, res) => {
    // We look up the tenant details which host the configuration
    const tenant = await Tenant.findById(req.user.tenantId).select('settings name plan status');

    if (!tenant) {
        res.status(404);
        throw new Error('Tenant settings not found.');
    }

    // Fallback to global system defaults if tenant settings are empty
    const settings = tenant.settings || {
        currency: 'ZAR',
        vatRate: 15,
        timezone: 'Africa/Johannesburg',
        dateFormat: 'YYYY/MM/DD'
    };

    res.status(200).json({
        status: 'success',
        data: {
            firmName: tenant.name,
            plan: tenant.plan,
            config: settings
        }
    });
});

/**
 * @desc    Update Firm/Tenant Settings
 * @route   PATCH /api/settings
 * @access  Admin Only
 */
exports.updateSettings = asyncHandler(async (req, res) => {
    const { settings } = req.body;

    if (!settings || typeof settings !== 'object') {
        res.status(400);
        throw new Error('Valid settings object is required.');
    }

    const tenant = await Tenant.findById(req.user.tenantId);

    if (!tenant) {
        res.status(404);
        throw new Error('Tenant record not found.');
    }

    // Capture old settings for the audit trail comparison
    const oldSettings = { ...tenant.settings };

    // Update settings using Mongoose dot notation or direct assignment
    tenant.settings = { ...tenant.settings, ...settings };
    await tenant.save();

    // 🚀 High-Severity Audit: Config changes affect the entire firm
    await emitAudit(req, {
        resource: 'system_settings',
        action: 'UPDATE_CONFIG',
        severity: 'WARN',
        summary: `Firm configuration updated for ${tenant.name}`,
        metadata: {
            changedKeys: Object.keys(settings),
            prevSettings: oldSettings,
            newSettings: tenant.settings
        }
    });

    res.status(200).json({
        status: 'success',
        message: 'Settings updated successfully',
        data: tenant.settings
    });
});

/**
 * @desc    Upload Firm Logo
 * @route   POST /api/settings/logo
 * @access  Admin Only
 */
exports.updateLogo = asyncHandler(async (req, res) => {
    const { logoUrl } = req.body;

    if (!logoUrl) {
        res.status(400);
        throw new Error('Logo URL is required.');
    }

    await Tenant.findByIdAndUpdate(req.user.tenantId, {
        'settings.logoUrl': logoUrl
    });

    res.status(200).json({
        status: 'success',
        message: 'Branding updated.'
    });
});

// Stubs to satisfy route dependencies if needed
exports.getAll = exports.getSettings;
exports.update = exports.updateSettings;