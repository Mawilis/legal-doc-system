/* eslint-disable */
/**
 * @fileoverview Wilsy CRM meeting model.
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
 * @function buildWilsyCrmMeetingSchema
 * @description Builds the Wilsy CRM meeting schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists CRM meeting records and discovery outcomes.
 */
function buildWilsyCrmMeetingSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      title: { type: String, trim: true, required: true },
      meetingType: { type: String, trim: true, index: true, default: 'DISCOVERY' },
      startsAt: { type: Date, index: true, default: null },
      endsAt: { type: Date, default: null },
      attendees: [{ type: String, trim: true }],
      relatedType: { type: String, trim: true, index: true, default: null },
      relatedId: { type: String, trim: true, index: true, default: null },
      outcome: { type: String, trim: true, default: null },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_meetings')
  );

  schema.index({ tenantId: 1, startsAt: -1 });

  return schema;
}

const WilsyCrmMeeting = getOrCreateModel('CRMMeeting', buildWilsyCrmMeetingSchema());

export { buildWilsyCrmMeetingSchema };
export default WilsyCrmMeeting;
