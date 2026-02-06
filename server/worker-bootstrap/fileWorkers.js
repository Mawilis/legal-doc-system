/**
 * File: server/worker-bootstrap/fileWorkers.js
 * STATUS: PRODUCTION-READY | EPITOME | WORKER BOOTSTRAP
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Starts and supervises file-related workers (fileScan, metadata extraction, etc.)
 * - Runs in a dedicated worker process (node server/worker-bootstrap/fileWorkers.js)
 * - Ensures graceful startup, health checks, observability hooks, and robust shutdown.
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @sre, @security, @observability, @product
 * - OPERATIONS:
 *   * Run this in a dedicated worker fleet (separate from API nodes).
 *   * Use process managers (systemd, k8s, PM2) to supervise the process.
 *   * Expose a lightweight health endpoint or integrate with your process manager's liveness checks.
 * - SECURITY:
 *   * Workers must run under least-privilege service accounts.
 *   * Ensure logs and generated bundles are stored in protected locations.
 * - TESTING:
 *   * Add integration tests that start this bootstrap in a test harness with mocked services.
 * -----------------------------------------------------------------------------
 */

'use strict';

const os = require('os');
const path = require('path');
const { promisify } = require('util');
const setTimeoutAsync = promisify(setTimeout);

const logger = require('../utils/logger');
const JobService = require('../services/jobService');

// Worker modules (each should export a register(...) helper)
const fileScanWorker = require('../workers/fileScanWorker');
let metadataWorker = null;
try { metadataWorker = require('../workers/fileMetadataWorker'); } catch (e) { /* optional */ }

const DEFAULTS = {
    queueName: process.env.JOB_QUEUE_NAME || 'default',
    fileScanConcurrency: parseInt(process.env.FILE_SCAN_CONCURRENCY || '2', 10),
    metadataConcurrency: parseInt(process.env.FILE_METADATA_CONCURRENCY || '1', 10),
    shutdownTimeoutMs: parseInt(process.env.WORKER_SHUTDOWN_TIMEOUT_MS || '30000', 10),
    healthPort: parseInt(process.env.WORKER_HEALTH_PORT || '0', 10) // 0 = disabled
};

/* Simple in-process health server (optional) */
let healthServer = null;
function startHealthServer(port) {
    if (!port || port <= 0) return null;
    const http = require('http');
    const server = http.createServer((req, res) => {
        if (req.url === '/health' || req.url === '/healthz') {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'ok', pid: process.pid, ts: new Date().toISOString() }));
            return;
        }
        res.writeHead(404);
        res.end();
    });
    server.listen(port, () => logger.info('worker-bootstrap: health server listening', { port }));
    return server;
}

/* Graceful shutdown helper */
async function gracefulShutdown(workers = [], timeoutMs = DEFAULTS.shutdownTimeoutMs) {
    logger.info('worker-bootstrap: initiating graceful shutdown', { pid: process.pid, timeoutMs });

    // Stop accepting new work: close health server first
    if (healthServer && typeof healthServer.close === 'function') {
        try { healthServer.close(); } catch (e) { /* ignore */ }
    }

    // Ask each worker to close (they may be Bull or BullMQ worker instances)
    const closePromises = workers.map(async (w) => {
        if (!w) return;
        try {
            // BullMQ Worker has close(); Bull Queue returned by register may expose close()
            if (typeof w.close === 'function') {
                // Some close() return a promise; others accept callback
                await Promise.race([
                    w.close(),
                    setTimeoutAsync(timeoutMs).then(() => { throw new Error('worker close timeout'); })
                ]);
                logger.info('worker-bootstrap: worker closed', { worker: w.name || w.queueName || 'unknown' });
            } else if (typeof w.disconnect === 'function') {
                // fallback
                w.disconnect();
            }
        } catch (e) {
            logger.warn('worker-bootstrap: worker close failed', { err: e && e.message ? e.message : e });
        }
    });

    // Also close JobService queues
    const jobServiceClose = (async () => {
        try {
            await Promise.race([
                JobService.shutdown(),
                setTimeoutAsync(timeoutMs).then(() => { throw new Error('JobService shutdown timeout'); })
            ]);
            logger.info('worker-bootstrap: JobService shutdown complete');
        } catch (e) {
            logger.warn('worker-bootstrap: JobService shutdown failed', { err: e && e.message ? e.message : e });
        }
    })();

    await Promise.allSettled([...closePromises, jobServiceClose]);

    logger.info('worker-bootstrap: graceful shutdown complete, exiting');
    // Give logs a moment to flush
    await setTimeoutAsync(200);
    process.exit(0);
}

