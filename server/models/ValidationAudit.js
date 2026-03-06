#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - VALIDATION AUDIT MODEL                                         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

// Export constants
export const AUDIT_ACTIONS = {
  CASE_CREATED: 'CASE_CREATED',
  CASE_UPDATED: 'CASE_UPDATED',
  CASE_DELETED: 'CASE_DELETED',
  DOCUMENT_UPLOADED: 'DOCUMENT_UPLOADED',
  DOCUMENT_VIEWED: 'DOCUMENT_VIEWED',
  DOCUMENT_DOWNLOADED: 'DOCUMENT_DOWNLOADED',
};

export const AUDIT_STATUS = {
  SUCCESS: 'SUCCESS',
  FAILURE: 'FAILURE',
  PENDING: 'PENDING',
};

export const SEVERITY_LEVELS = {
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL',
};

export const RETENTION_POLICIES = {
  COMPANIES_ACT_10_YEARS: 'COMPANIES_ACT_10_YEARS',
  POPIA_1_YEAR: 'POPIA_1_YEAR',
};

export const DATA_RESIDENCY = {
  ZA: 'ZA',
  US: 'US',
  EU: 'EU',
};

const validationAuditSchema = new mongoose.Schema(
  {
    tenantId: {
      type: String,
      required: true,
      index: true,
    },
    action: {
      type: String,
      enum: Object.values(AUDIT_ACTIONS),
      required: true,
    },
    status: {
      type: String,
      enum: Object.values(AUDIT_STATUS),
      required: true,
    },
    severity: {
      type: String,
      enum: Object.values(SEVERITY_LEVELS),
      required: true,
    },
    resourceId: String,
    userId: String,
    ipAddress: String,
    userAgent: String,
    details: mongoose.Schema.Types.Mixed,
    forensicHash: String,
    retentionPolicy: {
      type: String,
      enum: Object.values(RETENTION_POLICIES),
      default: RETENTION_POLICIES.COMPANIES_ACT_10_YEARS,
    },
    dataResidency: {
      type: String,
      enum: Object.values(DATA_RESIDENCY),
      default: DATA_RESIDENCY.ZA,
    },
    retentionEnd: Date,
  },
  {
    timestamps: true,
  },
);

// Pre-save middleware to set retention end
validationAuditSchema.pre('save', function (next) {
  if (!this.retentionEnd) {
    const endDate = new Date();
    if (this.retentionPolicy === RETENTION_POLICIES.COMPANIES_ACT_10_YEARS) {
      endDate.setFullYear(endDate.getFullYear() + 10);
    } else if (this.retentionPolicy === RETENTION_POLICIES.POPIA_1_YEAR) {
      endDate.setFullYear(endDate.getFullYear() + 1);
    }
    this.retentionEnd = endDate;
  }
  return;
});

// Static methods
validationAuditSchema.statics.findByTenant = function (tenantId) {
  return this.find({ tenantId }).sort({ createdAt: -1 });
};

validationAuditSchema.statics.findByAction = function (action) {
  return this.find({ action }).sort({ createdAt: -1 });
};

validationAuditSchema.statics.findBySeverity = function (severity) {
  return this.find({ severity }).sort({ createdAt: -1 });
};

const ValidationAudit = mongoose.model('ValidationAudit', validationAuditSchema);

export default ValidationAudit;
