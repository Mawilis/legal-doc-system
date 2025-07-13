const mongoose = require('mongoose');

const alertLogSchema = new mongoose.Schema({
    subject: String,
    message: String,
    email: String,
    sentToSlack: Boolean,
    timestamp: { type: Date, default: Date.now },
    ip: String,
});

module.exports = mongoose.model('AlertLog', alertLogSchema);
