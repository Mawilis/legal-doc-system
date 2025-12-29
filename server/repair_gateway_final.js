const fs = require('fs');
const path = require('path');

console.log('🔧 REPAIRING GATEWAY (server.js)...');

const serverCode = `/**
 * Copyright (c) 2025 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * All Rights Reserved.
 */
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
app.use(cors());

// --- PROXY HANDLER (Fixes Body Stream Issues) ---
const onProxyReq = (proxyReq, req, res) => {
    if (req.body && Object.keys(req.body).length > 0) {
        const bodyData = JSON.stringify(req.body);
        proxyReq.setHeader('Content-Type', 'application/json');
        proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
        proxyReq.write(bodyData);
    }
};

const proxyConfig = {
    changeOrigin: true,
    onProxyReq: onProxyReq,
    onError: (err, req, res) => {
        console.error('❌ Proxy Error:', err.message);
        res.status(500).json({ error: 'Service Unavailable', details: err.message });
    }
};

// --- ROUTES ---
// Map /api/billing to the Billing Service on Port 6400
app.use('/api/billing', express.json(), createProxyMiddleware({ 
    target: 'http://127.0.0.1:6400', 
    pathRewrite: { '^/api/billing': '' },
    ...proxyConfig 
}));

app.get('/health', (req, res) => res.send('Gateway Online'));

// --- START ---
mongoose.connect('mongodb://127.0.0.1:27017/legal-tech')
  .then(() => {
      app.listen(3001, '0.0.0.0', () => {
          console.log('🚀 [Gateway] Running on Port 3001');
          console.log('🔗 [Proxy] /api/billing -> 127.0.0.1:6400');
      });
  })
  .catch(err => console.log('❌ DB Error:', err.message));
`;

fs.writeFileSync(path.join(__dirname, 'server.js'), serverCode);
console.log('✅ GATEWAY REPAIRED.');
