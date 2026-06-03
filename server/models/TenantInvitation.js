/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  📨 TENANT INVITATION MODEL - WILSY OS 2050 (V10.2)                      ║
  ║  Quantum-secure invitation system with forensic audit trail              ║
  ║  Supreme Architect: Wilson Khanyezi - 10th Generation                    ║
  ║  Surgical Fix: Async Middleware & Index Synchronization                   ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import mongoose from 'mongoose';
import { ROLES } from '../constants/roles.js';
import crypto from 'crypto';

const { Schema } = mongoose;

const TenantInvitationSchema = new Schema({
  tenantId: { type: Schema.Types.ObjectId, ref: 'Tenant', required: true },
  email: { type: String, required: true, lowercase: true, trim: true },
  role: { type: String, enum: Object.values(ROLES), required: true },
  invitedBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  token: { type: String, required: true, default: () => crypto.randomBytes(48).toString('base64url') },
  expiresAt: { type: Date, required: true, default: () => new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) },
  status: {
    type: String,
    enum: ['pending', 'sent', 'accepted', 'expired', 'revoked', 'cancelled'],
    default: 'pending'
  },
  metadata: {
    invitedAt: { type: Date, default: Date.now, immutable: true },
    acceptedAt: Date,
    ipAddress: String,
    userAgent: String
  },
  auditLog: [{
    action: String,
    timestamp: { type: Date, default: Date.now },
    performedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    ipAddress: String,
    userAgent: String,
    quantumHash: { type: String, default: () => crypto.randomBytes(64).toString('hex') }
  }]
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// INDEXES - Consolidated to prevent duplicates
TenantInvitationSchema.index({ token: 1 }, { unique: true });
TenantInvitationSchema.index({ email: 1, tenantId: 1 });
TenantInvitationSchema.index({ status: 1 });
TenantInvitationSchema.index({ expiresAt: 1 });

// --- INSTANCE METHODS ---
TenantInvitationSchema.methods.recordView = async function(metadata = {}) {
  this.auditLog.push({
    action: 'INVITATION_VIEWED',
    ipAddress: metadata.ipAddress,
    userAgent: metadata.userAgent
  });
  return await this.save();
};

TenantInvitationSchema.methods.isExpired = function() {
  return this.expiresAt < new Date() || this.status === 'expired';
};

// --- STATIC METHODS ---
TenantInvitationSchema.statics.cleanupExpired = async function() {
  return await this.updateMany(
    { status: { $in: ['pending', 'sent'] }, expiresAt: { $lt: new Date() } },
    { $set: { status: 'expired' } }
  );
};

TenantInvitationSchema.statics.findValid = function(token) {
  return this.findOne({
    token,
    status: { $in: ['pending', 'sent'] },
    expiresAt: { $gt: new Date() }
  }).populate('tenantId invitedBy');
};

// --- MIDDLEWARE: ASYNC PATTERN ---
// By removing 'next', Mongoose correctly handles the returned promise/async execution.
TenantInvitationSchema.pre('save', async function() {
  if (this.isNew) {
    this.auditLog.push({
      action: 'INVITATION_CREATED',
      performedBy: this.invitedBy,
      timestamp: new Date()
    });
  }
});

const TenantInvitation = mongoose.models.TenantInvitation || mongoose.model('TenantInvitation', TenantInvitationSchema);
export default TenantInvitation;
