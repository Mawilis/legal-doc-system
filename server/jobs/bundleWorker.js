/**
 * File: server/jobs/bundleWorker.js
 * STATUS: PRODUCTION-READY | EPITOME | FORENSIC STITCHING
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Stitch PDF assets into a single, paginated court bundle with Bates stamping.
 * - Update JobModel progress, emit AuditEvents, and support remote storage.
 * - Designed to run in a dedicated worker process and integrate with JobService.
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @sre, @security, @product, @legal
 * - DESIGN NOTES:
 *   * Keep worker processes separate from API servers to avoid resource contention.
 *   * StorageService must implement streamToTemp(storageKey) and isTempPath(path).
 *   * AuditEvent must be append-only and indexed for forensic queries.
 *   * JobModel updates are used to surface progress to the UI; workers must call updateProgress.
 * - SECURITY:
 *   * Validate inputs at the API layer before enqueuing jobs.
 *   * Ensure output bundles are stored in a protected location and served via authenticated endpoints.
 * - TESTING:
 *   * Add unit tests using small fixture PDFs.
 *   * Add integration tests with a mocked StorageService and in-memory MongoDB.
 * - OPERATIONS:
 *   * Monitor job durations, pages stitched, and failure reasons via metrics.
 *   * Use a retention policy for generated bundles and rotate storage.
 * -----------------------------------------------------------------------------
 */

'use strict';

const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
const os = require('os');
const { v4: uuidv4 } = require('uuid');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const logger = require('../utils/logger');
const Document = require('../models/Document');
const JobModel = require('../models/jobModel');
const AuditEvent = require('../models/auditEventModel');
const JobService = require('../services/jobService');

// Optional services; provide implementations in production
let StorageService = null;
try { StorageService = require('../services/storageService'); } catch (e) { /* optional in tests */ }

/* Default configuration */
const DEFAULTS = {
    outputBaseDir: path.join(__dirname, '../../public/bundles'),
    // Avoid regex literal containing an escaped forward slash to satisfy linters.
    // Use two simple replaces instead of a character class with an escaped slash.
    filenameTemplate: ({ caseNumber }) => {
        return `BUNDLE_${String(caseNumber).replace(/\s+/g, '_').replace(/\//g, '_')}_${Date.now()}.pdf`;
    },
    stamp: {
        fontSize: 9,
        marginRight: 40,
        marginBottom: 20,
        color: rgb(0.1, 0.1, 0.1)
    },
    tempDir: os.tmpdir()
};

/* -------------------------
   Helpers
   ------------------------- */

async function ensureDir(dir) {
    await fsp.mkdir(dir, { recursive: true });
}

async function downloadToLocal(storageKey) {
    if (!storageKey) throw new Error('storageKey required');
    const isLocal = typeof storageKey === 'string' && (storageKey.startsWith('/') || storageKey.startsWith('./') || /^[A-Za-z]:\\/.test(storageKey));
    if (isLocal) {
        await fsp.access(storageKey, fs.constants.R_OK);
        return storageKey;
    }
    if (!StorageService || typeof StorageService.streamToTemp !== 'function') {
        throw new Error('StorageService not configured to stream remote storage keys');
    }
    const tmp = await StorageService.streamToTemp(storageKey);
    return tmp;
}

async function safeUnlink(p) {
    try {
        if (!p) return;
        await fsp.unlink(p).catch(() => null);
    } catch (e) {
        // swallow
    }
}

/* -------------------------
   Core: generateCourtBundle
   ------------------------- */

