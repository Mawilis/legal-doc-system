/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/integrationModel.js
 *
 * Integration Model
 * -----------------
 * Manages external service integrations (payments, e-sign, storage).
 */

const mongoose = require('mongoose');

const integrationSchema = new mongoose.Schema(
    {
        provider: { type: String, required: true, trim: true, lowercase: true, index: true }, // 'stripe', 'docusign', 's3'
        name: { type: String, required: true, trim: true }, // display label
        enabled: { type: Boolean, default: false, index: true },
        credentials: {
            type: Map,
            of: String, // NEVER store plaintext secrets; use KMS/HashiCorp/Vault in production
            default: {},
        },
        config: {
            type: Map,
            of: String,
            default: {},
        },
        scopes: { type: [String], default: [] }, // scope/permissions granted for integration
        lastHealthCheckAt: { type: Date },
        lastHealthStatus: { type: String, default: 'unknown', enum: ['unknown', 'ok', 'degraded', 'down'] },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    },
    { timestamps: true }
);

integrationSchema.index({ provider: 1, enabled: 1 });

module.exports = mongoose.model('Integration', integrationSchema);
