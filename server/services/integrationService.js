/**
 * File: server/services/integrationService.js
 * STATUS: PRODUCTION-READY | EPITOME | INTEGRATION ORCHESTRATOR
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Load provider integration configuration by combining DB entries with
 *   environment-injected secrets or KMS references.
 * - Ensure secrets are never stored in plaintext in DB; prefer env or KMS.
 * - Provide caching, cache invalidation, health checks, and audit hooks.
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @security, @sre, @compliance, @product
 * - SECURITY:
 *   * Do not persist plaintext secrets in DB. Use KMS or environment variables.
 *   * Access to KMS and environment must be restricted to service accounts.
 * - OPERATIONS:
 *   * Rotate secrets via KMS and call invalidateCache after rotation.
 *   * Monitor integration health and lastHealthCheckAt in Integration model.
 * - TESTING:
 *   * Add unit tests for env overrides, KMS resolution, and cache invalidation.
 * -----------------------------------------------------------------------------
 */

'use strict';

const Integration = require('../models/integrationModel');
const AuditEvent = require('../models/auditEventModel');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');

// Optional KMS resolver. Provide a concrete implementation in production.
// Expected API: resolveSecret(reference) => Promise<string|null>
let KMS = null;
try { KMS = require('../services/kmsService'); } catch (e) { KMS = null; }

// In-memory cache for provider configs
const cache = {
    map: new Map(), // provider -> { value, ts }
    ttlMs: parseInt(process.env.INTEGRATION_CACHE_TTL_MS || '5000', 10)
};

/**
 * invalidateCache
 * Clears cached provider config for a specific provider or all providers.
 */
function invalidateCache(provider = null) {
    if (provider) {
        cache.map.delete(String(provider).toUpperCase());
        logger.info('integrationService: cache invalidated for provider', { provider });
    } else {
        cache.map.clear();
        logger.info('integrationService: full cache invalidated');
    }
}

/**
 * safeResolveSecret
 * Resolves a secret value from environment or KMS reference.
 * - If envVar is provided and non-empty, returns it.
 * - If secretRef looks like a KMS reference (e.g., 'kms://...') and KMS is available, resolves it.
 * - Returns null if nothing found.
 */
async function safeResolveSecret(envVarValue, secretRef) {
    if (envVarValue) return envVarValue;
    if (!secretRef) return null;

    // If secretRef is a plain value but DB should not contain plaintext secrets.
    // Treat anything starting with 'kms://' as a KMS reference.
    if (typeof secretRef === 'string' && secretRef.startsWith('kms://')) {
        if (!KMS || typeof KMS.resolveSecret !== 'function') {
            logger.warn('integrationService: KMS resolver not configured but secretRef provided', { secretRef });
            return null;
        }
        try {
            const resolved = await KMS.resolveSecret(secretRef);
            return resolved || null;
        } catch (e) {
            logger.warn('integrationService: KMS resolve failed', { secretRef, err: e && e.message ? e.message : e });
            return null;
        }
    }

    // If secretRef is present but not a KMS ref, do not return it (avoid plaintext secrets).
    logger.warn('integrationService: plaintext secretRef detected in DB; ignoring for security', { secretRef });
    return null;
}

/**
 * mergeCredentials
 * Merge DB credentials with environment overrides and KMS resolution.
 * - baseCreds: object or array of [key,value] pairs from DB
 * - provider: canonical provider key used to look up env vars
 */
async function mergeCredentials(baseCreds = {}, provider) {
    // Normalize baseCreds to object
    let credsObj = {};
    if (Array.isArray(baseCreds)) {
        // support array of pairs or entries
        try {
            credsObj = Object.fromEntries(baseCreds);
        } catch (e) {
            // fallback: iterate
            credsObj = {};
            for (const entry of baseCreds) {
                if (Array.isArray(entry) && entry.length >= 2) credsObj[String(entry[0])] = entry[1];
                else if (entry && typeof entry === 'object' && entry.key) credsObj[String(entry.key)] = entry.value;
            }
        }
    } else if (baseCreds && typeof baseCreds === 'object') {
        credsObj = Object.assign({}, baseCreds);
    }

    // Environment prefix
    const prefix = `INTEGRATION_${String(provider).toUpperCase()}_`;

    // Known credential keys to check for env overrides
    const knownKeys = new Set(Object.keys(credsObj).concat(['API_KEY', 'API_SECRET', 'TOKEN', 'CLIENT_ID', 'CLIENT_SECRET']));

    // Resolve each credential: env -> KMS ref -> DB value (only if non-secret)
    const resolved = {};
    for (const key of knownKeys) {
        const envKey = `${prefix}${String(key).toUpperCase()}`;
        const envVal = process.env[envKey] || null;
        const dbVal = credsObj[key] || credsObj[String(key).toLowerCase()] || null;

        // If dbVal looks like an object with { secretRef } support that shape
        let secretRef = null;
        if (dbVal && typeof dbVal === 'object' && dbVal.secretRef) secretRef = dbVal.secretRef;
        else if (dbVal && typeof dbVal === 'string' && dbVal.startsWith('kms://')) secretRef = dbVal;

        const final = await safeResolveSecret(envVal, secretRef) || (typeof dbVal === 'string' ? dbVal : null);
        if (final !== null) resolved[key] = final;
    }

    return resolved;
}