async function generateCourtBundle(opts = {}) {
    const { tenantId, caseNumber, documentIds = [], title = '', config = {} } = opts;
    if (!tenantId) throw new Error('tenantId is required');
    if (!caseNumber) throw new Error('caseNumber is required');
    if (!Array.isArray(documentIds) || documentIds.length === 0) throw new Error('documentIds required');

    const cfg = Object.assign({}, DEFAULTS, config);
    const outDir = path.join(cfg.outputBaseDir, String(tenantId));
    await ensureDir(outDir);

    const fileName = (typeof cfg.filenameTemplate === 'function') ? cfg.filenameTemplate({ caseNumber, title }) : cfg.filenameTemplate;
    const filePath = path.join(outDir, fileName);

    const masterDoc = await PDFDocument.create();
    const helveticaFont = await masterDoc.embedFont(StandardFonts.Helvetica);
    let globalPageCounter = 1;
    const tempFilesToCleanup = new Set();

    const docs = await Document.find({
        tenantId,
        _id: { $in: documentIds },
        status: { $ne: 'DELETED' }
    }).sort({ createdAt: 1 }).lean();

    if (!docs || docs.length === 0) {
        throw new Error('ERR_BUNDLE_EMPTY: No valid documents found for stitching.');
    }

    for (const docRecord of docs) {
        try {
            const storageKey = docRecord.storageKey || docRecord.filename;
            if (!storageKey) {
                logger.warn('bundleWorker: document missing storageKey or filename', { docId: docRecord._id });
                continue;
            }

            let localPath;
            try {
                localPath = await downloadToLocal(storageKey);
            } catch (e) {
                logger.warn('bundleWorker: failed to download document', { docId: docRecord._id, err: e && e.message ? e.message : e });
                continue;
            }

            if (localPath !== storageKey) tempFilesToCleanup.add(localPath);

            const bytes = await fsp.readFile(localPath);
            const subDoc = await PDFDocument.load(bytes);
            const indices = subDoc.getPageIndices();
            const copiedPages = await masterDoc.copyPages(subDoc, indices);

            for (const page of copiedPages) {
                const { width, height } = page.getSize();
                const stampText = `CASE: ${caseNumber} | BATES: ${String(globalPageCounter).padStart(6, '0')}`;
                const textWidth = helveticaFont.widthOfTextAtSize(stampText, cfg.stamp.fontSize);
                const x = Math.max(10, width - cfg.stamp.marginRight - textWidth);
                const y = Math.max(10, cfg.stamp.marginBottom);

                page.drawText(stampText, {
                    x,
                    y,
                    size: cfg.stamp.fontSize,
                    font: helveticaFont,
                    color: cfg.stamp.color
                });

                masterDoc.addPage(page);
                globalPageCounter++;
            }

            logger.info('bundleWorker: stitched document', { docId: docRecord._id, title: docRecord.title, pagesAdded: indices.length });
        } catch (err) {
            logger.error('bundleWorker: failed to stitch document', { docId: docRecord._id, err: err && err.message ? err.message : err });
        }
    }

    const pdfBytes = await masterDoc.save();
    const tmpOut = path.join(cfg.tempDir, `bundle-${uuidv4()}.pdf`);
    await fsp.writeFile(tmpOut, pdfBytes);
    await fsp.rename(tmpOut, filePath);

    for (const t of tempFilesToCleanup) {
        await safeUnlink(t);
    }

    return {
        fileName,
        filePath,
        publicUrl: `/bundles/${tenantId}/${fileName}`,
        totalPages: Math.max(0, globalPageCounter - 1),
        processedAt: new Date()
    };
}

/* -------------------------
   Worker processor wrapper
   ------------------------- */

