/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/systemModel.js
 *
 * Enterprise System Model (Masterpiece Edition)
 * ---------------------------------------------
 * Complete, production-grade schema for representing overall system state.
 * - Identity: system code, name, and version.
 * - Environment: uptime, health, modules enabled, integrations.
 * - Governance: compliance posture, audit history, and operational metadata.
 * - Lifecycle: active → maintenance → degraded → offline → archived.
 * - Performance: indexed for queries by status, version, and createdAt.
 *
 * Distinction:
 * - systemSettingsModel.js = granular configuration values (key/value).
 * - systemModel.js = holistic system state and operational metadata.
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Audit History Sub-Schema
// ------------------------------------------
const historySchema = new mongoose.Schema(
    {
        action: { type: String, required: true, trim: true }, // e.g., "STATUS_CHANGED", "MODULE_ENABLED"
        by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        date: { type: Date, default: Date.now },
        reason: { type: String, trim: true },
        diff: { type: Object, default: {} }
    },
    { _id: false }
);

// ------------------------------------------
// Module Sub-Schema
// ------------------------------------------
const moduleSchema = new mongoose.Schema(
    {
        name: { type: String, required: true, trim: true }, // e.g., "Documents", "Invoices", "Compliance"
        enabled: { type: Boolean, default: true },
        version: { type: String, trim: true },
        lastCheckedAt: { type: Date, default: Date.now }
    },
    { _id: false }
);

// ------------------------------------------
// System Schema
// ------------------------------------------
const systemSchema = new mongoose.Schema(
    {
        // 1) Identity
        systemCode: { type: String, required: true, unique: true, index: true }, // e.g., "SYS-LEGAL-001"
        name: { type: String, required: true, trim: true }, // e.g., "Legal Document OS"
        version: { type: String, required: true, trim: true }, // e.g., "1.0.0"

        // 2) Environment
        uptimeSeconds: { type: Number, default: 0 },
        health: {
            type: String,
            enum: ['Healthy', 'Degraded', 'Maintenance', 'Offline'],
            default: 'Healthy',
            index: true
        },
        modules: { type: [moduleSchema], default: [] },
        integrations: { type: [String], default: [] }, // e.g., ["CRM", "ERP", "PaymentGateway"]

        // 3) Governance
        complianceStatus: {
            type: String,
            enum: ['Compliant', 'Non-Compliant', 'Pending Review'],
            default: 'Compliant',
            index: true
        },
        lastAuditAt: { type: Date, default: null },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 4) Metadata
        meta: { type: Object, default: {} },

        // 5) Audit
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
systemSchema.index({ health: 1, complianceStatus: 1 });
systemSchema.index({ version: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Update uptime.
 */
systemSchema.methods.updateUptime = function (seconds) {
    this.uptimeSeconds = seconds;
    this.history.push({
        action: 'UPTIME_UPDATED',
        reason: `System uptime set to ${seconds} seconds`
    });
    return this.save();
};

/**
 * Transition system health status.
 */
systemSchema.methods.transitionHealth = function (nextHealth, actor, reason) {
    const current = this.health;
    this.health = nextHealth;
    this.history.push({
        action: 'HEALTH_CHANGED',
        by: actor?._id,
        reason: reason || `Health changed from '${current}' to '${nextHealth}'`
    });
    return this.save();
};

/**
 * Enable or disable a module.
 */
systemSchema.methods.toggleModule = function (moduleName, enabled, actor) {
    const mod = this.modules.find((m) => m.name === moduleName);
    if (mod) {
        mod.enabled = enabled;
        mod.lastCheckedAt = new Date();
    } else {
        this.modules.push({ name: moduleName, enabled, version: '1.0.0' });
    }
    this.history.push({
        action: 'MODULE_TOGGLED',
        by: actor?._id,
        reason: `Module '${moduleName}' set to ${enabled ? 'enabled' : 'disabled'}`
    });
    return this.save();
};

/**
 * Record compliance audit.
 */
systemSchema.methods.recordAudit = function (status, actor, reason) {
    this.complianceStatus = status;
    this.lastAuditAt = new Date();
    this.history.push({
        action: 'COMPLIANCE_AUDIT',
        by: actor?._id,
        reason: reason || `Compliance status set to '${status}'`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('System', systemSchema);
