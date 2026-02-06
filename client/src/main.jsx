/**
 * File: client/src/main.jsx
 * PATH: client/src/main.jsx
 * STATUS: GENESIS | EPITOME | PRODUCTION-READY
 * VERSION: 10.0.0 (The Singularity)
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - The "Big Bang" of the Wilsy OS.
 * - Orchestrates the React DOM Injection.
 * - Initializes the "Neural Link" (AuditService) without blocking the UI thread.
 * - Establishes Global Panic Handlers for absolute fault tolerance.
 *
 * ARCHITECTURAL HIGHLIGHTS
 * 1. NON-BLOCKING HYDRATION: Uses 'requestIdleCallback' to init heavy services
 * only after the UI is interactive. Lawyers wait for nothing.
 * 2. GLOBAL PANIC TRAP: Catches runtime errors that occur before React mounts.
 * 3. ENV-AGNOSTIC: Runs safely in Docker, Local, or hardened Intranets.
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - FRONTEND: @frontend-team (Performance budgets)
 * - SECURITY: @security (CSP & Telemetry headers)
 * - SRE: @sre (Browser-side observability)
 *
 * "For the code is law, and the execution is justice."
 * -----------------------------------------------------------------------------
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Core Services
import AuditService from './features/auth/services/AuditService';
import useAuthStore from './store/authStore';
import ErrorBoundary from './components/common/ErrorBoundary';

/* -------------------------------------------------------------------------- */
/* 1. GLOBAL PANIC HANDLER (The Safety Net)                                   */
/* -------------------------------------------------------------------------- */
// Captures errors that happen before React even wakes up.
if (typeof window !== 'undefined') {
    window.onerror = function (message, source, lineno, colno, error) {
        // Log to console for dev visibility
        console.error('🔥 [CRITICAL BOOT FAILURE]:', message, source, lineno);

        // In production, we would beacon this to Sentry/AuditService manually here
        // preventing the "Silent Death" of the application.
        return false;
    };
}

/* -------------------------------------------------------------------------- */
/* 2. ENVIRONMENT DETECTION (The Radar)                                       */
/* -------------------------------------------------------------------------- */

/**
 * detectRuntimeEnvironment
 * - Determines if we are in Dev, Prod, or a Staging simulation.
 * - Uses a fail-safe eval approach to avoid bundler compilation errors on legacy systems.
 */
function detectRuntimeEnvironment() {
    try {
        // Modern Vite/Webpack injection
        // eslint-disable-next-line no-eval
        const meta = eval('typeof import !== "undefined" && import.meta ? import.meta : undefined');
        if (meta && meta.env && meta.env.MODE) return String(meta.env.MODE);
    } catch (e) { /* Fallback */ }

    try {
        // Node compatibility layer
        if (typeof process !== 'undefined' && process.env && process.env.NODE_ENV) {
            return String(process.env.NODE_ENV);
        }
    } catch (e) { /* Fallback */ }

    return 'development'; // Default safety
}

const ENV = detectRuntimeEnvironment();
const IS_PROD = ENV === 'production';

/* -------------------------------------------------------------------------- */
/* 3. ROOT DISCOVERY (The Anchor)                                             */
/* -------------------------------------------------------------------------- */

const rootElement = document.getElementById('root');
if (!rootElement) {
    const errorMsg = "CRITICAL: 'root' element missing. The OS has nowhere to mount.";
    console.error(errorMsg);
    document.body.innerHTML = `<div style="color: red; padding: 20px; font-family: monospace;"><h1>SYSTEM HALT</h1><p>${errorMsg}</p></div>`;
    throw new Error(errorMsg);
}

/* -------------------------------------------------------------------------- */
/* 4. BACKGROUND SERVICE HYDRATION (The Neural Link)                          */
/* -------------------------------------------------------------------------- */

/**
 * igniteTelemetry
 * - Initializes the Audit Service.
 * - Uses 'requestIdleCallback' to ensure this runs ONLY when the CPU is free.
 * - This guarantees the UI paints instantly, while security loads in the background.
 */
