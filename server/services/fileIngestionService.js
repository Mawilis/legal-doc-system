/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/services/fileIngestionService.js
 *
 * File Ingestion Service
 * ----------------------
 * Persists file metadata, versions, and links to related entities.
 */

const File = require('../models/fileModel');
const crypto = require('crypto');
const fs = require('fs');

exports.ingestLocalUpload = async ({
    ownerId,
    relatedEntityType,
    relatedEntityId,
    originalName,
    storageKey,
    mimeType,
    retentionPolicyId,
}) => {
    const stat = fs.statSync(storageKey);
    const sizeBytes = stat.size;

    const hash = crypto.createHash('sha256').update(fs.readFileSync(storageKey)).digest('hex');

    const baseName = originalName || storageKey.split('/').pop();

    const fileDoc = await File.create({
        ownerId,
        relatedEntity: { type: relatedEntityType, id: relatedEntityId },
        name: baseName,
        currentVersion: 1,
        versions: [{
            version: 1,
            storageKey,
            hash,
            sizeBytes,
            mimeType,
            uploadedBy: ownerId,
            scanStatus: 'pending',
            uploadedAt: new Date(),
        }],
        retentionPolicyId: retentionPolicyId || null,
        tags: [],
    });

    return fileDoc;
};
