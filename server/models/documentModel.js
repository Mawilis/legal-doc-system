'use strict';
const mongoose = require('mongoose');

const documentSchema = new mongoose.Schema({
  title: { type: String, required: true },       
  documentCode: { type: String, required: true }, 
  type: { type: String, required: true },        
  classification: { type: String, default: 'General' },
  
  status: { 
    type: String, 
    enum: ['Draft', 'Pending', 'Filed', 'Completed'], 
    default: 'Draft' 
  },
  
  // Flexible Metadata (Stores the billion-dollar details)
  metadata: {
    court: String,
    plaintiff: { name: String, id: String },
    defendant: { name: String, id: String },
    marriage: { type: String, type: String }, // Regime, Date
    children: Number,
    urgency: String
  },

  createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
}, { timestamps: true });

module.exports = mongoose.model('Document', documentSchema);
