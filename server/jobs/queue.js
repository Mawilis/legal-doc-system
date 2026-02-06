/*
 * File: server/jobs/queue.js
 * STATUS: PRODUCTION-READY | INDUSTRIAL EVENT BUS
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The platform's asynchronous backbone. Manages the hand-off between the 
 * API and background workers using Redis-backed BullMQ. Ensures "At-Least-Once" 
 * delivery for critical legal and financial events.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { Queue } = require('bullmq');

/**
 * REDIS ENGINE CONFIGURATION
 * Optimized for high-throughput and resilient connection handling.
 */
const connection = {
    host: process.env.REDIS_HOST || '127.0.0.1',
    port: parseInt(process.env.REDIS_PORT) || 6379,
    password: process.env.REDIS_PASSWORD || undefined,
    // Critical: BullMQ requires null here to prevent blocking connection issues
    maxRetriesPerRequest: null,
};

/**
 * GLOBAL JOB POLICY (The Resilience Guard)
 * Defines the lifecycle of every background task.
 */
const defaultJobOptions = {
    attempts: 5, // Increased for legal reliability
    backoff: {
        type: 'exponential', // 1s, 2s, 4s, 8s...
        delay: 2000,
    },
    // Prevent Redis memory bloat while keeping a forensic trail
    removeOnComplete: {
        age: 3600 * 24, // Keep history for 24 hours
        count: 1000,    // Limit to last 1000 successes
    },
    removeOnFail: {
        age: 3600 * 24 * 7, // Keep failures for 7 days for debugging
    },
    // Priority: 1 is highest, 2097152 is lowest
    priority: 10,
};

/**
 * QUEUE FACTORY
 * Standardizes the creation of isolated work streams.
 */
const createQueue = (name) => {
    const queue = new Queue(name, {
        connection,
        defaultJobOptions,
    });

    // CRITICAL: Silent errors in queues lead to data loss
    queue.on('error', (err) => {
        console.error(`🔥 [QUEUE_FAULT:${name.toUpperCase()}]:`, err.message);
    });

    return queue;
};

// -----------------------------------------------------------------------------
// INDUSTRIAL QUEUE REGISTRY
// -----------------------------------------------------------------------------

/**
 * 1. NOTIFICATION CLOUD (Emails, SMS, Push Alerts)
 * High velocity: Real-time alerts for service of process and deadlines.
 */
const notificationQueue = createQueue('NOTIF_SVC');

/**
 * 2. FINANCIAL SYNC (Invoicing & Ledger Integration)
 * High integrity: Syncing with Sage, Xero, or internal trust ledgers.
 */
const invoiceQueue = createQueue('FIN_SYNC');

/**
 * 3. DOCUMENT ARCHITECT (PDF Bundle Generation & OCR)
 * CPU Intensive: Heavy PDF merging and AI text extraction.
 */
const bundleQueue = createQueue('DOC_ARCHITECT');

/**
 * 4. LOGISTICS TRACKER (Sheriff GPS & Geofencing)
 * High volume: Ingesting location pings and verifying service proximity.
 */
const sheriffQueue = createQueue('LOG_TRACKER');

module.exports = {
    notificationQueue,
    invoiceQueue,
    bundleQueue,
    sheriffQueue,
    connection // Exported for Worker ingestion
};