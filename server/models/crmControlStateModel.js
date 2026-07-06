/* eslint-disable */
import mongoose from 'mongoose';

/**
 * @function buildCrmControlStateModel
 * @description Builds the CRM control state model for persisted operator UI selections.
 * @returns {*} CRM control state model.
 * @collaboration Leads filter buttons, tenant-scoped operator preferences, institutional evidence, backend persistence, and CRM control surfaces.
 */
function buildCrmControlStateModel() {
  const crmControlStateSchema = new mongoose.Schema(
    {
      tenantId: { type: String, required: true, index: true },
      operatorId: { type: String, required: true, index: true },
      moduleKey: { type: String, required: true, index: true },
      surfaceKey: { type: String, required: true, index: true },
      stateKey: { type: String, required: true, index: true },
      selectedFilters: { type: [String], default: [] },
      controlState: { type: mongoose.Schema.Types.Mixed, default: {} },
      institutionalHeaders: { type: mongoose.Schema.Types.Mixed, default: {} },
      strikePayload: { type: mongoose.Schema.Types.Mixed, default: {} },
      evidenceLedger: { type: [mongoose.Schema.Types.Mixed], default: [] },
      generatedAt: { type: Date, default: Date.now },
    },
    {
      timestamps: true,
      collection: 'crm_control_states',
    }
  );

  crmControlStateSchema.index(
    {
      tenantId: 1,
      operatorId: 1,
      moduleKey: 1,
      surfaceKey: 1,
      stateKey: 1,
    },
    {
      unique: true,
      name: 'crm_control_state_unique_scope',
    }
  );

  return (
    mongoose.models.CrmControlState || mongoose.model('CrmControlState', crmControlStateSchema)
  );
}

const CrmControlState = buildCrmControlStateModel();

export default CrmControlState;
