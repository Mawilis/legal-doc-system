const mongoose = require('mongoose');

const DispatchSchema = new mongoose.Schema({
  type: { type: String, default: 'Sheriff Service Instruction' },
  title: { type: String, required: true },
  documentCode: { type: String, required: true },
  caseNumber: { type: String, required: true },
  classification: { type: String, required: true },
  status: { type: String, default: 'Pending Dispatch', enum: ['Pending Dispatch', 'Dispatched', 'Served', 'Return Filed'] },
  
  // Logistics
  sheriff: {
    office: { type: String, required: true },
    serviceType: { type: String, required: true },
    urgency: { type: String, enum: ['normal', 'urgent'], default: 'normal' },
    distanceKm: Number,
    riskFlags: [String],
    accessNotes: String
  },

  // Locations & Parties
  serviceAddress: {
    street: String,
    city: String,
    province: String,
    code: String
  },
  parties: {
    plaintiff: String,
    defendant: String
  },

  // Financials
  financials: {
    tariff: Number,
    travel: Number,
    vat: Number,
    total: Number
  },

  // Evidence Link
  attachments: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Upload' }],

  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Dispatch', DispatchSchema);
