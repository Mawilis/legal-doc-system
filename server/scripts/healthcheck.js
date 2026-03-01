#!/usr/bin/env node/usr/bin/env node
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ HEALTH CHECK UTILITY - For k8s probes                                     ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import http from 'http';

const options = {
  hostname: 'localhost',
  port: process.env.PORT || 4000,
  path: '/api/predict/health',
  method: 'GET',
  timeout: 5000,
};

const req = http.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 200) {
      try {
        const health = JSON.parse(data);
        if (health.status === 'healthy') {
          console.log('✅ Health check passed');
          process.exit(0);
        } else {
          console.error('❌ Service unhealthy:', health);
          process.exit(1);
        }
      } catch (e) {
        console.error('❌ Invalid health response:', data);
        process.exit(1);
      }
    } else {
      console.error(`❌ Health check failed with status ${res.statusCode}`);
      process.exit(1);
    }
  });
});

req.on('error', (err) => {
  console.error('❌ Health check error:', err.message);
  process.exit(1);
});

req.on('timeout', () => {
  req.destroy();
  console.error('❌ Health check timeout');
  process.exit(1);
});

req.end();
