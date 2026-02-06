/**
 * File: server/services/jobService.js
 * STATUS: PRODUCTION-READY | JOB ORCHESTRATION | EPITOME
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Robust job orchestration layer for Wilsy OS.
 * - Lightweight wrapper around a Redis-backed queue (Bull or BullMQ).
 * - Ensures durable Job documents in MongoDB, emits forensic AuditEvents,
 *   supports graceful shutdown, health checks, metrics hooks, and safe defaults.
 *
 * FEATURES:
 * - Pluggable queue backend: Bull (v3) by default; auto-detects BullMQ if installed.
 * - Creates a Job document before enqueueing so UI can poll immediately.
 * - Correlation IDs for traceability; best-effort audit writes.
 * - Worker registration helper that updates Job documents (progress/status).
 * - Graceful shutdown and queue health checks.
 *
 * DEPENDENCIES:
 * - Redis (REDIS_URL)
 * - MongoDB models: Job, AuditEvent
 * - Structured logger at ../utils/logger
 *
 * USAGE:
 * const JobService = require('../services/jobService');
 * const job = await JobService.enqueue('backupNow', { snapshot: true }, { initiatedBy: userId });
 * JobService.registerWorker('default', async (payload, ctx) => { ... });
 * -----------------------------------------------------------------------------
 */

'use strict';

const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const JobModel = require('../models/jobModel');
const AuditEvent = require('../models/auditEventModel');

const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const DEFAULT_QUEUE_PREFIX = process.env.JOB_QUEUE_PREFIX || 'wilsy_jobs';
const DEFAULT_QUEUE_NAME = 'default';
const DEFAULT_ATTEMPTS = parseInt(process.env.JOB_DEFAULT_ATTEMPTS || '3', 10);
const DEFAULT_BACKOFF = { type: 'exponential', delay: 5000 };

let QueueImpl;
let isBullMQ = false;
try {
    // Prefer BullMQ if available (modern)
    // eslint-disable-next-line global-require
    const { Queue } = require('bullmq');
    QueueImpl = { type: 'bullmq', Queue };
    isBullMQ = true;
    logger.info('jobService: using BullMQ as queue backend');
} catch (e) {
    try {
        // Fallback to bull v3
        // eslint-disable-next-line global-require
        const Bull = require('bull');
        QueueImpl = { type: 'bull', Bull };
        logger.info('jobService: using Bull (v3) as queue backend');
    } catch (err) {
        logger.error('jobService: no queue backend available (install bull or bullmq)', { err: err && err.message ? err.message : err });
        throw new Error('No queue backend available. Install bull or bullmq.');
    }
}

// Map of queueName -> queue instance
const queues = new Map();

/* -------------------------
   Queue Factory
   ------------------------- */

function getQueueKey(name) {
    return `${DEFAULT_QUEUE_PREFIX}:${name}`;
}

function createBullQueue(name) {
    const Bull = QueueImpl.Bull;
    // Bull v3 constructor: new Queue(name, redisUrl, opts)
    return new Bull(name, REDIS_URL, { prefix: DEFAULT_QUEUE_PREFIX });
}

function createBullMQQueue(name) {
    const { Queue } = QueueImpl;
    // BullMQ constructor: new Queue(name, { connection: { url } })
    return new Queue(name, { connection: { url: REDIS_URL }, prefix: DEFAULT_QUEUE_PREFIX });
}

function getQueue(name = DEFAULT_QUEUE_NAME) {
    const key = getQueueKey(name);
    if (queues.has(key)) return queues.get(key);

    let q;
    if (isBullMQ) {
        q = createBullMQQueue(name);
    } else {
        q = createBullQueue(name);
    }

    queues.set(key, q);
    return q;
}

/* -------------------------
   Helper: create Job document
   ------------------------- */

async function createJobDoc({ type, payload = {}, initiatedBy, tenantId = null, correlationId = null, metadata = {} } = {}) {
    if (!type || !initiatedBy) {
        throw new Error('createJobDoc requires type and initiatedBy');
    }
    const jobDoc = await JobModel.createJob({
        type,
        payload,
        initiatedBy,
        tenantId,
        correlationId: correlationId || uuidv4(),
        metadata
    });
    return jobDoc;
}

