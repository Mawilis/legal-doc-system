const mongoose = require('mongoose');

const UploadSchema = new mongoose.Schema({
  caseId: { type: mongoose.Schema.Types.ObjectId, required: true }, // Links to Dispatch or Document
  filename: String,
  originalName: String,
  mimetype: String,
  size: Number,
  path: String,
  uploadedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Upload', UploadSchema);
