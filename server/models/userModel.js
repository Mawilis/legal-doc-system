/**
 * File: server/models/userModel.js
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - Purpose: Canonical User model for the Legal Doc System.
 * - Features:
 *   • Multi-tenant isolation via tenantId.
 *   • Role-based access control (RBAC) with role linkage + permission overrides.
 *   • Secure password hashing with bcrypt and optional pepper.
 *   • Email verification + password reset flows.
 *   • Audit fields for compliance and accountability.
 * - Security:
 *   • Never store plaintext passwords.
 *   • Always use setPassword() to hash before save.
 *   • comparePassword() handles timing attacks consistently.
 * - Engineers:
 *   • Keep this as the single source of truth for User schema.
 *   • Do not duplicate models in other folders; import from here.
 *   • Extend cautiously; document rationale for new fields.
 * -----------------------------------------------------------------------------
 */

'use strict';

const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const PEPPER = process.env.PASSWORD_PEPPER || ''; // Optional additional secret
const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12', 10);

const userSchema = new mongoose.Schema({
    // Tenant isolation
    tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true },

    // Identity
    name: { type: String, required: true, trim: true, index: true },
    email: { type: String, required: true, lowercase: true, trim: true, unique: true, index: true },

    // Auth
    passwordHash: { type: String, required: true, select: false },
    emailVerified: { type: Boolean, default: false },
    verificationToken: { type: String, default: null },
    verificationTokenExpiresAt: { type: Date, default: null },
    resetToken: { type: String, default: null },
    resetTokenExpiresAt: { type: Date, default: null },

    // RBAC
    role: { type: String, enum: ['ADMIN', 'SHERIFF', 'STAFF', 'USER'], default: 'USER', index: true },
    roleId: { type: mongoose.Schema.Types.ObjectId, ref: 'Role', index: true },
    permissionOverrides: { type: [String], default: [] },

    // Account status
    active: { type: Boolean, default: true, index: true },

    // Audit
    lastLoginAt: { type: Date, default: null },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', default: null },
    updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', default: null }
}, { timestamps: true });

// Compound indexes
userSchema.index({ tenantId: 1, email: 1 }, { unique: true });
userSchema.index({ roleId: 1, active: 1 });

// --- METHODS ---

// Hash password before save
userSchema.methods.setPassword = async function setPassword(plaintext) {
    const salted = `${plaintext}${PEPPER}`;
    this.passwordHash = await bcrypt.hash(salted, BCRYPT_ROUNDS);
};

// Compare candidate password
userSchema.methods.comparePassword = async function comparePassword(plaintext) {
    const salted = `${plaintext}${PEPPER}`;
    return bcrypt.compare(salted, this.passwordHash);
};

// Idempotent export to avoid overwrite errors
const User = mongoose.models.User || mongoose.model('User', userSchema);
module.exports = User;
