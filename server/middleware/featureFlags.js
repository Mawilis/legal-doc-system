/**
 * File: server/middleware/featureFlags.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Progressive Delivery & Upsell Intelligence
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Controls access to Beta/Premium features via Tenant configuration.
 * - SALES INTEL: Logs 'Access Denied' events to identify upsell opportunities.
 * - SAFETY: Prevents system-wide crashes by isolating new code paths.
 * - FLEXIBILITY: Supports global overrides, per-tenant flags, percentage rollouts, and kill switches.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { emitAudit } = require('./auditMiddleware');

const features = {
    // Premium Features (Monetization Gates)
    AI_DRAFTING: 'ai_drafting_v1',
    BLOCKCHAIN_AUDIT: 'blockchain_ledger_v1',
    ADVANCED_ANALYTICS: 'analytics_pro',

    // Beta/System Features (Safety Gates)
    NEW_UI: 'ui_v2_beta',
    BILLING_V2: 'billing_engine_v2',
};

/**
 * Evaluate feature flag for a tenant
 * @param {string} flagName
 * @param {Object} tenant
 */
function evaluateFlag(flagName, tenant = {}) {
    const tenantFeatures = tenant.features || [];

    // Global override via environment variable
    const envKey = `ENABLE_${flagName.toUpperCase()}`;
    if (process.env[envKey] === 'true') return true;

    // Kill switch
    const killKey = `DISABLE_${flagName.toUpperCase()}`;
    if (process.env[killKey] === 'true') return false;

    // Tenant-specific enablement
    if (tenantFeatures.includes(flagName)) return true;

    // Percentage rollout (optional: e.g., ENABLE_AI_DRAFTING_PERCENT=20)
    const percentKey = `${envKey}_PERCENT`;
    if (process.env[percentKey]) {
        const pct = parseInt(process.env[percentKey], 10);
        if (!Number.isNaN(pct) && pct > 0) {
            const hash = [...String(tenant._id || tenant.name || '')].reduce((a, c) => a + c.charCodeAt(0), 0);
            return (hash % 100) < pct;
        }
    }

    return false;
}

/**
 * Middleware factory to check if a feature is enabled.
 * @param {string} flagName - The key from the features object.
 */
const checkFeature = (flagName) => {
    return async (req, res, next) => {
        const tenant = req.tenant || req.user?.tenant || {};
        const enabled = evaluateFlag(flagName, tenant);

        if (enabled) {
            await emitAudit(req, {
                resource: 'feature_flag',
                action: 'granted',
                severity: 'info',
                metadata: {
                    feature: flagName,
                    tenantId: tenant._id,
                    tenantName: tenant.name,
                    path: req.originalUrl,
                    method: req.method,
                },
            });
            return next();
        }

        // Sales intelligence logging
        console.warn(
            `💰 [Upsell Opportunity] Tenant '${tenant.name || tenant._id}' attempted to access locked feature: ${flagName}`
        );

        await emitAudit(req, {
            resource: 'feature_flag',
            action: 'denied',
            severity: 'warning',
            metadata: {
                feature: flagName,
                tenantId: tenant._id,
                tenantName: tenant.name,
                reason: 'Plan Upgrade Required',
                path: req.originalUrl,
                method: req.method,
            },
        });

        return res.status(403).json({
            success: false,
            status: 'error',
            code: 'FEATURE_LOCKED',
            message: `Feature '${flagName}' is not enabled for your subscription plan. Contact sales to upgrade.`,
            upgradeUrl: '/billing/upgrade',
            correlationId: req.correlationId || req.context?.correlationId,
        });
    };
};

module.exports = { features, checkFeature, evaluateFlag };



