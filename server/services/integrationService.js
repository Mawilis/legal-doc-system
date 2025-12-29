/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/services/integrationService.js
 *
 * Integration Service
 * -------------------
 * Loads provider configurations with environment-injected secrets or KMS references.
 */

const Integration = require('../models/integrationModel');

/**
 * getProviderConfig(provider)
 * - Returns effective provider config combining DB entries and environment variables.
 * - Secrets should be provided via env or KMS and NOT stored in plaintext in DB.
 */
exports.getProviderConfig = async (provider) => {
    const base = await Integration.findOne({ provider, enabled: true }).lean();
    if (!base) return null;

    const envPrefix = `INTEGRATION_${provider.toUpperCase()}_`;
    const envSecrets = {
        apiKey: process.env[`${envPrefix}API_KEY`] || null,
        apiSecret: process.env[`${envPrefix}API_SECRET`] || null,
    };

    return {
        provider: base.provider,
        name: base.name,
        enabled: base.enabled,
        credentials: { ...Object.fromEntries(base.credentials || []), ...envSecrets },
        config: Object.fromEntries(base.config || []),
        scopes: base.scopes || [],
        health: { status: base.lastHealthStatus, at: base.lastHealthCheckAt },
    };
};
