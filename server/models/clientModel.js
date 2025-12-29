'use strict';
const mongoose = require('mongoose');

const ClientSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  email: { type: String, trim: true, lowercase: true },
  phone: { type: String },
  address: { type: String },
  type: { type: String, enum: ['Individual', 'Corporate'], default: 'Individual' },
  status: { type: String, default: 'Active', enum: ['Active', 'Inactive'] },
  createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
}, { timestamps: true });

module.exports = mongoose.model('Client', ClientSchema);
