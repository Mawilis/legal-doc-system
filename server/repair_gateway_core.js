const fs = require('fs');
const path = require('path');

console.log('🔧 APPLYING GATEWAY STREAM FIX...');

const serverPath = path.join(__dirname, 'server.js');

// THE FIXED GATEWAY CODE
// Includes "onProxyReq" logic to fix the consumed body stream error
const newServerCode = `/**
 * Copyright (c) 2025 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * All Rights Reserved.
 * Proprietary and confidential.
 */

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const { createProxyMiddleware, fixRequestBody } = require('http-proxy-middleware');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

// --- MIDDLEWARE ---
app.use(cors());
app.use(express.json()); // This consumes the stream! We must fix it below.

// --- DB CONNECTION ---
mongoose.connect('mongodb://127.0.0.1:27017/legal-tech')
  .then(() => console.log('✅ [DB] MongoDB Connected'))
  .catch(err => console.error('❌ [DB] Connection Error:', err));

// --- WEBSOCKETS ---
io.on('connection', (socket) => {
    console.log('⚡ [Socket] Client Connected:', socket.id);
    socket.on('disconnect', () => console.log('❌ [Socket] Disconnected:', socket.id));
});
console.log('📡 [Socket] WebSocket Gateway Active');

// --- PROXY CONFIGURATION (The Fix) ---
// This function re-writes the body so the microservice can read it
const proxyOptions = {
    changeOrigin: true,
    onProxyReq: (proxyReq, req, res) => {
        if (req.body && Object.keys(req.body).length > 0) {
            const bodyData = JSON.stringify(req.body);
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
            proxyReq.write(bodyData);
        }
    }
};

// --- MICROSERVICE ROUTES ---

// 1. LEDGER (Port 6000)
app.use('/api/ledger', createProxyMiddleware({ target: 'http://127.0.0.1:6000', ...proxyOptions }));

// 2. STANDARDS (Port 6100)
app.use('/api/standards', createProxyMiddleware({ target: 'http://127.0.0.1:6100', ...proxyOptions }));

// 3. BILLING (Port 6400)
app.use('/api/billing', createProxyMiddleware({ target: 'http://127.0.0.1:6400', ...proxyOptions }));

// 4. AI ENGINE (Port 6500)
app.use('/api/ai', createProxyMiddleware({ target: 'http://127.0.0.1:6500', ...proxyOptions }));

// 5. CRYPTO VAULT (Port 6600)
app.use('/api/crypto', createProxyMiddleware({ target: 'http://127.0.0.1:6600', ...proxyOptions }));

// --- LEGACY ROUTES (Local Controller) ---
// Kept for backward compatibility with your Dispatch Instructions
const dispatchRoutes = require('./routes/dispatchRoutes'); // Ensure this file exists or comment out if unused
try {
    app.use('/api/dispatch-instructions', dispatchRoutes);
} catch (e) { console.log('ℹ️ Dispatch Routes not loaded (Microservice Mode)'); }

// --- STARTUP ---
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
    console.log(\`🚀 [Core] Server running on port \${PORT}\`);
    console.log(\`🔗 [Gateway] Wiring Microservices...\`);
});
`;

fs.writeFileSync(serverPath, newServerCode);
console.log('✅ GATEWAY REPAIRED: Stream logic fixed.');
