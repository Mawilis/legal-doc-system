/**
 * File: ecosystem.config.js
 * STATUS: EPITOME | PM2 Production Fleet (10-Process Topology) | PRODUCTION-READY
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Orchestrates the Wilsy OS process topology under PM2.
 * - Core responsibilities: gateway, scheduler, general workers, bundle worker.
 * - Microservices: AI, Auth, Ledger, Crypto, Billing, Standards.
 *
 * COLLABORATION COMMENTS:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @platform, @sre, @security, @observability, @product
 * - OPERATIONS:
 *   * Use this file with PM2 v5+ in production. Prefer `pm2 start ecosystem.config.js --env production`.
 *   * Tune `instances` per service based on CPU, memory, and service characteristics.
 *   * Use process manager (k8s, systemd) for cluster orchestration at scale; PM2 is ideal for single-node fleets.
 * - SECURITY:
 *   * Secrets must come from environment or a secrets manager; do not hardcode secrets here.
 *   * Run services under least-privilege accounts and isolate network access between tiers.
 * - OBSERVABILITY:
 *   * Logs are merged and rotated by PM2; integrate with a log shipper (Fluentd/Vector) to centralize logs.
 * - TESTING:
 *   * Validate startup in a staging environment with identical env variables and a mocked external stack.
 * -----------------------------------------------------------------------------
 */

module.exports = {
    apps: [
        // --- 1. THE CORE (Gateway / API) ---
        {
            name: 'wilsy-gateway',
            script: './server/index.js',
            instances: 1,
            exec_mode: 'fork',
            autorestart: true,
            watch: false,
            max_memory_restart: '1G',
            restart_delay: 2000,
            merge_logs: true,
            env: {
                NODE_ENV: 'production',
                PORT: 3001,
                AI_SERVICE_URL: 'http://127.0.0.1:6500',
                CRYPTO_SERVICE_URL: 'http://127.0.0.1:6600',
                BILLING_SERVICE_URL: 'http://127.0.0.1:6400',
                STANDARDS_SERVICE_URL: 'http://127.0.0.1:6100'
            },
            env_production: {
                NODE_ENV: 'production'
            }
        },

        // --- Scheduler (single instance) ---
        {
            name: 'wilsy-scheduler',
            script: './server/jobs/scheduler.js',
            instances: 1,
            exec_mode: 'fork',
            autorestart: true,
            watch: false,
            env: {
                NODE_ENV: 'production',
                ENABLE_SCHEDULER: 'true'
            }
        },

        // --- General worker pool (short-running tasks) ---
        {
            name: 'wilsy-worker-general',
            script: './server/jobs/workerEntry.js',
            instances: 1,
            exec_mode: 'fork',
            autorestart: true,
            watch: false,
            env: {
                NODE_ENV: 'production'
            }
        },

        // --- Bundles worker (memory heavy; tuned) ---
        {
            name: 'wilsy-worker-bundles',
            script: './server/worker-bootstrap/fileWorkers.js', // bootstrap that registers bundle worker
            instances: 1,
            exec_mode: 'fork',
            autorestart: true,
            watch: false,
            max_memory_restart: '6G',
            node_args: '--max-old-space-size=4096',
            env: {
                NODE_ENV: 'production'
            }
        },

        // --- 2. THE INTELLIGENCE (Microservices) ---

        // AI Engine (Risk & Document Analysis)
        {
            name: 'wilsy-service-ai',
            script: './services/ai/index.js',
            instances: 1,
            exec_mode: 'fork',
            autorestart: true,
            watch: false,
            env: {
                PORT: 6500,
                NODE_ENV: 'production',
                MONGO_URI: process.env.MONGO_URI || process.env.MONGODB_URI,
    //     path: '/var/www/wilsy',
    //     'post-deploy': 'npm ci && pm2 reload ecosystem.config.js --env production'
    //   }
    // }
};
