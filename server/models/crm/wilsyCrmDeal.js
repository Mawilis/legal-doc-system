/* eslint-disable */
/**
 * @fileoverview Wilsy CRM deal model.
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
 * @function buildWilsyCrmDealSchema
 * @description Builds the Wilsy CRM deal schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists pipeline opportunities for weighted revenue and governance readiness.
 */
function buildWilsyCrmDealSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      title: { type: String, trim: true, index: true, required: true },
      accountId: { type: Schema.Types.ObjectId, ref: 'CRMAccount', index: true, default: null },
      contactId: { type: Schema.Types.ObjectId, ref: 'CRMContact', index: true, default: null },
      stage: { type: String, trim: true, index: true, default: 'Prospecting' },
      amount: { type: Number, min: 0, default: 0 },
      currency: { type: String, trim: true, uppercase: true, default: 'ZAR' },
      probability: { type: Number, min: 0, max: 100, default: 10 },
      expectedCloseDate: { type: Date, default: null },
      forecastCategory: { type: String, trim: true, index: true, default: 'PIPELINE' },
      complianceGate: { type: String, trim: true, index: true, default: 'PENDING' },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_deals')
  );

  schema.index({ tenantId: 1, stage: 1, updatedAt: -1 });
  schema.index({ tenantId: 1, forecastCategory: 1 });

  return schema;
}

const WilsyCrmDeal = getOrCreateModel('CRMDeal', buildWilsyCrmDealSchema());

export { buildWilsyCrmDealSchema };
export default WilsyCrmDeal;