async function bundleProcessor(payload = {}, ctx = {}) {
    const { tenantId, caseNumber, documentIds, title } = payload || {};
    const { job, meta = {}, jobDocId, updateProgress } = ctx || {};
    const correlationId = meta?.correlationId || (job && job.id) || uuidv4();

    const setProgress = async (p, patch = {}) => {
        try {
            if (typeof updateProgress === 'function') {
                await updateProgress(p, patch);
            } else if (jobDocId) {
                await JobModel.updateProgress(jobDocId, { progress: p, ...patch });
            }
        } catch (e) {
            logger.warn('bundleWorker: failed to update job progress', { err: e && e.message ? e.message : e, jobDocId });
        }
    };

    if (!tenantId || !caseNumber || !Array.isArray(documentIds) || documentIds.length === 0) {
        await setProgress(0, { status: 'failed', error: 'Invalid job payload' });
        throw new Error('Invalid job payload: tenantId, caseNumber and documentIds are required');
    }

    await setProgress(5, { status: 'processing' });

    try {
        const result = await generateCourtBundle({ tenantId, caseNumber, documentIds, title });

        await setProgress(100, { status: 'completed', result });

        try {
            if (AuditEvent && typeof AuditEvent.create === 'function') {
                await AuditEvent.create({
                    _id: uuidv4(),
                    timestamp: new Date().toISOString(),
                    actor: meta?.initiatedBy || null,
                    actorEmail: null,
                    actorRole: null,
                    eventType: 'BUNDLE_GENERATED',
                    severity: 'INFO',
                    summary: 'Court bundle generated',
                    metadata: { tenantId, caseNumber, totalPages: result.totalPages, fileName: result.fileName, correlationId }
                });
            }
        } catch (e) {
            logger.warn('bundleWorker: audit write failed', { err: e && e.message ? e.message : e });
        }

        return result;
    } catch (err) {
        await setProgress(0, { status: 'failed', error: err && err.message ? err.message : String(err) });

        try {
            if (AuditEvent && typeof AuditEvent.create === 'function') {
                await AuditEvent.create({
                    _id: uuidv4(),
                    timestamp: new Date().toISOString(),
                    actor: meta?.initiatedBy || null,
                    actorEmail: null,
                    actorRole: null,
                    eventType: 'BUNDLE_GENERATION_FAILED',
                    severity: 'HIGH',
                    summary: 'Court bundle generation failed',
                    metadata: { tenantId, caseNumber, error: err && err.message ? err.message : String(err), correlationId }
                });
            }
        } catch (e) {
            logger.warn('bundleWorker: failure audit write failed', { err: e && e.message ? e.message : e });
        }

        logger.error('bundleWorker: job failed', { err: err && err.message ? err.message : err });
        throw err;
    }
}

/* -------------------------
   Registration helpers
   ------------------------- */

function registerWithJobService(opts = {}) {
    const { queueName = 'bundleQueue', concurrency = 1, metricsClient = null } = opts;
    return JobService.registerWorker(queueName, async (payload, ctx) => {
        const updateProgress = async (progress, patch = {}) => {
            try {
                const jobDocId = ctx.jobDocId || (ctx.job && ctx.job.id);
                if (jobDocId) await JobModel.updateProgress(jobDocId, { progress, ...patch });
            } catch (e) {
                logger.warn('bundleWorker.register: updateProgress failed', { err: e && e.message ? e.message : e });
            }
        };

        return bundleProcessor(payload, Object.assign({}, ctx, { updateProgress }));
    }, { concurrency, metricsClient });
}

function registerBullMQWorker({ queueName = 'bundleQueue', connection, concurrency = 1 } = {}) {
    if (!connection) throw new Error('BullMQ connection required for registerBullMQWorker');
    const { Worker } = require('bullmq');
    const worker = new Worker(queueName, async (job) => {
        const payload = job.data || {};
        const meta = payload.meta || {};
        const jobDocId = payload.meta?.jobDocId || null;

        const updateProgress = async (progress, patch = {}) => {
            try {
                if (jobDocId) await JobModel.updateProgress(jobDocId, { progress, ...patch });
            } catch (e) {
                logger.warn('bundleWorker.bullmq.updateProgress failed', { err: e && e.message ? e.message : e, jobDocId });
            }
        };

        return bundleProcessor(payload, { job, meta, jobDocId, updateProgress });
    }, { connection, concurrency });

    worker.on('failed', (job, err) => {
        logger.error('bundleWorker.bullmq.failed', { jobId: job.id, err: err && err.message ? err.message : err });
    });

    worker.on('completed', (job) => {
        logger.info('bundleWorker.bullmq.completed', { jobId: job.id });
    });

    return worker;
}

/* -------------------------
   Exports
   ------------------------- */

module.exports = {
    generateCourtBundle,
    bundleProcessor,
    registerWithJobService,
    registerBullMQWorker
};
