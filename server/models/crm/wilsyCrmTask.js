/* eslint-disable */
/**
 * @fileoverview Wilsy CRM task model.
 */

import {
  Schema,
  buildCrmAuditTrailSchema,
  buildCrmSchemaOptions,
  buildCrmTenantFields,
  getOrCreateModel,
} from './wilsyCrmBaseSchemas.js';

/**
 * @function buildWilsyCrmTaskSchema
 * @description Builds the Wilsy CRM task schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists next-action work items for CRM execution.
 */
function buildWilsyCrmTaskSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      title: { type: String, trim: true, index: true, required: true },
      description: { type: String, trim: true, default: null },
      relatedType: { type: String, trim: true, index: true, default: null },
      relatedId: { type: String, trim: true, index: true, default: null },
      dueAt: { type: Date, default: null },
      priority: { type: String, trim: true, index: true, default: 'NORMAL' },
      completedAt: { type: Date, default: null },
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_tasks')
  );

  schema.index({ tenantId: 1, status: 1, dueAt: 1 });

  return schema;
}

const WilsyCrmTask = getOrCreateModel('CRMTask', buildWilsyCrmTaskSchema());

export { buildWilsyCrmTaskSchema };
export default WilsyCrmTask;