/* Main start routine */
async function start() {
    logger.info('worker-bootstrap: starting file workers', {
        pid: process.pid,
        node: process.version,
        platform: os.platform()
    });

    // Optional health server
    healthServer = startHealthServer(DEFAULTS.healthPort);

    // Register workers and collect returned worker handles for shutdown
    const registeredWorkers = [];

    try {
        // Register fileScan worker
        const fileScanHandle = fileScanWorker.register
            ? fileScanWorker.register({ queueName: DEFAULTS.queueName, concurrency: DEFAULTS.fileScanConcurrency, metricsClient: null })
            : fileScanWorker.registerWithJobService
                ? fileScanWorker.registerWithJobService({ queueName: DEFAULTS.queueName, concurrency: DEFAULTS.fileScanConcurrency })
                : null;

        if (fileScanHandle) {
            registeredWorkers.push(fileScanHandle);
            logger.info('worker-bootstrap: fileScan worker registered', { concurrency: DEFAULTS.fileScanConcurrency });
        } else {
            logger.warn('worker-bootstrap: fileScan worker did not return a handle; ensure register() exists');
        }

        // Register metadata worker if available
        if (metadataWorker && (metadataWorker.register || metadataWorker.registerWithJobService)) {
            const metadataHandle = metadataWorker.register
                ? metadataWorker.register({ queueName: DEFAULTS.queueName, concurrency: DEFAULTS.metadataConcurrency, metricsClient: null })
                : metadataWorker.registerWithJobService
                    ? metadataWorker.registerWithJobService({ queueName: DEFAULTS.queueName, concurrency: DEFAULTS.metadataConcurrency })
                    : null;

            if (metadataHandle) {
                registeredWorkers.push(metadataHandle);
                logger.info('worker-bootstrap: metadata worker registered', { concurrency: DEFAULTS.metadataConcurrency });
            }
        }

        // Listen for termination signals and perform graceful shutdown
        const shutdownHandler = async (signal) => {
            logger.info('worker-bootstrap: received shutdown signal', { signal });
            try {
                await gracefulShutdown(registeredWorkers, DEFAULTS.shutdownTimeoutMs);
            } catch (e) {
                logger.error('worker-bootstrap: gracefulShutdown failed', { err: e && e.message ? e.message : e });
                process.exit(1);
            }
        };

        process.on('SIGINT', () => shutdownHandler('SIGINT'));
        process.on('SIGTERM', () => shutdownHandler('SIGTERM'));

        // Handle uncaught exceptions and unhandled rejections: log and exit after attempting graceful shutdown
        process.on('uncaughtException', async (err) => {
            logger.error('worker-bootstrap: uncaughtException', { err: err && err.stack ? err.stack : err });
            try { await gracefulShutdown(registeredWorkers, DEFAULTS.shutdownTimeoutMs); } catch (_) { /* ignore */ }
            process.exit(1);
        });

        process.on('unhandledRejection', async (reason) => {
            logger.error('worker-bootstrap: unhandledRejection', { reason: reason && reason.stack ? reason.stack : reason });
            try { await gracefulShutdown(registeredWorkers, DEFAULTS.shutdownTimeoutMs); } catch (_) { /* ignore */ }
            process.exit(1);
        });

        logger.info('worker-bootstrap: all workers registered and running', { registeredCount: registeredWorkers.length });
    } catch (err) {
        logger.error('worker-bootstrap: startup failed', { err: err && err.message ? err.message : err });
        // Attempt best-effort shutdown
        try { await gracefulShutdown(registeredWorkers, DEFAULTS.shutdownTimeoutMs); } catch (_) { /* ignore */ }
        process.exit(1);
    }
}

/* Start when invoked directly */
if (require.main === module) {
    start().catch((err) => {
        logger.error('worker-bootstrap: fatal error on start', { err: err && err.message ? err.message : err });
        process.exit(1);
    });
}

/* Export start for test harnesses */
module.exports = { start, gracefulShutdown };
