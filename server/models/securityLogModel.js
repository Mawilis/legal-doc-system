// RETIRED — Python EOS owns security logs. Node securityLogModel retired 2026-10-26
const mongoose = require('mongoose');
const schema = new mongoose.Schema({ retired: { type: Boolean, default: true } }, { strict: false });
module.exports = mongoose.models.SecurityLog || mongoose.model('SecurityLog', schema);
module.exports.BLOCKCHAIN_NETWORKS = { NONE: 'NONE', RETIRED: 'RETIRED' };
module.exports.retired = true;