function igniteTelemetry() {
    try {
        // 1. Dynamic Tenant Resolution
        const resolveTenant = () => {
            try {
                const state = useAuthStore.getState();
                if (state.user?.tenantId) return state.user.tenantId;
                return localStorage.getItem('tenantId');
            } catch { return null; }
        };

        // 2. Dynamic Auth Header Injection
        const resolveAuth = async () => {
            try {
                const state = useAuthStore.getState();
                // Prefer Store (Memory) over LocalStorage (Disk) for speed
                if (state.token) return { Authorization: `Bearer ${state.token}` };

                const diskToken = localStorage.getItem('token');
                return diskToken ? { Authorization: `Bearer ${diskToken}` } : {};
            } catch { return {}; }
        };

        // 3. Initialize The Ledger
        AuditService.init({
            endpoint: '/api/audits',
            batchSize: IS_PROD ? 20 : 5,      // Larger batches in prod to save bandwidth
            batchIntervalMs: IS_PROD ? 5000 : 2000,
            maxRetries: 5,
            retryBaseMs: 500,
            tenantId: resolveTenant(),
            getAuthHeaders: resolveAuth,
            env: ENV,
            keepalive: true,   // Ensures logs survive tab close
            useIndexedDB: true, // Offline persistence
            enableConsoleFallback: !IS_PROD
        });

        // 4. Attach Visibility Hooks (Dev Only)
        if (!IS_PROD) {
            AuditService.setHook('onSend', (b) => console.debug(`📡 [TELEM] Uploading ${b.length} events...`));
            AuditService.setHook('onError', (e) => console.warn(`⚠️ [TELEM] Upload failed:`, e));
        }

        console.info(`%c 🛡️ WILSY OS TELEMETRY: ACTIVE [${ENV}]`, 'color: #00ff00; background: #000; padding: 4px;');

    } catch (err) {
        console.error('Telemetery Ignition Failed:', err);
    }
}

// EXECUTE: Schedule Telemetry for the next idle moment
const idleCallback = window.requestIdleCallback || ((cb) => setTimeout(cb, 1000));
idleCallback(igniteTelemetry);

/* -------------------------------------------------------------------------- */
/* 5. GRACEFUL SHUTDOWN (The Black Box)                                       */
/* -------------------------------------------------------------------------- */
// Ensures that if a user closes the tab, pending logs are flushed to the server.
if (typeof window !== 'undefined') {
    const flightRecorder = () => {
        if (AuditService && typeof AuditService.flush === 'function') {
            // Uses 'navigator.sendBeacon' internally for reliable unload requests
            AuditService.flush().catch(e => console.warn('Flush failed', e));
        }
    };
    window.addEventListener('beforeunload', flightRecorder);
    window.addEventListener('pagehide', flightRecorder); // Mobile Safari support
}

/* -------------------------------------------------------------------------- */
/* 6. REACT MOUNTING (The Big Bang)                                           */
/* -------------------------------------------------------------------------- */

const root = ReactDOM.createRoot(rootElement);

// Boot Message
if (!IS_PROD) {
    console.log(
        `%c WILSY OS v10.0.0 %c Booting... `,
        'background:#35495e ; padding: 1px; border-radius: 3px 0 0 3px;  color: #fff',
        'background:#41b883 ; padding: 1px; border-radius: 0 3px 3px 0;  color: #fff'
    );
}

root.render(
    <React.StrictMode>
        {/* ErrorBoundary prevents the entire OS from crashing due to one UI component */}
        <ErrorBoundary fallback={<div>System Error. Please refresh.</div>}>
            <App />
        </ErrorBoundary>
    </React.StrictMode>
);

/* -------------------------------------------------------------------------- */
/* DEV DIAGNOSTICS                                                            */
/* -------------------------------------------------------------------------- */
if (!IS_PROD && typeof window !== 'undefined') {
    window.__WILSY_DEBUG__ = {
        AuditService,
        AuthStore: useAuthStore
    };
}