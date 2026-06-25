/* eslint-disable */
/**
 * @fileoverview Wilsy CRM lead model.
 */

import {
  Schema,
  buildCrmAuditTrailSchema,
  buildCrmEvidenceSchema,
  buildCrmSchemaOptions,
  buildCrmTenantFields,
  getOrCreateModel,
} from './wilsyCrmBaseSchemas.js';

/**
 * @function buildWilsyCrmLeadSchema
 * @description Builds the Wilsy CRM lead schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists prospecting and lead qualification records for live CRM source posture.
 */
function buildWilsyCrmLeadSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      firstName: { type: String, trim: true, default: null },
      surname: { type: String, trim: true, default: null },
      fullName: { type: String, trim: true, index: true, default: null },
      companyName: { type: String, trim: true, index: true, default: null },
      email: { type: String, trim: true, lowercase: true, index: true, default: null },
      phone: { type: String, trim: true, default: null },
      stage: { type: String, trim: true, index: true, default: 'Prospecting' },
      score: { type: Number, min: 0, max: 100, default: 0 },
      priority: { type: String, trim: true, index: true, default: 'NORMAL' },
      consentBasis: { type: String, trim: true, default: null },
      sourceChannel: { type: String, trim: true, index: true, default: 'manual' },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_leads')
  );

  schema.index({ tenantId: 1, email: 1 });
  schema.index({ tenantId: 1, stage: 1, updatedAt: -1 });

  return schema;
}

const WilsyCrmLead = getOrCreateModel('CRMLead', buildWilsyCrmLeadSchema());

export { buildWilsyCrmLeadSchema };
export default WilsyCrmLead;
