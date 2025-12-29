/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/fileModel.js
 *
 * File Model
 * ----------
 * Tracks uploaded files, versions, hashes, storage locations, and scan status.
 */

const mongoose = require('mongoose');

const fileVersionSchema = new mongoose.Schema(
    {
        version: { type: Number, required: true }, // incremental
        storageKey: { type: String, required: true, index: true }, // path or cloud key
        hash: { type: String, required: true }, // SHA256 or similar
        sizeBytes: { type: Number, required: true },
        mimeType: { type: String, required: true },
        uploadedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
        uploadedAt: { type: Date, default: Date.now },
        scanStatus: { type: String, default: 'pending', enum: ['pending', 'clean', 'infected', 'error'], index: true },
        scanDetails: { type: String, trim: true },
        encryption: {
            algorithm: { type: String, trim: true },
            keyRef: { type: String, trim: true }, // reference to KMS key, not the key itself
        },
    },
    { _id: false }
);

const fileSchema = new mongoose.Schema(
    {
        ownerId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', index: true },
        relatedEntity: {
            type: {
                type: String, // e.g., 'document', 'case', 'evidence'
                lowercase: true,
                trim: true,
            },
            id: { type: String, trim: true },
        },
        name: { type: String, required: true, trim: true, index: true },
        currentVersion: { type: Number, default: 1, index: true },
        versions: { type: [fileVersionSchema], default: [] },
        tags: { type: [String], default: [], index: true },
        archived: { type: Boolean, default: false, index: true },
        retentionPolicyId: { type: mongoose.Schema.Types.ObjectId, ref: 'Retention' },
    },
    { timestamps: true }
);

fileSchema.index({ 'relatedEntity.type': 1, 'relatedEntity.id': 1 });
fileSchema.index({ archived: 1 });

module.exports = mongoose.model('File', fileSchema);
