/* eslint-disable */
import mongoose from 'mongoose';

const knowledgeBaseVaultReceiptSchema = new mongoose.Schema(
  {
    tenantId: {
      type: String,
      required: true,
      index: true,
      trim: true,
    },
    operatorId: {
      type: String,
      required: true,
      index: true,
      trim: true,
    },
    userId: {
      type: String,
      index: true,
      trim: true,
      default: '',
    },
    artifactId: {
      type: String,
      index: true,
      trim: true,
      default: '',
    },
    artifactTitle: {
      type: String,
      trim: true,
      default: '',
    },
    artifactCategory: {
      type: String,
      trim: true,
      default: '',
    },
    actionType: {
      type: String,
      required: true,
      index: true,
      trim: true,
      lowercase: true,
      default: 'view',
    },
    actionLabel: {
      type: String,
      trim: true,
      default: '',
    },
    pdfSha3: {
      type: String,
      index: true,
      trim: true,
      default: '',
    },
    fingerprint: {
      type: String,
      index: true,
      trim: true,
      default: '',
    },
    pdfUrl: {
      type: String,
      trim: true,
      default: '',
    },
    proofUrl: {
      type: String,
      trim: true,
      default: '',
    },
    sourceTag: {
      type: String,
      trim: true,
      default: '',
    },
    sourceCommit: {
      type: String,
      trim: true,
      default: '',
    },
    commandSurface: {
      type: String,
      index: true,
      trim: true,
      default: 'knowledge_base_vault_receipt',
    },
    route: {
      type: String,
      trim: true,
      default: '/api/knowledge-base/vault/receipts',
    },
    generatedAt: {
      type: Date,
      index: true,
      default: Date.now,
    },
    institutionalHeaders: {
      type: mongoose.Schema.Types.Mixed,
      default: {},
    },
    strikePayload: {
      type: mongoose.Schema.Types.Mixed,
      default: {},
    },
    metadata: {
      type: mongoose.Schema.Types.Mixed,
      default: {},
    },
  },
  {
    timestamps: true,
    minimize: false,
    collection: 'knowledge_base_vault_receipts',
  }
);

knowledgeBaseVaultReceiptSchema.index({ tenantId: 1, artifactId: 1, generatedAt: -1 });
knowledgeBaseVaultReceiptSchema.index({ tenantId: 1, actionType: 1, generatedAt: -1 });
knowledgeBaseVaultReceiptSchema.index({ tenantId: 1, operatorId: 1, generatedAt: -1 });

const KnowledgeBaseVaultReceipt =
  mongoose.models.KnowledgeBaseVaultReceipt ||
  mongoose.model('KnowledgeBaseVaultReceipt', knowledgeBaseVaultReceiptSchema);

export default KnowledgeBaseVaultReceipt;
