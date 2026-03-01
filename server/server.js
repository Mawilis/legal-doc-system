#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - MAIN SERVER                                                     ║
 * ║ Production-grade Express server with multi-tenant isolation                ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import Redis from 'ioredis';

// Load environment variables
dotenv.config();

// Import routes
import healthRoutes from './routes/health.js';
import predictiveRoutes from './routes/predictive.js';
import eSignRoutes from './routes/eSignRoutes.js';
import templateRoutes from './routes/templateRoutes.js';

// Import middleware
import { tenantContext } from './middleware/tenantContext.js';
import { requestLogger } from './middleware/requestLogger.js';
import { errorHandler } from './middleware/errorHandler.js';
import { rateLimiter } from './middleware/rateLimiter.js';
import { correlationId } from './middleware/correlationId.js';
import authMiddleware from './middleware/auth.js';

const app = express();
const PORT = process.env.PORT || 3000;

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Security middleware
app.use(
  helmet({
    contentSecurityPolicy: false,
    crossOriginEmbedderPolicy: false,
  })
);

// CORS
app.use(
  cors({
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true,
  })
);

// Compression
app.use(compression());

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(requestLogger);

// Correlation ID for request tracing
app.use(correlationId);

// Rate limiting (skip for health checks)
app.use((req, res, next) => {
  if (req.path.startsWith('/health')) {
    return next();
  }
  return rateLimiter(req, res, next);
});

// Tenant context
app.use(tenantContext);

// Auth middleware (will be bypassed in beta mode)
app.use(authMiddleware);

// ============================================================================
// ROUTES
// ============================================================================

// Health check (public)
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || '3.0.0',
    services: {
      database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
      redis: global.redisClient ? 'connected' : 'not configured',
    },
  });
});

// API routes
app.use('/api/predict', predictiveRoutes);
app.use('/api/signatures', eSignRoutes);
app.use('/api/templates', templateRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString(),
  });
});

// Error handler
app.use(errorHandler);

// ============================================================================
// DATABASE CONNECTION
// ============================================================================

const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy-os';
    await mongoose.connect(mongoURI);
    console.log('✅ MongoDB connected successfully');
  } catch (err) {
    console.error('❌ MongoDB connection error:', err.message);
    process.exit(1);
  }
};

// ============================================================================
// REDIS CONNECTION
// ============================================================================

global.redisClient = null;

const connectRedis = async () => {
  try {
    const redisURL = process.env.REDIS_URL || 'redis://localhost:6379';
    global.redisClient = new Redis(redisURL, {
      maxRetriesPerRequest: 3,
      retryStrategy: (times) => Math.min(times * 50, 2000),
    });

    global.redisClient.on('connect', () => console.log('✅ Redis connected successfully'));
    global.redisClient.on('error', (err) =>
      console.error('❌ Redis connection error:', err.message)
    );
  } catch (err) {
    console.error('❌ Redis connection error:', err.message);
  }
};

// ============================================================================
// SERVER INITIALIZATION
// ============================================================================

const startServer = async () => {
  try {
    // Connect to databases
    await connectDB();
    await connectRedis();

    // Start server
    const server = app.listen(PORT, () => {
      console.log(`\n🚀 WILSY OS v3.0 server running on port ${PORT}`);
      console.log(`📊 Health check: http://localhost:${PORT}/health`);
      console.log(`🔮 Predict API: http://localhost:${PORT}/api/predict/analyze`);
      console.log(`📝 Signatures API: http://localhost:${PORT}/api/signatures`);
      console.log(`📄 Templates API: http://localhost:${PORT}/api/templates`);
      console.log(`📈 Metrics: http://localhost:${PORT}/api/predict/metrics`);
      console.log(`💰 Investor value: R71.3B potential\n`);
    });

    // Graceful shutdown
    const shutdown = async () => {
      console.log('\n🛑 Shutting down gracefully...');
      server.close(async () => {
        console.log('✅ HTTP server closed');
        await mongoose.connection.close();
        console.log('✅ MongoDB connection closed');
        if (global.redisClient) {
          await global.redisClient.quit();
          console.log('✅ Redis connection closed');
        }
        process.exit(0);
      });
    };

    process.on('SIGTERM', shutdown);
    process.on('SIGINT', shutdown);
  } catch (err) {
    console.error('❌ Server startup error:', err.message);
    process.exit(1);
  }
};

startServer();

export default app;
