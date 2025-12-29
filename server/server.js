'use strict';

require('dotenv').config();

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const { createProxyMiddleware } = require('http-proxy-middleware');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { randomUUID } = require('crypto');
const winston = require('winston');
const bodyParser = require('body-parser');

// ---- Configuration ----
const PORT = 3001;
const HOST = '127.0.0.1'; // Standard IPv4 for macOS stability
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';
const CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000'];

const logger = winston.createLogger({
    level: 'debug',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.printf(({ timestamp, level, message }) => `${timestamp} ${level.toUpperCase()}: ${message}`)
    ),
    transports: [new winston.transports.Console()],
});

const app = express();
const server = http.createServer(app);

// ---- Middleware Stack ----
app.use(helmet({ crossOriginResourcePolicy: { policy: "cross-origin" }, contentSecurityPolicy: false }));
app.use(compression());
app.use(cors({ origin: CORS_ORIGINS, credentials: true }));
app.use(bodyParser.json({ limit: '10mb' }));

app.use((req, res, next) => {
    req.requestId = req.headers['x-request-id'] || randomUUID();
    next();
});

app.use(morgan(':method :url :status :response-time ms'));

// ---- Database Connection ----
mongoose.connect(MONGO_URI)
    .then(() => logger.info('✅ [Wilsy Gateway] DB Connected'))
    .catch(err => logger.error(`❌ DB Connection Failed: ${err.message}`));

// ---- Proxy Logic ----
const proxyCfg = {
    changeOrigin: true,
    onProxyReq: (proxyReq, req) => {
        if (req.body && Object.keys(req.body).length > 0) {
            const bodyData = JSON.stringify(req.body);
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
            proxyReq.write(bodyData);
        }
    }
};

// ---- Service Bridges ----
app.use('/api/auth', createProxyMiddleware({ target: 'http://127.0.0.1:4000', pathRewrite: { '^/api/auth': '' }, ...proxyCfg }));
app.use('/api/billing', createProxyMiddleware({ target: 'http://127.0.0.1:6400', pathRewrite: { '^/api/billing': '' }, ...proxyCfg }));
app.use('/api/ai', createProxyMiddleware({ target: 'http://127.0.0.1:6500', pathRewrite: { '^/api/ai': '' }, ...proxyCfg }));

// ---- Local Routes (The Fix) ----
// We mount them exactly where the frontend expects them
try {
    app.use('/api/documents', require('./routes/documentRoutes'));
    app.use('/api/dashboard', require('./routes/dashboardRoutes'));
    logger.info('🚀 [Wilsy Gateway] Local Sheriff Ops Routes Mounted');
} catch (e) {
    logger.error(`❌ Failed to load local routes: ${e.message}`);
}

// ---- Server Boot ----
server.listen(PORT, HOST, () => {
    logger.info(`🚀 [Wilsy Gateway] Epitome Routing Online at http://${HOST}:${PORT}`);
});