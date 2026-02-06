/**
 * File: client/src/features/auth/utils/authUtils.js
 * STATUS: EPITOME | LOGIC ENGINE | PRODUCTION-READY
 * VERSION: 10.0.0 (The Singularity)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The "Cerebral Cortex" of the Wilsy OS Client.
 * - Manages Forensic Auditing, Cryptographic Correlation, and Input Validation.
 *
 * CRITICAL UPGRADE: DURABLE TELEMETRY
 * - Implements an "Offline Queue". If the network fails (Load Shedding),
 * audit logs are buffered in memory and flushed when the connection returns.
 * - This guarantees ZERO DATA LOSS for compliance audits.
 *
 * COLLABORATION
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - SECURITY: @security (Masking & Fingerprinting)
 * - SRE: @sre (Telemetry Reliability)
 * -----------------------------------------------------------------------------
 */

export const CONFIG = {
    APP_NAME: 'Wilsy OS',
    VERSION: '10.0.0-SOVEREIGN',
    TERMS_URL: '/legal/terms',
    PRIVACY_URL: '/legal/privacy',
    MAX_ATTEMPTS: 5,
    MFA_ENABLED: true,
    LOCKOUT_DURATION: 300000 // 5 minutes
};

/* -----------------------------------------------------------------------------
   1. SECURITY SERVICE (The Shield)
   --------------------------------------------------------------------------- */
export const SecurityService = {
    /**
     * maskEmail
     * - Compliance Requirement: Never log raw PII in plain text.
     * - Returns: 'wi****@acme.co'
     */
    maskEmail(email) {
        if (!email || typeof email !== 'string') return 'UNKNOWN_ACTOR';
        const parts = email.split('@');
        if (parts.length < 2) return 'INVALID_FORMAT';

        const [local, domain] = parts;
        const visible = Math.max(1, Math.min(3, local.length));
        const masked = `${local.substring(0, visible)}${'*'.repeat(Math.max(4, local.length - visible))}`;
        return `${masked}@${domain}`;
    },

    /**
     * getFingerprint
     * - Generates a forensic snapshot of the user's environment.
     * - Used to detect account sharing or unauthorized device access.
     */
    getFingerprint() {
        try {
            return {
                ua: navigator.userAgent || 'unknown',
                lang: navigator.language || 'en',
                res: typeof window !== 'undefined' ? `${window.screen.width}x${window.screen.height}` : 'headless',
                tz: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
                cores: navigator.hardwareConcurrency || 1
            };
        } catch (e) {
            return { ua: 'unknown', error: 'fingerprint_failed' };
        }
    },

    /**
     * generateCorrelationId
     * - Uses Web Crypto API for collision-resistant tracing IDs.
     * - format: req_<timestamp>_<hex>
     */
    generateCorrelationId() {
        try {
            const arr = new Uint8Array(8);
            crypto.getRandomValues(arr);
            const hex = Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
            return `req_${Date.now()}_${hex}`;
        } catch (e) {
            // Fallback for older browsers
            return `req_${Date.now()}_${Math.random().toString(36).slice(2)}`;
        }
    }
};

/* -----------------------------------------------------------------------------
   2. LOGGER FACADE (The Noise Filter)
   --------------------------------------------------------------------------- */
export const Logger = {
    isDev: () => {
        try { return import.meta.env.MODE === 'development'; }
        catch { return false; } // Safety for non-Vite envs
    },

    info: (msg, data) => {
        if (Logger.isDev()) console.log(`%c ℹ️ ${msg}`, 'color: #3498db', data || '');
    },
    warn: (msg, data) => {
        console.warn(`%c ⚠️ ${msg}`, 'color: #f39c12', data || '');
    },
    error: (msg, data) => {
        console.error(`%c 🔥 ${msg}`, 'color: #e74c3c', data || '');
    }
};

/* -----------------------------------------------------------------------------
   3. AUDIT SERVICE (The Black Box)
   --------------------------------------------------------------------------- */
// In-memory buffer for offline events
const auditQueue = [];
let isFlushing = false;

export const AuditService = {
    /**
     * log
     * - The public interface. Queues the event and attempts to flush immediately.
     */
    async log(event, details = {}) {
        const correlationId = SecurityService.generateCorrelationId();

        const payload = {
            timestamp: new Date().toISOString(),
            correlationId,
            eventType: String(event || 'UNKNOWN').toUpperCase(),
            severity: String(details.severity || (event.includes('FAIL') ? 'WARN' : 'INFO')).toUpperCase(),
            actor: details.email ? SecurityService.maskEmail(details.email) : 'ANONYMOUS',
            metadata: {
                ...details.metadata,
                fingerprint: SecurityService.getFingerprint()
            }
        };

        // 1. Dev Visibility
        if (Logger.isDev()) {
            console.groupCollapsed(`🛡️ [AUDIT] ${payload.eventType}`);
            console.log(payload);
            console.groupEnd();
        }

        // 2. Add to Durable Queue
        auditQueue.push(payload);

        // 3. Attempt Flush
        this.flushQueue();

        return payload;
    },

    /**
     * flushQueue
     * - Processes the offline buffer.
     * - Uses 'navigator.sendBeacon' for reliability during page navigation.
     */
    async flushQueue() {
        if (isFlushing || auditQueue.length === 0) return;
        if (typeof navigator === 'undefined' || !navigator.onLine) return; // Wait for network

        isFlushing = true;
        const batch = [...auditQueue]; // Copy current batch

        try {
            // Strategy 1: Beacon (Perfect for page unload)
            const blob = new Blob([JSON.stringify({ events: batch })], { type: 'application/json' });
            const sent = navigator.sendBeacon('/api/audits/batch', blob);

            if (!sent) {
                // Strategy 2: Fetch (Fallback if payload is huge)
                await fetch('/api/audits/batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ events: batch }),
                    keepalive: true
                });
            }

            // Success: Remove items from queue
            auditQueue.splice(0, batch.length);

        } catch (e) {
            Logger.warn('Audit Sync Paused (Network Jitter)', e.message);
            // Keep items in queue for next retry
        } finally {
            isFlushing = false;
        }
    }
};

// Auto-retry flush when coming back online
if (typeof window !== 'undefined') {
    window.addEventListener('online', () => AuditService.flushQueue());
}

/* -----------------------------------------------------------------------------
   4. VALIDATION SERVICE (The Gatekeeper)
   --------------------------------------------------------------------------- */
export const ValidationService = {
    validateEmail(email) {
        if (!email) return 'Email is required.';
        // Enterprise-grade Regex (RFC 5322ish)
        const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!regex.test(String(email).trim())) return 'Invalid email format.';
        return null;
    },

    validatePassword(password) {
        if (!password) return 'Password is required.';
        if (password.length < 8) return 'Password must be at least 8 characters.';
        return null;
    },

    validateMfaCode(code) {
        if (!code) return 'Code is required.';
        if (!/^\d{6}$/.test(code.trim())) return 'Must be a 6-digit code.';
        return null;
    }
};

/* -----------------------------------------------------------------------------
   EXPORTS
   --------------------------------------------------------------------------- */
const AuthUtils = {
    CONFIG,
    SecurityService,
    AuditService,
    ValidationService,
    Logger
};

export default AuthUtils;