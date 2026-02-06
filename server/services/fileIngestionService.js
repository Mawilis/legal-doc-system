/**
 * File: server/services/fileIngestionService.js
 * STATUS: PRODUCTION-READY | EPITOME | FILE INGESTION ENGINE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Robust, production-grade service to persist file metadata, manage versions,
 *   deduplicate by content hash, trigger asynchronous scanning and processing,
 *   and integrate with storage backends and job workers.
 *
 * PRINCIPLES:
 * - Non-blocking I/O and streaming hashing for large files.
 * - Idempotent ingestion by content hash to avoid duplicates.
 * - Create a Job record or enqueue a scan job for long-running tasks.
 * - Emit forensic AuditEvents for traceability.
 * - Defensive validation and clear, actionable errors for callers.
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @security, @sre, @compliance
 * - DEPENDS ON: File model, Job service, AuditEvent model, optional StorageService,
 *   optional VirusScanService, optional MetadataExtractor.
 * - TESTING: Add unit tests for hash collisions, dedupe, version bumping, and error paths.
 * -----------------------------------------------------------------------------
 */

'use strict';

const fs = require('fs');
const fsp = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const stream = require('stream');
const { promisify } = require('util');

const pipeline = promisify(stream.pipeline);

// Models and services (assumed implemented)
const FileModel = require('../models/fileModel');
const JobModel = require('../models/jobModel');
const AuditEvent = require('../models/auditEventModel');
const JobService = require('./jobService'); // enqueue background jobs
const logger = require('../utils/logger');

// Optional helpers (implement or mock in tests)
let StorageService = null;
try { StorageService = require('./storageService'); } catch (e) { StorageService = null; }

let VirusScanService = null;
try { VirusScanService = require('./virusScanService'); } catch (e) { VirusScanService = null; }

let MetadataExtractor = null;
try { MetadataExtractor = require('./metadataExtractor'); } catch (e) { MetadataExtractor = null; }

/* -------------------------
   Helpers
   ------------------------- */

/**
 * computeSha256Stream
 * Streams file at localPath and computes SHA256 hash while returning size.
 */
async function computeSha256Stream(localPath) {
    const hash = crypto.createHash('sha256');
    let size = 0;

    const rs = fs.createReadStream(localPath);
    rs.on('data', (chunk) => { size += chunk.length; });

    await pipeline(rs, new stream.Writable({
        write(chunk, _enc, cb) {
            hash.update(chunk);
            cb();
        }
    }));

    return { hash: hash.digest('hex'), sizeBytes: size };
}

/**
 * safeStat
 * Returns stat or null if not found.
 */
async function safeStat(p) {
    try {
        return await fsp.stat(p);
    } catch (e) {
        return null;
    }
}

/**
 * createAudit
 * Best-effort audit write; does not throw.
 */
