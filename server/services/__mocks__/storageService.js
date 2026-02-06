/**
 * File: server/services/__mocks__/storageService.js
 * STATUS: PRODUCTION-READY | TEST MOCK | EPITOME
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Lightweight, deterministic mock for S3/Blob storage used in unit tests.
 * - Avoids network calls and credentials.
 * - Simulates download (streamToTemp), upload (uploadFromLocal), and temp-path detection.
 * - Supports configurable behavior for latency, forced failures, and custom mappings.
 * - Safe file operations with clear errors for test assertions.
 * -----------------------------------------------------------------------------
 */

'use strict';

const fs = require('fs');
const fsp = fs.promises;
const os = require('os');
const path = require('path');

let behavior = {
    delayMs: 0,            // artificial delay for stream/upload operations
    failOnStream: false,   // if true, streamToTemp will throw
    failOnUpload: false,   // if true, uploadFromLocal will throw
    mapping: {},           // optional map: storageKey -> localPath (for tests)
    preserveTemp: false    // if true, do not auto-clean temp files (useful for debugging)
};

/**
 * setBehavior
 * Configure mock behavior for tests.
 */
function setBehavior(opts = {}) {
    behavior = Object.assign({}, behavior, opts);
}

/**
 * resetBehavior
 * Restore default behavior.
 */
function resetBehavior() {
    behavior = { delayMs: 0, failOnStream: false, failOnUpload: false, mapping: {}, preserveTemp: false };
}

/**
 * safeTempPath
 * Generates a unique temp path under OS temp dir.
 */
function safeTempPath(prefix = 'wilsy-test') {
    const name = `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    return path.join(os.tmpdir(), name);
}

/**
 * isLocalPath
 * Heuristic to detect local filesystem paths.
 */
function isLocalPath(p) {
    if (!p || typeof p !== 'string') return false;
    return p.startsWith('/') || p.startsWith('./') || /^[A-Za-z]:\\/.test(p);
}

/**
 * streamToTemp
 * Simulates downloading a file from remote storage to a local temp path.
 * If storageKey is already a local path, returns it directly (no copy).
 * Honors behavior.mapping to resolve virtual keys to local files.
 */
async function streamToTemp(storageKey) {
    if (!storageKey || typeof storageKey !== 'string') {
        const err = new Error('streamToTemp requires a storageKey string');
        err.code = 'INVALID_ARG';
        throw err;
    }

    if (behavior.failOnStream) {
        const err = new Error('Simulated stream failure (failOnStream)');
        err.code = 'SIMULATED_STREAM_FAIL';
        throw err;
    }

    // Artificial delay for realism
    if (behavior.delayMs && behavior.delayMs > 0) {
        await new Promise((r) => setTimeout(r, behavior.delayMs));
    }

    // If mapping exists, use mapped local file as source
    if (behavior.mapping && behavior.mapping[storageKey]) {
        const mapped = behavior.mapping[storageKey];
        if (!isLocalPath(mapped)) {
            const err = new Error('Mapped storageKey must point to a local path');
            err.code = 'MAPPING_INVALID';
            throw err;
        }
        // Copy to temp to simulate download
        const tmp = safeTempPath('wilsy-mapped');
        await fsp.copyFile(mapped, tmp);
        return tmp;
    }

    // If storageKey already local, return as-is (caller should be careful)
    if (isLocalPath(storageKey)) {
        // Validate file exists
        try {
            const st = await fsp.stat(storageKey);
            if (!st.isFile()) throw new Error('Not a file');
            return storageKey;
        } catch (e) {
            const err = new Error(`Local storageKey not found: ${storageKey}`);
            err.code = 'LOCAL_NOT_FOUND';
            throw err;
        }
    }

    // Otherwise, treat storageKey as "remote" but for tests we require mapping
    const err = new Error(`No mapping for remote storageKey: ${storageKey}. Add behavior.mapping for tests.`);
    err.code = 'NO_MAPPING';
    throw err;
}

/**
 * uploadFromLocal
 * Simulates uploading a local file to remote storage and returns a storageKey and URL.
 * For tests, it will copy the file to a temp "remote" folder under os.tmpdir() to simulate persistence.
 */
async function uploadFromLocal(localPath, destKey = null) {
    if (!localPath || typeof localPath !== 'string') {
        const err = new Error('uploadFromLocal requires a localPath string');
        err.code = 'INVALID_ARG';
        throw err;
    }

    if (behavior.failOnUpload) {
        const err = new Error('Simulated upload failure (failOnUpload)');
        err.code = 'SIMULATED_UPLOAD_FAIL';
        throw err;
    }

    // Validate source exists
    try {
        const st = await fsp.stat(localPath);
        if (!st.isFile()) throw new Error('Not a file');
    } catch (e) {
        const err = new Error(`Local file not found: ${localPath}`);
        err.code = 'LOCAL_NOT_FOUND';
        throw err;
    }

    // Artificial delay
    if (behavior.delayMs && behavior.delayMs > 0) {
        await new Promise((r) => setTimeout(r, behavior.delayMs));
    }

    // Determine destination key and path
    const key = destKey || `mock/${path.basename(localPath)}-${Date.now()}`;
    const remoteDir = path.join(os.tmpdir(), 'wilsy-mock-remote');
    await fsp.mkdir(remoteDir, { recursive: true });
    const remotePath = path.join(remoteDir, key.replace(/[\\/]/g, '_'));

    // Copy file to remotePath
    await fsp.copyFile(localPath, remotePath);

    // Optionally record mapping so streamToTemp can resolve this key
    behavior.mapping[key] = remotePath;

    // Return a mock storageKey and URL
    const url = `mock://storage/${encodeURIComponent(key)}`;
    return { storageKey: key, url, remotePath };
}

/**
 * isTempPath
 * Returns true if path appears to be under OS temp dir or our mock remote dir.
 */
function isTempPath(p) {
    if (!p || typeof p !== 'string') return false;
    if (p.includes(os.tmpdir())) return true;
    if (p.includes(path.join(os.tmpdir(), 'wilsy-mock-remote'))) return true;
    return false;
}

/**
 * cleanupTemp
 * Removes a temp file if it exists and preserveTemp is false.
 */
async function cleanupTemp(p) {
    if (!p || typeof p !== 'string') return false;
    if (behavior.preserveTemp) return false;
    try {
        // Only unlink if path is under tmp dir for safety
        if (!isTempPath(p)) return false;
        await fsp.unlink(p).catch(() => null);
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * listMapping
 * Expose current mapping for assertions in tests.
 */
function listMapping() {
    return Object.assign({}, behavior.mapping);
}

/* Export API */
module.exports = {
    streamToTemp,
    uploadFromLocal,
    isTempPath,
    cleanupTemp,
    // Test helpers
    setBehavior,
    resetBehavior,
    listMapping,
    _behavior: () => Object.assign({}, behavior)
};
