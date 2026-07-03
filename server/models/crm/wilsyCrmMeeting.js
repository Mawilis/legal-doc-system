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
      subject: { type: String, trim: true, index: true, default: null },
      meetingTitle: { type: String, trim: true, index: true, default: null },
      meetingType: { type: String, trim: true, index: true, default: 'DISCOVERY' },
      status: { type: String, trim: true, index: true, default: 'SCHEDULED' },
      startsAt: { type: Date, index: true, default: null },
      endsAt: { type: Date, default: null },
      fromDate: { type: String, trim: true, default: '' },
      fromTime: { type: String, trim: true, default: '' },
      toDate: { type: String, trim: true, default: '' },
      toTime: { type: String, trim: true, default: '' },
      meetingVenue: { type: String, trim: true, index: true, default: '' },
      venue: { type: String, trim: true, index: true, default: '' },
      venueType: { type: String, trim: true, default: '' },
      meetingVenueLabel: { type: String, trim: true, default: '' },
      locationType: { type: String, trim: true, default: '' },
      location: { type: String, trim: true, default: '' },
      host: { type: String, trim: true, default: '' },
      participants: [{ type: Schema.Types.Mixed }],
      attendees: [{ type: Schema.Types.Mixed }],
      relatedType: { type: String, trim: true, index: true, default: null },
      relatedId: { type: String, trim: true, index: true, default: null },
      relatedRecord: { type: Schema.Types.Mixed, default: null },
      relatedTo: { type: Schema.Types.Mixed, default: null },
      repeat: { type: String, trim: true, default: 'None' },
      reminder: { type: String, trim: true, default: 'None' },
      description: { type: String, trim: true, default: '' },
      agenda: { type: String, trim: true, default: '' },
      outcome: { type: String, trim: true, default: null },
      sourceStatus: { type: String, trim: true, index: true, default: 'SOURCE_LIVE' },
      persistenceStatus: { type: String, trim: true, index: true, default: 'DB_PERSISTED' },
      wilsyVenuePersistence: { type: Schema.Types.Mixed, default: null },
      calendarUid: { type: String, trim: true, index: true, default: '' },
      calendarSequence: { type: Number, default: 0 },
      calendarInvite: { type: Schema.Types.Mixed, default: null },
      invitationStatus: { type: String, trim: true, index: true, default: 'NOT_SENT' },
      lastInviteSentAt: { type: Date, default: null },
      emailInvitationReceipts: [{ type: Schema.Types.Mixed }],
      smsInvitationReceipts: [{ type: Schema.Types.Mixed }],
      notificationReceipts: [{ type: Schema.Types.Mixed }],
      rescheduleRequests: [{ type: Schema.Types.Mixed }],
      meetingNotificationIntelligence: { type: Schema.Types.Mixed, default: null },
      wilsyMeetingNotificationContract: { type: String, trim: true, default: '' },
      auditMesh: { type: Schema.Types.Mixed, default: null },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_meetings')
  );

  schema.index({ tenantId: 1, startsAt: -1 });
  schema.index({ tenantId: 1, meetingVenue: 1, status: 1 });
  schema.index({ tenantId: 1, host: 1, updatedAt: -1 });
  schema.index({ tenantId: 1, invitationStatus: 1, lastInviteSentAt: -1 });

  return schema;
}

const WilsyCrmMeeting = getOrCreateModel('CRMMeeting', buildWilsyCrmMeetingSchema());

export { buildWilsyCrmMeetingSchema };
export default WilsyCrmMeeting;