async function createAudit({ actor = null, actorEmail = null, actorRole = null, eventType, severity = 'INFO', summary = '', metadata = {} } = {}) {
    try {
        if (AuditEvent && typeof AuditEvent.create === 'function') {
            await AuditEvent.create({
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
        logger.warn('fileIngestionService.createAudit failed', { err: e && e.message ? e.message : e, eventType });
    }
}

/* -------------------------
   Main API
   ------------------------- */

/**
 * ingestLocalUpload
 * Ingests a file that has been uploaded to local disk (or a storageKey that is a local path).
 *
 * Behavior:
 *  - Validates inputs.
 *  - Streams file to compute SHA256 and size.
 *  - Attempts to deduplicate by hash: if an existing file with same hash exists,
 *    it will create a new version entry referencing the same storageKey or return existing doc.
 *  - Persists File document with versions array and metadata.
 *  - Triggers asynchronous virus scan and metadata extraction via JobService.
 *
 * @param {Object} opts
 * @param {ObjectId} opts.ownerId required
 * @param {String} opts.relatedEntityType optional
 * @param {ObjectId|String} opts.relatedEntityId optional
 * @param {String} opts.originalName optional
 * @param {String} opts.storageKey required local path or storage identifier
 * @param {String} opts.mimeType optional
 * @param {ObjectId} opts.retentionPolicyId optional
 * @param {Object} opts.actor optional { id, email, role } for audit
 *
 * @returns {Object} fileDoc (freshly created or updated)
 *
 * Throws Error on validation or IO failures.
 */
async function ingestLocalUpload({
    ownerId,
    relatedEntityType = null,
    relatedEntityId = null,
    originalName = null,
    storageKey,
    mimeType = null,
    retentionPolicyId = null,
    actor = {}
} = {}) {
    // Input validation
    if (!ownerId) throw new Error('ownerId is required');
    if (!storageKey) throw new Error('storageKey is required');

    // Resolve local path vs storage service
    const isLocalPath = typeof storageKey === 'string' && (storageKey.startsWith('/') || storageKey.startsWith('./') || storageKey.match(/^[A-Za-z]:\\/));
    if (!isLocalPath && !StorageService) {
        throw new Error('Non-local storageKey provided but no StorageService is configured');
    }

    // If local path, ensure file exists
    if (isLocalPath) {
        const stat = await safeStat(storageKey);
        if (!stat || !stat.isFile()) throw new Error(`File not found at storageKey: ${storageKey}`);
    }

    // Compute hash and size
    let hash;
    let sizeBytes;
    try {
        if (isLocalPath) {
            const res = await computeSha256Stream(storageKey);
            hash = res.hash;
            sizeBytes = res.sizeBytes;
        } else {
            // If storage service, stream from storage service
            if (!StorageService || typeof StorageService.streamToLocal !== 'function') {
                throw new Error('StorageService streaming not available');
            }
            // stream to temp file then compute
            const tmpLocal = await StorageService.streamToTemp(storageKey);
            const res = await computeSha256Stream(tmpLocal);
            hash = res.hash;
            sizeBytes = res.sizeBytes;
            // Optionally remove temp file
            try { await fsp.unlink(tmpLocal); } catch (e) { /* ignore */ }
        }
    } catch (err) {
        logger.error('ingestLocalUpload: hash computation failed', { err: err && err.message ? err.message : err, storageKey });
        throw new Error('Failed to compute file hash or read file');
    }

    // Determine base name
    const baseName = originalName || path.basename(storageKey);

    // Deduplication: check if a file with same hash exists for same tenant/owner
    try {
        const existing = await FileModel.findOne({ 'versions.hash': hash, ownerId }).sort({ createdAt: -1 }).lean();
        if (existing) {
            // If exact same storageKey already present in versions, return existing doc
            const sameStorage = (existing.versions || []).some(v => v.hash === hash && v.storageKey === storageKey);
            if (sameStorage) {
                // Emit audit and return existing
                await createAudit({
                    actor: actor.id || ownerId,
                    actorEmail: actor.email || null,
                    actorRole: actor.role || null,
                    eventType: 'FILE_INGEST_DEDUP_RETURN',
                    severity: 'INFO',
                    summary: 'Duplicate file ingestion detected; returning existing file document',
                    metadata: { fileId: existing._id, hash, storageKey }
                });
                return existing;
            }

            // Otherwise, append a new version referencing same content (if storageKey differs, still allow)
            const newVersionNumber = (existing.currentVersion || 1) + 1;
            const versionEntry = {
                version: newVersionNumber,
                storageKey,
                hash,
                sizeBytes,
                mimeType,
                uploadedBy: ownerId,
                scanStatus: VirusScanService ? 'pending' : 'skipped',
                uploadedAt: new Date()
            };

            const updated = await FileModel.findByIdAndUpdate(existing._id, {
                $set: { currentVersion: newVersionNumber, name: baseName, retentionPolicyId: retentionPolicyId || existing.retentionPolicyId || null },
                $push: { versions: versionEntry }
            }, { new: true }).lean();

            await createAudit({
                actor: actor.id || ownerId,
                actorEmail: actor.email || null,
                actorRole: actor.role || null,
                eventType: 'FILE_INGEST_VERSION_ADDED',
                severity: 'INFO',
                summary: 'Added new version to existing file (deduplicated by hash)',
                metadata: { fileId: updated._id, version: newVersionNumber, hash, storageKey }
            });

            // Enqueue async scan/metadata extraction
            try {
                await JobService.enqueue('fileScan', { fileId: updated._id, version: newVersionNumber }, { initiatedBy: actor.id || ownerId, tenantId: relatedEntityId || null });
            } catch (e) {
                logger.warn('ingestLocalUpload: failed to enqueue fileScan job', { err: e && e.message ? e.message : e, fileId: updated._id });
            }

            return updated;
        }
    } catch (err) {
        logger.warn('ingestLocalUpload: dedupe check failed', { err: err && err.message ? err.message : err });
        // continue to create new doc to avoid blocking ingestion
    }

    // Create new File document
    const fileDocPayload = {
        ownerId,
        relatedEntity: relatedEntityType && relatedEntityId ? { type: relatedEntityType, id: relatedEntityId } : null,
        name: baseName,
        currentVersion: 1,
        versions: [{
            version: 1,
            storageKey,
            hash,
            sizeBytes,
            mimeType,
            uploadedBy: ownerId,
            scanStatus: VirusScanService ? 'pending' : 'skipped',
            uploadedAt: new Date()
        }],
        retentionPolicyId: retentionPolicyId || null,
        tags: [],
        metadata: {}
    };

    let fileDoc;
    try {
        fileDoc = await FileModel.create(fileDocPayload);
    } catch (err) {
        logger.error('ingestLocalUpload: failed to create File document', { err: err && err.message ? err.message : err, payload: fileDocPayload });
        throw new Error('Failed to persist file metadata');
    }

    // Emit audit
    await createAudit({
        actor: actor.id || ownerId,
        actorEmail: actor.email || null,
        actorRole: actor.role || null,
        eventType: 'FILE_INGEST_CREATED',
        severity: 'INFO',
        summary: 'File document created',
        metadata: { fileId: fileDoc._id, hash, storageKey, sizeBytes }
    });

    // Enqueue asynchronous tasks: virus scan, metadata extraction, thumbnailing, OCR
    try {
        // fileScan job should perform virus scan and update FileModel.versions[n].scanStatus
        await JobService.enqueue('fileScan', { fileId: fileDoc._id, version: 1 }, { initiatedBy: actor.id || ownerId, tenantId: relatedEntityId || null });
    } catch (e) {
        logger.warn('ingestLocalUpload: failed to enqueue fileScan job', { err: e && e.message ? e.message : e, fileId: fileDoc._id });
    }

    try {
        if (MetadataExtractor) {
            await JobService.enqueue('fileMetadataExtract', { fileId: fileDoc._id, version: 1 }, { initiatedBy: actor.id || ownerId, tenantId: relatedEntityId || null });
        }
    } catch (e) {
        logger.warn('ingestLocalUpload: failed to enqueue metadata extraction job', { err: e && e.message ? e.message : e, fileId: fileDoc._id });
    }

    return fileDoc;
}

/* -------------------------
   Exports
   ------------------------- */

module.exports = {
    ingestLocalUpload
};
