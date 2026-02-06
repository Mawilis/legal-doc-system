/**
 * File: server/services/permissionService.js
 * STATUS: PRODUCTION-READY | EPITOME | PERMISSION ORCHESTRATOR
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Computes effective permissions for a user by combining role permissions,
 * inherited role permissions, and user-specific overrides (allow/deny).
 *
 * DESIGN:
 * - Normalizes permission strings for stable comparisons.
 * - Supports role inheritance via role.inherits = [roleId|roleKey].
 * - Supports user.permissionOverrides as:
 *     [{ permission: 'documents.read', action: 'allow'|'deny' }, ...]
 *   or simple strings (treated as allow).
 * - Caches role documents in-memory with TTL; provides explicit invalidation.
 * - Non-fatal: on DB errors returns best-effort result (empty array) and logs.
 *
 * USAGE:
 * const permissionService = require('../services/permissionService');
 * const perms = await permissionService.computeEffectivePermissions(user, { tenantId, logger });
 *
 * COLLABORATION:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @security
 * -----------------------------------------------------------------------------
 */

'use strict';

const Role = require('../models/roleModel');
const { v4: uuidv4 } = require('uuid');

// Simple structured logger fallback
const defaultLogger = {
    info: (...args) => console.info(...args),
    warn: (...args) => console.warn(...args),
    error: (...args) => console.error(...args)
};

// In-memory role cache: { key -> { role, ts } }
const roleCache = new Map();
const DEFAULT_TTL_MS = parseInt(process.env.PERMISSION_ROLE_CACHE_TTL_MS || '5000', 10);

/* -------------------------
   Helpers
   ------------------------- */

/**
 * normalizePermission
 * Ensures stable permission string representation
 */
function normalizePermission(p) {
    if (!p && p !== 0) return '';
    return String(p).trim().toLowerCase();
}

/**
 * normalizeOverride
 * Accepts either string or { permission, action } and returns normalized object
 */
function normalizeOverride(o) {
    if (!o) return null;
    if (typeof o === 'string') return { permission: normalizePermission(o), action: 'allow' };
    if (typeof o === 'object' && o.permission) {
        const action = (o.action || 'allow').toLowerCase();
        return { permission: normalizePermission(o.permission), action: action === 'deny' ? 'deny' : 'allow' };
    }
    return null;
}

/**
 * fetchRoleByIdOrKey
 * Loads a role by id or key and caches it.
 */
async function fetchRoleByIdOrKey(idOrKey, { ttl = DEFAULT_TTL_MS, logger = defaultLogger } = {}) {
    if (!idOrKey) return null;
    const cacheKey = String(idOrKey);
    const now = Date.now();
    const cached = roleCache.get(cacheKey);
    if (cached && (now - cached.ts) < ttl) return cached.role;

    try {
        // Try by _id first, then by key/name
        let role = null;
        if (/^[0-9a-fA-F]{24}$/.test(cacheKey)) {
            role = await Role.findById(cacheKey).lean().exec();
        }
        if (!role) {
            role = await Role.findOne({ $or: [{ key: cacheKey }, { name: cacheKey }] }).lean().exec();
        }
        if (role) {
            roleCache.set(cacheKey, { role, ts: Date.now() });
            // Also cache by role._id and role.key/name for faster subsequent lookups
            if (role._id) roleCache.set(String(role._id), { role, ts: Date.now() });
            if (role.key) roleCache.set(String(role.key), { role, ts: Date.now() });
        }
        return role;
    } catch (err) {
        logger.error('permissionService.fetchRoleByIdOrKey error', { idOrKey, err: err && err.message ? err.message : err });
        return null;
    }
}

/**
 * resolveRolePermissions
 * Recursively resolves role permissions including inherited roles.
 * Uses a visited set to avoid cycles.
 */
