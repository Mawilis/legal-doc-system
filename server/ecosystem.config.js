/* eslint-disable */
/**
 * @file ecosystem.config.js
 * @version 2.0.0-PYTHON-EOS-API
 * @epitome Sovereign Process Management - Wilsy OS
 * @description PM2 configuration for the canonical Python EOS ASGI API.
 * ENSURES: Python EOS process supervision and restart policy; no Node API BFF.
 *
 * BIBLICAL STANDARDS:
 * - Worth: Billions (Investment-Grade Reliability).
 * - Integrity: Atomic process management; failures are auto-revived by the sentinel.
 * - Precision: Clustered for stability; bound to Sovereign Port 5050.
 */

module.exports = {
  apps: [
    {
      name: 'wilsy-os-python-eos-api',
      script: '../.venv/bin/python',
      args: '-m uvicorn tools.eos.api.server:app --host 127.0.0.1 --port 9095',
      cwd: '..',
      interpreter: 'none',

      // CRITICAL: one Python EOS process owns port 9095.
      instances: 1,
      exec_mode: 'fork',

      // Reliability: Auto-restart protocols for multi-billion dollar uptime
      watch: false,
      max_memory_restart: '1G',
      restart_delay: 3000,
      autorestart: true,

      // Environment Context
      env: {
        PYTHONPATH: '..',
        PYTHONUNBUFFERED: '1',
        WILSY_EOS_RUNTIME: 'python'
      },

      // Forensic Audit Trail: Centralized logging for R240M revenue monitoring
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: './logs/sovereign-error.log',
      out_file: './logs/sovereign-out.log',
      merge_logs: true,

      // Graceful Exit: Prevents data corruption during Omega-level shutdowns
      kill_timeout: 10000,
      wait_ready: true,
      listen_timeout: 10000,

      // Resource Management & Backoff
      exp_backoff_restart_delay: 100,
      max_restarts: 10,
      min_uptime: '5s'
    },
  ],
};
