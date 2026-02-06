/**
 * File: server/services/__mocks__/virusScanService.js
 * STATUS: PRODUCTION-READY | TEST MOCK | EPITOME
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Lightweight, deterministic mock for virus/AV scanning used in Jest tests.
 * - Simulates ClamAV/third-party scanner behavior without external dependencies.
 * - Deterministic rules: file content markers drive outcomes (see rules below).
 * - Supports configurable test hooks: artificial delay, forced outcomes, and error simulation.
 * - Returns a stable result shape used by workers and services.
 *
 * RULES (deterministic):
 * - If file contains the string "infected" (case-insensitive) => { status: 'infected' }
 * - If file contains the string "error-scan" => simulate scanner error (throws)
 * - If file contains the string "slow-scan" => respects configured delay (useful for timeouts)
 * - Otherwise => { status: 'clean' }
 *
 * USAGE IN TESTS:
 * - jest will auto-mock this file when placed under server/services/__mocks__.
 * - Tests can call `setBehavior({ delayMs, forceStatus, throwOnScan })` to override defaults.
 * - After each test, call `resetBehavior()` to restore defaults.
 *
 * RETURN SHAPE:
 * {
 *   status: 'clean' | 'infected' | 'error',
 *   details: string | null,
 *   engine: 'mock',
 *   durationMs: number
 * }
 *
 * NOTES:
 * - This mock intentionally avoids external binaries and network calls.
 * - Keep logic simple and deterministic so tests are reliable and fast.
 * -----------------------------------------------------------------------------
 */

'use strict';

const fs = require('fs');
const path = require('path');

let behavior = {
    delayMs: 0,          // artificial delay to simulate slow scans
    forceStatus: null,   // 'clean' | 'infected' | 'error' to force outcome
    throwOnScan: false   // if true, throw an error to simulate scanner crash
};

/**
 * setBehavior
 * Test helper to configure mock behavior.
 */
function setBehavior(opts = {}) {
    behavior = Object.assign({}, behavior, opts);
}

/**
 * resetBehavior
 * Restore default behavior.
 */
function resetBehavior() {
    behavior = { delayMs: 0, forceStatus: null, throwOnScan: false };
}

/**
 * safeReadFileUtf8
 * Attempts to read file as UTF-8 text; falls back to binary-to-hex string for non-text files.
 */
function safeReadFileUtf8(localPath) {
    try {
        return fs.readFileSync(localPath, 'utf8');
    } catch (e) {
        // Fallback: read as buffer and return hex snippet for deterministic checks
        try {
            const buf = fs.readFileSync(localPath);
            return buf.toString('hex').slice(0, 512); // small deterministic snippet
        } catch (err) {
            // If even this fails, rethrow original error
            throw e;
        }
    }
}

/**
 * scanFile
 * Main mock scanner function.
 *
 * @param {string} localPath - path to local file to scan
 * @returns {Promise<Object>} scan result
 */
async function scanFile(localPath) {
    const start = Date.now();

    // Basic validation
    if (!localPath || typeof localPath !== 'string') {
        const err = new Error('scanFile requires a valid localPath string');
        err.code = 'INVALID_ARG';
        throw err;
    }

    // Simulate configured scanner crash
    if (behavior.throwOnScan) {
        const err = new Error('Simulated scanner crash (throwOnScan)');
        err.code = 'SIMULATED_CRASH';
        throw err;
    }

    // Read file content deterministically
    let content;
    try {
        content = safeReadFileUtf8(localPath);
    } catch (e) {
        const err = new Error(`Failed to read file for scanning: ${e && e.message ? e.message : e}`);
        err.code = 'READ_ERROR';
        throw err;
    }

    // Respect artificial delay if configured or file marker present
    const hasSlowMarker = typeof content === 'string' && /slow-scan/i.test(content);
    const delayMs = Math.max(0, behavior.delayMs || 0) + (hasSlowMarker ? 200 : 0);
    if (delayMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
    }

    // If forced status is set by test, return it immediately
    if (behavior.forceStatus) {
        const forced = behavior.forceStatus;
        const durationMs = Date.now() - start;
        if (forced === 'infected') {
            return { status: 'infected', details: 'forced-infected', engine: 'mock', durationMs };
        }
        if (forced === 'error') {
            return { status: 'error', details: 'forced-error', engine: 'mock', durationMs };
        }
        return { status: 'clean', details: 'forced-clean', engine: 'mock', durationMs };
    }

    // Deterministic content-based rules
    const lower = String(content).toLowerCase();

    // Explicit error marker in file content
    if (lower.includes('error-scan')) {
        const durationMs = Date.now() - start;
        return { status: 'error', details: 'simulated-scan-error-marker', engine: 'mock', durationMs };
    }

    // Infected marker
    if (lower.includes('infected')) {
        const durationMs = Date.now() - start;
        return { status: 'infected', details: 'test-signature-match', engine: 'mock', durationMs };
    }

    // Default: clean
    const durationMs = Date.now() - start;
    return { status: 'clean', details: null, engine: 'mock', durationMs };
}

/* Export the mock API */
module.exports = {
    scanFile,
    // Test helpers
    setBehavior,
    resetBehavior,
    // Expose current behavior for assertions in tests
    _behavior: () => Object.assign({}, behavior)
};
