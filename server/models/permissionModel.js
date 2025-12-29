/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/models/permissionModel.js
 *
 * Permission Model
 * ----------------
 * Granular permission registry to support auditability and dynamic RBAC.
 */

const mongoose = require('mongoose');

const permissionSchema = new mongoose.Schema(
    {
        key: {
            type: String, // e.g., 'documents.view', 'cases.assign', 'reports.generate'
            required: true,
            unique: true,
            lowercase: true,
            trim: true,
            index: true,
        },
        description: { type: String, trim: true, default: '' },
        module: { type: String, trim: true, lowercase: true, index: true }, // e.g., 'documents', 'cases'
        defaultAssigned: { type: Boolean, default: false }, // baseline permissions for standard roles
    },
    { timestamps: true }
);

permissionSchema.index({ key: 1 }, { unique: true });
permissionSchema.index({ module: 1 });

module.exports = mongoose.model('Permission', permissionSchema);
