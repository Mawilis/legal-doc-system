const mongoose = require('mongoose');

const EvidenceSchema = new mongoose.Schema({
  type: { type: String, enum: ['photo', 'signature', 'note'], required: true },
  url: { type: String },
  text: { type: String },
  capturedAt: { type: Date, default: Date.now },
});

const AttemptSchema = new mongoose.Schema({
    instructionId: { type: mongoose.Schema.Types.ObjectId, ref: 'DispatchInstruction', required: true },
    at: { type: Date, required: true },
    gps: {
      lat: { type: Number, required: true },
      lng: { type: Number, required: true },
      accuracy: { type: Number },
    },
    window: { type: String },
    outcome: {
      type: String,
      enum: ['served', 'refused', 'no_answer', 'wrong_address', 'postponed', 'partial', 'other'],
      required: true,
    },
    notes: { type: String },
    evidence: [EvidenceSchema],
    hash: { type: String, required: true }, // SHA-256 Integrity Hash
}, { timestamps: true });

module.exports = mongoose.model('Attempt', AttemptSchema);
