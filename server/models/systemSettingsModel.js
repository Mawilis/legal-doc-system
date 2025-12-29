/**
 * ~/server/models/systemSettingsModel.js
 *
 * Enterprise System Settings Model
 * --------------------------------
 * Collaboration-ready, production-grade schema for managing system-wide settings.
 * - Stores configuration values, preferences, and global rules.
 * - Supports categories and key-value pairs.
 * - Tracks lifecycle with audit history.
 * - Indexed for performance on category and key.
 */

'use strict';

const mongoose = require('mongoose');

// ------------------------------------------
// Audit History Sub-Schema
// ------------------------------------------
const historySchema = new mongoose.Schema(
    {
        action: { type: String, required: true, trim: true },
        by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        date: { type: Date, default: Date.now },
        reason: { type: String, trim: true }
    },
    { _id: false }
);

// ------------------------------------------
// System Settings Schema
// ------------------------------------------
const systemSettingsSchema = new mongoose.Schema(
    {
        // 1) Identity
        settingCode: { type: String, required: true, unique: true, index: true }, // e.g., "SYS-SET-001"
        category: { type: String, required: true, trim: true, index: true }, // e.g., "Authentication", "Notifications"
        key: { type: String, required: true, trim: true }, // e.g., "maxLoginAttempts"
        value: { type: mongoose.Schema.Types.Mixed, required: true }, // Flexible: string, number, boolean, object

        // 2) Relations
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

        // 3) Status
        status: {
            type: String,
            enum: ['Active', 'Inactive', 'Deprecated'],
            default: 'Active',
            index: true
        },

        // 4) Metadata
        meta: { type: Object, default: {} },

        // 5) Audit History
        history: { type: [historySchema], default: [] }
    },
    { timestamps: true }
);

// ------------------------------------------
// Indexes
// ------------------------------------------
systemSettingsSchema.index({ category: 1, key: 1 });
systemSettingsSchema.index({ status: 1, createdAt: -1 });

// ------------------------------------------
// Instance Methods
// ------------------------------------------
/**
 * Update setting value with audit history.
 */
systemSettingsSchema.methods.updateValue = function (newValue, options = {}) {
    const oldValue = this.value;
    this.value = newValue;
    this.history.push({
        action: 'VALUE_UPDATED',
        by: options.by || undefined,
        reason: options.reason || `Value changed from '${oldValue}' to '${newValue}'`
    });
    return this.save();
};

/**
 * Transition setting status with audit history.
 */
systemSettingsSchema.methods.transitionStatus = function (nextStatus, options = {}) {
    const current = this.status;
    this.status = nextStatus;
    this.history.push({
        action: 'STATUS_CHANGED',
        by: options.by || undefined,
        reason: options.reason || `Status changed from '${current}' to '${nextStatus}'`
    });
    return this.save();
};

// ------------------------------------------
// Model Export
// ------------------------------------------
module.exports = mongoose.model('SystemSettings', systemSettingsSchema);
