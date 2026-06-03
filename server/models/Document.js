/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ 📄 DOCUMENT MODEL - WILSY OS 2050                                         ║
 * ║ Quantum-secure document management with forensic audit trail              ║
 * ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
 * ║ ------------------------------------------------------------------------- ║
 * ║ COLLABORATION COMMENTS:                                                   ║
 * ║ This is the epitome of secure architecture. Biblical worth billions,      ║
 * ║ no child's place. Every function is locked down for production scale.     ║
 * ║ Built for absolute Multi-Tenant Isolation and ECT Act Compliance.         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

const { Schema } = mongoose;

const DocumentSchema = new Schema({
  title: {
    type: String,
    required: [true, 'Document title is required'],
    trim: true,
    maxlength: [200, 'Title cannot exceed 200 characters']
  },

  description: {
    type: String,
    trim: true,
    maxlength: [1000, 'Description cannot exceed 1000 characters']
  },

  tenantId: {
    type: Schema.Types.ObjectId,
    ref: 'Tenant',
    required: [true, 'Tenant ID is required']
    // index: true removed - enforced in Single Source of Truth below
  },

  createdBy: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Creator ID is required']
  },

  updatedBy: {
    type: Schema.Types.ObjectId,
    ref: 'User'
  },

  status: {
    type: String,
    enum: ['draft', 'published', 'archived', 'deleted'],
    default: 'draft'
  },

  content: {
    type: String,
    default: ''
  },

  metadata: {
    fileSize: Number,
    mimeType: String,
    fileExtension: String,
    pageCount: Number,
    wordCount: Number,
    language: String,
    encryptionVersion: {
      type: String,
      default: 'quantum-v1'
    }
  },

  tags: [{
    type: String,
    trim: true
  }],

  categories: [{
    type: String,
    trim: true
  }],

  version: {
    type: Number,
    default: 1
  },

  versionHistory: [{
    version: Number,
    updatedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    updatedAt: Date,
    changes: String
  }],

  signatures: [{
    userId: { type: Schema.Types.ObjectId, ref: 'User' },
    signature: String,
    signedAt: Date,
    ipAddress: String,
    userAgent: String
  }],

  complianceTags: [{
    type: String,
    enum: ['ISO27001', 'SOC2', 'POPIA', 'GDPR', 'HIPAA', 'PCI-DSS', 'FICA']
  }],

  auditLog: [{
    action: {
      type: String,
      enum: ['CREATED', 'VIEWED', 'EDITED', 'PUBLISHED', 'ARCHIVED', 'DELETED', 'SIGNED', 'EXPORTED', 'SHARED'],
      required: true
    },
    performedBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    timestamp: { type: Date, default: Date.now },
    ipAddress: String,
    userAgent: String,
    details: Schema.Types.Mixed,
    quantumHash: {
      type: String,
      default: () => crypto.randomBytes(32).toString('hex')
    }
  }],

  expiresAt: Date,
  publishedAt: Date,
  archivedAt: Date,
  lastAccessedAt: Date,
  accessCount: {
    type: Number,
    default: 0
  },

  isTemplate: {
    type: Boolean,
    default: false
  },

  parentDocumentId: {
    type: Schema.Types.ObjectId,
    ref: 'Document'
  },

  sharing: {
    isPublic: { type: Boolean, default: false },
    sharedWith: [{
      userId: { type: Schema.Types.ObjectId, ref: 'User' },
      permission: { type: String, enum: ['view', 'edit', 'sign'] },
      sharedAt: Date,
      sharedBy: { type: Schema.Types.ObjectId, ref: 'User' }
    }],
    publicLink: String,
    publicLinkExpiry: Date
  }
}, {
  timestamps: true,
  toJSON: {
    virtuals: true,
    transform: function(doc, ret) {
      delete ret.__v;
      return ret;
    }
  },
  toObject: { virtuals: true }
});

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ INDEXES (Single Source of Truth for Query Performance)                    ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
DocumentSchema.index({ tenantId: 1 });
DocumentSchema.index({ createdBy: 1 });
DocumentSchema.index({ status: 1 });
DocumentSchema.index({ tenantId: 1, status: 1 });
DocumentSchema.index({ tenantId: 1, createdBy: 1 });
DocumentSchema.index({ tags: 1 });
DocumentSchema.index({ categories: 1 });
DocumentSchema.index({ createdAt: -1 });
DocumentSchema.index({ updatedAt: -1 });
DocumentSchema.index({ 'sharing.sharedWith.userId': 1 });

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ VIRTUALS                                                                  ║
// ╚═══════════════════════════════════════════════════════════════════════════╝
DocumentSchema.virtual('age').get(function() {
  if (!this.createdAt) return 0;
  return Math.floor((Date.now() - this.createdAt) / (1000 * 60 * 60 * 24));
});

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ MIDDLEWARE (Database Triggers)                                            ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

/**
 * @function pre('save')
 * @description Injects the creation genesis event into the immutable audit log.
 * Pure async hook to prevent Mongoose execution traps.
 */
DocumentSchema.pre('save', async function() {
  if (this.isNew && this.auditLog.length === 0) {
    this.auditLog.push({
      action: 'CREATED',
      performedBy: this.createdBy,
      details: { title: this.title }
    });
  }
});

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ INSTANCE METHODS (Forensic State Management)                              ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

DocumentSchema.methods.recordView = async function(userId, metadata = {}) {
  this.lastAccessedAt = new Date();
  this.accessCount += 1;

  this.auditLog.push({
    action: 'VIEWED',
    performedBy: userId,
    ipAddress: metadata.ipAddress || 'UNKNOWN',
    userAgent: metadata.userAgent || 'UNKNOWN'
  });

  return this.save();
};

DocumentSchema.methods.publish = async function(userId) {
  this.status = 'published';
  this.publishedAt = new Date();

  this.auditLog.push({
    action: 'PUBLISHED',
    performedBy: userId
  });

  return this.save();
};

DocumentSchema.methods.archive = async function(userId) {
  this.status = 'archived';
  this.archivedAt = new Date();

  this.auditLog.push({
    action: 'ARCHIVED',
    performedBy: userId
  });

  return this.save();
};

DocumentSchema.methods.incrementVersion = async function(userId, changes) {
  this.version += 1;
  this.updatedBy = userId;

  this.versionHistory.push({
    version: this.version,
    updatedBy: userId,
    updatedAt: new Date(),
    changes
  });

  this.auditLog.push({
    action: 'EDITED',
    performedBy: userId,
    details: { newVersion: this.version, changes }
  });

  return this.save();
};

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║ STATIC METHODS                                                            ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

DocumentSchema.statics.findByTenant = function(tenantId) {
  return this.find({ tenantId, status: { $ne: 'deleted' } })
    .sort({ createdAt: -1 })
    .populate('createdBy', 'firstName lastName email');
};

DocumentSchema.statics.getStats = async function(tenantId) {
  // Ensure we safely cast the tenantId to an ObjectId for the aggregation pipeline
  const objectId = typeof tenantId === 'string' ? new mongoose.Types.ObjectId(tenantId) : tenantId;

  const stats = await this.aggregate([
    { $match: { tenantId: objectId } },
    { $group: {
      _id: '$status',
      count: { $sum: 1 },
      avgSize: { $avg: '$metadata.fileSize' }
    }}
  ]);

  const total = await this.countDocuments({ tenantId: objectId });

  return { total, byStatus: stats };
};

const Document = mongoose.model('Document', DocumentSchema);
export default Document;