/**
 * buildConfigObject
 * Normalize config entries stored as array of pairs or object.
 */
function buildConfigObject(rawConfig) {
    if (!rawConfig) return {};
    if (Array.isArray(rawConfig)) {
        try {
            return Object.fromEntries(rawConfig);
        } catch (e) {
            const out = {};
            for (const entry of rawConfig) {
                if (Array.isArray(entry) && entry.length >= 2) out[String(entry[0])] = entry[1];
                else if (entry && typeof entry === 'object' && entry.key) out[String(entry.key)] = entry.value;
            }
            return out;
        }
    }
    if (typeof rawConfig === 'object') return Object.assign({}, rawConfig);
    return {};
}

/**
 * getProviderConfig
 * Returns effective provider config combining DB entries and environment/KMS secrets.
 * Caches result for cache TTL.
 */
async function getProviderConfig(provider) {
    if (!provider) throw new Error('provider is required');

    const key = String(provider).toUpperCase();
    const now = Date.now();
    const cached = cache.map.get(key);
    if (cached && (now - cached.ts) < cache.ttlMs) {
        return cached.value;
    }

    // Load base config from DB
    let base;
    try {
        base = await Integration.findOne({ provider: key, enabled: true }).lean();
    } catch (e) {
        logger.error('integrationService: DB lookup failed', { provider: key, err: e && e.message ? e.message : e });
        return null;
    }
    if (!base) return null;

    // Merge credentials with env/KMS
    let credentials = {};
    try {
        credentials = await mergeCredentials(base.credentials || {}, key);
    } catch (e) {
        logger.warn('integrationService: credential merge failed', { provider: key, err: e && e.message ? e.message : e });
    }

    // Build config object
    const config = buildConfigObject(base.config || {});

    const result = {
        provider: base.provider,
        name: base.name,
        enabled: !!base.enabled,
        credentials,
        config,
        scopes: base.scopes || [],
        health: { status: base.lastHealthStatus || 'unknown', at: base.lastHealthCheckAt || null },
        raw: base // include raw DB doc for advanced callers (do not expose secrets)
    };

    // Cache and return
    cache.map.set(key, { value: result, ts: Date.now() });
    return result;
}

/**
 * listProviders
 * Returns a list of enabled providers with minimal metadata.
 */
async function listProviders({ enabledOnly = true } = {}) {
    const q = enabledOnly ? { enabled: true } : {};
    const docs = await Integration.find(q).select('provider name enabled lastHealthStatus lastHealthCheckAt').lean();
    return docs || [];
}

/**
 * healthCheck
 * Lightweight health check for integrations subsystem.
 */
async function healthCheck() {
    // Check DB connectivity by counting integrations (fast)
    try {
        const count = await Integration.estimatedDocumentCount();
        return { ok: true, integrations: count };
    } catch (e) {
        logger.error('integrationService.healthCheck failed', { err: e && e.message ? e.message : e });
        return { ok: false, error: e && e.message ? e.message : String(e) };
    }
}

/**
 * emitIntegrationAudit
 * Best-effort audit writer for integration operations.
 */
async function emitIntegrationAudit({ actor = null, actorEmail = null, actorRole = null, eventType = 'INTEGRATION_ACCESS', severity = 'INFO', summary = '', metadata = {} } = {}) {
    try {
        if (AuditEvent && typeof AuditEvent.create === 'function') {
            await AuditEvent.create({
                _id: uuidv4(),
                timestamp: new Date().toISOString(),
                actor,
                actorEmail,
                actorRole,
                eventType,
                severity,
                summary,
                metadata
            });
        }
    } catch (e) {
        logger.warn('integrationService: audit write failed', { err: e && e.message ? e.message : e, eventType });
    }
}

/* -------------------------
   Exports
   ------------------------- */

module.exports = {
    getProviderConfig,
    listProviders,
    healthCheck,
    invalidateCache,
    emitIntegrationAudit,
    // Expose internals for testing
    _internals: {
        safeResolveSecret,
        mergeCredentials,
        buildConfigObject,
        cache
    }
};
