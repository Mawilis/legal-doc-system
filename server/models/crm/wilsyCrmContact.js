/* eslint-disable */
/**
 * @fileoverview Wilsy CRM contact model.
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
 * @function buildWilsyCrmContactSchema
 * @description Builds the Wilsy CRM contact schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists stakeholder identities for CRM account and deal operations.
 */
function buildWilsyCrmContactSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      firstName: { type: String, trim: true, default: null },
      surname: { type: String, trim: true, default: null },
      fullName: { type: String, trim: true, index: true, default: null },
      title: { type: String, trim: true, default: null },
      role: { type: String, trim: true, default: null },
      email: { type: String, trim: true, lowercase: true, index: true, default: null },
      phone: { type: String, trim: true, default: null },
      accountId: { type: Schema.Types.ObjectId, ref: 'CRMAccount', index: true, default: null },
      decisionRole: { type: String, trim: true, default: null },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_contacts')
  );

  schema.index({ tenantId: 1, email: 1 });
  schema.index({ tenantId: 1, accountId: 1 });

  return schema;
}

const WilsyCrmContact = getOrCreateModel('CRMContact', buildWilsyCrmContactSchema());

export { buildWilsyCrmContactSchema };
export default WilsyCrmContact;