/* -------------------------
   Enqueue
   ------------------------- */

async function enqueue(jobName, payload = {}, opts = {}) {
    const {
        queue = DEFAULT_QUEUE_NAME,
        initiatedBy,
        tenantId = null,
        correlationId = null,
        jobId = null,
        attempts = DEFAULT_ATTEMPTS,
        backoff = DEFAULT_BACKOFF,
        removeOnComplete = true,
        removeOnFail = false,
        timeout = 0,
        metadata = {},
        actorEmail = null,
        actorRole = null,
        metricsClient = null
    } = opts || {};

    if (!initiatedBy) {
        throw new Error('enqueue requires initiatedBy (user id) in opts');
    }

    // 1) Create Job document so UI can poll immediately
    const jobDoc = await createJobDoc({ type: jobName, payload, initiatedBy, tenantId, correlationId, metadata });

    // 2) Add to queue
    const q = getQueue(queue);
    const effectiveJobId = jobId || jobDoc._id || uuidv4();
    const corr = correlationId || jobDoc.correlationId || uuidv4();

    try {
        let queuedJob;
        if (isBullMQ) {
            // BullMQ: queue.add(name, data, opts)
            queuedJob = await q.add(jobName, { payload, meta: { initiatedBy, correlationId: corr, jobDocId: jobDoc._id } }, {
                jobId: effectiveJobId,
                attempts,
                backoff,
                removeOnComplete,
                removeOnFail,
                timeout
            });
            // queuedJob.id is string
        } else {
            // Bull v3: queue.add(name, data, opts)
            queuedJob = await q.add(jobName, { payload, meta: { initiatedBy, correlationId: corr, jobDocId: jobDoc._id } }, {
                jobId: effectiveJobId,
                attempts,
                backoff,
                removeOnComplete,
                removeOnFail,
                timeout
            });
        }

        // 3) Emit audit (best-effort)
        try {
            if (AuditEvent && typeof AuditEvent.create === 'function') {
                await AuditEvent.create({
                    _id: uuidv4(),
                    timestamp: new Date().toISOString(),
                    actor: initiatedBy || null,
                    actorEmail: actorEmail || null,
                    actorRole: actorRole || null,
                    eventType: 'JOB_ENQUEUED',
                    severity: 'INFO',
                    summary: `Job ${jobName} enqueued`,
                    metadata: { jobId: queuedJob.id || effectiveJobId, queue: queue, correlationId: corr, jobDocId: jobDoc._id }
                });
            }
        } catch (e) {
            logger.warn('jobService.enqueue: audit write failed', { err: e && e.message ? e.message : e });
        }

        if (metricsClient && typeof metricsClient.increment === 'function') {
            metricsClient.increment('jobs.enqueued', { job: jobName, queue });
        }

        return { id: queuedJob.id || effectiveJobId, jobDocId: jobDoc._id, queue, correlationId: corr };
    } catch (err) {
        // If queue add fails, mark job doc as failed
        try {
            await JobModel.markFailed(jobDoc._id, `Queue enqueue failed: ${err && err.message ? err.message : String(err)}`);
        } catch (e) {
            logger.warn('jobService.enqueue: failed to mark job doc failed', { err: e && e.message ? e.message : e });
        }
        logger.error('jobService.enqueue: queue add failed', { err: err && err.message ? err.message : err, jobName, queue });
        throw err;
    }
}

/* -------------------------
   Get Job (combined view)
   ------------------------- */

