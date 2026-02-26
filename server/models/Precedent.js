/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PRECEDENT MODEL                                                ║
 * ║ [Legal Precedent Database | Case Law | Forensic Citations]                ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

const precedentSchema = new mongoose.Schema({
  tenantId: {
    type: String,
    required: true,
    index: true
  },
  caseName: {
    type: String,
    required: true,
    index: true
  },
  citation: {
    type: String,
    required: true,
    unique: true
  },
  court: {
    type: String,
    required: true,
    enum: [
      'CONSTITUTIONAL_COURT',
      'SUPREME_COURT_APPEAL',
      'HIGH_COURT',
      'LABOUR_COURT',
      'LABOUR_APPEAL_COURT',
      'LAND_CLAIMS_COURT',
      'MAGISTRATE_COURT'
    ]
  },
  judgmentDate: Date,
  summary: String,
  keyPrinciples: [String],
  overruledBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Precedent'
  },
  overruledDate: Date,
  tags: [String],
  citations: [{
    citedIn: String,
    court: String,
    date: Date
  }],
  metadata: {
    createdBy: String,
    verifiedBy: String,
    verifiedAt: Date,
    source: String
  }
}, {
  timestamps: true
});

// Indexes
precedentSchema.index({ caseName: 'text', summary: 'text' });
precedentSchema.index({ court: 1, judgmentDate: -1 });
precedentSchema.index({ tags: 1 });

const Precedent = mongoose.model('Precedent', precedentSchema);

export default Precedent;
