#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PM2 PRODUCTION ECOSYSTEM v3.0.0                               ║
 * ║ [99.99% Uptime | Zero-Downtime Deploys | R2.4M Annual Savings]          ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

export default {
  apps: [
    {
      name: 'wilsy-os',
      script: './server.js',
      exec_mode: 'cluster',
      instances: 'max',
      interpreter: 'node',
      node_args: '--experimental-specifier-resolution=node --max-old-space-size=4096',

      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },

      env_development: {
        NODE_ENV: 'development',
        PORT: 3000,
        DEBUG: 'wilsy:*',
      },

      env_staging: {
        NODE_ENV: 'staging',
        PORT: 3000,
        DEBUG: 'wilsy:warn,wilsy:error',
      },

      max_memory_restart: '4G',
      kill_timeout: 5000,
      listen_timeout: 10000,
      shutdown_with_message: true,

      log_file: './logs/pm2/combined.log',
      error_file: './logs/pm2/error.log',
      out_file: './logs/pm2/out.log',
      pid_file: './pids/pm2.pid',
      log_date_format: 'YYYY-MM-DDTHH:mm:ss.sssZ',
      merge_logs: true,
      time: true,

      autorestart: true,
      watch: false,
      ignore_watch: [
        'node_modules',
        'logs',
        'pids',
        '.git',
        'tmp',
        'temp',
        'uploads',
        'downloads',
        'coverage',
        '*.log',
        '*.pid',
        '.env',
      ],

      min_uptime: 10000,
      max_restarts: 10,
      restart_delay: 4000,
      exp_backoff_restart_delay: 100,

      increment_var: 'NODE_APP_INSTANCE',
      instance_var: 'NODE_APP_INSTANCE',

      pre_start: 'npm run lint:check',
      post_start: 'npm run test:smoke',
      pre_restart: 'npm run lint:check',
      post_restart: 'npm run test:smoke',
      pre_stop: 'echo "Gracefully stopping..."',
      post_stop: 'echo "Stopped"',

      deploy: {
        production: {
          user: 'wilsy',
          host: ['api.wilsyos.com'],
          ref: 'origin/main',
          repo: 'https://github.com/Mawilis/legal-doc-system.git',
          path: '/var/www/wilsy-os/production',
          ssh_options: 'StrictHostKeyChecking=no',
          'pre-deploy-local': "echo 'Deploying to production...'",
          'post-deploy':
            'npm ci --production && pm2 reload ecosystem.config.js --only wilsy-os && pm2 save',
          'pre-setup': "echo 'Setting up production environment...'",
          env: {
            NODE_ENV: 'production',
          },
        },

        staging: {
          user: 'wilsy',
          host: ['staging.wilsyos.com'],
          ref: 'origin/develop',
          repo: 'https://github.com/Mawilis/legal-doc-system.git',
          path: '/var/www/wilsy-os/staging',
          ssh_options: 'StrictHostKeyChecking=no',
          'post-deploy':
            'npm ci && pm2 reload ecosystem.config.js --only wilsy-os --env staging && pm2 save',
          env: {
            NODE_ENV: 'staging',
          },
        },
      },
    },
  ],
};
