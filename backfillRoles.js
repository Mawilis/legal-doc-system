#!/usr/bin/env node
/**
 * File: scripts/backfillRoles.js
 * Path: scripts/backfillRoles.js
 * PURPOSE: Backfill missing user.role fields from IdP claims.
 * VERSION: 1.0.0
 *
 * COLLABORATION & OWNERSHIP
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @backend-team (run and validate)
 * - SECURITY OWNER: @security (approve backfill plan)
 * - SRE OWNER: @sre (DB backup, run in maintenance window)
 * - QA OWNER: @qa (validate dry-run output)
 *
 * SAFETY RULES
 * - Always run with --dry-run first
 * - Owners excluded by default; use --force to include
 * - Script writes audit entries for applied changes
 *
 * USAGE
 * - Dry run: node scripts/backfillRoles.js --dry-run --limit=100
 * - Apply:   node scripts/backfillRoles.js --apply --limit=200 --concurrency=5
 */

'use strict';

const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const os = require('os');
const pLimit = require('p-limit');
const argv = require('minimist')(process.argv.slice(2), {
    boolean: ['dry-run', 'apply', 'force'],
    default: { 'dry-run': true, limit: 100, concurrency: 3, force: false }
});

const DRY_RUN = argv['dry-run'];
const APPLY = argv['apply'];
const LIMIT = Number(argv.limit) || 100;
const CONCURRENCY = Number(argv.concurrency) || 3;
const FORCE = !!argv.force;

if (DRY_RUN && APPLY) {
    console.error('Cannot specify both --dry-run and --apply. Choose one.');
    process.exit(1);
}

const logger = (() => { try { return require('../server/utils/logger'); } catch (e) { return console; } })();
const idpService = require('../server/services/idpService');

async function main() {
    const mongoUri = process.env.MONGO_URI || process.env.DATABASE_URL || 'mongodb://localhost:27017/wilsy';
    await mongoose.connect(mongoUri, { useNewUrlParser: true, useUnifiedTopology: true });

    const User = require('../server/models/userModel');
    const AuditLog = (() => { try { return require('../server/models/auditModel'); } catch (e) { return null; } })();

    console.log(`Backfill Roles Script - ${new Date().toISOString()}`);
    console.log(`Mode: ${DRY_RUN ? 'DRY-RUN' : 'APPLY'} | Limit: ${LIMIT} | Concurrency: ${CONCURRENCY} | Force: ${FORCE}`);

    // Query users missing role
    const query = { $or: [{ role: { $exists: false } }, { role: null }, { role: '' }] };
    if (!FORCE) query.isOwner = { $ne: true };

    const cursor = User.find(query).lean().limit(LIMIT).cursor();
    const limit = pLimit(CONCURRENCY);
    const results = [];
    let processed = 0;

    for await (const user of cursor) {
        processed++;
        const task = limit(async () => {
            const userId = String(user._id);
            try {
                const res = await idpService.fetchClaimsForUser({ userId }, { correlationId: `backfill_${Date.now()}` });
                if (!res || !res.ok) {
                    results.push({ userId, email: user.email, status: 'no-claims', roleBefore: user.role || null, roleAfter: null });
                    return;
                }
                const normalizedRole = res.normalizedRole || null;
                results.push({ userId, email: user.email, status: normalizedRole ? 'found' : 'no-role-claim', roleBefore: user.role || null, roleAfter: normalizedRole });

                if (!DRY_RUN && normalizedRole) {
                    await User.updateOne({ _id: userId }, { $set: { role: normalizedRole, lastRoleSyncAt: new Date() } });
                    if (AuditLog && typeof AuditLog.create === 'function') {
                        try {
                            await AuditLog.create({
                                timestamp: new Date(),
                                action: 'ROLE_BACKFILL',
                                resource: 'USER',
                                severity: 'HIGH',
                                actor: { userId: 'system' },
                                metadata: { userId, email: user.email, role: normalizedRole, source: res.source || 'idp' }
                            });
                        } catch (e) {
                            logger.warn('Failed to write audit log for backfill', e && e.message);
                        }
                    }
                }
            } catch (err) {
                results.push({ userId, email: user.email, status: 'error', error: err.message });
            }
        });
        await task;
    }

    console.log(`Processed: ${processed} users. Results: ${results.length} entries.`);

    if (!DRY_RUN) {
        const outDir = path.join(process.cwd(), 'backfill-results');
        if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
        const filename = `backfill-${new Date().toISOString().replace(/[:.]/g, '-')}.csv`;
        const csvPath = path.join(outDir, filename);
        const header = ['userId', 'email', 'status', 'roleBefore', 'roleAfter', 'error'].join(',');
        const lines = results.map(r => [r.userId, r.email, r.status, r.roleBefore || '', r.roleAfter || '', r.error || ''].map(v => `"${String(v).replace(/"/g, '""')}"`).join(','));
        fs.writeFileSync(csvPath, [header, ...lines].join(os.EOL), 'utf8');
        console.log(`Wrote results to ${csvPath}`);
    } else {
        console.table(results.slice(0, 20));
    }

    await mongoose.disconnect();
    console.log('Done.');
}

main().catch(err => {
    console.error('Backfill failed', err && (err.stack || err));
    process.exit(1);
});
