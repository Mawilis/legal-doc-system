/**
 * File: server/models/systemConfigModel.js
 * PATH: server/models/systemConfigModel.js
 * VERSION: 2026-01-19
 * STATUS: PRODUCTION
 *
 * PURPOSE
 * - System configuration entries (global key/value, scopeable).
 * - Centralized index declarations to avoid duplicate index warnings.
 *
 * COLLABORATION
 * - AUTHOR: Chief Architect (Wilson Khanyezi)
 * - REVIEWERS: @backend-team, @sre
 *
 * MAINTAINER GUIDANCE
 * - Do not add `index: true` on fields in this file.
 * - Add or modify indexes only in the `schema.index(...)` block below.
 */

'use strict';

const mongoose = require('mongoose');
const { Schema } = mongoose;

const SystemConfigSchema = new Schema({
    key: { type: String, required: true, trim: true, uppercase: true },
    value: { type: Schema.Types.Mixed, required: true },
    scope: { type: String, trim: true, default: 'global' }, // e.g., 'global', 'tenant', 'feature'
    tenantId: { type: Schema.Types.ObjectId, ref: 'Tenant', default: null },
    description: { type: String, trim: true },
    isActive: { type: Boolean, default: true },
    createdAt: { type: Date, default: Date.now }
}, {
    timestamps: { createdAt: 'createdAt', updatedAt: 'updatedAt' },
    minimize: false,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

/**
 * Centralized index declarations
 */
SystemConfigSchema.index({ key: 1, scope: 1, tenantId: 1 }, { unique: true, background: true, name: 'idx_syscfg_key_scope_tenant' });
SystemConfigSchema.index({ scope: 1 }, { background: true, name: 'idx_syscfg_scope' });
SystemConfigSchema.index({ tenantId: 1 }, { background: true, sparse: true, name: 'idx_syscfg_tenantId' });

/**
 * Helper: safe getter for typed values
 */
SystemConfigSchema.methods.getValue = function getValue(defaultValue = null) {
    return (this && this.value !== undefined) ? this.value : defaultValue;
};

const SystemConfig = mongoose.models && mongoose.models.SystemConfig
    ? mongoose.model('SystemConfig')
    : mongoose.model('SystemConfig', SystemConfigSchema);

module.exports = SystemConfig;