async function getJob(jobId, { queueName = DEFAULT_QUEUE_NAME } = {}) {
    // Try to fetch from queue first (if available), then from JobModel
    try {
        const q = getQueue(queueName);
        let qJob = null;
        if (isBullMQ) {
            // BullMQ: q.getJob(jobId)
            qJob = await q.getJob(jobId);
        } else {
            qJob = await q.getJob(jobId);
        }

        const jobDoc = await JobModel.findById(jobId).lean().catch(() => null);

        if (qJob) {
            const state = await qJob.getState ? await qJob.getState() : (qJob._state || null);
            return {
                queueJob: {
                    id: qJob.id,
                    name: qJob.name,
                    data: qJob.data,
                    attemptsMade: qJob.attemptsMade,
                    failedReason: qJob.failedReason,
                    finishedOn: qJob.finishedOn,
                    processedOn: qJob.processedOn,
                    state
                },
                jobDoc
            };
        }

        // Fallback: return jobDoc only
        return { queueJob: null, jobDoc };
    } catch (err) {
        logger.warn('jobService.getJob: error fetching job', { err: err && err.message ? err.message : err, jobId, queueName });
        // Return jobDoc if possible
        const jobDoc = await JobModel.findById(jobId).lean().catch(() => null);
        return { queueJob: null, jobDoc };
    }
}

/* -------------------------
   Register Worker
   ------------------------- */

/**
 * registerWorker
 * - queueName: name of queue to process
 * - processor: async function(payload, ctx) => result
 *    ctx: { jobDocId, meta, job, updateProgress } where updateProgress is helper to update JobModel
 * - opts: { concurrency, metricsClient, heartbeatIntervalMs }
 */
function registerWorker(queueName = DEFAULT_QUEUE_NAME, processor, opts = {}) {
    if (typeof processor !== 'function') throw new Error('processor must be a function');

    const { concurrency = 1, metricsClient = null, heartbeatIntervalMs = 30_000 } = opts;
    const q = getQueue(queueName);

    // Worker wrapper for Bull v3
    const workerFn = async (job) => {
        const data = job.data || {};
        const payload = data.payload || {};
        const meta = data.meta || {};
        const jobDocId = meta.jobDocId || (job.data && job.data.meta && job.data.meta.jobDocId) || null;
        const correlationId = meta.correlationId || job.id || uuidv4();

        // Helper to update progress
        const updateProgress = async (progress, patch = {}) => {
            try {
                await JobModel.updateProgress(jobDocId, { progress, ...patch });
            } catch (e) {
                logger.warn('jobService.worker.updateProgress failed', { err: e && e.message ? e.message : e, jobDocId });
            }
        };

        // Mark processing start
        try {
            await JobModel.updateProgress(jobDocId, { status: 'processing', startedAt: new Date(), attempts: job.attemptsMade || 0 });
        } catch (e) {
            logger.warn('jobService.worker: failed to mark job processing', { err: e && e.message ? e.message : e, jobDocId });
        }

        // Optional heartbeat to update startedAt/progress to show liveness
        let heartbeat = null;
        if (heartbeatIntervalMs > 0) {
            heartbeat = setInterval(async () => {
                try {
                    await JobModel.updateProgress(jobDocId, { progress: undefined, status: 'processing' });
                } catch (e) {
                    logger.debug('jobService.worker: heartbeat update failed', { err: e && e.message ? e.message : e, jobDocId });
                }
            }, heartbeatIntervalMs);
        }

        try {
            const result = await processor(payload, { job, meta, jobDocId, correlationId, updateProgress });

            // Mark completed
            await JobModel.markCompleted(jobDocId, result || {});
            if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('jobs.completed', { queue: queueName, job: job.name });

            // Emit audit success (best-effort)
            try {
                if (AuditEvent && typeof AuditEvent.create === 'function') {
                    await AuditEvent.create({
                        _id: uuidv4(),
                        timestamp: new Date().toISOString(),
                        actor: meta?.initiatedBy || null,
                        actorEmail: null,
                        actorRole: null,
                        eventType: 'JOB_COMPLETED',
                        severity: 'INFO',
                        summary: `Job ${job.name} completed`,
                        metadata: { jobId: job.id, queue: queueName, jobDocId, correlationId }
                    });
                }
            } catch (e) {
                logger.warn('jobService.worker: audit write failed for completion', { err: e && e.message ? e.message : e, jobDocId });
            }

            return result;
        } catch (err) {
            // Mark failed
            try {
                await JobModel.markFailed(jobDocId, err && err.message ? err.message : String(err));
            } catch (e) {
                logger.warn('jobService.worker: failed to mark job failed', { err: e && e.message ? e.message : e, jobDocId });
            }

            // Emit audit failure (best-effort)
            try {
                if (AuditEvent && typeof AuditEvent.create === 'function') {
                    await AuditEvent.create({
                        _id: uuidv4(),
                        timestamp: new Date().toISOString(),
                        actor: meta?.initiatedBy || null,
                        actorEmail: null,
                        actorRole: null,
                        eventType: 'JOB_FAILED',
                        severity: 'HIGH',
                        summary: `Job ${job.name} failed`,
                        metadata: { jobId: job.id, queue: queueName, jobDocId, error: err && err.message ? err.message : String(err), correlationId }
                    });
                }
            } catch (e) {
                logger.warn('jobService.worker: audit write failed for failure', { err: e && e.message ? e.message : e, jobDocId });
            }

            if (metricsClient && typeof metricsClient.increment === 'function') metricsClient.increment('jobs.failed', { queue: queueName, job: job.name });

            throw err;
        } finally {
            if (heartbeat) clearInterval(heartbeat);
        }
    };

    // Register processor depending on backend
    if (isBullMQ) {
        // BullMQ: create Worker separately to process jobs (avoid circular import)
        // eslint-disable-next-line global-require
        const { Worker } = require('bullmq');
        const worker = new Worker(queueName, async (job) => workerFn(job), { connection: { url: REDIS_URL }, concurrency });
        worker.on('failed', (job, err) => {
            logger.error('jobService.worker.failed', { queue: queueName, jobId: job.id, err: err && err.message ? err.message : err });
        });
        worker.on('completed', (job) => {
            logger.info('jobService.worker.completed', { queue: queueName, jobId: job.id });
        });
        return worker;
    }

    // Bull v3
    q.process(concurrency, async (job) => workerFn(job));

    q.on('failed', (job, err) => {
        logger.error('jobService.queue.failed', { queue: queueName, jobId: job.id, err: err && err.message ? err.message : err });
    });

    q.on('completed', (job) => {
        logger.info('jobService.queue.completed', { queue: queueName, jobId: job.id });
    });

    return q;
}