async function resolveRolePermissions(roleIdentifier, { ttl, logger } = {}, visited = new Set()) {
    const perms = new Set();
    if (!roleIdentifier) return perms;

    const role = await fetchRoleByIdOrKey(roleIdentifier, { ttl, logger });
    if (!role) return perms;

    const roleKey = String(role._id || role.key || uuidv4());
    if (visited.has(roleKey)) return perms;
    visited.add(roleKey);

    // Add role permissions
    if (Array.isArray(role.permissions)) {
        role.permissions.forEach((p) => {
            const np = normalizePermission(p);
            if (np) perms.add(np);
        });
    }

    // Resolve inherited roles (supports array of ids/keys)
    if (Array.isArray(role.inherits) && role.inherits.length) {
        for (const parent of role.inherits) {
            const parentPerms = await resolveRolePermissions(parent, { ttl, logger }, visited);
            parentPerms.forEach((pp) => perms.add(pp));
        }
    }

    return perms;
}

/* -------------------------
   Public API
   ------------------------- */

/**
 * computeEffectivePermissions
 * Computes effective permissions for a user.
 *
 * @param {Object} user - user object. Accepts:
 *   - user.roleId or user.role (id or key)
 *   - user.permissionOverrides: array of strings or { permission, action }
 * @param {Object} opts - optional:
 *   - ttl: cache TTL for role lookups (ms)
 *   - logger: structured logger
 *   - includeRolePermissions: boolean (default true)
 * @returns {Promise<string[]>} sorted array of permission strings
 */
async function computeEffectivePermissions(user = {}, opts = {}) {
    const { ttl = DEFAULT_TTL_MS, logger = defaultLogger, includeRolePermissions = true } = opts || {};
    const perms = new Set();

    try {
        // 1) Role-based permissions (including inheritance)
        if (includeRolePermissions) {
            const roleIdentifier = user.roleId || user.role || user.roleKey || null;
            if (roleIdentifier) {
                const rolePerms = await resolveRolePermissions(roleIdentifier, { ttl, logger });
                rolePerms.forEach((p) => perms.add(p));
            }
        }

        // 2) User-level overrides
        if (Array.isArray(user.permissionOverrides)) {
            for (const raw of user.permissionOverrides) {
                const ov = normalizeOverride(raw);
                if (!ov || !ov.permission) continue;
                if (ov.action === 'allow') {
                    perms.add(ov.permission);
                } else if (ov.action === 'deny') {
                    // Deny removes permission if present
                    if (perms.has(ov.permission)) perms.delete(ov.permission);
                    // Also mark a negative permission to ensure it stays denied even if inherited later
                    // We'll track denies in a separate set to ensure final result respects denies
                }
            }
        }

        // 3) If user has explicit denies represented as objects with action 'deny',
        //    ensure denies are applied even if inherited later. For simplicity, re-apply:
        if (Array.isArray(user.permissionOverrides)) {
            for (const raw of user.permissionOverrides) {
                const ov = normalizeOverride(raw);
                if (!ov || !ov.permission) continue;
                if (ov.action === 'deny') {
                    if (perms.has(ov.permission)) perms.delete(ov.permission);
                }
            }
        }

        // 4) Return sorted array
        return Array.from(perms).sort();
    } catch (err) {
        logger.error('permissionService.computeEffectivePermissions failed', { err: err && err.message ? err.message : err, userId: user._id || user.id || null });
        // Fail-safe: return empty array (no permissions) to avoid accidental privilege escalation
        return [];
    }
}

/**
 * preloadRoles
 * Bulk-loads a set of roles into cache to warm it (useful at startup).
 * Accepts array of role ids or keys.
 */
async function preloadRoles(roleIdentifiers = [], opts = {}) {
    const { ttl = DEFAULT_TTL_MS, logger = defaultLogger } = opts || {};
    if (!Array.isArray(roleIdentifiers) || roleIdentifiers.length === 0) return 0;
    let count = 0;
    for (const id of roleIdentifiers) {
        const r = await fetchRoleByIdOrKey(id, { ttl, logger });
        if (r) count += 1;
    }
    return count;
}

/**
 * invalidateCache
 * Clears in-memory role cache (call after role updates).
 */
function invalidateCache() {
    roleCache.clear();
}

/* -------------------------
   Exports
   ------------------------- */

module.exports = {
    computeEffectivePermissions,
    preloadRoles,
    invalidateCache,
    // Expose internals for testing
    _internals: {
        normalizePermission,
        normalizeOverride,
        fetchRoleByIdOrKey,
        resolveRolePermissions,
        roleCache
    }
};
