/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN INCIDENT MODEL - FORTUNE 500 EDITION                ║
 * ║ [FORENSIC INCIDENT MANAGEMENT | BREACH TRACKING | COMPLIANCE]            ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'crypto';

const incidentSchema = new mongoose.Schema({
  incidentId: {
    type: String,
    default: () => crypto.randomUUID(),
    unique: true,
    required: true,
  },

  title: {
    type: String,
    required: true,
    trim: true,
  },

  description: {
    type: String,
    required: true,
  },

  severity: {
    type: String,
    enum: ['critical', 'high', 'medium', 'low'],
    required: true,
  },

  status: {
    type: String,
    enum: ['open', 'investigating', 'mitigated', 'resolved', 'closed'],
    default: 'open',
  },

  alerts: [{
    type: String,
    ref: 'Alert',
  }],

  timeline: [{
    action: String,
    timestamp: { type: Date, default: Date.now },
    userId: String,
    notes: String,
  }],

  forensicHash: {
    type: String,
    required: true,
  },

}, {
  timestamps: true,
});

incidentSchema.pre('save', async function(next) {
  if (this.isNew) {
    const hashData = {
      incidentId: this.incidentId,
      title: this.title,
      timestamp: new Date().toISOString(),
    };
    this.forensicHash = crypto
      .createHash('sha256')
      .update(JSON.stringify(hashData))
      .digest('hex');
  }
  next();
});

const Incident = mongoose.model('Incident', incidentSchema);
export default Incident;