/* -------------------------
   Health & Utilities
   ------------------------- */

async function health() {
    const info = { queues: [] };
    for (const [key, q] of queues.entries()) {
        try {
            if (isBullMQ) {
                // BullMQ: q.getJobCounts()
                const counts = await q.getJobCounts();
                info.queues.push({ key, counts });
            } else {
                // Bull v3: q.getJobCounts()
                const counts = await q.getJobCounts();
                info.queues.push({ key, counts });
            }
        } catch (e) {
            info.queues.push({ key, error: e && e.message ? e.message : String(e) });
        }
    }
    return info;
}

/* -------------------------
   Graceful Shutdown
   ------------------------- */

let shuttingDown = false;
async function shutdown() {
    if (shuttingDown) return;
    shuttingDown = true;
    logger.info('jobService.shutdown: closing queues');
    const closePromises = [];
    for (const [key, q] of queues.entries()) {
        try {
            if (isBullMQ) {
                // BullMQ: q.close()
                closePromises.push(q.close().catch((e) => logger.warn('jobService.shutdown: queue close failed', { key, err: e && e.message ? e.message : e })));
            } else {
                // Bull v3: q.close()
                closePromises.push(q.close().catch((e) => logger.warn('jobService.shutdown: queue close failed', { key, err: e && e.message ? e.message : e })));
            }
        } catch (e) {
            logger.warn('jobService.shutdown: error closing queue', { key, err: e && e.message ? e.message : e });
        }
    }
    await Promise.all(closePromises);
    logger.info('jobService.shutdown: all queues closed');
}

/* -------------------------
   Exports
   ------------------------- */

module.exports = {
    enqueue,
    getJob,
    registerWorker,
    shutdown,
    health,
    _getQueue: getQueue // for tests and advanced ops
};
