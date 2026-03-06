/* eslint-disable */
// ============================================================================
// WILSY OS 2050 - BLOCKCHAIN TRANSACTION MODEL
// THE LEDGER MIRROR | QUANTUM FORTRESS
// VERSION: 42.0.2 | GENERATION: 10 | REVOLUTIONARY FIX
// ============================================================================

import mongoose from 'mongoose';

const { Schema } = mongoose;

const blockchainTransactionSchema = new Schema({
  transactionHash: {
    type: String,
    unique: true,
    sparse: true,
    trim: true
  },

  documentHash: {
    type: String,
    required: true,
    trim: true
  },

  documentType: {
    type: String,
    enum: ['LEGAL_DOCUMENT', 'CONTRACT', 'EVIDENCE', 'AUDIT_LOG', 'CASE_FILE', 'OTHER'],
    default: 'AUDIT_LOG'
  },

  documentId: {
    type: Schema.Types.ObjectId,
    refPath: 'documentModel'
  },

  documentModel: {
    type: String,
    enum: ['Document', 'AuditLog', 'Case', 'Evidence']
  },

  blockNumber: { type: Number },
  blockHash: { type: String },
  transactionIndex: { type: Number },

  status: {
    type: String,
    enum: ['PENDING', 'CONFIRMED', 'FAILED', 'REORG', 'EXPIRED', 'VERIFIED'],
    default: 'PENDING'
  },

  confirmations: { type: Number, default: 0 },
  requiredConfirmations: { type: Number, default: 12 },

  network: {
    type: String,
    enum: ['HYPERLEDGER_FABRIC', 'ETHEREUM_MAINNET', 'ETHEREUM_TESTNET', 'POLYGON_MAINNET', 'POLYGON_AMOY', 'QUANTUM_LEDGER', 'CUSTOM'],
    default: 'HYPERLEDGER_FABRIC'
  },

  submittedAt: { type: Date, default: Date.now },
  confirmedAt: { type: Date },
  blockTimestamp: { type: Date },
  latencyMs: { type: Number },

  gasUsed: { type: Number },
  gasPrice: { type: String },
  transactionFee: { type: String },
  feeCurrency: { type: String, default: 'ETH' },

  auditId: { type: Schema.Types.ObjectId, ref: 'AuditLog' },

  metadata: { type: Map, of: Schema.Types.Mixed, default: new Map() },
  tags: [{ type: String }],

  retentionUntil: {
    type: Date,
    required: true,
    default: () => new Date(Date.now() + 7 * 365 * 24 * 60 * 60 * 1000)
  },

  dataSovereignty: {
    jurisdiction: { type: String, default: 'ZA' }
  },

  lastVerifiedAt: { type: Date },
  verificationStatus: {
    type: String,
    enum: ['UNVERIFIED', 'VERIFIED', 'DISCREPANCY', 'REORG_DETECTED'],
    default: 'UNVERIFIED'
  },

  createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
  version: { type: Number, default: 1 }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// ============================================================================
// VIRTUALS - FIXED for test expectations
// ============================================================================

blockchainTransactionSchema.virtual('isConfirmed').get(function() {
  return this.status === 'CONFIRMED' && this.confirmations >= 1;
});

blockchainTransactionSchema.virtual('isLegalAdmissible').get(function() {
  return this.status === 'CONFIRMED' && this.confirmations >= 6;
});

blockchainTransactionSchema.virtual('explorerUrl').get(function() {
  if (!this.transactionHash) return null;
  const explorers = {
    'ETHEREUM_MAINNET': `https://etherscan.io/tx/${this.transactionHash}`,
    'ETHEREUM_TESTNET': `https://sepolia.etherscan.io/tx/${this.transactionHash}`,
    'POLYGON_MAINNET': `https://polygonscan.com/tx/${this.transactionHash}`,
    'POLYGON_AMOY': `https://amoy.polygonscan.com/tx/${this.transactionHash}`
  };
  return explorers[this.network] || null;
});

// ============================================================================
// MIDDLEWARE - FIXED: No 'next' parameter
// ============================================================================

blockchainTransactionSchema.pre('save', async function() {
  if (this.isModified('confirmedAt') && this.confirmedAt && this.submittedAt) {
    this.latencyMs = this.confirmedAt - this.submittedAt;
  }

  if (!this.isNew) {
    this.version = (this.version || 0) + 1;
  }

  if (this.status === 'CONFIRMED' && !this.transactionHash) {
    throw new Error('CONFIRMED transactions must have a transaction hash');
  }
});

// ============================================================================
// STATIC METHODS
// ============================================================================

blockchainTransactionSchema.statics.findByHash = function(hash, network = null) {
  const query = { transactionHash: hash };
  if (network) query.network = network;
  return this.findOne(query);
};

blockchainTransactionSchema.statics.findUnconfirmed = function(olderThan = 3600000) {
  const cutoffTime = new Date(Date.now() - olderThan);
  return this.find({
    status: 'PENDING',
    submittedAt: { $lt: cutoffTime }
  }).sort({ submittedAt: 1 });
};

blockchainTransactionSchema.statics.findByDocument = function(documentId, documentModel) {
  return this.find({ documentId, documentModel }).sort({ createdAt: -1 });
};

blockchainTransactionSchema.statics.getNetworkStats = async function(network, days = 30) {
  const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  const stats = await this.aggregate([
    { $match: { network, createdAt: { $gte: cutoffDate } } },
    {
      $group: {
        _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
        count: { $sum: 1 },
        confirmed: { $sum: { $cond: [{ $eq: ['$status', 'CONFIRMED'] }, 1, 0] } },
        failed: { $sum: { $cond: [{ $eq: ['$status', 'FAILED'] }, 1, 0] } },
        avgLatency: { $avg: '$latencyMs' }
      }
    },
    { $sort: { '_id': 1 } }
  ]);
  return stats;
};

const BlockchainTransaction = mongoose.model('BlockchainTransaction', blockchainTransactionSchema);
export default BlockchainTransaction;
