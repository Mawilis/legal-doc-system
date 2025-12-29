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
const promClient = require('prom-client');
const bodyParser = require('body-parser');
const path = require('path');

const PORT = Number(process.env.PORT || 3001);
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';
const NODE_ENV = process.env.NODE_ENV || 'development';
const CORS_ORIGINS = process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['*'];
const PROXY_TIMEOUT = Number(process.env.PROXY_TIMEOUT_MS || 30000);

const logger = winston.createLogger({
    level: NODE_ENV === 'production' ? 'info' : 'debug',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.printf(({ timestamp, level, message, ...meta }) => {
            const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
            return `${timestamp} ${level.toUpperCase()} ${message} ${metaStr}`;
        })
    ),
    transports: [new winston.transports.Console()],
});

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: { origin: CORS_ORIGINS, methods: ['GET', 'POST'] },
});

// Observability
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

app.get('/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
});

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors({ origin: CORS_ORIGINS, credentials: true }));
app.use(bodyParser.json({ limit: '5mb' }));

app.use((req, res, next) => {
    req.requestId = req.headers['x-request-id'] || randomUUID();
    res.setHeader('x-request-id', req.requestId);
    next();
});

app.use(morgan(':method :url :status :res[content-length] - :response-time ms'));

// DB Connection with 127.0.0.1 Fallback (Crucial for Mac/Unix)
async function connectMongo(retries = 0) {
    try {
        const uri = MONGO_URI.replace('localhost', '127.0.0.1');
        await mongoose.connect(uri);
        logger.info('✅ [Wilsy Gateway] Database Connected');
    } catch (err) {
        logger.error('❌ DB Error', { message: err.message });
        if (retries < 5) setTimeout(() => connectMongo(retries + 1), 3000);
    }
}
connectMongo();

// Proxy Configuration
const proxyCfg = {
    changeOrigin: true,
    timeout: PROXY_TIMEOUT,
    onProxyReq: (proxyReq, req) => {
        if (req.body && Object.keys(req.body).length > 0) {
            const bodyData = JSON.stringify(req.body);
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
            proxyReq.write(bodyData);
        }
        proxyReq.setHeader('x-request-id', req.requestId);
    },
    onError: (err, req, res) => {
        logger.error('Proxy Timeout/Error', { target: req.url });
        if (!res.headersSent) res.status(504).json({ message: 'Gateway Timeout', requestId: req.requestId });
    }
};

// --- BRIDGES TO MICROSERVICES ---
app.use('/api/auth', createProxyMiddleware({ target: 'http://127.0.0.1:4000', pathRewrite: { '^/api/auth': '' }, ...proxyCfg }));
app.use('/api/dispatch-instructions', createProxyMiddleware({ target: 'http://127.0.0.1:5001', pathRewrite: { '^/api/dispatch-instructions': '' }, ...proxyCfg }));
app.use('/api/standards', createProxyMiddleware({ target: 'http://127.0.0.1:6100', pathRewrite: { '^/api/standards': '' }, ...proxyCfg }));
app.use('/api/billing', createProxyMiddleware({ target: 'http://127.0.0.1:6400', pathRewrite: { '^/api/billing': '' }, ...proxyCfg }));
app.use('/api/ai', createProxyMiddleware({ target: 'http://127.0.0.1:6500', pathRewrite: { '^/api/ai': '' }, ...proxyCfg }));

// --- INTERNAL CORE ROUTES (SHERIFF OPS) ---
app.use('/api/documents', require('./routes/documentRoutes'));
app.use('/api/dashboard', require('./routes/dashboardRoutes'));

server.listen(PORT, '0.0.0.0', () => {
    logger.info('🚀 [Wilsy Gateway] Epitome Routing Online', { port: PORT });
});
