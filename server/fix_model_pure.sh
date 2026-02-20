#!/bin/bash
MODEL_PATH="/Users/wilsonkhanyezi/legal-doc-system/server/models/Case.js"

cat << 'INNER_EOF' > "$MODEL_PATH"
'use strict';
const mongoose = require('mongoose');

const CaseSchema = new mongoose.Schema({
    tenantId: { type: String, required: true, index: true },
    caseNumber: { type: String, required: true, unique: true },
    title: { type: String, required: true },
    status: { type: String, default: 'PRE_INTAKE' },
    client: { name: { type: String, required: true } },
    paiaRequests: [{
        requestId: { type: String },
        status: { type: String, default: 'PENDING' },
        statutoryDeadline: { type: Date }
    }],
    paiaTracking: { totalRequests: { type: Number, default: 0 }, pendingRequests: { type: Number, default: 0 } },
    legalTeam: [{ userId: { type: 'ObjectId', ref: 'User' }, role: String }],
    audit: { createdBy: { type: 'ObjectId', ref: 'User' }, createdAt: { type: Date, default: Date.now } }
}, { 
    timestamps: true,
    statics: {
        findByTenant: function(tenantId) {
            return this.find({ tenantId });
        },
        addPaiaRequest: async function(caseId, paiaData) {
            const caseDoc = await this.findById(caseId);
            if (!caseDoc) throw new Error('Case not found');
            const requestId = 'PAIA-' + Date.now();
            caseDoc.paiaRequests.push({ ...paiaData, requestId });
            caseDoc.paiaTracking.totalRequests += 1;
            await caseDoc.save();
            return { success: true, requestId };
        }
    }
});

// REMOVE CACHE CHECK: Force fresh model registration for forensic purity
delete mongoose.models.Case;
const Case = mongoose.model('Case', CaseSchema);

module.exports = Case;
INNER_EOF

echo "✅ Case.js Hardened with Pure Constructor Export."
