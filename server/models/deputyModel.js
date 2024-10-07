const mongoose = require('mongoose');

const deputySchema = new mongoose.Schema({
    name: { type: String, required: true },
    role: { type: String, required: true },
    assignedClients: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Client' }],
    createdAt: { type: Date, default: Date.now },
});

module.exports = mongoose.model('Deputy', deputySchema);
