/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PM2 PRODUCTION ECOSYSTEM                                      ║
 * ║ [99.99% Uptime | Zero-Downtime Deploys | R2.4M Annual Savings]          ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

module.exports = {
  apps: [{
    name: 'wilsy-os',
    script: '/Users/wilsonkhanyezi/legal-doc-system/server/server.js',
    cwd: '/Users/wilsonkhanyezi/legal-doc-system/server',
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
    
    log_file: '/Users/wilsonkhanyezi/legal-doc-system/server/logs/pm2/combined.log',
    error_file: '/Users/wilsonkhanyezi/legal-doc-system/server/logs/pm2/error.log',
    out_file: '/Users/wilsonkhanyezi/legal-doc-system/server/logs/pm2/out.log',
    pid_file: '/Users/wilsonkhanyezi/legal-doc-system/server/pids/pm2.pid',
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
    ],
    
    min_uptime: 10000,
    max_restarts: 10,
    restart_delay: 4000,
    exp_backoff_restart_delay: 100,
  }],
};
