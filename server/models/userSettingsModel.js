/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/userSettingsModel.js
 *
 * User Settings Model
 * -------------------
 * Stores per-user preferences (notifications, theme, language).
 */

const mongoose = require('mongoose');

const userSettingsSchema = new mongoose.Schema(
    {
        userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, unique: true, index: true },
        notifications: {
            email: { type: Boolean, default: true },
            inApp: { type: Boolean, default: true },
            sms: { type: Boolean, default: false },
            digestFrequency: { type: String, default: 'daily', enum: ['instant', 'hourly', 'daily', 'weekly'] },
        },
        appearance: {
            theme: { type: String, default: 'light', enum: ['light', 'dark', 'system'] },
            density: { type: String, default: 'comfortable', enum: ['comfortable', 'compact'] },
        },
        locale: {
            language: { type: String, default: 'en', trim: true },
            region: { type: String, default: 'ZA', trim: true },
            timezone: { type: String, default: 'Africa/Johannesburg', trim: true },
        },
        accessibility: {
            highContrast: { type: Boolean, default: false },
            reducedMotion: { type: Boolean, default: false },
        },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    },
    { timestamps: true }
);

module.exports = mongoose.model('UserSettings', userSettingsSchema);


