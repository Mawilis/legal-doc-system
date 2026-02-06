/*
 * File: server/seed/seedAudits.js
 * STATUS: EPITOME | FINAL RELATIONAL ALIGNMENT | SINGLE-QUOTE ENFORCED
 */

'use strict';

const mongoose = require('mongoose');
const AuditLog = require('../models/AuditLog');

/**
 * SEED AUDIT TRAIL
 * Satisfies event.action and event.type requirements with strict single quotes.
 */
const seedAudits = async (tenantId, userId) => {
    try {
        console.log('📝 [SEED_AUDITS]: Generating forensic history...');

        const auditEvents = [
            {
                tenantId: tenantId,
                userId: userId,
                userEmail: 'admin@wilsyos.com',
                // NESTED EVENT OBJECT (Required by AuditLog schema)
                event: {
                    action: 'SYSTEM_HYDRATION',
                    type: 'SYSTEM_EVENT',
                    category: 'DATABASE',
                    severity: 'INFO'
                },
                resource: 'System',
                resourceId: tenantId,
                summary: 'Master Seed Data applied successfully.',
                metadata: { source: 'seed-script' },
                createdAt: new Date()
            }
        ];

        // 1. Clear existing for this tenant
        await AuditLog.deleteMany({ tenantId: tenantId });

        // 2. Insert new logs
        await AuditLog.insertMany(auditEvents);

        // 3. Success log with single quotes
        console.log('✅ [SEED_AUDITS]: Audit ledger successfully hydrated.');

        return true;
    } catch (err) {
        console.error('❌ [SEED_AUDITS_ERROR]:', err.message);
        throw err;
    }
};

module.exports = seedAudits;