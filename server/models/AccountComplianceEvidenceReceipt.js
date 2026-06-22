/* eslint-disable */
import mongoose from 'mongoose';

const { Schema } = mongoose;

/**
 * @function buildAccountComplianceEvidenceReceiptSchema
 * @description Builds the schema for explicit Account Compliance evidence receipts.
 * @returns {Schema} Mongoose schema for immutable account compliance receipt rows.
 * @collaboration Stores real tenant-scoped evidence hashes used by Account Command Center compliance dossiers.
 */
export function buildAccountComplianceEvidenceReceiptSchema() {
  const AccountComplianceEvidenceReceiptSchema = new Schema(
    {
      tenantId: { type: String, required: true, index: true },
      receiptId: { type: String, required: true, unique: true, index: true },
      reason: { type: String, required: true },
      actor: { type: String, default: 'system' },
      source: { type: String, default: 'account-compliance-evidence-command' },
      status: { type: String, default: 'SEALED', index: true },
      evidenceHash: { type: String, required: true, index: true },
      merkleRoot: { type: String, required: true, index: true },
      previousMerkleRoot: { type: String, default: '' },
      payload: { type: Schema.Types.Mixed, default: {} },
      complianceBindings: { type: [Schema.Types.Mixed], default: [] },
      generatedAt: { type: Date, default: Date.now, index: true },
    },
    {
      collection: 'account_compliance_evidence_receipts',
      strict: true,
      timestamps: true,
    }
  );

  AccountComplianceEvidenceReceiptSchema.index({ tenantId: 1, generatedAt: -1 });
  AccountComplianceEvidenceReceiptSchema.index({ tenantId: 1, merkleRoot: 1 });

  return AccountComplianceEvidenceReceiptSchema;
}

const AccountComplianceEvidenceReceipt =
  mongoose.models.AccountComplianceEvidenceReceipt ||
  mongoose.model('AccountComplianceEvidenceReceipt', buildAccountComplianceEvidenceReceiptSchema());

export default AccountComplianceEvidenceReceipt;
