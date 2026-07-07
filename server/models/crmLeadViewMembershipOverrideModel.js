/* eslint-disable */
import mongoose from 'mongoose';

const crmLeadViewMembershipOverrideSchema = new mongoose.Schema(
  {
    tenantId: { type: String, required: true, index: true, trim: true },
    viewId: { type: String, required: true, index: true, trim: true },
    leadId: { type: String, required: true, index: true, trim: true },
    mode: {
      type: String,
      required: true,
      enum: ['include', 'exclude'],
      index: true,
    },
    reason: { type: String, default: '', trim: true },
    status: {
      type: String,
      enum: ['active', 'cleared'],
      default: 'active',
      index: true,
    },
    createdBy: { type: String, required: true, trim: true },
    updatedBy: { type: String, required: true, trim: true },
    institutionalHeaders: { type: mongoose.Schema.Types.Mixed, default: {} },
    strikePayload: { type: mongoose.Schema.Types.Mixed, default: {} },
  },
  {
    timestamps: true,
    minimize: false,
  }
);

crmLeadViewMembershipOverrideSchema.index({ tenantId: 1, viewId: 1, leadId: 1 }, { unique: true });
crmLeadViewMembershipOverrideSchema.index({ tenantId: 1, viewId: 1, mode: 1, status: 1 });
crmLeadViewMembershipOverrideSchema.index({ tenantId: 1, leadId: 1, status: 1 });

/**
 * @function buildCrmLeadViewMembershipOverrideModel
 * @description Returns the CRM Lead View membership override model without recompiling during hot reloads.
 * @returns {mongoose.Model} CRM Lead View membership override model.
 * @collaboration Lead View Registry, selected-row membership controls, audit evidence, and live collection execution.
 */
function buildCrmLeadViewMembershipOverrideModel() {
  return (
    mongoose.models.CrmLeadViewMembershipOverride ||
    mongoose.model('CrmLeadViewMembershipOverride', crmLeadViewMembershipOverrideSchema)
  );
}

const CrmLeadViewMembershipOverride = buildCrmLeadViewMembershipOverrideModel();

export { buildCrmLeadViewMembershipOverrideModel };
export default CrmLeadViewMembershipOverride;
