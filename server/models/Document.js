/**
 * =============================================================================
 * WILSY OS - DOCUMENT VAULT MODEL
 * PURPOSE: Secure, multi-tenant file metadata management
 * =============================================================================
 */
const mongoose = require('mongoose');

const DocumentSchema = new mongoose.Schema({
    tenantId: { type: String, required: true, index: true },
    caseId: { type: mongoose.Schema.Types.ObjectId, ref: 'Case', required: true, index: true },
    
    // File Identity
    originalName: { type: String, required: true },
    mimeType: String,
    size: Number,
    
    // Storage Provider Data (Cloudinary/S3)
    storageUrl: { type: String, required: true },
    providerId: String,
    
    // Security & Compliance
    confidentiality: {
        type: String,
        enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'SECRET'],
        default: 'INTERNAL'
    },
    hash: String, // SHA-256 for integrity checks
    isArchived: { type: Boolean, default: false }
}, { timestamps: true });

module.exports = mongoose.model('Document', DocumentSchema);
