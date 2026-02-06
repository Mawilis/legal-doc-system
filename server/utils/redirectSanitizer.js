/**
 * File: server/utils/redirectSanitizer.js
 * PATH: server/utils/redirectSanitizer.js
 * STATUS: EPITOME | DEFENSE-IN-DEPTH
 * VERSION: 1.0.0
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - Centralized redirect sanitizer to prevent open-redirects and XSS via
 *   untrusted redirect targets.
 * - Use this helper everywhere the app accepts a "redirect" / "next" / "returnTo"
 *   parameter from the client (login callbacks, OAuth, SSO, post-actions).
 *
 * GUIDELINES
 * - Place this file under server/utils so it's discoverable and reusable.
 * - Always call isSafeRedirect() before redirecting to a user-supplied target.
 * - Prefer allowlistHosts over permissive checks.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { URL } = require('url');

/**
 * isSafeRedirect(target, originHost, allowlistHosts)
 * - target: string (user-supplied redirect target)
 * - originHost: string (your app's canonical host, e.g., 'app.example.com')
 * - allowlistHosts: array of hostnames explicitly allowed (e.g., ['accounts.example.com'])
 *
 * Returns: boolean (true if safe)
 */
function isSafeRedirect(target, originHost, allowlistHosts = []) {
    if (!target || typeof target !== 'string') return false;

    // Trim whitespace and normalize
    const t = target.trim();

    // 1) Allow internal absolute paths (e.g., /dashboard, /app/doc/123)
    if (t.startsWith('/')) return true;

    // 2) Disallow suspicious schemes outright
    const lower = t.toLowerCase();
    if (lower.startsWith('javascript:') || lower.startsWith('data:') || lower.startsWith('vbscript:')) {
        return false;
    }

    // 3) Parse absolute URLs and validate host + protocol
    try {
        const u = new URL(t);

        // Only allow http(s)
        if (u.protocol !== 'http:' && u.protocol !== 'https:') return false;

        // Normalize hostnames for comparison
        const hostname = u.hostname.toLowerCase();
        const origin = (originHost || '').toLowerCase();

        // Allow if hostname matches originHost or is in allowlistHosts
        if (hostname === origin) return true;
        if (Array.isArray(allowlistHosts) && allowlistHosts.map(h => h.toLowerCase()).includes(hostname)) return true;

        return false;
    } catch (e) {
        // If URL parsing fails, treat as unsafe
        return false;
    }
}

/**
 * sanitizeRedirect(target, options)
 * - Returns a safe redirect string: either the original target (if safe) or a safeDefault.
 *
 * options:
 *   - originHost: string (required for absolute URL checks)
 *   - allowlistHosts: array
 *   - safeDefault: string (defaults to '/')
 */
function sanitizeRedirect(target, options = {}) {
    const { originHost = '', allowlistHosts = [], safeDefault = '/' } = options;
    if (isSafeRedirect(target, originHost, allowlistHosts)) {
        // Normalize internal paths to ensure they start with '/'
        const t = String(target).trim();
        if (t.startsWith('/')) return t;
        // For absolute URLs, return the full URL (caller should still consider using a relative path)
        return t;
    }
    return safeDefault;
}

/**
 * expressRedirectGuard(paramName, opts)
 * - Returns Express middleware that validates a redirect parameter (query or body).
 * - If invalid, it replaces the param with opts.safeDefault and continues.
 *
 * Usage:
 *   router.get('/auth/callback', expressRedirectGuard('returnTo', opts), handler);
 */
function expressRedirectGuard(paramName = 'redirect', opts = {}) {
    return (req, res, next) => {
        try {
            const originHost = opts.originHost || req.headers.host || '';
            const allowlistHosts = opts.allowlistHosts || [];
            const safeDefault = opts.safeDefault || '/';

            // Look in query then body
            const raw = req.query[paramName] || req.body && req.body[paramName];
            const safe = sanitizeRedirect(raw, { originHost, allowlistHosts, safeDefault });

            // Normalize: set in both places so downstream code sees the sanitized value
            if (req.query && typeof req.query === 'object') req.query[paramName] = safe;
            if (req.body && typeof req.body === 'object') req.body[paramName] = safe;

            // Also attach to req.context for explicit usage
            req.context = req.context || {};
            req.context.sanitizedRedirect = safe;

            next();
        } catch (err) {
            // Fail-safe: set safe default and continue
            if (req.query && typeof req.query === 'object') req.query[paramName] = opts.safeDefault || '/';
            if (req.body && typeof req.body === 'object') req.body[paramName] = opts.safeDefault || '/';
            req.context = req.context || {};
            req.context.sanitizedRedirect = opts.safeDefault || '/';
            next();
        }
    };
}

module.exports = {
    isSafeRedirect,
    sanitizeRedirect,
    expressRedirectGuard
};
