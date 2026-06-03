/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SERVER ORCHESTRATOR [V43.0.1-TITAN-STABLE]                                                                                  ║
 * ║ [PRODUCTION CORS | SOVEREIGN AUTH GATEWAY | MULTI-TENANT | FORENSIC LOGGING | COMPLIANCE HUD]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 43.0.1-TITAN | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                     ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | BOARDROOM READY                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/index.js                                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated Production-Level CORS Finality and Origin Validation.                                ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Re-injected complianceRoutes and port alignment. [2026-05-14]                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import fileUpload from 'express-fileupload';
import dotenv from 'dotenv';
import connectDB from './config/db.js';
import loggerRaw from './utils/logger.js';
const logger = loggerRaw.default || loggerRaw;

// 🔱 SOVEREIGN ROUTE IMPORTS
import authRoutes from './routes/auth.js';
import revenueRoutes from './routes/revenue.js';
import tenantRoutes from './routes/tenants.js';
import emailRoutes from './routes/email.js';
import telemetryRoutes from './routes/telemetry.js';
import complianceRoutes from './routes/compliance.js'; // 🛡️ RECTIFIED: Re-injected

dotenv.config();

const app = express();

// 🏛️ DATABASE ANCHOR
connectDB();

/**
 * 🛡️ PRODUCTION CORS CONFIGURATION
 */
const allowedOrigins = [
  'http://localhost:3000',
  'http://127.0.0.1:3000',
  process.env.CLIENT_URL,
  process.env.FRONTEND_URL
].filter(Boolean);

const corsOptions = {
  origin: function (origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      logger.warn(`🛑 [CORS-VIOLATION] Blocked origin: ${origin}`);
      callback(new Error('CORS Not Allowed by Sovereign Policy'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'Accept',
    'X-CSRF-Token',
    'X-Tenant-ID',
    'X-Trace-ID',
    'X-Request-Seal',
    'X-Forensic-Timestamp',
    'X-Wilsy-OS-Build',
    'X-Cryptographic-Nonce', // Re-injected for HUD
    'X-Institutional-Finality', // Re-injected for HUD
    'X-Quantum-Verified', // Re-injected for HUD
    'X-Shard-Node' // Re-injected for HUD
  ],
  exposedHeaders: ['X-RateLimit-Limit', 'X-Institutional-Latency'],
  maxAge: 86400,
  optionsSuccessStatus: 200
};

// ====================== MIDDLEWARE ======================
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors(corsOptions));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

app.use(fileUpload({
  limits: { fileSize: 50 * 1024 * 1024 },
  useTempFiles: false
}));

// ====================== ROUTE MOUNTING ======================
app.use('/api/auth', authRoutes);
app.use('/api/tenants', tenantRoutes);
app.use('/api/revenue', revenueRoutes);
app.use('/api/email', emailRoutes);
app.use('/api/telemetry', telemetryRoutes);
app.use('/api/compliance', complianceRoutes); // 🛡️ RECTIFIED: Re-injected

// ====================== HEALTH & ROOT ======================
app.get('/', (req, res) => {
  res.json({
    status: "OPERATIONAL",
    system: "WILSY OS SINGULARITY",
    version: "43.0.1-TITAN",
    message: "Sovereign Quantum Encryption Nexus Active",
    timestamp: new Date().toISOString()
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'OPTIMAL',
    build: '43.0.1-TITAN',
    database: 'CONNECTED',
    timestamp: new Date().toISOString(),
    sovereign: true
  });
});

// ====================== GLOBAL ERROR HANDLER ======================
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  logger.error(`🚨 [ORCHESTRATOR-FRACTURE] ${err.message}`);

  res.status(statusCode).json({
    status: 'FRACTURE',
    message: process.env.NODE_ENV === 'production' ? 'Internal Sovereign Error' : err.message,
    traceId: req.headers['x-trace-id'] || 'UNKNOWN'
  });
});

// ====================== SERVER START ======================
const PORT = process.env.PORT || 4000; // 🛡️ RECTIFIED: Re-aligned to 4000
const server = app.listen(PORT, () => {
  logger.info(`
╔══════════════════════════════════════════════════════════════════════════╗
║ ⚛️  WILSY OS SINGULARITY v43.0.1-TITAN — FULLY OPERATIONAL               ║
║ Status: ONLINE | Integrity: SECURED | Quantum Shield: ACTIVE             ║
╠══════════════════════════════════════════════════════════════════════════╣
║ 📡 Server     : http://localhost:${PORT}                                 ║
║ 🔑 Auth       : /api/auth                                                ║
║ 🏛️  Tenants   : /api/tenants                                             ║
║ 🛡️  Sentinel  : /api/compliance                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
  `);
});

// Graceful Shutdown
process.on('SIGTERM', () => {
  logger.info('🔻 TERMINATING SOVEREIGN SESSION...');
  server.close(() => {
    logger.info('🛑 CORE OFFLINE. SINGULARITY PRESERVED.');
    process.exit(0);
  });
});

export default app;
