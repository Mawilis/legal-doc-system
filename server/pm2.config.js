#!/* eslint-disable */
/*
 * WILSY OS: PM2 PRODUCTION CONFIGURATION
 * Self-healing cluster configuration with auto-restart
 */

export default {
  apps: [
    {
      name: 'wilsy-server',
      script: './server.js',
      instances: 'max',
      exec_mode: 'cluster',
      watch: false,
      max_memory_restart: '4G',

      // Auto-restart configuration
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: 10000,
      listen_timeout: 30000,
      kill_timeout: 5000,
      shutdown_with_message: true,

      // Health monitoring
      health_check: {
        url: 'http://localhost:3000/api/v1/health',
        interval: 30000,
        timeout: 5000,
        healthy_threshold: 2,
        unhealthy_threshold: 3,
      },

      // Logging
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: './logs/pm2/error.log',
      out_file: './logs/pm2/out.log',
      log_file: './logs/pm2/combined.log',
      merge_logs: true,

      // Environment
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
      },

      // Metrics
      metrics: {
        http: true,
        event_loop: true,
        network: true,
        transaction: true,
      },

      // Error handling
      error: {
        enabled: true,
        path: './logs/pm2/errors.log',
        max_size: '100M',
        retain: 10,
      },
    },
    {
      name: 'recovery-sentinel',
      script: './scripts/recovery-sentinel.js',
      args: 'start 30000',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      autorestart: true,
      restart_delay: 10000,
      max_restarts: 5,

      // Logging
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: './logs/pm2/recovery-error.log',
      out_file: './logs/pm2/recovery-out.log',

      // Environment
      env: {
        NODE_ENV: 'production',
      },
    },
  ],

  // Deployment configuration
  deploy: {
    production: {
      user: 'wilsy',
      host: ['api.wilsy.os'],
      ref: 'origin/main',
      repo: 'https://github.com/Mawilis/legal-doc-system.git',
      path: '/var/www/wilsy',
      'post-deploy': 'npm install && pm2 reload pm2.config.js --env production',
    },
  },
};
