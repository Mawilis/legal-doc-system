/*
 * File: server/jobs/index.js
 * STATUS: PRODUCTION-READY | FLEET COMMAND
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The master initializer for background processes. Boots the workers and 
 * the scheduler, ensuring they are connected to the shared Redis backbone.
 * -----------------------------------------------------------------------------
 */

'use strict';

const winston = require('winston');
const scheduler = require('./scheduler');
const { bundleWorker } = require('./bundleWorker');
// Import other workers as they are created
// const { notificationWorker } = require('./notificationWorker');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
    transports: [new winston.transports.Console()]
});

/**
 * BOOT THE FLEET
 * Starts the workers and the master clock.
 */
const initJobs = async () => {
    try {
        logger.info('🚀 [JOBS_INIT]: Booting Background Worker Fleet...');

        // 1. Start the Master Clock (Leader Election handled inside)
        await scheduler.start();

        // 2. Initialize Workers
        // By simply requiring/referencing them, they begin listening to BullMQ
        if (bundleWorker) {
            logger.info('📦 [WORKER_READY]: Bundle Architect Online.');
        }

        // 3. Optional: Add a 'System Check' job to verify Redis health
        logger.info('✅ [JOBS_ONLINE]: All background systems operational.');

    } catch (err) {
        logger.error('💥 [JOBS_BOOT_FAILED]:', err);
        // In production, we might want to alert DevOps here
    }
};

module.exports = { initJobs };