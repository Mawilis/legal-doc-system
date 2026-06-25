/* eslint-disable */
/**
 * @fileoverview Wilsy CRM connector model.
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
 * @function buildWilsyCrmConnectorSchema
 * @description Builds the Wilsy CRM connector schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Persists connector posture for source graph readiness without exposing credentials.
 */
function buildWilsyCrmConnectorSchema() {
  const schema = new Schema(
    {
      ...buildCrmTenantFields(),
      connectorKey: { type: String, trim: true, index: true, required: true },
      label: { type: String, trim: true, required: true },
      provider: { type: String, trim: true, index: true, default: 'CUSTOM' },
      connectionStatus: { type: String, trim: true, index: true, default: 'DISCONNECTED' },
      lastSyncAt: { type: Date, default: null },
      syncHealth: { type: String, trim: true, default: 'UNKNOWN' },
      scopes: [{ type: String, trim: true }],
      secretRef: { type: String, trim: true, default: null },
      evidence: [buildCrmEvidenceSchema()],
      auditTrail: [buildCrmAuditTrailSchema()],
    },
    buildCrmSchemaOptions('crm_connectors')
  );

  schema.index({ tenantId: 1, connectorKey: 1 }, { unique: false });
  schema.index({ tenantId: 1, connectionStatus: 1 });

  return schema;
}

const WilsyCrmConnector = getOrCreateModel('CRMConnector', buildWilsyCrmConnectorSchema());

export { buildWilsyCrmConnectorSchema };
export default WilsyCrmConnector;
