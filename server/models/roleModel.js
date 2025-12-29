/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/roleModel.js
 *
 * Role Model
 * ----------
 * Defines application roles and associated permissions.
 */

const mongoose = require('mongoose');

const roleSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true,
            uppercase: true,
            trim: true,
            unique: true,
            index: true,
        },
        description: {
            type: String,
            trim: true,
            default: '',
        },
        permissions: {
            type: [String], // e.g., 'documents.view', 'documents.edit', 'users.manage'
            default: [],
            index: true,
        },
        systemRole: {
            type: Boolean, // protects core roles from deletion (ADMIN, SUPERADMIN)
            default: false,
        },
        createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
        updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    },
    { timestamps: true }
);

roleSchema.index({ name: 1 }, { unique: true });
roleSchema.index({ permissions: 1 });

module.exports = mongoose.model('Role', roleSchema);
