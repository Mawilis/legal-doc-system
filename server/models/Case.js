/* eslint-disable */
import mongoose from 'mongoose';

const { Schema } = mongoose;

/**
 * @function buildWilsyCaseSchema
 * @description Builds the flexible Case schema required to register the Case model for compliance services.
 * @returns {Schema} Mongoose schema for tenant-scoped case documents.
 * @collaboration Allows CaseComplianceService to query the real cases collection without fabricating case records.
 */
export function buildWilsyCaseSchema() {
  const CaseSchema = new Schema(
    {
      tenantId: { type: String, index: true },
      caseId: { type: String, index: true },
      matterId: { type: String, index: true },
      clientId: { type: String, index: true },
      status: { type: String, index: true },
      complianceStatus: { type: String, index: true },
      riskLevel: { type: String, index: true },
      metadata: { type: Schema.Types.Mixed, default: {} },
      compliance: { type: Schema.Types.Mixed, default: {} },
      audit: { type: Schema.Types.Mixed, default: {} },
    },
    {
      collection: 'cases',
      strict: false,
      timestamps: true,
    }
  );

  CaseSchema.index({ tenantId: 1, createdAt: -1 });
  CaseSchema.index({ tenantId: 1, status: 1 });
  CaseSchema.index({ tenantId: 1, complianceStatus: 1 });

  return CaseSchema;
}

const CaseModel = mongoose.models.Case || mongoose.model('Case', buildWilsyCaseSchema());

export default CaseModel;
