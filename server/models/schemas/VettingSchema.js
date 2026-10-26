// RETIRED — Python EOS owns vetting. Node VettingSchema retired 2026-10-26
const mongoose = require('mongoose');
const VettingSchema = new mongoose.Schema({ retired: { type: Boolean, default: true } }, { strict: false });
VettingSchema.methods.anchorToBlockchain = async function() { return { retired: true, reason: 'Node retired, EOS owns anchoring' }; };
module.exports = VettingSchema;
module.exports.BLOCKCHAIN_NETWORKS = { NONE: 'NONE', RETIRED: 'RETIRED', QUANTUM_LEDGER: 'RETIRED' };
module.exports.retired = true;
