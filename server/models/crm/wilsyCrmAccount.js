/* eslint-disable */
/**
 * @fileoverview Wilsy CRM account model.
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
 * @function buildWilsyCrmAccountSchema
 * @description Builds the Wilsy CRM account schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists account records for enterprise CRM source posture and deal linkage.
 */
function buildWilsyCrmAccountSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      name: { type: String, trim: true, index: true, required: true },
      legalName: { type: String, trim: true, default: null },
      registrationNumber: { type: String, trim: true, index: true, default: null },
      industry: { type: String, trim: true, default: null },
      website: { type: String, trim: true, default: null },
      accountTier: { type: String, trim: true, index: true, default: 'STANDARD' },
      lifecycleStage: { type: String, trim: true, index: true, default: 'PROSPECT' },
      complianceStatus: { type: String, trim: true, index: true, default: 'PENDING' },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_accounts')
  );

  schema.index({ tenantId: 1, name: 1 });
  schema.index({ tenantId: 1, lifecycleStage: 1 });

  return schema;
}

const WilsyCrmAccount = getOrCreateModel('CRMAccount', buildWilsyCrmAccountSchema());

export { buildWilsyCrmAccountSchema };
export default WilsyCrmAccount;
