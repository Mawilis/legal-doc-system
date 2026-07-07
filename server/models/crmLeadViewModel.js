/* eslint-disable */
const mongoose = require('mongoose');

const crmLeadViewCriterionSchema = new mongoose.Schema(
  {
    field: { type: String, required: true, trim: true },
    operator: { type: String, required: true, trim: true },
    value: { type: mongoose.Schema.Types.Mixed, default: '' },
    valueLabel: { type: String, default: '', trim: true },
  },
  { _id: false }
);

const crmLeadViewAuditSchema = new mongoose.Schema(
  {
    auditReceiptId: { type: String, required: true, index: true },
    action: { type: String, required: true, trim: true },
    route: { type: String, required: true, trim: true },
    operatorUserId: { type: String, default: 'system', trim: true },
    tenantId: { type: String, required: true, index: true, trim: true },
    criteriaHash: { type: String, default: '', trim: true },
    resultCount: { type: Number, default: 0 },
    generatedAt: { type: Date, default: Date.now },
    institutionalHeaders: { type: mongoose.Schema.Types.Mixed, default: {} },
    strikePayload: { type: mongoose.Schema.Types.Mixed, default: {} },
  },
  { _id: false }
);

const crmLeadViewSchema = new mongoose.Schema(
  {
    tenantId: { type: String, required: true, index: true, trim: true },
    ownerUserId: { type: String, required: true, index: true, trim: true },
    createdBy: { type: String, required: true, trim: true },
    updatedBy: { type: String, required: true, trim: true },
    module: { type: String, default: 'crm.leads', index: true, trim: true },
    name: { type: String, required: true, trim: true },
    description: { type: String, default: '', trim: true },
    visibility: {
      type: String,
      enum: ['private', 'team', 'tenant', 'role'],
      default: 'private',
      index: true,
    },
    status: {
      type: String,
      enum: ['active', 'archived'],
      default: 'active',
      index: true,
    },
    criteria: { type: [crmLeadViewCriterionSchema], default: [] },
    columns: { type: [String], default: [] },
    sort: {
      field: { type: String, default: 'updatedAt', trim: true },
      direction: { type: String, enum: ['asc', 'desc'], default: 'desc' },
    },
    pinned: { type: Boolean, default: false },
    criteriaHash: { type: String, default: '', index: true, trim: true },
    ruleEngineVersion: { type: String, default: 'wilsy-lead-category-engine-v1', trim: true },
    lastRun: {
      count: { type: Number, default: 0 },
      totalScopeCount: { type: Number, default: 0 },
      sampleLeadIds: { type: [String], default: [] },
      durationMs: { type: Number, default: 0 },
      executedAt: { type: Date },
    },
    auditTrail: { type: [crmLeadViewAuditSchema], default: [] },
    metadata: {
      source: { type: String, default: 'lead-custom-view-builder', trim: true },
      uiVersion: { type: String, default: 'FG98', trim: true },
      localFallbackId: { type: String, default: '', trim: true },
    },
  },
  {
    timestamps: true,
    minimize: false,
  }
);

crmLeadViewSchema.index({ tenantId: 1, ownerUserId: 1, name: 1, status: 1 });
crmLeadViewSchema.index({ tenantId: 1, visibility: 1, status: 1, updatedAt: -1 });

/**
 * @function buildCrmLeadViewModel
 * @description Returns the CRM Lead View mongoose model without recompiling it during hot reloads.
 * @collaboration Lead View Registry, CRM Leads, Wilsy AI, tenant evidence, and audit persistence.
 * @returns {mongoose.Model} CRM Lead View model.
 */
function buildCrmLeadViewModel() {
  return mongoose.models.CrmLeadView || mongoose.model('CrmLeadView', crmLeadViewSchema);
}

module.exports = buildCrmLeadViewModel();
