/*
 * File: server/seed/seedDocuments.js
 * STATUS: PRODUCTION-READY | FORENSIC ALIGNMENT
 */

'use strict';

const mongoose = require('mongoose');
const Document = require('../models/Document');

/**
 * SEED DOCUMENT REGISTRY
 * @param {ObjectId} tenantId - The firm context
 * @param {Array} clientIds - Relational links from seedClients
 */
const seedDocuments = async (tenantId, clientIds) => {
    try {
        console.log(`📂 [SEED_DOCUMENTS]: Generating legal workload for Tenant ${tenantId}...`);

        const demoDocs = [
            {
                tenantId,
                clientId: clientIds[0], // JPG
                caseId: new mongoose.Types.ObjectId(), // Simulated Case
                uploadedBy: new mongoose.Types.ObjectId('650c22222222222222222222'),

                // LEGAL CONTEXT (Aligned to your Enum)
                category: 'PLEADING',
                title: 'Summons: Debt Recovery',
                description: 'Initial summons for Johannesburg High Court filing.',

                // FILE METADATA
                filename: 'summons_001.pdf',
                mimeType: 'application/pdf',
                size: 154200, // bytes

                // STORAGE & SECURITY (Required by model)
                storageKey: `tenants/${tenantId}/cases/case_001/summons.pdf`,
                contentHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                isEncrypted: true,

                // LIFECYCLE (Aligned to your Enum)
                status: 'ACTIVE',
                visibility: 'TEAM',

                // AUDIT & PROVENANCE
                provenance: {
                    uploaderIp: '127.0.0.1',
                    uploaderAgent: 'Wilsy-Hydration-Script',
                    uploadedAt: new Date()
                },
                tags: ['summons', 'debt-recovery', 'high-court']
            },
            {
                tenantId,
                clientId: clientIds[1], // Sibongile Nkosi
                caseId: new mongoose.Types.ObjectId(),
                uploadedBy: new mongoose.Types.ObjectId('650c22222222222222222222'),

                category: 'COURT_NOTICE',
                title: 'Notice of Motion: Eviction',
                description: 'Section 4 notice for Pretoria Magistrates Court.',

                filename: 'notice_evict.pdf',
                mimeType: 'application/pdf',
                size: 98500,

                storageKey: `tenants/${tenantId}/cases/case_002/notice.pdf`,
                contentHash: 'f4f2c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b123',
                isEncrypted: true,

                status: 'ACTIVE',
                visibility: 'CLIENT_PORTAL',

                provenance: {
                    uploaderIp: '127.0.0.1',
                    uploaderAgent: 'Wilsy-Hydration-Script',
                    uploadedAt: new Date()
                },
                tags: ['eviction', 'section-4', 'pretoria']
            }
        ];

        // Clean previous seeded docs
        await Document.deleteMany({ tenantId });
        const savedDocs = await Document.insertMany(demoDocs);

        console.log(`✅ [SEED_DOCUMENTS]: Successfully injected ${savedDocs.length} forensic-grade documents.`);
        return savedDocs.map(d => d._id);
    } catch (err) {
        console.error('❌ [SEED_DOCUMENTS_ERROR]:', err.message);
        throw err;
    }
};

module.exports = seedDocuments;