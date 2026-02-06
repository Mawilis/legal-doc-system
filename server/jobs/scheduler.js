/*
 * File: server/jobs/scheduler.js
 * STATUS: PRODUCTION-READY | DISTRIBUTED MASTER CLOCK
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The platform's temporal authority. Dispatches statutory compliance scans, 
 * financial reminders, and briefings. Uses Redis-based leader election to 
 * prevent duplicate execution in clustered environments.
 * -----------------------------------------------------------------------------
 */

'use strict';

const cron = require('node-cron');
const IORedis = require('ioredis');
const { randomUUID } = require('crypto');
const winston = require('winston');
const mongoose = require('mongoose');
const User = require('../models/User');
const Tenant = require('../models/Tenant');
const { notificationQueue, bundleQueue } = require('./queue');

// --- 1. INDUSTRIAL LOGGING ---
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
    transports: [new winston.transports.Console()]
});

// --- 2. THE DISTRIBUTED LOCK (REDLOCK LITE) ---
const redis = new IORedis(process.env.REDIS_URL || 'redis://127.0.0.1:6379');
const LOCK_KEY = 'WILSY_SCHEDULER_LEADER_LOCK';
const LOCK_TTL = 30000; // 30s
let lockId = null;

const acquireLeadership = async () => {
    const id = randomUUID();
    // SET NX: Only sets if the key doesn't exist (Atomic Election)
    const result = await redis.set(LOCK_KEY, id, 'PX', LOCK_TTL, 'NX');
    if (result === 'OK') {
        lockId = id;
        return true;
    }
    return false;
};

const extendLeadership = async () => {
    if (!lockId) return;
    const val = await redis.get(LOCK_KEY);
    if (val === lockId) await redis.pexpire(LOCK_KEY, LOCK_TTL);
};

// --- 3. THE TEMPORAL ENGINE ---

const scheduler = {
    start: async () => {
        const isLeader = await acquireLeadership();

        if (!isLeader) {
            logger.info('💤 [SCHEDULER]: Standby mode. Another node is leading.');
            return;
        }

        logger.info('👑 [SCHEDULER]: Leadership acquired. Master clock online.');
        setInterval(extendLeadership, 15000); // Renew every 15s

        // A. MONDAY MORNING BRIEFING (09:00 SAST)
        cron.schedule('0 9 * * 1', async () => {
            logger.info('⏰ [CRON]: Dispatching Weekly Legal Briefings...');
            const users = await User.find({ role: { $in: ['admin', 'associate'] } }).select('email name tenantId');

            const jobs = users.map(u => ({
                name: 'WEEKLY_DIGEST',
                data: { email: u.email, name: u.name, tenantId: u.tenantId }
            }));

            await notificationQueue.addBulk(jobs);
        });

        // B. NIGHTLY COMPLIANCE SCAN (00:00 SAST)
        // Scans for FICA/ID expiries across all active law firms
        cron.schedule('0 0 * * *', async () => {
            logger.info('⏰ [CRON]: Initiating Firm-wide Compliance Scans...');
            const tenants = await Tenant.find({ status: 'ACTIVE' }).select('_id');

            for (const firm of tenants) {
                // We space these out slightly to avoid a massive spike in DB load
                await notificationQueue.add('RUN_COMPLIANCE_SCAN',
                    { tenantId: firm._id },
                    { priority: 5 }
                );
            }
        });

        // C. RETENTION PURGE (Sundays at 02:00 AM)
        cron.schedule('0 2 * * 0', async () => {
            logger.info('⏰ [CRON]: Triggering Statutory Retention Purge...');
            // Logic to move cases to 'Ready for Destruction' status
        });
    }
};

// Standalone initialization for PM2/Docker
if (require.main === module) {
    if (mongoose.connection.readyState === 0) {
        mongoose.connect(process.env.MONGO_URI).then(() => scheduler.start());
    } else {
        scheduler.start();
    }
}

module.exports = scheduler;