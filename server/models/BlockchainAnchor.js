// RETIRED — Python EOS owns anchoring. Node BlockchainAnchor retired 2026-10-26
// Stub — no BLOCKCHAIN_NETWORKS, no web3, keeps import from crashing
const mongoose = require('mongoose');
const schema = new mongoose.Schema({ retired: { type: Boolean, default: true }, reason: String }, { strict: false });
module.exports = mongoose.models.BlockchainAnchor || mongoose.model('BlockchainAnchor', schema);
module.exports.BLOCKCHAIN_NETWORKS = { NONE: 'NONE', RETIRED: 'RETIRED' };
module.exports.retired = true;
